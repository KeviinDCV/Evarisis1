#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WelcomeView - Pantalla de Bienvenida Mejorada
Vista inicial con estadísticas del sistema, accesos rápidos y casos recientes

Características:
- Estadísticas en tiempo real del sistema
- Accesos directos a funciones principales
- Últimos casos procesados
- Alertas y notificaciones
- Información institucional
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QGridLayout, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Optional
import pandas as pd


class WelcomeView(QWidget):
    """
    Pantalla de bienvenida mejorada con estadísticas y accesos rápidos

    Signals:
        navigation_requested(str): Solicita navegación a otra vista
    """

    # Signals
    navigation_requested = Signal(str)  # Emite ID de navegación (database, dashboard, etc.)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")

        # Estado
        self.df = None  # DataFrame con datos del sistema

        # Crear UI
        self._create_ui()

        # Cargar datos iniciales
        self.load_system_data()

    def _create_ui(self):
        """Crea la interfaz de bienvenida mejorada"""
        # Scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Widget contenedor
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # Header institucional
        header = self._create_header()
        layout.addWidget(header)

        # Estadísticas del sistema (4 KPIs)
        stats = self._create_statistics()
        layout.addWidget(stats)

        # Accesos rápidos
        quick_access = self._create_quick_access()
        layout.addWidget(quick_access)

        # Layout de 2 columnas
        columns_layout = QHBoxLayout()

        # Columna izquierda: Casos recientes
        recent_cases = self._create_recent_cases()
        columns_layout.addWidget(recent_cases, 3)

        # Columna derecha: Alertas y notificaciones
        alerts = self._create_alerts()
        columns_layout.addWidget(alerts, 2)

        layout.addLayout(columns_layout)

        # Footer con información
        footer = self._create_footer()
        layout.addWidget(footer)

        layout.addStretch()

        # Configurar scroll
        scroll.setWidget(container)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

    def _create_header(self) -> QWidget:
        """Crea el header con título e icono"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1e3a8a, stop:1 #1e40af);
                border-radius: 12px;
                padding: 30px;
            }
        """)

        layout = QHBoxLayout(header)

        # Icono y texto
        text_layout = QVBoxLayout()

        title = QLabel("🏥 EVARISIS")
        title.setStyleSheet("font-size: 42pt; font-weight: bold; color: white; background: transparent;")

        subtitle = QLabel("Sistema Inteligente de Gestión Oncológica")
        subtitle.setStyleSheet("font-size: 16pt; color: #dbeafe; background: transparent;")

        institution = QLabel("Hospital Universitario del Valle")
        institution.setStyleSheet("font-size: 12pt; color: #93c5fd; background: transparent; margin-top: 5px;")

        text_layout.addWidget(title)
        text_layout.addWidget(subtitle)
        text_layout.addWidget(institution)

        layout.addLayout(text_layout)
        layout.addStretch()

        # Versión
        version_label = QLabel("v6.2.14")
        version_label.setStyleSheet("""
            background: rgba(255, 255, 255, 0.2);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 11pt;
            font-weight: bold;
        """)
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        return header

    def _create_statistics(self) -> QWidget:
        """Crea las tarjetas de estadísticas"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)

        layout = QGridLayout(stats_frame)
        layout.setSpacing(15)

        # Crear referencia a labels para actualización dinámica
        self.stat_labels = {}

        stats = [
            ("total_casos", "📊 Total de Casos", "0", "#3b82f6"),
            ("casos_mes", "📅 Casos del Mes", "0", "#10b981"),
            ("completitud_promedio", "✅ Completitud Promedio", "0%", "#f59e0b"),
            ("casos_pendientes", "⏳ Casos Pendientes", "0", "#ef4444"),
        ]

        for idx, (key, title, value, color) in enumerate(stats):
            row = idx // 2
            col = idx % 2

            card = self._create_stat_card(title, value, color)
            self.stat_labels[key] = card['value_label']
            layout.addWidget(card['frame'], row, col)

        return stats_frame

    def _create_stat_card(self, title: str, value: str, color: str) -> dict:
        """Crea una tarjeta de estadística"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: #252538;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; background: transparent;")

        value_label = QLabel(value)
        value_label.setStyleSheet(f"color: {color}; font-size: 32pt; font-weight: bold; background: transparent;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        return {'frame': card, 'value_label': value_label}

    def _create_quick_access(self) -> QWidget:
        """Crea panel de accesos rápidos"""
        access_frame = QFrame()
        access_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(access_frame)
        layout.setSpacing(15)

        # Título
        title = QLabel("⚡ Accesos Rápidos")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffffff; background: transparent;")
        layout.addWidget(title)

        # Grid de botones
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(10)

        quick_actions = [
            ("📥 Importar PDFs", "database", "#3b82f6"),
            ("📊 Ver Dashboard", "dashboard", "#10b981"),
            ("🤖 Auditoría IA", "audit", "#8b5cf6"),
            ("🌐 Cargar a QHORTE", "web", "#f59e0b"),
        ]

        for idx, (text, nav_id, color) in enumerate(quick_actions):
            row = idx // 2
            col = idx % 2

            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-size: 11pt;
                    font-weight: bold;
                    min-height: 50px;
                }}
                QPushButton:hover {{
                    background-color: {self._lighten_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self._darken_color(color)};
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=nav_id: self.navigation_requested.emit(n))

            buttons_layout.addWidget(btn, row, col)

        layout.addLayout(buttons_layout)

        return access_frame

    def _create_recent_cases(self) -> QWidget:
        """Crea panel de casos recientes"""
        recent_frame = QFrame()
        recent_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(recent_frame)
        layout.setSpacing(15)

        # Título
        title_layout = QHBoxLayout()
        title = QLabel("📋 Casos Recientes")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffffff; background: transparent;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Botón ver todos
        view_all_btn = QPushButton("Ver Todos →")
        view_all_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #3b82f6;
                border: none;
                font-size: 10pt;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #60a5fa;
            }
        """)
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.clicked.connect(lambda: self.navigation_requested.emit('database'))
        title_layout.addWidget(view_all_btn)

        layout.addLayout(title_layout)

        # Tabla de casos recientes
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(3)
        self.recent_table.setHorizontalHeaderLabels(["Número", "Fecha", "Completitud"])
        self.recent_table.setMaximumHeight(250)
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        self.recent_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
            }
            QHeaderView::section {
                background-color: #2a2a3e;
                color: #ffffff;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
            }
        """)

        layout.addWidget(self.recent_table)

        return recent_frame

    def _create_alerts(self) -> QWidget:
        """Crea panel de alertas y notificaciones"""
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(alerts_frame)
        layout.setSpacing(15)

        # Título
        title = QLabel("🔔 Notificaciones")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffffff; background: transparent;")
        layout.addWidget(title)

        # Contenedor de alertas
        self.alerts_container = QVBoxLayout()
        self.alerts_container.setSpacing(10)
        layout.addLayout(self.alerts_container)

        # Alertas de ejemplo (se actualizarán dinámicamente)
        self._add_sample_alerts()

        layout.addStretch()

        return alerts_frame

    def _add_sample_alerts(self):
        """Agrega alertas de ejemplo (se reemplazarán con datos reales)"""
        # Limpiar alertas existentes
        while self.alerts_container.count():
            item = self.alerts_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Alert de información
        info_alert = self._create_alert(
            "ℹ️ Sistema Actualizado",
            "EVARISIS v6.2.14 instalado correctamente",
            "#3b82f6"
        )
        self.alerts_container.addWidget(info_alert)

        # Alert de advertencia (placeholder - se calculará con datos reales)
        warning_alert = self._create_alert(
            "⚠️ Casos Incompletos",
            "Calculando casos con completitud <80%...",
            "#f59e0b"
        )
        self.alerts_container.addWidget(warning_alert)
        self.warning_alert_label = warning_alert  # Guardar referencia para actualizar

    def _create_alert(self, title: str, message: str, color: str) -> QWidget:
        """Crea una tarjeta de alerta"""
        alert = QFrame()
        alert.setStyleSheet(f"""
            QFrame {{
                background-color: #1e1e2e;
                border-left: 3px solid {color};
                border-radius: 6px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(alert)
        layout.setSpacing(5)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10pt; background: transparent;")

        message_label = QLabel(message)
        message_label.setStyleSheet("color: #a1a1aa; font-size: 9pt; background: transparent;")
        message_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(message_label)

        # Guardar referencia al label de mensaje para actualizaciones
        alert.message_label = message_label

        return alert

    def _create_footer(self) -> QWidget:
        """Crea el footer con información adicional"""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 8px;
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(footer)

        # Información del sistema
        info_text = QLabel(
            "💡 Consejo: Usa la auditoría IA para validar casos antes de cargarlos a QHORTE"
        )
        info_text.setStyleSheet("color: #a1a1aa; font-size: 10pt; background: transparent;")
        info_text.setWordWrap(True)

        layout.addWidget(info_text)
        layout.addStretch()

        return footer

    def _lighten_color(self, color: str) -> str:
        """Aclara un color hex para hover"""
        color_map = {
            "#3b82f6": "#60a5fa",
            "#10b981": "#34d399",
            "#8b5cf6": "#a78bfa",
            "#f59e0b": "#fbbf24",
        }
        return color_map.get(color, color)

    def _darken_color(self, color: str) -> str:
        """Oscurece un color hex para pressed"""
        color_map = {
            "#3b82f6": "#2563eb",
            "#10b981": "#059669",
            "#8b5cf6": "#7c3aed",
            "#f59e0b": "#d97706",
        }
        return color_map.get(color, color)

    def load_system_data(self):
        """Carga datos del sistema y actualiza la vista"""
        try:
            from core.database_manager import get_all_records_as_dataframe
            from datetime import datetime

            # Cargar datos
            self.df = get_all_records_as_dataframe()

            if self.df.empty:
                self._update_stats_empty()
                return

            # Calcular estadísticas
            total_casos = len(self.df)

            # Casos del mes actual
            date_col = None
            for col in ['Fecha de Ingreso', 'Fecha Ingreso', 'fecha_ingreso']:
                if col in self.df.columns:
                    date_col = col
                    break

            casos_mes = 0
            if date_col:
                try:
                    current_month = datetime.now().month
                    current_year = datetime.now().year
                    df_dates = pd.to_datetime(self.df[date_col], errors='coerce')
                    casos_mes = len(df_dates[
                        (df_dates.dt.month == current_month) &
                        (df_dates.dt.year == current_year)
                    ])
                except:
                    pass

            # Completitud promedio
            completitud_promedio = 0.0
            if 'Completitud (%)' in self.df.columns:
                try:
                    completitud_promedio = pd.to_numeric(
                        self.df['Completitud (%)'],
                        errors='coerce'
                    ).mean()
                except:
                    pass

            # Casos pendientes (<80%)
            casos_pendientes = 0
            if 'Completitud (%)' in self.df.columns:
                try:
                    comp_numeric = pd.to_numeric(self.df['Completitud (%)'], errors='coerce')
                    casos_pendientes = len(comp_numeric[comp_numeric < 80])
                except:
                    pass

            # Actualizar stats
            self.stat_labels['total_casos'].setText(str(total_casos))
            self.stat_labels['casos_mes'].setText(str(casos_mes))
            self.stat_labels['completitud_promedio'].setText(f"{completitud_promedio:.1f}%")
            self.stat_labels['casos_pendientes'].setText(str(casos_pendientes))

            # Actualizar casos recientes
            self._update_recent_cases()

            # Actualizar alertas
            self._update_alerts(casos_pendientes, completitud_promedio)

        except Exception as e:
            self._update_stats_empty()

    def _update_stats_empty(self):
        """Actualiza estadísticas cuando no hay datos"""
        self.stat_labels['total_casos'].setText("0")
        self.stat_labels['casos_mes'].setText("0")
        self.stat_labels['completitud_promedio'].setText("0%")
        self.stat_labels['casos_pendientes'].setText("0")

    def _update_recent_cases(self):
        """Actualiza tabla de casos recientes"""
        self.recent_table.setRowCount(0)

        if self.df is None or self.df.empty:
            return

        # Buscar columnas
        col_numero = None
        col_fecha = None
        col_completitud = None

        for col in self.df.columns:
            col_lower = col.lower()
            if 'numero' in col_lower and 'peticion' in col_lower:
                col_numero = col
            elif 'fecha' in col_lower and 'ingreso' in col_lower:
                col_fecha = col
            elif 'completitud' in col_lower:
                col_completitud = col

        # Mostrar últimos 5 casos
        df_recent = self.df.tail(5)

        for idx, row in df_recent.iterrows():
            row_idx = self.recent_table.rowCount()
            self.recent_table.insertRow(row_idx)

            # Número
            numero = row.get(col_numero, 'N/A') if col_numero else 'N/A'
            item_num = QTableWidgetItem(str(numero))
            self.recent_table.setItem(row_idx, 0, item_num)

            # Fecha
            fecha = row.get(col_fecha, 'N/A') if col_fecha else 'N/A'
            item_fecha = QTableWidgetItem(str(fecha)[:10])  # Solo fecha
            self.recent_table.setItem(row_idx, 1, item_fecha)

            # Completitud
            if col_completitud:
                try:
                    comp = float(row.get(col_completitud, 0))
                    item_comp = QTableWidgetItem(f"{comp:.1f}%")

                    # Color coding
                    if comp >= 95:
                        item_comp.setForeground(QColor(16, 185, 129))
                    elif comp >= 80:
                        item_comp.setForeground(QColor(245, 158, 11))
                    else:
                        item_comp.setForeground(QColor(239, 68, 68))

                    self.recent_table.setItem(row_idx, 2, item_comp)
                except:
                    self.recent_table.setItem(row_idx, 2, QTableWidgetItem("N/A"))
            else:
                self.recent_table.setItem(row_idx, 2, QTableWidgetItem("N/A"))

    def _update_alerts(self, casos_pendientes: int, completitud_promedio: float):
        """Actualiza alertas con datos reales"""
        # Actualizar alert de casos incompletos
        if hasattr(self, 'warning_alert_label') and self.warning_alert_label:
            message_label = self.warning_alert_label.message_label

            if casos_pendientes > 0:
                message_label.setText(
                    f"Hay {casos_pendientes} casos con completitud <80%. "
                    "Revisa el dashboard para más detalles."
                )
            else:
                message_label.setText("¡Excelente! Todos los casos tienen completitud ≥80%")


# Ejemplo de uso standalone
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    # Cargar tema
    try:
        from pyside6_ui.components.theme_manager import get_theme_manager
        theme_mgr = get_theme_manager()
        theme_mgr.load_theme('darkly')
    except:
        pass

    window = QMainWindow()
    window.setWindowTitle("WelcomeView - Demo")
    window.resize(1400, 900)

    welcome = WelcomeView()

    # Conectar signal
    def on_navigation(nav_id):
        print(f"Navegación solicitada: {nav_id}")

    welcome.navigation_requested.connect(on_navigation)

    window.setCentralWidget(welcome)
    window.show()

    sys.exit(app.exec())
