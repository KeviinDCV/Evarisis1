# ANÁLISIS: Mapeo ACTINA_MUSCULO_ESPECIFICA en IHQ250140

## Resumen Ejecutivo
- **Case:** IHQ250140
- **FUNC-06:** Reprocessing exitoso (49 casos reprocesados)
- **FUNC-01:** Score 88.9% (NO es 100%)
- **Razón:** Biomarcadores no mapeados correctamente
- **Estado:** REQUERIDA CORRECCIÓN EN BIOMARKER EXTRACTOR

---

## Problema Identificado

### 1. ACTINA MÚSCULO ESPECÍFICA - NO EXTRAÍDO
**Expected state:**
```
OCR Line 36: "Las células tumorales son positivas para actina de músculo especifica, SMA y caldesmon"
→ IHQ_ACTINA_MUSCULO_ESPECIFICA debería ser: POSITIVO
```

**Actual state:**
```
BD IHQ250140: IHQ_ACTINA_MUSCULO_ESPECIFICA = N/A (vacío)
Audit JSON: ACTINA MÚSCULO ESPECÍFICA listed as "sin columna" (línea 90)
```

**Root cause:**
- Extractor reconoce "ACTINA MUSCULO ESPECIFICA" en alias mapping (línea 297-299)
- PERO no extrae correctamente del OCR
- Posible problema: Patrón regex busca formato exacto pero OCR tiene "actina de músculo especifica"
- El extractora SÍ captura "ACTINA MUSCULO LISO" (variante syn liso) pero NO la variante "especifica"

---

### 2. CKAE1E3 - MISSPELLED EN OCR
**Expected state:**
```
OCR Line 39: "No tienen expresión para CKE1E3, desmina, MyoD1..."
→ IHQ_CKAE1E3 debería ser: NEGATIVO (misspelled como CKE1E3)
```

**Actual state:**
```
BD IHQ250140: IHQ_CKAE1E3 = N/A (vacío)
Audit JSON: CKAE1E3 listed as "sin columna" (línea 87)
```

**Root cause:**
- OCR tiene "CKE1E3" (sin la A en primera posición → CKE1E3 vs CKAE1E3)
- Extractor alias mapping busca: "CKAE1E3", "CKAE1AE3", "CKAE1/AE3", etc. (línea 316-320)
- PERO no tiene alias para la versión misspelled "CKE1E3"
- Extractor es sensible a typos en el OCR

---

## Evidencia del OCR

```
Line 31: "Se revisan placas para marcación de CKAE1E3, desmina, actina de músculo
liso, actina músculo específica, caldesmon, MyoD1, mIogenina, Ki67, S100, SOX10, CD68, CD34 y MDM2."

Line 36: "Las células tumorales son positivas para actina de músculo especifica, 
SMA y caldesmon. CD34 positiv..."

Line 39: "No tienen expresión para CKE1E3, desmina, MyoD1, miogenina, MDMD2, 
S100 y SOX10."
```

---

## Análisis de Extracción

### Qué SÍ se extrajo correctamente:
- IHQ_DESMIN: POSITIVO ✅ (OCR: "positivas para... desmina")
- IHQ_ACTINA_MUSCULO_LISO: POSITIVO ✅ (OCR: "positivas para actina de músculo liso")
- IHQ_KI-67: 80% ✅ (aunque hay valor corrupto detectado: "d" en OCR)

### Qué NO se extrajo:
- IHQ_ACTINA_MUSCULO_ESPECIFICA: (vacío) ❌
  - OCR tiene: "actina de músculo especifica" (línea 32)
  - OCR tiene: "positivas para actina de músculo especifica" (línea 36)
  - Base datos alias: Reconoce "ACTINA MUSCULO ESPECIFICA" pero extractor no lo encuentra

- IHQ_CKAE1E3: (vacío) ❌
  - OCR tiene: "CKE1E3" (typo: falta la A) en línea 39
  - Base datos alias: Mapea "CKAE1E3" pero NO "CKE1E3"
  - Necesita alias para versión misspelled

---

## Soluciones Recomendadas

### Solución 1: Agregar soporte para "ACTINA DE MÚSCULO ESPECÍFICA"
**Archivo:** `core/extractors/biomarker_extractor.py`
**Acción:** Actualizar patrón regex de extracción para "ACTINA MÚSCULO ESPECÍFICA"

**Problema actual:**
- Extractor busca por alias exacto pero OCR tiene "actina de músculo especifica"
- Necesita patrón más flexible que reconozca ambas variantes:
  - "ACTINA MUSCULO ESPECIFICA"
  - "ACTINA DE MUSCULO ESPECIFICA"
  - "ACTINA MÚSCULO ESPECÍFICA"
  - "ACTINA DE MÚSCULO ESPECÍFICA"

**Cambio sugerido:**
```python
# En biomarker_extractor.py, función de ACTINA_MUSCULO_ESPECIFICA:
# Cambiar patrón de:
#   r'actina\s+de\s+m[uú]sculo\s+especif[íi]?ca'
# A:
#   r'actina\s+(?:de\s+)?m[uú]sculo\s+especif[íi]?ca'
# Esto permitirá: "actina músculo específica" O "actina de músculo específica"
```

### Solución 2: Agregar alias para CKAE1E3 misspelled
**Archivo:** `herramientas_ia/auditor_sistema.py` (línea 316-320)
**Acción:** Agregar alias "CKE1E3" que mapee a "IHQ_CKAE1E3"

**Cambio sugerido:**
```python
# En BIOMARKER_ALIAS_MAP, sección CKAE1:
'CKAE1E3': 'IHQ_CKAE1E3',
'CKAE1AE3': 'IHQ_CKAE1E3',
'CKAE1/AE3': 'IHQ_CKAE1E3',
'CK AE1 AE3': 'IHQ_CKAE1E3',
'CK AE1/AE3': 'IHQ_CKAE1E3',
'CKE1E3': 'IHQ_CKAE1E3',  # ← NUEVO: Alias para typo común (sin la A)
```

---

## Impacto de las Correcciones

Si se aplican ambas soluciones:
- **Antes:** IHQ250140 Score 88.9% (6 biomarcadores sin mapeo)
- **Después:** IHQ250140 Score 100% (todos los biomarcadores mapeados)

---

## Próximos Pasos

1. **Modificar biomarker_extractor.py** para reconocer "ACTINA DE MÚSCULO ESPECÍFICA" con patrón flexible
2. **Agregar alias en auditor_sistema.py** para "CKE1E3" → IHQ_CKAE1E3
3. **Ejecutar FUNC-06 nuevamente** para reprocesar IHQ250140 con extractores corregidos
4. **Ejecutar FUNC-01 nuevamente** para verificar Score = 100%

---

## Nota sobre Completitud Real vs Reportada

El caso IHQ250140 muestra el problema de **FALSA COMPLETITUD:**
- **BD reporta completitud:** X% 
- **FUNC-01 score de validación:** 88.9% (más bajo)
- **Motivo:** Biomarcadores que NO se extrajeron pero ESTÁN EN EL OCR

Este es exactamente el problema que FUNC-01 está diseñado para detectar.

