#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulación de correcciones para OCR_PROCESSOR.PY
Caso: IHQ251029 - Descripción macroscópica cortada

Objetivo: Probar diferentes soluciones ANTES de modificar código de producción
"""

import re
from typing import List, Tuple

# ═══════════════════════════════════════════════════════════════════════════
# TEXTO DE PRUEBA - Simulando el OCR actual (PROBLEMÁTICO)
# ═══════════════════════════════════════════════════════════════════════════

TEXTO_OCR_PROBLEMATICO = """IHQ251029
Final Pag. 1 de 2
Nombre : ROSA MARIA HERRERA VASQUEZ
N. peticion : IHQ251029

INFORME DE ANATOMÍA PATOLÓGICA
ESTUDIO DE INMUNOHISTOQUIMICA
DESCRIPCIÓN MACROSCÓPICA
Se recibe orden para realizar estudios de inmunohistoquímica en material institucional, rotulado
"M2510813"
y
DESCRIPCIÓN MICROSCÓPICA
Se realizan estudios de inmunohistoquímica con el método inmunoperoxidasa en el sistema
ROCHE VENTANA®. Se verifica el rendimiento de los controles externos e internos y se observa:
Proliferación de celulas poligonales, con citoplasma moderado, anfofílico, con núcleo redondo y
cromatina punteada en patrón "sal y pimienta" que se disponen en patrón organoide, con
actividad mitótica de y expresan inmunofenotipo con marcación fuerte y difusa para
Sinaptofisina+/Cromogranina A+ en patrón punteado apical y perinucleal, y CKAE1-AE3+
citoplasmático, con positividad débil para CD56.
El índice de proliferación celular estimado por Ki-67 es del 2%.
diagnóstico
"LOS
HALLAZGOS
MORFOLOGICOS
FAVORECEN
UN
TUMOR
NEUROENDOCRINO".
Previa
revisión
de
la
histología
se
solicitan
coloraciones
inmunohistoquímica
con
CD56,
Cromogranina-A, Sinaptofisina, CKAE1/AE3 y Ki-67.
DIAGNÓSTICO
Mesenterio. Tumor. Biopsia. Estudio de inmunohistoquímica.
TUMOR NEUROENDOCRINO BIEN DIFERENCIADO, GRADO 1 (1/3 WHO).
"""

# TEXTO ESPERADO (CORRECTO)
TEXTO_MACRO_ESPERADO = 'Se recibe orden para realizar estudios de inmunohistoquímica en material institucional, rotulado "M2510813" y diagnóstico "LOS HALLAZGOS MORFOLOGICOS FAVORECEN UN TUMOR NEUROENDOCRINO". Previa revisión de la histología se solicitan coloraciones inmunohistoquímica con CD56, Cromogranina-A, Sinaptofisina, CKAE1/AE3 y Ki-67.'

# ═══════════════════════════════════════════════════════════════════════════
# SOLUCIÓN 1: Consolidar líneas antes de segmentar secciones
# ═══════════════════════════════════════════════════════════════════════════

def solucion_1_merge_continuations(text: str) -> str:
    """
    ESTRATEGIA: Detectar cuando una línea termina incompleta y fusionarla con la siguiente

    Criterios de continuación:
    - Línea termina en: y, de, el, la, con, para, en (palabras conectoras)
    - Siguiente línea NO es un título de sección (MAYÚSCULAS)
    """
    lines = text.split('\n')
    merged_lines = []
    i = 0

    # Palabras que indican continuación
    continuation_words = {'y', 'de', 'del', 'el', 'la', 'con', 'para', 'en', 'a', 'por', 'se'}

    while i < len(lines):
        current = lines[i].strip()

        # Si la línea actual está vacía, mantenerla
        if not current:
            merged_lines.append(current)
            i += 1
            continue

        # Verificar si la línea termina en palabra conectora
        last_word = current.split()[-1].lower() if current.split() else ""

        # Verificar si la siguiente línea existe y NO es un título de sección
        if (i + 1 < len(lines) and
            last_word in continuation_words and
            lines[i + 1].strip() and
            not re.match(r'^[A-ZÁÉÍÓÚÑ\s]{5,}$', lines[i + 1].strip())):  # NO es título en mayúsculas

            # Fusionar con la siguiente línea
            next_line = lines[i + 1].strip()
            merged_lines.append(current + " " + next_line)
            i += 2  # Saltar la línea fusionada
        else:
            merged_lines.append(current)
            i += 1

    return '\n'.join(merged_lines)


# ═══════════════════════════════════════════════════════════════════════════
# SOLUCIÓN 2: Reordenar texto mal segmentado (ESPECÍFICO para este caso)
# ═══════════════════════════════════════════════════════════════════════════

def solucion_2_reorder_misplaced_text(text: str) -> str:
    """
    ESTRATEGIA: Detectar texto mal ubicado y moverlo a la sección correcta

    Patrón detectado en IHQ251029:
    1. DESCRIPCIÓN MACROSCÓPICA termina en "y"
    2. DESCRIPCIÓN MICROSCÓPICA aparece prematuramente
    3. Dentro de microscópica hay texto que debería estar en macroscópica
    """

    # Buscar sección macroscópica
    macro_match = re.search(
        r'DESCRIPCI[OÓ]N\s+MACROSC[OÓ]PICA\s*\n(.*?)(?=DESCRIPCI[OÓ]N\s+MICROSC[OÓ]PICA)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    # Buscar sección microscópica
    # CRÍTICO: Debe capturar hasta la sección "DIAGNÓSTICO" (al inicio de línea, en MAYÚSCULAS)
    # NO debe detenerse en "diagnóstico" (palabra dentro del texto, puede estar en minúsculas)
    # SOLUCIÓN: Usar re.search sin IGNORECASE solo para esta parte
    # Primero encontrar DESCRIPCIÓN MICROSCÓPICA (case insensitive)
    micro_start = re.search(r'DESCRIPCI[OÓ]N\s+MICROSC[OÓ]PICA', text, re.IGNORECASE)
    # Luego buscar DIAGNÓSTICO en MAYÚSCULAS (case sensitive) como sección
    micro_end = re.search(r'\nDIAGN[ÓO]STICO\s*\n', text[micro_start.end():] if micro_start else text)

    if micro_start and micro_end:
        micro_text_extracted = text[micro_start.end():micro_start.end() + micro_end.start()]
        micro_match_manual = True
    else:
        micro_match_manual = False
        micro_text_extracted = ""

    # Fallback al patrón original si no funciona
    if not micro_match_manual:
        micro_match = re.search(
            r'DESCRIPCI[OÓ]N\s+MICROSC[OÓ]PICA\s*\n(.*?)(?=DIAGN[OÓ]STICO|$)',
            text,
            re.IGNORECASE | re.DOTALL
        )
        if micro_match:
            micro_text_extracted = micro_match.group(1)
        else:
            micro_text_extracted = ""

    if not macro_match or not micro_text_extracted:
        print(f"[DEBUG SOL2] No match - macro:{bool(macro_match)} micro:{bool(micro_text_extracted)}")
        return text

    macro_text = macro_match.group(1)
    micro_text = micro_text_extracted

    print(f"[DEBUG SOL2] macro_text termina en: '{macro_text.strip()[-50:]}'")
    print(f"[DEBUG SOL2] micro_text empieza con: '{micro_text.strip()[:100]}'")
    print(f"[DEBUG SOL2] micro_text total length: {len(micro_text)} chars")
    # Mostrar si contiene "diagnostico" usando búsqueda simple de string
    if 'diagn' in micro_text.lower():
        idx = micro_text.lower().find('diagn')
        print(f"[DEBUG SOL2] 'diagn' found at position {idx}: '{micro_text[idx:idx+20]}'")

    # Detectar si macroscópica termina incompleta (en "y" o palabra conectora)
    macro_lines = macro_text.strip().split('\n')
    last_line_macro = macro_lines[-1].strip() if macro_lines else ""

    print(f"[DEBUG SOL2] Ultima linea de macro: '{last_line_macro}'")

    continuation_pattern = r'\b(y|de|del|con|para|en|a|por|se)\s*$'
    continuation_detected = re.search(continuation_pattern, last_line_macro, re.IGNORECASE)

    print(f"[DEBUG SOL2] Continuacion detectada? {bool(continuation_detected)}")

    if continuation_detected:
        # Macroscópica está incompleta, buscar continuación en microscópica
        print(f"[DEBUG SOL2] Macroscopica termina incompleta. Buscando continuacion...")

        # Buscar patrón: "diagnóstico" INCLUSO si está después de mucho texto
        # El patrón real en IHQ251029: hay descripción microscópica válida ANTES del diagnóstico citado
        # IMPORTANTE: Puede haber saltos de línea entre "diagnóstico" y las comillas
        # CRUCIAL: Probar con y sin acento (encoding issues)
        continuation_match = re.search(
            r'diagn.?stico',  # El . matchea cualquier carácter (incluso mal codificado)
            micro_text,
            re.IGNORECASE
        )
        print(f"[DEBUG SOL2] Encontro 'diagnostico' en micro? {bool(continuation_match)}")
        if continuation_match:
            print(f"[DEBUG SOL2] Posicion: {continuation_match.start()}, Texto: '{continuation_match.group(0)}'")

        if continuation_match:
            # Texto del diagnóstico citado encontrado
            # Buscar el patrón extendido que incluye "Previa revisión...se solicitan..."
            # IMPORTANTE: El texto tiene saltos de línea entre palabras, usar \s+ para matchear cualquier whitespace
            extended_match = re.search(
                r'(diagn[óo]stico\s+["\'].*?["\'].*?\.\s*Previa\s+.*?(?:se\s+solicitan?|coloraciones?)\s+.*?Ki-67\.)',
                micro_text,
                re.IGNORECASE | re.DOTALL
            )

            if extended_match:
                texto_movido = extended_match.group(1).strip()
                print(f"[DEBUG SOL2] Texto a mover ({len(texto_movido)} chars): '{texto_movido[:100]}...'")

                # Eliminar el texto movido de microscópica
                micro_text_limpio = micro_text.replace(texto_movido, '', 1).strip()

                # Reconstruir macroscópica con el texto completo
                macro_text_corregido = macro_text.strip() + " " + texto_movido

                # Limpiar saltos de línea excesivos en el texto corregido
                macro_text_corregido = re.sub(r'\n+', '\n', macro_text_corregido)

                # Reemplazar en el texto original
                search_pattern = f'DESCRIPCIÓN MACROSCÓPICA\n{macro_text}DESCRIPCIÓN MICROSCÓPICA\n{micro_text}'
                replace_with = f'DESCRIPCIÓN MACROSCÓPICA\n{macro_text_corregido}\nDESCRIPCIÓN MICROSCÓPICA\n{micro_text_limpio}'

                print(f"[DEBUG SOL2] Buscando patron de {len(search_pattern)} chars para reemplazar...")

                if search_pattern in text:
                    texto_corregido = text.replace(search_pattern, replace_with, 1)
                    print(f"[DEBUG SOL2] Reemplazo exitoso!")
                else:
                    print(f"[DEBUG SOL2] ADVERTENCIA: Patron no encontrado en texto. Reemplazo fallido.")
                    # Intentar reconstruir manualmente
                    texto_corregido = text

                print(f"[DEBUG SOL2] Texto corregido. Nueva macro tiene {len(macro_text_corregido)} chars")
                return texto_corregido
            else:
                print(f"[DEBUG SOL2] No se encontro patron extendido")

    return text


# ═══════════════════════════════════════════════════════════════════════════
# SOLUCIÓN 3: Hybrid - Combinar ambas estrategias
# ═══════════════════════════════════════════════════════════════════════════

def solucion_3_hybrid(text: str) -> str:
    """
    ESTRATEGIA: Aplicar solución 1 primero, luego solución 2
    """
    # Paso 1: Fusionar continuaciones obvias
    text_merged = solucion_1_merge_continuations(text)

    # Paso 2: Reordenar texto mal segmentado
    text_reordered = solucion_2_reorder_misplaced_text(text_merged)

    return text_reordered


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE PRUEBA Y VALIDACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def extraer_descripcion_macroscopica(text: str) -> str:
    """Simula la extracción que hace medical_extractor.py"""
    # Patrón actual de medical_extractor.py
    pattern = r'(Se\s+recibe\s+orden\s+para\s+(?:realizar|realización\s+de)\s+(?:estudios?\s+de\s+)?inmunohistoqu[ií]mica.+?)(?=\s*DESCRIPCI\w+N\s+MICROSC\w+PICA|fin\s+del\s+informe|$)'

    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        # Limpiar saltos de línea múltiples
        texto = match.group(1).strip()
        texto = re.sub(r'\s+', ' ', texto)
        return texto
    return ""


def validar_solucion(nombre: str, texto_procesado: str) -> Tuple[bool, str, str]:
    """Valida si una solución corrige el problema"""
    resultado = extraer_descripcion_macroscopica(texto_procesado)

    # Normalizar espacios para comparación
    resultado_norm = re.sub(r'\s+', ' ', resultado).strip()
    esperado_norm = re.sub(r'\s+', ' ', TEXTO_MACRO_ESPERADO).strip()

    # Verificar si contiene los elementos clave
    tiene_m2510813 = '"M2510813"' in resultado
    tiene_diagnostico = 'diagnóstico' in resultado.lower() and 'LOS HALLAZGOS' in resultado
    tiene_biomarcadores = 'CD56' in resultado and 'Cromogranina-A' in resultado

    exitoso = tiene_m2510813 and tiene_diagnostico and tiene_biomarcadores

    return exitoso, resultado_norm, esperado_norm


def ejecutar_pruebas():
    """Ejecuta todas las soluciones y reporta resultados"""

    print("=" * 80)
    print("SIMULACIÓN DE CORRECCIONES - OCR_PROCESSOR.PY")
    print("Caso: IHQ251029 - Descripción Macroscópica Cortada")
    print("=" * 80)
    print()

    # CONTROL: Sin modificaciones
    print("-" * 80)
    print("CONTROL (SIN MODIFICACIONES)")
    print("-" * 80)
    exitoso, resultado, esperado = validar_solucion("CONTROL", TEXTO_OCR_PROBLEMATICO)
    print(f"Estado: {'[OK] EXITOSO' if exitoso else '[FAIL] FALLIDO'}")
    print(f"\nResultado obtenido ({len(resultado)} chars):")
    print(f"  {resultado[:200]}...")
    print(f"\nEsperado ({len(esperado)} chars):")
    print(f"  {esperado[:200]}...")
    print()

    # SOLUCIÓN 1
    print("-" * 80)
    print("SOLUCION 1: Merge Continuations")
    print("-" * 80)
    texto_sol1 = solucion_1_merge_continuations(TEXTO_OCR_PROBLEMATICO)
    exitoso1, resultado1, _ = validar_solucion("SOL1", texto_sol1)
    print(f"Estado: {'[OK] EXITOSO' if exitoso1 else '[FAIL] FALLIDO'}")
    print(f"\nResultado obtenido ({len(resultado1)} chars):")
    print(f"  {resultado1[:200]}...")
    print()

    # SOLUCIÓN 2
    print("-" * 80)
    print("SOLUCION 2: Reorder Misplaced Text")
    print("-" * 80)
    texto_sol2 = solucion_2_reorder_misplaced_text(TEXTO_OCR_PROBLEMATICO)
    exitoso2, resultado2, _ = validar_solucion("SOL2", texto_sol2)
    print(f"Estado: {'[OK] EXITOSO' if exitoso2 else '[FAIL] FALLIDO'}")
    print(f"\nResultado obtenido ({len(resultado2)} chars):")
    print(f"  {resultado2[:200]}...")
    print()

    # SOLUCIÓN 3
    print("-" * 80)
    print("SOLUCION 3: Hybrid (Merge + Reorder)")
    print("-" * 80)
    texto_sol3 = solucion_3_hybrid(TEXTO_OCR_PROBLEMATICO)
    exitoso3, resultado3, _ = validar_solucion("SOL3", texto_sol3)
    print(f"Estado: {'[OK] EXITOSO' if exitoso3 else '[FAIL] FALLIDO'}")
    print(f"\nResultado obtenido ({len(resultado3)} chars):")
    print(f"  {resultado3[:200]}...")
    print()

    # RESUMEN
    print("=" * 80)
    print("RESUMEN DE RESULTADOS")
    print("=" * 80)
    print(f"CONTROL:     {'[OK] EXITOSO' if exitoso else '[FAIL] FALLIDO'}")
    print(f"SOLUCION 1:  {'[OK] EXITOSO' if exitoso1 else '[FAIL] FALLIDO'} (Merge Continuations)")
    print(f"SOLUCION 2:  {'[OK] EXITOSO' if exitoso2 else '[FAIL] FALLIDO'} (Reorder Misplaced)")
    print(f"SOLUCION 3:  {'[OK] EXITOSO' if exitoso3 else '[FAIL] FALLIDO'} (Hybrid)")
    print()

    # RECOMENDACIÓN
    if exitoso3:
        print("[>>] RECOMENDACION: Implementar SOLUCION 3 (Hybrid) en ocr_processor.py")
    elif exitoso2:
        print("[>>] RECOMENDACION: Implementar SOLUCION 2 (Reorder) en ocr_processor.py")
    elif exitoso1:
        print("[>>] RECOMENDACION: Implementar SOLUCION 1 (Merge) en ocr_processor.py")
    else:
        print("[!!] ADVERTENCIA: Ninguna solucion resolvio el problema. Requiere analisis adicional.")
    print()


if __name__ == '__main__':
    ejecutar_pruebas()
