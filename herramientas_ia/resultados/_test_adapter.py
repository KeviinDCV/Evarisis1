# -*- coding: utf-8 -*-
"""Valida el CAMINO REAL de la app: core/db_adapter lee config.ini y conecta.
Importa db_adapter standalone (core/ en path, sin paquete core -> sin utf8_fixer)."""
import sys, json
sys.path.insert(0, r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\core")
import db_adapter

res = {}
try:
    res['dialect'] = db_adapter.dialect()
    cfg = db_adapter._load_config()
    res['host'] = cfg.get('host'); res['base_datos'] = cfg.get('base_datos')
    res['usuario'] = cfg.get('usuario'); res['puerto'] = cfg.get('puerto')
    conn = db_adapter.get_connection(); cur = conn.cursor()
    cur.execute("SELECT VERSION()"); res['mysql_version'] = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM informes_ihq"); res['count_via_adapter'] = cur.fetchone()[0]
    conn.close()
    res['OK'] = (res['dialect'] == 'mysql' and res['count_via_adapter'] == 2073)
except Exception as e:
    import traceback
    res['OK'] = False; res['error'] = str(e); res['tb'] = traceback.format_exc()
print(json.dumps(res, ensure_ascii=False, default=str))
