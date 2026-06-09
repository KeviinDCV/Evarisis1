# -*- coding: utf-8 -*-
"""Diff ANTES/DESPUES de categorias: detecta regresiones."""
import json
from collections import Counter
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
b = json.load(open(ROOT + r"\herramientas_ia\resultados\_cats_baseline.json", encoding="utf-8"))
n = json.load(open(ROOT + r"\herramientas_ia\resultados\_cats_new.json", encoding="utf-8"))
cb, cn, dx = b["cats"], n["cats"], b["dx"]
assert len(cb) == len(cn), "longitudes distintas"

cambios_otro = []      # baseline == OTRO  (esperado: deben recategorizarse)
cambios_regresion = [] # baseline != OTRO  (PROHIBIDO: regresion)
destino = Counter()
for i in range(len(cb)):
    if cb[i] != cn[i]:
        if cb[i] == "OTRO / NO CATEGORIZADO":
            cambios_otro.append((dx[i], cn[i]))
            destino[cn[i]] += 1
        else:
            cambios_regresion.append((dx[i], cb[i], cn[i]))

print(f"Total casos: {len(cb)}")
print(f"Ex-OTRO recategorizados: {len(cambios_otro)} (esperado 97)")
print(f"REGRESIONES (ya-categorizado que cambio): {len(cambios_regresion)} (debe ser 0)")
print()
print("Destino de los ex-OTRO:")
for k, v in destino.most_common():
    print(f"  {v:3d}  {k}")
if cambios_regresion:
    print("\n!!! REGRESIONES DETECTADAS !!!")
    for dxt, vb, vn in cambios_regresion[:50]:
        print(f"  [{vb}] -> [{vn}]  {dxt!r}")
