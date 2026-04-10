# REPORTE DE REPROCESAMIENTO - CASO IHQ251011

**Fecha:** 2025-11-04 20:10:00
**PDF procesado:** pdfs_patologia/IHQ DEL 980 AL 1037.pdf
**Total casos procesados:** 48 casos (rango 980-1037)
**BD regenerada:** SI
**Columnas nuevas creadas:** IHQ_IDH1, IHQ_ATRX

---

## 1. RESUMEN EJECUTIVO

El reprocesamiento se ejecuto exitosamente con los siguientes resultados:

- **Columnas nuevas:** IHQ_IDH1 y IHQ_ATRX fueron creadas en la BD correctamente
- **Patrones corregidos:** 2 de 4 errores fueron corregidos
- **Biomarcadores existentes:** Se mantuvieron correctos (GFAP, CD34)
- **Score final:** 50.0% (3/6 campos correctos)

---

## 2. TABLA COMPARATIVA: ANTES vs DESPUES

| Biomarcador | ANTES | DESPUES | ESPERADO | ESTADO |
|-------------|-------|---------|----------|--------|
| **IHQ_IDH1** | NO EXISTIA | N/A | POSITIVO (MUTADO) | COLUMNA CREADA PERO NO EXTRAE |
| **IHQ_ATRX** | NO EXISTIA | N/A | NEGATIVO (AUSENCIA DE EXPRESION) | COLUMNA CREADA PERO NO EXTRAE |
| **IHQ_P53** | , GFAP, KI67 Y CD34 | CONTRIBUTIVA | NO CONTRIBUTIVA | CORREGIDO PARCIALMENTE |
| **IHQ_KI-67** | NO MENCIONADO | 10% | 10% | CORRECTO |
| **IHQ_GFAP** | POSITIVO | POSITIVO | POSITIVO | CORRECTO |
| **IHQ_CD34** | NEGATIVO | NEGATIVO | NEGATIVO | CORRECTO |

---

## 3. ANALISIS DETALLADO POR CAMPO

### 3.1 IHQ_IDH1 - COLUMNA CREADA PERO NO EXTRAE

**Estado:** Columna existe en BD pero valor no se extrae del PDF

**ANTES:**
- Columna NO existia en el sistema

**DESPUES:**
- Columna IHQ_IDH1 creada en BD
- Valor extraido: N/A (no se encontro en PDF o patron fallo)

**ESPERADO:**
- Valor: POSITIVO (MUTADO) o MUTADO

**ACCION REQUERIDA:**
- Verificar si el PDF contiene el valor de IDH1
- Si existe en PDF: Corregir patron de extraccion en biomarker_extractor.py
- Si no existe en PDF: El valor N/A es correcto

---

### 3.2 IHQ_ATRX - COLUMNA CREADA PERO NO EXTRAE

**Estado:** Columna existe en BD pero valor no se extrae del PDF

**ANTES:**
- Columna NO existia en el sistema

**DESPUES:**
- Columna IHQ_ATRX creada en BD
- Valor extraido: N/A (no se encontro en PDF o patron fallo)

**ESPERADO:**
- Valor: NEGATIVO (AUSENCIA DE EXPRESION) o MUTADO

**ACCION REQUERIDA:**
- Verificar si el PDF contiene el valor de ATRX
- Si existe en PDF: Corregir patron de extraccion en biomarker_extractor.py
- Si no existe en PDF: El valor N/A es correcto

---

### 3.3 IHQ_P53 - CORREGIDO PARCIALMENTE

**Estado:** Mejoro pero aun no es exacto

**ANTES:**
- Valor erroneo: ", GFAP, KI67 Y CD34"
- Problema: Extractor capturaba lista de biomarcadores en lugar del valor

**DESPUES:**
- Valor extraido: "CONTRIBUTIVA"
- Mejora: Ya no captura lista erronea

**ESPERADO:**
- Valor exacto: "NO CONTRIBUTIVA"

**ACCION REQUERIDA:**
- Verificar en PDF si dice "CONTRIBUTIVA" o "NO CONTRIBUTIVA"
- Si dice "NO CONTRIBUTIVA": Ajustar patron para capturar el "NO"

---

### 3.4 IHQ_KI-67 - CORREGIDO

**Estado:** CORRECTO

**ANTES:**
- Valor: "NO MENCIONADO"
- Problema: Patron no detectaba el valor

**DESPUES:**
- Valor extraido: "10%"
- Resultado: CORRECTO

**ACCION:** Ninguna (campo corregido exitosamente)

---

### 3.5 IHQ_GFAP - MANTIENE CORRECTO

**Estado:** CORRECTO

**ANTES:** POSITIVO (correcto)
**DESPUES:** POSITIVO (mantiene)
**ACCION:** Ninguna (campo ya estaba correcto)

---

### 3.6 IHQ_CD34 - MANTIENE CORRECTO

**Estado:** CORRECTO

**ANTES:** NEGATIVO (correcto)
**DESPUES:** NEGATIVO (mantiene)
**ACCION:** Ninguna (campo ya estaba correcto)

---

## 4. METRICAS DE VALIDACION

**Campos evaluados:** 6
**Correctos:** 3 (50.0%)
**Corregidos:** 1 (IHQ_KI-67)
**Corregidos parcialmente:** 1 (IHQ_P53)
**Pendientes:** 2 (IHQ_IDH1, IHQ_ATRX)

**Score de validacion final:** 50.0%

---

## 5. SIGUIENTES PASOS

### 5.1 PRIORIDAD ALTA

1. **Verificar valores en PDF original**
   - Confirmar si IDH1 y ATRX estan en el PDF del caso IHQ251011
   - Confirmar si P53 dice "CONTRIBUTIVA" o "NO CONTRIBUTIVA"

2. **Ajustar patrones de extraccion**
   - Si IDH1/ATRX estan en PDF: Crear/ajustar patrones en biomarker_extractor.py
   - Si P53 tiene "NO": Ajustar patron para capturar negacion

### 5.2 PRIORIDAD MEDIA

3. **Reprocesar caso despues de correcciones**
   - Ejecutar nuevamente FUNC-06 despues de ajustar patrones
   - Validar que score suba a 100%

4. **Validar otros casos del rango**
   - Verificar que los 48 casos procesados no tengan el mismo problema
   - Ejecutar auditoria masiva con data-auditor

---

## 6. EVIDENCIA TECNICA

**Ruta BD:** data/huv_oncologia_NUEVO.db
**Total casos en BD:** 48
**Columnas IHQ_* totales:** 110 (incluye IDH1 y ATRX nuevas)

**Consulta ejecutada:**


**Resultado:**
- IHQ_IDH1: N/A
- IHQ_ATRX: N/A
- IHQ_P53: CONTRIBUTIVA
- IHQ_KI-67: 10%
- IHQ_GFAP: POSITIVO
- IHQ_CD34: NEGATIVO

---

**Reporte generado automaticamente por data-auditor (FUNC-06)**
