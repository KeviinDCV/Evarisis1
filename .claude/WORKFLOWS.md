# 🔄 Workflows Maestros del Sistema EVARISIS

**Workflows esenciales con 4 agentes especializados**

---

## WORKFLOW 1: Procesamiento Completo de Caso Nuevo

```
1. Usuario procesa PDF → Sistema EVARISIS extrae datos
   ⭐ NUEVO v6.0.11: FALLBACK AUTOMÁTICO para FACTOR_PRONOSTICO
      - Si extracción directa falla → construye desde columnas IHQ_*
      - Soluciona PDFs con formato no estándar (biomarcadores fuera del bloque)

   ⭐ NUEVO v6.0.10: Filtrado ESTRICTO de FACTOR_PRONOSTICO
      - SOLO 4 biomarcadores (HER2, Ki-67, Estrógenos, Progesterona)
      - Si NO hay ninguno de los 4 → "NO APLICA" (no "poner lo que haya")
      - Biomarcadores de tipificación (GATA3, TTF-1, etc.) → columnas IHQ_*

   ⭐ NUEVO v6.0.9: Extractores normalizan automáticamente durante extracción:
      - Ki-67 sin "Índice de proliferación celular"
      - HER2 sin "SOBREEXPRESIÓN DE", formato "HER2"
      - Receptores sin guiones iniciales
      - DIAGNOSTICO_PRINCIPAL sin datos estudio M (GRADO, SCORE, etc.)

2. data-auditor ejecuta auditoría inteligente automáticamente (FUNC-01):
   a. Lee debug_map del caso (NO consulta BD directamente ni hace OCR repetido)
   b. Valida extracción inicial (unified_extractor)
   c. Valida campos críticos guardados en BD
   d. Aplica REGLA DE ORO #1: FACTOR_PRONOSTICO solo 4 biomarcadores (HER2, Ki-67, ER, PR)
      - Valida filtrado estricto (v6.0.10)
      - Valida que no haya biomarcadores de tipificación
      - Detecta si se usó FALLBACK desde columnas (v6.0.11)
   e. Aplica REGLA DE ORO #2: Ki-67 sin "Índice de proliferación celular" (automático)
   f. Aplica REGLA DE ORO #3: DIAGNOSTICO_COLORACION con datos estudio M (validación 3 estrategias)
   g. Aplica REGLA DE ORO #4: DIAGNOSTICO_PRINCIPAL sin datos estudio M (limpio)
   h. Valida consistencia biomarcadores: solicitados vs extraídos (búsqueda flexible con sufijos)
   i. Calcula score de validación (0-100%)
   j. Genera reporte JSON con warnings y errores
   k. Proporciona diagnóstico de causa raíz con sugerencias

3. Si score < 90% o hay campos críticos incorrectos:

   **OPCIÓN A: Corrección Automática (FUNC-02)**
   a. Usuario ejecuta: `python auditor_sistema.py IHQ250980 --corregir`
   b. data-auditor diagnostica causa raíz (archivo + línea + patrón problemático)
   c. data-auditor virtualiza corrección (simula cambio SIN modificar archivo)
   d. data-auditor muestra DIFF al usuario
   e. Usuario aprueba → data-auditor aplica cambio + backup
   f. data-auditor limpia debug_maps y reprocesa PDF completo
   g. data-auditor re-audita con FUNC-01
   h. Si score sigue < 90% → itera hasta 3 veces
   i. Genera reporte MD/JSON con resultado final

   **OPCIÓN B: Corrección con IA**
   a. lm-studio-connector sugiere correcciones IA (dry-run)
   b. Usuario revisa y aprueba correcciones
   c. lm-studio-connector aplica correcciones de alta confianza
   d. data-auditor re-valida casos afectados post-corrección

   **OPCIÓN C: Edición Manual**
   a. Usuario edita código manualmente basándose en diagnóstico
   b. data-auditor re-valida casos afectados
```

