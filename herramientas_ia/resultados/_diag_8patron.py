# -*- coding: utf-8 -*-
"""¿Los 8 incompletos siguen el patrón de IHQ250723 (contenido en página propia
del PDF que la segmentación pierde)? Para cada uno: extrae de la página del PDF
que contiene SU contenido y verifica si dx/órgano son recuperables."""
import sys, os, json, glob, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.unified_extractor import extract_ihq_data, map_to_database_format
DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ260034","IHQ260190","IHQ260214","IHQ260521","IHQ260704","IHQ260711","IHQ260725","IHQ260795"]

def pdf_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None
    return json.load(open(fs[-1], encoding="utf-8")).get("pdf_path", "")

out = {}
for caso in CASOS:
    pdf = pdf_de(caso)
    if not pdf or not os.path.exists(pdf):
        out[caso] = {"err": f"pdf no encontrado: {pdf}"}; continue
    doc = fitz.open(pdf)
    # Buscar la página que contiene el contenido del caso (DIAGNÓSTICO + el caso)
    mejor = None
    for i, pg in enumerate(doc):
        t = pg.get_text("text")
        if caso in t and re.search(r"(?i)DIAGN[ÓO]STICO|DESCRIPCI[ÓO]N\s+MICROSC", t):
            # extraer de esta página
            db = map_to_database_format(extract_ihq_data(t))
            dx = str(db.get("Diagnostico Principal", ""))
            org = str(db.get("IHQ_ORGANO", ""))
            if dx not in ("", "N/A") or org not in ("", "N/A"):
                mejor = {"pagina": i, "Dx": dx[:45], "Organo": org[:25],
                         "Malig": str(db.get("Malignidad",""))}
                break
    doc.close()
    out[caso] = {"pdf": os.path.basename(pdf), "recuperable_de_pagina": mejor}

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_diag_8patron.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
