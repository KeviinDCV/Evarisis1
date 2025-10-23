#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test completo de extracción IHQ250982"""

import sys
import json
import logging
from pathlib import Path

# Configurar logging mínimo
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.unified_extractor import extract_ihq_data
from core.extractors.medical_extractor import extract_medical_data, extract_biomarcadores_solicitados_robust

# Leer debug map
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer solo caso IHQ250982
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

# Escribir resultados a archivo
with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write("="*80 + "\n")
    f.write("TEST EXTRACCIÓN COMPLETA IHQ250982\n")
    f.write("="*80 + "\n")

    # Test 1: extract_biomarcadores_solicitados_robust directamente
    f.write("\n--- TEST 1: FUNCIÓN DIRECTA ---\n")
    resultado_directo = extract_biomarcadores_solicitados_robust(caso)
    f.write(f"Biomarcadores (directo): {resultado_directo}\n")

    # Test 2: extract_medical_data
    f.write("\n--- TEST 2: EXTRACT_MEDICAL_DATA ---\n")
    medical_data = extract_medical_data(caso)
    f.write(f"estudios_solicitados: {medical_data.get('estudios_solicitados', 'N/A')}\n")

    # Test 3: extract_ihq_data completo
    f.write("\n--- TEST 3: EXTRACT_IHQ_DATA COMPLETO ---\n")
    resultado_completo = extract_ihq_data(caso)
    f.write(f"IHQ_ESTUDIOS_SOLICITADOS: {resultado_completo.get('IHQ_ESTUDIOS_SOLICITADOS', 'N/A')}\n")
    f.write(f"estudios_solicitados_tabla: {resultado_completo.get('estudios_solicitados_tabla', 'N/A')}\n")
    f.write(f"FACTOR_PRONOSTICO: {resultado_completo.get('FACTOR_PRONOSTICO', 'N/A')}\n")
    f.write(f"IHQ_CK7: {resultado_completo.get('IHQ_CK7', 'N/A')}\n")
    f.write(f"IHQ_CKAE1_AE3: {resultado_completo.get('IHQ_CKAE1_AE3', 'N/A')}\n")

    f.write("\n" + "="*80 + "\n")

print("Resultados guardados en test_results.txt")
