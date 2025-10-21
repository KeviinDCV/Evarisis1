#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VENTANA EMERGENTE DE AUDITORÍA IA
=====================================

Ventana modal que muestra el progreso de auditoría con IA.
Se muestra automáticamente después del procesamiento normal.

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 5 de octubre de 2025
"""

import tkinter as tk
import logging
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *
import threading
from typing import Dict, Any, List, Optional, Callable


class VentanaAuditoriaIA(tk.Toplevel):
    """Ventana emergente para mostrar progreso de auditoría con IA"""

    def __init__(
        self,
        parent,
        casos_a_auditar: List[Dict[str, Any]],
        callback_completado: Optional[Callable] = None,
        modo: str = 'completa'  # NUEVO: 'parcial' o 'completa'
    ):
        """
        Inicializar ventana de auditoría

        Args:
            parent: Ventana padre
            casos_a_auditar: Lista de dict con 'numero_peticion', 'debug_map', 'datos_bd'
            callback_completado: Función a llamar cuando termine (recibe resultados)
            modo: 'parcial' (solo faltantes) o 'completa' (validación profunda)
        """
        super().__init__(parent)

        self.casos_a_auditar = casos_a_auditar
        self.callback_completado = callback_completado
        self.resultados = []
        self.caso_actual = 0
        self.auditoria_cancelada = False
        self.modo = modo  # NUEVO: Guardar modo de auditoría

        # Configurar ventana
        self.title("EVARISIS CIRUGÍA ONCOLÓGICA - Auditoría con IA")
        self.resizable(True, True)

        # Hacer modal
        self.transient(parent)
        self.grab_set()

        # Configurar UI primero
        self._crear_ui()

        # V2.1.7: Mejorar manejo de estado de ventana
        # Maximizar ventana DESPUÉS de crear UI
        self.update_idletasks()
        try:
            # Intentar maximizar (Windows)
            self.state('zoomed')
        except:
            # Fallback para otros sistemas
            self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # V2.1.7: Mantener ventana siempre visible y restaurable
        # Bind para detectar cuando se minimiza y forzar restauración
        self.bind("<Unmap>", self._on_minimizar)
        self.bind("<Map>", self._on_restaurar)

        # Evitar cierre con X
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar)

    def _on_minimizar(self, event=None):
        """Detecta cuando la ventana se minimiza"""
        # Si la ventana está en estado iconic (minimizada), restaurarla automáticamente
        # durante el procesamiento
        if self.state() == 'iconic' and self.resultados == []:
            logging.info(f"   ⚠️ Ventana minimizada durante procesamiento, restaurando...")
            self.after(500, self._forzar_restauracion)

    def _on_restaurar(self, event=None):
        """Detecta cuando la ventana se restaura"""
        pass  # No necesitamos hacer nada especial

    def _forzar_restauracion(self):
        """Fuerza la restauración de la ventana si está minimizada"""
        try:
            if self.state() == 'iconic':
                self.deiconify()  # Restaurar de minimizado
                self.state('zoomed')  # Volver a maximizar
                self.lift()  # Traer al frente
                self.focus_force()  # Forzar foco
                logging.info(f"   ✅ Ventana restaurada automáticamente")
        except Exception as e:
            logging.info(f"   ⚠️ No se pudo restaurar ventana: {e}")

    def _crear_ui(self):
        """Crea la interfaz de la ventana"""

        # Frame principal
        main_frame = ttkb.Frame(self, padding=30)
        main_frame.pack(fill=BOTH, expand=YES)

        # Logo/Icono (simulado con texto)
        logo_label = ttkb.Label(
            main_frame,
            text="🤖",
            font=("Segoe UI", 48)
        )
        logo_label.pack(pady=(0, 10))

        # Título
        titulo = ttkb.Label(
            main_frame,
            text="Realizando auditoría con EVARISIS Cirugía Oncológica",
            font=("Segoe UI", 16, "bold"),
            bootstyle="primary"
        )
        titulo.pack(pady=(0, 5))

        # Subtítulo (ajustado según modo)
        if self.modo == 'parcial':
            texto_modo = f"Auditoría PARCIAL: Completando campos faltantes en {len(self.casos_a_auditar)} caso(s)"
            estimado = len(self.casos_a_auditar) * 15  # 15 seg por caso en modo parcial
        else:
            texto_modo = f"Auditoría COMPLETA: Validación profunda de {len(self.casos_a_auditar)} caso(s)"
            estimado = len(self.casos_a_auditar) * 50  # 50 seg por caso en modo completa
        
        self.subtitulo = ttkb.Label(
            main_frame,
            text=texto_modo,
            font=("Segoe UI", 10),
            bootstyle="secondary"
        )
        self.subtitulo.pack(pady=(0, 5))
        
        # Tiempo estimado
        min_estimado = estimado // 60
        seg_estimado = estimado % 60
        tiempo_texto = f"Tiempo estimado: {min_estimado}m {seg_estimado}s" if min_estimado > 0 else f"Tiempo estimado: {seg_estimado}s"
        
        self.tiempo_label = ttkb.Label(
            main_frame,
            text=tiempo_texto,
            font=("Segoe UI", 9),
            bootstyle="info"
        )
        self.tiempo_label.pack(pady=(0, 20))

        # Frame de progreso
        progress_frame = ttkb.Frame(main_frame)
        progress_frame.pack(fill=X, pady=10)

        # Label de estado
        self.label_estado = ttkb.Label(
            progress_frame,
            text="Inicializando auditoría...",
            font=("Segoe UI", 10)
        )
        self.label_estado.pack(anchor=W, pady=(0, 5))

        # Barra de progreso
        self.progressbar = ttkb.Progressbar(
            progress_frame,
            mode='determinate',
            bootstyle="success-striped",
            length=640
        )
        self.progressbar.pack(fill=X)

        # Label de porcentaje
        self.label_porcentaje = ttkb.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        )
        self.label_porcentaje.pack(anchor=E, pady=(5, 0))

        # Separador
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=20)

        # Frame de estadísticas
        stats_frame = ttkb.Frame(main_frame)
        stats_frame.pack(fill=X)

        # Labels de estadísticas
        stats_left = ttkb.Frame(stats_frame)
        stats_left.pack(side=LEFT, fill=X, expand=YES)

        stats_right = ttkb.Frame(stats_frame)
        stats_right.pack(side=RIGHT, fill=X, expand=YES)

        # Casos procesados
        self.label_casos = ttkb.Label(
            stats_left,
            text=f"📋 Casos procesados: 0 / {len(self.casos_a_auditar)}",
            font=("Segoe UI", 9)
        )
        self.label_casos.pack(anchor=W)

        # V2.1.6: Caso actual en proceso
        self.label_caso_actual = ttkb.Label(
            stats_left,
            text="🔍 Caso actual: -",
            font=("Segoe UI", 9),
            bootstyle="info"
        )
        self.label_caso_actual.pack(anchor=W, pady=(5, 0))

        # Correcciones aplicadas
        self.label_correcciones = ttkb.Label(
            stats_right,
            text="🔧 Correcciones aplicadas: 0",
            font=("Segoe UI", 9)
        )
        self.label_correcciones.pack(anchor=E)

        # NUEVO: Frame de correcciones en tiempo real
        ttk.Separator(main_frame, orient=HORIZONTAL).pack(fill=X, pady=15)

        correcciones_label = ttkb.Label(
            main_frame,
            text="📝 Correcciones en Tiempo Real:",
            font=("Segoe UI", 10, "bold")
        )
        correcciones_label.pack(anchor=W, pady=(0, 5))

        # Frame scrollable para correcciones
        correcciones_frame = ttkb.Frame(main_frame)
        correcciones_frame.pack(fill=BOTH, expand=YES)

        # Scrollbar
        scrollbar = ttkb.Scrollbar(correcciones_frame, orient="vertical")
        scrollbar.pack(side=RIGHT, fill=Y)

        # Text widget para mostrar correcciones
        self.text_correcciones = tk.Text(
            correcciones_frame,
            height=8,
            width=80,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
            bg="#f5f5f5",
            fg="#333333",
            relief=tk.FLAT,
            padx=10,
            pady=10
        )
        self.text_correcciones.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.config(command=self.text_correcciones.yview)

        # V2.1.0: Configurar tags para estilos de texto
        self.text_correcciones.tag_configure("lote_header", font=("Consolas", 10, "bold"), foreground="#0066cc")
        self.text_correcciones.tag_configure("razon", foreground="#666666", font=("Consolas", 8, "italic"))

        # Deshabilitar edición
        self.text_correcciones.config(state=tk.DISABLED)

        # Botón cancelar (oculto inicialmente)
        self.btn_cancelar = ttkb.Button(
            main_frame,
            text="Cancelar",
            bootstyle="danger-outline",
            command=self._on_cancelar,
            width=15
        )
        # No lo mostramos por ahora para evitar interrupciones
        # self.btn_cancelar.pack(pady=(20, 0))

    def _on_cancelar(self):
        """Maneja el evento de cancelar auditoría"""
        if tk.messagebox.askyesno(
            "Cancelar Auditoría",
            "¿Está seguro que desea cancelar la auditoría?\n\n"
            "Los casos ya procesados se mantendrán, pero los pendientes no serán auditados."
        ):
            self.auditoria_cancelada = True
            self.label_estado.config(text="Cancelando auditoría...")

    def _on_cerrar(self):
        """Evita cerrar ventana con X durante auditoría, pero permite guardar reporte si hay resultados"""
        # Si ya hay resultados (auditoría terminada o parcial)
        if self.resultados:
            import tkinter.messagebox as messagebox
            respuesta = messagebox.askyesno(
                "Cerrar Auditoría",
                f"La auditoría ha procesado {len(self.resultados)} casos.\n\n"
                "¿Desea guardar el reporte antes de cerrar?",
                parent=self
            )

            if respuesta:
                # Guardar reporte antes de cerrar
                logging.info(f"   💾 Guardando reporte antes de cerrar ventana...")
                if self.callback_completado:
                    self.callback_completado(self.resultados)

                # Cerrar ventana
                self.grab_release()
                self.destroy()
            # Si no quiere guardar, no hacer nada (mantener ventana abierta)
        else:
            # Si no hay resultados, no permitir cerrar (auditoría en curso)
            pass  # No hacer nada, forzar espera

    def actualizar_progreso(self, mensaje: str, progreso: int):
        """
        Actualiza el progreso de la auditoría

        Args:
            mensaje: Mensaje de estado
            progreso: Porcentaje (0-100)
        """
        self.label_estado.config(text=mensaje)
        self.progressbar['value'] = progreso
        self.label_porcentaje.config(text=f"{progreso}%")
        self.update_idletasks()

    def actualizar_estadisticas(self, casos_procesados: int, correcciones_totales: int):
        """
        Actualiza las estadísticas mostradas

        Args:
            casos_procesados: Número de casos procesados
            correcciones_totales: Total de correcciones aplicadas
        """
        logging.info(f"      📊 Actualizando stats: {casos_procesados}/{len(self.casos_a_auditar)} casos, {correcciones_totales} correcciones")

        self.label_casos.config(
            text=f"📋 Casos procesados: {casos_procesados} / {len(self.casos_a_auditar)}"
        )
        self.label_correcciones.config(
            text=f"🔧 Correcciones aplicadas: {correcciones_totales}"
        )
        self.update_idletasks()
        self.update()  # Forzar redibujado inmediato

    def agregar_correccion_tiempo_real(self, numero_caso: str, campo: str, valor: str):
        """
        Agrega una corrección al log en tiempo real

        Args:
            numero_caso: Número de petición (ej: IHQ250019)
            campo: Nombre del campo corregido
            valor: Valor asignado
        """
        logging.info(f"      ✓ Agregando corrección: {numero_caso} - {campo} = {valor[:50]}")

        # Habilitar edición temporalmente
        self.text_correcciones.config(state=tk.NORMAL)

        # Formatear mensaje
        mensaje = f"✓ {numero_caso} - {campo} ← \"{valor}\"\n"

        # Agregar al final
        self.text_correcciones.insert(tk.END, mensaje)

        # Scroll automático al final
        self.text_correcciones.see(tk.END)

        # Deshabilitar edición
        self.text_correcciones.config(state=tk.DISABLED)

        # Forzar actualización visual
        self.update_idletasks()
        self.update()  # Forzar redibujado inmediato

    def _agregar_header_lote(self, lote_num: int, tiempo_str: str):
        """
        Agrega header de lote al log (V2.1.0)
        Formato: "LOTE X (tiempo: Y min Z seg)"

        Args:
            lote_num: Número del lote (1, 2, 3...)
            tiempo_str: Tiempo formateado (ej: "0 min 45 seg" o "procesando...")
        """
        logging.info(f"   📦 Header LOTE {lote_num} - {tiempo_str}")

        self.text_correcciones.config(state=tk.NORMAL)

        # Agregar separador visual
        if lote_num > 1:
            self.text_correcciones.insert(tk.END, "\n")

        # Header del lote con tag único para poder actualizarlo después
        header = f"LOTE {lote_num} (tiempo: {tiempo_str})\n"
        tag_name = f"lote_header_{lote_num}"

        # Guardar posición inicial del header para actualización posterior
        start_pos = self.text_correcciones.index(tk.END + "-1c linestart")
        self.text_correcciones.insert(tk.END, header, ("lote_header", tag_name))
        end_pos = self.text_correcciones.index(tk.END + "-1c lineend")

        # Guardar rango del header para poder actualizarlo
        if not hasattr(self, '_header_ranges'):
            self._header_ranges = {}
        self._header_ranges[lote_num] = (start_pos, end_pos, tag_name)

        self.text_correcciones.config(state=tk.DISABLED)
        self.text_correcciones.see(tk.END)
        self.update_idletasks()

    def _actualizar_tiempo_header_lote(self, lote_num: int, tiempo_str: str):
        """
        Actualiza el tiempo en el header de un lote ya mostrado (V2.1.5)

        Args:
            lote_num: Número del lote (1, 2, 3...)
            tiempo_str: Tiempo final formateado (ej: "2 min 15 seg")
        """
        logging.info(f"   🔄 Actualizando tiempo LOTE {lote_num} -> {tiempo_str}")

        if not hasattr(self, '_header_ranges') or lote_num not in self._header_ranges:
            logging.info(f"   ⚠️ No se encontró header para LOTE {lote_num}")
            return

        start_pos, end_pos, tag_name = self._header_ranges[lote_num]

        self.text_correcciones.config(state=tk.NORMAL)

        # Buscar el texto del header usando el tag
        ranges = self.text_correcciones.tag_ranges(tag_name)
        if ranges:
            start = ranges[0]
            end = ranges[1]

            # Reemplazar el texto completo del header
            nuevo_header = f"LOTE {lote_num} (tiempo: {tiempo_str})\n"
            self.text_correcciones.delete(start, end)
            self.text_correcciones.insert(start, nuevo_header, ("lote_header", tag_name))

            logging.info(f"   ✅ Header actualizado exitosamente")
        else:
            logging.info(f"   ⚠️ No se encontraron tags para el header")

        self.text_correcciones.config(state=tk.DISABLED)
        self.update_idletasks()

    def _agregar_correccion_lote(self, numero_caso: str, campo: str, valor: str, razon: str):
        """
        Agrega una corrección con razón en formato de lote (V2.1.0)
        Formato:
          ✓ IHQ250001 - Campo ← "Valor"
            Razón: Explicación

        Args:
            numero_caso: Número de petición (ej: IHQ250001)
            campo: Nombre del campo corregido
            valor: Valor asignado
            razon: Razón de la corrección
        """
        logging.info(f"      ✓ {numero_caso} - {campo}: {razon[:60]}")

        self.text_correcciones.config(state=tk.NORMAL)

        # Línea de corrección
        mensaje_correccion = f"  ✓ {numero_caso} - {campo} ← \"{valor}\"\n"
        self.text_correcciones.insert(tk.END, mensaje_correccion)

        # Línea de razón (si existe)
        if razon and razon.strip():
            mensaje_razon = f"    Razón: {razon}\n"
            self.text_correcciones.insert(tk.END, mensaje_razon, "razon")

        self.text_correcciones.config(state=tk.DISABLED)
        self.text_correcciones.see(tk.END)
        self.update_idletasks()

    def ejecutar_auditoria(self):
        """
        Ejecuta la auditoría en un thread separado
        """
        thread = threading.Thread(target=self._auditar_casos, daemon=True)
        thread.start()

    def _auditar_casos(self):
        """Lógica principal de auditoría (corre en thread)"""
        from core.auditoria_ia import AuditoriaIA

        # Inicializar auditor
        auditor = AuditoriaIA()

        if not auditor.llm_activo:
            # LLM no está activo
            self.after(0, lambda: self._mostrar_error_llm())
            return

        correcciones_totales = 0

        # NUEVO: Detectar si usar procesamiento por lotes
        usar_lotes = self.modo == 'parcial' and len(self.casos_a_auditar) > 1

        if usar_lotes:
            # Obtener tamaño de lote del primer caso (configurado en auditoria_parcial.py)
            batch_size = self.casos_a_auditar[0].get('batch_size', 3)
            
            # Dividir en lotes
            lotes = []
            for i in range(0, len(self.casos_a_auditar), batch_size):
                lote = self.casos_a_auditar[i:i + batch_size]
                lotes.append(lote)
            
            logging.info(f"\n📦 Procesamiento por LOTES activado")
            logging.info(f"   Total casos: {len(self.casos_a_auditar)}")
            logging.info(f"   Tamaño lote: {batch_size} casos")
            logging.info(f"   Total lotes: {len(lotes)}\n")
            
            # Procesar cada lote
            casos_procesados = 0

            # V2.1.0: Dict para trackear qué lotes ya mostraron header (FUERA del bucle)
            lote_iniciado = {}

            for idx_lote, lote in enumerate(lotes):
                if self.auditoria_cancelada:
                    break

                # Actualizar UI
                progreso_lote = int((idx_lote / len(lotes)) * 100)
                self.after(0, lambda p=progreso_lote: self.actualizar_progreso(
                    f"Procesando lote {idx_lote+1}/{len(lotes)} ({len(lote)} casos)...",
                    p
                ))

                logging.info(f"🔄 Procesando lote {idx_lote+1}/{len(lotes)}: {len(lote)} casos")

                # Procesar lote completo
                try:
                    logging.info(f"   📤 Enviando lote a IA...")

                    # Definir callback para actualizar UI en tiempo real
                    # V2.1.0: Soporta formato de LOTES con tiempo y razones
                    def actualizar_ui_tiempo_real(resultado):
                        """
                        Callback que se ejecuta después de cada caso procesado
                        V2.1.0: Muestra formato LOTE X (tiempo) con razones
                        """
                        logging.info(f"   🔔 UI callback recibido: {resultado.get('numero_peticion', 'N/A')}")

                        def _actualizar():
                            numero_peticion = resultado.get('numero_peticion', 'Desconocido')
                            casos_proc = resultado.get('casos_procesados', 0)
                            total = resultado.get('total_casos', 1)

                            logging.info(f"      🔄 Actualizando UI: {numero_peticion} - {casos_proc}/{total}")

                            # Actualizar estadísticas
                            nonlocal correcciones_totales, casos_procesados, lote_iniciado

                            if resultado.get('exito'):
                                num_corr = resultado.get('correcciones_aplicadas', 0)
                                correcciones_totales += num_corr
                                casos_procesados = casos_proc

                                # Actualizar estadísticas en UI
                                self.actualizar_estadisticas(casos_procesados, correcciones_totales)

                                # V2.1.6: Actualizar caso actual
                                self.label_caso_actual.config(text=f"🔍 Caso actual: {numero_peticion}")

                                # V2.1.0: Mostrar correcciones con formato de LOTE
                                detalles = resultado.get('detalles', [])

                                # V2.1.5: Detectar modo LOTE con nueva lógica
                                lote_num = resultado.get('lote')
                                tiempo_lote = resultado.get('tiempo_lote')  # En segundos (solo en último caso)
                                es_primer_caso = resultado.get('es_primer_caso_lote', False)

                                # DEBUG V2.1.6: Ver qué recibimos
                                logging.info(f"      [UI] Recibido: lote={lote_num}, primer={es_primer_caso}, tiempo={tiempo_lote}, lote_iniciado={lote_iniciado}")

                                if lote_num is not None:

                                    # Mostrar header solo en el PRIMER caso del lote
                                    if es_primer_caso and lote_num not in lote_iniciado:
                                        logging.info(f"      [UI] ✅ Creando header LOTE {lote_num}")
                                        lote_iniciado[lote_num] = "procesando"  # Marcar como en proceso
                                        # Agregar header SIN tiempo (todavía no terminó el lote)
                                        self._agregar_header_lote(lote_num, "procesando...")
                                    else:
                                        logging.info(f"      [UI] ⏭️  NO crear header (primer={es_primer_caso}, existe={lote_num in lote_iniciado})")

                                    # Actualizar header con tiempo FINAL solo en último caso
                                    if tiempo_lote is not None and lote_iniciado.get(lote_num) == "procesando":
                                        lote_iniciado[lote_num] = True  # Marcar como completado

                                        # Formatear tiempo
                                        minutos = int(tiempo_lote // 60)
                                        segundos = int(tiempo_lote % 60)
                                        tiempo_str = f"{minutos} min {segundos} seg"

                                        # ACTUALIZAR el header con tiempo final
                                        self._actualizar_tiempo_header_lote(lote_num, tiempo_str)

                                    # Mostrar correcciones con razón para este caso
                                    if detalles:
                                        for detalle in detalles:
                                            if detalle.get('aplicada'):
                                                campo = detalle.get('campo', 'Campo')
                                                valor = detalle.get('valor_nuevo', '')
                                                razon = detalle.get('razon', '')

                                                valor_display = str(valor)  # V2.1.6: Mostrar valor completo sin truncar
                                                if not valor_display or valor_display in ['nan', 'None', '']:
                                                    valor_display = "(vacío)"

                                                # Agregar corrección con razón
                                                self._agregar_correccion_lote(numero_peticion, campo, valor_display, razon)

                                else:
                                    # MODO INDIVIDUAL (sin info de lote): Formato original
                                    for detalle in detalles:
                                        if detalle.get('aplicada'):
                                            campo = detalle.get('campo', 'Campo')
                                            valor = detalle.get('valor_nuevo', '')

                                            valor_display = str(valor)[:80] + "..." if len(str(valor)) > 80 else str(valor)
                                            if not valor_display or valor_display in ['nan', 'None', '']:
                                                valor_display = "(vacío)"

                                            self.agregar_correccion_tiempo_real(numero_peticion, campo, valor_display)
                            else:
                                # Error
                                error = resultado.get('error', 'Error desconocido')
                                casos_procesados = casos_proc
                                self.actualizar_estadisticas(casos_procesados, correcciones_totales)
                                self.agregar_correccion_tiempo_real(numero_peticion, "ERROR", error)

                        self.after(0, _actualizar)

                    resultados_lote = auditor.auditar_casos_lote(
                        casos=lote,
                        progress_callback=lambda msg, prog: self.after(0, lambda m=msg, p=prog, il=idx_lote, tl=len(lotes):
                            self.actualizar_progreso(
                                f"[Lote {il+1}/{tl}] {m}",
                                int((il / tl) * 100 + (p / tl))
                            )
                        ),
                        ui_callback=actualizar_ui_tiempo_real,  # NUEVO: Callback para UI en tiempo real
                        lote_offset=idx_lote,  # V2.1.6: Pasar número de lote para headers correctos
                        total_casos_global=len(self.casos_a_auditar)  # V2.1.6: Total de casos en toda la auditoría
                    )
                    
                    logging.info(f"   ✅ Lote {idx_lote+1} procesado completamente")

                    # Guardar resultados para reporte final
                    for resultado in resultados_lote:
                        self.resultados.append(resultado)
                    
                except Exception as e:
                    logging.info(f"   ❌ Error crítico procesando lote {idx_lote+1}: {e}")
                    import traceback
                    traceback.print_exc()

                    # Agregar errores para todos los casos del lote
                    for caso in lote:
                        self.resultados.append({
                            "exito": False,
                            "error": f"Error crítico en lote: {str(e)}",
                            "numero_peticion": caso.get('numero_peticion', 'Desconocido')
                        })

                        # Mostrar error en UI para cada caso
                        def mostrar_error_critico(n=caso.get('numero_peticion', 'Desconocido'), err=str(e)):
                            self.agregar_correccion_tiempo_real(n, "ERROR CRÍTICO", err)
                        self.after(0, mostrar_error_critico)
            
            logging.info(f"\n✅ Procesamiento por lotes completado")
            logging.info(f"   Casos procesados: {casos_procesados}")
            logging.info(f"   Correcciones totales: {correcciones_totales}\n")
        
        else:
            # Procesamiento individual (modo completa o un solo caso)
            logging.info(f"\n🔍 Procesamiento INDIVIDUAL activado")
            logging.info(f"   Modo: {self.modo.upper()}")
            logging.info(f"   Total casos: {len(self.casos_a_auditar)}\n")
            
            for idx, caso in enumerate(self.casos_a_auditar):
                if self.auditoria_cancelada:
                    break

                numero_peticion = caso.get('numero_peticion')
                debug_map = caso.get('debug_map')
                datos_bd = caso.get('datos_bd')

                # Actualizar UI (desde thread principal)
                self.after(0, lambda i=idx: self.actualizar_estadisticas(i, correcciones_totales))

                # Callback de progreso
                def progress_callback(msg, prog):
                    # Convertir progreso del caso (0-100) a progreso total
                    progreso_caso = (idx / len(self.casos_a_auditar)) * 100
                    progreso_subcaso = (prog / 100) * (100 / len(self.casos_a_auditar))
                    progreso_total = int(progreso_caso + progreso_subcaso)

                    self.after(0, lambda: self.actualizar_progreso(
                        f"[{idx+1}/{len(self.casos_a_auditar)}] {msg}",
                        progreso_total
                    ))

                # Auditar caso
                campos_a_buscar = caso.get('campos_a_buscar', None)
                
                resultado = auditor.auditar_caso(
                    numero_peticion=numero_peticion,
                    debug_map=debug_map,
                    datos_bd=datos_bd,
                    progress_callback=progress_callback,
                    modo=self.modo,
                    campos_a_buscar=campos_a_buscar
                )

                self.resultados.append(resultado)

                if resultado.get('exito'):
                    correcciones_totales += resultado.get('correcciones_aplicadas', 0)

                    # Mostrar correcciones en tiempo real
                    cambios = resultado.get('cambios', {})
                    for campo, valor in cambios.items():
                        if valor and valor not in ['NO ENCONTRADO', 'nan', None, '']:
                            # V2.1.6: Mostrar valor completo sin truncar
                            valor_display = str(valor)
                            self.after(0, lambda n=numero_peticion, c=campo, v=valor_display:
                                       self.agregar_correccion_tiempo_real(n, c, v))

        # Auditoría completada
        self.after(0, lambda: self._finalizar_auditoria(correcciones_totales))

    def _mostrar_error_llm(self):
        """Muestra error si LLM no está activo"""
        from tkinter import messagebox

        self.label_estado.config(text="⚠️ LM Studio no está activo")
        self.progressbar['value'] = 0

        messagebox.showwarning(
            "Auditoría IA no disponible",
            "LM Studio no está activo o no hay modelo cargado.\n\n"
            "La auditoría con IA ha sido omitida.\n"
            "Los datos procesados se mantienen sin cambios.\n\n"
            "💡 Para habilitar auditoría IA:\n"
            "1. Inicia LM Studio\n"
            "2. Carga un modelo\n"
            "3. Inicia el servidor local (puerto 1234)",
            parent=self
        )

        # Cerrar ventana y continuar sin auditoría
        if self.callback_completado:
            self.callback_completado([])

        self.grab_release()
        self.destroy()

    def _finalizar_auditoria(self, correcciones_totales: int):
        """Finaliza la auditoría y muestra botón para ver resultados"""
        self.actualizar_progreso("✅ Auditoría completada", 100)
        self.actualizar_estadisticas(len(self.casos_a_auditar), correcciones_totales)

        # Preparar resumen
        casos_con_correcciones = sum(
            1 for r in self.resultados
            if r.get('exito') and r.get('correcciones_aplicadas', 0) > 0
        )

        casos_sin_errores = sum(
            1 for r in self.resultados
            if r.get('exito') and r.get('correcciones_aplicadas', 0) == 0
        )

        # Agregar resumen al área de correcciones
        self.text_correcciones.config(state=tk.NORMAL)
        self.text_correcciones.insert(tk.END, f"\n{'='*60}\n")
        self.text_correcciones.insert(tk.END, f"✅ AUDITORÍA COMPLETADA\n")
        self.text_correcciones.insert(tk.END, f"{'='*60}\n")
        self.text_correcciones.insert(tk.END, f"📊 Casos auditados: {len(self.resultados)}\n")
        self.text_correcciones.insert(tk.END, f"✓ Sin errores: {casos_sin_errores}\n")
        self.text_correcciones.insert(tk.END, f"🔧 Con correcciones: {casos_con_correcciones}\n")
        self.text_correcciones.insert(tk.END, f"📝 Total correcciones: {correcciones_totales}\n")
        self.text_correcciones.see(tk.END)
        self.text_correcciones.config(state=tk.DISABLED)

        # CRÍTICO: Generar reporte AUTOMÁTICAMENTE antes de mostrar botón
        # Esto garantiza que el reporte se guarde incluso si la ventana se cierra
        logging.info(f"\n💾 Guardando reporte automáticamente...")
        if self.callback_completado:
            try:
                # Llamar callback para generar el reporte
                self.callback_completado(self.resultados)
                logging.info(f"✅ Reporte guardado correctamente")
            except Exception as e:
                logging.info(f"❌ Error guardando reporte: {e}")
                import traceback
                traceback.print_exc()

        # Buscar el main_frame y agregar botón "Ver Resultados"
        for widget in self.winfo_children():
            if isinstance(widget, ttkb.Frame):
                self.btn_ver_resultados = ttkb.Button(
                    widget,
                    text="👁️ Ver Resultados Detallados",
                    command=self._ver_resultados,
                    bootstyle="success",
                    width=30
                )
                self.btn_ver_resultados.pack(pady=(15, 0))
                break

    def _ver_resultados(self):
        """Usuario hace clic en Ver Resultados - cerrar ventana y navegar"""
        # NOTA: El callback ya fue llamado en _finalizar_auditoria()
        # Solo necesitamos navegar a la sección de Análisis IA y cerrar la ventana

        logging.info(f"   👁️ Usuario solicitó ver resultados")

        # Cerrar ventana
        self.grab_release()
        self.destroy()

        # V2.1.6: Mostrar mensaje DESPUÉS de cerrar ventana
        from tkinter import messagebox
        from pathlib import Path
        # Intentar obtener la ruta del reporte del parent
        try:
            parent = self.master
            if hasattr(parent, '_ruta_ultimo_reporte'):
                ruta = parent._ruta_ultimo_reporte
                messagebox.showinfo(
                    "Auditoría Completada",
                    f"Auditoría completada exitosamente.\n\n"
                    f"Reporte generado: {Path(ruta).name}\n\n"
                    f"La sección 'Análisis IA' ha sido abierta automáticamente."
                )
        except Exception as e:
            logging.info(f"   ⚠️ No se pudo mostrar mensaje de completado: {e}")


def mostrar_ventana_auditoria(
    parent,
    casos_a_auditar: List[Dict[str, Any]] = None,
    callback_completado: Optional[Callable] = None,
    modo: str = 'completa',  # NUEVO: 'parcial' o 'completa'
    casos: List[Dict[str, Any]] = None  # NUEVO: Alias para casos_a_auditar
) -> VentanaAuditoriaIA:
    """
    Función helper para mostrar ventana de auditoría

    Args:
        parent: Ventana padre
        casos_a_auditar: Lista de casos a auditar (deprecado, usar 'casos')
        callback_completado: Callback al completar
        modo: 'parcial' (solo faltantes, rápido) o 'completa' (validación profunda)
        casos: Lista de casos a auditar (recomendado)

    Returns:
        Instancia de VentanaAuditoriaIA
    """
    # Soportar ambos nombres de parámetro para compatibilidad
    casos_finales = casos if casos is not None else casos_a_auditar
    
    if not casos_finales:
        casos_finales = []
    
    ventana = VentanaAuditoriaIA(
        parent, 
        casos_finales, 
        callback_completado,
        modo=modo  # NUEVO: Pasar modo
    )
    ventana.ejecutar_auditoria()

    return ventana


if __name__ == "__main__":
    # Test de la ventana
    root = ttkb.Window(themename="darkly")
    root.title("Test Ventana Auditoría")
    root.geometry("800x600")

    # Casos de prueba
    casos_test = [
        {
            'numero_peticion': 'IHQ250001',
            'debug_map': {'numero_peticion': 'IHQ250001', 'ocr': {'texto_consolidado': 'test'}, 'extraccion': {'unified_extractor': {}}},
            'datos_bd': {'N. peticion': 'IHQ250001'}
        }
    ]

    def on_completado(resultados):
        logging.info(f"✅ Auditoría completada: {len(resultados)} casos")
        root.quit()

    btn = ttkb.Button(
        root,
        text="Iniciar Auditoría de Prueba",
        command=lambda: mostrar_ventana_auditoria(root, casos_test, on_completado),
        bootstyle="success"
    )
    btn.pack(expand=YES)

    root.mainloop()
