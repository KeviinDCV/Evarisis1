#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ventana de Resultados Post-Importación
Muestra registros completos vs incompletos y ofrece auditoría IA
"""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
from typing import Dict, List, Any, Callable, Optional


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
        super().__init__(parent)

        self.completos = completos
        self.incompletos = incompletos
        self.resumen = resumen
        self.callback_auditar = callback_auditar
        self.callback_continuar = callback_continuar

        self._configurar_ventana()
        self._crear_ui()

    def _configurar_ventana(self):
        """Configurar ventana"""
        self.title("EVARISIS CIRUGÍA ONCOLÓGICA - Resultados de Importación")

        # Usar tamaño más grande para mejor visualización
        self.geometry("950x700")
        self.resizable(True, True)

        # Modal
        self.transient(self.master)
        self.grab_set()

        # Centrar
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (950 // 2)
        y = (self.winfo_screenheight() // 2) - (700 // 2)
        self.geometry(f"950x700+{x}+{y}")

    def _crear_ui(self):
        """Crear interfaz"""
        # Frame principal
        main_frame = ttkb.Frame(self, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # Título
        ttkb.Label(
            main_frame,
            text="🎉 Importación Completada",
            font=("Segoe UI", 18, "bold"),
            bootstyle="success"
        ).pack(pady=(0, 20))

        # Resumen
        self._crear_seccion_resumen(main_frame)

        # Listas de registros (scrollable)
        self._crear_listas_registros(main_frame)

        # Botones de acción
        self._crear_botones_accion(main_frame)

    def _crear_seccion_resumen(self, parent):
        """Sección de resumen"""
        frame = ttkb.LabelFrame(parent, text="📊 Resumen", padding=15)
        frame.pack(fill=X, pady=(0, 20))

        resumen_text = f"Total: {self.resumen['total']} registros | "
        resumen_text += f"✅ Completos: {self.resumen['completos']} | "
        resumen_text += f"⚠️ Incompletos: {self.resumen['incompletos']}"

        ttkb.Label(
            frame,
            text=resumen_text,
            font=("Segoe UI", 11)
        ).pack()

    def _crear_listas_registros(self, parent):
        """Listas de registros completos e incompletos con mejor distribución"""
        # Frame scrollable con fondo gris claro
        canvas_frame = ttkb.Frame(parent)
        canvas_frame.pack(fill=BOTH, expand=YES, pady=(0, 20))

        canvas = tk.Canvas(canvas_frame, bg='#f0f0f0', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Bind mousewheel para scroll (solo en el canvas, no global)
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass  # Canvas ya fue destruido

        # Usar bind en lugar de bind_all para evitar eventos después de cerrar
        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        # Registros completos
        if self.completos:
            ttkb.Label(
                scrollable_frame,
                text=f"✅ REGISTROS COMPLETOS ({len(self.completos)})",
                font=("Segoe UI", 12, "bold"),
                bootstyle="success"
            ).pack(anchor=W, pady=(5, 10), padx=10)

            for reg in self.completos:
                frame_reg = ttkb.Frame(scrollable_frame, bootstyle="light")
                frame_reg.pack(fill=X, padx=15, pady=3)

                texto = f"📄 {reg['numero_peticion']} - {reg['paciente_nombre']} ({reg['porcentaje_completitud']}%)"
                ttkb.Label(
                    frame_reg,
                    text=texto,
                    font=("Segoe UI", 10)
                ).pack(anchor=W, padx=5, pady=3)

        # Registros incompletos
        if self.incompletos:
            ttkb.Label(
                scrollable_frame,
                text=f"\n⚠️ REGISTROS INCOMPLETOS ({len(self.incompletos)})",
                font=("Segoe UI", 12, "bold"),
                bootstyle="warning"
            ).pack(anchor=W, pady=(15, 10), padx=10)

            for reg in self.incompletos:
                # Frame para cada registro con borde
                frame_reg = ttkb.LabelFrame(
                    scrollable_frame,
                    text=f"📄 {reg['numero_peticion']} - {reg['paciente_nombre']}",
                    bootstyle="warning",
                    padding=10
                )
                frame_reg.pack(fill=X, padx=15, pady=5)

                # Porcentaje de completitud
                porc_text = f"Completitud: {reg['porcentaje_completitud']}%"
                ttkb.Label(
                    frame_reg,
                    text=porc_text,
                    font=("Segoe UI", 9, "bold"),
                    bootstyle="warning"
                ).pack(anchor=W)

                # Mostrar campos faltantes DETALLADOS
                campos_faltantes_detalle = reg.get('campos_faltantes_detalle', '')
                if campos_faltantes_detalle and campos_faltantes_detalle != 'Ninguno':
                    ttkb.Label(
                        frame_reg,
                        text="Faltantes:",
                        font=("Segoe UI", 9, "bold")
                    ).pack(anchor=W, pady=(5, 2))

                    # Mostrar cada línea de detalle
                    for linea in campos_faltantes_detalle.split('\n'):
                        if linea.strip():
                            ttkb.Label(
                                frame_reg,
                                text=f"  • {linea}",
                                font=("Segoe UI", 8),
                                foreground="#666666"
                            ).pack(anchor=W, padx=10)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _crear_botones_accion(self, parent):
        """Botones de acción"""
        frame = ttkb.Frame(parent)
        frame.pack(fill=X)

        # Pregunta
        ttkb.Label(
            frame,
            text="🤖 ¿Desea realizar auditoría con Inteligencia Artificial?",
            font=("Segoe UI", 11, "bold")
        ).pack(pady=(0, 15))

        # Botones
        btn_frame = ttkb.Frame(frame)
        btn_frame.pack()

        ttkb.Button(
            btn_frame,
            text="✅ Sí, auditar con IA",
            command=self._on_auditar,
            bootstyle="success",
            width=20
        ).pack(side=LEFT, padx=10)

        ttkb.Button(
            btn_frame,
            text="❌ No, continuar",
            command=self._on_continuar,
            bootstyle="secondary",
            width=20
        ).pack(side=LEFT, padx=10)

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
    Función helper para mostrar ventana

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
