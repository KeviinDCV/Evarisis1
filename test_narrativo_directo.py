#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test directo de extracción narrativa con función mejorada"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.extractors.biomarker_extractor import extract_narrative_biomarkers_list, BIOMARKER_DEFINITIONS
import json

# Leer debug map para obtener descripción microscópica
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer caso
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

# Extraer descripción microscópica
inicio_micro = caso.find('DESCRIPCIÓN MICROSCÓPICA')
fin_micro = caso.find('DIAGNÓSTICO', inicio_micro)
desc_microscopica = caso[inicio_micro:fin_micro] if inicio_micro != -1 and fin_micro != -1 else ''

print("="*80)
print("TEST DIRECTO DE EXTRACCIÓN NARRATIVA v6.0.5")
print("="*80)

print("\n--- DESCRIPCIÓN MICROSCÓPICA (primeros 500 caracteres) ---")
print(desc_microscopica[:500])

print("\n--- EJECUTANDO extract_narrative_biomarkers_list() ---")
resultado = extract_narrative_biomarkers_list(desc_microscopica, BIOMARKER_DEFINITIONS)

print(f"\nResultado: {len(resultado)} biomarcadores detectados")
for col, valor in resultado.items():
    print(f"  {col}: {valor}")

print("\n" + "="*80)

# Verificar si función existe
from core.extractors.biomarker_extractor import parse_narrative_biomarker_list
print("\n✅ Función parse_narrative_biomarker_list() importada correctamente")

# Test directo de la nueva función
print("\n--- TEST DIRECTO DE parse_narrative_biomarker_list() ---")
test_text = "CKAE1E3, CK7 Y CAM 5.2"
test_result = parse_narrative_biomarker_list(test_text, BIOMARKER_DEFINITIONS)
print(f"\nInput: '{test_text}'")
print(f"Output: {test_result}")

print("\n" + "="*80)
