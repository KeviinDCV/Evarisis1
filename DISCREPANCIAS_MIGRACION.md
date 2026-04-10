# 🔍 REPORTE DE DISCREPANCIAS - MIGRACIÓN PYSIDE6

**Fecha:** 20 Noviembre 2025
**Versión TTKBootstrap:** v6.0.9 (ui.py)
**Versión PySide6:** v7.0.0-alpha (main_pyside6.py)
**Estado:** Auditoría completa feature por feature

---

## 📋 RESUMEN EJECUTIVO

La migración PySide6 **NO es una copia 1:1** de la funcionalidad TTKBootstrap. Existen **discrepancias críticas** en todas las vistas principales que reducen significativamente la funcionalidad disponible.

### Métrica Global

| Aspecto | TTKBootstrap | PySide6 | % Migrado |
|---------|--------------|---------|-----------|
| **Vistas principales** | 5 completas | 3 parciales + 2 ausentes | 40% |
| **Funcionalidades totales** | ~45 features | ~12 features | 27% |
| **Líneas código UI** | 6,550 | 5,200 | 79% |
| **Integración backend** | 100% | 37.5% | 37.5% |

---

## 🏠 VISTA 1: PANTALLA DE BIENVENIDA (Welcome Screen)

### ✅ TTKBootstrap (ui.py líneas 3121-3243) - COMPLETA

**Contenido:**
1. ✅ **Header institucional visible**
   - Logo HUV
   - Información de usuario (nombre, cargo, foto de perfil)
   - Botón de versión

2. ✅ **Título principal**: "🏥 Bienvenido al Gestor Oncológico 🔬"

3. ✅ **Subtítulo descriptivo**: Doble línea con contexto del HUV

4. ✅ **Iconos representativos**: Fila de 7 emojis (📊 📈 🧬 💡 📋 🔍 ⚕️)

5. ✅ **Detección dinámica de estado de BD**:
   - Si BD vacía → Mensaje "No hay información en la base de datos"
   - Si BD vacía → Botón "📥 Agregar Información a la Base de Datos"
   - Si BD con datos → Mensaje de instrucción "Selecciona una opción del menú..."

6. ✅ **Navegación directa**: Botón lleva directo al tab de importación (línea 3229-3243)

### ❌ PySide6 (welcome_view.py) - INCOMPLETA

**Contenido:**
1. ❌ **Sin header institucional** (no se ve logo, usuario, versión)

2. ✅ Título: "Bienvenido a EVARISIS" (diferente, menos descriptivo)

3. ✅ Subtítulo: 1 línea genérica

4. ❌ **Solo 1 icono** (🏥) vs 7 iconos en TTKBootstrap

5. ❌ **Sin detección de estado de BD** (no verifica si hay datos)

6. ❌ **Navegación genérica**: Botón dice "Iniciar Nueva Importación" pero solo emite signal genérico

### 🚨 FUNCIONALIDADES FALTANTES

| Feature | TTKBootstrap | PySide6 | Impacto |
|---------|--------------|---------|---------|
| Header institucional visible | ✅ | ❌ | **CRÍTICO** - Branding perdido |
| Detección de BD vacía | ✅ | ❌ | **ALTO** - UX confusa para nuevo usuario |
| Navegación directa a importación | ✅ | ❌ | **MEDIO** - 1 paso extra para usuario |
| Iconos informativos (7) | ✅ | ❌ (solo 1) | **BAJO** - Impacto visual reducido |
| Subtítulo de 2 líneas | ✅ | ❌ (solo 1) | **BAJO** - Menos contexto |

**% Funcionalidad migrada: 40%** (2/5 features)

---

## 🗄️ VISTA 2: BASE DE DATOS (Database View)

### ✅ TTKBootstrap - COMPLETA (líneas 1906-1970)

