# -*- coding: utf-8 -*-
"""Valida el patrón SUGIEREN/viñeta:
1) IHQ260190/214/521 -> ahora extraen su diagnóstico desde la página propia.
2) NO-REGRESIÓN: casos con dx ya correcto (FAVORECEN/COMPATIBLES/SUGIEREN en OCR)
   no cambian al re-extraer."""
import sys, os, json, glob, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import get_all_records_as_dataframe
DM = os.path.join(ROOT, "data", "debug_maps")

def pdf_de(c):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{c}_*.json")))
    return json.load(open(fs[-1], encoding="utf-8")).get("pdf_path", "") if fs else ""

def ocr_de(c):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{c}_*.json")))
    if not fs: return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado","texto","texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50: return o[k]
    return None

# 1) Los 3 casos: extraer de su página propia
res = {"objetivo": {}, "regresion": {"revisados": 0, "cambios": []}}
for c in ["IHQ260190","IHQ260214","IHQ260521"]:
    pdf = pdf_de(c); dx = "no pdf"
    if os.path.exists(pdf):
        doc = fitz.open(pdf)
        for pg in doc:
            t = pg.get_text("text")
            if c in t and re.search(r"(?i)DIAGN[ÓO]STICO", t):
                db = map_to_database_format(extract_ihq_data(t))
                dx = str(db.get("Diagnostico Principal",""))[:50]; break
        doc.close()
    res["objetivo"][c] = dx

# 2) No-regresión: casos con dx en BD cuyo OCR usa estos verbos
df = get_all_records_as_dataframe().fillna("")
verbos = re.compile(r"(?i)FAVORECEN|COMPATIBLES\s+CON|SUGIEREN")
revisados = 0
for i in range(len(df)):
    if revisados >= 25: break
    caso = str(df["Numero de caso"].iloc[i])
    dx_bd = str(df["Diagnostico Principal"].iloc[i]).strip()
    if not dx_bd or dx_bd.upper() in ("N/A","NO ENCONTRADO"): continue
    ocr = ocr_de(caso)
    if not ocr or not verbos.search(ocr): continue
    revisados += 1
    db = map_to_database_format(extract_ihq_data(ocr))
    dx_new = str(db.get("Diagnostico Principal","")).strip()
    if dx_new.upper() != dx_bd.upper():
        res["regresion"]["cambios"].append({"caso": caso, "bd": dx_bd[:40], "nuevo": dx_new[:40]})
res["regresion"]["revisados"] = revisados

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_valida_sugieren.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("OK")
