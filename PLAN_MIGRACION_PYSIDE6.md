# 🚀 PLAN MAESTRO DE MIGRACIÓN A PYSIDE6

## EVARISIS CIRUGÍA ONCOLÓGICA - Hospital Universitario del Valle

**Versión Actual:** v6.0.9 (TTKBootstrap)
**Versión Objetivo:** v7.0.0 (PySide6)
**Fecha Inicio:** 19 de Noviembre 2025
**Duración Estimada:** 10 semanas (2.5 meses)
**Estado:** 📋 PLANIFICACIÓN

---

## 📊 ANÁLISIS DE SITUACIÓN ACTUAL

### Arquitectura Existente

```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py (6,550 líneas)           ← MONOLITO A REFACTORIZAR
├── test_ui.py (448 líneas)        ← PROTOTIPO PYSIDE6 ✅
├── core/                          ← BACKEND (MANTENER)
│   ├── database_manager.py        → No cambiar
│   ├── unified_extractor.py       → No cambiar
│   ├── debug_mapper.py            → No cambiar
│   ├── validation_checker.py      → No cambiar
│   ├── enhanced_export_system.py  → Adaptar interfaz
│   ├── calendario.py              → Migrar widget
│   ├── ventana_auditoria_ia.py    → Migrar a QDialog
│   └── [19 módulos más]           → Evaluar uno a uno
├── ui_helpers/                    ← HELPERS UI (MIGRAR)
│   ├── ocr_helpers.py             → Adaptar a Qt signals
│   ├── database_helpers.py        → No cambiar
│   ├── export_helpers.py          → Adaptar a Qt
│   └── chart_helpers.py           → Migrar a Qt backend
├── herramientas_ia/               ← IA TOOLS (MANTENER)
│   ├── auditor_sistema.py         → No cambiar
│   ├── gestor_ia_lm_studio.py     → No cambiar
│   └── [4 herramientas más]       → No cambiar
├── config/                        ← CONFIGURACIÓN (MANTENER)
└── requirements.txt               → ACTUALIZAR

Total líneas UI: ~6,550
Total módulos core: 23
Total dependencias: 16
```

### Dependencias Críticas a Migrar

| Dependencia Actual             | Equivalente PySide6       | Acción             |
| ------------------------------ | ------------------------- | ------------------ |
| `ttkbootstrap==1.10.1`         | `PySide6>=6.6.0`          | ✅ Reemplazar      |
| `tksheet>=7.5.0`               | `QTableView + Model`      | ✅ Refactorizar    |
| `matplotlib (Tkinter backend)` | `matplotlib (Qt backend)` | ✅ Cambiar backend |
| `tkinter.messagebox`           | `QMessageBox`             | ✅ Migrar          |
| `tkinter.filedialog`           | `QFileDialog`             | ✅ Migrar          |

### Métricas de Código Actual

- **Líneas totales UI:** 6,550
- **Líneas reutilizables (backend):** ~4,200 (64%)
- **Líneas a migrar (UI pura):** ~2,350 (36%)
- **Reducción esperada:** ~1,500 líneas (componentes Qt)
- **Líneas finales estimadas:** ~4,800 (27% menos código)

---

## 🎯 OBJETIVOS ESTRATÉGICOS

### Objetivos Técnicos

1. ✅ **Arquitectura Modular:** Separar UI en componentes reutilizables
2. ✅ **Rendimiento:** +50% velocidad en tablas (virtualización Qt)
3. ✅ **Diseño Profesional:** CSS completo, gradientes, animaciones GPU
4. ✅ **Mantenibilidad:** Reducir 27% código UI, componentes testables
5. ✅ **Escalabilidad:** Base para plugins, i18n, temas dinámicos

### Objetivos de Negocio

1. 📊 **UX Profesional:** Interfaz al nivel de software médico comercial
2. 🏥 **Presentación Institucional:** Demo para directivos/inversionistas
3. 🚀 **Preparación Comercialización:** Base para licenciamiento a otros hospitales
4. 🔒 **Compatibilidad:** Mantener 100% funcionalidad existente
5. ⚡ **No Disrupción:** Coexistencia TTKBootstrap durante migración

---

## 📅 FASES DE MIGRACIÓN (10 SEMANAS)

### **FASE 0: PREPARACIÓN (Semana 1)**

**Duración:** 5 días
**Objetivo:** Configurar entorno y estructura base

