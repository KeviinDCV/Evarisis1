Changelog

Este proyecto sigue versionamiento semantico.

## [3.5] - 2025-09-24

### ADDED
- **Sistema de Navegación Floating**: Implementación completa de menú flotante animado con botones de navegación rápida entre módulos principales
- **Animaciones UI Profesionales**: Sistema de animaciones fluidas para elementos flotantes con efectos de aparición/desaparición progresivos
- **Navegación Fluida Entre Paneles**: Métodos especializados `_nav_to_*` para transiciones seamless entre Welcome, Database, Dashboard, Web Automation y Visualización
- **Sistema Scrollable Frames Mejorado**: Implementación optimizada de contenido scrollable con mejor manejo de overflow y responsive design
- **Arquitectura Modular UI**: Separación clara de responsabilidades con métodos `_create_*` para cada componente de interfaz
- **Palabras Clave IHQ Especializadas**: Nueva constante `MALIGNIDAD_KEYWORDS_IHQ` en `huv_constants.py` con términos oncológicos específicos expandidos
- **Parámetros de Usuario**: Sistema `info_usuario` en constructor `App()` para personalización de usuario
- **Control de Versiones**: Integración Git con `.gitattributes`, `.gitignore` y configuración VS Code
- **Directorios de Distribución**: Carpetas `build/`, `dist/` para empaquetado y distribución

### CHANGED
- **MIGRACIÓN FRAMEWORK UI CRÍTICA**: Transición completa de CustomTkinter → TTKBootstrap como framework principal de interfaz
- **Arquitectura de Clases Renovada**: `class App(ttk.Window)` reemplaza `class App(ctk.CTk)` con mejor integración bootstrap themes
- **Sistema de Importaciones Actualizado**: `import ttkbootstrap as ttk` sustituye `import customtkinter as ctk` manteniendo compatibilidad
- **Expansión Masiva de Código UI**: `ui.py` crecimiento de 59,043 → 136,021 bytes (+130%) reflejando nueva funcionalidad floating navigation
- **Mejoras en Procesador IHQ**: `procesador_ihq.py` expandido de 22,794 → 31,950 bytes (+40%) con funcionalidades mejoradas
- **Constantes Médicas Ampliadas**: `huv_constants.py` crecimiento de 4,996 → 6,628 bytes (+32%) con vocabulario oncológico expandido
- **Mejoras en Experiencia Usuario**: Interface más moderna y responsive con mejor feedback visual y navegación intuitiva

### REMOVED
- **Suite de Pruebas**: Eliminación de `test_sistema.py` (5,003 bytes) - funcionalidad de testing migrada o refactorizada

### TECHNICAL NOTES
- Mantiene compatibilidad con configuraciones existentes (config.ini idéntico)
- Requirements.txt preserva ambos frameworks durante período de transición
- Base de datos y lógica de negocio permanecen inalteradas (database_manager.py sin cambios)
- Arquitectura modular permite rollback selectivo de componentes UI
- Archivos core sin cambios: `calendario.py`, `crear_ejecutable.py`, `huv_web_automation.py`, `ocr_processing.py`, `procesador_ihq_biomarcadores.py`

[Unreleased]
- **CONSOLIDACIÓN COMPLETA SYSTEMPROMPT**: Finalización protocolo análisis SYSTEMPROMPT con reporte navegación ChatGPT.
- **REPORTE_CHATGPT.md completo**: Mapa navegable proyecto con rutas absolutas Drive, componentes principales, flujos pipeline y comandos navegación.
- **28 Plantillas NotebookLM**: Contenido especializado para 4 audiencias (Médico oncológico, Desarrollo, Dirección, Investigadores) en formatos audio, video y cuestionarios.
- **Navegación IA Externa**: Estructura optimizada para ChatGPT con referencias exactas archivo:línea y flujos consulta típicos por dominio técnico/médico.
- Integracion completa de Biopsia/Autopsia al flujo persistente y dashboards.
- Sincronizacion incremental con Power BI y agendas clinicas.
- Hardening de pruebas automaticas de extraccion y visualizacion.

---

## ANÁLISIS DETALLADO V3.5 vs LEGACY V2.5.0

### 🎯 MIGRACIÓN ARQUITECTÓNICA CRÍTICA: CustomTkinter → TTKBootstrap

