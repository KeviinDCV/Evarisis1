# EVARISIS Gestor H.U.V — README

**EVARISIS Gestor H.U.V** es un módulo especializado del ecosistema EVARISIS que transforma informes PDF de patología oncológica del Hospital Universitario del Valle en datos estructurados para análisis clínico, investigación y gestión institucional. Automatiza la extracción de información mediante OCR híbrido y proporciona una interfaz moderna con dashboard analítico integrado para la toma de decisiones basada en evidencia.

## Rol en el ecosistema EVARISIS

```
EVARISIS Dashboard
    │
    ├── CLI invocación
    │   └── python huv_ocr_sistema_definitivo.py [argumentos]
    │
    └── EVARISIS Gestor H.U.V
        ├── Entrada: PDFs patología (IHQ, Biopsia, Autopsia)
        ├── Procesamiento: OCR + Extracción + Normalización  
        ├── Persistencia: SQLite (huv_oncologia.db)
        └── Salida: Dashboard + Exportaciones + Automatización web
```

**Entradas de alto nivel**: PDFs de informes patológicos, credenciales portal web, configuración OCR  
**Salidas de alto nivel**: Base de datos estructurada, visualizaciones analíticas, reportes Excel, consultas automatizadas

## Stack tecnológico

**Lenguaje principal**: Python 3.9+  
**Framework UI**: TTKBootstrap v3.5 (migración completa desde CustomTkinter v2.5.0)  
**Navegación**: Sistema floating menu dinámico con animaciones y 18 temas intercambiables  
**Procesamiento**: PyMuPDF (PDFs), Pytesseract (OCR), Pandas (datos)  
**Visualización**: Matplotlib, Seaborn  
**Automatización**: Selenium WebDriver  
**Persistencia**: SQLite3

### Dependencias principales

| Nombre | Propósito | Dónde se usa |
|--------|-----------|--------------|
| `pytesseract` | OCR de documentos escaneados | `ocr_processing.py` |
| `PyMuPDF` | Extracción de texto nativo PDF | `ocr_processing.pdf_to_text_enhanced()` |
| `ttkbootstrap` | Framework UI moderno con temas bootstrap | `ui.py:App(ttk.Window)` |
| `pandas` | Manipulación y análisis de datos | `database_manager.py`, `ui.py` |
| `selenium` | Automatización portal web | `huv_web_automation.py` |
| `matplotlib` | Visualizaciones dashboard | `ui.py:create_dashboard_tab()` |
| `sqlite3` | Base de datos local | `database_manager.py` |

## Ejecución y argumentos

**Lanzado por**: EVARISIS Dashboard via CLI  
**Comando**: `python huv_ocr_sistema_definitivo.py`

### Argumentos CLI

| Argumento | Tipo | Requerido | Descripción | Evidencia |
|-----------|------|-----------|-------------|-----------|
| `--config` | str | No | Ruta alternativa config.ini | `huv_ocr_sistema_definitivo.py:configure_tesseract()` |
| `--debug` | bool | No | Modo debug con logging extendido | Inferido de sistema logging |

*Nota: El módulo actualmente funciona principalmente como aplicación standalone. Argumentos CLI adicionales pueden estar implementados en versiones futuras para integración completa con EVARISIS Dashboard.*

## Estructura del módulo

```
EVARISIS_Gestor_HUV/
├── documentacion/           # Documentación técnica y análisis
│   ├── analisis/           # Análisis detallado por componente
│   └── comunicados/        # Materiales para audiencias externas
├── LEGACY/                 # Versiones anteriores y código heredado
├── utilidades/            # Scripts auxiliares y herramientas
├── scripts/               # Scripts de mantenimiento y utilidades
├── EXCEL/                 # Archivos de salida y depuración OCR
├── pdfs_patologia/        # PDFs fuente para procesamiento
├── PROYECTO VISUAL/       # Recursos visuales y mockups
├── GPT/                   # Sistema de prompts para documentación
├── venv0/                 # Entorno virtual Python (excluido)
├── huv_ocr_sistema_definitivo.py  # Punto de entrada principal
├── ui.py                  # Interfaz TTKBootstrap con navegación floating
├── database_manager.py    # Gestor base de datos SQLite
├── ocr_processing.py      # Motor OCR híbrido
├── procesador_ihq_biomarcadores.py  # Extracción especializada IHQ
├── huv_web_automation.py  # Automatización portal web
├── calendario.py          # Widget calendario inteligente
└── config.ini            # Configuración OCR y rutas
```

**Exclusiones**: `venv0/`, `__pycache__/`, `*.db`, `*.exe`, archivos temporales OCR

## Puntos de entrada y flujo principal

**Entrada principal**: `huv_ocr_sistema_definitivo.py:main()`

