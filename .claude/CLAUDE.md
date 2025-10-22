# 🏥 EVARISIS - Ecosistema 6+7 Consolidado

**Sistema Inteligente de Gestión Oncológica - Hospital Universitario del Valle**

---

## 🚨 REGLA CRÍTICA #1: Claude SOLO Actúa Mediante Agentes

**PROHIBIDO TERMINANTEMENTE**:
- ❌ Crear archivos en carpeta raíz (resumen.md, cambios.md, temp_*.py, etc.)
- ❌ Crear scripts adhoc en cualquier ubicación
- ❌ Hacer cambios directos sin invocar agentes
- ❌ Generar documentación sin usar documentation-specialist
- ❌ Modificar código sin usar core-editor
- ❌ Auditar casos sin usar data-auditor

**OBLIGATORIO**:
- ✅ Claude SIEMPRE invoca agentes especializados
- ✅ Agentes crean archivos en `herramientas_ia/resultados/` únicamente
- ✅ Si NO existe agente para la tarea → Claude INFORMA al usuario
- ✅ Claude pregunta entre pasos de agentes

**Ejemplo CORRECTO**:
```
Usuario: "Audita el caso IHQ250025"
Claude: [Invoca agente data-auditor]
data-auditor:
  - Lee BD + PDF
  - Detecta error en Ki-67
  - Genera herramientas_ia/resultados/auditoria_IHQ250025_YYYYMMDD_HHMMSS.json
  - Muestra al usuario: "Ki-67 está mal. Extrajo '18' de 'índice: 18%' pero debería buscar 'Ki-67: 20%'"
  - TERMINA

Claude: "Encontré error en Ki-67. ¿Quieres que corrija el extractor?"
Usuario: "Sí"

Claude: [Invoca agente core-editor con contexto del data-auditor]
core-editor:
  - Lee reporte de data-auditor
  - Mejora patrón en biomarker_extractor.py
  - Genera herramientas_ia/resultados/cambios_YYYYMMDD_HHMMSS.md
  - TERMINA

Claude: "¿Actualizar versión del sistema?"
```

**Ejemplo INCORRECTO (NUNCA HACER)**:
```
Usuario: "Audita el caso IHQ250025"
Claude: [Lee BD directamente con Bash/Read]
Claude: [Crea resumen_auditoria.md en carpeta raíz]  ❌ MAL
Claude: [Crea temp_fix_ki67.py para corregir]  ❌ MAL
Claude: [Ejecuta script temporal]  ❌ MAL
```

**Si NO existe agente para la tarea**:
```
Usuario: "Genera reporte de tendencias de cáncer de mama 2020-2025"
Claude: "Actualmente no tengo un agente especializado para generar reportes de tendencias estadísticas.
Puedo hacerlo manualmente, pero sería mejor crear un agente 'trend-analyzer' que:
- Analice datos históricos
- Genere gráficos
- Exporte reportes en herramientas_ia/resultados/

¿Quieres que proceda manualmente esta vez, o prefieres que documentemos la necesidad de este agente?"
```

---

## 📊 Arquitectura del Ecosistema

### 7 HERRAMIENTAS ESPECIALIZADAS (Core Tools)
1. **auditor_sistema.py** (934 líneas) - Validación completa de precisión: biomarcadores + campos críticos (ORGANO, DIAGNOSTICO, FACTOR_PRONOSTICO)
2. **gestor_base_datos.py** (1074 líneas) - Gestión y consultas de BD
3. **inspector_sistema.py** (1423 líneas) - Diagnóstico y salud del sistema
4. **editor_core.py** (1234 líneas) - Edición inteligente de código y generación de reportes
5. **gestor_version.py** (~950 líneas) - Gestión de versionado + CHANGELOG + BITÁCORA (ACUMULATIVOS)
6. **generador_documentacion.py** (~800 líneas) - Documentación profesional (lee CHANGELOG/BITÁCORA, NO los genera)
7. **gestor_ia_lm_studio.py** (~1450 líneas) - Gestión completa de LM Studio + IA (CONSOLIDADO 2→1)

### 7 AGENTES ESPECIALIZADOS
1. **data-auditor** → Usa auditor_sistema.py - Detecta falsa completitud, valida TODOS los campos críticos
2. **database-manager** → Usa gestor_base_datos.py
3. **system-diagnostician** → Usa inspector_sistema.py
4. **core-editor** → Usa editor_core.py
5. **lm-studio-connector** → Usa gestor_ia_lm_studio.py (antes: detectar_lm_studio.py + validador_ia.py)
6. **version-manager** → Usa gestor_version.py
7. **documentation-specialist-HUV** → Usa generador_documentacion.py

---

## 🎯 Matriz de Responsabilidades

