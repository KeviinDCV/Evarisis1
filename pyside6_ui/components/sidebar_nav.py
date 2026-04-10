#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SidebarNav - Navegación Lateral Profesional
Componente de navegación lateral con botones exclusivos y animaciones

Características:
- Navegación exclusiva (radio-button style)
- Animaciones smooth
- Iconos + texto
- Estados visuales (hover/checked/pressed)
- Signals Qt para navegación
- Colapsable (opcional)

Uso:
    from pyside6_ui.components.sidebar_nav import SidebarNav, NavButton

    sidebar = SidebarNav()
    sidebar.add_nav_button("🏠", "Inicio", "home")
    sidebar.add_nav_button("🗄️", "Base de Datos", "database")

    # Conectar signal
    sidebar.nav_changed.connect(on_navigation)
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QWidget
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QSize
from PySide6.QtGui import QFont
from typing import List, Dict

class NavButton(QPushButton):
    """
    Botón de navegación personalizado

    Args:
        icon (str): Icono (emoji o texto)
        text (str): Texto del botón
        nav_id (str): ID único de navegación
        parent (QWidget, optional): Widget padre
    """

    def __init__(self, icon: str, text: str, nav_id: str, parent=None):
        super().__init__(f"  {icon}   {text}", parent)

        self.nav_id = nav_id
        self.icon = icon
        self.label_text = text

        # Configurar propiedades
        self.setProperty("class", "NavButton")
        self.setCheckable(True)  # Permite estado "checked"
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(50)

        # Fuente
        font = QFont("Segoe UI", 11)
        self.setFont(font)

    def get_nav_id(self) -> str:
        """Obtiene el ID de navegación"""
        return self.nav_id


class SidebarNav(QFrame):
    """
    Sidebar de navegación con botones exclusivos

    Signals:
        nav_changed(str): Emitido cuando cambia la navegación (nav_id)
    """

    # Signal emitido cuando cambia la navegación
    nav_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Lista de botones de navegación
        self._nav_buttons: List[NavButton] = []

        # ID de navegación actual
        self._current_nav = None

        # Configurar el frame
        self.setObjectName("SidebarFrame")
        self.setMinimumWidth(240)
        self.setMaximumWidth(240)

        # Crear layout
        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz del sidebar"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 20, 10, 20)
        self.main_layout.setSpacing(8)

        # Header del sidebar (opcional)
        header_label = QLabel("HUV ONCOLOGÍA")
        header_label.setStyleSheet("""
            font-size: 14pt;
            font-weight: bold;
            color: #3b82f6;
            padding: 10px;
        """)
        header_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(header_label)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #3f3f55; margin: 10px 0px;")
        self.main_layout.addWidget(separator)

        # Spacer al final (se llenará con botones dinámicamente)
        self.main_layout.addStretch()

        # Footer (versión)
        self.footer_label = QLabel("v7.0.0 Beta")
        self.footer_label.setStyleSheet("""
            color: #6b7280;
            font-size: 9pt;
            padding: 5px;
        """)
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.footer_label)

    def add_nav_button(self, icon: str, text: str, nav_id: str) -> NavButton:
        """
        Añade un botón de navegación

        Args:
            icon: Icono (emoji o texto)
            text: Texto del botón
            nav_id: ID único de navegación

        Returns:
            NavButton: Botón creado
        """
        # Crear botón
        btn = NavButton(icon, text, nav_id, self)

        # Conectar click
        btn.clicked.connect(lambda: self._on_nav_clicked(btn))

        # Agregar a lista
        self._nav_buttons.append(btn)

        # Insertar antes del stretch (penúltimo elemento antes del footer)
        insert_index = self.main_layout.count() - 2  # Antes de stretch y footer
        self.main_layout.insertWidget(insert_index, btn)

        # Si es el primer botón, activarlo
        if len(self._nav_buttons) == 1:
            btn.setChecked(True)
            self._current_nav = nav_id

        return btn

    def _on_nav_clicked(self, clicked_button: NavButton):
        """
        Maneja el click en un botón de navegación

        Args:
            clicked_button: Botón clickeado
        """
        # Desmarcar todos los botones
        for btn in self._nav_buttons:
            btn.setChecked(False)

        # Marcar el botón clickeado
        clicked_button.setChecked(True)

        # Actualizar navegación actual
        self._current_nav = clicked_button.get_nav_id()

        # Emitir signal
        self.nav_changed.emit(self._current_nav)

    def set_active_nav(self, nav_id: str):
        """
        Establece la navegación activa programáticamente

        Args:
            nav_id: ID de navegación a activar
        """
        for btn in self._nav_buttons:
            if btn.get_nav_id() == nav_id:
                btn.setChecked(True)
                self._current_nav = nav_id
                self.nav_changed.emit(nav_id)
            else:
                btn.setChecked(False)

    def get_current_nav(self) -> str:
        """
        Obtiene el ID de navegación actual

        Returns:
            str: ID de navegación actual
        """
        return self._current_nav

    def set_footer_text(self, text: str):
        """
        Actualiza el texto del footer

        Args:
            text: Nuevo texto para el footer
        """
        self.footer_label.setText(text)

    def remove_nav_button(self, nav_id: str):
        """
        Elimina un botón de navegación

        Args:
            nav_id: ID del botón a eliminar
        """
        for btn in self._nav_buttons[:]:  # Copiar lista para iterar
            if btn.get_nav_id() == nav_id:
                self.main_layout.removeWidget(btn)
                btn.deleteLater()
                self._nav_buttons.remove(btn)
                break

    def clear_nav_buttons(self):
        """Elimina todos los botones de navegación"""
        for btn in self._nav_buttons[:]:
            self.main_layout.removeWidget(btn)
            btn.deleteLater()

        self._nav_buttons.clear()
        self._current_nav = None


