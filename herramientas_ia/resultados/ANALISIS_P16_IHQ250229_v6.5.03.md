# ANÁLISIS: P16 IHQ250229 - Problema de Extracción en Auditor

## Caso
- IHQ250229
- Versión: v6.5.03
- Fecha: 2026-01-28

## Problema Reportado

El auditor reporta que `IHQ_P16_ESTADO = "NEGATIVO"` (extraído correctamente) NO coincide con OCR que dice `valor_ocr = "p"` (truncado incorrectamente).

## Investigación

### 1. Valor Extraído (CORRECTO)
```
IHQ_P16_ESTADO: "NEGATIVO"
```

**Fuente:** `debug_map_IHQ250229_20260128_043942.json` línea BD

### 2. Contexto en OCR (CORRECTO)
```
Línea 36: P16 presenta marcación citoplasmática focal (negativo)
```

### 3. Valor que el Auditor Detecta (INCORRECTO)
```json
{
  "biomarcador": "P16",
  "columna": "IHQ_P16_ESTADO",
  "valor_bd": "NEGATIVO",
  "valor_ocr": "p"  ← TRUNCADO INCORRECTAMENTE
}
```

## Causa Raíz

El problema NO es del **extractor** (biomarker_extractor.py v6.5.03), sino del **auditor** (auditor_sistema.py).

### Patrón Problemático en Auditor

**Archivo:** `herramientas_ia/auditor_sistema.py`
**Método:** `_extraer_valor_biomarcador_desde_ocr()` línea 2586-2689
**Patrón genérico:** línea 2645

```python
# Patrón genérico (último fallback):
r'{bio}[:\s]+(?!y\s)([^\.\n,]+?)(?:\s+y\s+\w+)?'
```

**Problema:**
- Usa `[^\.\n,]+?` (modo non-greedy)
- Captura muy poco texto (puede ser solo 1 carácter)
- No tiene patrón específico para "presenta marcación ... (negativo)"

### Por Qué Captura Solo "p"

El texto en OCR es:
```
P16 presenta marcación citoplasmática focal (negativo)
```

El patrón `P16[:\s]+(?!y\s)([^\.\n,]+?)` hace match y captura:
- `[:\s]+` → coincide con el espacio después de "P16"
- `([^\.\n,]+?)` → captura "presenta" (modo non-greedy)
- Pero el código en línea 2673 hace `match.group(1).strip()` que retorna "presenta"
- Sin embargo, el JSON muestra "p" → probablemente el código está truncando en algún lugar

**Necesito verificar si hay truncamiento adicional.**

## Solución Propuesta

### Opción 1: Agregar Patrón Específico para P16 en Auditor

Agregar ANTES del patrón genérico (línea 2615):

```python
# V6.5.03 FIX IHQ250229: Patrón específico para P16
# Formato: "P16 presenta marcación ... (negativo)" o "P16 presenta ... (positivo)"
r'{bio}\s+presenta\s+marcaci[oó]n\s+[^(]+\((?:positivo|negativo)\)',
```

Este patrón captura el valor dentro del paréntesis.

### Opción 2: Mejorar Patrón Genérico

Cambiar línea 2645:

```python
# ANTES (non-greedy, puede capturar muy poco):
r'{bio}[:\s]+(?!y\s)([^\.\n,]+?)(?:\s+y\s+\w+)?'

# DESPUÉS (captura hasta encontrar delimitador claro):
r'{bio}[:\s]+(?!y\s)([^\.\n,]{3,})(?:\s+y\s+\w+)?'
#                                  ^^^ mínimo 3 caracteres
```

### Opción 3: No Hacer Nada (Aceptar como Válido)

Modificar la lógica de validación en línea 2057-2058 para aceptar `"p"` como abreviatura válida de "presenta" en contextos de P16.

```python
# 3. Ambos indican negatividad (incluyendo "p" como abreviatura de "presenta")
elif ('NEGATIV' in valor_bd_norm and 'NEGATIV' in valor_ocr_norm):
    valores_validos = True
elif ('NEGATIV' in valor_bd_norm and valor_ocr_norm in ['P', 'PRESENTA']):
    # P16 específico: "presenta" truncado o abreviado
    valores_validos = True
```

## Recomendación

**Opción 1** es la mejor solución porque:
- Soluciona el problema específico de P16
- No afecta otros biomarcadores
- Sigue el patrón de prioridad de patrones específicos antes de genéricos
- Es consistente con la filosofía de no modificar patrones genéricos

## Impacto

**Score actual:** 66.7% (6/9 validaciones OK)
**Score esperado después del fix:** 77.8% (7/9 validaciones OK)

**Validación que fallará aún:**
- DIAGNOSTICO_COLORACION: ERROR (marcado como "NO APLICA" pero existe en OCR)

## Próximos Pasos

1. Aplicar fix Opción 1 en `auditor_sistema.py` línea ~2615
2. NO reprocesar caso (no es necesario, extractor ya funciona)
3. Re-auditar con `--inteligente` para validar fix
4. Verificar score mejora de 66.7% → 77.8%

---

**Conclusión:** El extractor v6.5.03 está funcionando **correctamente**. El problema es del **auditor** que trunca incorrectamente el valor al validar contra OCR.
