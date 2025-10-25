# 🤖 SISTEMA DE VALIDACIÓN Y CORRECCIÓN CON IA

**Versión 1.0.0** - Integración LM Studio para validación inteligente de datos médicos

---

## 📋 Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Flujo de Procesamiento](#flujo-de-procesamiento)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Guía de Uso](#guía-de-uso)
6. [Archivos Generados](#archivos-generados)
7. [Casos de Uso](#casos-de-uso)
8. [Solución de Problemas](#solución-de-problemas)

---

## 🎯 Resumen Ejecutivo

El **Sistema de Validación con IA** agrega una capa inteligente de validación y corrección al procesamiento existente de informes IHQ, usando un modelo LLM local (LM Studio) para:

✅ **Validar automáticamente** datos extraídos vs texto original
✅ **Detectar errores** en la extracción automática (regex)
✅ **Sugerir correcciones** basadas en contexto médico
✅ **Generar mapeos completos** (debug maps) del procesamiento
✅ **Todo en formato JSON** para trazabilidad completa

**PRIVACIDAD**: Modelo LLM corriendo 100% local, sin enviar datos a internet.

---

## 🏗️ Arquitectura del Sistema

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────┐
│                    FLUJO DE PROCESAMIENTO                    │
└─────────────────────────────────────────────────────────────┘

1️⃣ PDF → OCR → Texto consolidado

2️⃣ Texto → Extractores (Regex) → Datos extraídos

3️⃣ Datos → Debug Mapper → debug_map.json ✨ NUEVO

4️⃣ Debug Map → LLM Validator → Validación IA ✨ NUEVO

5️⃣ Validación → Correcciones → Base de Datos

6️⃣ Todo guardado en JSON para revisión manual
```

### Módulos Creados

#### 1. **`detectar_lm_studio.py`** 🔍
- Detecta si LM Studio está corriendo
- Valida conectividad y modelo cargado
- Prueba inferencia básica

**Uso:**
```bash
python herramientas_ia\detectar_lm_studio.py --probar
```

#### 2. **`core/debug_mapper.py`** 🗺️
- Genera mapeo completo del procesamiento
- Registra cada paso (OCR, extractores, BD)
- Exporta todo en JSON estructurado

**Campos capturados:**
- Texto OCR original y consolidado
- Datos de cada extractor (patient, medical, biomarker, unified)
- Datos guardados en BD
- Métricas de rendimiento
- Warnings y errores

#### 3. **`core/llm_client.py`** 🤖
- Cliente para comunicación con LM Studio
- Métodos especializados para validación médica
- Soporte para completaciones y formato JSON

**Métodos principales:**
```python
# Validar un campo específico
validar_campo_medico(campo, valor, texto_original)

# Validar múltiples campos
validar_multiple_campos(datos_extraidos, texto_original)

# Sugerir correcciones en lote
sugerir_correcciones_lote(datos_extraidos, datos_bd, texto)
```

#### 4. **`validador_ia.py`** 🔍
- Orquesta la validación completa
- Compara debug_map vs BD
- Genera reportes de correcciones
- Aplica correcciones automáticamente (opcional)

**Características:**
- Clasificación de correcciones por criticidad (CRITICA, IMPORTANTE, OPCIONAL)
- Cálculo de similitud entre valores
- Dry-run mode para pruebas seguras
- Exportación de reportes JSON

#### 5. **`core/procesamiento_con_ia.py`** 🔄
- Wrapper del procesamiento normal
- Integra debug_mapper y llm_client
- Procesamiento completo con validación IA

---

## 🔄 Flujo de Procesamiento

### Modo 1: Solo Debug (Sin IA)

```bash
# Procesar PDF y generar debug maps
python core\procesamiento_con_ia.py --pdf "pdfs_patologia/ordenamientos.pdf" --debug
```

**Resultado:**
- ✅ Procesamiento normal
- ✅ Debug maps generados en `data/debug_maps/`
- ❌ No valida con IA

### Modo 2: Debug + Validación IA

```bash
# Procesar con validación IA
python core\procesamiento_con_ia.py --pdf "pdfs_patologia/ordenamientos.pdf" --debug --validar-ia
```

**Resultado:**
- ✅ Procesamiento normal
- ✅ Debug maps generados
- ✅ Validación con IA de campos críticos
- ✅ Reportes de discrepancias
- ❌ No aplica correcciones (solo las sugiere)

### Modo 3: Debug + Validación + Correcciones Automáticas

```bash
# Procesar con correcciones automáticas (⚠️ USAR CON PRECAUCIÓN)
python core\procesamiento_con_ia.py --pdf "pdfs_patologia/ordenamientos.pdf" --debug --validar-ia --aplicar-correcciones
```

**Resultado:**
- ✅ Procesamiento normal
- ✅ Debug maps generados
- ✅ Validación con IA
- ✅ **Correcciones aplicadas automáticamente a BD** (solo si confianza > 0.8)

---

## 💻 Instalación y Configuración

### Requisitos Previos

1. **LM Studio instalado y corriendo**
   - Descargar: https://lmstudio.ai/
   - Modelo recomendado: Llama 3 8B, Mistral 7B, o similar
   - Configurar servidor local en puerto 1234

2. **Entorno virtual activado**
   ```bash
   .\venv0\Scripts\activate
   ```

3. **Dependencias instaladas**
   ```bash
   pip install requests  # Si no está ya instalado
   ```

### Configuración LM Studio

1. **Iniciar LM Studio**
2. **Cargar un modelo** (ej: `openai/gpt-oss-20b`)
3. **Iniciar servidor local**:
   - Click en "Local Server" en LM Studio
   - Puerto: 1234 (default)
   - Verificar que esté corriendo

4. **Probar conexión**:
   ```bash
   python herramientas_ia\detectar_lm_studio.py --probar
   ```

   Deberías ver:
   ```
   ✅ LM Studio DETECTADO en http://127.0.0.1:1234
   🧠 Inferencia: FUNCIONANDO
   ```

---

## 📖 Guía de Uso

### Caso de Uso 1: Generar Debug Map de un Caso Existente

Si ya procesaste un PDF y quieres generar el debug map retroactivamente:

```bash
# 1. Consultar caso en BD
python herramientas_ia\consulta_base_datos.py --buscar-peticion IHQ250001

# 2. Analizar PDF original
python herramientas_ia\cli_herramientas.py pdf -f ordenamientos.pdf -i 250001 --completo

# Esto generará el debug map automáticamente
```

### Caso de Uso 2: Validar un Caso con IA

```bash
# Validar caso específico (requiere debug map existente)
python herramientas_ia\validador_ia.py --ihq IHQ250001 --criticos-solo
```

**Salida:**
```
📊 RESUMEN DE VALIDACIÓN
✅ Campos validados: 7
✓ Campos correctos: 5
⚠️ Discrepancias encontradas: 2
🔧 Correcciones sugeridas: 2
  - Críticas: 1
  - Importantes: 1
  - Opcionales: 0
```

### Caso de Uso 3: Procesar PDF Nuevo con IA

```bash
# Procesar PDF completamente nuevo con validación IA
python core\procesamiento_con_ia.py --pdf "pdfs_patologia/nuevo_caso.pdf" --debug --validar-ia
```

### Caso de Uso 4: Aplicar Correcciones Sugeridas

```bash
# Generar validación
python herramientas_ia\validador_ia.py --ihq IHQ250001 > validacion.json

# Revisar manualmente validacion.json

# Aplicar correcciones (dry-run primero)
python herramientas_ia\validador_ia.py --ihq IHQ250001 --aplicar-correcciones --dry-run

# Si todo OK, aplicar de verdad
python herramientas_ia\validador_ia.py --ihq IHQ250001 --aplicar-correcciones
```

---

## 📁 Archivos Generados

### 1. Debug Maps (`data/debug_maps/`)

**Nombre:** `debug_map_IHQ250001_20251005_143022.json`

**Estructura:**
```json
{
  "session_id": "IHQ250001_20251005_143022",
  "numero_peticion": "IHQ250001",
  "timestamp": "2025-10-05T14:30:22",
  "ocr": {
    "texto_original": "...",
    "texto_consolidado": "...",
    "hash_original": "md5hash..."
  },
  "extraccion": {
    "patient_extractor": {...},
    "medical_extractor": {...},
    "biomarker_extractor": {...},
    "unified_extractor": {...}
  },
  "base_datos": {
    "datos_guardados": {...}
  },
  "validacion": {
    "campos_vacios": [...],
    "campos_con_valor": [...],
    "warnings": [...],
    "errores": [...]
  },
  "metricas": {
    "tiempo_ocr_segundos": 2.5,
    "tiempo_extraccion_segundos": 0.8,
    "tiempo_total_segundos": 3.3
  }
}
```

### 2. Validaciones IA (`herramientas_ia/resultados/validaciones_ia/`)

**Nombre:** `validacion_IHQ250001_20251005_143500.json`

**Estructura:**
```json
{
  "numero_peticion": "IHQ250001",
  "resumen": {
    "total_campos_validados": 7,
    "campos_correctos": 5,
    "total_discrepancias": 2,
    "correcciones_criticas": 1
  },
  "discrepancias": [
    {
      "campo": "edad",
      "valor_extraido": "54 años 3 meses",
      "valor_bd": "54 años 3 meses",
      "valor_sugerido_ia": "54",
      "confianza_ia": 0.95,
      "razonamiento": "La edad debe ser solo el número de años",
      "ubicacion_texto": "Edad: 54 años"
    }
  ],
  "correcciones_sugeridas": {
    "criticas": [...],
    "importantes": [...],
    "opcionales": [...]
  }
}
```

### 3. Logs de Correcciones (`herramientas_ia/resultados/validaciones_ia/`)

**Nombre:** `correcciones_aplicadas_IHQ250001_20251005_144000.json`

**Generado cuando se aplican correcciones.**

---

## 🎯 Casos de Uso Comunes

### 1. Verificar Calidad de Extracción

```bash
# 1. Procesar con debug
python core\procesamiento_con_ia.py --pdf caso.pdf --debug

# 2. Validar con IA
python herramientas_ia\validador_ia.py --ihq IHQ250001

# 3. Revisar JSON de validación
code herramientas_ia\resultados\validaciones_ia\validacion_IHQ250001_*.json
```

### 2. Corregir Errores de Extracción

```bash
# Si la IA detecta errores, aplicar correcciones:
python herramientas_ia\validador_ia.py --ihq IHQ250001 --aplicar-correcciones
```

### 3. Auditoría de Procesamiento

```bash
# Comparar debug map con BD para auditoría
python herramientas_ia\validador_ia.py --ihq IHQ250001 --criticos-solo --json auditoria.json
```

---

## 🐛 Solución de Problemas

### Problema 1: LM Studio no detectado

**Síntoma:**
```
❌ LM STUDIO NO DETECTADO
```

**Solución:**
1. Verificar que LM Studio esté corriendo
2. Verificar que el servidor local esté activo (puerto 1234)
3. Cargar un modelo en LM Studio
4. Probar manualmente: `curl http://127.0.0.1:1234/v1/models`

### Problema 2: Debug map no encontrado

**Síntoma:**
```
No se encontró debug map para IHQ250001
```

**Solución:**
1. Procesar el PDF primero con `--debug`:
   ```bash
   python core\procesamiento_con_ia.py --pdf caso.pdf --debug
   ```

2. Verificar que se generó en `data/debug_maps/`

### Problema 3: Validación IA muy lenta

**Síntoma:**
Validación toma más de 30 segundos por caso

**Solución:**
1. Usar `--criticos-solo` para validar solo campos importantes
2. Verificar que LM Studio tenga suficiente RAM/GPU
3. Considerar modelo más pequeño (7B en vez de 13B)

### Problema 4: Correcciones incorrectas

**Síntoma:**
La IA sugiere correcciones que no son correctas

**Solución:**
1. Usar `--dry-run` siempre primero
2. Revisar manualmente el JSON de validación
3. Solo aplicar correcciones con `confianza >= 0.9`
4. Considerar ajustar el prompt del sistema en `llm_client.py`

---

## 📊 Métricas y Rendimiento

### Tiempos Esperados

- **Detección LM Studio**: < 1 segundo
- **Generación Debug Map**: < 0.1 segundos (overhead mínimo)
- **Validación IA (1 campo)**: 2-5 segundos
- **Validación IA (7 campos críticos)**: 10-30 segundos
- **Procesamiento completo con IA**: +30-60 segundos vs normal

### Tokens Usados (LLM)

- **Validación 1 campo**: ~300-500 tokens
- **Validación 7 campos críticos**: ~2000-3000 tokens
- **Validación completa (30+ campos)**: ~8000-12000 tokens

---

## 🚀 Próximos Pasos Recomendados

1. ✅ **Probar con casos reales**
   - Procesar 5-10 PDFs con `--debug --validar-ia`
   - Revisar precisión de correcciones sugeridas

2. ✅ **Ajustar prompts**
   - Mejorar system prompts en `llm_client.py`
   - Agregar ejemplos médicos específicos

3. ✅ **Automatizar flujo**
   - Crear script batch para procesar todos los PDFs pendientes
   - Generar reporte consolidado de calidad

4. ✅ **Dashboard de validación**
   - Visualizar correcciones sugeridas en UI
   - Permitir aprobar/rechazar correcciones desde interfaz

---

## 📞 Soporte

Para problemas o sugerencias:
- **GitHub Issues**: https://github.com/anthropics/claude-code/issues
- **Documentación**: `herramientas_ia/GUIA_TECNICA_COMPLETA.md`

---

*EVARISIS Gestor H.U.V - Sistema de Validación con IA v1.0.0*
*Hospital Universitario del Valle*
*Octubre 2025*
