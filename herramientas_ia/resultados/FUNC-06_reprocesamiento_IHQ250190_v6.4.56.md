# FUNC-06: Reprocesamiento IHQ250190 con v6.4.56

## RESUMEN EJECUTIVO

**Estado:** FALLIDO - Persistencia del problema
**Score final:** 100% (pero con valores incorrectos)
**Versión probada:** v6.4.56 (terminador simplificado)

## VALORES EN OCR (FUENTE DE VERDAD)

```
"Presentan positividad fuerte para CD56, DESMINA, MYOGENINA y Myo D1."
```

## VALORES EXTRAÍDOS EN BD

| Biomarcador | Valor Esperado | Valor Actual | Estado |
|-------------|---------------|--------------|--------|
| IHQ_CD56 | POSITIVO (fuerte) | POSITIVO | OK |
| IHQ_DESMIN | POSITIVO (fuerte) | NEGATIVO | ERROR |
| IHQ_MYOGENIN | POSITIVO (fuerte) | NEGATIVO | ERROR |
| IHQ_MYOD1 | POSITIVO (fuerte) | POSITIVO (fuerte) | OK |

## ANÁLISIS DEL PROBLEMA

La corrección v6.4.56 del terminador simplificado NO resolvió el problema.

**Razón:**
El problema NO está en el terminador. El problema está en el patrón de captura que extrae "Presentan positividad fuerte para".

**Patrón actual en biomarker_extractor.py (línea ~2390):**
```python
# V6.4.53 FIX IHQ250190: Patrón "Presentan positividad fuerte para"
r'(?i)presentan?\s+positividad\s+(?:(?:muy\s+)?fuerte|moderada?|(?:muy\s+)?débil|focal(?:es)?|intensa|difusa?|variable|heterogénea?|extensa|focales?|leve)\s+para\s+([A-Z][A-Za-z0-9/-]+(?:\s+[A-Z][A-Za-z0-9/-]+)*)\.(?:\s+[A-Z]|$)',
```

**Problema identificado:**
El terminador `\.(?:\s+[A-Z]|$)` hace que la captura termine en el primer punto seguido de mayúscula. Pero en el texto:

```
"Presentan positividad fuerte para CD56, DESMINA, MYOGENINA y Myo D1. Presenta positividad focal..."
```

La captura termina ANTES de capturar todos los biomarcadores de la lista.

## SOLUCIÓN PROPUESTA

El patrón debe capturar HASTA el punto que termina la frase, NO hasta el primer punto + mayúscula.

**Cambio necesario en biomarker_extractor.py línea ~2390:**

```python
# V6.4.57 FIX IHQ250190: Capturar lista completa de biomarcadores
# PROBLEMA: Terminador `\.(?:\s+[A-Z]|$)` corta lista prematuramente
# SOLUCIÓN: Capturar hasta punto + (espacio + verbo_inicio_nueva_frase | fin)
r'(?i)presentan?\s+positividad\s+(?:(?:muy\s+)?fuerte|moderada?|(?:muy\s+)?débil|focal(?:es)?|intensa|difusa?|variable|heterogénea?|extensa|focales?|leve)\s+para\s+([^\.]+)\.',
```

**Explicación:**
- `[^\.]+` captura TODO hasta el primer punto (incluye "CD56, DESMINA, MYOGENINA y Myo D1")
- `\.` termina en el punto final de la frase
- NO necesitamos terminador complejo, simplemente capturar hasta el punto

## PRÓXIMO PASO

1. Modificar biomarker_extractor.py línea ~2390
2. Cambiar terminador de `\.(?:\s+[A-Z]|$)` a simple `\.`
3. Ejecutar FUNC-06 nuevamente
4. Validar que ahora extraiga DESMIN y MYOGENIN correctamente

