# 🏥 EVARISIS - Sistema Inteligente de Gestión Oncológica

**Hospital Universitario del Valle**
**Versión:** 6.0.16 | **Estado:** ✅ PRODUCCIÓN
**Fecha:** 30 de octubre de 2025

---

## 🚨 REGLA CRÍTICA: Claude SOLO Actúa Mediante Agentes

**PROHIBIDO:**
- ❌ Crear archivos en carpeta raíz
- ❌ Crear scripts temporales
- ❌ Hacer cambios directos sin invocar agentes
- ❌ Leer BD/archivos directamente (usa agentes)

**OBLIGATORIO:**
- ✅ Claude SIEMPRE invoca agentes especializados
- ✅ Agentes crean archivos SOLO en `herramientas_ia/resultados/`
- ✅ Si NO existe agente → Claude INFORMA al usuario
- ✅ Claude pregunta entre pasos de agentes

**Flujo correcto:**
```
Usuario: "Audita IHQ250025"
→ Claude invoca data-auditor
→ data-auditor ejecuta, genera reporte en herramientas_ia/resultados/
→ Claude muestra resultado y pregunta siguiente paso
```

---

## 📊 Arquitectura del Ecosistema

### 4 Herramientas Especializadas
1. **auditor_sistema.py** - Auditoría Inteligente + Corrección Automática + Gestión Biomarcadores
   - FUNC-01: Auditoría inteligente (validación semántica completa)
   - FUNC-02: Corrección automática con validación iterativa
   - FUNC-03: Agregar biomarcador automáticamente (6 archivos)
   - FUNC-05: Workflow completitud automática (detección + corrección)
2. **gestor_ia_lm_studio.py** - Gestión LM Studio + IA
3. **gestor_version.py** - Versionado + CHANGELOG + BITÁCORA
4. **generador_documentacion.py** - Documentación profesional

_Nota: editor_core.py e inspector_sistema.py están disponibles pero pendientes de reasignación._

### 3 Agentes Especializados
| Agente | Herramientas | Documentación |
|--------|-------------|---------------|
| **data-auditor** | auditor_sistema.py | [.claude/agents/data-auditor.md](.claude/agents/data-auditor.md) |
| **lm-studio-connector** | gestor_ia_lm_studio.py | [.claude/agents/lm-studio-connector.md](.claude/agents/lm-studio-connector.md) |
| **documentation-specialist-HUV** | generador_documentacion.py + gestor_version.py | [.claude/agents/documentation-specialist-HUV.md](.claude/agents/documentation-specialist-HUV.md) |

**Cada agente tiene documentación COMPLETA en su archivo .md** (capacidades, comandos, ejemplos)

**🆕 Cambios v6.0.16 (2025-10-30):**
- ✅ **FUNC-03 IMPLEMENTADA:** `agregar_biomarcador()` modifica automáticamente 6 archivos del sistema
- ✅ **FUNC-05 IMPLEMENTADA:** `corregir_completitud_automatica()` workflow inteligente end-to-end
- ✅ **Gestión automática biomarcadores:** Detecta "NO MAPEADO" en reportes → agrega al sistema completo
- ✅ **6 archivos sincronizados:** database_manager, auditor_sistema, ui, validation_checker, biomarker_extractor, unified_extractor
- ✅ **Generación de variantes:** Crea automáticamente alias (CK19 → CK-19, CK 19)
- ✅ **Reportes detallados:** Trazabilidad completa de modificaciones por archivo
- 🔧 **Workflow completo:** Reporte completitud → detección → corrección → validación
- 📝 **Herramientas actualizadas:**
  - `auditor_sistema.py` v3.3.0 (FUNC-01 + FUNC-02 + FUNC-03 + FUNC-05)
  - `data-auditor.md` v3.3.0 (documentación completa FUNC-03 + FUNC-05)
- ✅ **Fix CK19 IHQ250987:** Biomarcador agregado automáticamente a 6 archivos + validado

**Cambios v6.0.11 (2025-10-26 NOCHE FINAL):**
- ✅ **FALLBACK FACTOR_PRONOSTICO:** Construye desde columnas IHQ_* si extracción directa falla
- ✅ **Soluciona formatos PDF no estándar:** Casos donde biomarcadores están fuera del bloque estándar
- ✅ **Función nueva:** `build_factor_pronostico_from_columns()` en medical_extractor
- ✅ **Integración automática:** unified_extractor ejecuta fallback post-extracción
- 📝 **Extractores actualizados:**
  - `medical_extractor.py` v4.2.4 (+ fallback desde columnas)
  - `unified_extractor.py` v4.2.6 (integración fallback)
  - `auditor_sistema.py` v3.0.2 (búsqueda flexible biomarcadores)
