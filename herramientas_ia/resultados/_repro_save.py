# -*- coding: utf-8 -*-
"""Reproduce el flujo de guardado para IHQ260725: extract -> map -> save -> leer BD.
Localiza dónde se pierde el dato (map, save, o post-save)."""
import sys, json, glob, os
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import save_records
from core.db_adapter import get_connection

DM = os.path.join(ROOT, "data", "debug_maps")
out = {}
for caso in ["IHQ260725", "IHQ260034"]:
    f = sorted(glob.glob(os.path.join(DM, f"debug_map_{caso}_*.json")))[-1]
    o = json.load(open(f, encoding="utf-8")).get("ocr", {})
    cons = o.get("texto_consolidado")
    db = map_to_database_format(extract_ihq_data(cons))
    paso1 = {"Dx": str(db.get("Diagnostico Principal"))[:50], "Organo": str(db.get("Organo")),
             "Malig": str(db.get("Malignidad")), "Numero": str(db.get("Numero de caso"))}
    n = save_records([db])
    conn = get_connection(); cur = conn.cursor()
    cur.execute('SELECT `Diagnostico Principal`,`Organo`,`Malignidad` FROM informes_ihq WHERE `Numero de caso`=%s', (caso,))
    bd = cur.fetchone()
    conn.close()
    out[caso] = {"1_map": paso1, "2_save_retorno": n,
                 "3_bd_tras_save": {"Dx": str(bd[0])[:50], "Organo": str(bd[1]), "Malig": str(bd[2])} if bd else None}

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_repro_save.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
