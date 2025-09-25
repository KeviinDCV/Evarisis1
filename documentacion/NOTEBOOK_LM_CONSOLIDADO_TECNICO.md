# EVARISIS Gestor H.U.V - Consolidado Técnico para NotebookLM
**Documento optimizado para análisis IA externa**  
**Generado**: 22 de septiembre de 2025  
**Sistema**: EVARISIS Gestor H.U.V v2.5 - Hospital Universitario del Valle  

## ARQUITECTURA TÉCNICA GENERAL

### Resumen del Sistema
EVARISIS Gestor H.U.V es un sistema especializado de procesamiento OCR para informes médicos oncológicos que automatiza la extracción, normalización y persistencia de datos clínicos críticos para crear la "Base de Datos de la Verdad" oncológica del HUV. El sistema procesa PDFs de patología del Hospital Universitario del Valle, extrae biomarcadores oncológicos específicos (HER2, Ki-67, RE/RP, PD-L1) y almacena resultados en base de datos SQLite para análisis clínico y estratégico, habilitando identificación de patrones de riesgo, determinación de costos de tratamiento y optimización de recursos hospitalarios.

### Pipeline Técnico Principal
```
PDFs Médicos → OCR (PyMuPDF/Tesseract) → Extracción Especializada → Normalización Biomarcadores → SQLite (167 campos) → Dashboard Analítico → Reportes Excel
```

### Componentes Críticos del Sistema

#### 1. huv_ocr_sistema_definitivo.py - Entry Point Principal
- **Rol**: Punto de entrada que inicializa Tesseract OCR y lanza la interfaz principal
- **Líneas código**: 69 líneas de configuración crítica
- **Dependencia crítica**: Path Tesseract multiplataforma desde config.ini
- **Función clave**: `configurar_tesseract()` detecta OS y establece paths ejecutables

#### 2. ui.py - Interfaz Unificada CustomTkinter (1299 líneas)
- **Arquitectura**: 4 tabs especializados con dashboard integrado
  - Tab 1: Procesamiento PDFs con preview y validación
  - Tab 2: Visualización datos con filtros dinámicos  
  - Tab 3: Dashboard analítico con Matplotlib/Seaborn
  - Tab 4: Automatización portal HUV con Selenium
- **Gestión estado**: Thread-safe con actualizaciones asíncronas
- **Dashboard**: 8 tipos visualización (barras, líneas, scatter, heatmaps)
- **Performance**: Lazy loading datasets, filtros optimizados, zoom interactivo

#### 3. ocr_processing.py - Engine OCR Híbrido (117 líneas)
- **Estrategia dual**: PyMuPDF text nativo + Tesseract OCR fallback
- **Pipeline limpieza**: Eliminación caracteres especiales médicos, normalización espacios
- **Optimización**: Detección automática calidad texto para selección engine
- **Función crítica**: `clean_medical_text()` preserva terminología oncológica

#### 4. procesador_ihq_biomarcadores.py - Extractor Especializado (369 líneas)
- **Dominio médico**: Especializado en biomarcadores oncológicos HUV
- **Segmentación**: Multi-report parsing por PDF usando separadores médicos
- **Biomarcadores soportados**: HER2 (0-3+), Ki-67 (%), RE/RP (%), PD-L1 (CPS), P16
- **Normalización**: Mapeo variantes textuales a valores canónicos médicos
- **Validación**: Rangos clínicos y consistencia interna por biomarcador

#### 5. database_manager.py - Persistencia SQLite (86 líneas)
- **Esquema**: Tabla única `informes_ihq` con 167 campos médicos
- **Control duplicados**: Por número petición antes de inserción  
- **Transaccionalidad**: Operaciones ACID con rollback automático
- **Integración**: pandas DataFrame para dashboard seamless
- **Performance**: Conexiones efímeras evitan locks prolongados

