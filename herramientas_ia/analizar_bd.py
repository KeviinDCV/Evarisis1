# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
cursor = conn.cursor()

# Obtener todos los casos
cursor.execute('SELECT "N. peticion (0. Numero de biopsia)", "IHQ_KI-67" FROM informes_ihq ORDER BY "N. peticion (0. Numero de biopsia)"')
rows = cursor.fetchall()

print("=" * 80)
print(f"ANÁLISIS DE BASE DE DATOS - Total casos: {len(rows)}")
print("=" * 80)

# Buscar IHQ250044 específicamente
cursor.execute('SELECT "N. peticion (0. Numero de biopsia)", "IHQ_KI-67", "Factor pronostico" FROM informes_ihq WHERE "N. peticion (0. Numero de biopsia)" = "IHQ250044"')
ihq250044 = cursor.fetchone()

if ihq250044:
    print("\n### ✅ IHQ250044 ENCONTRADO EN BD:")
    print(f"  Petición: {ihq250044[0]}")
    print(f"  Ki-67: {ihq250044[1] if ihq250044[1] else '(vacío)'}")
    print(f"  Factor pronóstico: {ihq250044[2][:100] if ihq250044[2] else '(vacío)'}...")
else:
    print("\n### ❌ IHQ250044 NO ENCONTRADO EN BD")

# Buscar casos con Ki-67
print("\n" + "=" * 80)
print("CASOS CON Ki-67 EXTRAÍDO:")
print("=" * 80)

cursor.execute('SELECT "N. peticion (0. Numero de biopsia)", "IHQ_KI-67" FROM informes_ihq WHERE "IHQ_KI-67" IS NOT NULL AND "IHQ_KI-67" != "" ORDER BY "N. peticion (0. Numero de biopsia)"')
ki67_casos = cursor.fetchall()

print(f"\nTotal con Ki-67: {len(ki67_casos)}")
for caso in ki67_casos[:15]:
    print(f"  {caso[0]}: {caso[1]}")

if len(ki67_casos) > 15:
    print(f"  ... y {len(ki67_casos) - 15} más")

conn.close()
