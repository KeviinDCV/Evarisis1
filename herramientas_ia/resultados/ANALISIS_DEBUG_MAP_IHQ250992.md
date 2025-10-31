# 📊 ANÁLISIS COMPLETO DEBUG_MAP - Caso IHQ250992

**Fecha:** 29 de octubre de 2025
**Caso:** IHQ250992 (MARIELA FERNANDEZ - MÉDULA ÓSEA)
**Objetivo:** Entender estructura del debug_map y definir nueva estrategia de auditoría

---

## 🎯 CONCLUSIÓN EJECUTIVA

**El debug_map contiene TODA la información necesaria para auditoría:**

✅ **OCR completo** (`ocr.texto_consolidado` - 3,529 caracteres procesables)
✅ **Datos extraídos** por unified_extractor (`extraccion.unified_extractor`)
✅ **Datos guardados** en BD (`base_datos.datos_guardados`)
✅ **Metadata** del caso (número, página, total casos)

**Auditor NO necesita:**
❌ Consultar BD directamente (todo está en `datos_guardados`)
❌ Hacer OCR del PDF (texto_consolidado ya está procesado)
❌ Leer `texto_original` (50+ páginas, 193,865 caracteres)

**Auditor DEBE:**
✅ Comparar `datos_guardados` (BD) vs `texto_consolidado` (OCR)
✅ Validar independientemente extrayendo campos del OCR
✅ Detectar discrepancias entre extracción y fuente de verdad

---

## 📋 ESTRUCTURA DEL DEBUG_MAP

### Secciones Principales

```json
{
  "session_id": "IHQ250992_20251029_091949",
  "numero_peticion": "IHQ250992",
  "timestamp": "2025-10-29T09:19:49.285590",
  "pdf_path": "...",

  "ocr": {
    "texto_original": "[193,865 caracteres - OMITIR]",
    "texto_consolidado": "[3,529 caracteres - USAR ESTE]",
    "metadata": {...},
    "hash_original": "..."
  },

  "extraccion": {
    "unified_extractor": {
      // 55 campos extraídos
    }
  },

  "base_datos": {
    "datos_guardados": {
      // 120 campos guardados en BD
    },
    "campos_criticos": {
      // 5 campos críticos identificados
    },
    "columnas_mapeadas": {}
  },

  "validacion": {...},
  "correcciones_aplicadas": [...],
  "metadata": {...},
  "metricas": {...}
}
```

### Campos Disponibles por Sección

#### `ocr.texto_consolidado` (3,529 caracteres)
- ✅ Texto completo del PDF procesado
- ✅ Incluye DESCRIPCIÓN MACROSCÓPICA
- ✅ Incluye DESCRIPCIÓN MICROSCÓPICA
- ✅ Incluye DIAGNÓSTICO
- ✅ Incluye estudios solicitados ("se realiza marcación para...")

#### `extraccion.unified_extractor` (55 campos)
- `diagnostico` ✅
- `descripcion_macroscopica` ✅
- `descripcion_microscopica` ✅
- `factor_pronostico` ✅
- `estudios_solicitados_tabla` ❌ (vacío)
- `IHQ_CD5` ✅
- `IHQ_ORGANO` ✅
- ... (resto de biomarcadores vacíos)

#### `base_datos.datos_guardados` (120 campos)
- `Diagnostico Principal` → "N/A" ❌
- `Diagnostico Coloracion` → "NO APLICA" ❌
- `Factor pronostico` → "NO APLICA" ✅
- `IHQ_ESTUDIOS_SOLICITADOS` → "CD5" ❌
- `IHQ_CD5` → "6" ✅
- ... (resto de columnas IHQ_* vacías)

---

## 🔍 HALLAZGOS CRÍTICOS - Caso IHQ250992

### 1. DIAGNOSTICO_PRINCIPAL - Error de Mapeo

| Fuente | Valor |
|--------|-------|
| **OCR** | "M�dula �sea. Biopsia. Estudios de inmunohistoqu�mica. LOS HALLAZGOS MORFOL�GICOS Y DE INMUNOHISTOQU�MICA SON COMPATIBLES CON NEOPLASIA DE C�LULAS PLASM�TICAS CON RESTRICCI�N DE CADENAS LIVIANAS KAPPA." |
| **unified_extractor** | `diagnostico`: "M�dula �sea. Biopsia..." ✅ |
| **BD** | `Diagnostico Principal`: "N/A" ❌ |

