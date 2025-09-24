# Resumen de Arquitectura - EVARISIS Gestor H.U.V (v3.5)

Este documento resume como esta organizado el proyecto, el flujo de datos y la relacion entre componentes en la version 3.5 (24/09/2025).

## Objetivo del sistema
- Extraer texto de informes PDF de patologia (enfoque IHQ) mediante OCR hibrido.
- Normalizar datos clinicos y biomarcadores usando reglas especificas del HUV.
- Persistir la informacion en una base SQLite unificada y habilitar analitica inmediata.
- Ofrecer una interfaz moderna TTKBootstrap con navegación floating para procesamiento, exploración y automatización web.

## Flujo de datos (alto nivel) - v3.5
1) El usuario ingresa al módulo Welcome de `ui.App(ttk.Window)` con navegación floating.
2) Navegación fluida: Menú flotante animado permite acceso rápido entre Welcome, Database, Dashboard, Visualización, Web Automation.
3) Por cada PDF seleccionado (módulo Database):
   - `ocr_processing.pdf_to_text_enhanced` intenta extraer texto nativo y aplica OCR con Tesseract (DPI configurable).
   - `procesador_ihq_biomarcadores` limpia el texto, segmenta informes (IHQ######) y obtiene datos base via funciones heredadas de `procesador_ihq`.
   - Se calculan biomarcadores clave (HER2, Ki-67, RE, RP, PD-L1, P16, estudios solicitados) con heuristicas robustas.
   - `database_manager.save_records` inserta filas normalizadas en la tabla `informes_ihq` evitando duplicados por numero de peticion.
4) El módulo Visualización lee la base con `database_manager.get_all_records_as_dataframe`, muestra la tabla y detalle contextual con UI mejorada.
5) El módulo Dashboard aplica filtros (fecha, servicio, malignidad, responsable), genera graficos con Matplotlib/Seaborn y navegación floating optimizada.
6) Opcionalmente, el módulo Web Automation lanza la automatizacion del portal (`huv_web_automation.automatizar_entrega_resultados`) para preparar nuevas descargas.

## Componentes principales - v3.5
- `huv_ocr_sistema_definitivo.py`: configura Tesseract y lanza `ui.App(ttk.Window)` con TTKBootstrap.
- `ui.py`: interfaz TTKBootstrap con navegación floating (Welcome, Database, Dashboard, Visualización, Web Automation) y coordinación de hilos. **CRECIMIENTO**: 1,299 → 3,121 líneas (+140%).
- `ocr_processing.py`: motor OCR hibrido con limpieza dedicada para tokens IHQ (sin cambios arquitectónicos).
- `procesador_ihq_biomarcadores.py`: extraccion especializada, normalizacion y escritura en SQLite (lógica preservada).
- `database_manager.py`: inicializa la base y expone operaciones CRUD (init_db, save_records, get_all_records_as_dataframe) (sin cambios).
- `huv_web_automation.py`: automatizacion Selenium para el portal institucional (integración con navegación floating).
- `calendario.py`: calendario modal con festivos para seleccionar fechas (compatibilidad TTKBootstrap).
- `huv_constants.py`: constante hospitalarias y patrones compartidos (sin modificaciones).
- `config.ini`: parametros OCR, rutas y ajustes heredados de UI clasica.

## Conexiones entre modulos
- `huv_ocr_sistema_definitivo` importa `App` y prepara el entorno Tesseract.
- `App` (ui.py) usa `procesador_ihq_biomarcadores` y `database_manager` para el pipeline, `Matplotlib` para graficos y `huv_web_automation` para Selenium.
- `procesador_ihq_biomarcadores` reusa utilidades de `procesador_ihq` (legacy) para campos base y complementa biomarcadores.
- `database_manager` depende de `sqlite3` y se invoca desde `ui` y `procesador_ihq_biomarcadores`.
- `calendario.CalendarioInteligente` se usa en la vista de automatizacion web.

## Entradas y salidas
- Entradas: PDFs IHQ, credenciales del portal (para automatizacion), configuracion Tesseract.
- Salidas: registros en `huv_oncologia.db`, logs de procesamiento, visualizaciones en dashboard y (opcional) consultas abiertas en el portal web.

## Consideraciones de calidad
- OCR: calidad depende de DPI y nitidez; el motor escala imagenes segun `MIN_WIDTH`.
- Biomarcadores: heuristicas toleran errores comunes de OCR, pero requieren revision ante nuevos formatos.
- Base de datos: los duplicados se bloquean por numero de peticion; conviene monitorear colisiones legitimas.
- UI: el procesamiento se ejecuta en hilos para no bloquear la interfaz; logs reflejan el avance.

## Proximos pasos sugeridos
- Incorporar plantillas de Biopsia/Autopsia al pipeline persistente.
- Habilitar exportacion incremental hacia Power BI y data warehouse.
- Fortalecer pruebas automatizadas (unitarias para regex y integracion para dashboards).
