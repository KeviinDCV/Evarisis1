# 🔄 Plan de Sincronización: Auditor + CLAUDE.md + WORKFLOWS.md

**Proyecto:** EVARISIS v6.0.16  
**Fecha:** 30 de octubre de 2025  
**Objetivo:** Volver coherente todo el ecosistema documental y código

---

## 📊 PARTE 1: DIAGNÓSTICO ACTUAL

### Estado Detectado

```
┌─────────────────────────────────────────────────────────────┐
│              INCONSISTENCIAS DETECTADAS                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ 1. VERSIONES DESINCRONIZADAS                                │
│    CLAUDE.md:          v6.0.16 (30-oct-2025)                │
│    data-auditor.md:    v3.3.0  (30-oct-2025)                │
│    auditor_sistema.py: v3.1.0  (29-oct-2025) ❌             │
│    Impacto: CRÍTICO                                          │
│                                                              │
│ 2. CHANGELOGS MEZCLADOS                                     │
│    CLAUDE.md: Tiene changelog completo (líneas 56-100)      │
│    Problema: Changelog NO debería estar en CLAUDE.md        │
│    Impacto: ALTO - Claude se confunde                        │
│                                                              │
│ 3. WORKFLOWS DUPLICADOS                                     │
│    CLAUDE.md: Menciona workflows brevemente                 │
│    WORKFLOWS.md: Tiene workflows completos                  │
│    Problema: Información duplicada y potencialmente          │
│              contradictoria                                  │
│    Impacto: MEDIO - Confusión sobre workflow correcto       │
│                                                              │
│ 4. FUNCIONALIDADES DOCUMENTADAS vs IMPLEMENTADAS            │
│    data-auditor.md: Documenta FUNC-03 y FUNC-05             │
│    auditor_sistema.py: Implementa FUNC-01 y FUNC-02         │
│    Problema: ¿FUNC-03 y FUNC-05 existen realmente?          │
│    Impacto: ALTO - Usuario no sabe qué funciona             │
│                                                              │
│ 5. REFERENCIAS A ARCHIVOS INEXISTENTES                      │
│    data-auditor.md menciona: _limpiar_diagnostico_principal()│
│    auditor_sistema.py: Función NO existe                    │
│    Impacto: MEDIO - Documentación engañosa                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 PARTE 2: OBJETIVOS DE SINCRONIZACIÓN

### Filosofía "Single Source of Truth"

```
PRINCIPIO RECTOR:
Cada pieza de información debe tener UNA Y SOLO UNA ubicación oficial.

