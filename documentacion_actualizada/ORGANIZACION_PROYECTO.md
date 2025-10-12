# 📂 ORGANIZACIÓN DEL PROYECTO - V3.2.2

**Fecha de organización:** 11 de Octubre de 2025
**Versión:** 3.2.2
**Estado:** ✅ LIMPIO Y ORGANIZADO

---

## 🎯 OBJETIVO DE LA REORGANIZACIÓN

Limpiar el directorio raíz del proyecto, moviendo archivos de análisis, testing y documentación a sus carpetas correspondientes, manteniendo solo los archivos esenciales en el root.

---

## 📋 ESTRUCTURA FINAL DEL PROYECTO

### **Directorio Raíz (Solo Archivos Esenciales)**

```
ProyectoHUV9GESTOR_ONCOLOGIA_automatizado/
│
├── 📄 ui.py                     # Aplicación principal (229 KB)
├── 📋 requirements.txt          # Dependencias Python
├── 📖 README.md                 # Documentación principal
├── 🚀 iniciar_python.bat       # Launcher Windows
├── ⚙️ COMPILADOR.bat           # Compilador a .exe
├── 🔒 .gitignore               # Git ignore actualizado
└── 📝 .gitattributes           # Atributos de Git
```

**Total:** 7 archivos en root (antes: 27 archivos)

---

### **Carpetas Principales**

#### **1. `/core/` - Módulos Principales**
```
core/
├── auditoria_ia.py              # Sistema de auditoría con IA
├── llm_client.py                # Cliente LM Studio
├── ventana_auditoria_ia.py      # UI de auditoría
├── ventana_resultados_importacion.py  # Ventana de resultados
├── validation_checker.py        # Validación de completitud
├── database_manager.py          # Gestor de BD SQLite
├── unified_extractor.py         # Extractor unificado de datos
├── ihq_processor.py             # Procesador de archivos IHQ
└── processors/                  # Procesadores especializados
    ├── ocr_processor.py
    ├── biomarcador_extractor.py
    └── ...
```

#### **2. `/config/` - Configuración**
```
config/
└── config.ini                   # Parámetros del sistema
```

#### **3. `/data/` - Datos Persistentes**
```
data/
├── evarisis.db                  # Base de datos SQLite (NO INCLUIDA EN GIT)
├── reportes_ia/                 # Reportes Markdown generados
│   └── *.md                     # (NO INCLUIDOS EN GIT)
└── auditorias_ia/               # Auditorías históricas
    └── *.md                     # (NO INCLUIDOS EN GIT)
```

#### **4. `/documentacion_actualizada/` - Documentación Técnica Actualizada**
```
documentacion_actualizada/
├── ESTADO_SISTEMA_V3.2.2.md               # Estado completo del sistema
├── CAMBIOS_V3.2.2.md                      # Changelog detallado
├── ORGANIZACION_PROYECTO.md               # Este archivo
├── AUDITORIA_FINAL_V322.md                # Auditoría completa de 50 casos
├── REPORTE_CORRECCIONES_APLICADAS.md      # Detalles técnicos de fixes
├── DIAGNOSTICO_CAUSAS_ERRORES.md          # Análisis de errores
├── DIAGNOSTICO_BUG_KI67_EXTRACTOR.md      # Diagnóstico Ki-67
├── REPORTE_AUDITORIA_COMPLETA.md          # Auditoría detallada
├── REPORTE_AUDITORIA_FINAL_ANALISIS.md    # Análisis final
├── REPORTE_FINAL_COMPARATIVO_PROMPTS.md   # Comparativa de prompts
├── ANALISIS_MODULARIDAD.md                # Análisis modular
├── ANALISIS_REPROCESAMIENTO.md            # Análisis de reprocesamiento
└── VERIFICACION_FINAL_COMPLETA.md         # Verificación completa
```

#### **5. `/herramientas_ia/` - Scripts de Testing y Validación**
```
herramientas_ia/
├── verificar_todos_casos.py         # Verificación completa de 50 casos
├── auditoria_completa.py            # Auditoría con IA de todos los registros
├── verificar_precision.py           # Validación de biomarcadores
├── verificar_casos_final.py         # Verificación final
├── verificar_correciones_ia.py      # Verificación de correcciones IA
├── analizar_bd.py                   # Análisis de base de datos
├── investigar_ki67.py               # Investigación de patrones Ki-67
├── test_mejoras_v322.py             # Test de validación cruzada
├── test_ki67_fix.py                 # Test de patrones Ki-67
└── test_lotes_debug.py              # Test de procesamiento por lotes
```

