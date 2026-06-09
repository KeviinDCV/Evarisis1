# -*- coding: utf-8 -*-
"""Diff a nivel de BUCKET de cobertura (no nombre exacto), para validar que
los renames/splits no sacaron ningún caso de 'oncológico' ni dejaron OTRO."""
import json
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"

GRUPO_NO_NEOPLASICO = {
    "NEGATIVO PARA MALIGNIDAD", "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO",
    "GLIOSIS / LESION REACTIVA SNC", "RECHAZO DE TRASPLANTE",
    "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)",
    "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)", "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)",
    "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
}
GRUPO_SIN_DX = {
    "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)", "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)",
    "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA", "MUESTRA INSUFICIENTE / LIMITADA (OTRO)",
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)",
}

def bucket(cat):
    if cat == "OTRO / NO CATEGORIZADO": return "OTRO"
    if cat == "SIN DATO": return "SINDATO"
    if cat in GRUPO_NO_NEOPLASICO: return "NO-NEOPLASICO"
    if cat in GRUPO_SIN_DX: return "SIN-DX"
    return "ONCOLOGICO"

b = json.load(open(ROOT + r"\herramientas_ia\resultados\_cats_baseline.json", encoding="utf-8"))
n = json.load(open(ROOT + r"\herramientas_ia\resultados\_cats_new.json", encoding="utf-8"))
cb, cn, dx = b["cats"], n["cats"], b["dx"]

bb = [bucket(c) for c in cb]
bn = [bucket(c) for c in cn]
print("Buckets BASELINE:", dict(Counter(bb)))
print("Buckets NUEVO   :", dict(Counter(bn)))
print()
trans = Counter()
perdidos_cancer = []
for i in range(len(cb)):
    if bb[i] != bn[i]:
        trans[(bb[i], bn[i])] += 1
        # HARMFUL: estaba oncológico y dejó de estarlo (sin venir de OTRO)
        if bb[i] == "ONCOLOGICO" and bn[i] != "ONCOLOGICO":
            perdidos_cancer.append((dx[i], cb[i], cn[i]))
print("Transiciones de bucket:")
for (a, c), v in trans.most_common():
    print(f"  {v:3d}  {a:14} -> {c}")
print(f"\n*** Casos ONCOLOGICOS que se PERDIERON (harmful): {len(perdidos_cancer)} (debe ser 0) ***")
for dxt, vb, vn in perdidos_cancer[:30]:
    print(f"  [{vb}] -> [{vn}]  {dxt!r}")
