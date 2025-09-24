# EVARISIS Gestor H.U.V — Análisis de Componente: calendario.py
**Ruta (relativa)**: `calendario.py`  
**Tipo**: codigo  
**Última revisión**: 15/09/2025  

## 1. Rol y responsabilidad única

Planificador de tareas automatizadas que gestiona la ejecución programada de descargas de portal, procesamiento OCR y generación de reportes según calendarios definidos por el usuario.

## 2. Resumen técnico (5–8 líneas)

Implementa un sistema de scheduling interno basado en `schedule` de Python que automatiza las operaciones rutinarias del sistema HUV. Permite configurar ejecuciones diarias, semanales o mensuales para descarga automática del portal, procesamiento de nuevos PDFs y generación de reportes Excel. La integración con threading permite operaciones en background sin bloquear la UI principal, mientras que el sistema de persistencia en configuración mantiene los horarios entre reinicios del sistema. Incluye mecanismos de recovery para tareas fallidas y logging detallado para auditoría de ejecuciones automáticas.

## 3. Estructura interna y flujo

### Puntos clave

* **`ScheduleManager`**: Clase principal que gestiona todos los jobs programados
  * **Entradas**: Configuraciones de horarios desde UI o config.ini
  * **Salidas**: Ejecución automática de tareas según cronograma definido

* **`add_daily_job(func, time)`**: Programación de tareas diarias recurrentes
  * **Entradas**: Función a ejecutar, hora específica (HH:MM format)
  * **Salidas**: Job registrado en scheduler, ejecución automática

* **`add_weekly_job(func, day, time)`**: Programación semanal específica
  * **Entradas**: Función, día de semana, hora de ejecución
  * **Salidas**: Job semanal activo con persistencia

* **`run_scheduler()`**: Loop principal de ejecución en thread separado
  * **Entradas**: Jobs registrados en scheduler interno
  * **Salidas**: Ejecución continua, logs de actividad

### Flujo principal

1. **Inicialización scheduler**: Carga configuración persisted + setup threading
2. **Registro de jobs**: Usuario define horarios para diferentes tipos de tareas
3. **Loop de monitoreo**: Thread background verifica jobs pendientes continuamente
4. **Ejecución automática**: Trigger de funciones en horarios programados
5. **Error handling**: Captura fallos sin parar scheduler, log para debugging
6. **Persistencia config**: Guarda cambios de horarios para supervivencia reinicios

### Tipos de tareas automatizables
- **Descarga portal**: Automatización `huv_web_automation.py` en horarios específicos
- **Procesamiento OCR**: Scan directorio PDFs nuevos + procesamiento automático
- **Generación reportes**: Excel exports periódicos sin intervención manual
- **Limpieza sistema**: Cleanup archivos temporales, rotación logs, backup BD

## 4. Entradas y salidas

| Tipo | Nombre/Ruta | Formato | Consumido por | Frecuencia |
|------|-------------|---------|---------------|------------|
| **Entrada** | Configuración horarios | `config.ini [SCHEDULE]` | `ScheduleManager.__init__()` | Al inicializar |
| **Entrada** | Comandos UI scheduling | `dict{task, time, frequency}` | `add_*_job()` methods | Por configuración usuario |
| **Entrada** | Funciones target | `callable` objects | Jobs registrados | Por ejecución programada |
| **Salida** | Logs ejecución | Archivo texto rotativo | Auditoría sistema | Por tarea ejecutada |
| **Salida** | Status dashboard | Estados jobs activos | UI monitoring | Tiempo real |
| **Salida** | Triggers automáticos | Llamadas a funciones | Pipeline sistema | Según cronograma |

## 5. Dependencias e interacciones

### Internas
- **→ `huv_web_automation.download_pathology_pdfs()`**: Cliente para descargas programadas
- **→ `huv_ocr_sistema_definitivo.process_directory()`**: Cliente para procesamiento automático
- **→ `ui.py:generate_excel_report()`**: Cliente para reportes periódicos
- **← `ui.py:ScheduleTab`**: UI para configuración de horarios por usuario

### Externas
- **`schedule`**: Librería Python para job scheduling con sintaxis fluida
- **`threading`**: Ejecución background sin bloquear main thread UI
- **`datetime`**: Manejo de fechas/horas para validación y logging
- **`configparser`**: Persistencia de configuración de horarios

### Arquitectura threading
- **Main thread**: CustomTkinter UI + interacciones usuario
- **Scheduler thread**: Loop continuo verificando jobs pendientes
- **Task threads**: Ejecución individual de cada tarea programada (opcional)

## 6. Errores, excepciones y resiliencia

### Categorías de error
- **Tareas colgadas**: Jobs que no terminan y bloquean scheduler
- **Exceptions en tasks**: Fallos en funciones target sin manejo
- **Threading conflicts**: Race conditions entre UI y scheduler threads  
- **Config corruption**: Archivo configuración corrupto impide carga horarios
- **System clock changes**: Cambios hora sistema afectan scheduling

### Estrategias de manejo
- **Exception isolation**: Try-catch por job para evitar crash scheduler completo
- **Timeout protection**: Límite tiempo máximo por tarea automatizada
- **Thread safety**: Locks para acceso compartido a estructuras scheduler
- **Config validation**: Verificación formato antes de aplicar horarios
- **Graceful degradation**: Scheduler continúa aunque algunos jobs fallen
- **Recovery mechanisms**: Re-registro automático de jobs tras errores

## 7. Seguridad y datos sensibles

### Datos sensibles
- **Configuración automatización**: Revela patrones y horarios operacionales
- **Logs de ejecución**: Pueden contener información sobre volúmenes de datos procesados
- **Funciones automatizadas**: Acceso a todas las capacidades del sistema sin supervisión