**Estructura:**
- **Dashboard mejorado completo** (EnhancedDatabaseDashboard)
- **5 tabs integradas:**
  1. ✅ **Estadísticas Generales** - KPIs + gráficos
  2. ✅ **Visualizador de Datos** - Tabla completa con 15+ funcionalidades
  3. ✅ **Calendario Inteligente** - CalendarioInteligente() completo
  4. ✅ **Análisis Temporal** - Gráficos de tendencias
  5. ✅ **Importar Datos** - Sistema completo con detección duplicados

**Funcionalidades de Importación (Tab 5):**
1. ✅ Listbox con archivos seleccionados (color-coded)
2. ✅ Detección de duplicados en tiempo real (colores: rojo=duplicado, verde=nuevo)
3. ✅ Botón "Seleccionar archivo PDF" (individual)
4. ✅ Botón "Seleccionar carpeta" (batch)
5. ✅ Botón "Limpiar lista"
6. ✅ Botón "Procesar archivos seleccionados"
7. ✅ Progreso detallado con log de eventos
8. ✅ Conexión con `_refresh_files_list()` (línea 1948)
9. ✅ Auto-carga de dashboard después de importación (línea 1965)

**Funcionalidades del Visualizador (Tab 2 - líneas 1984-2500):**
1. ✅ **Título compacto** "📊 Visualizador de Datos"
2. ✅ **Barra de acciones** (16 botones):
   - 🔍 Filtrar
   - 🔎 Ver detalles
   - 📤 Exportar selección
   - 📊 Exportar todo
   - 📋 Copiar selección
   - 🔄 Actualizar
   - 🤖 Auditoría parcial
   - ✅ Auditoría completa
   - ... (8 más)
3. ✅ **Buscador global** (search entry con bind en tiempo real)
4. ✅ **Tabla tksheet completa**:
   - Headers personalizados
   - Color coding por completitud
   - Selección múltiple
   - Event bindings (select, deselect, shift_select)
   - Scroll horizontal y vertical
5. ✅ **Auto-carga de datos** al inicializar (línea 2503)
6. ✅ **Panel flotante de detalles** (creado bajo demanda)

### ❌ PySide6 - INCOMPLETA (database_view.py)

**Estructura:**
- **Solo 3 tabs básicas** (vs 5 completas)
  1. ⚠️ **Importación de PDFs** - Interfaz básica sin funcionalidad
  2. ⚠️ **Visualizar Datos** - Tabla sin backend conectado
  3. ❌ **Calendario** - Solo placeholder ("Calendario pendiente")

**Funcionalidades de Importación (Tab 1):**
1. ✅ Header descriptivo
2. ✅ Área drag-and-drop style
3. ✅ Etiqueta "Archivos seleccionados: 0"
4. ✅ Botón "📂 Seleccionar Archivos PDF"
5. ❌ **Sin botón seleccionar carpeta**
6. ❌ **Sin listbox con archivos** (no se ven los seleccionados)
7. ❌ **Sin detección de duplicados**
8. ❌ **Sin color coding**
9. ✅ ProgressBar (creada pero sin conectar)
10. ✅ QTextEdit para log (creado pero sin usar)
11. ❌ **Signal emitido pero no conectado** a worker real

**Funcionalidades del Visualizador (Tab 2):**
1. ✅ Header "Tabla de Datos"
2. ✅ Buscador global (QLineEdit)
3. ✅ Botón "🔄 Actualizar"
4. ✅ Botón "📤 Exportar"
5. ❌ **Sin botones de auditoría** (parcial, completa)
6. ❌ **Sin botón filtrar**
7. ❌ **Sin botón ver detalles**
8. ❌ **Sin botón copiar selección**
9. ✅ DataTable (componente creado)
10. ❌ **Tabla vacía** (sin datos cargados por defecto)
11. ❌ **Sin auto-carga** de datos al inicializar
12. ❌ **Sin panel de detalles**

### 🚨 FUNCIONALIDADES FALTANTES

