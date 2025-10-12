"""
Script de Auditoría Completa - 44 casos IHQ
Compara: PDF (texto OCR) vs BD (valores extraídos) vs Reporte IA (correcciones)
Objetivo: Verificar 100% efectividad del sistema de IA
"""

import sqlite3
import pandas as pd
import re
import sys
import io
from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase

# Force UTF-8 encoding para Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def extraer_biomarcador_pdf(texto, biomarcador):
    """
    Extrae el valor de un biomarcador del texto PDF
    """
    # Patrones comunes para cada biomarcador
    patrones = {
        'Ki-67': [
            r'Ki-?67[:\s]+(\d+)\s*%',
            r'Ki-?67[:\s]+([A-Za-z\s]+)',
            r'índice de proliferación[:\s]+(\d+)\s*%'
        ],
        'ER': [
            r'Receptor de Estrógeno[:\s]+(positivo|negativo)',
            r'RE[:\s]+(positivo|negativo)',
            r'Estrógeno[:\s]+(positivo|negativo)'
        ],
        'PR': [
            r'Receptor de Progesterona[:\s]+(positivo|negativo)',
            r'RP[:\s]+(positivo|negativo)',
            r'Progesterona[:\s]+(positivo|negativo)'
        ],
        'HER2': [
            r'HER2[:\s]+(positivo|negativo|\d\+)',
            r'HER-2[:\s]+(positivo|negativo|\d\+)'
        ],
        'P53': [
            r'p53[:\s]+(positivo|negativo|sobreexpresión|sobreexpresion)',
            r'P53[:\s]+(positivo|negativo|sobreexpresión|sobreexpresion)'
        ]
    }

    if biomarcador not in patrones:
        return "NO ENCONTRADO"

    texto_lower = texto.lower()
    for patron in patrones[biomarcador]:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1).strip().upper()

    return "NO MENCIONADO"

def normalizar_valor(valor):
    """Normaliza valores para comparación"""
    if pd.isna(valor) or valor is None or valor == '':
        return "NO REPORTADO"

    valor_str = str(valor).strip().upper()

    # Normalizar variantes comunes
    if 'POSITIVO' in valor_str:
        return "POSITIVO"
    elif 'NEGATIVO' in valor_str:
        return "NEGATIVO"
    elif 'NO MENCIONADO' in valor_str or 'NO REPORTADO' in valor_str:
        return "NO MENCIONADO"
    elif valor_str == '' or valor_str == 'NONE':
        return "NO REPORTADO"
    else:
        return valor_str

def comparar_valores(pdf_val, bd_val, campo):
    """
    Compara valor extraído del PDF vs valor en BD
    Retorna: (coincide: bool, tipo_error: str, pdf_normalizado, bd_normalizado)
    """
    pdf_norm = normalizar_valor(pdf_val)
    bd_norm = normalizar_valor(bd_val)

    # Caso 1: Coincidencia exacta
    if pdf_norm == bd_norm:
        return True, None, pdf_norm, bd_norm

    # Caso 2: PDF dice "NO MENCIONADO" pero BD tiene valor
    if pdf_norm == "NO MENCIONADO" and bd_norm != "NO REPORTADO":
        return False, "FALSO_POSITIVO", pdf_norm, bd_norm

    # Caso 3: PDF tiene valor pero BD dice "NO REPORTADO"
    if pdf_norm != "NO MENCIONADO" and bd_norm == "NO REPORTADO":
        return False, "FALSO_NEGATIVO", pdf_norm, bd_norm

    # Caso 4: Valores diferentes
    if pdf_norm != bd_norm:
        return False, "VALOR_INCORRECTO", pdf_norm, bd_norm

    return True, None, pdf_norm, bd_norm

# ============================================================================
# INICIO DE AUDITORÍA
# ============================================================================

print('='*100)
print('AUDITORIA COMPLETA - VERIFICACION 100% EFECTIVIDAD')
print('='*100)
print()

# 1. Cargar datos de BD
print('[1/5] Cargando datos de la base de datos...')
conn = sqlite3.connect('data/huv_oncologia_NUEVO.db')
query = '''
SELECT
    "N. peticion (0. Numero de biopsia)" as numero,
    "Diagnostico Principal" as diagnostico,
    "Factor pronostico" as factor,
    "IHQ_RECEPTOR_ESTROGENO" as ER,
    "IHQ_RECEPTOR_PROGESTERONOS" as PR,
    "IHQ_HER2" as HER2,
    "IHQ_KI-67" as Ki67,
    "IHQ_P53" as P53,
    "IHQ_PDL-1" as PDL1
FROM informes_ihq
WHERE "N. peticion (0. Numero de biopsia)" LIKE 'IHQ250%'
ORDER BY "N. peticion (0. Numero de biopsia)"
'''
df_bd = pd.read_sql_query(query, conn)
conn.close()
print(f'   Total casos en BD: {len(df_bd)}')
print()

# 2. Extraer y segmentar PDF
print('[2/5] Extrayendo texto del PDF...')
texto_completo = pdf_to_text_enhanced('pdfs_patologia/ordenamientos.pdf')
print(f'   Caracteres extraidos: {len(texto_completo)}')