#### 6. huv_web_automation.py - Automatización Portal Selenium
- **Target**: Portal institucional `huvpatologia.qhorte.com`
- **Funcionalidad**: Login automático, navegación guiada, descarga PDFs
- **Robustez**: WebDriverWait con múltiples estrategias selector
- **Error recovery**: Reintentos automáticos, fallback strategies
- **Anti-detección**: Configuraciones browser humanizadas

#### 7. calendario.py - Scheduler Interno
- **Framework**: `schedule` Python con threading background
- **Automatización**: Descargas periódicas, procesamiento batch, reportes
- **Configuración**: Horarios persistentes en config.ini
- **Thread safety**: Locks para acceso concurrente scheduler

#### 8. huv_constants.py - Vocabulario Médico Centralizado
- **Biomarcadores**: Diccionarios valores válidos HER2/Ki-67/RE/RP/PD-L1
- **Patrones regex**: Expresiones optimizadas extracción campos médicos
- **Servicios HUV**: Mapeos normalizados departamentos hospitalarios
- **Códigos diagnóstico**: Equivalencias ICD-10 y categorización

#### 9. config.ini - Configuración Multiplataforma
- **Secciones**: [TESSERACT], [DATABASE], [PORTAL_HUV], [PROCESSING]
- **Detección OS**: Paths automáticos Windows/Linux/macOS
- **Parámetros OCR**: OEM mode, PSM mode, DPI override, language
- **Timeouts**: Portal automation, database connections

#### 10. test_sistema.py - Suite Pruebas Automatizadas
- **Cobertura**: Tests unitarios + integración + performance
- **Datos médicos**: Fixtures anonimizadas con ground truth
- **Validación crítica**: Precisión biomarcadores >= 95%
- **Mocking**: Portal HUV, WebDriver, file system para tests aislados

## FLUJOS TÉCNICOS CRÍTICOS

### Flujo 1: Procesamiento PDF Individual
```python
# 1. Carga y validación PDF
pdf_path = validar_archivo_pdf(input_file)

# 2. Extracción texto OCR híbrida  
texto_crudo = ocr_processing.extract_text_hybrid(pdf_path)
texto_limpio = ocr_processing.clean_medical_text(texto_crudo)

# 3. Segmentación multi-informe
informes = procesador_ihq_biomarcadores.segment_reports(texto_limpio)

# 4. Extracción biomarcadores por informe
for informe in informes:
    biomarcadores = extract_biomarkers_ihq(informe)
    datos_normalizados = normalize_medical_values(biomarcadores)
    
# 5. Persistencia con control duplicados
database_manager.save_records(datos_normalizados)

# 6. Actualización dashboard tiempo real
ui.update_dashboard_with_new_data()
```

### Flujo 2: Automatización Portal HUV
```python
# 1. Setup WebDriver con configuraciones anti-detección
driver = huv_web_automation.setup_driver(headless=True)

# 2. Autenticación portal institucional
success = huv_web_automation.login_huv_portal(driver, credentials)

# 3. Navegación a sección patología con esperas inteligentes
huv_web_automation.navigate_to_pathology_section(driver)

# 4. Aplicación filtros y descarga masiva
criterios = {"fecha_inicio": "2025-09-01", "tipo": "IHQ"}
archivos = huv_web_automation.download_pathology_pdfs(driver, criterios)

# 5. Procesamiento automático archivos descargados
for archivo in archivos:
    procesar_pdf_completo(archivo)
```

### Flujo 3: Dashboard Analítico Tiempo Real
```python
# 1. Query optimizada base datos con filtros
filtros = {"servicio": "Mastología", "fecha_rango": "ultimo_mes"}
df = database_manager.get_filtered_dataframe(filtros)

# 2. Cálculos estadísticos biomarcadores
estadisticas = calcular_metricas_clinicas(df)
correlaciones = analizar_correlaciones_biomarcadores(df)

# 3. Generación visualizaciones dinámicas
graficos = {
    "distribucion_her2": generar_barplot_her2(df),
    "tendencia_ki67": generar_lineplot_temporal(df, "ki67"),
    "correlacion_re_rp": generar_scatterplot(df, "RE", "RP"),
    "heatmap_servicios": generar_heatmap_servicios(df)
}

# 4. Actualización UI thread-safe
ui.actualizar_dashboard_async(graficos, estadisticas)
```

