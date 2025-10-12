#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mapeos y diccionarios para procesamiento de datos del paciente

Versión: 5.0.0 - CONSOLIDADO
Migrado desde: config/mapeos/paciente.py
Nota: Toda la configuración de mapeos está ahora en core/utils/ para centralización
"""

# ======================== APELLIDOS Y NOMBRES ========================

# Apellidos comunes en Colombia (para división correcta de nombres)
APELLIDOS_COMUNES = {
    'GOMEZ', 'GÓMEZ', 'MEJIA', 'MEJÍA', 'PEREZ', 'PÉREZ', 'GARCIA', 'GARCÍA',
    'RODRIGUEZ', 'RODRÍGUEZ', 'HERNANDEZ', 'HERNÁNDEZ', 'LOPEZ', 'LÓPEZ',
    'MARTINEZ', 'MARTÍNEZ', 'GONZALEZ', 'GONZÁLEZ', 'RAMIREZ', 'RAMÍREZ',
    'SUAREZ', 'SUÁREZ', 'VARGAS', 'PERALTA', 'CAICEDO', 'ESTRADA', 'ROJAS',
    'RIVERA', 'HENAO', 'CASTRO', 'SALAZAR', 'VALENCIA', 'ORTEGA', 'CORTES',
    'CORTÉS', 'BUELVAS'
}

# Nombres compuestos comunes (para evitar división incorrecta)
NOMBRES_COMPUESTOS_INICIO = {
    'JUAN', 'MARIA', 'MARÍA', 'JOSE', 'JOSÉ', 'LUIS', 'ANA', 'ROSA', 'JUANA'
}

# Nombres que podrían confundirse con apellidos (excluir de morfología)
NOMBRES_EXCLUSION_MORFOLOGIA = {
    'CARLOS', 'HERNAN', 'HERNÁN', 'PAOLA', 'ANYI', 'ARMANDO'
}

# ======================== TIPOS DE DOCUMENTO ========================

# Tipos de documento de identificación en Colombia
TIPOS_DOCUMENTO = {
    'CC': 'Cédula de Ciudadanía',
    'TI': 'Tarjeta de Identidad',
    'CE': 'Cédula de Extranjería',
    'PA': 'Pasaporte',
    'RC': 'Registro Civil',
    'MS': 'Menor Sin Identificación',
    'AS': 'Adulto Sin Identificación',
    'CN': 'Certificado de Nacido Vivo',
    'PE': 'Permiso Especial de Permanencia',
    'PT': 'Permiso de Protección Temporal'
}

# Normalización de tipos de documento (variantes comunes)
TIPOS_DOCUMENTO_NORMALIZACION = {
    'cedula': 'CC',
    'cédula': 'CC',
    'cedula de ciudadania': 'CC',
    'cedula de ciudadanía': 'CC',
    'tarjeta de identidad': 'TI',
    'cedula de extranjeria': 'CE',
    'cédula de extranjería': 'CE',
    'pasaporte': 'PA',
    'registro civil': 'RC',
}

# ======================== NORMALIZACIÓN DE GÉNERO ========================

GENERO_NORMALIZACION = {
    'masculino': 'MASCULINO',
    'femenino': 'FEMENINO',
    'm': 'MASCULINO',
    'f': 'FEMENINO',
    'male': 'MASCULINO',
    'female': 'FEMENINO',
    'hombre': 'MASCULINO',
    'mujer': 'FEMENINO',
}

# ======================== EPS Y ENTIDADES DE SALUD ========================

# Normalización de nombres de EPS (Entidades Promotoras de Salud)
EPS_NORMALIZACION = {
    # Principales EPS
    'nueva eps': 'NUEVA EPS',
    'nueva eps s.a.': 'NUEVA EPS',
    'sura': 'SURA EPS',
    'eps sura': 'SURA EPS',
    'sanitas': 'SANITAS EPS',
    'eps sanitas': 'SANITAS EPS',
    'salud total': 'SALUD TOTAL EPS',
    'eps salud total': 'SALUD TOTAL EPS',
    'comfandi': 'COMFANDI EPS',
    'eps comfandi': 'COMFANDI EPS',
    'coomeva': 'COOMEVA EPS',
    'eps coomeva': 'COOMEVA EPS',
    'compensar': 'COMPENSAR EPS',
    'eps compensar': 'COMPENSAR EPS',

    # Regímenes especiales
    'magisterio': 'FONDO NACIONAL DEL MAGISTERIO',
    'policia': 'POLICIA NACIONAL',
    'policía': 'POLICIA NACIONAL',
    'fuerzas militares': 'FUERZAS MILITARES',
    'ecopetrol': 'ECOPETROL',

    # Subsidiado
    'caprecom': 'CAPRECOM',
    'coosalud': 'COOSALUD',
    'emssanar': 'EMSSANAR',
    'mutual ser': 'MUTUAL SER',
    'asmet salud': 'ASMET SALUD',
    'capital salud': 'CAPITAL SALUD',

    # Casos especiales y variantes
    'sisben': 'SISBEN',
    'vinculado': 'VINCULADO',
    'no afiliado': 'NO AFILIADO',
    'particular': 'PARTICULAR',
    'extranjero': 'EXTRANJERO',

    # Abreviaciones comunes
    'eps': 'EPS NO ESPECIFICADA',
    'sin eps': 'SIN EPS',
    'no tiene': 'SIN EPS',
}

# ======================== SERVICIOS HOSPITALARIOS ========================

# Servicios médicos del Hospital Universitario del Valle
SERVICIOS_HUV = {
    'CIRUGIA GENERAL': 'CIRUGÍA GENERAL',
    'CIRUGIA PLASTICA': 'CIRUGÍA PLÁSTICA',
    'CIRUGIA VASCULAR': 'CIRUGÍA VASCULAR',
    'GINECOLOGIA': 'GINECOLOGÍA',
    'OBSTETRICIA': 'OBSTETRICIA',
    'MEDICINA INTERNA': 'MEDICINA INTERNA',
    'NEUROLOGIA': 'NEUROLOGÍA',
    'CARDIOLOGIA': 'CARDIOLOGÍA',
    'ONCOLOGIA': 'ONCOLOGÍA',
    'HEMATOLOGIA': 'HEMATOLOGÍA',
    'PEDIATRIA': 'PEDIATRÍA',
    'NEONATOLOGIA': 'NEONATOLOGÍA',
    'UCI': 'UNIDAD DE CUIDADOS INTENSIVOS',
    'URGENCIAS': 'URGENCIAS',
    'PATOLOGIA': 'PATOLOGÍA',
    'ANESTESIA': 'ANESTESIOLOGÍA',
    'RADIOLOGIA': 'RADIOLOGÍA',
    'LABORATORIO': 'LABORATORIO CLÍNICO',
}

# ======================== CORRECCIÓN UTF-8 ========================

# Mapeo para corregir caracteres mal codificados (artefactos OCR)
BROKEN_UTF_MAP = {
    # Vocales con tildes
    'Ã"': 'Ó', 'Ã‰': 'É', 'Ãš': 'Ú', 'Ã': 'Á', 'Ã': 'Í',
    'Ã±': 'ñ', 'Ã¡': 'á', 'Ã©': 'é', 'Ã­': 'í', 'Ã³': 'ó', 'Ãº': 'ú',

    # Caracteres especiales
    '\u2013': '-', '\u2014': '-', '\u2015': '-', '\u201c': '"', '\u201d': '"',
    '\u2018': "'", '\u2019': "'", '\u00b4': "'", '\u00a8': '', '\u00ba': 'º', '\u00aa': 'ª',

    # Otros caracteres problemáticos
    '\ufffd': '', '\u2022': '•', '\u203a': '›', '\u2039': '‹',
}

# ======================== ESPECIALIDADES MÉDICAS ========================

# Especialidades por servicio (para médicos tratantes)
ESPECIALIDADES_POR_SERVICIO = {
    'UCI': 'MÉDICO INTENSIVISTA',
    'URGENCIAS': 'MÉDICO DE URGENCIAS',
    'CIRUGIA GENERAL': 'CIRUJANO GENERAL',
    'GINECOLOGIA': 'GINECÓLOGO',
    'OBSTETRICIA': 'OBSTETRA',
    'MEDICINA INTERNA': 'INTERNISTA',
    'NEUROLOGIA': 'NEURÓLOGO',
    'CARDIOLOGIA': 'CARDIÓLOGO',
    'ONCOLOGIA': 'ONCÓLOGO',
    'HEMATOLOGIA': 'HEMATÓLOGO',
    'PEDIATRIA': 'PEDIATRA',
    'NEONATOLOGIA': 'NEONATÓLOGO',
    'PATOLOGIA': 'PATÓLOGO',
    'ANESTESIA': 'ANESTESIÓLOGO',
    'RADIOLOGIA': 'RADIÓLOGO',
}

# ======================== FUNCIONES DE NORMALIZACIÓN ========================

def get_apellidos_comunes():
    """Retorna set de apellidos comunes"""
    return APELLIDOS_COMUNES

def get_nombres_compuestos():
    """Retorna set de nombres compuestos"""
    return NOMBRES_COMPUESTOS_INICIO

def normalize_eps(eps_text: str) -> str:
    """Normaliza nombre de EPS"""
    if not eps_text:
        return 'SIN EPS'

    eps_clean = eps_text.strip().lower()
    return EPS_NORMALIZACION.get(eps_clean, eps_text.upper())

def normalize_genero(genero_text: str) -> str:
    """Normaliza género"""
    if not genero_text:
        return 'NO ESPECIFICADO'

    genero_clean = genero_text.strip().lower()
    return GENERO_NORMALIZACION.get(genero_clean, genero_text.upper())

def normalize_tipo_documento(tipo_text: str) -> str:
    """Normaliza tipo de documento"""
    if not tipo_text:
        return 'CC'  # Default

    tipo_clean = tipo_text.strip().lower()
    return TIPOS_DOCUMENTO_NORMALIZACION.get(tipo_clean, tipo_text.upper())
