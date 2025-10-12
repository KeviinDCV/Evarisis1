# -*- coding: utf-8 -*-
"""
EVARISIS Gestor HUV - Módulos Principales (Core)
Arquitectura modular refactorizada v4.1

Módulos disponibles:
- processors: Procesadores OCR y segmentación
- extractors: Extractores de datos (paciente, médico, biomarcadores)
- utils: Utilidades de procesamiento de texto
- database_manager: Gestor de base de datos SQLite
- unified_extractor: Interfaz unificada de extracción
- calendario: Calendario inteligente con tooltips
- huv_web_automation: Automatización web con Selenium
- enhanced_export_system: Sistema de exportación mejorado
- enhanced_database_dashboard: Dashboard de base de datos
"""

__version__ = "4.1.0"
__author__ = "EVARISIS Team"

# Imports principales para facilitar el acceso
from .database_manager import *
from .unified_extractor import extract_ihq_data, process_ihq_paths

__all__ = [
    'database_manager',
    'unified_extractor',
    'processors',
    'extractors',
    'utils',
    'huv_web_automation',
    'calendario',
    'enhanced_export_system',
    'enhanced_database_dashboard'
]