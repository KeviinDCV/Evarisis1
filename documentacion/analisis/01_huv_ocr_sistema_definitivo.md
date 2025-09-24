# EVARISIS Gestor H.U.V — Análisis de Componente: huv_ocr_sistema_definitivo.py
**Ruta (relativa)**: `huv_ocr_sistema_definitivo.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Punto de entrada principal del sistema que configura el entorno OCR Tesseract y lanza la interfaz gráfica unificada.

## 2. Resumen técnico (5–8 líneas)

Este módulo actúa como bootstrap del sistema EVARISIS Gestor H.U.V. Su responsabilidad crítica es leer la configuración multi-plataforma de Tesseract OCR desde `config.ini`, establecer la ruta del ejecutable según el SO detectado, y transferir control a la interfaz CustomTkinter (`ui.App`). Es el único punto de entrada autorizado y garantiza que el entorno OCR esté correctamente inicializado antes de cualquier procesamiento. Sin este componente funcionando correctamente, toda la cadena de extracción de datos falla.

## 3. Estructura interna y flujo

### Puntos clave

* **`configure_tesseract()`**: Lee configuración multi-OS y establece `pytesseract.pytesseract.tesseract_cmd`
  * **Entradas**: Archivo `config.ini`, detección automática `sys.platform`
  * **Salidas**: Variable global pytesseract configurada, logs informativos/advertencia

* **`main()`**: Función principal de arranque
  * **Entradas**: None (argumentos CLI futuros)
  * **Salidas**: Lanzamiento `ui.App().mainloop()`, manejo de excepciones críticas

### Flujo principal

1. **Detección de plataforma**: `sys.platform.startswith()` para Windows/macOS/Linux
2. **Lectura configuración**: `configparser.ConfigParser()` lee `config.ini` con encoding UTF-8
3. **Extracción ruta Tesseract**: Sección `[PATHS]` según SO detectado
4. **Validación existencia**: `Path(tesseract_cmd).exists()` antes de configurar
5. **Configuración pytesseract**: Asignación a `pytesseract.pytesseract.tesseract_cmd`
6. **Lanzamiento UI**: Instanciación y `mainloop()` de `ui.App`
7. **Manejo de excepciones**: Try-catch global con logging de errores críticos

### CLI

No implementado en v2.5. Estructura preparada para argumentos futuros desde EVARISIS Dashboard.

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | `config.ini` | INI (UTF-8) | `configparser` | Una vez al arranque |
| **Entrada** | Detección SO | `sys.platform` | Lógica condicional | Una vez al arranque |
| **Salida** | Configuración pytesseract | Variable global | Todo el pipeline OCR | Persistente en sesión |
| **Salida** | Logs configuración | stdout/stderr | Usuario/debugging | Una vez al arranque |
| **Salida** | Transferencia control | Objeto UI | `ui.App.mainloop()` | Una vez al arranque |

## 5. Dependencias e interacciones

### Internas
- **→ `ui.py`**: Importa clase `App` y transfiere control total
- **→ `config.ini`**: Lee configuración crítica de rutas Tesseract
- **← Ninguna**: Es el punto de entrada, no es invocado por otros módulos

### Externas
- **`configparser`**: Parsing de archivo INI con interpolación desactivada
- **`pytesseract`**: Configuración global del comando ejecutable
- **`pathlib.Path`**: Validación de existencia de rutas de sistema
- **`sys`**: Detección de plataforma para configuración multi-OS

### Contrato con EVARISIS Dashboard
- **Invocación**: `python huv_ocr_sistema_definitivo.py` (CLI simple)
- **Argumentos esperados**: Ninguno en v2.5 (preparado para extensión)
- **Estado retorno**: Exit code 0 (éxito) o excepción no capturada (fallo crítico)

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Configuración faltante**: `config.ini` no encontrado o corrupto
- **Tesseract inaccesible**: Ruta inválida o permisos insuficientes
- **Fallo UI crítico**: Excepción no capturada en `ui.App`

### Estrategias de manejo
- **Graceful degradation**: Advierte sobre Tesseract faltante pero continúa con PATH del sistema
- **Logging informativo**: Imprime estado de configuración para debugging
- **Propagación controlada**: Permite que excepciones de UI se propaguen al usuario final
- **Fallback PATH**: Si configuración falla, intenta usar Tesseract del PATH del sistema

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Rutas del sistema**: Expone estructura de directorios en logs (información sensible menor)
- **Configuración**: `config.ini` podría contener rutas críticas del sistema

### Buenas prácticas presentes
- **Encoding explícito**: UTF-8 especificado para evitar problemas de caracteres
- **Validación de rutas**: Verifica existencia antes de configurar
- **Manejo de excepciones**: Evita crash silencioso

### Deudas de seguridad
- **Sin validación de permisos**: No verifica si Tesseract es ejecutable
- **Logs potencialmente verbosos**: Imprime rutas completas del sistema
- **Sin sanitización**: No valida contenido de config.ini contra inyecciones

## 8. Rendimiento y complejidad

### Operaciones costosas
- **I/O configuración**: Lectura de `config.ini` (operación única, impacto mínimo)
- **Validación de rutas**: `Path.exists()` (operación única de filesystem)

### Complejidad
- **Temporal**: O(1) - Operaciones constantes de inicialización
- **Espacial**: O(1) - Sin almacenamiento de datos significativo

### Oportunidades de optimización
- **Ninguna crítica**: Es un bootstrap de ejecución única
- **Posible mejora**: Cache de configuración para reinicializaciones (no aplicable en v2.5)

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Argumentos CLI**: Estructura preparada en `main()` para recibir argumentos del Dashboard
- **Configuración adicional**: Sección `[PATHS]` extensible para otras herramientas
- **Logging estructurado**: Migrar de `print()` a módulo `logging` estándar
- **Validaciones adicionales**: Verificar versión de Tesseract, permisos, etc.

### Acoplamientos a reducir
- **Dependencia directa ui.App**: Podría inyectarse vía factory pattern
- **Configuración hardcoded**: Ruta `config.ini` fija, podría ser parameterizable
- **Plataforma hardcoded**: Lógica de detección de OS podría externalizarse

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_configure_tesseract_windows_valid_path():
    # config.ini con ruta válida Windows, verificar pytesseract.tesseract_cmd
    
def test_configure_tesseract_fallback_path():
    # config.ini sin ruta, verificar advertencia y funcionamiento PATH

def test_main_launches_ui():
    # Mock ui.App, verificar instanciación y mainloop
```

