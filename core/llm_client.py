#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 CLIENTE LLM - Multi-Proveedor Gratuito
==========================================

Cliente con fallback automático entre múltiples proveedores de IA gratuitos:
  1. Google Gemini  (1,500 req/día gratis)
  2. Groq           (14,400 req/día gratis)
  3. OpenRouter     (~10-20 req/día gratis)

Todos usan formato OpenAI-compatible (chat/completions).
Si un proveedor se agota (HTTP 402), automáticamente prueba el siguiente.

VERSION 4.0.0 - Multi-Proveedor (10 Abr 2026):
- 3 proveedores gratuitos con fallback automático
- ~16,000 requests/día combinados (gratis)
- Suficiente para auditar cientos de casos sin costo

Autor: Sistema EVARISIS
Versión: 4.0.0
Fecha: 10 de abril de 2026
"""

import json
import logging
import os
import sys
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import time
import threading

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


class LMStudioClient:
    """Cliente LLM multi-proveedor (Gemini, Groq, OpenRouter) - todos gratuitos"""

    # Semáforo de clase para limitar concurrencia global
    _request_semaphore = threading.Semaphore(2)
    _last_request_time = 0
    _min_request_interval = 0.5  # 500ms entre peticiones

    # === CONFIGURACIÓN DE PROVEEDORES ===
    # Orden = prioridad de uso. Si uno se agota, pasa al siguiente.
    PROVEEDORES_CONFIG = [
        {
            "nombre": "Gemini",
            "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
            "modelos": [
                "gemma-3-27b-it",
                "gemini-2.0-flash-lite",
                "gemini-2.0-flash",
            ],
            "config_section": "gemini",
            "headers_extra": {},
            "descripcion": "15 req/min, 1500 req/dia gratis",
            "info_key": "Gratis en: https://aistudio.google.com/apikey",
        },
        {
            "nombre": "Groq",
            "endpoint": "https://api.groq.com/openai/v1",
            "modelos": [
                "llama-3.3-70b-versatile",
                "gemma2-9b-it",
                "llama-3.1-8b-instant",
            ],
            "config_section": "groq",
            "headers_extra": {},
            "descripcion": "30 req/min, 14400 req/dia gratis",
            "info_key": "Gratis en: https://console.groq.com/keys",
        },
        {
            "nombre": "OpenRouter",
            "endpoint": "https://openrouter.ai/api/v1",
            "modelos": [
                "google/gemma-4-31b-it:free",
                "meta-llama/llama-3.3-70b-instruct:free",
                "nvidia/nemotron-3-super-120b-a12b:free",
                "google/gemma-3-27b-it:free",
                "nousresearch/hermes-3-llama-3.1-405b:free",
                "qwen/qwen3-coder:free",
                "minimax/minimax-m2.5:free",
            ],
            "config_section": "openrouter",
            "headers_extra": {
                "HTTP-Referer": "https://evarisis-huv.local",
                "X-Title": "EVARISIS Gestor Oncologico"
            },
            "descripcion": "~10-20 req/dia gratis",
            "info_key": "Gratis en: https://openrouter.ai/keys",
        },
    ]

    # Backward compatibility alias
    MODELOS_GRATUITOS = PROVEEDORES_CONFIG[2]["modelos"]  # OpenRouter models

    def __init__(
        self,
        endpoint: str = "https://openrouter.ai/api/v1",
        model: Optional[str] = None,
        timeout: int = 120,
        max_retries: int = 3,
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session_history = []

        # Cargar todos los proveedores que tengan API key configurada
        self._proveedores_disponibles = []
        for prov_config in self.PROVEEDORES_CONFIG:
            key = self._cargar_api_key(prov_config["config_section"])
            if key:
                self._proveedores_disponibles.append({**prov_config, "api_key": key})

        # Si se pasó api_key explícita y no hay OpenRouter cargado, agregarla
        if api_key:
            tiene_openrouter = any(p["config_section"] == "openrouter" for p in self._proveedores_disponibles)
            if not tiene_openrouter:
                for prov_config in self.PROVEEDORES_CONFIG:
                    if prov_config["config_section"] == "openrouter":
                        self._proveedores_disponibles.append({**prov_config, "api_key": api_key})
                        break

        # Backward compatibility: self.endpoint, self.model, self.api_key
        if self._proveedores_disponibles:
            self.endpoint = self._proveedores_disponibles[0]["endpoint"]
            self.model = self._proveedores_disponibles[0]["modelos"][0]
            self.api_key = self._proveedores_disponibles[0]["api_key"]
            provs = [p["nombre"] for p in self._proveedores_disponibles]
            logging.info(f"✅ LLM Multi-proveedor: {', '.join(provs)}")
            for p in self._proveedores_disponibles:
                logging.info(f"   📡 {p['nombre']}: {p['modelos'][0]} ({p['descripcion']})")
        else:
            self.endpoint = endpoint
            self.model = model or "google/gemma-4-31b-it:free"
            self.api_key = ""
            logging.warning("⚠️ No hay API keys configuradas en config/config.ini")
            logging.warning("   Agrega al menos una de estas (TODAS son gratis):")
            for prov in self.PROVEEDORES_CONFIG:
                logging.warning(f"   [{prov['config_section']}] api_key = TU_KEY  # {prov['info_key']}")

    def _cargar_api_key(self, section: str) -> Optional[str]:
        """Carga API key desde config.ini para una sección específica"""
        # Primero intentar variable de entorno
        env_var = f"{section.upper()}_API_KEY"
        env_key = os.environ.get(env_var, "").strip()
        if env_key and len(env_key) > 10:
            return env_key

        # Luego config.ini
        try:
            import configparser
            config_path = Path(__file__).parent.parent / "config" / "config.ini"
            if config_path.exists():
                config = configparser.ConfigParser()
                config.read(config_path, encoding='utf-8')
                key = config.get(section, "api_key", fallback="").strip()
                if key and len(key) > 10:
                    return key
        except Exception:
            pass
        return None

    def _cargar_api_key_config(self):
        """Legacy: carga API key de OpenRouter desde config.ini"""
        key = self._cargar_api_key("openrouter")
        if key:
            self.api_key = key

    def _detectar_modelo(self):
        """Compatibilidad: no-op"""
        pass

    # =================================================================
    #  COMPLETAR - Punto de entrada principal
    # =================================================================
    def completar(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        formato_json: bool = False,
        enable_reasoning: bool = False
    ) -> Dict[str, Any]:
        """
        Genera una completación usando proveedores gratuitos con fallback automático.

        Flujo: Gemini → Groq → OpenRouter (si uno se agota, prueba el siguiente)
        """
        if not self._proveedores_disponibles:
            secciones = "\n".join(
                f"  [{p['config_section']}] api_key = TU_KEY  # {p['info_key']}"
                for p in self.PROVEEDORES_CONFIG
            )
            return {
                "exito": False,
                "error": f"No hay proveedores configurados. Agrega al menos una API key en config/config.ini:\n{secciones}",
                "timestamp": datetime.now().isoformat()
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        if self.session_history:
            messages = self.session_history + messages

        # Intentar cada proveedor disponible
        errores_proveedores = []
        for proveedor in self._proveedores_disponibles:
            resultado = self._intentar_proveedor(
                proveedor, messages, temperature, max_tokens, formato_json
            )

            if resultado.get("exito"):
                self.model = resultado.get("modelo", self.model)
                return resultado

            error_msg = resultado.get("error", "Error desconocido")

            if resultado.get("fatal_api"):
                errores_proveedores.append(f"🚫 {proveedor['nombre']}: AGOTADO")
                logging.warning(f"⚠️ {proveedor['nombre']} agotado, probando siguiente proveedor...")
                continue

            # Non-fatal: try next provider too
            errores_proveedores.append(f"❌ {proveedor['nombre']}: {error_msg[:80]}")
            continue

        # Todos los proveedores fallaron
        resumen = "\n".join(errores_proveedores)
        provs_faltantes = [
            p for p in self.PROVEEDORES_CONFIG
            if not any(d["config_section"] == p["config_section"] for d in self._proveedores_disponibles)
        ]
        sugerencia = ""
        if provs_faltantes:
            sugerencia = "\n\nProveedores NO configurados (agrega su API key para más capacidad):\n"
            sugerencia += "\n".join(f"  [{p['config_section']}] → {p['info_key']}" for p in provs_faltantes)

        return {
            "exito": False,
            "fatal_api": True,
            "error": f"Todos los proveedores fallaron:\n{resumen}{sugerencia}",
            "timestamp": datetime.now().isoformat()
        }

    # =================================================================
    #  LÓGICA INTERNA POR PROVEEDOR
    # =================================================================
    def _intentar_proveedor(
        self,
        proveedor: Dict,
        messages: List[Dict],
        temperature: float,
        max_tokens: int,
        formato_json: bool
    ) -> Dict[str, Any]:
        """Intenta completar con un proveedor específico, ciclando entre sus modelos"""
        endpoint = proveedor["endpoint"]
        api_key = proveedor["api_key"]
        modelos = proveedor["modelos"]
        nombre = proveedor["nombre"]
        headers_extra = proveedor.get("headers_extra", {})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            **headers_extra
        }

        payload = {
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
            "model": modelos[0]
        }

        last_error = None
        model_index = 0
        intentos_modelo = 0
        max_total_attempts = self.max_retries * len(modelos)

        for intento in range(max_total_attempts):
            try:
                # Rate limiting
                with self._request_semaphore:
                    current_time = time.time()
                    time_since_last = current_time - LMStudioClient._last_request_time
                    if time_since_last < self._min_request_interval:
                        time.sleep(self._min_request_interval - time_since_last)
                    LMStudioClient._last_request_time = time.time()

                    logging.info(f"   🔄 [{nombre}] Request ({modelos[model_index]})...")
                    response = requests.post(
                        f"{endpoint}/chat/completions",
                        json=payload,
                        headers=headers,
                        timeout=self.timeout
                    )
                    logging.info(f"   ✅ [{nombre}] Respuesta (status={response.status_code})")

                # ---- HTTP 200: Éxito potencial ----
                if response.status_code == 200:
                    data = response.json()

                    # Error dentro de respuesta 200
                    if "error" in data:
                        error_msg = (
                            data["error"].get("message", str(data["error"]))
                            if isinstance(data["error"], dict)
                            else str(data["error"])
                        )
                        logging.info(f"⚠️ [{nombre}] Error en 200: {error_msg[:200]}")
                        if any(w in error_msg.lower() for w in ["rate", "limit", "capacity"]):
                            if model_index < len(modelos) - 1:
                                model_index += 1
                                payload["model"] = modelos[model_index]
                                continue
                            return {"exito": False, "error": f"[{nombre}] Rate limit en todos los modelos", "todos_modelos_fallaron": True}
                        last_error = {"exito": False, "error": f"[{nombre}] Error del modelo: {error_msg[:300]}"}
                        if model_index < len(modelos) - 1:
                            model_index += 1
                            payload["model"] = modelos[model_index]
                            continue
                        return last_error

                    # Sin choices
                    if "choices" not in data or not data["choices"]:
                        logging.info(f"⚠️ [{nombre}] Respuesta sin 'choices'")
                        last_error = {"exito": False, "error": f"[{nombre}] Respuesta sin choices: {str(data)[:200]}"}
                        if model_index < len(modelos) - 1:
                            model_index += 1
                            payload["model"] = modelos[model_index]
                            continue
                        return last_error

                    # Extraer respuesta
                    message_data = data["choices"][0]["message"]
                    respuesta = message_data.get("content", "")
                    finish_reason = data["choices"][0].get("finish_reason")

                    if not respuesta and "reasoning" in message_data:
                        respuesta = message_data.get("reasoning", "")

                    if finish_reason == "length" and len(respuesta.strip()) < 20 and len(messages[-1]["content"]) > 50:
                        return {
                            "exito": False,
                            "error": f"Modelo alcanzó límite de tokens (max_tokens={max_tokens}). Respuesta incompleta.",
                            "finish_reason": finish_reason,
                            "timestamp": datetime.now().isoformat()
                        }

                    if not respuesta or len(respuesta.strip()) < 2:
                        return {
                            "exito": False,
                            "error": f"Modelo devolvió respuesta vacía (finish_reason={finish_reason}).",
                            "respuesta_cruda": str(data),
                            "timestamp": datetime.now().isoformat()
                        }

                    # Procesar JSON si se pidió
                    tokens = data.get("usage", {})
                    contenido = respuesta
                    if formato_json:
                        try:
                            texto_limpio = respuesta.strip()
                            if texto_limpio.startswith("```"):
                                lineas = texto_limpio.split("\n")
                                lineas = [l for l in lineas if not l.strip().startswith("```")]
                                texto_limpio = "\n".join(lineas)
                            contenido = json.loads(texto_limpio)
                        except json.JSONDecodeError:
                            logging.info("⚠️ Respuesta no es JSON válido, devolviendo texto plano")

                    return {
                        "exito": True,
                        "respuesta": contenido,
                        "tokens_usados": {
                            "prompt": tokens.get("prompt_tokens", 0),
                            "completion": tokens.get("completion_tokens", 0),
                            "total": tokens.get("total_tokens", 0)
                        },
                        "modelo": data.get("model", modelos[model_index]),
                        "proveedor": nombre,
                        "finish_reason": finish_reason,
                        "timestamp": datetime.now().isoformat()
                    }

                # ---- HTTP 429/404/400: Rate limit o modelo no disponible ----
                elif response.status_code in (429, 404, 400):
                    status = response.status_code
                    if model_index < len(modelos) - 1:
                        model_index += 1
                        payload["model"] = modelos[model_index]
                        intentos_modelo = 0
                        reason = "Rate limit" if status == 429 else "Modelo no disponible"
                        logging.info(f"⚠️ [{nombre}] {reason} ({status}), probando: {modelos[model_index]}")
                        time.sleep(1 if status != 429 else 2)
                        continue

                    intentos_modelo += 1
                    if intentos_modelo < self.max_retries:
                        wait_time = (2 ** intentos_modelo) * 3
                        model_index = 0
                        payload["model"] = modelos[0]
                        logging.info(f"⚠️ [{nombre}] Todos con rate limit - Esperando {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    return {
                        "exito": False,
                        "error": f"[{nombre}] Todos los modelos agotados (HTTP {status})",
                        "todos_modelos_fallaron": True,
                        "timestamp": datetime.now().isoformat()
                    }

                # ---- HTTP 402: Límite de gasto FATAL ----
                elif response.status_code == 402:
                    error_text = response.text[:500]
                    logging.error(f"\n🚫 [{nombre}] LÍMITE DE GASTO AGOTADO (HTTP 402)")
                    logging.error(f"   Detalle: {error_text[:200]}")
                    return {
                        "exito": False,
                        "error": f"{nombre}: Límite de gasto agotado",
                        "fatal_api": True,
                        "timestamp": datetime.now().isoformat()
                    }

                # ---- HTTP 413: Request demasiado grande - pasar a siguiente proveedor ----
                elif response.status_code == 413:
                    logging.warning(f"⚠️ [{nombre}] Prompt demasiado grande (HTTP 413)")
                    return {
                        "exito": False,
                        "error": f"[{nombre}] HTTP 413: Prompt demasiado grande para {modelos[model_index]}",
                        "timestamp": datetime.now().isoformat()
                    }

                # ---- Otros errores HTTP ----
                else:
                    last_error = {
                        "exito": False,
                        "error": f"[{nombre}] HTTP {response.status_code}: {response.text[:500]}",
                        "timestamp": datetime.now().isoformat()
                    }
                    if response.status_code >= 500 and intento < self.max_retries - 1:
                        wait_time = (2 ** intento) * 0.5
                        logging.info(f"⚠️ [{nombre}] Error servidor - Reintentando en {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    return last_error

            except requests.exceptions.Timeout:
                last_error = {
                    "exito": False,
                    "error": f"[{nombre}] Timeout después de {self.timeout}s",
                    "timestamp": datetime.now().isoformat()
                }
                if intento < self.max_retries - 1:
                    logging.info(f"⚠️ [{nombre}] Timeout - Reintentando...")
                    time.sleep(1)
                    continue
                return last_error

            except requests.exceptions.ConnectionError as e:
                return {
                    "exito": False,
                    "error": f"[{nombre}] No se puede conectar: {str(e)[:200]}",
                    "timestamp": datetime.now().isoformat()
                }

            except Exception as e:
                last_error = {
                    "exito": False,
                    "error": f"[{nombre}] Error: {type(e).__name__}: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                if intento < self.max_retries - 1:
                    logging.info(f"⚠️ [{nombre}] Error inesperado - Reintentando...")
                    time.sleep(1)
                    continue
                return last_error

        return last_error or {
            "exito": False,
            "error": f"[{nombre}] Todos los reintentos fallaron",
            "todos_modelos_fallaron": True,
            "timestamp": datetime.now().isoformat()
        }

    # =================================================================
    #  MÉTODOS DE VALIDACIÓN (sin cambios)
    # =================================================================
    def validar_campo_medico(
        self,
        campo: str,
        valor_extraido: str,
        texto_original: str,
        contexto: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Valida un campo médico usando el LLM"""
        system_prompt = """Eres un asistente médico experto en validación de datos de informes de inmunohistoquímica (IHQ).

Tu tarea es validar si un campo extraído automáticamente es correcto según el texto original del informe médico.

Debes responder ÚNICAMENTE en formato JSON con esta estructura:
{
  "campo_correcto": true/false,
  "confianza": 0.0-1.0,
  "valor_sugerido": "valor corregido" o null,
  "razonamiento": "explicación breve",
  "ubicacion_en_texto": "fragmento donde encontraste la info"
}"""

        contexto_str = ""
        if contexto:
            contexto_str = f"\n\nOtros campos extraídos (para contexto):\n{json.dumps(contexto, ensure_ascii=False, indent=2)}"

        prompt = f"""CAMPO A VALIDAR: {campo}
VALOR EXTRAÍDO: {valor_extraido}

TEXTO ORIGINAL DEL INFORME:
{texto_original[:3000]}

{contexto_str}

Valida si el valor extraído es correcto y sugiere correcciones si es necesario."""

        resultado = self.completar(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=500,
            formato_json=True
        )

        if resultado["exito"]:
            try:
                if isinstance(resultado["respuesta"], dict):
                    validacion = resultado["respuesta"]
                else:
                    validacion = json.loads(resultado["respuesta"])

                return {
                    "exito": True,
                    "campo": campo,
                    "valor_original": valor_extraido,
                    "validacion": validacion,
                    "tokens_usados": resultado["tokens_usados"]
                }
            except json.JSONDecodeError:
                return {
                    "exito": False,
                    "error": "Respuesta del LLM no es JSON válido",
                    "respuesta_cruda": resultado["respuesta"]
                }
        else:
            return resultado

    def validar_multiple_campos(
        self,
        datos_extraidos: Dict[str, Any],
        texto_original: str,
        campos_a_validar: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Valida múltiples campos en una sola llamada"""
        campos = campos_a_validar or list(datos_extraidos.keys())

        validaciones = {}
        tokens_totales = 0

        for campo in campos:
            if campo not in datos_extraidos:
                continue

            valor = datos_extraidos[campo]

            if not valor or str(valor).strip() in ['', 'N/A', 'None']:
                continue

            contexto = {k: v for k, v in datos_extraidos.items() if k != campo}

            resultado = self.validar_campo_medico(
                campo,
                str(valor),
                texto_original,
                contexto
            )

            validaciones[campo] = resultado

            if resultado.get("exito"):
                tokens_totales += resultado.get("tokens_usados", {}).get("total", 0)

        return {
            "validaciones": validaciones,
            "campos_validados": len(validaciones),
            "tokens_totales": tokens_totales,
            "timestamp": datetime.now().isoformat()
        }

    def sugerir_correcciones_lote(
        self,
        datos_extraidos: Dict[str, Any],
        datos_bd: Dict[str, Any],
        texto_original: str
    ) -> Dict[str, Any]:
        """Sugiere correcciones comparando extracción vs BD"""
        system_prompt = """Eres un experto en validación de datos médicos de informes IHQ.

Compara los datos extraídos automáticamente con los datos guardados en la base de datos.
Identifica discrepancias y sugiere correcciones basándote en el texto original del informe.

Responde ÚNICAMENTE en formato JSON:
{
  "correcciones": [
    {
      "campo": "nombre_campo",
      "valor_extraido": "valor",
      "valor_bd": "valor",
      "valor_sugerido": "valor_correcto",
      "confianza": 0.0-1.0,
      "razon": "explicación",
      "ubicacion_texto": "fragmento relevante"
    }
  ],
  "resumen": {
    "total_discrepancias": 0,
    "correcciones_criticas": 0,
    "correcciones_opcionales": 0
  }
}"""

        prompt = f"""DATOS EXTRAÍDOS:
{json.dumps(datos_extraidos, ensure_ascii=False, indent=2)}

DATOS EN BASE DE DATOS:
{json.dumps(datos_bd, ensure_ascii=False, indent=2)}

TEXTO ORIGINAL DEL INFORME:
{texto_original[:4000]}

Identifica discrepancias y sugiere correcciones."""

        resultado = self.completar(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=2000,
            formato_json=True
        )

        return resultado

    def extraer_campo_con_llm(
        self,
        campo: str,
        descripcion_campo: str,
        texto_original: str,
        ejemplos: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extrae un campo específico usando el LLM (fallback cuando regex falla)"""
        system_prompt = """Eres un experto en extracción de datos de informes médicos de inmunohistoquímica.

Extrae ÚNICAMENTE el valor solicitado del texto.
Responde en formato JSON:
{
  "valor": "valor_extraido" o null,
  "confianza": 0.0-1.0,
  "ubicacion": "fragmento donde encontraste el valor"
}"""

        ejemplos_str = ""
        if ejemplos:
            ejemplos_str = f"\n\nEJEMPLOS DE VALORES VÁLIDOS:\n" + "\n".join(f"- {ej}" for ej in ejemplos)

        prompt = f"""CAMPO A EXTRAER: {campo}
DESCRIPCIÓN: {descripcion_campo}{ejemplos_str}

TEXTO DEL INFORME:
{texto_original[:3000]}

Extrae el valor del campo solicitado."""

        resultado = self.completar(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.1,
            max_tokens=300,
            formato_json=True
        )

        return resultado

    def guardar_sesion(self, filepath: Path):
        """Guarda el historial de la sesión en JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "endpoint": self.endpoint,
                "model": self.model,
                "historial": self.session_history,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

    def limpiar_historial(self):
        """Limpia el historial de la sesión"""
        self.session_history = []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.info("🤖 CLIENTE LLM Multi-Proveedor v4.0")
    logging.info("=" * 60)

    client = LMStudioClient()

    if not client._proveedores_disponibles:
        logging.info("\n❌ No hay proveedores configurados.")
        logging.info("   Edita config/config.ini y agrega al menos una API key:")
        for prov in LMStudioClient.PROVEEDORES_CONFIG:
            logging.info(f"   [{prov['config_section']}] api_key = TU_KEY")
            logging.info(f"     {prov['info_key']}")
    else:
        logging.info(f"\n📡 Proveedores disponibles: {len(client._proveedores_disponibles)}")
        for p in client._proveedores_disponibles:
            logging.info(f"   ✅ {p['nombre']} ({len(p['modelos'])} modelos)")

        logging.info("\n📝 Probando completación...")
        resultado = client.completar(
            "Responde solo 'OK' si recibes este mensaje.",
            temperature=0.1,
            max_tokens=50
        )

        if resultado["exito"]:
            logging.info(f"✅ Respuesta: {resultado['respuesta']}")
            logging.info(f"   Proveedor: {resultado.get('proveedor', '?')}")
            logging.info(f"   Modelo: {resultado.get('modelo', '?')}")
        else:
            logging.info(f"❌ Error: {resultado['error']}")
