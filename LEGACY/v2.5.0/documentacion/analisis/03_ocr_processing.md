# EVARISIS Gestor H.U.V — Análisis de Componente: ocr_processing.py
**Ruta (relativa)**: `ocr_processing.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Motor OCR híbrido que extrae texto de PDFs patológicos priorizando texto nativo sobre OCR con Tesseract, aplicando limpieza post-proceso específica para tokens médicos IHQ.

## 2. Resumen técnico (5–8 líneas)

Este módulo implementa la estrategia dual de extracción de texto: primero intenta extraer texto nativo del PDF usando PyMuPDF, y si no encuentra patrones IHQ válidos, aplica OCR con Tesseract usando múltiples modos PSM para optimizar reconocimiento. Incluye limpieza post-OCR especializada para corregir errores comunes que afectan la segmentación de informes (IHQ######). La configuración es completamente parametrizable vía `config.ini` y soporta procesamiento multi-página con escalamiento automático de imágenes para mejorar precisión OCR.

## 3. Estructura interna y flujo

### Puntos clave

* **`_post_ocr_cleanup(txt: str)`**: Normalización de errores OCR comunes en tokens médicos
  * **Entradas**: Texto crudo de OCR o extracción nativa
  * **Salidas**: Texto normalizado con tokens IHQ######, "N. peticion" estandarizados

* **`pdf_to_text_enhanced(pdf_path: str)`**: Función principal de extracción híbrida
  * **Entradas**: Ruta absoluta a archivo PDF
  * **Salidas**: Texto completo multi-página con marcadores de página

* **Configuración global**: Carga parámetros desde `config.ini` al importar módulo
  * **Entradas**: Archivo `config.ini`, variables de entorno como fallback
  * **Salidas**: Variables globales DPI, PSM_MODE, LANGUAGE, rutas Tesseract

### Flujo principal

1. **Inicialización global**: Carga configuración multi-OS desde `config.ini`
2. **Configuración Tesseract**: Establece executable path según plataforma detectada
3. **Apertura PDF**: PyMuPDF abre documento con manejo de páginas configurables
4. **Por cada página**:
   - **Intento texto nativo**: `page.get_text("text")` con validación patrón IHQ
   - **Si nativo válido**: Usa texto nativo (más limpio y rápido)
   - **Si nativo insuficiente**: Fallback a OCR con preprocessamiento
5. **OCR preprocessing**: Conversión a escala de grises, escalamiento según MIN_WIDTH
6. **OCR multi-intento**: Prueba PSM_MODE configurado + fallbacks (PSM 6, 4)
7. **Validación calidad**: Busca patrones IHQ o longitud mínima para aceptar resultado
8. **Limpieza post-proceso**: `_post_ocr_cleanup()` normaliza tokens críticos
9. **Agregación**: Concatena páginas con separadores identificables

### Configuración dinámica
- **Rutas Tesseract**: Multi-OS con fallback a variables de entorno
- **Parámetros OCR**: DPI (300), PSM_MODE (6), LANGUAGE (spa), configuraciones adicionales
- **Procesamiento**: FIRST_PAGE (1), LAST_PAGE (0=todas), MIN_WIDTH (1000px)

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | PDF patológico | `*.pdf` | PyMuPDF + Tesseract | Por archivo procesado |
| **Entrada** | `config.ini` | INI (UTF-8) | ConfigParser | Una vez al import |
| **Entrada** | Variables entorno | ENV | Fallback configuración | Una vez al import |
| **Salida** | Texto completo | String multi-línea | Procesadores especializados | Por archivo procesado |
| **Salida** | Marcadores página | `--- PÁGINA N ---` | Segmentación downstream | Por página procesada |
| **Salida** | Excepciones detalladas | Exception con contexto | Manejo errores UI | En caso de fallo |

## 5. Dependencias e interacciones

### Internas
- **→ `config.ini`**: Configuración crítica de parámetros OCR y rutas
- **← `procesador_ihq_biomarcadores.py`**: Consume texto extraído para procesamiento especializado
- **← `ui.py`**: Invocado indirectamente vía pipeline de procesamiento

### Externas
- **`fitz` (PyMuPDF)**: Extracción de texto nativo y conversión a imágenes de alta resolución
- **`pytesseract`**: Motor OCR con configuración avanzada PSM y OEM
- **`PIL` (Pillow)**: Preprocessing de imágenes (escala de grises, redimensionamiento)
- **`configparser`**: Lectura de configuración multi-sección con fallbacks
- **`pathlib`**: Manejo robusto de rutas de archivo multiplataforma

### Contrato con Tesseract
- **Executable path**: Configuración obligatoria por plataforma
- **Parámetros OCR**: OEM 1 (LSTM), PSM configurable, idioma spa+eng por defecto
- **Formato salida**: Texto plano con preservación de espacios según configuración

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **PDF corrupto/protegido**: PyMuPDF no puede abrir o extraer contenido
- **Tesseract no disponible**: Executable no encontrado o sin permisos
- **Memoria insuficiente**: Imágenes de alta resolución exceden memoria disponible
- **OCR falla completamente**: Todos los modos PSM devuelven texto ilegible

### Estrategias de manejo
- **Fallback texto nativo → OCR**: Estrategia dual incrementa robustez
- **Multi-intento PSM**: PSM_MODE configurado + fallbacks automáticos (6, 4)
- **Validación de calidad**: Acepta resultado solo si encuentra patrones IHQ o longitud mínima
- **Excepciones contextuales**: Propaga errores con información específica del archivo
- **Limpieza defensiva**: `_post_ocr_cleanup()` maneja texto parcialmente corrupto

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Contenido médico**: Texto extraído contiene información de pacientes
- **Rutas del sistema**: Configuración expone estructura de directorios
- **PDFs temporales**: PyMuPDF puede crear archivos temporales

### Buenas prácticas presentes
- **No persistencia temporal**: Texto procesado en memoria únicamente
- **Encoding explícito**: UTF-8 para todos los archivos de configuración
- **Validación de rutas**: PathLib para manejo seguro de archivos

### Deudas de seguridad
- **Sin sanitización de entrada**: No valida que PDFs sean legítimos (no ejecutables)
- **Logs potencialmente verbosos**: Excepciones pueden exponer contenido médico
- **Sin cifrado en memoria**: Texto extraído permanece sin cifrar durante procesamiento
- **Dependencia externa crítica**: Tesseract ejecutable podría ser comprometido

## 8. Rendimiento y complejidad

### Operaciones costosas
- **OCR de alta resolución**: DPI 300+ con imágenes grandes consume CPU/memoria intensivamente
- **Multi-intento PSM**: Hasta 3 intentos OCR por página si fallan anteriores
- **Redimensionamiento imagen**: Escalamiento para MIN_WIDTH puede ser costoso
- **I/O PDF**: Carga y procesamiento de PDFs multipágina

### Complejidad
- **Temporal**: O(n*m*p) donde n=páginas, m=intentos PSM, p=píxeles por DPI
- **Espacial**: O(w*h*d) por imagen cargada en memoria (width*height*depth)

### Oportunidades de optimización
- **Cache de configuración**: Evitar re-lectura config.ini por cada invocación
- **Procesamiento diferido**: Lazy loading de páginas no requeridas
- **Paralelización**: OCR por página en threads separados
- **Optimización DPI**: DPI adaptativo según calidad detectada del PDF
- **Reutilización Tesseract**: Proceso persistente en lugar de invocaciones separadas

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevos idiomas OCR**: Agregar idiomas a LANGUAGE en config.ini
- **Algoritmos preprocessing**: Extender preprocessing de imagen antes de OCR
- **Modos PSM adicionales**: Ampliar lista de fallbacks PSM según tipos de documento
- **Formatos de entrada**: Extender soporte más allá de PDF (TIFF, PNG, etc.)
- **Post-processing**: Añadir reglas de limpieza específicas por tipo de informe

### Acoplamientos a reducir
- **Configuración global**: Podría inyectarse vía parámetros de función
- **Dependencia Tesseract hard**: Podría abstraerse vía interface OCR Engine
- **Limpieza específica IHQ**: Reglas hardcoded podrían externalizarse a configuración
- **Multi-intento hardcoded**: Secuencia PSM podría ser configurable

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_pdf_native_text_extraction():
    # PDF con texto nativo válido, verificar extracción sin OCR
    
def test_pdf_ocr_fallback():
    # PDF escaneado, verificar fallback a OCR y limpieza
    
def test_multi_page_processing():
    # PDF multipágina, verificar marcadores y concatenación
```

