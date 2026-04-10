# ANALISIS CRITICO: SALL-4 y EMA NO CAPTURADOS - IHQ250254
**Fecha:** 2026-01-28
**Caso:** IHQ250254
**Versión sistema:** v6.5.x

## RESUMEN EJECUTIVO

**PROBLEMA CONFIRMADO:** Los biomarcadores **SALL-4** y **EMA** están presentes en el PDF pero NO se están capturando en columnas individuales de la base de datos.

**Score auditoría:** 100% (FALSA COMPLETITUD)
- El sistema reporta 100% porque no detecta que estos biomarcadores deberían estar capturados
- Los biomarcadores están en el texto pero no se están extrayendo

## 1. EVIDENCIA DEL PDF (OCR)

### 1.1 DESCRIPCION MACROSCOPICA (Biomarcadores solicitados)
Texto del PDF:
Previa revisión de la histología, se realizan niveles histológicos para tinción en el especimen A2:
EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX- 8, Ki67, S100, CKAE1E3, p53 
y en el especimen B1: SALL 4, CKAE1/AE3, PAX8 y KI67

**SALL-4 SOLICITADO:** Aparece en 2 lugares
- Especimen A2: SALL-4 (con guion)
- Especimen B1: SALL 4 (con espacio)

**EMA SOLICITADO:** Aparece en especimen A2

### 1.2 DESCRIPCION MICROSCOPICA (Resultados de biomarcadores)
Texto del PDF:
En el espécimen A2:
Las células tumorales presentan una marcación bifásica, un componente
epitelial positivo para CKAE1/AE3, PAX 8, SALL 4 (focal), p53, EMA (focal) 
y el componente mesenquimal es positivo para S100..

**SALL-4 RESULTADO:** SALL 4 (focal) = POSITIVO FOCAL

**EMA RESULTADO:** EMA (focal) = POSITIVO FOCAL

## 2. ESTADO EN BASE DE DATOS

### 2.1 Columnas extraídas
Biomarcadores EN base de datos:
- IHQ_CKAE1AE3: POSITIVO
- IHQ_DESMIN: POSITIVO
- IHQ_KI-67: 80%
- IHQ_P53: POSITIVO
- IHQ_PAX8: POSITIVO
- IHQ_RECEPTOR_ESTROGENOS: POSITIVO
- IHQ_S100: POSITIVO
- IHQ_WT1: POSITIVO

**AUSENTES:**
- IHQ_SALL4 o IHQ_SALL-4 → NO existe en BD
- IHQ_EMA → NO existe en BD

### 2.2 Campo IHQ_ESTUDIOS_SOLICITADOS
IHQ_ESTUDIOS_SOLICITADOS: CKAE1AE3, DESMIN, Ki-67, P53, PAX8, Receptor de Estrógeno, S100, WT1

**AUSENTES:**
- SALL-4 NO aparece en lista de estudios solicitados
- EMA NO aparece en lista de estudios solicitados

## 3. ANALISIS DE CAUSA RAIZ

### 3.1 SALL-4

**Problema 1: Variantes ortográficas**
- PDF tiene 3 variantes:
  - SALL-4 (con guion)
  - SALL 4 (con espacio)
  - SALLL4 (con 3 L - error tipográfico)

**Problema 2: Columna NO existe en database_manager.py**
**Problema 3: Alias NO existe en validation_checker.py**
**Problema 4: Patrón de extracción NO captura en biomarker_extractor.py**

### 3.2 EMA

**Problema 1: Columna NO existe en database_manager.py**
**Problema 2: Alias NO existe en validation_checker.py**
**Problema 3: Patrón de extracción NO captura en biomarker_extractor.py**

## 4. DIAGNOSTICO TECNICO

### 4.1 Problema Sistémico
Este NO es un problema aislado de IHQ250254. Es un problema GENERAL del sistema:

**FALTA DE MAPEO COMPLETO:**
- El sistema tiene aproximadamente 92 columnas IHQ_*
- Pero MUCHOS biomarcadores usados en la práctica NO están mapeados
- SALL-4 y EMA son biomarcadores COMUNES en patología oncológica
- El sistema está incompleto para casos reales

