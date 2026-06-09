# -*- coding: utf-8 -*-
"""Investiga los buckets genéricos: 'REVISAR (EXTRACCION)' y 'NEOPLASIA
MALIGNA A CLASIFICAR (OTRO)'. Muestra dx + órgano de cada caso."""
import sys, json
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core import database_manager as dm
import core.normalizador_diagnosticos as nd
import core.normalizador_organos as no

df = dm.get_all_records_as_dataframe()
dc = "Diagnostico Principal"
co = no.elegir_columna_organo(df.columns)
org = df[co].apply(no.normalizar_organo) if co is not None else None

rows = []
for i in range(len(df)):
    dx = df[dc].iloc[i]
    o = org.iloc[i] if org is not None else None
    cat = nd.categorizar_diagnostico_con_organo(dx, o)
    rows.append((cat, str(dx)[:160], str(o)))

def dump(target):
    sub = [(dx, o) for c, dx, o in rows if c == target]
    print(f"\n===== {target} : {len(sub)} casos =====")
    print("--- órganos (campo Organo del caso) ---")
    for org_v, n in Counter(o for _, o in sub).most_common():
        print(f"  {n:3d}  {org_v}")
    print("--- diagnósticos (texto) ---")
    for dx, o in sub:
        print(f"  [{o[:22]:22}] {dx}")

res = {}
for t in ["SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)",
          "NEOPLASIA MALIGNA A CLASIFICAR (OTRO)"]:
    sub = [(dx, o) for c, dx, o in rows if c == t]
    res[t] = {"n": len(sub), "organos": dict(Counter(o for _, o in sub).most_common()),
              "casos": [{"dx": dx, "organo": o} for dx, o in sub]}
    dump(t)
with open(ROOT + r"\herramientas_ia\resultados\_buckets.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
