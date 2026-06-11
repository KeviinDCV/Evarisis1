# -*- coding: utf-8 -*-
"""Valida el FALLBACK (rellena campos vacíos) end-to-end + completitud."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)

import core.database_manager as dbm
_cap = []
dbm.save_records = lambda regs: (_cap.extend(regs), len(regs))[1]
dbm.init_db = lambda: None
dbm.update_incomplete_records_with_debug_data = lambda *a, **k: 0

from core.ihq_processor import process_ihq_file
from core.validation_checker import verificar_completitud_registro

pdf = os.path.join(ROOT, "pdfs_patologia", "2026", "IHQ260701 al IHQ260750.pdf")
if not os.path.exists(pdf):
    pdf = os.path.join(ROOT, "pdfs_patologia", "IHQ260701 al IHQ260750.pdf")

n = process_ihq_file(pdf, None)

objetivo = ["IHQ260704", "IHQ260711", "IHQ260725"]
res = {"pdf": os.path.basename(pdf), "total": n, "casos": {}}
for caso in objetivo:
    reg = next((r for r in _cap if str(r.get("Numero de caso")) == caso), None)
    if not reg:
        res["casos"][caso] = "NO ENCONTRADO"; continue
    comp = verificar_completitud_registro(caso, registro=reg)
    res["casos"][caso] = {
        "Organo": str(reg.get("IHQ_ORGANO", "")),
        "Dx": str(reg.get("Diagnostico Principal", ""))[:40],
        "nivel": comp.get("nivel"),
        "pct": comp.get("porcentaje_completitud"),
        "faltan": comp.get("campos_faltantes", []),
    }
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_test_fallback.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
