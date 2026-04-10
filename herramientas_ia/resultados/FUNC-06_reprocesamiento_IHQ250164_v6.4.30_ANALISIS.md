# ANÁLISIS FALLIDO: Corrección v6.4.30 IHQ250164

**Fecha:** 2026-01-08 03:00
**Caso:** IHQ250164
**Score final:** 88.9% (esperado: 100%)
**Estado:** ❌ **FALLÓ - Corrección NO funcionó**

---

## 📋 RESUMEN EJECUTIVO

Las correcciones v6.4.30 implementadas NO resolvieron el problema de extracción de biomarcadores NEGATIVOS en IHQ250164.

**Biomarcadores problemáticos (3/5 fallaron):**
- ❌ CD5: BD=NEGATIVO, OCR=POSITIVO (debería ser NEGATIVO)
- ❌ CD10: BD=NEGATIVO, OCR=POSITIVO (debería ser NEGATIVO)
- ❌ BCL6: BD=NEGATIVO, OCR=POSITIVO (debería ser NEGATIVO)
- ✅ SOX11: (valor correcto pero auditor lo marca como conflictivo)
- ❌ CICLINA_D1: Sin columna/mapeo

---

## 🔍 CAUSA RAÍZ IDENTIFICADA

### Problema 1: Lógica Condicional Incorrecta (CRÍTICO)

**Ubicación:** `biomarker_extractor.py` línea 3648

**Código actual v6.4.30:**
```python
if normalized and results.get(normalized) == 'POSITIVO':
    results[normalized] = 'NEGATIVO'
```

**Problema:**
Esta condición solo sobrescribe si el biomarcador **YA TIENE** valor `'POSITIVO'` en `results`. En IHQ250164:
- CD5, CD10, BCL6 **NUNCA fueron extraídos como POSITIVO** anteriormente
- Por lo tanto, `results.get(normalized)` devuelve `None` (no 'POSITIVO')
- La condición falla y NO sobrescribe a NEGATIVO

**Texto en OCR:**
```
"es positiva para CD20, PAX-5 Y BCL-2, y negativa con el CD5, CD10, BCL6, IgD, SOX -11 y Ciclyna D1"
```

Esto significa:
- **POSITIVO:** CD20, PAX-5, BCL-2
- **NEGATIVO:** CD5, CD10, BCL6, IgD, SOX-11, CICLINA_D1

**Solución:**
```python
if normalized:
    results[normalized] = 'NEGATIVO'  # Asignar NEGATIVO sin condición previa
```

---

### Problema 2: Aliases Faltantes en `normalize_biomarker_name()`

**Ubicación:** `biomarker_extractor.py` líneas 5717-6207 (función `normalize_biomarker_name`)

**Biomarcadores que NO normalizan:**
1. **"CICLYNA D1"** (variante ortográfica con Y + espacio)
   - Existe: `'CYCLINA': 'CICLINA_D1'` (línea 6198)
   - Falta: `'CICLYNA D1': 'CICLINA_D1'`
   - Falta: `'CICLYNA-D1': 'CICLINA_D1'`

2. **"IGD"** (inmunoglobulina D)
   - No existe en `name_mapping`
   - No existe columna `IHQ_IGD` en BD (confirmado)
   - Auditor lo marca como "sin columna"

**Test de normalización:**
```
normalize_biomarker_name("CICLYNA D1") → None  ❌
normalize_biomarker_name("SOX -11")     → None  ❌ (pero "SOX-11" SÍ funciona)
normalize_biomarker_name("IGD")         → None  ❌
normalize_biomarker_name("CD5")         → "CD5" ✅
normalize_biomarker_name("CD10")        → "CD10" ✅
normalize_biomarker_name("BCL6")        → "BCL6" ✅
```

**Solución:**
Agregar en `name_mapping` (alrededor línea 6198):
```python
'CICLYNA D1': 'CICLINA_D1',
'CICLYNA-D1': 'CICLINA_D1',
'CICLYNA': 'CICLINA_D1',  # Alias adicional
```

Para IGD: Decidir si agregar columna `IHQ_IGD` o marcar como "no estándar".

---

### Problema 3: Patrón Regex v6.4.30 es Correcto (NO es el problema)

**Ubicación:** `biomarker_extractor.py` líneas 3636-3637

**Patrón actual:**
```python
final_neg_con_el = re.findall(
    r'(?i)negativ[oa]s?\s+con(?:\s+el)?\s+([A-Za-z0-9\s,\-]+?)(?=;|\.|$)',
    text
)
```

