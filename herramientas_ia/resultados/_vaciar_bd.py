# -*- coding: utf-8 -*-
"""Vacía las tablas de datos para reproceso limpio. BACKUP CSV antes de borrar.
Salvaguarda: solo vacía una tabla si su backup quedó completo."""
import sys, os, json
from datetime import datetime
ROOT = r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA"
sys.path.insert(0, ROOT)
import pandas as pd
from core.db_adapter import get_connection, dialect

res = {"dialect": dialect(), "antes": {}, "backup": {}, "despues": {}, "errores": []}

ts = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = os.path.join(ROOT, "backups", f"V6.9.31_PRE_REPROCESO_{ts}")
os.makedirs(backup_dir, exist_ok=True)
res["backup_dir"] = backup_dir

conn = get_connection()
cur = conn.cursor()

cur.execute("SHOW TABLES")
tablas = [row[0] for row in cur.fetchall()]
res["tablas_encontradas"] = tablas

# Vaciar SOLO las tablas de datos del pipeline (no metadatos/usuarios)
objetivo = [t for t in tablas if t in ("informes_ihq", "diagnosticos_ia")]
res["tablas_objetivo"] = objetivo

for t in objetivo:
    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
    n = cur.fetchone()[0]
    res["antes"][t] = n

    respaldada = False
    nfilas = None
    try:
        df = pd.read_sql(f"SELECT * FROM `{t}`", conn)
        nfilas = len(df)
        csv_path = os.path.join(backup_dir, f"{t}.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        res["backup"][t] = {"filas": nfilas, "archivo": csv_path}
        respaldada = (nfilas == n)
    except Exception as e:
        res["errores"].append(f"backup {t}: {e}")

    # Vaciar solo si el backup quedó completo (o la tabla ya estaba vacía)
    if respaldada or n == 0:
        try:
            cur.execute(f"DELETE FROM `{t}`")
            conn.commit()
            try:
                cur.execute(f"ALTER TABLE `{t}` AUTO_INCREMENT = 1")
                conn.commit()
            except Exception:
                pass
        except Exception as e:
            res["errores"].append(f"delete {t}: {e}")
    else:
        res["errores"].append(f"NO se vacio {t}: backup incompleto ({nfilas} vs {n})")

    cur.execute(f"SELECT COUNT(*) FROM `{t}`")
    res["despues"][t] = cur.fetchone()[0]

conn.close()

with open(os.path.join(ROOT, "herramientas_ia", "resultados", "_vaciar_bd.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, ensure_ascii=False, indent=1, default=str)
