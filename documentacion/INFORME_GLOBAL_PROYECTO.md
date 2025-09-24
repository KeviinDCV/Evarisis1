# EVARISIS Gestor H.U.V — Informe Global del Proyecto

**Versión**: v2.5 (15/09/2025)  
**Fecha de actualización documental**: 22/09/2025  
**Ruta raíz Drive**: `DEBERES HUV\HUV_ONCOLOGIA\HUV_ONCOLOGIA`

## Resumen ejecutivo

**EVARISIS Gestor H.U.V** es un módulo estratégico del ecosistema EVARISIS que digitaliza y estructuratransforma el flujo de análisis de informes patológicos del Hospital Universitario del Valle. La versión 2.5 consolida un pipeline completo de captura, análisis y persistencia que reduce significativamente los tiempos de transcripción manual, mejora la calidad de datos clínicos y habilita análisis predictivos para la toma de decisiones en oncología. El sistema procesatualmente ha procesado cientos de informes IHQ generando una base de datos confiable para investigación clínica, optimización de recursos y futuros modelos de inteligencia artificial aplicada a la medicina de precisión.

## Visión y objetivos

**Objetivo general**: Transformar informes de patología en información estructurada confiable para la gestión clínica, investigación y planeación hospitalaria del HUV.

### Objetivos específicos medibles

1. **Analitica institucional**: Reducir el tiempo de transcripción manual de informes IHQ en 85% mediante OCR híbrido y extracción automatizada
2. **Investigación clínica**: Mantener dataset curado de biomarcadores oncológicos con trazabilidad completa para estudios longitudinales 
3. **Optimización de recursos**: Generar KPIs operativos (volumen, tiempos, responsables) con actualización en tiempo real
4. **Automatización de procesos**: Eliminar hojas de cálculo intermedias y habilitar conectores directos con el portal institucional
5. **Fundación para IA**: Establecer dataset de calidad productiva para futuros modelos predictivos y asistentes clínicos

## Alcance actual (v2.5)

### Qué SÍ hace
- **OCR híbrido avanzado**: Extrae texto nativo de PDFs y aplica Tesseract OCR para documentos escaneados con configuración optimizada
- **Extracción especializada IHQ**: Procesa informes de Inmunohistoquímica con segmentación multi-informe y normalización de biomarcadores críticos (HER2, Ki-67, RE/RP, PD-L1, P16)
- **Persistencia inteligente**: Almacena datos en SQLite con esquema de 167 campos y control automático de duplicados por número de petición
- **Dashboard analítico integrado**: Visualizaciones dinámicas con filtros contextuales, KPIs en tiempo real y modo pantalla completa
- **Automatización portal web**: Bot Selenium para consultas automatizadas en `huvpatologia.qhorte.com` con calendario inteligente
- **Interfaz moderna**: UI CustomTkinter con navegación por pestañas, tema claro/oscuro y experiencia no-bloqueante

### Qué NO hace (límites actuales)
- **Procesamiento completo Biopsia/Autopsia**: Solo IHQ tiene extracción completa implementada
- **Validación médica automatizada**: No incluye verificación de exactitud de extracción por profesional de salud
- **Integración EHR**: Sin conectores directos con sistemas core hospitalarios (SERVINTE, HIS)
- **Respaldo automático**: Requiere estrategia manual de backup para la base de datos crítica

## Arquitectura de alto nivel

```
Portal HUV Patología
(huvpatologia.qhorte.com)
        │
        │ [Selenium Bot]
        ▼
┌─────────────────────────┐
│   EVARISIS Gestor HUV   │
├─────────────────────────┤
│ PDFs Patología (Input)  │ → OCR Híbrido → Extracción IHQ → SQLite DB
│                         │     (PyMuPDF +     (Biomarcadores   (huv_oncologia.db)
│ Credenciales Portal     │      Tesseract)     + Metadatos)         │
│                         │                                          │
│ Dashboard Analytics ←───┼──────────────────────────────────────────┘
│ (Matplotlib/Seaborn)    │
│                         │
│ Exportaciones Excel     │
└─────────────────────────┘
        │
        ▼
Investigación + Gestión Clínica
```

### Componentes principales e integraciones
- **Motor OCR**: `ocr_processing.py` con estrategia híbrida (texto nativo + Tesseract configurable)
- **Extractor especializado**: `procesador_ihq_biomarcadores.py` reutiliza lógica de `procesador_ihq.py` (LEGACY) 
- **Gestor de datos**: `database_manager.py` maneja SQLite con transacciones seguras
- **Interfaz unificada**: `ui.py` coordina todos los componentes en CustomTkinter
- **Automatización web**: `huv_web_automation.py` con ChromeDriver management automático

