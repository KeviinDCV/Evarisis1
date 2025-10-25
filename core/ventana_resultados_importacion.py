#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana de Resultados Post-Importación (V6.0.6)
Muestra registros completos vs incompletos y ofrece auditoría IA

MEJORAS V6.0.6:
- Sistema de pestañas (Notebook) para organizar información
- Casos colapsables/expandibles por defecto
- Guardado automático de reportes en data/reportes_importacion/
- Pestaña de estadísticas con gráficos
- Interfaz más limpia y navegable
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Dict, List, Any, Callable, Optional
import logging
from pathlib import Path
import json
from datetime import datetime


class VentanaResultadosImportacion(tk.Toplevel):
    """Ventana emergente que muestra resultados de importación"""

    def __init__(
        self,
        parent,
        completos: List[Dict],
        incompletos: List[Dict],
        resumen: Dict,
        callback_auditar: Callable,
        callback_continuar: Callable
    ):
        """
        CRÍTICO: NO CAMBIAR FIRMA - Llamado desde ui.py líneas 4995, 5118, 5309

        Args:
            parent: Ventana padre
            completos: Lista de registros completos
            incompletos: Lista de registros incompletos
            resumen: Dict con {'total', 'completos', 'incompletos', 'porcentaje_exito'}
            callback_auditar: Función(tipo, registros) a llamar si elige auditar
            callback_continuar: Función() a llamar si elige continuar
        """
        super().__init__(parent)

        self.completos = completos
        self.incompletos = incompletos
        self.resumen = resumen
        self.callback_auditar = callback_auditar
        self.callback_continuar = callback_continuar

        # V6.0.6: Nuevo atributo para guardar ruta del reporte
        self.ruta_reporte_guardado = None

        self._configurar_ventana()
        self._crear_ui()

        # V6.0.6: Guardar reporte automáticamente al abrir
        self._guardar_reporte_automatico()

    def _configurar_ventana(self):
        """Configurar ventana maximizada (V5.3.9)"""
        self.title("EVARISIS CIRUGÍA ONCOLÓGICA - Resultados de Importación")

        # V5.3.9: Maximizar ventana como la UI principal
        self.state('zoomed')  # Windows
        # Para Linux/Mac: self.attributes('-zoomed', True)

        self.resizable(True, True)

        # Modal - mantener enfoque en esta ventana
        self.transient(self.master)
        self.grab_set()

    def _crear_seccion_resumen(self, parent):
        """Crear sección de resumen con estadísticas de importación (V5.3.9.3)"""
        # Frame contenedor del resumen
        resumen_frame = ttkb.Frame(parent, bootstyle="light")
        resumen_frame.pack(fill=X, pady=(0, 20), padx=20)

        # Título de la sección
        ttkb.Label(
            resumen_frame,
            text="📊 Resumen de Importación",
            font=("Segoe UI", 12, "bold"),
            bootstyle="info"
        ).pack(anchor=W, pady=(0, 10))

        # Frame para las estadísticas (horizontal)
        stats_frame = ttkb.Frame(resumen_frame)
        stats_frame.pack(fill=X, pady=(0, 5))

        # Obtener datos del resumen
        total = self.resumen.get('total', 0)
        completos = self.resumen.get('completos', 0)
        incompletos = self.resumen.get('incompletos', 0)
        porcentaje_exito = self.resumen.get('porcentaje_exito', 0.0)

        # Crear 4 badges con estadísticas
        badges = [
            ("📄 Total Procesados", str(total), "info"),
            ("✅ Completos", str(completos), "success"),
            ("⚠️ Incompletos", str(incompletos), "warning" if incompletos > 0 else "light"),
            ("📈 Éxito", f"{porcentaje_exito:.1f}%", "success" if porcentaje_exito >= 80 else "warning")
        ]

        for label_text, value_text, style in badges:
            badge_frame = ttkb.Frame(stats_frame, bootstyle=style)
            badge_frame.pack(side=LEFT, padx=10, pady=5, fill=X, expand=YES)

            # Etiqueta
            ttkb.Label(
                badge_frame,
                text=label_text,
                font=("Segoe UI", 9),
                bootstyle=style
            ).pack(pady=(5, 0))

            # Valor
            ttkb.Label(
                badge_frame,
                text=value_text,
                font=("Segoe UI", 16, "bold"),
                bootstyle=style
            ).pack(pady=(0, 5))

    def _cargar_correcciones_desde_debug_maps(self) -> List[Dict]:
        """
        Carga correcciones desde archivos debug_map de los casos procesados (V5.3.9)

        Returns:
            Lista de todas las correcciones aplicadas durante la importación
        """
        debug_maps_path = Path("data/debug_maps")
        todas_correcciones = []

        # Combinar todos los casos (completos + incompletos)
        todos_casos = self.completos + self.incompletos

        for caso in todos_casos:
            # Obtener número de petición del caso
            numero = caso.get('numero_peticion', '')
            if not numero:
                continue

            # Buscar debug_map más reciente de este caso
            try:
                debug_files = list(debug_maps_path.glob(f"debug_map_{numero}_*.json"))
                if not debug_files:
                    continue

                debug_file = sorted(debug_files)[-1]  # Más reciente

                # Leer el archivo JSON
                with open(debug_file, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)

                # Extraer correcciones
                correcciones_caso = debug_data.get("correcciones_aplicadas", [])
                if correcciones_caso:
                    todas_correcciones.extend(correcciones_caso)

            except Exception as e:
                logging.warning(f"⚠️ Error leyendo correcciones de {numero}: {e}")
                continue

        return todas_correcciones

    def _crear_ui(self):
        """V6.0.6: Crear interfaz con sistema de pestañas"""
        # Frame principal
        main_frame = ttkb.Frame(self, padding=40)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título fijo (no hace scroll)
        ttkb.Label(
            main_frame,
            text="🎉 Importación Completada",
            font=("Segoe UI", 22, "bold"),
            bootstyle="success"
        ).pack(pady=(0, 15))

        # Resumen fijo (no hace scroll)
        self._crear_seccion_resumen(main_frame)

        # V6.0.6: SISTEMA DE PESTAÑAS (Notebook)
        self.notebook = ttkb.Notebook(main_frame)
        self.notebook.pack(fill=BOTH, expand=YES, pady=(10, 20))

        # Crear pestañas
        self._crear_tab_resumen()
        self._crear_tab_completos()
        self._crear_tab_incompletos()
        self._crear_tab_correcciones()
        self._crear_tab_estadisticas()

        # Botones fijos al final (no hacen scroll)
        self._crear_botones_accion(main_frame)

    def _crear_tab_resumen(self):
        """V6.0.6: Pestaña de resumen general"""
        tab = ttkb.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Resumen General")

        # Crear canvas scrollable
        canvas_frame = ttkb.Frame(tab)
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con mousewheel
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Contenido del resumen
        ttkb.Label(
            scrollable_frame,
            text="📋 Vista General de la Importación",
            font=("Segoe UI", 16, "bold"),
            bootstyle="info"
        ).pack(anchor=W, pady=(20, 15), padx=20)

        # Información general
        info_frame = ttkb.LabelFrame(
            scrollable_frame,
            text="Información General",
            bootstyle="info",
            padding=20
        )
        info_frame.pack(fill=X, padx=20, pady=10)

        total = self.resumen.get('total', 0)
        completos_count = len(self.completos)
        incompletos_count = len(self.incompletos)
        porcentaje = self.resumen.get('porcentaje_exito', 0.0)

        info_items = [
            ("📄 Total de casos procesados:", str(total)),
            ("✅ Casos completos:", f"{completos_count} ({(completos_count/total*100) if total > 0 else 0:.1f}%)"),
            ("⚠️ Casos incompletos:", f"{incompletos_count} ({(incompletos_count/total*100) if total > 0 else 0:.1f}%)"),
            ("📈 Tasa de éxito:", f"{porcentaje:.1f}%"),
        ]

        for label, value in info_items:
            item_frame = ttkb.Frame(info_frame)
            item_frame.pack(fill=X, pady=5)

            ttkb.Label(
                item_frame,
                text=label,
                font=("Segoe UI", 10, "bold")
            ).pack(side=LEFT)

            ttkb.Label(
                item_frame,
                text=value,
                font=("Segoe UI", 10)
            ).pack(side=LEFT, padx=10)

        # Recomendaciones
        recom_frame = ttkb.LabelFrame(
            scrollable_frame,
            text="💡 Recomendaciones",
            bootstyle="warning",
            padding=20
        )
        recom_frame.pack(fill=X, padx=20, pady=10)

        if incompletos_count > 0:
            ttkb.Label(
                recom_frame,
                text=f"• Se detectaron {incompletos_count} caso(s) incompleto(s)",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=3)

            ttkb.Label(
                recom_frame,
                text="• Revise la pestaña 'Incompletos' para ver qué campos faltan",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=3)

            ttkb.Label(
                recom_frame,
                text="• Se recomienda usar auditoría con IA para completar campos faltantes",
                font=("Segoe UI", 10)
            ).pack(anchor=W, pady=3)
        else:
            ttkb.Label(
                recom_frame,
                text="✅ ¡Excelente! Todos los casos están completos",
                font=("Segoe UI", 10, "bold"),
                bootstyle="success"
            ).pack(anchor=W, pady=3)

        # Reporte guardado
        if hasattr(self, 'ruta_reporte_guardado') and self.ruta_reporte_guardado:
            reporte_frame = ttkb.LabelFrame(
                scrollable_frame,
                text="💾 Reporte Guardado",
                bootstyle="success",
                padding=20
            )
            reporte_frame.pack(fill=X, padx=20, pady=10)

            ttkb.Label(
                reporte_frame,
                text=f"Ruta: {self.ruta_reporte_guardado}",
                font=("Consolas", 9),
                foreground="#28a745"
            ).pack(anchor=W)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _crear_tab_completos(self):
        """V6.0.6: Pestaña de casos completos con colapsables"""
        tab = ttkb.Frame(self.notebook)
        self.notebook.add(tab, text=f"✅ Completos ({len(self.completos)})")

        if not self.completos:
            ttkb.Label(
                tab,
                text="No hay casos completos",
                font=("Segoe UI", 12),
                bootstyle="secondary"
            ).pack(pady=50)
            return

        # Crear canvas scrollable
        canvas_frame = ttkb.Frame(tab)
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con mousewheel
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Título
        ttkb.Label(
            scrollable_frame,
            text=f"✅ Casos Completos ({len(self.completos)})",
            font=("Segoe UI", 14, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=(10, 15), padx=20)

        # Crear cada caso como colapsable
        correcciones_por_caso = self._agrupar_correcciones_por_caso(
            self._cargar_correcciones_desde_debug_maps()
        )

        for reg in self.completos:
            numero = reg.get('numero_peticion', 'N/A')
            tiene_correcciones = numero in correcciones_por_caso
            self._crear_caso_completo_colapsable(
                scrollable_frame,
                reg,
                correcciones_por_caso.get(numero, [])
            )

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _crear_caso_completo_colapsable(self, parent, caso: Dict, correcciones: List[Dict]):
        """V6.0.6: Crear caso completo colapsable"""
        # Frame principal del caso
        caso_container = ttkb.Frame(parent)
        caso_container.pack(fill=X, padx=20, pady=5)

        # Variable para estado expandido
        expandido = tk.BooleanVar(value=False)

        # Header clickeable
        header_frame = ttkb.Frame(caso_container, bootstyle="success-light")
        header_frame.pack(fill=X)

        # Indicador ▶/▼
        icon_label = ttkb.Label(header_frame, text="▶", font=("Segoe UI", 10))
        icon_label.pack(side=LEFT, padx=10, pady=8)

        # Título caso
        numero = caso.get('numero_peticion', 'N/A')
        nombre = caso.get('paciente_nombre', 'N/A')
        completitud = caso.get('porcentaje_completitud', 100)

        titulo = f"{numero} - {nombre} ({completitud}%)"
        if correcciones:
            titulo += f" - 🔧 {len(correcciones)} corrección(es)"

        titulo_label = ttkb.Label(
            header_frame,
            text=titulo,
            font=("Segoe UI", 10, "bold"),
            bootstyle="success"
        )
        titulo_label.pack(side=LEFT, padx=10, pady=8)

        # Contenido expandible (oculto por defecto)
        content_frame = ttkb.Frame(caso_container, bootstyle="light")
        content_frame.pack_forget()  # Oculto inicialmente

        # Agregar información del caso
        info_frame = ttkb.Frame(content_frame, padding=10)
        info_frame.pack(fill=X)

        # Mostrar correcciones si existen
        if correcciones:
            ttkb.Label(
                info_frame,
                text=f"🔧 Correcciones aplicadas ({len(correcciones)}):",
                font=("Segoe UI", 9, "bold"),
                foreground="#28a745"
            ).pack(anchor=W, pady=(5, 5))

            for corr in correcciones[:5]:  # Mostrar máximo 5
                campo = corr.get('campo', 'N/A')
                ttkb.Label(
                    info_frame,
                    text=f"  • {campo}",
                    font=("Segoe UI", 9),
                    foreground="#666"
                ).pack(anchor=W, padx=20)

            if len(correcciones) > 5:
                ttkb.Label(
                    info_frame,
                    text=f"  ... y {len(correcciones)-5} más (ver pestaña Correcciones)",
                    font=("Segoe UI", 8, "italic"),
                    foreground="#999"
                ).pack(anchor=W, padx=20)
        else:
            ttkb.Label(
                info_frame,
                text="✅ Sin correcciones aplicadas (datos originales correctos)",
                font=("Segoe UI", 9),
                foreground="#28a745"
            ).pack(anchor=W, pady=5)

        # Función toggle
        def toggle_expand(event=None):
            if expandido.get():
                content_frame.pack_forget()
                icon_label.config(text="▶")
                expandido.set(False)
            else:
                content_frame.pack(fill=X, padx=20, pady=5)
                icon_label.config(text="▼")
                expandido.set(True)

        # Bind click
        header_frame.bind("<Button-1>", toggle_expand)
        icon_label.bind("<Button-1>", toggle_expand)
        titulo_label.bind("<Button-1>", toggle_expand)

    def _crear_tab_incompletos(self):
        """V6.0.6: Pestaña de casos incompletos con colapsables"""
        tab = ttkb.Frame(self.notebook)
        self.notebook.add(tab, text=f"⚠️ Incompletos ({len(self.incompletos)})")

        if not self.incompletos:
            ttkb.Label(
                tab,
                text="✅ No hay casos incompletos",
                font=("Segoe UI", 12),
                bootstyle="success"
            ).pack(pady=50)
            return

        # Crear canvas scrollable
        canvas_frame = ttkb.Frame(tab)
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con mousewheel
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Título
        ttkb.Label(
            scrollable_frame,
            text=f"⚠️ Casos Incompletos ({len(self.incompletos)})",
            font=("Segoe UI", 14, "bold"),
            bootstyle="warning"
        ).pack(anchor=W, pady=(10, 15), padx=20)

        # Crear cada caso como colapsable
        correcciones_por_caso = self._agrupar_correcciones_por_caso(
            self._cargar_correcciones_desde_debug_maps()
        )

        for reg in self.incompletos:
            numero = reg.get('numero_peticion', 'N/A')
            self._crear_caso_incompleto_colapsable(
                scrollable_frame,
                reg,
                correcciones_por_caso.get(numero, [])
            )

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _crear_caso_incompleto_colapsable(self, parent, caso: Dict, correcciones: List[Dict]):
        """V6.0.6: Crear caso incompleto colapsable"""
        # Frame principal del caso
        caso_container = ttkb.Frame(parent)
        caso_container.pack(fill=X, padx=20, pady=5)

        # Variable para estado expandido
        expandido = tk.BooleanVar(value=False)

        # Header clickeable
        header_frame = ttkb.Frame(caso_container, bootstyle="warning-light")
        header_frame.pack(fill=X)

        # Indicador ▶/▼
        icon_label = ttkb.Label(header_frame, text="▶", font=("Segoe UI", 10))
        icon_label.pack(side=LEFT, padx=10, pady=8)

        # Título caso
        numero = caso.get('numero_peticion', 'N/A')
        nombre = caso.get('paciente_nombre', 'N/A')
        completitud = caso.get('porcentaje_completitud', 0)

        titulo = f"{numero} - {nombre} ({completitud}%)"
        if correcciones:
            titulo += f" - 🔧 {len(correcciones)} corrección(es)"

        titulo_label = ttkb.Label(
            header_frame,
            text=titulo,
            font=("Segoe UI", 10, "bold"),
            bootstyle="warning"
        )
        titulo_label.pack(side=LEFT, padx=10, pady=8)

        # Contenido expandible (oculto por defecto)
        content_frame = ttkb.Frame(caso_container, bootstyle="light")
        content_frame.pack_forget()  # Oculto inicialmente

        # Agregar información del caso
        info_frame = ttkb.Frame(content_frame, padding=10)
        info_frame.pack(fill=X)

        # Mostrar campos faltantes
        campos_faltantes_detalle = caso.get('campos_faltantes_detalle', '')
        if campos_faltantes_detalle and campos_faltantes_detalle != 'Ninguno':
            ttkb.Label(
                info_frame,
                text="⚠️ Campos faltantes:",
                font=("Segoe UI", 9, "bold"),
                foreground="#dc3545"
            ).pack(anchor=W, pady=(5, 5))

            for linea in campos_faltantes_detalle.split('\n'):
                if linea.strip():
                    ttkb.Label(
                        info_frame,
                        text=f"  • {linea}",
                        font=("Segoe UI", 9),
                        foreground="#666"
                    ).pack(anchor=W, padx=20)

        # Mostrar correcciones si existen
        if correcciones:
            ttkb.Label(
                info_frame,
                text=f"🔧 Correcciones aplicadas ({len(correcciones)}):",
                font=("Segoe UI", 9, "bold"),
                foreground="#28a745"
            ).pack(anchor=W, pady=(10, 5))

            for corr in correcciones[:3]:  # Mostrar máximo 3
                campo = corr.get('campo', 'N/A')
                ttkb.Label(
                    info_frame,
                    text=f"  • {campo}",
                    font=("Segoe UI", 9),
                    foreground="#666"
                ).pack(anchor=W, padx=20)

            if len(correcciones) > 3:
                ttkb.Label(
                    info_frame,
                    text=f"  ... y {len(correcciones)-3} más (ver pestaña Correcciones)",
                    font=("Segoe UI", 8, "italic"),
                    foreground="#999"
                ).pack(anchor=W, padx=20)

        # Función toggle
        def toggle_expand(event=None):
            if expandido.get():
                content_frame.pack_forget()
                icon_label.config(text="▶")
                expandido.set(False)
            else:
                content_frame.pack(fill=X, padx=20, pady=5)
                icon_label.config(text="▼")
                expandido.set(True)

        # Bind click
        header_frame.bind("<Button-1>", toggle_expand)
        icon_label.bind("<Button-1>", toggle_expand)
        titulo_label.bind("<Button-1>", toggle_expand)

    def _crear_tab_correcciones(self):
        """V6.0.6: Pestaña de correcciones con colapsables por caso"""
        tab = ttkb.Frame(self.notebook)

        # Cargar correcciones
        correcciones = self._cargar_correcciones_desde_debug_maps()
        correcciones_por_caso = self._agrupar_correcciones_por_caso(correcciones)

        self.notebook.add(tab, text=f"🔧 Correcciones ({len(correcciones_por_caso)})")

        if not correcciones_por_caso:
            ttkb.Label(
                tab,
                text="✅ No se aplicaron correcciones automáticas",
                font=("Segoe UI", 12),
                bootstyle="success"
            ).pack(pady=50)
            return

        # Crear canvas scrollable
        canvas_frame = ttkb.Frame(tab)
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con mousewheel
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Título
        ttkb.Label(
            scrollable_frame,
            text=f"🔧 Correcciones Aplicadas ({len(correcciones_por_caso)} casos)",
            font=("Segoe UI", 14, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=(10, 15), padx=20)

        # Descripción
        ttkb.Label(
            scrollable_frame,
            text="✨ El sistema detectó y corrigió automáticamente las siguientes inconsistencias:",
            font=("Segoe UI", 10, "italic"),
            foreground="#155724"
        ).pack(anchor=W, pady=(0, 15), padx=20)

        # Crear cada caso como colapsable
        for numero_caso, correcciones_caso in correcciones_por_caso.items():
            self._crear_caso_correcciones_colapsable(scrollable_frame, numero_caso, correcciones_caso)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _crear_caso_correcciones_colapsable(self, parent, numero_caso: str, correcciones: List[Dict]):
        """V6.0.6: Crear caso con correcciones colapsable"""
        # Frame principal del caso
        caso_container = ttkb.Frame(parent)
        caso_container.pack(fill=X, padx=20, pady=5)

        # Variable para estado expandido
        expandido = tk.BooleanVar(value=False)

        # Header clickeable
        header_frame = ttkb.Frame(caso_container, bootstyle="success-light")
        header_frame.pack(fill=X)

        # Indicador ▶/▼
        icon_label = ttkb.Label(header_frame, text="▶", font=("Segoe UI", 10))
        icon_label.pack(side=LEFT, padx=10, pady=8)

        # Título caso
        titulo = f"📄 {numero_caso} - {len(correcciones)} corrección(es)"
        titulo_label = ttkb.Label(
            header_frame,
            text=titulo,
            font=("Segoe UI", 10, "bold"),
            bootstyle="success"
        )
        titulo_label.pack(side=LEFT, padx=10, pady=8)

        # Contenido expandible (oculto por defecto)
        content_frame = ttkb.Frame(caso_container, bootstyle="light")
        content_frame.pack_forget()  # Oculto inicialmente

        # Agrupar correcciones por tipo
        por_tipo = {
            "ortografica": [],
            "medico_servicio": [],
            "normalizacion_biomarcador": []
        }
        for corr in correcciones:
            tipo = corr.get("tipo", "ortografica")
            if tipo in por_tipo:
                por_tipo[tipo].append(corr)

        # Mostrar cada tipo
        if por_tipo["ortografica"]:
            self._mostrar_grupo_correcciones(
                content_frame,
                "📝 Correcciones Ortográficas",
                por_tipo["ortografica"]
            )

        if por_tipo["medico_servicio"]:
            self._mostrar_grupo_correcciones(
                content_frame,
                "🩺 Validación Médico-Servicio",
                por_tipo["medico_servicio"]
            )

        if por_tipo["normalizacion_biomarcador"]:
            self._mostrar_grupo_correcciones(
                content_frame,
                "🧬 Normalización Biomarcadores",
                por_tipo["normalizacion_biomarcador"]
            )

        # Función toggle
        def toggle_expand(event=None):
            if expandido.get():
                content_frame.pack_forget()
                icon_label.config(text="▶")
                expandido.set(False)
            else:
                content_frame.pack(fill=X, padx=20, pady=5)
                icon_label.config(text="▼")
                expandido.set(True)

        # Bind click
        header_frame.bind("<Button-1>", toggle_expand)
        icon_label.bind("<Button-1>", toggle_expand)
        titulo_label.bind("<Button-1>", toggle_expand)

    def _mostrar_grupo_correcciones(self, parent, titulo: str, correcciones: List[Dict]):
        """V6.0.6: Mostrar un grupo de correcciones"""
        grupo_frame = ttkb.Frame(parent, padding=10)
        grupo_frame.pack(fill=X)

        ttkb.Label(
            grupo_frame,
            text=f"{titulo} ({len(correcciones)})",
            font=("Segoe UI", 9, "bold"),
            foreground="#17a2b8"
        ).pack(anchor=W, pady=(5, 5))

        for corr in correcciones:
            self._mostrar_detalle_correccion(grupo_frame, corr)

    def _mostrar_detalle_correccion(self, parent, correccion: Dict):
        """V6.0.6: Mostrar detalle de una corrección individual"""
        campo = correccion.get('campo', 'N/A')
        antes = correccion.get('valor_original', '')
        despues = correccion.get('valor_corregido', '')
        razon = correccion.get('razon', '')

        # Truncar valores muy largos
        antes_display = (antes[:60] + '...') if len(antes) > 60 else antes
        despues_display = (despues[:60] + '...') if len(despues) > 60 else despues

        # Frame para cada corrección individual
        corr_frame = ttkb.Frame(parent)
        corr_frame.pack(fill=X, padx=10, pady=2)

        # Campo
        ttkb.Label(
            corr_frame,
            text=f"  • {campo}:",
            font=("Segoe UI", 9, "bold"),
            foreground="#333"
        ).pack(anchor=W)

        # Antes → Después
        ttkb.Label(
            corr_frame,
            text=f"    ❌ Antes: {antes_display}",
            font=("Consolas", 8),
            foreground="#dc3545"
        ).pack(anchor=W, padx=10)

        ttkb.Label(
            corr_frame,
            text=f"    ✅ Después: {despues_display}",
            font=("Consolas", 8),
            foreground="#28a745"
        ).pack(anchor=W, padx=10)

        # Razón
        if razon:
            ttkb.Label(
                corr_frame,
                text=f"    💡 Razón: {razon}",
                font=("Segoe UI", 8, "italic"),
                foreground="#6c757d"
            ).pack(anchor=W, padx=10, pady=(2, 0))

    def _crear_tab_estadisticas(self):
        """V6.0.6: Pestaña de estadísticas con gráficos"""
        tab = ttkb.Frame(self.notebook)
        self.notebook.add(tab, text="📈 Estadísticas")

        # Crear canvas scrollable
        canvas_frame = ttkb.Frame(tab)
        canvas_frame.pack(fill=BOTH, expand=YES)

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Scroll con mousewheel
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Título
        ttkb.Label(
            scrollable_frame,
            text="📈 Análisis Estadístico de Importación",
            font=("Segoe UI", 16, "bold"),
            bootstyle="info"
        ).pack(anchor=W, pady=(20, 15), padx=20)

        # Métricas generales
        metricas_frame = ttkb.LabelFrame(
            scrollable_frame,
            text="📊 Métricas Generales",
            bootstyle="info",
            padding=20
        )
        metricas_frame.pack(fill=X, padx=20, pady=10)

        total = self.resumen.get('total', 0)
        completos = len(self.completos)
        incompletos = len(self.incompletos)

        correcciones = self._cargar_correcciones_desde_debug_maps()
        total_correcciones = len(correcciones)

        metricas = [
            ("Total de casos procesados", str(total)),
            ("Casos completos", f"{completos} ({(completos/total*100) if total > 0 else 0:.1f}%)"),
            ("Casos incompletos", f"{incompletos} ({(incompletos/total*100) if total > 0 else 0:.1f}%)"),
            ("Total de correcciones aplicadas", str(total_correcciones)),
            ("Promedio de correcciones por caso", f"{(total_correcciones/total) if total > 0 else 0:.1f}"),
        ]

        for label, value in metricas:
            metric_frame = ttkb.Frame(metricas_frame)
            metric_frame.pack(fill=X, pady=5)

            ttkb.Label(
                metric_frame,
                text=f"{label}:",
                font=("Segoe UI", 10, "bold")
            ).pack(side=LEFT)

            ttkb.Label(
                metric_frame,
                text=value,
                font=("Segoe UI", 10),
                bootstyle="info"
            ).pack(side=LEFT, padx=10)

        # Tipos de correcciones
        if correcciones:
            tipos_frame = ttkb.LabelFrame(
                scrollable_frame,
                text="🔧 Tipos de Correcciones",
                bootstyle="success",
                padding=20
            )
            tipos_frame.pack(fill=X, padx=20, pady=10)

            tipos_count = {}
            for corr in correcciones:
                tipo = corr.get('tipo', 'Desconocido')
                tipos_count[tipo] = tipos_count.get(tipo, 0) + 1

            for tipo, count in sorted(tipos_count.items(), key=lambda x: x[1], reverse=True):
                tipo_frame = ttkb.Frame(tipos_frame)
                tipo_frame.pack(fill=X, pady=3)

                # Barra de progreso visual
                porcentaje = (count / total_correcciones * 100) if total_correcciones > 0 else 0

                ttkb.Label(
                    tipo_frame,
                    text=f"{tipo}:",
                    font=("Segoe UI", 10, "bold"),
                    width=30,
                    anchor=W
                ).pack(side=LEFT)

                ttkb.Label(
                    tipo_frame,
                    text=f"{count} ({porcentaje:.1f}%)",
                    font=("Segoe UI", 10)
                ).pack(side=LEFT, padx=10)

                # Barra visual simple
                barra_frame = ttkb.Frame(tipo_frame, bootstyle="success")
                barra_frame.pack(side=LEFT, fill=X, expand=YES)

                barra_width = int(porcentaje * 2)  # Escalar para visualización
                ttkb.Label(
                    barra_frame,
                    text=" " * barra_width,
                    bootstyle="success"
                ).pack()

        # Campos más corregidos
        if correcciones:
            campos_frame = ttkb.LabelFrame(
                scrollable_frame,
                text="📝 Campos Más Corregidos",
                bootstyle="warning",
                padding=20
            )
            campos_frame.pack(fill=X, padx=20, pady=10)

            campos_count = {}
            for corr in correcciones:
                campo = corr.get('campo', 'Desconocido')
                campos_count[campo] = campos_count.get(campo, 0) + 1

            # Top 10 campos
            top_campos = sorted(campos_count.items(), key=lambda x: x[1], reverse=True)[:10]

            for campo, count in top_campos:
                campo_frame = ttkb.Frame(campos_frame)
                campo_frame.pack(fill=X, pady=3)

                ttkb.Label(
                    campo_frame,
                    text=f"{campo}:",
                    font=("Segoe UI", 10, "bold"),
                    width=40,
                    anchor=W
                ).pack(side=LEFT)

                ttkb.Label(
                    campo_frame,
                    text=f"{count} vez/veces",
                    font=("Segoe UI", 10)
                ).pack(side=LEFT, padx=10)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _agrupar_correcciones_por_caso(self, correcciones: List[Dict]) -> Dict[str, List[Dict]]:
        """V6.0.6: Agrupar correcciones por número de caso"""
        por_caso = {}
        for corr in correcciones:
            numero_caso = corr.get('numero_caso', 'DESCONOCIDO')
            if numero_caso not in por_caso:
                por_caso[numero_caso] = []
            por_caso[numero_caso].append(corr)
        return por_caso

    def _guardar_reporte_automatico(self):
        """V6.0.6: Guardar reporte automáticamente al abrir la ventana"""
        try:
            # Crear directorio si no existe
            reportes_dir = Path("data/reportes_importacion")
            reportes_dir.mkdir(parents=True, exist_ok=True)

            # Generar timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_importacion_{timestamp}.json"
            ruta_reporte = reportes_dir / nombre_archivo

            # Cargar correcciones
            correcciones = self._cargar_correcciones_desde_debug_maps()

            # Estructura del reporte
            reporte = {
                "timestamp": datetime.now().isoformat(),
                "resumen": {
                    "total": self.resumen.get('total', 0),
                    "completos": len(self.completos),
                    "incompletos": len(self.incompletos),
                    "porcentaje_exito": self.resumen.get('porcentaje_exito', 0.0),
                    "total_correcciones": len(correcciones)
                },
                "completos": self.completos,
                "incompletos": self.incompletos,
                "correcciones": correcciones,
                "correcciones_por_caso": self._agrupar_correcciones_por_caso(correcciones)
            }

            # Guardar JSON
            with open(ruta_reporte, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, indent=2, ensure_ascii=False)

            # Guardar ruta
            self.ruta_reporte_guardado = str(ruta_reporte)

            # CRÍTICO: Guardar en parent para visualización posterior
            if hasattr(self.master, '_ultima_ruta_reporte_importacion'):
                self.master._ultima_ruta_reporte_importacion = str(ruta_reporte)

            logging.info(f"✅ Reporte guardado automáticamente: {ruta_reporte}")

        except Exception as e:
            logging.error(f"❌ Error guardando reporte automático: {e}")

    def _crear_botones_accion(self, parent):
        """Botones de acción mejorados para pantalla completa (V5.3.9)"""
        frame = ttkb.Frame(parent)
        frame.pack(fill=X, pady=(20, 0))

        # Pregunta más grande
        ttkb.Label(
            frame,
            text="🤖 ¿Desea realizar auditoría con Inteligencia Artificial?",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 20))

        # Botones más grandes y visibles
        btn_frame = ttkb.Frame(frame)
        btn_frame.pack()

        ttkb.Button(
            btn_frame,
            text="✅ Sí, auditar con IA",
            command=self._on_auditar,
            bootstyle="success",
            width=25,
            padding=(20, 10)
        ).pack(side=LEFT, padx=15)

        ttkb.Button(
            btn_frame,
            text="❌ No, continuar",
            command=self._on_continuar,
            bootstyle="secondary",
            width=25,
            padding=(20, 10)
        ).pack(side=LEFT, padx=15)

    def _on_auditar(self):
        """Usuario elige auditar"""
        # Cerrar ventana actual
        self.destroy()

        # Mostrar selector de tipo de auditoría
        # TODO: Implementar ventana de selección
        # Por ahora, auditar solo incompletos si los hay
        if self.incompletos:
            self.callback_auditar('parcial', self.incompletos)
        else:
            self.callback_auditar('completa', None)

    def _on_continuar(self):
        """Usuario elige continuar sin auditoría"""
        self.destroy()
        self.callback_continuar()


def mostrar_ventana_resultados(
    parent,
    completos: List[Dict],
    incompletos: List[Dict],
    resumen: Dict,
    callback_auditar: Callable,
    callback_continuar: Callable
):
    """
    CRÍTICO: NO CAMBIAR FIRMA - Función helper para mostrar ventana
    Llamado desde ui.py líneas 4995, 5118, 5309

    V6.0.6: Las correcciones ya NO se pasan como parámetro.
    La ventana las carga automáticamente desde los archivos debug_map.
    Los reportes se guardan automáticamente en data/reportes_importacion/

    Args:
        parent: Ventana padre
        completos: Lista de registros completos
        incompletos: Lista de registros incompletos
        resumen: Dict con resumen {'total', 'completos', 'incompletos'}
        callback_auditar: Función(tipo, registros) a llamar si elige auditar
        callback_continuar: Función() a llamar si elige continuar
    """
    ventana = VentanaResultadosImportacion(
        parent=parent,
        completos=completos,
        incompletos=incompletos,
        resumen=resumen,
        callback_auditar=callback_auditar,
        callback_continuar=callback_continuar
    )

    # Esperar a que se cierre la ventana
    parent.wait_window(ventana)
