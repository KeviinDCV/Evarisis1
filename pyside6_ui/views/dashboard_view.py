#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DashboardView - Vista de Dashboard con Métricas
Pantalla principal de métricas y KPIs del sistema
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                                QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
                                QScrollArea)
from PySide6.QtCore import Qt
from pyside6_ui.components.kpi_card import KPICard
from pyside6_ui.components.chart_widget import ChartWidget
import pandas as pd
from datetime import datetime
import logging

class DashboardView(QWidget):
    """Vista de dashboard con KPIs y métricas"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("PageContent")

        # DataFrame para datos
        self.df = None

        # Referencias a widgets - Tab 1
        self.diagnosis_chart = None
        self.top_diagnosis_table = None

        # Referencias a widgets - Tab 2 (Temporal)
        self.tiempo_proceso_chart = None
        self.throughput_chart = None
        self.edad_ki67_chart = None

        # Referencias a widgets - Tab 3 (Completitud y Calidad)
        self.missingness_chart = None
        self.top_responsables_chart = None
        self.longitud_diagnostico_chart = None

        # Referencias a widgets - Tab 4 (Biomarcadores)
        self.ki67_chart = None
        self.her2_chart = None
        self.re_rp_chart = None
        self.pdl1_chart = None

        # Referencias a widgets - Tab 5 (Servicios y Médicos)
        self.malignidad_chart = None
        self.servicios_chart = None
        self.organos_chart = None

        self._create_ui()

    def _create_ui(self):
        """Crea la interfaz del dashboard con tabs"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Título principal
        title = QLabel("📈 Dashboard General")
        title.setObjectName("PageTitle")
        layout.addWidget(title)

        # Crear pestañas
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #3f3f55;
                background-color: #1e1e2e;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #252538;
                color: #a1a1aa;
                padding: 10px 20px;
                border: 1px solid #3f3f55;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3b82f6;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #2e2e42;
            }
        """)

        # Tab 1: Estadísticas Generales
        tab1 = self._create_general_stats_tab()
        self.tabs.addTab(tab1, "📊 Estadísticas Generales")

        # Tab 2: Análisis Temporal
        tab2 = self._create_temporal_analysis_tab()
        self.tabs.addTab(tab2, "📈 Análisis Temporal")

        # Tab 3: Completitud y Calidad
        tab3 = self._create_quality_tab()
        self.tabs.addTab(tab3, "✅ Completitud y Calidad")

        # Tab 4: Biomarcadores
        tab4 = self._create_biomarkers_tab()
        self.tabs.addTab(tab4, "🧬 Biomarcadores")

        # Tab 5: Servicios y Médicos
        tab5 = self._create_services_tab()
        self.tabs.addTab(tab5, "🏥 Servicios y Órganos")

        layout.addWidget(self.tabs)

    def _create_general_stats_tab(self):
        """Crea el tab de estadísticas generales"""
        tab = QWidget()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e2e; }")

        # Contenedor scrollable
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Sección 1: KPI Cards
        kpi_frame = QFrame()
        kpi_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        kpi_layout = QHBoxLayout(kpi_frame)
        kpi_layout.setSpacing(15)

        # Crear KPI cards
        self.kpi_total = KPICard("Total Registros", "0", "📁", "#3b82f6")
        self.kpi_biomarcadores = KPICard("Con Biomarcadores", "0", "🧬", "#10b981")
        self.kpi_malignos = KPICard("Casos Malignos", "0", "⚠️", "#ef4444")
        self.kpi_dias_datos = KPICard("Días de Datos", "0", "📅", "#f59e0b")

        kpi_layout.addWidget(self.kpi_total)
        kpi_layout.addWidget(self.kpi_biomarcadores)
        kpi_layout.addWidget(self.kpi_malignos)
        kpi_layout.addWidget(self.kpi_dias_datos)

        layout.addWidget(kpi_frame)

        # Sección 2: Gráfico de Distribución de Diagnósticos
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)

        chart_title = QLabel("🏥 Distribución por Tipos de Diagnóstico")
        chart_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        chart_layout.addWidget(chart_title)

        # ChartWidget para el gráfico
        self.diagnosis_chart = ChartWidget(figsize=(10, 5))
        chart_layout.addWidget(self.diagnosis_chart)

        layout.addWidget(chart_frame)

        # Sección 3: Tabla Top 10 Diagnósticos
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)

        table_title = QLabel("🔝 Top 10 Diagnósticos Principales")
        table_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        table_layout.addWidget(table_title)

        # QTableWidget para la tabla
        self.top_diagnosis_table = QTableWidget()
        self.top_diagnosis_table.setColumnCount(3)
        self.top_diagnosis_table.setHorizontalHeaderLabels(["Diagnóstico Principal", "Frecuencia", "% del Total"])
        self.top_diagnosis_table.horizontalHeader().setStretchLastSection(True)
        self.top_diagnosis_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_diagnosis_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.top_diagnosis_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.top_diagnosis_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.top_diagnosis_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.top_diagnosis_table.setAlternatingRowColors(True)
        self.top_diagnosis_table.setMaximumHeight(350)

        self.top_diagnosis_table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1e2e;
                border: 1px solid #3f3f55;
                border-radius: 6px;
                color: #ffffff;
                gridline-color: #3f3f55;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #3b82f6;
            }
            QHeaderView::section {
                background-color: #252538;
                color: #ffffff;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #3b82f6;
                font-weight: bold;
            }
        """)

        table_layout.addWidget(self.top_diagnosis_table)
        layout.addWidget(table_frame)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout del tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        return tab

    def _create_temporal_analysis_tab(self):
        """Crea el tab de análisis temporal"""
        tab = QWidget()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e2e; }")

        # Contenedor scrollable
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Gráfico 1: Tiempo de Proceso (Boxplot)
        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame1_layout = QVBoxLayout(frame1)

        title1 = QLabel("⏱️ Tiempo de Proceso (días)")
        title1.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame1_layout.addWidget(title1)

        self.tiempo_proceso_chart = ChartWidget(figsize=(10, 5))
        frame1_layout.addWidget(self.tiempo_proceso_chart)

        layout.addWidget(frame1)

        # Gráfico 2: Throughput Semanal (Línea)
        frame2 = QFrame()
        frame2.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame2_layout = QVBoxLayout(frame2)

        title2 = QLabel("📊 Throughput Semanal (casos por semana)")
        title2.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame2_layout.addWidget(title2)

        self.throughput_chart = ChartWidget(figsize=(10, 5))
        frame2_layout.addWidget(self.throughput_chart)

        layout.addWidget(frame2)

        # Gráfico 3: Edad vs Ki-67 (Scatter)
        frame3 = QFrame()
        frame3.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame3_layout = QVBoxLayout(frame3)

        title3 = QLabel("🔬 Correlación: Edad vs Ki-67")
        title3.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame3_layout.addWidget(title3)

        self.edad_ki67_chart = ChartWidget(figsize=(10, 5))
        frame3_layout.addWidget(self.edad_ki67_chart)

        layout.addWidget(frame3)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout del tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        return tab

    def _create_quality_tab(self):
        """Crea el tab de completitud y calidad"""
        tab = QWidget()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e2e; }")

        # Contenedor scrollable
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Gráfico 1: Campos Vacíos (%)
        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame1_layout = QVBoxLayout(frame1)

        title1 = QLabel("📊 Campos Vacíos por Columna (%)")
        title1.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame1_layout.addWidget(title1)

        self.missingness_chart = ChartWidget(figsize=(10, 5))
        frame1_layout.addWidget(self.missingness_chart)

        layout.addWidget(frame1)

        # Gráfico 2: Productividad por Responsable (Top 10)
        frame2 = QFrame()
        frame2.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame2_layout = QVBoxLayout(frame2)

        title2 = QLabel("👨‍⚕️ Productividad por Responsable (Top 10)")
        title2.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame2_layout.addWidget(title2)

        self.top_responsables_chart = ChartWidget(figsize=(10, 5))
        frame2_layout.addWidget(self.top_responsables_chart)

        layout.addWidget(frame2)

        # Gráfico 3: Longitud del Diagnóstico
        frame3 = QFrame()
        frame3.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame3_layout = QVBoxLayout(frame3)

        title3 = QLabel("📝 Distribución: Longitud de Diagnósticos")
        title3.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame3_layout.addWidget(title3)

        self.longitud_diagnostico_chart = ChartWidget(figsize=(10, 5))
        frame3_layout.addWidget(self.longitud_diagnostico_chart)

        layout.addWidget(frame3)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout del tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        return tab

    def _create_biomarkers_tab(self):
        """Crea el tab de análisis de biomarcadores"""
        tab = QWidget()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e2e; }")

        # Contenedor scrollable
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Grid 2x2 para los 4 gráficos
        # Fila 1: Ki-67 y HER2
        row1_frame = QFrame()
        row1_frame.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        row1_layout = QHBoxLayout(row1_frame)
        row1_layout.setSpacing(15)

        # Gráfico 1: Ki-67 (Histograma)
        ki67_frame = QFrame()
        ki67_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        ki67_layout = QVBoxLayout(ki67_frame)

        ki67_title = QLabel("📊 Distribución Ki-67 (%)")
        ki67_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        ki67_layout.addWidget(ki67_title)

        self.ki67_chart = ChartWidget(figsize=(8, 5))
        ki67_layout.addWidget(self.ki67_chart)

        # Gráfico 2: HER2 (Barras)
        her2_frame = QFrame()
        her2_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        her2_layout = QVBoxLayout(her2_frame)

        her2_title = QLabel("🎯 Distribución HER2 (Score)")
        her2_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        her2_layout.addWidget(her2_title)

        self.her2_chart = ChartWidget(figsize=(8, 5))
        her2_layout.addWidget(self.her2_chart)

        row1_layout.addWidget(ki67_frame)
        row1_layout.addWidget(her2_frame)

        layout.addWidget(row1_frame)

        # Fila 2: RE/RP y PDL-1
        row2_frame = QFrame()
        row2_frame.setStyleSheet("QFrame { background-color: transparent; border: none; }")
        row2_layout = QHBoxLayout(row2_frame)
        row2_layout.setSpacing(15)

        # Gráfico 3: RE/RP (Barras agrupadas)
        re_rp_frame = QFrame()
        re_rp_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        re_rp_layout = QVBoxLayout(re_rp_frame)

        re_rp_title = QLabel("🔬 Receptores Hormonales (RE/RP)")
        re_rp_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        re_rp_layout.addWidget(re_rp_title)

        self.re_rp_chart = ChartWidget(figsize=(8, 5))
        re_rp_layout.addWidget(self.re_rp_chart)

        # Gráfico 4: PDL-1 (Barras)
        pdl1_frame = QFrame()
        pdl1_frame.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        pdl1_layout = QVBoxLayout(pdl1_frame)

        pdl1_title = QLabel("💉 Distribución PD-L1")
        pdl1_title.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        pdl1_layout.addWidget(pdl1_title)

        self.pdl1_chart = ChartWidget(figsize=(8, 5))
        pdl1_layout.addWidget(self.pdl1_chart)

        row2_layout.addWidget(re_rp_frame)
        row2_layout.addWidget(pdl1_frame)

        layout.addWidget(row2_frame)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout del tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        return tab

    def _create_services_tab(self):
        """Crea el tab de análisis de servicios y órganos"""
        tab = QWidget()

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e2e; }")

        # Contenedor scrollable
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(20)

        # Gráfico 1: Distribución de Malignidad (Pie chart)
        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame1_layout = QVBoxLayout(frame1)

        title1 = QLabel("⚠️ Distribución de Malignidad")
        title1.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame1_layout.addWidget(title1)

        self.malignidad_chart = ChartWidget(figsize=(10, 5))
        frame1_layout.addWidget(self.malignidad_chart)

        layout.addWidget(frame1)

        # Gráfico 2: Top Servicios (Barras)
        frame2 = QFrame()
        frame2.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame2_layout = QVBoxLayout(frame2)

        title2 = QLabel("🏥 Distribución por Servicios (Top 12)")
        title2.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame2_layout.addWidget(title2)

        self.servicios_chart = ChartWidget(figsize=(10, 5))
        frame2_layout.addWidget(self.servicios_chart)

        layout.addWidget(frame2)

        # Gráfico 3: Top Órganos (Barras)
        frame3 = QFrame()
        frame3.setStyleSheet("""
            QFrame {
                background-color: #252538;
                border-radius: 8px;
                border: 1px solid #3f3f55;
                padding: 15px;
            }
        """)
        frame3_layout = QVBoxLayout(frame3)

        title3 = QLabel("🫀 Distribución por Órganos (Top 12)")
        title3.setStyleSheet("color: #ffffff; font-size: 14pt; font-weight: bold; background: transparent; border: none;")
        frame3_layout.addWidget(title3)

        self.organos_chart = ChartWidget(figsize=(10, 5))
        frame3_layout.addWidget(self.organos_chart)

        layout.addWidget(frame3)

        layout.addStretch()

        scroll.setWidget(content)

        # Layout del tab
        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        return tab

    def load_data_from_database(self):
        """Carga datos desde la base de datos y actualiza el dashboard"""
        try:
            from core.database_manager import get_all_records_as_dataframe

            self.df = get_all_records_as_dataframe()

            if self.df is None or self.df.empty:
                logging.warning("No hay datos en la base de datos")
                return

            # Actualizar KPIs
            self._update_kpis()

            # Actualizar gráfico de diagnósticos
            self._update_diagnosis_chart()

            # Actualizar tabla top 10
            self._update_top_diagnosis_table()

            # Actualizar gráficos temporales
            self._update_temporal_charts()

            # Actualizar gráficos de calidad
            self._update_quality_charts()

            # Actualizar gráficos de biomarcadores
            self._update_biomarker_charts()

            # Actualizar gráficos de servicios
            self._update_services_charts()

        except Exception as e:
            logging.error(f"Error cargando datos del dashboard: {e}", exc_info=True)

    def _update_kpis(self):
        """Actualiza las tarjetas KPI con datos de la BD"""
        if self.df is None or self.df.empty:
            return

        # Total de registros
        total_records = len(self.df)
        self.kpi_total.update_value(str(total_records))

        # Contar registros con biomarcadores válidos
        biomarker_keywords = ['her2', 'ki67', 'ki-67', 'er', 'pr', 'pdl1', 'p16']
        with_biomarkers = self._count_valid_biomarkers(biomarker_keywords)
        self.kpi_biomarcadores.update_value(str(with_biomarkers))

        # Contar casos malignos
        malignant_count = 0
        malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]
        if malignidad_cols:
            try:
                malignant_count = (self.df[malignidad_cols[0]].astype(str).str.contains('MALIGNO', case=False, na=False)).sum()
            except Exception as e:
                logging.warning(f"Error contando casos malignos: {e}")

        self.kpi_malignos.update_value(str(malignant_count))

        # Calcular días de datos
        days_of_data = self._calculate_days_of_data()
        self.kpi_dias_datos.update_value(str(days_of_data))

    def _count_valid_biomarkers(self, keywords):
        """Cuenta registros con biomarcadores válidos"""
        if not keywords or self.df is None or self.df.empty:
            return 0

        count = 0
        bio_cols = [col for col in self.df.columns if any(kw in col.lower() for kw in keywords)]

        if not bio_cols:
            return 0

        for _, row in self.df.iterrows():
            has_valid_biomarker = False
            for col in bio_cols:
                value = str(row[col]) if pd.notna(row[col]) else ""
                if self._is_valid_biomarker_result(value):
                    has_valid_biomarker = True
                    break
            if has_valid_biomarker:
                count += 1

        return count

    def _is_valid_biomarker_result(self, text):
        """Verifica si el texto contiene un resultado válido de biomarcador"""
        if not text or text.strip() == "" or text.lower() in ['nan', 'null', 'none', 'n/a']:
            return False

        text = text.lower().strip()

        # Patrones que indican resultados válidos
        import re
        valid_patterns = [
            r'\b(positiv|negativ)\w*\b',
            r'\d+\s*%',
            r'score\s*[:\-]?\s*[0-3][\+]?',
            r'\b(intensidad|débil|fuerte|moderada?|intensa?)\b',
            r'\b[0-3]\+?\b',
            r'\b(presente|ausente|expresión|sobreexpresión)\b',
        ]

        for pattern in valid_patterns:
            if re.search(pattern, text):
                return True

        return False

    def _calculate_days_of_data(self):
        """Calcula los días de datos disponibles"""
        if self.df is None or self.df.empty:
            return 0

        fecha_cols = [col for col in self.df.columns if 'fecha' in col.lower() and 'nacimiento' not in col.lower()]

        if not fecha_cols:
            return 0

        # Intentar parsear fechas
        for fecha_col in fecha_cols:
            try:
                fechas = pd.to_datetime(self.df[fecha_col], errors='coerce')
                fechas_validas = fechas.dropna()

                if not fechas_validas.empty and len(fechas_validas) > 0:
                    fecha_min = fechas_validas.min()
                    fecha_max = fechas_validas.max()
                    days = (fecha_max - fecha_min).days
                    if days >= 0:
                        return days
            except Exception as e:
                logging.debug(f"Error parseando fechas de columna {fecha_col}: {e}")
                continue

        return 0

    def _update_diagnosis_chart(self):
        """Actualiza el gráfico de distribución de diagnósticos"""
        if self.df is None or self.df.empty or self.diagnosis_chart is None:
            return

        try:
            # Encontrar columna de diagnóstico
            diag_cols = [col for col in self.df.columns if 'diagnostico' in col.lower() and 'principal' not in col.lower()]
            if not diag_cols:
                diag_cols = [col for col in self.df.columns if 'diagnostico' in col.lower()]

            if not diag_cols:
                return

            diag_col = diag_cols[0]

            # Limpiar chart
            self.diagnosis_chart.clear()

            # Clasificar diagnósticos en categorías
            diagnosticos = self.df[diag_col].dropna()

            categorias = {
                'Carcinomas': 0,
                'Adenocarcinomas': 0,
                'Lesiones Benignas': 0,
                'Procesos Inflamatorios': 0,
                'Otros': 0
            }

            for diag in diagnosticos:
                diag_upper = str(diag).upper()
                if 'CARCINOMA' in diag_upper and 'ADENOCARCINOMA' not in diag_upper:
                    categorias['Carcinomas'] += 1
                elif 'ADENOCARCINOMA' in diag_upper:
                    categorias['Adenocarcinomas'] += 1
                elif any(word in diag_upper for word in ['BENIGNO', 'HIPERPLASIA', 'ADENOMA']):
                    categorias['Lesiones Benignas'] += 1
                elif any(word in diag_upper for word in ['INFLAMATORIO', 'INFLAMACION']):
                    categorias['Procesos Inflamatorios'] += 1
                else:
                    categorias['Otros'] += 1

            # Crear gráfico de barras
            labels = list(categorias.keys())
            values = list(categorias.values())
            colors = ['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc']

            # Usar el método plot_bar del ChartWidget
            self.diagnosis_chart.plot_bar(labels, values, color=colors)
            self.diagnosis_chart.set_title('Distribución por Tipos de Diagnóstico')
            self.diagnosis_chart.set_labels('', 'Número de Casos')

            # Añadir valores sobre las barras manualmente
            for i, (label, value) in enumerate(zip(labels, values)):
                if value > 0:
                    self.diagnosis_chart.ax.text(i, value + (max(values) * 0.02),
                                                str(value), ha='center', va='bottom',
                                                color='#ffffff', fontsize=10)

            self.diagnosis_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de diagnósticos: {e}", exc_info=True)

    def _update_top_diagnosis_table(self):
        """Actualiza la tabla de top 10 diagnósticos principales"""
        if self.df is None or self.df.empty or self.top_diagnosis_table is None:
            return

        try:
            # Limpiar tabla
            self.top_diagnosis_table.setRowCount(0)

            # Buscar columna "Diagnostico Principal"
            diag_col = None
            for col in self.df.columns:
                if col.lower() == 'diagnostico principal':
                    diag_col = col
                    break

            if diag_col is None:
                logging.warning("No se encontró la columna 'Diagnostico Principal'")
                return

            # Filtrar valores vacíos
            df_filtered = self.df[self.df[diag_col].notna() & (self.df[diag_col] != '') & (self.df[diag_col] != 'N/A')]

            if df_filtered.empty:
                return

            # Contar diagnósticos
            diag_counts = df_filtered[diag_col].value_counts().head(10)
            total = len(df_filtered)

            # Llenar tabla
            self.top_diagnosis_table.setRowCount(len(diag_counts))

            for i, (diag, count) in enumerate(diag_counts.items()):
                percentage = (count / total * 100) if total > 0 else 0

                # Truncar diagnóstico si es muy largo
                diag_text = str(diag)
                if len(diag_text) > 80:
                    diag_text = diag_text[:77] + "..."

                # Agregar items
                item_diag = QTableWidgetItem(diag_text)
                item_freq = QTableWidgetItem(str(count))
                item_perc = QTableWidgetItem(f"{percentage:.1f}%")

                # Centrar frecuencia y porcentaje
                item_freq.setTextAlignment(Qt.AlignCenter)
                item_perc.setTextAlignment(Qt.AlignCenter)

                self.top_diagnosis_table.setItem(i, 0, item_diag)
                self.top_diagnosis_table.setItem(i, 1, item_freq)
                self.top_diagnosis_table.setItem(i, 2, item_perc)

        except Exception as e:
            logging.error(f"Error actualizando tabla de diagnósticos: {e}", exc_info=True)

    def _update_temporal_charts(self):
        """Actualiza los 3 gráficos del análisis temporal"""
        if self.df is None or self.df.empty:
            return

        self._update_tiempo_proceso_chart()
        self._update_throughput_chart()
        self._update_edad_ki67_chart()

    def _update_tiempo_proceso_chart(self):
        """Actualiza el gráfico de tiempo de proceso (boxplot)"""
        if self.df is None or self.df.empty or self.tiempo_proceso_chart is None:
            return

        try:
            # Buscar columnas de fecha
            col_ingreso = None
            col_informe = None

            for col in self.df.columns:
                if 'fecha' in col.lower() and 'ingreso' in col.lower():
                    col_ingreso = col
                if 'fecha' in col.lower() and 'informe' in col.lower():
                    col_informe = col

            if not col_ingreso or not col_informe:
                logging.warning("No se encontraron columnas de fecha para tiempo de proceso")
                return

            # Parsear fechas
            f_ing = pd.to_datetime(self.df[col_ingreso], errors='coerce')
            f_inf = pd.to_datetime(self.df[col_informe], errors='coerce')

            # Calcular días
            dias = (f_inf - f_ing).dt.days.dropna()

            if dias.empty:
                logging.warning("No hay datos válidos de tiempo de proceso")
                return

            # Limpiar chart
            self.tiempo_proceso_chart.clear()

            # Crear boxplot usando plot_custom
            def draw_boxplot(fig, ax):
                ax.boxplot(dias.values, vert=True, patch_artist=True,
                          boxprops=dict(facecolor='#3b82f6', alpha=0.7),
                          medianprops=dict(color='#ffffff', linewidth=2),
                          whiskerprops=dict(color='#a1a1aa'),
                          capprops=dict(color='#a1a1aa'))

                ax.set_ylabel('Días', color='#ffffff', fontsize=12)
                ax.set_title('Tiempo de Proceso (días)', color='#ffffff', fontsize=14, fontweight='bold')

                # Estadísticas
                mean_dias = dias.mean()
                median_dias = dias.median()

                stats_text = f'Media: {mean_dias:.1f} días\nMediana: {median_dias:.1f} días'
                ax.text(0.98, 0.98, stats_text,
                       transform=ax.transAxes,
                       verticalalignment='top',
                       horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='#252538', alpha=0.8, edgecolor='#3f3f55'),
                       color='#ffffff',
                       fontsize=10)

            self.tiempo_proceso_chart.plot_custom(draw_boxplot)

        except Exception as e:
            logging.error(f"Error actualizando gráfico de tiempo de proceso: {e}", exc_info=True)

    def _update_throughput_chart(self):
        """Actualiza el gráfico de throughput semanal (línea)"""
        if self.df is None or self.df.empty or self.throughput_chart is None:
            return

        try:
            # Buscar columna de fecha de informe
            col_informe = None
            for col in self.df.columns:
                if 'fecha' in col.lower() and 'informe' in col.lower():
                    col_informe = col
                    break

            if not col_informe:
                logging.warning("No se encontró columna de fecha de informe")
                return

            # Parsear fechas
            fechas = pd.to_datetime(self.df[col_informe], errors='coerce')
            df_valid = self.df[fechas.notna()].copy()
            df_valid['_fecha_informe'] = fechas[fechas.notna()]

            if df_valid.empty:
                logging.warning("No hay fechas válidas para throughput")
                return

            # Resamplear por semana (lunes a lunes)
            df_valid = df_valid.set_index('_fecha_informe')
            weekly = df_valid.resample('W-MON').size()

            if weekly.empty:
                return

            # Limpiar chart
            self.throughput_chart.clear()

            # Crear gráfico de línea
            x_vals = [d.strftime('%Y-%m-%d') for d in weekly.index]
            y_vals = weekly.values.tolist()

            self.throughput_chart.plot_line(range(len(x_vals)), y_vals, color='#10b981', marker='o')
            self.throughput_chart.set_title('Throughput Semanal')
            self.throughput_chart.set_labels('Semana', 'Número de Informes')

            # Configurar ticks del eje X (mostrar solo algunas fechas)
            step = max(1, len(x_vals) // 10)
            self.throughput_chart.ax.set_xticks(range(0, len(x_vals), step))
            self.throughput_chart.ax.set_xticklabels([x_vals[i] for i in range(0, len(x_vals), step)], rotation=45, ha='right')

            self.throughput_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de throughput: {e}", exc_info=True)

    def _update_edad_ki67_chart(self):
        """Actualiza el gráfico de correlación Edad vs Ki-67 (scatter)"""
        if self.df is None or self.df.empty or self.edad_ki67_chart is None:
            return

        try:
            # Buscar columna de edad
            if "Edad" not in self.df.columns:
                logging.warning("No se encontró columna 'Edad'")
                return

            # Parsear edad
            x = pd.to_numeric(self.df["Edad"], errors='coerce')

            # Buscar y parsear Ki-67
            ki67_col = None
            for col in self.df.columns:
                if 'ki' in col.lower() and '67' in col.lower():
                    ki67_col = col
                    break

            if not ki67_col:
                logging.warning("No se encontró columna de Ki-67")
                return

            # Limpiar Ki-67 (remover % y convertir a número)
            raw_ki67 = self.df[ki67_col].astype(str).str.strip().replace('', pd.NA)
            clean_ki67 = raw_ki67.str.replace('%', '', regex=False)
            y = pd.to_numeric(clean_ki67, errors='coerce')

            # Filtrar valores válidos
            mask = x.notna() & y.notna()
            if not mask.any():
                logging.warning("No hay datos válidos para Edad vs Ki-67")
                return

            x_valid = x[mask].values
            y_valid = y[mask].values

            # Limpiar chart
            self.edad_ki67_chart.clear()

            # Crear scatter plot
            self.edad_ki67_chart.plot_scatter(x_valid, y_valid, color='#f59e0b', alpha=0.6, s=50)
            self.edad_ki67_chart.set_title('Correlación: Edad vs Ki-67')
            self.edad_ki67_chart.set_labels('Edad (años)', 'Ki-67 (%)')

            # Añadir línea de tendencia
            import numpy as np
            if len(x_valid) > 2:
                z = np.polyfit(x_valid, y_valid, 1)
                p = np.poly1d(z)
                x_line = np.linspace(x_valid.min(), x_valid.max(), 100)
                self.edad_ki67_chart.ax.plot(x_line, p(x_line), "--", color='#ef4444', linewidth=2, alpha=0.8, label='Tendencia')
                self.edad_ki67_chart.ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')

            self.edad_ki67_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico Edad vs Ki-67: {e}", exc_info=True)

    def _update_quality_charts(self):
        """Actualiza los 3 gráficos de completitud y calidad"""
        if self.df is None or self.df.empty:
            return

        self._update_missingness_chart()
        self._update_top_responsables_chart()
        self._update_longitud_diagnostico_chart()

    def _update_missingness_chart(self):
        """Actualiza el gráfico de campos vacíos (%)"""
        if self.df is None or self.df.empty or self.missingness_chart is None:
            return

        try:
            # Columnas importantes a analizar
            cols_to_check = [
                "Servicio", "Malignidad", "Patologo", "Organo",
                "IHQ_HER2", "IHQ_KI-67", "Edad", "Genero"
            ]

            # Filtrar columnas que existen
            present_cols = [c for c in cols_to_check if c in self.df.columns]

            if not present_cols:
                logging.warning("No se encontraron columnas para análisis de completitud")
                return

            # Calcular porcentaje de campos vacíos
            missingness = self.df[present_cols].isna().mean() * 100
            missingness = missingness.sort_values(ascending=False)

            if missingness.empty:
                return

            # Limpiar chart
            self.missingness_chart.clear()

            # Crear gráfico de barras
            labels = list(missingness.index)
            values = list(missingness.values)

            # Colores según severidad
            colors = []
            for val in values:
                if val < 10:
                    colors.append('#10b981')  # Verde - Excelente
                elif val < 30:
                    colors.append('#f59e0b')  # Amarillo - Aceptable
                else:
                    colors.append('#ef4444')  # Rojo - Problemático

            self.missingness_chart.plot_bar(labels, values, color=colors)
            self.missingness_chart.set_title('Campos Vacíos por Columna (%)')
            self.missingness_chart.set_labels('', '% Vacío')

            # Rotar etiquetas del eje X
            self.missingness_chart.ax.tick_params(axis='x', rotation=45)

            # Añadir línea de referencia en 20%
            self.missingness_chart.ax.axhline(y=20, color='#f59e0b', linestyle='--', linewidth=1, alpha=0.5, label='Umbral 20%')
            self.missingness_chart.ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')

            self.missingness_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de campos vacíos: {e}", exc_info=True)

    def _update_top_responsables_chart(self):
        """Actualiza el gráfico de productividad por responsable (Top 10)"""
        if self.df is None or self.df.empty or self.top_responsables_chart is None:
            return

        try:
            # Buscar columna de patólogo/responsable
            patologo_col = None
            for col in self.df.columns:
                if 'patologo' in col.lower() or 'responsable' in col.lower():
                    patologo_col = col
                    break

            if not patologo_col:
                logging.warning("No se encontró columna de patólogo/responsable")
                return

            # Contar casos por responsable
            responsables = self.df[patologo_col].astype(str).value_counts().head(10)

            if responsables.empty:
                return

            # Limpiar chart
            self.top_responsables_chart.clear()

            # Crear gráfico de barras
            labels = list(responsables.index)
            values = list(responsables.values)

            # Truncar nombres largos
            labels = [label[:30] + '...' if len(label) > 30 else label for label in labels]

            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'] * 2  # Rotar colores

            self.top_responsables_chart.plot_bar(labels, values, color=colors[:len(labels)])
            self.top_responsables_chart.set_title('Productividad por Responsable (Top 10)')
            self.top_responsables_chart.set_labels('', 'Número de Informes')

            # Rotar etiquetas del eje X
            self.top_responsables_chart.ax.tick_params(axis='x', rotation=45)
            self.top_responsables_chart.ax.tick_params(axis='x', labelsize=9)

            self.top_responsables_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de responsables: {e}", exc_info=True)

    def _update_longitud_diagnostico_chart(self):
        """Actualiza el gráfico de distribución de longitud de diagnósticos"""
        if self.df is None or self.df.empty or self.longitud_diagnostico_chart is None:
            return

        try:
            # Buscar columna de diagnóstico descriptivo
            diag_col = None
            for col in self.df.columns:
                if 'descripcion' in col.lower() and 'diagnostico' in col.lower():
                    diag_col = col
                    break

            # Si no hay descripción, usar diagnóstico principal
            if not diag_col:
                for col in self.df.columns:
                    if 'diagnostico' in col.lower() and 'principal' in col.lower():
                        diag_col = col
                        break

            if not diag_col:
                logging.warning("No se encontró columna de diagnóstico")
                return

            # Calcular longitudes
            longitudes = self.df[diag_col].astype(str).str.len()

            # Definir bins
            bins = [0, 50, 150, 300, 600, 1200, float('inf')]
            labels_bins = ["<50", "50-150", "150-300", "300-600", "600-1200", "1200+"]

            # Crear categorías
            import numpy as np
            categorias = pd.cut(longitudes, bins=bins, labels=labels_bins, include_lowest=True)
            distribucion = categorias.value_counts().sort_index()

            if distribucion.empty:
                return

            # Limpiar chart
            self.longitud_diagnostico_chart.clear()

            # Crear gráfico de barras
            labels_chart = [str(label) for label in distribucion.index]
            values = list(distribucion.values)

            colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

            self.longitud_diagnostico_chart.plot_bar(labels_chart, values, color=colors[:len(labels_chart)])
            self.longitud_diagnostico_chart.set_title('Distribución: Longitud de Diagnósticos (caracteres)')
            self.longitud_diagnostico_chart.set_labels('Rango de Caracteres', 'Número de Casos')

            self.longitud_diagnostico_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de longitud de diagnósticos: {e}", exc_info=True)

    def _update_biomarker_charts(self):
        """Actualiza los 4 gráficos de biomarcadores"""
        if self.df is None or self.df.empty:
            return

        self._update_ki67_chart()
        self._update_her2_chart()
        self._update_re_rp_chart()
        self._update_pdl1_chart()

    def _update_ki67_chart(self):
        """Actualiza el histograma de Ki-67"""
        if self.df is None or self.df.empty or self.ki67_chart is None:
            return

        try:
            # Buscar columna Ki-67
            ki67_col = None
            for col in self.df.columns:
                if 'ki' in col.lower() and '67' in col.lower():
                    ki67_col = col
                    break

            if not ki67_col:
                logging.warning("No se encontró columna de Ki-67")
                return

            # Limpiar y convertir datos
            raw_data = self.df[ki67_col].astype(str).str.strip().replace('', pd.NA)
            numeric_data = raw_data.str.replace('%', '', regex=False)
            s = pd.to_numeric(numeric_data, errors='coerce').dropna()

            if s.empty:
                logging.warning("No hay datos válidos de Ki-67")
                return

            # Limpiar chart
            self.ki67_chart.clear()

            # Crear histograma usando plot_custom
            def draw_histogram(fig, ax):
                bins = min(12, len(s.unique()))
                n, bins_edges, patches = ax.hist(s.values, bins=bins, color='#3b82f6', alpha=0.7, edgecolor='#1e1e2e')

                ax.set_xlabel('% Ki-67', color='#ffffff', fontsize=12)
                ax.set_ylabel('Frecuencia', color='#ffffff', fontsize=12)
                ax.set_title('Distribución Ki-67 (%)', color='#ffffff', fontsize=14, fontweight='bold')

                # Estadísticas
                mean_val = s.mean()
                median_val = s.median()

                stats_text = f'Media: {mean_val:.1f}%\nMediana: {median_val:.1f}%\nN: {len(s)}'
                ax.text(0.98, 0.98, stats_text,
                       transform=ax.transAxes,
                       verticalalignment='top',
                       horizontalalignment='right',
                       bbox=dict(boxstyle='round', facecolor='#252538', alpha=0.8, edgecolor='#3f3f55'),
                       color='#ffffff',
                       fontsize=10)

            self.ki67_chart.plot_custom(draw_histogram)

        except Exception as e:
            logging.error(f"Error actualizando gráfico de Ki-67: {e}", exc_info=True)

    def _update_her2_chart(self):
        """Actualiza el gráfico de barras de HER2"""
        if self.df is None or self.df.empty or self.her2_chart is None:
            return

        try:
            # Buscar columna HER2
            her2_col = None
            for col in self.df.columns:
                if 'her2' in col.lower():
                    her2_col = col
                    break

            if not her2_col:
                logging.warning("No se encontró columna de HER2")
                return

            # Contar valores
            order = ["0", "1+", "2+", "3+", "NEGATIVO", "POSITIVO"]
            ser = self.df[her2_col].astype(str).str.upper().value_counts()

            # Reordenar según el orden estándar
            if any(k in ser.index for k in order):
                ser = ser.reindex(order, fill_value=0)

            if ser.sum() == 0:
                return

            # Limpiar chart
            self.her2_chart.clear()

            # Crear gráfico de barras
            labels = list(ser.index)
            values = list(ser.values)

            # Colores según interpretación clínica
            colors = []
            for label in labels:
                if label in ['0', '1+', 'NEGATIVO']:
                    colors.append('#10b981')  # Verde - Negativo
                elif label == '2+':
                    colors.append('#f59e0b')  # Amarillo - Indeterminado
                elif label in ['3+', 'POSITIVO']:
                    colors.append('#ef4444')  # Rojo - Positivo
                else:
                    colors.append('#8b5cf6')  # Púrpura - Otro

            self.her2_chart.plot_bar(labels, values, color=colors)
            self.her2_chart.set_title('Distribución HER2 (Score)')
            self.her2_chart.set_labels('Score', 'Número de Casos')

            # Añadir nota interpretativa
            note_text = '0/1+: Negativo  |  2+: Indeterminado  |  3+: Positivo'
            self.her2_chart.ax.text(0.5, -0.15, note_text,
                                   transform=self.her2_chart.ax.transAxes,
                                   ha='center', va='top',
                                   color='#a1a1aa', fontsize=9,
                                   bbox=dict(boxstyle='round', facecolor='#252538', alpha=0.5, edgecolor='#3f3f55'))

            self.her2_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de HER2: {e}", exc_info=True)

    def _update_re_rp_chart(self):
        """Actualiza el gráfico de barras agrupadas para RE/RP"""
        if self.df is None or self.df.empty or self.re_rp_chart is None:
            return

        try:
            # Buscar columnas de receptores
            cols = []
            col_names = []

            for col in self.df.columns:
                if 'receptor' in col.lower() and 'estrogeno' in col.lower():
                    cols.append(col)
                    col_names.append('RE')
                elif 'receptor' in col.lower() and 'progesterona' in col.lower():
                    cols.append(col)
                    col_names.append('RP')

            if not cols:
                logging.warning("No se encontraron columnas de receptores hormonales")
                return

            # Limpiar chart
            self.re_rp_chart.clear()

            # Preparar datos
            import numpy as np

            data = []
            for col in cols:
                ser = self.df[col].astype(str).str.upper().replace({"": "ND", "NAN": "ND"}).value_counts()
                data.append(ser)

            # Normalizar categorías
            all_cats = sorted(set().union(*[d.index for d in data]))

            # Crear matriz de datos
            mat = np.array([[d.get(k, 0) for k in all_cats] for d in data])

            # Crear gráfico de barras agrupadas usando plot_custom
            def draw_grouped_bars(fig, ax):
                x = np.arange(len(all_cats))
                width = 0.35

                for i, (row, label) in enumerate(zip(mat, col_names)):
                    offset = (i - 0.5) * width
                    color = '#3b82f6' if label == 'RE' else '#ec4899'
                    ax.bar(x + offset, row, width, label=label, color=color, alpha=0.8)

                ax.set_xticks(x)
                ax.set_xticklabels(all_cats, rotation=0, color='#ffffff')
                ax.set_ylabel('Número de Casos', color='#ffffff', fontsize=12)
                ax.set_title('Receptores Hormonales (RE/RP)', color='#ffffff', fontsize=14, fontweight='bold')
                ax.legend(facecolor='#252538', edgecolor='#3f3f55', labelcolor='#ffffff')
                ax.tick_params(colors='#ffffff')

            self.re_rp_chart.plot_custom(draw_grouped_bars)

        except Exception as e:
            logging.error(f"Error actualizando gráfico de RE/RP: {e}", exc_info=True)

    def _update_pdl1_chart(self):
        """Actualiza el gráfico de barras de PDL-1"""
        if self.df is None or self.df.empty or self.pdl1_chart is None:
            return

        try:
            # Buscar columna PDL-1 (varios nombres posibles)
            pdl1_col = None
            for col in ['IHQ_PDL-1', 'IHQ_PDL1_TPS', 'IHQ_PDL1_CPS']:
                if col in self.df.columns:
                    pdl1_col = col
                    break

            # Búsqueda flexible
            if not pdl1_col:
                for col in self.df.columns:
                    if 'pdl' in col.lower() or 'pd-l' in col.lower():
                        pdl1_col = col
                        break

            if not pdl1_col:
                logging.warning("No se encontró columna de PD-L1")
                return

            # Contar valores
            ser = self.df[pdl1_col].astype(str).replace({"": "ND", "nan": "ND"}).value_counts()

            if ser.empty:
                return

            # Limpiar chart
            self.pdl1_chart.clear()

            # Crear gráfico de barras
            labels = list(ser.index)
            values = list(ser.values)

            # Colores diferenciados
            colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'] * (len(labels) // 5 + 1)

            self.pdl1_chart.plot_bar(labels, values, color=colors[:len(labels)])
            self.pdl1_chart.set_title('Distribución PD-L1')
            self.pdl1_chart.set_labels('', 'Número de Casos')

            # Rotar etiquetas si son muchas
            if len(labels) > 5:
                self.pdl1_chart.ax.tick_params(axis='x', rotation=45)

            self.pdl1_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de PD-L1: {e}", exc_info=True)

    def _update_services_charts(self):
        """Actualiza los 3 gráficos de servicios y órganos"""
        if self.df is None or self.df.empty:
            return

        self._update_malignidad_chart()
        self._update_servicios_chart()
        self._update_organos_chart()

    def _update_malignidad_chart(self):
        """Actualiza el gráfico de pastel de malignidad"""
        if self.df is None or self.df.empty or self.malignidad_chart is None:
            return

        try:
            # Buscar columna de malignidad
            if "Malignidad" not in self.df.columns:
                logging.warning("No se encontró columna de Malignidad")
                return

            # Contar valores
            ser = self.df["Malignidad"].astype(str).str.upper().replace({"": "DESCONOCIDO", "NAN": "DESCONOCIDO"}).value_counts()

            if ser.empty:
                return

            # Limpiar chart
            self.malignidad_chart.clear()

            # Crear gráfico de pastel usando plot_pie
            labels = list(ser.index)
            sizes = list(ser.values)

            # Colores según categoría
            colors = []
            for label in labels:
                if 'MALIGNO' in label and 'NO' not in label:
                    colors.append('#ef4444')  # Rojo - Maligno
                elif 'BENIGNO' in label:
                    colors.append('#10b981')  # Verde - Benigno
                elif 'DESCONOCIDO' in label:
                    colors.append('#6b7280')  # Gris - Desconocido
                else:
                    colors.append('#3b82f6')  # Azul - Otro

            self.malignidad_chart.plot_pie(sizes, labels, colors=colors, autopct='%1.1f%%')
            self.malignidad_chart.set_title('Distribución de Malignidad')

        except Exception as e:
            logging.error(f"Error actualizando gráfico de malignidad: {e}", exc_info=True)

    def _update_servicios_chart(self):
        """Actualiza el gráfico de barras de servicios (Top 12)"""
        if self.df is None or self.df.empty or self.servicios_chart is None:
            return

        try:
            # Buscar columna de servicio
            if "Servicio" not in self.df.columns:
                logging.warning("No se encontró columna de Servicio")
                return

            # Contar top 12 servicios
            ser = self.df["Servicio"].astype(str).value_counts().head(12)

            if ser.empty:
                return

            # Limpiar chart
            self.servicios_chart.clear()

            # Crear gráfico de barras
            labels = list(ser.index)
            values = list(ser.values)

            # Truncar nombres largos
            labels = [label[:25] + '...' if len(label) > 25 else label for label in labels]

            # Colores degradados
            colors = ['#3b82f6', '#4f46e5', '#7c3aed', '#a855f7', '#c026d3',
                     '#db2777', '#f43f5e', '#f97316', '#f59e0b', '#eab308',
                     '#84cc16', '#22c55e']

            self.servicios_chart.plot_bar(labels, values, color=colors[:len(labels)])
            self.servicios_chart.set_title(f'Distribución por Servicios (n={ser.sum()})')
            self.servicios_chart.set_labels('', 'Número de Casos')

            # Rotar etiquetas para mejor legibilidad
            self.servicios_chart.ax.tick_params(axis='x', rotation=30, labelsize=9)

            self.servicios_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de servicios: {e}", exc_info=True)

    def _update_organos_chart(self):
        """Actualiza el gráfico de barras de órganos (Top 12)"""
        if self.df is None or self.df.empty or self.organos_chart is None:
            return

        try:
            # Buscar columna de órgano (puede ser "Organo" o "IHQ_ORGANO")
            organo_col = None
            if "Organo" in self.df.columns:
                organo_col = "Organo"
            elif "IHQ_ORGANO" in self.df.columns:
                organo_col = "IHQ_ORGANO"
            else:
                # Búsqueda flexible
                for col in self.df.columns:
                    if 'organo' in col.lower():
                        organo_col = col
                        break

            if not organo_col:
                logging.warning("No se encontró columna de Órgano")
                return

            # Contar top 12 órganos
            ser = self.df[organo_col].astype(str).replace({"": "No especificado", "nan": "No especificado"}).value_counts().head(12)

            if ser.empty:
                return

            # Limpiar chart
            self.organos_chart.clear()

            # Crear gráfico de barras
            labels = list(ser.index)
            values = list(ser.values)

            # Truncar nombres largos
            labels = [label[:25] + '...' if len(label) > 25 else label for label in labels]

            # Colores cálidos
            colors = ['#ef4444', '#f97316', '#f59e0b', '#eab308', '#84cc16',
                     '#22c55e', '#10b981', '#14b8a6', '#06b6d4', '#0ea5e9',
                     '#3b82f6', '#6366f1']

            self.organos_chart.plot_bar(labels, values, color=colors[:len(labels)])
            self.organos_chart.set_title('Distribución por Órganos')
            self.organos_chart.set_labels('', 'Número de Casos')

            # Rotar etiquetas para mejor legibilidad
            self.organos_chart.ax.tick_params(axis='x', rotation=30, labelsize=9)

            self.organos_chart.refresh()

        except Exception as e:
            logging.error(f"Error actualizando gráfico de órganos: {e}", exc_info=True)
