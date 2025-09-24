# EVARISIS Gestor H.U.V — Análisis de Componente: procesador_ihq_biomarcadores.py
**Ruta (relativa)**: `procesador_ihq_biomarcadores.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Extractor especializado de biomarcadores IHQ que procesa informes de Inmunohistoquímica segmentando múltiples informes por PDF y normalizando biomarcadores críticos (HER2, Ki-67, RE/RP, PD-L1, P16) con persistencia automática en SQLite.

## 2. Resumen técnico (5–8 líneas)

Este procesador representa la evolución v2.5 del sistema, combinando la funcionalidad base del `procesador_ihq.py` (LEGACY) con capacidades avanzadas de segmentación multi-informe y normalización específica de biomarcadores oncológicos. Utiliza heurísticas robustas para tolerar errores OCR, segmenta automáticamente PDFs que contienen múltiples informes IHQ###### y extrae valores cuantitativos y cualitativos de marcadores críticos para análisis clínico. La integración directa con `database_manager` garantiza persistencia inmediata sin pasos manuales intermedios.

## 3. Estructura interna y flujo

### Puntos clave

* **`_iter_reports(full_text: str)`**: Segmentador inteligente de múltiples informes por PDF
  * **Entradas**: Texto completo extraído por OCR
  * **Salidas**: Generator de bloques de texto individuales por informe IHQ######

* **`_clean_token(t: str)`**: Normalización de tokens con correcciones OCR específicas
  * **Entradas**: Token crudo de "Estudios solicitados"
  * **Salidas**: Token normalizado con correcciones IHQ/P16/AE1-AE3/etc.

* **`extract_biomarcadores_ihq(texto: str)`**: Extractor principal de biomarcadores
  * **Entradas**: Texto de informe individual
  * **Salidas**: Dict con HER2, Ki-67, RE, RP, PD-L1, P16 (estado/porcentaje), estudios

* **`process_pdf_to_database(pdf_path: str)`**: Pipeline completo PDF → SQLite
  * **Entradas**: Ruta absoluta a archivo PDF IHQ
  * **Salidas**: Lista de registros insertados en base de datos, logs de procesamiento

### Flujo principal

1. **Extracción OCR**: Invoca `ocr_processing.pdf_to_text_enhanced()` para texto limpio
2. **Segmentación inteligente**: `_iter_reports()` identifica códigos IHQ###### y separa informes
3. **Por cada informe segmentado**:
   - **Extracción base**: Reutiliza `procesador_ihq.extract_data()` para campos estándar HUV
   - **Enriquecimiento biomarcadores**: `extract_biomarcadores_ihq()` añade marcadores especializados
   - **Normalización**: Limpieza específica de tokens médicos con tolerancia OCR
   - **Validación**: Verificar que registro tenga datos mínimos (número petición)
4. **Persistencia automática**: `database_manager.save_records()` inserta en SQLite con control duplicados
5. **Logging resultados**: Retorna count de registros procesados y guardados

### Segmentación multi-informe
- **Estrategia primaria**: Busca "peticion : IHQ######" en cualquier parte del texto
- **Fallback**: Primera aparición cruda de "IHQ######" para informes sin formato estándar
- **Anti-duplicación**: `set()` previene procesamiento repetido del mismo código
- **Ordenamiento**: Procesa informes en orden de aparición en el PDF

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | PDF IHQ | `*.pdf` | `ocr_processing` → `procesador_ihq` | Por archivo procesado |
| **Entrada** | Texto OCR | String multi-línea | Segmentación y extracción | Por PDF procesado |
| **Salida** | Registros SQLite | Dict estructurado | `database_manager.save_records()` | Por informe segmentado |
| **Salida** | Logs procesamiento | Lista de strings | UI para feedback usuario | Por lote procesado |
| **Salida** | Debug files | `DEBUG_OCR_OUTPUT_*.txt` | Debugging manual | Por PDF (opcional) |
| **Salida** | DataFrame | pandas.DataFrame | Retorno para análisis inmediato | Por lote procesado |

## 5. Dependencias e interacciones

### Internas
- **→ `ocr_processing.pdf_to_text_enhanced()`**: Extracción de texto híbrida
- **→ `procesador_ihq.extract_data()`**: Funcionalidad base de extracción HUV (LEGACY)
- **→ `database_manager.save_records()`**: Persistencia SQLite con control duplicados
- **← `ui.py`**: Invocado desde pipeline de procesamiento en thread separado

### Externas
- **`pandas`**: Construcción de DataFrames para análisis y debug
- **`pathlib`**: Manejo robusto de rutas de archivos
- **`re`**: Regex complejas para extracción de biomarcadores y segmentación
- **`datetime`**: Timestamps para trazabilidad de procesamiento

### Contrato con procesador base
- **Reutilización**: Hereda toda funcionalidad estándar de `procesador_ihq.py`
- **Extensión**: Añade campos especializados sin modificar esquema base
- **Compatibilidad**: Mantiene estructura de salida compatible con Excel legacy

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **PDF sin informes IHQ**: No se encuentran códigos IHQ###### válidos
- **OCR deficiente**: Texto extraído no contiene patrones reconocibles
- **Base de datos bloqueada**: SQLite no disponible para escritura
- **Datos incompletos**: Informe sin número de petición o datos críticos mínimos

### Estrategias de manejo
- **Segmentación defensiva**: Si no encuentra códigos IHQ, procesa texto completo como único informe
- **Validación por campos**: Rechaza registros sin número petición pero continúa con siguientes
- **Logging detallado**: Registra cada paso del procesamiento para debugging
- **Transacciones parciales**: `database_manager` maneja rollback por registro fallido
- **Tolerancia OCR**: Múltiples patrones regex para capturar variaciones de escritura

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Información de pacientes**: Nombres, identificaciones, datos clínicos completos
- **Resultados médicos**: Biomarcadores con implicaciones diagnósticas críticas
- **Archivos debug**: `DEBUG_OCR_OUTPUT_*.txt` contienen texto completo extraído

### Buenas prácticas presentes
- **No persistencia temporal**: Procesamiento en memoria únicamente
- **Control de duplicados**: Evita re-procesamiento de informes ya guardados
- **Logs estructurados**: Información de progreso sin exposición de datos médicos

### Deudas de seguridad
- **Archivos debug no cifrados**: Texto médico guardado en archivos planos
- **Sin sanitización de entrada**: No valida que PDFs sean legítimos
- **Logs potencialmente verbosos**: Pueden incluir fragmentos de datos de pacientes
- **Base datos sin cifrar**: SQLite almacena información médica sin protección

## 8. Rendimiento y complejidad

### Operaciones costosas
- **OCR por PDF**: Invocación completa de pipeline OCR (más costoso del flujo)
- **Regex complejas**: Múltiples patrones para cada biomarcador con lookaheads/lookbehinds
- **Segmentación de texto**: Análisis completo del texto para encontrar códigos IHQ
- **Normalización de tokens**: Limpieza exhaustiva de "Estudios solicitados"

### Complejidad
- **Temporal**: O(n*m*k) donde n=informes, m=biomarcadores, k=patrones regex por biomarcador
- **Espacial**: O(n) para almacenamiento de registros extraídos en memoria

### Oportunidades de optimización
- **Regex compiladas**: Pre-compilar patrones frecuentes para evitar re-parsing
- **Segmentación lazy**: Procesar informes bajo demanda en lugar de cargar todos
- **Cache de biomarcadores**: Evitar re-extracción si texto no cambia
- **Paralelización**: Procesar múltiples informes de un PDF en paralelo
- **Índices SQLite**: Optimizar queries de duplicados con índices apropiados

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevos biomarcadores**: Añadir patrones de extracción para marcadores adicionales
- **Tipos de informe**: Extender segmentación para Biopsia/Autopsia con códigos específicos
- **Normalización avanzada**: ML para corrección OCR más sofisticada
- **Validaciones médicas**: Reglas de negocio para detectar valores anómalos
- **Exportaciones**: Formatos adicionales más allá de SQLite

### Acoplamientos a reducir
- **Dependencia directa procesador_ihq**: Podría abstraerse vía interface común
- **Patrones hardcoded**: Regex de biomarcadores podrían externalizarse a configuración
- **Estructura SQLite fija**: Schema podría ser más flexible para nuevos campos
- **Lógica de segmentación específica**: Podría generalizarse para otros tipos de código

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_single_ihq_report_extraction():
    # PDF con un informe IHQ, verificar extracción completa biomarcadores
    
def test_multiple_ihq_reports_segmentation():
    # PDF con múltiples IHQ######, verificar segmentación correcta
    
def test_biomarcador_normalization():
    # Variaciones OCR de HER2/Ki-67/etc, verificar normalización
```

