#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test para ver qué claves contiene extracted_data"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.unified_extractor import extract_ihq_data
import json

# Leer debug map
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_034221.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer caso
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

# Extraer datos
datos_extraidos = extract_ihq_data(caso)

# Filtrar solo biomarcadores IHQ
biomarcadores = {k: v for k, v in datos_extraidos.items() if k.startswith('IHQ_')}

print("="*80)
print("BIOMARCADORES EN extracted_data")
print("="*80)
for key, valor in biomarcadores.items():
    print(f"{key}: {valor}")
print(f"\nTotal: {len(biomarcadores)} biomarcadores")
