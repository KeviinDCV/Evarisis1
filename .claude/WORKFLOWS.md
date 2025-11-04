# 🔄 WORKFLOWS - Sistema EVARISIS

**Este archivo define los workflows maestros paso a paso.**

**Para versiones e historial:** Ver `documentacion/CHANGELOG_CLAUDE.md`

---

## WORKFLOW 1: Procesamiento y Auditoría de Caso IHQ

**Objetivo:** Procesar PDF de caso IHQ + auditar + corregir si es necesario

### Contexto: Estructura de PDFs Fuente

Los PDFs están organizados por rangos en `pdfs_patologia/`:
- **Ubicación:** `C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV9GESTOR_ONCOLOGIA\pdfs_patologia\`
- **Formato:** `IHQ DEL XXX AL YYY.pdf` (ej: `IHQ DEL 980 AL 1037.pdf`)
- **Contenido:** Cada PDF contiene ~50 casos consolidados
- **Total:** 20 PDFs con casos del 001 al 1037

**Ejemplo:**
- Caso IHQ251007 está en → `IHQ DEL 001 AL 050.pdf` (rango 001-050, contiene casos 001-050)
- Caso IHQ250982 está en → `IHQ DEL 980 AL 1037.pdf` (rango 980-1037)

**Búsqueda Automática:**
```python
# auditor_sistema.py incluye función para localizar PDF correcto
auditor._buscar_pdf_por_numero("IHQ251007")
# → Retorna: Path("pdfs_patologia/IHQ DEL 001 AL 050.pdf")
```

**⚠️ IMPORTANTE:**
- **NO existen** PDFs individuales por caso (no hay "IHQ251007.pdf")
- **Reprocesar un caso = procesar el PDF completo** (~50 casos)
- Sistema NO puede procesar casos individuales de forma aislada

---

### Paso 1: Procesamiento Automático

**Opción A: Selección Manual (ui.py)**
```
1. Usuario abre ui.py
2. Usuario selecciona PDF desde diálogo de archivos (pdfs_patologia/)
3. Sistema EVARISIS procesa:
   - unified_extractor procesa PDF completo (~50 casos)
   - Aplica reglas de extracción y normalización
   - Guarda en BD
   - Genera debug_map.json para cada caso con OCR + datos extraídos
```

**Opción B: Búsqueda Automática (auditor_sistema.py)**
```
1. Usuario/agente necesita procesar caso específico IHQ251007
2. auditor._buscar_pdf_por_numero("IHQ251007")
   → Encuentra automáticamente: pdfs_patologia/IHQ DEL 001 AL 050.pdf
3. Usuario procesa el PDF manualmente (contiene 50 casos incluyendo IHQ251007)
4. Sistema genera debug_maps para todos los casos del PDF
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

**OPCIÓN D: Reprocesamiento Automático** (FUNC-06 - NUEVO)
```
1. Usuario ejecuta: auditor.reprocesar_caso_completo("IHQ251007")
2. data-auditor lee debug_map → identifica pdf_path automáticamente
3. data-auditor audita ANTES (para comparación)
4. data-auditor elimina registros BD + debug_maps del PDF completo (~50 casos)
5. data-auditor reprocesa PDF automáticamente con extractores actualizados
6. data-auditor re-audita DESPUÉS
7. data-auditor muestra comparación antes/después
8. data-auditor genera reporte JSON con métricas
```

**Cuándo usar cada opción:**
- **Opción A (Manual):** Cuando necesitas control fino sobre los cambios
- **Opción B (FUNC-02):** Cuando quieres corrección automática sin perder datos (ROADMAP)
- **Opción C (IA):** Cuando necesitas sugerencias inteligentes de corrección
- **Opción D (FUNC-06):** Después de modificar extractores o agregar biomarcadores (FUNC-03)

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

## WORKFLOW 4: Reprocesar Caso Después de Corregir Extractor

**Objetivo:** Workflow completo para validar correcciones en extractores

**Caso de uso:** Modificaste código de extracción (ej: biomarker_extractor.py) y quieres validar que la corrección funcionó correctamente.

**Ejemplo real:** E-Cadherina no se extraía → Modificaste patrón regex → Quieres verificar que ahora se extrae "POSITIVO".

### Paso 1: Diagnóstico Inicial (FUNC-01)

```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
auditor.auditar_caso_inteligente('IHQ251008', json_export=True)
```

**Resultado esperado:**
- Identifica el problema (ej: "E-Cadherina NO MAPEADO")
- Score de validación: 88.9% (8/9)
- Cobertura de biomarcadores: 80% (4/5)

### Paso 2: Investigar Causa Raíz

```
data-auditor genera diagnóstico:
1. Lee debug_map.json del caso
2. Busca texto del biomarcador en OCR
3. Identifica por qué NO se extrajo:
   - ¿Patrón regex no coincide?
   - ¿Sección prioritaria incorrecta?
   - ¿Falta fallback al texto completo?
```

**Ubicaciones de investigación:**
- `data/debug_maps/debug_map_IHQ251008_[timestamp].json` → Ver OCR completo
- `core/extractors/biomarker_extractor.py` → Revisar patrones del biomarcador
- `core/extractors/medical_extractor.py` → Si es campo médico
- `core/unified_extractor.py` → Si es campo general

### Paso 3: Corregir Código del Extractor

**Usuario modifica el extractor directamente:**

```python
# Ejemplo en biomarker_extractor.py línea 499
# ANTES:
r'(?i)marcaci[óo]n\s+(positiva|negativa)\s+para[:\s]+E[\s-]?CADHERINA'

# DESPUÉS (permite guion pegado):
r'(?i)marcaci[óo]n\s+(positiva|negativa)\s+para[:\s-]+E[\s-]?CADHERINA'
```

