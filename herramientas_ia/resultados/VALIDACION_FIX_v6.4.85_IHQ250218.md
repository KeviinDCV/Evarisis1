# REPORTE DE VALIDACIÓN FUNC-06: IHQ250218

**Fecha:** 2026-01-19 01:23
**Versión extractores:** 6.4.85
**Resultado FUNC-06:** EXITOSO - 50 casos reprocesados

---

## RESUMEN EJECUTIVO

**Score auditoría:** 55.6% (5/9 validaciones OK)
**Problemas críticos detectados:** 3

| Categoría | Cantidad |
|-----------|----------|
| Biomarcadores solicitados | 11 |
| Correctamente extraídos | 8 |
| NO extraídos | 2 |
| Extraídos INCORRECTAMENTE | 1 |

---

## PROBLEMAS DETECTADOS

### 1. Ki-67 NO EXTRAÍDO (ERROR CRÍTICO)

**Valor en BD:** `NO MENCIONADO`
**Valor esperado:** `90%`

**Texto OCR:**
```
presentan un índice mitótico alto dado por un Ki67o es de 90%
```

**Causa raíz:**
- OCR tiene error tipográfico: `Ki67o` en lugar de `Ki67` o `Ki-67`
- El patrón actual probablemente busca `Ki-?67` pero NO `Ki67o`
- La letra "o" pegada después de "Ki67" impide el match

**Solución propuesta:**
```python
# Archivo: core/extractors/biomarker_extractor.py
# Línea aproximada: ~300-400

# Patrón actual:
r'Ki-?67'

# Patrón nuevo (tolera OCR con "o" pegada):
r'Ki-?67o?'
```

**Impacto:** Permitirá extraer Ki-67 cuando OCR tenga errores tipográficos comunes

---

### 2. MUM1 NO EXTRAÍDO (ERROR CRÍTICO)

**Valor en BD:** `NO MENCIONADO`
**Valor esperado:** `30%`

**Texto OCR:**
```
el MUM1 es del 30%
```

**Causa raíz:**
- Patrón de extracción NO reconoce formato narrativo `el MUM1 es del X%`
- El patrón actual probablemente busca formato estándar `MUM1: X%`

**Solución propuesta:**
```python
# Archivo: core/extractors/biomarker_extractor.py
# Línea aproximada: ~400-500

# Agregar patrón alternativo narrativo:
r'el\s+MUM-?1\s+es\s+del?\s+(\d+%)'

# Casos que captura:
# - "el MUM1 es del 30%"
# - "el MUM-1 es del 40%"
# - "el MUM1 es de 50%"
```

**Impacto:** Permitirá extraer MUM1 en formato narrativo (común en linfomas)

---

### 3. CD3 EXTRAÍDO INCORRECTAMENTE (WARNING - CONTAMINACIÓN)

**Valor en BD:** `POSITIVO`
**Valor esperado:** `NEGATIVO` o `NO MENCIONADO`

**Texto OCR (contexto CORRECTO - células tumorales):**
```
Son negativas para CD38, cMYC y CD30
```

**Texto OCR (contexto INCORRECTO - células acompañantes):**
```
Hay linfocitos T acompañantes CD3+, BCL2+
```

**Causa raíz:**
- Extractor captura `CD3+` de **linfocitos T acompañantes** (células NO tumorales)
- NO captura el valor real: células tumorales son CD3 negativas (implícito)
- **Contaminación con células del microambiente**

**Contexto clínico:**
- Linfocitos T (CD3+) son células del microambiente, NO tumorales
- Las células tumorales (linfocitos B) NO expresan CD3
- El valor `POSITIVO` es INCORRECTO porque describe células acompañantes

**Solución propuesta:**
```python
# Archivo: core/extractors/biomarker_extractor.py
# Línea aproximada: Función de extracción general

# ANTES de extraer biomarcador, verificar contexto
# Patrón de filtro:
r'(?:linfocitos|células)\s+(?:T\s+)?acompañantes'

# Lógica:
# 1. Buscar biomarcador en texto
# 2. SI está en contexto de "acompañantes" → IGNORAR
# 3. SI está en contexto de células tumorales → EXTRAER
```

**Impacto:**
- Evitará contaminar valores tumorales con valores de células del microambiente
- Afecta especialmente casos de linfomas donde se describe microambiente

---

### 4. BCL2 CORRECTAMENTE NO EXTRAÍDO (OK)

**Valor en BD:** `NO MENCIONADO`
**Valor esperado:** `NO MENCIONADO` (correcto)

**Texto OCR:**
```
Hay linfocitos T acompañantes CD3+, BCL2+
```

**Estado:** CORRECTO

**Nota:**
- BCL2+ en células acompañantes fue correctamente IGNORADO
- El extractor YA tiene lógica que previene esta contaminación para BCL2
- **Este es el comportamiento esperado y debe mantenerse**
- **La misma lógica debe aplicarse a CD3**

---

## ANÁLISIS COMPARATIVO: BCL2 vs CD3

| Biomarcador | Contexto | Valor BD | Estado |
|-------------|----------|----------|--------|
| BCL2 | "linfocitos T acompañantes BCL2+" | NO MENCIONADO | ✓ CORRECTO (ignorado) |
| CD3 | "linfocitos T acompañantes CD3+" | POSITIVO | ✗ INCORRECTO (capturado) |

**Conclusión:** El extractor ya tiene lógica para ignorar BCL2 en contexto de células acompañantes, pero NO la tiene para CD3. **La solución es extender esta lógica a CD3 y otros biomarcadores.**

---

## ACCIONES REQUERIDAS

### Prioridad ALTA

1. **Agregar variante `Ki67o` al patrón de Ki-67**
   - Archivo: `core/extractors/biomarker_extractor.py`
   - Cambio: `r'Ki-?67'` → `r'Ki-?67o?'`
   - Impacto: Tolerará errores tipográficos de OCR

2. **Agregar patrón narrativo para MUM1**
   - Archivo: `core/extractors/biomarker_extractor.py`
   - Agregar: `r'el\s+MUM-?1\s+es\s+del?\s+(\d+%)'`
   - Impacto: Extraerá MUM1 en formato narrativo

3. **Agregar filtro de contexto de células acompañantes**
   - Archivo: `core/extractors/biomarker_extractor.py`
   - Lógica: Verificar contexto ANTES de extraer
   - Patrón filtro: `r'(?:linfocitos|células)\s+(?:T\s+)?acompañantes'`
   - Impacto: Evitará contaminación con microambiente

### Validación Posterior

**Después de aplicar correcciones:**

1. Reprocesar IHQ250218 con FUNC-06
2. Validar:
   - Ki-67 = `90%`
   - MUM1 = `30%`
   - CD3 = `NO MENCIONADO` o `NEGATIVO` (NO `POSITIVO`)
3. Verificar score mejora: 55.6% → ~90%+

**Casos de referencia a validar (anti-regresión):**
- Buscar otros casos con MUM1 en formato estándar
- Buscar otros casos con Ki-67 normal
- Buscar otros casos con linfocitos acompañantes

---

## ARCHIVOS GENERADOS

- `herramientas_ia/resultados/VALIDACION_FIX_v6.4.85_IHQ250218.json`
- `herramientas_ia/resultados/VALIDACION_FIX_v6.4.85_IHQ250218.md` (este archivo)
- `herramientas_ia/resultados/auditoria_inteligente_IHQ250218.json`
- `data/debug_maps/debug_map_IHQ250218_[timestamp].json`

---

**Fin del reporte**
