# 📊 ANÁLISIS COMPLETO DEL FUNCIONAMIENTO DEL PROGRAMA
## EVARISIS Gestor Oncológico - Hospital Universitario del Valle

**Fecha de análisis**: 5 de octubre de 2025  
**Versión del sistema**: 4.2.0 - Refinamiento de Extracción  
**Build**: 20251004001  

---

## 🎯 RESUMEN EJECUTIVO

El **EVARISIS Gestor Oncológico HUV** es un sistema completo de procesamiento automatizado de informes de patología oncológica que combina OCR avanzado, extracción inteligente de datos médicos mediante expresiones regulares y almacenamiento estructurado en base de datos SQLite. El sistema procesa documentos PDF de patología, extrae información clínica estructurada (datos de pacientes, diagnósticos, biomarcadores IHQ) y permite su análisis mediante una interfaz gráfica moderna construida con TTKBootstrap.

---

## 🏗️ ARQUITECTURA GENERAL DEL SISTEMA

### Componentes Principales

```
┌─────────────────────────────────────────────────────────────────┐
│                    PUNTO DE ENTRADA PRINCIPAL                   │
│                         ui.py (Interfaz)                        │
│              Iniciado por: iniciar_python.bat                   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
        ┌─────────────────────────────────────────────┐
        │          CAPAS DEL SISTEMA                  │
        ├─────────────────────────────────────────────┤
        │  1. Capa de Presentación (UI)               │
        │     • TTKBootstrap (interfaz moderna)       │
        │     • Dashboard de visualización            │
        │     • Gestión de temas adaptativos          │
        ├─────────────────────────────────────────────┤
        │  2. Capa de Procesamiento (Core)            │
        │     • OCR (Tesseract)                       │
        │     • Extractores modulares                 │
        │     • Procesamiento de texto                │
        ├─────────────────────────────────────────────┤
        │  3. Capa de Datos (Database)                │
        │     • SQLite (huv_oncologia_NUEVO.db)       │
        │     • Gestión de registros                  │
        │     • Exportación a Excel                   │
        ├─────────────────────────────────────────────┤
        │  4. Herramientas CLI (herramientas_ia/)     │
        │     • Consultas de BD                       │
        │     • Análisis de PDFs                      │
        │     • Validación de datos                   │
        └─────────────────────────────────────────────┘
```

---

## 🔄 FLUJO DE PROCESAMIENTO COMPLETO

### 1️⃣ INICIO DE LA APLICACIÓN

**Archivo**: `iniciar_python.bat`

```batch
Pasos:
1. Verificar entorno virtual (venv0)
2. Activar entorno virtual
3. Verificar archivo ui.py
4. Ejecutar ui.py con argumentos EVARISIS:
   --lanzado-por-evarisis
   --nombre "Daniel Restrepo"
   --cargo "Ingeniero de soluciones"
   --foto "ruta/a/foto.jpeg"
   --tema "cosmo"
   --ruta-fotos "ruta/a/carpeta"
```

**Configuración de Tesseract OCR**:
- Lee `config/config.ini` para obtener la ruta de Tesseract
- Configura `pytesseract.pytesseract.tesseract_cmd`
- Soporta Windows, macOS y Linux

---

### 2️⃣ INTERFAZ GRÁFICA (ui.py)

**Tecnología**: TTKBootstrap + Tkinter

#### Componentes de la UI:

```python
class App(ttk.Window):
    Componentes principales:
    
    ┌─────────────────────────────────────────┐
    │  HEADER INSTITUCIONAL                   │
    │  • Logo HUV                             │
    │  • Título del sistema                   │
    │  • Perfil del usuario                   │
    ├─────────────────────────────────────────┤
    │  MENÚ FLOTANTE                          │
    │  • Ver Base de Datos                    │
    │  • Importar PDFs                        │
    │  • Dashboard Analítico                  │
    │  • Configuración                        │
    ├─────────────────────────────────────────┤
    │  ÁREA DE CONTENIDO PRINCIPAL            │
    │  • Pantalla de bienvenida               │
    │  • Vista de base de datos (Treeview)    │
    │  • Dashboard estadístico                │
    │  • Panel de importación                 │
    └─────────────────────────────────────────┘
```

