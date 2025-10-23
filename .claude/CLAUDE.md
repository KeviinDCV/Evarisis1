# 🏥 EVARISIS - Sistema Inteligente de Gestión Oncológica

**Hospital Universitario del Valle**
**Versión:** 6.0.2 | **Estado:** ✅ PRODUCCIÓN

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

### 7 Herramientas Especializadas
1. **auditor_sistema.py** - Validación completa (biomarcadores + campos críticos)
2. **gestor_base_datos.py** - Gestión y consultas de BD
3. **inspector_sistema.py** - Diagnóstico de salud del sistema
4. **editor_core.py** - Edición inteligente de código
5. **gestor_version.py** - Versionado + CHANGELOG + BITÁCORA
6. **generador_documentacion.py** - Documentación profesional
7. **gestor_ia_lm_studio.py** - Gestión LM Studio + IA

### 7 Agentes Especializados
| Agente | Herramienta | Documentación |
|--------|-------------|---------------|
| **data-auditor** | auditor_sistema.py | [.claude/agents/data-auditor.md](.claude/agents/data-auditor.md) |
| **database-manager** | gestor_base_datos.py | [.claude/agents/database-manager.md](.claude/agents/database-manager.md) |
| **system-diagnostician** | inspector_sistema.py | [.claude/agents/system-diagnostician.md](.claude/agents/system-diagnostician.md) |
| **core-editor** | editor_core.py | [.claude/agents/core-editor.md](.claude/agents/core-editor.md) |
| **lm-studio-connector** | gestor_ia_lm_studio.py | [.claude/agents/lm-studio-connector.md](.claude/agents/lm-studio-connector.md) |
| **version-manager** | gestor_version.py | [.claude/agents/version-manager.md](.claude/agents/version-manager.md) |
| **documentation-specialist-HUV** | generador_documentacion.py | [.claude/agents/documentation-specialist-HUV.md](.claude/agents/documentation-specialist-HUV.md) |

**Cada agente tiene documentación COMPLETA en su archivo .md** (capacidades, comandos, ejemplos)

---

## 🎯 Matriz Rápida de Responsabilidades

| Usuario necesita | Agente |
|------------------|--------|
| Auditar caso | **data-auditor** |
| Buscar casos, estadísticas | **database-manager** |
| Verificar salud del sistema | **system-diagnostician** |
| Modificar código, agregar biomarcador | **core-editor** |
| Validar con IA, editar prompts | **lm-studio-connector** |
| Cambiar versión, generar CHANGELOG | **version-manager** |
| Generar documentación institucional | **documentation-specialist-HUV** |

---

## 🔗 Reglas de Coordinación entre Agentes

### Validación Obligatoria
- **core-editor** → notifica a **data-auditor** después de modificar extractores
- **lm-studio-connector** → notifica a **data-auditor** después de correcciones IA

### Health Check Proactivo
- **system-diagnostician** verifica salud ANTES de:
  - Procesar lotes grandes (>10 casos)
  - Modificaciones críticas
  - Operaciones masivas de BD

### Backup Obligatorio
- **database-manager**, **lm-studio-connector**, **core-editor** → SIEMPRE crean backup en `backups/` antes de modificar

### Dry-Run Primero
- **lm-studio-connector** → SIEMPRE dry-run antes de aplicar
- **core-editor** → SIEMPRE simula antes de aplicar
- **database-manager** → SIEMPRE simula limpieza antes de aplicar

### Generación de Reportes
- **core-editor** y **lm-studio-connector** → SIEMPRE generan reporte MD en `herramientas_ia/resultados/`
- **version-manager** → lee reportes para generar CHANGELOG

