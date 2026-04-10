# 🔍 ANÁLISIS COMPLETO: AUDITOR FUNC-01

## Comando de Entrada
```bash
python herramientas_ia/auditor_sistema.py IHQ250XXX --inteligente
```

O desde el agente `data-auditor`:
```python
auditor.auditar_caso_inteligente('IHQ250XXX')
```

---

## 📊 FLUJO PRINCIPAL: `auditar_caso_inteligente()`

### Línea de ejecución: 2384-2426

```python
def auditar_caso_inteligente(numero_caso, json_export=False, nivel='completo'):
    # PASO 1: Inicializar y leer debug_map
    resultado = _inicializar_auditoria_inteligente(numero_caso, nivel)

    # PASO 2: Auditar unified_extractor (extracción inicial)
    _auditar_unified_extractor(resultado)

    # PASO 3: Auditar datos_guardados (lo crítico)
    _auditar_datos_guardados(resultado)

    # PASO 4: Calcular métricas finales
    _calcular_metricas_finales(resultado)

    # Exportar JSON si se solicita
    if json_export:
        _exportar_json_auditoria(resultado)

    return resultado
```

---

## 🎯 PASO 1: Inicialización (`_inicializar_auditoria_inteligente`)

**Líneas:** 634-699

### ¿Qué hace?
1. **Busca el debug_map** del caso en `data/debug_maps/debug_map_IHQ250XXX_*.json`
2. **Extrae 3 fuentes de datos:**
   - `ocr`: Texto completo extraído del PDF
   - `extraccion`: Datos extraídos por unified_extractor
   - `base_datos`: Datos guardados en la BD (campos_criticos)

### Datos que obtiene:
```python
{
    "numero_caso": "IHQ250XXX",
    "nivel": "completo",
    "debug_map_path": "ruta/al/debug_map.json",
    "_ocr_completo": "texto OCR del PDF...",
    "_datos_extraccion": {...},  # Salida de unified_extractor
    "_datos_bd": {...},          # Campos críticos de BD
    "metadata": {...}            # Info del caso (paciente, órgano, etc.)
}
```

### ⚠️ Fuente de Verdad
**El OCR es la fuente de verdad absoluta.**
- Compara todo contra el texto OCR del PDF
- NO consulta la BD directamente
- NO re-extrae del PDF

---

## 🔬 PASO 2: Auditar Extracción (`_auditar_unified_extractor`)

**Líneas:** 702-774

### ¿Qué valida?

#### 2.1 Descripciones
```python
# Verifica que se extrajeron correctamente:
- Descripcion_macroscopica: Debe contener "Se recibe orden..."
- Descripcion_microscopica: Debe contener "Previa valoración..."
```

**Método:** Busca keywords en el texto extraído vs OCR

#### 2.2 Diagnóstico
```python
# Verifica que el diagnóstico principal se extrajo:
- Debe contener términos médicos válidos
- NO debe estar vacío
- NO debe contener "N/A"
```

#### 2.3 Biomarcadores Detectados
```python
# Cuenta biomarcadores mencionados en el OCR
- Busca patrones: "CD34", "Ki-67", "CK7", etc.
- Cuenta cuántos se mencionan en el texto
```

### Salida:
```python
{
    "auditoria_unified_extractor": {
        "estado": "OK" | "WARNING" | "ERROR",
        "descripciones": {
            "macroscopica": "OK",
            "microscopica": "OK"
        },
        "diagnostico": {"estado": "OK"},
        "biomarcadores_detectados": 5
    }
}
```

---

## ⚡ PASO 3: Auditar Datos Guardados (`_auditar_datos_guardados`)

**Líneas:** 777-844

**Este es el paso MÁS CRÍTICO** - Valida 10 campos clave:

### 3.1 DIAGNOSTICO_COLORACION (Estudio M)
**Función:** `_validar_diagnostico_coloracion()`

