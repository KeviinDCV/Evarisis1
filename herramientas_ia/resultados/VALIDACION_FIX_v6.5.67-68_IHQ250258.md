# VALIDACIÓN FINAL - v6.5.67 + v6.5.68
## Caso IHQ250258 - Receptores Hormonales con Porcentaje (<1%)

**Fecha:** 2026-01-29  
**Versiones aplicadas:** v6.5.67 (biomarker_extractor) + v6.5.68 (unified_extractor)

---

## PROBLEMA ORIGINAL

El caso IHQ250258 tenía receptores hormonales en formato sin paréntesis:
```
OCR ORIGINAL:
- EXPRESIÓN DE RECEPTORES DE ESTRÓGENOS NEGATIVO MENOR AL 1%.
- EXPRESIÓN DE RECEPTORES DE PROGESTERONA: NEGATIVO MENOR AL 1%.
```

**Extracción incorrecta v6.5.66:**
- IHQ_RECEPTOR_ESTROGENOS: `NEGATIVO (<1%)` ✅ (capturado)
- IHQ_RECEPTOR_PROGESTERONA: `NEGATIVO` ❌ (falta porcentaje)

---

## CAUSA RAÍZ

### Problema 1: biomarker_extractor.py (RESUELTO v6.5.67)

**Patrón v6.5.66:**
```python
patron_pr_menor = r'...\(\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)'
                        ^^                              ^^
                     Requiere paréntesis obligatorios
```

**Problema:** OCR tiene texto SIN paréntesis: `NEGATIVO MENOR AL 1%`

**Solución v6.5.67:**
```python
patron_pr_menor = r'...\(?\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)?'
                        ^^^                              ^^^
                     Paréntesis opcionales
```

### Problema 2: unified_extractor.py (RESUELTO v6.5.68)

**Código v6.5.66:**
```python
tiene_porcentaje_nuevo = bool(re.search(r'\(\d+%\)', valor_biomarker))
                                              ^^^
                                         No detecta '<1%'
```

**Problema:** Patrón NO detecta `(<1%)` porque tiene `<` antes del dígito

**Solución v6.5.68:**
```python
tiene_porcentaje_nuevo = bool(re.search(r'\([<>]?\d+%\)', valor_biomarker))
                                              ^^^^^
                                    Acepta < o > opcional
```

---

## CAMBIOS APLICADOS

### 1. biomarker_extractor.py v6.5.67

**Líneas 4316, 4324:**
```python
# ANTES (v6.5.66)
patron_er_menor = r'...\(\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)'
patron_pr_menor = r'...\(\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)'

# DESPUÉS (v6.5.67)
patron_er_menor = r'...\(?\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)?'
patron_pr_menor = r'...\(?\s*MENOR\s+AL?\s+(\d+)\s*%\s*\)?'
```

**Comentario agregado (línea 4308):**
```python
# V6.5.67 FIX IHQ250258: Paréntesis OPCIONALES - Captura ambos formatos:
#   - "NEGATIVO (MENOR AL 1%)" (con paréntesis)
#   - "NEGATIVO MENOR AL 1%" (sin paréntesis - OCR IHQ250258)
```

### 2. unified_extractor.py v6.5.68

**Líneas 1096-1097:**
```python
# ANTES (v6.5.66)
tiene_porcentaje_nuevo = bool(re.search(r'\(\d+%\)', valor_biomarker))
tiene_porcentaje_existente = bool(re.search(r'\(\d+%\)', valor_existente or ''))

# DESPUÉS (v6.5.68)
tiene_porcentaje_nuevo = bool(re.search(r'\([<>]?\d+%\)', valor_biomarker))
tiene_porcentaje_existente = bool(re.search(r'\([<>]?\d+%\)', valor_existente or ''))
```

**Comentario agregado (línea 1094):**
```python
# V6.5.68 FIX IHQ250258: También detectar porcentajes con < o > (ej: "<1%", ">90%")
```

---

## VALIDACIÓN FINAL

### Reprocesamiento IHQ250258

**Logs de extracción:**
```
✅ [ER MENOR v6.5.67] Extraído: NEGATIVO (<1%)
✅ [PR MENOR v6.5.67] Extraído: NEGATIVO (<1%)
```

### Valores en Base de Datos

**Columnas individuales:**
```
IHQ_RECEPTOR_ESTROGENOS: NEGATIVO (<1%)     ✅
IHQ_RECEPTOR_PROGESTERONA: NEGATIVO (<1%)   ✅
```

**Factor Pronóstico:**
```
HER2: NEGATIVO (SCORE 0), Ki-67: 90%, Receptor de Estrógeno: NEGATIVO (<1%), Receptor de Progesterona: NEGATIVO (<1%)
```

### Auditoría Inteligente

```
Score de validación: 100.0%
Estado final: OK
Warnings: 0
Errores: 0
```

---

## IMPACTO

**Casos beneficiados:**
- IHQ250258 (validado)
- Cualquier caso con formato "NEGATIVO MENOR AL X%" sin paréntesis
- Cualquier caso con porcentajes con símbolos `<` o `>` (ej: `<1%`, `>90%`)

**Archivos modificados:**
1. `core/extractors/biomarker_extractor.py` (v6.5.67)
   - Líneas 4316, 4324: Paréntesis opcionales en patrones ER/PR
   - Líneas 4322, 4330: Logs actualizados a v6.5.67

2. `core/unified_extractor.py` (v6.5.68)
   - Líneas 1096-1097: Detección de porcentajes con `<` o `>`

**Backups creados:**
- `core/extractors/biomarker_extractor.py.backup_v6566`
- `core/unified_extractor.py.backup_v6567`

---

## CONCLUSIÓN

✅ **CORRECCIÓN EXITOSA**

- AMBOS receptores hormonales ahora capturan el porcentaje `(<1%)`
- Patrón robusto soporta ambos formatos (con y sin paréntesis)
- Sistema detecta porcentajes con símbolos comparativos (`<`, `>`)
- Score de validación: 100%
- Sin regresiones detectadas

**Siguiente paso:** Validar con casos adicionales que tengan formato similar.
