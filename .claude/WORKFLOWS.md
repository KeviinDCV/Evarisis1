# 🔄 WORKFLOWS - Sistema EVARISIS

**Este archivo define los workflows maestros paso a paso.**

**Para versiones e historial:** Ver `documentacion/CHANGELOG_CLAUDE.md`

---

## WORKFLOW 1: Procesamiento y Auditoría de Caso IHQ

**Objetivo:** Procesar PDF de caso IHQ + auditar + corregir si es necesario

### Paso 1: Procesamiento Automático
```
Usuario procesa PDF → Sistema EVARISIS extrae datos automáticamente
- unified_extractor procesa PDF completo
- Aplica reglas de extracción y normalización
- Guarda en BD
- Genera debug_map.json con OCR + datos extraídos
```

### Paso 2: Auditoría Automática (FUNC-01)
```
data-auditor ejecuta auditoría inteligente:

1. Lee debug_map.json del caso
   - ⚠️ NO consulta BD directamente
   - ⚠️ NO hace OCR nuevamente

2. Valida extracción inicial (unified_extractor)

3. Valida campos críticos guardados en BD

4. Valida consistencia de biomarcadores
   - Solicitados vs extraídos
   - Búsqueda flexible con sufijos (_ESTADO, _PORCENTAJE)

5. Calcula score de validación (0-100%)

6. Genera reporte JSON con:
   - Warnings y errores
   - Diagnóstico de causa raíz
   - Sugerencias de corrección
```

**Comando:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
```

### Paso 3: Corrección (si score < 90%)

**OPCIÓN A: Corrección Manual** (Actual)
```
1. Usuario revisa diagnóstico de data-auditor
2. Usuario edita extractores en core/extractors/
3. Usuario regenera BD y reprocesa caso
4. data-auditor re-audita
```

**OPCIÓN B: Corrección Automática** (FUNC-02 - ROADMAP)
```
1. Usuario ejecuta: python auditor_sistema.py IHQ250980 --corregir
2. data-auditor diagnostica causa raíz
3. data-auditor virtualiza corrección
4. data-auditor muestra DIFF
5. Usuario aprueba
6. data-auditor aplica cambio + backup
7. data-auditor limpia debug_maps y reprocesa
8. data-auditor re-audita
9. Itera hasta score >= 90% (máx 3 iteraciones)
```

**OPCIÓN C: Corrección con IA** (lm-studio-connector)
```
1. lm-studio-connector sugiere correcciones (dry-run)
2. Usuario revisa y aprueba
3. lm-studio-connector aplica correcciones
4. data-auditor re-valida
```

---

## WORKFLOW 2: Agregar Biomarcador Nuevo al Sistema

**Objetivo:** Agregar biomarcador NO MAPEADO automáticamente

### Paso 1: Detección
```
Usuario detecta biomarcador NO MAPEADO en:
- Reporte de auditoría
- Reporte de completitud
- Procesamiento manual de PDF
```

### Paso 2: Invocación FUNC-03
```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.agregar_biomarcador(
    nombre_biomarcador='CK19',
    variantes=['CK-19', 'CK 19', 'CITOQUERATINA 19']
)
```

### Paso 3: Modificación Automática
```
data-auditor modifica automáticamente 6 archivos:

1. core/database_manager.py
   - Agrega columna IHQ_[BIOMARCADOR]_ESTADO
   - Agrega columna IHQ_[BIOMARCADOR]_PORCENTAJE

2. herramientas_ia/auditor_sistema.py
   - Agrega a BIOMARKER_ALIAS_MAP

3. ui.py
   - Agrega columnas a interfaz

4. core/validation_checker.py
   - Agrega a all_biomarker_mapping

5. core/extractors/biomarker_extractor.py
   - Agrega patrones de extracción (4 ubicaciones)

6. core/extractors/unified_extractor.py
   - Agrega mapeos (2 ubicaciones)
```

### Paso 4: Validación y Reprocesamiento
```
1. data-auditor valida que todos los cambios se aplicaron
2. Usuario regenera BD:
   rm data/huv_oncologia_NUEVO.db