| Feature | TTKBootstrap | PySide6 | Impacto |
|---------|--------------|---------|---------|
| **IMPORTACIÓN** | | | |
| Listbox con archivos | ✅ | ❌ | **CRÍTICO** - Usuario no ve qué seleccionó |
| Detección duplicados | ✅ | ❌ | **CRÍTICO** - Puede importar duplicados |
| Color coding (rojo/verde) | ✅ | ❌ | **ALTO** - Feedback visual perdido |
| Seleccionar carpeta (batch) | ✅ | ❌ | **ALTO** - Solo puede 1 archivo a la vez |
| Limpiar lista | ✅ | ❌ | **MEDIO** - Debe cerrar y reabrir |
| Log de progreso funcional | ✅ | ❌ | **MEDIO** - No se ve qué está pasando |
| Auto-refresh dashboard | ✅ | ❌ | **MEDIO** - Debe actualizar manual |
| **VISUALIZADOR** | | | |
| 16 botones de acción | ✅ | ❌ (solo 2) | **CRÍTICO** - 87.5% funcionalidad perdida |
| Auditoría parcial | ✅ | ❌ | **CRÍTICO** - Feature principal ausente |
| Auditoría completa | ✅ | ❌ | **CRÍTICO** - Feature principal ausente |
| Ver detalles | ✅ | ❌ | **ALTO** - No puede ver info completa |
| Filtrar | ✅ | ❌ | **ALTO** - No puede buscar específico |
| Copiar selección | ✅ | ❌ | **MEDIO** - Workflow manual más lento |
| Auto-carga datos | ✅ | ❌ | **MEDIO** - Vista vacía por defecto |
| Panel detalles flotante | ✅ | ❌ | **MEDIO** - Debe exportar para ver |
| **TABS ADICIONALES** | | | |
| Estadísticas Generales | ✅ | ❌ | **ALTO** - Vista analítica perdida |
| Calendario Inteligente | ✅ | ❌ | **ALTO** - Feature completa ausente |
| Análisis Temporal | ✅ | ❌ | **ALTO** - Gráficos de tendencias perdidos |

**% Funcionalidad migrada: 25%** (8/32 features)

---

## 📈 VISTA 3: DASHBOARD GRÁFICO (Dashboard View)

### ✅ TTKBootstrap - COMPLETA (líneas 2507-3109)

**Estructura:**
1. ✅ **Título**: "📈 Análisis Gráfico de la Base de Datos"

2. ✅ **Sidebar de filtros colapsable**:
   - Fecha desde/hasta
   - Servicio (combobox dinámico)
   - Malignidad (PRESENTE/AUSENTE)
   - Responsable (combobox dinámico)
   - Botón "Refrescar"
   - Botón "Limpiar"

3. ✅ **Toolbar superior**:
   - Botón "≡ Mostrar filtros" (toggle sidebar)
   - Botón "Filtros…" (abrir sheet avanzado)

4. ✅ **Notebook con 5 tabs** de gráficos:
   - **Overview** (4 gráficos en grid 2x2)
   - **Biomarkers** (4 gráficos de biomarcadores)
   - **Times** (4 gráficos temporales)
   - **Quality** (4 gráficos de calidad)
   - **Compare** (4 gráficos comparativos)

5. ✅ **Grid responsive 2x2** por cada tab (20 gráficos totales)

6. ✅ **Integración Matplotlib** con backend Tkinter

7. ✅ **Carga dinámica** de datos con `cargar_dashboard()` (línea 3261-3273)

### ❌ PySide6 - INCOMPLETA (dashboard_view.py)

**Estructura:**
1. ✅ Título: "📈 Dashboard General"

2. ❌ **Sin sidebar de filtros** (0 filtros)

3. ❌ **Sin toolbar**

4. ❌ **Sin tabs** (solo 1 vista fija)

5. ✅ **4 KPIs** (bien implementadas):
   - Total Registros
   - Casos Malignos
   - Productividad Mes
   - Pendientes IA

6. ❌ **Solo 1 placeholder de gráfico** vs 20 gráficos reales

7. ❌ **Sin integración con datos reales** (valores hardcoded)

8. ❌ **Sin método de carga dinámica**

### 🚨 FUNCIONALIDADES FALTANTES