#### Tareas:

- [x] ✅ Crear backup completo del proyecto
- [ ] 🔧 Instalar PySide6 en entorno virtual separado
- [ ] 📁 Crear estructura de carpetas modular
- [ ] 📄 Configurar requirements_pyside6.txt
- [ ] 🎨 Diseñar sistema de temas (QSS)
- [ ] 📋 Crear documento de arquitectura

**Entregables:**

```
pyside6_migration/
├── requirements_pyside6.txt     ← Nuevas dependencias
├── arquitectura.md              ← Diseño técnico
├── themes/                      ← Temas QSS
│   ├── darkly.qss
│   ├── flatly.qss
│   └── medical.qss
└── components/                  ← Base componentes
    └── __init__.py
```

---

### **FASE 1: COMPONENTES BASE (Semanas 2-3)**

**Duración:** 10 días
**Objetivo:** Crear librería de componentes reutilizables

#### Componentes a Desarrollar:

##### 1. Sistema de Temas (3 días)

```python
# components/theme_manager.py
class ThemeManager:
    - load_theme(name: str) → QSS
    - apply_theme(app: QApplication)
    - get_color(key: str) → QColor
    - create_custom_theme(config: dict)
```

##### 2. Componentes UI Base (7 días)

```python
# components/kpi_card.py
class KPICard(QFrame):
    - Tarjetas métricas profesionales
    - Animaciones hover
    - Iconos personalizables

# components/sidebar_nav.py
class SidebarNav(QFrame):
    - Navegación lateral animada
    - Botones con estados
    - Collapse/expand

# components/data_table.py
class DataTable(QTableView):
    - Modelo-vista Qt nativo
    - Filtros integrados
    - Sorting por columna
    - Exportación Excel

# components/chart_widget.py
class ChartWidget(QWidget):
    - Wrapper Matplotlib con backend Qt
    - Soporte PyQtGraph
    - Interactividad completa

# components/dialog_base.py
class DialogBase(QDialog):
    - Dialogs profesionales
    - Botones estándar
    - Animaciones entrada/salida
```

**Entregables:**

- 5 componentes base funcionales
- Tests unitarios para cada componente
- Documentación inline

---

### **FASE 2: VISTAS PRINCIPALES (Semanas 4-6)**

**Duración:** 15 días
**Objetivo:** Migrar las 4 pantallas principales

#### Vista 1: Welcome Screen (3 días)

```python
# views/welcome_view.py
class WelcomeView(QWidget):
    - Pantalla bienvenida institucional
    - Accesos rápidos
    - Información de versión
    - Animaciones entrada
```

**Migración desde:** ui.py:3121-3248

#### Vista 2: Database View (5 días)

```python
# views/database_view.py
class DatabaseView(QWidget):
    - Tab importación PDFs
    - Tab visualizador datos (QTableView)
    - Tab calendario
    - Detección duplicados
```

**Migración desde:** ui.py:1906-2171

**Componentes críticos:**

- Sistema de importación OCR
- Tabla virtualizada (tksheet → QTableView + QAbstractTableModel)
- Filtros avanzados

#### Vista 3: Dashboard View (4 días)

```python
# views/dashboard_view.py
class DashboardView(QWidget):
    - Grid de KPIs (usar KPICard)
    - Gráficos Matplotlib/PyQtGraph
    - Métricas en tiempo real
```

**Migración desde:** ui.py:2507-3109

#### Vista 4: Auditoría IA View (3 días)

```python
# views/audit_ia_view.py
class AuditIAView(QWidget):
    - Integración con auditor_sistema.py
    - Progreso en tiempo real (QProgressBar)
    - Resultados interactivos
```

**Migración desde:** ui.py:707-1562

**Entregables:**

- 4 vistas completas y funcionales
- Integración con backend existente (core/)
- Tests de integración

---

### **FASE 3: INTEGRACIÓN BACKEND (Semanas 7-8)**

**Duración:** 10 días
**Objetivo:** Conectar vistas con lógica de negocio

#### Tareas por Módulo:

##### 1. Database Manager (2 días)

- ✅ Mantener sin cambios
- Crear signals Qt para notificaciones de BD
- Wrapper para threading Qt (QThread)

##### 2. Unified Extractor (2 días)

- ✅ Mantener sin cambios
- Progress signals para QProgressBar
- Error handling con QMessageBox

