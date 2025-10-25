#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del flujo COMPLETO que usa el sistema al procesar PDF
Simula exactamente lo que hace unified_extractor.py
"""

import sys
import io
from pathlib import Path

# Configurar UTF-8
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Importar exactamente como lo hace unified_extractor.py
print("=" * 80)
print("TEST DE FLUJO COMPLETO - Simulando unified_extractor.py")
print("=" * 80)
print()

print("1. Importando módulos (como unified_extractor.py)...")
from core.extractors.biomarker_extractor import extract_biomarkers
print("   ✓ Importado extract_biomarkers")
print()

# Texto OCR del PDF IHQ250984
texto_pdf = """
REPORTE DE BIOMARCADORES:
BLOQUE 1.
Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3. Son
negativas para SXO10.
-RECEPTOR DE ESTROGENOS: Negativo.
-RECEPTOR DE PROGRESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 % de las células
tumorales.
-Ki-67: Tinción nuclear en el 60% de las células tumorales.

Anticuerpos:
Estrógeno: CONFIRM anti-Estrogen Receptor (ER) (SP1) Rabbit Monoclonal Primary Antibody.
Progesterona: CONFIRM anti-Progesterone Receptor (ER) (1E2) Rabbit Monoclonal Primary
Antibody. VENTANA Ref. 790-2223.
Her2/Neu: PATHWAY anti-HER-2/Neu (4B5) Rabbit Monoclonal Antibody. VENTANA Ref. 790-4493.
Ki67: anti-Ki67 (30-9) Rabbit Monoclonal Primary Antibody. VENTANA Ref. 790-4286.
"""

print("2. Extrayendo biomarcadores con extract_biomarkers()...")
biomarkers = extract_biomarkers(texto_pdf)
print()

print("3. Resultados:")
print("-" * 80)
for bio, valor in biomarkers.items():
    print(f"  {bio:15} = {repr(valor)}")
print()

print("=" * 80)
print("VERIFICACIÓN ESPECÍFICA DE HER2")
print("=" * 80)
her2_value = biomarkers.get('HER2', 'NO ENCONTRADO')
print(f"Valor capturado: {repr(her2_value)}")
print()

# Verificaciones
if 'PATHWAY' in str(her2_value).upper():
    print("✗ ERROR: Captura texto técnico del reactivo")
    print("  Contiene: 'PATHWAY'")
elif 'POSITIVO' in str(her2_value).upper() and 'SCORE 3+' in str(her2_value).upper():
    print("✓ CORRECTO: Captura solo el resultado")
    print("  Formato: POSITIVO (SCORE 3+)")
elif 'POSITIVO' in str(her2_value).upper():
    print("⚠ PARCIAL: Captura POSITIVO pero sin score")
else:
    print("✗ ERROR: No captura correctamente")

print()
print("=" * 80)
print("MÓDULO CARGADO")
print("=" * 80)
import core.extractors.biomarker_extractor as biomarker_module
print(f"Archivo: {biomarker_module.__file__}")

# Verificar que el patrón está correcto en el código fuente
import inspect
source = inspect.getsource(biomarker_module.extract_narrative_biomarkers)
her2_patterns = [line.strip() for line in source.split('\n') if 'HER' in line and '2' in line and 'POSITIVO' in line]
if her2_patterns:
    print(f"Patrón HER2 en fuente:")
    for pattern in her2_patterns[:2]:  # Primeros 2
        print(f"  {pattern[:100]}...")
