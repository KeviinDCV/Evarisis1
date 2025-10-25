#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CÓDIGO PROPUESTO - v6.0.11
Función: extract_biomarkers() MEJORADA
Archivo: core/extractors/biomarker_extractor.py
Línea original: 1137

CAMBIO CRÍTICO: Filtra sección "Anticuerpos:" antes de extraer biomarcadores (IHQ250984)
"""

import re
from typing import Dict


def extract_biomarkers(text: str) -> Dict[str, str]:
    """Extrae todos los biomarcadores configurados del texto

    v6.0.11: CRÍTICO - Filtra sección "Anticuerpos:" antes de extraer (IHQ250984)
    v6.0.2: MEJORADO - Prioriza "Expresión molecular" > REPORTE > texto completo (IHQ250981)

    CORRECCIÓN IHQ250984:
    =====================
    La sección "Anticuerpos:" contiene SOLO nombres de reactivos técnicos:
      - RECEPTOR DE ESTRÓGENOS (ER): (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY
      - HER-2/NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT MONOCLONAL ANTIBODY

    Los resultados REALES están en:
      - "REPORTE DE BIOMARCADORES:"
      - "DESCRIPCIÓN MICROSCÓPICA:"

    Este filtro ELIMINA la sección técnica antes de buscar biomarcadores.

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}

    Examples:
        >>> text = "Anticuerpos:\\n- ER: (SP1) ANTIBODY\\n\\nREPORTE DE BIOMARCADORES:\\n-ER: NEGATIVO"
        >>> result = extract_biomarkers(text)
        >>> result['RECEPTOR_ESTROGENOS']
        'NEGATIVO'
    """
    if not text:
        return {}

    # ═══════════════════════════════════════════════════════════════════════
    # V6.0.11: FILTRO CRÍTICO - Eliminar sección "Anticuerpos:" (IHQ250984)
    # ═══════════════════════════════════════════════════════════════════════
    # La sección "Anticuerpos:" contiene SOLO nombres de reactivos técnicos,
    # NO resultados de biomarcadores.
    #
    # Ejemplo de contenido técnico a ELIMINAR:
    #   "RECEPTOR DE ESTRÓGENOS (ER): (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY"
    #   "HER-2/NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT MONOCLONAL ANTIBODY"
    #
    # Los resultados REALES están en:
    #   "REPORTE DE BIOMARCADORES:" o "DESCRIPCIÓN MICROSCÓPICA:"
    #
    # Este regex elimina todo desde "Anticuerpos:" hasta encontrar:
    # - "DESCRIPCIÓN" (inicio de sección de resultados)
    # - "REPORTE" (inicio de bloque de biomarcadores)
    # - "DIAGNÓSTICO" (sección final)
    # - Fin de texto (si no hay más secciones)
    # ═══════════════════════════════════════════════════════════════════════

    text_filtered = text

    # ESTRATEGIA 1: Eliminar todo desde "Anticuerpos:" hasta próxima sección válida
    # Esto elimina completamente la sección técnica de reactivos
    text_filtered = re.sub(
        r'Anticuerpos?:\s*.*?(?=DESCRIPCI[ÓO]N|REPORTE|DIAGN[ÓO]STICO|$)',
        '',
        text_filtered,
        flags=re.IGNORECASE | re.DOTALL
    )

    # ESTRATEGIA 2: Si existe "REPORTE DE BIOMARCADORES:", extraer TODO después de él
    # Esto asegura que busquemos primero en la sección correcta (página 2)
    # El bloque "REPORTE DE BIOMARCADORES:" termina cuando encuentra "DIAGNÓSTICO FINAL"
    match_reporte = re.search(
        r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO\s+FINAL|CONCLUSI[ÓO]N|$)',
        text_filtered,
        re.IGNORECASE | re.DOTALL
    )

    # Si encontramos bloque "REPORTE DE BIOMARCADORES:", usarlo como texto prioritario
    # De lo contrario, usar el texto completo filtrado (sin "Anticuerpos:")
    priority_text = match_reporte.group(1) if match_reporte else text_filtered

    # DEBUG: Descomentar para ver qué texto se está usando
    # print(f"DEBUG: Texto filtrado (primeros 500 chars): {text_filtered[:500]}")
    # print(f"DEBUG: Texto prioritario (primeros 500 chars): {priority_text[:500]}")

    results = {}

    # v6.0.2: PRIORIDAD 1 - Extraer sección "Expresión molecular" PRIMERO (caso IHQ250981)
    # NOTA: Aplicar a texto filtrado (sin "Anticuerpos:")
    molecular_section = extract_molecular_expression_section(text_filtered)

    # v5.3.1: PRIORIDAD 2 - Extraer sección REPORTE (descripción microscópica)
    # NOTA: Aplicar a texto filtrado (sin "Anticuerpos:")
    report_section = extract_report_section(text_filtered)

    # Definir biomarcadores que deben priorizarse de "Expresión molecular"
    # Estos biomarcadores suelen estar en formato estructurado con paréntesis
    molecular_priority = ['ER', 'PR', 'HER2', 'RECEPTOR_ESTROGENOS', 'RECEPTOR_PROGESTERONA']

    # ═══════════════════════════════════════════════════════════════════════
    # FASE 1: Detectar formato narrativo de biomarcadores
    # ═══════════════════════════════════════════════════════════════════════

    # Para ER, PR, HER2: Buscar PRIMERO en "Expresión molecular" (IHQ250981)
    if molecular_section:
        narrative_results = extract_narrative_biomarkers(molecular_section)
        results.update(narrative_results)

    # Si no encontró en "Expresión molecular", buscar en REPORTE
    if not results and report_section:
        narrative_results = extract_narrative_biomarkers(report_section)
        results.update(narrative_results)

    # V6.0.11: CAMBIO CRÍTICO - Buscar en priority_text (bloque "REPORTE DE BIOMARCADORES:")
    # en lugar de texto completo sin filtrar
    # Esto asegura que NO capturemos texto de "Anticuerpos:"
    if not results:
        narrative_results = extract_narrative_biomarkers(priority_text)
        results.update(narrative_results)

    # ═══════════════════════════════════════════════════════════════════════
    # FASE 2: Procesar biomarcadores con patrones específicos
    # ═══════════════════════════════════════════════════════════════════════

    # Procesar cada biomarcador definido en configuración (método original)
    for biomarker_name, definition in BIOMARKER_DEFINITIONS.items():
        # Solo procesar si no fue encontrado por método narrativo
        if biomarker_name not in results:
            value = None

            # Para biomarcadores prioritarios: buscar PRIMERO en "Expresión molecular"
            if biomarker_name.upper() in molecular_priority and molecular_section:
                value = extract_single_biomarker(molecular_section, biomarker_name, definition)

            # Si no encontró en molecular, buscar en REPORTE
            if not value and report_section:
                value = extract_single_biomarker(report_section, biomarker_name, definition)

            # V6.0.11: CAMBIO CRÍTICO - Si no se encontró en REPORTE, buscar en priority_text
            # (bloque "REPORTE DE BIOMARCADORES:" sin sección "Anticuerpos:")
            # en lugar de buscar en texto completo sin filtrar
            if not value:
                value = extract_single_biomarker(priority_text, biomarker_name, definition)

            if value:
                results[biomarker_name] = value

    return results


# ═══════════════════════════════════════════════════════════════════════
# NOTA: Las funciones auxiliares NO requieren cambios:
# - extract_molecular_expression_section()
# - extract_report_section()
# - extract_narrative_biomarkers()
# - extract_single_biomarker()
# - BIOMARKER_DEFINITIONS (configuración)
#
# Todas estas funciones continúan funcionando igual, pero ahora reciben
# texto FILTRADO (sin sección "Anticuerpos:")
# ═══════════════════════════════════════════════════════════════════════
