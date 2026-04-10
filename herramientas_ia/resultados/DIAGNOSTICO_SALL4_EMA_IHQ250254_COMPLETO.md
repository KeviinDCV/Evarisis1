# 🔍 DIAGNÓSTICO COMPLETO: SALL-4 y EMA no se capturan en IHQ250254

**Fecha:** 2026-01-28
**Versión Actual:** v6.5.57
**Caso:** IHQ250254 - CARCINOSARCOMA DEL OVARIO

---

## ✅ RESUMEN EJECUTIVO

**PROBLEMA CONFIRMADO:** SALL-4 y EMA están en el PDF pero NO se extraen a la base de datos.

**CAUSA RAÍZ IDENTIFICADA:** El patrón de línea 9230 en `biomarker_extractor.py` NO incluye paréntesis en la clase de caracteres permitida, por lo que se detiene al encontrar "SALL 4 (focal)" y "EMA (focal)".

**SOLUCIÓN:** Agregar `()` a la clase de caracteres del patrón de línea 9230.

---

## 📄 EVIDENCIA DEL PROBLEMA

### En el OCR (Descripción Microscópica):

```
"Las células tumorales presentan una marcación bifásica, un componente
epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal) y el componente
mesenquimal es positivo para S100."
```

**Biomarcadores esperados (componente epitelial):**
1. CKAE1/AE3 → ✅ POSITIVO (capturado)
2. PAX 8 → ✅ POSITIVO (capturado)
3. **SALL 4 (focal)** → ❌ NO capturado
4. P53 → ✅ POSITIVO (capturado)
5. **EMA (focal)** → ❌ NO capturado

### En el debug_map (línea 57):

```json
"descripcion_microscopica": "Previa valoración de la técnica y verificación de la adecuada tinción de los controles externos e internos se realizan estudios de inmunohistoquímica en la plataforma automatizada Roche VENTANA®. En el espécimen A2: Las células tumorales presentan una marcación bifásica, un componente epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), p53, EMA (focal) y el componente mesenquimal es positivo para S100.. Sin marcación positiva para : DESMINA, WT1, RECEPTORES DE ESTROGENOS. El KI-67(indice de proliferación):80%. El especimen B muestra un grupo de celularidad atípica focal en el ovario que presenta una marcación positiva para : CKAE1/AE3, PAX 8, y KI-67 del 80% . Sin marcación positiva para SALLL4"
```

### En la BD (línea 86):

```json
"IHQ_ESTUDIOS_SOLICITADOS": "CKAE1AE3, DESMIN, Ki-67, P53, PAX8, Receptor de Estrógeno, S100, WT1"
```

**Faltan: SALL-4 y EMA**

### Biomarcadores capturados (líneas 96-103):

```json
"IHQ_CKAE1AE3": "POSITIVO",
"IHQ_DESMIN": "POSITIVO",
"IHQ_KI-67": "80%",
"IHQ_P53": "POSITIVO",
"IHQ_PAX8": "POSITIVO",
"IHQ_RECEPTOR_ESTROGENOS": "POSITIVO",
"IHQ_S100": "POSITIVO",
"IHQ_WT1": "POSITIVO"
```

**NO capturados:**
- IHQ_SALL4
- IHQ_EMA

---

## 🔧 ANÁLISIS TÉCNICO

### Patrón Responsable (línea 9230):

```python
r'positiv[oa]s?(?:\s+\w+){0,10}\s+para\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+]+)+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+]+)+)*)',
```

### Clase de caracteres actual:

```
[\w\s/.\-+]
```

**Incluye:**
- `\w` → letras, dígitos, guión bajo (a-zA-Z0-9_)
- `\s` → espacios
- `/` → slash
- `.` → punto
- `-` → guión
- `+` → más

**NO incluye:**
- `(` → paréntesis izquierdo ❌
- `)` → paréntesis derecho ❌

### Por qué falla la captura:

**Texto procesado:**
```
"positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
```

**Comportamiento del patrón:**

1. Encuentra "positivo para "
2. Comienza captura: "CKAE1/AE3, PAX 8, SALL 4 "
3. Encuentra `(` → NO está en `[\w\s/.\-+]` → **SE DETIENE**
4. Captura parcial: "CKAE1/AE3, PAX 8, SALL 4"
5. NO continúa después del paréntesis

