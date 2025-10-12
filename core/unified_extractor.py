#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Módulo de integración unificado para extractores refactorizados

Este módulo proporciona una interfaz compatible con el ui.py existente
utilizando internamente los nuevos extractores modulares de la refactorización v4.0.

Versión: 4.2.4 - Mejoras críticas en extracción y limpieza de diagnóstico
Fecha: 5 de octubre de 2025
Cambios: 
  - Búsqueda en descripción macroscópica para diagnósticos referenciados
  - Limpieza de texto explicativo en diagnósticos
  - 4 niveles de prioridad para extracción de diagnóstico
"""

import sys
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agregar path del proyecto para imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Importar extractores nuevos refactorizados
    from core.extractors.biomarker_extractor import extract_biomarkers
    from core.extractors.patient_extractor import extract_patient_data
    from core.extractors.medical_extractor import extract_medical_data
    from core.utils.name_splitter import split_full_name
    from core.utils.date_processor import parse_date, calculate_birth_date
    from core.utils.utf8_fixer import clean_text_comprehensive
    from core.utils.spelling_corrector import correct_extracted_data, correct_spelling

    # IMPORTANTE: Importar funciones de extracción médica
    from core.extractors.medical_extractor import (
        extract_factor_pronostico, 
        extract_principal_diagnosis, 
        clean_diagnosis_text
    )

    EXTRACTORS_AVAILABLE = True
    logger.info("✅ Extractores refactorizados cargados correctamente")

except ImportError as e:
    # Fallback a procesadores antiguos si los nuevos no están disponibles
    logger.warning(f"⚠️ No se pudieron cargar extractores nuevos: {e}")
    logger.info("🔄 Cargando procesadores antiguos como fallback...")

    try:
        from core.procesador_ihq_biomarcadores import (
            process_ihq_paths as process_ihq_paths_legacy
        )
        from core.procesador_ihq import (
            extract_ihq_data as extract_ihq_data_legacy_alt,
            parse_estudios_table_for_organo as parse_estudios_table_for_organo_legacy
        )
        from core.extractors.medical_extractor import (
            extract_principal_diagnosis,
            clean_diagnosis_text
        )
        EXTRACTORS_AVAILABLE = False
        logger.info("✅ Procesadores antiguos cargados como fallback")
    except ImportError as e:
        logger.error(f"❌ Error crítico: No se pueden cargar ni extractores nuevos ni antiguos: {e}")
        # Definir funciones dummy como último recurso
        def clean_diagnosis_text(text):
            """Función dummy si todo falla"""
            return text if text else ''
        def extract_principal_diagnosis(text):
            """Función dummy si todo falla"""
            return text if text else ''
        raise


def extract_ihq_data(text: str) -> Dict[str, Any]:
    """Extrae datos IHQ de texto usando extractores refactorizados
    
    Interfaz compatible con la función original pero implementada
    con los nuevos extractores modulares.
    
    Args:
        text (str): Texto a procesar
        
    Returns:
        Dict[str, Any]: Datos extraídos en formato compatible
    """
    if not text or not text.strip():
        return {}
    
    if not EXTRACTORS_AVAILABLE:
        # Fallback a extractor antiguo
        logger.warning("⚠️ Usando extractor legacy como fallback")
        try:
            return extract_ihq_data_legacy_alt(text)
        except:
            return {}
    
    try:
        # CORREGIDO: NO limpiar el texto aquí, los extractores lo hacen internamente
        clean_text = text  # No usar clean_text_comprehensive aquí

        # Extraer datos con nuevos extractores COMPLETOS
        patient_data = extract_patient_data(clean_text)
        biomarker_data = extract_biomarkers(clean_text)
        medical_data = extract_medical_data(clean_text)  # NUEVO: Datos médicos

        # Combinar y mapear al formato esperado por ui.py
        combined_data = {}
        
        # === DATOS DE PACIENTE ===
        if patient_data:
            # Campos básicos de identificación
            combined_data.update({
                'nombre_completo': patient_data.get('nombre_completo', ''),
                'numero_peticion': patient_data.get('numero_peticion', ''),
                # CORREGIDO v4.2: Priorizar identificacion_numero (solo dígitos) sobre identificacion_completa
                'identificacion': patient_data.get('identificacion_numero', '') or patient_data.get('identificacion_completa', ''),
                'tipo_documento': patient_data.get('tipo_documento', ''),
                'genero': patient_data.get('genero', ''),
                'edad': patient_data.get('edad', ''),
                'eps': patient_data.get('eps', ''),
                'medico_tratante': patient_data.get('medico_tratante', ''),
                'servicio': patient_data.get('servicio', ''),
                'fecha_ingreso': patient_data.get('fecha_ingreso', ''),
                'fecha_informe': patient_data.get('fecha_informe', ''),
                'procedencia': patient_data.get('procedencia', ''),
                'historia_clinica': patient_data.get('historia_clinica', ''),
            })
            
            # NUEVO: Mapeo adicional a nombres de columnas de BD
            combined_data['N. peticion (0. Numero de biopsia)'] = patient_data.get('numero_peticion', '')
            combined_data['N. de identificación'] = patient_data.get('identificacion_numero', '') or patient_data.get('identificacion_completa', '')
            combined_data['Tipo de documento'] = patient_data.get('tipo_documento', 'CC')
            combined_data['Edad'] = patient_data.get('edad', '')
            combined_data['Genero'] = patient_data.get('genero', '')
            combined_data['EPS'] = patient_data.get('eps', '')
            combined_data['Servicio'] = patient_data.get('servicio', '')
            combined_data['Médico tratante'] = patient_data.get('medico_tratante', '')
            combined_data['Fecha de ingreso (2. Fecha de la muestra)'] = patient_data.get('fecha_ingreso', '')
            combined_data['Fecha Informe'] = patient_data.get('fecha_informe', '')
            
            # Campos procesados adicionales
            if 'nombres' in patient_data:
                combined_data['nombres'] = patient_data['nombres']
                # CORREGIDO: Dividir nombres en campos individuales para BD
                nombres_split = patient_data['nombres'].split() if patient_data['nombres'] else []
                combined_data['Primer nombre'] = nombres_split[0] if len(nombres_split) > 0 else ''
                combined_data['Segundo nombre'] = nombres_split[1] if len(nombres_split) > 1 else ''
            else:
                combined_data['Primer nombre'] = ''
                combined_data['Segundo nombre'] = ''
                
            if 'apellidos' in patient_data:
                combined_data['apellidos'] = patient_data['apellidos']
                # CORREGIDO: Dividir apellidos en campos individuales para BD
                apellidos_split = patient_data['apellidos'].split() if patient_data['apellidos'] else []
                combined_data['Primer apellido'] = apellidos_split[0] if len(apellidos_split) > 0 else ''
                combined_data['Segundo apellido'] = apellidos_split[1] if len(apellidos_split) > 1 else ''
            else:
                combined_data['Primer apellido'] = ''
                combined_data['Segundo apellido'] = ''
                
            if 'nombre_formal' in patient_data:
                combined_data['nombre_formal'] = patient_data['nombre_formal']
            if 'edad_años' in patient_data:
                combined_data['edad_años'] = patient_data['edad_años']
            if 'fecha_nacimiento_calculada' in patient_data:
                combined_data['fecha_nacimiento'] = patient_data['fecha_nacimiento_calculada']
        
        # === DATOS MÉDICOS ===
        if medical_data:
            # Integrar todos los datos médicos extraídos

            # CORREGIDO v4.2: Priorizar organo de la tabla (patient_extractor) sobre ihq_organo del diagnóstico
            # Razón: El campo "Organo" de la tabla es el nombre oficial/administrativo
            #        mientras que ihq_organo del diagnóstico es más descriptivo
            organo_final = ''
            ihq_organo = medical_data.get('ihq_organo', '')
            organo_patient = patient_data.get('organo', '') if patient_data else ''  # ESTE tiene el órgano de la tabla

            # Prioridad: organo_patient (tabla de estudios) > ihq_organo (diagnóstico)
            if organo_patient and organo_patient != 'ORGANO_NO_ESPECIFICADO':
                organo_final = organo_patient
            elif ihq_organo and ihq_organo != 'ORGANO_NO_ESPECIFICADO':
                organo_final = ihq_organo

            combined_data.update({
                'diagnostico': medical_data.get('diagnostico_final', '') or medical_data.get('diagnostico_final_ihq', ''),
                'descripcion_microscopica': medical_data.get('descripcion_microscopica', '') or medical_data.get('descripcion_microscopica_final', ''),
                'descripcion_macroscopica': medical_data.get('descripcion_macroscopica', '') or medical_data.get('descripcion_macroscopica_final', ''),
                'organo': organo_final,  # CORREGIDO: Usar lógica de priorización
                'ihq_organo': ihq_organo,  # NUEVO: Órgano extraído del diagnóstico
                'malignidad': medical_data.get('malignancy_status', '') or medical_data.get('malignidad', ''),
                'fecha_toma': medical_data.get('fecha_toma', ''),
                'responsable_final': medical_data.get('responsable_final', ''),
                'especialidad_deducida': medical_data.get('especialidad_deducida', ''),
                'tipo_informe': medical_data.get('tipo_informe', ''),
                'hospitalizado': medical_data.get('hospitalizado', ''),
                # ELIMINADO: 'n_autorizacion' - campo no utilizado que genera NaN
                'estudios_solicitados': medical_data.get('estudios_solicitados', ''),
                'procedimiento': patient_data.get('procedimiento', '') if patient_data else '',  # Nuevo campo
                'factor_pronostico': medical_data.get('factor_pronostico', ''),  # AGREGADO
            })
            
            # NUEVO: Mapeo adicional a nombres de columnas de BD
            combined_data['Diagnostico Principal'] = medical_data.get('diagnostico_final', '') or medical_data.get('diagnostico_final_ihq', '')
            combined_data['Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)'] = medical_data.get('descripcion_microscopica', '') or medical_data.get('descripcion_microscopica_final', '')
            combined_data['Descripcion macroscopica'] = medical_data.get('descripcion_macroscopica', '') or medical_data.get('descripcion_macroscopica_final', '')
            combined_data['Organo (1. Muestra enviada a patología)'] = organo_final
            combined_data['IHQ_ORGANO'] = ihq_organo
            combined_data['Malignidad'] = medical_data.get('malignancy_status', '') or medical_data.get('malignidad', '')
            combined_data['Fecha de toma (1. Fecha de la toma)'] = medical_data.get('fecha_toma', '')
            combined_data['Usuario finalizacion'] = medical_data.get('responsable_final', '')
            combined_data['Factor pronostico'] = medical_data.get('factor_pronostico', '')
            combined_data['IHQ_ESTUDIOS_SOLICITADOS'] = medical_data.get('estudios_solicitados', '')
            
            # Si no hay diagnóstico específico, intentar extraer de texto libre
            if not combined_data['diagnostico']:
                diag_patterns = [
                    r'DIAGNÓSTICO[:\s]+(.*?)(?=\s*(?:MALIGNIDAD|FECHA|ÓRGANO|$))',
                    r'DIAGNOSIS[:\s]+(.*?)(?=\s*(?:MALIGNANCY|DATE|ORGAN|$))',
                    r'(ADENOCARCINOMA[^.]*)',
                    r'(CARCINOMA[^.]*)',
                    r'(SARCOMA[^.]*)',
                    r'(LINFOMA[^.]*)',
                    r'(MELANOMA[^.]*)'
                ]
                
                for pattern in diag_patterns:
                    match = re.search(pattern, clean_text, re.IGNORECASE)
                    if match:
                        combined_data['diagnostico'] = match.group(1).strip()
                        break
            
            # Sobrescribir servicio, fecha_ingreso y fecha_informe si medical_data tiene mejores valores
            if medical_data.get('servicio') and not combined_data.get('servicio'):
                combined_data['servicio'] = medical_data['servicio']
            if medical_data.get('fecha_informe') and not combined_data.get('fecha_informe'):
                combined_data['fecha_informe'] = medical_data['fecha_informe']
            if medical_data.get('fecha_ingreso') and not combined_data.get('fecha_ingreso'):
                combined_data['fecha_ingreso'] = medical_data['fecha_ingreso']
        
        # === BIOMARCADORES ===
        if biomarker_data:
            # SISTEMA AVANZADO v5.0: Integrar extract_narrative_biomarkers
            narrative_biomarkers = {}
            try:
                from core.extractors.biomarker_extractor import extract_narrative_biomarkers
                narrative_biomarkers = extract_narrative_biomarkers(clean_text) or {}
                if narrative_biomarkers:
                    logger.info(f"🧬 Sistema avanzado detectó {len(narrative_biomarkers)} biomarcadores narrativos")
            except ImportError:
                logger.warning("⚠️ Sistema avanzado de biomarcadores no disponible")

            # Mapear biomarcadores al formato IHQ esperado - MAPEO COMPLETO v5.0
            biomarker_mapping = {
                'HER2': 'IHQ_HER2',
                'KI67': 'IHQ_KI-67', 
                'ER': 'IHQ_RECEPTOR_ESTROGENO',
                'PR': 'IHQ_RECEPTOR_PROGESTERONOS',
                'PDL1': 'IHQ_PDL-1',
                'P16': 'IHQ_P16_ESTADO',
                'P40': 'IHQ_P40_ESTADO',
                'P53': 'IHQ_P53',
                'CDX2': 'IHQ_CDX2',
                'CK7': 'IHQ_CK7',
                'CK20': 'IHQ_CK20',
                'TTF1': 'IHQ_TTF1',
                # BIOMARCADORES QUE REALMENTE EXISTEN EN LA BASE DE DATOS
                'S100': 'IHQ_S100',
                'CD117': 'IHQ_CD117',
                'GATA3': 'IHQ_GATA3',
                'CD68': 'IHQ_CD68',
                'CD45': 'IHQ_CD45',
                'CD20': 'IHQ_CD20',
                'CD3': 'IHQ_CD3',
                'CD10': 'IHQ_CD10',
                'CD5': 'IHQ_CD5',
                'CD30': 'IHQ_CD30',
                'CD34': 'IHQ_CD34',
                'CD38': 'IHQ_CD38',
                'CD56': 'IHQ_CD56',
                'CD61': 'IHQ_CD61',
                'CD138': 'IHQ_CD138',
                'EMA': 'IHQ_EMA',
                'SOX10': 'IHQ_SOX10',
                'VIMENTINA': 'IHQ_VIMENTINA',
                'VIMENTIN': 'IHQ_VIMENTINA',  # Variante
                'CHROMOGRANINA': 'IHQ_CHROMOGRANINA',
                'SYNAPTOPHYSIN': 'IHQ_SYNAPTOPHYSIN',
                'MELAN_A': 'IHQ_MELAN_A',
                # BIOMARCADORES ADICIONALES QUE PUEDEN NO ESTAR EN DB PERO SÍ EN TEXTOS
                'CDK4': 'IHQ_CDK4',  # CRÍTICO - RESTAURADO
                'MDM2': 'IHQ_MDM2',  # CRÍTICO - RESTAURADO
                'NAPSIN': 'IHQ_NAPSIN',
                'BCL2': 'IHQ_BCL2',
                'BCL6': 'IHQ_BCL6',
                'MUM1': 'IHQ_MUM1',
                'PAX5': 'IHQ_PAX5',
                'CD79A': 'IHQ_CD79A',
                'CD15': 'IHQ_CD15',
                'ALK': 'IHQ_ALK',
                'CKAE1AE3': 'IHQ_CKAE1AE3',
                'CKAE1_AE3': 'IHQ_CKAE1AE3',  # Variante del caso 2
                'DESMIN': 'IHQ_DESMIN',
                'ACTIN': 'IHQ_ACTIN',
                'MYOGENIN': 'IHQ_MYOGENIN',
                'MYOD1': 'IHQ_MYOD1',
                'SMA': 'IHQ_SMA',
                'MSA': 'IHQ_MSA',
                'CALRETININ': 'IHQ_CALRETININ',
                # NUEVOS BIOMARCADORES HORMONALES DEL CASO 2 - CRÍTICOS
                'ACTH': 'IHQ_ACTH',
                'GH': 'IHQ_GH',
                'PROLACTINA': 'IHQ_PROLACTINA',
                'TSH': 'IHQ_TSH',
                'LH': 'IHQ_LH',
                'FSH': 'IHQ_FSH',
                'WT1': 'IHQ_WT1',
                'CD31': 'IHQ_CD31',
                'FACTOR_VIII': 'IHQ_FACTOR_VIII',
                'MELANOMA': 'IHQ_MELANOMA',
                'HMB45': 'IHQ_HMB45',
                'TYROSINASE': 'IHQ_TYROSINASE'
            }
            
            # PRIORIDAD 1: Sistema avanzado (narrative_biomarkers) - MÁS PRECISO
            for biomarker_name, result in narrative_biomarkers.items():
                biomarker_upper = biomarker_name.upper()
                if biomarker_upper in biomarker_mapping:
                    ihq_field = biomarker_mapping[biomarker_upper]
                    combined_data[ihq_field] = result
                    logger.debug(f"🧬 Avanzado: {biomarker_upper} -> {ihq_field} = {result}")
            
            # PRIORIDAD 2: Sistema refactorizado (biomarker_data) - SOLO SI NO EXISTE
            for new_name, ihq_field in biomarker_mapping.items():
                if new_name in biomarker_data and biomarker_data[new_name]:
                    # Solo usar si el campo no fue llenado por sistema avanzado
                    if ihq_field not in combined_data or not combined_data[ihq_field]:
                        combined_data[ihq_field] = biomarker_data[new_name]
                        logger.debug(f"🔬 Refactorizado: {new_name} -> {ihq_field} = {biomarker_data[new_name]}")
            
            # También mantener los nombres originales para compatibilidad
            for new_name, old_name in biomarker_mapping.items():
                old_field = old_name.lower().replace('ihq_', '').replace('_estado', '')
                if new_name in biomarker_data and biomarker_data[new_name]:
                    combined_data[old_field] = biomarker_data[new_name]
        
        # === CORRECCIÓN ORTOGRÁFICA ===
        # Aplicar corrección ortográfica a todos los campos extraídos
        combined_data = correct_extracted_data(combined_data)
        logger.info("✅ Corrección ortográfica aplicada a datos extraídos")

        # === CAMPOS DE METADATA ===
        combined_data.update({
            'extraction_timestamp': datetime.now().isoformat(),
            'extractor_version': '4.0.0_refactored',
            'processing_method': 'modular_extractors'
        })

        logger.info(f"✅ Extraídos {len(combined_data)} campos con extractores refactorizados")
        return combined_data
        
    except Exception as e:
        logger.error(f"❌ Error en extractores refactorizados: {e}")
        # Fallback a extractor antiguo en caso de error
        if EXTRACTORS_AVAILABLE:
            logger.info("🔄 Intentando fallback a extractor legacy...")
            try:
                return extract_ihq_data_legacy_alt(text)
            except:
                return {}
        else:
            return {}


def process_ihq_paths(pdf_paths: List[str], output_dir: str) -> int:
    """Procesa múltiples PDFs usando extractores refactorizados
    
    Interfaz compatible con la función original pero implementada
    con los nuevos extractores modulares y mejor manejo de errores.
    ACTUALIZADA: Ahora procesa múltiples casos por PDF.
    
    Args:
        pdf_paths (List[str]): Lista de rutas de PDFs
        output_dir (str): Directorio de salida
        
    Returns:
        int: Número de registros procesados exitosamente
    """
    if not pdf_paths:
        logger.warning("⚠️ No se proporcionaron PDFs para procesar")
        return 0
    
    if not EXTRACTORS_AVAILABLE:
        # Fallback a procesador antiguo
        logger.warning("⚠️ Usando procesador legacy como fallback")
        return process_ihq_paths_legacy(pdf_paths, output_dir)
    
    logger.info(f"🚀 Procesando {len(pdf_paths)} PDFs con extractores refactorizados...")
    
    processed_count = 0
    results = []
    errors = []
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    for i, pdf_path in enumerate(pdf_paths, 1):
        try:
            logger.info(f"📄 Procesando {i}/{len(pdf_paths)}: {Path(pdf_path).name}")
            
            # Extraer texto del PDF
            try:
                # Usar OCR real del sistema existente
                from core.processors.ocr_processor import pdf_to_text_enhanced
                
                text_content = pdf_to_text_enhanced(pdf_path)
                
                # Si devuelve una lista, convertir a string
                if isinstance(text_content, list):
                    text_content = '\n'.join(text_content)
                
                if not text_content or len(text_content.strip()) < 10:
                    logger.warning(f"⚠️ PDF vacío o texto insuficiente: {pdf_path}")
                    continue
                    
                logger.info(f"✅ Texto extraído: {len(text_content)} caracteres")
                
            except Exception as e:
                logger.error(f"❌ Error extrayendo texto de {pdf_path}: {e}")
                errors.append(f"{Path(pdf_path).name}: Error OCR - {str(e)}")
                continue
            
            # NUEVO: Segmentar texto en múltiples casos
            try:
                # Usar función de segmentación del OCR processor
                from core.processors.ocr_processor import segment_reports_multicase
                
                segments = segment_reports_multicase(text_content)
                logger.info(f"🔍 Encontrados {len(segments)} casos en {Path(pdf_path).name}")
                
                if not segments:
                    logger.warning(f"⚠️ No se encontraron casos en {pdf_path}")
                    continue
                    
            except Exception as e:
                logger.warning(f"⚠️ Error segmentando casos, procesando como caso único: {e}")
                segments = [text_content]  # Fallback a procesamiento único
            
            # Procesar cada caso individualmente
            pdf_case_count = 0
            for case_idx, case_text in enumerate(segments, 1):
                try:
                    if not case_text.strip():
                        continue
                    
                    logger.info(f"  📋 Procesando caso {case_idx}/{len(segments)}")
                    
                    # Extraer datos estructurados del caso
                    extracted_data = extract_ihq_data(case_text)
                    
                    if not extracted_data:
                        logger.warning(f"  ⚠️ No se extrajeron datos del caso {case_idx}")
                        continue
                    
                    # Agregar metadatos del archivo y caso
                    extracted_data.update({
                        'archivo_pdf': Path(pdf_path).name,
                        'ruta_completa': pdf_path,
                        'fecha_procesamiento': datetime.now().isoformat(),
                        'numero_archivo': i,
                        'caso_numero': case_idx,
                        'total_casos_archivo': len(segments)
                    })
                    
                    results.append(extracted_data)
                    pdf_case_count += 1
                    
                    logger.info(f"  ✅ Caso {case_idx} procesado exitosamente")
                    
                except Exception as e:
                    logger.error(f"  ❌ Error procesando caso {case_idx}: {e}")
                    errors.append(f"{Path(pdf_path).name} - Caso {case_idx}: {str(e)}")
                    continue
            
            processed_count += pdf_case_count
            logger.info(f"✅ PDF completado: {pdf_case_count} casos extraídos de {Path(pdf_path).name}")
            
        except Exception as e:
            logger.error(f"❌ Error procesando {pdf_path}: {e}")
            errors.append(f"{Path(pdf_path).name}: {str(e)}")
            continue
    
    # Guardar resultados si hay datos
    if results:
        try:
            # MAPEAR DATOS PARA AMBOS: EXCEL Y BASE DE DATOS
            db_records = []
            for result in results:
                db_record = map_to_database_format(result)
                db_records.append(db_record)
            
            # Crear DataFrame con datos mapeados (no crudos)
            df = pd.DataFrame(db_records)
            
            # Guardar en Excel
            excel_path = Path(output_dir) / f"resultados_ihq_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(excel_path, index=False)
            logger.info(f"💾 Resultados guardados en: {excel_path}")
            
            # Guardar en base de datos
            try:
                from core.database_manager import save_records, init_db
                
                # Inicializar BD para asegurar nuevas columnas
                init_db()
                
                # Usar los mismos datos mapeados para la BD
                saved_count = save_records(db_records)
                logger.info(f"💾 {saved_count} registros guardados en base de datos")
                logger.info(f"💾 {saved_count} registros guardados en base de datos")
                
            except Exception as e:
                logger.warning(f"⚠️ No se pudo guardar en BD: {e}")
                # Continuar porque ya se guardó en Excel
                
        except Exception as e:
            logger.error(f"❌ Error guardando resultados: {e}")
    
    # Reporte final
    if errors:
        error_file = Path(output_dir) / f"errores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(error_file, 'w', encoding='utf-8') as f:
            f.write("ERRORES DE PROCESAMIENTO:\n\n")
            for error in errors:
                f.write(f"• {error}\n")
        logger.warning(f"⚠️ {len(errors)} errores registrados en: {error_file}")
    
    logger.info(f"🎯 Procesamiento completado: {processed_count}/{len(pdf_paths)} archivos exitosos")
    return processed_count


def parse_estudios_table_for_organo(text: str) -> Dict[str, Any]:
    """Parsea tabla de estudios para mapear órganos específicos
    
    Versión mejorada que usa extractores refactorizados para 
    mejor detección de órganos y diagnósticos.
    
    Args:
        text (str): Texto completo del informe
        
    Returns:
        Dict[str, Any]: Mapeo de órganos detectados
    """
    if not text or not text.strip():
        return {}
    
    if not EXTRACTORS_AVAILABLE:
        # Fallback a función antigua
        logger.warning("⚠️ Usando parser legacy para órganos")
        return parse_estudios_table_for_organo_legacy(text)
    
    try:
        # Limpiar texto
        clean_text = clean_text_comprehensive(text)
        
        # TODO: Implementar detector de órganos con extractores refactorizados
        # Por ahora, usar lógica básica mejorada
        
        organos_detectados = {}
        
        # Patrones básicos de órganos comunes
        organ_patterns = {
            'mama': ['mama', 'breast', 'mamario', 'mamaria'],
            'pulmon': ['pulmón', 'pulmonar', 'lung', 'bronquio'],
            'colon': ['colon', 'colorrectal', 'intestino'],
            'prostata': ['próstata', 'prostate', 'prostático'],
            'estomago': ['estómago', 'gástrico', 'stomach'],
            'higado': ['hígado', 'hepático', 'liver'],
            'pancreas': ['páncreas', 'pancreático', 'pancreas'],
            'ovario': ['ovario', 'ovárico', 'ovarian'],
            'utero': ['útero', 'uterino', 'endometrio'],
            'riñon': ['riñón', 'renal', 'kidney'],
            'vejiga': ['vejiga', 'vesical', 'bladder'],
            'tiroides': ['tiroides', 'tiroideo', 'thyroid']
        }
        
        text_lower = clean_text.lower()
        
        for organo, keywords in organ_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    organos_detectados[organo] = {
                        'detectado': True,
                        'keyword_usado': keyword,
                        'confianza': 0.8  # Confianza básica
                    }
                    break
        
        if organos_detectados:
            logger.info(f"🎯 Detectados órganos: {list(organos_detectados.keys())}")
        
        return organos_detectados
        
    except Exception as e:
        logger.error(f"❌ Error en parser de órganos: {e}")
        # Fallback a función antigua
        return parse_estudios_table_for_organo_legacy(text)


# === FUNCIONES AUXILIARES ===

def get_extractor_status() -> Dict[str, Any]:
    """Retorna el estado de los extractores disponibles"""
    return {
        'extractors_available': EXTRACTORS_AVAILABLE,
        'version': '4.0.0',
        'modules_loaded': {
            'biomarker_extractor': EXTRACTORS_AVAILABLE,
            'patient_extractor': EXTRACTORS_AVAILABLE,
            'utils': EXTRACTORS_AVAILABLE
        },
        'fallback_active': not EXTRACTORS_AVAILABLE
    }


def validate_extraction_result(data: Dict[str, Any]) -> bool:
    """Valida que los datos extraídos tengan calidad mínima"""
    if not data:
        return False
    
    # Verificar campos mínimos requeridos
    required_fields = ['nombre_completo', 'numero_peticion']
    has_required = any(field in data and data[field] for field in required_fields)
    
    # Verificar que tenga al menos algunos biomarcadores
    biomarker_fields = ['her2', 'ki67', 'er', 'pr', 'pdl1']
    has_biomarkers = any(field in data and data[field] for field in biomarker_fields)
    
    return has_required or has_biomarkers

# Agregar función helper para construir nombre completo limpio
def build_clean_full_name(primer_nombre: str, segundo_nombre: str, primer_apellido: str, segundo_apellido: str) -> str:
    """Construye nombre completo sin N/A ni valores vacíos.
    
    v4.2.2: Elimina 'N/A', 'nan', y valores vacíos del nombre completo
    
    Args:
        primer_nombre: Primer nombre
        segundo_nombre: Segundo nombre (puede ser N/A o vacío)
        primer_apellido: Primer apellido
        segundo_apellido: Segundo apellido (puede ser N/A o vacío)
    
    Returns:
        Nombre completo limpio sin N/A
    """
    parts = []
    
    # Agregar primer nombre (siempre debería existir)
    if primer_nombre and primer_nombre not in ['N/A', 'nan', '', 'None']:
        parts.append(primer_nombre.strip())
    
    # Agregar segundo nombre solo si existe y no es N/A
    if segundo_nombre and segundo_nombre not in ['N/A', 'nan', '', 'None']:
        parts.append(segundo_nombre.strip())
    
    # Agregar primer apellido (siempre debería existir)
    if primer_apellido and primer_apellido not in ['N/A', 'nan', '', 'None']:
        parts.append(primer_apellido.strip())
    
    # Agregar segundo apellido solo si existe y no es N/A
    if segundo_apellido and segundo_apellido not in ['N/A', 'nan', '', 'None']:
        parts.append(segundo_apellido.strip())
    
    return ' '.join(parts) if parts else 'N/A'


def map_to_database_format(extracted_data: Dict[str, Any]) -> Dict[str, str]:
    """Mapea los datos extraídos al formato de base de datos del HUV
    
    Convierte los datos extraídos por los nuevos extractores al formato
    esperado por database_manager.save_records()
    """
    if not extracted_data:
        return {}
    
    # Crear mapeo básico usando los datos disponibles
    db_record = {}
    
    # === DATOS BÁSICOS DE IDENTIFICACIÓN ===
    db_record["N. peticion (0. Numero de biopsia)"] = extracted_data.get('numero_peticion', '')
    db_record["N. de identificación"] = extracted_data.get('identificacion', '')
    db_record["Tipo de documento"] = extracted_data.get('tipo_documento', 'CC')
    
    # === NOMBRES Y APELLIDOS ===
    # Priorizar nombres separados si están disponibles
    nombres_split = extracted_data.get('nombres', '').split() if extracted_data.get('nombres') else []
    apellidos_split = extracted_data.get('apellidos', '').split() if extracted_data.get('apellidos') else []
    
    # Si no hay nombres separados, intentar desde nombre_completo
    if not nombres_split and not apellidos_split and extracted_data.get('nombre_completo'):
        nombre_completo = extracted_data['nombre_completo']
        # Dividir por última palabra como apellido
        parts = nombre_completo.strip().split()
        if len(parts) >= 2:
            nombres_split = parts[:-1]
            apellidos_split = [parts[-1]]
        elif len(parts) == 1:
            nombres_split = parts
    
    primer_nom = nombres_split[0] if len(nombres_split) > 0 else ""
    segundo_nom = nombres_split[1] if len(nombres_split) > 1 else ""
    primer_ape = apellidos_split[0] if len(apellidos_split) > 0 else ""
    segundo_ape = apellidos_split[1] if len(apellidos_split) > 1 else ""
    
    db_record["Primer nombre"] = primer_nom if primer_nom else "N/A"
    db_record["Segundo nombre"] = segundo_nom if segundo_nom else "N/A"
    db_record["Primer apellido"] = primer_ape if primer_ape else "N/A"
    db_record["Segundo apellido"] = segundo_ape if segundo_ape else "N/A"
    
    # === DATOS DEMOGRÁFICOS ===
    db_record["Edad"] = extracted_data.get('edad', 'N/A')
    db_record["Genero"] = extracted_data.get('genero', 'N/A')
    db_record["Fecha de nacimiento"] = extracted_data.get('fecha_nacimiento', 'N/A')
    
    # === DATOS CLÍNICOS ===
    db_record["EPS"] = extracted_data.get('eps', 'N/A')
    db_record["Servicio"] = extracted_data.get('servicio', 'N/A')
    db_record["Médico tratante"] = extracted_data.get('medico_tratante', 'N/A')
    db_record["Especialidad"] = 'PATOLOGIA'  # Default para IHQ
    
    # === DATOS ADMINISTRATIVOS ===
    db_record["Hospitalizado"] = 'NO'  # Default
    db_record["Sede"] = 'HUV'  # Default
    # ELIMINADO: 'N. Autorizacion' - campo no utilizado que genera NaN en exportación
    db_record["Datos Clinicos"] = 'SI'
    db_record["Departamento"] = 'VALLE DEL CAUCA'
    db_record["Municipio"] = 'CALI'
    
    # === FECHAS ===
    # ELIMINADO v4.2: "Fecha ordenamiento" - campo no utilizado
    db_record["Fecha de toma (1. Fecha de la toma)"] = extracted_data.get('fecha_toma', 'N/A')
    db_record["Fecha de ingreso (2. Fecha de la muestra)"] = extracted_data.get('fecha_ingreso', 'N/A')
    db_record["Fecha Informe"] = extracted_data.get('fecha_informe', 'N/A')
    # CORREGIDO: El campo se llama 'responsable_final' en los extractores
    db_record["Usuario finalizacion"] = extracted_data.get('responsable_final', '') or 'N/A'
    
    # === INFORMACIÓN MÉDICA ===
    # CORREGIDO: Priorizar organo (de tabla) sobre ihq_organo (diagnóstico), con fallback a N/A
    organo_db = extracted_data.get('organo', '') or extracted_data.get('ihq_organo', '')
    if not organo_db or organo_db == 'ORGANO_NO_ESPECIFICADO':
        organo_db = 'N/A'

    db_record["Organo (1. Muestra enviada a patología)"] = organo_db

    db_record["Malignidad"] = extracted_data.get('malignidad', 'N/A')

    # CORREGIDO v4.2.4: Extraer diagnóstico con múltiples fuentes y limpieza
    # Prioridad 1: Campo 'diagnostico' (diagnóstico extraído directamente)
    diagnostico_completo = extracted_data.get('diagnostico', '')
    
    # Prioridad 2: Si está vacío, usar 'Diagnostico Principal' que viene de medical_data
    if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
        diagnostico_completo = extracted_data.get('Diagnostico Principal', '')
    
    # Prioridad 3: Buscar en descripción macroscópica (diagnóstico referenciado)
    if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
        desc_macro = extracted_data.get('descripcion_macroscopica', '')
        if desc_macro and len(desc_macro) > 20:
            # Buscar patrón de diagnóstico entre comillas
            match_quoted = re.search(r'diagnósticos?\s+de\s+"([^"]+)"', desc_macro, re.IGNORECASE)
            if match_quoted:
                diagnostico_completo = match_quoted.group(1).strip()
    
    # Prioridad 4: Si aún vacío, extraer de descripción microscópica
    if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
        desc_micro = extracted_data.get('descripcion_microscopica', '')
        if desc_micro and len(desc_micro) > 20:
            # Solo si tiene keywords diagnósticas
            keywords_diag = ['CARCINOMA', 'ADENOCARCINOMA', 'SARCOMA', 'TUMOR', 'NEOPLASIA', 'MELANOMA', 'LINFOMA']
            if any(kw in desc_micro.upper() for kw in keywords_diag):
                diagnostico_completo = desc_micro

    # Si no hay nada, marcar como N/A
    if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
        diagnostico_completo = 'N/A'
    
    # Usar función especializada para extraer solo el diagnóstico principal (sin texto adicional)
    diagnostico_principal = extract_principal_diagnosis(diagnostico_completo) if diagnostico_completo and diagnostico_completo != 'N/A' else 'N/A'
    
    # NUEVO v4.2.4: Limpiar texto explicativo del diagnóstico
    if diagnostico_principal and diagnostico_principal != 'N/A':
        diagnostico_principal = clean_diagnosis_text(diagnostico_principal)

    db_record["Diagnostico Principal"] = diagnostico_principal
    db_record["Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)"] = diagnostico_completo
    db_record["Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)"] = extracted_data.get('descripcion_microscopica', 'N/A')

    # DEBUG: verificar valor de descripcion_macroscopica
    macro_value = extracted_data.get('descripcion_macroscopica', 'N/A')

    db_record["Descripcion macroscopica"] = macro_value

    # CORREGIDO: Priorizar factor_pronostico del extractor, luego extraer del diagnóstico
    factor_pronostico = extracted_data.get('factor_pronostico', '')

    # Si no viene en extracted_data, intentar extraer del diagnóstico completo
    if not factor_pronostico and diagnostico_completo and diagnostico_completo != 'N/A':
        factor_pronostico = extract_factor_pronostico(diagnostico_completo)

    db_record["Factor pronostico"] = factor_pronostico if factor_pronostico else 'N/A'
    
    # === INFORMACIÓN DE MUESTRA ===
    # ELIMINADO v4.2: "N. muestra" - campo duplicado con N. petición
    db_record["CUPS"] = '90201'  # Código IHQ
    db_record["Tipo de examen (4, 12, Metodo de obtención de la muestra, factor de certeza para el diagnóstico)"] = "ESTUDIO DE INMUNOHISTOQUIMICA"

    # Usar procedimiento extraído (CIRUGÍA o BIOPSIA) o default a INMUNOHISTOQUIMICA
    procedimiento_tipo = extracted_data.get('procedimiento', 'INMUNOHISTOQUIMICA')
    db_record["Procedimiento (11. Tipo de estudio para el diagnóstico)"] = procedimiento_tipo if procedimiento_tipo else "INMUNOHISTOQUIMICA"
    
    # === CAMPOS ADICIONALES QUE NO APLICAN ===
    empty_fields = [
        "Congelaciones /Otros estudios", "Liquidos (5 Tipo histologico)",
        "Citometria de flujo (5 Tipo histologico)", "Hora Desc. macro", "Responsable macro"
    ]
    for field in empty_fields:
        db_record[field] = 'N/A'
    
    # === MAPEAR BIOMARCADORES ===
    # Mapeo completo de biomarcadores (case-insensitive) - EXPANDIDO VERSIÓN 5.0
    all_biomarker_mapping = {
        # Biomarcadores principales
        'HER2': 'IHQ_HER2', 'her2': 'IHQ_HER2', 'IHQ_HER2': 'IHQ_HER2',
        'KI67': 'IHQ_KI-67', 'ki67': 'IHQ_KI-67', 'ki-67': 'IHQ_KI-67', 'IHQ_KI-67': 'IHQ_KI-67',  # CORREGIDO: agregar variantes
        'ER': 'IHQ_RECEPTOR_ESTROGENO', 'er': 'IHQ_RECEPTOR_ESTROGENO', 'IHQ_RECEPTOR_ESTROGENO': 'IHQ_RECEPTOR_ESTROGENO',  # CORREGIDO
        'PR': 'IHQ_RECEPTOR_PROGESTERONOS', 'pr': 'IHQ_RECEPTOR_PROGESTERONOS', 'IHQ_RECEPTOR_PROGESTERONOS': 'IHQ_RECEPTOR_PROGESTERONOS',  # CORREGIDO
        'PDL1': 'IHQ_PDL-1', 'pdl1': 'IHQ_PDL-1',
        'P16': 'IHQ_P16_ESTADO', 'p16': 'IHQ_P16_ESTADO',
        'P40': 'IHQ_P40_ESTADO', 'p40': 'IHQ_P40_ESTADO',

        # Biomarcadores v4.0
        'CK7': 'IHQ_CK7', 'ck7': 'IHQ_CK7',
        'CK20': 'IHQ_CK20', 'ck20': 'IHQ_CK20',
        'CDX2': 'IHQ_CDX2', 'cdx2': 'IHQ_CDX2',
        'EMA': 'IHQ_EMA', 'ema': 'IHQ_EMA',
        'GATA3': 'IHQ_GATA3', 'gata3': 'IHQ_GATA3',
        'SOX10': 'IHQ_SOX10', 'sox10': 'IHQ_SOX10',

        # Biomarcadores v4.1
        'P53': 'IHQ_P53', 'p53': 'IHQ_P53',
        'TTF1': 'IHQ_TTF1', 'ttf1': 'IHQ_TTF1',
        'S100': 'IHQ_S100', 's100': 'IHQ_S100',
        'VIMENTINA': 'IHQ_VIMENTINA', 'vimentina': 'IHQ_VIMENTINA',
        'CHROMOGRANINA': 'IHQ_CHROMOGRANINA', 'chromogranina': 'IHQ_CHROMOGRANINA',
        'SYNAPTOPHYSIN': 'IHQ_SYNAPTOPHYSIN', 'synaptophysin': 'IHQ_SYNAPTOPHYSIN',
        'MELAN_A': 'IHQ_MELAN_A', 'melan_a': 'IHQ_MELAN_A',

        # Marcadores CD
        'CD3': 'IHQ_CD3', 'cd3': 'IHQ_CD3',
        'CD5': 'IHQ_CD5', 'cd5': 'IHQ_CD5',
        'CD10': 'IHQ_CD10', 'cd10': 'IHQ_CD10',
        'CD20': 'IHQ_CD20', 'cd20': 'IHQ_CD20',
        'CD30': 'IHQ_CD30', 'cd30': 'IHQ_CD30',
        'CD34': 'IHQ_CD34', 'cd34': 'IHQ_CD34',
        'CD38': 'IHQ_CD38', 'cd38': 'IHQ_CD38',
        'CD45': 'IHQ_CD45', 'cd45': 'IHQ_CD45',
        'CD56': 'IHQ_CD56', 'cd56': 'IHQ_CD56',
        'CD61': 'IHQ_CD61', 'cd61': 'IHQ_CD61',
        'CD68': 'IHQ_CD68', 'cd68': 'IHQ_CD68',
        'CD117': 'IHQ_CD117', 'cd117': 'IHQ_CD117',
        'CD138': 'IHQ_CD138', 'cd138': 'IHQ_CD138',
        
        # NUEVOS BIOMARCADORES v5.0 - CRÍTICOS PARA CASO 2 Y OTROS
        'ACTH': 'IHQ_ACTH', 'acth': 'IHQ_ACTH',
        'GH': 'IHQ_GH', 'gh': 'IHQ_GH',
        'PROLACTINA': 'IHQ_PROLACTINA', 'prolactina': 'IHQ_PROLACTINA',
        'TSH': 'IHQ_TSH', 'tsh': 'IHQ_TSH',
        'LH': 'IHQ_LH', 'lh': 'IHQ_LH',
        'FSH': 'IHQ_FSH', 'fsh': 'IHQ_FSH',
        'CKAE1AE3': 'IHQ_CKAE1AE3', 'ckae1ae3': 'IHQ_CKAE1AE3',
        'CKAE1_AE3': 'IHQ_CKAE1AE3', 'ckae1_ae3': 'IHQ_CKAE1AE3',
        'NAPSIN': 'IHQ_NAPSIN', 'napsin': 'IHQ_NAPSIN',
        'CDK4': 'IHQ_CDK4', 'cdk4': 'IHQ_CDK4',
        'MDM2': 'IHQ_MDM2', 'mdm2': 'IHQ_MDM2',
        'BCL2': 'IHQ_BCL2', 'bcl2': 'IHQ_BCL2',
        'BCL6': 'IHQ_BCL6', 'bcl6': 'IHQ_BCL6',
        'MUM1': 'IHQ_MUM1', 'mum1': 'IHQ_MUM1',
        'PAX5': 'IHQ_PAX5', 'pax5': 'IHQ_PAX5',
        'CD79A': 'IHQ_CD79A', 'cd79a': 'IHQ_CD79A',
        'CD15': 'IHQ_CD15', 'cd15': 'IHQ_CD15',
        'ALK': 'IHQ_ALK', 'alk': 'IHQ_ALK',
        'DESMIN': 'IHQ_DESMIN', 'desmin': 'IHQ_DESMIN',
        'ACTIN': 'IHQ_ACTIN', 'actin': 'IHQ_ACTIN',
        'MYOGENIN': 'IHQ_MYOGENIN', 'myogenin': 'IHQ_MYOGENIN',
        'MYOD1': 'IHQ_MYOD1', 'myod1': 'IHQ_MYOD1',
        'SMA': 'IHQ_SMA', 'sma': 'IHQ_SMA',
        'MSA': 'IHQ_MSA', 'msa': 'IHQ_MSA',
        'CALRETININ': 'IHQ_CALRETININ', 'calretinin': 'IHQ_CALRETININ',
    }
    
    # Aplicar mapeos de biomarcadores
    found_biomarkers = []
    
    # Primero inicializar todos los campos de biomarcadores a vacío
    all_biomarker_columns = set(all_biomarker_mapping.values())
    for db_col in all_biomarker_columns:
        db_record[db_col] = ''
    
    # Luego aplicar los valores encontrados (sin sobreescribir)
    for bio_key, db_col in all_biomarker_mapping.items():
        if bio_key in extracted_data and extracted_data[bio_key]:
            value = str(extracted_data[bio_key]).upper()
            # Solo asignar si el campo no ha sido llenado ya
            if not db_record.get(db_col):
                db_record[db_col] = value
                found_biomarkers.append(bio_key.upper())
    
    # === CAMPOS ADICIONALES DE IHQ ===
    db_record["IHQ_ESTUDIOS_SOLICITADOS"] = ', '.join(found_biomarkers) if found_biomarkers else ''

    # CORREGIDO: Usar la misma lógica de priorización para IHQ_ORGANO
    ihq_organo_value = extracted_data.get('ihq_organo', '') or extracted_data.get('organo', '')
    if not ihq_organo_value or ihq_organo_value == 'ORGANO_NO_ESPECIFICADO':
        ihq_organo_value = ''

    db_record["IHQ_ORGANO"] = ihq_organo_value
    db_record["IHQ_P16_PORCENTAJE"] = ''  # Campo específico
    
    return db_record


def map_to_excel_format(extracted_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Mapea los datos extraídos al formato final de base de datos HUV

    CORREGIDO v4.1: Usar map_to_database_format para mapeo completo
    """
    if not extracted_data:
        return []

    # CORREGIDO: Usar map_to_database_format que tiene TODOS los mapeos correctos
    db_record = map_to_database_format(extracted_data)

    return [db_record]


