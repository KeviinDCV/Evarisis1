# -*- coding: utf-8 -*-
"""Re-evalúa los 57 casos con la condición ESTRICTA. Restaura el Dx Principal
original (desde debug_map) para dx válidos (NEUROMA...); mantiene el reemplazo
por Coloración solo para fragmentos reales (ESTUDIO/PATRÓN MICROSATELITAL...)."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico
from core.db_adapter import get_connection
DM = os.path.join(ROOT, "data", "debug_maps")

_TERM_DX = ('CARCINOMA','ADENOCARCINOMA','NEOPLASIA','TUMOR','LINFOMA','SARCOMA','MELANOMA',
            'INFILTRAC','HIPERPLASIA','DISPLASIA','METASTAS','PROLIFERAC','LESION','LESIÓN',
            'MALIGN','ADENOMA','PAPILAR','BLASTOMA','GLIOMA','MIELOMA','LEUCEMIA','ATIPIC')
_FRAG = ('ESTUDIO','INMUNOHISTOQU','PATRON MICROSATELITAL','PATRÓN MICROSATELITAL',
         'INFORME EXTERNO','VER COMENTARIO','VER DESCRIPCI','LAMINA','LÁMINA','BLOQUE','NIVELES HISTOL')
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'

backup = json.load(open(os.path.join(ROOT,'backups','dxprincipal_backup.json'),encoding='utf-8'))
casos = [b['caso'] for b in backup]
df = get_all_records_as_dataframe().fillna('')
reg_by = {str(df['Numero de caso'].iloc[i]): i for i in range(len(df))}

def dxp_orig(caso):
    fs = sorted(glob.glob(os.path.join(DM, f'debug_map_{caso}_*.json')))
    if not fs: return None
    try:
        return json.load(open(fs[-1],encoding='utf-8')).get('base_datos',{}).get('campos_criticos',{}).get('Diagnostico Principal')
    except Exception:
        return None

conn = get_connection(); cur = conn.cursor()
restaurados = 0; mantenidos = 0; ej_restaurados = []
for caso in casos:
    orig = dxp_orig(caso)
    if orig is None: continue
    i = reg_by.get(caso)
    dxc = str(df['Diagnostico Coloracion'].iloc[i]) if i is not None else ''
    es_frag = (not str(orig).strip()) or any(m in str(orig).upper() for m in _FRAG)
    reemplazar = (es_frag and categorizar_diagnostico(str(orig)) == SIN
                  and dxc.upper() not in ('','N/A','NO APLICA','NO ENCONTRADO','NAN')
                  and any(t in dxc.upper() for t in _TERM_DX))
    if reemplazar:
        cur.execute('UPDATE informes_ihq SET `Diagnostico Principal`=%s WHERE `Numero de caso`=%s', (dxc, caso)); mantenidos += 1
    else:
        cur.execute('UPDATE informes_ihq SET `Diagnostico Principal`=%s WHERE `Numero de caso`=%s', (orig, caso)); restaurados += 1
        if len(ej_restaurados) < 6: ej_restaurados.append({'caso': caso, 'restaurado': str(orig)[:40]})
conn.commit(); conn.close()

out = {'mantenidos_reemplazo': mantenidos, 'restaurados_original': restaurados, 'ejemplos_restaurados': ej_restaurados}
with open(os.path.join(ROOT,'herramientas_ia','resultados','_reeval_dxprincipal.json'),'w',encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
