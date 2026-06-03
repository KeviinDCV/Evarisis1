# -*- coding: utf-8 -*-
"""Backup (SOLO LECTURA) del contenido legible de las grant tables corruptas,
para poder re-GRANT manualmente si REPAIR pierde filas. Tambien enumera que
apps/usuarios tienen privilegios por-BD (a quien afectaria el REPAIR)."""
import pymysql, json
OUT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_grants_backup.json"
res = {}
rc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                     connect_timeout=5, charset='utf8mb4')
cur = rc.cursor()
for t in ('mysql.db', 'mysql.tables_priv', 'mysql.columns_priv'):
    try:
        cur.execute(f"SELECT * FROM {t}")
        names = [d[0] for d in cur.description]
        rows = [list(r) for r in cur.fetchall()]
        res[t] = {'columns': names, 'rows': rows}
    except Exception as e:
        res[t] = 'ERR_LECTURA: ' + str(e)[:160]
# usuarios y a quien afecta
try:
    cur.execute("SELECT User, Host FROM mysql.user ORDER BY User")
    res['usuarios'] = [list(r) for r in cur.fetchall()]
except Exception as e:
    res['usuarios'] = 'err'
# resumen de quien tiene grants por-BD (de mysql.db si se pudo leer)
if isinstance(res.get('mysql.db'), dict):
    try:
        idx_u = res['mysql.db']['columns'].index('User')
        idx_d = res['mysql.db']['columns'].index('Db')
        res['resumen_db_grants'] = sorted({(r[idx_u] or '(any)', r[idx_d]) for r in res['mysql.db']['rows']})
    except Exception as e:
        res['resumen_db_grants'] = 'err: ' + str(e)[:120]
rc.close()
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
# imprimir resumen compacto
comp = {
    'mysql.db_legible': isinstance(res.get('mysql.db'), dict),
    'mysql.tables_priv_legible': isinstance(res.get('mysql.tables_priv'), dict),
    'resumen_db_grants': res.get('resumen_db_grants'),
    'usuarios': res.get('usuarios'),
}
print(json.dumps(comp, ensure_ascii=False, default=str))
