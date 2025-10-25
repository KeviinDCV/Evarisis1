#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug de extracción de sección REPORTE DE BIOMARCADORES"""

import sys
import io
import re
from pathlib import Path

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.extractors.biomarker_extractor import extract_narrative_biomarkers

# Texto OCR del PDF IHQ250984 (sección relevante)
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
"""

print("=" * 80)
print("DEBUG: EXTRACCIÓN SECCIÓN REPORTE DE BIOMARCADORES")
print("=" * 80)
print()

# Test 1: Extraer sección REPORTE DE BIOMARCADORES
print("1. EXTRACCIÓN DE SECCIÓN")
print("-" * 80)
match_reporte = re.search(
    r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO|$)',
    texto_pdf,
    re.IGNORECASE | re.DOTALL
)

if match_reporte:
    seccion_reporte = match_reporte.group(1)
    print(f"✓ Sección extraída ({len(seccion_reporte)} caracteres)")
    print()
    print("Contenido de la sección:")
    print("-" * 80)
    print(seccion_reporte[:500])  # Primeros 500 caracteres
    print("-" * 80)
    print()
else:
    print("✗ Sección NO extraída")
    seccion_reporte = ""
    print()

# Test 2: Extraer biomarcadores narrativos de la sección
print("2. EXTRACCIÓN DE BIOMARCADORES NARRATIVOS")
print("-" * 80)

if seccion_reporte:
    resultados = extract_narrative_biomarkers(seccion_reporte)
    print(f"Biomarcadores detectados: {len(resultados)}")
    print()
    for bio, valor in resultados.items():
        print(f"  {bio:25} = {valor}")
    print()
else:
    print("No hay sección para procesar")
    print()

# Test 3: Probar patrones directamente
print("3. TEST DE PATRONES DIRECTOS")
print("-" * 80)

patrones_test = [
    (r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?', 'ER'),
    (r'(?i)-\s*RECEPTORES?\s+DE\s+PROGRESTE?RONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?', 'PR'),
    (r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\(([^)]+)\))?(?:\s+(.+?))?\.?', 'HER2'),
    (r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(?:Tinción\s+nuclear\s+en\s+el\s+)?(\d+)\s*%', 'Ki-67'),
    (r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3', 'GATA3'),
    (r'(?i)negativas?\s+para\s+S[OX]{1,2}[OX]?\s*10', 'SOX10'),
]

for patron, bio_name in patrones_test:
    matches = re.findall(patron, texto_pdf)
    if matches:
        print(f"✓ {bio_name:10} | Patrón: MATCH")
        print(f"             | Captura: {matches}")
    else:
        print(f"✗ {bio_name:10} | Patrón: NO MATCH")
    print()

print("=" * 80)
