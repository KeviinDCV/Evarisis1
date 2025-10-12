#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Avanzado de Base de Datos - Sistema EVARISIS
Panel super robusto con estadísticas profundas de biomarcadores
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from collections import defaultdict
import re

class EnhancedDatabaseDashboard:
    """Dashboard avanzado para análisis completo de la base de datos"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.df = None
        self.biomarker_stats = {}
        self.charts = {}

        # Configurar estilo de gráficos
        plt.style.use('default')
        sns.set_palette("husl")

        self.create_dashboard()

    def create_dashboard(self):
        """Crear el dashboard completo"""

        # Título principal
        title_frame = ttk.Frame(self.parent_frame)
        title_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            title_frame,
            text="🗄️ Dashboard Avanzado - Base de Datos EVARISIS",
            font=("Segoe UI", 18, "bold")
        ).pack(side=LEFT)

        # Crear contenedor con pestañas
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(expand=True, fill=BOTH)

        # Pestaña 1: Estadísticas Generales
        self.general_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.general_tab, text="📊 Estadísticas Generales")

        # Pestaña 2: Análisis de Biomarcadores
        self.biomarker_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.biomarker_tab, text="🧬 Biomarcadores")

        # Pestaña 3: Análisis Temporal
        self.temporal_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.temporal_tab, text="📅 Análisis Temporal")

        # Pestaña 4: Análisis de Malignidad
        self.malignancy_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.malignancy_tab, text="⚠️ Análisis de Malignidad")

        # Pestaña 5: Importar Datos
        self.import_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.import_tab, text="📥 Importar Datos")

        # Pestaña 6: Exportaciones
        self.export_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.export_tab, text="📤 Exportaciones")

        # Crear contenido de cada pestaña
        self.create_general_stats_tab()
        self.create_biomarker_analysis_tab()
        self.create_temporal_analysis_tab()
        self.create_malignancy_analysis_tab()
        self.create_import_tab()
        self.create_export_tab()

        # Cargar datos iniciales
        self.refresh_all_data()

    def create_general_stats_tab(self):
        """Crear pestaña de estadísticas generales"""

        # Frame scrollable
        canvas = tk.Canvas(self.general_tab)
        scrollbar = ttk.Scrollbar(self.general_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        def configure_scroll_region(event=None):
            try:
                # Obtener el tamaño requerido del frame
                scrollable_frame.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    canvas.configure(scrollregion=bbox)
                else:
                    # Fallback: usar el tamaño del frame scrollable
                    width = scrollable_frame.winfo_reqwidth()
                    height = scrollable_frame.winfo_reqheight()
                    canvas.configure(scrollregion=(0, 0, width, height))
            except Exception as e:
                print(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # Sección 1: Métricas Principales
        metrics_section = ttk.LabelFrame(main_frame, text="📈 Métricas Principales", padding=20)
        metrics_section.pack(fill=X, padx=20, pady=10)

        # Grid de métricas
        metrics_grid = ttk.Frame(metrics_section)
        metrics_grid.pack(fill=X)

        # Configurar grid
        for i in range(4):
            metrics_grid.grid_columnconfigure(i, weight=1)

        # Métricas principales
        self.metric_cards = {}
        metrics_data = [
            ("📊", "Total Registros", "0", "primary"),
            ("🧬", "Con Biomarcadores", "0", "success"),
            ("⚠️", "Casos Malignos", "0", "danger"),
            ("📅", "Días de Datos", "0", "info")
        ]

        for i, (icon, title, value, style) in enumerate(metrics_data):
            card = self.create_metric_card(metrics_grid, icon, title, value, style)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.metric_cards[title] = card

        # Sección 2: Distribución por Tipos de Diagnóstico
        diagnosis_section = ttk.LabelFrame(main_frame, text="🏥 Distribución por Diagnósticos", padding=20)
        diagnosis_section.pack(fill=X, padx=20, pady=10)

        # Frame para gráfico de diagnósticos
        self.diagnosis_chart_frame = ttk.Frame(diagnosis_section)
        self.diagnosis_chart_frame.pack(fill=X, pady=10)

        # Sección 3: Top Diagnósticos
        top_diagnosis_section = ttk.LabelFrame(main_frame, text="🔝 Top 10 Diagnósticos", padding=20)
        top_diagnosis_section.pack(fill=X, padx=20, pady=10)

        # Treeview para top diagnósticos
        self.top_diagnosis_tree = ttk.Treeview(
            top_diagnosis_section,
            columns=("Diagnóstico", "Frecuencia", "Porcentaje"),
            show="headings",
            height=10
        )

        self.top_diagnosis_tree.heading("Diagnóstico", text="Diagnóstico")
        self.top_diagnosis_tree.heading("Frecuencia", text="Frecuencia")
        self.top_diagnosis_tree.heading("Porcentaje", text="% del Total")

        self.top_diagnosis_tree.column("Diagnóstico", width=400)
        self.top_diagnosis_tree.column("Frecuencia", width=100, anchor="center")
        self.top_diagnosis_tree.column("Porcentaje", width=100, anchor="center")

        self.top_diagnosis_tree.pack(fill=X, padx=10, pady=10)

        # Scrollbar para la tabla
        diagnosis_scrollbar = ttk.Scrollbar(top_diagnosis_section, orient="vertical", command=self.top_diagnosis_tree.yview)
        diagnosis_scrollbar.pack(side="right", fill="y")
        self.top_diagnosis_tree.configure(yscrollcommand=diagnosis_scrollbar.set)

    def create_biomarker_analysis_tab(self):
        """Crear pestaña de análisis profundo de biomarcadores"""

        # Frame scrollable
        canvas = tk.Canvas(self.biomarker_tab)
        scrollbar = ttk.Scrollbar(self.biomarker_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        def configure_scroll_region(event=None):
            try:
                # Obtener el tamaño requerido del frame
                scrollable_frame.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    canvas.configure(scrollregion=bbox)
                else:
                    # Fallback: usar el tamaño del frame scrollable
                    width = scrollable_frame.winfo_reqwidth()
                    height = scrollable_frame.winfo_reqheight()
                    canvas.configure(scrollregion=(0, 0, width, height))
            except Exception as e:
                print(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # Sección 1: Resumen de Biomarcadores
        biomarker_summary = ttk.LabelFrame(main_frame, text="🧬 Resumen de Biomarcadores", padding=20)
        biomarker_summary.pack(fill=X, padx=20, pady=10)

        # Grid de biomarcadores con más espacio horizontal
        biomarker_grid = ttk.Frame(biomarker_summary)
        biomarker_grid.pack(fill=BOTH, expand=True)

        # Configurar grid para biomarcadores - 6 columnas para evitar cortes
        for i in range(6):
            biomarker_grid.grid_columnconfigure(i, weight=1, minsize=150)

        # Cards de biomarcadores principales
        self.biomarker_cards = {}
        biomarker_data = [
            ("HER2", "0", "danger"),
            ("Ki-67", "0", "warning"),
            ("ER/PR", "0", "info"),
            ("P16", "0", "success"),
            ("PDL-1", "0", "secondary"),
            ("Otros", "0", "dark")
        ]

        # Distribuir en una sola fila horizontal para evitar cortes
        for i, (name, value, style) in enumerate(biomarker_data):
            card = self.create_biomarker_card(biomarker_grid, name, value, style)
            card.grid(row=0, column=i, padx=5, pady=10, sticky="ew")
            self.biomarker_cards[name] = card

        # Sección 2: Distribución de Valores de Biomarcadores
        values_section = ttk.LabelFrame(main_frame, text="📊 Distribución de Valores", padding=20)
        values_section.pack(fill=X, padx=20, pady=10)

        # Frame para gráficos de distribución
        self.biomarker_charts_frame = ttk.Frame(values_section)
        self.biomarker_charts_frame.pack(fill=X, pady=10)

        # Sección 3: Correlaciones entre Biomarcadores
        correlation_section = ttk.LabelFrame(main_frame, text="🔗 Correlaciones entre Biomarcadores", padding=20)
        correlation_section.pack(fill=X, padx=20, pady=10)

        # Frame para matriz de correlación
        self.correlation_frame = ttk.Frame(correlation_section)
        self.correlation_frame.pack(fill=X, pady=10)

        # Sección 4: Estadísticas Avanzadas por Biomarcador
        advanced_stats_section = ttk.LabelFrame(main_frame, text="🔍 Estadísticas Detalladas", padding=20)
        advanced_stats_section.pack(fill=X, padx=20, pady=10)

        # Treeview para estadísticas detalladas
        self.biomarker_stats_tree = ttk.Treeview(
            advanced_stats_section,
            columns=("Biomarcador", "Total", "Positivos", "Negativos", "% Positividad", "Media", "Desv.Std"),
            show="headings",
            height=8
        )

        headers = ["Biomarcador", "Total", "Positivos", "Negativos", "% Positividad", "Media", "Desv.Std"]
        for header in headers:
            self.biomarker_stats_tree.heading(header, text=header)
            self.biomarker_stats_tree.column(header, width=120, anchor="center")

        self.biomarker_stats_tree.pack(fill=X, padx=10, pady=10)

    def create_temporal_analysis_tab(self):
        """Crear pestaña de análisis temporal"""

        # Frame scrollable
        canvas = tk.Canvas(self.temporal_tab)
        scrollbar = ttk.Scrollbar(self.temporal_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        def configure_scroll_region(event=None):
            try:
                # Obtener el tamaño requerido del frame
                scrollable_frame.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    canvas.configure(scrollregion=bbox)
                else:
                    # Fallback: usar el tamaño del frame scrollable
                    width = scrollable_frame.winfo_reqwidth()
                    height = scrollable_frame.winfo_reqheight()
                    canvas.configure(scrollregion=(0, 0, width, height))
            except Exception as e:
                print(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # Sección 1: Tendencias Temporales
        trends_section = ttk.LabelFrame(main_frame, text="📈 Tendencias Temporales", padding=20)
        trends_section.pack(fill=X, padx=20, pady=10)

        # Frame para gráfico de tendencias
        self.trends_chart_frame = ttk.Frame(trends_section)
        self.trends_chart_frame.pack(fill=X, pady=10)

        # Sección 2: Distribución por Períodos
        periods_section = ttk.LabelFrame(main_frame, text="📅 Distribución por Períodos", padding=20)
        periods_section.pack(fill=X, padx=20, pady=10)

        # Frame para gráfico de períodos
        self.periods_chart_frame = ttk.Frame(periods_section)
        self.periods_chart_frame.pack(fill=X, pady=10)

        # Sección 3: Estadísticas por Mes/Año
        monthly_stats_section = ttk.LabelFrame(main_frame, text="📊 Estadísticas Mensuales", padding=20)
        monthly_stats_section.pack(fill=X, padx=20, pady=10)

        # Treeview para estadísticas mensuales
        self.monthly_stats_tree = ttk.Treeview(
            monthly_stats_section,
            columns=("Período", "Total Casos", "Con Biomarcadores", "Malignos", "% Malignidad"),
            show="headings",
            height=12
        )

        headers = ["Período", "Total Casos", "Con Biomarcadores", "Malignos", "% Malignidad"]
        for header in headers:
            self.monthly_stats_tree.heading(header, text=header)
            self.monthly_stats_tree.column(header, width=150, anchor="center")

        self.monthly_stats_tree.pack(fill=X, padx=10, pady=10)

    def create_malignancy_analysis_tab(self):
        """Crear pestaña de análisis de malignidad"""

        # Frame scrollable
        canvas = tk.Canvas(self.malignancy_tab)
        scrollbar = ttk.Scrollbar(self.malignancy_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        def configure_scroll_region(event=None):
            try:
                # Obtener el tamaño requerido del frame
                scrollable_frame.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    canvas.configure(scrollregion=bbox)
                else:
                    # Fallback: usar el tamaño del frame scrollable
                    width = scrollable_frame.winfo_reqwidth()
                    height = scrollable_frame.winfo_reqheight()
                    canvas.configure(scrollregion=(0, 0, width, height))
            except Exception as e:
                print(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # Sección 1: Resumen de Malignidad
        malignancy_summary = ttk.LabelFrame(main_frame, text="⚠️ Resumen de Malignidad", padding=20)
        malignancy_summary.pack(fill=X, padx=20, pady=10)

        # Grid de estadísticas de malignidad
        malignancy_grid = ttk.Frame(malignancy_summary)
        malignancy_grid.pack(fill=X)

        for i in range(4):
            malignancy_grid.grid_columnconfigure(i, weight=1)

        # Cards de malignidad
        self.malignancy_cards = {}
        malignancy_data = [
            ("⚠️", "Casos Malignos", "0", "danger"),
            ("✅", "Casos Benignos", "0", "success"),
            ("❓", "Indeterminados", "0", "warning"),
            ("📊", "% Malignidad", "0%", "info")
        ]

        for i, (icon, title, value, style) in enumerate(malignancy_data):
            card = self.create_metric_card(malignancy_grid, icon, title, value, style)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.malignancy_cards[title] = card

        # Sección 2: Distribución por Tipo de Malignidad
        malignancy_types_section = ttk.LabelFrame(main_frame, text="🔍 Tipos de Malignidad", padding=20)
        malignancy_types_section.pack(fill=X, padx=20, pady=10)

        # Frame para gráfico de tipos de malignidad
        self.malignancy_chart_frame = ttk.Frame(malignancy_types_section)
        self.malignancy_chart_frame.pack(fill=X, pady=10)

        # Sección 3: Correlación Malignidad vs Biomarcadores
        correlation_malignancy_section = ttk.LabelFrame(main_frame, text="🧬 Biomarcadores vs Malignidad", padding=20)
        correlation_malignancy_section.pack(fill=X, padx=20, pady=10)

        # Treeview para correlación biomarcadores-malignidad
        self.malignancy_biomarker_tree = ttk.Treeview(
            correlation_malignancy_section,
            columns=("Biomarcador", "Malignos Positivos", "Malignos Negativos", "Benignos Positivos", "Benignos Negativos"),
            show="headings",
            height=8
        )

        headers = ["Biomarcador", "Malignos Positivos", "Malignos Negativos", "Benignos Positivos", "Benignos Negativos"]
        for header in headers:
            self.malignancy_biomarker_tree.heading(header, text=header)
            self.malignancy_biomarker_tree.column(header, width=120, anchor="center")

        self.malignancy_biomarker_tree.pack(fill=X, padx=10, pady=10)

    def create_metric_card(self, parent, icon, title, value, style):
        """Crear una tarjeta de métrica"""
        card = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)

        # Header con icono
        header = ttk.Frame(card)
        header.pack(fill=X, pady=(0, 10))

        ttk.Label(header, text=icon, font=("Segoe UI", 24)).pack()

        # Valor principal
        value_label = ttk.Label(card, text=value, font=("Segoe UI", 20, "bold"))
        value_label.pack()

        # Título
        ttk.Label(card, text=title, font=("Segoe UI", 10)).pack()

        # Guardar referencia del label de valor para actualizaciones
        card.value_label = value_label

        return card

    def create_biomarker_card(self, parent, name, value, style):
        """Crear una tarjeta específica para biomarcadores"""
        card = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)

        # Nombre del biomarcador
        ttk.Label(card, text=name, font=("Segoe UI", 14, "bold")).pack()

        # Valor
        value_label = ttk.Label(card, text=value, font=("Segoe UI", 18, "bold"))
        value_label.pack(pady=(5, 0))

        # Descripción
        desc_label = ttk.Label(card, text="casos", font=("Segoe UI", 9))
        desc_label.pack()

        # Guardar referencias
        card.value_label = value_label
        card.desc_label = desc_label

        return card

    def refresh_all_data(self):
        """Actualizar todos los datos del dashboard"""
        try:
            # Cargar datos de la base de datos
            from core.database_manager import get_all_records_as_dataframe
            self.df = get_all_records_as_dataframe()

            if self.df is None or self.df.empty:
                self.show_no_data_message()
                return

            # Actualizar cada pestaña
            self.update_general_stats()
            self.update_biomarker_analysis()
            self.update_temporal_analysis()
            self.update_malignancy_analysis()

        except Exception as e:
            print(f"Error actualizando dashboard: {e}")
            self.show_error_message(str(e))

    def update_general_stats(self):
        """Actualizar estadísticas generales"""
        if self.df is None or self.df.empty:
            return

        # Calcular métricas principales
        total_records = len(self.df)

        # Contar registros con biomarcadores válidos usando lógica robusta
        all_biomarker_keywords = ['her2', 'ki67', 'ki-67', 'er', 'pr', 'pdl1', 'p16', 'gata', 's100', 'cd', 'cromogranina', 'sinaptofisina']
        with_biomarkers = self._count_valid_biomarkers(all_biomarker_keywords)

        # Contar casos malignos
        malignant_count = 0
        malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]
        if malignidad_cols:
            malignant_count = (self.df[malignidad_cols[0]].str.contains('PRESENTE', case=False, na=False)).sum()

        # Calcular días de datos
        fecha_cols = [col for col in self.df.columns if 'fecha' in col.lower() and 'nacimiento' not in col.lower()]
        days_of_data = 0
        if fecha_cols:
            try:
                fechas = pd.to_datetime(self.df[fecha_cols[0]], errors='coerce', format='%d/%m/%Y')
                fechas_validas = fechas.dropna()
                if not fechas_validas.empty:
                    days_of_data = (fechas_validas.max() - fechas_validas.min()).days
            except:
                pass

        # Actualizar cards
        metrics_values = [
            ("Total Registros", str(total_records)),
            ("Con Biomarcadores", str(with_biomarkers)),
            ("Casos Malignos", str(malignant_count)),
            ("Días de Datos", str(days_of_data))
        ]

        for title, value in metrics_values:
            if title in self.metric_cards:
                self.metric_cards[title].value_label.config(text=value)

        # Actualizar gráfico de diagnósticos
        self.update_diagnosis_chart()

        # Actualizar top diagnósticos
        self.update_top_diagnosis_table()

    def update_biomarker_analysis(self):
        """Actualizar análisis de biomarcadores con detección robusta"""
        if self.df is None or self.df.empty:
            return

        # Analizar cada tipo de biomarcador con validación robusta
        biomarkers = {
            'HER2': ['her2'],
            'Ki-67': ['ki67', 'ki-67'],
            'ER/PR': ['er', 'pr', 'receptor'],
            'P16': ['p16'],
            'PDL-1': ['pdl1', 'pd-l1'],
            'Otros': []
        }

        total_other = 0
        for bio_name, keywords in biomarkers.items():
            if bio_name == 'Otros':
                continue

            count = self._count_valid_biomarkers(keywords)

            # Actualizar card
            if bio_name in self.biomarker_cards:
                self.biomarker_cards[bio_name].value_label.config(text=str(count))

        # Contar otros biomarcadores con validación
        other_keywords = ['gata', 's100', 'cd', 'cromogranina', 'sinaptofisina']
        total_other = self._count_valid_biomarkers(other_keywords)

        if 'Otros' in self.biomarker_cards:
            self.biomarker_cards['Otros'].value_label.config(text=str(total_other))

        # Actualizar gráficos y tablas de biomarcadores
        self.update_biomarker_charts()
        self.update_biomarker_stats_table()

    def _count_valid_biomarkers(self, keywords):
        """Contar registros que realmente contienen biomarcadores válidos"""
        if not keywords:
            return 0

        count = 0
        bio_cols = [col for col in self.df.columns if any(kw in col.lower() for kw in keywords)]

        if not bio_cols:
            return 0

        for index, row in self.df.iterrows():
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
        """Verificar si el texto contiene un resultado válido de biomarcador"""
        if not text or text.strip() == "" or text.lower() in ['nan', 'null', 'none']:
            return False

        text = text.lower().strip()

        # Patrones que indican resultados válidos de biomarcadores
        valid_patterns = [
            # Resultados positivos/negativos explícitos
            r'\b(positiv|negativ)\w*\b',
            # Porcentajes
            r'\d+\s*%',
            # Scores
            r'score\s*[:\-]?\s*[0-3][\+]?',
            # Intensidades
            r'\b(intensidad|débil|fuerte|moderada?|intensa?)\b',
            # Escalas numéricas con +
            r'\b[0-3]\+?\b',
            # Expresiones específicas
            r'\b(presente|ausente|expresión|sobreexpresión)\b',
            # Valores Ki67 específicos
            r'\b(menor|mayor)\s+(del?\s*|al\s*)?\d+\s*%',
            # Estados específicos
            r'\b(mutado|no\s+mutado|salvaje)\b'
        ]

        import re
        for pattern in valid_patterns:
            if re.search(pattern, text):
                return True

        return False

    def update_temporal_analysis(self):
        """Actualizar análisis temporal"""
        if self.df is None or self.df.empty:
            return

        # Encontrar columnas de fecha
        fecha_cols = [col for col in self.df.columns if 'fecha' in col.lower() and 'nacimiento' not in col.lower()]

        if not fecha_cols:
            return

        try:
            # Convertir fechas
            fecha_col = fecha_cols[0]
            self.df['fecha_parsed'] = pd.to_datetime(self.df[fecha_col], errors='coerce', format='%d/%m/%Y')

            # Filtrar fechas válidas
            df_with_dates = self.df[self.df['fecha_parsed'].notna()].copy()

            if df_with_dates.empty:
                return

            # Agregar columnas de período
            df_with_dates['año_mes'] = df_with_dates['fecha_parsed'].dt.to_period('M')
            df_with_dates['año'] = df_with_dates['fecha_parsed'].dt.year
            df_with_dates['mes'] = df_with_dates['fecha_parsed'].dt.month

            # Actualizar gráficos temporales
            self.update_temporal_charts(df_with_dates)

            # Actualizar tabla de estadísticas mensuales
            self.update_monthly_stats_table(df_with_dates)

        except Exception as e:
            print(f"Error en análisis temporal: {e}")

    def update_malignancy_analysis(self):
        """Actualizar análisis de malignidad"""
        if self.df is None or self.df.empty:
            return

        # Encontrar columnas de malignidad
        malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]

        if not malignidad_cols:
            return

        malignidad_col = malignidad_cols[0]

        # Analizar malignidad
        malignos = (self.df[malignidad_col].str.contains('PRESENTE', case=False, na=False)).sum()
        benignos = (self.df[malignidad_col].str.contains('AUSENTE', case=False, na=False)).sum()
        indeterminados = len(self.df) - malignos - benignos

        porcentaje_malignidad = (malignos / len(self.df) * 100) if len(self.df) > 0 else 0

        # Actualizar cards de malignidad
        malignancy_values = [
            ("Casos Malignos", str(malignos)),
            ("Casos Benignos", str(benignos)),
            ("Indeterminados", str(indeterminados)),
            ("% Malignidad", f"{porcentaje_malignidad:.1f}%")
        ]

        for title, value in malignancy_values:
            if title in self.malignancy_cards:
                self.malignancy_cards[title].value_label.config(text=value)

        # Actualizar gráficos y tablas de malignidad
        self.update_malignancy_charts()
        self.update_malignancy_biomarker_table()

    def update_diagnosis_chart(self):
        """Actualizar gráfico de distribución de diagnósticos"""
        try:
            # Limpiar frame anterior
            for widget in self.diagnosis_chart_frame.winfo_children():
                widget.destroy()

            # Encontrar columna de diagnóstico
            diag_cols = [col for col in self.df.columns if 'diagnostico' in col.lower()]
            if not diag_cols:
                return

            diag_col = diag_cols[0]

            # Crear figura
            fig = Figure(figsize=(12, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Contar diagnósticos por tipo (simplificado)
            diagnosticos = self.df[diag_col].dropna()

            # Clasificar en categorías principales
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

            bars = ax.bar(labels, values, color=['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc'])

            # Personalizar gráfico
            ax.set_title('Distribución por Tipos de Diagnóstico', fontsize=14, fontweight='bold')
            ax.set_ylabel('Número de Casos')

            # Agregar valores en las barras
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{value}', ha='center', va='bottom')

            fig.tight_layout()

            # Mostrar en la interfaz
            canvas = FigureCanvasTkAgg(fig, self.diagnosis_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=X, expand=True)

        except Exception as e:
            print(f"Error creando gráfico de diagnósticos: {e}")

    def update_top_diagnosis_table(self):
        """Actualizar tabla de top diagnósticos"""
        try:
            # Limpiar tabla
            for item in self.top_diagnosis_tree.get_children():
                self.top_diagnosis_tree.delete(item)

            # Encontrar columna de diagnóstico
            diag_cols = [col for col in self.df.columns if 'diagnostico' in col.lower()]
            if not diag_cols:
                return

            diag_col = diag_cols[0]

            # Contar diagnósticos
            diag_counts = self.df[diag_col].value_counts().head(10)
            total = len(self.df)

            # Agregar a la tabla
            for i, (diag, count) in enumerate(diag_counts.items()):
                percentage = (count / total * 100) if total > 0 else 0

                # Truncar diagnóstico si es muy largo
                diag_truncated = (diag[:60] + '...') if len(str(diag)) > 60 else str(diag)

                self.top_diagnosis_tree.insert(
                    '', 'end',
                    values=(diag_truncated, count, f"{percentage:.1f}%")
                )

        except Exception as e:
            print(f"Error actualizando tabla de diagnósticos: {e}")

    def update_biomarker_charts(self):
        """Actualizar gráficos de biomarcadores"""
        try:
            # Limpiar frame anterior
            for widget in self.biomarker_charts_frame.winfo_children():
                widget.destroy()

            # Encontrar columnas de biomarcadores IHQ_ correctas
            biomarker_cols = [col for col in self.df.columns if col.startswith('IHQ_')]

            if not biomarker_cols:
                # Mostrar mensaje si no hay datos
                ttk.Label(
                    self.biomarker_charts_frame,
                    text="No hay datos de biomarcadores para mostrar",
                    font=("Segoe UI", 10)
                ).pack(pady=20)
                return

            # Crear figura con subplots
            fig = Figure(figsize=(14, 6), dpi=100)

            # Gráfico de distribución de positividad
            ax1 = fig.add_subplot(121)

            # Contar casos positivos por biomarcador
            positivity_data = {}
            for col in biomarker_cols[:6]:  # Limitar a 6 principales
                col_name = col.replace('IHQ_', '').replace('_', ' ')

                # Contar casos con datos
                non_empty = self.df[col].notna() & (self.df[col].astype(str).str.strip() != '')
                total_count = non_empty.sum()

                if total_count > 0:
                    # Contar positivos
                    positive_count = self.df[col].astype(str).str.contains('POSITIV|\\+|[1-3]\\+', case=False, na=False, regex=True).sum()
                    positivity_data[col_name] = (positive_count / total_count) * 100

            if positivity_data:
                labels = list(positivity_data.keys())
                values = list(positivity_data.values())

                bars = ax1.bar(labels, values, color=['#ff6b6b', '#ffa726', '#66bb6a', '#42a5f5', '#ab47bc', '#ec407a'])
                ax1.set_title('% Positividad por Biomarcador', fontsize=12, fontweight='bold')
                ax1.set_ylabel('% Positividad')
                ax1.tick_params(axis='x', rotation=45)
                ax1.grid(axis='y', alpha=0.3)

                # Agregar valores en las barras
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                           f'{value:.1f}%', ha='center', va='bottom', fontsize=9)

            # Gráfico de completitud de datos
            ax2 = fig.add_subplot(122)
            completeness_data = {}
            for col in biomarker_cols[:6]:
                col_name = col.replace('IHQ_', '').replace('_', ' ')
                non_empty = self.df[col].notna() & (self.df[col].astype(str).str.strip() != '')
                completeness = (non_empty.sum() / len(self.df)) * 100
                completeness_data[col_name] = completeness

            if completeness_data:
                labels = list(completeness_data.keys())
                values = list(completeness_data.values())

                bars = ax2.barh(labels, values, color=['#4caf50', '#2196f3', '#ff9800', '#9c27b0', '#f44336', '#00bcd4'])
                ax2.set_title('% Completitud de Datos', fontsize=12, fontweight='bold')
                ax2.set_xlabel('% Registros con Datos')
                ax2.grid(axis='x', alpha=0.3)

                # Agregar valores en las barras
                for bar, value in zip(bars, values):
                    width = bar.get_width()
                    ax2.text(width + 1, bar.get_y() + bar.get_height()/2.,
                           f'{value:.1f}%', ha='left', va='center', fontsize=9)

            fig.tight_layout()

            # Mostrar en la interfaz
            canvas = FigureCanvasTkAgg(fig, self.biomarker_charts_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            print(f"Error creando gráficos de biomarcadores: {e}")
            ttk.Label(
                self.biomarker_charts_frame,
                text=f"Error al generar gráficos: {str(e)}",
                font=("Segoe UI", 10)
            ).pack(pady=20)

    def update_biomarker_stats_table(self):
        """Actualizar tabla de estadísticas de biomarcadores"""
        try:
            # Limpiar tabla
            for item in self.biomarker_stats_tree.get_children():
                self.biomarker_stats_tree.delete(item)

            # Encontrar columnas de biomarcadores - SOLO columnas IHQ_*
            biomarker_cols = [col for col in self.df.columns if col.startswith('IHQ_')]

            for col in biomarker_cols:
                col_name = col.replace('IHQ_', '').replace('_', ' ')

                # Calcular estadísticas
                total = self.df[col].notna().sum()

                if total == 0:
                    continue

                positivos = self.df[col].str.contains('POSITIV', case=False, na=False).sum()
                negativos = self.df[col].str.contains('NEGATIV', case=False, na=False).sum()
                porcentaje_pos = (positivos / total * 100) if total > 0 else 0

                # Intentar calcular media y desviación para valores numéricos
                media = "N/A"
                desv_std = "N/A"

                # Extraer valores numéricos (porcentajes, scores)
                numeric_values = []
                for val in self.df[col].dropna():
                    # Buscar números en el texto
                    numbers = re.findall(r'\d+(?:\.\d+)?', str(val))
                    for num in numbers:
                        try:
                            numeric_values.append(float(num))
                        except:
                            pass

                if numeric_values:
                    media = f"{np.mean(numeric_values):.2f}"
                    desv_std = f"{np.std(numeric_values):.2f}"

                # Agregar a la tabla
                self.biomarker_stats_tree.insert(
                    '', 'end',
                    values=(col_name, total, positivos, negativos, f"{porcentaje_pos:.1f}%", media, desv_std)
                )

        except Exception as e:
            print(f"Error actualizando tabla de estadísticas de biomarcadores: {e}")

    def update_temporal_charts(self, df_with_dates):
        """Actualizar gráficos temporales"""
        try:
            # Limpiar frames anteriores
            for widget in self.trends_chart_frame.winfo_children():
                widget.destroy()
            for widget in self.periods_chart_frame.winfo_children():
                widget.destroy()

            # Crear gráfico de tendencias
            fig1 = Figure(figsize=(12, 6), dpi=100)
            ax1 = fig1.add_subplot(111)

            # Agrupar por mes
            monthly_counts = df_with_dates.groupby('año_mes').size()

            # Convertir a fechas para el gráfico
            dates = [period.start_time for period in monthly_counts.index]
            counts = monthly_counts.values

            ax1.plot(dates, counts, marker='o', linewidth=2, markersize=6, color='#2196F3')
            ax1.set_title('Tendencia de Casos por Mes', fontsize=14, fontweight='bold')
            ax1.set_ylabel('Número de Casos')
            ax1.grid(True, alpha=0.3)

            # Rotar etiquetas del eje x
            fig1.autofmt_xdate()
            fig1.tight_layout()

            # Mostrar gráfico de tendencias
            canvas1 = FigureCanvasTkAgg(fig1, self.trends_chart_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill=X, expand=True)

            # Crear gráfico de distribución por año
            fig2 = Figure(figsize=(10, 6), dpi=100)
            ax2 = fig2.add_subplot(111)

            yearly_counts = df_with_dates.groupby('año').size()
            years = yearly_counts.index.astype(str)
            counts = yearly_counts.values

            bars = ax2.bar(years, counts, color='#4CAF50')
            ax2.set_title('Distribución de Casos por Año', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Número de Casos')

            # Agregar valores en las barras
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                       f'{count}', ha='center', va='bottom')

            fig2.tight_layout()

            # Mostrar gráfico de períodos
            canvas2 = FigureCanvasTkAgg(fig2, self.periods_chart_frame)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill=X, expand=True)

        except Exception as e:
            print(f"Error creando gráficos temporales: {e}")

    def update_monthly_stats_table(self, df_with_dates):
        """Actualizar tabla de estadísticas mensuales"""
        try:
            # Limpiar tabla
            for item in self.monthly_stats_tree.get_children():
                self.monthly_stats_tree.delete(item)

            # Agrupar por mes y calcular estadísticas
            grouped = df_with_dates.groupby('año_mes')

            # Encontrar columnas relevantes
            biomarker_cols = [col for col in df_with_dates.columns if any(bio in col.lower() for bio in ['her2', 'ki67', 'er', 'pr'])]
            malignidad_cols = [col for col in df_with_dates.columns if 'malign' in col.lower()]

            for period, group in grouped:
                total_casos = len(group)

                # Contar casos con biomarcadores
                con_biomarcadores = 0
                if biomarker_cols:
                    con_biomarcadores = group[biomarker_cols].notna().any(axis=1).sum()

                # Contar casos malignos
                malignos = 0
                if malignidad_cols:
                    malignos = group[malignidad_cols[0]].str.contains('PRESENTE', case=False, na=False).sum()

                # Calcular porcentaje de malignidad
                porcentaje_malignidad = (malignos / total_casos * 100) if total_casos > 0 else 0

                # Agregar a la tabla
                self.monthly_stats_tree.insert(
                    '', 'end',
                    values=(str(period), total_casos, con_biomarcadores, malignos, f"{porcentaje_malignidad:.1f}%")
                )

        except Exception as e:
            print(f"Error actualizando tabla de estadísticas mensuales: {e}")

    def update_malignancy_charts(self):
        """Actualizar gráficos de malignidad"""
        try:
            # Limpiar frame anterior
            for widget in self.malignancy_chart_frame.winfo_children():
                widget.destroy()

            # Encontrar columna de malignidad
            malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]
            if not malignidad_cols:
                return

            malignidad_col = malignidad_cols[0]

            # Crear figura
            fig = Figure(figsize=(12, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Contar tipos de malignidad
            malignos = (self.df[malignidad_col].str.contains('PRESENTE', case=False, na=False)).sum()
            benignos = (self.df[malignidad_col].str.contains('AUSENTE', case=False, na=False)).sum()
            indeterminados = len(self.df) - malignos - benignos

            # Crear gráfico de pie
            labels = ['Malignos', 'Benignos', 'Indeterminados']
            sizes = [malignos, benignos, indeterminados]
            colors = ['#ff6b6b', '#66bb6a', '#ffa726']

            # Filtrar valores cero
            filtered_data = [(label, size, color) for label, size, color in zip(labels, sizes, colors) if size > 0]
            if filtered_data:
                labels, sizes, colors = zip(*filtered_data)

                wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
                ax.set_title('Distribución de Malignidad', fontsize=14, fontweight='bold')

            fig.tight_layout()

            # Mostrar en la interfaz
            canvas = FigureCanvasTkAgg(fig, self.malignancy_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=X, expand=True)

        except Exception as e:
            print(f"Error creando gráfico de malignidad: {e}")

    def update_malignancy_biomarker_table(self):
        """Actualizar tabla de correlación malignidad-biomarcadores"""
        try:
            # Limpiar tabla
            for item in self.malignancy_biomarker_tree.get_children():
                self.malignancy_biomarker_tree.delete(item)

            # Encontrar columnas relevantes
            malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]
            biomarker_cols = [col for col in self.df.columns if any(bio in col.lower() for bio in ['her2', 'ki67', 'er', 'pr', 'p16'])]

            if not malignidad_cols or not biomarker_cols:
                return

            malignidad_col = malignidad_cols[0]

            # Crear máscaras para malignidad
            malignos_mask = self.df[malignidad_col].str.contains('PRESENTE', case=False, na=False)
            benignos_mask = self.df[malignidad_col].str.contains('AUSENTE', case=False, na=False)

            # Analizar cada biomarcador
            for col in biomarker_cols:
                col_name = col.replace('IHQ_', '').replace('_', ' ')

                # Crear máscara para biomarcador positivo
                bio_positivo_mask = self.df[col].str.contains('POSITIV', case=False, na=False)
                bio_negativo_mask = self.df[col].str.contains('NEGATIV', case=False, na=False)

                # Calcular intersecciones
                malignos_positivos = (malignos_mask & bio_positivo_mask).sum()
                malignos_negativos = (malignos_mask & bio_negativo_mask).sum()
                benignos_positivos = (benignos_mask & bio_positivo_mask).sum()
                benignos_negativos = (benignos_mask & bio_negativo_mask).sum()

                # Agregar a la tabla
                self.malignancy_biomarker_tree.insert(
                    '', 'end',
                    values=(col_name, malignos_positivos, malignos_negativos, benignos_positivos, benignos_negativos)
                )

        except Exception as e:
            print(f"Error actualizando tabla de correlación malignidad-biomarcadores: {e}")

    def show_no_data_message(self):
        """Mostrar mensaje cuando no hay datos"""
        ttk.Label(
            self.parent_frame,
            text="No hay datos disponibles en la base de datos",
            font=("Segoe UI", 14),
            foreground="gray"
        ).pack(expand=True)

    def show_error_message(self, error):
        """Mostrar mensaje de error"""
        ttk.Label(
            self.parent_frame,
            text=f"Error cargando datos: {error}",
            font=("Segoe UI", 12),
            foreground="red"
        ).pack(expand=True)

    def create_import_tab(self):
        """Crear pestaña de importación de datos"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.import_tab, padding=30)
        main_frame.pack(expand=True, fill=BOTH)

        # Título de la sección
        ttk.Label(
            main_frame,
            text="📥 Importación de Datos",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 30))

        # Descripción
        ttk.Label(
            main_frame,
            text="Selecciona archivos PDF o carpetas para procesar e importar a la base de datos",
            font=("Segoe UI", 11),
            foreground="gray"
        ).pack(pady=(0, 20))

        # Contenedor centralizado para botones
        button_container = ttk.Frame(main_frame)
        button_container.pack(expand=True)

        # Grid para centrar botones
        button_container.grid_rowconfigure(0, weight=1)
        button_container.grid_rowconfigure(1, weight=0)
        button_container.grid_rowconfigure(2, weight=0)
        button_container.grid_rowconfigure(3, weight=0)
        button_container.grid_rowconfigure(4, weight=1)
        button_container.grid_columnconfigure(0, weight=1)

        # Sección de importación de archivos
        import_section = ttk.LabelFrame(button_container, text="📄 Importar Archivos", padding=30)
        import_section.grid(row=1, column=0, pady=20, padx=50, sticky="ew")

        ttk.Button(
            import_section,
            text="📄 Seleccionar Archivo PDF",
            command=lambda: self.select_pdf_file(),
            bootstyle="primary",
            width=30
        ).pack(pady=10, fill=X)

        ttk.Button(
            import_section,
            text="📁 Seleccionar Carpeta de PDFs",
            command=lambda: self.select_pdf_folder(),
            bootstyle="primary",
            width=30
        ).pack(pady=10, fill=X)

        # Sección de archivos disponibles
        files_section = ttk.LabelFrame(button_container, text="📂 Archivos Disponibles", padding=30)
        files_section.grid(row=2, column=0, pady=20, padx=50, sticky="ew")

        # Lista de archivos
        list_frame = ttk.Frame(files_section)
        list_frame.pack(fill=X, pady=10)

        self.import_files_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 10),
            height=8
        )
        self.import_files_listbox.pack(side=LEFT, expand=True, fill=BOTH)

        import_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.import_files_listbox.yview)
        import_scrollbar.pack(side=RIGHT, fill=Y)
        self.import_files_listbox.configure(yscrollcommand=import_scrollbar.set)

        # Botones de control
        control_frame = ttk.Frame(files_section)
        control_frame.pack(fill=X, pady=(10, 0))
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)

        ttk.Button(
            control_frame,
            text="🔄 Actualizar Lista",
            command=lambda: self.refresh_files_list(),
            bootstyle="secondary"
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))

        ttk.Button(
            control_frame,
            text="⚡ Procesar Seleccionados",
            command=lambda: self.process_selected_files(),
            bootstyle="success"
        ).grid(row=0, column=1, sticky="ew", padx=(10, 0))

        # Información de progreso
        self.progress_section = ttk.LabelFrame(button_container, text="📊 Estado del Procesamiento", padding=20)
        self.progress_section.grid(row=3, column=0, pady=20, padx=50, sticky="ew")

        self.progress_label = ttk.Label(
            self.progress_section,
            text="Listo para procesar archivos",
            font=("Segoe UI", 10)
        )
        self.progress_label.pack()

        # Nota: No llamamos a refresh_files_list() aquí porque se llamará
        # después de que la UI principal conecte los métodos en _connect_import_functionality()

    # Métodos auxiliares para la funcionalidad de importación
    # Estos métodos serán reasignados por la UI principal en _connect_import_functionality()
    def select_pdf_file(self):
        """Método placeholder - será reasignado por la UI principal"""
        print("DEBUG: Dashboard.select_pdf_file() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método select_pdf_file no fue reasignado correctamente")

    def select_pdf_folder(self):
        """Método placeholder - será reasignado por la UI principal"""
        print("DEBUG: Dashboard.select_pdf_folder() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método select_pdf_folder no fue reasignado correctamente")

    def refresh_files_list(self):
        """Método placeholder - será reasignado por la UI principal"""
        print("DEBUG: Dashboard.refresh_files_list() llamado (PLACEHOLDER)")
        pass

    def process_selected_files(self):
        """Método placeholder - será reasignado por la UI principal"""
        print("DEBUG: Dashboard.process_selected_files() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método process_selected_files no fue reasignado correctamente")

    def create_export_tab(self):
        """Crear pestaña de exportaciones con visor de archivos"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.export_tab, padding=30)
        main_frame.pack(expand=True, fill=BOTH)

        # Título de la sección
        ttk.Label(
            main_frame,
            text="📤 Exportaciones Realizadas",
            font=("Segoe UI", 16, "bold")
        ).pack(pady=(0, 30))

        # Descripción
        ttk.Label(
            main_frame,
            text="Aquí se muestran todas las exportaciones realizadas. Puedes ver, editar y auditar el contenido.",
            font=("Segoe UI", 11),
            foreground="gray"
        ).pack(pady=(0, 20))

        # Contenedor principal
        content_container = ttk.Frame(main_frame)
        content_container.pack(expand=True, fill=BOTH)
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_columnconfigure(1, weight=2)
        content_container.grid_rowconfigure(0, weight=1)

        # Panel izquierdo - Lista de archivos exportados
        files_section = ttk.LabelFrame(content_container, text="📁 Archivos Exportados", padding=20)
        files_section.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Lista de archivos
        list_frame = ttk.Frame(files_section)
        list_frame.pack(fill=BOTH, expand=True, pady=10)

        self.exports_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 10),
            height=15
        )
        self.exports_listbox.pack(side=LEFT, expand=True, fill=BOTH)
        self.exports_listbox.bind("<<ListboxSelect>>", self.on_export_file_select)

        exports_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.exports_listbox.yview)
        exports_scrollbar.pack(side=RIGHT, fill=Y)
        self.exports_listbox.configure(yscrollcommand=exports_scrollbar.set)

        # Botones de control
        export_control_frame = ttk.Frame(files_section)
        export_control_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            export_control_frame,
            text="🔄 Actualizar Lista",
            command=self.refresh_exports_list,
            bootstyle="secondary"
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            export_control_frame,
            text="📂 Abrir Carpeta",
            command=self.open_exports_folder,
            bootstyle="info"
        ).pack(side=LEFT)

        # Panel derecho - Visor/Editor de contenido
        viewer_section = ttk.LabelFrame(content_container, text="👁️ Visor de Contenido", padding=20)
        viewer_section.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        viewer_section.grid_rowconfigure(2, weight=1)  # CORREGIDO: row 2 para el contenido
        viewer_section.grid_columnconfigure(0, weight=1)

        # Información del archivo seleccionado
        self.file_info_label = ttk.Label(
            viewer_section,
            text="Selecciona un archivo para ver su contenido",
            font=("Segoe UI", 12),
            foreground="gray"
        )
        self.file_info_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        # CORREGIDO: Frame para botones justo debajo del título
        self.viewer_buttons_frame = ttk.Frame(viewer_section)
        self.viewer_buttons_frame.grid(row=1, column=0, pady=(0, 10), sticky="w")

        # Botón Atrás (inicialmente oculto)
        self.back_button = ttk.Button(
            self.viewer_buttons_frame,
            text="← Atrás",
            command=self.clear_export_viewer,
            bootstyle="secondary"
        )

        # Botón Editar (inicialmente oculto)
        self.edit_button = ttk.Button(
            self.viewer_buttons_frame,
            text="✏️ Editar",
            command=self.edit_current_export,
            bootstyle="info"
        )

        # Variable para guardar el archivo actual
        self.current_export_file = None

        # CORREGIDO: Área de contenido ahora en row 2 (más espacio)
        self.content_frame = ttk.Frame(viewer_section)
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Mensaje inicial cuando no hay archivo seleccionado
        self.empty_viewer_label = ttk.Label(
            self.content_frame,
            text="👆 Selecciona un archivo de la lista para visualizar su contenido",
            font=("Segoe UI", 11),
            foreground="gray"
        )
        self.empty_viewer_label.pack(expand=True)

        # Inicializar lista de exportaciones
        self.refresh_exports_list()

    def on_export_file_select(self, event=None):
        """Manejar selección de archivo de exportación"""
        selection = self.exports_listbox.curselection()
        if not selection:
            return

        filename = self.exports_listbox.get(selection[0])
        self.load_export_file_content(filename)

    def load_export_file_content(self, filename):
        """Cargar contenido del archivo de exportación"""
        try:
            import os
            export_base_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Gestor Oncologico", "Exportaciones Base de datos")

            if filename.endswith('.xlsx'):
                file_path = os.path.join(export_base_path, "Excel", filename)
                self.load_excel_content(file_path, filename)
            elif filename.endswith('.db'):
                file_path = os.path.join(export_base_path, "Base de datos", filename)
                self.load_database_content(file_path, filename)

        except Exception as e:
            self.file_info_label.config(text=f"Error cargando archivo: {e}")

    def load_excel_content(self, file_path, filename):
        """Cargar contenido de archivo Excel"""
        try:
            import pandas as pd

            # Limpiar frame anterior
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Guardar archivo actual
            self.current_export_file = file_path

            # Actualizar etiqueta de información
            self.file_info_label.config(text=f"📊 Excel: {filename}")

            # Mostrar botones de control
            self.back_button.pack(side=tk.LEFT, padx=(0, 10))
            self.edit_button.pack(side=tk.LEFT)

            # Leer Excel
            df = pd.read_excel(file_path)

            # Crear Treeview para mostrar datos - OPTIMIZADO para mejor rendimiento
            tree = ttk.Treeview(self.content_frame, show="headings")
            tree.grid(row=0, column=0, sticky="nsew")

            # Configurar columnas
            tree["columns"] = list(df.columns)
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100, minwidth=50, stretch=False)  # stretch=False para mejor scroll

            # OPTIMIZADO: Insertar datos en lotes para mejor rendimiento
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                for index, row in batch.iterrows():
                    tree.insert('', 'end', values=list(row), iid=index)

            # Scrollbars OPTIMIZADAS con mejor velocidad
            v_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=tree.yview)
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=v_scrollbar.set)

            h_scrollbar = ttk.Scrollbar(self.content_frame, orient="horizontal", command=tree.xview)
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            tree.configure(xscrollcommand=h_scrollbar.set)
            
            # NUEVO: Scroll más rápido con mousewheel
            def _on_mousewheel(event):
                tree.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")  # 3x más rápido
                return "break"
            
            tree.bind("<MouseWheel>", _on_mousewheel)
            
            # NUEVO: Agregar tooltips en celdas
            self._add_tooltips_to_tree(tree)

        except Exception as e:
            self.file_info_label.config(text=f"Error cargando Excel: {e}")

    def load_database_content(self, file_path, filename):
        """Cargar contenido de base de datos"""
        try:
            import sqlite3
            import pandas as pd

            # Limpiar frame anterior
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Guardar archivo actual
            self.current_export_file = file_path

            # Actualizar etiqueta de información
            self.file_info_label.config(text=f"🗄️ Base de datos: {filename}")

            # Mostrar botones de control (solo Atrás para bases de datos)
            self.back_button.pack(side=tk.LEFT, padx=(0, 10))
            # No mostrar botón Editar para bases de datos

            # Conectar a la base de datos
            conn = sqlite3.connect(file_path)
            df = pd.read_sql_query("SELECT * FROM informes_ihq", conn)
            conn.close()

            # Crear Treeview para mostrar datos - OPTIMIZADO
            tree = ttk.Treeview(self.content_frame, show="headings")
            tree.grid(row=0, column=0, sticky="nsew")

            # Configurar columnas (mostrar solo las más importantes)
            important_cols = ['numero_peticion', 'fecha_informe', 'paciente_nombre', 'paciente_apellido', 'diagnostico_morfologico']
            available_cols = [col for col in important_cols if col in df.columns]

            tree["columns"] = available_cols
            for col in available_cols:
                tree.heading(col, text=col.replace('_', ' ').title())
                tree.column(col, width=120, minwidth=80, stretch=False)  # stretch=False para mejor scroll

            # OPTIMIZADO: Insertar datos en lotes
            batch_size = 100
            for i in range(0, len(df), batch_size):
                batch = df.iloc[i:i+batch_size]
                for index, row in batch.iterrows():
                    values = [str(row[col]) if pd.notna(row[col]) else "" for col in available_cols]
                    tree.insert('', 'end', values=values, iid=index)

            # Scrollbars OPTIMIZADAS
            v_scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=tree.yview)
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=v_scrollbar.set)

            h_scrollbar = ttk.Scrollbar(self.content_frame, orient="horizontal", command=tree.xview)
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            tree.configure(xscrollcommand=h_scrollbar.set)
            
            # NUEVO: Scroll más rápido con mousewheel
            def _on_mousewheel(event):
                tree.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")  # 3x más rápido
                return "break"
            
            tree.bind("<MouseWheel>", _on_mousewheel)
            
            # NUEVO: Agregar tooltips en celdas
            self._add_tooltips_to_tree(tree)

        except Exception as e:
            self.file_info_label.config(text=f"Error cargando base de datos: {e}")
    
    def _add_tooltips_to_tree(self, tree):
        """Agregar tooltips emergentes a las celdas del Treeview"""
        tooltip = None
        tooltip_job = None
        
        def show_tooltip(event):
            nonlocal tooltip, tooltip_job
            
            # Cancelar tooltip anterior
            if tooltip_job:
                tree.after_cancel(tooltip_job)
                tooltip_job = None
            
            if tooltip:
                tooltip.destroy()
                tooltip = None
            
            # Identificar celda
            region = tree.identify("region", event.x, event.y)
            if region != "cell":
                return
            
            column = tree.identify_column(event.x)
            row = tree.identify_row(event.y)
            
            if not column or not row:
                return
            
            # Obtener valor
            col_index = int(column.replace('#', '')) - 1
            values = tree.item(row)['values']
            
            if col_index >= len(values):
                return
            
            cell_value = str(values[col_index])
            
            # Solo mostrar si es largo
            if not cell_value or cell_value in ['', 'N/A', 'nan', 'None'] or len(cell_value) < 20:
                return
            
            # Crear tooltip con delay
            def create():
                nonlocal tooltip
                tooltip = tk.Toplevel(tree)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
                
                frame = tk.Frame(tooltip, bg="#ffffcc", relief="solid", borderwidth=1, padx=5, pady=5)
                frame.pack()
                
                display_text = cell_value[:500] + "..." if len(cell_value) > 500 else cell_value
                label = tk.Label(
                    frame,
                    text=display_text,
                    bg="#ffffcc",
                    fg="#000000",
                    font=("Segoe UI", 9),
                    wraplength=400,
                    justify=tk.LEFT
                )
                label.pack()
            
            tooltip_job = tree.after(500, create)
        
        def hide_tooltip(event):
            nonlocal tooltip, tooltip_job
            if tooltip_job:
                tree.after_cancel(tooltip_job)
                tooltip_job = None
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        tree.bind("<Motion>", show_tooltip)
        tree.bind("<Leave>", hide_tooltip)
        tree.bind("<Button-1>", hide_tooltip)

    def refresh_exports_list(self):
        """Actualizar lista de archivos exportados"""
        try:
            import os

            # Limpiar lista
            self.exports_listbox.delete(0, tk.END)

            export_base_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Gestor Oncologico", "Exportaciones Base de datos")

            files_found = False

            # Listar archivos Excel
            excel_path = os.path.join(export_base_path, "Excel")
            if os.path.exists(excel_path):
                for file in sorted(os.listdir(excel_path)):
                    if file.endswith('.xlsx'):
                        self.exports_listbox.insert(tk.END, file)
                        files_found = True

            # Listar archivos de base de datos
            db_path = os.path.join(export_base_path, "Base de datos")
            if os.path.exists(db_path):
                for file in sorted(os.listdir(db_path)):
                    if file.endswith('.db'):
                        self.exports_listbox.insert(tk.END, file)
                        files_found = True

            if not files_found:
                self.exports_listbox.insert(tk.END, "No hay exportaciones disponibles")

        except Exception as e:
            self.exports_listbox.delete(0, tk.END)
            self.exports_listbox.insert(tk.END, f"Error: {e}")

    def open_exports_folder(self):
        """Abrir carpeta de exportaciones en el explorador"""
        try:
            import os
            import subprocess

            export_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Gestor Oncologico", "Exportaciones Base de datos")

            if os.path.exists(export_path):
                subprocess.Popen(f'explorer "{export_path}"')
            else:
                print("La carpeta de exportaciones no existe aún")

        except Exception as e:
            print(f"Error abriendo carpeta: {e}")

    def clear_export_viewer(self):
        """Limpiar el visor y ocultar botones (función Atrás) - CORREGIDO"""
        try:
            # CORREGIDO: Desvincular temporalmente el evento para evitar recursión
            self.exports_listbox.unbind("<<ListboxSelect>>")

            # Limpiar contenido
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # CORREGIDO: Restaurar el mensaje inicial
            self.empty_viewer_label = ttk.Label(
                self.content_frame,
                text="👆 Selecciona un archivo de la lista para visualizar su contenido",
                font=("Segoe UI", 11),
                foreground="gray"
            )
            self.empty_viewer_label.pack(expand=True)

            # Ocultar botones
            self.back_button.pack_forget()
            self.edit_button.pack_forget()

            # Restablecer etiqueta de información
            self.file_info_label.config(
                text="Selecciona un archivo para ver su contenido",
                foreground="gray"
            )

            # Limpiar selección actual
            self.current_export_file = None

            # Limpiar selección en el listbox
            self.exports_listbox.selection_clear(0, tk.END)

            # CORREGIDO: Re-vincular el evento después de limpiar
            self.exports_listbox.bind("<<ListboxSelect>>", self.on_export_file_select)

            print("✅ Visor limpiado correctamente y restaurado a estado inicial")

        except Exception as e:
            print(f"Error limpiando visor: {e}")
            import traceback
            traceback.print_exc()
            # Asegurar que el evento se re-vincule incluso si hay error
            try:
                self.exports_listbox.bind("<<ListboxSelect>>", self.on_export_file_select)
            except:
                pass

    def edit_current_export(self):
        """Abrir editor para el archivo de exportación actual"""
        try:
            import os
            import tkinter.messagebox as mb

            if not self.current_export_file:
                mb.showwarning("Sin archivo", "No hay un archivo seleccionado para editar")
                return

            # Solo permitir edición de archivos Excel
            if not self.current_export_file.endswith('.xlsx'):
                mb.showinfo("No disponible", "Solo se pueden editar archivos Excel (.xlsx)")
                return

            # CORREGIDO: Crear ventana de edición usando parent_frame como parent
            # Obtener la ventana raíz
            root_window = self.parent_frame.winfo_toplevel()
            edit_window = tk.Toplevel(root_window)
            edit_window.title(f"Editar: {os.path.basename(self.current_export_file)}")
            edit_window.geometry("1400x900")

            # Frame principal
            main_frame = ttk.Frame(edit_window, padding=20)
            main_frame.pack(expand=True, fill=BOTH)

            # Título
            ttk.Label(
                main_frame,
                text=f"✏️ Editando: {os.path.basename(self.current_export_file)}",
                font=("Segoe UI", 14, "bold")
            ).pack(pady=(0, 20))

            # Frame para tabla con scrollbars
            table_frame = ttk.Frame(main_frame)
            table_frame.pack(expand=True, fill=BOTH)
            table_frame.grid_rowconfigure(0, weight=1)
            table_frame.grid_columnconfigure(0, weight=1)

            # Leer datos del Excel
            import pandas as pd
            df = pd.read_excel(self.current_export_file)

            # Crear Treeview editable MEJORADO
            tree = ttk.Treeview(table_frame, show="headings")
            tree.grid(row=0, column=0, sticky="nsew")

            # Configurar columnas
            tree["columns"] = list(df.columns)
            for col in df.columns:
                tree.heading(col, text=col)
                tree.column(col, width=120, minwidth=80, stretch=False)

            # Insertar datos con IDs únicos
            for index, row in df.iterrows():
                tree.insert('', 'end', values=list(row), iid=str(index))

            # Scrollbars OPTIMIZADAS
            v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            v_scroll.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=v_scroll.set)

            h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            h_scroll.grid(row=1, column=0, sticky="ew")
            tree.configure(xscrollcommand=h_scroll.set)
            
            # NUEVO: Scroll más rápido
            def _on_mousewheel(event):
                tree.yview_scroll(int(-1 * (event.delta / 120)) * 3, "units")
                return "break"
            
            tree.bind("<MouseWheel>", _on_mousewheel)
            
            # NUEVO: Hacer editable el Treeview con doble-click
            entry_popup = None
            
            def edit_cell(event):
                """Permitir edición de celda con doble-click"""
                nonlocal entry_popup
                
                # Identificar celda
                region = tree.identify("region", event.x, event.y)
                if region != "cell":
                    return
                
                column = tree.identify_column(event.x)
                row = tree.identify_row(event.y)
                
                if not column or not row:
                    return
                
                # Obtener índices
                col_index = int(column.replace('#', '')) - 1
                col_name = tree["columns"][col_index]
                
                # Obtener valor actual
                current_values = tree.item(row)['values']
                current_value = current_values[col_index]
                
                # Obtener posición de la celda
                x, y, width, height = tree.bbox(row, column)
                
                # Destruir entry anterior si existe
                if entry_popup:
                    entry_popup.destroy()
                
                # Crear Entry para edición
                entry_popup = ttk.Entry(tree, width=width)
                entry_popup.place(x=x, y=y, width=width, height=height)
                entry_popup.insert(0, str(current_value))
                entry_popup.select_range(0, tk.END)
                entry_popup.focus()
                
                def save_edit(event=None):
                    """Guardar el valor editado"""
                    nonlocal entry_popup
                    new_value = entry_popup.get()
                    
                    # Actualizar Treeview
                    new_values = list(current_values)
                    new_values[col_index] = new_value
                    tree.item(row, values=new_values)
                    
                    # Destruir entry
                    entry_popup.destroy()
                    entry_popup = None
                
                def cancel_edit(event=None):
                    """Cancelar edición"""
                    nonlocal entry_popup
                    if entry_popup:
                        entry_popup.destroy()
                        entry_popup = None
                
                # Vincular eventos
                entry_popup.bind("<Return>", save_edit)
                entry_popup.bind("<Escape>", cancel_edit)
                entry_popup.bind("<FocusOut>", save_edit)
            
            tree.bind("<Double-1>", edit_cell)
            
            # Agregar tooltips
            self._add_tooltips_to_tree(tree)

            # Frame de botones
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill=X, pady=(20, 0))

            def save_changes():
                """Guardar cambios en el archivo Excel"""
                try:
                    # Recolectar datos del Treeview
                    new_data = []
                    for item in tree.get_children():
                        values = tree.item(item)['values']
                        new_data.append(values)

                    # Crear nuevo DataFrame
                    new_df = pd.DataFrame(new_data, columns=df.columns)

                    # Guardar a Excel
                    new_df.to_excel(self.current_export_file, index=False)

                    mb.showinfo("Guardado", "Los cambios se han guardado exitosamente")

                    # Recargar el contenido en el visor principal
                    filename = os.path.basename(self.current_export_file)
                    self.load_excel_content(self.current_export_file, filename)

                except Exception as e:
                    mb.showerror("Error", f"Error al guardar cambios:\n{str(e)}")

            ttk.Button(
                buttons_frame,
                text="💾 Guardar Cambios",
                command=save_changes,
                bootstyle="success"
            ).pack(side=tk.LEFT, padx=(0, 10))

            ttk.Button(
                buttons_frame,
                text="❌ Cerrar sin Guardar",
                command=edit_window.destroy,
                bootstyle="danger"
            ).pack(side=tk.LEFT)

            # Notas informativas MEJORADAS
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(pady=(10, 0), fill=X)
            
            ttk.Label(
                info_frame,
                text="💡 Instrucciones:",
                font=("Segoe UI", 10, "bold"),
                foreground="#3498db"
            ).pack(anchor=W, pady=(0, 5))
            
            ttk.Label(
                info_frame,
                text="• Haz doble-click sobre cualquier celda para editarla",
                font=("Segoe UI", 9),
                foreground="#2c3e50"
            ).pack(anchor=W, padx=(20, 0))
            
            ttk.Label(
                info_frame,
                text="• Presiona Enter para guardar el cambio o Escape para cancelar",
                font=("Segoe UI", 9),
                foreground="#2c3e50"
            ).pack(anchor=W, padx=(20, 0))
            
            ttk.Label(
                info_frame,
                text="• Usa el scroll con la rueda del mouse (3x más rápido que antes)",
                font=("Segoe UI", 9),
                foreground="#2c3e50"
            ).pack(anchor=W, padx=(20, 0))
            
            ttk.Label(
                info_frame,
                text="⚠️ Los cambios se guardarán directamente en el archivo al hacer clic en 'Guardar Cambios'",
                font=("Segoe UI", 9),
                foreground="#ff6b6b"
            ).pack(anchor=W, padx=(20, 0), pady=(5, 0))

        except Exception as e:
            mb.showerror("Error", f"Error abriendo editor:\n{str(e)}")

    def refresh_dashboard(self):
        """Método público para refrescar el dashboard desde la UI principal"""
        self.refresh_all_data()