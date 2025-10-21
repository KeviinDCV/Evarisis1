#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidad para procesamiento y cálculo de fechas

Maneja fechas de pacientes, cálculo de edad, conversión de formatos
y validaciones específicas para el sistema HUV.

Versión: 4.0.0
Migrado de: core/procesador_ihq.py (función calculate_birth_date y similares)
"""

import re
import logging
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import Optional, Dict, Tuple, Union


# Patrones para extracción de fechas en diferentes formatos
DATE_PATTERNS = {
    'dd/mm/yyyy': re.compile(r'(\d{1,2})/(\d{1,2})/(\d{4})'),
    'yyyy-mm-dd': re.compile(r'(\d{4})-(\d{1,2})-(\d{1,2})'),
    'dd-mm-yyyy': re.compile(r'(\d{1,2})-(\d{1,2})-(\d{4})'),
    'dd.mm.yyyy': re.compile(r'(\d{1,2})\.(\d{1,2})\.(\d{4})'),
}

# Patrones para edad en texto
AGE_PATTERNS = {
    'años_meses_días': re.compile(r'(\d+)\s+años?\s+(\d+)\s+meses?\s+(\d+)\s+días?', re.IGNORECASE),
    'años_meses': re.compile(r'(\d+)\s+años?\s+(\d+)\s+meses?', re.IGNORECASE),
    'años_días': re.compile(r'(\d+)\s+años?\s+(\d+)\s+días?', re.IGNORECASE),
    'solo_años': re.compile(r'(\d+)\s+años?', re.IGNORECASE),
    'meses_días': re.compile(r'(\d+)\s+meses?\s+(\d+)\s+días?', re.IGNORECASE),
    'solo_meses': re.compile(r'(\d+)\s+meses?', re.IGNORECASE),
    'solo_días': re.compile(r'(\d+)\s+días?', re.IGNORECASE),
}

# Meses en español para conversión
MESES_ESPAÑOL = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12,
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4,
    'may': 5, 'jun': 6, 'jul': 7, 'ago': 8,
    'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12,
}


def parse_date(date_string: str, default_format: str = 'dd/mm/yyyy') -> Optional[date]:
    """Convierte string de fecha a objeto date
    
    Args:
        date_string: Fecha en formato string
        default_format: Formato esperado por defecto
        
    Returns:
        Objeto date o None si no se puede parsear
    """
    if not date_string or not date_string.strip():
        return None
    
    date_clean = date_string.strip()
    
    # Intentar con todos los patrones
    for format_name, pattern in DATE_PATTERNS.items():
        match = pattern.search(date_clean)
        if match:
            try:
                if format_name == 'yyyy-mm-dd':
                    year, month, day = match.groups()
                else:
                    day, month, year = match.groups()
                
                return date(int(year), int(month), int(day))
            except (ValueError, TypeError):
                continue
    
    # Intentar parseo manual para formatos especiales
    try:
        # Formato DD/MM/YYYY (más común)
        if '/' in date_clean:
            parts = date_clean.split('/')
            if len(parts) == 3:
                day, month, year = parts
                return date(int(year), int(month), int(day))
    except (ValueError, TypeError, IndexError):
        pass
    
    return None


def format_date(date_obj: date, format_type: str = 'dd/mm/yyyy') -> str:
    """Formatea objeto date a string
    
    Args:
        date_obj: Objeto date
        format_type: Tipo de formato deseado
        
    Returns:
        Fecha formateada como string
    """
    if not date_obj:
        return ''
    
    if format_type == 'dd/mm/yyyy':
        return date_obj.strftime('%d/%m/%Y')
    elif format_type == 'yyyy-mm-dd':
        return date_obj.strftime('%Y-%m-%d')
    elif format_type == 'dd-mm-yyyy':
        return date_obj.strftime('%d-%m-%Y')
    elif format_type == 'dd.mm.yyyy':
        return date_obj.strftime('%d.%m.%Y')
    else:
        return date_obj.strftime('%d/%m/%Y')  # Default


def parse_age_text(age_text: str) -> Dict[str, int]:
    """Extrae edad en años, meses y días de texto
    
    Args:
        age_text: Texto con edad (ej: "45 años 3 meses 12 días")
        
    Returns:
        Diccionario con claves: 'años', 'meses', 'días'
    """
    if not age_text:
        return {'años': 0, 'meses': 0, 'días': 0}
    
    age_clean = age_text.strip().lower()
    
    # Intentar con cada patrón
    for pattern_name, pattern in AGE_PATTERNS.items():
        match = pattern.search(age_clean)
        if match:
            groups = match.groups()
            
            if pattern_name == 'años_meses_días':
                return {'años': int(groups[0]), 'meses': int(groups[1]), 'días': int(groups[2])}
            elif pattern_name == 'años_meses':
                return {'años': int(groups[0]), 'meses': int(groups[1]), 'días': 0}
            elif pattern_name == 'años_días':
                return {'años': int(groups[0]), 'meses': 0, 'días': int(groups[1])}
            elif pattern_name == 'solo_años':
                return {'años': int(groups[0]), 'meses': 0, 'días': 0}
            elif pattern_name == 'meses_días':
                return {'años': 0, 'meses': int(groups[0]), 'días': int(groups[1])}
            elif pattern_name == 'solo_meses':
                return {'años': 0, 'meses': int(groups[0]), 'días': 0}
            elif pattern_name == 'solo_días':
                return {'años': 0, 'meses': 0, 'días': int(groups[0])}
    
    return {'años': 0, 'meses': 0, 'días': 0}


def calculate_birth_date(reference_date: Union[date, str], age_text: str) -> Optional[date]:
    """Calcula fecha de nacimiento basada en edad y fecha de referencia
    
    Args:
        reference_date: Fecha de referencia (ingreso/informe)
        age_text: Texto con edad del paciente
        
    Returns:
        Fecha de nacimiento calculada o None si no se puede calcular
    """
    # Convertir fecha de referencia si es string
    if isinstance(reference_date, str):
        reference_date = parse_date(reference_date)
    
    if not reference_date:
        return None
    
    # Extraer edad
    age_parts = parse_age_text(age_text)
    
    # Calcular fecha de nacimiento restando la edad
    try:
        birth_date = reference_date - relativedelta(
            years=age_parts['años'],
            months=age_parts['meses'],
            days=age_parts['días']
        )
        return birth_date
    except (ValueError, TypeError):
        return None


def calculate_age(birth_date: Union[date, str], reference_date: Optional[Union[date, str]] = None) -> Dict[str, int]:
    """Calcula edad basada en fecha de nacimiento
    
    Args:
        birth_date: Fecha de nacimiento
        reference_date: Fecha de referencia (por defecto fecha actual)
        
    Returns:
        Diccionario con edad en años, meses y días
    """
    # Convertir fechas si son strings
    if isinstance(birth_date, str):
        birth_date = parse_date(birth_date)
    
    if isinstance(reference_date, str):
        reference_date = parse_date(reference_date)
    elif reference_date is None:
        reference_date = date.today()
    
    if not birth_date or not reference_date:
        return {'años': 0, 'meses': 0, 'días': 0}
    
    try:
        delta = relativedelta(reference_date, birth_date)
        return {
            'años': delta.years,
            'meses': delta.months,
            'días': delta.days
        }
    except (ValueError, TypeError):
        return {'años': 0, 'meses': 0, 'días': 0}


def format_age(años: int, meses: int = 0, días: int = 0) -> str:
    """Formatea edad en texto legible
    
    Args:
        años: Años de edad
        meses: Meses adicionales
        días: Días adicionales
        
    Returns:
        Edad formateada (ej: "45 años 3 meses 12 días")
    """
    parts = []
    
    if años > 0:
        parts.append(f"{años} año{'s' if años != 1 else ''}")
    
    if meses > 0:
        parts.append(f"{meses} mes{'es' if meses != 1 else ''}")
    
    if días > 0:
        parts.append(f"{días} día{'s' if días != 1 else ''}")
    
    if not parts:
        return "0 días"
    
    return ' '.join(parts)


def validate_date(date_obj: date, min_year: int = 1900, max_year: Optional[int] = None) -> Dict[str, any]:
    """Valida que una fecha sea razonable
    
    Args:
        date_obj: Fecha a validar
        min_year: Año mínimo válido
        max_year: Año máximo válido (por defecto año actual + 1)
        
    Returns:
        Diccionario con validación:
        - 'is_valid': True si la fecha es válida
        - 'warnings': Lista de advertencias
    """
    if max_year is None:
        max_year = date.today().year + 1
    
    warnings = []
    is_valid = True
    
    if not date_obj:
        return {'is_valid': False, 'warnings': ['Fecha no proporcionada']}
    
    # Verificar rango de años
    if date_obj.year < min_year:
        warnings.append(f"Año muy antiguo: {date_obj.year}")
        is_valid = False
    
    if date_obj.year > max_year:
        warnings.append(f"Año futuro: {date_obj.year}")
        is_valid = False
    
    # Verificar que no sea fecha futura para fechas de nacimiento
    if date_obj > date.today():
        warnings.append("Fecha en el futuro")
        is_valid = False
    
    return {
        'is_valid': is_valid,
        'warnings': warnings
    }


def get_age_group(años: int) -> str:
    """Categoriza edad en grupos etarios
    
    Args:
        años: Edad en años
        
    Returns:
        Grupo etario como string
    """
    if años < 1:
        return 'NEONATO'
    elif años < 2:
        return 'LACTANTE'
    elif años < 12:
        return 'NIÑO'
    elif años < 18:
        return 'ADOLESCENTE'
    elif años < 65:
        return 'ADULTO'
    else:
        return 'ADULTO MAYOR'


def normalize_date_format(date_string: str, target_format: str = 'dd/mm/yyyy') -> str:
    """Normaliza fecha a formato estándar

    Args:
        date_string: Fecha en cualquier formato soportado
        target_format: Formato objetivo

    Returns:
        Fecha normalizada o string original si no se puede parsear
    """
    parsed_date = parse_date(date_string)
    if parsed_date:
        return format_date(parsed_date, target_format)
    return date_string


def convert_date_format(date_str: str) -> str:
    """Convierte fecha a formato DD/MM/YYYY estándar

    Función de compatibilidad con procesador_ihq.py legacy.
    Intenta convertir fechas en múltiples formatos al formato estándar DD/MM/YYYY.

    Args:
        date_str: Fecha en cualquier formato soportado

    Returns:
        Fecha en formato DD/MM/YYYY o string original si no se puede convertir
    """
    if not date_str:
        return ''

    # Intentar con formatos comunes
    for fmt in ('%d/%m/%Y', '%Y-%m-%d', '%d-%m-%Y'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
        except ValueError:
            continue

    # Fallback si no se pudo convertir
    return date_str


# ======================== UTILIDADES DE TESTING ========================

def test_date_processor():
    """Función de prueba para validar el procesador de fechas"""
    logging.info("=== Test del Procesador de Fechas ===")
    
    # Test parsing de fechas
    test_dates = [
        "15/01/2025",
        "2025-01-15",
        "15-01-2025",
        "15.01.2025",
    ]
    
    logging.info("\n--- Test Parsing Fechas ---")
    for date_str in test_dates:
        parsed = parse_date(date_str)
        logging.info(f"{date_str} -> {parsed}")
    
    # Test parsing de edades
    test_ages = [
        "45 años 3 meses 12 días",
        "25 años",
        "6 meses 15 días",
        "30 días",
        "2 años 6 meses",
    ]
    
    logging.info("\n--- Test Parsing Edades ---")
    for age_str in test_ages:
        parsed = parse_age_text(age_str)
        formatted = format_age(parsed['años'], parsed['meses'], parsed['días'])
        logging.info(f"{age_str} -> {parsed} -> {formatted}")
    
    # Test cálculo de fecha de nacimiento
    logging.info("\n--- Test Cálculo Fecha Nacimiento ---")
    ref_date = date(2025, 1, 15)
    for age_str in test_ages[:3]:
        birth_date = calculate_birth_date(ref_date, age_str)
        logging.info(f"Ref: {ref_date}, Edad: {age_str} -> Nacimiento: {birth_date}")


if __name__ == "__main__":
    test_date_processor()