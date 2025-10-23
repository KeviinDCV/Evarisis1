#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extraer secciones de diagnóstico del caso IHQ250982"""

import json
from pathlib import Path

# Leer debug map
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_035542.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer caso IHQ250982
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

print("="*80)
print("CASO IHQ250982 - EXTRACCIÓN DE DIAGNÓSTICOS")
print("="*80)

# Buscar sección DIAGNÓSTICO
inicio_diag = caso.find('DIAGNÓSTICO')
if inicio_diag == -1:
    inicio_diag = caso.find('DIAGNOSTICO')

if inicio_diag != -1:
    # Buscar fin de diagnóstico (siguiente sección o fin)
    secciones = ['MALIGNIDAD', 'FECHA', 'ÓRGANO', 'RESPONSABLE', 'IHQ']
    fin_diag = len(caso)
    for seccion in secciones:
        pos = caso.find(seccion, inicio_diag + 20)
        if pos != -1 and pos < fin_diag:
            fin_diag = pos

    diagnostico_completo = caso[inicio_diag:fin_diag].strip()
    print("\n--- SECCIÓN DIAGNÓSTICO COMPLETA ---")
    print(diagnostico_completo)
    print("\n" + "="*80)

# Buscar DESCRIPCIÓN MACROSCÓPICA (contiene estudios solicitados)
inicio_macro = caso.find('DESCRIPCIÓN MACROSCÓPICA')
if inicio_macro == -1:
    inicio_macro = caso.find('DESCRIPCION MACROSCOPICA')

if inicio_macro != -1:
    fin_macro = caso.find('DESCRIPCIÓN MICROSCÓPICA', inicio_macro)
    if fin_macro == -1:
        fin_macro = caso.find('DESCRIPCION MICROSCOPICA', inicio_macro)

    if fin_macro == -1:
        fin_macro = inicio_macro + 500

    desc_macro = caso[inicio_macro:fin_macro].strip()
    print("\n--- DESCRIPCIÓN MACROSCÓPICA ---")
    print(desc_macro)
    print("\n" + "="*80)

# Buscar DESCRIPCIÓN MICROSCÓPICA (puede contener diagnóstico)
inicio_micro = caso.find('DESCRIPCIÓN MICROSCÓPICA')
if inicio_micro == -1:
    inicio_micro = caso.find('DESCRIPCION MICROSCOPICA')

if inicio_micro != -1:
    fin_micro = caso.find('DIAGNÓSTICO', inicio_micro)
    if fin_micro == -1:
        fin_micro = caso.find('DIAGNOSTICO', inicio_micro)

    if fin_micro == -1:
        fin_micro = inicio_micro + 800

    desc_micro = caso[inicio_micro:fin_micro].strip()
    print("\n--- DESCRIPCIÓN MICROSCÓPICA ---")
    print(desc_micro[:800])
    print("\n" + "="*80)
