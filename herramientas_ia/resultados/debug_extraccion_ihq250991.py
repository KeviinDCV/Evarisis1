#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug de extracción de IHQ_ESTUDIOS_SOLICITADOS para IHQ250991"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.extractors.medical_extractor import extract_biomarcadores_solicitados_robust, parse_biomarker_list
import re

# Simular texto de descripción macroscópica del PDF IHQ250991
texto_simulado = """
DESCRIPCIÓN MACROSCÓPICA
Se recibe material extra-institucional. Previa valoración, se decide realizar marcadores para: BERRP4, BCL2, P63 P40.
DESCRIPCIÓN MICROSCÓPICA
"""

print("=" * 70)
print("DEBUG EXTRACCIÓN IHQ250991 - ESTUDIOS SOLICITADOS")
print("=" * 70)
print()

# PASO 1: Verificar qué captura extract_biomarcadores_solicitados_robust
print("PASO 1: Extracción con función completa")
print("-" * 70)
biomarcadores_extraidos = extract_biomarcadores_solicitados_robust(texto_simulado)
print(f"Biomarcadores extraídos ({len(biomarcadores_extraidos)}):")
for i, bio in enumerate(biomarcadores_extraidos, 1):
    print(f"  {i}. '{bio}'")
print()

# PASO 2: Simular qué texto se captura con el patrón -1
print("PASO 2: Simulación de captura con Patrón -1")
print("-" * 70)
patron = r'(?:Previa\s+valoraci[óo]n.*?)?se\s+decide\s+realizar\s+marcadores?\s+para:\s*([A-Z0-9\s,./\-\(\)pPyYóÓúÚáÁéÉíÍ]+?)(?:\.|$)'
match = re.search(patron, texto_simulado, re.IGNORECASE | re.DOTALL)
if match:
    texto_capturado = match.group(1).strip()
    print(f"Texto capturado: '{texto_capturado}'")
    print(f"Longitud: {len(texto_capturado)} caracteres")
    print(f"Representación: {repr(texto_capturado)}")
    print()
    
    # PASO 3: Parsear con parse_biomarker_list
    print("PASO 3: Parseo con parse_biomarker_list()")
    print("-" * 70)
    biomarcadores_parseados = parse_biomarker_list(texto_capturado)
    print(f"Biomarcadores parseados ({len(biomarcadores_parseados)}):")
    for i, bio in enumerate(biomarcadores_parseados, 1):
        print(f"  {i}. '{bio}'")
    print()
    
    # PASO 4: Aplicar regex manualmente
    print("PASO 4: Aplicar regex de separación manualmente")
    print("-" * 70)
    texto_test = texto_capturado
    
    # Reemplazar "y" por coma
    texto_test = re.sub(r'\s+y\s+', ', ', texto_test, flags=re.IGNORECASE)
    print(f"Después de reemplazar 'y': '{texto_test}'")
    
    # Aplicar patrón 1 (números)
    patron_numeros = r'\b([A-Z]{1,2}[0-9]{1,3}(?:-?[A-Z0-9]{1,3})?)\s+([A-Z]{1,2}[0-9]{1,3}(?:-?[A-Z0-9]{1,3})?)\b'
    texto_test = re.sub(patron_numeros, r'\1, \2', texto_test)
    print(f"Después de patrón números: '{texto_test}'")
    
    # Aplicar patrón 2 (alfanuméricos)
    patron_alfanum = r'\b([A-Z]{2,6}[0-9]{0,2})\s+([A-Z]{2,6}[0-9]{0,2})\b'
    for i in range(3):
        texto_nuevo = re.sub(patron_alfanum, r'\1, \2', texto_test)
        if texto_nuevo == texto_test:
            break
        texto_test = texto_nuevo
        print(f"  Iteración {i+1}: '{texto_test}'")
    
    print(f"Resultado final: '{texto_test}'")
    print()
    
    # Separar por comas
    biomarcadores_finales = [b.strip() for b in texto_test.split(',')]
    print(f"Biomarcadores finales ({len(biomarcadores_finales)}):")
    for i, bio in enumerate(biomarcadores_finales, 1):
        print(f"  {i}. '{bio}'")
else:
    print("❌ NO se encontró match con el patrón")

print()
print("=" * 70)
print("DIAGNÓSTICO")
print("=" * 70)

if len(biomarcadores_extraidos) == 4 and 'P63' in biomarcadores_extraidos and 'P40' in biomarcadores_extraidos:
    print("✅ EXTRACCIÓN CORRECTA - P63 y P40 separados")
else:
    print("❌ PROBLEMA DETECTADO")
    if 'P63 P40' in biomarcadores_extraidos:
        print("   → P63 y P40 NO están separados (aparecen como un solo elemento)")
    else:
        print(f"   → Biomarcadores extraídos: {biomarcadores_extraidos}")