**Agentes:**
- Opción A: data-auditor FUNC-02 (automático iterativo)
- Opción B: data-auditor → lm-studio-connector → data-auditor
- Opción C: data-auditor → (Usuario) → data-auditor

---

## WORKFLOW 2: Actualización de Versión + Documentación Completa

```
1. Usuario: "Actualiza a v6.0.7 con corrección del auditor"

2. Claude pregunta detalles:
   - ¿Qué cambios tiene v6.0.7?
   - ¿Contexto de esta iteración?
   - ¿Validación técnica?

3. Claude invoca documentation-specialist-HUV:

   Acciones internas:
   a. Actualiza config/version_info.py → v6.0.7 (gestor_version.py)
   b. Actualiza README.md, CLAUDE.md (menciones de versión)
   c. Genera/Actualiza documentacion/CHANGELOG.md (ACUMULATIVO)
   d. Genera/Actualiza documentacion/BITACORA_DE_ACERCAMIENTOS.md (ACUMULATIVO)
   e. Genera documentación completa (REESCRITURA):
      - INFORME_GLOBAL_PROYECTO.md
      - README.md
      - NOTEBOOK_LM_CONSOLIDADO_TECNICO.md
      - analisis/*.md (archivos técnicos)
      - comunicados/*.md (archivos stakeholders)
   f. TERMINA

4. Claude reporta archivos actualizados con ubicación

5. FIN
```

**Agente:** documentation-specialist-HUV (usa generador_documentacion.py + gestor_version.py)

**IMPORTANTE:**
- documentation-specialist-HUV ahora maneja VERSIONADO + CHANGELOG/BITÁCORA + DOCUMENTACIÓN
- Un solo agente para todo el ciclo de documentación

---

## WORKFLOW 3: Mantenimiento Preventivo Mensual

```
1. data-auditor ejecuta auditoría inteligente en casos críticos

2. Si errores sistemáticos detectados:
   a. data-auditor identifica patrón (ej: REGLA 1 violada en múltiples casos)
   b. lm-studio-connector sugiere correcciones IA (si aplica) O Usuario edita manualmente
   c. data-auditor re-valida casos afectados

3. Usuario revisa código y refactoriza si es necesario
```

**Agentes:** data-auditor → lm-studio-connector (opcional) → data-auditor

_Nota: Health check manual con inspector_sistema.py hasta crear agente de diagnóstico._

---

## WORKFLOW 4: Corrección Automática Iterativa (FUNC-02)

**⚠️ NOTA (v6.0.8):** Este workflow describe FUNC-02 Fase 2 (modificación de código), que está **PENDIENTE de implementación**. Actualmente FUNC-02 solo corrige datos en BD (Fase 1). Ver sección al final de este workflow para comportamiento actual.

