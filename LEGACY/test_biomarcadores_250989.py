#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test de extracción de biomarcadores para IHQ250989
UBICACIÓN: LEGACY/ - Script temporal de testing
Verifica: BCL6, MUM1, CD20+, CD138/CD38+
"""

import sys
import os
import re

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.extractors.biomarker_extractor import extract_biomarkers, BIOMARKER_DEFINITIONS, normalize_biomarker_value

# Texto de IHQ250989 (descripción microscópica)
texto_microscopica = """
Previa valoración de la técnica y verificación de la adecuada tinción de los controles externos e internos 
se realizan estudios de inmunohistoquímica en la plataforma automatizada Roche VENTANA®. Se identifica 
población dispersa de linfocitos B (CD20+), sin formación de cúmulos. Las células plasmáticas (CD38+) 
distribuidas de manera dispersa y sin agregados. BCL6 Negativo. Los marcadores MUM-1 negativo. 
Índice de proliferación KI-67 del 5%.
"""

print("="*80)
print("TEST: Extracción de Biomarcadores - IHQ250989")
print("="*80)

print(f"\n📝 Texto microscópica:")
print(texto_microscopica.strip())

# Extraer biomarcadores
print(f"\n🔍 Extrayendo biomarcadores...")
biomarkers = extract_biomarkers(texto_microscopica)

print(f"\n✅ Biomarcadores extraídos: {len(biomarkers)}")
for name, value in biomarkers.items():
    print(f"   {name}: {value}")

# Verificar específicamente los problemáticos
print(f"\n📊 Verificación de biomarcadores solicitados:")

# CD20
cd20 = biomarkers.get('IHQ_CD20', 'NO EXTRAÍDO')
print(f"   CD20: {cd20} {'✅' if cd20 == 'POSITIVO' else '❌ (esperado: POSITIVO)'}")

# CD138 (CD38)
cd138 = biomarkers.get('IHQ_CD138', 'NO EXTRAÍDO')
print(f"   CD138/CD38: {cd138} {'✅' if cd138 == 'POSITIVO' else '❌ (esperado: POSITIVO)'}")

# BCL6
bcl6 = biomarkers.get('IHQ_BCL6', 'NO EXTRAÍDO')
print(f"   BCL6: {bcl6} {'✅' if bcl6 == 'NEGATIVO' else '❌ (esperado: NEGATIVO)'}")

# MUM1
mum1 = biomarkers.get('IHQ_MUM1', 'NO EXTRAÍDO')
print(f"   MUM1: {mum1} {'✅' if mum1 == 'NEGATIVO' else '❌ (esperado: NEGATIVO)'}")

# Ki-67
ki67 = biomarkers.get('IHQ_KI-67', 'NO EXTRAÍDO')
print(f"   Ki-67: {ki67} {'✅' if ki67 == '5%' else '❌ (esperado: 5%)'}")

# Resumen
print(f"\n📋 RESUMEN:")
total_solicitados = 5
total_extraidos = sum([
    1 if cd20 == 'POSITIVO' else 0,
    1 if cd138 == 'POSITIVO' else 0,
    1 if bcl6 == 'NEGATIVO' else 0,
    1 if mum1 == 'NEGATIVO' else 0,
    1 if ki67 == '5%' else 0,
])
cobertura = (total_extraidos / total_solicitados) * 100
print(f"   Cobertura: {total_extraidos}/{total_solicitados} ({cobertura:.0f}%)")

if total_extraidos == total_solicitados:
    print(f"\n🎉 ¡ÉXITO! Todos los biomarcadores extraídos correctamente")
else:
    print(f"\n⚠️  Faltan {total_solicitados - total_extraidos} biomarcadores")

# Test normalización de "+"
print(f"\n🧪 Test normalización símbolo '+':")
test_values = ["CD20+", "CD38+", "POSITIVO", "negativo", "5%"]
for test_val in test_values:
    normalized = normalize_biomarker_value(test_val, {}, 'CATEGORICAL')
    print(f"   '{test_val}' → '{normalized}'")