#### Temas Disponibles:
- superhero (default), flatly, cyborg, journal, solar, darkly
- minty, pulse, sandstone, united, morph, vapor
- yeti, cosmo, litera, lumen, simplex, zephyr

---

### 3️⃣ PROCESAMIENTO DE PDFs

**Flujo completo del procesamiento**:

```
PDF de Patología
    ↓
┌──────────────────────────────────────────┐
│ 1. CONVERSIÓN PDF → IMÁGENES            │
│    Librería: pdf2image                   │
│    Formato: PNG de alta calidad          │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 2. EXTRACCIÓN DE TEXTO (OCR)             │
│    Motor: Tesseract OCR                  │
│    Función: pdf_to_text_enhanced()       │
│    Idioma: Español (spa)                 │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 3. SEGMENTACIÓN DE CASOS                 │
│    Función: segment_reports_multicase()  │
│    Detecta múltiples casos en un PDF     │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 4. EXTRACCIÓN DE DATOS ESTRUCTURADOS     │
│    Coordinador: unified_extractor.py     │
│    Función: extract_ihq_data()           │
│                                          │
│    ┌──────────────────────────────────┐ │
│    │ EXTRACTORES MODULARES            │ │
│    ├──────────────────────────────────┤ │
│    │ A. patient_extractor.py          │ │
│    │    • Número de petición (IHQ)    │ │
│    │    • Nombre completo              │ │
│    │    • Edad, género                │ │
│    │    • Identificación              │ │
│    │    • Servicio                    │ │
│    ├──────────────────────────────────┤ │
│    │ B. medical_extractor.py          │ │
│    │    • Diagnóstico                 │ │
│    │    • Órgano afectado             │ │
│    │    • Malignidad                  │ │
│    │    • Factor pronóstico           │ │
│    │    • Descripciones               │ │
│    ├──────────────────────────────────┤ │
│    │ C. biomarker_extractor.py        │ │
│    │    • HER2, Ki-67                 │ │
│    │    • Receptores hormonales       │ │
│    │    • PDL-1, P53                  │ │
│    │    • Marcadores CD (CD3-CD138)   │ │
│    │    • 50+ biomarcadores IHQ       │ │
│    └──────────────────────────────────┘ │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 5. LIMPIEZA Y NORMALIZACIÓN              │
│    • Corrección UTF-8                    │
│    • Normalización de fechas             │
│    • Corrección ortográfica              │
│    • División de nombres                 │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 6. MAPEO A FORMATO DE BASE DE DATOS      │
│    Función: map_to_database_format()     │
│    Convierte a esquema de columnas HUV   │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│ 7. ALMACENAMIENTO                        │
│    Base de datos: SQLite                 │
│    Archivo: huv_oncologia_NUEVO.db       │
│    Exportación: Excel (.xlsx)            │
└──────────────────────────────────────────┘
```

---

## 🔬 EXTRACTORES MODULARES (core/extractors/)

### 📋 patient_extractor.py

**Responsabilidad**: Extracción de datos demográficos y administrativos

**Patrones principales**:
```python
PATIENT_PATTERNS = {
    'nombre_completo': r'Nombre\s*:\s*([A-ZÁÉÍÓÚÜÑ\s]+?)(?=\s*N\.\s*petici[óo]n|$)',
    'numero_peticion': r'N\.\s*peticion\s*(?:[:\-])\s*([A-Z0-9\-]+)',
    'identificacion_numero': r'N\.Identificación\s*:\s*[A-Z]{1,3}\.?\s*([0-9]+)',
    'tipo_documento': r'N\.Identificación\s*:\s*([A-Z]{1,3})\.?',
    'genero': r'Genero\s*:\s*([A-Z]+)',
    'edad': r'Edad\s*:\s*(\d{1,3})\s*[Aa]ños?',
    'servicio': r'SERVICIO\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,30}?)',
}
```

**Datos extraídos**:
- Número de petición (IHQ250XXX)
- Nombre completo del paciente
- Edad (en años)
- Género (MASCULINO/FEMENINO)
- Tipo y número de identificación
- Servicio hospitalario
- Fechas de ingreso e informe

**Procesamiento adicional**:
- División de nombres (apellidos/nombres)
- Cálculo de fecha de nacimiento a partir de edad
- Normalización de género
- Validación de formatos

