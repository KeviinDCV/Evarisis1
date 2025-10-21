#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔄 AUTO-VALIDADOR - EVARISIS CIRUGÍA ONCOLÓGICA
================================================

Módulo que se integra automáticamente en el proceso de guardado
para validar y corregir inconsistencias médico-servicio en tiempo real.

Se ejecuta automáticamente después de guardar casos en la BD.

Autor: Sistema EVARISIS CIRUGÍA ONCOLÓGICA
Versión: 5.3.9.3
Fecha: 19 de octubre de 2025
"""

import sys
import io
import logging
from typing import List, Dict

# Configurar salida UTF-8 en Windows
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'buffer') and not sys.stdout.closed:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validar_y_corregir_casos_guardados(numeros_caso: List[str]) -> Dict[str, any]:
    """
    Valida y corrige automáticamente los casos recién guardados

    Args:
        numeros_caso: Lista de números de petición de casos guardados

    Returns:
        Dict con estadísticas de correcciones aplicadas
    """
    from core.validador_medico_servicio import validar_caso_completo, aplicar_correccion_bd
    from core.database_manager import get_registro_by_peticion

    logger.info("\n🔍 Validando consistencia médico-servicio...")

    estadisticas = {
        "casos_validados": 0,
        "casos_corregidos": 0,
        "correcciones": []
    }

    for numero_caso in numeros_caso:
        try:
            # Obtener registro
            registro = get_registro_by_peticion(numero_caso)

            if not registro:
                continue

            # Validar
            resultado = validar_caso_completo(registro)
            estadisticas["casos_validados"] += 1

            # Si necesita corrección, aplicarla
            if not resultado["valido"] and resultado["servicio_correcto"]:
                logger.warning(f"\n⚠️ Inconsistencia detectada en {numero_caso}:")
                logger.info(f"   Médico: {registro.get('Médico tratante', 'N/A')} ({resultado['especialidad']})")
                logger.info(f"   Servicio actual: {resultado['servicio_actual']}")
                logger.info(f"   Servicio correcto: {resultado['servicio_correcto']}")

                # Aplicar corrección
                exito = aplicar_correccion_bd(
                    numero_caso,
                    resultado["servicio_correcto"],
                    resultado["comentario_sistema"]
                )

                if exito:
                    estadisticas["casos_corregidos"] += 1
                    estadisticas["correcciones"].append({
                        "numero_caso": numero_caso,
                        "medico": registro.get('Médico tratante', 'N/A'),
                        "servicio_anterior": resultado['servicio_actual'],
                        "servicio_nuevo": resultado['servicio_correcto']
                    })
                    logger.info(f"   ✅ Corrección aplicada automáticamente")

        except Exception as e:
            logger.error(f"   ❌ Error validando {numero_caso}: {e}")
            continue

    # Resumen
    if estadisticas["casos_corregidos"] > 0:
        logger.info(f"\n📊 Resumen de validación:")
        logger.info(f"   • Casos validados: {estadisticas['casos_validados']}")
        logger.info(f"   • Correcciones aplicadas: {estadisticas['casos_corregidos']}")
    else:
        logger.info(f"   ✅ Todos los casos son consistentes")

    return estadisticas


def mostrar_correcciones_en_ui(correcciones: List[Dict], parent_window=None):
    """
    Muestra las correcciones aplicadas en una ventana de diálogo

    Args:
        correcciones: Lista de correcciones aplicadas
        parent_window: Ventana padre (opcional)
    """
    if not correcciones:
        return

    try:
        import tkinter as tk
        from tkinter import ttk
        import ttkbootstrap as ttk_bootstrap

        # Crear ventana
        ventana = tk.Toplevel(parent_window) if parent_window else tk.Tk()
        ventana.title("Correcciones Automáticas - Validador Médico-Servicio")
        ventana.geometry("700x400")

        # Frame principal
        main_frame = ttk.Frame(ventana, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = ttk.Label(
            main_frame,
            text=f"🩺 Se aplicaron {len(correcciones)} corrección(es) automática(s)",
            font=("Segoe UI", 14, "bold")
        )
        titulo.pack(pady=(0, 20))

        # Frame con scroll
        scroll_frame = ttk.Frame(main_frame)
        scroll_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text widget
        texto = tk.Text(
            scroll_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 10),
            padx=10,
            pady=10
        )
        texto.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=texto.yview)

        # Agregar correcciones
        for i, corr in enumerate(correcciones, 1):
            texto.insert(tk.END, f"{i}. Caso {corr['numero_caso']}\n", "titulo")
            texto.insert(tk.END, f"   Médico: {corr['medico']}\n")
            texto.insert(tk.END, f"   Servicio: {corr['servicio_anterior']} ", "error")
            texto.insert(tk.END, "→ ", "flecha")
            texto.insert(tk.END, f"{corr['servicio_nuevo']}\n", "exito")
            texto.insert(tk.END, "\n")

        # Configurar tags
        texto.tag_config("titulo", font=("Segoe UI", 10, "bold"), foreground="#2E86DE")
        texto.tag_config("error", foreground="#EE5A6F", font=("Consolas", 10, "bold"))
        texto.tag_config("exito", foreground="#26DE81", font=("Consolas", 10, "bold"))
        texto.tag_config("flecha", font=("Consolas", 10, "bold"))

        texto.config(state=tk.DISABLED)

        # Botón cerrar
        btn_cerrar = ttk.Button(
            main_frame,
            text="Cerrar",
            command=ventana.destroy,
            bootstyle="primary"
        )
        btn_cerrar.pack(pady=(10, 0))

        # Centrar ventana
        ventana.update_idletasks()
        x = (ventana.winfo_screenwidth() // 2) - (ventana.winfo_width() // 2)
        y = (ventana.winfo_screenheight() // 2) - (ventana.winfo_height() // 2)
        ventana.geometry(f"+{x}+{y}")

        if not parent_window:
            ventana.mainloop()

    except Exception as e:
        logging.info(f"Error mostrando ventana de correcciones: {e}")


if __name__ == "__main__":
    # Test
    logging.info("🔍 Test del auto-validador")
    logging.info("=" * 80)

    # Simular guardado de casos
    casos_test = ["IHQ250980", "IHQ250999"]

    resultado = validar_y_corregir_casos_guardados(casos_test)

    logging.info("\n" + "=" * 80)
    logging.info(f"✅ Validación completada")
    logging.info(f"   Casos validados: {resultado['casos_validados']}")
    logging.info(f"   Correcciones aplicadas: {resultado['casos_corregidos']}")

    if resultado['correcciones']:
        logging.info("\n📝 Correcciones:")
        for corr in resultado['correcciones']:
            logging.info(f"   • {corr['numero_caso']}: {corr['servicio_anterior']} → {corr['servicio_nuevo']}")
