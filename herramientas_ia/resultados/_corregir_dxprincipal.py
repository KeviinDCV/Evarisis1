# -*- coding: utf-8 -*-
"""Corrige en la BD el 'Diagnostico Principal' cuando es un fragmento inválido
pero 'Diagnostico Coloracion' tiene el dx real. Guarda los valores viejos."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.db_adapter import get_connection

_TERM_DX = ('CARCINOMA','ADENOCARCINOMA','NEOPLASIA','TUMOR','LINFOMA','SARCOMA','MELANOMA',
            'INFILTRAC','HIPERPLASIA','DISPLASIA','METASTAS','PROLIFERAC','LESION','LESIÓN',
            'MALIGN','ADENOMA','PAPILAR','BLASTOMA','GLIOMA','MIELOMA','LEUCEMIA','ATIPIC')
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'

df = get_all_records_as_dataframe().fillna('')
conn = get_connection(); cur = conn.cursor()
backup = []
for i in range(len(df)):
    dxp = str(df['Diagnostico Principal'].iloc[i])
    if categorizar_diagnostico(dxp) == SIN:
        dxc = str(df['Diagnostico Coloracion'].iloc[i])
        if dxc.upper() not in ('','N/A','NO APLICA','NO ENCONTRADO','NAN') and any(t in dxc.upper() for t in _TERM_DX):
            caso = str(df['Numero de caso'].iloc[i])
            backup.append({'caso': caso, 'viejo': dxp[:40], 'nuevo': dxc[:40]})
            cur.execute('UPDATE informes_ihq SET `Diagnostico Principal`=%s WHERE `Numero de caso`=%s', (dxc, caso))
conn.commit(); conn.close()

# Verificar nueva distribución de "sin dx"
df2 = get_all_records_as_dataframe().fillna('')
sin_dx_despues = sum(1 for v in df2['Diagnostico Principal'].astype(str) if categorizar_diagnostico(v) == SIN)

out = {'corregidos': len(backup), 'sin_dx_despues': sin_dx_despues, 'ejemplos': backup[:6]}
# guardar backup completo
json.dump(backup, open(os.path.join(ROOT,'backups','dxprincipal_backup.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
with open(os.path.join(ROOT,'herramientas_ia','resultados','_corregir_dxprincipal.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
