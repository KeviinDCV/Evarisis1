# DIAGNÓSTICO: PAX8 y TTF1 No Se Extraen del Caso IHQ250983

**Fecha**: 2025-10-24
**Versión Sistema**: v6.0.5
**Caso Afectado**: IHQ250983
**Agente**: core-editor (Claude Code)

---

## PROBLEMA REPORTADO

Usuario reportó que las columnas IHQ_PAX8 e IHQ_TTF1 no existen en la base de datos y por eso no se guardan los valores extraídos.

---

## INVESTIGACIÓN REALIZADA

### 1. Verificación de Schema BD

Ejecutado:
```bash
python herramientas_ia/gestor_base_datos.py --columnas --tabla informes_ihq
```

**RESULTADO:**
- IHQ_PAX8 existe (Columna #74, tipo TEXT)
- IHQ_TTF1 existe (Columna #55, tipo TEXT)

### 2. Verificación de Valores en BD

Ejecutado:
```python
SELECT IHQ_PAX8, IHQ_TTF1 FROM informes_ihq WHERE "Numero de caso" = 'IHQ250983'
```

**RESULTADO:**
- IHQ_PAX8 = "N/A"
- IHQ_TTF1 = "N/A"

### 3. Verificación de Contenido del PDF

Ejecutado:
```bash
python herramientas_ia/auditor_sistema.py IHQ250983 --buscar "PAX8"
python herramientas_ia/auditor_sistema.py IHQ250983 --buscar "TTF1"
```

**RESULTADO:**

**Ocurrencia PAX8:**
```
"inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo y son negativas para GATA3, CDX2, y TTF1"
```

**Ocurrencias TTF1:**
1. "para tinción con GATA3, CDX2, PAX 8, TTF1, P40, S100 y CKAE1AE3"
2. "son negativas para GATA3, CDX2, y TTF1"

---

## DIAGNÓSTICO FINAL

### CAUSA RAÍZ

El problema NO es que las columnas no existan en la base de datos.

**EL PROBLEMA REAL ES:**

El extractor de biomarcadores narrativos (`extract_narrative_biomarkers` en `biomarker_extractor.py`) NO está detectando correctamente la sintaxis compleja del caso IHQ250983:

```
"inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo
y son negativas para GATA3, CDX2, y TTF1"
```

### VALORES ESPERADOS vs REALES

| Biomarcador | Valor Esperado | Valor en BD | Estado |
|-------------|----------------|-------------|---------|
| IHQ_PAX8 | POSITIVO HETEROGÉNEO | N/A | FALLA |
| IHQ_TTF1 | NEGATIVO | N/A | FALLA |
| IHQ_S100 | POSITIVO | ? | ¿OK? |
| IHQ_CKAE1AE3 | POSITIVO | ? | ¿OK? |
| IHQ_P40_ESTADO | POSITIVO HETEROGÉNEO | ? | ¿OK? |
| IHQ_GATA3 | NEGATIVO | ? | ¿OK? |
| IHQ_CDX2 | NEGATIVO | ? | ¿OK? |

---

## ANÁLISIS TÉCNICO

### 1. Mapeo de Biomarcadores

Verificado en `biomarker_extractor.py`:

```python
# Línea 1624-1626
'PAX8': 'PAX8',
'PAX-8': 'PAX8',
'PAX 8': 'PAX8',

# Línea 1577-1578
'TTF1': 'TTF1',
'TTF-1': 'TTF1',
```

**MAPEO CORRECTO: OK**

### 2. Normalización en medical_extractor.py

```python
# Línea 1184-1186
if 'PAX8' in nombre_upper or 'PAX-8' in nombre_upper or 'PAX 8' in nombre_upper:
    return 'IHQ_PAX8'

# Línea 1100
return 'IHQ_TTF1'
```

**NORMALIZACIÓN CORRECTA: OK**

### 3. Columnas en database_manager.py

```python
# Línea 147
"IHQ_PAX8", "IHQ_PAX5", "IHQ_WT1", "IHQ_NAPSIN", "IHQ_P63",

# Línea 142
"IHQ_P53", "IHQ_TTF1", "IHQ_S100", "IHQ_VIMENTINA", "IHQ_CHROMOGRANINA", "IHQ_SYNAPTOPHYSIN", "IHQ_MELAN_A",
```

**SCHEMA BD CORRECTO: OK**

### 4. Extracción Narrativa

El problema está en la función `extract_narrative_biomarkers()` en `biomarker_extractor.py`.

**SINTAXIS PROBLEMÁTICA:**

```
"inmunorreactividad para BIOMARCADOR1, BIOMARCADOR2, BIOMARCADOR3 y BIOMARCADOR4 MODIFICADOR
y son negativas para BIOMARCADOR5, BIOMARCADOR6, y BIOMARCADOR7"
```

**COMPLEJIDAD:**
1. Lista de positivos con modificador al final ("heterogéneo")
2. Conjunción "y" que conecta con lista de negativos
3. Modificador solo aplica a p40, NO a PAX8

**PATRONES ACTUALES** (biomarker_extractor.py línea 1423-1448):

```python
r'(?i)(p16|p40|s100|her2|...|ttf1|...)\s+(positivo|negativo|focal)',
r'(?i)(p16|p40|s100|her2|...|ttf1|...)\s*:\s*(positivo|negativo|focal)',
```

**PROBLEMA:** No capturan listas complejas con modificadores mixtos.

---

## SOLUCIÓN REQUERIDA

### Opción 1: Mejorar Extractor Narrativo (RECOMENDADO)

Modificar `extract_narrative_biomarkers()` para:

1. Detectar patrón: `"para LISTA_BIOMARCADORES y son negativas para LISTA_NEGATIVOS"`
2. Parsear listas con modificadores selectivos
3. Aplicar modificador solo al biomarcador adyacente

**Ejemplo:**
```
"PAX8 y p40 heterogéneo" → PAX8: POSITIVO, P40: POSITIVO HETEROGÉNEO
```

### Opción 2: Usar Corrección IA (COMPLEMENTARIO)

Invocar `lm-studio-connector` para:

1. Corregir valores faltantes usando IA
2. Aplicar solo a IHQ250983 (caso específico)

### Opción 3: Reprocesar con Extractor Mejorado (FINAL)

1. Mejorar extractor (Opción 1)
2. Reprocesar caso IHQ250983
3. Validar con `data-auditor`

---

## PASOS SIGUIENTES RECOMENDADOS

### Paso 1: Analizar Función `extract_narrative_biomarkers()`

```bash
python herramientas_ia/editor_core.py --analizar-arquitectura
```

### Paso 2: Simular Mejora del Patrón

```bash
python herramientas_ia/editor_core.py --editar-extractor narrativo --patron "NUEVO_PATRON" --razon "Capturar listas complejas con modificadores mixtos" --simular
```

### Paso 3: Aplicar Mejora

```bash
python herramientas_ia/editor_core.py --editar-extractor narrativo --patron "NUEVO_PATRON" --razon "Capturar listas complejas"
```

### Paso 4: Reprocesar Caso

```bash
python herramientas_ia/editor_core.py --reprocesar IHQ250983 --validar-antes
```

### Paso 5: Validar Corrección

```bash
python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente
```

---

## IMPACTO ESTIMADO

- **Casos afectados**: ~10-15% (casos con sintaxis narrativa compleja)
- **Biomarcadores afectados**: PAX8, TTF1, otros en listas mixtas
- **Severidad**: MEDIA (los biomarcadores existen pero no se extraen)
- **Prioridad**: ALTA (afecta completitud de datos)

---

## CONCLUSIÓN

Las columnas IHQ_PAX8 e IHQ_TTF1 **YA EXISTEN** en la base de datos.

El problema real es que el **extractor narrativo NO captura correctamente** biomarcadores en listas complejas con modificadores mixtos.

**NO SE REQUIERE MIGRACIÓN DE SCHEMA.**

**SE REQUIERE MEJORA DEL EXTRACTOR NARRATIVO.**

---

**Generado por**: core-editor (Claude Code)
**Herramienta**: Manual (análisis sin ejecución de comandos de edición)
**Próximo agente recomendado**: core-editor (para implementar solución)
