#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS CIRUGÍA ONCOLÓGICA - Sistema de Oncología
Punto de entrada principal de la aplicación - Migrado completamente a TTKBootstrap

Este script se encarga de:
1. Configurar la ruta del ejecutable de Tesseract OCR.
2. Iniciar la interfaz gráfica de usuario moderna (dashboard).
"""

import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import tkinter.ttk as ttk_std
from PIL import Image, ImageTk
from tkinter import filedialog, messagebox
import tkinter as tk
from tksheet import Sheet  # V5.3.8: Tabla virtualizada tipo Excel
import threading
import os
import re
import pandas as pd
import seaborn as sns
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import numpy as np
import argparse
import sys
import logging
import traceback
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import configparser
import pytesseract
from pathlib import Path

from core.calendario import CalendarioInteligente
# LAZY IMPORT: huv_web_automation solo se importa cuando se necesita (evita error de webdriver_manager al iniciar)
# from core.huv_web_automation import automatizar_entrega_resultados, Credenciales
from core.enhanced_export_system import EnhancedExportSystem
from config.version_info import get_version_string, get_build_info, get_full_version_info, get_dependencies_actual

# === IMPORTS PARA SISTEMA DE AUDITORÍA IA ===
from core.debug_mapper import DebugMapper
from core.ventana_auditoria_ia import mostrar_ventana_auditoria
from core.database_manager import get_registro_by_peticion

# === IMPORTS DE UI HELPERS ===
from ui_helpers import ocr_helpers, database_helpers, export_helpers, chart_helpers

# ======================== CONSTANTES UI ========================
# Movido desde: config/huv_constants.py

# Meses en español para formateo de fechas
MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}

# Configuración para detección de duplicados
DUPLICATE_DETECTION = {
    'COLORS': {
        'duplicado': '#ff4444',      # Rojo para archivos duplicados
        'nuevo': '#44ff44',          # Verde para archivos nuevos
        'procesando': '#ffaa44',     # Naranja para en proceso
        'error': '#ff0000'           # Rojo intenso para errores
    },
    'SCROLL_SPEED_MULTIPLIER': 4,    # 4x más rápido que el scroll normal
    'HORIZONTAL_SCROLL_UNITS': 3     # Unidades por scroll
}

# =========================
# Configuración de Tesseract OCR
# =========================

def configure_tesseract():
    """
    Lee el archivo config.ini para encontrar la ruta de Tesseract OCR
    y la configura para que Pytesseract pueda utilizarla.
    """
    try:
        config = configparser.ConfigParser(interpolation=None)

        # CORREGIDO: Detectar si estamos en un ejecutable empaquetado
        if getattr(sys, 'frozen', False):
            # Estamos ejecutando como .exe - buscar config.ini junto al .exe
            base_path = Path(sys.executable).parent
        else:
            # Estamos ejecutando como script Python
            base_path = Path(__file__).resolve().parent

        config_path = base_path / 'config' / 'config.ini'
        config.read(config_path, encoding='utf-8')

        tesseract_cmd = None
        if sys.platform.startswith("win"):
            tesseract_cmd = config.get('PATHS', 'WINDOWS_TESSERACT', fallback=None)
        elif sys.platform.startswith("darwin"):
            tesseract_cmd = config.get('PATHS', 'MACOS_TESSERACT', fallback=None)
        else: # Asumimos Linux/otro
            tesseract_cmd = config.get('PATHS', 'LINUX_TESSERACT', fallback=None)

        if tesseract_cmd and Path(tesseract_cmd).exists():
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logging.info(f"Tesseract OCR configurado en: {tesseract_cmd}")
        else:
            logging.warning("No se encontro la ruta de Tesseract en config.ini o la ruta no es valida.")
            logging.warning("El sistema intentara usar la variable de entorno PATH.")

    except Exception as e:
        logging.error(f"Error al configurar Tesseract desde config.ini: {e}")
        logging.warning("Se continuara usando la configuracion por defecto de Pytesseract.")

# =========================
# Configuración de temas TTKBootstrap
# =========================

# Mapeo de argumentos de tema a temas TTKBootstrap
THEME_MAP = {
    "dark": "darkly",
    "light": "flatly", 
    "blue": "cosmo",
    "professional": "litera",
    "medical": "pulse",
    "modern": "superhero",
    "classic": "journal",
    # Agregar más temas TTKBootstrap compatibles
    "darkly": "darkly",
    "flatly": "flatly",
    "cosmo": "cosmo",
    "litera": "litera",
    "pulse": "pulse",
    "superhero": "superhero",
    "journal": "journal",
    "cyborg": "cyborg",
    "solar": "solar",
    "minty": "minty",
    "sandstone": "sandstone",
    "united": "united",
    "morph": "morph",
    "vapor": "vapor",
    "yeti": "yeti",
    "lumen": "lumen",
    "simplex": "simplex",
    "zephyr": "zephyr"
}

# Paleta de colores base (se ajustará según el tema)
COLORS = {
    "accent": "#2b6cb0",
    "bg": "#ffffff", 
    "surface": "#f8f9fa",
    "text": "#212529",
    "muted": "#6c757d"
}

# Estilo visual para seaborn/mpl dentro de Tk
sns.set_theme(
    style="darkgrid",
    rc={
        "axes.facecolor": "#343638",
        "grid.color": "#4a4d50",
        "figure.facecolor": "#2b2b2b",
        "text.color": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "axes.labelcolor": "white",
        "axes.titlecolor": "white",
    },
)

# Módulos del proyecto
# Importar módulo unificado de extractores refactorizados
import core.unified_extractor as procesador_ihq_biomarcadores
import core.database_manager as database_manager


class App(ttk.Window):
    def __init__(self, info_usuario=None, tema="superhero"):
        # Inicializar TTKBootstrap Window con el tema
        super().__init__(themename=tema)
        
        self.title("EVARISIS CIRUGÍA ONCOLÓGICA")
        self.state('zoomed')  # Maximizar ventana

        # Información del usuario
        self.info_usuario = info_usuario or {"nombre": "Invitado", "cargo": "N/A", "ruta_foto": "SIN_FOTO", "ruta_directorio_fotos": ""}
        
        # Fuentes estándar para consistencia - usando las mismas del proyecto estadístico
        self.FONT_TITULO = ("Segoe UI", 22, "bold")
        self.FONT_SUBTITULO = ("Segoe UI", 12)
        self.FONT_NORMAL = ("Segoe UI", 11)
        self.FONT_ETIQUETA = ("Segoe UI", 9, "italic")
        self.FONT_NOMBRE_PERFIL = ("Segoe UI", 16, "bold")
        self.FONT_BOTONES = ("Segoe UI", 12)
        
        # Configurar tema actual
        self.current_theme = tema
        self.temas_disponibles = [
            'superhero', 'flatly', 'cyborg', 'journal', 'solar', 'darkly', 
            'minty', 'pulse', 'sandstone', 'united', 'morph', 'vapor', 
            'yeti', 'cosmo', 'litera', 'lumen', 'simplex', 'zephyr'
        ]
        
        # Configurar iconos y foto del usuario
        self.iconos = self._cargar_iconos()
        self.foto_usuario = self._cargar_foto_usuario()

        # Estados del nuevo sistema de navegación flotante
        self.header_visible = True
        self.sidebar_visible = False  # Sidebar no se usa en el nuevo diseño flotante
        self.floating_menu_visible = False
        self.welcome_screen_active = True
        self.current_view = "welcome"  # welcome, database, visualizar, dashboard

        # NUEVO: Variables para tracking de importación y auditoría IA
        self._ultimos_registros_procesados = []  # Lista de IDs recién importados
        self.ultimos_resultados_ia = None  # Resultados de última auditoría IA

        # Crear la interfaz
        self._create_layout()

    def _create_layout(self):
        """Crear la interfaz principal usando TTKBootstrap"""
        # Crear layout principal similar al proyecto estadístico
        main_frame = ttk.Frame(self, padding=0)
        main_frame.pack(expand=True, fill=BOTH)

        # ===== Header institucional =====
        self._create_header(main_frame)

        # Variables necesarias ANTES de crear la interfaz
        self.master_df = pd.DataFrame()  # DataFrame maestro (fuente única de verdad)
        self._compare_controls = {}

        # Inicializar componentes que serán referenciados (para evitar AttributeError)
        self.cmb_servicio = None
        self.cmb_malig = None
        self.cmb_resp = None
        self.tree = None
        self._ultimas_filas_seleccionadas = []

        # Inicializar sistema de exportación mejorado
        self.export_system = EnhancedExportSystem(self)

        # Variables para paneles flotantes
        self.details_panel = None
        self.filters_panel = None

        # ===== Separador =====
        self.header_separator = ttk.Separator(main_frame, orient=HORIZONTAL)
        self.header_separator.pack(fill=X, padx=20, pady=5)

        # ===== Contenido principal (sin sidebar tradicional) =====
        self._create_main_content(main_frame)
        
        # ===== Menú flotante =====
        self._create_floating_menu()
        
        # ===== Botón flotante =====
        self._create_floating_button()

        # Inicializar estilo de treeview
        self._init_treeview_style()
        
        # Crear y mostrar pantalla de bienvenida inmediatamente
        self._create_welcome_screen()
        self.after(50, self.show_welcome_screen)

    def _create_header(self, parent):
        """Crear header institucional compacto y profesional"""
        self.header = ttk.Frame(parent, padding=(15, 8))
        self.header.pack(fill=X)

        # Logo izquierdo (compacto)
        left = ttk.Frame(self.header)
        left.pack(side=LEFT, padx=(0, 12))
        if self.iconos.get("logo1"):
            ttk.Label(left, image=self.iconos["logo1"]).pack()

        # Centro - Título y subtítulo
        center = ttk.Frame(self.header)
        center.pack(side=LEFT, expand=True)
        
        ttk.Label(
            center,
            text="EVARISIS CIRUGÍA ONCOLÓGICA",
            font=("Segoe UI", 18, "bold"),
            anchor=W
        ).pack(fill=X)
        
        ttk.Label(
            center,
            text="Suite de procesamiento y análisis oncológico del Hospital Universitario del Valle",
            font=("Segoe UI", 10),
            anchor=W,
            bootstyle=SECONDARY
        ).pack(fill=X, pady=(1, 0))

        # Perfil derecho
        right = ttk.Frame(self.header)
        right.pack(side=RIGHT)

        # Tarjeta de perfil profesional (más compacta)
        profile_card = ttk.Frame(right, padding=(10, 6), bootstyle="dark")
        profile_card.pack(side=RIGHT, padx=(8, 0))
        
        # Foto del usuario si existe
        if self.foto_usuario:
            ttk.Label(profile_card, image=self.foto_usuario).pack(side=LEFT, padx=(0, 8))
        
        # Datos del usuario
        datos = ttk.Frame(profile_card)
        datos.pack(side=LEFT)
        ttk.Label(datos, text=self.info_usuario.get("nombre", "Invitado"), font=("Segoe UI", 13, "bold")).pack(anchor=W)
        ttk.Label(datos, text=self.info_usuario.get("cargo", "N/A"), font=("Segoe UI", 10), bootstyle=INFO).pack(anchor=W)
        
        # Badge de versión (pill compacto)
        version_btn = ttk.Button(
            right,
            text=f"v{get_version_string().split('-')[0].replace('v', '')}",
            command=self._show_version_info,
            bootstyle="info-outline",
            width=7
        )
        version_btn.pack(side=RIGHT, padx=(8, 8))
        
        # Logo derecho (compacto)
        if self.iconos.get("logo3"):
            ttk.Label(right, image=self.iconos["logo3"]).pack(side=RIGHT, padx=(8, 0))

    def _create_main_content(self, parent):
        """Crear el contenido principal sin sidebar tradicional"""
        # Contenedor principal que ocupa toda la ventana
        self.content_container = ttk.Frame(parent, padding=0)
        self.content_container.pack(expand=True, fill=BOTH)

        # Crear los diferentes paneles de contenido
        self._create_content_panels()

    def _create_floating_menu(self):
        """Crear el menú flotante con diseño profesional y sombras"""
        # Frame principal del menú con sombra
        self.floating_menu = ttk.Frame(
            self, 
            padding=5,
            relief="raised",
            borderwidth=3
        )
        self.floating_menu.place(x=-300, y=20, width=280, height=420)  # Inicialmente oculto, más arriba
        
        # Header del menú con gradiente visual
        header_frame = ttk.Frame(self.floating_menu, bootstyle="primary", padding=10)
        header_frame.pack(fill=X, pady=(0, 5))
        
        # Título con mejor diseño
        ttk.Label(
            header_frame,
            text="🏥 HUV ONCOLOGÍA",
            font=("Segoe UI", 13, "bold"),
            bootstyle="inverse-primary",
            anchor="center"
        ).pack(expand=True)
        
        ttk.Label(
            header_frame,
            text="Panel de Navegación",
            font=("Segoe UI", 9),
            bootstyle="inverse-primary",
            anchor="center"
        ).pack()
        
        # Separador elegante
        separator = ttk.Separator(self.floating_menu, orient="horizontal")
        separator.pack(fill=X, padx=10, pady=5)
        
        # Frame para botones de navegación
        nav_frame = ttk.Frame(self.floating_menu, padding=5)
        nav_frame.pack(fill=BOTH, expand=True)
        
        # Botones de navegación con mejor espaciado y diseño
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Inicio", "home", "success-outline", self._nav_to_welcome),
            ("🗄️ Base de Datos", "database", "primary", self._nav_to_database),
            ("📈 Dashboard", "dashboard", "warning", self._nav_to_dashboard),
            ("📋 Análisis IA", "analisis", "danger-outline", self._nav_to_analisis_ia),
            ("🔗 Interoperabilidad QHORTE", "web", "secondary", self._nav_to_web_auto),
        ]
        
        for text, icon_key, style, callback in nav_items:
            # Frame para cada botón con efecto hover
            btn_frame = ttk.Frame(nav_frame, padding=2)
            btn_frame.pack(fill=X, pady=3)
            
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=callback,
                bootstyle=style,
                width=28
            )
            btn.pack(fill=X)
            self.nav_buttons[text] = btn
            
            # Agregar efectos hover
            btn.bind("<Enter>", lambda e, b=btn: self._on_menu_btn_hover(b, True))
            btn.bind("<Leave>", lambda e, b=btn: self._on_menu_btn_hover(b, False))
        
        # Footer con botón de cerrar
        footer_frame = ttk.Frame(self.floating_menu, bootstyle="secondary", padding=5)
        footer_frame.pack(fill=X, side=BOTTOM, pady=(5, 0))
        
        close_btn = ttk.Button(
            footer_frame,
            text="✕ Cerrar Menú",
            command=self._toggle_floating_menu,
            bootstyle="danger-outline",
            width=25
        )
        close_btn.pack()
        
        # Variable para controlar estado del menú
        self.menu_is_open = False

    def _on_menu_btn_hover(self, button, entering):
        """Efectos hover para botones del menú"""
        if entering:
            # Efecto al entrar - escalar ligeramente
            button.configure(cursor="hand2")
            # Aquí se podría agregar más efectos visuales
        else:
            # Efecto al salir - restaurar
            button.configure(cursor="")

    def _create_floating_button(self):
        """Crear el botón flotante circular, compacto y natural"""
        # Frame contenedor circular más pequeño
        self.floating_btn_container = ttk.Frame(
            self,
            relief="raised",
            borderwidth=2
        )
        self.floating_btn_container.place(x=15, y=150, width=50, height=50)
        
        # Botón flotante circular y compacto
        self.floating_btn = ttk.Button(
            self.floating_btn_container,
            text="⚡",  # Icono más compacto y moderno
            command=self._toggle_floating_menu,
            bootstyle="info-outline",  # Estilo outline para apariencia más suave
            width=2,  # Más compacto
            cursor="hand2"
        )
        self.floating_btn.pack(expand=True, fill=BOTH, padx=3, pady=3)
        
        # Variables para animaciones con nueva posición
        self.floating_btn_base_y = 150
        self.floating_animation_running = False
        self.hover_animation_running = False
        
        # Configurar eventos de hover
        self.floating_btn.bind("<Enter>", self._on_btn_hover_enter)
        self.floating_btn.bind("<Leave>", self._on_btn_hover_leave)
        
        # Agregar tooltip visual
        self.floating_btn.bind("<Button-1>", lambda e: self.floating_btn.configure(text="✕" if not self.floating_menu_visible else "☰"))
        
        # Iniciar animación flotante continua
        self._start_floating_animation()

    def _start_floating_animation(self):
        """Iniciar animación flotante continua sutil"""
        if not self.floating_animation_running and not self.floating_menu_visible:
            self.floating_animation_running = True
            self._animate_floating(0)

    def _animate_floating(self, step):
        """Animación flotante sutil - movimiento vertical suave como flotando"""
        if self.floating_animation_running and not self.floating_menu_visible:
            import math
            # Movimiento sinusoidal más sutil para botón pequeño (±3 pixels)  
            offset = math.sin(step * 0.08) * 3
            new_y = self.floating_btn_base_y + offset
            
            # Actualizar posición del botón con dimensiones más pequeñas
            if hasattr(self, 'floating_btn_container'):
                self.floating_btn_container.place(x=15, y=int(new_y), width=50, height=50)
            
            # Continuar la animación con ritmo más lento para mayor fluidez
            self.after(60, lambda: self._animate_floating(step + 1))
        elif self.floating_menu_visible:
            # Detener animación si el menú está visible
            self.floating_animation_running = False

    def _on_btn_hover_enter(self, event):
        """Efecto al pasar el mouse - vibración y cambio de color"""
        if not self.hover_animation_running:
            self.hover_animation_running = True
            # Cambiar a color más vibrante
            self.floating_btn.configure(bootstyle="warning")
            self._start_hover_vibration()

    def _on_btn_hover_leave(self, event):
        """Efecto al salir el mouse - restaurar estado normal"""
        self.hover_animation_running = False
        # Restaurar color original
        self.floating_btn.configure(bootstyle="info")

    def _start_hover_vibration(self):
        """Animación de vibración cuando el mouse está encima"""
        self._vibrate_button(0)

    def _vibrate_button(self, step):
        """Efecto de vibración muy sutil para botón pequeño"""
        if self.hover_animation_running and step < 12:  # Vibración más corta para botón pequeño
            import random
            # Vibración muy sutil para botón compacto (±1 pixel)
            offset_x = random.randint(-1, 1)
            offset_y = random.randint(-1, 1)
            
            base_x = 15 + offset_x
            base_y = self.floating_btn_base_y + offset_y
            
            if hasattr(self, 'floating_btn_container'):
                self.floating_btn_container.place(x=base_x, y=base_y, width=50, height=50)
            
            # Continuar vibración con ritmo más rápido para efecto de tembleque
            self.after(30, lambda: self._vibrate_button(step + 1))
        elif self.hover_animation_running:
            # Reiniciar vibración para efecto continuo mientras hay hover
            self.after(100, lambda: self._vibrate_button(0))

    def _hide_floating_button(self):
        """Ocultar el botón flotante con animación de desvanecimiento"""
        if hasattr(self, 'floating_btn_container'):
            # Detener animaciones actuales
            self.floating_animation_running = False
            self.hover_animation_running = False
            
            # Animación de desvanecimiento (escala hacia 0)
            def fade_out(step=0):
                if step <= 10:
                    # Reducir tamaño gradualmente
                    scale = 1 - (step / 10)
                    new_width = int(50 * scale)
                    new_height = int(50 * scale)
                    
                    if new_width > 0 and new_height > 0:
                        # Centrar el botón mientras se reduce
                        offset_x = (50 - new_width) // 2
                        offset_y = (50 - new_height) // 2
                        current_y = self.floating_btn_base_y if hasattr(self, 'floating_btn_base_y') else 150
                        
                        self.floating_btn_container.place(
                            x=15 + offset_x, 
                            y=current_y + offset_y, 
                            width=new_width, 
                            height=new_height
                        )
                    
                    self.after(20, lambda: fade_out(step + 1))
                else:
                    # Ocultar completamente
                    self.floating_btn_container.place_forget()
            
            fade_out()

    def _show_floating_button(self):
        """Mostrar el botón flotante con animación de aparición"""
        if hasattr(self, 'floating_btn_container'):
            # Determinar posición correcta según si el header está visible
            current_y = self.floating_btn_base_y if hasattr(self, 'floating_btn_base_y') else 150
            
            # Animación de aparición (escala desde 0)
            def fade_in(step=0):
                if step <= 10:
                    # Aumentar tamaño gradualmente
                    scale = step / 10
                    new_width = int(50 * scale)
                    new_height = int(50 * scale)
                    
                    if new_width > 0 and new_height > 0:
                        # Centrar el botón mientras crece
                        offset_x = (50 - new_width) // 2
                        offset_y = (50 - new_height) // 2
                        
                        self.floating_btn_container.place(
                            x=15 + offset_x, 
                            y=current_y + offset_y, 
                            width=new_width, 
                            height=new_height
                        )
                    
                    self.after(20, lambda: fade_in(step + 1))
                else:
                    # Restaurar tamaño completo y reactivar animaciones
                    self.floating_btn_container.place(x=15, y=current_y, width=50, height=50)
                    self._start_floating_animation()
            
            fade_in()

    def _toggle_floating_menu(self):
        """Alternar visibilidad del menú flotante con animación"""
        if self.floating_menu_visible:
            self._hide_floating_menu()
        else:
            self._show_floating_menu()

    def _show_floating_menu(self):
        """Mostrar el menú flotante con animación suave y ocultar botón"""
        self.floating_menu_visible = True
        
        # Ocultar el botón flotante con animación de desvanecimiento
        self._hide_floating_button()
        
        # Animación suave con easing (ease-out)
        def slide_in(step=0):
            if step <= 25:
                # Función de easing ease-out cuádrica
                progress = step / 25
                eased_progress = 1 - (1 - progress) ** 2
                x_pos = -300 + (eased_progress * 300)  # De -300 a 0
                
                self.floating_menu.place(x=int(x_pos), y=20, width=280, height=420)
                self.after(12, lambda: slide_in(step + 1))
        
        slide_in()

    def _hide_floating_menu(self):
        """Ocultar el menú flotante con animación suave y mostrar botón"""
        self.floating_menu_visible = False
        
        # Animación suave con easing (ease-in)
        def slide_out(step=0):
            if step <= 25:
                # Función de easing ease-in cuádrica
                progress = step / 25
                eased_progress = progress ** 2
                x_pos = 0 - (eased_progress * 300)  # De 0 a -300
                
                self.floating_menu.place(x=int(x_pos), y=20, width=280, height=420)
                self.after(12, lambda: slide_out(step + 1))
            else:
                # Cuando la animación termine, mostrar el botón flotante
                self._show_floating_button()
        
        slide_out()

    # Funciones de navegación modernas
    def _nav_to_welcome(self):
        """Navegar a la pantalla de bienvenida"""
        self._hide_floating_menu()
        self.current_view = "welcome"
        self._show_header()  # Mostrar header solo en bienvenida
        self.show_welcome_screen()

    def _nav_to_database(self):
        """Navegar a la sección de base de datos"""
        self._hide_floating_menu()
        self._hide_header_if_not_welcome()
        self.current_view = "database"
        self._show_panel(self.database_frame)

    def _nav_to_visualizar(self):
        """Navegar a la pestaña Visualizador de Datos dentro de Base de Datos"""
        self._hide_floating_menu()
        self._hide_header_if_not_welcome()
        self.current_view = "database"
        self._show_panel(self.database_frame)

        # Seleccionar la pestaña del visualizador (índice 1)
        if hasattr(self, 'enhanced_dashboard') and hasattr(self.enhanced_dashboard, 'notebook'):
            try:
                self.enhanced_dashboard.notebook.select(1)  # Pestaña "Visualizador de Datos"
                logging.info("📊 Navegando a pestaña Visualizador de Datos en Base de Datos")
            except Exception as e:
                logging.error(f"Error seleccionando pestaña visualizador: {e}")

    def _nav_to_dashboard(self):
        """Navegar a la sección de dashboard"""
        self._hide_floating_menu()
        self._hide_header_if_not_welcome()
        self.current_view = "dashboard"
        self._show_panel(self.dashboard_frame)

        # CORREGIDO: Auto-cargar datos si están vacíos y cargar dashboard
        try:
            if self.master_df.empty:
                from core.database_manager import init_db, get_all_records_as_dataframe
                # V6.2.0: Comentado - init_db() ya se llama en ihq_processor antes del guardado
                # Llamarlo aquí causa que el UPDATE de relleno sobrescriba valores recién insertados
                # init_db()
                self.master_df = get_all_records_as_dataframe()

                # Ordenar por número de caso automáticamente
                if self.master_df is not None and not self.master_df.empty and "Numero de caso" in self.master_df.columns:
                    self.master_df = self.master_df.sort_values(
                        by="Numero de caso",
                        ascending=True,
                        na_position='last'
                    ).reset_index(drop=True)
            self.cargar_dashboard()
        except Exception as e:
            logging.error(f"Error auto-cargando dashboard: {e}")
            # Aún cargar dashboard vacío para mostrar interfaz
            self.cargar_dashboard()

    def _nav_to_web_auto(self):
        """Navegar a la sección de automatización web"""
        self._hide_floating_menu()
        self._hide_header_if_not_welcome()
        messagebox.showinfo("Web Automation", "Función de automatización web - En desarrollo")

    def _nav_to_analisis_ia(self):
        """Navegar a sección de Análisis con IA"""
        self._hide_floating_menu()
        self._hide_header_if_not_welcome()
        self.current_view = "analisis_ia"
        self._show_panel(self.analisis_ia_frame)

    def _mostrar_selector_tipo_auditoria(self, tipo_auditoria, registros_incompletos=None):
        """
        Muestra ventana para seleccionar tipo de auditoría (Parcial o Completa)

        Args:
            tipo_auditoria: 'parcial' (valor predefinido desde ventana de resultados)
            registros_incompletos: Lista de registros incompletos
        """
        # Guardar registros incompletos para usar después
        self._registros_incompletos_temp = registros_incompletos

        from core.ventana_selector_auditoria import mostrar_selector_auditoria

        # Mostrar selector
        mostrar_selector_auditoria(
            parent=self,
            callback_seleccion=self._iniciar_auditoria_ia
        )

    def _iniciar_auditoria_ia(self, tipo_auditoria):
        """
        Callback cuando usuario elige auditar con IA

        Args:
            tipo_auditoria: 'parcial' o 'completa'
        """
        logging.info(f"Iniciando auditoria IA - Tipo: {tipo_auditoria}")

        # Guardar tipo de auditoría para usar en el callback de resultados
        self._tipo_auditoria_actual = tipo_auditoria

        # Recuperar registros incompletos guardados
        registros_incompletos = getattr(self, '_registros_incompletos_temp', None)

        if tipo_auditoria == 'parcial' and registros_incompletos:
            # Auditoría solo de registros incompletos
            try:
                from core.auditoria_parcial import auditar_registros_incompletos

                numeros_peticion = [r['numero_peticion'] for r in registros_incompletos]
                logging.info(f"Auditando {len(numeros_peticion)} registros incompletos")

                # Esto mostrará VentanaAuditoriaIA automáticamente
                auditar_registros_incompletos(
                    numeros_peticion=numeros_peticion,
                    parent=self,
                    callback_completado=self._mostrar_resultados_auditoria
                )
            except ImportError:
                # Fallback: usar auditoría completa si la parcial no está implementada
                logging.warning("Auditoria parcial no disponible, usando auditoria completa")
                from core.ventana_auditoria_ia import mostrar_ventana_auditoria

                mostrar_ventana_auditoria(
                    parent=self,
                    callback_completado=self._mostrar_resultados_auditoria
                )

        elif tipo_auditoria == 'completa':
            # Auditoría COMPLETA - Solo registros recién importados (igual que PARCIAL)
            logging.info("Auditando registros recien importados con analisis profundo")

            # Obtener registros recién importados
            ultimos_registros = getattr(self, '_ultimos_registros_procesados', [])

            if not ultimos_registros:
                messagebox.showwarning(
                    "Sin registros para auditar",
                    "No hay registros recién importados para auditar.\n\n"
                    "La auditoría COMPLETA solo procesa los casos que acabas de importar.\n\n"
                    "Para auditar casos específicos:\n"
                    "1. Ve a 'Visualizar datos'\n"
                    "2. Selecciona los casos que deseas auditar\n"
                    "3. (Funcionalidad en desarrollo)"
                )
                return

            logging.info(f"Registros recien importados: {len(ultimos_registros)}")

            try:
                from pathlib import Path
                import glob
                from core.debug_mapper import DebugMapper
                from core.database_manager import get_registro_by_peticion

                # Preparar casos para auditoría COMPLETA
                project_root = Path(__file__).parent
                casos_preparados = []

                for numero in ultimos_registros:
                    try:
                        # Obtener datos del registro de BD
                        registro_bd = get_registro_by_peticion(numero)
                        if not registro_bd:
                            logging.warning(f"No se encontro registro en BD para {numero}")
                            continue

                        # Cargar debug_map para tener el PDF completo
                        debug_maps_dir = project_root / "data" / "debug_maps"
                        pattern = str(debug_maps_dir / f"debug_map_{numero}_*.json")
                        debug_map_files = glob.glob(pattern)

                        if debug_map_files:
                            # Usar el más reciente
                            debug_map_path = Path(sorted(debug_map_files)[-1])
                            try:
                                debug_map = DebugMapper.cargar_mapa(debug_map_path)
                            except Exception as e:
                                logging.warning(f"Error cargando debug_map para {numero}: {e}")
                                debug_map = {}
                        else:
                            logging.warning(f"No se encontro debug_map para {numero}")
                            debug_map = {}

                        # Preparar caso para auditoría COMPLETA
                        caso = {
                            'numero_peticion': numero,
                            'datos_bd': registro_bd,
                            'debug_map': debug_map,
                            'modo': 'completa'
                        }

                        casos_preparados.append(caso)

                    except Exception as e:
                        logging.error(f"Error preparando {numero}: {e}")
                        continue

                if not casos_preparados:
                    logging.error("No se pudieron preparar casos para auditoria")
                    messagebox.showerror(
                        "Error",
                        "No se pudieron preparar los casos para auditoría.\n"
                        "Verifique que existan debug_maps en data/debug_maps/"
                    )
                    return

                logging.info(f"{len(casos_preparados)} casos preparados para auditoria COMPLETA")

                # Mostrar ventana de auditoría con casos recién importados
                from core.ventana_auditoria_ia import mostrar_ventana_auditoria

                mostrar_ventana_auditoria(
                    parent=self,
                    casos=casos_preparados,
                    modo='completa',
                    callback_completado=self._mostrar_resultados_auditoria
                )

            except Exception as e:
                logging.error(f"Error preparando auditoria completa: {e}", exc_info=True)
                messagebox.showerror(
                    "Error",
                    f"Error preparando auditoría completa:\n{str(e)}"
                )

    def _auditar_seleccion_parcial(self):
        """V3.2.4: Auditar el item seleccionado en modo PARCIAL"""
        self._auditar_item_seleccionado(modo='parcial')

    def _auditar_seleccion_completa(self):
        """V3.2.4: Auditar el item seleccionado en modo COMPLETA"""
        self._auditar_item_seleccionado(modo='completa')

    def _auditar_item_seleccionado(self, modo='completa'):
        """
        V3.2.4.2: Audita los items seleccionados en la tabla (1 o múltiples)

        Comportamiento inteligente:
        - 1 item seleccionado: Auditar individualmente
        - Múltiples items + COMPLETA: Auditar 1 por 1
        - Múltiples items + PARCIAL: Auditar en lotes de 3 (como auditoría masiva)

        Args:
            modo: 'parcial' o 'completa'
        """
        # Obtener selección
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Seleccionar registro",
                "Por favor selecciona al menos UN registro para auditar."
            )
            return

        num_seleccionados = len(selection)
        logging.info(f"Auditando {num_seleccionados} caso(s) seleccionado(s) (modo: {modo.upper()})")

        # V3.2.4.2: FIX 10 - Filtrado inteligente según estado de auditoría
        from core.database_manager import get_estado_auditoria

        # Extraer números de petición y filtrar según estado
        # v6.0.12: CORREGIDO - Sheet no tiene atributo ["columns"], usar método alternativo
        try:
            headers = self.sheet.headers() if hasattr(self.sheet, 'headers') else []
            col_idx = headers.index("Numero de caso") if "Numero de caso" in headers else 0
        except:
            col_idx = 0  # Fallback: primera columna es "Numero de caso"

        numeros_peticion = []
        casos_omitidos_info = {
            'ya_parcial': [],
            'ya_completa': [],
            'error': []
        }

        for item_id in selection:
            # tksheet: Usar get_row_data() en lugar de .item()
            values = self.sheet.get_row_data(item_id)
            try:
                if not values or len(values) <= col_idx:
                    logging.warning(f"No se pudieron obtener valores para item_id={item_id}")
                    continue
                numero = values[col_idx]
                estado = get_estado_auditoria(numero)

                # Lógica de filtrado inteligente
                if modo == 'parcial':
                    # AUDITORÍA PARCIAL: Solo procesar casos SIN auditoría
                    if estado == "PARCIAL":
                        casos_omitidos_info['ya_parcial'].append(numero)
                        logging.info(f"Omitiendo {numero}: Ya tiene auditoria PARCIAL")
                        continue
                    elif estado == "COMPLETA":
                        casos_omitidos_info['ya_completa'].append(numero)
                        logging.info(f"Omitiendo {numero}: Ya tiene auditoria COMPLETA")
                        continue
                    else:
                        # NULL o sin auditar → Procesar
                        numeros_peticion.append(numero)

                elif modo == 'completa':
                    # AUDITORÍA COMPLETA: Procesar NULL y PARCIAL, omitir COMPLETA
                    if estado == "COMPLETA":
                        casos_omitidos_info['ya_completa'].append(numero)
                        logging.info(f"Omitiendo {numero}: Ya tiene auditoria COMPLETA")
                        continue
                    else:
                        # NULL o PARCIAL → Procesar (PARCIAL se upgrade a COMPLETA)
                        numeros_peticion.append(numero)
                        if estado == "PARCIAL":
                            logging.info(f"{numero}: Upgrade de PARCIAL a COMPLETA")

            except (ValueError, IndexError) as e:
                casos_omitidos_info['error'].append(numero if 'numero' in locals() else 'desconocido')
                logging.warning(f"Error obteniendo numero de peticion de item {item_id}: {e}")
                continue

        # Mostrar resumen de omisiones si hay
        total_omitidos = len(casos_omitidos_info['ya_parcial']) + len(casos_omitidos_info['ya_completa']) + len(casos_omitidos_info['error'])

        if total_omitidos > 0:
            mensaje_omisiones = f"De {num_seleccionados} casos seleccionados:\n\n"
            mensaje_omisiones += f"✅ Se procesarán: {len(numeros_peticion)}\n"
            mensaje_omisiones += f"⏭️ Se omitirán: {total_omitidos}\n\n"

            if casos_omitidos_info['ya_parcial']:
                mensaje_omisiones += f"• {len(casos_omitidos_info['ya_parcial'])} ya tienen PARCIAL\n"
            if casos_omitidos_info['ya_completa']:
                mensaje_omisiones += f"• {len(casos_omitidos_info['ya_completa'])} ya tienen COMPLETA\n"
            if casos_omitidos_info['error']:
                mensaje_omisiones += f"• {len(casos_omitidos_info['error'])} con errores\n"

            logging.info(f"Resumen de filtrado:")
            logging.info(f"A procesar: {len(numeros_peticion)}")
            logging.info(f"Omitidos: {total_omitidos}")

            # Mostrar mensaje informativo al usuario
            if len(numeros_peticion) > 0:
                # Hay casos para procesar, informar omisiones
                messagebox.showinfo(
                    "Filtrado Inteligente",
                    mensaje_omisiones + f"\n¿Deseas continuar con los {len(numeros_peticion)} casos?"
                )

        # Verificar si quedan casos para procesar
        if not numeros_peticion:
            # Mensaje personalizado según el motivo
            if casos_omitidos_info['ya_completa'] and modo == 'completa':
                messagebox.showinfo(
                    "Nada que procesar",
                    f"Todos los {num_seleccionados} caso(s) seleccionado(s) ya tienen auditoría COMPLETA.\n\n"
                    f"✅ No es necesario volver a auditarlos."
                )
            elif casos_omitidos_info['ya_parcial'] and casos_omitidos_info['ya_completa'] and modo == 'parcial':
                messagebox.showinfo(
                    "Nada que procesar",
                    f"Todos los {num_seleccionados} caso(s) seleccionado(s) ya tienen auditoría.\n\n"
                    f"• {len(casos_omitidos_info['ya_parcial'])} con PARCIAL\n"
                    f"• {len(casos_omitidos_info['ya_completa'])} con COMPLETA\n\n"
                    f"💡 Selecciona casos sin auditar para procesarlos."
                )
            else:
                messagebox.showerror(
                    "Error",
                    f"No se pudo obtener los números de petición de los registros seleccionados.\n\n"
                    f"Casos con error: {len(casos_omitidos_info['error'])}"
                )
            return

        # V3.2.4.2: Lógica inteligente según número de items a procesar
        try:
            from pathlib import Path
            import glob
            from core.debug_mapper import DebugMapper
            from core.database_manager import get_registro_by_peticion
            from core.ventana_auditoria_ia import mostrar_ventana_auditoria

            project_root = Path(__file__).parent
            debug_maps_dir = project_root / "data" / "debug_maps"

            # Campos protegidos (no auditar)
            CAMPOS_PROTEGIDOS = [
                "Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido",
                "N. de identificación", "Edad", "Genero",
                "Fecha de ingreso (2. Fecha de la muestra)", "Tipo de documento",
                "Numero de caso"
            ]

            # Preparar TODOS los casos seleccionados
            casos_preparados = []
            casos_omitidos = 0

            for numero_peticion in numeros_peticion:
                logging.info(f"Preparando caso: {numero_peticion}")

                # Obtener datos del registro de BD
                registro_bd = get_registro_by_peticion(numero_peticion)
                if not registro_bd:
                    logging.warning(f"No se encontro en BD, omitiendo {numero_peticion}")
                    casos_omitidos += 1
                    continue

                # Cargar debug_map
                pattern = str(debug_maps_dir / f"debug_map_{numero_peticion}_*.json")
                debug_map_files = glob.glob(pattern)

                if debug_map_files:
                    debug_map_path = Path(sorted(debug_map_files)[-1])
                    try:
                        debug_map = DebugMapper.cargar_mapa(debug_map_path)
                        logging.info(f"Debug map cargado para {numero_peticion}")
                    except Exception as e:
                        logging.warning(f"Error cargando debug_map para {numero_peticion}: {e}")
                        debug_map = {}
                else:
                    logging.warning(f"No se encontro debug_map para {numero_peticion}")
                    debug_map = {}

                # Pre-check para modo PARCIAL (V5.1.2: Usar validation_checker)
                campos_vacios = []
                if modo == 'parcial':
                    # V5.1.2: FIX - Usar validation_checker en lugar de chequeo manual
                    # Esto filtra solo los campos REALMENTE faltantes (basándose en ESTUDIOS SOLICITADOS)
                    from core.validation_checker import verificar_completitud_registro

                    analisis = verificar_completitud_registro(numero_peticion)
                    campos_vacios = (
                        analisis.get('campos_faltantes', []) +
                        analisis.get('biomarcadores_faltantes', [])
                    )

                    logging.info(f"Campos realmente faltantes en {numero_peticion}: {len(campos_vacios)}")

                    # Si no hay campos faltantes, omitir este caso en modo PARCIAL
                    if len(campos_vacios) == 0:
                        logging.info(f"Caso {numero_peticion} completo, omitiendo en modo PARCIAL")
                        casos_omitidos += 1
                        continue

                # Preparar caso
                caso = {
                    'numero_peticion': numero_peticion,
                    'datos_bd': registro_bd,
                    'debug_map': debug_map
                }

                # Agregar campos_a_buscar en modo PARCIAL
                if modo == 'parcial':
                    caso['campos_a_buscar'] = campos_vacios
                    # V3.2.4.2: FIX 8 - Agregar batch_size para procesamiento por lotes
                    caso['batch_size'] = 3  # Lotes de 3 casos simultáneos

                casos_preparados.append(caso)

            # Verificar si hay casos para procesar
            if not casos_preparados:
                if modo == 'parcial' and casos_omitidos > 0:
                    messagebox.showinfo(
                        "Nada que auditar",
                        f"Los {casos_omitidos} caso(s) seleccionado(s) ya están completos.\n\n"
                        f"✅ No hay campos vacíos que completar en modo PARCIAL.\n\n"
                        f"💡 Si deseas verificar la calidad de los datos existentes,\n"
                        f"   usa 'Auditoría COMPLETA' en su lugar."
                    )
                else:
                    messagebox.showerror(
                        "Error",
                        "No se pudo preparar ningún caso para auditar"
                    )
                return

            num_casos = len(casos_preparados)
            logging.info(f"{num_casos} caso(s) preparado(s) para auditoria {modo.upper()}")
            if casos_omitidos > 0:
                logging.info(f"{casos_omitidos} caso(s) omitido(s)")

            # Guardar el modo para el callback
            self._modo_auditoria_seleccion = modo

            # DECISIÓN INTELIGENTE: ¿Procesamiento individual o por lotes?
            if num_casos == 1:
                # UN SOLO CASO: Procesar individualmente (más info en UI)
                logging.info(f"Procesamiento INDIVIDUAL (1 caso)")
                mostrar_ventana_auditoria(
                    parent=self,
                    casos=casos_preparados,
                    modo=modo,
                    callback_completado=self._callback_auditoria_seleccion
                )

            elif modo == 'completa':
                # MÚLTIPLES + COMPLETA: Procesar 1 por 1 (análisis profundo)
                logging.info(f"Procesamiento SECUENCIAL (modo COMPLETA, 1 por 1)")
                mostrar_ventana_auditoria(
                    parent=self,
                    casos=casos_preparados,
                    modo='completa',
                    callback_completado=self._callback_auditoria_seleccion
                )

            else:  # modo == 'parcial' and num_casos > 1
                # MÚLTIPLES + PARCIAL: Procesar en LOTES de 3 (como auditoría masiva)
                num_lotes = (num_casos + 2) // 3  # Redondear hacia arriba
                logging.info(f"Procesamiento POR LOTES (modo PARCIAL)")
                logging.info(f"{num_casos} casos = {num_lotes} lote(s) de 3")
                logging.info(f"Tiempo estimado: ~{num_lotes * 30}s")

                mostrar_ventana_auditoria(
                    parent=self,
                    casos=casos_preparados,
                    modo='parcial',
                    callback_completado=self._callback_auditoria_seleccion
                )

        except Exception as e:
            logging.error(f"Error preparando auditoria: {e}", exc_info=True)
            messagebox.showerror(
                "Error",
                f"Error preparando auditoría:\n{str(e)}"
            )

    def _callback_auditoria_seleccion(self, resultados):
        """
        V3.2.4: Callback específico para auditoría de selección
        V3.2.4.2: Simplificado - La actualización de estados ahora se hace en _mostrar_resultados_auditoria()
        """
        logging.info(f"Auditoria de seleccion completada")

        if not resultados:
            logging.warning(f"No hay resultados")
            return

        # V3.2.4.2: FIX 7 - La actualización de estados ahora es centralizada
        # _mostrar_resultados_auditoria() se encarga de actualizar BD y refrescar UI
        self._mostrar_resultados_auditoria(resultados)

    def _mostrar_resultados_auditoria(self, resultados):
        """
        Callback cuando termina la auditoría IA
        Genera reporte Markdown y navega a la sección de Análisis IA

        Args:
            resultados: Dict con resultados de auditoría
        """
        logging.info(f"Auditoria completada - Mostrando resultados")

        # Guardar resultados en variable de instancia
        self.ultimos_resultados_ia = resultados

        # V3.2.4.2: FIX 7 - Actualizar estados de auditoría en BD ANTES de refrescar UI
        # Determinar tipo de auditoría (intentar ambas variables para soportar ambos flujos)
        tipo_auditoria = getattr(self, '_modo_auditoria_seleccion', None) or getattr(self, '_tipo_auditoria_actual', 'completa')

        # Actualizar estado en BD para cada caso auditado exitosamente
        from core.database_manager import set_estado_auditoria

        if isinstance(resultados, list):
            # Formato: lista de resultados individuales
            for resultado in resultados:
                if resultado.get('exito'):
                    numero_peticion = resultado.get('numero_peticion')
                    if numero_peticion:
                        estado = "PARCIAL" if tipo_auditoria == 'parcial' else "COMPLETA"
                        set_estado_auditoria(numero_peticion, estado)
                        logging.info(f"Estado actualizado: {numero_peticion} -> {estado}")
        elif isinstance(resultados, dict) and 'resultados' in resultados:
            # Formato: dict con clave 'resultados'
            for resultado in resultados.get('resultados', []):
                if resultado.get('exito'):
                    numero_peticion = resultado.get('numero_peticion')
                    if numero_peticion:
                        estado = "PARCIAL" if tipo_auditoria == 'parcial' else "COMPLETA"
                        set_estado_auditoria(numero_peticion, estado)
                        logging.info(f"Estado actualizado: {numero_peticion} -> {estado}")

        # Refrescar tabla DESPUÉS de actualizar BD
        self.refresh_data_and_table()

        # Generar reporte Markdown
        logging.info(f"Generando reporte Markdown...")
        ruta_reporte = self._generar_reporte_ia(resultados, tipo_auditoria)

        if ruta_reporte:
            logging.info(f"Reporte generado exitosamente: {ruta_reporte}")

            # Navegar a la sección de Análisis IA
            logging.info(f"Navegando a seccion Analisis IA...")
            try:
                self._nav_to_analisis_ia()
                logging.info(f"Navegacion exitosa")
            except Exception as e:
                logging.error(f"Error navegando: {e}", exc_info=True)

            # Actualizar lista de reportes
            try:
                self._actualizar_lista_reportes()
                logging.info(f"Lista de reportes actualizada")
            except Exception as e:
                logging.warning(f"Error actualizando lista de reportes: {e}")
                # Continuar sin fallar

            # Seleccionar automáticamente el reporte recién generado
            try:
                self._seleccionar_ultimo_reporte()
                logging.info(f"Reporte seleccionado automaticamente")
            except Exception as e:
                logging.warning(f"Error seleccionando reporte: {e}")
                # Continuar sin fallar

            # V2.1.6: No mostrar mensaje automáticamente
            # El mensaje se mostrará cuando el usuario haga clic en "Ver Resultados"
            # Guardar ruta para mostrar después
            self._ruta_ultimo_reporte = ruta_reporte
        else:
            logging.error(f"Error generando reporte")
            messagebox.showerror(
                "Error",
                "La auditoría se completó pero hubo un error al generar el reporte."
            )
            # Navegar al visualizador como fallback
            self._nav_to_visualizar()

    def _show_version_info(self):
        """Mostrar información detallada de la versión del sistema"""
        self._hide_floating_menu()
        
        try:
            version_info = get_full_version_info()
            actual_deps = get_dependencies_actual()
            
            # Crear ventana modal
            version_window = ttk.Toplevel(self)
            version_window.title(f"Acerca de - {version_info['project']['name']}")
            version_window.resizable(True, True)

            # Configurar fondo gris claro
            version_window.configure(bg='#f0f0f0')

            # IMPORTANTE: Maximizar ANTES de transient y grab_set
            try:
                version_window.state('zoomed')  # Windows
            except:
                try:
                    version_window.attributes('-zoomed', True)  # Linux
                except:
                    # Fallback: tamaño muy grande
                    screen_width = version_window.winfo_screenwidth()
                    screen_height = version_window.winfo_screenheight()
                    version_window.geometry(f"{screen_width-100}x{screen_height-100}+50+50")

            # Después de maximizar, configurar modal
            version_window.transient(self)
            version_window.grab_set()
            
            # Frame principal
            main_frame = ttk.Frame(version_window, padding=10)
            main_frame.pack(fill=BOTH, expand=True)
            
            # Header con información principal
            header_frame = ttk.Frame(main_frame, bootstyle="primary", padding=15)
            header_frame.pack(fill=X, pady=(0, 10))
            
            ttk.Label(
                header_frame,
                text=version_info['project']['name'],
                font=("Arial", 18, "bold"),
                bootstyle="inverse-primary"
            ).pack()
            
            ttk.Label(
                header_frame,
                text=f"{get_version_string()} | {get_build_info()}",
                font=("Arial", 12),
                bootstyle="inverse-primary"
            ).pack(pady=(5, 0))
            
            ttk.Label(
                header_frame,
                text=version_info['project']['description'],
                font=("Arial", 10),
                bootstyle="inverse-primary"
            ).pack(pady=(5, 0))
            
            # Notebook para las diferentes secciones
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=BOTH, expand=True, pady=10)
            
            # Tab 1: Información General - Compacta, sin scroll
            info_frame = ttk.Frame(notebook, padding=15)
            notebook.add(info_frame, text="📋 General")

            # Frame para centrar el contenido
            info_center = ttk.Frame(info_frame)
            info_center.pack(expand=True)
            
            # Traducir tipo de release a español
            release_type_es = {
                'stable': 'Estable',
                'beta': 'Beta',
                'alpha': 'Alfa',
                'rc': 'Release Candidate'
            }.get(version_info['version']['release_type'].lower(), version_info['version']['release_type'])

            self._create_info_section(info_center, "Información del Proyecto", [
                ("Nombre Completo", version_info['project']['full_name']),
                ("Organización", version_info['project']['organization']),
                ("Versión", version_info['version']['version']),
                ("Nombre de Versión", version_info['version']['version_name']),
                ("Tipo de Release", release_type_es),
                ("Fecha de Build", version_info['version']['build_date']),
                ("Número de Build", version_info['version']['build_number'])
            ])
            
            # Tab 2: Sistema - Con scroll habilitado
            system_frame = ttk.Frame(notebook, padding=10)
            notebook.add(system_frame, text="💻 Sistema")

            # Crear canvas y scrollbar para permitir scroll
            system_canvas = tk.Canvas(system_frame, bg='#f0f0f0', highlightthickness=0)
            system_scrollbar = ttk.Scrollbar(system_frame, orient="vertical", command=system_canvas.yview)
            system_scrollable = ttk.Frame(system_canvas)

            system_scrollable.bind(
                "<Configure>",
                lambda e: system_canvas.configure(scrollregion=system_canvas.bbox("all"))
            )

            system_canvas.create_window((0, 0), window=system_scrollable, anchor="nw")
            system_canvas.configure(yscrollcommand=system_scrollbar.set)

            system_canvas.pack(side="left", fill="both", expand=True)
            system_scrollbar.pack(side="right", fill="y")

            # Configurar columnas para distribución 50/50
            system_scrollable.columnconfigure(0, weight=1)
            system_scrollable.columnconfigure(1, weight=1)

            # Variables para trackear filas
            left_row = 0
            right_row = 0

            # COLUMNA IZQUIERDA
            # Información básica del sistema
            basic_system_info = [
                ("Versión Python", version_info['system']['python_version'].split()[0]),
                ("Plataforma", version_info['system']['platform']),
                ("Sistema", version_info['system'].get('system', 'No disponible')),
                ("Release", version_info['system'].get('release', 'No disponible')),
                ("Arquitectura", version_info['system']['architecture']),
                ("Máquina", version_info['system'].get('machine', 'No disponible')),
                ("Nodo", version_info['system'].get('node', 'No disponible')),
                ("Procesador", version_info['system']['processor'] or "No disponible")
            ]
            self._create_info_section_grid(system_scrollable, "Información Básica", basic_system_info, row=left_row, column=0)
            left_row += 1

            # COLUMNA DERECHA
            # Información de memoria
            if 'memoria_total' in version_info['system']:
                memory_info = [
                    ("Memoria Total", version_info['system']['memoria_total']),
                    ("Memoria Disponible", version_info['system']['memoria_disponible']),
                    ("Memoria Usada", version_info['system']['memoria_usada']),
                    ("Porcentaje Usado", version_info['system']['memoria_porcentaje'])
                ]
                self._create_info_section_grid(system_scrollable, "Información de Memoria", memory_info, row=right_row, column=1)
                right_row += 1

            # Información de CPU
            if 'cpu_cores' in version_info['system']:
                cpu_info = [
                    ("Núcleos Físicos", str(version_info['system']['cpu_cores'])),
                    ("Hilos Lógicos", str(version_info['system']['cpu_threads'])),
                    ("Frecuencia Máxima", version_info['system']['cpu_frecuencia'])
                ]
                self._create_info_section_grid(system_scrollable, "Información del Procesador", cpu_info, row=right_row, column=1)
                right_row += 1

            # Información de hardware adicional
            hardware_info = []
            if 'tarjeta_grafica' in version_info['system']:
                gpus = version_info['system']['tarjeta_grafica']
                if isinstance(gpus, list):
                    for i, gpu in enumerate(gpus):
                        hardware_info.append((f"Tarjeta Gráfica {i+1}", gpu))
                else:
                    hardware_info.append(("Tarjeta Gráfica", str(gpus)))

            if 'placa_madre' in version_info['system']:
                hardware_info.append(("Placa Madre", version_info['system']['placa_madre']))

            if hardware_info:
                self._create_info_section_grid(system_scrollable, "Hardware", hardware_info, row=right_row, column=1)
                right_row += 1

            # Información de discos - ANCHO COMPLETO (debajo de ambas columnas)
            disk_row = max(left_row, right_row)  # Empezar después de la columna más larga
            if 'discos' in version_info['system'] and isinstance(version_info['system']['discos'], list):
                for i, disco in enumerate(version_info['system']['discos']):
                    if isinstance(disco, dict):
                        disk_info = [
                            ("Dispositivo", disco.get('dispositivo', 'No disponible')),
                            ("Punto de Montaje", disco.get('punto_montaje', 'No disponible')),
                            ("Sistema de Archivos", disco.get('sistema_archivos', 'No disponible')),
                            ("Espacio Total", disco.get('total', 'No disponible')),
                            ("Espacio Usado", disco.get('usado', 'No disponible')),
                            ("Espacio Libre", disco.get('libre', 'No disponible')),
                            ("Porcentaje Usado", disco.get('porcentaje', 'No disponible'))
                        ]
                        self._create_info_section_grid(system_scrollable, f"Disco {i+1}", disk_info, row=disk_row+i, column=0, columnspan=2)
            
            # Tab 3: Equipo de Desarrollo - Centrado, sin espacios en blanco
            team_frame = ttk.Frame(notebook, padding=20)
            notebook.add(team_frame, text="👥 Equipo")

            # Frame para centrar el contenido
            team_center = ttk.Frame(team_frame)
            team_center.pack(expand=True)
            
            # Información del equipo
            role_titles = {
                'desarrollador': '👨‍💻 Desarrollador',
                'lider_investigacion': '👨‍⚕️ Líder de Investigación y Proyección Oncológica',
                'jefe_gestion_informacion': '👨‍💼 Jefe de Gestión de la Información'
            }

            for role_key, role_info in version_info['team'].items():
                role_data = [
                    ("Nombre", role_info['nombre']),
                    ("Cargo", role_info['cargo']),
                    ("Departamento", role_info['departamento']),
                    ("Correo", role_info['correo'])
                ]
                title = role_titles.get(role_key, role_info['cargo'])
                self._create_info_section(team_center, title, role_data)

            # Frame de botones
            buttons_frame = ttk.Frame(main_frame, padding=10)
            buttons_frame.pack(fill=X, pady=10)

            # Botón dinámico que cambia según la pestaña
            copy_button = ttk.Button(
                buttons_frame,
                text="📋 Copiar Información",
                bootstyle="info"
            )
            copy_button.pack(side=LEFT, padx=(0, 10))

            # Función para actualizar el botón según la pestaña activa
            def update_copy_button():
                current_tab = notebook.index(notebook.select())
                if current_tab == 0:  # General
                    copy_button.configure(
                        text="📋 Copiar Info General",
                        command=lambda: self._copy_general_info(version_info),
                        state="normal"
                    )
                elif current_tab == 1:  # Sistema
                    copy_button.configure(
                        text="📋 Copiar Info Sistema",
                        command=lambda: self._copy_system_info(version_info),
                        state="normal"
                    )
                elif current_tab == 2:  # Equipo
                    # Ocultar el botón en la pestaña Equipo
                    copy_button.pack_forget()
                    return
                else:
                    copy_button.configure(state="disabled")

                # Asegurar que el botón esté visible si no es la pestaña Equipo
                if not copy_button.winfo_ismapped():
                    copy_button.pack(side=LEFT, padx=(0, 10))

            # Bind para actualizar cuando cambie de pestaña
            notebook.bind("<<NotebookTabChanged>>", lambda e: update_copy_button())

            # Inicializar el botón
            update_copy_button()

            ttk.Button(
                buttons_frame,
                text="✅ Cerrar",
                command=version_window.destroy,
                bootstyle="success"
            ).pack(side=RIGHT)
            
            # Habilitar scroll con la rueda del mouse en la pestaña Sistema
            def _on_mousewheel(event):
                try:
                    # Obtener el notebook tab actual
                    current_tab = notebook.index(notebook.select())

                    # Scroll solo en pestaña Sistema (tab 1)
                    if current_tab == 1:
                        system_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                except:
                    pass

            # Bind a la ventana completa
            version_window.bind_all("<MouseWheel>", _on_mousewheel)

            # Cleanup al cerrar
            def on_closing():
                try:
                    version_window.unbind_all("<MouseWheel>")
                except:
                    pass
                version_window.destroy()

            version_window.protocol("WM_DELETE_WINDOW", on_closing)
            
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error al mostrar información de versión:\n{str(e)}"
            )

    def _create_info_section(self, parent, title, info_items):
        """Crear una sección de información con título y elementos usando pack"""
        # Frame para la sección
        section_frame = ttk.LabelFrame(parent, text=title, padding=10)
        section_frame.pack(fill=X, pady=(0, 10))

        # Grid de información
        for i, (label, value) in enumerate(info_items):
            ttk.Label(
                section_frame,
                text=f"{label}:",
                font=("Arial", 9, "bold")
            ).grid(row=i, column=0, sticky=W, padx=(0, 10), pady=2)

            ttk.Label(
                section_frame,
                text=str(value),
                font=("Arial", 9)
            ).grid(row=i, column=1, sticky=W, pady=2)

    def _create_info_section_grid(self, parent, title, info_items, row=0, column=0, columnspan=1):
        """Crear una sección de información con título y elementos usando grid layout"""
        # Frame para la sección
        section_frame = ttk.LabelFrame(parent, text=title, padding=10)
        section_frame.grid(row=row, column=column, columnspan=columnspan, sticky=(N, S, E, W), padx=5, pady=5)

        # Grid de información dentro del frame
        for i, (label, value) in enumerate(info_items):
            ttk.Label(
                section_frame,
                text=f"{label}:",
                font=("Arial", 9, "bold")
            ).grid(row=i, column=0, sticky=W, padx=(0, 10), pady=2)

            ttk.Label(
                section_frame,
                text=str(value),
                font=("Arial", 9)
            ).grid(row=i, column=1, sticky=W, pady=2)
    
    def _copy_general_info(self, version_info):
        """Copiar información de la pestaña General al clipboard"""
        try:
            release_type_es = {
                'stable': 'Estable',
                'beta': 'Beta',
                'alpha': 'Alfa',
                'rc': 'Release Candidate'
            }.get(version_info['version']['release_type'].lower(), version_info['version']['release_type'])

            info_text = f"""EVARISIS CIRUGÍA ONCOLÓGICA - Información General
=====================================
Nombre Completo: {version_info['project']['full_name']}
Organización: {version_info['project']['organization']}
Versión: {version_info['version']['version']}
Nombre de Versión: {version_info['version']['version_name']}
Tipo de Release: {release_type_es}
Fecha de Build: {version_info['version']['build_date']}
Número de Build: {version_info['version']['build_number']}
"""

            self.clipboard_clear()
            self.clipboard_append(info_text)
            self.update()

            messagebox.showinfo("Copiado", "Información general copiada al portapapeles")

        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar:\n{str(e)}")

    def _copy_system_info(self, version_info):
        """Copiar información de la pestaña Sistema al clipboard"""
        try:
            info_text = f"""EVARISIS CIRUGÍA ONCOLÓGICA - Información del Sistema
=====================================
Versión Python: {version_info['system']['python_version'].split()[0]}
Plataforma: {version_info['system']['platform']}
Sistema: {version_info['system'].get('system', 'No disponible')}
Release: {version_info['system'].get('release', 'No disponible')}
Arquitectura: {version_info['system']['architecture']}
Máquina: {version_info['system'].get('machine', 'No disponible')}
Nodo: {version_info['system'].get('node', 'No disponible')}
Procesador: {version_info['system']['processor'] or 'No disponible'}
"""

            # Memoria
            if 'memoria_total' in version_info['system']:
                info_text += f"""
Memoria:
- Total: {version_info['system']['memoria_total']}
- Disponible: {version_info['system']['memoria_disponible']}
- Usada: {version_info['system']['memoria_usada']}
- Porcentaje Usado: {version_info['system']['memoria_porcentaje']}
"""

            # CPU
            if 'cpu_cores' in version_info['system']:
                info_text += f"""
Procesador:
- Núcleos Físicos: {version_info['system']['cpu_cores']}
- Hilos Lógicos: {version_info['system']['cpu_threads']}
- Frecuencia Máxima: {version_info['system']['cpu_frecuencia']}
"""

            # Discos
            if 'discos' in version_info['system']:
                info_text += "\nDiscos:\n"
                for i, disco in enumerate(version_info['system']['discos'], 1):
                    if isinstance(disco, dict):
                        info_text += f"""
Disco {i}:
- Dispositivo: {disco.get('dispositivo', 'No disponible')}
- Punto de Montaje: {disco.get('punto_montaje', 'No disponible')}
- Sistema de Archivos: {disco.get('sistema_archivos', 'No disponible')}
- Espacio Total: {disco.get('total', 'No disponible')}
- Espacio Usado: {disco.get('usado', 'No disponible')}
- Espacio Libre: {disco.get('libre', 'No disponible')}
- Porcentaje Usado: {disco.get('porcentaje', 'No disponible')}
"""

            self.clipboard_clear()
            self.clipboard_append(info_text)
            self.update()

            messagebox.showinfo("Copiado", "Información del sistema copiada al portapapeles")

        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar:\n{str(e)}")

    def _hide_header_if_not_welcome(self):
        """Ocultar header si no estamos en la pantalla de bienvenida"""
        if self.header_visible:
            self.header.pack_forget()
            self.header_separator.pack_forget()
            self.header_visible = False
            # Actualizar posición base del botón flotante sin header
            self.floating_btn_base_y = 20
            # Reposicionar inmediatamente el botón si existe
            if hasattr(self, 'floating_btn_container') and not self.floating_menu_visible:
                self.floating_btn_container.place(x=15, y=20, width=50, height=50)

    def _show_header(self):
        """Mostrar header (solo para pantalla de bienvenida)"""
        if not self.header_visible:
            self.header.pack(fill=X, before=self.content_container)
            self.header_separator.pack(fill=X, padx=20, pady=5, before=self.content_container)
            self.header_visible = True
            # Reajustar posición base del botón flotante con header visible
            self.floating_btn_base_y = 150
            # Reposicionar inmediatamente el botón
            if hasattr(self, 'floating_btn_container'):
                self.floating_btn_container.place(x=15, y=150, width=50, height=50)

    def _create_sidebar(self):
        """Crear la barra lateral de navegación"""
        # Header del sidebar elegante
        top = ttk.Frame(self.sidebar, padding=10)
        top.pack(fill=X)
        
        # Título del sidebar
        ttk.Label(
            top, 
            text="� NAVEGACIÓN", 
            font=("Segoe UI", 12, "bold"),
            anchor="center"
        ).pack(fill=X, pady=(0, 10))

        # Navegación
        nav = ttk.Frame(self.sidebar, padding=(10, 10))
        nav.pack(fill=BOTH, expand=True)

        self.nav_buttons = {}

        # Botones de navegación reorganizados
        nav_items = [
            ("🏠 Inicio", "home", "light", self.show_welcome_screen),
            ("🗄️ Base de Datos", "database", "primary", self.show_database_frame),
            ("📈 Análisis Gráfico", "dashboard", "info", self.show_dashboard_frame),
            ("🔗 Interoperabilidad QHORTE\n(Sistema de Entrega)", "web", "warning", self.open_web_auto_modal),
        ]

        for text, icon_key, style, callback in nav_items:
            btn = ttk.Button(
                nav, 
                text=text,
                image=self.iconos.get(icon_key),
                compound=LEFT,
                bootstyle=style,
                command=callback,
                width=20
            )
            btn.pack(fill=X, pady=2)
            self.nav_buttons[text] = btn

        # Botón de navegación (mostrar/ocultar menús)
        self.nav_toggle_btn = ttk.Button(
            nav, 
            text="◀ Ocultar Menús", 
            command=self._toggle_navigation_visibility, 
            bootstyle="secondary",
            width=20
        )
        self.nav_toggle_btn.pack(fill=X, pady=(20, 0))

        # Footer
        ttk.Label(
            self.sidebar, 
            text="HUV • EVARISIS", 
            anchor=CENTER, 
            padding=(10, 8), 
            bootstyle="light"
        ).pack(side=BOTTOM, fill=X)

    def _toggle_sidebar(self):
        """Alternar visibilidad de la sidebar"""
        target = 0 if self.sidebar_expanded else self.sidebar_width
        step = -24 if self.sidebar_expanded else 24

        def animate(curr):
            if (step > 0 and curr < target) or (step < 0 and curr > target):
                curr += step
                self.sidebar.configure(width=max(0, curr))
                self.after(10, lambda: animate(curr))
            else:
                self.sidebar.configure(width=target)
                self.sidebar_expanded = not self.sidebar_expanded

        current = self.sidebar.winfo_width() or (self.sidebar_width if self.sidebar_expanded else 0)
        animate(current)

    def _create_content_panels(self):
        """Crear los paneles de contenido principal con scroll"""
        # Panel de base de datos con scroll
        self.database_frame = self._create_scrollable_frame(self.content_container)
        self._create_database_content()

        # Panel de visualización con scroll
        self.visualizar_frame = self._create_scrollable_frame(self.content_container)
        self._create_visualizar_content()

        # Panel de análisis gráfico con scroll
        self.dashboard_frame = self._create_scrollable_frame(self.content_container)
        self._create_dashboard_content()

        # Panel de análisis IA con scroll
        self.analisis_ia_frame = self._create_scrollable_frame(self.content_container)
        self._crear_analisis_ia_content()

        # Panel activo actual
        self.panel_activo = None

    def _create_scrollable_frame(self, parent):
        """Crear un frame con barra de desplazamiento"""
        # Frame contenedor principal que llena toda el área
        container = ttk.Frame(parent, padding=0)
        
        # Canvas para scroll sin bordes ni highlight
        canvas = tk.Canvas(container, highlightthickness=0, borderwidth=0, relief='flat')
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=10)
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Hacer que el scrollable_frame se expanda horizontalmente en el canvas
        def _configure_canvas(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Hacer que el frame interno sea del mismo ancho que el canvas
            canvas_width = event.width
            canvas.itemconfig(window_id, width=canvas_width)
            # Auto-mostrar/ocultar scrollbar según si el contenido excede el canvas
            _update_scrollbar_visibility()
        
        def _update_scrollbar_visibility():
            """Mostrar scrollbar solo cuando el contenido excede el área visible"""
            try:
                canvas.update_idletasks()
                bbox = canvas.bbox("all")
                if bbox:
                    content_height = bbox[3] - bbox[1]
                    canvas_height = canvas.winfo_height()
                    if content_height > canvas_height:
                        if not scrollbar.winfo_ismapped():
                            scrollbar.pack(side="right", fill="y")
                    else:
                        if scrollbar.winfo_ismapped():
                            scrollbar.pack_forget()
            except Exception:
                pass
        
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.bind('<Configure>', _configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Variable para trackear el último widget con focus para scroll anidado
        container.last_scroll_target = None

        # Scroll con rueda del mouse mejorado - maneja scroll anidado
        def _on_mousewheel(event):
            # Obtener el widget bajo el cursor
            widget = event.widget

            # Buscar si el widget o algún padre tiene un canvas con scroll
            current = widget
            scrollable_canvas = None

            while current and current != container:
                if hasattr(current, 'master') and isinstance(current.master, tk.Canvas):
                    # Este widget está dentro de un canvas scrollable
                    scrollable_canvas = current.master
                    break
                current = current.master if hasattr(current, 'master') else None

            # Si encontramos un canvas scrollable anidado, hacer scroll en ese
            if scrollable_canvas and scrollable_canvas != canvas:
                try:
                    scrollable_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                    return "break"
                except:
                    pass

            # Si no, hacer scroll en el canvas principal
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"

        # Vincular el evento al canvas específico
        canvas.bind("<MouseWheel>", _on_mousewheel)

        # También vincular a todos los widgets hijos del scrollable_frame
        def _bind_to_mousewheel(widget):
            # No vincular scroll a widgets que ya manejan su propio scroll
            widget_type = widget.winfo_class()
            if widget_type not in ['Listbox', 'Treeview', 'Text']:
                widget.bind("<MouseWheel>", _on_mousewheel)

            for child in widget.winfo_children():
                _bind_to_mousewheel(child)
        
        # Empacar elementos para llenar toda el área
        canvas.pack(side="left", fill="both", expand=True)
        # scrollbar se muestra/oculta automáticamente según contenido
        
        # Aplicar el binding del scroll a todos los widgets después de un pequeño delay
        # para asegurar que todos los widgets hijos se han creado
        def _apply_scroll_binding():
            try:
                _bind_to_mousewheel(scrollable_frame)
            except:
                pass  # Si hay error, continuamos sin problemas
        
        container.after(100, _apply_scroll_binding)
        
        # Guardar referencias para uso posterior
        container.scrollable_frame = scrollable_frame
        container.canvas = canvas
        container._bind_to_mousewheel = _bind_to_mousewheel  # Guardar función para uso posterior
        
        return container

    def _create_database_content(self):
        """Crear contenido del panel de base de datos con dashboard mejorado de ancho completo"""
        # Usar el frame scrollable
        frame = self.database_frame.scrollable_frame

        # ELIMINADO: Título duplicado (el dashboard ya tiene su propio título)
        # ttk.Label(
        #     frame,
        #     text="🏥 Dashboard Base de Datos EVARISIS CIRUGÍA ONCOLÓGICA",
        #     font=self.FONT_TITULO
        # ).pack(pady=(0, 20), anchor=W)

        # Dashboard mejorado que usa todo el ancho disponible
        dashboard_container = ttk.Frame(frame, padding=0)
        dashboard_container.pack(expand=True, fill=BOTH)

        # Crear dashboard mejorado con funcionalidad de importación integrada
        try:
            from core.enhanced_database_dashboard import EnhancedDatabaseDashboard
            self.enhanced_dashboard = EnhancedDatabaseDashboard(dashboard_container)

            # Conectar métodos de importación del dashboard con la UI principal
            self._connect_import_functionality()

            # Poblar la pestaña de visualizador en el dashboard
            self._populate_visualizar_tab_in_dashboard()

        except ImportError as e:
            # Fallback en caso de error
            ttk.Label(
                dashboard_container,
                text=f"Error: No se pudo cargar el dashboard mejorado: {e}",
                font=("Segoe UI", 12)
            ).pack(pady=50)

    def _connect_import_functionality(self):
        """Conectar la funcionalidad de importación del dashboard con los métodos de la UI principal"""
        if hasattr(self, 'enhanced_dashboard'):
            # Conectar los métodos de importación
            dashboard = self.enhanced_dashboard

            # Reasignar los métodos del dashboard a los de la UI principal
            dashboard.select_pdf_file = self._select_pdf_file
            dashboard.select_pdf_folder = self._select_pdf_folder
            dashboard.process_selected_files = self._process_selected_files

            # Crear referencia al listbox del dashboard para que los métodos antiguos funcionen
            if hasattr(dashboard, 'import_files_listbox'):
                self.files_listbox = dashboard.import_files_listbox
                dashboard.refresh_files_list = self._refresh_files_list

                # Actualizar la lista de archivos después de conectar
                try:
                    self._refresh_files_list()
                except Exception as e:
                    logging.error(f"Error al actualizar lista de archivos inicial: {e}")

            # v6.0.12: Cargar datos del dashboard inmediatamente al inicializar
            try:
                dashboard.refresh_all_data()
                logging.info("✅ Dashboard inicializado con datos de la base de datos")
            except Exception as e:
                logging.error(f"❌ Error al cargar datos iniciales del dashboard: {e}")
                logging.error(f"Traceback: {traceback.format_exc()}")

    def _populate_visualizar_tab_in_dashboard(self):
        """Poblar la pestaña de visualizador en el dashboard con el contenido completo IGUAL al visualizador original"""
        if not hasattr(self, 'enhanced_dashboard'):
            return

        dashboard = self.enhanced_dashboard

        # Verificar que existe el tab
        if not hasattr(dashboard, 'visualizar_tab'):
            logging.warning("Dashboard no tiene visualizar_tab")
            return

        # Usar el visualizar_tab directamente como frame
        frame = dashboard.visualizar_tab

        # Limpiar todo el contenido previo
        for widget in frame.winfo_children():
            widget.destroy()

        # ===== CREAR EL MISMO CONTENIDO QUE _create_visualizar_content() =====

        # Título principal compacto
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=X, padx=10, pady=5)

        ttk.Label(
            title_frame,
            text="📊 Visualizador de Datos",
            font=self.FONT_TITULO
        ).pack(side=LEFT)

        # Botones de acción en el header
        actions_frame = ttk.Frame(title_frame)
        actions_frame.pack(side=RIGHT)

        # Botón de filtros avanzados
        self.filter_btn_dashboard = ttk.Button(
            actions_frame,
            text="🔍 Filtros",
            command=self._toggle_advanced_filters,
            bootstyle="info"
        )
        self.filter_btn_dashboard.pack(side=RIGHT, padx=(0, 5))

        # Botón de detalles flotante
        self.details_btn_dashboard = ttk.Button(
            actions_frame,
            text="📋 Detalles",
            command=self._toggle_details_panel,
            bootstyle="secondary"
        )
        self.details_btn_dashboard.pack(side=RIGHT, padx=(0, 5))

        # Botón exportar selección (inicialmente deshabilitado)
        self.export_selection_btn_dashboard = ttk.Button(
            actions_frame,
            text="📤 Exportar Selección",
            command=self._export_selected_data,
            bootstyle="success",
            state="disabled"
        )
        self.export_selection_btn_dashboard.pack(side=RIGHT, padx=(0, 5))

        # Botón exportar toda la base de datos
        ttk.Button(
            actions_frame,
            text="💾 Exportar Todo",
            command=self._export_full_database,
            bootstyle="warning"
        ).pack(side=RIGHT, padx=(0, 5))

        # Botón Resumen IA
        ttk.Button(
            actions_frame,
            text="📊 Resumen IA",
            command=self._generar_resumen_ia,
            bootstyle="dark"
        ).pack(side=RIGHT, padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="🔄 Actualizar Datos",
            command=self.refresh_data_and_table,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=(0, 5))

        # V3.2.4: Botones de auditoría IA
        self.audit_parcial_btn_dashboard = ttk.Button(
            actions_frame,
            text="🔍 Auditoría PARCIAL",
            command=self._auditar_seleccion_parcial,
            bootstyle="info-outline",
            state="disabled"
        )
        self.audit_parcial_btn_dashboard.pack(side=RIGHT, padx=(0, 5))

        self.audit_completa_btn_dashboard = ttk.Button(
            actions_frame,
            text="✅ Auditoría COMPLETA",
            command=self._auditar_seleccion_completa,
            bootstyle="success-outline",
            state="disabled"
        )
        self.audit_completa_btn_dashboard.pack(side=RIGHT, padx=(0, 5))

        # Frame para tabla - FULL SCREEN
        table_frame = ttk.Frame(frame)
        table_frame.pack(expand=True, fill=BOTH, padx=10, pady=5)
        table_frame.grid_rowconfigure(1, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Campo de búsqueda
        self._search_placeholder = "Buscar por N° Petición, Nombre o Apellido..."
        self.search_var_dashboard = tk.StringVar()
        self.search_var_dashboard.trace_add("write", self.filter_tabla)
        self._search_entry_dashboard = ttk.Entry(
            table_frame,
            textvariable=self.search_var_dashboard,
            font=("Segoe UI", 11)
        )
        self._search_entry_dashboard.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._search_entry_dashboard.insert(0, self._search_placeholder)
        self._search_entry_dashboard.bind("<FocusIn>", lambda e: self._on_search_focus_in(self._search_entry_dashboard, self.search_var_dashboard))
        self._search_entry_dashboard.bind("<FocusOut>", lambda e: self._on_search_focus_out(self._search_entry_dashboard, self.search_var_dashboard))

        # Crear Sheet en el dashboard (compartiremos la misma instancia para sincronización)
        # IMPORTANTE: Usamos self.sheet para que sea la MISMA instancia que el visualizador original
        from tksheet import Sheet

        self.sheet_dashboard = Sheet(
            table_frame,
            page_up_down_select_row=True,
            expand_sheet_if_paste_too_big=False,
            column_width=150,
            startup_select=(0, 0, "rows"),
            headers_height=30,
            default_row_height=25,
            show_horizontal_grid=True,
            show_vertical_grid=True,
            show_top_left=False,
            show_row_index=True,
            show_header=True,
            empty_horizontal=0,
            empty_vertical=0,
            header_font=("Segoe UI", 10, "bold"),
            font=("Segoe UI", 10, "normal"),
            header_bg="#E8F5E9",
            header_fg="#1B5E20",
            table_bg="white",
            table_fg="black",
            table_selected_cells_bg="#BBDEFB",
            table_selected_cells_fg="black",
            table_selected_rows_bg="#E3F2FD",
            table_selected_rows_fg="black",
            top_left_bg="#E8F5E9",
            index_bg="#F5F5F5",
            index_fg="#424242",
            index_selected_cells_bg="#CFD8DC",
            index_selected_rows_bg="#B0BEC5"
        )
        self.sheet_dashboard.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        # Habilitar funcionalidades tipo Excel
        self.sheet_dashboard.enable_bindings(
            "all", "copy", "row_select", "column_select", "drag_select",
            "select_all", "rc_select", "arrowkeys", "single_select", "drag_and_drop", "move_columns"
        )

        # Deshabilitar edición
        self.sheet_dashboard.disable_bindings(
            "edit_cell", "cut", "paste", "delete", "undo",
            "column_width_resize", "double_click_column_resize",
            "row_width_resize", "column_height_resize"
        )

        # Evento de selección
        self.sheet_dashboard.bind("<<SheetSelect>>", self.mostrar_detalle_registro)

        # Agregar métodos de compatibilidad Treeview → Sheet
        def _sheet_selection_dashboard():
            try:
                rows = set()
                selected_rows = self.sheet_dashboard.get_selected_rows()
                if selected_rows:
                    rows.update(selected_rows)
                selected_cells = self.sheet_dashboard.get_selected_cells()
                if selected_cells:
                    rows.update([cell[0] for cell in selected_cells])
                return list(rows)
            except Exception as e:
                logging.error(f"Error en _sheet_selection_dashboard: {e}")
                return []

        self.sheet_dashboard.selection = _sheet_selection_dashboard

        # Marcar que el dashboard tiene sheet
        dashboard.has_sheet = True
        dashboard.sheet_dashboard = self.sheet_dashboard

        # Cargar datos iniciales
        self.refresh_data_and_table()

        logging.info("✅ Pestaña de visualizador COMPLETA poblada en el dashboard con tabla Sheet")

    def _refresh_files_list_for_dashboard(self):
        """Actualizar lista de archivos específicamente para el dashboard con detección de estado"""
        if hasattr(self, 'enhanced_dashboard') and hasattr(self.enhanced_dashboard, 'import_files_listbox'):
            # Usar la nueva función de actualización con estado
            self.files_listbox = self.enhanced_dashboard.import_files_listbox
            self._actualizar_lista_archivos_con_estado()

    def _create_visualizar_content(self):
        """Crear contenido del panel de visualización mejorado - FULL SCREEN"""
        # Usar el frame principal directamente (sin scroll externo)
        frame = self.visualizar_frame

        # Limpiar cualquier contenido previo
        for widget in frame.winfo_children():
            widget.destroy()

        # Título principal compacto
        title_frame = ttk.Frame(frame)
        title_frame.pack(fill=X, padx=10, pady=5)

        ttk.Label(
            title_frame,
            text="📊 Visualizador de Datos",
            font=self.FONT_TITULO
        ).pack(side=LEFT)

        # Botones de acción en el header
        actions_frame = ttk.Frame(title_frame)
        actions_frame.pack(side=RIGHT)

        # Botón de filtros avanzados
        self.filter_btn = ttk.Button(
            actions_frame,
            text="🔍 Filtros",
            command=self._toggle_advanced_filters,
            bootstyle="info"
        )
        self.filter_btn.pack(side=RIGHT, padx=(0, 5))

        # Botón de detalles flotante
        self.details_btn = ttk.Button(
            actions_frame,
            text="📋 Detalles",
            command=self._toggle_details_panel,
            bootstyle="secondary"
        )
        self.details_btn.pack(side=RIGHT, padx=(0, 5))

        # Botón exportar selección (inicialmente deshabilitado)
        self.export_selection_btn = ttk.Button(
            actions_frame,
            text="📤 Exportar Selección",
            command=self._export_selected_data,
            bootstyle="success",
            state="disabled"
        )
        self.export_selection_btn.pack(side=RIGHT, padx=(0, 5))

        # Botón exportar toda la base de datos
        ttk.Button(
            actions_frame,
            text="💾 Exportar Todo",
            command=self._export_full_database,
            bootstyle="warning"
        ).pack(side=RIGHT, padx=(0, 5))

        # Botón Resumen IA
        ttk.Button(
            actions_frame,
            text="📊 Resumen IA",
            command=self._generar_resumen_ia,
            bootstyle="dark"
        ).pack(side=RIGHT, padx=(0, 5))

        ttk.Button(
            actions_frame,
            text="🔄 Actualizar Datos",
            command=self.refresh_data_and_table,
            bootstyle="primary"
        ).pack(side=RIGHT, padx=(0, 5))

        # V3.2.4: Botones de auditoría IA
        self.audit_parcial_btn = ttk.Button(
            actions_frame,
            text="🔍 Auditoría PARCIAL",
            command=self._auditar_seleccion_parcial,
            bootstyle="info-outline",
            state="disabled"
        )
        self.audit_parcial_btn.pack(side=RIGHT, padx=(0, 5))

        self.audit_completa_btn = ttk.Button(
            actions_frame,
            text="✅ Auditoría COMPLETA",
            command=self._auditar_seleccion_completa,
            bootstyle="success-outline",
            state="disabled"
        )
        self.audit_completa_btn.pack(side=RIGHT, padx=(0, 5))

        # Frame para tabla - FULL SCREEN
        table_frame = ttk.Frame(frame)
        table_frame.pack(expand=True, fill=BOTH, padx=10, pady=5)
        table_frame.grid_rowconfigure(1, weight=1)  # Treeview
        table_frame.grid_columnconfigure(0, weight=1)

        # Campo de búsqueda
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_tabla)
        self._search_entry = ttk.Entry(
            table_frame,
            textvariable=self.search_var,
            font=("Segoe UI", 11)
        )
        self._search_entry.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self._search_entry.insert(0, self._search_placeholder)
        self._search_entry.bind("<FocusIn>", lambda e: self._on_search_focus_in(self._search_entry, self.search_var))
        self._search_entry.bind("<FocusOut>", lambda e: self._on_search_focus_out(self._search_entry, self.search_var))

        # V5.3.8: Sheet virtualizado tipo Excel (reemplaza Treeview)
        # VENTAJAS: Virtualización nativa, rendimiento profesional, comportamiento Excel

        # Crear Sheet con scrollbars integrados
        self.sheet = Sheet(
            table_frame,
            page_up_down_select_row=True,
            expand_sheet_if_paste_too_big=False,
            column_width=150,
            startup_select=None,  # No auto-seleccionar fila 0
            headers_height=30,
            default_row_height=25,
            show_horizontal_grid=True,
            show_vertical_grid=True,
            show_top_left=False,
            show_row_index=True,
            show_header=True,
            empty_horizontal=0,
            empty_vertical=0,
            header_font=("Segoe UI", 10, "bold"),
            font=("Segoe UI", 10, "normal"),  # FIX: Agregar estilo "normal" (3 elementos)
            header_bg="#E8F5E9",  # Verde muy claro (profesional)
            header_fg="#1B5E20",  # Verde oscuro
            table_bg="white",
            table_fg="black",
            table_selected_cells_bg="#BBDEFB",  # Azul claro
            table_selected_cells_fg="black",
            table_selected_rows_bg="#E3F2FD",  # Azul muy claro
            table_selected_rows_fg="black",
            top_left_bg="#E8F5E9",
            index_bg="#F5F5F5",
            index_fg="#424242",
            index_selected_cells_bg="#CFD8DC",
            index_selected_rows_bg="#B0BEC5"
        )
        self.sheet.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0, 10))

        # Habilitar funcionalidades tipo Excel (NO usar "all" para evitar single_select)
        self.sheet.enable_bindings(
            "copy",  # Ctrl+C
            "row_select",  # Selección de filas
            "column_select",  # Selección de columnas
            "drag_select",  # Arrastrar para seleccionar
            "select_all",  # Ctrl+A
            "rc_select",  # Click derecho
            "arrowkeys",  # Navegación con flechas
            "toggle_select",  # Ctrl+Click / Shift+Click para multi-selección
        )

        # Evento de selección
        self.sheet.bind("<<SheetSelect>>", self.mostrar_detalle_registro)
        # IMPORTANTE: También enlazar a ButtonRelease para capturar clicks que no disparen <<SheetSelect>>
        self.sheet.bind("<ButtonRelease-1>", self.mostrar_detalle_registro, add="+")
        # Y navegación con teclado
        self.sheet.bind("<KeyRelease-Up>", self.mostrar_detalle_registro, add="+")
        self.sheet.bind("<KeyRelease-Down>", self.mostrar_detalle_registro, add="+")
        self.sheet.bind("<KeyRelease-Left>", self.mostrar_detalle_registro, add="+")
        self.sheet.bind("<KeyRelease-Right>", self.mostrar_detalle_registro, add="+")

        # Binding permanente para ordenamiento por click en encabezado
        # IMPORTANTE: Se bindea UNA SOLA VEZ aquí (no en _populate_treeview)
        def _on_header_click(event):
            """Callback cuando se hace clic en un encabezado para ordenar columna"""
            import logging

            # Validación robusta: verificar que el evento tenga atributo 'region'
            if not hasattr(event, 'region'):
                logging.debug("_on_header_click: event sin atributo 'region', ignorando")
                return

            if event.region != "header":
                logging.debug(f"_on_header_click: region='{event.region}' (no es header), ignorando")
                return

            # Procesar click en encabezado para ordenar
            col_idx = event.column
            if col_idx is not None and hasattr(self, 'master_df') and not self.master_df.empty:
                # Obtener DataFrame actual (puede estar filtrado)
                df_display = self.master_df

                if col_idx < len(df_display.columns):
                    col_name = df_display.columns[col_idx]

                    # Alternar orden ascendente/descendente
                    if not hasattr(self, '_last_sorted_col') or self._last_sorted_col != col_name:
                        self._last_sorted_col = col_name
                        self._last_sorted_reverse = False
                    else:
                        self._last_sorted_reverse = not self._last_sorted_reverse

                    logging.info(f"Ordenando por columna '{col_name}' (reverso={self._last_sorted_reverse})")
                    self._sort_treeview(col_name, self._last_sorted_reverse)

        # Bindear el handler (add="+" para no reemplazar handlers existentes)
        self.sheet.bind("<ButtonRelease-1>", _on_header_click, add="+")
        logging.info("Handler de ordenamiento por encabezado bindeado correctamente")

        # V5.3.8: CAPA DE COMPATIBILIDAD TREEVIEW → SHEET
        # =================================================
        # Agregar métodos a Sheet para que se comporte como Treeview

        def _sheet_selection():
            """Emula tree.selection() - Retorna lista de índices de filas seleccionadas

            v6.0.15: Lee selection_boxes del Sheet + fallback a últimas filas guardadas.
            Cuando el usuario hace clic en un botón, el Sheet pierde selección interna,
            así que usamos self._ultimas_filas_seleccionadas como caché confiable.
            """
            try:
                rows = set()

                # ESTRATEGIA 1: Leer selection_boxes directamente del Sheet
                # Esto captura rangos de celdas/filas seleccionadas
                try:
                    boxes = self.sheet.get_all_selection_boxes()
                    if boxes:
                        for box in boxes:
                            # box es (from_r, from_c, upto_r, upto_c)
                            if len(box) >= 4:
                                from_r, _, upto_r, _ = box[0], box[1], box[2], box[3]
                                for r in range(from_r, upto_r):
                                    rows.add(r)
                        if rows:
                            logging.info(f"_sheet_selection: Estrategia 1 (selection_boxes): {sorted(rows)}")
                except Exception:
                    pass

                # ESTRATEGIA 2: get_selected_rows y get_selected_cells
                if not rows:
                    selected_rows = self.sheet.get_selected_rows()
                    if selected_rows:
                        rows.update(selected_rows)
                    selected_cells = self.sheet.get_selected_cells()
                    if selected_cells:
                        rows.update(row for row, col in selected_cells)
                    if rows:
                        logging.info(f"_sheet_selection: Estrategia 2 (rows/cells): {sorted(rows)}")

                # ESTRATEGIA 3: get_currently_selected
                if not rows:
                    selected = self.sheet.get_currently_selected()
                    if selected and hasattr(selected, 'row') and selected.row is not None:
                        rows.add(selected.row)
                        logging.info(f"_sheet_selection: Estrategia 3 (currently_selected): fila {selected.row}")

                # ESTRATEGIA 4: Fallback a últimas filas guardadas (crucial para multi-selección)
                # Cuando el usuario hace clic en un botón, el Sheet pierde la selección
                if not rows and hasattr(self, '_ultimas_filas_seleccionadas') and self._ultimas_filas_seleccionadas:
                    rows.update(self._ultimas_filas_seleccionadas)
                    logging.info(f"_sheet_selection: Estrategia 4 (caché): {sorted(rows)}")

                # Actualizar caché si obtuvimos filas por estrategias 1-3
                if rows and not (not rows and hasattr(self, '_ultimas_filas_seleccionadas')):
                    self._ultimas_filas_seleccionadas = list(rows)

                if rows:
                    result = sorted(rows)
                    logging.info(f"_sheet_selection: ✅ RETORNANDO {len(result)} fila(s): {result}")
                    return result
                else:
                    logging.info("_sheet_selection: ⚠️ Sin selección, retornando []")
                    return []

            except Exception as e:
                logging.error(f"_sheet_selection: Error obteniendo selección: {e}", exc_info=True)
                return []

        def _sheet_item(row_idx, option=None):
            """Emula tree.item(item_id, option) - Retorna datos de la fila"""
            if option == 'values' or option is None:
                try:
                    row_data = self.sheet.get_row_data(row_idx, return_copy=True)
                    return {'values': row_data} if option is None else row_data
                except:
                    return {'values': []} if option is None else []
            return {}

        def _sheet_get_children(item=""):
            """Emula tree.get_children() - Retorna lista de todos los índices de filas"""
            total_rows = self.sheet.get_total_rows()
            return list(range(total_rows))

        def _sheet_index(item_id):
            """Emula tree.index(item_id) - Retorna el índice de la fila"""
            return item_id  # En Sheet, item_id YA ES el índice

        # Agregar métodos de compatibilidad al objeto sheet
        self.sheet.selection = _sheet_selection
        self.sheet.item = _sheet_item
        self.sheet.get_children = _sheet_get_children
        self.sheet.index = _sheet_index

        # COMPATIBILIDAD: Mantener alias 'tree' para código legacy
        self.tree = self.sheet  # Ahora funciona como Treeview

        # NUEVO: Agregar tooltips al pasar mouse sobre celdas
        self._setup_cell_tooltips()

        # Habilitar/deshabilitar botones según selección (V3.2.4: incluye botones de auditoría)
        # v6.0.12: SIMPLIFICADO - Delegar a métodos de clase
        def _update_selection_buttons(event=None):
            logging.debug(f"_update_selection_buttons: Llamado con evento={event}")
            # Llamar a métodos de clase que contienen toda la lógica
            self._update_export_button_state()
            self._update_audit_buttons_state()

        # v6.0.12: CORREGIDO - Sheet NO emite <<TreeviewSelect>>, usar eventos nativos de Sheet
        # IMPORTANTE: Usar add="+" para NO reemplazar el bind existente de mostrar_detalle_registro
        self.sheet.bind("<<SheetSelect>>", _update_selection_buttons, add="+")  # Evento nativo de tksheet
        self.sheet.bind("<ButtonRelease-1>", _update_selection_buttons, add="+")  # Click del mouse
        self.sheet.bind("<KeyRelease-Up>", _update_selection_buttons, add="+")  # Navegación con flechas
        self.sheet.bind("<KeyRelease-Down>", _update_selection_buttons, add="+")  # Navegación con flechas

        logging.info("Eventos de selección bindeados correctamente a Sheet")

        # Cargar datos automáticamente al inicializar el visualizador
        self.after(100, lambda: self.refresh_data_and_table() if hasattr(self, 'refresh_data_and_table') else None)

        # El panel de detalles ahora será flotante (se crea en demanda)

    def _create_dashboard_content(self):
        """Crear contenido del panel de dashboard"""
        # Usar el frame scrollable
        frame = self.dashboard_frame.scrollable_frame
        
        # Título principal actualizado
        ttk.Label(frame, text="📈 Análisis Gráfico de la Base de Datos", font=self.FONT_TITULO).pack(pady=(0, 10), anchor=W)
        
        # Container principal
        main_container = ttk.Frame(frame)
        main_container.pack(expand=True, fill=BOTH)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=0)  # sidebar
        main_container.grid_columnconfigure(1, weight=1)  # main area

        # Sidebar de filtros (inicialmente oculto)
        self.db_filters = {
            "fecha_desde": tk.StringVar(value=""),
            "fecha_hasta": tk.StringVar(value=""),
            "servicio": tk.StringVar(value=""),
            "malignidad": tk.StringVar(value=""),
            "responsable": tk.StringVar(value=""),
        }
        self.db_sidebar_collapsed = True
        self.db_sidebar = ttk.Frame(main_container, padding=15, width=280)
        
        # Título del sidebar de filtros
        ttk.Label(self.db_sidebar, text="Filtros", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 10))
        
        # Campos de filtros
        ttk.Label(self.db_sidebar, text="Fecha desde (dd/mm/aaaa)").grid(row=1, column=0, sticky="w", pady=(5, 2))
        ttk.Entry(self.db_sidebar, textvariable=self.db_filters["fecha_desde"]).grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(self.db_sidebar, text="Fecha hasta (dd/mm/aaaa)").grid(row=3, column=0, sticky="w", pady=(5, 2))
        ttk.Entry(self.db_sidebar, textvariable=self.db_filters["fecha_hasta"]).grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(self.db_sidebar, text="Servicio").grid(row=5, column=0, sticky="w", pady=(5, 2))
        self.cmb_servicio = ttk.Combobox(self.db_sidebar, textvariable=self.db_filters["servicio"], values=[])
        self.cmb_servicio.grid(row=6, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(self.db_sidebar, text="Malignidad").grid(row=7, column=0, sticky="w", pady=(5, 2))
        self.cmb_malig = ttk.Combobox(self.db_sidebar, textvariable=self.db_filters["malignidad"], values=["", "PRESENTE", "AUSENTE"])
        self.cmb_malig.grid(row=8, column=0, sticky="ew", pady=(0, 10))
        
        ttk.Label(self.db_sidebar, text="Responsable").grid(row=9, column=0, sticky="w", pady=(5, 2))
        self.cmb_resp = ttk.Combobox(self.db_sidebar, textvariable=self.db_filters["responsable"], values=[])
        self.cmb_resp.grid(row=10, column=0, sticky="ew", pady=(0, 10))
        
        # Botones del sidebar
        btns_frame = ttk.Frame(self.db_sidebar)
        btns_frame.grid(row=11, column=0, sticky="ew", pady=(10, 0))
        btns_frame.grid_columnconfigure(0, weight=1)
        btns_frame.grid_columnconfigure(1, weight=1)
        
        ttk.Button(btns_frame, text="Refrescar", command=self._refresh_dashboard).grid(row=0, column=0, sticky="ew", padx=(0, 5))
        ttk.Button(btns_frame, text="Limpiar", command=self._clear_filters).grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Configurar grid del sidebar
        self.db_sidebar.grid_columnconfigure(0, weight=1)

        # Área principal con toolbar + notebook
        main_area = ttk.Frame(main_container)
        main_area.grid(row=0, column=1, sticky="nsew")
        main_area.grid_rowconfigure(1, weight=1)
        main_area.grid_columnconfigure(0, weight=1)

        # Toolbar superior
        toolbar = ttk.Frame(main_area, padding=(5, 5))
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        self.btn_toggle_sidebar = ttk.Button(toolbar, text="≡ Mostrar filtros", command=self._toggle_db_sidebar)
        self.btn_toggle_sidebar.pack(side=LEFT, padx=(0, 10))
        
        ttk.Button(toolbar, text="Filtros…", command=self._open_filters_sheet).pack(side=LEFT)

        # Notebook con las pestañas del dashboard
        self.tabs = ttk.Notebook(main_area)
        self.tabs.grid(row=1, column=0, sticky="nsew")

        # Crear las pestañas con scroll
        self.tab_overview   = ttk.Frame(self.tabs)
        self.tab_biomarkers = ttk.Frame(self.tabs)
        self.tab_times      = ttk.Frame(self.tabs)
        self.tab_quality    = ttk.Frame(self.tabs)
        self.tab_compare    = ttk.Frame(self.tabs)

        # Configurar cada pestaña para ser responsive con grid 2x2
        for tab in [self.tab_overview, self.tab_biomarkers, self.tab_times, self.tab_quality, self.tab_compare]:
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_columnconfigure(1, weight=1)
            tab.grid_rowconfigure(0, weight=1)
            tab.grid_rowconfigure(1, weight=1)

        self.tabs.add(self.tab_overview,   text="Overview")
        self.tabs.add(self.tab_biomarkers, text="Biomarcadores")
        self.tabs.add(self.tab_times,      text="Tiempos")
        self.tabs.add(self.tab_quality,    text="Calidad")
        self.tabs.add(self.tab_compare,    text="Comparador")

        self._dash_canvases = []

    def _crear_analisis_ia_content(self):
        """Crear contenido completo de la sección de Análisis IA"""
        # Usar el frame scrollable
        frame = self.analisis_ia_frame.scrollable_frame

        # Variables de instancia
        self.tipo_reporte_var = tk.StringVar(value="parcial")
        self.reporte_seleccionado = None

        # HEADER
        header_frame = ttk.Frame(frame, bootstyle="primary", padding=15)
        header_frame.pack(fill=X, pady=(0, 20))

        ttk.Label(
            header_frame,
            text="🤖 EVARISIS CIRUGÍA ONCOLÓGICA - Análisis con IA",
            font=("Arial", 20, "bold"),
            bootstyle="inverse-primary"
        ).pack()

        # PANEL SELECTOR DE TIPO DE REPORTE
        selector_frame = ttk.LabelFrame(frame, text="Tipo de Reporte", padding=15, bootstyle="info")
        selector_frame.pack(fill=X, pady=(0, 10))

        radio_frame = ttk.Frame(selector_frame)
        radio_frame.pack(fill=X)

        ttk.Radiobutton(
            radio_frame,
            text="Análisis Parcial",
            variable=self.tipo_reporte_var,
            value="parcial",
            command=self._actualizar_lista_reportes,
            bootstyle="info"
        ).pack(side=LEFT, padx=10)

        ttk.Radiobutton(
            radio_frame,
            text="Análisis Completo",
            variable=self.tipo_reporte_var,
            value="completo",
            command=self._actualizar_lista_reportes,
            bootstyle="info"
        ).pack(side=LEFT, padx=10)

        # LISTA DE REPORTES DISPONIBLES
        reportes_frame = ttk.LabelFrame(frame, text="Reportes Disponibles", padding=15, bootstyle="success")
        reportes_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Treeview con scrollbar
        tree_container = ttk.Frame(reportes_frame)
        tree_container.pack(fill=BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.reportes_tree = ttk.Treeview(
            tree_container,
            columns=("Fecha", "Tipo", "Casos", "Archivo"),
            show="headings",
            yscrollcommand=scrollbar.set,
            bootstyle="success"
        )
        scrollbar.config(command=self.reportes_tree.yview)

        # Configurar columnas
        self.reportes_tree.heading("Fecha", text="Fecha")
        self.reportes_tree.heading("Tipo", text="Tipo")
        self.reportes_tree.heading("Casos", text="Casos")
        self.reportes_tree.heading("Archivo", text="Archivo")

        self.reportes_tree.column("Fecha", width=150, anchor=W)
        self.reportes_tree.column("Tipo", width=120, anchor=CENTER)
        self.reportes_tree.column("Casos", width=200, anchor=W)
        self.reportes_tree.column("Archivo", width=400, anchor=W)

        self.reportes_tree.pack(fill=BOTH, expand=True)

        # Bind de selección
        self.reportes_tree.bind("<<TreeviewSelect>>", self._cargar_reporte_seleccionado)

        # VISUALIZADOR MARKDOWN
        visualizador_frame = ttk.LabelFrame(frame, text="Contenido del Reporte", padding=15, bootstyle="warning")
        visualizador_frame.pack(fill=BOTH, expand=True, pady=(0, 10))

        # Frame para el text widget con scrollbar
        text_container = ttk.Frame(visualizador_frame)
        text_container.pack(fill=BOTH, expand=True)

        text_scrollbar = ttk.Scrollbar(text_container, orient="vertical")
        text_scrollbar.pack(side=RIGHT, fill=Y)

        self.markdown_text = tk.Text(
            text_container,
            wrap=WORD,
            font=("Consolas", 10),
            yscrollcommand=text_scrollbar.set,
            state=DISABLED
        )
        text_scrollbar.config(command=self.markdown_text.yview)
        self.markdown_text.pack(fill=BOTH, expand=True)

        # Configurar tags para formato Markdown
        self.markdown_text.tag_config("h1", font=("Arial", 18, "bold"), foreground="#2c3e50")
        self.markdown_text.tag_config("h2", font=("Arial", 15, "bold"), foreground="#34495e")
        self.markdown_text.tag_config("h3", font=("Arial", 13, "bold"), foreground="#7f8c8d")
        self.markdown_text.tag_config("bold", font=("Arial", 10, "bold"))
        self.markdown_text.tag_config("italic", font=("Arial", 10, "italic"))
        self.markdown_text.tag_config("code", font=("Consolas", 9), background="#ecf0f1")
        self.markdown_text.tag_config("list", lmargin1=20, lmargin2=40)

        # Botón copiar
        btn_frame = ttk.Frame(visualizador_frame)
        btn_frame.pack(fill=X, pady=(10, 0))

        ttk.Button(
            btn_frame,
            text="📋 Copiar Contenido",
            command=self._copiar_contenido_reporte,
            bootstyle="warning"
        ).pack(side=LEFT)

        # Cargar reportes inicialmente
        self._actualizar_lista_reportes()

    def _actualizar_lista_reportes(self):
        """Actualizar la lista de reportes según el tipo seleccionado"""
        logging.info(f"Actualizando lista de reportes - Tipo: {self.tipo_reporte_var.get()}")

        # Limpiar treeview
        for item in self.reportes_tree.get_children():
            self.reportes_tree.delete(item)

        # Directorio de reportes
        reportes_dir = Path("data/reportes_ia")
        if not reportes_dir.exists():
            logging.warning(f"Directorio {reportes_dir} no existe, creandolo...")
            reportes_dir.mkdir(parents=True, exist_ok=True)
            return

        # Obtener tipo seleccionado
        tipo = self.tipo_reporte_var.get()
        patron = "PARCIAL" if tipo == "parcial" else "COMPLETA"

        # Buscar archivos
        reportes = []
        for archivo in reportes_dir.glob("*.md"):
            if patron in archivo.name:
                # Parsear nombre: YYYYMMDD_HHMMSS_TIPO_casos.md
                partes = archivo.name.split("_")
                if len(partes) >= 3:
                    fecha_str = partes[0]
                    hora_str = partes[1]

                    # Formatear fecha
                    try:
                        fecha_obj = datetime.strptime(f"{fecha_str} {hora_str}", "%Y%m%d %H%M%S")
                        fecha_display = fecha_obj.strftime("%d/%m/%Y %H:%M:%S")
                    except:
                        fecha_display = f"{fecha_str} {hora_str}"

                    # Extraer casos
                    casos_str = "_".join(partes[3:]).replace(".md", "")

                    reportes.append({
                        "fecha": fecha_obj if 'fecha_obj' in locals() else datetime.now(),
                        "fecha_display": fecha_display,
                        "tipo": "Parcial" if patron == "PARCIAL" else "Completo",
                        "casos": casos_str,
                        "archivo": archivo.name,
                        "ruta": str(archivo)
                    })

        # Ordenar por fecha (más recientes primero)
        reportes.sort(key=lambda x: x["fecha"], reverse=True)

        # Agregar a treeview
        for rep in reportes:
            self.reportes_tree.insert("", "end", values=(
                rep["fecha_display"],
                rep["tipo"],
                rep["casos"],
                rep["archivo"]
            ), tags=(rep["ruta"],))

        logging.info(f"{len(reportes)} reportes cargados")

    def _cargar_reporte_seleccionado(self, event):
        """Cargar y mostrar el reporte seleccionado"""
        selection = self.reportes_tree.selection()
        if not selection:
            return

        # Obtener ruta del archivo
        item = selection[0]
        tags = self.reportes_tree.item(item, "tags")
        if not tags:
            return

        ruta_archivo = tags[0]
        logging.info(f"Cargando reporte: {ruta_archivo}")

        try:
            # Leer contenido
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Renderizar en el text widget
            self._renderizar_markdown(contenido)
            self.reporte_seleccionado = ruta_archivo

        except Exception as e:
            logging.error(f"Error cargando reporte: {e}")
            messagebox.showerror("Error", f"No se pudo cargar el reporte:\n{e}")

    def _renderizar_markdown(self, contenido):
        """Renderizar contenido Markdown con formato en el Text widget"""
        self.markdown_text.config(state=NORMAL)
        self.markdown_text.delete(1.0, END)

        lineas = contenido.split('\n')

        for linea in lineas:
            # Headers
            if linea.startswith('# '):
                self.markdown_text.insert(END, linea[2:] + '\n', "h1")
            elif linea.startswith('## '):
                self.markdown_text.insert(END, linea[3:] + '\n', "h2")
            elif linea.startswith('### '):
                self.markdown_text.insert(END, linea[4:] + '\n', "h3")
            # Listas
            elif linea.strip().startswith(('-', '*', '•')):
                self.markdown_text.insert(END, linea + '\n', "list")
            # Línea normal - procesar bold, italic, code
            else:
                self._procesar_linea_con_formato(linea)

        self.markdown_text.config(state=DISABLED)

    def _procesar_linea_con_formato(self, linea):
        """Procesar una línea aplicando formato inline (bold, italic, code)"""
        pos = 0
        while pos < len(linea):
            # Bold **texto**
            if linea[pos:pos+2] == '**':
                cierre = linea.find('**', pos+2)
                if cierre != -1:
                    self.markdown_text.insert(END, linea[pos+2:cierre], "bold")
                    pos = cierre + 2
                    continue

            # Italic *texto*
            if linea[pos] == '*' and (pos == 0 or linea[pos-1] != '*'):
                cierre = linea.find('*', pos+1)
                if cierre != -1 and (cierre+1 >= len(linea) or linea[cierre+1] != '*'):
                    self.markdown_text.insert(END, linea[pos+1:cierre], "italic")
                    pos = cierre + 1
                    continue

            # Code `texto`
            if linea[pos] == '`':
                cierre = linea.find('`', pos+1)
                if cierre != -1:
                    self.markdown_text.insert(END, linea[pos+1:cierre], "code")
                    pos = cierre + 1
                    continue

            # Carácter normal
            self.markdown_text.insert(END, linea[pos])
            pos += 1

        self.markdown_text.insert(END, '\n')

    def _copiar_contenido_reporte(self):
        """Copiar el contenido del reporte al portapapeles"""
        contenido = self.markdown_text.get(1.0, END)
        self.clipboard_clear()
        self.clipboard_append(contenido)
        messagebox.showinfo("Copiado", "Contenido copiado al portapapeles")

    def _seleccionar_ultimo_reporte(self):
        """Seleccionar automáticamente el primer reporte (más reciente) en la lista"""
        # Obtener primer item del treeview
        items = self.reportes_tree.get_children()
        if items:
            # Seleccionar y hacer focus en el primer item
            primer_item = items[0]
            self.reportes_tree.selection_set(primer_item)
            self.reportes_tree.focus(primer_item)
            self.reportes_tree.see(primer_item)

            # Cargar el reporte manualmente
            tags = self.reportes_tree.item(primer_item, "tags")
            if tags:
                ruta_archivo = tags[0]
                logging.info(f"Auto-cargando reporte: {ruta_archivo}")

                try:
                    with open(ruta_archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    self._renderizar_markdown(contenido)
                    self.reporte_seleccionado = ruta_archivo
                except Exception as e:
                    logging.error(f"Error auto-cargando reporte: {e}")

    def _generar_reporte_ia(self, resultados, tipo):
        """
        Generar un archivo de reporte Markdown a partir de los resultados de auditoría

        Args:
            resultados: Dict con resultados de auditoría IA O lista de resultados
            tipo: 'parcial' o 'completa'

        Returns:
            str: Ruta al archivo generado
        """
        logging.info(f"Generando reporte IA tipo: {tipo}")

        # Crear directorio si no existe
        reportes_dir = Path("data/reportes_ia")
        reportes_dir.mkdir(parents=True, exist_ok=True)

        # V2.1.6: Detectar formato de entrada (dict o lista)
        if isinstance(resultados, list):
            # Formato nuevo: lista plana de resultados
            registros = resultados
            casos_procesados = len(registros)
            casos_exitosos = sum(1 for r in registros if r.get("exito", False))
            casos_errores = casos_procesados - casos_exitosos
            total_correcciones = sum(r.get("correcciones_aplicadas", 0) for r in registros)
        else:
            # Formato viejo: dict con "registros"
            registros = resultados.get("registros", [])
            casos_procesados = len(registros)
            casos_exitosos = sum(1 for r in registros if r.get("estado") == "exitoso")
            casos_errores = casos_procesados - casos_exitosos
            total_correcciones = sum(len(r.get("correcciones", [])) for r in registros)

        # Determinar rango de IHQ (compatible con ambos formatos)
        ihq_numeros = []
        for r in registros:
            # V2.1.6: Soportar ambos formatos
            ihq = r.get("ihq_numero") or r.get("numero_peticion", "")
            if ihq and ihq.startswith("IHQ"):
                try:
                    num = int(ihq.replace("IHQ", ""))
                    ihq_numeros.append(num)
                except:
                    pass

        if ihq_numeros:
            ihq_min = min(ihq_numeros)
            ihq_max = max(ihq_numeros)
            casos_str = f"IHQ{ihq_min:05d}_IHQ{ihq_max:05d}" if ihq_min != ihq_max else f"IHQ{ihq_min:05d}"
        else:
            casos_str = f"{casos_procesados}_casos"

        # Generar nombre de archivo
        timestamp = datetime.now()
        fecha_str = timestamp.strftime("%Y%m%d")
        hora_str = timestamp.strftime("%H%M%S")
        tipo_str = "PARCIAL" if tipo == "parcial" else "COMPLETA"
        nombre_archivo = f"{fecha_str}_{hora_str}_{tipo_str}_{casos_str}.md"
        ruta_archivo = reportes_dir / nombre_archivo

        # Generar contenido Markdown
        contenido = f"""# 📊 Reporte de Auditoría {tipo_str.title()} - EVARISIS CIRUGÍA ONCOLÓGICA

**Fecha**: {timestamp.strftime("%d/%m/%Y %H:%M:%S")}
**Tipo**: {"Parcial" if tipo == "parcial" else "Completa"}
**Casos procesados**: {casos_procesados}

## 📋 Resumen Ejecutivo

- ✅ Casos exitosos: {casos_exitosos}
- ❌ Casos con errores: {casos_errores}
- 🔧 Total correcciones: {total_correcciones}

## 📝 Detalle por Caso

"""

        # V3.2.4.2: Agregar detalles de cada caso CON DIFERENCIAS según tipo
        for registro in registros:
            # Formato nuevo vs viejo
            if isinstance(resultados, list):
                # Formato nuevo
                ihq = registro.get("numero_peticion", "N/A")
                estado = "EXITOSO" if registro.get("exito", False) else "ERROR"
                num_correcciones = registro.get("correcciones_aplicadas", 0)
                detalles = registro.get("detalles", [])
                error = registro.get("error", "")
                # V3.2.4.2: Nuevos campos
                analisis_profundo = registro.get("analisis_profundo", {})
                no_encontrados = registro.get("no_encontrados", [])
            else:
                # Formato viejo
                ihq = registro.get("ihq_numero", "N/A")
                estado = registro.get("estado", "desconocido").upper()
                detalles = registro.get("correcciones", [])
                num_correcciones = len(detalles)
                error = registro.get("errores", [])
                analisis_profundo = {}
                no_encontrados = []

            contenido += f"### Caso: {ihq}\n\n"
            contenido += f"**Estado**: {estado}  \n"
            contenido += f"**Correcciones aplicadas**: {num_correcciones}\n\n"

            # Correcciones aplicadas
            if detalles and any(d.get("aplicada") for d in detalles):
                contenido += "**Correcciones aplicadas:**\n\n"
                for i, detalle in enumerate(detalles, 1):
                    if not detalle.get("aplicada"):
                        continue
                    campo = detalle.get("campo", "N/A")
                    valor_anterior = detalle.get("valor_anterior", "")
                    valor_nuevo = detalle.get("valor_nuevo", "")
                    razon = detalle.get("razon", "")

                    contenido += f"{i}. **Campo**: `{campo}`\n"
                    contenido += f"   - *Valor anterior*: {valor_anterior or '(vacío)'}\n"
                    contenido += f"   - *Valor nuevo*: {valor_nuevo}\n"
                    contenido += f"   - *Razón*: {razon}\n\n"

            # V3.2.4.2: AUDITORÍA PARCIAL - Mostrar campos no encontrados
            if tipo == 'parcial' and no_encontrados:
                contenido += f"**Campos no encontrados en el PDF** ({len(no_encontrados)}):\n\n"
                contenido += "> Estos campos están vacíos en BD y no se encontraron datos en el PDF para completarlos.\n\n"
                for campo in no_encontrados[:10]:  # Mostrar máximo 10
                    if isinstance(campo, dict):
                        campo_nombre = campo.get("campo", str(campo))
                    else:
                        campo_nombre = str(campo)
                    contenido += f"- {campo_nombre}\n"
                if len(no_encontrados) > 10:
                    contenido += f"\n... y {len(no_encontrados) - 10} campos más.\n"
                contenido += "\n"

            # V3.2.4.2: AUDITORÍA COMPLETA - Mostrar análisis profundo
            if tipo == 'completa' and analisis_profundo:
                contenido += "## 📊 Análisis Profundo\n\n"

                # Veracidad
                veracidad = analisis_profundo.get("veracidad_porcentaje")
                if veracidad is not None:
                    contenido += f"**Veracidad**: {veracidad}% de coincidencia entre PDF y BD\n\n"

                # Problemas detectados
                problemas = analisis_profundo.get("problemas_detectados", [])
                if problemas:
                    contenido += f"**⚠️ Problemas detectados** ({len(problemas)}):\n\n"
                    for problema in problemas:
                        contenido += f"- {problema}\n"
                    contenido += "\n"

                # Sugerencias
                sugerencias = analisis_profundo.get("sugerencias", [])
                if sugerencias:
                    contenido += f"**💡 Sugerencias de mejora** ({len(sugerencias)}):\n\n"
                    for sugerencia in sugerencias:
                        contenido += f"- {sugerencia}\n"
                    contenido += "\n"

                # Biomarcadores no mapeados
                bio_no_mapeados = analisis_profundo.get("biomarcadores_no_mapeados", [])
                if bio_no_mapeados:
                    contenido += f"**🧬 Biomarcadores sin columna** ({len(bio_no_mapeados)}):\n\n"
                    for bio in bio_no_mapeados:
                        contenido += f"- {bio}\n"
                    contenido += "\n"

            # Errores
            if error:
                contenido += "**Errores encontrados:**\n\n"
                if isinstance(error, list):
                    for e in error:
                        contenido += f"- {e}\n"
                else:
                    contenido += f"- {error}\n"
                contenido += "\n"

            contenido += "---\n\n"

        # Footer
        contenido += f"""
---
*Generated by EVARISIS CIRUGÍA ONCOLÓGICA*
*{timestamp.strftime("%d/%m/%Y %H:%M:%S")}*
"""

        # Guardar archivo
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            logging.info(f"Reporte generado: {ruta_archivo}")
            return str(ruta_archivo)
        except Exception as e:
            logging.error(f"Error guardando reporte: {e}")
            return None

    def _create_kpi_card(self, parent, title, value):
        """Crear una tarjeta KPI usando TTKBootstrap"""
        card = ttk.Frame(parent, padding=10, relief="solid", borderwidth=1)
        
        ttk.Label(card, text=title, font=("Segoe UI", 12)).pack(anchor=W, padx=4, pady=(2, 0))
        value_lbl = ttk.Label(card, text=value, font=("Segoe UI", 26, "bold")).pack(anchor=W, padx=4, pady=(0, 2))
        
        # Store reference for updating
        card.value_lbl = list(card.winfo_children())[-1] if card.winfo_children() else None
        
        return card

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Dibujar un rectángulo con esquinas redondeadas en un Canvas"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
            x1 + radius, y1,
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _create_circle_icon(self, parent, icon_text, size=52, bg_color="#2d3075", fg_color="white"):
        """Crear un icono circular con fondo coloreado usando Canvas"""
        canvas = tk.Canvas(parent, width=size, height=size, highlightthickness=0, bg=parent["bg"] if isinstance(parent, tk.Canvas) else "#1e2152")
        # Dibujar círculo de fondo
        pad = 2
        canvas.create_oval(pad, pad, size - pad, size - pad, fill=bg_color, outline="")
        # Texto del icono centrado
        canvas.create_text(size // 2, size // 2, text=icon_text, font=("Segoe UI", 16), fill=fg_color)
        return canvas

    def _create_welcome_screen(self):
        """Crear la pantalla de bienvenida inicial con diseño profesional"""
        self.welcome_frame = ttk.Frame(self.content_container, padding=20)

        # Contenedor central con grid para centrado vertical
        center_container = ttk.Frame(self.welcome_frame)
        center_container.pack(expand=True, fill=BOTH)
        center_container.grid_rowconfigure(0, weight=1)
        center_container.grid_rowconfigure(1, weight=0)
        center_container.grid_rowconfigure(2, weight=1)
        center_container.grid_columnconfigure(0, weight=1)

        # Espaciador superior
        ttk.Frame(center_container).grid(row=0, column=0)

        # === TARJETA PRINCIPAL CON FONDO OSCURO Y ESQUINAS REDONDEADAS ===
        card_width = 720
        card_height = 460
        card_radius = 28
        card_bg = "#1e2152"  # Azul oscuro índigo
        card_icon_bg = "#2d3075"  # Fondo de iconos circulares

        # Canvas para la tarjeta redondeada
        self._welcome_card_canvas = tk.Canvas(
            center_container,
            width=card_width,
            height=card_height,
            highlightthickness=0,
            bd=0
        )
        self._welcome_card_canvas.grid(row=1, column=0, pady=10)

        # Obtener color de fondo del tema para el canvas exterior
        try:
            theme_bg = self.style.lookup("TFrame", "background")
            if not theme_bg:
                theme_bg = "#2b3e50"
        except Exception:
            theme_bg = "#2b3e50"
        self._welcome_card_canvas.configure(bg=theme_bg)

        # Dibujar tarjeta redondeada
        self._draw_rounded_rect(
            self._welcome_card_canvas,
            0, 0, card_width, card_height,
            card_radius,
            fill=card_bg, outline=""
        )

        # --- Título principal ---
        self._welcome_card_canvas.create_text(
            card_width // 2, 80,
            text="🏥  Bienvenido al Gestor Oncológico  🔬",
            font=("Segoe UI", 26, "bold"),
            fill="white",
            anchor="center"
        )

        # --- Subtítulo ---
        subtitle_text = ("Enfocado en la investigación y mejora del área de oncología\n"
                        "del Hospital Universitario del Valle")
        self._welcome_card_canvas.create_text(
            card_width // 2, 135,
            text=subtitle_text,
            font=("Segoe UI", 13),
            fill="#b8bedd",
            anchor="center",
            justify="center"
        )

        # --- Fila de iconos circulares ---
        welcome_icons = ["📊", "📋", "🧬", "💡", "📅", "🔍", "⚕️"]
        icon_size = 52
        icon_spacing = 16
        total_icons_width = len(welcome_icons) * icon_size + (len(welcome_icons) - 1) * icon_spacing
        icon_start_x = (card_width - total_icons_width) // 2
        icon_y = 200

        for i, icon_text in enumerate(welcome_icons):
            x = icon_start_x + i * (icon_size + icon_spacing)
            # Dibujar círculo de fondo
            self._welcome_card_canvas.create_oval(
                x + 2, icon_y + 2, x + icon_size - 2, icon_y + icon_size - 2,
                fill=card_icon_bg, outline=""
            )
            # Dibujar icono centrado
            self._welcome_card_canvas.create_text(
                x + icon_size // 2, icon_y + icon_size // 2,
                text=icon_text,
                font=("Segoe UI", 18),
                fill="white"
            )

        # --- Verificar datos y mostrar contenido inferior ---
        has_data = False
        try:
            from core.database_manager import get_all_records_as_dataframe
            df_check = get_all_records_as_dataframe()
            has_data = not df_check.empty
        except Exception as e:
            logging.error(f"Error verificando datos: {e}")

        if not has_data:
            # Texto "No hay información"
            self._welcome_card_canvas.create_text(
                card_width // 2, 310,
                text="No hay información en la base de datos",
                font=("Segoe UI", 13),
                fill="#8890b5",
                anchor="center"
            )

            # Botón "Agregar Información" con estilo outline sobre la card
            btn_w = 380
            btn_h = 48
            btn_x = (card_width - btn_w) // 2
            btn_y = 355
            btn_radius = 24

            # Borde redondeado del botón
            self._draw_rounded_rect(
                self._welcome_card_canvas,
                btn_x, btn_y, btn_x + btn_w, btn_y + btn_h,
                btn_radius,
                fill="#252a6b", outline="#5b6abf", width=2
            )

            # Texto del botón
            self._welcome_card_canvas.create_text(
                card_width // 2, btn_y + btn_h // 2,
                text="⊕  Agregar Información a la Base de Datos",
                font=("Segoe UI", 13, "bold"),
                fill="white",
                anchor="center"
            )

            # Zona clickeable invisible sobre el botón
            self._welcome_btn_hitbox = self._welcome_card_canvas.create_rectangle(
                btn_x, btn_y, btn_x + btn_w, btn_y + btn_h,
                fill="", outline="", tags="add_btn"
            )
            self._welcome_card_canvas.tag_bind("add_btn", "<Button-1>", lambda e: self._goto_import_data_tab())
            self._welcome_card_canvas.tag_bind("add_btn", "<Enter>", lambda e: self._welcome_card_canvas.configure(cursor="hand2"))
            self._welcome_card_canvas.tag_bind("add_btn", "<Leave>", lambda e: self._welcome_card_canvas.configure(cursor=""))
        else:
            # Mensaje de instrucción cuando hay datos
            instruction_text = ("Selecciona una opción del menú flotante para comenzar\n"
                               "a trabajar con los datos oncológicos")
            self._welcome_card_canvas.create_text(
                card_width // 2, 320,
                text=instruction_text,
                font=("Segoe UI", 13),
                fill="#8890b5",
                anchor="center",
                justify="center"
            )

        # Espaciador inferior
        ttk.Frame(center_container).grid(row=2, column=0)

    def _goto_import_data_tab(self):
        """Navegar directamente a la pestaña de importar datos del dashboard"""
        # Navegar a base de datos
        self._nav_to_database()
        # Esperar un poco para que se cargue el dashboard
        self.after(100, self._select_import_tab)

    def _select_import_tab(self):
        """Seleccionar la pestaña de importar datos en el dashboard mejorado"""
        try:
            if hasattr(self, 'enhanced_dashboard') and hasattr(self.enhanced_dashboard, 'notebook'):
                # La pestaña de importar es la número 4 (índice 4)
                self.enhanced_dashboard.notebook.select(4)
        except Exception as e:
            logging.error(f"Error seleccionando pestana de importar: {e}")



    # Métodos de navegación actualizados
    def show_database_frame(self):
        """Mostrar panel de base de datos (función compatibilidad)"""
        self._nav_to_database()
        # Actualizar dashboard mejorado cuando se muestre el panel
        if hasattr(self, 'enhanced_dashboard'):
            self.enhanced_dashboard.refresh_dashboard()

    def show_visualizar_frame(self):
        """Mostrar panel de visualización (función compatibilidad)"""
        self._nav_to_visualizar()

    def show_dashboard_frame(self):
        """Mostrar panel de análisis gráfico (función compatibilidad)"""
        self._nav_to_dashboard()
        # CORREGIDO: Asegurar que los datos estén cargados antes de mostrar el dashboard
        try:
            # Si master_df está vacío, cargar datos de la base de datos
            if self.master_df.empty:
                from core.database_manager import init_db, get_all_records_as_dataframe
                # V6.2.0: Comentado - init_db() ya se llama en ihq_processor antes del guardado
                # Llamarlo aquí causa que el UPDATE de relleno sobrescriba valores recién insertados
                # init_db()
                self.master_df = get_all_records_as_dataframe()

                # Ordenar por número de caso automáticamente
                if self.master_df is not None and not self.master_df.empty and "Numero de caso" in self.master_df.columns:
                    self.master_df = self.master_df.sort_values(
                        by="Numero de caso",
                        ascending=True,
                        na_position='last'
                    ).reset_index(drop=True)

            # Ahora cargar el dashboard con datos disponibles
            self.cargar_dashboard()
        except Exception as e:
            logging.error(f"Error cargando datos para dashboard: {e}")
            # Cargar dashboard vacío para mostrar mensaje apropiado
            self.cargar_dashboard()
        
    def show_welcome_screen(self):
        """Mostrar pantalla de bienvenida con header visible y menú flotante oculto"""
        # Ocultar otros paneles
        if self.panel_activo:
            self.panel_activo.pack_forget()
        
        # Ocultar menú flotante si está visible
        if self.floating_menu_visible:
            self._hide_floating_menu()
        
        # Mostrar header (solo en pantalla de bienvenida)
        self._show_header()
        
        # Mostrar la pantalla de bienvenida
        self.welcome_frame.pack(fill=BOTH, expand=True)
        self.panel_activo = self.welcome_frame
        self.welcome_screen_active = True
        self.current_view = "welcome"

    def _hide_welcome_and_show_panel(self, panel):
        """Ocultar pantalla de bienvenida, animar menús y mostrar panel"""
        # Si es la primera navegación desde la pantalla de bienvenida
        if self.welcome_screen_active:
            self._animate_menus_hide()
            self.welcome_screen_active = False
        
        # Cambiar el panel
        self._show_panel(panel)
    
    def _show_panel(self, panel):
        """Mostrar un panel específico"""
        if self.panel_activo:
            self.panel_activo.pack_forget()
        
        self.panel_activo = panel
        panel.pack(fill=BOTH, expand=True)
    
    def _animate_menus_hide(self):
        """Animar el ocultamiento de header y sidebar"""
        # Animar header hacia arriba
        self._animate_header_hide()
        # Animar sidebar hacia la izquierda  
        self._animate_sidebar_hide()
        # Actualizar el botón de navegación
        self.nav_toggle_btn.configure(text="▶ Mostrar Menús")

    def _animate_header_hide(self):
        """Animar ocultamiento del header hacia arriba - ULTRA RÁPIDO"""
        def slide_up(steps_remaining):
            if steps_remaining > 0:
                current_height = self.header.winfo_height()
                new_height = max(0, current_height - 20)  # Aumentado de 10 a 20
                if new_height > 0:
                    self.after(5, lambda: slide_up(steps_remaining - 1))  # Reducido de 20ms a 5ms
                else:
                    self.header.pack_forget()
                    self.header_separator.pack_forget()
                    self.header_visible = False
            
        if self.header_visible:
            slide_up(5)  # Reducido de 10 a 5 pasos

    def _animate_sidebar_hide(self):
        """Animar ocultamiento del sidebar hacia la izquierda - ULTRA RÁPIDO"""
        if not hasattr(self, 'sidebar') or not self.sidebar_visible:
            self.sidebar_visible = False
            return
        def slide_left(steps_remaining):
            if steps_remaining > 0:
                current_width = self.sidebar.winfo_width()
                new_width = max(0, current_width - 50)  # Aumentado de 30 a 50
                self.sidebar.config(width=new_width)
                if new_width > 0:
                    self.after(5, lambda: slide_left(steps_remaining - 1))  # Reducido de 20ms a 5ms
                else:
                    self.sidebar.pack_forget()
                    self.sidebar_visible = False
            
        if self.sidebar_visible:
            slide_left(4)  # Reducido de 8 a 4 pasos

    def _toggle_navigation_visibility(self):
        """Alternar visibilidad de header y sidebar con animación"""
        if self.header_visible and self.sidebar_visible:
            # Ocultar menús
            self._animate_menus_hide()
        else:
            # Mostrar menús
            self._animate_menus_show()

    def _animate_menus_show(self):
        """Animar la aparición de header y sidebar"""
        # Mostrar header
        if not self.header_visible:
            # Obtener el contenedor padre correcto
            parent = self.content_container.master
            self.header.pack(fill=X, before=parent.children[list(parent.children.keys())[0]])
            self.header_visible = True
            
        # Mostrar sidebar
        if not self.sidebar_visible and hasattr(self, 'sidebar'):
            # Obtener el contenedor padre correcto (body frame)
            body_parent = self.content_container.master
            self.sidebar.pack(side=LEFT, fill=Y, before=self.content_container)
            self.sidebar.config(width=self.sidebar_width)
            self.sidebar_visible = True
            
        # Actualizar botón
        self.nav_toggle_btn.configure(text="◀ Ocultar Menús")
        
        # Si no estamos en la pantalla de bienvenida, salir del modo bienvenida
        if self.welcome_screen_active and self.panel_activo != self.welcome_frame:
            self.welcome_screen_active = False

    def open_web_auto_modal(self):
        """Abrir modal de automatización web"""
        messagebox.showinfo("Web Automation", "Función de automatización web - En desarrollo")



    # Métodos de utilidad (conservando la lógica de carga de archivos)
    def _get_path(self, relative_path):
        """Obtiene la ruta absoluta de un archivo, compatible con PyInstaller"""
        try: 
            base_path = sys._MEIPASS
        except Exception: 
            base_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(base_path, relative_path)
    
    def _cargar_foto_usuario(self):
        """Cargar foto del usuario desde la ruta especificada"""
        try:
            ruta_foto = self.info_usuario.get("ruta_foto", "SIN_FOTO")
            if ruta_foto and ruta_foto != "SIN_FOTO" and os.path.exists(ruta_foto):
                img = Image.open(ruta_foto).resize((50, 50), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            return None
        except Exception as e:
            logging.error(f"Error al cargar la foto del usuario: {e}")
            return None

    def _cargar_iconos(self):
        """Carga todos los iconos necesarios para la interfaz"""
        iconos = {}
        icon_files = {
            "logo1": "logo1.png", 
            "logo2": "logo2.png", 
            "logo3": "logo3.png",
            "usuario": "usuario.png"
        }
        for name, filename in icon_files.items():
            try:
                path = self._get_path(os.path.join("imagenes", filename))
                if name == "logo1":
                    size = (55, 55)       # logo izquierdo header (compacto)
                elif name == "logo3":
                    size = (60, 60)       # logo derecho header (compacto)
                elif name == "logo2":
                    size = (140, 140)
                elif name == "usuario":
                    size = (48, 48)       # foto usuario por defecto
                else:
                    size = (32, 32)
                img = Image.open(path).resize(size, Image.Resampling.LANCZOS)
                iconos[name] = ImageTk.PhotoImage(img)
            except Exception as e:
                logging.warning(f"No se encontró el icono o logo '{filename}': {e}")
                iconos[name] = None
        return iconos

    # =========================
    # Helpers UI (KPI y Status)
    # =========================
    # =========================
    # Métodos de utilidad y renderizado
    # =========================
    def _render_kpis(self, df):
        """Actualizar los valores de los KPIs con datos del DataFrame"""
        if df is None or df.empty:
            # Resetear valores cuando no hay datos
            try:
                if hasattr(self, 'kpi_total') and hasattr(self.kpi_total, 'value_lbl'):
                    self.kpi_total.value_lbl.configure(text="0")
                if hasattr(self, 'kpi_rango') and hasattr(self.kpi_rango, 'value_lbl'):
                    self.kpi_rango.value_lbl.configure(text="—")
                if hasattr(self, 'kpi_ultimo') and hasattr(self.kpi_ultimo, 'value_lbl'):
                    self.kpi_ultimo.value_lbl.configure(text="—")
            except Exception as e:
                logging.error(f"Error al resetear KPIs: {e}")
            return

        total = len(df)

        # Rango de fechas: fecha mínima y máxima
        fecha_cols = [
            "Fecha Informe",
            "Fecha de informe",
            "Fecha de ingreso",
        ]
        fecha_min = None
        fecha_max = None
        
        for c in fecha_cols:
            if c in df.columns:
                try:
                    fechas_validas = pd.to_datetime(df[c], dayfirst=True, errors="coerce").dropna()
                    if not fechas_validas.empty:
                        if fecha_min is None or fechas_validas.min() < fecha_min:
                            fecha_min = fechas_validas.min()
                        if fecha_max is None or fechas_validas.max() > fecha_max:
                            fecha_max = fechas_validas.max()
                except Exception:
                    pass

        # Formatear rango de fechas
        if fecha_min and fecha_max:
            if fecha_min.date() == fecha_max.date():
                rango_txt = fecha_min.strftime("%d/%m/%Y")
            else:
                rango_txt = f"{fecha_min.strftime('%d/%m/%Y')} - {fecha_max.strftime('%d/%m/%Y')}"
        else:
            rango_txt = "—"

        # Última importación (fecha más reciente)
        ultimo_txt = "—" if (fecha_max is None or pd.isna(fecha_max)) else fecha_max.strftime("%d/%m/%Y")

        # Actualizar KPIs con los nuevos valores
        try:
            if hasattr(self, 'kpi_total') and hasattr(self.kpi_total, 'value_lbl'):
                self.kpi_total.value_lbl.configure(text=f"{total:,}".replace(",", "."))
            if hasattr(self, 'kpi_rango') and hasattr(self.kpi_rango, 'value_lbl'):
                self.kpi_rango.value_lbl.configure(text=rango_txt)
            if hasattr(self, 'kpi_ultimo') and hasattr(self.kpi_ultimo, 'value_lbl'):
                self.kpi_ultimo.value_lbl.configure(text=ultimo_txt)
        except Exception as e:
            logging.error(f"Error al actualizar KPIs: {e}")

    def set_status(self, text):
        """Actualiza el texto de la barra de estado"""
        try:
            # Crear una barra de estado temporal si no existe
            if not hasattr(self, 'status_label'):
                self.status_label = ttk.Label(self, text=text, bootstyle="secondary")
                self.status_label.pack(side="bottom", fill="x", padx=5, pady=2)
            else:
                self.status_label.configure(text=text)
        except Exception as e:
            logging.error(f"Error al actualizar status: {e}")
            logging.info(f"[STATUS] {text}")  # Fallback al console

    # =========================
    # Métodos de carga de recursos (conservados)
    # =========================
            pass

    # =========================
    # Navegación (métodos obsoletos removidos - usar los métodos nuevos)
    # =========================




    # ---------- Helpers Dashboard ----------

    def _clear_filters(self):
        for k in self.db_filters:
            self.db_filters[k].set("")
        self._refresh_dashboard()

    def _refresh_dashboard(self):
        try:
            self.set_status("Actualizando dashboard…")
            self.cargar_dashboard()
        finally:
            self.set_status("Dashboard actualizado.")

    def _get_filtered_df(self, df):
        dff = df.copy()
        fd = self.db_filters["fecha_desde"].get().strip()
        fh = self.db_filters["fecha_hasta"].get().strip()
        if fd:
            d0 = pd.to_datetime(fd, dayfirst=True, errors="coerce")
            if pd.notna(d0):
                dff = dff[dff["_fecha_informe"] >= d0]
        if fh:
            d1 = pd.to_datetime(fh, dayfirst=True, errors="coerce")
            if pd.notna(d1):
                dff = dff[dff["_fecha_informe"] <= d1]

        srv = self.db_filters["servicio"].get().strip()
        if srv:
            dff = dff[dff.get("Servicio", "").astype(str).eq(srv)]
        mal = self.db_filters["malignidad"].get().strip()
        if mal:
            dff = dff[dff.get("Malignidad", "").astype(str).str.upper().eq(mal)]
        rsp = self.db_filters["responsable"].get().strip()
        if rsp:
            dff = dff[dff.get("Patologo", "").astype(str).eq(rsp)]
        return dff

    def _clear_dash_area(self):
        # Desmonta los canvases previos para liberar memoria
        for cv in getattr(self, "_dash_canvases", []):
            try:
                cv.get_tk_widget().destroy()
            except Exception:
                pass
        self._dash_canvases = []

        # Limpia frames hijos en cada pestaña
        for tab in [self.tab_overview, self.tab_biomarkers, self.tab_times, self.tab_quality, self.tab_compare]:
            for child in tab.grid_slaves():
                child.destroy()

    def _chart_in(self, tab, row, col, render_fn, title, dff):
        card = ttk.Frame(tab, padding=8, relief="solid", borderwidth=1)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Configurar responsive grid
        tab.grid_rowconfigure(row, weight=1)
        tab.grid_columnconfigure(col, weight=1)

        header = ttk.Frame(card)
        header.pack(fill="x", pady=(0, 6))
        ttk.Label(header, text=title, font=("Segoe UI", 11, "bold")).pack(side="left")
        ttk.Button(header, text="⛶", 
                  command=lambda: self._open_fullscreen_figure(render_fn, title, dff),
                  bootstyle="outline").pack(side="right")

        try:
            fig = render_fn()
            if fig is None:
                ttk.Label(card, text="(sin datos)", font=("Segoe UI", 10)).pack(padx=10, pady=20)
                return
            
            # Ajustar tamaño de figura para mejor responsive
            fig.set_size_inches(4.5, 3.2)
            fig.set_dpi(90)
            
            canvas = FigureCanvasTkAgg(fig, master=card)
            canvas.draw()
            widget = canvas.get_tk_widget()
            widget.pack(fill="both", expand=True, padx=4, pady=4)
            widget.bind("<Double-Button-1>", lambda e: self._open_fullscreen_figure(render_fn, title, dff))
            self._dash_canvases.append(canvas)
        except Exception as e:
            ttk.Label(card, text=f"Error: {e}", font=("Segoe UI", 9), bootstyle="danger").pack(padx=10, pady=10)

    def _toggle_db_sidebar(self):
        # Muestra/oculta el sidebar, ajusta texto del botón y grid
        if self.db_sidebar_collapsed:
            self.db_sidebar.grid(row=0, column=0, sticky="ns", padx=(0, 12), pady=6)
            self.btn_toggle_sidebar.configure(text="✕ Ocultar filtros")
        else:
            self.db_sidebar.grid_forget()
            self.btn_toggle_sidebar.configure(text="≡ Mostrar filtros")
        self.db_sidebar_collapsed = not self.db_sidebar_collapsed

    def _open_filters_sheet(self):
        # Modal de filtros (para no robar ancho)
        top = tk.Toplevel(self)
        top.title("Filtros")
        top.geometry("420x420")
        top.grab_set()
        top.transient(self)
        
        wrap = ttk.Frame(top, padding=12)
        wrap.pack(fill="both", expand=True)

        def row(lbl, widget):
            r = ttk.Frame(wrap)
            r.pack(fill="x", pady=6)
            ttk.Label(r, text=lbl, width=20, anchor="w").pack(side="left")
            widget.pack(in_=r, side="left", fill="x", expand=True)

        e1 = ttk.Entry(wrap, textvariable=self.db_filters["fecha_desde"])
        e2 = ttk.Entry(wrap, textvariable=self.db_filters["fecha_hasta"])
        
        # Verificar si los componentes existen antes de obtener sus valores
        servicio_vals = []
        if self.cmb_servicio is not None:
            try:
                servicio_vals = list(self.cmb_servicio.cget("values"))
            except:
                servicio_vals = []
        
        malig_vals = ["", "PRESENTE", "AUSENTE"]
        if self.cmb_malig is not None:
            try:
                malig_vals = list(self.cmb_malig.cget("values"))
            except:
                malig_vals = ["", "PRESENTE", "AUSENTE"]
        
        resp_vals = []
        if self.cmb_resp is not None:
            try:
                resp_vals = list(self.cmb_resp.cget("values"))
            except:
                resp_vals = []
        
        cb1 = ttk.Combobox(wrap, values=servicio_vals, textvariable=self.db_filters["servicio"])
        cb2 = ttk.Combobox(wrap, values=malig_vals, textvariable=self.db_filters["malignidad"])
        cb3 = ttk.Combobox(wrap, values=resp_vals, textvariable=self.db_filters["responsable"])

        row("Fecha desde (dd/mm/aaaa)", e1)
        row("Fecha hasta (dd/mm/aaaa)", e2)
        row("Servicio", cb1)
        row("Malignidad", cb2)
        row("Responsable", cb3)

        btns = ttk.Frame(wrap)
        btns.pack(fill="x", pady=(10,0))
        ttk.Button(btns, text="Aplicar", command=lambda:(self._refresh_dashboard(), top.destroy())).pack(side="left", expand=True, fill="x", padx=(0,6))
        ttk.Button(btns, text="Limpiar", command=self._clear_filters).pack(side="left", expand=True, fill="x", padx=(6,0))

    def _open_fullscreen_figure(self, render_fn, title, dff):
        # Ventana a pantalla completa con inspector lateral
        fs = tk.Toplevel(self)
        fs.title(title)
        try:
            fs.state('zoomed')
        except Exception:
            pass
        fs.grid_rowconfigure(0, weight=1)
        fs.grid_columnconfigure(0, weight=1)
        fs.grid_columnconfigure(1, weight=0)

        # Área de gráfico
        graph_area = ttk.Frame(fs, padding=10)
        graph_area.grid(row=0, column=0, sticky="nsew", padx=(10,6), pady=10)
        fig = render_fn()
        if fig is None:
            ttk.Label(graph_area, text="(sin datos)").pack(padx=12, pady=12)
        else:
            canv = FigureCanvasTkAgg(fig, master=graph_area)
            canv.draw()
            canv.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Inspector lateral
        insp = ttk.Frame(fs, padding=10, width=300)
        insp.grid(row=0, column=1, sticky="ns", padx=(6,10), pady=10)
        ttk.Label(insp, text="Inspector", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,6))
        self._build_inspector(insp, title, dff)

        # Barra superior simple (cerrar)
        topbar = ttk.Frame(graph_area)
        topbar.pack(fill="x", pady=(0,10))
        ttk.Label(topbar, text=title, font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Button(topbar, text="Cerrar", command=fs.destroy).pack(side="right")

    def _build_inspector(self, parent, title, dff):
        # Datos generales
        n = len(dff)
        fmin = pd.to_datetime(dff.get("_fecha_informe"), errors="coerce").min()
        fmax = pd.to_datetime(dff.get("_fecha_informe"), errors="coerce").max()
        rng = f"{fmin:%d/%m/%Y} – {fmax:%d/%m/%Y}" if pd.notna(fmin) and pd.notna(fmax) else "—"

        def row(k, v):
            r = ttk.Frame(parent)
            r.pack(fill="x", padx=12, pady=4)
            ttk.Label(r, text=k).pack(side="left")
            ttk.Label(r, text=v).pack(side="right")

        row("Registros filtrados", f"{n:,}".replace(",", "."))
        row("Rango de fechas", rng)

        # Secciones condicionales útiles
        if "Malignidad" in dff.columns:
            ser = dff["Malignidad"].astype(str).str.upper().value_counts()
            box = ttk.Frame(parent, padding=8, relief="solid", borderwidth=1); box.pack(fill="x", padx=12, pady=(10,4))
            ttk.Label(box, text="Malignidad", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(8,2))
            for k,v in ser.items():
                rowtxt = ttk.Frame(box); rowtxt.pack(fill="x", padx=10, pady=2)
                ttk.Label(rowtxt, text=f"{k}").pack(side="left")
                ttk.Label(rowtxt, text=str(v)).pack(side="right")

        if "Organo" in dff.columns:
            top_org = dff["Organo"].astype(str).replace({"": "No especificado"}).value_counts().head(8)
        elif "IHQ_ORGANO" in dff.columns:
            top_org = dff["IHQ_ORGANO"].astype(str).replace({"": "No especificado"}).value_counts().head(8)
        else:
            top_org = None

        if top_org is not None and not top_org.empty:
            box2 = ttk.Frame(parent, padding=8, relief="solid", borderwidth=1); box2.pack(fill="x", padx=12, pady=(10,12))
            ttk.Label(box2, text="Top Órganos", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=(8,2))
            for k,v in top_org.items():
                rowtxt = ttk.Frame(box2); rowtxt.pack(fill="x", padx=10, pady=2)
                ttk.Label(rowtxt, text=f"{k}").pack(side="left")
                ttk.Label(rowtxt, text=str(v)).pack(side="right")

    # ---------- Renderers: Overview ----------

    def _g_line_informes_por_mes(self, df):
        if df.empty or df["_fecha_informe"].isna().all():
            return None
        ser = df.dropna(subset=["_fecha_informe"]).set_index("_fecha_informe").resample("MS").size()
        fig = Figure(figsize=(5.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(ser.index, ser.values, marker="o")
        ax.set_title("Informes por mes")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Conteo")
        fig.tight_layout()
        return fig

    def _g_pie_malignidad(self, df):
        if "Malignidad" not in df.columns or df.empty:
            return None
        ser = df["Malignidad"].astype(str).str.upper().replace({"": "DESCONOCIDO"}).value_counts()
        if ser.empty: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(ser.values, labels=ser.index, autopct="%1.1f%%", startangle=90)
        ax.set_title("Distribución de Malignidad")
        fig.tight_layout()
        return fig

    def _g_bar_top_servicio(self, df, top=12):
        if "Servicio" not in df.columns or df.empty:
            return None
        ser = df["Servicio"].astype(str).value_counts().head(top)
        if ser.empty: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(ser.index, ser.values)
        ax.set_title(f"Top Servicios (n={ser.sum()})")
        ax.set_ylabel("Informes")
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        fig.tight_layout()
        return fig

    def _g_bar_top_organo(self, df, top=12):
        # soporta tanto columna Excel como IHQ_ORGANO
        col = "Organo" if "Organo" in df.columns else ("IHQ_ORGANO" if "IHQ_ORGANO" in df.columns else None)
        if not col: return None
        ser = df[col].astype(str).replace({"": "No especificado"}).value_counts().head(top)
        if ser.empty: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(ser.index, ser.values)
        ax.set_title("Top Órganos")
        ax.set_ylabel("Informes")
        ax.tick_params(axis="x", rotation=30, labelsize=8)
        fig.tight_layout()
        return fig

    # ---------- Renderers: Biomarcadores ----------

    def _g_hist_ki67(self, df):
        col = "IHQ_KI-67" if "IHQ_KI-67" in df.columns else None
        if not col: return None
        
        # Limpiar y convertir los datos
        raw_data = df[col].astype(str)  # Convertir todo a string primero
        # Remover espacios y reemplazar cadenas vacías con NaN
        clean_data = raw_data.str.strip().replace('', pd.NA)
        # Remover el símbolo % y convertir a numérico
        numeric_data = clean_data.str.replace('%', '', regex=False)
        s = pd.to_numeric(numeric_data, errors="coerce").dropna()
        
        if s.empty: 
            return None
            
        fig = Figure(figsize=(5.6, 3.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.hist(s.values, bins=min(12, len(s.unique())))  # Ajustar bins si hay pocos datos únicos
        ax.set_title("Ki-67 (%)")
        ax.set_xlabel("%")
        ax.set_ylabel("Frecuencia")
        fig.tight_layout()
        return fig

    def _g_bar_her2(self, df):
        col = "IHQ_HER2" if "IHQ_HER2" in df.columns else None
        if not col: return None
        order = ["0", "1+", "2+", "3+", "NEGATIVO", "POSITIVO"]
        ser = df[col].astype(str).str.upper().value_counts()
        ser = ser.reindex(order, fill_value=0) if any(k in ser.index for k in order) else ser
        if ser.sum() == 0: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.bar(ser.index, ser.values)
        ax.set_title("HER2 (score)")
        ax.set_ylabel("Informes")
        fig.tight_layout()
        return fig

    def _g_bar_re_rp(self, df):
        cols = [c for c in ["IHQ_RECEPTOR_ESTROGENOS", "IHQ_RECEPTOR_PROGESTERONA"] if c in df.columns]
        if not cols: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        data = []
        labels = []
        for c in cols:
            ser = df[c].astype(str).str.upper().replace({"": "ND"}).value_counts()
            data.append(ser)
            labels.append(c.replace("IHQ_", ""))
        # Normaliza categorías
        cats = sorted(set().union(*[d.index for d in data]))
        mat = np.array([[d.get(k, 0) for k in cats] for d in data])
        for i, row in enumerate(mat):
            ax.bar(np.arange(len(cats))+i*0.35, row, width=0.35, label=labels[i])
        ax.set_xticks(np.arange(len(cats))+0.35/2)
        ax.set_xticklabels(cats, rotation=0)
        ax.set_title("RE / RP (estado)")
        ax.legend()
        fig.tight_layout()
        return fig

    def _g_bar_pdl1(self, df):
        # intenta TPS o CPS
        for col in ["IHQ_PDL-1", "IHQ_PDL1_TPS", "IHQ_PDL1_CPS"]:
            if col in df.columns:
                s = df[col].astype(str)
                break
        else:
            return None
        ser = s.replace({"": "ND"}).value_counts()
        if ser.empty: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.bar(ser.index, ser.values)
        ax.set_title("PD-L1")
        ax.set_ylabel("Informes")
        ax.tick_params(axis="x", rotation=0)
        fig.tight_layout()
        return fig

    # ---------- Renderers: Tiempos ----------

    def _g_box_tiempo_proceso(self, df):
        f_ing = pd.to_datetime(df.get("Fecha de ingreso (2. Fecha de la muestra)", ""), dayfirst=True, errors="coerce")
        f_inf = pd.to_datetime(df.get("Fecha Informe", df.get("Fecha de informe", "")), dayfirst=True, errors="coerce")
        dias = (f_inf - f_ing).dt.days.dropna()
        if dias.empty: return None
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.boxplot(dias.values, vert=True)
        ax.set_title("Tiempo de proceso (días)")
        fig.tight_layout()
        return fig

    def _g_line_throughput_semana(self, df):
        if df.empty or df["_fecha_informe"].isna().all(): return None
        ser = df.dropna(subset=["_fecha_informe"]).set_index("_fecha_informe").resample("W-MON").size()
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.plot(ser.index, ser.values, marker="o")
        ax.set_title("Throughput semanal")
        ax.set_xlabel("Semana")
        ax.set_ylabel("Informes")
        fig.tight_layout()
        return fig

    def _g_scatter_edad_ki67(self, df):
        if "Edad" not in df.columns: return None
        x = pd.to_numeric(df["Edad"], errors="coerce")
        
        # Limpiar los datos Ki-67 igual que en _g_hist_ki67
        if "IHQ_KI-67" in df.columns:
            raw_ki67 = df["IHQ_KI-67"].astype(str).str.strip().replace('', pd.NA)
            clean_ki67 = raw_ki67.str.replace('%', '', regex=False)
            y = pd.to_numeric(clean_ki67, errors="coerce")
        else:
            y = pd.Series(np.nan, index=df.index)
            
        m = x.notna() & y.notna()
        if not m.any(): 
            return None
            
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.scatter(x[m], y[m], alpha=0.6)
        ax.set_title("Edad vs Ki-67")
        ax.set_xlabel("Edad")
        ax.set_ylabel("Ki-67 (%)")
        fig.tight_layout()
        return fig

    # ---------- Renderers: Calidad ----------

    def _g_bar_missingness(self, df):
        cols = [
            "Servicio", "Malignidad", "Patologo",
            "Organo", "IHQ_HER2", "IHQ_KI-67"
        ]
        present = [c for c in cols if c in df.columns]
        if not present: return None
        miss = df[present].isna().mean().sort_values(ascending=False)
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.bar(miss.index, (miss.values*100.0))
        ax.set_title("Campos vacíos (%)")
        ax.set_ylabel("% vacío")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        return fig

    def _g_bar_top_responsables(self, df, top=10):
        col = "Patologo"
        if col not in df.columns: return None
        ser = df[col].astype(str).value_counts().head(top)
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.bar(ser.index, ser.values)
        ax.set_title("Productividad por responsable (Top)")
        ax.set_ylabel("Informes")
        ax.tick_params(axis="x", rotation=25)
        fig.tight_layout()
        return fig

    def _g_bar_largos_texto(self, df):
        col = "Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)"
        if col not in df.columns: return None
        s = df[col].astype(str).str.len()
        bins = [0, 50, 150, 300, 600, 1200, np.inf]
        ser = pd.cut(s, bins=bins, labels=["<50", "50–150", "150–300", "300–600", "600–1200", "1200+"], include_lowest=True).value_counts().sort_index()
        fig = Figure(figsize=(5.6, 3.2), dpi=100); ax = fig.add_subplot(111)
        ax.bar(ser.index.astype(str), ser.values)
        ax.set_title("Longitud del diagnóstico (bins)")
        ax.set_ylabel("Informes")
        fig.tight_layout()
        return fig

    # ---------- Comparador parametrizable ----------

    def _build_comparator(self, tab, df):
        # Controles
        ctrl = ttk.Frame(tab)
        ctrl.grid(row=0, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")

        dims = [c for c in ["Servicio", "Patologo", "Malignidad", "Organo"] if c in df.columns]
        mets = [c for c in ["IHQ_KI-67"] if c in df.columns]  # se pueden añadir más numéricas

        self._compare_controls["dim"] = tk.StringVar(value=dims[0] if dims else "")
        self._compare_controls["agg"] = tk.StringVar(value="conteo")
        self._compare_controls["met"] = tk.StringVar(value=mets[0] if mets else "")

        row = ttk.Frame(ctrl, padding=10, relief="solid", borderwidth=1)
        row.pack(fill="x", padx=4, pady=4)
        ttk.Label(row, text="Dimensión:").pack(side="left", padx=6)
        ttk.Combobox(row, values=dims or [""], textvariable=self._compare_controls["dim"]).pack(side="left", padx=6)
        ttk.Label(row, text="Agregador:").pack(side="left", padx=6)
        ttk.Combobox(row, values=["conteo", "promedio"], textvariable=self._compare_controls["agg"]).pack(side="left", padx=6)
        ttk.Label(row, text="Métrica:").pack(side="left", padx=6)
        ttk.Combobox(row, values=mets or [""], textvariable=self._compare_controls["met"]).pack(side="left", padx=6)
        ttk.Button(row, text="Aplicar", command=lambda: self._chart_in(tab, 1, 0, lambda: self._g_compare(df), "Comparación de Datos", df)).pack(side="left", padx=10)

        # Gráfico inicial
        self._chart_in(tab, 1, 0, lambda: self._g_compare(df), "Comparación de Datos", df)

    def _g_compare(self, df):
        dim = self._compare_controls["dim"].get()
        agg = self._compare_controls["agg"].get()
        met = self._compare_controls["met"].get()
        if not dim or df.empty: return None

        fig = Figure(figsize=(11.6, 3.2), dpi=100); ax = fig.add_subplot(111)

        if agg == "conteo":
            ser = df[dim].astype(str).value_counts()
            ax.bar(ser.index, ser.values)
            ax.set_title(f"Conteo por {dim}")
            ax.tick_params(axis="x", rotation=25)
        else:
            if not met or met not in df.columns:
                return None
            s = pd.to_numeric(df[met], errors="coerce")
            grp = df.assign(_metric=s).groupby(dim)["_metric"].mean().dropna()
            ax.bar(grp.index, grp.values)
            ax.set_title(f"Promedio de {met} por {dim}")
            ax.tick_params(axis="x", rotation=25)

        fig.tight_layout()
        return fig

    # =========================
    # Funcionalidad
    # =========================
    def log_to_widget(self, message):
        """Log seguro que funciona con y sin log_textbox"""
        try:
            if hasattr(self, 'log_textbox') and self.log_textbox:
                self.log_textbox.configure(state="normal")
                self.log_textbox.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
                self.log_textbox.see("end")
                self.log_textbox.configure(state="disabled")
            else:
                # Fallback a logging normal si no hay widget
                import logging
                logging.info(message)
        except Exception as e:
            # Si falla, usar logging como último recurso
            import logging
            logging.info(f"{message} (log_to_widget error: {e})")

    def select_files(self):
        self.pdf_files = filedialog.askopenfilenames(title="Seleccione archivos PDF", filetypes=[("PDF", "*.pdf")])
        if self.pdf_files:
            self.log_to_widget(f"Seleccionados {len(self.pdf_files)} archivos.")
            self.start_button.configure(state="normal")
            self.set_status(f"{len(self.pdf_files)} archivos listos.")
        else:
            self.log_to_widget("Selección cancelada.")
            self.start_button.configure(state="disabled")
            self.set_status("Selección cancelada.")

    def start_processing(self):
        if not self.pdf_files:
            messagebox.showwarning("Advertencia", "Por favor, seleccione archivos PDF primero.")
            return

        self.start_button.configure(state="disabled")
        self.select_files_button.configure(state="disabled")
        self.log_to_widget("=" * 50)
        self.log_to_widget("INICIANDO PROCESAMIENTO...")
        self.set_status("Procesando… esto puede tardar según el tamaño de los PDFs.")

        threading.Thread(target=self.processing_thread, daemon=True).start()

    def processing_thread(self):
        try:
            # FORZAR RECARGA DEL MÓDULO para asegurar que tenemos las últimas modificaciones
            import importlib
            import core.unified_extractor
            importlib.reload(core.unified_extractor)

            # === USAR PROCESAMIENTO CON AUDITORÍA IA INTEGRADA ===
            self.log_to_widget("\n" + "="*60)
            self.log_to_widget("🔄 CARGANDO SISTEMA DE AUDITORÍA IA...")
            self.log_to_widget("="*60)

            from core.process_with_audit import process_ihq_paths_with_audit, crear_callback_auditoria_para_ui

            self.log_to_widget("✅ Módulos de auditoría importados correctamente")

            output_dir = os.path.dirname(self.pdf_files[0])

            # Crear callback para auditoría IA
            self.log_to_widget("🔧 Configurando callback de auditoría IA...")
            callback_auditoria = crear_callback_auditoria_para_ui(self)
            self.log_to_widget("✅ Callback configurado")

            # Procesar con auditoría integrada
            self.log_to_widget("\n🚀 INICIANDO PROCESAMIENTO CON AUDITORÍA INTEGRADA...")
            self.log_to_widget("="*60)

            num_records = process_ihq_paths_with_audit(
                pdf_paths=self.pdf_files,
                output_dir=output_dir,
                ui_callback_auditoria=callback_auditoria,
                log_callback=self.log_to_widget
            )

            # Nota: El mensaje de éxito y el refresh se manejan en el callback de auditoría
            # Solo mostramos mensaje si no hay casos para auditar
            if num_records == 0:
                self.log_to_widget(f"⚠️ No se procesaron registros.")
                logging.warning("No se encontraron casos IHQ válidos en los PDFs seleccionados.")
            else:
                # El mensaje final se mostrará después de la auditoría
                self.log_to_widget(f"\n✅ Procesamiento completado: {num_records} registros")
                logging.info("Procesamiento completado - Auditando con IA...")

        except Exception as e:
            import traceback
            error_msg = f"ERROR: {e}\n{traceback.format_exc()}"
            self.log_to_widget(error_msg)
            logging.error(f"Error durante el procesamiento: {e}")
        finally:
            # V4.2.1 FIX: Usar after() para operaciones de UI desde thread
            def _restore_buttons():
                try:
                    self.start_button.configure(state="normal")
                    self.select_files_button.configure(state="normal")
                except Exception:
                    pass
            self.after(0, _restore_buttons)

    def refresh_data_and_table(self):
        """Actualizar datos y tabla desde la base de datos"""
        try:
            # V5.3.9.3: Usar logging en lugar de print (stdout puede estar cerrado)
            logging.info("🔄 Iniciando refresh de datos...")

            from core.database_manager import init_db, get_all_records_as_dataframe

            # V6.2.0: Comentado - init_db() ya se llama en ihq_processor antes del guardado
            # Llamarlo aquí (en refresh_data) causa que el UPDATE de relleno sobrescriba
            # valores recién insertados con N/A
            # init_db()

            # Cargar datos
            self.master_df = get_all_records_as_dataframe()

            # Ordenar por número de caso automáticamente
            if self.master_df is not None and not self.master_df.empty and "Numero de caso" in self.master_df.columns:
                self.master_df = self.master_df.sort_values(
                    by="Numero de caso",
                    ascending=True,
                    na_position='last'
                ).reset_index(drop=True)

            if self.master_df is not None and not self.master_df.empty:
                logging.info(f"📊 Datos cargados: {len(self.master_df)} registros")

                # Actualizar tabla solo si existe
                if hasattr(self, 'tree') and self.tree is not None:
                    self._populate_treeview(self.master_df)
                    logging.info("🗂️ Tabla actualizada")

                # Actualizar KPIs si existe el método
                try:
                    self._render_kpis(self.master_df)
                    logging.info("📈 KPIs actualizados")
                except:
                    pass

                # Actualizar estado con información inteligente
                footer_info = self._crear_footer_inteligente()
                self.set_status(footer_info)
                logging.info("✅ Refresh completado exitosamente")

            else:
                logging.warning("⚠️ No hay datos en la base de datos")
                self.set_status("⚠️ No hay datos en la base de datos")

        except Exception as e:
            error_msg = f"No se pudieron cargar los datos: {e}"
            logging.error(f"❌ Error en refresh: {error_msg}")

            # Solo mostrar error si no es un problema de UI
            try:
                if hasattr(self, 'tree'):  # Solo mostrar error si la UI está inicializada
                    messagebox.showerror("Error de Base de Datos", error_msg)
                self.set_status("❌ Error al cargar datos")
            except:
                logging.error("❌ Error mostrando mensaje de error")

    def _populate_treeview(self, df_to_display):
        """
        V5.3.8: Población de Sheet virtualizado (antes era Treeview)
        VENTAJA: Carga COMPLETA en <100ms para 1000+ filas × 88 columnas
        """
        # Verificar que el sheet exista
        if not hasattr(self, 'sheet') or self.sheet is None:
            return

        if df_to_display.empty:
            self.sheet.set_sheet_data([[]])  # Limpiar sheet
            self.sheet.headers([])
            return

        # V5.3.9.3: NO sobrescribir "Nombre Completo" si ya existe (creada en database_manager.py sin N/A)
        # Crear columna de Nombre Completo solo si NO existe
        if "Nombre Completo" not in df_to_display.columns and all(col in df_to_display.columns for col in ["Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido"]):
            # Fallback: Si por alguna razón no existe, crearla (pero normalmente ya existe)
            from core.unified_extractor import build_clean_full_name

            def crear_nombre_limpio_ui(row):
                try:
                    return build_clean_full_name(
                        str(row.get("Primer nombre", "")),
                        str(row.get("Segundo nombre", "")),
                        str(row.get("Primer apellido", "")),
                        str(row.get("Segundo apellido", ""))
                    )
                except:
                    return "N/A"

            df_to_display["Nombre Completo"] = df_to_display.apply(crear_nombre_limpio_ui, axis=1)

        # V5.3.7: Columnas reorganizadas para mejor rendimiento y visualización
        # Eliminadas: EPS (innecesaria), columnas duplicadas
        # Reordenadas: IHQ_ORGANO e IHQ_ESTUDIOS_SOLICITADOS antes de biomarcadores
        # V6.0.12: ELIMINADAS columnas sensibles (N. de identificación, Nombre Completo) por privacidad
        cols_to_show = [
            "Numero de caso",
            # "N. de identificación",  # ELIMINADA - Datos sensibles (privacidad)
            # "Nombre Completo",  # ELIMINADA - Datos sensibles (privacidad)
            # "EPS",  # ELIMINADA - No relevante para investigación
            "Procedimiento",
            "Organo",
            "Malignidad",
            "Diagnostico Coloracion",  # v6.1.0: Diagnóstico del Estudio M (Coloración)
            "Diagnostico Principal",
            "Factor pronostico",
            # "Descripcion macroscopica",  # V5.3.8: ELIMINADA - Texto muy largo, poco útil en tabla
            # "Descripcion microscopica",  # V5.3.8: ELIMINADA - Texto muy largo, poco útil en tabla
            # V5.3.7: IHQ_ORGANO e IHQ_ESTUDIOS_SOLICITADOS ANTES de biomarcadores
            "IHQ_ORGANO",
            "IHQ_ESTUDIOS_SOLICITADOS",
            # Biomarcadores principales
            "IHQ_HER2",
            "IHQ_KI-67",
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_PDL-1",
            "IHQ_P16_ESTADO",
            "IHQ_P16_PORCENTAJE",
            "IHQ_P40_ESTADO",
            "IHQ_E_CADHERINA",  # v6.0.3 - E-Cadherina
            # Biomarcadores adicionales v4.0/v4.1
            "IHQ_CK7",
            "IHQ_CROMOGRAMINA",
            "IHQ_DESMINA",
            "IHQ_LCA",
            "IHQ_CD11",
            "IHQ_MIOGENINA",
            "IHQ_MAMAGLOBINA",
            "IHQ_TIROGLOBULINA",
            "IHQ_CK34BETAE12",
            "IHQ_CK34BETA12",
            "IHQ_OCT4",
            "IHQ_PODOPLANINA",
            "IHQ_IDH",
            "IHQ_GPC3",
            "IHQ_AFP",
            "IHQ_IGD",
            "IHQ_BETACATENINA",
            "IHQ_ACTINA_MUSCULO_ESPECIFICA",
            "IHQ_MIELOPEROXIDASA",
            "IHQ_CD7",
            "IHQ_EBER",
            # V6.4.25: IHQ_CALRRETININA (typo v4.0) eliminado - duplicado de IHQ_CALRETININA (línea 4378)
            "IHQ_SYNAPTOFISINA",
            "IHQ_CKAE1E3",
            "IHQ_SINAPTOFISINA",
            "IHQ_CROMOGRANINA",
            "IHQ_CK56",
            "IHQ_CAM5",
            "IHQ_GLICOFORINA",
            "IHQ_TDT",
            "IHQ_ATRX",
            "IHQ_IDH1",
            "IHQ_CMYC",
            "IHQ_IGG4",
            "IHQ_IGG",
            "IHQ_MAMOGLOBINA",
            "IHQ_HEPATOCITO",  # V6.0.16: Auto-agregado
            "IHQ_CK19",
            "IHQ_CK20",
            "IHQ_CDX2",
            "IHQ_EMA",
            "IHQ_GATA3",
            "IHQ_SOX10",
            "IHQ_P53",
            "IHQ_TTF1",
            "IHQ_S100",
            "IHQ_VIMENTINA",
            "IHQ_CHROMOGRANINA",
            "IHQ_SYNAPTOPHYSIN",
            "IHQ_MELAN_A",
            # Marcadores CD
            "IHQ_CD2",
            "IHQ_CD3",
            "IHQ_CD5",
            "IHQ_CD10",
            "IHQ_CD20",
            "IHQ_CD30",
            "IHQ_CD34",
            "IHQ_CD38",
            "IHQ_CD45",
            "IHQ_CD56",
            "IHQ_CD61",
            "IHQ_CD68",
            "IHQ_CD117",
            "IHQ_CD138",
            "IHQ_KAPPA",
            "IHQ_LAMBDA",
            # V6.0.13: Biomarcadores para linfomas y mielomas
            "IHQ_BCL2",
            "IHQ_BCL6",
            "IHQ_MUM1", "IHQ_MUC1", "IHQ_MUC2"  # V6.4.43: MUC1 agregado,
            "IHQ_CD15",
            "IHQ_CD79A",
            "IHQ_ALK",
            # NUEVOS BIOMARCADORES v5.0 - CRÍTICOS PARA CASOS COMPLEJOS
            "IHQ_CKAE1AE3",
            "IHQ_NAPSIN",
            "IHQ_CDK4",
            "IHQ_MDM2",
            "IHQ_PAX5",
            "IHQ_ACTIN",
            # BIOMARCADORES ADICIONALES v5.1 - COMPLETAR CON TODAS LAS COLUMNAS DE BD
            "IHQ_PAX8",
            "IHQ_GFAP",
            # V6.5.83: IHQ_CAM52 eliminado (obsoleto, migrado a IHQ_CAM5)
            "IHQ_DOG1",
            "IHQ_H_CALDESMON",  # V6.1.2: Biomarcador IHQ250997 (tumor maligno indiferenciado)
            "IHQ_AML",  # V6.1.2: Biomarcador IHQ250997 (tumor maligno indiferenciado)
            "IHQ_HHV8",
            "IHQ_NEUN",
            "IHQ_P63",
            # V6.1.3: Biomarcador celulas mioepiteliales (IHQ250999) - CK5_6 ya existe en V5.3
            "IHQ_CALPONINA",
            "IHQ_BER_EP4",  # V6.0.12.1: Agregado BER-EP4 (Ep-CAM) - FIX IHQ250991
            "IHQ_WT1",
            # MARCADORES MMR (Mismatch Repair) - CRÍTICOS PARA CÁNCER COLORRECTAL
            "IHQ_MLH1",
            "IHQ_MSH2",
            "IHQ_MSH6",
            "IHQ_PMS2",
            # V5.3 - NUEVOS BIOMARCADORES (28 adicionales detectados en producción)
            "IHQ_CD23",
            "IHQ_CD4",
            "IHQ_CD8",
            "IHQ_CD99",
            "IHQ_CD1A",
            "IHQ_C4D",
            "IHQ_LMP1",
            "IHQ_CITOMEGALOVIRUS",
            "IHQ_SV40",
            "IHQ_CEA",
            "IHQ_CA19_9",
            "IHQ_CALRETININA",
            "IHQ_CK34BE12",
            "IHQ_CK5_6",
            "IHQ_HEPAR",
            "IHQ_GLIPICAN",
            "IHQ_ARGINASA",
            "IHQ_HMB45",
            "IHQ_PSA",
            "IHQ_INHIBINA",  # V6.4.60: Biomarcador hormonal
            "IHQ_RACEMASA",
            "IHQ_34BETA",
            "IHQ_B2",
            # V6.0.16 - Biomarcadores para linfomas (IHQ250988)
            "IHQ_SALL4",
            "IHQ_ALK1",
            # V5.3.7: Columnas de sistema al final
            "Estado Auditoria IA",  # V3.2.4
            "Fecha Ingreso Base de Datos",
        ]

        # Filtrar solo las columnas que existen en el DataFrame
        available_cols = [c for c in cols_to_show if c in df_to_display.columns]
        df_display = df_to_display[available_cols].copy()

        # Guardar DataFrame actual para ordenamiento
        self.current_displayed_df = df_display.copy()

        # V5.3.8: CONFIGURACIÓN DE SHEET - Una sola carga, virtualización automática
        # =========================================================================

        # Preparar encabezados (simplificados para mejor visualización)
        headers = [col.split("(")[0].strip() for col in df_display.columns]

        # Convertir DataFrame a lista de listas (formato Sheet)
        sheet_data = df_display.fillna("").astype(str).values.tolist()

        # PASO 1: Cargar TODOS los datos de una sola vez (ultra rápido)
        self.sheet.set_sheet_data(data=sheet_data, reset_col_positions=True, reset_row_positions=True, redraw=False)
        self.sheet.headers(newheaders=headers, index=None, reset_col_positions=False, show_headers_if_not_sheet=True, redraw=False)

        # PASO 1.5: Ordenamiento por encabezado YA está configurado en __init__ (línea 2357-2391)
        # NO bindear aquí para evitar acumulación de handlers duplicados

        # PASO 2: Configurar anchos de columnas
        column_widths = {}
        for idx, col in enumerate(df_display.columns):
            if "Numero de caso" in col:
                width = 120
            # V6.0.12: Columnas eliminadas (privacidad)
            # elif "Nombre Completo" in col:
            #     width = 250
            # elif "N. de identificación" in col:
            #     width = 120
            elif "Fecha" in col:
                width = 120
            elif "Procedimiento" in col:
                width = 200
            elif "Organo" in col:
                width = 200
            elif "Malignidad" in col:
                width = 100
            elif "Diagnostico Coloracion" in col:
                width = 300
            elif "Diagnostico Principal" in col:
                width = 300
            elif "Factor pronostico" in col:
                width = 200
            elif "Descripcion" in col:
                width = 350
            elif col.startswith("IHQ_"):
                width = 150
            elif "Estado Auditoria IA" in col:
                width = 150
            elif "Fecha Ingreso" in col:
                width = 180
            else:
                width = 150  # Default

            self.sheet.column_width(column=idx, width=width, only_set_if_too_small=False, redraw=False)

        # PASO 3: DIBUJAR DATOS INMEDIATAMENTE (no bloquear UI)
        # ====================================================
        # V4.2.1 FIX: Mostrar datos ANTES de calcular colores para evitar tabla en blanco
        self.sheet.refresh()

        # PASO 4: Aplicar colores de fila de forma diferida (no bloquea UI)
        # ================================================================
        self.after(100, lambda: self._apply_row_colors(df_display, sheet_data))

        # PASO 7: Actualizar también sheet_dashboard si existe
        if hasattr(self, 'sheet_dashboard') and self.sheet_dashboard is not None:
            try:
                self.sheet_dashboard.set_sheet_data(data=sheet_data, reset_col_positions=True, reset_row_positions=True, redraw=False)
                self.sheet_dashboard.headers(newheaders=headers, index=None, reset_col_positions=False, show_headers_if_not_sheet=True, redraw=False)

                # Aplicar anchos de columna
                for col_idx, width in column_widths.items():
                    self.sheet_dashboard.column_width(column=col_idx, width=width, only_set_if_too_small=False, redraw=False)

                self.sheet_dashboard.refresh()
                logging.debug("✅ sheet_dashboard actualizado")
            except Exception as e:
                logging.error(f"Error actualizando sheet_dashboard: {e}")

        # Actualizar KPIs en base a lo mostrado
        try:
            self._render_kpis(df_display)
        except Exception:
            pass

    def _apply_row_colors(self, df_display, sheet_data):
        """V4.2.1: Aplicar colores de fila de forma diferida para no bloquear UI.
        Se ejecuta via after() DESPUÉS de que los datos ya se muestran en la tabla."""
        try:
            estado_col_idx = None
            peticion_col_idx = None
            if "Estado Auditoria IA" in df_display.columns:
                estado_col_idx = list(df_display.columns).index("Estado Auditoria IA")
            if "Numero de caso" in df_display.columns:
                peticion_col_idx = list(df_display.columns).index("Numero de caso")

            # Calcular completitud en batch
            completitud_cache = {}
            if peticion_col_idx is not None:
                try:
                    from core.validation_checker import verificar_completitud_registro
                    numeros_peticion = df_display["Numero de caso"].dropna().unique()
                    for numero in numeros_peticion:
                        try:
                            analisis = verificar_completitud_registro(numero)
                            completitud_cache[numero] = analisis.get('completo', False)
                        except Exception:
                            completitud_cache[numero] = False
                except Exception as e:
                    logging.warning(f"Error calculando completitud: {e}")

            # Clasificar filas
            rows_auditoria_parcial = []
            rows_auditoria_completa = []
            rows_incompletos = []

            for row_idx, row_data in df_display.iterrows():
                sheet_row_idx = df_display.index.get_loc(row_idx)
                if estado_col_idx is not None:
                    estado = row_data.iloc[estado_col_idx]
                    if estado == "PARCIAL":
                        rows_auditoria_parcial.append(sheet_row_idx)
                        continue
                    elif estado == "COMPLETA":
                        rows_auditoria_completa.append(sheet_row_idx)
                        continue
                if peticion_col_idx is not None:
                    numero_peticion = row_data.iloc[peticion_col_idx]
                    if numero_peticion in completitud_cache:
                        if not completitud_cache[numero_peticion]:
                            rows_incompletos.append(sheet_row_idx)

            # Aplicar highlighting
            if rows_auditoria_parcial:
                self.sheet.highlight_rows(rows=rows_auditoria_parcial, bg="#FFF3CD", fg="#856404", redraw=False)
            if rows_auditoria_completa:
                self.sheet.highlight_rows(rows=rows_auditoria_completa, bg="#D4EDDA", fg="#155724", redraw=False)
            if rows_incompletos:
                self.sheet.highlight_rows(rows=rows_incompletos, bg="#FFE5E5", fg="#721C24", redraw=False)

            self.sheet.refresh()

            # Aplicar también al dashboard sheet
            if hasattr(self, 'sheet_dashboard') and self.sheet_dashboard is not None:
                if rows_incompletos:
                    self.sheet_dashboard.highlight_rows(rows=rows_incompletos, bg="#FFE5E5", fg="#721C24", redraw=False)
                    self.sheet_dashboard.refresh()

        except Exception as e:
            logging.warning(f"⚠️ Error aplicando colores de fila: {e}")

    def _sort_treeview(self, col, reverse):
        """
        V5.3.8: Ordenamiento optimizado para Sheet
        Ordena el DataFrame y recarga el Sheet (mega rápido con virtualización)
        """
        if not hasattr(self, 'current_displayed_df') or self.current_displayed_df is None:
            return

        from datetime import datetime as _dt

        def _sort_key(val):
            """Función de ordenamiento inteligente"""
            s = str(val).strip()
            # Intentar número
            try:
                return (0, float(s.replace(",", ".")))
            except:
                pass
            # Intentar fecha
            for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
                try:
                    return (1, _dt.strptime(s, fmt))
                except:
                    pass
            # Texto
            return (2, s.lower())

        # Ordenar DataFrame
        try:
            df_sorted = self.current_displayed_df.sort_values(
                by=col,
                ascending=not reverse,
                key=lambda x: x.map(_sort_key),
                na_position='last'
            )
            # Recargar Sheet con datos ordenados
            self._populate_treeview(df_sorted)
        except Exception as e:
            logging.warning(f"Error ordenando por {col}: {e}")

    def filter_tabla(self, *args):
        # Guardia: no filtrar si aún no hay datos cargados
        if not hasattr(self, 'master_df') or self.master_df is None or self.master_df.empty:
            return
        # Leer de ambas search vars (dashboard y visualizador)
        query = ""
        placeholder = getattr(self, '_search_placeholder', '').lower()
        if hasattr(self, 'search_var_dashboard'):
            q = self.search_var_dashboard.get().strip().lower()
            if q and q != placeholder:
                query = q
        if not query and hasattr(self, 'search_var'):
            q = self.search_var.get().strip().lower()
            if q and q != placeholder:
                query = q
        if not query:
            self._populate_treeview(self.master_df)
            return

        df = self.master_df.copy()
        if df.empty:
            self._populate_treeview(df)
            return
            
        search_cols = ["Numero de caso", "Primer nombre", "Primer apellido"]
        for col in search_cols:
            if col in df.columns:
                df[col] = df[col].astype(str)
        
        # Inicializar máscara con todos False
        mask = pd.Series([False] * len(df), index=df.index)
        
        if search_cols[0] in df.columns:
            mask |= df[search_cols[0]].str.lower().str.contains(query, na=False)
        if search_cols[1] in df.columns:
            mask |= df[search_cols[1]].str.lower().str.contains(query, na=False)
        if search_cols[2] in df.columns:
            mask |= df[search_cols[2]].str.lower().str.contains(query, na=False)
        
        self._populate_treeview(df[mask])

    def _on_search_focus_in(self, entry_widget, string_var):
        """Limpiar placeholder al enfocar el campo de búsqueda"""
        if string_var.get() == self._search_placeholder:
            string_var.set("")

    def _on_search_focus_out(self, entry_widget, string_var):
        """Restaurar placeholder si el campo queda vacío"""
        if not string_var.get().strip():
            string_var.set(self._search_placeholder)

    def mostrar_detalle_registro(self, event):
        # v6.0.15: Extraer TODAS las filas seleccionadas del evento y del Sheet
        logging.info("=" * 60)
        logging.info("mostrar_detalle_registro: EVENTO DISPARADO")

        # Extraer filas de selection_boxes del evento (captura multi-selección)
        event_rows = set()
        if isinstance(event, dict):
            # Extraer de selection_boxes (contiene TODOS los rangos seleccionados)
            sel_boxes = event.get('selection_boxes', {})
            for box in sel_boxes:
                # box es Box_nt(from_r, from_c, upto_r, upto_c)
                if hasattr(box, 'from_r') and hasattr(box, 'upto_r'):
                    for r in range(box.from_r, box.upto_r):
                        event_rows.add(r)
                elif isinstance(box, (tuple, list)) and len(box) >= 4:
                    for r in range(box[0], box[2]):
                        event_rows.add(r)

            # Fallback: extraer de 'selected'
            if not event_rows:
                selected_info = event.get('selected', None)
                if selected_info and hasattr(selected_info, 'row') and selected_info.row is not None:
                    event_rows.add(selected_info.row)

        if event_rows:
            logging.info(f"mostrar_detalle_registro: {len(event_rows)} fila(s) desde evento: {sorted(event_rows)}")

        # Obtener selección del Sheet (puede tener más filas si toggle_select)
        try:
            selection = self.tree.selection()
            logging.info(f"self.tree.selection() retornó: {selection}")

            # Combinar: si el evento tiene filas Y selection también, usar la unión
            if event_rows and selection:
                combined = set(selection) | event_rows
                selection = sorted(combined)
            elif event_rows and not selection:
                selection = sorted(event_rows)

            # Guardar TODAS las filas seleccionadas (para multi-selección en auditoría)
            if selection and len(selection) > 0:
                self.ultima_seleccion = selection[0]
                self._ultimas_filas_seleccionadas = list(selection)
                logging.info(f"💾 Guardada selección: {len(selection)} fila(s): {selection}")
        except Exception as e:
            logging.error(f"ERROR al llamar self.tree.selection(): {e}", exc_info=True)

        # v6.0.12: Actualizar estado de TODOS los botones cuando hay selección
        logging.info("Llamando a _update_export_button_state()...")
        self._update_export_button_state()

        logging.info("Llamando a _update_audit_buttons_state()...")
        self._update_audit_buttons_state()

        logging.info("=" * 60)

        # NUEVO: Si el panel de detalles está abierto, actualizarlo con el nuevo registro
        try:
            if (hasattr(self.export_system, 'details_panel') and
                self.export_system.details_panel.winfo_exists() and
                selection and len(selection) > 0):
                logging.info("Panel de detalles abierto - actualizando contenido...")
                self.export_system._update_details_panel_content(selection[0])
        except Exception as e:
            logging.error(f"Error al actualizar panel de detalles: {e}")

        # El panel de detalles ahora es flotante y se maneja en el export_system
        # Aquí solo manejamos la selección

    def _export_full_database(self):
        """Exportar toda la base de datos usando el sistema mejorado"""
        try:
            self.export_system.export_full_database()
        except Exception as e:
            messagebox.showerror("Error de Exportación", f"Error al exportar la base de datos:\n{str(e)}")

    # ================================================================
    #  RESUMEN IA — Análisis profesional de la base de datos
    # ================================================================

    def _generar_resumen_ia(self):
        """Genera un resumen profesional de la BD usando IA (en hilo aparte)."""
        if not hasattr(self, 'master_df') or self.master_df is None or self.master_df.empty:
            messagebox.showwarning("Sin Datos", "No hay datos en la base de datos para analizar.")
            return

        # Mostrar overlay mientras se genera
        self._resumen_ia_overlay = tk.Toplevel(self)
        overlay = self._resumen_ia_overlay
        overlay.title("Generando Resumen IA...")
        overlay.transient(self)
        overlay.grab_set()
        overlay.resizable(False, False)
        overlay.protocol("WM_DELETE_WINDOW", lambda: None)

        w, h = 420, 140
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        overlay.geometry(f"{w}x{h}+{x}+{y}")

        frame = ttk.Frame(overlay, padding=25)
        frame.pack(fill=BOTH, expand=True)
        ttk.Label(frame, text="📊 Generando resumen con IA…", font=("Segoe UI", 13, "bold")).pack(pady=(0, 8))
        ttk.Label(frame, text="Esto puede tomar varios minutos con modelos locales.", font=("Segoe UI", 10)).pack()
        pb = ttk.Progressbar(frame, mode="indeterminate", bootstyle="info-striped")
        pb.pack(fill=X, pady=(10, 0))
        pb.start(15)

        # Resultado compartido entre hilos
        self._resumen_ia_result = {"done": False, "texto": "", "error": None}

        thread = threading.Thread(target=self._resumen_ia_worker, daemon=True)
        thread.start()
        self.after(500, self._poll_resumen_ia)

    def _compilar_estadisticas(self):
        """Compila estadísticas locales del DataFrame para enviar a la IA."""
        df = self.master_df.copy()
        stats = {}

        stats["total_casos"] = len(df)
        stats["nota"] = "Todos los casos son estudios de Inmunohistoquímica (IHQ)"

        # Rango de fechas
        for col in ["Fecha Informe", "Fecha de informe", "Fecha de ingreso"]:
            if col in df.columns:
                fechas = pd.to_datetime(df[col], dayfirst=True, errors="coerce").dropna()
                if not fechas.empty:
                    stats["fecha_min"] = fechas.min().strftime("%d/%m/%Y")
                    stats["fecha_max"] = fechas.max().strftime("%d/%m/%Y")
                    break

        # Distribución de malignidad
        if "Malignidad" in df.columns:
            stats["malignidad"] = df["Malignidad"].fillna("SIN DATO").value_counts().head(10).to_dict()

        # Distribución por órgano — NORMALIZACIÓN CANÓNICA
        # Usa core/normalizador_organos para agrupar por categoría anatómica
        # real (MAMA, COLON, MEDULA OSEA, etc.) en lugar de strings literales.
        # Prefiere IHQ_ORGANO (más limpio) sobre Organo.
        from core.normalizador_organos import (
            normalizar_organo,
            elegir_columna_organo,
        )
        col_organo = elegir_columna_organo(df.columns)
        if col_organo is not None:
            serie_norm = df[col_organo].apply(normalizar_organo)
            total_validos = int((serie_norm != "SIN DATO").sum())
            top = serie_norm.value_counts()
            # Excluir SIN DATO del ranking principal
            top_sin_nulos = top[top.index != "SIN DATO"]
            stats["organos_normalizados"] = top_sin_nulos.head(20).to_dict()
            stats["organos_total_con_dato"] = total_validos
            stats["organos_columna_fuente"] = col_organo
            stats["organos_categorias_distintas"] = int(top_sin_nulos.shape[0])
        # Distribución por procedimiento — filtrar "INMUNOHISTOQUIMICA" (no es procedimiento quirúrgico)
        # V6.6.8: Agregar totales y agrupación por tipo (biopsia/cirugía/etc.)
        if "Procedimiento" in df.columns:
            procs = df["Procedimiento"].fillna("SIN DATO").astype(str).str.upper().str.strip()
            procs = procs[~procs.isin(["INMUNOHISTOQUIMICA", "INMUNOHISTOQUÍMICA"])]
            procs_validos = procs[procs != "SIN DATO"]
            stats["procedimientos"] = procs_validos.value_counts().head(10).to_dict()
            stats["procedimientos_total_con_dato"] = int(len(procs_validos))
            stats["procedimientos_categorias_distintas"] = int(procs_validos.nunique())
            # Agrupar por tipo clínico: BIOPSIA / CIRUGIA / PUNCION
            def _clasificar_proc(p: str) -> str:
                p = p.upper()
                if any(k in p for k in ["BIOPSIA", "BX ", "BIOP"]):
                    return "BIOPSIA"
                if any(k in p for k in ["ECTOMIA", "ECTOMÍA", "RESECCION", "RESECCIÓN",
                                         "CIRUG", "MASTECTOM", "CUADRANTECT",
                                         "HEMICOLECT", "APENDICECT", "NEFRECT",
                                         "HISTERECT", "TIROIDECT", "PROSTATECT",
                                         "GASTRECT", "SIGMOIDECT", "HEPATECT",
                                         "SALPINGOOFOR", "ESPLENECT", "LARINGECT"]):
                    return "CIRUGIA"
                if any(k in p for k in ["PUNCION", "PUNCIÓN", "ASPIRADO", "PAAF"]):
                    return "PUNCION/ASPIRADO"
                if "LEGRADO" in p or "CURETAJE" in p:
                    return "LEGRADO"
                return "OTRO"
            tipos = procs_validos.apply(_clasificar_proc)
            stats["procedimientos_por_tipo"] = tipos.value_counts().to_dict()

        # Diagnósticos — filtrar entradas genéricas que no son diagnósticos reales
        filtro_diag = ["ESTUDIO DE INMUNOHISTOQUÍMICA", "INMUNOHISTOQUÍMICA",
                       "ESTUDIO DE INMUNOHISTOQUIMICA", "INMUNOHISTOQUIMICA"]
        for diag_col in ["Diagnostico Principal", "Diagnostico Coloracion"]:
            if diag_col in df.columns:
                vals = df[diag_col].dropna().astype(str).str.strip()
                vals = vals[(vals != "") & (~vals.str.upper().isin([f.upper() for f in filtro_diag]))]
                if not vals.empty:
                    stats[f"top_{diag_col.lower().replace(' ', '_')}"] = vals.value_counts().head(10).to_dict()

        # Diagnósticos CATEGORIZADOS — agrupa los 883 diagnósticos literales
        # distintos en categorías clínicas (CARCINOMA DUCTAL DE MAMA,
        # ADENOCARCINOMA, LINFOMA, etc.). Esto refleja el volumen real
        # del HUV en lugar de strings literales fragmentados.
        # V6.6.8: Usar categorizar_diagnostico_con_organo para refinar diagnósticos
        # genéricos ("ADENOCARCINOMA SIN ORIGEN", "CARCINOMA OTRO") usando el campo
        # Organo del caso. Esto resuelve el feedback clínico: "Adenocarcinoma debe
        # especificar ubicación", "Carcinoma escamocelular debe aclarar órgano".
        from core.normalizador_diagnosticos import (
            categorizar_diagnostico,
            categorizar_diagnostico_con_organo,
        )
        from core.normalizador_organos import normalizar_organo as _norm_organo
        if "Diagnostico Principal" in df.columns:
            # Pasar diagnóstico + órgano canónico para inferencia contextual
            organo_col = col_organo if 'col_organo' in dir() and col_organo else None
            if organo_col is not None and organo_col in df.columns:
                organos_norm = df[organo_col].apply(_norm_organo)
                cat_serie = df.apply(
                    lambda row: categorizar_diagnostico_con_organo(
                        row["Diagnostico Principal"],
                        organos_norm.loc[row.name] if row.name in organos_norm.index else None
                    ),
                    axis=1
                )
            else:
                cat_serie = df["Diagnostico Principal"].apply(categorizar_diagnostico)
            cat_top = cat_serie.value_counts()

            # V6.6.9 FIX feedback clínico: separar DIAGNÓSTICOS ONCOLÓGICOS reales
            # (neoplasias benignas o malignas) de HALLAZGOS NO-NEOPLÁSICOS
            # (negativo para malignidad, muestra no representativa, gliosis,
            # rechazo trasplante, malformaciones, etc.). Antes todas estas
            # categorías aparecían mezcladas en "Diagnósticos Principales", lo
            # cual el patólogo correctamente señaló como incorrecto: "Negativo
            # para malignidad NO es un diagnóstico oncológico".
            CATEGORIAS_NO_NEOPLASICAS = {
                "NEGATIVO PARA MALIGNIDAD",
                "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA",
                "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO",
                "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)",
                "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)",
                "GLIOSIS / LESION REACTIVA SNC",
                "RECHAZO DE TRASPLANTE",
                "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
            }

            EXCLUIR_DEL_TOP = (CATEGORIAS_NO_NEOPLASICAS | {"SIN DATO", "OTRO / NO CATEGORIZADO"})

            # Diagnósticos oncológicos reales (para gráfico/tabla principal)
            cat_oncologico = cat_top[~cat_top.index.isin(EXCLUIR_DEL_TOP)]
            stats["diagnosticos_categorizados"] = cat_oncologico.head(20).to_dict()
            stats["diagnosticos_total_categorizado"] = int(cat_oncologico.sum())

            # Hallazgos NO neoplásicos (separados, para sección aparte)
            hallazgos_no_neo = cat_top[cat_top.index.isin(CATEGORIAS_NO_NEOPLASICAS)]
            stats["hallazgos_no_neoplasicos"] = hallazgos_no_neo.to_dict()
            stats["hallazgos_no_neoplasicos_total"] = int(hallazgos_no_neo.sum())

            # Métricas de control
            stats["diagnosticos_otro_no_categorizado"] = int(cat_top.get("OTRO / NO CATEGORIZADO", 0))
            stats["diagnosticos_estudio_ihq_sin_dx"] = int(cat_top.get("ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)", 0))
            stats["diagnosticos_sin_dato"] = int(cat_top.get("SIN DATO", 0))

        # Biomarcadores principales — top 15, valores compactos
        bio_cols = [c for c in df.columns if c.startswith("IHQ_")]
        # Excluir columnas auxiliares (no son biomarcadores clínicos)
        excluir = {"IHQ_ORGANO", "IHQ_ESTUDIOS_SOLICITADOS"}
        bio_cols = [c for c in bio_cols if c not in excluir]
        bio_counts = {}
        for bc in bio_cols:
            serie = df[bc].dropna().astype(str).str.strip()
            serie = serie[(serie != "") & (serie.str.upper() != "N/A") & (serie.str.upper() != "NO MENCIONADO")]
            if len(serie) > 0:
                bio_counts[bc] = len(serie)
        top_bio = sorted(bio_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        bio_summary = {}
        for bc, count in top_bio:
            serie = df[bc].dropna().astype(str).str.strip()
            serie = serie[(serie != "") & (serie.str.upper() != "N/A") & (serie.str.upper() != "NO MENCIONADO")]
            bio_summary[bc] = {
                "n": count,
                "top": serie.value_counts().head(3).to_dict()
            }
        if bio_summary:
            stats["biomarcadores_top15"] = bio_summary
        stats["total_biomarcadores_distintos"] = len(bio_counts)

        # Paneles más solicitados (estudios solicitados)
        if "IHQ_ESTUDIOS_SOLICITADOS" in df.columns:
            estudios = df["IHQ_ESTUDIOS_SOLICITADOS"].dropna().astype(str).str.strip()
            estudios = estudios[(estudios != "") & (estudios.str.upper() != "N/A")]
            if not estudios.empty:
                stats["paneles_ihq_solicitados"] = estudios.value_counts().head(10).to_dict()

        # Servicio solicitante — filtrar N/A y SIN DATO
        # V6.6.8 FIX: Agregar totales para que la IA sepa cuántos casos hay en
        # total y cuántos servicios distintos. Antes solo enviaba top 10 sin
        # contexto, generando reportes que aparentaban no sumar al total.
        if "Servicio" in df.columns:
            servicios = df["Servicio"].fillna("").astype(str).str.strip()
            servicios = servicios[(servicios != "") & (servicios.str.upper() != "N/A") & (servicios.str.upper() != "SIN DATO")]
            if not servicios.empty:
                stats["servicios"] = servicios.value_counts().head(10).to_dict()
                stats["servicios_total_con_dato"] = int(len(servicios))
                stats["servicios_categorias_distintas"] = int(servicios.nunique())

        return stats

    def _resumen_ia_worker(self):
        """Hilo: compila estadísticas y llama a la IA."""
        import json
        try:
            stats = self._compilar_estadisticas()
            # Guardamos las estadísticas crudas para el dashboard de gráficos
            self._resumen_ia_result["stats"] = stats
            # JSON compacto (sin indent) para reducir tokens de prompt
            stats_json = json.dumps(stats, ensure_ascii=False, separators=(",", ":"))

            system_prompt = (
                "/no_think\n"
                "Eres analista clínico-oncológico del HUV. Recibirás estadísticas "
                "PRE-CALCULADAS y EXACTAS. NO debes recalcular ni redondear. "
                "Reglas obligatorias:\n"
                "1) Usa SOLO los números provistos. Cita conteos exactos.\n"
                "2) Para 'Distribución Anatómica' usa el campo 'organos_normalizados' "
                "(ya unificado: MAMA agrupa todas las variantes/lateralidades, "
                "COLON incluye recto/sigmoide, etc.). Indica el total con dato "
                "('organos_total_con_dato') y el número de categorías distintas.\n"
                "3) Para 'Diagnósticos Principales' usa SIEMPRE 'diagnosticos_categorizados' "
                "que contiene SOLO diagnósticos ONCOLÓGICOS reales (neoplasias benignas "
                "o malignas: CARCINOMA DUCTAL DE MAMA, ADENOCARCINOMA COLORRECTAL, LINFOMA, "
                "TIMOMA, MENINGIOMA, etc.). El total real de casos categorizados como "
                "diagnóstico oncológico está en 'diagnosticos_total_categorizado'.\n"
                "3B) IMPORTANTE — los HALLAZGOS NO-NEOPLÁSICOS se reportan APARTE en "
                "'hallazgos_no_neoplasicos' (negativo para malignidad, muestra no "
                "representativa, hallazgo histológico normal, resultado IHQ sin dx, "
                "gliosis, rechazo de trasplante, malformación, etc.). NO los mezcles "
                "en la lista de Diagnósticos Principales — son categorías clínicas "
                "DIFERENTES (no son neoplasias). Crea una sección separada llamada "
                "'Hallazgos No-Neoplásicos / Casos sin diagnóstico oncológico' usando "
                "'hallazgos_no_neoplasicos_total' y la distribución detallada.\n"
                "3C) NO uses 'top_diagnostico_principal' como fuente principal: solo "
                "cítalo como ejemplo del literal más frecuente. Reporta "
                "'diagnosticos_estudio_ihq_sin_dx' y 'diagnosticos_otro_no_categorizado' "
                "como métricas de control de calidad.\n"
                "4) Calcula porcentajes sobre 'total_casos' o el denominador "
                "explícito. Muestra siempre el N usado.\n"
                "5) Para biomarcadores: 'biomarcadores_top15' es un dict {marcador: "
                "{n: <casos evaluados>, top: {valor: conteo}}}. NO sumes los 'n' como "
                "si fueran casos únicos: un mismo paciente aparece en varios marcadores. "
                "El total de marcadores distintos está en 'total_biomarcadores_distintos'.\n"
                "6) Si un dato no está en las estadísticas, escribe 'no disponible'.\n"
                "7) NO inventes diagnósticos, biomarcadores ni cifras.\n"
                "8) Para 'Servicios': usa 'servicios' (top 10), 'servicios_total_con_dato' "
                "(suma real) y 'servicios_categorias_distintas'. SIEMPRE indica que la "
                "tabla muestra los TOP 10 sobre el total real; si el top 10 no suma al "
                "total, la diferencia son servicios menos frecuentes.\n"
                "9) Para 'Procedimientos': usa 'procedimientos_por_tipo' (BIOPSIA/CIRUGIA/"
                "PUNCION/LEGRADO/OTRO) como categorización clínica primaria. Cita además "
                "los top específicos de 'procedimientos' como ejemplos. Cualquier "
                "*ECTOMÍA (apendicectomía, mastectomía, hemicolectomía, etc.) ES una "
                "CIRUGÍA, no un diagnóstico.\n"
                "10) Para 'Diagnósticos': cuando una categoría sea 'ADENOCARCINOMA "
                "(SIN ORIGEN ESPECIFICADO)' o 'CARCINOMA (OTRO/INESPECIFICO)' o "
                "'CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)', explicar al lector "
                "que el patólogo NO especificó el subtipo en el texto del informe. "
                "Si aparecen, listar el órgano más frecuente asociado para dar contexto "
                "(usa 'organos_normalizados').\n\n"
                "Estructura del informe (Markdown español):\n"
                "1. Resumen Ejecutivo (volumen, periodo, hallazgos principales)\n"
                "2. Volumen y Temporalidad\n"
                "3. Malignidad (porcentajes con N sobre total_casos)\n"
                "4. Distribución Anatómica (top categorías canónicas)\n"
                "5. Diagnósticos Oncológicos Principales (SOLO neoplasias benignas/malignas, "
                "usar 'diagnosticos_categorizados')\n"
                "6. Hallazgos No-Neoplásicos (usar 'hallazgos_no_neoplasicos': negativos, "
                "muestras no representativas, hallazgos reactivos, etc.) — sección SEPARADA\n"
                "7. Biomarcadores (top 15 con N evaluados y resultado predominante)\n"
                "8. Servicios y Procedimientos (con totales y categorización por tipo)\n"
                "9. Observaciones clínicas (sin sobre-interpretar)"
            )

            from core.llm_client import LMStudioClient
            client = LMStudioClient(timeout=900)
            resultado = client.completar(
                prompt=f"Estadísticas IHQ del HUV:\n{stats_json}",
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=4000,
            )

            if resultado.get("exito"):
                self._resumen_ia_result["texto"] = resultado.get("respuesta", "Sin contenido.")
            else:
                self._resumen_ia_result["error"] = resultado.get("error", "Error desconocido de IA.")

        except Exception as e:
            self._resumen_ia_result["error"] = str(e)
        finally:
            self._resumen_ia_result["done"] = True

    def _poll_resumen_ia(self):
        """Polling main thread: espera a que el hilo de resumen IA termine."""
        if not self._resumen_ia_result["done"]:
            self.after(500, self._poll_resumen_ia)
            return

        # Cerrar overlay
        if hasattr(self, '_resumen_ia_overlay') and self._resumen_ia_overlay:
            self._resumen_ia_overlay.grab_release()
            self._resumen_ia_overlay.destroy()
            self._resumen_ia_overlay = None

        error = self._resumen_ia_result.get("error")
        if error:
            messagebox.showerror("Error Resumen IA", f"No se pudo generar el resumen:\n{error}")
            return

        texto = self._resumen_ia_result["texto"]
        stats = self._resumen_ia_result.get("stats", {})
        self._mostrar_ventana_resumen_ia(texto, stats)

    def _mostrar_ventana_resumen_ia(self, texto: str, stats: dict | None = None):
        """Muestra el resumen IA con dashboard: Informe + Gráficos + Tablas."""
        stats = stats or {}
        win = tk.Toplevel(self)
        win.title("📊 Resumen IA — Base de Datos IHQ")
        win.geometry("1200x800")
        win.transient(self)

        # ── Cabecera ──────────────────────────────────────────────
        top_frame = ttk.Frame(win, padding=10)
        top_frame.pack(fill=X)

        ttk.Label(
            top_frame,
            text="📊 Resumen Profesional generado por IA",
            font=("Segoe UI", 14, "bold"),
        ).pack(side=LEFT)

        ttk.Button(
            top_frame,
            text="💾 Exportar",
            command=lambda: self._exportar_resumen_ia(texto, stats, win),
            bootstyle="success",
        ).pack(side=RIGHT, padx=5)

        ttk.Button(
            top_frame,
            text="📋 Copiar",
            command=lambda: self._copiar_resumen_ia(texto, win),
            bootstyle="info",
        ).pack(side=RIGHT, padx=5)

        # ── KPI cards ─────────────────────────────────────────────
        kpi_frame = ttk.Frame(win, padding=(10, 0, 10, 10))
        kpi_frame.pack(fill=X)
        self._render_kpi_cards(kpi_frame, stats)

        # ── Notebook con pestañas ─────────────────────────────────
        notebook = ttk.Notebook(win)
        notebook.pack(fill=BOTH, expand=True, padx=10, pady=(0, 10))

        # Tab 1 — Informe IA (markdown con formato)
        tab_informe = ttk.Frame(notebook)
        notebook.add(tab_informe, text="📝 Informe IA")
        self._render_informe_markdown(tab_informe, texto)

        # Tab 2 — Gráficos (matplotlib)
        tab_graficos = ttk.Frame(notebook)
        notebook.add(tab_graficos, text="📊 Gráficos")
        self._render_graficos_dashboard(tab_graficos, stats)

        # Tab 3 — Tablas (Treeviews limpios)
        tab_tablas = ttk.Frame(notebook)
        notebook.add(tab_tablas, text="📋 Tablas")
        self._render_tablas_dashboard(tab_tablas, stats)

    # ──────────────────────────────────────────────────────────────
    # Helpers de presentación del Resumen IA
    # ──────────────────────────────────────────────────────────────

    def _render_kpi_cards(self, parent, stats: dict):
        """Tarjetas con métricas clave en la parte superior."""
        if not stats:
            return

        total = stats.get("total_casos", 0)
        malig = stats.get("malignidad", {}) or {}
        n_malig = sum(v for k, v in malig.items() if "MALIGN" in str(k).upper() and "BENIG" not in str(k).upper())
        # Si no se detectó por keyword, usa la primera clave
        if n_malig == 0 and malig:
            primera = next(iter(malig.keys()))
            if "MALIGN" in primera.upper() and "BENIG" not in primera.upper():
                n_malig = malig[primera]
        pct_malig = (n_malig / total * 100) if total else 0

        organos_dist = stats.get("organos_categorias_distintas", 0)
        bio_total = stats.get("total_biomarcadores_distintos", 0)
        dx_cat = stats.get("diagnosticos_total_categorizado", 0)

        cards = [
            ("Total casos", f"{total:,}", "primary"),
            ("% Malignos", f"{pct_malig:.1f}%", "danger"),
            ("Categorías anatómicas", f"{organos_dist}", "info"),
            ("Biomarcadores distintos", f"{bio_total}", "warning"),
            ("Diagnósticos categorizados", f"{dx_cat:,}", "success"),
        ]

        for titulo, valor, estilo in cards:
            card = ttk.Frame(parent, padding=10, bootstyle=estilo)
            card.pack(side=LEFT, fill=BOTH, expand=True, padx=4)
            ttk.Label(
                card, text=titulo, font=("Segoe UI", 9),
                bootstyle=f"inverse-{estilo}",
            ).pack(anchor="w")
            ttk.Label(
                card, text=valor, font=("Segoe UI", 18, "bold"),
                bootstyle=f"inverse-{estilo}",
            ).pack(anchor="w")

    def _render_informe_markdown(self, parent, texto: str):
        """Renderiza el markdown con tipografía y colores básicos."""
        text_frame = ttk.Frame(parent, padding=10)
        text_frame.pack(fill=BOTH, expand=True)

        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            padx=20,
            pady=15,
            relief="flat",
            borderwidth=0,
            spacing1=4,
            spacing3=4,
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        text_widget.pack(fill=BOTH, expand=True)

        # Tags de estilo
        text_widget.tag_configure("h1", font=("Segoe UI", 18, "bold"), foreground="#0d6efd",
                                  spacing1=12, spacing3=8)
        text_widget.tag_configure("h2", font=("Segoe UI", 14, "bold"), foreground="#198754",
                                  spacing1=10, spacing3=6)
        text_widget.tag_configure("h3", font=("Segoe UI", 12, "bold"), foreground="#6c757d",
                                  spacing1=8, spacing3=4)
        text_widget.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        text_widget.tag_configure("bullet", lmargin1=20, lmargin2=40)
        text_widget.tag_configure("table", font=("Consolas", 10), foreground="#212529")
        text_widget.tag_configure("hr", foreground="#dee2e6")

        # Parser sencillo de markdown línea a línea
        import re as _re
        for raw in texto.splitlines():
            linea = raw.rstrip()
            if linea.startswith("# "):
                text_widget.insert("end", linea[2:] + "\n", "h1")
            elif linea.startswith("## "):
                text_widget.insert("end", linea[3:] + "\n", "h2")
            elif linea.startswith("### "):
                text_widget.insert("end", linea[4:] + "\n", "h3")
            elif linea.strip() in {"---", "***"}:
                text_widget.insert("end", "─" * 80 + "\n", "hr")
            elif linea.lstrip().startswith(("* ", "- ")):
                text_widget.insert("end", "  • " + linea.lstrip()[2:] + "\n", "bullet")
            elif linea.startswith("|"):
                text_widget.insert("end", linea + "\n", "table")
            else:
                # Sustituye **negritas** por tag
                pos = 0
                for m in _re.finditer(r"\*\*(.+?)\*\*", linea):
                    text_widget.insert("end", linea[pos:m.start()])
                    text_widget.insert("end", m.group(1), "bold")
                    pos = m.end()
                text_widget.insert("end", linea[pos:] + "\n")

        text_widget.configure(state="disabled")

    def _render_graficos_dashboard(self, parent, stats: dict):
        """Tablero matplotlib con 4 gráficos principales."""
        if not stats:
            ttk.Label(parent, text="No hay estadísticas disponibles para graficar.",
                      font=("Segoe UI", 11)).pack(pady=40)
            return

        try:
            import matplotlib
            matplotlib.use("TkAgg")
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_tkagg import (
                FigureCanvasTkAgg, NavigationToolbar2Tk,
            )
        except Exception as e:  # matplotlib no disponible
            ttk.Label(
                parent,
                text=f"Matplotlib no disponible: {e}",
                font=("Segoe UI", 10),
            ).pack(pady=40)
            return

        fig = Figure(figsize=(12, 9), dpi=100, tight_layout=True)
        fig.patch.set_facecolor("#ffffff")

        # 1) Malignidad — pie
        ax1 = fig.add_subplot(2, 2, 1)
        malig = stats.get("malignidad", {}) or {}
        if malig:
            etiquetas = list(malig.keys())[:5]
            valores = [malig[k] for k in etiquetas]
            colores = ["#dc3545", "#198754", "#ffc107", "#6c757d", "#0dcaf0"][:len(etiquetas)]
            ax1.pie(valores, labels=etiquetas, autopct="%1.1f%%",
                    colors=colores, startangle=90, textprops={"fontsize": 9})
            ax1.set_title("Malignidad", fontsize=12, fontweight="bold")
        else:
            ax1.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            ax1.axis("off")

        # 2) Top órganos — barra horizontal
        ax2 = fig.add_subplot(2, 2, 2)
        organos = stats.get("organos_normalizados", {}) or {}
        if organos:
            top = list(organos.items())[:10]
            top.reverse()
            etq = [k for k, _ in top]
            val = [v for _, v in top]
            ax2.barh(etq, val, color="#0d6efd")
            ax2.set_title("Top 10 órganos (canónicos)", fontsize=12, fontweight="bold")
            ax2.tick_params(axis="y", labelsize=9)
            for i, v in enumerate(val):
                ax2.text(v, i, f" {v}", va="center", fontsize=8)
        else:
            ax2.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            ax2.axis("off")

        # 3) Top diagnósticos oncológicos (V6.6.9: solo neoplasias, sin hallazgos
        # no-neoplásicos como "negativo para malignidad")
        ax3 = fig.add_subplot(2, 2, 3)
        dx = stats.get("diagnosticos_categorizados", {}) or {}
        # Excluir "OTRO / NO CATEGORIZADO" del gráfico para ver categorías clínicas
        dx = {k: v for k, v in dx.items() if k != "OTRO / NO CATEGORIZADO"}
        if dx:
            top = list(dx.items())[:10]
            top.reverse()
            etq = [k[:40] + ("…" if len(k) > 40 else "") for k, _ in top]
            val = [v for _, v in top]
            ax3.barh(etq, val, color="#198754")
            ax3.set_title("Top 10 diagnósticos oncológicos", fontsize=12, fontweight="bold")
            ax3.tick_params(axis="y", labelsize=8)
            for i, v in enumerate(val):
                ax3.text(v, i, f" {v}", va="center", fontsize=8)
        else:
            ax3.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            ax3.axis("off")

        # 4) Top biomarcadores — barra horizontal
        ax4 = fig.add_subplot(2, 2, 4)
        bios = stats.get("biomarcadores_top15", {}) or {}
        if bios:
            items = sorted(bios.items(), key=lambda x: x[1].get("n", 0), reverse=True)[:10]
            items.reverse()
            etq = [k.replace("IHQ_", "")[:25] for k, _ in items]
            val = [v.get("n", 0) for _, v in items]
            ax4.barh(etq, val, color="#fd7e14")
            ax4.set_title("Top 10 biomarcadores (N evaluados)", fontsize=12, fontweight="bold")
            ax4.tick_params(axis="y", labelsize=9)
            for i, v in enumerate(val):
                ax4.text(v, i, f" {v}", va="center", fontsize=8)
        else:
            ax4.text(0.5, 0.5, "Sin datos", ha="center", va="center")
            ax4.axis("off")

        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=BOTH, expand=True, padx=8, pady=8)

        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=X, padx=8)
        toolbar = NavigationToolbar2Tk(canvas, toolbar_frame)
        toolbar.update()

    def _render_tablas_dashboard(self, parent, stats: dict):
        """Tablas claras con scroll para cada bloque del informe."""
        if not stats:
            ttk.Label(parent, text="No hay estadísticas disponibles.",
                      font=("Segoe UI", 11)).pack(pady=40)
            return

        # Scroll global
        canvas = tk.Canvas(parent, highlightthickness=0)
        vbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vbar.set)
        vbar.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)

        inner = ttk.Frame(canvas, padding=10)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_config(_e=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_config(e):
            canvas.itemconfigure(canvas_window, width=e.width)

        inner.bind("<Configure>", _on_inner_config)
        canvas.bind("<Configure>", _on_canvas_config)

        bloques = [
            ("🧬 Distribución anatómica", stats.get("organos_normalizados", {}),
             ("Órgano", "Casos")),
            ("🩺 Diagnósticos oncológicos (neoplasias)",
             stats.get("diagnosticos_categorizados", {}),
             ("Categoría neoplásica", "Casos")),
            ("📋 Hallazgos no-neoplásicos (separados)",
             stats.get("hallazgos_no_neoplasicos", {}),
             ("Categoría", "Casos")),
            ("⚕️ Procedimientos", stats.get("procedimientos", {}),
             ("Procedimiento", "Casos")),
            ("🏥 Servicios solicitantes", stats.get("servicios", {}),
             ("Servicio", "Casos")),
        ]

        for titulo, data, (col1, col2) in bloques:
            if not data:
                continue
            ttk.Label(inner, text=titulo, font=("Segoe UI", 12, "bold"),
                      bootstyle="primary").pack(anchor="w", pady=(10, 4))

            tv = ttk.Treeview(
                inner, columns=("c1", "c2"), show="headings",
                height=min(12, len(data)),
                bootstyle="primary",
            )
            tv.heading("c1", text=col1)
            tv.heading("c2", text=col2)
            tv.column("c1", anchor="w", width=400)
            tv.column("c2", anchor="e", width=100)
            for k, v in data.items():
                tv.insert("", "end", values=(k, v))
            tv.pack(fill=X, pady=(0, 6))

        # Bloque biomarcadores con N y resultado predominante
        bios = stats.get("biomarcadores_top15", {}) or {}
        if bios:
            ttk.Label(inner, text="🔬 Biomarcadores (top 15)",
                      font=("Segoe UI", 12, "bold"),
                      bootstyle="primary").pack(anchor="w", pady=(10, 4))
            tv = ttk.Treeview(
                inner, columns=("m", "n", "top"),
                show="headings",
                height=min(15, len(bios)),
                bootstyle="primary",
            )
            tv.heading("m", text="Biomarcador")
            tv.heading("n", text="N evaluados")
            tv.heading("top", text="Resultado predominante")
            tv.column("m", anchor="w", width=240)
            tv.column("n", anchor="e", width=110)
            tv.column("top", anchor="w", width=420)
            for marcador, info in sorted(bios.items(), key=lambda x: x[1].get("n", 0), reverse=True):
                top = info.get("top", {}) or {}
                if top:
                    primer_valor, primer_n = next(iter(top.items()))
                    resumen = f"{primer_valor} (N={primer_n})"
                else:
                    resumen = "—"
                tv.insert("", "end", values=(marcador, info.get("n", 0), resumen))
            tv.pack(fill=X, pady=(0, 6))

    def _exportar_resumen_ia(self, texto: str, stats: dict | None = None, parent=None):
        """Permite elegir entre Excel formateado o PDF profesional."""
        stats = stats or {}
        dlg = tk.Toplevel(parent or self)
        dlg.title("Exportar Resumen IA")
        dlg.geometry("420x200")
        dlg.transient(parent or self)
        dlg.grab_set()
        dlg.resizable(False, False)

        ttk.Label(
            dlg, text="¿En qué formato deseas exportar el resumen?",
            font=("Segoe UI", 11, "bold"), padding=15,
        ).pack()

        btn_frame = ttk.Frame(dlg, padding=10)
        btn_frame.pack(fill=BOTH, expand=True)

        def _hacer_excel():
            dlg.destroy()
            self._exportar_resumen_excel(texto, stats)

        def _hacer_pdf():
            dlg.destroy()
            self._exportar_resumen_pdf(texto, stats)

        ttk.Button(
            btn_frame, text="📊  Excel (.xlsx)\ncon tablas y gráficos",
            bootstyle="success", command=_hacer_excel, width=22,
        ).pack(side=LEFT, expand=True, padx=8, ipady=8)

        ttk.Button(
            btn_frame, text="📄  PDF\nInforme profesional",
            bootstyle="danger", command=_hacer_pdf, width=22,
        ).pack(side=LEFT, expand=True, padx=8, ipady=8)

    # ── Excel ─────────────────────────────────────────────────────────
    def _exportar_resumen_excel(self, texto: str, stats: dict):
        """Genera un .xlsx con KPIs, tablas formateadas y gráficos nativos."""
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filepath = filedialog.asksaveasfilename(
            title="Exportar Resumen IA — Excel",
            defaultextension=".xlsx",
            initialfile=f"Resumen_IA_HUV_{fecha_str}.xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not filepath:
            return

        try:
            from openpyxl import Workbook
            from openpyxl.styles import (
                Font, PatternFill, Alignment, Border, Side,
            )
            from openpyxl.chart import BarChart, PieChart, Reference
            from openpyxl.utils import get_column_letter
        except Exception as e:
            messagebox.showerror("Error", f"openpyxl no disponible: {e}")
            return

        wb = Workbook()

        # Estilos reutilizables
        azul_huv = "0D6EFD"
        verde_huv = "198754"
        gris_claro = "F1F3F5"
        thin = Side(style="thin", color="DEE2E6")
        borde = Border(top=thin, bottom=thin, left=thin, right=thin)
        font_titulo = Font(name="Calibri", size=18, bold=True, color="FFFFFF")
        fill_titulo = PatternFill("solid", fgColor=azul_huv)
        font_h2 = Font(name="Calibri", size=13, bold=True, color="FFFFFF")
        fill_h2 = PatternFill("solid", fgColor=verde_huv)
        font_th = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        fill_th = PatternFill("solid", fgColor=azul_huv)
        fill_alt = PatternFill("solid", fgColor=gris_claro)
        center = Alignment(horizontal="center", vertical="center", wrap_text=True)
        left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        right = Alignment(horizontal="right", vertical="center")

        def _aplicar_tabla(ws, fila_ini, col_ini, headers, filas):
            for i, h in enumerate(headers):
                c = ws.cell(row=fila_ini, column=col_ini + i, value=h)
                c.font = font_th
                c.fill = fill_th
                c.alignment = center
                c.border = borde
            for r, row in enumerate(filas, start=1):
                for j, val in enumerate(row):
                    c = ws.cell(row=fila_ini + r, column=col_ini + j, value=val)
                    c.alignment = right if isinstance(val, (int, float)) else left
                    c.border = borde
                    if r % 2 == 0:
                        c.fill = fill_alt
            return fila_ini + len(filas)

        # ── Hoja 1: Resumen Ejecutivo (KPIs) ──────────────────────
        ws1 = wb.active
        ws1.title = "Resumen Ejecutivo"
        ws1.merge_cells("A1:F1")
        c = ws1["A1"]
        c.value = "📊 RESUMEN IA — BASE DE DATOS IHQ HUV"
        c.font = font_titulo
        c.fill = fill_titulo
        c.alignment = center
        ws1.row_dimensions[1].height = 36

        ws1["A2"] = "Generado:"
        ws1["B2"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        ws1["A3"] = "Periodo cubierto:"
        ws1["B3"] = f"{stats.get('fecha_min', '—')} → {stats.get('fecha_max', '—')}"
        for r in (2, 3):
            ws1.cell(row=r, column=1).font = Font(bold=True)

        # KPIs
        total = stats.get("total_casos", 0)
        malig = stats.get("malignidad", {}) or {}
        n_malig = next(
            (v for k, v in malig.items()
             if "MALIGN" in str(k).upper() and "BENIG" not in str(k).upper()),
            0,
        )
        pct_malig = (n_malig / total * 100) if total else 0
        kpis = [
            ("Total casos", total),
            ("% Malignos", f"{pct_malig:.1f}%"),
            ("Categorías anatómicas", stats.get("organos_categorias_distintas", 0)),
            ("Biomarcadores distintos", stats.get("total_biomarcadores_distintos", 0)),
            ("Diagnósticos categorizados", stats.get("diagnosticos_total_categorizado", 0)),
        ]
        ws1.cell(row=5, column=1, value="Indicadores Clave").font = font_h2
        ws1.cell(row=5, column=1).fill = fill_h2
        ws1.cell(row=5, column=1).alignment = center
        ws1.merge_cells("A5:F5")
        ws1.row_dimensions[5].height = 24

        for i, (k, v) in enumerate(kpis):
            row = 6 + i
            a = ws1.cell(row=row, column=1, value=k)
            b = ws1.cell(row=row, column=2, value=v)
            a.font = Font(bold=True)
            a.fill = fill_alt
            a.border = borde
            b.border = borde
            b.alignment = right
            ws1.row_dimensions[row].height = 20

        for col in range(1, 7):
            ws1.column_dimensions[get_column_letter(col)].width = 24

        # ── Hoja 2: Distribución Anatómica ─────────────────────────
        ws2 = wb.create_sheet("Distribución Anatómica")
        ws2.merge_cells("A1:C1")
        ws2["A1"] = "🧬 Top categorías anatómicas (canónicas)"
        ws2["A1"].font = font_titulo
        ws2["A1"].fill = fill_titulo
        ws2["A1"].alignment = center
        ws2.row_dimensions[1].height = 30
        organos = stats.get("organos_normalizados", {}) or {}
        filas = [(k, v) for k, v in organos.items()]
        end_row = _aplicar_tabla(ws2, 3, 1, ["Órgano", "Casos"], filas)
        ws2.column_dimensions["A"].width = 38
        ws2.column_dimensions["B"].width = 14

        if filas:
            chart = BarChart()
            chart.type = "bar"
            chart.style = 11
            chart.title = "Top órganos"
            chart.y_axis.title = "Órgano"
            chart.x_axis.title = "Casos"
            data = Reference(ws2, min_col=2, min_row=3, max_row=end_row, max_col=2)
            cats = Reference(ws2, min_col=1, min_row=4, max_row=end_row)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.height = 12
            chart.width = 20
            ws2.add_chart(chart, "E3")

        # ── Hoja 3: Diagnósticos ──────────────────────────────────
        ws3 = wb.create_sheet("Diagnósticos")
        ws3.merge_cells("A1:C1")
        ws3["A1"] = "🩺 Diagnósticos por categoría clínica"
        ws3["A1"].font = font_titulo
        ws3["A1"].fill = fill_titulo
        ws3["A1"].alignment = center
        ws3.row_dimensions[1].height = 30
        dx = stats.get("diagnosticos_categorizados", {}) or {}
        filas = [(k, v) for k, v in dx.items() if k != "OTRO / NO CATEGORIZADO"]
        end_row = _aplicar_tabla(ws3, 3, 1, ["Categoría clínica", "Casos"], filas)
        ws3.column_dimensions["A"].width = 50
        ws3.column_dimensions["B"].width = 14

        # Notas adicionales
        nota_row = end_row + 2
        ws3.cell(row=nota_row, column=1, value="Sin diagnóstico específico (Estudio IHQ):").font = Font(bold=True, italic=True)
        ws3.cell(row=nota_row, column=2, value=stats.get("diagnosticos_estudio_ihq_sin_dx", 0))
        ws3.cell(row=nota_row + 1, column=1, value="Otros (no categorizados):").font = Font(bold=True, italic=True)
        ws3.cell(row=nota_row + 1, column=2, value=stats.get("diagnosticos_otro_no_categorizado", 0))
        ws3.cell(row=nota_row + 2, column=1, value="Sin dato:").font = Font(bold=True, italic=True)
        ws3.cell(row=nota_row + 2, column=2, value=stats.get("diagnosticos_sin_dato", 0))

        if filas:
            chart = BarChart()
            chart.type = "bar"
            chart.style = 12
            chart.title = "Top diagnósticos clínicos"
            data = Reference(ws3, min_col=2, min_row=3, max_row=end_row, max_col=2)
            cats = Reference(ws3, min_col=1, min_row=4, max_row=end_row)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.height = 12
            chart.width = 22
            ws3.add_chart(chart, "E3")

        # ── Hoja 4: Biomarcadores ─────────────────────────────────
        ws4 = wb.create_sheet("Biomarcadores")
        ws4.merge_cells("A1:D1")
        ws4["A1"] = "🔬 Top biomarcadores"
        ws4["A1"].font = font_titulo
        ws4["A1"].fill = fill_titulo
        ws4["A1"].alignment = center
        ws4.row_dimensions[1].height = 30
        bios = stats.get("biomarcadores_top15", {}) or {}
        filas = []
        for marcador, info in sorted(bios.items(), key=lambda x: x[1].get("n", 0), reverse=True):
            top = info.get("top", {}) or {}
            if top:
                primer_valor, primer_n = next(iter(top.items()))
                resumen = f"{primer_valor} (N={primer_n})"
            else:
                resumen = "—"
            filas.append((marcador, info.get("n", 0), resumen))
        end_row = _aplicar_tabla(
            ws4, 3, 1,
            ["Biomarcador", "N evaluados", "Resultado predominante"], filas,
        )
        ws4.column_dimensions["A"].width = 32
        ws4.column_dimensions["B"].width = 14
        ws4.column_dimensions["C"].width = 42

        if filas:
            chart = BarChart()
            chart.type = "bar"
            chart.style = 13
            chart.title = "Biomarcadores por N evaluados"
            data = Reference(ws4, min_col=2, min_row=3, max_row=end_row, max_col=2)
            cats = Reference(ws4, min_col=1, min_row=4, max_row=end_row)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.height = 12
            chart.width = 22
            ws4.add_chart(chart, "E3")

        # ── Hoja 5: Procedimientos & Servicios ────────────────────
        ws5 = wb.create_sheet("Procedimientos & Servicios")
        ws5.merge_cells("A1:E1")
        ws5["A1"] = "⚕️ Procedimientos y servicios solicitantes"
        ws5["A1"].font = font_titulo
        ws5["A1"].fill = fill_titulo
        ws5["A1"].alignment = center
        ws5.row_dimensions[1].height = 30
        procs = stats.get("procedimientos", {}) or {}
        servs = stats.get("servicios", {}) or {}
        _aplicar_tabla(ws5, 3, 1, ["Procedimiento", "Casos"],
                       [(k, v) for k, v in procs.items()])
        _aplicar_tabla(ws5, 3, 4, ["Servicio", "Casos"],
                       [(k, v) for k, v in servs.items()])
        ws5.column_dimensions["A"].width = 32
        ws5.column_dimensions["B"].width = 12
        ws5.column_dimensions["D"].width = 38
        ws5.column_dimensions["E"].width = 12

        # Pie de malignidad
        if malig:
            ws5.cell(row=20, column=1, value="Distribución de malignidad").font = font_h2
            ws5.cell(row=20, column=1).fill = fill_h2
            ws5.cell(row=20, column=1).alignment = center
            ws5.merge_cells("A20:B20")
            mfilas = [(k, v) for k, v in malig.items()]
            mend = _aplicar_tabla(ws5, 21, 1, ["Categoría", "Casos"], mfilas)
            chart = PieChart()
            chart.title = "Malignidad"
            chart.style = 10
            data = Reference(ws5, min_col=2, min_row=21, max_row=mend)
            cats = Reference(ws5, min_col=1, min_row=22, max_row=mend)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.height = 9
            chart.width = 13
            ws5.add_chart(chart, "D20")

        # ── Hoja 6: Informe IA en texto ───────────────────────────
        ws6 = wb.create_sheet("Informe IA")
        ws6.merge_cells("A1:H1")
        ws6["A1"] = "📝 Informe redactado por IA"
        ws6["A1"].font = font_titulo
        ws6["A1"].fill = fill_titulo
        ws6["A1"].alignment = center
        ws6.row_dimensions[1].height = 30
        ws6.column_dimensions["A"].width = 110

        for i, linea in enumerate(texto.splitlines(), start=3):
            cell = ws6.cell(row=i, column=1, value=linea)
            if linea.startswith("# "):
                cell.font = Font(size=14, bold=True, color=azul_huv)
                cell.value = linea[2:]
            elif linea.startswith("## "):
                cell.font = Font(size=12, bold=True, color=verde_huv)
                cell.value = linea[3:]
            elif linea.startswith("### "):
                cell.font = Font(size=11, bold=True)
                cell.value = linea[4:]
            else:
                cell.font = Font(size=10)
            cell.alignment = Alignment(wrap_text=True, vertical="top")

        try:
            wb.save(filepath)
            messagebox.showinfo(
                "Exportación exitosa",
                f"Excel guardado en:\n{filepath}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el Excel:\n{e}")

    # ── PDF ───────────────────────────────────────────────────────────
    def _exportar_resumen_pdf(self, texto: str, stats: dict):
        """Genera un PDF profesional con KPIs, tablas y gráficos matplotlib."""
        fecha_str = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        filepath = filedialog.asksaveasfilename(
            title="Exportar Resumen IA — PDF",
            defaultextension=".pdf",
            initialfile=f"Resumen_IA_HUV_{fecha_str}.pdf",
            filetypes=[("PDF", "*.pdf")],
        )
        if not filepath:
            return

        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, Image,
            )
        except Exception as e:
            messagebox.showerror("Error", f"reportlab no disponible: {e}")
            return

        # Generar imágenes de gráficos con matplotlib
        chart_paths = []
        try:
            import tempfile
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            tmpdir = tempfile.mkdtemp(prefix="huv_pdf_")

            def _save_bar(data: dict, titulo: str, color: str, fname: str, top_n=10):
                if not data:
                    return None
                items = list(data.items())[:top_n]
                items.reverse()
                etq = [str(k)[:42] for k, _ in items]
                val = [v for _, v in items]
                fig, ax = plt.subplots(figsize=(7, 4.2), dpi=150)
                ax.barh(etq, val, color=color)
                ax.set_title(titulo, fontsize=12, fontweight="bold")
                ax.tick_params(axis="y", labelsize=9)
                for i, v in enumerate(val):
                    ax.text(v, i, f" {v}", va="center", fontsize=8)
                fig.tight_layout()
                p = f"{tmpdir}/{fname}.png"
                fig.savefig(p, bbox_inches="tight")
                plt.close(fig)
                return p

            def _save_pie(data: dict, titulo: str, fname: str):
                if not data:
                    return None
                etq = list(data.keys())[:5]
                val = [data[k] for k in etq]
                fig, ax = plt.subplots(figsize=(5, 4.2), dpi=150)
                ax.pie(val, labels=etq, autopct="%1.1f%%",
                       colors=["#dc3545", "#198754", "#ffc107", "#6c757d", "#0dcaf0"][:len(etq)],
                       startangle=90, textprops={"fontsize": 9})
                ax.set_title(titulo, fontsize=12, fontweight="bold")
                fig.tight_layout()
                p = f"{tmpdir}/{fname}.png"
                fig.savefig(p, bbox_inches="tight")
                plt.close(fig)
                return p

            chart_paths.append(_save_pie(stats.get("malignidad", {}), "Malignidad", "malig"))
            chart_paths.append(_save_bar(stats.get("organos_normalizados", {}),
                                         "Top 10 órganos", "#0d6efd", "organos"))
            dx = {k: v for k, v in (stats.get("diagnosticos_categorizados", {}) or {}).items()
                  if k != "OTRO / NO CATEGORIZADO"}
            chart_paths.append(_save_bar(dx, "Top 10 diagnósticos clínicos", "#198754", "dx"))
            bios_top = {k: v.get("n", 0) for k, v in
                        sorted((stats.get("biomarcadores_top15", {}) or {}).items(),
                               key=lambda x: x[1].get("n", 0), reverse=True)}
            chart_paths.append(_save_bar(bios_top, "Top 10 biomarcadores (N evaluados)",
                                         "#fd7e14", "bios"))
        except Exception as e:
            logging.warning(f"No se pudieron generar gráficos para PDF: {e}")

        # Documento
        doc = SimpleDocTemplate(
            filepath, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm,
            topMargin=2*cm, bottomMargin=2*cm,
            title="Resumen IA HUV", author="EVARISIS",
        )
        styles = getSampleStyleSheet()
        h1 = ParagraphStyle("h1", parent=styles["Heading1"],
                            fontSize=20, textColor=colors.HexColor("#0D6EFD"),
                            spaceAfter=12)
        h2 = ParagraphStyle("h2", parent=styles["Heading2"],
                            fontSize=14, textColor=colors.HexColor("#198754"),
                            spaceBefore=12, spaceAfter=8)
        h3 = ParagraphStyle("h3", parent=styles["Heading3"],
                            fontSize=11, textColor=colors.HexColor("#6c757d"),
                            spaceBefore=6, spaceAfter=4)
        body = ParagraphStyle("body", parent=styles["Normal"],
                              fontSize=10, leading=14, spaceAfter=6)

        story = []

        # Portada
        story.append(Paragraph("📊 Resumen IA — Base de Datos IHQ", h1))
        story.append(Paragraph(
            "Hospital Universitario del Valle — EVARISIS Gestor Oncológico",
            body))
        story.append(Spacer(1, 6))
        story.append(Paragraph(
            f"<b>Generado:</b> {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>"
            f"<b>Periodo cubierto:</b> {stats.get('fecha_min', '—')} → "
            f"{stats.get('fecha_max', '—')}",
            body))
        story.append(Spacer(1, 12))

        # KPIs
        total = stats.get("total_casos", 0)
        malig = stats.get("malignidad", {}) or {}
        n_malig = next(
            (v for k, v in malig.items()
             if "MALIGN" in str(k).upper() and "BENIG" not in str(k).upper()),
            0,
        )
        pct_malig = (n_malig / total * 100) if total else 0

        kpi_data = [
            ["Total casos", "% Malignos", "Cat. anatómicas",
             "Biomarcadores", "Dx categorizados"],
            [str(total), f"{pct_malig:.1f}%",
             str(stats.get("organos_categorias_distintas", 0)),
             str(stats.get("total_biomarcadores_distintos", 0)),
             str(stats.get("diagnosticos_total_categorizado", 0))],
        ]
        kpi_tbl = Table(kpi_data, colWidths=[3.4*cm]*5)
        kpi_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D6EFD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#F1F3F5")),
            ("FONTSIZE", (0, 1), (-1, 1), 14),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#212529")),
            ("ROWBACKGROUNDS", (0, 1), (-1, 1), [colors.HexColor("#F1F3F5")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DEE2E6")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(kpi_tbl)
        story.append(Spacer(1, 16))

        # Helper para generar tablas de datos
        def _tabla_datos(titulo, data, col1, col2, max_filas=15):
            if not data:
                return
            story.append(Paragraph(titulo, h2))
            rows = [[col1, col2]]
            for k, v in list(data.items())[:max_filas]:
                rows.append([str(k), str(v)])
            t = Table(rows, colWidths=[12*cm, 3*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D6EFD")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DEE2E6")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#F8F9FA")]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t)
            story.append(Spacer(1, 10))

        # Sección gráficos
        story.append(Paragraph("Indicadores visuales", h2))
        # Pares de gráficos en 2 columnas
        valid_charts = [p for p in chart_paths if p]
        for i in range(0, len(valid_charts), 2):
            par = valid_charts[i:i+2]
            row = []
            for p in par:
                row.append(Image(p, width=8*cm, height=5.5*cm))
            if len(row) == 1:
                row.append("")
            t = Table([row], colWidths=[8.5*cm, 8.5*cm])
            t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            story.append(t)
            story.append(Spacer(1, 8))

        story.append(PageBreak())

        # Tablas detalle
        _tabla_datos("🧬 Top órganos (canónicos)",
                     stats.get("organos_normalizados", {}), "Órgano", "Casos")
        dx_clin = {k: v for k, v in (stats.get("diagnosticos_categorizados", {}) or {}).items()
                   if k != "OTRO / NO CATEGORIZADO"}
        _tabla_datos("🩺 Diagnósticos (categorías clínicas)",
                     dx_clin, "Categoría", "Casos")
        story.append(Paragraph(
            f"<i>Sin diagnóstico específico (Estudio IHQ): {stats.get('diagnosticos_estudio_ihq_sin_dx', 0)} · "
            f"Otros no categorizados: {stats.get('diagnosticos_otro_no_categorizado', 0)} · "
            f"Sin dato: {stats.get('diagnosticos_sin_dato', 0)}</i>",
            body))
        story.append(Spacer(1, 8))

        bios = stats.get("biomarcadores_top15", {}) or {}
        if bios:
            story.append(Paragraph("🔬 Top biomarcadores", h2))
            rows = [["Biomarcador", "N evaluados", "Resultado predominante"]]
            for marcador, info in sorted(bios.items(),
                                         key=lambda x: x[1].get("n", 0), reverse=True):
                top = info.get("top", {}) or {}
                if top:
                    primer_valor, primer_n = next(iter(top.items()))
                    resumen = f"{primer_valor} (N={primer_n})"
                else:
                    resumen = "—"
                rows.append([marcador, str(info.get("n", 0)), resumen])
            t = Table(rows, colWidths=[5.5*cm, 2.5*cm, 9*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D6EFD")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DEE2E6")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#F8F9FA")]),
            ]))
            story.append(t)
            story.append(Spacer(1, 8))

        _tabla_datos("⚕️ Procedimientos", stats.get("procedimientos", {}),
                     "Procedimiento", "Casos")
        _tabla_datos("🏥 Servicios solicitantes", stats.get("servicios", {}),
                     "Servicio", "Casos")

        story.append(PageBreak())

        # Informe IA narrativo
        story.append(Paragraph("📝 Informe redactado por IA", h1))
        import re as _re
        for raw in texto.splitlines():
            linea = raw.rstrip()
            if not linea:
                story.append(Spacer(1, 4))
                continue
            if linea.startswith("# "):
                story.append(Paragraph(linea[2:], h1))
            elif linea.startswith("## "):
                story.append(Paragraph(linea[3:], h2))
            elif linea.startswith("### "):
                story.append(Paragraph(linea[4:], h3))
            elif linea.strip() in {"---", "***"}:
                story.append(Spacer(1, 6))
            elif linea.startswith("|"):
                # Líneas de tabla markdown — las dejamos como código simple
                story.append(Paragraph(
                    f"<font face='Courier' size='8'>{linea.replace('<', '&lt;').replace('>', '&gt;')}</font>",
                    body,
                ))
            else:
                # Convertir **negritas**
                txt = _re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", linea)
                story.append(Paragraph(txt, body))

        try:
            doc.build(story)
            messagebox.showinfo(
                "Exportación exitosa",
                f"PDF guardado en:\n{filepath}",
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF:\n{e}")

    def _copiar_resumen_ia(self, texto: str, ventana: tk.Toplevel):
        """Copia el resumen IA al portapapeles."""
        ventana.clipboard_clear()
        ventana.clipboard_append(texto)
        messagebox.showinfo("Copiado", "Resumen copiado al portapapeles.")

    def _export_selected_data(self):
        """Exportar datos seleccionados usando el sistema mejorado (v6.0.12: con logging mejorado)"""
        try:
            import pandas as pd

            # v6.0.12: Logging inicial para debugging
            logging.debug("_export_selected_data: Iniciando exportación de selección")

            # Obtener elementos seleccionados del treeview
            selected_items = self.tree.selection()
            logging.debug(f"_export_selected_data: selection() retornó {len(selected_items) if selected_items else 0} items")

            if not selected_items:
                logging.warning("_export_selected_data: No hay selección para exportar")
                messagebox.showwarning("Sin Selección", "No hay elementos seleccionados para exportar")
                return

            logging.info(f"Exportar Seleccion: {len(selected_items)} elementos seleccionados")

            # Validar que master_df existe
            if not hasattr(self, 'master_df') or self.master_df is None or self.master_df.empty:
                logging.error("master_df no existe o esta vacio")
                messagebox.showerror(
                    "Error",
                    "Los datos no están cargados en memoria.\n"
                    "Recarga la base de datos e intenta de nuevo."
                )
                return

            # Obtener datos de las filas seleccionadas (enfoque simple que funciona)
            selected_rows_data = []
            for item in selected_items:
                # tksheet: Usar get_row_data() en lugar de .item()
                values = self.sheet.get_row_data(item)
                logging.info(f"DEBUG item={item}: values={values}")

                if values:
                    # El primer valor es el número de petición/caso
                    numero_peticion = values[0]

                    # Buscar el registro correspondiente en master_df usando la primera columna
                    # (esto es lo que funciona en _export_selected_data_professional)
                    matching_row = self.master_df[self.master_df.iloc[:, 0] == numero_peticion]

                    if not matching_row.empty:
                        selected_rows_data.append(matching_row.iloc[0])
                        logging.info(f"Fila '{numero_peticion}' encontrada y agregada")
                    else:
                        logging.warning(f"No se encontro la fila '{numero_peticion}' en master_df")
                else:
                    logging.warning(f"Item sin valores: {item}")

            if not selected_rows_data:
                logging.error("No se pudieron obtener datos de la seleccion")
                messagebox.showwarning(
                    "Sin Datos",
                    "No se pudieron obtener los datos de la selección.\n"
                    "Intenta recargar la base de datos."
                )
                return

            logging.info(f"Filas obtenidas exitosamente: {len(selected_rows_data)}")

            # Crear DataFrame con los registros seleccionados
            selected_df = pd.DataFrame(selected_rows_data)

            # Exportar usando el sistema mejorado
            self.export_system.export_selected_data(selected_df)

        except Exception as e:
            logging.error(f"Error en _export_selected_data: {e}", exc_info=True)
            messagebox.showerror("Error de Exportación", f"Error al exportar la selección:\n{str(e)}")

    def _toggle_details_panel(self):
        """Mostrar/ocultar panel flotante de detalles"""
        try:
            self.export_system.toggle_floating_details_panel()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar panel de detalles:\n{str(e)}")

    def _toggle_advanced_filters(self):
        """Mostrar/ocultar panel de filtros avanzados"""
        try:
            self.export_system.toggle_advanced_filters_panel()
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar filtros avanzados:\n{str(e)}")

    def _update_export_button_state(self):
        """Actualizar estado del botón de exportar selección según la selección"""
        try:
            logging.info("_update_export_button_state: INICIANDO")

            # Obtener selección del sheet apropiado
            selected_items = []
            if hasattr(self, 'sheet') and self.sheet is not None:
                try:
                    selected_items = self.sheet.selection()
                except:
                    pass
            elif hasattr(self, 'sheet_dashboard') and self.sheet_dashboard is not None:
                try:
                    selected_items = self.sheet_dashboard.selection()
                except:
                    pass
            elif hasattr(self, 'tree') and self.tree is not None:
                selected_items = self.tree.selection()

            logging.info(f"_update_export_button_state: selection() = {selected_items}")
            has_selection = bool(selected_items)

            # Actualizar botón original
            if hasattr(self, 'export_selection_btn'):
                logging.info("_update_export_button_state: export_selection_btn existe")
                if has_selection:
                    logging.info("_update_export_button_state: HAY SELECCIÓN -> Habilitando botón")
                    self.export_selection_btn.configure(state="normal")
                else:
                    logging.info("_update_export_button_state: SIN SELECCIÓN -> Deshabilitando botón")
                    self.export_selection_btn.configure(state="disabled")

            # Actualizar botón del dashboard
            if hasattr(self, 'export_selection_btn_dashboard'):
                if has_selection:
                    self.export_selection_btn_dashboard.configure(state="normal")
                else:
                    self.export_selection_btn_dashboard.configure(state="disabled")

        except Exception as e:
            logging.error(f"Error actualizando estado del boton: {e}", exc_info=True)

    def _update_audit_buttons_state(self):
        """v6.0.14: Actualizar estado de botones de auditoría según la selección"""
        try:
            logging.info("_update_audit_buttons_state: INICIANDO")

            # Obtener selección del sheet apropiado
            selection = []
            if hasattr(self, 'sheet') and self.sheet is not None:
                try:
                    selection = self.sheet.selection()
                except:
                    pass
            elif hasattr(self, 'sheet_dashboard') and self.sheet_dashboard is not None:
                try:
                    selection = self.sheet_dashboard.selection()
                except:
                    pass
            elif hasattr(self, 'tree') and self.tree is not None:
                selection = self.tree.selection()

            logging.info(f"_update_audit_buttons_state: selection() = {selection}")
            has_selection = bool(selection)
            logging.info(f"_update_audit_buttons_state: has_selection = {has_selection}")
            logging.info(f"_update_audit_buttons_state: CHECKPOINT 1 - Antes del if")

            if not has_selection:
                logging.info(f"_update_audit_buttons_state: CHECKPOINT 2 - Dentro del if not has_selection")
                # Sin selección → deshabilitar botones
                logging.info("_update_audit_buttons_state: SIN SELECCIÓN -> Deshabilitando botones")

                # Deshabilitar botones originales
                if hasattr(self, 'audit_parcial_btn'):
                    logging.info("  -> Deshabilitando audit_parcial_btn")
                    self.audit_parcial_btn.configure(state="disabled")
                if hasattr(self, 'audit_completa_btn'):
                    logging.info("  -> Deshabilitando audit_completa_btn")
                    self.audit_completa_btn.configure(state="disabled")

                # Deshabilitar botones del dashboard
                if hasattr(self, 'audit_parcial_btn_dashboard'):
                    self.audit_parcial_btn_dashboard.configure(state="disabled")
                if hasattr(self, 'audit_completa_btn_dashboard'):
                    self.audit_completa_btn_dashboard.configure(state="disabled")
            else:
                # Hay selección → determinar estados
                logging.info("_update_audit_buttons_state: CHECKPOINT 3 - Dentro del else (HAY SELECCIÓN)")
                logging.info("_update_audit_buttons_state: HAY SELECCIÓN -> Determinando estados...")
                from core.database_manager import get_estado_auditoria

                try:
                    # Obtener el sheet correcto (dashboard o original)
                    active_sheet = None
                    if hasattr(self, 'sheet_dashboard') and self.sheet_dashboard is not None:
                        try:
                            if self.sheet_dashboard.selection():
                                active_sheet = self.sheet_dashboard
                        except:
                            pass
                    if active_sheet is None and hasattr(self, 'sheet') and self.sheet is not None:
                        active_sheet = self.sheet

                    if active_sheet is None:
                        logging.error("No hay sheet activo disponible")
                        return

                    # Obtener índice de columna "Numero de caso"
                    try:
                        headers = active_sheet.headers() if hasattr(active_sheet, 'headers') else []
                        logging.info(f"_update_audit_buttons_state: headers = {headers}")
                        col_idx = headers.index("Numero de caso") if "Numero de caso" in headers else 0
                        logging.info(f"_update_audit_buttons_state: col_idx = {col_idx}")
                    except Exception as e:
                        logging.error(f"_update_audit_buttons_state: ERROR obteniendo col_idx: {e}")
                        col_idx = 0

                    # Obtener estados de todos los items seleccionados
                    estados = []
                    logging.info(f"_update_audit_buttons_state: Obteniendo estados para {len(selection)} items...")
                    for item_id in selection:
                        # tksheet: Usar get_row_data() en lugar de .item()
                        values = active_sheet.get_row_data(item_id)
                        logging.info(f"_update_audit_buttons_state: item_id={item_id}, values={values}")
                        if values and len(values) > col_idx:
                            numero_peticion = values[col_idx]
                            logging.info(f"_update_audit_buttons_state: numero_peticion={numero_peticion}")
                            estado = get_estado_auditoria(numero_peticion)
                            logging.info(f"_update_audit_buttons_state: estado={estado}")
                            estados.append(estado)
                        else:
                            logging.warning(f"_update_audit_buttons_state: No se pudieron obtener valores para item_id={item_id}")

                    # Lógica de habilitación basada en estados
                    logging.info(f"_update_audit_buttons_state: estados recolectados = {estados}")

                    if all(e == "COMPLETA" for e in estados):
                        # TODOS tienen auditoría COMPLETA → Bloquear ambos
                        logging.info("_update_audit_buttons_state: TODOS COMPLETA -> Bloqueando ambos")
                        if hasattr(self, 'audit_parcial_btn'):
                            self.audit_parcial_btn.configure(state="disabled")
                        if hasattr(self, 'audit_completa_btn'):
                            self.audit_completa_btn.configure(state="disabled")
                        if hasattr(self, 'audit_parcial_btn_dashboard'):
                            self.audit_parcial_btn_dashboard.configure(state="disabled")
                        if hasattr(self, 'audit_completa_btn_dashboard'):
                            self.audit_completa_btn_dashboard.configure(state="disabled")

                    elif all(e == "PARCIAL" for e in estados):
                        # TODOS tienen auditoría PARCIAL → Solo permitir COMPLETA
                        logging.info("_update_audit_buttons_state: TODOS PARCIAL -> Solo COMPLETA habilitada")
                        if hasattr(self, 'audit_parcial_btn'):
                            self.audit_parcial_btn.configure(state="disabled")
                        if hasattr(self, 'audit_completa_btn'):
                            self.audit_completa_btn.configure(state="normal")
                        if hasattr(self, 'audit_parcial_btn_dashboard'):
                            self.audit_parcial_btn_dashboard.configure(state="disabled")
                        if hasattr(self, 'audit_completa_btn_dashboard'):
                            self.audit_completa_btn_dashboard.configure(state="normal")

                    elif all(e in [None, "NULL", ""] for e in estados):
                        # TODOS sin auditoría → Permitir ambas
                        logging.info("_update_audit_buttons_state: TODOS SIN AUDITORIA -> Habilitando ambos")
                        if hasattr(self, 'audit_parcial_btn'):
                            logging.info("  -> Habilitando audit_parcial_btn")
                            self.audit_parcial_btn.configure(state="normal")
                        if hasattr(self, 'audit_completa_btn'):
                            logging.info("  -> Habilitando audit_completa_btn")
                            self.audit_completa_btn.configure(state="normal")
                        if hasattr(self, 'audit_parcial_btn_dashboard'):
                            self.audit_parcial_btn_dashboard.configure(state="normal")
                        if hasattr(self, 'audit_completa_btn_dashboard'):
                            self.audit_completa_btn_dashboard.configure(state="normal")

                    else:
                        # Mezcla de estados → Permitir ambas
                        logging.info("_update_audit_buttons_state: MEZCLA DE ESTADOS -> Habilitando ambos")
                        if hasattr(self, 'audit_parcial_btn'):
                            logging.info("  -> Habilitando audit_parcial_btn")
                            self.audit_parcial_btn.configure(state="normal")
                        if hasattr(self, 'audit_completa_btn'):
                            logging.info("  -> Habilitando audit_completa_btn")
                            self.audit_completa_btn.configure(state="normal")
                        if hasattr(self, 'audit_parcial_btn_dashboard'):
                            self.audit_parcial_btn_dashboard.configure(state="normal")
                        if hasattr(self, 'audit_completa_btn_dashboard'):
                            self.audit_completa_btn_dashboard.configure(state="normal")

                except Exception as e:
                    logging.error(f"Error en lógica de auditoría: {e}")
                    # Si hay error, deshabilitar botones
                    if hasattr(self, 'audit_parcial_btn'):
                        self.audit_parcial_btn.configure(state="disabled")
                    if hasattr(self, 'audit_completa_btn'):
                        self.audit_completa_btn.configure(state="disabled")
                    if hasattr(self, 'audit_parcial_btn_dashboard'):
                        self.audit_parcial_btn_dashboard.configure(state="disabled")
                    if hasattr(self, 'audit_completa_btn_dashboard'):
                        self.audit_completa_btn_dashboard.configure(state="disabled")

        except Exception as e:
            logging.error(f"Error actualizando botones de auditoría: {e}", exc_info=True)
    
    def _setup_cell_tooltips(self):
        """
        V5.3.8: Configurar tooltips emergentes al pasar el mouse sobre celdas del Sheet
        Muestra el contenido COMPLETO de la celda cuando es muy largo
        """
        # Crear tooltip widget (inicialmente oculto)
        self.tooltip = None
        self.tooltip_job = None
        self._last_tooltip_cell = None  # Rastrear última celda con tooltip

        def show_tooltip(event):
            """Mostrar tooltip con el contenido completo de la celda"""
            # Cancelar tooltip anterior si existe
            if self.tooltip_job:
                self.after_cancel(self.tooltip_job)
                self.tooltip_job = None

            try:
                # V5.3.8: Obtener celda bajo el cursor usando métodos correctos de Sheet
                # Método 1: get_cell_at_position
                cell_info = None
                try:
                    # Convertir coordenadas de evento a coordenadas del canvas
                    x = self.sheet.canvasx(event.x)
                    y = self.sheet.canvasy(event.y)

                    # Intentar obtener la celda en esa posición
                    # tksheet usa diferentes métodos dependiendo de la versión
                    if hasattr(self.sheet, 'get_cell_at_position'):
                        cell_info = self.sheet.get_cell_at_position(x, y)
                    elif hasattr(self.sheet.MT, 'identify_row') and hasattr(self.sheet.MT, 'identify_col'):
                        # Acceder al MainTable interno
                        row = self.sheet.MT.identify_row(y=event.y)
                        col = self.sheet.MT.identify_col(x=event.x)
                        if row is not None and col is not None:
                            cell_info = {'row': row, 'column': col}
                except:
                    pass

                # Si no se pudo obtener la celda, salir
                if not cell_info:
                    if self.tooltip:
                        self.tooltip.destroy()
                        self.tooltip = None
                        self._last_tooltip_cell = None
                    return

                # Extraer fila y columna del resultado
                row = cell_info.get('row') if isinstance(cell_info, dict) else getattr(cell_info, 'row', None)
                col = cell_info.get('column') if isinstance(cell_info, dict) else getattr(cell_info, 'column', None)

                if row is None or col is None:
                    return

                # Evitar recrear tooltip para la misma celda
                if self._last_tooltip_cell == (row, col):
                    return

                # Destruir tooltip anterior
                if self.tooltip:
                    self.tooltip.destroy()
                    self.tooltip = None

                # Obtener valor de la celda
                try:
                    cell_value = self.sheet.get_cell_data(row, col, return_copy=True)
                except:
                    return

                if not cell_value:
                    return

                cell_value = str(cell_value).strip()

                # Solo mostrar tooltip si el valor es suficientemente largo (>30 chars)
                # o contiene saltos de línea
                if len(cell_value) < 30 and '\n' not in cell_value:
                    return

                # Evitar tooltips para valores vacíos o inútiles
                if cell_value in ['', 'N/A', 'nan', 'None', 'null']:
                    return

                # Crear tooltip después de un pequeño delay
                def create_tooltip():
                    try:
                        self.tooltip = tk.Toplevel(self.sheet)
                        self.tooltip.wm_overrideredirect(True)

                        # Posicionar tooltip cerca del cursor
                        x_pos = event.x_root + 15
                        y_pos = event.y_root + 10

                        # Ajustar si está muy cerca del borde derecho
                        screen_width = self.tooltip.winfo_screenwidth()
                        if x_pos + 450 > screen_width:
                            x_pos = screen_width - 460

                        self.tooltip.wm_geometry(f"+{x_pos}+{y_pos}")

                        # Frame con borde y sombra
                        frame = tk.Frame(
                            self.tooltip,
                            relief="solid",
                            borderwidth=2,
                            background="#2C3E50",  # Borde azul oscuro profesional
                            padx=1,
                            pady=1
                        )
                        frame.pack()

                        inner_frame = tk.Frame(
                            frame,
                            background="#FFFEF0",  # Fondo crema claro
                            padx=10,
                            pady=8
                        )
                        inner_frame.pack()

                        # Texto del tooltip (máximo 1000 caracteres para auditoría)
                        display_text = cell_value[:1000] + "..." if len(cell_value) > 1000 else cell_value

                        label = tk.Label(
                            inner_frame,
                            text=display_text,
                            background="#FFFEF0",
                            foreground="#1A1A1A",
                            font=("Segoe UI", 9),
                            wraplength=450,  # Ancho máximo del tooltip
                            justify=tk.LEFT,
                            anchor="w"
                        )
                        label.pack()

                        # Agregar longitud del texto si es muy largo
                        if len(cell_value) > 100:
                            length_label = tk.Label(
                                inner_frame,
                                text=f"({len(cell_value)} caracteres)",
                                background="#FFFEF0",
                                foreground="#7F8C8D",
                                font=("Segoe UI", 8, "italic")
                            )
                            length_label.pack(anchor="e", pady=(5, 0))

                        # Guardar celda actual
                        self._last_tooltip_cell = (row, col)

                    except Exception as e:
                        logging.warning(f"Error creando tooltip: {e}")
                        if self.tooltip:
                            self.tooltip.destroy()
                            self.tooltip = None

                self.tooltip_job = self.after(400, create_tooltip)  # 400ms delay (más rápido)

            except Exception as e:
                # Silenciar errores de tooltips para no interrumpir la UI
                pass

        def hide_tooltip(event=None):
            """Ocultar tooltip"""
            if self.tooltip_job:
                self.after_cancel(self.tooltip_job)
                self.tooltip_job = None

            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

            self._last_tooltip_cell = None

        # Vincular eventos al Sheet
        self.sheet.bind("<Motion>", show_tooltip, add="+")
        self.sheet.bind("<Leave>", hide_tooltip, add="+")
        self.sheet.bind("<Button-1>", hide_tooltip, add="+")  # Ocultar al hacer clic

    def _delayed_refresh_after_processing(self):
        """Refresh retardado después del procesamiento para asegurar actualización"""
        try:
            # V5.3.9.3: Usar logging en lugar de print (stdout puede estar cerrado)
            logging.info("🔄 Ejecutando refresh automático después del procesamiento...")

            # Forzar refresh de datos
            self.refresh_data_and_table()

            # Si estamos en otra vista, cambiar automáticamente al visualizador
            if hasattr(self, 'current_view') and self.current_view != "visualizar":
                logging.info("📊 Cambiando automáticamente al Visualizador de Datos...")
                self.show_visualizar_frame()

            # Actualizar estado de los botones de exportación
            self._update_export_button_state()

            logging.info("✅ Refresh automático completado")

        except Exception as e:
            logging.error(f"❌ Error en refresh automático: {e}")
            # Mostrar mensaje al usuario si falla
            try:
                messagebox.showwarning(
                    "Actualización automática",
                    f"Los datos se procesaron correctamente, pero no se pudo actualizar la vista automáticamente.\n\n"
                    f"Por favor, ve al Visualizador y haz clic en 'Actualizar Datos'.\n\nError: {e}"
                )
            except:
                pass

    def cargar_dashboard(self):
        # 1) Preparar DF y combos de filtros
        df = self.master_df.copy()
        if df is None or df.empty:
            self._render_kpis(df)
            self._clear_dash_area()
            return

        # Normaliza fechas (varias columnas posibles)
        df["_fecha_informe"] = pd.to_datetime(
            df.get("Fecha Informe", df.get("Fecha de informe", df.get("Fecha de ingreso", ""))),
            dayfirst=True, errors="coerce"
        )

        # Llenar combos dinámicos (servicios / responsables)
        srv_vals = sorted([s for s in df.get("Servicio", pd.Series(dtype=str)).dropna().astype(str).unique() if s.strip()])
        rsp_vals = sorted([s for s in df.get("Patologo", pd.Series(dtype=str)).dropna().astype(str).unique() if s.strip()])
        
        # Solo configurar si los componentes existen
        if self.cmb_servicio is not None:
            try:
                self.cmb_servicio.configure(values=[""] + srv_vals)
            except:
                pass
        
        if self.cmb_resp is not None:
            try:
                self.cmb_resp.configure(values=[""] + rsp_vals)
            except:
                pass

        # 2) Render de KPIs básicos
        self._render_kpis(df)

        # 3) Limpiar canvases anteriores y pintar
        self._clear_dash_area()

        # Filtros iniciales (los que estén llenos)
        dff = self._get_filtered_df(df)

        # 4) PINTAR: OVERVIEW (4 gráficos)
        self._chart_in(self.tab_overview, 0, 0, lambda: self._g_line_informes_por_mes(dff), "Informes por mes", dff)
        self._chart_in(self.tab_overview, 0, 1, lambda: self._g_pie_malignidad(dff), "Distribución de Malignidad", dff)
        self._chart_in(self.tab_overview, 1, 0, lambda: self._g_bar_top_servicio(dff), "Top Servicios", dff)
        self._chart_in(self.tab_overview, 1, 1, lambda: self._g_bar_top_organo(dff), "Top Órganos", dff)

        # 5) PINTAR: BIOMARCADORES
        self._chart_in(self.tab_biomarkers, 0, 0, lambda: self._g_hist_ki67(dff), "Ki-67 (%)", dff)
        self._chart_in(self.tab_biomarkers, 0, 1, lambda: self._g_bar_her2(dff), "HER2 (score)", dff)
        self._chart_in(self.tab_biomarkers, 1, 0, lambda: self._g_bar_re_rp(dff), "RE / RP (estado)", dff)
        self._chart_in(self.tab_biomarkers, 1, 1, lambda: self._g_bar_pdl1(dff), "PD-L1", dff)

        # 6) PINTAR: TIEMPOS
        self._chart_in(self.tab_times, 0, 0, lambda: self._g_box_tiempo_proceso(dff), "Tiempo de proceso (días)", dff)
        self._chart_in(self.tab_times, 0, 1, lambda: self._g_line_throughput_semana(dff), "Throughput semanal", dff)
        self._chart_in(self.tab_times, 1, 0, lambda: self._g_scatter_edad_ki67(dff), "Edad vs Ki-67", dff)

        # 7) PINTAR: CALIDAD
        self._chart_in(self.tab_quality, 0, 0, lambda: self._g_bar_missingness(dff), "Campos vacíos (%)", dff)
        self._chart_in(self.tab_quality, 0, 1, lambda: self._g_bar_top_responsables(dff), "Productividad por responsable", dff)
        self._chart_in(self.tab_quality, 1, 0, lambda: self._g_bar_largos_texto(dff), "Longitud del diagnóstico", dff)

        # 8) PINTAR: COMPARADOR
        self._build_comparator(self.tab_compare, dff)


    # =========================
    # Estilo de tabla (Treeview) - MÉTODO ACTUALIZADO
    # =========================
    def setup_treeview_style(self):
        style = ttk_std.Style()
        style.theme_use("clam")  # look & feel moderno y estable en Windows

        # Cuerpo de la tabla - Estilo profesional mejorado
        style.configure(
            "Custom.Treeview",
            background="#ffffff",        # Fondo blanco para mejor legibilidad
            fieldbackground="#ffffff",   # Fondo de campos blanco
            foreground="#2c3e50",        # Texto azul oscuro para mayor contraste
            rowheight=35,                # Filas más altas para mejor espaciado
            borderwidth=1,               # Borde sutil
            relief="solid",              # Borde sólido
            font=("Segoe UI", 10),       # Fuente más legible
        )

        # Configurar colores alternados para filas
        style.map(
            "Custom.Treeview",
            background=[
                ("selected", "#0078d4"),     # Azul Microsoft para selección
                ("!selected", "#ffffff")     # Blanco para filas no seleccionadas
            ],
            foreground=[
                ("selected", "white"),       # Texto blanco en selección
                ("!selected", "#2c3e50")     # Texto azul oscuro normal
            ]
        )

        # Encabezados profesionales
        style.configure(
            "Custom.Treeview.Heading",
            background="#f8f9fa",           # Gris muy claro para encabezados
            foreground="#495057",           # Gris oscuro para texto
            font=("Segoe UI", 11, "bold"),  # Fuente en negrita
            relief="ridge",                 # Relieve elevado
            borderwidth=1,                  # Borde definido
        )

        # Efectos hover en encabezados
        style.map(
            "Custom.Treeview.Heading",
            background=[("active", "#e9ecef")],  # Gris claro en hover
            foreground=[("active", "#212529")]   # Texto más oscuro en hover
        )

        return style
    # ---------- Automatización Web (modal + ejecución) ----------

    def open_web_auto_modal(self):
        top = tk.Toplevel(self)
        top.title("Interoperabilidad QHORTE - Sistema de Entrega")
        top.geometry("460x360")
        top.grab_set()

        top.transient(self)
        try:
            top.lift(); top.focus_force()
        except Exception:
            pass
        
        # Campos
        frm = ttk.Frame(top, padding=12, relief="solid", borderwidth=1)
        frm.pack(fill="both", expand=True, padx=12, pady=12)

        # Usuario / Clave
        ttk.Label(frm, text="Usuario").grid(row=0, column=0, padx=10, pady=(12,6), sticky="w")
        user_var = tk.StringVar(value="12345")
        ttk.Entry(frm, textvariable=user_var).grid(row=0, column=1, padx=10, pady=(12,6), sticky="ew")

        ttk.Label(frm, text="Contraseña").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        pass_var = tk.StringVar(value="CONSULTA1")
        ttk.Entry(frm, textvariable=pass_var, show="•").grid(row=1, column=1, padx=10, pady=6, sticky="ew")

        # Criterio
        ttk.Label(frm, text="Buscar por").grid(row=2, column=0, padx=10, pady=6, sticky="w")
        criterio_var = tk.StringVar(value="Fecha de Ingreso")
        ttk.Combobox(frm, values=["Fecha de Ingreso", "Fecha de Finalizacion", "Rango de Peticion", "Datos del Paciente"], textvariable=criterio_var).grid(row=2, column=1, padx=10, pady=6, sticky="ew")

        # Fechas
        fi_var = tk.StringVar(value="")
        ff_var = tk.StringVar(value="")

        def pick_fi():
            sel = CalendarioInteligente.seleccionar_fecha(parent=top, locale='es_CO', codigo_pais_festivos='CO')
            if sel:
                fi_var.set(sel.strftime("%d/%m/%Y"))
            # RE-ADQUIRIR MODAL Y TRAER AL FRENTE
            try:
                top.deiconify()
                # truco para traer al frente en Windows
                top.attributes("-topmost", True); top.attributes("-topmost", False)
                top.lift(); top.focus_force(); top.grab_set()
            except Exception:
                pass

        def pick_ff():
            sel = CalendarioInteligente.seleccionar_fecha(parent=top, locale='es_CO', codigo_pais_festivos='CO')
            if sel:
                ff_var.set(sel.strftime("%d/%m/%Y"))
            # RE-ADQUIRIR MODAL Y TRAER AL FRENTE
            try:
                top.deiconify()
                top.attributes("-topmost", True); top.attributes("-topmost", False)
                top.lift(); top.focus_force(); top.grab_set()
            except Exception:
                pass

        ttk.Label(frm, text="Fecha inicial").grid(row=3, column=0, padx=10, pady=6, sticky="w")
        row_fi = ttk.Frame(frm); row_fi.grid(row=3, column=1, padx=10, pady=6, sticky="ew")
        ttk.Entry(row_fi, textvariable=fi_var).pack(side="left", fill="x", expand=True, padx=(0,6))
        ttk.Button(row_fi, text="Elegir…", width=10, command=pick_fi).pack(side="left")

        ttk.Label(frm, text="Fecha final").grid(row=4, column=0, padx=10, pady=6, sticky="w")
        row_ff = ttk.Frame(frm); row_ff.grid(row=4, column=1, padx=10, pady=6, sticky="ew")
        ttk.Entry(row_ff, textvariable=ff_var).pack(side="left", fill="x", expand=True, padx=(0,6))
        ttk.Button(row_ff, text="Elegir…", width=10, command=pick_ff).pack(side="left")

        # Botones
        btns = ttk.Frame(frm); btns.grid(row=5, column=0, columnspan=2, pady=(12,8), sticky="ew")
        ttk.Button(btns, text="Cancelar", command=top.destroy).pack(side="right", padx=6)
        def go():
            top.destroy()
            self._start_web_automation(
                fi_var.get().strip(), ff_var.get().strip(),
                user_var.get().strip(), pass_var.get().strip(),
                criterio_var.get().strip()
            )
        ttk.Button(btns, text="Iniciar", command=go).pack(side="right", padx=6)

        # grid conf
        frm.grid_columnconfigure(1, weight=1)

    def _start_web_automation(self, fi, ff, user, pwd, criterio):
        if not fi or not ff:
            messagebox.showwarning("Fechas requeridas", "Debe seleccionar fecha inicial y final.")
            return
        self.set_status("Automatizando Entrega de resultados…")
        t = threading.Thread(target=self._run_web_automation, args=(fi, ff, user, pwd, criterio), daemon=True)
        t.start()

    def _run_web_automation(self, fi, ff, user, pwd, criterio):
        try:
            # LAZY IMPORT: Solo importar cuando realmente se necesite
            from core.huv_web_automation import automatizar_entrega_resultados, Credenciales

            ok = automatizar_entrega_resultados(
                fecha_inicial_ddmmaa=fi,
                fecha_final_ddmmaa=ff,
                cred=Credenciales(usuario=user, clave=pwd),
                criterio=criterio,
                headless=False,
                log_cb=self._log_auto
            )
            if ok:
                self.set_status("Consulta web completada. Revise resultados en el navegador.")
                messagebox.showinfo("Automatización", "Consulta completada en el portal.")
            else:
                self.set_status("Automatización: sin resultado.")
        except Exception as e:
            self.set_status(f"Error en automatización: {e}")
            messagebox.showerror("Automatización", f"Ocurrió un error:\n{e}")

    def _log_auto(self, msg: str):
        try:
            # Si está visible el textbox de logs de Procesar, úsalo; si no, status.
            if hasattr(self, "log_textbox") and str(self.log_textbox.winfo_exists()) == "1":
                self.log_textbox.configure(state="normal")
                self.log_textbox.insert("end", f"[AUTO] {msg}\n")
                self.log_textbox.configure(state="disabled")
                self.log_textbox.see("end")
            else:
                self.set_status(msg)
        except Exception:
            self.set_status(msg)

    # =========================
    # Tema claro/oscuro
    # =========================
    # =========================
    # Métodos para el panel de procesamiento
    # =========================
    def _show_external_data_info(self):
        """Mostrar información de los datos externos en un modal"""
        top = tk.Toplevel(self)
        top.title("Información de Datos Externos")
        top.geometry("500x400")
        top.grab_set()
        top.transient(self)
        
        frame = ttk.Frame(top, padding=20)
        frame.pack(fill=BOTH, expand=True)
        
        ttk.Label(frame, text="Información de Base de Datos", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))
        
        # Obtener información de la base de datos
        try:
            from core.database_manager import get_all_records_as_dataframe
            df = get_all_records_as_dataframe()
            
            if df.empty:
                total_records = 0
                date_range = "No disponible"
                last_import = "No disponible"
                unique_services = 0
                malignant_count = 0
            else:
                total_records = len(df)
                date_range = "Disponible" 
                last_import = "Disponible"
                unique_services = df.get('Servicio', pd.Series()).nunique() if 'Servicio' in df.columns else 0
                malignant_count = (df.get('Malignidad', pd.Series()).str.contains('PRESENTE', case=False, na=False)).sum() if 'Malignidad' in df.columns else 0
            
            info_text = f"""Total de informes en BD: {total_records}

Rango de fechas: {date_range}

Última importación: {last_import}

Servicios únicos: {unique_services}

Informes con malignidad: {malignant_count}"""
            
        except Exception as e:
            info_text = f"Error al obtener información de la base de datos:\n{str(e)}"
        
        text_widget = tk.Text(frame, wrap="word", font=("Segoe UI", 11))
        text_widget.pack(fill=BOTH, expand=True, pady=(0, 20))
        text_widget.insert("1.0", info_text)
        text_widget.configure(state="disabled")
        
        ttk.Button(frame, text="Cerrar", command=top.destroy, bootstyle="primary").pack()

    def _select_pdf_file(self):
        """Seleccionar un archivo PDF individual con flujo completo de análisis"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=os.path.join(os.getcwd(), "pdfs_patologia") if os.path.exists("pdfs_patologia") else os.getcwd()
        )
        if file_path:
            # NUEVO: Limpiar lista de registros procesados y obtener peticiones existentes antes del procesamiento
            self._ultimos_registros_procesados = []
            peticiones_antes = set()
            try:
                import sqlite3
                from core.database_manager import DB_FILE
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
                peticiones_antes = set(row[0] for row in cursor.fetchall() if row[0])
                conn.close()
            except Exception as e:
                logging.warning(f"Error obteniendo peticiones existentes: {e}")

            try:
                # V5.3.9: _process_file ahora retorna (records_count, correcciones)
                records, correcciones = self._process_file(file_path)

                # NUEVO: Obtener los números de petición de los registros recién procesados
                try:
                    import sqlite3
                    from core.database_manager import DB_FILE
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
                    peticiones_despues = set(row[0] for row in cursor.fetchall() if row[0])
                    conn.close()

                    # Calcular la diferencia: nuevos registros = después - antes
                    nuevas_peticiones = list(peticiones_despues - peticiones_antes)
                    self._ultimos_registros_procesados = nuevas_peticiones
                    # V5.3.9.3: Usar logging en lugar de print (stdout puede estar cerrado)
                    logging.info(f"📋 Registros nuevos detectados: {len(nuevas_peticiones)}")
                    if nuevas_peticiones:
                        logging.info(f"   IDs: {', '.join(nuevas_peticiones[:5])}" + (" ..." if len(nuevas_peticiones) > 5 else ""))
                except Exception as e:
                    logging.warning(f"⚠️ Error capturando nuevos registros: {e}")
                    self._ultimos_registros_procesados = []

                # NUEVO: Analizar completitud de registros
                try:
                    from core.validation_checker import analizar_batch_registros

                    numeros_peticion_procesados = self._ultimos_registros_procesados
                    logging.info(f"🔍 Analizando completitud de {len(numeros_peticion_procesados)} registros...")
                    analisis = analizar_batch_registros(numeros_peticion_procesados)

                    logging.info(f"✅ Análisis completado:")
                    logging.info(f"   • Completos: {analisis['resumen']['completos']}")
                    logging.info(f"   • Incompletos: {analisis['resumen']['incompletos']}")

                    # Actualizar vista antes de mostrar ventana
                    try:
                        self.refresh_data_and_table()
                        self.after(500, self._delayed_refresh_after_processing)

                        if hasattr(self, 'enhanced_dashboard'):
                            self.enhanced_dashboard.refresh_all_data()
                    except Exception as e:
                        logging.warning(f"⚠️ Error en refresh: {e}")

                    # Actualizar lista de archivos
                    self._refresh_files_list()

                    # Mostrar ventana de resultados con análisis de completitud
                    from core.ventana_resultados_importacion import mostrar_ventana_resultados

                    mostrar_ventana_resultados(
                        parent=self,
                        completos=analisis['completos'],
                        incompletos=analisis['incompletos'],
                        resumen=analisis['resumen'],
                        callback_auditar=self._mostrar_selector_tipo_auditoria,
                        callback_continuar=self._nav_to_visualizar
                    )

                except Exception as e:
                    # Fallback al flujo original si hay error en el análisis
                    logging.warning(f"⚠️ Error en análisis de completitud: {e}")
                    logging.info(f"   Usando flujo de importación original")

                    messagebox.showinfo("Procesamiento", f"✅ Archivo procesado exitosamente:\n{records} registros extraídos")

                    # Actualizar la vista de datos y el dashboard
                    self.refresh_data_and_table()

                    # Actualizar el dashboard si existe
                    if hasattr(self, 'enhanced_dashboard'):
                        try:
                            self.enhanced_dashboard.refresh_all_data()
                        except Exception as e:
                            logging.error(f"Error actualizando dashboard: {e}")

                    # Actualizar lista de archivos
                    self._refresh_files_list()

                    # Redirigir a visualizar datos
                    self._nav_to_visualizar()

            except Exception as e:
                messagebox.showerror("Error", f"❌ Error procesando el archivo:\n{str(e)}")

    def _select_pdf_folder(self):
        """Seleccionar una carpeta con archivos PDF con flujo completo de análisis"""
        folder_path = filedialog.askdirectory(
            title="Seleccionar carpeta con PDFs",
            initialdir=os.path.join(os.getcwd(), "pdfs_patologia") if os.path.exists("pdfs_patologia") else os.getcwd()
        )
        if folder_path:
            # Usar helper para obtener PDFs (retorna rutas completas)
            pdf_files = ocr_helpers.obtener_pdfs_en_carpeta(folder_path)
            if pdf_files:
                # NUEVO: Limpiar lista de registros procesados y obtener peticiones existentes antes del procesamiento
                self._ultimos_registros_procesados = []
                peticiones_antes = set()
                try:
                    import sqlite3
                    from core.database_manager import DB_FILE
                    conn = sqlite3.connect(DB_FILE)
                    cursor = conn.cursor()
                    cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
                    peticiones_antes = set(row[0] for row in cursor.fetchall() if row[0])
                    conn.close()
                except Exception as e:
                    logging.warning(f"Error obteniendo peticiones existentes: {e}")

                processed_count = 0
                total_records = 0
                errors = []

                for pdf_path in pdf_files:
                    try:
                        # V5.3.9: _process_file ahora retorna (records_count, correcciones)
                        records, correcciones = self._process_file(pdf_path)
                        processed_count += 1
                        total_records += records
                    except Exception as e:
                        pdf_name = os.path.basename(pdf_path)
                        errors.append(f"{pdf_name}: {str(e)}")

                # NUEVO: Obtener los números de petición de los registros recién procesados
                if processed_count > 0:
                    try:
                        import sqlite3
                        from core.database_manager import DB_FILE
                        conn = sqlite3.connect(DB_FILE)
                        cursor = conn.cursor()
                        cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
                        peticiones_despues = set(row[0] for row in cursor.fetchall() if row[0])
                        conn.close()

                        # Calcular la diferencia: nuevos registros = después - antes
                        nuevas_peticiones = list(peticiones_despues - peticiones_antes)
                        self._ultimos_registros_procesados = nuevas_peticiones
                        # V5.3.9.3: Usar logging en lugar de print (stdout puede estar cerrado)
                        logging.info(f"📋 Registros nuevos detectados: {len(nuevas_peticiones)}")
                        if nuevas_peticiones:
                            logging.info(f"   IDs: {', '.join(nuevas_peticiones[:5])}" + (" ..." if len(nuevas_peticiones) > 5 else ""))
                    except Exception as e:
                        logging.warning(f"⚠️ Error capturando nuevos registros: {e}")
                        self._ultimos_registros_procesados = []

                    # NUEVO: Analizar completitud de registros
                    try:
                        from core.validation_checker import analizar_batch_registros

                        numeros_peticion_procesados = self._ultimos_registros_procesados
                        logging.info(f"🔍 Analizando completitud de {len(numeros_peticion_procesados)} registros...")
                        analisis = analizar_batch_registros(numeros_peticion_procesados)

                        logging.info(f"✅ Análisis completado:")
                        logging.info(f"   • Completos: {analisis['resumen']['completos']}")
                        logging.info(f"   • Incompletos: {analisis['resumen']['incompletos']}")

                        # Actualizar vista antes de mostrar ventana
                        try:
                            self.refresh_data_and_table()
                            self.after(500, self._delayed_refresh_after_processing)

                            if hasattr(self, 'enhanced_dashboard'):
                                self.enhanced_dashboard.refresh_all_data()
                        except Exception as e:
                            logging.warning(f"⚠️ Error en refresh: {e}")

                        # Actualizar lista de archivos
                        self._refresh_files_list()

                        # Mostrar ventana de resultados con análisis de completitud
                        from core.ventana_resultados_importacion import mostrar_ventana_resultados

                        mostrar_ventana_resultados(
                            parent=self,
                            completos=analisis['completos'],
                            incompletos=analisis['incompletos'],
                            resumen=analisis['resumen'],
                            callback_auditar=self._mostrar_selector_tipo_auditoria,
                            callback_continuar=self._nav_to_visualizar
                        )

                    except Exception as e:
                        # Fallback al flujo original si hay error en el análisis
                        logging.warning(f"⚠️ Error en análisis de completitud: {e}")
                        logging.info(f"   Usando flujo de importación original")

                        # Mostrar resultado tradicional
                        msg = f"✅ Procesados {processed_count} de {len(pdf_files)} archivos\n"
                        msg += f"Total de registros: {total_records}"
                        if errors:
                            msg += f"\n\n❌ Errores en {len(errors)} archivos:\n" + "\n".join(errors[:3])
                            if len(errors) > 3:
                                msg += f"\n... y {len(errors) - 3} más"

                        messagebox.showinfo("Procesamiento completado", msg)

                        # Actualizar vistas
                        self.refresh_data_and_table()
                        if hasattr(self, 'enhanced_dashboard'):
                            try:
                                self.enhanced_dashboard.refresh_all_data()
                            except Exception as e:
                                logging.error(f"Error actualizando dashboard: {e}")
                        self._refresh_files_list()
                else:
                    # No se procesó ningún archivo
                    error_msg = "❌ No se pudo procesar ningún archivo.\n\nErrores encontrados:\n"
                    error_msg += "\n".join(errors[:5])  # Mostrar los primeros 5 errores
                    messagebox.showerror("Error de procesamiento", error_msg)
            else:
                messagebox.showwarning("Sin archivos", "No se encontraron archivos PDF en la carpeta seleccionada.")

    def _refresh_files_list(self):
        """Actualizar la lista de archivos en la carpeta pdfs_patologia"""
        # Verificar que existe el listbox
        if not hasattr(self, 'files_listbox') or self.files_listbox is None:
            logging.warning("Advertencia: files_listbox no está disponible")
            return

        pdfs_path = os.path.join(os.getcwd(), "pdfs_patologia")

        # Crear la carpeta si no existe
        if not os.path.exists(pdfs_path):
            os.makedirs(pdfs_path)

        # Limpiar la lista actual
        self.files_listbox.delete(0, tk.END)

        # Obtener archivos PDF usando helper
        try:
            pdf_paths = ocr_helpers.obtener_pdfs_en_carpeta(pdfs_path)
            pdf_files = [os.path.basename(p) for p in pdf_paths]
            pdf_files.sort()

            for pdf_file in pdf_files:
                self.files_listbox.insert(tk.END, pdf_file)

            if not pdf_files:
                self.files_listbox.insert(tk.END, "(No hay archivos PDF)")

        except Exception as e:
            self.files_listbox.insert(tk.END, f"Error: {str(e)}")

    def _process_selected_files(self):
        """Procesar los archivos seleccionados de la lista (con barra de progreso)"""
        # Verificar que existe el listbox
        if not hasattr(self, 'files_listbox') or self.files_listbox is None:
            messagebox.showerror("Error", "El visor de archivos no está disponible.")
            return

        selected_indices = self.files_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Sin selección", "Por favor seleccione uno o más archivos para procesar.")
            return

        pdfs_path = os.path.join(os.getcwd(), "pdfs_patologia")

        # Pre-validar archivos y verificar duplicados (rápido, main thread)
        files_to_process = []
        for index in selected_indices:
            filename = self.files_listbox.get(index)
            if filename == "(No hay archivos PDF)" or filename.startswith("Error:"):
                continue
            file_path = os.path.join(pdfs_path, filename)
            if not os.path.exists(file_path):
                continue

            duplicado_info = self._verificar_archivo_duplicado(file_path, filename)
            if duplicado_info["es_duplicado"]:
                respuesta = messagebox.askyesno(
                    "Archivo ya importado",
                    f"El archivo '{filename}' ya ha sido importado.\n\n"
                    f"Número de petición: {duplicado_info['numero_peticion']}\n"
                    f"Fecha del informe (PDF): {duplicado_info['fecha_informe']}\n"
                    f"Fecha de importación al sistema: {duplicado_info['fecha_importacion']}\n\n"
                    f"¿Desea ir al visualizador para ver el registro existente?"
                )
                if respuesta:
                    self._redirigir_a_visualizador_con_filtro(duplicado_info['numero_peticion'])
                continue

            files_to_process.append((file_path, filename))

        if not files_to_process:
            messagebox.showinfo("Sin archivos", "No hay archivos nuevos para procesar.")
            return

        # Obtener peticiones existentes antes del procesamiento
        peticiones_antes = set()
        try:
            import sqlite3
            from core.database_manager import DB_FILE
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
            peticiones_antes = set(row[0] for row in cursor.fetchall() if row[0])
            conn.close()
        except Exception as e:
            logging.warning(f"⚠️ Error obteniendo peticiones existentes: {e}")

        # Mostrar overlay de progreso
        self._show_processing_overlay(len(files_to_process))

        # Estado compartido con el thread
        self._processing_result = {
            "done": False,
            "processed_count": 0,
            "total_records": 0,
            "errors": [],
            "correcciones": [],
            "peticiones_antes": peticiones_antes,
            "current_file": "",
            "current_index": 0,
            "total_files": len(files_to_process),
        }

        # Limpiar registros procesados
        self._ultimos_registros_procesados = []

        # Lanzar thread de procesamiento
        thread = threading.Thread(
            target=self._process_files_worker,
            args=(files_to_process,),
            daemon=True
        )
        thread.start()

        # Polling desde main thread para actualizar progreso
        self._poll_processing_progress()

    def _show_processing_overlay(self, num_files):
        """Mostrar overlay con barra de progreso sobre la UI"""
        self._progress_overlay = tk.Toplevel(self)
        overlay = self._progress_overlay
        overlay.title("Procesando PDFs...")
        overlay.transient(self)
        overlay.grab_set()
        overlay.resizable(False, False)
        overlay.protocol("WM_DELETE_WINDOW", lambda: None)  # No se puede cerrar

        # Centrar ventana
        w, h = 480, 200
        x = self.winfo_x() + (self.winfo_width() - w) // 2
        y = self.winfo_y() + (self.winfo_height() - h) // 2
        overlay.geometry(f"{w}x{h}+{x}+{y}")

        frame = ttk.Frame(overlay, padding=30)
        frame.pack(fill=BOTH, expand=True)

        ttk.Label(
            frame,
            text="⏳ Procesando archivos PDF...",
            font=("Segoe UI", 13, "bold"),
        ).pack(pady=(0, 5))

        self._progress_status_label = ttk.Label(
            frame,
            text=f"Preparando {num_files} archivo(s)...",
            font=("Segoe UI", 10),
        )
        self._progress_status_label.pack(pady=(0, 15))

        self._progress_bar = ttk.Progressbar(
            frame,
            mode="determinate",
            length=400,
            maximum=num_files,
            bootstyle="success-striped",
        )
        self._progress_bar.pack(pady=(0, 10))

        self._progress_detail_label = ttk.Label(
            frame,
            text="El OCR puede tardar varios minutos por archivo...",
            font=("Segoe UI", 9),
            foreground="gray",
        )
        self._progress_detail_label.pack()

    def _process_files_worker(self, files_to_process):
        """Worker thread: procesa PDFs (pesado, NO toca UI)"""
        result = self._processing_result

        for i, (file_path, filename) in enumerate(files_to_process):
            result["current_file"] = filename
            result["current_index"] = i

            try:
                records_count, correcciones = self._process_file(file_path)
                result["processed_count"] += 1
                result["total_records"] += records_count
                if correcciones:
                    result["correcciones"].extend(correcciones)
            except Exception as e:
                result["errors"].append(f"{filename}: {str(e)}")
                logging.error(f"❌ Error procesando {filename}: {e}")

        result["done"] = True

    def _poll_processing_progress(self):
        """Polling desde main thread: actualiza barra de progreso"""
        result = self._processing_result

        if not result["done"]:
            # Actualizar progreso
            idx = result["current_index"]
            filename = result["current_file"]
            total = result["total_files"]

            if filename:
                self._progress_status_label.configure(
                    text=f"Procesando ({idx + 1}/{total}): {filename}"
                )
                self._progress_bar.configure(value=idx)

            # Seguir haciendo polling cada 500ms
            self.after(500, self._poll_processing_progress)
            return

        # Procesamiento terminado - cerrar overlay
        self._progress_bar.configure(value=result["total_files"])
        self._progress_status_label.configure(text="✅ Procesamiento completado")
        self.after(600, self._on_processing_complete)

    def _on_processing_complete(self):
        """Callback main thread: mostrar resultados después del procesamiento"""
        result = self._processing_result

        # Cerrar overlay
        if hasattr(self, '_progress_overlay') and self._progress_overlay:
            self._progress_overlay.grab_release()
            self._progress_overlay.destroy()
            self._progress_overlay = None

        processed_count = result["processed_count"]
        total_records = result["total_records"]
        errors = result["errors"]
        peticiones_antes = result["peticiones_antes"]

        if processed_count > 0:
            # Obtener nuevos registros
            try:
                import sqlite3
                from core.database_manager import DB_FILE
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT "Numero de caso" FROM informes_ihq')
                peticiones_despues = set(row[0] for row in cursor.fetchall() if row[0])
                conn.close()

                nuevas_peticiones = list(peticiones_despues - peticiones_antes)
                self._ultimos_registros_procesados = nuevas_peticiones
                logging.info(f"📋 Registros nuevos detectados: {len(nuevas_peticiones)}")
            except Exception as e:
                logging.warning(f"⚠️ Error capturando nuevos registros: {e}")
                self._ultimos_registros_procesados = []

            numeros_peticion_procesados = self._ultimos_registros_procesados

            # Analizar completitud
            try:
                from core.validation_checker import analizar_batch_registros

                logging.info(f"🔍 Analizando completitud de {len(numeros_peticion_procesados)} registros...")
                analisis = analizar_batch_registros(numeros_peticion_procesados)

                logging.info(f"✅ Análisis completado:")
                logging.info(f"   • Completos: {analisis['resumen']['completos']}")
                logging.info(f"   • Incompletos: {analisis['resumen']['incompletos']}")

                try:
                    self.refresh_data_and_table()
                    self.after(500, self._delayed_refresh_after_processing)
                    if hasattr(self, 'enhanced_dashboard'):
                        self.enhanced_dashboard.refresh_all_data()
                except Exception as e:
                    logging.warning(f"⚠️ Error en refresh: {e}")

                from core.ventana_resultados_importacion import mostrar_ventana_resultados

                mostrar_ventana_resultados(
                    parent=self,
                    completos=analisis['completos'],
                    incompletos=analisis['incompletos'],
                    resumen=analisis['resumen'],
                    callback_auditar=self._mostrar_selector_tipo_auditoria,
                    callback_continuar=self._nav_to_visualizar
                )

            except Exception as e:
                logging.warning(f"⚠️ Error en análisis de completitud: {e}")

                success_msg = f"✅ Procesamiento completado:\n"
                success_msg += f"• {processed_count} archivos procesados\n"
                success_msg += f"• {total_records} registros extraídos y guardados en BD"

                if errors:
                    success_msg += f"\n\n⚠️ Errores en {len(errors)} archivos:\n"
                    success_msg += "\n".join(errors[:3])
                    if len(errors) > 3:
                        success_msg += f"\n... y {len(errors) - 3} errores más."

                messagebox.showinfo("Procesamiento completado", success_msg)

                self.refresh_data_and_table()
                self.after(1000, self._delayed_refresh_after_processing)
                if hasattr(self, 'enhanced_dashboard'):
                    self.enhanced_dashboard.refresh_all_data()
                self._nav_to_visualizar()

        else:
            error_msg = "❌ No se pudo procesar ningún archivo.\n\nErrores encontrados:\n"
            error_msg += "\n".join(errors[:5])
            messagebox.showerror("Error de procesamiento", error_msg)

    def _process_file(self, file_path):
        """Procesar un archivo PDF individual

        Returns:
            tuple: (records_count, correcciones_list)
        """
        try:
            filename = os.path.basename(file_path)
            # V4.2.1 FIX: No llamar set_status desde worker thread (no es thread-safe en Python 3.13)
            logging.info(f"Procesando {filename}...")

            # Determinar el tipo de archivo y procesarlo adecuadamente
            if self._is_ihq_file(filename, file_path):
                # Procesar como archivo IHQ (biomarcadores)
                records_processed = self._process_ihq_file(file_path)
                correcciones = []  # IHQ no tiene validación aún
                logging.info(f"✅ {filename}: {records_processed} registros IHQ procesados")
            else:
                # Procesar como archivo general de patología (retorna tuple)
                records_processed, correcciones = self._process_general_file(file_path)
                logging.info(f"✅ {filename}: {records_processed} registros generales procesados")

            # V5.3.9: Usar logging en lugar de print (stdout puede estar cerrado)
            logging.info(f"✅ Procesamiento completado: {file_path} - {records_processed} registros")
            return records_processed, correcciones

        except Exception as e:
            error_msg = f"Error procesando {filename}: {str(e)}"
            logging.error(f"❌ {error_msg}")
            raise Exception(error_msg)

    def _is_ihq_file(self, filename, file_path):
        """Determinar si un archivo es de IHQ basándose en el nombre y contenido"""
        # Criterio 1: Nombre del archivo
        if "ihq" in filename.lower():
            return True
        
        # Criterio 2: Revisar contenido del archivo (muestra)
        try:
            from core.processors.ocr_processor import pdf_to_text_enhanced
            # Solo leer una página para determinar el tipo
            import fitz
            doc = fitz.open(file_path)
            if len(doc) > 0:
                page_text = doc[0].get_text()
                doc.close()
                # Buscar indicadores de IHQ
                ihq_indicators = ['ihq', 'inmunohistoquimica', 'her2', 'ki-67', 'receptor estrogeno']
                return any(indicator in page_text.lower() for indicator in ihq_indicators)
        except Exception:
            pass
        
        return False

    def _process_ihq_file(self, file_path):
        """Procesar archivo IHQ - LÓGICA MOVIDA A core/ihq_processor.py"""
        from core.ihq_processor import process_ihq_file

        # Crear función de log que use el widget de UI
        def log_callback(msg):
            if hasattr(self, 'log_to_widget'):
                self.log_to_widget(msg)

        # Delegar procesamiento a módulo core
        return process_ihq_file(file_path, log_callback)

    def _process_general_file(self, file_path):
        """Procesar archivo general usando el procesador estándar

        Returns:
            tuple: (records_count, correcciones_list)
        """
        try:
            # Importar los módulos necesarios
            from core.processors.ocr_processor import pdf_to_text_enhanced
            from core import unified_extractor as ihq
            from core import database_manager

            # Extraer texto del PDF
            full_text = pdf_to_text_enhanced(file_path)
            if not isinstance(full_text, str):
                full_text = '\n'.join(full_text)

            # Segmentar por informes (usando lógica similar a IHQ pero más general)
            records = []

            # Para archivos generales, puede haber múltiples informes
            # Intentar segmentar por "N. petición" o números de orden
            segments = self._segment_general_reports(full_text)

            if not segments:
                # Si no se puede segmentar, procesar como un solo informe
                segments = [full_text]

            for segment in segments:
                # Extraer datos base usando el procesador IHQ (que maneja datos generales también)
                base_data = ihq.extract_ihq_data(segment)
                base_rows = ihq.map_to_excel_format(base_data)

                if base_rows:
                    records.extend(base_rows)

            if not records:
                raise RuntimeError("No se pudo extraer información del PDF.")

            # Guardar en base de datos
            from core.database_manager import init_db, save_records, update_incomplete_records_with_debug_data
            init_db()
            saved_count = save_records(records)

            # V5.3.9.3: VALIDACIÓN MÉDICO-SERVICIO YA APLICADA EN ihq_processor.py
            # Las correcciones médico-servicio ahora se aplican ANTES de crear debug_maps
            # en ihq_processor.py líneas 119-144, por lo que NO necesitamos volver a aplicarlas aquí.
            # Las correcciones ya están guardadas en los debug_maps y se mostrarán en la ventana.
            correcciones_aplicadas = []
            logging.info("✅ Validación médico-servicio aplicada durante extracción (ihq_processor.py)")

            # REACTIVADO: Actualización automática mejorada para completar datos faltantes
            try:
                logging.info("🔄 Ejecutando actualización automática de registros incompletos...")

                # CORREGIDO: Usar el texto OCR del archivo recién procesado para completar datos
                # Crear archivo DEBUG temporal para este archivo específico
                debug_file_path = self._create_debug_file_for_current_pdf(file_path, full_text)

                # Actualizar usando el DEBUG específico de este archivo
                updated_count = update_incomplete_records_with_debug_data(debug_file_path)
                if updated_count > 0:
                    logging.info(f"✅ Se actualizaron {updated_count} registros con datos completos del archivo actual")

                # NUEVO: Ahora aplicar mapeo específico de órganos usando parse_estudios_table_for_organo
                logging.info("🔄 Aplicando mapeo avanzado de órganos...")
                organ_updated_count = self._update_organs_with_advanced_parsing(full_text, records)
                if organ_updated_count > 0:
                    logging.info(f"✅ Se mapearon {organ_updated_count} órganos adicionales")

            except Exception as e:
                # No fallar el proceso principal si la actualización automática falla
                logging.warning(f"⚠️ Advertencia en actualización automática: {str(e)}")

            # V5.3.9: Retornar tanto el conteo como las correcciones
            return saved_count, correcciones_aplicadas

        except Exception as e:
            raise Exception(f"Error en procesamiento general: {str(e)}")

    def _create_debug_file_for_current_pdf(self, file_path, full_text):
        """Crear archivo DEBUG temporal para el PDF actual"""
        try:
            # Crear nombre de archivo DEBUG basado en el PDF actual
            pdf_name = os.path.basename(file_path)
            debug_filename = f"DEBUG_OCR_OUTPUT_{pdf_name}.txt"
            debug_path = os.path.join("EXCEL", debug_filename)
            
            # Asegurar que el directorio existe
            os.makedirs("EXCEL", exist_ok=True)
            
            # Guardar el texto OCR en formato DEBUG
            with open(debug_path, 'w', encoding='utf-8') as f:
                f.write(f"=== DEBUG OCR OUTPUT PARA {pdf_name} ===\n")
                f.write(f"Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(full_text)

            logging.info(f"📄 Archivo DEBUG creado: {debug_path}")
            return debug_path

        except Exception as e:
            logging.warning(f"⚠️ Error creando archivo DEBUG: {e}")
            # Fallback al archivo DEBUG global si falla
            return None

    def _find_available_debug_files(self):
        """Buscar todos los archivos DEBUG disponibles en el directorio EXCEL"""
        debug_files = []
        excel_dir = "EXCEL"
        
        if os.path.exists(excel_dir):
            for filename in os.listdir(excel_dir):
                if filename.startswith("DEBUG_OCR_OUTPUT_") and filename.endswith(".txt"):
                    debug_path = os.path.join(excel_dir, filename)
                    debug_files.append(debug_path)
                    
        return debug_files

    def _segment_general_reports(self, text):
        """Segmentar texto en informes individuales para archivos generales"""
        segments = []
        
        # Buscar patrones de número de petición más generales
        patterns = [
            r'(?i)(?:N[°.\s]*|No\.\s*|Nº\s*|N\s*)?petici[oó]n\s*[:\-]?\s*([A-Z]?\d{6,})',
            r'(?i)(?:registro|orden|numero|no\.?)\s*[:\-]?\s*(\d{4,})',
            r'(?i)(\d{4,})\s*(?:patolog[ií]a|biopsia|citolog[ií]a)'
        ]
        
        # Intentar segmentar por cualquiera de los patrones
        for pattern in patterns:
            matches = list(re.finditer(pattern, text))
            if len(matches) > 1:  # Solo si encontramos múltiples coincidencias
                starts = [(m.start(), m.group(1)) for m in matches]
                starts.sort()
                
                for i, (start, code) in enumerate(starts):
                    if i + 1 < len(starts):
                        end = starts[i + 1][0]
                        segment = text[start:end].strip()
                    else:
                        segment = text[start:].strip()
                    
                    if len(segment) > 100:  # Solo segmentos con contenido suficiente
                        segments.append(segment)
                
                break  # Usar el primer patrón que funcione
        
        return segments

    def _export_full_database_professional(self):
        """Exportar toda la base de datos a Excel con presentación profesional y diálogo de ubicación"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Obtener todos los datos de la base de datos
            from core.database_manager import get_all_records_as_dataframe
            df_complete = get_all_records_as_dataframe()
            
            if df_complete.empty:
                messagebox.showwarning("Advertencia", "No hay datos en la base de datos para exportar.")
                return
                
            # Diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                title="Exportar Base de Datos Completa - EVARISIS",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                self._create_professional_excel_export(df_complete, file_path, "completa")
                
                # Redirigir a pestaña de exportaciones
                if hasattr(self, 'notebook'):
                    self.notebook.select(5)  # Pestaña de Exportaciones
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al exportar:\n{str(e)}")
            logging.error(f"Error detallado: {e}", exc_info=True)

    def _export_full_database_direct(self):
        """Exportar toda la base de datos directamente a la carpeta de Documentos sin diálogo"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            
            # Obtener todos los datos de la base de datos
            from core.database_manager import get_all_records_as_dataframe
            df_complete = get_all_records_as_dataframe()
            
            if df_complete.empty:
                messagebox.showwarning("Advertencia", "No hay datos en la base de datos para exportar.")
                return
            
            # Generar nombre automático usando helper
            filename = export_helpers.generar_nombre_archivo_export(
                prefijo="BD_Completa_HUV",
                tipo="xlsx",
                incluir_timestamp=True
            )
            
            # Ruta automática a Documentos
            export_base_path = os.path.join(os.path.expanduser("~"), "Documents", "EVARISIS CIRUGÍA ONCOLÓGICA", "Exportaciones Base de datos")
            excel_dir = os.path.join(export_base_path, "Excel")
            os.makedirs(excel_dir, exist_ok=True)
            
            file_path = os.path.join(excel_dir, filename)
            
            self._create_professional_excel_export(df_complete, file_path, "completa")
            
            # Redirigir a pestaña de exportaciones
            if hasattr(self, 'notebook'):
                self.notebook.select(5)  # Pestaña de Exportaciones
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al exportar:\n{str(e)}")
            logging.error(f"Error detallado: {e}", exc_info=True)

    def _export_selected_data_professional(self):
        """Exportar solo datos seleccionados a Excel con presentación profesional y diálogo de ubicación"""
        try:
            import pandas as pd
            from datetime import datetime
            
            # Obtener elementos seleccionados del treeview
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("Sin Selección", "No hay elementos seleccionados para exportar")
                return

            # CORREGIDO: Obtener los datos reales de las filas seleccionadas
            selected_rows_data = []
            for item in selected_items:
                # tksheet: Usar get_row_data() en lugar de .item()
                values = self.sheet.get_row_data(item)
                if values:
                    # Buscar el registro correspondiente en master_df usando el número de petición
                    numero_peticion = values[0]  # Asumiendo que la primera columna es número de petición
                    matching_row = self.master_df[self.master_df.iloc[:, 0] == numero_peticion]
                    if not matching_row.empty:
                        selected_rows_data.append(matching_row.iloc[0])

            if not selected_rows_data:
                messagebox.showwarning("Sin Datos", "No se pudieron obtener los datos de la selección")
                return

            # Crear DataFrame con solo los registros seleccionados
            selected_df = pd.DataFrame(selected_rows_data)
            
            # Diálogo para guardar archivo
            file_path = filedialog.asksaveasfilename(
                title=f"Exportar Selección ({len(selected_df)} registros) - EVARISIS",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
            )
            
            if file_path:
                self._create_professional_excel_export(selected_df, file_path, "seleccion")
                
                # Redirigir a pestaña de exportaciones si el archivo está en la carpeta estándar
                documents_path = os.path.join(os.path.expanduser("~"), "Documents")
                if file_path.startswith(documents_path) and hasattr(self, 'notebook'):
                    self.notebook.select(5)  # Pestaña de Exportaciones
                
        except Exception as e:
            messagebox.showerror("Error", f"❌ Error al exportar:\n{str(e)}")
            logging.error(f"Error detallado: {e}", exc_info=True)

    def _create_professional_excel_export(self, df_data, file_path, export_type):
        """Crear archivo Excel con formato profesional (función común)"""
        try:
            import pandas as pd
            from datetime import datetime
            import os
            # Crear el archivo Excel con múltiples hojas
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                
                # ========== HOJA 1: PRESENTACIÓN ==========
                # Crear DataFrame para la presentación
                export_title = "Exportación Completa" if export_type == "completa" else "Exportación de Selección"
                
                presentation_data = [
                    ["EVARISIS CIRUGÍA ONCOLÓGICA", ""],
                    [export_title, ""],
                    ["", ""],
                    ["Información del Reporte", ""],
                    ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""],
                    ["Fecha y Hora de Exportación:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                    ["Usuario:", self.info_usuario.get("nombre", "Sistema")],
                    ["Cargo:", self.info_usuario.get("cargo", "N/A")],
                    ["", ""],
                    ["Estadísticas de la Exportación", ""],
                    ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""],
                    ["Total de Registros:", len(df_data)],
                    ["Número de Campos:", len(df_data.columns)],
                    ["", ""],
                ]
                
                # Calcular estadísticas adicionales
                fecha_cols = [col for col in df_data.columns if 'fecha' in col.lower()]
                if fecha_cols:
                    try:
                        for col in fecha_cols:
                            fechas = pd.to_datetime(df_data[col], errors='coerce')
                            fechas_validas = fechas.dropna()
                            if not fechas_validas.empty:
                                fecha_min = fechas_validas.min().strftime("%d/%m/%Y")
                                fecha_max = fechas_validas.max().strftime("%d/%m/%Y")
                                presentation_data.extend([
                                    [f"Rango de Fechas ({col}):", f"{fecha_min} - {fecha_max}"],
                                ])
                                break
                    except:
                        pass
                
                # Servicios únicos
                servicio_cols = [col for col in df_data.columns if 'servicio' in col.lower()]
                if servicio_cols:
                    unique_services = df_data[servicio_cols[0]].nunique()
                    presentation_data.append(["Servicios Únicos:", unique_services])
                
                # Casos malignos
                malignidad_cols = [col for col in df_data.columns if 'malign' in col.lower()]
                if malignidad_cols:
                    malignant_count = (df_data[malignidad_cols[0]].str.contains('PRESENTE', case=False, na=False)).sum()
                    presentation_data.append(["Casos con Malignidad:", malignant_count])
                
                presentation_data.extend([
                    ["", ""],
                    ["Descripción", ""],
                    ["━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", ""],
                    ["Este archivo contiene la exportación", ""],
                    ["de la base de datos del sistema EVARISIS", ""],
                    ["Cirugía Oncológica.", ""],
                    ["", ""],
                    ["La información incluye todos los campos", ""],
                    ["almacenados para cada informe médico:", ""],
                    ["- Datos del paciente", ""],
                    ["- Información clínica", ""],
                    ["- Resultados de laboratorio", ""],
                    ["- Análisis histopatológicos", ""],
                    ["- Biomarcadores (IHQ)", ""],
                    ["- Fechas y responsables", ""],
                    ["", ""],
                    ["Hospital Universitario del Valle", ""],
                    ["Sistema EVARISIS © 2025", ""],
                ])
                
                df_presentation = pd.DataFrame(presentation_data, columns=["Campo", "Valor"])
                df_presentation.to_excel(writer, sheet_name='Presentación', index=False)
                
                # ========== HOJA 2: DATOS COMPLETOS ==========
                sheet_name = 'Datos_Completos' if export_type == "completa" else 'Datos_Seleccionados'
                df_data.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # ========== FORMATO ==========
                from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
                
                # Formatear hoja de presentación
                ws_pres = writer.sheets['Presentación']
                
                # Título principal
                ws_pres['A1'].font = Font(size=18, bold=True, color="FFFFFF")
                ws_pres['A1'].fill = PatternFill(start_color="1B4F72", end_color="1B4F72", fill_type="solid")
                ws_pres['A1'].alignment = Alignment(horizontal="center", vertical="center")
                ws_pres.merge_cells('A1:B1')
                
                # Subtítulo
                ws_pres['A2'].font = Font(size=14, bold=True, color="FFFFFF")
                ws_pres['A2'].fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
                ws_pres['A2'].alignment = Alignment(horizontal="center", vertical="center")
                ws_pres.merge_cells('A2:B2')
                
                # Secciones
                section_font = Font(size=12, bold=True, color="1B4F72")
                for row in range(1, len(presentation_data) + 2):
                    cell_value = ws_pres[f'A{row}'].value
                    if cell_value and ("Información" in str(cell_value) or "Estadísticas" in str(cell_value) or "Descripción" in str(cell_value)):
                        ws_pres[f'A{row}'].font = section_font
                        ws_pres.merge_cells(f'A{row}:B{row}')
                
                # Ajustar ancho de columnas
                ws_pres.column_dimensions['A'].width = 40
                ws_pres.column_dimensions['B'].width = 30
                
                # Formatear hoja de datos
                ws_data = writer.sheets[sheet_name]
                
                # Headers
                header_font = Font(bold=True, color="FFFFFF")
                header_fill = PatternFill(start_color="2E86AB", end_color="2E86AB", fill_type="solid")
                header_alignment = Alignment(horizontal="center", vertical="center")
                
                for cell in ws_data[1]:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                
                # Ajustar ancho de columnas automáticamente
                for column in ws_data.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)  # Máximo 50 caracteres
                    ws_data.column_dimensions[column_letter].width = adjusted_width
            
            # Mensaje de confirmación
            record_text = "completos" if export_type == "completa" else "seleccionados"
            messagebox.showinfo(
                "Exportación Exitosa", 
                f"✅ Base de datos exportada exitosamente!\n\n"
                f"📊 {len(df_data)} registros {record_text} exportados\n"
                f"📋 {len(df_data.columns)} campos por registro\n"
                f"📁 Archivo: {os.path.basename(file_path)}\n\n"
                f"El archivo incluye:\n"
                f"• Hoja de presentación con estadísticas\n"
                f"• Datos {record_text} de los registros"
            )
            
        except Exception as e:
            raise e

    def _export_current_record(self):
        """Exportar el registro actualmente seleccionado"""
        try:
            selection = self.tree.selection()
            if not selection:
                messagebox.showwarning("Advertencia", "No hay registro seleccionado.")
                return
                
            # Tomar solo el primer registro seleccionado
            item = selection[0]
            self._export_selected_data_professional()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar registro: {str(e)}")

    def _copy_details(self):
        """Copiar detalles del registro al clipboard"""
        try:
            details_text = self.detail_textbox.get("1.0", tk.END)
            if details_text.strip():
                self.clipboard_clear()
                self.clipboard_append(details_text)
                messagebox.showinfo("Copiado", "Detalles copiados al portapapeles")
            else:
                messagebox.showwarning("Advertencia", "No hay detalles para copiar")
        except Exception as e:
            messagebox.showerror("Error", f"Error al copiar: {str(e)}")

    def _on_double_click(self, event):
        """Manejar doble clic en la tabla"""
        selection = self.tree.selection()
        if selection:
            # Expandir detalles o realizar acción específica
            self.mostrar_detalle_registro(event)

    def _init_treeview_style(self):
        """
        Define el estilo 'Custom.Treeview' usando los colores del tema actual de TTKBootstrap.
        """
        try:
            from tkinter import ttk as _ttk
            s = _ttk.Style()

            # Usar colores del tema TTKBootstrap actual
            bg_color = self.style.colors.bg or "#ffffff"
            fg_color = self.style.colors.fg or "#000000"  
            primary_color = self.style.colors.primary or "#0d6efd"
            secondary_color = self.style.colors.secondary or "#6c757d"

            s.configure(
                "Custom.Treeview",
                background=bg_color,
                fieldbackground=bg_color,
                foreground=fg_color,
                rowheight=26,
                borderwidth=0,
            )
            s.map(
                "Custom.Treeview",
                background=[("selected", primary_color)],
                foreground=[("selected", "white")],
            )
            s.configure(
                "Custom.Treeview.Heading",
                background=secondary_color,
                foreground="white",
                relief="flat",
                padding=6,
            )
        except Exception as e:
            logging.warning(f"No se pudo configurar Custom.Treeview: {e}")

def main():
    """
    Función principal que configura el entorno y lanza la aplicación.
    """
    logging.info("Iniciando EVARISIS Gestor H.U.V...")

    # Configurar el parser de argumentos
    parser = argparse.ArgumentParser(description="EVARISIS CIRUGÍA ONCOLÓGICA")
    
    parser.add_argument("--nombre", type=str, default="Usuario Sistema", help="Nombre del usuario logueado.")
    parser.add_argument("--cargo", type=str, default="Administrador", help="Cargo del usuario logueado.")
    parser.add_argument("--foto", type=str, default="SIN_FOTO", help="Ruta a la foto de perfil del usuario.")
    parser.add_argument("--tema", type=str, default="dark", help="Tema visual de la aplicación.")
    parser.add_argument("--ruta-fotos", type=str, default="", help="Ruta al directorio base de fotos de usuarios.")
    parser.add_argument("--ruta-datos", type=str, default="", help="Ruta a datos de EVARISIS.")
    parser.add_argument(
        "--lanzado-por-evarisis",
        action='store_true',
        help="Bandera interna para verificar el lanzamiento desde la app principal."
    )
    parser.add_argument(
        "--modo-independiente",
        action='store_true',
        help="Permite ejecutar la aplicación de forma independiente (sin EVARISIS)."
    )
    
    args = parser.parse_args()

    # 1. Configuramos Tesseract antes de que cualquier otra cosa lo necesite
    configure_tesseract()

    # Configurar información del usuario
    info_usuario_recibida = {
        "nombre": args.nombre,
        "cargo": args.cargo,
        "ruta_foto": args.foto,
        "ruta_directorio_fotos": args.ruta_fotos
    }
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Mapear tema del argumento a tema TTKBootstrap
    tema_ttk = THEME_MAP.get(args.tema, "darkly")
    
    # Crear y ejecutar la aplicación
    app = App(info_usuario=info_usuario_recibida, tema=tema_ttk)
    app.mainloop()

    logging.info("Aplicacion cerrada. Hasta luego!")


# === NUEVAS FUNCIONES PARA DETECCIÓN DE DUPLICADOS ===
def _verificar_archivo_duplicado(self, file_path, filename):
    """
    Verifica si un archivo ya ha sido importado basándose en contenido y número de petición
    """
    try:
        # Extraer número de petición del archivo
        from core.processors.ocr_processor import pdf_to_text_enhanced
        from core.extractors.patient_extractor import PATIENT_PATTERNS
        import re
        
        # Obtener texto del PDF
        texto = pdf_to_text_enhanced(file_path)

        # Buscar número de petición
        match = re.search(PATIENT_PATTERNS['numero_peticion']['patrones'][0], texto, re.IGNORECASE)
        if not match:
            return {"es_duplicado": False, "razon": "No se pudo extraer número de petición"}
        
        numero_peticion = match.group(1).strip()
        
        # Verificar en base de datos
        from core.database_manager import verificar_duplicado_por_peticion
        resultado = verificar_duplicado_por_peticion(numero_peticion)
        
        if resultado.get("existe", False):
            registro = resultado.get("registro", {})
            return {
                "es_duplicado": True,
                "numero_peticion": numero_peticion,
                "fecha_informe": registro.get("Fecha Informe", "N/A"),
                "fecha_importacion": registro.get("Fecha Ingreso Base de Datos", "N/A"),  # FECHA REAL DE IMPORTACIÓN
                "registro": registro
            }
        else:
            return {"es_duplicado": False}

    except Exception as e:
        logging.error(f"Error verificando duplicado para {filename}: {e}")
        return {"es_duplicado": False, "error": str(e)}

# Agregar estas funciones como métodos de la clase App
App._verificar_archivo_duplicado = _verificar_archivo_duplicado

def _redirigir_a_visualizador_con_filtro(self, numero_peticion):
    """
    Redirige al visualizador de datos y resalta el registro específico
    """
    try:
        # Navegar a visualizador
        self._nav_to_visualizar()
        
        # Aplicar filtro para mostrar solo ese registro
        if hasattr(self, 'tree') and self.tree:
            # Limpiar filtros existentes
            self._clear_filters()
            
            # Aplicar filtro por número de petición
            for item in self.tree.get_children():
                values = self.tree.item(item)['values']
                if values and len(values) > 0:
                    # Buscar la columna del número de petición
                    if numero_peticion in str(values[0]):  # Asumiendo que está en la primera columna
                        self.tree.selection_set(item)
                        self.tree.focus(item)
                        self.tree.see(item)
                        break
                        
        messagebox.showinfo(
            "Registro encontrado",
            f"Se ha localizado y resaltado el registro con número de petición: {numero_peticion}"
        )
        
    except Exception as e:
        logging.error(f"Error redirigiendo al visualizador: {e}")

App._redirigir_a_visualizador_con_filtro = _redirigir_a_visualizador_con_filtro

def _actualizar_lista_archivos_con_estado(self):
    """
    Actualiza la lista de archivos mostrando en ROJO los ya importados
    """
    try:
        if not hasattr(self, 'files_listbox') or self.files_listbox is None:
            return
            
        # Limpiar lista actual
        self.files_listbox.delete(0, tk.END)
        
        pdfs_path = os.path.join(os.getcwd(), "pdfs_patologia")
        if not os.path.exists(pdfs_path):
            self.files_listbox.insert(tk.END, "(No existe la carpeta pdfs_patologia)")
            return
        
        # Usar helper para obtener PDFs
        pdf_paths = ocr_helpers.obtener_pdfs_en_carpeta(pdfs_path)

        if not pdf_paths:
            self.files_listbox.insert(tk.END, "(No hay archivos PDF)")
            return

        # Procesar cada archivo para verificar estado
        for file_path in sorted(pdf_paths):
            archivo = os.path.basename(file_path)
            duplicado_info = self._verificar_archivo_duplicado(file_path, archivo)
            
            if duplicado_info.get("es_duplicado", False):
                # Marcar como duplicado en rojo
                display_text = f"🔴 {archivo} (YA IMPORTADO)"
                self.files_listbox.insert(tk.END, display_text)
            else:
                # Archivo nuevo en verde
                display_text = f"🟢 {archivo}"
                self.files_listbox.insert(tk.END, display_text)
                
    except Exception as e:
        logging.error(f"Error actualizando lista de archivos: {e}")

App._actualizar_lista_archivos_con_estado = _actualizar_lista_archivos_con_estado

def _clear_filters(self):
    """
    Limpia todos los filtros activos en el visualizador
    """
    try:
        # Limpiar combos de filtro si existen
        if hasattr(self, 'cmb_servicio') and self.cmb_servicio:
            self.cmb_servicio.set("")
        if hasattr(self, 'cmb_malig') and self.cmb_malig:
            self.cmb_malig.set("")
        if hasattr(self, 'cmb_resp') and self.cmb_resp:
            self.cmb_resp.set("")
            
        # Refrescar datos
        self.refresh_data()

    except Exception as e:
        logging.error(f"Error limpiando filtros: {e}")

App._clear_filters = _clear_filters

def _crear_footer_inteligente(self):
    """
    Crea un footer inteligente con información de rangos de fechas y distribución mensual
    """
    try:
        if self.master_df.empty:
            return "📂 Base de datos vacía - Importa archivos para comenzar"
        
        # Obtener información de fechas y distribución
        from core.database_manager import get_fecha_range_registros, get_distribucion_mensual
        # MESES_ES está definido al inicio del archivo
        from datetime import datetime
        
        fecha_info = get_fecha_range_registros()
        distribucion = get_distribucion_mensual()
        
        if fecha_info.get("error") or not fecha_info.get("fecha_min"):
            return f"💾 Base de datos cargada: {len(self.master_df)} registros (fechas no disponibles)"
        
        # Formatear fechas - Ya vienen en formato DD/MM/YYYY desde database_manager
        fecha_min = fecha_info["fecha_min"]
        fecha_max = fecha_info["fecha_max"]

        # Crear distribución legible - CORREGIDO: Mostrar TODOS los meses
        if distribucion and not distribucion.get("error"):
            dist_texto = []
            for mes_ano, cantidad in sorted(distribucion.items()):
                try:
                    año, mes = mes_ano.split('-')
                    mes_nombre = MESES_ES.get(int(mes), f"Mes {mes}")
                    # Formato compacto: Ene 25: 1
                    dist_texto.append(f"{mes_nombre[:3]} {año[2:]}: {cantidad}")
                except:
                    dist_texto.append(f"{mes_ano}: {cantidad}")

            # Mostrar TODOS los meses
            dist_resumen = " | ".join(dist_texto)
        else:
            dist_resumen = "Distribución no disponible"
        
        footer_text = f"💾 Base de datos cargada desde {fecha_min} hasta {fecha_max} | "
        footer_text += f"📊 Total: {len(self.master_df)} registros | "
        footer_text += f"📅 Distribución: {dist_resumen}"
        
        return footer_text

    except Exception as e:
        logging.error(f"Error creando footer inteligente: {e}")
        return f"💾 Base de datos cargada: {len(self.master_df)} registros"

App._crear_footer_inteligente = _crear_footer_inteligente

def _update_organs_with_advanced_parsing(self, full_text, records):
    """
    Aplica mapeo avanzado de órganos usando parse_estudios_table_for_organo
    """
    try:
        from core.unified_extractor import parse_estudios_table_for_organo
        from core.database_manager import get_connection
        
        # Extraer órganos usando el parser avanzado
        organos_mapeados = parse_estudios_table_for_organo(full_text)
        
        if not organos_mapeados:
            return 0

        logging.info(f"Organos detectados por parser avanzado: {organos_mapeados}")
        
        # Actualizar registros que no tienen órgano o tienen órgano incompleto
        updated_count = 0
        
        # Obtener números de petición de los registros recién procesados
        numeros_peticion = []
        for record in records:
            if isinstance(record, dict) and 'Numero de caso' in record:
                numeros_peticion.append(record['Numero de caso'])
        
        if numeros_peticion:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Actualizar solo registros recién procesados que no tienen órgano completo
                for numero_peticion in numeros_peticion:
                    cursor.execute("""
                        UPDATE informes_ihq 
                        SET "Organo" = ?
                        WHERE "Numero de caso" = ? 
                        AND ("Organo" IS NULL 
                             OR "Organo" = '' 
                             OR "Organo" = 'NO ENCONTRADO')
                    """, (organos_mapeados, numero_peticion))
                    
                    if cursor.rowcount > 0:
                        updated_count += cursor.rowcount
                
                conn.commit()
        
        return updated_count

    except Exception as e:
        logging.error(f"Error en mapeo avanzado de organos: {e}")
        return 0

App._update_organs_with_advanced_parsing = _update_organs_with_advanced_parsing


if __name__ == "__main__":
    main()