#### **6. `/ui_helpers/` - Helpers de Interfaz**
```
ui_helpers/
├── enhanced_dashboard.py            # Dashboard mejorado
└── ...
```

#### **7. `/LEGACY/` - Archivos Antiguos**
```
LEGACY/
└── (código anterior movido aquí)
```

#### **8. `/pdfs_patologia/` - PDFs de Entrada**
```
pdfs_patologia/
└── *.pdf                            # Archivos PDF médicos (NO INCLUIDOS EN GIT)
```

#### **9. `/EXCEL/` - Exportaciones Excel**
```
EXCEL/
└── *.xlsx                           # Exportaciones generadas (NO INCLUIDOS EN GIT)
```

---

## 🔄 CAMBIOS REALIZADOS

### **Archivos Movidos a `documentacion_actualizada/`**

```bash
ANALISIS_MODULARIDAD.md              → documentacion_actualizada/
ANALISIS_REPROCESAMIENTO.md          → documentacion_actualizada/
AUDITORIA_FINAL_V322.md               → documentacion_actualizada/
DIAGNOSTICO_BUG_KI67_EXTRACTOR.md     → documentacion_actualizada/
DIAGNOSTICO_CAUSAS_ERRORES.md         → documentacion_actualizada/
REPORTE_AUDITORIA_COMPLETA.md         → documentacion_actualizada/
REPORTE_AUDITORIA_FINAL_ANALISIS.md   → documentacion_actualizada/
REPORTE_CORRECCIONES_APLICADAS.md     → documentacion_actualizada/
REPORTE_FINAL_COMPARATIVO_PROMPTS.md  → documentacion_actualizada/
VERIFICACION_FINAL_COMPLETA.md        → documentacion_actualizada/
```

**Total:** 10 archivos de documentación organizados

---

### **Archivos Movidos a `herramientas_ia/`**

```bash
analizar_bd.py                → herramientas_ia/
auditoria_completa.py         → herramientas_ia/
investigar_ki67.py            → herramientas_ia/
test_ki67_fix.py              → herramientas_ia/
test_lotes_debug.py           → herramientas_ia/
test_mejoras_v322.py          → herramientas_ia/
verificar_casos_final.py      → herramientas_ia/
verificar_correciones_ia.py   → herramientas_ia/
verificar_precision.py        → herramientas_ia/
verificar_todos_casos.py      → herramientas_ia/
```

**Total:** 10 scripts de testing organizados

---

### **Archivos Eliminados (Temporales)**

```bash
nul                           → ELIMINADO
test_timezone_fix.py          → ELIMINADO
```

**Total:** 2 archivos temporales eliminados

---

### **Documentación Creada**

```bash
documentacion_actualizada/ESTADO_SISTEMA_V3.2.2.md      → CREADO
documentacion_actualizada/CAMBIOS_V3.2.2.md             → CREADO
documentacion_actualizada/ORGANIZACION_PROYECTO.md      → CREADO (este archivo)
```

**Total:** 3 archivos nuevos de documentación

---

## 📊 RESUMEN DE CAMBIOS

### **Antes de la Reorganización:**

```
Directorio raíz:
- 27 archivos
- 10+ reportes de análisis
- 10+ scripts de testing
- 2 archivos temporales
- Difícil navegación
```

### **Después de la Reorganización:**

```
Directorio raíz:
- 7 archivos esenciales
- 0 reportes (movidos a documentacion_actualizada/)
- 0 scripts de testing (movidos a herramientas_ia/)
- 0 archivos temporales (eliminados)
- Navegación clara y organizada
```

---

## 🔒 ACTUALIZACIÓN DE .GITIGNORE

### **Carpetas Agregadas a Git:**

```gitignore
!/documentacion_actualizada/
!/herramientas_ia/
!/ui_helpers/
!/LEGACY/
```

### **Exclusiones Agregadas:**

```gitignore
# Archivos temporales de testing
**/test_*.py
**/nul
**/*.bak
**/prueba*/

# Reportes generados con datos sensibles
data/reportes_ia/*.md
data/auditorias_ia/*.md
```

---

## 📚 GUÍA DE USO DE LA NUEVA ESTRUCTURA

### **Para Desarrolladores:**

#### **Ejecutar el sistema:**
```bash
# Desde el root del proyecto
python ui.py
```

#### **Ejecutar tests de validación:**
```bash
cd herramientas_ia
python verificar_todos_casos.py
```

#### **Leer documentación técnica:**
```bash
cd documentacion_actualizada
# Abrir ESTADO_SISTEMA_V3.2.2.md
```

