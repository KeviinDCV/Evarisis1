# DIAGNOSTICO: Patrón v6.5.02 P16 NO Extrae Resultado

## Caso: IHQ250229
**Fecha:** 2026-01-28 04:35
**Version actual:** v6.5.02
**Problema:** P16 capturado pero NO extraído (valor = N/A)

---

## PROBLEMA DETECTADO

### Texto en OCR
```
P16 presenta marcación citoplasmática focal (negativo)
```

### Valor Esperado
```
IHQ_P16: "NEGATIVO"
```

### Valor Actual en BD
```
IHQ_P16: "N/A"
```

---

## ROOT CAUSE ANALYSIS

### Patrón Actual v6.5.02 (línea 1064)
```python
r'(?i)p16\s+presenta\s+marcaci[óo]n\s+[^(]+\((?:positivo|negativo)\)'
```

**Problema:** El patrón usa non-capturing group `(?:positivo|negativo)` que hace MATCH pero NO CAPTURA el valor.

### Comportamiento Actual
1. Patrón hace match: ✅ SI
2. Grupo de captura extrae resultado: ❌ NO (porque es `(?:...` en vez de `(...)`)
3. Sistema intenta normalizar: valor = texto completo "p16 presenta marcación..."
4. Normalización falla (no hay entrada para ese texto)
5. Sistema devuelve: N/A

---

## SOLUCIÓN PROPUESTA v6.5.03

### Patrón Corregido
```python
# ANTES (v6.5.02):
r'(?i)p16\s+presenta\s+marcaci[óo]n\s+[^(]+\((?:positivo|negativo)\)'

# DESPUÉS (v6.5.03):
r'(?i)p16\s+presenta\s+marcaci[óo]n\s+[^(]+\((positivo|negativo)\)'
#                                               ^               ^
#                                               Capturing group (extrae valor)
```

**Cambio:** Remover `?:` del grupo para convertirlo en capturing group.

### Resultado Esperado
1. Patrón hace match: ✅ SI
2. Grupo de captura extrae: `"negativo"` (group(1))
3. Sistema normaliza: `"negativo"` → `"NEGATIVO"`
4. Sistema devuelve: `"NEGATIVO"`

---

## KI-67: ANÁLISIS SEPARADO

### Texto en OCR
```
Ki67 presenta marcación de celularidad de membrana basal (marcación usual)
```

### Valor Actual en BD
```
IHQ_KI-67: "POSITIVO (KI67 PRESENTA MARCACIÓN DE CELULARIDAD DE MEMBRANA BASAL (MARCACIÓN USUAL))"
```

**Estado:** ✅ Ki-67 SÍ se extrajo (por patrón existente más amplio)
**Problema:** El valor incluye texto descriptivo completo en vez de normalizar

### Interpretación Clínica Correcta
- **"marcación basal usual"** = Patrón normal benigno en tejido cervical
- **Valor esperado:** `"NEGATIVO"` o `"NEGATIVO (marcación basal normal)"`

**PERO:** El sistema actual ya tiene normalización para esto en línea 916-917:
```python
'presenta marcación de celularidad de membrana basal (marcación usual)': 'NEGATIVO (marcación basal)',
```

**Problema:** Esa entrada NO se está aplicando porque el valor extraído es MAYÚSCULAS y con prefijo.

---

## SOLUCIÓN COMPLETA v6.5.03

### 1. Corregir Patrón P16 (línea 1064)
```python
# Remover ?: del grupo
r'(?i)p16\s+presenta\s+marcaci[óo]n\s+[^(]+\((positivo|negativo)\)'
```

### 2. Mejorar Normalización Ki-67 (después línea 917)
```python
# Agregar variantes en mayúsculas y con prefijo
'ki67 presenta marcación de celularidad de membrana basal (marcación usual)': 'NEGATIVO (marcación basal)',
'ki-67 presenta marcación de celularidad de membrana basal (marcación usual)': 'NEGATIVO (marcación basal)',
# Variantes con uppercase
'KI67 PRESENTA MARCACIÓN DE CELULARIDAD DE MEMBRANA BASAL (MARCACIÓN USUAL)': 'NEGATIVO (marcación basal)',
'KI-67 PRESENTA MARCACIÓN DE CELULARIDAD DE MEMBRANA BASAL (MARCACIÓN USUAL)': 'NEGATIVO (marcación basal)',
```

---

## IMPACTO ESPERADO

### P16
- **Antes:** N/A (no extraído)
- **Después:** NEGATIVO ✅

### Ki-67
- **Antes:** POSITIVO (KI67 PRESENTA MARCACIÓN...)
- **Después:** NEGATIVO (marcación basal) ✅

### Score Caso
- **Antes:** 77.8% (1 error: DIAGNOSTICO_COLORACION)
- **Después:** 88.9% (P16 y Ki-67 correctos, solo DIAGNOSTICO_COLORACION pendiente)

---

## VALIDACIÓN ANTI-REGRESIÓN

### Casos de Referencia a Validar
- **IHQ250229:** Caso actual (score: 77.8% → 88.9%)
- **IHQ250167:** Caso con "sin sobreexpresión de p16" (debe seguir NEGATIVO)
- **IHQ251027:** Caso con "NO presentan inmunoreactividad a P16" (debe seguir NEGATIVO)
- **IHQ251026:** Caso con "No hay marcación en la muestra para p16" (debe seguir NEGATIVO)
- **IHQ251010:** Caso con "POSITIVO PARA SOBREEXPRESIÓN DE P16" (debe seguir POSITIVO)

---

## PRÓXIMO PASO

**USUARIO:** ¿Aplicar corrección v6.5.03?

Si aprueba:
1. Modificar línea 1064 (remover ?: del grupo P16)
2. Agregar normalizaciones Ki-67 uppercase (después línea 917)
3. Reprocesar IHQ250229 (FUNC-06)
4. Validar 5 casos de referencia
5. Comparar scores (antes/después)

