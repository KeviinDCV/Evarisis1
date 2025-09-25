# EVARISIS Gestor H.U.V — Informe Global del Proyecto

**Versión**: v2.5 (15/09/2025)  
**Fecha de actualización documental**: 22/09/2025  
**Ruta raíz Drive**: `DEBERES HUV\HUV_ONCOLOGIA\HUV_ONCOLOGIA`

## Resumen ejecutivo

**EVARISIS Gestor H.U.V** es un módulo estratégico del ecosistema EVARISIS diseñado para crear la **"Base de Datos de la Verdad"** de los datos oncológicos del Hospital Universitario del Valle. La versión 2.5 consolida un motor de inteligencia estratégica y clínica que transforma informes de patología (PDFs) en información estructurada de alta confiabilidad para la toma de decisiones estratégicas y la futura auditoría de sistemas hospitalarios, eliminando las discrepancias y baja confiabilidad de los datos ingresados manualmente en sistemas existentes como SERVINTE. El sistema ha procesado cientos de informes IHQ generando una base de datos autoritativa que habilita análisis avanzados para identificar patrones de riesgo, determinar órganos y patologías más recurrentes, estimar costos de tratamiento por paciente y tipo de cáncer, y proveer a la gerencia hospitalaria datos sólidos para crear estrategias comerciales con farmacéuticas y optimizar la asignación de recursos.

## Visión y objetivos

**Objetivo general**: Transformar informes de patología (IHQ y Biopsias) en una base de datos de alta confiabilidad ("la fuente de la verdad") que habilite el análisis clínico-estratégico y sirva como fundamento para la futura auditoría y corrección de los sistemas de información del HUV.

### Objetivos específicos medibles

1. **Analitica institucional**: Reducir el tiempo de transcripción manual de informes IHQ en 85% mediante OCR híbrido y extracción automatizada
2. **Investigación clínica**: Mantener dataset curado de biomarcadores oncológicos con trazabilidad completa para estudios longitudinales 
3. **Optimización de recursos**: Generar KPIs operativos (volumen, tiempos, responsables) con actualización en tiempo real
4. **Automatización de procesos**: Eliminar la interpretación manual y las hojas de cálculo intermedias, estableciendo una fuente única de verdad que reemplace datos ingresados manualmente
5. **Fundación para IA**: Establecer dataset de calidad productiva que sirva como base para el futuro desarrollo de un Auditor IA (Fase 4) capaz de mantener proactivamente la integridad de datos oncológicos

## Alcance actual (v2.5)

### Qué SÍ hace
- **OCR híbrido avanzado**: Extrae texto nativo de PDFs y aplica Tesseract OCR para documentos escaneados con configuración optimizada
- **Extracción especializada IHQ (Fase 0)**: Procesa informes de Inmunohistoquímica con segmentación multi-informe y normalización de biomarcadores críticos (HER2, Ki-67, RE/RP, PD-L1, P16), estableciendo la base de la plataforma
- **Persistencia inteligente**: Almacena datos en SQLite con esquema de 167 campos y control automático de duplicados por número de petición
- **Dashboard analítico integrado**: Visualizaciones dinámicas con filtros contextuales, KPIs en tiempo real y modo pantalla completa
- **Automatización portal web**: Bot Selenium para consultas automatizadas en `huvpatologia.qhorte.com` con calendario inteligente
- **Interfaz moderna**: UI CustomTkinter con navegación por pestañas, tema claro/oscuro y experiencia no-bloqueante

### Qué NO hace (límites actuales)
- **Soporte completo para Patologías (Biopsias)**: El procesamiento de Autopsias está fuera del alcance actual y de los planes a corto-mediano plazo
- **Validación médica automatizada**: No incluye verificación de exactitud de extracción por profesional de salud
- **No realiza una integración de escritura directa con SERVINTE**: El sistema está diseñado para una futura interoperabilidad de auditoría
- **Análisis estadístico avanzado**: Corresponde a la implementación de la Fase 2 (Motor Analítico)

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

**Estado actual**: Fase 0 completa (v2.5) - Plataforma base y extracción inicial de IHQ
**Próximo milestone (Q4 2025)**: Completar Fases 1 y 2

### Fase 1 — Maestría en Extracción (Q4 2025)
- **Objetivo**: Perfeccionar la extracción de IHQ a un nivel de precisión clínica (>98%) y desarrollar el módulo completo para la extracción de Patologías (Biopsias)
- **Entregables**: 
  - Motor de extracción IHQ optimizado con precisión clínica
  - Procesador completo para informes de Biopsias
  - Validación exhaustiva de biomarcadores críticos

### Fase 2 — Motor Analítico (Q4 2025)
- **Objetivo**: Con los datos perfectos de la Fase 1, construir un dashboard avanzado con gráficas y estadísticas complejas que respondan a las preguntas estratégicas y clínicas del Dr. Bayona
- **Entregables**:
  - Dashboard analítico avanzado con estadísticas complejas
  - Análisis de patrones de riesgo en pacientes
  - Cálculos de costos de tratamiento por tipo de cáncer
  - KPIs estratégicos para la gerencia hospitalaria

### Fase 3 — Interoperabilidad de Auditoría (Post-Q4 2025)
- **Objetivo**: Migrar la "Base de Datos de la Verdad" a SERVINTE, no como una simple integración, sino como una fuente de datos autoritativa para corregir la información existente
- **Entregables**:
  - Sistema de cross-referencia con SERVINTE
  - Herramientas de auditoría y corrección de datos
  - Protocolos de migración de datos autoritativos

### Fase 4 — Auditor IA (Visión Futura)
- **Objetivo**: Desarrollar una IA entrenada con la base de conocimientos del proyecto para auditar y mantener de forma proactiva la integridad de los datos oncológicos en SERVINTE
- **Entregables**:
  - Modelo de IA especializado en auditoría de datos oncológicos
  - Sistema de mantenimiento proactivo de integridad
  - Alertas inteligentes de discrepancias y anomalías
