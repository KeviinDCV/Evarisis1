# TEMPLATES DE IMPLEMENTACIÓN - SISTEMA DE VERSIONADO OBLIGATORIO

## 🎯 PROPÓSITO
Templates específicos por tecnología para implementar el sistema de versionado estándar de manera rápida y consistente.

---

## 🐍 TEMPLATE PYTHON + TKINTER/TTKBOOTSTRAP

### 1. Estructura de Archivos Requerida
```
proyecto/
├── version_info.py          # ← OBLIGATORIO
├── main.py                  # o app.py, ui.py, etc.
├── requirements.txt         # ← Actualizar con psutil
├── README.md               # ← Actualizar con info de versión
├── CHANGELOG.md            # ← Actualizar con nueva funcionalidad
└── VERSION_INFO_GUIDE.md   # ← CREAR
```

### 2. Template `version_info.py`
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[NOMBRE_PROYECTO] - Información de Versión
Sistema de versionado estándar profesional
"""

from datetime import datetime
import sys
import os
import platform

# Información de versión principal
VERSION_INFO = {
    "version": "[X.Y.Z]",
    "version_name": "[NOMBRE_VERSION]",
    "build_date": "[DD/MM/YYYY]",
    "build_number": "[YYYYMMDDNNN]",
    "release_type": "Stable",
    "codename": "[CODENAME]",
}

# Información del proyecto
PROJECT_INFO = {
    "name": "[NOMBRE_PROYECTO]",
    "full_name": "[NOMBRE_COMPLETO_PROYECTO]",
    "description": "[DESCRIPCION_BREVE]",
    "organization": "[ORGANIZACION]",
    "repository": "[URL_REPOSITORIO]",
    "license": "[LICENCIA]",
    "contact": "Equipo de Desarrollo [ORGANIZACION]"
}

# Información del equipo de desarrollo
TEAM_INFO = {
    "desarrollador_principal": {
        "nombre": "[NOMBRE_DESARROLLADOR]",
        "cargo": "[CARGO_DESARROLLADOR]",
        "departamento": "[DEPARTAMENTO_DESARROLLADOR]",
        "contacto": "[EMAIL_DESARROLLADOR]"
    },
    "supervisor_tecnico": {
        "nombre": "[NOMBRE_SUPERVISOR_TECNICO]",
        "cargo": "[CARGO_SUPERVISOR_TECNICO]",
        "departamento": "[DEPARTAMENTO_SUPERVISOR_TECNICO]",
        "contacto": "[EMAIL_SUPERVISOR_TECNICO]"
    },
    "supervisor_area": {
        "nombre": "[NOMBRE_SUPERVISOR_AREA]",
        "cargo": "[CARGO_SUPERVISOR_AREA]",
        "departamento": "[DEPARTAMENTO_SUPERVISOR_AREA]",
        "contacto": "[EMAIL_SUPERVISOR_AREA]"
    }
}

# Dependencias principales del proyecto
DEPENDENCIES = {
    "tkinter": "Built-in",
    "ttkbootstrap": "^1.10.1",
    # Agregar dependencias específicas del proyecto
}

# Características de la versión actual
FEATURES = [
    "✅ [CARACTERISTICA_1]",
    "✅ [CARACTERISTICA_2]",
    "✅ [CARACTERISTICA_3]",
    # Agregar características específicas
]

# Roadmap de próximas versiones
ROADMAP = {
    "v[X.Y+1]": "[DESCRIPCION_PROXIMA_VERSION]",
    "v[X+1.0]": "[DESCRIPCION_VERSION_MAYOR]",
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
        
        # GPU para Windows
        try:
            if platform.system() == "Windows":
                import subprocess
                gpu_result = subprocess.run([
                    "wmic", "path", "win32_VideoController", "get", "name"
                ], capture_output=True, text=True, timeout=5)
                
                if gpu_result.returncode == 0:
                    gpu_lines = [line.strip() for line in gpu_result.stdout.split('\n') 
                                if line.strip() and line.strip() != 'Name']
                    system_info["tarjeta_grafica"] = gpu_lines if gpu_lines else ["No detectada"]
        except Exception:
            system_info["tarjeta_grafica"] = ["No disponible"]
        
        return system_info
        
    except Exception as e:
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "error": f"Error: {str(e)}"
        }

SYSTEM_INFO = get_system_info()

def get_version_string():
    """Retorna string completo de versión"""
    return f"v{VERSION_INFO['version']} - {VERSION_INFO['version_name']}"

def get_build_info():
    """Retorna información de build"""
    return f"Build {VERSION_INFO['build_number']} ({VERSION_INFO['build_date']})"

def get_full_version_info():
    """Retorna diccionario completo con toda la información"""
    return {
        "version": VERSION_INFO,
        "system": SYSTEM_INFO,
        "dependencies": DEPENDENCIES,
        "features": FEATURES,
        "project": PROJECT_INFO,
        "team": TEAM_INFO,
        "roadmap": ROADMAP
    }

def get_dependencies_actual():
    """Obtiene versiones reales de dependencias instaladas"""
    actual_deps = {}
    for package in DEPENDENCIES.keys():
        try:
            if package == "tkinter":
                actual_deps[package] = "✅ Built-in"
            elif package == "ttkbootstrap":
                try:
                    import ttkbootstrap
                    actual_deps[package] = getattr(ttkbootstrap, '__version__', '✅ Instalado')
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            else:
                try:
                    exec(f"import {package}")
                    version = eval(f"{package}.__version__")
                    actual_deps[package] = version
                except AttributeError:
                    actual_deps[package] = "✅ Instalado (sin versión)"
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
        except Exception as e:
            actual_deps[package] = f"⚠️ Error: {str(e)}"
    
    return actual_deps

if __name__ == "__main__":
    print(f"=== {PROJECT_INFO['name']} - Información de Versión ===")
    print(f"Versión: {get_version_string()}")
    print(f"Build: {get_build_info()}")
    print(f"Sistema: {SYSTEM_INFO['platform']}")
```

### 3. Template función `_show_version_info()` para UI Principal

```python
def _show_version_info(self):
    """Mostrar información detallada de la versión del sistema"""
    try:
        from version_info import get_full_version_info, get_version_string, get_build_info, get_dependencies_actual
        
        version_info = get_full_version_info()
        actual_deps = get_dependencies_actual()
        
        # Crear ventana modal
        version_window = ttk.Toplevel(self)
        version_window.title(f"Acerca de - {version_info['project']['name']}")
        version_window.geometry("900x800")
        version_window.resizable(True, True)
        version_window.transient(self)
        version_window.grab_set()
        
        # Centrar ventana
        version_window.update_idletasks()
        x = (version_window.winfo_screenwidth() // 2) - (900 // 2)
        y = (version_window.winfo_screenheight() // 2) - (800 // 2)
        version_window.geometry(f"900x800+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(version_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame, bootstyle="primary", padding=15)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text=version_info['project']['name'],
                 font=("Arial", 18, "bold"), bootstyle="inverse-primary").pack()
        ttk.Label(header_frame, text=f"{get_version_string()} | {get_build_info()}",
                 font=("Arial", 12), bootstyle="inverse-primary").pack(pady=(5, 0))
        ttk.Label(header_frame, text=version_info['project']['description'],
                 font=("Arial", 10), bootstyle="inverse-primary").pack(pady=(5, 0))
        
        # Notebook con 6 pestañas
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 1. Pestaña General
        self._create_general_tab(notebook, version_info)
        
        # 2. Pestaña Sistema
        self._create_system_tab(notebook, version_info)
        
        # 3. Pestaña Dependencias
        self._create_dependencies_tab(notebook, version_info, actual_deps)
        
        # 4. Pestaña Equipo
        self._create_team_tab(notebook, version_info)
        
        # 5. Pestaña Características
        self._create_features_tab(notebook, version_info)
        
        # 6. Pestaña Roadmap
        self._create_roadmap_tab(notebook, version_info)
        
        # Botones
        buttons_frame = ttk.Frame(main_frame, padding=10)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(buttons_frame, text="📋 Copiar Info Sistema",
                  command=lambda: self._copy_system_info(version_info),
                  bootstyle="info").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="✅ Cerrar",
                  command=version_window.destroy,
                  bootstyle="success").pack(side=tk.RIGHT)
        
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Error al mostrar información de versión:\n{str(e)}")

# Métodos auxiliares para crear cada pestaña...
def _create_general_tab(self, notebook, version_info):
    # Implementar pestaña General
    pass

def _create_system_tab(self, notebook, version_info):
    # Implementar pestaña Sistema
    pass

# ... etc para cada pestaña
```

---

## 🌐 TEMPLATE WEB (HTML/JavaScript)

### 1. Estructura de Archivos
```
proyecto/
├── version_info.js          # ← OBLIGATORIO
├── index.html              
├── about.html              # ← Modal de versión
├── package.json            # ← Actualizar versión
└── README.md               # ← Actualizar
```

### 2. Template `version_info.js`
```javascript
// Version Info System - Standard Professional
const VERSION_INFO = {
    version: "[X.Y.Z]",
    versionName: "[NOMBRE_VERSION]",
    buildDate: "[DD/MM/YYYY]",
    buildNumber: "[YYYYMMDDNNN]",
    releaseType: "Stable",
    codename: "[CODENAME]"
};

const PROJECT_INFO = {
    name: "[NOMBRE_PROYECTO]",
    fullName: "[NOMBRE_COMPLETO]",
    description: "[DESCRIPCION]",
    organization: "[ORGANIZACION]",
    repository: "[URL_REPO]",
    license: "[LICENCIA]"
};

const TEAM_INFO = {
    desarrolladorPrincipal: {
        nombre: "[NOMBRE]",
        cargo: "[CARGO]",
        contacto: "[EMAIL]"
    }
    // ... más miembros del equipo
};

function getSystemInfo() {
    return {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        language: navigator.language,
        cookieEnabled: navigator.cookieEnabled,
        onLine: navigator.onLine,
        screenResolution: `${screen.width}x${screen.height}`,
        colorDepth: screen.colorDepth,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone
    };
}

function showVersionModal() {
    // Implementar modal con 6 pestañas
    // General, Sistema, Dependencias, Equipo, Características, Roadmap
}
```

---

## 🗄️ TEMPLATE BASE DE DATOS/API

### Template `version_info.sql`
```sql
-- Tabla de información de versión del sistema
CREATE TABLE system_version_info (
    id INTEGER PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    version_name VARCHAR(100),
    build_date DATE,
    build_number VARCHAR(50),
    release_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla del equipo de desarrollo
CREATE TABLE development_team (
    id INTEGER PRIMARY KEY,
    role_key VARCHAR(50),
    nombre VARCHAR(100),
    cargo VARCHAR(100),
    departamento VARCHAR(100),
    contacto VARCHAR(100)
);

-- Insertar información inicial
INSERT INTO system_version_info (version, version_name, build_date, build_number, release_type)
VALUES ('[X.Y.Z]', '[NOMBRE_VERSION]', '[YYYY-MM-DD]', '[BUILD_NUMBER]', 'Stable');
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

### Para Cualquier Tecnología:
- [ ] Módulo/archivo de información de versión creado
- [ ] Información del proyecto completa
- [ ] Equipo de desarrollo documentado (mínimo 3 roles)
- [ ] Detección de información del sistema
- [ ] Estado de dependencias con iconos
- [ ] Interfaz de acceso (botón/modal/comando)
- [ ] 6 secciones obligatorias implementadas
- [ ] Funcionalidad de copia/exportación
- [ ] Documentación creada (VERSION_INFO_GUIDE.md)
- [ ] README actualizado con acceso a versión
- [ ] CHANGELOG actualizado con nueva funcionalidad

### Validación Final:
- [ ] Sin errores al mostrar información de versión
- [ ] Información del sistema se detecta correctamente
- [ ] Todos los miembros del equipo aparecen
- [ ] Dependencias muestran estados claros
- [ ] Funcionalidad de copia funciona
- [ ] Documentación está completa y actualizada

---

**🎯 Estos templates aseguran implementación rápida y consistente del sistema de versionado obligatorio en cualquier tecnología.**