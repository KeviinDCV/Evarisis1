# -*- coding: utf-8 -*-
"""Recuperación AGRESIVA de los casos 'SIN DIAGNOSTICO': concatena TODAS las
páginas del PDF que contienen el caso y extrae el dx del texto completo
(DIAGNÓSTICO + COMENTARIOS + MICROSCÓPICA). Reporta qué recupera."""
import sys, os, json, glob, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.unified_extractor import extract_ihq_data, map_to_database_format
DM = os.path.join(ROOT, "data", "debug_maps")
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'

def pdf_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs: return ''
    try: return json.load(open(fs[-1], encoding="utf-8")).get("pdf_path", "")
    except Exception: return ''

def texto_caso(pdf, caso):
    """Concatena SOLO las páginas que contienen el caso y NO otro IHQ distinto."""
    try: doc = fitz.open(pdf)
    except Exception: return ''
    partes = []
    for pg in doc:
        t = pg.get_text("text")
        nums = set(re.findall(r"IHQ\d{6}", t))
        if caso in nums and (nums == {caso} or len(nums) <= 1):
            partes.append(t)
    doc.close()
    return "\n".join(partes)

df = get_all_records_as_dataframe().fillna('')
recup = []; queda = []
for i in range(len(df)):
    dxp = str(df['Diagnostico Principal'].iloc[i]).strip()
    if categorizar_diagnostico(dxp) != SIN: continue
    caso = str(df['Numero de caso'].iloc[i])
    pdf = pdf_de(caso)
    nuevo = ''
    if pdf and os.path.exists(pdf):
        txt = texto_caso(pdf, caso)
        if txt:
            try:
                db = map_to_database_format(extract_ihq_data(txt))
                nuevo = str(db.get('Diagnostico Principal','')).strip()
            except Exception:
                nuevo = ''
    cat_nuevo = categorizar_diagnostico(nuevo) if nuevo else SIN
    if nuevo and cat_nuevo != SIN and len(nuevo) > 4:
        recup.append({'caso': caso, 'de': dxp[:20], 'a': nuevo[:42], 'cat': cat_nuevo[:25]})
    else:
        queda.append({'caso': caso, 'dxp': dxp[:45]})

out = {'recuperables': len(recup), 'quedan': len(queda),
       'recup': recup, 'irreductibles': queda}
with open(os.path.join(ROOT,'herramientas_ia','resultados','_recup26_agresivo.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("recup", len(recup), "queda", len(queda))