**Test exitoso:**
```python
Input:  "negativa con el CD5,\nCD10, BCL6, IgD, SOX -11 y Ciclyna D1; hay..."
Output: ['CD5,\nCD10, BCL6, IgD, SOX -11 y Ciclyna D1']  ✅ CORRECTO
```

El patrón captura correctamente la lista completa (incluyendo saltos de línea).

---

## 📊 VALORES ACTUALES vs ESPERADOS

| Biomarcador | Valor BD Actual | Valor OCR | Valor Esperado | Estado |
|-------------|-----------------|-----------|----------------|--------|
| CD5         | NEGATIVO        | POSITIVO  | NEGATIVO       | ❌ ERROR |
| CD10        | NEGATIVO        | POSITIVO  | NEGATIVO       | ❌ ERROR |
| BCL6        | NEGATIVO        | POSITIVO  | NEGATIVO       | ❌ ERROR |
| SOX11       | (?)             | NEGATIVO  | NEGATIVO       | ⚠️ Verificar |
| CICLINA_D1  | (sin columna)   | NEGATIVO  | NEGATIVO       | ❌ Sin mapeo |
| IGD         | (sin columna)   | NEGATIVO  | (N/A)          | ⚠️ No estándar |

**Nota:** Auditor marca CD5/CD10/BCL6 como "OCR=POSITIVO" porque detecta la frase "positiva para CD20..." y asocia erróneamente estos biomarcadores.

---

## 🛠️ CORRECCIONES NECESARIAS v6.4.31

### Corrección 1: Cambiar Lógica Condicional (CRÍTICO)

**Archivo:** `core/extractors/biomarker_extractor.py`
**Línea:** 3648

**Cambio:**
```python
# ANTES (v6.4.30):
if normalized and results.get(normalized) == 'POSITIVO':
    results[normalized] = 'NEGATIVO'

# DESPUÉS (v6.4.31):
if normalized:
    results[normalized] = 'NEGATIVO'  # V6.4.31: Asignar directamente sin verificar valor previo
    logging.info(f"🔴 [V6.4.31 negativa con el] {normalized} = NEGATIVO")
```

**Justificación:**
- El patrón "negativa con el X" es **definitivo** (no correctivo)
- No requiere que el biomarcador haya sido POSITIVO antes
- Si aparece en esta lista, debe ser NEGATIVO independientemente del valor previo

---

### Corrección 2: Agregar Aliases en `name_mapping`

**Archivo:** `core/extractors/biomarker_extractor.py`
**Línea:** ~6198 (después de `'CYCLINA': 'CICLINA_D1',`)

**Agregar:**
```python
'CICLYNA': 'CICLINA_D1',      # V6.4.31: Variante ortográfica (Ciclyna)
'CICLYNA D1': 'CICLINA_D1',   # V6.4.31: Con espacio
'CICLYNA-D1': 'CICLINA_D1',   # V6.4.31: Con guion
```

---

### Corrección 3: Decisión sobre IGD

**Opciones:**

**A. Agregar columna IHQ_IGD (si es biomarcador estándar)**
1. Modificar `database_manager.py` (agregar columna)
2. Agregar alias en `biomarker_extractor.py`:
   ```python
   'IGD': 'IGD',
   'IG D': 'IGD',
   'IG-D': 'IGD',
   ```

**B. Marcar como no estándar (si es poco común)**
- Auditor lo seguirá marcando como "sin columna"
- No afecta score si no se usa frecuentemente

**Recomendación:** Verificar frecuencia de IGD en otros casos antes de decidir.

---

## 🔄 PLAN DE VALIDACIÓN v6.4.31

1. **Aplicar correcciones 1 y 2**
2. **Reprocesar IHQ250164 con FUNC-06**
3. **Auditar con FUNC-01**
4. **Validar score = 100%**
5. **Validar casos de referencia (sin regresión):**
   - IHQ250133 (MMR 4 marcadores)
   - IHQ250159 (MMR 4 marcadores)
   - Otros casos con patrón "negativa con el"

---

## 📝 NOTAS ADICIONALES

- El patrón v6.4.30 línea 3635 fue **bien diseñado** pero con lógica condicional incorrecta
- La normalización de "SOX -11" (con espacio) requiere revisar si el alias "SOX 11" (línea 5845) incluye espacios antes del guion
- El auditor puede tener falsos positivos al marcar biomarcadores como "POSITIVO en OCR" por contexto ambiguo

---

**Siguiente paso:** Aplicar correcciones v6.4.31 y reprocesar.

