#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IHQ Processor - Procesamiento de archivos IHQ
Lógica de negocio para procesamiento de archivos IHQ extraída de ui.py
"""

import logging
import re
import os
from typing import Callable, Optional


def process_ihq_file(file_path: str, log_callback: Optional[Callable] = None) -> int:
    """
    Procesar archivo IHQ con detección de múltiples informes SIN auditoría automática

    Args:
        file_path: Ruta al archivo PDF IHQ
        log_callback: Función para logging (opcional)

    Returns:
        Número de registros guardados

    Raises:
        RuntimeError: Si el procesamiento falla
    """
    from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase
    from core.unified_extractor import extract_ihq_data, map_to_database_format
    from core.database_manager import init_db, save_records
    from core.debug_mapper import DebugMapper

    # Función de log segura
    def safe_log(msg):
        if log_callback:
            log_callback(msg)
        else:
            logging.info(msg)

    try:
        safe_log("\n" + "="*60)
        safe_log("🔍 PROCESANDO ARCHIVO IHQ...")
        safe_log("="*60)

        # 1. EXTRACCIÓN OCR
        safe_log("📄 Paso 1/4: Extrayendo texto con OCR...")
        texto_ocr_completo = pdf_to_text_enhanced(file_path)

        if not texto_ocr_completo or len(texto_ocr_completo.strip()) < 10:
            raise RuntimeError("PDF vacío o con texto insuficiente")

        safe_log("✅ Texto extraído correctamente")

        # 2. SEGMENTACIÓN DE MÚLTIPLES INFORMES IHQ
        safe_log("🔀 Paso 2/4: Segmentando informes IHQ...")
        segmentos_lista = segment_reports_multicase(texto_ocr_completo)

        if not segmentos_lista:
            safe_log("⚠️ No se encontraron casos IHQ válidos, intentando procesar como un solo informe...")
            segmentos_lista = [texto_ocr_completo]

        # Extraer números IHQ de cada segmento
        segmentos_ihq = {}
        for segmento in segmentos_lista:
            # Buscar el código IHQ en el segmento
            ihq_match = re.search(r'IHQ(\d{6})', segmento, re.IGNORECASE)
            if ihq_match:
                numero_ihq = f"IHQ{ihq_match.group(1)}"
                segmentos_ihq[numero_ihq] = segmento
            else:
                # Si no tiene número IHQ, usar un identificador temporal
                temp_id = f"TEMP_{len(segmentos_ihq)+1}"
                segmentos_ihq[temp_id] = segmento

        safe_log(f"✅ {len(segmentos_ihq)} informe(s) detectado(s)")

        # 3. PROCESAR CADA INFORME INDIVIDUALMENTE
        safe_log("📋 Paso 3/4: Extrayendo datos de cada informe...")
        todos_los_registros = []

        for caso_num, (numero_ihq, texto_consolidado) in enumerate(segmentos_ihq.items(), 1):
            safe_log(f"   📄 Informe {caso_num}/{len(segmentos_ihq)}: {numero_ihq}")

            try:
                # Crear debug mapper para este caso
                mapper = DebugMapper()
                mapper.iniciar_sesion(numero_ihq, file_path)

                # Registrar OCR
                mapper.registrar_ocr(
                    texto_original=texto_ocr_completo,
                    texto_consolidado=texto_consolidado,
                    metadata={
                        'pdf_path': file_path,
                        'numero_ihq': numero_ihq,
                        'caso_num': caso_num,
                        'total_casos': len(segmentos_ihq)
                    }
                )

                # Extraer datos del informe
                safe_log(f"      🔍 Extrayendo datos...")
                datos_extraidos = extract_ihq_data(texto_consolidado)

                # DEBUGGING: Verificar qué devuelve extract_ihq_data
                safe_log(f"      📊 Tipo de datos extraídos: {type(datos_extraidos)}")
                if datos_extraidos:
                    safe_log(f"      📊 Cantidad de campos: {len(datos_extraidos)}")
                else:
                    safe_log(f"      ⚠️ DATOS EXTRAÍDOS ES FALSY: {datos_extraidos}")

                if not datos_extraidos:
                    safe_log(f"      ⚠️ No se extrajeron datos del informe {numero_ihq}")
                    safe_log(f"      📝 Primeros 500 caracteres del texto consolidado:")
                    safe_log(f"      {texto_consolidado[:500]}")
                    logging.warning(f"extract_ihq_data retornó vacío para {numero_ihq}")
                    continue

                # Registrar extracción
                mapper.registrar_extractor("unified", datos_extraidos)

                # CRÍTICO: Mapear al formato de BD
                safe_log(f"      🗺️ Mapeando a formato BD...")
                datos_mapeados = map_to_database_format(datos_extraidos)

                if not datos_mapeados:
                    safe_log(f"      ⚠️ El mapeo retornó vacío para {numero_ihq}")
                    logging.warning(f"map_to_database_format retornó vacío para {numero_ihq}")
                    continue

                # Guardar debug map
                try:
                    mapper.guardar_mapa()
                except Exception as e:
                    safe_log(f"      ⚠️ Warning: Error guardando debug map: {e}")

                # Agregar a la lista de registros
                todos_los_registros.append(datos_mapeados)

                campos_extraidos = len([v for v in datos_extraidos.values() if v and str(v).strip()])
                safe_log(f"      ✅ {campos_extraidos} campos extraídos")

            except Exception as e:
                safe_log(f"      ❌ Error procesando informe {numero_ihq}: {e}")
                logging.error(f"Error completo en informe {numero_ihq}: {e}", exc_info=True)
                import traceback
                safe_log(f"      📋 Traceback: {traceback.format_exc()}")
                continue

        if not todos_los_registros:
            error_detallado = f"No se pudo extraer información de ningún informe en el PDF.\n\n"
            error_detallado += f"Detalles:\n"
            error_detallado += f"- PDF: {os.path.basename(file_path)}\n"
            error_detallado += f"- Segmentos detectados: {len(segmentos_ihq)}\n"
            error_detallado += f"- Casos que intentaron procesarse: {caso_num}\n\n"
            error_detallado += "Posibles causas:\n"
            error_detallado += "1. El PDF no contiene informes IHQ válidos\n"
            error_detallado += "2. El formato del PDF es diferente al esperado\n"
            error_detallado += "3. Los datos extraídos están vacíos o son inválidos\n\n"
            error_detallado += f"Casos encontrados: {list(segmentos_ihq.keys())}"
            safe_log(f"\n❌ ERROR: {error_detallado}")
            raise RuntimeError(error_detallado)

        # 4. GUARDAR TODOS LOS REGISTROS EN BD
        safe_log(f"💾 Paso 4/4: Guardando {len(todos_los_registros)} registro(s) en BD...")
        init_db()
        saved_count = save_records(todos_los_registros)

        safe_log(f"✅ {saved_count} registro(s) guardado(s) en BD")
        safe_log("="*60)
        safe_log("✅ PROCESAMIENTO COMPLETADO")
        safe_log(f"📊 Resumen: {len(segmentos_ihq)} informes detectados → {saved_count} registros guardados")
        safe_log("="*60)
        safe_log("\n⏭️  La auditoría IA se ejecutará después si el usuario lo elige")

        # NOTA: La auditoría IA ahora se ejecuta DESPUÉS, cuando el usuario
        # ve la ventana de resultados y decide si quiere auditar o no

        return saved_count

    except Exception as e:
        import traceback
        error_msg = f"Error en procesamiento IHQ: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_msg)
        safe_log(error_msg)
        raise Exception(error_msg)


__all__ = ['process_ihq_file']
