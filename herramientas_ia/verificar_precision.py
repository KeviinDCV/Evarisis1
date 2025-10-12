#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la precisión del sistema de extracción
Compara texto OCR original (debug maps) con datos finales en BD
"""

import json
import sqlite3
import sys
import io
from pathlib import Path
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Casos representativos para análisis detallado
casos_analizar = ['IHQ250004', 'IHQ250044', 'IHQ250002', 'IHQ250022', 'IHQ250034']

print('='*90)
print('ANALISIS DE PRECISION: TEXTO OCR vs DATOS EN BASE DE DATOS')
print('='*90)
print()

conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
cursor = conn.cursor()

errores_encontrados = []
aciertos = []

for caso_id in casos_analizar:
    print(f'\n{"#"*90}')
    print(f'# CASO: {caso_id}')
    print(f'{"#"*90}\n')

    # 1. Cargar debug map
    debug_files = list(Path('data/debug_maps').glob(f'debug_map_{caso_id}_*.json'))
    if not debug_files:
        print(f'ERROR: Debug map no encontrado\n')
        continue

    with open(debug_files[0], 'r', encoding='utf-8') as f:
        debug_data = json.load(f)

    # 2. Extraer texto OCR consolidado
    texto_ocr = debug_data.get('ocr', {}).get('texto_consolidado', '')

    # 3. Obtener datos de BD
    cursor.execute('''
        SELECT "Primer nombre", "Primer apellido", "N. de identificacion",
               "IHQ_KI-67", "Factor pronostico", "Diagnostico Principal",
               "IHQ_HER2", "IHQ_RECEPTOR_ESTROGENO", "IHQ_RECEPTOR_PROGESTERONOS"
        FROM informes_ihq
        WHERE "N. peticion (0. Numero de biopsia)" = ?
    ''', (caso_id,))

    bd_row = cursor.fetchone()
    if not bd_row:
        print(f'ERROR: No encontrado en BD\n')
        continue

    nombre, apellido, id_num, ki67, factor, dx, her2, er, pr = bd_row

    # 4. VERIFICACION: Datos del paciente
    print('[1] DATOS DEL PACIENTE')
    print('-'*90)

    # Buscar nombre en texto
    if nombre and nombre != 'N/A':
        if nombre.upper() in texto_ocr.upper():
            print(f'  OK Nombre: {nombre} - ENCONTRADO en OCR')
            aciertos.append(f'{caso_id}: Nombre correcto')
        else:
            print(f'  WARN Nombre: {nombre} - NO encontrado en OCR')
            errores_encontrados.append(f'{caso_id}: Nombre {nombre} no en OCR')

    # Buscar identificación
    if id_num and id_num != 'N/A':
        if id_num in texto_ocr:
            print(f'  OK Identificacion: {id_num} - ENCONTRADO en OCR')
            aciertos.append(f'{caso_id}: ID correcto')
        else:
            print(f'  WARN Identificacion: {id_num} - NO encontrado en OCR')
            errores_encontrados.append(f'{caso_id}: ID {id_num} no en OCR')

    # 5. VERIFICACION: Biomarcadores
    print(f'\n[2] BIOMARCADORES PRINCIPALES')
    print('-'*90)

    # Ki-67
    ki67_en_texto = bool(re.search(r'ki.?67', texto_ocr, re.IGNORECASE))
    print(f'  Ki-67 en BD: {ki67 if ki67 else "(vacio)"}')
    print(f'  Ki-67 en OCR: {"SI mencionado" if ki67_en_texto else "NO mencionado"}')

    if ki67 and ki67 != 'N/A':
        if ki67_en_texto:
            # Buscar el valor específico en el texto
            valor_match = re.search(r'ki.?67[:\s]*([^\n]{1,50})', texto_ocr, re.IGNORECASE)
            if valor_match:
                contexto = valor_match.group(0)[:80]
                print(f'  Contexto OCR: "{contexto}..."')

                # Verificar si el valor en BD está en el contexto
                ki67_limpio = ki67.replace('%', '').strip()
                if ki67_limpio in contexto or ki67 in contexto:
                    print(f'  OK: Valor "{ki67}" coincide con OCR')
                    aciertos.append(f'{caso_id}: Ki-67 correcto ({ki67})')
                else:
                    print(f'  WARN: Valor "{ki67}" podria no coincidir exactamente')
        else:
            print(f'  WARN: Ki-67 en BD pero NO en texto OCR')
            errores_encontrados.append(f'{caso_id}: Ki-67 {ki67} no encontrado en OCR')
    elif not ki67 or ki67 == 'N/A':
        if ki67_en_texto:
            print(f'  WARN: Ki-67 en OCR pero NO extraido a BD')
            errores_encontrados.append(f'{caso_id}: Ki-67 en OCR pero no extraido')

    # HER2
    her2_en_texto = bool(re.search(r'her.?2', texto_ocr, re.IGNORECASE))
    print(f'\n  HER2 en BD: {her2 if her2 else "(vacio)"}')
    print(f'  HER2 en OCR: {"SI mencionado" if her2_en_texto else "NO mencionado"}')

    if her2 and her2 != 'N/A' and her2 != 'NO MENCIONADO':
        if not her2_en_texto:
            print(f'  WARN: HER2 en BD pero NO en texto OCR')
            errores_encontrados.append(f'{caso_id}: HER2 {her2} no en OCR')
        else:
            print(f'  OK: HER2 presente en ambos')
            aciertos.append(f'{caso_id}: HER2 correcto')

    # ER (Receptor Estrogeno)
    er_en_texto = bool(re.search(r'estr[oó]geno|\bER\b|receptor.*estr', texto_ocr, re.IGNORECASE))
    print(f'\n  Receptor Estrogeno en BD: {er if er else "(vacio)"}')
    print(f'  Receptor Estrogeno en OCR: {"SI mencionado" if er_en_texto else "NO mencionado"}')

    # 6. VERIFICACION: Diagnostico
    print(f'\n[3] DIAGNOSTICO PRINCIPAL')
    print('-'*90)

    if dx and dx != 'N/A':
        # Buscar palabras clave del diagnóstico en el texto
        dx_words = [w for w in dx[:100].upper().split() if len(w) > 3][:5]
        matches = sum(1 for word in dx_words if word in texto_ocr.upper())
        print(f'  Diagnostico en BD: {dx[:80]}...')
        print(f'  Coincidencia: {matches}/{len(dx_words)} palabras clave en OCR')

        if matches >= len(dx_words) * 0.6:  # 60% de palabras encontradas
            print(f'  OK: Diagnostico parece correcto')
            aciertos.append(f'{caso_id}: Diagnostico verificado')
        else:
            print(f'  WARN: Baja coincidencia de diagnostico con OCR')
            errores_encontrados.append(f'{caso_id}: Diagnostico con baja coincidencia')

print(f'\n{"="*90}')
print('RESUMEN FINAL')
print(f'{"="*90}\n')

print(f'Total aciertos verificados: {len(aciertos)}')
print(f'Total advertencias/errores: {len(errores_encontrados)}')

if errores_encontrados:
    print(f'\nADVERTENCIAS/ERRORES ENCONTRADOS:')
    for i, error in enumerate(errores_encontrados, 1):
        print(f'  {i}. {error}')
else:
    print(f'\n   Todos los datos verificados son correctos!')

print(f'\n{"="*90}')

conn.close()