| Necesidad del Usuario | Agente Responsable | Herramienta(s) Usada(s) |
|------------------------|-------------------|------------------------|
| **AUDITORÍA Y VALIDACIÓN** | | |
| "Valida el caso IHQ250025" | data-auditor | auditor_sistema.py |
| "Audita todos los casos" | data-auditor | auditor_sistema.py --todos |
| "¿Por qué el ORGANO está mal en IHQ251029?" | data-auditor | auditor_sistema.py IHQ251029 --nivel profundo |
| "Valida que el diagnóstico esté correcto" | data-auditor | auditor_sistema.py [CASO] --buscar "diagnóstico" |
| "Verifica si el factor pronóstico está completo" | data-auditor | auditor_sistema.py [CASO] --buscar "grado\|invasión" |
| "Detecta casos con falsa completitud" | data-auditor | auditor_sistema.py --todos --nivel profundo |
| "¿Qué dice el PDF sobre Ki-67?" | data-auditor | auditor_sistema.py [CASO] --buscar "Ki-67" |
| "Lee el texto completo del PDF del caso X" | data-auditor | auditor_sistema.py [CASO] --leer-ocr |
| **GESTIÓN DE BASE DE DATOS** | | |
| "Busca casos de mama en mujeres 40-60" | database-manager | gestor_base_datos.py |
| "Muéstrame estadísticas de la BD" | database-manager | gestor_base_datos.py --stats |
| **DIAGNÓSTICO DE SISTEMA** | | |
| "¿El sistema está funcionando bien?" | system-diagnostician | inspector_sistema.py |
| "Analiza la complejidad del código" | system-diagnostician | inspector_sistema.py --complejidad |
| **EDICIÓN DE CÓDIGO** | | |
| "Mejora la extracción de Ki-67" | core-editor | editor_core.py |
| "Agrega el biomarcador BCL2" | core-editor | editor_core.py --agregar-biomarcador BCL2 |
| "Corrige el extractor de ORGANO" | core-editor | editor_core.py --editar-extractor ORGANO --simular |
| **INTELIGENCIA ARTIFICIAL** | | |
| "¿Está listo LM Studio?" | lm-studio-connector | gestor_ia_lm_studio.py --estado |
| "Valida caso IHQ250025 con IA" | lm-studio-connector | gestor_ia_lm_studio.py --validar-caso IHQ250025 --dry-run |
| "Aplica correcciones IA a IHQ250025" | lm-studio-connector | gestor_ia_lm_studio.py --validar-caso IHQ250025 |
| "Valida últimos 50 casos con IA" | lm-studio-connector | gestor_ia_lm_studio.py --validar-lote --ultimos 50 |
| "Analiza calidad de los prompts" | lm-studio-connector | gestor_ia_lm_studio.py --analizar-prompts |
| "Simula extracción de Ki-67 de este texto" | lm-studio-connector | gestor_ia_lm_studio.py --simular "texto" --biomarcador Ki-67 |
| "Mejora el prompt de biomarcadores" | lm-studio-connector | gestor_ia_lm_studio.py --editar-prompt system_prompt_comun.txt --aplicar |
| **VERSIONADO** | | |
| "Cambia la versión a 6.0.0" | version-manager | gestor_version.py --actualizar 6.0.0 |
| "Actualiza CHANGELOG con v6.0.0" | version-manager | gestor_version.py --generar-changelog |
| "Añade iteración a BITÁCORA" | version-manager | gestor_version.py --generar-bitacora |
| "Copia CHANGELOG desde LEGACY" | version-manager | gestor_version.py --copiar-legacy changelog |
| "¿Qué versión tenemos?" | version-manager | gestor_version.py --actual |
| **DOCUMENTACIÓN** | | |
| "Genera documentación completa del sistema" | documentation-specialist-HUV | generador_documentacion.py --completo |
| "Genera comunicados para stakeholders" | documentation-specialist-HUV | generador_documentacion.py --generar comunicacion |
| "Valida que CHANGELOG y BITÁCORA existan" | documentation-specialist-HUV | generador_documentacion.py --validar |

---

## 🔍 CAPACIDADES CLAVE DEL AGENTE DATA-AUDITOR

El agente **data-auditor** realiza auditoría COMPLETA de casos oncológicos, validando NO SOLO biomarcadores, sino TODOS los campos críticos del sistema.

### ✅ QUÉ VALIDA EL AGENTE:

#### 1. **BIOMARCADORES (IHQ_*)**
- Compara cada biomarcador mencionado en el PDF contra la BD
- Detecta biomarcadores vacíos que deberían tener valores
- Detecta confusiones (ej: CD5 vs CD56)
- Valida formatos no estándar (ej: "Sinaptofisina+", "Cromogranina A+")

#### 2. **IHQ_ORGANO** (validación crítica)
- Verifica que contenga un órgano válido
- Detecta si contiene diagnóstico u otro texto erróneo
- Ejemplo de error: ORGANO = "LOS HALLAZGOS MORFOLOGICOS..." (debería ser "MESENTERIO")

#### 3. **DIAGNOSTICO_PRINCIPAL** (validación crítica)
- Verifica que el diagnóstico sea legible y completo
- Detecta fragmentos incorrectos
- Ejemplo de error: DIAGNOSTICO = "67 DEL 2%" (debería ser "TUMOR NEUROENDOCRINO BIEN DIFERENCIADO, GRADO 1")

#### 4. **FACTOR_PRONOSTICO** (validación de completitud)
- Verifica que incluya TODOS los factores pronósticos:
  - Grado de diferenciación (BIEN DIFERENCIADO, MODERADAMENTE, etc.)
  - Grado tumoral (GRADO 1, 2, 3)
  - Invasión linfovascular (NEGATIVO/POSITIVO)
  - Índice Ki-67 (si aplica)
- Detecta si solo tiene Ki-67 (incompleto)
- Ejemplo: "Ki-67 DEL 2%" está incompleto, falta grado e invasión

#### 5. **IHQ_ESTUDIOS_SOLICITADOS** (validación de completitud)
- Verifica que capturó TODOS los biomarcadores solicitados en el PDF
- Calcula completitud: X% (Y/Z biomarcadores capturados)
- Detecta biomarcadores omitidos

### 🚨 DETECCIÓN DE "FALSA COMPLETITUD"

El agente detecta casos donde:
- Sistema reporta: **100% completo** ✅
- Realidad: Campos llenos con datos **INCORRECTOS** ❌

**Ejemplo real (caso IHQ251029)**:
```
Sistema reporta: 100% completo
Precisión REAL: 11.1% (1/9 campos correctos)

Errores detectados:
- ORGANO: Contiene diagnóstico en lugar de "MESENTERIO"
- DIAGNOSTICO: "67 DEL 2%" (fragmento ilegible)
- FACTOR_PRONOSTICO: Solo Ki-67 (falta grado e invasión)
- 4 biomarcadores vacíos (CD56, Sinaptofisina, Cromogranina A, CKAE1/AE3)
- 1 biomarcador incorrecto (CD5="6", confusión con CD56)
```

### 📋 PROTOCOLO DE AUDITORÍA COMPLETA

El agente ejecuta automáticamente:

**PASO 1:** Auditoría principal con JSON (métricas)
**PASO 2:** Lectura completa del OCR (evidencia del PDF)
**PASO 3:** Búsqueda de cada biomarcador específico
**PASO 3B:** Búsqueda de campos críticos (órgano, diagnóstico, grado, invasión)
**PASO 4:** Cálculo de precisión REAL vs reportada
**PASO 5:** Presentación de resumen completo con:
- Comparación BD vs PDF (lado a lado)
- Ubicación exacta en el PDF (número de línea)
- Evidencia textual completa
- Clasificación de errores por severidad (CRÍTICO / IMPORTANTE)
- Sugerencias de corrección específicas (archivo + función + regex + comando)

