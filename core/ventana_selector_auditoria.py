#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana de Selección de Tipo de Auditoría
Permite elegir entre auditoría Parcial (solo incompletos) o Completa (toda la BD)
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Callable


class VentanaSelectorAuditoria(tk.Toplevel):
    """Ventana para seleccionar tipo de auditoría: Parcial o Completa"""

    def __init__(self, parent, callback_seleccion: Callable):
        super().__init__(parent)

        self.callback_seleccion = callback_seleccion
        self.seleccion = None

        self._configurar_ventana()
        self._crear_ui()

    def _configurar_ventana(self):
        """Configurar ventana"""
        self.title("EVARISIS CIRUGÍA ONCOLÓGICA - Seleccionar Tipo de Auditoría")
        self.geometry("950x850")
        self.resizable(False, False)

        # Modal
        self.transient(self.master)
        self.grab_set()

        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.winfo_screenheight() // 2) - (550 // 2)
        self.geometry(f"650x550+{x}+{y}")

    def _crear_ui(self):
        """Crear interfaz"""
        # Frame principal con scroll
        main_frame = ttkb.Frame(self, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título
        ttkb.Label(
            main_frame,
            text="🔍 Seleccione Tipo de Auditoría",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        ).pack(pady=(0, 15))

        # Descripción
        ttkb.Label(
            main_frame,
            text="Elija el alcance de la auditoría con IA:",
            font=("Segoe UI", 11)
        ).pack(pady=(0, 20))

        # Canvas con scrollbar para opciones
        canvas_frame = ttkb.Frame(main_frame)
        canvas_frame.pack(fill=BOTH, expand=YES, pady=(0, 15))

        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        opciones_frame = ttkb.Frame(canvas)

        opciones_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=opciones_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel
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

        # Opción: Auditoría Parcial
        parcial_frame = ttkb.LabelFrame(
            opciones_frame,
            text="📋 Auditoría Parcial",
            padding=20,
            bootstyle="warning"
        )
        parcial_frame.pack(fill=X, pady=10)

        ttkb.Label(
            parcial_frame,
            text="Solo analiza registros INCOMPLETOS",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W)

        ttkb.Label(
            parcial_frame,
            text="• Busca campos faltantes en registros incompletos\n"
                 "• Más rápido y eficiente\n"
                 "• Recomendado para importaciones recientes",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=W, pady=(5, 10))

        ttkb.Button(
            parcial_frame,
            text="✅ Seleccionar Parcial",
            command=lambda: self._seleccionar('parcial'),
            bootstyle="warning",
            width=25
        ).pack()

        # Opción: Auditoría Completa
        completa_frame = ttkb.LabelFrame(
            opciones_frame,
            text="📊 Auditoría Completa",
            padding=20,
            bootstyle="info"
        )
        completa_frame.pack(fill=X, pady=10)

        ttkb.Label(
            completa_frame,
            text="Analiza TODOS los registros de la base de datos",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor=W)

        ttkb.Label(
            completa_frame,
            text="• Revisa todos los registros (completos e incompletos)\n"
                 "• Análisis exhaustivo de calidad de datos\n"
                 "• Puede tomar más tiempo",
            font=("Segoe UI", 9),
            foreground="#666666"
        ).pack(anchor=W, pady=(5, 10))

        ttkb.Button(
            completa_frame,
            text="✅ Seleccionar Completa",
            command=lambda: self._seleccionar('completa'),
            bootstyle="info",
            width=25
        ).pack()

        # Botón Cancelar
        ttkb.Button(
            main_frame,
            text="❌ Cancelar",
            command=self._cancelar,
            bootstyle="secondary",
            width=20
        ).pack(pady=(20, 0))

    def _seleccionar(self, tipo: str):
        """Usuario seleccionó un tipo de auditoría"""
        self.seleccion = tipo
        self.destroy()
        self.callback_seleccion(tipo)

    def _cancelar(self):
        """Usuario canceló"""
        self.seleccion = None
        self.destroy()


def mostrar_selector_auditoria(parent, callback_seleccion: Callable):
    """
    Función helper para mostrar ventana de selección

    Args:
        parent: Ventana padre
        callback_seleccion: Función(tipo) a llamar con 'parcial' o 'completa'
    """
    ventana = VentanaSelectorAuditoria(
        parent=parent,
        callback_seleccion=callback_seleccion
    )

    # Esperar a que se cierre
    parent.wait_window(ventana)