3. Usuario reprocesa PDFs con el nuevo biomarcador
4. data-auditor re-audita casos afectados
```

---

## WORKFLOW 3: Corrección Completitud Automática

**Objetivo:** Workflow end-to-end para casos incompletos por biomarcadores NO MAPEADOS

### Paso 1: Detección de Caso Incompleto
```
Usuario identifica caso con biomarcadores NO MAPEADOS:
- Reporte de completitud muestra "NO MAPEADO"
- Score de completitud < 100%
```

### Paso 2: Invocación FUNC-05
```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.corregir_completitud_automatica('IHQ250987')
```

### Paso 3: Workflow Automático (Fase 1)
```
data-auditor ejecuta:

1. Lee reporte de completitud del caso
2. Detecta biomarcadores "NO MAPEADO"
3. Para cada biomarcador:
   - Llama FUNC-03 (agregar_biomarcador)
   - Genera variantes automáticamente
   - Modifica 6 archivos del sistema
4. Valida que todos los cambios se aplicaron
5. Genera reporte de trazabilidad
```

### Paso 4: Pasos Manuales (Fase 1)
```
Usuario completa manualmente:

1. Regenerar BD:
   rm data/huv_oncologia_NUEVO.db

2. Reprocesar caso:
   python ui.py
   → Seleccionar PDF del caso
   → Procesar

3. Verificar completitud:
   python auditor_sistema.py IHQ250987 --inteligente
   → Verificar score = 100%
```

**Nota:** Fase 2 (completamente automático) en ROADMAP

---

## WORKFLOW 4: Actualización de Versión + Documentación

**Objetivo:** Actualizar versión del sistema y generar documentación completa

### Paso 1: Usuario Solicita Actualización
```
Usuario: "Actualiza a v6.0.8 con corrección del auditor"
```

### Paso 2: Claude Pregunta Detalles
```
Claude pregunta:
- ¿Qué cambios tiene esta versión?
- ¿Contexto de esta iteración?
- ¿Validación técnica requerida?
```

### Paso 3: Claude Invoca documentation-specialist-HUV
```
documentation-specialist-HUV ejecuta:

1. Actualiza config/version_info.py → nueva versión

2. Genera/Actualiza documentacion/CHANGELOG.md (ACUMULATIVO)
   - Historial del programa principal

3. Genera/Actualiza documentacion/BITACORA_DE_ACERCAMIENTOS.md (ACUMULATIVO)
   - Bitácora de desarrollo

