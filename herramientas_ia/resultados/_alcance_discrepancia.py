# -*- coding: utf-8 -*-
"""Mide el ALCANCE de la discrepancia: compara la BD (informes_ihq) vs el
debug_map (extractor tradicional) para una muestra de casos. Si difieren
sistemáticamente, la BD NO se llenó con el pipeline regex."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
DM = os.path.join(ROOT, "data", "debug_maps")

df = get_all_records_as_dataframe().fillna("")
casos = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
# Muestra: 1 de cada N para cubrir todo el rango (~30 casos)
paso = max(1, len(casos) // 30)
muestra = casos[::paso][:30]

def dmap_campos(caso):
    files = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not files:
        return None
    try:
        dm = json.load(open(files[-1], encoding="utf-8"))
    except Exception:
        return None
    cc = dm.get("base_datos", {}).get("campos_criticos", {})
    return {
        "Diagnostico Principal": str(cc.get("Diagnostico Principal", "")).strip(),
        "Malignidad": str(cc.get("Malignidad", "")).strip(),
        "Organo": str(cc.get("Organo", "")).strip(),
    } if cc else None

rows = {df["Numero de caso"].iloc[i]: i for i in range(len(df))}
difieren = []
coinciden = 0
sin_dmap = 0
for caso in muestra:
    i = rows.get(caso)
    bd = {
        "Diagnostico Principal": str(df["Diagnostico Principal"].iloc[i]).strip(),
        "Malignidad": str(df["Malignidad"].iloc[i]).strip(),
        "Organo": str(df["Organo"].iloc[i]).strip(),
    }
    dm = dmap_campos(caso)
    if dm is None:
        sin_dmap += 1
        continue
    dif = {k: {"bd": bd[k], "debug_map": dm[k]} for k in bd if bd[k] != dm[k]}
    if dif:
        difieren.append({"caso": caso, "dif": dif})
    else:
        coinciden += 1

out = {
    "total_bd": len(casos),
    "muestra": len(muestra),
    "coinciden": coinciden,
    "difieren": len(difieren),
    "sin_debug_map": sin_dmap,
    "ejemplos_discrepancia": difieren[:12],
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_alcance_discrepancia.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