### Bordes
```python
def test_corrupted_pdf():
    # PDF corrupto, verificar excepción contextual
    
def test_tesseract_not_available():
    # Sin Tesseract, verificar graceful fallback o error claro
    
def test_ocr_quality_validation():
    # OCR produce basura, verificar rechazo y reintentos
    
def test_memory_intensive_pdf():
    # PDF alta resolución, verificar manejo de memoria
```

### Doubles y fixtures
- **Mock pytesseract**: Para aislar pruebas de dependencia Tesseract
- **Mock PyMuPDF**: Para simular diferentes tipos de PDF
- **Fixture PDFs**: Archivos de prueba (nativo, escaneado, corrupto, multipágina)
- **Mock config.ini**: Diferentes configuraciones de parámetros OCR

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Tesseract no instalado/configurado** | Crítico | Medio | Validación configuración + fallback a variables entorno |
| **OCR calidad deficiente** | Alto | Alto | Multi-intento PSM + validación calidad + limpieza post-proceso |
| **Memoria insuficiente con PDFs grandes** | Alto | Medio | Procesamiento página a página + escalamiento controlado |
| **PDFs protegidos/corruptos** | Medio | Medio | Try-catch con contexto específico del archivo |
| **Cambios en API PyMuPDF/Tesseract** | Alto | Bajo | Versionado explícito en requirements.txt |
| **Configuración inválida** | Medio | Bajo | Fallbacks en ConfigParser + valores por defecto sensatos |

## 12. Evidencias

### Referencias exactas
- **Función principal**: `ocr_processing.py:61-117` - `pdf_to_text_enhanced()` completa
- **Limpieza post-OCR**: `ocr_processing.py:19-30` - `_post_ocr_cleanup()` con regex especializados
- **Configuración multi-OS**: `ocr_processing.py:31-42` - Detección plataforma y configuración Tesseract
- **Estrategia híbrida**: `ocr_processing.py:72-85` - Intento texto nativo con validación IHQ
- **Multi-intento OCR**: `ocr_processing.py:95-108` - Loop PSM con candidates y validación calidad
- **Parámetros globales**: `ocr_processing.py:45-52` - Carga configuración desde config.ini

### Limitaciones del análisis
- **Dependencia Tesseract externa**: Calidad OCR depende de versión y configuración específica
- **Reglas de limpieza específicas**: `_post_ocr_cleanup()` optimizada para informes HUV únicamente
- **Sin métricas de calidad**: No hay scoring cuantitativo de calidad de extracción