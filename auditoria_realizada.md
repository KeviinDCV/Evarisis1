# 📋 Plan de Auditoría - Casos Procesados

**Fecha de inicio:** 2025-12-02
**Responsable:** Equipo HUV
**Sistema:** EVARISIS - Gestión Oncológica

---

## 📊 Resumen General

| Estado | Casos Procesados | Casos Auditados | Pendientes de Auditoría |
|--------|------------------|-----------------|-------------------------|
| 🔄 | 344* | 300 | 44 |

*Nota: 3 números de caso faltantes (IHQ250243 no existe en PDF, IHQ250269 y IHQ250288 no procesados)

---

## 📁 Archivo 1: IHQ DEL 001 AL 050

**Ubicación:** `pdfs_patologia/IHQ DEL 001 AL 050.pdf`
**Estado:** ✅ REPROCESADO COMPLETO - 2025-12-12 (v6.4.1)
**Rango:** IHQ250001 - IHQ250050
**Cambios:** Biomarcador ACTINA_MUSCULO_LISO agregado al sistema

### ✅ Casos Auditados Completamente (50/50)

### IHQ250228 - 2026-01-28 04:18:57
**Score:** 88.9%
**Estado:** OK
**Versión:** v6.5.01
**Cambios validados:**
- ✅ GLIPICAN: NEGATIVO (mapeo agregado validation_checker.py V1.0.10)
- ✅ EMA: POSITIVO FOCAL (ya corregido v6.4.98)
- ⚠️ AFP sin columna (1 caso, no prioritario)
- ⚠️ CKAE1AE3 extra (no crítico)

**Mejora:** 77.8% → 88.9% (+11.1%)
**Método:** FUNC-06 (reprocesamiento completo rango 212-262)
**Reporte:** herramientas_ia/resultados/VALIDACION_FIX_v6.5.01_IHQ250228.md

### IHQ250229 - 2026-01-28 05:14:22
**Score:** 77.8%
**Estado:** OK con pendientes
**Versión:** v6.5.03 (extractores) + v6.5.04 (auditor)
**Cambios implementados:**
- ✅ P16: NEGATIVO - Patrón "presenta marcación...(...)" agregado (biomarker_extractor.py)
- ✅ Ki-67: NEGATIVO (marcación basal) - Normalizaciones UPPERCASE agregadas
- ✅ Auditor: Fix truncamiento P16 (auditor_sistema.py v6.5.04)

**Problemas pendientes:**
- ⚠️ DIAGNOSTICO_COLORACION: "NO APLICA" (debería extraer "CERVICITIS AGUDA")
- ⚠️ MALIGNIDAD: "MALIGNO" (lesión bajo grado normalmente BENIGNO)

**Tipo de caso:** Estudio cervical IHQ (P16 + Ki-67)
**Formato especial:** "presenta marcación [descripción] (resultado)"
**Método:** FUNC-06 (reprocesamiento v6.5.03) + FUNC-01 (validación v6.5.04)
**Reporte:** herramientas_ia/resultados/auditoria_inteligente_IHQ250229.json

---

| # | Número de Caso | Estado Auditoría | Fecha | Observaciones |
|---|----------------|------------------|-------|---------------|
| 1 | IHQ250001 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 2 | IHQ250002 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 3 | IHQ250003 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 4 | IHQ250004 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 5 | IHQ250005 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 6 | IHQ250006 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 7 | IHQ250007 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 8 | IHQ250008 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 9 | IHQ250009 | ✅ Auditado | 2025-12-02 | Auditoría completada |
| 10 | IHQ250010 | ✅ Auditado | 2025-12-02 | Score: 100.0% |
| 11 | IHQ250011 | ✅ Auditado | 2025-12-02 | Score: 100.0% - Correcciones v6.3.9 |
| 12 | IHQ250012 | ✅ Auditado | 2025-12-04 | Score: 100.0% - v6.4.0 (MPO, CICLINA_D1, CD61 completos) |
| 13 | IHQ250013 | ✅ Auditado | 2025-12-05 | Score: 100.0% - v6.4.0 (DIAGNOSTICO_COLORACION y MALIGNIDAD corregidos) |
| 14 | IHQ250014 | ✅ Auditado | 2025-12-09 | Score: 100.0% - v6.3.13/14/15 (DIAGNOSTICO_COLORACION, KI-67, MALIGNIDAD corregidos) |
| 15 | IHQ250015 | ✅ Auditado | 2025-12-09 | Score: 100.0% - v3.3.3/3.3.4 (Auditor mejorado: normalización OCR y plural "diagnósticos") |
| 16 | IHQ250016 | ✅ Auditado | 2025-12-09 | Score: 88.9% → 100%* - Descripción reconstruida correctamente (warning menor de formato) |
| 17 | IHQ250017 | ✅ Auditado | 2025-12-09 | Score: 100.0% - v6.3.20/21/22 + v3.3.5 (HER2 score completo, MMR prioridad secciones, PMS2 normalizado, corrección ortográfica) |
| 18 | IHQ250018 | ✅ Auditado | 2025-12-12 | Score: 100%* - v6.4.1 (ACTINA_MUSCULO_LISO agregado, DOG1=POSITIVO confirmado) |
| 19 | IHQ250019 | ✅ Auditado | 2025-12-13 | Score: 100.0% - v6.3.21 (P63 alias "p65", MOSAICO(NORMAL)→POSITIVO, DIAGNOSTICO_PRINCIPAL filtro COMENTARIOS, Patrón 0C sin guión) |
| 20 | IHQ250020 | ✅ Auditado | 2025-12-13 | Score: 100.0% - Carcinoma escamocelular oral no queratinizante |
| 21 | IHQ250021 | ✅ Auditado | 2025-12-13 | Score: 100.0% - v6.3.22 (Patrón 0D para diagnósticos descriptivos: TÉJIDO SIN REPRESENTACIÓN DE PARENQUIMA RENAL) |
| 22 | IHQ250022 | ✅ Auditado | 2025-12-13 | Score: 100%* - v6.3.23+v6.3.24 (DIAGNOSTICO_COLORACION correcto, biomarcadores limpios sin contaminación, 2 warnings falsos positivos del auditor) |
| 23 | IHQ250023 | ✅ Auditado | 2025-12-13 | Score: 100.0% - v6.3.25 (Patrón 1A1 "LOS HALLAZGOS SON SUGESTIVOS DE": NEOPLASIA EN PATRON ACINAR CON CAMBIOS ONCOCITICOS) |
| 24 | IHQ250024 | ✅ Auditado | 2025-12-13 | Score: 88.9% - v6.3.26 (limpiar_diagnostico elimina GRADO HISTOLÓGICO y NOTTINGHAM del diagnóstico principal) |
| 25 | IHQ250025 | ✅ Auditado | 2025-12-13 | Score: 88.9% - Adenocarcinoma pulmonar (1 warning falso positivo: diagnóstico IHQ vs coloración son diferentes estudios) |
| 26 | IHQ250026 | ✅ Auditado | 2025-12-13 | Score: 100.0% - Melanoma pulmonar (8 biomarcadores) |
| 27 | IHQ250027 | ✅ Auditado | 2025-12-13 | Score: 100.0% - Carcinoma escamocelular lengua (Ki-67 90%) |
| 28 | IHQ250028 | ✅ Auditado | 2025-12-13 | Score: 100.0% - v6.3.27+v6.3.28+v6.3.29 (HER2 limpio, corrector espacios OCR, auditor umbral 60%) |
| 29 | IHQ250029 | ✅ Auditado | 2025-12-13 | Score: 100.0% - Linfoma de células B maduras vertebra L1 (9 biomarcadores) |
| 30 | IHQ250030 | ✅ Auditado | 2025-12-13 | Score: 100.0% - Mieloma múltiple médula ósea (CD56, CD117) |
| 31 | IHQ250031 | ✅ Auditado | 2025-12-15 | Score: 100.0% - v6.3.36+v6.3.37 (HER2=EQUIVOCO preservado, Diagnóstico Principal=ADENOCARCINOMA GÁSTRICO desde "Historia de") |
| 32 | IHQ250032 | ✅ Auditado | 2025-12-15 | Score: 100.0% - v6.3.38 (TDT y CK19 agregados a biomarker_display_names, TIMOMA TIPO B2, 7 biomarcadores) |
| 33 | IHQ250033 | ✅ Auditado | 2025-12-15 | Score: 100.0% - v6.3.39 (Sync columnas alias: SYNAPTOFISINA/CKAE1E3, CARCINOIDE TÍPICO pulmón, 8 biomarcadores) |
| 34 | IHQ250034 | ✅ Auditado | 2025-12-15 | Score: 100.0% - v6.3.40 (Captura descripción microscópica página 2: MAMAGLOBINA/GATA3, CARCINOMA METASTÁSICO mama) |
| 35 | IHQ250035 | ✅ Auditado | 2025-12-16 | Score: 100.0% - v6.3.42 (Exclusión MMR del extractor narrativo: MLH1/MSH2/MSH6/PMS2, Adenocarcinoma sigmoides, HER2=NEGATIVO score 0) |
| 36 | IHQ250036 | ✅ Auditado | 2025-12-16 | Score: 100.0% - Carcinoma poco cohesivo mucosa estómago (6 biomarcadores: MLH1/PMS2/MSH2/MSH6/HER2/CKAE1AE3) |
| 37 | IHQ250037 | ✅ Auditado | 2025-12-16 | Score: 100.0% - v6.3.44 (HHV8/CD34 agregados, patrón "QUE FAVORECEN", normalización "expresión para"→POSITIVO) COLITIS AGUDA Y CRÓNICA NO ESPECÍFICA |
| 38 | IHQ250038 | ✅ Auditado | 2025-12-16 | Score: 100.0% - Adenocarcinoma rectal con panel MMR (MLH1/MSH2/MSH6/PMS2), PATRÓN MICROSATELITAL ESTABLE |
| 39 | IHQ250039 | ✅ Auditado | 2025-12-17 | Score: 100.0% - v6.3.45 (P63/CK5_6 paréntesis invertidos, RE marcación difusa) CARCINOMA DUCTAL IN SITU mama (3 biomarcadores: P63/CK5_6/RE) |
| 40 | IHQ250040 | ✅ Auditado | 2025-12-17 | Score: 100.0% - CRANEOFARINGIOMA ADAMANTINOMATOSO región clivus (5 biomarcadores: CK7/Ki67<1%/RP-/S100/SOX10) |
| 41 | IHQ250041 | ✅ Auditado | 2025-12-17 | Score: 100.0% - CARCINOMA ESCAMOCELULAR INVASIVO cuero cabelludo (1 biomarcador: P40+) |
| 42 | IHQ250042 | ✅ Auditado | 2025-12-17 | Score: 100%* - v6.3.46 (SV40/C4D trasplante renal) RECHAZO INJERTO RENAL postrasplante (2 biomarcadores: SV40-/C4D+) |
| 43 | IHQ250043 | ✅ Auditado | 2025-12-17 | Score: 100%* - v6.3.47 (NeuN="POSITIVO", MPO word-boundary, estudios separados por guión) ESCLEROSIS HIPOCAMPAL (3 biomarcadores: NeuN+/GFAP+/CD68+) |

| 44 | IHQ250044 | ✅ Auditado | 2025-12-17 | Score: 100.0% - CARCINOMA INTRADUCTAL mama (4 biomarcadores: HER2 equívoco/Ki67 20%/RE+ 90%/RP+ 50%) |
| 45 | IHQ250045 | ✅ Auditado | 2025-12-17 | Score: 100.0% - CARCINOMA NEUROENDOCRINO METASTÁSICO ganglio cuello (5 biomarcadores: CK20/CK7/Ki67 80%/P40/TTF1) |
| 46 | IHQ250046 | ✅ Auditado | 2025-12-17 | Score: 100.0% - ADENOCARCINOMA MUCINOSO pulmón (5 biomarcadores: CA19-9/CK19/CK7/NAPSIN/TTF1) |

| 47 | IHQ250047 | ✅ Auditado | 2025-12-17 | Score: 100.0% - v6.3.47 (P16 patrón contexto, P16/P40 mapeo _ESTADO) MUESTRA NEGATIVA PARA DISPLASIA exocérvix (2 biomarcadores: P16-/Ki67 basal) |

| 48 | IHQ250048 | ✅ Auditado | 2025-12-17 | Score: 88.9% - v6.3.48 (CALRRETININA patrón doble R) CÉLULAS GANGLIONARES PRESENTES mucosa rectal (1 biomarcador: CALRRETININA+) |

| 49 | IHQ250049 | ✅ Auditado | 2025-12-17 | Score: 88.9% - v6.3.48 (PAX8 "positivo focal para", VIMENTINA "fue negativa") NEOPLASIA PAPILAR ONCOCÍTICA riñón izquierdo (3 biomarcadores: CK7+/PAX8+ focal/VIMENTINA-) |
| 50 | IHQ250050 | ✅ Auditado | 2025-12-17 | Score: 88.9% - v6.3.49 (LMP1 patrones tinción/inmunorreactividad, fix lookahead estudios_solicitados) CARCINOMA ESCAMOSO NO QUERATINIZANTE nasofaringea (1 biomarcador: LMP1-) Estudios: LMP 1 |

### 📋 Nota sobre Auditorías Anteriores

Los casos IHQ250019-IHQ250050 tuvieron auditorías preliminares en diciembre 2025 con scores entre 66.7% y 88.9%. Esas auditorías están DESACTUALIZADAS porque:
- El archivo completo fue reprocesado el 2025-12-12 con extractores v6.4.1
- Se agregó el biomarcador ACTINA_MUSCULO_LISO
- Los scores antiguos ya no son válidos
- Se requiere nueva auditoría completa para estos 32 casos

---

## 📁 Archivo 2: IHQ DEL 980 AL 1037

**Ubicación:** `pdfs_patologia/IHQ DEL 980 AL 1037.pdf`
**Estado:** ✅ Procesado completo (47 casos)
**Estado Auditoría:** ✅ Auditoría completa (47/47 casos)
**Fecha procesamiento:** 2025-12-02
**Fecha auditoría:** 2025-12-02
**Rango procesado:** IHQ250980 - IHQ251037
**Nota:** El PDF contiene 48 casos detectados, pero se guardaron 47 en la BD (falta IHQ250990)

### ✅ Casos Procesados y Auditados (47/47 casos)

