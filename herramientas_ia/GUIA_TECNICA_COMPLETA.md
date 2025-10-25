# 🏥 GUÍA TÉCNICA COMPLETA - GESTOR ONCOLOGÍA HUV

## 📖 Descripción General
Este documento contiene toda la información técnica necesaria para entender, modificar y extender el sistema de Gestión Oncológica del Hospital Universitario del Valle (HUV). El sistema procesa PDFs de patología, extrae información médica mediante OCR y gestiona una base de datos SQLite con exportación a Excel.

---

## 🚀 INICIO RÁPIDO

### ⚡ Cómo iniciar el programa
```bash
# Windows
.\iniciar_python.bat

# macOS
cd VERSION_MAC/
./iniciar_python_mac.sh
```

### 📍 Punto de entrada principal
- **Archivo**: `ui.py` (archivo principal de la aplicación)
- **Framework**: TTKBootstrap (interfaz gráfica moderna)
- **Argumentos EVARISIS**: Se ejecuta con parámetros específicos para integración

---

## 📁 ESTRUCTURA DEL PROYECTO

### 🔧 Directorios principales
```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py                    # 🎯 ARCHIVO PRINCIPAL
├── iniciar_python.bat       # 🚀 Iniciador Windows
├── requirements.txt         # 📦 Dependencias Python
├── core/                    # 🧠 LÓGICA PRINCIPAL
├── config/                  # ⚙️ Configuración
├── data/                    # 💾 Base de datos
├── herramientas_ia/         # 🤖 Herramientas de IA (ESTA CARPETA)
├── VERSION_MAC/             # 🍎 Scripts para macOS
├── pdfs_patologia/          # 📄 PDFs a procesar
├── EXCEL/                   # 📊 Archivos de prueba
└── documentacion/           # 📚 Documentación técnica
```

---

## 🧠 MÓDULOS CORE PRINCIPALES

### 1. 📊 database_manager.py
**Ubicación**: `core/database_manager.py`
**Propósito**: Gestión completa de la base de datos SQLite

#### 🔑 Constantes importantes:
```python
# Configuración HUV (MOVIDO DESDE config/)
HUV_CONFIG = {
    'HOSPITAL_NAME': 'Hospital Universitario del Valle',
    'DEPARTMENT': 'Patología',
    # ... más configuraciones
}

# Códigos CUPS (MOVIDO DESDE config/)
CUPS_CODES = {
    'IHQ': '902210',
    'BIOPSIA': '879900',
    # ... más códigos
}
```

#### 🔧 Funciones principales:
- `init_db()`: Inicializa la base de datos
- `save_record_to_db()`: Guarda registros extraídos
- `get_all_records_as_dataframe()`: Obtiene todos los datos como DataFrame
- `get_connection()`: Conexión a la base de datos

### 2. 🔍 unified_extractor.py
**Ubicación**: `core/unified_extractor.py`
**Propósito**: Coordinador principal de extracción de datos

#### 📋 Flujo de procesamiento:
1. **Recibe PDF** → `process_pdf_file()`
2. **Convierte a imágenes** → `pdf2image`
3. **Aplica OCR** → `pytesseract`
4. **Extrae datos** → Extractores modulares
5. **Guarda en BD** → `database_manager`

### 3. 📤 enhanced_export_system.py
**Ubicación**: `core/enhanced_export_system.py`
**Propósito**: Sistema de exportación avanzado a Excel

#### 📂 Directorio de exportación:
```
Documents/EVARISIS Gestor Oncologico/Exportaciones Base de datos/
```

#### 📊 Tipos de exportación:
- **Exportación completa**: Todos los registros
- **Exportación filtrada**: Por fechas, servicios, etc.
- **Reportes estadísticos**: Resúmenes y gráficos

---

## 🎯 EXTRACTORES MODULARES

### 📁 Ubicación: `core/extractors/`

### 1. 👤 patient_extractor.py
**Datos extraídos**:
- Número de petición (IHQ250XXX)
- Nombre del paciente
- Edad y género
- Servicio solicitante