### 💡 SUGERENCIAS DE CORRECCIÓN ESPECÍFICAS

Para CADA error detectado, el agente proporciona:
```
ERROR: Confusión CD5/CD56
├─ Archivo: core/extractors/biomarker_extractor.py
├─ Función: extract_cd5() y extract_cd56()
├─ Causa: Patrón regex captura "CD56" como "CD5"
├─ Solución regex: patron_cd5 = r'(?<!6)CD[- ]?5(?![0-9])'
└─ Comando: python herramientas_ia/editor_core.py --editar-extractor CD5 --simular
```

### 🎯 USO RECOMENDADO

**Auditar caso individual (completo):**
```
Usuario: "Audita el caso IHQ251029"
Claude: [Invoca data-auditor]
→ Ejecuta protocolo completo (5 pasos)
→ Valida biomarcadores + ORGANO + DIAGNOSTICO + FACTOR_PRONOSTICO
→ Calcula precisión real
→ Detecta falsa completitud
→ Proporciona sugerencias específicas
```

**Validar campo específico:**
```
Usuario: "¿Por qué el ORGANO está mal en IHQ251029?"
Claude: [Invoca data-auditor con --buscar "órgano"]
→ Muestra texto del PDF donde menciona el órgano
→ Compara con valor en BD
→ Explica discrepancia con evidencia
```

**Detectar casos con falsa completitud:**
```
Usuario: "Detecta casos que parecen completos pero tienen errores"
Claude: [Invoca data-auditor --todos --nivel profundo]
→ Audita todos los casos
→ Identifica casos con precisión reportada > precisión real
→ Lista casos con "falsa completitud"
```

---

## 🔄 7 Workflows Maestros

### WORKFLOW 1: Procesamiento Completo de Caso Nuevo
```
1. Usuario procesa PDF → Sistema EVARISIS extrae datos
2. system-diagnostician verifica salud del sistema proactivamente
3. data-auditor ejecuta auditoría completa automáticamente:
   a. Valida TODOS los biomarcadores mencionados en PDF
   b. Valida IHQ_ORGANO (¿es órgano correcto o texto erróneo?)
   c. Valida DIAGNOSTICO_PRINCIPAL (¿es legible y correcto?)
   d. Valida FACTOR_PRONOSTICO (¿está completo o solo tiene Ki-67?)
   e. Valida IHQ_ESTUDIOS_SOLICITADOS (¿capturó todos los biomarcadores?)
   f. Calcula precisión REAL vs precisión reportada
   g. Detecta "falsa completitud" si el sistema reporta 100% pero hay errores
4. Si precisión REAL < 90% o hay campos críticos incorrectos:
   a. data-auditor identifica campos problemáticos con evidencia del PDF
   b. data-auditor proporciona sugerencias de corrección (archivo + función + regex)
   c. lm-studio-connector sugiere correcciones IA (dry-run)
   d. Usuario revisa errores críticos y aprueba correcciones
   e. lm-studio-connector aplica correcciones de alta confianza
   f. core-editor corrige extractores si hay patrones sistemáticos
5. data-auditor re-valida precisión post-corrección (todos los campos)
6. database-manager almacena caso validado
```

**Agentes involucrados**: system-diagnostician → data-auditor → lm-studio-connector → core-editor → database-manager

**IMPORTANTE**: data-auditor ahora detecta errores en campos NO-biomarcadores que antes pasaban desapercibidos.

---

