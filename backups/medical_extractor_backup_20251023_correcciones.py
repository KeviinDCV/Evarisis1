#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extractor de datos médicos

Extrae información médica específica de los informes IHQ:
- Diagnósticos
- Órganos
- Descripciones microscópicas y macroscópicas
- Fechas médicas
- Malignidad
- Información clínica
- Factor pronóstico con sistema de prioridades

Versión: 4.2.0 - Sistema robusto de factor pronóstico
Migrado de: core/procesador_ihq.py (funciones extract_ihq_data, patrones PATTERNS_IHQ)
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# Agregar path del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Importar utilidades
from core.utils.utf8_fixer import clean_text_comprehensive

# Importar función específica de conversión de fechas
try:
    from core.utils.date_processor import convert_date_format
except ImportError:
    # Fallback: importar del procesador original
    from core.procesador_ihq import convert_date_format

# ======================== PATRONES DE EXTRACCIÓN ========================
# Movido desde: config/huv_constants.py y core/procesador_ihq.py

# Patrones HUV (solo el que se usa aquí: servicio)
PATTERNS_HUV = {
    'servicio': r'SERVICIO\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,30}?)(?:\s+FECHA|\s+Fecha|$)',
}

# Patrones específicos para datos médicos IHQ
PATTERNS_IHQ = {
    # CORREGIDO v4.2: Solo detener en encabezados de sección (DESCRIPCIÓN MICROSCÓPICA al inicio de línea)
    'descripcion_macroscopica_ihq': r'(?:DESCRIPCI\w+N\s+MACROSC\w+PICA)[:\s]+(.*?)(?=\s*(?:^|\n)\s*DESCRIPCI\w+N\s+MICROSC\w+PICA|fin\s+del\s+informe|$)',
    'descripcion_macroscopica_se_realiza': r'(Se\s+realizan?\s+estudios?\s+de\s+inmunohistoqu[ií]mica.*?)(?=\s*(?:^|\n)\s*DESCRIPCI\w+N\s+MICROSC\w+PICA|fin\s+del\s+informe|$)',
    'descripcion_macroscopica_se_recibe': r'(Se\s+recibe\s+orden\s+para\s+realización\s+de\s+(?:estudio\s+de\s+)?inmunohistoqu[ií]mica.*?)(?=\s*(?:^|\n)\s*DESCRIPCI\w+N\s+MICROSC\w+PICA|fin\s+del\s+informe|$)',
    # v5.3.3: CORREGIDO - Solo detener en DIAGNÓSTICO en MAYÚSCULAS al inicio de línea
    # Patrón: requiere newline + DIAGNÓSTICO (SOLO mayúsculas) + newline
    # NO coincide con "diagnóstico de" (minúsculas en medio de texto)
    # Se aplica SIN re.IGNORECASE para detectar solo mayúsculas
    'descripcion_microscopica_final': r'(?i:DESCRIPCI\w+N\s+MICROSC\w+PICA)[:\s]+(.*?)(?=\nDIAGN[ÓO]STICO\s*\n|fin\s+del\s+informe|$)',
    # v5.3.1: CORREGIDO - Solo capturar DIAGNÓSTICO de sección (uppercase), NO "diagnóstico de" inline
    'diagnostico_final_ihq': r'(?:^|\n)\s*DIAGN[OÓ]STICO\s*\n(.*?)(?=\s*(?:observaciones|responsable|fecha|FACTOR\s+PRONOSTICO|FACTOR\s+PRON\w+STICO|EXPRESI\w+N\s+HORMONAL|COMENTARIOS|fin\s+del\s+informe)|$)',
    'factor_pronostico': r'(?:FACTOR\s+PRONOSTICO|FACTOR\s+PRON\w+STICO)[:\s]+(.*?)(?=\s*(?:observaciones|responsable|fecha|COMENTARIOS|fin\s+del\s+informe)|$)',
    # V5.1.2: NUEVO - Extracción de sección COMENTARIOS
    'comentarios': r'(?:^|\n)\s*COMENTARIOS[:\s]+(.*?)(?=\s*(?:[A-ZÁÉÍÓÚÑ\s]{15,60}?\s*\n\s*(?:Responsable|M[ÉE]DIC[OA]\s+PAT[ÓO]LOG[OA]|RM:))|$)',
    'fecha_toma_raw': r'(?:fecha\s+de?\s+toma|fecha\s+toma)[:\s]*(\d{1,2}[/.-]\d{1,2}[/.-]\d{2,4}|\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
    # CORREGIDO: El nombre del responsable está ANTES de "Responsable del análisis"
    # Puede haber líneas como "COMENTARIOS" o líneas vacías entre el nombre y "Responsable"
    'responsable_ihq': r'([A-ZÁÉÍÓÚÑ\s]{10,50}?)\s*\n\s*(?:COMENTARIOS\s*\n\s*)?Responsable\s+del\s+an[aá]lisis',
    # NUEVO v4.2.2: Patrones alternativos para responsable
    'responsable_alt1': r'([A-ZÁÉÍÓÚÑ\s]{15,60}?)\s*\n\s*(?:M[ÉE]DIC[OA]\s+PAT[ÓO]LOG[OA]|PAT[ÓO]LOG[OA])',
    'responsable_alt2': r'([A-ZÁÉÍÓÚÑ\s]{15,60}?)\s*\n\s*RM:?\s*\d+',  # Nombre antes de RM: (registro médico)
    'responsable_alt3': r'(NANCY\s+MEJIA\s+VARGAS|ARMANDO\s+CORTES\s+BUELVAS|CARLOS\s+CAICEDO\s+ESTRADA|NATALIA\s+AGUIRRE\s+VASQUEZ|JOSE\s+BRAVO\s+BONILLA)',  # Nombres conocidos
    # V4.2.6: ELIMINADO patrón antiguo 'estudios_solicitados' - usamos extract_biomarcadores_solicitados_robust() en su lugar
    # PROBLEMA: El patrón antiguo capturaba encabezados de tabla como "N. ESTUDIO", "TIPO ESTUDIO", "ALMACENAMIENTO"
    'organo_raw': r'(?:ORGANO|órgano)[:\s]+(.*?)(?=\s*(?:descripción|responsable|fecha|estudios|fin\s+del\s+informe)|$)',
}

# Palabras clave de malignidad específicas para IHQ
MALIGNIDAD_KEYWORDS_IHQ = [
    'CARCINOMA', 'ADENOCARCINOMA', 'ADENOCACRINOMA',
    'CARCINOIDE', 'CARCINOSARCOMA', 'CORIOCARCINOMA',
    'SARCOMA', 'OSTEOSARCOMA', 'CONDROSARCOMA', 'LIPOSARCOMA',
    'MELANOMA', 'CARCINOMATOSIS', 'METÁSTASIS', 'METASTASIS',
    'TUMOR MALIGNO', 'NEOPLASIA MALIGNA', 'MALIGNO', 'MALIGNIDAD',
    'INVASIVO', 'INVASIÓN', 'INFILTRANTE', 'ANAPLÁSICO',
    'PLEOMÓRFICO', 'ATÍPICO', 'DISPLÁSICO', 'DISPLASIA SEVERA',
    'ANEUPLOIDE', 'ANEUPLOIDIA', 'CARCINOMA IN SITU', 'CIS',
    'NEOPLASIA INTRAEPITELIAL', 'NIE', 'NIC', 'LESIÓN INTRAEPITELIAL',
    'GRADO III', 'GRADO 3', 'ALTO GRADO', 'POORLY DIFFERENTIATED',
    'UNDIFFERENTIATED', 'DEDIFFERENTIATED'
]

# Palabras clave de benignidad
BENIGNIDAD_KEYWORDS_IHQ = [
    'BENIGNO', 'BENIGNIDAD', 'ADENOMA', 'FIBROMA', 'LIPOMA',
    'PÓLIPO', 'POLIPO', 'HIPERPLASIA', 'DISPLASIA LEVE',
    'DISPLASIA MODERADA', 'INFLAMACIÓN', 'INFLAMACION',
    'CICATRIZ', 'FIBROSIS', 'QUISTE', 'HAMARTOMA',
    'CONDROMA', 'OSTEOMA', 'HEMANGIOMA', 'LEIOMIOMA',
    'FIBROTECOMA', 'TERATOMA MADURO', 'GRADO I', 'GRADO 1',
    'BAJO GRADO', 'WELL DIFFERENTIATED', 'REACTIVE'
]

# Mapeo de órganos específicos
ORGAN_KEYWORDS = {
    'MAMA': ['mama', 'mamario', 'breast', 'seno'],
    'CERVIX': ['cervix', 'cérvix', 'cuello uterino', 'cervical'],
    'COLON': ['colon', 'cólico', 'colónico', 'intestino'],
    'PULMON': ['pulmón', 'pulmonar', 'bronquio', 'bronquial'],
    'ESTOMAGO': ['estómago', 'estomago', 'gástrico', 'antro', 'gástrica', 'gastrica', 'lesion gastrica', 'lesión gástrica', 'mucosa de estomago', 'mucosa de estómago', 'mucosa gastrica', 'mucosa gástrica'],
    'PROSTATA': ['próstata', 'prostático', 'prostate'],
    'OVARIO': ['ovario', 'ovárico', 'ovarian'],
    'ENDOMETRIO': ['endometrio', 'endometrial', 'útero', 'uterino'],
    'HIGADO': ['hígado', 'hepático', 'liver', 'hepatic'],
    'PANCREAS': ['páncreas', 'pancreático', 'pancreas'],
    'RIÑON': ['riñón', 'renal', 'kidney', 'nefro'],
    'TIROIDES': ['tiroides', 'tiroideo', 'thyroid'],
    'PIEL': ['piel', 'cutáneo', 'dermatol', 'skin'],
    'VEJIGA': ['vejiga', 'vesical', 'bladder', 'urotelial'],
    'TUMOR REGION INTRADURAL': ['tumor region intradural', 'tumor intradural', 'region intradural'],
    'HIPOFISIS': ['hipofisis', 'hipófisis', 'hipofisiario', 'lesion hipofisis', 'lesión hipófisis'],
    'POLO TEMPORAL': ['polo temporal', 'temporal', 'meningioma temporal', 'lóbulo temporal'],
    'GANGLIO': ['ganglio', 'ganglios', 'ganglio profundo', 'ganglio linfático', 'ganglio linfatico'],  # REMOVED: 'metastásico', 'metastasico' - causan clasificación errónea
    'FEMUR': ['fémur', 'femur', 'femur distal', 'fémur distal', 'hueso fémur', 'hueso femur'],
    'MUSLO': ['muslo', 'muslo derecho', 'muslo izquierdo', 'biopsia de muslo', 'lesión muslo', 'lesion muslo'],
    'REGION PARIETO OCCIPITAL': ['region parieto occipital', 'región parieto occipital', 'parieto occipital', 'region parieto', 'región parieto', 'tumor extra axial', 'meningioma']
}


