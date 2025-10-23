#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de Simulación: Corrección de Extractores IHQ250983
Versión: 6.0.6
Fecha: 2025-10-23

Este script prueba las correcciones propuestas SIN modificar el archivo real.
"""

import re
from typing import Dict

# ==============================================================================
# FUNCIÓN DE NORMALIZACIÓN (COPIADA DEL ARCHIVO ORIGINAL)
# ==============================================================================

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


# ==============================================================================
# NUEVA FUNCIÓN: Post-procesamiento con modificadores
# ==============================================================================

def post_process_biomarker_list_with_modifiers(biomarker_text: str) -> Dict[str, str]:
    """
    Procesa lista narrativa de biomarcadores, detectando modificadores individuales.

    Ejemplos:
    - "CKAE1AE3, S100, PAX8 y p40 heterogéneo"
      → {'CKAE1AE3': 'POSITIVO', 'S100': 'POSITIVO', 'PAX8': 'POSITIVO', 'P40': 'POSITIVO HETEROGÉNEO'}
    - "CK7, CK20 focal y TTF-1 difuso"
      → {'CK7': 'POSITIVO', 'CK20': 'POSITIVO FOCAL', 'TTF1': 'POSITIVO DIFUSO'}

    Args:
        biomarker_text: Texto con lista (ej: "CKAE1AE3, S100, PAX8 y p40 heterogéneo")

    Returns:
        Dict con biomarcadores y valores con modificadores
    """
    if not biomarker_text:
        return {}

    result = {}

    # Limpiar texto
    text_clean = biomarker_text.strip()

    # Dividir por comas y "y"/"e"
    parts = re.split(r',\s*|\s+y\s+|\s+e\s+', text_clean, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Detectar modificador al final (heterogéneo, focal, difuso)
        modifier_match = re.search(r'^(.+?)\s+(heterog[eé]neo|focal|difuso)$', part, re.IGNORECASE)

        if modifier_match:
            # Tiene modificador
            biomarker_raw = modifier_match.group(1).strip()
            modifier = modifier_match.group(2).strip().upper()

            # Normalizar modificador
            if modifier in ['HETEROGÉNEO', 'HETEROGENEO']:
                modifier = 'HETEROGÉNEO'

            normalized_name = normalize_biomarker_name(biomarker_raw)
            if normalized_name:
                result[normalized_name] = f'POSITIVO {modifier}'
        else:
            # Sin modificador, solo positivo
            normalized_name = normalize_biomarker_name(part)
            if normalized_name:
                result[normalized_name] = 'POSITIVO'

    return result


# ==============================================================================
# FUNCIÓN DE EXTRACCIÓN MEJORADA (CON CORRECCIONES)
# ==============================================================================

def extract_narrative_biomarkers_v606(text: str) -> Dict[str, str]:
    """
    Versión 6.0.6 - CON CORRECCIONES para IHQ250983

    Extrae biomarcadores del formato narrativo con soporte para:
    - Listas con inmunorreactividad
    - Modificadores (heterogéneo, focal, difuso)
    - Negativos en formato "son negativas para X, Y y Z"
    """
    results = {}

    # NUEVO: V6.0.6 - Patrón para listas narrativas con inmunorreactividad
    # Ej: "inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo"
    # MEJORADO: Captura hasta "y son" o "y células" (para terminar lista antes de negativos)
    immunoreactivity_list_pattern = r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-éÉóÓáÁíÍúÚñÑ]+?)(?=\s+y\s+son|\s+y\s+c[eé]lulas|\s*\.')

    for match in re.finditer(immunoreactivity_list_pattern, text):
        lista_biomarkers = match.group(1).strip()

        print(f"  [DEBUG] Lista capturada: '{lista_biomarkers}'")

        # Usar post-procesador con modificadores
        biomarkers_with_modifiers = post_process_biomarker_list_with_modifiers(lista_biomarkers)

        print(f"  [DEBUG] Biomarcadores procesados: {biomarkers_with_modifiers}")

        # Agregar a resultados (NO sobreescribir)
        for bio_name, bio_value in biomarkers_with_modifiers.items():
            if bio_name not in results:
                results[bio_name] = bio_value

    # Patrón de negativos MEJORADO
    # V6.0.6: Mejorado para capturar "son negativas para X, Y y Z"
    # Termina en punto o fin de texto
    negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9\-]+)*)(?:\s*\.|$)'

    negative_match = re.search(negative_pattern, text)

    if negative_match:
        negative_list = negative_match.group(1)
        print(f"  [DEBUG] Lista de negativos capturada: '{negative_list}'")

        # Dividir por "y" y "," y normalizar nombres
        negative_biomarkers = []
        for part in re.split(r',\s*', negative_list):
            negative_biomarkers.extend([b.strip() for b in re.split(r'\s+y\s+', part)])

        for biomarker in negative_biomarkers:
            normalized_name = normalize_biomarker_name(biomarker)
            if normalized_name:
                results[normalized_name] = 'NEGATIVO'
                print(f"  [DEBUG] Negativo detectado: {normalized_name} = NEGATIVO")

    return results


# ==============================================================================
# CASOS DE PRUEBA
# ==============================================================================

def test_caso_ihq250983():
    """Test del caso IHQ250983"""
    print("=" * 80)
    print("TEST 1: Caso IHQ250983 - Lista con modificador")
    print("=" * 80)

    texto = """
    Se evidencia inmunorreactividad en las células tumorales para
    CKAE1AE3, S100, PAX8 y p40 heterogéneo y son negativas para GATA3, CDX2, y TTF1.
    """

    print(f"\nTexto de entrada:\n{texto.strip()}\n")

    resultados = extract_narrative_biomarkers_v606(texto)

    print("\n--- RESULTADOS ---")
    for bio, valor in sorted(resultados.items()):
        print(f"  {bio}: {valor}")

    # Validar resultados esperados
    print("\n--- VALIDACIÓN ---")
    esperados = {
        'CKAE1AE3': 'POSITIVO',
        'S100': 'POSITIVO',
        'PAX8': 'POSITIVO',
        'P40': 'POSITIVO HETEROGÉNEO',
        'GATA3': 'NEGATIVO',
        'CDX2': 'NEGATIVO',
        'TTF1': 'NEGATIVO'
    }

    todos_ok = True
    for bio, valor_esperado in esperados.items():
        valor_obtenido = resultados.get(bio, 'FALTA')
        if valor_obtenido == valor_esperado:
            print(f"  [OK] {bio}: {valor_esperado}")
        else:
            print(f"  [ERROR] {bio}: Esperado '{valor_esperado}', obtenido '{valor_obtenido}'")
            todos_ok = False

    if todos_ok:
        print("\n[OK] TEST EXITOSO: Todos los biomarcadores se extrajeron correctamente")
    else:
        print("\n[ERROR] TEST FALLIDO: Algunos biomarcadores no coinciden")

    return todos_ok


def test_modificadores_multiples():
    """Test de modificadores múltiples"""
    print("\n" + "=" * 80)
    print("TEST 2: Modificadores múltiples")
    print("=" * 80)

    texto = "positivas para CK7, CK20 focal y TTF-1 difuso"

    print(f"\nTexto de entrada:\n{texto}\n")

    # Simular con patrón de positividad simple
    pattern = r'(?i)positivas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9\-]+(?:\s+heterog[eé]neo|focal|difuso)?)?)'
    match = re.search(pattern, texto)

    if match:
        lista = match.group(1).strip()
        print(f"Lista capturada: '{lista}'")
        resultados = post_process_biomarker_list_with_modifiers(lista)

        print("\n--- RESULTADOS ---")
        for bio, valor in sorted(resultados.items()):
            print(f"  {bio}: {valor}")

        # Validar
        esperados = {
            'CK7': 'POSITIVO',
            'CK20': 'POSITIVO FOCAL',
            'TTF1': 'POSITIVO DIFUSO'
        }

        todos_ok = True
        print("\n--- VALIDACIÓN ---")
        for bio, valor_esperado in esperados.items():
            valor_obtenido = resultados.get(bio, 'FALTA')
            if valor_obtenido == valor_esperado:
                print(f"  [OK] {bio}: {valor_esperado}")
            else:
                print(f"  [ERROR] {bio}: Esperado '{valor_esperado}', obtenido '{valor_obtenido}'")
                todos_ok = False

        if todos_ok:
            print("\n[OK] TEST EXITOSO")
        else:
            print("\n[ERROR] TEST FALLIDO")

        return todos_ok
    else:
        print("[ERROR] No se capturo ningun match")
        return False


def test_sin_modificador():
    """Test de lista sin modificador (regresión)"""
    print("\n" + "=" * 80)
    print("TEST 3: Sin modificador (regresión)")
    print("=" * 80)

    texto = "positivas para CK7 y GATA3"

    print(f"\nTexto de entrada:\n{texto}\n")

    pattern = r'(?i)positivas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9\-]+(?:\s+heterog[eé]neo|focal|difuso)?)?)'
    match = re.search(pattern, texto)

    if match:
        lista = match.group(1).strip()
        print(f"Lista capturada: '{lista}'")
        resultados = post_process_biomarker_list_with_modifiers(lista)

        print("\n--- RESULTADOS ---")
        for bio, valor in sorted(resultados.items()):
            print(f"  {bio}: {valor}")

        # Validar
        esperados = {
            'CK7': 'POSITIVO',
            'GATA3': 'POSITIVO'
        }

        todos_ok = True
        print("\n--- VALIDACIÓN ---")
        for bio, valor_esperado in esperados.items():
            valor_obtenido = resultados.get(bio, 'FALTA')
            if valor_obtenido == valor_esperado:
                print(f"  [OK] {bio}: {valor_esperado}")
            else:
                print(f"  [ERROR] {bio}: Esperado '{valor_esperado}', obtenido '{valor_obtenido}'")
                todos_ok = False

        if todos_ok:
            print("\n[OK] TEST EXITOSO")
        else:
            print("\n[ERROR] TEST FALLIDO")

        return todos_ok
    else:
        print("[ERROR] No se capturo ningun match")
        return False


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("""
================================================================================
                    TEST DE SIMULACION IHQ250983
                      Version 6.0.6 - core-editor
================================================================================

Este script prueba las correcciones propuestas SIN modificar archivos reales.
""")

    # Ejecutar todos los tests
    resultados = []

    resultados.append(("IHQ250983 - Lista con modificador", test_caso_ihq250983()))
    resultados.append(("Modificadores múltiples", test_modificadores_multiples()))
    resultados.append(("Sin modificador (regresión)", test_sin_modificador()))

    # Resumen final
    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)

    total = len(resultados)
    exitosos = sum(1 for _, ok in resultados if ok)
    fallidos = total - exitosos

    for nombre, ok in resultados:
        status = "[PASS]" if ok else "[FAIL]"
        print(f"  {status} - {nombre}")

    print(f"\nTotal: {exitosos}/{total} exitosos, {fallidos}/{total} fallidos")

    if fallidos == 0:
        print("\n[OK] TODOS LOS TESTS PASARON - Las correcciones son seguras para aplicar")
        print("\nProximo paso: Aplicar cambios con core-editor")
    else:
        print("\n[ERROR] ALGUNOS TESTS FALLARON - Revisar correcciones antes de aplicar")
