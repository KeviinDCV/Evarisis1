# -*- coding: utf-8 -*-
"""Validación anti-regresión del fix CD31:
1) Los 18 casos con CD31 vacío -> ahora deben dar POSITIVO/NEGATIVO.
2) CD34 y CD3 en esos casos NO deben cambiar.
3) Muestra de control (casos que NO mencionan CD31) -> CD31 debe seguir vacío.
"""
import sys, os, json, re, glob, random
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.unified_extractor import extract_ihq_data, map_to_database_format
DM = os.path.join(ROOT, "data", "debug_maps")

OBJETIVO = ["IHQ250277","IHQ250299","IHQ250309","IHQ250311","IHQ250343","IHQ250346",
            "IHQ250380","IHQ250435","IHQ250446","IHQ250448","IHQ250452","IHQ250638",
            "IHQ250696","IHQ250779","IHQ251420","IHQ251434","IHQ251444","IHQ251487"]

def ocr_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado", "texto", "texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50:
            return o[k]
    return None

def menciona_cd31(ocr):
    return bool(re.search(r"CD\s*[-]?\s*31", ocr or "", re.IGNORECASE))

objetivo_res = {}
for c in OBJETIVO:
    ocr = ocr_de(c)
    if not ocr:
        objetivo_res[c] = {"err": "sin ocr"}; continue
    db = map_to_database_format(extract_ihq_data(ocr))
    objetivo_res[c] = {"CD31": str(db.get("IHQ_CD31","")), "CD34": str(db.get("IHQ_CD34","")),
                       "CD3": str(db.get("IHQ_CD3",""))}

# Muestra de control: casos con debug_map que NO mencionan CD31
todos = sorted(set(re.findall(r"debug_map_(IHQ\d{6})_", " ".join(os.listdir(DM)))))
control = [c for c in todos if c not in OBJETIVO]
random.seed(7)
random.shuffle(control)
falsos_positivos = []
revisados = 0
for c in control:
    if revisados >= 30:
        break
    ocr = ocr_de(c)
    if not ocr or menciona_cd31(ocr):
        continue  # solo casos que NO mencionan CD31
    revisados += 1
    db = map_to_database_format(extract_ihq_data(ocr))
    cd31 = str(db.get("IHQ_CD31","")).strip().upper()
    if cd31 and cd31 not in ("", "N/A", "NO MENCIONADO", "NAN", "NO APLICA"):
        falsos_positivos.append({"caso": c, "CD31": cd31})

out = {
    "objetivo_18": objetivo_res,
    "control_revisados_sin_cd31": revisados,
    "falsos_positivos": falsos_positivos,
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_valida_cd31.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