**Patrones importantes**:
```python
PATIENT_PATTERNS = {
    'numero_peticion': [
        r'(?:Petición|Peticion|Pet\.?|N°|Número|Numero).*?([A-Z]{2,4}\d{6,})',
        r'([A-Z]{2,4}\d{6,})',  # Patrón directo
    ],
    'edad': [
        r'(\d{1,3})\s*años?',
        r'Edad[:\s]*(\d{1,3})',
    ],
    # ... más patrones
}
```

### 2. 🧬 medical_extractor.py
**Datos extraídos**:
- Diagnósticos
- Biomarcadores IHQ
- Malignidad
- Procedimientos

**Constantes importantes**:
```python
MALIGNIDAD_KEYWORDS_IHQ = {
    'MALIGNO': [
        'carcinoma', 'adenocarcinoma', 'sarcoma',
        'metástasis', 'metastasis', 'maligno'
    ],
    'BENIGNO': [
        'benigno', 'hamartoma', 'adenoma',
        'fibroma', 'lipoma'
    ]
}
```

### 3. 🔬 biomarker_extractor.py
**Biomarcadores detectados**:
- HER2, Ki-67, RE (Receptor Estrógeno)
- RP (Receptor Progesterona), PDL-1
- P53, BRCA1/BRCA2

---

## 💾 BASE DE DATOS

### 📍 Ubicación
**Archivo**: `data/huv_oncologia_NUEVO.db`
**Tipo**: SQLite3
**Tabla principal**: `informes_ihq`

### 📊 Estructura de la tabla
```sql
CREATE TABLE informes_ihq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_peticion TEXT,
    nombre_paciente TEXT,
    edad INTEGER,
    genero TEXT,
    servicio TEXT,
    fecha_informe TEXT,
    diagnostico TEXT,
    malignidad TEXT,
    ihq_her2 TEXT,
    ihq_ki67 TEXT,
    ihq_receptor_estrogeno TEXT,
    ihq_receptor_progesteronos TEXT,
    ihq_pdl1 TEXT,
    -- ... más campos
    fecha_procesamiento TEXT,
    archivo_origen TEXT
);
```

### 🔍 Consultas frecuentes
Usa `herramientas_ia/consulta_base_datos.py` para:
- Estadísticas generales
- Búsqueda por petición
- Verificación de biomarcadores
- Consultas SQL personalizadas

---

## 📊 VISUALIZACIÓN DE DATOS

### 🎨 Modificar visualización en ui.py

#### ➕ Agregar nuevas columnas al grid:
**Ubicación**: `ui.py` - función `actualizar_tabla()`
```python
# Buscar la sección donde se definen las columnas
self.tree["columns"] = ("col1", "col2", "nueva_columna")
self.tree.heading("nueva_columna", text="Nueva Columna")
self.tree.column("nueva_columna", width=100)
```

#### 📈 Agregar nuevos gráficos:
**Ubicación**: `ui.py` - función `mostrar_panel_visualizacion()`
```python
# Agregar nuevo tipo de gráfico
def crear_grafico_personalizado(self, df):
    fig, ax = plt.subplots()
    # Tu código de gráfico aquí
    return fig
```

### 🎛️ Dashboard en tiempo real
**Archivo**: `core/enhanced_database_dashboard.py`
- Métricas en tiempo real
- Gráficos interactivos
- Filtros dinámicos

---

## 🔧 CONFIGURACIÓN Y MAPEOS

### ⚙️ Archivos de configuración
```
config/
├── config.ini              # Configuración general
├── version_info.py          # Información de versión
└── mapeos/                  # Mapeos y patrones
    ├── cups_oncologia.py    # Códigos CUPS
    ├── procedimientos.py    # Procedimientos médicos
    └── servicios_huv.py     # Servicios hospitalarios
```

### 🗺️ Modificar mapeos
**Para agregar nuevos códigos CUPS**:
1. Editar `core/database_manager.py` → `CUPS_CODES`
2. Agregar el mapeo correspondiente
3. Reiniciar la aplicación

