#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS - Aplicación Principal PySide6
Aplicación principal del sistema EVARISIS Cirugía Oncológica

Este es el punto de entrada principal de la interfaz PySide6
"""

import sys
from pathlib import Path
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QStackedWidget, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

# Importar componentes
from pyside6_ui.components.theme_manager import get_theme_manager
from pyside6_ui.components.sidebar_nav import SidebarNav
from pyside6_ui.views.welcome_view import WelcomeView
from pyside6_ui.views.dashboard_view import DashboardView
from pyside6_ui.views.database_view import DatabaseView
from pyside6_ui.views.audit_view import AuditIAView
from pyside6_ui.views.web_view import WebAutoView

# Importar workers
from pyside6_ui.workers import OCRWorker, ExportWorker, AuditWorker, RepairWorker


class EvarisisApp(QMainWindow):
    """
    Aplicación principal de EVARISIS

    Arquitectura:
        - Header institucional fijo
        - Sidebar de navegación colapsable
        - Área de contenido con QStackedWidget
        - Vistas modulares (Welcome, Database, Dashboard, etc.)
    """

    def __init__(self):
        super().__init__()

        # Configuración de la ventana
        self.setWindowTitle("EVARISIS - Cirugía Oncológica (PySide6)")
        self.resize(1400, 850)

        # Cargar tema inicial
        self.theme_manager = get_theme_manager()
        self.theme_manager.load_theme('darkly')

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Crear componentes
        self._create_header(main_layout)
        self._create_body(main_layout)

    def _create_header(self, parent_layout):
        """Crea el header institucional"""
        header = QFrame()
        header.setObjectName("HeaderFrame")
        header.setFixedHeight(70)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Logo y título (izquierda)
        logo_layout = QVBoxLayout()

        logo_title = QLabel("EVARISIS")
        logo_title.setObjectName("LogoTexto")

        logo_sub = QLabel("Hospital Universitario del Valle")
        logo_sub.setObjectName("Subtitulo")

        logo_layout.addWidget(logo_title)
        logo_layout.addWidget(logo_sub)
        logo_layout.setAlignment(Qt.AlignVCenter)

        # Usuario (derecha)
        user_label = QLabel("👤 Dr. Usuario Sistema")
        user_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 14pt;
        """)

        header_layout.addLayout(logo_layout)
        header_layout.addStretch()
        header_layout.addWidget(user_label)

        parent_layout.addWidget(header)

    def _create_body(self, parent_layout):
        """Crea el cuerpo principal (sidebar + content)"""
        body_frame = QFrame()
        body_layout = QHBoxLayout(body_frame)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar de navegación
        self.sidebar = SidebarNav()
        self.sidebar.add_nav_button("🏠", "Inicio", "home")
        self.sidebar.add_nav_button("🗄️", "Base de Datos", "database")
        self.sidebar.add_nav_button("📈", "Dashboard", "dashboard")
        self.sidebar.add_nav_button("🤖", "Auditoría IA", "audit")
        self.sidebar.add_nav_button("🌐", "QHORTE Web", "web")

        # Conectar navegación
        self.sidebar.nav_changed.connect(self.on_nav_changed)

        # Área de contenido (QStackedWidget)
        self.pages = QStackedWidget()

        # Crear vistas
        self.page_welcome = WelcomeView()
        self.page_dashboard = DashboardView()
        self.page_database = DatabaseView()
        self.page_audit = AuditIAView()      # ✅ Vista completa migrada
        self.page_web = WebAutoView()        # ✅ Vista completa migrada

        # Conectar signals de DatabaseView con workers
        self.page_database.import_requested.connect(self._on_import_pdfs)
        self.page_database.export_requested.connect(self._on_export_data)

        # Conectar signals de AuditIAView con workers
        self.page_audit.audit_requested.connect(self._on_audit_case)
        self.page_audit.batch_audit_requested.connect(self._on_batch_audit)
        self.page_audit.repair_requested.connect(self._on_repair_case)

        # Conectar signals de WebAutoView
        self.page_web.upload_requested.connect(self._on_upload_web)
        self.page_web.config_saved.connect(self._on_web_config_saved)

        # Conectar signals de WelcomeView
        self.page_welcome.navigation_requested.connect(self._on_welcome_navigation)

        # Agregar vistas al stack
        self.pages.addWidget(self.page_welcome)    # Index 0
        self.pages.addWidget(self.page_database)   # Index 1
        self.pages.addWidget(self.page_dashboard)  # Index 2
        self.pages.addWidget(self.page_audit)      # Index 3
        self.pages.addWidget(self.page_web)        # Index 4

        # Ensamblar body
        body_layout.addWidget(self.sidebar)
        body_layout.addWidget(self.pages, 1)  # stretch=1

        parent_layout.addWidget(body_frame)

        # Estado inicial
        self.pages.setCurrentIndex(0)

    def on_nav_changed(self, nav_id: str):
        """
        Maneja el cambio de navegación

        Args:
            nav_id: ID de navegación seleccionado
        """
        navigation_map = {
            'home': 0,
            'database': 1,
            'dashboard': 2,
            'audit': 3,
            'web': 4
        }

        index = navigation_map.get(nav_id, 0)
        self.pages.setCurrentIndex(index)

        # Cargar datos específicos de cada vista
        if nav_id == 'home':
            # Recargar estadísticas de la pantalla de bienvenida
            self.page_welcome.load_system_data()
        elif nav_id == 'dashboard':
            # Cargar datos del dashboard cuando se navega a esa vista
            self.page_dashboard.load_data_from_database()
        elif nav_id == 'database':
            # Recargar datos de la base de datos cuando se navega a esa vista
            self.page_database.load_data_from_database()

        # print(f"Navegación cambiada a: {nav_id} (index: {index})")  # Deshabilitado: stdout cerrado

    def _on_welcome_navigation(self, nav_id: str):
        """Maneja navegación desde la pantalla de bienvenida"""
        # Delegar a on_nav_changed
        self.on_nav_changed(nav_id)

    # ===== Handlers para DatabaseView =====

    def _on_import_pdfs(self, pdf_files: list):
        """Maneja importación de PDFs con OCR"""
        # print(f"Iniciando importación de {len(pdf_files)} archivos...")  # Deshabilitado: stdout cerrado

        # Crear worker OCR
        self.ocr_worker = OCRWorker(pdf_files)

        # Conectar signals
        self.ocr_worker.progress.connect(
            lambda p, m: self.page_database.show_progress(True, p, m)
        )

        self.ocr_worker.finished.connect(self._on_import_finished)
        self.ocr_worker.error.connect(self._on_import_error)

        # Iniciar procesamiento
        self.ocr_worker.start()

    def _on_import_finished(self, results: dict):
        """Maneja finalización de importación"""
        from PySide6.QtWidgets import QMessageBox

        success_count = results.get('success_count', 0)
        failed_count = results.get('failed_count', 0)

        msg = QMessageBox(self)
        msg.setWindowTitle("Importación Completada")

        if failed_count == 0:
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"Importación exitosa de {success_count} casos")
        else:
            msg.setIcon(QMessageBox.Warning)
            msg.setText(
                f"Importación completada con advertencias:\n\n"
                f"Exitosos: {success_count}\n"
                f"Fallidos: {failed_count}"
            )

        msg.exec()

        # Recargar datos en tabla
        self.page_database.load_data_from_database()

    def _on_import_error(self, error_msg: str):
        """Maneja error en importación"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Error en Importación",
            f"Ocurrió un error durante la importación:\n\n{error_msg}"
        )

    def _on_export_data(self):
        """Maneja exportación de datos a Excel"""
        from PySide6.QtWidgets import QFileDialog
        from datetime import datetime

        # Solicitar ubicación de archivo
        default_name = f"evarisis_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Exportación",
            default_name,
            "Excel Files (*.xlsx);;All Files (*)"
        )

        if file_path:
            # Obtener DataFrame actual
            df = self.page_database.current_dataframe

            if df.empty:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(
                    self,
                    "Sin Datos",
                    "No hay datos para exportar."
                )
                return

            # Crear worker de exportación
            self.export_worker = ExportWorker(df, file_path, include_formatting=True)

            # Conectar signals
            self.export_worker.progress.connect(
                lambda p, m: self.page_database.show_progress(True, p, m)
            )

            self.export_worker.finished.connect(self._on_export_finished)
            self.export_worker.error.connect(self._on_export_error)

            # Iniciar exportación
            self.export_worker.start()

    def _on_export_finished(self, file_path: str):
        """Maneja finalización de exportación"""
        from PySide6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Exportación Exitosa")
        msg.setText(f"Datos exportados exitosamente")
        msg.setInformativeText(f"Archivo: {file_path}")
        msg.exec()

        self.page_database.show_progress(False)

    def _on_export_error(self, error_msg: str):
        """Maneja error en exportación"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Error en Exportación",
            f"Ocurrió un error durante la exportación:\n\n{error_msg}"
        )

        self.page_database.show_progress(False)

    # ===== Handlers para AuditIAView =====

    def _on_audit_case(self, case_id: str, audit_type: str):
        """Maneja auditoría de caso"""
        # print(f"Auditando caso {case_id} con tipo {audit_type}...")  # Deshabilitado: stdout cerrado

        # Crear worker de auditoría
        self.audit_worker = AuditWorker(case_id, audit_type)

        # Conectar signals
        self.audit_worker.progress.connect(
            lambda p, m: self.page_audit.show_progress(True, p, m)
        )

        self.audit_worker.finished.connect(self._on_audit_finished)
        self.audit_worker.error.connect(self._on_audit_error)

        # Iniciar auditoría
        self.audit_worker.start()

    def _on_audit_finished(self, result: dict):
        """Maneja finalización de auditoría"""
        # Mostrar resultado en vista
        self.page_audit.display_audit_result(result)
        self.page_audit.show_progress(False)

    def _on_audit_error(self, error_msg: str):
        """Maneja error en auditoría"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Error en Auditoría",
            f"Ocurrió un error durante la auditoría:\n\n{error_msg}"
        )

        self.page_audit.show_progress(False)

    def _on_batch_audit(self, case_ids: list):
        """Maneja auditoría por lotes"""
        from pyside6_ui.workers import BatchAuditWorker

        # print(f"Iniciando auditoría por lotes de {len(case_ids)} casos...")  # Deshabilitado: stdout cerrado

        # Crear worker de auditoría por lotes
        self.batch_audit_worker = BatchAuditWorker(case_ids, 'inteligente')

        # Conectar signals
        self.batch_audit_worker.progress.connect(
            lambda p, m: self.page_audit.show_batch_progress(True, p, m)
        )

        # Signal de caso completado (agregar a tabla)
        self.batch_audit_worker.case_completed.connect(
            lambda case_id, resultado: self.page_audit.add_batch_case_result(case_id, resultado)
        )

        self.batch_audit_worker.finished.connect(self._on_batch_audit_finished)
        self.batch_audit_worker.error.connect(self._on_batch_audit_error)

        # Iniciar auditoría por lotes
        self.batch_audit_worker.start()

    def _on_batch_audit_finished(self, results: dict):
        """Maneja finalización de auditoría por lotes"""
        from PySide6.QtWidgets import QMessageBox

        total = results.get('total', 0)
        procesados = len(results.get('cases_processed', []))
        fallidos = len(results.get('cases_failed', []))
        avg_score = results.get('average_score', 0.0)

        msg = QMessageBox(self)
        msg.setWindowTitle("Auditoría por Lotes Completada")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Auditoría de {total} casos completada")
        msg.setInformativeText(
            f"Procesados exitosamente: {procesados}\n"
            f"Fallidos: {fallidos}\n"
            f"Score promedio: {avg_score:.1f}%"
        )
        msg.exec()

        self.page_audit.show_batch_progress(False)

    def _on_batch_audit_error(self, error_msg: str):
        """Maneja error en auditoría por lotes"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Error en Auditoría por Lotes",
            f"Ocurrió un error durante la auditoría por lotes:\n\n{error_msg}"
        )

        self.page_audit.show_batch_progress(False)

    def _on_repair_case(self, case_id: str):
        """Maneja reprocesamiento de caso"""
        # print(f"Reprocesando caso {case_id}...")  # Deshabilitado: stdout cerrado

        # Crear worker de reparación
        self.repair_worker = RepairWorker(case_id)

        # Conectar signals
        self.repair_worker.progress.connect(
            lambda p, m: self.page_audit.show_progress(True, p, m)
        )

        self.repair_worker.finished.connect(self._on_repair_finished)
        self.repair_worker.error.connect(self._on_repair_error)

        # Iniciar reprocesamiento
        self.repair_worker.start()

    def _on_repair_finished(self, result: dict):
        """Maneja finalización de reprocesamiento"""
        # Mostrar resultado comparativo
        self.page_audit.display_repair_result(result)
        self.page_audit.show_progress(False)

        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Reprocesamiento Completado",
            f"El caso ha sido reprocesado exitosamente.\n\n"
            f"Revisa la comparación antes/después en la vista."
        )

    def _on_repair_error(self, error_msg: str):
        """Maneja error en reprocesamiento"""
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(
            self,
            "Error en Reprocesamiento",
            f"Ocurrió un error durante el reprocesamiento:\n\n{error_msg}"
        )

        self.page_audit.show_progress(False)

    # ===== Handlers para WebAutoView =====

    def _on_upload_web(self, cases: list):
        """Maneja carga de casos a QHORTE Web"""
        # print(f"Cargando {len(cases)} casos a QHORTE...")  # Deshabilitado: stdout cerrado

        from PySide6.QtWidgets import QMessageBox

        # Mostrar información sobre casos seleccionados
        casos_str = "\n".join([f"• {c.get('numero', 'N/A')} - {c.get('paciente', 'N/A')}" for c in cases[:5]])
        if len(cases) > 5:
            casos_str += f"\n... y {len(cases) - 5} casos más"

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Automatización Web - En Desarrollo")
        msg.setText(f"Casos seleccionados para carga ({len(cases)} total):")
        msg.setDetailedText(casos_str)
        msg.setInformativeText(
            "\n✅ UI Completada:\n"
            "  • Selector de casos desde BD\n"
            "  • Filtros (Completos, Con Errores, etc.)\n"
            "  • Panel de configuración\n"
            "  • Monitoreo en tiempo real\n"
            "  • Sistema de logging\n\n"
            "⏳ Pendiente:\n"
            "  • Worker de automatización web (Selenium/Playwright)\n"
            "  • Integración con credenciales QHORTE\n"
            "  • Mapeo de campos formulario web\n\n"
            "📝 Nota: La infraestructura está lista. Solo falta implementar\n"
            "el módulo de automatización web con las credenciales reales."
        )
        msg.exec()

        # Log en la vista
        self.page_web.add_log_message(f"✓ Casos seleccionados: {len(cases)}")
        self.page_web.add_log_message("⏳ Esperando implementación de worker de automatización web")

    def _on_web_config_saved(self, config: dict):
        """Maneja guardado de configuración web"""
        # print(f"Configuración web guardada: {config.get('url', 'N/A')}")  # Deshabilitado: stdout cerrado

        # TODO: Guardar configuración en archivo seguro
        # Por ahora, solo log


def run_app():
    """Función para ejecutar la aplicación"""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Aplicar estilos globales
    theme_mgr = get_theme_manager()
    theme_mgr.load_theme('darkly')

    # Crear y mostrar ventana principal
    window = EvarisisApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
