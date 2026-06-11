# -*- coding: utf-8 -*-
"""Lee los debug_maps de los 5 casos y verifica contra el OCR (la fuente real):
órgano, diagnóstico, malignidad, coloración."""
import sys, os, json, re, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ260034", "IHQ260704", "IHQ260711", "IHQ260725", "IHQ260795"]

def ultimo_debugmap(caso):
    files = glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json"))
    return sorted(files)[-1] if files else None

def get_ocr(dm):
    # Buscar el texto OCR en varias claves posibles
    for path in [("ocr", "texto_consolidado"), ("ocr", "texto"), ("ocr_texto",),
                 ("texto_ocr",), ("ocr", "texto_completo")]:
        cur = dm
        ok = True
        for k in path:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                ok = False; break
        if ok and isinstance(cur, str) and len(cur) > 50:
            return cur
    return None

out = {}
for caso in CASOS:
    f = ultimo_debugmap(caso)
    if not f:
        out[caso] = {"err": "sin debug_map"}
        continue
    with open(f, "r", encoding="utf-8") as fh:
        dm = json.load(fh)
    ocr = get_ocr(dm)
    info = {"debug_map": os.path.basename(f), "claves_top": list(dm.keys())}
    if ocr:
        lin = [l.strip() for l in ocr.split("\n") if l.strip()]
        # Órgano: etiqueta de tabla + contexto, y 'Órgano:' explícito
        idx = next((i for i,l in enumerate(lin) if l.lower() in ("organo","órgano","organo:","órgano:")), None)
        info["ctx_tabla_organo"] = lin[idx-1:idx+9] if idx is not None else "no etiqueta 'Organo'"
        m = re.search(r"(?i)[Óó]rgano\s*:\s*([^\n]+)", ocr)
        info["organo_colon"] = m.group(1).strip() if m else None
        # Diagnóstico / malignidad: buscar carcinoma/leucemia/maligno
        info["menciona_carcinoma"] = bool(re.search(r"(?i)carcinoma|leucemia|adenocarcinoma|maligno|neoplasia malign", ocr))
        # Líneas de diagnóstico
        info["lineas_dx"] = [l for l in lin if re.search(r"(?i)(diagn[óo]stico|leucemia|carcinoma|cuello|[úu]tero|mama|c[ée]rvi)", l)][:6]
    else:
        info["ocr"] = "NO se encontró texto OCR en el debug_map"
        # mostrar estructura de 'ocr' si existe
        if "ocr" in dm and isinstance(dm["ocr"], dict):
            info["ocr_subkeys"] = list(dm["ocr"].keys())
    out[caso] = info

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_debugmaps.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
