# -*- coding: utf-8 -*-
"""Validacion END-TO-END del cableado: pipeline completo extract_ihq_data ->
map_to_database_format. Caso problematico (IA debe correr) + caso bueno (intacto)."""
import sys, os, time
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

# IHQ251374 = problematico (regex da "Mucosa gastrica antral. Biopsia")
# IHQ251409 = bueno (linfoma, regex extrae bien) -> IA NO debe correr
import json
res = []
_casos = sys.argv[1:] or ["IHQ251374", "IHQ251409"]
for caso in _casos:
    txt = texto_caso(caso)
    if not txt:
        res.append({"caso": caso, "error": "sin PDF"}); continue
    t0 = time.time()
    extracted = extract_ihq_data(txt)
    db = map_to_database_format(extracted)
    dt = time.time() - t0
    res.append({
        "caso": caso, "segundos": round(dt, 1),
        "diagnostico_final": str(db.get("Diagnostico Principal"))[:100],
        "organo": str(db.get("Organo", ""))[:40],
    })
# escribir a archivo (stdout puede estar cerrado por utf8_fixer)
with open(ROOT + r"\herramientas_ia\resultados\_e2e_dx.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
