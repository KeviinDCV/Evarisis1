# -*- coding: utf-8 -*-
"""Repara las 2 grant tables Aria corruptas + completa la migracion.
Orden seguro: si REPAIR/FLUSH/GRANT fallan, SE DETIENE antes de tocar datos.
La migracion de datos (DROP/CREATE/INSERT informes_ihq) solo corre si los
privilegios quedaron sanos. Solo toca: mysql.db, mysql.tables_priv (repair) y
huv_oncologia.informes_ihq (datos). NO toca otras BD.
"""
import sqlite3, pymysql, json, traceback

SQLITE = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db"
OUT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_repair_and_migrate.json"
res = {'pasos': []}

def q(c):
    return '`' + c.replace('`', '``') + '`'

try:
    rc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                         charset='utf8mb4', autocommit=True)
    cur = rc.cursor()

    # === FASE 1: REPARAR PRIVILEGIOS ===
    for t in ('mysql.db', 'mysql.tables_priv'):
        cur.execute(f"REPAIR TABLE {t}")
        res['pasos'].append(f"REPAIR {t}: " + json.dumps([list(r) for r in cur.fetchall()], default=str))
    cur.execute("FLUSH PRIVILEGES")
    res['pasos'].append("FLUSH PRIVILEGES OK")

    # re-GRANT (idempotente) para asegurar cache fresca
    for acct in ("'huv_app'@'%'", "'huv_app'@'localhost'"):
        cur.execute(f"GRANT ALL PRIVILEGES ON huv_oncologia.* TO {acct}")
    cur.execute("FLUSH PRIVILEGES")
    res['pasos'].append("GRANT ALL ON huv_oncologia.* a huv_app + FLUSH")

    cur.execute("SHOW GRANTS FOR 'huv_app'@'%'")
    res['grants_huv_app_pct'] = [r[0] for r in cur.fetchall()]
    # verificar que phpMyAdmin (pma) sobrevivio
    cur.execute("SELECT User, Db FROM mysql.db ORDER BY User, Db")
    res['mysql_db_post'] = [list(r) for r in cur.fetchall()]

    # GUARD: el grant de huv_app sobre huv_oncologia DEBE existir ahora
    tiene_grant = any('huv_oncologia' in g.lower() for g in res['grants_huv_app_pct'])
    if not tiene_grant:
        raise RuntimeError("El GRANT sobre huv_oncologia NO quedo activo tras REPAIR. Abortando migracion de datos.")

    # === FASE 2: MIGRAR DATOS (solo si privilegios OK) ===
    sc = sqlite3.connect(SQLITE); scur = sc.cursor()
    scur.execute("PRAGMA table_info(informes_ihq)")
    info = scur.fetchall()
    colnames = [r[1] for r in info]
    pk = [r[1] for r in info if r[5]]
    sel_cols = ", ".join('"' + c.replace('"', '""') + '"' for c in colnames)
    scur.execute(f'SELECT {sel_cols} FROM informes_ihq')
    rows = scur.fetchall()
    sc.close()
    res['pasos'].append(f"SQLite: {len(rows)} filas, {len(colnames)} cols")

    rc.begin()  # transaccion para la carga de datos
    coldefs = []
    for c in colnames:
        coldefs.append(f"{q(c)} VARCHAR(255) NOT NULL" if c in pk else f"{q(c)} LONGTEXT")
    pkclause = (", PRIMARY KEY (" + ", ".join(q(c) for c in pk) + ")") if pk else ""
    cur.execute("DROP TABLE IF EXISTS informes_ihq")
    cur.execute(f"CREATE TABLE informes_ihq ({', '.join(coldefs)}{pkclause}) "
                f"ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
    placeholders = ", ".join(["%s"] * len(colnames))
    insert = f"INSERT INTO informes_ihq ({', '.join(q(c) for c in colnames)}) VALUES ({placeholders})"
    for i in range(0, len(rows), 100):
        cur.executemany(insert, rows[i:i + 100])
    rc.commit()
    cur.execute("SELECT COUNT(*) FROM informes_ihq")
    res['mysql_count_post'] = cur.fetchone()[0]
    res['pasos'].append(f"informes_ihq recreada + {len(rows)} filas -> {res['mysql_count_post']}")
    rc.close()

    # === FASE 3: VERIFICAR como huv_app (lee + escribe) ===
    hc = pymysql.connect(host='127.0.0.1', port=3306, user='huv_app', password='huv2026',
                         database='huv_oncologia', connect_timeout=5, charset='utf8mb4')
    hcur = hc.cursor()
    hcur.execute("SELECT COUNT(*) FROM informes_ihq"); res['huv_app_count'] = hcur.fetchone()[0]
    hcur.execute('SELECT `Numero de caso` FROM informes_ihq LIMIT 1'); primer = hcur.fetchone()[0]
    hcur.execute('UPDATE informes_ihq SET `Numero de caso`=`Numero de caso` WHERE `Numero de caso`=%s', (primer,))
    hc.commit(); hc.close()
    res['huv_app_rw'] = f"OK lee {res['huv_app_count']} y escribe"
    res['OK'] = True

except Exception as e:
    res['OK'] = False
    res['error'] = str(e)
    res['traceback'] = traceback.format_exc()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps(res, ensure_ascii=False, default=str))
