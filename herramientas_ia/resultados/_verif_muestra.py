# -*- coding: utf-8 -*-
"""Verificación aleatoria: compara la BD contra los PDFs reales."""
import sys, os, json, re, random
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe

df = get_all_records_as_dataframe()
n = len(df)
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

k = min(8, n)
idxs = random.sample(range(n), k) if n else []
out = {"total_bd": n, "casos": []}
for i in idxs:
    caso = str(df["Numero de caso"].iloc[i])
    rec = {
        "caso": caso,
        "BD_dx": str(df["Diagnostico Principal"].iloc[i]),
        "BD_edad": str(df["Edad"].iloc[i]),
        "BD_organo": str(df["Organo"].iloc[i]),
        "BD_malig": str(df["Malignidad"].iloc[i]),
        "BD_genero": str(df["Genero"].iloc[i]),
    }
    txt = texto_caso(caso)
    if not txt:
        rec["PDF"] = "NO ENCONTRADO"
    else:
        m = re.search(r'DIAGN[OÓ]STICO', txt)
        if m:
            frag = re.sub(r'\n{2,}', '\n', txt[m.start():m.start()+520])
            rec["PDF_dx_seccion"] = [l.strip() for l in frag.split("\n") if l.strip()][:9]
        me = re.search(r'Edad\s*\n?\s*:\s*([^\n]+)', txt)
        rec["PDF_edad"] = me.group(1).strip()[:30] if me else "?"
        mg = re.search(r'Genero\s*\n?\s*:\s*([^\n]+)', txt)
        rec["PDF_genero"] = mg.group(1).strip()[:20] if mg else "?"
    out["casos"].append(rec)

with open(ROOT + r"\herramientas_ia\resultados\_verif_muestra.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