# Ejemplo de uso y testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel

    app = QApplication(sys.argv)

    # Cargar tema
    try:
        from pyside6_ui.components.theme_manager import get_theme_manager
        theme_mgr = get_theme_manager()
        theme_mgr.load_theme('darkly')
    except:
        print("ThemeManager no disponible")

    # Ventana principal
    window = QMainWindow()
    window.setWindowTitle("SidebarNav - Prueba de Componente")
    window.resize(800, 600)

    # Widget central
    central_widget = QWidget()
    window.setCentralWidget(central_widget)

    # Layout horizontal (sidebar + content)
    layout = QHBoxLayout(central_widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    # Crear sidebar
    sidebar = SidebarNav()

    # Añadir botones de navegación
    sidebar.add_nav_button("🏠", "Inicio", "home")
    sidebar.add_nav_button("🗄️", "Base de Datos", "database")
    sidebar.add_nav_button("📈", "Dashboard", "dashboard")
    sidebar.add_nav_button("🤖", "Auditoría IA", "audit")
    sidebar.add_nav_button("🌐", "QHORTE Web", "web")

    # Área de contenido
    content_area = QLabel("Selecciona una opción del menú")
    content_area.setStyleSheet("""
        background-color: #1e1e2e;
        color: #ffffff;
        font-size: 24pt;
        padding: 50px;
    """)
    content_area.setAlignment(Qt.AlignCenter)

    # Conectar signal de navegación
    def on_nav_changed(nav_id):
        texts = {
            'home': "🏠 Pantalla de Inicio",
            'database': "🗄️ Base de Datos - Gestión de Casos",
            'dashboard': "📈 Dashboard - Métricas y Análisis",
            'audit': "🤖 Auditoría con IA",
            'web': "🌐 Interoperabilidad QHORTE"
        }
        content_area.setText(texts.get(nav_id, "Vista no encontrada"))
        print(f"Navegación cambiada a: {nav_id}")

    sidebar.nav_changed.connect(on_nav_changed)

    # Agregar al layout
    layout.addWidget(sidebar)
    layout.addWidget(content_area, 1)  # stretch=1 para que ocupe el resto

    window.show()

    sys.exit(app.exec())
