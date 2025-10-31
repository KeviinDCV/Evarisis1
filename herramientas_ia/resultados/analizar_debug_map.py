#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Analizar debug_map IHQ250992"""

import json
import re

with open('data/debug_maps/debug_map_IHQ250992_20251029_091949.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

unified = data['extraccion']['unified_extractor']
bd = data['base_datos']['datos_guardados']
texto_ocr = data['ocr']['texto_consolidado']

print('='*80)
print('COMPARACION: UNIFIED_EXTRACTOR vs DATOS_GUARDADOS vs OCR')
print('='*80)
print()

# Campos críticos a comparar
campos = [
    ('Diagnostico Principal', 'diagnostico'),
    ('Diagnostico Coloracion', None),
    ('Factor pronostico', 'factor_pronostico'),
    ('IHQ_ESTUDIOS_SOLICITADOS', 'estudios_solicitados_tabla'),
]

for campo_bd, campo_unified in campos:
    valor_bd = bd.get(campo_bd, '[NO EXISTE]')
    valor_unified = unified.get(campo_unified, '[NO EXISTE]') if campo_unified else '[NO EXTRAE]'

    print(f'CAMPO: {campo_bd}')
    print(f'-' * 80)
    print(f'BD guardó:')
    if isinstance(valor_bd, str) and len(valor_bd) > 150:
        print(f'  {valor_bd[:150]}...')
    else:
        print(f'  {valor_bd}')
    print()
    print(f'Unified extrajo ({campo_unified}):')
    if isinstance(valor_unified, str) and len(valor_unified) > 150:
        print(f'  {valor_unified[:150]}...')
    else:
        print(f'  {valor_unified}')
    print()
    coinciden = 'SI' if valor_bd == valor_unified else 'NO'
    print(f'¿Coinciden? {coinciden}')
    print()
    print()

print('='*80)
print('ANALISIS: ESTUDIOS SOLICITADOS')
print('='*80)
print()

# Extraer estudios del OCR
patron_estudios = r'se\s+realiza\s+marcaci[óo]n\s+para\s+([^\.]+)'
match = re.search(patron_estudios, texto_ocr, re.IGNORECASE)

if match:
    estudios_ocr_texto = match.group(1).strip()
    print(f'OCR dice (texto completo):')
    print(f'  "{estudios_ocr_texto}"')
    print()

    # Parsear biomarcadores
    biomarcadores = [b.strip() for b in re.split(r',|\sy\s', estudios_ocr_texto)]
    biomarcadores = [b for b in biomarcadores if b]

    print(f'OCR parseado (biomarcadores individuales):')
    for b in biomarcadores:
        print(f'  - {b}')
    print(f'Total: {len(biomarcadores)} biomarcadores')
else:
    biomarcadores = []
    print('❌ No se encontró patrón de estudios solicitados en OCR')

print()
print(f'IHQ_ESTUDIOS_SOLICITADOS en BD:')
print(f'  "{bd.get("IHQ_ESTUDIOS_SOLICITADOS", "")}"')
print()

# Verificar columnas IHQ_* pobladas
print('='*80)
print('COLUMNAS IHQ_* POBLADAS EN BD')
print('='*80)
print()

columnas_pobladas = {}
for k, v in bd.items():
    if k.startswith('IHQ_') and v:
        if k not in ['IHQ_ESTUDIOS_SOLICITADOS', 'IHQ_ORGANO']:
            columnas_pobladas[k] = v

print(f'Total columnas con valor: {len(columnas_pobladas)}')
for k, v in columnas_pobladas.items():
    print(f'  {k}: {v}')
print()

# Comparar con OCR
print(f'Biomarcadores esperados (OCR): {len(biomarcadores)}')
print(f'Biomarcadores extraídos (BD): {len(columnas_pobladas)}')
print(f'Diferencia: {len(biomarcadores) - len(columnas_pobladas)} faltantes')
print()

# Listar faltantes
if biomarcadores:
    print('='*80)
    print('BIOMARCADORES FALTANTES')
    print('='*80)
    print()

    # Normalizar nombres para comparar
    def normalizar(nombre):
        return nombre.upper().strip()

    biomarcadores_norm = [normalizar(b) for b in biomarcadores]
    columnas_norm = {normalizar(k.replace('IHQ_', '').replace('_', '-')): k for k in columnas_pobladas.keys()}

    for bio in biomarcadores:
        bio_norm = normalizar(bio)
        if bio_norm not in columnas_norm:
            print(f'  ❌ {bio} (no mapeado)')
        else:
            columna = columnas_norm[bio_norm]
            print(f'  ✅ {bio} → {columna}')
