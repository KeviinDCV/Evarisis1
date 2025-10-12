#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidad para corrección de caracteres UTF-8 mal codificados

Corrige artefactos comunes de OCR y problemas de encoding
que aparecen en documentos PDF procesados.

Versión: 4.0.0
Migrado de: core/procesador_ihq.py (función fix_broken_utf8)
"""

import unicodedata
from typing import Dict, Set
from core.utils.patient_mappings import BROKEN_UTF_MAP


def fix_broken_utf8(text: str) -> str:
    """Corrige caracteres UTF-8 mal codificados
    
    Args:
        text: Texto con posibles caracteres mal codificados
        
    Returns:
        Texto con caracteres corregidos
    """
    if not text:
        return ''
    
    # Aplicar mapeo de correcciones conocidas
    corrected_text = text
    for bad_char, good_char in BROKEN_UTF_MAP.items():
        corrected_text = corrected_text.replace(bad_char, good_char)
    
    return corrected_text


def normalize_unicode(text: str) -> str:
    """Normaliza texto unicode para consistencia
    
    Args:
        text: Texto a normalizar
        
    Returns:
        Texto normalizado
    """
    if not text:
        return ''
    
    # Normalizar usando NFD (Canonical Decomposition)
    # luego recomponer para consistencia
    normalized = unicodedata.normalize('NFC', text)
    return normalized


def remove_control_characters(text: str) -> str:
    """Elimina caracteres de control problemáticos
    
    Args:
        text: Texto con posibles caracteres de control
        
    Returns:
        Texto sin caracteres de control
    """
    if not text:
        return ''
    
    # Eliminar caracteres de control excepto espacios, tabs y newlines
    cleaned = ''.join(char for char in text 
                      if unicodedata.category(char)[0] != 'C' 
                      or char in '\t\n\r ')
    
    return cleaned


def fix_common_ocr_errors(text: str) -> str:
    """Corrige errores comunes de OCR
    
    Args:
        text: Texto con posibles errores de OCR
        
    Returns:
        Texto con errores corregidos
    """
    if not text:
        return ''
    
    # Mapeo de errores comunes de OCR
    ocr_corrections = {
        # Confusiones numéricas/letras comunes (COMENTADO - demasiado agresivo)
        # '0': 'O',  # En contextos de letras - PROBLEMA: arruina P40 → P4O
        # '1': 'I',  # En contextos de letras - PROBLEMA: arruina P16 → PI6
        'rn': 'm',  # OCR confunde 'rn' con 'm'
        'cl': 'd',  # En algunos contextos
        
        # Errores específicos encontrados en HUV
        'ADENOCACRINOMA': 'ADENOCARCINOMA',
        'HODKING': 'HODGKIN',
        'MIELOMA MULTIPLI': 'MIELOMA MULTIPLE',
        'NUEROENDOCRINO': 'NEUROENDOCRINO',
        'GLANGIOMA': 'GLIOMA',
        
        # Espacios incorrectos
        ' DE ': ' DE ',  # Normalizar espacios
        'INMUNOHISTOQUI MICA': 'INMUNOHISTOQUIMICA',
        'DESCRIPCI N': 'DESCRIPCION',
        'DIAGN STICO': 'DIAGNOSTICO',
    }
    
    corrected_text = text
    for error, correction in ocr_corrections.items():
        corrected_text = corrected_text.replace(error, correction)
    
    return corrected_text


def clean_text_comprehensive(text: str) -> str:
    """Limpieza comprehensiva de texto
    
    Aplica todas las correcciones disponibles en orden lógico:
    1. Corrige UTF-8 roto
    2. Normaliza unicode
    3. Elimina caracteres de control
    4. Corrige errores de OCR
    5. Normaliza espacios
    
    Args:
        text: Texto a limpiar
        
    Returns:
        Texto completamente limpio
    """
    if not text:
        return ''
    
    # Paso 1: Corregir UTF-8 roto
    cleaned = fix_broken_utf8(text)
    
    # Paso 2: Normalizar unicode
    cleaned = normalize_unicode(cleaned)
    
    # Paso 3: Eliminar caracteres de control
    cleaned = remove_control_characters(cleaned)
    
    # Paso 4: Corregir errores de OCR
    cleaned = fix_common_ocr_errors(cleaned)
    
    # Paso 5: Normalizar espacios
    cleaned = normalize_whitespace(cleaned)
    
    return cleaned


def normalize_whitespace(text: str) -> str:
    """Normaliza espacios en blanco
    
    Args:
        text: Texto con espacios irregulares
        
    Returns:
        Texto con espacios normalizados
    """
    if not text:
        return ''
    
    # Reemplazar múltiples espacios con uno solo
    import re
    
    # Normalizar diferentes tipos de espacios
    normalized = re.sub(r'[\s\u00a0\u2000-\u200f\u2028-\u202f\u205f\u3000]+', ' ', text)
    
    # Limpiar espacios al inicio y final de líneas
    lines = normalized.split('\n')
    lines = [line.strip() for line in lines]
    
    # Eliminar líneas vacías duplicadas
    clean_lines = []
    prev_empty = False
    for line in lines:
        if line.strip() == '':
            if not prev_empty:
                clean_lines.append('')
            prev_empty = True
        else:
            clean_lines.append(line)
            prev_empty = False
    
    return '\n'.join(clean_lines).strip()


def detect_encoding_issues(text: str) -> Dict[str, any]:
    """Detecta problemas de encoding en el texto
    
    Args:
        text: Texto a analizar
        
    Returns:
        Diccionario con información sobre problemas encontrados
    """
    if not text:
        return {'has_issues': False, 'issues': [], 'confidence': 1.0}
    
    issues = []
    confidence = 1.0
    
    # Detectar caracteres de BROKEN_UTF_MAP
    broken_chars_found = []
    for bad_char in BROKEN_UTF_MAP.keys():
        if bad_char in text:
            broken_chars_found.append(bad_char)
    
    if broken_chars_found:
        issues.append(f"Caracteres UTF-8 rotos: {broken_chars_found}")
        confidence -= 0.3
    
    # Detectar caracteres de control problemáticos
    control_chars = [char for char in text 
                     if unicodedata.category(char)[0] == 'C' 
                     and char not in '\t\n\r ']
    
    if control_chars:
        issues.append(f"Caracteres de control: {set(control_chars)}")
        confidence -= 0.2
    
    # Detectar posibles errores de OCR
    ocr_indicators = ['rn', 'cl', '0O', '1I']  # Simplificado
    found_indicators = [ind for ind in ocr_indicators if ind in text]
    
    if found_indicators:
        issues.append(f"Posibles errores OCR: {found_indicators}")
        confidence -= 0.1
    
    has_issues = len(issues) > 0
    
    return {
        'has_issues': has_issues,
        'issues': issues,
        'confidence': max(0.0, confidence),
        'broken_chars_count': len(broken_chars_found),
        'control_chars_count': len(control_chars),
    }


def get_text_statistics(text: str) -> Dict[str, any]:
    """Obtiene estadísticas del texto para análisis
    
    Args:
        text: Texto a analizar
        
    Returns:
        Diccionario con estadísticas
    """
    if not text:
        return {'char_count': 0, 'line_count': 0, 'word_count': 0}
    
    char_count = len(text)
    line_count = text.count('\n') + 1
    word_count = len(text.split())
    
    # Contar diferentes tipos de caracteres
    alpha_count = sum(1 for c in text if c.isalpha())
    digit_count = sum(1 for c in text if c.isdigit())
    space_count = sum(1 for c in text if c.isspace())
    punct_count = sum(1 for c in text if unicodedata.category(c)[0] == 'P')
    
    return {
        'char_count': char_count,
        'line_count': line_count,
        'word_count': word_count,
        'alpha_count': alpha_count,
        'digit_count': digit_count,
        'space_count': space_count,
        'punct_count': punct_count,
        'alpha_ratio': alpha_count / char_count if char_count > 0 else 0,
        'digit_ratio': digit_count / char_count if char_count > 0 else 0,
    }


# ======================== UTILIDADES DE TESTING ========================

def test_utf8_fixer():
    """Función de prueba para validar el corrector UTF-8"""
    print("=== Test del Corrector UTF-8 ===")
    
    # Ejemplos de texto con problemas
    test_texts = [
        "DiagnÃ³stico de cÃ¡ncer",
        "PacÃ©nte con mÃ¡lignidad",
        "â€œCarcinomaâ€ de mama",
        "Descripciï¿½n microscÃ³pica",
        "ADENOCACRINOMA ductal",
        "Tumor NUEROENDOCRINO",
    ]
    
    print("\n--- Test Corrección UTF-8 ---")
    for text in test_texts:
        cleaned = clean_text_comprehensive(text)
        issues = detect_encoding_issues(text)
        
        print(f"Original: {text}")
        print(f"Limpio:   {cleaned}")
        print(f"Problemas: {issues['issues']}")
        print(f"Confianza: {issues['confidence']:.2f}")
        print("-" * 50)


if __name__ == "__main__":
    test_utf8_fixer()