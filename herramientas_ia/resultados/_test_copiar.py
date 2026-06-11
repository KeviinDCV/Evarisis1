# -*- coding: utf-8 -*-
"""Prueba de humo: modal con botón copiar. Verifica que los tabs construyen y que
el texto de copiado se genera bien (sin abrir messagebox)."""
import sys, os, json, traceback
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import tkinter as tk

res = {"errores": [], "tabs": {}}
try:
    root = tk.Tk(); root.withdraw()
    from core.ventana_resultados_importacion import VentanaResultadosImportacion

    incompletos = [
        {"numero_peticion": "IHQ260034", "paciente_nombre": "SALOME GALINDEZ",
         "porcentaje_completitud": 80.9, "campos_faltantes_detalle": "Campos: Diagnostico Principal, Organo"},
        {"numero_peticion": "IHQ260711", "paciente_nombre": "RUD ENRIQUEZ",
         "porcentaje_completitud": 80.9, "campos_faltantes_detalle": "Campos: Organo"},
    ]
    completos = [{"numero_peticion": f"IHQ25{1000+i}", "paciente_nombre": "X",
                  "porcentaje_completitud": 100} for i in range(5)]
    resumen = {"total": 7, "completos": 5, "incompletos": 2, "porcentaje_exito": 98.4}
    v = VentanaResultadosImportacion(root, completos, incompletos, resumen, lambda *a: None, lambda *a: None)

    for i in range(5):
        v.notebook.select(i); v._on_tab_changed()
        v.update_idletasks()
        res["tabs"][i] = len(v._tab_specs[i]["frame"].winfo_children())

    # Probar generación de texto
    txt_inc = v._casos_a_texto(v.incompletos, "CASOS INCOMPLETOS")
    res["texto_incompletos"] = txt_inc
    # Probar copia real al portapapeles (sin messagebox: copiar directo)
    v.clipboard_clear(); v.clipboard_append(txt_inc); v.update_idletasks()
    res["clipboard_ok"] = (v.clipboard_get() == txt_inc)

    v.destroy(); root.destroy()
except Exception as e:
    res["errores"].append(f"{e}\n{traceback.format_exc()}")

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_test_copiar.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
