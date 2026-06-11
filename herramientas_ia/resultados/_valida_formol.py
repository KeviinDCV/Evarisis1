# -*- coding: utf-8 -*-
"""Valida el ancla 'Formol al N%' para el órgano:
1) IHQ260795 -> ahora extrae MAMA.
2) NO-REGRESIÓN: casos con órgano ya correcto en BD no cambian al re-extraer."""
import sys, os, json, glob, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import get_all_records_as_dataframe
DM = os.path.join(ROOT, "data", "debug_maps")

def ocr_de(c):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{c}_*.json")))
    if not fs: return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado","texto","texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50: return o[k]
    return None

res = {"objetivo": {}, "regresion": {"revisados": 0, "cambios": []}}

# 1) IHQ260795 desde p2 de su PDF
pdf = json.load(open(sorted(glob.glob(os.path.join(DM,'debug_map_IHQ260795_*.json')))[-1],encoding='utf-8')).get('pdf_path','')
doc = fitz.open(pdf); t = doc[2].get_text("text"); doc.close()
db = map_to_database_format(extract_ihq_data(t))
res["objetivo"]["IHQ260795"] = {"Organo": str(db.get("IHQ_ORGANO")), "OrganoRaw": str(db.get("Organo"))[:30]}

# 2) No-regresión: casos con IHQ_ORGANO válido en BD
df = get_all_records_as_dataframe().fillna("")
rev = 0
for i in range(len(df)):
    if rev >= 40: break
    caso = str(df["Numero de caso"].iloc[i])
    org_bd = str(df["IHQ_ORGANO"].iloc[i]).strip()
    if not org_bd or org_bd.upper() in ("N/A","NO ENCONTRADO",""): continue
    ocr = ocr_de(caso)
    if not ocr: continue
    rev += 1
    db2 = map_to_database_format(extract_ihq_data(ocr))
    org_new = str(db2.get("IHQ_ORGANO","")).strip()
    if org_new.upper() != org_bd.upper():
        res["regresion"]["cambios"].append({"caso": caso, "bd": org_bd[:30], "nuevo": org_new[:30]})
res["regresion"]["revisados"] = rev

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_valida_formol.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK")
