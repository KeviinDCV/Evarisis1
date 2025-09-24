# EVARISIS Gestor H.U.V — Análisis de Componente: config.ini
**Ruta (relativa)**: `config.ini`  
**Tipo**: configuracion  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Archivo de configuración centralizado que define parámetros de ejecución multi-OS, rutas de Tesseract OCR, configuraciones de base de datos y ajustes de comportamiento del sistema según el entorno de despliegue.

## 2. Resumen técnico (5–8 líneas)

Consolida toda la configuración crítica del sistema en formato INI estándar con secciones organizadas por funcionalidad: paths de Tesseract para Windows/Linux/macOS, configuración SQLite, parámetros OCR de calidad, y settings específicos del portal HUV. La detección automática del OS permite deployment sin modificación manual, mientras que la estructura seccional facilita mantenimiento y extensión. Incluye configuraciones de fallback para entornos de desarrollo y parámetros de optimización específicos para OCR de documentos médicos con calidades variables.

## 3. Estructura interna y flujo

### Puntos clave

* **`[TESSERACT]`**: Configuración multiplataforma para engine OCR
  * **Contenido**: Rutas ejecutables por OS, parámetros optimización médica
  * **Uso**: Inicialización `huv_ocr_sistema_definitivo.py` y `ocr_processing.py`

* **`[DATABASE]`**: Configuración persistencia SQLite
  * **Contenido**: Nombre archivo BD, configuraciones conexión, backups
  * **Uso**: `database_manager.py` para inicialización y operaciones

* **`[PORTAL_HUV]`**: Configuración automatización web específica
  * **Contenido**: URLs portal, timeouts, configuración browser automation
  * **Uso**: `huv_web_automation.py` para navegación y descarga

* **`[PROCESSING]`**: Parámetros de procesamiento OCR y extracción
  * **Contenido**: Calidad mínima OCR, threads concurrentes, batch sizes
  * **Uso**: Todos los módulos de procesamiento para optimización

### Estructura típica
```ini
[TESSERACT]
windows_path = C:\Program Files\Tesseract-OCR\tesseract.exe
linux_path = /usr/bin/tesseract
macos_path = /usr/local/bin/tesseract
oem_mode = 3
psm_mode = 6
language = spa
dpi_override = 300

[DATABASE]
db_file = huv_oncologia.db
backup_enabled = true
backup_frequency = daily
max_connections = 10
timeout = 30

[PORTAL_HUV]
base_url = https://portal.huv.gov.co
login_timeout = 15
download_timeout = 120
retry_attempts = 3
headless_mode = true

[PROCESSING]
min_ocr_confidence = 60
max_concurrent_pdfs = 4
batch_size = 10
temp_cleanup = true
debug_mode = false
```

### Flujo de carga
1. **Detección OS**: `platform.system()` determina sección OS apropiada
2. **Carga ConfigParser**: Parsing completo archivo con validación formato
3. **Distribución settings**: Cada módulo consume sección específica
4. **Fallback defaults**: Valores por defecto si configuración falta
5. **Validación paths**: Verificación existencia ejecutables/archivos críticos

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | Modificaciones manuales | Archivo INI texto | Administrador sistema | Por cambio configuración |
| **Entrada** | Updates automáticos | Escritura programática | Sistema durante runtime | Por optimización dinámica |
| **Salida** | Configuración Tesseract | Path + parámetros | OCR modules | Al inicializar |
| **Salida** | Settings BD | Connection params | `database_manager.py` | Por conexión |
| **Salida** | Config portal | URLs + timeouts | `huv_web_automation.py` | Por sesión web |
| **Salida** | Parámetros procesamiento | Límites + optimización | Todos los procesadores | Por operación |

## 5. Dependencias e interacciones

### Internas (alta frecuencia)
- **← `huv_ocr_sistema_definitivo.py`**: Consume path Tesseract para inicialización
- **← `database_manager.py`**: Lee configuración BD para conexiones SQLite
- **← `huv_web_automation.py`**: Usa settings portal para automation parameters
- **← `ocr_processing.py`**: Consume parámetros calidad y performance OCR

### Externas
- **`configparser`**: Parsing estándar Python para archivos INI
- **`platform`**: Detección OS para selección configuración apropiada
- **`pathlib`**: Validación existencia paths y archivos configurados
- **`os.path`**: Manejo rutas multiplataforma robusto

### Patrón de acceso
- **Singleton loading**: Cargado una vez al inicio, compartido entre módulos
- **Lazy validation**: Validación de paths solo cuando se usan primera vez
- **Hot reload**: Algunos cambios pueden aplicarse sin reiniciar sistema

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Archivo faltante**: config.ini no existe en deployment
- **Formato inválido**: Sintaxis INI corrupta o malformada
- **Paths inexistentes**: Ejecutables Tesseract no están en rutas configuradas
- **Valores fuera de rango**: Timeouts/límites con valores no válidos
- **Permisos insuficientes**: No se puede leer o escribir archivo configuración

### Estrategias de manejo
- **Defaults robustos**: Valores por defecto funcionales para todos los parámetros
- **Path discovery**: Búsqueda automática de Tesseract en locations estándar
- **Validación progresiva**: Verificar configuración solo cuando se necesita
- **Error logging**: Registrar problemas configuración para debugging
- **Graceful degradation**: Sistema funciona con configuración mínima
- **Auto-generation**: Crear config.ini con defaults si no existe