##### 3. Export System (2 días)

```python
# Migrar de:
EnhancedExportSystem(self)  # TTKBootstrap

# A:
EnhancedExportSystemQt(self)  # PySide6
    - QFileDialog para selección
    - QProgressDialog para progreso
    - Signals para completado
```

##### 4. Helpers UI (2 días)

```python
# ui_helpers/ocr_helpers.py → Migrar a Qt signals
class OCRProcessor(QObject):
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

# ui_helpers/chart_helpers.py → Backend Qt
matplotlib.use('QtAgg')  # Cambiar backend
```

##### 5. Ventanas Modales (2 días)

```python
# core/ventana_auditoria_ia.py → QDialog
# core/ventana_selector_auditoria.py → QDialog
# core/ventana_resultados_importacion.py → QDialog
```

**Entregables:**

- Backend 100% compatible con PySide6
- Sin cambios en lógica de negocio
- Signals/slots Qt implementados

---

### **FASE 4: FEATURES AVANZADAS (Semana 9)**

**Duración:** 5 días
**Objetivo:** Implementar capacidades exclusivas de Qt

#### Features a Implementar:

##### 1. Animaciones (2 días)

```python
from PySide6.QtCore import QPropertyAnimation, QEasingCurve

# Transiciones de página suaves
# Sidebar colapsable animado
# Fade in/out de dialogs
# Hover effects en botones
```

##### 2. Gráficos Real-Time (1 día)

```python
import pyqtgraph as pg

# Dashboard con actualización 60fps
# Monitoreo de procesamiento OCR
# Estadísticas en tiempo real
```

##### 3. Sistema de Notificaciones (1 día)

```python
from PySide6.QtWidgets import QSystemTrayIcon

# Notificaciones sistema
# Icono en bandeja
# Mensajes de completado
```

##### 4. Shortcuts de Teclado (1 día)

```python
from PySide6.QtGui import QShortcut, QKeySequence

# Ctrl+N → Nueva importación
# Ctrl+E → Exportar
# Ctrl+F → Buscar
# F5 → Actualizar dashboard
```

**Entregables:**

- Animaciones fluidas en toda la app
- Dashboard con gráficos real-time
- Sistema de notificaciones funcional
- Shortcuts documentados

---

### **FASE 5: TESTING Y OPTIMIZACIÓN (Semana 10)**

**Duración:** 5 días
**Objetivo:** Validación completa y pulido final

#### Testing:

##### 1. Tests Unitarios (2 días)

```python
# tests/test_components.py
def test_kpi_card_creation()
def test_sidebar_navigation()
def test_data_table_filtering()
def test_theme_switching()

# tests/test_views.py
def test_welcome_view_load()
def test_database_import()
def test_dashboard_metrics()
def test_audit_ia_workflow()
```

##### 2. Tests de Integración (1 día)

```python
# tests/integration/test_ocr_workflow.py
def test_full_ocr_import_workflow()
def test_duplicate_detection()
def test_export_to_excel()

# tests/integration/test_audit_workflow.py
def test_parcial_audit()
def test_completa_audit()
```

##### 3. Optimización de Rendimiento (1 día)

- Profiling con cProfile
- Optimizar lazy loading
- Cachear queries BD
- Virtualización tablas grandes

##### 4. Validación de Usuario (1 día)

- Testing con usuarios reales
- Feedback UX
- Ajustes finales

**Entregables:**

- Suite de tests completa (>80% cobertura)
- Benchmarks de rendimiento
- Reporte de validación de usuarios
- App lista para producción

---

## 🏗️ ARQUITECTURA MODULAR PROPUESTA

### Estructura de Carpetas Final

