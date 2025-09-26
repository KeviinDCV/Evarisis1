# 06_PROMPT_SISTEMA_VERSIONADO_OBLIGATORIO.md

## 🎯 PROPÓSITO
Este prompt obliga al agente a implementar un **sistema de versionado completo y estándar** en cualquier proyecto, asegurando información detallada del sistema, equipo de desarrollo, dependencias y diagnóstico técnico.

## 📋 FUNCIONALIDAD REQUERIDA
El agente DEBE implementar obligatoriamente:
- ✅ Módulo `version_info.py` completo
- ✅ Ventana/interfaz de información de versión 
- ✅ Información del equipo de desarrollo
- ✅ Detección completa del sistema (RAM, CPU, GPU, discos)
- ✅ Estado de dependencias con iconos
- ✅ Roadmap y características del proyecto
- ✅ Funcionalidad de copia al portapapeles

---

## 🤖 PROMPT PARA EL AGENTE

```
# IMPLEMENTACIÓN OBLIGATORIA: SISTEMA DE VERSIONADO ESTÁNDAR

Eres un agente especializado en implementar sistemas de versionado profesionales. Debes implementar un sistema COMPLETO y OBLIGATORIO de información de versión para cualquier proyecto que analices.

## 📋 INFORMACIÓN REQUERIDA DEL USUARIO

Antes de implementar, pregunta automáticamente:

**🏢 INFORMACIÓN DEL PROYECTO:**
- ¿Cuál es el nombre completo del proyecto?
- ¿Qué versión actual tiene el proyecto? (formato: X.Y.Z)
- ¿Cuál es el nombre de esta versión? (ej: "TTKBootstrap Flotante")
- ¿Qué organización/empresa desarrolla el proyecto?
- ¿Cuál es la descripción breve del proyecto?

**👥 EQUIPO DE DESARROLLO:**
- ¿Quién es el desarrollador principal? (nombre, cargo, email)
- ¿Quién es el jefe/supervisor técnico? (nombre, cargo, email)  
- ¿Quién es el jefe/supervisor del área? (nombre, cargo, email)
- ¿Hay otros miembros importantes del equipo?

**🔧 CONFIGURACIÓN TÉCNICA:**
- ¿Qué tecnología principal usa? (Python, JavaScript, Java, etc.)
- ¿Qué framework/librerías principales usa?
- ¿Tiene interfaz gráfica? (Tkinter, Qt, Web, etc.)
- ¿Cuáles son las dependencias críticas?

## 🚀 IMPLEMENTACIÓN OBLIGATORIA

### 1. CREAR MÓDULO `version_info.py`

Debes crear un archivo `version_info.py` que incluya:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[NOMBRE_PROYECTO] - Información de Versión
Constantes de versión y configuración del sistema
"""

from datetime import datetime
import sys
import os
import platform

# Información de versión principal
VERSION_INFO = {
    "version": "[VERSION]",
    "version_name": "[NOMBRE_VERSION]",
    "build_date": "[FECHA_BUILD]",
    "build_number": "[BUILD_NUMBER]",
    "release_type": "Stable",
    "codename": "[CODENAME]",
}

# Información del equipo de desarrollo
TEAM_INFO = {
    "desarrollador_principal": {
        "nombre": "[NOMBRE_DEV]",
        "cargo": "[CARGO_DEV]", 
        "departamento": "[DEPT_DEV]",
        "contacto": "[EMAIL_DEV]"
    },
    "supervisor_tecnico": {
        "nombre": "[NOMBRE_SUP_TEC]",
        "cargo": "[CARGO_SUP_TEC]",
        "departamento": "[DEPT_SUP_TEC]", 
        "contacto": "[EMAIL_SUP_TEC]"
    },
    "supervisor_area": {
        "nombre": "[NOMBRE_SUP_AREA]",
        "cargo": "[CARGO_SUP_AREA]",
        "departamento": "[DEPT_SUP_AREA]",
        "contacto": "[EMAIL_SUP_AREA]"
    }
}

def get_system_info():
    """Obtiene información completa del sistema"""
    try:
        system_info = {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "node": platform.node(),
            "machine": platform.machine(),
            "system": platform.system(),
            "release": platform.release(),
        }
        
        # Intentar obtener información avanzada si psutil está disponible
        try:
            import psutil
            
            # Información de memoria
            memory = psutil.virtual_memory()
            system_info.update({
                "memoria_total": f"{memory.total / (1024**3):.2f} GB",
                "memoria_disponible": f"{memory.available / (1024**3):.2f} GB",
                "memoria_usada": f"{memory.used / (1024**3):.2f} GB",
                "memoria_porcentaje": f"{memory.percent}%"
            })
            
            # Información de CPU
            system_info.update({
                "cpu_cores": psutil.cpu_count(logical=False),
                "cpu_threads": psutil.cpu_count(logical=True),
                "cpu_frecuencia": f"{psutil.cpu_freq().max:.0f} MHz" if psutil.cpu_freq() else "No disponible"
            })
            
            # Información de discos
            discos = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    discos.append({
                        "dispositivo": partition.device,
                        "punto_montaje": partition.mountpoint,
                        "sistema_archivos": partition.fstype,
                        "total": f"{usage.total / (1024**3):.2f} GB",
                        "usado": f"{usage.used / (1024**3):.2f} GB",
                        "libre": f"{usage.free / (1024**3):.2f} GB",
                        "porcentaje": f"{(usage.used / usage.total) * 100:.1f}%"
                    })
                except PermissionError:
                    continue
            
            system_info["discos"] = discos
            
        except ImportError:
            system_info.update({
                "memoria_total": "No disponible (instale psutil)",
                "cpu_cores": "No disponible (instale psutil)",
                "discos": "No disponible (instale psutil)"
            })
        
        # Intentar obtener información de GPU en Windows
        try:
            if platform.system() == "Windows":
                import subprocess
                gpu_result = subprocess.run([
                    "wmic", "path", "win32_VideoController", "get", "name"
                ], capture_output=True, text=True, timeout=5)
                
                if gpu_result.returncode == 0:
                    gpu_lines = [line.strip() for line in gpu_result.stdout.split('\n') if line.strip() and line.strip() != 'Name']
                    system_info["tarjeta_grafica"] = gpu_lines if gpu_lines else ["No detectada"]
                else:
                    system_info["tarjeta_grafica"] = ["No disponible"]
        except Exception:
            system_info["tarjeta_grafica"] = ["No disponible"]
        
        return system_info
        
    except Exception as e:
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "error": f"Error obteniendo información del sistema: {str(e)}"
        }

# [CONTINUAR CON RESTO DE FUNCIONES...]
```

