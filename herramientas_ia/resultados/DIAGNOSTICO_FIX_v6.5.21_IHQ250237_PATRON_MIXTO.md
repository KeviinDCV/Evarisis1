# DIAGNOSTICO v6.5.21 - IHQ250237 Patron Mixto NO Funciono

## Contexto
- Caso: IHQ250237
- Modificacion v6.5.20: Patron de contexto mixto "positivo para X y es negativo para Y,Z,W"
- Ubicacion: `core/extractors/biomarker_extractor.py` linea 8563

## Texto Real en OCR
```
"es positivo focal para CKAE1/E3 y es negativo para GLYPICAN 3, AFP y CD 30"
```

## Patron Actual (v6.5.20 - linea 8563)
```python
r'(?i)(?:es|son)\s+positiv[ao]s?\s+(?:focal|difuso|difusa|fuerte|d[eé]bil|moderado|moderada)?\s*para\s+([A-Za-z0-9\s,./\-\(\)]+?)\s+y\s+(?:es|son)\s+negativ[ao]s?\s+para\s+([A-Za-z0-9\s,./\-\(\)+yYeÉóÓ\n]+)(?:\.|\s*$)'
```

## Problemas Detectados

### 1. Espaciado del Modificador
**Patron actual:**
```
positiv[ao]s?\s+(?:focal|...)?para
```

**Problema:** Espera espacio DESPUES de "positivo" pero el modificador es opcional.

**Secuencia esperada:**
- `positivo` + espacio obligatorio + `(?:focal)?` + espacio opcional + `para`

**Secuencia real:**
- `positivo` + espacio + `focal` + espacio + `para`

**Resultado:** El patron NO matchea cuando hay modificador con espacio.

### 2. Normalizacion CKAE1/E3 → IHQ_CKAE1AE3
**Problema:** El patron captura "CKAE1/E3" pero la columna BD es "IHQ_CKAE1AE3" (sin barra).

**Mapeo actual en validation_checker.py:**
```python
'CKAE1AE3': 'IHQ_CKAE1AE3',
'CK AE1AE3': 'IHQ_CKAE1AE3',
'CK AE1/AE3': 'IHQ_CKAE1AE3',
```

**Falta:**
```python
'CKAE1/E3': 'IHQ_CKAE1AE3',  # Formato con barra
```

### 3. Procesamiento Especial No Ejecutado
**Codigo esperado (linea ~8766):**
```python
# V6.5.20 FIX IHQ250237: Manejo especial para patron de contexto mixto (2 grupos: POSITIVOS y NEGATIVOS)
```

**Problema:** Si el patron NO matchea, el codigo especial nunca se ejecuta.

## Estado Actual vs Esperado

| Biomarcador | Estado Actual | Estado Esperado |
|-------------|---------------|-----------------|
| IHQ_CKAE1AE3 | NO EXISTE | POSITIVO FOCAL |
| IHQ_AFP | POSITIVO | NEGATIVO |
| IHQ_CD30 | NO EXISTE | NEGATIVO |
| IHQ_GLIPICAN | NEGATIVO ✅ | NEGATIVO ✅ |
| IHQ_GPC3 | NEGATIVO ✅ | NEGATIVO ✅ |

**Resultado:** AFP se extrajo con patron individual como POSITIVO (incorrecto), y CKAE1AE3/CD30 no se extrajeron.

## Solucion Propuesta v6.5.21

### Fix 1: Corregir Patron con Espaciado Flexible
```python
# Cambiar:
r'(?i)(?:es|son)\s+positiv[ao]s?\s+(?:focal|difuso|difusa|fuerte|d[eé]bil|moderado|moderada)?\s*para'

# Por (espacios flexibles con \s*):
r'(?i)(?:es|son)\s+positiv[ao]s?\s*(?:focal|difuso|difusa|fuerte|d[eé]bil|moderado|moderada)?\s*para'
```

**Explicacion:**
- `\s+` despues de "positivo" → `\s*` (0 o mas espacios)
- `\s*` despues del modificador → mantener (0 o mas espacios)
- Permite "positivo focal para" o "positivofocal para" o "positivo para"

### Fix 2: Agregar Alias CKAE1/E3 en validation_checker.py
```python
# En MAPEO_BIOMARCADORES:
'CKAE1/E3': 'IHQ_CKAE1AE3',  # V6.5.21 FIX IHQ250237: Formato con barra
'CKAE1/AE3': 'IHQ_CKAE1AE3',
'CK AE1/E3': 'IHQ_CKAE1AE3',
```

### Fix 3: Validar Procesamiento Especial
**Verificar que codigo en linea ~8766 se ejecute correctamente cuando patron matchee.**

## Validacion Requerida

### Casos de Referencia para Validar Regresion
**ANTES de aplicar fix, auditar estos casos:**
```bash
# Casos que usan patron mixto (buscar en otros casos procesados)
# Por ahora solo IHQ250237 conocido
```

### Despues de Aplicar Fix
1. Modificar patron en linea 8563
2. Agregar aliases en validation_checker.py
3. Reprocesar IHQ250237 con FUNC-06
4. Auditar con FUNC-01
5. Validar:
   - IHQ_CKAE1AE3 = POSITIVO FOCAL
   - IHQ_AFP = NEGATIVO
   - IHQ_CD30 = NEGATIVO
   - IHQ_GLIPICAN = NEGATIVO (mantener)
   - IHQ_GPC3 = NEGATIVO (mantener)
   - Score = 100%

## Impacto Esperado
- Score actual: 88.9%
- Score esperado: 100%
- Mejora: +11.1%

## Fecha
2026-01-28

## Version
v6.5.21 (propuesta)