```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── main_pyside6.py                 ← NUEVO: Entry point PySide6
├── ui.py                           ← MANTENER: Entry point TTKBootstrap (legacy)
├── test_ui.py                      ← PROTOTIPO: Referencia
│
├── pyside6_ui/                     ← NUEVA CARPETA PRINCIPAL
│   ├── __init__.py
│   ├── app.py                      ← Aplicación principal (QMainWindow)
│   │
│   ├── components/                 ← Componentes reutilizables
│   │   ├── __init__.py
│   │   ├── kpi_card.py             ← Tarjetas métricas
│   │   ├── sidebar_nav.py          ← Navegación lateral
│   │   ├── data_table.py           ← Tabla virtualizada
│   │   ├── chart_widget.py         ← Gráficos
│   │   ├── dialog_base.py          ← Dialogs base
│   │   ├── progress_widget.py      ← Barras de progreso
│   │   └── theme_manager.py        ← Sistema de temas
│   │
│   ├── views/                      ← Vistas principales
│   │   ├── __init__.py
│   │   ├── welcome_view.py         ← Pantalla bienvenida
│   │   ├── database_view.py        ← Gestión BD
│   │   ├── dashboard_view.py       ← Dashboard métricas
│   │   ├── audit_ia_view.py        ← Auditoría IA
│   │   └── web_auto_view.py        ← QHORTE (futuro)
│   │
│   ├── dialogs/                    ← Ventanas modales
│   │   ├── __init__.py
│   │   ├── audit_dialog.py         ← Auditoría IA
│   │   ├── selector_dialog.py      ← Selector auditoría
│   │   ├── results_dialog.py       ← Resultados importación
│   │   └── settings_dialog.py      ← Configuración
│   │
│   ├── workers/                    ← QThread workers
│   │   ├── __init__.py
│   │   ├── ocr_worker.py           ← Procesamiento OCR
│   │   ├── export_worker.py        ← Exportación
│   │   └── audit_worker.py         ← Auditoría IA
│   │
│   ├── models/                     ← Modelos Qt (Model-View)
│   │   ├── __init__.py
│   │   ├── database_model.py       ← QAbstractTableModel para BD
│   │   └── filter_proxy.py         ← QSortFilterProxyModel
│   │
│   ├── resources/                  ← Recursos Qt compilados
│   │   ├── resources.qrc           ← Archivo de recursos
│   │   ├── resources_rc.py         ← Compilado (generado)
│   │   ├── icons/                  ← Iconos SVG
│   │   ├── images/                 ← Imágenes
│   │   └── fonts/                  ← Fuentes custom
│   │
│   └── themes/                     ← Temas QSS
│       ├── darkly.qss
│       ├── flatly.qss
│       ├── medical.qss
│       └── custom.qss
│
├── core/                           ← MANTENER SIN CAMBIOS
│   ├── [23 módulos existentes]    ← Backend no cambia
│   └── qt_adapters/                ← NUEVO: Adaptadores Qt
│       ├── __init__.py
│       └── signal_adapters.py      ← Signals para Qt
│
├── ui_helpers/                     ← ADAPTAR A QT
│   ├── ocr_helpers_qt.py           ← Versión Qt (con signals)
│   ├── database_helpers.py         ← Sin cambios
│   ├── export_helpers_qt.py        ← Versión Qt
│   └── chart_helpers_qt.py         ← Backend Qt
│
├── herramientas_ia/                ← MANTENER SIN CAMBIOS
│   └── [6 herramientas]            ← Backend IA no cambia
│
├── config/                         ← MANTENER
│   ├── version_info.py             ← Actualizar a v7.0.0
│   └── config.ini
│
├── tests/                          ← NUEVA CARPETA
│   ├── __init__.py
│   ├── test_components.py
│   ├── test_views.py
│   ├── test_models.py
│   └── integration/
│       ├── test_ocr_workflow.py
│       └── test_audit_workflow.py
│
├── docs/                           ← DOCUMENTACIÓN
│   ├── MIGRACION_PYSIDE6.md        ← Este archivo
│   ├── ARQUITECTURA.md             ← Diseño técnico
│   ├── COMPONENTES.md              ← Guía de componentes
│   └── API_REFERENCE.md            ← Referencia API
│
├── requirements.txt                ← MANTENER (TTKBootstrap)
├── requirements_pyside6.txt        ← NUEVO (PySide6)
└── pyproject.toml                  ← NUEVO (empaquetado moderno)
```

### Tamaño Estimado de Archivos

| Archivo                      | Líneas | Descripción                 |
| ---------------------------- | ------ | --------------------------- |
| `main_pyside6.py`            | ~50    | Entry point                 |
| `pyside6_ui/app.py`          | ~300   | Aplicación principal        |
| **Componentes (7 archivos)** | ~1,200 | Componentes reutilizables   |
| **Vistas (5 archivos)**      | ~2,000 | Vistas principales          |
| **Dialogs (4 archivos)**     | ~800   | Ventanas modales            |
| **Workers (3 archivos)**     | ~400   | Threading                   |
| **Models (2 archivos)**      | ~300   | Modelos Qt                  |
| **TOTAL NUEVO CÓDIGO**       | ~5,050 | vs 6,550 actual (23% menos) |