**¿Qué valida?**
```python
# ESTRATEGIA 1: Extracción independiente desde OCR
diagnostico_ocr = _extraer_diagnostico_coloracion_desde_ocr(ocr_completo)

# ESTRATEGIA 2: Validación semántica
# Busca keywords: "GRADO NOTTINGHAM", "INVASIÓN LINFOVASCULAR", etc.

# ESTRATEGIA 3: Detectar casos IHQ puros (sin estudio M)
if es_ihq_puro:
    # Debe ser "NO APLICA"
```

**Errores detectados:**
- ✅ "NO APLICA" cuando SÍ hay estudio M
- ✅ Contaminación con diagnóstico IHQ
- ✅ Texto incorrecto capturado

---

### 3.2 DIAGNOSTICO_PRINCIPAL (Resultado IHQ)
**Función:** `_validar_diagnostico_principal()`

**¿Qué valida?**
```python
# REGLA DE ORO: NO debe contener información del estudio M
# Validaciones:
1. Similitud con OCR (>70%)
2. NO contiene keywords del estudio M ("NOTTINGHAM", "INVASIÓN")
3. Está en sección correcta del PDF (después de "DIAGNÓSTICO")
```

**Errores detectados:**
- ✅ Contaminación con diagnóstico de estudio M
- ✅ Valor diferente al del OCR
- ✅ Valor vacío o "N/A"

---

### 3.3 FACTOR_PRONOSTICO
**Función:** `_validar_factor_pronostico()`

**REGLA CRÍTICA:**
```python
# SOLO 4 biomarcadores permitidos:
BIOMARCADORES_FP = ['HER2', 'Ki-67', 'Receptor de Estrógeno', 'Receptor de Progesterona']

# SI el caso NO tiene ninguno de estos 4:
# → FACTOR_PRONOSTICO debe ser "NO APLICA"

# SI el caso tiene alguno:
# → FACTOR_PRONOSTICO debe contener SOLO esos valores
```

**Errores detectados:**
- ✅ Contiene biomarcadores NO permitidos (E-Cadherina, P53, CD10)
- ✅ Dice "NO APLICA" cuando SÍ hay FP
- ✅ Faltan biomarcadores que deberían estar

---

### 3.4 IHQ_ESTUDIOS_SOLICITADOS
**Función:** `_validar_estudios_solicitados()`

**¿Qué valida?**
```python
# Extrae biomarcadores solicitados del OCR usando:
extract_biomarcadores_solicitados_robust(ocr_completo)

# Compara con el valor en BD
# Verifica que la lista sea completa y correcta
```

**Errores detectados:**
- ✅ Faltan biomarcadores
- ✅ Biomarcadores extra/incorrectos
- ✅ Formato incorrecto

---

### 3.5 IHQ_ORGANO
**Función:** `_validar_ihq_organo()`

**¿Qué valida?**
```python
# El campo IHQ_ORGANO debe:
1. Estar limpio (sin códigos de caso, sin "BX DE", etc.)
2. Coincidir con el órgano mencionado en OCR
3. NO estar vacío
```

---

### 3.6 Descripción Macroscópica
**Función:** `_validar_descripcion_macroscopica()`

**¿Qué valida?**
```python
# Compara similitud textual con OCR
similitud = calcular_similitud(desc_bd, ocr_desc_macro)

# Umbrales:
- < 50%: ERROR (texto muy diferente)
- 50-70%: WARNING (puede tener diferencias)
- > 70%: OK
```

---

### 3.7 Descripción Microscópica
**Función:** `_validar_descripcion_microscopica()`

**Similar a macroscópica** - Compara similitud textual.

---

### 3.8 Malignidad
**Función:** `_validar_malignidad()`

**¿Qué valida?**
```python
# Verifica clasificación MALIGNO/BENIGNO/BORDERLINE

# Si BD = "MALIGNO":
# → OCR debe contener: "CARCINOMA", "SARCOMA", "METASTÁSICO", etc.

# Si BD = "BENIGNO":
# → OCR debe contener: "HIPERPLASIA", "ADENOMA", "BENIGNO", etc.
```

---

### 3.9 Biomarcadores (Completitud)
**Función:** `_validar_biomarcadores_completos()`

