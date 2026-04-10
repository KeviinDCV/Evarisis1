#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DatabaseTableModel - Modelo Qt para tabla de base de datos
Implementación de QAbstractTableModel para virtualización de datos

Características:
- Virtualización nativa Qt (miles de filas sin lag)
- Sorting por columna
- Filtrado con QSortFilterProxyModel
- Edición inline
- Colores por estado
- Performance optimizada
"""

from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor, QBrush, QFont
import pandas as pd
from typing import Any, List, Optional

class DatabaseTableModel(QAbstractTableModel):
    """
    Modelo Qt para tabla de base de datos

    Args:
        dataframe (pd.DataFrame): DataFrame con los datos
        parent (QObject): Objeto padre
    """

    def __init__(self, dataframe: pd.DataFrame = None, parent=None):
        super().__init__(parent)
        self._dataframe = dataframe if dataframe is not None else pd.DataFrame()
        self._headers = list(self._dataframe.columns) if not self._dataframe.empty else []

    def rowCount(self, parent=QModelIndex()) -> int:
        """Número de filas"""
        if parent.isValid():
            return 0
        return len(self._dataframe)

    def columnCount(self, parent=QModelIndex()) -> int:
        """Número de columnas"""
        if parent.isValid():
            return 0
        return len(self._headers)

    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """
        Obtiene datos para una celda específica

        Args:
            index: Índice de la celda
            role: Rol de los datos (Display, Background, Foreground, etc.)
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if row >= len(self._dataframe) or col >= len(self._headers):
            return None

        # Valor de la celda
        value = self._dataframe.iloc[row, col]

        # DisplayRole: Texto a mostrar
        if role == Qt.DisplayRole:
            # Manejar NaN y None
            if pd.isna(value):
                return "N/A"
            return str(value)

        # TextAlignmentRole: Alineación
        elif role == Qt.TextAlignmentRole:
            # Números a la derecha, texto a la izquierda
            if isinstance(value, (int, float)) and not pd.isna(value):
                return Qt.AlignRight | Qt.AlignVCenter
            return Qt.AlignLeft | Qt.AlignVCenter

        # BackgroundRole: Color de fondo
        elif role == Qt.BackgroundRole:
            return self._get_background_color(row, col, value)

        # ForegroundRole: Color de texto
        elif role == Qt.ForegroundRole:
            return self._get_foreground_color(row, col, value)

        # FontRole: Fuente
        elif role == Qt.FontRole:
            font = QFont("Segoe UI", 10)

            # Negrita para números de caso
            if col == 0:  # Primera columna (número de caso)
                font.setBold(True)

            return font

        return None

    def _get_background_color(self, row: int, col: int, value: Any) -> Optional[QBrush]:
        """
        Determina el color de fondo según el valor y contexto

        Args:
            row: Fila
            col: Columna
            value: Valor de la celda
        """
        # Color por completitud (si existe columna "Completitud")
        if "Completitud" in self._headers:
            completitud_col = self._headers.index("Completitud")
            completitud = self._dataframe.iloc[row, completitud_col]

            if not pd.isna(completitud):
                try:
                    completitud_val = float(completitud)

                    # Verde: >= 95%
                    if completitud_val >= 95:
                        return QBrush(QColor("#10b98133"))  # Verde transparente
                    # Amarillo: 80-95%
                    elif completitud_val >= 80:
                        return QBrush(QColor("#f59e0b33"))  # Amarillo transparente
                    # Rojo: < 80%
                    else:
                        return QBrush(QColor("#ef444433"))  # Rojo transparente
                except (ValueError, TypeError):
                    pass

        # Filas alternas (zebra striping)
        if row % 2 == 0:
            return QBrush(QColor("#252538"))
        else:
            return QBrush(QColor("#2a2a3e"))

    def _get_foreground_color(self, row: int, col: int, value: Any) -> Optional[QBrush]:
        """
        Determina el color de texto según el valor

        Args:
            row: Fila
            col: Columna
            value: Valor de la celda
        """
        # N/A en gris
        if pd.isna(value):
            return QBrush(QColor("#6b7280"))

        # Estados de auditoría IA
        if "Estado IA" in self._headers and col == self._headers.index("Estado IA"):
            if value == "COMPLETA":
                return QBrush(QColor("#10b981"))  # Verde
            elif value == "PARCIAL":
                return QBrush(QColor("#f59e0b"))  # Amarillo
            elif value == "PENDIENTE":
                return QBrush(QColor("#ef4444"))  # Rojo

        return QBrush(QColor("#ffffff"))  # Blanco por defecto

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole) -> Any:
        """
        Obtiene datos del header

        Args:
            section: Índice de la sección
            orientation: Horizontal o Vertical
            role: Rol de los datos
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                if section < len(self._headers):
                    return self._headers[section]
            else:
                return str(section + 1)  # Número de fila

        elif role == Qt.FontRole:
            font = QFont("Segoe UI", 10, QFont.Bold)
            return font

        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter

        return None

    def setData(self, index: QModelIndex, value: Any, role=Qt.EditRole) -> bool:
        """
        Actualiza datos (para edición inline)

        Args:
            index: Índice de la celda
            value: Nuevo valor
            role: Rol
        """
        if not index.isValid() or role != Qt.EditRole:
            return False

        row = index.row()
        col = index.column()

        if row >= len(self._dataframe) or col >= len(self._headers):
            return False

        # Actualizar DataFrame
        self._dataframe.iloc[row, col] = value

        # Emitir signal de cambio
        self.dataChanged.emit(index, index, [Qt.DisplayRole])

        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Flags de la celda (editable, seleccionable, etc.)

        Args:
            index: Índice de la celda
        """
        if not index.isValid():
            return Qt.NoItemFlags

        # Todas las celdas son seleccionables y editables
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def sort(self, column: int, order=Qt.AscendingOrder):
        """
        Ordena los datos por columna

        Args:
            column: Índice de la columna
            order: Orden (Ascendente o Descendente)
        """
        if column >= len(self._headers):
            return

        self.layoutAboutToBeChanged.emit()

        col_name = self._headers[column]
        ascending = (order == Qt.AscendingOrder)

        self._dataframe = self._dataframe.sort_values(
            by=col_name,
            ascending=ascending,
            na_position='last'
        ).reset_index(drop=True)

        self.layoutChanged.emit()

    def update_dataframe(self, new_dataframe: pd.DataFrame):
        """
        Actualiza el DataFrame completo

        Args:
            new_dataframe: Nuevo DataFrame
        """
        self.beginResetModel()
        self._dataframe = new_dataframe
        self._headers = list(new_dataframe.columns) if not new_dataframe.empty else []
        self.endResetModel()

    def get_dataframe(self) -> pd.DataFrame:
        """Obtiene el DataFrame actual"""
        return self._dataframe.copy()

    def get_row_data(self, row: int) -> dict:
        """
        Obtiene los datos de una fila como diccionario

        Args:
            row: Índice de la fila

        Returns:
            dict: Datos de la fila
        """
        if row >= len(self._dataframe):
            return {}

        return self._dataframe.iloc[row].to_dict()


