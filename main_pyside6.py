#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS CIRUGÍA ONCOLÓGICA - Punto de Entrada PySide6
Sistema de Gestión Oncológica Inteligente - Versión Qt6

Hospital Universitario del Valle
Versión: 7.0.0-alpha
"""

import sys
import logging
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Función principal de entrada"""
    logger.info("="*60)
    logger.info("EVARISIS CIRUGÍA ONCOLÓGICA v7.0.0-alpha (PySide6)")
    logger.info("Hospital Universitario del Valle")
    logger.info("="*60)

    try:
        # Importar y ejecutar la aplicación
        from pyside6_ui.app import run_app

        logger.info("Iniciando aplicación PySide6...")
        run_app()

    except ImportError as e:
        logger.error(f"Error de importación: {e}")
        logger.error("Asegúrate de que PySide6 esté instalado:")
        logger.error("  pip install PySide6>=6.6.0")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
