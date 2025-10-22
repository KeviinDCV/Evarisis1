#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 GESTOR INTEGRAL DE IA - LM STUDIO
====================================

Herramienta consolidada para gestión completa de infraestructura IA del proyecto.
Fusiona detectar_lm_studio.py + validador_ia.py + capacidades expandidas.

CAPACIDADES:
1. Verificación y diagnóstico de LM Studio
2. Correcciones IA de casos (validación + aplicación)
3. Diagnóstico avanzado de prompts
4. Experimentación sandbox (simulaciones sin afectar BD)
5. Benchmarking de modelos
6. Análisis de comportamiento IA en producción
7. Edición inteligente de prompts y configuraciones IA
8. Generación de reportes técnicos detallados

Autor: Sistema EVARISIS
Versión: 2.0.0
Fecha: 20 de octubre de 2025
"""

import sys
import json
import argparse
import requests
import difflib
import re
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import time

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
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

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Imports del proyecto
try:
    from core.llm_client import LMStudioClient
    from core.database_manager import get_registro_by_peticion
    from core.debug_mapper import DebugMapper
except ImportError as e:
    print(f"⚠️  Advertencia: No se pudieron importar algunos módulos del core: {e}")
    print("   Algunas funcionalidades estarán limitadas.")


class GestorIALMStudio:
    """Gestor integral de infraestructura IA para EVARISIS"""

    # Endpoints por defecto para LM Studio
    DEFAULT_ENDPOINTS = [
        "http://127.0.0.1:1234",
        "http://localhost:1234",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    def __init__(self, custom_endpoint: Optional[str] = None):
        """
        Inicializar gestor IA

        Args:
            custom_endpoint: Endpoint personalizado (opcional)
        """
        self.project_root = PROJECT_ROOT
        self.endpoints = [custom_endpoint] if custom_endpoint else self.DEFAULT_ENDPOINTS
        self.active_endpoint = None
        self.model_info = None

        # Directorios clave
        self.prompts_dir = self.project_root / "core" / "prompts"
        self.resultados_dir = self.project_root / "herramientas_ia" / "resultados"
        self.backups_dir = self.project_root / "backups"
        self.debug_maps_dir = self.project_root / "data" / "debug_maps"

        # Crear directorios si no existen
        self.resultados_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # Cliente LLM (se inicializa cuando se necesita)
        self.llm_client = None

    # =========================================================================
    # SECCIÓN 1: VERIFICACIÓN Y DIAGNÓSTICO DE LM STUDIO
    # =========================================================================

    def verificar_servidor(self, verbose: bool = True) -> Dict[str, Any]:
        """
        Verifica si LM Studio está corriendo y en qué puerto

        Args:
            verbose: Si True, muestra mensajes detallados

        Returns:
            Dict con información de detección
        """
        resultado = {
            "detectado": False,
            "endpoint": None,
            "modelo": None,
            "capacidades": [],
            "error": None
        }

        if verbose:
            print("🔍 VERIFICANDO LM STUDIO LOCAL...")
            print("=" * 80)

        for endpoint in self.endpoints:
            if verbose:
                print(f"\n📡 Probando endpoint: {endpoint}")

            try:
                # Probar endpoint /v1/models (OpenAI compatible)
                response = requests.get(
                    f"{endpoint}/v1/models",
                    timeout=3
                )

                if response.status_code == 200:
                    data = response.json()
                    self.active_endpoint = endpoint

                    resultado["detectado"] = True
                    resultado["endpoint"] = endpoint

                    # Extraer información de modelos
                    if "data" in data and len(data["data"]) > 0:
                        modelo = data["data"][0]
                        resultado["modelo"] = {
                            "id": modelo.get("id", "desconocido"),
                            "object": modelo.get("object", "model"),
                            "owned_by": modelo.get("owned_by", "local")
                        }

                        if verbose:
                            print(f"✅ LM Studio DETECTADO en {endpoint}")
                            print(f"📦 Modelo cargado: {modelo.get('id', 'desconocido')}")
                    else:
                        if verbose:
                            print(f"⚠️  Servidor activo pero sin modelos cargados")
                        resultado["error"] = "Sin modelos cargados"

                    # Probar capacidades
                    resultado["capacidades"] = self._probar_capacidades(endpoint, verbose=verbose)

                    break

            except requests.exceptions.ConnectionError:
                if verbose:
                    print(f"❌ No hay conexión en {endpoint}")
            except requests.exceptions.Timeout:
                if verbose:
                    print(f"⏱️  Timeout en {endpoint}")
            except Exception as e:
                if verbose:
                    print(f"⚠️  Error en {endpoint}: {e}")

        if not resultado["detectado"]:
            resultado["error"] = "No se encontró LM Studio activo en los puertos predeterminados"
            if verbose:
                print("\n❌ LM STUDIO NO DETECTADO")
                print("💡 Asegúrate de que LM Studio esté corriendo y tenga un modelo cargado")

        return resultado

    def _probar_capacidades(self, endpoint: str, verbose: bool = True) -> List[str]:
        """
        Prueba las capacidades del servidor LM Studio

        Args:
            endpoint: URL del servidor
            verbose: Si True, muestra mensajes

        Returns:
            Lista de capacidades disponibles
        """
        capacidades = []

        if verbose:
            print("\n🧪 Probando capacidades del servidor...")

        # Probar endpoint /v1/chat/completions
        try:
            response = requests.post(
                f"{endpoint}/v1/chat/completions",
                json={
                    "messages": [{"role": "user", "content": "test"}],
                    "max_tokens": 1,
                    "temperature": 0
                },
                timeout=5
            )

            if response.status_code in [200, 400]:  # 400 también indica que el endpoint existe
                capacidades.append("chat_completions")
                if verbose:
                    print("  ✅ Chat Completions (v1/chat/completions)")
        except:
            pass

        # Probar endpoint /v1/completions
        try:
            response = requests.post(
                f"{endpoint}/v1/completions",
                json={
                    "prompt": "test",
                    "max_tokens": 1
                },
                timeout=5
            )

            if response.status_code in [200, 400]:
                capacidades.append("completions")
                if verbose:
                    print("  ✅ Completions (v1/completions)")
        except:
            pass

        # Probar endpoint /v1/embeddings
        try:
            response = requests.post(
                f"{endpoint}/v1/embeddings",
                json={
                    "input": "test"
                },
                timeout=5
            )

            if response.status_code in [200, 400]:
                capacidades.append("embeddings")
                if verbose:
                    print("  ✅ Embeddings (v1/embeddings)")
        except:
            pass

        return capacidades

    def probar_inferencia(self, prompt: str = "Di 'OK' si estás funcionando correctamente.") -> Dict[str, Any]:
        """
        Prueba la inferencia del modelo con un prompt simple

        Args:
            prompt: Prompt de prueba

        Returns:
            Dict con resultado de la inferencia
        """
        if not self.active_endpoint:
            deteccion = self.verificar_servidor(verbose=False)
            if not deteccion["detectado"]:
                return {
                    "exito": False,
                    "error": "No hay servidor LM Studio activo"
                }

        print("\n🧠 PROBANDO INFERENCIA DEL MODELO...")
        print("=" * 80)
        print(f"📝 Prompt: {prompt}")

        try:
            response = requests.post(
                f"{self.active_endpoint}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": "Eres un asistente útil."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 100,
                    "temperature": 0.1,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                respuesta = data["choices"][0]["message"]["content"]
                tokens_usados = data.get("usage", {})

                print(f"\n✅ RESPUESTA DEL MODELO:")
                print(f"💬 {respuesta}")
                print(f"\n📊 Tokens usados:")
                print(f"  - Prompt: {tokens_usados.get('prompt_tokens', 'N/A')}")
                print(f"  - Completion: {tokens_usados.get('completion_tokens', 'N/A')}")
                print(f"  - Total: {tokens_usados.get('total_tokens', 'N/A')}")

                return {
                    "exito": True,
                    "respuesta": respuesta,
                    "tokens": tokens_usados,
                    "modelo": data.get("model", "desconocido")
                }
            else:
                error_msg = f"Error HTTP {response.status_code}: {response.text}"
                print(f"\n❌ ERROR: {error_msg}")
                return {
                    "exito": False,
                    "error": error_msg
                }

        except Exception as e:
            error_msg = f"Error de conexión: {str(e)}"
            print(f"\n❌ ERROR: {error_msg}")
            return {
                "exito": False,
                "error": error_msg
            }

    def listar_modelos_disponibles(self) -> Dict[str, Any]:
        """
        Lista todos los modelos disponibles en LM Studio

        Returns:
            Dict con lista de modelos
        """
        if not self.active_endpoint:
            deteccion = self.verificar_servidor(verbose=False)
            if not deteccion["detectado"]:
                return {
                    "exito": False,
                    "error": "No hay servidor LM Studio activo"
                }

        try:
            response = requests.get(
                f"{self.active_endpoint}/v1/models",
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                modelos = data.get("data", [])

                print("\n📦 MODELOS DISPONIBLES EN LM STUDIO:")
                print("=" * 80)

                if modelos:
                    for i, modelo in enumerate(modelos, 1):
                        print(f"\n{i}. {modelo.get('id', 'desconocido')}")
                        print(f"   Tipo: {modelo.get('object', 'N/A')}")
                        print(f"   Propietario: {modelo.get('owned_by', 'N/A')}")
                else:
                    print("⚠️  No hay modelos cargados")

                return {
                    "exito": True,
                    "modelos": [m.get("id") for m in modelos],
                    "total": len(modelos)
                }
            else:
                return {
                    "exito": False,
                    "error": f"Error HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "exito": False,
                "error": str(e)
            }

    # =========================================================================
    # SECCIÓN 2: CORRECCIONES IA (migrado de validador_ia.py)
    # =========================================================================

    def _inicializar_llm_client(self):
        """Inicializa el cliente LLM si no existe"""
        if self.llm_client is None:
            if not self.active_endpoint:
                self.verificar_servidor(verbose=False)

            self.llm_client = LMStudioClient(endpoint=self.active_endpoint or "http://127.0.0.1:1234")

    def validar_caso(
        self,
        numero_peticion: str,
        debug_map_path: Optional[Path] = None,
        validar_solo_criticos: bool = False,
        campo_especifico: Optional[str] = None,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Valida un caso IHQ completo o un campo específico comparando debug map vs BD

        Args:
            numero_peticion: Número de petición IHQ
            debug_map_path: Ruta al archivo debug_map (opcional, se busca automáticamente)
            validar_solo_criticos: Si True, solo valida campos críticos
            campo_especifico: Si se especifica, solo valida ese campo (ej: "IHQ_Ki67")
            dry_run: Si True, solo simula (NO aplica correcciones)

        Returns:
            Dict con resultados de validación
        """
        print(f"\n🔍 VALIDANDO CASO: {numero_peticion}")
        print("=" * 80)

        # Inicializar cliente LLM
        self._inicializar_llm_client()

        # 1. Cargar debug map
        if not debug_map_path:
            debug_map_path = self._buscar_debug_map(numero_peticion)

        if not debug_map_path or not debug_map_path.exists():
            return {
                "exito": False,
                "error": f"No se encontró debug map para {numero_peticion}"
            }

        print(f"📂 Cargando debug map: {debug_map_path.name}")
        debug_map = DebugMapper.cargar_mapa(debug_map_path)

        # 2. Cargar datos de BD
        print(f"🗄️  Consultando base de datos...")
        bd_data = get_registro_by_peticion(numero_peticion)

        if not bd_data:
            return {
                "exito": False,
                "error": f"No se encontró {numero_peticion} en la base de datos"
            }

        # 3. Extraer datos relevantes
        texto_original = debug_map["ocr"]["texto_consolidado"]
        datos_extraidos = debug_map["extraccion"]["unified_extractor"]
        datos_bd_dict = dict(bd_data) if bd_data else {}

        # 4. Campos a validar
        if campo_especifico:
            # Validar solo el campo específico
            campos_a_validar = [campo_especifico]
            print(f"\n🎯 MODO: Validación de campo específico")
            print(f"📌 Campo seleccionado: {campo_especifico}")
        elif validar_solo_criticos:
            # Validar solo campos críticos
            campos_criticos = [
                "numero_peticion", "identificacion", "nombre_completo",
                "edad", "genero", "diagnostico", "organo"
            ]
            campos_a_validar = campos_criticos
            print(f"\n⚠️  MODO: Validación de campos críticos solamente")
        else:
            # Validar TODOS los campos
            campos_a_validar = None
            print(f"\n📋 MODO: Validación COMPLETA de todos los campos")

        # 5. Validar con IA
        print(f"\n🤖 Validando con IA (LM Studio)...")
        if campos_a_validar:
            print(f"📋 Campos a validar: {len(campos_a_validar)} campo(s)")
            for campo in campos_a_validar:
                print(f"   • {campo}")
        else:
            print(f"📋 Validando TODOS los campos del caso")

        validacion_resultado = self.llm_client.validar_multiple_campos(
            datos_extraidos=datos_extraidos,
            texto_original=texto_original,
            campos_a_validar=campos_a_validar
        )

        # 6. Comparar con BD y generar informe
        print(f"\n📊 Generando informe de validación...")
        informe = self._generar_informe_validacion(
            numero_peticion=numero_peticion,
            debug_map=debug_map,
            datos_bd=datos_bd_dict,
            validacion_ia=validacion_resultado
        )

        # 7. Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.resultados_dir / f"validacion_ia_{numero_peticion}_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(informe, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados guardados en: {output_file}")

        return informe

    def _buscar_debug_map(self, numero_peticion: str) -> Optional[Path]:
        """
        Busca el debug map más reciente para un número de petición

        Args:
            numero_peticion: Número de petición IHQ

        Returns:
            Path al debug map o None si no se encuentra
        """
        if not self.debug_maps_dir.exists():
            return None

        # Buscar archivos que contengan el número de petición
        mapas = list(self.debug_maps_dir.glob(f"debug_map_{numero_peticion}_*.json"))

        if not mapas:
            return None

        # Retornar el más reciente
        return max(mapas, key=lambda p: p.stat().st_mtime)

    def _generar_informe_validacion(
        self,
        numero_peticion: str,
        debug_map: Dict[str, Any],
        datos_bd: Dict[str, Any],
        validacion_ia: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera informe completo de validación

        Args:
            numero_peticion: Número de petición
            debug_map: Mapa de debug completo
            datos_bd: Datos de la base de datos
            validacion_ia: Resultados de validación con IA

        Returns:
            Dict con informe completo
        """
        discrepancias = []
        correcciones_sugeridas = []
        campos_correctos = []

        validaciones = validacion_ia.get("validaciones", {})

        for campo, validacion in validaciones.items():
            if not validacion.get("exito"):
                continue

            val_data = validacion.get("validacion", {})

            campo_correcto = val_data.get("campo_correcto", True)
            confianza = val_data.get("confianza", 0.0)
            valor_sugerido = val_data.get("valor_sugerido")

            # Comparar con BD
            valor_extraido = debug_map["extraccion"]["unified_extractor"].get(campo)
            valor_bd = datos_bd.get(campo)

            if not campo_correcto or valor_sugerido:
                # Hay una discrepancia o sugerencia de corrección
                discrepancia = {
                    "campo": campo,
                    "valor_extraido": str(valor_extraido),
                    "valor_bd": str(valor_bd),
                    "valor_sugerido_ia": valor_sugerido,
                    "confianza_ia": confianza,
                    "razonamiento": val_data.get("razonamiento", ""),
                    "ubicacion_texto": val_data.get("ubicacion_en_texto", ""),
                    "similitud_extraido_bd": self._calcular_similitud(
                        str(valor_extraido), str(valor_bd)
                    )
                }

                discrepancias.append(discrepancia)

                # Si la IA sugiere un valor diferente al de BD, es una corrección
                if valor_sugerido and str(valor_sugerido) != str(valor_bd):
                    correcciones_sugeridas.append({
                        "campo": campo,
                        "valor_actual_bd": str(valor_bd),
                        "valor_nuevo_sugerido": valor_sugerido,
                        "confianza": confianza,
                        "razon": val_data.get("razonamiento", ""),
                        "criticidad": self._evaluar_criticidad(campo)
                    })
            else:
                campos_correctos.append(campo)

        # Resumen ejecutivo
        total_validados = len(validaciones)
        total_discrepancias = len(discrepancias)
        total_correcciones = len(correcciones_sugeridas)

        # Clasificar correcciones por criticidad
        correcciones_criticas = [c for c in correcciones_sugeridas if c["criticidad"] == "CRITICA"]
        correcciones_importantes = [c for c in correcciones_sugeridas if c["criticidad"] == "IMPORTANTE"]
        correcciones_opcionales = [c for c in correcciones_sugeridas if c["criticidad"] == "OPCIONAL"]

        informe = {
            "numero_peticion": numero_peticion,
            "timestamp": datetime.now().isoformat(),
            "resumen": {
                "total_campos_validados": total_validados,
                "campos_correctos": len(campos_correctos),
                "total_discrepancias": total_discrepancias,
                "total_correcciones_sugeridas": total_correcciones,
                "correcciones_criticas": len(correcciones_criticas),
                "correcciones_importantes": len(correcciones_importantes),
                "correcciones_opcionales": len(correcciones_opcionales),
                "tokens_usados": validacion_ia.get("tokens_totales", 0)
            },
            "discrepancias": discrepancias,
            "correcciones_sugeridas": {
                "criticas": correcciones_criticas,
                "importantes": correcciones_importantes,
                "opcionales": correcciones_opcionales
            },
            "campos_correctos": campos_correctos,
            "debug_map_usado": debug_map.get("session_id", ""),
            "metadata": {
                "caracteres_procesados": debug_map["metricas"]["caracteres_procesados"],
                "tiempo_total_extraccion": debug_map["metricas"]["tiempo_total_segundos"]
            }
        }

        return informe

    def _calcular_similitud(self, texto1: str, texto2: str) -> float:
        """
        Calcula similitud entre dos textos

        Args:
            texto1: Primer texto
            texto2: Segundo texto

        Returns:
            Similitud de 0.0 a 1.0
        """
        if not texto1 or not texto2:
            return 0.0

        return difflib.SequenceMatcher(None, texto1, texto2).ratio()

    def _evaluar_criticidad(self, campo: str) -> str:
        """
        Evalúa la criticidad de un campo

        Args:
            campo: Nombre del campo

        Returns:
            "CRITICA", "IMPORTANTE" o "OPCIONAL"
        """
        campos_criticos = [
            "numero_peticion", "identificacion", "nombre_completo", "edad", "genero"
        ]

        campos_importantes = [
            "diagnostico", "organo", "fecha_informe", "eps", "medico_tratante",
            "IHQ_Ki_67", "IHQ_HER2", "IHQ_ER", "IHQ_PR", "Factor_Pronostico"
        ]

        if campo in campos_criticos:
            return "CRITICA"
        elif campo in campos_importantes:
            return "IMPORTANTE"
        else:
            return "OPCIONAL"

    def validar_lote(
        self,
        ultimos_n: int = 10,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Valida un lote de casos (los últimos N procesados)

        Args:
            ultimos_n: Número de casos a validar
            dry_run: Si True, solo simula

        Returns:
            Dict con resultados del lote
        """
        print(f"\n📦 VALIDANDO LOTE: Últimos {ultimos_n} casos")
        print("=" * 80)

        # Buscar últimos N debug maps
        if not self.debug_maps_dir.exists():
            return {
                "exito": False,
                "error": "No se encontró directorio de debug maps"
            }

        debug_maps = sorted(
            self.debug_maps_dir.glob("debug_map_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:ultimos_n]

        if not debug_maps:
            return {
                "exito": False,
                "error": "No se encontraron debug maps"
            }

        resultados = []

        for i, debug_map_path in enumerate(debug_maps, 1):
            # Extraer número de petición del nombre del archivo
            match = re.search(r'debug_map_(IHQ\d+)_', debug_map_path.name)
            if not match:
                continue

            numero_peticion = match.group(1)

            print(f"\n[{i}/{len(debug_maps)}] Validando {numero_peticion}...")

            informe = self.validar_caso(
                numero_peticion=numero_peticion,
                debug_map_path=debug_map_path,
                dry_run=dry_run
            )

            resultados.append({
                "numero_peticion": numero_peticion,
                "informe": informe
            })

        # Generar resumen del lote
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        resumen_file = self.resultados_dir / f"validacion_lote_{ultimos_n}casos_{timestamp}.json"

        resumen = {
            "timestamp": datetime.now().isoformat(),
            "total_casos": len(resultados),
            "resultados": resultados
        }

        with open(resumen_file, 'w', encoding='utf-8') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resumen del lote guardado en: {resumen_file}")

        return resumen

    def analizar_completitud(self, numero_peticion: str) -> Dict[str, Any]:
        """
        Analiza por qué un caso está marcado como incompleto

        Entiende la lógica del módulo de completitud:
        - Verifica IHQ_Estudios_Solicitados
        - Detecta biomarcadores vacíos vs diagnóstico completo
        - Explica las reglas de completitud

        Args:
            numero_peticion: Número de petición IHQ

        Returns:
            Dict con análisis detallado de completitud
        """
        print(f"\n🔬 ANALIZANDO COMPLETITUD: {numero_peticion}")
        print("=" * 80)

        # Importar módulo de validación
        try:
            from core.validation_checker import verificar_completitud_registro
        except ImportError:
            return {
                "exito": False,
                "error": "No se pudo importar validation_checker"
            }

        # 1. Obtener análisis de completitud actual
        print(f"📊 Calculando completitud según reglas del sistema...")
        resultado_completitud = verificar_completitud_registro(numero_peticion)

        if 'error' in resultado_completitud:
            return {
                "exito": False,
                "error": resultado_completitud['error']
            }

        # 2. Obtener datos de BD
        print(f"🗄️  Consultando base de datos...")
        bd_data = get_registro_by_peticion(numero_peticion)

        if not bd_data:
            return {
                "exito": False,
                "error": f"No se encontró {numero_peticion} en la base de datos"
            }

        bd_dict = dict(bd_data)

        # 3. Analizar IHQ_Estudios_Solicitados
        estudios_solicitados = bd_dict.get('IHQ_ESTUDIOS_SOLICITADOS', '')
        tiene_estudios = bool(estudios_solicitados and estudios_solicitados.strip() and estudios_solicitados != 'N/A')

        # 4. Analizar campos críticos
        diagnostico_principal = bd_dict.get('DIAGNOSTICO', '')
        factor_pronostico = bd_dict.get('FACTOR_PRONOSTICO', '')

        # 5. Contar biomarcadores vacíos
        biomarcadores_ihq = [
            'IHQ_HER2', 'IHQ_Ki67', 'IHQ_RE', 'IHQ_RP',
            'IHQ_P53', 'IHQ_PDL1', 'IHQ_P16_ESTADO', 'IHQ_P16_PORCENTAJE',
            'IHQ_CKAE1_AE3', 'IHQ_CK5_6', 'IHQ_CK7', 'IHQ_CK20',
            'IHQ_CD10', 'IHQ_CD20', 'IHQ_CD3', 'IHQ_CD34',
            'IHQ_CD45', 'IHQ_CD68', 'IHQ_S100', 'IHQ_VIMENTINA',
            'IHQ_EMA', 'IHQ_CROMOGRANINA', 'IHQ_SINAPTOFISINA',
            'IHQ_TTF1', 'IHQ_NAPSIN_A', 'IHQ_PAX8', 'IHQ_GATA3',
            'IHQ_SOX10', 'IHQ_MELAN_A', 'IHQ_HMB45', 'IHQ_BCL2'
        ]

        biomarcadores_vacios = []
        biomarcadores_completos = []

        for bio in biomarcadores_ihq:
            valor = bd_dict.get(bio, '')
            if not valor or valor == 'N/A':
                biomarcadores_vacios.append(bio)
            else:
                biomarcadores_completos.append(bio)

        # 6. Análisis de situación
        print(f"\n📋 ANÁLISIS DE COMPLETITUD:")
        print(f"   Estado: {'✅ COMPLETO' if resultado_completitud['completo'] else '⚠️  INCOMPLETO'}")
        print(f"   Porcentaje: {resultado_completitud['porcentaje_completitud']}%")
        print(f"   Campos completos: {resultado_completitud['campos_completos']}/{resultado_completitud['campos_totales']}")
        print(f"   Biomarcadores detectados: {resultado_completitud['biomarcadores_detectados']}")

        print(f"\n🔍 DETALLES:")
        print(f"   IHQ_Estudios_Solicitados: {'✅ SÍ tiene datos' if tiene_estudios else '❌ Vacío o N/A'}")
        if tiene_estudios:
            print(f"      Contenido: {estudios_solicitados[:100]}...")

        print(f"   Diagnóstico principal: {'✅ Completo' if diagnostico_principal and diagnostico_principal != 'N/A' else '❌ Vacío'}")
        print(f"   Factor pronóstico: {'✅ Completo' if factor_pronostico and factor_pronostico != 'N/A' else '❌ Vacío'}")

        print(f"\n💊 BIOMARCADORES:")
        print(f"   Completos: {len(biomarcadores_completos)}")
        if biomarcadores_completos:
            print(f"      {', '.join(biomarcadores_completos[:5])}{'...' if len(biomarcadores_completos) > 5 else ''}")
        print(f"   Vacíos: {len(biomarcadores_vacios)}")
        if biomarcadores_vacios:
            print(f"      {', '.join(biomarcadores_vacios[:5])}{'...' if len(biomarcadores_vacios) > 5 else ''}")

        # 7. Explicar la lógica de completitud
        print(f"\n💡 EXPLICACIÓN DE COMPLETITUD:")

        if tiene_estudios:
            print(f"   ℹ️  Caso CON estudios solicitados → REGLA ESTRICTA")
            print(f"      • TODOS los biomarcadores solicitados deben estar completos")
            print(f"      • Si hay biomarcadores faltantes → se marca INCOMPLETO")
            if resultado_completitud['biomarcadores_faltantes']:
                print(f"      • Biomarcadores faltantes: {', '.join(resultado_completitud['biomarcadores_faltantes'])}")
        else:
            print(f"   ℹ️  Caso SIN estudios solicitados → REGLA GENÉRICA")
            print(f"      • Al menos 1 biomarcador debe estar completo")
            print(f"      • Porcentaje general ≥ 100%")

        if not resultado_completitud['completo']:
            print(f"\n⚠️  RAZÓN DE INCOMPLETITUD:")
            if resultado_completitud['campos_faltantes']:
                print(f"   • Campos faltantes: {', '.join(resultado_completitud['campos_faltantes'])}")
            if resultado_completitud['biomarcadores_faltantes']:
                print(f"   • Biomarcadores faltantes: {', '.join(resultado_completitud['biomarcadores_faltantes'])}")

        # 8. Generar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_file = self.resultados_dir / f"analisis_completitud_{numero_peticion}_{timestamp}.json"

        analisis = {
            "timestamp": datetime.now().isoformat(),
            "numero_peticion": numero_peticion,
            "completitud_actual": resultado_completitud,
            "ihq_estudios_solicitados": {
                "tiene_datos": tiene_estudios,
                "contenido": estudios_solicitados if tiene_estudios else None
            },
            "diagnostico_principal": {
                "completo": bool(diagnostico_principal and diagnostico_principal != 'N/A'),
                "valor": diagnostico_principal
            },
            "factor_pronostico": {
                "completo": bool(factor_pronostico and factor_pronostico != 'N/A'),
                "valor": factor_pronostico
            },
            "biomarcadores": {
                "total": len(biomarcadores_ihq),
                "completos": len(biomarcadores_completos),
                "vacios": len(biomarcadores_vacios),
                "lista_completos": biomarcadores_completos,
                "lista_vacios": biomarcadores_vacios
            },
            "explicacion_regla": "ESTRICTA (con estudios solicitados)" if tiene_estudios else "GENÉRICA (sin estudios solicitados)"
        }

        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(analisis, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Análisis guardado en: {reporte_file}")

        return analisis

    def diagnosticar_fallo(
        self,
        numero_peticion: str,
        campo: str,
        valor_esperado: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Diagnostica por qué la IA no corrigió bien un campo

        Analiza múltiples factores:
        - Estado del prompt (tiene ejemplos del biomarcador?)
        - Datos en BD (IHQ_Estudios_Solicitados completo?)
        - Modelo actual (es adecuado para esta tarea?)
        - OCR del PDF (texto fuente tiene el dato?)

        Args:
            numero_peticion: Número de petición IHQ
            campo: Campo que falló (ej: "IHQ_Ki67")
            valor_esperado: Valor que debería tener (opcional)

        Returns:
            Dict con diagnóstico completo del fallo
        """
        print(f"\n🔬 DIAGNOSTICANDO FALLO EN CORRECCIÓN IA")
        print("=" * 80)
        print(f"   Caso: {numero_peticion}")
        print(f"   Campo problemático: {campo}")
        if valor_esperado:
            print(f"   Valor esperado: {valor_esperado}")

        diagnostico = {
            "timestamp": datetime.now().isoformat(),
            "numero_peticion": numero_peticion,
            "campo": campo,
            "valor_esperado": valor_esperado,
            "problemas_detectados": [],
            "hipotesis": [],
            "soluciones_sugeridas": []
        }

        # 1. Verificar datos en BD
        print(f"\n📊 1. VERIFICANDO DATOS EN BASE DE DATOS...")
        bd_data = get_registro_by_peticion(numero_peticion)

        if not bd_data:
            diagnostico["problemas_detectados"].append("Caso no encontrado en BD")
            return diagnostico

        bd_dict = dict(bd_data)
        valor_actual = bd_dict.get(campo, '')

        print(f"   Valor actual en BD: {valor_actual if valor_actual else '(vacío)'}")

        # 2. Verificar IHQ_Estudios_Solicitados
        print(f"\n📋 2. VERIFICANDO IHQ_ESTUDIOS_SOLICITADOS...")
        estudios = bd_dict.get('IHQ_ESTUDIOS_SOLICITADOS', '')
        tiene_estudios = bool(estudios and estudios.strip() and estudios != 'N/A')

        print(f"   Estado: {'✅ Tiene datos' if tiene_estudios else '❌ Vacío o N/A'}")

        if not tiene_estudios:
            diagnostico["problemas_detectados"].append("IHQ_Estudios_Solicitados vacío")
            diagnostico["hipotesis"].append("IA no tiene contexto de qué biomarcadores buscar")
            diagnostico["soluciones_sugeridas"].append("Verificar OCR de 'Estudios Solicitados' en PDF")

        # 3. Buscar debug map para ver OCR original
        print(f"\n📄 3. VERIFICANDO OCR DEL PDF...")
        debug_map_path = self._buscar_debug_map(numero_peticion)

        if debug_map_path and debug_map_path.exists():
            from core.debug_mapper import DebugMapper
            debug_map = DebugMapper.cargar_mapa(debug_map_path)
            texto_original = debug_map["ocr"]["texto_consolidado"]

            # Buscar el campo en el texto
            campo_limpio = campo.replace('IHQ_', '').replace('_', '-')
            patron_busqueda = f"{campo_limpio}.*?(\\d+\\.?\\d*)%?"

            import re
            match = re.search(patron_busqueda, texto_original, re.IGNORECASE)

            if match:
                print(f"   ✅ Campo '{campo_limpio}' ENCONTRADO en PDF")
                print(f"      Fragmento: {match.group(0)}")
                diagnostico["ocr_tiene_dato"] = True
                diagnostico["fragmento_ocr"] = match.group(0)
            else:
                print(f"   ❌ Campo '{campo_limpio}' NO encontrado en OCR")
                diagnostico["ocr_tiene_dato"] = False
                diagnostico["problemas_detectados"].append(f"OCR no capturó {campo_limpio}")
                diagnostico["hipotesis"].append("Problema de calidad OCR o campo no presente en PDF")
                diagnostico["soluciones_sugeridas"].append("Revisar PDF original manualmente")
        else:
            print(f"   ⚠️  Debug map no disponible")

        # 4. Verificar prompt actual
        print(f"\n📝 4. ANALIZANDO PROMPTS...")
        prompt_comun = self.prompts_dir / "system_prompt_comun.txt"

        if prompt_comun.exists():
            with open(prompt_comun, 'r', encoding='utf-8') as f:
                contenido_prompt = f.read()

            # Buscar ejemplos del biomarcador
            tiene_ejemplos = campo_limpio.lower() in contenido_prompt.lower()

            print(f"   Ejemplos de '{campo_limpio}' en prompt: {'✅ SÍ' if tiene_ejemplos else '❌ NO'}")

            if not tiene_ejemplos:
                diagnostico["problemas_detectados"].append(f"Prompt no tiene ejemplos de {campo_limpio}")
                diagnostico["hipotesis"].append("IA no está entrenada específicamente para este biomarcador")
                diagnostico["soluciones_sugeridas"].append(f"Agregar ejemplos de extracción de {campo_limpio} al prompt")

        # 5. Verificar modelo actual
        print(f"\n🤖 5. VERIFICANDO MODELO IA...")
        servidor_info = self.verificar_servidor(verbose=False)

        if servidor_info["detectado"]:
            modelo_actual = servidor_info.get("modelo", {}).get("id")
            print(f"   Modelo actual: {modelo_actual}")

            # Evaluar si el modelo es adecuado
            if "20b" in str(modelo_actual).lower() or "gpt-oss" in str(modelo_actual).lower():
                print(f"   ✅ Modelo pesado (bueno para correcciones complejas)")
                diagnostico["modelo_adecuado"] = True
            elif "3b" in str(modelo_actual).lower() or "7b" in str(modelo_actual).lower():
                print(f"   ⚠️  Modelo ligero (puede fallar en extracciones complejas)")
                diagnostico["modelo_adecuado"] = False
                diagnostico["problemas_detectados"].append("Modelo ligero para tarea compleja")
                diagnostico["soluciones_sugeridas"].append("Usar modelo más grande (qwen2.5-14b o gpt-oss-20b)")

        # 6. Generar diagnóstico final
        print(f"\n🎯 DIAGNÓSTICO FINAL:")

        if not diagnostico["problemas_detectados"]:
            print(f"   ✅ No se detectaron problemas obvios")
            diagnostico["hipotesis"].append("Posible problema de configuración sutil")
            diagnostico["soluciones_sugeridas"].append("Revisar logs de IA para más detalles")
        else:
            print(f"   ⚠️  Problemas detectados:")
            for problema in diagnostico["problemas_detectados"]:
                print(f"      • {problema}")

        print(f"\n💡 HIPÓTESIS:")
        for hipotesis in diagnostico["hipotesis"]:
            print(f"   • {hipotesis}")

        print(f"\n🔧 SOLUCIONES SUGERIDAS:")
        for solucion in diagnostico["soluciones_sugeridas"]:
            print(f"   • {solucion}")

        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_file = self.resultados_dir / f"diagnostico_fallo_{numero_peticion}_{campo}_{timestamp}.json"

        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(diagnostico, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Diagnóstico guardado en: {reporte_file}")

        return diagnostico

    def experimentar_modelos(
        self,
        numero_peticion: str,
        campo: str
    ) -> Dict[str, Any]:
        """
        Experimenta con TODOS los modelos disponibles en LM Studio
        para validar un mismo campo y comparar resultados

        Args:
            numero_peticion: Número de petición IHQ
            campo: Campo a validar (ej: "IHQ_Ki67")

        Returns:
            Dict con comparación de resultados por modelo
        """
        print(f"\n🧪 EXPERIMENTANDO CON MÚLTIPLES MODELOS")
        print("=" * 80)
        print(f"   Caso: {numero_peticion}")
        print(f"   Campo: {campo}")

        # 1. Listar modelos disponibles
        print("\n📦 1. LISTANDO MODELOS DISPONIBLES...")
        modelos_info = self.listar_modelos_disponibles()

        if not modelos_info.get("exito"):
            print(f"❌ Error: {modelos_info.get('error')}")
            return modelos_info

        modelos = modelos_info.get("modelos", [])

        if not modelos:
            print("⚠️  No hay modelos disponibles en LM Studio")
            return {
                "exito": False,
                "error": "No hay modelos cargados en LM Studio"
            }

        print(f"   ✅ Encontrados {len(modelos)} modelo(s)")

        # 2. Obtener datos del caso
        print(f"\n📋 2. OBTENIENDO DATOS DEL CASO {numero_peticion}...")
        bd_data = get_registro_by_peticion(numero_peticion)

        if not bd_data:
            print(f"❌ No se encontró el caso {numero_peticion} en BD")
            return {
                "exito": False,
                "error": f"Caso {numero_peticion} no encontrado en BD"
            }

        bd_dict = dict(bd_data)
        valor_actual_bd = bd_dict.get(campo, '')
        print(f"   Valor actual en BD: '{valor_actual_bd}'")

        # 3. Buscar debug_map
        debug_map_path = self._buscar_debug_map(numero_peticion)
        if not debug_map_path:
            print(f"❌ No se encontró debug_map para {numero_peticion}")
            return {
                "exito": False,
                "error": f"Debug map no encontrado para {numero_peticion}"
            }

        debug_map = DebugMapper.cargar_mapa(debug_map_path)
        texto_original = debug_map["ocr"]["texto_consolidado"]

        # 4. Experimentar con cada modelo
        print(f"\n🔬 3. EXPERIMENTANDO CON {len(modelos)} MODELO(S)...")
        print("   NOTA: Esto puede tardar varios minutos...")

        resultados_por_modelo = []

        for i, modelo_id in enumerate(modelos, 1):
            print(f"\n{'=' * 80}")
            print(f"🤖 MODELO {i}/{len(modelos)}: {modelo_id}")
            print(f"{'=' * 80}")

            # Crear cliente temporal con este modelo
            # NOTA: LM Studio solo permite 1 modelo cargado a la vez
            # Por ahora, solo documentamos que el usuario debe cambiar el modelo manualmente
            print(f"\n⚠️  IMPORTANTE: Asegúrate de tener cargado el modelo '{modelo_id}' en LM Studio")
            print("   Presiona ENTER cuando el modelo esté cargado (o Ctrl+C para saltar)...")

            try:
                input()
            except KeyboardInterrupt:
                print("\n⏭️  Saltando este modelo...")
                resultados_por_modelo.append({
                    "modelo": modelo_id,
                    "estado": "saltado",
                    "razon": "Usuario saltó este modelo"
                })
                continue

            # Validar campo con este modelo
            inicio = time.time()

            try:
                # Inicializar cliente LLM
                self._inicializar_llm_client()

                # Intentar corrección del campo
                print(f"   🔍 Solicitando corrección a la IA...")
                correccion = self.llm_client.corregir_campo_individual(
                    campo_nombre=campo,
                    valor_actual=valor_actual_bd,
                    texto_original=texto_original,
                    numero_peticion=numero_peticion
                )

                tiempo_respuesta = time.time() - inicio

                # Analizar resultado
                valor_sugerido = correccion.get("valor_corregido", "")
                confianza = correccion.get("confianza", 0.0)
                explicacion = correccion.get("explicacion", "")

                print(f"   ✅ Respuesta recibida en {tiempo_respuesta:.2f}s")
                print(f"   💬 Valor sugerido: '{valor_sugerido}'")
                print(f"   📊 Confianza: {confianza:.2%}")

                resultados_por_modelo.append({
                    "modelo": modelo_id,
                    "estado": "exitoso",
                    "valor_sugerido": valor_sugerido,
                    "confianza": confianza,
                    "explicacion": explicacion,
                    "tiempo_respuesta_segundos": round(tiempo_respuesta, 2)
                })

            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                resultados_por_modelo.append({
                    "modelo": modelo_id,
                    "estado": "error",
                    "error": str(e)
                })

        # 5. Generar análisis comparativo
        print(f"\n{'=' * 80}")
        print("📊 ANÁLISIS COMPARATIVO")
        print(f"{'=' * 80}")

        modelos_exitosos = [r for r in resultados_por_modelo if r["estado"] == "exitoso"]

        if not modelos_exitosos:
            print("⚠️  Ningún modelo pudo generar una respuesta exitosa")
            mejor_modelo = None
        else:
            # Encontrar mejor modelo (mayor confianza)
            mejor_modelo = max(modelos_exitosos, key=lambda x: x["confianza"])

            print(f"\n🏆 MEJOR MODELO: {mejor_modelo['modelo']}")
            print(f"   Valor sugerido: '{mejor_modelo['valor_sugerido']}'")
            print(f"   Confianza: {mejor_modelo['confianza']:.2%}")
            print(f"   Tiempo: {mejor_modelo['tiempo_respuesta_segundos']}s")

            # Mostrar comparación de todos
            print(f"\n📋 COMPARACIÓN COMPLETA:")
            for resultado in modelos_exitosos:
                print(f"\n   • {resultado['modelo']}")
                print(f"     Valor: '{resultado['valor_sugerido']}'")
                print(f"     Confianza: {resultado['confianza']:.2%}")
                print(f"     Tiempo: {resultado['tiempo_respuesta_segundos']}s")

        # 6. Guardar reporte
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        reporte_file = self.resultados_dir / f"experimento_modelos_{numero_peticion}_{campo}_{timestamp}.json"

        experimento = {
            "timestamp": datetime.now().isoformat(),
            "numero_peticion": numero_peticion,
            "campo": campo,
            "valor_actual_bd": valor_actual_bd,
            "total_modelos_probados": len(resultados_por_modelo),
            "resultados": resultados_por_modelo,
            "mejor_modelo": mejor_modelo["modelo"] if mejor_modelo else None,
            "mejor_confianza": mejor_modelo["confianza"] if mejor_modelo else None
        }

        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(experimento, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Experimento guardado en: {reporte_file}")

        return experimento

    def sugerir_modelo(
        self,
        tipo_tarea: str,
        prioridad: str = "balanceado"
    ) -> Dict[str, Any]:
        """
        Sugiere el modelo más apropiado para un tipo de tarea específico

        Args:
            tipo_tarea: Tipo de tarea (correcciones, validaciones, análisis, experimentación)
            prioridad: Prioridad del usuario (velocidad, precisión, balanceado)

        Returns:
            Dict con recomendación de modelo y justificación
        """
        print(f"\n💡 SUGIRIENDO MODELO ÓPTIMO")
        print("=" * 80)
        print(f"   Tipo de tarea: {tipo_tarea}")
        print(f"   Prioridad: {prioridad}")

        # 1. Listar modelos disponibles
        print("\n📦 1. VERIFICANDO MODELOS DISPONIBLES EN LM STUDIO...")
        modelos_info = self.listar_modelos_disponibles()

        if not modelos_info.get("exito"):
            print(f"❌ Error: {modelos_info.get('error')}")
            return modelos_info

        modelos_disponibles = modelos_info.get("modelos", [])
        print(f"   ✅ {len(modelos_disponibles)} modelo(s) disponibles")

        # 2. Definir características de modelos conocidos
        # Basado en experiencia real con los modelos del proyecto
        caracteristicas_modelos = {
            "llama-3.2-3b": {
                "parametros_b": 3,
                "velocidad": "muy_rapida",
                "precision": "moderada",
                "uso_memoria_gb": 2,
                "ideal_para": ["correcciones_simples", "validaciones_rapidas"],
                "no_ideal_para": ["analisis_complejo", "extraccion_precisa"]
            },
            "qwen2.5-7b": {
                "parametros_b": 7,
                "velocidad": "rapida",
                "precision": "buena",
                "uso_memoria_gb": 4,
                "ideal_para": ["correcciones", "validaciones", "balanceado"],
                "no_ideal_para": ["analisis_muy_complejo"]
            },
            "qwen2.5-14b": {
                "parametros_b": 14,
                "velocidad": "moderada",
                "precision": "muy_buena",
                "uso_memoria_gb": 8,
                "ideal_para": ["analisis_complejo", "correcciones_precisas", "extraccion"],
                "no_ideal_para": ["procesamiento_masivo"]
            },
            "gpt-oss-20b": {
                "parametros_b": 20,
                "velocidad": "lenta",
                "precision": "excelente",
                "uso_memoria_gb": 12,
                "ideal_para": ["validaciones_criticas", "analisis_profundo", "casos_complejos"],
                "no_ideal_para": ["correcciones_masivas", "velocidad_critica"]
            },
            "llama-3.1-70b": {
                "parametros_b": 70,
                "velocidad": "muy_lenta",
                "precision": "excepcional",
                "uso_memoria_gb": 40,
                "ideal_para": ["investigacion", "casos_extremadamente_complejos"],
                "no_ideal_para": ["uso_rutinario", "produccion"]
            }
        }

        # 3. Mapear tipo_tarea a características deseadas
        print("\n🎯 2. ANALIZANDO REQUISITOS DE LA TAREA...")

        requisitos = {}

        if tipo_tarea.lower() in ["correcciones", "corregir", "correcciones_simples"]:
            requisitos = {
                "velocidad_min": "rapida",
                "precision_min": "buena",
                "categorias": ["correcciones", "correcciones_simples", "balanceado"]
            }
            print("   📝 Tarea: Correcciones de campos")
            print("   ⚡ Requiere: Velocidad buena, precisión buena")

        elif tipo_tarea.lower() in ["validaciones", "validar", "validaciones_criticas"]:
            requisitos = {
                "velocidad_min": "moderada",
                "precision_min": "muy_buena",
                "categorias": ["validaciones", "validaciones_criticas", "correcciones_precisas"]
            }
            print("   ✅ Tarea: Validaciones de casos")
            print("   🎯 Requiere: Precisión alta, velocidad moderada")

        elif tipo_tarea.lower() in ["analisis", "analizar", "analisis_complejo"]:
            requisitos = {
                "velocidad_min": "moderada",
                "precision_min": "muy_buena",
                "categorias": ["analisis_complejo", "analisis_profundo", "extraccion"]
            }
            print("   🔍 Tarea: Análisis y extracción compleja")
            print("   🧠 Requiere: Precisión muy alta, comprensión profunda")

        elif tipo_tarea.lower() in ["experimentacion", "experimentar", "investigacion"]:
            requisitos = {
                "velocidad_min": "lenta",
                "precision_min": "excelente",
                "categorias": ["investigacion", "casos_extremadamente_complejos", "casos_complejos"]
            }
            print("   🧪 Tarea: Experimentación e investigación")
            print("   🎓 Requiere: Máxima precisión, sin restricciones de tiempo")

        else:
            print(f"   ⚠️  Tipo de tarea '{tipo_tarea}' no reconocido")
            print("   📋 Tipos válidos: correcciones, validaciones, analisis, experimentacion")
            return {
                "exito": False,
                "error": f"Tipo de tarea '{tipo_tarea}' no reconocido"
            }

        # 4. Aplicar ajustes según prioridad del usuario
        print(f"\n⚙️  3. APLICANDO PRIORIDAD: {prioridad}")

        if prioridad.lower() == "velocidad":
            print("   ⚡ Priorizando velocidad sobre precisión")
            # Bajar requisito de precisión, mantener velocidad
            if requisitos["precision_min"] == "muy_buena":
                requisitos["precision_min"] = "buena"
            elif requisitos["precision_min"] == "excelente":
                requisitos["precision_min"] = "muy_buena"

        elif prioridad.lower() == "precision":
            print("   🎯 Priorizando precisión sobre velocidad")
            # Subir requisito de precisión, bajar requisito de velocidad
            if requisitos["precision_min"] == "buena":
                requisitos["precision_min"] = "muy_buena"
            elif requisitos["precision_min"] == "muy_buena":
                requisitos["precision_min"] = "excelente"

            if requisitos["velocidad_min"] == "rapida":
                requisitos["velocidad_min"] = "moderada"
            elif requisitos["velocidad_min"] == "moderada":
                requisitos["velocidad_min"] = "lenta"

        # 5. Evaluar modelos disponibles
        print("\n📊 4. EVALUANDO MODELOS DISPONIBLES...")

        candidatos = []

        for modelo_id in modelos_disponibles:
            # Buscar características del modelo
            modelo_key = None
            for key in caracteristicas_modelos.keys():
                if key in modelo_id.lower():
                    modelo_key = key
                    break

            if not modelo_key:
                print(f"   ⚠️  Modelo '{modelo_id}' no tiene características conocidas (se omite)")
                continue

            caracteristicas = caracteristicas_modelos[modelo_key]

            # Calcular puntuación de compatibilidad
            puntuacion = 0

            # +10 puntos si la tarea está en ideal_para
            for categoria in requisitos["categorias"]:
                if categoria in caracteristicas["ideal_para"]:
                    puntuacion += 10

            # -5 puntos si la tarea está en no_ideal_para
            for categoria in requisitos["categorias"]:
                if categoria in caracteristicas["no_ideal_para"]:
                    puntuacion -= 5

            # Bonus por velocidad
            if prioridad == "velocidad":
                if caracteristicas["velocidad"] == "muy_rapida":
                    puntuacion += 5
                elif caracteristicas["velocidad"] == "rapida":
                    puntuacion += 3

            # Bonus por precisión
            if prioridad == "precision":
                if caracteristicas["precision"] == "excepcional":
                    puntuacion += 5
                elif caracteristicas["precision"] == "excelente":
                    puntuacion += 4
                elif caracteristicas["precision"] == "muy_buena":
                    puntuacion += 3

            candidatos.append({
                "modelo": modelo_id,
                "puntuacion": puntuacion,
                "caracteristicas": caracteristicas
            })

            print(f"   • {modelo_id}: {puntuacion} puntos")

        # 6. Seleccionar mejor candidato
        if not candidatos:
            print("\n❌ No se encontraron modelos compatibles")
            return {
                "exito": False,
                "error": "No hay modelos disponibles con características conocidas"
            }

        mejor_candidato = max(candidatos, key=lambda x: x["puntuacion"])

        print(f"\n{'=' * 80}")
        print("🏆 RECOMENDACIÓN FINAL")
        print(f"{'=' * 80}")
        print(f"\n   Modelo recomendado: {mejor_candidato['modelo']}")
        print(f"   Puntuación: {mejor_candidato['puntuacion']}")
        print(f"\n   Características:")
        print(f"   • Parámetros: {mejor_candidato['caracteristicas']['parametros_b']}B")
        print(f"   • Velocidad: {mejor_candidato['caracteristicas']['velocidad']}")
        print(f"   • Precisión: {mejor_candidato['caracteristicas']['precision']}")
        print(f"   • Memoria estimada: {mejor_candidato['caracteristicas']['uso_memoria_gb']} GB")
        print(f"\n   Ideal para:")
        for uso in mejor_candidato['caracteristicas']['ideal_para']:
            print(f"   ✓ {uso.replace('_', ' ').title()}")

        if mejor_candidato['caracteristicas']['no_ideal_para']:
            print(f"\n   No recomendado para:")
            for uso in mejor_candidato['caracteristicas']['no_ideal_para']:
                print(f"   ✗ {uso.replace('_', ' ').title()}")

        # 7. Mostrar alternativas
        if len(candidatos) > 1:
            print(f"\n📋 ALTERNATIVAS:")
            alternativas = sorted(candidatos, key=lambda x: x["puntuacion"], reverse=True)[1:4]

            for alt in alternativas:
                print(f"\n   • {alt['modelo']} ({alt['puntuacion']} puntos)")
                print(f"     Velocidad: {alt['caracteristicas']['velocidad']}, Precisión: {alt['caracteristicas']['precision']}")

        # 8. Guardar reporte
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        reporte_file = self.resultados_dir / f"sugerencia_modelo_{tipo_tarea}_{prioridad}_{timestamp}.json"

        sugerencia = {
            "timestamp": datetime.now().isoformat(),
            "tipo_tarea": tipo_tarea,
            "prioridad": prioridad,
            "modelo_recomendado": mejor_candidato["modelo"],
            "puntuacion": mejor_candidato["puntuacion"],
            "caracteristicas": mejor_candidato["caracteristicas"],
            "alternativas": [{"modelo": a["modelo"], "puntuacion": a["puntuacion"]} for a in alternativas] if len(candidatos) > 1 else []
        }

        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(sugerencia, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Sugerencia guardada en: {reporte_file}")

        return sugerencia

    # =========================================================================
    # SECCIÓN 3: DIAGNÓSTICO DE PROMPTS (NUEVO)
    # =========================================================================

    def analizar_prompts(self) -> Dict[str, Any]:
        """
        Analiza todos los prompts en core/prompts/

        Returns:
            Dict con análisis de calidad de prompts
        """
        print("\n📝 ANALIZANDO PROMPTS DEL SISTEMA...")
        print("=" * 80)

        if not self.prompts_dir.exists():
            return {
                "exito": False,
                "error": f"No se encontró directorio de prompts: {self.prompts_dir}"
            }

        prompts_txt = list(self.prompts_dir.glob("*.txt"))

        if not prompts_txt:
            return {
                "exito": False,
                "error": "No se encontraron archivos .txt en core/prompts/"
            }

        analisis = {}

        for prompt_file in prompts_txt:
            print(f"\n📄 Analizando: {prompt_file.name}")

            with open(prompt_file, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Análisis básico
            lineas = contenido.split('\n')
            palabras = contenido.split()

            # Detectar instrucciones críticas
            instrucciones_criticas = self._detectar_instrucciones_criticas(contenido)

            # Detectar contradicciones
            contradicciones = self._detectar_contradicciones_prompt(contenido)

            # Calcular score de calidad
            score_calidad = self._calcular_score_calidad_prompt(contenido)

            analisis[prompt_file.name] = {
                "archivo": str(prompt_file),
                "lineas": len(lineas),
                "palabras": len(palabras),
                "caracteres": len(contenido),
                "instrucciones_criticas": instrucciones_criticas,
                "contradicciones": contradicciones,
                "score_calidad": score_calidad,
                "recomendaciones": self._generar_recomendaciones_prompt(contenido, contradicciones)
            }

            print(f"  📊 Líneas: {len(lineas)} | Palabras: {len(palabras)}")
            print(f"  ⭐ Score de calidad: {score_calidad:.2f}/10")
            if contradicciones:
                print(f"  ⚠️  {len(contradicciones)} contradicción(es) detectada(s)")

        # Guardar análisis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.resultados_dir / f"analisis_prompts_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analisis, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Análisis guardado en: {output_file}")

        return {
            "exito": True,
            "analisis": analisis,
            "total_prompts": len(analisis)
        }

    def _detectar_instrucciones_criticas(self, contenido: str) -> List[str]:
        """Detecta instrucciones críticas en el prompt"""
        instrucciones = []

        patrones_criticos = [
            (r'NUNCA', 'Instrucción prohibitiva'),
            (r'SIEMPRE', 'Instrucción obligatoria'),
            (r'NO\s+(revises|completes|inferir|asumas)', 'Restricción de acción'),
            (r'SOLO\s+', 'Limitación de alcance'),
            (r'IMPORTANTE:', 'Directiva importante'),
            (r'CRÍTICO:', 'Directiva crítica'),
        ]

        for patron, tipo in patrones_criticos:
            matches = re.finditer(patron, contenido, re.IGNORECASE)
            for match in matches:
                # Extraer contexto (línea completa)
                inicio_linea = contenido.rfind('\n', 0, match.start()) + 1
                fin_linea = contenido.find('\n', match.end())
                if fin_linea == -1:
                    fin_linea = len(contenido)

                linea = contenido[inicio_linea:fin_linea].strip()
                instrucciones.append({
                    "tipo": tipo,
                    "texto": linea[:100]  # Primeros 100 chars
                })

        return instrucciones

    def _detectar_contradicciones_prompt(self, contenido: str) -> List[str]:
        """
        Detecta posibles contradicciones en el prompt

        Args:
            contenido: Texto del prompt

        Returns:
            Lista de contradicciones detectadas
        """
        contradicciones = []

        # Patrones de contradicción
        lineas = contenido.split('\n')

        instrucciones_nunca = []
        instrucciones_siempre = []

        for i, linea in enumerate(lineas):
            if re.search(r'NUNCA|❌', linea, re.IGNORECASE):
                instrucciones_nunca.append((i, linea))
            if re.search(r'SIEMPRE|✅', linea, re.IGNORECASE):
                instrucciones_siempre.append((i, linea))

        # Buscar contradicciones entre NUNCA y SIEMPRE sobre el mismo concepto
        for idx_nunca, linea_nunca in instrucciones_nunca:
            for idx_siempre, linea_siempre in instrucciones_siempre:
                # Extraer conceptos clave de cada línea
                conceptos_nunca = set(re.findall(r'\b\w{5,}\b', linea_nunca.lower()))
                conceptos_siempre = set(re.findall(r'\b\w{5,}\b', linea_siempre.lower()))

                # Si hay solapamiento significativo, posible contradicción
                solapamiento = conceptos_nunca & conceptos_siempre
                if len(solapamiento) >= 2:  # Al menos 2 palabras en común
                    contradicciones.append(
                        f"Posible contradicción entre líneas {idx_nunca+1} y {idx_siempre+1}: "
                        f"'{linea_nunca[:50]}...' vs '{linea_siempre[:50]}...'"
                    )

        return contradicciones

    def _calcular_score_calidad_prompt(self, contenido: str) -> float:
        """
        Calcula un score de calidad del prompt (0-10)

        Args:
            contenido: Texto del prompt

        Returns:
            Score de 0.0 a 10.0
        """
        score = 10.0

        # Penalizar prompts muy cortos
        if len(contenido) < 200:
            score -= 3.0

        # Penalizar prompts muy largos (>5000 chars)
        if len(contenido) > 5000:
            score -= 1.0

        # Bonificar estructura clara (secciones numeradas, bullets)
        if re.search(r'^\d+\.', contenido, re.MULTILINE):
            score += 1.0
        if re.search(r'^-\s', contenido, re.MULTILINE):
            score += 0.5

        # Bonificar ejemplos
        if 'ejemplo' in contenido.lower() or 'ej:' in contenido.lower():
            score += 0.5

        # Bonificar instrucciones claras (NUNCA, SIEMPRE, IMPORTANTE)
        instrucciones_claras = len(re.findall(r'(NUNCA|SIEMPRE|IMPORTANTE|CRÍTICO)', contenido))
        score += min(instrucciones_claras * 0.2, 1.5)

        # Penalizar ambigüedad
        palabras_ambiguas = len(re.findall(r'\b(tal vez|quizás|posiblemente|puede ser)\b', contenido, re.IGNORECASE))
        score -= palabras_ambiguas * 0.3

        return max(0.0, min(10.0, score))

    def _generar_recomendaciones_prompt(self, contenido: str, contradicciones: List[str]) -> List[str]:
        """
        Genera recomendaciones para mejorar el prompt

        Args:
            contenido: Texto del prompt
            contradicciones: Lista de contradicciones detectadas

        Returns:
            Lista de recomendaciones
        """
        recomendaciones = []

        if len(contenido) < 200:
            recomendaciones.append("⚠️  Prompt muy corto. Considera agregar más contexto y ejemplos.")

        if len(contenido) > 5000:
            recomendaciones.append("⚠️  Prompt muy largo. Considera dividirlo en secciones más específicas.")

        if contradicciones:
            recomendaciones.append(f"❌ {len(contradicciones)} contradicción(es) detectada(s). Revisa la consistencia de las instrucciones.")

        if 'ejemplo' not in contenido.lower():
            recomendaciones.append("💡 Considera agregar ejemplos concretos para mayor claridad.")

        if not re.search(r'formato.*json', contenido, re.IGNORECASE):
            recomendaciones.append("💡 Si esperas respuesta JSON, especifícalo explícitamente en el prompt.")

        return recomendaciones if recomendaciones else ["✅ Prompt bien estructurado. Sin recomendaciones críticas."]

    # =========================================================================
    # SECCIÓN 4: EXPERIMENTACIÓN SANDBOX (NUEVO)
    # =========================================================================

    def simular_extraccion(self, texto: str, biomarcador: Optional[str] = None) -> Dict[str, Any]:
        """
        Simula extracción de datos de un texto sin afectar BD

        Args:
            texto: Texto a analizar
            biomarcador: Biomarcador específico a extraer (opcional)

        Returns:
            Dict con resultado de la simulación
        """
        print("\n🧪 SIMULACIÓN DE EXTRACCIÓN (SANDBOX)")
        print("=" * 80)
        print(f"📝 Texto: {texto[:100]}...")
        if biomarcador:
            print(f"🎯 Biomarcador objetivo: {biomarcador}")

        # Inicializar cliente LLM
        self._inicializar_llm_client()

        # Cargar prompt de sistema
        prompt_file = self.prompts_dir / "system_prompt_comun.txt"
        if prompt_file.exists():
            with open(prompt_file, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
        else:
            system_prompt = "Eres un experto en extracción de datos médicos de informes IHQ."

        if biomarcador:
            user_prompt = f"Extrae ÚNICAMENTE el valor de {biomarcador} del siguiente texto médico:\n\n{texto}\n\nResponde en formato JSON con: {{\"valor\": \"...\", \"confianza\": 0.0-1.0}}"
        else:
            user_prompt = f"Extrae todos los biomarcadores y datos relevantes del siguiente texto médico:\n\n{texto}\n\nResponde en formato JSON."

        inicio = time.time()
        resultado = self.llm_client.completar(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=500,
            formato_json=True
        )
        tiempo_respuesta = time.time() - inicio

        if resultado["exito"]:
            print(f"\n✅ SIMULACIÓN EXITOSA")
            print(f"⏱️  Tiempo de respuesta: {tiempo_respuesta:.2f}s")
            print(f"📊 Tokens usados: {resultado['tokens_usados']['total']}")
            print(f"\n💬 Resultado:")
            print(json.dumps(resultado["respuesta"], indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ ERROR EN SIMULACIÓN: {resultado.get('error')}")

        # Guardar simulación
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.resultados_dir / f"simulacion_ia_{timestamp}.json"

        simulacion_data = {
            "timestamp": datetime.now().isoformat(),
            "texto_entrada": texto,
            "biomarcador_objetivo": biomarcador,
            "tiempo_respuesta_segundos": tiempo_respuesta,
            "resultado": resultado
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(simulacion_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Simulación guardada en: {output_file}")

        return simulacion_data

    # =========================================================================
    # SECCIÓN 5: EDICIÓN DE PROMPTS (NUEVO)
    # =========================================================================

    def editar_prompt(
        self,
        nombre_archivo: str,
        cambios: str,
        simular_primero: bool = True,
        aplicar: bool = False
    ) -> Dict[str, Any]:
        """
        Edita un archivo de prompt con versionado automático

        Args:
            nombre_archivo: Nombre del archivo prompt (ej: system_prompt_comun.txt)
            cambios: Descripción de los cambios a realizar
            simular_primero: Si True, simula el cambio antes de aplicar
            aplicar: Si True, aplica el cambio (requiere simular_primero=False o aprobación)

        Returns:
            Dict con resultado de la edición
        """
        prompt_file = self.prompts_dir / nombre_archivo

        if not prompt_file.exists():
            return {
                "exito": False,
                "error": f"No se encontró el archivo: {nombre_archivo}"
            }

        print(f"\n✏️  EDITANDO PROMPT: {nombre_archivo}")
        print("=" * 80)
        print(f"📝 Cambios solicitados: {cambios}")

        if simular_primero and not aplicar:
            print("\n🧪 MODO SIMULACIÓN (DRY-RUN)")
            print("Los cambios NO se aplicarán al archivo real.")
            print("\nPara aplicar cambios, usa: --editar-prompt {} --aplicar".format(nombre_archivo))

            return {
                "exito": True,
                "modo": "simulacion",
                "archivo": str(prompt_file),
                "cambios_propuestos": cambios,
                "mensaje": "Simulación completada. Los cambios NO fueron aplicados."
            }

        if aplicar:
            # Crear backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backups_dir / f"{prompt_file.stem}_{timestamp}{prompt_file.suffix}.bak"

            print(f"\n💾 Creando backup en: {backup_file}")
            shutil.copy2(prompt_file, backup_file)

            # Aquí iría la lógica de edición automática
            # Por ahora, solo mostramos mensaje
            print("\n⚠️  ADVERTENCIA: Edición automática de prompts requiere implementación específica.")
            print("Por favor, edita manualmente el archivo y confirma los cambios.")

            # Generar reporte de cambios
            reporte_file = self.resultados_dir / f"cambios_prompt_{timestamp}.md"
            reporte_md = f"""# Edición de Prompt - {nombre_archivo}

**Fecha**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Archivo**: `{prompt_file}`
**Backup**: `{backup_file}`

## Cambios Solicitados

{cambios}

## Estado

⚠️  Cambios pendientes de aplicación manual.

## Pasos Siguientes

1. Editar manualmente `{prompt_file}`
2. Verificar con: `python herramientas_ia/gestor_ia_lm_studio.py --analizar-prompts`
3. Probar con: `python herramientas_ia/gestor_ia_lm_studio.py --simular "texto de prueba"`

---
🤖 Generado por gestor_ia_lm_studio.py
"""

            with open(reporte_file, 'w', encoding='utf-8') as f:
                f.write(reporte_md)

            print(f"\n📋 Reporte generado en: {reporte_file}")

            return {
                "exito": True,
                "modo": "aplicado",
                "archivo": str(prompt_file),
                "backup": str(backup_file),
                "reporte": str(reporte_file),
                "cambios": cambios
            }

    # =========================================================================
    # SECCIÓN 6: GENERACIÓN DE REPORTES
    # =========================================================================

    def generar_reporte_estado(self) -> Dict[str, Any]:
        """
        Genera reporte completo del estado del sistema IA

        Returns:
            Dict con estado completo
        """
        print("\n📊 GENERANDO REPORTE DE ESTADO DEL SISTEMA IA...")
        print("=" * 80)

        # Verificar servidor
        servidor_info = self.verificar_servidor(verbose=False)

        # Listar modelos
        modelos_info = self.listar_modelos_disponibles() if servidor_info["detectado"] else {"modelos": []}

        # Analizar prompts
        prompts_info = self.analizar_prompts() if self.prompts_dir.exists() else {"analisis": {}}

        # Contar archivos en resultados
        total_validaciones = len(list(self.resultados_dir.glob("validacion_*.json"))) if self.resultados_dir.exists() else 0
        total_simulaciones = len(list(self.resultados_dir.glob("simulacion_*.json"))) if self.resultados_dir.exists() else 0

        # Generar reporte
        reporte = {
            "timestamp": datetime.now().isoformat(),
            "servidor_lm_studio": {
                "activo": servidor_info["detectado"],
                "endpoint": servidor_info.get("endpoint"),
                "modelo_actual": servidor_info.get("modelo", {}).get("id") if servidor_info.get("modelo") else None,
                "capacidades": servidor_info.get("capacidades", [])
            },
            "modelos_disponibles": modelos_info.get("modelos", []),
            "prompts": {
                "total": len(prompts_info.get("analisis", {})),
                "analisis": prompts_info.get("analisis", {})
            },
            "estadisticas_uso": {
                "total_validaciones": total_validaciones,
                "total_simulaciones": total_simulaciones,
                "total_backups": len(list(self.backups_dir.glob("*.bak"))) if self.backups_dir.exists() else 0
            }
        }

        # Guardar reporte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.resultados_dir / f"estado_sistema_ia_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(reporte, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Reporte guardado en: {output_file}")

        # Mostrar resumen
        print("\n📋 RESUMEN DEL ESTADO:")
        print(f"  LM Studio: {'✅ Activo' if reporte['servidor_lm_studio']['activo'] else '❌ Inactivo'}")
        if reporte['servidor_lm_studio']['activo']:
            print(f"  Modelo: {reporte['servidor_lm_studio']['modelo_actual']}")
        print(f"  Prompts: {reporte['prompts']['total']} archivo(s)")
        print(f"  Validaciones realizadas: {reporte['estadisticas_uso']['total_validaciones']}")
        print(f"  Simulaciones realizadas: {reporte['estadisticas_uso']['total_simulaciones']}")

        return reporte


def main():
    """Función principal CLI"""
    parser = argparse.ArgumentParser(
        description="🤖 Gestor Integral de IA - LM Studio v2.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:

  # VERIFICACIÓN
  python herramientas_ia/gestor_ia_lm_studio.py --estado
  python herramientas_ia/gestor_ia_lm_studio.py --probar-conexion
  python herramientas_ia/gestor_ia_lm_studio.py --listar-modelos

  # CORRECCIONES
  python herramientas_ia/gestor_ia_lm_studio.py --validar-caso IHQ250025 --dry-run
  python herramientas_ia/gestor_ia_lm_studio.py --validar-caso IHQ250025 --campo IHQ_Ki67 --dry-run
  python herramientas_ia/gestor_ia_lm_studio.py --validar-lote --ultimos 10

  # DIAGNÓSTICO
  python herramientas_ia/gestor_ia_lm_studio.py --analizar-prompts
  python herramientas_ia/gestor_ia_lm_studio.py --analizar-completitud IHQ251037
  python herramientas_ia/gestor_ia_lm_studio.py --diagnosticar-fallo IHQ251037 --campo-problema IHQ_Ki67 --valor-esperado "20%"

  # EXPERIMENTACIÓN
  python herramientas_ia/gestor_ia_lm_studio.py --simular "Ki-67: 25%"
  python herramientas_ia/gestor_ia_lm_studio.py --experimentar-modelos IHQ251037 --campo-experimento IHQ_Ki67
  python herramientas_ia/gestor_ia_lm_studio.py --sugerir-modelo correcciones --prioridad velocidad
  python herramientas_ia/gestor_ia_lm_studio.py --sugerir-modelo validaciones --prioridad precision

  # EDICIÓN
  python herramientas_ia/gestor_ia_lm_studio.py --editar-prompt system_prompt_comun.txt --simular

NOTAS:
  - Todos los reportes se guardan en herramientas_ia/resultados/
  - Los backups se guardan en backups/ (raíz del proyecto)
  - Usa --dry-run para simular antes de aplicar cambios
"""
    )

    # VERIFICACIÓN
    parser.add_argument(
        "--estado",
        action="store_true",
        help="Mostrar estado completo del sistema IA"
    )

    parser.add_argument(
        "--probar-conexion",
        action="store_true",
        help="Probar conexión e inferencia con LM Studio"
    )

    parser.add_argument(
        "--listar-modelos",
        action="store_true",
        help="Listar modelos disponibles en LM Studio"
    )

    # CORRECCIONES
    parser.add_argument(
        "--validar-caso",
        type=str,
        metavar="IHQ250025",
        help="Validar un caso específico"
    )

    parser.add_argument(
        "--campo",
        type=str,
        metavar="NOMBRE_CAMPO",
        help="Campo específico a validar (usar con --validar-caso para validar solo ese campo)"
    )

    parser.add_argument(
        "--validar-lote",
        action="store_true",
        help="Validar un lote de casos"
    )

    parser.add_argument(
        "--ultimos",
        type=int,
        default=10,
        metavar="N",
        help="Número de casos en el lote (default: 10)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Simular sin aplicar cambios (default: True)"
    )

    # DIAGNÓSTICO DE PROMPTS
    parser.add_argument(
        "--analizar-prompts",
        action="store_true",
        help="Analizar calidad de todos los prompts"
    )

    parser.add_argument(
        "--analizar-completitud",
        type=str,
        metavar="IHQ250025",
        help="Analizar por qué un caso está marcado como incompleto"
    )

    parser.add_argument(
        "--diagnosticar-fallo",
        type=str,
        metavar="IHQ251037",
        help="Diagnosticar por qué la IA no corrigió bien un campo"
    )

    parser.add_argument(
        "--campo-problema",
        type=str,
        metavar="IHQ_Ki67",
        help="Campo problemático a diagnosticar (usar con --diagnosticar-fallo)"
    )

    parser.add_argument(
        "--valor-esperado",
        type=str,
        metavar="20%",
        help="Valor esperado del campo (opcional, para diagnóstico más preciso)"
    )

    parser.add_argument(
        "--experimentar-modelos",
        type=str,
        metavar="IHQ251037",
        help="Experimentar con todos los modelos disponibles en LM Studio para un caso/campo"
    )

    parser.add_argument(
        "--campo-experimento",
        type=str,
        metavar="IHQ_Ki67",
        help="Campo a experimentar (usar con --experimentar-modelos)"
    )

    parser.add_argument(
        "--sugerir-modelo",
        type=str,
        metavar="TIPO_TAREA",
        help="Sugerir modelo óptimo para un tipo de tarea (correcciones, validaciones, analisis, experimentacion)"
    )

    parser.add_argument(
        "--prioridad",
        type=str,
        default="balanceado",
        choices=["velocidad", "precision", "balanceado"],
        help="Prioridad al sugerir modelo (default: balanceado)"
    )

    # EXPERIMENTACIÓN
    parser.add_argument(
        "--simular",
        type=str,
        metavar="TEXTO",
        help="Simular extracción de datos de un texto"
    )

    parser.add_argument(
        "--biomarcador",
        type=str,
        metavar="Ki-67",
        help="Biomarcador específico a extraer en simulación"
    )

    # EDICIÓN
    parser.add_argument(
        "--editar-prompt",
        type=str,
        metavar="ARCHIVO",
        help="Editar un archivo de prompt"
    )

    parser.add_argument(
        "--cambios",
        type=str,
        metavar="DESC",
        help="Descripción de cambios a realizar en el prompt"
    )

    parser.add_argument(
        "--aplicar",
        action="store_true",
        help="Aplicar cambios (por defecto solo simula)"
    )

    # GENERAL
    parser.add_argument(
        "--endpoint",
        type=str,
        metavar="URL",
        help="Endpoint personalizado de LM Studio"
    )

    parser.add_argument(
        "--json",
        type=str,
        metavar="ARCHIVO",
        help="Exportar resultado a JSON"
    )

    args = parser.parse_args()

    # Crear gestor
    gestor = GestorIALMStudio(custom_endpoint=args.endpoint)

    resultado = None

    # VERIFICACIÓN
    if args.estado:
        resultado = gestor.generar_reporte_estado()

    elif args.probar_conexion:
        servidor_info = gestor.verificar_servidor()
        if servidor_info["detectado"]:
            resultado = gestor.probar_inferencia()
        else:
            resultado = servidor_info

    elif args.listar_modelos:
        resultado = gestor.listar_modelos_disponibles()

    # CORRECCIONES
    elif args.validar_caso:
        numero_peticion = args.validar_caso.upper()
        if not numero_peticion.startswith("IHQ"):
            numero_peticion = f"IHQ{numero_peticion}"

        resultado = gestor.validar_caso(
            numero_peticion=numero_peticion,
            campo_especifico=args.campo,
            dry_run=args.dry_run
        )

    elif args.validar_lote:
        resultado = gestor.validar_lote(
            ultimos_n=args.ultimos,
            dry_run=args.dry_run
        )

    # DIAGNÓSTICO DE PROMPTS
    elif args.analizar_prompts:
        resultado = gestor.analizar_prompts()

    elif args.analizar_completitud:
        numero_peticion = args.analizar_completitud.upper()
        if not numero_peticion.startswith("IHQ"):
            numero_peticion = f"IHQ{numero_peticion}"
        resultado = gestor.analizar_completitud(numero_peticion=numero_peticion)

    elif args.diagnosticar_fallo:
        numero_peticion = args.diagnosticar_fallo.upper()
        if not numero_peticion.startswith("IHQ"):
            numero_peticion = f"IHQ{numero_peticion}"

        if not args.campo_problema:
            print("❌ Error: Debes especificar --campo-problema para diagnosticar un fallo")
            return

        resultado = gestor.diagnosticar_fallo(
            numero_peticion=numero_peticion,
            campo=args.campo_problema,
            valor_esperado=args.valor_esperado
        )

    elif args.experimentar_modelos:
        numero_peticion = args.experimentar_modelos.upper()
        if not numero_peticion.startswith("IHQ"):
            numero_peticion = f"IHQ{numero_peticion}"

        if not args.campo_experimento:
            print("❌ Error: Debes especificar --campo-experimento para experimentar con modelos")
            return

        resultado = gestor.experimentar_modelos(
            numero_peticion=numero_peticion,
            campo=args.campo_experimento
        )

    elif args.sugerir_modelo:
        resultado = gestor.sugerir_modelo(
            tipo_tarea=args.sugerir_modelo,
            prioridad=args.prioridad
        )

    # EXPERIMENTACIÓN
    elif args.simular:
        resultado = gestor.simular_extraccion(
            texto=args.simular,
            biomarcador=args.biomarcador
        )

    # EDICIÓN
    elif args.editar_prompt:
        if not args.cambios and args.aplicar:
            print("❌ Error: Debes especificar --cambios cuando uses --aplicar")
            return

        resultado = gestor.editar_prompt(
            nombre_archivo=args.editar_prompt,
            cambios=args.cambios or "Simulación de edición",
            simular_primero=not args.aplicar,
            aplicar=args.aplicar
        )

    else:
        parser.print_help()
        return

    # Guardar en JSON si se solicita
    if args.json and resultado:
        output_path = Path(args.json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultado, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultado exportado a: {output_path}")


if __name__ == "__main__":
    main()
