# -*- coding: utf-8 -*-
"""¿De dónde vienen los datos malos? Lee base_datos.datos_guardados + extraccion
+ pdf_path + metadata de los debug_maps para identificar el pipeline de origen."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ260034", "IHQ260725", "IHQ260795"]

def ultimo(caso):
    files = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    return files[-1] if files else None

out = {}
for caso in CASOS:
    f = ultimo(caso)
    with open(f, "r", encoding="utf-8") as fh:
        dm = json.load(fh)
    bd = dm.get("base_datos", {})
    guardados = bd.get("datos_guardados", bd) if isinstance(bd, dict) else {}
    ext = dm.get("extraccion", {})
    info = {
        "archivo": os.path.basename(f),
        "pdf_path": dm.get("pdf_path", "?"),
        "metadata": dm.get("metadata", {}),
        "bd_guardados_clave": {
            k: str(guardados.get(k, "(no key)"))[:60] for k in
            ["Diagnostico Principal", "Organo", "IHQ_ORGANO", "Malignidad", "Numero de caso"]
        } if isinstance(guardados, dict) else str(guardados)[:200],
        "extraccion_subkeys": list(ext.keys()) if isinstance(ext, dict) else str(type(ext)),
    }
    # buscar dx/organo dentro de extraccion
    if isinstance(ext, dict):
        for k in ["diagnostico_principal", "diagnostico_final_ihq", "organo", "malignidad"]:
            for sub in [ext] + [v for v in ext.values() if isinstance(v, dict)]:
                if k in sub:
                    info.setdefault("extraccion_valores", {})[k] = str(sub[k])[:60]
                    break
    out[caso] = info

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_origen_datos.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
