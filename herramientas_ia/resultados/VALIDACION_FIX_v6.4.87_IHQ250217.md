# VALIDACIÓN FALLIDA - FIX v6.4.87 IHQ250217

## RESUMEN EJECUTIVO

- **Caso:** IHQ250217
- **Fix aplicado:** v6.4.87 - PAX8 extracción con separador Y case-insensitive
- **Resultado:** ❌ FALLIDO
- **Score final:** 100.0% (falso positivo - caso completo pero biomarcador MAL)
- **Problema crítico:** IHQ_PAX8 = "NO MENCIONADO" (debería ser "NEGATIVO")

---

## EVIDENCIA OCR

```
Son negativas para CK20, CDX2, TTF-1 y PAX-8
                                        ^^^
                            (no se extrae)
```

---

## DIAGNÓSTICO COMPLETO

### PASO 1: Validación del patrón regex v6.4.87

**Ubicación:** `core/extractors/biomarker_extractor.py` líneas 5470-5498

**Patrón:**
```python
negativo_para_pattern = r'(?i)negativ[oa]s?\s+para\s+(?:para\s+)?([A-Za-z0-9\s,.\-/]+?)(?=\s+Linfocitos|\s+células|\s+acompañantes|\.\s|,\s+diagn[oó]stico|$)'
biomarcadores_encontrados = re.split(r'\s+[Yy]\s+|[,]\s*', lista_biomarkers_raw)
```

**Test manual:**
```
Lista detectada: "CK20, CDX2, TTF-1 y PAX-8"
Split: ["CK20", "CDX2", "TTF-1", "PAX-8"]
```

**Resultado:** ✅ PATRÓN FUNCIONA CORRECTAMENTE

---

### PASO 2: Validación de extract_narrative_biomarkers

**Test directo con texto del caso:**

```python
from core.extractors.biomarker_extractor import extract_narrative_biomarkers

text = 'Son negativas para CK20, CDX2, TTF-1 y PAX-8'
result = extract_narrative_biomarkers(text)

# Resultado:
{
    'PAX8': 'NEGATIVO',       # ✅ EXTRAÍDO
    'IHQ_PAX8': 'NEGATIVO',   # ✅ EXTRAÍDO
    'CK20': 'NEGATIVO',
    'CDX2': 'NEGATIVO',
    'TTF1': 'NEGATIVO',
    ...
}
```

**Logs del extractor:**
```
[V6.4.87 negativo/negativas para] Extraído: 'PAX-8' → PAX8 = NEGATIVO
```

**Resultado:** ✅ EXTRACTOR FUNCIONA CORRECTAMENTE

---

### PASO 3: Validación de unified_extractor (PROBLEMA ENCONTRADO)

**Integración en unified_extractor.py:**

```python
# Línea 742: Ejecuta extract_narrative_biomarkers
narrative_biomarkers = extract_narrative_biomarkers(clean_text) or {}

# Línea 873: Mapeo PAX8 → IHQ_PAX8 existe
biomarker_mapping = {
    ...
    'PAX8': 'IHQ_PAX8',  # ✅ MAPEO CORRECTO
    ...
}

# Línea 982-989: Procesa narrative_biomarkers
for biomarker_name, result in narrative_biomarkers.items():
    biomarker_upper = biomarker_name.upper()
    if biomarker_upper in biomarker_mapping:
        # AQUÍ DEBERÍA MAPEAR PAX8 → IHQ_PAX8
        ...
```

**Verificación en debug_map:**

```json
// extraccion.unified_extractor NO contiene PAX8
{
    "IHQ_CK7": "POSITIVO",
    "IHQ_CK20": "NEGATIVO",
    "IHQ_CDX2": "NEGATIVO",
    "IHQ_TTF1": "NEGATIVO",
    // ❌ IHQ_PAX8: FALTA
}

// base_datos.campos_criticos
{
    "IHQ_PAX8": "NO MENCIONADO"  // ❌ VALOR INCORRECTO
}
```

**Resultado:** ❌ UNIFIED_EXTRACTOR NO GUARDA PAX8

---

## CAUSA RAÍZ IDENTIFICADA

### Problema: unified_extractor descarta PAX8 después de extraerlo

**Evidencia:**
1. biomarker_extractor devuelve `PAX8: NEGATIVO` ✅
2. biomarker_mapping tiene `'PAX8': 'IHQ_PAX8'` ✅
3. unified_extractor NO guarda PAX8 en extraccion ❌
4. BD recibe `IHQ_PAX8: NO MENCIONADO` ❌

