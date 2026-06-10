# -*- coding: utf-8 -*-
"""Verifica que el reproceso (extraccion+mapeo actual) llena 'Organo' en los 2 casos."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.unified_extractor import extract_ihq_data, map_to_database_format

PD = os.path.join(ROOT, "pdfs_patologia")
PDFS = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]

def texto_caso(caso):
    for p in PDFS:
        try:
            doc = fitz.open(p)
        except Exception:
            continue
        pgs = [pg.get_text("text") for pg in doc if caso in pg.get_text("text")]
        doc.close()
        if pgs:
            return "\n".join(pgs)
    return None

out = {}
for caso in ["IHQ250368", "IHQ250723"]:
    txt = texto_caso(caso)
    if not txt:
        out[caso] = {"err": "no encontrado"}
        continue
    ex = extract_ihq_data(txt)
    db = map_to_database_format(ex)
    out[caso] = {
        "Organo": str(db.get("Organo", "(no key)")),
        "IHQ_ORGANO": str(db.get("IHQ_ORGANO", "(no key)")),
        "Diagnostico Principal": str(db.get("Diagnostico Principal", ""))[:60],
        "Diagnostico Coloracion": str(db.get("Diagnostico Coloracion", "(no key)"))[:60],
    }

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_reproceso.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
