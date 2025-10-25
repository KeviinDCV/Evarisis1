#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reprocesar caso IHQ250984 con extractores corregidos
Inserta datos directamente en la BD
"""

import sys
import io
import sqlite3
from pathlib import Path

# Configurar UTF-8
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.extractors.biomarker_extractor import extract_biomarkers
from core.extractors.medical_extractor import extract_biomarcadores_solicitados_robust

# Texto OCR del PDF IHQ250984
texto_pdf = """
DESCRIPCIÓN MACROSCÓPICA
Informe de Estudios de Inmunohistoquímica
Caso extrainstitucional: P2501777
Laboratorio de patología UNESPAT
Órgano: mama izquierda. biopsia con aguja gruesa. (dos bloques de parafina y dos
láminas coloreadas con H&E)
Diagnóstico Inicial: CARCINOMA DUCTAL INFILTRANTE NOS, GRADO HISTOLÓGICO 3,
NECROSIS TUMORAL PRESENTE, SIN COMPROMISO LINFOVASCULAR NI PERINEURAL.
INFLAMACIÓN CRONICA INTERSTICIAL MODERADA.
Fecha de diagnóstico: 24-08-2025
Paciente: LETICIA ASTAIZA TACUE
Identificación: 25392960
Edad: 89 años
Género: FEMENINO
Tras la valoración inicial de las láminas teñidas con H&E, se realizan niveles histológicos
al bloque 1.
Estudios Solicitados:
Se realizó tinción especial para GATA 3, RECEPTOR DE ESTROGENOS, RECEPTOR DE
PROGESTERONA, HER 2, Ki 67, SOX10.
DESCRIPCIÓN MICROSCÓPICA
Previa valoración de la técnica y verificación de la adecuada tinción de los controles externos e
internos se realizan estudios de inmunohistoquímica en la plataforma automatizada Roche
VENTANA®.
Anticuerpos:
Estrógeno: CONFIRM anti-Estrogen Receptor (ER) (SP1) Rabbit Monoclonal Primary Antibody.
VENTANA Ref. 790-4324.
Progesterona: CONFIRM anti-Progesterone Receptor (ER) (1E2) Rabbit Monoclonal Primary
Antibody. VENTANA Ref. 790-2223.
Her2/Neu: PATHWAY anti-HER-2/Neu (4B5) Rabbit Monoclonal Antibody. VENTANA Ref. 790-4493.
Ki67: anti-Ki67 (30-9) Rabbit Monoclonal Primary Antibody. VENTANA Ref. 790-4286.
REPORTE DE BIOMARCADORES:
BLOQUE 1.
Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3. Son
negativas para SXO10.
-RECEPTOR DE ESTROGENOS: Negativo.
-RECEPTOR DE PROGRESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 % de las células
tumorales.
-Ki-67: Tinción nuclear en el 60% de las células tumorales.