## DATOS MÉDICOS Y ESTRUCTURAS

### Esquema Base de Datos (167 campos)
```sql
CREATE TABLE informes_ihq (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Identificación paciente/informe
    numero_peticion TEXT UNIQUE,
    nombre_paciente TEXT,
    fecha_nacimiento TEXT,
    cedula TEXT,
    
    -- Biomarcadores críticos IHQ
    her2_resultado TEXT,           -- 0, 1+, 2+, 3+, POSITIVO, NEGATIVO
    ki67_porcentaje TEXT,          -- <5%, 5-14%, 15-30%, >30%
    receptor_estrogenico TEXT,     -- POSITIVO/NEGATIVO + %
    receptor_progesterona TEXT,    -- POSITIVO/NEGATIVO + %
    pd_l1_resultado TEXT,          -- <1%, 1-49%, >=50%
    p16_resultado TEXT,            -- POSITIVO/NEGATIVO
    
    -- Información clínica
    servicio_solicitante TEXT,
    medico_tratante TEXT,
    diagnostico_principal TEXT,
    estudios_solicitados TEXT,
    
    -- Metadatos sistema
    fecha_procesado DATETIME,
    archivo_origen TEXT,
    calidad_ocr INTEGER,
    
    -- ... 140+ campos adicionales
);
```

### Patrones Regex Médicos Críticos
```python
REGEX_PATTERNS = {
    'numero_peticion': r'(?:N°|No\.?|Petición)\s*:?\s*([A-Z]?\d{6,8})',
    'fecha_nacimiento': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    'her2_resultado': r'HER-?2[:\s]*([0-3]\+?|POSITIVO|NEGATIVO)',
    'ki67_porcentaje': r'Ki-?67[:\s]*([<>]?\d+(?:\.\d+)?%?)',
    'receptor_estrogenico': r'(?:RE|Receptor.*Estrógeno)[:\s]*(\d+%|POSITIVO|NEGATIVO)',
    'receptor_progesterona': r'(?:RP|Receptor.*Progesterona)[:\s]*(\d+%|POSITIVO|NEGATIVO)',
    'pd_l1_score': r'PD-?L1[:\s]*([<>]?\d+%?|CPS\s*\d+)',
    'diagnostico_final': r'(?:DIAGNÓSTICO|CONCLUSIÓN)[:\s]*(.+?)(?=\n\n|\n[A-Z])',
    'medico_patólogo': r'(?:PATÓLOGO|Dr\.|Dra\.)[:\s]*([A-ZÁÉÍÓÚ][a-záéíóú\s]+)',
}
```

### Biomarcadores Oncológicos Soportados
```python
BIOMARKERS_VOCABULARY = {
    'HER2': {
        'valores_validos': ['0', '1+', '2+', '3+', 'NEGATIVO', 'POSITIVO'],
        'interpretacion': {
            '0': 'Negativo', '1+': 'Negativo', 
            '2+': 'Equívoco (requiere FISH)', 
            '3+': 'Positivo sobreexpresado'
        }
    },
    'Ki67': {
        'rangos': ['<5%', '5-14%', '15-30%', '>30%'],
        'clasificacion': {
            '<15%': 'BAJO', '15-30%': 'INTERMEDIO', '>30%': 'ALTO'
        }
    },
    'RE': {
        'valores': ['POSITIVO', 'NEGATIVO', 'PORCENTAJE'],
        'threshold_positivo': 1  # >= 1% considerado positivo
    },
    'RP': {
        'valores': ['POSITIVO', 'NEGATIVO', 'PORCENTAJE'], 
        'threshold_positivo': 1  # >= 1% considerado positivo
    },
    'PD_L1': {
        'scoring': ['CPS', 'TPS', 'IC'],
        'thresholds': {'<1%': 'Bajo', '1-49%': 'Intermedio', '>=50%': 'Alto'}
    }
}
```

