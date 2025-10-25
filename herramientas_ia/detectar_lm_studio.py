#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DETECTOR DE LM STUDIO LOCAL
================================

Detecta y valida la configuración de LM Studio corriendo localmente.
Obtiene información del modelo, capacidades y conectividad.

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List

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

class LMStudioDetector:
    """Detector y validador de LM Studio local"""

    DEFAULT_ENDPOINTS = [
        "http://127.0.0.1:1234",
        "http://localhost:1234",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    def __init__(self, custom_endpoint: Optional[str] = None):
        """
        Inicializar detector

        Args:
            custom_endpoint: Endpoint personalizado (opcional)
        """
        self.endpoints = [custom_endpoint] if custom_endpoint else self.DEFAULT_ENDPOINTS
        self.active_endpoint = None
        self.model_info = None

    def detectar_servidor(self) -> Dict[str, Any]:
        """
        Detecta si LM Studio está corriendo y en qué puerto

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

        print("🔍 DETECTANDO LM STUDIO LOCAL...")
        print("=" * 80)

        for endpoint in self.endpoints:
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

                        print(f"✅ LM Studio DETECTADO en {endpoint}")
                        print(f"📦 Modelo cargado: {modelo.get('id', 'desconocido')}")
                    else:
                        print(f"⚠️ Servidor activo pero sin modelos cargados")
                        resultado["error"] = "Sin modelos cargados"

                    # Probar capacidades
                    resultado["capacidades"] = self._probar_capacidades(endpoint)

                    break

            except requests.exceptions.ConnectionError:
                print(f"❌ No hay conexión en {endpoint}")
            except requests.exceptions.Timeout:
                print(f"⏱️ Timeout en {endpoint}")
            except Exception as e:
                print(f"⚠️ Error en {endpoint}: {e}")

        if not resultado["detectado"]:
            resultado["error"] = "No se encontró LM Studio activo en los puertos predeterminados"
            print("\n❌ LM STUDIO NO DETECTADO")
            print("💡 Asegúrate de que LM Studio esté corriendo y tenga un modelo cargado")

        return resultado

    def _probar_capacidades(self, endpoint: str) -> List[str]:
        """
        Prueba las capacidades del servidor LM Studio

        Args:
            endpoint: URL del servidor

        Returns:
            Lista de capacidades disponibles
        """
        capacidades = []

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
            deteccion = self.detectar_servidor()
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

    def guardar_configuracion(self, output_file: str = "lm_studio_config.json") -> bool:
        """
        Guarda la configuración detectada en un archivo JSON

        Args:
            output_file: Ruta del archivo de salida

        Returns:
            True si se guardó correctamente
        """
        deteccion = self.detectar_servidor()

        config = {
            "timestamp": Path(__file__).stat().st_mtime,
            "deteccion": deteccion,
            "endpoint_activo": self.active_endpoint,
            "modelo_info": self.model_info
        }

        output_path = Path(__file__).parent / "resultados" / output_file
        output_path.parent.mkdir(exist_ok=True)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Configuración guardada en: {output_path}")
            return True
        except Exception as e:
            print(f"\n❌ Error guardando configuración: {e}")
            return False

    def obtener_info_completa(self) -> Dict[str, Any]:
        """
        Obtiene información completa del servidor LM Studio

        Returns:
            Dict con toda la información disponible
        """
        deteccion = self.detectar_servidor()

        info_completa = {
            "servidor": deteccion,
            "inferencia": None,
            "recomendaciones": []
        }

        if deteccion["detectado"]:
            # Probar inferencia
            inferencia = self.probar_inferencia()
            info_completa["inferencia"] = inferencia

            # Generar recomendaciones
            if "chat_completions" in deteccion["capacidades"]:
                info_completa["recomendaciones"].append(
                    "✅ Usar endpoint /v1/chat/completions para validación de campos médicos"
                )

            if inferencia.get("exito"):
                info_completa["recomendaciones"].append(
                    "✅ El modelo está respondiendo correctamente - listo para integración"
                )
            else:
                info_completa["recomendaciones"].append(
                    "⚠️ El modelo tiene problemas de inferencia - verificar configuración"
                )
        else:
            info_completa["recomendaciones"].extend([
                "❌ LM Studio no está activo",
                "💡 Iniciar LM Studio y cargar un modelo",
                "💡 Verificar que el servidor local esté en puerto 1234"
            ])

        return info_completa


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(
        description="🔍 Detector de LM Studio Local v1.0.0",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--endpoint",
        type=str,
        help="Endpoint personalizado (ej: http://localhost:1234)"
    )

    parser.add_argument(
        "--probar",
        action="store_true",
        help="Probar inferencia con prompt de prueba"
    )

    parser.add_argument(
        "--prompt",
        type=str,
        default="Di 'OK' si estás funcionando correctamente.",
        help="Prompt personalizado para prueba de inferencia"
    )

    parser.add_argument(
        "--guardar",
        action="store_true",
        help="Guardar configuración detectada en JSON"
    )

    parser.add_argument(
        "--json",
        type=str,
        help="Guardar resultado completo en archivo JSON"
    )

    args = parser.parse_args()

    # Crear detector
    detector = LMStudioDetector(custom_endpoint=args.endpoint)

    # Obtener información completa
    info = detector.obtener_info_completa()

    # Guardar en JSON si se solicita
    if args.json:
        output_path = Path(args.json)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Información completa guardada en: {output_path}")

    # Guardar configuración si se solicita
    if args.guardar:
        detector.guardar_configuracion()

    # Mostrar resumen final
    print("\n" + "=" * 80)
    print("📋 RESUMEN DE DETECCIÓN")
    print("=" * 80)

    if info["servidor"]["detectado"]:
        print(f"✅ Estado: LM Studio ACTIVO")
        print(f"🌐 Endpoint: {info['servidor']['endpoint']}")
        print(f"📦 Modelo: {info['servidor']['modelo']['id']}")
        print(f"🔧 Capacidades: {', '.join(info['servidor']['capacidades'])}")

        if info["inferencia"] and info["inferencia"].get("exito"):
            print(f"🧠 Inferencia: FUNCIONANDO")
        else:
            print(f"⚠️ Inferencia: CON PROBLEMAS")
    else:
        print(f"❌ Estado: LM Studio NO DETECTADO")
        print(f"⚠️ Error: {info['servidor']['error']}")

    print("\n💡 RECOMENDACIONES:")
    for rec in info["recomendaciones"]:
        print(f"  {rec}")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