**Problema:** Unified_extractor extrajo correctamente en campo `diagnostico`, pero BD lo guardó como "N/A".

**Causa raíz:** Posible mapeo incorrecto entre `diagnostico` → `Diagnostico Principal` en el proceso de guardado.

---

### 2. DIAGNOSTICO_COLORACION - No Extraído

| Fuente | Valor |
|--------|-------|
| **OCR** | "MUESTRA SUB�PTIMA PARA DIAGN�STICO (ESCASA Y FRAGMENTADA). CELULARIDAD GLOBAL DEL 30%. RELACI�N MIELOIDE ERITROIDE DE 3:1. MADURACI�N NORMAL DE LA L�NEA MIELOIDE. SIN EVIDENCIA MORFOL�GICA DE INCREMENTO DE BLASTOS." |
| **unified_extractor** | (No extrae este campo) ❌ |
| **BD** | `Diagnostico Coloracion`: "NO APLICA" ❌ |

**Problema:** Unified_extractor NO extrae `DIAGNOSTICO_COLORACION`, y BD lo marca como "NO APLICA" cuando SÍ existe en el OCR.

**Patrón en OCR:**
```
Se realizan niveles al bloque M2510141 el cual corresponde a "biopsia de hueso" con diagn�stico de
"MUESTRA SUB�PTIMA PARA DIAGN�STICO..."
```

**Causa raíz:**
- medical_extractor.extract_diagnostico_coloracion() no detecta este patrón
- Patrón esperado: texto entre comillas después de "diagnóstico de"

---

### 3. IHQ_ESTUDIOS_SOLICITADOS - Extracción Incompleta

| Fuente | Valor |
|--------|-------|
| **OCR** | "se realiza marcaci�n para CD38, CD138, CD56, CD117, kappa y lambda" |
| **OCR parseado** | CD38, CD138, CD56, CD117, kappa, lambda (6 biomarcadores) |
| **unified_extractor** | `estudios_solicitados_tabla`: "" (vacío) ❌ |
| **BD** | `IHQ_ESTUDIOS_SOLICITADOS`: "CD5" ❌ |

**Problema:**
- Unified_extractor NO extrajo estudios solicitados (`estudios_solicitados_tabla` vacío)
- BD guardó "CD5" (¿de dónde salió?)
- Faltan 5 biomarcadores: CD38, CD138, CD56, CD117, kappa, lambda

**Biomarcadores faltantes:**
- ❌ CD38 (en OCR, no en BD)
- ❌ CD138 (en OCR, no en BD)
- ❌ CD56 (en OCR, no en BD)
- ❌ CD117 (en OCR, no en BD)
- ❌ kappa (en OCR, no en BD)
- ❌ lambda (en OCR, no en BD)
- ✅ CD5 (en BD con valor "6", pero NO en OCR) ← **¿De dónde salió?**

**Causa raíz:**
- Función de extracción de estudios solicitados falló
- CD5 apareció de forma incorrecta (posible confusión con tabla de estudios)

---

### 4. BIOMARCADORES INDIVIDUALES - 5 Faltantes

| Biomarcador | Columna esperada | Valor en BD | Estado |
|-------------|------------------|-------------|--------|
| CD38 | IHQ_CD38 | (vacío) | ❌ NO EXTRAÍDO |
| CD138 | IHQ_CD138 | (vacío) | ❌ NO EXTRAÍDO |
| CD56 | IHQ_CD56 | (vacío) | ❌ NO EXTRAÍDO |
| CD117 | IHQ_CD117 | (vacío) | ❌ NO EXTRAÍDO |
| kappa | IHQ_KAPPA | (vacío) | ❌ NO EXTRAÍDO (columna no existe?) |
| lambda | IHQ_LAMBDA | (vacío) | ❌ NO EXTRAÍDO (columna no existe?) |
| CD5 | IHQ_CD5 | "6" | ✅ EXTRAÍDO (pero no estaba solicitado) |

**Información en descripción microscópica (OCR):**
```
M�dula �sea con presencia de c�lulas plasm�ticas que corresponden alrededor del 20% de la
celularidad, con expresi�n de CD38 y CD138. Presenta expresi�n aberrante para CD56, expresi�n d�bil
para CD117 y con restricci�n de cadenas livianas kappa (lambda negativo).
```