<details>
<summary>Ver casos del rango 980-999 (19 casos auditados, falta IHQ250990)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 1 | IHQ250980 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 2 | IHQ250981 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 3 | IHQ250982 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 4 | IHQ250983 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 5 | IHQ250984 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 6 | IHQ250985 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 7 | IHQ250986 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 8 | IHQ250987 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 9 | IHQ250988 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 10 | IHQ250989 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 11 | IHQ250990 | ❌ NO PROCESADO | ❌ No existe | - |
| 12 | IHQ250991 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 13 | IHQ250992 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 14 | IHQ250993 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 15 | IHQ250994 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 16 | IHQ250995 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 17 | IHQ250996 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 18 | IHQ250997 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 19 | IHQ250998 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 20 | IHQ250999 | ✅ Procesado | ✅ Auditado | 2025-12-02 |

</details>

<details>
<summary>Ver casos del rango 1000-1037 (28 casos auditados de 38 posibles)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 21 | IHQ251000 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 22 | IHQ251001 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 23 | IHQ251002 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 24 | IHQ251003 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 25 | IHQ251004 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 26 | IHQ251005 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 27 | IHQ251006 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 28 | IHQ251007 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 29 | IHQ251008 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 30 | IHQ251009 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 31 | IHQ251010 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 32 | IHQ251011 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 33 | IHQ251012 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 34 | IHQ251013 | ❌ NO PROCESADO | ❌ No existe | - |
| 35 | IHQ251014 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 36 | IHQ251015 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 37 | IHQ251016 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 38 | IHQ251017 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 39 | IHQ251018 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 40 | IHQ251019 | ❌ NO PROCESADO | ❌ No existe | - |
| 41 | IHQ251020 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 42 | IHQ251021 | ❌ NO PROCESADO | ❌ No existe | - |
| 43 | IHQ251022 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 44 | IHQ251023 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 45 | IHQ251024 | ❌ NO PROCESADO | ❌ No existe | - |
| 46 | IHQ251025 | ❌ NO PROCESADO | ❌ No existe | - |
| 47 | IHQ251026 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 48 | IHQ251027 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 49 | IHQ251028 | ❌ NO PROCESADO | ❌ No existe | - |
| 50 | IHQ251029 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 51 | IHQ251030 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 52 | IHQ251031 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 53 | IHQ251032 | ❌ NO PROCESADO | ❌ No existe | - |
| 54 | IHQ251033 | ✅ Procesado | ✅ Auditado | 2025-12-02 |
| 55 | IHQ251034 | ❌ NO PROCESADO | ❌ No existe | - |
| 56 | IHQ251035 | ❌ NO PROCESADO | ❌ No existe | - |
| 57 | IHQ251036 | ❌ NO PROCESADO | ❌ No existe | - |
| 58 | IHQ251037 | ✅ Procesado | ✅ Auditado | 2025-12-02 |

</details>

### ⚠️ Casos NO Procesados (11 casos faltantes)

Los siguientes casos NO fueron procesados (posiblemente no existen en el PDF o tienen errores):

- ❌ IHQ250990
- ❌ IHQ251013
- ❌ IHQ251019
- ❌ IHQ251021
- ❌ IHQ251024
- ❌ IHQ251025
- ❌ IHQ251028
- ❌ IHQ251032
- ❌ IHQ251034
- ❌ IHQ251035
- ❌ IHQ251036

---

## 📁 Archivo 3: IHQ DEL 052 AL 107

**Ubicación:** `pdfs_patologia/IHQ DEL 052 AL 107.pdf`
**Estado:** ✅ Procesado completo (50 casos)
**Estado Auditoría:** ✅ Auditoría completa (50/50 casos)
**Fecha procesamiento:** 2025-12-17
**Rango procesado:** IHQ250052 - IHQ250107

### ✅ Estado de Auditoría (50/50 completados)

<details>
<summary>Ver casos del rango 052-069 (16 casos)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 1 | IHQ250052 | ✅ Procesado | ✅ Auditado | 2025-12-17 | v6.3.50 (CD117 fix, RCC agregado, Diagnóstico Principal patrón colon) CARCINOMA RENAL DE CELULAS CLARAS (4 biomarcadores: RCC+/PAX8+/CD117-/CK7-) |
| 2 | IHQ250053 | ❌ NO PROCESADO | ❌ No existe | - |
| 3 | IHQ250054 | ✅ Procesado | ✅ Auditado | 2025-12-17 | Score: 88.9%* - NEFROPATÍA POR POLIOMAVIRUS riñón trasplantado (4 biomarcadores: C4D/Kappa/Lambda/SV40) *Falso positivo auditor: "GIST" en "Pathologists" |
| 4 | IHQ250055 | ✅ Procesado | ✅ Auditado | 2025-12-17 | Score: 88.9%* - v6.3.51 (patrón M+diagnóstico de, CD4/ALK/BCL2/BCL6 mapping, nombre+/- compacto, NO CONCLUYENTE sobreescribe POSITIVO, ausencia expresión mejorado) HIPERPLASIA SINUSOIDAL ganglios mediastinales (12 biomarcadores: CD3+/CD10+/CD20+/CD23+/BCL2+/BCL6+/CD68+/S100-/ALK-/CD1A-/CD4=NC/Ki67) *Falso positivo: factor pronóstico no aplica en hiperplasia |
| 5 | IHQ250056 | ✅ Procesado | ✅ Auditado | 2025-12-17 | Score: 77.8%* - v6.3.51 (patrón rótulo genérico para DIAGNOSTICO_COLORACION, patrón "marcación de X y Y difusos") LINFOMA FOLICULAR GRADO 1 ganglio cervical (8 biomarcadores: CD3+/CD5+/CD10+/CD20+/CD23+/BCL2+/BCL6+/Ki67) *2 falsos positivos: validador BCL2 y factor pronóstico |
| 6 | IHQ250057 | ✅ Procesado | ✅ Auditado | 2025-12-17 | Score: 100.0% - CARCINOMA METASTÁSICO adenopatía axilar derecha (7 biomarcadores: CDX2-/HER2- score0/Ki67 70%/RE-/RP-/SOX10-/TTF1-) Probable origen mamario |
| 7 | IHQ250058 | ❌ NO PROCESADO | ❌ No existe | - |
| 8 | IHQ250059 | ✅ Procesado | ✅ Auditado | 2025-12-18 | Score: 100.0% - v6.3.52 (Patrón diagnóstico "HALLAZGOS MORFOLÓGICOS E IHQ FAVORECEN", PR alias "PROGRESTÁGENOS") CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL) mama (5 biomarcadores: HER2/Ki67 20%/RE+/RP+/GATA3+) |
| 9 | IHQ250060 | ✅ Procesado | ✅ Auditado | 2025-12-18 | Score: 100.0% - v6.3.52 (Fix REGLA 2: preservar ER/PR normalizados, no sobrescribir con texto descriptivo FP) CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL) mama (5 biomarcadores: HER2 equívoco/Ki67 10%/RE+/RP+/GATA3+) |
| 10 | IHQ250061 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.53+v3.3.6 (CALRRETININA en BIOMARCADORES_TIPIFICACION, IHQ_CALRRETININA en display_names, fix GIST word boundary) ENFERMEDAD DE HIRSCHSPRUNG - Calretinina NEGATIVA (1 biomarcador: CALRRETININA-) |
| 11 | IHQ250062 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.54 (patrón "inmunorreactividad positiva nuclear para X y para Y", patrón 0C3 diagnóstico "IHQ: - DIAGNÓSTICO") CARCINOMA DE CÉLULAS NO PEQUEÑAS pulmón (2 biomarcadores: P40+/TTF1+) |
| 12 | IHQ250063 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - CARCINOMA ESCAMOCELULAR INFILTRANTE región submandibular (2 biomarcadores: P16-/P40+) Sin expresión P16 |
| 13 | IHQ250064 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.55 (patrón "positiva fuerte y difusa", "en bloque para", "FAVORECE [diagnóstico]") CARCINOMA ESCAMOCELULAR INVASIVO cúpula vaginal (2 biomarcadores: P40+/P16+) |
| 14 | IHQ250065 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.56+v3.3.7 (patrón "(BIOMARCADOR+)", Ki-67 "del X%", HIPERPLASIA→BENIGNO, SIN COMPROMISO POR LINFOMA, PAX8 NO MENCIONADO, "marca células"→POSITIVO) HIPERPLASIA FOLICULAR Y PARACORTICAL ganglio cervical (10 biomarcadores: CD3+/CD20+/CD10+/CD5+/BCL2+/BCL6+/Ki-67 70%/CD38+/CD23+/PAX8=NO MENCIONADO) |
| 15 | IHQ250066 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.57+v3.3.9 (Ki-67 "positivo en espesor"→POSITIVO, Diagnóstico Principal patrón DIAGNÓSTICO section, NIC3/CIN3→keywords maligno, DIAGNOSTICO_COLORACION patrón 2C sin punto) LESIÓN ESCAMOSA INTRAEPITELIAL DE ALTO GRADO (NIC 3) CON EXTENSION GLANDULAR exocérvix (2 biomarcadores: Ki-67+/P16+) |
| 16 | IHQ250067 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.58 (P40 "inmunorreactividad...para p40") CARCINOMA EPIDERMOIDE MAL DIFERENCIADO pulmón izquierdo (2 biomarcadores: P16+/P40+) |
| 17 | IHQ250068 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - NEOPLASIA CÉLULAS PLASMÁTICAS restricción Lambda (8 biomarcadores: CD138/CD38/CD45/CD56/CKAE1AE3/Kappa-/Lambda+/SINAPTOFISINA-) |
| 18 | IHQ250069 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - CARCINOMA METASTÁSICO origen genital femenino (12 biomarcadores: CK20-/CK5_6-/CK7+/CKAE1AE3+/GATA3-/P16+/P40-/P63-/PAX8+/RE-/RP-/TTF1-) |

</details>

<details>
<summary>Ver casos del rango 070-089 (19 casos)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 19 | IHQ250070 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA MODERADAMENTE DIFERENCIADO INFILTRANTE (6 biomarcadores: MLH1+/PMS2+/MSH2+/MSH6+/HER2 score 0) MICROSATELITAL ESTABLE |
| 20 | IHQ250071 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.59+v3.3.10 ("Se ordenan los siguientes marcadores:", patrones "no presentan inmunotinción"→NEGATIVO, Ki-67 "es bajo (menos del X%)"→"<X%", auditor fix falso positivo) TUMOR FILODES DE BAJO GRADO mama (3 biomarcadores: P63-/CD117-/Ki-67 <10%) |
| 21 | IHQ250072 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.60 (ADENOMA HIPOFISIARIO→BENIGNO) ADENOMA HIPOFISIARIO PRODUCTOR DE GONADOTROFINAS (3 biomarcadores: CROMOGRANINA+/Ki-67<1%/SINAPTOFISINA+) |
| 22 | IHQ250073 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA METASTÁSICO PROBABLE ORIGEN PULMONAR (6 biomarcadores: CK7+/CK20-/TTF1+/P40-/NAPSINA+) |
| 23 | IHQ250074 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA POBREMENTE DIFERENCIADO células anillo sello (9 biomarcadores: CD45-/CDX2+/CKAE1AE3+/HER2 score 0/panel MMR) |
| 24 | IHQ250075 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 77.8% - PERITONITIS AGUDA Y CRÓNICA células atípicas (2 biomarcadores: CALRRETININA+/CKAE1AE3+) Warnings: desc macroscópica truncada + clasificación MALIGNO |
| 25 | IHQ250076 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA ORIGEN TRACTO GENITAL FEMENINO cérvix (7 biomarcadores: CEA/CK20/Ki-67 70%/P40/RE-/RP-/WT1) |
| 26 | IHQ250077 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA MODERADAMENTE DIFERENCIADO INVASIVO colon izquierdo (5 biomarcadores: HER2 score 1+/MLH1/MSH2/MSH6/PMS2) MICROSATELITAL ESTABLE |
| 27 | IHQ250078 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - LINFOMA DIFUSO DE CÉLULAS B MADURAS región supraclavicular (14 biomarcadores: BCL2/BCL6/CD10/CD20/CD23/CD3/CD30/CD45/CD5/CKAE1AE3/Ki-67 90%/MUM1/PAX5/SOX10) |
| 28 | IHQ250079 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - CAMBIOS PIGMENTARIOS POST INFLAMATORIOS piel muslo izquierdo (6 biomarcadores: CD3/CD4/CD5/CD8/CD20/CD30) Negativo para neoplasia |
| 29 | IHQ250080 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - CARCINOMA CÉLULAS EN ANILLO SELLO INVASIÓN MUSCULAR PROPIA colon derecho (5 biomarcadores: HER2 score 0/MLH1/MSH2/MSH6/PMS2) |
| 30 | IHQ250081 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - LINFOMA DIFUSO DE CÉLULAS B GRANDES CENTRO GERMINAL mucosa gástrica antral (11 biomarcadores: BCL2/BCL6/CD10/CD20/CD23/CD3/CD30/CD5/CKAE1AE3/Ki-67 90%/MUM1) |
| 31 | IHQ250082 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.61+v6.3.62 (HCG agregado, GIST word boundary fix) ADENOMA HIPOFISIARIO PRODUCTOR DE GONADOTROPINAS hipófisis (5 biomarcadores: CROMOGRANINA+/SINAPTOFISINA+/HCG+/Ki-67 2%/CAM5.2-) Malignidad: BENIGNO |
| 32 | IHQ250083 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.63+v6.3.64 (diagnóstico sin comillas, marcación difusa, positividad focal, negativo para) ADENOCARCINOMA METASTÁSICO DE PROBABLE ORIGEN PULMONAR cerebro (5 biomarcadores: TTF1+/NAPSIN+/CK7+ focal/CK20-/GATA3-) |
| 33 | IHQ250084 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - SCHWANNOMA ángulo pontocerebeloso cráneo (3 biomarcadores: Ki-67 1%/S100/SOX10) |
| 34 | IHQ250085 | ❌ NO PROCESADO | ❌ No existe | - |
| 35 | IHQ250086 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA INVASIVO mucosa colónica (5 biomarcadores: HER2 score 0/MLH1/MSH2/MSH6/PMS2) |
| 36 | IHQ250087 | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.65 (DESMIN agregado, limpieza modificadores "en bloque") MELANOMA INVASIVO canal anal (9 biomarcadores: SOX10+/CKAE1E3-/CD34-/DESMIN-/P40-/S100+/HMB45+/MELAN_A+/P16+) |
| 37 | IHQ250088 | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.66 (receptores hormonales de X, P53 mutado) CARCINOMA METASTÁSICO DE PROBABLE ORIGEN GINECOLÓGICO peritoneo parietal (9 biomarcadores: CK7+/GATA3-/CK20-/RE-/RP-/WT1-/P16+/P53 mutado/PAX8+) |
| 38 | IHQ250089 | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.67 (BCL6+, CMYC/MYC+ patrones) LINFOMA DE CÉLULAS B GRANDES DE ALTO GRADO ganglio cervical izquierdo (10 biomarcadores: BCL2+/BCL6+/CD10+/CD20+/CD30-/CD5+/CMYC+/Ki-67 90%/MUM1+/PAX5+) |