## RIESGOS TÉCNICOS IDENTIFICADOS

### Riesgos Críticos de Seguridad Médica
1. **Datos médicos sin cifrado**: Base SQLite almacena información sensible sin protección
2. **Sin auditoría accesos**: No hay trazabilidad de quién accede/modifica datos pacientes
3. **Credenciales portal texto plano**: Passwords interceptables en memoria
4. **Logs con información médica**: Posible leak datos sensibles en archivos log

### Riesgos Performance y Escalabilidad  
1. **OCR bottleneck**: Procesamiento secuencial PDFs limita throughput
2. **SQLite locks**: Acceso concurrente desde UI puede causar bloqueos
3. **Memory leaks**: Dashboard con datasets grandes puede agotar memoria
4. **Selenium instability**: Automatización portal vulnerable a cambios DOM

### Riesgos Operacionales Médicos
1. **Precisión biomarcadores**: Errores OCR pueden afectar valores críticos para tratamiento
2. **Vocabulario desactualizado**: Terminología médica puede cambiar sin actualización sistema  
3. **Dependencia Tesseract**: Fallo OCR engine compromete funcionalidad completa
4. **Portal HUV changes**: Cambios estructura portal rompen automatización

## OPORTUNIDADES DE OPTIMIZACIÓN

### Performance Críticas
1. **OCR paralelo**: Procesamiento concurrente múltiples PDFs
2. **Database indexing**: Índices en campos críticos (numero_peticion, fecha, servicio)
3. **Connection pooling**: Reutilizar conexiones SQLite para mejor throughput
4. **Caching inteligente**: Cache compiled regex patterns y vocabulario médico
5. **Lazy loading dashboard**: Paginación datasets grandes para UI responsiva

### Arquitectura y Mantenibilidad
1. **Plugin system**: Arquitectura modular para nuevos tipos informe médico
2. **Configuration management**: External config para vocabulario médico actualizable
3. **Error monitoring**: Sistema centralizado logging y alertas
4. **API layer**: REST API para integración con sistemas hospitalarios (lectura/auditoría) y herramientas de visualización internas
5. **Containerization**: Docker para deployment reproducible multiplataforma

### Extensibilidad Médica
1. **Multi-hospital support**: Abstracción para diferentes instituciones
2. **DICOM integration**: Soporte imágenes médicas además de PDFs texto
3. **HL7 FHIR**: Estándares interoperabilidad para integración hospitalaria
4. **ML/AI enhancement**: Modelos machine learning para mejora precision extracción
5. **Real-time dashboards**: Streaming updates para monitoreo clínico continuo

## MÉTRICAS TÉCNICAS CLAVE

### Cobertura de Código y Calidad
- **Líneas código total**: ~2.200 líneas Python
- **Componentes críticos**: 10 módulos principales documentados
- **Referencias exactas**: 120+ referencias archivo:línea para mantenibilidad
- **Test coverage**: Suite automatizada con fixtures médicas anonimizadas

### Performance Benchmarks
- **OCR processing**: ~2-5 segundos por PDF estándar
- **Database operations**: <100ms inserción, <500ms queries filtradas
- **UI responsiveness**: <1 segundo actualización dashboard con datasets 1000+ registros
- **Portal automation**: ~30-60 segundos por sesión descarga completa

### Precisión Médica
- **Biomarcadores extraction**: Meta >= 95% precisión en campos críticos
- **OCR quality**: Threshold mínimo 60% confidence Tesseract
- **Data integrity**: Control duplicados 100% por número petición
- **Medical terminology**: Vocabulario centralizado 200+ términos oncológicos

