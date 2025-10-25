# GUÍA DE USO: Sistema de Logging - auditor_sistema.py

**Fecha**: 2025-10-23
**Versión**: v6.0.2

---

## INTRODUCCIÓN

El sistema de logging reemplaza `print()` con niveles de severidad configurables:

- **ERROR**: Fallos críticos, excepciones
- **WARNING**: Validaciones fallidas, datos sospechosos
- **INFO**: Progreso de auditoría, estados OK (DEFAULT)
- **DEBUG**: Detalles internos, valores intermedios

---

## USO BÁSICO

### 1. Uso Normal (Nivel INFO - Recomendado para Producción)

```bash
# Por defecto, muestra solo INFO, WARNING, ERROR
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
```

**Salida típica:**
```
INFO: AuditorSistema inicializado correctamente
INFO: Caso IHQ250980 procesado correctamente
WARNING: Biomarcador Ki-67 no encontrado en BD
```

### 2. Modo DEBUG (Para Debugging Detallado)

```python
from herramientas_ia.auditor_sistema import AuditorSistema
import logging

# Crear auditor
auditor = AuditorSistema()

# Activar DEBUG
auditor.logger.setLevel(logging.DEBUG)

# Auditar caso (muestra TODOS los mensajes)
auditor.auditar_caso("IHQ250980")
```

**Salida típica:**
```
INFO: AuditorSistema inicializado correctamente
DEBUG: DB: C:\...\huv_oncologia.db
DEBUG: Debug maps: C:\...\data\debug_maps
DEBUG: Buscando debug_map para caso: IHQ250980
DEBUG: Archivo más reciente: debug_map_IHQ250980_20251020_153000.json
DEBUG: Debug_map cargado exitosamente para IHQ250980
INFO: Caso IHQ250980 procesado correctamente
WARNING: Biomarcador Ki-67 no encontrado en BD
```

### 3. Modo Silencioso (Solo Errores Críticos)

```python
auditor = AuditorSistema()
auditor.logger.setLevel(logging.ERROR)

# Solo mostrará errores críticos
auditor.auditar_caso("IHQ250980")
```

**Salida típica:**
```
ERROR: Error al leer debug_map debug_map_IHQ250980_*.json: [Errno 2] No such file or directory
```

---

## CONFIGURACIÓN AVANZADA

### Cambiar Formato de Mensajes

```python
import logging

auditor = AuditorSistema()

# Formato personalizado (con timestamp)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Aplicar a handler
for handler in auditor.logger.handlers:
    handler.setFormatter(formatter)

auditor.auditar_caso("IHQ250980")
```

**Salida:**
```
2025-10-23 12:30:45 - herramientas_ia.auditor_sistema - INFO - AuditorSistema inicializado correctamente
2025-10-23 12:30:45 - herramientas_ia.auditor_sistema - DEBUG - Buscando debug_map para caso: IHQ250980
```

### Guardar Logs en Archivo

```python
import logging

auditor = AuditorSistema()

# Agregar handler de archivo
file_handler = logging.FileHandler('auditor_sistema.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
auditor.logger.addHandler(file_handler)

# Ahora los logs van a consola Y archivo
auditor.auditar_caso("IHQ250980")
```

### Logging por Caso

```python
import logging

auditor = AuditorSistema()

# Auditar múltiples casos con logging
casos = ["IHQ250980", "IHQ250981", "IHQ250982"]

for i, caso in enumerate(casos, 1):
    auditor.logger.info(f"Procesando caso {i}/{len(casos)}: {caso}")
    resultado = auditor.auditar_caso(caso)

    if resultado.get('errores'):
        auditor.logger.warning(f"Caso {caso} tiene {len(resultado['errores'])} errores")
    else:
        auditor.logger.info(f"Caso {caso} procesado sin errores")
```

---

## TABLA DE NIVELES DE LOGGING

| Nivel | Valor Numérico | Cuándo Usar | Ejemplo |
|-------|----------------|-------------|---------|
| **DEBUG** | 10 | Desarrollo, debugging detallado | "Buscando debug_map para caso X" |
| **INFO** | 20 | Producción normal, progreso | "Caso X procesado correctamente" |
| **WARNING** | 30 | Advertencias, datos sospechosos | "Biomarcador no encontrado" |
| **ERROR** | 40 | Errores recuperables | "Error al leer archivo" |
| **CRITICAL** | 50 | Errores irrecuperables | "Base de datos corrupta" |

---

## EJEMPLOS DE USO POR ESCENARIO

### Escenario 1: Desarrollo (Debug Completo)

```python
import logging

auditor = AuditorSistema()
auditor.logger.setLevel(logging.DEBUG)

# Ver TODO lo que pasa internamente
auditor.auditar_caso("IHQ250980")
```

### Escenario 2: Producción (Solo Info y Errores)

```python
import logging

auditor = AuditorSistema()
auditor.logger.setLevel(logging.INFO)

# Ver solo progreso y problemas
for caso in casos:
    auditor.auditar_caso(caso)
```

