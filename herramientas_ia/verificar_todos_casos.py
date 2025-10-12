#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificación completa de TODOS los 50 casos
Compara texto OCR original vs datos finales en BD
"""

import json
import sqlite3
import sys
import io
from pathlib import Path
import re
from collections import defaultdict

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Obtener todos los casos
debug_dir = Path('data/debug_maps')
debug_files = sorted(debug_dir.glob('debug_map_IHQ*.json'))

print('='*100)
print(f'VERIFICACION COMPLETA DE PRECISION - {len(debug_files)} CASOS')
print('='*100)
print()

conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
cursor = conn.cursor()

# Contadores globales
total_casos = 0
casos_perfectos = 0
casos_con_advertencias = 0
errores_por_tipo = defaultdict(int)
advertencias_detalladas = []

# Verificar cada caso
for debug_file in debug_files:
    total_casos += 1

    # Extraer numero de peticion del nombre de archivo
    caso_id = debug_file.stem.split('_')[2]  # debug_map_IHQ250001_timestamp

    print(f'[{total_casos:2d}/50] Verificando {caso_id}... ', end='', flush=True)

    # Cargar debug map
    with open(debug_file, 'r', encoding='utf-8') as f:
        debug_data = json.load(f)

    texto_ocr = debug_data.get('ocr', {}).get('texto_consolidado', '')

    # Obtener datos de BD
    cursor.execute('''
        SELECT "Primer nombre", "Primer apellido", "N. de identificacion",
               "IHQ_KI-67", "Factor pronostico", "Diagnostico Principal",
               "IHQ_HER2", "IHQ_RECEPTOR_ESTROGENO", "IHQ_RECEPTOR_PROGESTERONOS",
               "Edad", "Medico tratante", "EPS"
        FROM informes_ihq
        WHERE "N. peticion (0. Numero de biopsia)" = ?
    ''', (caso_id,))

    bd_row = cursor.fetchone()
    if not bd_row:
        print('ERROR: No en BD')
        errores_por_tipo['no_en_bd'] += 1
        advertencias_detalladas.append(f'{caso_id}: NO encontrado en base de datos')
        casos_con_advertencias += 1
        continue

    nombre, apellido, id_num, ki67, factor, dx, her2, er, pr, edad, medico, eps = bd_row

    # Contadores locales de este caso
    errores_caso = []
    advertencias_caso = []

    # ==========================================
    # VERIFICACION 1: Datos del paciente
    # ==========================================

    # Nombre
    if nombre and nombre != 'N/A' and nombre != 'Primer nombre':
        if nombre.upper() not in texto_ocr.upper():
            errores_caso.append(f'Nombre "{nombre}" no en OCR')
            errores_por_tipo['nombre_incorrecto'] += 1

    # Apellido
    if apellido and apellido != 'N/A' and apellido != 'Primer apellido':
        if apellido.upper() not in texto_ocr.upper():
            advertencias_caso.append(f'Apellido "{apellido}" no en OCR')
            errores_por_tipo['apellido_no_encontrado'] += 1

    # Edad
    if edad and edad != 'N/A':
        edad_str = str(edad).split()[0]  # "46 años" -> "46"
        if edad_str.isdigit() and edad_str not in texto_ocr:
            advertencias_caso.append(f'Edad "{edad}" no verificable')
            errores_por_tipo['edad_no_verificable'] += 1

    # ==========================================
    # VERIFICACION 2: Biomarcadores principales
    # ==========================================

    # Ki-67
    ki67_en_ocr = bool(re.search(r'ki.?67', texto_ocr, re.IGNORECASE))

    if ki67 and ki67 != 'N/A' and ki67 != 'NO MENCIONADO':
        if not ki67_en_ocr:
            errores_caso.append(f'Ki-67 "{ki67}" en BD pero NO en OCR')
            errores_por_tipo['ki67_fantasma'] += 1
        else:
            # Verificar que el valor está en el texto
            ki67_limpio = ki67.replace('%', '').replace('<', '').replace('>', '').strip()
            # Buscar contexto de Ki-67
            ki67_match = re.search(r'.{0,60}ki.?67.{0,60}', texto_ocr, re.IGNORECASE)
            if ki67_match:
                contexto = ki67_match.group(0)
                if ki67 not in contexto and ki67_limpio not in contexto:
                    advertencias_caso.append(f'Ki-67 valor "{ki67}" podria no coincidir con OCR')
    elif not ki67 or ki67 == 'N/A':
        if ki67_en_ocr:
            # Ki-67 en OCR pero no extraido
            errores_caso.append('Ki-67 en OCR pero NO extraido a BD')
            errores_por_tipo['ki67_no_extraido'] += 1

    # HER2
    her2_en_ocr = bool(re.search(r'her.?2', texto_ocr, re.IGNORECASE))

    if her2 and her2 != 'N/A' and her2 != 'NO MENCIONADO':
        if not her2_en_ocr:
            errores_caso.append(f'HER2 "{her2}" en BD pero NO en OCR')
            errores_por_tipo['her2_fantasma'] += 1

    # Receptor Estrogeno
    er_en_ocr = bool(re.search(r'estr[oó]geno|\bER\b|receptor.*estr', texto_ocr, re.IGNORECASE))

    if er and er not in ['N/A', 'NO MENCIONADO']:
        if not er_en_ocr:
            errores_caso.append(f'ER "{er}" en BD pero NO en OCR')
            errores_por_tipo['er_fantasma'] += 1

    # ==========================================
    # VERIFICACION 3: Diagnostico Principal
    # ==========================================

    if dx and dx != 'N/A' and len(dx) > 10:
        # Extraer palabras significativas (>3 chars)
        dx_words = [w.upper() for w in re.findall(r'\b\w{4,}\b', dx[:100])][:5]
        if dx_words:
            matches = sum(1 for word in dx_words if word in texto_ocr.upper())
            coincidencia_pct = (matches / len(dx_words)) * 100

            if coincidencia_pct < 50:
                errores_caso.append(f'Diagnostico baja coincidencia ({coincidencia_pct:.0f}%)')
                errores_por_tipo['dx_bajo_match'] += 1

    # ==========================================
    # RESUMEN DEL CASO
    # ==========================================

    if errores_caso:
        print(f'ERRORES: {len(errores_caso)}')
        casos_con_advertencias += 1
        for error in errores_caso:
            advertencias_detalladas.append(f'{caso_id}: {error}')
    elif advertencias_caso:
        print(f'Advertencias: {len(advertencias_caso)}')
        casos_con_advertencias += 1
        for adv in advertencias_caso:
            advertencias_detalladas.append(f'{caso_id}: {adv}')
    else:
        print('OK')
        casos_perfectos += 1

print()
print('='*100)
print('RESUMEN FINAL DE VERIFICACION')
print('='*100)
print()

print(f'Total casos analizados:           {total_casos}')
print(f'Casos perfectos (sin errores):    {casos_perfectos} ({(casos_perfectos/total_casos*100):.1f}%)')
print(f'Casos con advertencias/errores:   {casos_con_advertencias} ({(casos_con_advertencias/total_casos*100):.1f}%)')
print()

print('ERRORES POR TIPO:')
print('-'*100)
for tipo, count in sorted(errores_por_tipo.items(), key=lambda x: x[1], reverse=True):
    print(f'  {tipo:30} {count:3} casos')

print()
print('='*100)
print('DETALLE DE ADVERTENCIAS/ERRORES')
print('='*100)
print()

if advertencias_detalladas:
    # Agrupar por tipo de error
    por_tipo = defaultdict(list)
    for adv in advertencias_detalladas:
        caso = adv.split(':')[0]
        tipo = adv.split(':')[1].strip().split()[0] if ':' in adv else 'Otro'
        por_tipo[tipo].append(adv)

    for tipo, items in sorted(por_tipo.items()):
        print(f'\n[{tipo}] - {len(items)} casos:')
        print('-'*100)
        for item in items[:10]:  # Mostrar max 10 por tipo
            print(f'  • {item}')
        if len(items) > 10:
            print(f'  ... y {len(items)-10} más')
else:
    print('   ¡Sin advertencias! Todos los datos son correctos.')

print()
print('='*100)
print('CALIFICACION FINAL')
print('='*100)
print()

precision = (casos_perfectos / total_casos) * 100
if precision >= 95:
    calificacion = 'EXCELENTE'
    emoji = '✅✅✅'
elif precision >= 85:
    calificacion = 'MUY BUENA'
    emoji = '✅✅'
elif precision >= 75:
    calificacion = 'BUENA'
    emoji = '✅'
else:
    calificacion = 'NECESITA REVISION'
    emoji = '⚠️'

print(f'{emoji} PRECISION DEL SISTEMA: {precision:.1f}% - {calificacion}')
print()

# Calcular precision por componente
if total_casos > 0:
    print('PRECISION POR COMPONENTE:')
    print(f'  Datos del paciente:    {((total_casos - errores_por_tipo.get("nombre_incorrecto", 0)) / total_casos * 100):.1f}%')
    print(f'  Biomarcadores:         {((total_casos - errores_por_tipo.get("ki67_no_extraido", 0) - errores_por_tipo.get("ki67_fantasma", 0)) / total_casos * 100):.1f}%')
    print(f'  Diagnostico:           {((total_casos - errores_por_tipo.get("dx_bajo_match", 0)) / total_casos * 100):.1f}%')

print()
print('='*100)

conn.close()