print('[3/5] Segmentando reportes individuales...')
segmentos = segment_reports_multicase(texto_completo)
print(f'   Total segmentos: {len(segmentos)}')
print()

# 3. Crear diccionario de segmentos por número de caso
print('[4/5] Indexando segmentos por numero de caso...')
segmentos_dict = {}
for seg in segmentos:
    match = re.search(r'(IHQ\d{6})', seg)
    if match:
        numero_caso = match.group(1)
        segmentos_dict[numero_caso] = seg

print(f'   Casos indexados: {len(segmentos_dict)}')
print()

# 4. Auditar cada caso
print('[5/5] Auditando cada caso...')
print('='*100)

# Listas para estadísticas
total_casos = 0
total_campos_verificados = 0
total_coincidencias = 0
total_falsos_positivos = 0
total_falsos_negativos = 0
total_valores_incorrectos = 0

errores_detallados = []

# Filtrar solo casos del rango IHQ250004 a IHQ250050 (44 casos del reporte IA)
casos_auditoria = [f'IHQ250{i:03d}' for i in range(4, 51)]

for caso in casos_auditoria:
    # Verificar si existe en BD
    if caso not in df_bd['numero'].values:
        print(f'\n[ERROR] {caso} - NO ENCONTRADO EN BD')
        continue

    # Verificar si existe en PDF
    if caso not in segmentos_dict:
        print(f'\n[ERROR] {caso} - NO ENCONTRADO EN PDF')
        continue

    total_casos += 1

    # Obtener datos de BD
    bd_row = df_bd[df_bd['numero'] == caso].iloc[0]

    # Obtener texto del PDF
    texto_pdf = segmentos_dict[caso]

    # Comparar biomarcadores clave
    biomarcadores = {
        'Ki-67': ('Ki67', extraer_biomarcador_pdf(texto_pdf, 'Ki-67')),
        'ER': ('ER', extraer_biomarcador_pdf(texto_pdf, 'ER')),
        'PR': ('PR', extraer_biomarcador_pdf(texto_pdf, 'PR')),
        'HER2': ('HER2', extraer_biomarcador_pdf(texto_pdf, 'HER2')),
        'P53': ('P53', extraer_biomarcador_pdf(texto_pdf, 'P53'))
    }

    caso_tiene_errores = False
    caso_errores = []

    for nombre_campo, (columna_bd, valor_pdf) in biomarcadores.items():
        total_campos_verificados += 1

        valor_bd = bd_row[columna_bd]

        coincide, tipo_error, pdf_norm, bd_norm = comparar_valores(valor_pdf, valor_bd, nombre_campo)

        if coincide:
            total_coincidencias += 1
        else:
            caso_tiene_errores = True

            if tipo_error == "FALSO_POSITIVO":
                total_falsos_positivos += 1
            elif tipo_error == "FALSO_NEGATIVO":
                total_falsos_negativos += 1
            elif tipo_error == "VALOR_INCORRECTO":
                total_valores_incorrectos += 1

            caso_errores.append({
                'campo': nombre_campo,
                'tipo_error': tipo_error,
                'pdf': pdf_norm,
                'bd': bd_norm
            })

    # Imprimir resultado del caso
    if caso_tiene_errores:
        print(f'\n{caso} - [ERRORES DETECTADOS]')
        for error in caso_errores:
            print(f'   {error["campo"]:10s} | Tipo: {error["tipo_error"]:20s} | PDF: {error["pdf"]:20s} | BD: {error["bd"]}')

        errores_detallados.append({
            'caso': caso,
            'errores': caso_errores
        })
    else:
        print(f'{caso} - OK', end=' ')
        if total_casos % 5 == 0:
            print()  # Nueva línea cada 5 casos

print()
print()
print('='*100)
print('RESUMEN DE AUDITORIA')
print('='*100)
print()
print(f'Total casos auditados: {total_casos}')
print(f'Total campos verificados: {total_campos_verificados}')
print()
print(f'COINCIDENCIAS: {total_coincidencias} / {total_campos_verificados} ({100*total_coincidencias/total_campos_verificados:.1f}%)')
print()
print(f'ERRORES:')
print(f'  - Falsos Positivos: {total_falsos_positivos} (BD tiene valor pero PDF no menciona)')
print(f'  - Falsos Negativos: {total_falsos_negativos} (PDF tiene valor pero BD no lo capturo)')
print(f'  - Valores Incorrectos: {total_valores_incorrectos} (BD extrajo valor diferente al PDF)')
print()
print(f'PRECISION GLOBAL: {100*total_coincidencias/total_campos_verificados:.2f}%')
print()

if len(errores_detallados) > 0:
    print('='*100)
    print(f'CASOS CON ERRORES: {len(errores_detallados)}')
    print('='*100)
    for item in errores_detallados:
        print(f'\n{item["caso"]}:')
        for error in item['errores']:
            print(f'  [{error["tipo_error"]}] {error["campo"]}: PDF="{error["pdf"]}" vs BD="{error["bd"]}"')
else:
    print('='*100)
    print('[EXITO] NO SE ENCONTRARON ERRORES - 100% EFECTIVIDAD CONFIRMADA')
    print('='*100)