### Escenario 3: Auditoría Masiva (Archivo + Consola)

```python
import logging

auditor = AuditorSistema()

# Archivo: TODO (DEBUG)
file_handler = logging.FileHandler('auditoria_masiva.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
auditor.logger.addHandler(file_handler)

# Consola: Solo INFO
auditor.logger.setLevel(logging.INFO)

# Auditar 100 casos (detalle en archivo, resumen en consola)
for caso in casos_100:
    auditor.auditar_caso(caso)
```

### Escenario 4: Integración con Sistema Externo

```python
import logging
import logging.handlers

auditor = AuditorSistema()

# Enviar logs a servidor syslog
syslog_handler = logging.handlers.SysLogHandler(address=('localhost', 514))
syslog_handler.setLevel(logging.INFO)
auditor.logger.addHandler(syslog_handler)

# Ahora los logs también van a syslog
auditor.auditar_caso("IHQ250980")
```

---

## MENSAJES DE LOGGING IMPLEMENTADOS

### En `__init__()`
- `INFO`: "AuditorSistema inicializado correctamente"
- `DEBUG`: "DB: {path}"
- `DEBUG`: "Debug maps: {path}"

### En `_obtener_debug_map()`
- `DEBUG`: "Buscando debug_map para caso: {numero_caso}"
- `WARNING`: "No se encontró debug_map para {numero_caso}"
- `DEBUG`: "Archivo más reciente: {archivo.name}"
- `DEBUG`: "Debug_map cargado exitosamente para {numero_caso}"
- `ERROR`: "Error al leer debug_map {archivo.name}: {error}"

### En `clear_cache()`
- `INFO`: "Caché de debug_maps limpiado"

---

## COMPARACIÓN: Antes vs. Después

### ANTES (con print)
```python
print(f"🔍 AUDITANDO CASO: {numero_caso}")  # No se puede filtrar
print(f"❌ Error: {e}")  # No hay nivel
print(f"✅ OK")  # No hay contexto
```

**Problemas:**
- ❌ No se puede filtrar
- ❌ No hay niveles de severidad
- ❌ No se puede redirigir fácilmente
- ❌ Difícil integración con sistemas de logging

### DESPUÉS (con logging)
```python
self.logger.info(f"AUDITANDO CASO: {numero_caso}")
self.logger.error(f"Error al procesar: {e}")
self.logger.debug(f"Detalle interno: {valor}")
```

**Ventajas:**
- ✅ Filtrable por nivel
- ✅ Niveles de severidad claros
- ✅ Fácil redirigir (archivo, syslog, etc.)
- ✅ Compatible con logging centralizado

---

## TIPS Y MEJORES PRÁCTICAS

### 1. Niveles de Logging según Ambiente

```python
import os

auditor = AuditorSistema()

# Automático según variable de ambiente
if os.getenv('ENV') == 'production':
    auditor.logger.setLevel(logging.INFO)
elif os.getenv('ENV') == 'development':
    auditor.logger.setLevel(logging.DEBUG)
else:
    auditor.logger.setLevel(logging.WARNING)
```

### 2. Rotar Logs Automáticamente

```python
import logging.handlers

auditor = AuditorSistema()

# Rotar cuando el archivo alcance 10MB (mantener 5 backups)
rotating_handler = logging.handlers.RotatingFileHandler(
    'auditor_sistema.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
rotating_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
auditor.logger.addHandler(rotating_handler)
```

### 3. Logs por Fecha

```python
import logging.handlers

auditor = AuditorSistema()

# Un archivo por día
timed_handler = logging.handlers.TimedRotatingFileHandler(
    'auditor_sistema.log',
    when='midnight',
    interval=1,
    backupCount=30,  # Mantener 30 días
    encoding='utf-8'
)
timed_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
auditor.logger.addHandler(timed_handler)
```

---

## TROUBLESHOOTING

### Problema: No veo mensajes DEBUG

**Causa**: Nivel de logging demasiado alto

**Solución:**
```python
auditor.logger.setLevel(logging.DEBUG)
```

### Problema: Demasiados mensajes

**Causa**: Nivel DEBUG en producción

**Solución:**
```python
auditor.logger.setLevel(logging.INFO)  # O WARNING
```

### Problema: Logs duplicados

**Causa**: Múltiples handlers agregados

**Solución:**
```python
# Limpiar handlers antes de agregar nuevos
auditor.logger.handlers.clear()

# Agregar handler limpio
handler = logging.StreamHandler()
auditor.logger.addHandler(handler)
```

---

## CONCLUSIÓN

El sistema de logging implementado proporciona:

- ✅ **Control granular** de verbosidad
- ✅ **Mejor debugging** con niveles
- ✅ **Producción limpia** (solo INFO/WARNING/ERROR)
- ✅ **Integración fácil** con sistemas externos

**Recomendación para producción**: `logging.INFO`
**Recomendación para desarrollo**: `logging.DEBUG`

---

**Documentado por**: EVARISIS
**Versión**: v6.0.2
**Fecha**: 2025-10-23
