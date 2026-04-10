# DIAGNÓSTICO: Patrón v6.4.61 NO Funciona para IHQ250202

**Caso:** IHQ250202
**Versión:** v6.4.61
**Fecha:** 2026-01-09
**Estado:** ❌ FALLIDO - Patrón con error de sintaxis regex

---

## 📋 RESUMEN EJECUTIVO

El patrón v6.4.61 posicionado con máxima prioridad (línea 4047 de biomarker_extractor.py) NO está extrayendo correctamente TTF-1 como NEGATIVO en el caso IHQ250202.

**Resultado actual:**
- **valor_bd:** POSITIVO ❌ (INCORRECTO)
- **valor_ocr:** NEGATIVO ✅ (CORRECTO)
- **Score:** 88.9% (debería ser 100%)

---

## 🔍 ANÁLISIS DE CAUSA RAÍZ

### Texto del OCR (línea 54 del debug_map):
```
Los marcadores napsina y TTF-1 - son negativos.
```

### Patrón v6.4.61 (línea 4051):
```python
marcadores_con_guion_pattern = r'(?i)Los?\s+marcadores?\s+([^-]+?)\s+-\s+(?:son|es)\s+(negativos?|positivos?)\s*\.'
```

### ERROR DETECTADO:

El componente `[^-]+?` tiene un problema semántico:

**Significado de `[^-]+?`:**
- `[^-]`: Cualquier carácter que NO sea guión
- `+?`: Uno o más, non-greedy (se detiene en la primera oportunidad)
- **PROBLEMA:** Se detiene en el primer espacio después de "n" porque el patrón espera `\s+-`

**Captura real:**
```
Los marcadores n ← [^-]+? captura solo "n"
                 ^ espacio detectado, patrón busca "-" pero encuentra "apsina..."
```

**Análisis paso por paso:**
1. ✅ `Los?\s+marcadores?` → Match: "Los marcadores"
2. ✅ `\s+` → Match: espacio
3. ❌ `[^-]+?` → Captura: "n" (se detiene porque siguiente es espacio)
4. ❌ `\s+-` → NO MATCH (esperaba espacio+guión, encontró "apsina...")

---

## ✅ SOLUCIÓN

### Patrón corregido v6.4.62:
```python
# Cambiar [^-]+? por .+? para capturar TODO hasta el espacio antes del guión
marcadores_con_guion_pattern = r'(?i)Los?\s+marcadores?\s+(.+?)\s+-\s+(?:son|es)\s+(negativos?|positivos?)'
```

**También eliminar `\s*\.` al final** porque:
- El punto es parte del texto normal, no debe ser obligatorio en el patrón
- Hace el patrón más restrictivo innecesariamente

### Resultado esperado con v6.4.62:
```
Grupo 1 (lista): "napsina y TTF-1"
Grupo 2 (resultado): "negativos"
```

**Procesamiento:**
1. Separar lista: `["napsina", "TTF-1"]`
2. Normalizar: `["NAPSIN", "TTF1"]`
3. Asignar: `results['NAPSIN'] = 'NEGATIVO'`, `results['TTF1'] = 'NEGATIVO'`

---

## 🔄 VALIDACIÓN DE REGRESIÓN OBLIGATORIA

**ANTES de aplicar v6.4.62, validar casos de referencia:**

| Caso | Formato | Estado Actual | Debe Mantener |
|------|---------|---------------|---------------|
| IHQ250202 | "Los marcadores X y Y - son negativos" | 88.9% | Mejorar a 100% ✅ |
| (Buscar otros casos con mismo formato) | Similar | ? | Mantener score |

**PROTOCOLO:**
1. Buscar casos con formato "Los marcadores [lista] - son [resultado]"
2. Auditar casos ANTES de modificar patrón
3. Aplicar v6.4.62
4. Reprocesar TODOS los casos detectados
5. Validar que NINGUNO baja su score

---

## 📝 ACCIÓN REQUERIDA

**PASO 1:** Modificar línea 4051 en `core/extractors/biomarker_extractor.py`:

```python
# ANTES (v6.4.61 - INCORRECTO):
marcadores_con_guion_pattern = r'(?i)Los?\s+marcadores?\s+([^-]+?)\s+-\s+(?:son|es)\s+(negativos?|positivos?)\s*\.'

# DESPUÉS (v6.4.62 - CORRECTO):
marcadores_con_guion_pattern = r'(?i)Los?\s+marcadores?\s+(.+?)\s+-\s+(?:son|es)\s+(negativos?|positivos?)'
```

**PASO 2:** Agregar comentario de versión:
```python
# V6.4.62 FIX IHQ250202: Corregido [^-]+? → .+? para capturar lista completa
# PROBLEMA v6.4.61: [^-]+? capturaba solo primer carácter (non-greedy sobre char class)
# SOLUCIÓN v6.4.62: .+? captura TODO hasta espacio antes del guión
```

**PASO 3:** Reprocesar caso IHQ250202:
```bash
python herramientas_ia/auditor_sistema.py IHQ250202 --func-06
```

**PASO 4:** Validar score mejora a 100%:
```bash
python herramientas_ia/auditor_sistema.py IHQ250202 --inteligente
```

---

## 📊 IMPACTO ESPERADO

**ANTES (v6.4.61):**
- IHQ250202: Score 88.9% ❌
- TTF1: POSITIVO (incorrecto)
- NAPSIN: NEGATIVO (correcto)

**DESPUÉS (v6.4.62):**
- IHQ250202: Score 100% ✅
- TTF1: NEGATIVO (correcto)
- NAPSIN: NEGATIVO (correcto)

---

## ⚠️ ADVERTENCIA DE REGRESIÓN

**CRÍTICO:** Este cambio modifica la captura del grupo 1 de `[^-]+?` (restrictivo) a `.+?` (más permisivo).

**Riesgo:** Si hay casos con formato ambiguo que dependían del comportamiento restrictivo de `[^-]+?`, podrían verse afectados.

**Mitigación:**
1. Buscar TODOS los casos con formato "Los marcadores ... - son ..."
2. Validar regresión en TODOS ellos
3. Si alguno baja score → revertir y replantear estrategia

---

**Reporte generado:** 2026-01-09 15:25
**Próximo paso:** Aplicar v6.4.62 y validar