```
1. Usuario detecta caso con errores: `python auditor_sistema.py IHQ250980 --inteligente`
   Score: 66.7% (warnings en FACTOR_PRONOSTICO)

2. Usuario activa corrección automática:
   `python auditor_sistema.py IHQ250980 --corregir`

3. ITERACIÓN 1:
   a. data-auditor audita con FUNC-01 → Score 66.7%
   b. data-auditor diagnostica causa raíz:
      - Campo: FACTOR_PRONOSTICO
      - Error: "ER: POSITIVO" (falta intensidad, grado, porcentaje)
      - Archivo: medical_extractor.py
      - Línea: 560
      - Causa: Patrón normaliza a abreviatura

   c. data-auditor virtualiza corrección (SIN modificar archivo todavía):
      - Lee medical_extractor.py línea 560
      - Simula cambio: nombre_bio = 'ER' → 'RECEPTOR DE ESTRÓGENO'
      - Ejecuta extracción virtualizada
      - Resultado virtualizado: "RECEPTOR DE ESTRÓGENO: POSITIVO FUERTE 3+ (80-90%)"

   d. data-auditor muestra DIFF al usuario:
      ```diff
      ANTES (línea 560):
      -    nombre_bio = 'ER'

      DESPUÉS (propuesto):
      +    nombre_bio = 'RECEPTOR DE ESTRÓGENO'
      ```

      ```
      Resultado esperado:
      ANTES: "ER: POSITIVO"
      DESPUÉS: "RECEPTOR DE ESTRÓGENO: POSITIVO FUERTE 3+ (80-90%)"
      ```

   e. Usuario confirma: [s/n] → s

   f. data-auditor aplica cambio:
      - Backup: backups/medical_extractor_backup_20251026_165432.py
      - Modifica: medical_extractor.py línea 560
      - Valida sintaxis: python -m py_compile ✓

   g. data-auditor reprocesa caso completo:
      - Limpia: data/debug_maps/debug_map_IHQ250980_*.json (antiguos)
      - Procesa: python main.py --procesar-caso IHQ250980
      - Genera: nuevo debug_map con timestamp actual

   h. data-auditor re-audita con FUNC-01:
      - Lee nuevo debug_map
      - Valida datos_guardados (fuente de verdad)
      - Nuevo score: 100.0% ✓

4. RESULTADO:
   - Iteraciones necesarias: 1
   - Score inicial: 66.7%
   - Score final: 100.0%
   - Estado: ÉXITO
   - Cambios aplicados: 1 (medical_extractor.py:560)

5. data-auditor genera reporte final:
   - MD: herramientas_ia/resultados/correccion_IHQ250980_20251026_165500.md
   - JSON: herramientas_ia/resultados/correccion_IHQ250980_20251026_165500.json
```

**Agente:** data-auditor FUNC-02 (completamente automático e iterativo)

**Comando alternativo (modo batch sin confirmación):**
```bash
python auditor_sistema.py IHQ250980 --corregir --auto-aprobar --max-iteraciones 5
```

### COMPORTAMIENTO ACTUAL (v6.0.8 - Fase 1)

**Lo que FUNC-02 hace actualmente:**

```
1. Usuario: `python auditor_sistema.py IHQ250982 --corregir --usar-reporte-existente`

2. ITERACIÓN 1:
   a. Lee reporte JSON existente de FUNC-01 (modo optimizado)
   b. Identifica errores en BD
   c. Aplica correcciones DIRECTAMENTE en BD:
      - Crea backup: bd_backup_IHQ250982_20251026_190335.db
      - UPDATE tabla SET campo = valor_corregido WHERE caso = 'IHQ250982'
   d. Reprocesa PDF:
      - Limpia debug_maps antiguos
      - Ejecuta: unified_extractor.process_ihq_paths()
      - Genera nuevo debug_map con datos de BD corregidos
   e. Re-audita con FUNC-01

3. ITERACIÓN 2 (si score < 100%):
   - Repite hasta max_iteraciones = 3

4. RESULTADO:
   - Estado: EXITO/REQUIERE_MANUAL
   - Correcciones: Aplicadas en BD (NO en código)
   - ⚠️ Limitación: Casos futuros similares fallarán igual
```

**Diferencia clave:** Fase 1 corrige SÍNTOMAS (datos), Fase 2 corregirá CAUSA RAÍZ (código).

---

## WORKFLOW 5: Agregar Biomarcador Automáticamente (FUNC-03)

**🆕 v6.0.16 - Gestión Automática de Biomarcadores**

