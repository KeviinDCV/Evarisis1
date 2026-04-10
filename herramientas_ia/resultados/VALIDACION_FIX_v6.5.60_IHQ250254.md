# VALIDACIÓN FIX v6.5.58-59 - IHQ250254
**Fecha:** 2026-01-28  
**Versión:** v6.5.58 biomarker_extractor.py + v6.5.59 medical_extractor.py  
**Caso:** IHQ250254

---

## RESULTADO DE REPROCESAMIENTO

### Score Final: 88.9% (8/9 validaciones OK)

---

## VALIDACIÓN ESPECÍFICA SOLICITADA

### 1. IHQ_ESTUDIOS_SOLICITADOS
**Estado:** ✅ PARCIALMENTE CORRECTO

**Valor en BD:**
```
EMA, DESMINA, SALL 4, Receptor de Estrógeno, WT1, PAX 8, Ki-67, S100, CKAE1AE3, P53, DESMIN
```

**Checklist solicitado:**
- ✅ EMA (presente)
- ✅ SALL-4 (presente como "SALL 4")
- ✅ DESMINA (presente)
- ✅ ESTROGENO (presente como "Receptor de Estrógeno")
- ✅ WT1 (presente)
- ✅ PAX8 (presente como "PAX 8")
- ✅ Ki-67 (presente)
- ✅ S100 (presente)
- ✅ CKAE1AE3 (presente)
- ✅ P53 (presente)

**Nota:** Hay un duplicado "DESMIN" que no afecta negativamente.

---

### 2. IHQ_SALL4
**Estado:** ❌ FALLO

**Valor esperado:** "POSITIVO (FOCAL)" o "POSITIVO (focal)"  
**Valor en BD:** "NO MENCIONADO"

**Evidencia en OCR:**
```
En el espécimen A2: Las células tumorales presentan una marcación bifásica, 
un componente epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), 
P53, EMA (focal)
```

**Problema detectado:**
El biomarcador está presente en el texto como **"SALL 4 (focal)"** dentro de una lista narrativa, pero NO se está extrayendo el valor.

---

### 3. IHQ_EMA
**Estado:** ❌ FALLO

**Valor esperado:** "POSITIVO (FOCAL)" o "POSITIVO (focal)"  
**Valor en BD:** "NO MENCIONADO"

**Evidencia en OCR:**
```
un componente epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), 
P53, EMA (focal)
```

**Problema detectado:**
El biomarcador está presente en el texto como **"EMA (focal)"** dentro de una lista narrativa, pero NO se está extrayendo el valor.

---

## ANÁLISIS DE CAUSA RAÍZ

### Contexto del formato en PDF:

El caso IHQ250254 usa un formato MIXTO complejo:

1. **Descripción macroscópica (estudios solicitados):**
   ```
   para tinción en el especimen A2: EMA, DESMINA, SALL-4, ESTROGENO, 
   WT1, PAX- 8, Ki67, S100, CKAE1E3, p53
   ```
   - ✅ FIX v6.5.59 funciona correctamente (lista con paréntesis capturada)

2. **Descripción microscópica (resultados):**
   ```
   positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)
   ```
   - ❌ FIX v6.5.58 NO captura correctamente el formato "BIOMARCADOR (focal)"

### Patrón actual en biomarker_extractor.py (v6.5.58):

```python
# V6.5.58 FIX IHQ250254: Lista con paréntesis (ej: "PAX 8 (focal)")
parenthesis_match = re.search(r'positivo\s+para[:\s]+([A-Z0-9\s,/\(\)-]+?)(?:\.|y\s+el\s+componente|$)', 
                               text, re.IGNORECASE)
```

**Problema:**
- El patrón captura la cadena completa: `"CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"`
- Pero al hacer el split por comas: `split(',')`
- Resulta en: `["CKAE1/AE3", " PAX 8", " SALL 4 (focal)", " P53", " EMA (focal)"]`
- La lógica actual NO extrae el valor cuando el biomarcador tiene paréntesis con información adicional

### Lo que se necesita:

**Para "SALL 4 (focal)" y "EMA (focal)":**
1. Detectar el biomarcador base: `SALL 4`, `EMA`
2. Extraer el valor del paréntesis: `focal`
3. Construir el valor completo: `POSITIVO (focal)` o `POSITIVO (FOCAL)`

---

## IMPACTO DEL PROBLEMA

### Casos afectados potenciales:
Cualquier caso que use el formato narrativo con paréntesis que indican detalles del resultado:
- `"BIOMARCADOR (focal)"`
- `"BIOMARCADOR (difuso)"`
- `"BIOMARCADOR (intenso)"`
- `"BIOMARCADOR (débil)"`

---

## RECOMENDACIÓN

### OPCIÓN 1: Agregar lógica específica para paréntesis en listas narrativas

Modificar `extract_narrative_biomarkers()` en `biomarker_extractor.py`:

```python
# V6.5.60 FIX IHQ250254: Capturar valor en paréntesis dentro de lista narrativa
for bio_part in bio_list:
    bio_clean = bio_part.strip()
    
    # Detectar formato "BIOMARCADOR (detalle)"
    paren_match = re.match(r'([A-Z0-9\s/-]+?)\s*\(([^)]+)\)', bio_clean)
    if paren_match:
        bio_name = paren_match.group(1).strip()
        detail = paren_match.group(2).strip()
        
        # Mapear a columna IHQ_*
        col = get_biomarker_column(bio_name)
        if col:
            results[col] = f"POSITIVO ({detail.upper()})"
            continue
    
    # Lógica existente para otros formatos...
```

---

## SIGUIENTE PASO

Se requiere implementar el FIX v6.5.60 para capturar correctamente el formato:
- `"SALL 4 (focal)"` → `IHQ_SALL4 = "POSITIVO (FOCAL)"`
- `"EMA (focal)"` → `IHQ_EMA = "POSITIVO (FOCAL)"`

Una vez implementado, ejecutar nuevamente FUNC-06 para IHQ250254 y validar que el score suba a 100%.
