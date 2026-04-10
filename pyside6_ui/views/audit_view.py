#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AuditIAView - Vista de Auditoría Inteligente
Vista completa para auditoría IA con validación semántica

Características:
- Auditoría individual de casos
- Auditoría por lotes
- Reprocesamiento de casos (FUNC-06)
- Visualización de reportes
- Integración con herramientas_ia/auditor_sistema.py
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QLabel, QLineEdit, QTextEdit, QFrame,
    QProgressBar, QGroupBox, QRadioButton, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QSplitter
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Optional, Dict, Any


class AuditIAView(QWidget):
    """
    Vista de Auditoría Inteligente

    Signals:
        audit_requested(str, str): Emitido cuando se solicita auditoría (case_id, tipo)
        repair_requested(str): Emitido cuando se solicita reprocesamiento (case_id)
    """

    # Signals
    audit_requested = Signal(str, str)    # (case_id, audit_type)
    batch_audit_requested = Signal(list)  # (case_ids)
    repair_requested = Signal(str)        # (case_id)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")

        # Estado
        self.current_worker = None
        self.last_audit_result = None

        # Crear UI
        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz de la vista"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título
        title_layout = QHBoxLayout()

        title = QLabel("🤖 Auditoría Inteligente")
        title.setObjectName("PageTitle")

        # Botón de ayuda
        help_btn = QPushButton("❓ Ayuda")
        help_btn.setProperty("class", "ActionButton")
        help_btn.clicked.connect(self._show_help)

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(help_btn)

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

        # Tab 1: Auditoría Individual
        self.individual_tab = self._create_individual_tab()
        self.tabs.addTab(self.individual_tab, "🔍 Auditoría Individual")

        # Tab 2: Auditoría por Lotes
        self.batch_tab = self._create_batch_tab()
        self.tabs.addTab(self.batch_tab, "📦 Auditoría por Lotes")

        # Tab 3: Reprocesar Caso
        self.repair_tab = self._create_repair_tab()
        self.tabs.addTab(self.repair_tab, "🔧 Reprocesar Caso (FUNC-06)")

        layout.addWidget(self.tabs)

    def _create_individual_tab(self) -> QWidget:
        """Crea el tab de auditoría individual"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Input de caso
        input_group = QGroupBox("Seleccionar Caso")
        input_group.setStyleSheet("""
            QGroupBox {
                font-size: 12pt;
                font-weight: bold;
                color: #ffffff;
                border: 2px solid #3f3f55;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        input_layout = QVBoxLayout(input_group)

        # Campo de entrada
        case_input_layout = QHBoxLayout()
        case_label = QLabel("Número de Caso:")
        case_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; font-weight: normal;")

        self.case_input = QLineEdit()
        self.case_input.setPlaceholderText("Ej: IHQ251001")
        self.case_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                padding: 10px;
                color: #ffffff;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #3b82f6;
            }
        """)

        case_input_layout.addWidget(case_label)
        case_input_layout.addWidget(self.case_input, 1)
        input_layout.addLayout(case_input_layout)

        # Tipo de auditoría
        type_layout = QHBoxLayout()
        type_label = QLabel("Tipo de Auditoría:")
        type_label.setStyleSheet("color: #a1a1aa; font-size: 11pt; font-weight: normal;")

        self.audit_type_combo = QComboBox()
        self.audit_type_combo.addItems([
            "Inteligente (Recomendado)",
            "Básica",
            "Completa"
        ])
        self.audit_type_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                padding: 8px;
                color: #ffffff;
                font-size: 11pt;
            }
            QComboBox:hover {
                border: 2px solid #3b82f6;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
                margin-right: 10px;
            }
        """)

        type_layout.addWidget(type_label)
        type_layout.addWidget(self.audit_type_combo, 1)
        input_layout.addLayout(type_layout)

        # Botón auditar
        self.audit_btn = QPushButton("🚀 Iniciar Auditoría")
        self.audit_btn.setProperty("class", "ActionButton")
        self.audit_btn.setMinimumHeight(50)
        self.audit_btn.clicked.connect(self._on_audit_individual)
        input_layout.addWidget(self.audit_btn)

        layout.addWidget(input_group)

        # Área de progreso
        self.progress_frame = QFrame()
        self.progress_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        self.progress_frame.setVisible(False)

        progress_layout = QVBoxLayout(self.progress_frame)

        self.progress_label = QLabel("Ejecutando auditoría...")
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

        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)

        layout.addWidget(self.progress_frame)

        # Área de resultado
        result_group = QGroupBox("Resultado de Auditoría")
        result_group.setStyleSheet("""
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

        result_layout = QVBoxLayout(result_group)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                padding: 10px;
            }
        """)

        result_layout.addWidget(self.result_text)

        layout.addWidget(result_group)

        return tab

    def _create_batch_tab(self) -> QWidget:
        """Crea el tab de auditoría por lotes"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Info
        info_label = QLabel(
            "Audita múltiples casos secuencialmente con reporte consolidado"
        )
        info_label.setStyleSheet("color: #a1a1aa; font-size: 11pt;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Input
        input_group = QGroupBox("Casos a Auditar")
        input_layout = QVBoxLayout(input_group)

        desc = QLabel("Ingresa los números de caso separados por comas:")
        desc.setStyleSheet("color: #a1a1aa; font-size: 10pt;")
        input_layout.addWidget(desc)

        self.batch_input = QTextEdit()
        self.batch_input.setPlaceholderText(
            "Ejemplo:\n"
            "IHQ251001, IHQ251002, IHQ251003\n"
            "IHQ251004, IHQ251005"
        )
        self.batch_input.setMaximumHeight(120)
        self.batch_input.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                color: #ffffff;
                font-size: 10pt;
                padding: 10px;
            }
        """)
        input_layout.addWidget(self.batch_input)

        self.batch_audit_btn = QPushButton("🚀 Iniciar Auditoría por Lotes")
        self.batch_audit_btn.setProperty("class", "ActionButton")
        self.batch_audit_btn.setMinimumHeight(45)
        self.batch_audit_btn.clicked.connect(self._on_audit_batch)
        input_layout.addWidget(self.batch_audit_btn)

        layout.addWidget(input_group)

        # Tabla de resultados
        result_group = QGroupBox("Resultados")
        result_layout = QVBoxLayout(result_group)

        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4)
        self.batch_table.setHorizontalHeaderLabels([
            "Caso", "Score", "Estado", "Errores"
        ])
        self.batch_table.horizontalHeader().setStretchLastSection(True)
        self.batch_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #2a2a3e;
                color: #ffffff;
                font-weight: bold;
                padding: 10px;
                border: none;
            }
        """)

        result_layout.addWidget(self.batch_table)

        layout.addWidget(result_group)

        return tab

    def _create_repair_tab(self) -> QWidget:
        """Crea el tab de reprocesamiento (FUNC-06)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Descripción
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: #2a2a3e;
                border-left: 4px solid #f59e0b;
                border-radius: 6px;
                padding: 15px;
            }
        """)

        desc_layout = QVBoxLayout(desc_frame)

        desc_title = QLabel("⚠️ Reprocesamiento Completo (FUNC-06)")
        desc_title.setStyleSheet("color: #f59e0b; font-size: 13pt; font-weight: bold;")

        desc_text = QLabel(
            "Esta función elimina los datos antiguos del caso y lo regenera completamente "
            "con los extractores actuales. Úsala cuando hayas modificado los extractores "
            "y necesites validar las correcciones."
        )
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("color: #a1a1aa; font-size: 10pt;")

        desc_layout.addWidget(desc_title)
        desc_layout.addWidget(desc_text)

        layout.addWidget(desc_frame)

        # Input
        input_group = QGroupBox("Seleccionar Caso")
        input_layout = QVBoxLayout(input_group)

        case_layout = QHBoxLayout()
        case_label = QLabel("Número de Caso:")
        case_label.setStyleSheet("color: #a1a1aa; font-size: 11pt;")

        self.repair_input = QLineEdit()
        self.repair_input.setPlaceholderText("Ej: IHQ251007")
        self.repair_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e2e;
                border: 2px solid #3f3f55;
                border-radius: 6px;
                padding: 10px;
                color: #ffffff;
                font-size: 11pt;
            }
            QLineEdit:focus {
                border: 2px solid #f59e0b;
            }
        """)

        case_layout.addWidget(case_label)
        case_layout.addWidget(self.repair_input, 1)
        input_layout.addLayout(case_layout)

        # Botón reprocesar
        self.repair_btn = QPushButton("🔧 Reprocesar Caso")
        self.repair_btn.setStyleSheet("""
            QPushButton {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f59e0b, stop:1 #d97706);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #fbbf24, stop:1 #f59e0b);
            }
            QPushButton:pressed {
                background-color: #d97706;
            }
        """)
        self.repair_btn.clicked.connect(self._on_repair_case)
        input_layout.addWidget(self.repair_btn)

        layout.addWidget(input_group)

        # Resultado comparativo
        comparison_group = QGroupBox("Comparación Antes/Después")
        comparison_layout = QVBoxLayout(comparison_group)

        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #a1a1aa;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                padding: 10px;
            }
        """)

        comparison_layout.addWidget(self.comparison_text)

        layout.addWidget(comparison_group)

        return tab

    def _on_audit_individual(self):
        """Maneja auditoría individual"""
        case_id = self.case_input.text().strip()

        if not case_id:
            QMessageBox.warning(
                self,
                "Caso Requerido",
                "Por favor ingresa un número de caso válido."
            )
            return

        # Determinar tipo de auditoría
        audit_type_text = self.audit_type_combo.currentText()
        if "Inteligente" in audit_type_text:
            audit_type = "inteligente"
        elif "Básica" in audit_type_text:
            audit_type = "basica"
        else:
            audit_type = "completa"

        # Emitir signal
        self.audit_requested.emit(case_id, audit_type)

    def _on_audit_batch(self):
        """Maneja auditoría por lotes"""
        text = self.batch_input.toPlainText().strip()

        if not text:
            QMessageBox.warning(
                self,
                "Casos Requeridos",
                "Por favor ingresa al menos un número de caso."
            )
            return

        # Parsear casos
        cases = [c.strip() for c in text.replace('\n', ',').split(',') if c.strip()]

        if len(cases) == 0:
            QMessageBox.warning(
                self,
                "Casos Inválidos",
                "No se pudieron extraer números de caso válidos."
            )
            return

        # Confirmación
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("Confirmar Auditoría por Lotes")
        msg.setText(f"¿Deseas auditar {len(cases)} casos?")
        msg.setInformativeText("Este proceso puede tomar varios minutos.")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            # Limpiar tabla
            self.batch_table.setRowCount(0)

            # Emitir signal para auditoría por lotes
            self.batch_audit_requested.emit(cases)

    def _on_repair_case(self):
        """Maneja reprocesamiento de caso"""
        case_id = self.repair_input.text().strip()

        if not case_id:
            QMessageBox.warning(
                self,
                "Caso Requerido",
                "Por favor ingresa un número de caso válido."
            )
            return

        # Confirmación con advertencia
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("⚠️ Confirmar Reprocesamiento")
        msg.setText(f"¿Estás seguro de reprocesar el caso {case_id}?")
        msg.setInformativeText(
            "Esta acción:\n"
            "• Eliminará los datos actuales del caso\n"
            "• Regenerará el caso con extractores actuales\n"
            "• No se puede deshacer fácilmente\n\n"
            "Se recomienda tener un backup de la base de datos."
        )
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        if msg.exec() == QMessageBox.Yes:
            # Emitir signal
            self.repair_requested.emit(case_id)

    def _show_help(self):
        """Muestra ayuda sobre auditoría"""
        help_text = """