---

## 🔄 ESTRATEGIA DE COEXISTENCIA

### Dual-Mode Durante Migración

```python
# main.py (punto de entrada único)
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ui', choices=['tkinter', 'pyside6'], default='tkinter')
    args = parser.parse_args()

    if args.ui == 'pyside6':
        # Lanzar versión PySide6 (nueva)
        from pyside6_ui.app import run_app
        run_app()
    else:
        # Lanzar versión TTKBootstrap (actual)
        import ui
        ui.main()

if __name__ == "__main__":
    main()
```

### Testing Gradual

1. **Semanas 1-4:** Solo desarrollo en PySide6
2. **Semanas 5-8:** Testing paralelo (usuarios alpha en PySide6)
3. **Semanas 9-10:** Todos en PySide6, TTKBootstrap como fallback
4. **Post-lanzamiento:** Deprecar TTKBootstrap en v7.1.0

---

## 📦 DEPENDENCIAS ACTUALIZADAS

### requirements_pyside6.txt

```txt
# === FRAMEWORK UI PRINCIPAL ===
PySide6>=6.6.0                      # Qt6 framework completo
PySide6-Addons>=6.6.0               # Módulos adicionales Qt
qt-material>=2.14                   # Material Design para Qt

# === GRÁFICOS AVANZADOS ===
pyqtgraph>=0.13.3                   # Gráficos real-time 60fps
matplotlib>=3.8.0                   # Gráficos científicos
seaborn>=0.13.0                     # Visualización estadística

# === BACKEND (MANTENER) ===
numpy>=1.24.0
pandas>=2.0.0
pytesseract>=0.3.10
PyMuPDF>=1.23.0
pillow>=10.0.0
selenium>=4.15.0
webdriver-manager>=4.0.0
openpyxl>=3.1.0
python-dateutil>=2.8.0
Babel>=2.12.0
holidays>=0.34
cryptography>=41.0.0
psutil>=5.9.0

# === TESTING ===
pytest>=7.0.0
pytest-qt>=4.2.0                    # Testing específico Qt
pytest-cov>=4.0.0

# === COMPILACIÓN ===
pyinstaller>=6.0.0
nuitka>=1.9.0                       # Alternativa a PyInstaller (mejor rendimiento)

# === DESARROLLO ===
black>=23.0.0                       # Formatter
pylint>=3.0.0                       # Linter
```

---

## 🎨 SISTEMA DE TEMAS

### Temas Predefinidos

#### 1. Darkly (Modo Oscuro Profesional)

```css
/* themes/darkly.qss */
QMainWindow {
  background-color: #1e1e2e;
}

QFrame#SidebarFrame {
  background: qlineargradient(
    x1: 0,
    y1: 0,
    x2: 1,
    y2: 0,
    stop: 0 #252538,
    stop: 1 #2a2a3e
  );
  border-right: 1px solid #3f3f55;
}

QPushButton.NavButton:checked {
  background-color: qlineargradient(
    x1: 0,
    y1: 0,
    x2: 1,
    y2: 0,
    stop: 0 #3b82f6,
    stop: 1 #2563eb
  );
  color: white;
  border-left: 4px solid #60a5fa;
}

QFrame.KPICard {
  background-color: #252538;
  border-radius: 12px;
  border: 1px solid #3f3f55;
}

QFrame.KPICard:hover {
  border: 1px solid #3b82f6;
  /* Animación via QPropertyAnimation en Python */
}
```

#### 2. Medical (Tema Hospitalario)

```css
/* themes/medical.qss */
QMainWindow {
  background-color: #f0f4f8;
}

QFrame#SidebarFrame {
  background-color: #ffffff;
  border-right: 2px solid #0ea5e9;
}

QPushButton.NavButton:checked {
  background-color: #0ea5e9;
  color: white;
}

QFrame.KPICard {
  background-color: white;
  border: 1px solid #e2e8f0;
  border-left: 4px solid #0ea5e9;
}
```

### Sistema Dinámico de Temas

