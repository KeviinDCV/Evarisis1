# VALIDACIÓN CORRECCIÓN v6.4.80 - IHQ250214

**Fecha:** 2026-01-17
**Caso:** IHQ250214
**Problema:** DIAGNOSTICO_COLORACION captura demasiado texto
**Estado:** FALLO - Requiere corrección del patrón

---

## PROBLEMA DETECTADO

### Patrón Actual (v6.4.80, línea 880)
```python
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"([^"]+(?:\n[^"]+)*?)\.\s+'
```

### Texto en OCR
```
M2501390 que corresponde a "ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL
PERITONEO VISCERAL. Previa valoración de la coloración básica, se realizan cortes histológicos al
bloque A3 para los siguientes marcadores: HER-2 , MSH6 , MSH2 , MLH1 , PMS2.
DESCRIPCIÓN MICROSCÓPICA
...
(continúa por ~1500 caracteres más hasta llegar a las comillas de cierre)
```

### Captura Actual (INCORRECTA)
El patrón captura **TODO** el texto desde "ADENOCARCINOMA..." hasta "...dentro de su especialidadillas" (1500+ caracteres).

**Por qué:** El patrón `([^"]+(?:\n[^"]+)*?)\.\s+` busca:
1. `[^"]+` - Texto sin comillas
2. `(?:\n[^"]+)*?` - Opcionalmente texto después de saltos de línea
3. `\.\s+` - Hasta encontrar punto + espacio

El problema es que hay múltiples puntos en el texto antes de las comillas de cierre, entonces sigue capturando.

### Captura Esperada (CORRECTA)
```
ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL PERITONEO VISCERAL
```

**Score actual:** 88.9% (WARNING por DIAGNOSTICO_COLORACION no encontrado en OCR)
**Score esperado:** 100%

---

## ANÁLISIS DE CAUSA RAÍZ

### Problema 1: Patrón demasiado permisivo
El patrón actual permite capturar múltiples líneas y múltiples puntos sin restricción.

### Problema 2: No hay límite de captura
El patrón `(?:\n[^"]+)*?` permite capturar infinitas líneas mientras no haya comillas.

### Problema 3: Punto ambiguo
El patrón busca `\.\s+` que puede aparecer en múltiples lugares del texto (descripción microscópica, diagnóstico, notas, etc.).

---

## SOLUCIÓN PROPUESTA

### Opción A: Capturar hasta primer punto después de salto de línea
```python
# Captura hasta el PRIMER punto que aparece en una nueva línea
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"([^"\n]+(?:\n[^"\n.]+)*?)\.'
```

**Ventajas:**
- Detiene en el primer punto después de completar el diagnóstico en la segunda línea
- Más restrictivo, menos ambigüedad

**Desventajas:**
- Si el diagnóstico tiene puntos internos (ej: "ca. in situ"), podría cortar prematuramente

### Opción B: Capturar hasta comillas de cierre (máximo 200 caracteres)
```python
# Captura hasta comillas de cierre pero con límite de longitud
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"([^"]{10,200}?)"'
```

**Ventajas:**
- Más directo, captura exactamente lo que está entre comillas
- Límite de 200 caracteres evita capturar descripciones largas

**Desventajas:**
- Si el diagnóstico legítimo tiene >200 caracteres, fallaría

### Opción C: Capturar hasta marcador de sección siguiente
```python
# Captura hasta que aparece "Previa" o "DESCRIPCIÓN"
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"([^"]+?)(?:\.\s+Previa|\.\s+DESCRIPCIÓN)'
```

**Ventajas:**
- Usa contexto semántico del documento
- Detiene en el límite natural de la sección

**Desventajas:**
- Dependiente de formato específico del PDF
- Más frágil ante variaciones

---

## RECOMENDACIÓN

**Usar Opción B modificada:**
```python
# V6.4.81 - FIX IHQ250214: Capturar diagnóstico completo entre comillas con límite razonable
# Captura texto entre comillas dobles, permitiendo saltos de línea, máximo 300 caracteres
# Esto evita capturar descripciones largas después del diagnóstico
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"(.{10,300}?)\."'
```

**Por qué:**
1. Captura exactamente lo que está entre `"..."` 
2. Permite saltos de línea (`.` con `re.DOTALL`)
3. Límite de 300 caracteres cubre diagnósticos largos pero evita capturar secciones completas
4. Requiere punto antes de comillas de cierre (validación de formato)

---

## VALIDACIÓN REQUERIDA

Después de aplicar el fix v6.4.81, validar estos casos:

1. **IHQ250214** (caso actual)
   - Score esperado: 88.9% → 100%
   - DIAGNOSTICO_COLORACION: "ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL PERITONEO VISCERAL"

2. **Casos de referencia con patrón v6.4.80**
   - Buscar otros casos que usen formato "M[número] que corresponde a"
   - Validar que NO haya regresión

---

## SIGUIENTE PASO

1. Modificar `core/extractors/medical_extractor.py` línea 880
2. Cambiar patrón a versión v6.4.81 recomendada
3. Ejecutar FUNC-06 en IHQ250214
4. Validar score mejora a 100%
5. Buscar casos de referencia y validar sin regresión