class FilterProxyModel(QSortFilterProxyModel):
    """
    Modelo proxy para filtrado de datos

    Permite filtrar sin modificar el modelo base
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self._filter_columns = []  # Columnas específicas a filtrar

    def set_filter_columns(self, columns: List[int]):
        """
        Establece las columnas a filtrar

        Args:
            columns: Lista de índices de columnas
        """
        self._filter_columns = columns
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """
        Determina si una fila pasa el filtro

        Args:
            source_row: Fila del modelo fuente
            source_parent: Padre del modelo fuente
        """
        if not self._filter_columns:
            # Filtrar en todas las columnas
            return super().filterAcceptsRow(source_row, source_parent)

        # Filtrar solo en columnas específicas
        model = self.sourceModel()
        regex = self.filterRegularExpression()

        for col in self._filter_columns:
            index = model.index(source_row, col, source_parent)
            data = model.data(index, Qt.DisplayRole)

            if data and regex.match(str(data)).hasMatch():
                return True

        return False


# Ejemplo de uso
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QTableView, QVBoxLayout, QWidget, QLineEdit

    app = QApplication(sys.argv)

    # Crear datos de prueba
    data = {
        'Numero de caso': ['IHQ250001', 'IHQ250002', 'IHQ250003', 'IHQ250004'],
        'Paciente': ['Paciente A', 'Paciente B', 'Paciente C', 'Paciente D'],
        'Servicio': ['Cirugía', 'Oncología', 'Cirugía', 'Oncología'],
        'Completitud': [98.5, 85.2, 72.1, 100.0],
        'Estado IA': ['COMPLETA', 'PARCIAL', 'PENDIENTE', 'COMPLETA']
    }
    df = pd.DataFrame(data)

    # Crear modelo
    model = DatabaseTableModel(df)

    # Crear proxy para filtrado
    proxy_model = FilterProxyModel()
    proxy_model.setSourceModel(model)

    # Crear vista
    window = QWidget()
    window.setWindowTitle("DatabaseTableModel - Demo")
    window.resize(900, 500)

    layout = QVBoxLayout(window)

    # Buscador
    search = QLineEdit()
    search.setPlaceholderText("Buscar...")
    search.textChanged.connect(proxy_model.setFilterFixedString)
    layout.addWidget(search)

    # Tabla
    table = QTableView()
    table.setModel(proxy_model)
    table.setSortingEnabled(True)
    table.setAlternatingRowColors(False)  # Usamos nuestros colores
    layout.addWidget(table)

    window.show()

    sys.exit(app.exec())
