# -*- coding: utf-8 -*-
"""READ-ONLY: distribucion de datos de los 5 clusters de biomarcadores duplicados.
Para cada cluster (canonica primero) reporta: conteo por columna, casos con dato
SOLO en una variante (=> hay que MOVER a la canonica antes de eliminar), y conflictos
(canonica y variante con valores DIFERENTES)."""
import sqlite3, json, os

DB = r'C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
V = ('', 'N/A', 'NO MENCIONADO', 'NO APLICA', 'NAN', 'NONE', 'NULL', 'SIN DATO', 'NO ENCONTRADO')
def ok(v): return v is not None and str(v).strip().upper() not in V

CLUSTERS = {
    'Calretinina': ['IHQ_CALRETININA', 'IHQ_CALRETININ', 'IHQ_CALRRETININA'],
    'Desmina':     ['IHQ_DESMINA', 'IHQ_DESMIN'],
    'CK34betaE12': ['IHQ_CK34BETAE12', 'IHQ_CK34BE12', 'IHQ_CK34BETA12'],
    'Mamoglobina': ['IHQ_MAMOGLOBINA', 'IHQ_MAMAGLOBINA'],
    'Miogenina':   ['IHQ_MIOGENINA', 'IHQ_MYOGENIN'],
}

con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
cur = con.cursor()
allcols = [r[1] for r in cur.execute('PRAGMA table_info(informes_ihq)').fetchall()]
res = {}
for nombre, columnas in CLUSTERS.items():
    canon = columnas[0]
    variantes = columnas[1:]
    existen = {c: (c in allcols) for c in columnas}
    sel = ','.join(f'"{c}"' for c in columnas if c in allcols)
    rows = cur.execute(f'SELECT "Numero de caso",{sel} FROM informes_ihq').fetchall()
    presentes = [c for c in columnas if c in allcols]
    idx = {c: i+1 for i, c in enumerate(presentes)}
    counts = {c: 0 for c in presentes}
    solo_variante = []   # casos con dato en variante pero NO en canonica
    conflictos = []      # canonica y variante con valor distinto
    union = 0
    for row in rows:
        caso = row[0]
        vals = {c: row[idx[c]] for c in presentes}
        for c in presentes:
            if ok(vals[c]):
                counts[c] += 1
        canon_ok = canon in presentes and ok(vals.get(canon))
        var_ok = any(ok(vals.get(c)) for c in variantes if c in presentes)
        if canon_ok or var_ok:
            union += 1
        if (not canon_ok) and var_ok:
            quien = [c for c in variantes if c in presentes and ok(vals.get(c))]
            solo_variante.append((caso, {c: vals[c] for c in quien}))
        if canon_ok and var_ok:
            for c in variantes:
                if c in presentes and ok(vals.get(c)) and str(vals[c]).strip() != str(vals[canon]).strip():
                    conflictos.append((caso, canon, str(vals[canon]), c, str(vals[c])))
    res[nombre] = {
        'canonica': canon, 'existen': existen, 'counts': counts,
        'union_real': union, 'n_solo_variante': len(solo_variante),
        'solo_variante_ejemplos': solo_variante[:10], 'n_conflictos': len(conflictos),
        'conflictos_ejemplos': conflictos[:10],
    }
con.close()

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'investigar_clusters_resultado.json')
json.dump(res, open(out, 'w', encoding='utf-8'), indent=2, ensure_ascii=False, default=str)

for nombre, r in res.items():
    print(f"\n=== {nombre} (canonica: {r['canonica']}) ===")
    print('  existen:', {k: v for k, v in r['existen'].items()})
    print('  counts :', r['counts'])
    print(f"  union real: {r['union_real']} | SOLO en variante (mover): {r['n_solo_variante']} | conflictos: {r['n_conflictos']}")
    if r['n_solo_variante']:
        print('   ejemplos solo-variante:', r['solo_variante_ejemplos'][:5])
    if r['n_conflictos']:
        print('   ejemplos conflicto:', r['conflictos_ejemplos'][:5])
print('\nJSON:', out)
