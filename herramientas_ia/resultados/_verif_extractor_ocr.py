# -*- coding: utf-8 -*-
"""Corre el extractor ACTUAL sobre el OCR real de los 5 casos y muestra el
fragmento de tabla (órgano) y la sección DIAGNÓSTICO (malignidad)."""
import sys, os, json, re, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.unified_extractor import extract_ihq_data, map_to_database_format

DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ260034", "IHQ260704", "IHQ260711", "IHQ260725", "IHQ260795"]

def ocr_de(caso):
    files = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not files:
        return None
    with open(files[-1], "r", encoding="utf-8") as fh:
        dm = json.load(fh)
    o = dm.get("ocr", {})
    if isinstance(o, dict):
        for k in ("texto_consolidado", "texto", "texto_completo"):
            if isinstance(o.get(k), str) and len(o[k]) > 50:
                return o[k]
    return None

out = {}
for caso in CASOS:
    ocr = ocr_de(caso)
    if not ocr:
        out[caso] = {"err": "sin ocr"}
        continue
    info = {}
    # Extractor actual
    try:
        db = map_to_database_format(extract_ihq_data(ocr))
        info["extractor_actual"] = {
            "Organo": str(db.get("Organo", "(no key)")),
            "IHQ_ORGANO": str(db.get("IHQ_ORGANO", "(no key)")),
            "Malignidad": str(db.get("Malignidad", "(no key)")),
            "Diagnostico Principal": str(db.get("Diagnostico Principal", ""))[:70],
        }
    except Exception as e:
        info["extractor_actual"] = {"ERROR": str(e)}
    # Fragmento crudo alrededor de "Bloques y laminas" (órgano de tabla)
    m = re.search(r"Bloques y laminas", ocr)
    if m:
        info["frag_bloques"] = repr(ocr[m.start():m.start()+120])
    # Sección DIAGNÓSTICO (para verificar malignidad)
    md = re.search(r"(?i)\bDIAGN[ÓO]STICO\b", ocr)
    if md:
        info["seccion_dx"] = ocr[md.start():md.start()+400].replace("\n", " | ")
    out[caso] = info

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_extractor_ocr.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
