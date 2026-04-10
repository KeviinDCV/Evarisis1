#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KPICard - Tarjeta de Métricas Estilo Material Design
Componente reutilizable para mostrar indicadores clave de rendimiento

Características:
- Diseño profesional estilo Material Design
- Iconos personalizables (texto o emoji)
- Colores dinámicos por tipo de métrica
- Animaciones hover
- Actualización dinámica de valores
- Trending indicators (↑/↓/→)

Uso:
    from pyside6_ui.components.kpi_card import KPICard

    card = KPICard(
        title="Total Casos",
        value="1,245",
        icon="📁",
        color="#3b82f6",
        trend=12.5  # Opcional: % de cambio
    )
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property, QRect
from PySide6.QtGui import QFont, QColor
from typing import Optional

class KPICard(QFrame):
    """
    Tarjeta visual para mostrar métricas (KPIs)

    Args:
        title (str): Título de la métrica
        value (str): Valor de la métrica
        icon (str): Icono (emoji o texto corto)
        color (str): Color hex para el icono/valor
        trend (float, optional): Porcentaje de cambio (+/-) para indicador de tendencia
        parent (QWidget, optional): Widget padre
    """

    def __init__(
        self,
        title: str = "Métrica",
        value: str = "0",
        icon: str = "📊",
        color: str = "#3b82f6",
        trend: Optional[float] = None,
        parent=None
    ):
        super().__init__(parent)

        # Guardar propiedades
        self._title = title
        self._value = value
        self._icon = icon
        self._color = color
        self._trend = trend

        # Configurar el frame
        self.setProperty("class", "KPICard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setMinimumSize(200, 120)
        self.setMaximumHeight(150)

        # Crear layout principal
        self._create_ui()

        # Configurar cursor
        self.setCursor(Qt.PointingHandCursor)

        # Configurar animación hover
        self._setup_animations()

    def _create_ui(self):
        """Crea la interfaz de usuario de la tarjeta"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # === HEADER: Icono + Título ===
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        # Icono
        self.icon_label = QLabel(self._icon)
        self.icon_label.setStyleSheet(f"""
            font-size: 24pt;
            color: {self._color};
            background: transparent;
        """)
        self.icon_label.setFixedSize(40, 40)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Título
        self.title_label = QLabel(self._title)
        self.title_label.setProperty("class", "KPITitle")
        self.title_label.setWordWrap(True)

        # Spacer para empujar trending a la derecha
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label, 1)  # stretch=1

        # Trending indicator (si existe)
        if self._trend is not None:
            self.trend_label = self._create_trend_label(self._trend)
            header_layout.addWidget(self.trend_label)

        layout.addLayout(header_layout)

        # === VALOR ===
        self.value_label = QLabel(self._value)
        self.value_label.setProperty("class", "KPIValue")
        self.value_label.setStyleSheet(f"""
            color: {self._color};
            font-size: 36pt;
            font-weight: bold;
        """)
        self.value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout.addWidget(self.value_label)
        layout.addStretch()

    def _create_trend_label(self, trend_value: float) -> QLabel:
        """
        Crea el indicador de tendencia

        Args:
            trend_value: Porcentaje de cambio (+/-)

        Returns:
            QLabel con el indicador visual
        """
        # Determinar icono y color según tendencia
        if trend_value > 0:
            arrow = "↑"
            trend_color = "#10b981"  # Verde (success)
            prefix = "+"
        elif trend_value < 0:
            arrow = "↓"
            trend_color = "#ef4444"  # Rojo (danger)
            prefix = ""
        else:
            arrow = "→"
            trend_color = "#a1a1aa"  # Gris (neutral)
            prefix = ""

        label = QLabel(f"{arrow} {prefix}{trend_value:.1f}%")
        label.setStyleSheet(f"""
            color: {trend_color};
            font-size: 12pt;
            font-weight: bold;
            background: transparent;
        """)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        return label

    def _setup_animations(self):
        """Configura animaciones hover"""
        # Animación de elevación (simula sombra más grande)
        self._elevation_animation = QPropertyAnimation(self, b"geometry")
        self._elevation_animation.setDuration(200)
        self._elevation_animation.setEasingCurve(QEasingCurve.OutCubic)

        # Guardar geometría original
        self._original_geometry = None

    def enterEvent(self, event):
        """Evento al pasar el mouse"""
        # Guardar geometría original si no está guardada
        if self._original_geometry is None:
            self._original_geometry = self.geometry()

        # Animación sutil: elevar 2px
        current_rect = self.geometry()
        elevated_rect = QRect(
            current_rect.x(),
            current_rect.y() - 2,
            current_rect.width(),
            current_rect.height()
        )

        self._elevation_animation.setStartValue(current_rect)
        self._elevation_animation.setEndValue(elevated_rect)
        self._elevation_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Evento al salir el mouse"""
        if self._original_geometry:
            # Volver a posición original
            self._elevation_animation.setStartValue(self.geometry())
            self._elevation_animation.setEndValue(self._original_geometry)
            self._elevation_animation.start()

        super().leaveEvent(event)

    # === MÉTODOS PÚBLICOS DE ACTUALIZACIÓN ===

    def update_value(self, new_value: str):
        """
        Actualiza el valor mostrado en la tarjeta

        Args:
            new_value: Nuevo valor a mostrar
        """
        self._value = new_value
        self.value_label.setText(new_value)

    def update_trend(self, new_trend: float):
        """
        Actualiza el indicador de tendencia

        Args:
            new_trend: Nuevo porcentaje de cambio
        """
        self._trend = new_trend

        if hasattr(self, 'trend_label'):
            # Actualizar label existente
            if new_trend > 0:
                arrow = "↑"
                color = "#10b981"
                prefix = "+"
            elif new_trend < 0:
                arrow = "↓"
                color = "#ef4444"
                prefix = ""
            else:
                arrow = "→"
                color = "#a1a1aa"
                prefix = ""

            self.trend_label.setText(f"{arrow} {prefix}{new_trend:.1f}%")
            self.trend_label.setStyleSheet(f"""
                color: {color};
                font-size: 12pt;
                font-weight: bold;
                background: transparent;
            """)

    def update_title(self, new_title: str):
        """
        Actualiza el título de la tarjeta

        Args:
            new_title: Nuevo título
        """
        self._title = new_title
        self.title_label.setText(new_title)

    def update_icon(self, new_icon: str):
        """
        Actualiza el icono de la tarjeta

        Args:
            new_icon: Nuevo icono (emoji o texto)
        """
        self._icon = new_icon
        self.icon_label.setText(new_icon)

    def update_color(self, new_color: str):
        """
        Actualiza el color de la tarjeta

        Args:
            new_color: Nuevo color hex (ej: '#3b82f6')
        """
        self._color = new_color

        # Actualizar estilos del icono y valor
        self.icon_label.setStyleSheet(f"""
            font-size: 24pt;
            color: {new_color};
            background: transparent;
        """)

        self.value_label.setStyleSheet(f"""
            color: {new_color};
            font-size: 36pt;
            font-weight: bold;
        """)

    def set_data(self, title: str = None, value: str = None,
                 icon: str = None, color: str = None, trend: float = None):
        """
        Actualiza múltiples propiedades a la vez

        Args:
            title: Nuevo título (opcional)
            value: Nuevo valor (opcional)
            icon: Nuevo icono (opcional)
            color: Nuevo color (opcional)
            trend: Nueva tendencia (opcional)
        """
        if title is not None:
            self.update_title(title)
        if value is not None:
            self.update_value(value)
        if icon is not None:
            self.update_icon(icon)
        if color is not None:
            self.update_color(color)
        if trend is not None:
            self.update_trend(trend)

    # === GETTERS ===

    def get_value(self) -> str:
        """Obtiene el valor actual"""
        return self._value

    def get_title(self) -> str:
        """Obtiene el título actual"""
        return self._title

    def get_trend(self) -> Optional[float]:
        """Obtiene la tendencia actual"""
        return self._trend


# Ejemplo de uso y testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QWidget, QGridLayout

    app = QApplication(sys.argv)

    # Cargar tema darkly si existe
    try:
        from pyside6_ui.components.theme_manager import get_theme_manager
        theme_mgr = get_theme_manager()
        theme_mgr.load_theme('darkly')
    except:
        print("ThemeManager no disponible, usando estilos por defecto")

    # Ventana de prueba
    window = QWidget()
    window.setWindowTitle("KPICard - Prueba de Componente")
    window.resize(900, 400)

    # Layout grid para mostrar múltiples tarjetas
    layout = QGridLayout(window)
    layout.setSpacing(20)
    layout.setContentsMargins(30, 30, 30, 30)

    # Crear varias tarjetas de ejemplo
    card1 = KPICard("Total Casos", "1,245", "📁", "#3b82f6", trend=12.5)
    card2 = KPICard("Casos Malignos", "843", "☣️", "#ef4444", trend=-3.2)
    card3 = KPICard("Productividad", "+15%", "🚀", "#10b981", trend=15.0)
    card4 = KPICard("Pendientes IA", "56", "🤖", "#f59e0b", trend=0.0)

    # Agregar al layout
    layout.addWidget(card1, 0, 0)
    layout.addWidget(card2, 0, 1)
    layout.addWidget(card3, 1, 0)
    layout.addWidget(card4, 1, 1)

    window.show()

    # Demostración de actualización dinámica
    from PySide6.QtCore import QTimer

    def update_demo():
        """Actualiza valores cada 2 segundos para demo"""
        import random
        new_value = str(random.randint(1000, 2000))
        card1.update_value(new_value)

        new_trend = round(random.uniform(-10, 20), 1)
        card1.update_trend(new_trend)

    timer = QTimer()
    timer.timeout.connect(update_demo)
    timer.start(2000)  # Actualizar cada 2 segundos

    sys.exit(app.exec())
