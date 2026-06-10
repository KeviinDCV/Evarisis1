# -*- coding: utf-8 -*-
"""Análisis FRESCO de incompletos: qué biomarcadores faltan y si están en el PDF."""
import sys, os, json, re
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros
from core.biomarcadores_ia import _norm, _token_marcador

df = get_all_records_as_dataframe()
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
res = analizar_batch_registros(nums)
bios = Counter(); caso_por_bio = {}
campos = Counter()
for x in res["incompletos"]:
    for b in x.get("biomarcadores_faltantes", []):
        bios[b] += 1; caso_por_bio.setdefault(b, []).append(x["numero_peticion"])
    for c in x.get("campos_faltantes", []):
        campos[c] += 1

PD = os.path.join(ROOT, "pdfs_patologia")
PDFS = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]
def tc(caso):
    for p in PDFS:
        try: doc = fitz.open(p)
        except Exception: continue
        pgs = [pg.get_text("text") for pg in doc if caso in pg.get_text("text")]; doc.close()
        if pgs: return "\n".join(pgs)
    return None

verif = []
for bio, cnt in bios.most_common(5):
    token = _token_marcador(bio) or bio.replace("IHQ_", "")
    for caso in caso_por_bio[bio][:2]:
        txt = tc(caso)
        menc = bool(txt and re.search(rf"\b{re.escape(token)}\b", _norm(txt))) if txt else None
        verif.append({"bio": bio, "caso": caso, "token": token, "menciona_pdf": menc})

out = {"total": len(df), "resumen": res["resumen"],
       "campos_faltantes": campos.most_common(8), "bio_faltantes": bios.most_common(12),
       "verif_en_pdf": verif}
with open(ROOT + r"\herramientas_ia\resultados\_incompletos2.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
