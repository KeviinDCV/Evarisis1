#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extractor de datos del paciente

Extrae información demográfica y administrativa del paciente con configuración integrada.

Versión: 4.2.0 - Refinamiento de patrones multi-línea y formato de datos
Migrado de: core/procesador_ihq.py, config/patterns/patient_patterns.py
Nota: Toda la configuración de patrones está ahora en este archivo para centralización
"""

import re
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Agregar path del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar utilidades
from core.utils.name_splitter import split_full_name, validate_name_split
from core.utils.date_processor import (
    parse_date,
    parse_age_text,
    calculate_birth_date,
    format_age,
    validate_date
)
from core.utils.utf8_fixer import clean_text_comprehensive

# ======================== PATRONES DE EXTRACCIÓN ========================
# Movido desde: config/patterns/patient_patterns.py

PATIENT_PATTERNS = {
    # Datos de identificación básicos
    'nombre_completo': {
        'descripcion': 'Nombre completo del paciente',
        'patrones': [
            r'Nombre\s*:\s*([A-ZÁÉÍÓÚÜÑ\s]+?)(?=\s*N\.\s*petici[óo]n|$)',
        ],
        'ejemplo': 'Nombre: DIEGO HERNAN RUIZ IMBACHI'
    },

    'numero_peticion': {
        'descripcion': 'Número de petición del estudio (ej: IHQ250001)',
        'patrones': [
            r'N\.\s*peticion\s*(?:[:\-])\s*([A-Z0-9\-]+)',
        ],
        'ejemplo': 'N. peticion: IHQ250001'
    },

    'identificacion_completa': {
        'descripcion': 'Número de identificación con tipo de documento',
        'patrones': [
            r'N\.Identificación\s*:\s*([A-Z]{1,3}\.?\s*[0-9\.]+)',
            r'N\.Identificaci[óo]n\s*:\s*([A-Z]{1,3}\.?\s*[0-9\.]+)',
        ],
        'ejemplo': 'N.Identificación: CC. 94123456'
    },

    'identificacion_numero': {
        'descripcion': 'Solo el número de identificación (sin tipo)',
        'patrones': [
            r'N\.Identificación\s*:\s*[A-Z]{1,3}\.?\s*([0-9]+)',
            r'N\.Identificaci[óo]n\s*:\s*[A-Z]{1,3}\.?\s*([0-9]+)',
        ],
        'ejemplo': 'N.Identificación: CC. 94123456 → 94123456'
    },

    'tipo_documento': {
        'descripcion': 'Tipo de documento (CC, TI, CE, etc.)',
        'patrones': [
            r'N\.Identificación\s*:\s*([A-Z]{1,3})\.?',
            r'N\.Identificaci[óo]n\s*:\s*([A-Z]{1,3})\.?',
        ],
        'valores_posibles': ['CC', 'TI', 'CE', 'PA', 'RC', 'MS', 'AS'],
        'ejemplo': 'N.Identificación: CC. 94123456 → CC'
    },

    # Datos demográficos
    'genero': {
        'descripcion': 'Género del paciente',
        'patrones': [
            r'Genero\s*:\s*([A-Z]+)',
            r'G[ée]nero\s*:\s*([A-Z]+)',
        ],
        'valores_posibles': ['MASCULINO', 'FEMENINO', 'M', 'F'],
        'normalizacion': {
            'm': 'MASCULINO',
            'f': 'FEMENINO',
            'masculino': 'MASCULINO',
            'femenino': 'FEMENINO',
        },
        'ejemplo': 'Genero: MASCULINO'
    },

    'edad': {
        'descripcion': 'Edad del paciente (solo años como número)',
        'patrones': [
            r'Edad\s*:\s*([0-9]+)\s+[a-záéíóúñ]+',  # Captura solo el número de años
        ],
        'post_process': lambda x: re.search(r'(\d+)', x).group(1) if re.search(r'(\d+)', x) else x,
        'ejemplo': 'Edad: 45 años 3 meses 12 días'
    },

    # EPS e información de salud
    'eps': {
        'descripcion': 'Entidad Promotora de Salud (puede estar en varias líneas)',
        'patrones': [
            # Patrón 1: Capturar EPS en múltiples líneas (incluyendo SALUD N4)
            r'EPS\s*:\s*([A-ZÁÉÍÓÚÑ\s\.0-9]+?)(?:\s*\n\s*([A-ZÁÉÍÓÚÑ\s0-9]+?))?(?=\s*\n?\s*M[Éé]dico\s+tratante|\s*\n?\s*Servicio|$)',
            # Patrón 2: Captura todo hasta Médico tratante o Servicio
            r'EPS\s*:\s*([^\n]+?)(?:\s*\n\s*([^\n]+?))?(?=\s*\n\s*(?:Médico|M[ée]dico|Servicio))',
            # Patrón 3: Fallback simple
            r'EPS\s*:\s*([A-ZÁÉÍÓÚÑ\s\.0-9]+)',
        ],
        'ejemplo': 'EPS: REGIONAL EN ASEGURAMIENTO DE\nSALUD N4',
        'multilínea': True,
        'concatenar_grupos': True
    },

    # Información médica
    'medico_tratante': {
        'descripcion': 'Nombre del médico tratante',
        'patrones': [
            r'Médico tratante\s*[:\-—]*\s*:\s*([A-ZÁÉÍÓÚÜÑ\s]+?)(?:\s*Servicio|\s*Fecha Ingreso|$)',
        ],
        'ejemplo': 'Médico tratante: JUAN PEREZ'
    },

    'servicio': {
        'descripcion': 'Servicio hospitalario (UCI, Ginecología, etc.)',
        'patrones': [
            r'SERVICIO\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,30}?)(?:\s+FECHA|\s+Fecha|$)',
            r'Servicio\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,30}?)(?:\s+FECHA|\s+Fecha|$)',
        ],
        'ejemplo': 'Servicio: CIRUGIA GENERAL → CIRUGIA GENERAL'
    },

    # Fechas
    'fecha_ingreso': {
        'descripcion': 'Fecha de ingreso del paciente',
        'patrones': [
            r'Fecha Ingreso[^\d/]*(\d{2}/\d{2}/\d{4})',
        ],
        'formato': 'DD/MM/YYYY',
        'ejemplo': 'Fecha Ingreso: 15/01/2025'
    },

    'fecha_informe': {
        'descripcion': 'Fecha del informe',
        'patrones': [
            r'Fecha Informe[^\d/]*(\d{2}/\d{2}/\d{4})',
        ],
        'formato': 'DD/MM/YYYY',
        'ejemplo': 'Fecha Informe: 16/01/2025'
    },

    'fecha_autopsia': {
        'descripcion': 'Fecha de autopsia (solo para autopsias)',
        'patrones': [
            r'Fecha y hora de la autopsia:\s*(\d{2}/\d{2}/\d{4})',
        ],
        'formato': 'DD/MM/YYYY',
        'ejemplo': 'Fecha y hora de la autopsia: 16/01/2025'
    },

    'fecha_toma': {
        'descripcion': 'Fecha de toma de muestra',
        'patrones': [
            r'Fecha toma\s*:\s*(\d{4}-\d{2}-\d{2})',
        ],
        'formato': 'YYYY-MM-DD',
        'ejemplo': 'Fecha toma: 2025-01-15'
    },

    # Información adicional
    'certificado_defuncion': {
        'descripcion': 'Número de certificado de defunción (solo autopsias)',
        'patrones': [
            r'No\.\s*Certificado\s*de\s*defunción\s*([0-9]+)',
        ],
        'ejemplo': 'No. Certificado de defunción: 12345'
    },

    # Responsables
    'responsable_analisis': {
        'descripcion': 'Nombre del responsable del análisis',
        'patrones': [
            r'([A-ZÁÉÍÓÚÑ\s]+)\s*\n\s*Responsable del análisis',
        ],
        'ejemplo': 'ARMANDO CORTES BUELVAS\nResponsable del análisis'
    },

    'usuario_finalizacion': {
        'descripcion': 'Usuario que finalizó el informe con timestamp',
        'patrones': [
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}),\s*([A-ZÁÉÍÓÚÑ\s]+)',
        ],
        'ejemplo': '2025-01-16 14:30:00, JUAN PEREZ'
    },

    # Identificadores únicos
    'identificador_unico': {
        'descripcion': 'Identificador único del sistema',
        'patrones': [
            r'Identificador Unico[^:]*:\s*(\d+)',
        ],
        'ejemplo': 'Identificador Unico: 123456789'
    },

    # ELIMINADO v4.2: numero_autorizacion - campo no utilizado
    # 'numero_autorizacion': {
    #     'descripcion': 'Número de autorización',
    #     'patrones': [
    #         r'N\.\s*Autorizacion[^:]*:\s*([A-Z0-9]+)',
    #     ],
    #     'ejemplo': 'N. Autorizacion: AUT123456'
    # },

    # Campos específicos de IHQ
    'organo': {
        'descripcion': 'Órgano o sitio anatómico del estudio (de tabla)',
        'patrones': [
            # Patrón 1: Órgano multilínea que termina con "+" o "BX DE" o "DE" (ej: "BX DE PLEURA + BX DE\nPULMON")
            r'(?:Bloques y laminas|Tejido en fresco)\s+([A-ZÁÉÍÓÚÑ][^\n]*(?:\+|BX\s+DE|DE)\s*)\n\s*([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s0-9]+?)(?=\s*(?:\n|INFORME|DESCRIPCI))',
            # Patrón 2: TUMOR REGION/REGIÓON seguido de INTRADURAL en siguiente línea
            r'(?:Bloques y laminas|Tejido en fresco)\s+(TUMOR\s+REGI[OÓ]O?N)\s*\n\s*(INTRADURAL)',
            # Patrón 3: Captura solo TUMOR REGION cuando no puede capturar INTRADURAL
            r'(?:Bloques y laminas|Tejido en fresco)\s+(TUMOR\s+REGI[OÓ]O?N)',
            # Patrón 4: Órgano completo en una sola línea
            r'(?:Bloques y laminas|Tejido en fresco)\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s0-9+]*?)(?:\s*$|\s*\n)',
        ],
        'ejemplo': 'Bloques y laminas  BX DE PLEURA + BX DE\nPULMON',
        'multilínea': True,
        'concatenar_grupos': True,
        'post_process': lambda x: x.replace('REGIÓON', 'REGION').replace('REGIÓN', 'REGION').strip()
    },

    'procedimiento': {
        'descripcion': 'Tipo de procedimiento (CIRUGÍA o BIOPSIA)',
        'patrones': [
            r'(?i)(Resección|Reseccion|Extirpación|Extirpacion|Exéresis|Exeresis|Hemicolectomía|Hemicolectomia|Gastrectomía|Gastrectomia|Mastectomía|Mastectomia|Nefrectomía|Nefrectomia|Colectomía|Colectomia|Sigmoidectomía|Sigmoidectomia|Cuadrantectomía|Cuadrantectomia)',
            r'(?i)(Biopsia|BX)',
        ],
        'normalizacion': {
            'resección': 'CIRUGÍA',
            'reseccion': 'CIRUGÍA',
            'extirpación': 'CIRUGÍA',
            'extirpacion': 'CIRUGÍA',
            'exéresis': 'CIRUGÍA',
            'exeresis': 'CIRUGÍA',
            'hemicolectomía': 'CIRUGÍA',
            'hemicolectomia': 'CIRUGÍA',
            'gastrectomía': 'CIRUGÍA',
            'gastrectomia': 'CIRUGÍA',
            'mastectomía': 'CIRUGÍA',
            'mastectomia': 'CIRUGÍA',
            'nefrectomía': 'CIRUGÍA',
            'nefrectomia': 'CIRUGÍA',
            'colectomía': 'CIRUGÍA',
            'colectomia': 'CIRUGÍA',
            'sigmoidectomía': 'CIRUGÍA',
            'sigmoidectomia': 'CIRUGÍA',
            'cuadrantectomía': 'CIRUGÍA',
            'cuadrantectomia': 'CIRUGÍA',
            'biopsia': 'BIOPSIA',
            'bx': 'BIOPSIA',
        },
        'ejemplo': 'Resección → CIRUGÍA, Biopsia → BIOPSIA'
    },
}

# Categorías de patrones
PATIENT_PATTERN_CATEGORIES = {
    'identificacion': [
        'nombre_completo',
        'numero_peticion',
        'identificacion_completa',
        'identificacion_numero',
        'tipo_documento',
    ],
    'demograficos': [
        'genero',
        'edad',
    ],
    'salud': [
        'eps',
        'medico_tratante',
        'servicio',
    ],
    'fechas': [
        'fecha_ingreso',
        'fecha_informe',
        'fecha_autopsia',
        'fecha_toma',
    ],
    'administrativos': [
        'certificado_defuncion',
        'responsable_analisis',
        'usuario_finalizacion',
        'identificador_unico',
        'numero_autorizacion',
    ],
}


def get_patient_field_info(field_name: str):
    """Retorna información de un campo específico"""
    return PATIENT_PATTERNS.get(field_name.lower(), None)


# Importar funciones de normalización desde core/utils/patient_mappings.py
from core.utils.patient_mappings import (
    normalize_eps,
    normalize_genero,
    normalize_tipo_documento
)


def extract_patient_data(text: str) -> Dict[str, Any]:
    """Extrae todos los datos del paciente del texto
    
    Args:
        text: Texto del informe médico
        
    Returns:
        Diccionario con datos del paciente extraídos
    """
    if not text:
        return {}

    # CORREGIDO: clean_text_comprehensive rompe los patrones, usar texto original
    clean_text = text  # clean_text_comprehensive(text)

    results = {}
    
    # Extraer todos los campos configurados
    for field_name, field_config in PATIENT_PATTERNS.items():
        value = extract_single_field(clean_text, field_name, field_config)
        if value:
            results[field_name] = value
    
    # Post-procesamiento y normalización
    results = normalize_patient_data(results)
    
    # Procesamiento especial para nombres
    if 'nombre_completo' in results:
        name_data = process_patient_name(results['nombre_completo'])
        results.update(name_data)
    
    # Procesamiento especial para fechas y edad
    if 'edad' in results and 'fecha_ingreso' in results:
        birth_data = process_patient_birth_date(results['edad'], results['fecha_ingreso'])
        results.update(birth_data)
    
    return results


def extract_single_field(text: str, field_name: str, field_config: Dict[str, Any]) -> Optional[str]:
    """Extrae un campo específico del texto

    Args:
        text: Texto del informe
        field_name: Nombre del campo a extraer
        field_config: Configuración del campo

    Returns:
        Valor extraído o None si no se encuentra
    """
    if not text or not field_config.get('patrones'):
        return None

    # Probar cada patrón configurado
    for pattern in field_config['patrones']:
        try:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)

            if match:
                # Si hay flag de concatenar_grupos y hay múltiples grupos, concatenarlos
                if field_config.get('concatenar_grupos') and len(match.groups()) > 1:
                    # Concatenar todos los grupos capturados con espacio
                    parts = [g.strip() for g in match.groups() if g]
                    value = ' '.join(parts)
                else:
                    # Tomar el primer grupo capturado
                    value = match.group(1).strip() if match.groups() else match.group(0).strip()

                # Limpiar valor extraído
                value = clean_extracted_value(value)

                # Aplicar post_process si existe
                if value and 'post_process' in field_config:
                    value = field_config['post_process'](value)

                if value:
                    return value
        except (re.error, AttributeError, IndexError):
            continue

    return None


def clean_extracted_value(value: str) -> str:
    """Limpia valor extraído de artefactos comunes
    
    Args:
        value: Valor extraído sin procesar
        
    Returns:
        Valor limpio
    """
    if not value:
        return ''
    
    # Limpiar UTF-8 y normalizar
    cleaned = clean_text_comprehensive(value)
    
    # Eliminar caracteres extraños al final
    cleaned = re.sub(r'[^\w\s\./\-:,áéíóúüñÁÉÍÓÚÜÑ]+$', '', cleaned)
    
    # Normalizar espacios múltiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned


def normalize_patient_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Normaliza datos extraídos usando mapeos de configuración

    Args:
        raw_data: Datos sin normalizar

    Returns:
        Datos normalizados
    """
    normalized = raw_data.copy()

    # Normalizar género
    if 'genero' in normalized:
        normalized['genero'] = normalize_genero(normalized['genero'])

    # Normalizar EPS
    if 'eps' in normalized:
        normalized['eps'] = normalize_eps(normalized['eps'])

    # Normalizar tipo de documento
    if 'tipo_documento' in normalized:
        normalized['tipo_documento'] = normalize_tipo_documento(normalized['tipo_documento'])

    # Limpiar y normalizar identificación
    if 'identificacion_numero' in normalized:
        # Eliminar puntos y espacios de números de identificación
        id_num = normalized['identificacion_numero']
        id_clean = re.sub(r'[^\d]', '', id_num)
        normalized['identificacion_numero'] = id_clean

    # Normalizar procedimiento usando configuración de patrón
    if 'procedimiento' in normalized:
        proc_value = normalized['procedimiento'].lower()
        proc_config = PATIENT_PATTERNS.get('procedimiento', {})
        normalizacion_map = proc_config.get('normalizacion', {})

        # Buscar normalización en el mapa
        normalized['procedimiento'] = normalizacion_map.get(proc_value, normalized['procedimiento'])

    return normalized