```
1. Usuario: "Agrega CK19 al sistema"

2. data-auditor ejecuta FUNC-03 (agregar_biomarcador):
   from herramientas_ia.auditor_sistema import AuditorSistema

   auditor = AuditorSistema()
   resultado = auditor.agregar_biomarcador('CK19', ['CK-19', 'CK 19', 'CITOQUERATINA 19'])

3. FUNC-03 modifica automáticamente 6 archivos:
   a. core/database_manager.py (CREATE TABLE + new_biomarkers list)
   b. herramientas_ia/auditor_sistema.py (BIOMARKER_ALIAS_MAP)
   c. ui.py (columnas de interfaz)
   d. core/validation_checker.py (all_biomarker_mapping)
   e. core/extractors/biomarker_extractor.py (4 lugares: patrones individuales, patrones compuestos, normalize_biomarker_name)
   f. core/unified_extractor.py (2 mapeos: línea ~491, línea ~1179)

4. FUNC-03 valida que todos los archivos se modificaron correctamente

5. FUNC-03 retorna reporte detallado:
   {
     'biomarcador': 'CK19',
     'columna_bd': 'IHQ_CK19',
     'archivos_modificados': [lista de 6-7 modificaciones],
     'errores': [],
     'estado': 'EXITOSO'
   }

6. Usuario regenera BD (OBLIGATORIO):
   rm data/huv_oncologia_NUEVO.db

7. Usuario reprocesa casos con CK19 en interfaz

8. data-auditor valida con FUNC-01 que CK19 se extrae correctamente
```

**Agentes:** data-auditor (FUNC-03 autónomo)

**Ventajas:**
- ✅ Modifica 6 archivos automáticamente (antes era manual)
- ✅ Genera variantes automáticamente si no se proporcionan
- ✅ Validación post-modificación completa
- ✅ Reportes detallados con trazabilidad
- ✅ No requiere intervención manual en código

---

## WORKFLOW 6: Corrección Completitud Automática (FUNC-05)

**🆕 v6.0.16 - Workflow Inteligente End-to-End**

```
1. Usuario procesa caso IHQ250987 → Reporte de completitud muestra: "CK19 (NO MAPEADO)"

2. Usuario ejecuta FUNC-05:
   from herramientas_ia.auditor_sistema import AuditorSistema

   auditor = AuditorSistema()
   resultado = auditor.corregir_completitud_automatica('IHQ250987')

3. FUNC-05 ejecuta workflow automático:

   Paso 1: Lee reporte más reciente
   - Busca: data/reportes_importacion/reporte_importacion_*.json
   - Encuentra último reporte generado por sistema de importación

   Paso 2: Busca caso IHQ250987 en sección 'incompletos'
   - Detecta: biomarcadores_faltantes = ['CK19 (NO MAPEADO)']
   - Parsea: CK19 (elimina "(NO MAPEADO)")

   Paso 3: Agrega cada biomarcador detectado
   - Ejecuta FUNC-03 para CK19
   - Modifica automáticamente 6 archivos
   - Valida modificaciones

   Paso 4: Indica pasos para reprocesar
   - Muestra: "rm data/huv_oncologia_NUEVO.db"
   - Muestra: "python ui.py → reprocesar PDF IHQ250987"

   Paso 5: Guía para validación final
   - Después de reprocesar: ejecutar FUNC-01
   - Verificar completitud = 100%

4. FUNC-05 retorna reporte completo:
   {
     'caso': 'IHQ250987',
     'paso_1_reporte_leido': True,
     'paso_2_biomarcadores_detectados': ['CK19'],
     'paso_3_biomarcadores_agregados': {'CK19': 'EXITOSO'},
     'paso_4_reprocesado': 'PENDIENTE_REGENERAR_BD',
     'paso_5_auditado': 'PENDIENTE_REGENERAR_BD',
     'estado': 'FASE_1_EXITOSA_PENDIENTE_BD',
     'errores': []
   }

5. Usuario completa pasos manuales:
   a. rm data/huv_oncologia_NUEVO.db
   b. python ui.py
   c. Reprocesar PDF IHQ250987
   d. Verificar completitud = 100%
```

**Agentes:** data-auditor (FUNC-05 autónomo)

**Ventajas:**
- ✅ Detecta automáticamente biomarcadores "NO MAPEADO"
- ✅ Agrega TODOS los biomarcadores faltantes en un solo comando
- ✅ Workflow completo desde reporte → corrección → validación
- ✅ Reportes detallados con estado de cada paso
- ✅ Maneja múltiples estados (CASO_COMPLETO, SIN_BIOMARCADORES_FALTANTES, etc.)

---

