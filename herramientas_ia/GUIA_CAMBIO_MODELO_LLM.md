# 🔄 Guía para Cambiar el Modelo LLM

**Proyecto**: EVARISIS Gestor Oncológico HUV  
**Versión**: 4.2.0  
**Fecha**: 10 de octubre de 2025  
**Propósito**: Guía técnica para alternar entre diferentes modelos LLM

---

## 📋 Resumen Ejecutivo

El sistema actualmente usa **LM Studio** con el modelo **GPT-OSS-20B** para auditoría médica. Cambiar a otro modelo es **sencillo** y solo requiere modificar **1-2 archivos** principales.

**Buenas noticias**: La arquitectura está bien diseñada con **separación de responsabilidades**, lo que facilita el cambio de modelo sin afectar el resto del sistema.

---

## 🏗️ Arquitectura de Comunicación con LLM

### Capa 1: Cliente LLM (Comunicación)
**Archivo**: `core/llm_client.py`  
**Responsabilidad**: Comunicación HTTP con el servidor LLM  
**Modificar**: ✅ SÍ (si cambias servidor o API)

### Capa 2: Sistema de Auditoría (Lógica de Negocio)
**Archivo**: `core/auditoria_ia.py`  
**Responsabilidad**: Orquestación de auditoría, aplicación de correcciones  
**Modificar**: ⚠️ RARAMENTE (solo si cambia estructura de respuesta)

### Capa 3: Procesamiento con IA (Integración)
**Archivo**: `core/procesamiento_con_ia.py`  
**Responsabilidad**: Wrapper que integra IA con procesamiento OCR  
**Modificar**: ❌ NO (usa las capas anteriores)

### Capa 4: UI (Interfaz)
**Archivo**: `ui.py`  
**Responsabilidad**: Interfaz gráfica y callbacks  
**Modificar**: ❌ NO (independiente del modelo)

### Capa 5: Prompts (Configuración)
**Archivos**: `core/prompts/*.txt`  
**Responsabilidad**: Instrucciones para el modelo  
**Modificar**: ⚠️ SEGÚN MODELO (ajustar según capacidades)

---

## 🎯 Escenarios de Cambio de Modelo

### Escenario 1: Cambiar modelo en LM Studio (FÁCIL)
**Complejidad**: ⭐ Muy Fácil  
**Archivos a modificar**: 0  
**Tiempo estimado**: 2 minutos

**Pasos**:
1. Abrir LM Studio
2. Ir a "My Models"
3. Seleccionar otro modelo (ej: Llama 3, Mixtral, Qwen)
4. Cargar el modelo
5. ✅ Listo, el sistema lo detectará automáticamente

**Por qué funciona**: `llm_client.py` detecta automáticamente el modelo activo:
```python
def _detectar_modelo(self):
    # Detecta el primer modelo disponible automáticamente
    modelos_disponibles = [m["id"] for m in data["data"]]
    self.model = modelos_disponibles[0]
```

---

### Escenario 2: Usar API externa (OpenAI, Claude, etc.)
**Complejidad**: ⭐⭐⭐ Moderado  
**Archivos a modificar**: 1 principal (`llm_client.py`)  
**Tiempo estimado**: 30-60 minutos

#### Opción A: Modificar `LMStudioClient` existente

**Archivo**: `core/llm_client.py`

**Cambios necesarios**:

1. **Modificar endpoint y autenticación** (líneas 59-76):
```python
def __init__(
    self,
    endpoint: str = "https://api.openai.com/v1",  # ← CAMBIAR
    api_key: str = None,  # ← AGREGAR
    model: str = "gpt-4",  # ← ESPECIFICAR
    timeout: int = 300,
    max_retries: int = 3
):
    self.endpoint = endpoint.rstrip('/')
    self.model = model
    self.api_key = api_key  # ← GUARDAR
    self.timeout = timeout
    self.max_retries = max_retries
    self.session_history = []
```

2. **Agregar headers de autenticación** (líneas 191-196):
```python
headers = {
    "Authorization": f"Bearer {self.api_key}",  # ← AGREGAR
    "Content-Type": "application/json"
}

response = requests.post(
    f"{self.endpoint}/chat/completions",
    json=payload,
    headers=headers,  # ← AGREGAR
    timeout=self.timeout
)
```

3. **Ajustar payload según API** (líneas 158-164):
```python
payload = {
    "messages": messages,
    "temperature": temperature,
    "max_tokens": max_tokens,
    "model": self.model,  # ← Siempre incluir
    # "reasoning_level": reasoning_level,  # ← ELIMINAR (específico de GPT-OSS)
}
```