### Bordes
```python
def test_configure_tesseract_missing_config():
    # config.ini inexistente, verificar manejo de excepción
    
def test_configure_tesseract_invalid_path():
    # Ruta Tesseract inválida, verificar advertencia y continuación

def test_main_ui_exception():
    # ui.App lanza excepción, verificar propagación
```

### Doubles y fixtures
- **Mock `configparser.ConfigParser`**: Para simular diferentes configuraciones
- **Mock `ui.App`**: Para aislar pruebas del bootstrap de UI
- **Fixture `config.ini`**: Archivos de configuración de prueba por SO

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Tesseract no instalado** | Crítico | Medio | Advertencia informativa, fallback a PATH del sistema |
| **config.ini corrupto** | Alto | Bajo | Manejo de excepciones con logging, continuación con valores por defecto |
| **Permisos de ejecución** | Alto | Bajo | Path.exists() valida accesibilidad básica |
| **Incompatibilidad SO** | Medio | Bajo | Detección multi-plataforma con fallback genérico Linux |
| **Fallo crítico UI** | Alto | Muy bajo | Propagación de excepción permite diagnóstico al usuario |

## 12. Evidencias

### Referencias exactas
- **Configuración Tesseract**: `huv_ocr_sistema_definitivo.py:23-41` - Función `configure_tesseract()` completa
- **Detección multi-OS**: `huv_ocr_sistema_definitivo.py:30-37` - Lógica condicional por plataforma  
- **Validación de rutas**: `huv_ocr_sistema_definitivo.py:38-44` - `Path(tesseract_cmd).exists()`
- **Punto de entrada**: `huv_ocr_sistema_definitivo.py:62-69` - Función `main()` con lanzamiento UI
- **Manejo de configuración**: `huv_ocr_sistema_definitivo.py:24-29` - ConfigParser con encoding UTF-8

### Limitaciones del análisis
- **Argumentos CLI futuros**: Código preparado pero sin implementación activa
- **Logging estructurado**: Usa `print()` en lugar de módulo logging estándar
- **Configuración dinámica**: Actualmente limitada a rutas Tesseract únicamente