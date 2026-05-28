#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 CLIENTE LLM - Local-First (Ollama / LM Studio) + Cloud Fallback
==================================================================

Prioridad de proveedores (configurable via [llm].provider en config.ini):
  1. Ollama LOCAL      (datos NUNCA salen del PC - HIPAA/Ley 1581 safe) [puerto 11434]
  2. LM Studio LOCAL   (datos NUNCA salen del PC - HIPAA/Ley 1581 safe) [puerto 1234]
  3. Google Gemini     (solo si los locales no disponibles)
  4. Groq              (fallback cloud)
  5. OpenRouter        (último recurso cloud)

⚠️ DATOS MÉDICOS CONFIDENCIALES: Se recomienda usar SOLO proveedores locales
   (Ollama o LM Studio). Los proveedores cloud están deshabilitados por defecto.
   Para habilitarlos, agregue api_key en config/config.ini.

VERSION 5.0.0 - Local-First (10 Abr 2026):
- LM Studio como proveedor prioritario (datos locales)
- Cloud providers deshabilitados por defecto para protección HC
- 32GB RAM soporta modelos 7B-13B cómodamente

V6.9.6 - Ollama support (13 May 2026):
- Soporte para Ollama (endpoint OpenAI-compatible en localhost:11434)
- Sección [llm] en config.ini: provider = ollama | lm_studio | both
- Selección de modelo y endpoint configurables sin tocar código
- Clase LMStudioClient conservada (compat con ui.py y resto del pipeline)

V6.9.7 - Fix Ollama provider not detected (13 May 2026):
- FIX: _verificar_servidor_local timeout 3s → 10s con 2 reintentos.
  Ollama responde a /v1/models en ~2.0s en idle pero supera 3s bajo
  carga (modelo 27B procesando). Falso negativo dejaba _proveedores_
  disponibles vacío y completar() devolvía "No hay proveedores
  configurados" para los 51 chunks subsiguientes en ui.py worker IA.
- FIX: Fallback "trust-the-config" cuando [llm].provider y [llm].modelo
  están explícitamente configurados, se registra el proveedor aunque
  el sondeo inicial falle (la petición real fallará limpiamente si
  el servidor sí está caído, en vez de fallar en bloque al constructor).

Autor: Sistema EVARISIS
Versión: 6.9.7
Fecha: 13 de mayo de 2026
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


def _extraer_json_robusto(texto: str) -> Optional[Union[Dict, List]]:
    """
    Extrae JSON de una respuesta LLM tolerando:
    - Bloques de razonamiento <think>...</think> (Qwen3, DeepSeek, etc.)
    - Prefacios "Thinking Process:", "Reasoning:", etc.
    - Code fences ```json ... ```
    - Texto libre alrededor del JSON

    Devuelve el objeto parseado o None si no se pudo extraer.
    """
    import re as _re

    if not texto or not isinstance(texto, str):
        return None

    t = texto.strip()

    # 1) Eliminar bloques <think>...</think> (Qwen3 reasoning)
    t = _re.sub(r'<think>.*?</think>', '', t, flags=_re.DOTALL | _re.IGNORECASE).strip()
    # También si quedó <think> sin cierre, descartar hasta el final del bloque
    t = _re.sub(r'<think>.*', '', t, flags=_re.DOTALL | _re.IGNORECASE).strip()

    # 2) Intentar bloque fenced ```json ... ``` o ``` ... ```
    m = _re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', t, _re.DOTALL)
    candidatos: List[str] = []
    if m:
        candidatos.append(m.group(1))

    # 3) Parse directo
    candidatos.append(t)

    # 4) Primer objeto/array balanceado
    for abre, cierra in (('{', '}'), ('[', ']')):
        idx = t.find(abre)
        while idx != -1:
            depth = 0
            in_str = False
            esc = False
            for i in range(idx, len(t)):
                ch = t[i]
                if in_str:
                    if esc:
                        esc = False
                    elif ch == '\\':
                        esc = True
                    elif ch == '"':
                        in_str = False
                    continue
                if ch == '"':
                    in_str = True
                elif ch == abre:
                    depth += 1
                elif ch == cierra:
                    depth -= 1
                    if depth == 0:
                        candidatos.append(t[idx:i + 1])
                        break
            idx = t.find(abre, idx + 1)
            if len(candidatos) > 20:
                break

    for c in candidatos:
        c = c.strip()
        if not c:
            continue
        try:
            return json.loads(c)
        except (json.JSONDecodeError, ValueError):
            continue

    return None


