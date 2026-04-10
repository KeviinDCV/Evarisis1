# DIAGNÓSTICO FIX v6.4.70 - CASO IHQ250205

**Fecha:** 2026-01-12  
**Versión:** v6.4.70  
**Caso:** IHQ250205 (Ganglio inguinal derecho)

---

## ESTADO ACTUAL

**Score:** 77.8% (sin mejora después de FUNC-06)

**Biomarcadores con valores incorrectos:**
1. CD3: BD=POSITIVO, OCR=NEGATIVO ❌
2. CD4: BD=POSITIVO, OCR=NEGATIVO ❌
3. CD5: BD=POSITIVO, OCR=NEGATIVO ❌
4. BCL2: BD=POSITIVO, OCR=NEGATIVO ❌

---

## ANÁLISIS DEL TEXTO OCR

### Fragmento Crítico:

```
[Células neoplásicas:]
"...que son positivas para CD45, CD20, PAX 5, focal y tenue para
MUM1 con marcación irregular heterogénea para CD30 y LMP-1. 
Son negativas para ALK, CD15, BcL2, BcL6, CD3, CD5, CD45, CD10."

[Microambiente reactivo:]
"El microambiente acompañante está compuesto de linfocitos T maduros 
(CD2+, CD3+, CD4+, CD5+, CD7+, BCL2+) con ausencia de células 
plasmáticas (CD138-)."
```

---

## PROBLEMA IDENTIFICADO

### Extracción Incorrecta de Múltiples Fuentes

El extracto de IHQ tiene DOS poblaciones celulares con marcadores DIFERENTES:

1. **CÉLULAS NEOPLÁSICAS (malignas):**
   - CD3: NEGATIVO
   - CD5: NEGATIVO
   - BCL2 (BcL2): NEGATIVO
   - CD4: NO MENCIONADO

2. **MICROAMBIENTE REACTIVO (linfocitos T normales):**
   - CD2: POSITIVO
   - CD3: POSITIVO
   - CD4: POSITIVO
   - CD5: POSITIVO
   - CD7: POSITIVO
   - BCL2: POSITIVO

### Orden de Extracción (CAUSA DEL ERROR)

1. **PASO 1:** Extractor captura del microambiente:
   - CD3+ → IHQ_CD3 = POSITIVO ✅ (captura correcta)
   - CD4+ → IHQ_CD4 = POSITIVO ✅ (captura correcta)
   - CD5+ → IHQ_CD5 = POSITIVO ✅ (captura correcta)
   - BCL2+ → IHQ_BCL2 = POSITIVO ✅ (captura correcta)

2. **PASO 2 (FIX v6.4.70):** Pase final "Son negativas para..."
   - Patrón: `(?i)(?:son|siendo)\s+negativas?\s+para:?\s+([A-Za-z0-9\s,\-]+?)(?:\s*[\.;]|$)`
   - Match: "Son negativas para ALK, CD15, BcL2, BcL6, CD3, CD5, CD45, CD10"
   - Lista capturada: ['ALK', 'CD15', 'BcL2', 'BcL6', 'CD3', 'CD5', 'CD45', 'CD10']

3. **PASO 3 (FIX v6.4.70):** Sobrescribir POSITIVO → NEGATIVO
   - CD3: POSITIVO → NEGATIVO ❌ **NO APLICÓ**
   - CD5: POSITIVO → NEGATIVO ❌ **NO APLICÓ**
   - BCL2: POSITIVO → NEGATIVO ❌ **NO APLICÓ**
   - CD4: POSITIVO → ??? ❌ **NO ESTÁ EN LISTA "Son negativas para"**

---

## VERIFICACIÓN DEL FIX v6.4.70

### Código Actual (líneas 3990-4004):

```python
# Patrón 5: V6.4.70 FIX IHQ250205
final_son_negativas_pattern = r'(?i)(?:son|siendo)\s+negativas?\s+para:?\s+([A-Za-z0-9\s,\-]+?)(?:\s*[\.;]|$)'
for match in re.finditer(final_son_negativas_pattern, text):
    lista_biomarcadores = match.group(1).strip()
    for bio in re.split(r'\s*,\s*', lista_biomarcadores):
        bio = bio.strip()
        if bio and len(bio) > 1:
            normalized = normalize_biomarker_name(bio)
            if normalized and results.get(normalized) == 'POSITIVO':
                # SOBRESCRIBIR POSITIVO a NEGATIVO
                results[normalized] = 'NEGATIVO'
                logging.info(f"🔴 [PASE FINAL v6.4.70] {normalized}: POSITIVO → NEGATIVO")
```

### Prueba del Patrón:

**Input:** Texto OCR completo  
**Match 1:** "Son negativas para ALK, CD15, BcL2, BcL6, CD3, CD5, CD45, CD10."  
**Captura:** "ALK, CD15, BcL2, BcL6, CD3, CD5, CD45, CD10"  
**Biomarcadores separados:** ['ALK', 'CD15', 'BcL2', 'BcL6', 'CD3', 'CD5', 'CD45', 'CD10']

