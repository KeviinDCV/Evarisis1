#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SIMULACIÓN: Corrección para IHQ251030 - Descripción Macroscópica Cortada
================================================================================

PROBLEMA DETECTADO:
- Descripción macroscópica termina en: ". y con"
- Falta texto que está en descripción microscópica:
  "diagnóstico de "ADENOCARCINOMA..." Previa revisión...Her2."

PATRÓN SIMILAR A IHQ251029:
- IHQ251029: termina en "y" → FIXED exitosamente
- IHQ251030: termina en "y con" → necesita mismo fix pero con patrón extendido

ESTRATEGIA:
1. Detectar cuando macroscópica termina en palabra conectora o combinación de ellas
2. Buscar texto mal ubicado en microscópica que mencione "diagnóstico previo"
3. Mover ese texto de microscópica a macroscópica
4. Normalizar espacios
"""

import re
import json

# ============================================================================
# DATOS DE PRUEBA - IHQ251030
# ============================================================================

MACRO_ACTUAL = 'Se recibe orden para realización de inmunohistoquímica en material extrainstitucional rotulado como "M2501720 bloque A7" que corresponde a "Tumor de estomago. Gastrectomía total.". y con'

MICRO_ACTUAL = 'Previa valoración de la técnica y verificación de la adecuada tinción de los controles externos e internos se realizan estudios de inmunohistoquímica en la plataforma automatizada Roche VENTANA®. Pruebas realizadas en la muestra / número: M2501720 A7. HER2 : NEGATIVO (Score 0) diagnóstico de "ADENOCARCINOMA INTESTINAL INVASIVO MODERADAMENTE DIFERENCIADO". Previa revisión de la histología se realizan niveles histológicos para tinción con: Her2.'

# Esperado: la parte que debería estar en macro
TEXTO_ESPERADO_EN_MACRO = 'diagnóstico de "ADENOCARCINOMA INTESTINAL INVASIVO MODERADAMENTE DIFERENCIADO". Previa revisión de la histología se realizan niveles histológicos para tinción con: Her2.'

MACRO_ESPERADA_FINAL = MACRO_ACTUAL + ' ' + TEXTO_ESPERADO_EN_MACRO

# ============================================================================
# SOLUCIÓN PROPUESTA
# ============================================================================

def fix_macro_micro_separation(macro_text: str, micro_text: str, debug=False):
    """
    Corrige separación incorrecta entre descripción macro y micro

    V6.2.14: Detecta cuando macroscópica termina incompleta y recupera texto de microscópica

    Casos cubiertos:
    - IHQ251029: termina en "y"
    - IHQ251030: termina en "y con"
    - Futuros: cualquier combinación de conectores

    Args:
        macro_text: Descripción macroscópica (puede estar incompleta)
        micro_text: Descripción microscópica (puede contener texto de macro)
        debug: Si True, imprime información de depuración

    Returns:
        tuple: (macro_corregida, micro_corregida)
    """

    if not macro_text or not micro_text:
        return macro_text, micro_text

    # PASO 1: Detectar si macroscópica termina incompleta
    # Buscar una o dos palabras conectoras al final (ej: "y", "y con", "y de", etc.)
    continuation_pattern = r'\b(?:y\s+)?(?:y|de|del|con|para|en|a|por|se)\s*$'
    continuation_match = re.search(continuation_pattern, macro_text, re.IGNORECASE)

    if debug:
        print(f"[DEBUG] Macro termina en: '{macro_text[-50:]}'")
        print(f"[DEBUG] ¿Continuación detectada?: {bool(continuation_match)}")
        if continuation_match:
            print(f"[DEBUG] Patrón encontrado: '{continuation_match.group()}'")

    if not continuation_match:
        # No hay continuación, las descripciones están correctas
        return macro_text, micro_text

    # PASO 2: Buscar texto mal ubicado en microscópica
    # Patrón: "diagnóstico [de] "..." ...Previa revisión...se realizan/solicitan...biomarcadores"
    misplaced_pattern = r'(diagn[óo]stico\s+(?:de\s+)?["\'].*?["\'].*?\.\s*Previa\s+.*?(?:se\s+(?:solicitan?|realizan?)|coloraciones?)\s+.*?\.)'

    misplaced_match = re.search(misplaced_pattern, micro_text, re.IGNORECASE | re.DOTALL)

    if debug:
        print(f"[DEBUG] ¿Texto mal ubicado encontrado?: {bool(misplaced_match)}")
        if misplaced_match:
            texto_encontrado = misplaced_match.group(1)
            print(f"[DEBUG] Texto encontrado ({len(texto_encontrado)} chars):")
            print(f"[DEBUG]   Inicio: '{texto_encontrado[:80]}...'")
            print(f"[DEBUG]   Fin: '...{texto_encontrado[-80:]}'")

    if not misplaced_match:
        # No se encontró el texto mal ubicado
        if debug:
            print("[DEBUG] ADVERTENCIA: Continuación detectada pero no se encontró texto mal ubicado")
        return macro_text, micro_text

    # PASO 3: Mover texto de micro a macro
    texto_recuperado = misplaced_match.group(1).strip()

    # Normalizar espacios en el texto recuperado
    texto_recuperado = re.sub(r'\s+', ' ', texto_recuperado)

    # Agregar a macroscópica (quitar conector incompleto y agregar texto completo)
    macro_corregida = macro_text + ' ' + texto_recuperado

    # Eliminar de microscópica
    micro_corregida = micro_text.replace(misplaced_match.group(1), '', 1).strip()

    # Limpiar espacios múltiples
    micro_corregida = re.sub(r'\s+', ' ', micro_corregida)

    if debug:
        print(f"\n[DEBUG] CORRECCIÓN APLICADA:")
        print(f"[DEBUG] Macro original: {len(macro_text)} chars")
        print(f"[DEBUG] Macro corregida: {len(macro_corregida)} chars (+{len(macro_corregida)-len(macro_text)})")
        print(f"[DEBUG] Micro original: {len(micro_text)} chars")
        print(f"[DEBUG] Micro corregida: {len(micro_corregida)} chars ({len(micro_corregida)-len(micro_text)})")

    return macro_corregida, micro_corregida


# ============================================================================
# PRUEBAS
# ============================================================================

def test_fix():
    """Ejecuta prueba de la corrección"""

    print("=" * 80)
    print("SIMULACIÓN: Corrección IHQ251030 - Descripción Macroscópica Cortada")
    print("=" * 80)
    print()

    # Mostrar datos de entrada
    print("DATOS DE ENTRADA:")
    print("-" * 80)
    print(f"Macro actual ({len(MACRO_ACTUAL)} chars):")
    print(f"  '{MACRO_ACTUAL}'")
    print()
    print(f"Micro actual ({len(MICRO_ACTUAL)} chars):")
    print(f"  '{MICRO_ACTUAL[:100]}...'")
    print()
    print(f"Texto esperado en macro ({len(TEXTO_ESPERADO_EN_MACRO)} chars):")
    print(f"  '{TEXTO_ESPERADO_EN_MACRO}'")
    print()

    # Ejecutar corrección
    print("=" * 80)
    print("EJECUTANDO CORRECCIÓN (con debug):")
    print("=" * 80)
    macro_corregida, micro_corregida = fix_macro_micro_separation(
        MACRO_ACTUAL,
        MICRO_ACTUAL,
        debug=True
    )

    # Validar resultados
    print()
    print("=" * 80)
    print("RESULTADOS:")
    print("=" * 80)
    print()
    print(f"Macro corregida ({len(macro_corregida)} chars):")
    print(f"  '{macro_corregida}'")
    print()
    print(f"Micro corregida ({len(micro_corregida)} chars):")
    print(f"  '{micro_corregida[:100]}...'")
    print()

    # Validación
    print("=" * 80)
    print("VALIDACIÓN:")
    print("=" * 80)

    success = True

    # Check 1: ¿La macro contiene el texto esperado?
    if TEXTO_ESPERADO_EN_MACRO in macro_corregida:
        print("[OK] Macro contiene el texto esperado")
    else:
        print("[FAIL] Macro NO contiene el texto esperado")
        success = False

    # Check 2: ¿La macro ya no termina en conector incompleto?
    if not re.search(r'\b(?:y\s+)?(?:y|de|del|con|para|en|a|por|se)\s*$', macro_corregida):
        print("[OK] Macro ya no termina en conector incompleto")
    else:
        print("[FAIL] Macro aun termina en conector")
        success = False

    # Check 3: ¿La micro ya no contiene el texto mal ubicado?
    if TEXTO_ESPERADO_EN_MACRO not in micro_corregida:
        print("[OK] Micro ya no contiene el texto mal ubicado")
    else:
        print("[FAIL] Micro todavia contiene el texto mal ubicado")
        success = False

    # Check 4: ¿La micro aún contiene su contenido propio?
    if 'Previa valoración de la técnica' in micro_corregida:
        print("[OK] Micro conserva su contenido original")
    else:
        print("[FAIL] Micro perdio contenido original")
        success = False

    print()
    if success:
        print("=" * 80)
        print("EXITO: Todas las validaciones pasaron")
        print("=" * 80)
        print()
        print("CODIGO LISTO PARA APLICAR A medical_extractor.py")
    else:
        print("=" * 80)
        print("FALLO: Algunas validaciones no pasaron")
        print("=" * 80)
        print()
        print("REVISAR LOGICA ANTES DE APLICAR")

    return success


if __name__ == '__main__':
    test_fix()