</details>

<details>
<summary>Ver casos del rango 090-107 (15 casos)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 39 | IHQ250090 | ❌ NO PROCESADO | ❌ No existe | - |
| 40 | IHQ250091 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.72+v6.3.73 (patrones narrativos SIEMPRE ejecutar, excluir células acompañantes) LINFOMA DE CÉLULAS B GRANDES DIFUSO NO CENTRO GERMINAL ganglio cervical (12 biomarcadores: CD3-/CD5-/CD10-/CD20+/CD30-/MUM1+/LMP1-/BCL2+/BCL6+/Ki-67 80%/CMYC-/CD79A+) |
| 41 | IHQ250092 | ❌ NO PROCESADO | ❌ No existe | - |
| 42 | IHQ250093 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.74 (patrón "No hay inmunorreactividad para X ni Y") CAMBIOS REPARATIVOS órbita izquierda (2 biomarcadores: IGG4-/CD38-) BENIGNO |
| 43 | IHQ250094 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - v6.3.75+v6.3.76 (CD1a preservado en corrector, word-boundaries para NIC, INFLAMACIÓN CRÓNICA GRANULOMATOSA→BENIGNO) INFLAMACIÓN CRÓNICA GRANULOMATOSA hígado (2 biomarcadores: CD1A-/S100-) BENIGNO |
| 44 | IHQ250095 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 88.9%* - v6.3.77 (LINFOMA agregado a keywords malignidad) LINFOMA DIFUSO DE CÉLULAS B GRANDES CENTROGERMINAL retroperitoneo (13 biomarcadores: CD20+/PAX5+/MUM1+/BCL6+/BCL2+/CD5-/CD3-/CD10+/CD23-/CD30-/CMYC-/Ki67 80%/CD38+) MALIGNO *Bug auditor: Ki-67 OCR="d" |
| 45 | IHQ250096 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.70 (5 patrones linfoma/hematopatología + CD7 agregado) LINFOMA LINFOBLÁSTICO DE CÉLULAS T mediastino (17 biomarcadores: TDT+/CD1A+/CD3+/CD5+/CD7+/CD4+/CD8+/CD10-/CD20-/CD34-/CD56-/CD68+/CD79A-/CD99+/CD117-/Ki67 90%/BCL2+) MALIGNO |
| 46 | IHQ250097 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.71 (hormonas hipofisarias: ACTH/GH/FSH/LH/TSH/PROLACTINA) ADENOMA HIPOFISIARIO PRODUCTOR DE PROLACTINA hipófisis (12 biomarcadores: CAM5.2+/SINAPTOFISINA+/PROLACTINA+/CROMOGRANINA-/ACTH-/GH-/FSH-/LH-/TSH-/P53-/Ki67 1%) BENIGNO |
| 47 | IHQ250098 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.72 (receptor estrógenos con tilde) CARCINOMA PAPILAR mama derecha (4 biomarcadores: RE+/P63-/CK5_6-) MALIGNO |
| 48 | IHQ250099 | ✅ Procesado | ✅ Auditado | 2025-12-19 | Score: 100.0% - ADENOCARCINOMA DIFUSO POBREMENTE COHESIVO estómago (2 biomarcadores: HER2-/Ki67) MALIGNO |
| 49 | IHQ250100 | ✅ Procesado | ⚠️ Auditado | 2025-12-19 | Score: 77.8% - BIOPSIA INJERTO RENAL trasplante (SV40/C4d) BENIGNO - Requiere mejora extractor diagnóstico trasplante |
| 50 | IHQ250101 | ❌ NO PROCESADO | ❌ No existe | - |
| 51 | IHQ250102 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.74 (ER/PR con intensidad+porcentaje) CARCINOMA DUCTAL INFILTRANTE mama (4 biomarcadores: RE+/RP+/HER2/Ki67) |
| 52 | IHQ250103 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.75 (IHQ_ORGANO limpieza contaminación) CARCINOMA METASTÁSICO ganglio axilar (biomarcadores: GATA3/WT1/PAX8/TTF1/CDX2) |
| 53 | IHQ250104 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - (SV40/C4D "NO MENCIONADO") BIOPSIA INJERTO RENAL trasplante (2 biomarcadores: SV40-/C4D-) BENIGNO |
| 54 | IHQ250105 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.77 (PASE FINAL CD20/CD23/CD34 fix NEGATIVO) LEUCEMIA/LINFOMA LINFOBLÁSTICO DE CÉLULAS B piel antebrazo (12 biomarcadores: CD20-/CD79A+/PAX5+/BCL2+/TDT+/CD10+/CD34-/CD23-/CD99+/CD3+/CD5+/Ki67 90%) MALIGNO |
| 55 | IHQ250106 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.78 (GATA3 separador "ni", keywords benignos SIN EVIDENCIA NEOPLASIA) INFLAMACIÓN AGUDA SIN EVIDENCIA DE LESIÓN NEOPLÁSICA piel axilar (2 biomarcadores: CKAE1AE3-/GATA3-) BENIGNO |
| 56 | IHQ250107 | ✅ Procesado | ✅ Auditado | 2025-12-20 | Score: 100.0% - v6.3.79 (Panel NO VALORABLE completo) CARCINOMA METASTASICO fosa ilíaca (10 biomarcadores: CKAE1AE3/CK7/CK20/CD45/SOX10/DESMIN/CD34/SINAPTOFISINA/CROMOGRANINA/Ki67 - todos NO VALORABLE) MALIGNO |

</details>

### ⚠️ Casos NO Procesados (6 casos faltantes)

Los siguientes casos NO fueron procesados (posiblemente no existen en el PDF o tienen errores):

- ❌ IHQ250053
- ❌ IHQ250058
- ❌ IHQ250085
- ❌ IHQ250090
- ❌ IHQ250092
- ❌ IHQ250101

---

## 📈 Próximos Pasos

### ✅ Completado
1. ✅ Auditoría de casos 001-050 del primer archivo (50 casos)
2. ✅ Procesamiento completo del archivo 980-1037 (47 casos)
3. ✅ Auditoría completa del archivo 980-1037 (47 casos)
4. ✅ Correcciones en extractores (v6.2.8, v6.3.7, v6.3.9, v6.3.11, auditor v3.3.1, v3.3.2)
5. ✅ Procesamiento completo del archivo 052-107 (50 casos) - 2025-12-17
6. ✅ Auditoría completa del archivo 052-107 (50 casos) - 2025-12-20 (v6.3.50 a v6.3.79)
7. ✅ Procesamiento completo del archivo 108-159 (48 casos) - 2025-12-23
8. ✅ Auditoría completa del archivo 108-159 (48 casos) - 2026-01-07 (v6.3.80 a v6.4.13)
9. ✅ Procesamiento completo del archivo 160-211 (50 casos) - 2026-01-07
10. ✅ Auditoría completa del archivo 160-211 (50 casos) - 2026-01-12 (v6.4.74 a v6.4.79)

### 🔄 En Progreso
1. ⚠️ Resolver casos incompletos con biomarcadores NO mapeados (IGD, DIFUSA)

### 📋 Pendientes
1. **Agregar biomarcadores faltantes:**
   - IGD (Inmunoglobulina D) - IHQ250164
   - Revisar "DIFUSA" (descriptor, no biomarcador) - IHQ250198
2. **Procesar siguiente archivo:** IHQ DEL 212 AL 262 (51 casos aproximadamente)
3. Procesar archivos intermedios restantes (212-979)
4. **Investigar casos no procesados (13 casos totales):**
   - 1 caso del archivo 980-1037: IHQ250990
   - 6 casos del archivo 052-107: IHQ250053, IHQ250058, IHQ250085, IHQ250090, IHQ250092, IHQ250101
   - 4 casos del archivo 108-159: IHQ250122, IHQ250130, IHQ250137, IHQ250145
   - 2 casos del archivo 160-211: IHQ250161, IHQ250196

### Archivos Intermedios Pendientes de Procesamiento
Los siguientes archivos NO han sido procesados aún:
- IHQ DEL 212 AL 260 (aproximadamente)
- IHQ DEL 261 AL 310
- ... (continuar secuencialmente)
- IHQ DEL 930 AL 979 (aproximadamente)

---

## 📁 Archivo 4: IHQ DEL 108 AL 159

**Ubicación:** `pdfs_patologia/IHQ DEL 108 AL 159.pdf`
**Estado:** ✅ Procesado completo (48 casos)
**Estado Auditoría:** ✅ Auditoría completa (48/48 casos)
**Fecha procesamiento:** 2025-12-23
**Fecha auditoría:** 2025-12-24 a 2026-01-07
**Rango procesado:** IHQ250108 - IHQ250159

### ✅ Estado de Auditoría (48/48 completados)

