import sqlite3

db_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT [Numero de caso] FROM informes_ihq ORDER BY [Numero de caso]")
cases = cursor.fetchall()
conn.close()

for case in cases:
    print(case[0])