**¿Qué valida?**
```python
# Para cada biomarcador en IHQ_ESTUDIOS_SOLICITADOS:

# PASO 1: Verificar que existe columna en BD
columna = BIOMARKER_ALIAS_MAP.get(biomarcador)
if not columna:
    # → ERROR: Biomarcador NO MAPEADO

# PASO 2: Verificar que tiene valor
valor_bd = datos_bd.get(columna)
if valor_bd in ['', 'N/A', None]:
    # → WARNING: Biomarcador SIN VALOR

# PASO 3: Validar valor contra OCR
valor_ocr = _extraer_valor_biomarcador_desde_ocr(biomarcador, ocr)
if valor_bd != valor_ocr:
    # → ERROR: Valor INCORRECTO
```

**Métricas calculadas:**
```python
{
    "biomarcadores_solicitados": 5,
    "biomarcadores_mapeados": 4,
    "biomarcadores_con_valor": 3,
    "biomarcadores_incorrectos": 1,
    "cobertura": 80.0  # (4/5)
}
```

---

### 3.10 Campo Organo (Tabla)
**Función:** `_validar_organo()`

**¿Qué valida?**
```python
# Detecta contaminación:
1. Texto duplicado ("BX DE PLEURA + BX DE PLEURA")
2. Códigos de caso (IHQ251014-B)
3. Códigos numéricos (898807)
4. Texto administrativo ("ESTUDIO DE INMUNOHISTOQUIMICA")

# Genera sugerencia de valor limpio
```

---

## 📈 PASO 4: Métricas Finales (`_calcular_metricas_finales`)

**Líneas:** 2274-2362

### Cálculos:

```python
# 1. Contar validaciones
total_validaciones = 10  # (diagnóstico_coloracion, diagnóstico_principal, etc.)
validaciones_ok = sum(1 for v in validaciones if v['estado'] == 'OK')

# 2. Score de validación
score = (validaciones_ok / total_validaciones) * 100

# 3. Estado final
if score == 100:
    estado = "EXCELENTE"
elif score >= 90:
    estado = "BUENO"
elif score >= 70:
    estado = "ACEPTABLE"
elif score >= 50:
    estado = "ADVERTENCIA"
else:
    estado = "INCOMPLETO"

# 4. Resumen
total_warnings = len([v for v in validaciones if v['estado'] == 'WARNING'])
total_errores = len([v for v in validaciones if v['estado'] == 'ERROR'])
```

---

## 📄 Salida Final

### Estructura del Reporte:
```python
{
    "numero_caso": "IHQ250XXX",
    "nivel": "completo",
    "timestamp": "2025-11-17T23:00:00",

    "metadata": {
        "paciente": "...",
        "organo": "...",
        "diagnostico": "..."
    },

    "auditoria_unified_extractor": {
        "estado": "OK",
        "descripciones": {...},
        "diagnostico": {...}
    },

    "validaciones": [
        {
            "campo": "DIAGNOSTICO_COLORACION",
            "estado": "OK" | "WARNING" | "ERROR",
            "mensaje": "...",
            "valor_bd": "...",
            "valor_esperado": "...",
            "sugerencias": [...]
        },
        # ... 9 validaciones más
    ],

    "metricas": {
        "score_validacion": 88.9,
        "estado_final": "BUENO",
        "validaciones_ok": 8,
        "validaciones_total": 10,
        "warnings": 1,
        "errores": 1,

        "biomarcadores": {
            "solicitados": 5,
            "mapeados": 4,
            "con_valor": 3,
            "incorrectos": 1,
            "cobertura": 80.0
        }
    }
}
```

### Archivo JSON generado:
```
herramientas_ia/resultados/auditoria_inteligente_IHQ250XXX.json
```

---

## 🎯 PUNTOS CLAVE PARA "INGENIERO SOLUCIONES"

### 1. **Entrada Única:**
- Solo necesita el número de caso: `IHQ250XXX`
- No necesita parámetros adicionales

### 2. **Fuente de Verdad:**
- **OCR del PDF** es la referencia absoluta
- NO consulta BD directamente
- Lee debug_map que YA tiene OCR + extracción + BD

