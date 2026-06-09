# -*- coding: utf-8 -*-
"""Lista los diagnosticos que caen en 'OTRO / NO CATEGORIZADO' (Sin categorizar)."""
import sys, json
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core import database_manager as dm
from core.normalizador_diagnosticos import categorizar_diagnostico_con_organo
from core.normalizador_organos import normalizar_organo, elegir_columna_organo

df = dm.get_all_records_as_dataframe()
dc = "Diagnostico Principal"
co = elegir_columna_organo(df.columns)
org = df[co].apply(normalizar_organo) if co is not None else None

def categ(r):
    o = org.loc[r.name] if (org is not None and r.name in org.index) else None
    return categorizar_diagnostico_con_organo(r[dc], o)

cat = df.apply(categ, axis=1)
mask = cat == "OTRO / NO CATEGORIZADO"
diags = df.loc[mask, dc].astype(str).str.strip()
out = [{"n": n, "diag": d[:220]} for d, n in Counter(diags).most_common(70)]
res = {"total_sin_categorizar": int(mask.sum()), "distintos": int(diags.nunique()), "casos": out}
with open(ROOT + r"\herramientas_ia\resultados\_sincateg.json", "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
print("sin_categorizar:", int(mask.sum()), "| distintos:", int(diags.nunique()))