**Resultados esperados:**
- CD38: "POSITIVO" o "expresión positiva"
- CD138: "POSITIVO" o "expresión positiva"
- CD56: "POSITIVO (expresión aberrante)" o "POSITIVO"
- CD117: "POSITIVO (expresión débil)" o "POSITIVO"
- kappa: "POSITIVO (restricción)" o "POSITIVO"
- lambda: "NEGATIVO"

**Causa raíz:**
- Extractores de biomarcadores (biomarker_extractor.py) no detectan estos resultados en descripción microscópica
- Posiblemente solo buscan en secciones específicas o tablas
- Necesitan patrones más flexibles

---

## 🎯 NUEVA ESTRATEGIA DE AUDITORÍA

### Principio Fundamental

```
FUENTE DE VERDAD: ocr.texto_consolidado (debug_map)
DATOS A VALIDAR: base_datos.datos_guardados (debug_map)
MÉTODO: Extracción independiente + comparación
```

### Flujo de Auditoría Corregido

```
1. Leer debug_map
   ├─ ocr.texto_consolidado (fuente de verdad)
   └─ base_datos.datos_guardados (datos a validar)

2. Extraer INDEPENDIENTEMENTE del OCR:
   ├─ DIAGNOSTICO_PRINCIPAL (sección "DIAGN�STICO")
   ├─ DIAGNOSTICO_COLORACION (bloque M + "diagn�stico de")
   ├─ IHQ_ESTUDIOS_SOLICITADOS ("marcaci�n para...")
   └─ BIOMARCADORES individuales (descripción microscópica)

3. Comparar extracción independiente vs datos_guardados:
   ├─ Si coinciden → ✅ OK
   ├─ Si difieren → ❌ ERROR (mostrar ambos valores)
   └─ Si OCR tiene pero BD no → ❌ ERROR (falta extracción)

4. Validar COMPLETITUD:
   ├─ Campos críticos NO deben estar vacíos o "N/A"
   ├─ Biomarcadores solicitados deben tener columnas IHQ_* pobladas
   └─ Factor pronóstico debe ser "NO APLICA" SI no hay HER2/Ki-67/ER/PR

5. Generar reporte con:
   ├─ Valor esperado (del OCR)
   ├─ Valor encontrado (en BD)
   ├─ Discrepancia (si existe)
   └─ Sugerencia de corrección
```

### Funciones Necesarias en Auditor

#### 1. `_extraer_diagnostico_principal_desde_ocr(ocr: str) -> str`
```python
"""
Extrae DIAGNOSTICO_PRINCIPAL directamente del OCR.

Patrón: Sección "DIAGN�STICO" hasta "COMENTARIOS" o final.
Retorna: Texto del diagnóstico sin prefijos.
"""
```

#### 2. `_extraer_diagnostico_coloracion_desde_ocr(ocr: str) -> str`
```python
"""
Extrae DIAGNOSTICO_COLORACION directamente del OCR.

Patrón: bloque M + "diagn�stico de" + texto entre comillas.
Retorna: Diagnóstico del estudio M previo o None.
"""
```

#### 3. `_extraer_estudios_solicitados_desde_ocr(ocr: str) -> List[str]`
```python
"""
Extrae IHQ_ESTUDIOS_SOLICITADOS directamente del OCR.

Patrón: "se realiza marcaci�n para" + lista de biomarcadores.
Retorna: Lista de biomarcadores normalizados.
"""
```

#### 4. `_extraer_resultados_biomarcadores_desde_ocr(ocr: str, biomarcadores: List[str]) -> Dict[str, str]`
```python
"""
Extrae resultados de biomarcadores desde descripción microscópica.

Para cada biomarcador en la lista, busca:
- "expresi�n de X" → POSITIVO
- "X positivo/negativo"
- "restricci�n de X" → POSITIVO

Retorna: Dict {biomarcador: resultado}
"""
```

#### 5. `_validar_campo_critico(nombre: str, valor_bd: str, valor_ocr: str) -> Dict`
```python
"""
Valida un campo crítico comparando BD vs OCR.

Retorna:
{
    'campo': nombre,
    'estado': 'OK' | 'ERROR' | 'WARNING',
    'valor_bd': valor_bd,
    'valor_ocr': valor_ocr,
    'mensaje': '...',
    'sugerencia': '...'
}
"""
```

### Validaciones Específicas

