#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca biomarcadores que no tengan el formato estándar POSITIVO/NEGATIVO (...)
"""

import json
import glob
import re
from collections import defaultdict

print('=' * 80)
print('BÚSQUEDA DE BIOMARCADORES SIN FORMATO ESTÁNDAR')
print('=' * 80)
print()
print('Formato esperado: POSITIVO/NEGATIVO (contexto opcional en minúsculas)')
print()

# Buscar todos los debug_maps más recientes de cada caso
casos_problema = []

# Obtener lista de casos únicos
archivos = glob.glob('data/debug_maps/debug_map_IHQ*.json')
casos = {}

for archivo in archivos:
    # Extraer número de caso
    match = re.search(r'IHQ\d+', archivo)
    if match:
        caso = match.group()
        # Guardar solo el más reciente (último por nombre)
        if caso not in casos or archivo > casos[caso]:
            casos[caso] = archivo

print(f'Analizando {len(casos)} casos...')
print()

# Analizar cada caso
for caso, archivo in sorted(casos.items()):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)

        bd_data = data.get('base_datos', {}).get('datos_guardados', {})

        # Buscar campos IHQ_*
        for campo, valor in bd_data.items():
            if not campo.startswith('IHQ_'):
                continue
            if not valor or valor == 'SIN DATO':
                continue

            # Verificar si tiene formato estándar
            valor_str = str(valor)
            valor_upper = valor_str.upper()

            # Excluir campos válidos
            # 1. POSITIVO o NEGATIVO (con contexto opcional entre paréntesis)
            if re.match(r'^(POSITIVO|NEGATIVO)(\s*\([^)]+\))?$', valor_upper):
                continue

            # 2. Porcentajes simples: 50%, 12.5%
            if re.match(r'^\d+(\.\d+)?%?$', valor_str):
                continue

            # 3. Rangos: 10-20%, 51-60
            if re.match(r'^\d+-\d+%?$', valor_str):
                continue

            # 4. Valores especiales aceptados
            if valor_upper in ['SIN DATO', 'NO DETERMINADO', 'NO CONTRIBUTIVA', 'NO CONTRIBUTIVO',
                              'EQUIVOCO', 'SCORE 0', 'SCORE 1+', 'SCORE 2+', 'SCORE 3+']:
                continue

            # 5. EQUIVOCO con score
            if re.match(r'^EQUIVOCO\s*\(.*\)$', valor_upper):
                continue

            # Si llegamos aquí, el formato NO es estándar
            casos_problema.append({
                'caso': caso,
                'campo': campo,
                'valor': valor_str
            })
    except Exception as e:
        print(f'Error en {caso}: {e}')
        continue

print(f'Encontrados {len(casos_problema)} biomarcadores con formato no estándar')
print()

if casos_problema:
    # Agrupar por patrón de problema
    patrones = defaultdict(list)

    for item in casos_problema:
        # Identificar tipo de problema
        valor = item['valor']

        if 'EXPRESIÓN' in valor.upper() or 'EXPRESION' in valor.upper():
            patron = 'EXPRESIÓN (sin normalizar)'
        elif 'INMUNOREACTIVIDAD' in valor.upper():
            patron = 'INMUNOREACTIVIDAD (sin normalizar)'
        elif 'SOBREEXPRESIÓN' in valor.upper() or 'SOBREEXPRESION' in valor.upper():
            patron = 'SOBREEXPRESIÓN (sin normalizar)'
        elif len(valor) > 50:
            patron = 'TEXTO NARRATIVO LARGO'
        else:
            patron = 'OTRO'

        patrones[patron].append(item)

    print('RESUMEN POR TIPO DE PROBLEMA:')
    print('-' * 80)
    for patron, items in sorted(patrones.items(), key=lambda x: -len(x[1])):
        print(f'\n{patron}: {len(items)} casos')
        print('-' * 80)
        for item in items[:5]:  # Mostrar primeros 5 de cada tipo
            valor_corto = item['valor'][:60] + '...' if len(item['valor']) > 60 else item['valor']
            print(f"  {item['caso']:12} | {item['campo']:30} | {valor_corto}")
        if len(items) > 5:
            print(f"  ... y {len(items) - 5} más")
else:
    print('✅ Todos los biomarcadores tienen formato estándar')

print()
print('=' * 80)