**Resultado:**
- Lista capturada: "CKAE1/AE3, PAX 8, SALL 4" (incompleta)
- "SALL 4" sin "(focal)" → se procesa
- Pero al llegar a `parse_narrative_biomarker_list()`, "SALL 4" NO normaliza correctamente

### ¿Por qué "SALL 4" no normaliza?

En `parse_narrative_biomarker_list()` (líneas 9705-9717):

```python
# V6.5.56 FIX IHQ250254: Preservar paréntesis con calificadores (focal, difuso, etc.)
preservar_parentesis = False
if re.search(r'\((?:focal|difuso|difusa|fuerte|d[eé]bil|moderado|moderada|intensa|leve)\)', part, re.IGNORECASE):
    preservar_parentesis = True

if part.startswith('(') and not re.match(r'^\([0-3]\+?\)', part) and not preservar_parentesis:
    part = part[1:].strip()
if part.endswith(')') and not re.search(r'\([0-3]\+?\)$', part) and not preservar_parentesis:
    part = part[:-1].strip()
```

**Problema:**
- Si el patrón de línea 9230 captura "SALL 4" (sin paréntesis), la función `parse_narrative_biomarker_list()` recibe "SALL 4"
- Luego intenta normalizar "SALL 4" → busca en aliases

En `normalize_biomarker_name()` (línea 7684):

```python
'SALL4': 'SALL4',
'SALL-4': 'SALL4',
'SALL 4': 'SALL4',  # ✅ EXISTE
```

**PERO:**
- El patrón de línea 9230 NO captura "SALL 4 (focal)" completo
- Solo captura fragmentos antes del paréntesis
- Como la lista queda incompleta, el procesamiento posterior falla

### ¿Por qué EMA tampoco se captura?

**Mismo problema:**

```
"positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
```

1. Patrón se detiene en "SALL 4 (" → captura "CKAE1/AE3, PAX 8, SALL 4"
2. NO continúa después del paréntesis
3. **EMA (focal) queda fuera de la captura**

---

## 🎯 SOLUCIÓN

### Modificación en biomarker_extractor.py

**Línea 9230 (ANTES):**

```python
r'positiv[oa]s?(?:\s+\w+){0,10}\s+para\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+]+)+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+]+)+)*)',
```

**Línea 9230 (DESPUÉS):**

```python
r'positiv[oa]s?(?:\s+\w+){0,10}\s+para\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+()\n]+)+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-+()\n]+)+)*)',
```

**Cambios:**
- `[\w\s/.\-+]` → `[\w\s/.\-+()\n]`
- Agregado: `()` (paréntesis) y `\n` (salto de línea opcional)

### Justificación:

1. **Paréntesis `()`:** Permite capturar calificadores como "(focal)", "(difuso)", "(fuerte)"
2. **Salto de línea `\n`:** El OCR puede tener saltos de línea dentro de listas largas

### Resultado esperado:

**Texto procesado:**
```
"positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
```

**Captura:**
```
"CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
```

**Procesamiento en `parse_narrative_biomarker_list()`:**

Partes identificadas:
1. "CKAE1/AE3" → IHQ_CKAE1AE3 = POSITIVO
2. "PAX 8" → IHQ_PAX8 = POSITIVO
3. "SALL 4 (focal)" → IHQ_SALL4 = POSITIVO (FOCAL) ✅
4. "P53" → IHQ_P53 = POSITIVO
5. "EMA (focal)" → IHQ_EMA = POSITIVO (FOCAL) ✅

---

## 📊 PATRONES ADICIONALES A VERIFICAR

Hay **otros patrones** en `high_priority_list_patterns` que también necesitan `()`:

### Línea 9144 (FIX v6.4.47):
```python
r'(?i)positiv[oa]s?\s+para:\s+(.+?)(?:\.\s|\s+las\s+células\s+tumorales)',
```
**Clase:** `.+?` (acepta TODO, incluyendo paréntesis) ✅ OK

### Línea 9156 (FIX v6.4.47):
```python
r'(?i)negativ[oa]s?\s+para:\s+(.+?)(?:\.\s|$|\s+con\s)',
```
**Clase:** `.+?` (acepta TODO) ✅ OK

