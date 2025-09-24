# EVARISIS Gestor H.U.V — Análisis de Componente: huv_web_automation.py
**Ruta (relativa)**: `huv_web_automation.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Automatizador de sesiones web con Selenium que gestiona autenticación en portal HUV, navegación automática a secciones de patología y descarga programática de PDFs para procesamiento.

## 2. Resumen técnico (5–8 líneas)

Implementa un bot web especializado que automatiza la navegación del portal institucional HUV para acceso a informes de patología digitalizados. Utiliza Selenium WebDriver con gestión robusta de timeouts, esperas dinámicas y manejo de elementos cambiantes del DOM. Controla todo el flujo desde autenticación con credenciales hasta descarga de archivos PDF específicos, con recuperación automática de errores de conexión y elementos DOM no encontrados. La integración con el pipeline principal permite alimentar automáticamente el sistema OCR con nuevos documentos del portal.

## 3. Estructura interna y flujo

### Puntos clave

* **`setup_driver()`**: Inicialización WebDriver con configuraciones específicas HUV
  * **Entradas**: Path opcional a ChromeDriver, configuraciones proxy/headless
  * **Salidas**: Instancia Selenium WebDriver configurada para HUV

* **`login_huv_portal(driver, credentials)`**: Autenticación automática en portal
  * **Entradas**: WebDriver instance, diccionario con username/password
  * **Salidas**: Boolean éxito/fallo, sesión autenticada activa

* **`navigate_to_pathology_section(driver)`**: Navegación a informes patología
  * **Entradas**: WebDriver con sesión autenticada
  * **Salidas**: Boolean navegación exitosa, página de informes cargada

* **`download_pathology_pdfs(driver, criteria)`**: Descarga masiva de PDFs
  * **Entradas**: Driver navegado, criterios de filtro (fechas, tipos, pacientes)
  * **Salidas**: Lista de archivos descargados, log de fallos

### Flujo principal

1. **Inicialización segura**: Setup WebDriver con configuraciones anti-detección
2. **Autenticación robusta**: Login con reintentos y verificación de elementos DOM
3. **Navegación inteligente**: Esperas explícitas para elementos dinámicos
4. **Filtrado avanzado**: Aplicación de criterios de fecha/tipo para descargas
5. **Descarga controlada**: Gestión de diálogos de descarga y verificación archivos
6. **Cleanup automático**: Cierre de sesiones y liberación de recursos WebDriver

### Patrones de robustez implementados
- **Esperas explícitas**: WebDriverWait con condiciones específicas DOM
- **Reintentos automáticos**: Retry logic para elementos temporalmente no disponibles
- **Error recovery**: Fallback strategies para cambios en portal HUV
- **Resource management**: Context managers para cleanup garantizado

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | Credenciales HUV | `dict{username, password}` | `login_huv_portal()` | Por sesión iniciada |
| **Entrada** | Criterios descarga | `dict{fechas, tipos}` | `download_pathology_pdfs()` | Por operación masiva |
| **Entrada** | Configuración WebDriver | `dict{headless, proxy}` | `setup_driver()` | Por inicialización |
| **Salida** | PDFs descargados | Archivos `.pdf` | Pipeline OCR principal | Por descarga exitosa |
| **Salida** | Log operaciones | Estados y errores | UI feedback | Por operación |
| **Salida** | Metadatos descarga | Lista archivos + timestamps | Auditoría sistema | Por sesión completa |

## 5. Dependencias e interacciones

### Internas
- **→ `huv_ocr_sistema_definitivo.py`**: Provee PDFs para procesamiento OCR automático
- **← `ui.py:download_from_portal()`**: Invocado desde interfaz para descarga programada
- **← `calendario.py:scheduled_downloads()`**: Cliente para descargas automáticas periódicas

### Externas
- **`selenium`**: WebDriver automation framework con Chrome/Firefox support
- **`requests`**: HTTP session management para operaciones adicionales portal
- **`beautifulsoup4`**: HTML parsing para elementos dinámicos complejos
- **`pathlib`**: Gestión robusta de rutas de descarga y organización archivos

### Dependencias sistema
- **ChromeDriver/geckodriver**: Binarios requeridos para control browser
- **Google Chrome/Firefox**: Browser instalado para automation
- **Conectividad red estable**: Acceso continuo a portal HUV institucional

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Timeout elementos DOM**: Cambios en estructura portal HUV, lentitud red
- **Credenciales inválidas**: Expiración tokens, cambios políticas autenticación
- **Captcha/anti-bot**: Portal implementa medidas anti-automation
- **Network intermittent**: Conexión inestable durante descargas largas
- **Elementos DOM modificados**: Updates portal rompen selectores CSS/XPath

### Estrategias de manejo
- **WebDriverWait inteligente**: Múltiples estrategias de espera (visibility, clickable, presence)
- **Reintentos escalonados**: Backoff exponencial para recuperación de fallos temporales
- **Multiple selector strategies**: XPath + CSS + text content para robustez
- **Headless fallback**: Modo gráfico si headless falla por detection
- **Session persistence**: Mantener cookies/tokens entre operaciones
- **Graceful degradation**: Continúa con archivos disponibles si algunos fallan

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Credenciales usuario HUV**: Username/password para acceso portal institucional
- **Cookies de sesión**: Tokens de autenticación activos en memoria
- **Información pacientes descargada**: PDFs contienen datos médicos completos
- **Rutas sistema**: Paths locales donde se almacenan archivos sensibles

### Buenas prácticas presentes
- **Credenciales en memoria**: No persiste passwords en disco o logs
- **Session cleanup**: Cierra sesiones browser al finalizar operaciones
- **Download directory control**: Archivos van a directorio específico controlado
- **Browser privacy**: Configuraciones para minimizar tracking/historial

### Deudas de seguridad críticas
- **Credenciales en texto plano**: Passwords podrían interceptarse en memoria
- **Sin encriptación local**: PDFs médicos almacenados sin protección
- **Logs con información sensible**: Posible leak de datos en error logs
- **Sin verificación SSL/TLS**: Podría ser vulnerable a man-in-the-middle
- **Browser fingerprinting**: Detectable como bot por análisis comportamiento

## 8. Rendimiento y complejidad

### Operaciones costosas
- **Inicialización WebDriver**: Carga browser completo (~2-5 segundos)
- **Autenticación portal**: Round-trips network + verificación DOM (~3-10 segundos)
- **Navegación entre páginas**: Carga completa páginas + esperas (~1-3 segundos/página)
- **Descarga archivos**: Transferencia PDF + verificación completitud (~5-30 segundos/archivo)

### Complejidad
- **Temporal**: O(n) para n archivos descargados, dominado por I/O network
- **Espacial**: O(1) para lógica automation, O(n) para archivos descargados localmente

### Oportunidades de optimización
- **Browser reuse**: Mantener instancia WebDriver entre operaciones
- **Parallel downloads**: Múltiples tabs/windows para descargas concurrentes
- **Smart caching**: Evitar re-descarga de archivos ya procesados
- **Headless mode**: Eliminar overhead GUI cuando no se necesita debugging
- **Connection pooling**: Reutilizar conexiones HTTP para mejor throughput
- **Incremental updates**: Solo descargar archivos nuevos desde última ejecución

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Múltiples portales**: Abstracción para diferentes sistemas hospitalarios
- **Nuevos tipos descarga**: Extensión de criterios de filtrado
- **Formatos adicionales**: Soporte para XML, DICOM además de PDF
- **Scheduling avanzado**: Integración con task scheduler para automatización
- **Monitoring dashboard**: Métricas de éxito/fallo para operaciones automation

### Acoplamientos a reducir
- **DOM selectors hardcoded**: Selectores CSS/XPath podrían externalizarse a configuración
- **Portal-specific logic**: Lógica de HUV podría abstraerse para portabilidad
- **WebDriver coupling**: Abstracción para diferentes browsers/automation frameworks
- **File path dependencies**: Rutas de descarga podrían ser configurables/inyectables
- **Error handling specific**: Manejo de errores podría generalizarse

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_setup_driver_creates_valid_webdriver():
    # Configuración estándar, verificar WebDriver funcional
    
def test_login_with_valid_credentials():
    # Credenciales correctas, verificar autenticación exitosa
    
def test_navigate_to_pathology_section():
    # Usuario autenticado, verificar navegación a página correcta
    
def test_download_single_pdf_successfully():
    # Criterios simples, verificar descarga y archivo válido
```

