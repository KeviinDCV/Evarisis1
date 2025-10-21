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
import logging


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
        from pathlib import Path
        import json

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
        """Crear interfaz maximizada con scroll único (V5.3.9.2)"""
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

        # V5.3.9.2: TODO EL CONTENIDO EN UN SOLO FRAME SCROLLABLE
        self._crear_contenido_scrollable(main_frame)

        # Botones fijos al final (no hacen scroll)
        self._crear_botones_accion(main_frame)

    def _crear_contenido_scrollable(self, parent):
        """V5.3.9.2: Crear todo el contenido en un frame scrollable único"""
        # Frame scrollable principal
        canvas_frame = ttkb.Frame(parent)
        canvas_frame.pack(fill=BOTH, expand=YES, pady=(10, 20))

        canvas = tk.Canvas(canvas_frame, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttkb.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttkb.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Sistema de scroll mejorado
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except tk.TclError:
                pass

        canvas.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)

        def _on_keypress(event):
            try:
                if not canvas.winfo_exists():
                    return
                if event.keysym == 'Up':
                    canvas.yview_scroll(-1, "units")
                elif event.keysym == 'Down':
                    canvas.yview_scroll(1, "units")
                elif event.keysym == 'Prior':
                    canvas.yview_scroll(-1, "pages")
                elif event.keysym == 'Next':
                    canvas.yview_scroll(1, "pages")
            except tk.TclError:
                pass

        canvas.bind("<Up>", _on_keypress)
        canvas.bind("<Down>", _on_keypress)
        canvas.bind("<Prior>", _on_keypress)
        canvas.bind("<Next>", _on_keypress)
        canvas.focus_set()

        # V5.3.9.2: Cargar correcciones y agrupar por caso
        correcciones = self._cargar_correcciones_desde_debug_maps()
        correcciones_por_caso = self._agrupar_correcciones_por_caso(correcciones)

        # 1. SECCIÓN: CORRECCIONES POR CASO (si existen)
        if correcciones_por_caso:
            self._mostrar_correcciones_por_caso(scrollable_frame, correcciones_por_caso)

        # 2. SECCIÓN: REGISTROS COMPLETOS
        if self.completos:
            self._mostrar_registros_completos(scrollable_frame)

        # 3. SECCIÓN: REGISTROS INCOMPLETOS
        if self.incompletos:
            self._mostrar_registros_incompletos(scrollable_frame)

        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)

    def _agrupar_correcciones_por_caso(self, correcciones: List[Dict]) -> Dict[str, List[Dict]]:
        """V5.3.9.2: Agrupar correcciones por número de caso"""
        por_caso = {}
        for corr in correcciones:
            numero_caso = corr.get('numero_caso', 'DESCONOCIDO')
            if numero_caso not in por_caso:
                por_caso[numero_caso] = []
            por_caso[numero_caso].append(corr)
        return por_caso

    def _mostrar_correcciones_por_caso(self, parent, correcciones_por_caso: Dict[str, List[Dict]]):
        """V5.3.9.2: Mostrar correcciones agrupadas por caso con estilo similar a incompletos"""
        # Título de sección
        ttkb.Label(
            parent,
            text=f"🔧 CORRECCIONES AUTOMÁTICAS APLICADAS ({len(correcciones_por_caso)} casos)",
            font=("Segoe UI", 14, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=(10, 10), padx=20)

        # Descripción
        ttkb.Label(
            parent,
            text="✨ El sistema detectó y corrigió automáticamente las siguientes inconsistencias en cada caso:",
            font=("Segoe UI", 10, "italic"),
            foreground="#155724"
        ).pack(anchor=W, pady=(0, 15), padx=20)

        # Mostrar cada caso con sus correcciones
        for numero_caso, correcciones in correcciones_por_caso.items():
            # Frame para cada caso (estilo similar a incompletos)
            caso_frame = ttkb.LabelFrame(
                parent,
                text=f"📄 {numero_caso}",
                bootstyle="success",
                padding=15
            )
            caso_frame.pack(fill=X, padx=20, pady=8)

            # Contador de correcciones
            total_corr = len(correcciones)
            ttkb.Label(
                caso_frame,
                text=f"Correcciones aplicadas: {total_corr}",
                font=("Segoe UI", 10, "bold"),
                bootstyle="success"
            ).pack(anchor=W, pady=(0, 10))

            # Agrupar por tipo para organizar
            por_tipo = {
                "ortografica": [],
                "medico_servicio": [],
                "normalizacion_biomarcador": []
            }
            for corr in correcciones:
                tipo = corr.get("tipo", "ortografica")
                if tipo in por_tipo:
                    por_tipo[tipo].append(corr)

            # Mostrar cada tipo de corrección
            if por_tipo["ortografica"]:
                ttkb.Label(
                    caso_frame,
                    text=f"📝 Correcciones Ortográficas ({len(por_tipo['ortografica'])})",
                    font=("Segoe UI", 9, "bold"),
                    foreground="#17a2b8"
                ).pack(anchor=W, pady=(5, 3), padx=10)

                for corr in por_tipo["ortografica"]:
                    self._mostrar_detalle_correccion(caso_frame, corr)

            if por_tipo["medico_servicio"]:
                ttkb.Label(
                    caso_frame,
                    text=f"🩺 Validación Médico-Servicio ({len(por_tipo['medico_servicio'])})",
                    font=("Segoe UI", 9, "bold"),
                    foreground="#28a745"
                ).pack(anchor=W, pady=(10, 3), padx=10)

                for corr in por_tipo["medico_servicio"]:
                    self._mostrar_detalle_correccion(caso_frame, corr)

            if por_tipo["normalizacion_biomarcador"]:
                ttkb.Label(
                    caso_frame,
                    text=f"🧬 Normalización Biomarcadores ({len(por_tipo['normalizacion_biomarcador'])})",
                    font=("Segoe UI", 9, "bold"),
                    foreground="#6f42c1"
                ).pack(anchor=W, pady=(10, 3), padx=10)

                for corr in por_tipo["normalizacion_biomarcador"]:
                    self._mostrar_detalle_correccion(caso_frame, corr)

    def _mostrar_detalle_correccion(self, parent, correccion: Dict):
        """V5.3.9.2: Mostrar detalle de una corrección individual"""
        campo = correccion.get('campo', 'N/A')
        antes = correccion.get('valor_original', '')
        despues = correccion.get('valor_corregido', '')
        razon = correccion.get('razon', '')

        # Truncar valores muy largos
        antes_display = (antes[:60] + '...') if len(antes) > 60 else antes
        despues_display = (despues[:60] + '...') if len(despues) > 60 else despues

        # Frame para cada corrección individual
        corr_frame = ttkb.Frame(parent)
        corr_frame.pack(fill=X, padx=20, pady=2)

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

    def _mostrar_registros_completos(self, parent):
        """V5.3.9.2: Mostrar registros completos en el área scrollable"""
        ttkb.Label(
            parent,
            text=f"✅ REGISTROS COMPLETOS ({len(self.completos)})",
            font=("Segoe UI", 14, "bold"),
            bootstyle="success"
        ).pack(anchor=W, pady=(20, 10), padx=20)

        for reg in self.completos:
            frame_reg = ttkb.Frame(parent, bootstyle="light")
            frame_reg.pack(fill=X, padx=25, pady=3)

            texto = f"📄 {reg['numero_peticion']} - {reg['paciente_nombre']} ({reg['porcentaje_completitud']}%)"
            ttkb.Label(
                frame_reg,
                text=texto,
                font=("Segoe UI", 10)
            ).pack(anchor=W, padx=5, pady=3)

    def _mostrar_registros_incompletos(self, parent):
        """V5.3.9.2: Mostrar registros incompletos en el área scrollable"""
        ttkb.Label(
            parent,
            text=f"⚠️ REGISTROS INCOMPLETOS ({len(self.incompletos)})",
            font=("Segoe UI", 14, "bold"),
            bootstyle="warning"
        ).pack(anchor=W, pady=(20, 10), padx=20)

        for reg in self.incompletos:
            # Frame para cada registro con borde
            frame_reg = ttkb.LabelFrame(
                parent,
                text=f"📄 {reg['numero_peticion']} - {reg['paciente_nombre']}",
                bootstyle="warning",
                padding=15
            )
            frame_reg.pack(fill=X, padx=25, pady=8)

            # Porcentaje de completitud
            porc_text = f"Completitud: {reg['porcentaje_completitud']}%"
            ttkb.Label(
                frame_reg,
                text=porc_text,
                font=("Segoe UI", 10, "bold"),
                bootstyle="warning"
            ).pack(anchor=W)

            # Mostrar campos faltantes DETALLADOS
            campos_faltantes_detalle = reg.get('campos_faltantes_detalle', '')
            if campos_faltantes_detalle and campos_faltantes_detalle != 'Ninguno':
                ttkb.Label(
                    frame_reg,
                    text="Faltantes:",
                    font=("Segoe UI", 9, "bold")
                ).pack(anchor=W, pady=(8, 3))

                # Mostrar cada línea de detalle
                for linea in campos_faltantes_detalle.split('\n'):
                    if linea.strip():
                        ttkb.Label(
                            frame_reg,
                            text=f"  • {linea}",
                            font=("Segoe UI", 9),
                            foreground="#666666"
                        ).pack(anchor=W, padx=10)

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
    Función helper para mostrar ventana

    V5.3.9: Las correcciones ya NO se pasan como parámetro.
    La ventana las carga automáticamente desde los archivos debug_map.

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