<details>
<summary>Ver casos del rango 108-159 (48 casos)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Fecha Auditoría |
|---|----------------|---------------------|------------------|-----------------|
| 1 | IHQ250108 | ✅ Procesado | ✅ Auditado | 2025-12-24 | Score: 100.0% - v6.3.80 (CK34BE12 agregado, fix extractor beta-catenin/basales) FOCOS MICROACINARES ATÍPICOS prostata (3 biomarcadores: P63+/CK34BE12+/RACEMASA-) |
| 2 | IHQ250109 | ✅ Procesado | ✅ Auditado | 2025-12-24 | Score: 100.0% - v6.3.81 (Fix P53, IDH, GFAP extraction) - p53:NEGATIVO(WT), IDH:NEGATIVO(WT), GFAP:POSITIVO |
| 3 | IHQ250110 | ✅ Procesado | ✅ Auditado | 2025-12-24 | Score: 100.0% - v6.3.83 (Fix CKAE1E3). ADENOCARCINOMA METASTASICO PROSTÁTICO. |
| 4 | IHQ250111 | ✅ Procesado | ✅ Auditado | 2025-12-24 | Score: 100.0% - v6.3.84 (Fix narrative: Calponina, P63, CK5/6). LESIÓN FIBROEPITELIAL. |
| 5 | IHQ250112 | ✅ Procesado | ✅ Auditado | 2026-01-02 | Score: 100.0% - v6.3.85 (Fix P16/Ki67 extraction). CARCINOMA ESCAMOCELULAR INVASIVO. |
| 6 | IHQ250113 | ✅ Procesado | ✅ Auditado | 2026-01-02 | Score: 100.0% - v6.3.86 (Fix RE mosaico/Calponina/CD34). HIPERPLASIA PSEUDOANGIOMATOSA. |
| 7 | IHQ250114 | ✅ Procesado | ✅ Auditado | 2026-01-02 | Score: 100.0% - v6.3.87 (Fix MMR panel/P53). CARCINOMA ENDOMETRIOIDE. |
| 8 | IHQ250115 | ✅ Procesado | ✅ Auditado | 2026-01-02 | Score: 100.0% - v6.3.88 (Fix CD10/Ciclina/SOX11). LEUCEMIA LINFOCÍTICA CRÓNICA. |
| 9 | IHQ250116 | ✅ Procesado | ✅ Auditado | 2026-01-02 | Score: 100.0% - v6.3.90 (Fix malignancy/HER2 score/ER/PR description/Narrative lists: P63, CK5/6, S100, Calponina, Cromogranina, Sinaptofisina). LESIÓN PAPILAR ATÍPICA. |
| 10 | IHQ250117 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.3.96 (Fix dash-prefix ER/PR/HER2 & greedy capture). ADENOCARCINOMA PROSTÁTICO. |
| 11 | IHQ250118 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.3.97 (Fix SV40/C4D "ambos negativos", fixed diagnostic truncation at hyphens). NEFRITIS TÚBULO-INTERSTICIAL. |
| 12 | IHQ250119 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.4.2 (GATA3 persistence, fix PR split/SCORE truncation). CARCINOMA INVASIVO MAMA. |
| 13 | IHQ250120 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.4.3 (Fix negative lists & MATR-1/MART-1 alias). MELANONIQUIA ESTRIADA. |
| 14 | IHQ250121 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.4.4 (Fix CDX2 heterogénea & CA19.9 missing). GASTROPANCREATOBILIAR. |
| 15 | IHQ250122 | ❌ NO PROCESADO | ❌ No existe | - |
| 16 | IHQ250123 | ✅ Procesado | ✅ Auditado | 2026-01-03 | Score: 100.0% - v6.4.5 (Fix muscle markers: Myogenin/Actin/MyoD1 mapping, support masculine "negativos", preserve "ALTO GRADO" in diag). LEIOMIOSARCOMA. |
| 17 | IHQ250124 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - TTF-1 correctamente extraído. Adenocarcinoma Pulmonar. |
| 18 | IHQ250125 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5: CD20/CD79A extraídos (regex fixe), CD138 colisión con CD38 fix. |
| 19 | IHQ250126 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - p16 (NEGATIVO) y Ki-67 correctamente extraídos. MALIGNO (HSIL). |
| 20 | IHQ250127 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.3 (Fix CD34/CD117 negation, CD56 parenthetical, studies fallback). |
| 21 | IHQ250128 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.4 (Fix end-of-macro studies list, clean organ ID/date prefix, normalize RE/RP). MAMA DERECHA. |
| 22 | IHQ250129 | ✅ Auditado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5 (MMR nuclear intacto, HER2 score 0, malignidad MALIGNO corregida para Grado I). |
| 23 | IHQ250130 | ❌ NO PROCESADO | ❌ No existe | - |
| 24 | IHQ250131 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5: Corregido ruido en biomarcadores narrativos, flip de Sinaptofisina y clasificación de malignidad para NET G1. |
| 25 | IHQ250132 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5: Corregida extracción fantasma de P63 y duplicación de PAX8 en estudios solicitados. |
| 26 | IHQ250133 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5 (Fix HER2 extraction mapping & regex, resolve batch-processing UnboundLocalError). |
| 27 | IHQ250134 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5: Biomarcadores (CK7, RP, RE, PAX8, P16, P53) correctamente extraídos de narrativa. Diagnóstico Principal y Organo correctos. |
| 28 | IHQ250135 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.5: Biomarcadores (RE, RP, P53, HER2, MMR x 4) correctamente extraídos. Patólogo y Diagnóstico Principal correctos. |
| 29 | IHQ250136 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 100.0% - v6.4.8: Extracción de CK7, GATA3, HER2 y Mamoglobina (focal). ER/PR capturados con intensidad (+) tras corrección de secciones y patrones. |
| 30 | IHQ250137 | ❌ NO PROCESADO | ❌ No existe | - |
| 31 | IHQ250138 | ✅ Procesado | ✅ Auditado | 2026-01-05 | Score: 88.9% - v6.4.0 (Malignidad: NO_DETERMINADO→BENIGNO, MPO/MPX→MIELOPEROXIDASA, campos compuestos CD117 GLICOFORINA, completitud 100%) CELULARIDAD MEDULA ÓSEA 30-70% |
| 32 | IHQ250139 | ✅ Procesado | ✅ Auditado | 2026-01-05 |
| 33 | IHQ250140 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - v6.4.0+ (Biomarcadores musculares: ACTINA_MUSCULO_ESPECIFICA/CALDESMON/MIOGENINA sin mapear) LEIOMIOSARCOMA brazo derecho |
| 34 | IHQ250141 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - v6.4.9 (CD138/CD56 espaciados, CD177→CD117 OCR, CICLINA sin D1, LAMBDA implícito, "de forma" lista) NEOPLASIA DE CELULAS PLASMATICAS CON RESTRICCIÓN KAPPA médula ósea (10 biomarcadores: CD117/CD138/CD20/CD3/CD38/CD56/CICLINA_D1/Kappa/Lambda/MIELOPEROXIDASA) MALIGNO |
| 35 | IHQ250142 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - ADENOCARCINOMA DE ORIGEN PULMONAR lóbulo superior izquierdo (1 biomarcador: P40) MALIGNO |
| 36 | IHQ250143 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - FASCITIS NODULAR piel pie derecho (10 biomarcadores: ACTINA/CD34/CD45/CKAE1AE3/HHV8/HMB45/Ki-67/RE/S100/SOX10) BENIGNO |
| 37 | IHQ250144 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - v6.4.10 + v3.3.11 (Ki-67 patrón "entre X y Y%", P53 aberrante, IDH 1 alias, GLIOMA keyword) GLIOMA DE ALTO GRADO IDH MUTANTE cerebro región frontal izquierda (4 biomarcadores: P53/GFAP/IDH1/Ki-67) MALIGNO |
| 38 | IHQ250145 | ❌ NO PROCESADO | ❌ No existe | - |
| 39 | IHQ250146 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - CARCINOMA ESCAMOCELULAR INVASIVO ASOCIADO A VPH región preauricular izquierda (4 biomarcadores: CKAE1AE3/P40/P16/Ki-67) MALIGNO |
| 40 | IHQ250147 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - ADENOCARCINOMA BIEN DIFERENCIADO INFILTRANTE mucosa rectal patrón microsatelital estable (5 biomarcadores: HER2/MLH1/MSH2/MSH6/PMS2) MALIGNO |
| 41 | IHQ250148 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - v6.4.11 (Casos externos: patrón "correspondientes a... y con diagnóstico de") NEGATIVO PARA NEOPLASIA próstata (3 biomarcadores: CK34BE12/P63/RACEMASA) BENIGNO |
| 42 | IHQ250149 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - v6.4.12 (Patrón "marcación negativo para" masculino) SARCOMA DE BAJO GRADO muslo izquierdo (9 biomarcadores: DESMINA/CD34/MDM2/CDK4/MYOD1/SMA/S100/CKAE1AE3/H_CALDESMON) MALIGNO |
| 43 | IHQ250150 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - ADENOCARCINOMA METASTÁSICO DE PROBABLE ORIGEN GASTROPANCREATOBILIAR (14 biomarcadores: CK7/CK20/CK19/PAX8/WT1/CDX2/P16/GATA3/RE/RP/TTF-1/NAPSIN/CEA/CA19-9) MALIGNO |
| 44 | IHQ250151 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - ADENOCARCINOMA METASTÁSICO DE PROBABLE ORIGEN GASTROPANCREATOBILIAR (8 biomarcadores: ARGINASA/CA19-9/CALRETININA/CDX2/CK19/CK20/CK7/CKAE1AE3) MALIGNO |
| 45 | IHQ250152 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - ADENOCARCINOMA TIPO DIFUSO CON CÉLULAS EN ANILLO DE SELLO (1 biomarcador: HER2) MALIGNO |
| 46 | IHQ250153 | ✅ Procesado | ✅ Auditado | 2026-01-07 | Score: 88.9% - v6.4.13 CELULARIDAD GLOBAL DEL 10%, APLASIA médula ósea HIPOCELULAR (6 biomarcadores: MIELOPEROXIDASA/CD34/CD20/CD117/CD3/GLICOFORINA = NO VALORABLE) BENIGNO - Muestra hipocelular, patólogo no reportó valores individuales |
| 47 | IHQ250154 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - CARCINOMA INVASIVO EN PATRÓN PAPILAR Y SÓLIDO cérvix (12 biomarcadores: GATA3/RP/DESMINA/MIOGENINA/P16/P53/Ki-67/P40/CK7/CK20/CKAE1E2/WT1 + extras: RE/CKAE1AE3/PAX8/DESMIN) MALIGNO |
| 48 | IHQ250155 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - CARCINOMA DE CÉLULAS ESCAMOSAS P16 POSITIVO glándula salival (7 biomarcadores: CKAE1AE3/P40/P16/CK5_6/SOX10/S100/SYNAPTOFISINA) MALIGNO |
| 49 | IHQ250156 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - CARCINOMA METASTÁSICO pulmón (14 biomarcadores: TTF-1/NAPSIN/P40/CKAE1E3/CK7/CK20/CK19/CA19-9/CDX2/SYNAPTOFISINA/GATA3/PAX8/PSA/HEPATOCITO) MALIGNO - NAPSIN corrupto + 4 discrepancias |
| 50 | IHQ250157 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - LEUCEMIA/LINFOMA DE PRECURSORES LINFOIDES B médula ósea (7 biomarcadores: CD20/CD79A/CD38/CD10/CD34/CD117/TDT) MALIGNO |
| 51 | IHQ250158 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 100.0% - CARCINOMA UROTELIAL POBREMENTE DIFERENCIADO ULCERADO vejiga y próstata (9 biomarcadores: CK34BE12/CKAE1AE3/DESMIN/GATA3/Ki-67/P63/PAX8/RACEMASA/VIMENTINA) MALIGNO - Factor pronóstico: Ki-67 90% |
| 52 | IHQ250159 | ✅ Procesado | ✅ Auditado | 2026-01-06 | Score: 88.9% - ADENOCARCINOMA CON COMPONENTE MUCINOSO mucosa rectal (Panel MMR: MLH1/MSH2/MSH6/PMS2) MALIGNO - WARNING: Diagnóstico principal resumido |

</details>

### ⚠️ Casos NO Procesados (4 casos faltantes)

- ❌ IHQ250122
- ❌ IHQ250130
- ❌ IHQ250137
- ❌ IHQ250145

---

## 📁 Archivo 5: IHQ DEL 160 AL 211

**Ubicación:** `pdfs_patologia/IHQ DEL 160 AL 211.pdf`
**Estado:** ✅ Procesado completo (50 casos)
**Estado Auditoría:** ✅ Completada (50/50 casos auditados - 100%)
**Fecha procesamiento:** 2026-01-07
**Fecha inicio auditoría:** 2026-01-07
**Fecha finalización auditoría:** 2026-01-12
**Rango procesado:** IHQ250160 - IHQ250211

### 📊 Resumen de Completitud (Módulo de Importación)

| Métrica | Valor |
|---------|-------|
| **Total procesados** | 50 casos |
| **Casos completos** | 41 (82.0%) |
| **Casos incompletos** | 9 (18.0%) |
| **Total correcciones aplicadas** | 105 |

### ⚠️ Casos Incompletos por Biomarcadores NO Mapeados (9 casos)

Los siguientes casos tienen biomarcadores que NO están mapeados en el sistema:

<details>
<summary>Ver lista de casos incompletos (9 casos)</summary>

| # | Número de Caso | Completitud | Biomarcador NO Mapeado | Observaciones |
|---|----------------|-------------|------------------------|---------------|
| 1 | IHQ250160 | 100% ✅ | ~~GLYCOFORINA~~ | **RESUELTO v6.4.22** - Alias agregado al sistema |
| 2 | IHQ250162 | 88.9% ✅ | ~~N/A~~ | **RESUELTO v3.4.3** - Auditor mejorado (búsqueda debug_map + validación descripción) |
| 3 | IHQ250164 | 98.1% | **IGD** | Inmunoglobulina D, requiere agregar al sistema |
| 4 | IHQ250169 | 97.9% | (Pendiente verificar) | Requiere revisión de reporte |
| 5 | IHQ250170 | 91.4% | (Pendiente verificar) | Requiere revisión de reporte |
| 6 | ~~IHQ250185~~ | ~~96.2%~~ | ~~(Pendiente verificar)~~ | **RESUELTO v6.4.47/48** - P53 SOBRE EXPRESADO, RECEPTOR_ESTROGENOS, PAX8 extraídos correctamente (100%) |
| 7 | IHQ250189 | 94.0% | (Pendiente verificar) | Requiere revisión de reporte |
| 8 | IHQ250195 | 93.3% | (Pendiente verificar) | Requiere revisión de reporte |
| 9 | IHQ250198 | 98.0% | **DIFUSA** | No es biomarcador, es descriptor de patrón |

</details>

### ✅ Casos Auditados (23/49)

**IHQ250160** - Auditado 2026-01-07
- **Score inicial:** 88.9% (GLYCOFORINA no mapeado)
- **Corrección aplicada:** v6.4.22 - Agregado alias GLYCOFORINA → GLICOFORINA
- **Score final:** 100%* (completitud alcanzada)
- **Archivos modificados:**
  - validation_checker.py v1.0.7
  - auditor_sistema.py v3.4.2
  - biomarker_extractor.py v6.4.22

### ✅ Auditoría Completada (50/50 casos - 100%)

**Estado:** ✅ Todos los casos procesados han sido auditados