### Flujo resumido
1. **Configuración inicial**: Lee `config.ini`, configura Tesseract OCR
2. **Lanzamiento UI**: Inicializa `ui.App(info_usuario, tema)` con TTKBootstrap Window y 18 temas intercambiables
3. **Navegación floating**: Menú deslizable `_create_floating_menu()` en posición `(15, 150)` con animaciones hover y transiciones fluidas entre 5 módulos principales
4. **Procesamiento**: Usuario selecciona PDFs → OCR híbrido → Extracción especializada → Persistencia SQLite
5. **Visualización**: Dashboard analítico con filtros dinámicos y KPIs
6. **Automatización**: Bot Selenium para portal institucional (`huvpatologia.qhorte.com`)

## Integraciones

| Sistema | Propósito | Configuración |
|---------|-----------|---------------|
| Portal HUV Patología | Automatización consultas y descargas | `huv_web_automation.py` + credenciales usuario |
| Tesseract OCR | Extracción texto de imágenes | `config.ini:[PATHS]` |
| SQLite Local | Persistencia datos estructurados | `database_manager.py:DB_FILE` |
| Selenium ChromeDriver | Control navegador web | Descarga automática vía `webdriver-manager` |

## Buenas prácticas y convenciones

**Versionamiento**: Semantic Versioning (SemVer)  
**Ramas**: `main` (producción), `develop` (desarrollo)  
**Logging**: Sistema integrado con timestamps en UI y archivos debug OCR  
**Manejo errores**: Try-catch con logging detallado, UI no-bloqueante con threading  
**Trazabilidad**: Control duplicados por número de petición, logs de procesamiento por lote

### Convenciones código
- Encoding UTF-8 explícito en todos los archivos Python
- Documentación en español para dominio médico
- Prefijo `IHQ######` para identificadores de informes
- Nomenclatura archivos: `snake_case` para Python, `PascalCase` para clases

## Mantenimiento

### Actualizar dependencias
```bash
pip install -r requirements.txt --upgrade
```

### Empaquetado ejecutable
```bash
python crear_ejecutable.py  # Genera OCR_Medico.exe con PyInstaller
```

### Compatibilidad SO
- **Windows**: Soporte completo (desarrollo principal)
- **Linux**: Compatible con ajuste rutas Tesseract en `config.ini`
- **macOS**: Compatible con Homebrew Tesseract

### Verificación instalación
```bash
tesseract --version  # Verificar OCR disponible
python -c "import pytesseract, fitz, pandas, ttkbootstrap, selenium"  # Verificar dependencias
```

## Migración Arquitectónica v3.5 

### ⚡ BREAKING CHANGES: CustomTkinter → TTKBootstrap
**Versión 3.5 introduce una migración completa del framework de interfaz**

| Aspecto | LEGACY v2.5.0 | ACTUAL v3.5 | Impacto |
|---------|----------------|--------------|---------|
| **Framework** | `import customtkinter as ctk` | `import ttkbootstrap as ttk` | Migración completa UI |
| **Herencia principal** | `class App(ctk.CTk)` | `class App(ttk.Window)` | Nueva arquitectura bootstrap |
| **Navegación** | 5 tabs estáticos `ttk.Notebook` | Sistema floating dinámico | UX revolucionaria |
| **Temas** | Fijo `dark-blue` | 18 temas intercambiables | Personalización avanzada |
| **Tamaño ui.py** | 59,043 bytes (1,299 líneas) | 136,021 bytes (3,121 líneas) | +130% crecimiento |

### 🚀 Nuevas Capacidades v3.5
- **Profile Integration**: Parámetro `info_usuario` con foto, nombre y cargo personalizable
- **Theme Switching**: Runtime switching entre 18 themes TTKBootstrap ('superhero', 'flatly', 'cyborg', etc.)
- **Advanced Navigation**: `_create_floating_menu()` con animaciones y efectos hover avanzados
- **Medical Vocabulary**: Nuevas `MALIGNIDAD_KEYWORDS_IHQ` con 50+ términos oncológicos especializados
- **Enhanced IHQ Processing**: Algoritmos mejorados (+40% código) para detección órganos y biomarcadores

### 📂 Archivos Modificados
- `ui.py`: **+130%** (59KB → 136KB) - Migración completa arquitectura UI
- `procesador_ihq.py`: **+40%** (23KB → 32KB) - Funcionalidades expandidas
- `huv_constants.py`: **+32%** (5KB → 7KB) - Vocabulario médico ampliado
- **ELIMINADO**: `test_sistema.py` - Suite testing refactorizada
- **NUEVOS**: `.vscode/`, `build/`, `dist/`, control de versiones Git

---

## Características principales de la interfaz

### Sistema de Navegación Floating (v3.5+)
- **Menú flotante animado**: Acceso rápido a todos los módulos principales mediante botón floating persistente
- **Transiciones fluidas**: Animaciones suaves para aparición/desaparición de elementos de navegación
- **Navegación intuitiva**: Métodos especializados `_nav_to_*` para transiciones seamless entre paneles
- **Responsive design**: Interface adaptable con scrollable frames optimizados para contenido extenso

