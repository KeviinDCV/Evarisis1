# -*- coding: utf-8 -*-
"""Grupo B: casos 'SIN DIAGNOSTICO' cuyo Dx Principal es FRAGMENTO y Coloración
tiene dx real -> usar Coloración. NO toca dx válidos (tumores raros)."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.db_adapter import get_connection

SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'
_TERM_DX = ('CARCINOMA','ADENOCARCINOMA','NEOPLASIA','TUMOR','LINFOMA','SARCOMA','MELANOMA',
            'INFILTRAC','HIPERPLASIA','DISPLASIA','METASTAS','PROLIFERAC','LESION','LESIÓN',
            'MALIGN','ADENOMA','PAPILAR','BLASTOMA','GLIOMA','MIELOMA','LEUCEMIA','ATIPIC',
            'GASTRITIS','INFLAMAC','SIALODENITIS','CARCINOMATOSIS','ESCAMOCELULAR')
_FRAG = ('ESTUDIO','INMUNOHISTOQU','PATRON MICROSATELITAL','PATRÓN MICROSATELITAL','INFORME EXTERNO',
         'VER COMENTARIO','VER DESCRIPCI','LAMINA','LÁMINA','BLOQUE','NIVELES HISTOL','HER2','HER-2',
         'RECEPTOR DE ESTROG','RECEPTOR DE PROGEST','RECEPTORES DE','REVISIÓN','REVISION','FOCUS',
         'ROTULAD','CORRELACIÓN CON','CORRELACION CON','GRADO HISTOLOGICO','NOTTINGHAM','NOTINGHAM',
         'MLH1','MSH2','MSH6','PMS2','EXPRESIÓN NUCLEAR','EXPRESION NUCLEAR','REPRESENTACION DE LAS',
         'MADURACIÓN DE LAS','MADURACION DE LAS','BIOPSIA DE','BIOPSIA DEL','SIN AUMENTO DE',
         'SIN EVIDENCIA DE','POBLACIÓN DE','POBLACION DE','LINFOCITOS INTRA','MUESTRA CON','MUESTRA LIMITADA')

df = get_all_records_as_dataframe().fillna('')
conn = get_connection(); cur = conn.cursor()
corr = 0; ej = []
for i in range(len(df)):
    dxp = str(df['Diagnostico Principal'].iloc[i]).strip()
    if categorizar_diagnostico(dxp) != SIN:
        continue
    es_frag = (not dxp) or len(dxp) < 4 or any(m in dxp.upper() for m in _FRAG)
    if not es_frag:
        continue  # dx válido (tumor raro) -> no tocar
    dxc = str(df['Diagnostico Coloracion'].iloc[i]).strip()
    if dxc.upper() not in ('','N/A','NO APLICA','NO ENCONTRADO','NAN') and any(t in dxc.upper() for t in _TERM_DX):
        caso = str(df['Numero de caso'].iloc[i])
        cur.execute('UPDATE informes_ihq SET `Diagnostico Principal`=%s WHERE `Numero de caso`=%s', (dxc, caso))
        corr += 1
        if len(ej) < 8: ej.append({'caso': caso, 'de': dxp[:22], 'a': dxc[:38]})
conn.commit(); conn.close()

df2 = get_all_records_as_dataframe().fillna('')
sin = sum(1 for v in df2['Diagnostico Principal'].astype(str) if categorizar_diagnostico(v) == SIN)
out = {'corregidos_grupoB': corr, 'sin_dx_restantes': sin, 'ejemplos': ej}
with open(os.path.join(ROOT,'herramientas_ia','resultados','_reeval_grupoB.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
