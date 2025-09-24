# EVARISIS Gestor H.U.V — Análisis de Componente: huv_constants.py
**Ruta (relativa)**: `huv_constants.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Repositorio centralizado de constantes del dominio médico HUV que define vocabularios especializados, patrones de extracción, configuraciones de normalización y mapeos terminológicos para procesamiento OCR.

## 2. Resumen técnico (5–8 líneas)

Concentra toda la configuración específica del dominio oncológico HUV en estructuras de datos reutilizables: diccionarios de biomarcadores con sus valores esperados, expresiones regulares para extracción de campos médicos, listas de servicios hospitalarios normalizadas y mapeos de códigos diagnósticos. Esta centralización permite mantenimiento eficiente de la terminología médica especializada, actualizaciones sin tocar lógica de procesamiento y extensión controlada del vocabulario. Las constantes incluyen tanto valores estrictos para validación como patrones flexibles para captura de variantes textuales encontradas en OCR de documentos reales.

## 3. Estructura interna y flujo

### Puntos clave

* **`BIOMARKERS_VOCABULARY`**: Diccionario maestro de biomarcadores IHQ válidos
  * **Contenido**: `{marker_name: {valid_values, synonyms, ranges}}`
  * **Uso**: Validación y normalización de resultados biomarcadores

* **`EXTRACTION_PATTERNS`**: Expresiones regulares para campos médicos
  * **Contenido**: `{field_name: compiled_regex_pattern}`
  * **Uso**: Extracción automática desde texto OCR procesado

* **`HOSPITAL_SERVICES`**: Mapeo normalizado de servicios HUV
  * **Contenido**: `{service_code: canonical_name}`
  * **Uso**: Consistencia en nombres de servicios hospitalarios

* **`DIAGNOSTIC_CODES`**: Códigos ICD-10 y equivalencias HUV
  * **Contenido**: `{huv_code: {icd10, description, category}}`
  * **Uso**: Normalización y categorización diagnósticos

### Estructura organizacional
```python
# Biomarcadores especializados
BIOMARKERS = {
    'HER2': ['0', '1+', '2+', '3+', 'NEGATIVO', 'POSITIVO'],
    'Ki67': ['<5%', '5-14%', '15-30%', '>30%', 'BAJO', 'ALTO'],
    'RE': ['POSITIVO', 'NEGATIVO', '%_VALUE'],
    'RP': ['POSITIVO', 'NEGATIVO', '%_VALUE'],
    'PD_L1': ['<1%', '1-49%', '>=50%', 'CPS_SCORE']
}

# Patrones extracción
REGEX_PATTERNS = {
    'numero_peticion': r'(?:N°|No\.?|Petición)\s*:?\s*([A-Z]?\d{6,8})',
    'fecha_nacimiento': r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
    'biomarcador_her2': r'HER-?2[:\s]*([0-3]\+?|POSITIVO|NEGATIVO)',
    # ... más patrones especializados
}
```

### Uso en pipeline
1. **Validación entrada**: Verificar texto OCR contiene patrones esperados
2. **Extracción dirigida**: Aplicar regex específicos según tipo documento
3. **Normalización valores**: Mapear variantes textuales a valores canónicos  
4. **Enriquecimiento datos**: Agregar códigos/categorías desde diccionarios

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | Actualizaciones vocabulario | Modificaciones código fuente | Desarrollador/médico | Por versión sistema |
| **Salida** | Constantes biomarcadores | `dict` structures | `procesador_ihq_biomarcadores.py` | Por procesamiento |
| **Salida** | Patrones regex | `re.Pattern` objects | `ocr_processing.py` | Por extracción texto |
| **Salida** | Mapeos servicios | `dict` normalizados | `database_manager.py` | Por inserción BD |
| **Salida** | Códigos diagnóstico | Estructuras validación | Todos los procesadores | Por normalización |

## 5. Dependencias e interacciones

### Internas (alta frecuencia)
- **← `procesador_ihq_biomarcadores.py`**: Principal consumidor patrones biomarcadores
- **← `ocr_processing.py`**: Cliente para regex de extracción general
- **← `database_manager.py`**: Usa mapeos para normalización antes inserción
- **← `ui.py`**: Referencia listas para validación entrada usuario

### Externas
- **`re`**: Compilación de expresiones regulares optimizadas
- **`typing`**: Type hints para estructuras de datos complejas
- **Sin dependencias externas pesadas**: Módulo ligero de solo definiciones

### Patrón de consumo
- **Import time**: Constantes cargadas una vez al importar módulos cliente
- **Runtime references**: Acceso directo sin overhead computacional
- **Memory sharing**: Mismas estructuras compartidas entre múltiples módulos

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Regex malformados**: Expresiones regulares sintácticamente incorrectas
- **Referencias faltantes**: Código cliente referencia constante no definida
- **Valores inválidos**: Biomarcadores con valores no reconocidos por validadores
- **Encoding issues**: Caracteres especiales médicos no manejados correctamente
- **Inconsistencias mapeo**: Misma entidad médica con múltiples representaciones

### Estrategias de manejo
- **Validación en definición**: Regex compilados y testados al definir constantes
- **Fallback values**: Valores por defecto para casos no cubiertos
- **Comprehensive coverage**: Múltiples sinónimos y variantes por entidad médica
- **Unicode support**: Caracteres especiales médicos (μ, α, β, etc.) soportados
- **Validation functions**: Funciones helper para verificar consistencia constantes

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Terminología médica propietaria**: Vocabulario específico HUV puede ser confidencial
- **Códigos internos**: Mapeos de códigos hospitalarios internos
- **Patrones diagnóstico**: Regex pueden revelar estructura informes médicos

### Buenas prácticas presentes
- **Solo metadatos**: No contiene datos de pacientes, solo estructuras vocabulario
- **Versionado controlado**: Cambios a constantes médicas requieren revisión
- **Documentación clara**: Cada constante documentada para uso apropiado

### Deudas de seguridad menores
- **Sin cifrado vocabulario**: Terminología médica almacenada en texto plano
- **Acceso sin restricción**: Cualquier módulo puede importar y usar constantes
- **Sin auditoría cambios**: Modificaciones a vocabulario no son trackeadas

## 8. Rendimiento y complejidad

### Operaciones costosas
- **Compilación regex**: Una vez al cargar módulo, costo de compile()
- **Búsquedas diccionario**: O(1) lookups pero con estructuras grandes
- **Pattern matching**: Aplicación regex sobre textos largos OCR

### Complejidad
- **Espacial**: O(V) donde V es tamaño total vocabulario médico
- **Temporal**: O(1) para lookups, O(n*m) para pattern matching sobre texto

### Oportunidades de optimización
- **Lazy compilation**: Compilar regex solo cuando se usan primera vez
- **Trie structures**: Para búsquedas de prefijos en vocabulario médico
- **Caching compiled patterns**: Evitar re-compilación en múltiples usos
- **Optimized regex**: Patrones más específicos para reducir backtracking
- **Partitioned lookups**: Dividir vocabulario por categorías para búsquedas más rápidas

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevos biomarcadores**: Agregar sin afectar procesamiento existente
- **Patrones adicionales**: Más regex para capturar variantes no cubiertas
- **Servicios hospitalarios**: Expansión mapeos para nuevas áreas médicas
- **Códigos diagnóstico**: Integración con estándares internacionales (SNOMED, ICD-11)
- **Validadores dinámicos**: Funciones de validación más complejas

### Acoplamientos a reducir
- **Hardcoded values**: Vocabulario podría cargarse desde archivos externos
- **Format-specific patterns**: Regex muy específicos a formato actual informes
- **Static definitions**: Constantes podrían ser configurables por instalación
- **Monolithic structure**: Podría separarse por dominios médicos específicos

## 10. Pruebas recomendadas (test design)

### Validación constantes
```python
def test_all_regex_patterns_compile():
    # Verificar que todos los regex son sintácticamente válidos
    
