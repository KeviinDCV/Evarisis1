#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThemeManager - Sistema de Temas Dinámicos para EVARISIS
Gestiona la carga y aplicación de temas QSS (Qt Style Sheets)

Características:
- Carga dinámica de temas desde archivos .qss
- Hot-reload de temas sin reiniciar app
- Acceso a paleta de colores del tema actual
- Signal cuando cambia el tema
- Soporte para temas custom

Uso:
    from pyside6_ui.components.theme_manager import ThemeManager

    theme_mgr = ThemeManager()
    theme_mgr.load_theme('darkly')

    # Obtener color del tema
    primary_color = theme_mgr.get_color('primary')

    # Conectar a signal de cambio
    theme_mgr.theme_changed.connect(on_theme_changed)
"""

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor
from pathlib import Path
import logging

class ThemeManager(QObject):
    """
    Gestor de temas QSS para la aplicación

    Signals:
        theme_changed(str): Emitido cuando se cambia el tema (nombre del tema)
    """

    # Signal emitido cuando cambia el tema
    theme_changed = Signal(str)

    # Mapeo de temas disponibles
    THEMES = {
        'darkly': 'darkly.qss',
        'flatly': 'flatly.qss',
        'medical': 'medical.qss',
        'custom': 'custom.qss'
    }

    # Paletas de colores por tema
    COLOR_PALETTES = {
        'darkly': {
            'primary': '#3b82f6',
            'secondary': '#8b5cf6',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#06b6d4',
            'background': '#1e1e2e',
            'surface': '#252538',
            'surface-variant': '#2a2a3e',
            'border': '#3f3f55',
            'text': '#ffffff',
            'text-muted': '#a1a1aa',
            'text-disabled': '#6b7280',
        },
        'flatly': {
            'primary': '#2c3e50',
            'secondary': '#95a5a6',
            'success': '#18bc9c',
            'danger': '#e74c3c',
            'warning': '#f39c12',
            'info': '#3498db',
            'background': '#ffffff',
            'surface': '#ecf0f1',
            'surface-variant': '#bdc3c7',
            'border': '#95a5a6',
            'text': '#2c3e50',
            'text-muted': '#7f8c8d',
            'text-disabled': '#95a5a6',
        },
        'medical': {
            'primary': '#0ea5e9',
            'secondary': '#6366f1',
            'success': '#14b8a6',
            'danger': '#f43f5e',
            'warning': '#f59e0b',
            'info': '#0891b2',
            'background': '#f0f4f8',
            'surface': '#ffffff',
            'surface-variant': '#e2e8f0',
            'border': '#cbd5e1',
            'text': '#1e293b',
            'text-muted': '#64748b',
            'text-disabled': '#94a3b8',
        }
    }

    def __init__(self):
        """Inicializa el gestor de temas"""
        super().__init__()
        self.current_theme = 'darkly'  # Tema por defecto
        self._themes_dir = Path(__file__).parent.parent / 'themes'

        # Crear directorio de temas si no existe
        self._themes_dir.mkdir(parents=True, exist_ok=True)

        logging.info(f"ThemeManager inicializado. Directorio temas: {self._themes_dir}")

    def load_theme(self, theme_name: str) -> bool:
        """
        Carga y aplica un tema a la aplicación

        Args:
            theme_name: Nombre del tema ('darkly', 'flatly', 'medical', 'custom')

        Returns:
            bool: True si el tema se cargó correctamente, False en caso contrario

        Raises:
            FileNotFoundError: Si el archivo de tema no existe
        """
        if theme_name not in self.THEMES:
            logging.error(f"Tema '{theme_name}' no encontrado. Temas disponibles: {list(self.THEMES.keys())}")
            return False

        theme_file = self.THEMES[theme_name]
        theme_path = self._themes_dir / theme_file

        if not theme_path.exists():
            logging.error(f"Archivo de tema no encontrado: {theme_path}")
            return False

        try:
            # Leer el archivo QSS
            with open(theme_path, 'r', encoding='utf-8') as f:
                qss = f.read()

            # Aplicar el stylesheet a la aplicación
            app = QApplication.instance()
            if app:
                app.setStyleSheet(qss)
                self.current_theme = theme_name

                logging.info(f"Tema '{theme_name}' cargado exitosamente desde {theme_path}")

                # Emitir signal de cambio de tema
                self.theme_changed.emit(theme_name)

                return True
            else:
                logging.error("No hay instancia de QApplication activa")
                return False

        except Exception as e:
            logging.error(f"Error cargando tema '{theme_name}': {e}")
            return False

    def get_color(self, key: str) -> str:
        """
        Obtiene un color de la paleta del tema actual

        Args:
            key: Clave del color ('primary', 'success', 'danger', etc.)

        Returns:
            str: Código hexadecimal del color (ej: '#3b82f6')

        Example:
            >>> theme_mgr.get_color('primary')
            '#3b82f6'
        """
        palette = self.COLOR_PALETTES.get(self.current_theme, {})
        color = palette.get(key, '#000000')

        if color == '#000000' and key != 'background':
            logging.warning(f"Color '{key}' no encontrado en tema '{self.current_theme}', usando negro")

        return color

    def get_qcolor(self, key: str) -> QColor:
        """
        Obtiene un color como QColor del tema actual

        Args:
            key: Clave del color

        Returns:
            QColor: Objeto QColor
        """
        hex_color = self.get_color(key)
        return QColor(hex_color)

    def get_current_theme(self) -> str:
        """
        Obtiene el nombre del tema actual

        Returns:
            str: Nombre del tema actual
        """
        return self.current_theme

    def get_available_themes(self) -> list:
        """
        Obtiene lista de temas disponibles

        Returns:
            list: Lista de nombres de temas disponibles
        """
        return list(self.THEMES.keys())

    def reload_current_theme(self):
        """
        Recarga el tema actual (útil para desarrollo)
        """
        self.load_theme(self.current_theme)
        logging.info(f"Tema '{self.current_theme}' recargado")

    def create_custom_theme(self, name: str, colors: dict, base_theme: str = 'darkly'):
        """
        Crea un tema personalizado basado en un tema existente

        Args:
            name: Nombre del nuevo tema
            colors: Diccionario de colores a sobrescribir
            base_theme: Tema base a usar como plantilla

        Example:
            >>> theme_mgr.create_custom_theme(
            ...     'mi_tema',
            ...     {'primary': '#ff0000', 'success': '#00ff00'},
            ...     base_theme='darkly'
            ... )
        """
        # Copiar paleta del tema base
        if base_theme in self.COLOR_PALETTES:
            new_palette = self.COLOR_PALETTES[base_theme].copy()
            new_palette.update(colors)
            self.COLOR_PALETTES[name] = new_palette

            # Leer QSS del tema base
            base_theme_path = self._themes_dir / self.THEMES.get(base_theme, 'darkly.qss')

            if base_theme_path.exists():
                with open(base_theme_path, 'r', encoding='utf-8') as f:
                    qss = f.read()

                # Reemplazar colores en el QSS
                for key, color in colors.items():
                    old_color = self.COLOR_PALETTES[base_theme].get(key, '')
                    if old_color:
                        qss = qss.replace(old_color, color)

                # Guardar nuevo tema
                custom_theme_path = self._themes_dir / f"{name}.qss"
                with open(custom_theme_path, 'w', encoding='utf-8') as f:
                    f.write(qss)

                # Agregar a temas disponibles
                self.THEMES[name] = f"{name}.qss"

                logging.info(f"Tema personalizado '{name}' creado basado en '{base_theme}'")
            else:
                logging.error(f"Tema base '{base_theme}' no encontrado")
        else:
            logging.error(f"Tema base '{base_theme}' no existe en COLOR_PALETTES")


# Instancia global del gestor de temas (singleton)
_theme_manager_instance = None

def get_theme_manager() -> ThemeManager:
    """
    Obtiene la instancia global del ThemeManager (patrón Singleton)

    Returns:
        ThemeManager: Instancia única del gestor de temas
    """
    global _theme_manager_instance
    if _theme_manager_instance is None:
        _theme_manager_instance = ThemeManager()
    return _theme_manager_instance


# Ejemplo de uso
if __name__ == "__main__":
    import sys

    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Crear aplicación Qt
    app = QApplication(sys.argv)

    # Obtener gestor de temas
    theme_mgr = get_theme_manager()

    # Probar carga de temas
    print(f"Temas disponibles: {theme_mgr.get_available_themes()}")
    print(f"Tema actual: {theme_mgr.get_current_theme()}")

    # Cargar tema darkly
    if theme_mgr.load_theme('darkly'):
        print(f"Tema 'darkly' cargado correctamente")
        print(f"Color primary: {theme_mgr.get_color('primary')}")
        print(f"Color success: {theme_mgr.get_color('success')}")
        print(f"Color danger: {theme_mgr.get_color('danger')}")

    # Conectar a signal
    def on_theme_changed(theme_name):
        print(f"SIGNAL: Tema cambiado a '{theme_name}'")

    theme_mgr.theme_changed.connect(on_theme_changed)

    # Probar hot-reload
    theme_mgr.reload_current_theme()