### WORKFLOW 2: Actualización de Versión + Documentación Completa (CONSOLIDADO)
```
1. Usuario solicita: "Actualiza a v6.0.0 con nuevos biomarcadores y genera documentación"

2. Claude pregunta detalles:
   "¿Qué cambios tiene v6.0.0?"
   Usuario: "BCL2 agregado, SOX11 agregado, MYC agregado"

   "¿Contexto de esta iteración?"
   Usuario: "Expansión de biomarcadores oncológicos"

   "¿Validación técnica?"
   Usuario: "Tests: 95% aprobados"

   "¿Validación médica?"
   Usuario: "Dr. Bayona validó BCL2 y SOX11"

3. Claude invoca: version-manager

   version-manager ejecuta:
   python herramientas_ia/gestor_version.py --actualizar 5.4.0 \
     --nombre "Nuevos Biomarcadores" \
     --cambios "BCL2 agregado" "SOX11 agregado" "MYC agregado" \
     --generar-changelog \
     --generar-bitacora \
     --contexto-iteracion "Expansión de biomarcadores oncológicos" \
     --validacion-tecnica "Tests: 95% aprobados" \
     --validacion-medica "Dr. Bayona validó BCL2 y SOX11"

   Acciones internas:
   a. Actualiza config/version_info.py → v6.0.0
   b. Actualiza README.md, CLAUDE.md (menciones de versión)
   c. Genera/Actualiza documentacion/CHANGELOG.md:
      - Si NO existe: Copia desde LEGACY/v6.0.0/documentacion/CHANGELOG.md
      - Añade nueva entrada al inicio:
        ## [5.4.0] - 2025-10-20
        ### Added
        - BCL2 agregado
        - SOX11 agregado
        - MYC agregado
      - PRESERVA todo el historial anterior (ACUMULATIVO)

   d. Genera/Actualiza documentacion/BITACORA_DE_ACERCAMIENTOS.md:
      - Si NO existe: Copia desde LEGACY/v6.0.0/documentacion/BITACORA_DE_ACERCAMIENTOS.md
      - Añade nueva iteración al inicio:
        ## Iteración N — Nuevos Biomarcadores (20/10/2025)
        ### Contexto: Expansión de biomarcadores oncológicos
        ### Cambios: BCL2, SOX11, MYC
        ### Validación técnica: Tests: 95% aprobados
        ### Validación médica: Dr. Bayona validó BCL2 y SOX11
      - PRESERVA todas las iteraciones anteriores (ACUMULATIVO)

   e. TERMINA

4. Claude reporta:
   "✅ Versión actualizada a 5.4.0

   📦 ARCHIVOS ACTUALIZADOS:
   - config/version_info.py → v6.0.0
   - README.md, CLAUDE.md (menciones)
   - documentacion/CHANGELOG.md (acumulativo - entrada v6.0.0 añadida)
   - documentacion/BITACORA_DE_ACERCAMIENTOS.md (acumulativo - iteración nueva añadida)

   ¿Quieres generar la documentación completa de v6.0.0?"

5. Usuario responde: "Sí"

6. Claude invoca: documentation-specialist-HUV

   documentation-specialist-HUV ejecuta:
   python herramientas_ia/generador_documentacion.py --completo

   Acciones internas:
   a. Verifica que documentacion/CHANGELOG.md existe ✅
   b. Verifica que documentacion/BITACORA_DE_ACERCAMIENTOS.md existe ✅
   c. Lee config/version_info.py → v6.0.0
   d. Lee documentacion/CHANGELOG.md → Extrae cambios de v6.0.0
   e. Lee documentacion/BITACORA_DE_ACERCAMIENTOS.md → Extrae contexto

   f. Genera (REESCRITURA COMPLETA):
      ✅ documentacion/INFORME_GLOBAL_PROYECTO.md (con cambios de v6.0.0)
      ✅ documentacion/README.md
      ✅ documentacion/NOTEBOOK_LM_CONSOLIDADO_TECNICO.md
      ✅ documentacion/analisis/ (7 archivos técnicos modulares)
      ✅ documentacion/comunicados/ (4 comunicados por stakeholder)
      ✅ documentacion/comunicados_ia/ (4 formatos NotebookLM)

   g. NO TOCA:
      ❌ documentacion/CHANGELOG.md (ya lo generó version-manager)
      ❌ documentacion/BITACORA_DE_ACERCAMIENTOS.md (ya lo generó version-manager)

   h. TERMINA

7. Claude reporta resultado final:
   "✅ PROCESO COMPLETO

   📦 VERSIONADO (version-manager):
   - Versión: 6.0.0 → 5.4.0
   - CHANGELOG: Entrada v6.0.0 añadida (acumulativo)
   - BITÁCORA: Iteración nueva añadida (acumulativo)

   📚 DOCUMENTACIÓN (documentation-specialist-HUV):
   - INFORME_GLOBAL_PROYECTO.md (actualizado)
   - README.md (actualizado)
   - 7 análisis técnicos modulares (actualizados)
   - 4 comunicados stakeholders (actualizados)
   - 4 formatos NotebookLM (actualizados)

   📁 Ubicación: documentacion/

   Todo listo para v6.0.0 'Nuevos Biomarcadores'"

8. FIN - Archivos generados/actualizados:
   Por version-manager:
   - config/version_info.py
   - README.md, CLAUDE.md
   - documentacion/CHANGELOG.md (ACUMULATIVO)
   - documentacion/BITACORA_DE_ACERCAMIENTOS.md (ACUMULATIVO)

   Por documentation-specialist-HUV:
   - documentacion/INFORME_GLOBAL_PROYECTO.md
   - documentacion/README.md
   - documentacion/NOTEBOOK_LM_CONSOLIDADO_TECNICO.md
   - documentacion/analisis/*.md (7 archivos)
   - documentacion/comunicados/*.md (4 archivos)
   - documentacion/comunicados_ia/*.md (4 archivos)
```

**Agentes involucrados**: version-manager → documentation-specialist-HUV

**IMPORTANTE**:
- version-manager genera CHANGELOG y BITÁCORA (acumulativos)
- documentation-specialist-HUV genera RESTO de documentación (reescritura)
- Claude NO crea ningún archivo directamente

---

### WORKFLOW 3: Mantenimiento Preventivo Mensual
```
1. system-diagnostician ejecuta health check completo
2. system-diagnostician analiza complejidad ciclomática
3. system-diagnostician detecta code smells
4. Si CC > 10 en funciones críticas:
   a. core-editor sugiere refactorizaciones
   b. core-editor versiona archivos
   c. core-editor aplica refactorización
   d. system-diagnostician valida que no hay breaking changes
5. database-manager crea backup de BD
6. database-manager optimiza BD (VACUUM + ANALYZE)
7. data-auditor ejecuta auditoría completa de todos los casos
8. data-auditor analiza tendencias de errores
9. Si errores sistemáticos detectados:
   a. core-editor corrige extractores problemáticos
```

**Agentes involucrados**: system-diagnostician → core-editor → database-manager → data-auditor

---

### WORKFLOW 4: Agregar Nuevo Biomarcador al Sistema
```
1. Usuario solicita: "Agrega BCL2 al sistema"
2. system-diagnostician verifica salud del sistema
3. database-manager verifica que columna IHQ_BCL2 no existe
4. core-editor ejecuta: --agregar-biomarcador BCL2 --variantes "BCL-2,BCL 2"
   Esto automáticamente:
   a. Agrega función extract_bcl2() a biomarker_extractor.py
   b. Agrega entrada al MAPEO_BIOMARCADORES
   c. Migra schema BD (nueva columna IHQ_BCL2)
   d. Genera test unitario
5. core-editor valida sintaxis Python
6. system-diagnostician verifica que no hay breaking changes
7. database-manager confirma que columna IHQ_BCL2 existe
8. Usuario procesa casos con BCL2
9. data-auditor valida que BCL2 se extrae correctamente
```

**Agentes involucrados**: system-diagnostician → database-manager → core-editor → data-auditor

---

### WORKFLOW 5: Búsqueda y Análisis de Casos Similares
```
1. Usuario solicita: "Busca casos similares a IHQ250988 para comparar"
2. database-manager busca caso de referencia: --buscar IHQ250988
3. database-manager identifica características: Órgano, Género, Edad, Biomarcadores
4. database-manager ejecuta búsqueda avanzada con criterios similares
5. database-manager muestra casos similares encontrados
6. Usuario solicita estadísticas de biomarcadores en esos casos
7. database-manager genera análisis de tendencias
8. data-auditor valida precisión de casos similares
9. database-manager exporta resultados a JSON/Excel
```

**Agentes involucrados**: database-manager → data-auditor

---