## WORKFLOW 7: Búsqueda y Análisis de Casos Similares

```
1. Usuario: "Busca casos similares a IHQ250988 para comparar"

2. data-auditor busca caso de referencia: --buscar IHQ250988 (gestor_base_datos.py)

3. data-auditor identifica características:
   - Órgano
   - Género
   - Edad
   - Biomarcadores

4. data-auditor ejecuta búsqueda avanzada con criterios similares

5. data-auditor muestra casos similares encontrados

6. Usuario solicita estadísticas de biomarcadores en esos casos

7. data-auditor genera análisis de tendencias

8. data-auditor valida precisión de casos similares

9. data-auditor exporta resultados a JSON/Excel
```

**Agente:** data-auditor (búsqueda + análisis + validación en un solo flujo)

---

## WORKFLOW 8: Corrección IA Masiva con Validación

```
1. Usuario: "Aplica correcciones IA a los últimos 10 casos"

2. lm-studio-connector verifica que LM Studio está activo

3. data-auditor lista últimos 10 casos procesados (gestor_base_datos.py)

4. lm-studio-connector ejecuta validación en lote (dry-run primero)

5. lm-studio-connector agrupa correcciones por criticidad:
   - CRITICA: Requiere revisión manual
   - IMPORTANTE: Confianza ≥ 0.90
   - OPCIONAL: Confianza ≥ 0.85

6. Usuario revisa correcciones CRITICAS manualmente

7. lm-studio-connector aplica correcciones IMPORTANTES y OPCIONALES aprobadas

8. data-auditor valida precisión post-corrección

9. data-auditor actualiza estadísticas de completitud en BD
```

**Agentes:** lm-studio-connector → data-auditor

---

## WORKFLOW 9: Rollback de Emergencia

```
1. Usuario reporta: "El último cambio rompió la extracción de HER2"

2. core-editor identifica archivo modificado: biomarker_extractor.py

3. core-editor ejecuta rollback inmediato (restaura desde backups/)

4. data-auditor restaura backup de BD si necesario (gestor_base_datos.py)

5. core-editor reprocesa casos afectados

6. data-auditor valida que HER2 ahora se extrae correctamente

7. core-editor analiza qué causó el problema

8. core-editor sugiere solución correcta con simulación previa

9. Usuario verifica sistema restaurado
```

**Agentes:** core-editor → data-auditor

---

## WORKFLOW 10: Debugging de Comportamiento IA Anómalo

```
1. Usuario reporta: "Ki-67 siempre se extrae mal, la IA no lo corrige bien"

2. Claude invoca lm-studio-connector para diagnóstico:
   - Verifica estado servidor LM Studio
   - Verifica modelo cargado
   - Verifica latencia y tokens/segundo
   - TERMINA con estado OK/ERROR

3. Claude invoca lm-studio-connector --analizar-prompts:
   - Lee prompts actuales
   - Analiza calidad (0-10): claridad, especificidad, ejemplos
   - Detecta contradicciones
   - Genera reporte en herramientas_ia/resultados/
   - TERMINA

4. Claude muestra problemas detectados:
   - Falta de ejemplos concretos
   - Contradicciones en instrucciones
   - Scores bajos en especificidad

5. Claude pregunta: "¿Simular mejora del prompt?"

6. Usuario: "Sí, simula primero"

7. Claude invoca lm-studio-connector --simular:
   - Crea prompt mejorado (en memoria)
   - Prueba extracción con caso problemático
   - Compara ANTES vs DESPUÉS
   - Genera reporte comparativo
   - Muestra mejora detectada
   - TERMINA

8. Usuario: "Sí, aplica los cambios"

9. Claude invoca lm-studio-connector --editar-prompt --aplicar:
   - Crea backup automático en backups/prompts/
   - Aplica cambios al prompt
   - Valida sintaxis
   - Reprocesa caso de prueba
   - Genera reporte de cambios
   - TERMINA

10. Claude pregunta: "¿Actualizar versión y documentar?"

11. Usuario: "Sí, actualiza a v6.0.8"

12. Claude invoca documentation-specialist-HUV:
    - Lee reporte de cambios de lm-studio-connector
    - Actualiza VERSION_INFO a v6.0.8 (gestor_version.py)
    - Crea entrada en CHANGELOG.md
    - Actualiza README.md, CLAUDE.md
    - Genera documentación completa
    - TERMINA

13. FIN
```