### Arquitectura UI Moderna
- **Framework TTKBootstrap**: Interface moderna con temas bootstrap profesionales
- **Modularidad**: Separación clara de responsabilidades con métodos `_create_*` para cada componente
- **Feedback visual**: Indicadores de estado en tiempo real y logging integrado en UI
- **Experiencia usuario**: Design centrado en usabilidad médica con terminología especializada

### Funcionalidades Principales
- **Procesamiento OCR híbrido**: Extracción inteligente texto nativo + OCR en documentos mixtos
- **Dashboard analítico**: Visualizaciones interactivas con filtros dinámicos y KPIs especializados
- **Automatización web**: Bot Selenium para portal institucional con recuperación de errores
- **Gestión base datos**: Interface completa CRUD con validación y control duplicados

## Créditos y contacto técnico

**Equipo responsable**:
- **Dr. Juan Camilo Bayona** - Líder médico e investigador principal (Oncología HUV)
- **Ing. Daniel Restrepo** - Desarrollador principal (Área de Innovación y Desarrollo, GDI)
- **Ing. Diego Peña** - Jefe de Gestión de la Información (HUV)

**Organización**: Hospital Universitario del Valle "Evaristo García" (HUV)  
**Área ejecutora**: Área de Innovación y Desarrollo - Gestión de la Información (GDI)  
**Contacto técnico**: Área GDI HUV

**Repositorio**: Control de versiones interno HUV  
**Documentación**: `DEBERES HUV\HUV_ONCOLOGIA\HUV_ONCOLOGIA\documentacion\`
- Calidad: campos faltantes, productividad por responsable, longitud del diagnostico.
- Comparador: agregaciones por dimension seleccionable (conteo o promedio).

Automatizacion del portal
- Utiliza Selenium y ChromeDriver gestionado por `webdriver-manager`.
- Opciones de criterio soportadas: Fecha de Ingreso, Fecha de Finalizacion, Rango de Peticion, Datos del Paciente.
- El log integrado muestra el avance del bot y captura errores.

Gobernanza y autoria
- Lider clinico: Dr. Juan Camilo Bayona (Oncologia).
- Desarrollador principal: Ing. Daniel Restrepo (Area de Innovacion y Desarrollo, GDI).
- Jefe de Gestion de la Informacion: Ing. Diego Pena.
- Entidad ejecutora: Area de Innovacion y Desarrollo del HUV Evaristo Garcia.

Instalacion rapida
```cmd
pip install -r requirements.txt
python huv_ocr_sistema_definitivo.py
```
Para despliegues nuevos en Windows instale Tesseract y verifique que el ejecutable coincida con `config.ini`.

Requisitos
- Python 3.9+ (probado en 3.13).
- Tesseract OCR instalado (con idioma spa).
- Paquetes de `requirements.txt` (incluye customtkinter, matplotlib, selenium, webdriver-manager, Babel, holidays).
- Google Chrome para la automatizacion web.
- Acceso a los PDFs institucionales.

Verificacion rapida
```bash
tesseract --version
python -c 'import pytesseract, fitz, PIL, pandas, customtkinter, selenium'
```

Configuracion relevante (config.ini)
- [PATHS]: rutas especificas de Tesseract por sistema operativo.
- [OCR_SETTINGS]: DPI, PSM y banderas adicionales de Tesseract.
- [PROCESSING]: rango de paginas y ancho minimo para el render.
- [OUTPUT]: parametros historicos para nombres de Excel (opcional si se usa export manual).
- [INTERFACE]: dimensiones y altura del log (heredado del modo clasico).

Hoja de ruta
- Fase 1 – Fundacion (completa, v1.0).
- Fase 2 – Enriquecimiento IHQ (completa, v1.1).
- Fase 3 – Centralizacion y visualizacion (en curso, v2.5 entrega dashboard y SQLite).
- Fase 4 – Integracion SERVINTE (planeada: API o CSV y colas de reenvio).
- Fase 5 – Inteligencia aumentada (planeada: modelos predictivos y asistente).

Arquitectura y analisis
- Ver `documentacion/analisis/README.md` para el indice detallado.
- Modulos destacados: `ui.py`, `procesador_ihq_biomarcadores.py`, `database_manager.py`, `huv_web_automation.py`, `calendario.py`, `ocr_processing.py`, `huv_constants.py`.
 - Reporte para ChatGPT: `documentacion/REPORTE_CHATGPT.md` (mapa navegable del proyecto).

Soporte y problemas comunes
- 'Tesseract not found': revise `config.ini` o agregue el ejecutable al PATH.
- Selenium falla al iniciar: confirme la version de Chrome y que la red permita descargar el driver.
- OCR deficiente: incremente DPI, verifique calidad del PDF y revise MIN_WIDTH.
- Datos duplicados: verifique que el PDF no reutilice el mismo numero de peticion; la base ignora duplicados exactos.

Historial
- Cambios: `documentacion/CHANGELOG.md`.
- Bitacora de acercamientos: `documentacion/BITACORA_DE_ACERCAMIENTOS.md`.