# V6.9.15 - Modelos cuya plantilla jinja NO acepta role="system"
# (ej.: Mistral 7B Instruct v0.3, Codestral, algunos Mixtral).
# Para estos modelos el system prompt se fusiona con el primer user message
# como "[INSTRUCCIONES]\n{system}\n\n[CONTENIDO]\n{user}".
_MODELOS_SIN_SYSTEM_ROLE = (
    "mistral",       # mistralai/mistral-7b-instruct-v0.3, mistral-7b-instruct-v0.2, etc.
    "codestral",     # mistralai/codestral-*
    "mixtral",       # algunos mixtral antiguos
    "ministral",     # ministral-* nuevos
)


def _modelo_requiere_merge_system(nombre_modelo: str) -> bool:
    """Devuelve True si el modelo NO acepta role=system y hay que fusionar."""
    if not nombre_modelo:
        return False
    n = nombre_modelo.lower()
    return any(tag in n for tag in _MODELOS_SIN_SYSTEM_ROLE)


def _fusionar_system_en_user(messages: List[Dict]) -> List[Dict]:
    """Fusiona los mensajes role=system con el primer role=user.

    Mistral 7B Instruct v0.3 y otros usan una plantilla jinja que solo
    permite ['user', 'assistant']. Si llega role=system el LM Studio
    retorna HTTP 400 'Only user and assistant roles are supported!'.

    Esta función:
    - Concatena todos los system messages (en orden).
    - Los pega como cabecera del primer user message:
        [INSTRUCCIONES]
        {system_concat}

        [CONTENIDO]
        {user_original}
    - Si no hay user message, crea uno con solo el system concatenado.
    - Conserva el resto de mensajes (assistant, user posteriores) sin tocar.
    """
    if not messages:
        return messages

    system_parts: List[str] = []
    rest: List[Dict] = []
    for m in messages:
        role = m.get("role", "")
        content = m.get("content", "") or ""
        if role == "system":
            if content.strip():
                system_parts.append(content)
        else:
            rest.append(m)

    if not system_parts:
        return messages  # No hay system, nada que fusionar

    system_concat = "\n\n".join(system_parts).strip()

    # Buscar primer user para fusionar
    primer_user_idx = next(
        (i for i, m in enumerate(rest) if m.get("role") == "user"), None
    )

    if primer_user_idx is None:
        # No hay user; convertimos el system en un user con etiqueta
        return [{"role": "user", "content": f"[INSTRUCCIONES]\n{system_concat}"}] + rest

    nuevo_user_content = (
        f"[INSTRUCCIONES]\n{system_concat}\n\n"
        f"[CONTENIDO]\n{rest[primer_user_idx].get('content', '') or ''}"
    )
    rest[primer_user_idx] = {"role": "user", "content": nuevo_user_content}
    return rest


