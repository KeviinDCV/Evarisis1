#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS Gestor HUV - Información de Versión
Constantes de versión y configuración del sistema
"""

from datetime import datetime
import sys
import os
import platform
import psutil
import subprocess
import socket
import uuid
import shutil

# Información de versión principal
VERSION_INFO = {
    "version": "3.2.1",
    "version_name": "TTKBootstrap Flotante",
    "build_date": "25/09/2025",
    "build_number": "20250925001",
    "release_type": "Stable",
    "codename": "Phoenix",
}

# Información del equipo de desarrollo
TEAM_INFO = {
    "desarrollador": {
        "nombre": "Daniel Restrepo",
        "cargo": "Ingeniero de Soluciones",
        "departamento": "Innovación y Desarrollo",
        "correo": "Pendiente"
    },
    "lider_investigacion": {
        "nombre": "Dr. Juan Camilo Bayona",
        "cargo": "Coordinador del Área Cirugía Oncológica",
        "departamento": "Servicio de Oncología",
        "correo": "Pendiente"
    },
    "jefe_gestion_informacion": {
        "nombre": "Ing. Diego Peña",
        "cargo": "Jefe de Gestión de la Información",
        "departamento": "Gestión de la Información",
        "correo": "Pendiente"
    }
}

def get_system_info():
    """Obtiene información completa del sistema"""
    try:
        # Información básica del sistema
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
            # Si psutil no está disponible, usar información básica
            system_info.update({
                "memoria_total": "No disponible (instale psutil)",
                "cpu_cores": "No disponible (instale psutil)",
                "discos": "No disponible (instale psutil)"
            })
        
        # Intentar obtener información de GPU en Windows
        try:
            if platform.system() == "Windows":
                import subprocess
                
                # Obtener información de GPU usando wmic
                gpu_result = subprocess.run([
                    "wmic", "path", "win32_VideoController", "get", "name"
                ], capture_output=True, text=True, timeout=5)
                
                if gpu_result.returncode == 0:
                    gpu_lines = [line.strip() for line in gpu_result.stdout.split('\n') if line.strip() and line.strip() != 'Name']
                    system_info["tarjeta_grafica"] = gpu_lines if gpu_lines else ["No detectada"]
                else:
                    system_info["tarjeta_grafica"] = ["No disponible"]
                
                # Obtener información de la placa madre
                board_result = subprocess.run([
                    "wmic", "baseboard", "get", "product,manufacturer"
                ], capture_output=True, text=True, timeout=5)
                
                if board_result.returncode == 0:
                    lines = [line.strip() for line in board_result.stdout.split('\n') if line.strip()]
                    if len(lines) > 1:
                        board_info = lines[1].split()
                        if len(board_info) >= 2:
                            system_info["placa_madre"] = f"{board_info[0]} {board_info[1]}"
                        else:
                            system_info["placa_madre"] = " ".join(board_info)
                    else:
                        system_info["placa_madre"] = "No detectada"
                else:
                    system_info["placa_madre"] = "No disponible"
                    
        except Exception:
            system_info["tarjeta_grafica"] = ["No disponible"]
            system_info["placa_madre"] = "No disponible"
        
        return system_info
        
    except Exception as e:
        return {
            "python_version": sys.version,
            "platform": platform.platform(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor(),
            "error": f"Error obteniendo información del sistema: {str(e)}"
        }

# Información del sistema (será calculada dinámicamente)
SYSTEM_INFO = get_system_info()

# Dependencias principales y sus versiones esperadas
DEPENDENCIES = {
    "ttkbootstrap": "^1.10.1",
    "selenium": "^4.15.0", 
    "PyMuPDF": "^1.23.0",
    "pandas": "^2.1.0",
    "matplotlib": "^3.8.0",
    "PIL": "^10.0.0",
    "pytesseract": "^0.3.10",
    "openpyxl": "^3.1.0",
    "seaborn": "^0.13.0",
    "numpy": "^1.24.0"
}

# Características de la versión actual
FEATURES = [
    "✅ Interfaz TTKBootstrap moderna",
    "✅ Sistema de navegación flotante",
    "✅ Temas adaptativos (litera/darkly)",
    "✅ OCR híbrido optimizado",
    "✅ Dashboard analítico avanzado",
    "✅ Automatización web Selenium",
    "✅ Base de datos SQLite normalizada",
    "✅ Exportaciones Excel automatizadas",
    "✅ Threading no-bloqueante",
    "✅ Gestión de memoria optimizada"
]

# Métricas de rendimiento
PERFORMANCE_METRICS = {
    "startup_improvement": "+40% más rápido vs v2.5",
    "memory_usage": "-25% uso de memoria vs v2.5",
    "ocr_accuracy": ">95% en documentos nativos",
    "processing_speed": "100+ informes/hora",
    "database_capacity": "10,000+ registros optimizados",
    "ui_responsiveness": "Threading optimizado"
}

# Información del proyecto
PROJECT_INFO = {
    "name": "EVARISIS Gestor H.U.V",
    "full_name": "EVARISIS Gestor Hospital Universitario del Valle",
    "description": "Sistema de Gestión Oncológica Inteligente",
    "organization": "Hospital Universitario del Valle",
    "license": "MIT License",
    "contact": "Equipo de Desarrollo EVARISIS"
}

# Audiencias del sistema
AUDIENCES = {
    "Equipo Médico Oncológico": "Dashboard biomarcadores para decisiones terapéuticas",
    "Dirección Hospitalaria": "Métricas operativas y ROI (85% reducción tiempo)",
    "Investigadores Clínicos": "Dataset curado con 167 campos estructurados",
    "Equipo de Desarrollo": "Arquitectura modular y documentación completa"
}

# Próximas versiones (roadmap)
ROADMAP = {
    "v3.3": "Mejoras OCR y nuevos biomarcadores",
    "v3.4": "Dashboard interactivo con filtros avanzados", 
    "v4.0": "Integración SERVINTE y API REST",
    "v4.1": "Motor de auditoría automática con IA"
}

def get_version_string():
    """Retorna string completo de versión"""
    return f"v{VERSION_INFO['version']} - {VERSION_INFO['version_name']}"

def get_build_info():
    """Retorna información de build"""
    return f"Build {VERSION_INFO['build_number']} ({VERSION_INFO['build_date']})"

def get_full_version_info():
    """Retorna diccionario completo con toda la información de versión"""
    return {
        "version": VERSION_INFO,
        "system": SYSTEM_INFO,
        "dependencies": DEPENDENCIES,
        "features": FEATURES,
        "performance": PERFORMANCE_METRICS,
        "project": PROJECT_INFO,
        "audiences": AUDIENCES,
        "roadmap": ROADMAP,
        "team": TEAM_INFO
    }

def get_dependencies_actual():
    """Intenta obtener las versiones reales de las dependencias instaladas"""
    actual_deps = {}
    for package in DEPENDENCIES.keys():
        try:
            if package == "PIL":
                import PIL
                actual_deps[package] = PIL.__version__
            elif package == "PyMuPDF":
                try:
                    import fitz
                    actual_deps[package] = fitz.__version__
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            elif package == "matplotlib":
                import matplotlib
                actual_deps[package] = matplotlib.__version__
            elif package == "pandas":
                import pandas
                actual_deps[package] = pandas.__version__
            elif package == "numpy":
                import numpy
                actual_deps[package] = numpy.__version__
            elif package == "seaborn":
                try:
                    import seaborn
                    actual_deps[package] = seaborn.__version__
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            elif package == "openpyxl":
                try:
                    import openpyxl
                    actual_deps[package] = openpyxl.__version__
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            elif package == "pytesseract":
                try:
                    import pytesseract
                    actual_deps[package] = pytesseract.__version__ if hasattr(pytesseract, '__version__') else "✅ Instalado"
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            elif package == "selenium":
                try:
                    import selenium
                    actual_deps[package] = selenium.__version__
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            elif package == "ttkbootstrap":
                try:
                    import ttkbootstrap
                    actual_deps[package] = ttkbootstrap.__version__
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
            else:
                # Método genérico para otros paquetes
                try:
                    exec(f"import {package}")
                    version = eval(f"{package}.__version__")
                    actual_deps[package] = version
                except AttributeError:
                    actual_deps[package] = "✅ Instalado (sin versión)"
                except ImportError:
                    actual_deps[package] = "❌ No instalado"
                    
        except ImportError:
            actual_deps[package] = "❌ No instalado"
        except Exception as e:
            actual_deps[package] = f"⚠️ Error: {str(e)}"
    
    return actual_deps

if __name__ == "__main__":
    # Test de la información de versión
    print("=== EVARISIS Gestor H.U.V - Información de Versión ===")
    print(f"Versión: {get_version_string()}")
    print(f"Build: {get_build_info()}")
    print(f"Python: {SYSTEM_INFO['python_version']}")
    print(f"Plataforma: {SYSTEM_INFO['platform']}")