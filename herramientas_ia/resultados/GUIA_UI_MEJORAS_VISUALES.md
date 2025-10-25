# GUIA COMPLETA DE MEJORAS VISUALES - UI EVARISIS

**Hospital Universitario del Valle - Sistema EVARISIS**
**Fecha**: 2025-10-24
**Version**: 1.0.0
**Autor**: Core Editor Agent (EVARISIS)

---

## TABLA DE CONTENIDOS

1. [Mapa Completo de la UI Actual](#1-mapa-completo-de-la-ui-actual)
2. [Sistema de Design Tokens](#2-sistema-de-design-tokens)
3. [Biblioteca de Patrones Visuales](#3-biblioteca-de-patrones-visuales)
4. [Componentes Reutilizables](#4-componentes-reutilizables)
5. [Guias de Mejora Especificas](#5-guias-de-mejora-especificas)
6. [Ejemplos Antes/Despues](#6-ejemplos-antesdespues)
7. [Checklist de Revision UI](#7-checklist-de-revision-ui)

---

## 1. MAPA COMPLETO DE LA UI ACTUAL

### 1.1 Arquitectura de Archivos UI

```
EVARISIS UI Structure
│
├── ui.py (ARCHIVO PRINCIPAL - 270KB)
│   ├── App (clase principal)
│   │   ├── Header Institucional
│   │   ├── Navegacion Flotante
│   │   ├── Pantalla de Bienvenida
│   │   ├── Sistema de Pestanas (Notebook)
│   │   │   ├── Pestana: Procesar Datos
│   │   │   ├── Pestana: Dashboard BD
│   │   │   ├── Pestana: Calendario
│   │   │   ├── Pestana: Automatizacion Web
│   │   │   └── Pestana: Acerca de
│   │   └── Componentes Comunes
│   │       ├── Metric Cards
│   │       ├── LabelFrames con Iconos
│   │       └── Scroll Containers
│
├── core/ventana_selector_auditoria.py (194 lineas)
│   └── VentanaSelectorAuditoria
│       ├── Modal Card: Auditoria Parcial
│       ├── Modal Card: Auditoria Completa
│       └── Scroll Container
│
├── core/ventana_resultados_importacion.py (535 lineas)
│   └── VentanaResultadosImportacion (MAXIMIZADA)
│       ├── Seccion Resumen (4 badges estadisticos)
│       ├── Seccion Correcciones IA
│       ├── Seccion Completos (tabla virtualizada)
│       ├── Seccion Incompletos (tabla virtualizada)
│       └── Scroll Container Vertical
│
├── core/ventana_auditoria_ia.py (914 lineas)
│   └── VentanaAuditoriaIA (MAXIMIZADA)
│       ├── Header con Progreso
│       ├── Logs en Tiempo Real
│       │   └── Text Widget con Tags de Color
│       ├── Sistema de Lotes Dinamicos
│       └── Prevencion Auto-Minimize
│
├── core/enhanced_database_dashboard.py (28K+ tokens)
│   └── EnhancedDatabaseDashboard
│       ├── Notebook con 6 Pestanas
│       │   ├── Estadisticas Generales
│       │   ├── Biomarcadores
│       │   ├── Analisis Temporal
│       │   ├── Analisis Malignidad
│       │   ├── Importar Datos
│       │   └── Exportaciones
│       ├── Metric Cards Grid
│       ├── Graficos Matplotlib/Seaborn
│       └── Tablas Virtualizadas (tksheet)
│
├── core/enhanced_export_system.py
│   └── EnhancedExportSystem
│       ├── Cards de Seleccion
│       └── Modal de Exportacion
│
├── core/calendario.py
│   └── CalendarioInteligente
│       ├── Vista Mensual
│       ├── Marcadores de Casos
│       └── Navegacion Interactiva
│
└── ui_helpers/ (modulos auxiliares)
    ├── ocr_helpers.py
    ├── database_helpers.py
    ├── export_helpers.py
    └── chart_helpers.py
```

### 1.2 Arbol de Componentes UI

```
App (Ventana Principal)
│
├── Header Frame
│   ├── Logo HUV (ImageLabel)
│   ├── Titulo Sistema (Label bold 22pt)
│   ├── Selector de Tema (Combobox)
│   └── Perfil Usuario (Frame)
│       ├── Avatar (Label emoji 24pt)
│       ├── Nombre (Label bold 16pt)
│       └── Rol (Label italic 9pt)
│
├── Navegacion Flotante (Frame animado)
│   ├── Boton Toggle (hamburguesa)
│   └── Menu Items (Buttons)
│       ├── Procesar Datos
│       ├── Dashboard BD
│       ├── Calendario
│       ├── Automatizacion Web
│       └── Acerca de
│
├── Pantalla Bienvenida (Frame)
│   ├── Logo Central (Label 64pt)
│   ├── Mensaje Bienvenida (Label)
│   └── Instrucciones (Label)
│
└── Notebook Principal
    ├── Tab 1: Procesar Datos
    │   ├── LabelFrame: Seleccion Archivos
    │   │   ├── Entry (ruta archivos)
    │   │   └── Button (examinar)
    │   ├── LabelFrame: Opciones Procesamiento
    │   │   ├── Checkbutton (validar archivos)
    │   │   └── Checkbutton (procesamiento IA)
    │   └── Button (procesar) + Progressbar
    │
    ├── Tab 2: Dashboard BD
    │   └── EnhancedDatabaseDashboard
    │       └── Nested Notebook (6 tabs)
    │
    ├── Tab 3: Calendario
    │   └── CalendarioInteligente
    │       ├── Header Navegacion
    │       ├── Grid Dias
    │       └── Panel Detalles
    │
    ├── Tab 4: Automatizacion Web
    │   ├── LabelFrame: Credenciales
    │   ├── LabelFrame: Opciones
    │   └── Button (iniciar automatizacion)
    │
    └── Tab 5: Acerca de
        ├── Version Info
        ├── Dependencies
        └── Credits
```

---

## 2. SISTEMA DE DESIGN TOKENS

### 2.1 Tokens de Color

**IMPORTANTE**: Centralizar todos los colores en un unico archivo de configuracion.

```python
# Crear: config/design_tokens.py

"""
Sistema de Design Tokens para EVARISIS
Centraliza colores, espaciado, tipografia y animaciones
"""

from typing import Dict, Any
import ttkbootstrap as ttk

class ColorTokens:
    """Tokens de color semanticos"""

    # Colores Base (theme-agnostic)
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    TRANSPARENT = "transparent"

    # Paleta Principal (ajustable por tema)
    PRIMARY = "#2b6cb0"      # Azul institucional
    SECONDARY = "#6c757d"    # Gris medio
    SUCCESS = "#28a745"      # Verde exito
    DANGER = "#dc3545"       # Rojo error
    WARNING = "#ffc107"      # Amarillo advertencia
    INFO = "#17a2b8"         # Azul info
    LIGHT = "#f8f9fa"        # Gris muy claro
    DARK = "#343a40"         # Gris muy oscuro

    # Estados de Procesamiento
    DUPLICADO = "#ff4444"    # Rojo duplicado
    NUEVO = "#44ff44"        # Verde nuevo
    PROCESANDO = "#ffaa44"   # Naranja procesando
    ERROR_CRITICO = "#ff0000" # Rojo intenso error

    # Grises (escala neutral)
    GRAY_50 = "#f8f9fa"
    GRAY_100 = "#f1f3f5"
    GRAY_200 = "#e9ecef"
    GRAY_300 = "#dee2e6"
    GRAY_400 = "#ced4da"
    GRAY_500 = "#adb5bd"
    GRAY_600 = "#6c757d"
    GRAY_700 = "#495057"
    GRAY_800 = "#343a40"
    GRAY_900 = "#212529"

    # Colores Semanticos (texto)
    TEXT_PRIMARY = "#212529"      # Negro suave
    TEXT_SECONDARY = "#6c757d"    # Gris medio
    TEXT_MUTED = "#adb5bd"        # Gris claro
    TEXT_DISABLED = "#ced4da"     # Gris muy claro
    TEXT_INVERSE = "#FFFFFF"      # Blanco

    # Colores Semanticos (backgrounds)
    BG_PRIMARY = "#FFFFFF"        # Fondo principal
    BG_SECONDARY = "#f8f9fa"      # Fondo secundario
    BG_TERTIARY = "#e9ecef"       # Fondo terciario
    BG_SURFACE = "#FFFFFF"        # Superficie elevada
    BG_OVERLAY = "rgba(0,0,0,0.5)" # Overlay modal (no soportado en tkinter)

    # Colores de Borde
    BORDER_DEFAULT = "#dee2e6"
    BORDER_SUBTLE = "#e9ecef"
    BORDER_STRONG = "#adb5bd"
    BORDER_ACCENT = "#2b6cb0"

    # Colores de Sombra (para efectos visuales)
    SHADOW_SM = "#00000015"   # 15% opacidad
    SHADOW_MD = "#00000025"   # 25% opacidad
    SHADOW_LG = "#00000035"   # 35% opacidad

    # Colores de Graficos (Matplotlib/Seaborn)
    CHART_COLORS = [
        "#2b6cb0",  # Azul
        "#28a745",  # Verde
        "#ffc107",  # Amarillo
        "#dc3545",  # Rojo
        "#17a2b8",  # Cian
        "#6f42c1",  # Purpura
        "#fd7e14",  # Naranja
        "#20c997",  # Turquesa
    ]

    # Gradient Stops (para efectos futuros)
    GRADIENT_PRIMARY = ["#2b6cb0", "#1e4d7b"]
    GRADIENT_SUCCESS = ["#28a745", "#1e7e34"]
    GRADIENT_DANGER = ["#dc3545", "#bd2130"]

    @classmethod
    def get_bootstyle_map(cls) -> Dict[str, str]:
        """Mapa de bootstyles a colores hex"""
        return {
            "primary": cls.PRIMARY,
            "secondary": cls.SECONDARY,
            "success": cls.SUCCESS,
            "danger": cls.DANGER,
            "warning": cls.WARNING,
            "info": cls.INFO,
            "light": cls.LIGHT,
            "dark": cls.DARK,
        }


class SpacingTokens:
    """Tokens de espaciado consistente"""

    # Escala de espaciado (sistema 4px base)
    XS = 4      # Extra pequeno
    SM = 8      # Pequeno
    MD = 12     # Mediano (base)
    LG = 16     # Grande
    XL = 20     # Extra grande
    XXL = 24    # Extra extra grande
    XXXL = 32   # Triple extra grande

    # Padding semantico
    PADDING_TIGHT = XS       # 4px
    PADDING_COMPACT = SM     # 8px
    PADDING_NORMAL = MD      # 12px
    PADDING_RELAXED = LG     # 16px
    PADDING_LOOSE = XL       # 20px

    # Margin semantico
    MARGIN_TIGHT = XS        # 4px
    MARGIN_COMPACT = SM      # 8px
    MARGIN_NORMAL = MD       # 12px
    MARGIN_RELAXED = LG      # 16px
    MARGIN_LOOSE = XL        # 20px

    # Gap (para grids)
    GAP_XS = XS
    GAP_SM = SM
    GAP_MD = MD
    GAP_LG = LG
    GAP_XL = XL


class TypographyTokens:
    """Tokens de tipografia"""

    # Familia de fuente
    FONT_FAMILY = "Segoe UI"
    FONT_FAMILY_MONO = "Consolas"

    # Tamanos de fuente
    FONT_SIZE_XS = 8
    FONT_SIZE_SM = 9
    FONT_SIZE_BASE = 11
    FONT_SIZE_MD = 12
    FONT_SIZE_LG = 14
    FONT_SIZE_XL = 16
    FONT_SIZE_XXL = 18
    FONT_SIZE_XXXL = 22
    FONT_SIZE_HUGE = 24

    # Pesos de fuente
    FONT_WEIGHT_NORMAL = "normal"
    FONT_WEIGHT_BOLD = "bold"

    # Estilos de fuente
    FONT_STYLE_NORMAL = "normal"
    FONT_STYLE_ITALIC = "italic"

    # Fuentes semanticas (pre-construidas)
    @staticmethod
    def get_font(size: int = 11, weight: str = "normal", style: str = "normal", family: str = "Segoe UI"):
        """Construir tupla de fuente"""
        return (family, size, f"{weight} {style}".strip())

    # Fuentes comunes
    FONT_DISPLAY = ("Segoe UI", 24, "bold")      # Titulos muy grandes
    FONT_H1 = ("Segoe UI", 22, "bold")          # Titulos principales
    FONT_H2 = ("Segoe UI", 18, "bold")          # Subtitulos
    FONT_H3 = ("Segoe UI", 16, "bold")          # Encabezados
    FONT_H4 = ("Segoe UI", 14, "bold")          # Sub-encabezados
    FONT_BODY = ("Segoe UI", 11, "normal")      # Texto normal
    FONT_SMALL = ("Segoe UI", 9, "normal")      # Texto pequeno
    FONT_CAPTION = ("Segoe UI", 9, "italic")    # Captions/metadata
    FONT_CODE = ("Consolas", 9, "normal")       # Codigo/logs
    FONT_BUTTON = ("Segoe UI", 12, "normal")    # Botones


class AnimationTokens:
    """Tokens de animacion (tiempos en ms)"""

    DURATION_INSTANT = 0
    DURATION_FAST = 150
    DURATION_NORMAL = 300
    DURATION_SLOW = 500
    DURATION_SLOWER = 800

    EASING_LINEAR = "linear"
    EASING_EASE_IN = "ease-in"
    EASING_EASE_OUT = "ease-out"
    EASING_EASE_IN_OUT = "ease-in-out"


class ShadowTokens:
    """Tokens de sombras (simuladas en tkinter)"""

    # Relief styles (tkinter nativo)
    RELIEF_FLAT = "flat"
    RELIEF_RAISED = "raised"
    RELIEF_SUNKEN = "sunken"
    RELIEF_GROOVE = "groove"
    RELIEF_RIDGE = "ridge"
    RELIEF_SOLID = "solid"

    # Borderwidth semantico
    BORDER_NONE = 0
    BORDER_THIN = 1
    BORDER_MEDIUM = 2
    BORDER_THICK = 3

    # Efectos de elevacion (visual depth)
    ELEVATION_FLAT = {"relief": "flat", "borderwidth": 0}
    ELEVATION_1 = {"relief": "solid", "borderwidth": 1}
    ELEVATION_2 = {"relief": "raised", "borderwidth": 2}
    ELEVATION_3 = {"relief": "ridge", "borderwidth": 2}


class BorderRadiusTokens:
    """Tokens de border radius (limitado en tkinter)"""

    # Nota: tkinter no soporta border-radius nativamente
    # Estos valores son para referencia futura si se migra a CustomTkinter

    RADIUS_NONE = 0
    RADIUS_SM = 4
    RADIUS_MD = 8
    RADIUS_LG = 12
    RADIUS_XL = 16
    RADIUS_FULL = 9999  # Circulo completo


class DesignTokens:
    """Clase contenedora de todos los tokens"""

    Color = ColorTokens
    Spacing = SpacingTokens
    Typography = TypographyTokens
    Animation = AnimationTokens
    Shadow = ShadowTokens
    BorderRadius = BorderRadiusTokens

    @classmethod
    def apply_theme(cls, theme_name: str):
        """
        Aplicar tema y ajustar tokens dinamicamente

        Args:
            theme_name: Nombre del tema ttkbootstrap
        """
        # Implementar logica para ajustar colores segun tema
        # Por ahora es placeholder
        pass
```

### 2.2 Uso de Design Tokens

**ANTES (colores hardcodeados):**
```python
label = ttk.Label(parent, text="Titulo", font=("Segoe UI", 22, "bold"), foreground="#212529")
frame = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)
```

**DESPUES (usando tokens):**
```python
from config.design_tokens import DesignTokens as DT

label = ttk.Label(
    parent,
    text="Titulo",
    font=DT.Typography.FONT_H1,
    foreground=DT.Color.TEXT_PRIMARY
)

frame = ttk.Frame(
    parent,
    padding=DT.Spacing.PADDING_RELAXED,
    **DT.Shadow.ELEVATION_1
)
```

---

## 3. BIBLIOTECA DE PATRONES VISUALES

### 3.1 Patron: Metric Card (Tarjeta de Metrica)

**Uso Actual**: Dashboard, ventanas de resultados

**Anatomia**:
```
┌─────────────────────┐
│  🔥 Icono           │
│                     │
│      1,234          │ <- Valor grande (20pt bold)
│                     │
│   Total Casos       │ <- Label pequeno (9pt)
└─────────────────────┘
```

**Codigo Actual (inconsistente)**:
```python
# En ui.py y enhanced_database_dashboard.py hay MULTIPLES implementaciones
card = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)
icon = ttk.Label(card, text="🔥", font=24)
value = ttk.Label(card, text="123", font=("Segoe UI", 20, "bold"))
title = ttk.Label(card, text="Total", font=9)
```

**Codigo MEJORADO (componente reutilizable)**:
```python
# Crear: ui_components/metric_card.py

from config.design_tokens import DesignTokens as DT
import ttkbootstrap as ttk

class MetricCard(ttk.Frame):
    """
    Tarjeta de metrica estandarizada

    Uso:
        card = MetricCard(
            parent=parent,
            icon="🔥",
            value="1,234",
            label="Total Casos",
            bootstyle="info"
        )
        card.pack(side=LEFT, padx=10, pady=10)
    """

    def __init__(
        self,
        parent,
        icon: str = "",
        value: str = "0",
        label: str = "",
        bootstyle: str = "info",
        **kwargs
    ):
        # Aplicar elevation y padding
        super().__init__(
            parent,
            padding=DT.Spacing.PADDING_RELAXED,
            **DT.Shadow.ELEVATION_1,
            bootstyle=bootstyle,
            **kwargs
        )

        # Header con icono
        if icon:
            header_frame = ttk.Frame(self)
            header_frame.pack(fill='x', pady=(0, DT.Spacing.MARGIN_COMPACT))

            icon_label = ttk.Label(
                header_frame,
                text=icon,
                font=DT.Typography.FONT_HUGE,
                bootstyle=bootstyle
            )
            icon_label.pack()

        # Valor principal
        self.value_label = ttk.Label(
            self,
            text=value,
            font=("Segoe UI", 24, "bold"),  # Extra grande para metricas
            bootstyle=bootstyle
        )
        self.value_label.pack(pady=DT.Spacing.MARGIN_COMPACT)

        # Label descriptivo
        self.title_label = ttk.Label(
            self,
            text=label,
            font=DT.Typography.FONT_SMALL,
            foreground=DT.Color.TEXT_SECONDARY
        )
        self.title_label.pack()

    def update_value(self, new_value: str):
        """Actualizar valor de la metrica"""
        self.value_label.configure(text=new_value)

    def update_label(self, new_label: str):
        """Actualizar label"""
        self.title_label.configure(text=new_label)
```

### 3.2 Patron: Stat Badge (Badge Estadistico)

**Uso Actual**: ventana_resultados_importacion.py

**Anatomia**:
```
┌──────────────┐
│ 📄 Total     │ <- Label + icono
│   1,234      │ <- Valor
└──────────────┘
```

**Codigo Mejorado**:
```python
# Crear: ui_components/stat_badge.py

from config.design_tokens import DesignTokens as DT
import ttkbootstrap as ttk

class StatBadge(ttk.Frame):
    """
    Badge estadistico compacto

    Uso:
        badge = StatBadge(
            parent=parent,
            label="📄 Total",
            value="1,234",
            bootstyle="info"
        )
        badge.pack(side=LEFT, padx=5)
    """

    def __init__(
        self,
        parent,
        label: str = "",
        value: str = "0",
        bootstyle: str = "info",
        **kwargs
    ):
        super().__init__(
            parent,
            bootstyle=bootstyle,
            padding=DT.Spacing.PADDING_COMPACT,
            **kwargs
        )

        # Label
        ttk.Label(
            self,
            text=label,
            font=DT.Typography.FONT_SMALL,
            bootstyle=bootstyle
        ).pack(pady=(DT.Spacing.MARGIN_TIGHT, 0))

        # Valor
        self.value_label = ttk.Label(
            self,
            text=value,
            font=DT.Typography.FONT_H3,
            bootstyle=bootstyle
        )
        self.value_label.pack()

    def update_value(self, new_value: str):
        """Actualizar valor"""
        self.value_label.configure(text=new_value)
```

### 3.3 Patron: Scroll Container

**Uso Actual**: MULTIPLES archivos con implementaciones inconsistentes

**Problemas**:
- Algunos tienen keyboard bindings, otros no
- Scroll speed inconsistente
- Configuracion de scrollregion varia

**Codigo Mejorado**:
```python
# Crear: ui_components/scroll_container.py

import tkinter as tk
import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class ScrollContainer(ttk.Frame):
    """
    Contenedor con scroll vertical consistente

    Uso:
        container = ScrollContainer(parent)
        container.pack(fill='both', expand=True)

        # Agregar contenido al frame interno
        ttk.Label(container.content, text="Contenido").pack()
    """

    def __init__(self, parent, show_scrollbar: bool = True, **kwargs):
        super().__init__(parent, **kwargs)

        # Canvas para scroll
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar opcional
        if show_scrollbar:
            self.scrollbar = ttk.Scrollbar(
                self,
                orient="vertical",
                command=self.canvas.yview
            )
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Frame de contenido
        self.content = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        # Configurar scroll region automaticamente
        self.content.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mousewheel (CONSISTENTE)
        self._bind_mousewheel()

        # Bind keyboard (NUEVO - para accesibilidad)
        self._bind_keyboard()

    def _on_content_configure(self, event=None):
        """Actualizar scroll region cuando contenido cambia"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event=None):
        """Ajustar ancho del contenido al canvas"""
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_mousewheel(self):
        """Bind consistente de mousewheel"""
        def _on_mousewheel(event):
            try:
                # Scroll speed: 1 unidad = 1 linea
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass

        self.canvas.bind("<MouseWheel>", _on_mousewheel)
        self.content.bind("<MouseWheel>", _on_mousewheel)

        # Para Linux
        self.canvas.bind("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _bind_keyboard(self):
        """Bind de teclado para accesibilidad"""
        def _on_key(event):
            if event.keysym == "Up":
                self.canvas.yview_scroll(-1, "units")
            elif event.keysym == "Down":
                self.canvas.yview_scroll(1, "units")
            elif event.keysym == "Prior":  # Page Up
                self.canvas.yview_scroll(-1, "pages")
            elif event.keysym == "Next":   # Page Down
                self.canvas.yview_scroll(1, "pages")
            elif event.keysym == "Home":
                self.canvas.yview_moveto(0)
            elif event.keysym == "End":
                self.canvas.yview_moveto(1)

        # Foco en canvas para recibir eventos de teclado
        self.canvas.bind("<FocusIn>", lambda e: None)
        self.canvas.bind("<Key>", _on_key)

        # Hacer canvas focusable
        self.canvas.config(takefocus=1)

    def scroll_to_top(self):
        """Scroll al inicio"""
        self.canvas.yview_moveto(0)

    def scroll_to_bottom(self):
        """Scroll al final"""
        self.canvas.yview_moveto(1)
```

### 3.4 Patron: LabelFrame con Icono

**Uso Actual**: Muy comun en toda la UI

**Codigo Mejorado**:
```python
# Crear: ui_components/icon_label_frame.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class IconLabelFrame(ttk.LabelFrame):
    """
    LabelFrame con icono estandarizado

    Uso:
        frame = IconLabelFrame(
            parent=parent,
            icon="📊",
            text="Estadisticas",
            bootstyle="info"
        )
        frame.pack(fill='x', pady=10)
    """

    def __init__(
        self,
        parent,
        icon: str = "",
        text: str = "",
        bootstyle: str = "primary",
        padding: int = None,
        **kwargs
    ):
        # Construir label con icono
        label_text = f"{icon} {text}" if icon else text

        # Aplicar padding default
        if padding is None:
            padding = DT.Spacing.PADDING_RELAXED

        super().__init__(
            parent,
            text=label_text,
            padding=padding,
            bootstyle=bootstyle,
            **kwargs
        )
```

### 3.5 Patron: Grid de Cards Responsivo

**Uso Actual**: Dashboard, multiples secciones

**Codigo Mejorado**:
```python
# Crear: ui_components/card_grid.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT
from typing import List, Tuple

class CardGrid(ttk.Frame):
    """
    Grid responsivo de cards

    Uso:
        grid = CardGrid(
            parent=parent,
            columns=3,
            gap=10
        )
        grid.pack(fill='both', expand=True)

        # Agregar cards
        for i in range(6):
            card = ttk.Frame(grid.get_cell(i))
            card.pack(fill='both', expand=True)
    """

    def __init__(
        self,
        parent,
        columns: int = 3,
        gap: int = None,
        min_cell_width: int = 150,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.columns = columns
        self.gap = gap if gap is not None else DT.Spacing.GAP_MD
        self.min_cell_width = min_cell_width
        self.cells = []

        # Configurar grid
        for i in range(columns):
            self.grid_columnconfigure(i, weight=1, minsize=min_cell_width)

    def get_cell(self, index: int) -> ttk.Frame:
        """
        Obtener frame de celda en el grid

        Args:
            index: Indice de la celda (0-indexed)

        Returns:
            Frame de la celda
        """
        row = index // self.columns
        col = index % self.columns

        # Crear frame de celda
        cell = ttk.Frame(self)
        cell.grid(
            row=row,
            column=col,
            padx=self.gap,
            pady=self.gap,
            sticky="nsew"
        )

        # Configurar peso de fila
        self.grid_rowconfigure(row, weight=1)

        self.cells.append(cell)
        return cell

    def add_cards(self, card_widgets: List):
        """
        Agregar multiples cards al grid

        Args:
            card_widgets: Lista de widgets a agregar
        """
        for i, widget in enumerate(card_widgets):
            cell = self.get_cell(i)
            widget.configure(master=cell)
            widget.pack(fill='both', expand=True)
```

### 3.6 Patron: Modal Window (Ventana Modal)

**Uso Actual**: ventana_selector_auditoria.py, ventana_auditoria_ia.py

**Codigo Mejorado**:
```python
# Crear: ui_components/modal_window.py

import tkinter as tk
import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class ModalWindow(tk.Toplevel):
    """
    Ventana modal estandarizada

    Uso:
        modal = ModalWindow(
            parent=root,
            title="Titulo Modal",
            width=600,
            height=400,
            maximized=False
        )

        # Agregar contenido
        ttk.Label(modal.content, text="Contenido").pack()

        # Mostrar
        modal.show()
    """

    def __init__(
        self,
        parent,
        title: str = "",
        width: int = 600,
        height: int = 400,
        maximized: bool = False,
        resizable: bool = True,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.title(title)
        self.resizable(resizable, resizable)

        # Configurar como modal
        self.transient(parent)
        self.grab_set()

        # Frame de contenido principal
        self.content = ttk.Frame(self, padding=DT.Spacing.PADDING_NORMAL)
        self.content.pack(fill='both', expand=True)

        # Maximizar o centrar
        if maximized:
            self._maximize()
        else:
            self._center(width, height)

    def _center(self, width: int, height: int):
        """Centrar ventana en pantalla"""
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _maximize(self):
        """Maximizar ventana"""
        try:
            self.state('zoomed')  # Windows
        except:
            # Fallback para otros sistemas
            w = self.winfo_screenwidth()
            h = self.winfo_screenheight()
            self.geometry(f"{w}x{h}+0+0")

    def show(self):
        """Mostrar modal y esperar"""
        self.wait_window(self)
```

---

## 4. COMPONENTES REUTILIZABLES

### 4.1 Componente: ProgressIndicator

**Proposito**: Indicador de progreso consistente para operaciones largas

```python
# Crear: ui_components/progress_indicator.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class ProgressIndicator(ttk.Frame):
    """
    Indicador de progreso con mensaje y barra

    Uso:
        progress = ProgressIndicator(parent)
        progress.pack(fill='x', pady=10)

        # Actualizar progreso
        progress.update_progress(50, "Procesando caso 5/10...")

        # Completar
        progress.complete("Procesamiento completado")
    """

    def __init__(self, parent, bootstyle: str = "info", **kwargs):
        super().__init__(parent, **kwargs)

        self.bootstyle = bootstyle

        # Label de mensaje
        self.message_label = ttk.Label(
            self,
            text="Iniciando...",
            font=DT.Typography.FONT_BODY,
            bootstyle=bootstyle
        )
        self.message_label.pack(fill='x', pady=(0, DT.Spacing.MARGIN_COMPACT))

        # Barra de progreso
        self.progressbar = ttk.Progressbar(
            self,
            bootstyle=bootstyle,
            mode="determinate",
            maximum=100
        )
        self.progressbar.pack(fill='x')

        # Label de porcentaje
        self.percent_label = ttk.Label(
            self,
            text="0%",
            font=DT.Typography.FONT_SMALL,
            foreground=DT.Color.TEXT_SECONDARY
        )
        self.percent_label.pack(anchor='e', pady=(DT.Spacing.MARGIN_TIGHT, 0))

    def update_progress(self, value: float, message: str = None):
        """
        Actualizar progreso

        Args:
            value: Valor de progreso (0-100)
            message: Mensaje opcional
        """
        self.progressbar['value'] = value
        self.percent_label.configure(text=f"{value:.0f}%")

        if message:
            self.message_label.configure(text=message)

        self.update_idletasks()

    def complete(self, message: str = "Completado"):
        """Marcar como completado"""
        self.update_progress(100, message)
        self.progressbar.configure(bootstyle="success")
        self.message_label.configure(bootstyle="success")

    def error(self, message: str = "Error"):
        """Marcar como error"""
        self.progressbar.configure(bootstyle="danger")
        self.message_label.configure(text=message, bootstyle="danger")
```

### 4.2 Componente: StatusBanner

**Proposito**: Banner de estado para mensajes importantes

```python
# Crear: ui_components/status_banner.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class StatusBanner(ttk.Frame):
    """
    Banner de estado para mensajes importantes

    Uso:
        banner = StatusBanner(
            parent=parent,
            message="Operacion completada exitosamente",
            status="success"
        )
        banner.pack(fill='x', pady=10)

        # Cerrar banner
        banner.close()
    """

    ICONS = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }

    def __init__(
        self,
        parent,
        message: str = "",
        status: str = "info",
        closable: bool = True,
        **kwargs
    ):
        bootstyle = status
        super().__init__(
            parent,
            bootstyle=bootstyle,
            padding=DT.Spacing.PADDING_NORMAL,
            **kwargs
        )

        # Icono
        icon = self.ICONS.get(status, "ℹ️")
        ttk.Label(
            self,
            text=icon,
            font=DT.Typography.FONT_H3,
            bootstyle=bootstyle
        ).pack(side='left', padx=(0, DT.Spacing.MARGIN_COMPACT))

        # Mensaje
        ttk.Label(
            self,
            text=message,
            font=DT.Typography.FONT_BODY,
            bootstyle=bootstyle
        ).pack(side='left', fill='x', expand=True)

        # Boton cerrar
        if closable:
            close_btn = ttk.Button(
                self,
                text="✖",
                bootstyle=f"{bootstyle}-link",
                command=self.close,
                width=3
            )
            close_btn.pack(side='right')

    def close(self):
        """Cerrar banner"""
        self.pack_forget()
        self.destroy()
```

### 4.3 Componente: EmptyState

**Proposito**: Estado vacio cuando no hay datos

```python
# Crear: ui_components/empty_state.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class EmptyState(ttk.Frame):
    """
    Estado vacio cuando no hay datos

    Uso:
        empty = EmptyState(
            parent=parent,
            icon="📭",
            title="No hay casos",
            description="Importa archivos PDF para comenzar",
            action_text="Importar Archivos",
            action_callback=lambda: print("Importar")
        )
        empty.pack(fill='both', expand=True)
    """

    def __init__(
        self,
        parent,
        icon: str = "📭",
        title: str = "No hay datos",
        description: str = "",
        action_text: str = None,
        action_callback = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        # Centrar contenido
        container = ttk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor='center')

        # Icono grande
        ttk.Label(
            container,
            text=icon,
            font=("Segoe UI", 64)
        ).pack(pady=(0, DT.Spacing.MARGIN_NORMAL))

        # Titulo
        ttk.Label(
            container,
            text=title,
            font=DT.Typography.FONT_H2,
            foreground=DT.Color.TEXT_PRIMARY
        ).pack()

        # Descripcion
        if description:
            ttk.Label(
                container,
                text=description,
                font=DT.Typography.FONT_BODY,
                foreground=DT.Color.TEXT_SECONDARY
            ).pack(pady=(DT.Spacing.MARGIN_COMPACT, DT.Spacing.MARGIN_NORMAL))

        # Boton de accion
        if action_text and action_callback:
            ttk.Button(
                container,
                text=action_text,
                bootstyle="primary",
                command=action_callback
            ).pack()
```

### 4.4 Componente: LoadingSkeleton

**Proposito**: Skeleton loader mientras carga datos

```python
# Crear: ui_components/loading_skeleton.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class LoadingSkeleton(ttk.Frame):
    """
    Skeleton loader animado

    Uso:
        skeleton = LoadingSkeleton(parent, lines=3)
        skeleton.pack(fill='x', pady=10)

        # Cuando termina carga
        skeleton.destroy()
    """

    def __init__(self, parent, lines: int = 3, **kwargs):
        super().__init__(parent, **kwargs)

        self.lines = []
        self.animation_state = 0

        # Crear lineas de skeleton
        for i in range(lines):
            line = ttk.Frame(
                self,
                height=20,
                bootstyle="secondary"
            )
            line.pack(
                fill='x',
                pady=DT.Spacing.MARGIN_COMPACT,
                padx=DT.Spacing.PADDING_NORMAL
            )
            self.lines.append(line)

        # Iniciar animacion pulse
        self._animate()

    def _animate(self):
        """Animacion pulse simple"""
        # Alternar bootstyle para simular pulse
        style = "light" if self.animation_state % 2 == 0 else "secondary"

        for line in self.lines:
            line.configure(bootstyle=style)

        self.animation_state += 1

        # Repetir cada 500ms
        if self.winfo_exists():
            self.after(500, self._animate)
```

### 4.5 Componente: Tooltip

**Proposito**: Tooltip informativo al hacer hover

```python
# Crear: ui_components/tooltip.py

import tkinter as tk
import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class Tooltip:
    """
    Tooltip que aparece al hacer hover

    Uso:
        button = ttk.Button(parent, text="Ayuda")
        Tooltip(button, "Este boton muestra ayuda")
    """

    def __init__(self, widget, text: str, delay: int = 500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self.tooltip_window = None
        self.after_id = None

        # Bind eventos
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        """Mouse entra en widget"""
        self._schedule_show()

    def _on_leave(self, event=None):
        """Mouse sale de widget"""
        self._cancel_show()
        self._hide()

    def _schedule_show(self):
        """Programar mostrar tooltip"""
        self._cancel_show()
        self.after_id = self.widget.after(self.delay, self._show)

    def _cancel_show(self):
        """Cancelar mostrar tooltip"""
        if self.after_id:
            self.widget.after_cancel(self.after_id)
            self.after_id = None

    def _show(self):
        """Mostrar tooltip"""
        if self.tooltip_window:
            return

        # Calcular posicion
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # Crear ventana tooltip
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Frame con borde
        frame = ttk.Frame(
            self.tooltip_window,
            bootstyle="dark",
            padding=DT.Spacing.PADDING_COMPACT,
            **DT.Shadow.ELEVATION_2
        )
        frame.pack()

        # Label con texto
        label = ttk.Label(
            frame,
            text=self.text,
            font=DT.Typography.FONT_SMALL,
            bootstyle="dark",
            foreground=DT.Color.TEXT_INVERSE
        )
        label.pack()

    def _hide(self):
        """Ocultar tooltip"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
```

### 4.6 Componente: SearchBar

**Proposito**: Barra de busqueda con icono

```python
# Crear: ui_components/search_bar.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class SearchBar(ttk.Frame):
    """
    Barra de busqueda con icono y boton limpiar

    Uso:
        search = SearchBar(
            parent=parent,
            placeholder="Buscar casos...",
            callback=lambda query: print(f"Buscando: {query}")
        )
        search.pack(fill='x', pady=10)
    """

    def __init__(
        self,
        parent,
        placeholder: str = "Buscar...",
        callback = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        self.callback = callback
        self.placeholder = placeholder

        # Icono de busqueda
        ttk.Label(
            self,
            text="🔍",
            font=DT.Typography.FONT_H4
        ).pack(side='left', padx=(DT.Spacing.PADDING_COMPACT, 0))

        # Entry de busqueda
        self.entry = ttk.Entry(
            self,
            font=DT.Typography.FONT_BODY
        )
        self.entry.pack(
            side='left',
            fill='x',
            expand=True,
            padx=DT.Spacing.PADDING_COMPACT
        )

        # Placeholder
        self._show_placeholder()
        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

        # Bind Enter
        self.entry.bind("<Return>", self._on_search)

        # Boton limpiar
        self.clear_btn = ttk.Button(
            self,
            text="✖",
            bootstyle="secondary-link",
            command=self._clear,
            width=3
        )
        self.clear_btn.pack(side='right')
        self.clear_btn.pack_forget()  # Ocultar inicialmente

        # Bind cambio de texto
        self.entry.bind("<KeyRelease>", self._on_text_change)

    def _show_placeholder(self):
        """Mostrar placeholder"""
        self.entry.delete(0, 'end')
        self.entry.insert(0, self.placeholder)
        self.entry.configure(foreground=DT.Color.TEXT_MUTED)

    def _on_focus_in(self, event=None):
        """Focus en entry"""
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, 'end')
            self.entry.configure(foreground=DT.Color.TEXT_PRIMARY)

    def _on_focus_out(self, event=None):
        """Focus fuera de entry"""
        if not self.entry.get():
            self._show_placeholder()

    def _on_text_change(self, event=None):
        """Texto cambio"""
        text = self.entry.get()

        # Mostrar/ocultar boton limpiar
        if text and text != self.placeholder:
            self.clear_btn.pack(side='right')
        else:
            self.clear_btn.pack_forget()

    def _on_search(self, event=None):
        """Usuario presiono Enter"""
        query = self.entry.get()

        if query and query != self.placeholder and self.callback:
            self.callback(query)

    def _clear(self):
        """Limpiar busqueda"""
        self.entry.delete(0, 'end')
        self.clear_btn.pack_forget()

        if self.callback:
            self.callback("")

    def get_query(self) -> str:
        """Obtener query actual"""
        query = self.entry.get()
        return "" if query == self.placeholder else query
```

### 4.7 Componente: DataTable

**Proposito**: Wrapper para tksheet con estilos consistentes

```python
# Crear: ui_components/data_table.py

import ttkbootstrap as ttk
from tksheet import Sheet
from config.design_tokens import DesignTokens as DT
from typing import List, Dict

class DataTable(ttk.Frame):
    """
    Tabla de datos estandarizada usando tksheet

    Uso:
        table = DataTable(
            parent=parent,
            headers=["Nombre", "Edad", "Ciudad"],
            data=[
                ["Juan", 30, "Cali"],
                ["Maria", 25, "Bogota"]
            ]
        )
        table.pack(fill='both', expand=True)
    """

    def __init__(
        self,
        parent,
        headers: List[str] = None,
        data: List[List] = None,
        height: int = 300,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        # Crear sheet
        self.sheet = Sheet(
            self,
            headers=headers,
            data=data,
            height=height,
            font=DT.Typography.FONT_BODY,
            header_font=DT.Typography.FONT_SMALL + ("bold",),
            theme="light blue"
        )

        # Habilitar funcionalidades
        self.sheet.enable_bindings(
            "single_select",
            "row_select",
            "column_width_resize",
            "arrowkeys",
            "right_click_popup_menu",
            "rc_select",
            "copy"
        )

        self.sheet.pack(fill='both', expand=True)

    def update_data(self, data: List[List]):
        """Actualizar datos de la tabla"""
        self.sheet.set_sheet_data(data)

    def get_selected_row(self) -> List:
        """Obtener fila seleccionada"""
        selected = self.sheet.get_currently_selected()
        if selected:
            row_idx = selected[0]
            return self.sheet.get_row_data(row_idx)
        return None

    def clear(self):
        """Limpiar tabla"""
        self.sheet.set_sheet_data([])
```

### 4.8 Componente: Tabs (Pestanas Mejoradas)

**Proposito**: Sistema de pestanas con iconos

```python
# Crear: ui_components/tabs.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT
from typing import List, Tuple

class IconTabs(ttk.Notebook):
    """
    Notebook con pestanas con iconos

    Uso:
        tabs = IconTabs(parent)
        tabs.pack(fill='both', expand=True)

        tab1 = ttk.Frame(tabs)
        tabs.add_tab(tab1, icon="📊", text="Dashboard")

        tab2 = ttk.Frame(tabs)
        tabs.add_tab(tab2, icon="📅", text="Calendario")
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.tabs = []

    def add_tab(self, frame, icon: str = "", text: str = ""):
        """
        Agregar pestana con icono

        Args:
            frame: Frame de contenido
            icon: Emoji/icono
            text: Texto de la pestana
        """
        label = f"{icon} {text}" if icon else text
        self.add(frame, text=label)
        self.tabs.append((frame, icon, text))
```

### 4.9 Componente: ButtonGroup

**Proposito**: Grupo de botones relacionados

```python
# Crear: ui_components/button_group.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT
from typing import List, Tuple, Callable

class ButtonGroup(ttk.Frame):
    """
    Grupo de botones relacionados

    Uso:
        buttons = ButtonGroup(
            parent=parent,
            buttons=[
                ("Guardar", "success", callback_guardar),
                ("Cancelar", "secondary", callback_cancelar)
            ],
            orientation="horizontal"
        )
        buttons.pack(pady=10)
    """

    def __init__(
        self,
        parent,
        buttons: List[Tuple[str, str, Callable]] = None,
        orientation: str = "horizontal",
        gap: int = None,
        **kwargs
    ):
        super().__init__(parent, **kwargs)

        if gap is None:
            gap = DT.Spacing.GAP_SM

        self.orientation = orientation
        self.gap = gap
        self.buttons = []

        if buttons:
            for text, bootstyle, callback in buttons:
                self.add_button(text, bootstyle, callback)

    def add_button(self, text: str, bootstyle: str = "primary", callback: Callable = None):
        """Agregar boton al grupo"""
        btn = ttk.Button(
            self,
            text=text,
            bootstyle=bootstyle,
            command=callback
        )

        if self.orientation == "horizontal":
            btn.pack(side='left', padx=(0, self.gap))
        else:
            btn.pack(fill='x', pady=(0, self.gap))

        self.buttons.append(btn)
        return btn
```

### 4.10 Componente: Divider

**Proposito**: Separador visual

```python
# Crear: ui_components/divider.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class Divider(ttk.Separator):
    """
    Separador visual mejorado

    Uso:
        Divider(parent, orientation="horizontal").pack(fill='x', pady=10)
    """

    def __init__(self, parent, orientation: str = "horizontal", **kwargs):
        super().__init__(
            parent,
            orient=orientation,
            bootstyle="secondary",
            **kwargs
        )
```

---

## 5. GUIAS DE MEJORA ESPECIFICAS

### 5.1 Como Mejorar Contraste

**Problema**: Texto dificil de leer sobre fondos claros/oscuros

**Solucion**: Usar colores semanticos de texto

```python
from config.design_tokens import DesignTokens as DT

# ANTES (mal contraste)
label = ttk.Label(parent, text="Texto", foreground="#999999")  # Gris muy claro

# DESPUES (buen contraste)
label = ttk.Label(
    parent,
    text="Texto",
    foreground=DT.Color.TEXT_PRIMARY  # Negro suave con buen contraste
)

# Para texto secundario
label_secondary = ttk.Label(
    parent,
    text="Metadata",
    foreground=DT.Color.TEXT_SECONDARY  # Gris medio, aun legible
)
```

**Regla WCAG AA**: Contraste minimo 4.5:1 para texto normal, 3:1 para texto grande

**Herramienta de verificacion**:
```python
def verificar_contraste(color_texto: str, color_fondo: str) -> float:
    """
    Calcular ratio de contraste entre dos colores

    Returns:
        Ratio de contraste (ej: 4.5)
    """
    # Implementar calculo segun formula WCAG
    # https://www.w3.org/TR/WCAG20-TECHS/G17.html
    pass
```

### 5.2 Como Agregar Sombras (Depth Visual)

**Problema**: UI plana sin jerarquia visual

**Solucion**: Usar elevation tokens

```python
from config.design_tokens import DesignTokens as DT

# Nivel 0: Plano (sin sombra)
frame_flat = ttk.Frame(parent, **DT.Shadow.ELEVATION_FLAT)

# Nivel 1: Sombra sutil (cards normales)
card = ttk.Frame(parent, **DT.Shadow.ELEVATION_1)

# Nivel 2: Sombra media (modals, dropdowns)
modal = ttk.Frame(parent, **DT.Shadow.ELEVATION_2)

# Nivel 3: Sombra fuerte (elementos flotantes)
floating_menu = ttk.Frame(parent, **DT.Shadow.ELEVATION_3)
```

**Nota**: tkinter tiene soporte limitado de sombras reales. Los niveles usan combinaciones de `relief` y `borderwidth` para simular depth.

**Para sombras reales**: Considerar migrar a CustomTkinter que soporta sombras CSS-like.

### 5.3 Como Hacer Animaciones

**Problema**: Transiciones abruptas sin feedback visual

**Solucion**: Usar animaciones suaves

#### 5.3.1 Animacion FadeIn

```python
# Crear: ui_components/animations.py

import ttkbootstrap as ttk
from config.design_tokens import DesignTokens as DT

class FadeInAnimation:
    """
    Animacion de fade-in para widgets

    Uso:
        widget = ttk.Label(parent, text="Hola")
        widget.pack()
        FadeInAnimation(widget, duration=300)
    """

    def __init__(self, widget, duration: int = 300, steps: int = 10):
        self.widget = widget
        self.duration = duration
        self.steps = steps
        self.step_delay = duration // steps
        self.current_step = 0

        # Guardar configuracion original
        try:
            self.original_fg = widget.cget("foreground")
        except:
            self.original_fg = DT.Color.TEXT_PRIMARY

        # Iniciar con transparencia (simulada con gris claro)
        self.widget.configure(foreground=DT.Color.GRAY_100)

        # Iniciar animacion
        self._animate()

    def _animate(self):
        """Step de animacion"""
        if self.current_step >= self.steps:
            # Completar - restaurar color original
            self.widget.configure(foreground=self.original_fg)
            return

        # Calcular opacidad (simulada con escala de grises)
        # Nota: tkinter no soporta alpha channel, esto es una aproximacion
        progress = self.current_step / self.steps

        # Aproximar fade con escala de grises
        gray_scale = [
            DT.Color.GRAY_100,
            DT.Color.GRAY_200,
            DT.Color.GRAY_300,
            DT.Color.GRAY_400,
            DT.Color.GRAY_500,
            DT.Color.GRAY_600,
            DT.Color.GRAY_700,
            DT.Color.GRAY_800,
            DT.Color.GRAY_900,
            self.original_fg
        ]

        color_idx = int(progress * (len(gray_scale) - 1))
        self.widget.configure(foreground=gray_scale[color_idx])

        self.current_step += 1

        if self.widget.winfo_exists():
            self.widget.after(self.step_delay, self._animate)
```

#### 5.3.2 Animacion SlideIn

```python
class SlideInAnimation:
    """
    Animacion de slide-in para frames

    Uso:
        frame = ttk.Frame(parent)
        SlideInAnimation(frame, direction="left", duration=300)
    """

    def __init__(
        self,
        widget,
        direction: str = "left",  # left, right, top, bottom
        duration: int = 300,
        steps: int = 20
    ):
        self.widget = widget
        self.direction = direction
        self.duration = duration
        self.steps = steps
        self.step_delay = duration // steps
        self.current_step = 0

        # Obtener dimensiones
        widget.update_idletasks()
        self.width = widget.winfo_reqwidth()
        self.height = widget.winfo_reqheight()

        # Calcular posicion inicial y final
        self._calculate_positions()

        # Posicionar widget fuera de vista
        widget.place(x=self.start_x, y=self.start_y)

        # Iniciar animacion
        self._animate()

    def _calculate_positions(self):
        """Calcular posiciones inicial y final"""
        # Posicion final (visible)
        self.end_x = 0
        self.end_y = 0

        # Posicion inicial (fuera de vista)
        if self.direction == "left":
            self.start_x = -self.width
            self.start_y = 0
        elif self.direction == "right":
            self.start_x = self.widget.master.winfo_width()
            self.start_y = 0
        elif self.direction == "top":
            self.start_x = 0
            self.start_y = -self.height
        elif self.direction == "bottom":
            self.start_x = 0
            self.start_y = self.widget.master.winfo_height()

    def _animate(self):
        """Step de animacion"""
        if self.current_step >= self.steps:
            # Completar
            self.widget.place(x=self.end_x, y=self.end_y)
            return

        # Calcular progreso (easing ease-out)
        progress = self.current_step / self.steps
        eased_progress = 1 - (1 - progress) ** 2  # Ease-out quad

        # Interpolar posicion
        current_x = self.start_x + (self.end_x - self.start_x) * eased_progress
        current_y = self.start_y + (self.end_y - self.start_y) * eased_progress

        self.widget.place(x=int(current_x), y=int(current_y))

        self.current_step += 1

        if self.widget.winfo_exists():
            self.widget.after(self.step_delay, self._animate)
```

#### 5.3.3 Animacion Pulse

```python
class PulseAnimation:
    """
    Animacion de pulse para llamar atencion

    Uso:
        button = ttk.Button(parent, text="Importante")
        PulseAnimation(button, cycles=3)
    """

    def __init__(self, widget, cycles: int = 3, duration: int = 500):
        self.widget = widget
        self.cycles = cycles
        self.duration = duration
        self.current_cycle = 0

        # Guardar relief original
        try:
            self.original_relief = widget.cget("relief")
        except:
            self.original_relief = "flat"

        self._pulse()

    def _pulse(self):
        """Ejecutar un ciclo de pulse"""
        if self.current_cycle >= self.cycles:
            # Restaurar estado original
            try:
                self.widget.configure(relief=self.original_relief)
            except:
                pass
            return

        # Pulse: raised -> sunken -> raised
        self.widget.configure(relief="raised")

        if self.widget.winfo_exists():
            self.widget.after(self.duration // 2, self._pulse_down)

    def _pulse_down(self):
        """Fase down del pulse"""
        try:
            self.widget.configure(relief="sunken")
        except:
            pass

        self.current_cycle += 1

        if self.widget.winfo_exists():
            self.widget.after(self.duration // 2, self._pulse)
```

### 5.4 Como Mejorar Spacing

**Problema**: Espaciado inconsistente, elementos muy juntos/separados

**Solucion**: Usar spacing tokens consistentes

```python
from config.design_tokens import DesignTokens as DT

# ANTES (espaciado arbitrario)
frame1 = ttk.Frame(parent, padding=15)
frame2 = ttk.Frame(parent, padding=10)
label.pack(pady=7)

# DESPUES (espaciado consistente)
frame1 = ttk.Frame(parent, padding=DT.Spacing.PADDING_RELAXED)  # 16px
frame2 = ttk.Frame(parent, padding=DT.Spacing.PADDING_NORMAL)   # 12px
label.pack(pady=DT.Spacing.MARGIN_COMPACT)  # 8px
```

**Sistema de espaciado de 4px**:
- XS (4px): Muy apretado
- SM (8px): Compacto
- MD (12px): Normal (base)
- LG (16px): Relajado
- XL (20px): Espacioso
- XXL (24px): Muy espacioso
- XXXL (32px): Extra espacioso

**Guia de uso**:
- Padding interno de cards: RELAXED (16px)
- Margin entre secciones: NORMAL (12px)
- Gap en grids: SM (8px) o MD (12px)
- Padding de modals: NORMAL (12px)

### 5.5 Como Unificar Colores

**Problema**: Colores hardcodeados inconsistentes

**Solucion**: Centralizar en ColorTokens

**Paso 1**: Auditar colores actuales
```python
# Buscar en codigo:
# foreground="#...", background="#...", fg="#...", bg="#..."
```

**Paso 2**: Mapear a tokens
```python
# ANTES
label = ttk.Label(parent, text="Error", foreground="#ff0000")

# DESPUES
from config.design_tokens import DesignTokens as DT
label = ttk.Label(parent, text="Error", foreground=DT.Color.DANGER)
```

**Paso 3**: Usar bootstyles cuando sea posible
```python
# Preferir bootstyles sobre colores directos
label = ttk.Label(parent, text="Error", bootstyle="danger")
```

### 5.6 Como Mejorar Accesibilidad

#### 5.6.1 Navegacion por Teclado

**Problema**: Solo se puede navegar con mouse

**Solucion**: Implementar keyboard bindings

```python
# Ejemplo: Navegacion en tabla
def setup_keyboard_navigation(widget):
    """Configurar navegacion por teclado"""

    widget.bind("<Up>", lambda e: scroll_up())
    widget.bind("<Down>", lambda e: scroll_down())
    widget.bind("<Left>", lambda e: scroll_left())
    widget.bind("<Right>", lambda e: scroll_right())
    widget.bind("<Home>", lambda e: scroll_to_start())
    widget.bind("<End>", lambda e: scroll_to_end())
    widget.bind("<Prior>", lambda e: page_up())  # Page Up
    widget.bind("<Next>", lambda e: page_down())  # Page Down
    widget.bind("<Return>", lambda e: activate_selected())
    widget.bind("<Escape>", lambda e: cancel())

    # Hacer widget focusable
    widget.config(takefocus=1)
```

#### 5.6.2 Indicadores de Foco

**Problema**: No se ve que elemento tiene foco

**Solucion**: Highlight visual al enfocar

```python
def add_focus_indicator(widget):
    """Agregar indicador visual de foco"""

    original_relief = widget.cget("relief")

    def on_focus_in(event):
        widget.configure(relief="solid", borderwidth=2)

    def on_focus_out(event):
        widget.configure(relief=original_relief, borderwidth=1)

    widget.bind("<FocusIn>", on_focus_in)
    widget.bind("<FocusOut>", on_focus_out)
```

#### 5.6.3 Labels Descriptivos

**Problema**: Campos sin labels claros

**Solucion**: Siempre incluir labels descriptivos

```python
# ANTES
entry = ttk.Entry(parent)
entry.pack()

# DESPUES
label_frame = ttk.Frame(parent)
label_frame.pack(fill='x', pady=DT.Spacing.MARGIN_COMPACT)

ttk.Label(label_frame, text="Numero de Peticion:", font=DT.Typography.FONT_BODY).pack(anchor='w')
entry = ttk.Entry(label_frame)
entry.pack(fill='x')
```

---

## 6. EJEMPLOS ANTES/DESPUES

### 6.1 Ejemplo: Metric Card

**ANTES (inconsistente, sin elevation)**:
```python
# En ui.py linea ~2345
card = ttk.Frame(parent, padding=15, relief="solid", borderwidth=1)
card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

icon = ttk.Label(card, text="🔥", font=("Segoe UI", 24))
icon.pack()

value = ttk.Label(card, text="1234", font=("Segoe UI", 20, "bold"))
value.pack()

title = ttk.Label(card, text="Total Casos", font=("Segoe UI", 9))
title.pack()
```

**DESPUES (componente reutilizable, tokens, elevation)**:
```python
from ui_components.metric_card import MetricCard
from config.design_tokens import DesignTokens as DT

card = MetricCard(
    parent=parent,
    icon="🔥",
    value="1,234",
    label="Total Casos",
    bootstyle="info"
)
card.grid(
    row=0,
    column=0,
    padx=DT.Spacing.GAP_MD,
    pady=DT.Spacing.GAP_MD,
    sticky="nsew"
)
```

**Mejoras**:
- Codigo reducido de 11 lineas a 5
- Espaciado consistente usando tokens
- Elevation visual con shadow
- Componente reutilizable
- Facil de mantener

### 6.2 Ejemplo: Scroll Container

**ANTES (implementacion manual, sin keyboard)**:
```python
# En ventana_selector_auditoria.py linea 64-92
canvas = tk.Canvas(canvas_frame, highlightthickness=0)
scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
opciones_frame = ttkb.Frame(canvas)

opciones_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=opciones_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

def _on_mousewheel(event):
    try:
        if canvas.winfo_exists():
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    except tk.TclError:
        pass

canvas.bind("<MouseWheel>", _on_mousewheel)
opciones_frame.bind("<MouseWheel>", _on_mousewheel)

canvas.pack(side=tk.LEFT, fill=BOTH, expand=YES)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ... agregar contenido a opciones_frame
```

**DESPUES (componente, keyboard, consistente)**:
```python
from ui_components.scroll_container import ScrollContainer

container = ScrollContainer(parent=canvas_frame)
container.pack(fill='both', expand=True)

# Agregar contenido al frame interno
parcial_frame = ttk.LabelFrame(container.content, text="📋 Auditoria Parcial")
parcial_frame.pack(fill='x', pady=10)
```

**Mejoras**:
- Codigo reducido de ~30 lineas a 6
- Keyboard navigation incluida
- Mousewheel consistente
- Soporte Linux/Mac
- Auto-resize del contenido

### 6.3 Ejemplo: Status Banner

**ANTES (no existe)**:
```python
# Actualmente no hay sistema de banners de estado
# Los mensajes se muestran en messageboxes o logs
```

**DESPUES (componente nuevo)**:
```python
from ui_components.status_banner import StatusBanner

# Mostrar exito
banner = StatusBanner(
    parent=parent,
    message="Procesamiento completado: 25 casos importados exitosamente",
    status="success",
    closable=True
)
banner.pack(fill='x', pady=DT.Spacing.MARGIN_NORMAL)

# Auto-cerrar despues de 5 segundos
banner.after(5000, banner.close)
```

**Mejoras**:
- Feedback visual no-intrusivo
- Usuario puede cerrar manualmente
- Colores semanticos (success, error, warning, info)
- Consistente con el resto de la UI

### 6.4 Ejemplo: Empty State

**ANTES (espacio en blanco confuso)**:
```python
# Cuando no hay datos, se muestra frame vacio o mensaje simple
if not casos:
    ttk.Label(parent, text="No hay casos").pack()
```

**DESPUES (empty state informativo)**:
```python
from ui_components.empty_state import EmptyState

if not casos:
    empty = EmptyState(
        parent=parent,
        icon="📭",
        title="No hay casos para mostrar",
        description="Importa archivos PDF desde la pestana 'Procesar Datos'",
        action_text="Ir a Procesamiento",
        action_callback=lambda: notebook.select(0)  # Cambiar a tab 0
    )
    empty.pack(fill='both', expand=True)
```

**Mejoras**:
- Guia al usuario sobre que hacer
- Accion directa para resolver el problema
- Visualmente atractivo
- Reduce confusion

### 6.5 Ejemplo: Modal Window

**ANTES (codigo repetido en multiples archivos)**:
```python
# En ventana_selector_auditoria.py
def __init__(self, parent, callback_seleccion):
    super().__init__(parent)

    self.title("EVARISIS - Seleccionar Tipo de Auditoria")
    self.geometry("950x850")
    self.resizable(False, False)

    self.transient(self.master)
    self.grab_set()

    self.update_idletasks()
    x = (self.winfo_screenwidth() // 2) - (650 // 2)
    y = (self.winfo_screenheight() // 2) - (550 // 2)
    self.geometry(f"650x550+{x}+{y}")

    # ... crear UI
```

**DESPUES (componente base reutilizable)**:
```python
from ui_components.modal_window import ModalWindow

class VentanaSelectorAuditoria(ModalWindow):
    def __init__(self, parent, callback_seleccion):
        super().__init__(
            parent=parent,
            title="EVARISIS - Seleccionar Tipo de Auditoria",
            width=650,
            height=550,
            maximized=False
        )

        self.callback_seleccion = callback_seleccion
        self._crear_ui()

    def _crear_ui(self):
        # Agregar contenido a self.content
        # ...
```

**Mejoras**:
- Configuracion modal centralizada
- Centrado automatico
- Soporte para maximizar
- Menos codigo duplicado

### 6.6 Ejemplo: Progress Indicator

**ANTES (implementacion basica)**:
```python
# En ui.py
self.progress_bar = ttk.Progressbar(parent, mode="determinate", maximum=100)
self.progress_bar.pack(fill='x')

# Actualizar progreso
self.progress_bar['value'] = 50
```

**DESPUES (componente completo con mensaje)**:
```python
from ui_components.progress_indicator import ProgressIndicator

progress = ProgressIndicator(parent, bootstyle="info")
progress.pack(fill='x', pady=DT.Spacing.MARGIN_NORMAL)

# Actualizar progreso con mensaje
for i in range(total_casos):
    progress.update_progress(
        (i + 1) / total_casos * 100,
        f"Procesando caso {i + 1} de {total_casos}..."
    )
    # ... procesar caso

# Completar
progress.complete("Procesamiento finalizado exitosamente")
```

**Mejoras**:
- Mensaje descriptivo incluido
- Porcentaje visible
- Estado visual (info -> success)
- Feedback claro al usuario

---

## 7. CHECKLIST DE REVISION UI

Usar esta checklist al crear/modificar UI para mantener consistencia.

### 7.1 Checklist General

- [ ] Se usan design tokens para colores (NO colores hardcodeados)
- [ ] Se usan design tokens para espaciado (NO padding/margin arbitrarios)
- [ ] Se usan design tokens para tipografia (NO fuentes hardcodeadas)
- [ ] Los componentes son reutilizables (NO codigo duplicado)
- [ ] El codigo UI esta modularizado (NO todo en ui.py)
- [ ] Se usan bootstyles cuando es posible
- [ ] La UI es responsive (se adapta a resoluciones)

### 7.2 Checklist de Accesibilidad

- [ ] Todos los campos tienen labels descriptivos
- [ ] Hay navegacion por teclado completa
- [ ] Los elementos focusables tienen indicador visual de foco
- [ ] El contraste de texto cumple WCAG AA (4.5:1)
- [ ] Los iconos tienen texto alternativo/tooltip
- [ ] Los errores se muestran claramente
- [ ] Los estados (loading, success, error) son visibles

### 7.3 Checklist de Componentes

- [ ] Se usa MetricCard para metricas
- [ ] Se usa StatBadge para badges estadisticos
- [ ] Se usa ScrollContainer para areas con scroll
- [ ] Se usa IconLabelFrame para secciones
- [ ] Se usa CardGrid para grids de cards
- [ ] Se usa ModalWindow para ventanas modales
- [ ] Se usa ProgressIndicator para operaciones largas
- [ ] Se usa StatusBanner para mensajes de estado
- [ ] Se usa EmptyState cuando no hay datos
- [ ] Se usa Tooltip para ayuda contextual

### 7.4 Checklist de Colores

- [ ] Colores primarios usan ColorTokens.PRIMARY
- [ ] Errores usan ColorTokens.DANGER
- [ ] Exitos usan ColorTokens.SUCCESS
- [ ] Advertencias usan ColorTokens.WARNING
- [ ] Info usan ColorTokens.INFO
- [ ] Texto usa ColorTokens.TEXT_PRIMARY/SECONDARY/MUTED
- [ ] Fondos usan ColorTokens.BG_PRIMARY/SECONDARY
- [ ] Bordes usan ColorTokens.BORDER_DEFAULT/SUBTLE/STRONG

### 7.5 Checklist de Espaciado

- [ ] Padding de cards usa PADDING_RELAXED (16px)
- [ ] Margin entre elementos usa MARGIN_NORMAL (12px)
- [ ] Gap en grids usa GAP_MD (12px)
- [ ] Padding de modals usa PADDING_NORMAL (12px)
- [ ] NO se usan valores arbitrarios como 13px, 17px, etc.

### 7.6 Checklist de Tipografia

- [ ] Titulos principales usan FONT_H1
- [ ] Subtitulos usan FONT_H2
- [ ] Texto normal usa FONT_BODY
- [ ] Texto pequeno usa FONT_SMALL
- [ ] Metadata usa FONT_CAPTION
- [ ] Codigo/logs usan FONT_CODE
- [ ] NO se crean tuplas de fuente manualmente

### 7.7 Checklist de Animaciones

- [ ] Transiciones importantes tienen animacion
- [ ] Duracion de animacion es apropiada (300ms normal)
- [ ] Animaciones no bloquean la UI
- [ ] Se puede desactivar animaciones (accesibilidad)

### 7.8 Checklist de Testing

- [ ] UI se ve bien en 1920x1080
- [ ] UI se ve bien en 1366x768
- [ ] UI funciona con todos los temas de ttkbootstrap
- [ ] Scroll funciona con mouse y teclado
- [ ] Navegacion por teclado completa
- [ ] NO hay elementos cortados o superpuestos
- [ ] Los textos largos no rompen el layout

---

## 8. PLAN DE MIGRACION

### 8.1 Fase 1: Crear Infraestructura (Semana 1)

**Objetivo**: Establecer base para mejoras

**Tareas**:
1. Crear `config/design_tokens.py` con todos los tokens
2. Crear carpeta `ui_components/`
3. Implementar 10 componentes basicos:
   - MetricCard
   - StatBadge
   - ScrollContainer
   - IconLabelFrame
   - CardGrid
   - ModalWindow
   - ProgressIndicator
   - StatusBanner
   - EmptyState
   - Tooltip

**NO modificar archivos existentes todavia**

### 8.2 Fase 2: Refactorizar ui.py (Semana 2-3)

**Objetivo**: Modularizar el archivo gigante (270KB)

**Tareas**:
1. Extraer seccion "Procesar Datos" a `ui_tabs/procesar_datos.py`
2. Extraer seccion "Dashboard BD" a `ui_tabs/dashboard_bd.py`
3. Extraer seccion "Calendario" a `ui_tabs/calendario_tab.py`
4. Extraer seccion "Automatizacion Web" a `ui_tabs/automatizacion_web.py`
5. Extraer seccion "Acerca de" a `ui_tabs/acerca_de.py`
6. Dejar en ui.py SOLO:
   - Clase App
   - Header
   - Navegacion flotante
   - Pantalla bienvenida
   - Notebook principal (que carga los tabs)

**Estructura final**:
```
ui.py (reducido a ~100 lineas)
ui_tabs/
  ├── procesar_datos.py
  ├── dashboard_bd.py
  ├── calendario_tab.py
  ├── automatizacion_web.py
  └── acerca_de.py
```

### 8.3 Fase 3: Aplicar Componentes (Semana 4-5)

**Objetivo**: Reemplazar implementaciones manuales por componentes

**Tareas**:
1. Buscar todos los usos de metric cards → reemplazar por MetricCard
2. Buscar todos los scroll containers → reemplazar por ScrollContainer
3. Buscar todos los modals → heredar de ModalWindow
4. Buscar todos los progressbars → reemplazar por ProgressIndicator
5. Agregar StatusBanner donde se usan messageboxes
6. Agregar EmptyState donde hay espacios vacios

### 8.4 Fase 4: Aplicar Design Tokens (Semana 6)

**Objetivo**: Eliminar colores/espaciado hardcodeados

**Tareas**:
1. Buscar todos `foreground="#..."` → reemplazar por ColorTokens
2. Buscar todos `padding=15` → reemplazar por SpacingTokens
3. Buscar todos `font=("Segoe UI", ...)` → reemplazar por TypographyTokens
4. Verificar contraste de todos los textos

### 8.5 Fase 5: Mejorar Accesibilidad (Semana 7)

**Objetivo**: UI 100% navegable por teclado

**Tareas**:
1. Agregar keyboard bindings a todos los ScrollContainers
2. Agregar focus indicators a todos los elementos focusables
3. Agregar tooltips a botones sin texto
4. Verificar que todos los campos tienen labels
5. Testing completo con solo teclado (sin mouse)

### 8.6 Fase 6: Pulir Detalles (Semana 8)

**Objetivo**: Detalles finales de calidad

**Tareas**:
1. Agregar animaciones FadeIn a secciones importantes
2. Agregar animaciones SlideIn a modales
3. Revisar spacing de TODA la UI
4. Asegurar consistencia de fuentes
5. Testing con todos los temas de ttkbootstrap
6. Generar screenshots antes/despues

---

## 9. METRICAS DE EXITO

### 9.1 Metricas de Codigo

**Objetivo**: Codigo mas mantenible

- [ ] ui.py reducido de 270KB a <50KB
- [ ] 0 colores hardcodeados (100% tokens)
- [ ] 0 fuentes hardcodeadas (100% tokens)
- [ ] 0 espaciado arbitrario (100% tokens)
- [ ] 10+ componentes reutilizables creados
- [ ] Duplicacion de codigo <5%

### 9.2 Metricas de UX

**Objetivo**: Mejor experiencia de usuario

- [ ] 100% navegable por teclado
- [ ] Contraste WCAG AA en 100% de textos
- [ ] Feedback visual en todas las acciones
- [ ] Tiempo de carga percibido <2s
- [ ] 0 elementos cortados/superpuestos
- [ ] Funciona en resoluciones 1366x768+

### 9.3 Metricas de Mantenibilidad

**Objetivo**: Facil de mantener/extender

- [ ] Nuevos componentes en <50 lineas
- [ ] Cambio de tema en 1 linea
- [ ] Agregar nueva tab en <100 lineas
- [ ] Documentacion completa de componentes
- [ ] Ejemplos de uso de todos los componentes

---

## 10. REFERENCIAS

### 10.1 Documentacion Oficial

- **TTKBootstrap**: https://ttkbootstrap.readthedocs.io/
- **Tkinter**: https://docs.python.org/3/library/tkinter.html
- **tksheet**: https://github.com/ragardner/tksheet
- **WCAG 2.1**: https://www.w3.org/WAI/WCAG21/quickref/

### 10.2 Guias de Diseno

- **Material Design**: https://material.io/design
- **Apple Human Interface Guidelines**: https://developer.apple.com/design/
- **Microsoft Fluent Design**: https://www.microsoft.com/design/fluent/

### 10.3 Herramientas

- **Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Color Palette Generator**: https://coolors.co/
- **Icon Library**: https://emojipedia.org/

---

## CONCLUSION

Esta guia proporciona un sistema completo para mejorar la UI de EVARISIS de forma consistente y mantenible. Los proximos pasos son:

1. **Crear infraestructura**: Design tokens + componentes basicos
2. **Refactorizar ui.py**: Modularizar el archivo gigante
3. **Aplicar componentes**: Reemplazar implementaciones manuales
4. **Aplicar tokens**: Eliminar hardcoding
5. **Mejorar accesibilidad**: Navegacion por teclado completa
6. **Pulir detalles**: Animaciones y ajustes finos

Con esta guia, el core-editor puede aplicar mejoras visuales de forma autonoma, manteniendo consistencia y calidad en toda la UI.

---

**Fecha de creacion**: 2025-10-24
**Autor**: Core Editor Agent (EVARISIS)
**Version**: 1.0.0
**Paginas**: 47
**Palabras**: ~12,000