### WORKFLOW 6: Corrección IA Masiva con Validación
```
1. Usuario solicita: "Aplica correcciones IA a los últimos 10 casos"
2. lm-studio-connector verifica que LM Studio está activo
3. database-manager lista últimos 10 casos procesados
4. lm-studio-connector ejecuta validación en lote (dry-run primero)
5. lm-studio-connector agrupa correcciones por criticidad:
   - CRITICA: Requiere revisión manual
   - IMPORTANTE: Confianza ≥ 0.90
   - OPCIONAL: Confianza ≥ 0.85
6. Usuario revisa correcciones CRITICAS manualmente
7. lm-studio-connector aplica correcciones IMPORTANTES y OPCIONALES aprobadas
8. data-auditor valida precisión post-corrección
9. database-manager actualiza estadísticas de completitud
10. system-diagnostician verifica integridad de BD
```

**Agentes involucrados**: lm-studio-connector → database-manager → data-auditor → system-diagnostician

---

### WORKFLOW 7: Rollback de Emergencia
```
1. Usuario reporta: "El último cambio rompió la extracción de HER2"
2. system-diagnostician ejecuta diagnóstico de componentes
3. core-editor identifica archivo modificado: biomarker_extractor.py
4. core-editor ejecuta rollback inmediato
5. database-manager restaura backup de BD (si necesario)
6. core-editor reprocesa casos afectados
7. data-auditor valida que HER2 ahora se extrae correctamente
8. system-diagnostician confirma sistema restaurado
9. core-editor analiza qué causó el problema
10. core-editor sugiere solución correcta con simulación previa
```

**Agentes involucrados**: system-diagnostician → core-editor → database-manager → data-auditor

---

### WORKFLOW 8: Debugging de Comportamiento IA Anómalo
```
1. Usuario reporta: "Ki-67 siempre se extrae mal, la IA no lo corrige bien"

2. Claude invoca: lm-studio-connector para diagnóstico
   lm-studio-connector ejecuta:
   python herramientas_ia/gestor_ia_lm_studio.py --estado

   Verifica:
   a. Estado del servidor LM Studio ✅ Activo en http://localhost:1234
   b. Modelo cargado: gpt-oss-20b (MXFP4.gguf) ✅
   c. Latencia promedio: 450ms ✅
   d. Tokens/segundo: 18.5 ✅
   e. TERMINA con estado OK

3. Claude invoca: lm-studio-connector --analizar-prompts
   lm-studio-connector ejecuta:
   a. Lee core/prompts/system_prompt_comun.txt
   b. Lee core/prompts/system_prompt_parcial.txt
   c. Analiza calidad de prompts (0-10):
      - Claridad: 7/10
      - Especificidad: 6/10 ⚠️
      - Ejemplos: 4/10 ⚠️ (Ki-67 no tiene ejemplos concretos)
      - Contradicciones: DETECTADAS ⚠️
        * Línea 45: "Extrae Ki-67 del diagnóstico"
        * Línea 89: "Busca Ki-67 en descripción microscópica"
        * CONFLICTO: ¿Cuál priorizar?
   d. Genera reporte detallado en:
      herramientas_ia/resultados/analisis_prompts_20251020_160000.json
   e. TERMINA

4. Claude muestra al usuario:
   "🔍 DIAGNÓSTICO COMPLETADO

   ⚠️ PROBLEMAS DETECTADOS en prompts:
   1. Ki-67 no tiene ejemplos concretos de extracción
   2. CONTRADICCIÓN detectada:
      - Línea 45 dice buscar en 'diagnóstico'
      - Línea 89 dice buscar en 'descripción microscópica'

   📊 Scores de calidad:
   - Claridad: 7/10
   - Especificidad: 6/10 ⚠️
   - Ejemplos: 4/10 ⚠️

   ¿Quieres que simule una mejora del prompt antes de aplicarla?"

5. Usuario responde: "Sí, simula primero"

6. Claude invoca: lm-studio-connector --simular
   lm-studio-connector ejecuta:
   a. Crea prompt mejorado (en memoria, no guardado):
      - Elimina contradicción: prioriza "descripción microscópica"
      - Agrega ejemplos concretos de Ki-67
      - Mejora especificidad con patrones regex sugeridos

   b. Prueba extracción con caso problemático IHQ250025:
      ANTES (prompt actual):
      - Ki-67 extraído: "18%" (INCORRECTO - de texto irrelevante)

      DESPUÉS (prompt mejorado):
      - Ki-67 extraído: "20%" (CORRECTO - de "Ki-67: 20%" en desc. microscópica)

   c. Genera reporte comparativo en:
      herramientas_ia/resultados/simulacion_ki67_20251020_160100.md

   d. Muestra al usuario:
      "✅ SIMULACIÓN EXITOSA

      📈 Mejora detectada:
      - Caso IHQ250025: 18% → 20% ✓
      - Confianza: 0.95

      📝 Cambios propuestos:
      1. Línea 45: Eliminar referencia a 'diagnóstico'
      2. Línea 89: Priorizar 'descripción microscópica'
      3. Agregar ejemplo: 'Ki-67: X%' o 'índice proliferativo Ki-67: X%'

      ¿Aplicar cambios al prompt?"

   e. TERMINA

7. Usuario responde: "Sí, aplica los cambios"

8. Claude invoca: lm-studio-connector --editar-prompt system_prompt_comun.txt --aplicar
   lm-studio-connector ejecuta:
   a. Crea backup automático en:
      backups/prompts/system_prompt_comun_20251020_160200.txt.bak

   b. Aplica cambios al prompt:
      - Elimina línea 45 (contradicción)
      - Mejora línea 89 con ejemplos concretos
      - Agrega sección de ejemplos Ki-67

   c. Valida sintaxis del prompt modificado

   d. Reprocesa caso IHQ250025 con IA:
      - Ki-67 ahora: "20%" ✓ (correcto)

   e. Genera reporte en:
      herramientas_ia/resultados/cambios_prompts_20251020_160300.md

   f. TERMINA

9. Claude muestra:
   "✅ CAMBIOS APLICADOS EXITOSAMENTE

   💾 Backup creado: backups/prompts/system_prompt_comun_20251020_160200.txt.bak
   ✏️ Prompt mejorado: core/prompts/system_prompt_comun.txt
   🔄 IHQ250025 reprocesado: Ki-67 = 20% ✓
   📝 Reporte: herramientas_ia/resultados/cambios_prompts_20251020_160300.md

   ¿Quieres actualizar la versión del sistema?"

10. Usuario responde: "Sí, actualiza a 5.4.1"

11. Claude invoca: version-manager --actualizar 5.4.1 --nombre "Mejora Prompts Ki-67"
    version-manager ejecuta:
    a. Lee herramientas_ia/resultados/cambios_prompts_20251020_160300.md
    b. Actualiza config/version_info.py a 5.4.1
    c. Crea entrada en documentacion/CHANGELOG.md:
       ## [5.4.1] - 2025-10-20
       ### Fixed
       - Eliminada contradicción en prompts sobre ubicación de Ki-67
       - Agregados ejemplos concretos de extracción Ki-67
       - Mejorada especificidad de prompts IA (6→8/10)
    d. Actualiza README.md, CLAUDE.md con versión 5.4.1
    e. TERMINA

12. Claude pregunta: "¿Quieres generar documentación técnica de este cambio?"

13. Usuario responde: "No, gracias"

14. FIN - Archivos generados/modificados:
    - backups/prompts/system_prompt_comun_20251020_160200.txt.bak (backup)
    - core/prompts/system_prompt_comun.txt (mejorado)
    - herramientas_ia/resultados/analisis_prompts_20251020_160000.json (diagnóstico)
    - herramientas_ia/resultados/simulacion_ki67_20251020_160100.md (simulación)
    - herramientas_ia/resultados/cambios_prompts_20251020_160300.md (cambios aplicados)
    - config/version_info.py (v5.4.1)
    - documentacion/CHANGELOG.md (entrada v5.4.1)
```