```python
# components/theme_manager.py
from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from pathlib import Path

class ThemeManager(QObject):
    theme_changed = Signal(str)

    THEMES = {
        'darkly': 'themes/darkly.qss',
        'flatly': 'themes/flatly.qss',
        'medical': 'themes/medical.qss',
        'custom': 'themes/custom.qss'
    }

    def __init__(self):
        super().__init__()
        self.current_theme = 'darkly'

    def load_theme(self, theme_name: str):
        """Cargar y aplicar tema"""
        theme_path = Path(__file__).parent.parent / self.THEMES[theme_name]

        with open(theme_path, 'r', encoding='utf-8') as f:
            qss = f.read()

        QApplication.instance().setStyleSheet(qss)
        self.current_theme = theme_name
        self.theme_changed.emit(theme_name)

    def get_color(self, key: str) -> str:
        """Obtener color del tema actual"""
        colors = {
            'darkly': {
                'primary': '#3b82f6',
                'success': '#10b981',
                'danger': '#ef4444',
                'warning': '#f59e0b',
                'background': '#1e1e2e',
                'surface': '#252538',
                'text': '#ffffff',
                'text-muted': '#a1a1aa'
            },
            'medical': {
                'primary': '#0ea5e9',
                'success': '#14b8a6',
                'danger': '#f43f5e',
                'warning': '#f59e0b',
                'background': '#f0f4f8',
                'surface': '#ffffff',
                'text': '#1e293b',
                'text-muted': '#64748b'
            }
        }

        return colors.get(self.current_theme, {}).get(key, '#000000')
```

---

## 🧪 ESTRATEGIA DE TESTING

### Testing Unitario (Componentes)

```python
# tests/test_components.py
import pytest
from PySide6.QtWidgets import QApplication
from pyside6_ui.components.kpi_card import KPICard

@pytest.fixture(scope='session')
def qapp():
    """Fixture para QApplication"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app

def test_kpi_card_creation(qapp):
    """Test creación básica de KPICard"""
    card = KPICard("Total Casos", "1,245", "📁", "#3b82f6")
    assert card is not None
    assert card.windowTitle() == ""  # No debe tener título

def test_kpi_card_update_value(qapp):
    """Test actualización de valor"""
    card = KPICard("Total Casos", "1,245", "📁", "#3b82f6")
    card.update_value("2,500")
    # Verificar que el label interno cambió
    assert "2,500" in card.findChild(QLabel).text()
```

### Testing de Integración (Workflows)

```python
# tests/integration/test_ocr_workflow.py
import pytest
from pathlib import Path
from pyside6_ui.app import EvarisisApp
from core.ihq_processor import process_pdf

@pytest.fixture
def app(qapp, tmp_path):
    """Fixture para aplicación completa"""
    return EvarisisApp()

def test_full_ocr_import_workflow(app, tmp_path):
    """Test workflow completo de importación OCR"""
    # 1. Seleccionar PDF de prueba
    test_pdf = Path("tests/fixtures/caso_prueba.pdf")

    # 2. Simular importación
    app.database_view.import_pdf(test_pdf)

    # 3. Verificar procesamiento
    assert app.database_view.import_status == "completed"

    # 4. Verificar registro en BD
    from core.database_manager import get_all_records_as_dataframe
    df = get_all_records_as_dataframe()
    assert len(df) > 0

    # 5. Verificar debug_map generado
    debug_map_path = tmp_path / "debug_maps" / f"debug_map_{df.iloc[0]['numero_peticion']}_*.json"
    assert debug_map_path.exists()
```

### Benchmarking de Rendimiento

```python
# tests/performance/test_table_performance.py
import pytest
import time
from pyside6_ui.views.database_view import DatabaseView

def test_table_large_dataset_performance(qapp, benchmark):
    """Test rendimiento tabla con dataset grande"""
    view = DatabaseView()

    # Generar dataset de 10,000 registros
    large_df = generate_test_dataframe(10000)

    # Benchmark: Cargar datos en tabla
    def load_data():
        view.load_dataframe(large_df)

    result = benchmark(load_data)

    # Verificar que carga en menos de 1 segundo
    assert result.stats['mean'] < 1.0
```

---

## 📈 MÉTRICAS DE ÉXITO

### KPIs de Migración