#### Cambios Fundamentales en `ui.py` (+130% crecimiento)
```python
# LEGACY v2.5.0 (59,043 bytes - 1,299 líneas)
import customtkinter as ctk
class App(ctk.CTk):  # línea 48
    def __init__(self):
        super().__init__()
        
# Navegación LEGACY: Sistema tabs estático
self.tabs = ttk.Notebook(main)  # línea 382
self.tabs.add(self.tab_overview, text="Overview")
self.tabs.add(self.tab_biomarkers, text="Biomarcadores")  
self.tabs.add(self.tab_times, text="Tiempos")
self.tabs.add(self.tab_quality, text="Calidad")
self.tabs.add(self.tab_compare, text="Comparador")

# Tema LEGACY: Fijo dark-blue
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
```

```python
# ACTUAL v3.5 (136,021 bytes - 3,121 líneas)
import ttkbootstrap as ttk
class App(ttk.Window):  # línea 117
    def __init__(self, info_usuario=None, tema="superhero"):
        super().__init__(themename=tema)
        
# Navegación ACTUAL: Sistema floating dinámico
self._create_floating_menu()    # línea 183
self._create_floating_button()  # línea 186
self.floating_menu.place(x=-300, y=20, width=280, height=420)
self.floating_btn_container.place(x=15, y=150, width=50, height=50)

# Temas ACTUAL: 18 intercambiables
self.temas_disponibles = [
    'superhero', 'flatly', 'cyborg', 'journal', 'solar', 'darkly', 
    'minty', 'pulse', 'sandstone', 'united', 'morph', 'vapor'
]
```

#### Nuevas Funcionalidades UI Implementadas
- **Floating Navigation**: Sistema de menú deslizable con animaciones
- **User Profile Integration**: Parámetro `info_usuario` con foto y cargo
- **Theme Switching**: 18 themes TTKBootstrap intercambiables en runtime
- **Hover Effects**: Animaciones hover en botones flotantes
- **Modern Layout**: Diseño responsive con mejor UX

### 🧬 MEJORAS EN PROCESAMIENTO IHQ (+40% crecimiento)

#### `procesador_ihq.py`: 22,794 → 31,950 bytes (+219 líneas)
```python
# LEGACY v2.5.0 (443 líneas)
- Funcionalidad básica extracción IHQ
- Patrones de reconocimiento limitados

# ACTUAL v3.5 (662 líneas)  
- Nuevos patrones de órganos específicos:
  r'NEFRECTOMIA\s+(?:RADICAL\s+)?(?:IZQUIERDA|DERECHA|BILATERAL)?'
  r'HISTERECTOMIA\s+(?:TOTAL|RADICAL)?'
  r'(?:UTERO|CERVIX|OVARIO|ENDOMETRIO)'
- Mejor fallback para detección órganos
- Refinamientos algoritmos extracción datos
```

### 🏥 EXPANSIÓN VOCABULARIO MÉDICO (+32% crecimiento)

#### `huv_constants.py`: 4,996 → 6,628 bytes (+1,632 bytes)
```python
# NUEVO EN v3.5: MALIGNIDAD_KEYWORDS_IHQ
MALIGNIDAD_KEYWORDS_IHQ = [
    'CARCINOMA', 'ADENOCARCINOMA', 'SARCOMA', 'MELANOMA',
    'LINFOMA', 'METASTASIS', 'TUMOR MALIGNO', 'NEOPLASIA MALIGNA',
    'CARCINOMA UROTELIAL', 'CARCINOMA BASOCELULAR', 
    'CARCINOMA ESCAMOCELULAR', 'CARCINOMA DUCTAL INVASIVO',
    # ... 50+ términos oncológicos especializados
]
```

### 📁 CAMBIOS EN ESTRUCTURA DE ARCHIVOS

#### Archivos ELIMINADOS de v2.5.0
- `test_sistema.py` (5,003 bytes) - Suite de pruebas automatizadas

#### Archivos/Directorios NUEVOS en v3.5  
- `.vscode/` - Configuración VS Code workspace
- `build/`, `dist/` - Directorios distribución y empaquetado
- `.git*` - Control de versiones Git integrado
- `daniel.jpeg` - Recurso imagen usuario

#### Archivos SIN CAMBIOS (Idénticos)
- `database_manager.py` - Lógica BD intacta
- `calendario.py` - Funcionalidad calendario preservada  
- `config.ini` - Configuración compatible
- `requirements.txt` - Dependencias mantenidas