| Feature | TTKBootstrap | PySide6 | Impacto |
|---------|--------------|---------|---------|
| Sidebar de filtros | ✅ | ❌ | **CRÍTICO** - 0 capacidad de filtrado |
| 5 tabs de gráficos | ✅ | ❌ | **CRÍTICO** - 95% gráficos perdidos |
| 20 gráficos Matplotlib | ✅ | ❌ (solo placeholder) | **CRÍTICO** - Análisis visual 0% |
| Toolbar con toggle | ✅ | ❌ | **ALTO** - Sin controles de vista |
| Filtro por fecha | ✅ | ❌ | **ALTO** - No puede ver rangos |
| Filtro por servicio | ✅ | ❌ | **ALTO** - No puede comparar servicios |
| Filtro por malignidad | ✅ | ❌ | **ALTO** - No puede separar casos |
| Grid 2x2 responsive | ✅ | ❌ | **MEDIO** - Solo vista única |
| Carga dinámica BD | ✅ | ❌ | **CRÍTICO** - Datos falsos (1,245) |
| Tab Overview | ✅ | ❌ | **ALTO** - Vista general perdida |
| Tab Biomarkers | ✅ | ❌ | **ALTO** - Análisis IHQ perdido |
| Tab Times | ✅ | ❌ | **MEDIO** - Tendencias temporales perdidas |
| Tab Quality | ✅ | ❌ | **MEDIO** - Métricas calidad perdidas |
| Tab Compare | ✅ | ❌ | **MEDIO** - Comparativas perdidas |

**% Funcionalidad migrada: 15%** (2/14 features principales)

---

## 🤖 VISTA 4: AUDITORÍA IA (Audit View)

### ✅ TTKBootstrap - COMPLETA (líneas 707-1562)

**Módulo completo:** `core/ventana_auditoria_ia.py`

**Funcionalidades:**
1. ✅ **Ventana modal completa** (QDialog style)
2. ✅ **Selector de caso** (input número de petición)
3. ✅ **Selector de tipo de auditoría**:
   - Parcial (solo validación)
   - Completa (validación + IA)
4. ✅ **Progreso en tiempo real**:
   - Barra de progreso
   - Log detallado de pasos
   - Mensajes de estado
5. ✅ **Integración con auditor_sistema.py**:
   - FUNC-01: Auditoría inteligente
   - FUNC-03: Agregar biomarcador
   - FUNC-05: Workflow completitud
   - FUNC-06: Reprocesar caso
6. ✅ **Resultados interactivos**:
   - Score de completitud
   - Lista de errores
   - Sugerencias de corrección
7. ✅ **Botones de exportación** de reporte
8. ✅ **Llamadas desde múltiples lugares**:
   - Botón en visualizador
   - Botón en dashboard
   - Menú flotante

### ❌ PySide6 - AUSENTE

**Archivo:** `pyside6_ui/views/audit_view.py`

**Contenido actual:** Solo placeholder vacío (49 líneas)

```python
# Contenido completo del archivo:
class AuditView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        # PLACEHOLDER: Vista de auditoría IA pendiente
```

### 🚨 FUNCIONALIDADES FALTANTES

| Feature | TTKBootstrap | PySide6 | Impacto |
|---------|--------------|---------|---------|
| Vista completa de auditoría | ✅ | ❌ | **CRÍTICO** - Feature ausente 100% |
| Selector de caso | ✅ | ❌ | **CRÍTICO** |
| Selector tipo auditoría | ✅ | ❌ | **CRÍTICO** |
| Progreso en tiempo real | ✅ | ❌ | **CRÍTICO** |
| Integración FUNC-01 | ✅ | ❌ | **CRÍTICO** |
| Integración FUNC-06 | ✅ | ❌ | **CRÍTICO** |
| Resultados interactivos | ✅ | ❌ | **CRÍTICO** |
| Exportación de reporte | ✅ | ❌ | **ALTO** |

**% Funcionalidad migrada: 0%** (0/8 features)

---

## 🌐 VISTA 5: AUTOMATIZACIÓN WEB (Web Auto View)

### ✅ TTKBootstrap - COMPLETA