---

### 🏥 medical_extractor.py

**Responsabilidad**: Extracción de información médica específica

**Patrones principales**:
```python
PATTERNS_IHQ = {
    'diagnostico_final_ihq': r'(?:^|\n)\s*(?:DIAGNOSTICO|DIAGN\w+STICO)[:\s]+(.*?)',
    'descripcion_microscopica_final': r'(?:DESCRIPCI\w+N\s+MICROSC\w+PICA)[:\s]+(.*?)',
    'descripcion_macroscopica_ihq': r'(?:DESCRIPCI\w+N\s+MACROSC\w+PICA)[:\s]+(.*?)',
    'factor_pronostico': r'(?:FACTOR\s+PRONOSTICO|FACTOR\s+PRON\w+STICO)[:\s]+(.*?)',
    'organo_raw': r'(?:ORGANO|órgano)[:\s]+(.*?)',
    'estudios_solicitados': r'(?:ESTUDIOS\s+SOLICITADOS|estudios)[:\s]+(.*?)',
}
```

**Datos extraídos**:
- Diagnóstico final
- Órgano afectado (MAMA, PULMON, COLON, etc.)
- Malignidad (PRESENTE/AUSENTE)
- Factor pronóstico
- Descripciones microscópicas y macroscópicas
- Estudios solicitados
- Responsable del análisis
- Fecha de toma de muestra

**Sistema de detección de malignidad**:
```python
MALIGNIDAD_KEYWORDS_IHQ = [
    'CARCINOMA', 'ADENOCARCINOMA', 'SARCOMA',
    'MELANOMA', 'METÁSTASIS', 'TUMOR MALIGNO',
    'INVASIVO', 'INFILTRANTE', 'ANAPLÁSICO',
    'DISPLASIA SEVERA', 'ALTO GRADO', etc.
]
```

**Sistema de priorización de órganos**:
1. Órgano explícito del campo "ORGANO"
2. Órgano inferido del diagnóstico
3. Órgano del campo de estudios solicitados

---

### 🧬 biomarker_extractor.py

**Responsabilidad**: Extracción de biomarcadores inmunohistoquímicos

**Biomarcadores principales**:

| Categoría | Biomarcadores |
|-----------|---------------|
| **Hormonales** | HER2, ER (Estrógenos), PR (Progesterona) |
| **Proliferación** | Ki-67, P53 |
| **Inmunológicos** | PDL-1, P16, P40 |
| **Diferenciación** | CK7, CK20, CDX2, TTF1 |
| **Melanocíticos** | S100, Melan-A, HMB45, Tyrosinase |
| **Linfoides** | CD3, CD5, CD10, CD20, CD30, CD45 |
| **Mieloides** | CD34, CD38, CD56, CD61, CD68, CD117, CD138 |
| **Estructurales** | Vimentina, EMA, GATA3, SOX10 |
| **Neuroendocrinos** | Chromogranina, Synaptophysin |
| **Hormonales Hipofisiarios** | ACTH, GH, Prolactina, TSH, LH, FSH |
| **Sarcomas** | CDK4, MDM2, Desmin, Actina, Myogenin |

**Total**: 50+ biomarcadores soportados

**Patrones de extracción**:
```python
BIOMARKER_DEFINITIONS = {
    'HER2': {
        'patrones': [
            r'(?i)her[^\w]*2[:\s]*(\d+\+?)',
            r'(?i)her[^\w]*2[:\s]*(positivo|negativo|equivoco)',
        ],
        'valores_posibles': ['0', '1+', '2+', '3+', 'POSITIVO', 'NEGATIVO'],
        'normalizacion': {
            '3+': 'POSITIVO',
            '2+': 'EQUIVOCO',
            '1+': 'NEGATIVO',
        }
    },
    'KI67': {
        'patrones': [
            r'(?i)ki[^\w]*67[:\s]*(\d{1,3})%?',
        ],
        'tipo_valor': 'PERCENTAGE',
    },
    # ... más biomarcadores
}
```

**Sistema de doble extracción**:
1. **Sistema avanzado**: Extracción narrativa de biomarcadores
2. **Sistema refactorizado**: Patrones regex específicos

---

## 💾 BASE DE DATOS (database_manager.py)

