# 📝 CHANGELOG CLAUDE - Agentes y Herramientas IA

**Propósito:** Historial de cambios de agentes y herramientas de inteligencia artificial del ecosistema EVARISIS.

**Nota:** Para cambios del programa principal (EVARISIS), ver `CHANGELOG.md`

---

## 🔍 Convenciones de Versionado

- **Agentes:** Versionados según documentación (ej. `data-auditor v3.3.0`)
- **Herramientas:** Versionadas según código fuente (ej. `auditor_sistema.py v3.1.1`)
- **CLAUDE.md:** Versionado del ecosistema completo (ej. `v6.0.16`)

---

## [auditor_sistema.py v3.1.1] - 2025-10-31

### 🐛 Corregido
- **FIX CRÍTICO:** Mapeo P16/P40 corregido a columnas `_ESTADO`
- Antes: `'P16'` → `'IHQ_P16'` (columna inexistente)
- Ahora: `'P16'` → `'IHQ_P16_ESTADO'` (columna real en BD)
- Antes: `'P40'` → `'IHQ_P40'` (columna inexistente)
- Ahora: `'P40'` → `'IHQ_P40_ESTADO'` (columna real en BD)

### ✅ Validado
- Resuelve: IHQ250994 y otros casos con P16/P40 no detectados como completos

---

## [auditor_sistema.py v3.1.0] - 2025-10-29

### ✅ Agregado
- **FUNC-01:** Auditoría Inteligente (validación semántica completa)
- **FUNC-03:** `agregar_biomarcador()` - Modifica automáticamente 6 archivos del sistema
  - Ubicación: línea 2313
  - Capacidad: Agrega biomarcador a database_manager, auditor_sistema, ui, validation_checker, biomarker_extractor, unified_extractor
  - Genera variantes automáticamente (ej. CK19 → CK-19, CK 19)
- **FUNC-05:** `corregir_completitud_automatica()` - Workflow inteligente end-to-end
  - Ubicación: línea 2676
  - Capacidad: Detecta biomarcadores NO MAPEADO → llama FUNC-03 → genera reporte

### 🎯 Estrategia Nueva
- Validación independiente desde OCR (sin validación circular)
- Nueva función: `_extraer_diagnostico_principal_desde_ocr()`
- Nueva función: `_extraer_diagnostico_coloracion_desde_ocr()`
- Nueva función: `_extraer_estudios_solicitados_desde_ocr()`
- Detecta placeholders ("N/A", "NO APLICA") como ERROR si OCR tiene valor
- Compara SIEMPRE BD vs OCR (fuente de verdad)

### 📊 Mejora Reportes
- Reportes incluyen `valor_bd` Y `valor_ocr` para comparación

### 📝 Backups
- Creado: `auditor_sistema_backup_20251029_pre_v3.1.0.py`

---

## [auditor_sistema.py v3.0.2] - 2025-10-26

### ✅ Agregado
- **Búsqueda flexible de biomarcadores:** Función `_buscar_columna_biomarcador()` con 3 estrategias
  1. Búsqueda exacta con sufijo `_ESTADO`
  2. Búsqueda exacta con sufijo `_PORCENTAJE`
  3. Búsqueda sin sufijo

### 🐛 Corregido
- Soluciona falsos negativos (ej. P40 → `IHQ_P40_ESTADO` ahora se detecta correctamente)

### 📝 Backups
- Creado: `auditor_sistema_backup_20251026_pre_validacion_biomarkers.py`

---

## [auditor_sistema.py v3.0.1] - 2025-10-26

### ✅ Agregado
- **Validación robusta DIAGNOSTICO_COLORACION:** 3 estrategias de validación
  1. Búsqueda exacta normalizada
  2. Búsqueda por componentes (≥80% coincidencia)
  3. Patrón flexible en descripción macroscópica
- **Normalización avanzada:** Uppercase, espacios, comillas para evitar falsos positivos

### 📚 Clarificado
- **REGLA DE ORO #1:** FACTOR_PRONOSTICO solo 4 biomarcadores principales
  - ✅ Permitidos: HER2, Ki-67, Receptor Estrógenos, Receptor Progesterona
  - ❌ Prohibidos: CKAE1AE3, S100, GATA3, TTF-1, PAX8, CDX2, E-Cadherina, P53, CD10, CD56
  - Filosofía: Si NO hay biomarcadores de pronóstico → "NO APLICA"

### 📝 Backups
- Creado: `auditor_sistema_backup_20251026_mejora_validacion.py`

---

## [auditor_sistema.py v3.0.0] - 2025-10-26

### 🧹 Limpieza Mayor
- **Eliminadas:** FUNC-02 a FUNC-17 (39 funcionalidades obsoletas)
- **Mantenido:** FUNC-01 (Auditoría Inteligente) únicamente
- **Reducción de código:** 4590 → 1144 líneas (75.1% reducción)
- **Funciones restantes:** 16 funciones

