# EVARISIS Gestor H.U.V — Reporte de Navegación para ChatGPT
**Versión:** v2.5 — **Fecha:** 22 de septiembre de 2025  
**Ruta raíz (Drive):** DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA

> Este reporte es un mapa navegable del proyecto para agentes de IA con acceso a Google Drive.  
> Todas las rutas son absolutas (prefijo `DEBERES HUV/`).

---

## 1. Estructura de Carpetas y Rutas Clave
Tabla de directorios principales (máximo nivel + subniveles relevantes).

| Carpeta (Drive) | Propósito | Observaciones |
|---|---|---|
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion | Destino de toda la documentación generada | Incluye `analisis/` y `comunicados/` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/analisis | Análisis técnico modular detallado | 10 componentes críticos documentados |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/comunicados | Plantillas para NotebookLM y IA externa | 28 plantillas especializadas por audiencia |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/pdfs_patologia | PDFs de entrada para procesamiento OCR | Informes médicos HUV reales |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/EXCEL | Archivos de salida y debug OCR | Resultados procesamiento y logs debug |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/GPT | Prompts SYSTEMPROMPT para documentación | 5 prompts especializados para análisis |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/scripts | Scripts auxiliares y utilidades | Herramientas apoyo desarrollo |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/venv0 | Entorno virtual Python | Dependencias aisladas del sistema |

---

## 2. Componentes y Responsabilidades (Mapa de Módulos)
Archivos **clave** (código, config, esquemas). Un ítem por archivo.

| Archivo (Drive) | Tipo | Rol principal (1–2 líneas) | Punto(s) de evidencia |
|---|---|---|---|
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_ocr_sistema_definitivo.py | Código (Entry Point) | Punto entrada principal: configura Tesseract OCR y lanza UI | `huv_ocr_sistema_definitivo.py:12-25` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/ui.py | Código (UI/Orquestación) | Interfaz CustomTkinter con 4 tabs: procesamiento, visualización, dashboard, automatización | `ui.py:45-1299` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/ocr_processing.py | Código (OCR Engine) | Motor OCR híbrido PyMuPDF+Tesseract con limpieza médica | `ocr_processing.py:25-117` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/procesador_ihq_biomarcadores.py | Código (Extracción) | Extractor especializado biomarcadores HER2/Ki-67/RE/RP/PD-L1 con segmentación multi-informe | `procesador_ihq_biomarcadores.py:1-369` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/database_manager.py | Código (Persistencia) | Gestor SQLite con esquema 167 campos médicos, control duplicados transaccional | `database_manager.py:8-86` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_web_automation.py | Código (Automatización) | Bot Selenium para portal HUV: login, navegación, descarga PDFs automática | `huv_web_automation.py:15-200` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/calendario.py | Código (Scheduling) | Planificador tareas automatizadas con threading background para operaciones periódicas | `calendario.py:15-175` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_constants.py | Código (Vocabulario) | Constantes médicas centralizadas: biomarcadores, regex, servicios, códigos diagnóstico | `huv_constants.py:15-250` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/test_sistema.py | Código (Testing) | Suite pruebas automatizadas con fixtures médicas, validación precisión biomarcadores | `test_sistema.py:45-580` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/config.ini | Configuración | Configuración multiplataforma: paths Tesseract, BD, portal HUV, parámetros OCR | `[TESSERACT]`, `[DATABASE]`, `[PORTAL_HUV]` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_oncologia.db | Base Datos | SQLite con tabla `informes_ihq` (167 campos), datos estructurados biomarcadores | Esquema en `database_manager.py:10-25` |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/analisis/[01-10]_*.md | Documentación técnica | Análisis evidence-based por componente: 12 secciones, referencias exactas archivo:línea | `documentacion/analisis/README.md` |

> **Nota:** El detalle fino por componente está en `documentacion/analisis/`.

---

## 3. Flujos / Pipelines (entrada → pasos → salida)
Describe los procesos principales, con rutas y contratos.