### 3. **10 Validaciones Críticas:**
```
1. DIAGNOSTICO_COLORACION (estudio M)
2. DIAGNOSTICO_PRINCIPAL (resultado IHQ)
3. FACTOR_PRONOSTICO (solo HER2, Ki-67, ER, PR)
4. IHQ_ESTUDIOS_SOLICITADOS (lista completa)
5. IHQ_ORGANO (limpio)
6. Descripcion_macroscopica (similitud >70%)
7. Descripcion_microscopica (similitud >70%)
8. Malignidad (MALIGNO/BENIGNO/BORDERLINE)
9. Biomarcadores (completitud + valores correctos)
10. Organo (sin duplicación/contaminación)
```

### 4. **Salida Estructurada:**
- Score de 0-100%
- Estado: EXCELENTE/BUENO/ACEPTABLE/ADVERTENCIA/INCOMPLETO
- Lista de errores con causa raíz
- Sugerencias de corrección

### 5. **Independencia:**
- NO modifica BD
- NO modifica archivos
- SOLO lectura y análisis
- Exporta JSON con resultados

### 6. **Límites Conocidos:**
- **Requiere debug_map existente** (caso debe haberse procesado antes)
- Si no hay debug_map → Error
- No puede auditar casos no procesados

### 7. **Tiempo de Ejecución:**
- ~30-60 segundos por caso
- Lee archivos grandes (debug_map puede ser >1MB)
- Hace análisis semántico complejo

---

## 🔧 RECOMENDACIONES PARA "INGENIERO SOLUCIONES"

### Usar FUNC-01 cuando:
✅ Necesites validar si un caso está correctamente procesado
✅ Quieras identificar qué campos tienen problemas
✅ Necesites un diagnóstico completo de errores
✅ Antes de aplicar correcciones automáticas

### NO usar FUNC-01 cuando:
❌ El caso no ha sido procesado (no existe debug_map)
❌ Solo necesitas reprocesar (usa FUNC-06 directamente)
❌ Solo necesitas agregar biomarcador (usa FUNC-03 directamente)

### Flujo Recomendado para "Ingeniero Soluciones":
```
1. Usuario: "Corrige el caso IHQ250XXX"
2. Ingeniero: Ejecuta FUNC-01 (auditar)
3. Ingeniero: Analiza resultado JSON
4. Ingeniero: Identifica acciones necesarias:
   - Si falta biomarcador → FUNC-03
   - Si extractor tiene bug → Modificar extractor + FUNC-06
   - Si datos incorrectos → FUNC-06
5. Ingeniero: Ejecuta acciones
6. Ingeniero: Re-ejecuta FUNC-01 para verificar
```

---

## 📊 EJEMPLO COMPLETO

### Entrada:
```bash
python herramientas_ia/auditor_sistema.py IHQ250003 --inteligente
```

### Proceso:
```
1. Lee debug_map_IHQ250003_*.json
2. Extrae OCR, extracción, BD
3. Valida 10 campos críticos
4. Calcula score: 88.9%
5. Genera reporte JSON
```

### Salida (Consola):
```
================================================================================
AI AUDITORIA INTELIGENTE - CASO IHQ250003
================================================================================

Metadata:
   Caso 3 de 50
   Paciente: NOMBRE APELLIDO
   Organo (tabla): BX DE PLEURA + BX DE PULMON
   IHQ_ORGANO (diagnostico): PLEURA
   Diagnostico: ADENOCARCINOMA METASTÁSICO CON PRIMARIO PULMONAR...

[... validaciones ...]

================================================================================
METRICAS FINALES
================================================================================

Score de validación: 88.9%
Estado: BUENO
Validaciones OK: 8/10
Warnings: 1
Errores: 1

Biomarcadores: 80.0% cobertura (4/5)
```

### Salida (JSON):
```json
{
  "numero_caso": "IHQ250003",
  "metricas": {
    "score_validacion": 88.9,
    "estado_final": "BUENO",
    "errores": 1,
    "warnings": 1
  },
  "validaciones": [...]
}
```

---

**FIN DEL ANÁLISIS**