#### DIAGNOSTICO_PRINCIPAL
```python
# Extraer del OCR
diagnostico_ocr = self._extraer_diagnostico_principal_desde_ocr(texto_ocr)
diagnostico_bd = datos_bd.get('Diagnostico Principal', '')

# Validar
PLACEHOLDERS = ['N/A', 'NO APLICA', '', 'SIN DATO', 'PENDIENTE']

if diagnostico_bd.upper() in PLACEHOLDERS:
    if diagnostico_ocr:
        # ERROR: BD vacío pero OCR tiene valor
        return {
            'estado': 'ERROR',
            'mensaje': 'DIAGNOSTICO_PRINCIPAL está vacío/placeholder pero existe en OCR',
            'valor_bd': diagnostico_bd,
            'valor_ocr': diagnostico_ocr[:200],
            'sugerencia': 'Verificar mapeo diagnostico → Diagnostico Principal en database_manager'
        }
    else:
        # WARNING: BD y OCR ambos vacíos
        return {
            'estado': 'WARNING',
            'mensaje': 'DIAGNOSTICO_PRINCIPAL y OCR ambos vacíos (caso sin diagnóstico confirmado?)',
            'valor_bd': diagnostico_bd,
            'valor_ocr': diagnostico_ocr
        }

# Comparar valores normalizados
if self._normalizar(diagnostico_bd) != self._normalizar(diagnostico_ocr):
    return {
        'estado': 'ERROR',
        'mensaje': 'DIAGNOSTICO_PRINCIPAL difiere entre BD y OCR',
        'valor_bd': diagnostico_bd,
        'valor_ocr': diagnostico_ocr[:200],
        'similitud': self._calcular_similitud(diagnostico_bd, diagnostico_ocr)
    }

return {'estado': 'OK', 'mensaje': 'Correcto'}
```

#### DIAGNOSTICO_COLORACION
```python
# Extraer del OCR
diagnostico_coloracion_ocr = self._extraer_diagnostico_coloracion_desde_ocr(texto_ocr)
diagnostico_coloracion_bd = datos_bd.get('Diagnostico Coloracion', '')

# Caso 1: OCR tiene diagnóstico pero BD dice "NO APLICA"
if diagnostico_coloracion_ocr and diagnostico_coloracion_bd in ['NO APLICA', '', 'N/A']:
    return {
        'estado': 'ERROR',
        'mensaje': 'DIAGNOSTICO_COLORACION marcado como "NO APLICA" pero existe en OCR',
        'valor_bd': diagnostico_coloracion_bd,
        'valor_ocr': diagnostico_coloracion_ocr[:200],
        'patron_encontrado': 'bloque M + diagnóstico de "..."',
        'sugerencia': 'Verificar medical_extractor.extract_diagnostico_coloracion()'
    }

# Caso 2: BD tiene diagnóstico pero OCR no
if not diagnostico_coloracion_ocr and diagnostico_coloracion_bd not in ['NO APLICA', '', 'N/A']:
    return {
        'estado': 'WARNING',
        'mensaje': 'DIAGNOSTICO_COLORACION en BD pero no encontrado en OCR (verificar manualmente)',
        'valor_bd': diagnostico_coloracion_bd,
        'valor_ocr': None
    }

# Caso 3: Ambos vacíos → OK
if not diagnostico_coloracion_ocr and diagnostico_coloracion_bd in ['NO APLICA', '', 'N/A']:
    return {'estado': 'OK', 'mensaje': 'No hay estudio M previo'}

# Caso 4: Comparar valores
if self._normalizar(diagnostico_coloracion_bd) != self._normalizar(diagnostico_coloracion_ocr):
    return {
        'estado': 'ERROR',
        'mensaje': 'DIAGNOSTICO_COLORACION difiere entre BD y OCR',
        'valor_bd': diagnostico_coloracion_bd,
        'valor_ocr': diagnostico_coloracion_ocr[:200]
    }

return {'estado': 'OK', 'mensaje': 'Correcto'}
```

