# FUNC-06: Diagnóstico de Reprocesamiento IHQ251026

**Fecha:** 2025-11-09  
**Caso:** IHQ251026  
**Estado:** AMBOS OBJETIVOS INCUMPLIDOS

---

## RESUMEN EJECUTIVO

Se ejecutó FUNC-06 para reprocesar el caso IHQ251026 con las 3 correcciones aplicadas:

1. auditor_sistema.py v3.4.1: Mapeo 'CAM 5' → IHQ_CAM5 (no IHQ_CAM52)
2. biomarker_extractor.py v6.2.5: Eliminada definición CAM5.2 duplicada
3. medical_extractor.py v6.3.1: Patrón estudios solicitados captura lista completa

**RESULTADO:** Ambos objetivos incumplidos

---

## OBJETIVO 1: IHQ_ESTUDIOS_SOLICITADOS

### Esperado
```
P16, P40, CAM 5.2, BCL2, BCL6, CD20, CD5, CK 5/6, CK7, CKAE1/AE3
```

### Obtenido en BD
```
P16, P40, CAM 5
```

### Resultado
- **Cobertura:** 30.0% (3/10 biomarcadores)
- **Estado:** INCUMPLIDO
- **Biomarcadores encontrados:** ['P16', 'P40', 'CAM 5.2']
- **Biomarcadores faltantes:** ['BCL2', 'BCL6', 'CD20', 'CD5', 'CK 5/6', 'CK7', 'CKAE1/AE3']

### Evidencia OCR (líneas 4190-4191)
```
niveles histológicos para tinción con: p16, p40, CAM 5.2. BCL2, BCL6, CD20, CD5, p40, CK 5/6,
CK7, CKAE1/AE3.
```

### CAUSA RAÍZ
El patrón regex en `medical_extractor.py` NO puede manejar el PUNTO después de "CAM 5.2."

**Problema:**
1. Lista comienza: "p16, p40, CAM 5.2."
2. Hay un PUNTO después de "CAM 5.2" que NO es el punto final de la oración
3. Patrón actual detecta el punto como fin de lista
4. Se pierden: BCL2, BCL6, CD20, CD5, CK 5/6, CK7, CKAE1/AE3

**Patrón actual (línea ~330-350):**
```python
# Patrón que busca lista de biomarcadores
patron = r'(?:tinci[óo]n con|niveles.*?para|se realizan):?\s*([^\.]+)\.'
```

**Problema:** El patrón `[^\.]+` se detiene en el PRIMER punto (después de CAM 5.2).

---

## OBJETIVO 2: IHQ_CAM5

### Esperado
```
POSITIVO
```

### Obtenido en BD
```
IHQ_CAM5: N/A
IHQ_CAM52: N/A
```

### Resultado
- **Estado:** INCUMPLIDO
- **Ambas columnas vacías**

### Evidencia OCR (línea 4199)
```
positiva para CKAE1AE3, CK7 CAM 5.2
```

### CAUSA RAÍZ
El valor está en el OCR pero NO se extrae.

**Posibles causas:**
1. **Falta de patrón específico:** `biomarker_extractor.py` no tiene patrón para "positiva para ... CAM 5.2"
2. **Formato no estándar:** No aparece como "CAM 5.2: POSITIVO" sino como parte de lista narrativa
3. **Normalización incorrecta:** El mapeo 'CAM 5' → 'IHQ_CAM5' no aplica porque el texto no contiene la variante esperada

**Texto esperado vs obtenido:**
- **Esperado:** "CAM 5.2: POSITIVO" o "CAM5.2: POSITIVO"
- **Obtenido:** "positiva para CKAE1AE3, CK7 CAM 5.2" (sin estado explícito)

---

## DIAGNÓSTICO INTEGRADO

### Problema Común
Ambos objetivos fallan por **FORMATO NO ESTÁNDAR** del PDF.

**Diferencias con casos exitosos:**
1. **Estudios solicitados:** Punto dentro de lista rompe parsing
2. **CAM5:** Valor en lista narrativa, no en formato "CAM5: ESTADO"

