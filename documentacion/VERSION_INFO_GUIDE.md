# Información de Versión - EVARISIS Gestor H.U.V

## 📋 Descripción

La funcionalidad de **Información de Versión** permite a los usuarios y administradores acceder a información detallada sobre la versión actual del sistema, dependencias, características, y estado técnico de la aplicación.

## 🚀 Acceso Rápido

### Desde la Interfaz Gráfica

1. **Botón del Header**: Click en el botón de versión (ej: `v3.2`) en la esquina superior derecha
2. **Menú Flotante**: Abrir el menú flotante (☰) y seleccionar `ℹ️ Acerca de`

### Programáticamente

```python
from version_info import get_version_string, get_build_info, get_full_version_info

# Información básica
version = get_version_string()  # "v3.2.1 - TTKBootstrap Flotante"
build = get_build_info()        # "Build 20250925001 (25/09/2025)"

# Información completa
full_info = get_full_version_info()
```

## 🔧 Características de la Ventana de Información

### 📋 Tab General
- Nombre completo del proyecto
- Organización responsable
- Información de versión y build
- Tipo de release y codename
- Licencia y repositorio

### 💻 Tab Sistema
- Versión de Python utilizada
- Información de la plataforma (OS, arquitectura)
- Procesador del sistema

### 📦 Tab Dependencias
- Lista completa de dependencias esperadas vs actuales
- Estado de cada librería (✅ OK / ❌ Error)
- Tabla interactiva con información detallada

### ✨ Tab Características
- Lista de todas las características implementadas
- Métricas de rendimiento comparativo
- Información sobre audiencias objetivo

### 🗺️ Tab Roadmap
- Próximas versiones planificadas
- Características y mejoras futuras
- Fechas estimadas de release

## 🛠️ Funcionalidades Adicionales

### 📋 Copiar al Portapapeles
- Botón "📋 Copiar Info Sistema" genera un reporte completo
- Útil para soporte técnico y troubleshooting
- Incluye toda la información relevante del sistema

### 🎨 Interfaz Responsive
- Ventana redimensionable (800x700 por defecto)
- Scroll automático para contenido extenso
- Diseño adaptive a diferentes resoluciones
- Centrado automático en pantalla

## 🎯 Casos de Uso

### Para Usuarios Finales
- **Verificar versión actual**: Confirmar que se está usando la última versión
- **Reportar problemas**: Obtener información técnica para soporte
- **Conocer características**: Explorar las funcionalidades disponibles

### Para Administradores
- **Diagnóstico técnico**: Verificar estado de dependencias
- **Auditoría de sistemas**: Documentar versiones instaladas
- **Planificación**: Revisar roadmap de futuras versiones

### Para Desarrolladores
- **Debugging**: Acceso rápido a información del entorno
- **Testing**: Verificar configuración en diferentes sistemas
- **Documentación**: Referencia técnica actualizada

## 🔧 Configuración y Personalización

### Modificar Información de Versión
Editar el archivo `version_info.py`:

```python
VERSION_INFO = {
    "version": "3.2.1",           # Versión semántica
    "version_name": "Mi Versión", # Nombre descriptivo
    "build_date": "25/09/2025",   # Fecha de build
    "release_type": "Stable",     # Tipo de release
    "codename": "Phoenix",        # Nombre en clave
}
```

### Agregar Nuevas Características
```python
FEATURES = [
    "✅ Mi nueva característica",
    "✅ Otra funcionalidad importante",
    # ... más características
]
```

### Actualizar Métricas de Rendimiento
```python
PERFORMANCE_METRICS = {
    "mi_metrica": "Valor de mejora",
    "otra_metrica": "+50% rendimiento",
    # ... más métricas
}
```

## 🚦 Estados y Indicadores

### Estados de Dependencias
- **✅ OK**: Dependencia instalada y funcionando
- **❌ Error**: Problema con la dependencia
- **⚠️ Warning**: Versión diferente a la esperada

### Indicadores Visuales
- **Verde**: Sistema funcionando correctamente
- **Amarillo**: Advertencias menores
- **Rojo**: Errores críticos que requieren atención

## 📱 Integración con la UI Principal

### Ubicaciones de Acceso
1. **Header Principal**: Botón pequeño con número de versión
2. **Menú Flotante**: Opción "ℹ️ Acerca de"
3. **Atajos de Teclado**: *Por implementar en futuras versiones*

### Consistencia Visual
- Utiliza el sistema de temas TTKBootstrap
- Se adapta automáticamente al tema seleccionado (litera/darkly)
- Iconos consistentes con el resto de la aplicación

## 🔍 Troubleshooting

### Problemas Comunes

**Error al mostrar información de versión**
- Verificar que `version_info.py` existe en el directorio raíz
- Comprobar permisos de lectura del archivo

**Dependencias marcadas como "Error"**
- Ejecutar `pip install -r requirements.txt`
- Verificar entorno virtual activado

**Ventana no se centra correctamente**
- Problema conocido en sistemas multi-monitor
- La ventana se abrirá en monitor principal

## 📊 Estadísticas de Uso

La funcionalidad de información de versión incluye:
- **5 tabs** de información organizada
- **15+ métricas** del sistema
- **10+ dependencias** monitoreadas
- **Roadmap** de 4 versiones futuras
- **Soporte** para múltiples plataformas

## 🚀 Versiones Futuras

### Próximas Mejoras
- **v3.3**: Exportación de reportes en PDF
- **v3.4**: Comparación entre versiones
- **v4.0**: API REST para información de versión
- **v4.1**: Notificaciones automáticas de updates

---

**Nota**: Esta funcionalidad está disponible desde la versión 3.2.1 del sistema EVARISIS Gestor H.U.V. Para más información, consultar la documentación técnica completa.