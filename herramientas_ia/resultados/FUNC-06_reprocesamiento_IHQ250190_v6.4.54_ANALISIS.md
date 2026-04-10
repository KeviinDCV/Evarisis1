# ANÁLISIS REGRESIÓN v6.4.53 → v6.4.54

## CASO: IHQ250190

### RESULTADO v6.4.53 (ACTUAL):
- IHQ_DESMIN: NEGATIVO ❌
- IHQ_MYOGENIN: NEGATIVO ❌  
- IHQ_MYOD1: POSITIVO (fuerte) ✅
- IHQ_CD56: POSITIVO ✅
- Score: 100% (pero valores incorrectos)

### OCR REAL:
```
Línea 44: ...CD34. Presentan positividad fuerte para CD56,
Línea 45: DESMINA, MYOGENINA y Myo D1. Presenta positividad focal...
```

### PROBLEMA IDENTIFICADO:

**Patrón v6.4.53 ACTUAL (línea 5391):**
```python
r'(?i)Presenta[n]?\s+positividad\s+(?:fuerte|d[eé]bil|moderada|focal)(?:\s+y\s+(?:difuso|difusa|focal))?\s+para\s+([A-Za-z0-9\s,()\./\-]+?)(?:\.|[\.\s]Presenta[n]?)'
```

**¿Qué captura?**
- Match: "Presentan positividad fuerte para CD56,"
- Grupo 1: "CD56,"
- STOP: encuentra salto de línea + "DESMINA" pero el patrón termina con `[\.\s]Presenta` que matchea el inicio de "Presenta positividad focal" en línea 45

**¿Por qué NO captura DESMINA/MYOGENINA/MYOD1?**
1. El grupo de captura `([A-Za-z0-9\s,()\./\-]+?)` es **no-greedy** (`+?`)
2. Termina al primer match con `(?:\.|[\.\s]Presenta[n]?)`
3. Encuentra "CD56,\n" y luego busca el final
4. El "Presenta positividad focal" en línea 45 hace que termine sin capturar DESMINA/MYOGENINA/MYOD1

### CORRECCIÓN v6.4.54:

**Cambiar final del patrón (línea 5391):**
```python
# ANTES (v6.4.53 - termina muy pronto)
(?:\.|[\.\s]Presenta[n]?)

# DESPUÉS (v6.4.54 - captura lista completa hasta punto final)
(?:\.\s+(?:[A-Z]|Presenta[n]?\s+positividad))
```

**Patrón completo v6.4.54:**
```python
r'(?i)Presenta[n]?\s+positividad\s+(?:fuerte|d[eé]bil|moderada|focal)(?:\s+y\s+(?:difuso|difusa|focal))?\s+para\s+([A-Za-z0-9\s,()\./\-]+?)(?:\.\s+(?:[A-Z]|Presenta[n]?\s+positividad))'
```

**¿Qué capturará ahora?**
- Match: "Presentan positividad fuerte para CD56,\nDESMINA, MYOGENINA y Myo D1."
- Grupo 1: "CD56,\nDESMINA, MYOGENINA y Myo D1"
- STOP: encuentra ". Presenta positividad focal" (punto + espacio + "Presenta positividad")

### VALIDACIÓN ESPERADA:

Después de aplicar v6.4.54 y reprocesar IHQ250190:
- IHQ_DESMIN: POSITIVO (fuerte) ✅
- IHQ_MYOGENIN: POSITIVO (fuerte) ✅
- IHQ_MYOD1: POSITIVO (fuerte) ✅
- IHQ_CD56: POSITIVO (fuerte) ✅
- Score: 100% con valores correctos

### CASOS DE REFERENCIA A VALIDAR:

**Antes de aplicar v6.4.54, auditar estos casos con v6.4.53:**
1. IHQ250190 (caso actual - sabemos que falla)
2. [Agregar 2-3 casos que usan patrón "Presentan positividad"]

**Después de aplicar v6.4.54:**
1. Reprocesar todos los casos de referencia
2. Verificar que NINGUNO baje su score
3. IHQ250190 debe tener todos los biomarcadores correctos
