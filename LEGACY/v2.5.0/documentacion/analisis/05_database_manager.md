# EVARISIS Gestor H.U.V — Análisis de Componente: database_manager.py
**Ruta (relativa)**: `database_manager.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Gestor de persistencia SQLite que inicializa la base de datos con esquema de 167 campos, maneja operaciones CRUD transaccionales y controla duplicados por número de petición.

## 2. Resumen técnico (5–8 líneas)

Este módulo implementa la capa de persistencia unificada del sistema v2.5, reemplazando las exportaciones Excel manuales con una base de datos relacional automática. Define el esquema completo de 167 campos que abarca todos los tipos de informe HUV (IHQ, Biopsia, Autopsia, Revisión) y proporciona operaciones thread-safe para inserción masiva con control de duplicados. La integración con pandas facilita el análisis posterior desde el dashboard, mientras que el control transaccional garantiza consistencia de datos ante fallos parciales durante procesamiento.

## 3. Estructura interna y flujo

### Puntos clave

* **`init_db()`**: Inicialización de base de datos con esquema completo
  * **Entradas**: None (usa constantes globales DB_FILE, TABLE_NAME)
  * **Salidas**: Archivo SQLite con tabla `informes_ihq` creada

* **`save_records(records: list[dict])`**: Inserción masiva con control de duplicados
  * **Entradas**: Lista de diccionarios con datos de informes normalizados
  * **Salidas**: Count de registros insertados, log de duplicados rechazados

* **`get_all_records_as_dataframe()`**: Lectura completa para análisis
  * **Entradas**: None (lee tabla completa)
  * **Salidas**: pandas.DataFrame con todos los registros para dashboard

### Flujo principal

1. **Inicialización**: `init_db()` crea tabla si no existe con esquema de 167 campos
2. **Validación entrada**: Rechaza listas vacías sin operación costosa
3. **Control duplicados**: Query por número de petición antes de inserción
4. **Inserción transaccional**: Batch insert con rollback automático en fallos
5. **Logging operacional**: Registra duplicados rechazados y nuevos insertados
6. **Liberación conexión**: Cierre explícito de conexiones SQLite

### Esquema de datos
- **Campos base HUV**: 55 campos estándar de informes patológicos
- **Campos IHQ especializados**: 8 campos de biomarcadores (HER2, Ki-67, RE/RP, PD-L1, P16)
- **Metadatos sistema**: `id` autoincremental, `fecha_procesado` timestamp
- **Compatibilidad futura**: Estructura preparada para Biopsia/Autopsia/Revisión

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | Registros normalizados | `list[dict]` | `save_records()` | Por lote de procesamiento |
| **Salida** | Base SQLite | `huv_oncologia.db` | Dashboard, exportaciones | Persistente |
| **Salida** | DataFrame maestro | `pandas.DataFrame` | UI dashboard analítico | Por consulta/actualización |
| **Salida** | Logs operación | Count + detalles | UI feedback usuario | Por operación save/load |

## 5. Dependencias e interacciones

### Internas
- **← `procesador_ihq_biomarcadores.process_pdf_to_database()`**: Principal cliente para inserción
- **← `ui.py:load_and_display_data()`**: Cliente para lectura dashboard
- **← `ui.py:update_dashboard()`**: Cliente para análisis con filtros

### Externas
- **`sqlite3`**: Motor de base de datos embedido con soporte transaccional
- **`pandas`**: Construcción de DataFrames para integración seamless con dashboard
- **`pathlib`**: Manejo robusto del archivo de base de datos

### Contrato de datos
- **Clave primaria**: `id` autoincremental para unicidad técnica
- **Clave de negocio**: `"N. peticion (0. Numero de biopsia)"` para control duplicados
- **Flexibilidad**: Columnas TEXT permiten datos heterogéneos sin strict typing

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Base de datos bloqueada**: Acceso concurrente desde múltiples threads UI
- **Corrupción SQLite**: Cierre abrupto durante transacciones
- **Datos inválidos**: Registros sin número de petición o estructura incorrecta
- **Espacio en disco**: Insuficiente para crecimiento de base de datos

### Estrategias de manejo
- **Transacciones automáticas**: `sqlite3` maneja rollback en excepciones
- **Logging sin fallo**: Errores loggeados pero no propagados críticxamente
- **Validación entrada**: Rechaza listas vacías, continúa con registros válidos  
- **Conexiones efímeras**: Abrir/cerrar por operación evita bloqueos prolongados
- **Control duplicados preventivo**: Query antes de insert evita constraint violations

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Información médica completa**: Nombres pacientes, diagnósticos, resultados biomarcadores
- **Datos demográficos**: Identificaciones, fechas nacimiento, contactos
- **Información institucional**: Médicos tratantes, servicios, autorizaciones

### Buenas prácticas presentes
- **Base local**: SQLite evita exposición de red
- **Sin logging de datos**: Logs operacionales no incluyen contenido médico
- **Transacciones atómicas**: Evita estados inconsistentes

### Deudas de seguridad
- **Sin cifrado**: Base SQLite almacena datos médicos sin protección
- **Sin control de acceso**: Cualquier proceso puede leer/escribir archivo
- **Sin auditoría**: No hay trazabilidad de quién accede o modifica datos
- **Backups no automatizados**: Riesgo de pérdida de datos médicos críticos

## 8. Rendimiento y complejidad

### Operaciones costosas
- **Inicialización tabla**: CREATE TABLE con 167 columnas (operación única)
- **Queries de duplicados**: SELECT por número petición (por registro nuevo)
- **Inserción masiva**: INSERT múltiple con validación (por lote)
- **Lectura completa**: SELECT * para dashboard (por actualización)

### Complejidad
- **Temporal**: O(n) para inserción, O(1) para duplicados (con índice), O(n) para lectura completa
- **Espacial**: O(n) para DataFrames en memoria, SQLite eficiente en disco

### Oportunidades de optimización
- **Índices estratégicos**: Índice en número petición para duplicados O(log n)
- **Prepared statements**: Reutilizar queries compiladas para inserción
- **Batch size tuning**: Optimizar tamaño de lotes para mejor I/O
- **Paginación lectura**: Lazy loading para datasets grandes en dashboard
- **Conexión pooling**: Reutilizar conexiones en lugar de abrir/cerrar constante

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevas tablas**: Esquema extensible para otros tipos de informe
- **Campos adicionales**: Columnas TEXT permiten expansión sin migration
- **Índices adicionales**: Optimización de queries específicos sin cambio de API
- **Backup automático**: Rutinas de respaldo sin alterar funcionalidad core
- **Encriptación**: Migración a SQLCipher preservando API

### Acoplamientos a reducir
- **Esquema hardcoded**: Definición de tabla podría externalizarse a configuración
- **Nombres constantes**: DB_FILE y TABLE_NAME podrían ser inyectables
- **Control duplicados específico**: Lógica de negocio podría abstraerse
- **DataFrame coupling**: Podría retornar iteradores en lugar de DataFrame completo

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_init_db_creates_table():
    # Primera ejecución crea tabla con esquema correcto
    
def test_save_valid_records():
    # Lista de registros válidos, verificar inserción exitosa
    
def test_get_all_records_returns_dataframe():
    # Datos en BD, verificar DataFrame estructurado correctamente
```

