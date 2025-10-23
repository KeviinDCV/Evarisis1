#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test de normalización de nombres de columna"""

def _normalize_column_name(column_name: str) -> str:
    """Copia de la función de database_manager.py"""
    column_mappings = {
        'Descripcion macroscopica': 'descripcion_macroscopica',
        'Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)': 'descripcion_microscopica',
        'Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)': 'diagnostico_final',
        'Diagnostico Coloracion': 'diagnostico_coloracion',
        'N. de identificación': 'numero_identificacion',
        'N. peticion (0. Numero de biopsia)': 'numero_peticion',
        'Médico tratante': 'medico_tratante',
        'Organo (1. Muestra enviada a patología)': 'organo',
        'IHQ_ORGANO': 'ihq_organo',
        'organo': 'organo',
        'ihq_organo': 'ihq_organo',
        'Factor pronostico': 'factor_pronostico',
        'Diagnostico Principal': 'diagnostico_principal'
    }

    if column_name in column_mappings:
        return column_mappings[column_name]

    normalized = column_name.lower()
    normalized = normalized.replace(' ', '_')
    normalized = normalized.replace('(', '').replace(')', '')
    normalized = normalized.replace('.', '').replace(',', '')
    normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')

    return normalized

# Simular lo que hace save_records()
record = {
    'IHQ_ESTUDIOS_SOLICITADOS': 'CKAE1E3, CAM5.2, CK7, GFAP, SOX10, SOX100',
    'FACTOR_PRONOSTICO': 'positivo para CK7, CAM5.2',
    'IHQ_CK7': 'POSITIVO',
    'IHQ_CKAE1AE3': 'POSITIVO',
    'Numero de caso': 'IHQ250982'
}

print("="*80)
print("TEST NORMALIZACIÓN Y BÚSQUEDA")
print("="*80)

# Columnas de la BD (como las obtiene PRAGMA table_info)
bd_columns = [
    'Numero de caso',
    'IHQ_ESTUDIOS_SOLICITADOS',
    'FACTOR_PRONOSTICO',
    'IHQ_CK7',
    'IHQ_CKAE1AE3'
]

for col in bd_columns:
    normalized_col = _normalize_column_name(col)

    # Lógica de save_records línea 709
    value = record.get(normalized_col, record.get(col, 'N/A'))

    print(f"\nColumna BD: {col}")
    print(f"  Normalizada: {normalized_col}")
    print(f"  Búsqueda 1 (normalizada): {record.get(normalized_col, 'NOT FOUND')}")
    print(f"  Búsqueda 2 (original): {record.get(col, 'NOT FOUND')}")
    print(f"  VALOR FINAL: {value}")

    if value == 'N/A':
        print(f"  ❌ ERROR: Valor no encontrado")
    else:
        print(f"  ✅ OK: Valor encontrado")

print("\n" + "="*80)
