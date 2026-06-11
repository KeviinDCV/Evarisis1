# -*- coding: utf-8 -*-
"""Extrae el contexto de 'CD31' en el OCR de los casos con CD31 vacío, para ver
las formas narrativas que el regex debe captar."""
import sys, os, json, re, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
DM = os.path.join(ROOT, "data", "debug_maps")
CASOS = ["IHQ250277", "IHQ250299", "IHQ250309", "IHQ250311", "IHQ250343",
         "IHQ250346", "IHQ250380", "IHQ250452", "IHQ250638", "IHQ250696"]

def ocr_de(caso):
    fs = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not fs:
        return None
    o = json.load(open(fs[-1], encoding="utf-8")).get("ocr", {})
    for k in ("texto_consolidado", "texto", "texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50:
            return o[k]
    return None

out = {}
for caso in CASOS:
    ocr = ocr_de(caso)
    if not ocr:
        out[caso] = "sin ocr"
        continue
    # Normalizar para buscar CD31 / CD 31 / CD-31
    fragmentos = []
    for m in re.finditer(r"CD\s*[-]?\s*31", ocr, re.IGNORECASE):
        ini = max(0, m.start() - 60)
        fin = min(len(ocr), m.end() + 80)
        frag = ocr[ini:fin].replace("\n", " ")
        frag = re.sub(r"\s+", " ", frag).strip()
        fragmentos.append(frag)
    out[caso] = fragmentos[:3] if fragmentos else "CD31 NO aparece en OCR"

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_cd31_contexto.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