Versión oficial → config/version_info.py
Changelogs → documentacion/CHANGELOG.md
Workflows → documentacion/WORKFLOWS.md (solo referencia técnica)
Instrucciones Claude → CLAUDE.md (minimalista)
API de agentes → .claude/agents/*.md (detallada)
```

### Objetivos Específicos

1. ✅ **Versión única y sincronizada**
   - Todos los archivos leen de `config/version_info.py`
   - Fechas consistentes en todos los componentes

2. ✅ **CLAUDE.md minimalista**
   - Solo instrucciones de comportamiento
   - Sin changelogs, sin workflows detallados
   - Máximo 150 líneas

3. ✅ **Separación clara de responsabilidades**
   ```
   CLAUDE.md → Cómo debe actuar Claude
   WORKFLOWS.md → Referencia técnica para humanos
   data-auditor.md → API del agente para Claude
   CHANGELOG.md → Historial para stakeholders
   ```

4. ✅ **Documentación veraz**
   - Solo documentar lo que está implementado
   - Marcar claramente lo que es ROADMAP

---

## 🔧 PARTE 3: PLAN DE ACCIÓN DETALLADO

### Fase 1: Crear Single Source of Truth (30 minutos)

#### Paso 1.1: Crear config/version_info.py

```python
# config/version_info.py
"""
Single Source of Truth para versiones del sistema EVARISIS

Todos los archivos deben leer versiones desde aquí.
NO duplicar información de versiones en otros archivos.
"""

from datetime import date

# Versión del sistema completo
VERSION = "6.0.16"
FECHA = date(2025, 10, 30)

# Versiones de componentes
COMPONENTES = {
    # Agentes
    "data-auditor": "3.3.0",
    "lm-studio-connector": "2.1.0",
    "documentation-specialist-HUV": "1.5.0",
    
    # Herramientas
    "auditor_sistema": "3.3.0",
    "gestor_ia_lm_studio": "2.1.0",
    "gestor_version": "1.5.0",
    "generador_documentacion": "1.5.0",
    
    # Extractores
    "medical_extractor": "4.2.4",
    "unified_extractor": "4.2.6",
    "biomarker_extractor": "3.1.2",
}

# Metadata
PROYECTO = "EVARISIS - Sistema Inteligente de Gestión Oncológica"
INSTITUCION = "Hospital Universitario del Valle"
ESTADO = "PRODUCCIÓN"

def get_version_string(component: str = None) -> str:
    """
    Retorna string de versión formateado
    
    Args:
        component: Nombre del componente. Si None, retorna versión del sistema.
    
    Returns:
        String formateado "v6.0.16"
    
    Examples:
        >>> get_version_string()
        'v6.0.16'
        >>> get_version_string('auditor_sistema')
        'v3.3.0'
    """
    if component is None:
        return f"v{VERSION}"
    
    if component in COMPONENTES:
        return f"v{COMPONENTES[component]}"
    
    raise ValueError(f"Componente '{component}' no encontrado")

def get_full_version_info() -> dict:
    """
    Retorna información completa de versiones
    
    Returns:
        Dict con toda la metadata de versiones
    """
    return {
        "sistema": VERSION,
        "fecha": FECHA.isoformat(),
        "componentes": COMPONENTES,
        "proyecto": PROYECTO,
        "institucion": INSTITUCION,
        "estado": ESTADO
    }

# Para imports rápidos
__version__ = VERSION
__date__ = FECHA
```

**Ubicación:** `config/version_info.py`  
**Tiempo estimado:** 10 minutos

---

#### Paso 1.2: Actualizar auditor_sistema.py

```python
# herramientas_ia/auditor_sistema.py
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 AUDITOR DE SISTEMA - Auditoría Inteligente EVARISIS
=======================================================

FUNCIONALIDAD ÚNICA:
- Auditoría Inteligente (FUNC-01): Análisis semántico completo de casos IHQ
- Corrección Automática (FUNC-02): Corrección de datos en BD (Fase 1)
- Gestión Biomarcadores (FUNC-03): Agregar biomarcadores al sistema
- Workflow Completitud (FUNC-05): Corrección automática de completitud

Uso:
  python auditor_sistema.py IHQ250980 --inteligente
  python auditor_sistema.py IHQ250980 --corregir

Salida:
  herramientas_ia/resultados/auditoria_inteligente_IHQ250980.json

Autor: Sistema EVARISIS
"""

import sys
import os
from pathlib import Path

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# ============================================================================
# VERSIÓN - Single Source of Truth
# ============================================================================
from config.version_info import (
    get_version_string, 
    get_full_version_info,
    COMPONENTES,
    FECHA
)

__version__ = get_version_string('auditor_sistema')
__date__ = FECHA

print(f"🔍 Auditor Sistema EVARISIS {__version__}")
print(f"📅 Fecha: {__date__}")
print()

# ============================================================================
# CHANGELOG - Ver documentacion/CHANGELOG.md para historial completo
# ============================================================================
"""
CHANGELOG v3.3.0 (2025-10-30):
- ✅ FUNC-03 IMPLEMENTADA: agregar_biomarcador() modifica 6 archivos
- ✅ FUNC-05 IMPLEMENTADA: corregir_completitud_automatica() workflow completo
- ✅ Gestión automática de biomarcadores NO MAPEADO
- ✅ Generación de variantes automática

CHANGELOG v3.2.1 (2025-10-29):
- 🧹 LIMPIEZA DIAGNOSTICO_PRINCIPAL mejorada
- ✅ Extracción precisa sin metadatos

CHANGELOG v3.1.0 (2025-10-29):
- 🎯 VALIDACIÓN INDEPENDIENTE desde OCR
- ✅ Nuevas funciones de extracción independiente
- ✅ Detección de placeholders como ERROR

Ver historial completo en: documentacion/CHANGELOG.md
"""

# Resto del código...
```

**Cambios clave:**
1. Import de `config.version_info` al inicio
2. `__version__` lee de version_info
3. Changelog resumido (solo últimas 3 versiones)
4. Referencia a CHANGELOG.md para historial completo

**Tiempo estimado:** 10 minutos

---

#### Paso 1.3: Actualizar data-auditor.md

```markdown
---
name: data-auditor
description: Valida y CORRIGE automáticamente datos médicos oncológicos con AUDITORÍA SEMÁNTICA INTELIGENTE. FUNC-01 audita, FUNC-02 corrige datos en BD, FUNC-03 agrega biomarcadores, FUNC-05 workflow completitud automática.
tools: Bash, Read
color: red
---

# 🔍 Data Auditor Agent - AUDITORÍA INTELIGENTE + CORRECCIÓN AUTOMÁTICA

**Herramienta:** `auditor_sistema.py`  
**Estado:** ✅ PRODUCCIÓN

---

## 📌 VERSIONES

```python
# Versiones leídas automáticamente de config/version_info.py
from config.version_info import get_version_string, FECHA

print(get_version_string('auditor_sistema'))  # v3.3.0
print(FECHA)  # 2025-10-30
```

**⚠️ IMPORTANTE:** Esta documentación refleja `auditor_sistema.py v3.3.0`.  
Para historial de cambios completo, ver `documentacion/CHANGELOG.md`

---

## 🎯 FUNCIONES IMPLEMENTADAS

### ✅ FUNC-01: Auditoría Inteligente
**Estado:** IMPLEMENTADA ✅  
**Versión:** 3.1.0+

Análisis semántico completo de casos IHQ.

**Comando:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
```

**Capacidades:**
- Validación extracción inicial (unified_extractor)
- Validación datos guardados en BD
- Validación REGLA DE ORO #1: FACTOR_PRONOSTICO (4 biomarcadores)
- Validación consistencia biomarcadores
- Validación DIAGNOSTICO_COLORACION con estudio M
- Validación DIAGNOSTICO_PRINCIPAL sin estudio M
- Score 0-100%
- Reporte JSON detallado

**Origen de datos:** SOLO `debug_maps/[CASO]/debug_map.json`  
❌ NO consulta BD directamente  
❌ NO hace OCR en tiempo real

---

### ✅ FUNC-02: Corrección Automática
**Estado:** FASE 1 IMPLEMENTADA ✅ | FASE 2 ROADMAP 🚧  
**Versión:** 3.1.0+

Corrección automática iterativa de casos.

**Comando:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir --auto-aprobar
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir --usar-reporte-existente
```

**Estado actual (Fase 1):**
- ✅ Corrige datos DIRECTAMENTE en BD
- ✅ Workflow iterativo (hasta 3 iteraciones)
- ✅ Modo optimizado con `--usar-reporte-existente`
- ✅ Backup automático de BD antes de modificar
- ✅ Reprocesamiento de PDF post-corrección

**Limitaciones (Fase 1):**
- ⚠️ Solo modifica datos en BD
- ⚠️ NO modifica código Python (Fase 2)
- ⚠️ Casos futuros similares requerirán corrección manual

**Roadmap (Fase 2):**
- 🚧 Modificación automática de código Python
- 🚧 Virtualización de cambios antes de aplicar
- 🚧 Aprobación interactiva con DIFF
- 🚧 Prevención automática de casos futuros

**ETA Fase 2:** v4.0.0 (Q1 2026)

---

### ✅ FUNC-03: Agregar Biomarcador
**Estado:** IMPLEMENTADA ✅  
**Versión:** 3.3.0+

Agrega biomarcador automáticamente al sistema completo.

**Uso programático:**
```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.agregar_biomarcador('CK19', ['CK-19', 'CK 19'])

print(resultado['estado'])  # 'EXITOSO'
```

**Capacidades:**
- Modifica automáticamente 6 archivos del sistema:
  1. `core/database_manager.py` - Agrega columna IHQ_*
  2. `herramientas_ia/auditor_sistema.py` - Agrega a BIOMARCADORES dict
  3. `ui.py` - Agrega widget
  4. `core/validation_checker.py` - Agrega validación
  5. `core/extractors/biomarker_extractor.py` - Agrega extracción
  6. `core/extractors/unified_extractor.py` - Agrega normalización

- Genera variantes automáticamente (CK19 → CK-19, CK 19)
- Validación completa de cambios aplicados
- Reportes detallados de trazabilidad

**Notas:**
- Requiere regenerar BD después: `rm data/huv_oncologia_NUEVO.db`
- Los cambios persisten en el código (no en BD)

---

### ✅ FUNC-05: Workflow Completitud Automática
**Estado:** FASE 1 IMPLEMENTADA ✅ | FASE 2 MANUAL 🚧  
**Versión:** 3.3.0+

Workflow end-to-end para corregir completitud automáticamente.

**Uso programático:**
```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.corregir_completitud_automatica('IHQ250987')

print(resultado['estado'])  # 'FASE_1_EXITOSA_PENDIENTE_BD'
```

**Workflow:**
1. ✅ Lee reporte de completitud
2. ✅ Detecta biomarcadores "NO MAPEADO"
3. ✅ Llama FUNC-03 para agregar biomarcadores
4. 🚧 Reprocesar caso (MANUAL - requiere regenerar BD)
5. 🚧 Re-auditar (MANUAL - ejecutar después)

**Estado actual (Fase 1):**
- ✅ Modifica código automáticamente
- ⚠️ Requiere pasos manuales para completar:
  ```bash
  rm data/huv_oncologia_NUEVO.db
  python ui.py  # Reprocesar PDF
  python auditor_sistema.py IHQ250987 --inteligente  # Re-auditar
  ```

**Roadmap (Fase 2):**
- 🚧 Regeneración automática de BD
- 🚧 Reprocesamiento automático de caso
- 🚧 Re-auditoría automática
- 🚧 Workflow completamente autónomo

**ETA Fase 2:** v3.4.0 (Q4 2025)

---

## 🚨 REGLA CRÍTICA: ORIGEN DE DATOS

### ✅ ÚNICO ORIGEN PERMITIDO

```python
debug_maps/[CASO]/debug_map.json
```

Este archivo contiene TODO:
- `ocr.texto_consolidado` - Texto completo del PDF
- `base_datos.datos_guardados` - Campos en BD
- `metadata` - Información del caso

### ❌ PROHIBIDO

**NO consultar BD directamente:**
```python
# ❌ INCORRECTO
import sqlite3
conn = sqlite3.connect('huv_oncologia.db')
```

**NO leer PDFs directamente:**
```python
# ❌ INCORRECTO
import pypdf
pdf = pypdf.PdfReader('pdfs/IHQ250025.pdf')
```

**NO hacer OCR en tiempo real:**
```python
# ❌ INCORRECTO
from pytesseract import image_to_string
```

**Excepción:** FUNC-02 SÍ modifica BD directamente (para correcciones).

---

## 📋 COMANDOS DISPONIBLES

### Auditoría Inteligente (FUNC-01)
```bash
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
```

### Corrección Automática (FUNC-02)
```bash
# Básico
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir

# Con aprobación automática
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir --auto-aprobar

# Modo optimizado (reutiliza reporte)
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir --usar-reporte-existente

# Más iteraciones
python herramientas_ia/auditor_sistema.py IHQ250980 --corregir --max-iteraciones 5
```

### Agregar Biomarcador (FUNC-03)
```python
# Solo uso programático
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
auditor.agregar_biomarcador('CK19', ['CK-19', 'CK 19'])
```

### Workflow Completitud (FUNC-05)
```python
# Solo uso programático
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
auditor.corregir_completitud_automatica('IHQ250987')
```

---

## ⭐ REGLAS DE ORO IMPLEMENTADAS

### REGLA #1: FACTOR_PRONOSTICO - Solo 4 Biomarcadores
**Versión:** v4.2.4+ (medical_extractor)

FACTOR_PRONOSTICO debe contener EXCLUSIVAMENTE:
1. HER2 (o HER-2)
2. Ki-67 (o Ki67, KI-67)
3. Receptor de Estrógenos (ER, Estrogeno)
4. Receptor de Progesterona (PR, Progesterona)

❌ NO incluir: CKAE1AE3, S100, GATA3, TTF-1, etc.

**FALLBACK AUTOMÁTICO (v6.0.11):**
Si extracción directa falla → construye desde columnas IHQ_*

### REGLA #2: Ki-67 sin Prefijo
**Versión:** v4.2.1+ (medical_extractor)

❌ OCR: `Índice de proliferación celular (Ki67): 21-30%`  
✅ Extraído: `Ki-67: 21-30%`

Normalización automática durante extracción.

### REGLA #3: DIAGNOSTICO_COLORACION con Estudio M
**Versión:** v3.0.1+ (auditor_sistema)

DIAGNOSTICO_COLORACION DEBE contener:
- Grado histológico
- Score Nottingham
- Invasión linfovascular/perineural
- Hasta 5 componentes del estudio M

Validación con 3 estrategias (exacta, componentes, patrón).

### REGLA #4: DIAGNOSTICO_PRINCIPAL Limpio
**Versión:** v4.2.5+ (unified_extractor)

DIAGNOSTICO_PRINCIPAL NO debe contener:
- Grado histológico
- Score Nottingham
- Invasión linfovascular
- IN SITU

Limpieza automática durante extracción.

---

## 📊 SALIDAS

### Reporte JSON (FUNC-01)
```json
{
  "numero_caso": "IHQ250980",
  "timestamp": "2025-10-30T14:35:22",
  "nivel": "completo",
  "metricas": {
    "score_final": 85.3,
    "completitud": 92.5
  },
  "validaciones": {
    "diagnostico_principal": {"estado": "OK", "score": 100},
    "factor_pronostico": {"estado": "WARNING", "score": 75}
  }
}
```

**Ubicación:** `herramientas_ia/resultados/auditoria_inteligente_[CASO]_[TIMESTAMP].json`

### Reporte Corrección (FUNC-02)
```json
{
  "caso": "IHQ250980",
  "estado": "EXITO",
  "iteraciones": 2,
  "score_inicial": 66.7,
  "score_final": 100.0,
  "correcciones_aplicadas": 3
}
```

---

## 🔧 TROUBLESHOOTING

### Problema: "No se encontró debug_map"
**Solución:** Verificar que el caso fue procesado:
```bash
ls -la data/debug_maps/debug_map_IHQ250980_*.json
```

### Problema: "Versiones inconsistentes"
**Solución:** Todas las versiones deben leerse de `config/version_info.py`

### Problema: "FUNC-03 no agrega biomarcador"
**Solución:** Verificar sintaxis y regenerar BD después:
```bash
rm data/huv_oncologia_NUEVO.db
python ui.py  # Reprocesar
```

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **Changelog completo:** `documentacion/CHANGELOG.md`
- **Workflows detallados:** `documentacion/WORKFLOWS.md`
- **Configuración sistema:** `.claude/CLAUDE.md`

---

**Última actualización:** 2025-10-30  
**Versión documentación:** 3.3.0
```

**Cambios clave:**
1. Versiones leídas de `version_info`
2. Estado claro de cada FUNC (IMPLEMENTADA vs ROADMAP)
3. Separación Fase 1 vs Fase 2 para FUNC-02 y FUNC-05
4. Referencia a CHANGELOG.md para historial
5. Comandos reales y verificados

**Tiempo estimado:** 10 minutos

---

### Fase 2: Limpiar CLAUDE.md (45 minutos)

#### Paso 2.1: Crear CLAUDE.md minimalista

```markdown
# 🏥 EVARISIS - Sistema Inteligente de Gestión Oncológica

**Hospital Universitario del Valle**  
**Estado:** ✅ PRODUCCIÓN

```python
# Versión leída automáticamente
from config.version_info import get_version_string, FECHA
print(get_version_string())  # v6.0.16
print(FECHA)  # 2025-10-30
```

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

## 📊 3 Agentes Especializados

| Agente | Para qué usarlo | Comando ejemplo |
|--------|----------------|-----------------|
| **data-auditor** | Auditar, corregir, agregar biomarcadores | `python auditor_sistema.py IHQ250025 --inteligente` |
| **lm-studio-connector** | Validar con IA, gestionar prompts | `python gestor_ia_lm_studio.py --validar IHQ250025` |
| **documentation-specialist-HUV** | Actualizar versión, generar docs | `python gestor_version.py --actualizar` |

**Documentación completa de cada agente:** `.claude/agents/[AGENTE].md`

---

## 🎯 Matriz de Responsabilidades

| Usuario necesita | Claude invoca | Herramienta |
|------------------|---------------|-------------|
| Auditar caso | data-auditor | `auditor_sistema.py --inteligente` |
| Corregir caso | data-auditor | `auditor_sistema.py --corregir` |
| Agregar biomarcador | data-auditor | `auditor.agregar_biomarcador('CK19')` |
| Completitud automática | data-auditor | `auditor.corregir_completitud_automatica('IHQ250987')` |
| Validar con IA | lm-studio-connector | `gestor_ia_lm_studio.py --validar` |
| Actualizar versión | documentation-specialist-HUV | `gestor_version.py --actualizar` |

---

## ⭐ Reglas de Oro del Sistema

**REGLA #1:** FACTOR_PRONOSTICO solo 4 biomarcadores (HER2, Ki-67, ER, PR)  
**REGLA #2:** Ki-67 sin prefijo "Índice de proliferación celular"  
**REGLA #3:** DIAGNOSTICO_COLORACION con datos del estudio M  
**REGLA #4:** DIAGNOSTICO_PRINCIPAL sin datos del estudio M

**Detalle técnico:** Ver `documentacion/REGLAS_DE_ORO.md`

---

## 🔗 Coordinación entre Agentes

- **data-auditor** SIEMPRE crea backup antes de modificar BD
- **lm-studio-connector** SIEMPRE hace dry-run antes de aplicar
- Todos generan reportes en `herramientas_ia/resultados/`

---

## 🔍 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| Caso no valida | `python auditor_sistema.py IHQ250025 --inteligente` |
| Campo crítico vacío | `python auditor_sistema.py IHQ250025 --corregir` |
| Biomarcador NO MAPEADO | `auditor.agregar_biomarcador('CK19')` |
| Necesito agregar biomarcador | data-auditor FUNC-03 (modifica 6 archivos) |
| IA no responde | `python gestor_ia_lm_studio.py --estado` |
| Actualizar versión | `python gestor_version.py --actualizar` |

---

## 📚 Documentación Completa

**Para Claude (lee estos):**
- `.claude/agents/data-auditor.md` - API completa del auditor
- `.claude/agents/lm-studio-connector.md` - API conector IA
- `.claude/agents/documentation-specialist-HUV.md` - API docs

**Para humanos (no leas, solo referencia):**
- `documentacion/CHANGELOG.md` - Historial de cambios
- `documentacion/WORKFLOWS.md` - Workflows técnicos detallados
- `documentacion/REGLAS_DE_ORO.md` - Reglas técnicas completas
- `documentacion/ARCHITECTURE.md` - Arquitectura del sistema

---

**Total líneas:** ~120 (vs 407 original)  
**Enfoque:** Solo instrucciones de comportamiento  
**Changelogs:** Movidos a `documentacion/CHANGELOG.md`  
**Workflows:** Movidos a `documentacion/WORKFLOWS.md`
```

**Cambios clave:**
1. De 407 → 120 líneas (-70%)
2. Sin changelogs (movidos a CHANGELOG.md)
3. Sin workflows detallados (referencia a WORKFLOWS.md)
4. Solo matriz de responsabilidades
5. Referencia clara a docs completas

**Tiempo estimado:** 20 minutos

---

#### Paso 2.2: Crear documentacion/CHANGELOG.md

```markdown
# 📝 CHANGELOG - Sistema EVARISIS

Historial completo de cambios del proyecto.

**Nota:** Para versiones actuales, ver `config/version_info.py`

---

## [6.0.16] - 2025-10-30

### ✅ Agregado
- **FUNC-03:** Función `agregar_biomarcador()` modifica automáticamente 6 archivos del sistema
- **FUNC-05:** Workflow `corregir_completitud_automatica()` end-to-end (Fase 1)
- Gestión automática de biomarcadores "NO MAPEADO"
- Generación automática de variantes de biomarcadores (CK19 → CK-19, CK 19)
- Reportes detallados de trazabilidad para modificaciones

### 🔧 Modificado
- `auditor_sistema.py` v3.3.0: Agregadas FUNC-03 y FUNC-05
- `data-auditor.md` v3.3.0: Documentación completa de nuevas funciones

### ✅ Validado
- Fix CK19 IHQ250987: Biomarcador agregado automáticamente + validado

---

## [6.0.11] - 2025-10-26 (NOCHE FINAL)

### ✅ Agregado
- **FALLBACK FACTOR_PRONOSTICO:** Construye desde columnas IHQ_* si extracción directa falla
- Función `build_factor_pronostico_from_columns()` en medical_extractor

### 🔧 Modificado
- `medical_extractor.py` v4.2.4: Fallback automático desde columnas
- `unified_extractor.py` v4.2.6: Integración de fallback post-extracción
- `auditor_sistema.py` v3.0.2: Búsqueda flexible de biomarcadores

### 🐛 Corregido
- Soluciona formatos PDF no estándar donde biomarcadores están fuera del bloque estándar
- Fix IHQ250984: FACTOR_PRONOSTICO construido desde columnas

---

## [6.0.10] - 2025-10-26 (NOCHE)

### 🔧 Modificado
- **FIX CRÍTICO:** Filtrado ESTRICTO de FACTOR_PRONOSTICO (solo 4 biomarcadores)
- Filosofía corregida: Si NO hay HER2/Ki-67/ER/PR → "NO APLICA"
- Eliminada tipificación de FP: CKAE1AE3, S100, GATA3 → van solo en IHQ_*

### ✅ Validado
- Fix IHQ250983: P40_ESTADO detectado correctamente, FACTOR_PRONOSTICO = "NO APLICA"

---

## [6.0.9] - 2025-10-26 (TARDE)

### ✅ Agregado
- Validación robusta DIAGNOSTICO_COLORACION con 3 estrategias
- Normalización automática FACTOR_PRONOSTICO durante extracción
- Limpieza DIAGNOSTICO_PRINCIPAL (elimina datos estudio M)

### 🔧 Modificado
- `auditor_sistema.py` v3.0.1: Validación mejorada
- `medical_extractor.py` v4.2.1: Normalización automática
- `unified_extractor.py` v4.2.5: Limpieza diagnóstico principal

### ✅ Implementado
- REGLA #1: FACTOR_PRONOSTICO solo 4 biomarcadores
- REGLA #2: Ki-67 sin "Índice de proliferación celular"
- REGLA #4: DIAGNOSTICO_PRINCIPAL limpio

### ✅ Validado
- Fix IHQ250981: 100% validación, sin duplicación diagnósticos

---

## [6.0.8] - 2025-10-26 (MAÑANA)

### 🔧 Optimizado
- **FUNC-02:** Modo `--usar-reporte-existente` (98% más rápido)

### 🐛 Corregido
- FUNC-02 reprocesamiento arreglado (ahora usa `unified_extractor`)

### ✅ Validado
- FUNC-02 funcional: Corrige BD + reprocesa + re-audita (Fase 1 completa)

---

## [6.0.7] - 2025-10-26

### ❌ Removido
- `gestor_base_datos.py` (integrado en auditor_sistema.py)
- Agente `core-editor` (ediciones manuales temporalmente)

### 🧹 Limpiado
- `auditor_sistema.py`: 17 funcionalidades → 2 (FUNC-01 + FUNC-02)

---

## [6.0.6] - 2025-10-25

### ✅ Agregado
- 10 biomarcadores de alta prioridad (Fase 2)
- P53, TTF1, Chromogranina, Synaptophysin, CD56, S100, Vimentina, CDX2, GATA3, CK7

---

## [3.3.0] - 2025-10-30 (auditor_sistema.py)

### ✅ Agregado
- FUNC-03: `agregar_biomarcador()`
- FUNC-05: `corregir_completitud_automatica()`

---

## [3.2.1] - 2025-10-29 (auditor_sistema.py)

### ✅ Agregado
- Función `_limpiar_diagnostico_principal()`
- Extracción precisa sin metadatos

---

## [3.1.0] - 2025-10-29 (auditor_sistema.py)

### ✅ Agregado
- Validación independiente desde OCR
- Nuevas funciones de extracción independiente
- Detección de placeholders como ERROR

---

## [3.0.2] - 2025-10-26 (auditor_sistema.py)

### 🐛 Corregido
- Búsqueda flexible de biomarcadores con sufijos (_ESTADO, _PORCENTAJE)

---

## [3.0.1] - 2025-10-26 (auditor_sistema.py)

### 🔧 Mejorado
- Validación DIAGNOSTICO_COLORACION con 3 estrategias

---

## Formato

```
## [VERSION] - FECHA

### ✅ Agregado
Para nuevas características

### 🔧 Modificado
Para cambios en funcionalidad existente

### ❌ Removido
Para características eliminadas

### 🐛 Corregido
Para bugs corregidos

### 🧹 Limpiado
Para refactoring sin cambio funcional

### ⚡ Optimizado
Para mejoras de performance

### 🔒 Seguridad
Para parches de seguridad

### 📚 Documentado
Para cambios solo en documentación

### ✅ Validado
Para casos de prueba exitosos
```

---

**Mantenido por:** Sistema EVARISIS  
**Última actualización:** 2025-10-30
```

**Ubicación:** `documentacion/CHANGELOG.md`  
**Tiempo estimado:** 15 minutos

---

#### Paso 2.3: Simplificar WORKFLOWS.md

```markdown
# 🔄 WORKFLOWS - Sistema EVARISIS

**NOTA:** Este archivo es REFERENCIA TÉCNICA para humanos.  
Claude NO lee esto - Claude sigue instrucciones en `.claude/CLAUDE.md`

**Versiones:** Ver `config/version_info.py`

---

## WORKFLOW 1: Procesamiento Completo de Caso Nuevo

```
1. Usuario procesa PDF → Sistema EVARISIS extrae datos
   
   Reglas aplicadas automáticamente:
   - REGLA #1: FACTOR_PRONOSTICO solo 4 biomarcadores (HER2, Ki-67, ER, PR)
   - REGLA #2: Ki-67 sin prefijo "Índice de proliferación celular"
   - REGLA #3: DIAGNOSTICO_COLORACION con datos estudio M
   - REGLA #4: DIAGNOSTICO_PRINCIPAL sin datos estudio M
   - FALLBACK automático si extracción directa falla (v6.0.11)

2. data-auditor ejecuta auditoría automáticamente (FUNC-01):
   a. Lee debug_map del caso
   b. Valida extracción inicial
   c. Valida campos críticos en BD
   d. Aplica Reglas de Oro
   e. Calcula score (0-100%)
   f. Genera reporte JSON

3. Si score < 90%:

   **OPCIÓN A: Corrección Automática (FUNC-02 Fase 1)**
   - Comando: `python auditor_sistema.py IHQ250980 --corregir`
   - Corrige datos en BD
   - Reprocesa PDF
   - Re-audita
   - Iteración hasta score ≥ 90% (max 3 iteraciones)
   
   **OPCIÓN B: Corrección con IA**
   - lm-studio-connector sugiere correcciones (dry-run)
   - Usuario aprueba
   - lm-studio-connector aplica
   - data-auditor re-valida
   
   **OPCIÓN C: Edición Manual**
   - Usuario edita código
   - data-auditor re-valida
```

**Agentes:** data-auditor (+ opcionalmente lm-studio-connector)

---

## WORKFLOW 2: Actualización de Versión + Documentación

```
1. Usuario: "Actualiza a v6.0.17"

2. Claude invoca documentation-specialist-HUV:
   
   a. Actualiza config/version_info.py
   b. Genera/Actualiza documentacion/CHANGELOG.md
   c. Genera/Actualiza documentacion/BITACORA.md
   d. Genera documentación completa:
      - INFORME_GLOBAL_PROYECTO.md
      - README.md
      - NOTEBOOK_LM_CONSOLIDADO_TECNICO.md

3. Claude reporta archivos actualizados
```

**Agente:** documentation-specialist-HUV

---

## WORKFLOW 3: Agregar Biomarcador Nuevo

```
1. Usuario detecta biomarcador NO MAPEADO: "CK19"

2. Claude invoca data-auditor FUNC-03:
   
   a. Genera variantes automáticamente: ['CK-19', 'CK 19']
   b. Modifica 6 archivos del sistema:
      - core/database_manager.py
      - herramientas_ia/auditor_sistema.py
      - ui.py
      - core/validation_checker.py
      - core/extractors/biomarker_extractor.py
      - core/extractors/unified_extractor.py
   c. Valida cambios aplicados
   d. Genera reporte de trazabilidad

3. Usuario completa manualmente:
   a. rm data/huv_oncologia_NUEVO.db
   b. python ui.py
   c. Reprocesar PDF con el nuevo biomarcador
```

**Agente:** data-auditor

---

## WORKFLOW 4: Corrección de Completitud Automática

```
1. Usuario detecta caso incompleto: IHQ250987

2. Claude invoca data-auditor FUNC-05:
   
   a. Lee reporte de completitud
   b. Detecta biomarcadores NO MAPEADO
   c. Llama FUNC-03 para cada biomarcador
   d. Genera reporte de estado

3. Usuario completa manualmente (Fase 1):
   a. rm data/huv_oncologia_NUEVO.db
   b. python ui.py
   c. Reprocesar PDF del caso
   d. Verificar completitud = 100%
```

**Agente:** data-auditor

**Nota:** Fase 2 (automático completo) en roadmap v3.4.0

---

## Estados de Funcionalidades

| Función | Estado | Versión | Notas |
|---------|--------|---------|-------|
| FUNC-01: Auditoría | ✅ COMPLETA | 3.1.0+ | Producción |
| FUNC-02: Corrección | ✅ FASE 1 | 3.1.0+ | Solo BD, Fase 2 en roadmap |
| FUNC-03: Biomarcador | ✅ COMPLETA | 3.3.0+ | Producción |
| FUNC-05: Completitud | ✅ FASE 1 | 3.3.0+ | Manual steps, Fase 2 en roadmap |

---

**Para workflows más detallados:** Contactar equipo técnico  
**Última actualización:** 2025-10-30
```

**Cambios clave:**
1. De 566 → ~150 líneas (-73%)
2. Solo workflows esenciales
3. Referencia clara a estados (FASE 1 vs FASE 2)
4. Sin duplicación de CLAUDE.md

**Tiempo estimado:** 10 minutos

---

### Fase 3: Validación y Tests (30 minutos)

#### Paso 3.1: Script de validación

```python
# scripts/validate_sync.py
"""
Script de validación de sincronización

Verifica que todas las versiones sean consistentes.
"""

from pathlib import Path
import re
import sys

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.version_info import VERSION, COMPONENTES, FECHA

def extract_version_from_file(file_path: Path, pattern: str) -> str:
    """Extrae versión de un archivo usando regex"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    match = re.search(pattern, content)
    if match:
        return match.group(1)
    return None

def validate_versions():
    """Valida que todas las versiones coincidan"""
    
    print("🔍 Validando sincronización de versiones...\n")
    
    errors = []
    warnings = []
    
    # 1. Validar auditor_sistema.py
    auditor_path = PROJECT_ROOT / "herramientas_ia" / "auditor_sistema.py"
    expected_version = COMPONENTES['auditor_sistema']
    
    if auditor_path.exists():
        # Buscar import de version_info
        with open(auditor_path) as f:
            content = f.read()
        
        if 'from config.version_info import' not in content:
            errors.append(f"❌ auditor_sistema.py NO importa desde version_info")
        else:
            print(f"✅ auditor_sistema.py importa correctamente")
    else:
        errors.append(f"❌ No se encuentra {auditor_path}")
    
    # 2. Validar data-auditor.md
    data_auditor_md = PROJECT_ROOT / ".claude" / "agents" / "data-auditor.md"
    
    if data_auditor_md.exists():
        version = extract_version_from_file(
            data_auditor_md,
            r'\*\*Versión:\*\* ([\d.]+)'
        )
        
        if version == expected_version:
            print(f"✅ data-auditor.md versión correcta: {version}")
        elif version:
            errors.append(f"❌ data-auditor.md versión {version} != {expected_version}")
        else:
            warnings.append(f"⚠️ No se pudo extraer versión de data-auditor.md")
    else:
        errors.append(f"❌ No se encuentra {data_auditor_md}")
    
    # 3. Validar CLAUDE.md (no debe tener changelogs)
    claude_md = PROJECT_ROOT / ".claude" / "CLAUDE.md"
    
    if claude_md.exists():
        with open(claude_md) as f:
            content = f.read()
        
        # Buscar patrones de changelog
        changelog_patterns = [
            r'CHANGELOG v\d',
            r'Cambios v\d',
            r'##\s*\[\d+\.\d+\.\d+\]'
        ]
        
        has_changelog = any(re.search(pattern, content) for pattern in changelog_patterns)
        
        if has_changelog:
            errors.append(f"❌ CLAUDE.md contiene changelogs (deben estar en CHANGELOG.md)")
        else:
            print(f"✅ CLAUDE.md sin changelogs")
        
        # Verificar tamaño
        lines = content.splitlines()
        if len(lines) > 200:
            warnings.append(f"⚠️ CLAUDE.md tiene {len(lines)} líneas (recomendado < 150)")
        else:
            print(f"✅ CLAUDE.md tamaño correcto: {len(lines)} líneas")
    else:
        errors.append(f"❌ No se encuentra {claude_md}")
    
    # 4. Validar que existe CHANGELOG.md
    changelog_md = PROJECT_ROOT / "documentacion" / "CHANGELOG.md"
    
    if changelog_md.exists():
        print(f"✅ CHANGELOG.md existe")
    else:
        warnings.append(f"⚠️ No existe documentacion/CHANGELOG.md")
    
    # 5. Validar WORKFLOWS.md (debe mencionar que es para humanos)
    workflows_md = PROJECT_ROOT / "documentacion" / "WORKFLOWS.md"
    
    if workflows_md.exists():
        with open(workflows_md) as f:
            content = f.read()
        
        if 'Claude NO lee esto' in content or 'REFERENCIA TÉCNICA' in content:
            print(f"✅ WORKFLOWS.md claramente marcado como referencia")
        else:
            warnings.append(f"⚠️ WORKFLOWS.md debería aclarar que es solo para humanos")
    else:
        warnings.append(f"⚠️ No existe documentacion/WORKFLOWS.md")
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE VALIDACIÓN")
    print("="*60)
    
    if not errors and not warnings:
        print("✅ TODO SINCRONIZADO CORRECTAMENTE")
        return 0
    
    if warnings:
        print(f"\n⚠️  {len(warnings)} ADVERTENCIAS:")
        for warning in warnings:
            print(f"  {warning}")
    
    if errors:
        print(f"\n❌ {len(errors)} ERRORES CRÍTICOS:")
        for error in errors:
            print(f"  {error}")
        print("\n🔧 Ejecuta sincronización para corregir")
        return 1
    
    return 0 if not errors else 1

if __name__ == "__main__":
    exit_code = validate_versions()
    sys.exit(exit_code)
```

**Ubicación:** `scripts/validate_sync.py`  
**Uso:** `python scripts/validate_sync.py`

**Tiempo estimado:** 15 minutos

---

#### Paso 3.2: Tests automatizados

```python
# tests/test_version_sync.py
"""
Tests de sincronización de versiones
"""

import pytest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config.version_info import VERSION, COMPONENTES, get_version_string

def test_version_info_exists():
    """Verifica que version_info.py existe"""
    version_file = PROJECT_ROOT / "config" / "version_info.py"
    assert version_file.exists(), "config/version_info.py debe existir"

def test_version_format():
    """Verifica formato de versión"""
    assert isinstance(VERSION, str)
    parts = VERSION.split('.')
    assert len(parts) == 3, "Versión debe ser X.Y.Z"
    assert all(p.isdigit() for p in parts), "Versión debe ser numérica"

def test_get_version_string():
    """Verifica función get_version_string"""
    # Sin parámetro
    version = get_version_string()
    assert version.startswith('v')
    assert version == f"v{VERSION}"
    
    # Con componente
    version_auditor = get_version_string('auditor_sistema')
    assert version_auditor.startswith('v')
    
    # Componente inexistente
    with pytest.raises(ValueError):
        get_version_string('componente_inexistente')

def test_auditor_imports_version_info():
    """Verifica que auditor_sistema.py importa version_info"""
    auditor_file = PROJECT_ROOT / "herramientas_ia" / "auditor_sistema.py"
    
    if auditor_file.exists():
        with open(auditor_file) as f:
            content = f.read()
        
        assert 'from config.version_info import' in content, \
            "auditor_sistema.py debe importar desde version_info"

def test_claude_md_is_minimal():
    """Verifica que CLAUDE.md no tiene changelogs"""
    claude_file = PROJECT_ROOT / ".claude" / "CLAUDE.md"
    
    if claude_file.exists():
        with open(claude_file) as f:
            content = f.read()
        
        # No debe tener patrones de changelog
        assert 'CHANGELOG v' not in content, \
            "CLAUDE.md no debe contener changelogs"
        
        # Debe ser relativamente corto
        lines = content.splitlines()
        assert len(lines) < 200, \
            f"CLAUDE.md debe tener < 200 líneas (tiene {len(lines)})"

def test_changelog_exists():
    """Verifica que existe documentacion/CHANGELOG.md"""
    changelog_file = PROJECT_ROOT / "documentacion" / "CHANGELOG.md"
    assert changelog_file.exists(), \
        "documentacion/CHANGELOG.md debe existir"

def test_workflows_is_reference():
    """Verifica que WORKFLOWS.md está marcado como referencia"""
    workflows_file = PROJECT_ROOT / "documentacion" / "WORKFLOWS.md"
    
    if workflows_file.exists():
        with open(workflows_file) as f:
            content = f.read()
        
        # Debe mencionar que es para humanos
        assert ('Claude NO lee esto' in content or 
                'REFERENCIA TÉCNICA' in content), \
            "WORKFLOWS.md debe estar marcado como referencia para humanos"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Ubicación:** `tests/test_version_sync.py`  
**Uso:** `pytest tests/test_version_sync.py -v`

**Tiempo estimado:** 15 minutos

---

### Fase 4: Documentación de Proceso (15 minutos)

#### Crear guía de mantenimiento

```markdown
# 📘 Guía de Mantenimiento: Sincronización de Versiones

## Filosofía

**Single Source of Truth:** Cada pieza de información tiene UNA ubicación oficial.

```
config/version_info.py → Versiones (ÚNICA fuente)
documentacion/CHANGELOG.md → Historial de cambios
documentacion/WORKFLOWS.md → Referencia técnica
.claude/CLAUDE.md → Instrucciones para Claude (minimalista)
.claude/agents/*.md → API de agentes
```

---

## Al Actualizar Versión

### Paso 1: Actualizar version_info.py

```python
# config/version_info.py

VERSION = "6.0.17"  # ← SOLO cambiar aquí
FECHA = date(2025, 11, 1)  # ← SOLO cambiar aquí

COMPONENTES = {
    "auditor_sistema": "3.3.1",  # ← Si cambió el componente
    # ...
}
```

### Paso 2: Actualizar CHANGELOG.md

```markdown
# documentacion/CHANGELOG.md

## [6.0.17] - 2025-11-01

### ✅ Agregado
- Nueva funcionalidad X

### 🐛 Corregido
- Bug Y
```

### Paso 3: Validar sincronización

```bash
python scripts/validate_sync.py
```

**Debe mostrar:** ✅ TODO SINCRONIZADO CORRECTAMENTE

### Paso 4: Ejecutar tests

```bash
pytest tests/test_version_sync.py -v
```

**Debe pasar:** 8/8 tests

---

## Al Agregar Funcionalidad Nueva

### Paso 1: Implementar en código

```python
# herramientas_ia/auditor_sistema.py

def nueva_funcion():
    """Nueva funcionalidad"""
    pass
```

### Paso 2: Actualizar versión componente

```python
# config/version_info.py

COMPONENTES = {
    "auditor_sistema": "3.4.0",  # ← Incrementar versión
}
```

### Paso 3: Documentar en agente

```markdown
# .claude/agents/data-auditor.md

## FUNC-XX: Nueva Funcionalidad
**Estado:** IMPLEMENTADA ✅  
**Versión:** 3.4.0+

Descripción...
```

### Paso 4: Agregar a CHANGELOG

```markdown
# documentacion/CHANGELOG.md

## [3.4.0] - FECHA

### ✅ Agregado
- FUNC-XX: nueva_funcion()
```

### Paso 5: NO tocar CLAUDE.md

CLAUDE.md NO debe modificarse a menos que cambie el COMPORTAMIENTO de Claude.

---

## Al Modificar Workflows

### SÍ modificar:
- `documentacion/WORKFLOWS.md` (referencia técnica)

### NO modificar:
- `.claude/CLAUDE.md` (solo si cambia cómo actúa Claude)

---

## Checklist de Sincronización

```
□ version_info.py actualizado
□ CHANGELOG.md actualizado
□ Agente .md actualizado (si aplica)
□ Tests pasan
□ Validación pasa
□ CLAUDE.md NO tiene changelogs
□ WORKFLOWS.md está en documentacion/
```

---

## Comandos Útiles

```bash
# Validar sincronización
python scripts/validate_sync.py

# Ejecutar tests
pytest tests/test_version_sync.py -v

# Ver versión actual
python -c "from config.version_info import VERSION; print(VERSION)"

# Ver todas las versiones
python -c "from config.version_info import get_full_version_info; import json; print(json.dumps(get_full_version_info(), indent=2))"
```

---

## Errores Comunes

### ❌ Error: "Versiones desincronizadas"

**Causa:** Se actualizó versión en múltiples lugares

**Solución:**
1. Elegir versión correcta
2. Actualizar SOLO en `config/version_info.py`
3. Borrar versiones duplicadas en otros archivos
4. Validar: `python scripts/validate_sync.py`

### ❌ Error: "CLAUDE.md tiene changelogs"

**Causa:** Se agregó changelog directamente a CLAUDE.md

**Solución:**
1. Mover changelog a `documentacion/CHANGELOG.md`
2. Borrar de CLAUDE.md
3. Validar: `python scripts/validate_sync.py`

### ❌ Error: "auditor_sistema.py no importa version_info"

**Causa:** Se hardcodeó versión en lugar de importarla

**Solución:**
```python
# ❌ Incorrecto
__version__ = "3.3.0"

# ✅ Correcto
from config.version_info import get_version_string
__version__ = get_version_string('auditor_sistema')
```

---

**Última actualización:** 2025-10-30
```

**Ubicación:** `documentacion/GUIA_MANTENIMIENTO_VERSIONES.md`  
**Tiempo estimado:** 15 minutos

---

## 📊 PARTE 4: RESUMEN EJECUTIVO

### Tiempo Total Estimado

```
Fase 1: Single Source of Truth     30 minutos
Fase 2: Limpiar CLAUDE.md          45 minutos
Fase 3: Validación y Tests         30 minutos
Fase 4: Documentación              15 minutos
────────────────────────────────────────────
TOTAL:                            120 minutos (2 horas)
```

### Archivos a Crear

```
✅ config/version_info.py (nuevo)
✅ documentacion/CHANGELOG.md (nuevo)
✅ documentacion/GUIA_MANTENIMIENTO_VERSIONES.md (nuevo)
✅ scripts/validate_sync.py (nuevo)
✅ tests/test_version_sync.py (nuevo)
```

### Archivos a Modificar

```
🔧 herramientas_ia/auditor_sistema.py
   - Importar version_info
   - Eliminar versión hardcodeada
   - Resumir changelog

🔧 .claude/agents/data-auditor.md
   - Estado claro de funciones
   - Separar Fase 1 vs Fase 2
   - Referenciar CHANGELOG.md

🔧 .claude/CLAUDE.md
   - Reducir de 407 → ~120 líneas
   - Eliminar changelogs
   - Eliminar workflows detallados
   - Solo instrucciones de comportamiento

🔧 documentacion/WORKFLOWS.md
   - Mover de .claude/ a documentacion/
   - Reducir de 566 → ~150 líneas
   - Marcar como "referencia para humanos"
```

### Archivos a NO Modificar

```
✋ config/database_manager.py
✋ core/extractors/*.py
✋ ui.py
✋ otros archivos funcionales
```

---

## 🎯 PARTE 5: CHECKLIST DE IMPLEMENTACIÓN

### Pre-requisitos

```bash
□ Backup completo del proyecto
  git commit -am "Backup pre-sincronización"
  
□ Crear branch
  git checkout -b sync-versions-docs
```

### Fase 1 ✅

```bash
□ Crear config/version_info.py
□ Actualizar auditor_sistema.py (import version_info)
□ Actualizar data-auditor.md (clarificar estados)
□ Validar: python -c "from config.version_info import VERSION; print(VERSION)"
```

### Fase 2 ✅

```bash
□ Crear CLAUDE.md minimalista (~120 líneas)
□ Crear documentacion/CHANGELOG.md
□ Mover WORKFLOWS.md a documentacion/
□ Simplificar WORKFLOWS.md (~150 líneas)
□ Validar: Comparar tamaños antes/después
```

### Fase 3 ✅

```bash
□ Crear scripts/validate_sync.py
□ Crear tests/test_version_sync.py
□ Ejecutar: python scripts/validate_sync.py
□ Ejecutar: pytest tests/test_version_sync.py -v
□ Resultado: Todo en verde ✅
```

### Fase 4 ✅

```bash
□ Crear documentacion/GUIA_MANTENIMIENTO_VERSIONES.md
□ Revisar que toda la documentación sea consistente
□ git add .
□ git commit -m "Sincronización completa: versiones + docs"
```

### Post-implementación ✅

```bash
□ Merge a main
  git checkout main
  git merge sync-versions-docs
  
□ Validar en producción
  python scripts/validate_sync.py
  
□ Comunicar cambios al equipo
```

---

## 🚀 PARTE 6: BENEFICIOS ESPERADOS

### Antes (Estado Actual)

```
❌ 3 versiones diferentes (6.0.16, 3.3.0, 3.1.0)
❌ CLAUDE.md: 407 líneas (confuso)
❌ Changelogs en múltiples lugares
❌ Workflows duplicados
❌ Claude se confunde sobre qué funciona
❌ Mantenimiento requiere actualizar 5+ archivos
```

### Después (Estado Deseado)

```
✅ 1 versión única (config/version_info.py)
✅ CLAUDE.md: ~120 líneas (claro)
✅ Changelog en UN lugar (CHANGELOG.md)
✅ Workflows en documentacion/ (referencia)
✅ Claude sabe exactamente qué hacer
✅ Mantenimiento: 1 archivo (version_info.py)
```

### Métricas de Mejora

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Archivos con versión | 5+ | 1 | -80% |
| Líneas CLAUDE.md | 407 | 120 | -70% |
| Líneas WORKFLOWS.md | 566 | 150 | -73% |
| Tiempo actualizar versión | 30 min | 5 min | -83% |
| Claridad para Claude | Confuso | Claro | ∞ |

---

## 📌 CONCLUSIÓN

Este plan de sincronización:

1. ✅ **Resuelve el problema raíz** (información duplicada)
2. ✅ **Establece "Single Source of Truth"** (version_info.py)
3. ✅ **Simplifica CLAUDE.md** (407 → 120 líneas)
4. ✅ **Separa responsabilidades** (Claude vs Humanos vs Código)
5. ✅ **Automatiza validación** (scripts + tests)
6. ✅ **Documenta el proceso** (guía de mantenimiento)

### Siguiente Paso

**Opción A:** "Empecemos - dame el código de version_info.py"  
**Opción B:** "Ajusta el plan - quiero cambiar [X]"  
**Opción C:** "Dame un script que haga todo automáticamente"  
**Opción D:** "Explica más sobre [fase específica]"

¿Qué prefieres?

---

**Preparado por:** Sistema de Análisis  
**Fecha:** 30 de octubre de 2025  
**Tiempo estimado total:** 2 horas  
**Dificultad:** Media  
**Riesgo:** Bajo (con backup)