**Archivos generados:**
- backups/prompts/*.txt.bak (backup)
- core/prompts/*.txt (mejorado)
- herramientas_ia/resultados/analisis_prompts_*.json
- herramientas_ia/resultados/simulacion_*.md
- herramientas_ia/resultados/cambios_prompts_*.md
- config/version_info.py (actualizado)
- documentacion/CHANGELOG.md (actualizado)
- documentacion/*.md (generados)

**Agentes:** lm-studio-connector → documentation-specialist-HUV

**IMPORTANTE:**
- lm-studio-connector diagnostica, simula y aplica cambios a prompts/IA
- SIEMPRE hace backup antes de modificar
- SIEMPRE simula antes de aplicar (dry-run)
- NO modifica extractores (responsabilidad de core-editor)

---

---

## 📋 Resumen de Agentes y Workflows

### 4 Agentes Especializados Activos

| Agente | Herramientas | Workflows donde participa |
|--------|-------------|---------------------------|
| **data-auditor** | auditor_sistema.py + gestor_base_datos.py | 1, 3, 4, 5, 6, 7 |
| **core-editor** | editor_core.py | 1, 3, 4, 7 |
| **lm-studio-connector** | gestor_ia_lm_studio.py | 1, 6, 8 |
| **documentation-specialist-HUV** | generador_documentacion.py + gestor_version.py | 2, 8 |

### Herramienta Disponible (sin agente asignado)
- **inspector_sistema.py**: Diagnóstico manual del sistema (pendiente de reasignación)

---

## ⭐ Reglas de Oro IMPLEMENTADAS en Workflows (v6.0.11)

### Durante Extracción (automático):
- **REGLA #1:** FACTOR_PRONOSTICO solo 4 biomarcadores (HER2, Ki-67, ER, PR)
  - **v6.0.10:** Filtrado ESTRICTO (NO incluye tipificación: GATA3, TTF-1, etc.)
  - **v6.0.11:** FALLBACK automático desde columnas IHQ_* si extracción directa falla
- **REGLA #2:** Normalización automática Ki-67, HER2, Receptores
- **REGLA #4:** DIAGNOSTICO_PRINCIPAL sin datos estudio M (GRADO, SCORE, etc.)

### Durante Auditoría (FUNC-01):
- **REGLA #1:** Valida que FACTOR_PRONOSTICO tenga solo 4 biomarcadores principales
  - Valida filtrado estricto (NO biomarcadores de tipificación)
  - Detecta si se usó FALLBACK desde columnas
- **REGLA #2:** Verifica normalización correcta (Ki-67, HER2, Receptores)
- **REGLA #3:** Valida DIAGNOSTICO_COLORACION con datos estudio M (3 estrategias)
- **REGLA #4:** Valida DIAGNOSTICO_PRINCIPAL limpio (sin GRADO, SCORE, NOTTINGHAM)
- **Biomarcadores:** Búsqueda flexible con sufijos (_ESTADO, _PORCENTAJE)

### Archivos Implementados:
- `medical_extractor.py` v4.2.4 → Normalización + Filtrado estricto + FALLBACK (líneas 514-525, 738-757, 1017-1015, 1145)
- `unified_extractor.py` v4.2.6 → Limpieza DIAGNOSTICO_PRINCIPAL + Integración FALLBACK (líneas 132, 577-595)
- `auditor_sistema.py` v3.0.2 → Validación robusta + Búsqueda flexible biomarcadores (líneas 710-774)

---

**Última actualización:** 2025-10-26 (NOCHE)
**Versión EVARISIS:** 6.0.11
