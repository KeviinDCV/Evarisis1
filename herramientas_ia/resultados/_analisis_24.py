# -*- coding: utf-8 -*-
"""Analiza los incompletos actuales: clasifica por campos faltantes y revisa si el
dato está en el debug_map (recuperable) o es N/A honesto (provisional)."""
import sys, os, json, glob
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros
DM = os.path.join(ROOT, "data", "debug_maps")

df = get_all_records_as_dataframe().fillna("")
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
res = analizar_batch_registros(nums)

def dmap_cc(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None
    try:
        return json.load(open(fs[-1], encoding="utf-8")).get("base_datos", {}).get("campos_criticos", {})
    except Exception:
        return None

combos = Counter()
detalle = []
for x in res["incompletos"]:
    caso = x["numero_peticion"]
    cf = tuple(sorted(x.get("campos_faltantes", [])))
    combos[cf] += 1
    cc = dmap_cc(caso) or {}
    # ¿El debug_map tiene dato para los campos faltantes? (recuperable vs honesto)
    recuperable = {}
    for campo in x.get("campos_faltantes", []):
        v = str(cc.get(campo, "")).strip()
        if v and v.upper() not in ("", "N/A", "NO APLICA", "NAN"):
            recuperable[campo] = v[:40]
    detalle.append({
        "caso": caso,
        "pct": x.get("porcentaje_completitud"),
        "faltan": list(cf),
        "biomarc_faltan": x.get("biomarcadores_faltantes", []),
        "debug_map_tiene": recuperable,  # si no vacío -> recuperable (dato perdido al guardar)
    })

out = {
    "resumen": res["resumen"],
    "combinaciones_campos_faltantes": {", ".join(k) if k else "(ninguno)": v for k, v in combos.most_common()},
    "detalle": detalle,
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_analisis_24.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
