#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 PROCESAMIENTO CON IA - INTEGRACIÓN COMPLETA
==============================================

Wrapper del procesamiento normal que agrega:
1. Generación de debug maps
2. Validación con IA
3. Correcciones automáticas (opcional)

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Imports del sistema existente
from core.processors.ocr_processor import pdf_to_text_enhanced, consolidate_text_by_ihq
from core.extractors.patient_extractor import extract_patient_data
from core.extractors.medical_extractor import extract_medical_data
from core.extractors.biomarker_extractor import extract_biomarkers
from core.unified_extractor import extract_ihq_data
from core.database_manager import insert_or_update_registro

# Imports de nuevos módulos IA
from core.debug_mapper import DebugMapper, crear_mapa_desde_procesamiento
from core.llm_client import LMStudioClient


class ProcesadorConIA:
    """Procesador mejorado con validación y corrección IA"""

    def __init__(
        self,
        generar_debug: bool = True,
        validar_con_ia: bool = False,
        aplicar_correcciones: bool = False,
        llm_endpoint: str = "http://127.0.0.1:1234"
    ):
        """
        Inicializar procesador con IA

        Args:
            generar_debug: Si True, genera archivos debug_map
            validar_con_ia: Si True, valida con LLM (requiere LM Studio activo)
            aplicar_correcciones: Si True, aplica correcciones sugeridas por IA
            llm_endpoint: Endpoint del servidor LM Studio
        """
        self.generar_debug = generar_debug
        self.validar_con_ia = validar_con_ia
        self.aplicar_correcciones = aplicar_correcciones

        # Inicializar cliente LLM si se necesita
        self.llm_client = None
        if validar_con_ia:
            try:
                self.llm_client = LMStudioClient(endpoint=llm_endpoint)
                print("✅ Cliente LLM inicializado correctamente")
            except Exception as e:
                print(f"⚠️ No se pudo inicializar LLM: {e}")
                print("  Continuando sin validación IA...")
                self.validar_con_ia = False

    def procesar_pdf(
        self,
        pdf_path: str,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Procesa un PDF completo con generación de debug y validación IA

        Args:
            pdf_path: Ruta al archivo PDF
            progress_callback: Callback para actualizar progreso (opcional)

        Returns:
            Lista de resultados por cada caso IHQ procesado
        """
        print(f"\n🔄 PROCESANDO PDF CON IA: {Path(pdf_path).name}")
        print("=" * 80)

        tiempo_inicio = time.time()

        # 1. OCR
        if progress_callback:
            progress_callback("Extrayendo texto del PDF...")

        print("📄 Paso 1/5: Extracción OCR...")
        tiempo_ocr_inicio = time.time()
        texto_ocr_completo = pdf_to_text_enhanced(pdf_path)
        tiempo_ocr = time.time() - tiempo_ocr_inicio

        print(f"  ✅ Extraídos {len(texto_ocr_completo)} caracteres en {tiempo_ocr:.2f}s")

        # 2. Consolidación y segmentación
        if progress_callback:
            progress_callback("Consolidando y segmentando casos IHQ...")

        print("🔀 Paso 2/5: Consolidación y segmentación...")
        segmentos_ihq = consolidate_text_by_ihq(texto_ocr_completo)

        print(f"  ✅ Encontrados {len(segmentos_ihq)} casos IHQ")

        # 3. Procesar cada caso
        resultados = []

        for idx, (numero_ihq, texto_consolidado) in enumerate(segmentos_ihq.items(), 1):
            if progress_callback:
                progress_callback(f"Procesando caso {idx}/{len(segmentos_ihq)}: {numero_ihq}")

            print(f"\n📋 Paso 3/5: Procesando caso {numero_ihq} ({idx}/{len(segmentos_ihq)})...")

            resultado_caso = self._procesar_caso_ihq(
                numero_ihq=numero_ihq,
                texto_consolidado=texto_consolidado,
                texto_ocr_original=texto_ocr_completo,
                pdf_path=pdf_path,
                tiempo_ocr=tiempo_ocr
            )

            resultados.append(resultado_caso)

        tiempo_total = time.time() - tiempo_inicio

        print(f"\n✅ PROCESAMIENTO COMPLETO")
        print(f"  📊 Casos procesados: {len(resultados)}")
        print(f"  ⏱️ Tiempo total: {tiempo_total:.2f}s")
        print("=" * 80)

        return resultados

    def _procesar_caso_ihq(
        self,
        numero_ihq: str,
        texto_consolidado: str,
        texto_ocr_original: str,
        pdf_path: str,
        tiempo_ocr: float
    ) -> Dict[str, Any]:
        """
        Procesa un caso IHQ individual con todas las mejoras IA

        Args:
            numero_ihq: Número de petición IHQ
            texto_consolidado: Texto consolidado del caso
            texto_ocr_original: Texto OCR completo (para debug)
            pdf_path: Ruta al PDF original
            tiempo_ocr: Tiempo que tomó el OCR

        Returns:
            Dict con resultado del procesamiento
        """
        tiempo_inicio_caso = time.time()

        # Inicializar debug mapper si está habilitado
        mapper = None
        if self.generar_debug:
            mapper = DebugMapper()
            mapper.iniciar_sesion(numero_ihq, pdf_path)

            # Registrar OCR
            mapper.registrar_ocr(
                texto_original=texto_ocr_original,
                texto_consolidado=texto_consolidado,
                metadata={
                    "pdf_path": pdf_path,
                    "numero_ihq": numero_ihq,
                    "longitud_texto": len(texto_consolidado)
                }
            )

        # 4. Extracción de datos
        print(f"  🔍 Extrayendo datos...")
        tiempo_extraccion_inicio = time.time()

        # Extraer con cada extractor
        datos_patient = extract_patient_data(texto_consolidado)
        datos_medical = extract_medical_data(texto_consolidado)
        datos_biomarker = extract_biomarkers(texto_consolidado)

        # Unificar datos
        datos_unified = extract_ihq_data(texto_consolidado)

        tiempo_extraccion = time.time() - tiempo_extraccion_inicio

        # Registrar en debug map
        if mapper:
            mapper.registrar_extractor("patient", datos_patient)
            mapper.registrar_extractor("medical", datos_medical)
            mapper.registrar_extractor("biomarker", datos_biomarker)
            mapper.registrar_extractor("unified", datos_unified)

        # 5. Validación con IA (opcional)
        validacion_ia = None
        correcciones_aplicadas = []

        if self.validar_con_ia and self.llm_client:
            print(f"  🤖 Validando con IA...")

            try:
                # Validar campos críticos
                campos_criticos = [
                    "numero_peticion", "identificacion", "nombre_completo",
                    "edad", "genero", "diagnostico", "organo"
                ]

                validacion_ia = self.llm_client.validar_multiple_campos(
                    datos_extraidos=datos_unified,
                    texto_original=texto_consolidado,
                    campos_a_validar=campos_criticos
                )

                # Aplicar correcciones si está habilitado
                if self.aplicar_correcciones:
                    print(f"  🔧 Aplicando correcciones IA...")
                    correcciones_aplicadas = self._aplicar_correcciones_ia(
                        datos_unified=datos_unified,
                        validacion_ia=validacion_ia,
                        mapper=mapper
                    )

                print(f"  ✅ Validación IA completada")

            except Exception as e:
                print(f"  ⚠️ Error en validación IA: {e}")
                if mapper:
                    mapper.agregar_error(f"Error validación IA: {str(e)}")

        # 6. Guardar en base de datos
        print(f"  💾 Guardando en base de datos...")

        try:
            # Usar datos corregidos si hay correcciones aplicadas
            datos_para_bd = datos_unified.copy()

            for correccion in correcciones_aplicadas:
                campo = correccion["campo"]
                valor_nuevo = correccion["valor_nuevo"]
                datos_para_bd[campo] = valor_nuevo

            # Insertar o actualizar
            exito_bd = insert_or_update_registro(datos_para_bd)

            if mapper:
                mapper.registrar_base_datos(
                    datos_guardados=datos_para_bd,
                    columnas_mapeadas={}  # TODO: Agregar mapeo real
                )

            print(f"  ✅ {'Actualizado' if exito_bd else 'Insertado'} en BD")

        except Exception as e:
            print(f"  ❌ Error guardando en BD: {e}")
            if mapper:
                mapper.agregar_error(f"Error BD: {str(e)}")

        # 7. Guardar debug map
        debug_map_path = None
        if mapper:
            tiempo_total_caso = time.time() - tiempo_inicio_caso

            mapper.registrar_metricas(
                tiempo_ocr=tiempo_ocr,
                tiempo_extraccion=tiempo_extraccion,
                tiempo_total=tiempo_total_caso
            )

            try:
                debug_map_path = mapper.guardar_mapa()
                print(f"  📁 Debug map guardado: {debug_map_path.name}")
            except Exception as e:
                print(f"  ⚠️ Error guardando debug map: {e}")

        # Resultado del caso
        return {
            "numero_ihq": numero_ihq,
            "exito": True,
            "datos_extraidos": datos_unified,
            "validacion_ia": validacion_ia,
            "correcciones_aplicadas": correcciones_aplicadas,
            "debug_map_path": str(debug_map_path) if debug_map_path else None,
            "metricas": {
                "tiempo_ocr": tiempo_ocr,
                "tiempo_extraccion": tiempo_extraccion,
                "tiempo_total": time.time() - tiempo_inicio_caso
            }
        }

    def _aplicar_correcciones_ia(
        self,
        datos_unified: Dict[str, Any],
        validacion_ia: Dict[str, Any],
        mapper: Optional[DebugMapper] = None
    ) -> List[Dict[str, Any]]:
        """
        Aplica correcciones sugeridas por IA

        Args:
            datos_unified: Datos unificados extraídos
            validacion_ia: Resultados de validación IA
            mapper: Debug mapper (opcional)

        Returns:
            Lista de correcciones aplicadas
        """
        correcciones = []

        validaciones = validacion_ia.get("validaciones", {})

        for campo, validacion in validaciones.items():
            if not validacion.get("exito"):
                continue

            val_data = validacion.get("validacion", {})
            valor_sugerido = val_data.get("valor_sugerido")

            if valor_sugerido and valor_sugerido != datos_unified.get(campo):
                confianza = val_data.get("confianza", 0.0)

                # Solo aplicar correcciones con alta confianza
                if confianza >= 0.8:
                    correcciones.append({
                        "campo": campo,
                        "valor_original": datos_unified.get(campo),
                        "valor_nuevo": valor_sugerido,
                        "confianza": confianza,
                        "razon": val_data.get("razonamiento", "")
                    })

                    # Actualizar datos
                    datos_unified[campo] = valor_sugerido

                    if mapper:
                        mapper.agregar_warning(
                            f"Corrección IA aplicada en campo '{campo}'",
                            {
                                "valor_original": datos_unified.get(campo),
                                "valor_nuevo": valor_sugerido,
                                "confianza": confianza
                            }
                        )

        return correcciones


def procesar_pdf_con_ia_simple(
    pdf_path: str,
    generar_debug: bool = True,
    validar_con_ia: bool = False
) -> List[Dict[str, Any]]:
    """
    Función simplificada para procesar PDF con IA

    Args:
        pdf_path: Ruta al PDF
        generar_debug: Generar debug maps
        validar_con_ia: Validar con IA

    Returns:
        Lista de resultados
    """
    procesador = ProcesadorConIA(
        generar_debug=generar_debug,
        validar_con_ia=validar_con_ia,
        aplicar_correcciones=False  # Por seguridad, no aplicar automáticamente
    )

    return procesador.procesar_pdf(pdf_path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="🤖 Procesador con IA v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--pdf",
        type=str,
        required=True,
        help="Ruta al archivo PDF"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=True,
        help="Generar archivos debug_map (default: True)"
    )

    parser.add_argument(
        "--validar-ia",
        action="store_true",
        help="Validar con IA (requiere LM Studio activo)"
    )

    parser.add_argument(
        "--aplicar-correcciones",
        action="store_true",
        help="Aplicar correcciones sugeridas por IA automáticamente"
    )

    args = parser.parse_args()

    # Procesar
    procesador = ProcesadorConIA(
        generar_debug=args.debug,
        validar_con_ia=args.validar_ia,
        aplicar_correcciones=args.aplicar_correcciones
    )

    resultados = procesador.procesar_pdf(args.pdf)

    # Mostrar resumen
    print("\n" + "=" * 80)
    print("📊 RESUMEN DE PROCESAMIENTO")
    print("=" * 80)

    for resultado in resultados:
        print(f"\n📋 {resultado['numero_ihq']}")
        print(f"  ✅ Extraído correctamente")

        if resultado.get("validacion_ia"):
            val_ia = resultado["validacion_ia"]
            print(f"  🤖 Validación IA: {val_ia.get('campos_validados', 0)} campos")

        if resultado.get("correcciones_aplicadas"):
            print(f"  🔧 Correcciones aplicadas: {len(resultado['correcciones_aplicadas'])}")

        if resultado.get("debug_map_path"):
            print(f"  📁 Debug map: {Path(resultado['debug_map_path']).name}")

        metricas = resultado.get("metricas", {})
        print(f"  ⏱️ Tiempo: {metricas.get('tiempo_total', 0):.2f}s")

    print("\n" + "=" * 80)
