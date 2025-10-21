#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database Helpers - Funciones auxiliares para operaciones de base de datos
Funciones independientes para manejo de datos y validaciones
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


def validar_numero_peticion(numero: str) -> Tuple[bool, str]:
    """
    Valida formato de número de petición IHQ

    Args:
        numero: Número de petición a validar

    Returns:
        Tupla (es_valido, mensaje)
    """
    if not numero:
        return False, "Número de petición vacío"

    # Formato esperado: IHQ + 6 dígitos (ej: IHQ250001)
    patron = r'^IHQ\d{6}$'
    if re.match(patron, numero):
        return True, "Formato válido"

    # También aceptar otros formatos comunes
    if numero.startswith('IHQ') and len(numero) >= 7:
        return True, "Formato aceptado (variante)"

    return False, f"Formato inválido (esperado: IHQnnnnnn)"


def validar_campo_requerido(valor: Any, nombre_campo: str) -> Tuple[bool, str]:
    """
    Valida que un campo requerido tenga valor

    Args:
        valor: Valor del campo
        nombre_campo: Nombre del campo para mensaje de error

    Returns:
        Tupla (es_valido, mensaje)
    """
    if valor is None or valor == "" or str(valor).strip() == "":
        return False, f"{nombre_campo} es requerido"

    if isinstance(valor, str) and valor.upper() == "N/A":
        return False, f"{nombre_campo} está marcado como N/A"

    return True, "Campo válido"


def normalizar_genero(genero: str) -> str:
    """
    Normaliza el género a formato estándar

    Args:
        genero: Género a normalizar (M/F, Masculino/Femenino, Hombre/Mujer, etc.)

    Returns:
        Género normalizado: "Masculino" o "Femenino" o "No especificado"
    """
    if not genero:
        return "No especificado"

    genero_lower = str(genero).lower().strip()

    masculinos = ['m', 'masculino', 'hombre', 'male']
    femeninos = ['f', 'femenino', 'mujer', 'female']

    if genero_lower in masculinos:
        return "Masculino"
    elif genero_lower in femeninos:
        return "Femenino"
    else:
        return "No especificado"


def validar_edad(edad: Any) -> Tuple[bool, str, Optional[int]]:
    """
    Valida que la edad sea un valor razonable

    Args:
        edad: Edad a validar

    Returns:
        Tupla (es_valido, mensaje, edad_normalizada)
    """
    if edad is None or edad == "":
        return False, "Edad vacía", None

    try:
        edad_int = int(edad)

        if edad_int < 0:
            return False, "Edad no puede ser negativa", None

        if edad_int > 120:
            return False, "Edad fuera de rango razonable (>120)", None

        return True, "Edad válida", edad_int

    except (ValueError, TypeError):
        return False, f"Edad debe ser un número entero (recibido: {edad})", None


def normalizar_fecha(fecha: Any) -> Optional[str]:
    """
    Normaliza una fecha a formato ISO (YYYY-MM-DD)

    Args:
        fecha: Fecha en diversos formatos

    Returns:
        Fecha en formato ISO o None si es inválida
    """
    if not fecha or fecha == "N/A":
        return None

    # Si ya es un objeto datetime
    if isinstance(fecha, datetime):
        return fecha.strftime("%Y-%m-%d")

    # Si es string, intentar parsear formatos comunes
    if isinstance(fecha, str):
        formatos = [
            "%Y-%m-%d",           # 2025-01-15
            "%d/%m/%Y",           # 15/01/2025
            "%d-%m-%Y",           # 15-01-2025
            "%Y/%m/%d",           # 2025/01/15
            "%d/%m/%y",           # 15/01/25
        ]

        for formato in formatos:
            try:
                dt = datetime.strptime(fecha.strip(), formato)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return None


