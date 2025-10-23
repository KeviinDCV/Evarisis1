#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analizar texto narrativo del caso IHQ250982"""

import json
from pathlib import Path

# Leer debug map
debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")
with open(debug_map_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

texto = data['ocr']['texto_original']

# Extraer caso IHQ250982
inicio = texto.find('IHQ250982')
siguiente = texto.find('IHQ250983', inicio)
caso = texto[inicio:siguiente] if siguiente != -1 else texto[inicio:]

# Extraer sección DESCRIPCIÓN MICROSCÓPICA
inicio_micro = caso.find('DESCRIPCIÓN MICROSCÓPICA')
fin_micro = caso.find('DIAGNÓSTICO', inicio_micro)
desc_microscopica = caso[inicio_micro:fin_micro] if inicio_micro != -1 and fin_micro != -1 else ''

print("="*80)
print("ANÁLISIS DE TEXTO NARRATIVO - IHQ250982")
print("="*80)
print("\n--- DESCRIPCIÓN MICROSCÓPICA COMPLETA ---")
print(desc_microscopica)
print("\n" + "="*80)

# Buscar patrones narrativos
import re

print("\n--- ANÁLISIS DE PATRONES NARRATIVOS ---")

# Patrón 1: "positivas para X, Y y Z"
patron1 = r'positivas?\s+para\s+([^.]+?)(?:\s+y\s+c[eé]lulas|\.|$)'
matches1 = re.finditer(patron1, desc_microscopica, re.IGNORECASE)

print("\n1. Patrón 'positivas para':")
for i, match in enumerate(matches1, 1):
    lista_biomarcadores = match.group(1)
    print(f"   Match {i}: '{lista_biomarcadores}'")

    # Extraer biomarcadores individuales de la lista
    biomarcadores = re.split(r'[,y]+', lista_biomarcadores)
    biomarcadores = [b.strip().upper() for b in biomarcadores if b.strip()]
    print(f"   Biomarcadores: {biomarcadores}")

# Patrón 2: "son positivas para X, Y, Z"
patron2 = r'son\s+positivas?\s+para\s+([^.]+?)(?:\s+y\s+c[eé]lulas|\.|$)'
matches2 = re.finditer(patron2, desc_microscopica, re.IGNORECASE)

print("\n2. Patrón 'son positivas para':")
for i, match in enumerate(matches2, 1):
    lista_biomarcadores = match.group(1)
    print(f"   Match {i}: '{lista_biomarcadores}'")

    # Extraer biomarcadores individuales
    biomarcadores = re.split(r'[,y]+', lista_biomarcadores)
    biomarcadores = [b.strip().upper() for b in biomarcadores if b.strip()]
    print(f"   Biomarcadores: {biomarcadores}")

print("\n" + "="*80)