#### **Ver cambios de versión:**
```bash
cd documentacion_actualizada
# Abrir CAMBIOS_V3.2.2.md
```

---

### **Para Usuarios Médicos:**

#### **Iniciar sistema:**
1. Doble click en `iniciar_python.bat`
2. Sistema iniciará automáticamente

#### **Importar informes:**
1. Copiar PDFs a carpeta `pdfs_patologia/`
2. Usar interfaz gráfica para importar
3. Revisar resultados en ventana de análisis

#### **Exportar datos:**
1. Ir a pestaña "Visualizar datos"
2. Seleccionar registros
3. Click "Exportar Selección"
4. Archivo se guarda en carpeta `EXCEL/`

---

## 🛠️ MANTENIMIENTO DEL PROYECTO

### **Ubicaciones de Archivos por Tipo:**

| Tipo de Archivo | Ubicación |
|-----------------|-----------|
| Código principal | `ui.py`, `/core/` |
| Scripts de testing | `/herramientas_ia/` |
| Documentación técnica | `/documentacion_actualizada/` |
| Configuración | `/config/` |
| Datos y BD | `/data/` |
| PDFs médicos | `/pdfs_patologia/` |
| Exportaciones | `/EXCEL/` |
| Helpers UI | `/ui_helpers/` |
| Código antiguo | `/LEGACY/` |

### **Convenciones de Nombres:**

#### **Scripts de Testing:**
```
verificar_*.py          # Scripts de verificación
test_*.py              # Scripts de testing
auditoria_*.py         # Scripts de auditoría
analizar_*.py          # Scripts de análisis
```

#### **Documentación:**
```
ESTADO_*.md            # Estado del sistema
CAMBIOS_*.md           # Changelogs
REPORTE_*.md           # Reportes técnicos
ANALISIS_*.md          # Análisis técnicos
DIAGNOSTICO_*.md       # Diagnósticos de bugs
VERIFICACION_*.md      # Verificaciones
```

---

## 📦 BACKUP Y VERSIONADO

### **Archivos a Respaldar:**

✅ **Críticos (backup diario):**
- `data/evarisis.db`
- `/config/config.ini`

⚠️ **Importantes (backup semanal):**
- Todo el contenido de `/core/`
- `ui.py`
- `requirements.txt`

ℹ️ **Opcionales (backup mensual):**
- `/documentacion_actualizada/`
- `/herramientas_ia/`

### **NO Respaldar (generados automáticamente):**
- `/data/reportes_ia/*.md`
- `/data/auditorias_ia/*.md`
- `/EXCEL/*.xlsx`
- `__pycache__/`
- `*.pyc`

---

## 🔄 CONTROL DE VERSIONES GIT

### **Estado del Repositorio:**

```bash
# Archivos rastreados por Git:
✅ ui.py
✅ requirements.txt
✅ README.md
✅ /core/
✅ /config/ (estructura, no config.ini)
✅ /documentacion_actualizada/
✅ /herramientas_ia/
✅ /ui_helpers/

# Archivos ignorados por Git:
❌ data/*.db
❌ data/reportes_ia/*.md
❌ pdfs_patologia/*.pdf
❌ EXCEL/*.xlsx
❌ **/test_*.py (en herramientas_ia se incluyen explícitamente)
❌ nul, *.bak, prueba*/
```

### **Comandos Git Útiles:**

```bash
# Ver estado del repositorio
git status

# Ver archivos ignorados
git status --ignored

# Agregar cambios
git add .

# Commit
git commit -m "v3.2.2 - Reorganización de proyecto"

# Ver historial
git log --oneline

# Ver cambios en archivos
git diff
```

---

## 🎯 PRÓXIMOS PASOS

### **Mantenimiento Recomendado:**

1. **Semanal:**
   - Revisar logs de auditoría en `data/reportes_ia/`
   - Limpiar archivos temporales
   - Backup de `data/evarisis.db`

2. **Mensual:**
   - Actualizar documentación si hay cambios
   - Revisar y archivar reportes antiguos
   - Verificar integridad de BD con `herramientas_ia/analizar_bd.py`

3. **Trimestral:**
   - Auditoría completa con `herramientas_ia/auditoria_completa.py`
   - Actualizar README.md si hay mejoras
   - Revisar y optimizar estructura de carpetas

---

## 📞 CONTACTO

**Proyecto:** EVARISIS Cirugía Oncológica
**Institución:** Hospital Universitario del Valle - Cali, Colombia
**Versión:** 3.2.2
**Fecha de organización:** 11 de Octubre de 2025

---

**© 2025 Hospital Universitario del Valle**
*Uso exclusivo para fines médicos y de investigación oncológica*