- ✅ **Fix IHQ250984:** FACTOR_PRONOSTICO construido desde columnas (HER2, Ki-67, Estrógenos, Progesterona)

**Cambios v6.0.10 (2025-10-26 NOCHE):**
- ✅ **FIX CRÍTICO - FACTOR_PRONOSTICO:** Filtrado ESTRICTO de solo 4 biomarcadores de pronóstico
- ✅ **FIX CRÍTICO - Validación biomarcadores:** Búsqueda flexible con sufijos (_ESTADO, _PORCENTAJE)
- ✅ **Filosofía corregida:** Si NO hay HER2/Ki-67/Estrógenos/Progesterona → "NO APLICA" (no "poner lo que haya")
- ✅ **Elimina tipificación de FP:** CKAE1AE3, S100, GATA3, TTF-1, PAX8, CDX2 → van SOLO en columnas IHQ_*
- 📝 **Extractores actualizados:**
  - `auditor_sistema.py` v3.0.2 (búsqueda flexible biomarcadores)
  - `medical_extractor.py` v4.2.3 (filtrado completo todos los formatos)
- ✅ **Fix IHQ250983:** P40_ESTADO detectado correctamente, FACTOR_PRONOSTICO = "NO APLICA"

**Cambios v6.0.9 (2025-10-26 TARDE):**
- ✅ **Validación robusta:** DIAGNOSTICO_COLORACION con 3 estrategias (exacta, componentes, patrón)
- ✅ **Normalización automática:** FACTOR_PRONOSTICO normaliza Ki-67, HER2, Receptores DURANTE extracción
- ✅ **Limpieza DIAGNOSTICO_PRINCIPAL:** Elimina datos del estudio M (GRADO, SCORE, NOTTINGHAM)
- ✅ **REGLAS DE ORO implementadas:** #1 (4 biomarcadores), #2 (Ki-67 sin prefijo), #4 (Principal limpio)
- 📝 **Extractores actualizados:**
  - `auditor_sistema.py` v3.0.1 (validación mejorada)
  - `medical_extractor.py` v4.2.1 (normalización automática)
  - `unified_extractor.py` v4.2.5 (limpieza diagnóstico principal)
- ✅ **Fix IHQ250981:** 100% validación, sin duplicación diagnósticos

**Cambios v6.0.8 (2025-10-26 MAÑANA):**
- ✅ **FUNC-02 optimizada:** Modo `--usar-reporte-existente` (98% más rápido)
- ✅ **FUNC-02 reprocesamiento:** Arreglado para usar `unified_extractor` (antes fallaba)
- ✅ **FUNC-02 funcional:** Corrige datos en BD + reprocesa + re-audita (Fase 1 completa)
- 📚 **Documentación actualizada:** data-auditor.md refleja estado real de FUNC-02

**Cambios v6.0.7 (2025-10-26):**
- ❌ Eliminado `gestor_base_datos.py` (integrado en auditor_sistema.py)
- ❌ Removido agente `core-editor` (ediciones manuales por ahora)
- 🧹 Limpiado `auditor_sistema.py`: 17 funcionalidades → 2 (FUNC-01 + FUNC-02)

---

## 🎯 Matriz Rápida de Responsabilidades

| Usuario necesita | Agente / Acción | Comando |
|------------------|--------|---------|
| Auditar caso | **data-auditor** (FUNC-01) | `python herramientas_ia/auditor_sistema.py IHQ250025 --inteligente` |
| Corregir caso automáticamente | **data-auditor** (FUNC-02) | `python herramientas_ia/auditor_sistema.py IHQ250025 --corregir` |
| Agregar biomarcador al sistema | **data-auditor** (FUNC-03) | `auditor.agregar_biomarcador('CK19', ['CK-19', 'CK 19'])` |
| Corregir completitud automática | **data-auditor** (FUNC-05) | `auditor.corregir_completitud_automatica('IHQ250987')` |
| Validar campos críticos, biomarcadores | **data-auditor** (FUNC-01) | Lee `debug_maps/IHQ250025/debug_map.json` |
| Validar con IA, editar prompts | **lm-studio-connector** | `python herramientas_ia/gestor_ia_lm_studio.py --validar IHQ250025` |
| Cambiar versión, generar CHANGELOG | **documentation-specialist-HUV** | `python herramientas_ia/gestor_version.py --actualizar` |

