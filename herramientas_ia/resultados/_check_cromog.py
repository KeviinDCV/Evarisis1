# -*- coding: utf-8 -*-
"""Verifica estado de IHQ_CROMOGRAMINA (mal escrita) vs IHQ_CROMOGRANINA (correcta)
en MySQL y SQLite. SOLO LECTURA."""
import pymysql, sqlite3, json
o = {}
SQLITE = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db"

mc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                     database='huv_oncologia', charset='utf8mb4')
c = mc.cursor()
c.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
          "WHERE TABLE_SCHEMA='huv_oncologia' AND TABLE_NAME='informes_ihq'")
m = [x[0] for x in c.fetchall()]
o['mysql_ncols'] = len(m)
for col in ('IHQ_CROMOGRAMINA', 'IHQ_CROMOGRANINA'):
    if col in m:
        c.execute(f"SELECT COUNT(*) FROM informes_ihq WHERE `{col}` IS NOT NULL AND TRIM(`{col}`) <> ''")
        o['mysql_' + col] = f"existe, {c.fetchone()[0]} casos con dato"
    else:
        o['mysql_' + col] = "NO existe"
mc.close()

s = sqlite3.connect(SQLITE); sc = s.cursor()
sc.execute("PRAGMA table_info(informes_ihq)")
sl = [x[1] for x in sc.fetchall()]
o['sqlite_ncols'] = len(sl)
for col in ('IHQ_CROMOGRAMINA', 'IHQ_CROMOGRANINA'):
    o['sqlite_' + col] = 'existe' if col in sl else 'NO existe'
s.close()

with open(r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_check_cromog.json", 'w', encoding='utf-8') as f:
    json.dump(o, f, ensure_ascii=False, indent=2)
print(json.dumps(o, ensure_ascii=False))
