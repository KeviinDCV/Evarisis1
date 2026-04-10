# Analisis de Patrones de Extraccion - Biomarcadores IHQ251014

**Fecha:** 2025-11-05
**Caso:** IHQ251014
**Archivo analizado:** core/extractors/biomarker_extractor.py (3768 lineas)

---

## RESUMEN EJECUTIVO

### ESTADO GENERAL
- OK: 13/14 biomarcadores tienen columnas en BD (92.9%)
- ADVERTENCIA: 2 biomarcadores con patrones CORRECTOS pero NO extraen (CD117, CD34)
- ERROR: 6 biomarcadores sin patrones para formatos especificos
- ERROR: 1 biomarcador sin columna en BD (GLICOFORINA)

### HALLAZGO CRITICO
CD117 y CD34 tienen patrones correctos (agregados v6.2.2) pero siguen reportando "NO MENCIONADO".

Problema potencial:
1. Precedencia de patrones (patron general captura primero)
2. Flujo de invocacion en unified_extractor.py
3. Problema en guardado/mapeo

---

## ANALISIS DETALLADO POR BIOMARCADOR

### 1. GLICOFORINA - PATRONES CORRECTOS

**Estado:** NO EXISTE COLUMNA IHQ_GLICOFORINA
**OCR:** "eritroide (Glycophorin)" -> POSITIVO
**Lineas 1552-1554:**

Patron YA AGREGADO en v6.2.2:

r'(?i)eritroide\s*\(\s*glycophorin'  # OK - YA EXISTE

**Diagnostico:** Patrones correctos, falta columna BD
**Accion:** Usuario ejecuta FUNC-03 si desea agregar

---

### 2. CD117 - PATRONES OK PERO NO EXTRAE

**Estado:** COLUMNA EXISTE | BD: NO MENCIONADO | OCR: CD117 +
**Lineas 1289-1302:**

Patrones YA AGREGADOS en v6.2.2:
- r'(?i)cd\s*117\s+(\+)'  # OK - EXISTE
- r'(?i)cd\s*117\s+(-)'   # OK - EXISTE

Normalizacion:
- '+': 'POSITIVO'  # OK - EXISTE
- '-': 'NEGATIVO'  # OK - EXISTE

**Diagnostico:** Patrones completos y correctos
**Problema potencial:** Precedencia, invocacion o guardado
**Accion:** Investigar logs de extraccion

---

### 3. CD34 - PATRONES OK PERO NO EXTRAE

**Estado:** COLUMNA EXISTE | BD: NO MENCIONADO | OCR: CD34 -
**Lineas 1142-1151:**

Mismo problema que CD117. Patrones correctos existen.

---

### 4. CD56 - FALTAN PATRONES COMPACTOS

**OCR esperado:** CD56- (formato sin espacios)
**Patrones actuales:** NO cubre formato compacto

**AGREGAR (despues linea 1230):**
```python
# V6.2.3: Formato compacto (IHQ251014)
r'(?i)cd\s*56\s*\+',
r'(?i)cd\s*56\s*-',
```

**NORMALIZACION:**
```python
'+': 'POSITIVO',
'-': 'NEGATIVO',
```

---

### 5. CD3 - FALTAN PATRONES COMPACTOS

**OCR esperado:** CD3+

**AGREGAR (despues linea 975):**
```python
# V6.2.3: Formato compacto (IHQ251014)
r'(?i)cd\s*3\s*\+',
r'(?i)cd\s*3\s*-',
```

---

### 6. CD5 - FALTAN PATRONES COMPACTOS

**OCR esperado:** CD5+
**PRECAUCION:** Mantener (?!6) para evitar CD56

**AGREGAR (despues linea 1013):**
```python
# V6.2.3: Formato compacto - Evita CD56 (IHQ251014)
r'(?i)cd\s*5(?!6)\s*\+',
r'(?i)cd\s*5(?!6)\s*-',
```

---

### 7. CD15 - FALTAN PATRONES NARRATIVOS

**OCR esperado:** linea mieloide (CD15) -> POSITIVO

**AGREGAR (despues linea 1059):**
```python
# V6.2.3: Formato narrativo (IHQ251014)
r'(?i)l[íi]nea\s+mieloide\s*\(\s*cd\s*15',
r'(?i)mieloide\s*\(\s*cd\s*15',
```

---

### 8. CD61 - FALTAN PATRONES NARRATIVOS

**OCR esperado:** megacariocitos (CD61) -> POSITIVO

**AGREGAR (despues linea 1243):**
```python
# V6.2.3: Formato narrativo (IHQ251014)
r'(?i)megacariocitos?\s*\(\s*cd\s*61',
```

---

### 9. CKAE1AE3 - FALTA PATRON NEGATIVO

**OCR esperado:** Sin marcacion para CKAE1AE3 -> NEGATIVO

**AGREGAR (ANTES linea 1657 - ALTA PRIORIDAD):**
```python
# V6.2.3: Sin marcacion (IHQ251014)
r'(?i)sin\s+marcaci[óo]n\s+para\s+(?:[A-Z0-9]+,\s*)*CKAE1[/E\s]*(?:AE)?3',
```

**NORMALIZACION:**
```python
'sin marcación': 'NEGATIVO',
'sin marcacion': 'NEGATIVO',
```

---

### 10. TDT - PROBLEMA DE AUDITOR

**BD:** NEGATIVO (CORRECTO)
**OCR:** - (simbolo)

**Diagnostico:** Extractor funciona. Auditor no normaliza OCR antes de comparar.
**Accion:** Verificar auditor_sistema.py

---

## TABLA RESUMEN - CORRECCIONES REQUERIDAS

| Biomarcador | Linea | Patron Faltante | Prioridad |
|-------------|-------|-----------------|-----------||
| CD56 | 1230 | Compacto: +/- | ALTA |
| CD3 | 975 | Compacto: +/- | ALTA |
| CD5 | 1013 | Compacto: +/- (con (?!6)) | ALTA |
| CD15 | 1059 | Narrativo: mieloide | ALTA |
| CD61 | 1243 | Narrativo: megacariocitos | ALTA |
| CKAE1AE3 | 1656 | "sin marcacion" | ALTA |
| CD117 | - | Investigar extraccion | MEDIA |
| CD34 | - | Investigar extraccion | MEDIA |
| TDT | - | Auditor normalizacion | MEDIA |
| GLICOFORINA | - | Falta columna BD | BAJA |

---

## INVESTIGACION CD117/CD34

Pasos:
1. Verificar mapeo en unified_extractor:
   grep -n "CD117\|CD34" core/unified_extractor.py

2. Verificar orden de patrones (mover especificos ANTES de generales)

3. Activar logs y procesar caso para ver si patrones matchean

---

## VERIFICACION POST-CORRECCION

```bash
# 1. Aplicar modificaciones a biomarker_extractor.py
# 2. rm data/huv_oncologia_NUEVO.db
# 3. python ui.py (procesar IHQ251014)
# 4. python herramientas_ia/auditor_sistema.py IHQ251014 --inteligente
```

**Resultado esperado:**
- 6 biomarcadores nuevos extraen correctamente
- CD117/CD34 requieren investigacion si persiste

---

**FIN DEL ANALISIS**
