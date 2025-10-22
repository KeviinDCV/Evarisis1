#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Migración: Agregar columna DIAGNOSTICO_COLORACION

Versión: 6.1.0
Fecha: 2025-10-22
Propósito: Agregar columna para diagnóstico del Estudio M (Coloración) con Nottingham
"""

import sqlite3
import os
from pathlib import Path

# Ruta a la base de datos
DB_PATH = Path(__file__).parent.parent / "data" / "huv_oncologia_NUEVO.db"

def agregar_columna_diagnostico_coloracion():
    """Agrega columna DIAGNOSTICO_COLORACION a la tabla informes_ihq"""

    print("="*60)
    print("MIGRACIÓN: Agregar columna DIAGNOSTICO_COLORACION")
    print("="*60)

    if not DB_PATH.exists():
        print(f"ERROR: Base de datos no encontrada en {DB_PATH}")
        return False

    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(informes_ihq)")
        columnas = [col[1] for col in cursor.fetchall()]

        if "Diagnostico Coloracion" in columnas:
            print("INFO: La columna 'Diagnostico Coloracion' ya existe")
            print("No se requiere migración")
            conn.close()
            return True

        # Agregar la columna
        print("Agregando columna 'Diagnostico Coloracion'...")
        cursor.execute('''
            ALTER TABLE informes_ihq
            ADD COLUMN "Diagnostico Coloracion" TEXT
        ''')

        conn.commit()
        print("✅ Columna 'Diagnostico Coloracion' agregada exitosamente")

        # Verificar
        cursor.execute("PRAGMA table_info(informes_ihq)")
        columnas_updated = [col[1] for col in cursor.fetchall()]

        if "Diagnostico Coloracion" in columnas_updated:
            print("✅ Verificación exitosa: La columna existe en la tabla")
        else:
            print("ERROR: La columna no se agregó correctamente")
            conn.close()
            return False

        conn.close()
        print("="*60)
        print("MIGRACIÓN COMPLETADA")
        print("="*60)
        return True

    except Exception as e:
        print(f"ERROR durante la migración: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys

    print("\nEste script agregará la columna 'Diagnostico Coloracion' a la base de datos.")
    print(f"Ruta BD: {DB_PATH}\n")

    respuesta = input("¿Continuar? (sí/no): ").strip().lower()

    if respuesta in ['si', 'sí', 's', 'y', 'yes']:
        resultado = agregar_columna_diagnostico_coloracion()
        sys.exit(0 if resultado else 1)
    else:
        print("Migración cancelada por el usuario")
        sys.exit(0)