<details>
<summary>Ver casos del rango 160-211 (50 casos procesados, 50 auditados)</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Completitud |
|---|----------------|---------------------|------------------|-------------|
| 1 | IHQ250160 | ✅ Procesado | ✅ Auditado | 88.9% → 100%* (v6.4.22) |
| 2 | IHQ250161 | ❌ NO PROCESADO | ❌ No existe | - |
| 3 | IHQ250162 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v3.4.3) |
| 4 | IHQ250163 | ✅ Procesado | ✅ Auditado | 100% ✅ (v3.4.3) |
| 5 | IHQ250164 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.4.31) |
| 6 | IHQ250165 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (falso positivo validador) |
| 7 | IHQ250166 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 8 | IHQ250167 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.32) |
| 9 | IHQ250168 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 10 | IHQ250169 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (alias CKEA1EA3 agregado) |
| 11 | IHQ250170 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.4.34: EMA, PROGESTERONA, CK, S100 corregidos) |
| 12 | IHQ250171 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 13 | IHQ250172 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.35: patrones narrativos P63, CALPONINA, CK5_6; auditor v3.4.4) |
| 14 | IHQ250173 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 15 | IHQ250174 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.36-38: PAX8, P16, WT1 "tinción positiva"; PR capture fix; caracteres acentuados) |
| 16 | IHQ250175 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.4.39-41: P53 "tinción nuclear"; IDH campos_criticos; IDH NEGATIVO "No se identifica marcación") |
| 17 | IHQ250176 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (Datos correctos, falsos positivos auditor. Agregado alias CYCLINA) |
| 18 | IHQ250177 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 19 | IHQ250178 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.4.42: MALIGNIDAD corregida en casos múltiples muestras - BENIGNO→MALIGNO) |
| 20 | IHQ250179 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.43-44: MUC1 agregado al sistema; Ki-67 cualitativo "distribución uniforme") |
| 21 | IHQ250180 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (P40 dato correcto, falso positivo auditor) |
| 22 | IHQ250181 | ✅ Procesado | ✅ Auditado | 88.9% → 100%* ✅ (P40 correcto, falso positivo auditor captura "f" de "fuerte") |
| 23 | IHQ250182 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.45: DIAGNOSTICO_COLORACION patrón "diagnósticos de") |
| 24 | IHQ250183 | ✅ Procesado | ✅ Auditado | 100% ✅ |
| 25 | IHQ250184 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.46: CA19_9/TTF1 NEGATIVO, HER2 score 1+ preservado) |
| 26 | IHQ250185 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.47/48: Lista con dos puntos, P53 SOBRE EXPRESADO, RECEPTOR_ESTROGENOS, PAX8 extraídos correctamente) |
| 27 | IHQ250186 | ✅ Procesado | ✅ Auditado | 88.9% → 100%* ✅ (v6.4.48: CD3/CD5 "linfocitos T acompañantes" extraídos correctamente. Score 88.9% por falso positivo auditor en Ki-67) |
| 28 | IHQ250187 | ✅ Procesado | ✅ Auditado | 88.9% → 100%* ✅ (GLIOBLASTOMA WHO 4, 4 biomarcadores correctos. Score 88.9% por falso positivo validador MALIGNIDAD) |
| 29 | IHQ250188 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.51: Lookahead negativo patrón "con [lista] positivo", v3.2.0: PASO 3 campos_criticos narrativos. GPC3/HEPAR/ARGINASA/AFP extraídos correctamente) |
| 30 | IHQ250189 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (Alias "GLYPICAN 3" agregado a GPC3. Hepatocarcinoma, 5 biomarcadores correctos) |
| 31 | IHQ250190 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.59: Eliminadas columnas duplicadas IHQ_CKAE1E3/IHQ_SYNAPTOFISINA. MYOD1/DESMIN/MYOGENIN = POSITIVO fuerte. RABDOMIOSARCOMA NOS, 16 biomarcadores correctos) |
| 32 | IHQ250191 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA METASTASICO tracto genital femenino, 10 biomarcadores correctos) |
| 33 | IHQ250192 | ✅ Procesado | ✅ Auditado | 100% ✅ (XANTOMA GASTRICO benigno, 3 biomarcadores correctos) |
| 34 | IHQ250193 | ✅ Procesado | ✅ Auditado | 100% ✅ (NEOPLASIA CELULAS PLASMATICAS restricción lambda, 9 biomarcadores correctos - v6.4.60) |
| 35 | IHQ250194 | ✅ Procesado | ✅ Auditado | 100% ✅ (SINDROME MIELODISPLASICO médula ósea, 9 biomarcadores correctos - v6.4.60 eliminó duplicación IHQ_MPO) |
| 36 | IHQ250195 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (SCHWANNOMA fosa posterior, 10 biomarcadores correctos - v6.4.60: CD34 "resalta vasculatura"→NEGATIVO, KI65→KI-67, INHIBINA agregada - extractores OK, score bajo por limitación auditor) |
| 37 | IHQ250196 | ❌ NO PROCESADO | ❌ No existe | - |
| 38 | IHQ250197 | ✅ Procesado | ✅ Auditado | 100% ✅ (ASTROCITOMA IDH MUTADO WHO IV SNC, 5 biomarcadores correctos - v6.4.60: IDH/GFAP/KI-67 agregados, FIX malignidad WHO IV→MALIGNO) |
| 39 | IHQ250198 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (LINFOMA CELULAS T PERIFERICAS mediastino, 15 biomarcadores correctos - v6.4.60: BCL6/CD2/CD56/KI-67 corregidos) |
| 40 | IHQ250199 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA TIPO INTESTINAL gástrico, 5 biomarcadores correctos: MMR panel + HER2) |
| 41 | IHQ250200 | ✅ Procesado | ✅ Auditado | 100% ✅ (PAPILOMA ESCAMOSO lengua, 3 biomarcadores correctos - v6.4.60: P40 "marcación celular... con p40"→POSITIVO + Ki-67 "esperable") |
| 42 | IHQ250201 | ✅ Procesado | ✅ Auditado | 100% ✅ (SEMINOMA METASTASICO región intraabdominal, 7 biomarcadores correctos: CD117/CD30/CKAE1AE3/Ki-67/MELAN-A/SALL4/SOX10) |
| 43 | IHQ250202 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (ADENOCARCINOMA METASTASICO mucinoso pared torácica, 2 biomarcadores correctos: TTF-1/NAPSIN NEGATIVO - v6.4.62: patrón "Los marcadores X - son negativos" corregido, score bajo por falso negativo auditor) |
| 44 | IHQ250203 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (CARCINOMA ESCAMOCELULAR INVASIVO endocérvix, 2 biomarcadores correctos: P16/P63 - warning en DIAGNOSTICO_COLORACION por formato) |
| 45 | IHQ250204 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO mucosa gástrica, HER2: NEGATIVO (SCORE 0) - v6.4.68: Fix patrón HER2 para preservar score con espacios en diagnóstico, warning DIAGNOSTICO_COLORACION) |
| 46 | IHQ250205 | ✅ Procesado | ✅ Auditado | 77.8% ✅ (LINFOMA DIFUSO CELULAS B GRANDES ganglio inguinal, 16 biomarcadores correctos - v6.4.72: CD7 definición agregada, CD4/CD7 excluidos de microambiente, "NO MENCIONADO" solo para biomarcadores solicitados, error FACTOR_PRONOSTICO) |
| 47 | IHQ250206 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA PATRON ACINAR Y MICROPAPILAR pulmón derecho, TTF1: POSITIVO, P40: NEGATIVO - v6.4.73: Fix patrón auditoría "sin marcación para {bio}" = NEGATIVO, evita falso positivo en validación) |
| 48 | IHQ250207 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA METASTASICO PROBABLE ORIGEN RENAL región parietal derecho, 10 biomarcadores: CKAE1AE3/PAX8 POSITIVO; CK7/CK20/GFAP/GATA3/TTF1/P53/IDH1 NEGATIVO; Ki-67 60% - v6.4.74: Patrón "siendo negativas para la expresión de [lista]" captura CK20/TTF1/GATA3) |
| 49 | IHQ250208 | ✅ Procesado | ✅ Auditado | 100% ✅ (HIPERPLASIA FOLICULAR SIN REPRESENTACION NEOPLASIA canal anal, 5 biomarcadores: CD20/BCL6/CD3/BCL2 POSITIVO marcación esperada, Ki-67 20% - v6.4.75: Fix PatternError lookbehind permite procesar; v6.4.76: Patrón "marcación esperada [lista] acompañantes"→POSITIVO; v6.4.77: Alias 'BLC2'→'BCL2'; v6.4.78: Patrón "índice proliferativo" sin "Ki-67" explícito) |
| 50 | IHQ250209 | ✅ Procesado | ✅ Auditado | 100% ✅ (TEJIDO FIBROTICO SIN COMPROMISO LINFOMA omento, 4 biomarcadores: CD3/CD10/CD20/BCL2) |
| 51 | IHQ250210 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOSIS SIMPLE Y FIBROSIS mama derecha, 4 biomarcadores: P63/CK5-6/Calponina/RE POSITIVO mosaico - v6.4.79: Patrón extendido "marcación para células con [lista] positivo" captura P63 correctamente) |
| 52 | IHQ250211 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (CARCINOMA INVASIVO TIPO NO ESPECIAL mama izquierda, 4 biomarcadores: HER2 NEGATIVO (0), RE/RP/Ki-67 correctos - Ki-67: 40% en BD correcto, auditor re-extrae "a" por patrón) |

</details>

### ⚠️ Casos NO Procesados (2 casos faltantes)

Los siguientes casos NO fueron procesados (posiblemente no existen en el PDF o tienen errores):

**IHQ250208:** ✅ RESUELTO - v6.4.75 Fix PatternError permitió procesarlo correctamente

- ❌ IHQ250161
- ❌ IHQ250196

### 🔧 Biomarcadores Detectados que Requieren Atención

1. ~~**GLYCOFORINA** (IHQ250160)~~ - ✅ **RESUELTO v6.4.22** - Alias agregado (validation_checker.py v1.0.7, auditor_sistema.py v3.4.2, biomarker_extractor.py v6.4.22)
2. **IGD** (IHQ250164) - Inmunoglobulina D, biomarcador válido, agregar al sistema
3. **DIFUSA** (IHQ250198) - NO es biomarcador, es descriptor de patrón de tinción, revisar extracción

---

## 📁 Archivo 6: IHQ DEL 212 AL 262

**Ubicación:** `pdfs_patologia/IHQ DEL 212 AL 262.pdf`
**Estado:** ✅ Procesado completo (50 casos - IHQ250243 no existe)
**Estado Auditoría:** ✅ Auditoría completa (50/50 casos auditados - 100%)
**Fecha procesamiento:** 2026-01-17
**Fecha inicio auditoría:** 2026-01-17
**Rango procesado:** IHQ250212 - IHQ250262 (salto: IHQ250243)
**Última auditoría:** 2026-01-29 - IHQ250262 (score 88.9%)

### ✅ Casos Auditados (50/50)

