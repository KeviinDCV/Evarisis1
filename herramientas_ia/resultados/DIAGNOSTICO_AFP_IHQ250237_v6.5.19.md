# DIAGNOSTICO: IHQ250237 - AFP y CD30 No Se Extrajeron Correctamente

## Contexto
- **Caso:** IHQ250237
- **Versión:** v6.5.19
- **Modificación:** Terminador del patrón "es negativo para [lista]" corregido
- **Problema:** Cambio no tuvo efecto - AFP y CD30 siguen incorrectos

## Estado Actual (Después de Reprocesamiento)

### Biomarcadores en BD:
- **IHQ_AFP:** POSITIVO ❌ (debería ser NEGATIVO)
- **IHQ_CD30:** NO EXISTE ❌ (no se extrajo, debería ser NEGATIVO)
- **IHQ_GLIPICAN:** NEGATIVO ✅ (correcto)
- **IHQ_GPC3:** NEGATIVO ✅ (correcto)

### Score: 88.9% (Baja por WARNING en DIAGNOSTICO_COLORACION, no por biomarcadores)

## Texto Original en OCR

```
es positivo focal para CKAE1/E3 y es negativo para GLYPICAN 3, AFP y CD 30.
```

**Interpretación correcta:**
- CKAE1/E3: POSITIVO
- GLYPICAN 3: NEGATIVO
- AFP: NEGATIVO
- CD 30: NEGATIVO

## Análisis del Patrón V6.5.19

**Patrón implementado (línea 8688):**
```regex
r'(?i)(?:es|son)\s+negativ[ao]s?\s+para\s+([A-Za-z0-9\s,./\-\(\)+yYeÉóÓ\n]+)(?:\.|\s*$)'
```

**Comentario:**
```python
# V6.5.18 FIX IHQ250237: PRIORIDAD MÁXIMA - "es negativo para [lista]"
# V6.5.19 FIX: Terminador corregido para capturar lista completa con " y "
# Formato: "es positivo focal para CKAE1/E3 y es negativo para GLYPICAN 3, AFP y CD 30"
# → GLYPICAN3=NEGATIVO, AFP=NEGATIVO, CD30=NEGATIVO
# DEBE IR ANTES del patrón genérico para capturar correctamente el contexto "es"
# Terminador: solo punto o fin de texto (NO " y " que es parte de la lista)
```

## Prueba del Patrón

**Resultado de captura:**
```
Match completo: "es negativo para GLYPICAN 3, AFP y CD 30."
Grupo 1: "GLYPICAN 3, AFP y CD 30."
Estado detectado: NEGATIVO (correcto)
Items parseados: ['GLYPICAN 3', 'AFP', 'CD 30.']
```

**Problemas detectados:**
1. ✅ Patrón captura correctamente
2. ✅ Estado NEGATIVO detectado correctamente
3. ❌ Punto final incluido en "CD 30." (problema menor de parsing)
4. ❌ AFP se extrae como POSITIVO en BD (PROBLEMA CRÍTICO)
5. ❌ CD30 NO se extrae en absoluto (PROBLEMA CRÍTICO)

## Causa Raíz Sospechada

### Hipótesis 1: Prioridad de Patrones
El patrón negativo (línea 8688) está en la posición correcta (ANTES del genérico), pero hay OTRO patrón positivo que está capturando AFP antes.

**Patrón sospechoso (línea 8720):**
```regex
r'(?:son\s+)?positivas?\s+para\s+((?:(?!siendo\s+negativ[oa]s?|son\s+negativ[oa]s?|y\s+es\s+negativ[oa]s?|y\s+negativ[oa]s?|,\s*negativ[oa]s?)[\w\s,./\-\(\)+yYeÉóÓ\n])+?)(?=\s+y\s+c[eé]lulas|\.|$|,\s*(?:son|siendo)?\s*negativ[ao]s?)'
```

