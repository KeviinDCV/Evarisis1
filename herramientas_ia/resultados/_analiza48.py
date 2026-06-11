# -*- coding: utf-8 -*-
"""Para los casos 'SIN DIAGNOSTICO' restantes: aplica el extractor de dx sobre el
OCR completo y categoriza, para ver cuáles son RECUPERABLES (el dx está en el OCR
pero no se extrajo) vs genuinamente sin dx."""
import sys, os, json, glob, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.unified_extractor import extract_diagnostico_principal
DM = os.path.join(ROOT, "data", "debug_maps")
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'

def ocr_de(c):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{c}_*.json")))
    if not fs: return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado","texto","texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50: return o[k]
    return None

def seccion_dx(ocr):
    # última sección DIAGNÓSTICO (conclusión)
    ms = list(re.finditer(r"(?i)\bDIAGN[ÓO]STICO\b", ocr))
    if not ms: return ""
    s = ocr[ms[-1].start():ms[-1].start()+300]
    return re.sub(r"\s+", " ", s).strip()

df = get_all_records_as_dataframe().fillna('')
recuperables = []; sin_recuperar = []
for i in range(len(df)):
    dxp = str(df['Diagnostico Principal'].iloc[i]).strip()
    if categorizar_diagnostico(dxp) != SIN: continue
    caso = str(df['Numero de caso'].iloc[i])
    ocr = ocr_de(caso)
    cand = ""
    if ocr:
        try:
            cand = (extract_diagnostico_principal(ocr) or "").strip()
            cand = re.sub(r"^[\s\-•·]+", "", cand)
        except Exception:
            cand = ""
    cat_cand = categorizar_diagnostico(cand) if cand else SIN
    item = {"caso": caso, "dxp_actual": dxp[:30], "cand_extract": cand[:40], "cat_cand": cat_cand[:30],
            "ocr_dx": seccion_dx(ocr)[:120] if ocr else "sin ocr"}
    if cand and cat_cand != SIN and len(cand) > 4:
        recuperables.append(item)
    else:
        sin_recuperar.append(item)

out = {"n_recuperables": len(recuperables), "n_sin_recuperar": len(sin_recuperar),
       "recuperables": recuperables, "sin_recuperar": sin_recuperar[:20]}
with open(os.path.join(ROOT,'herramientas_ia','resultados','_analiza48.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK", len(recuperables), len(sin_recuperar))
