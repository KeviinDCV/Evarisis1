"""
PRUEBA DE CORRECCIÓN: extract_biomarcadores_solicitados_robust()
=================================================================
Fecha: 2025-10-22
Versión: v6.0.3
Cambio: Agregar soporte para dos puntos después de "con" en patrones 3 y 4

ANTES: "para tinción con X, Y, Z" ✅
       "para tinción con: X, Y, Z" ❌ (NO capturaba)

DESPUÉS: "para tinción con X, Y, Z" ✅
         "para tinción con: X, Y, Z" ✅ (AHORA captura)
"""

import sys
import os

# Agregar ruta del proyecto
sys.path.insert(0, r'C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV9GESTOR_ONCOLOGIA')

from core.extractors.medical_extractor import extract_biomarcadores_solicitados_robust

# TEXTO DE PRUEBA (caso IHQ250981)
texto_macro = '''Se recibe orden para realización de inmunohistoquímica en material institucional rotulado como
«M2506442» que corresponde a "tumor mama izquierda. Mastectomía radical" y con diagnóstico
de «CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)». Previa revisión
de la histología se realizan niveles histológicos para tinción con: E-Cadherina, Progesterona,
Estrógenos, Her2, Ki67.

DESCRIPCIÓN MICROSCÓPICA
...
'''

print("=" * 80)
print("PRUEBA DE CORRECCIÓN v6.0.3")
print("=" * 80)
print()
print("TEXTO DE PRUEBA:")
print("-" * 80)
print(texto_macro[:400] + "...")
print("-" * 80)
print()

# EJECUTAR EXTRACCIÓN
resultado = extract_biomarcadores_solicitados_robust(texto_macro)

print("RESULTADO:")
print("-" * 80)
print(f"Lista extraída: {resultado}")
print(f"Total biomarcadores: {len(resultado)}")
print("-" * 80)
print()

# VALIDACIÓN
esperado = ['E-Cadherina', 'Progesterona', 'Estrógenos', 'HER2', 'Ki-67']
print("VALIDACIÓN:")
print("-" * 80)
print(f"Esperado: {esperado}")
print(f"Obtenido: {resultado}")

if len(resultado) == 5:
    print("\n✅ CORRECCIÓN EXITOSA: Se capturaron los 5 biomarcadores")
    print("✅ El patrón 'para tinción con:' ahora funciona correctamente")
else:
    print(f"\n❌ ERROR: Se esperaban 5 biomarcadores, se obtuvieron {len(resultado)}")
    print("❌ La corrección NO funcionó como se esperaba")

print("=" * 80)