### Línea 9235 (V6.3.88):
```python
r'marcaci[óo]n(?:\s+\w+){1,10}\s+de\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+)*)',
```
**Clase:** `[\w\s/.\-]` → **FALTA ()** ❌

### Línea 9215 (V6.3.84):
```python
r'marcaci[óo]n(?:\s+\w+){0,10}\s+para\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+)*)',
```
**Clase:** `[\w\s/.\-]` → **FALTA ()** ❌

### Línea 9218 (V6.3.84):
```python
r'positividad(?:\s+\w+){0,10}\s+para\s+((?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+(?:\s+(?:y|e|,)\s+(?:(?!y\s+con\b|con\s+positividad|con\s+marcaci)[\w\s/.\-])+)*)',
```
**Clase:** `[\w\s/.\-]` → **FALTA ()** ❌

**RECOMENDACIÓN:** Actualizar **TODAS** las clases `[\w\s/.\-]` a `[\w\s/.\-+()\n]` para consistencia.

---

## ⚠️ VALIDACIÓN ANTI-REGRESIÓN REQUERIDA

**ANTES de modificar:**

1. **Identificar casos de referencia** (mínimo 5):
   - Casos con score 100% que usan el patrón de línea 9230
   - Buscar casos con listas "positivo para X, Y, Z"

2. **Auditar casos de referencia ANTES:**
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250XXX --inteligente
   python herramientas_ia/auditor_sistema.py IHQ250YYY --inteligente
   python herramientas_ia/auditor_sistema.py IHQ250ZZZ --inteligente
   ```

3. **Guardar scores actuales** para comparación

**DESPUÉS de modificar:**

4. **Reprocesar caso problemático:**
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250254 --func-06
   ```

5. **Reprocesar casos de referencia:**
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250XXX --func-06
   python herramientas_ia/auditor_sistema.py IHQ250YYY --func-06
   python herramientas_ia/auditor_sistema.py IHQ250ZZZ --func-06
   ```

6. **Comparar scores ANTES/DESPUÉS:**
   - Si CUALQUIER caso baja su score → REVERTIR INMEDIATAMENTE
   - Solo continuar si TODOS mantienen o mejoran su score

---

## 🎯 CASOS DE REFERENCIA SUGERIDOS

Buscar casos que usan el patrón "positivo para [lista]":

```bash
grep -l "positivo para" data/debug_maps/*.json | head -10
```

**Criterios:**
- Casos con score 100%
- Casos con listas de biomarcadores después de "positivo para"
- Casos SIN calificadores entre paréntesis (para validar que no se rompen)

---

## 📝 CHANGELOG PROPUESTO

```
Cambios v6.5.58:
  - ✅ FIX IHQ250254: Agregar soporte para paréntesis en listas narrativas (línea 9230)
  - 🔍 Problema: "SALL 4 (focal)", "EMA (focal)" no se extraían
  - 🔍 Causa raíz: Clase de caracteres [\w\s/.\-+] NO incluía paréntesis ()
    → Patrón se detenía al encontrar "(" en "SALL 4 (focal)"
    → Lista capturada parcialmente: "CKAE1/AE3, PAX 8, SALL 4" (sin EMA)
  - 💡 Solución: Actualizar clase de caracteres a [\w\s/.\-+()\n]
    → Ahora captura calificadores completos: "SALL 4 (focal)", "EMA (focal)"
  - 📝 Líneas modificadas: 9230
  - 🎯 Resultado: SALL4 y EMA ahora extraen como "POSITIVO (FOCAL)"
  - ⚠️ Validación: Requiere reprocesamiento de casos afectados (FUNC-06)
  - ✅ Casos de referencia validados: [AGREGAR DESPUÉS DE VALIDACIÓN]
```

---

## 🔄 PRÓXIMOS PASOS

1. **Modificar línea 9230** (agregar `()` a clase de caracteres)
2. **Identificar 5 casos de referencia** (score 100%, uso de patrón línea 9230)
3. **Auditar casos de referencia ANTES** (guardar scores)
4. **Reprocesar IHQ250254** (FUNC-06)
5. **Reprocesar casos de referencia** (FUNC-06)
6. **Comparar scores ANTES/DESPUÉS**
7. **SI REGRESIÓN → REVERTIR**
8. **SI OK → Actualizar changelog + versión**

---

**FIN DEL DIAGNÓSTICO**
