#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗺️ SISTEMA DE DEBUG Y MAPEO OPTIMIZADO
========================================

Genera archivos JSON con el mapeo del procesamiento de forma OPTIMIZADA:
- Texto OCR consolidado (NO guarda texto_original completo - ahorro 95%)
- Datos extraídos por extractor unificado
- Solo campos críticos de BD (NO duplica SQLite - ahorro 87%)
- Estadísticas y contadores (NO listas completas - ahorro 97%)
- Metadata del proceso

V3.0 OPTIMIZACIÓN NIVEL 1:
- Eliminado: ocr.texto_original (193KB → 0KB)
- Eliminado: base_datos.datos_guardados completo (40KB → 5KB críticos)
- Eliminado: validacion.campos_vacios/con_valor listas (150 items → 5 top críticos)
- Resultado: 87KB → 10KB por debug_map (88% reducción)

V3.1 MEJORA DINÁMICA:
- Campos críticos ahora incluyen AUTOMÁTICAMENTE los biomarcadores en IHQ_ESTUDIOS_SOLICITADOS
- Ejemplo: Si ESTUDIOS_SOLICITADOS = "HEPATOCITO, CD34, CK7", se agregan IHQ_HEPATOCITO, IHQ_CD34, IHQ_CK7
- Auditoría más precisa: muestra valores reales de los biomarcadores solicitados

V3.1.1 CORRECCIÓN DUPLICADOS:
- Eliminada duplicación de biomarcadores (IHQ_KI-67 + ki-67)
- Solo se guardan versiones con prefijo IHQ_ (se descartan minúsculas sin prefijo)
- Ejemplo: Antes guardaba "IHQ_KI-67: 50%" Y "ki-67: 50%", ahora solo "IHQ_KI-67: 50%"

V3.1.2 FIX MAPEO P16/P40 (IHQ251010):
- Agregadas variaciones con _ESTADO para biomarcadores P16 y P40
- Ahora detecta IHQ_P16_ESTADO cuando ESTUDIOS_SOLICITADOS contiene "P16"
- Ahora detecta IHQ_P40_ESTADO cuando ESTUDIOS_SOLICITADOS contiene "P40"
- Fix: P16 y P40 ahora aparecen en campos_criticos del debug_map

V6.4.21 FIX MAPEO P40 CON ESPACIO (IHQ250025):
- Problema: "P 40" (con espacio) en ESTUDIOS_SOLICITADOS no mapeaba a IHQ_P40_ESTADO
- Causa: Las variaciones generadas ('IHQ_P 40_ESTADO', 'IHQ_P_40_ESTADO') no coincidían con columna real
- Solución: Casos especiales explícitos para P 40/P-40/P40 → IHQ_P40_ESTADO (línea 415)
- Solución: Casos especiales explícitos para P 16/P-16/P16 → IHQ_P16_ESTADO (línea 419)
- Efecto: P40 y P16 ahora aparecen en campos_criticos con TODAS sus variantes de escritura

V6.4.40 FIX MAPEO IDH (IHQ250175):
- Problema: "IDH" en ESTUDIOS_SOLICITADOS no mapeaba a IHQ_IDH1
- Causa: Las variaciones generadas ('IHQ_IDH', 'IHQ_IDH_ESTADO') no incluían IHQ_IDH1
- Solución: Caso especial explícito para IDH/IDH1/IDH-1 → IHQ_IDH1 (línea 429-432)
- Efecto: IDH ahora aparece en campos_criticos correctamente

V3.2.0 FIX BIOMARCADORES NARRATIVOS (IHQ250188):
- Problema: Biomarcadores narrativos (GPC3, AFP) NO aparecían en campos_criticos
- Causa: Solo se agregaban biomarcadores en IHQ_ESTUDIOS_SOLICITADOS (PASO 2)
- Causa raíz: Biomarcadores detectados por extract_narrative_biomarkers NO están en estudios_solicitados
- Solución: Agregado PASO 3 que incluye TODOS los biomarcadores IHQ_* con valores válidos
- Efecto: GPC3, AFP, HEPAR ahora aparecen en campos_criticos aunque no estén solicitados formalmente
- Nota: Esto permite auditar biomarcadores incidentales detectados en descripción microscópica

