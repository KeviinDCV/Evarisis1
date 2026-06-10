# -*- coding: utf-8 -*-
"""Prueba de humo del modal de resultados: construye los 5 tabs (lazy) y verifica
que ninguno lanza excepción ni queda en blanco (con datos representativos)."""
import sys, os, json, traceback
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import tkinter as tk

res = {"tabs": {}, "errores": []}
try:
    root = tk.Tk()
    root.withdraw()
    from core.ventana_resultados_importacion import VentanaResultadosImportacion

    incompletos = [
        {"numero_peticion": "IHQ250368", "paciente_nombre": "PACIENTE X",
         "porcentaje_completitud": 93.6, "campos_faltantes_detalle": "Campos: Organo"},
        {"numero_peticion": "IHQ250723", "paciente_nombre": "PACIENTE Y",
         "porcentaje_completitud": 87.3, "campos_faltantes_detalle": "Campos: Diagnostico Coloracion, Organo"},
    ]
    # 300 completos para probar el cap de render
    completos = [{"numero_peticion": f"IHQ25{1000+i}", "paciente_nombre": "Z",
                  "porcentaje_completitud": 100} for i in range(300)]
    resumen = {"total": 302, "completos": 300, "incompletos": 2, "porcentaje_exito": 99.3}

    v = VentanaResultadosImportacion(root, completos, incompletos, resumen,
                                     lambda *a: None, lambda *a: None)

    # Forzar construcción de cada pestaña (lazy) y contar widgets hijos
    for i in range(5):
        try:
            v.notebook.select(i)
            v._on_tab_changed()
            frame = v._tab_specs[i]["frame"]
            v.update_idletasks()
            n_hijos = len(frame.winfo_children())
            res["tabs"][i] = {"construido": v._tab_specs[i]["construido"], "hijos": n_hijos}
        except Exception as e:
            res["errores"].append(f"tab {i}: {e}\n{traceback.format_exc()}")

    v.destroy()
    root.destroy()
except Exception as e:
    res["errores"].append(f"global: {e}\n{traceback.format_exc()}")

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_test_modal.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