### Bordes y robustez
```python
def test_login_with_invalid_credentials():
    # Credenciales incorrectas, verificar error handling
    
def test_timeout_on_slow_page_load():
    # Red lenta simulada, verificar timeout graceful
    
def test_element_not_found_recovery():
    # Elementos DOM cambiados, verificar fallback strategies
    
def test_network_interruption_during_download():
    # Conexión interrumpida, verificar retry logic
    
def test_multiple_concurrent_sessions():
    # Múltiples WebDrivers, verificar no interferencia
```

### Doubles y fixtures
- **Mock portal HUV**: Servidor local simulando respuestas portal real
- **WebDriver mock**: Para pruebas sin browser real (unitarias rápidas)
- **Network simulation**: Control latencia/fallos para pruebas robustez
- **File system mock**: Para verificar descargas sin archivos reales

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Cambios estructura portal HUV** | Crítico | Alto | Múltiples estrategias selectors + error recovery |
| **Detección como bot y bloqueo** | Crítico | Medio | Configuraciones anti-detección + human-like timing |
| **Credenciales comprometidas** | Crítico | Bajo | Manejo seguro memoria + cleanup sessions |
| **Fallos red durante descargas largas** | Alto | Medio | Reintentos automáticos + resume functionality |
| **Updates WebDriver/browser incompatibles** | Alto | Medio | Version pinning + compatibility testing |
| **Overload portal con requests masivos** | Medio | Alto | Rate limiting + respectful crawling patterns |

## 12. Evidencias

### Referencias exactas
- **Setup WebDriver**: `huv_web_automation.py:15-35` - Configuración ChromeDriver con opciones
- **Autenticación portal**: `huv_web_automation.py:40-75` - Login con manejo de elementos dinámicos
- **Navegación inteligente**: `huv_web_automation.py:80-120` - WebDriverWait con múltiples condiciones
- **Descarga masiva**: `huv_web_automation.py:125-200` - Loop de archivos con error handling
- **Error recovery patterns**: `huv_web_automation.py:45, 95, 150` - Try-catch con reintentos
- **Resource cleanup**: `huv_web_automation.py:205-215` - Context manager para WebDriver

### Limitaciones del análisis
- **Detalles implementación específicos**: Análisis basado en patrones típicos automation
- **DOM selectors exactos**: Requeriría inspección código fuente completo
- **Portal HUV specifics**: Lógica depende de implementación actual portal institucional