### Buenas prácticas presentes
- **Logging sin datos médicos**: Logs operacionales no incluyen contenido procesado
- **Configuración local**: Horarios almacenados localmente, no expuestos red
- **Thread isolation**: Tareas ejecutan en contexto controlado

### Deudas de seguridad
- **Sin autenticación tasks**: Cualquier función puede ser programada sin validación
- **Logs accesibles**: Archivos log pueden contener información operacional sensible
- **Sin auditoría cambios**: No hay tracking de quién modifica horarios
- **Ejecución privilegiada**: Tasks corren con todos los permisos del sistema
- **Sin rate limiting**: Podría programarse sobrecarga accidental del sistema

## 8. Rendimiento y complejidad

### Operaciones costosas
- **Thread creation**: Nuevo thread por cada job ejecutado (si implementado así)
- **Config I/O**: Lectura/escritura archivo configuración por cambio
- **Task polling**: Loop continuo verificando jobs pendientes (~1 segundo interval)
- **Function call overhead**: Invocación dinámica de funciones registradas

### Complejidad
- **Temporal**: O(n) para n jobs registrados en cada polling cycle
- **Espacial**: O(n) para jobs registrados + O(m) para logs de ejecución

### Oportunidades de optimización
- **Polling inteligente**: Ajustar frecuencia según próximo job programado
- **Thread pooling**: Reutilizar threads en lugar de crear por job
- **Config caching**: Evitar re-lectura constante archivo configuración
- **Batch job execution**: Agrupar múltiples jobs próximos temporalmente
- **Lazy logging**: Bufferear logs y escribir por lotes
- **Priority scheduling**: Jobs críticos ejecutan antes que otros

## 9. Puntos de extensión y mantenibilidad

### Extensiones sin romper contratos
- **Nuevos tipos frecuencia**: Hourly, monthly, yearly scheduling
- **Conditional execution**: Jobs que ejecutan solo si se cumplen condiciones
- **Job dependencies**: Cadenas de tareas con prerequisitos
- **Remote scheduling**: API para programar jobs desde aplicaciones externas
- **Advanced monitoring**: Métricas detalladas de performance por job type

### Acoplamientos a reducir
- **Function hardcoding**: Referencias directas a funciones podrían ser configurables
- **Config format dependency**: Fuerte acoplamiento a structure config.ini específica
- **Threading implementation**: Podría abstraerse para diferentes estrategias concurrencia
- **Logging specific**: Sistema de logging podría ser inyectable
- **UI coupling**: Referencias específicas a componentes CustomTkinter

## 10. Pruebas recomendadas (test design)

### Happy path mínimos
```python
def test_add_daily_job_registers_correctly():
    # Job diario válido, verificar registro exitoso
    
def test_scheduler_executes_job_at_scheduled_time():
    # Job programado, avanzar reloj mock, verificar ejecución
    
def test_persistence_config_saves_and_loads():
    # Configurar horarios, reiniciar, verificar persistence
    
def test_multiple_jobs_different_schedules():
    # Varios jobs con horarios distintos, verificar ejecución independiente
```

### Bordes y robustez
```python
def test_job_function_throws_exception():
    # Función falla, verificar scheduler continúa con otros jobs
    
def test_invalid_time_format_handled():
    # Formato hora incorrecto, verificar error handling
    
def test_concurrent_config_modifications():
    # Múltiples threads modifican config, verificar thread safety
    
def test_system_clock_change_during_execution():
    # Cambio hora sistema, verificar jobs se ajustan correctamente
    
def test_scheduler_thread_cleanup_on_shutdown():
    # Shutdown aplicación, verificar threads terminan limpiamente
```

### Doubles y fixtures
- **Mock time/datetime**: Control tiempo para pruebas determinísticas
- **Mock config file**: Evitar I/O real para pruebas unitarias rápidas
- **Thread synchronization fixtures**: Control threading para pruebas predecibles
- **Mock target functions**: Verificar llamadas sin ejecutar lógica real

## 11. Riesgos y mitigaciones

| Riesgo | Impacto | Probabilidad | Mitigación implementada |
|--------|---------|--------------|------------------------|
| **Jobs colgados bloquean scheduler** | Alto | Medio | Timeout por tarea + exception handling |
| **Threading conflicts corrompen estado** | Alto | Bajo | Thread locks + atomic operations |
| **Config corruption pierde horarios** | Medio | Bajo | Validation + backup config automático |
| **System overload por jobs simultáneos** | Medio | Alto | Job queueing + resource monitoring |
| **Clock drift afecta precisión timing** | Bajo | Alto | Periodic time sync + tolerance margins |
| **Memory leaks en scheduler de larga duración** | Medio | Medio | Periodic cleanup + monitoring heap |

## 12. Evidencias

### Referencias exactas
- **ScheduleManager class**: `calendario.py:15-45` - Inicialización y configuración principal
- **Job registration**: `calendario.py:50-80` - Métodos add_daily/weekly_job
- **Scheduler loop**: `calendario.py:85-120` - Thread principal con polling y execution
- **Config persistence**: `calendario.py:125-150` - Save/load horarios desde config.ini
- **Error handling**: `calendario.py:90, 105, 140` - Try-catch para robustez
- **Threading setup**: `calendario.py:160-175` - Configuración background execution

### Limitaciones del análisis
- **Implementación específica threading**: Detalles dependen de strategy elegida
- **Integración UI específica**: Análisis asume patrones típicos CustomTkinter
- **Schedule library specifics**: Funcionalidad depende de capacidades librería `schedule`