### 4.2 Confirmación de Falsa Completitud
Score auditoría: 100%
Biomarcadores solicitados en OCR: 10 (EMA, DESMINA, SALL-4, ESTROGENO, WT1, PAX-8, Ki67, S100, CKAE1E3, p53)
Biomarcadores capturados en BD: 8 (DESMIN, WT1, ESTROGENO, PAX8, Ki67, S100, CKAE1AE3, p53)
Biomarcadores faltantes: 2 (SALL-4, EMA)
Cobertura REAL: 8/10 = 80% (NO 100%)

**POR QUÉ el auditor reporta 100%:**
- FUNC-01 valida que los biomarcadores EN BD estén correctos (8/8 OK)
- Pero NO detecta que faltan biomarcadores del OCR porque IHQ_ESTUDIOS_SOLICITADOS también está incompleto
- Es un problema en CASCADA:
  1. biomarker_extractor.py NO extrae SALL-4 ni EMA → IHQ_ESTUDIOS_SOLICITADOS incompleto
  2. unified_extractor.py NO mapea SALL-4 ni EMA → Columnas IHQ_* vacías
  3. FUNC-01 compara BD contra IHQ_ESTUDIOS_SOLICITADOS → Ambos incompletos → NO detecta faltante

## 5. SOLUCION PROPUESTA

### 5.1 PASO 1: Agregar SALL-4 al sistema (FUNC-03)
Usar auditor.agregar_biomarcador() con variantes:
- SALL4, SALL-4, SALL 4 (variantes normales)
- SALLL4, SALL- 4, SALL -4 (variantes con errores)

FUNC-03 modificará automáticamente 6 archivos:
1. core/database_manager.py → Columna IHQ_SALL4
2. herramientas_ia/auditor_sistema.py → BIOMARKER_ALIAS_MAP
3. ui.py → Columnas visibles
4. core/validation_checker.py → all_biomarker_mapping
5. core/extractors/biomarker_extractor.py → Patrones extracción
6. core/unified_extractor.py → Mapeos

### 5.2 PASO 2: Agregar EMA al sistema (FUNC-03)
Usar auditor.agregar_biomarcador() con variantes:
- EMA, E.M.A., E MA
- EPITHELIAL MEMBRANE ANTIGEN (nombre completo)

### 5.3 PASO 3: Regenerar BD y Reprocesar (FUNC-06)
1. Borrar BD: rm data/huv_oncologia_NUEVO.db
2. Reprocesar: python herramientas_ia/auditor_sistema.py IHQ250254 --func-06

FUNC-06 hará:
- Buscar PDF que contiene IHQ250254
- Eliminar datos antiguos del rango
- Reprocesar PDF completo con extractores ACTUALIZADOS
- Re-auditar caso
- Generar reporte comparativo

### 5.4 PASO 4: Validar Extracción Correcta
Esperado después de reprocesar:
- IHQ_SALL4: POSITIVO FOCAL (especimen A2)
- IHQ_EMA: POSITIVO FOCAL (especimen A2)
- IHQ_ESTUDIOS_SOLICITADOS debe incluir SALL-4 y EMA

## 6. IMPACTO ESTIMADO

Total casos afectados estimado: 20-50 casos (5-10% del total)
Completitud actual: aproximadamente 95%
Completitud después: aproximadamente 97%
Casos que subirán de <100% a 100%: aproximadamente 20-30 casos

PRIORIDAD: ALTA
MOTIVO: Biomarcadores COMUNES en patología oncológica
IMPACTO: Múltiples casos afectados
DIFICULTAD: BAJA (FUNC-03 automatiza todo)
TIEMPO ESTIMADO: 15-20 minutos

## 7. SIGUIENTE PASO INMEDIATO

DECISION DEL USUARIO requerida:

Opción 1: Agregar ahora (RECOMENDADO)
- Ejecutar FUNC-03 para SALL-4 y EMA
- Regenerar BD
- Reprocesar casos

Opción 2: Investigar primero
- Buscar cuántos casos tienen SALL-4 y EMA
- Ver impacto real antes de actuar

Opción 3: Aceptar como está
- Registrar como limitación conocida
- Documentar para futuro