**Para agregar nuevos servicios**:
1. Editar `config/mapeos/servicios_huv.py`
2. Agregar al diccionario `SERVICIOS_MAPPING`

---

## 📂 DIRECTORIOS IMPORTANTES

### 📄 PDFs de entrada
**Ubicación**: `pdfs_patologia/`
**Formato esperado**: Informes de patología en PDF
**Procesamiento**: Automático al seleccionar archivo

### 📊 Exportaciones Excel
**Directorio principal**:
```
Documents/EVARISIS Gestor Oncologico/Exportaciones Base de datos/
├── exports/                 # Exportaciones automáticas
├── reportes/               # Reportes estadísticos
└── backups/                # Respaldos de datos
```

### 🖼️ Imágenes y recursos
**Ubicación**: `imagenes/`
**Contiene**: Iconos, logos, recursos gráficos de la UI

### 🔬 Debug y desarrollo
**Ubicación**: `EXCEL/`
**Propósito**: Archivos de prueba y debug
**Contiene**: `DEBUG_OCR_OUTPUT_*.txt` con salidas de OCR

---

## 🛠️ HERRAMIENTAS DE DESARROLLO

### 🤖 Herramientas de IA (esta carpeta)
```
herramientas_ia/
├── consulta_base_datos.py           # 🔍 Consultor BD con CLI
├── verificar_exceles_exportados.py  # 📊 Verificador exportaciones
├── analizar_pdf_completo.py         # 📄 Analizador PDF con CLI avanzado
├── cli_herramientas.py              # 🔧 CLI unificado (wrapper)
├── utilidades_debug.py              # 🔧 Utilidades generales
├── test_herramientas.py             # 🧪 Suite de pruebas
└── GUIA_TECNICA_COMPLETA.md         # 📖 Este documento
```

### 💻 **USO POR CLI (RECOMENDADO)**

#### 🔍 **consulta_base_datos.py** - Opciones CLI:
```bash
# 📊 Ver estadísticas generales de la BD
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --estadisticas

# 🔍 Buscar caso específico por número de petición
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --buscar-peticion IHQ250001

# 📋 Ver ayuda completa
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --help

# ❌ NO usar modo interactivo para automatización
# python herramientas_ia/consulta_base_datos.py  # Solo para uso manual
```

#### 📄 **analizar_pdf_completo.py** - Opciones CLI avanzadas:
```bash
# ⚡ ANÁLISIS RÁPIDO - Solo caso específico (RECOMENDADO)
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --ihq 250001

# 🧬 Verificar solo biomarcadores
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --biomarcadores

# 👤 Verificar solo datos del paciente
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --paciente

# 📊 Análisis completo con comparación BD
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --ihq 250001 --comparar-bd

# 🔍 Buscar patrón específico (regex)
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --patron "IHQ.*250001"

# 🔍 Auditar rango de casos (análisis masivo)
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --auditar-rango 1 50

# 📋 Ver todas las opciones disponibles
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --help
```

#### 📊 **Verificar exportaciones:**
```bash
# Verificar exportaciones Excel (modo interactivo)
.\venv0\Scripts\python.exe herramientas_ia\verificar_exceles_exportados.py
```

#### 🧪 **Suite de pruebas:**
```bash
# Ejecutar todas las pruebas del sistema
.\venv0\Scripts\python.exe herramientas_ia\test_herramientas.py
```

### � **FLUJOS DE TRABAJO TÍPICOS CON CLI**

#### 1️⃣ **Diagnóstico rápido de un caso:**
```bash
# Paso 1: Analizar PDF específico
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\caso.pdf" --ihq 250001 --biomarcadores

# Paso 2: Verificar qué se guardó en BD
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --buscar-peticion IHQ250001

# Paso 3: Comparar automáticamente
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\caso.pdf" --ihq 250001 --comparar-bd
```

