#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Consulta simple para verificar biomarcadores IHQ250984"""

import sqlite3
import sys
from pathlib import Path

# Path a la base de datos
db_path = Path(__file__).parent.parent.parent / "data" / "huv_oncologia_NUEVO.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta
    query = """
    SELECT
        [Numero de caso],
        IHQ_RECEPTOR_ESTROGENOS,
        IHQ_RECEPTOR_PROGESTERONA,
        IHQ_HER2,
        [IHQ_KI-67],
        IHQ_GATA3,
        IHQ_SOX10,
        IHQ_ESTUDIOS_SOLICITADOS
    FROM informes_ihq
    WHERE [Numero de caso] = 'IHQ250984'
    """

    cursor.execute(query)
    row = cursor.fetchone()

    if row:
        print(f"Caso: {row[0]}")
        print(f"ER: {row[1] if row[1] else 'N/A'}")
        print(f"PR: {row[2] if row[2] else 'N/A'}")
        print(f"HER2: {row[3] if row[3] else 'N/A'}")
        print(f"Ki-67: {row[4] if row[4] else 'N/A'}")
        print(f"GATA3: {row[5] if row[5] else 'N/A'}")
        print(f"SOX10: {row[6] if row[6] else 'N/A'}")
        print(f"ESTUDIOS_SOLICITADOS: {row[7] if row[7] else 'N/A'}")
    else:
        print("Caso no encontrado")

except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