### ✅ Validado
- Sintaxis validada y funcional

### 📝 Backups
- Creado: `auditor_sistema_pre_limpieza_20251026.py`

---

## [data-auditor v3.3.0] - 2025-10-30

### 📚 Documentación Actualizada
- Documentación completa de FUNC-03 (agregar biomarcador)
- Documentación completa de FUNC-05 (workflow completitud automática)
- Workflows detallados con ejemplos de uso
- Comandos programáticos documentados

### ⚠️ Nota Importante
- La documentación menciona FUNC-02 (Corrección Automática), pero esta funcionalidad **NO está implementada** en `auditor_sistema.py v3.1.1`
- FUNC-02 está marcada como ROADMAP para futuras versiones

---

## [data-auditor v3.2.1] - 2025-10-29

### 📚 Documentación Actualizada
- Nueva sección: Lógica de DIAGNOSTICO_PRINCIPAL limpio
- Nueva sección: Lógica de DIAGNOSTICO_COLORACION con estudio M
- Función `_limpiar_diagnostico_principal()` documentada
- Validado: IHQ250992 extrae correctamente

---

## [data-auditor v3.2.0] - 2025-10-28

### 📚 Documentación Completa
- **Workflow detallado:** Agregar biomarcadores nuevos al sistema
- **REGLA DE ORO SUPREMA:** Prohibición EXPLÍCITA de modificar BD directamente
- **Checklist 5 pasos:** database_manager.py → auditor_sistema.py → ui.py → enhanced_export_system.py → enhanced_database_dashboard.py
- **Detección automática:** Cómo identificar biomarcadores no mapeados desde debug_map
- **Workflow ejemplo:** Caso completo CD38 (detección → modificación → validación)
- **Ubicaciones exactas:** Líneas, funciones y secciones específicas en cada archivo

---

## [data-auditor v3.1.5] - 2025-10-27

### 📝 Logging Mejorado
- `_obtener_debug_map()` muestra ruta completa y estado de búsqueda
- Mensajes claros con emojis visuales (🔍, ✅, ❌, 📁)
- Validación de estructura: Verifica OCR + BD antes de continuar
- Diagnóstico mejorado: Muestra directorio de búsqueda cuando falla
- Transparencia total: Reporta patrón de búsqueda y archivo encontrado

---

## [data-auditor v3.1.4] - 2025-10-26

### ✅ Agregado
- **FALLBACK AUTOMÁTICO:** Si FACTOR_PRONOSTICO vacío → construye desde columnas IHQ_*
- Búsqueda en: `IHQ_HER2`, `IHQ_KI-67`, `IHQ_RECEPTOR_ESTROGENOS`, `IHQ_RECEPTOR_PROGESTERONA`
- Integrado en `unified_extractor.py` v4.2.6

---

## [medical_extractor.py v4.2.4] - 2025-10-26

### ✅ Agregado
- **FALLBACK FACTOR_PRONOSTICO:** Función `build_factor_pronostico_from_columns()`
- Construye FACTOR_PRONOSTICO desde columnas IHQ_* si extracción directa falla
- Soluciona formatos PDF no estándar (biomarcadores fuera del bloque estándar)

### 🐛 Corregido
- Fix IHQ250984: FACTOR_PRONOSTICO construido desde columnas (HER2, Ki-67, Estrógenos, Progesterona)

---

## [medical_extractor.py v4.2.3] - 2025-10-26

### ✅ Agregado
- **Filtrado ESTRICTO FACTOR_PRONOSTICO:** Solo 4 biomarcadores de pronóstico permitidos
- Elimina tipificación tumoral de FACTOR_PRONOSTICO (CKAE1AE3, S100, GATA3, TTF-1, PAX8, CDX2)

### 🔧 Filosofía Corregida
- Si NO hay HER2/Ki-67/Estrógenos/Progesterona → "NO APLICA"
- Biomarcadores de tipificación → Solo en columnas IHQ_* individuales

### ✅ Validado
- Fix IHQ250983: P40_ESTADO detectado correctamente, FACTOR_PRONOSTICO = "NO APLICA"

---

## [medical_extractor.py v4.2.1] - 2025-10-26

