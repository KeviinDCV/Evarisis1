#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Debug para IHQ250984 - Analizar Flujo de Extracción
v6.0.12 - Debug profundo para identificar por qué no extrae correctamente

Uso:
    python herramientas_ia/debug_extraccion_IHQ250984.py

Genera:
    herramientas_ia/resultados/DEBUG_IHQ250984_[timestamp].md
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

# Agregar path para importar módulos del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.extractors.biomarker_extractor import (
    extract_biomarkers,
    extract_narrative_biomarkers,
    extract_molecular_expression_section,
    extract_report_section
)
from core.processors.ocr_processor import extract_text_from_pdf

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════

PDF_PATH = "pdfs_patologia/IHQ250984.pdf"
OUTPUT_DIR = "herramientas_ia/resultados"

# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES DE DEBUG
# ═══════════════════════════════════════════════════════════════════════

def debug_step(step_name, content, max_chars=500):
    """Imprime un paso de debug con contenido limitado"""
    print(f"\n{'='*80}")
    print(f"PASO: {step_name}")
    print(f"{'='*80}")

    if content is None:
        print("❌ CONTENIDO: None (vacío)")
    elif isinstance(content, str):
        print(f"✅ LONGITUD: {len(content)} caracteres")
        print(f"PREVIEW (primeros {max_chars} chars):")
        print(f"---")
        print(content[:max_chars])
        if len(content) > max_chars:
            print(f"... (+ {len(content) - max_chars} caracteres más)")
        print(f"---")
    elif isinstance(content, dict):
        print(f"✅ DICCIONARIO con {len(content)} keys:")
        for key, value in content.items():
            print(f"  - {key}: {value[:100] if isinstance(value, str) else value}")
    else:
        print(f"✅ TIPO: {type(content)}")
        print(f"CONTENIDO: {str(content)[:max_chars]}")


def buscar_en_texto(texto, patron, nombre_patron):
    """Busca un patrón en el texto y muestra resultados"""
    print(f"\n🔍 Buscando: {nombre_patron}")
    print(f"   Patrón: {patron}")

    matches = re.findall(patron, texto, re.IGNORECASE | re.DOTALL)

    if matches:
        print(f"   ✅ ENCONTRADO: {len(matches)} coincidencia(s)")
        for i, match in enumerate(matches[:3], 1):  # Mostrar máximo 3
            if isinstance(match, tuple):
                print(f"      Match {i}: {match}")
            else:
                print(f"      Match {i}: {match[:200]}")
    else:
        print(f"   ❌ NO ENCONTRADO")

    return matches


def verificar_secciones_clave(texto):
    """Verifica presencia de secciones clave en el texto"""
    print(f"\n{'='*80}")
    print("VERIFICACIÓN DE SECCIONES CLAVE")
    print(f"{'='*80}")

    secciones = {
        "Anticuerpos:": r'Anticuerpos?:',
        "REPORTE DE BIOMARCADORES:": r'REPORTE\s+DE\s+BIOMARCADORES?:',
        "DESCRIPCIÓN MICROSCÓPICA:": r'DESCRIPCI[ÓO]N\s+MICROSC[ÓO]PICA:',
        "-RECEPTOR DE ESTROGENOS:": r'-\s*RECEPTOR\s+DE\s+ESTROGENOS?:',
        "-RECEPTOR DE PROGESTERONA:": r'-\s*RECEPTOR\s+DE\s+PROG[RE]?STERONA:',
        "-HER 2:": r'-\s*HER\s*-?\s*2:',
        "-Ki-67:": r'-\s*Ki\s*-?\s*67:',
        "GATA 3": r'GATA\s*3',
        "SXO10 o SOX10": r'S[XO]{2,3}\s*10',
    }

    resultados = {}

    for nombre, patron in secciones.items():
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            pos = match.start()
            # Calcular línea aproximada (asumiendo 80 chars por línea)
            linea_aprox = pos // 80 + 1
            print(f"✅ {nombre:35} → Posición {pos:6} (línea ~{linea_aprox})")
            resultados[nombre] = (pos, match.group(0))
        else:
            print(f"❌ {nombre:35} → NO ENCONTRADO")
            resultados[nombre] = None

    return resultados


def extraer_seccion_reporte_manual(texto):
    """Extrae manualmente la sección REPORTE DE BIOMARCADORES"""
    print(f"\n{'='*80}")
    print("EXTRACCIÓN MANUAL: REPORTE DE BIOMARCADORES")
    print(f"{'='*80}")

    # Patrón usado en v6.0.12
    patron = r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO|$)'

    match = re.search(patron, texto, re.IGNORECASE | re.DOTALL)

    if match:
        seccion = match.group(1)
        print(f"✅ SECCIÓN EXTRAÍDA")
        print(f"   Posición inicio: {match.start()}")
        print(f"   Posición fin: {match.end()}")
        print(f"   Longitud: {len(seccion)} caracteres")
        print(f"\nCONTENIDO:")
        print(f"---")
        print(seccion[:1000])
        if len(seccion) > 1000:
            print(f"... (+ {len(seccion) - 1000} caracteres más)")
        print(f"---")
        return seccion
    else:
        print(f"❌ NO SE PUDO EXTRAER LA SECCIÓN")
        return None


