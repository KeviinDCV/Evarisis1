# -*- coding: utf-8 -*-
"""Detalle de los 2 casos incompletos restantes."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.database_manager import get_all_records_as_dataframe
from core.validation_checker import analizar_batch_registros

df = get_all_records_as_dataframe().fillna("")
nums = [str(df["Numero de caso"].iloc[i]) for i in range(len(df))]
res = analizar_batch_registros(nums)

out = []
for x in res["incompletos"]:
    caso = x["numero_peticion"]
    sub = df[df["Numero de caso"].astype(str) == caso]
    reg = sub.iloc[0] if len(sub) else None
    detalle = {
        "caso": caso,
        "nivel": x.get("nivel"),
        "porcentaje": x.get("porcentaje_completitud"),
        "campos_faltantes": x.get("campos_faltantes", []),
        "biomarcadores_faltantes": x.get("biomarcadores_faltantes", []),
        "ESTUDIOS_SOLIC": str(reg.get("IHQ_ESTUDIOS_SOLICITADOS", "")) if reg is not None else "?",
        "DX_PRINCIPAL": str(reg.get("Diagnostico Principal", ""))[:60] if reg is not None else "?",
    }
    # valores de los campos faltantes
    if reg is not None:
        detalle["valores_faltantes"] = {c: repr(str(reg.get(c, "(no existe)"))) for c in x.get("campos_faltantes", [])}
    out.append(detalle)

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_ultimos2.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("OK", len(out))
