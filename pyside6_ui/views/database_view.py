#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DatabaseView - Vista completa de gestión de base de datos
Vista principal para importación, visualización y gestión de datos

Características:
- Tab 1: Importación de PDFs con OCR
- Tab 2: Visualización de datos con tabla avanzada
- Tab 3: Calendario inteligente (placeholder)
- Integración completa con backend
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                               QPushButton, QLabel, QFileDialog, QTextEdit,
                               QFrame, QProgressBar, QMessageBox, QListWidget,
                               QListWidgetItem, QSplitter)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QColor
import pandas as pd
from pathlib import Path

from pyside6_ui.components.data_table import DataTable
from pyside6_ui.components.calendar_widget import CalendarWidget

class DatabaseView(QWidget):
    """
    Vista de gestión de base de datos

    Signals:
        import_requested(list): Emitido cuando se solicita importación (lista de archivos)
        export_requested(): Emitido cuando se solicita exportación
    """

    # Signals
    import_requested = Signal(list)
    export_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")

        # DataFrame actual
        self.current_dataframe = pd.DataFrame()

        # Lista de archivos seleccionados para importación
        self.selected_files = []
        self.file_status = {}  # {filepath: 'nuevo'|'duplicado'|'procesando'|'error'}

        # Crear UI
        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz de la vista"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title_layout = QHBoxLayout()

        title = QLabel("🗄️ Base de Datos")
        title.setObjectName("PageTitle")

        # Botón de actualizar (a la derecha del título)
        self.refresh_btn = QPushButton("🔄 Actualizar")
        self.refresh_btn.setProperty("class", "ActionButton")
        self.refresh_btn.clicked.connect(self._on_refresh_clicked)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.refresh_btn)

        layout.addLayout(title_layout)

        # Tabs principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3f3f55;
                border-radius: 8px;
                background-color: #252538;
            }
            QTabBar::tab {
                background-color: #1e1e2e;
                color: #a1a1aa;
                padding: 12px 24px;
                border: 1px solid #3f3f55;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-size: 11pt;
            }
            QTabBar::tab:hover {
                background-color: #252538;
                color: #ffffff;
            }
            QTabBar::tab:selected {
                background-color: #252538;
                color: #3b82f6;
                font-weight: bold;
                border-bottom: 2px solid #3b82f6;
            }
        """)

        # Tab 1: Importación
        self.import_tab = self._create_import_tab()
        self.tabs.addTab(self.import_tab, "📥 Importación de PDFs")

        # Tab 2: Visualización
        self.view_tab = self._create_view_tab()
        self.tabs.addTab(self.view_tab, "👁️ Visualizar Datos")

        # Tab 3: Calendario (placeholder)
        self.calendar_tab = self._create_calendar_tab()
        self.tabs.addTab(self.calendar_tab, "📅 Calendario")

        layout.addWidget(self.tabs)

    def _create_import_tab(self) -> QWidget:
        """Crea el tab de importación con detección de duplicados"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header_label = QLabel("Importar Informes de Patología (PDF)")
        header_label.setStyleSheet("font-size: 18pt; font-weight: bold; color: #ffffff;")
        layout.addWidget(header_label)

        desc_label = QLabel(
            "Selecciona uno o más archivos PDF para procesarlos con OCR y "
            "extraer automáticamente los datos de los informes de inmunohistoquímica. "
            "El sistema detectará automáticamente si el caso ya existe en la base de datos."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #a1a1aa; font-size: 11pt;")
        layout.addWidget(desc_label)

        layout.addSpacing(10)

        # Botones de selección
        buttons_layout = QHBoxLayout()

        self.select_files_btn = QPushButton("📂 Seleccionar Archivos")
        self.select_files_btn.setProperty("class", "ActionButton")
        self.select_files_btn.setMinimumHeight(40)
        self.select_files_btn.clicked.connect(self._on_select_files)

        self.select_folder_btn = QPushButton("📁 Seleccionar Carpeta")
        self.select_folder_btn.setProperty("class", "ActionButton")
        self.select_folder_btn.setMinimumHeight(40)
        self.select_folder_btn.clicked.connect(self._on_select_folder)

        self.clear_list_btn = QPushButton("🗑️ Limpiar Lista")
        self.clear_list_btn.setProperty("class", "ActionButton")
        self.clear_list_btn.setMinimumHeight(40)
        self.clear_list_btn.clicked.connect(self._on_clear_list)
        self.clear_list_btn.setEnabled(False)

        buttons_layout.addWidget(self.select_files_btn)
        buttons_layout.addWidget(self.select_folder_btn)
        buttons_layout.addWidget(self.clear_list_btn)
        buttons_layout.addStretch()

        layout.addLayout(buttons_layout)

        # Lista de archivos seleccionados con color coding
        list_header = QLabel("Archivos Seleccionados:")
        list_header.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12pt;")
        layout.addWidget(list_header)

        # Leyenda de colores
        legend_layout = QHBoxLayout()
        legend_layout.addWidget(QLabel("Leyenda:"))

        legend_new = QLabel("🟢 Nuevo")
        legend_new.setStyleSheet("color: #10b981;")
        legend_layout.addWidget(legend_new)

        legend_dup = QLabel("🔴 Duplicado")
        legend_dup.setStyleSheet("color: #ef4444;")
        legend_layout.addWidget(legend_dup)

        legend_proc = QLabel("🟠 Procesando")
        legend_proc.setStyleSheet("color: #f59e0b;")
        legend_layout.addWidget(legend_proc)

        legend_err = QLabel("⚫ Error")
        legend_err.setStyleSheet("color: #6b7280;")
        legend_layout.addWidget(legend_err)

        legend_layout.addStretch()
        layout.addLayout(legend_layout)

        self.files_listbox = QListWidget()
        self.files_listbox.setMinimumHeight(200)
        self.files_listbox.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                font-size: 10pt;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #2a2a3e;
            }
            QListWidget::item:hover {
                background-color: #252538;
            }
        """)
        layout.addWidget(self.files_listbox)

        # Botón de procesar
        process_btn_layout = QHBoxLayout()
        self.process_files_btn = QPushButton("⚡ Procesar Archivos Seleccionados")
        self.process_files_btn.setProperty("class", "ActionButton")
        self.process_files_btn.setMinimumHeight(50)
        self.process_files_btn.setMinimumWidth(300)
        self.process_files_btn.clicked.connect(self._on_process_files)
        self.process_files_btn.setEnabled(False)
        process_btn_layout.addStretch()
        process_btn_layout.addWidget(self.process_files_btn)
        process_btn_layout.addStretch()
        layout.addLayout(process_btn_layout)

        # Área de progreso (oculta inicialmente)
        self.progress_area = QFrame()
        self.progress_area.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.progress_area.setVisible(False)

        progress_layout = QVBoxLayout(self.progress_area)

        self.progress_label = QLabel("Procesando archivos...")
        self.progress_label.setStyleSheet("color: #ffffff; font-weight: bold;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3f3f55;
                border-radius: 6px;
                text-align: center;
                background-color: #1e1e2e;
                color: #ffffff;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 5px;
            }
        """)

        self.progress_detail = QTextEdit()
        self.progress_detail.setReadOnly(True)
        self.progress_detail.setMaximumHeight(120)
        self.progress_detail.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
                font-family: 'Consolas', monospace;
                font-size: 9pt;
                padding: 8px;
            }
        """)

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.progress_detail)

        layout.addWidget(self.progress_area)

        return tab

    def _create_view_tab(self) -> QWidget:
        """Crea el tab de visualización con barra de acciones completa"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Barra de título y acciones
        title_actions = QFrame()
        title_actions.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        title_layout = QHBoxLayout(title_actions)

        # Título
        title_label = QLabel("📊 Visualizador de Datos")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #ffffff;")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # Botones de acción (16 botones en 2 filas)
        actions_container = QFrame()
        actions_layout = QVBoxLayout(actions_container)
        actions_layout.setSpacing(5)
        actions_layout.setContentsMargins(0, 0, 0, 0)

        # Fila 1 de botones
        row1 = QHBoxLayout()
        row1.setSpacing(5)

        self.btn_filter = QPushButton("🔍 Filtrar")
        self.btn_filter.setMinimumWidth(100)
        self.btn_filter.clicked.connect(self._on_filter_clicked)

        self.btn_details = QPushButton("🔎 Ver Detalles")
        self.btn_details.setMinimumWidth(120)
        self.btn_details.clicked.connect(self._on_view_details)
        self.btn_details.setEnabled(False)

        self.btn_export_selection = QPushButton("📤 Exportar Selección")
        self.btn_export_selection.setMinimumWidth(150)
        self.btn_export_selection.clicked.connect(self._on_export_selection)
        self.btn_export_selection.setEnabled(False)

        self.btn_export_all = QPushButton("📊 Exportar Todo")
        self.btn_export_all.setMinimumWidth(130)
        self.btn_export_all.clicked.connect(self._on_export_all)

        self.btn_copy = QPushButton("📋 Copiar")
        self.btn_copy.setMinimumWidth(100)
        self.btn_copy.clicked.connect(self._on_copy_selection)
        self.btn_copy.setEnabled(False)

        self.btn_refresh_data = QPushButton("🔄 Actualizar")
        self.btn_refresh_data.setMinimumWidth(110)
        self.btn_refresh_data.clicked.connect(self._on_refresh_data)

        self.btn_audit_partial = QPushButton("🤖 Auditoría Parcial")
        self.btn_audit_partial.setMinimumWidth(150)
        self.btn_audit_partial.clicked.connect(self._on_audit_partial)
        self.btn_audit_partial.setEnabled(False)

        self.btn_audit_complete = QPushButton("✅ Auditoría Completa")
        self.btn_audit_complete.setMinimumWidth(160)
        self.btn_audit_complete.clicked.connect(self._on_audit_complete)
        self.btn_audit_complete.setEnabled(False)

        row1.addWidget(self.btn_filter)
        row1.addWidget(self.btn_details)
        row1.addWidget(self.btn_export_selection)
        row1.addWidget(self.btn_export_all)
        row1.addWidget(self.btn_copy)
        row1.addWidget(self.btn_refresh_data)
        row1.addWidget(self.btn_audit_partial)
        row1.addWidget(self.btn_audit_complete)

        actions_layout.addLayout(row1)

        title_layout.addWidget(actions_container)

        layout.addWidget(title_actions)

        # Crear tabla de datos
        self.data_table = DataTable()

        # Conectar signals
        self.data_table.export_requested.connect(self.export_requested.emit)
        self.data_table.row_selected.connect(self._on_row_selected)
        self.data_table.rows_selected.connect(self._on_rows_selected)

        layout.addWidget(self.data_table)

        return tab

    def _create_calendar_tab(self) -> QWidget:
        """Crea el tab de calendario con CalendarWidget completo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)

        # Crear widget de calendario
        self.calendar_widget = CalendarWidget()

        # Conectar signals
        self.calendar_widget.date_selected.connect(self._on_calendar_date_selected)

        layout.addWidget(self.calendar_widget)

        return tab

    def _on_calendar_date_selected(self, qdate):
        """Maneja la selección de una fecha en el calendario"""
        # Convertir QDate a string
        date_str = qdate.toString("dd/MM/yyyy")
        # Por ahora solo log, en el futuro podría abrir un diálogo con los casos de esa fecha
        pass  # El calendario ya muestra la información en su área de detalles

    def _on_select_files(self):
        """Maneja la selección de archivos individuales"""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Archivos PDF (*.pdf)")
        file_dialog.setWindowTitle("Seleccionar archivos PDF para importar")

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self._add_files_to_list(selected_files)

    def _on_select_folder(self):
        """Maneja la selección de una carpeta completa"""
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta con archivos PDF",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder_path:
            # Buscar todos los PDFs en la carpeta
            from pathlib import Path
            pdf_files = list(Path(folder_path).glob("*.pdf"))
            pdf_files_str = [str(f) for f in pdf_files]

            if pdf_files_str:
                self._add_files_to_list(pdf_files_str)
            else:
                QMessageBox.information(
                    self,
                    "Sin archivos PDF",
                    f"No se encontraron archivos PDF en:\n{folder_path}"
                )

    def _add_files_to_list(self, files: list):
        """Agrega archivos a la lista con detección de duplicados"""
        for file_path in files:
            # Evitar agregar duplicados a la lista de selección
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)

                # Detectar si el caso ya existe en BD
                status = self._check_if_duplicate(file_path)
                self.file_status[file_path] = status

                # Agregar a listbox con color coding
                self._add_item_to_listbox(file_path, status)

        # Actualizar estado de botones
        self._update_button_states()

    def _check_if_duplicate(self, file_path: str) -> str:
        """
        Verifica si el PDF ya fue procesado (duplicado)

        Returns:
            'nuevo' si no existe en BD
            'duplicado' si ya existe
        """
        try:
            from core.database_manager import get_all_records_as_dataframe
            import re

            # Obtener DataFrame de BD
            df = get_all_records_as_dataframe()

            if df.empty:
                return 'nuevo'

            # Extraer número de petición del nombre del archivo
            filename = Path(file_path).stem
            # Buscar patrón IHQ + números (ej: IHQ251001)
            match = re.search(r'IHQ\s*(\d+)', filename, re.IGNORECASE)

            if not match:
                # Si no tiene patrón IHQ, asumir que es nuevo
                return 'nuevo'

            numero_peticion = f"IHQ{match.group(1)}"

            # Buscar en BD
            if 'Numero de Peticion' in df.columns:
                existe = numero_peticion in df['Numero de Peticion'].values
                return 'duplicado' if existe else 'nuevo'
            else:
                return 'nuevo'

        except Exception as e:
            # En caso de error, asumir que es nuevo
            return 'nuevo'

    def _add_item_to_listbox(self, file_path: str, status: str):
        """Agrega un item a la listbox con color según estado"""
        filename = Path(file_path).name

        item = QListWidgetItem(filename)

        # Colores según estado
        if status == 'nuevo':
            item.setForeground(QColor(16, 185, 129))  # Verde #10b981
            item.setData(Qt.UserRole, '🟢')
        elif status == 'duplicado':
            item.setForeground(QColor(239, 68, 68))   # Rojo #ef4444
            item.setData(Qt.UserRole, '🔴')
        elif status == 'procesando':
            item.setForeground(QColor(245, 158, 11))  # Naranja #f59e0b
            item.setData(Qt.UserRole, '🟠')
        else:  # error
            item.setForeground(QColor(107, 114, 128)) # Gris #6b7280
            item.setData(Qt.UserRole, '⚫')

        # Guardar ruta completa en userData
        item.setData(Qt.UserRole + 1, file_path)

        # Agregar prefijo con emoji
        icon = item.data(Qt.UserRole)
        item.setText(f"{icon} {filename}")

        self.files_listbox.addItem(item)

    def _on_clear_list(self):
        """Limpia la lista de archivos seleccionados"""
        self.selected_files.clear()
        self.file_status.clear()
        self.files_listbox.clear()
        self._update_button_states()

    def _update_button_states(self):
        """Actualiza el estado de los botones según archivos seleccionados"""
        has_files = len(self.selected_files) > 0
        self.clear_list_btn.setEnabled(has_files)
        self.process_files_btn.setEnabled(has_files)

        # Actualizar texto del botón de procesar
        if has_files:
            total = len(self.selected_files)
            nuevos = sum(1 for status in self.file_status.values() if status == 'nuevo')
            duplicados = total - nuevos

            if duplicados == 0:
                text = f"⚡ Procesar {total} Archivo{'s' if total > 1 else ''}"
            else:
                text = f"⚡ Procesar {total} Archivos ({nuevos} nuevos, {duplicados} duplicados)"

            self.process_files_btn.setText(text)

    def _on_process_files(self):
        """Procesa los archivos seleccionados"""
        if not self.selected_files:
            return

        # Contar nuevos vs duplicados
        nuevos = [f for f in self.selected_files if self.file_status.get(f) == 'nuevo']
        duplicados = [f for f in self.selected_files if self.file_status.get(f) == 'duplicado']

        # Mostrar confirmación con información de duplicados
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmar Importación")

        if duplicados:
            msg.setText(f"Se procesarán {len(self.selected_files)} archivos:")
            msg.setInformativeText(
                f"• {len(nuevos)} archivos nuevos\n"
                f"• {len(duplicados)} archivos duplicados (se sobrescribirán)\n\n"
                "¿Deseas continuar?"
            )
        else:
            msg.setText(f"¿Deseas importar {len(self.selected_files)} archivo(s)?")
            msg.setInformativeText(
                "Los archivos se procesarán con OCR y se extraerán los datos automáticamente."
            )

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)

        if msg.exec() == QMessageBox.Yes:
            # Emitir signal de importación
            self.import_requested.emit(self.selected_files)

            # Actualizar estado visual de todos los archivos a "procesando"
            for i in range(self.files_listbox.count()):
                item = self.files_listbox.item(i)
                file_path = item.data(Qt.UserRole + 1)
                self.file_status[file_path] = 'procesando'
                item.setForeground(QColor(245, 158, 11))  # Naranja
                filename = Path(file_path).name
                item.setText(f"🟠 {filename}")

            # Mostrar área de progreso
            self.show_progress(True)

    def _on_refresh_clicked(self):
        """Maneja el click en el botón actualizar"""
        # Emitir signal para recargar datos desde BD
        self.load_data_from_database()

    def _on_row_selected(self, row_data: dict):
        """Maneja la selección de una fila"""
        # Habilitar botones que requieren selección individual
        self.btn_details.setEnabled(True)
        self.btn_export_selection.setEnabled(True)
        self.btn_copy.setEnabled(True)
        self.btn_audit_partial.setEnabled(True)
        self.btn_audit_complete.setEnabled(True)

    def _on_rows_selected(self, rows_data: list):
        """Maneja la selección de múltiples filas"""
        has_selection = len(rows_data) > 0

        # Habilitar botones según selección
        self.btn_export_selection.setEnabled(has_selection)
        self.btn_copy.setEnabled(has_selection)
        self.btn_audit_partial.setEnabled(has_selection)
        self.btn_audit_complete.setEnabled(has_selection)

        # Ver detalles solo para selección individual
        self.btn_details.setEnabled(len(rows_data) == 1)

    def _on_filter_clicked(self):
        """Abre un diálogo de filtros avanzados"""
        # TODO: Implementar diálogo de filtros avanzados con múltiples criterios
        QMessageBox.information(
            self,
            "Filtros Avanzados",
            "Diálogo de filtros avanzados próximamente.\n\n"
            "Por ahora usa el buscador de la tabla."
        )

    def _on_view_details(self):
        """Muestra detalles completos del caso seleccionado"""
        selected_row = self.data_table.get_selected_row()

        if not selected_row:
            return

        # Crear diálogo de detalles
        from PySide6.QtWidgets import QDialog, QTextEdit

        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalles del Caso - {selected_row.get('Numero de Peticion', 'N/A')}")
        dialog.resize(800, 600)

        layout = QVBoxLayout(dialog)

        # Área de texto con todos los detalles
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        details_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                color: #ffffff;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                padding: 10px;
            }
        """)

        # Formatear detalles
        details_str = "═" * 80 + "\n"
        details_str += f"  DETALLES DEL CASO: {selected_row.get('Numero de Peticion', 'N/A')}\n"
        details_str += "═" * 80 + "\n\n"

        for key, value in selected_row.items():
            details_str += f"{key:.<40} {value}\n"

        details_text.setPlainText(details_str)
        layout.addWidget(details_text)

        # Botón cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def _on_export_selection(self):
        """Exporta las filas seleccionadas a Excel"""
        selected_rows = self.data_table.get_selected_rows()

        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "No hay filas seleccionadas para exportar."
            )
            return

        # Convertir a DataFrame
        df_selection = pd.DataFrame(selected_rows)

        # Solicitar ubicación de guardado
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Exportación",
            f"exportacion_seleccion_{len(selected_rows)}_casos.xlsx",
            "Archivos Excel (*.xlsx)"
        )

        if file_path:
            try:
                df_selection.to_excel(file_path, index=False)
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"Se exportaron {len(selected_rows)} caso(s) a:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error de Exportación",
                    f"Error al exportar:\n{str(e)}"
                )

    def _on_export_all(self):
        """Exporta todos los datos visibles a Excel"""
        if self.current_dataframe.empty:
            QMessageBox.warning(
                self,
                "Sin Datos",
                "No hay datos para exportar."
            )
            return

        # Solicitar ubicación de guardado
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Exportación Completa",
            f"exportacion_completa_{len(self.current_dataframe)}_casos.xlsx",
            "Archivos Excel (*.xlsx)"
        )

        if file_path:
            try:
                self.current_dataframe.to_excel(file_path, index=False)
                QMessageBox.information(
                    self,
                    "Exportación Exitosa",
                    f"Se exportaron {len(self.current_dataframe)} caso(s) a:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error de Exportación",
                    f"Error al exportar:\n{str(e)}"
                )

    def _on_copy_selection(self):
        """Copia la selección al portapapeles"""
        selected_rows = self.data_table.get_selected_rows()

        if not selected_rows:
            return

        # Convertir a formato de tabla
        df_selection = pd.DataFrame(selected_rows)

        # Copiar al portapapeles
        from PySide6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(df_selection.to_csv(index=False, sep='\t'))

        QMessageBox.information(
            self,
            "Copiado",
            f"Se copiaron {len(selected_rows)} fila(s) al portapapeles."
        )

    def _on_refresh_data(self):
        """Actualiza los datos desde la base de datos"""
        self.load_data_from_database()

    def _on_audit_partial(self):
        """Lanza auditoría parcial en casos seleccionados"""
        selected_rows = self.data_table.get_selected_rows()

        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Selecciona al menos un caso para auditar."
            )
            return

        # TODO: Integrar con AuditWorker
        numeros_peticion = [row.get('Numero de Peticion', 'N/A') for row in selected_rows]

        QMessageBox.information(
            self,
            "Auditoría Parcial",
            f"Función en desarrollo.\n\n"
            f"Se auditarán {len(numeros_peticion)} caso(s):\n" +
            "\n".join(numeros_peticion[:5]) +
            (f"\n... y {len(numeros_peticion) - 5} más" if len(numeros_peticion) > 5 else "")
        )

    def _on_audit_complete(self):
        """Lanza auditoría completa en casos seleccionados"""
        selected_rows = self.data_table.get_selected_rows()

        if not selected_rows:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Selecciona al menos un caso para auditar."
            )
            return

        # TODO: Integrar con AuditWorker
        numeros_peticion = [row.get('Numero de Peticion', 'N/A') for row in selected_rows]

        QMessageBox.information(
            self,
            "Auditoría Completa",
            f"Función en desarrollo.\n\n"
            f"Se auditarán {len(numeros_peticion)} caso(s) con validación completa:\n" +
            "\n".join(numeros_peticion[:5]) +
            (f"\n... y {len(numeros_peticion) - 5} más" if len(numeros_peticion) > 5 else "")
        )

    def load_dataframe(self, dataframe: pd.DataFrame):
        """
        Carga un DataFrame en la tabla

        Args:
            dataframe: DataFrame a mostrar
        """
        self.current_dataframe = dataframe
        self.data_table.load_dataframe(dataframe)

        # Cambiar a tab de visualización
        self.tabs.setCurrentIndex(1)

    def load_data_from_database(self):
        """Carga datos desde la base de datos y actualiza calendario"""
        try:
            from core.database_manager import get_all_records_as_dataframe

            df = get_all_records_as_dataframe()

            if df.empty:
                QMessageBox.information(
                    self,
                    "Base de Datos Vacía",
                    "No hay registros en la base de datos.\n\n"
                    "Importa archivos PDF desde el tab 'Importación de PDFs'."
                )
            else:
                self.load_dataframe(df)

                # Actualizar calendario también
                if hasattr(self, 'calendar_widget'):
                    self.calendar_widget.load_data_from_database()

                QMessageBox.information(
                    self,
                    "Datos Cargados",
                    f"Se cargaron {len(df)} registros desde la base de datos.\n"
                    f"Calendario actualizado con casos por fecha."
                )

        except ImportError:
            QMessageBox.warning(
                self,
                "Módulo no disponible",
                "El módulo database_manager no está disponible.\n\n"
                "Asegúrate de que el backend esté correctamente configurado."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Error cargando datos de la base de datos:\n\n{str(e)}"
            )

    def show_progress(self, visible: bool, progress: int = 0, message: str = ""):
        """
        Muestra/oculta el área de progreso

        Args:
            visible: Si debe mostrarse
            progress: Porcentaje de progreso (0-100)
            message: Mensaje a mostrar
        """
        self.progress_area.setVisible(visible)

        if visible:
            self.progress_bar.setValue(progress)
            if message:
                self.progress_detail.append(message)

    def clear_progress(self):
        """Limpia el área de progreso"""
        self.progress_bar.setValue(0)
        self.progress_detail.clear()


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
    window.setWindowTitle("DatabaseView - Demo")
    window.resize(1400, 800)

    db_view = DatabaseView()

    # Conectar signals
    def on_import(files):
        print(f"Importar {len(files)} archivos")
        db_view.show_progress(True, 50, "Procesando archivo 1...")

    db_view.import_requested.connect(on_import)

    window.setCentralWidget(db_view)
    window.show()

    sys.exit(app.exec())
