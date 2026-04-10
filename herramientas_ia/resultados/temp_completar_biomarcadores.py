import sys
import re
from pathlib import Path

print('='*80)
print('COMPLETANDO IMPLEMENTACION DE TDT Y GLICOFORINA')
print('='*80)
print()

# Definir biomarcadores
biomarcadores = [
    {
        'nombre': 'TDT',
        'columna': 'IHQ_TDT',
        'variantes': ['TDT', 'TdT', 'TERMINAL DEOXYNUCLEOTIDYL TRANSFERASE']
    },
    {
        'nombre': 'GLICOFORINA',
        'columna': 'IHQ_GLICOFORINA',
        'variantes': ['GLICOFORINA', 'GLYCOPHORIN', 'GLICOFORINA A', 'GLYCOPHORIN A']
    }
]

archivos_modificados_total = []
errores_total = []

for bio in biomarcadores:
    nombre = bio['nombre']
    columna = bio['columna']
    variantes = bio['variantes']
    
    print(f'PROCESANDO: {nombre}')
    print(f'  Columna BD: {columna}')
    print()
    
    # 1. database_manager.py - Agregar columna
    print('  1/5 database_manager.py...')
    try:
        archivo_path = Path('core/database_manager.py')
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        modificaciones = 0
        
        # Verificar si ya existe
        if columna in contenido:
            print(f'     SKIP: {columna} ya existe')
        else:
            # Agregar en NEW_TABLE_COLUMNS_ORDER (después de IHQ_CK7)
            patron1 = r'("IHQ_CK7",\s+"IHQ_MAMOGLOBINA",)'
            if re.search(patron1, contenido):
                contenido = re.sub(patron1, f'\1 "{columna}",', contenido, count=1)
                modificaciones += 1
            
            # Agregar en CREATE TABLE
            patron2 = r'("IHQ_CK7" TEXT,)'
            if re.search(patron2, contenido):
                contenido = re.sub(patron2, f'\1\n            "{columna}" TEXT,', contenido, count=1)
                modificaciones += 1
            
            # Agregar en new_biomarkers list
            patron3 = r'(new_biomarkers = \[[\s\S]*?"IHQ_CK7",)'
            if re.search(patron3, contenido):
                contenido = re.sub(patron3, f'\1 "{columna}",', contenido, count=1)
                modificaciones += 1
            
            if modificaciones > 0:
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print(f'     OK: {modificaciones} lugares modificados')
                archivos_modificados_total.append(f'{archivo_path.name} ({nombre})')
            else:
                print(f'     ERROR: No se pudo modificar')
                errores_total.append(f'{archivo_path.name}: No se encontraron patrones ({nombre})')
    except Exception as e:
        print(f'     ERROR: {e}')
        errores_total.append(f'database_manager.py: {e} ({nombre})')
    
    # 2. ui.py - Agregar a columnas visibles
    print('  2/5 ui.py...')
    try:
        archivo_path = Path('ui.py')
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if columna in contenido:
            print(f'     SKIP: {columna} ya existe')
        else:
            # Buscar lista de columnas (después de IHQ_CK7)
            patron = r'("IHQ_CK7",)'
            if re.search(patron, contenido):
                contenido = re.sub(patron, f'\1\n            "{columna}",', contenido, count=1)
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print(f'     OK: Agregado a columnas visibles')
                archivos_modificados_total.append(f'{archivo_path.name} ({nombre})')
            else:
                print(f'     ERROR: No se encontró patrón')
                errores_total.append(f'ui.py: No se encontró patrón ({nombre})')
    except Exception as e:
        print(f'     ERROR: {e}')
        errores_total.append(f'ui.py: {e} ({nombre})')
    
    # 3. validation_checker.py - Agregar mapeo
    print('  3/5 validation_checker.py...')
    try:
        archivo_path = Path('core/validation_checker.py')
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if f"'{nombre}':" in contenido:
            print(f'     SKIP: {nombre} ya existe')
        else:
            # Agregar en all_biomarker_mapping
            patron = r"('CK7': 'IHQ_CK7',)"
            if re.search(patron, contenido):
                contenido = re.sub(patron, f"\1\n    '{nombre}': '{columna}',", contenido, count=1)
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print(f'     OK: Agregado a mapeo de validación')
                archivos_modificados_total.append(f'{archivo_path.name} ({nombre})')
            else:
                print(f'     ERROR: No se encontró patrón')
                errores_total.append(f'validation_checker.py: No se encontró patrón ({nombre})')
    except Exception as e:
        print(f'     ERROR: {e}')
        errores_total.append(f'validation_checker.py: {e} ({nombre})')
    
    # 4. biomarker_extractor.py (solo si no existe)
    print('  4/5 biomarker_extractor.py...')
    try:
        archivo_path = Path('core/extractors/biomarker_extractor.py')
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if nombre.lower() in contenido.lower():
            print(f'     SKIP: {nombre} ya existe')
        else:
            modificaciones = 0
            
            # Agregar en single_marker_patterns
            patron1 = r'(single_marker_patterns = \[[\s\S]*?ck7\|)'
            if re.search(patron1, contenido):
                contenido = re.sub(patron1, f'\1{nombre.lower()}|', contenido, count=2)
                modificaciones += 1
            
            # Agregar en normalize_biomarker_name
            patron2 = r"('CK7': 'CK7',\s+'CK-7': 'CK7',\s+'CK 7': 'CK7',)"
            mapeo = f"\n        '{nombre}': '{nombre}',\n        '{nombre.replace('_', '-')}': '{nombre}',\n        '{nombre.replace('_', ' ')}': '{nombre}',"
            if re.search(patron2, contenido):
                contenido = re.sub(patron2, f'\1{mapeo}', contenido, count=1)
                modificaciones += 1
            
            if modificaciones > 0:
                with open(archivo_path, 'w', encoding='utf-8') as f:
                    f.write(contenido)
                print(f'     OK: {modificaciones} lugares modificados')
                archivos_modificados_total.append(f'{archivo_path.name} ({nombre})')
            else:
                print(f'     ERROR: No se pudo modificar')
                errores_total.append(f'biomarker_extractor.py: No se encontraron patrones ({nombre})')
    except Exception as e:
        print(f'     ERROR: {e}')
        errores_total.append(f'biomarker_extractor.py: {e} ({nombre})')
    
    # 5. unified_extractor.py - Agregar mapeo
    print('  5/5 unified_extractor.py...')
    try:
        archivo_path = Path('core/unified_extractor.py')
        with open(archivo_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        if f"