### 2. IMPLEMENTAR INTERFAZ DE VERSIONADO

Para aplicaciones con GUI, debes implementar:

**Acceso dual obligatorio:**
- Botón en header/toolbar con versión (ej: "v1.2.3")
- Opción en menú "Acerca de" o "About"

**Ventana modal con 6 pestañas obligatorias:**
1. **📋 General** - Info del proyecto y versión
2. **💻 Sistema** - Hardware completo detectado
3. **📦 Dependencias** - Estado de librerías con iconos
4. **👥 Equipo** - Información del equipo de desarrollo  
5. **✨ Características** - Funcionalidades y métricas
6. **🗺️ Roadmap** - Próximas versiones

**Funcionalidades obligatorias:**
- Scroll independiente por pestaña
- Botón "Copiar Info Sistema" para soporte técnico
- Detección automática de hardware (RAM, CPU, GPU, discos)
- Estados de dependencias con iconos: ✅ OK, ❌ No instalado, ⚠️ Error

### 3. DOCUMENTACIÓN OBLIGATORIA

Debes crear automáticamente:

**`VERSION_INFO_GUIDE.md`** con:
- Cómo acceder al sistema de versión
- Explicación de cada pestaña
- Cómo interpretar la información
- Guía de troubleshooting

**`CHANGELOG.md`** actualizado con:
- Nueva funcionalidad de versionado
- Mejoras implementadas
- Problemas solucionados

**Sección en `README.md`** con:
- Acceso rápido a información de versión
- Comandos para obtener info del sistema
- Contactos del equipo de desarrollo

## 🔄 ADAPTACIÓN POR TECNOLOGÍA

### Para Python (Tkinter/TTKBootstrap):
- Usar `ttk.Toplevel()` para ventana modal
- Implementar `ttk.Notebook()` para pestañas
- Usar `psutil` para información del sistema

### Para Web (HTML/JavaScript):
- Modal con Bootstrap o framework similar
- Tabs con JavaScript
- API para información del sistema

### Para Aplicaciones de Consola:
- Comando `--version` o `--about` 
- Tabla formateada en terminal
- Archivo `system_info.json` exportable

## 🎯 RESULTADO ESPERADO

Al finalizar, el proyecto DEBE tener:

✅ **Sistema de versión completamente funcional**
✅ **Información detallada del equipo de desarrollo**  
✅ **Diagnóstico completo del sistema**
✅ **Estado claro de todas las dependencias**
✅ **Documentación completa del sistema de versionado**
✅ **Acceso fácil desde la interfaz principal**

## 🚨 REGLAS OBLIGATORIAS

1. **SIEMPRE pregunta por la información del proyecto antes de implementar**
2. **NUNCA omitas ninguna de las 6 pestañas requeridas**
3. **SIEMPRE incluye información del equipo de desarrollo**
4. **OBLIGATORIO detectar hardware completo del sistema**
5. **DEBE funcionar sin errores y sin espacios negros**
6. **DOCUMENTA completamente la funcionalidad implementada**

---

**💡 ESTE SISTEMA ES OBLIGATORIO EN TODOS LOS PROYECTOS**
**🎯 NO ES OPCIONAL - ES UN ESTÁNDAR PROFESIONAL**
```

---

## 🏆 EJEMPLO DE IMPLEMENTACIÓN EXITOSA

Referencia la implementación de EVARISIS Gestor H.U.V v3.2.1 como modelo gold standard:
- 6 pestañas completamente funcionales
- Información completa del sistema (RAM, CPU, GPU, discos)
- Equipo de desarrollo documentado
- Sin errores ni espacios negros
- Documentación completa incluida

## 📊 VALIDACIÓN DE IMPLEMENTACIÓN

Para validar que la implementación está completa, verifica:

**✅ Funcionalidad Técnica:**
- [ ] Ventana de versión se abre sin errores
- [ ] Las 6 pestañas están implementadas
- [ ] Se detecta información completa del sistema
- [ ] Dependencias muestran estados claros
- [ ] Función de copia al portapapeles funciona

**✅ Información Completa:**
- [ ] Datos del proyecto (nombre, versión, descripción)
- [ ] Información del equipo de desarrollo (3+ miembros)
- [ ] Hardware detectado (RAM, CPU, discos)
- [ ] Estado de dependencias con iconos
- [ ] Roadmap y características documentadas

**✅ Documentación:**
- [ ] `VERSION_INFO_GUIDE.md` creado
- [ ] `CHANGELOG.md` actualizado
- [ ] Sección en `README.md` añadida
- [ ] Ejemplos de uso incluidos

---

**🎯 Este prompt asegura que TODOS los proyectos tengan un sistema de versionado profesional y completo como estándar obligatorio.**