| Métrica                       | Objetivo      | Cómo Medir                     |
| ----------------------------- | ------------- | ------------------------------ |
| **Reducción código UI**       | -27%          | Líneas de código               |
| **Mejora rendimiento tablas** | +50%          | Benchmark loading 10k rows     |
| **Startup time**              | -30%          | Tiempo hasta UI visible        |
| **Memory footprint**          | Igual o menor | psutil.Process().memory_info() |
| **Test coverage**             | >80%          | pytest-cov                     |
| **Bugs críticos**             | 0             | GitHub Issues                  |
| **Satisfacción usuario**      | >4/5          | Encuesta post-migración        |

### Checklist de Calidad

- [ ] ✅ Todas las features actuales funcionan en PySide6
- [ ] ✅ No hay regresiones en funcionalidad
- [ ] ✅ Tests unitarios pasan al 100%
- [ ] ✅ Tests de integración pasan al 100%
- [ ] ✅ Rendimiento igual o superior a TTKBootstrap
- [ ] ✅ Documentación completa de componentes
- [ ] ✅ Temas funcionan correctamente
- [ ] ✅ Animaciones fluidas (60fps)
- [ ] ✅ Shortcuts de teclado documentados
- [ ] ✅ Sistema de notificaciones operativo

---

## 🚨 RIESGOS Y MITIGACIÓN

### Riesgos Identificados

| Riesgo                       | Probabilidad | Impacto | Mitigación                                    |
| ---------------------------- | ------------ | ------- | --------------------------------------------- |
| **Incompatibilidad backend** | Baja         | Alto    | Mantener core/ sin cambios, adapters Qt       |
| **Curva aprendizaje Qt**     | Media        | Medio   | Prototipo test_ui.py, documentación Qt        |
| **Bugs PySide6**             | Media        | Medio   | Usar versión estable 6.6.0, tests exhaustivos |
| **Rendimiento inferior**     | Baja         | Alto    | Benchmarks continuos, optimización early      |
| **Tiempo excedido**          | Media        | Medio   | Buffer 2 semanas, fases ajustables            |
| **Resistencia usuarios**     | Baja         | Medio   | Demo early, feedback continuo                 |

### Plan de Rollback

Si en Semana 8 se identifica que la migración no es viable:

1. **Mantener TTKBootstrap** como versión principal
2. **Extraer componentes útiles** de PySide6 (temas QSS como CSS)
3. **Refactorizar ui.py** modularmente pero en TTKBootstrap
4. **Aprendizajes documentados** para futuras mejoras

---

## 📚 RECURSOS Y REFERENCIAS

### Documentación Oficial

- **PySide6 Docs:** https://doc.qt.io/qtforpython-6/
- **Qt6 QSS Reference:** https://doc.qt.io/qt-6/stylesheet-reference.html
- **PyQtGraph Docs:** https://pyqtgraph.readthedocs.io/
- **qt-material:** https://github.com/UN-GCPDS/qt-material

### Tutoriales Recomendados

- **Python GUIs (Martin Fitzpatrick):** https://www.pythonguis.com/
- **Qt for Python Examples:** https://github.com/qt/pyside-setup/tree/dev/examples
- **Real Python Qt Tutorial:** https://realpython.com/python-pyqt-gui-calculator/

### Herramientas de Desarrollo

- **Qt Designer:** Diseñador visual de UI (incluido con PySide6)
- **Qt Creator:** IDE completo para Qt
- **pytest-qt:** Framework de testing para Qt

---

## 👥 EQUIPO Y ROLES

### Roles Necesarios

| Rol                         | Responsabilidad           | Tiempo Dedicación  |
| --------------------------- | ------------------------- | ------------------ |
| **Desarrollador Principal** | Migración completa        | 100% (10 semanas)  |
| **Revisor Técnico**         | Code review, arquitectura | 20%                |
| **Tester QA**               | Testing funcional, UX     | 30% (semanas 8-10) |
| **Usuario Alpha**           | Feedback temprano         | 5% (semanas 6-10)  |

### Equipo Actual

- **Desarrollador:** Innovación y Desarrollo (Ingenieros de soluciones)
- **Líder Investigación:** Dr. Juan Camilo Bayona
- **Jefe TI:** Ing. Diego Peña

---

## 📅 CRONOGRAMA DETALLADO

### Vista Gantt Simplificada