**⚠️ IMPORTANTE para data-auditor:**
- ✅ **SÍ usa:** `debug_maps/[CASO]/debug_map.json` (contiene TODO: OCR + BD)
- ❌ **NO usa:** Consultas directas a BD SQLite
- ❌ **NO usa:** Lectura directa de PDFs
- ❌ **NO usa:** OCR en tiempo real

---

## 🔗 Reglas de Coordinación entre Agentes

### Validación Obligatoria
- Después de editar código → **data-auditor** valida casos afectados
- **lm-studio-connector** → notifica a **data-auditor** después de correcciones IA

### Backup Obligatorio
- **data-auditor** → SIEMPRE crea backup en `backups/` antes de modificar BD

### Dry-Run Primero
- **lm-studio-connector** → SIEMPRE dry-run antes de aplicar correcciones IA

### Generación de Reportes
- **data-auditor** → Genera reportes JSON en `herramientas_ia/resultados/`
- **lm-studio-connector** → Genera reportes MD en `herramientas_ia/resultados/`
- **documentation-specialist-HUV** → Lee reportes para generar CHANGELOG/documentación

### Separación de Responsabilidades
- **data-auditor** → Auditoría inteligente + Corrección automática + Gestión biomarcadores
  - **ORIGEN DE DATOS:** SOLO debug_maps (NUNCA consultar BD directamente)
  - FUNC-01: Valida casos desde `debug_maps/[CASO]/debug_map.json`
  - FUNC-02: Corrige datos en BD + reprocesa (parche temporal)
  - FUNC-03 (v6.0.16): Agrega biomarcadores automáticamente (modifica 6 archivos)
  - FUNC-05 (v6.0.16): Workflow completitud automática (detecta + agrega + reprocesa)
  - **FLUJO CORRECTO:**
    1. Lee debug_map.json (contiene OCR + datos extraídos)
    2. Valida semánticamente campos críticos
    3. Genera reporte JSON en `herramientas_ia/resultados/`
    4. **NO consulta BD** (BD solo para correcciones FUNC-02)
  - **GESTIÓN BIOMARCADORES (FUNC-03/FUNC-05):**
    1. Detecta biomarcadores "NO MAPEADO" en reportes de completitud
    2. Modifica automáticamente 6 archivos del sistema
    3. Valida que todos los cambios se aplicaron correctamente
    4. Genera reportes detallados de trazabilidad
- **lm-studio-connector** → SOLO archivos IA (prompts, llm_client.py, validación IA)
- **documentation-specialist-HUV** → Versionado + CHANGELOG/BITÁCORA + documentación institucional

---

## 🔄 Flujo de Coordinación (Claude Orquestador)

**Claude NO permite que agentes se invoquen entre sí. Claude orquesta secuencialmente:**

```
1. Usuario edita código manualmente O lm-studio-connector aplica correcciones IA
   → Modifica extractores, agrega biomarcadores, etc.
   → TERMINA edición

2. Claude pregunta: "¿Validar cambios con auditoría?"
   → Usuario: "Sí"

3. Claude invoca data-auditor
   → valida casos afectados
   → genera reporte de validación JSON
   → TERMINA

4. Claude pregunta: "¿Actualizar versión y documentar?"
   → Usuario: "Sí, v6.0.8"

5. Claude invoca documentation-specialist-HUV
   → lee reportes de data-auditor y/o lm-studio-connector
   → actualiza VERSION_INFO (gestor_version.py)
   → genera/actualiza CHANGELOG.md + BITACORA.md
   → genera documentación completa
   → TERMINA

6. FIN
```

---

## 🚨 Anti-Patrones (NUNCA HACER)

❌ **Modificar sin validar**
```
INCORRECTO: Usuario modifica código → Continúa sin validar
CORRECTO: Usuario modifica código → data-auditor valida → Continuar
```

❌ **Crear scripts adhoc**
```
INCORRECTO: Claude crea temp_fix_ki67.py
CORRECTO: Usuario modifica extractor existente directamente
```

❌ **Agente excediendo responsabilidad**
```
INCORRECTO: data-auditor modifica código Y actualiza versión
CORRECTO: Usuario modifica código → data-auditor valida → documentation-specialist actualiza versión
```

❌ **data-auditor consultando BD directamente (CRÍTICO)**
```
INCORRECTO: data-auditor lee BD → compara con PDF → genera reporte
CORRECTO: data-auditor lee debug_map.json → valida semántica → genera reporte

POR QUÉ ESTÁ MAL:
- debug_map.json YA contiene datos_guardados de BD
- debug_map.json YA contiene OCR del PDF
- Consultar BD duplica trabajo y ralentiza
- FUNC-01 debe ser SOLO lectura de debug_map
```

