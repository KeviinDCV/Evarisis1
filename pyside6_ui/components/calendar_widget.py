#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CalendarWidget - Calendario inteligente con integración a BD
Muestra casos por fecha con tooltips y color coding

Características:
- QCalendarWidget personalizado
- Tooltips con información de casos
- Color coding por completitud
- Integración con BD SQLite
- Festivos de Colombia
- Navegación por mes/año
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                               QPushButton, QLabel, QFrame, QTextEdit, QToolTip)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QTextCharFormat, QColor, QFont, QPalette
from datetime import datetime, date
import pandas as pd


class CalendarWidget(QWidget):
    """
    Widget de calendario inteligente con datos de casos

    Signals:
        date_selected(QDate): Emitido cuando se selecciona una fecha
        cases_requested(QDate): Emitido cuando se solicitan detalles de casos de una fecha
    """

    # Signals
    date_selected = Signal(QDate)
    cases_requested = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Datos de casos por fecha
        self.cases_by_date = {}  # {date: [{'numero_peticion': 'IHQ...', 'completitud': 98.5, ...}, ...]}

        # Crear UI
        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz del calendario"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # Header con título
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(header)

        title = QLabel("📅 Calendario de Casos")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        # Botones de acción
        self.btn_today = QPushButton("📍 Hoy")
        self.btn_today.setMinimumWidth(100)
        self.btn_today.clicked.connect(self._go_to_today)

        self.btn_refresh = QPushButton("🔄 Actualizar")
        self.btn_refresh.setMinimumWidth(120)
        self.btn_refresh.clicked.connect(self._refresh_data)

        header_layout.addWidget(self.btn_today)
        header_layout.addWidget(self.btn_refresh)

        layout.addWidget(header)

        # Leyenda de colores
        legend_frame = QFrame()
        legend_frame.setStyleSheet("""
            QFrame {
                background-color: #1e1e2e;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        legend_layout = QHBoxLayout(legend_frame)

        legend_label = QLabel("Leyenda:")
        legend_label.setStyleSheet("color: #a1a1aa; font-weight: bold;")
        legend_layout.addWidget(legend_label)

        # Colores de leyenda
        legends = [
            ("🟢 Completo (≥95%)", "#10b981"),
            ("🟡 Incompleto (80-94%)", "#f59e0b"),
            ("🔴 Deficiente (<80%)", "#ef4444"),
            ("🔵 Hoy", "#3b82f6"),
            ("⚪ Festivo", "#9ca3af"),
        ]

        for text, color in legends:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {color};")
            legend_layout.addWidget(lbl)

        legend_layout.addStretch()
        layout.addWidget(legend_frame)

        # Calendario
        self.calendar = QCalendarWidget()
        self.calendar.setMinimumHeight(400)
        self.calendar.setGridVisible(True)

        # Configurar apariencia
        self._setup_calendar_style()

        # Conectar signals
        self.calendar.selectionChanged.connect(self._on_date_selected)
        self.calendar.currentPageChanged.connect(self._on_month_changed)

        layout.addWidget(self.calendar)

        # Área de información de la fecha seleccionada
        self.info_area = QFrame()
        self.info_area.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        info_layout = QVBoxLayout(self.info_area)

        self.info_title = QLabel("Selecciona una fecha para ver los casos")
        self.info_title.setStyleSheet("font-size: 12pt; font-weight: bold; color: #ffffff;")
        info_layout.addWidget(self.info_title)

        self.info_details = QTextEdit()
        self.info_details.setReadOnly(True)
        self.info_details.setMaximumHeight(150)
        self.info_details.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                padding: 8px;
            }
        """)
        info_layout.addWidget(self.info_details)

        layout.addWidget(self.info_area)

    def _setup_calendar_style(self):
        """Configura el estilo del calendario"""
        # Configurar navegación
        self.calendar.setNavigationBarVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Fuente
        font = QFont("Segoe UI", 10)
        self.calendar.setFont(font)

        # Establecer formato de hoy
        today_format = QTextCharFormat()
        today_format.setBackground(QColor(59, 130, 246))  # Azul #3b82f6
        today_format.setForeground(QColor(255, 255, 255))
        today_format.setFontWeight(QFont.Bold)
        self.calendar.setDateTextFormat(QDate.currentDate(), today_format)

        # Configurar festivos (Colombia)
        self._mark_holidays()

    def _mark_holidays(self):
        """Marca festivos de Colombia en el calendario"""
        try:
            import holidays

            # Obtener festivos de Colombia para el año actual y siguientes
            current_year = datetime.now().year
            co_holidays = holidays.Colombia(years=[current_year, current_year + 1])

            # Formato para festivos
            holiday_format = QTextCharFormat()
            holiday_format.setBackground(QColor(156, 163, 175))  # Gris #9ca3af
            holiday_format.setForeground(QColor(255, 255, 255))

            # Marcar festivos en el calendario
            for holiday_date in co_holidays.keys():
                qdate = QDate(holiday_date.year, holiday_date.month, holiday_date.day)
                self.calendar.setDateTextFormat(qdate, holiday_format)

        except ImportError:
            # Si holidays no está instalado, continuar sin festivos
            pass

    def _on_date_selected(self):
        """Maneja la selección de una fecha"""
        selected_date = self.calendar.selectedDate()
        py_date = date(selected_date.year(), selected_date.month(), selected_date.day())

        # Emitir signal
        self.date_selected.emit(selected_date)

        # Actualizar área de información
        self._update_info_area(py_date)

    def _on_month_changed(self, year: int, month: int):
        """Maneja el cambio de mes"""
        # Recargar datos para el nuevo mes
        self._load_month_data(year, month)

    def _update_info_area(self, selected_date: date):
        """Actualiza el área de información con los casos de la fecha seleccionada"""
        cases = self.cases_by_date.get(selected_date, [])

        # Actualizar título
        date_str = selected_date.strftime("%d de %B de %Y")
        self.info_title.setText(f"📅 {date_str}")

        # Actualizar detalles
        if not cases:
            self.info_details.setPlainText("No hay casos registrados para esta fecha.")
        else:
            details_text = f"Total de casos: {len(cases)}\n"
            details_text += "─" * 60 + "\n\n"

            for case in cases:
                numero = case.get('numero_peticion', 'N/A')
                completitud = case.get('completitud', 0)
                diagnostico = case.get('diagnostico', 'N/A')

                # Emoji según completitud
                if completitud >= 95:
                    emoji = "🟢"
                elif completitud >= 80:
                    emoji = "🟡"
                else:
                    emoji = "🔴"

                details_text += f"{emoji} {numero} - {completitud:.1f}%\n"
                details_text += f"   Diagnóstico: {diagnostico}\n\n"

            self.info_details.setPlainText(details_text)

    def _go_to_today(self):
        """Navega a la fecha de hoy"""
        self.calendar.setSelectedDate(QDate.currentDate())

    def _refresh_data(self):
        """Recarga los datos desde la BD"""
        current_date = self.calendar.selectedDate()
        self._load_month_data(current_date.year(), current_date.month())

    def _load_month_data(self, year: int, month: int):
        """Carga datos de casos para el mes especificado"""
        try:
            from core.database_manager import get_all_records_as_dataframe

            # Obtener todos los registros
            df = get_all_records_as_dataframe()

            if df.empty:
                self.cases_by_date = {}
                self._clear_date_formats()
                return

            # Filtrar por mes/año si existe columna de fecha
            date_column = None
            for col in ['Fecha de Ingreso', 'Fecha Ingreso', 'fecha_ingreso', 'Fecha']:
                if col in df.columns:
                    date_column = col
                    break

            if not date_column:
                # Si no hay columna de fecha, no hay nada que mostrar
                self.cases_by_date = {}
                self._clear_date_formats()
                return

            # Limpiar formatos anteriores
            self._clear_date_formats()

            # Procesar cada registro
            self.cases_by_date = {}

            for idx, row in df.iterrows():
                try:
                    # Convertir fecha a datetime
                    fecha_str = row[date_column]
                    if pd.isna(fecha_str) or fecha_str == '':
                        continue

                    # Intentar parsear fecha
                    fecha_dt = pd.to_datetime(fecha_str, errors='coerce')
                    if pd.isna(fecha_dt):
                        continue

                    fecha_date = fecha_dt.date()

                    # Filtrar por mes/año
                    if fecha_date.year != year or fecha_date.month != month:
                        continue

                    # Obtener completitud
                    completitud = row.get('Completitud (%)', 0)
                    if pd.isna(completitud):
                        completitud = 0

                    # Agregar caso a la fecha
                    if fecha_date not in self.cases_by_date:
                        self.cases_by_date[fecha_date] = []

                    self.cases_by_date[fecha_date].append({
                        'numero_peticion': row.get('Numero de Peticion', 'N/A'),
                        'completitud': float(completitud),
                        'diagnostico': row.get('Diagnostico Principal', 'N/A')
                    })

                    # Aplicar color según completitud promedio del día
                    avg_completitud = sum(c['completitud'] for c in self.cases_by_date[fecha_date]) / len(self.cases_by_date[fecha_date])
                    self._set_date_color(fecha_date, avg_completitud)

                except Exception as e:
                    # Ignorar errores de parsing individual
                    continue

        except Exception as e:
            # Error general, limpiar datos
            self.cases_by_date = {}
            self._clear_date_formats()

    def _set_date_color(self, fecha: date, completitud: float):
        """Establece el color de una fecha según la completitud"""
        qdate = QDate(fecha.year, fecha.month, fecha.day)

        # Formato según completitud
        date_format = QTextCharFormat()

        if completitud >= 95:
            # Verde - Completo
            date_format.setBackground(QColor(16, 185, 129))  # #10b981
            date_format.setForeground(QColor(255, 255, 255))
        elif completitud >= 80:
            # Amarillo - Incompleto
            date_format.setBackground(QColor(245, 158, 11))  # #f59e0b
            date_format.setForeground(QColor(0, 0, 0))
        else:
            # Rojo - Deficiente
            date_format.setBackground(QColor(239, 68, 68))  # #ef4444
            date_format.setForeground(QColor(255, 255, 255))

        date_format.setFontWeight(QFont.Bold)

        self.calendar.setDateTextFormat(qdate, date_format)

    def _clear_date_formats(self):
        """Limpia todos los formatos de fechas (excepto hoy y festivos)"""
        # Obtener mes actual del calendario
        current_date = self.calendar.selectedDate()
        year = current_date.year()
        month = current_date.month()

        # Limpiar todos los días del mes
        for day in range(1, 32):
            try:
                qdate = QDate(year, month, day)
                if qdate.isValid():
                    # Solo limpiar si no es hoy
                    if qdate != QDate.currentDate():
                        self.calendar.setDateTextFormat(qdate, QTextCharFormat())
            except:
                break

        # Re-aplicar formato de hoy
        today_format = QTextCharFormat()
        today_format.setBackground(QColor(59, 130, 246))
        today_format.setForeground(QColor(255, 255, 255))
        today_format.setFontWeight(QFont.Bold)
        self.calendar.setDateTextFormat(QDate.currentDate(), today_format)

        # Re-aplicar festivos
        self._mark_holidays()

    def load_data_from_database(self):
        """Carga datos desde la base de datos (método público)"""
        current_date = self.calendar.selectedDate()
        self._load_month_data(current_date.year(), current_date.month())


# Ejemplo de uso
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
    window.setWindowTitle("CalendarWidget - Demo")
    window.resize(900, 800)

    calendar_widget = CalendarWidget()

    # Cargar datos
    calendar_widget.load_data_from_database()

    window.setCentralWidget(calendar_widget)
    window.show()

    sys.exit(app.exec())
