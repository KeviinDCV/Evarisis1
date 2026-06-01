# -*- coding: utf-8 -*-
"""Auditoria READ-ONLY de calidad de columnas de biomarcadores en produccion.
Detecta: (1) columnas muertas (0 casos), (2) clusters de columnas con nombre
casi-identico (posibles duplicados/typos) y cuanta data tiene cada variante.
NO modifica nada."""
import sqlite3, unicodedata, json, os, re

DB = r'C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
VACIO = ('', 'N/A', 'NO MENCIONADO', 'NO APLICA', 'NAN', 'NONE', 'NULL', 'SIN DATO', 'NO ENCONTRADO')
NO_BIOMARCADOR = {'IHQ_ORGANO', 'IHQ_ESTUDIOS_SOLICITADOS'}

con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
cur = con.cursor()
cols = [r[1] for r in cur.execute('PRAGMA table_info(informes_ihq)').fetchall()]
ihq = [c for c in cols if c.upper().startswith('IHQ_') and c.upper() not in NO_BIOMARCADOR]

# Conteo de casos con valor real por columna
counts = {}
for c in ihq:
    rows = cur.execute(f'SELECT "{c}" FROM informes_ihq').fetchall()
    counts[c] = sum(1 for (v,) in rows if v is not None and str(v).strip().upper() not in VACIO)
con.close()

def norm(c):
    s = c.upper().replace('IHQ_', '')
    for suf in ('_ESTADO', '_PORCENTAJE', '_PCT'):
        if s.endswith(suf):
            s = s[:-len(suf)]
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if unicodedata.category(ch) != 'Mn')
    return ''.join(ch for ch in s if ch.isalnum())

def lev(a, b):
    if a == b:
        return 0
    la, lb = len(a), len(b)
    if abs(la - lb) > 2:
        return 99
    prev = list(range(lb + 1))
    for i in range(1, la + 1):
        cur_row = [i] + [0] * lb
        for j in range(1, lb + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            cur_row[j] = min(prev[j] + 1, cur_row[j-1] + 1, prev[j-1] + cost)
        prev = cur_row
    return prev[lb]

# Clustering por nombre normalizado casi-identico (Levenshtein <= 2)
normmap = {c: norm(c) for c in ihq}
parent = {c: c for c in ihq}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

def clusterable(n):
    # Excluir marcadores CD/CK distinguidos por numero (CD20, CK7, CD79A...) -> NO son duplicados
    if re.match(r'^C[DK]\d{1,3}[A-Z]?$', n):
        return False
    return len(n) >= 5

ihq_sorted = sorted(ihq)
for i in range(len(ihq_sorted)):
    for j in range(i+1, len(ihq_sorted)):
        a, b = ihq_sorted[i], ihq_sorted[j]
        na, nb = normmap[a], normmap[b]
        if not clusterable(na) or not clusterable(nb):
            continue
        # mismo cluster si distancia<=2 o uno es prefijo del otro
        if lev(na, nb) <= 2 or (na.startswith(nb) or nb.startswith(na)):
            union(a, b)

clusters = {}
for c in ihq:
    clusters.setdefault(find(c), []).append(c)
dupes = {k: v for k, v in clusters.items() if len(v) > 1}

muertas = sorted([c for c in ihq if counts[c] == 0])
pobladas = sorted([c for c in ihq if counts[c] > 0], key=lambda c: -counts[c])

res = {
    'total_columnas_biomarcador': len(ihq),
    'pobladas': len(pobladas),
    'muertas_0_casos': len(muertas),
    'lista_muertas': muertas,
    'clusters_duplicados': [
        {'variantes': sorted(v, key=lambda c: -counts[c]),
         'conteos': {c: counts[c] for c in sorted(v, key=lambda c: -counts[c])},
         'casos_total_si_se_unen': sum(counts[c] for c in v)}
        for v in sorted(dupes.values(), key=lambda v: -sum(counts[c] for c in v))
    ],
}
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'auditar_columnas_biomarcadores_resultado.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)

print(f"Columnas biomarcador: {len(ihq)} | pobladas: {len(pobladas)} | MUERTAS (0 casos): {len(muertas)}")
print(f"\n=== CLUSTERS DE POSIBLES DUPLICADOS (nombre casi-identico) ===")
for cl in res['clusters_duplicados']:
    pares = ', '.join(f"{c}={cl['conteos'][c]}" for c in cl['variantes'])
    print(f"  [{pares}]")
print(f"\n=== COLUMNAS MUERTAS (0 casos, candidatas a depurar) ===")
print('  ' + ', '.join(muertas))
print(f"\nJSON: {out}")
