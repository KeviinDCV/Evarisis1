# Changelog

## [6.6.16] - 2026-05-04 — Diagnosis Categorization Sprint

**Sprint:** Refinamiento masivo del normalizador de diagnósticos (`core/normalizador_diagnosticos.py`) y un fix crítico de detección de malignidad en `core/extractors/medical_extractor.py`. El sprint cubre seis versiones consecutivas (V6.6.12 → V6.6.16) aplicadas como cambios quirúrgicos validados con auditoría cuantitativa sobre 188 casos del rango IHQ250001-200.

### Impact (cuantitativo)
| Métrica | Antes | Después | Mejora |
|---|---|---|---|
| Diagnósticos oncológicos categorizados | 62/100 (62.0%) | 161/188 (85.6%) | **+23.6 pts** |
| Casos problemáticos (OTRO + SIN DX) | 28/100 (28.0%) | 27/188 (14.4%) | **−13.6 pts** |
| Distribución MALIGNO/BENIGNO | 73/27 | 75/25 | sin desbalance |
| Regresiones detectadas | — | 0 | limpio |

### Files modified
- `core/normalizador_diagnosticos.py` — cambios mayores: typos del patólogo, 6 categorías nuevas/extendidas, stripping de preámbulos, reordenamientos de prioridad, ampliación de inferencia por órgano.
- `core/extractors/medical_extractor.py` (función `determine_malignancy`, líneas ~3641-3686) — nueva PRIORIDAD -2 que aísla negaciones explícitas en `Diagnostico Principal` para evitar contaminación por historia clínica.

### Changes by version

#### V6.6.12 — Typo del patólogo "CARICNOMA"
- `normalizar_texto()`: corregido typo "CARICNOMA" → "CARCINOMA" en preprocesamiento.
- **Caso piloto:** IHQ250060.
- **Impacto:** 1 caso recuperado (OTRO/NO CATEGORIZADO → CARCINOMA → refinado por órgano a OTRO CARCINOMA DE MAMA).

#### V6.6.13 — Categorías faltantes en el diccionario
- Agregadas 4 categorías nuevas: **TUMOR FILODES DE MAMA**, **CARCINOMA PAPILAR DE MAMA**, **NEOPLASIA DE CELULAS FUSIFORMES / FUSOCELULAR**, **LESION ESCAMOSA INTRAEPITELIAL / NIC**.
- Extendida **LINFOMA NO HODGKIN B** con patrones OMS 2022 ("NEOPLASIA DE CELULAS B MADURAS").
- **Casos piloto:** IHQ250071, IHQ250081, IHQ250066, IHQ250126, IHQ250107, IHQ250116.
- **Impacto:** 6 casos recuperados.

#### V6.6.14 — Stripping de preámbulos del patólogo + reordenamiento
- Nueva función `stripear_preambulos()` con 11 preámbulos típicos del patólogo del HUV (ej. "RESULTADO IHQ COMPATIBLE CON…").
- `categorizar_diagnostico()` modificada para invocar el stripping antes del matching.
- **Reordenamientos críticos** (resolver cortocircuitos contra patrones genéricos):
  - `ADENOCARCINOMA (SIN ORIGEN)` y `CARCINOMA (OTRO)` ANTES de `RESULTADO IHQ`.
  - `LEUCEMIA MIELOIDE` y `LEUCEMIA LINFOIDE AGUDA` ANTES de `LINFOMA (OTRO/INESPECIFICO)`.
- Nueva categoría: **CARCINOMA ANEXIAL CUTANEO**.
- **LINFOMA NO HODGKIN B** extendido con "ZONA MARGINAL".
- **LEUCEMIA LINFOIDE AGUDA** extendida con "LEUCEMIA/LINFOMA LINFOBLASTICO".
- **Casos piloto:** IHQ250026, IHQ250028, IHQ250041, IHQ250087, IHQ250091, IHQ250099, IHQ250105, IHQ250140, IHQ250147, IHQ250158, IHQ250164, IHQ250166, IHQ250174.
- **Impacto:** 15 casos recuperados (13 por preámbulos + 2 por sufijo SOBREEXPRESIÓN).

#### V6.6.14 (cont.) — Mini-fix RECTAL en INFERENCIA_POR_ORGANO_ADENO
- El patrón "RECTO" no matcheaba "RECTAL" como substring.
- **Caso piloto:** IHQ250159.
- **Impacto:** 1 caso recuperado.

