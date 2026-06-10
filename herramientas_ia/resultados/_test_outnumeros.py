# -*- coding: utf-8 -*-
"""Prueba que process_ihq_file(out_numeros=...) captura los números SIN tocar la BD."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)

# Monkeypatch para NO escribir en la BD (solo probar la captura de números)
import core.database_manager as dbm
dbm.save_records = lambda regs: len(regs)   # no guarda; devuelve conteo
dbm.init_db = lambda: None

from core.ihq_processor import process_ihq_file

PD = os.path.join(ROOT, "pdfs_patologia")
# Elegir el PDF más pequeño para que la prueba sea rápida
pdfs = [os.path.join(PD, f) for f in os.listdir(PD) if f.lower().endswith(".pdf")]
pdfs.sort(key=lambda p: os.path.getsize(p))
pdf = pdfs[0]

nums = []
count = process_ihq_file(pdf, None, out_numeros=nums)

out = {
    "pdf": os.path.basename(pdf),
    "saved_count": count,
    "out_numeros_len": len(nums),
    "primeros": nums[:8],
    "coinciden_count_y_numeros": count == len(nums),
}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_test_outnumeros.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