def buscar_biomarcadores_en_seccion(seccion, nombre_seccion):
    """Busca biomarcadores específicos en una sección"""
    print(f"\n{'='*80}")
    print(f"BÚSQUEDA DE BIOMARCADORES EN: {nombre_seccion}")
    print(f"{'='*80}")

    if not seccion:
        print("❌ Sección vacía, no se puede buscar")
        return {}

    patrones = {
        "ER (formato -RECEPTOR:)": r'-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
        "ER (narrativo)": r'receptor\s+de\s+estr[óo]genos?:\s*(negativo|positivo)',
        "PR (formato -RECEPTOR:)": r'-\s*RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
        "HER2 (formato -HER:)": r'-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO)',
        "Ki-67 (formato -Ki:)": r'-\s*Ki\s*-?\s*67\s*:\s*(.+?)(?=\n-|\n\n|$)',
        "GATA3 (tinción)": r'tinción\s+nuclear\s+positiva\s+.*?para\s+GATA\s*3',
        "SOX10 (negativas)": r'negativas?\s+para\s+S[OX]{1,2}[OX]?\s*10',
    }

    resultados = {}

    for nombre, patron in patrones.items():
        matches = buscar_en_texto(seccion, patron, nombre)
        resultados[nombre] = matches

    return resultados


# ═══════════════════════════════════════════════════════════════════════
# FLUJO PRINCIPAL DE DEBUG
# ═══════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'#'*80}")
    print(f"# DEBUG PROFUNDO - Extracción IHQ250984")
    print(f"# Versión: v6.0.12")
    print(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 1: Extraer texto del PDF
    # ═══════════════════════════════════════════════════════════════════════

    print(f"📄 Extrayendo texto de: {PDF_PATH}")

    if not os.path.exists(PDF_PATH):
        print(f"❌ ERROR: PDF no encontrado en {PDF_PATH}")
        return

    texto_completo = extract_text_from_pdf(PDF_PATH)
    debug_step("1. TEXTO COMPLETO DEL PDF", texto_completo, max_chars=1000)

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 2: Verificar secciones clave
    # ═══════════════════════════════════════════════════════════════════════

    secciones_encontradas = verificar_secciones_clave(texto_completo)

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 3: Extraer sección "REPORTE DE BIOMARCADORES" manualmente
    # ═══════════════════════════════════════════════════════════════════════

    seccion_reporte = extraer_seccion_reporte_manual(texto_completo)

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 4: Buscar biomarcadores en la sección
    # ═══════════════════════════════════════════════════════════════════════

    if seccion_reporte:
        buscar_biomarcadores_en_seccion(seccion_reporte, "REPORTE DE BIOMARCADORES")

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 5: Ejecutar extractor REAL y comparar
    # ═══════════════════════════════════════════════════════════════════════

    print(f"\n{'='*80}")
    print("PASO 5: EJECUTAR EXTRACTOR REAL (extract_biomarkers)")
    print(f"{'='*80}")

    try:
        resultados_extractor = extract_biomarkers(texto_completo)
        debug_step("5. RESULTADOS DEL EXTRACTOR", resultados_extractor)
    except Exception as e:
        print(f"❌ ERROR al ejecutar extractor: {e}")
        import traceback
        traceback.print_exc()

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 6: Comparar resultados esperados vs reales
    # ═══════════════════════════════════════════════════════════════════════

    print(f"\n{'='*80}")
    print("PASO 6: COMPARACIÓN ESPERADO vs REAL")
    print(f"{'='*80}")

    esperados = {
        "ER": "NEGATIVO",
        "PR": "NEGATIVO",
        "HER2": "POSITIVO (SCORE 3+)",
        "KI67": "60%",
        "GATA3": "POSITIVO",
        "SOX10": "NEGATIVO"
    }

    print(f"\n{'Biomarcador':<15} {'Esperado':<25} {'Real':<40} {'Estado':<10}")
    print(f"{'-'*95}")

    for bio, esperado in esperados.items():
        real = resultados_extractor.get(bio, "N/A (no encontrado)")
        if isinstance(real, str) and len(real) > 35:
            real = real[:35] + "..."

        if esperado.upper() in str(real).upper():
            estado = "✅ OK"
        else:
            estado = "❌ ERROR"

        print(f"{bio:<15} {esperado:<25} {str(real):<40} {estado:<10}")

    # ═══════════════════════════════════════════════════════════════════════
    # PASO 7: Generar reporte MD
    # ═══════════════════════════════════════════════════════════════════════

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(OUTPUT_DIR, f"DEBUG_IHQ250984_{timestamp}.md")

    print(f"\n{'='*80}")
    print(f"📝 Generando reporte en: {output_file}")
    print(f"{'='*80}")

    # Aquí se podría generar un reporte MD completo
    print(f"\n✅ Debug completado")
    print(f"\nPróximo paso: Revisar logs arriba para identificar el problema")


if __name__ == "__main__":
    main()
