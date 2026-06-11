# -*- coding: utf-8 -*-
"""Compara TODOS los casos IHQ260xxx: MySQL (BD) vs debug_map (extractor regex).
Define si el problema es sistémico en los casos 2026."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
DM = os.path.join(ROOT, "data", "debug_maps")

df = get_all_records_as_dataframe().fillna("")
df["_n"] = df["Numero de caso"].astype(str)
casos2026 = sorted(df[df["_n"].str.startswith("IHQ26")]["_n"].tolist())

def dmap(caso):
    files = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not files:
        return None
    try:
        dm = json.load(open(files[-1], encoding="utf-8"))
    except Exception:
        return None
    return dm.get("base_datos", {}).get("campos_criticos", {})

rows = {df["_n"].iloc[i]: i for i in range(len(df))}
difieren, coinciden, sin_dm = [], 0, 0
for caso in casos2026:
    i = rows[caso]
    cc = dmap(caso)
    if not cc:
        sin_dm += 1
        continue
    bd_dx = str(df["Diagnostico Principal"].iloc[i]).strip()
    bd_mal = str(df["Malignidad"].iloc[i]).strip()
    bd_org = str(df["Organo"].iloc[i]).strip()
    dm_dx = str(cc.get("Diagnostico Principal", "")).strip()
    dm_mal = str(cc.get("Malignidad", "")).strip()
    dm_org = str(cc.get("Organo", "")).strip()
    if (bd_dx, bd_mal, bd_org) != (dm_dx, dm_mal, dm_org):
        difieren.append({"caso": caso,
                         "BD": {"dx": bd_dx[:35], "mal": bd_mal, "org": bd_org[:25]},
                         "debug_map": {"dx": dm_dx[:35], "mal": dm_mal, "org": dm_org[:25]}})
    else:
        coinciden += 1

out = {
    "total_2026": len(casos2026),
    "coinciden": coinciden,
    "difieren": len(difieren),
    "sin_debug_map": sin_dm,
    "ejemplos": difieren[:15],
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_alcance_2026.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