#### 2️⃣ **Auditoría masiva de casos:**
```bash
# Auditar casos del 1 al 50
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --auditar-rango 1 50

# Ver estadísticas generales después de auditoría
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --estadisticas
```

#### 3️⃣ **Búsqueda de patrones específicos:**
```bash
# Buscar patrón en PDF específico
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --patron "CARCINOMA.*METASTÁSICO"

# Analizar biomarcadores específicos
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --ihq 250001 --biomarcadores
```

---

## 🔄 FLUJO DE DATOS COMPLETO

### 📋 Proceso paso a paso:
1. **📄 Usuario selecciona PDF** → `ui.py`
2. **🔍 Conversión a imágenes** → `pdf2image`
3. **👁️ OCR con Tesseract** → `pytesseract`
4. **🧠 Extracción coordinada** → `unified_extractor.py`
5. **👤 Datos del paciente** → `patient_extractor.py`
6. **🧬 Datos médicos** → `medical_extractor.py`
7. **🔬 Biomarcadores** → `biomarker_extractor.py`
8. **💾 Guardado en BD** → `database_manager.py`
9. **📊 Actualización UI** → `ui.py`
10. **📤 Exportación opcional** → `enhanced_export_system.py`

---

## 🔧 PERSONALIZACIÓN AVANZADA

### 🎨 Modificar la interfaz
**Archivo principal**: `ui.py` (4373 líneas)
**Framework**: TTKBootstrap con temas personalizables

#### Cambiar colores y temas:
```python
# En ui.py, buscar la configuración del tema
self.style = ttk.Style()
self.style.theme_use('cosmo')  # Cambiar tema aquí
```

### 🔍 Agregar nuevos extractores
1. **Crear nuevo archivo** en `core/extractors/`
2. **Implementar clase** heredando de base común
3. **Registrar en** `unified_extractor.py`
4. **Agregar campos** a la base de datos si es necesario

### 📊 Personalizar exportaciones
**Archivo**: `core/enhanced_export_system.py`
- Modificar plantillas Excel
- Agregar nuevos formatos
- Personalizar estilos y gráficos

---

## 📋 TABLA DE REFERENCIA RÁPIDA - COMANDOS CLI

### 🚀 **COMANDOS ESENCIALES PARA DESARROLLADORES**

| 🎯 **Objetivo** | 🛠️ **Comando CLI** | ⚡ **Velocidad** | 📝 **Notas** |
|----------------|-------------------|------------------|---------------|
| **Buscar caso específico** | `.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --buscar-peticion IHQ250001` | ⚡ Muy rápido | Ideal para verificación rápida |
| **Ver estadísticas BD** | `.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --estadisticas` | ⚡ Muy rápido | Overview general del sistema |
| **Analizar caso específico** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --ihq 250001` | ⚡ Rápido | **RECOMENDADO** para análisis |
| **Solo biomarcadores** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --biomarcadores` | ⚡ Rápido | Verificar extracción IHQ |
| **Solo datos paciente** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --paciente` | ⚡ Rápido | Verificar datos demográficos |
| **Comparar PDF vs BD** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --ihq 250001 --comparar-bd` | 🟡 Moderado | Detectar discrepancias |
| **Buscar patrón regex** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --patron "regex"` | 🟡 Moderado | Para patrones específicos |
| **Auditar rango casos** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --auditar-rango 1 50` | 🔴 Lento | Análisis masivo |
| **Análisis completo** | `.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py archivo.pdf --completo` | 🔴 Muy lento | Sin límites, uso ocasional |

### 💻 **PLANTILLAS DE COMANDOS COPY-PASTE**

#### 🔍 **Para diagnóstico rápido:**
```bash
# Buscar caso en BD
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --buscar-peticion IHQ250001

# Analizar PDF específico
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\archivo.pdf" --ihq 250001

# Verificar biomarcadores
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\archivo.pdf" --ihq 250001 --biomarcadores
```

