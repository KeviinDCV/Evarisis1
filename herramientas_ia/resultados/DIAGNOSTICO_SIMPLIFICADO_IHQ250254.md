# 🔍 DIAGNÓSTICO SIMPLIFICADO: Por qué SALL-4 y EMA no se capturan

**Fecha:** 2026-01-28
**Caso:** IHQ250254

---

## 📋 EXPLICACIÓN SIMPLE

Hay **DOS problemas separados**:

### 1️⃣ **PROBLEMA 1: Descripción Macroscópica → IHQ_ESTUDIOS_SOLICITADOS**

**¿Qué dice el PDF?**
```
"se realizan niveles histológicos para tinción en el especimen A2:
EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX- 8, Ki67, S100, CKAE1E3, p53"
```

**¿Qué debería extraerse?**
```
IHQ_ESTUDIOS_SOLICITADOS = "EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX-8, Ki-67, S100, CKAE1AE3, P53"
```

**¿Qué se extrae actualmente?**
```
IHQ_ESTUDIOS_SOLICITADOS = "CKAE1AE3, DESMIN, Ki-67, P53, PAX8, Receptor de Estrógeno, S100, WT1"
```
❌ **Faltan: SALL-4 y EMA**

**¿Por qué falla?**

El patrón en `medical_extractor.py` (línea 2367) busca:
```
"para tinción con [lista]"
```

Pero el PDF dice:
```
"para tinción en el especimen A2: [lista]"
```

**NO** tiene "con", tiene "en el especimen A2:". El patrón NO hace match, entonces usa un **fallback** que construye la lista desde los biomarcadores encontrados en la descripción microscópica (que NO incluye SALL-4 y EMA porque tampoco se extrajeron ahí).

---

### 2️⃣ **PROBLEMA 2: Descripción Microscópica → Columnas IHQ_SALL4 e IHQ_EMA**

**¿Qué dice el PDF?**
```
"un componente epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
```

**¿Qué debería extraerse?**
```
IHQ_SALL4 = "POSITIVO (FOCAL)"
IHQ_EMA = "POSITIVO (FOCAL)"
```

**¿Qué se extrae actualmente?**
```
IHQ_SALL4 = (no existe)
IHQ_EMA = (no existe)
```

**¿Por qué falla?**

El patrón en `biomarker_extractor.py` (línea 9230) tiene clase de caracteres:
```python
[\w\s/.\-+]  # NO incluye ()
```

Cuando encuentra "SALL 4 (", se detiene porque `(` NO está permitido.

**YA CORREGIMOS ESTO** en v6.5.58 agregando `()` a la clase:
```python
[\w\s/.\-+()\n]  # ✅ Ahora incluye ()
```

---

## 🎯 SOLUCIÓN COMPLETA

### ✅ **Problema 2: SOLUCIONADO**

Ya aplicamos el FIX v6.5.58 que permite capturar paréntesis.

### ⚠️ **Problema 1: FALTA SOLUCIONAR**

Necesitamos agregar un **patrón nuevo** en `medical_extractor.py` para capturar formato:
```
"para tinción en el especimen [X]: [lista]"
```

**Ubicación:** `medical_extractor.py`, función `extract_biomarcadores_solicitados_robust()`, línea ~2276

**Patrón a agregar:**
```python
# V6.5.59 FIX IHQ250254: "para tinción en el especimen [X]: [lista]"
# Formato: "se realizan niveles histológicos para tinción en el especimen A2: EMA, DESMINA, SALL-4, ..."
# DEBE IR ANTES del patrón genérico "para tinción con" para ejecutarse primero
r'se\s+realizan?\s+(?:cortes?|niveles?)\s+histol[óo]gicos?\s+para\s+(?:la\s+)?tinci[óo]n\s+en\s+(?:el\s+)?(?:especimen|espécimen|bloque)\s+[A-Z0-9]+:\s*([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ\n]+?)(?:\.|$|y\s+en\s+el\s+especimen)',
```

