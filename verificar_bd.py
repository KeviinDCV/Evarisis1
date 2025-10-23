#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verificar datos guardados en BD para IHQ250982"""

import sqlite3
import json

conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM informes_ihq WHERE "Numero de caso" = ?', ('IHQ250982',))
columns = [desc[0] for desc in cursor.description]
row = cursor.fetchone()

if row:
    data = dict(zip(columns, row))

    # Campos críticos a verificar
    campos_criticos = [
        'Numero de caso',
        'IHQ_ESTUDIOS_SOLICITADOS',
        'Factor pronostico',  # CORREGIDO: nombre exacto en BD
        'IHQ_CK7',
        'IHQ_CKAE1AE3',
        'IHQ_CAM52',
        'IHQ_GFAP',
        'IHQ_S100',
        'IHQ_SOX10'
    ]

    resultado = {k: data.get(k, 'N/A') for k in campos_criticos}

    with open('verificacion_bd.json', 'w', encoding='utf-8') as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print("Resultado guardado en verificacion_bd.json")

    # Mostrar resumen
    print("\n=== VERIFICACIÓN BD ===")
    for campo in campos_criticos:
        valor = resultado.get(campo, 'N/A')
        valor_mostrar = valor[:60] + "..." if valor and len(str(valor)) > 60 else valor
        print(f"{campo:30s}: {valor_mostrar}")
else:
    print("Caso IHQ250982 NO encontrado en BD")

conn.close()