4. Genera documentación completa (REESCRITURA):
   - INFORME_GLOBAL_PROYECTO.md
   - README.md
   - NOTEBOOK_LM_CONSOLIDADO_TECNICO.md
   - analisis/*.md
   - comunicados/*.md
```

### Paso 4: Claude Reporta Resultado
```
Claude reporta:
- Archivos actualizados
- Ubicación de documentación
- Resumen de cambios
```

**Comando:**
```bash
python herramientas_ia/gestor_version.py --actualizar
```

---

## WORKFLOW 5: Validación Post-Modificación de Código

**Objetivo:** Validar casos después de modificar extractores o agregar biomarcadores

### Paso 1: Modificación de Código
```
Usuario O lm-studio-connector modifica:
- Extractores en core/extractors/
- Reglas de validación
- Agregó biomarcadores
```

### Paso 2: Claude Pregunta
```
Claude: "¿Validar cambios con auditoría inteligente?"
Usuario: "Sí, validar casos IHQ250980, IHQ250981, IHQ250982"
```

### Paso 3: Claude Invoca data-auditor
```
Para cada caso:
1. data-auditor ejecuta FUNC-01
2. Genera reporte JSON
3. Claude recopila resultados
```

### Paso 4: Claude Presenta Resultados
```
Claude muestra:
- Tabla de scores por caso
- Casos que mejoraron
- Casos que necesitan atención
- Sugerencias de siguiente paso
```

### Paso 5: Claude Pregunta Siguiente Acción
```
Claude: "¿Actualizar versión y documentar?"
Usuario: "Sí, v6.0.9"

Claude invoca documentation-specialist-HUV
```

---

## WORKFLOW 6: Validación con IA (LM Studio)

**Objetivo:** Usar IA local para validar casos complejos

### Paso 1: Usuario Solicita Validación IA
```
Usuario: "Valida IHQ250980 con IA"
```

### Paso 2: Claude Invoca lm-studio-connector
```
lm-studio-connector ejecuta:

1. Verifica estado de LM Studio
2. Lee debug_map del caso
3. Prepara prompt con:
   - OCR del PDF
   - Datos extraídos
   - Reglas de validación
4. Envía a LM Studio
5. Procesa respuesta de IA
6. Genera reporte MD con:
   - Validación IA
   - Confianza (0-100%)
   - Sugerencias de corrección
```

### Paso 3: Claude Presenta Resultados
```
Claude muestra:
- Validación IA vs validación data-auditor
- Áreas de discrepancia
- Sugerencias de IA para mejorar
```

### Paso 4: Aplicar Correcciones (Opcional)
```
Si Usuario aprueba:
1. lm-studio-connector aplica correcciones de alta confianza
2. data-auditor re-valida
3. Claude reporta resultado final
```

**Comando:**
```bash
python herramientas_ia/gestor_ia_lm_studio.py --validar IHQ250980
```

---

## 🔄 Coordinación entre Agentes

### Regla de Orquestación
```
Claude NO permite que agentes se invoquen entre sí.
Claude orquesta secuencialmente:

1. Acción → Usuario/agente modifica código
2. Validación → Claude invoca data-auditor
3. Documentación → Claude invoca documentation-specialist-HUV
4. Claude pregunta entre cada paso antes de continuar
```

### Separación de Responsabilidades
```
data-auditor:
- Auditoría inteligente
- Gestión de biomarcadores
- ⚠️ ORIGEN DE DATOS: SOLO debug_maps/

lm-studio-connector:
- Gestión LM Studio
- Validación con IA
- Correcciones sugeridas por IA

documentation-specialist-HUV:
- Versionado
- Generación de CHANGELOG
- Documentación institucional
```

---

## 📋 Reglas de Ejecución

### Antes de Modificar BD
```
1. data-auditor SIEMPRE crea backup
2. Ubicación: backups/bd_backup_[CASO]_[TIMESTAMP].db
3. Validar que backup existe antes de continuar
```

### Antes de Aplicar Correcciones IA
```
1. lm-studio-connector SIEMPRE hace dry-run
2. Muestra cambios propuestos al usuario
3. Usuario aprueba antes de aplicar
```

### Generación de Reportes
```
Todos los agentes generan reportes en:
herramientas_ia/resultados/

Formatos:
- data-auditor → JSON
- lm-studio-connector → MD
- documentation-specialist-HUV → MD
```

---

## 🚨 Anti-Patrones (NUNCA HACER)

### ❌ Modificar sin Validar
```
INCORRECTO:
Usuario modifica código → Continúa sin validar

CORRECTO:
Usuario modifica código → data-auditor valida → Continuar
```

### ❌ Crear Scripts Adhoc
```
INCORRECTO:
Claude crea temp_fix_ki67.py

CORRECTO:
Usuario modifica extractor existente directamente
```

### ❌ data-auditor Consultando BD Directamente
```
INCORRECTO:
data-auditor lee BD → compara con PDF → genera reporte

CORRECTO:
data-auditor lee debug_map.json → valida semántica → genera reporte

POR QUÉ ESTÁ MAL:
- debug_map.json YA contiene datos_guardados de BD
- debug_map.json YA contiene OCR del PDF
- Consultar BD duplica trabajo y ralentiza
```

### ❌ Agente Buscando PDFs o Haciendo OCR
```
INCORRECTO:
data-auditor busca PDF → hace OCR → extrae datos

CORRECTO:
data-auditor lee debug_map.json (ya tiene OCR + datos)

debug_map.json contiene:
- ocr.texto_consolidado (texto completo del PDF)
- base_datos.datos_guardados (datos en BD)
- metadata completa
```

---

**Para información de versiones actuales:** Ver `documentacion/CHANGELOG_CLAUDE.md`
**Para API detallada de agentes:** Ver `.claude/agents/*.md`
