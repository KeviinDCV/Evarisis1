# DIAGNÓSTICO FIX v6.4.89 - IHQ250218 CD3 PROBLEMA

## ESTADO
❌ **FALLIDO** - El fix v6.4.89 es demasiado agresivo

## CASO DE PRUEBA
**IHQ250218** - Linfoma difuso de células B grandes

## RESULTADO ACTUAL (v6.4.89)
```
Score: 66.7% ❌
Ki-67: 90% ✅
MUM1: 30% ✅
CD3: NO MENCIONADO ❌ (INCORRECTO - debería ser NEGATIVO)
```

## ANÁLISIS DEL PROBLEMA

### Contexto del OCR
```
Línea 39: "Son negativas para CD38, cMYC y CD30"
Línea 40: "Hay linfocitos T acompañantes CD3+, BCL2+"
```

### Interpretación Correcta
- **CD3 de células tumorales (linfoma B):** NEGATIVO (no está en lista de positivos)
- **CD3 de linfocitos T acompañantes:** POSITIVO (pero NO es resultado tumoral)

### Comportamiento Actual del Filtro v6.4.89

**Código actual (líneas 1286-1318):**
```python
# Detecta patrón
acompanantes_pattern = r'(?i)(?:hay\s+)?linfocitos?\s+T\s+acompa[ñn]antes\s+(?:CD\s*3|BCL\s*2)'
patron_encontrado = re.search(acompanantes_pattern, text)

if patron_encontrado:
    # ELIMINA COMPLETAMENTE CD3 sin verificar su valor
    for clave in ['CD3', 'IHQ_CD3', 'cd3']:
        if clave in combined_data:
            valor_removido = combined_data.pop(clave)  # ❌ PROBLEMA AQUÍ
```

**Problema:**
- ✅ Detecta correctamente el patrón "linfocitos T acompañantes CD3+"
- ❌ Elimina TODO el CD3, incluso el CD3 NEGATIVO que es el resultado real

### Resultado Esperado vs Actual

| Biomarcador | Esperado | Actual v6.4.89 | Estado |
|-------------|----------|----------------|--------|
| Ki-67 | 90% | 90% | ✅ OK |
| MUM1 | 30% | 30% | ✅ OK |
| CD3 | NEGATIVO | NO MENCIONADO | ❌ ERROR |
| BCL2 | POSITIVO | Eliminado (correcto) | ✅ OK |

## SOLUCIÓN PROPUESTA (v6.4.90)

### Lógica Correcta

```python
# V6.4.90 FIX IHQ250218: Filtro selectivo CD3/BCL2 según valor
# Problema: v6.4.89 elimina TODO el CD3, incluso el NEGATIVO real
# Solución: Solo eliminar si es POSITIVO (viene de linfocitos acompañantes)
#           Mantener si es NEGATIVO (es el resultado tumoral real)

acompanantes_pattern = r'(?i)(?:hay\s+)?linfocitos?\s+T\s+acompa[ñn]antes\s+(?:CD\s*3|BCL\s*2)'
patron_encontrado = re.search(acompanantes_pattern, text)

if patron_encontrado:
    # CD3: Solo eliminar si es POSITIVO
    for clave in ['CD3', 'IHQ_CD3', 'cd3']:
        if clave in combined_data:
            valor = str(combined_data[clave]).upper()
            
            # Si es POSITIVO → viene de linfocitos acompañantes → eliminar
            if 'POSITIV' in valor or '+' in valor:
                valor_removido = combined_data.pop(clave)
                logger.info(f"⚠️ [V6.4.90] {clave} POSITIVO removido: '{valor_removido}' (linfocitos T acompañantes)")
            
            # Si es NEGATIVO → es resultado tumoral → MANTENER
            else:
                logger.info(f"✅ [V6.4.90] {clave} NEGATIVO mantenido: '{valor}' (resultado tumoral válido)")
    
    # BCL2: Siempre eliminar (linfomas B DEBEN ser BCL2-)
    for clave in ['BCL2', 'IHQ_BCL2', 'bcl2']:
        if clave in combined_data:
            valor_removido = combined_data.pop(clave)
            logger.info(f"⚠️ [V6.4.90] {clave} removido: '{valor_removido}' (linfocitos T acompañantes)")
```

### Casos de Validación

| Caso | OCR | CD3 Extraído | Patrón Acompañantes | Acción Correcta |
|------|-----|--------------|---------------------|-----------------|
| **IHQ250218** | "linfocitos T acompañantes CD3+" | NEGATIVO | ✅ Presente | MANTENER (resultado tumoral) |
| Caso normal | No menciona acompañantes | POSITIVO | ❌ Ausente | MANTENER (resultado tumoral) |
| Caso futuro | "linfocitos T acompañantes CD3+" | POSITIVO | ✅ Presente | ELIMINAR (es de acompañantes) |

## IMPACTO DE LA CORRECCIÓN

### Antes (v6.4.89)
- Score: 66.7%
- CD3: NO MENCIONADO ❌
- Error: "CD3 valor incorrecto (esperado: NEGATIVO, obtenido: NO MENCIONADO)"

### Después (v6.4.90 esperado)
- Score: 100% ✅
- CD3: NEGATIVO ✅
- Sin errores

## CASOS DE REGRESIÓN A VALIDAR

**Antes de aplicar v6.4.90, validar estos casos:**

1. **IHQ250218** (caso actual - linfoma B)
   - Esperado: CD3 NEGATIVO ✅
   
2. Casos previos con "linfocitos T acompañantes" (buscar en BD)
   - Verificar que no se rompa la lógica de eliminación

3. Casos sin "linfocitos T acompañantes" con CD3 POSITIVO/NEGATIVO
   - Verificar que se mantengan intactos

## RECOMENDACIÓN

1. **Implementar v6.4.90** con filtro selectivo por valor
2. **Reprocesar IHQ250218** y validar score 100%
3. **Validar casos de regresión** (mínimo 3 casos)
4. **Documentar cambio** en CHANGELOG

---
**Generado:** 2026-01-19 08:02:00
**Versión actual:** v6.4.89 (problemática)
**Versión propuesta:** v6.4.90 (con fix selectivo)
