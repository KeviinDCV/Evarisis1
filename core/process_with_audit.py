#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 PROCESAMIENTO CON AUDITORÍA INTEGRADA
========================================

Wrapper que reemplaza process_ihq_paths() para integrar auditoría IA
automáticamente en el flujo normal de procesamiento.

ESTE ARCHIVO SE USA DESDE UI.PY

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    # Solo configurar si no está ya configurado Y está accesible
    try:
        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding != 'utf-8':
            if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

    try:
        if hasattr(sys.stderr, 'encoding') and sys.stderr.encoding != 'utf-8':
            if hasattr(sys.stderr, 'buffer') and not sys.stderr.closed:
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError, OSError):
        pass

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)


def process_ihq_paths_with_audit(
    pdf_paths: List[str],
    output_dir: str,
    ui_callback_auditoria: Optional[Callable] = None,
    log_callback: Optional[Callable] = None
) -> int:
    """
    Procesa PDFs con generación de debug maps y opción de auditoría IA

    Args:
        pdf_paths: Lista de rutas a PDFs
        output_dir: Directorio de salida
        ui_callback_auditoria: Callback para mostrar ventana de auditoría
        log_callback: Callback para logging en UI

    Returns:
        Número de registros procesados
    """
    if not pdf_paths:
        logger.warning("⚠️ No se proporcionaron PDFs para procesar")
        return 0

    # Importar módulos necesarios
    from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase
    from core.unified_extractor import extract_ihq_data
    from core.database_manager import save_records, get_registro_by_peticion
    from core.debug_mapper import DebugMapper
    import re

    if log_callback:
        log_callback(f"🚀 Procesando {len(pdf_paths)} archivo(s) PDF...")

    casos_para_auditoria = []
    total_registros = 0

    for idx, pdf_path in enumerate(pdf_paths, 1):
        try:
            if log_callback:
                log_callback(f"\n{'='*50}")
                log_callback(f"📄 Procesando archivo {idx}/{len(pdf_paths)}: {Path(pdf_path).name}")

            # 1. EXTRACCIÓN OCR
            if log_callback:
                log_callback("  🔍 Paso 1/5: Extrayendo texto con OCR...")

            texto_ocr_completo = pdf_to_text_enhanced(pdf_path)

            if not texto_ocr_completo or len(texto_ocr_completo.strip()) < 10:
                if log_callback:
                    log_callback("  ⚠️ PDF vacío o con texto insuficiente, omitiendo...")
                continue

            # 2. CONSOLIDACIÓN Y SEGMENTACIÓN
            if log_callback:
                log_callback("  🔀 Paso 2/5: Consolidando y segmentando casos IHQ...")

            segmentos_lista = segment_reports_multicase(texto_ocr_completo)

            if not segmentos_lista:
                if log_callback:
                    log_callback("  ⚠️ No se encontraron casos IHQ válidos en el PDF")
                continue

            # Extraer números IHQ de cada segmento
            segmentos_ihq = {}
            for segmento in segmentos_lista:
                # Buscar el código IHQ en el segmento
                ihq_match = re.search(r'IHQ(\d{6})', segmento)
                if ihq_match:
                    numero_ihq = f"IHQ{ihq_match.group(1)}"
                    segmentos_ihq[numero_ihq] = segmento

            if not segmentos_ihq:
                if log_callback:
                    log_callback("  ⚠️ No se pudieron extraer números IHQ de los segmentos")
                continue

            if log_callback:
                log_callback(f"  ✅ Encontrados {len(segmentos_ihq)} caso(s) IHQ")

            # 3. PROCESAR CADA CASO IHQ
            for caso_num, (numero_ihq, texto_consolidado) in enumerate(segmentos_ihq.items(), 1):
                if log_callback:
                    log_callback(f"\n  📋 Procesando caso {caso_num}/{len(segmentos_ihq)}: {numero_ihq}")

                # === CREAR DEBUG MAPPER ===
                mapper = DebugMapper()
                mapper.iniciar_sesion(numero_ihq, pdf_path)

                # Registrar OCR
                mapper.registrar_ocr(
                    texto_original=texto_ocr_completo,
                    texto_consolidado=texto_consolidado,
                    metadata={
                        'pdf_path': pdf_path,
                        'numero_ihq': numero_ihq,
                        'caso_num': caso_num,
                        'total_casos': len(segmentos_ihq)
                    }
                )

                if log_callback:
                    log_callback(f"    🔍 Paso 3/5: Extrayendo datos médicos...")

                # === EXTRAER DATOS ===
                datos_extraidos = extract_ihq_data(texto_consolidado)

                # Registrar extracción en debug map
                mapper.registrar_extractor("unified", datos_extraidos)

                if log_callback:
                    campos_extraidos = len([v for v in datos_extraidos.values() if v and str(v).strip()])
                    log_callback(f"    ✅ Extraídos {campos_extraidos} campos con datos")

                # === MAPEAR A FORMATO DE BASE DE DATOS ===
                if log_callback:
                    log_callback(f"    🔄 Paso 4a/5: Mapeando datos al formato de BD...")

                try:
                    from core.unified_extractor import map_to_database_format
                    
                    # CRÍTICO: Mapear antes de guardar
                    datos_mapeados = map_to_database_format(datos_extraidos)
                    
                    if log_callback:
                        log_callback(f"    ✅ Mapeo completado: {len(datos_mapeados)} campos preparados")
                
                except Exception as e:
                    if log_callback:
                        log_callback(f"    ❌ Error mapeando datos: {e}")
                    mapper.agregar_error(f"Error Mapeo: {str(e)}")
                    continue

                # === GUARDAR EN BASE DE DATOS ===
                if log_callback:
                    log_callback(f"    💾 Paso 4b/5: Guardando en base de datos...")

                try:
                    # save_records espera una lista de diccionarios MAPEADOS
                    count = save_records([datos_mapeados])

                    if count > 0:
                        total_registros += 1
                        if log_callback:
                            log_callback(f"    ✅ Registro guardado correctamente")
                    else:
                        if log_callback:
                            log_callback(f"    ⚠️ Warning: No se pudo guardar el registro")

                except Exception as e:
                    if log_callback:
                        log_callback(f"    ❌ Error guardando en BD: {e}")
                    mapper.agregar_error(f"Error BD: {str(e)}")
                    continue

                # === OBTENER DATOS GUARDADOS ===
                datos_bd = get_registro_by_peticion(numero_ihq)

                # Registrar en debug map
                if datos_bd:
                    mapper.registrar_base_datos(datos_bd)
                else:
                    mapper.agregar_warning(f"No se pudieron recuperar datos de BD para {numero_ihq}")

                # === GUARDAR DEBUG MAP ===
                if log_callback:
                    log_callback(f"    🗺️ Paso 5/5: Generando debug map...")

                try:
                    debug_map_path = mapper.guardar_mapa()
                    if log_callback:
                        log_callback(f"    ✅ Debug map guardado: {debug_map_path.name}")
                except Exception as e:
                    if log_callback:
                        log_callback(f"    ⚠️ Warning: Error guardando debug map: {e}")

                # === PREPARAR PARA AUDITORÍA ===
                if datos_bd:
                    casos_para_auditoria.append({
                        'numero_peticion': numero_ihq,
                        'debug_map': mapper.current_map,
                        'datos_bd': datos_bd
                    })

        except Exception as e:
            if log_callback:
                log_callback(f"  ❌ Error procesando {Path(pdf_path).name}: {e}")
            logger.error(f"Error procesando {pdf_path}: {e}", exc_info=True)
            continue

    # === RESUMEN FINAL ===
    if log_callback:
        log_callback(f"\n{'='*50}")
        log_callback(f"✅ PROCESAMIENTO COMPLETADO")
        log_callback(f"📊 Total de registros guardados: {total_registros}")
        log_callback(f"🗺️ Debug maps generados: {len(casos_para_auditoria)}")

    # === CALLBACK PARA AUDITORÍA IA ===
    # DESACTIVADO: Los datos se mapean correctamente ahora, auditoría IA ya no es necesaria
    # La auditoría IA tomaba 25+ minutos para 50 casos sin agregar valor significativo
    # Si necesitas validación, usa: python cli_herramientas.py validar --ihq XXX --pdf archivo.pdf

    AUDITORIA_IA_ACTIVADA = True  # Cambiar a True solo si realmente lo necesitas

    if AUDITORIA_IA_ACTIVADA and ui_callback_auditoria and casos_para_auditoria:
        if log_callback:
            log_callback(f"\n🤖 Iniciando auditoría con IA...")

        # Llamar callback que mostrará ventana de auditoría
        ui_callback_auditoria(casos_para_auditoria)
    else:
        if log_callback:
            if not casos_para_auditoria:
                log_callback(f"\n⚠️ No hay casos para auditar")
            elif not AUDITORIA_IA_ACTIVADA:
                log_callback(f"\n✅ Auditoría IA desactivada - datos mapeados correctamente")
                log_callback(f"💡 Para validar casos, usa: python cli_herramientas.py validar --ihq XXX --pdf archivo.pdf")
            else:
                log_callback(f"\n💡 Auditoría IA omitida (callback no proporcionado)")

    return total_registros