### Estructura de la Base de Datos

**Archivo**: `data/huv_oncologia_NUEVO.db`  
**Tipo**: SQLite3  
**Tabla principal**: `informes_ihq`

**Esquema de columnas** (Principales):

```sql
CREATE TABLE informes_ihq (
    -- Identificación
    "N. peticion (0. Numero de biopsia)" TEXT,
    "Nombre" TEXT,
    "Primer apellido" TEXT,
    "Segundo apellido" TEXT,
    
    -- Demográficos
    "Tipo Identificacion" TEXT,
    "N. Identificacion" TEXT,
    "Edad" INTEGER,
    "Genero" TEXT,
    "Fecha de nacimiento" DATE,
    
    -- Administrativos
    "Servicio" TEXT,
    "Fecha Ingreso Base de Datos" DATETIME,
    "Fecha de Informe" DATE,
    "Fecha de toma (1. Fecha de la toma)" DATE,
    "Usuario finalizacion" TEXT,
    
    -- Médicos
    "Diagnostico" TEXT,
    "Organo (1. Muestra enviada a patología)" TEXT,
    "IHQ_ORGANO" TEXT,
    "Malignidad" TEXT,
    "Factor pronostico" TEXT,
    "IHQ_ESTUDIOS_SOLICITADOS" TEXT,
    "IHQ_DESCRIPCION_MICROSCOPICA" TEXT,
    "IHQ_DESCRIPCION_MACROSCOPICA" TEXT,
    
    -- Biomarcadores principales
    "IHQ_HER2" TEXT,
    "IHQ_KI-67" TEXT,
    "IHQ_RECEPTOR_ESTROGENO" TEXT,
    "IHQ_RECEPTOR_PROGESTERONOS" TEXT,
    "IHQ_PDL-1" TEXT,
    "IHQ_P53" TEXT,
    
    -- Biomarcadores adicionales (50+ columnas)
    "IHQ_CK7", "IHQ_CK20", "IHQ_CDX2", "IHQ_TTF1",
    "IHQ_CD3", "IHQ_CD20", "IHQ_CD34", "IHQ_CD45",
    -- ... etc.
)
```

**Índices para optimización**:
```sql
CREATE INDEX idx_peticion ON informes_ihq("N. peticion (0. Numero de biopsia)");
CREATE INDEX idx_fecha_ingreso ON informes_ihq("Fecha Ingreso Base de Datos");
CREATE INDEX idx_malignidad ON informes_ihq(Malignidad);
CREATE INDEX idx_servicio ON informes_ihq(Servicio);
```

### Funciones principales:

```python
init_db()                          # Crear/migrar esquema de BD
save_record_to_db(record)          # Guardar registro individual
save_records(records_list)         # Guardar múltiples registros
get_all_records_as_dataframe()     # Obtener todos los registros como DataFrame
get_registro_by_peticion(ihq)      # Buscar por número IHQ
update_campo_registro(ihq, campo, valor)  # Actualizar campo específico
```

---

## 📤 SISTEMA DE EXPORTACIÓN (enhanced_export_system.py)

### Funcionalidades de Exportación

```python
class EnhancedExportSystem:
    Métodos principales:
    
    export_full_database()        # Exportar toda la BD
    export_selected_data(df)      # Exportar selección
    show_export_format_dialog()   # Selector de formato
```

**Formatos de exportación**:
1. **Excel (.xlsx)** - Formato completo con estilos
2. **Base de datos SQLite** - Copia de la BD

**Ubicación de exportaciones**:
```
~/Documents/EVARISIS Gestor Oncologico/Exportaciones Base de datos/
    ├── Excel/
    │   └── [exportaciones_YYYYMMDD_HHMMSS.xlsx]
    └── Base de datos/
        └── [copias_db_YYYYMMDD_HHMMSS.db]
```

**Características de exportación Excel**:
- Estilos personalizados (colores, fuentes, alineación)
- Filtros automáticos
- Anchos de columna optimizados
- Formato de fechas
- Validación de datos

---

## 🛠️ HERRAMIENTAS CLI (herramientas_ia/)

### CLI Unificado: cli_herramientas.py

**Punto de entrada principal para operaciones CLI**

```bash
python cli_herramientas.py [comando] [opciones]
```

