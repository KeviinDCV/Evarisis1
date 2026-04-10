#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChartWidget - Widget de gráficos con Matplotlib backend Qt
Wrapper profesional para gráficos científicos en Qt

Características:
- Backend Qt optimizado (FigureCanvasQTAgg)
- Toolbar de navegación integrado
- Temas coherentes con la app
- Actualización dinámica
- Soporte múltiples tipos (line, bar, pie, scatter)
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
import matplotlib
matplotlib.use('QtAgg')  # Backend Qt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
import pandas as pd
import numpy as np

class ChartWidget(QWidget):
    """
    Widget de gráficos con Matplotlib

    Args:
        parent (QWidget): Widget padre
        figsize (tuple): Tamaño de la figura (ancho, alto)
        dpi (int): DPI de la figura
    """

    def __init__(self, parent=None, figsize=(8, 6), dpi=100):
        super().__init__(parent)

        # Crear figura y canvas
        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.canvas = FigureCanvasQTAgg(self.figure)

        # Configurar estilo oscuro
        self._setup_dark_style()

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toolbar de navegación
        self.toolbar = NavigationToolbar2QT(self.canvas, self)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background-color: #252538;
                border: none;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                color: #ffffff;
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #3f3f55;
            }
        """)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        # Eje por defecto
        self.ax = self.figure.add_subplot(111)

    def _setup_dark_style(self):
        """Configura el estilo oscuro para los gráficos"""
        # Colores del tema darkly
        self.figure.patch.set_facecolor('#1e1e2e')

        # Configurar estilo matplotlib
        import matplotlib.pyplot as plt
        plt.style.use('dark_background')

    def clear(self):
        """Limpia el gráfico"""
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self._apply_dark_theme_to_axes()

    def _apply_dark_theme_to_axes(self):
        """Aplica tema oscuro a los ejes"""
        self.ax.set_facecolor('#252538')
        self.ax.tick_params(colors='#ffffff', which='both')
        self.ax.spines['bottom'].set_color('#3f3f55')
        self.ax.spines['left'].set_color('#3f3f55')
        self.ax.spines['top'].set_color('#3f3f55')
        self.ax.spines['right'].set_color('#3f3f55')
        self.ax.xaxis.label.set_color('#ffffff')
        self.ax.yaxis.label.set_color('#ffffff')
        self.ax.title.set_color('#ffffff')
        self.ax.grid(True, color='#3f3f55', alpha=0.3)

    def plot_line(self, x, y, label=None, color='#3b82f6', **kwargs):
        """
        Gráfico de línea

        Args:
            x: Datos del eje X
            y: Datos del eje Y
            label: Etiqueta de la serie
            color: Color de la línea
        """
        self.ax.plot(x, y, label=label, color=color, linewidth=2, **kwargs)
        self._apply_dark_theme_to_axes()

        if label:
            self.ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')

        self.canvas.draw()

    def plot_bar(self, x, y, label=None, color='#3b82f6', **kwargs):
        """
        Gráfico de barras

        Args:
            x: Categorías
            y: Valores
            label: Etiqueta
            color: Color de las barras
        """
        self.ax.bar(x, y, label=label, color=color, alpha=0.8, **kwargs)
        self._apply_dark_theme_to_axes()

        if label:
            self.ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')

        self.canvas.draw()

    def plot_pie(self, sizes, labels, colors=None, **kwargs):
        """
        Gráfico de torta

        Args:
            sizes: Tamaños de las porciones
            labels: Etiquetas
            colors: Colores personalizados
        """
        if colors is None:
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

        self.ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                   startangle=90, textprops={'color': '#ffffff'}, **kwargs)
        self.ax.axis('equal')

        self.canvas.draw()

    def plot_scatter(self, x, y, label=None, color='#3b82f6', **kwargs):
        """
        Gráfico de dispersión

        Args:
            x: Datos eje X
            y: Datos eje Y
            label: Etiqueta
            color: Color de los puntos
        """
        self.ax.scatter(x, y, label=label, color=color, alpha=0.6, s=50, **kwargs)
        self._apply_dark_theme_to_axes()

        if label:
            self.ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')

        self.canvas.draw()

    def set_title(self, title: str):
        """Establece el título del gráfico"""
        self.ax.set_title(title, color='#ffffff', fontsize=14, fontweight='bold')
        self.canvas.draw()

    def set_labels(self, xlabel: str, ylabel: str):
        """Establece las etiquetas de los ejes"""
        self.ax.set_xlabel(xlabel, color='#ffffff', fontsize=12)
        self.ax.set_ylabel(ylabel, color='#ffffff', fontsize=12)
        self.canvas.draw()

    def refresh(self):
        """Refresca el canvas"""
        self.canvas.draw()


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget

    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("ChartWidget - Demo")
    window.resize(1000, 700)

    tabs = QTabWidget()
    window.setCentralWidget(tabs)

    # Tab 1: Gráfico de línea
    chart1 = ChartWidget()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    chart1.plot_line(x, y, label='sen(x)', color='#3b82f6')
    chart1.set_title('Gráfico de Línea')
    chart1.set_labels('X', 'sen(X)')
    tabs.addTab(chart1, "Línea")

    # Tab 2: Gráfico de barras
    chart2 = ChartWidget()
    categories = ['Cirugía', 'Oncología', 'Patología', 'Medicina Interna']
    values = [120, 85, 95, 70]
    chart2.plot_bar(categories, values, color='#10b981')
    chart2.set_title('Casos por Servicio')
    chart2.set_labels('Servicio', 'Número de Casos')
    tabs.addTab(chart2, "Barras")

    # Tab 3: Gráfico de torta
    chart3 = ChartWidget()
    sizes = [843, 402]
    labels = ['Malignos', 'Benignos']
    colors = ['#ef4444', '#10b981']
    chart3.plot_pie(sizes, labels, colors=colors)
    chart3.set_title('Distribución Malignidad')
    tabs.addTab(chart3, "Torta")

    window.show()

    sys.exit(app.exec())
