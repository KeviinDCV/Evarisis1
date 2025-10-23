#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Simulacion: Correccion de Extractores IHQ250983
Version: 6.0.6
"""

import re
from typing import Dict

def normalize_biomarker_name(raw_name: str) -> str:
    """Normaliza nombres de biomarcadores"""
    if not raw_name:
        return None

    raw_clean = raw_name.strip().upper()

    name_mapping = {
        'CK7': 'CK7',
        'CK20': 'CK20',
        'GATA3': 'GATA3',
        'CDX2': 'CDX2',
        'TTF1': 'TTF1',
        'TTF-1': 'TTF1',
        'P40': 'P40',
        'S100': 'S100',
        'PAX8': 'PAX8',
        'PAX-8': 'PAX8',
        'CKAE1AE3': 'CKAE1AE3',
        'CKAE1/AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CKAE1 AE3': 'CKAE1AE3',
    }

    return name_mapping.get(raw_clean)


def post_process_biomarker_list_with_modifiers(biomarker_text: str) -> Dict[str, str]:
    """Procesa lista narrativa detectando modificadores individuales"""
    if not biomarker_text:
        return {}

    result = {}
    text_clean = biomarker_text.strip()

    # Dividir por comas y "y"/"e"
    parts = re.split(r',\s*|\s+y\s+|\s+e\s+', text_clean, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Detectar modificador al final
        modifier_match = re.search(r'^(.+?)\s+(heterogeneo|focal|difuso)$', part, re.IGNORECASE)

        if modifier_match:
            biomarker_raw = modifier_match.group(1).strip()
            modifier = modifier_match.group(2).strip().upper()
            normalized_name = normalize_biomarker_name(biomarker_raw)
            if normalized_name:
                result[normalized_name] = f'POSITIVO {modifier}'
        else:
            normalized_name = normalize_biomarker_name(part)
            if normalized_name:
                result[normalized_name] = 'POSITIVO'

    return result


def extract_narrative_biomarkers_v606(text: str) -> Dict[str, str]:
    """Version 6.0.6 con correcciones para IHQ250983"""
    results = {}

    # Patron inmunorreactividad - captura hasta "y son"
    immunoreactivity_pattern = r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:celulas\s+)?(?:tumorales\s+)?para\s+([^.]+?)(?=\s+y\s+son)'

    for match in re.finditer(immunoreactivity_pattern, text):
        lista = match.group(1).strip()
        print(f"  [DEBUG] Lista positivos: '{lista}'")

        biomarkers_dict = post_process_biomarker_list_with_modifiers(lista)
        print(f"  [DEBUG] Procesados: {biomarkers_dict}")

        for bio_name, bio_value in biomarkers_dict.items():
            if bio_name not in results:
                results[bio_name] = bio_value

    # Patron negativos - captura "son negativas para X, Y y Z"
    negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([^.]+)'

    negative_match = re.search(negative_pattern, text)
    if negative_match:
        negative_list = negative_match.group(1).strip()
        print(f"  [DEBUG] Lista negativos RAW: '{negative_list}'")

        # Dividir por comas, "y", "e" - MEJORADO para manejar ", y X"
        # Primero normalizar ", y" a solo ","
        negative_list_clean = re.sub(r',\s+y\s+', ', ', negative_list)
        parts = re.split(r',\s*|\s+y\s+|\s+e\s+', negative_list_clean)
        print(f"  [DEBUG] Partes divididas: {parts}")

        for part in parts:
            part = part.strip().rstrip('.')
            if part:
                print(f"    [DEBUG] Procesando parte: '{part}'")
                normalized_name = normalize_biomarker_name(part)
                print(f"    [DEBUG] Normalizado: {normalized_name}")
                if normalized_name:
                    results[normalized_name] = 'NEGATIVO'
                    print(f"  [DEBUG] Negativo guardado: {normalized_name}")

    return results


def test_caso_ihq250983():
    """Test del caso IHQ250983"""
    print("=" * 80)
    print("TEST 1: Caso IHQ250983")
    print("=" * 80)

    texto = """
    Se evidencia inmunorreactividad en las celulas tumorales para
    CKAE1AE3, S100, PAX8 y p40 heterogeneo y son negativas para GATA3, CDX2, y TTF1.
    """

    print(f"\nTexto:\n{texto.strip()}\n")

    resultados = extract_narrative_biomarkers_v606(texto)

    print("\n--- RESULTADOS ---")
    for bio, valor in sorted(resultados.items()):
        print(f"  {bio}: {valor}")

    esperados = {
        'CKAE1AE3': 'POSITIVO',
        'S100': 'POSITIVO',
        'PAX8': 'POSITIVO',
        'P40': 'POSITIVO HETEROGENEO',
        'GATA3': 'NEGATIVO',
        'CDX2': 'NEGATIVO',
        'TTF1': 'NEGATIVO'
    }

    print("\n--- VALIDACION ---")
    todos_ok = True
    for bio, esperado in esperados.items():
        obtenido = resultados.get(bio, 'FALTA')
        if obtenido == esperado:
            print(f"  [OK] {bio}: {esperado}")
        else:
            print(f"  [ERROR] {bio}: Esperado '{esperado}', obtenido '{obtenido}'")
            todos_ok = False

    if todos_ok:
        print("\n[OK] TEST EXITOSO")
    else:
        print("\n[ERROR] TEST FALLIDO")

    return todos_ok


if __name__ == "__main__":
    print("""
================================================================================
                    TEST DE SIMULACION IHQ250983
                      Version 6.0.6 - core-editor
================================================================================
""")

    resultado = test_caso_ihq250983()

    print("\n" + "=" * 80)
    if resultado:
        print("[OK] TEST EXITOSO - Correcciones validadas")
        print("\nProximo paso: Aplicar cambios a biomarker_extractor.py")
    else:
        print("[ERROR] TEST FALLIDO - Revisar patrones")
