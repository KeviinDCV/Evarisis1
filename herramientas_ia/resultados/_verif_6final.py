# -*- coding: utf-8 -*-
"""Verifica los 6 incompletos finales: qué da el extractor actual sobre el OCR vs
la BD, y el contexto del diagnóstico/órgano en el OCR (recuperable vs N/A honesto)."""
import sys, os, json, re, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.unified_extractor import extract_ihq_data, map_to_database_format
DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ250368", "IHQ250411", "IHQ250424", "IHQ250723", "IHQ251356", "IHQ251488"]

def ocr_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None, None
    dm = json.load(open(fs[-1], encoding="utf-8"))
    o = dm.get("ocr", {})
    cc = dm.get("base_datos", {}).get("campos_criticos", {})
    for k in ("texto_consolidado", "texto", "texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50:
            return o[k], cc
    return None, cc

out = {}
for caso in CASOS:
    ocr, cc = ocr_de(caso)
    if not ocr:
        out[caso] = {"err": "sin ocr"}; continue
    db = map_to_database_format(extract_ihq_data(ocr))
    # Sección DIAGNÓSTICO del OCR (última ocurrencia, la conclusión real)
    dxs = [m.start() for m in re.finditer(r"(?i)\bDIAGN[ÓO]STICO\b", ocr)]
    seccion = ocr[dxs[-1]:dxs[-1]+260].replace("\n", " | ") if dxs else ""
    out[caso] = {
        "extractor": {"Dx": str(db.get("Diagnostico Principal"))[:55],
                      "Organo": str(db.get("IHQ_ORGANO"))[:30],
                      "DxColoracion": str(db.get("Diagnostico Coloracion"))[:55]},
        "debug_map_cc": {"Dx": str(cc.get("Diagnostico Principal",""))[:55],
                         "Organo": str(cc.get("IHQ_ORGANO",""))[:30]} if cc else {},
        "ocr_seccion_dx": re.sub(r"\s+", " ", seccion).strip(),
    }
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_6final.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
