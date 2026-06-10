# -*- coding: utf-8 -*-
"""Diagnóstico para llegar al 100%: clasifica CADA biomarcador faltante en:
  - MAPEO: '(NO MAPEADO)' -> el nombre solicitado no está en MAPEO_BIOMARCADORES
  - DATO_PRESENTE: la columna canónica YA tiene valor (falso incompleto puro)
  - EXTRACCION: columna vacía pero el token SÍ aparece en el PDF
  - AUSENTE_PDF: columna vacía y el token NO aparece en el PDF (solicitado sin resultado)
"""
import sys, os, json, re, unicodedata
from collections import Counter, defaultdict
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros, MAPEO_BIOMARCADORES

def norm_key(s):
    nf = unicodedata.normalize("NFKD", str(s))
    t = "".join(c for c in nf if not unicodedata.combining(c)).upper()
    return re.sub(r"[\s\-_/.]+", "", t)

# Índice normalizado del mapa (para ver si una variante SÍ tiene destino)
MAPA_NORM = {}
for k, v in MAPEO_BIOMARCADORES.items():
    MAPA_NORM.setdefault(norm_key(k), v)

df = get_all_records_as_dataframe()
df = df.fillna("")
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
reg_by = {str(df["Numero de caso"].iloc[i]): {c: df[c].iloc[i] for c in df.columns} for i in range(len(df))}
res = analizar_batch_registros(nums)

# Índice caso -> texto PDF (una pasada por todos los PDFs)
PD = os.path.join(ROOT, "pdfs_patologia")
texto_por_caso = {}
for f in os.listdir(PD):
    if not f.lower().endswith(".pdf"):
        continue
    try:
        doc = fitz.open(os.path.join(PD, f))
    except Exception:
        continue
    for pg in doc:
        tx = pg.get_text("text")
        m = re.findall(r"IHQ\d{6}", tx)
        for caso in set(m):
            texto_por_caso.setdefault(caso, []).append(tx)
    doc.close()
texto_por_caso = {k: norm_key("  ".join(v)) for k, v in texto_por_caso.items()}

VACIO = ("", "N/A", "NA", "NO ENCONTRADO", "NAN", "NO APLICA", "NO MENCIONADO", "SIN DATO", "NONE")
cat = Counter()
ejemplos = defaultdict(list)
mapeo_pendiente = Counter()  # nombre normalizado -> cuenta (para variantes a agregar)

for x in res["incompletos"]:
    caso = x["numero_peticion"]
    reg = reg_by.get(caso, {})
    pdftxt = texto_por_caso.get(caso, "")
    for b in x.get("biomarcadores_faltantes", []):
        if "(NO MAPEADO)" in b:
            nombre = b.replace("(NO MAPEADO)", "").strip()
            nk = norm_key(nombre)
            destino = MAPA_NORM.get(nk)
            if destino:
                # SÍ tiene destino al normalizar -> el dato puede estar ahí
                val = str(reg.get(destino, "")).strip()
                if val.upper() not in VACIO:
                    cat["MAPEO_dato_presente"] += 1
                    ejemplos["MAPEO_dato_presente"].append(f"{caso}:{nombre}->{destino}={val[:20]}")
                else:
                    cat["MAPEO_col_vacia"] += 1
                    ejemplos["MAPEO_col_vacia"].append(f"{caso}:{nombre}->{destino}")
                mapeo_pendiente[f"{nk} -> {destino}"] += 1
            else:
                cat["MAPEO_sin_destino"] += 1
                ejemplos["MAPEO_sin_destino"].append(f"{caso}:{nombre}")
                mapeo_pendiente[f"{nk} -> ???"] += 1
        else:
            # Es una columna canónica (IHQ_...)
            val = str(reg.get(b, "")).strip()
            if val.upper() not in VACIO:
                cat["DATO_PRESENTE"] += 1
                ejemplos["DATO_PRESENTE"].append(f"{caso}:{b}={val[:20]}")
            else:
                tok = norm_key(b.replace("IHQ_", ""))
                en_pdf = bool(tok and len(tok) >= 2 and tok in pdftxt)
                if en_pdf:
                    cat["EXTRACCION"] += 1
                    ejemplos["EXTRACCION"].append(f"{caso}:{b}")
                else:
                    cat["AUSENTE_PDF"] += 1
                    ejemplos["AUSENTE_PDF"].append(f"{caso}:{b}")

out = {
    "resumen": res["resumen"],
    "n_incompletos": len(res["incompletos"]),
    "categorias": dict(cat),
    "mapeo_variantes_pendientes": mapeo_pendiente.most_common(40),
    "ejemplos": {k: v[:12] for k, v in ejemplos.items()},
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_diag_100.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
