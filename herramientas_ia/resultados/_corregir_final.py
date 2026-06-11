# -*- coding: utf-8 -*-
"""Corrección final:
1) Reprocesa IHQ250368 desde su OCR (recupera Organo=CERVIX perdido al guardar).
2) Re-analiza los 6 casos con la lógica de completitud V6.9.34 (dx en Coloracion).
"""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import save_records, get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros
DM = os.path.join(ROOT, "data", "debug_maps")

def ocr_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado", "texto", "texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50:
            return o[k]
    return None

res = {}

# 1) Reprocesar IHQ250368
ocr = ocr_de("IHQ250368")
db = map_to_database_format(extract_ihq_data(ocr))
n = save_records([db])
res["reproceso_250368"] = {"save": n, "Organo": str(db.get("IHQ_ORGANO")),
                           "Dx": str(db.get("Diagnostico Principal"))[:40]}

# 2) Re-analizar los 6 casos
CASOS = ["IHQ250368", "IHQ250411", "IHQ250424", "IHQ250723", "IHQ251356", "IHQ251488"]
ana = analizar_batch_registros(CASOS)
res["resumen_6"] = ana["resumen"]
res["incompletos_restantes"] = [
    {"caso": x["numero_peticion"], "pct": x.get("porcentaje_completitud"),
     "faltan": x.get("campos_faltantes", [])}
    for x in ana["incompletos"]
]

# 3) Re-analizar TODOS para el total actualizado
df = get_all_records_as_dataframe().fillna("")
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
ana_all = analizar_batch_registros(nums)
res["resumen_total"] = ana_all["resumen"]

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_corregir_final.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
