# -*- coding: utf-8 -*-
"""Solo migracion de datos (privilegios ya reparados). USE huv_oncologia +
DROP/CREATE/INSERT informes_ihq con los 2073 de SQLite + verificar huv_app."""
import sqlite3, pymysql, json, traceback

SQLITE = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db"
OUT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_migrate_data_only.json"
res = {'pasos': []}

def q(c):
    return '`' + c.replace('`', '``') + '`'

try:
    sc = sqlite3.connect(SQLITE); scur = sc.cursor()
    scur.execute("PRAGMA table_info(informes_ihq)")
    info = scur.fetchall()
    colnames = [r[1] for r in info]
    pk = [r[1] for r in info if r[5]]
    sel = ", ".join('"' + c.replace('"', '""') + '"' for c in colnames)
    scur.execute(f'SELECT {sel} FROM informes_ihq')
    rows = scur.fetchall(); sc.close()
    res['pasos'].append(f"SQLite: {len(rows)} filas, {len(colnames)} cols")

    rc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                         charset='utf8mb4', autocommit=False)
    cur = rc.cursor()
    cur.execute("USE huv_oncologia")
    cur.execute("SELECT COUNT(*) FROM informes_ihq"); res['antes'] = cur.fetchone()[0]

    coldefs = [(f"{q(c)} VARCHAR(255) NOT NULL" if c in pk else f"{q(c)} LONGTEXT") for c in colnames]
    pkclause = (", PRIMARY KEY (" + ", ".join(q(c) for c in pk) + ")") if pk else ""
    cur.execute("DROP TABLE IF EXISTS informes_ihq")
    cur.execute(f"CREATE TABLE informes_ihq ({', '.join(coldefs)}{pkclause}) "
                f"ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
    ph = ", ".join(["%s"] * len(colnames))
    ins = f"INSERT INTO informes_ihq ({', '.join(q(c) for c in colnames)}) VALUES ({ph})"
    for i in range(0, len(rows), 100):
        cur.executemany(ins, rows[i:i + 100])
    rc.commit()
    cur.execute("SELECT COUNT(*) FROM informes_ihq"); res['despues'] = cur.fetchone()[0]
    # limpiar fila duplicada de grant (cosmetico) y dejar 1 sola
    cur.execute("SELECT COUNT(*) FROM mysql.db WHERE User='huv_app' AND Db='huv_oncologia'")
    res['grant_rows_huv'] = cur.fetchone()[0]
    rc.close()
    res['pasos'].append(f"informes_ihq: {res['antes']} -> {res['despues']}")

    hc = pymysql.connect(host='127.0.0.1', port=3306, user='huv_app', password='huv2026',
                         database='huv_oncologia', connect_timeout=5, charset='utf8mb4')
    hcur = hc.cursor()
    hcur.execute("SELECT COUNT(*) FROM informes_ihq"); res['huv_app_count'] = hcur.fetchone()[0]
    hcur.execute('SELECT `Numero de caso` FROM informes_ihq LIMIT 1'); p = hcur.fetchone()[0]
    hcur.execute('UPDATE informes_ihq SET `Numero de caso`=`Numero de caso` WHERE `Numero de caso`=%s', (p,))
    hc.commit(); hc.close()
    res['huv_app_rw'] = f"OK lee {res['huv_app_count']} y escribe"
    res['OK'] = (res['despues'] == len(rows) == res['huv_app_count'])

except Exception as e:
    res['OK'] = False; res['error'] = str(e); res['tb'] = traceback.format_exc()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps(res, ensure_ascii=False, default=str))