#### Opción B: Crear cliente específico (RECOMENDADO)

**Crear nuevo archivo**: `core/openai_client.py` o `core/claude_client.py`

**Ventaja**: Mantiene compatibilidad con LM Studio

```python
# core/openai_client.py
from openai import OpenAI

class OpenAIClient:
    """Cliente para API de OpenAI"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def completar(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        formato_json: bool = False,
        enable_reasoning: bool = False
    ) -> Dict[str, Any]:
        """Mantener misma interfaz que LMStudioClient"""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if formato_json else None
            )
            
            return {
                "exito": True,
                "respuesta": response.choices[0].message.content,
                "tokens_usados": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "modelo": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "exito": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

**Modificar**: `core/auditoria_ia.py` (línea 72):
```python
# Opción 1: LM Studio (actual)
from core.llm_client import LMStudioClient as LLMClient

# Opción 2: OpenAI
# from core.openai_client import OpenAIClient as LLMClient

# Opción 3: Claude
# from core.claude_client import ClaudeClient as LLMClient

# Resto del código permanece igual
self.llm_client = LLMClient(...)
```

---

### Escenario 3: Usar Ollama local
**Complejidad**: ⭐⭐ Fácil  
**Archivos a modificar**: 1 (`llm_client.py` o crear `ollama_client.py`)  
**Tiempo estimado**: 15-30 minutos

**Ollama usa la misma API de OpenAI**, solo cambiar endpoint:

```python
# En core/llm_client.py, línea 59
def __init__(
    self,
    endpoint: str = "http://localhost:11434/v1",  # ← Ollama endpoint
    model: str = "llama3",  # ← Modelo en Ollama
    ...
)
```

O crear `core/ollama_client.py`:
```python
from core.llm_client import LMStudioClient

class OllamaClient(LMStudioClient):
    """Cliente para Ollama - Hereda de LMStudioClient"""
    
    def __init__(
        self,
        model: str = "llama3",
        endpoint: str = "http://localhost:11434/v1",
        **kwargs
    ):
        super().__init__(endpoint=endpoint, model=model, **kwargs)
