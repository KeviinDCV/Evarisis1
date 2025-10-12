# -*- coding: utf-8 -*-
"""
EVARISIS Gestor HUV - Configuración del Sistema
Contiene solo configuración de sistema (rutas OCR, versión)

NOTA: Todas las constantes de comportamiento fueron movidas a core/
para centralizar la lógica del sistema.

Versión: 4.1.0
"""

__version__ = "4.1.0"

# Solo imports de información de versión
from .version_info import *

__all__ = [
    'version_info'
]