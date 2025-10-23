#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test directo del patrón corregido v6.0.4.1"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.extractors.medical_extractor import extract_biomarcadores_solicitados_robust

# Leer debug map
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer solo caso IHQ250982
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

print("="*80)
print("TEST PATRÓN CORREGIDO v6.0.4.1")
print("="*80)
print(f"\nLongitud texto caso: {len(caso)} caracteres")

# Buscar fragmento relevante
fragmento_inicio = caso.find('Se revisan')
fragmento_fin = caso.find('DESCRIPCIÓN MICROSCÓPICA')
fragmento = caso[fragmento_inicio:fragmento_fin] if fragmento_inicio != -1 and fragmento_fin != -1 else ""

print(f"\n--- FRAGMENTO DESCRIPCIÓN MACROSCÓPICA ---")
print(repr(fragmento[:300]))

# Test función
resultado = extract_biomarcadores_solicitados_robust(caso)

print(f"\n--- RESULTADO EXTRACCIÓN ---")
print(f"Biomarcadores encontrados: {len(resultado)}")
print(f"Lista: {resultado}")

print("\n" + "="*80)

if resultado:
    print("✅ EXTRACCIÓN EXITOSA")
else:
    print("❌ NO SE ENCONTRARON BIOMARCADORES")
    print("\nPosibles causas:")
    print("1. El patrón no coincide con el texto")
    print("2. Problema de encoding")
    print("3. El texto no llega a la función correctamente")
