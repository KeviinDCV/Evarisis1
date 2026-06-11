# -*- coding: utf-8 -*-
"""Verifica los 9 casos incompletos del reproceso IA-off: qué campos faltan,
qué hay en la BD, y si el dato está en el OCR (fallo de extraccion) o es N/A real."""
import sys, os, json, re, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros
DM = os.path.join(ROOT, "data", "debug_maps")

df = get_all_records_as_dataframe().fillna("")
df["_n"] = df["Numero de caso"].astype(str)
casos2026 = sorted(df[df["_n"].str.startswith("IHQ26")]["_n"].tolist())
res = analizar_batch_registros(casos2026)

rows = {df["_n"].iloc[i]: i for i in range(len(df))}

def ocr_de(caso):
    files = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))
    if not files:
        return None
    try:
        o = json.load(open(files[-1], encoding="utf-8")).get("ocr", {})
    except Exception:
        return None
    for k in ("texto_consolidado", "texto", "texto_completo"):
        if isinstance(o.get(k), str) and len(o[k]) > 50:
            return o[k]
    return None

CAMPOS = ["Organo", "IHQ_ORGANO", "Diagnostico Principal", "Diagnostico Coloracion", "Malignidad"]
out = {"total_2026": len(casos2026), "resumen": res["resumen"], "casos": []}
for x in res["incompletos"]:
    caso = x["numero_peticion"]
    i = rows.get(caso)
    reg = {c: str(df[c].iloc[i]) for c in CAMPOS} if i is not None else {}
    ocr = ocr_de(caso)
    item = {
        "caso": caso,
        "porcentaje": x.get("porcentaje_completitud"),
        "campos_faltantes": x.get("campos_faltantes", []),
        "biomarcadores_faltantes": x.get("biomarcadores_faltantes", []),
        "bd": reg,
    }
    if ocr:
        # ¿El órgano aparece en la tabla del OCR?
        mb = re.search(r"Bloques y laminas\s*\n([^\n]+)", ocr)
        item["ocr_organo_tabla"] = mb.group(1).strip() if mb else None
        # ¿Sección diagnóstico?
        md = re.search(r"(?i)\bDIAGN[ÓO]STICO\b[:\s]*\n?(.{0,180})", ocr)
        item["ocr_dx"] = md.group(1).replace("\n", " | ").strip() if md else None
    out["casos"].append(item)

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_9casos.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
