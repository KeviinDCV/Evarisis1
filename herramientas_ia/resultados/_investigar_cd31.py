# -*- coding: utf-8 -*-
"""Investiga los casos con IHQ_CD31 faltante: ¿el PDF menciona CD31 o no?"""
import sys, os, json, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros

df = get_all_records_as_dataframe()
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
res = analizar_batch_registros(nums)
casos = [x["numero_peticion"] for x in res["incompletos"] if "IHQ_CD31" in x.get("biomarcadores_faltantes", [])]

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

out = {"n_casos_cd31": len(casos), "detalle": []}
for caso in casos:
    row = df[df["Numero de caso"] == caso]
    bd_cd31 = str(row["IHQ_CD31"].iloc[0]) if not row.empty and "IHQ_CD31" in df.columns else "?"
    solic = str(row["IHQ_ESTUDIOS_SOLICITADOS"].iloc[0])[:90] if not row.empty else "?"
    txt = texto_caso(caso)
    menciona, contexto = False, ""
    if txt:
        m = re.search(r'\bCD\s*[-/]?\s*31\b', txt, re.IGNORECASE)
        if m:
            menciona = True
            contexto = " ".join(txt[max(0, m.start()-50):m.start()+70].split())
    out["detalle"].append({
        "caso": caso, "pdf_menciona_CD31": menciona, "contexto_pdf": contexto,
        "BD_IHQ_CD31": bd_cd31[:40], "solicitados_BD": solic,
    })
with open(ROOT + r"\herramientas_ia\resultados\_cd31.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
