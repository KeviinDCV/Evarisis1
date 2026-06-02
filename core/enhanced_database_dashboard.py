#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Avanzado de Base de Datos - Sistema EVARISIS
Panel super robusto con estadísticas profundas de biomarcadores
"""

import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tksheet import Sheet  # V5.3.8: Tabla virtualizada tipo Excel
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import seaborn as sns
from collections import defaultdict
import re
import os
import subprocess
import platform
import logging
import traceback

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDatabaseDashboard:
    """Dashboard avanzado para análisis completo de la base de datos"""

    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.df = None
        self.biomarker_stats = {}
        self.charts = {}

        # v6.0.12: Variables para mensajes dinámicos
        self.no_data_label = None
        self.error_label = None

        # Configurar estilo de gráficos
        plt.style.use('default')
        sns.set_palette("husl")

        # Diccionario de nombres amigables para biomarcadores
        self.BIOMARKER_LABELS = {
            'RECEPTOR PROGESTERONOS': 'RECEPTOR DE PROGESTERONA',
            'RECEPTOR PROGESTERONA': 'RECEPTOR DE PROGESTERONA',
            'RECEPTOR ESTROGENO': 'RECEPTOR DE ESTRÓGENO',
            'RECEPTOR ESTROGENOS': 'RECEPTOR DE ESTRÓGENO',
            'E CADHERINA': 'E-Cadherina',
            'KI-67': 'Ki-67',
            'HER2': 'HER2',
            'PDL-1': 'PDL-1',
            'P16 ESTADO': 'P16',
            'P16 PORCENTAJE': 'P16 %'
        }

        self.create_dashboard()

    def create_dashboard(self):
        """Crear el dashboard completo"""

        # Título principal
        title_frame = ttk.Frame(self.parent_frame)
        title_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            title_frame,
            text="Gestión de la base de datos",
            font=("Segoe UI Semibold", 20),
            bootstyle="primary"
        ).pack(side=LEFT)

        # Crear contenedor con pestañas
        self.notebook = ttk.Notebook(self.parent_frame)
        self.notebook.pack(expand=True, fill=BOTH)

        # Pestaña 1: Estadísticas Generales
        self.general_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.general_tab, text="📊 Estadísticas Generales")

        # Pestaña 2: Visualizador de Datos
        self.visualizar_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visualizar_tab, text="📊 Visualizador de Datos")

        # Pestaña 3: Análisis de Biomarcadores
        self.biomarker_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.biomarker_tab, text="🧬 Biomarcadores")

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
        self.create_visualizar_tab()
        self.create_biomarker_analysis_tab()
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
                logging.error(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # ===== Seccion 1: Metricas principales (header limpio, sin LabelFrame) =====
        ttk.Label(
            main_frame, text="Métricas principales",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).pack(anchor=W, padx=24, pady=(22, 6))

        metrics_grid = ttk.Frame(main_frame)
        metrics_grid.pack(fill=X, padx=20)
        for i in range(4):
            metrics_grid.grid_columnconfigure(i, weight=1)

        self.metric_cards = {}
        metrics_data = [
            ("📊", "Total Registros", "0", "primary"),
            ("🧬", "Con Biomarcadores", "0", "success"),
            ("⚠️", "Casos Malignos", "0", "danger"),
            ("📅", "Días de Datos", "0", "info")
        ]
        for i, (icon, title, value, style) in enumerate(metrics_data):
            card = self.create_metric_card(metrics_grid, icon, title, value, style)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            self.metric_cards[title] = card

        # ===== Seccion 2: Distribucion por diagnosticos =====
        ttk.Label(
            main_frame, text="Distribución por diagnósticos",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).pack(anchor=W, padx=24, pady=(26, 6))

        self.diagnosis_chart_frame = ttk.Frame(main_frame)
        self.diagnosis_chart_frame.pack(fill=X, padx=24, pady=(0, 6))

        # ===== Seccion 3: Top 10 diagnosticos principales =====
        ttk.Label(
            main_frame, text="Top 10 diagnósticos principales",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).pack(anchor=W, padx=24, pady=(26, 6))

        top_wrap = ttk.Frame(main_frame)
        top_wrap.pack(fill=X, padx=24, pady=(0, 22))

        self.top_diagnosis_tree = ttk.Treeview(
            top_wrap,
            columns=("Diagnóstico Principal", "Frecuencia", "Porcentaje"),
            show="headings",
            height=10,
            style="Custom.Treeview"
        )
        self.top_diagnosis_tree.heading("Diagnóstico Principal", text="Diagnóstico Principal")
        self.top_diagnosis_tree.heading("Frecuencia", text="Frecuencia")
        self.top_diagnosis_tree.heading("Porcentaje", text="% del Total")
        self.top_diagnosis_tree.column("Diagnóstico Principal", width=400)
        self.top_diagnosis_tree.column("Frecuencia", width=100, anchor="center")
        self.top_diagnosis_tree.column("Porcentaje", width=100, anchor="center")

        diagnosis_scrollbar = ttk.Scrollbar(top_wrap, orient="vertical", command=self.top_diagnosis_tree.yview)
        diagnosis_scrollbar.pack(side="right", fill="y")
        self.top_diagnosis_tree.pack(side="left", fill=X, expand=True)
        self.top_diagnosis_tree.configure(yscrollcommand=diagnosis_scrollbar.set)

    def create_visualizar_tab(self):
        """Crear pestaña de visualizador de datos completo

        Esta pestaña contiene un visualizador completo con tabla, búsqueda y exportación.
        Nota: El contenido real (tabla Sheet) se inyecta desde ui.py después de la inicialización
        porque necesita acceso a los métodos de la UI principal.
        """
        # Frame principal para el visualizador
        self.visualizar_main_frame = ttk.Frame(self.visualizar_tab)
        self.visualizar_main_frame.pack(fill=BOTH, expand=True)

        # Título y controles superiores
        title_frame = ttk.Frame(self.visualizar_main_frame)
        title_frame.pack(fill=X, padx=10, pady=5)

        ttk.Label(
            title_frame,
            text="📊 Visualizador de Datos",
            font=("Segoe UI", 14, "bold")
        ).pack(side=LEFT)

        # Mensaje temporal (se reemplazará con controles reales desde ui.py)
        temp_label = ttk.Label(
            self.visualizar_main_frame,
            text="⏳ Inicializando visualizador...\n\nLa tabla de datos se cargará automáticamente.",
            font=("Segoe UI", 11),
            justify="center",
            foreground="#666"
        )
        temp_label.pack(expand=True, pady=50)

        # Frame para la tabla (se poblará desde ui.py)
        self.visualizar_table_container = ttk.Frame(self.visualizar_main_frame)
        self.visualizar_table_container.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Marcar que este tab necesita ser poblado
        self.visualizar_tab_needs_content = True

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
                logging.error(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # ===== Seccion 1: Resumen de biomarcadores (header limpio) =====
        ttk.Label(main_frame, text="Resumen de biomarcadores",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(22, 6))

        biomarker_grid = ttk.Frame(main_frame)
        biomarker_grid.pack(fill=X, padx=20)
        for i in range(6):
            biomarker_grid.grid_columnconfigure(i, weight=1, minsize=140)

        self.biomarker_cards = {}
        biomarker_data = [
            ("HER2", "0", "danger"),
            ("Ki-67", "0", "warning"),
            ("ER/PR", "0", "info"),
            ("P16", "0", "success"),
            ("PDL-1", "0", "secondary"),
            ("Otros", "0", "dark")
        ]
        for i, (name, value, style) in enumerate(biomarker_data):
            card = self.create_biomarker_card(biomarker_grid, name, value, style)
            card.grid(row=0, column=i, padx=6, pady=10, sticky="ew")
            self.biomarker_cards[name] = card

        # ===== Seccion 2: Distribucion de valores =====
        ttk.Label(main_frame, text="Distribución de valores",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        self.biomarker_charts_frame = ttk.Frame(main_frame)
        self.biomarker_charts_frame.pack(fill=X, padx=24, pady=(0, 6))

        # ===== Seccion 3: Correlaciones entre biomarcadores =====
        ttk.Label(main_frame, text="Correlaciones entre biomarcadores",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        self.correlation_frame = ttk.Frame(main_frame)
        self.correlation_frame.pack(fill=X, padx=24, pady=(0, 6))

        # ===== Seccion 4: Estadisticas detalladas =====
        ttk.Label(main_frame, text="Estadísticas detalladas",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        stats_wrap = ttk.Frame(main_frame)
        stats_wrap.pack(fill=X, padx=24, pady=(0, 6))

        self.biomarker_stats_tree = ttk.Treeview(
            stats_wrap,
            columns=("Biomarcador", "Total", "Positivos", "Negativos", "% Positividad", "Media", "Desv.Std"),
            show="headings",
            height=8,
            style="Custom.Treeview"
        )
        headers = ["Biomarcador", "Total", "Positivos", "Negativos", "% Positividad", "Media", "Desv.Std"]
        for header in headers:
            self.biomarker_stats_tree.heading(header, text=header)
            self.biomarker_stats_tree.column(header, width=120, anchor="center")
        self.biomarker_stats_tree.pack(fill=X, pady=6)

        # Nota informativa sobre interpretacion de HER2 (cohesiva)
        her2_info_frame = ttk.Frame(stats_wrap)
        her2_info_frame.pack(fill=X, pady=(12, 6))
        ttk.Label(her2_info_frame, text="ℹ️  Interpretación de HER2",
                  font=("Segoe UI Semibold", 10), bootstyle="primary").pack(anchor="w")
        ttk.Label(her2_info_frame,
                  text="0 y 1+ = NEGATIVO      ·      2+ = INDETERMINADO      ·      3+ = POSITIVO",
                  font=("Segoe UI", 9), bootstyle="secondary").pack(anchor="w", pady=(2, 0))

        # ===== Seccion 5: Distribucion de RE/RP por % de positividad =====
        ttk.Label(main_frame, text="Distribución de RE/RP por % de positividad",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        self.er_pr_chart_frame = ttk.Frame(main_frame)
        self.er_pr_chart_frame.pack(fill=X, padx=24, pady=(0, 22))

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
                logging.error(f"Error configurando scroll region: {e}")

        scrollable_frame.bind("<Configure>", configure_scroll_region)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Contenedor principal
        main_frame = scrollable_frame

        # ===== Seccion 1: Resumen de malignidad (header limpio) =====
        ttk.Label(main_frame, text="Resumen de malignidad",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(22, 6))

        malignancy_grid = ttk.Frame(main_frame)
        malignancy_grid.pack(fill=X, padx=20)
        for i in range(4):
            malignancy_grid.grid_columnconfigure(i, weight=1)

        self.malignancy_cards = {}
        malignancy_data = [
            ("⚠️", "Casos Malignos", "0", "danger"),
            ("✅", "Casos Benignos", "0", "success"),
            ("❓", "Indeterminados", "0", "warning"),
            ("📊", "% Malignidad", "0%", "info")
        ]
        for i, (icon, title, value, style) in enumerate(malignancy_data):
            card = self.create_metric_card(malignancy_grid, icon, title, value, style)
            card.grid(row=0, column=i, padx=8, pady=10, sticky="ew")
            self.malignancy_cards[title] = card

        # ===== Seccion 2: Tipos de malignidad =====
        ttk.Label(main_frame, text="Tipos de malignidad",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        self.malignancy_chart_frame = ttk.Frame(main_frame)
        self.malignancy_chart_frame.pack(fill=X, padx=24, pady=(0, 6))

        # ===== Seccion 3: Biomarcadores vs malignidad =====
        ttk.Label(main_frame, text="Biomarcadores vs malignidad",
                  font=("Segoe UI Semibold", 14), bootstyle="primary").pack(
                  anchor=W, padx=24, pady=(26, 6))
        corr_wrap = ttk.Frame(main_frame)
        corr_wrap.pack(fill=X, padx=24, pady=(0, 22))

        self.malignancy_biomarker_tree = ttk.Treeview(
            corr_wrap,
            columns=("Biomarcador", "Malignos Positivos", "Malignos Negativos", "Benignos Positivos", "Benignos Negativos"),
            show="headings",
            height=8,
            style="Custom.Treeview"
        )
        headers = ["Biomarcador", "Malignos Positivos", "Malignos Negativos", "Benignos Positivos", "Benignos Negativos"]
        for header in headers:
            self.malignancy_biomarker_tree.heading(header, text=header)
            self.malignancy_biomarker_tree.column(header, width=120, anchor="center")
        self.malignancy_biomarker_tree.pack(fill=X, pady=6)

    def create_metric_card(self, parent, icon, title, value, style):
        """Crear una tarjeta de metrica (V6.9.16) estilo dashboard moderno:
        barra de acento de color a la izquierda, etiqueta gris en mayuscula y
        el numero grande en azul institucional. Minimalista y de alto contraste."""
        card = ttk.Frame(parent, relief="solid", borderwidth=1)

        # Barra de acento de color (diferencia visual de cada metrica)
        bar = ttk.Frame(card, bootstyle=style, width=4)
        bar.pack(side=LEFT, fill=Y)

        # Cuerpo de la tarjeta
        body = ttk.Frame(card, padding=(18, 16))
        body.pack(side=LEFT, fill=BOTH, expand=True)

        # Etiqueta (gris, mayuscula, pequena)
        ttk.Label(
            body, text=title.upper(), font=("Segoe UI Semibold", 9),
            bootstyle="secondary", anchor=W
        ).pack(anchor=W)

        # Valor principal (numero grande en navy)
        value_label = ttk.Label(
            body, text=value, font=("Segoe UI", 26, "bold"),
            bootstyle="primary", anchor=W
        )
        value_label.pack(anchor=W, pady=(6, 0))

        # Guardar referencia del label de valor para actualizaciones
        card.value_label = value_label

        return card

    def create_biomarker_card(self, parent, name, value, style):
        """Tarjeta de biomarcador (V6.9.16): barra de acento de color + nombre
        gris en mayuscula + numero navy. Coherente con las KPI de Estadisticas."""
        card = ttk.Frame(parent, relief="solid", borderwidth=1)

        # Barra de acento de color
        bar = ttk.Frame(card, bootstyle=style, width=4)
        bar.pack(side=LEFT, fill=Y)

        body = ttk.Frame(card, padding=(14, 12))
        body.pack(side=LEFT, fill=BOTH, expand=True)

        # Nombre del biomarcador (gris, mayuscula)
        ttk.Label(body, text=name.upper(), font=("Segoe UI Semibold", 9),
                  bootstyle="secondary", anchor=W).pack(anchor=W)

        # Valor (numero grande navy)
        value_label = ttk.Label(body, text=value, font=("Segoe UI", 22, "bold"),
                                 bootstyle="primary", anchor=W)
        value_label.pack(anchor=W, pady=(4, 0))

        # Descripcion
        desc_label = ttk.Label(body, text="casos", font=("Segoe UI", 8),
                               bootstyle="secondary", anchor=W)
        desc_label.pack(anchor=W)

        # Guardar referencias
        card.value_label = value_label
        card.desc_label = desc_label

        return card

    def refresh_all_data(self):
        """Actualizar todos los datos del dashboard (v6.0.12: con limpieza de mensajes)"""
        try:
            # v6.0.12: Limpiar mensajes de estado antes de cargar datos
            self.clear_status_messages()

            # Cargar datos de la base de datos
            from core.database_manager import get_all_records_as_dataframe
            self.df = get_all_records_as_dataframe()

            if self.df is None or self.df.empty:
                self.show_no_data_message()
                return

            # Actualizar cada pestaña
            self.update_general_stats()
            self.update_biomarker_analysis()
            self.update_malignancy_analysis()

        except Exception as e:
            logging.error(f"Error actualizando dashboard: {e}")
            logging.error(f"Traceback completo: {traceback.format_exc()}")
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

        # Contar casos malignos (v6.0.12: Con validación robusta de tipos + valores correctos)
        malignant_count = 0
        malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]
        if malignidad_cols:
            try:
                # Convertir a string antes de usar .str.contains() para evitar errores
                # v6.0.12: CORREGIDO - Buscar 'MALIGNO' en lugar de 'PRESENTE'
                malignant_count = (self.df[malignidad_cols[0]].astype(str).str.contains('MALIGNO', case=False, na=False)).sum()
            except Exception as e:
                logger.warning(f"Error contando casos malignos: {e}")
                malignant_count = 0

        # Calcular días de datos (v6.0.12: CORREGIDO - Múltiples intentos con diferentes formatos)
        fecha_cols = [col for col in self.df.columns if 'fecha' in col.lower() and 'nacimiento' not in col.lower()]
        days_of_data = 0

        if fecha_cols:
            logging.info(f"Columnas de fecha encontradas: {fecha_cols}")

            # Intentar con múltiples columnas de fecha (prioridad: toma > ingreso > informe)
            fecha_priority = [
                'Fecha de toma (1. Fecha de la toma)',
                'Fecha de ingreso (2. Fecha de la muestra)',
                'Fecha Informe',
                'fecha_toma',
                'fecha_ingreso',
                'fecha_informe'
            ]

            # Buscar primera columna disponible según prioridad
            fecha_col = None
            for priority_col in fecha_priority:
                if priority_col in self.df.columns:
                    fecha_col = priority_col
                    logging.info(f"Usando columna de fecha prioritaria: {fecha_col}")
                    break

            # Si no encuentra columna prioritaria, usar la primera encontrada
            if not fecha_col:
                fecha_col = fecha_cols[0]
                logging.info(f"Usando primera columna de fecha encontrada: {fecha_col}")

            try:
                # Intentar múltiples formatos de fecha comunes
                fechas = None
                formatos = [
                    '%d/%m/%Y',      # 25/10/2025
                    '%Y-%m-%d',      # 2025-10-25
                    '%d-%m-%Y',      # 25-10-2025
                    '%m/%d/%Y',      # 10/25/2025
                    'mixed'          # Inferir automáticamente (pandas moderno)
                ]

                for formato in formatos:
                    try:
                        if formato == 'mixed':
                            # Para pandas moderno: usar format='mixed' o dejar None
                            try:
                                fechas = pd.to_datetime(self.df[fecha_col], errors='coerce', format='mixed')
                            except:
                                # Fallback para pandas antiguo
                                fechas = pd.to_datetime(self.df[fecha_col], errors='coerce')
                        else:
                            fechas = pd.to_datetime(self.df[fecha_col], errors='coerce', format=formato)

                        fechas_validas = fechas.dropna()
                        logging.info(f"Formato {formato}: {len(fechas_validas)} fechas válidas de {len(fechas)} totales")

                        if not fechas_validas.empty and len(fechas_validas) > 0:
                            fecha_min = fechas_validas.min()
                            fecha_max = fechas_validas.max()
                            days_of_data = (fecha_max - fecha_min).days
                            logging.info(f"Rango de fechas: {fecha_min} a {fecha_max} = {days_of_data} días")

                            if days_of_data >= 0:  # Aceptar incluso 0 días si hay fechas válidas
                                break
                    except Exception as e:
                        logging.debug(f"Formato {formato} falló: {e}")
                        continue

                if days_of_data == 0 and len(fechas_validas) == 0:
                    logger.warning(f"No se pudieron parsear fechas de columna '{fecha_col}'")
                    # Intentar mostrar algunas muestras de datos para debugging
                    muestras = self.df[fecha_col].head(5).tolist()
                    logger.warning(f"Muestras de datos en '{fecha_col}': {muestras}")

            except Exception as e:
                logger.error(f"Error calculando días de datos: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
                days_of_data = 0
        else:
            logging.warning("No se encontraron columnas de fecha en el DataFrame")

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

        # Biomarcadores destacados (tarjetas con nombre propio)
        # V6.9.17 FIX:
        #   - ER/PR: antes ['er','pr','receptor']. 'er'/'pr' como substring matcheaban por
        #     error HER2, Genero, Primer nombre/apellido, Servicio, Procedimiento, Diagnostico,
        #     Factor pronostico, E-Cadherina, EBER... (inflaba a 859). Ahora SOLO 'receptor'
        #     -> columnas IHQ_RECEPTOR_ESTROGENOS / IHQ_RECEPTOR_PROGESTERONA (real ~283).
        #   - PDL-1: antes ['pdl1','pd-l1'] NUNCA coincidian con la columna real IHQ_PDL-1
        #     (siempre mostraba 0). Ahora incluye 'pdl-1'.
        biomarkers = {
            'HER2': ['her2'],
            'Ki-67': ['ki67', 'ki-67'],
            'ER/PR': ['receptor'],
            'P16': ['p16'],
            'PDL-1': ['pdl-1', 'pdl1', 'pd-l1'],
        }

        # Columnas ya representadas por las tarjetas con nombre (se excluyen de "Otros")
        columnas_destacadas = set()
        for bio_name, keywords in biomarkers.items():
            cols = [c for c in self.df.columns if any(kw in c.lower() for kw in keywords)]
            columnas_destacadas.update(cols)

            count = self._count_valid_biomarkers(keywords)

            # Actualizar card
            if bio_name in self.biomarker_cards:
                self.biomarker_cards[bio_name].value_label.config(text=str(count))

        # V6.9.17 FIX "Otros": antes era un subconjunto fijo (gata, s100, cd, cromogranina,
        # sinaptofisina) que dejaba ~106 biomarcadores invisibles. Ahora cuenta los casos con
        # resultado valido en CUALQUIER otro biomarcador IHQ_ no destacado arriba.
        NO_SON_BIOMARCADOR = {'IHQ_ORGANO', 'IHQ_ESTUDIOS_SOLICITADOS'}
        otros_cols = [c for c in self.df.columns
                      if c.upper().startswith('IHQ_')
                      and c not in columnas_destacadas
                      and c.upper() not in NO_SON_BIOMARCADOR]
        total_other = self._count_valid_biomarkers_cols(otros_cols)

        if 'Otros' in self.biomarker_cards:
            self.biomarker_cards['Otros'].value_label.config(text=str(total_other))

        # Actualizar gráficos y tablas de biomarcadores
        self.update_biomarker_charts()
        self.update_biomarker_stats_table()
        self.update_er_pr_distribution()

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

    def _count_valid_biomarkers_cols(self, bio_cols):
        """V6.9.17: Igual que _count_valid_biomarkers pero recibe columnas EXPLICITAS
        (en vez de keywords). Cuenta casos con resultado valido en alguna de esas columnas.
        Se usa para la tarjeta 'Otros' (cualquier biomarcador no destacado)."""
        if not bio_cols:
            return 0

        count = 0
        for index, row in self.df.iterrows():
            for col in bio_cols:
                value = str(row[col]) if pd.notna(row[col]) else ""
                if self._is_valid_biomarker_result(value):
                    count += 1
                    break

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

    def update_malignancy_analysis(self):
        """Actualizar análisis de malignidad"""
        if self.df is None or self.df.empty:
            return

        # Encontrar columnas de malignidad
        malignidad_cols = [col for col in self.df.columns if 'malign' in col.lower()]

        if not malignidad_cols:
            return

        malignidad_col = malignidad_cols[0]

        # Analizar malignidad (v6.0.12: Con validación robusta de tipos + valores correctos)
        try:
            # v6.0.12: CORREGIDO - Buscar 'MALIGNO'/'BENIGNO' en lugar de 'PRESENTE'/'AUSENTE'
            malignos = (self.df[malignidad_col].astype(str).str.contains('MALIGNO', case=False, na=False)).sum()
            benignos = (self.df[malignidad_col].astype(str).str.contains('BENIGNO', case=False, na=False)).sum()
            indeterminados = len(self.df) - malignos - benignos
        except Exception as e:
            logger.warning(f"Error analizando malignidad: {e}")
            malignos = benignos = indeterminados = 0

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

            # Elegir columna de diagnóstico (preferir 'Diagnostico Principal')
            diag_col = None
            for col in self.df.columns:
                if col.lower() == 'diagnostico principal':
                    diag_col = col
                    break
            if diag_col is None:
                diag_cols = [col for col in self.df.columns if 'diagnostico' in col.lower()]
                if not diag_cols:
                    return
                diag_col = diag_cols[0]

            # V6.9.21: Categorización clínica GRANULAR (la misma del Resumen IA),
            # en vez de 5 buckets gruesos que metían casi todo en 'Otros' (964).
            try:
                from core.normalizador_diagnosticos import (
                    categorizar_diagnostico, categorizar_diagnostico_con_organo,
                )
                from core.normalizador_organos import normalizar_organo, elegir_columna_organo
                col_org = elegir_columna_organo(self.df.columns)
                if col_org is not None:
                    org_norm = self.df[col_org].apply(normalizar_organo)
                    cat_serie = self.df.apply(
                        lambda row: categorizar_diagnostico_con_organo(
                            row[diag_col],
                            org_norm.loc[row.name] if row.name in org_norm.index else None),
                        axis=1)
                else:
                    cat_serie = self.df[diag_col].apply(categorizar_diagnostico)
            except Exception as e_cat:
                logging.warning(f"Categorizador no disponible, usando conteo literal: {e_cat}")
                cat_serie = self.df[diag_col].dropna().astype(str)

            cat_top = cat_serie.value_counts()
            cat_top = cat_top[~cat_top.index.isin(['SIN DATO', '', 'N/A', 'NAN'])]
            top = cat_top.head(20)
            if top.empty:
                return

            # Barras horizontales: caben nombres largos y muchas categorías (con scroll)
            n = len(top)
            fig = Figure(figsize=(11, max(4.5, 0.42 * n + 1.2)), dpi=100)
            ax = fig.add_subplot(111)
            etiquetas = [str(k)[:48] for k in top.index][::-1]
            valores = list(top.values)[::-1]
            barras = ax.barh(etiquetas, valores, color="#2d3e5e")
            ax.set_title(f'Distribución por diagnóstico (top {n})', fontsize=14, fontweight='bold')
            ax.set_xlabel('Número de casos')
            ax.tick_params(axis='y', labelsize=9)
            ax.margins(x=0.12)
            for b, v in zip(barras, valores):
                ax.text(b.get_width(), b.get_y() + b.get_height() / 2, f' {v}',
                        va='center', fontsize=8)
            fig.tight_layout()

            # Mostrar en la interfaz
            canvas = FigureCanvasTkAgg(fig, self.diagnosis_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

        except Exception as e:
            logging.error(f"Error creando gráfico de diagnósticos: {e}")

    def update_top_diagnosis_table(self):
        """Actualizar tabla de top diagnósticos principales"""
        try:
            # Limpiar tabla
            for item in self.top_diagnosis_tree.get_children():
                self.top_diagnosis_tree.delete(item)

            # Buscar específicamente la columna "Diagnostico Principal"
            diag_col = None
            for col in self.df.columns:
                if col.lower() == 'diagnostico principal':
                    diag_col = col
                    break

            if diag_col is None:
                logging.warning("No se encontró la columna 'Diagnostico Principal'")
                # Mostrar mensaje en la tabla
                self.top_diagnosis_tree.insert(
                    '', 'end',
                    values=("No se encontró la columna 'Diagnostico Principal'", "-", "-")
                )
                return

            # Filtrar valores vacíos o N/A
            df_filtered = self.df[self.df[diag_col].notna() & (self.df[diag_col] != '') & (self.df[diag_col] != 'N/A')]

            if df_filtered.empty:
                self.top_diagnosis_tree.insert(
                    '', 'end',
                    values=("No hay diagnósticos principales registrados", "-", "-")
                )
                return

            # Contar diagnósticos principales
            diag_counts = df_filtered[diag_col].value_counts().head(10)
            total = len(df_filtered)

            # Agregar a la tabla
            for i, (diag, count) in enumerate(diag_counts.items()):
                percentage = (count / total * 100) if total > 0 else 0

                # Truncar diagnóstico si es muy largo (mostrar más caracteres)
                diag_truncated = (diag[:80] + '...') if len(str(diag)) > 80 else str(diag)

                self.top_diagnosis_tree.insert(
                    '', 'end',
                    values=(diag_truncated, count, f"{percentage:.1f}%")
                )

        except Exception as e:
            logging.error(f"Error actualizando tabla de diagnósticos principales: {e}")

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
                # Aplicar mapeo de nombre amigable
                col_name = self.BIOMARKER_LABELS.get(col_name, col_name)

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
                ax1.set_title('Distribución de biomarcadores', fontsize=12, fontweight='bold')
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
                # Aplicar mapeo de nombre amigable
                col_name = self.BIOMARKER_LABELS.get(col_name, col_name)
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
            logging.error(f"Error creando gráficos de biomarcadores: {e}")
            ttk.Label(
                self.biomarker_charts_frame,
                text=f"Error al generar gráficos: {str(e)}",
                font=("Segoe UI", 10)
            ).pack(pady=20)

    def _calcular_her2_scores(self):
        """
        Calcular scores de HER2 según interpretación médica:
        - 0 y 1+ = NEGATIVO
        - 2+ = INDETERMINADO
        - 3+ = POSITIVO

        Returns:
            tuple: (positivos, negativos, indeterminados)
        """
        positivos = 0
        negativos = 0
        indeterminados = 0

        if 'IHQ_HER2' not in self.df.columns:
            return (0, 0, 0)

        for valor in self.df['IHQ_HER2'].dropna():
            valor_str = str(valor).upper()

            # Buscar puntuación explícita (0, 1+, 2+, 3+)
            if '3+' in valor_str or '3 +' in valor_str:
                # 3+ = POSITIVO
                positivos += 1
            elif '2+' in valor_str or '2 +' in valor_str:
                # 2+ = INDETERMINADO
                indeterminados += 1
            elif '1+' in valor_str or '1 +' in valor_str:
                # 1+ = NEGATIVO
                negativos += 1
            elif ': 0' in valor_str or ' 0 ' in valor_str or valor_str.endswith(' 0') or valor_str.strip() == '0' or 'CERO' in valor_str or 'SCORE 0' in valor_str or 'SCORE: 0' in valor_str:
                # 0 = NEGATIVO (múltiples formatos: "HER2: 0", "HER2 0", "0", etc.)
                negativos += 1
            else:
                # Fallback: usar texto si no hay puntuación
                # (para valores actuales en BD: "NEGATIVO", "EQUIVOCO", etc.)
                if 'POSITIV' in valor_str:
                    positivos += 1
                elif 'NEGATIV' in valor_str:
                    negativos += 1
                elif 'EQUIVOCO' in valor_str or 'INDETERMINADO' in valor_str:
                    indeterminados += 1
                else:
                    # Valor no reconocido - contar como indeterminado
                    indeterminados += 1

        return (positivos, negativos, indeterminados)

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
                # Aplicar mapeo de nombre amigable
                col_name = self.BIOMARKER_LABELS.get(col_name, col_name)

                # Calcular estadísticas
                total = self.df[col].notna().sum()

                if total == 0:
                    continue

                # ⚕️ LÓGICA ESPECÍFICA PARA HER2 (según interpretación médica)
                if col == 'IHQ_HER2':
                    positivos, negativos, indeterminados = self._calcular_her2_scores()
                    # Para HER2: solo 3+ cuenta como positivo
                    porcentaje_pos = (positivos / total * 100) if total > 0 else 0
                else:
                    # Lógica estándar para otros biomarcadores
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
            logging.error(f"Error actualizando tabla de estadísticas de biomarcadores: {e}")

    def update_er_pr_distribution(self):
        """Actualizar gráfico de distribución de RE/RP por rangos de porcentaje"""
        try:
            # Limpiar frame anterior
            for widget in self.er_pr_chart_frame.winfo_children():
                widget.destroy()

            # Verificar si existen las columnas
            if 'IHQ_RECEPTOR_ESTROGENOS' not in self.df.columns and 'IHQ_RECEPTOR_PROGESTERONA' not in self.df.columns:
                ttk.Label(
                    self.er_pr_chart_frame,
                    text="No hay datos de RE/RP disponibles",
                    font=("Segoe UI", 10),
                    foreground="gray"
                ).pack(pady=20)
                return

            # Definir rangos de positividad (0-10%, 11-20%, etc.)
            rangos = [
                ('0-10%', 0, 10),
                ('11-20%', 11, 20),
                ('21-30%', 21, 30),
                ('31-40%', 31, 40),
                ('41-50%', 41, 50),
                ('51-60%', 51, 60),
                ('61-70%', 61, 70),
                ('71-80%', 71, 80),
                ('81-90%', 81, 90),
                ('91-100%', 91, 100)
            ]

            # Extraer porcentajes de RE y RP
            re_percentages = []
            rp_percentages = []

            # Procesar RE
            if 'IHQ_RECEPTOR_ESTROGENOS' in self.df.columns:
                for valor in self.df['IHQ_RECEPTOR_ESTROGENOS'].dropna():
                    valor_str = str(valor)
                    # Buscar porcentajes en el texto (ej: "90%", "85% positivo", etc.)
                    matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', valor_str)
                    if matches:
                        try:
                            pct = float(matches[0])
                            if 0 <= pct <= 100:
                                re_percentages.append(pct)
                        except:
                            pass

            # Procesar RP
            if 'IHQ_RECEPTOR_PROGESTERONA' in self.df.columns:
                for valor in self.df['IHQ_RECEPTOR_PROGESTERONA'].dropna():
                    valor_str = str(valor)
                    matches = re.findall(r'(\d+(?:\.\d+)?)\s*%', valor_str)
                    if matches:
                        try:
                            pct = float(matches[0])
                            if 0 <= pct <= 100:
                                rp_percentages.append(pct)
                        except:
                            pass

            # Si no hay datos, mostrar mensaje
            if not re_percentages and not rp_percentages:
                ttk.Label(
                    self.er_pr_chart_frame,
                    text="No se encontraron valores porcentuales en RE/RP",
                    font=("Segoe UI", 10),
                    foreground="gray"
                ).pack(pady=20)
                return

            # Clasificar en rangos
            re_counts = {rango[0]: 0 for rango in rangos}
            rp_counts = {rango[0]: 0 for rango in rangos}

            for pct in re_percentages:
                for rango_label, min_val, max_val in rangos:
                    if min_val <= pct <= max_val:
                        re_counts[rango_label] += 1
                        break

            for pct in rp_percentages:
                for rango_label, min_val, max_val in rangos:
                    if min_val <= pct <= max_val:
                        rp_counts[rango_label] += 1
                        break

            # Crear gráfico de barras agrupadas
            fig = Figure(figsize=(14, 6), dpi=100)
            ax = fig.add_subplot(111)

            # Preparar datos
            labels = [rango[0] for rango in rangos]
            re_values = [re_counts[label] for label in labels]
            rp_values = [rp_counts[label] for label in labels]

            # Posiciones de las barras
            x = np.arange(len(labels))
            width = 0.35

            # Crear barras
            bars1 = ax.bar(x - width/2, re_values, width, label='RE (Receptor de Estrógeno)', color='#ff6b6b')
            bars2 = ax.bar(x + width/2, rp_values, width, label='RP (Receptor de Progesterona)', color='#4ecdc4')

            # Configurar gráfico
            ax.set_xlabel('% de Positividad', fontsize=11, fontweight='bold')
            ax.set_ylabel('# de Casos', fontsize=11, fontweight='bold')
            ax.set_title('Distribución de RE/RP por Rangos de Positividad', fontsize=13, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.legend()
            ax.grid(axis='y', alpha=0.3)

            # Agregar valores sobre las barras
            def add_value_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    if height > 0:  # Solo mostrar si hay casos
                        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                               f'{int(height)}', ha='center', va='bottom', fontsize=9)

            add_value_labels(bars1)
            add_value_labels(bars2)

            fig.tight_layout()

            # Mostrar en la interfaz
            canvas = FigureCanvasTkAgg(fig, self.er_pr_chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=BOTH, expand=True)

            # Agregar resumen estadístico
            summary_frame = ttk.Frame(self.er_pr_chart_frame)
            summary_frame.pack(fill=X, pady=(10, 0), padx=10)

            summary_text = f"📊 Total casos RE: {len(re_percentages)}    |    Total casos RP: {len(rp_percentages)}"
            if re_percentages:
                summary_text += f"    |    Promedio RE: {np.mean(re_percentages):.1f}%"
            if rp_percentages:
                summary_text += f"    |    Promedio RP: {np.mean(rp_percentages):.1f}%"

            ttk.Label(
                summary_frame,
                text=summary_text,
                font=("Segoe UI", 9),
                foreground="#555555"
            ).pack()

        except Exception as e:
            logging.error(f"Error creando gráfico de distribución RE/RP: {e}")
            ttk.Label(
                self.er_pr_chart_frame,
                text=f"Error al generar gráfico: {str(e)}",
                font=("Segoe UI", 10),
                foreground="red"
            ).pack(pady=20)

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

            # Contar tipos de malignidad (v6.0.12: CORREGIDO - valores correctos + validación robusta)
            # v6.0.12: CORREGIDO - Buscar 'MALIGNO'/'BENIGNO' en lugar de 'PRESENTE'/'AUSENTE'
            malignos = (self.df[malignidad_col].astype(str).str.contains('MALIGNO', case=False, na=False)).sum()
            benignos = (self.df[malignidad_col].astype(str).str.contains('BENIGNO', case=False, na=False)).sum()
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
            logging.error(f"Error creando gráfico de malignidad: {e}")

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

            # Crear máscaras para malignidad (v6.0.12: CORREGIDO - valores correctos + validación robusta)
            # v6.0.12: CORREGIDO - Buscar 'MALIGNO'/'BENIGNO' en lugar de 'PRESENTE'/'AUSENTE'
            malignos_mask = self.df[malignidad_col].astype(str).str.contains('MALIGNO', case=False, na=False)
            benignos_mask = self.df[malignidad_col].astype(str).str.contains('BENIGNO', case=False, na=False)

            # Analizar cada biomarcador
            for col in biomarker_cols:
                col_name = col.replace('IHQ_', '').replace('_', ' ')
                # Aplicar mapeo de nombre amigable
                col_name = self.BIOMARKER_LABELS.get(col_name, col_name)

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
            logging.error(f"Error actualizando tabla de correlación malignidad-biomarcadores: {e}")

    def show_no_data_message(self):
        """Mostrar mensaje cuando no hay datos (v6.0.12: con limpieza automática)"""
        # Eliminar mensaje anterior si existe
        self.clear_status_messages()

        self.no_data_label = ttk.Label(
            self.parent_frame,
            text="No hay datos disponibles en la base de datos",
            font=("Segoe UI", 14),
            foreground="gray"
        )
        self.no_data_label.pack(expand=True)

    def show_error_message(self, error):
        """Mostrar mensaje de error (v6.0.12: con limpieza automática)"""
        # Eliminar mensaje anterior si existe
        self.clear_status_messages()

        self.error_label = ttk.Label(
            self.parent_frame,
            text=f"Error cargando datos: {error}",
            font=("Segoe UI", 12),
            foreground="red"
        )
        self.error_label.pack(expand=True)

    def clear_status_messages(self):
        """Eliminar mensajes de estado (v6.0.12: nueva función)"""
        if self.no_data_label is not None:
            try:
                self.no_data_label.destroy()
                self.no_data_label = None
            except:
                pass

        if self.error_label is not None:
            try:
                self.error_label.destroy()
                self.error_label = None
            except:
                pass

    def create_import_tab(self):
        """Crear pestaña de importación de datos (rediseño minimalista navy V6.9.16)"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.import_tab, padding=30)
        main_frame.pack(expand=True, fill=BOTH)

        # ===== Encabezado de página =====
        ttk.Label(
            main_frame, text="Importación de datos",
            font=("Segoe UI Semibold", 18), bootstyle="primary"
        ).pack(anchor=W)
        ttk.Label(
            main_frame,
            text="Seleccioná archivos PDF o carpetas para procesar e importar a la base de datos.",
            font=("Segoe UI", 10), bootstyle="secondary"
        ).pack(anchor=W, pady=(3, 24))

        # ===== Sección 1: Importar archivos =====
        ttk.Label(
            main_frame, text="Importar archivos",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).pack(anchor=W, pady=(0, 8))

        sel_row = ttk.Frame(main_frame)
        sel_row.pack(fill=X, pady=(0, 24))
        ttk.Button(
            sel_row, text="📄  Seleccionar archivo PDF",
            command=lambda: self.select_pdf_file(),
            bootstyle="primary", width=30
        ).pack(side=LEFT, padx=(0, 12))
        ttk.Button(
            sel_row, text="📁  Seleccionar carpeta de PDFs",
            command=lambda: self.select_pdf_folder(),
            bootstyle="primary-outline", width=30
        ).pack(side=LEFT)

        # ===== Sección 2: Archivos disponibles =====
        ttk.Label(
            main_frame, text="Archivos disponibles",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).pack(anchor=W, pady=(0, 8))

        # Lista de archivos (estilo limpio, selección navy)
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill=BOTH, expand=True)

        self.import_files_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            font=("Segoe UI", 10),
            height=10,
            bg="#ffffff", fg="#2a2f3a",
            relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground="#d2d9e6", highlightcolor="#2d3e5e",
            selectbackground="#2d3e5e", selectforeground="#ffffff",
            activestyle="none"
        )
        self.import_files_listbox.pack(side=LEFT, expand=True, fill=BOTH)

        import_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.import_files_listbox.yview)
        import_scrollbar.pack(side=RIGHT, fill=Y)
        self.import_files_listbox.configure(yscrollcommand=import_scrollbar.set)

        # Botones de control
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=X, pady=(14, 0))

        ttk.Button(
            control_frame,
            text="🔄  Actualizar lista",
            command=lambda: self.refresh_files_list(),
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            control_frame,
            text="⚡  Procesar seleccionados",
            command=lambda: self.process_selected_files(),
            bootstyle="success"
        ).pack(side=LEFT, padx=(0, 10))

        # V6.7.0: Procesar con IA — diagnóstico de cobertura del OCR.
        # Toma cada PDF, hace OCR completo (sin segmentación) y le pasa el
        # texto entero al LLM para que identifique TODOS los IHQ presentes.
        # Sirve para verificar si el extractor tradicional pierde casos.
        ttk.Button(
            control_frame,
            text="🤖  Procesar con IA",
            command=lambda: self.process_selected_files_ia(),
            bootstyle="info-outline"
        ).pack(side=LEFT)

        # Nota: No llamamos a refresh_files_list() aquí porque se llamará
        # después de que la UI principal conecte los métodos en _connect_import_functionality()

    # Métodos auxiliares para la funcionalidad de importación
    # Estos métodos serán reasignados por la UI principal en _connect_import_functionality()
    def select_pdf_file(self):
        """Método placeholder - será reasignado por la UI principal"""
        logging.debug("DEBUG: Dashboard.select_pdf_file() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método select_pdf_file no fue reasignado correctamente")

    def select_pdf_folder(self):
        """Método placeholder - será reasignado por la UI principal"""
        logging.debug("DEBUG: Dashboard.select_pdf_folder() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método select_pdf_folder no fue reasignado correctamente")

    def refresh_files_list(self):
        """Método placeholder - será reasignado por la UI principal"""
        logging.debug("DEBUG: Dashboard.refresh_files_list() llamado (PLACEHOLDER)")
        pass

    def process_selected_files(self):
        """Método placeholder - será reasignado por la UI principal"""
        logging.debug("DEBUG: Dashboard.process_selected_files() llamado (PLACEHOLDER - NO DEBERÍA VERSE)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método process_selected_files no fue reasignado correctamente")

    def process_selected_files_ia(self):
        """V6.7.0: Procesa los PDFs seleccionados pasando el OCR completo al LLM
        para verificar la cobertura del pipeline tradicional. Placeholder - será
        reasignado por la UI principal."""
        logging.debug("DEBUG: Dashboard.process_selected_files_ia() llamado (PLACEHOLDER)")
        import tkinter.messagebox as mb
        mb.showwarning("No conectado", "El método process_selected_files_ia no fue reasignado correctamente")

    def create_export_tab(self):
        """Crear pestaña de exportaciones con visor de archivos (rediseño minimalista navy V6.9.16)"""
        # Frame principal con padding
        main_frame = ttk.Frame(self.export_tab, padding=30)
        main_frame.pack(expand=True, fill=BOTH)

        # ===== Encabezado de página =====
        ttk.Label(
            main_frame, text="Exportaciones realizadas",
            font=("Segoe UI Semibold", 18), bootstyle="primary"
        ).pack(anchor=W)
        ttk.Label(
            main_frame,
            text="Visualizá, editá y auditá el contenido de las exportaciones generadas.",
            font=("Segoe UI", 10), bootstyle="secondary"
        ).pack(anchor=W, pady=(3, 24))

        # Contenedor principal (col0=lista, col1=visor | row0=headers, row1=contenido)
        content_container = ttk.Frame(main_frame)
        content_container.pack(expand=True, fill=BOTH)
        content_container.grid_columnconfigure(0, weight=1)
        content_container.grid_columnconfigure(1, weight=2)
        content_container.grid_rowconfigure(1, weight=1)

        # ----- Panel izquierdo: Archivos exportados -----
        ttk.Label(
            content_container, text="Archivos exportados",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).grid(row=0, column=0, sticky=W, pady=(0, 8), padx=(0, 16))

        left_panel = ttk.Frame(content_container)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 16))

        # Lista de archivos (estilo limpio, selección navy)
        list_frame = ttk.Frame(left_panel)
        list_frame.pack(fill=BOTH, expand=True)

        self.exports_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.SINGLE,
            font=("Segoe UI", 10),
            height=15,
            bg="#ffffff", fg="#2a2f3a",
            relief="flat", borderwidth=0,
            highlightthickness=1, highlightbackground="#d2d9e6", highlightcolor="#2d3e5e",
            selectbackground="#2d3e5e", selectforeground="#ffffff",
            activestyle="none"
        )
        self.exports_listbox.pack(side=LEFT, expand=True, fill=BOTH)
        self.exports_listbox.bind("<<ListboxSelect>>", self.on_export_file_select)

        exports_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.exports_listbox.yview)
        exports_scrollbar.pack(side=RIGHT, fill=Y)
        self.exports_listbox.configure(yscrollcommand=exports_scrollbar.set)

        # Botones de control
        export_control_frame = ttk.Frame(left_panel)
        export_control_frame.pack(fill=X, pady=(12, 0))

        ttk.Button(
            export_control_frame,
            text="🔄  Actualizar lista",
            command=self.refresh_exports_list,
            bootstyle="secondary-outline"
        ).pack(side=LEFT, padx=(0, 10))

        ttk.Button(
            export_control_frame,
            text="📂  Abrir carpeta",
            command=self.open_exports_folder,
            bootstyle="info-outline"
        ).pack(side=LEFT)

        # ----- Panel derecho: Visor de contenido -----
        ttk.Label(
            content_container, text="Visor de contenido",
            font=("Segoe UI Semibold", 14), bootstyle="primary"
        ).grid(row=0, column=1, sticky=W, pady=(0, 8))

        right_panel = ttk.Frame(content_container)
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.grid_rowconfigure(2, weight=1)  # row 2 = contenido (más espacio)
        right_panel.grid_columnconfigure(0, weight=1)

        # Información del archivo seleccionado
        self.file_info_label = ttk.Label(
            right_panel,
            text="Seleccioná un archivo para ver su contenido",
            font=("Segoe UI", 11),
            bootstyle="secondary"
        )
        self.file_info_label.grid(row=0, column=0, pady=(0, 10), sticky="w")

        # Frame para botones justo debajo del título
        self.viewer_buttons_frame = ttk.Frame(right_panel)
        self.viewer_buttons_frame.grid(row=1, column=0, pady=(0, 10), sticky="w")

        # Botón Atrás (inicialmente oculto)
        self.back_button = ttk.Button(
            self.viewer_buttons_frame,
            text="← Atrás",
            command=self.clear_export_viewer,
            bootstyle="secondary-outline"
        )

        # V5.3.8: Botón Abrir en Excel (inicialmente oculto)
        self.open_excel_button = ttk.Button(
            self.viewer_buttons_frame,
            text="📊  Abrir en Excel",
            command=self.open_in_excel,
            bootstyle="success"
        )

        # V5.3.8: Botón Abrir Carpeta (inicialmente oculto)
        self.open_folder_button = ttk.Button(
            self.viewer_buttons_frame,
            text="📂  Abrir carpeta",
            command=self.open_file_location,
            bootstyle="info-outline"
        )

        # Variable para guardar el archivo actual
        self.current_export_file = None

        # Área de contenido en row 2 (más espacio)
        self.content_frame = ttk.Frame(right_panel)
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        # Mensaje inicial cuando no hay archivo seleccionado
        self.empty_viewer_label = ttk.Label(
            self.content_frame,
            text="👆 Seleccioná un archivo de la lista para visualizar su contenido",
            font=("Segoe UI", 11),
            bootstyle="secondary"
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
            export_base_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Cirugía Oncológica", "Exportaciones Base de datos")

            if filename.endswith('.xlsx'):
                file_path = os.path.join(export_base_path, "Excel", filename)
                self.load_excel_content(file_path, filename)
            elif filename.endswith('.db'):
                file_path = os.path.join(export_base_path, "Base de datos", filename)
                self.load_database_content(file_path, filename)

        except Exception as e:
            self.file_info_label.config(text=f"Error cargando archivo: {e}")

    def load_excel_content(self, file_path, filename):
        """
        V5.3.8: Cargar contenido de archivo Excel con Sheet virtualizado
        RENDIMIENTO: Carga instantánea de archivos grandes (1000+ filas)
        """
        try:
            import pandas as pd

            # Limpiar frame anterior
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Guardar archivo actual
            self.current_export_file = file_path

            # Actualizar etiqueta de información con detalles del archivo
            file_size = os.path.getsize(file_path) / 1024  # KB
            self.file_info_label.config(
                text=f"📊 Excel: {filename} ({file_size:.1f} KB)"
            )

            # Mostrar botones de control
            self.back_button.pack(side=tk.LEFT, padx=(0, 10))
            self.open_excel_button.pack(side=tk.LEFT, padx=(0, 10))
            self.open_folder_button.pack(side=tk.LEFT)

            # Leer Excel
            logging.info(f"📖 Cargando Excel: {filename}...")
            df = pd.read_excel(file_path)
            logging.info(f"✅ Excel cargado: {len(df)} filas × {len(df.columns)} columnas")

            # V5.3.8: Crear Sheet virtualizado (ultra rápido)
            sheet = Sheet(
                self.content_frame,
                page_up_down_select_row=True,
                expand_sheet_if_paste_too_big=False,
                column_width=120,
                startup_select=(0, 0, "rows"),
                headers_height=28,
                default_row_height=22,
                show_horizontal_grid=True,
                show_vertical_grid=True,
                show_top_left=False,
                show_row_index=True,
                show_header=True,
                empty_horizontal=0,
                empty_vertical=0,
                header_font=("Segoe UI", 9, "bold"),
                font=("Segoe UI", 9, "normal"),
                header_bg="#e9edf3",  # Gris azulado claro (institucional)
                header_fg="#2d3e5e",  # Navy institucional
                table_bg="white",
                table_fg="#2a2f3a",
                table_selected_cells_bg="#dbe2f0",
                table_selected_cells_fg="#1f2733",
                table_selected_rows_bg="#eef1f6",
                table_selected_rows_fg="#1f2733",
                index_bg="#f4f6fa",
                index_fg="#2d3e5e"
            )
            sheet.grid(row=0, column=0, sticky="nsew")

            # Habilitar funcionalidades tipo Excel
            sheet.enable_bindings(
                "all",
                "copy",  # Ctrl+C
                "row_select",
                "column_select",
                "drag_select",
                "select_all",
                "arrowkeys",
                "single_select",
                "drag_and_drop"
            )

            # Deshabilitar edición (solo lectura)
            sheet.disable_bindings("edit_cell", "cut", "paste", "delete", "undo")

            # Preparar datos
            headers = list(df.columns)
            sheet_data = df.fillna("").astype(str).values.tolist()

            # Cargar datos (mega rápido con virtualización)
            sheet.set_sheet_data(data=sheet_data, reset_col_positions=True, reset_row_positions=True, redraw=False)
            sheet.headers(newheaders=headers, index=None, reset_col_positions=False, show_headers_if_not_sheet=True, redraw=False)

            # Configurar anchos de columnas inteligentemente
            for idx, col in enumerate(df.columns):
                # Calcular ancho óptimo basado en el contenido
                try:
                    max_len = max(df[col].astype(str).str.len().max(), len(col))
                    width = min(250, max(80, int(max_len * 8)))
                except:
                    width = 120  # Default

                sheet.column_width(column=idx, width=width, only_set_if_too_small=False, redraw=False)

            # Redibuja UNA SOLA VEZ (mega optimización)
            sheet.refresh()

            logging.info(f"✅ Visualizador Sheet cargado exitosamente")

        except Exception as e:
            logging.error(f"❌ Error cargando Excel: {e}")
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
            tree = ttk.Treeview(self.content_frame, show="headings", style="Custom.Treeview")
            tree.grid(row=0, column=0, sticky="nsew")

            # Configurar columnas (mostrar solo las más importantes)
            important_cols = ['numero_peticion', 'fecha_informe', 'paciente_nombre', 'paciente_apellido', 'diagnostico_coloracion', 'diagnostico_morfologico']
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

            export_base_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Cirugía Oncológica", "Exportaciones Base de datos")

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

            export_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS Cirugía Oncológica", "Exportaciones Base de datos")

            if os.path.exists(export_path):
                subprocess.Popen(f'explorer "{export_path}"')
            else:
                logging.warning("La carpeta de exportaciones no existe aún")

        except Exception as e:
            logging.error(f"Error abriendo carpeta: {e}")

    def open_in_excel(self):
        """V5.3.8: Abrir el archivo actual en Excel"""
        try:
            if not hasattr(self, 'current_export_file') or not self.current_export_file:
                logging.warning("No hay ningún archivo seleccionado")
                return

            if not os.path.exists(self.current_export_file):
                logging.warning(f"El archivo no existe: {self.current_export_file}")
                return

            # Cross-platform file opening
            system = platform.system()

            if system == "Windows":
                os.startfile(self.current_export_file)
            elif system == "Darwin":  # macOS
                subprocess.call(['open', self.current_export_file])
            else:  # Linux
                subprocess.call(['xdg-open', self.current_export_file])

            logging.info(f"✅ Abriendo en Excel: {os.path.basename(self.current_export_file)}")

        except Exception as e:
            logging.error(f"❌ Error abriendo archivo en Excel: {e}")

    def open_file_location(self):
        """V5.3.8: Abrir la carpeta contenedora del archivo actual"""
        try:
            if not hasattr(self, 'current_export_file') or not self.current_export_file:
                logging.warning("No hay ningún archivo seleccionado")
                return

            folder_path = os.path.dirname(self.current_export_file)

            if not os.path.exists(folder_path):
                logging.warning(f"La carpeta no existe: {folder_path}")
                return

            # Cross-platform folder opening
            system = platform.system()

            if system == "Windows":
                # Select the file in Windows Explorer
                subprocess.run(['explorer', '/select,', os.path.normpath(self.current_export_file)])
            elif system == "Darwin":  # macOS
                # Reveal file in Finder
                subprocess.call(['open', '-R', self.current_export_file])
            else:  # Linux
                # Open folder (most file managers don't support file selection)
                subprocess.call(['xdg-open', folder_path])

            logging.info(f"✅ Abriendo ubicación: {folder_path}")

        except Exception as e:
            logging.error(f"❌ Error abriendo ubicación del archivo: {e}")

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
                text="👆 Seleccioná un archivo de la lista para visualizar su contenido",
                font=("Segoe UI", 11),
                bootstyle="secondary"
            )
            self.empty_viewer_label.pack(expand=True)

            # Ocultar botones
            self.back_button.pack_forget()
            self.edit_button.pack_forget()

            # Restablecer etiqueta de información
            self.file_info_label.config(
                text="Seleccioná un archivo para ver su contenido",
                bootstyle="secondary"
            )

            # Limpiar selección actual
            self.current_export_file = None

            # Limpiar selección en el listbox
            self.exports_listbox.selection_clear(0, tk.END)

            # CORREGIDO: Re-vincular el evento después de limpiar
            self.exports_listbox.bind("<<ListboxSelect>>", self.on_export_file_select)

            logging.info("✅ Visor limpiado correctamente y restaurado a estado inicial")

        except Exception as e:
            logging.error(f"Error limpiando visor: {e}")
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
            tree = ttk.Treeview(table_frame, show="headings", style="Custom.Treeview")
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