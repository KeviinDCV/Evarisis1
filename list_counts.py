import sqlite3

db_path = r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA\data\huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

for table in tables:
    t_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM \"{t_name}\"")
    count = cursor.fetchone()[0]
    print(f"Table: {t_name}, Count: {count}")

conn.close()
