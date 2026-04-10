import sqlite3
import pandas as pd

db_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
query = "SELECT [Numero de caso], [Primer nombre], [Primer apellido], [Fecha Informe] FROM informes_ihq LIMIT 50"
df = pd.read_sql_query(query, conn)
conn.close()

print(df.to_string())