#### IHQ_ESTUDIOS_SOLICITADOS
```python
# Extraer del OCR
estudios_ocr = self._extraer_estudios_solicitados_desde_ocr(texto_ocr)
estudios_bd = datos_bd.get('IHQ_ESTUDIOS_SOLICITADOS', '').split(', ')
estudios_bd = [e.strip() for e in estudios_bd if e.strip()]

# Normalizar nombres
estudios_ocr_norm = [self._normalizar_biomarcador(e) for e in estudios_ocr]
estudios_bd_norm = [self._normalizar_biomarcador(e) for e in estudios_bd]

# Comparar
faltantes = [e for e in estudios_ocr if self._normalizar_biomarcador(e) not in estudios_bd_norm]
extras = [e for e in estudios_bd if self._normalizar_biomarcador(e) not in estudios_ocr_norm]

# Validar completitud de columnas IHQ_*
estudios_sin_mapeo = []
for biomarcador in estudios_ocr:
    columna = self._buscar_columna_biomarcador(biomarcador, datos_bd)
    if not columna:
        estudios_sin_mapeo.append(biomarcador)
    else:
        valor = datos_bd.get(columna, '')
        if not valor:
            estudios_sin_mapeo.append(f"{biomarcador} (columna {columna} vacía)")

# Determinar estado
if faltantes or estudios_sin_mapeo:
    return {
        'estado': 'ERROR',
        'mensaje': 'Estudios solicitados incompletos',
        'esperado_ocr': estudios_ocr,
        'en_bd': estudios_bd,
        'faltantes': faltantes,
        'extras': extras,
        'sin_mapeo': estudios_sin_mapeo,
        'cobertura': f"{len(estudios_bd) - len(faltantes)}/{len(estudios_ocr)}"
    }

if extras:
    return {
        'estado': 'WARNING',
        'mensaje': 'Estudios extras en BD no encontrados en OCR',
        'extras': extras
    }

return {'estado': 'OK', 'mensaje': f'Todos los estudios mapeados ({len(estudios_ocr)}/{len(estudios_ocr)})'}
```

---

## 📝 RESUMEN DE MEJORAS NECESARIAS

### Auditor (`auditor_sistema.py`)

1. **Eliminar consultas a BD**
   - ✅ Ya usa `datos_guardados` del debug_map
   - ❌ Todavía valida contra BD en vez de OCR

2. **Agregar funciones de extracción independiente**
   - `_extraer_diagnostico_principal_desde_ocr()`
   - `_extraer_diagnostico_coloracion_desde_ocr()`
   - `_extraer_estudios_solicitados_desde_ocr()`
   - `_extraer_resultados_biomarcadores_desde_ocr()`

3. **Reescribir validaciones**
   - `_validar_diagnostico_principal()` → usar extracción del OCR
   - `_validar_diagnostico_coloracion()` → validar contra OCR
   - `_validar_biomarcadores_completos()` → extraer del OCR + comparar

4. **NO usar `texto_original`**
   - ✅ Usar `texto_consolidado` (3,529 caracteres)
   - ❌ Evitar `texto_original` (193,865 caracteres)

### Extractores (para futuras correcciones)

1. **`medical_extractor.py`**
   - Mejorar `extract_diagnostico_coloracion()` para detectar patrón `bloque M + "diagnóstico de"`
   - Corregir mapeo `diagnostico` → `Diagnostico Principal`

2. **`biomarker_extractor.py`**
   - Agregar extracción desde descripción microscópica
   - Detectar patrones: "expresión de X", "restricción de X", "X positivo/negativo"

3. **`unified_extractor.py`**
   - Corregir extracción de `estudios_solicitados_tabla`
   - Integrar resultados de biomarcadores desde descripción microscópica

---

## ✅ PRÓXIMOS PASOS

1. **Implementar funciones de extracción independiente en auditor**
   - Usar SOLO `texto_consolidado` del debug_map
   - NO consultar BD, NO usar texto_original

2. **Reescribir validaciones para comparar OCR vs BD**
   - Mostrar AMBOS valores en reportes de error
   - Calcular similitud/diferencias

3. **Probar con caso IHQ250992**
   - Debe detectar 4 errores críticos
   - Score esperado: 20% (1/5 validaciones OK)

4. **Validar con otros casos**
   - Verificar que nueva estrategia funciona en casos variados

5. **Documentar comportamiento nuevo del agente**
   - Actualizar `.claude/agents/data-auditor.md`
   - Agregar ejemplos de uso

---

**Archivo:** `herramientas_ia/resultados/ANALISIS_DEBUG_MAP_IHQ250992.md`
**Próximo archivo:** `IMPLEMENTACION_AUDITOR_V3.1.0.md` (plan de corrección)