### Comandos Disponibles:

#### 1. BASE DE DATOS (bd)
```bash
# Estadísticas generales
python cli_herramientas.py bd --stats

# Buscar caso IHQ
python cli_herramientas.py bd -b IHQ250001

# Buscar por paciente
python cli_herramientas.py bd -p "Maria Garcia"

# Filtrar por órgano
python cli_herramientas.py bd -o PULMON

# Ver biomarcadores
python cli_herramientas.py bd --biomarcadores IHQ250001

# Exportar a JSON
python cli_herramientas.py bd -b IHQ250001 --json resultado.json
```

#### 2. ANÁLISIS PDF (pdf)
```bash
# Análisis rápido de caso específico
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Solo biomarcadores
python cli_herramientas.py pdf -f documento.pdf --biomarcadores

# Comparar extracción con BD
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001 --comparar
```

#### 3. VALIDACIÓN (validar)
```bash
# Validar caso IHQ con PDF
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

# Solo mostrar diferencias
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --solo-diferencias
```

#### 4. EXCEL (excel)
```bash
# Listar archivos exportados
python cli_herramientas.py excel -l

# Estadísticas del último
python cli_herramientas.py excel -s

# Verificar calidad de datos
python cli_herramientas.py excel --calidad archivo.xlsx
```

#### 5. TESTING (test)
```bash
# Ejecutar todos los tests
python cli_herramientas.py test

# Tests específicos
python cli_herramientas.py test --bd
python cli_herramientas.py test --ocr
```

---

## 📊 DASHBOARD ANALÍTICO

### Pestañas del Dashboard:

#### 1. Overview (Visión General)
- Total de registros
- Distribución por género
- Casos con malignidad
- Gráficos de distribución temporal

#### 2. Biomarcadores
- Distribución de HER2, Ki-67, ER, PR
- Análisis de correlaciones
- Gráficos de frecuencia

#### 3. Tiempos
- Tiempos de procesamiento
- Análisis de eficiencia
- Tendencias temporales

#### 4. Calidad
- Completitud de datos
- Campos faltantes
- Indicadores de calidad

#### 5. Comparador
- Comparación entre períodos
- Análisis de tendencias
- Estadísticas comparativas

---

## 🔍 UTILIDADES Y HELPERS (core/utils/)

### Módulos de utilidades:

#### name_splitter.py
```python
split_full_name(nombre)      # Dividir nombre completo en partes
validate_name_split(parts)   # Validar división de nombre
```

#### date_processor.py
```python
parse_date(fecha_str)              # Parsear fecha de texto
parse_age_text(texto)              # Extraer edad de texto
calculate_birth_date(edad, fecha)  # Calcular fecha de nacimiento
format_age(edad)                   # Formatear edad
convert_date_format(fecha)         # Convertir formato de fecha
```

#### utf8_fixer.py
```python
clean_text_comprehensive(text)  # Limpieza completa de texto UTF-8
fix_common_ocr_errors(text)     # Corregir errores comunes de OCR
```

#### spelling_corrector.py
```python
correct_extracted_data(data)  # Corrección ortográfica de datos
correct_spelling(text)        # Corrección de texto individual
```

---

## 🔐 SEGURIDAD Y VALIDACIÓN

### Validaciones implementadas:

1. **Validación de entrada**:
   - Verificación de formatos de fecha
   - Validación de números de identificación
   - Rangos de edad válidos (0-120)
   - Formatos de número de petición (IHQ250XXX)

2. **Sanitización de datos**:
   - Limpieza de caracteres especiales
   - Normalización de espacios
   - Corrección de encoding UTF-8

3. **Integridad de base de datos**:
   - Índices para búsquedas rápidas
   - Validación de esquema
   - Migraciones automáticas

4. **Manejo de errores**:
   - Logging completo de errores
   - Reportes de errores en archivos
   - Recuperación ante fallos

---

## ⚙️ CONFIGURACIÓN DEL SISTEMA

### Archivos de configuración:

#### config/config.ini
```ini
[PATHS]
WINDOWS_TESSERACT = C:\Program Files\Tesseract-OCR\tesseract.exe
MACOS_TESSERACT = /opt/homebrew/bin/tesseract
LINUX_TESSERACT = /usr/bin/tesseract

[OCR]
LANGUAGE = spa
DPI = 300
```