def crear_callback_auditoria_para_ui(app_instance):
    """
    Crea un callback para mostrar ventana de auditoría desde la UI

    Args:
        app_instance: Instancia de la clase App de ui.py

    Returns:
        Función callback
    """
    def callback_auditoria(casos):
        """Callback que se ejecuta en el thread de UI"""

        def mostrar_auditoria():
            from core.ventana_auditoria_ia import mostrar_ventana_auditoria

            def on_auditoria_completada(resultados):
                # Cuando termine la auditoría, refrescar datos
                if hasattr(app_instance, 'refresh_data_and_table'):
                    app_instance.refresh_data_and_table()

                # Log de resultado
                if hasattr(app_instance, 'log_to_widget'):
                    total_correcciones = sum(
                        r.get('correcciones_aplicadas', 0)
                        for r in resultados
                        if r.get('exito')
                    )

                    app_instance.log_to_widget(f"\n{'='*50}")
                    app_instance.log_to_widget(f"🤖 AUDITORÍA IA COMPLETADA")
                    app_instance.log_to_widget(f"✅ Casos auditados: {len(resultados)}")
                    app_instance.log_to_widget(f"🔧 Total de correcciones aplicadas: {total_correcciones}")
                    app_instance.log_to_widget(f"{'='*50}\n")

            # Mostrar ventana de auditoría
            mostrar_ventana_auditoria(
                app_instance,
                casos,
                on_auditoria_completada
            )

        # Ejecutar en thread de UI
        app_instance.after(0, mostrar_auditoria)

    return callback_auditoria


if __name__ == "__main__":
    # Test básico
    logging.info("🔄 Procesamiento con Auditoría - Test")

    import tempfile

    def log_test(msg):
        logging.info(f"  {msg}")

    # Simular procesamiento (requeriría PDFs reales)
    # count = process_ihq_paths_with_audit(
    #     pdf_paths=["test.pdf"],
    #     output_dir=tempfile.gettempdir(),
    #     ui_callback_auditoria=None,
    #     log_callback=log_test
    # )

    logging.info("✅ Módulo listo para usar")
