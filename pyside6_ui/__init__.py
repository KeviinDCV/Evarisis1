#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS CIRUGÍA ONCOLÓGICA - PySide6 UI Module
Interfaz de usuario moderna basada en Qt6

Este módulo contiene toda la capa de presentación del sistema EVARISIS
migrada desde TTKBootstrap a PySide6 para obtener mejor rendimiento,
diseño profesional y capacidades avanzadas.

Estructura:
    - components/: Componentes reutilizables (KPI cards, navegación, tablas)
    - views/: Vistas principales (Welcome, Database, Dashboard, Audit IA)
    - dialogs/: Ventanas modales (Auditoría, Resultados, Configuración)
    - workers/: QThread workers para tareas pesadas (OCR, Export, Audit)
    - models/: Modelos Qt para arquitectura Model-View (Tablas, Filtros)
    - themes/: Hojas de estilo QSS (Darkly, Flatly, Medical)
    - resources/: Recursos Qt compilados (Iconos, Imágenes, Fuentes)

Versión: 7.0.0
Fecha: Noviembre 2025
"""

__version__ = "7.0.0-alpha"
__author__ = "Innovación y Desarrollo"
__email__ = "innovacionydesarrollo@correohuv.gov.co"

# Exportar clases principales para importación simplificada
__all__ = [
    "EvarisisApp",
    "ThemeManager",
    "KPICard",
    "SidebarNav",
    "DataTable",
]
