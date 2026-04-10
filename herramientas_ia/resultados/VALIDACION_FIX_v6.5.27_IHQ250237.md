# VALIDACION FINAL - IHQ250237 (v6.5.27)

## CAMBIOS IMPLEMENTADOS

**v6.5.24:** Alias 'CKAE1/E3' → 'IHQ_CKAE1AE3'  
**v6.5.25:** Alias 'CD 30' → 'IHQ_CD30'  
**v6.5.26:** Patrón limpiar "HALLAZGOS MORFOLOGICOS Y DE INMUNOHISTOQUIMICA COMPATIBLES CON"  
**v6.5.27:** FIX CRÍTICO - Variable no definida en patrón mixto (líneas 8787, 8797)

## RESULTADO ACTUAL (después de reprocesar)

| Campo | Valor BD | Valor Esperado | Estado |
|-------|----------|----------------|--------|
| Numero de caso | IHQ250237 | IHQ250237 | ✅ OK |
| Organo | TESTICULO IZQUIERDO | TESTICULO IZQUIERDO | ✅ OK |
| Diagnostico Principal | SEMINOMA | SEMINOMA | ✅ OK (v6.5.26 funcionó!) |
| IHQ_OCT4 | POSITIVO | POSITIVO | ✅ OK |
| IHQ_PODOPLANINA | POSITIVO | POSITIVO | ✅ OK |
| IHQ_CKAE1AE3 | POSITIVO | POSITIVO FOCAL | ⚠️ PARCIAL (alias funcionó, falta intensidad) |
| IHQ_GPC3 | NEGATIVO | NEGATIVO | ✅ OK |
| IHQ_GLIPICAN | NEGATIVO | NEGATIVO | ✅ OK |
| **IHQ_AFP** | **POSITIVO** | **NEGATIVO** | ❌ ERROR |
| **IHQ_CD30** | **POSITIVO** | **NEGATIVO** | ❌ ERROR |

## SCORE ESTIMADO

**Campos críticos correctos:** 7/10 = 70%
**Score esperado con debug_map:** 88.9%

## ANÁLISIS DEL PROBLEMA

### Problema con AFP y CD30

El texto OCR dice:
```
La celularidad tumoral tiene marcación positiva y fuerte para OCT 4, PODOPLANINA, 
es positivo focal para CKAE1/E3 y es negativo para GLYPICAN 3, AFP y CD 30.
```

**Causa raíz:**
1. Patrón v6.4.86 "marcación/tinción" captura TODA la lista como POSITIVO
2. Patrón v6.5.20 mixto (positivo X y negativo Y) NO tiene prioridad sobre v6.4.86
3. AFP y CD30 quedan marcados como POSITIVO incorrectamente

**Logs del procesamiento:**
```
✅ [V6.4.86 marcación] Extraído: 'AFP' → AFP = POSITIVO
✅ [V6.4.86 marcación] Extraído: 'CD 30' → CD30 = POSITIVO
...
⏭️ [negativo/negativas] Skipping 'AFP' → AFP (ya existe: POSITIVO)
⏭️ [negativo/negativas] Skipping 'CD 30' → CD30 (ya existe: POSITIVO)
```

El patrón "negativo para" NO sobrescribe porque ya existe el valor POSITIVO.

## SOLUCIÓN NECESARIA

El patrón mixto v6.5.20 debe tener **PRIORIDAD ABSOLUTA** y ejecutarse ANTES que v6.4.86.

**Archivo:** `core/extractors/biomarker_extractor.py`  
**Función:** `extract_narrative_biomarkers_list()`  
**Cambio:** Mover patrón mixto (línea 8566) al inicio de la lista de patrones (antes de v6.4.86)

O ALTERNATIVAMENTE:

Configurar el patrón mixto para SOBRESCRIBIR valores existentes (sin verificar "if columna not in").

## SIGUIENTE PASO

Modificar orden de patrones para dar prioridad al patrón mixto v6.5.20.