<details>
<summary>Ver casos auditados del rango 212-262</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Completitud |
|---|----------------|---------------------|------------------|-------------|
| 1 | IHQ250212 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA MODERADAMENTE DIFERENCIADO mucosa recto, 5 biomarcadores: MMR panel (MLH1/PMS2/MSH2/MSH6) + HER2 NEGATIVO (score 0) - Extracción completa sin errores) |
| 2 | IHQ250213 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.80: Patrón "ni hay marcación para [lista]" captura TTF-1 NEGATIVO. PROCESO INFLAMATORIO MIXTO ganglio cervical, 9 biomarcadores: 8 NEGATIVOS (CK7/CK20/TTF-1/GATA3/CDX2/HEPATOCITO/PAX8/CKAE1AE3) + CD68 POSITIVO - TTF-1 corregido de "NO MENCIONADO"→NEGATIVO) |
| 3 | IHQ250214 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.84: Mejora auditor - Patrón "que corresponde a" para DIAGNOSTICO_COLORACION en descripciones macroscópicas IHQ. ADENOCARCINOMA MUCINOSO INVASIVO colon ascendente, 5 biomarcadores: MMR panel estable (MLH1/PMS2/MSH2/MSH6 expresión nuclear intacta) + HER2 NEGATIVO (score 0) - Sin regresión en casos de referencia) |
| 4 | IHQ250215 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.4.85: Fix auditor - Mapeo SYNAPTOFISINA/CROMOGRANINA A a columnas correctas (IHQ_SINAPTOFISINA con I, IHQ_CROMOGRANINA sin H). CARCINOMA DE CÉLULAS PEQUEÑAS pulmón izquierdo, 7 biomarcadores: CKAE1E3+/P40+/TTF-1+/CD56+/SYNAPTOFISINA+/CROMOGRANINA-/Ki-67 100% - Biomarcadores 100% cobertura, sin regresión en casos de referencia) |
| 5 | IHQ250216 | ✅ Procesado | ✅ Auditado | 66.7% → 100% ✅ (v6.4.86: Patrón "inmunorreactividad positiva fuerte y difusa para [LISTA]" + "y focal para [biomarcador]". CARCINOMA METASTÁSICO ORIGEN GINECOLÓGICO pared abdominal, 6 biomarcadores: P16-/P53+ (sobre expresado-mutado)/PAX8+/RE+ (tinción nuclear fuerte difusa)/RP+ FOCAL (tinción nuclear débil)/WT1+ - Diagnóstico coloración: CARCINOMA METASTÁSICO - P53/RE/RP corregidos de NEGATIVO→POSITIVO) |
| 6 | IHQ250217 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.88: FIX biomarker_extractor - Terminador mejorado patrón "Son negativas para" (no captura secciones siguientes como DIAGNÓSTICO) + unified_extractor - Soporte claves IHQ_ prefijadas (IHQ_PAX8, IHQ_CDX2, IHQ_TTF1, etc.). ADENOCARCINOMA DE PROBABLE ORIGEN GASTROPANCREATOBILIAR clavícula derecha, 7 biomarcadores: CK7+/CK19+/CA19-9+/CK20-/CDX2-/TTF-1-/PAX8- - PAX8 corregido de "NO MENCIONADO"→NEGATIVO) |
| 7 | IHQ250218 | ✅ Procesado | ✅ Auditado | 66.7% ✅ (v6.4.89: Patrón "Ki67o es de X%" para OCR error + "el MUM1 es del X%" con PERCENTAGE. v6.4.90: Filtro selectivo CD3/BCL2 por valor - elimina solo POSITIVOS de "linfocitos T acompañantes", mantiene NEGATIVOS. LINFOMA DIFUSO DE CÉLULAS B GRANDES fenotipo centro germinal masa cuello, 11 biomarcadores: CD20+/CD10+/BCL6+/CD5+ (aberrante)/MUM1 30%/Ki-67 90%/CD38-/CMYC-/CD30-. Score 66.7% por bug auditor (detecta CD3 en CD**3**0), extractores funcionan correctamente) |
| 8 | IHQ250219 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.91: Patrón Ki-67 cualitativo "se distribuye predominantemente" (vs "uniformemente"). v6.4.92: Patrón robusto "No hay expresión para" acepta typo OCR "expreisón" + normalizaciones HHV-8/LMP-1. HIPERPLASIA FOLICULAR REACTIVA ganglio inguinal izquierdo (BENIGNO), 9 biomarcadores: CD20+/CD10+/BCL6+/CD23+/BCL2+/CD3+/Ki-67 POSITIVO (distribución predominante)/HHV-8-/LMP-1- - Ki-67/HHV-8/LMP-1 corregidos de "NO MENCIONADO"→valores correctos) |
| 9 | IHQ250220 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA METASTÁSICO DE PROBABLE ORIGEN PROSTÁTICO ganglio cervical izquierdo, 8 biomarcadores: CK7/CK20/PSA/RACEMASA/CK19/CA19-9/CDX2/TTF-1 - Extracción perfecta, sin errores ni warnings) |
| 10 | IHQ250221 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL) mama izquierda, 4 biomarcadores: HER2 NEGATIVO (0)/Ki-67 30%/Receptor Estrógeno POSITIVO (100%)/Receptor Progesterona POSITIVO (50%) - Alias pendiente: "ESTROGÉNOS" (con acento) no mapeado pero biomarcador extraído correctamente) |
| 11 | IHQ250222 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA METASTÁSICO DE PROBABLE ORIGEN PULMONAR pleura parietal, 3 biomarcadores: NAPSIN/TTF-1/P40 - Extracción perfecta, todos los campos validados correctamente) |
| 12 | IHQ250223 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.91: Patrón "muestran inmunorreactividad con [LISTA]" + tolerancia error OCR "inmunorreactivadad". ADENOCARCINOMA DUCTAL PANCREÁTICO MODERADAMENTE DIFERENCIADO duodeno/vía biliar/páncreas, 11 biomarcadores: CK7+ (marcación focal)/CK19+ (marcación focal)/CA19-9+ (marcación focal)/CDX2+ (marcación focal)/CEA+ (marcación focal)/GATA3-/Mamoglobina-/PAX8-/Estrógenos-/CK20-/TTF-1- - CK7/CK19/CA19-9/CDX2/CEA corregidos de NEGATIVO/NO MENCIONADO→POSITIVO) |
| 13 | IHQ250224 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.93/94/96: Mapeo CK34BETA12→CK34BE12 + Limpieza metadatos IHQ en diagnóstico. ADENOCARCINOMA GLEASON próstata lóbulo derecho, 3 biomarcadores: P63-/RACEMASA+/CK34BE12- - CK34BE12 agregado al sistema, diagnóstico limpio sin "ESTUDIO DE INMUNOHISTOQUIMICA (LÁMINA A)") |
| 14 | IHQ250225 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.4.97: Patrones narrativos complejos para formatos descriptivos. NEVUS MELANOCITICO ACRAL COMPUESTO CON DISPLASIA MODERADA piel planta izquierda, 5 biomarcadores: MELAN-A+/S100+/SOX10+/HMB45+ (desde superficie hacia base)/Ki-67- (sin positividad en melanocitos dérmicos) - HMB45/Ki-67 agregados con formato normalizado: RESULTADO (detalles clínicos)) |
| 15 | IHQ250226 | ✅ Procesado | ✅ Auditado | 88.9% → 100% ✅ (v6.4.98/99: Patrón "Receptores [lista] con marcación [tipo]" + refinamiento terminador. ADENOMA DE LA LACTANCIA mama izquierda (BENIGNO), 5 biomarcadores: S100+/P63+/Calponina+/RE+ (marcación usual en mosaico)/RP+ (marcación usual en mosaico) - RE/RP corregidos de NO MENCIONADO→POSITIVO con detalles clínicos) |
| 16 | IHQ250227 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.5.00: Patrones "células [tipo] [biomarcador]+" + "[bio1] y [bio2] negativo". CARCINOMA ADENOIDE QUÍSTICO pulmón, 4 biomarcadores: P63+/CD117+/TTF-1-/SINAPTOFISINA- - P63/TTF-1 corregidos de NO MENCIONADO→valores correctos con nuevos patrones celulares y conjuntos) |
| 17 | IHQ250228 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.5.01: Patrón "con marcación [intensidad] para" + mapeo GLIPICAN corregido (GLIPICAN sin número → IHQ_GLIPICAN, con número-3 → IHQ_GPC3) + lookahead mejorado "\.\s*[A-Z]" + protección anti-sobrescritura. CARCINOMA DE PROBABLE ORIGEN BILIAR hígado, 12 biomarcadores: CK7+/CK19+/EMA+ FOCAL/CK20-/CDX2-/CA19-9-/ARGINASA-/HEPATOCITO-/GLIPICAN-/GATA3-/TTF1-/CEA- - GLIPICAN corregido de NO MENCIONADO→NEGATIVO, EMA extraído como POSITIVO FOCAL con nuevo patrón) |
| 18 | IHQ250229 | ✅ Procesado | ✅ Auditado | 77.8% ✅ (v6.5.03/04: Patrón "presenta marcación [desc] (resultado)" para estudios cervicales + normalizaciones UPPERCASE Ki-67 + fix auditor truncamiento. ESTUDIO CERVICAL (CERVICITIS AGUDA), 2 biomarcadores: P16-/Ki-67- (marcación basal usual) - P16/Ki-67 corregidos de N/A→NEGATIVO con nuevo patrón específico. PENDIENTE: DIAGNOSTICO_COLORACION no extraído, clasificación malignidad revisar) |
| 19 | IHQ250230 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO CON COMPONENTE MUCINOSO colon transverso, 5 biomarcadores: MLH1+/MSH2+/MSH6+/PMS2+ (MMR estable)/HER2- (Score 1+) - Extracción perfecta, todos los campos validados correctamente) |
| 20 | IHQ250231 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (v6.5.05-10: Fixes múltiples para caso complejo pulmonar. ADENOCARCINOMA INVASIVO DE ORIGEN PULMONAR pulmón izquierdo, 3 biomarcadores: TTF1+ (CON TINCIÓN BAJA)/P40-/SINAPTOFISINA- - v6.5.05-09: patrones narrativos "positivas/negativas para:" + limpieza calificador "con tinción baja" + mapeo "TTF- 1". v6.5.10: protección secciones críticas en _preprocess_multipage_diagnosis. DESCRIPCION_MICROSCOPICA/MACROSCOPICA/DIAGNOSTICO_COLORACION extraídos correctamente) |
| 20 | IHQ250231 | ✅ Procesado | ⏳ Pendiente | - |
| 21 | IHQ250232 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.11: Patrón "Presenta marcación positiva [tipo] de [biomarcador]" agregado. NEGATIVO PARA MALIGNIDAD - Estudio prostático próstata, 3 biomarcadores: P63+/CK34BE12+/RACEMASA- (marcación en células basales) - Diagnóstico: ATROFIA CON ATIPIA LEVE; PROLIFERACIÓN ACINAR PEQUEÑA ATÍPICA (ASAP). P63 corregido de NO EXTRAÍDO→POSITIVO con v6.5.11) |
| 22 | IHQ250233 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL) mama, 4 biomarcadores: RE+ (90% tinción fuerte)/RP-/HER2- (Score 1+)/Ki-67 40% - Extracción perfecta, todos los campos validados correctamente) |
| 23 | IHQ250234 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (CARCINOMA HEPATOCELULAR MODERADAMENTE DIFERENCIADO hígado, 11 biomarcadores: CKAE1AE3+/CK7-/CK19-/CK20-/CA19-9-/CDX2-/TTF-1-/ARGINASA+/HEPATOCITO+/GLYPICAN-3+/GPC3 (alias) - Normalización CKE1E3→CKAE1AE3 correcta. Score 88.9% por nomenclatura en OCR diferente a BD, extracción válida) |
| 24 | IHQ250235 | ✅ Procesado | ✅ Auditado | 77.8% ⚠️ (BIOPSIA MEDULA ÓSEA, 10 biomarcadores: MYOGENIN-/MYOD1-/DESMIN-/CD3+/CD20+/CD38+/CD56-/CD61+/CD34+/CD117+ - v6.5.13: Patrón "No se observan células inmunorreactivas para [lista]" → NEGATIVO. v6.5.14/v6.5.15: DIAGNOSTICO_COLORACION soporte comillas Unicode + fallback. MYOGENINA sin columna [alias: MYOGENIN]) |
| 25 | IHQ250236 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO CON COMPONENTE MUCINOSO colon transverso, 5 biomarcadores: HER2/MSH6/MSH2/MLH1/PMS2 - Caso completo sin observaciones) |
| 26 | IHQ250237 | ✅ Procesado | ✅ Auditado | 100% ✅ (SEMINOMA testículo izquierdo, 7 biomarcadores: OCT4+/PODOPLANINA+/CKAE1AE3+ (focal)/GPC3-/GLIPICAN-/AFP-/CD30- - v6.5.24-28: Alias CKAE1/E3, CD 30; v6.5.26: Limpiar "HALLAZGOS MORFOLOGICOS Y DE INMUNOHISTOQUIMICA COMPATIBLES CON"; v6.5.28: Terminador patrón v6.4.86 mejorado para no capturar negativos) |
| 27 | IHQ250238 | ✅ Procesado | ✅ Auditado | 100% ✅ (HIPERPLASIA GLANDULAR Y ESTROMAL próstata, 4 biomarcadores: RACEMASA-/P63+ (difusa)/CK5/6+/CK34BETAE12+ (difusa) - v6.5.29: Unificación mapeo CK34BE12→IHQ_CK34BETAE12. Panel células basales preservadas, compatible con hiperplasia benigna) |
| 28 | IHQ250239 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA MUCINOSO colon rectosigmoide, 4 biomarcadores: MLH1+ (expresión nuclear intacta)/MSH2+ (expresión nuclear intacta)/MSH6+ (expresión nuclear intacta)/PMS2+ (expresión nuclear intacta) - v6.5.30-35: Fix protocolo CAP MMR - v6.5.35 implementa búsqueda en DESCRIPCIÓN MICROSCÓPICA primero para capturar "Resultado de [marker]: expresión nuclear intacta". Panel MMR estable. Validación anti-regresión OK: IHQ250212/IHQ250230 sin regresión) |
| 29 | IHQ250240 | ✅ Procesado | ✅ Auditado | 100% ✅ (NEOPLASIA MIELOPROLIFERATIVA/MIELODISPLASICA médula ósea, 9 biomarcadores: CD10/CD117/CD15/CD20/CD3/CD34/CD56/GLICOFORINA/MIELOPEROXIDASA - Extracción perfecta, todos los campos validados correctamente sin errores ni warnings) |
| 30 | IHQ250241 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA PAPILAR DE PROBABLE ORIGEN TIROIDEO hemicuello derecho, 6 biomarcadores: CK7+/CK20-/CKAE1AE3+/PAX8+/TTF1+/TIROGLOBULINA+ - v6.5.36: TIROGLOBULINA agregada al sistema (FUNC-03) y caso reprocesado (FUNC-06). Extracción perfecta con 6/6 biomarcadores) |
| 31 | IHQ250242 | ✅ Procesado | ✅ Auditado | 88.9% ✅ (ADENOCARCINOMA INVASIVO ENDOCERVICAL cérvix, 7 biomarcadores: P16+/P40-/Receptor Estrógeno-/VIMENTINA-/CKAE1AE3+/Ki-67: 80%/PAX8- - v6.5.39-45: Ki-67 porcentaje preservado (POSITIVO→80%), CKAE1AE3 corregido (NEGATIVO→POSITIVO), P40 corregido con PASE FINAL ABSOLUTO (POSITIVO→NEGATIVO). Contexto: dos regiones (exocervical displasia vs endocervical adenocarcinoma), valores del diagnóstico principal prevalecen. Factor pronóstico detectado (Ki-67: 80%/RE: NEGATIVO)) |
| - | IHQ250243 | ❌ No existe | - | **Número de caso saltado** (no presente en PDF ni BD, la numeración pasa de IHQ250242 → IHQ250244) |
| 32 | IHQ250244 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA INVASIVO NEGATIVO PARA INESTABILIDAD MICROSATELITAL mucosa rectal, 4 biomarcadores: Panel MMR estable (MLH1+/MSH2+/MSH6+/PMS2+ expresión nuclear intacta) - Extracción perfecta, todos los campos validados correctamente sin errores ni warnings. Factor pronóstico: NO APLICA [biomarcadores MMR no son pronósticos]) |
| 33 | IHQ250245 | ✅ Procesado | ✅ Auditado | 100% ✅ (LESIÓN HIPOFISARIA hipófisis resección, 11 biomarcadores: Panel neuroendocrino completo ACTH/CD3/CD68/CROMOGRANINA/FSH/GH/Ki-67 <1%/LH/PROLACTINA/SYNAPTOFISINA/TSH - Extracción perfecta de panel hormonal hipofisario. Malignidad: BENIGNO. Factor pronóstico: Ki-67 <1%. Sin errores ni warnings) |
| 34 | IHQ250246 | ✅ Procesado | ✅ Auditado | 100% ✅ (TUMOR FILOIDES BORDERLINE mama derecha, 1 biomarcador: Ki-67 30% - Malignidad: BENIGNO. Extracción perfecta sin errores ni warnings. Factor pronóstico: Ki-67 30%) |
| 35 | IHQ250247 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA PAPILAR INVASIVO mama izquierda, 8 biomarcadores: ER/PR/HER2/CK5-6/P63/SINAPTOFISINA/GATA3/Ki-67 - v6.5.50: Extracción correcta con porcentajes en receptores (ER: POSITIVO 90%, PR: POSITIVO 90%), CK5-6 y SINAPTOFISINA negativos (mioepitelio). Malignidad: MALIGNO. Sin errores ni warnings) |
| 36 | IHQ250248 | ✅ Procesado | ✅ Auditado | 100% ✅ (TUMOR MALIGNO INDIFERENCIADO CON MATERIAL METAPLÁSICO OSTEOGÉNICO mama izquierda, 13 biomarcadores: ER-/PR-/HER2-/GATA3-/MAMAGLOBINA-/SOX10-/CKAE1AE3-/DESMIN-/CD34-/EMA-/P63-/E-Cadherina-/Ki-67: 30% - v6.5.51: Nuevo patrón "Los siguientes marcadores son negativos: [lista]" + MAMAGLOBINA agregada al sistema (FUNC-03). Panel completo negativo excepto Ki-67. Malignidad: MALIGNO. Sin errores) |
| 37 | IHQ250249 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA GLEASON próstata lóbulo derecho, 3 biomarcadores: Panel prostático CK34BETAE12/P63/RACEMASA - Proliferación acinar atípica. Malignidad: MALIGNO. Extracción perfecta sin errores ni warnings. Factor pronóstico: NO APLICA) |
| 38 | IHQ250250 | ✅ Procesado | ✅ Auditado | 100% ✅ (NEGATIVO PARA LESIÓN ESCAMOSA exocérvix, 2 biomarcadores: P16-/Ki-67 (distribución basal) - v6.5.52+v6.5.53: Nuevo patrón "se realizan cortes histológicos para [lista]" (sin "tinción") + Ki-67 narrativo "distribución a nivel de la capa basal". Malignidad: BENIGNO. Sin errores) |
| 39 | IHQ250251 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA INVASIVO DE ORIGEN PULMONAR lóbulo superior derecho, 5 biomarcadores: Panel pulmonar CK7+/CK20-/TTF-1+/P40-/NAPSIN+ - Malignidad: MALIGNO. Extracción perfecta sin errores ni warnings. Factor pronóstico: NO APLICA) |
| 40 | IHQ250252 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA ESCAMOCELULAR INVASIVO NOS cérvix, 2 biomarcadores: P40+/P16+ - Malignidad: MALIGNO. Extracción perfecta sin errores ni warnings. Factor pronóstico: NO APLICA) |
| 41 | IHQ250253 | ✅ Procesado | ✅ Auditado | 88.9% ⚠️ (DERMATOFIBROSARCOMA PROTUBERANS región malar derecha, 11 biomarcadores: CD34+/H_CALDESMON+/Ki-67: 40%/DESMIN-/SMA-/MIOGENINA-/SOX10-/S100-/CKAE1AE3-/BETACATENINA-/CD11- - v6.5.54+v6.5.55: Punto interno en lista negativos + patrón genérico + FUNC-03 MIOGENINA/CD11. Cobertura 100%, score 88.9% por alias H_CALDESMON. Malignidad: MALIGNO) |
| 42 | IHQ250254 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.58+v6.5.59+v6.5.60+v6.5.61: Fix bifásico "(focal)" + "en especimen" + calificadores con espacios. CARCINOSARCOMA DEL OVARIO tuba uterina/ovario, 11 biomarcadores: EMA/DESMIN/SALL4/ER/WT1/PAX8/Ki-67/S100/CKAE1AE3/P53 - MALIGNO) |
| 43 | IHQ250255 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.62: Ki-67 narrativo "es el esperado en [contexto]". HIPERPLASIA FOLICULAR Y SINUSOIDAL REACTIVA ganglio linfático cervical, 8 biomarcadores: Ki-67/BCL2/BCL6/CD3/CD5/CD20/CD38/PAX5 - BENIGNO) |
| 44 | IHQ250256 | ✅ Procesado | ✅ Auditado | 100% ✅ (ADENOCARCINOMA INVASIVO mucosa gástrica, 2 biomarcadores: HER2/CKAE1AE3 - MALIGNO) |
| 45 | IHQ250257 | ✅ Procesado | ✅ Auditado | 100% ✅ (Caso completo - MALIGNO) |
| 46 | IHQ250258 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.63-68: ER/PR formato "NEGATIVO (MENOR AL 1%)" + paréntesis opcionales + detección `(<X%)`. CARCINOMA INFILTRANTE DUCTAL GRADO 3 mama derecha, 8 biomarcadores: CK20/CKAE1AE3/HER2/Ki-67/P40/ER/PR/Mamaglobina - MALIGNO) |
| 47 | IHQ250259 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.69: MMR captura descriptiva completa hasta punto final. ADENOCARCINOMA INVASIVO CON PATRON MICROSATELITAL ESTABLE mucosa rectal, 5 biomarcadores: HER2/MSH2/MSH6/MLH1/PMS2 con marcación citoplasmática 90% - MALIGNO) |
| 48 | IHQ250260 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.70-73: MMR "Resultado de" captura multilínea. ADENOCARCINOMA BIEN DIFERENCIADO INFILTRANTE colon izquierdo, 5 biomarcadores: MLH1/MSH2/MSH6/PMS2/HER2 - MALIGNO) |
| 49 | IHQ250261 | ✅ Procesado | ✅ Auditado | 100% ✅ (NEOPLASIA DE CELULAS B MADURAS médula ósea, 8 biomarcadores: BCL6/CD10/CD20/CD3/CD5/CMYC/MUM1/PAX5 - MALIGNO) |
| 50 | IHQ250262 | ✅ Procesado | ✅ Auditado | 88.9% ⚠️ (WARNING DIAGNOSTICO_PRINCIPAL contaminado "LABORATORIO CLINICO NO". ADENOCARCINOMA INVASIVO mucosa rectal, 4 biomarcadores: MLH1/MSH2/MSH6/PMS2 100% correctos - MALIGNO) |

