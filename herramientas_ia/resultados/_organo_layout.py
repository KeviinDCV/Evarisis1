# -*- coding: utf-8 -*-
"""Muestra el layout crudo alrededor de 'Organo' y prueba la extracción actual + fallback."""
import sys, os, json, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz

PD = os.path.join(ROOT, "pdfs_patologia")
PDFS = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]

def texto_caso(caso):
    for p in PDFS:
        try:
            doc = fitz.open(p)
        except Exception:
            continue
        pgs = [pg.get_text("text") for pg in doc if caso in pg.get_text("text")]
        doc.close()
        if pgs:
            return "\n".join(pgs)
    return None

# Extracción actual de órgano
from core.extractors.patient_extractor import extract_patient_data

out = {}
for caso in ["IHQ250368", "IHQ250723"]:
    txt = texto_caso(caso)
    if not txt:
        out[caso] = {"err": "no encontrado"}
        continue
    lineas = txt.split("\n")
    # Contexto alrededor de la primera línea que es exactamente 'Organo' o contiene 'rgano'
    idx_org = next((i for i, l in enumerate(lineas) if l.strip().lower() in ("organo", "órgano", "organo:", "órgano:")), None)
    ctx_tabla = lineas[idx_org-1:idx_org+8] if idx_org is not None else []
    # Contexto alrededor de 'Órgano:' (con tilde, macroscópica)
    idx_mac = next((i for i, l in enumerate(lineas) if re.search(r"[Óó]rgano\s*:", l)), None)
    ctx_mac = lineas[idx_mac:idx_mac+3] if idx_mac is not None else []

    # Extracción actual
    try:
        pd_data = extract_patient_data(txt)
        organo_actual = pd_data.get("organo", pd_data.get("Organo", "?"))
    except Exception as e:
        organo_actual = f"ERR: {e}"

    # Candidatos fallback
    fb = {}
    m1 = re.search(r"(?i)[Óó]rgano\s*:\s*([^\n]+)", txt)
    fb["fallback_organo_colon"] = m1.group(1).strip() if m1 else None

    out[caso] = {
        "organo_extraido_actual": str(organo_actual),
        "idx_tabla": idx_org,
        "contexto_tabla": ctx_tabla,
        "contexto_macroscopica": ctx_mac,
        "candidato_fallback": fb,
    }

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_organo_layout.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
