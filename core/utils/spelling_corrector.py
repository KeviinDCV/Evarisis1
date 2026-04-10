#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Corrector ortográfico para términos médicos y biomarcadores
Versión: 5.3.10
Fecha: 8 de enero de 2026

V5.3.10 (8/01/2026): FIX IHQ250162 - Limpieza de comillas escapadas y caracteres especiales
  - Problema: Comillas escapadas \" en descripciones causaban baja similitud al comparar con OCR
  - Solución: Agregada limpieza de caracteres especiales al inicio de correct_spelling():
    * Comillas escapadas \" → "
    * Comillas Unicode \u201c \u201d → "
    * Saltos de línea/tabulaciones escapados → espacio
  - Impacto: Mejora validación de descripciones macroscópicas/microscópicas
  - Ubicación: Línea 175-189 (antes de correcciones de términos médicos)

V5.3.9: Agregado tracking de correcciones aplicadas
"""

import re
from typing import Dict, List, Tuple

# ─────────────────────────── DICCIONARIO DE CORRECCIONES ─────────────────────────────

# Términos médicos con errores comunes del OCR
MEDICAL_TERMS_CORRECTIONS: Dict[str, str] = {
    # Neuroendocrino y variantes
    'NUEROENDOCRINO': 'NEUROENDOCRINO',
    'NEUROENDOCRINO': 'NEUROENDOCRINO',  # Normalización
    'NUERO-ENDOCRINO': 'NEUROENDOCRINO',
    'NEURO-ENDOCRINO': 'NEUROENDOCRINO',
    'NUEROENDOCRINA': 'NEUROENDOCRINA',
    'NEUROENDOCRINA': 'NEUROENDOCRINA',

    # Inmunohistoquímica y variantes
    'INMUNO-HISTOQUIMICA': 'INMUNOHISTOQUIMICA',
    'INMUNO HISTOQUIMICA': 'INMUNOHISTOQUIMICA',
    'INMUNOHISTOQU1MICA': 'INMUNOHISTOQUIMICA',
    'INMUN0HISTOQUIMICA': 'INMUNOHISTOQUIMICA',

    # Carcinoma y variantes
    'CARCIN0MA': 'CARCINOMA',
    'CARCINOMA': 'CARCINOMA',
    'CARCIN0MAS': 'CARCINOMAS',
    'CARC1NOMA': 'CARCINOMA',

    # Adenocarcinoma
    'ADENOCARCIN0MA': 'ADENOCARCINOMA',
    'ADENOCARCINOMA': 'ADENOCARCINOMA',
    'ADEN0CARCINOMA': 'ADENOCARCINOMA',

    # Neoplasia
    'NE0PLASIA': 'NEOPLASIA',
    'NEOPLASIA': 'NEOPLASIA',
    'NE0PLASIAS': 'NEOPLASIAS',

    # Diagnóstico
    'DIAGN0STICO': 'DIAGNOSTICO',
    'DIAGN0ST1CO': 'DIAGNOSTICO',
    'D1AGNOSTICO': 'DIAGNOSTICO',

    # Microscópica
    'MICROSC0PICA': 'MICROSCOPICA',
    'MICROSC0P1CA': 'MICROSCOPICA',
    'M1CROSCOPICA': 'MICROSCOPICA',

    # Macroscópica
    'MACROSC0PICA': 'MACROSCOPICA',
    'MACROSC0P1CA': 'MACROSCOPICA',
    'M1ACROSCOPICA': 'MACROSCOPICA',

    # Sinaptofisina (común en IHQ)
    'SINAPTOFISINA': 'SYNAPTOPHYSIN',
    'SYNAPTOPH1SIN': 'SYNAPTOPHYSIN',
    'SYNAPTOFISINA': 'SYNAPTOPHYSIN',
    'S1NAPTOPHYSIN': 'SYNAPTOPHYSIN',

    # Cromogranina
    'CR0MOGRANINA': 'CROMOGRANINA',
    'CROM0GRANINA': 'CROMOGRANINA',
    'CHR0M0GRANIN': 'CHROMOGRANIN',

    # Positivo/Negativo
    'P0SITIVO': 'POSITIVO',
    'P0SIT1VO': 'POSITIVO',
    'NEGAT1VO': 'NEGATIVO',
    'NEGAT1V0': 'NEGATIVO',

    # Receptor
    'RECEPT0R': 'RECEPTOR',
    'RECEPT0RES': 'RECEPTORES',
    'RECEPT1R': 'RECEPTOR',

    # Estrógen o
    'ESTR0GENO': 'ESTROGENO',
    'ESTR0GEN0': 'ESTROGENO',
    'ESTROGEN0': 'ESTROGENO',

    # Progesterona
    'PR0GESTERONA': 'PROGESTERONA',
    'PR0GESTER0NA': 'PROGESTERONA',
    'PROGESTERON1': 'PROGESTERONA',
}

# Patrones para normalizar biomarcadores (preservar mayúsculas/guiones)
BIOMARKER_PATTERNS: Dict[str, str] = {
    r'\bKI[\s-]?67\b': 'KI-67',
    r'\bKI[\s-]?6[7O]\b': 'KI-67',
    r'\bK1[\s-]?67\b': 'KI-67',
    r'\bP[\s]?40\b': 'P40',
    r'\bP[\s]?4O\b': 'P40',
    r'\bP[\s]?16\b': 'P16',
    r'\bP[\s]?1[6G]\b': 'P16',
    r'\bP[\s]?63\b': 'P63',
    r'\bP[\s]?6[3B]\b': 'P63',
    r'\bCK[\s]?7\b': 'CK7',
    r'\bCK[\s]?2[0O]\b': 'CK20',
    r'\bCK[\s]?5[\s/]?6\b': 'CK5/6',
    r'\bTTF[\s-]?1\b': 'TTF1',
    r'\bTTF[\s-]?[1I]\b': 'TTF1',
}


# ─────────────────────────── FUNCIONES HELPER V5.3.9 ─────────────────────────────

def detect_correction_pattern(original: str, corrected: str) -> str:
    """
    Detecta qué patrón de corrección se aplicó

    Args:
        original: Texto original
        corrected: Texto corregido

    Returns:
        Descripción del patrón aplicado
    """
    if original == corrected:
        return "Sin cambios"

    original_upper = original.upper()
    corrected_upper = corrected.upper()

    # Verificar si está en el diccionario de términos médicos
    if original_upper in MEDICAL_TERMS_CORRECTIONS:
        if MEDICAL_TERMS_CORRECTIONS[original_upper] == corrected_upper:
            # Identificar el tipo de error OCR
            if '0' in original and 'O' in corrected:
                return "Corrección OCR: 0 → O"
            elif '1' in original and 'I' in corrected:
                return "Corrección OCR: 1 → I"
            elif '1' in original and 'L' in corrected:
                return "Corrección OCR: 1 → L"
            else:
                return f"Corrección ortográfica: {original_upper} → {corrected_upper}"

    # Verificar si es normalización de biomarcador
    for pattern, normalized in BIOMARKER_PATTERNS.items():
        if re.match(pattern, original, re.IGNORECASE):
            if normalized.upper() == corrected_upper:
                return f"Normalización biomarcador: espacios/guiones corregidos"

    # Corrección general
    return f"Corrección automática"


# ─────────────────────────── FUNCIONES DE CORRECCIÓN ─────────────────────────────

def correct_spelling(text: str, case_sensitive: bool = False) -> str:
    """
    Corrige errores ortográficos en términos médicos

    Args:
        text: Texto a corregir
        case_sensitive: Si debe respetar mayúsculas/minúsculas

    Returns:
        Texto corregido
    """
    if not text:
        return text

    corrected = text

    # 0. V5.3.10 FIX IHQ250162: Limpieza de caracteres especiales (ANTES de correcciones)
    # Problema: Comillas escapadas \"  y comillas Unicode causan fallos en comparaciones
    # Solución: Normalizar a comillas estándar al inicio del proceso

    # Reemplazar comillas escapadas literales (backslash + comilla)
    corrected = corrected.replace('\\"', '"')       # Comillas dobles escapadas → comillas normales
    corrected = corrected.replace("\\'", "'")       # Comillas simples escapadas → comillas simples

    # Reemplazar comillas Unicode (caracteres Unicode reales)
    corrected = corrected.replace('\u201c', '"')    # Comilla Unicode izquierda "
    corrected = corrected.replace('\u201d', '"')    # Comilla Unicode derecha "
    corrected = corrected.replace('\u2018', "'")    # Comilla simple Unicode izquierda '
    corrected = corrected.replace('\u2019', "'")    # Comilla simple Unicode derecha '

    # Reemplazar otros caracteres especiales escapados
    corrected = corrected.replace('\\n', ' ')       # Saltos de línea escapados → espacio
    corrected = corrected.replace('\\t', ' ')       # Tabulaciones escapadas → espacio

    # Normalizar espacios múltiples resultantes de limpiezas
    corrected = re.sub(r'\s+', ' ', corrected)

    # 1. Correcciones de términos médicos (case-insensitive por defecto)
    for wrong, correct in MEDICAL_TERMS_CORRECTIONS.items():
        if case_sensitive:
            corrected = corrected.replace(wrong, correct)
        else:
            # Reemplazar ignorando mayúsculas/minúsculas pero preservando el case del texto
            pattern = re.compile(re.escape(wrong), re.IGNORECASE)

            def replace_preserving_case(match):
                original = match.group(0)
                # Si el original está todo en mayúsculas, devolver corrección en mayúsculas
                if original.isupper():
                    return correct.upper()
                # Si el original está en minúsculas, devolver corrección en minúsculas
                elif original.islower():
                    return correct.lower()
                # Si es capitalizado, capitalizar la corrección
                elif original[0].isupper() and original[1:].islower():
                    return correct.capitalize()
                # Por defecto, devolver la corrección tal cual
                return correct

            corrected = pattern.sub(replace_preserving_case, corrected)

    # 2. Normalización de biomarcadores (preservar formato estándar)
    for pattern, normalized in BIOMARKER_PATTERNS.items():
        corrected = re.sub(pattern, normalized, corrected, flags=re.IGNORECASE)

    # 3. V6.3.28: FIX IHQ250028 - Corregir espacios faltantes entre número y palabra
    # Formato común OCR: "M2408063que" → "M2408063 que"
    # Patrón: número seguido directamente de letra minúscula (sin espacio)
    # V6.3.75 FIX IHQ250094: EXCLUIR biomarcadores conocidos que terminan en letra minúscula
    # Ej: CD1a, CD3, p16, p40, p53 - NO deben separarse como "CD1 a", "p 16"
    # Paso 1: Proteger biomarcadores conocidos con placeholder
    biomarkers_to_protect = [
        (r'\bCD1a\b', '##CD1A_PLACEHOLDER##'),
        (r'\bCD3\b', '##CD3_PLACEHOLDER##'),
        (r'\bp16\b', '##P16_PLACEHOLDER##'),
        (r'\bp40\b', '##P40_PLACEHOLDER##'),
        (r'\bp53\b', '##P53_PLACEHOLDER##'),
        (r'\bp63\b', '##P63_PLACEHOLDER##'),
    ]
    for pattern, placeholder in biomarkers_to_protect:
        corrected = re.sub(pattern, placeholder, corrected, flags=re.IGNORECASE)

    # Paso 2: Aplicar corrección de espacios
    corrected = re.sub(r'(\d)([a-záéíóúñ])', r'\1 \2', corrected)

    # Paso 3: Restaurar biomarcadores
    biomarkers_restore = [
        ('##CD1A_PLACEHOLDER##', 'CD1a'),
        ('##CD3_PLACEHOLDER##', 'CD3'),
        ('##P16_PLACEHOLDER##', 'p16'),
        ('##P40_PLACEHOLDER##', 'p40'),
        ('##P53_PLACEHOLDER##', 'p53'),
        ('##P63_PLACEHOLDER##', 'p63'),
    ]
    for placeholder, biomarker in biomarkers_restore:
        corrected = corrected.replace(placeholder, biomarker)

    return corrected


def correct_medical_field(field_value: str, field_type: str = 'general') -> str:
    """
    Corrige un campo médico específico

    Args:
        field_value: Valor del campo a corregir
        field_type: Tipo de campo ('diagnosis', 'biomarker', 'organ', 'general')

    Returns:
        Valor corregido
    """
    if not field_value:
        return field_value

    # Aplicar corrección general
    corrected = correct_spelling(field_value)

    # Correcciones específicas por tipo de campo
    if field_type == 'biomarker':
        # Normalizar nombres de biomarcadores
        corrected = corrected.strip().upper()

        # Corregir espacios en biomarcadores compuestos
        corrected = re.sub(r'CK\s+AE\s*1\s*/\s*AE\s*3', 'CKAE1/AE3', corrected)
        corrected = re.sub(r'AE\s*1\s*/\s*AE\s*3', 'AE1/AE3', corrected)

    elif field_type == 'diagnosis':
        # Correcciones específicas para diagnósticos
        # Normalizar espacios múltiples
        corrected = re.sub(r'\s+', ' ', corrected).strip()

    elif field_type == 'organ':
        # Normalizar órganos a mayúsculas
        corrected = corrected.strip().upper()

    return corrected


def correct_extracted_data(extracted_data: Dict[str, any], numero_caso: str = "") -> Tuple[Dict[str, any], List[Dict]]:
    """
    Corrige todos los campos de un diccionario de datos extraídos

    V5.3.9: Ahora retorna también las correcciones aplicadas

    Args:
        extracted_data: Diccionario con datos extraídos
        numero_caso: Número de caso IHQ (opcional, para tracking)

    Returns:
        Tuple con:
        - Diccionario con datos corregidos
        - Lista de correcciones aplicadas (cada una es un Dict con tipo, campo, antes, después, razón)
    """
    if not extracted_data:
        return extracted_data, []

    corrected_data = extracted_data.copy()
    correcciones = []

    # Campos de diagnóstico
    diagnosis_fields = [
        'diagnostico_final_ihq', 'diagnostico', 'ihq_diagnostico',
        'descripcion_macroscopica', 'descripcion_microscopica',
        'comentarios', 'observaciones', 'Diagnostico Principal'  # V5.3.9: Agregado campo BD
    ]

    for field in diagnosis_fields:
        if field in corrected_data and corrected_data[field]:
            original_value = corrected_data[field]
            corrected_value = correct_medical_field(original_value, field_type='diagnosis')

            # Si hubo corrección, registrarla
            if original_value != corrected_value:
                razon = detect_correction_pattern(original_value, corrected_value)
                correcciones.append({
                    "tipo": "ortografica",
                    "campo": field,
                    "valor_original": original_value,
                    "valor_corregido": corrected_value,
                    "razon": razon,
                    "numero_caso": numero_caso
                })
                corrected_data[field] = corrected_value

    # Campos de órgano
    organ_fields = ['organo', 'ihq_organo', 'organo_medical', 'Organo (1. Muestra enviada a patología)']

    for field in organ_fields:
        if field in corrected_data and corrected_data[field]:
            original_value = corrected_data[field]
            corrected_value = correct_medical_field(original_value, field_type='organ')

            if original_value != corrected_value:
                razon = detect_correction_pattern(original_value, corrected_value)
                correcciones.append({
                    "tipo": "ortografica",
                    "campo": field,
                    "valor_original": original_value,
                    "valor_corregido": corrected_value,
                    "razon": razon,
                    "numero_caso": numero_caso
                })
                corrected_data[field] = corrected_value

    # Campos de biomarcadores (estado y valores)
    biomarker_fields = [k for k in corrected_data.keys() if '_ESTADO' in k or '_VALOR' in k]

    for field in biomarker_fields:
        if corrected_data[field]:
            original_value = corrected_data[field]

            # Para estados, corregir como texto general
            if '_ESTADO' in field:
                corrected_value = correct_medical_field(original_value, field_type='general')

                if original_value != corrected_value:
                    razon = detect_correction_pattern(original_value, corrected_value)
                    correcciones.append({
                        "tipo": "ortografica",
                        "campo": field,
                        "valor_original": original_value,
                        "valor_corregido": corrected_value,
                        "razon": razon,
                        "numero_caso": numero_caso
                    })
                    corrected_data[field] = corrected_value

            # Para valores numéricos, no modificar
            elif '_VALOR' in field and isinstance(corrected_data[field], str):
                corrected_value = correct_medical_field(original_value, field_type='general')

                if original_value != corrected_value:
                    razon = detect_correction_pattern(original_value, corrected_value)
                    correcciones.append({
                        "tipo": "ortografica",
                        "campo": field,
                        "valor_original": original_value,
                        "valor_corregido": corrected_value,
                        "razon": razon,
                        "numero_caso": numero_caso
                    })
                    corrected_data[field] = corrected_value

    return corrected_data, correcciones


def get_corrections_report(original: str, corrected: str) -> List[str]:
    """
    Genera un reporte de las correcciones realizadas

    Args:
        original: Texto original
        corrected: Texto corregido

    Returns:
        Lista de correcciones en formato 'original → corregido'
    """
    if original == corrected:
        return []

    corrections = []

    # Detectar cambios palabra por palabra
    original_words = set(re.findall(r'\b\w+\b', original.upper()))
    corrected_words = set(re.findall(r'\b\w+\b', corrected.upper()))

    changed_words = original_words - corrected_words

    for wrong_word in changed_words:
        # Buscar la palabra corregida correspondiente
        for correct_word in corrected_words:
            if correct_word not in original_words:
                # Verificar si es una corrección conocida
                if wrong_word in MEDICAL_TERMS_CORRECTIONS:
                    if MEDICAL_TERMS_CORRECTIONS[wrong_word].upper() == correct_word:
                        corrections.append(f"{wrong_word} -> {correct_word}")
                        break

    return corrections