</details>

---

## 🔧 Comandos Útiles

### Auditar un caso individual
```bash
python herramientas_ia/auditor_sistema.py IHQ250010 --inteligente
```

### Auditar múltiples casos con callery
```bash
python herramientas_ia/callery_workflow.py --iniciar --casos "IHQ250010,IHQ250011,IHQ250012"
```

### Verificar casos en BD
```python
from core.database_manager import get_all_records_as_dataframe
df = get_all_records_as_dataframe()
print(df['Numero de caso'].tolist())
```

---

## 📝 Notas

- **Formato de archivo:** Este documento se actualiza manualmente después de cada auditoría
- **Estados:**
  - ✅ Auditado: Validado completamente
  - ⏳ Pendiente: Procesado pero no auditado
  - ❓ Verificar: Estado incierto, requiere verificación
  - ❌ Error: Caso con problemas detectados

---

**Última actualización:** 2026-02-03 (Estado: 7 archivos procesados, 6 auditados completos + Archivo 7 auditado hasta IHQ250300 - 344 casos procesados [3 números faltantes: IHQ250243, IHQ250269, IHQ250288], 300 casos auditados, 44 pendientes de auditoría)

---

## 🔬 Casos con Score 100%

| Caso | Fecha | Observaciones |
|------|-------|---------------|
| IHQ250010 | 2025-12-02 | Score perfecto |
| IHQ250011 | 2025-12-02 | v6.3.9 - Corrección endometriosis |
| IHQ250012 | 2025-12-04 | v6.4.0 - MPO, CICLINA_D1, CD61 completos |
| IHQ250013 | 2025-12-05 | v6.4.0 - DIAGNOSTICO_COLORACION y MALIGNIDAD |
| IHQ250116 | 2026-01-02 | v6.3.89 - HER2, ER, PR, P63, CK5/6, S100, CALPONINA, CROMOGRANINA, SINAPTOFISINA |
| IHQ250014 | 2025-12-09 | v6.3.13/14/15 - 3 bugs críticos corregidos |
| IHQ250015 | 2025-12-09 | v3.3.3/3.3.4 - Auditor mejorado |
| IHQ250016 | 2025-12-09 | 100%* - Warning menor de formato (contenido correcto) |
| IHQ250017 | 2025-12-09 | v6.3.20/21/22 + v3.3.5 - HER2 score completo, MMR prioridad secciones, corrección ortográfica |
| IHQ250018 | 2025-12-12 | v6.4.1 - ACTINA_MUSCULO_LISO agregado al sistema (100% cobertura biomarcadores) |
| IHQ250019 | 2025-12-13 | v6.3.21 - P63 alias, MOSAICO→POSITIVO, Patrón 0C |
| IHQ250020 | 2025-12-13 | Carcinoma escamocelular oral no queratinizante |
| IHQ250021 | 2025-12-13 | v6.3.22 - Patrón 0D diagnósticos descriptivos |
| IHQ250022 | 2025-12-13 | v6.3.23+v6.3.24 - Biomarcadores limpios |
| IHQ250023 | 2025-12-13 | v6.3.25 - Patrón 1A1 "SUGESTIVOS DE" |
| IHQ250026 | 2025-12-13 | Melanoma pulmonar (8 biomarcadores) |
| IHQ250027 | 2025-12-13 | Carcinoma escamocelular lengua (Ki-67 90%) |
| IHQ250028 | 2025-12-13 | v6.3.27+v6.3.28+v6.3.29 - HER2 limpio |
| IHQ250029 | 2025-12-13 | Linfoma células B maduras (9 biomarcadores) |
| IHQ250030 | 2025-12-13 | Mieloma múltiple médula ósea |
| IHQ250031 | 2025-12-15 | v6.3.36+v6.3.37 - HER2 EQUIVOCO, Diagnóstico "Historia de" |
| IHQ250032 | 2025-12-15 | v6.3.38 - TDT/CK19 en display_names, TIMOMA TIPO B2 |
| IHQ250033 | 2025-12-15 | v6.3.39 - Sync alias SYNAPTOFISINA/CKAE1E3, CARCINOIDE TÍPICO |
| IHQ250034 | 2025-12-15 | v6.3.40 - Captura descripción microscópica página 2 |
| IHQ250035 | 2025-12-16 | v6.3.42 - Exclusión MMR del extractor narrativo, Adenocarcinoma sigmoides |
| IHQ250036 | 2025-12-16 | Carcinoma poco cohesivo mucosa estómago (6 biomarcadores) |
| IHQ250037 | 2025-12-16 | v6.3.44 - HHV8/CD34, patrón "QUE FAVORECEN", COLITIS AGUDA Y CRÓNICA |
| IHQ250038 | 2025-12-16 | Adenocarcinoma rectal panel MMR, PATRÓN MICROSATELITAL ESTABLE |
| IHQ250039 | 2025-12-17 | v6.3.45 - P63/CK5_6 paréntesis invertidos, RE marcación difusa, CARCINOMA DUCTAL IN SITU mama |
| IHQ250040 | 2025-12-17 | CRANEOFARINGIOMA ADAMANTINOMATOSO región clivus (5 biomarcadores: CK7/Ki67/RP/S100/SOX10) |
| IHQ250041 | 2025-12-17 | CARCINOMA ESCAMOCELULAR INVASIVO cuero cabelludo (1 biomarcador: P40+) |
| IHQ250042 | 2025-12-17 | v6.3.46 - SV40/C4D trasplante renal, RECHAZO INJERTO RENAL postrasplante |
| IHQ250091 | 2025-12-19 | v6.3.72+v6.3.73 - Patrones narrativos SIEMPRE ejecutar, excluir células acompañantes, LINFOMA DE CÉLULAS B GRANDES DIFUSO |
| IHQ250093 | 2025-12-19 | v6.3.74 - Patrón "No hay inmunorreactividad para X ni Y", CAMBIOS REPARATIVOS órbita |
| IHQ250094 | 2025-12-19 | v6.3.75+v6.3.76 - CD1a preservado, word-boundaries NIC, INFLAMACIÓN CRÓNICA GRANULOMATOSA hígado BENIGNO |
| IHQ250095 | 2025-12-19 | v6.3.77 - LINFOMA agregado a keywords malignidad, LINFOMA DIFUSO DE CÉLULAS B GRANDES retroperitoneo MALIGNO |
| IHQ250096 | 2025-12-19 | LINFOMA LINFOBLÁSTICO DE CÉLULAS T mediastino (11 biomarcadores) MALIGNO |
| IHQ250097 | 2025-12-19 | ADENOMA HIPOFISIARIO PRODUCTOR DE PROLACTINA silla turca (5 biomarcadores) BENIGNO |
| IHQ250098 | 2025-12-19 | CARCINOMA DUCTAL INFILTRANTE mama derecha (3 biomarcadores: RE/P63/CK5_6) MALIGNO |
| IHQ250099 | 2025-12-19 | ADENOCARCINOMA DIFUSO POBREMENTE COHESIVO estómago (2 biomarcadores) MALIGNO |
| IHQ250100 | 2025-12-19 | BIOPSIA INJERTO RENAL trasplante (SV40/C4d) - Requiere mejora extractor |
| IHQ250102 | 2025-12-20 | v6.3.74 - ER/PR con intensidad+porcentaje, CARCINOMA DUCTAL INFILTRANTE mama |
| IHQ250103 | 2025-12-20 | v6.3.75 - IHQ_ORGANO limpieza contaminación, CARCINOMA METASTÁSICO ganglio axilar |
| IHQ250104 | 2025-12-20 | SV40/C4D "NO MENCIONADO", BIOPSIA INJERTO RENAL trasplante BENIGNO |
| IHQ250105 | 2025-12-20 | v6.3.77 - PASE FINAL CD20/CD23/CD34 fix NEGATIVO, LEUCEMIA/LINFOMA LINFOBLÁSTICO CÉLULAS B |
| IHQ250106 | 2025-12-20 | v6.3.78 - GATA3 separador "ni", keywords benignos SIN EVIDENCIA NEOPLASIA |
| IHQ250107 | 2025-12-20 | v6.3.79 - Panel NO VALORABLE completo, CARCINOMA METASTASICO fosa ilíaca (10 biomarcadores) |
| IHQ250109 | 2025-12-24 | v6.3.82 - Fix P53/IDH persistence & keys (p53:NEGATIVO(WT), IDH:NEGATIVO(WT), GFAP:POSITIVO) |
| IHQ250110 | 2025-12-24 | v6.3.83 - Fix CKAE1E3 persistence (mapped to IHQ_CKAE1AE3). Score 100%. ADENOCARCINOMA METASTASICO. |
| IHQ250111 | 2025-12-24 | v6.3.84 - Fix narrative extraction (Calponina, P63, CK5/6) & RE Mosaic value. Score 100%. LESIÓN FIBROEPITELIAL. |
| IHQ250112 | 2026-01-02 | v6.3.85 - Fix P16/Ki67 in blocks. Score 100%. CARCINOMA ESCAMOCELULAR. |
| IHQ250113 | 2026-01-02 | v6.3.86 - Fix RE mosaico y Calponina/p63. Score 100%. HIPERPLASIA PSEUDOANGIOMATOSA. |
| IHQ250114 | 2026-01-02 | v6.3.87 - MMR Panel intacto y P53 mutado. Score 100%. CARCINOMA ENDOMETRIOIDE. |
| IHQ250115 | 2026-01-02 | v6.3.88 - CD10, Ciclina D1 y SOX11 (con versiones de prueba v1-v9). Score 100%. LLC/Linfoma. |
| IHQ250117 | 2026-01-03 | v6.3.96 - Fix dash-prefix ER/PR/HER2 & greedy capture. Score 100% (Manual verification). ADENOCARCINOMA PROSTÁTICO. |
| IHQ250118 | 2026-01-03 | v6.3.97 - Fix SV40/C4D "ambos negativos" & multiline diagnostic principal. Score 100% (Manual verification). NEFRITIS TÚBULO-INTERSTICIAL. |
| IHQ250119 | 2026-01-03 | v6.4.2 - Fix PR split, GATA3 mapping, SCORE truncation & Merge found biomarkers into IHQ_ESTUDIOS_SOLICITADOS (GATA3 persistence). Score 100%. CARCINOMA INVASIVO MAMA. |
| IHQ250120 | 2026-01-03 | v6.4.3 - Fix negative list extraction & MATR-1/MART-1 alias mapping. Score 100%. MELANONIQUIA ESTRIADA (Negativo para proliferación melanocítica). |
| IHQ250127 | 2026-01-05 | v6.4.3 - Fix CD34/CD117 negation, CD56 parenthetical, studies fallback. Score 100%. MIELOFIBROSIS (médula ósea). |
| IHQ250128 | 2026-01-05 | v6.4.4 - Fix end-of-macro studies list, clean organ ID/date prefix, normalize RE/RP in studies. Score 100%. CARCINOMA MAMA. |
| IHQ250129 | 2026-01-05 | v6.4.5 - MMR markers correctly extracted. Malignancy fixed for ADENOCARCINOMA with GRADO I (MALIGNO). Score 100%. |
| IHQ250133 | 2026-01-05 | v6.4.5 - HER2 extraction fixed (mapping & regex), UnboundLocalError resolved for stable batch processing. Score 100%. |
| IHQ250134 | 2026-01-05 | v6.4.5 - Full narrative extraction verified (CK7, RE, RP, PAX8, P16, P53). Regional vaginal diagnosis correctly mapped. Score 100%. |
| IHQ250135 | 2026-01-05 | v6.4.5 - Full profile verified (RE, RP, P53, HER2, MLH1, MSH2, MSH6, PMS2). Metastatic adenocarcinoma diagnosis correctly captured. Score 100%. |
| IHQ250136 | 2026-01-05 | v6.4.8 - Fix Mamoglobina definition, sections headers (RESULTADO:) and ER/PR " son positivos\ intensity capture. Score 100%. |
| IHQ250141 | 2026-01-06 | v6.4.9 - Fix CD138/CD56 spaced variants, CD177→CD117 OCR alias, CICLINA without D1, LAMBDA implicit post-processing, "de forma" list pattern. Score 100%. NEOPLASIA CÉLULAS PLASMÁTICAS. |
| IHQ250142 | 2026-01-06 | Score: 100.0% - ADENOCARCINOMA DE ORIGEN PULMONAR lóbulo superior izquierdo. Extracción completa. |
| IHQ250143 | 2026-01-06 | Score: 100.0% - FASCITIS NODULAR piel pie derecho. 10 biomarcadores correctamente extraídos. BENIGNO. |
| IHQ250246 | 2026-01-28 | Score: 100.0% - CARCINOMA DUCTAL INFILTRANTE mama izquierda. 8 biomarcadores (HER2, Ki-67, ER, PR, CK5/6, P63, GATA3, E-Cadherina). MALIGNO. |
| IHQ250247 | 2026-01-28 | v6.5.50 - Fix ER/PR percentage extraction "(90%)" format. Score: 100.0% - CARCINOMA ESCAMOCELULAR mediano diferenciado lengua. 4 biomarcadores (ER, PR, HER2, Ki-67). MALIGNO. |
| IHQ250248 | 2026-01-28 | v6.5.51 - Patrón "Los siguientes marcadores son negativos: [lista]" + FUNC-03 MAMAGLOBINA. Score: 100.0% - TUMOR MALIGNO INDIFERENCIADO mama izquierda. 13 biomarcadores. MALIGNO. |
| IHQ250249 | 2026-01-28 | Score: 100.0% - PROLIFERACIÓN ACINAR ATÍPICA próstata lóbulo derecho. 3 biomarcadores (CK34BETAE12, P63, RACEMASA). MALIGNO. |
| IHQ250250 | 2026-01-28 | v6.5.52+v6.5.53 - "se realizan cortes histológicos para [lista]" + Ki-67 narrativo "distribución a nivel de". Score: 100.0% - NEGATIVO PARA LESIÓN ESCAMOSA exocérvix. 2 biomarcadores (P16, Ki-67). BENIGNO. |
| IHQ250251 | 2026-01-28 | Score: 100.0% - ADENOCARCINOMA INVASIVO DE ORIGEN PULMONAR lóbulo superior derecho. 5 biomarcadores (CK7, CK20, TTF-1, P40, NAPSIN). MALIGNO. |
| IHQ250252 | 2026-01-28 | Score: 100.0% - CARCINOMA ESCAMOCELULAR INVASIVO NOS cérvix. 2 biomarcadores (P40, P16). MALIGNO. |
| IHQ250253 | 2026-01-28 | v6.5.54+v6.5.55 - Punto interno en lista negativos + patrón genérico + FUNC-03 MIOGENINA/CD11. Score: 88.9% (100% cobertura, H_CALDESMON alias) - DERMATOFIBROSARCOMA PROTUBERANS región malar derecha. 11 biomarcadores. MALIGNO. |
| IHQ250254 | 2026-01-28 | v6.5.58+v6.5.59+v6.5.60+v6.5.61 - Fix bifásico "(focal)" capture + "en especimen" pattern + calificadores con espacios. Score: 100.0% - CARCINOSARCOMA DEL OVARIO tuba uterina/ovario. 11 biomarcadores (EMA, DESMIN, SALL4, ER, WT1, PAX8, Ki-67, S100, CKAE1AE3, P53). MALIGNO. |
| IHQ250255 | 2026-01-28 | v6.5.62 - Fix Ki-67 narrativo "es el esperado en [contexto]" (hiperplasias reactivas). Score: 100.0% - HIPERPLASIA FOLICULAR Y SINUSOIDAL REACTIVA ganglio linfático cervical. 8 biomarcadores (Ki-67, BCL2, BCL6, CD3, CD5, CD20, CD38, PAX5). BENIGNO. |
| IHQ250256 | 2026-01-28 | Score: 100.0% - ADENOCARCINOMA INVASIVO mucosa gástrica. 2 biomarcadores (HER2, CKAE1AE3). MALIGNO. |
| IHQ250257 | 2026-01-28 | Score: 100.0% - Caso completo. |
| IHQ250258 | 2026-01-28 | v6.5.63+v6.5.64+v6.5.65+v6.5.66+v6.5.67+v6.5.68 - Fix ER/PR formato "NEGATIVO (MENOR AL 1%)" con paréntesis opcionales + detección `(<X%)`. Score: 100.0% - CARCINOMA INFILTRANTE DUCTAL GRADO 3 mama derecha. 8 biomarcadores (CK20, CKAE1AE3, HER2, Ki-67, P40, ER, PR, Mamaglobina). MALIGNO. |
| IHQ250259 | 2026-01-29 | v6.5.69 - Fix MMR (MLH1/MSH2/MSH6/PMS2) captura información completa descriptiva hasta punto final. Score: 100.0% - ADENOCARCINOMA INVASIVO CON PATRON MICROSATELITAL ESTABLE mucosa rectal. 5 biomarcadores (HER2, MSH2, MSH6, MLH1, PMS2: con marcación citoplasmática 90%). MALIGNO. |
| IHQ250260 | 2026-01-29 | v6.5.70+v6.5.71+v6.5.72+v6.5.73 - Fix MMR "Resultado de" captura multilínea (PMS2 con salto interno en paréntesis "patrón punteado y\nnuclear moteado"). Patrón `[^\n(]+(?:\([^)]*(?:\n[^)]*)*\))?` detiene correctamente sin contaminar con líneas siguientes. Score: 100.0% - ADENOCARCINOMA BIEN DIFERENCIADO INFILTRANTE colon izquierdo. 5 biomarcadores (MLH1, MSH2, MSH6, PMS2, HER2). MALIGNO. |
| IHQ250261 | 2026-01-28 | Score: 100.0% - NEOPLASIA DE CELULAS B MADURAS médula ósea. 8 biomarcadores (BCL6, CD10, CD20, CD3, CD5, CMYC, MUM1, PAX5). MALIGNO. |
| IHQ250262 | 2026-01-29 | Score: 88.9% - WARNING: DIAGNOSTICO_PRINCIPAL contaminado con "LABORATORIO CLINICO NO" (tabla administrativa). Biomarcadores 100% correctos (4/4: MLH1, MSH2, MSH6, PMS2). ADENOCARCINOMA INVASIVO mucosa rectal. MALIGNO. |
| IHQ250263 | 2026-01-29 | v6.5.75 - Fix limpieza prefijo "LOS HALLAZGOS MORFOLÓGICOS E INMUNOHISTOQUÍMICOS FAVORECEN:" en DIAGNOSTICO_PRINCIPAL (unified_extractor.py línea 482). Score: 100.0% - TUMOR DE CÉLULAS GRANULARES muslo izquierdo. 4 biomarcadores (S100, CD68, SOX10, CKAE1AE3). BENIGNO. |