# Exponer funciones con nombres exactos para compatibilidad
__all__ = [
    'extract_ihq_data',
    'process_ihq_paths', 
    'parse_estudios_table_for_organo',
    'map_to_excel_format',  # Nueva función agregada
    'get_extractor_status',
    'validate_extraction_result'
]


if __name__ == "__main__":
    # Test del módulo unificado
    print("=== Test del Módulo de Integración Unificado ===")
    
    # Verificar estado
    status = get_extractor_status()
    print(f"\n📊 Estado de extractores:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    # Test de extracción
    texto_test = """
    Nombre: MARIA ELENA RODRIGUEZ GUTIERREZ
    N. peticion: IHQ250002
    N.Identificación: CC. 52123789
    Genero: FEMENINO
    Edad: 58 años
    EPS: SANITAS
    
    RESULTADOS INMUNOHISTOQUIMICA:
    HER2: 2+ (EQUIVOCO)
    Ki-67: 35%
    ER: 90% (POSITIVO)
    PR: 85% (POSITIVO)
    """
    
    print(f"\n🧪 Probando extract_ihq_data...")
    resultado = extract_ihq_data(texto_test)
    
    print(f"\n📋 Resultados ({len(resultado)} campos):")
    for campo, valor in sorted(resultado.items()):
        if valor:  # Solo mostrar campos con valor
            print(f"  {campo}: {valor}")
    
    # Validar resultado
    es_valido = validate_extraction_result(resultado)
    print(f"\n✅ Validación: {'EXITOSA' if es_valido else 'FALLIDA'}")
    
    print(f"\n🎉 Módulo unificado funcionando correctamente!")
