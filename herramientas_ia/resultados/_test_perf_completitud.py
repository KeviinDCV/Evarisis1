# -*- coding: utf-8 -*-
"""Verifica que el calculo de completitud NUEVO (1 consulta) da identico al
VIEJO (1 consulta por caso) y mide la mejora de velocidad."""
import sys, time, traceback
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
STATUS = ROOT + r"\herramientas_ia\resultados\_test_perf_status.txt"

def log(m):
    with open(STATUS, "a", encoding="utf-8") as f:
        f.write(str(m) + "\n")

open(STATUS, "w").close()
try:
    import sqlite3
    from core import database_manager as dm
    from core.validation_checker import verificar_completitud_registro
    DB = dm.DB_FILE
    df = dm.get_all_records_as_dataframe()
    casos = list(df["Numero de caso"].dropna().unique())
    log(f"total_casos={len(casos)}")

    # NUEVO: 1 SELECT * + analizar todos en memoria
    t0 = time.time()
    conn = sqlite3.connect(DB); cur = conn.cursor(); cur.execute("SELECT * FROM informes_ihq")
    cols = [d[0] for d in cur.description]; ic = cols.index("Numero de caso")
    regs = {r[ic]: dict(zip(cols, r)) for r in cur.fetchall()}; conn.close()
    new_res = {}
    for n in casos:
        new_res[n] = verificar_completitud_registro(n, registro=regs.get(n)).get('completo')
    t_new = time.time() - t0
    log(f"NUEVO (1 consulta, {len(casos)} casos) = {t_new:.3f}s")

    # VIEJO: 1 consulta por caso (muestra de 200 para no esperar demasiado)
    sample = casos[:200]
    t0 = time.time()
    old_res = {n: verificar_completitud_registro(n).get('completo') for n in sample}
    t_old = time.time() - t0
    log(f"VIEJO (1 consulta/caso, {len(sample)} casos) = {t_old:.3f}s  ->  extrapolado a {len(casos)}: ~{t_old/len(sample)*len(casos):.1f}s")

    # Comparar coloreo (sin regresion)
    mismatches = [n for n in sample if old_res[n] != new_res[n]]
    log(f"coincidencias={len(sample)-len(mismatches)}/{len(sample)}  mismatches={mismatches[:10]}")
    log("OK")
except Exception as e:
    log("ERROR=" + str(e)); log(traceback.format_exc())
