import sqlite3

db_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
conn.close()

print(tables)