### Escalabilidad y Límites
- **SQLite capacity**: Testado hasta 10,000 registros sin degradación significativa  
- **Concurrent users**: UI diseñada para uso single-user institucional
- **File processing**: Batch processing hasta 50 PDFs sin memory issues
- **Portal throughput**: Rate limiting respeta policies institucionales HUV

## DEPENDENCIAS TÉCNICAS CRÍTICAS

### Dependencias Sistema Operativo
```txt
# Windows
tesseract.exe en C:\Program Files\Tesseract-OCR\
Chrome/Firefox + WebDriver compatible

# Linux  
tesseract via apt/yum package manager
chromium-driver o geckodriver en PATH

# macOS
tesseract via homebrew
Safari WebDriver o Chrome via cask
```

### Dependencias Python Críticas
```txt
# OCR y procesamiento
PyMuPDF==1.23.5          # PDF text extraction nativa
pytesseract==0.3.10      # Tesseract OCR wrapper
Pillow==10.0.0            # Image processing OCR

# UI y visualización  
customtkinter==5.2.0     # Modern UI framework
matplotlib==3.7.2        # Plotting dashboard
seaborn==0.12.2          # Statistical visualization
pandas==2.0.3            # Data manipulation

# Database y web
sqlite3                   # Built-in Python (persistencia)
selenium==4.11.2         # Web automation portal
requests==2.31.0         # HTTP client adicional

# Scheduling y utilidades
schedule==1.2.0          # Job scheduling interno
python-dateutil==2.8.2   # Date parsing robusto
configparser             # Built-in (config.ini)
```

### Configuraciones Críticas Deployment
```ini
# config.ini crítico para deployment
[TESSERACT]
windows_path = C:\Program Files\Tesseract-OCR\tesseract.exe
oem_mode = 3              # LSTM + Legacy OCR engine
psm_mode = 6              # Uniform block of text
language = spa            # Spanish language model
dpi_override = 300        # High resolution processing

[DATABASE]  
db_file = huv_oncologia.db
backup_enabled = true
timeout = 30

[PORTAL_HUV]
base_url = https://huvpatologia.qhorte.com  
login_timeout = 15
headless_mode = true      # Production mode
retry_attempts = 3

[PROCESSING]
min_ocr_confidence = 60   # Quality threshold
max_concurrent_pdfs = 4   # Resource management
debug_mode = false        # Production setting
```

## INTEGRATION POINTS Y APIs

### Puntos Integración Actuales
1. **SQLite Database**: Interface estándar SQL para external tools
2. **Excel Export**: Formato estándar para análisis estadísticos y reportes gerenciales
3. **Portal HUV**: Web scraping automatizado institucional
4. **File System**: Standard file I/O para PDFs y configuración

### APIs Potenciales Futuras
```python
# REST API conceptual para integración externa
GET /api/v1/informes?servicio={servicio}&fecha={rango}
POST /api/v1/procesar-pdf
GET /api/v1/biomarcadores/estadisticas
GET /api/v1/dashboard/metricas
PUT /api/v1/configuracion/vocabulario
```

### Integración Sistemas Hospitalarios
- **HIS (Hospital Information System)**: Cross-referencia y auditoría futura usando la base de datos como estándar autoritativo
- **LIS (Laboratory Information System)**: Verificación cruzada resultados lab contra base de datos de la verdad
- **PACS (Picture Archive System)**: Correlación con imágenes radiológicas para validación integral  
- **EMR/SERVINTE**: Futura integración de auditoría para corrección de información existente usando datos autoritativos del proyecto

Este documento consolida todos los aspectos técnicos críticos del sistema EVARISIS Gestor H.U.V v2.5 para análisis por sistemas IA externos como NotebookLM, proporcionando una visión completa desde arquitectura hasta implementación, riesgos y oportunidades de evolución.