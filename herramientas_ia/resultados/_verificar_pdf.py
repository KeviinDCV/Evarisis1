# -*- coding: utf-8 -*-
"""Abre los PDFs reales y muestra el texto del informe para casos
problematicos, para verificar si el diagnostico SI esta en el PDF."""
import sys, os, re, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core import database_manager as dm

PD = os.path.join(ROOT, "pdfs_patologia")
PDFS = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]

df = dm.get_all_records_as_dataframe()
cc, dc = "Numero de caso", "Diagnostico Principal"
db_dx = {str(df[cc].iloc[i]): str(df[dc].iloc[i]) for i in range(len(df))}

def texto_caso(caso):
    """Busca el caso en los PDFs y devuelve el texto de sus paginas."""
    for p in PDFS:
        try:
            doc = fitz.open(p)
        except Exception:
            continue
        paginas = []
        for pg in doc:
            t = pg.get_text("text")
            if caso in t:
                paginas.append(t)
        doc.close()
        if paginas:
            return "\n".join(paginas), os.path.basename(p)
    return None, None

casos = sys.argv[1:] or ["IHQ251313", "IHQ251247", "IHQ251374", "IHQ251229"]
out = {}
for caso in casos:
    txt, pdf = texto_caso(caso)
    print("=" * 80)
    print(f"CASO {caso}   (PDF: {pdf})")
    print(f"  BD Diagnostico Principal (lo que guardo el regex):")
    print(f"    >>> {db_dx.get(caso, '?')[:200]!r}")
    if not txt:
        print("  !! No encontrado en PDFs"); out[caso] = {"pdf": None}; continue
    # Mostrar la seccion DIAGNOSTICO y COMENTARIO del PDF
    for etiqueta, pat in [("DIAGNOSTICO", r"DIAGN[OÓ]STICO"), ("COMENTARIO", r"COMENTARIOS?")]:
        m = re.search(pat, txt)
        if m:
            frag = txt[m.start():m.start() + 600]
            frag = re.sub(r"\n{2,}", "\n", frag)
            print(f"  --- Seccion {etiqueta} en el PDF ---")
            for ln in frag.split("\n")[:14]:
                if ln.strip():
                    print(f"      {ln.strip()[:110]}")
    out[caso] = {"pdf": pdf, "bd": db_dx.get(caso, "")[:200]}
with open(ROOT + r"\herramientas_ia\resultados\_verif_pdf.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