**Tipos de correcciones comunes:**
- Ajustar patrón regex (capturar variantes del texto)
- Agregar fallback al texto completo (si `usa_prioridad_seccion = True`)
- Normalizar valores extraídos
- Agregar alias de biomarcadores

### Paso 4: Reprocesar Automáticamente (FUNC-06)

```python
auditor.reprocesar_caso_completo('IHQ251008')
```

**Qué hace FUNC-06 automáticamente:**
1. Busca debug_map → extrae pdf_path
2. Identifica rango del PDF (ej: 980-1037)
3. Audita ANTES (para comparación)
4. **Crea backup automático** (BD + debug_maps en `backups/func06/`)
5. Elimina registros BD del rango completo (~50 casos)
6. Elimina debug_maps del rango completo
7. **Reprocesa PDF completo con extractores ACTUALIZADOS**
8. Re-audita caso objetivo
9. Genera reporte comparativo (antes/después)

**Resultado esperado:**
```
💾 PASO 4.5: Creando backup automático...
   ✅ Backup BD: huv_oncologia_pre_func06_IHQ251008_20251103_223015.db
   ✅ Backup debug_maps: 47 archivos respaldados

🔄 PASO 7: Reprocesando PDF completo...
   ✅ 47 casos reprocesados correctamente

📊 COMPARACIÓN:
   Score ANTES:   88.9%
   Score DESPUÉS: 100.0%
   Mejora:        +11.1% ✅
```

### Paso 5: Validar Corrección (FUNC-01)

```python
auditor.auditar_caso_inteligente('IHQ251008', json_export=True)
```

**Resultado esperado:**
- E-Cadherina: POSITIVO ✅
- Score de validación: 100.0% (9/9)
- Cobertura de biomarcadores: 100% (5/5)

**Verificaciones específicas:**
- Campo `IHQ_E_CADHERINA` contiene "POSITIVO"
- Sin biomarcadores "NO MAPEADO"
- Sin warnings ni errores en reporte
- Cobertura de biomarcadores = 100%

---

### Manejo de Errores en FUNC-06

**Error: PDF no encontrado**
```
╔══════════════════════════════════════════════════════════════════════╗
║ ERROR: PDF NO ENCONTRADO                                             ║
╚══════════════════════════════════════════════════════════════════════╝

Archivo esperado: pdfs_patologia/IHQ DEL 980 AL 1037.pdf

📋 OPCIONES DE RECUPERACIÓN:
   1. Verificar que el PDF existe: ls pdfs_patologia/
   2. Restaurar backup: backups/func06/huv_oncologia_pre_func06_IHQ251008_[timestamp].db
```

**Error: Fallo en reprocesamiento**
```
╔══════════════════════════════════════════════════════════════════════╗
║ ERROR EN REPROCESAMIENTO                                             ║
╚══════════════════════════════════════════════════════════════════════╝

PDF: IHQ DEL 980 AL 1037.pdf
Error técnico: SyntaxError in biomarker_extractor.py line 505

🔄 INTENTANDO ROLLBACK AUTOMÁTICO...
   ✅ BD restaurada exitosamente

📋 OPCIONES DE RECUPERACIÓN:
   1. Revisar error de sintaxis en extractor
   2. Corregir código y ejecutar FUNC-06 nuevamente
```

### Cuándo Usar FUNC-06 vs Otras Opciones

| Situación | Solución | Razón |
|-----------|----------|-------|
| Modificaste patrón regex de biomarcador | **FUNC-06** | Necesitas reprocesar con extractor actualizado |
| Biomarcador NO existe en sistema (no hay columna BD) | FUNC-03 → FUNC-06 | Primero agrega columna, luego reprocesa |
| Caso incompleto por múltiples biomarcadores NO MAPEADOS | FUNC-05 | Workflow especializado para completitud |
| Solo quieres validar sin reprocesar | FUNC-01 | Auditoría sin modificar datos |
| Modificaste normalización de valores | **FUNC-06** | Necesitas reprocesar para aplicar nueva normalización |

### Reporte JSON Generado

**Ubicación:** `herramientas_ia/resultados/FUNC-06_reprocesamiento_IHQ251008_[timestamp].json`

**Contenido:**
```json
{
  "caso": "IHQ251008",
  "pdf_path": "pdfs_patologia/IHQ DEL 980 AL 1037.pdf",
  "casos_eliminados": 47,
  "casos_reprocesados": 47,
  "score_antes": 88.9,
  "score_despues": 100.0,
  "mejora_porcentaje": 11.1,
  "backup_db": "backups/func06/huv_oncologia_pre_func06_IHQ251008_20251103_223015.db",
  "backup_debug_maps": "backups/func06/debug_maps_pre_func06_IHQ251008_20251103_223015",
  "estado": "EXITOSO",
  "errores": []
}
```

**Uso del reporte:**
- Verificar que backup se creó (`backup_db`)
- Comparar scores (antes/después)
- Troubleshooting si falló (`errores`)
- Auditoría de cambios

---

### Ventajas de FUNC-06

✅ **Todo automático:** NO necesitas borrar BD, NO necesitas abrir ui.py, NO necesitas buscar PDF
✅ **Backups automáticos:** Crea backup antes de eliminar datos
✅ **Rollback automático:** Restaura BD si falla el reprocesamiento
✅ **Comparación integrada:** Muestra mejora de score antes/después
✅ **Trazabilidad completa:** Reporte JSON con todas las métricas
✅ **Reporte siempre se guarda:** Incluso si falla (para troubleshooting)

---

## WORKFLOW 5: Actualización de Versión + Documentación

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

## WORKFLOW 7: Validación con IA (LM Studio)

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
