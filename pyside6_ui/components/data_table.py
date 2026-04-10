#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataTable - Tabla de datos profesional con filtros
Wrapper de QTableView con funcionalidades avanzadas

Características:
- Virtualización nativa (miles de filas)
- Búsqueda en tiempo real
- Sorting por columna
- Filtros por columna específica
- Exportación a Excel
- Selección múltiple
- Colores por estado
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableView,
                               QLineEdit, QPushButton, QLabel, QComboBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd
from pyside6_ui.models.database_model import DatabaseTableModel, FilterProxyModel

class DataTable(QWidget):
    """
    Componente de tabla de datos con filtros integrados

    Signals:
        row_selected(dict): Emitido cuando se selecciona una fila (datos de la fila)
        rows_selected(list): Emitido cuando se seleccionan múltiples filas
        export_requested(): Emitido cuando se solicita exportación
    """

    # Signals
    row_selected = Signal(dict)
    rows_selected = Signal(list)
    export_requested = Signal()

    def __init__(self, dataframe: pd.DataFrame = None, parent=None):
        super().__init__(parent)

        # Modelo de datos
        self.model = DatabaseTableModel(dataframe if dataframe is not None else pd.DataFrame())
        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(self.model)

        # Crear UI
        self._create_ui()

        # Conectar signals
        self._connect_signals()

    def _create_ui(self):
        """Crea la interfaz de la tabla"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Barra de herramientas
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Tabla
        self.table_view = QTableView()
        self.table_view.setModel(self.proxy_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.setAlternatingRowColors(False)  # Usamos colores custom
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)  # Múltiple selección

        # Configurar headers
        self.table_view.horizontalHeader().setStretchLastSection(True)
        self.table_view.verticalHeader().setVisible(False)

        # Font
        font = QFont("Segoe UI", 10)
        self.table_view.setFont(font)

        layout.addWidget(self.table_view)

        # Barra de estado
        self.status_bar = self._create_status_bar()
        layout.addWidget(self.status_bar)

    def _create_toolbar(self) -> QFrame:
        """Crea la barra de herramientas con búsqueda y filtros"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(10, 10, 10, 10)

        # Icono de búsqueda
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 16pt; background: transparent;")

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en todos los campos...")
        self.search_input.setMinimumWidth(300)

        # Filtro por columna
        filter_label = QLabel("Filtrar por:")
        filter_label.setStyleSheet("color: #a1a1aa; background: transparent;")

        self.column_filter = QComboBox()
        self.column_filter.addItem("Todas las columnas", -1)
        self.column_filter.setMinimumWidth(150)

        # Botón limpiar filtros
        self.clear_btn = QPushButton("🗑️ Limpiar")
        self.clear_btn.setProperty("class", "ActionButton")

        # Botón exportar
        self.export_btn = QPushButton("📤 Exportar")
        self.export_btn.setProperty("class", "SuccessButton")
        self.export_btn.clicked.connect(self.export_requested.emit)

        # Agregar al layout
        layout.addWidget(search_icon)
        layout.addWidget(self.search_input)
        layout.addSpacing(20)
        layout.addWidget(filter_label)
        layout.addWidget(self.column_filter)
        layout.addSpacing(20)
        layout.addWidget(self.clear_btn)
        layout.addStretch()
        layout.addWidget(self.export_btn)

        return toolbar

    def _create_status_bar(self) -> QFrame:
        """Crea la barra de estado con información"""
        status_bar = QFrame()
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 5px 10px;
            }
        """)

        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(10, 5, 10, 5)

        # Label de registros
        self.status_label = QLabel("Registros: 0 / 0")
        self.status_label.setStyleSheet("color: #a1a1aa;")

        # Label de selección
        self.selection_label = QLabel("Seleccionados: 0")
        self.selection_label.setStyleSheet("color: #3b82f6;")

        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addWidget(self.selection_label)

        return status_bar

    def _connect_signals(self):
        """Conecta signals internos"""
        # Búsqueda
        self.search_input.textChanged.connect(self._on_search_changed)

        # Limpiar filtros
        self.clear_btn.clicked.connect(self._clear_filters)

        # Selección
        self.table_view.selectionModel().selectionChanged.connect(self._on_selection_changed)

        # Filtro por columna
        self.column_filter.currentIndexChanged.connect(self._on_column_filter_changed)

    def _on_search_changed(self, text: str):
        """Maneja cambios en el campo de búsqueda"""
        self.proxy_model.setFilterFixedString(text)
        self._update_status()

    def _on_column_filter_changed(self, index: int):
        """Maneja cambios en el filtro de columna"""
        column_index = self.column_filter.currentData()

        # Verificar que column_index sea válido (no None)
        if column_index is None:
            return

        if column_index == -1:
            # Todas las columnas
            self.proxy_model.set_filter_columns([])
            self.proxy_model.setFilterKeyColumn(-1)
        else:
            # Columna específica
            self.proxy_model.setFilterKeyColumn(column_index)

    def _on_selection_changed(self):
        """Maneja cambios en la selección"""
        selected_rows = self.table_view.selectionModel().selectedRows()
        num_selected = len(selected_rows)

        self.selection_label.setText(f"Seleccionados: {num_selected}")

        if num_selected == 1:
            # Una fila seleccionada
            row = selected_rows[0].row()
            source_row = self.proxy_model.mapToSource(selected_rows[0]).row()
            row_data = self.model.get_row_data(source_row)
            self.row_selected.emit(row_data)
        elif num_selected > 1:
            # Múltiples filas
            rows_data = []
            for selected in selected_rows:
                source_row = self.proxy_model.mapToSource(selected).row()
                row_data = self.model.get_row_data(source_row)
                rows_data.append(row_data)
            self.rows_selected.emit(rows_data)

    def _clear_filters(self):
        """Limpia todos los filtros"""
        self.search_input.clear()
        self.column_filter.setCurrentIndex(0)

    def _update_status(self):
        """Actualiza la barra de estado"""
        total_rows = self.model.rowCount()
        filtered_rows = self.proxy_model.rowCount()

        self.status_label.setText(f"Registros: {filtered_rows} / {total_rows}")

    def load_dataframe(self, dataframe: pd.DataFrame, auto_sort_column: str = "Numero de caso"):
        """
        Carga un nuevo DataFrame con ordenamiento automático opcional

        Args:
            dataframe: DataFrame a cargar
            auto_sort_column: Columna para ordenar automáticamente (None = sin orden)
        """
        # Ordenar DataFrame si se especifica columna
        if auto_sort_column and auto_sort_column in dataframe.columns:
            dataframe = dataframe.sort_values(
                by=auto_sort_column,
                ascending=True,
                na_position='last'
            ).reset_index(drop=True)

        self.model.update_dataframe(dataframe)

        # Actualizar combo de columnas
        self.column_filter.clear()
        self.column_filter.addItem("Todas las columnas", -1)

        for idx, col in enumerate(dataframe.columns):
            self.column_filter.addItem(col, idx)

        self._update_status()

    def get_dataframe(self) -> pd.DataFrame:
        """Obtiene el DataFrame actual"""
        return self.model.get_dataframe()

    def get_selected_rows(self) -> list:
        """
        Obtiene las filas seleccionadas

        Returns:
            list: Lista de diccionarios con datos de filas
        """
        selected_rows = self.table_view.selectionModel().selectedRows()
        rows_data = []

        for selected in selected_rows:
            source_row = self.proxy_model.mapToSource(selected).row()
            row_data = self.model.get_row_data(source_row)
            rows_data.append(row_data)

        return rows_data

    def get_selected_row(self) -> dict:
        """
        Obtiene la primera fila seleccionada (para selección individual)

        Returns:
            dict: Datos de la fila o diccionario vacío si no hay selección
        """
        rows = self.get_selected_rows()
        return rows[0] if rows else {}

    def clear_selection(self):
        """Limpia la selección"""
        self.table_view.clearSelection()


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

    # Crear datos de prueba
    data = {
        'Numero de caso': [f'IHQ25{str(i).zfill(4)}' for i in range(1, 51)],
        'Paciente': [f'Paciente {chr(65 + i % 26)}' for i in range(50)],
        'Servicio': ['Cirugía', 'Oncología', 'Patología'] * 17,
        'Fecha Ingreso': ['2025-11-19'] * 50,
        'Completitud': [98.5, 85.2, 72.1, 100.0, 91.3] * 10,
        'Estado IA': ['COMPLETA', 'PARCIAL', 'PENDIENTE', 'COMPLETA', 'PARCIAL'] * 10
    }
    df = pd.DataFrame(data)

    # Ventana principal
    window = QMainWindow()
    window.setWindowTitle("DataTable - Demo")
    window.resize(1200, 700)

    # Crear tabla
    table = DataTable(df)

    # Conectar signals
    def on_row_selected(row_data):
        print(f"Fila seleccionada: {row_data.get('Numero de caso', 'N/A')}")

    def on_export():
        print("Exportar solicitado")

    table.row_selected.connect(on_row_selected)
    table.export_requested.connect(on_export)

    window.setCentralWidget(table)
    window.show()

    sys.exit(app.exec())