#### 🔧 **Para desarrollo y debug:**
```bash
# Comparar extracción vs BD
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\archivo.pdf" --ihq 250001 --comparar-bd

# Buscar patrón específico
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py "pdfs_patologia\archivo.pdf" --patron "CARCINOMA.*METASTÁSICO"

# Ver estadísticas generales
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --estadisticas
```

#### 📊 **Para auditoría masiva:**
```bash
# Auditar casos por rangos
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --auditar-rango 1 50
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --auditar-rango 51 100
```

#### 🆘 **Para obtener ayuda:**
```bash
# Ver todas las opciones disponibles
.\venv0\Scripts\python.exe herramientas_ia\consulta_base_datos.py --help
.\venv0\Scripts\python.exe herramientas_ia\analizar_pdf_completo.py --help
```

### ⚠️ **RECORDATORIOS IMPORTANTES:**
- ✅ **Usar CLI con argumentos** para automatización
- ❌ **Evitar modo interactivo** en scripts automatizados  
- ⚡ **Usar `--ihq XXXXX`** para análisis específicos y rápidos
- 🔍 **Usar `--comparar-bd`** para detectar problemas de extracción
- 📊 **Usar `--estadisticas`** para overview general del sistema

---

## 🐛 DEBUG Y TROUBLESHOOTING

### 📝 Logs del sistema
**Ubicación**: Consola durante ejecución
**Nivel**: INFO, DEBUG, ERROR
**Configuración**: En cada módulo individual

### 🔍 Herramientas de debug disponibles:
1. **📄 Análisis PDF completo**: `analizar_pdf_completo.py`
2. **💾 Consulta BD interactiva**: `consulta_base_datos.py`
3. **📊 Verificación exportaciones**: `verificar_exceles_exportados.py`
4. **🧪 Suite de pruebas**: `test_herramientas.py`

### ⚠️ Problemas comunes:
- **OCR no funciona**: Verificar instalación Tesseract
- **PDF no se procesa**: Verificar `pdf2image` instalado
- **BD no se conecta**: Verificar permisos en `data/`
- **Exportación falla**: Verificar permisos en Documents/

---

## 🎯 MEJORES PRÁCTICAS

### 💡 Desarrollo:
1. **Usar herramientas de debug** antes de modificar código
2. **Hacer backup** de la BD antes de cambios importantes
3. **Probar extractores** con PDFs conocidos
4. **Documentar cambios** en el código

### 🔒 Producción:
1. **Verificar dependencias** con `test_herramientas.py`
2. **Monitorear exportaciones** regularmente
3. **Hacer respaldos** de la base de datos
4. **Validar integridad** de datos extraídos

---

## 📞 SOPORTE TÉCNICO

### 🤝 Para obtener ayuda:
1. **Revisar esta guía** primero
2. **Usar herramientas de debug** para diagnosticar
3. **Revisar logs** de consola para errores
4. **Verificar configuración** con test_herramientas.py

### 📧 Información del proyecto:
- **Versión actual**: Ver `config/version_info.py`
- **Última actualización**: Ver `documentacion/CHANGELOG.md`
- **Autor**: EVARISIS Team
- **Propósito**: Gestión automatizada oncología HUV

---

## 🔗 ARCHIVOS RELACIONADOS

### 📚 Documentación adicional:
- `documentacion/README.md` - Información general
- `documentacion/CHANGELOG.md` - Historial de cambios
- `documentacion/REPORTE_FINAL_*.md` - Reportes técnicos
- `VERSION_MAC/README_INSTALACION_MACOS.md` - Guía específica macOS

### 🔧 Scripts de utilidad:
- `iniciar_python.bat` - Iniciador Windows
- `COMPILADOR.bat` - Compilación a ejecutable
- `VERSION_MAC/iniciar_python_mac.sh` - Iniciador macOS
- `VERSION_MAC/instalar_entorno_mac.sh` - Instalador macOS

---

*📅 Última actualización: 3 de octubre de 2025*
*🏥 Hospital Universitario del Valle - Sistema de Gestión Oncológica*