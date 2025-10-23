#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test extracción de factor pronóstico"""

from core.extractors.medical_extractor import extract_factor_pronostico

# Texto completo del caso
texto_completo = """
DESCRIPCIÓN MICROSCÓPICA
Previa revisión de la técnica y verificación del adecuado rendimiento de los controles internos y externos,
se analizan tinciones de Inmunohistoquímica realizadas con técnica de inmunoperoxidasa en la
plataforma automatizada Roche VENTANA®.
En los niveles realizados se observan fragmentos de una lesión neoplásica con celularidad bifásica, una
población de células epiteliales recubriendo estructuras pseudoacinares que son positivas para CKAE1E3,
CK7 Y CAM 5.2 y células mioepiteliales que se distribuyen en un estroma condromixoide, positivas para
GFAP, S100 y SOX10.

DIAGNÓSTICO
Región cervical. Lesión. Biopsia. Estudios de inmunohistoquímica.
LOS HALLAZGOS MORFOLÓGICOS Y DE INMUNOHISTOQUÍMICA FAVORECEN UNA LESIÓN BIFÁSICA CON
COMPONENTE CONDROMIXOIDE Y EPITELIAL SIN NECROSIS.
VER COMENTARIO.
"""

print("="*80)
print("TEST EXTRACCIÓN FACTOR PRONÓSTICO")
print("="*80)

resultado = extract_factor_pronostico(texto_completo)

print(f"\nResultado: \"{resultado}\"")
print("\n" + "="*80)

# Verificar qué debería extraer
print("\nDEBERÍA EXTRAER:")
print("positivo para: CKAE1E3, CK7 Y CAM 5.2 / GFAP, S100 y SOX10")
print("\n" + "="*80)
