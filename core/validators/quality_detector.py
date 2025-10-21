#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Calidad de Registros para Sistema de Gestión Oncológica HUV

Este módulo evalúa la calidad de los registros extraídos y determina
automáticamente si necesitan revisión por IA.

Versión: 4.2.4
Fecha: 5 de octubre de 2025
"""
import re
import logging
from typing import Dict, List, Any, Tuple


def evaluate_record_quality(record: Dict[str, Any]) -> Dict[str, Any]:
    """Evalúa la calidad de un registro y determina si necesita revisión IA
    
    Args:
        record: Diccionario con los datos del registro extraído
        
    Returns:
        Dict con:
        - score_total: Puntuación de calidad (0-100)
        - needs_ia_review: Boolean indicando si necesita IA
        - problems: Lista de problemas detectados
        - confidence: Nivel de confianza (HIGH/MEDIUM/LOW)
    """
    
    problems = []
    needs_ia = False
    
    # Obtener campos críticos
    diagnostico_principal = record.get('Diagnostico Principal', '')
    descripcion_diagnostico = record.get('Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)', '')
    descripcion_micro = record.get('Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)', '')
    malignidad = record.get('Malignidad', '')
    factor_pronostico = record.get('Factor pronostico', '')
    
    # === CRITERIO 1: Diagnóstico Principal Vacío con Descripción ===
    if (not diagnostico_principal or diagnostico_principal in ['N/A', '', 'None']) and descripcion_diagnostico and len(descripcion_diagnostico) > 50:
        problems.append({
            'tipo': 'DIAGNÓSTICO_VACÍO_CON_DESCRIPCIÓN',
            'severidad': 'CRÍTICO',
            'descripcion': 'Diagnóstico principal vacío pero hay descripción diagnóstico completa'
        })
        needs_ia = True
    
    # === CRITERIO 2: Diagnóstico Contiene Texto Explicativo ===
    if diagnostico_principal and diagnostico_principal not in ['N/A', '']:
        keywords_explicativos = ['SIN EMBARGO', 'SE REALIZARON', 'SE SUGIERE', 'A CRITERIO', 'VER COMENTARIO', 'QUEDA A CRITERIO']
        if any(kw in diagnostico_principal.upper() for kw in keywords_explicativos):
            problems.append({
                'tipo': 'DIAGNÓSTICO_CONTIENE_EXPLICACIÓN',
                'severidad': 'ALTO',
                'descripcion': 'Diagnóstico incluye texto explicativo que debería estar en comentarios'
            })
            needs_ia = True
    
    # === CRITERIO 3: Diagnóstico Muy Corto ===
    if diagnostico_principal and diagnostico_principal not in ['N/A', '']:
        keywords_validos_cortos = ['BENIGNO', 'MALIGNO', 'TUMOR', 'NEOPLASIA', 'GIST', 'MELANOMA']
        if len(diagnostico_principal) < 10 and diagnostico_principal.upper() not in keywords_validos_cortos:
            problems.append({
                'tipo': 'DIAGNÓSTICO_MUY_CORTO',
                'severidad': 'MEDIO',
                'descripcion': f'Diagnóstico muy corto ({len(diagnostico_principal)} caracteres), puede estar incompleto'
            })
            needs_ia = True
    
    # === CRITERIO 4: Diagnóstico = Descripción Completa ===
    if diagnostico_principal and descripcion_diagnostico:
        if diagnostico_principal == descripcion_diagnostico and len(diagnostico_principal) > 200:
            problems.append({
                'tipo': 'DIAGNÓSTICO_SIN_EXTRAER',
                'severidad': 'ALTO',
                'descripcion': 'Diagnóstico principal es igual a descripción completa, no está extraído correctamente'
            })
            needs_ia = True
    
    # === CRITERIO 5: Malignidad NO_DETERMINADO ===
    if malignidad == 'NO_DETERMINADO':
        problems.append({
            'tipo': 'MALIGNIDAD_NO_DETERMINADA',
            'severidad': 'ALTO',
            'descripcion': 'Malignidad no determinada, requiere análisis manual'
        })
        needs_ia = True
    
    # === CRITERIO 6: Factor Pronóstico Vacío pero Mencionado ===
    if (not factor_pronostico or factor_pronostico in ['N/A', '']) and descripcion_micro:
        keywords_fp = ['KI-67', 'KI67', 'P53', 'ÍNDICE DE PROLIFERACIÓN', 'SCORE', 'GRADO']
        if any(kw in descripcion_micro.upper() for kw in keywords_fp):
            problems.append({
                'tipo': 'FACTOR_PRONÓSTICO_NO_EXTRAÍDO',
                'severidad': 'MEDIO',
                'descripcion': 'Factor pronóstico vacío pero se menciona en descripción microscópica'
            })
            # No marcar needs_ia automáticamente, es opcional
    
    # === CRITERIO 7: Biomarcadores Todos Vacíos ===
    biomarcadores_campos = ['IHQ_HER2', 'IHQ_KI-67', 'IHQ_RECEPTOR_ESTROGENOS', 'IHQ_RECEPTOR_PROGESTERONA']
    biomarcadores_vacios = all(not record.get(campo) or record.get(campo) in ['N/A', '', 'None'] for campo in biomarcadores_campos)
    
    if biomarcadores_vacios and descripcion_micro:
        keywords_ihq = ['INMUNOHISTOQUÍMICA', 'INMUNOHISTOQUIMICA', 'IHQ', 'HER2', 'KI-67', 'RE:', 'RP:']
        if any(kw in descripcion_micro.upper() for kw in keywords_ihq):
            problems.append({
                'tipo': 'BIOMARCADORES_NO_EXTRAÍDOS',
                'severidad': 'BAJO',
                'descripcion': 'Biomarcadores vacíos pero se mencionan en descripción microscópica'
            })
            # No marcar needs_ia automáticamente para este caso
    
    # === CRITERIO 8: Campos Demográficos Vacíos ===
    campos_demograficos = ['Primer nombre', 'Edad', 'Genero']
    for campo in campos_demograficos:
        if not record.get(campo) or record.get(campo) in ['N/A', '', 'None']:
            problems.append({
                'tipo': 'CAMPO_DEMOGRÁFICO_VACÍO',
                'severidad': 'CRÍTICO',
                'descripcion': f'Campo demográfico crítico vacío: {campo}'
            })
            needs_ia = True  # Campos demográficos son críticos
    
    # === CALCULAR SCORE DE CALIDAD ===
    score = calculate_quality_score(record, problems)
    
    # === DETERMINAR NIVEL DE CONFIANZA ===
    if score >= 95 and len(problems) == 0:
        confidence = 'HIGH'
    elif score >= 80 and len([p for p in problems if p['severidad'] == 'CRÍTICO']) == 0:
        confidence = 'MEDIUM'
    else:
        confidence = 'LOW'
    
    return {
        'score_total': score,
        'needs_ia_review': needs_ia,
        'problems': problems,
        'confidence': confidence,
        'problem_count': len(problems),
        'critical_problems': len([p for p in problems if p['severidad'] == 'CRÍTICO']),
        'recommendation': 'REVISAR_CON_IA' if needs_ia else 'ACEPTAR_DIRECTO'
    }


def calculate_quality_score(record: Dict[str, Any], problems: List[Dict]) -> float:
    """Calcula score de calidad basado en completitud de campos
    
    Args:
        record: Diccionario con datos del registro
        problems: Lista de problemas detectados
        
    Returns:
        Score de 0-100
    """
    
    # Campos críticos (peso 40%)
    campos_criticos = {
        'Numero de caso': record.get('Numero de caso'),
        'Primer nombre': record.get('Primer nombre'),
        'Edad': record.get('Edad'),
        'Genero': record.get('Genero'),
        'Diagnostico Principal': record.get('Diagnostico Principal'),
        'Malignidad': record.get('Malignidad')
    }
    
    criticos_ok = sum(1 for v in campos_criticos.values() if v and v not in ['N/A', '', 'None'])
    score_criticos = (criticos_ok / len(campos_criticos)) * 40
    
    # Campos importantes (peso 30%)
    campos_importantes = {
        'EPS': record.get('EPS'),
        'Organo': record.get('Organo'),
        'Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)': record.get('Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)'),
        'Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)': record.get('Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)'),
        'Descripcion macroscopica': record.get('Descripcion macroscopica')
    }
    
    importantes_ok = sum(1 for v in campos_importantes.values() if v and v not in ['N/A', '', 'None'])
    score_importantes = (importantes_ok / len(campos_importantes)) * 30
    
    # Biomarcadores (peso 20%)
    campos_biomarcadores = {
        'IHQ_HER2': record.get('IHQ_HER2'),
        'IHQ_KI-67': record.get('IHQ_KI-67'),
        'IHQ_RECEPTOR_ESTROGENOS': record.get('IHQ_RECEPTOR_ESTROGENOS'),
        'IHQ_RECEPTOR_PROGESTERONA': record.get('IHQ_RECEPTOR_PROGESTERONA'),
        'Factor pronostico': record.get('Factor pronostico')
    }
    
    biomarcadores_ok = sum(1 for v in campos_biomarcadores.values() if v and v not in ['N/A', '', 'None'])
    score_biomarcadores = (biomarcadores_ok / len(campos_biomarcadores)) * 20
    
    # Penalización por problemas (peso 10%)
    penalties = {
        'CRÍTICO': 5,
        'ALTO': 3,
        'MEDIO': 1.5,
        'BAJO': 0.5
    }
    
    penalty_total = sum(penalties.get(p['severidad'], 0) for p in problems)
    score_problemas = max(0, 10 - penalty_total)
    
    # Score total
    total_score = score_criticos + score_importantes + score_biomarcadores + score_problemas
    
    return round(total_score, 2)


def prepare_ia_payload(record: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
    """Prepara el payload completo para enviar a la IA
    
    Args:
        record: Datos del registro
        evaluation: Evaluación de calidad del registro
        
    Returns:
        Dict con todos los datos necesarios para la IA
    """
    
    return {
        'numero_peticion': record.get('Numero de caso', ''),
        'score_calidad': evaluation['score_total'],
        'problemas_detectados': [p['tipo'] for p in evaluation['problems']],
        'confianza': evaluation['confidence'],
        
        'contexto_completo': {
            'descripcion_macroscopica': record.get('Descripcion macroscopica', ''),
            'descripcion_microscopica': record.get('Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)', ''),
            'descripcion_diagnostico': record.get('Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)', '')
        },
        
        'datos_actuales': {
            'diagnostico_principal': record.get('Diagnostico Principal', ''),
            'malignidad': record.get('Malignidad', ''),
            'factor_pronostico': record.get('Factor pronostico', '')
        },
        
        'biomarcadores_actuales': {
            'HER2': record.get('IHQ_HER2', ''),
            'Ki67': record.get('IHQ_KI-67', ''),
            'RE': record.get('IHQ_RECEPTOR_ESTROGENOS', ''),
            'RP': record.get('IHQ_RECEPTOR_PROGESTERONA', ''),
            'P16': record.get('IHQ_P16_ESTADO', ''),
            'P40': record.get('IHQ_P40_ESTADO', ''),
            'PDL1': record.get('IHQ_PDL-1', ''),
            'P53': record.get('IHQ_P53', '')
        },
        
        'instrucciones_ia': """
        Analiza el contexto completo y proporciona correcciones para los campos problemáticos:
        
        1. DIAGNÓSTICO PRINCIPAL:
           - Extrae el diagnóstico EXACTO sin comentarios ni explicaciones
           - Si hay múltiples diagnósticos, prioriza el principal
           - No incluyas "SIN EMBARGO", "SE SUGIERE", etc.
        
        2. MALIGNIDAD:
           - Determina: MALIGNO / BENIGNO / NO_APLICABLE
           - Basado en keywords del diagnóstico
        
        3. FACTOR PRONÓSTICO:
           - Extrae Ki-67, p53, grado histológico si existen
           - Formato: "Ki-67: X% / p53: estado"
        
        4. BIOMARCADORES:
           - Extrae todos los valores mencionados
           - Formato: POSITIVO / NEGATIVO / porcentaje
        
        5. VALIDACIÓN:
           - Verifica consistencia entre todos los campos
           - Marca con confianza: HIGH/MEDIUM/LOW
        
        Devuelve JSON con campos corregidos y nivel de confianza.
        """
    }


if __name__ == '__main__':
    # Test básico
    test_record = {
        'Numero de caso': 'IHQ250001',
        'Primer nombre': 'TEST',
        'Edad': '50',
        'Genero': 'FEMENINO',
        'Diagnostico Principal': 'N/A',
        'Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)': 'ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO',
        'Malignidad': 'MALIGNO'
    }
    
    evaluation = evaluate_record_quality(test_record)
    logging.info(f"Score: {evaluation['score_total']}")
    logging.info(f"Needs IA: {evaluation['needs_ia_review']}")
    logging.info(f"Problems: {len(evaluation['problems'])}")
    for problem in evaluation['problems']:
        logging.info(f"  - {problem['tipo']}: {problem['descripcion']}")
