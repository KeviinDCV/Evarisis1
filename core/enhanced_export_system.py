#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de exportación mejorado para el Gestor de Oncología HUV
Incluye exportación completa, selecciones, y gestión de archivos
"""

import os
import shutil
import tkinter as tk
import ttkbootstrap as ttk
from tkinter import messagebox, filedialog
import pandas as pd
import sqlite3
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedExportSystem:
    """Sistema de exportación robusto y completo"""

    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.export_base_path = os.path.join(
            os.path.expanduser("~"),
            "Documents",
            "EVARISIS Cirug\u00eda Oncol\u00f3gica",
            "Exportaciones Base de datos"
        )
        self.ensure_export_directories()

    def ensure_export_directories(self):
        """Crear directorios de exportación si no existen"""
        try:
            excel_path = os.path.join(self.export_base_path, "Excel")
            db_path = os.path.join(self.export_base_path, "Base de datos")

            os.makedirs(excel_path, exist_ok=True)
            os.makedirs(db_path, exist_ok=True)

        except Exception as e:
            logging.error(f"Error creando directorios de exportación: {e}")

    def export_full_database(self):
        """Exportar toda la base de datos directamente sin mostrar diálogo de formato"""
        try:
            # Cargar datos
            from core.database_manager import get_all_records_as_dataframe
            df = get_all_records_as_dataframe()

            if df is None or df.empty:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            logging.debug(f"DEBUG: Exportando directamente {len(df)} registros completos sin diálogo")

            # CORREGIDO: Mostrar diálogo de selección de formato para base de datos completa
            # La función 'Exportar Todo' debe mostrar opciones pero guardar en ubicaciones predefinidas
            self.show_export_format_dialog(df, "completa")

        except Exception as e:
            logging.error(f"Error en export_full_database: {e}")
            messagebox.showerror("Error", f"Error exportando base de datos: {e}")

    def export_full_database_direct(self):
        """Exportar toda la base de datos directamente con ambos formatos sin diálogo"""
        try:
            # Cargar datos
            from core.database_manager import get_all_records_as_dataframe
            df = get_all_records_as_dataframe()

            if df is None or df.empty:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            logging.debug(f"DEBUG: Exportando directamente {len(df)} registros a Excel y Base de Datos")

            # Mostrar diálogo simple de selección de formato sin opción de ubicación
            self.show_quick_export_dialog(df, "completa")

        except Exception as e:
            logging.error(f"Error en export_full_database_direct: {e}")
            messagebox.showerror("Error", f"Error exportando base de datos: {e}")

    def export_selected_data(self, selected_df):
        """Exportar solo los elementos seleccionados directamente a Excel en ubicación estándar"""
        try:
            if selected_df is None or selected_df.empty:
                messagebox.showwarning("Sin selección", "No hay elementos seleccionados para exportar")
                return

            logging.debug(f"DEBUG: Exportando directamente {len(selected_df)} registros seleccionados a Excel")

            # CORREGIDO: Exportar directamente a Excel en ubicación estándar sin mostrar diálogo
            self.execute_export(selected_df, "seleccion", "excel", None)

        except Exception as e:
            logging.error(f"Error en export_selected_data: {e}")
            messagebox.showerror("Error", f"Error exportando selección: {e}")

    def show_export_format_dialog(self, df, export_type):
        """Mostrar diálogo para seleccionar formato de exportación"""
        dialog = tk.Toplevel(self.parent_app)
        dialog.title("Formato de Exportación")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self.parent_app)
        dialog.grab_set()

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Contenido del diálogo
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        ttk.Label(
            main_frame,
            text=f"Exportar {export_type.title()}",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 20))

        # Información
        info_text = f"Se exportarán {len(df)} registros\n¿En qué formato desea exportar?"
        ttk.Label(
            main_frame,
            text=info_text,
            font=("Segoe UI", 11),
            justify="center"
        ).pack(pady=(0, 20))

        # Botones de formato
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(expand=True, fill='x')

        ttk.Button(
            buttons_frame,
            text="📊 Exportar a Excel",
            command=lambda: self.execute_export(df, export_type, "excel", dialog),
            bootstyle="success",
            width=25
        ).pack(pady=5, fill='x')

        ttk.Button(
            buttons_frame,
            text="🗄️ Exportar Base de Datos",
            command=lambda: self.execute_export(df, export_type, "database", dialog),
            bootstyle="info",
            width=25
        ).pack(pady=5, fill='x')

        # Botón Cancelar quitado - puede cerrar con X de la ventana

    def show_quick_export_dialog(self, df, export_type):
        """Mostrar diálogo rápido para exportar sin elegir ubicación (para Exportar Todo)"""
        dialog = tk.Toplevel(self.parent_app)
        dialog.title("Exportar Todo - Formato")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.transient(self.parent_app)
        dialog.grab_set()

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Contenido del diálogo
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        ttk.Label(
            main_frame,
            text="Exportar Base de Datos Completa",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))

        # Información
        info_text = f"Se exportarán {len(df)} registros\na la carpeta de Documentos."
        ttk.Label(
            main_frame,
            text=info_text,
            font=("Segoe UI", 11),
            justify="center"
        ).pack(pady=(0, 15))

        # Botones de formato
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(expand=True, fill='x')

        ttk.Button(
            buttons_frame,
            text="📊 Excel",
            command=lambda: self.execute_export(df, export_type, "excel", dialog),
            bootstyle="success",
            width=15
        ).pack(side='left', padx=(0, 5), fill='x', expand=True)

        ttk.Button(
            buttons_frame,
            text="🗄️ Base de Datos",
            command=lambda: self.execute_export(df, export_type, "database", dialog),
            bootstyle="info",
            width=15
        ).pack(side='right', padx=(5, 0), fill='x', expand=True)

    def show_selection_export_dialog(self, selected_df):
        """Mostrar diálogo completo para exportar selección con opción de ubicación"""
        dialog = tk.Toplevel(self.parent_app)
        dialog.title("Exportar Selección")
        dialog.geometry("450x300")
        dialog.resizable(False, False)
        dialog.transient(self.parent_app)
        dialog.grab_set()

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Contenido del diálogo
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(expand=True, fill='both')

        # Título
        ttk.Label(
            main_frame,
            text="Exportar Elementos Seleccionados",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=(0, 15))

        # Información
        info_text = f"Se exportarán {len(selected_df)} registros seleccionados.\n¿Dónde desea guardar el archivo?"
        ttk.Label(
            main_frame,
            text=info_text,
            font=("Segoe UI", 11),
            justify="center"
        ).pack(pady=(0, 20))

        # Opciones de ubicación
        location_frame = ttk.LabelFrame(main_frame, text="Ubicación", padding=10)
        location_frame.pack(fill='x', pady=(0, 15))

        self.location_var = tk.StringVar(value="documentos")

        ttk.Radiobutton(
            location_frame,
            text="📁 Guardar en Documentos (ubicación estándar)",
            variable=self.location_var,
            value="documentos"
        ).pack(anchor='w', pady=2)

        ttk.Radiobutton(
            location_frame,
            text="🎯 Elegir ubicación específica",
            variable=self.location_var,
            value="personalizada"
        ).pack(anchor='w', pady=2)

        # Botones de formato
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x')

        ttk.Button(
            buttons_frame,
            text="📊 Exportar a Excel",
            command=lambda: self.execute_selection_export(selected_df, "excel", dialog),
            bootstyle="success",
            width=20
        ).pack(side='left', padx=(0, 5), fill='x', expand=True)

        ttk.Button(
            buttons_frame,
            text="🗄️ Exportar Base de Datos",
            command=lambda: self.execute_selection_export(selected_df, "database", dialog),
            bootstyle="info",
            width=20
        ).pack(side='right', padx=(5, 0), fill='x', expand=True)

    def execute_export(self, df, export_type, format_type, dialog):
        """Ejecutar la exportación en el formato seleccionado"""
        try:
            # CORREGIDO: Solo destruir diálogo si existe
            if dialog is not None:
                dialog.destroy()

            # CORREGIDO: Usar la misma ruta configurada en __init__
            export_dir = self.export_base_path
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)

            # MEJORADO: Generar nombre de archivo más legible con fecha y hora
            from datetime import datetime
            now = datetime.now()
            fecha = now.strftime("%Y-%m-%d")  # Formato: 2025-10-04
            hora = now.strftime("%H%M")       # Formato: 2030
            
            if export_type == "completa":
                base_name = f"{fecha}_{hora}_BD_Completa_HUV"
            else:
                num_registros = len(df)
                base_name = f"{fecha}_{hora}_Seleccion_{num_registros}_registros"

            if format_type == "excel":
                filename = f"{base_name}.xlsx"
                # CORREGIDO: Guardar en subcarpeta Excel para que aparezca en el dashboard
                excel_dir = os.path.join(export_dir, "Excel")
                os.makedirs(excel_dir, exist_ok=True)
                filepath = os.path.join(excel_dir, filename)
                success = self.export_to_excel(df, filepath)
            else:  # database
                filename = f"{base_name}.db"
                # CORREGIDO: Guardar en subcarpeta Base de datos para que aparezca en el dashboard
                db_dir = os.path.join(export_dir, "Base de datos")
                os.makedirs(db_dir, exist_ok=True)
                filepath = os.path.join(db_dir, filename)
                success = self.export_to_database(df, filepath)

            if success:
                logging.info(f"✅ Exportación exitosa: {filepath}")

                # CORREGIDO: Mostrar confirmación con información correcta
                messagebox.showinfo(
                    "Exportación Completa",
                    f"✅ Datos exportados exitosamente!\n\n"
                    f"📁 Archivo: {filename}\n"
                    f"📂 Ubicación: {export_dir}\n"
                    f"📊 Registros: {len(df)}\n"
                    f"📋 Formato: {format_type.upper()}\n\n"
                    f"Puedes revisar el archivo en la pestaña de Exportaciones."
                )

                # CORREGIDO: NO abrir carpeta automáticamente, solo redirigir a pestaña Exportaciones
                # import subprocess
                # import platform
                # if platform.system() == "Windows":
                #     subprocess.run(f'explorer "{export_dir}"', shell=True)
                # elif platform.system() == "Darwin":  # macOS
                #     subprocess.run(["open", export_dir])
                # else:  # Linux
                #     subprocess.run(["xdg-open", export_dir])

                # CORREGIDO: Actualizar dashboard y redirigir a pestaña Exportaciones
                if hasattr(self.parent_app, 'enhanced_dashboard'):
                    try:
                        # Primero navegar al dashboard de base de datos
                        self.parent_app._nav_to_database()
                        logging.info("✅ Navegado a dashboard de base de datos")

                        # Esperar un momento para que se cargue el dashboard
                        self.parent_app.after(200, lambda: self._delayed_redirect_to_exports())
                    except Exception as e:
                        logging.warning(f"⚠️ No se pudo cambiar a pestaña Exportaciones: {e}")

        except Exception as e:
            logging.error(f"❌ Error durante exportación: {e}")
            messagebox.showerror("Error", f"Error durante la exportación: {e}")

    def _delayed_redirect_to_exports(self):
        """Redirigir a la pestaña de exportaciones después de un delay"""
        try:
            if hasattr(self.parent_app, 'enhanced_dashboard') and hasattr(self.parent_app.enhanced_dashboard, 'notebook'):
                self.parent_app.enhanced_dashboard.refresh_exports_list()
                # Cambiar automáticamente a la pestaña de Exportaciones (índice 5)
                self.parent_app.enhanced_dashboard.notebook.select(5)
                logging.info("✅ Redirigido a pestaña de Exportaciones")
        except Exception as e:
            logging.warning(f"⚠️ Error en redirección diferida: {e}")

    def generate_filename(self, df, export_type, format_type):
        """Generar nombre de archivo con fechas"""
        try:
            # Buscar columnas de fecha
            fecha_cols = [col for col in df.columns if 'fecha' in col.lower() and 'informe' in col.lower()]

            if fecha_cols:
                fecha_col = fecha_cols[0]
                fechas_validas = pd.to_datetime(df[fecha_col], errors='coerce', format='%d/%m/%Y').dropna()

                if not fechas_validas.empty:
                    fecha_min = fechas_validas.min().strftime('%d.%m.%Y')
                    fecha_max = fechas_validas.max().strftime('%d.%m.%Y')
                    fecha_range = f"{fecha_min} al {fecha_max}"
                else:
                    fecha_range = datetime.now().strftime('%d.%m.%Y')
            else:
                fecha_range = datetime.now().strftime('%d.%m.%Y')

            # Determinar tipo y extensión
            if export_type == "completa":
                tipo_desc = "Base de datos completa"
            else:
                tipo_desc = f"Seleccion {len(df)} registros"

            extension = ".xlsx" if format_type == "excel" else ".db"

            # Generar nombre
            filename = f"Exportacion {tipo_desc} {fecha_range}{extension}"

            # Limpiar caracteres no válidos
            invalid_chars = '<>:"/\\|?*'
            for char in invalid_chars:
                filename = filename.replace(char, '_')

            return filename

        except Exception as e:
            # Fallback a nombre simple
            timestamp = datetime.now().strftime('%d.%m.%Y_%H.%M')
            extension = ".xlsx" if format_type == "excel" else ".db"
            return f"Exportacion_{export_type}_{timestamp}{extension}"

    def toggle_floating_details_panel(self):
        """Mostrar/ocultar panel flotante lateral animado de detalles del registro seleccionado"""
        try:
            # Si el panel ya existe, cerrarlo con animación
            if hasattr(self, 'details_panel') and self.details_panel.winfo_exists():
                self.close_details_panel()
                return

            # Verificar si hay selección
            if not hasattr(self.parent_app, 'tree'):
                messagebox.showwarning("No disponible", "El visor de datos no está inicializado")
                return

            selected = self.parent_app.tree.selection()
            if not selected:
                messagebox.showinfo("Sin selección", "Por favor seleccione un registro para ver los detalles")
                return

            # Obtener el registro seleccionado
            item_id = selected[0]
            try:
                row_data = self.parent_app.master_df.loc[int(item_id)]

                # Crear panel lateral flotante
                self.details_panel = tk.Frame(
                    self.parent_app,
                    bg="#ffffff",
                    relief="raised",
                    borderwidth=2
                )

                # Obtener dimensiones de la ventana principal
                screen_width = self.parent_app.winfo_width()
                screen_height = self.parent_app.winfo_height()
                panel_width = 500

                # Posicionar el panel fuera de la pantalla (derecha)
                self.details_panel.place(
                    x=screen_width,
                    y=0,
                    width=panel_width,
                    height=screen_height
                )

                # Header del panel
                header_frame = ttk.Frame(self.details_panel, padding=15)
                header_frame.pack(fill="x")

                ttk.Label(
                    header_frame,
                    text="📋 Detalles del Registro",
                    font=("Segoe UI", 14, "bold")
                ).pack(side="left")

                ttk.Button(
                    header_frame,
                    text="✕",
                    command=self.close_details_panel,
                    bootstyle="danger",
                    width=3
                ).pack(side="right")

                ttk.Separator(self.details_panel, orient="horizontal").pack(fill="x")

                # Frame con scroll para el contenido
                canvas = tk.Canvas(self.details_panel, bg="#ffffff", highlightthickness=0)
                scrollbar = ttk.Scrollbar(self.details_panel, orient="vertical", command=canvas.yview)
                scrollable_frame = ttk.Frame(canvas)

                scrollable_frame.bind(
                    "<Configure>",
                    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
                )

                canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                canvas.configure(yscrollcommand=scrollbar.set)

                # Mostrar todos los campos
                for i, (key, value) in enumerate(row_data.items()):
                    field_frame = ttk.Frame(scrollable_frame, padding=15)
                    field_frame.pack(fill="x", padx=10, pady=5)

                    ttk.Label(
                        field_frame,
                        text=f"{key}:",
                        font=("Segoe UI", 9, "bold"),
                        foreground="#2c3e50"
                    ).pack(anchor="w")

                    value_text = str(value) if pd.notna(value) else "(vacío)"
                    ttk.Label(
                        field_frame,
                        text=value_text,
                        font=("Segoe UI", 9),
                        wraplength=450,
                        foreground="#34495e"
                    ).pack(anchor="w", padx=10, pady=(5, 0))

                    if i < len(row_data) - 1:
                        ttk.Separator(scrollable_frame, orient="horizontal").pack(fill="x", padx=20, pady=10)

                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")

                # Habilitar scroll con rueda del ratón solo cuando el cursor está sobre el panel
                def _on_mousewheel(event):
                    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                    return "break"

                def _bind_mousewheel(event):
                    canvas.bind("<MouseWheel>", _on_mousewheel)

                def _unbind_mousewheel(event):
                    canvas.unbind("<MouseWheel>")

                # Activar/desactivar scroll según posición del cursor
                self.details_panel.bind("<Enter>", _bind_mousewheel)
                self.details_panel.bind("<Leave>", _unbind_mousewheel)
                canvas.bind("<Enter>", _bind_mousewheel)
                canvas.bind("<Leave>", _unbind_mousewheel)

                # Animar entrada del panel (deslizar desde la derecha)
                self.animate_panel_in(screen_width, screen_width - panel_width, panel_width)

            except Exception as e:
                messagebox.showerror("Error", f"Error al obtener detalles del registro:\n{str(e)}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar panel de detalles:\n{str(e)}")

    def animate_panel_in(self, start_x, end_x, panel_width, step=0):
        """Animar el panel deslizándose desde la derecha"""
        if not hasattr(self, 'details_panel') or not self.details_panel.winfo_exists():
            return

        # Calcular progreso (20 pasos de animación)
        total_steps = 20
        if step <= total_steps:
            # Ease-out cubic para animación suave
            progress = 1 - pow(1 - (step / total_steps), 3)
            current_x = start_x - int((start_x - end_x) * progress)

            self.details_panel.place(x=current_x)
            self.parent_app.after(10, lambda: self.animate_panel_in(start_x, end_x, panel_width, step + 1))

    def close_details_panel(self):
        """Cerrar el panel con animación de deslizamiento hacia la derecha"""
        if not hasattr(self, 'details_panel') or not self.details_panel.winfo_exists():
            return

        screen_width = self.parent_app.winfo_width()
        current_x = self.details_panel.winfo_x()

        self.animate_panel_out(current_x, screen_width)

    def animate_panel_out(self, start_x, end_x, step=0):
        """Animar el panel deslizándose hacia la derecha"""
        if not hasattr(self, 'details_panel') or not self.details_panel.winfo_exists():
            return

        # Calcular progreso (20 pasos de animación)
        total_steps = 20
        if step <= total_steps:
            # Ease-in cubic para animación suave
            progress = pow(step / total_steps, 3)
            current_x = start_x + int((end_x - start_x) * progress)

            self.details_panel.place(x=current_x)

            if step < total_steps:
                self.parent_app.after(10, lambda: self.animate_panel_out(start_x, end_x, step + 1))
            else:
                # Destruir el panel al finalizar la animación
                self.details_panel.destroy()

    def toggle_advanced_filters_panel(self):
        """Mostrar/ocultar panel de filtros avanzados"""
        try:
            messagebox.showinfo(
                "Filtros Avanzados",
                "Los filtros avanzados se implementarán en una versión futura.\n\n"
                "Por ahora, puede usar el campo de búsqueda en el visualizador de datos."
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar filtros:\n{str(e)}")

    def export_to_excel(self, df, filepath):
        """Exportar DataFrame a Excel"""
        try:
            # CORREGIDO: Usar la ruta completa que se pasa como parámetro
            logging.debug(f"DEBUG: Exportando a Excel: {filepath}")

            # Crear directorio padre si no existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Exportar con formato mejorado
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Datos', index=False)

                # Obtener el workbook y worksheet para formato
                workbook = writer.book
                worksheet = writer.sheets['Datos']

                # Ajustar ancho de columnas
                for column in worksheet.columns:
                    max_length = 0
                    column = [cell for cell in column]
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column[0].column_letter].width = adjusted_width

            logging.info(f"✅ Excel exportado exitosamente: {filepath}")
            return True

        except Exception as e:
            logging.error(f"❌ Error exportando a Excel: {e}")
            return False

    def export_to_database(self, df, filepath):
        """Exportar DataFrame a base de datos SQLite"""
        try:
            # CORREGIDO: Usar filepath completo que ya incluye la subcarpeta correcta
            logging.debug(f"DEBUG: Exportando a base de datos: {filepath}")

            # Crear directorio padre si no existe
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Crear copia de la base de datos original
            original_db_path = os.path.join("data", "huv_oncologia.db")

            if os.path.exists(original_db_path):
                # Copiar base de datos completa
                shutil.copy2(original_db_path, filepath)

                # Si es exportación de selección, filtrar la base de datos
                filename = os.path.basename(filepath)
                if "Seleccion" in filename:
                    conn = sqlite3.connect(filepath)

                    # Obtener números de petición de la selección
                    peticiones = df['numero_peticion'].tolist()
                    placeholders = ','.join(['?'] * len(peticiones))

                    # Eliminar registros que no están en la selección
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM informes_ihq WHERE numero_peticion NOT IN ({placeholders})", peticiones)

                    conn.commit()
                    conn.close()
            else:
                # Crear nueva base de datos con los datos del DataFrame
                conn = sqlite3.connect(filepath)
                df.to_sql('informes_ihq', conn, if_exists='replace', index=False)
                conn.close()

            logging.info(f"✅ Base de datos exportada exitosamente: {filepath}")
            return True

        except Exception as e:
            logging.error(f"Error exportando base de datos: {e}")
            return False

# Métodos adicionales para integrar con la UI principal

def create_floating_details_panel(parent_app):
    """Crear panel flotante de detalles"""
    if hasattr(parent_app, 'details_window') and parent_app.details_window:
        parent_app.details_window.lift()
        return

    # Crear ventana flotante
    details_window = tk.Toplevel(parent_app)
    details_window.title("Detalles del Registro")
    details_window.geometry("600x800")
    details_window.transient(parent_app)

    # Frame principal
    main_frame = ttk.Frame(details_window, padding=20)
    main_frame.pack(expand=True, fill='both')

    # Título
    title_label = ttk.Label(
        main_frame,
        text="Detalles del Registro",
        font=("Segoe UI", 16, "bold")
    )
    title_label.pack(pady=(0, 10))

    # Área de texto para detalles
    text_area = tk.Text(
        main_frame,
        state="disabled",
        wrap="word",
        font=("Calibri", 12),
        relief="flat",
        padx=15,
        pady=15
    )
    text_area.pack(expand=True, fill='both')

    # Scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=text_area.yview)
    scrollbar.pack(side='right', fill='y')
    text_area.configure(yscrollcommand=scrollbar.set)

    # Guardar referencias
    parent_app.details_window = details_window
    parent_app.details_text_area = text_area
    parent_app.details_title_label = title_label

    # Manejar cierre
    def on_close():
        parent_app.details_window = None
        details_window.destroy()

    details_window.protocol("WM_DELETE_WINDOW", on_close)

def create_advanced_filters_panel(parent_app):
    """Crear panel flotante de filtros avanzados"""
    if hasattr(parent_app, 'filters_window') and parent_app.filters_window:
        parent_app.filters_window.lift()
        return

    # Crear ventana flotante
    filters_window = tk.Toplevel(parent_app)
    filters_window.title("Filtros Avanzados")
    filters_window.geometry("400x600")
    filters_window.transient(parent_app)

    # Frame principal
    main_frame = ttk.Frame(filters_window, padding=20)
    main_frame.pack(expand=True, fill='both')

    # Título
    ttk.Label(
        main_frame,
        text="Filtros Avanzados",
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(0, 20))

    # Variables de filtro
    if not hasattr(parent_app, 'advanced_filters'):
        parent_app.advanced_filters = {
            'fecha_desde': tk.StringVar(),
            'fecha_hasta': tk.StringVar(),
            'numero_peticion': tk.StringVar(),
            'paciente_nombre': tk.StringVar(),
            'diagnostico': tk.StringVar(),
            'servicio': tk.StringVar(),
            'malignidad': tk.StringVar()
        }

    # Campos de filtro
    filters_data = [
        ("Fecha desde (dd/mm/aaaa)", 'fecha_desde'),
        ("Fecha hasta (dd/mm/aaaa)", 'fecha_hasta'),
        ("Número de petición", 'numero_peticion'),
        ("Nombre del paciente", 'paciente_nombre'),
        ("Diagnóstico (contiene)", 'diagnostico'),
        ("Servicio", 'servicio'),
        ("Malignidad", 'malignidad')
    ]

    for label_text, var_key in filters_data:
        ttk.Label(main_frame, text=label_text).pack(anchor='w', pady=(5, 2))

        if var_key == 'malignidad':
            # Combobox para malignidad
            combo = ttk.Combobox(
                main_frame,
                textvariable=parent_app.advanced_filters[var_key],
                values=["", "PRESENTE", "AUSENTE"],
                state="readonly"
            )
            combo.pack(fill='x', pady=(0, 10))
        else:
            # Entry normal
            ttk.Entry(
                main_frame,
                textvariable=parent_app.advanced_filters[var_key]
            ).pack(fill='x', pady=(0, 10))

    # Botones
    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(fill='x', pady=(20, 0))

    ttk.Button(
        buttons_frame,
        text="🔍 Aplicar Filtros",
        command=lambda: apply_advanced_filters(parent_app),
        bootstyle="primary"
    ).pack(side='left', padx=(0, 10))

    ttk.Button(
        buttons_frame,
        text="🗑️ Limpiar Filtros",
        command=lambda: clear_advanced_filters(parent_app),
        bootstyle="secondary"
    ).pack(side='left', padx=(0, 10))

    ttk.Button(
        buttons_frame,
        text="❌ Cerrar",
        command=lambda: close_filters_window(parent_app),
        bootstyle="outline"
    ).pack(side='right')

    # Guardar referencia
    parent_app.filters_window = filters_window

    # Manejar cierre
    def on_close():
        parent_app.filters_window = None
        filters_window.destroy()

    filters_window.protocol("WM_DELETE_WINDOW", on_close)

def apply_advanced_filters(parent_app):
    """Aplicar filtros avanzados a la tabla"""
    try:
        from core.database_manager import get_all_records_as_dataframe
        df = get_all_records_as_dataframe()

        if df is None or df.empty:
            return

        # Aplicar filtros
        filtered_df = df.copy()
        filters = parent_app.advanced_filters

        # Filtro por fecha
        if filters['fecha_desde'].get():
            try:
                fecha_desde = pd.to_datetime(filters['fecha_desde'].get(), format='%d/%m/%Y')
                fecha_col = [col for col in df.columns if 'fecha' in col.lower() and 'informe' in col.lower()]
                if fecha_col:
                    df_fechas = pd.to_datetime(filtered_df[fecha_col[0]], format='%d/%m/%Y', errors='coerce')
                    filtered_df = filtered_df[df_fechas >= fecha_desde]
            except:
                pass

        if filters['fecha_hasta'].get():
            try:
                fecha_hasta = pd.to_datetime(filters['fecha_hasta'].get(), format='%d/%m/%Y')
                fecha_col = [col for col in df.columns if 'fecha' in col.lower() and 'informe' in col.lower()]
                if fecha_col:
                    df_fechas = pd.to_datetime(filtered_df[fecha_col[0]], format='%d/%m/%Y', errors='coerce')
                    filtered_df = filtered_df[df_fechas <= fecha_hasta]
            except:
                pass

        # Otros filtros
        if filters['numero_peticion'].get():
            filtered_df = filtered_df[filtered_df['numero_peticion'].astype(str).str.contains(filters['numero_peticion'].get(), na=False, case=False)]

        if filters['paciente_nombre'].get():
            nombre_cols = [col for col in df.columns if 'nombre' in col.lower()]
            if nombre_cols:
                filtered_df = filtered_df[filtered_df[nombre_cols[0]].astype(str).str.contains(filters['paciente_nombre'].get(), na=False, case=False)]

        # Actualizar tabla con datos filtrados
        parent_app.update_table_with_filtered_data(filtered_df)

        # Mostrar resultado
        messagebox.showinfo("Filtros Aplicados", f"Se encontraron {len(filtered_df)} registros que cumplen los criterios.")

    except Exception as e:
        messagebox.showerror("Error", f"Error aplicando filtros: {e}")

def clear_advanced_filters(parent_app):
    """Limpiar todos los filtros"""
    for var in parent_app.advanced_filters.values():
        var.set("")

    # Recargar datos completos
    parent_app.refresh_data_and_table()

def close_filters_window(parent_app):
    """Cerrar ventana de filtros"""
    if hasattr(parent_app, 'filters_window') and parent_app.filters_window:
        parent_app.filters_window.destroy()
        parent_app.filters_window = None