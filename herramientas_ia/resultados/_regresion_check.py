# -*- coding: utf-8 -*-
"""Snapshot de categoria por caso (para diff ANTES/DESPUES) + cobertura."""
import sys, json, importlib
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core import database_manager as dm
import core.normalizador_diagnosticos as nd
import core.normalizador_organos as no
importlib.reload(nd); importlib.reload(no)

NO_ONCO = {
    "NEGATIVO PARA MALIGNIDAD", "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA",
    "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO", "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)",
    "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)", "GLIOSIS / LESION REACTIVA SNC",
    "RECHAZO DE TRASPLANTE", "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)", "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)",
    "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)", "MUESTRA INSUFICIENTE / LIMITADA (OTRO)",
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)", "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
    "OTRO / NO CATEGORIZADO", "SIN DATO",
}

df = dm.get_all_records_as_dataframe()
dc = "Diagnostico Principal"
co = no.elegir_columna_organo(df.columns)
org = df[co].apply(no.normalizar_organo) if co is not None else None
cats = []
for i in range(len(df)):
    dx = df[dc].iloc[i]
    o = org.iloc[i] if org is not None else None
    cats.append(nd.categorizar_diagnostico_con_organo(dx, o))

from collections import Counter
dist = Counter(cats)
n_onco = sum(v for k, v in dist.items() if k not in NO_ONCO)
mode = sys.argv[1] if len(sys.argv) > 1 else "new"
out = {
    "n": len(cats),
    "n_onco": n_onco,
    "n_otro": dist.get("OTRO / NO CATEGORIZADO", 0),
    "cats": cats,
    "dx": [str(x)[:120] for x in df[dc].tolist()],
}
with open(ROOT + rf"\herramientas_ia\resultados\_cats_{mode}.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False)
print(f"{mode}: n={len(cats)} n_onco={n_onco} n_otro={out['n_otro']}")