### ✅ Agregado
- **Normalización automática FACTOR_PRONOSTICO durante extracción:**
  - Ki-67: Elimina "Índice de proliferación celular" (REGLA DE ORO #2)
  - HER2: Elimina "SOBREEXPRESIÓN DE", formato "HER2" (sin guión)
  - Receptores: Elimina guiones iniciales, formato estándar
- Ubicación: líneas 836-844

---

## [unified_extractor.py v4.2.6] - 2025-10-26

### ✅ Agregado
- **Integración FALLBACK automático:** Ejecuta fallback post-extracción
- Ubicación: líneas 577-595

---

## [unified_extractor.py v4.2.5] - 2025-10-26

### 🧹 Limpieza
- **DIAGNOSTICO_PRINCIPAL limpio:** Elimina datos del estudio M
- Remueve: GRADO HISTOLÓGICO, SCORE, NOTTINGHAM, INVASIÓN LINFOVASCULAR/PERINEURAL, IN SITU
- Ubicación: línea 132
- Implementa REGLA DE ORO #4

### ✅ Validado
- Fix IHQ250981: 100% validación, sin duplicación de diagnósticos

---

## [CLAUDE.md v6.0.16] - 2025-10-30

### 📚 Documentación Sistema
- Ecosistema completo documentado: 4 herramientas + 3 agentes
- Matriz de responsabilidades actualizada
- Reglas de Oro IMPLEMENTADAS (v6.0.11) documentadas
- Anti-patrones clarificados
- Workflows de coordinación entre agentes

### ⚠️ Inconsistencia Detectada
- CLAUDE.md menciona `auditor_sistema.py v3.3.0` pero código real es `v3.1.1`
- CLAUDE.md documenta FUNC-02 que no existe en código v3.1.1

---

## [CLAUDE.md v6.0.11] - 2025-10-26

### 📚 Documentación
- REGLA DE ORO #1: FACTOR_PRONOSTICO - Filtrado estricto + FALLBACK
- REGLA DE ORO #2: Ki-67 sin prefijo
- REGLA DE ORO #3: DIAGNOSTICO_COLORACION con estudio M
- REGLA DE ORO #4: DIAGNOSTICO_PRINCIPAL sin estudio M

---

## [CLAUDE.md v6.0.10] - 2025-10-26

### 📚 Documentación
- FIX CRÍTICO FACTOR_PRONOSTICO: Filtrado estricto
- FIX CRÍTICO Validación biomarcadores: Búsqueda flexible con sufijos
- Filosofía corregida: "NO APLICA" si no hay biomarcadores de pronóstico

---

## [CLAUDE.md v6.0.9] - 2025-10-26

### 📚 Documentación
- Validación robusta DIAGNOSTICO_COLORACION (3 estrategias)
- Normalización automática FACTOR_PRONOSTICO durante extracción
- Limpieza DIAGNOSTICO_PRINCIPAL (elimina datos estudio M)
- REGLAS DE ORO implementadas documentadas

---

## [CLAUDE.md v6.0.8] - 2025-10-26

### 📚 Documentación
- FUNC-02 optimizada: Modo `--usar-reporte-existente` documentado
- FUNC-02 reprocesamiento arreglado documentado
- FUNC-02 funcional (Fase 1 completa) documentado

---

## [CLAUDE.md v6.0.7] - 2025-10-26

### 🧹 Limpieza
- Eliminado `gestor_base_datos.py` de documentación (integrado en auditor_sistema.py)
- Removido agente `core-editor` (ediciones manuales temporalmente)
- Documentado: auditor_sistema.py 17 funcionalidades → 2 (FUNC-01 + FUNC-02)

---

## 📋 Resumen de Estado Actual

### ✅ Implementado en Código

| Componente | Versión | Funcionalidades |
|------------|---------|-----------------|
| `auditor_sistema.py` | v3.1.1 | FUNC-01 ✅, FUNC-03 ✅, FUNC-05 ✅ |
| `medical_extractor.py` | v4.2.4 | Filtrado estricto + FALLBACK ✅ |
| `unified_extractor.py` | v4.2.6 | Integración FALLBACK + Limpieza ✅ |

### 📚 Documentado

| Componente | Versión | Estado |
|------------|---------|--------|
| `data-auditor.md` | v3.3.0 | ⚠️ Menciona FUNC-02 no implementada |
| `CLAUDE.md` | v6.0.16 | ⚠️ Menciona `auditor_sistema.py v3.3.0` (real: v3.1.1) |

### 🚧 Roadmap (No Implementado)

- **FUNC-02:** Corrección automática iterativa en BD (documentada pero NO en código v3.1.1)
- **FUNC-05 Fase 2:** Regeneración automática BD + reprocesamiento automático
- **FUNC-03 Fase 2:** Modificación automática código Python

---

## 🔗 Referencias

- **Programa principal:** `documentacion/CHANGELOG.md`
- **Configuración versión programa:** `config/version_info.py`
- **Documentación agentes:** `.claude/agents/*.md`
- **Instrucciones Claude:** `.claude/CLAUDE.md`

---

**Última actualización:** 2025-10-31
**Mantenido por:** Claude Code
**Propósito:** Trazabilidad evolución componentes IA del ecosistema EVARISIS