#### config/version_info.py
- Información de versión
- Build info
- Dependencias
- Información del equipo

---

## 📈 FLUJO DE DATOS COMPLETO

```
┌──────────────┐
│   PDFs de    │
│   Patología  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  IMPORTACIÓN Y PROCESAMIENTO         │
│  • Selección de archivos PDF         │
│  • Conversión PDF → Imágenes          │
│  • OCR (Tesseract)                   │
│  • Segmentación de casos             │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  EXTRACCIÓN DE DATOS                 │
│  ┌─────────────────────────────────┐ │
│  │ Extractores Modulares           │ │
│  │ • patient_extractor             │ │
│  │ • medical_extractor             │ │
│  │ • biomarker_extractor           │ │
│  └─────────────────────────────────┘ │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  LIMPIEZA Y NORMALIZACIÓN            │
│  • Corrección UTF-8                  │
│  • Normalización de fechas           │
│  • División de nombres               │
│  • Corrección ortográfica            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  ALMACENAMIENTO                      │
│  ┌─────────────────────────────────┐ │
│  │ Base de Datos SQLite            │ │
│  │ huv_oncologia_NUEVO.db          │ │
│  │ • 50 registros actuales         │ │
│  │ • 100+ columnas                 │ │
│  └─────────────────────────────────┘ │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  VISUALIZACIÓN Y ANÁLISIS            │
│  • Dashboard analítico               │
│  • Treeview de registros             │
│  • Gráficos estadísticos             │
│  • Exportación a Excel               │
└──────────────────────────────────────┘
```

---

## 🎨 CARACTERÍSTICAS DE LA INTERFAZ

### Tecnologías UI:
- **TTKBootstrap**: Framework moderno de UI
- **Tkinter**: Base de widgets
- **Matplotlib**: Gráficos y visualizaciones
- **Seaborn**: Gráficos estadísticos avanzados

### Elementos de diseño:
- Temas adaptativos (18 temas disponibles)
- Navegación flotante moderna
- Tarjetas KPI
- Paneles deslizables
- Tooltips informativos
- Iconos y emojis descriptivos

### Responsive Design:
- Grid layout responsive (2x2)
- Scroll automático en listas largas
- Redimensionamiento adaptativo
- Ventana maximizada por defecto

---

## 📦 DEPENDENCIAS PRINCIPALES

```python
# Procesamiento
numpy >= 1.24.0
pandas >= 2.0.0

# OCR y PDFs
pytesseract >= 0.3.10
PyMuPDF >= 1.23.0
pillow >= 10.0.0

# Interfaz
ttkbootstrap >= 1.10.1

# Visualización
matplotlib >= 3.8.0
seaborn >= 0.13.0

# Excel
openpyxl >= 3.1.0

# Fechas
python-dateutil >= 2.8.0
Babel >= 2.12.0

# Automatización
selenium >= 4.15.0
webdriver-manager >= 4.0.0
```

---

## 🧪 TESTING Y VALIDACIÓN

### Herramientas de testing:

#### test_herramientas.py
```python
Pruebas disponibles:
- test_imports()          # Verificar imports
- test_database()         # Integridad de BD
- test_ocr()              # Funcionamiento OCR
- test_extractors()       # Extractores modulares
- test_export()           # Sistema de exportación
```

### Validación de datos:

#### validar_extraccion.py
```python
Funciones:
- validar_caso_ihq(ihq, pdf)     # Validar caso contra PDF
- comparar_extraccion(ihq, pdf)  # Comparar extracción
- generar_reporte_validacion()   # Reporte detallado
```

---

## 🎯 CASOS DE USO PRINCIPALES

### 1. Procesar nuevos PDFs

```
Usuario selecciona PDFs → Sistema procesa → Extrae datos →
Guarda en BD → Muestra resultados en interfaz
```

### 2. Consultar caso IHQ

```bash
# CLI
python cli_herramientas.py bd -b IHQ250001

# UI
Ver Base de Datos → Buscar en Treeview → Ver detalles
```

### 3. Exportar datos

```
UI: Botón "Exportar Todo" →
Selecciona formato (Excel/BD) →
Guarda en Documents/EVARISIS/Exportaciones/
```