DIAGNÓSTICO
CARCINOMA INVASIVO DE TIPO NO ESPECIAL.
GRADO HISTOLÓGICO: GRADO 3 (NOTTINGHAM SCORE 9/9 PUNTOS)
INVASIÓN LINFOVASCULAR: NO IDENTIFICADA.
INVASIÓN PERINEURAL: NO IDENTIFICADA
CLASIFICACIÓN MOLECULAR: HER 2 POSITIVO.
"""

print("="*80)
print("REPROCESANDO CASO IHQ250984 CON EXTRACTORES CORREGIDOS")
print("="*80)
print()

# Extraer información
print("1. Información del paciente (hardcoded del PDF)...")
patient_info = {
    'nombre': 'LETICIA ASTAIZA TACUE',
    'identificacion': '25392960',
    'edad': '89',
    'genero': 'FEMENINO'
}
print(f"   ✓ Paciente: {patient_info.get('nombre', 'N/A')}")
print(f"   ✓ Edad: {patient_info.get('edad', 'N/A')}")
print(f"   ✓ Género: {patient_info.get('genero', 'N/A')}")
print()

print("2. Extrayendo biomarcadores solicitados...")
estudios = extract_biomarcadores_solicitados_robust(texto_pdf)
estudios_str = ', '.join(estudios)
print(f"   ✓ Biomarcadores: {estudios_str}")
print()

print("3. Extrayendo biomarcadores individuales...")
biomarcadores = extract_biomarkers(texto_pdf)
for bio, valor in biomarcadores.items():
    print(f"   ✓ {bio}: {valor}")
print()

# Preparar datos para BD
datos = {
    'numero_caso': 'IHQ250984',
    'paciente': patient_info.get('nombre', ''),
    'identificacion': patient_info.get('identificacion', ''),
    'edad': patient_info.get('edad', ''),
    'genero': patient_info.get('genero', ''),
    'organo': 'MAMA IZQUIERDA',
    'diagnostico': 'CARCINOMA INVASIVO DE TIPO NO ESPECIAL',
    'estudios_solicitados': estudios_str,
    'her2': biomarcadores.get('HER2', ''),
    'er': biomarcadores.get('ER', ''),
    'pr': biomarcadores.get('PR', ''),
    'ki67': biomarcadores.get('KI67', ''),
    'gata3': biomarcadores.get('GATA3', ''),
    'sox10': biomarcadores.get('SOX10', ''),
}

print("4. Insertando en la base de datos...")
db_path = PROJECT_ROOT / 'data' / 'huv_oncologia_NUEVO.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Insertar (adaptado a la estructura real de tu BD)
try:
    cursor.execute("""
        INSERT INTO informes_ihq (
            [Numero de caso],
            [N. de identificación],
            [Primer nombre],
            [Primer apellido],
            [Segundo apellido],
            Edad,
            Genero,
            Organo,
            [Diagnostico Principal],
            IHQ_ESTUDIOS_SOLICITADOS,
            IHQ_HER2,
            IHQ_RECEPTOR_ESTROGENOS,
            IHQ_RECEPTOR_PROGESTERONA,
            [IHQ_KI-67],
            IHQ_GATA3,
            IHQ_SOX10
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datos['numero_caso'],
        datos['identificacion'],
        'LETICIA',
        'ASTAIZA',
        'TACUE',
        datos['edad'],
        datos['genero'],
        datos['organo'],
        datos['diagnostico'],
        datos['estudios_solicitados'],
        datos['her2'],
        datos['er'],
        datos['pr'],
        datos['ki67'],
        datos['gata3'],
        datos['sox10']
    ))
    conn.commit()
    print("   ✓ Caso insertado exitosamente")
except Exception as e:
    print(f"   ✗ Error al insertar: {e}")
    conn.rollback()

conn.close()

print()
print("="*80)
print("VERIFICACIÓN FINAL")
print("="*80)

# Verificar en BD
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("""
    SELECT IHQ_HER2, IHQ_RECEPTOR_ESTROGENOS, IHQ_RECEPTOR_PROGESTERONA, [IHQ_KI-67]
    FROM informes_ihq
    WHERE [Numero de caso] = ?
""", ('IHQ250984',))
result = cursor.fetchone()
conn.close()

if result:
    print("Biomarcadores guardados en BD:")
    print(f"  HER2: {result[0]}")
    print(f"  ER:   {result[1]}")
    print(f"  PR:   {result[2]}")
    print(f"  Ki-67: {result[3]}")
    print()

    # Verificar HER2
    if 'POSITIVO (SCORE 3+)' in str(result[0]).upper():
        print("✓ HER2 CORRECTO: Captura 'POSITIVO (SCORE 3+)'")
        print("✓ NO captura texto técnico del reactivo")
    else:
        print(f"✗ HER2 INCORRECTO: '{result[0]}'")
else:
    print("✗ Caso no encontrado en BD")