**Módulo:** `core/huv_web_automation.py`

**Funcionalidades:**
1. ✅ **Interfaz de credenciales**
2. ✅ **Selector de casos a entregar**
3. ✅ **Integración con Selenium**
4. ✅ **Progreso de navegación web**
5. ✅ **Upload automático QHORTE**
6. ✅ **Validación de entrega exitosa**

### ❌ PySide6 - AUSENTE

**Archivo:** `pyside6_ui/views/web_view.py`

**Contenido actual:** Solo placeholder vacío (49 líneas)

**% Funcionalidad migrada: 0%** (0/6 features)

---

## 📊 RESUMEN DE DISCREPANCIAS POR VISTA

| Vista | TTKBootstrap Features | PySide6 Features | % Migrado | Criticidad |
|-------|----------------------|------------------|-----------|-----------|
| **Welcome Screen** | 5 | 2 | **40%** | 🟡 MEDIA |
| **Database View** | 32 | 8 | **25%** | 🔴 CRÍTICA |
| **Dashboard View** | 14 | 2 | **15%** | 🔴 CRÍTICA |
| **Audit IA View** | 8 | 0 | **0%** | 🔴 CRÍTICA |
| **Web Auto View** | 6 | 0 | **0%** | 🟠 ALTA |
| **TOTAL** | **65** | **12** | **18.5%** | 🔴 CRÍTICA |

---

## 🎯 COMPONENTES EXISTENTES PERO SIN USAR

### Componentes PySide6 creados pero NO implementados en vistas:

1. ✅ **ChartWidget** (`chart_widget.py` - 280 líneas)
   - Backend Matplotlib con Qt
   - Métodos: `plot_bar()`, `plot_line()`, `plot_pie()`
   - **DISPONIBLE pero NO usado en DashboardView**
   - **IMPACTO:** Los 20 gráficos podrían crearse fácilmente

2. ✅ **DataTable** (`data_table.py` - 350 líneas)
   - QAbstractTableModel completo
   - Virtualización nativa
   - **USADO en DatabaseView pero SIN datos**
   - **IMPACTO:** Tabla funcional esperando conexión

3. ✅ **Workers** (3 archivos creados):
   - `ocr_worker.py` ✅ (conectado parcialmente)
   - `export_worker.py` ⚠️ (creado, no conectado)
   - `audit_worker.py` ⚠️ (creado, no conectado)

---

## 🔗 INTEGRACIONES BACKEND FALTANTES

| Backend Module | TTKBootstrap | PySide6 | Gap |
|---------------|--------------|---------|-----|
| `database_manager.py` | ✅ Completo | ⚠️ Parcial | Sin auto-load |
| `unified_extractor.py` | ✅ Completo | ⚠️ Parcial | Sin progreso real |
| `enhanced_export_system.py` | ✅ Completo | ❌ No conectado | 0% |
| `auditor_sistema.py` (FUNC-01) | ✅ Completo | ❌ No conectado | 0% |
| `auditor_sistema.py` (FUNC-06) | ✅ Completo | ❌ No conectado | 0% |
| `llm_client.py` | ✅ Completo | ❌ No conectado | 0% |
| `huv_web_automation.py` | ✅ Completo | ❌ No conectado | 0% |
| `calendario.py` | ✅ Completo | ❌ No migrado | 0% |

---

## 🚨 IMPACTO EN PRODUCCIÓN

### Si se desplegara PySide6 HOY:

**Features perdidas críticas:**
- ❌ **No se puede auditar con IA** (FUNC-01 ausente)
- ❌ **No se puede reprocesar casos** (FUNC-06 ausente)
- ❌ **No se ven gráficos** (20 gráficos perdidos)
- ❌ **No se detectan duplicados** (importación insegura)
- ❌ **No se puede filtrar** (dashboard ciego)
- ❌ **No se puede ver calendario** (feature completa perdida)
- ❌ **No hay automatización web** (QHORTE manual)

