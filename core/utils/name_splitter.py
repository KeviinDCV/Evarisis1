#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Utilidad para división inteligente de nombres completos

Separa nombres completos en nombres y apellidos usando heurística
basada en apellidos comunes colombianos y morfología de apellidos.

Versión: 4.0.0
Migrado de: core/procesador_ihq.py (función split_full_name)
"""

import re
import logging
from typing import Dict, Set
from core.utils.patient_mappings import (
    APELLIDOS_COMUNES,
    NOMBRES_COMPUESTOS_INICIO,
    NOMBRES_EXCLUSION_MORFOLOGIA
)

# Patrón para detectar morfología típica de apellidos castellanos
_PATRON_MORFO_APELLIDO = re.compile(r'.{3,}(?:EZ|ES|OS|AS|IS|OR|AR|AL|ER|IN|ON)$', re.IGNORECASE)


def _es_apellido(token: str) -> bool:
    """Determina si un token es probablemente un apellido
    
    Args:
        token: Palabra a evaluar
        
    Returns:
        True si es probablemente un apellido
    """
    if not token or len(token) < 2:
        return False
        
    t = token.upper()
    
    # Verificar lista de apellidos comunes
    if t in APELLIDOS_COMUNES:
        return True
    
    # Evitar que nombres frecuentes sean falsos positivos
    if t in NOMBRES_COMPUESTOS_INICIO or t in NOMBRES_EXCLUSION_MORFOLOGIA:
        return False
    
    # Verificar morfología típica de apellidos castellanos
    if _PATRON_MORFO_APELLIDO.match(t):
        return True
    
    return False


def split_full_name(full_name: str) -> Dict[str, str]:
    """Divide un nombre completo en nombres y apellidos usando heurística mejorada
    
    Args:
        full_name: Nombre completo (ej: "DIEGO HERNAN RUIZ IMBACHI")
        
    Returns:
        Diccionario con claves:
        - 'nombres': Nombres separados por espacio
        - 'apellidos': Apellidos separados por espacio
        - 'nombre_completo': Nombre original
        
    Ejemplos:
        >>> split_full_name("DIEGO HERNAN RUIZ IMBACHI")
        {'nombres': 'DIEGO HERNAN', 'apellidos': 'RUIZ IMBACHI', 'nombre_completo': 'DIEGO HERNAN RUIZ IMBACHI'}
        
        >>> split_full_name("MARIA JOSE GARCIA")
        {'nombres': 'MARIA JOSE', 'apellidos': 'GARCIA', 'nombre_completo': 'MARIA JOSE GARCIA'}
    """
    if not full_name or not full_name.strip():
        return {
            'nombres': '',
            'apellidos': '',
            'nombre_completo': ''
        }
    
    # Limpiar y normalizar
    name_clean = full_name.strip().upper()
    tokens = [t for t in name_clean.split() if t and len(t) > 1]
    
    if not tokens:
        return {
            'nombres': '',
            'apellidos': '',
            'nombre_completo': name_clean
        }
    
    # Caso especial: solo un token
    if len(tokens) == 1:
        return {
            'nombres': tokens[0],
            'apellidos': '',
            'nombre_completo': name_clean
        }
    
    # Caso especial: dos tokens
    if len(tokens) == 2:
        # Si el segundo es claramente apellido, dividir así
        if _es_apellido(tokens[1]):
            return {
                'nombres': tokens[0],
                'apellidos': tokens[1],
                'nombre_completo': name_clean
            }
        else:
            # Probablemente dos nombres o nombre compuesto
            return {
                'nombres': ' '.join(tokens),
                'apellidos': '',
                'nombre_completo': name_clean
            }
    
    # Caso general: 3+ tokens
    # Buscar el primer apellido (divide nombres de apellidos)
    primer_apellido_idx = None

    # v5.3.2 FIX: Buscar TODOS los índices de apellidos, no solo el primero
    apellido_indices = [i for i, token in enumerate(tokens) if _es_apellido(token)]

    if apellido_indices:
        # v5.3.2 FIX: Si el primer token es apellido pero hay otros apellidos después,
        # usar el siguiente apellido para evitar tomar nombres como apellidos
        # Ejemplo: "MERCEDES DEL CARMEN VIVEROS CALDERON"
        #          MERCEDES=apellido, pero es nombre en este contexto
        #          Verdaderos apellidos: VIVEROS CALDERON
        if apellido_indices[0] == 0 and len(apellido_indices) > 1:
            # Hay más apellidos adelante, usar el siguiente
            primer_apellido_idx = apellido_indices[1]
        else:
            # Usar el primer apellido encontrado
            primer_apellido_idx = apellido_indices[0]

    # Si no encontramos apellidos, asumir que los últimos 2 son apellidos
    if primer_apellido_idx is None:
        if len(tokens) >= 3:
            primer_apellido_idx = len(tokens) - 2
        else:
            primer_apellido_idx = len(tokens) - 1
    
    # Casos especiales para nombres compuestos al inicio
    if len(tokens) >= 2:
        nombre_compuesto = ' '.join(tokens[:2])
        if nombre_compuesto in NOMBRES_COMPUESTOS_INICIO:
            # Ajustar índice si tenemos nombre compuesto
            if primer_apellido_idx <= 2:
                primer_apellido_idx = max(2, primer_apellido_idx)
    
    # Dividir en nombres y apellidos
    nombres = tokens[:primer_apellido_idx] if primer_apellido_idx > 0 else [tokens[0]]
    apellidos = tokens[primer_apellido_idx:] if primer_apellido_idx < len(tokens) else []
    
    return {
        'nombres': ' '.join(nombres),
        'apellidos': ' '.join(apellidos),
        'nombre_completo': name_clean
    }


def get_nombre_formal(nombres: str, apellidos: str) -> str:
    """Construye nombre formal (Apellidos, Nombres)
    
    Args:
        nombres: Nombres del paciente
        apellidos: Apellidos del paciente
        
    Returns:
        Nombre en formato "APELLIDOS, NOMBRES"
    """
    if not apellidos:
        return nombres or ''
    
    if not nombres:
        return apellidos
    
    return f"{apellidos}, {nombres}"


def get_primer_nombre(nombres: str) -> str:
    """Extrae el primer nombre
    
    Args:
        nombres: Nombres completos
        
    Returns:
        Primer nombre o string vacío
    """
    if not nombres:
        return ''
    
    tokens = nombres.strip().split()
    return tokens[0] if tokens else ''


def display_name_clean(primer_nombre: str, segundo_nombre: str,
                        primer_apellido: str, segundo_apellido: str) -> str:
    """
    Construye nombre completo para MOSTRAR en UI (sin N/A) - V5.3.9

    NOTA: Los datos en BD pueden tener 'N/A', pero en UI se filtran.
    Esta función reutiliza la lógica de build_clean_full_name() de unified_extractor.

    Args:
        primer_nombre: Primer nombre (puede ser 'N/A' o vacío)
        segundo_nombre: Segundo nombre (puede ser 'N/A' o vacío)
        primer_apellido: Primer apellido (puede ser 'N/A' o vacío)
        segundo_apellido: Segundo apellido (puede ser 'N/A' o vacío)

    Returns:
        Nombre completo limpio sin N/A para mostrar en UI

    Example:
        >>> display_name_clean("MERCEDES", "DEL CARMEN", "VIVEROS", "CALDERON")
        "MERCEDES DEL CARMEN VIVEROS CALDERON"

        >>> display_name_clean("JUAN", "N/A", "PEREZ", "N/A")
        "JUAN PEREZ"  # Sin N/A
    """
    parts = []

    # Agregar primer nombre (siempre debería existir)
    if primer_nombre and primer_nombre not in ['N/A', 'nan', '', 'None', 'null']:
        parts.append(primer_nombre.strip())

    # Agregar segundo nombre solo si existe y no es N/A
    if segundo_nombre and segundo_nombre not in ['N/A', 'nan', '', 'None', 'null']:
        parts.append(segundo_nombre.strip())

    # Agregar primer apellido (siempre debería existir)
    if primer_apellido and primer_apellido not in ['N/A', 'nan', '', 'None', 'null']:
        parts.append(primer_apellido.strip())

    # Agregar segundo apellido solo si existe y no es N/A
    if segundo_apellido and segundo_apellido not in ['N/A', 'nan', '', 'None', 'null']:
        parts.append(segundo_apellido.strip())

    return ' '.join(parts) if parts else 'N/A'


def clean_display_name(nombre: str) -> str:
    """
    Limpia nombre completo eliminando 'N/A' para mostrar en UI (V5.3.9)

    Args:
        nombre: Nombre que puede contener 'N/A'

    Returns:
        Nombre limpio sin 'N/A'

    Example:
        >>> clean_display_name("JUAN N/A PEREZ N/A")
        "JUAN PEREZ"

        >>> clean_display_name("MERCEDES DEL CARMEN VIVEROS CALDERON")
        "MERCEDES DEL CARMEN VIVEROS CALDERON"
    """
    if not nombre:
        return ""

    # Eliminar todas las ocurrencias de N/A y variantes
    nombre_limpio = nombre
    for na_variant in ['N/A', 'nan', 'None', 'null']:
        nombre_limpio = nombre_limpio.replace(na_variant, '')

    # Limpiar espacios múltiples
    import re
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio).strip()

    return nombre_limpio if nombre_limpio else 'N/A'


def get_primer_apellido(apellidos: str) -> str:
    """Extrae el primer apellido

    Args:
        apellidos: Apellidos completos

    Returns:
        Primer apellido o string vacío
    """
    if not apellidos:
        return ''

    tokens = apellidos.strip().split()
    return tokens[0] if tokens else ''


def validate_name_split(full_name: str, nombres: str, apellidos: str) -> Dict[str, any]:
    """Valida que la división de nombres sea razonable
    
    Args:
        full_name: Nombre completo original
        nombres: Nombres extraídos
        apellidos: Apellidos extraídos
        
    Returns:
        Diccionario con validación:
        - 'is_valid': True si la división parece correcta
        - 'warnings': Lista de advertencias
        - 'confidence': Nivel de confianza (0.0-1.0)
    """
    warnings = []
    confidence = 1.0
    
    # Verificar que no se perdieron tokens
    original_tokens = set(full_name.upper().split())
    split_tokens = set((nombres + ' ' + apellidos).upper().split())
    
    missing_tokens = original_tokens - split_tokens
    if missing_tokens:
        warnings.append(f"Tokens perdidos: {missing_tokens}")
        confidence -= 0.3
    
    # Verificar que tenemos al menos algo
    if not nombres and not apellidos:
        warnings.append("No se pudo extraer nombres ni apellidos")
        confidence = 0.0
    
    # Verificar balance (no todos nombres o todos apellidos para >2 tokens)
    if len(full_name.split()) > 2:
        if not nombres:
            warnings.append("Solo se encontraron apellidos")
            confidence -= 0.2
        elif not apellidos:
            warnings.append("Solo se encontraron nombres")
            confidence -= 0.2
    
    # Verificar morfología de apellidos
    if apellidos:
        apellido_tokens = apellidos.split()
        apellidos_reconocidos = sum(1 for token in apellido_tokens if _es_apellido(token))
        if apellidos_reconocidos == 0 and len(apellido_tokens) > 0:
            warnings.append("Ningún apellido reconocido morfológicamente")
            confidence -= 0.1
    
    is_valid = confidence >= 0.5
    
    return {
        'is_valid': is_valid,
        'warnings': warnings,
        'confidence': confidence
    }


# ======================== UTILIDADES DE TESTING ========================

def test_name_splitter():
    """Función de prueba para validar el divisor de nombres"""
    test_cases = [
        "DIEGO HERNAN RUIZ IMBACHI",
        "MARIA JOSE GARCIA PEREZ",
        "JUAN CARLOS RODRIGUEZ",
        "ANA SOFIA MARTINEZ HERNANDEZ",
        "LUIS FERNANDO GOMEZ",
        "CARLOS ALBERTO VARGAS CAICEDO",
        "SOFIA VALENCIA",
        "ARMANDO CORTES BUELVAS",
    ]
    
    logging.info("=== Test del Divisor de Nombres ===")
    for name in test_cases:
        result = split_full_name(name)
        validation = validate_name_split(name, result['nombres'], result['apellidos'])
        
        logging.info(f"\nNombre: {name}")
        logging.info(f"  Nombres: {result['nombres']}")
        logging.info(f"  Apellidos: {result['apellidos']}")
        logging.info(f"  Válido: {validation['is_valid']} (confianza: {validation['confidence']:.2f})")
        if validation['warnings']:
            logging.info(f"  Advertencias: {', '.join(validation['warnings'])}")


if __name__ == "__main__":
    test_name_splitter()