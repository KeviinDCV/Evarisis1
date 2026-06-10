# -*- coding: utf-8 -*-
"""Verifica columnas reales en BD y valores en casos clave."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe

df = get_all_records_as_dataframe().fillna("")
cols = list(df.columns)

# ¿Existen estas columnas?
buscar = ["CD13", "NSE", "CA19", "LAMBDA", "LAMDA", "SALL", "MAMOGLOBINA", "MAMAGLOBINA",
          "CROMOGRANINA", "CROMOGRAMINA", "SINAPTOFISINA", "GFAP", "OCT4", "MDM2",
          "CICLINA", "CYCLINA", "BETACATENINA", "CKAE1AE3", "CK5_6", "WT1", "CDX2",
          "ENOLASA", "KAPPA"]
existe = {}
for b in buscar:
    matches = [c for c in cols if b in c.upper()]
    existe[b] = matches

def fila(caso):
    sub = df[df["Numero de caso"].astype(str) == caso]
    if len(sub) == 0:
        return None
    r = sub.iloc[0]
    return {c: str(r[c]) for c in cols if str(r[c]).strip() not in ("", "N/A", "nan")}

casos_clave = {}
for caso, campos_interes in [
    ("IHQ250366", ["IHQ_ESTUDIOS_SOLICITADOS"]),
    ("IHQ250402", ["IHQ_ESTUDIOS_SOLICITADOS"]),
    ("IHQ250136", ["IHQ_ESTUDIOS_SOLICITADOS", "IHQ_MAMOGLOBINA", "IHQ_MAMAGLOBINA"]),
    ("IHQ250439", ["IHQ_ESTUDIOS_SOLICITADOS"]),
    ("IHQ250404", ["IHQ_ESTUDIOS_SOLICITADOS", "IHQ_SINAPTOFISINA"]),
    ("IHQ250352", ["IHQ_ESTUDIOS_SOLICITADOS", "IHQ_CROMOGRANINA"]),
]:
    sub = df[df["Numero de caso"].astype(str) == caso]
    if len(sub) == 0:
        casos_clave[caso] = "NO EXISTE"
        continue
    r = sub.iloc[0]
    d = {}
    for c in campos_interes:
        d[c] = str(r[c]) if c in cols else "(columna no existe)"
    casos_clave[caso] = d

out = {
    "total_columnas": len(cols),
    "columnas_IHQ": [c for c in cols if c.startswith("IHQ_")],
    "existe_columna_para": existe,
    "casos_clave": casos_clave,
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_verif_cols.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK")
