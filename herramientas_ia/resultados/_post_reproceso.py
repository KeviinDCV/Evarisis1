# -*- coding: utf-8 -*-
"""Estado tras el reproceso: total, distribución de categorías y detalle de los
casos en 'CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)' (¿dx real o problema?)."""
import sys, os, json
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.normalizador_diagnosticos import categorizar_diagnostico, categorizar_diagnostico_con_organo
from core.normalizador_organos import normalizar_organo, elegir_columna_organo
CAT = 'CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)'

df = get_all_records_as_dataframe().fillna('')
co = elegir_columna_organo(df.columns)
org = df[co].apply(normalizar_organo) if co is not None else None
cat_con = df.apply(lambda r: categorizar_diagnostico_con_organo(
    r['Diagnostico Principal'], org.loc[r.name] if (org is not None and r.name in org.index) else None), axis=1)

dist = Counter(cat_con)
SIN = 'SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)'
IHQ = 'ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)'
# detalle de los casos en la categoría escamocelular genérica
detalle = []
org_counter = Counter()
for i in range(len(df)):
    if cat_con.iloc[i] != CAT: continue
    o = str(org.iloc[i]) if org is not None else ''
    org_counter[o] += 1
    if len(detalle) < 18:
        detalle.append({'caso': str(df['Numero de caso'].iloc[i]),
                        'dx': str(df['Diagnostico Principal'].iloc[i])[:55], 'organo': o})

out = {'total_registros': len(df),
       'SIN_DIAGNOSTICO': dist.get(SIN, 0),
       'ESTUDIO_IHQ': dist.get(IHQ, 0),
       'escamocelular_generico_total': dist.get(CAT, 0),
       'escamocelular_por_organo': dict(org_counter.most_common()),
       'top12_categorias': dict(dist.most_common(12)),
       'ejemplos_escamocelular': detalle}
with open(os.path.join(ROOT, 'herramientas_ia', 'resultados', '_post_reproceso.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('total', len(df), 'SIN', dist.get(SIN,0), 'ESTUDIO_IHQ', dist.get(IHQ,0), 'escamo_generico', dist.get(CAT,0))
