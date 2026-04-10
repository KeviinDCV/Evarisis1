import sqlite3
import pandas as pd

db_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
query = "SELECT * FROM informes_ihq WHERE [Numero de caso] = 'IHQ250133'"
df = pd.read_sql_query(query, conn)
conn.close()

if not df.empty:
    print(df.to_string())
else:
    print("No records found for IHQ250133")