#### V6.6.15 — Fix CRÍTICO Malignidad (PRIORIDAD -2 en `determine_malignancy`)
- **Problema:** la PRIORIDAD -1 evaluaba `combined_text = diagnostico + macroscopica + microscopica + full_text`. La historia clínica con "Historia de carcinoma de mama" disparaba MALIGNO aunque el dx final fuera benigno (ej. INFLAMACIÓN AGUDA SIN EVIDENCIA DE LESIÓN NEOPLÁSICA).
- **Solución:** nueva PRIORIDAD -2 que evalúa SOLO el `Diagnostico Principal` para negaciones explícitas. Si tiene negación y NO tiene también keyword maligno (caso multi-muestra), retorna BENIGNO.
- **Casos piloto:** IHQ250106 (target — crítico clínicamente), IHQ250065 (bonus).
- **Impacto:** 2 casos recuperados.

#### V6.6.16 — Mini-fixes basados en audit cuantitativo
- Typo "HISTOLOGIOS" → "HISTOLOGICOS" en `normalizar_texto` (caso IHQ250026 MELANOMA).
- Nueva categoría **INFLAMACION / PROCESO INFECCIOSO** (cubre IHQ250037 colitis, IHQ250075 peritonitis, IHQ250061 Hirschsprung).
- `INFERENCIA_POR_ORGANO_ESCAMO` ampliado con: LABIO, BOCA, FARINGE, HIPOFARINGE, NASOFARINGE, ESOFAGO, ANO, VULVA, VAGINA.
- **Impacto:** 4+ casos recuperados.

### Validation
- 75+ casos validados manualmente con resultados esperados (todos OK).
- 54 self-tests internos del normalizador (54/54 OK).
- 12 casos de regresión específicos para `determine_malignancy` (12/12 OK).
- Audit cuantitativo sobre 188 casos del período IHQ250001-200 (**0 regresiones**).

### Anti-regression notes (REGLA CRÍTICA #1)
Todos los cambios siguen el patrón "patrón específico nuevo ANTES + fallback genérico ORIGINAL preservado". Ningún patrón existente fue eliminado o sobrescrito; todas las extensiones se agregaron como ramas adicionales o reordenamientos de prioridad. Comentarios `V6.6.XX FIX IHQYYYYY` en el código documentan la trazabilidad caso-por-caso.

---

## [6.0.0] - 2025-10-20

### Changed
- Consolidación 19→6 archivos core
- 7 workflows maestros implementados
- version-manager gestiona CHANGELOG+BITÁCORA acumulativos
- documentation-specialist simplificado (solo lee CHANGELOG)
- 4 herramientas densas (4665 líneas)
- 5 agentes especializados (2066 líneas)

---

Changelog

Este proyecto sigue versionamiento semantico.

[Unreleased]
- **CONSOLIDACIÓN COMPLETA SYSTEMPROMPT**: Finalización protocolo análisis SYSTEMPROMPT con reporte navegación ChatGPT.
- **REPORTE_CHATGPT.md completo**: Mapa navegable proyecto con rutas absolutas Drive, componentes principales, flujos pipeline y comandos navegación.
- **28 Plantillas NotebookLM**: Contenido especializado para 4 audiencias (Médico oncológico, Desarrollo, Dirección, Investigadores) en formatos audio, video y cuestionarios.
- **Navegación IA Externa**: Estructura optimizada para ChatGPT con referencias exactas archivo:línea y flujos consulta típicos por dominio técnico/médico.
- Integracion completa de Biopsia/Autopsia al flujo persistente y dashboards.
- Sincronizacion incremental con Power BI y agendas clinicas.
- Hardening de pruebas automaticas de extraccion y visualizacion.

