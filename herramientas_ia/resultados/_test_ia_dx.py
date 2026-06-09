# -*- coding: utf-8 -*-
"""Prueba funcional: la IA extrae el diagnostico real de casos donde el regex fallo."""
import sys, os, time
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core import database_manager as dm
from core.extractor_diagnostico_ia import extraer_diagnostico_con_ia, es_diagnostico_no_valido

PD = os.path.join(ROOT, "pdfs_patologia")
PDFS = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]
df = dm.get_all_records_as_dataframe()
cc, dc = "Numero de caso", "Diagnostico Principal"
co = [c for c in df.columns if c.strip().lower() == "organo" or "rgano" in c.lower()]
co = co[0] if co else None
db = {str(df[cc].iloc[i]): (str(df[dc].iloc[i]), str(df[co].iloc[i]) if co else "") for i in range(len(df))}

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

casos = sys.argv[1:] or ["IHQ251374", "IHQ251313", "IHQ251247", "IHQ251229", "IHQ251386", "IHQ251384"]
for caso in casos:
    bd_dx, organo = db.get(caso, ("?", ""))
    txt = texto_caso(caso)
    print("=" * 78)
    print(f"CASO {caso}   (organo BD: {organo})")
    print(f"  REGEX guardo:  {bd_dx[:75]!r}")
    print(f"  flagged?       {es_diagnostico_no_valido(bd_dx)}")
    if not txt:
        print("  (no PDF)"); continue
    t0 = time.time()
    dx_ia = extraer_diagnostico_con_ia(txt, organo=organo)
    print(f"  IA extrajo:    {dx_ia!r}   ({time.time()-t0:.1f}s)")