**Agentes involucrados**: lm-studio-connector → version-manager

**IMPORTANTE**:
- lm-studio-connector diagnostica, simula y aplica cambios a prompts/IA
- SIEMPRE hace backup en `backups/` antes de modificar
- SIEMPRE simula antes de aplicar (dry-run)
- Genera reportes técnicos detallados en `herramientas_ia/resultados/`
- NO modifica extractores (eso es responsabilidad de core-editor)

---

## 🔗 Reglas de Coordinación entre Agentes

### Regla 1: Validación Obligatoria
- **core-editor** DEBE notificar a **data-auditor** después de modificar extractores
- **lm-studio-connector** DEBE notificar a **data-auditor** después de aplicar correcciones

### Regla 2: Health Check Proactivo
- **system-diagnostician** DEBE verificar salud antes de:
  - Procesamiento de lotes grandes (>10 casos)
  - Modificaciones críticas por **core-editor**
  - Operaciones masivas de BD por **database-manager**

### Regla 3: Backup Obligatorio
- **database-manager** DEBE crear backup antes de:
  - Migraciones de schema por **core-editor**
  - Limpieza de duplicados
  - Optimización VACUUM
- **lm-studio-connector** DEBE crear backup en `backups/` antes de:
  - Editar prompts (core/prompts/*.txt)
  - Modificar llm_client.py
  - Modificar procesamiento_con_ia.py
- **core-editor** DEBE crear backup en `backups/` antes de:
  - Modificar extractors
  - Migrar schema BD
  - Refactorizar funciones críticas

### Regla 4: Dry-Run Primero
- **lm-studio-connector** SIEMPRE ejecuta dry-run antes de aplicar correcciones
- **core-editor** SIEMPRE simula cambios antes de aplicar
- **database-manager** SIEMPRE simula limpieza de duplicados antes de aplicar

### Regla 5: Generación de Reportes Obligatoria
- **core-editor** SIEMPRE genera reporte MD después de modificar código
- **lm-studio-connector** SIEMPRE genera reporte MD después de:
  - Editar prompts
  - Validar casos con IA
  - Analizar calidad de prompts
  - Realizar experimentos sandbox
- **version-manager** lee reportes para generar CHANGELOG
- Reportes almacenados en `herramientas_ia/resultados/`

### Regla 6: Separación de Responsabilidades IA vs Extractores
- **lm-studio-connector** SOLO modifica archivos relacionados con IA:
  - core/prompts/*.txt
  - core/llm_client.py
  - core/procesamiento_con_ia.py
  - core/auditoria_ia.py
- **core-editor** SOLO modifica archivos relacionados con extracción:
  - core/extractors/*.py
  - core/unified_extractor.py
  - core/ihq_processor.py
  - Schema de BD
- **PROHIBIDO**: lm-studio-connector NO puede modificar extractores
- **PROHIBIDO**: core-editor NO puede modificar prompts/llm_client

---

## 🚨 Anti-Patrones (NUNCA HACER)

### ❌ Anti-Patrón 1: Modificar sin Validar
```
INCORRECTO:
core-editor modifica extractor → Usuario continúa procesando casos

CORRECTO:
core-editor modifica extractor → data-auditor valida con caso de prueba → Si OK, continuar
```

### ❌ Anti-Patrón 2: Aplicar IA sin Dry-Run
```
INCORRECTO:
lm-studio-connector aplica correcciones directamente

CORRECTO:
lm-studio-connector dry-run → Usuario revisa → Usuario aprueba → Aplicar
```

### ❌ Anti-Patrón 3: Migrar Schema sin Backup
```
INCORRECTO:
core-editor migra schema directamente

CORRECTO:
database-manager crea backup → core-editor migra schema → Verificar
```

### ❌ Anti-Patrón 4: Editar Múltiples Extractores Simultáneamente
```
INCORRECTO:
core-editor modifica Ki-67, HER2, ER simultáneamente

CORRECTO:
core-editor modifica Ki-67 → Valida → Modifica HER2 → Valida → Modifica ER
```

### ❌ Anti-Patrón 5: Ignorar Health Check
```
INCORRECTO:
Usuario procesa 50 casos sin verificar sistema

CORRECTO:
system-diagnostician health check → Si OK, procesar 50 casos
```

### ❌ Anti-Patrón 6: CREAR SCRIPTS ADHOC (PROHIBIDO)
```
INCORRECTO:
Claude crea script temporal temp_fix_ki67.py para resolver problema

CORRECTO:
Claude usa agente core-editor para modificar extractor existente
```

**REGLA CRÍTICA**: Claude NUNCA debe crear scripts adhoc, temporales o de utilidad.
SIEMPRE debe usar los agentes especializados que tienen todas las funcionalidades necesarias.

Si Claude detecta que NO existe un agente para una funcionalidad necesaria, debe:
1. Informar al usuario de la carencia
2. Sugerir crear un nuevo agente especializado
3. NO crear scripts temporales como solución

### ❌ Anti-Patrón 7: Agente Excediendo su Responsabilidad
```
INCORRECTO:
core-editor modifica extractores Y actualiza versión del sistema a 6.0.0

CORRECTO:
core-editor modifica extractores → Claude pregunta si actualizar versión → version-manager actualiza versión
```

**REGLA CRÍTICA**: Cada agente tiene una responsabilidad específica:
- **core-editor**: Modifica archivos de código, genera reportes de cambios
- **version-manager**: Gestiona TODO tipo de versionado (sistema, archivos, backups, CHANGELOG, BITÁCORA)
- **documentation-specialist-HUV**: Genera documentación técnica y profesional (NO CHANGELOG/BITÁCORA)

UN AGENTE NUNCA DEBE HACER EL TRABAJO DE OTRO AGENTE.

### ❌ Anti-Patrón 8: documentation-specialist Generando CHANGELOG/BITÁCORA
```
INCORRECTO:
documentation-specialist-HUV genera CHANGELOG.md + BITACORA.md + INFORME_GLOBAL.md

CORRECTO:
version-manager genera/actualiza CHANGELOG.md + BITACORA.md (ACUMULATIVOS)
→ documentation-specialist-HUV lee CHANGELOG/BITACORA
→ documentation-specialist-HUV genera RESTO de documentación (INFORME_GLOBAL, etc.)
```

**REGLA CRÍTICA**: CHANGELOG.md y BITACORA_DE_ACERCAMIENTOS.md son ACUMULATIVOS y SOLO gestionados por version-manager.
documentation-specialist-HUV NUNCA los crea ni modifica, solo los lee para contexto.

---

## 🔄 FLUJO DE COORDINACIÓN OBLIGATORIO (Claude Orquestador)

**Claude actúa como ORQUESTADOR** de agentes. Los agentes NO se invocan entre sí directamente.

### FLUJO COMPLETO: Modificación de Código → Versionado → Documentación

```
1. core-editor hace modificaciones
   ↓
2. core-editor genera reporte MD en herramientas_ia/resultados/cambios_YYYYMMDD_HHMMSS.md
   ↓
3. core-editor TERMINA (no cambia versión del sistema)
   ↓
4. Claude pregunta al usuario: "¿Quieres actualizar la versión del sistema?"
   ↓
5. Si usuario dice SÍ:
   a. Claude pregunta: "¿Cuál es la nueva versión? (ej: 6.0.0)"
   b. Usuario proporciona nueva versión
   c. Claude invoca version-manager con:
      - Nueva versión
      - Ruta al reporte MD generado por core-editor
   d. version-manager lee el reporte MD
   e. version-manager actualiza VERSION_INFO
   f. version-manager crea entrada en CHANGELOG.md
   g. version-manager actualiza archivos relevantes
   ↓
6. version-manager TERMINA
   ↓
7. Claude pregunta al usuario: "¿Quieres generar documentación completa?"
   ↓
8. Si usuario dice SÍ:
   a. Claude invoca documentation-specialist-HUV
   b. documentation-specialist-HUV verifica que CHANGELOG.md y BITACORA.md existan
   c. documentation-specialist-HUV lee CHANGELOG.md para extraer cambios de versión actual
   d. documentation-specialist-HUV genera documentación técnica completa
   e. documentation-specialist-HUV genera reporte ejecutivo (si necesario)
   f. documentation-specialist-HUV guarda en documentacion/ (NO en herramientas_ia/resultados/)
   ↓
9. FIN
```

### EJEMPLO CONCRETO:

```
Usuario: "Mejora la extracción de Ki-67"
Claude: [Invoca agente core-editor]
core-editor:
  - Modifica función extract_ki67() en biomarker_extractor.py
  - Valida sintaxis
  - Reprocesa caso de prueba IHQ250025
  - Genera herramientas_ia/resultados/cambios_20251020_150000.md con:
    * Archivos modificados
    * Funciones cambiadas
    * Casos reprocesados
    * Resultados de validación
  - TERMINA

Claude: "✅ Modificaciones completadas. He generado un reporte en herramientas_ia/resultados/cambios_20251020_150000.md
¿Quieres actualizar la versión del sistema?"

Usuario: "Sí, actualiza a 5.3.10"

Claude: [Invoca agente version-manager con --actualizar 5.3.10 y ruta al reporte]
version-manager:
  - Lee cambios_20251020_150000.md
  - Actualiza VERSION_INFO a 5.3.10
  - Crea entrada en CHANGELOG.md:
    ## [5.3.10] - 2025-10-20
    ### Changed
    - Mejorada extracción de Ki-67 en biomarker_extractor.py
    - Reprocesados casos con Ki-67 vacío
  - Actualiza README.md, CLAUDE.md con nueva versión
  - TERMINA

Claude: "✅ Versión actualizada a 5.3.10. ¿Quieres generar documentación completa del sistema?"

Usuario: "Sí"

Claude: [Invoca agente documentation-specialist-HUV]
documentation-specialist-HUV:
  - Verifica que CHANGELOG.md y BITACORA.md existan (✓)
  - Lee CHANGELOG.md para extraer cambios de v6.0.0
  - Genera documentación técnica completa
  - Crea documentacion/INFORME_GLOBAL_PROYECTO.md
  - Crea documentacion/ESTADO_ACTUAL_v6.0.0.md
  - TERMINA

Claude: "✅ Proceso completo. Archivos generados:
- herramientas_ia/resultados/cambios_20251020_150000.md (por core-editor)
- documentacion/CHANGELOG.md (actualizado por version-manager)
- documentacion/BITACORA_DE_ACERCAMIENTOS.md (actualizado por version-manager)
- documentacion/INFORME_GLOBAL_PROYECTO.md (por documentation-specialist-HUV)
- documentacion/ESTADO_ACTUAL_v6.0.0.md (por documentation-specialist-HUV)
```

### REGLAS DE COORDINACIÓN:

1. **core-editor**:
   - Hace TODAS las modificaciones de código necesarias
   - Genera reporte MD en `herramientas_ia/resultados/`
   - NO cambia versión del sistema
   - NO invoca a otros agentes

2. **version-manager**:
   - SOLO se invoca si usuario quiere cambiar versión del sistema
   - Recibe ruta al reporte MD de core-editor (opcional)
   - Lee reporte para generar entrada en CHANGELOG.md (ACUMULATIVO)
   - Genera/actualiza BITACORA_DE_ACERCAMIENTOS.md (ACUMULATIVO)
   - Ambos archivos en documentacion/ (NO en herramientas_ia/resultados/)
   - NO modifica código del sistema (solo archivos de versionado)

3. **documentation-specialist-HUV**:
   - SOLO se invoca si usuario quiere documentar
   - Verifica que CHANGELOG.md y BITACORA.md existan (generados por version-manager)
   - Lee CHANGELOG/BITACORA para extraer contexto de versión actual
   - Genera RESTO de documentación profesional en documentacion/
   - NO genera CHANGELOG ni BITACORA (responsabilidad de version-manager)
   - NO modifica código ni versión del sistema

4. **Claude (orquestador)**:
   - Invoca agentes SECUENCIALMENTE
   - Pregunta al usuario entre cada paso
   - NO permite que agentes se invoquen entre sí

---

## 📈 Uso Proactivo de Agentes

### Usar PROACTIVAMENTE sin esperar solicitud explícita:

**system-diagnostician:**
- Antes de procesar lotes grandes
- Al inicio de sesión diaria
- Mensualmente para mantenimiento

**data-auditor:**
- Después de procesar nuevos casos
- Después de modificaciones por core-editor
- Después de correcciones IA

**database-manager:**
- Antes de operaciones críticas (backup)
- Semanalmente para estadísticas
- Antes de migraciones de schema

**core-editor:**
- Cuando data-auditor detecta patrón de error sistemático
- Cuando system-diagnostician detecta CC > 20
- Cuando usuario menciona "no se extrae", "falta"

**lm-studio-connector:**
- Antes de procesamiento con IA habilitado
- Después de actualizar prompts
- Al detectar campos vacíos corregibles

**documentation-specialist-HUV:**
- Después de completar milestone mayor (6.0.0, etc.)
- Antes de releases importantes
- Cuando se requiere documentar cambios técnicos
- Al crear comunicación para stakeholders
- Cuando version-manager actualiza versión del sistema
- Para generar documentación institucional estilo HUV

---

## 🎯 Métricas de Éxito del Ecosistema

### Métricas de Calidad de Datos:
- **Precisión de extracción**: > 95%
- **Completitud promedio**: > 85%
- **Falsos positivos**: < 3%

### Métricas de Código:
- **Complejidad ciclomática promedio**: < 10
- **Code smells**: < 100
- **Cobertura de tests**: > 80%

### Métricas de Sistema:
- **Disponibilidad**: > 99%
- **Tiempo de procesamiento por caso**: < 30s
- **Uptime LM Studio**: > 95%

### Métricas de BD:
- **Integridad**: 100%
- **Duplicados**: 0
- **Backups disponibles**: Últimos 7 días

---

## 🔍 Troubleshooting Rápido

### Problema: "Caso no se valida correctamente"
**Agente**: data-auditor
```bash
python herramientas_ia/auditor_sistema.py IHQ250025 --nivel profundo
```

### Problema: "Sistema lento"
**Agente**: system-diagnostician
```bash
python herramientas_ia/inspector_sistema.py --benchmark
python herramientas_ia/inspector_sistema.py --analizar-memoria
```

### Problema: "No encuentro un caso específico"
**Agente**: database-manager
```bash
python herramientas_ia/gestor_base_datos.py --buscar IHQ250025
```

### Problema: "Biomarcador no se extrae"
**Agente**: core-editor + data-auditor
```bash
# 1. Leer PDF
python herramientas_ia/auditor_sistema.py IHQ250025 --buscar "Ki-67"
# 2. Mejorar extractor
python herramientas_ia/editor_core.py --editar-extractor Ki-67 --simular
```

### Problema: "IA no responde"
**Agente**: lm-studio-connector
```bash
python herramientas_ia/detectar_lm_studio.py --probar
```

### Problema: "Necesito documentar el proyecto"
**Agente**: documentation-specialist
```bash
python herramientas_ia/generador_documentacion.py --estado
python herramientas_ia/generador_documentacion.py --interactivo
```

---

## 📚 Documentación Detallada

Cada agente tiene documentación completa en `.claude/agents/`:
- **data-auditor.md** (~791 líneas) - Auditoría completa + validación de campos críticos + detección de falsa completitud
- **database-manager.md** (430 líneas)
- **system-diagnostician.md** (456 líneas)
- **core-editor.md** (473 líneas)
- **lm-studio-connector.md** (710 líneas)
- **version-manager.md** (650 líneas)
- **documentation-specialist-HUV.md** (600 líneas) - Estilo institucional HUV

Cada herramienta tiene `--help` integrado con ejemplos.

---

## 🎓 Guía de Uso para Nuevos Usuarios

### Paso 1: Verificar Sistema
```bash
python herramientas_ia/inspector_sistema.py --salud
```

### Paso 2: Ver Estadísticas
```bash
python herramientas_ia/gestor_base_datos.py --stats
```

### Paso 3: Auditar un Caso
```bash
python herramientas_ia/auditor_sistema.py IHQ250001
```

### Paso 4: Buscar Casos
```bash
python herramientas_ia/gestor_base_datos.py --buscar-avanzado --organo MAMA --genero FEMENINO
```

### Paso 5: Validar con IA
```bash
python herramientas_ia/gestor_ia_lm_studio.py --estado
python herramientas_ia/gestor_ia_lm_studio.py --validar-caso IHQ250001 --dry-run
```

### Paso 6: Generar Documentación Institucional HUV
```bash
python herramientas_ia/generador_documentacion.py --completo
python herramientas_ia/generador_documentacion.py --generar comunicados
python herramientas_ia/generador_documentacion.py --interactivo
```
La documentación se genera en `documentacion/` (raíz del proyecto)

---

**Versión del Ecosistema**: 6.0.0
**Fecha**: 2025-10-20
**Total líneas de código**: ~6,865 (7 herramientas especializadas)
**Total documentación**: ~3,069 líneas (7 agentes)
**Estado**: ✅ PRODUCCIÓN - Consolidación LM Studio connector completada (2→1 herramienta)