## Valor por audiencia

| Audiencia | Foco principal | Beneficio/Resultado clave |
|-----------|----------------|---------------------------|
| **Equipo médico oncológico** | Análisis clínico y seguimiento biomarcadores | Dashboard inmediato con KPIs de HER2, Ki-67, RE/RP para toma decisiones terapéuticas |
| **Equipo de desarrollo** | Mantenimiento y evolución técnica | Arquitectura modular, documentación completa y versionamiento semántico para iteraciones ágiles |
| **Dirección hospitalaria** | Métricas operativas y ROI | Reducción 85% tiempo transcripción, optimización recursos y base para decisiones estratégicas |
| **Investigadores clínicos** | Dataset curado y trazabilidad | Base datos estructurada con 167 campos para estudios longitudinales y publicaciones científicas |

## Gobernanza del proyecto

### Stakeholders y responsabilidades

| Nombre | Rol | Responsabilidad |
|--------|-----|----------------|
| **Dr. Juan Camilo Bayona** | Líder médico e investigador principal | Validación clínica, requerimientos funcionales, casos de uso oncológicos |
| **Ing. Daniel Restrepo** | Desarrollador principal | Arquitectura técnica, implementación, control de calidad del código |
| **Ing. Diego Peña** | Jefe de Gestión de la Información | Gobernanza datos, integración sistemas hospitalarios, alineación estratégica |

### Ciclo de desarrollo
- **Versionamiento**: Semantic Versioning (SemVer) - Mayor.Menor.Parche
- **Ventanas de entrega**: Iteraciones bimestrales con revisiones médicas intermedias
- **Criterio "done"**: Funcionalidad validada médicamente + documentación + pruebas + deploy exitoso

## Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Degradación calidad OCR** | Alto | Medio | DPI configurable, limpieza post-OCR, logs detallados para ajuste |
| **Cambios portal web HUV** | Alto | Medio | Selenium con selectores robustos, ChromeDriver automático, modo debug |
| **Corrupción base datos** | Crítico | Bajo | Control transaccional, duplicados bloqueados, respaldo manual documentado |
| **Dependencia Tesseract** | Medio | Bajo | Multi-OS support, instalación documentada, fallback a texto nativo |
| **Sobrecarga UI con datasets grandes** | Medio | Alto | Threading no-bloqueante, paginación implícita, filtros dinámicos |
| **Pérdida expertise médico clave** | Alto | Bajo | Documentación exhaustiva casos uso, validaciones automatizables |

## Métricas y trazabilidad

### Indicadores de rendimiento
- **Tiempo promedio procesamiento**: < 30 segundos/PDF IHQ 
- **Exactitud extracción biomarcadores**: > 95% (validación manual muestra)
- **Disponibilidad sistema**: > 99% (aplicación desktop local)
- **Satisfacción usuario final**: Evaluación trimestral equipo oncología

### Registros y auditoría
- **Logs procesamiento**: Timestamps detallados por lote en `ui.py`
- **Bitácora médica**: `BITACORA_DE_ACERCAMIENTOS.md` con validaciones Dr. Bayona
- **Control versiones**: `CHANGELOG.md` con formato estándar Keep a Changelog
- **Métricas EVARISIS**: Integración futura con dashboard central del ecosistema

## Próximos hitos (roadmap)

### Fase 4 — Integración SERVINTE (Q1 2026)
- **Prioridad**: Alta - Conector API/CSV con sistema core hospitalario
- **Entregables**: Modo dry-run, colas locales, sincronización bidireccional

### Fase 5 — Inteligencia aumentada (Q2 2026) 
- **Prioridad**: Alta - Modelos predictivos y asistente clínico
- **Entregables**: ML pipeline, validación médica automatizada, alertas inteligentes

### Extensión Biopsia/Autopsia (Q4 2025)
- **Prioridad**: Media - Completar cobertura tipos informe
- **Entregables**: Procesadores especializados, dashboard ampliado

### Integración Power BI (Q1 2026)
- **Prioridad**: Media - Conectores BI corporativo
- **Entregables**: API exportación, dashboards ejecutivos tiempo real

### Validación médica asistida (Q2 2026)
- **Prioridad**: Media - Reducir intervención manual
- **Entregables**: Workflows validación, alertas discrepancias, ML confidence scoring

**Estado actual**: Fase 3 completa (v2.5) - Centralización y visualización operativa
**Próximo milestone**: Inicio Fase 4 tras revisión integral con dirección hospitalaria
