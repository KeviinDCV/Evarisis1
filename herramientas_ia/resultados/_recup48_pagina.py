# -*- coding: utf-8 -*-
"""Aplica el fallback de página propia a los 48 casos 'SIN DIAGNOSTICO': busca el
dx/órgano en la página del PDF que los contiene y actualiza la BD si recupera un
diagnóstico real. Los que no -> quedan en 'REVISAR' (honesto)."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.ihq_processor import _recuperar_de_pagina_propia
from core.db_adapter import get_connection
DM = os.path.join(ROOT, "data", "debug_maps")
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'

def pdf_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs: return ''
    try:
        return json.load(open(fs[-1], encoding="utf-8")).get("pdf_path", "")
    except Exception:
        return ''

df = get_all_records_as_dataframe().fillna('')
conn = get_connection(); cur = conn.cursor()
recuperados = []; no_recup = 0
for i in range(len(df)):
    dxp = str(df['Diagnostico Principal'].iloc[i]).strip()
    if categorizar_diagnostico(dxp) != SIN:
        continue
    caso = str(df['Numero de caso'].iloc[i])
    pdf = pdf_de(caso)
    if not pdf or not os.path.exists(pdf):
        no_recup += 1; continue
    db = _recuperar_de_pagina_propia(pdf, caso, lambda m: None)
    if not db:
        no_recup += 1; continue
    nuevo_dx = str(db.get('Diagnostico Principal', '')).strip()
    if nuevo_dx and categorizar_diagnostico(nuevo_dx) != SIN and len(nuevo_dx) > 4:
        cur.execute('UPDATE informes_ihq SET `Diagnostico Principal`=%s WHERE `Numero de caso`=%s', (nuevo_dx, caso))
        org = str(db.get('IHQ_ORGANO', '')).strip()
        org_act = str(df['IHQ_ORGANO'].iloc[i]).strip().upper()
        if org and org.upper() not in ('','N/A','NO APLICA','NO ENCONTRADO') and org_act in ('','N/A','NO APLICA','NO ENCONTRADO'):
            cur.execute('UPDATE informes_ihq SET `IHQ_ORGANO`=%s WHERE `Numero de caso`=%s', (org, caso))
        recuperados.append({'caso': caso, 'de': dxp[:22], 'a': nuevo_dx[:42]})
    else:
        no_recup += 1
conn.commit(); conn.close()

# distribución final
df2 = get_all_records_as_dataframe().fillna('')
sin = sum(1 for v in df2['Diagnostico Principal'].astype(str) if categorizar_diagnostico(v) == SIN)
out = {'recuperados_pagina': len(recuperados), 'no_recuperados': no_recup,
       'sin_dx_final': sin, 'ejemplos': recuperados[:15]}
with open(os.path.join(ROOT,'herramientas_ia','resultados','_recup48_pagina.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