**Hipótesis principales:**

1. **Problema de mapeo case-sensitive:**
   - `narrative_biomarkers` devuelve `'PAX8'` (uppercase)
   - `biomarker_mapping` tiene `'PAX8'` (uppercase)
   - **DEBERÍA funcionar**, pero hay que verificar línea 984

2. **Problema de sobrescritura:**
   - Otro patrón posterior sobrescribe PAX8
   - unified_extractor tiene prioridades mal configuradas

3. **Problema de filtrado:**
   - Existe un filtro que descarta PAX8 antes de guardar
   - Posiblemente en líneas posteriores a 989

---

## COMPARACIÓN CON OTROS BIOMARCADORES

| Biomarcador | Patrón | Valor esperado | Valor BD | Estado |
|-------------|--------|----------------|----------|--------|
| CK20 | "negativas para CK20..." | NEGATIVO | NEGATIVO | ✅ OK |
| CDX2 | "negativas para... CDX2..." | NEGATIVO | NEGATIVO | ✅ OK |
| TTF1 | "negativas para... TTF-1..." | NEGATIVO | NEGATIVO | ✅ OK |
| PAX8 | "negativas para... y PAX-8" | NEGATIVO | NO MENCIONADO | ❌ ERROR |

**Observación crítica:** PAX8 es el ÚLTIMO biomarcador después de "y". Los 3 anteriores (separados por comas) SÍ se extrajeron correctamente.

---

## SIGUIENTE PASO

### Acción inmediata requerida

1. **Revisar unified_extractor.py líneas 982-989:**
   - Agregar logging para PAX8
   - Verificar por qué no se guarda en la extracción final

2. **Agregar código debug:**
   ```python
   # Después de línea 989
   if 'PAX8' in narrative_biomarkers:
       logger.info(f"🔍 DEBUG PAX8: narrative tiene PAX8 = {narrative_biomarkers['PAX8']}")
       logger.info(f"🔍 DEBUG PAX8: biomarker_mapping tiene PAX8? {'PAX8' in biomarker_mapping}")
       logger.info(f"🔍 DEBUG PAX8: se guardó en data? {'IHQ_PAX8' in data}")
   ```

3. **Reprocesar caso con logging activado:**
   - Ejecutar FUNC-06 nuevamente
   - Revisar logs para ver dónde se pierde PAX8

4. **Verificar si hay REGLAS DE PRIORIDAD que sobrescriban:**
   - ¿Hay código después de línea 989 que sobrescribe biomarcadores?
   - ¿Hay lógica de "PRIORIDAD 2" que reemplaza narrative_biomarkers?

---

## CASOS DE REFERENCIA

**Casos para validar regresión después del fix:**

1. **IHQ250217** (este caso) - PAX8 NEGATIVO después de "y"
2. Buscar otros casos con patrón "negativas para... y PAX8/PAX-8"
3. Validar que otros biomarcadores NO se rompan

---

## REPORTE DE FIX

**Versión del fix:** v6.4.87
**Fecha:** 2026-01-17
**Archivo modificado:** core/extractors/biomarker_extractor.py líneas 5470-5498

**Cambio realizado:**
```python
# ANTES (v6.4.86 o anterior):
biomarcadores_encontrados = re.split(r'\s+y\s+|[,]\s*', lista_biomarkers_raw)
                                        ^^^ solo minúscula

# DESPUÉS (v6.4.87):
biomarcadores_encontrados = re.split(r'\s+[Yy]\s+|[,]\s*', lista_biomarkers_raw)
                                        ^^^^ case-insensitive
```

**Resultado:** ✅ FIX CORRECTO en biomarker_extractor  
**Problema:** ❌ unified_extractor NO integra el resultado correctamente

---

## CONCLUSIÓN

El fix v6.4.87 es **CORRECTO** pero **INCOMPLETO**.

- ✅ biomarker_extractor extrae PAX8 correctamente
- ❌ unified_extractor NO guarda PAX8 en la extracción final
- **Requiere:** Fix adicional en unified_extractor.py para guardar PAX8

**Estado final:** IHQ250217 Score 100% es un **FALSO POSITIVO**. El caso reporta completitud 100% pero IHQ_PAX8 tiene valor INCORRECTO ("NO MENCIONADO" en lugar de "NEGATIVO").