def es_biomarcador_positivo(valor: str) -> Optional[bool]:
    """
    Determina si un biomarcador es positivo, negativo o no especificado

    Args:
        valor: Valor del biomarcador

    Returns:
        True si positivo, False si negativo, None si no especificado
    """
    if not valor or valor == "N/A":
        return None

    valor_lower = str(valor).lower().strip()

    positivos = ['positivo', 'positive', '+', 'presente']
    negativos = ['negativo', 'negative', '-', 'ausente']

    if any(p in valor_lower for p in positivos):
        return True
    elif any(n in valor_lower for n in negativos):
        return False
    else:
        return None


def extraer_porcentaje_de_texto(texto: str) -> Optional[float]:
    """
    Extrae porcentaje de un texto (ej: "Ki-67: 15%" -> 15.0)

    Args:
        texto: Texto que contiene porcentaje

    Returns:
        Porcentaje como float o None
    """
    if not texto:
        return None

    # Buscar patrón de porcentaje: número seguido de %
    match = re.search(r'(\d+(?:\.\d+)?)\s*%', texto)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    # Buscar patrón de fracción: número/número (ej: "50/100")
    match = re.search(r'(\d+)/(\d+)', texto)
    if match:
        try:
            numerador = float(match.group(1))
            denominador = float(match.group(2))
            if denominador > 0:
                return (numerador / denominador) * 100
        except ValueError:
            pass

    return None


def detectar_campos_vacios(registro: Dict[str, Any], campos_criticos: List[str]) -> List[str]:
    """
    Detecta campos críticos que están vacíos en un registro

    Args:
        registro: Diccionario con datos del registro
        campos_criticos: Lista de nombres de campos que deben tener valor

    Returns:
        Lista de nombres de campos vacíos
    """
    campos_vacios = []

    for campo in campos_criticos:
        valor = registro.get(campo)
        if not valor or valor == "N/A" or str(valor).strip() == "":
            campos_vacios.append(campo)

    return campos_vacios


def calcular_completitud_registro(registro: Dict[str, Any], total_campos: int) -> float:
    """
    Calcula el porcentaje de completitud de un registro

    Args:
        registro: Diccionario con datos del registro
        total_campos: Total de campos esperados

    Returns:
        Porcentaje de completitud (0-100)
    """
    if total_campos == 0:
        return 0.0

    campos_llenos = sum(
        1 for valor in registro.values()
        if valor and valor != "N/A" and str(valor).strip() != ""
    )

    return (campos_llenos / total_campos) * 100


def comparar_registros(registro1: Dict[str, Any], registro2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compara dos registros y retorna las diferencias

    Args:
        registro1: Primer registro
        registro2: Segundo registro

    Returns:
        Dict con campos diferentes: {campo: (valor1, valor2)}
    """
    diferencias = {}

    # Obtener todos los campos de ambos registros
    todos_campos = set(registro1.keys()) | set(registro2.keys())

    for campo in todos_campos:
        val1 = registro1.get(campo)
        val2 = registro2.get(campo)

        if val1 != val2:
            diferencias[campo] = (val1, val2)

    return diferencias


def generar_resumen_registro(registro: Dict[str, Any]) -> str:
    """
    Genera un resumen legible de un registro

    Args:
        registro: Diccionario con datos del registro

    Returns:
        String con resumen del registro
    """
    numero_peticion = registro.get("Numero de caso", "N/A")
    nombre = registro.get("Primer nombre", "")
    apellido = registro.get("Primer apellido", "")
    edad = registro.get("Edad", "N/A")
    genero = registro.get("Genero", "N/A")
    diagnostico = registro.get("Diagnostico Principal", "N/A")

    resumen = f"Petición: {numero_peticion}\n"
    if nombre or apellido:
        resumen += f"Paciente: {nombre} {apellido}\n"
    resumen += f"Edad/Género: {edad} años, {genero}\n"
    resumen += f"Diagnóstico: {diagnostico[:100]}..."

    return resumen


__all__ = [
    'validar_numero_peticion',
    'validar_campo_requerido',
    'normalizar_genero',
    'validar_edad',
    'normalizar_fecha',
    'es_biomarcador_positivo',
    'extraer_porcentaje_de_texto',
    'detectar_campos_vacios',
    'calcular_completitud_registro',
    'comparar_registros',
    'generar_resumen_registro'
]
