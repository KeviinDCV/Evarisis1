# REPORTE FUNC-06: IHQ250174 - Validación Patrón v6.4.36

**Fecha:** 2026-01-08 05:44
**Patrón modificado:** v6.4.36 - Captura "tinción positiva fuerte y difusa para [lista]"
**Caso reprocesado:** IHQ250174 (CÉRVIX - CARCINOMA SEROSO DE ALTO GRADO)

---

## 1. CONTEXTO DEL PATRÓN v6.4.36

### Mejoras Implementadas:
1. Acepta "tinción" además de "marcación"
2. Captura adjetivos múltiples ("fuerte y difusa")
3. Limpia calificadores ("p16 en bloque" → "p16")
4. SIEMPRE sobrescribe valores anteriores (alta confianza)

### Frase del PDF que captura:
```
"La lesión carcinomatosa invasiva de alto grado descrito demuestra una 
tinción positiva fuerte y difusa para CKAE1/AE3, PAX8, p16 en bloque y 
WT1 heterogéneo débil con sobre-expresión de p53 (mutado)."
```

---

## 2. COMPARACIÓN ANTES vs DESPUÉS DEL REPROCESAMIENTO

### Biomarcadores Problemáticos:

| Biomarcador | ANTES (v6.4.35) | DESPUÉS (v6.4.36) | ESPERADO | ESTADO |
|-------------|-----------------|-------------------|----------|---------|
| **IHQ_PAX8** | `NEGATIVO` ❌ | `POSITIVO` ✅ | `POSITIVO` | **CORREGIDO** ✅ |
| **IHQ_P16_ESTADO** | `NEGATIVO` ❌ | `POSITIVO` ✅ | `POSITIVO` | **CORREGIDO** ✅ |
| **IHQ_WT1** | `NEGATIVO` ❌ | `POSITIVO` ✅ | `POSITIVO` | **CORREGIDO** ✅ |
| **IHQ_RECEPTOR_PROGESTERONA** | `, CEA Y NAPSINA` ❌ | `, CEA Y NAPSINA` ❌ | `NEGATIVO` | **PENDIENTE** ⚠️ |

### Biomarcadores Correctos (Sin cambio):

| Biomarcador | ANTES | DESPUÉS | ESTADO |
|-------------|-------|---------|--------|
| IHQ_CKAE1AE3 | `POSITIVO (fuerte y difusa)` | `POSITIVO (fuerte y difusa)` | ✅ CORRECTO |
| IHQ_P53 | `POSITIVO` | `POSITIVO` | ✅ CORRECTO |
| IHQ_RECEPTOR_ESTROGENOS | `NEGATIVO` | `NEGATIVO` | ✅ CORRECTO |

---

## 3. ANÁLISIS DE RESULTADOS

### ✅ ÉXITOS (3/4 biomarcadores corregidos):

1. **IHQ_PAX8:** `NEGATIVO` → `POSITIVO`
   - **Causa raíz anterior:** Patrón no capturaba "tinción positiva fuerte y difusa"
   - **Solución v6.4.36:** Nuevo patrón específico para "tinción" + adjetivos múltiples
   - **Evidencia:** "tinción positiva fuerte y difusa para CKAE1/AE3, PAX8..."

2. **IHQ_P16_ESTADO:** `NEGATIVO` → `POSITIVO`
   - **Causa raíz anterior:** Calificador "p16 en bloque" no era capturado
   - **Solución v6.4.36:** Limpieza de calificadores ("en bloque" se remueve)
   - **Evidencia:** "p16 en bloque" → extractor detecta "p16" limpio

3. **IHQ_WT1:** `NEGATIVO` → `POSITIVO`
   - **Causa raíz anterior:** Calificador "heterogéneo débil" interfería
   - **Solución v6.4.36:** Limpieza de calificadores post-nombre
   - **Evidencia:** "WT1 heterogéneo débil" → extractor detecta "WT1" limpio

### ⚠️ PROBLEMA PENDIENTE (1/4):

**IHQ_RECEPTOR_PROGESTERONA:** Sigue con valor incorrecto `, CEA Y NAPSINA`

**Causa raíz:**
- El biomarcador está en la frase de **NEGATIVOS**, no en la frase de positivos
- Frase correcta: "Son negativas para RECEPTORES DE ESTRÓGENOS, **RECEPTORES DE PROGESTERONA**, CEA y NAPSINA."
- El patrón v6.4.36 solo captura positivos ("tinción positiva fuerte y difusa para...")
- El extractor de negativos NO está limpiando correctamente el valor

**Valor esperado:** `NEGATIVO`
**Valor actual:** `, CEA Y NAPSINA` (fragmento incorrecto de la lista)

**Solución requerida:**
- Modificar el extractor de negativos para limpiar listas correctamente
- El patrón debe detectar "RECEPTORES DE PROGESTERONA" en la lista de negativos
- Asignar valor `NEGATIVO` limpio (sin fragmentos de otros biomarcadores)

---

## 4. IMPACTO EN SCORE DE VALIDACIÓN

### Score ANTES del reprocesamiento:
- **100.0%** (falso positivo - valores incorrectos no detectados)

### Score DESPUÉS del reprocesamiento:
- **100.0%** (3 biomarcadores corregidos, 1 pendiente)

**Nota:** El auditor no detecta el problema de IHQ_RECEPTOR_PROGESTERONA porque:
- El campo `Factor pronostico` no valida formato individual de cada biomarcador
- El auditor valida presencia, no formato exacto de valores

---

## 5. CONCLUSIONES Y PRÓXIMOS PASOS

### ✅ LOGROS v6.4.36:
- **75% de biomarcadores corregidos** (3/4)
- PAX8, P16, WT1 ahora extraen correctamente desde frase de positivos
- Patrón robusto para "tinción" + adjetivos múltiples funciona

### ⚠️ PENDIENTE v6.4.37:
- Corregir extractor de **negativos** para limpiar listas correctamente
- IHQ_RECEPTOR_PROGESTERONA debe ser `NEGATIVO`, no `, CEA Y NAPSINA`
- Aplicar limpieza similar a la de positivos (remover fragmentos de lista)

### 📋 ACCIÓN REQUERIDA:
```python
# En biomarker_extractor.py o medical_extractor.py
# Buscar función que extrae negativos y agregar limpieza de listas:

# V6.4.37 FIX IHQ250174: Limpiar listas de negativos
# Patrón actual captura: "RECEPTORES DE PROGESTERONA, CEA y NAPSINA"
# Debe extraer SOLO: "RECEPTORES DE PROGESTERONA" → NEGATIVO

# Solución: Split por coma y procesar cada biomarcador individualmente
```

---

**Reporte generado por:** data-auditor (FUNC-06)
**Timestamp:** 2026-01-08T05:44:26
**Versión extractor:** 6.4.36 → 6.4.37 (pendiente)
