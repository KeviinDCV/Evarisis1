# REPORTE FUNC-06: Reprocesamiento IHQ250268 v6.5.78
## Estado: FALLIDO - CK34BETAE12 sigue sin extraerse

### RESUMEN EJECUTIVO

**Caso:** IHQ250268
**Versión:** 6.5.78 (corrección de CK34BETAE12)
**Resultado:** FALLO - Score sigue en 88.9%

### COMPARACIÓN ANTES/DESPUÉS

| Métrica | ANTES (v6.5.77) | DESPUÉS (v6.5.78) | CAMBIO |
|---------|------------------|-------------------|---------|
| Score | 88.9% | 88.9% | ❌ Sin cambio |
| IHQ_CK34BETAE12 | NO EXTRAÍDO | NO EXTRAÍDO | ❌ Sin cambio |
| IHQ_P63 | NO MENCIONADO | NO MENCIONADO | ⚠️ También falta |
| IHQ_RACEMASA | POSITIVO | POSITIVO | ✅ OK |

### CAUSA RAÍZ

**Problema identificado:** Patrón regex NO captura "CK34BETA" sin "E12"

**OCR dice:**
```
...pierden expresión de células basales (p63 y CK34BETA negativos)...
```

**Patrón actual (línea 1799):**
```python
r'(?i)ck[^\w]*34[^\w]*beta[^\w]*e[^\w]*12[:\s]*(positiv[oa]|negativ[oa])'
```

**Por qué falla:**
- El patrón requiere `e[^\w]*12` después de `beta`
- El OCR tiene "CK34BETA negativos" (sin E12)
- No hay match

### ANÁLISIS DE VARIANTES EN OCR

**En estudios solicitados:**
```
p63, 34BetaE12 y racemasa
```

**En resultados:**
```
p63 y CK34BETA negativos
```

Hay **DOS variantes diferentes** del mismo biomarcador en el mismo PDF:
1. "34BetaE12" (con E12, sin CK)
2. "CK34BETA" (con CK, sin E12)

### CORRECCIÓN NECESARIA

Agregar patrón que capture "CK34BETA" sin el "E12" obligatorio:

```python
# V6.5.79 FIX IHQ250268: Capturar "CK34BETA" sin E12 obligatorio
r'(?i)ck[^\w]*34[^\w]*beta(?:[^\w]*e[^\w]*12)?[:\s]*(positiv[oa]s?|negativ[oa]s?)',
```

**Cambio clave:** `(?:[^\w]*e[^\w]*12)?` hace E12 opcional.

**ADEMÁS, debe capturar plurales:** `(positiv[oa]s?|negativ[oa]s?)`

### PROBLEMA ADICIONAL: P63

IHQ_P63 también está "NO MENCIONADO" pero aparece en OCR:
```
...pierden expresión de células basales (p63 y CK34BETA negativos)...
```

Necesita patrón similar para capturar formato narrativo.

### SIGUIENTE PASO

1. Modificar biomarker_extractor.py línea ~1799
2. Agregar patrón con E12 opcional
3. Agregar captura de plurales
4. Reprocesar IHQ250268 con FUNC-06
5. Validar score = 100%

