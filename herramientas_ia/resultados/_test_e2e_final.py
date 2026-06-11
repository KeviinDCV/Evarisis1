# -*- coding: utf-8 -*-
"""Validación end-to-end final: procesa el PDF 151-200 (tiene IHQ260190) con el
pipeline completo (fallback incluido), SIN tocar BD, y mide completitud:
- IHQ260190 debe quedar completo.
- El conteo de incompletos NO debe aumentar (no-regresión)."""
import sys, os, json, glob
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)

import core.database_manager as dbm
_cap = []
dbm.save_records = lambda regs: (_cap.extend(regs), len(regs))[1]
dbm.init_db = lambda: None
dbm.update_incomplete_records_with_debug_data = lambda *a, **k: 0

from core.ihq_processor import process_ihq_file
from core.validation_checker import verificar_completitud_registro

pdf = None
for cand in [os.path.join(ROOT, "pdfs_patologia", "2026", "IHQ260151 al IHQ260200.pdf"),
             os.path.join(ROOT, "pdfs_patologia", "IHQ260151 al IHQ260200.pdf")]:
    if os.path.exists(cand):
        pdf = cand; break

n = process_ihq_file(pdf, None)

incompletos = []
for reg in _cap:
    caso = str(reg.get("Numero de caso", ""))
    comp = verificar_completitud_registro(caso, registro=reg)
    if comp.get("nivel") != "completo":
        incompletos.append({"caso": caso, "faltan": comp.get("campos_faltantes", [])})

reg190 = next((r for r in _cap if str(r.get("Numero de caso")) == "IHQ260190"), None)
out = {
    "pdf": os.path.basename(pdf) if pdf else "?",
    "total_procesados": n,
    "IHQ260190": {"Dx": str(reg190.get("Diagnostico Principal",""))[:45],
                  "Organo": str(reg190.get("IHQ_ORGANO",""))} if reg190 else "no encontrado",
    "n_incompletos_en_pdf": len(incompletos),
    "incompletos": incompletos[:10],
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_test_e2e_final.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