def process_patient_name(nombre_completo: str) -> Dict[str, Any]:
    """Procesa nombre completo del paciente
    
    Args:
        nombre_completo: Nombre completo extraído
        
    Returns:
        Diccionario con nombres procesados
    """
    if not nombre_completo:
        return {}
    
    # Dividir nombre usando utilidad especializada
    name_split = split_full_name(nombre_completo)
    
    # Validar división
    validation = validate_name_split(
        nombre_completo, 
        name_split['nombres'], 
        name_split['apellidos']
    )
    
    result = {
        'nombres': name_split['nombres'],
        'apellidos': name_split['apellidos'],
        'nombre_formal': f"{name_split['apellidos']}, {name_split['nombres']}" if name_split['apellidos'] else name_split['nombres'],
        'nombre_division_valida': validation['is_valid'],
        'nombre_confianza': validation['confidence'],
    }
    
    # Agregar advertencias si las hay
    if validation['warnings']:
        result['nombre_advertencias'] = validation['warnings']
    
    return result


def process_patient_birth_date(edad_texto: str, fecha_referencia: str) -> Dict[str, Any]:
    """Procesa fecha de nacimiento basada en edad y fecha de referencia
    
    Args:
        edad_texto: Texto con edad del paciente
        fecha_referencia: Fecha de ingreso o informe
        
    Returns:
        Diccionario con datos de fecha de nacimiento
    """
    if not edad_texto:
        return {}
    
    result = {}
    
    # Parsear edad
    age_parts = parse_age_text(edad_texto)
    result['edad_años'] = age_parts['años']
    result['edad_meses'] = age_parts['meses']
    result['edad_días'] = age_parts['días']
    result['edad_formateada'] = format_age(age_parts['años'], age_parts['meses'], age_parts['días'])
    
    # Calcular fecha de nacimiento si tenemos fecha de referencia
    if fecha_referencia:
        birth_date = calculate_birth_date(fecha_referencia, edad_texto)
        if birth_date:
            result['fecha_nacimiento_calculada'] = birth_date.strftime('%d/%m/%Y')
            
            # Validar fecha de nacimiento
            validation = validate_date(birth_date)
            result['fecha_nacimiento_valida'] = validation['is_valid']
            if validation['warnings']:
                result['fecha_nacimiento_advertencias'] = validation['warnings']
    
    return result


