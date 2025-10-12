#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ Utilidades Comunes para Herramientas de IA
============================================

Este módulo contiene funciones auxiliares y configuraciones comunes
para todas las herramientas de análisis del sistema HUV.

Autor: Sistema EVARISIS
Fecha: 3 de octubre de 2025
Versión: 1.0.0
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Agregar el directorio padre al path para importar módulos del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

def verificar_entorno():
    """Verificar que el entorno y dependencias están correctos"""
    try:
        # Verificar imports principales
        from core.database_manager import get_base_path, DB_FILE, TABLE_NAME, HUV_CONFIG
        from core.extractors.medical_extractor import MALIGNIDAD_KEYWORDS_IHQ
        from core.extractors.patient_extractor import PATIENT_PATTERNS
        from core.unified_extractor import extract_ihq_data
        
        return True, "✅ Todos los módulos importados correctamente"
    except ImportError as e:
        return False, f"❌ Error importando módulos: {e}"

def obtener_configuracion_proyecto():
    """Obtener configuración centralizada del proyecto"""
    try:
        from core.database_manager import HUV_CONFIG, CUPS_CODES, PROCEDIMIENTOS, ESPECIALIDADES_SERVICIOS
        from core.extractors.medical_extractor import MALIGNIDAD_KEYWORDS_IHQ
        from core.extractors.patient_extractor import PATIENT_PATTERNS
        
        return {
            'huv_config': HUV_CONFIG,
            'cups_codes': CUPS_CODES,
            'procedimientos': PROCEDIMIENTOS,
            'especialidades_servicios': ESPECIALIDADES_SERVICIOS,
            'malignidad_keywords': MALIGNIDAD_KEYWORDS_IHQ,
            'patient_patterns': PATIENT_PATTERNS
        }
    except ImportError:
        return {}

def obtener_rutas_sistema():
    """Obtener rutas importantes del sistema"""
    try:
        from core.database_manager import get_base_path, DB_FILE
        
        base_path = get_base_path()
        export_path = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "EVARISIS Gestor Oncologico",
            "Exportaciones Base de datos"
        )
        
        return {
            'base_path': str(base_path),
            'db_file': DB_FILE,
            'pdf_input': str(base_path / "pdfs_patologia"),
            'excel_debug': str(base_path / "EXCEL"),
            'export_path': export_path,
            'excel_export': os.path.join(export_path, "Excel"),
            'db_export': os.path.join(export_path, "Base de datos"),
            'config_path': str(base_path / "config" / "config.ini")
        }
    except Exception as e:
        return {'error': str(e)}

def mostrar_banner_herramienta(nombre_herramienta: str, version: str = "1.0.0"):
    """Mostrar banner inicial de la herramienta"""
    banner = f"""
{'='*80}
🏥 {nombre_herramienta.upper()}
EVARISIS Gestor HUV - Sistema de Oncología
{'='*80}
📅 Fecha: {datetime.now().strftime('%d de %B de %Y')}
⚡ Versión: {version}
🔧 Estado: Sistema Operativo
{'='*80}
"""
    print(banner)

def verificar_base_datos():
    """Verificar estado de la base de datos"""
    try:
        from core.database_manager import DB_FILE
        
        if not os.path.exists(DB_FILE):
            return False, f"❌ Base de datos no encontrada: {DB_FILE}"
        
        # Verificar tamaño
        tamaño = os.path.getsize(DB_FILE)
        if tamaño == 0:
            return False, "❌ Base de datos está vacía"
        
        tamaño_mb = tamaño / (1024 * 1024)
        
        return True, f"✅ Base de datos OK ({tamaño_mb:.1f} MB)"
        
    except Exception as e:
        return False, f"❌ Error verificando base de datos: {e}"

# Diccionario de comandos disponibles para las herramientas
COMANDOS_DISPONIBLES = {
    'consulta_base_datos': {
        'descripcion': 'Consultar y verificar información en la base de datos',
        'archivo': 'consulta_base_datos.py',
        'ejemplos': [
            'python herramientas_ia/consulta_base_datos.py',
            'Luego seleccionar opción del menú interactivo'
        ]
    },
    'verificar_exceles': {
        'descripcion': 'Verificar archivos Excel exportados',
        'archivo': 'verificar_exceles_exportados.py', 
        'ejemplos': [
            'python herramientas_ia/verificar_exceles_exportados.py',
            'Revisar exportaciones en Documents/EVARISIS Gestor Oncologico'
        ]
    },
    'analizar_pdf': {
        'descripcion': 'Análisis completo de PDFs con debug',
        'archivo': 'analizar_pdf_completo.py',
        'ejemplos': [
            'python herramientas_ia/analizar_pdf_completo.py "archivo.pdf"',
            'python herramientas_ia/analizar_pdf_completo.py --solo-ocr "archivo.pdf"',
            'Modo interactivo si se ejecuta sin argumentos'
        ]
    }
}

if __name__ == "__main__":
    mostrar_banner_herramienta("Herramientas de IA - Utilidades Comunes")