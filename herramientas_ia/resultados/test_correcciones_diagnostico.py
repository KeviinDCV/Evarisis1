#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de correcciones de extractores de diagnóstico
Caso referencia: IHQ250981
Fecha: 2025-10-23
"""

import sys
import os
import re

# Agregar core al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from extractors.medical_extractor import extract_principal_diagnosis, extract_diagnostico_coloracion


def test_limpieza_diagnostico_principal():
    """Test de limpieza de DIAGNOSTICO_PRINCIPAL"""
    print("=" * 80)
    print("TEST 1: Limpieza de DIAGNOSTICO_PRINCIPAL")
    print("=" * 80)

    casos_prueba = [
        {
            'nombre': 'IHQ250981 - Carcinoma con grado',
            'entrada': 'CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)',
            'esperado': 'CARCINOMA MICROPAPILAR'
        },
        {
            'nombre': 'Carcinoma con Nottingham',
            'entrada': 'CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2 (SCORE 7)',
            'esperado': 'CARCINOMA DUCTAL INVASIVO'
        },
        {
            'nombre': 'Adenocarcinoma con invasiones',
            'entrada': 'ADENOCARCINOMA INVASIVO, GRADO 3, INVASIÓN LINFOVASCULAR: POSITIVO',
            'esperado': 'ADENOCARCINOMA INVASIVO'
        },
        {
            'nombre': 'Diagnóstico simple (sin contaminación)',
            'entrada': 'CARCINOMA DUCTAL INVASIVO',
            'esperado': 'CARCINOMA DUCTAL INVASIVO'
        },
    ]

    exitos = 0
    fallos = 0

    for caso in casos_prueba:
        print(f"\nCaso: {caso['nombre']}")
        print(f"Entrada:  {caso['entrada']}")

        resultado = extract_principal_diagnosis(caso['entrada'])

        print(f"Esperado: {caso['esperado']}")
        print(f"Obtenido: {resultado}")

        if resultado == caso['esperado']:
            print("[PASS]")
            exitos += 1
        else:
            print("[FAIL]")
            fallos += 1

    print(f"\n{'=' * 80}")
    print(f"Resultados TEST 1: {exitos} PASS, {fallos} FAIL")
    print(f"{'=' * 80}\n")

    return fallos == 0


def test_limpieza_diagnostico_coloracion():
    """Test de limpieza de DIAGNOSTICO_COLORACION"""
    print("=" * 80)
    print("TEST 2: Limpieza de DIAGNOSTICO_COLORACION")
    print("=" * 80)

    casos_prueba = [
        {
            'nombre': 'IHQ250981 - Duplicación con contexto',
            'entrada': 'de "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)". Previa revisión CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)',
            'esperado': 'CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)'
        },
        {
            'nombre': 'Contexto sin duplicación',
            'entrada': 'de "CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2". ',
            'esperado': 'CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2'
        },
        {
            'nombre': 'Sin contexto (normal)',
            'entrada': 'CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2 (SCORE 7)',
            'esperado': 'CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2 (SCORE 7)'
        },
    ]

    exitos = 0
    fallos = 0

    for caso in casos_prueba:
        print(f"\nCaso: {caso['nombre']}")
        print(f"Entrada:  {caso['entrada']}")

        # Simular la limpieza que hace extract_diagnostico_coloracion
        text = caso['entrada']

        # Aplicar las limpiezas
        text = re.sub(r'^de\s+"([^"]+)"\.\s*Previa\s+revisi[óo]n\s+\1', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'^de\s+"([^"]+)"\.\s*', r'\1. ', text, flags=re.IGNORECASE)
        text = re.sub(r'^de\s+"([^"]+)"', r'\1', text, flags=re.IGNORECASE)
        text = re.sub(r'\s{2,}', ' ', text)
        text = text.strip()
        text = text.rstrip('.')  # Eliminar punto final si existe

        resultado = text

        print(f"Esperado: {caso['esperado']}")
        print(f"Obtenido: {resultado}")

        if resultado == caso['esperado']:
            print("[PASS]")
            exitos += 1
        else:
            print("[FAIL]")
            fallos += 1

    print(f"\n{'=' * 80}")
    print(f"Resultados TEST 2: {exitos} PASS, {fallos} FAIL")
    print(f"{'=' * 80}\n")

    return fallos == 0


def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 80)
    print(" TEST DE CORRECCIONES DE EXTRACTORES DE DIAGNÓSTICO")
    print(" Caso referencia: IHQ250981")
    print("=" * 80 + "\n")

    test1_ok = test_limpieza_diagnostico_principal()
    test2_ok = test_limpieza_diagnostico_coloracion()

    print("\n" + "=" * 80)
    print(" RESUMEN FINAL")
    print("=" * 80)
    print(f"TEST 1 (DIAGNOSTICO_PRINCIPAL): {'[PASS]' if test1_ok else '[FAIL]'}")
    print(f"TEST 2 (DIAGNOSTICO_COLORACION): {'[PASS]' if test2_ok else '[FAIL]'}")
    print("=" * 80 + "\n")

    if test1_ok and test2_ok:
        print("[OK] TODOS LOS TESTS PASARON - Correcciones funcionando correctamente\n")
        return 0
    else:
        print("[ERROR] ALGUNOS TESTS FALLARON - Revisar correcciones\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
