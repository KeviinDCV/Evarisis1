# TEXTO VERIFICADO DEL PDF - IHQ250984

**Fecha:** 2025-10-24 09:56:00
**Fuente:** Búsqueda directa en texto OCR almacenado en BD

---

## ESTUDIOS SOLICITADOS (Confirmado)

```
Se realizó tinción especial para GATA 3, RECEPTOR DE ESTROGENOS, RECEPTOR DE
PROGESTERONA, HER 2, Ki 67, SOX10.
```

**Estado actual en BD:**
- `IHQ_ESTUDIOS_SOLICITADOS: "HER2, Receptor de Estrógeno"` ❌ (solo 2/6)

**Esperado:**
- `IHQ_ESTUDIOS_SOLICITADOS: "GATA 3, RECEPTOR DE ESTROGENOS, RECEPTOR DE PROGESTERONA, HER 2, Ki 67, SOX10"` ✅ (6/6)

---

## DESCRIPCIÓN MICROSCÓPICA - BLOQUE DE BIOMARCADORES (Confirmado)

```
negativas para SXO10.
-RECEPTOR DE ESTROGENOS: Negativo.
-RECEPTOR DE PROGRESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 % de las células tumorales.
-Ki-67: Tinción nuclear en el 60% de las células tumorales.
```

**NOTA CRÍTICA:**
- Hay un typo en el PDF: `"SXO10"` (debería ser `"SOX10"`)
- Los extractores deben capturar AMBAS variantes

---

## GATA3 - FORMATO NARRATIVO (Confirmado)

```
[Las células tumorales] tienen una tinción nuclear positiva fuerte y difusa para GATA 3. Son [negativas para SXO10].
```

**Estado actual en BD:**
- `IHQ_GATA3: N/A` ❌

**Esperado:**
- `IHQ_GATA3: Positivo` ✅

---

## CLASIFICACIÓN MOLECULAR (Confirmado)

```
CLASIFICACIÓN MOLECULAR: HER 2 POSITIVO.
```

**Estado actual en BD:**
- `IHQ_HER2: /NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT MONOCLONAL ANTIBOD...` ❌ (parcial, solo anticuerpo)

**Esperado:**
- `IHQ_HER2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100%` ✅

---

## ANTICUERPOS UTILIZADOS (Confirmado)

```
RECEPTOR DE ESTROGENOS (SP1) Rabbit Monoclonal Primary Antibody. VENTANA Ref. 790-2223.
Her2/Neu: PATHWAY anti-HER-2/Neu (4B5) Rabbit Monoclonal Antibody. VENTANA Ref. 790-4493.
Ki67: anti-Ki67 (30-9) Rabbit Monoclonal Primary Antibody. VENTANA Ref. 790-4286.
```

---

## RESUMEN DE EXTRACCIÓN ACTUAL VS ESPERADA

| Biomarcador | Valor en PDF | Columna BD | Estado actual | Estado esperado |
|-------------|--------------|------------|---------------|-----------------|
| **GATA3** | Positivo (fuerte y difuso) | IHQ_GATA3 | N/A ❌ | Positivo ✅ |
| **SOX10** | Negativo (typo: SXO10) | IHQ_SOX10 | N/A ❌ | Negativo ✅ |
| **Receptor Estrógenos** | Negativo | IHQ_RECEPTOR_ESTROGENOS | ") (SP1) RABBIT..." ❌ | Negativo ✅ |
| **Receptor Progesterona** | Negativo | IHQ_RECEPTOR_PROGESTERONA | N/A ❌ | Negativo ✅ |
| **HER2** | Positivo (Score 3+) 100% | IHQ_HER2 | "/NEU: PATHWAY..." ❌ | Positivo (Score 3+) 100% ✅ |
| **Ki-67** | 60% | IHQ_KI-67 | N/A ❌ | 60% ✅ |

---

## FORMATO EXACTO DETECTADO

### Formato Estructurado con Guiones
```regex
-RECEPTOR DE ESTROGENOS: Negativo.
-RECEPTOR DE PROGRESTERONA: Negativo.
-HER 2: Positivo (Score 3+) [descripción larga].
-Ki-67: Tinción nuclear en el 60% de las células tumorales.
```

**Patrón regex necesario:**
```python
r'-\s*([A-ZÁÉÍÓÚÑ\s0-9/\-]+)\s*:\s*(.+?)(?=\n-|\.|$)'
```

### Formato Narrativo Complementario
```regex
[células] tienen una tinción nuclear positiva fuerte y difusa para GATA 3
Son negativas para SXO10
```

**Patrón regex necesario:**
```python
r'tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+([A-Z0-9\s]+)'
r'negativas?\s+para\s+([A-Z0-9]+)'
```

---

## VALIDACIÓN COMPLETA

✅ **Confirmado:** El PDF contiene TODOS los biomarcadores en formato estructurado
✅ **Confirmado:** Los extractores actuales NO capturan este formato
✅ **Confirmado:** Las correcciones propuestas son NECESARIAS y CORRECTAS

---

**Generado por:** core-editor (verificación de texto)
**Fuente:** Texto OCR almacenado en BD
**Longitud texto:** 4,320 caracteres