## 7. Seguridad y datos sensibles

### Datos sensibles
- **URLs portal HUV**: Endpoints específicos que podrían ser confidenciales
- **Paths sistema**: Rutas podrían revelar estructura filesystem
- **Parámetros conexión**: Settings BD podrían exponer información arquitectura

### Buenas prácticas presentes
- **Solo configuración**: No contiene credenciales o datos médicos
- **Local file**: Configuración almacenada localmente, no transmitida
- **Read-only después carga**: Modificaciones solo por admin

### Deudas de seguridad menores
- **Paths en texto plano**: Rutas sistema visibles a cualquier usuario con acceso
- **Sin cifrado**: Archivo configuración no está protegido
- **Permisos file system**: Depende de OS para controlar acceso
- **No rotación secrets**: Si se añaden secrets, no hay mecanismo rotación

## 8. Rendimiento y complejidad

### Operaciones costosas
- **File I/O**: Lectura archivo desde disco al inicializar cada módulo
- **Parsing INI**: ConfigParser processing, aunque es muy eficiente
- **Path validation**: Verificación existencia archivos/directorios configurados
- **OS detection**: platform.system() call, aunque es muy rápida

### Complejidad
- **Espacial**: O(C) donde C es cantidad total configuraciones
- **Temporal**: O(1) para lookups después de carga inicial O(n) parsing

### Oportunidades de optimización
- **Config caching**: Cargar una vez, compartir objeto entre módulos
- **Lazy loading sections**: Cargar solo secciones que se usan
- **Compiled validation**: Pre-compilar validaciones complejas
- **Memory mapping**: Para archivos config muy grandes (no aplicable aquí)
- **Hot reload inteligente**: Solo recargar secciones modificadas

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevas secciones**: Agregar módulos con sus propias configuraciones
- **Parámetros adicionales**: Más settings en secciones existentes
- **Environment overrides**: Variables de entorno que override config.ini
- **Profile support**: Múltiples perfiles (dev/staging/prod) en mismo archivo
- **Include directives**: Separar configuración en múltiples archivos

### Acoplamientos a reducir
- **Hardcoded section names**: Nombres de secciones podrían ser más flexibles
- **OS-specific sections**: Podría unificarse con detección automática mejorada
- **Static file location**: Path de config.ini podría ser configurable
- **Format dependency**: Acoplamiento fuerte a formato INI específico

## 10. Pruebas recomendadas (test design)

### Validación configuración
```python
def test_config_file_exists_and_parseable():
    # Archivo existe y tiene formato INI válido
    
def test_all_required_sections_present():
    # Secciones críticas (TESSERACT, DATABASE) están definidas
    
def test_tesseract_paths_valid_for_current_os():
    # Path configurado para OS actual apunta a ejecutable válido
    
def test_database_config_has_required_fields():
    # Sección DATABASE tiene todos los campos obligatorios
```

### Robustez y fallbacks
```python
def test_missing_config_file_uses_defaults():
    # Sistema funciona con defaults cuando config.ini falta
    
def test_invalid_values_fallback_gracefully():
    # Valores fuera de rango usan fallbacks sin fallar
    
def test_partial_config_sections_handled():
    # Secciones incompletas se completan con defaults
    
def test_different_os_configurations():
    # Mock diferentes OS, verificar path selection correcta
```

### Doubles y fixtures
- **Mock config files**: Archivos INI test con diferentes configuraciones
- **Platform mocking**: Simular diferentes OS para testing multiplataforma
- **File system mocking**: Test sin dependencias filesystem reales
- **Temporary config**: Archivos temporales para testing modificaciones

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Config file corruption pierde todos settings** | Alto | Bajo | Defaults funcionales + auto-generation |
| **Paths incorrectos rompen OCR completamente** | Crítico | Medio | Path discovery + validation al uso |
| **Timeouts inadecuados causan fallos intermitentes** | Alto | Alto | Valores conservadores + configurabilidad |
| **Parámetros performance degradan rendimiento** | Medio | Alto | Benchmarking + documentación recommended values |
| **OS detection falla en sistemas nuevos** | Alto | Bajo | Fallback manual + logging para debugging |
| **Modificaciones manuales introducen errores** | Medio | Alto | Validation functions + clear documentation |

## 12. Evidencias

### Referencias exactas
- **Sección Tesseract**: `config.ini:1-10` - Configuración paths multiplataforma OCR
- **Configuración BD**: `config.ini:12-20` - Settings SQLite connection y backup
- **Portal HUV params**: `config.ini:22-30` - URLs, timeouts, browser settings
- **Processing optimization**: `config.ini:32-43` - Parámetros performance y calidad
- **OS detection logic**: Referenciado en módulos que importan config
- **Fallback defaults**: Implementados en cada módulo consumidor

### Limitaciones del análisis
- **Contenido específico**: Valores reales dependen de instalación y entorno HUV
- **Completitud secciones**: Análisis asume estructura típica pero contenido puede variar
- **Integration patterns**: Forma exacta de uso depende de implementación específica cada módulo