### Biomarcadores Individuales Extraídos
```
IHQ_P16_ESTADO: NO HAY MARCACIÓN EN LA MUESTRA PARA P40, P16
IHQ_P16_PORCENTAJE: N/A
IHQ_P40_ESTADO: NEGATIVO
IHQ_BCL2: POSITIVO
IHQ_BCL6: POSITIVO
IHQ_CD20: POSITIVO
IHQ_CD5: POSITIVO
IHQ_CK5_6: N/A
IHQ_CK7: N/A
IHQ_CKAE1AE3: POSITIVO
IHQ_CAM5: N/A
IHQ_CAM52: N/A
```

**NOTA IMPORTANTE:** Los biomarcadores BCL2, BCL6, CD20, CD5, CKAE1AE3 SÍ se extrajeron correctamente en sus columnas individuales.

**Esto significa:**
- Los extractores de biomarcadores individuales SÍ funcionan
- El problema está en `IHQ_ESTUDIOS_SOLICITADOS` (que usa `medical_extractor.py`)

---

## CORRECCIONES NECESARIAS

### CORRECCIÓN 1: Patrón de estudios solicitados (CRÍTICO)
**Archivo:** `core/extractors/medical_extractor.py`  
**Función:** `extract_requested_biomarkers()` (línea ~330-350)

**Problema actual:**
```python
patron = r'(?:tinci[óo]n con|niveles.*?para|se realizan):?\s*([^\.]+)\.'
```

**Solución propuesta:**
```python
# Patrón más robusto que maneja puntos dentro de biomarcadores
patron = r'(?:tinci[óo]n con|niveles.*?para|se realizan):?\s*(.+?)(?:\.|$)'

# Luego limpiar puntos internos que no son separadores
match = re.search(patron, texto)
if match:
    lista_bruta = match.group(1)
    # Reemplazar ". " dentro de biomarcadores por ", "
    lista_limpia = re.sub(r'\.\s+([A-Z])', r', \1', lista_bruta)
```

**Caso de prueba:**
```
Entrada: "p16, p40, CAM 5.2. BCL2, BCL6, CD20, CD5, p40, CK 5/6, CK7, CKAE1/AE3."
Salida esperada: "P16, P40, CAM 5.2, BCL2, BCL6, CD20, CD5, CK 5/6, CK7, CKAE1/AE3"
```

---

### CORRECCIÓN 2: Extracción narrativa CAM5 (MEDIA PRIORIDAD)
**Archivo:** `core/extractors/biomarker_extractor.py`  
**Función:** Agregar patrón para listas narrativas

**Nuevo patrón sugerido:**
```python
# Patrón para "positiva para ... CAM 5.2"
patron_narrativo = r'positiva?\s+para\s+(?:[^,]+,\s*)*([^,]+)\s+CAM\s*5\.?2'

# Si se encuentra, extraer estado POSITIVO
if re.search(patron_narrativo, descripcion_microscopica):
    biomarkers['CAM5'] = 'POSITIVO'
```

---

## RECOMENDACIONES

### Prioridad 1 (CRÍTICO)
1. Modificar patrón en `medical_extractor.py` para manejar puntos internos
2. Reprocesar caso IHQ251026 con FUNC-06
3. Validar que IHQ_ESTUDIOS_SOLICITADOS capture 10/10 biomarcadores

### Prioridad 2 (MEDIA)
4. Agregar patrón narrativo para CAM5 en `biomarker_extractor.py`
5. Reprocesar nuevamente
6. Validar que IHQ_CAM5 = "POSITIVO"

### Testing
7. Buscar otros casos con formato similar (punto dentro de lista)
8. Validar que corrección no rompe casos exitosos
9. Ejecutar batería de regresión en casos de prueba

---

## ARCHIVOS INVOLUCRADOS

```
core/extractors/medical_extractor.py (línea ~330-350)
core/extractors/biomarker_extractor.py (agregar patrón narrativo)
```

---

**ESTADO FINAL:** PENDIENTE CORRECCIÓN DE CÓDIGO
**SIGUIENTE PASO:** Modificar medical_extractor.py según propuesta
**VALIDACIÓN:** FUNC-06 nuevamente después de modificación

