# 📝 CHANGELOG CLAUDE - Agentes y Herramientas IA

**Propósito:** Historial de cambios de agentes y herramientas de inteligencia artificial del ecosistema EVARISIS.

**Nota:** Para cambios del programa principal (EVARISIS), ver `CHANGELOG.md`

---

## 🔍 Convenciones de Versionado

- **Agentes:** Versionados según documentación (ej. `data-auditor v3.3.0`)
- **Herramientas:** Versionadas según código fuente (ej. `auditor_sistema.py v3.1.1`)
- **CLAUDE.md:** Versionado del ecosistema completo (ej. `v6.0.16`)

---

## [Sprint EVARISIS V6.6.12 → V6.6.16] - 2026-05-04 — Diagnosis Categorization Sprint

**Orquestador:** Claude (Opus 4.7, 1M context)
**Agente delegado:** `data-auditor` (FUNC-01 auditoría inteligente, FUNC-06 reprocesamiento)
**Modo de trabajo:** quirúrgico, anti-regresión (REGLA CRÍTICA #1 de `.claude/CLAUDE.md`).

### Contexto IA
Sprint coordinado de seis fixes consecutivos sobre el normalizador de diagnósticos (`core/normalizador_diagnosticos.py`) y la lógica de malignidad (`core/extractors/medical_extractor.py`). El orquestador Claude invocó `data-auditor` para validar cada caso piloto antes y después de cada cambio, manteniendo el patrón "patrón nuevo específico ANTES + fallback genérico ORIGINAL preservado".

### Decisiones del orquestador
1. **Sin reescritura de patrones existentes.** Cada nueva categoría/regla se agregó como rama adicional o reordenamiento de prioridad; ningún patrón vigente fue eliminado.
2. **Validación 1:1 caso↔fix.** Cada versión deja en el código comentarios trazables `V6.6.XX FIX IHQYYYYY` que enlazan el cambio con el caso piloto auditado.
3. **Cierre con audit cuantitativo.** Tras V6.6.16 se ejecutó audit sobre 188 casos del rango IHQ250001-200: 0 regresiones, +23.6 pts de cobertura categorial.

### Cambios por versión (resumen para tracking IA)
| Versión | Tipo | Casos piloto | Impacto |
|---|---|---|---|
| V6.6.12 | Typo patólogo "CARICNOMA" | IHQ250060 | +1 caso |
| V6.6.13 | 5 categorías nuevas/extendidas | IHQ250071, 081, 066, 126, 107, 116 | +6 casos |
| V6.6.14 | Stripping preámbulos + reordenamientos | 13 IHQ piloto | +15 casos |
| V6.6.14b | Mini-fix RECTAL en órgano-adeno | IHQ250159 | +1 caso |
| V6.6.15 | PRIORIDAD -2 en `determine_malignancy` | IHQ250106, 065 | +2 casos (1 crítico) |
| V6.6.16 | Audit-driven mini-fixes (typo, INFLAMACIÓN, escamo-órganos) | IHQ250026, 037, 075, 061 | +4 casos |

### Validación con `data-auditor`
- 75+ auditorías individuales FUNC-01 ejecutadas sobre casos piloto.
- 54/54 self-tests del normalizador OK.
- 12/12 casos de regresión Malignidad OK.
- Audit final 188 casos: 0 regresiones, distribución MALIGNO/BENIGNO estable (73/27 → 75/25).

### Versionado
- `config/version_info.py`: `6.5.94` → `6.6.16` (`Diagnosis Categorization Sprint`).
- Documentación principal: ver entrada `[6.6.16]` en `CHANGELOG.md`.
- Bitácora ejecutiva: nueva iteración en `BITACORA_DE_ACERCAMIENTOS.md`.

---