### Separación de Responsabilidades
- **lm-studio-connector** → SOLO archivos IA (prompts, llm_client.py)
- **core-editor** → SOLO archivos extracción (extractors/*.py, schema BD)
- **version-manager** → SOLO CHANGELOG/BITÁCORA (acumulativos)
- **documentation-specialist-HUV** → RESTO de documentación (NO toca CHANGELOG/BITÁCORA)

---

## 🔄 Flujo de Coordinación (Claude Orquestador)

**Claude NO permite que agentes se invoquen entre sí. Claude orquesta secuencialmente:**

```
1. core-editor hace cambios
   → genera herramientas_ia/resultados/cambios_*.md
   → TERMINA

2. Claude pregunta: "¿Actualizar versión?"
   → Usuario: "Sí, v6.0.3"

3. Claude invoca version-manager
   → lee reporte de core-editor
   → actualiza VERSION_INFO
   → genera/actualiza CHANGELOG.md + BITACORA.md (acumulativos)
   → TERMINA

4. Claude pregunta: "¿Generar documentación?"
   → Usuario: "Sí"

5. Claude invoca documentation-specialist-HUV
   → lee CHANGELOG/BITACORA
   → genera documentación completa en documentacion/
   → TERMINA

6. FIN
```

---

## 🚨 Anti-Patrones (NUNCA HACER)

❌ **Modificar sin validar**
```
INCORRECTO: core-editor modifica → Usuario continúa
CORRECTO: core-editor modifica → data-auditor valida → Continuar
```

❌ **Aplicar sin dry-run**
```
INCORRECTO: lm-studio-connector aplica directamente
CORRECTO: dry-run → Usuario revisa → Aplicar
```

❌ **Crear scripts adhoc**
```
INCORRECTO: Claude crea temp_fix_ki67.py
CORRECTO: Claude usa core-editor para modificar extractor existente
```

❌ **Agente excediendo responsabilidad**
```
INCORRECTO: core-editor modifica código Y actualiza versión
CORRECTO: core-editor modifica código → version-manager actualiza versión
```

❌ **documentation-specialist generando CHANGELOG**
```
INCORRECTO: documentation-specialist genera CHANGELOG + BITACORA
CORRECTO: version-manager genera CHANGELOG/BITACORA → documentation-specialist lee para contexto
```

---

## 📈 Uso Proactivo de Agentes

**Usar SIN esperar solicitud explícita:**

- **system-diagnostician**: Antes de lotes grandes, inicio de sesión, mensualmente
- **data-auditor**: Después de procesar PDFs, después de modificaciones
- **database-manager**: Antes de operaciones críticas (backup), semanalmente (estadísticas)
- **core-editor**: Cuando data-auditor detecta patrón sistemático
- **lm-studio-connector**: Antes de procesamiento IA, después de actualizar prompts
- **documentation-specialist-HUV**: Después de milestones, antes de releases

---

## 🔍 Troubleshooting Rápido

| Problema | Comando |
|----------|---------|
| Caso no valida correctamente | `python herramientas_ia/auditor_sistema.py IHQ250025 --inteligente` |
| Sistema lento | `python herramientas_ia/inspector_sistema.py --benchmark` |
| No encuentro caso | `python herramientas_ia/gestor_base_datos.py --buscar IHQ250025` |
| Biomarcador no se extrae | `python herramientas_ia/auditor_sistema.py IHQ250025 --buscar "Ki-67"` |
| IA no responde | `python herramientas_ia/gestor_ia_lm_studio.py --estado` |
| Necesito documentar | `python herramientas_ia/generador_documentacion.py --interactivo` |

---

## 📚 Documentación Adicional

- **Workflows completos**: [.claude/WORKFLOWS.md](.claude/WORKFLOWS.md) (8 workflows maestros detallados)
- **Agentes individuales**: `.claude/agents/*.md` (documentación completa de cada agente)
- **Métricas de éxito**: Ver documentación de cada agente
- **Guía de uso**: Cada herramienta tiene `--help` integrado

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

**Total líneas código:** ~6,865 (7 herramientas)
**Total documentación:** ~3,069 líneas (7 agentes)
**Última actualización:** 2025-10-22
