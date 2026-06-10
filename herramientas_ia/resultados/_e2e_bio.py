# -*- coding: utf-8 -*-
"""E2E de la capa IA de biomarcadores: casos de CD31 narrativo."""
import sys, os, json, time
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

res = []
for caso in ["IHQ250380", "IHQ250452", "IHQ250299"]:
    txt = texto_caso(caso)
    if not txt:
        res.append({"caso": caso, "err": "no pdf"}); continue
    t0 = time.time()
    ex = extract_ihq_data(txt)
    db = map_to_database_format(ex)
    res.append({
        "caso": caso, "seg": round(time.time() - t0, 1),
        "IHQ_CD31": str(db.get("IHQ_CD31")), "IHQ_CD34": str(db.get("IHQ_CD34")),
        "IHQ_HHV8": str(db.get("IHQ_HHV8")),
        "dx": str(db.get("Diagnostico Principal"))[:45],
    })
with open(ROOT + r"\herramientas_ia\resultados\_e2e_bio.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