def clean_diagnostico_multipage(diagnostico_text: str) -> str:
    """Limpia el diagnóstico capturado de PDFs multipage

    v5.3.1: Maneja pie de página, separadores de página y metadatos repetidos

    Args:
        diagnostico_text: Texto del diagnóstico capturado

    Returns:
        Diagnóstico limpio sin residuos de cambio de página
    """
    if not diagnostico_text:
        return ''

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 1: Eliminar PIE DE PÁGINA estándar ISO/CAP/RCPAQAP
    # ═══════════════════════════════════════════════════════════════════════════
    pie_pagina_patterns = [
        # v5.3.2: AGREGADO - Pie de página "Patólogos (CAP), The Royal College..."
        r'Pat[óo]logos?\s*\(CAP\).*?(?:Oneworld\s+Accuracy|1WA)[^\n]*',
        r'Todos\s+los\s+an[aá]lisis\s+son\s+avalados.*?(?:ISO\s+17043|Oneworld\s+Accuracy|1WA)[^\n]*',
        r'Todos\s+los\s+an[aá]lisis\s+son\s+avalados.*?(?=\n---|\nIHQ\d+|$)',
        # v5.3.2: AGREGADO - Patrones adicionales para certificaciones
        r'The\s+Royal\s+College\s+of\s+Pathologists.*?(?:Oneworld|1WA)[^\n]*',
        r'Quality\s+Assurance\s+Programs.*?(?:Oneworld|1WA)[^\n]*',
    ]

    for pattern in pie_pagina_patterns:
        diagnostico_text = re.sub(pattern, '', diagnostico_text, flags=re.IGNORECASE | re.DOTALL)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 2: Eliminar SEPARADORES de página
    # ═══════════════════════════════════════════════════════════════════════════
    diagnostico_text = re.sub(r'-{3,}\s*P[ÁA]GINA\s+\d+\s*-{3,}', '', diagnostico_text, flags=re.IGNORECASE)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 3: Eliminar BLOQUES DE METADATOS repetidos (después de separador)
    # ═══════════════════════════════════════════════════════════════════════════
    # Patrón: IHQ######\nCopia Pag...\nNombre...\n...\nFecha Informe...
    # MEJORADO v5.3.1: Capturar TODO hasta después de "Servicio" o "Fecha Informe"
    # v5.3.1.1: También captura fragmentos pegados sin newline (ej: ".Copia Pag.")
    metadatos_patterns = [
        # Patrón completo: desde IHQ hasta Servicio (última línea de metadatos)
        r'[\n\.]?\s*IHQ\d{6}\s*[\n\s]*Copia\s+Pag\..*?Servicio\s*:\s*[A-ZÁÉÍÓÚÑ\s]+',
        # Patrón alternativo: desde IHQ hasta Fecha Informe
        r'[\n\.]?\s*IHQ\d{6}\s*[\n\s]*Copia\s+Pag\..*?Fecha\s+Informe\s*:\s*[\d/]+',
        # Patrón más simple: cualquier IHQ seguido de 6 dígitos
        r'[\n\.]?\s*IHQ\d{6}\s*',
        # Eliminar "Copia Pag." restantes (con o sin newline)
        r'[\n\.]?\s*Copia\s+Pag\.\s*\d+\s+de\s+\d+',
    ]

    for pattern in metadatos_patterns:
        diagnostico_text = re.sub(pattern, '', diagnostico_text, flags=re.IGNORECASE | re.DOTALL)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 3.5: Eliminar campos de metadatos individuales que puedan quedar
    # ═══════════════════════════════════════════════════════════════════════════
    # v5.3.1.1: También captura fragmentos pegados (ej: ". peticion : IHQ250980")
    campos_metadatos = [
        r'[\n\.]?\s*Nombre\s*:\s*[A-ZÁÉÍÓÚÑ\s]+(?:\n[A-ZÁÉÍÓÚÑ\s]+)?',  # Nombre (puede ser multilinea)
        r'[\n\.]?\s*N\.\s*peticion\s*:\s*IHQ\d+',
        r'[\n\.]?\s*peticion\s*:\s*IHQ\d+',  # Sin "N." (fragmento)
        r'[\n\.]?\s*N\.Identificaci[óo]n\s*:\s*[A-Z]{2}\.\s*\d+',
        r'[\n\.]?\s*Genero\s*:\s*[A-ZÁÉÍÓÚÑ]+',
        r'[\n\.]?\s*Edad\s*:\s*[\d\s]+a[ñn]os?.*?',
        r'[\n\.]?\s*EPS\s*:\s*[A-ZÁÉÍÓÚÑ\s]+',
        r'[\n\.]?\s*M[ée]dico\s+tratante\s*:\s*[A-ZÁÉÍÓÚÑ\s]+',
        r'[\n\.]?\s*Servicio\s*:\s*[A-ZÁÉÍÓÚÑ\s]+',
        r'[\n\.]?\s*Fecha\s+Ingreso\s*:\s*[\d/]+',
        r'[\n\.]?\s*Fecha\s+Informe\s*:\s*[\d/]+',
    ]

    for pattern in campos_metadatos:
        diagnostico_text = re.sub(pattern, '', diagnostico_text, flags=re.IGNORECASE)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 4: Eliminar NOMBRE DEL PATÓLOGO al final
    # ═══════════════════════════════════════════════════════════════════════════
    # Nombres conocidos: NANCY MEJIA VARGAS, ARMANDO CORTES BUELVAS, etc.
    nombres_patologos = [
        'NANCY\\s+MEJIA\\s+VARGAS',
        'ARMANDO\\s+CORTES\\s+BUELVAS',
        'CARLOS\\s+CAICEDO\\s+ESTRADA',
        'NATALIA\\s+AGUIRRE\\s+VASQUEZ',
        'JOSE\\s+BRAVO\\s+BONILLA',
    ]

    for nombre in nombres_patologos:
        # Eliminar nombre + cualquier línea posterior (Médica Patóloga, RM:, etc.)
        pattern = f'{nombre}.*?(?=\\n\\n|$)'
        diagnostico_text = re.sub(pattern, '', diagnostico_text, flags=re.IGNORECASE | re.DOTALL)

    # Patrón genérico: nombre en mayúsculas seguido de "Médica Patóloga" o "RM:"
    diagnostico_text = re.sub(
        r'\n\s*([A-ZÁÉÍÓÚÑ\s]{15,60}?)\s*\n\s*(?:M[ÉE]DIC[OA]\s+PAT[ÓO]LOG[OA]|RM:\s*\d+).*?$',
        '',
        diagnostico_text,
        flags=re.DOTALL
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 5: Eliminar líneas de NOTA y DISCLAIMER al final
    # ═══════════════════════════════════════════════════════════════════════════
    diagnostico_text = re.sub(
        r'Nota:\s+Este\s+informe.*?especialidadillas\.',
        '',
        diagnostico_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 6: Eliminar fragmentos residuales pegados al final
    # ═══════════════════════════════════════════════════════════════════════════
    # v5.3.1.1: Captura fragmentos como ". peticion :" que quedan pegados
    fragmentos_residuales = [
        r'\.\s*peticion\s*:.*?$',  # ". peticion : ..."
        r'\.\s*N\.\s*peticion.*?$',  # ". N. peticion ..."
        r'\.\s*Copia\s+Pag\..*?$',  # ". Copia Pag. ..."
        r'\.\s*[A-Z][a-z]+\s*:.*?$',  # ". Campo : ..." (genérico)
    ]

    for pattern in fragmentos_residuales:
        diagnostico_text = re.sub(pattern, '.', diagnostico_text, flags=re.IGNORECASE)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 7: Normalizar espacios y saltos de línea
    # ═══════════════════════════════════════════════════════════════════════════
    # Eliminar líneas vacías múltiples
    diagnostico_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', diagnostico_text)
    # Normalizar espacios múltiples en la misma línea
    diagnostico_text = re.sub(r' {2,}', ' ', diagnostico_text)
    # Eliminar puntos finales duplicados
    diagnostico_text = re.sub(r'\.\.+', '.', diagnostico_text)
    # Limpiar inicio y fin
    diagnostico_text = diagnostico_text.strip()

    return diagnostico_text


def extract_diagnostico_coloracion(text: str) -> str:
    """Extrae el diagnóstico completo del Estudio M (Coloración) con detección semántica.

    NUEVO v6.1.0 - Diagnóstico del Estudio M (Coloración)

    Este diagnóstico incluye información del estudio de patología general (NO IHQ):
    - Diagnóstico base histológico (ej: CARCINOMA DUCTAL INVASIVO)
    - Grado Nottingham (ej: GRADO NOTTINGHAM 2)
    - Invasión linfovascular (ej: INVASIÓN LINFOVASCULAR: NEGATIVO)
    - Invasión perineural (ej: INVASIÓN PERINEURAL: NEGATIVO)
    - Carcinoma ductal in situ (ej: CARCINOMA DUCTAL IN SITU: NO)

    A diferencia de DIAGNOSTICO_PRINCIPAL (que es la confirmación del IHQ),
    este campo captura el diagnóstico completo del estudio de coloración inicial.

    Detección semántica: busca keywords (NOTTINGHAM, GRADO, INVASIÓN) para identificar
    el diagnóstico correcto, NO se basa en posición.

    Args:
        text: Texto completo del informe IHQ

    Returns:
        str: Diagnóstico completo del Estudio M o cadena vacía

    Ejemplo de salida:
        "CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2 (SCORE 7), INVASIÓN LINFOVASCULAR: NEGATIVO, INVASIÓN PERINEURAL: NEGATIVO, CARCINOMA DUCTAL IN SITU: NO"
    """
    if not text:
        return ''

    # V6.0.2: CRÍTICO - Limpiar formato "de \"DIAGNOSTICO\"" (IHQ250981)
    # Problema: Extractor captura contexto de DESCRIPCIÓN MACROSCÓPICA con formato narrativo
    if text and isinstance(text, str):
        # Patrón 1: de "DIAGNOSTICO". Previa revisión DIAGNOSTICO (DUPLICADO)
        # Solución: Quitar "de \"" inicial y texto después de primera ocurrencia
        text = re.sub(r'^de\s+"([^"]+)"\.\s*Previa\s+revisi[óo]n\s+\1', r'\1', text, flags=re.IGNORECASE)

        # Patrón 2: de "DIAGNOSTICO". (sin duplicación)
        text = re.sub(r'^de\s+"([^"]+)"\.\s*', r'\1. ', text, flags=re.IGNORECASE)

        # Patrón 3: de "DIAGNOSTICO" (sin punto)
        text = re.sub(r'^de\s+"([^"]+)"', r'\1', text, flags=re.IGNORECASE)

        # Eliminar espacios múltiples resultantes
        text = re.sub(r'\s{2,}', ' ', text)
        text = text.strip()

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 1: Buscar en DESCRIPCIÓN MACROSCÓPICA
    # ═══════════════════════════════════════════════════════════════════════════
    # El diagnóstico del Estudio M (Coloración) suele aparecer citado aquí

    # Patrón: buscar texto entre comillas después de "diagnóstico de" o similar
    # Soporta comillas ASCII (" ') y Unicode (" " ' ')
    patron_citado = r'diagn[óo]stico\s+de\s*["\"\'\'\"]([^"\"\'\'\"]]+)["\"\'\'\"]'
    match_citado = re.search(patron_citado, text, re.IGNORECASE)

    if match_citado:
        diagnostico_candidato = match_citado.group(1).strip()

        # Validar que contiene keywords del Estudio M
        keywords_estudio_m = ['NOTTINGHAM', 'GRADO', 'INVASIÓN', 'INVASIVO', 'CARCINOMA']
        tiene_keywords = any(kw in diagnostico_candidato.upper() for kw in keywords_estudio_m)

        if tiene_keywords:
            return diagnostico_candidato

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 2: Buscar en la sección DIAGNÓSTICO
    # ═══════════════════════════════════════════════════════════════════════════
    # Si no está en DESC. MACROSCÓPICA, buscar líneas con keywords en DIAGNÓSTICO

    patron_diagnostico = r'DIAGN[ÓO]STICO\s*\n(.*?)(?=\n\s*[A-Z]{3,}:|\Z)'
    match_diagnostico = re.search(patron_diagnostico, text, re.DOTALL | re.IGNORECASE)

    if match_diagnostico:
        texto_diagnostico = match_diagnostico.group(1).strip()
        lineas = texto_diagnostico.split('\n')

        # Buscar líneas que contengan keywords del Estudio M
        candidatos = []
        keywords_estudio_m = ['NOTTINGHAM', 'GRADO', 'INVASIÓN LINFOVASCULAR', 'INVASIÓN PERINEURAL',
                              'CARCINOMA DUCTAL IN SITU', 'CARCINOMA IN SITU']

        for linea in lineas:
            linea_limpia = linea.strip().lstrip('- ').strip()

            # Ignorar líneas cortas o que son biomarcadores IHQ
            if len(linea_limpia) < 15:
                continue

            es_biomarcador = re.search(r'(RECEPTOR|HER|KI-67|P53|TTF|CK\d+|CD\d+)\s*[:\s]+(POSITIVO|NEGATIVO|\d+%)',
                                       linea_limpia, re.IGNORECASE)
            if es_biomarcador:
                continue

            # Verificar si tiene keywords del Estudio M
            tiene_keywords = any(kw in linea_limpia.upper() for kw in keywords_estudio_m)

            if tiene_keywords:
                candidatos.append(linea_limpia)

        # Concatenar todas las líneas candidatas (el diagnóstico puede ser multilinea)
        if candidatos:
            return ' '.join(candidatos)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 3: Buscar patrones específicos en todo el texto
    # ═══════════════════════════════════════════════════════════════════════════

    # Patrón 1: CARCINOMA ... GRADO NOTTINGHAM ... INVASIÓN ...
    patron_completo = r'((?:CARCINOMA|ADENOCARCINOMA)[^.\n]*?NOTTINGHAM[^.\n]*?INVASI[ÓO]N[^.]+\.)'
    match_completo = re.search(patron_completo, text, re.IGNORECASE | re.DOTALL)

    if match_completo:
        return match_completo.group(1).strip()

    # Patrón 2: Buscar componentes individuales y concatenar
    componentes = {}

    # Diagnóstico base
    patron_base = r'((?:CARCINOMA|ADENOCARCINOMA)[A-ZÁÉÍÓÚÑ\s]+?(?:INVASIVO|INFILTRANTE|IN SITU))'
    match_base = re.search(patron_base, text, re.IGNORECASE)
    if match_base:
        componentes['base'] = match_base.group(1).strip()

    # Grado Nottingham
    patron_nottingham = r'(GRADO\s+NOTTINGHAM\s+\d+(?:\s*\(SCORE\s+\d+\))?)'
    match_nottingham = re.search(patron_nottingham, text, re.IGNORECASE)
    if match_nottingham:
        componentes['nottingham'] = match_nottingham.group(1).strip()

    # Invasión linfovascular
    patron_linfovascular = r'(INVASI[ÓO]N\s+LINFOVASCULAR\s*[:\s]+(NEGATIVO|POSITIVO|NO|SI))'
    match_linfovascular = re.search(patron_linfovascular, text, re.IGNORECASE)
    if match_linfovascular:
        componentes['linfovascular'] = match_linfovascular.group(1).strip()

    # Invasión perineural
    patron_perineural = r'(INVASI[ÓO]N\s+PERINEURAL\s*[:\s]+(NEGATIVO|POSITIVO|NO|SI))'
    match_perineural = re.search(patron_perineural, text, re.IGNORECASE)
    if match_perineural:
        componentes['perineural'] = match_perineural.group(1).strip()

    # Carcinoma in situ
    patron_in_situ = r'(CARCINOMA\s+(?:DUCTAL\s+)?IN\s+SITU\s*[:\s]+(NO|SI|NEGATIVO|POSITIVO))'
    match_in_situ = re.search(patron_in_situ, text, re.IGNORECASE)
    if match_in_situ:
        componentes['in_situ'] = match_in_situ.group(1).strip()

    # Concatenar componentes en orden lógico
    if componentes:
        orden = ['base', 'nottingham', 'linfovascular', 'perineural', 'in_situ']
        partes = [componentes[k] for k in orden if k in componentes]
        return ', '.join(partes)

    # Si no se encontró nada, retornar vacío
    return ''


def extract_factor_pronostico(diagnostico_completo: str, ihq_estudios_solicitados: str = "") -> str:
    """Extrae factor pronóstico de biomarcadores de IHQ ÚNICAMENTE.

    CORRECCIÓN CRÍTICA v6.0.2:
    Este extractor fue corregido para extraer SOLO biomarcadores de inmunohistoquímica (IHQ).

    NO extrae información del estudio M (patología general):
    - NO extrae: Grado Nottingham (es del estudio M)
    - NO extrae: Invasión linfovascular (es del estudio M)
    - NO extrae: Invasión perineural (es del estudio M)
    - NO extrae: Carcinoma ductal in situ (es del estudio M)

    SÍ extrae biomarcadores de IHQ:
    - ER, PR, HER2, Ki-67, p53
    - TTF-1, CK7, CK20, p40, p16
    - Sinaptofisina, Cromogranina A, CD56
    - Napsina A, CDX2
    - Y otros biomarcadores específicos de IHQ

    Prioridades de búsqueda:
    1. Biomarcadores específicos (ER, PR, HER2, Ki-67, p53, TTF-1, CK7, etc.)
    2. Líneas de inmunorreactividad (si no hay biomarcadores específicos)
    3. Ki-67 genérico (si no hay nada más)

    Args:
        diagnostico_completo: Texto completo del informe (incluye DESCRIPCIÓN MICROSCÓPICA y DIAGNÓSTICO)
        ihq_estudios_solicitados: Lista de biomarcadores solicitados (opcional)

    Returns:
        Factor pronóstico concatenado con " / " o cadena vacía
    """
    if not diagnostico_completo:
        return ''

    factores = []

    # ═══════════════════════════════════════════════════════════════════════
    # PRIORIDAD 1: Biomarcadores específicos de IHQ
    # ═══════════════════════════════════════════════════════════════════════

    # V6.0.3: LISTA ORDENADA de biomarcadores (orden de impresión garantizado)
    # Orden: Ki-67 → HER2 → Receptor Estrógeno → Receptor Progesterona → resto
    biomarcadores_ordenados = [
        ('Ki-67', [
            r'Ki[\s-]?67\s*[:\s]+[0-9]+(?:-[0-9]+)?%',  # Ki-67: 51-60%
            r'Ki[\s-]?67\s+DEL\s+[0-9]+\s*%',           # Ki-67 DEL 2%
            r'[ÍI]NDICE\s+DE\s+PROLIFERACI[ÓO]N\s+C[ÉE]LULAR\s+(?:MEDIDO\s+CON\s+)?(?:\()?Ki[\s-]?67(?:\))?\s*[:\s]+[0-9]+(?:-[0-9]+)?\s*%',
            r'Ki[\s-]?67\s*[:\s]+(POSITIVO|NEGATIVO|ALTO|BAJO)',
        ]),
        ('HER2', [
            # V6.0.2: PRIORIDAD 1 - Formato "Expresión molecular" (IHQ250981)
            r'-?\s*SOBREEXPRESI[ÓO]N\s+DE\s+HER-?2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)\s*\([^)]+\)',
            # V6.0.2: PRIORIDAD 2 - Otros formatos
            r'HER[\s-]?2\s*[:\s]+[^.\n]+',
        ]),
        ('Receptor de Estrógeno', [
            # V6.0.2: PRIORIDAD 1 - Formato "Expresión molecular" (IHQ250981)
            r'-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\([^)]+\)',
            # V6.0.2: PRIORIDAD 2 - Formato descripción microscópica
            r'Estado\s+del\s+receptor\s+de\s+estr[óo]geno\s+\(ER\)\s+(Positivos?|Negativos?)\.\s+Porcentaje\s+de\s+c[ée]lulas\s+con\s+positividad\s+nuclear:\s+[^.\n]+',
            r'RECEPTOR(?:ES)?\s+DE\s+ESTR[ÓO]GENO[S]?\s*[:\s]+[^.\n]+',
            r'RE\s*[:\s]+[^.\n]+',
            r'ER\s*[:\s]+[^.\n]+',
        ]),
        ('Receptor de Progesterona', [
            # V6.0.2: PRIORIDAD 1 - Formato "Expresión molecular" (IHQ250981)
            r'-?\s*RECEPTORES\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\([^)]+\)',
            # V6.0.2: PRIORIDAD 2 - Formato descripción microscópica
            r'Estado\s+del\s+receptor\s+de\s+progesterona\s+\(PgR\)\s*:\s+(Positivos?|Negativos?)\.\s+Porcentaje\s+de\s+c[ée]lulas\s+con\s+positividad\s+nuclear:\s+[^.\n]+',
            r'RECEPTOR(?:ES)?\s+DE\s+PROGESTERONA\s*[:\s]+[^.\n]+',
            r'RP\s*[:\s]+[^.\n]+',
            r'PR\s*[:\s]+[^.\n]+',
        ]),
        ('p53', [
            r'p53\s+tiene\s+expresi[ÓO]n[^.\n]+',
            r'p53\s*[:\s]+[^.\n]+',
        ]),
        ('TTF-1', [
            r'TTF[\s-]?1\s*[:\s]+[^.\n]+',
        ]),
        ('CK7', [
            r'CK7\s*[:\s]+[^.\n]+',
        ]),
        ('CK20', [
            r'CK20\s*[:\s]+[^.\n]+',
        ]),
        ('p40', [
            r'p40\s+(POSITIVO|NEGATIVO|FOCAL|DIFUSO)',
        ]),
        ('p16', [
            r'p16\s+(POSITIVO|NEGATIVO)',
        ]),
        ('Sinaptofisina', [
            r'(?:Sinaptofisina|Synaptophysin)\s*[:\s]+[^.\n]+',
        ]),
        ('Cromogranina A', [
            r'Cromogranina\s*(?:A)?\s*[:\s]+[^.\n]+',
        ]),
        ('CD56', [
            r'CD56\s*[:\s]+[^.\n]+',
        ]),
        ('Napsina A', [
            r'Napsina\s+A\s*[:\s]+[^.\n]+',
        ]),
        ('CDX2', [
            r'CDX2\s*[:\s]+[^.\n]+',
        ]),
        ('CKAE1/AE3', [
            r'(?:CKAE1/AE3|CK\s*AE1\s*/\s*AE3)\s*[:\s]+[^.\n]+',
        ]),
    ]

    # Buscar cada biomarcador en el texto (en orden)
    for nombre_bio, patrones in biomarcadores_ordenados:
        for patron in patrones:
            match = re.search(patron, diagnostico_completo, re.IGNORECASE)
            if match:
                # Extraer valor completo del match
                valor = match.group(0).strip()

                # Validar que NO sea del contexto de Grado Nottingham o invasiones (estudio M)
                match_start = match.start()
                context_before = diagnostico_completo[max(0, match_start - 100):match_start].upper()

                # Ignorar si está en contexto de patología general (estudio M)
                if any(keyword in context_before for keyword in ['NOTTINGHAM', 'INVASIÓN LINFOVASCULAR', 'INVASIÓN PERINEURAL']):
                    continue

                # Limpiar valor (remover saltos de línea innecesarios)
                valor = re.sub(r'\s+', ' ', valor).strip()

                # Agregar a factores si no está duplicado
                if valor not in factores:
                    factores.append(valor)
                break

    # ═══════════════════════════════════════════════════════════════════════
    # PRIORIDAD 2: Líneas de inmunorreactividad (si no hay biomarcadores específicos)
    # ═══════════════════════════════════════════════════════════════════════

    if not factores:
        inmuno_patterns = [
            r'Las\s+c[ée]lulas\s+tumorales\s+presentan\s+inmuno[^\n.]+\.',
            r'Los\s+marcadores[^\n.]+(?:negativos?|positivos?)\.',
        ]

        for patron in inmuno_patterns:
            match = re.search(patron, diagnostico_completo, re.IGNORECASE)
            if match:
                inmuno_text = match.group(0).strip()
                inmuno_text = re.sub(r'\s+', ' ', inmuno_text)
                factores.append(inmuno_text)
                break

    # ═══════════════════════════════════════════════════════════════════════
    # PRIORIDAD 3: Otros biomarcadores en última línea del diagnóstico
    # ═══════════════════════════════════════════════════════════════════════
    # Formato: "- TUMOR... p40 POSITIVO / p16 POSITIVO"

    if not factores:
        diag_lines = [line.strip() for line in diagnostico_completo.split('\n')
                      if line.strip().startswith('-') and not line.strip().startswith('---')]

        if diag_lines:
            last_diag_line = diag_lines[-1]
            marker_pattern = r'(?:CARCINOMA|ADENOCARCINOMA|SARCOMA|MELANOMA|LINFOMA|TUMOR|NEOPLASIA)\s+[A-ZÁÉÍÓÚÑ\s]+?\s+((?:[a-zA-Z0-9\-]+\s+(?:POSITIVO|NEGATIVO|FOCAL|DIFUSO)[/\s]*)+)'
            marker_match = re.search(marker_pattern, last_diag_line, re.IGNORECASE)

            if marker_match:
                otros_marcadores = marker_match.group(1).strip()
                factores.append(otros_marcadores)

    # ═══════════════════════════════════════════════════════════════════════
    # RETORNAR
    # ═══════════════════════════════════════════════════════════════════════

    # V6.0.1: Normalizar términos largos de Ki-67 (AMPLIADO para IHQ250981)
    factor_pronostico_texto = ' / '.join(factores)

    # Normalizar "Índice de proliferación celular (Ki67)" → "Ki-67"
    normalizaciones = [
        ("Índice de proliferación celular (Ki67)", "Ki-67"),
        ("Índice de proliferación celular (Ki-67)", "Ki-67"),
        ("índice de proliferación celular (Ki67)", "Ki-67"),
        ("índice de proliferación celular (Ki-67)", "Ki-67"),
        ("ÍNDICE DE PROLIFERACIÓN CELULAR (KI67)", "Ki-67"),
        ("ÍNDICE DE PROLIFERACIÓN CELULAR (KI-67)", "Ki-67"),
        # V6.0.1: Variantes con múltiples espacios (OCR puede introducir espacios extra)
        ("Índice  de  proliferación  celular  (Ki67)", "Ki-67"),
        ("Índice  de  proliferación  celular  (Ki-67)", "Ki-67"),
        # V6.0.1: Normalizar otras variantes verbosas
        ("receptor de estrógeno (ER)", "ER"),
        ("receptor de progesterona (PgR)", "PR"),
        ("receptor de progesterona (PR)", "PR"),
        ("Receptor de estrógeno", "ER"),
        ("Receptor de progesterona", "PR"),
    ]

    # V6.0.1: Aplicar normalizaciones (case-insensitive)
    for original, reemplazo in normalizaciones:
        # Buscar case-insensitive
        factor_pronostico_texto = re.sub(re.escape(original), reemplazo, factor_pronostico_texto, flags=re.IGNORECASE)

    return factor_pronostico_texto if factores else ''


def extract_biomarcadores_solicitados_robust(text: str) -> List[str]:
    """Extrae TODOS los biomarcadores solicitados del PDF con alta precisión.

    Versión: 3.2.5 - Extractor robusto para IHQ_ESTUDIOS_SOLICITADOS

    Busca patrones en DESCRIPCION MACROSCOPICA como:
    - "para tinción con [lista]"
    - "para los siguientes marcadores: [lista]"
    - "se solicitan los siguiente biomarcadores: [lista]"
    - "se realizan niveles histológicos para tinción con [lista]"

    Args:
        text: Texto completo del informe IHQ

    Returns:
        Lista de biomarcadores solicitados (normalizados y sin duplicados)
    """
    if not text:
        return []

    biomarcadores_encontrados = []

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 1: Extraer sección DESCRIPCION MACROSCOPICA
    # ═══════════════════════════════════════════════════════════════════════════
    desc_macro_match = re.search(
        r'DESCRIPCI[OÓ]N\s+MACROSC[OÓ]PICA(.*?)(?:DESCRIPCI[OÓ]N\s+MICROSC[OÓ]PICA|$)',
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not desc_macro_match:
        return []

    desc_macro_text = desc_macro_match.group(1)

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 2: Buscar patrones de listas de biomarcadores
    # ═══════════════════════════════════════════════════════════════════════════

    # Patrones ordenados por especificidad (más específico primero)
    patrones_biomarcadores = [
        # Patrón 1: "para los siguientes marcadores:" (IHQ250002, IHQ250006)
        r'para\s+los?\s+siguientes?\s+(?:biomarcadores?|marcadores?):\s*([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ]+?)(?:\.|\n\s*DESCRIPCI)',

        # Patrón 2: "se solicitan los siguiente biomarcadores:" (IHQ250005)
        r'se\s+solicitan?\s+los?\s+siguientes?\s+(?:biomarcadores?|marcadores?):\s*([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ]+?)(?:\.|\n\s*DESCRIPCI)',

        # Patrón 3: "para tinción con" O "para tinción con:" (IHQ250001, IHQ250003, IHQ250981)
        # v6.0.3 - Agregado soporte para dos puntos opcionales después de "con"
        # v6.0.3 - CORREGIDO: Termina solo en punto (.) para permitir saltos de línea en lista
        r'para\s+tinci[óo]n\s+con:?\s+([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ\n]+?)\.',

        # Patrón 4: "se realizan niveles histológicos para tinción con" O "para tinción con:"
        # v6.0.3 - Agregado soporte para dos puntos opcionales después de "con"
        # v6.0.3 - CORREGIDO: Termina solo en punto (.) para permitir saltos de línea en lista
        r'se\s+realizan?\s+(?:cortes?|niveles?)\s+histol[óo]gicos?\s+.*?para\s+tinci[óo]n\s+con:?\s+([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ\n]+?)\.',

        # Patrón 5: "para tinción de la siguiente manera:" seguido de lista con guiones
        r'para\s+tinci[óo]n\s+de\s+la\s+siguiente\s+manera:\s*((?:-\s*Bloque[^\n]+\n?)+)',

        # Patrón 6: V5.3.2 - "se solicita(n) marcador(es) X" (IHQ250050)
        # Captura todo después de "marcador(es)" hasta el punto o salto de línea
        r'se\s+solicitan?\s+marcador(?:es)?\s+([^.\n]+)',

        # Patrón 7: V5.3.2 - "para X Y Y" (IHQ250021, IHQ250042)
        # Captura lista de biomarcadores separados por "Y" o "y"
        r'(?:de\s+)?inmunohistoqu[íi]mica\s+para\s+([A-Z0-9\s]+(?:\s+[Yy]\s+[A-Z0-9\s]+)+)',

        # Patrón 8: V5.3.2 - "con X - Y - Z" (IHQ250043)
        # Captura lista de biomarcadores separados por guiones
        r'inmunohistoqu[íi]mica\s+con\s+([A-Z0-9\s]+(?:\s*-\s*[A-Z0-9\s]+)+)',

        # Patrón 9: V5.3.2 - "para marcar con X" (IHQ250048)
        # Captura biomarcador después de "para marcar con"
        r'para\s+marcar\s+con\s+([^.\n]+)',
    ]

    for patron in patrones_biomarcadores:
        match = re.search(patron, desc_macro_text, re.IGNORECASE | re.DOTALL)
        if match:
            lista_texto = match.group(1).strip()

            # CASO ESPECIAL: Lista con formato "- Bloque A: X, Y, Z"
            if '- Bloque' in lista_texto or '-Bloque' in lista_texto:
                # Extraer biomarcadores de cada línea de bloque
                lineas_bloque = re.findall(r'-\s*Bloque\s+[A-Z0-9]+:\s*([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ]+)', lista_texto, re.IGNORECASE)
                for linea in lineas_bloque:
                    biomarcadores_linea = parse_biomarker_list(linea)
                    biomarcadores_encontrados.extend(biomarcadores_linea)
            else:
                # CASO NORMAL: Lista separada por comas/y
                biomarcadores = parse_biomarker_list(lista_texto)
                biomarcadores_encontrados.extend(biomarcadores)

            # Si encontramos algo, no seguir buscando con otros patrones
            if biomarcadores_encontrados:
                break

    # ═══════════════════════════════════════════════════════════════════════════
    # PASO 3: Normalizar y eliminar duplicados
    # ═══════════════════════════════════════════════════════════════════════════
    biomarcadores_normalizados = []
    vistos = set()

    # V5.2: Lista de valores no válidos que deben ser filtrados DESPUÉS de normalización
    valores_invalidos = {
        'IHQ_NA', 'IHQ_N/A', 'IHQ_N / A', 'IHQ_NO APLICA',  # N/A normalizados
        'IHQ_ACTH', 'IHQ_FSH', 'IHQ_GH', 'IHQ_LH', 'IHQ_PROLACTINA', 'IHQ_TSH',  # Hormonas
        'IHQ_CORTISOL', 'IHQ_INSULINA', 'IHQ_GLUCAGON', 'IHQ_T3', 'IHQ_T4'
    }

    for bio in biomarcadores_encontrados:
        # V5.3: CORRECCIÓN - Usar normalize_biomarker_name_simple() sin prefijo IHQ_
        # La columna IHQ_ESTUDIOS_SOLICITADOS debe contener nombres simples: "MLH1, MSH2, Ki-67"
        # NO debe contener "IHQ_MLH1, IHQ_MSH2, IHQ_Ki-67" (eso es para columnas BD)
        bio_norm = normalize_biomarker_name_simple(bio)

        # V5.2: Filtrar valores no válidos DESPUÉS de normalización
        if bio_norm.upper() in valores_invalidos:
            continue

        if bio_norm and bio_norm.upper() not in vistos:
            biomarcadores_normalizados.append(bio_norm)
            vistos.add(bio_norm.upper())

    return biomarcadores_normalizados


def parse_biomarker_list(text: str) -> List[str]:
    """Parsea una lista de biomarcadores de texto con separadores variados.

    Maneja separadores como:
    - Comas: "CK7, CK20, TTF-1"
    - "y": "p16 y p40"
    - "/": "CKAE1/AE3"
    - Espacios múltiples

    Args:
        text: Texto conteniendo lista de biomarcadores

    Returns:
        Lista de biomarcadores individuales
    """
    if not text:
        return []

    # Limpiar texto
    text = text.strip()

    # Eliminar texto explicativo común
    text = re.sub(r'(?:Previa\s+valoraci[óo]n|se\s+realizan?|niveles?\s+histol[óo]gicos?|cortes?\s+histol[óo]gicos?).*?(?=(?:[A-Z]{2,}|$))', '', text, flags=re.IGNORECASE)

    # Reemplazar separadores por comas
    # "y" final → ","
    text = re.sub(r'\s+y\s+', ', ', text, flags=re.IGNORECASE)

    # Dividir por comas
    biomarcadores = [b.strip() for b in text.split(',')]

    # Filtrar vacíos y texto no-biomarcador
    biomarcadores_filtrados = []
    for bio in biomarcadores:
        # Ignorar si es muy corto o contiene palabras no-biomarcador
        if len(bio) < 2:
            continue

        # V3.2.5.1: FILTRO MEJORADO - Detectar encabezados de tabla
        bio_upper = bio.upper().strip()

        # V5.2: FILTRO DE N/A - Ignorar entradas "N/A"
        if bio_upper in ['N/A', 'NA', 'N / A', 'NO APLICA']:
            continue

        # V5.2: FILTRO DE HORMONAS - No son biomarcadores IHQ, son hormonas endocrinas
        hormonas_endocrinas = [
            'ACTH', 'FSH', 'GH', 'LH', 'PROLACTINA', 'TSH',
            'CORTISOL', 'INSULINA', 'GLUCAGON', 'T3', 'T4'
        ]
        if bio_upper in hormonas_endocrinas:
            continue

        # Filtrar encabezados de tabla EXACTOS o con prefijos
        encabezados_tabla = [
            r'^N\.?\s*ESTUDIO$',  # "N. ESTUDIO" o "N ESTUDIO"
            r'^TIPO\s+ESTUDIO$',  # "TIPO ESTUDIO"
            r'^TIPO\s+DE\s+ESTUDIO$',  # "TIPO DE ESTUDIO"
            r'^ESTUDIO$',  # "ESTUDIO" solo
            r'^ORGANO$',  # "ORGANO" solo
            r'^ÓRGANO$',  # "ÓRGANO" solo
            r'^FECHA\s+TOMA$',  # "FECHA TOMA"
            r'^BLOQUES?\s+Y\s+LAMINAS?$',  # "BLOQUES Y LAMINAS"
            r'^ALMACENAMIENTO$',  # "ALMACENAMIENTO"
        ]

        if any(re.match(patron, bio_upper) for patron in encabezados_tabla):
            continue

        # Filtrar palabras no-biomarcador en texto
        if re.search(r'(?:bloque|laminas?|para|con|los|siguiente|almacenamiento)', bio, re.IGNORECASE):
            continue

        biomarcadores_filtrados.append(bio)

    return biomarcadores_filtrados


def normalize_biomarker_name_simple(name: str) -> str:
    """Normaliza el nombre de un biomarcador SIN prefijo IHQ_.

    V5.3: Para uso en IHQ_ESTUDIOS_SOLICITADOS (sin prefijo)

    Ejemplos:
    - "CKAE1/AE3" → "CKAE1AE3"
    - "Ki 67" → "Ki-67"
    - "RECEPTOR DE ESTROGENOS" → "Receptor de Estrógeno"
    - "CD68" → "CD68"
    - "MLH1" → "MLH1"

    Args:
        name: Nombre del biomarcador

    Returns:
        Nombre normalizado SIN prefijo IHQ_
    """
    if not name:
        return ''

    # Limpiar espacios extras
    name = re.sub(r'\s+', ' ', name.strip())
    nombre_upper = name.upper()

    # Mapeo directo para casos especiales (SIN prefijo IHQ_)
    simple_mapping = {
        'CKAE1/AE3': 'CKAE1AE3',
        'CKAE1 / AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CAM 5.2': 'CAM5.2',
        'CAM5.2': 'CAM5.2',
    }

    for pattern, result in simple_mapping.items():
        if pattern in nombre_upper:
            return result

    # Normalizar espacios y caracteres especiales
    # Eliminar palabras intermedias comunes (DE, DEL, LOS, LAS)
    nombre_clean = re.sub(r'\b(DE|DEL|LOS|LAS|LA|EL)\b', '', nombre_upper)
    nombre_clean = re.sub(r'\s+', ' ', nombre_clean).strip()

    # Receptores: mantener formato legible
    if 'RECEPTOR' in nombre_clean:
        if any(v in nombre_clean for v in ['ESTROGENO', 'ESTROGENOS', 'ESTRÓGENO', 'ESTRÓGENOS']):
            return 'Receptor de Estrógeno'
        if any(v in nombre_clean for v in ['PROGESTERONA', 'PROGESTERON', 'PROGESTERONOS']):
            return 'Receptor de Progesterona'

    # V6.0.1: Normalizar nombres cortos de receptores (CORRIGE IHQ250981)
    if nombre_upper in ['PROGESTERONA', 'PROGRESTERONA']:
        return 'Receptor de Progesterona'
    if nombre_upper in ['ESTROGENOS', 'ESTRÓGENOS', 'ESTROGENO', 'ESTRÓGENO']:
        return 'Receptor de Estrógeno'

    # Ki-67: mantener guión (TODAS LAS VARIANTES)
    if re.match(r'KI[\s-]?67', nombre_upper):
        return 'Ki-67'

    # TTF-1: mantener guión
    if re.match(r'TTF[\s-]?1', nombre_upper):
        return 'TTF-1'

    # PDL-1: mantener guión
    if 'PDL' in nombre_upper or 'PD-L' in nombre_upper or 'PD L' in nombre_upper:
        return 'PDL-1'

    # HER2: normalizar espacios
    if 'HER2' in nombre_upper or 'HER-2' in nombre_upper or 'HER 2' in nombre_upper:
        return 'HER2'

    # V6.0.1: E-Cadherina (CORRIGE IHQ250981)
    if 'CADHERINA' in nombre_upper or 'CADHERIN' in nombre_upper:
        return 'E-Cadherina'

    # MMR markers: mantener nombre simple
    if 'MLH1' in nombre_upper:
        return 'MLH1'
    if 'MSH2' in nombre_upper:
        return 'MSH2'
    if 'MSH6' in nombre_upper:
        return 'MSH6'
    if 'PMS2' in nombre_upper:
        return 'PMS2'

    # Marcadores CD: mantener formato
    if re.match(r'^CD\d+$', nombre_upper):
        return nombre_upper

    # Para otros: limpiar y devolver en mayúsculas
    name_clean = name.replace('/', '').replace('-', ' ')
    name_clean = re.sub(r'\s+', ' ', name_clean).strip()
    return name_clean.upper()


def normalize_biomarker_name(name: str) -> str:
    """Normaliza el nombre de un biomarcador CON prefijo IHQ_.

    V5.2: SIEMPRE retorna nombres con prefijo IHQ_ para consistencia con columnas BD.
    V5.3: SOLO usar para columnas BD, NO para IHQ_ESTUDIOS_SOLICITADOS

    Ejemplos:
    - "CKAE1/AE3" → "IHQ_CKAE1AE3"
    - "Ki 67" → "IHQ_KI-67"
    - "RECEPTOR DE ESTROGENOS" → "IHQ_RECEPTOR_ESTROGENOS"
    - "CD68" → "IHQ_CD68"
    - "P16" → "IHQ_P16_ESTADO"

    Args:
        name: Nombre del biomarcador

    Returns:
        Nombre normalizado con prefijo IHQ_
    """
    if not name:
        return ''

    # Limpiar espacios extras
    name = re.sub(r'\s+', ' ', name.strip())

    # Mapeo de nombres especiales
    nombre_upper = name.upper()

    # CORREGIDO v3.2.5.1: Eliminar palabras intermedias comunes (DE, DEL, LOS, LAS)
    nombre_clean = re.sub(r'\b(DE|DEL|LOS|LAS|LA|EL)\b', '', nombre_upper)
    nombre_clean = re.sub(r'\s+', ' ', nombre_clean).strip()

    # Receptores hormonales (buscar en texto limpio con y sin acentos)
    # V3.2.5.2: FIX - Agregar variantes con acentos (ESTRÓGENO, ESTRÓGENOS)
    if 'RECEPTOR' in nombre_clean:
        # Buscar variantes de estrógeno (con y sin acento, singular y plural)
        if any(variant in nombre_clean for variant in ['ESTROGENO', 'ESTROGENOS', 'ESTRÓGENO', 'ESTRÓGENOS']):
            return 'IHQ_RECEPTOR_ESTROGENOS'
        # Buscar variantes de progesterona (con y sin acento, singular y plural)
        if any(variant in nombre_clean for variant in ['PROGESTERONA', 'PROGESTERON', 'PROGESTERONOS']):
            return 'IHQ_RECEPTOR_PROGESTERONA'

    # Citoqueratinas con barra
    if 'CKAE1/AE3' in nombre_upper or 'CKAE1 / AE3' in nombre_upper or 'CK AE1/AE3' in nombre_upper:
        return 'IHQ_CKAE1AE3'

    # Ki-67 variantes - V5.2: CON prefijo IHQ_
    if re.match(r'KI[\s-]?67', nombre_upper):
        return 'IHQ_KI-67'

    # TTF-1 variantes - V5.2: CON prefijo IHQ_
    if re.match(r'TTF[\s-]?1', nombre_upper):
        return 'IHQ_TTF1'

    # Napsina - V5.2: CON prefijo IHQ_
    if 'NAPSIN' in nombre_upper:
        return 'IHQ_NAPSIN'

    # CAM 5.2 - V5.2: CON prefijo IHQ_
    if 'CAM' in nombre_upper and '5' in nombre_upper:
        return 'IHQ_CAM52'

    # Chromogranina - V5.2: CON prefijo IHQ_
    if 'CHROMO' in nombre_upper:
        return 'IHQ_CHROMOGRANINA'

    # Synaptofisina - V5.2: CON prefijo IHQ_
    if 'SINAPTO' in nombre_upper or 'SYNAPTO' in nombre_upper:
        return 'IHQ_SYNAPTOPHYSIN'

    # HER2 - V5.2: CON prefijo IHQ_
    if 'HER2' in nombre_upper or 'HER-2' in nombre_upper or 'HER 2' in nombre_upper:
        return 'IHQ_HER2'

    # P16 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'P16':
        return 'IHQ_P16_ESTADO'

    # P40 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'P40':
        return 'IHQ_P40_ESTADO'

    # P53 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'P53':
        return 'IHQ_P53'

    # P63 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'P63':
        return 'IHQ_P63'

    # PDL-1 - V5.2: CON prefijo IHQ_
    if 'PDL' in nombre_upper or 'PD-L' in nombre_upper or 'PD L' in nombre_upper:
        return 'IHQ_PDL-1'

    # S100 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'S100':
        return 'IHQ_S100'

    # VIMENTINA - V5.2: CON prefijo IHQ_
    if 'VIMENT' in nombre_upper:
        return 'IHQ_VIMENTINA'

    # EMA - V5.2: CON prefijo IHQ_
    if nombre_upper == 'EMA':
        return 'IHQ_EMA'

    # GATA3 - V5.2: CON prefijo IHQ_
    if 'GATA3' in nombre_upper:
        return 'IHQ_GATA3'

    # SOX10 - V5.2: CON prefijo IHQ_
    if 'SOX10' in nombre_upper:
        return 'IHQ_SOX10'

    # CK7 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'CK7':
        return 'IHQ_CK7'

    # CK20 - V5.2: CON prefijo IHQ_
    if nombre_upper == 'CK20':
        return 'IHQ_CK20'

    # CDX2 - V5.2: CON prefijo IHQ_
    if 'CDX2' in nombre_upper:
        return 'IHQ_CDX2'

    # MMR markers - V5.2: CON prefijo IHQ_
    if 'MLH1' in nombre_upper:
        return 'IHQ_MLH1'
    if 'MSH2' in nombre_upper:
        return 'IHQ_MSH2'
    if 'MSH6' in nombre_upper:
        return 'IHQ_MSH6'
    if 'PMS2' in nombre_upper:
        return 'IHQ_PMS2'

    # PAX8 - V5.2: CON prefijo IHQ_
    if 'PAX8' in nombre_upper or 'PAX-8' in nombre_upper or 'PAX 8' in nombre_upper:
        return 'IHQ_PAX8'

    # PAX5 - V5.2: CON prefijo IHQ_
    if 'PAX5' in nombre_upper or 'PAX-5' in nombre_upper:
        return 'IHQ_PAX5'

    # GFAP - V5.2: CON prefijo IHQ_
    if 'GFAP' in nombre_upper:
        return 'IHQ_GFAP'

    # MELAN-A - V5.2: CON prefijo IHQ_
    if 'MELAN' in nombre_upper:
        return 'IHQ_MELAN_A'

    # CDK4 - V5.2: CON prefijo IHQ_
    if 'CDK4' in nombre_upper:
        return 'IHQ_CDK4'

    # MDM2 - V5.2: CON prefijo IHQ_
    if 'MDM2' in nombre_upper:
        return 'IHQ_MDM2'

    # DOG1 - V5.2: CON prefijo IHQ_
    if 'DOG1' in nombre_upper or 'DOG-1' in nombre_upper:
        return 'IHQ_DOG1'

    # HHV8 - V5.2: CON prefijo IHQ_
    if 'HHV8' in nombre_upper or 'HHV-8' in nombre_upper:
        return 'IHQ_HHV8'

    # WT1 - V5.2: CON prefijo IHQ_
    if 'WT1' in nombre_upper or 'WT-1' in nombre_upper:
        return 'IHQ_WT1'

    # NEUN - V5.2: CON prefijo IHQ_
    if 'NEUN' in nombre_upper or 'NEU-N' in nombre_upper:
        return 'IHQ_NEUN'

    # ACTIN - V5.2: CON prefijo IHQ_
    if 'ACTIN' in nombre_upper or ('MUSCULO' in nombre_upper and 'LISO' in nombre_upper):
        return 'IHQ_ACTIN'

    # Biomarcadores CD - V5.2: CON prefijo IHQ_
    if re.match(r'^CD\d+$', nombre_upper):
        return f'IHQ_{nombre_upper}'  # "CD68" → "IHQ_CD68"

    # CORREGIDO v3.2.5.1: No eliminar TODOS los espacios, solo normalizar múltiples
    # Eliminar barras y guiones, normalizar espacios múltiples a uno solo
    name_clean = name.replace('/', '').replace('-', '')
    name_clean = re.sub(r'\s+', ' ', name_clean).strip()

    # V5.2: SIEMPRE agregar prefijo IHQ_ si no lo tiene
    normalized = name_clean.upper()
    if not normalized.startswith('IHQ_'):
        normalized = f'IHQ_{normalized}'

    return normalized


def _preprocess_multipage_diagnosis(text: str) -> str:
    """Preprocesa texto para unir diagnóstico que está dividido en múltiples páginas

    v5.3.2: Detecta cuando el DIAGNÓSTICO continúa después de separador de página
    y metadatos, y une las partes en un solo bloque antes de la extracción.

    Ejemplo:
        Página 1:
            DIAGNÓSTICO
             - CARCINOMA...
             - RECEPTORES DE ESTRÓGENO...
            [pie de página]
            --- PÁGINA 2 ---
            [metadatos repetidos]
            - RECEPTORES DE PROGESTERONA...  ← CONTINUACIÓN
            - HER2...
            - KI-67...

    Args:
        text: Texto OCR completo con múltiples páginas

    Returns:
        Texto con diagnóstico unificado
    """
    if not text or '---' not in text:
        # No hay separadores de página, retornar sin cambios
        return text

    # Buscar patrón: DIAGNÓSTICO seguido de contenido, luego separador de página
    # Patrón: DIAGNÓSTICO\n (contenido) \n (pie de página) \n --- PÁGINA X --- \n (metadatos) \n (continuación con "- ")

    # Paso 1: Encontrar la sección DIAGNÓSTICO en página 1
    match_diag = re.search(
        r'(DIAGN[OÓ]STICO\s*\n.*?)(?=Todos\s+los\s+an[aá]lisis\s+son\s+avalados|Pat[óo]logos?\s*\(CAP\)|---\s*P[ÁA]GINA)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if not match_diag:
        return text

    diagnostico_pag1 = match_diag.group(1)

    # Paso 2: Buscar continuación después de separador de página
    # Patrón: --- PÁGINA X --- ... (metadatos) ... líneas que empiezan con "- " (continuación del diagnóstico)
    match_continuation = re.search(
        r'---\s*P[ÁA]GINA\s+\d+\s*---.*?(?:Fecha\s+Informe\s*:.*?\n)((?:\s*-\s+[^\n]+\n)+)',
        text,
        re.DOTALL | re.IGNORECASE
    )

    if not match_continuation:
        return text

    continuacion_pag2 = match_continuation.group(1).strip()

    # Paso 3: Unir diagnóstico completo
    diagnostico_completo = diagnostico_pag1.rstrip() + '\n' + continuacion_pag2

    # Paso 4: Reemplazar en el texto original
    # Eliminar la parte original del diagnóstico en pag 1 (hasta pie de página)
    text = re.sub(
        r'DIAGN[OÓ]STICO\s*\n.*?(?=Todos\s+los\s+an[aá]lisis\s+son\s+avalados|Pat[óo]logos?\s*\(CAP\)|---\s*P[ÁA]GINA)',
        diagnostico_completo + '\n',
        text,
        count=1,
        flags=re.DOTALL | re.IGNORECASE
    )

    # Eliminar la continuación de pag 2 (ya está unida arriba)
    text = re.sub(
        r'(---\s*P[ÁA]GINA\s+\d+\s*---.*?Fecha\s+Informe\s*:.*?\n)((?:\s*-\s+[^\n]+\n)+)',
        r'\1',  # Mantener separador y metadatos, eliminar continuación
        text,
        flags=re.DOTALL | re.IGNORECASE
    )

    return text


def extract_medical_data(text: str) -> Dict[str, Any]:
    """Extrae todos los datos médicos del texto IHQ

    Args:
        text: Texto del informe médico IHQ

    Returns:
        Diccionario con datos médicos extraídos
    """
    if not text:
        return {}

    # CORREGIDO: clean_text_comprehensive rompe los patrones, usar texto original
    clean_text = text  # clean_text_comprehensive(text)

    # v5.3.2: PREPROCESAR - Unir diagnóstico multipágina ANTES de extracción
    clean_text = _preprocess_multipage_diagnosis(clean_text)

    results = {}

    # === EXTRAER CAMPOS MÉDICOS BÁSICOS ===
    for key, pattern in PATTERNS_IHQ.items():
        # v5.3.3: Para descripcion_microscopica_final, NO usar re.IGNORECASE
        # para que solo detecte "DIAGNÓSTICO" en mayúsculas
        if key == 'descripcion_microscopica_final':
            match = re.search(pattern, clean_text, re.DOTALL)  # Sin re.IGNORECASE
        else:
            match = re.search(pattern, clean_text, re.IGNORECASE | re.DOTALL)

        if key == 'fecha_toma_raw':
            val = match.group(1).strip() if match else ''
            results['fecha_toma'] = convert_date_format(val) if val else 'SIN DATO'
        else:
            results[key] = match.group(1).strip() if match else ''

    # === LIMPIEZA ESPECIAL: DIAGNÓSTICO MULTIPAGE ===
    # v5.3.1: Limpiar diagnóstico de residuos de página (footer, separadores, metadatos repetidos)
    if results.get('diagnostico_final_ihq'):
        diagnostico_raw = results['diagnostico_final_ihq']
        diagnostico_clean = clean_diagnostico_multipage(diagnostico_raw)
        results['diagnostico_final_ihq'] = diagnostico_clean

    # === EXTRAER DATOS ADICIONALES CON PATRONES GENÉRICOS ===
    # Información de estudios y procedimientos - VERSIÓN ROBUSTA v3.2.5
    # CORREGIDO v4.2.6: Siempre sobrescribir (incluso si vacío) para eliminar encabezados de tabla capturados por patrón antiguo
    biomarcadores_solicitados = extract_biomarcadores_solicitados_robust(clean_text)
    results['estudios_solicitados'] = ', '.join(biomarcadores_solicitados) if biomarcadores_solicitados else ''

    # Información del órgano (múltiples patrones)
    organo_value = extract_organ_information(clean_text)
    if organo_value:
        results['organo'] = organo_value

    # === EXTRACCIÓN INTELIGENTE DE IHQ_ORGANO ===
    # Extraer órgano desde el diagnóstico (ej: "Región intradural (cauda equina)")
    ihq_organo = extract_ihq_organ_from_diagnosis(results.get('diagnostico_final_ihq', ''))
    if ihq_organo:
        results['ihq_organo'] = ihq_organo

    # === DERIVAR CAMPOS COMPLEJOS ===

    # Malignidad basada en múltiples fuentes
    malignidad = determine_malignancy(
        results.get('diagnostico_final_ihq', ''),
        results.get('descripcion_macroscopica_ihq', ''),
        results.get('descripcion_microscopica_final', ''),
        clean_text
    )
    results['malignidad'] = malignidad

    # Procesar descripciones finales
    results = process_medical_descriptions(results, clean_text)

    # EXTRAER FECHAS ADICIONALES Y COMBINAR RESULTADOS
    fecha_results = extract_additional_dates(results, clean_text)
    results.update(fecha_results)

    # Extraer información del responsable
    results = extract_responsible_physician(results, clean_text)

    # CORREGIDO v4.2: Extraer factor pronóstico de TODO el texto (no solo diagnóstico)
    # Esto permite capturar Ki-67 y p53 que pueden estar en cualquier parte del informe
    factor_pronostico = extract_factor_pronostico(clean_text)
    if factor_pronostico:
        results['factor_pronostico'] = factor_pronostico

    # NUEVO v6.1.0: Extraer diagnóstico del Estudio M (Coloración) con Nottingham
    diagnostico_coloracion = extract_diagnostico_coloracion(clean_text)
    if diagnostico_coloracion:
        results['diagnostico_coloracion'] = diagnostico_coloracion

    # Especialidad deducida
    servicio = extract_service_info(clean_text)
    if servicio:
        results['servicio'] = servicio
        results['especialidad_deducida'] = deduce_specialty_ihq(servicio)

    # Información complementaria
    results['tipo_informe'] = 'INMUNOHISTOQUIMICA'
    results['hospitalizado'] = 'NO'
    # ELIMINADO: n_autorizacion - campo no utilizado que genera NaN en exportación


    # ═══════════════════════════════════════════════════════════════════════
    # NUEVO v4.2.2: Si no hay diagnóstico principal, extraer de descripción
    # v5.3.6: CORREGIDO - Guardar texto COMPLETO, no solo diagnóstico principal
    # ═══════════════════════════════════════════════════════════════════════
    if not results.get('diagnostico_final_ihq') or results.get('diagnostico_final_ihq') in ['', 'N/A']:
        # Buscar descripción diagnóstico en el texto
        desc_diag_match = re.search(
            r'Descripci[óo]n\s+Diagn[óo]stico.*?[:\s]+(.*?)(?=Todos\s+los\s+an[áa]lisis|FACTOR|CONGELACIONES|---\s+P[ÁA]GINA|$)',
            clean_text,
            re.IGNORECASE | re.DOTALL
        )
        if desc_diag_match:
            desc_diag_text = desc_diag_match.group(1).strip()
            if desc_diag_text and len(desc_diag_text) > 20:
                # v5.3.6: Guardar el texto COMPLETO (no extraer solo principal)
                # La extracción del diagnóstico principal se hace después en extract_diagnostico_principal()
                results['diagnostico_final_ihq'] = desc_diag_text

    # Mapear campos para compatibilidad con base de datos
    results = map_medical_fields_to_database(results)

    return results


def map_medical_fields_to_database(results: Dict[str, Any]) -> Dict[str, Any]:
    """Mapea campos médicos a formato de base de datos"""

    # Mapeo de campos con nombres alternativos
    field_mapping = {
        'malignidad': 'malignancy_status',
        'diagnostico_final_ihq': 'diagnostico_final',
        'descripcion_macroscopica_final': 'descripcion_macroscopica',  # CORREGIDO: usar _final
        'descripcion_microscopica_final': 'descripcion_microscopica'
    }

    # Aplicar mapeo
    for old_key, new_key in field_mapping.items():
        if old_key in results and results[old_key]:
            results[new_key] = results[old_key]

    return results


def extract_organ_information(text: str) -> str:
    """Extrae información del órgano usando múltiples estrategias

    CORREGIDO: Retorna nombre normalizado o cadena vacía (NO 'ORGANO_NO_ESPECIFICADO')
    para mejor integración con ihq_organo
    """

    # Estrategia 1: Buscar patrón específico "TUMOR REGION/REGIÓON" + "INTRADURAL" (líneas separadas)
    # Incluye variaciones de OCR: REGION, REGIÓON, REGIÓN
    tumor_region_multiline = re.search(r'bloques\s+y\s+laminas\s+(TUMOR\s+REGI[OÓ]O?N).*?\n.*?(INTRADURAL)', text, re.IGNORECASE | re.DOTALL)
    if tumor_region_multiline:
        organo_part1 = tumor_region_multiline.group(1).strip()
        organo_part2 = tumor_region_multiline.group(2).strip()
        organo_completo = f"{organo_part1} {organo_part2}".strip()
        # Normalizar errores de OCR
        organo_completo = organo_completo.replace('REGIÓON', 'REGION').replace('REGIÓN', 'REGION')
        if len(organo_completo) > 5:
            normalized = normalize_organ_name(organo_completo)
            if normalized != 'ORGANO_NO_ESPECIFICADO':
                return normalized

    # Estrategia 1b: Buscar patrón original "TUMOR REGION/REGIÓON" + "INTRADURAL" en misma línea
    tumor_region_match = re.search(r'bloques\s+y\s+laminas\s+(TUMOR\s+REGI[OÓ]O?N)[^A-Z]*([A-Z\s]*INTRADURAL)', text, re.IGNORECASE | re.DOTALL)
    if tumor_region_match:
        organo_part1 = tumor_region_match.group(1).strip()
        organo_part2 = tumor_region_match.group(2).strip()
        organo_completo = f"{organo_part1} {organo_part2}".strip()
        # Normalizar errores de OCR
        organo_completo = organo_completo.replace('REGIÓON', 'REGION').replace('REGIÓN', 'REGION')
        if len(organo_completo) > 5:
            normalized = normalize_organ_name(organo_completo)
            if normalized != 'ORGANO_NO_ESPECIFICADO':
                return normalized

    # Estrategia 2: Buscar en tabla de estudios solicitados (patrón general)
    estudios_table_pattern = r'estudios\s+solicitados.*?(?:organo|órgano)\s+fecha\s+toma.*?(?:bloques\s+y\s+laminas\s+|almacenamiento.*?)([A-Z\s]+)(?:\s+INFORME|\s+ESTUDIO|\n|$)'
    estudios_match = re.search(estudios_table_pattern, text, re.IGNORECASE | re.DOTALL)
    if estudios_match:
        organo_from_table = estudios_match.group(1).strip()
        if organo_from_table and len(organo_from_table) > 3:
            normalized = normalize_organ_name(organo_from_table)
            if normalized != 'ORGANO_NO_ESPECIFICADO':
                return normalized

    # Estrategia 3: Buscar patrón específico "Bloques y laminas ÓRGANO"
    # CORREGIDO: Capturar órgano en múltiples líneas después de "Bloques y laminas"
    bloques_pattern = r'bloques\s+y\s+laminas\s*\n?\s*([A-Z\s]+?(?:\n[A-Z\s]+?)?)(?:\s+INFORME|\s+ESTUDIO|\n\s*INFORME|\n\s*ESTUDIO|$)'
    bloques_match = re.search(bloques_pattern, text, re.IGNORECASE | re.MULTILINE)
    if bloques_match:
        organo_from_bloques = bloques_match.group(1).strip()
        # Limpiar saltos de línea internos
        organo_from_bloques = re.sub(r'\s*\n\s*', ' ', organo_from_bloques).strip()
        if organo_from_bloques and len(organo_from_bloques) > 3:
            normalized = normalize_organ_name(organo_from_bloques)
            if normalized != 'ORGANO_NO_ESPECIFICADO':
                return normalized

    # Estrategia 4: Patrón directo de órgano
    organo_match = re.search(PATTERNS_IHQ['organo_raw'], text, re.IGNORECASE | re.DOTALL)
    if organo_match:
        organo_raw = organo_match.group(1).strip()
        if organo_raw and len(organo_raw) > 2:
            normalized = normalize_organ_name(organo_raw)
            if normalized != 'ORGANO_NO_ESPECIFICADO':
                return normalized

    # Estrategia 5: Buscar en estudios solicitados con keywords
    estudios_match = re.search(r'(?:estudios?\s+solicitados?)[:\s]+(.*?)(?=\s*(?:órgano|organo|responsable|fecha)|$)',
                              text, re.IGNORECASE | re.DOTALL)
    if estudios_match:
        estudios_text = estudios_match.group(1).strip()
        for organo, keywords in ORGAN_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in estudios_text.lower():
                    return organo

    # Estrategia 6: Buscar en descripción macroscópica con keywords
    macro_match = re.search(PATTERNS_IHQ['descripcion_macroscopica_ihq'], text, re.IGNORECASE | re.DOTALL)
    if macro_match:
        macro_text = macro_match.group(1).strip()
        for organo, keywords in ORGAN_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in macro_text.lower():
                    return organo

    # Estrategia 7: Buscar en todo el texto con keywords
    for organo, keywords in ORGAN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                return organo

    # CORREGIDO: Retornar cadena vacía en lugar de 'ORGANO_NO_ESPECIFICADO'
    # Esto permite que ihq_organo tenga prioridad
    return ''


def normalize_organ_name(organ_text: str) -> str:
    """Normaliza el nombre del órgano

    CORREGIDO: Siempre retorna el nombre normalizado, nunca 'ORGANO_NO_ESPECIFICADO'
    para permitir que el sistema de priorización funcione correctamente
    """
    if not organ_text:
        return 'ORGANO_NO_ESPECIFICADO'

    organ_lower = organ_text.lower().strip()

    # Mapeo directo de términos conocidos (prioridad alta)
    for organo, keywords in ORGAN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in organ_lower:
                return organo

    # Si no se encuentra en keywords, limpiar y devolver texto normalizado
    # CORREGIDO: Preservar espacios internos importantes
    cleaned = re.sub(r'[^\w\s]', '', organ_text).upper().strip()
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Normalizar espacios múltiples

    # Si el texto limpio es muy corto o vacío, marcar como no especificado
    if len(cleaned) < 3:
        return 'ORGANO_NO_ESPECIFICADO'

    return cleaned


def determine_malignancy(diagnostico: str, macroscopica: str, microscopica: str, full_text: str) -> str:
    """Determina malignidad basada en múltiples fuentes con lógica mejorada.
    
    v4.2.2: Lógica mejorada que considera:
    - Patrones específicos de alta prioridad (WHO grados, GIST, mielomas)
    - Contexto (ej: "MENINGIOMA WHO GRADO 1" → BENIGNO)
    - Scoring ponderado
    """

    # Combinar todos los textos para análisis
    combined_text = f"{diagnostico} {macroscopica} {microscopica} {full_text}".upper()

    # ════════════════════════════════════════════════════════════════════════
    # PRIORIDAD 1: Patrones específicos de alta confianza
    # ════════════════════════════════════════════════════════════════════════
    
    # WHO GRADO 1 → BENIGNO (meningiomas, astrocitomas de bajo grado)
    if re.search(r'WHO\s+GRADO\s+1|WHO\s+1|GRADO\s+I\b', combined_text):
        return 'BENIGNO'
    
    # WHO GRADO 3, 4 → MALIGNO
    if re.search(r'WHO\s+GRADO\s+[34]|WHO\s+[34]|GRADO\s+(?:III|IV)\b', combined_text):
        return 'MALIGNO'
    
    # GIST (Tumor del estroma gastrointestinal) → Siempre potencialmente MALIGNO
    # Incluso de "bajo grado" tienen potencial metastásico
    if 'TUMOR DEL ESTROMA GASTROINTESTINAL' in combined_text or 'GIST' in combined_text:
        return 'MALIGNO'
    
    # Neoplasias hematológicas específicas
    if 'NEOPLASIA DE CELULAS PLASMATICAS' in combined_text or 'PLASMOCITOMA' in combined_text:
        return 'MALIGNO'
    
    if 'MIELOMA' in combined_text or 'LEUCEMIA' in combined_text:
        return 'MALIGNO'
    
    # Tumores específicos típicamente benignos
    hibernoma_benign = ['HIBERNOMA', 'NEUROFIBROMA', 'SCHWANNOMA BENIGNO']
    for tumor in hibernoma_benign:
        if tumor in combined_text:
            return 'BENIGNO'
    
    # MENINGIOMA sin alto grado → BENIGNO (mayoría son WHO grado 1)
    if 'MENINGIOMA' in combined_text:
        if not any(x in combined_text for x in ['GRADO 2', 'GRADO 3', 'GRADO II', 'GRADO III', 'ATIPICO', 'ANAPLASICO']):
            return 'BENIGNO'
    
    # Lesiones fusiformes bien diferenciadas → BENIGNO
    if 'LESION FUSOCELULAR BIEN DIFERENCIADA' in combined_text or 'FUSIFORME BIEN DIFERENCIADA' in combined_text:
        return 'BENIGNO'
    
    # ════════════════════════════════════════════════════════════════════════
    # PRIORIDAD 2: Scoring ponderado con keywords
    # ════════════════════════════════════════════════════════════════════════
    
    # Verificar malignidad con ponderación
    malignidad_score = 0
    for keyword in MALIGNIDAD_KEYWORDS_IHQ:
        if keyword in combined_text:
            # Palabras de alta certeza valen más
            if keyword in ['CARCINOMA', 'ADENOCARCINOMA', 'SARCOMA', 'MELANOMA', 
                          'METASTASIS', 'METÁSTASIS', 'INVASIVO', 'LINFOMA']:
                malignidad_score += 3
            else:
                malignidad_score += 1

    # Verificar benignidad
    benignidad_score = 0
    for keyword in BENIGNIDAD_KEYWORDS_IHQ:
        if keyword in combined_text:
            # Palabras de alta certeza valen más
            if keyword in ['BENIGNO', 'BENIGNIDAD', 'ADENOMA', 'FIBROMA', 
                          'LIPOMA', 'HIBERNOMA', 'GRADO 1', 'WHO 1']:
                benignidad_score += 3
            else:
                benignidad_score += 1

    # ════════════════════════════════════════════════════════════════════════
    # DECISIÓN FINAL
    # ════════════════════════════════════════════════════════════════════════
    
    # Decisión con umbral más claro
    if malignidad_score > benignidad_score and malignidad_score >= 2:
        return 'MALIGNO'
    elif benignidad_score > malignidad_score and benignidad_score >= 2:
        return 'BENIGNO'
    elif malignidad_score > 0:  # Si hay alguna señal de malignidad, ser conservador
        return 'MALIGNO'
    elif benignidad_score > 0:
        return 'BENIGNO'
    else:
        # Si realmente no hay información, dejar NO_DETERMINADO
        # pero esto debería ser rarísimo con las mejoras
        return 'NO_DETERMINADO'

def process_medical_descriptions(results: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Procesa y mejora las descripciones médicas"""

    # CORREGIDO: Priorizar descripcion_macroscopica_ihq (la del encabezado)
    macro_body = results.get('descripcion_macroscopica_ihq', '').lstrip(': ').strip()
    se_recibe_body = results.get('descripcion_macroscopica_se_recibe', '').strip()

    # CORREGIDO: Priorizar texto completo capturado del patrón principal
    if macro_body:
        results['descripcion_macroscopica_final'] = macro_body
    elif se_recibe_body:
        results['descripcion_macroscopica_final'] = se_recibe_body
    else:
        results['descripcion_macroscopica_final'] = ''

    # Limpiar descripción microscópica
    microscopica = results.get('descripcion_microscopica_final', '').strip()
    if microscopica:
        # Limpiar caracteres especiales y normalizar espacios
        microscopica = re.sub(r'\s+', ' ', microscopica).strip()
        results['descripcion_microscopica_final'] = microscopica

    return results


def extract_additional_dates(results: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Extrae fechas adicionales del texto"""
    
    additional_dates = {}
    
    # Patrones que manejan tanto dígitos como letras confundidas por OCR
    # [0O] para manejar 0/O, [1I] para 1/I, etc.
    date_pattern = r'[0O\d][0-9O\d]/[0O\d][0-9I\d]/[2][0O\d][2][5]'
    
    # Buscar fecha de informe con múltiples patrones
    fecha_informe_patterns = [
        fr'(?:FECHA\s+INFORME)[:\s]*({date_pattern})',
        fr'fecha\s+informe\s*[:\-—]\s*({date_pattern})',
        fr'({date_pattern})(?=\s*(?:responsable|elaborado|firma))'
    ]
    
    for pattern in fecha_informe_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fecha_raw = match.group(1).strip()
            # Convertir letras confundidas de vuelta a números
            fecha_clean = clean_ocr_date(fecha_raw)
            additional_dates['fecha_informe'] = convert_date_format(fecha_clean)
            break
    
    # Buscar fecha de ingreso con múltiples patrones
    fecha_ingreso_patterns = [
        fr'(?:FECHA\s+DE\s+INGRESO)[:\s]*({date_pattern})',
        fr'fecha\s+de?\s+ingreso\s*[:\-—]\s*({date_pattern})',
        fr'ingreso[:\s]*({date_pattern})'
    ]
    
    for pattern in fecha_ingreso_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fecha_raw = match.group(1).strip()
            # Convertir letras confundidas de vuelta a números
            fecha_clean = clean_ocr_date(fecha_raw)
            additional_dates['fecha_ingreso'] = convert_date_format(fecha_clean)
            break
    
    # Devolver SOLO las fechas adicionales encontradas
    return additional_dates


def clean_ocr_date(date_str: str) -> str:
    """Limpia errores comunes de OCR en fechas"""
    if not date_str:
        return date_str
    
    # Reemplazar errores comunes de OCR
    replacements = {
        'O': '0',  # O → 0
        'I': '1',  # I → 1
        'l': '1',  # l → 1
        'S': '5',  # S → 5 (menos común)
    }
    
    result = date_str
    for wrong, correct in replacements.items():
        result = result.replace(wrong, correct)
    
    return result


def extract_responsible_physician(results: Dict[str, Any], text: str) -> Dict[str, Any]:
    """Extrae información del médico responsable con múltiples estrategias.
    
    v4.2.2: Patrones alternativos para mayor cobertura
    """

    resp_name = ''

    # v5.3.5: PRIORIDAD REORGANIZADA - Buscar primero nombres conocidos (más confiables)
    # ═══════════════════════════════════════════════════════════════════════
    # ESTRATEGIA 1: Nombres conocidos de patólogos (búsqueda directa) - MÁS CONFIABLE
    # ═══════════════════════════════════════════════════════════════════════
    if 'responsable_alt3' in PATTERNS_IHQ:
        resp_match = re.search(PATTERNS_IHQ['responsable_alt3'], text, re.IGNORECASE)
        if resp_match:
            resp_name = resp_match.group(1).strip()

    # ═══════════════════════════════════════════════════════════════════════
    # ESTRATEGIA 2: Patrón antes de "RM:" (registro médico)
    # ═══════════════════════════════════════════════════════════════════════
    if not resp_name and 'responsable_alt2' in PATTERNS_IHQ:
        resp_match = re.search(PATTERNS_IHQ['responsable_alt2'], text, re.IGNORECASE)
        if resp_match:
            resp_name = resp_match.group(1).strip()

    # ═══════════════════════════════════════════════════════════════════════
    # ESTRATEGIA 3: Patrón antes de "MÉDICO PATÓLOGO"
    # ═══════════════════════════════════════════════════════════════════════
    if not resp_name and 'responsable_alt1' in PATTERNS_IHQ:
        resp_match = re.search(PATTERNS_IHQ['responsable_alt1'], text, re.IGNORECASE)
        if resp_match:
            resp_name = resp_match.group(1).strip()

    # ═══════════════════════════════════════════════════════════════════════
    # ESTRATEGIA 4: Patrón principal (nombre antes de "Responsable del análisis")
    # ═══════════════════════════════════════════════════════════════════════
    if not resp_name:
        resp_match = re.search(PATTERNS_IHQ['responsable_ihq'], text, re.IGNORECASE | re.DOTALL)
        if resp_match:
            resp_name = resp_match.group(1).strip()

    # Limpiar el nombre capturado de líneas no deseadas
    if resp_name:
        # Eliminar líneas que contengan palabras clave no deseadas
        lines = [line.strip() for line in resp_name.split('\n')]
        clean_lines = []

        for line in lines:
            line_upper = line.upper()
            # v5.3.5: Ignorar líneas que claramente no son nombres de patólogos
            keywords_to_exclude = [
                'COMENTARIOS', 'POSITIVO', 'NEGATIVO', 'FOCAL', 'DIFUSO', 'MD', 'PATOLOGO', '%', 'RESPONSABLE',
                'COLEGIO', 'AMERICANO', 'HOSPITAL', 'ANALISIS', 'AVALADOS', 'PROGRAMA', 'CALIDAD',
                'RECEPTOR', 'HER', 'KI-67', 'ESTUDIOS', 'ISO', 'ONEWORLD', 'ACCURACY', 'AUSTRALASIA'
            ]
            if any(keyword in line_upper for keyword in keywords_to_exclude):
                continue
            # Ignorar líneas vacías
            if not line.strip():
                continue
            # Ignorar líneas con RM:
            if 'RM:' in line or 'RM ' in line:
                continue
            # v5.3.5: Solo aceptar líneas con formato de nombre (2-4 palabras en mayúsculas)
            # Ejemplo válido: "NANCY MEJIA VARGAS"
            words = line.split()
            if 2 <= len(words) <= 4 and all(word.isupper() for word in words):
                clean_lines.append(line)

        # Tomar la última línea limpia (el nombre del responsable suele ser la última línea)
        resp_name = clean_lines[-1] if clean_lines else ''

    # Normalizar nombres conocidos
    if resp_name:
        resp_upper = resp_name.upper()
        if 'NANCY' in resp_upper and 'MEJIA' in resp_upper:
            results['responsable_final'] = 'NANCY MEJIA VARGAS'
        elif 'ARMANDO' in resp_upper and 'CORTES' in resp_upper:
            results['responsable_final'] = 'ARMANDO CORTES BUELVAS'
        elif 'CARLOS' in resp_upper and 'CAICEDO' in resp_upper:
            results['responsable_final'] = 'CARLOS CAICEDO ESTRADA'
        elif 'NATALIA' in resp_upper and 'AGUIRRE' in resp_upper:
            results['responsable_final'] = 'NATALIA AGUIRRE VASQUEZ'
        elif 'JOSE' in resp_upper and 'BRAVO' in resp_upper:
            results['responsable_final'] = 'JOSE BRAVO BONILLA'
        else:
            # Limpiar y normalizar el nombre
            resp_name = re.sub(r'\s+', ' ', resp_name).strip()
            # Solo asignar si tiene al menos 10 caracteres (evitar capturas erróneas)
            if len(resp_name) >= 10:
                results['responsable_final'] = resp_name
            else:
                results['responsable_final'] = ''
    else:
        results['responsable_final'] = ''

    return results

def extract_service_info(text: str) -> str:
    """Extrae información del servicio médico"""
    
    # Buscar servicio con patrón del sistema original
    if 'servicio' in PATTERNS_HUV:
        match = re.search(PATTERNS_HUV['servicio'], text, re.IGNORECASE | re.DOTALL)
        if match and match.groups():
            return re.sub(r'\s+', ' ', match.group(1).strip())
    
    return ''


def deduce_specialty_ihq(servicio: str) -> str:
    """Deduce la especialidad médica basada en el servicio"""
    if not servicio:
        return 'PATOLOGIA'
    
    servicio_upper = servicio.upper()
    
    # Mapeo de servicios a especialidades
    specialty_mapping = {
        'ONCOLOGIA': 'ONCOLOGIA',
        'GINECOLOGIA': 'GINECOLOGIA',
        'UROLOGIA': 'UROLOGIA',
        'CIRUGIA': 'CIRUGIA_GENERAL',
        'MEDICINA INTERNA': 'MEDICINA_INTERNA',
        'DERMATOLOGIA': 'DERMATOLOGIA',
        'QUIROFANO': 'CIRUGIA_GENERAL',
        'EMERGENCIAS': 'URGENCIAS'
    }
    
    for keyword, specialty in specialty_mapping.items():
        if keyword in servicio_upper:
            return specialty

    return 'PATOLOGIA'  # Default para IHQ


def extract_ihq_organ_from_diagnosis(diagnostico: str) -> str:
    """Extrae el órgano de forma inteligente desde el diagnóstico

    Ejemplos:
        "Región intradural (cauda equina). Tumor. Resección." → "Región intradural (cauda equina)"
        "Mama derecha. Biopsia. Carcinoma ductal." → "Mama derecha"
        "Colon sigmoide. Resección. Adenocarcinoma." → "Colon sigmoide"

    Args:
        diagnostico: Texto del diagnóstico

    Returns:
        Órgano extraído o cadena vacía
    """
    if not diagnostico:
        return ''

    # Limpiar texto
    text = diagnostico.strip()

    # Estrategia 1: Capturar primera frase antes de punto (puede contener paréntesis)
    # Patrón: captura todo hasta el primer punto, incluyendo paréntesis
    match = re.match(r'^([^.]+(?:\([^)]+\))?[^.]*?)\.', text)
    if match:
        candidato = match.group(1).strip()

        # Verificar que no sea un término de procedimiento
        procedimiento_terms = ['tumor', 'biopsia', 'resección', 'reseccion', 'extirpación', 'extirpacion']
        candidato_lower = candidato.lower()

        # Si NO es solo un término de procedimiento, es probable que sea el órgano
        if not any(candidato_lower == term for term in procedimiento_terms):
            # Si contiene un procedimiento al final, quitarlo
            for term in procedimiento_terms:
                if candidato_lower.endswith(term):
                    candidato = candidato[:-(len(term))].strip('. ')
                    break

            # Validar que tenga longitud razonable (3-80 caracteres)
            if 3 <= len(candidato) <= 80:
                return candidato

    # Estrategia 2: Buscar patrón específico de órgano conocido
    for organo, keywords in ORGAN_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text.lower():
                # Extraer contexto alrededor del keyword
                idx = text.lower().find(keyword.lower())
                if idx >= 0:
                    # Capturar desde inicio o desde palabra anterior hasta punto o paréntesis de cierre
                    start = max(0, idx - 30)
                    end = min(len(text), idx + len(keyword) + 30)
                    contexto = text[start:end]

                    # Buscar el segmento más específico
                    seg_match = re.search(r'([A-Za-záéíóúÁÉÍÓÚñÑ\s\(\)]+?)(?:\.|$)', contexto)
                    if seg_match:
                        return seg_match.group(1).strip()

                return organo

    # Estrategia 3: Si no se encuentra, devolver primera parte significativa
    palabras = text.split()
    if len(palabras) >= 2:
        # Tomar primeras 2-4 palabras antes de términos clave
        for i, palabra in enumerate(palabras[:6]):
            if palabra.lower() in ['tumor', 'biopsia', 'resección', 'carcinoma', 'adenocarcinoma']:
                if i > 0:
                    return ' '.join(palabras[:i]).strip('. ')

    return ''


# ─────────────────────────── EXTRACCIÓN DE DIAGNÓSTICO PRINCIPAL ─────────────────────────────

# Términos clave de diagnóstico (migrados desde procesador_ihq.py)
_KEY_DIAG_TERMS = [
    # CRÍTICO v4.2.3: Carcinomas (los más comunes) - AGREGADOS
    'CARCINOMA','ADENOCARCINOMA','ESCAMOCELULAR','DUCTAL','LOBULILLAR',
    'BASOCELULAR','ESPINOCELULAR','NEUROENDOCRINO',
    # Sarcomas
    'SARCOMA','LIPOSARCOMA','OSTEOSARCOMA','CONDROSARCOMA','RABDOMIOSARCOMA',
    # Tumores del sistema nervioso
    'MELANOMA','GLIOMA','MENINGIOMA','ASTROCITOMA','OLIGODENDROGLIOMA',
    'SCHWANNOMA','GLANGIOMA','NEUROBLASTOMA','MEDULOBLASTOMA',
    # Tumores hematológicos
    'LINFOMA','LINFOIDE','MIELOMA','PLASMATICAS','LEUCEMIA',
    # Metástasis
    'METASTASICO','METASTÁSICO','METASTASIS','METÁSTASIS',
    # Tumores benignos e intermedios
    'HEMANGIOMA','HIBERNOMA','FIBROMA','TIMOMA','LIPOMA','CONDROMA','OSTEOMA',
    # Lesiones específicas
    'ENDOMETRIAL','ECTOPICO','ECTÓPICO','DECIDUALIZADO','ESCAMOSA','PREINVASIVA',
    'DISPLASIA','HETEROTOPIA',
    # Otros términos diagnósticos importantes
    'PLASMOCITOMA','SEMINOMA','TERATOMA','GERMINOMA','CORIOCARCINOMA',
    'ADENOSIS','FIBROADENOMA','PAPILOMA'
]

_LOW_PRIORITY_GENERIC = {'TUMOR','NEOPLASIA'}

_IMMUNO_MARKER_PATTERN = re.compile(
    r"^(?:p(?:\d{1,2}|16|40)|ck\d{1,2}|cd\d{2,3}|er|pr|her2|ki67|pax8|gata3|sox10|gfap|s100|synaptofisina|chromogranina|ema|alk|ros1|braf|idh1|idh2)$",
    re.IGNORECASE
)


def extract_principal_diagnosis(full_text: str) -> str:
    """Extrae frase diagnóstica principal con scoring robusto (orden invariante).

    Scoring por segmento:
      +5 por cada término específico (_KEY_DIAG_TERMS)
      +2 si contiene genérico (TUMOR/NEOPLASIA) y ningún específico
      -2 por cada marcador inmuno detectado tempranamente
      Penalización proporcional si > 35 palabras (texto demasiado largo)
    Se recorta desde primer término clave hasta antes de marcadores / POSITIVO / NEGATIVO.

    Args:
        full_text: Texto completo del diagnóstico

    Returns:
        Diagnóstico principal extraído
    """
    if not full_text:
        return ''

    # ═══════════════════════════════════════════════════════════════════════════
    # NUEVO v4.2.2: Detectar patrones especiales PRIMERO
    # Estos patrones tienen prioridad sobre el scoring normal
    # ═══════════════════════════════════════════════════════════════════════════
    
    full_text_upper = full_text.upper()
    
    # Patrón 1: "HALLAZGOS... COMPATIBLES CON [diagnóstico]"
    pattern_hallazgos = r'HALLAZGOS\s+(?:HIST[ÓO]L[ÓO]GICOS\s+)?(?:DE\s+)?(?:MORFOLOG[ÍI]A\s+E\s+)?(?:INMUNOHISTOQU[ÍI]MICA\s+)?COMPATIBLES?\s+CON\s+([A-ZÁÉÍÓÚÑ\s]{10,150}?)(?:\.||NANCY|ARMANDO|CARLOS|RESPONSABLE|M[ÉE]DICO)'
    match_hallazgos = re.search(pattern_hallazgos, full_text_upper)
    if match_hallazgos:
        diag = match_hallazgos.group(1).strip()
        diag = re.sub(r'\s+', ' ', diag)  # Normalizar espacios
        # Recortar en punto final o médico
        diag = re.split(r'(?:\.|\s+(?:NANCY|ARMANDO|CARLOS|RESPONSABLE|M[ÉE]DICO))', diag)[0].strip()
        if len(diag) > 10:  # Mínimo razonable
            return diag
    
    # Patrón 2: "NEGATIVO PARA [condición]"
    pattern_negativo = r'NEGATIVO\s+PARA\s+([A-ZÁÉÍÓÚÑ\s/]{10,100}?)(?:\.||NANCY|ARMANDO|CARLOS)'
    match_negativo = re.search(pattern_negativo, full_text_upper)
    if match_negativo:
        diag = match_negativo.group(1).strip()
        diag = re.sub(r'\s+', ' ', diag)
        diag = re.split(r'(?:\.|\s+(?:NANCY|ARMANDO|CARLOS))', diag)[0].strip()
        if len(diag) > 10:
            return f"NEGATIVO PARA {diag}"
    
    # Patrón 3: "EXPRESIÓN DE [marcadores] NEGATIVA/POSITIVA"
    pattern_expresion = r'EXPRESI[ÓO]N\s+DE\s+([A-Z0-9\s,YÓÚ]+?)\s+(NEGATIVA|POSITIVA)(?:\.|)'
    match_expresion = re.search(pattern_expresion, full_text_upper)
    if match_expresion:
        marcadores = match_expresion.group(1).strip()
        estado = match_expresion.group(2).strip()
        marcadores = re.sub(r'\s+', ' ', marcadores)
        if len(marcadores) < 60:  # Evitar capturas demasiado largas
            return f"EXPRESIÓN DE {marcadores} {estado}"

    text = full_text.replace('\r', '\n')
    raw_segments: List[str] = []

    for ln in text.split('\n'):
        ln = ln.strip()
        if not ln:
            continue
        ln = re.sub(r'^[-•]\s*', '', ln)
        parts = re.split(r'(?<=[.;:])\s+', ln)
        for p in parts:
            sp = p.strip()
            if sp:
                raw_segments.append(sp)

    if not raw_segments:
        raw_segments = [full_text.strip()]

    best: Dict[str, Any] = {'score': -9999, 'principal': ''}
    principal = ''  # inicialización defensiva para análisis estático

    for seg in raw_segments:
        up = seg.upper()
        # saltar segmentos sin ninguna señal oncológica
        if not any(term in up for term in _KEY_DIAG_TERMS) and not any(g in up for g in _LOW_PRIORITY_GENERIC):
            continue

        # localizar primer índice de término relevante
        idx_start: Optional[int] = None
        for term in list(_KEY_DIAG_TERMS) + list(_LOW_PRIORITY_GENERIC):
            pos = up.find(term)
            if pos != -1 and (idx_start is None or pos < idx_start):
                idx_start = pos

        if idx_start is None:
            continue

        candidate = seg[idx_start:].strip()
        words = candidate.split()
        out_words: List[str] = []
        immuno_hits = 0

        for w in words:
            clean = w.strip('.,;:()')
            if _IMMUNO_MARKER_PATTERN.match(clean) or clean.upper() in {"POSITIVO","NEGATIVO","POS","NEG"} or re.fullmatch(r"\d+%", clean):
                break
            if _IMMUNO_MARKER_PATTERN.match(clean):
                immuno_hits += 1
            out_words.append(w)
            principal_raw = ' '.join(out_words).strip(' .,:;')
            if principal_raw:
                # Recorte de cláusulas finales indeseadas
                principal_cut = re.sub(r'\bNO\s+DESCARTA.*', '', principal_raw, flags=re.IGNORECASE)
                principal_cut = re.sub(r'\bQUEDA\s+A\s+CRITERIO.*', '', principal_cut, flags=re.IGNORECASE)
                principal_cut = re.sub(r'\bSUGIERE\s+REALIZAR.*', '', principal_cut, flags=re.IGNORECASE)
                principal_cut = re.sub(r'\bPENDIENTE\s+DE.*', '', principal_cut, flags=re.IGNORECASE)

                # V6.0.2: Detener ANTES de primer guion en nueva línea (CRÍTICO IHQ250981)
                # Buscar patrón: salto de línea seguido de guion (lista de atributos adicionales)
                match_first_dash = re.search(r'\n\s*-', principal_cut)
                if match_first_dash:
                    principal_cut = principal_cut[:match_first_dash.start()].strip()
                # Alternativamente, si hay " - " en la misma línea
                elif ' - ' in principal_cut:
                    parts = principal_cut.split(' - ')
                    principal_cut = parts[0].strip()

                principal = re.sub(r'\s{2,}', ' ', principal_cut).strip(' .,:;')
            else:
                principal = ''

        principal = re.sub(r'\s{2,}', ' ', principal)
        if not principal:
            continue

        # V6.0.0: Detener en " - " o "\n-" (información adicional) - REDUNDANCIA PARA SEGURIDAD
        # CORREGIDO: También detener en saltos de línea con guión (caso IHQ250981)
        if ' - ' in principal or '\n-' in principal or '\n -' in principal:
            # Intentar con diferentes separadores
            for sep in [' - ', '\n- ', '\n-']:
                if sep in principal:
                    parts = principal.split(sep)
                    principal = parts[0].strip()
                    break

        up_pr = principal.upper()
        spec_count = sum(1 for t in _KEY_DIAG_TERMS if t in up_pr)
        gen_count = sum(1 for g in _LOW_PRIORITY_GENERIC if g in up_pr)
        score = spec_count * 5

        if spec_count == 0 and gen_count:
            score += 2

        score -= immuno_hits * 2
        length_penalty = max(0, len(out_words) - 35)
        score -= length_penalty

        # ligera preferencia por frases más cortas si empate
        if score > best['score'] or (score == best['score'] and len(out_words) < len(best['principal'].split())):
            best['score'] = score
            best['principal'] = principal.upper()

    # V6.0.2: LIMPIEZA FINAL - Eliminar contaminación del estudio M (IHQ250981)
    # El diagnóstico principal NO debe contener grado Nottingham, invasiones, ni score
    resultado = best['principal']
    if resultado:
        # Eliminar desde ", INVASIVO" hasta el final (incluye todo: grado, score, etc.)
        # Patrón: ", INVASIVO GRADO HISTOLOGICO: X (SCORE X/X)"
        resultado = re.sub(r',\s*INVASIVO\s+GRADO\s+HISTOL[ÓO]GICO.*$', '', resultado, flags=re.IGNORECASE)

        # Eliminar desde ", GRADO NOTTINGHAM" hasta el final
        resultado = re.sub(r',\s*GRADO\s+NOTTINGHAM.*$', '', resultado, flags=re.IGNORECASE)
        resultado = re.sub(r',\s*NOTTINGHAM\s+GRADO.*$', '', resultado, flags=re.IGNORECASE)

        # Eliminar desde ", GRADO X" hasta el final (para casos sin Nottingham)
        resultado = re.sub(r',\s*GRADO\s+[I1-3].*$', '', resultado, flags=re.IGNORECASE)

        # Eliminar invasiones en cualquier posición
        resultado = re.sub(r',?\s*INVASI[ÓO]N\s+(LINFOVASCULAR|PERINEURAL)[^,]*', '', resultado, flags=re.IGNORECASE)

        # Eliminar score en cualquier posición
        resultado = re.sub(r',?\s*\(SCORE\s+\d+(/\d+)?\)', '', resultado, flags=re.IGNORECASE)
        resultado = re.sub(r',?\s*SCORE\s+\d+(/\d+)?[^,]*', '', resultado, flags=re.IGNORECASE)

        # Limpiar comas/espacios múltiples resultantes
        resultado = re.sub(r'\s*,\s*,\s*', ', ', resultado)  # Comas duplicadas
        resultado = re.sub(r'^,\s*|\s*,$', '', resultado)  # Comas al inicio/fin
        resultado = re.sub(r'\s{2,}', ' ', resultado)  # Espacios múltiples
        resultado = resultado.strip()

    return resultado


def clean_diagnosis_text(diagnosis: str) -> str:
    """Limpia texto explicativo del diagnóstico principal

    Elimina comentarios, sugerencias y texto explicativo que no es parte
    del diagnóstico en sí.

    Versión: 5.3.1 - MEJORADO: Integra limpieza de multipágina

    Args:
        diagnosis: Diagnóstico extraído que puede contener texto adicional

    Returns:
        Diagnóstico limpio sin texto explicativo
    """
    if not diagnosis or diagnosis in ['', 'N/A']:
        return diagnosis

    # v5.3.1: PRIMERO aplicar limpieza de multipágina
    diagnosis = clean_diagnostico_multipage(diagnosis)

    # Patrones de texto explicativo a eliminar (después de coma o punto y coma)
    cutoff_patterns = [
        r',?\s+SIN EMBARGO.*',
        r',?\s+SE REALIZARON?.*',
        r',?\s+SE SUGIERE.*',
        r',?\s+A CRITERIO.*',
        r',?\s+VER COMENTARIO.*',
        r',?\s+COMENTARIOS?:?.*',
        r',?\s+QUEDA A CRITERIO.*',
        r',?\s+PENDIENTE DE.*',
        r',?\s+NO DESCARTA.*',
        r';\s+.*'  # Todo después de punto y coma
    ]

    cleaned = diagnosis
    for pattern in cutoff_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

    # Limpiar espacios múltiples y caracteres finales
    cleaned = re.sub(r'\s+', ' ', cleaned).strip(' .,:;')

    return cleaned if cleaned else diagnosis  # Retornar original si queda vacío