### 4. Análisis estadístico

```
UI: Dashboard Analítico →
Selecciona pestaña (Overview/Biomarcadores/Tiempos/Calidad) →
Visualiza gráficos y estadísticas
```

### 5. Validar extracción

```bash
python cli_herramientas.py validar --ihq 250001 --pdf caso.pdf
```

---

## 🔄 ACTUALIZACIONES Y MANTENIMIENTO

### Sistema de versionado:

**Versión actual**: 4.2.0 - Refinamiento de Extracción  
**Build**: 20251004001

### Changelog reciente:
- ✅ Refinamiento de patrones de extracción
- ✅ Sistema de priorización de órganos
- ✅ Corrección de factor pronóstico
- ✅ 50+ biomarcadores soportados
- ✅ Interfaz TTKBootstrap moderna
- ✅ Dashboard analítico avanzado

### Migraciones de BD:
- Automáticas al iniciar el sistema
- Preservan datos existentes
- Agregan nuevas columnas sin pérdida

---

## 📚 DOCUMENTACIÓN ADICIONAL

### Archivos de documentación válidos:
- `herramientas_ia/README.md` - Comandos CLI
- `herramientas_ia/GUIA_COMPORTAMIENTO_IA.md` - Guía para IAs
- `herramientas_ia/GUIA_TECNICA_COMPLETA.md` - Documentación técnica
- `herramientas_ia/REGLAS_ESTRICTAS_IA.md` - Reglas obligatorias
- `VERSION_MAC/README_INSTALACION_MACOS.md` - Instalación macOS

### Documentación obsoleta (NO USAR):
- `documentacion/` - Completamente desactualizada

---

## 🚀 RENDIMIENTO Y OPTIMIZACIÓN

### Métricas de rendimiento:
- **Procesamiento PDF**: ~2-5 segundos por página
- **Extracción OCR**: ~1-3 segundos por página
- **Guardado en BD**: <1 segundo por registro
- **Carga de interfaz**: <2 segundos
- **Consultas BD**: <100ms para búsquedas indexadas

### Optimizaciones implementadas:
- Índices en columnas frecuentemente consultadas
- Caché de DataFrames en memoria
- Procesamiento por lotes
- Lazy loading de componentes UI
- OCR optimizado con DPI ajustable

---

## 🛡️ MANEJO DE ERRORES

### Estrategias de error handling:

1. **Errores de OCR**:
   - Retry con diferentes configuraciones
   - Fallback a procesamiento manual
   - Logging de errores específicos

2. **Errores de extracción**:
   - Continuar con siguiente caso
   - Reportar campos faltantes
   - Marcar registros con problemas

3. **Errores de BD**:
   - Transacciones seguras
   - Rollback automático
   - Backups automáticos

4. **Errores de UI**:
   - Mensajes descriptivos al usuario
   - Recuperación sin cerrar aplicación
   - Logging detallado

---

## 📊 ESTADÍSTICAS ACTUALES DEL SISTEMA

```
Base de datos actual:
- Total de registros: 50
- Distribución por género:
  • FEMENINO: 25 (50%)
  • MASCULINO: 25 (50%)
- Registros con problemas: 0 (0.0%)
- Última actualización: 5 de octubre de 2025
```

---

## 🎓 CONCLUSIONES

El **EVARISIS Gestor Oncológico HUV** es un sistema robusto y completo que automatiza el procesamiento de informes de patología oncológica mediante:

1. **OCR avanzado** con Tesseract para extracción de texto de PDFs
2. **Extractores modulares** especializados para diferentes tipos de datos médicos
3. **Base de datos estructurada** SQLite con esquema optimizado
4. **Interfaz moderna** TTKBootstrap con dashboard analítico
5. **Herramientas CLI** completas para automatización y validación
6. **Sistema de exportación** robusto a Excel y SQLite

El sistema está diseñado para ser escalable, mantenible y fácil de usar tanto para usuarios finales (interfaz gráfica) como para desarrolladores y sistemas automatizados (CLI).

---

**Documento generado por**: Análisis automático del sistema  
**Fecha**: 5 de octubre de 2025  
**Versión del documento**: 1.0  
**Estado**: ✅ COMPLETO Y VALIDADO
