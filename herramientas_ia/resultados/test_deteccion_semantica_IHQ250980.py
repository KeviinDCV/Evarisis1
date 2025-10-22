#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DE DETECCIÓN SEMÁNTICA INTELIGENTE - Caso IHQ250980

Prueba las 3 funciones nuevas de detección semántica:
1. _detectar_diagnostico_principal_inteligente()
2. _detectar_biomarcadores_ihq_inteligente()
3. _detectar_biomarcadores_solicitados_inteligente()

Autor: core-editor agent (EVARISIS)
Fecha: 2025-10-22
"""

import sys
import os
from pathlib import Path

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from herramientas_ia.auditor_sistema import AuditorSistema


def print_header(title):
    """Imprime header formateado"""
    print(f"\n{'='*80}")
    print(f"{title.center(80)}")
    print(f"{'='*80}\n")


def test_caso_ihq250980():
    """Prueba detección semántica con caso IHQ250980"""

    print_header("TEST DE DETECCIÓN SEMÁNTICA INTELIGENTE")
    print("Caso: IHQ250980 (Tumor Neuroendocrino)")
    print("Funciones probadas: 3")

    # Inicializar auditor
    auditor = AuditorSistema()

    # Obtener debug_map y texto OCR
    print("\n[1/4] Cargando caso IHQ250980...")
    debug_map = auditor._obtener_debug_map('IHQ250980')

    if not debug_map:
        print("❌ ERROR: No se encontró debug_map para IHQ250980")
        return

    texto_ocr = debug_map.get('ocr', {}).get('texto_consolidado', '')

    if not texto_ocr:
        print("❌ ERROR: No se encontró texto OCR")
        return

    print(f"✅ Caso cargado - OCR: {len(texto_ocr):,} caracteres")

    # ============================================================================
    # TEST 1: Detección de DIAGNOSTICO_PRINCIPAL
    # ============================================================================
    print_header("TEST 1: Detección de DIAGNOSTICO_PRINCIPAL")

    resultado_diag = auditor._detectar_diagnostico_principal_inteligente(texto_ocr)

    print("RESULTADO:")
    if resultado_diag['diagnostico_encontrado']:
        print(f"✅ Diagnóstico detectado:")
        print(f"   Texto: {resultado_diag['diagnostico_encontrado']}")
        print(f"   Ubicación: {resultado_diag['ubicacion']}")
        print(f"   Línea: {resultado_diag['linea_numero']}")
        print(f"   Confianza: {resultado_diag['confianza']:.2f} / 1.00")

        # Análisis
        print(f"\n📊 ANÁLISIS:")
        if resultado_diag['confianza'] >= 0.8:
            print(f"   🟢 Confianza ALTA - Diagnóstico muy probable")
        elif resultado_diag['confianza'] >= 0.6:
            print(f"   🟡 Confianza MEDIA - Diagnóstico probable")
        else:
            print(f"   🔴 Confianza BAJA - Revisar manualmente")

        # Validación semántica
        keywords_correctos = ['TUMOR', 'NEUROENDOCRINO', 'BIEN DIFERENCIADO', 'GRADO']
        keywords_incorrectos = ['NOTTINGHAM', 'INVASIÓN', 'RECEPTOR', 'KI-67']

        tiene_correctos = [kw for kw in keywords_correctos if kw in resultado_diag['diagnostico_encontrado'].upper()]
        tiene_incorrectos = [kw for kw in keywords_incorrectos if kw in resultado_diag['diagnostico_encontrado'].upper()]

        print(f"   Keywords esperados: {len(tiene_correctos)}/{len(keywords_correctos)} ✓")
        print(f"   Keywords prohibidos: {len(tiene_incorrectos)} ❌")

    else:
        print("❌ No se detectó diagnóstico principal")

    # ============================================================================
    # TEST 2: Detección de Biomarcadores IHQ
    # ============================================================================
    print_header("TEST 2: Detección de Biomarcadores IHQ")

    resultado_bio = auditor._detectar_biomarcadores_ihq_inteligente(texto_ocr)

    print("RESULTADO:")
    if resultado_bio['biomarcadores_encontrados']:
        print(f"✅ {len(resultado_bio['biomarcadores_encontrados'])} biomarcador(es) detectado(s):\n")

        for i, bio in enumerate(resultado_bio['biomarcadores_encontrados'], 1):
            print(f"   [{i}] {bio['nombre']}")
            print(f"       Valor: {bio['valor']}")
            print(f"       Ubicación: {bio['ubicacion']}")
            print()

        print(f"📊 ANÁLISIS:")
        print(f"   Confianza global: {resultado_bio['confianza_global']:.2f} / 1.00")

        # Secciones utilizadas
        secciones_usadas = set(resultado_bio['ubicaciones'].values())
        print(f"   Secciones consultadas: {', '.join(secciones_usadas)}")

        # Distribución por sección
        print(f"\n   Distribución por sección:")
        for seccion in secciones_usadas:
            count = list(resultado_bio['ubicaciones'].values()).count(seccion)
            print(f"     - {seccion}: {count} biomarcador(es)")

    else:
        print("❌ No se detectaron biomarcadores IHQ")

    # ============================================================================
    # TEST 3: Detección de Biomarcadores SOLICITADOS
    # ============================================================================
    print_header("TEST 3: Detección de Biomarcadores SOLICITADOS")

    resultado_sol = auditor._detectar_biomarcadores_solicitados_inteligente(texto_ocr)

    print("RESULTADO:")
    if resultado_sol['biomarcadores_solicitados']:
        print(f"✅ {len(resultado_sol['biomarcadores_solicitados'])} biomarcador(es) solicitado(s):\n")

        for i, bio in enumerate(resultado_sol['biomarcadores_solicitados'], 1):
            print(f"   [{i}] {bio}")

        print(f"\n📊 ANÁLISIS:")
        print(f"   Formato detectado: '{resultado_sol['formato']}'")
        print(f"   Ubicación: {resultado_sol['ubicacion']}")

        # Comparación con biomarcadores encontrados
        if resultado_bio['biomarcadores_encontrados']:
            solicitados = set(resultado_sol['biomarcadores_solicitados'])
            encontrados = set([b['nombre'] for b in resultado_bio['biomarcadores_encontrados']])

            print(f"\n   Comparación SOLICITADOS vs ENCONTRADOS:")
            print(f"     Solicitados: {len(solicitados)}")
            print(f"     Encontrados: {len(encontrados)}")

            # Cobertura (aproximada, nombres pueden no coincidir exactamente)
            cobertura_aprox = (len(encontrados) / len(solicitados) * 100) if solicitados else 0
            print(f"     Cobertura aproximada: {cobertura_aprox:.1f}%")

    else:
        print("❌ No se detectaron biomarcadores solicitados")

    # ============================================================================
    # RESUMEN FINAL
    # ============================================================================
    print_header("RESUMEN FINAL")

    print("ESTADÍSTICAS DE DETECCIÓN:\n")

    # Diagnóstico principal
    diag_status = "✅" if resultado_diag['diagnostico_encontrado'] else "❌"
    diag_conf = resultado_diag['confianza'] if resultado_diag['diagnostico_encontrado'] else 0.0
    print(f"  {diag_status} Diagnóstico Principal: {'DETECTADO' if resultado_diag['diagnostico_encontrado'] else 'NO DETECTADO'}")
    print(f"     Confianza: {diag_conf:.2f}")

    # Biomarcadores IHQ
    bio_count = len(resultado_bio['biomarcadores_encontrados'])
    bio_status = "✅" if bio_count > 0 else "❌"
    print(f"\n  {bio_status} Biomarcadores IHQ: {bio_count} detectados")
    print(f"     Confianza: {resultado_bio['confianza_global']:.2f}")

    # Biomarcadores solicitados
    sol_count = len(resultado_sol['biomarcadores_solicitados'])
    sol_status = "✅" if sol_count > 0 else "❌"
    print(f"\n  {sol_status} Biomarcadores Solicitados: {sol_count} detectados")
    print(f"     Formato: {resultado_sol['formato'] if resultado_sol['formato'] else 'N/A'}")

    # Score global
    print(f"\n📊 SCORE GLOBAL:")
    tests_pasados = sum([
        1 if resultado_diag['diagnostico_encontrado'] else 0,
        1 if bio_count > 0 else 0,
        1 if sol_count > 0 else 0
    ])
    score_global = (tests_pasados / 3 * 100)
    print(f"   Tests pasados: {tests_pasados}/3")
    print(f"   Score: {score_global:.1f}%")

    if score_global == 100:
        print(f"\n   🏆 EXCELENTE - Todas las funciones operan correctamente")
    elif score_global >= 66:
        print(f"\n   ✅ BUENO - Mayoría de funciones operan correctamente")
    elif score_global >= 33:
        print(f"\n   ⚠️  REGULAR - Algunas funciones necesitan revisión")
    else:
        print(f"\n   ❌ CRÍTICO - Sistema de detección necesita revisión urgente")

    # Comparación con BD
    print(f"\n{'='*80}")
    print("COMPARACIÓN CON BASE DE DATOS:")
    print(f"{'='*80}\n")

    datos_bd = debug_map.get('base_datos', {}).get('datos_guardados', {})

    # Diagnóstico BD
    diag_bd = datos_bd.get('Diagnostico Principal', 'N/A')
    print(f"DIAGNOSTICO_PRINCIPAL:")
    print(f"  BD:       {diag_bd}")
    print(f"  Detectado: {resultado_diag['diagnostico_encontrado'] if resultado_diag['diagnostico_encontrado'] else 'N/A'}")
    match_diag = (diag_bd.upper() == resultado_diag['diagnostico_encontrado'].upper()) if resultado_diag['diagnostico_encontrado'] else False
    print(f"  Match:    {'✅ SÍ' if match_diag else '❌ NO'}")

    # Biomarcadores BD (muestra)
    print(f"\nBIOMARCADORES (muestra):")
    biomarcadores_muestra = ['IHQ_KI-67', 'IHQ_CD56', 'IHQ_SYNAPTOPHYSIN', 'IHQ_CHROMOGRANINA']
    for col in biomarcadores_muestra:
        valor_bd = datos_bd.get(col, 'N/A')
        print(f"  {col}: {valor_bd}")

    print(f"\n{'='*80}")
    print("TEST COMPLETADO")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    try:
        test_caso_ihq250980()
    except Exception as e:
        print(f"\n❌ ERROR DURANTE TEST: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
