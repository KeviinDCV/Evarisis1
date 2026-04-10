#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test directo del código V6.2.14 desde el extractor real
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.extractors.medical_extractor import process_medical_descriptions

# Datos reales de IHQ251030
macro = 'Se recibe orden para realización de inmunohistoquímica en material extrainstitucional rotulado como "M2501720 bloque A7" que corresponde a "Tumor de estomago. Gastrectomía total.". y con'

micro = 'Previa valoración de la técnica y verificación de la adecuada tinción de los controles externos e internos se realizan estudios de inmunohistoquímica en la plataforma automatizada Roche VENTANA®. Pruebas realizadas en la muestra / número: M2501720 A7. HER2 : NEGATIVO (Score 0) diagnóstico de "ADENOCARCINOMA INTESTINAL INVASIVO MODERADAMENTE DIFERENCIADO". Previa revisión de la histología se realizan niveles histológicos para tinción con: Her2.'

results = {
    'descripcion_macroscopica_se_recibe': macro,  # V6.2.14 busca en estos campos
    'descripcion_microscopica_final': micro
}

print("=" * 80)
print("TEST: process_medical_descriptions con datos reales IHQ251030")
print("=" * 80)
print()
print("ANTES:")
print(f"Macro ({len(macro)} chars): '{macro}'")
print(f"Micro ({len(micro)} chars): '{micro[:100]}...'")
print()

results_after = process_medical_descriptions(results, "")

print()
print("DESPUES:")
print(f"Macro ({len(results_after['descripcion_macroscopica_final'])} chars):")
print(f"  '{results_after['descripcion_macroscopica_final']}'")
print()
print(f"Micro ({len(results_after['descripcion_microscopica_final'])} chars):")
print(f"  '{results_after['descripcion_microscopica_final'][:100]}...'")
print()

# Validar
if results_after['descripcion_macroscopica_final'] != macro:
    print("[OK] Macro fue modificada")
else:
    print("[FAIL] Macro NO fue modificada")

if 'diagnóstico de "ADENOCARCINOMA' in results_after['descripcion_macroscopica_final']:
    print("[OK] Macro contiene el texto esperado")
else:
    print("[FAIL] Macro NO contiene el texto esperado")
