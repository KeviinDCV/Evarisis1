# -*- coding: utf-8 -*-
"""Valida que la app arranca en modo MySQL: init_db() + lectura del visualizador.
Importa core (utf8_fixer cierra stdout) -> escribe resultado a JSON, no usa print."""
import sys, json, traceback
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
OUT = ROOT + r"\herramientas_ia\resultados\_test_app_init.json"
res = {}
try:
    from core import database_manager as dm
    res['use_mysql'] = dm._use_mysql()
    res['DB_FILE_local'] = dm.DB_FILE
    dm.init_db()
    res['init_db'] = 'OK'
    df = dm.get_all_records_as_dataframe()
    res['visualizador_rows'] = int(len(df))
    res['visualizador_cols'] = int(len(df.columns)) if hasattr(df, 'columns') else None
    try:
        fr = dm.get_fecha_range_registros()
        res['fecha_range'] = fr
    except Exception as e:
        res['fecha_range'] = 'ERR: ' + str(e)[:120]
    res['OK'] = True
except Exception as e:
    res['OK'] = False; res['error'] = str(e); res['tb'] = traceback.format_exc()
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
