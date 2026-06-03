# -*- coding: utf-8 -*-
"""Diagnostico (SOLO LECTURA) de la corrupcion Aria + estado del GRANT."""
import pymysql, json, traceback
res = {}

# 1) Aplico GRANT immediate? huv_app puede conectar/leer?
try:
    hc = pymysql.connect(host='127.0.0.1', port=3306, user='huv_app', password='huv2026',
                         database='huv_oncologia', connect_timeout=4, charset='utf8mb4')
    hcur = hc.cursor(); hcur.execute('SELECT COUNT(*) FROM informes_ihq')
    res['huv_app_count'] = hcur.fetchone()[0]; hc.close()
    res['huv_app'] = 'OK - el GRANT ya aplico (no necesita FLUSH)'
except Exception as e:
    res['huv_app'] = 'FALLO: ' + str(e)[:180]

# 2) root: grants + CHECK TABLE de las tablas de sistema (read-only)
try:
    rc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                         connect_timeout=4, charset='utf8mb4')
    rcur = rc.cursor()
    for label, acct in (('grants_pct', "'huv_app'@'%'"), ('grants_local', "'huv_app'@'localhost'")):
        try:
            rcur.execute(f"SHOW GRANTS FOR {acct}")
            res[label] = [r[0] for r in rcur.fetchall()]
        except Exception as e:
            res[label] = 'err: ' + str(e)[:140]
    res['check_table'] = {}
    for t in ['mysql.user', 'mysql.db', 'mysql.tables_priv', 'mysql.columns_priv',
              'mysql.procs_priv', 'mysql.global_priv', 'mysql.proxies_priv',
              'mysql.servers', 'mysql.roles_mapping']:
        try:
            rcur.execute(f"CHECK TABLE {t}")
            res['check_table'][t] = [list(r) for r in rcur.fetchall()]
        except Exception as e:
            res['check_table'][t] = 'ERR: ' + str(e)[:160]
    try:
        rcur.execute("SELECT @@version, @@aria_recover_options, @@datadir")
        res['server'] = list(rcur.fetchone())
    except Exception as e:
        res['server'] = 'err: ' + str(e)[:120]
    rc.close()
except Exception as e:
    res['root_err'] = str(e)[:180]; res['tb'] = traceback.format_exc()

with open(r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_mysql_diag.json", 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps(res, ensure_ascii=False, default=str))