### Bordes
```python
def test_pdf_no_ihq_codes():
    # PDF sin códigos IHQ######, verificar procesamiento como único informe
    
def test_incomplete_biomarcador_data():
    # Informe con biomarcadores parciales, verificar manejo graceful
    
def test_ocr_quality_variations():
    # Diferentes calidades OCR, verificar tolerancia a errores
```

### Doubles y fixtures
- **Mock ocr_processing**: Para controlar calidad de texto extraído
- **Mock procesador_ihq**: Para aislar funcionalidad de biomarcadores
- **Mock database_manager**: Para pruebas sin dependencia SQLite
- **Fixture PDFs IHQ**: Archivos reales con diferentes características

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Cambios formato informes IHQ** | Crítico | Medio | Múltiples patrones regex + fallbacks de segmentación |
| **OCR degrada calidad biomarcadores** | Alto | Alto | Normalización exhaustiva + patrones tolerantes a errores |
| **Base datos corrupción durante lote** | Alto | Bajo | Transacciones por registro + rollback automático |
| **Segmentación incorrecta multi-informe** | Medio | Medio | Validación por número petición + logs detallados |
| **Memoria insuficiente con lotes grandes** | Medio | Bajo | Procesamiento streaming + liberación explícita objetos |
| **Regex performance degradation** | Bajo | Alto | Patrones optimizados + early termination conditions |

## 12. Evidencias

### Referencias exactas
- **Segmentación multi-informe**: `procesador_ihq_biomarcadores.py:35-65` - Función `_iter_reports()` completa
- **Normalización tokens**: `procesador_ihq_biomarcadores.py:67-95` - `_clean_token()` con correcciones OCR
- **Extracción biomarcadores**: `procesador_ihq_biomarcadores.py:150-250` - `extract_biomarcadores_ihq()` con patrones específicos
- **Pipeline completo**: `procesador_ihq_biomarcadores.py:300-369` - `process_pdf_to_database()` principal
- **Integración database**: `procesador_ihq_biomarcadores.py:340-350` - Llamada a `database_manager.save_records()`
- **Fallback segmentación**: `procesador_ihq_biomarcadores.py:45-55` - Estrategia dual petición/código crudo

### Limitaciones del análisis
- **Archivo extenso**: 369 líneas requieren análisis detallado por secciones específicas
- **Patrones regex complejos**: Algunos patrones requieren validación con datos reales
- **Dependencia LEGACY**: Funcionalidad heredada de `procesador_ihq.py` no completamente analizada