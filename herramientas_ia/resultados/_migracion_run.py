# -*- coding: utf-8 -*-
"""Batch B: GRANT privilegios a huv_app + recrear informes_ihq en MySQL con
los 2073 casos de SQLite. Backup ya hecho. solo_en_mysql=0 verificado.
Solo toca la tabla informes_ihq de huv_oncologia. NO toca diagnosticos_ia
ni las otras BD del servidor (glpi, mis, turnero_huv, evarisbot).
"""
import sqlite3, pymysql, json, traceback

SQLITE = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db"
OUT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_migracion_run.json"
res = {'pasos': []}

def q(c):
    return '`' + c.replace('`', '``') + '`'

try:
    # --- Leer SQLite (esquema + filas) ---
    sc = sqlite3.connect(SQLITE); scur = sc.cursor()
    scur.execute("PRAGMA table_info(informes_ihq)")
    info = scur.fetchall()
    colnames = [r[1] for r in info]
    pk = [r[1] for r in info if r[5]]
    sel_cols = ", ".join('"' + c.replace('"', '""') + '"' for c in colnames)
    scur.execute(f'SELECT {sel_cols} FROM informes_ihq')
    rows = scur.fetchall()
    sc.close()
    res['pasos'].append(f"SQLite leido: {len(rows)} filas, {len(colnames)} cols, PK={pk}")

    # --- MySQL como root ---
    mc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                         database='huv_oncologia', charset='utf8mb4', autocommit=False)
    mcur = mc.cursor()

    # 1) GRANT privilegios a huv_app (solo huv_oncologia)
    for acct in ("'huv_app'@'%'", "'huv_app'@'localhost'"):
        mcur.execute(f"GRANT ALL PRIVILEGES ON huv_oncologia.* TO {acct}")
    mcur.execute("FLUSH PRIVILEGES")
    res['pasos'].append("GRANT ALL ON huv_oncologia.* a huv_app@% y @localhost + FLUSH")

    # 2) Recrear informes_ihq (respaldada en .sql)
    coldefs = []
    for c in colnames:
        if c in pk:
            coldefs.append(f"{q(c)} VARCHAR(255) NOT NULL")
        else:
            coldefs.append(f"{q(c)} LONGTEXT")
    pkclause = (", PRIMARY KEY (" + ", ".join(q(c) for c in pk) + ")") if pk else ""
    create = (f"CREATE TABLE informes_ihq ({', '.join(coldefs)}{pkclause}) "
              f"ENGINE=InnoDB DEFAULT CHARSET=utf8mb4")
    mcur.execute("DROP TABLE IF EXISTS informes_ihq")
    mcur.execute(create)
    res['pasos'].append(f"informes_ihq recreada ({len(colnames)} cols, PK VARCHAR(255))")

    # 3) Insertar 2073 filas
    placeholders = ", ".join(["%s"] * len(colnames))
    insert = (f"INSERT INTO informes_ihq ({', '.join(q(c) for c in colnames)}) "
              f"VALUES ({placeholders})")
    BATCH = 100
    for i in range(0, len(rows), BATCH):
        mcur.executemany(insert, rows[i:i + BATCH])
    mc.commit()
    mcur.execute("SELECT COUNT(*) FROM informes_ihq")
    res['mysql_count_post'] = mcur.fetchone()[0]
    res['pasos'].append(f"Insertadas {len(rows)} filas -> MySQL ahora tiene {res['mysql_count_post']}")
    mc.close()

    # 4) Verificar como huv_app (confirma que el GRANT funciona end-to-end)
    hc = pymysql.connect(host='127.0.0.1', port=3306, user='huv_app', password='huv2026',
                         database='huv_oncologia', charset='utf8mb4', connect_timeout=4)
    hcur = hc.cursor()
    hcur.execute("SELECT COUNT(*) FROM informes_ihq")
    res['huv_app_count'] = hcur.fetchone()[0]
    # prueba de escritura: UPDATE no-op (set un campo a si mismo en 1 fila) para confirmar permisos de escritura
    hcur.execute('SELECT `Numero de caso` FROM informes_ihq LIMIT 1')
    primer = hcur.fetchone()[0]
    hcur.execute('UPDATE informes_ihq SET `Numero de caso`=`Numero de caso` WHERE `Numero de caso`=%s', (primer,))
    hc.commit()
    hc.close()
    res['huv_app_escritura'] = 'OK (UPDATE no-op exitoso)'
    res['pasos'].append(f"huv_app lee {res['huv_app_count']} casos y puede escribir")
    res['OK'] = True

except Exception as e:
    res['OK'] = False
    res['error'] = str(e)
    res['traceback'] = traceback.format_exc()

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2, default=str)
print(json.dumps(res, ensure_ascii=False, default=str))