Este patrón tiene un **lookahead negativo** `(?!...y\s+es\s+negativ[oa]s?...)` que DEBERÍA evitar capturar cuando viene "y es negativo", pero podría no estar funcionando correctamente.

### Hipótesis 2: Overwriting de Valores
El patrón negativo se ejecuta y asigna correctamente AFP=NEGATIVO, pero luego otro patrón lo sobrescribe con POSITIVO.

## Estado del Patrón en Código

**Ubicación:** `core/extractors/biomarker_extractor.py` línea 8682-8688

**Posición en lista:** CORRECTA (antes del genérico línea 8691)

**Lógica de detección de estado (líneas 8775-8779):**
```python
match_full = match.group(0).upper()
if 'NO SE DETECTA' in match_full or 'NEGATIV' in match_full or 'NO SE OBSERVA' in match_full:
    estado_defecto = 'NEGATIVO'
else:
    estado_defecto = 'POSITIVO'
```
✅ Esta lógica es correcta y detectaría 'NEGATIV' correctamente.

## Siguientes Pasos de Diagnóstico

### 1. Verificar si hay un patrón positivo capturando antes
Buscar patrones que coincidan con "positivo focal para" o "positivo para" que estén ANTES de línea 8688.

### 2. Agregar logging detallado
Modificar temporalmente `biomarker_extractor.py` para imprimir:
- Qué patrón captura cada biomarcador
- Valor asignado por cada patrón
- Si hay sobrescrituras

### 3. Verificar orden de procesamiento
Confirmar que los patrones se evalúan en el orden esperado:
1. Patrón V6.5.19 (negativo para [lista]) - línea 8688
2. Patrón genérico (negativo para) - línea 8691
3. Patrones positivos - líneas 8713+

## Recomendación Inmediata

**ESTRATEGIA:** Agregar patrón de mayor prioridad que capture el contexto completo.

**Ubicación sugerida:** Antes de línea 8682 (PRIORIDAD MÁXIMA ABSOLUTA)

**Nuevo patrón propuesto:**
```regex
# V6.5.20 FIX IHQ250237: PRIORIDAD ABSOLUTA - Contexto mixto "positivo para X y es negativo para Y,Z,W"
# Formato: "es positivo focal para CKAE1/E3 y es negativo para GLYPICAN 3, AFP y CD 30"
# CAPTURA TODO EL CONTEXTO para evitar interferencia de patrones posteriores
r'(?i)(?:es|son)\s+positiv[ao]s?\s+(?:focal\s+)?para\s+([A-Za-z0-9\s,./\-\(\)]+?)\s+y\s+(?:es|son)\s+negativ[ao]s?\s+para\s+([A-Za-z0-9\s,./\-\(\)+yYeÉóÓ\n]+)(?:\.|\s*$)'
```

**Grupos de captura:**
- Grupo 1: Biomarcadores POSITIVOS (ej: "CKAE1/E3")
- Grupo 2: Biomarcadores NEGATIVOS (ej: "GLYPICAN 3, AFP y CD 30")

**Lógica de procesamiento:**
1. Capturar grupo 1 → marcar como POSITIVO
2. Capturar grupo 2 → parsear lista → marcar cada uno como NEGATIVO

**Ventaja:** Captura el contexto completo en un solo match, evitando que otros patrones interfieran.

## Resumen

| Biomarcador | Estado Actual | Estado Esperado | ¿Correcto? |
|-------------|---------------|-----------------|------------|
| CKAE1/E3    | ?             | POSITIVO        | ?          |
| GLIPICAN    | NEGATIVO      | NEGATIVO        | ✅          |
| GPC3        | NEGATIVO      | NEGATIVO        | ✅          |
| AFP         | POSITIVO      | NEGATIVO        | ❌          |
| CD30        | NO EXISTE     | NEGATIVO        | ❌          |

**Conclusión:** El patrón v6.5.19 captura correctamente el texto, pero hay un problema en la prioridad de patrones o en el procesamiento posterior que causa que AFP se marque como POSITIVO y CD30 no se extraiga.
