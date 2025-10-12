# -*- coding: utf-8 -*-
import sqlite3
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
cursor = conn.cursor()

print("=" * 80)
print("VERIFICACION FINAL - CASOS CRITICOS")
print("=" * 80)

# IHQ250044
print("\n### CASO IHQ250044 (Ki-67)")
print("-" * 80)
cursor.execute("""
    SELECT `IHQ_KI-67`, `IHQ_HER2`, `IHQ_RECEPTOR_ESTROGENO`, `Factor pronostico`
    FROM informes_ihq
    WHERE `N. peticion (0. Numero de biopsia)` = 'IHQ250044'
""")
row = cursor.fetchone()
if row:
    print(f"Ki-67: {row[0] if row[0] else 'N/A'}")
    print(f"HER2: {row[1] if row[1] else 'N/A'}")
    print(f"ER: {row[2] if row[2] else 'N/A'}")
    print(f"Factor Pronostico: {row[3][:100] if row[3] else 'N/A'}...")

    if row[0] == "20%":
        print("\n✅ CORRECTO: Ki-67 = 20%")
    elif row[0] == "10%":
        print("\n❌ ERROR: Ki-67 sigue siendo 10% (debio ser 20%)")
    else:
        print(f"\n⚠️ INESPERADO: Ki-67 = {row[0]}")

# IHQ250010
print("\n\n### CASO IHQ250010 (HER2, ER, P53)")
print("-" * 80)
cursor.execute("""
    SELECT `IHQ_KI-67`, `IHQ_HER2`, `IHQ_RECEPTOR_ESTROGENO`,
           `IHQ_P53`, `IHQ_PDL-1`, `IHQ_RECEPTOR_PROGESTERONOS`
    FROM informes_ihq
    WHERE `N. peticion (0. Numero de biopsia)` = 'IHQ250010'
""")
row = cursor.fetchone()
if row:
    print(f"Ki-67: {row[0] if row[0] else 'N/A'}")
    print(f"HER2: {row[1] if row[1] else 'N/A'}")
    print(f"ER: {row[2] if row[2] else 'N/A'}")
    print(f"P53: {row[3] if row[3] else 'N/A'}")
    print(f"PDL-1: {row[4] if row[4] else 'N/A'}")
    print(f"PR: {row[5] if row[5] else 'N/A'}")

    errores = []
    if row[1] == "NEGATIVO":
        errores.append("HER2 = NEGATIVO (debio ser NO MENCIONADO)")
    if row[2] == "NEGATIVO":
        errores.append("ER = NEGATIVO (debio ser NO MENCIONADO)")
    if row[3] == "NEGATIVO":
        errores.append("P53 = NEGATIVO (debio ser NO MENCIONADO)")

    if errores:
        print("\n❌ ERRORES ENCONTRADOS:")
        for e in errores:
            print(f"  - {e}")
    else:
        print("\n✅ CORRECTO: Ningun biomarcador marcado como NEGATIVO sin evidencia")

conn.close()

print("\n" + "=" * 80)
print("FIN DE VERIFICACION")
print("=" * 80)