---

## 📁 Archivo 7: IHQ DEL 263 AL 313

**Ubicación:** `pdfs_patologia/IHQ DEL 263 AL 313.pdf`
**Estado:** ✅ Procesado (49 casos - IHQ250269 y IHQ250288 no procesados)
**Estado Auditoría:** 🔄 En progreso (5/49 casos auditados - 10%)
**Fecha procesamiento:** 2026-01-29
**Fecha inicio auditoría:** 2026-01-29
**Rango procesado:** IHQ250263 - IHQ250313 (saltos: IHQ250269, IHQ250288)
**Última auditoría:** 2026-01-29 - IHQ250267 (score 100%)

### ✅ Casos Auditados (5/49)

<details>
<summary>Ver casos auditados del rango 263-313</summary>

| # | Número de Caso | Estado Procesamiento | Estado Auditoría | Completitud |
|---|----------------|---------------------|------------------|-------------|
| 1 | IHQ250263 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.75: Limpieza prefijo "LOS HALLAZGOS MORFOLÓGICOS E INMUNOHISTOQUÍMICOS FAVORECEN:" en DIAGNOSTICO_PRINCIPAL. TUMOR DE CÉLULAS GRANULARES muslo izquierdo, 4 biomarcadores: S100+/CD68+/SOX10+/CKAE1AE3- - BENIGNO) |
| 2 | IHQ250264 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA ESCAMOCELULAR INVASIVO segmento intestino delgado, 7 biomarcadores: CKAE1AE3/CROMOGRANINA/P16/P40/S100/SOX10/SYNAPTOFISINA - MALIGNO) |
| 3 | IHQ250265 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA ESCAMOCELULAR MODERADAMENTE DIFERENCIADO vagina, 3 biomarcadores: Ki-67 60%/P16/P40 - MALIGNO) |
| 4 | IHQ250266 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.76: Fix auditor - filtro valores espurios 1-2 chars. CARCINOMA SEROSO DE ALTO GRADO cérvix, 10 biomarcadores: P16+/P63-/P40-/P53 mutado/SOX10-/CKAE1AE3+/Ki-67 80%/PAX8-/Estrógenos+/Vimentina+ - MALIGNO) |
| 5 | IHQ250267 | ✅ Procesado | ✅ Auditado | 100% ✅ (CARCINOMA POBREMENTE DIFERENCIADO DE PROBABLE ORIGEN EN MAMA útero/ovarios, 17 biomarcadores: CA19-9/CDX2/CK19/CK20/CK7/CKAE1AE3/CROMOGRANINA/GATA3/Ki-67 30%/P16/P40/P53/PAX8/Estrógenos+/SYNAPTOFISINA/TTF1/WT1 - MALIGNO) |
| 6 | IHQ250268 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.79: Patrones agrupados paréntesis + CK34BETA sin E12 + P63 "pierden expresión". ADENOCARCINOMA ACINAR GRUPO 1 GLEASON 3+3=6 próstata lóbulo izquierdo, 3 biomarcadores: P63-/CK34BETAE12-/RACEMASA+ - MALIGNO) |
| - | IHQ250269 | ❌ No procesado | - | **Número de caso faltante** |
| 7 | IHQ250270 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.80: Patrón "positividad heterogénea". TUMOR DE CÉLULAS DE LA GRANULOSA DEL ADULTO ovario izquierdo, 6 biomarcadores: CK7-/CKAE1AE3 heterog+/EMA-/INHIBINA heterog+/PAX8-/CALRETININA heterog+ - BENIGNO) |
| 8 | IHQ250271 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.81: Patrón "ausencia de expresión" P53. LEIOMIOMA útero, 4 biomarcadores: H CALDESMON+/P16-/Ki-67 <5%/P53- (ausencia expresión) - BENIGNO) |
| 9 | IHQ250272 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.82: Fix mapeo IHQ_CAM52 obsoleto. ADENOMA HIPOFISIARIO PITNET TIPO TIROTROPO región selar, 8 biomarcadores: Ki-67 3%/CAM5.2-/SYNAPTOFISINA+/TSH+/GH-/FSH-/PROLACTINA-/ACTH- - BENIGNO) |
| 10 | IHQ250273 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.86: FIX extracción TTF-1 con terminador "así como positividad". CARCINOMA NEUROENDOCRINO DE CELULA GRANDE pulmón izquierdo, 5 biomarcadores: CROMOGRANINA-/Ki-67 60%/P40-/SYNAPTOFISINA+/TTF-1+ - MALIGNO) |
| 11 | IHQ250274 | ✅ Procesado | ✅ Auditado | 90% ⚠️ (v6.5.89: FIX completo extracción listas biomarcadores (GFAP/S100/EMA/SYNAPTOFISINA+/CAM5.2/CROMOGRANINA/NEU-N). Warning DIAGNOSTICO_COLORACION aceptable (caso extrainstitucional). EPENDIMOMA GRADO II cráneo fosa posterior, 7 biomarcadores correctos - BENIGNO) |
| 12 | IHQ250275 | ✅ Procesado | ✅ Auditado | 100% ✅ (v6.5.90: FIX extracción "encontrándose ambos negativos" para SV40 y C4D. SIN EVIDENCIA DE RECHAZO ACTIVO biopsia injerto renal, 2 biomarcadores: SV40-/C4D- - BENIGNO) |
| 13 | IHQ250276 | ✅ Procesado | ✅ Auditado | 90% ⚠️ (v6.5.91: FIX CK5/6 "negativa para mioepiteliales" + CALRETININA "es negativa" (v6.5.90). CK5/6 extraía solicitud macroscópica ("para tinción con") como POSITIVO → Ahora captura resultado microscópico ("negativa para mioepiteliales") como NEGATIVO. Warning MALIGNIDAD (BD=MALIGNO pero diagnóstico PAPILOMA INTRADUCTAL ESCLEROSANTE = benigno). MAMA IZQUIERDA, 5 biomarcadores: RE+/P63+/CK5/6-/S100+/CALRETININA- - BENIGNO con atipia) |
| 14 | IHQ250277 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 15 | IHQ250278 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 16 | IHQ250279 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 17 | IHQ250280 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 18 | IHQ250281 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 19 | IHQ250282 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 20 | IHQ250283 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 21 | IHQ250284 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 22 | IHQ250285 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 23 | IHQ250286 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 24 | IHQ250287 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| - | IHQ250288 | ❌ No procesado | - | **Número de caso faltante** |
| 25 | IHQ250289 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 26 | IHQ250290 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 27 | IHQ250291 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 28 | IHQ250292 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 29 | IHQ250293 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 30 | IHQ250294 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 31 | IHQ250295 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 32 | IHQ250296 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 33 | IHQ250297 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 34 | IHQ250298 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 35 | IHQ250299 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 36 | IHQ250300 | ✅ Procesado | ✅ Auditado | Auditado 2026-02-03 |
| 37 | IHQ250301 | ✅ Procesado | ⏳ Pendiente | - |
| 38 | IHQ250302 | ✅ Procesado | ⏳ Pendiente | - |
| 39 | IHQ250303 | ✅ Procesado | ⏳ Pendiente | - |
| 40 | IHQ250304 | ✅ Procesado | ⏳ Pendiente | - |
| 41 | IHQ250305 | ✅ Procesado | ⏳ Pendiente | - |
| 42 | IHQ250306 | ✅ Procesado | ⏳ Pendiente | - |
| 43 | IHQ250307 | ✅ Procesado | ⏳ Pendiente | - |
| 44 | IHQ250308 | ✅ Procesado | ⏳ Pendiente | - |
| 45 | IHQ250309 | ✅ Procesado | ⏳ Pendiente | - |
| 46 | IHQ250310 | ✅ Procesado | ⏳ Pendiente | - |
| 47 | IHQ250311 | ✅ Procesado | ⏳ Pendiente | - |
| 48 | IHQ250312 | ✅ Procesado | ⏳ Pendiente | - |
| 49 | IHQ250313 | ✅ Procesado | ⏳ Pendiente | - |

</details>

---

## 📋 Casos Incompletos Detectados

**Última actualización:** 2026-01-08 00:49:12
**Fuente:** reporte_importacion_20260108_001346.json

| Caso | Paciente | Completitud | Biomarcadores Faltantes |
|------|----------|-------------|-------------------------|