❌ **Agente buscando PDFs o haciendo OCR**
```
INCORRECTO: data-auditor busca PDF → hace OCR → extrae datos
CORRECTO: data-auditor lee debug_map.json (ya tiene OCR + datos)

debug_map.json contiene:
- ocr.texto_consolidado (texto completo del PDF)
- base_datos.datos_guardados (datos en BD)
- metadata completa
```

---

## ⭐ Reglas de Oro IMPLEMENTADAS (v6.0.11)

### REGLA DE ORO #1: FACTOR_PRONOSTICO - SOLO 4 Biomarcadores (FILTRADO ESTRICTO + FALLBACK)
**✅ IMPLEMENTADO en `medical_extractor.py` v4.2.4** (filtrado estricto + fallback desde columnas)

**FILOSOFÍA CORRECTA (v6.0.10):**
```
SI (HER2 OR Ki-67 OR Estrógenos OR Progesterona están en IHQ_ESTUDIOS_SOLICITADOS):
   FACTOR_PRONOSTICO = SOLO esos 4 biomarcadores (los que estén presentes)
SINO:
   FACTOR_PRONOSTICO = "NO APLICA"
```

**FACTOR_PRONOSTICO debe contener EXCLUSIVAMENTE:**
1. **HER2** (o HER-2)
2. **Ki-67** (o Ki67, KI-67)
3. **Receptor de Estrógenos** (ER, Estrogeno, Estrogenos)
4. **Receptor de Progesterona** (PR, Progesterona)

**NO incluir:** CKAE1AE3, S100, GATA3, TTF-1, CK7, PAX8, CDX2, E-Cadherina, P53, CD10, CD56, etc.
→ **Estos son biomarcadores de TIPIFICACIÓN TUMORAL** (identifican origen del tumor)
→ Van EXCLUSIVAMENTE en columnas individuales `IHQ_*`

**Ejemplo correcto (IHQ250983):**
- Biomarcadores solicitados: GATA3, CDX2, PAX8, TTF-1, P40, S100, CKAE1AE3
- NINGUNO es biomarcador de pronóstico → `FACTOR_PRONOSTICO = "NO APLICA"`
- ✅ Correcto: Todos van en `IHQ_GATA3`, `IHQ_CDX2`, `IHQ_PAX8`, etc.
- ❌ **INCORRECTO (filosofía antigua):** Poner todos en FACTOR_PRONOSTICO "porque no encontró los 4"

**🆕 FALLBACK AUTOMÁTICO (v6.0.11):**

Si la extracción directa de FACTOR_PRONOSTICO falla (por formato PDF no estándar), el sistema construye automáticamente desde columnas individuales:

```python
# Ejecutado automáticamente en unified_extractor.py (línea 577-595)
if FACTOR_PRONOSTICO vacío o "NO APLICA":
    Buscar en: IHQ_HER2, IHQ_KI-67, IHQ_RECEPTOR_ESTROGENOS, IHQ_RECEPTOR_PROGESTERONA
    if al menos 1 tiene valor:
        Construir: "HER2: X, Ki-67: Y, Receptor de Estrógeno: Z, Receptor de Progesterona: W"
```

**Ejemplo FALLBACK (IHQ250984):**
- **Problema:** Biomarcadores en PDF fuera del bloque "REPORTE DE BIOMARCADORES" → extracción directa falla
- **Columnas IHQ_* pobladas:** ✅ HER2, Ki-67, Estrógenos, Progesterona extraídos correctamente
- **FACTOR_PRONOSTICO original:** ❌ "NO APLICA"
- **FALLBACK activado:** ✅ Construye desde columnas → `"HER2: POSITIVO (SCORE 3+), Ki-67: 60%, Receptor de Estrógeno: NEGATIVO, Receptor de Progesterona: NEGATIVO"`

**Casos donde se activa el FALLBACK:**
- PDFs con biomarcadores fuera del bloque estándar
- Formatos de PDF no estándar o corruptos
- Biomarcadores divididos entre páginas
- OCR con errores que impiden patrones de extracción

### REGLA DE ORO #2: Ki-67 SIN "Índice de proliferación celular"
**✅ IMPLEMENTADO en `medical_extractor.py` v4.2.1 (líneas 836-844)**

**Normalización automática durante extracción:**
- ❌ OCR: `Índice de proliferación celular (Ki67): 21-30%`
- ✅ Extraído: `Ki-67: 21-30%`