**Explicación:**
- `se\s+realizan?\s+(?:cortes?|niveles?)` → "se realiza" o "se realizan niveles/cortes"
- `histol[óo]gicos?\s+para\s+(?:la\s+)?tinci[óo]n` → "histológicos para tinción" o "para la tinción"
- `\s+en\s+(?:el\s+)?(?:especimen|espécimen|bloque)\s+[A-Z0-9]+:` → "en el especimen A2:" o "en bloque B1:"
- `\s*([A-Z0-9\s,./\-\(\)yYóÓúÚáÁéÉíÍ\n]+?)` → captura la lista (AHORA con paréntesis incluidos)
- `(?:\.|$|y\s+en\s+el\s+especimen)` → termina en punto, fin de texto, o cuando dice "y en el especimen B1"

**Terminador especial:**
`y\s+en\s+el\s+especimen` porque el PDF dice:
```
"...en el especimen A2: EMA, DESMINA, SALL-4, ... p53 y en el especimen B1: SALL 4, ..."
```

Hay DOS listas (especimen A2 y B1) que deben capturarse por separado.

---

## 🔄 FLUJO COMPLETO DE EXTRACCIÓN

```
PDF
 │
 ├─ DESCRIPCIÓN MACROSCÓPICA: "para tinción en el especimen A2: EMA, DESMINA, SALL-4, ..."
 │   │
 │   └─ extract_biomarcadores_solicitados_robust()  [medical_extractor.py]
 │       │
 │       └─ Patrón captura lista: "EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX-8, ..."
 │           │
 │           └─ IHQ_ESTUDIOS_SOLICITADOS = "EMA, DESMINA, SALL-4, ..." ✅
 │
 ├─ DESCRIPCIÓN MICROSCÓPICA: "positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
 │   │
 │   └─ extract_narrative_biomarkers()  [biomarker_extractor.py]
 │       │
 │       └─ Patrón línea 9230 (YA CORREGIDO v6.5.58) captura: "CKAE1/AE3, PAX 8, SALL 4 (focal), P53, EMA (focal)"
 │           │
 │           ├─ IHQ_SALL4 = "POSITIVO (FOCAL)" ✅
 │           └─ IHQ_EMA = "POSITIVO (FOCAL)" ✅
 │
 └─ RESULTADO FINAL:
     ├─ IHQ_ESTUDIOS_SOLICITADOS: "EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX-8, Ki-67, S100, CKAE1AE3, P53" ✅
     ├─ IHQ_SALL4: "POSITIVO (FOCAL)" ✅
     └─ IHQ_EMA: "POSITIVO (FOCAL)" ✅
```

---

## 📝 PRÓXIMOS PASOS

1. **Agregar patrón nuevo** en `medical_extractor.py` línea ~2276
2. **Reprocesar IHQ250254** con FUNC-06
3. **Validar** que ambos problemas estén resueltos:
   - `IHQ_ESTUDIOS_SOLICITADOS` incluye SALL-4 y EMA
   - `IHQ_SALL4` y `IHQ_EMA` tienen valores "POSITIVO (FOCAL)"

---

## 🎯 ¿POR QUÉ ES TAN COMPLICADO?

**Respuesta corta:** Porque hay **múltiples variantes** de cómo los médicos escriben los informes.

**Variantes conocidas:**
1. "para tinción **con** [lista]"
2. "para tinción **en el especimen A2:** [lista]"
3. "para **marcación con** [lista]"
4. "se **revisa marcación para** [lista]"
5. "se **solicitan coloraciones** con [lista]"
6. ... y ~20 más

Cada variante requiere un patrón regex específico. El sistema tiene que:
1. Capturar **TODAS** las variantes posibles
2. **NO** capturar falsos positivos (ej: "para tinción con azul de Prusia" no es un biomarcador)
3. Manejar formatos con **saltos de línea**, **paréntesis**, **guiones**, **espacios inconsistentes**

**Por eso** tenemos:
- **~30 patrones** en `extract_biomarcadores_solicitados_robust()`
- **~50 patrones** en `extract_narrative_biomarkers()`
- Múltiples capas de normalización y validación

Cada vez que encontramos un nuevo formato (como "en el especimen A2:"), agregamos un patrón nuevo.

---

**FIN DEL DIAGNÓSTICO SIMPLIFICADO**
