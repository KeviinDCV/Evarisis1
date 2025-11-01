#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Prueba: Correcciones para IHQ250995
==============================================

Valida las correcciones propuestas para resolver:
1. Fragmentacin en IHQ_ESTUDIOS_SOLICITADOS ("RACEMASA EN, LAS")
2. Normalizacin de "34BETA"  "34BE12"
3. Extraccin de "prdida de expresin"  NEGATIVO
4. Patrn complejo "prdida de X con marcacin positiva para Y"

Versin: 1.0.0
Fecha: 2025-10-31
"""

import re
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 
# VERSIN ORIGINAL (con bugs)
# 

def parse_biomarker_list_ORIGINAL(text: str) -> List[str]:
    """Versin ORIGINAL con el bug de fragmentacin"""
    if not text:
        return []

    text = text.strip()

    # Reemplazar "y" por comas
    text = re.sub(r'\s+y\s+', ', ', text, flags=re.IGNORECASE)

    # Convertir a maysculas
    text_upper = text.upper()

    # Dividir por comas
    biomarcadores = [b.strip() for b in text_upper.split(',')]

    # Filtrar vacos
    biomarcadores_filtrados = []
    for bio in biomarcadores:
        if len(bio) < 2:
            continue

        # BUG: Este filtro se ejecuta DESPUS de dividir, por lo que no elimina "EN" y "LAS"
        if re.search(r'(?:bloque|laminas?|para|con|los|siguiente|almacenamiento)', bio, re.IGNORECASE):
            continue

        biomarcadores_filtrados.append(bio)

    return biomarcadores_filtrados


def normalize_biomarker_name_simple_ORIGINAL(name: str) -> str:
    """Versin ORIGINAL sin normalizacin de 34BETA"""
    if not name:
        return ''

    name = re.sub(r'\s+', ' ', name.strip())
    nombre_upper = name.upper()

    # Mapeo ORIGINAL (sin 34BETA)
    simple_mapping = {
        'CKAE1/AE3': 'CKAE1AE3',
        'CKAE1 / AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CAM 5.2': 'CAM5.2',
        'CAM5.2': 'CAM5.2',
    }

    for pattern, result in simple_mapping.items():
        if pattern in nombre_upper:
            return result

    return name


# 
# VERSIN CORREGIDA (con fixes)
# 

def parse_biomarker_list_FIXED(text: str) -> List[str]:
    """Versin CORREGIDA que limpia contexto ANTES de dividir"""
    if not text:
        return []

    text = text.strip()

    #  FIX 1: Limpiar contexto ANTES de procesar
    # Eliminar frases contextuales que no son biomarcadores
    text = re.sub(r'\s+en\s+las?\s+(?:tres|dos|cuatro|una)?\s*(?:laminas?|bloques?)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^.*?para\s+tinci[oa]n\s+con\s+', '', text, flags=re.IGNORECASE)  # Eliminar todo hasta "para tincion con"
    text = re.sub(r'\s+en\s+el\s+bloque\s+[A-Z0-9]+', '', text, flags=re.IGNORECASE)

    logger.info(f" Texto limpio: '{text}'")

    # Reemplazar "y" por comas
    text = re.sub(r'\s+y\s+', ', ', text, flags=re.IGNORECASE)

    # Convertir a maysculas
    text_upper = text.upper()

    # Dividir por comas
    biomarcadores = [b.strip() for b in text_upper.split(',')]

    # Filtrar vacos y texto residual
    biomarcadores_filtrados = []
    for bio in biomarcadores:
        if len(bio) < 2:
            continue

        # Filtrar palabras sueltas que no son biomarcadores
        if bio.upper() in ['EN', 'LAS', 'LOS', 'CON', 'PARA', 'DE']:
            logger.info(f" Filtrado palabra residual: '{bio}'")
            continue

        if re.search(r'(?:bloque|laminas?|para|con|los|siguiente|almacenamiento)', bio, re.IGNORECASE):
            logger.info(f" Filtrado por contexto: '{bio}'")
            continue

        biomarcadores_filtrados.append(bio)

    return biomarcadores_filtrados


def normalize_biomarker_name_simple_FIXED(name: str) -> str:
    """Versin CORREGIDA con normalizacin de 34BETA"""
    if not name:
        return ''

    name = re.sub(r'\s+', ' ', name.strip())
    nombre_upper = name.upper()

    #  FIX 2: Mapeo ampliado con 34BETA
    simple_mapping = {
        'CKAE1/AE3': 'CKAE1AE3',
        'CKAE1 / AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CAM 5.2': 'CAM5.2',
        'CAM5.2': 'CAM5.2',
        # NUEVO: Normalizar 34BETA
        '34BETA': '34BE12',
        '34 BETA': '34BE12',
        'CK34BETA': '34BE12',
        'CK34 BETA': '34BE12',
        'CK34BETAE12': '34BE12',
        'CK34 BETA E12': '34BE12',
        'CK34BETA E12': '34BE12',
    }

    for pattern, result in simple_mapping.items():
        if pattern in nombre_upper:
            logger.info(f" Normalizado: '{name}'  '{result}'")
            return result

    return name


def extract_narrative_biomarkers_ORIGINAL(text: str) -> Dict[str, str]:
    """Versin ORIGINAL que NO detecta 'prdida de expresin'"""
    results = {}

    # Solo detecta "marcacin positiva/negativa"
    marcacion_list_pattern = r'(?i)(?:presentan\s+)?marcaci[o]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?=\s+adems|\.\s*(?:En|A\d+\.)|$)'
    for match in re.finditer(marcacion_list_pattern, text, re.DOTALL):
        estado = 'POSITIVO' if 'positiva' in match.group(1).lower() else 'NEGATIVO'
        lista_biomarkers_raw = match.group(2).strip()
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            if bio_raw.upper() not in results:
                results[bio_raw.upper()] = estado

    return results


def extract_narrative_biomarkers_FIXED(text: str) -> Dict[str, str]:
    """Versin CORREGIDA que detecta 'prdida de expresin' y patrones complejos"""
    results = {}

    #  FIX 3: NUEVO patron para "perdida/ausencia de expresion"
    # Soporta variantes sin acentos (perdida, expresion) y con acentos (prdida, expresin)
    perdida_pattern = r'(?i)(?:p[e]rdida|ausencia|sin)\s+de\s+expresi[oa]n\s+para[:\s]+(.+?)(?:\s+con\s+marcaci[oa]n|\.|$)'
    for match in re.finditer(perdida_pattern, text, re.DOTALL):
        lista_biomarkers_raw = match.group(1).strip()
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            bio_norm = normalize_biomarker_name_simple_FIXED(bio_raw)
            if bio_norm and bio_norm.upper() not in results:
                results[bio_norm.upper()] = 'NEGATIVO'
                logger.info(f" Prdida de expresin: '{bio_raw}'  {bio_norm.upper()} = NEGATIVO")

    #  FIX 4: NUEVO patron complejo "perdida de X con marcacion positiva para Y"
    # Soporta variantes sin acentos
    complejo_pattern = r'(?i)(?:p[e]rdida|ausencia)\s+de\s+expresi[oa]n\s+para[:\s]+(.+?)\s+con\s+marcaci[oa]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?:\.|$)'
    for match in re.finditer(complejo_pattern, text, re.DOTALL):
        # Grupo 1: biomarcadores NEGATIVOS
        negativos_raw = match.group(1).strip()
        negativos = re.split(r'[,;]\s*|\s+y\s+', re.sub(r'\s*\n\s*', ' ', negativos_raw))

        for bio_raw in negativos:
            bio_norm = normalize_biomarker_name_simple_FIXED(bio_raw.strip().rstrip('.'))
            if bio_norm and bio_norm.upper() not in results:
                results[bio_norm.upper()] = 'NEGATIVO'
                logger.info(f" Prdida (complejo): '{bio_raw}'  {bio_norm.upper()} = NEGATIVO")

        # Grupo 2+3: estado y biomarcadores POSITIVOS/NEGATIVOS
        estado = 'POSITIVO' if 'positiva' in match.group(2).lower() else 'NEGATIVO'
        positivos_raw = match.group(3).strip()
        positivos = re.split(r'[,;]\s*|\s+y\s+', re.sub(r'\s*\n\s*', ' ', positivos_raw))

        for bio_raw in positivos:
            bio_norm = normalize_biomarker_name_simple_FIXED(bio_raw.strip().rstrip('.'))
            if bio_norm and bio_norm.upper() not in results:
                results[bio_norm.upper()] = estado
                logger.info(f" Marcacin (complejo): '{bio_raw}'  {bio_norm.upper()} = {estado}")

    # Patron original para "marcacion positiva/negativa" (mantener compatibilidad)
    # Soporta variantes sin acentos
    marcacion_list_pattern = r'(?i)(?:presentan\s+)?marcaci[oa]n\s+(positiva|negativa)\s+para[:\s]+(.+?)(?=\s+ademas|\.\s*(?:En|A\d+\.)|$)'
    for match in re.finditer(marcacion_list_pattern, text, re.DOTALL):
        estado = 'POSITIVO' if 'positiva' in match.group(1).lower() else 'NEGATIVO'
        lista_biomarkers_raw = match.group(2).strip()
        lista_biomarkers_raw = re.sub(r'\s*\n\s*', ' ', lista_biomarkers_raw)
        biomarcadores_encontrados = re.split(r'[,;]\s*|\s+y\s+', lista_biomarkers_raw)

        for bio_raw in biomarcadores_encontrados:
            bio_raw = bio_raw.strip().rstrip('.')
            if not bio_raw:
                continue

            bio_norm = normalize_biomarker_name_simple_FIXED(bio_raw)
            if bio_norm and bio_norm.upper() not in results:
                results[bio_norm.upper()] = estado
                logger.info(f" Marcacin simple: '{bio_raw}'  {bio_norm.upper()} = {estado}")

    return results


# 
# CASOS DE PRUEBA
# 

def test_parse_biomarker_list():
    """Test para parse_biomarker_list"""
    print("\n" + "="*80)
    print("TEST 1: parse_biomarker_list - Fragmentacin 'RACEMASA EN, LAS'")
    print("="*80)

    texto_test = "p63, 34BETA y racemasa en las tres laminas"

    print(f"\n Texto de entrada:")
    print(f"   '{texto_test}'")

    print(f"\n VERSIN ORIGINAL (con bug):")
    resultado_original = parse_biomarker_list_ORIGINAL(texto_test)
    print(f"   Resultado: {resultado_original}")
    print(f"   Problema:  Contiene fragmentos 'EN', 'LAS' o texto incompleto")

    print(f"\n VERSIN CORREGIDA:")
    resultado_fixed = parse_biomarker_list_FIXED(texto_test)
    print(f"   Resultado: {resultado_fixed}")
    print(f"   Esperado: ['P63', '34BETA', 'RACEMASA']")

    # Validacin
    esperado = {'P63', '34BETA', 'RACEMASA'}
    obtenido = set(resultado_fixed)

    if obtenido == esperado:
        print(f"\n    TEST PASADO: Los biomarcadores son correctos")
    else:
        print(f"\n    TEST FALLIDO:")
        print(f"      Esperado: {esperado}")
        print(f"      Obtenido: {obtenido}")
        print(f"      Faltantes: {esperado - obtenido}")
        print(f"      Extras: {obtenido - esperado}")


def test_normalize_biomarker_name():
    """Test para normalize_biomarker_name_simple"""
    print("\n" + "="*80)
    print("TEST 2: normalize_biomarker_name_simple - Normalizacin '34BETA'  '34BE12'")
    print("="*80)

    casos_test = [
        ("34BETA", "34BE12"),
        ("34 BETA", "34BE12"),
        ("CK34BETA", "34BE12"),
        ("CK34 BETA E12", "34BE12"),
        ("P63", "P63"),  # No debe cambiar
        ("RACEMASA", "RACEMASA"),  # No debe cambiar
    ]

    print(f"\n Casos de prueba:")

    for entrada, esperado in casos_test:
        original = normalize_biomarker_name_simple_ORIGINAL(entrada)
        fixed = normalize_biomarker_name_simple_FIXED(entrada)

        print(f"\n   Entrada: '{entrada}'")
        print(f"    Original: '{original}'")
        print(f"    Corregido: '{fixed}'")
        print(f"   Esperado: '{esperado}'")

        if fixed == esperado:
            print(f"       CORRECTO")
        else:
            print(f"       INCORRECTO (esperado: '{esperado}', obtenido: '{fixed}')")


def test_extract_narrative_biomarkers():
    """Test para extract_narrative_biomarkers"""
    print("\n" + "="*80)
    print("TEST 3: extract_narrative_biomarkers - 'Prdida de expresin' + Patrn Complejo")
    print("="*80)

    texto_test = """
    Sin embargo se reconoce un foco de 1 mm ( corresponde a 3 glandulas) con perdida de
    expresion para CK34 BETA E12 y P63 con marcacion positiva para Racemasa.
    """

    print(f"\n Texto de entrada:")
    print(f"{texto_test}")

    print(f"\n VERSIN ORIGINAL (con bug):")
    resultado_original = extract_narrative_biomarkers_ORIGINAL(texto_test)
    print(f"   Resultado: {resultado_original}")
    print(f"   Problema:  NO detecta 'prdida de expresin'")
    print(f"   Problema:  Solo captura 'marcacin positiva para Racemasa'")

    print(f"\n VERSIN CORREGIDA:")
    resultado_fixed = extract_narrative_biomarkers_FIXED(texto_test)
    print(f"   Resultado: {resultado_fixed}")
    print(f"   Esperado: {{'34BE12': 'NEGATIVO', 'P63': 'NEGATIVO', 'RACEMASA': 'POSITIVO'}}")

    # Validacin
    esperado = {
        '34BE12': 'NEGATIVO',
        'P63': 'NEGATIVO',
        'RACEMASA': 'POSITIVO'
    }

    print(f"\n   Validacin:")
    todo_correcto = True

    for bio, estado_esperado in esperado.items():
        estado_obtenido = resultado_fixed.get(bio, '(NO ENCONTRADO)')
        if estado_obtenido == estado_esperado:
            print(f"       {bio}: {estado_obtenido} (correcto)")
        else:
            print(f"       {bio}: esperado '{estado_esperado}', obtenido '{estado_obtenido}'")
            todo_correcto = False

    if todo_correcto:
        print(f"\n    TEST PASADO: Todos los biomarcadores correctos")
    else:
        print(f"\n    TEST FALLIDO: Hay discrepancias")


def test_integracion_completa():
    """Test de integracin completa con datos reales de IHQ250995"""
    print("\n" + "="*80)
    print("TEST 4: INTEGRACIN COMPLETA - Caso IHQ250995")
    print("="*80)

    # Datos reales del PDF (sin acentos como queda despues de procesar)
    desc_macro = "para tincion con p63, 34BETA y racemasa en las tres laminas"
    desc_micro = """
    Sin embargo se reconoce un foco de 1 mm ( corresponde a 3 glandulas) con perdida de
    expresion para CK34 BETA E12 y P63 con marcacion positiva para Racemasa.
    """

    print(f"\n PASO 1: Extraer estudios solicitados (Descripcin Macroscpica)")
    print(f"   Texto: '{desc_macro}'")

    estudios_solicitados = parse_biomarker_list_FIXED(desc_macro)
    print(f"\n    Estudios solicitados extrados: {estudios_solicitados}")

    # Normalizar nombres
    estudios_normalizados = [normalize_biomarker_name_simple_FIXED(bio) for bio in estudios_solicitados]
    ihq_estudios_solicitados = ', '.join(estudios_normalizados)

    print(f"    IHQ_ESTUDIOS_SOLICITADOS: '{ihq_estudios_solicitados}'")
    print(f"   Esperado: 'P63, 34BE12, RACEMASA'")

    print(f"\n PASO 2: Extraer resultados (Descripcin Microscpica)")
    print(f"   Texto: {desc_micro}")

    resultados = extract_narrative_biomarkers_FIXED(desc_micro)
    print(f"\n    Resultados extrados: {resultados}")

    print(f"\n RESUMEN FINAL:")
    print(f"   {'Campo':<30} {'Valor Actual (BD)':<25} {'Valor Corregido':<25} {'Estado'}")
    print(f"   {'-'*30} {'-'*25} {'-'*25} {'-'*10}")

    # IHQ_ESTUDIOS_SOLICITADOS
    actual_estudios = "P63, 34BETA, RACEMASA EN, LAS"
    corregido_estudios = ihq_estudios_solicitados
    estado_estudios = " CORREGIDO" if "EN" not in corregido_estudios and "LAS" not in corregido_estudios else " ERROR"
    print(f"   {'IHQ_ESTUDIOS_SOLICITADOS':<30} {actual_estudios:<25} {corregido_estudios:<25} {estado_estudios}")

    # IHQ_P63
    actual_p63 = "POSITIVO"
    corregido_p63 = resultados.get('P63', '(NO ENCONTRADO)')
    estado_p63 = " CORREGIDO" if corregido_p63 == "NEGATIVO" else " ERROR"
    print(f"   {'IHQ_P63':<30} {actual_p63:<25} {corregido_p63:<25} {estado_p63}")

    # IHQ_RACEMASA
    actual_racemasa = "(vaco)"
    corregido_racemasa = resultados.get('RACEMASA', '(NO ENCONTRADO)')
    estado_racemasa = " CORREGIDO" if corregido_racemasa == "POSITIVO" else " ERROR"
    print(f"   {'IHQ_RACEMASA':<30} {actual_racemasa:<25} {corregido_racemasa:<25} {estado_racemasa}")

    # IHQ_34BE12
    actual_34be12 = "(no existe columna)"
    corregido_34be12 = resultados.get('34BE12', '(NO ENCONTRADO)')
    estado_34be12 = " CORREGIDO" if corregido_34be12 == "NEGATIVO" else " ERROR"
    print(f"   {'IHQ_34BE12':<30} {actual_34be12:<25} {corregido_34be12:<25} {estado_34be12}")

    # Validacin final
    print(f"\n{'='*80}")
    if all([
        "EN" not in corregido_estudios,
        "LAS" not in corregido_estudios,
        corregido_p63 == "NEGATIVO",
        corregido_racemasa == "POSITIVO",
        corregido_34be12 == "NEGATIVO"
    ]):
        print("   TODOS LOS TESTS PASADOS - Las correcciones funcionan correctamente")
    else:
        print("   ALGUNOS TESTS FALLARON - Revisar implementacin")
    print(f"{'='*80}\n")


# 
# MAIN
# 

if __name__ == "__main__":
    print("\n")
    print("+" + "="*78 + "+")
    print("|" + " "*20 + "TEST DE CORRECCIONES - IHQ250995" + " "*26 + "|")
    print("+" + "="*78 + "+")

    print("\nEste script valida las correcciones propuestas para resolver:")
    print("   1. Fragmentacion en IHQ_ESTUDIOS_SOLICITADOS")
    print("   2. Normalizacion de 34BETA -> 34BE12")
    print("   3. Deteccion de 'perdida de expresion' -> NEGATIVO")
    print("   4. Patron complejo con multiples estados")

    try:
        # Ejecutar tests
        test_parse_biomarker_list()
        test_normalize_biomarker_name()
        test_extract_narrative_biomarkers()
        test_integracion_completa()

        print("\n" + "="*80)
        print("EJECUCION COMPLETADA")
        print("="*80)
        print("\nSi todos los tests pasaron, las correcciones estan listas para aplicarse.")
        print("Archivos a modificar:")
        print("  - core/extractors/medical_extractor.py (parse_biomarker_list + normalize)")
        print("  - core/extractors/biomarker_extractor.py (extract_narrative_biomarkers)")
        print("\n")

    except Exception as e:
        logger.error(f"Error durante la ejecucion: {e}", exc_info=True)
        print("\nLa ejecucion fallo. Revisar el traceback arriba.")