**Además normaliza automáticamente:**
- **HER2:** Elimina "SOBREEXPRESIÓN DE", formato "HER2" (sin guión)
- **Receptores:** Elimina guiones iniciales, formato estándar

### REGLA DE ORO #3: DIAGNOSTICO_COLORACION con datos del estudio M
**✅ IMPLEMENTADO en `auditor_sistema.py` v3.0.1 (líneas 710-774)**

DIAGNOSTICO_COLORACION **DEBE** contener:
- ✅ Grado histológico
- ✅ Score Nottingham
- ✅ Invasión linfovascular/perineural
- ✅ Hasta 5 componentes del estudio M

**Validación con 3 estrategias:**
1. Búsqueda exacta normalizada
2. Búsqueda por componentes (≥80%)
3. Patrón flexible en descripción macroscópica

### REGLA DE ORO #4: DIAGNOSTICO_PRINCIPAL sin datos del estudio M
**✅ IMPLEMENTADO en `unified_extractor.py` v4.2.5 (líneas 132)**

DIAGNOSTICO_PRINCIPAL **NO debe** contener:
- ❌ GRADO HISTOLÓGICO, SCORE, NOTTINGHAM
- ❌ INVASIÓN LINFOVASCULAR/PERINEURAL
- ❌ IN SITU, etc.

**Ejemplo:**
- ❌ Incorrecto: "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)"
- ✅ Correcto: "CARCINOMA MICROPAPILAR, INVASIVO"

---

## 📈 Uso Proactivo de Agentes

**Usar SIN esperar solicitud explícita:**

- **data-auditor**: Después de procesar PDFs, después de modificaciones en extractores, antes de lotes grandes
- **lm-studio-connector**: Antes de procesamiento IA, después de actualizar prompts
- **documentation-specialist-HUV**: Después de milestones, antes de releases, al finalizar sprints

---

## 🔍 Troubleshooting Rápido

| Problema | Agente / Comando |
|----------|---------|
| Caso no valida correctamente | **data-auditor** FUNC-01: `python herramientas_ia/auditor_sistema.py IHQ250025 --inteligente` |
| Campo crítico vacío o mal formateado | **data-auditor** FUNC-02: `python herramientas_ia/auditor_sistema.py IHQ250025 --corregir` |
| Biomarcador "NO MAPEADO" | **data-auditor** FUNC-03: `auditor.agregar_biomarcador('CK19')` |
| Caso incompleto por biomarcadores | **data-auditor** FUNC-05: `auditor.corregir_completitud_automatica('IHQ250987')` |
| Necesito agregar biomarcador al sistema | **data-auditor** FUNC-03 (modifica 6 archivos automáticamente) |
| Biomarcador no se extrae | **data-auditor** (FUNC-01 detecta + FUNC-03 agrega + reprocesar) |
| IA no responde | **lm-studio-connector** o `python herramientas_ia/gestor_ia_lm_studio.py --estado` |
| Necesito documentar | **documentation-specialist-HUV** o `python herramientas_ia/generador_documentacion.py --interactivo` |
| Necesito actualizar versión | **documentation-specialist-HUV** o `python herramientas_ia/gestor_version.py --actualizar` |

---

## 📚 Documentación Adicional

- **Workflows completos**: [.claude/WORKFLOWS.md](.claude/WORKFLOWS.md) (workflows maestros detallados)
- **Agentes individuales**: `.claude/agents/*.md` (documentación completa de cada agente)
- **Métricas de éxito**: Ver documentación de cada agente
- **Guía de uso**: Cada herramienta tiene `--help` integrado

_Nota: inspector_sistema.py disponible para diagnóstico manual hasta futura reasignación a agente._

---

## 🎯 Métricas de Calidad

**Datos:**
- Precisión de extracción: > 95%
- Completitud promedio: > 85%
- Falsos positivos: < 3%

**Código:**
- Complejidad ciclomática: < 10
- Code smells: < 100
- Cobertura tests: > 80%

**Sistema:**
- Disponibilidad: > 99%
- Tiempo por caso: < 30s
- Uptime LM Studio: > 95%

**BD:**
- Integridad: 100%
- Duplicados: 0
- Backups: Últimos 7 días

---

**Total líneas código:** ~3,970 (4 herramientas activas)
**Total documentación:** ~2,190 líneas (3 agentes)
**Código v6.0.16:** +552 líneas (FUNC-03 + FUNC-05)
**Última actualización:** 2025-10-30