<h2>Ayuda - Auditoría Inteligente</h2>

<h3>Auditoría Individual</h3>
<p>Valida un caso específico usando el sistema de validación semántica (FUNC-01).</p>
<ul>
  <li><b>Inteligente:</b> Validación completa con análisis semántico (recomendado)</li>
  <li><b>Básica:</b> Validación rápida de campos críticos</li>
  <li><b>Completa:</b> Validación exhaustiva de todos los campos</li>
</ul>

<h3>Auditoría por Lotes</h3>
<p>Audita múltiples casos secuencialmente con reporte consolidado.</p>

<h3>Reprocesar Caso (FUNC-06)</h3>
<p>Elimina datos antiguos y regenera el caso con extractores actuales.</p>
<p><b>⚠️ Úsalo cuando:</b></p>
<ul>
  <li>Hayas modificado extractores en core/extractors/</li>
  <li>Necesites validar correcciones</li>
  <li>El caso tenga errores persistentes</li>
</ul>

<p><b>Para más información:</b> Ver documentación en .claude/agents/data-auditor.md</p>
"""

        msg = QMessageBox(self)
        msg.setWindowTitle("Ayuda - Auditoría IA")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def show_progress(self, visible: bool, progress: int = 0, message: str = ""):
        """Muestra/oculta progreso"""
        self.progress_frame.setVisible(visible)

        if visible:
            self.progress_bar.setValue(progress)
            if message:
                self.progress_label.setText(message)

    def display_audit_result(self, result: Dict[str, Any]):
        """Muestra resultado de auditoría con formato mejorado"""
        self.last_audit_result = result

        # Extraer datos del resultado
        case_id = result.get('case_id', 'DESCONOCIDO')
        score = result.get('score', 0.0)
        estado = result.get('estado', 'DESCONOCIDO')
        errores = result.get('errores', [])
        warnings = result.get('warnings', [])

        # Emoji según score
        if score >= 95:
            emoji = "✅"
            color_status = "#10b981"  # Verde
        elif score >= 80:
            emoji = "⚠️"
            color_status = "#f59e0b"  # Amarillo
        else:
            emoji = "❌"
            color_status = "#ef4444"  # Rojo

        # Crear texto formateado con HTML
        html = f"""
        <style>
            body {{ font-family: 'Consolas', monospace; font-size: 10pt; }}
            .header {{ background-color: #2a2a3e; padding: 15px; border-radius: 6px; margin-bottom: 15px; }}
            .score {{ font-size: 24pt; font-weight: bold; color: {color_status}; }}
            .section {{ background-color: #1e1e2e; padding: 10px; border-left: 3px solid #3b82f6; margin: 10px 0; }}
            .error {{ background-color: #2d1515; padding: 8px; margin: 5px 0; border-left: 3px solid #ef4444; }}
            .warning {{ background-color: #2d2415; padding: 8px; margin: 5px 0; border-left: 3px solid #f59e0b; }}
            .label {{ color: #3b82f6; font-weight: bold; }}
            .value {{ color: #a1a1aa; }}
        </style>

        <div class="header">
            <h2 style="margin: 0; color: #ffffff;">{emoji} Resultado de Auditoría</h2>
            <p style="margin: 5px 0;"><span class="label">Caso:</span> <span class="value">{case_id}</span></p>
            <p style="margin: 5px 0;"><span class="label">Estado:</span> <span class="value">{estado}</span></p>
            <p class="score">{score:.1f}%</p>
        </div>
        """

        # Resumen de problemas
        total_problemas = len(errores) + len(warnings)
        if total_problemas > 0:
            html += f"""
            <div class="section">
                <h3 style="color: #ffffff; margin-top: 0;">📊 Resumen de Problemas</h3>
                <p><span class="label">Errores Críticos:</span> <span style="color: #ef4444; font-weight: bold;">{len(errores)}</span></p>
                <p><span class="label">Advertencias:</span> <span style="color: #f59e0b; font-weight: bold;">{len(warnings)}</span></p>
            </div>
            """

        # Mostrar errores
        if errores:
            html += """
            <div class="section">
                <h3 style="color: #ef4444; margin-top: 0;">❌ Errores Críticos</h3>
            """
            for idx, error in enumerate(errores, 1):
                campo = error.get('campo', 'N/A')
                descripcion = error.get('descripcion', error.get('razon', 'Sin descripción'))
                valor_bd = error.get('valor_bd', 'N/A')
                valor_esperado = error.get('valor_esperado', error.get('valor_ocr', ''))

                html += f"""
                <div class="error">
                    <p style="margin: 0; color: #ffffff;"><b>{idx}. {campo}</b></p>
                    <p style="margin: 5px 0; color: #ef4444;">{descripcion}</p>
                """
                if valor_bd != 'N/A':
                    html += f'<p style="margin: 2px 0; font-size: 9pt;"><span class="label">BD:</span> {valor_bd}</p>'
                if valor_esperado:
                    html += f'<p style="margin: 2px 0; font-size: 9pt;"><span class="label">Esperado:</span> {valor_esperado}</p>'
                html += "</div>"

            html += "</div>"

        # Mostrar warnings
        if warnings:
            html += """
            <div class="section">
                <h3 style="color: #f59e0b; margin-top: 0;">⚠️ Advertencias</h3>
            """
            for idx, warning in enumerate(warnings, 1):
                campo = warning.get('campo', 'N/A')
                descripcion = warning.get('descripcion', warning.get('razon', 'Sin descripción'))

                html += f"""
                <div class="warning">
                    <p style="margin: 0; color: #ffffff;"><b>{idx}. {campo}</b></p>
                    <p style="margin: 5px 0; color: #f59e0b;">{descripcion}</p>
                </div>
                """

            html += "</div>"

        # Mensaje de éxito si no hay problemas
        if total_problemas == 0:
            html += """
            <div class="section" style="border-left-color: #10b981;">
                <h3 style="color: #10b981; margin-top: 0;">✅ Validación Exitosa</h3>
                <p style="color: #a1a1aa;">El caso pasó todas las validaciones sin problemas.</p>
            </div>
            """

        self.result_text.setHtml(html)

    def display_repair_result(self, result: Dict[str, Any]):
        """Muestra resultado de reprocesamiento con comparación antes/después"""
        # Extraer comparación
        comparacion = result.get('comparacion', {})
        antes = comparacion.get('antes', {})
        despues = comparacion.get('despues', {})

        score_antes = antes.get('score', 0.0)
        score_despues = despues.get('score', 0.0)
        mejora = score_despues - score_antes

        # Determinar emoji de mejora
        if mejora > 10:
            emoji_mejora = "🚀"
            color_mejora = "#10b981"
        elif mejora > 0:
            emoji_mejora = "📈"
            color_mejora = "#3b82f6"
        elif mejora == 0:
            emoji_mejora = "➡️"
            color_mejora = "#a1a1aa"
        else:
            emoji_mejora = "📉"
            color_mejora = "#ef4444"

        # Crear HTML formateado
        html = f"""
        <style>
            body {{ font-family: 'Consolas', monospace; font-size: 10pt; }}
            .header {{ background-color: #2a2a3e; padding: 15px; border-radius: 6px; margin-bottom: 15px; }}
            .comparison {{ display: flex; gap: 20px; margin: 15px 0; }}
            .box {{ background-color: #1e1e2e; padding: 15px; border-radius: 6px; flex: 1; }}
            .before {{ border-left: 4px solid #ef4444; }}
            .after {{ border-left: 4px solid #10b981; }}
            .score {{ font-size: 20pt; font-weight: bold; }}
            .label {{ color: #3b82f6; font-weight: bold; }}
            .value {{ color: #a1a1aa; }}
            .improvement {{ background-color: #2a2a3e; padding: 15px; border-radius: 6px; text-align: center; }}
        </style>

        <div class="header">
            <h2 style="margin: 0; color: #ffffff;">🔧 Reprocesamiento Completado</h2>
            <p style="margin: 5px 0; color: #a1a1aa;">Comparación Antes vs Después</p>
        </div>

        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="width: 45%; vertical-align: top; padding-right: 10px;">
                    <div class="box before">
                        <h3 style="margin-top: 0; color: #ef4444;">❌ ANTES</h3>
                        <p class="score" style="color: #ef4444;">{score_antes:.1f}%</p>
                        <p><span class="label">Estado:</span> <span class="value">{antes.get('estado', 'N/A')}</span></p>
                        <p><span class="label">Errores:</span> <span class="value">{antes.get('errores_count', 0)}</span></p>
                    </div>
                </td>
                <td style="width: 10%; text-align: center; vertical-align: middle;">
                    <div style="font-size: 36pt;">{emoji_mejora}</div>
                </td>
                <td style="width: 45%; vertical-align: top; padding-left: 10px;">
                    <div class="box after">
                        <h3 style="margin-top: 0; color: #10b981;">✅ DESPUÉS</h3>
                        <p class="score" style="color: #10b981;">{score_despues:.1f}%</p>
                        <p><span class="label">Estado:</span> <span class="value">{despues.get('estado', 'N/A')}</span></p>
                        <p><span class="label">Errores:</span> <span class="value">{despues.get('errores_count', 0)}</span></p>
                    </div>
                </td>
            </tr>
        </table>

        <div class="improvement">
            <h3 style="margin-top: 0; color: {color_mejora};">
                {emoji_mejora} Mejora: {mejora:+.1f}%
            </h3>
            <p style="color: #a1a1aa; margin-bottom: 0;">
                {"✅ Caso mejorado exitosamente" if mejora > 0 else "⚠️ No hubo mejora significativa" if mejora == 0 else "❌ Caso empeoró"}
            </p>
        </div>
        """

        self.comparison_text.setHtml(html)

    def add_batch_case_result(self, case_id: str, resultado: Dict[str, Any]):
        """Agrega un caso al resultado de auditoría por lotes"""
        # Extraer datos
        metricas = resultado.get('metricas', {})
        auditoria_bd = resultado.get('auditoria_bd', {})

        score = metricas.get('score', 0.0)
        estado = metricas.get('estado', 'DESCONOCIDO')
        errores = auditoria_bd.get('errores', [])
        warnings = auditoria_bd.get('warnings', [])
        total_problemas = len(errores) + len(warnings)

        # Agregar fila a la tabla
        row = self.batch_table.rowCount()
        self.batch_table.insertRow(row)

        # Columna 0: Caso
        item_caso = QTableWidgetItem(case_id)
        self.batch_table.setItem(row, 0, item_caso)

        # Columna 1: Score (con color)
        item_score = QTableWidgetItem(f"{score:.1f}%")
        if score >= 95:
            item_score.setForeground(QColor(16, 185, 129))  # Verde
        elif score >= 80:
            item_score.setForeground(QColor(245, 158, 11))  # Amarillo
        else:
            item_score.setForeground(QColor(239, 68, 68))   # Rojo
        self.batch_table.setItem(row, 1, item_score)

        # Columna 2: Estado
        item_estado = QTableWidgetItem(estado)
        self.batch_table.setItem(row, 2, item_estado)

        # Columna 3: Errores
        item_errores = QTableWidgetItem(str(total_problemas))
        if total_problemas > 0:
            item_errores.setForeground(QColor(239, 68, 68))  # Rojo
        self.batch_table.setItem(row, 3, item_errores)

    def show_batch_progress(self, visible: bool, progress: int = 0, message: str = ""):
        """Muestra progreso de auditoría por lotes"""
        # Reutilizar progress_frame del tab individual
        # (Podríamos crear uno dedicado si es necesario)
        self.progress_frame.setVisible(visible)

        if visible:
            self.progress_bar.setValue(progress)
            if message:
                self.progress_label.setText(message)


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
    window.setWindowTitle("AuditIAView - Demo")
    window.resize(1200, 800)

    audit_view = AuditIAView()

    # Conectar signals de prueba
    def on_audit(case_id, audit_type):
        print(f"Auditar: {case_id} - Tipo: {audit_type}")
        audit_view.show_progress(True, 50, "Procesando...")

        # Simular resultado
        import time
        from PySide6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: audit_view.display_audit_result({
            'case_id': case_id,
            'score': 92.5,
            'estado': 'COMPLETO',
            'resultado_completo': {
                'errores': [
                    {'campo': 'Ki67', 'tipo': 'FORMATO', 'descripcion': 'Valor no estándar'}
                ]
            }
        }))

    def on_repair(case_id):
        print(f"Reprocesar: {case_id}")

    audit_view.audit_requested.connect(on_audit)
    audit_view.repair_requested.connect(on_repair)

    window.setCentralWidget(audit_view)
    window.show()

    sys.exit(app.exec())