2025-09-22 — docs - SYSTEMPROMPT Analysis
- **DOCUMENTACIÓN TÉCNICA MODULAR COMPLETA**: Análisis exhaustivo de 10 componentes críticos del sistema siguiendo protocolo SYSTEMPROMPT con 12 secciones por componente.
- **Análisis técnico evidence-based**: Documentación con referencias exactas archivo:línea para cada componente del pipeline OCR.
- **Arquitectura médica especializada**: Documentación profunda del dominio oncológico HUV con vocabulario biomarcadores, patrones extracción y flujos clínicos.
- **Componentes analizados**: 
  - `01_huv_ocr_sistema_definitivo.md` - Entry point y configuración Tesseract
  - `02_ui.md` - Interfaz CustomTkinter 1299 líneas con 4 tabs especializados
  - `03_ocr_processing.md` - Engine OCR híbrido PyMuPDF/Tesseract con limpieza médica
  - `04_procesador_ihq_biomarcadores.md` - Extractor biomarcadores HER2/Ki-67/RE/RP/PD-L1 
  - `05_database_manager.md` - Gestor SQLite con esquema 167 campos transaccional
  - `06_huv_web_automation.md` - Automatización portal Selenium con error recovery
  - `07_calendario.md` - Scheduler interno tareas automatizadas con threading
  - `08_huv_constants.md` - Vocabulario médico centralizado y patrones regex
  - `09_config.ini.md` - Configuración multiplataforma con detección OS
  - `10_test_sistema.py.md` - Suite pruebas automatizadas con fixtures médicas
- **Gestión técnica**: Identificación riesgos médicos críticos, deuda técnica, puntos extensión y estrategias optimización por componente.
- **Cobertura completa**: Desde entry point hasta testing, incluyendo seguridad datos médicos, performance OCR y mantenibilidad arquitectura.
- **Documentación EVARISIS**: Actualización README.md, INFORME_GLOBAL_PROYECTO.md, INICIO_RAPIDO.md con nueva arquitectura v2.5.

2025-09-20 — docs
- Generado/actualizado `documentacion/REPORTE_CHATGPT.md` con el mapa del proyecto.
- Enlace agregado en `documentacion/README.md`.
 - Documentado `scripts/inspect_excel.py` en `documentacion/analisis/21_inspect_excel.md`.
 - Limpieza de binarios: movidos a `utilidades/binarios/` y `.gitignore` ampliado (EXCEL/, pdfs_patologia/, huv_oncologia.db, *.exe).
 - Ejecutable probado con PyInstaller (`dist/OCR_Medico.exe`).

2025-09-15 – v2.5.0
- Rediseno de la aplicacion de escritorio con CustomTkinter: navegacion por Procesar PDFs, Visualizar Datos, Dashboard Analitico y Automatizar BD Web.
- Canalizacion persistente: `procesador_ihq_biomarcadores` segmenta multiples informes por PDF, normaliza biomarcadores y guarda resultados en `huv_oncologia.db` mediante `database_manager`.
- Dashboard analitico integrado (Matplotlib/Seaborn) con filtros dinamicos, comparador parametrizado y modo pantalla completa.
- Automatizacion del portal `huvpatologia.qhorte.com` con Selenium (`huv_web_automation.py`) para consultas guiadas desde la aplicacion.
- Widget `CalendarioInteligente` (Babel + holidays) para seleccionar rangos de fecha con contexto de festivos.
- Documentacion actualizada para arquitectura 2.5 e incorporacion de analisis de `database_manager`, `huv_web_automation` y `calendario.py`.

2025-09-10 – v1.1.0
- Version estable v1.1 liberada.
- Nuevo analisis avanzado de IHQ accesible desde la UI (boton "Analizar Biomarcadores IHQ (v1.1)") que genera un Excel separado con HER2, Ki-67, RE/ER, RP/PR, PD-L1, P16 (estado/porcentaje) y "Estudios Solicitados".
- Documentacion actualizada: `INFORME_GLOBAL_PROYECTO.md`, `README.md`, `INICIO_RAPIDO.md` y bitacora.

2025-09-10
- Rebranding y reestructuracion documental al ecosistema "EVARISIS Gestor H.U.V".
- Creacion de `BITACORA_DE_ACERCAMIENTOS.md` y carpeta `comunicados/` (cinco artefactos).
- Ajustes de analisis: documentacion de extensiones IHQ y activos de datos.

2025-09-05 – v1.0.0
- Fundacion y validacion: motor OCR + app de escritorio.
- Procesadores especializados: Autopsia, IHQ, Biopsia, Revision.
- Exportacion validada a Excel (55 columnas) con formato profesional.

2025-08-20 – v0.1.0
- Inicio del desarrollo: estructura base, OCR y primeras reglas de extraccion.
