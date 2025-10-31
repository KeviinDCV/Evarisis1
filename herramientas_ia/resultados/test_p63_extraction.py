#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test de extracción de P63 y BER-EP4

Verifica que extract_narrative_biomarkers capture correctamente estos biomarcadores
"""

import sys
from pathlib import Path

# Agregar path del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.extractors.biomarker_extractor import extract_narrative_biomarkers, normalize_biomarker_name

# Texto del caso IHQ250991
texto_test = """
Las células tumorales basaloides presentan marcación positiva para: p40, p63, EBERP4/Ep-CAM, BCL2.
"""

print("="*80)
print("TEST: Extracción de P63 y BER-EP4 (IHQ250991)")
print("="*80)

print("\n📝 Texto de entrada:")
print(texto_test.strip())

print("\n🔬 Probando normalize_biomarker_name:")
test_names = ["p63", "P63", "EBERP4", "Ep-CAM", "BER-EP4", "BERRP4", "p40", "BCL2"]
for name in test_names:
    normalized = normalize_biomarker_name(name)
    print(f"  {name:15} → {normalized}")

print("\n🔍 Ejecutando extract_narrative_biomarkers:")
resultados = extract_narrative_biomarkers(texto_test)

print(f"\n✅ Biomarcadores extraídos: {len(resultados)}")
for bio, valor in resultados.items():
    print(f"  - {bio}: {valor}")

print("\n🎯 Verificación:")
esperados = ["P40", "P63", "BER_EP4", "BCL2"]
for bio in esperados:
    if bio in resultados:
        print(f"  ✅ {bio}: {resultados[bio]}")
    else:
        print(f"  ❌ {bio}: NO EXTRAÍDO")

print("\n" + "="*80)