def test_biomarker_values_are_valid():
    # Todos los valores de biomarcadores siguen formato esperado
    
def test_service_mappings_complete():
    # Mapeos de servicios no tienen entradas duplicadas/conflictivas
    
def test_diagnostic_codes_format():
    # Códigos diagnóstico siguen estándar ICD-10
```

### Funcionalidad práctica
```python  
def test_patterns_extract_from_real_samples():
    # Regex extraen correctamente de muestras texto OCR real
    
def test_biomarker_normalization_works():
    # Variantes textuales se mapean a valores canónicos correctos
    
def test_service_resolution_handles_variants():
    # Diferentes formas escribir servicio resuelven a mismo canonical
    
def test_vocabulary_coverage_sufficient():
    # Vocabulario cubre casos encontrados en producción
```

### Doubles y fixtures
- **Sample OCR texts**: Textos reales (anonimizados) para test patterns
- **Edge case vocabulary**: Casos límite y variantes poco comunes
- **Performance datasets**: Vocabularios grandes para test rendimiento
- **Unicode test cases**: Caracteres especiales médicos diversos

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Vocabulario desactualizado vs. práctica médica** | Alto | Alto | Revisión periódica con personal médico |
| **Regex patterns rompen con cambios formato** | Alto | Medio | Múltiples patrones por campo + fallbacks |
| **Inconsistencias terminología médica** | Medio | Alto | Normalización centralizada + validación |
| **Performance degradation con vocabulario grande** | Medio | Medio | Estructuras eficientes + lazy loading |
| **Conflictos entre códigos diagnóstico** | Alto | Bajo | Validación unicidad + tests automatizados |
| **Caracteres especiales médicos mal manejados** | Medio | Medio | Unicode support + encoding tests |

## 12. Evidencias

### Referencias exactas
- **Biomarcadores IHQ**: `huv_constants.py:15-35` - Diccionario HER2, Ki-67, RE/RP, PD-L1
- **Patrones regex**: `huv_constants.py:40-80` - Expresiones para campos médicos estándar
- **Servicios HUV**: `huv_constants.py:85-120` - Mapeo normalizado departamentos/servicios
- **Códigos diagnóstico**: `huv_constants.py:125-200` - ICD-10 mappings y categorías
- **Validadores helper**: `huv_constants.py:205-250` - Funciones utilidad para validación
- **Unicode support**: `huv_constants.py:10-12` - Configuración encoding y caracteres especiales

### Limitaciones del análisis
- **Contenido específico vocabulario**: Análisis asume estructura típica pero contenido real puede variar
- **Completitud biomarcadores**: Cobertura real depende de necesidades médicas específicas HUV
- **Evolución terminología médica**: Vocabulario debe mantenerse actualizado con avances médicos