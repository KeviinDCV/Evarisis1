# -*- coding: utf-8 -*-
"""Batch A (SOLO LECTURA): verifica antes de migrar SQLite -> MySQL.
- Esquema SQLite informes_ihq (columnas, PK)
- Conteos SQLite vs MySQL
- Casos que existen SOLO en MySQL (se perderian al reemplazar) -> CRITICO
- Tablas presentes en cada motor
- Existencia de mysqldump
NO modifica nada.
"""
import sqlite3, pymysql, json, os

SQLITE = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db"
OUT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA\herramientas_ia\resultados\_migracion_check.json"

out = {}

# --- SQLite ---
sc = sqlite3.connect(SQLITE); scur = sc.cursor()
scur.execute("PRAGMA table_info(informes_ihq)")
cols = scur.fetchall()  # (cid, name, type, notnull, dflt, pk)
out['sqlite_cols'] = [{'name': c[1], 'type': c[2], 'notnull': c[3], 'pk': c[5]} for c in cols]
out['sqlite_ncols'] = len(cols)
out['sqlite_pk_cols'] = [c[1] for c in cols if c[5]]
scur.execute("SELECT COUNT(*) FROM informes_ihq"); out['sqlite_count'] = scur.fetchone()[0]
scur.execute('SELECT "Numero de caso" FROM informes_ihq')
sqlite_cases = set(r[0] for r in scur.fetchall())
scur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
out['sqlite_tables'] = [r[0] for r in scur.fetchall()]
# conteo de otras tablas relevantes
for t in ('diagnosticos_ia',):
    try:
        scur.execute(f'SELECT COUNT(*) FROM {t}'); out[f'sqlite_{t}_count'] = scur.fetchone()[0]
    except Exception as e:
        out[f'sqlite_{t}_count'] = f'NO_EXISTE'
sc.close()

# --- MySQL (root, solo lectura) ---
mc = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='',
                     database='huv_oncologia', connect_timeout=4, charset='utf8mb4')
mcur = mc.cursor()
mcur.execute("SELECT COUNT(*) FROM informes_ihq"); out['mysql_count'] = mcur.fetchone()[0]
mcur.execute('SELECT `Numero de caso` FROM informes_ihq')
mysql_cases = set(r[0] for r in mcur.fetchall())
mcur.execute("SHOW TABLES"); out['mysql_tables'] = [r[0] for r in mcur.fetchall()]
mc.close()

# --- Diff critico ---
only_mysql = sorted([c for c in (mysql_cases - sqlite_cases)])
out['solo_en_mysql_total'] = len(only_mysql)
out['solo_en_mysql_muestra'] = only_mysql[:80]
out['en_ambos'] = len(mysql_cases & sqlite_cases)
out['solo_en_sqlite_total'] = len(sqlite_cases - mysql_cases)

# --- mysqldump ---
out['mysqldump_path'] = r"C:\xampp\mysql\bin\mysqldump.exe"
out['mysqldump_exists'] = os.path.exists(out['mysqldump_path'])

with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2, default=str)

resumen = {k: v for k, v in out.items() if k != 'sqlite_cols'}
print(json.dumps(resumen, ensure_ascii=False, default=str))
