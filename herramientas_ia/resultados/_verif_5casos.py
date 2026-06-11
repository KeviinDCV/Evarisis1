# -*- coding: utf-8 -*-
"""Verificación completa de los 5 casos incompletos del último procesamiento.
Para cada uno: campos faltantes (completitud) + valor actual en BD + valor que
produce el extractor ACTUAL + presencia del dato en el PDF real."""
import sys, os, json, re
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros
from core.unified_extractor import extract_ihq_data, map_to_database_format

CASOS = ["IHQ260034", "IHQ260704", "IHQ260711", "IHQ260725", "IHQ260795"]

# 1) BD actual
df = get_all_records_as_dataframe().fillna("")
reg_by = {}
for i in range(len(df)):
    num = str(df["Numero de caso"].iloc[i])
    if num in CASOS:
        reg_by[num] = {c: str(df[c].iloc[i]) for c in df.columns}

# 2) Completitud (campos faltantes)
res = analizar_batch_registros(CASOS)
falt_by = {}
for x in res["incompletos"]:
    falt_by[x["numero_peticion"]] = {
        "porcentaje": x.get("porcentaje_completitud"),
        "campos_faltantes": x.get("campos_faltantes", []),
        "biomarcadores_faltantes": x.get("biomarcadores_faltantes", []),
    }

# 3) Texto PDF por caso
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
            return "\n".join(pgs), os.path.basename(p)
    return None, None

out = {}
CAMPOS_CLAVE = ["Organo", "IHQ_ORGANO", "Diagnostico Principal", "Diagnostico Coloracion",
                "Malignidad", "IHQ_ESTUDIOS_SOLICITADOS"]
for caso in CASOS:
    txt, pdf = texto_caso(caso)
    reg = reg_by.get(caso, {})
    info = {
        "pdf": pdf,
        "completitud": falt_by.get(caso, {}),
        "bd_actual": {k: reg.get(k, "(no key)") for k in CAMPOS_CLAVE},
    }
    # Extractor ACTUAL (lo que produciría un reproceso)
    if txt:
        try:
            db = map_to_database_format(extract_ihq_data(txt))
            info["extractor_actual"] = {k: str(db.get(k, "(no key)")) for k in CAMPOS_CLAVE}
        except Exception as e:
            info["extractor_actual"] = {"ERROR": str(e)}
        # Buscar 'Órgano:' explícito y líneas de diagnóstico/coloración en el PDF
        m_org = re.search(r"(?i)[Óó]rgano\s*:\s*([^\n]+)", txt)
        info["pdf_organo_colon"] = m_org.group(1).strip() if m_org else None
        # contexto coloración / HE
        lin = [l.strip() for l in txt.split("\n") if l.strip()]
        info["pdf_lineas_coloracion"] = [l for l in lin if re.search(r"(?i)(coloraci[óo]n|hematoxilina|H\s*&\s*E|H-E|\bHE\b)", l)][:4]
    out[caso] = info

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_5casos.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
