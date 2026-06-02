# -*- coding: utf-8 -*-
"""Valida el categorizador de diagnósticos con comparación ANTES/DESPUÉS.
Primera corrida: guarda baseline. Siguientes: compara per-caso y verifica que
NINGÚN caso que ya tenía categoría real cambie (solo se permite OTRO/NO
CATEGORIZADO -> nueva categoría). READ-ONLY sobre la BD."""
import os, sys, json, sqlite3, importlib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, ROOT)
import pandas as pd
import core.normalizador_diagnosticos as nd
import core.normalizador_organos as no
importlib.reload(nd); importlib.reload(no)

con = sqlite3.connect('file:data/huv_oncologia_NUEVO.db?mode=ro', uri=True)
df = pd.read_sql_query('SELECT "Numero de caso","Diagnostico Principal","Organo","IHQ_ORGANO" FROM informes_ihq', con)
con.close()
co = no.elegir_columna_organo(df.columns)
on = df[co].apply(no.normalizar_organo) if co is not None else None
cats = df.apply(lambda r: nd.categorizar_diagnostico_con_organo(
    r['Diagnostico Principal'], on.loc[r.name] if (on is not None and r.name in on.index) else None), axis=1)
actual = {str(df.loc[i, 'Numero de caso']): cats.loc[i] for i in df.index}

BASE = os.path.join('herramientas_ia', 'resultados', '_cat_baseline.json')
OTRO = 'OTRO / NO CATEGORIZADO'
n_otro = sum(1 for v in actual.values() if v == OTRO)

if not os.path.exists(BASE):
    json.dump(actual, open(BASE, 'w', encoding='utf-8'), ensure_ascii=False)
    print('BASELINE guardado. OTRO/NO CATEGORIZADO:', n_otro, '| total:', len(actual))
else:
    base = json.load(open(BASE, encoding='utf-8'))
    regresiones = []   # caso que tenia categoria REAL y cambio
    mejoras = {}       # OTRO -> nueva categoria (conteo)
    for caso, nueva in actual.items():
        vieja = base.get(caso)
        if vieja is None:
            continue
        if vieja != nueva:
            if vieja == OTRO:
                mejoras[nueva] = mejoras.get(nueva, 0) + 1
            else:
                regresiones.append((caso, vieja, nueva))
    res = {
        'otro_antes': sum(1 for v in base.values() if v == OTRO),
        'otro_despues': n_otro,
        'recuperados': sum(mejoras.values()),
        'mejoras_por_categoria': dict(sorted(mejoras.items(), key=lambda x: -x[1])),
        'n_regresiones': len(regresiones),
        'regresiones_ejemplos': regresiones[:30],
    }
    json.dump(res, open(os.path.join('herramientas_ia', 'resultados', 'validar_categorizador_resultado.json'),
                        'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    print('=== COMPARACION ANTES/DESPUES ===')
    print('OTRO antes:', res['otro_antes'], '-> despues:', res['otro_despues'], f"(recuperados {res['recuperados']})")
    print('REGRESIONES (categoria real que cambio):', res['n_regresiones'])
    if regresiones:
        for c, vj, nv in regresiones[:30]:
            print(f'   !! {c}: {vj}  ->  {nv}')
    print('Recuperados por categoria:')
    for k, v in res['mejoras_por_categoria'].items():
        print(f'   +{v:4}  {k}')
