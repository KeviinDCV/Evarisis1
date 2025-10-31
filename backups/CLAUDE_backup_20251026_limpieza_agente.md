# 🏥 EVARISIS - Sistema Inteligente de Gestión Oncológica

**Hospital Universitario del Valle**
**Versión:** 6.0.8 | **Estado:** ✅ PRODUCCIÓN

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
1. **auditor_sistema.py** - Auditoría Inteligente + Corrección Automática
   - FUNC-01: Auditoría inteligente (validación semántica completa)
   - FUNC-02: Corrección automática con validación iterativa
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

**Cambios v6.0.8 (2025-10-26):**
- ✅ **FUNC-02 optimizada:** Modo `--usar-reporte-existente` (98% más rápido)
- ✅ **FUNC-02 reprocesamiento:** Arreglado para usar `unified_extractor` (antes fallaba)
- ✅ **FUNC-02 funcional:** Corrige datos en BD + reprocesa + re-audita (Fase 1 completa)
- ⚠️ **FUNC-02 Fase 2 pendiente:** Corrección de extractores (modificar código, no solo BD)
- 📚 **Documentación actualizada:** data-auditor.md refleja estado real de FUNC-02
- 🎯 **3 agentes especializados:** auditoría + IA + documentación

**Cambios v6.0.7 (2025-10-26):**
- ❌ Eliminado `gestor_base_datos.py` (integrado en auditor_sistema.py)
- ❌ Removido agente `core-editor` (ediciones manuales por ahora)
- 🧹 Limpiado `auditor_sistema.py`: 17 funcionalidades → 2 (FUNC-01 + FUNC-02)

---

## 🎯 Matriz Rápida de Responsabilidades

| Usuario necesita | Agente / Acción |
|------------------|--------|
| Auditar caso | **data-auditor** (FUNC-01) |
| Corregir caso automáticamente | **data-auditor** (FUNC-02) |
| Validar campos críticos, biomarcadores | **data-auditor** |
| Validar con IA, editar prompts | **lm-studio-connector** |
| Modificar código, agregar biomarcador | Edición manual (sin agente por ahora) |
| Cambiar versión, generar CHANGELOG, documentación | **documentation-specialist-HUV** |

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
- **data-auditor** → Auditoría inteligente (FUNC-01) + Corrección automática (FUNC-02)
  - FUNC-01: Valida casos desde debug_map
  - FUNC-02 (v6.0.8): Corrige datos en BD + reprocesa (parche temporal)
  - FUNC-02 (v6.1.0 futuro): Modificará extractores (corrección permanente)
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
| Biomarcador no se extrae | **data-auditor** (FUNC-01 detecta + FUNC-02 corrige automáticamente) |
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

**Total líneas código:** ~3,418 (4 herramientas activas)
**Total documentación:** ~2,000 líneas (3 agentes)
**Reducción código v6.0.7:** -3,447 líneas (50% más simple)
**Última actualización:** 2025-10-26
