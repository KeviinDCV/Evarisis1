# -*- coding: utf-8 -*-
"""Reprocesa IHQ250723 con el OCR CORRECTO (pag0, que la segmentación perdió por
ser un 'estudio ligado'). Verifica dx/órgano y guarda."""
import sys, os, json
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import fitz
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import save_records
from core.db_adapter import get_connection
from core.validation_checker import analizar_batch_registros

pdf = os.path.join(ROOT, "pdfs_patologia", "IHQ DEL 723 AL 774.pdf")
doc = fitz.open(pdf)
texto = doc[0].get_text("text")  # pag0 = contenido completo de IHQ250723
doc.close()

db = map_to_database_format(extract_ihq_data(texto))
antes = {"Organo": str(db.get("IHQ_ORGANO")), "Dx": str(db.get("Diagnostico Principal"))[:45],
         "DxColoracion": str(db.get("Diagnostico Coloracion"))[:45], "Malignidad": str(db.get("Malignidad")),
         "Numero": str(db.get("Numero de caso"))}
n = save_records([db])

# Verificar BD + completitud
conn = get_connection(); cur = conn.cursor()
cur.execute('SELECT `Organo`,`Diagnostico Principal`,`Malignidad` FROM informes_ihq WHERE `Numero de caso`=%s', ('IHQ250723',))
bd = cur.fetchone()
conn.close()
ana = analizar_batch_registros(["IHQ250723"])

res = {"extractor": antes, "save": n,
       "bd_tras_save": {"Organo": str(bd[0]), "Dx": str(bd[1])[:45], "Malig": str(bd[2])} if bd else None,
       "completitud": ana["resumen"], "sigue_incompleto": [x["numero_peticion"] for x in ana["incompletos"]]}
with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_reproc_723.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
