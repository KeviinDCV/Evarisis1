# Diagnóstico: Extracción Incorrecta de MLH1 en IHQ250035

## Caso
- **Número:** IHQ250035
- **Biomarcador:** MLH1
- **Valor Esperado:** POSITIVO (expresión nuclear intacta)
- **Valor Obtenido:** NEGATIVO
- **Estado:** ❌ INCORRECTO

## Texto OCR (líneas 42-46)
```
42: +Resultado de MLH1: Expresión nuclear intact
43: +Resultado de MSH2: Expresión nuclear intacta
44: +Resultado de MSH6: Expresión nuclear intacta
45: +Resultado de PMS2: Expresión nuclear intacta
46: Interpretación de Reparación de Desajuste (MMR): No hay pérdida de expresión nuclear de las proteínas
```

## Causa Raíz

El **extractor narrativo** (`extract_narrative_biomarkers_list()`) está capturando MLH1 con demasiado contexto:

1. **Patrón descriptivo** (línea 3717 de `biomarker_extractor.py`):
   ```python
   descriptive_pattern = r'(?i)([A-Z][A-Za-z0-9\-]+(?:\s+y\s+[A-Z][A-Za-z0-9\-]+)*):\s*([^.]+?)(?=\.\s*[A-Z][A-Za-z0-9\-]+:|\.(?:\s|$)|$)'
   ```

2. **Texto capturado:**
   - Biomarcador: `MLH1`
   - Descripción: `Expresión nuclear intact +Resultado de MSH2: ... Interpretación ... No hay pérdida de expresión`

3. **Lógica de clasificación** (líneas 3729-3736):
   ```python
   if any(keyword in descripcion for keyword in ['positiv', 'reactiv', 'expresión', ...]):
       # Verificar si hay negación
       if any(neg in descripcion for neg in ['no se', 'ausencia', 'negativ', ..., 'pérdida', 'perdida']):
           estado = 'NEGATIVO'  # ← AQUÍ SE ASIGNA INCORRECTAMENTE
   ```

4. **Problema:** La palabra "pérdida" en la línea 46 ("No hay pérdida") causa falso negativo

## Pruebas que Confirman el Diagnóstico

### Test 1: Patrón actualizado MLH1 funciona correctamente
```python
# Patrón: r'(?i)[\+]?\s*Resultado\s+de\s+MLH1[:\s]*(Expresi[óo]n\s+nuclear\s+(?:intact[a]?|preservada|normal))'
# Match: "Resultado de MLH1: Expresión nuclear intact"
# Normaliza a: "POSITIVO (expresión nuclear intacta)" ✅
```

### Test 2: Texto simplificado extrae correctamente
```python
text = '''
+Resultado de MLH1: Expresión nuclear intact
+Resultado de MSH2: Expresión nuclear intacta
'''
# Resultado: MLH1 = POSITIVO ✅
```

### Test 3: OCR completo extrae incorrectamente
```python
# Cuando incluye línea 46 con "No hay pérdida"
# Resultado: MLH1 = NEGATIVO ❌
```

## Soluciones Propuestas

### Opción 1: Modificar patrón descriptivo (detener en "+")
```python
# ANTES:
descriptive_pattern = r'(?i)([A-Z][A-Za-z0-9\-]+):\s*([^.]+?)(?=\.\s*[A-Z]|\.(?:\s|$)|$)'

# DESPUÉS:
descriptive_pattern = r'(?i)([A-Z][A-Za-z0-9\-]+):\s*([^\.\+]+?)(?=[\.\+]|\n|$)'
# Detiene en punto (.) O en signo más (+)
```

### Opción 2: Dar prioridad al patrón específico de MLH1
```python
# En extract_biomarkers(), ejecutar extract_single_biomarker('MLH1') ANTES de extract_narrative_biomarkers_list()
# Si MLH1 ya tiene valor, skip en narrativo
```

### Opción 3: Excluir marcadores MMR del patrón descriptivo
```python
# Línea 3726-3728: Ya existe exclusión para HER2
# Agregar exclusión para MLH1, MSH2, MSH6, PMS2:
if re.search(r'(?i)^(MLH1|MSH2|MSH6|PMS2)$', biomarcadores_raw):
    continue
```

### Opción 4: Mejorar detección de negación (más específica)
```python
# ANTES:
if any(neg in descripcion for neg in ['no se', 'ausencia', 'negativ', 'pérdida', 'perdida']):
    estado = 'NEGATIVO'

# DESPUÉS:
# Detectar "No hay pérdida" como positivo (doble negación)
if re.search(r'(?i)no\s+hay\s+p[eé]rdida', descripcion):
    estado = 'POSITIVO'  # Doble negación = positivo
elif any(neg in descripcion for neg in ['ausencia', 'negativ', 'sin expresión', 'p[eé]rdida']):
    estado = 'NEGATIVO'
```

## Recomendación

**Implementar Opción 3** (excluir marcadores MMR del patrón descriptivo):
- ✅ Simple y quirúrgica
- ✅ No afecta otros biomarcadores
- ✅ Consistente con exclusión existente de HER2
- ✅ Los marcadores MMR tienen patrones específicos en `ADVANCED_BIOMARKER_PATTERNS`

## Archivos a Modificar

1. **`core/extractors/biomarker_extractor.py`**
   - Línea ~3726: Agregar exclusión de marcadores MMR
   ```python
   # V6.3.36 FIX IHQ250031: Excluir HER2 del patrón descriptivo
   if re.search(r'(?i)^HER\s*-?\s*2$', biomarcadores_raw):
       continue
   
   # V6.3.42 FIX IHQ250035: Excluir marcadores MMR (tienen patrones específicos)
   if re.search(r'(?i)^(MLH1|MSH2|MSH6|PMS2)$', biomarcadores_raw):
       continue
   ```

## Validación

Después de aplicar la corrección:
1. Ejecutar: `auditor.reprocesar_caso_completo('IHQ250035')`
2. Verificar: `IHQ_MLH1 = "POSITIVO (expresión nuclear intacta)"`
3. Ejecutar: `auditor_sistema.py IHQ250035 --inteligente`
4. Score esperado: 100%

---

**Fecha:** 2025-12-16
**Versión actual:** v6.3.41
**Próxima versión:** v6.3.42