**Features funcionales básicas:**
- ✅ Importar PDFs (sin detección duplicados)
- ✅ Ver tabla de datos (vacía por defecto)
- ✅ Exportar a Excel (worker creado pero no probado)
- ✅ Ver 4 KPIs (con datos falsos hardcoded)

**Veredict final:** **NO listo para producción**
**Recomendación:** Completar al menos vistas 2, 3 y 4 antes de release

---

## 📋 PRIORIDADES DE COMPLETACIÓN

### FASE CRÍTICA (Bloqueante para producción)

**Prioridad 1: Database View (40 horas)**
1. Conectar auto-load de datos (2h)
2. Implementar detección de duplicados (4h)
3. Crear listbox de archivos seleccionados (3h)
4. Agregar color coding (2h)
5. Implementar 14 botones de acción faltantes (15h)
6. Conectar auditoría parcial/completa (6h)
7. Crear panel de detalles flotante (4h)
8. Migrar calendario inteligente (4h)

**Prioridad 2: Dashboard View (25 horas)**
1. Implementar sidebar de filtros (6h)
2. Crear 5 tabs de gráficos (4h)
3. Integrar ChartWidget existente (3h)
4. Generar 20 gráficos con datos reales (10h)
5. Conectar carga dinámica de BD (2h)

**Prioridad 3: Audit IA View (15 horas)**
1. Crear interfaz completa desde cero (8h)
2. Conectar auditor_sistema.py FUNC-01 (3h)
3. Conectar auditor_sistema.py FUNC-06 (2h)
4. Implementar progreso en tiempo real (2h)

### FASE OPCIONAL (Post-lanzamiento)

**Prioridad 4: Web Auto View (12 horas)**
1. Migrar interfaz credenciales (3h)
2. Conectar huv_web_automation.py (5h)
3. Implementar progreso Selenium (4h)

**Prioridad 5: Mejoras Welcome Screen (3 horas)**
1. Agregar header institucional (1h)
2. Implementar detección BD vacía (1h)
3. Mejorar iconos (7 emojis) (1h)

---

## ⏱️ ESTIMACIÓN TOTAL PARA PARIDAD

**Horas necesarias:** ~95 horas
**Días laborales (8h/día):** ~12 días
**Semanas (5 días/semana):** ~2.5 semanas

**Bloqueantes críticos (para producción mínima):**
**Horas críticas:** ~80 horas (Prioridades 1-3)
**Días laborales:** ~10 días
**Semanas:** ~2 semanas

---

## 💡 RECOMENDACIONES

### Opción A: Completar migración completa
- **Tiempo:** 2.5 semanas
- **Resultado:** Paridad 100% con TTKBootstrap
- **Ventaja:** UI profesional lista para comercializar
- **Desventaja:** Tiempo de desarrollo adicional

### Opción B: Migración híbrida (RECOMENDADO)
- **Implementar:** Prioridades 1-3 (80 horas)
- **Dejar en TTKBootstrap:** Web Auto View
- **Tiempo:** 2 semanas
- **Resultado:** 90% paridad, producción viable
- **Ventaja:** Balance tiempo/funcionalidad

### Opción C: Mantener TTKBootstrap
- **Tiempo:** 0 horas
- **Resultado:** Sistema actual funcional al 100%
- **Ventaja:** Sin riesgo de migración
- **Desventaja:** Sin mejoras UI profesionales

---

## 📞 CONCLUSIONES

1. **La migración NO está completa** - Solo 18.5% de funcionalidad migrada
2. **Componentes existen** - ChartWidget, DataTable, Workers están listos
3. **Falta conexión** - 62.5% del backend NO está conectado
4. **Vistas críticas ausentes** - Auditoría IA y Web Auto al 0%
5. **Estimación conservadora** - 80-95 horas para completar

**Estado actual:** ⚠️ **ALFA TEMPRANO** - No listo para producción
**Estado esperado (según docs):** ✅ 60% completo
**Estado real (feature-wise):** ❌ 18.5% completo

---

**Generado:** 20 Noviembre 2025
**Autor:** Sistema de auditoría Claude
**Versión:** 1.0
