#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗺️ SISTEMA DE DEBUG Y MAPEO COMPLETO
======================================

Genera archivos JSON con el mapeo completo de todo el procesamiento:
- Texto OCR original
- Texto consolidado
- Datos extraídos por cada extractor
- Datos finales guardados en BD
- Metadata del proceso

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

# Configurar salida UTF-8 en Windows (con manejo de errores)
if sys.platform.startswith('win'):
    import io
    try:
        # Solo reconfigurar si stdout tiene buffer disponible
        if hasattr(sys.stdout, 'buffer') and not isinstance(sys.stdout, io.TextIOWrapper):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        # Ya está configurado o no es necesario
        pass

# Agregar path del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DebugMapper:
    """Sistema de mapeo y debug completo del procesamiento"""

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializar mapeador de debug

        Args:
            output_dir: Directorio de salida para archivos debug
        """
        self.output_dir = output_dir or (project_root / "data" / "debug_maps")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.current_map = None
        self.session_id = None

    def iniciar_sesion(self, numero_peticion: str, pdf_path: Optional[str] = None) -> str:
        """
        Inicia una nueva sesión de debug

        Args:
            numero_peticion: Número de petición IHQ
            pdf_path: Ruta al PDF procesado (opcional)

        Returns:
            ID de la sesión
        """
        timestamp = datetime.now()
        self.session_id = f"{numero_peticion}_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        self.current_map = {
            "session_id": self.session_id,
            "numero_peticion": numero_peticion,
            "timestamp": timestamp.isoformat(),
            "pdf_path": str(pdf_path) if pdf_path else None,
            "ocr": {
                "texto_original": None,
                "texto_consolidado": None,
                "metadata": {}
            },
            "extraccion": {
                # V2.0: Solo unified_extractor (sin redundancias de extractores individuales)
                "unified_extractor": {}
            },
            "base_datos": {
                "datos_guardados": {},  # V2.0: Contiene TODOS los campos incluyendo IHQ_ESTUDIOS_SOLICITADOS
                "campos_criticos": {},  # V2.0: Acceso rápido a campos críticos
                "columnas_mapeadas": {}
            },
            "validacion": {
                "campos_vacios": [],
                "campos_con_valor": [],
                "warnings": [],
                "errores": []
            },
            "correcciones_aplicadas": [],  # V5.3.9: Sistema unificado de correcciones
            "metadata": {  # V5.3.9: Metadata de correcciones
                "correcciones_totales": 0,
                "correcciones_por_tipo": {}
            },
            "metricas": {
                "tiempo_ocr_segundos": 0,
                "tiempo_extraccion_segundos": 0,
                "tiempo_total_segundos": 0,
                "caracteres_procesados": 0,
                "campos_extraidos": 0
            }
        }

        return self.session_id

    def registrar_ocr(
        self,
        texto_original: str,
        texto_consolidado: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Registra resultados del proceso OCR

        Args:
            texto_original: Texto crudo extraído del PDF
            texto_consolidado: Texto después de limpieza y consolidación
            metadata: Metadata adicional del proceso OCR
        """
        if not self.current_map:
            raise RuntimeError("Debe iniciar una sesión primero con iniciar_sesion()")

        self.current_map["ocr"]["texto_original"] = texto_original
        self.current_map["ocr"]["texto_consolidado"] = texto_consolidado
        self.current_map["ocr"]["metadata"] = metadata or {}

        # Calcular hash para verificación de integridad
        self.current_map["ocr"]["hash_original"] = hashlib.md5(
            texto_original.encode('utf-8')
        ).hexdigest()

        # Métricas
        self.current_map["metricas"]["caracteres_procesados"] = len(texto_original)

    def registrar_extractor(
        self,
        nombre_extractor: str,
        datos_extraidos: Dict[str, Any]
    ):
        """
        Registra datos extraídos por un extractor específico
        V2.0: Elimina redundancias - solo guarda unified_extractor

        Args:
            nombre_extractor: Nombre del extractor (patient, medical, biomarker, unified)
            datos_extraidos: Diccionario con los datos extraídos
        """
        if not self.current_map:
            raise RuntimeError("Debe iniciar una sesión primero con iniciar_sesion()")

        # V2.0: Solo guardar el extractor unificado para evitar redundancias
        # Los extractores individuales (patient, medical, biomarker) se fusionan en unified
        if nombre_extractor == "unified" or nombre_extractor == "unified_extractor":
            # V2.0.1: Limpiar datos extraídos para evitar duplicación
            datos_limpios = {}
            campos_guardados = set()

            # Prioridad: usar nombre con mayúscula inicial (formato BD) si existe
            # Mapeo de normalizaciones
            normalizaciones = {}

            for campo in datos_extraidos.keys():
                campo_lower = campo.lower()

                # Normalizar descripciones
                if 'descripcion' in campo_lower or 'diagnostico' in campo_lower:
                    if 'macroscopica' in campo_lower:
                        campo_norm = 'descripcion_macroscopica'
                    elif 'microscopica' in campo_lower:
                        campo_norm = 'descripcion_microscopica'
                    elif 'diagnostico' in campo_lower and 'descripcion' in campo_lower:
                        campo_norm = 'descripcion_diagnostico'
                    elif 'diagnostico' in campo_lower:
                        campo_norm = 'diagnostico'
                    else:
                        campo_norm = campo_lower
                # Normalizar edad (edad, Edad, edad_años -> Edad)
                elif campo_lower in ['edad', 'edad_años', 'edad_anos']:
                    campo_norm = 'Edad'
                # Normalizar géneros
                elif campo_lower in ['genero', 'género']:
                    campo_norm = 'Genero'
                # Normalizar estudios solicitados
                elif campo_lower in ['estudios_solicitados', 'estudios_solicitados_tabla']:
                    campo_norm = 'estudios_solicitados_tabla'  # Nombre descriptivo
                else:
                    # Usar nombre original si es mayúscula inicial, sino minúscula
                    campo_norm = campo if campo[0].isupper() else campo_lower

                normalizaciones[campo] = campo_norm

            # Aplicar normalizaciones y eliminar duplicados
            for campo, valor in datos_extraidos.items():
                campo_norm = normalizaciones[campo]

                # Solo guardar si no existe ya este campo normalizado
                if campo_norm not in campos_guardados:
                    # Priorizar valor no vacío si hay múltiples versiones
                    if campo_norm in datos_limpios:
                        valor_existente = datos_limpios[campo_norm]
                        # Si el valor existente está vacío pero este no, reemplazar
                        if (not valor_existente or str(valor_existente).strip() == '' or str(valor_existente) in ['0', 'N/A']) and \
                           valor and str(valor).strip() and str(valor) not in ['0', 'N/A']:
                            datos_limpios[campo_norm] = valor
                    else:
                        datos_limpios[campo_norm] = valor
                        campos_guardados.add(campo_norm)

            self.current_map["extraccion"]["unified_extractor"] = datos_limpios

            # Contar campos extraídos
            campos_no_vacios = sum(
                1 for v in datos_limpios.values()
                if v and str(v).strip() and str(v) not in ['N/A', 'None', '']
            )

            self.current_map["metricas"]["campos_extraidos"] = campos_no_vacios

    def registrar_base_datos(
        self,
        datos_guardados: Dict[str, Any],
        columnas_mapeadas: Optional[Dict[str, str]] = None
    ):
        """
        Registra TODOS los datos guardados en la base de datos
        V2.0: Guarda absolutamente todo incluyendo IHQ_ESTUDIOS_SOLICITADOS y todos los biomarcadores

        Args:
            datos_guardados: Diccionario COMPLETO con TODOS los datos guardados en BD
            columnas_mapeadas: Mapeo de campos extraídos a columnas de BD
        """
        if not self.current_map:
            raise RuntimeError("Debe iniciar una sesión primero con iniciar_sesion()")

        # V2.0: Guardar TODO sin filtros
        self.current_map["base_datos"]["datos_guardados"] = datos_guardados
        self.current_map["base_datos"]["columnas_mapeadas"] = columnas_mapeadas or {}

        # Estadísticas especiales para campos críticos
        campos_criticos = {
            'IHQ_ESTUDIOS_SOLICITADOS': datos_guardados.get('IHQ_ESTUDIOS_SOLICITADOS'),
            'IHQ_KI-67': datos_guardados.get('IHQ_KI-67'),
            'IHQ_HER2': datos_guardados.get('IHQ_HER2'),
            'IHQ_RECEPTOR_ESTROGENOS': datos_guardados.get('IHQ_RECEPTOR_ESTROGENOS'),
            'IHQ_RECEPTOR_PROGESTERONA': datos_guardados.get('IHQ_RECEPTOR_PROGESTERONA'),
        }

        self.current_map["base_datos"]["campos_criticos"] = campos_criticos

        # Validar campos
        for campo, valor in datos_guardados.items():
            if not valor or str(valor).strip() in ['', 'N/A', 'None']:
                self.current_map["validacion"]["campos_vacios"].append(campo)
            else:
                self.current_map["validacion"]["campos_con_valor"].append(campo)

    def agregar_warning(self, mensaje: str, contexto: Optional[Dict[str, Any]] = None):
        """
        Agrega un warning al mapa de debug

        Args:
            mensaje: Mensaje de warning
            contexto: Contexto adicional del warning
        """
        if not self.current_map:
            return

        self.current_map["validacion"]["warnings"].append({
            "mensaje": mensaje,
            "contexto": contexto or {},
            "timestamp": datetime.now().isoformat()
        })

    def agregar_error(self, mensaje: str, contexto: Optional[Dict[str, Any]] = None):
        """
        Agrega un error al mapa de debug

        Args:
            mensaje: Mensaje de error
            contexto: Contexto adicional del error
        """
        if not self.current_map:
            return

        self.current_map["validacion"]["errores"].append({
            "mensaje": mensaje,
            "contexto": contexto or {},
            "timestamp": datetime.now().isoformat()
        })

    def registrar_metricas(
        self,
        tiempo_ocr: float = 0,
        tiempo_extraccion: float = 0,
        tiempo_total: float = 0
    ):
        """
        Registra métricas de rendimiento

        Args:
            tiempo_ocr: Tiempo de procesamiento OCR en segundos
            tiempo_extraccion: Tiempo de extracción de datos en segundos
            tiempo_total: Tiempo total del proceso en segundos
        """
        if not self.current_map:
            return

        self.current_map["metricas"]["tiempo_ocr_segundos"] = tiempo_ocr
        self.current_map["metricas"]["tiempo_extraccion_segundos"] = tiempo_extraccion
        self.current_map["metricas"]["tiempo_total_segundos"] = tiempo_total

    def registrar_correcciones(self, correcciones: List[Dict]):
        """
        Registra todas las correcciones aplicadas durante extracción (V5.3.9)

        Args:
            correcciones: Lista de diccionarios con correcciones aplicadas
                Cada corrección debe tener: tipo, campo, valor_original, valor_corregido, razon
        """
        if not self.current_map:
            return

        self.current_map["correcciones_aplicadas"] = correcciones

        # Calcular estadísticas
        total = len(correcciones)
        por_tipo = {}
        for corr in correcciones:
            tipo = corr.get("tipo", "unknown")
            por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

        self.current_map["metadata"]["correcciones_totales"] = total
        self.current_map["metadata"]["correcciones_por_tipo"] = por_tipo

    def guardar_mapa(self, custom_filename: Optional[str] = None) -> Path:
        """
        Guarda el mapa de debug en un archivo JSON

        Args:
            custom_filename: Nombre personalizado para el archivo (opcional)

        Returns:
            Path al archivo guardado
        """
        if not self.current_map:
            raise RuntimeError("No hay mapa de debug activo para guardar")

        filename = custom_filename or f"debug_map_{self.session_id}.json"
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.current_map, f, indent=2, ensure_ascii=False)

        return output_path

    def generar_resumen(self) -> Dict[str, Any]:
        """
        Genera un resumen ejecutivo del mapa de debug

        Returns:
            Dict con resumen ejecutivo
        """
        if not self.current_map:
            return {}

        total_campos = len(self.current_map["validacion"]["campos_vacios"]) + \
                      len(self.current_map["validacion"]["campos_con_valor"])

        completitud = (
            len(self.current_map["validacion"]["campos_con_valor"]) / total_campos * 100
            if total_campos > 0 else 0
        )

        resumen = {
            "numero_peticion": self.current_map["numero_peticion"],
            "timestamp": self.current_map["timestamp"],
            "completitud_porcentaje": round(completitud, 2),
            "campos_totales": total_campos,
            "campos_completos": len(self.current_map["validacion"]["campos_con_valor"]),
            "campos_vacios": len(self.current_map["validacion"]["campos_vacios"]),
            "warnings": len(self.current_map["validacion"]["warnings"]),
            "errores": len(self.current_map["validacion"]["errores"]),
            "tiempo_total_segundos": self.current_map["metricas"]["tiempo_total_segundos"],
            "caracteres_procesados": self.current_map["metricas"]["caracteres_procesados"]
        }

        return resumen

    def exportar_para_llm(self) -> Dict[str, Any]:
        """
        Exporta el mapa en un formato optimizado para envío a LLM

        Returns:
            Dict con datos formateados para LLM
        """
        if not self.current_map:
            return {}

        # Formato condensado para LLM
        llm_data = {
            "numero_peticion": self.current_map["numero_peticion"],
            "texto_procesado": self.current_map["ocr"]["texto_consolidado"],
            "datos_extraidos": self.current_map["extraccion"]["unified_extractor"],
            "datos_guardados_bd": self.current_map["base_datos"]["datos_guardados"],
            "campos_vacios": self.current_map["validacion"]["campos_vacios"],
            "warnings": [w["mensaje"] for w in self.current_map["validacion"]["warnings"]],
            "errores": [e["mensaje"] for e in self.current_map["validacion"]["errores"]],
            "resumen": self.generar_resumen()
        }

        return llm_data

    @staticmethod
    def cargar_mapa(filepath: Path) -> Dict[str, Any]:
        """
        Carga un mapa de debug desde archivo

        Args:
            filepath: Ruta al archivo JSON

        Returns:
            Dict con el mapa de debug
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def listar_mapas(output_dir: Optional[Path] = None) -> List[Path]:
        """
        Lista todos los mapas de debug disponibles

        Args:
            output_dir: Directorio donde buscar (opcional)

        Returns:
            Lista de rutas a archivos de mapas
        """
        search_dir = output_dir or (project_root / "data" / "debug_maps")

        if not search_dir.exists():
            return []

        return sorted(
            search_dir.glob("debug_map_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )


# Funciones de utilidad para integración con el sistema existente

def crear_mapa_desde_procesamiento(
    numero_peticion: str,
    pdf_path: str,
    texto_ocr: str,
    texto_consolidado: str,
    datos_unified: Dict[str, Any],
    datos_bd: Dict[str, Any],
    **kwargs
) -> Path:
    """
    Crea un mapa de debug completo desde un procesamiento
    V2.0: Simplificado - solo unified_extractor y datos_bd completos

    Args:
        numero_peticion: Número de petición IHQ
        pdf_path: Ruta al PDF
        texto_ocr: Texto OCR original
        texto_consolidado: Texto consolidado
        datos_unified: Datos del extractor unificado (incluye patient + medical + biomarker)
        datos_bd: Datos COMPLETOS guardados en BD (incluye IHQ_ESTUDIOS_SOLICITADOS)
        **kwargs: Argumentos adicionales (tiempos, metadata, etc.)

    Returns:
        Path al archivo de mapa guardado
    """
    mapper = DebugMapper()
    mapper.iniciar_sesion(numero_peticion, pdf_path)

    # Registrar OCR
    mapper.registrar_ocr(
        texto_ocr,
        texto_consolidado,
        kwargs.get('ocr_metadata', {})
    )

    # V2.0: Solo registrar unified_extractor (ya contiene todo)
    mapper.registrar_extractor("unified", datos_unified)

    # V2.0: Registrar BD con TODOS los datos (incluyendo IHQ_ESTUDIOS_SOLICITADOS)
    mapper.registrar_base_datos(datos_bd)

    # Registrar correcciones si existen
    if 'correcciones' in kwargs:
        mapper.registrar_correcciones(kwargs['correcciones'])

    # Registrar métricas
    mapper.registrar_metricas(
        tiempo_ocr=kwargs.get('tiempo_ocr', 0),
        tiempo_extraccion=kwargs.get('tiempo_extraccion', 0),
        tiempo_total=kwargs.get('tiempo_total', 0)
    )

    # Guardar
    return mapper.guardar_mapa()


if __name__ == "__main__":
    # Ejemplo de uso
    logging.info("🗺️ SISTEMA DE DEBUG Y MAPEO - Ejemplo de uso")
    logging.info("=" * 80)

    # Crear una sesión de ejemplo
    mapper = DebugMapper()
    mapper.iniciar_sesion("IHQ250999", "ejemplo.pdf")

    # Simular datos
    mapper.registrar_ocr(
        "Texto OCR ejemplo...",
        "Texto consolidado ejemplo...",
        {"dpi": 300, "psm": 6}
    )

    mapper.registrar_extractor("patient", {
        "nombre_completo": "JUAN PEREZ",
        "identificacion": "12345678",
        "edad": "45"
    })

    mapper.registrar_base_datos({
        "N. peticion": "IHQ250999",
        "Nombre": "JUAN PEREZ",
        "Edad": "45"
    })

    # Guardar
    output = mapper.guardar_mapa()
    logging.info(f"\n✅ Mapa de debug guardado en: {output}")

    # Mostrar resumen
    resumen = mapper.generar_resumen()
    logging.info(f"\n📊 Resumen:")
    logging.info(json.dumps(resumen, indent=2, ensure_ascii=False))