```
Semana  | Fase                    | Entregables
--------|-------------------------|----------------------------------
   1    | PREPARACIÓN             | Estructura base, temas QSS
  2-3   | COMPONENTES BASE        | 5 componentes reutilizables
  4-6   | VISTAS PRINCIPALES      | 4 vistas completas
  7-8   | INTEGRACIÓN BACKEND     | Backend conectado, signals Qt
   9    | FEATURES AVANZADAS      | Animaciones, real-time, shortcuts
   10   | TESTING Y OPTIMIZACIÓN  | Tests >80%, benchmarks, release
```

### Hitos Críticos

- **Día 5:** ✅ Estructura base creada
- **Día 15:** ✅ Primer componente funcional (KPICard)
- **Día 25:** ✅ Welcome View completa
- **Día 40:** ✅ Database View funcional
- **Día 50:** ✅ Backend integrado
- **Día 60:** ✅ Features avanzadas implementadas
- **Día 70:** ✅ App lista para producción (v7.0.0)

---

## 🎯 PRÓXIMOS PASOS INMEDIATOS

### Semana 1 - Tareas Concretas

#### Día 1-2: Setup Entorno

```bash
# 1. Crear entorno virtual PySide6
python -m venv venv_pyside6
venv_pyside6\Scripts\activate

# 2. Instalar dependencias base
pip install PySide6>=6.6.0 PySide6-Addons qt-material

# 3. Verificar instalación
python -c "from PySide6.QtWidgets import QApplication; print('OK')"

# 4. Copiar test_ui.py como base
copy test_ui.py pyside6_ui\app_base.py
```

#### Día 3: Estructura de Carpetas

```bash
# Crear estructura modular
mkdir pyside6_ui
mkdir pyside6_ui\components
mkdir pyside6_ui\views
mkdir pyside6_ui\dialogs
mkdir pyside6_ui\workers
mkdir pyside6_ui\models
mkdir pyside6_ui\themes
mkdir pyside6_ui\resources
mkdir tests
mkdir docs

# Crear archivos __init__.py
type nul > pyside6_ui\__init__.py
type nul > pyside6_ui\components\__init__.py
type nul > pyside6_ui\views\__init__.py
# ... etc
```

#### Día 4-5: Primer Tema QSS

```python
# Crear themes/darkly.qss basado en test_ui.py
# Crear components/theme_manager.py
# Test: Aplicación con tema cargado dinámicamente
```

---

## 📄 DOCUMENTACIÓN A GENERAR

### Documentos Requeridos

1. **ARQUITECTURA.md** (Día 5)
   - Diagrama de componentes
   - Flujo de datos
   - Patrones de diseño

2. **COMPONENTES.md** (Semana 3)
   - API de cada componente
   - Ejemplos de uso
   - Props y signals

3. **GUIA_MIGRACION.md** (Semana 10)
   - Lecciones aprendidas
   - Problemas comunes
   - Soluciones

4. **API_REFERENCE.md** (Semana 10)
   - Referencia completa de API
   - Índice de funciones/clases
   - Ejemplos de código

---

## 🏁 CRITERIOS DE ACEPTACIÓN FINAL

### App Lista para Producción v7.0.0 Cuando:

- [x] ✅ Backup completo del proyecto creado
- [ ] ✅ 100% funcionalidad actual replicada en PySide6
- [ ] ✅ Tests unitarios >80% cobertura
- [ ] ✅ Tests de integración pasan al 100%
- [ ] ✅ Rendimiento >= TTKBootstrap (benchmarks)
- [ ] ✅ 3 temas QSS funcionales (darkly, flatly, medical)
- [ ] ✅ Animaciones implementadas y fluidas
- [ ] ✅ Documentación completa generada
- [ ] ✅ Testing con 3 usuarios alpha exitoso
- [ ] ✅ No bugs críticos abiertos
- [ ] ✅ Instalador/ejecutable funcional

---

## 📞 CONTACTO Y SOPORTE

### Durante Migración

- **Developer:** Innovación y Desarrollo (innovacionydesarrollo@correohuv.gov.co)
- **Issues GitHub:** ProyectoHUV9GESTOR_ONCOLOGIA/issues
- **Slack Channel:** #pyside6-migration (crear)

---

**Estado Actual:** 📋 Plan aprobado, iniciando FASE 0
**Próxima Revisión:** Día 5 (Fin Semana 1)
**Versión Documento:** 1.0 (19 Nov 2025)

---

_Este documento es un plan vivo. Se actualizará semanalmente con progreso real._