```

---

## 📁 Archivos Clave y Sus Roles

### 1. `core/llm_client.py` ⭐⭐⭐⭐⭐
**Importancia**: CRÍTICO  
**Líneas clave**:
- **59-76**: Inicialización (endpoint, modelo, timeout)
- **83-116**: Detección automática de modelo
- **118-318**: Método `completar()` - NÚCLEO de comunicación
- **191-196**: Request HTTP al servidor

**Modificar para**:
- Cambiar servidor (LM Studio → OpenAI/Claude/Ollama)
- Agregar autenticación (API keys)
- Ajustar formato de payload
- Cambiar timeout

### 2. `core/auditoria_ia.py` ⭐⭐⭐
**Importancia**: ALTA  
**Líneas clave**:
- **59**: Import del cliente LLM
- **72**: Parámetro `llm_endpoint` (default: http://127.0.0.1:1234)
- **85-95**: Inicialización del cliente
- **167-391**: Método `auditar_lote()` - Usa el cliente

**Modificar para**:
- Cambiar endpoint por defecto
- Agregar parámetros de API key
- Ajustar lógica de reintentos

### 3. `core/procesamiento_con_ia.py` ⭐⭐
**Importancia**: MEDIA  
**Líneas clave**:
- **53**: Parámetro `llm_endpoint`
- **72**: Inicialización de `LMStudioClient`

**Modificar para**:
- Pasar parámetros adicionales al cliente
- NO necesita cambios si modificas solo `llm_client.py`

### 4. `core/prompts/*.txt` ⭐⭐⭐
**Importancia**: ALTA (calidad de resultados)  
**Archivos**:
- `system_prompt_completa.txt`: Auditoría completa
- `system_prompt_parcial.txt`: Auditoría parcial (rápida)
- `system_prompt_comun.txt`: Instrucciones comunes

**Modificar para**:
- Ajustar instrucciones según capacidades del modelo
- Remover referencias a "reasoning" si el modelo no lo soporta
- Ajustar nivel de detalle esperado

### 5. `config/config.ini` ⭐
**Importancia**: BAJA  
**No contiene configuración de LLM actualmente**

**Opcional agregar**:
```ini
[LLM]
# Configuración del modelo LLM
PROVIDER = lm_studio  # lm_studio, openai, claude, ollama
ENDPOINT = http://127.0.0.1:1234
MODEL = gpt-oss-20b
API_KEY = 
TIMEOUT = 300
MAX_RETRIES = 3
```

---

## 🔧 Guía Paso a Paso: Cambiar a OpenAI GPT-4

### Paso 1: Instalar dependencia
```bash
pip install openai
```

### Paso 2: Crear cliente OpenAI
**Archivo**: `core/openai_client.py` (nuevo)

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cliente para API de OpenAI"""

import os
from openai import OpenAI
from typing import Dict, Any, Optional
from datetime import datetime

class OpenAIClient:
    """Cliente para comunicación con API de OpenAI"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        timeout: int = 300,
        max_retries: int = 3
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        if not self.api_key:
            raise ValueError("API key requerida. Configura OPENAI_API_KEY")
        
        self.client = OpenAI(api_key=self.api_key, timeout=timeout)
        print(f"✅ Cliente OpenAI inicializado: {model}")
    
    def completar(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        formato_json: bool = False,
        enable_reasoning: bool = False  # Ignorado, mantenido por compatibilidad
    ) -> Dict[str, Any]:
        """
        Genera completación usando GPT
        Interfaz compatible con LMStudioClient
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if formato_json else {"type": "text"}
            )
            
            return {
                "exito": True,
                "respuesta": response.choices[0].message.content,
                "tokens_usados": {
                    "prompt": response.usage.prompt_tokens,
                    "completion": response.usage.completion_tokens,
                    "total": response.usage.total_tokens
                },
                "modelo": response.model,
                "finish_reason": response.choices[0].finish_reason,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "exito": False,
                "error": f"Error OpenAI: {type(e).__name__}: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
```

### Paso 3: Modificar auditoria_ia.py
**Archivo**: `core/auditoria_ia.py`  
**Cambio**: Línea 59

```python
# ANTES:
from core.llm_client import LMStudioClient

# DESPUÉS:
from core.openai_client import OpenAIClient as LMStudioClient
# O bien:
# from core.openai_client import OpenAIClient
# Y cambiar: self.llm_client = OpenAIClient(...)
```

### Paso 4: Configurar API Key
**Opción A**: Variable de entorno
```bash
# Windows
set OPENAI_API_KEY=sk-proj-...

# Linux/Mac
export OPENAI_API_KEY=sk-proj-...
```

**Opción B**: Modificar `auditoria_ia.py` línea 85
```python
self.llm_client = LMStudioClient(
    api_key="sk-proj-...",  # ← AGREGAR
    model="gpt-4",
    timeout=timeout
)
```

### Paso 5: Probar
```bash
cd herramientas_ia
python cli_herramientas.py bd --stats
```

---

## 🧪 Testing de Cambios

### Test 1: Verificar conexión
```bash
cd herramientas_ia
python -c "from core.llm_client import LMStudioClient; client = LMStudioClient(); print(client.model)"
```

### Test 2: Test simple de completación
```python
# test_llm.py
from core.llm_client import LMStudioClient

client = LMStudioClient()
resultado = client.completar("¿Qué es la inmunohistoquímica?", max_tokens=100)

if resultado["exito"]:
    print(f"✅ Funciona: {resultado['respuesta'][:100]}")
else:
    print(f"❌ Error: {resultado['error']}")
```

### Test 3: Test de auditoría completa
```bash
# Con LM Studio corriendo
python cli_herramientas.py validar --ihq 250001 --pdf pdfs_patologia/ordenamientos.pdf
```

---

## 📊 Comparación de Modelos

### LM Studio (Local) - Actual
**Pros**:
- ✅ Gratuito, ilimitado
- ✅ Privacidad total (datos no salen del equipo)
- ✅ Sin latencia de red
- ✅ Sin costos por token

**Contras**:
- ❌ Requiere GPU potente (8GB+ VRAM)
- ❌ Modelos grandes lentos en CPU
- ❌ Mantenimiento manual de modelos

**Mejor para**: Desarrollo, testing, privacidad médica

### OpenAI GPT-4
**Pros**:
- ✅ Máxima calidad de respuestas
- ✅ Sin requisitos de hardware
- ✅ Muy rápido (API optimizada)
- ✅ JSON mode nativo

**Contras**:
- ❌ Costo por uso (~$0.03/1K tokens output)
- ❌ Requiere conexión a internet
- ❌ Datos salen del servidor (compliance)

**Mejor para**: Producción, máxima calidad

### Claude (Anthropic)
**Pros**:
- ✅ Excelente razonamiento médico
- ✅ Contexto largo (200K tokens)
- ✅ Muy bueno con JSON estructurado

**Contras**:
- ❌ Más caro que GPT-4
- ❌ Rate limits estrictos
- ❌ Requiere cuenta Anthropic

**Mejor para**: Casos complejos, contextos largos

### Ollama (Local)
**Pros**:
- ✅ Gratuito, open source
- ✅ Fácil instalación (curl | sh)
- ✅ Compatible con OpenAI API
- ✅ Modelos optimizados

**Contras**:
- ❌ Calidad menor que GPT-4
- ❌ Requiere recursos locales
- ❌ Menos modelos médicos especializados

**Mejor para**: Testing, desarrollo local económico

---

## ⚠️ Consideraciones Importantes

### 1. Privacidad de Datos Médicos
**Si usas APIs externas** (OpenAI, Claude):
- ⚠️ Los datos del paciente **salen del hospital**
- ⚠️ Requiere compliance con HIPAA/regulaciones locales
- ⚠️ Revisar acuerdos de privacidad del proveedor
- ✅ **Anonimizar** datos antes de enviar (remover nombres, IDs)

**Si usas LM Studio/Ollama local**:
- ✅ Datos permanecen en el servidor local
- ✅ Cumplimiento automático con privacidad médica

### 2. Costos
**OpenAI GPT-4** (estimado):
- Input: $0.01 / 1K tokens
- Output: $0.03 / 1K tokens
- **Costo por caso IHQ**: ~$0.05-0.15 (según complejidad)
- **50 casos**: ~$2.50-7.50

**Claude**:
- Más caro (~2x GPT-4)

**LM Studio/Ollama**:
- $0 (solo electricidad)

### 3. Velocidad
**Ranking** (más rápido → más lento):
1. OpenAI GPT-4 Turbo (~2-5s)
2. Claude Sonnet (~3-8s)
3. LM Studio GPU (~10-30s según modelo)
4. Ollama CPU (~20-60s según modelo)
5. LM Studio CPU (~60-180s)

### 4. Calidad Médica
**Ranking** (mejor → peor):
1. GPT-4 + prompts médicos (mejor)
2. Claude Sonnet (excelente razonamiento)
3. GPT-OSS-20B (actual, bueno)
4. Llama 3 70B (bueno)
5. Mixtral 8x7B (aceptable)
6. Llama 3 8B (básico)

---

## 📝 Checklist de Cambio de Modelo

### Antes de cambiar:
- [ ] Backup de base de datos (`data/huv_oncologia_NUEVO.db`)
- [ ] Documentar configuración actual
- [ ] Verificar que modelo nuevo esté disponible
- [ ] Revisar costos si es API externa
- [ ] Verificar compliance de privacidad

### Durante el cambio:
- [ ] Modificar `core/llm_client.py` o crear nuevo cliente
- [ ] Ajustar `core/auditoria_ia.py` si necesario
- [ ] Configurar API keys si aplica
- [ ] Ajustar prompts en `core/prompts/*.txt`
- [ ] Actualizar timeouts según velocidad del modelo

### Después del cambio:
- [ ] Test de conexión básico
- [ ] Test de completación simple
- [ ] Test con caso IHQ real
- [ ] Comparar calidad de resultados
- [ ] Validar tiempos de respuesta
- [ ] Documentar cambios realizados

---

## 🎯 Recomendación Final

### Para Producción:
**Opción 1**: **LM Studio local** (actual)
- ✅ Privacidad garantizada
- ✅ Sin costos recurrentes
- ✅ Ya configurado y funcionando
- ⚠️ Requiere GPU decente

**Opción 2**: **Ollama local** + Llama 3
- ✅ Más fácil de instalar que LM Studio
- ✅ Mismo nivel de privacidad
- ✅ API compatible con OpenAI
- ⚠️ Calidad levemente menor

### Para Testing/Desarrollo:
**OpenAI GPT-4 Turbo**
- ✅ Máxima calidad de validación
- ✅ Muy rápido para iterar
- ✅ Sin setup de hardware
- ⚠️ Costo moderado (~$5/mes testing)

### Para Máxima Calidad (sin importar costo):
**GPT-4o + Claude Sonnet 3.5 (híbrido)**
- Usar GPT-4o para casos estándar
- Usar Claude para casos complejos/largos
- Implementar lógica de selección automática

---

## 📞 Soporte

**Problemas con LM Studio**:
- Verificar que el servidor esté corriendo
- Puerto 1234 debe estar libre
- Modelo debe estar cargado en memoria

**Problemas con OpenAI**:
- Verificar API key válida
- Revisar límites de rate
- Verificar balance de cuenta

**Problemas con Ollama**:
- `ollama serve` debe estar corriendo
- Modelo descargado: `ollama pull llama3`
- Puerto 11434 debe estar libre

---

**Última actualización**: 10 de octubre de 2025  
**Autor**: Documentación Técnica EVARISIS  
**Versión**: 1.0