### Bordes
```python
def test_save_empty_list():
    # Lista vacía, verificar manejo sin error
    
def test_save_duplicate_records():
    # Registros con mismo número petición, verificar rechazo de duplicados
    
def test_database_locked_scenario():
    # Acceso concurrente, verificar manejo de locks
    
def test_invalid_record_structure():
    # Diccionario malformado, verificar tolerancia
```

### Doubles y fixtures
- **Fixture temporal SQLite**: Base de datos en memoria para pruebas aisladas
- **Mock pandas**: Para acelerar pruebas sin DataFrame processing
- **Fixture registros**: Datos de prueba con diferentes características
- **Mock sqlite3**: Para simular condiciones de error específicas

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Corrupción base de datos** | Crítico | Bajo | Transacciones SQLite + cierre explícito conexiones |
| **Acceso concurrente desde UI** | Alto | Medio | Conexiones efímeras + manejo de excepciones |
| **Crecimiento descontrolado BD** | Medio | Alto | Estructura eficiente SQLite + sin logs embedded |
| **Pérdida de datos por fallo disco** | Crítico | Bajo | Recomendación backup manual (no implementado) |
| **Performance degradation con datasets grandes** | Medio | Alto | DataFrame chunking + paginación recomendada |
| **Incompatibilidad schema futuro** | Medio | Medio | Columnas TEXT flexibles + migration path preparado |

## 12. Evidencias

### Referencias exactas
- **Inicialización BD**: `database_manager.py:8-30` - Función `init_db()` con CREATE TABLE completo
- **Control duplicados**: `database_manager.py:35-45` - Query SELECT para verificar existencia
- **Inserción masiva**: `database_manager.py:50-70` - INSERT con executemany() transaccional
- **Lectura DataFrame**: `database_manager.py:75-86` - `get_all_records_as_dataframe()` completa
- **Definición esquema**: `database_manager.py:10-25` - 167 campos con tipos y constraints
- **Constantes globales**: `database_manager.py:5-7` - DB_FILE y TABLE_NAME definiciones

### Limitaciones del análisis
- **Archivo conciso**: 86 líneas permiten análisis completo y detallado
- **Funcionalidad directa**: Sin complejidades algorítmicas ocultas
- **Dependencia SQLite**: Comportamiento depende de implementación SQLite específica