2025-09-22 — docs - SYSTEMPROMPT Analysis
- **DOCUMENTACIÓN TÉCNICA MODULAR COMPLETA**: Análisis exhaustivo de 10 componentes críticos del sistema siguiendo protocolo SYSTEMPROMPT con 12 secciones por componente.
- **Análisis técnico evidence-based**: Documentación con referencias exactas archivo:línea para cada componente del pipeline OCR.
- **Arquitectura médica especializada**: Documentación profunda del dominio oncológico HUV con vocabulario biomarcadores, patrones extracción y flujos clínicos.
- **Componentes analizados**: 
  - `01_huv_ocr_sistema_definitivo.md` - Entry point y configuración Tesseract
  - `02_ui.md` - Interfaz CustomTkinter 1299 líneas con 4 tabs especializados
  - `03_ocr_processing.md` - Engine OCR híbrido PyMuPDF/Tesseract con limpieza médica
  - `04_procesador_ihq_biomarcadores.md` - Extractor biomarcadores HER2/Ki-67/RE/RP/PD-L1 
  - `05_database_manager.md` - Gestor SQLite con esquema 167 campos transaccional
  - `06_huv_web_automation.md` - Automatización portal Selenium con error recovery
  - `07_calendario.md` - Scheduler interno tareas automatizadas con threading
  - `08_huv_constants.md` - Vocabulario médico centralizado y patrones regex
  - `09_config.ini.md` - Configuración multiplataforma con detección OS
  - `10_test_sistema.py.md` - Suite pruebas automatizadas con fixtures médicas
- **Gestión técnica**: Identificación riesgos médicos críticos, deuda técnica, puntos extensión y estrategias optimización por componente.
- **Cobertura completa**: Desde entry point hasta testing, incluyendo seguridad datos médicos, performance OCR y mantenibilidad arquitectura.
- **Documentación EVARISIS**: Actualización README.md, INFORME_GLOBAL_PROYECTO.md, INICIO_RAPIDO.md con nueva arquitectura v2.5.

2025-09-20 — docs
- Generado/actualizado `documentacion/REPORTE_CHATGPT.md` con el mapa del proyecto.
- Enlace agregado en `documentacion/README.md`.
 - Documentado `scripts/inspect_excel.py` en `documentacion/analisis/21_inspect_excel.md`.
 - Limpieza de binarios: movidos a `utilidades/binarios/` y `.gitignore` ampliado (EXCEL/, pdfs_patologia/, huv_oncologia.db, *.exe).
 - Ejecutable probado con PyInstaller (`dist/OCR_Medico.exe`).

2025-09-15 – v2.5.0
- Rediseno de la aplicacion de escritorio con CustomTkinter: navegacion por Procesar PDFs, Visualizar Datos, Dashboard Analitico y Automatizar BD Web.
- Canalizacion persistente: `procesador_ihq_biomarcadores` segmenta multiples informes por PDF, normaliza biomarcadores y guarda resultados en `huv_oncologia.db` mediante `database_manager`.
- Dashboard analitico integrado (Matplotlib/Seaborn) con filtros dinamicos, comparador parametrizado y modo pantalla completa.
- Automatizacion del portal `huvpatologia.qhorte.com` con Selenium (`huv_web_automation.py`) para consultas guiadas desde la aplicacion.
- Widget `CalendarioInteligente` (Babel + holidays) para seleccionar rangos de fecha con contexto de festivos.
- Documentacion actualizada para arquitectura 2.5 e incorporacion de analisis de `database_manager`, `huv_web_automation` y `calendario.py`.

2025-09-10 – v1.1.0
- Version estable v1.1 liberada.
- Nuevo analisis avanzado de IHQ accesible desde la UI (boton "Analizar Biomarcadores IHQ (v1.1)") que genera un Excel separado con HER2, Ki-67, RE/ER, RP/PR, PD-L1, P16 (estado/porcentaje) y "Estudios Solicitados".
- Documentacion actualizada: `INFORME_GLOBAL_PROYECTO.md`, `README.md`, `INICIO_RAPIDO.md` y bitacora.

2025-09-10
- Rebranding y reestructuracion documental al ecosistema "EVARISIS Gestor H.U.V".
- Creacion de `BITACORA_DE_ACERCAMIENTOS.md` y carpeta `comunicados/` (cinco artefactos).
- Ajustes de analisis: documentacion de extensiones IHQ y activos de datos.

2025-09-05 – v1.0.0
- Fundacion y validacion: motor OCR + app de escritorio.
- Procesadores especializados: Autopsia, IHQ, Biopsia, Revision.
- Exportacion validada a Excel (55 columnas) con formato profesional.

2025-08-20 – v0.1.0
- Inicio del desarrollo: estructura base, OCR y primeras reglas de extraccion.
