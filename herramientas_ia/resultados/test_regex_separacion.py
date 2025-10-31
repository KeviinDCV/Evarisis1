#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test del regex de separación de biomarcadores - ENFOQUE DUAL"""

import re

def aplicar_regex_dual(texto):
    """Aplica enfoque dual: patrón original + patrón mejorado"""
    
    # PATRÓN 1 (ORIGINAL): Biomarcadores con números
    patron_numeros = r'\b([A-Z]{1,2}[0-9]{1,3}(?:-?[A-Z0-9]{1,3})?)\s+([A-Z]{1,2}[0-9]{1,3}(?:-?[A-Z0-9]{1,3})?)\b'
    texto = re.sub(patron_numeros, r'\1, \2', texto)
    
    # PATRÓN 2 (MEJORADO): Biomarcadores alfanuméricos (letras + números opcionales)
    patron_alfanum = r'\b([A-Z]{2,6}[0-9]{0,2})\s+([A-Z]{2,6}[0-9]{0,2})\b'
    for _ in range(3):  # Hasta 3 iteraciones
        texto_nuevo = re.sub(patron_alfanum, r'\1, \2', texto)
        if texto_nuevo == texto:
            break
        texto = texto_nuevo
    
    return texto

# Texto de prueba
texto_original = "BERRP4, BCL2, P63 P40"

print("=" * 60)
print("TEST REGEX DE SEPARACIÓN - ENFOQUE DUAL")
print("=" * 60)
print(f"Texto original: '{texto_original}'")
print()

texto_con_regex = aplicar_regex_dual(texto_original)
print(f"Después del regex: '{texto_con_regex}'")
print()

# Separar por comas
biomarcadores = [b.strip() for b in texto_con_regex.split(',')]
print(f"Biomarcadores separados ({len(biomarcadores)}):")
for i, bio in enumerate(biomarcadores, 1):
    print(f"  {i}. '{bio}'")
print()

# Casos de prueba adicionales
casos_prueba = [
    ("P63 P40", "P63, P40"),  # Con números
    ("P16 Ki-67", "P16 Ki-67"),  # Ki-67 NO debe separarse (es un solo biomarcador)
    ("CD3 CD5", "CD3, CD5"),  # Con números
    ("HER2 Ki-67", "HER2 Ki-67"),  # Ki-67 NO debe separarse
    ("P63 P40 BCL2", "P63, P40 BCL2"),  # PATRÓN 1 solo captura primeros 2
    ("RE RP", "RE, RP"),  # Solo letras - PATRÓN 2
    ("MLH1 MSH2 MSH6 PMS2", "MLH1, MSH2, MSH6, PMS2"),  # Solo letras - PATRÓN 2 con iteraciones
]

print("=" * 60)
print("CASOS DE PRUEBA ADICIONALES")
print("=" * 60)

total_casos = len(casos_prueba)
casos_correctos = 0

for caso, esperado in casos_prueba:
    resultado = aplicar_regex_dual(caso)
    es_correcto = resultado == esperado
    if es_correcto:
        casos_correctos += 1
    
    marca = "✅" if es_correcto else "❌"
    print(f"{marca} '{caso}' → '{resultado}'")
    if not es_correcto:
        print(f"   Esperado: '{esperado}'")

print()
print("=" * 60)
print("DIAGNÓSTICO:")
print("=" * 60)

porcentaje = (casos_correctos / total_casos) * 100
print(f"Casos correctos: {casos_correctos}/{total_casos} ({porcentaje:.0f}%)")
print()

if casos_correctos == total_casos:
    print("✅ ENFOQUE DUAL FUNCIONA PERFECTAMENTE")
elif casos_correctos >= 5:
    print(f"✅ ENFOQUE DUAL FUNCIONA BIEN ({porcentaje:.0f}%)")
else:
    print(f"⚠️  ENFOQUE DUAL TIENE PROBLEMAS ({porcentaje:.0f}%)")