Autor: Sistema EVARISIS
Versión: 3.2.0 (Biomarcadores narrativos incluidos en campos_criticos)
Fecha: 8 de enero de 2026
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
                # V3.0 OPTIMIZACIÓN: No guardar texto_original completo (redundancia 193KB → 0KB)
                # Solo conservar texto_consolidado (lo que realmente se usa)
                "texto_consolidado": None,
                "hash_original": None,  # Hash MD5 del texto original para verificación
                "estadisticas": {
                    "caracteres_totales": 0,
                    "caracteres_consolidados": 0,
                    "reduccion_porcentaje": 0
                },
                "metadata": {}
            },
            "extraccion": {
                # V2.0: Solo unified_extractor (sin redundancias de extractores individuales)
                "unified_extractor": {}
            },
            "base_datos": {
                # V3.0 OPTIMIZACIÓN: Solo campos críticos (no duplicar todo de SQLite)
                # Ahorro: ~40KB → ~5KB (87% reducción)
                "campos_criticos": {},  # Solo campos esenciales para auditoría
                "estadisticas": {
                    "total_campos_guardados": 0,
                    "campos_vacios": 0,
                    "campos_completos": 0,
                    "biomarcadores_encontrados": 0
                },
                "columnas_mapeadas": {}
            },
            "validacion": {
                # V3.0 OPTIMIZACIÓN: Contadores + top críticos en lugar de listas completas
                # Ahorro: 150 items → 5 items (97% reducción)
                "estadisticas": {
                    "total_campos_vacios": 0,
                    "total_campos_completos": 0
                },
                "top_campos_criticos_vacios": [],  # Solo top 5 campos críticos que faltan
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
        V3.0 OPTIMIZACIÓN: No guarda texto_original completo (ahorra ~95% de espacio en OCR)

        Args:
            texto_original: Texto crudo extraído del PDF (solo para calcular estadísticas)
            texto_consolidado: Texto después de limpieza y consolidación (SE GUARDA)
            metadata: Metadata adicional del proceso OCR
        """
        if not self.current_map:
            raise RuntimeError("Debe iniciar una sesión primero con iniciar_sesion()")

        # V3.0: NO guardar texto_original completo (redundancia eliminada)
        # Solo guardar texto_consolidado (lo que realmente se usa para extracción)
        self.current_map["ocr"]["texto_consolidado"] = texto_consolidado
        self.current_map["ocr"]["metadata"] = metadata or {}

        # Calcular hash del original para verificación de integridad (sin guardarlo)
        self.current_map["ocr"]["hash_original"] = hashlib.md5(
            texto_original.encode('utf-8')
        ).hexdigest()

        # V3.0: Estadísticas en lugar de texto completo
        chars_original = len(texto_original)
        chars_consolidado = len(texto_consolidado)
        reduccion = ((chars_original - chars_consolidado) / chars_original * 100) if chars_original > 0 else 0

        self.current_map["ocr"]["estadisticas"] = {
            "caracteres_totales": chars_original,
            "caracteres_consolidados": chars_consolidado,
            "reduccion_porcentaje": round(reduccion, 2)
        }

        # Métricas
        self.current_map["metricas"]["caracteres_procesados"] = chars_original

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
            # V3.1.1: Limpiar datos extraídos para evitar duplicación (especialmente biomarcadores)
            datos_limpios = {}
            campos_guardados = set()

            # PASO 1: Identificar biomarcadores con prefijo IHQ_
            biomarcadores_con_prefijo = set()
            for campo in datos_extraidos.keys():
                if campo.startswith('IHQ_'):
                    # Guardar el nombre del biomarcador sin prefijo para comparación
                    nombre_sin_prefijo = campo[4:].lower().replace('_', '-')  # IHQ_KI-67 -> ki-67
                    biomarcadores_con_prefijo.add(nombre_sin_prefijo)

            # PASO 2: Normalizar campos
            normalizaciones = {}

            for campo in datos_extraidos.keys():
                campo_lower = campo.lower()

                # V3.1.1: FILTRAR biomarcadores sin prefijo si existe versión con IHQ_
                # Ejemplo: si existe "IHQ_KI-67", descartar "ki-67"
                if not campo.startswith('IHQ_'):
                    # Verificar si este campo es un biomarcador sin prefijo
                    nombre_normalizado = campo_lower.replace('_', '-')
                    if nombre_normalizado in biomarcadores_con_prefijo:
                        # Ya existe versión con IHQ_, SALTAR este campo
                        normalizaciones[campo] = None  # Marcar para ignorar
                        continue

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

            # PASO 3: Aplicar normalizaciones y eliminar duplicados
            for campo, valor in datos_extraidos.items():
                campo_norm = normalizaciones.get(campo)

                # V3.1.1: Ignorar campos marcados como None (biomarcadores duplicados)
                if campo_norm is None:
                    continue

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
        Registra solo campos críticos de la base de datos
        V3.0 OPTIMIZACIÓN: No duplicar TODO (datos ya están en SQLite)
        Solo guarda campos esenciales para auditoría (ahorra ~87% de espacio)

        Args:
            datos_guardados: Diccionario COMPLETO con TODOS los datos guardados en BD
            columnas_mapeadas: Mapeo de campos extraídos a columnas de BD
        """
        if not self.current_map:
            raise RuntimeError("Debe iniciar una sesión primero con iniciar_sesion()")

        # V3.1: Lista de campos base críticos (SIEMPRE se guardan)
        # NO incluye identificación de paciente (N. peticion, Nombre)
        # Solo incluye campos clínicos esenciales para auditoría
        CAMPOS_BASE_CRITICOS = [
            # Campo maestro con lista de estudios solicitados
            'IHQ_ESTUDIOS_SOLICITADOS',

            # Descripciones críticas para validación semántica
            'Descripcion macroscopica',
            'Descripcion microscopica',
            'Descripcion Diagnostico',

            # Información de órgano y diagnóstico
            'IHQ_ORGANO',
            'Organo',
            'Diagnostico Coloracion',
            'Diagnostico Principal',

            # Características oncológicas
            'Malignidad',
            'Factor pronostico'
        ]

        # V3.1: Construir campos_criticos dinámicamente
        campos_criticos = {}
        biomarcadores_count = 0

        # PASO 1: Agregar campos base (SIEMPRE se incluyen)
        for campo in CAMPOS_BASE_CRITICOS:
            if campo in datos_guardados:
                campos_criticos[campo] = datos_guardados[campo]

        # PASO 2: Parsear IHQ_ESTUDIOS_SOLICITADOS y agregar solo biomarcadores solicitados
        estudios_solicitados = datos_guardados.get('IHQ_ESTUDIOS_SOLICITADOS', '')
        if estudios_solicitados and str(estudios_solicitados).strip():
            # Parsear biomarcadores del string (separados por comas)
            biomarcadores_solicitados = [
                b.strip().upper() for b in str(estudios_solicitados).split(',')
                if b.strip()
            ]

            # Agregar cada biomarcador solicitado a campos críticos
            # IMPORTANTE: Se incluyen INCLUSO si están vacíos (permite detectar campos faltantes)
            for biomarcador in biomarcadores_solicitados:
                # Buscar en datos_guardados con diferentes variaciones del nombre
                # Ejemplos: "CD34" -> "IHQ_CD34", "Ki-67" -> "IHQ_KI-67", "CKAE1AE3" -> "IHQ_CKAE1AE3"
                posibles_nombres = [
                    f'IHQ_{biomarcador}',
                    f'IHQ_{biomarcador.replace(" ", "_")}',
                    f'IHQ_{biomarcador.replace("-", "_")}',
                    f'IHQ_{biomarcador.replace(".", "_")}',
                    f'IHQ_{biomarcador.replace("/", "_")}',  # CK5/6 → IHQ_CK5_6
                    # V6.5.83: CAM5.2 → IHQ_CAM5 (IHQ_CAM52 obsoleto, eliminado)
                    f'IHQ_{biomarcador.replace(".", "").replace(" ", "")}',  # CAM5.2 → IHQ_CAM52 (histórico), CAM 5.2 → IHQ_CAM52
                    f'IHQ_{biomarcador.replace(".", "").replace(" ", "")[:-1]}',  # CAM5.2 → IHQ_CAM5 (preferido desde v6.2.3)
                    # V6.1.3: Variantes con _ESTADO para P16, P40 (IHQ251010)
                    f'IHQ_{biomarcador}_ESTADO',
                    f'IHQ_{biomarcador.replace(" ", "_")}_ESTADO',
                    f'IHQ_{biomarcador.replace("-", "_")}_ESTADO',
                    # Remover "DE" y espacios para receptores
                    f'IHQ_{biomarcador.replace(" DE ", "_").replace(" ", "_")}',  # Receptor de Estrógeno → IHQ_RECEPTOR_ESTRÓGENO
                    # Variante con plural
                    f'IHQ_{biomarcador.replace(" DE ", "_").replace(" ", "_")}S',  # IHQ_RECEPTOR_ESTROGENOS
                    # Combinación: remover DE + normalizar caracteres especiales
                    f'IHQ_{biomarcador.replace(" DE ", "_").replace(" ", "_").replace("Ó", "O").replace("É", "E")}S',
                    # V6.4.1: FIX IHQ250115 - CYCLINA -> CICLINA (subs Y por I)
                    f'IHQ_{biomarcador.replace("CYCLIN", "CICLIN").replace(" ", "_")}',
                ]

                # Casos especiales para receptores hormonales
                if 'RECEPTOR' in biomarcador and 'ESTROGEN' in biomarcador.replace('Ó', 'O').replace('É', 'E'):
                    posibles_nombres.extend(['IHQ_RECEPTOR_ESTROGENOS', 'IHQ_RECEPTORES_ESTROGENOS'])
                if 'RECEPTOR' in biomarcador and 'PROGEST' in biomarcador:
                    posibles_nombres.extend(['IHQ_RECEPTOR_PROGESTERONA', 'IHQ_RECEPTORES_PROGESTERONA'])

                # V6.5.83: CAM5.2 → IHQ_CAM5 (IHQ_CAM52 eliminado, obsoleto desde v6.2.3)
                if 'CAM5' in biomarcador or 'CAM 5' in biomarcador:
                    posibles_nombres.insert(0, 'IHQ_CAM5')  # Prioridad: IHQ_CAM5

                # V6.X.X: Caso especial TTF-1 → IHQ_TTF1 (sin guión/guión bajo)
                if 'TTF' in biomarcador:
                    posibles_nombres.insert(0, 'IHQ_TTF1')  # Prioridad: IHQ_TTF1 primero

                # V6.X.X: Caso especial NAPSINA A → IHQ_NAPSIN (sin A final)
                if 'NAPSIN' in biomarcador or 'NAPSINA' in biomarcador:
                    posibles_nombres.insert(0, 'IHQ_NAPSIN')  # Prioridad: IHQ_NAPSIN primero

                # V6.3.89 FIX IHQ250113: CD34 explícito en campos críticos (solicitado por usuario)
                if 'CD34' in biomarcador or 'CD 34' in biomarcador:
                    posibles_nombres.insert(0, 'IHQ_CD34')

                # V6.4.21 FIX IHQ250025: P 40 → IHQ_P40_ESTADO (sin espacio ni underscore)
                # Problema: "P 40" en ESTUDIOS_SOLICITADOS no mapeaba a IHQ_P40_ESTADO
                if biomarcador in ['P 40', 'P-40', 'P40']:
                    posibles_nombres.insert(0, 'IHQ_P40_ESTADO')

                # V6.4.21: P 16 → IHQ_P16_ESTADO (consistencia con P40)
                if biomarcador in ['P 16', 'P-16', 'P16']:
                    posibles_nombres.insert(0, 'IHQ_P16_ESTADO')

                # V6.4.40 FIX IHQ250175: IDH → IHQ_IDH1 (casos de glioma)
                # IDH aparece en estudios solicitados pero la columna real es IHQ_IDH1
                if biomarcador in ['IDH', 'IDH1', 'IDH-1']:
                    posibles_nombres.insert(0, 'IHQ_IDH1')

                for nombre_campo in posibles_nombres:
                    if nombre_campo in datos_guardados:
                        valor_biomarcador = datos_guardados[nombre_campo]
                        campos_criticos[nombre_campo] = valor_biomarcador

                        # Contar si tiene valor
                        if valor_biomarcador and str(valor_biomarcador).strip() and str(valor_biomarcador) not in ['N/A', 'None', '']:
                            biomarcadores_count += 1
                        break  # Ya encontramos el campo, no seguir buscando variaciones

        # PASO 3: V3.2.0 - Agregar biomarcadores narrativos detectados (aunque NO estén en estudios_solicitados)
        # Contexto: extract_narrative_biomarkers puede detectar biomarcadores incidentales en descripción microscópica
        # Ejemplo: "con positividad para Glypican-3..." → IHQ_GPC3 se extrae pero NO está en estudios_solicitados
        # Solución: Incluir TODOS los biomarcadores IHQ_* con valores válidos (no N/A, no vacío)
        for campo, valor in datos_guardados.items():
            # Filtrar: solo campos IHQ_* que NO sean ESTUDIOS_SOLICITADOS u ORGANO
            if campo.startswith('IHQ_') and campo not in ['IHQ_ESTUDIOS_SOLICITADOS', 'IHQ_ORGANO']:
                # Filtrar: solo valores válidos (no N/A, no vacío, no None)
                if valor and str(valor).strip() and str(valor) not in ['N/A', 'None', '']:
                    # Si NO está ya en campos_criticos, agregarlo
                    if campo not in campos_criticos:
                        campos_criticos[campo] = valor
                        biomarcadores_count += 1

        self.current_map["base_datos"]["campos_criticos"] = campos_criticos
        self.current_map["base_datos"]["columnas_mapeadas"] = columnas_mapeadas or {}

        # V3.0: Estadísticas en lugar de listas completas
        total_campos = len(datos_guardados)
        campos_vacios = sum(
            1 for v in datos_guardados.values()
            if not v or str(v).strip() in ['', 'N/A', 'None']
        )
        campos_completos = total_campos - campos_vacios

        # V6.4.9: FIX IHQ250108/IHQ250121 - Calcular completitud SOLO sobre campos críticos
        # NO sobre todas las 168 columnas de la BD (la mayoría son biomarcadores no aplicables)
        total_campos_criticos = len(CAMPOS_BASE_CRITICOS)
        campos_criticos_completos = sum(
            1 for campo in CAMPOS_BASE_CRITICOS
            if campo in datos_guardados
            and datos_guardados[campo]
            and str(datos_guardados[campo]).strip() not in ['', 'N/A', 'None', 'SIN DATO']
        )

        self.current_map["base_datos"]["estadisticas"] = {
            "total_campos_guardados": total_campos,
            "campos_vacios": campos_vacios,
            "campos_completos": campos_completos,
            "biomarcadores_encontrados": biomarcadores_count,
            "campos_criticos_total": total_campos_criticos,  # V6.4.9: Nuevo
            "campos_criticos_completos": campos_criticos_completos,  # V6.4.9: Nuevo
            "completitud_porcentaje": round((campos_criticos_completos / total_campos_criticos * 100) if total_campos_criticos > 0 else 0, 2)  # V6.4.9: FIX - usar campos críticos
        }

        # V3.0 OPTIMIZACIÓN: Solo guardar contadores + top campos críticos vacíos
        # NO guardar listas completas de 150+ items

        # V3.1: Detectar campos críticos vacíos usando CAMPOS_BASE_CRITICOS
        # Solo revisamos campos base, no biomarcadores específicos hardcodeados
        campos_criticos_vacios = []
        for campo in CAMPOS_BASE_CRITICOS:
            if campo in datos_guardados:
                valor = datos_guardados[campo]
                if not valor or str(valor).strip() in ['', 'N/A', 'None']:
                    campos_criticos_vacios.append(campo)

        # Guardar solo top 5 campos críticos vacíos
        self.current_map["validacion"]["top_campos_criticos_vacios"] = campos_criticos_vacios[:5]

        # Actualizar contadores
        self.current_map["validacion"]["estadisticas"]["total_campos_vacios"] = campos_vacios
        self.current_map["validacion"]["estadisticas"]["total_campos_completos"] = campos_completos

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
        V3.0: Actualizado para usar estadísticas en lugar de listas

        Returns:
            Dict con resumen ejecutivo
        """
        if not self.current_map:
            return {}

        # V3.0: Usar estadísticas de base_datos
        stats_bd = self.current_map["base_datos"]["estadisticas"]
        stats_validacion = self.current_map["validacion"]["estadisticas"]

        total_campos = stats_bd.get("total_campos_guardados", 0)
        campos_completos = stats_bd.get("campos_completos", 0)
        campos_vacios = stats_bd.get("campos_vacios", 0)
        completitud = stats_bd.get("completitud_porcentaje", 0)

        resumen = {
            "numero_peticion": self.current_map["numero_peticion"],
            "timestamp": self.current_map["timestamp"],
            "completitud_porcentaje": completitud,
            "campos_totales": total_campos,
            "campos_completos": campos_completos,
            "campos_vacios": campos_vacios,
            "biomarcadores_encontrados": stats_bd.get("biomarcadores_encontrados", 0),
            "warnings": len(self.current_map["validacion"]["warnings"]),
            "errores": len(self.current_map["validacion"]["errores"]),
            "tiempo_total_segundos": self.current_map["metricas"]["tiempo_total_segundos"],
            "caracteres_procesados": self.current_map["metricas"]["caracteres_procesados"]
        }

        return resumen

    def exportar_para_llm(self) -> Dict[str, Any]:
        """
        Exporta el mapa en un formato optimizado para envío a LLM
        V3.0: Actualizado para estructura optimizada

        Returns:
            Dict con datos formateados para LLM
        """
        if not self.current_map:
            return {}

        # V3.0: Formato condensado para LLM con campos críticos
        llm_data = {
            "numero_peticion": self.current_map["numero_peticion"],
            "texto_procesado": self.current_map["ocr"]["texto_consolidado"],
            "datos_extraidos": self.current_map["extraccion"]["unified_extractor"],
            "campos_criticos_bd": self.current_map["base_datos"]["campos_criticos"],  # V3.0: Solo críticos
            "campos_criticos_vacios": self.current_map["validacion"]["top_campos_criticos_vacios"],  # V3.0: Top 5
            "estadisticas": self.current_map["base_datos"]["estadisticas"],  # V3.0: Estadísticas
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