class LMStudioClient:
    """Cliente LLM multi-proveedor (Gemini, Groq, OpenRouter) - todos gratuitos"""

    # Semáforo de clase para limitar concurrencia global
    _request_semaphore = threading.Semaphore(2)
    _last_request_time = 0
    _min_request_interval = 0.5  # 500ms entre peticiones

    # === CONFIGURACIÓN DE PROVEEDORES ===
    # Orden = prioridad de uso. Proveedores LOCALES primero (datos no salen del PC).
    # V6.9.6: Ollama añadido como proveedor local prioritario.
    PROVEEDORES_CONFIG = [
        {
            "nombre": "Ollama (Local)",
            "endpoint": "http://localhost:11434/v1",
            "modelos": [
                "medgemma:27b",
                "llama3.1:8b",
                "qwen2.5:14b",
                "qwen2.5:7b",
                "gemma2:9b",
            ],
            "config_section": "ollama",
            "headers_extra": {},
            "descripcion": "LOCAL (Ollama) - datos nunca salen del PC",
            "info_key": "Descargar: https://ollama.ai  |  Modelo: ollama pull medgemma:27b",
            "es_local": True,
            "tipo_local": "ollama",
        },
        {
            "nombre": "LM Studio (Local)",
            "endpoint": "http://127.0.0.1:1234/v1",
            "modelos": [
                "google/gemma-4-e4b",
                "google/gemma-3n-e4b",
                "google/gemma-3-4b",
                "qwen/qwen3.5-9b",
                "qwen/qwen3-14b",
                "qwen2.5-7b-instruct",
                "nvidia/nemotron-3-nano-4b",
                "openai/gpt-oss-20b",
            ],
            "config_section": "lmstudio",
            "headers_extra": {},
            "descripcion": "LOCAL (LM Studio) - datos nunca salen del PC",
            "info_key": "Descargar: https://lmstudio.ai",
            "es_local": True,
            "tipo_local": "lmstudio",
        },
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
        timeout: int = 300,
        max_retries: int = 2,
        api_key: Optional[str] = None,
        **kwargs
    ):
        self.max_retries = max_retries
        self.session_history = []

        # V6.9.6: Cargar selector de proveedor local desde [llm] en config.ini
        cfg_llm = self._cargar_config_llm()
        self.provider = cfg_llm.get("provider", "both").strip().lower() or "both"
        cfg_base_url = cfg_llm.get("base_url", "").strip()
        cfg_modelo = cfg_llm.get("modelo", "").strip()
        cfg_api_key_ollama = cfg_llm.get("api_key", "ollama").strip() or "ollama"

        # Timeout: honra config.ini si no se pasó explícitamente con kwargs
        try:
            timeout_cfg = int(cfg_llm.get("timeout", "0") or 0)
        except (ValueError, TypeError):
            timeout_cfg = 0
        # Si el usuario pasó timeout != default (300), respetarlo; si no, usar config si existe
        self.timeout = timeout if timeout != 300 else (timeout_cfg if timeout_cfg > 0 else timeout)

        # Tokens y temperatura por defecto desde config (consumidos por completar() si no se sobreescriben)
        try:
            self._default_max_tokens = int(cfg_llm.get("max_tokens", "0") or 0) or None
        except (ValueError, TypeError):
            self._default_max_tokens = None
        try:
            self._default_temperature = float(cfg_llm.get("temperature", "")) if cfg_llm.get("temperature", "").strip() != "" else None
        except (ValueError, TypeError):
            self._default_temperature = None

        # Determinar qué tipos de locales son admisibles según self.provider
        # Acepta valores: 'ollama', 'lm_studio', 'lmstudio', 'both', '' (=both)
        if self.provider in ("ollama",):
            tipos_locales_permitidos = {"ollama"}
        elif self.provider in ("lm_studio", "lmstudio"):
            tipos_locales_permitidos = {"lmstudio"}
        else:
            tipos_locales_permitidos = {"ollama", "lmstudio"}

        # Cargar todos los proveedores que tengan API key configurada (o sean locales)
        self._proveedores_disponibles = []
        for prov_config in self.PROVEEDORES_CONFIG:
            if prov_config.get("es_local"):
                tipo_local = prov_config.get("tipo_local", "lmstudio")
                # Filtrar por provider seleccionado en [llm]
                if tipo_local not in tipos_locales_permitidos:
                    continue

                # Aplicar override de endpoint desde [llm].base_url si fue especificado
                # y coincide con el tipo de proveedor único elegido
                endpoint_local = prov_config["endpoint"]
                if cfg_base_url and len(tipos_locales_permitidos) == 1:
                    endpoint_local = cfg_base_url

                # Verificar si el proveedor local está corriendo
                servidor_ok = self._verificar_servidor_local(endpoint_local, tipo_local)

                # V6.9.7 FIX: Fallback "trust-the-config" cuando el usuario eligió
                # EXPLÍCITAMENTE este proveedor en [llm].provider y configuró un modelo.
                # Si _verificar_servidor_local da un falso negativo (timeout bajo carga,
                # respuesta lenta, etc.) la lógica anterior dejaba _proveedores_disponibles
                # vacía y completar() devolvía "No hay proveedores configurados" para
                # TODOS los chunks subsiguientes — bug crítico V6.9.6 que rompía
                # _process_files_ia_worker. Ahora, si el usuario lo configuró
                # explícitamente, registramos el proveedor y dejamos que la petición
                # real de chat falle limpiamente si el servidor está realmente caído.
                config_explicit = (
                    cfg_modelo
                    and len(tipos_locales_permitidos) == 1
                    and tipo_local in tipos_locales_permitidos
                )

                if servidor_ok or config_explicit:
                    if not servidor_ok and config_explicit:
                        logging.warning(
                            f"   ⚠️ {prov_config['nombre']} no respondió al sondeo /models "
                            f"pero está configurado explícitamente en [llm] con modelo "
                            f"'{cfg_modelo}'. Se intentará usar bajo demanda."
                        )
                    modelos_cargados = (
                        self._obtener_modelos_servidor_local(endpoint_local) if servidor_ok else []
                    )
                    cfg = {
                        **prov_config,
                        "endpoint": endpoint_local,
                        "api_key": cfg_api_key_ollama if tipo_local == "ollama" else "local",
                    }
                    if modelos_cargados:
                        # Si [llm].modelo está especificado y existe en el servidor,
                        # colocarlo PRIMERO (prioridad máxima).
                        if cfg_modelo and cfg_modelo in modelos_cargados:
                            ordenados = [cfg_modelo] + [m for m in modelos_cargados if m != cfg_modelo]
                            cfg["modelos"] = ordenados
                        elif cfg_modelo:
                            # Modelo solicitado no está cargado todavía: agregarlo al principio
                            # (Ollama lo cargará bajo demanda al hacer la primera petición)
                            cfg["modelos"] = [cfg_modelo] + modelos_cargados
                            logging.info(
                                f"   ⚠️ Modelo '{cfg_modelo}' no listado en {prov_config['nombre']}; "
                                f"se intentará bajo demanda."
                            )
                        else:
                            cfg["modelos"] = modelos_cargados
                        logging.info(f"   📦 Modelos disponibles en {prov_config['nombre']}: {cfg['modelos']}")
                    elif cfg_modelo:
                        # Servidor activo pero sin modelos listados; usar el solicitado
                        cfg["modelos"] = [cfg_modelo]
                    self._proveedores_disponibles.append(cfg)
                else:
                    puerto = "11434" if tipo_local == "ollama" else "1234"
                    logging.warning(f"⚠️ {prov_config['nombre']} no detectado en {endpoint_local}")
                    logging.warning(f"   Asegúrate de que el servidor esté corriendo en puerto {puerto}")
                continue
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
        # V6.9.6: exponer también self.base_url y self.modelo (alias semánticos pedidos por el orquestador)
        if self._proveedores_disponibles:
            self.endpoint = self._proveedores_disponibles[0]["endpoint"]
            self.model = self._proveedores_disponibles[0]["modelos"][0]
            self.api_key = self._proveedores_disponibles[0]["api_key"]
            self.base_url = self.endpoint
            self.modelo = self.model
            provs = [p["nombre"] for p in self._proveedores_disponibles]
            logging.info(f"✅ LLM Multi-proveedor [provider={self.provider}]: {', '.join(provs)}")
            for p in self._proveedores_disponibles:
                logging.info(f"   📡 {p['nombre']}: {p['modelos'][0]} ({p['descripcion']})")
        else:
            self.endpoint = endpoint
            self.model = model or "google/gemma-4-31b-it:free"
            self.api_key = ""
            self.base_url = self.endpoint
            self.modelo = self.model
            logging.warning(f"⚠️ No hay proveedores activos (provider={self.provider}) ni API keys en config/config.ini")
            logging.warning("   Asegúrate de tener Ollama o LM Studio corriendo, o agrega una API key:")
            for prov in self.PROVEEDORES_CONFIG:
                logging.warning(f"   [{prov['config_section']}] -> {prov['info_key']}")

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

    def _cargar_config_llm(self) -> Dict[str, str]:
        """
        V6.9.6: Carga la sección [llm] de config.ini.
        Devuelve un dict con: provider, base_url, api_key, modelo, timeout,
        max_tokens, temperature. Si la sección no existe, retorna defaults seguros.
        """
        defaults = {
            "provider": "both",         # ollama | lm_studio | both
            "base_url": "",
            "api_key": "ollama",
            "modelo": "",
            "timeout": "0",
            "max_tokens": "0",
            "temperature": "",
        }
        try:
            import configparser
            config_path = Path(__file__).parent.parent / "config" / "config.ini"
            if not config_path.exists():
                return defaults
            config = configparser.ConfigParser()
            config.read(config_path, encoding="utf-8")
            if not config.has_section("llm"):
                return defaults
            return {
                "provider": config.get("llm", "provider", fallback=defaults["provider"]),
                "base_url": config.get("llm", "base_url", fallback=defaults["base_url"]),
                "api_key": config.get("llm", "api_key", fallback=defaults["api_key"]),
                "modelo": config.get("llm", "modelo", fallback=defaults["modelo"]),
                "timeout": config.get("llm", "timeout", fallback=defaults["timeout"]),
                "max_tokens": config.get("llm", "max_tokens", fallback=defaults["max_tokens"]),
                "temperature": config.get("llm", "temperature", fallback=defaults["temperature"]),
            }
        except Exception as e:
            logging.warning(f"No se pudo leer [llm] de config.ini: {e}")
            return defaults

    # === Detección de servidores locales (Ollama / LM Studio) ===
    # Ambos exponen el endpoint OpenAI-compatible /v1/models y /v1/chat/completions.
    # Por eso, una vez detectados, se tratan de forma idéntica en el pipeline.

    def _verificar_servidor_local(self, endpoint: str, tipo_local: str) -> bool:
        """V6.9.6: Verifica si un servidor LLM local (Ollama o LM Studio) está corriendo.

        V6.9.7 FIX: Timeout subido de 3s → 10s y se reintenta 2 veces. Ollama
        responde a /v1/models en ~2.0s cuando está libre, pero bajo carga
        (modelo de 27B procesando otra petición) puede superar 3s y disparar
        un falso negativo. Tras un falso negativo, _proveedores_disponibles
        quedaba vacío y completar() devolvía "No hay proveedores configurados"
        para los 51 chunks subsiguientes.
        """
        nombre = "Ollama" if tipo_local == "ollama" else "LM Studio"
        last_err = None
        for intento in (1, 2):
            try:
                resp = requests.get(f"{endpoint}/models", timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    modelos = data.get("data", [])
                    if modelos:
                        modelo_id = modelos[0].get("id", "local-model")
                        logging.info(f"✅ {nombre} detectado en {endpoint}: {modelo_id}")
                        return True
                    logging.info(f"✅ {nombre} activo en {endpoint} (sin modelo aún cargado)")
                    return True
                last_err = f"HTTP {resp.status_code}"
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                last_err = type(e).__name__
                if intento == 1:
                    logging.info(f"   ⏳ {nombre} ({endpoint}) lento en intento 1 ({last_err}), reintentando...")
                    time.sleep(0.5)
                    continue
            except Exception as e:
                last_err = str(e)[:120]
                break
        logging.warning(f"⚠️ {nombre} no respondió a /models en {endpoint} ({last_err})")
        return False

    def _obtener_modelos_servidor_local(self, endpoint: str) -> List[str]:
        """V6.9.6: Lista modelos disponibles en un servidor local (Ollama o LM Studio).

        V6.9.7 FIX: Timeout subido de 3s → 10s (mismo motivo que
        _verificar_servidor_local). Si el servidor responde con 200 pero sin
        modelos, no es error; el llamador puede confiar en [llm].modelo
        del config.ini.
        """
        try:
            resp = requests.get(f"{endpoint}/models", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                ids = [m.get("id", "") for m in data.get("data", []) if m.get("id")]
                # Filtrar modelos de embeddings (no sirven para chat)
                ids = [i for i in ids if "embed" not in i.lower()]
                return ids
        except Exception as e:
            logging.warning(f"No se pudieron listar modelos del servidor local: {e}")
        return []

    # Aliases legacy (compat con código que importe estos métodos directamente)
    def _verificar_lmstudio(self, endpoint: str) -> bool:
        """Legacy alias: usa _verificar_servidor_local con tipo lmstudio."""
        return self._verificar_servidor_local(endpoint, "lmstudio")

    def _obtener_modelos_lmstudio(self, endpoint: str) -> List[str]:
        """Legacy alias: usa _obtener_modelos_servidor_local."""
        return self._obtener_modelos_servidor_local(endpoint)

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
        enable_reasoning: bool = False,
        json_schema: Optional[Dict[str, Any]] = None,
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
                proveedor, messages, temperature, max_tokens, formato_json,
                json_schema=json_schema,
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
        formato_json: bool,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Intenta completar con un proveedor específico, ciclando entre sus modelos"""
        endpoint = proveedor["endpoint"]
        api_key = proveedor["api_key"]
        modelos = proveedor["modelos"]
        nombre = proveedor["nombre"]
        headers_extra = proveedor.get("headers_extra", {})

        headers = {
            "Content-Type": "application/json",
            **headers_extra
        }
        # Solo agregar Authorization para providers cloud (no local)
        if not proveedor.get("es_local"):
            headers["Authorization"] = f"Bearer {api_key}"

        # V6.9.15 - Pre-merge proactivo: si el modelo seleccionado pertenece
        # a la familia Mistral/Codestral (jinja template sin role=system),
        # fusionamos los mensajes system+user ANTES de enviar para evitar
        # el HTTP 400 "Only user and assistant roles are supported!".
        if _modelo_requiere_merge_system(modelos[0]):
            mensajes_payload = _fusionar_system_en_user(messages)
            logging.info(
                f"   🔧 [{nombre}] Modelo '{modelos[0]}' sin role=system: "
                f"fusionando {len(messages)}→{len(mensajes_payload)} mensajes"
            )
        else:
            mensajes_payload = messages

        payload = {
            "messages": mensajes_payload,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        # Siempre enviar el modelo explícitamente (incluido LM Studio local)
        payload["model"] = modelos[0]

        # Forzar salida JSON cuando se pida (LM Studio / OpenAI compatible).
        # V6.9.8: si se pasa json_schema explícito (modo strict), se prefiere
        # response_format={"type":"json_schema", "json_schema": {...}}.
        # Ollama y LM Studio soportan ambos formatos (Ollama también acepta
        # `format` nativo en /api/chat, pero acá usamos /v1/chat/completions).
        if json_schema is not None:
            # El esquema viene como {"name": "...", "schema": {...}, "strict": True}
            # o directamente como dict {"type":"object", ...}. Aceptamos ambos.
            if isinstance(json_schema, dict) and "schema" in json_schema:
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": json_schema,
                }
            else:
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "respuesta",
                        "schema": json_schema,
                        "strict": True,
                    },
                }
        elif formato_json:
            payload["response_format"] = {"type": "json_object"}

        # Desactivar "thinking mode" en modelos de razonamiento (Qwen3, etc.)
        # para evitar que emitan el Chain-of-Thought dentro de `content`
        # y rompan el parseo JSON. LM Studio soporta chat_template_kwargs.
        if proveedor.get("es_local"):
            payload["chat_template_kwargs"] = {"enable_thinking": False}

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
                                # V6.9.15 - Re-fusionar messages según el nuevo modelo
                                if _modelo_requiere_merge_system(modelos[model_index]):
                                    payload["messages"] = _fusionar_system_en_user(messages)
                                else:
                                    payload["messages"] = messages
                                continue
                            return {"exito": False, "error": f"[{nombre}] Rate limit en todos los modelos", "todos_modelos_fallaron": True}
                        last_error = {"exito": False, "error": f"[{nombre}] Error del modelo: {error_msg[:300]}"}
                        if model_index < len(modelos) - 1:
                            model_index += 1
                            payload["model"] = modelos[model_index]
                            # V6.9.15 - Re-fusionar messages según el nuevo modelo
                            if _modelo_requiere_merge_system(modelos[model_index]):
                                payload["messages"] = _fusionar_system_en_user(messages)
                            else:
                                payload["messages"] = messages
                            continue
                        return last_error

                    # Sin choices
                    if "choices" not in data or not data["choices"]:
                        logging.info(f"⚠️ [{nombre}] Respuesta sin 'choices'")
                        last_error = {"exito": False, "error": f"[{nombre}] Respuesta sin choices: {str(data)[:200]}"}
                        if model_index < len(modelos) - 1:
                            model_index += 1
                            payload["model"] = modelos[model_index]
                            # V6.9.15 - Re-fusionar messages según el nuevo modelo
                            if _modelo_requiere_merge_system(modelos[model_index]):
                                payload["messages"] = _fusionar_system_en_user(messages)
                            else:
                                payload["messages"] = messages
                            continue
                        return last_error

                    # Extraer respuesta
                    message_data = data["choices"][0]["message"]
                    respuesta = message_data.get("content", "")
                    finish_reason = data["choices"][0].get("finish_reason")

                    if not respuesta and "reasoning_content" in message_data:
                        respuesta = message_data.get("reasoning_content", "")
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
                        contenido = _extraer_json_robusto(respuesta)
                        if contenido is None:
                            logging.info("⚠️ Respuesta no es JSON válido, devolviendo texto plano")
                            contenido = respuesta

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

                    # Capturar el body real del error para diagnóstico
                    try:
                        err_body = response.json()
                        err_text = json.dumps(err_body)[:300]
                    except Exception:
                        err_text = response.text[:300]
                    logging.warning(f"⚠️ [{nombre}] HTTP {status}: {err_text}")

                    # V6.9.15 - 400 por chat template sin role=system
                    # (Mistral 7B Instruct v0.3, Codestral, etc.).
                    # Mensaje típico del jinja: "Only user and assistant roles are supported!"
                    err_lower = err_text.lower()
                    es_error_role_system = (
                        status == 400 and proveedor.get("es_local") and (
                            "only user and assistant" in err_lower
                            or ("system" in err_lower and "role" in err_lower
                                and ("not supported" in err_lower or "are supported" in err_lower))
                            or "jinja template" in err_lower
                        )
                    )
                    if es_error_role_system:
                        # Verificar si ya está fusionado (no quedan role=system en payload)
                        tiene_system = any(
                            m.get("role") == "system" for m in payload.get("messages", [])
                        )
                        if tiene_system:
                            logging.info(
                                f"   🔧 [{nombre}] Chat template rechaza role=system. "
                                f"Fusionando system+user y reintentando..."
                            )
                            payload["messages"] = _fusionar_system_en_user(payload["messages"])
                            continue

                    # 400 en LM Studio: probable incompatibilidad con response_format
                    # o chat_template_kwargs. Reintentar SIN esos parámetros.
                    if (status == 400 and proveedor.get("es_local")
                            and ("response_format" in payload or "chat_template_kwargs" in payload)):
                        logging.info(f"   🔄 [{nombre}] Reintentando sin response_format/chat_template_kwargs...")
                        payload.pop("response_format", None)
                        payload.pop("chat_template_kwargs", None)
                        continue

                    if model_index < len(modelos) - 1:
                        model_index += 1
                        payload["model"] = modelos[model_index]
                        # V6.9.15 - Si el nuevo modelo también requiere merge,
                        # re-fusionar messages originales para él.
                        if _modelo_requiere_merge_system(modelos[model_index]):
                            payload["messages"] = _fusionar_system_en_user(messages)
                        else:
                            # Restaurar mensajes originales (con role=system) para modelos que sí lo soportan
                            payload["messages"] = messages
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
                        # V6.9.15 - Re-fusionar messages según el modelo primario
                        if _modelo_requiere_merge_system(modelos[0]):
                            payload["messages"] = _fusionar_system_en_user(messages)
                        else:
                            payload["messages"] = messages
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
