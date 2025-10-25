#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visor de Reportes de Importación (V6.0.6)
Permite visualizar reportes guardados de importaciones anteriores

NUEVO EN V6.0.6:
- Visualizar reportes guardados en data/reportes_importacion/
- Listar cronológicamente las importaciones realizadas
- Abrir y explorar reportes previos con pestañas
- Comparar estadísticas entre importaciones
"""

import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import List, Dict, Optional
import logging
from pathlib import Path
import json
from datetime import datetime


class VisorReportesImportacion(tk.Toplevel):
    """Ventana para visualizar reportes guardados de importaciones"""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("EVARISIS - Visor de Reportes de Importación")
        self.geometry("1200x800")
        self.resizable(True, True)

        # Modal
        self.transient(parent)
        self.grab_set()

        self._crear_ui()
        self._cargar_lista_reportes()

    def _crear_ui(self):
        """Crear interfaz del visor"""
        # Frame principal
        main_frame = ttkb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título
        ttkb.Label(
            main_frame,
            text="📋 Reportes de Importación Guardados",
            font=("Segoe UI", 18, "bold"),
            bootstyle="info"
        ).pack(pady=(0, 15))

        # Descripción
        ttkb.Label(
            main_frame,
            text="Seleccione un reporte para ver detalles de una importación anterior",
            font=("Segoe UI", 10),
            foreground="#666"
        ).pack(pady=(0, 20))

        # Frame contenedor de lista y detalles
        content_frame = ttkb.Frame(main_frame)
        content_frame.pack(fill=BOTH, expand=YES)

        # Panel izquierdo: Lista de reportes
        left_panel = ttkb.LabelFrame(
            content_frame,
            text="📂 Reportes Disponibles",
            bootstyle="info",
            padding=10
        )
        left_panel.pack(side=LEFT, fill=BOTH, expand=NO, padx=(0, 10))
        left_panel.config(width=350)

        # Treeview para lista de reportes
        tree_frame = ttkb.Frame(left_panel)
        tree_frame.pack(fill=BOTH, expand=YES)

        scrollbar = ttkb.Scrollbar(tree_frame, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("fecha", "total", "completos"),
            show="tree headings",
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.heading("#0", text="ID")
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("total", text="Total")
        self.tree.heading("completos", text="Completos")

        self.tree.column("#0", width=100)
        self.tree.column("fecha", width=120)
        self.tree.column("total", width=60)
        self.tree.column("completos", width=70)

        self.tree.pack(fill=BOTH, expand=YES)

        # Bind doble click
        self.tree.bind("<Double-1>", lambda e: self._mostrar_reporte_seleccionado())

        # Botón ver reporte
        ttkb.Button(
            left_panel,
            text="Ver Reporte",
            command=self._mostrar_reporte_seleccionado,
            bootstyle="info",
            width=30
        ).pack(pady=(10, 0))

        # Panel derecho: Detalles del reporte
        self.right_panel = ttkb.LabelFrame(
            content_frame,
            text="📊 Detalles del Reporte",
            bootstyle="success",
            padding=10
        )
        self.right_panel.pack(side=RIGHT, fill=BOTH, expand=YES)

        # Mensaje inicial
        self.mensaje_inicial = ttkb.Label(
            self.right_panel,
            text="Seleccione un reporte de la lista para ver sus detalles",
            font=("Segoe UI", 12),
            foreground="#999"
        )
        self.mensaje_inicial.pack(pady=50)

        # Botón cerrar
        ttkb.Button(
            main_frame,
            text="Cerrar",
            command=self.destroy,
            bootstyle="secondary",
            width=20
        ).pack(pady=(20, 0))

    def _cargar_lista_reportes(self):
        """Cargar lista de reportes disponibles"""
        reportes_dir = Path("data/reportes_importacion")

        if not reportes_dir.exists():
            reportes_dir.mkdir(parents=True, exist_ok=True)
            return

        # Buscar archivos JSON
        reportes_files = sorted(
            reportes_dir.glob("reporte_importacion_*.json"),
            reverse=True  # Más recientes primero
        )

        if not reportes_files:
            return

        # Cargar y mostrar cada reporte
        for i, reporte_file in enumerate(reportes_files):
            try:
                with open(reporte_file, 'r', encoding='utf-8') as f:
                    reporte = json.load(f)

                # Extraer información
                timestamp = reporte.get('timestamp', '')
                resumen = reporte.get('resumen', {})
                total = resumen.get('total', 0)
                completos = resumen.get('completos', 0)

                # Formatear fecha
                try:
                    fecha_obj = datetime.fromisoformat(timestamp)
                    fecha_str = fecha_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    fecha_str = timestamp[:19] if len(timestamp) >= 19 else timestamp

                # Insertar en tree
                item_id = f"reporte_{i+1}"
                self.tree.insert(
                    "",
                    "end",
                    iid=item_id,
                    text=f"#{i+1}",
                    values=(fecha_str, total, completos),
                    tags=(str(reporte_file),)
                )

            except Exception as e:
                logging.error(f"Error cargando reporte {reporte_file}: {e}")

    def _mostrar_reporte_seleccionado(self):
        """Mostrar detalles del reporte seleccionado"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning(
                "Sin selección",
                "Por favor seleccione un reporte de la lista"
            )
            return

        # Obtener ruta del archivo
        item = selection[0]
        tags = self.tree.item(item, "tags")
        if not tags:
            return

        ruta_reporte = Path(tags[0])

        try:
            # Cargar reporte
            with open(ruta_reporte, 'r', encoding='utf-8') as f:
                reporte = json.load(f)

            # Limpiar panel derecho
            for widget in self.right_panel.winfo_children():
                widget.destroy()

            # Crear canvas scrollable
            canvas_frame = ttkb.Frame(self.right_panel)
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

            # Mostrar información del reporte
            self._mostrar_resumen_reporte(scrollable_frame, reporte)
            self._mostrar_casos_reporte(scrollable_frame, reporte)
            self._mostrar_correcciones_reporte(scrollable_frame, reporte)

            canvas.pack(side=LEFT, fill=BOTH, expand=YES)
            scrollbar.pack(side=RIGHT, fill=Y)

        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Error cargando reporte:\n{str(e)}"
            )
            logging.error(f"Error mostrando reporte: {e}")

    def _mostrar_resumen_reporte(self, parent, reporte: Dict):
        """Mostrar resumen del reporte"""
        resumen = reporte.get('resumen', {})
        timestamp = reporte.get('timestamp', '')

        # Frame de resumen
        resumen_frame = ttkb.LabelFrame(
            parent,
            text="📊 Resumen de Importación",
            bootstyle="info",
            padding=15
        )
        resumen_frame.pack(fill=X, padx=10, pady=10)

        # Fecha
        try:
            fecha_obj = datetime.fromisoformat(timestamp)
            fecha_str = fecha_obj.strftime("%d/%m/%Y a las %H:%M:%S")
        except:
            fecha_str = timestamp

        ttkb.Label(
            resumen_frame,
            text=f"📅 Fecha: {fecha_str}",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, pady=3)

        # Métricas
        total = resumen.get('total', 0)
        completos = resumen.get('completos', 0)
        incompletos = resumen.get('incompletos', 0)
        exito = resumen.get('porcentaje_exito', 0.0)
        correcciones = resumen.get('total_correcciones', 0)

        metricas = [
            ("📄 Total procesados:", str(total)),
            ("✅ Completos:", f"{completos} ({(completos/total*100) if total > 0 else 0:.1f}%)"),
            ("⚠️ Incompletos:", f"{incompletos} ({(incompletos/total*100) if total > 0 else 0:.1f}%)"),
            ("📈 Tasa de éxito:", f"{exito:.1f}%"),
            ("🔧 Correcciones:", str(correcciones)),
        ]

        for label, value in metricas:
            metric_frame = ttkb.Frame(resumen_frame)
            metric_frame.pack(fill=X, pady=2)

            ttkb.Label(
                metric_frame,
                text=label,
                font=("Segoe UI", 9, "bold"),
                width=20,
                anchor=W
            ).pack(side=LEFT)

            ttkb.Label(
                metric_frame,
                text=value,
                font=("Segoe UI", 9)
            ).pack(side=LEFT)

    def _mostrar_casos_reporte(self, parent, reporte: Dict):
        """Mostrar resumen de casos del reporte"""
        completos = reporte.get('completos', [])
        incompletos = reporte.get('incompletos', [])

        # Frame de casos
        casos_frame = ttkb.LabelFrame(
            parent,
            text="📋 Casos Procesados",
            bootstyle="success",
            padding=15
        )
        casos_frame.pack(fill=X, padx=10, pady=10)

        # Completos
        if completos:
            ttkb.Label(
                casos_frame,
                text=f"✅ Casos Completos ({len(completos)})",
                font=("Segoe UI", 10, "bold"),
                bootstyle="success"
            ).pack(anchor=W, pady=(5, 5))

            for caso in completos[:5]:  # Mostrar primeros 5
                numero = caso.get('numero_peticion', 'N/A')
                nombre = caso.get('paciente_nombre', 'N/A')
                ttkb.Label(
                    casos_frame,
                    text=f"  • {numero} - {nombre}",
                    font=("Segoe UI", 9)
                ).pack(anchor=W, padx=20)

            if len(completos) > 5:
                ttkb.Label(
                    casos_frame,
                    text=f"  ... y {len(completos)-5} más",
                    font=("Segoe UI", 8, "italic"),
                    foreground="#999"
                ).pack(anchor=W, padx=20)

        # Incompletos
        if incompletos:
            ttkb.Label(
                casos_frame,
                text=f"⚠️ Casos Incompletos ({len(incompletos)})",
                font=("Segoe UI", 10, "bold"),
                bootstyle="warning"
            ).pack(anchor=W, pady=(15, 5))

            for caso in incompletos[:5]:  # Mostrar primeros 5
                numero = caso.get('numero_peticion', 'N/A')
                nombre = caso.get('paciente_nombre', 'N/A')
                completitud = caso.get('porcentaje_completitud', 0)
                ttkb.Label(
                    casos_frame,
                    text=f"  • {numero} - {nombre} ({completitud}%)",
                    font=("Segoe UI", 9)
                ).pack(anchor=W, padx=20)

            if len(incompletos) > 5:
                ttkb.Label(
                    casos_frame,
                    text=f"  ... y {len(incompletos)-5} más",
                    font=("Segoe UI", 8, "italic"),
                    foreground="#999"
                ).pack(anchor=W, padx=20)

    def _mostrar_correcciones_reporte(self, parent, reporte: Dict):
        """Mostrar resumen de correcciones del reporte"""
        correcciones_por_caso = reporte.get('correcciones_por_caso', {})

        if not correcciones_por_caso:
            return

        # Frame de correcciones
        corr_frame = ttkb.LabelFrame(
            parent,
            text="🔧 Correcciones Aplicadas",
            bootstyle="warning",
            padding=15
        )
        corr_frame.pack(fill=X, padx=10, pady=10)

        ttkb.Label(
            corr_frame,
            text=f"Total de casos con correcciones: {len(correcciones_por_caso)}",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W, pady=(5, 10))

        # Mostrar primeros casos
        for i, (numero_caso, correcciones) in enumerate(list(correcciones_por_caso.items())[:5]):
            ttkb.Label(
                corr_frame,
                text=f"  • {numero_caso}: {len(correcciones)} corrección(es)",
                font=("Segoe UI", 9)
            ).pack(anchor=W, padx=20, pady=2)

        if len(correcciones_por_caso) > 5:
            ttkb.Label(
                corr_frame,
                text=f"  ... y {len(correcciones_por_caso)-5} casos más",
                font=("Segoe UI", 8, "italic"),
                foreground="#999"
            ).pack(anchor=W, padx=20, pady=2)


def mostrar_visor_reportes(parent):
    """
    Función helper para mostrar el visor de reportes

    Args:
        parent: Ventana padre
    """
    visor = VisorReportesImportacion(parent)
    parent.wait_window(visor)
