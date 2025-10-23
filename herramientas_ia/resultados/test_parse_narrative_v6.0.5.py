#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script de validación para parse_narrative_biomarker_list()

Test rápido de la nueva función agregada en v6.0.5
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.extractors.biomarker_extractor import parse_narrative_biomarker_list, BIOMARKER_DEFINITIONS


def test_parse_narrative():
    """Ejecuta tests de validación"""

    print("=" * 80)
    print("TEST DE VALIDACIÓN: parse_narrative_biomarker_list()")
    print("Versión: 6.0.5")
    print("=" * 80)
    print()

    tests = [
        {
            'nombre': 'Test 1: Lista con Y mayúscula',
            'input': 'CKAE1E3, CK7 Y CAM 5.2',
            'esperado': {
                'IHQ_CKAE1AE3': 'POSITIVO',
                'IHQ_CK7': 'POSITIVO',
                'IHQ_CAM52': 'POSITIVO'
            }
        },
        {
            'nombre': 'Test 2: Lista con y minúscula',
            'input': 'GFAP, S100 y SOX10',
            'esperado': {
                'IHQ_GFAP': 'POSITIVO',
                'IHQ_S100': 'POSITIVO',
                'IHQ_SOX10': 'POSITIVO'
            }
        },
        {
            'nombre': 'Test 3: CAM 5.2 con espacio y punto',
            'input': 'CAM 5.2, CK7',
            'esperado': {
                'IHQ_CAM52': 'POSITIVO',
                'IHQ_CK7': 'POSITIVO'
            }
        },
        {
            'nombre': 'Test 4: Texto vacío',
            'input': '',
            'esperado': {}
        },
        {
            'nombre': 'Test 5: Mezcla mayúsculas/minúsculas',
            'input': 'ckae1e3, Ck7 Y cam 5.2',
            'esperado': {
                'IHQ_CKAE1AE3': 'POSITIVO',
                'IHQ_CK7': 'POSITIVO',
                'IHQ_CAM52': 'POSITIVO'
            }
        },
        {
            'nombre': 'Test 6: Caso real IHQ250982 - Lista 1',
            'input': 'CKAE1E3, CK7 Y CAM 5.2',
            'esperado': {
                'IHQ_CKAE1AE3': 'POSITIVO',
                'IHQ_CK7': 'POSITIVO',
                'IHQ_CAM52': 'POSITIVO'
            }
        },
        {
            'nombre': 'Test 7: Caso real IHQ250982 - Lista 2',
            'input': 'GFAP, S100 y SOX10',
            'esperado': {
                'IHQ_GFAP': 'POSITIVO',
                'IHQ_S100': 'POSITIVO',
                'IHQ_SOX10': 'POSITIVO'
            }
        }
    ]

    total_tests = len(tests)
    tests_exitosos = 0
    tests_fallidos = 0

    for i, test in enumerate(tests, 1):
        print(f"[{i}/{total_tests}] {test['nombre']}")
        print(f"  Input: '{test['input']}'")

        try:
            resultado = parse_narrative_biomarker_list(test['input'], BIOMARKER_DEFINITIONS)

            print(f"  Resultado: {resultado}")
            print(f"  Esperado:  {test['esperado']}")

            if resultado == test['esperado']:
                print("  [OK] EXITOSO")
                tests_exitosos += 1
            else:
                print("  [FAIL] FALLIDO")
                print(f"     Diferencias:")

                # Mostrar diferencias
                keys_resultado = set(resultado.keys())
                keys_esperado = set(test['esperado'].keys())

                faltantes = keys_esperado - keys_resultado
                extras = keys_resultado - keys_esperado

                if faltantes:
                    print(f"     - Faltantes: {faltantes}")
                if extras:
                    print(f"     - Extras: {extras}")

                tests_fallidos += 1

        except Exception as e:
            print(f"  [ERROR]: {e}")
            tests_fallidos += 1

        print()

    print("=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)
    print(f"Total tests: {total_tests}")
    print(f"Exitosos: {tests_exitosos} ({tests_exitosos/total_tests*100:.1f}%)")
    print(f"Fallidos: {tests_fallidos} ({tests_fallidos/total_tests*100:.1f}%)")
    print()

    if tests_fallidos == 0:
        print("[OK] TODOS LOS TESTS PASARON EXITOSAMENTE")
        return 0
    else:
        print("[WARNING] ALGUNOS TESTS FALLARON - REVISAR")
        return 1


if __name__ == '__main__':
    sys.exit(test_parse_narrative())
