# ANÁLISIS REPROCESAMIENTO IHQ250162 - Patrón v6.4.23

## FECHA
2026-01-07 22:47:00

## ESTADO DEL REPROCESAMIENTO
- ✅ PDF reprocesado correctamente (50 casos)
- ✅ Debug_map generado: debug_map_IHQ250162_20260107_224652.json
- ⚠️ Score final: 77.8% (ADVERTENCIA)

## PROBLEMA DETECTADO
El patrón v6.4.23 "No presentan expresión para" NO está sobrescribiendo valores incorrectos.

### Valores Actuales en BD (INCORRECTOS)
```
IHQ_CALRETININA            = POSITIVO (focal)   ❌ DEBERÍA SER: NEGATIVO
IHQ_DESMIN                 = NEGATIVO           ✅ CORRECTO
IHQ_SMA                    = NO MENCIONADO      ❌ DEBERÍA SER: NEGATIVO
IHQ_EMA                    = NEGATIVO           ✅ CORRECTO
IHQ_RECEPTOR_PROGESTERONA  = NEGATIVO           ✅ CORRECTO
IHQ_CD34                   = NEGATIVO           ✅ CORRECTO
IHQ_GFAP                   = NO MENCIONADO      ❌ DEBERÍA SER: NEGATIVO
IHQ_P53                    = NEGATIVO           ✅ CORRECTO
```

### Valores Esperados (Según OCR)
El PDF dice claramente:
```
"No presentan expresión para calretinina, desmina, SMA, EMA, progesterona, CD34, GFAP, p53."
```

TODOS los 8 biomarcadores deberían ser **NEGATIVO**.

## ANÁLISIS TÉCNICO

### 1. ¿El patrón v6.4.23 está en el código?
✅ **SÍ** - Ubicación: `core/extractors/biomarker_extractor.py` líneas 5483-5511

### 2. ¿El patrón regex funciona?
✅ **SÍ** - Probado manualmente, detecta correctamente los 8 biomarcadores

### 3. ¿La función se llama desde unified_extractor?
✅ **SÍ** - `extract_narrative_biomarkers()` se llama en línea 701

### 4. ¿El patrón se ejecutó durante el reprocesamiento?
❌ **NO** - No hay mensajes de log `[V6.4.23 PASE FINAL - No presentan expresión]`

## CAUSA RAÍZ PROBABLE

El patrón v6.4.23 está en `extract_narrative_biomarkers()` pero:

1. **HIPÓTESIS 1**: El patrón NO está coincidiendo por problema de encoding (ó vs o)
   - Regex usa: `expresi[óo]n`
   - OCR tiene: "expresión" (con ó)
   - ✅ Regex debería funcionar

2. **HIPÓTESIS 2**: El patrón NO se ejecuta porque hay un `return` temprano
   - ✅ Verificado: `return results` está en línea 5512 (DESPUÉS del patrón)
   
3. **HIPÓTESIS 3**: La función `extract_narrative_biomarkers()` NO recibe el texto correcto
   - Se llama con `clean_text` en línea 701
   - ¿`clean_text` contiene la sección DESCRIPCIÓN MICROSCÓPICA?

4. **HIPÓTESIS 4**: Hay MERGE posterior que sobrescribe los valores
   - Después de `extract_narrative_biomarkers()` retorna results
   - unified_extractor hace merge con otros biomarcadores
   - ¿El merge está sobrescribiendo valores NEGATIVOS con "POSITIVO (focal)"?

## SIGUIENTE PASO REQUERIDO

Necesito verificar:
1. ¿Qué contiene `clean_text` cuando se llama `extract_narrative_biomarkers()`?
2. ¿Los logs del procesamiento muestran ejecución del patrón v6.4.23?
3. ¿Hay merge posterior que sobrescriba valores?

## SOLUCIÓN PROPUESTA

Si el problema es MERGE posterior:
- Agregar el patrón v6.4.23 TAMBIÉN en `extract_narrative_biomarkers_list()` (línea ~6863)
- O hacer que el MERGE priorice valores NEGATIVOS sobre valores incorrectos

## REPORTE CONSOLIDADO
- Caso: IHQ250162
- Score: 77.8% (5/8 biomarcadores NEGATIVOS correctos)
- Biomarcadores incorrectos: 3 (CALRETININA, SMA, GFAP)
- Motivo: Patrón v6.4.23 NO sobrescribe valores previos incorrectos