✅ **Patrón captura correctamente CD3, CD5, BcL2**  
❌ **CD4 NO está en la lista (porque NO es negativo para células neoplásicas, solo se menciona en microambiente)**

---

## CAUSA RAÍZ

### POR QUÉ EL FIX NO SE APLICÓ

**Hipótesis 1:** Condición `results.get(normalized) == 'POSITIVO'` falla

El código solo sobrescribe si el valor previo es exactamente "POSITIVO". Necesito verificar si el extractor está guardando valores con formato diferente.

**Verificación necesaria:**
- ¿Qué valor tiene exactamente `results['CD3']` antes del pase final?
- ¿Es "POSITIVO" o "POSITIVO (algún detalle adicional)"?

**Hipótesis 2:** Normalización falla para BcL2

El texto OCR tiene "BcL2" (con minúscula L), la función `normalize_biomarker_name()` debe normalizar a "BCL2".

---

## VALIDACIÓN DE REGRESIÓN

### Casos de Referencia (NO VALIDADOS):

⚠️ **REGLA CRÍTICA #1 VIOLADA**

**ANTES de modificar, debería haberse:**
1. Identificado 3-5 casos con score 100% que usan estos patrones
2. Auditado ANTES de aplicar fix v6.4.70
3. Reprocesado DESPUÉS del fix
4. Comparado scores ANTES/DESPUÉS

**Estado actual:** NO se validó anti-regresión

---

## SOLUCIÓN PROPUESTA

### Opción 1: Debugging del Fix v6.4.70 (INMEDIATO)

Agregar logging detallado ANTES del pase final:

```python
# ANTES del pase final v6.4.70
logging.info(f"📊 [PRE-PASE v6.4.70] Estado actual:")
for bio in ['CD3', 'CD4', 'CD5', 'BCL2']:
    valor = results.get(bio, 'N/A')
    logging.info(f"   {bio}: {repr(valor)}")

# Ejecutar pase final...

# DESPUÉS del pase final
logging.info(f"📊 [POST-PASE v6.4.70] Estado final:")
for bio in ['CD3', 'CD4', 'CD5', 'BCL2']:
    valor = results.get(bio, 'N/A')
    logging.info(f"   {bio}: {repr(valor)}")
```

### Opción 2: Fix para CD4 (COMPLEMENTARIO)

CD4 solo aparece en microambiente, NO en células neoplásicas. Necesita regla específica:

```python
# V6.4.71 FIX CD4: Detectar microambiente reactivo
microambiente_pattern = r'(?i)microambiente\s+acompa[ñn]ante\s+.*?\(([^)]+)\)'
for match in re.finditer(microambiente_pattern, text):
    # Biomarcadores del microambiente NO deben extraerse como resultado IHQ
    bios_reactivos = match.group(1)
    for bio in re.findall(r'([A-Z0-9]+)\+', bios_reactivos):
        normalized = normalize_biomarker_name(bio)
        if normalized in results and normalized not in ['CD45', 'CD20']:  # Excepciones
            # ELIMINAR biomarcador que solo está en microambiente
            del results[normalized]
            logging.info(f"🔴 [MICROAMBIENTE v6.4.71] {normalized}: ELIMINADO (solo en microambiente)")
```

### Opción 3: Validación de Normalización (VERIFICACIÓN)

Agregar test unitario:

```python
# Test normalización BcL2 → BCL2
assert normalize_biomarker_name('BcL2') == 'BCL2'
assert normalize_biomarker_name('BCL2') == 'BCL2'
assert normalize_biomarker_name('bcl2') == 'BCL2'
```

---

## PRÓXIMOS PASOS

1. **INMEDIATO:** Agregar logging detallado (Opción 1)
2. **REPROCESAR:** IHQ250205 con logging activado
3. **ANALIZAR:** Logs para entender por qué no se aplica
4. **CORREGIR:** Fix v6.4.70 según hallazgos
5. **VALIDAR:** Anti-regresión con 3-5 casos de referencia
6. **DOCUMENTAR:** Actualizar CHANGELOG con resultado

---

## APRENDIZAJES

1. **Fix v6.4.70 es PARCIAL:** Solo cubre biomarcadores en "Son negativas para", NO cubre microambiente
2. **Necesidad de DEBUGGING:** Sin logs, imposible saber si el código se ejecuta correctamente
3. **REGLA CRÍTICA #1:** Validación anti-regresión OBLIGATORIA antes de deploy
4. **Complejidad de IHQ:** Múltiples poblaciones celulares con marcadores diferentes requiere lógica sofisticada

---

**ESTADO:** FIX v6.4.70 NO FUNCIONA COMO ESPERADO  
**ACCIÓN REQUERIDA:** DEBUGGING + CORRECCIÓN + VALIDACIÓN ANTI-REGRESIÓN  
**PRIORIDAD:** ALTA (caso con score 77.8%)
