# -*- coding: utf-8 -*-
"""Inspecciona el texto PDF de los 2 casos sin Organo: ¿está el dato? ¿por qué falló?"""
import sys, os, json, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz

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
            return "\n".join(pgs), os.path.basename(p)
    return None, None

out = {}
for caso in ["IHQ250368", "IHQ250723"]:
    txt, pdf = texto_caso(caso)
    if not txt:
        out[caso] = {"err": "no encontrado"}
        continue
    lineas = [l.strip() for l in txt.split("\n") if l.strip()]
    # líneas con palabras clave de órgano/espécimen/coloración
    kw = re.compile(r"(ORGAN|ÓRGAN|ESPEC|MUESTRA|REMIT|MACROSC|DESCRIP|COLORAC|"
                    r"CUELLO|[ÚU]TERO|C[ÉE]RVI|COLON|ENDOMETR|RECIBE|RÓTULO|ROTULO|"
                    r"PROCEDENC|LOCALIZ|TZ |BIOPSIA|CONO)", re.IGNORECASE)
    relevantes = [l for l in lineas if kw.search(l)]
    out[caso] = {
        "pdf": pdf,
        "n_lineas": len(lineas),
        "lineas_relevantes": relevantes[:40],
    }

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_pdf_organo.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
