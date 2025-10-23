#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para reprocesar y actualizar caso IHQ250982"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.unified_extractor import extract_ihq_data
from core import database_manager

# Cargar debug map con texto original
debug_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")
print(f"📄 Cargando debug map: {debug_path}")

with open(debug_path, 'r', encoding='utf-8') as f:
    debug_data = json.load(f)

texto_original = debug_data['ocr']['texto_original']

# Extraer con código actualizado
print("\n🔄 Extrayendo datos con extractores v6.0.5...")
resultados = extract_ihq_data(texto_original)

# Conectar a BD
db = database_manager.get_database_connection()
cursor = db.cursor()

# Obtener caso actual
cursor.execute('SELECT "Factor pronostico", "Diagnostico Principal", "Diagnostico Coloracion" FROM casos WHERE "Numero de caso" = ?', ('IHQ250982',))
caso_actual = cursor.fetchone()

print("\n" + "="*80)
print("📊 VALORES ACTUALES VS NUEVOS")
print("="*80)

if caso_actual:
    print(f"\n🔹 Factor Pronóstico:")
    print(f"   ACTUAL: {caso_actual[0]}")
    print(f"   NUEVO:  {resultados.get('factor_pronostico', 'N/A')}")

    print(f"\n🔹 Diagnóstico Principal:")
    print(f"   ACTUAL: {caso_actual[1]}")
    print(f"   NUEVO:  {resultados.get('diagnostico_principal', 'N/A')}")

    print(f"\n🔹 Diagnóstico Coloración:")
    print(f"   ACTUAL: {caso_actual[2]}")
    print(f"   NUEVO:  {resultados.get('diagnostico_coloracion', 'N/A')}")

    # Actualizar BD
    print("\n" + "="*80)
    respuesta = input("¿Actualizar base de datos con nuevos valores? (s/n): ")

    if respuesta.lower() == 's':
        cursor.execute('''
            UPDATE casos
            SET "Factor pronostico" = ?,
                "Diagnostico Principal" = ?,
                "Diagnostico Coloracion" = ?
            WHERE "Numero de caso" = ?
        ''', (
            resultados.get('factor_pronostico', 'N/A'),
            resultados.get('diagnostico_principal', 'N/A'),
            resultados.get('diagnostico_coloracion', 'N/A'),
            'IHQ250982'
        ))
        db.commit()

        print("\n✅ Base de datos actualizada correctamente")

        # Verificar
        cursor.execute('SELECT "Factor pronostico", "Diagnostico Principal", "Diagnostico Coloracion" FROM casos WHERE "Numero de caso" = ?', ('IHQ250982',))
        caso_verificado = cursor.fetchone()

        print("\n📊 VERIFICACIÓN POST-ACTUALIZACIÓN:")
        print(f"   Factor Pronóstico: {caso_verificado[0]}")
        print(f"   Diagnóstico Principal: {caso_verificado[1]}")
        print(f"   Diagnóstico Coloración: {caso_verificado[2]}")
    else:
        print("\n⚠️ Actualización cancelada")
else:
    print("❌ Caso IHQ250982 no encontrado en BD")

db.close()
print("\n" + "="*80)