### Flujo: Procesamiento PDF Individual
- **Entrada(s):** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/pdfs_patologia/*.pdf` (informes patología HUV)
- **Pasos (resumen):** 1) OCR híbrido PyMuPDF/Tesseract 2) Limpieza texto médico 3) Segmentación multi-informe 4) Extracción biomarcadores 5) Normalización valores 6) Inserción SQLite con control duplicados
- **Salida(s):** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_oncologia.db` (registros estructurados), `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/EXCEL/*.xlsx` (reportes)
- **Componentes implicados:** `ocr_processing.py`, `procesador_ihq_biomarcadores.py`, `database_manager.py`, `ui.py`
- **Validaciones/contratos:** PDF válido, número petición único, biomarcadores en rangos clínicos, precisión OCR >60%

### Flujo: Automatización Portal HUV
- **Entrada(s):** Credenciales usuario, criterios filtro (fechas, tipos informe)
- **Pasos (resumen):** 1) Setup WebDriver Selenium 2) Login portal huvpatologia.qhorte.com 3) Navegación sección patología 4) Aplicación filtros 5) Descarga masiva PDFs 6) Procesamiento automático pipeline OCR
- **Salida(s):** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/pdfs_patologia/*.pdf` (nuevos), registros BD actualizados
- **Componentes implicados:** `huv_web_automation.py`, pipeline procesamiento completo
- **Validaciones/contratos:** Autenticación exitosa, elementos DOM encontrados, archivos descargados válidos

### Flujo: Dashboard Analítico Tiempo Real
- **Entrada(s):** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_oncologia.db` (registros existentes), filtros usuario
- **Pasos (resumen):** 1) Query SQLite con filtros 2) Cálculos estadísticos biomarcadores 3) Generación visualizaciones Matplotlib/Seaborn 4) Actualización UI thread-safe
- **Salida(s):** Dashboard interactivo con 8 tipos gráficos, métricas clínicas, exportaciones Excel
- **Componentes implicados:** `ui.py:create_dashboard_tab()`, `database_manager.py`
- **Validaciones/contratos:** DataFrames no vacíos, filtros válidos, memoria suficiente para visualizaciones

---

## 4. Integraciones Externas
Servicios, APIs, SDKs y su propósito.

| Integración | Para qué | Dónde se configura | Evidencia |
|---|---|---|---|
| Tesseract OCR | Extracción texto de PDFs escaneados con baja calidad | `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/config.ini` `[TESSERACT]` | `ocr_processing.py:45-80` |
| PyMuPDF (fitz) | Extracción texto nativo PDFs alta calidad, fallback engine | Dependencias requirements.txt | `ocr_processing.py:15-40` |
| Selenium WebDriver | Automatización portal HUV institucional para descarga PDFs | `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/config.ini` `[PORTAL_HUV]` | `huv_web_automation.py:15-200` |
| CustomTkinter | Framework UI moderna para interface desktop | Dependencias requirements.txt | `ui.py:1-50` |
| SQLite3 | Base datos embebida para persistencia información médica | `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/config.ini` `[DATABASE]` | `database_manager.py:5-15` |
| Matplotlib/Seaborn | Generación visualizaciones dashboard analítico | Dependencias requirements.txt | `ui.py:create_dashboard_tab()` |

---

## 5. Configuración y Seguridad (sin secretos)
Archivos que gobiernan la configuración; no expongas valores.

| Archivo (Drive) | Secciones/Claves críticas | Impacto | Notas de seguridad |
|---|---|---|---|
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/config.ini | `[TESSERACT] windows_path`, `[DATABASE] db_file`, `[PORTAL_HUV] base_url` | Configura engines OCR, persistencia, automatización web | Paths sistema expuestos, URLs portal institucional |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/huv_oncologia.db | Tabla `informes_ihq` con 167 campos médicos | Contiene información pacientes, biomarcadores, diagnósticos | **CRÍTICO:** Datos médicos sin cifrado, requiere protección acceso |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/requirements.txt | Dependencias Python críticas | Versiones específicas OCR, UI, automatización | Validar integridad packages, vulnerabilidades conocidas |

---

## 6. Empaquetado y Despliegue
Cómo se empaqueta y se distribuye.

- **Empaquetado:** PyInstaller con especificación OCR_Medico.spec
- **Scripts de build:** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/crear_ejecutable.py` (generación .exe Windows)
- **Artefactos resultantes:** `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/dist/OCR_Medico.exe` (aplicación standalone)
- **Notas de compatibilidad:** Windows 10+, Tesseract OCR instalado, Chrome/ChromeDriver para automatización portal

---

## 7. Glosario Rápido de Archivos
Lista de referencia de alta velocidad.

| Archivo (Drive) | Descripción (1 línea) |
|---|---|
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/README.md | Visión técnica compacta: stack, dependencias, argumentos CLI |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/INFORME_GLOBAL_PROYECTO.md | Resumen ejecutivo: problema, solución, stakeholders, roadmap |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/INICIO_RAPIDO.md | Guía instalación rápida y primer uso |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/CHANGELOG.md | Historial versiones con versionamiento semántico |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/BITACORA_DE_ACERCAMIENTOS.md | Registro reuniones médicas con Dr. Bayona y stakeholders |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/analisis/README.md | Índice análisis modular: 10 componentes con 12 secciones cada uno |
| DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/NOTEBOOK_LM_CONSOLIDADO_TECNICO.md | Consolidado técnico completo para análisis IA externa |

---

## 8. Cómo usar este reporte con ChatGPT
- **Localización:** pide archivos por su **ruta absoluta** (copiar/pegar desde tablas).
- **Contexto:** usa este reporte como mapa maestro; para detalles finos, abre `analisis/` o el archivo de código indicado.
- **Cambios:** si agregas/renombras archivos en Drive, **actualiza este reporte** y el `CHANGELOG.md`.

### Comandos de navegación sugeridos:
- Para **visión general**: `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/INFORME_GLOBAL_PROYECTO.md`
- Para **detalles técnicos**: `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/analisis/[NN_componente].md`
- Para **arquitectura**: `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/README.md`
- Para **plantillas IA**: `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/comunicados/`
- Para **código fuente**: Archivos `.py` listados en sección 2

### Flujos de consulta típicos:
1. **Consulta médica**: Biomarcadores → `procesador_ihq_biomarcadores.py` + `analisis/04_procesador_ihq_biomarcadores.md`
2. **Consulta técnica**: Arquitectura → `README.md` + `analisis/02_ui.md` (orchestrator principal)
3. **Consulta deployment**: Instalación → `INICIO_RAPIDO.md` + `crear_ejecutable.py`
4. **Consulta evolutiva**: Historia → `CHANGELOG.md` + `BITACORA_DE_ACERCAMIENTOS.md`

---

## Apéndice A — Inventario mínimo de fuentes relacionadas
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/README.md`  
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/INFORME_GLOBAL_PROYECTO.md`  
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/analisis/` (10 archivos)  
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/CHANGELOG.md`  
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/BITACORA_DE_ACERCAMIENTOS.md`
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/comunicados/` (28 archivos plantillas)
- `DEBERES HUV/HUV_ONCOLOGIA/HUV_ONCOLOGIA/documentacion/NOTEBOOK_LM_CONSOLIDADO_TECNICO.md`

## Apéndice B — Métricas del Proyecto SYSTEMPROMPT
**Análisis SYSTEMPROMPT completado**: 22 septiembre 2025
- **Componentes analizados**: 10 módulos críticos
- **Documentos generados**: 45+ archivos (análisis + plantillas + consolidados)
- **Referencias code exactas**: 120+ archivo:línea para mantenibilidad
- **Audiencias cubiertas**: 4 (Médico oncológico, Desarrollo, Dirección, Investigadores)
- **Plantillas NotebookLM**: 28 especializadas por audiencia y formato
- **Cobertura funcional**: Entry point → UI → OCR → Processing → Database → Testing → Deployment