def get_patient_summary(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Genera resumen del paciente extraído
    
    Args:
        patient_data: Datos del paciente
        
    Returns:
        Resumen con datos principales
    """
    summary = {}
    
    # Datos de identificación
    summary['identificacion'] = {
        'nombre_completo': patient_data.get('nombre_completo', ''),
        'tipo_documento': patient_data.get('tipo_documento', ''),
        'numero_identificacion': patient_data.get('identificacion_numero', ''),
        'numero_peticion': patient_data.get('numero_peticion', ''),
    }
    
    # Datos demográficos
    summary['demograficos'] = {
        'edad': patient_data.get('edad_formateada', patient_data.get('edad', '')),
        'genero': patient_data.get('genero', ''),
        'fecha_nacimiento': patient_data.get('fecha_nacimiento_calculada', ''),
    }
    
    # Datos de salud
    summary['salud'] = {
        'eps': patient_data.get('eps', ''),
        'medico_tratante': patient_data.get('medico_tratante', ''),
        'servicio': patient_data.get('servicio', ''),
    }
    
    # Fechas importantes
    summary['fechas'] = {
        'fecha_ingreso': patient_data.get('fecha_ingreso', ''),
        'fecha_informe': patient_data.get('fecha_informe', ''),
        'fecha_toma': patient_data.get('fecha_toma', ''),
    }
    
    return summary


def validate_patient_data(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """Valida datos del paciente extraídos
    
    Args:
        patient_data: Datos del paciente
        
    Returns:
        Diccionario con validación
    """
    warnings = []
    errors = []
    confidence = 1.0
    
    # Validar campos requeridos
    required_fields = ['nombre_completo', 'identificacion_numero']
    for field in required_fields:
        if not patient_data.get(field):
            errors.append(f"Campo requerido faltante: {field}")
            confidence -= 0.3
    
    # Validar formato de identificación
    if 'identificacion_numero' in patient_data:
        id_num = patient_data['identificacion_numero']
        if not re.match(r'^\d{6,12}$', id_num):
            warnings.append(f"Formato de identificación inusual: {id_num}")
            confidence -= 0.1
    
    # Validar edad razonable
    if 'edad_años' in patient_data:
        edad = patient_data['edad_años']
        if edad < 0 or edad > 120:
            warnings.append(f"Edad inusual: {edad} años")
            confidence -= 0.2
    
    # Validar nombre tiene apellidos
    if not patient_data.get('apellidos'):
        warnings.append("No se pudieron extraer apellidos")
        confidence -= 0.1
    
    is_valid = len(errors) == 0 and confidence >= 0.5
    
    return {
        'is_valid': is_valid,
        'confidence': max(0.0, confidence),
        'warnings': warnings,
        'errors': errors,
        'required_fields_complete': len(errors) == 0,
    }


def get_missing_fields(patient_data: Dict[str, Any]) -> List[str]:
    """Identifica campos faltantes en los datos del paciente
    
    Args:
        patient_data: Datos extraídos
        
    Returns:
        Lista de campos faltantes importantes
    """
    important_fields = [
        'nombre_completo', 'identificacion_numero', 'tipo_documento',
        'genero', 'edad', 'eps', 'fecha_ingreso'
    ]
    
    missing = []
    for field in important_fields:
        if not patient_data.get(field):
            missing.append(field)
    
    return missing


# ======================== UTILIDADES DE TESTING ========================

def test_patient_extractor():
    """Función de prueba para validar el extractor de paciente"""
    print("=== Test del Extractor de Paciente ===")
    
    # Ejemplo de texto de informe
    sample_text = """
    Nombre: DIEGO HERNAN RUIZ IMBACHI
    N. peticion: IHQ250001
    N.Identificación: CC. 94123456
    Genero: MASCULINO
    Edad: 45 años 3 meses 12 días
    EPS: NUEVA EPS
    Médico tratante: DR. JUAN PEREZ
    Servicio: CIRUGIA GENERAL
    Fecha Ingreso: 15/01/2025
    Fecha Informe: 16/01/2025
    """
    
    print("Texto de prueba:")
    print(sample_text)
    print("\n" + "="*50)
    
    # Extraer datos
    patient_data = extract_patient_data(sample_text)
    
    print("\nDatos extraídos:")
    for key, value in patient_data.items():
        print(f"  {key}: {value}")
    
    # Generar resumen
    summary = get_patient_summary(patient_data)
    print(f"\nResumen:")
    for category, data in summary.items():
        print(f"  {category.upper()}:")
        for key, value in data.items():
            print(f"    {key}: {value}")
    
    # Validar datos
    validation = validate_patient_data(patient_data)
    print(f"\nValidación:")
    print(f"  Válido: {validation['is_valid']}")
    print(f"  Confianza: {validation['confidence']:.2f}")
    if validation['warnings']:
        print(f"  Advertencias: {validation['warnings']}")
    if validation['errors']:
        print(f"  Errores: {validation['errors']}")


if __name__ == "__main__":
    test_patient_extractor()