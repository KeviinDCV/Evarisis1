#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebAutoView - Vista de automatización web QHORTE
Vista para automatización de carga de datos a plataforma web QHORTE

Características:
- Configuración de credenciales
- Selección de casos a cargar
- Monitoreo en tiempo real
- Log de operaciones
- Integración con módulo web automation
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFrame,
    QProgressBar, QGroupBox, QCheckBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import List, Dict, Any
import pandas as pd


class WebAutoView(QWidget):
    """
    Vista de automatización web QHORTE

    Signals:
        upload_requested(list): Emitido cuando se solicita carga (lista de casos)
        config_saved(dict): Emitido cuando se guarda configuración
    """

    # Signals
    upload_requested = Signal(list)
    config_saved = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")

        # Estado
        self.selected_cases = []
        self.is_uploading = False
        self.df = None  # DataFrame con casos
        self.upload_stats = {
            'total': 0,
            'exitosos': 0,
            'fallidos': 0,
            'en_proceso': 0
        }

        # Crear UI
        self._create_ui()

        # Cargar datos iniciales
        self.load_cases_from_database()

    def _create_ui(self):
        """Crea la interfaz de la vista"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title_layout = QHBoxLayout()

        title = QLabel("🌐 QHORTE Web Automation")
        title.setObjectName("PageTitle")

        # Botón de estado de conexión
        self.connection_status = QLabel("● Desconectado")
        self.connection_status.setStyleSheet(
            "color: #ef4444; font-size: 11pt; font-weight: bold;"
        )

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(self.connection_status)

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
                color: #10b981;
                font-weight: bold;
                border-bottom: 2px solid #10b981;
            }
        """)

        # Tab 1: Configuración
        self.config_tab = self._create_config_tab()
        self.tabs.addTab(self.config_tab, "⚙️ Configuración")

        # Tab 2: Carga de Datos
        self.upload_tab = self._create_upload_tab()
        self.tabs.addTab(self.upload_tab, "📤 Carga de Datos")

        # Tab 3: Monitoreo
        self.monitor_tab = self._create_monitor_tab()
        self.tabs.addTab(self.monitor_tab, "📊 Monitoreo")

        layout.addWidget(self.tabs)

    def _create_config_tab(self) -> QWidget:
        """Crea el tab de configuración"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Advertencia de seguridad
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a3e;
                border-left: 4px solid #f59e0b;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        warning_layout = QVBoxLayout(warning_frame)

        warning_title = QLabel("⚠️ Advertencia de Seguridad")
        warning_title.setStyleSheet("color: #f59e0b; font-size: 12pt; font-weight: bold;")

        warning_text = QLabel(
            "Las credenciales se almacenan de manera segura en el sistema. "
            "No compartas esta información con terceros."
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("color: #a1a1aa; font-size: 10pt;")

        warning_layout.addWidget(warning_title)
        warning_layout.addWidget(warning_text)

        layout.addWidget(warning_frame)

        # Configuración de credenciales
        cred_group = QGroupBox("Credenciales QHORTE")
        cred_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #3f3f55;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)

        cred_layout = QVBoxLayout(cred_group)

        # URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; font-weight: normal;")
        url_label.setMinimumWidth(120)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://qhorte.hospitaldelvalle.gov.co")
        self.url_input.setStyleSheet(self._input_style())

        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input, 1)
        cred_layout.addLayout(url_layout)

        # Usuario
        user_layout = QHBoxLayout()
        user_label = QLabel("Usuario:")
        user_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; font-weight: normal;")
        user_label.setMinimumWidth(120)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("usuario@hospital.gov.co")
        self.user_input.setStyleSheet(self._input_style())

        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_input, 1)
        cred_layout.addLayout(user_layout)

        # Contraseña
        pass_layout = QHBoxLayout()
        pass_label = QLabel("Contraseña:")
        pass_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; font-weight: normal;")
        pass_label.setMinimumWidth(120)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("••••••••")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet(self._input_style())

        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_input, 1)
        cred_layout.addLayout(pass_layout)

        # Botones
        btn_layout = QHBoxLayout()

        self.test_connection_btn = QPushButton("🔌 Probar Conexión")
        self.test_connection_btn.setProperty("class", "ActionButton")
        self.test_connection_btn.clicked.connect(self._on_test_connection)

        self.save_config_btn = QPushButton("💾 Guardar Configuración")
        self.save_config_btn.setProperty("class", "ActionButton")
        self.save_config_btn.clicked.connect(self._on_save_config)

        btn_layout.addWidget(self.test_connection_btn)
        btn_layout.addWidget(self.save_config_btn)
        cred_layout.addLayout(btn_layout)

        layout.addWidget(cred_group)

        # Opciones avanzadas
        advanced_group = QGroupBox("Opciones Avanzadas")
        advanced_layout = QVBoxLayout(advanced_group)

        self.headless_check = QCheckBox("Ejecutar en modo headless (sin ventana del navegador)")
        self.headless_check.setStyleSheet("color: #a1a1aa; font-size: 10pt;")
        self.headless_check.setChecked(False)

        self.auto_retry_check = QCheckBox("Reintentar automáticamente en caso de error")
        self.auto_retry_check.setStyleSheet("color: #a1a1aa; font-size: 10pt;")
        self.auto_retry_check.setChecked(True)

        advanced_layout.addWidget(self.headless_check)
        advanced_layout.addWidget(self.auto_retry_check)

        layout.addWidget(advanced_group)

        layout.addStretch()

        return tab

    def _create_upload_tab(self) -> QWidget:
        """Crea el tab de carga de datos"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Información
        info_label = QLabel(
            "Selecciona los casos que deseas cargar a la plataforma QHORTE"
        )
        info_label.setStyleSheet("color: #a1a1aa; font-size: 11pt;")
        layout.addWidget(info_label)

        # Filtros
        filter_group = QGroupBox("Filtros")
        filter_layout = QHBoxLayout(filter_group)

        filter_label = QLabel("Estado:")
        filter_label.setStyleSheet("color: #a1a1aa;")

        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Todos",
            "Completos (≥95%)",
            "Pendientes de Carga",
            "Con Errores"
        ])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
            }
        """)

        refresh_btn = QPushButton("🔄 Actualizar")
        refresh_btn.setProperty("class", "ActionButton")
        refresh_btn.clicked.connect(self.load_cases_from_database)

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_combo, 1)
        filter_layout.addWidget(refresh_btn)

        # Conectar filtro
        self.filter_combo.currentIndexChanged.connect(self._on_filter_changed)

        layout.addWidget(filter_group)

        # Tabla de casos
        self.cases_table = QTableWidget()
        self.cases_table.setColumnCount(5)
        self.cases_table.setHorizontalHeaderLabels([
            "Seleccionar", "Número", "Paciente", "Completitud", "Estado Web"
        ])
        self.cases_table.horizontalHeader().setStretchLastSection(True)
        self.cases_table.setStyleSheet("""
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
                padding: 10px;
                border: none;
            }
        """)

        layout.addWidget(self.cases_table)

        # Botones de acción
        action_layout = QHBoxLayout()

        self.select_all_btn = QPushButton("✓ Seleccionar Todo")
        self.select_all_btn.setProperty("class", "ActionButton")
        self.select_all_btn.clicked.connect(self._select_all_cases)

        self.deselect_all_btn = QPushButton("✗ Deseleccionar Todo")
        self.deselect_all_btn.setProperty("class", "ActionButton")
        self.deselect_all_btn.clicked.connect(self._deselect_all_cases)

        self.upload_btn = QPushButton("📤 Cargar Seleccionados")
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 11pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #34d399, stop:1 #10b981);
            }
        """)
        self.upload_btn.clicked.connect(self._on_upload_cases)

        action_layout.addWidget(self.select_all_btn)
        action_layout.addWidget(self.deselect_all_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.upload_btn)

        layout.addLayout(action_layout)

        return tab

    def _create_monitor_tab(self) -> QWidget:
        """Crea el tab de monitoreo"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Estadísticas
        stats_layout = QHBoxLayout()

        # Crear labels de estadísticas como atributos para actualización dinámica
        self.stat_labels = {}
        stats = [
            ("total", "Total Procesados", "#3b82f6"),
            ("exitosos", "Exitosos", "#10b981"),
            ("fallidos", "Fallidos", "#ef4444"),
            ("en_proceso", "En Proceso", "#f59e0b")
        ]

        for key, title, color in stats:
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: #252538;
                    border-left: 4px solid {color};
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)

            stat_layout = QVBoxLayout(stat_frame)

            stat_title = QLabel(title)
            stat_title.setStyleSheet("color: #a1a1aa; font-size: 10pt;")

            stat_value = QLabel("0")
            stat_value.setStyleSheet(f"color: {color}; font-size: 24pt; font-weight: bold;")

            stat_layout.addWidget(stat_title)
            stat_layout.addWidget(stat_value)

            stats_layout.addWidget(stat_frame)

            # Guardar referencia
            self.stat_labels[key] = stat_value

        layout.addLayout(stats_layout)

        # Progreso actual
        progress_group = QGroupBox("Progreso de Carga")
        progress_layout = QVBoxLayout(progress_group)

        self.upload_progress_label = QLabel("Sin operaciones activas")
        self.upload_progress_label.setStyleSheet("color: #a1a1aa; font-size: 11pt;")

        self.upload_progress_bar = QProgressBar()
        self.upload_progress_bar.setTextVisible(True)
        self.upload_progress_bar.setValue(0)
        self.upload_progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #3f3f55;
                border-radius: 6px;
                text-align: center;
                background-color: #1e1e2e;
                color: #ffffff;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #10b981;
                border-radius: 5px;
            }
        """)

        progress_layout.addWidget(self.upload_progress_label)
        progress_layout.addWidget(self.upload_progress_bar)

        layout.addWidget(progress_group)

        # Log de operaciones
        log_group = QGroupBox("Log de Operaciones")
        log_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
                font-family: 'Consolas', monospace;
                font-size: 9pt;
                padding: 10px;
            }
        """)

        log_layout.addWidget(self.log_text)

        # Botones de log
        log_btn_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️ Limpiar Log")
        clear_log_btn.setProperty("class", "ActionButton")
        clear_log_btn.clicked.connect(lambda: self.log_text.clear())

        export_log_btn = QPushButton("💾 Exportar Log")
        export_log_btn.setProperty("class", "ActionButton")

        log_btn_layout.addWidget(clear_log_btn)
        log_btn_layout.addWidget(export_log_btn)
        log_btn_layout.addStretch()

        log_layout.addLayout(log_btn_layout)

        layout.addWidget(log_group)

        return tab

    def _input_style(self) -> str:
        """Retorna estilo para inputs"""
        return """
            QLineEdit {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                padding: 10px;
                color: #ffffff;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #10b981;
            }
        """

    def _on_test_connection(self):
        """Prueba la conexión con QHORTE"""
        url = self.url_input.text().strip()
        user = self.user_input.text().strip()
        password = self.pass_input.text()

        if not all([url, user, password]):
            QMessageBox.warning(
                self,
                "Datos Incompletos",
                "Por favor completa todos los campos de configuración."
            )
            return

        # TODO: Implementar test de conexión real
        QMessageBox.information(
            self,
            "Función en Desarrollo",
            "La prueba de conexión se implementará con el módulo "
            "de automatización web (Selenium/Playwright)."
        )

        # Simular conexión exitosa
        self.connection_status.setText("● Conectado")
        self.connection_status.setStyleSheet(
            "color: #10b981; font-size: 11pt; font-weight: bold;"
        )

    def _on_save_config(self):
        """Guarda la configuración"""
        config = {
            'url': self.url_input.text().strip(),
            'user': self.user_input.text().strip(),
            'password': self.pass_input.text(),
            'headless': self.headless_check.isChecked(),
            'auto_retry': self.auto_retry_check.isChecked()
        }

        # Emitir signal
        self.config_saved.emit(config)

        QMessageBox.information(
            self,
            "Configuración Guardada",
            "La configuración se ha guardado exitosamente."
        )

    def _on_upload_cases(self):
        """Inicia carga de casos seleccionados"""
        # Obtener casos seleccionados
        selected = self._get_selected_cases()

        if not selected:
            QMessageBox.warning(
                self,
                "Sin Selección",
                "Por favor selecciona al menos un caso para cargar."
            )
            return

        # Confirmación
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmar Carga")
        msg.setText(f"¿Deseas cargar {len(selected)} casos a QHORTE?")
        msg.setInformativeText("Esta operación puede tomar varios minutos.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            # Emitir signal
            self.upload_requested.emit(selected)
            self.add_log_message(f"📤 Iniciando carga de {len(selected)} casos a QHORTE...")

    def add_log_message(self, message: str):
        """Agrega mensaje al log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def load_cases_from_database(self):
        """Carga casos desde la base de datos"""
        try:
            from core.database_manager import get_all_records_as_dataframe

            # Cargar datos
            self.df = get_all_records_as_dataframe()

            if self.df.empty:
                self.add_log_message("⚠️ No hay casos en la base de datos")
                return

            # Aplicar filtro actual
            self._apply_filter()

            self.add_log_message(f"✓ Cargados {len(self.df)} casos desde la base de datos")

        except Exception as e:
            self.add_log_message(f"❌ Error al cargar casos: {str(e)}")

    def _apply_filter(self):
        """Aplica el filtro seleccionado y actualiza la tabla"""
        if self.df is None or self.df.empty:
            return

        # Obtener filtro actual
        filter_index = self.filter_combo.currentIndex()

        # Crear DataFrame filtrado
        df_filtered = self.df.copy()

        if filter_index == 1:  # Completos (≥95%)
            if 'Completitud (%)' in df_filtered.columns:
                df_filtered = df_filtered[pd.to_numeric(df_filtered['Completitud (%)'], errors='coerce') >= 95]
        elif filter_index == 2:  # Pendientes de carga
            # Placeholder: filtrar por estado web (columna que no existe aún)
            pass
        elif filter_index == 3:  # Con errores
            if 'Completitud (%)' in df_filtered.columns:
                df_filtered = df_filtered[pd.to_numeric(df_filtered['Completitud (%)'], errors='coerce') < 80]

        # Actualizar tabla
        self._populate_table(df_filtered)

    def _populate_table(self, df: pd.DataFrame):
        """Puebla la tabla con los casos del DataFrame"""
        self.cases_table.setRowCount(0)

        if df.empty:
            return

        # Buscar columnas relevantes
        col_numero = None
        col_paciente = None
        col_completitud = None

        # Detección flexible de columnas
        for col in df.columns:
            col_lower = col.lower()
            if 'numero' in col_lower and 'peticion' in col_lower:
                col_numero = col
            elif 'paciente' in col_lower or 'nombre' in col_lower:
                col_paciente = col
            elif 'completitud' in col_lower:
                col_completitud = col

        # Limitar a primeros 100 casos para rendimiento
        df_display = df.head(100)

        for idx, row in df_display.iterrows():
            row_idx = self.cases_table.rowCount()
            self.cases_table.insertRow(row_idx)

            # Columna 0: Checkbox
            checkbox = QCheckBox()
            checkbox.setStyleSheet("margin-left: 10px;")
            self.cases_table.setCellWidget(row_idx, 0, checkbox)

            # Columna 1: Número de caso
            numero = row.get(col_numero, 'N/A') if col_numero else 'N/A'
            item_numero = QTableWidgetItem(str(numero))
            self.cases_table.setItem(row_idx, 1, item_numero)

            # Columna 2: Paciente
            paciente = row.get(col_paciente, 'N/A') if col_paciente else 'N/A'
            item_paciente = QTableWidgetItem(str(paciente)[:30])  # Truncar
            self.cases_table.setItem(row_idx, 2, item_paciente)

            # Columna 3: Completitud
            if col_completitud:
                completitud = row.get(col_completitud, 0)
                try:
                    completitud_val = float(completitud)
                    item_comp = QTableWidgetItem(f"{completitud_val:.1f}%")

                    # Color según completitud
                    if completitud_val >= 95:
                        item_comp.setForeground(QColor(16, 185, 129))  # Verde
                    elif completitud_val >= 80:
                        item_comp.setForeground(QColor(245, 158, 11))  # Amarillo
                    else:
                        item_comp.setForeground(QColor(239, 68, 68))   # Rojo

                except:
                    item_comp = QTableWidgetItem("N/A")

                self.cases_table.setItem(row_idx, 3, item_comp)
            else:
                self.cases_table.setItem(row_idx, 3, QTableWidgetItem("N/A"))

            # Columna 4: Estado Web (placeholder)
            item_estado = QTableWidgetItem("Pendiente")
            item_estado.setForeground(QColor(156, 163, 175))  # Gris
            self.cases_table.setItem(row_idx, 4, item_estado)

    def _on_filter_changed(self, index: int):
        """Maneja cambio de filtro"""
        self._apply_filter()

    def _select_all_cases(self):
        """Selecciona todos los casos de la tabla"""
        for row in range(self.cases_table.rowCount()):
            checkbox = self.cases_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(True)

        self.add_log_message(f"✓ Seleccionados {self.cases_table.rowCount()} casos")

    def _deselect_all_cases(self):
        """Deselecciona todos los casos"""
        for row in range(self.cases_table.rowCount()):
            checkbox = self.cases_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)

        self.add_log_message("✗ Deseleccionados todos los casos")

    def _get_selected_cases(self) -> List[Dict[str, Any]]:
        """Obtiene lista de casos seleccionados"""
        selected = []

        for row in range(self.cases_table.rowCount()):
            checkbox = self.cases_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                # Obtener datos del caso
                numero_item = self.cases_table.item(row, 1)
                paciente_item = self.cases_table.item(row, 2)

                if numero_item:
                    case_data = {
                        'numero': numero_item.text(),
                        'paciente': paciente_item.text() if paciente_item else 'N/A',
                        'row': row
                    }
                    selected.append(case_data)

        return selected

    def update_upload_stats(self, total: int = None, exitosos: int = None,
                           fallidos: int = None, en_proceso: int = None):
        """Actualiza estadísticas de carga"""
        if total is not None:
            self.upload_stats['total'] = total
            self.stat_labels['total'].setText(str(total))

        if exitosos is not None:
            self.upload_stats['exitosos'] = exitosos
            self.stat_labels['exitosos'].setText(str(exitosos))

        if fallidos is not None:
            self.upload_stats['fallidos'] = fallidos
            self.stat_labels['fallidos'].setText(str(fallidos))

        if en_proceso is not None:
            self.upload_stats['en_proceso'] = en_proceso
            self.stat_labels['en_proceso'].setText(str(en_proceso))

    def show_upload_progress(self, visible: bool, progress: int = 0, message: str = ""):
        """Muestra/oculta progreso de carga"""
        if visible:
            self.upload_progress_bar.setValue(progress)
            if message:
                self.upload_progress_label.setText(message)
        else:
            self.upload_progress_label.setText("Sin operaciones activas")
            self.upload_progress_bar.setValue(0)


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
    window.setWindowTitle("WebAutoView - Demo")
    window.resize(1200, 800)

    web_view = WebAutoView()

    # Conectar signals
    def on_upload(cases):
        print(f"Cargar {len(cases)} casos")
        web_view.add_log_message(f"Iniciando carga de {len(cases)} casos...")

    def on_config_saved(config):
        print(f"Configuración guardada: {config['url']}")

    web_view.upload_requested.connect(on_upload)
    web_view.config_saved.connect(on_config_saved)

    window.setCentralWidget(web_view)
    window.show()

    sys.exit(app.exec())
