#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de correcciones para IHQ250984
Simula procesamiento del PDF con extractores corregidos
"""

import sys
import io
from pathlib import Path

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.extractors.biomarker_extractor import extract_biomarkers
from core.extractors.medical_extractor import extract_biomarcadores_solicitados_robust

# Texto OCR del PDF IHQ250984 (sección relevante)
texto_pdf = """
DESCRIPCIÓN MACROSCÓPICA
Informe de Estudios de Inmunohistoquímica
Caso extrainstitucional: P2501777
Laboratorio de patología UNESPAT
Órgano: mama izquierda. biopsia con aguda gruesa. (dos bloques de parafina y dos
láminas coloreadas con H&E)
Diagnóstico Inicial: CARCINOMA DUCTAL INFILTRANTE NOS, GRADO HISTOLÓGICO 3,
NECROSIS TUMORAL PRESENTE, SIN COMPROMISO LINFOVASCULAR NI PERINEURAL.
INFLAMACIÓN CRONICA INTERSTICIAL MODERADA.
Fecha de diagnóstico: 24-08-2025
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
"""

print("="*80)
print("TEST DE CORRECCIONES - IHQ250984")
print("="*80)
print()

# Test 1: Extracción de estudios solicitados
print("1. TEST: IHQ_ESTUDIOS_SOLICITADOS")
print("-" * 80)
estudios = extract_biomarcadores_solicitados_robust(texto_pdf)
print(f"Biomarcadores detectados: {len(estudios)}")
for i, bio in enumerate(estudios, 1):
    print(f"  {i}. {bio}")
print()
print(f"RESULTADO: {'✓ CORRECTO' if len(estudios) == 6 else '✗ INCORRECTO'} (esperado: 6 biomarcadores)")
print()

# Test 2: Extracción de biomarcadores individuales
print("2. TEST: BIOMARCADORES INDIVIDUALES")
print("-" * 80)
biomarcadores = extract_biomarkers(texto_pdf)

# Valores esperados (usando claves correctas del sistema)
esperados = {
    'ER': 'NEGATIVO',
    'PR': 'NEGATIVO',
    'HER2': 'POSITIVO (SCORE 3+)',
    'KI67': '60%',
    'GATA3': 'POSITIVO',
    'SOX10': 'NEGATIVO'
}

correctos = 0
total = len(esperados)

for bio_key, valor_esperado in esperados.items():
    valor_obtenido = biomarcadores.get(bio_key, 'N/A')
    es_correcto = False

    # Comparación flexible
    if valor_esperado == 'N/A' and not valor_obtenido:
        es_correcto = True
    elif valor_esperado.upper() in str(valor_obtenido).upper():
        es_correcto = True
    elif valor_esperado == '60%' and '60' in str(valor_obtenido):
        es_correcto = True

    if es_correcto:
        correctos += 1
        status = "✓"
    else:
        status = "✗"

    print(f"{status} {bio_key:25} | Esperado: {valor_esperado:25} | Obtenido: {valor_obtenido}")

print()
score = (correctos / total) * 100
print(f"SCORE: {score:.1f}% ({correctos}/{total} correctos)")
print()

# Resumen final
print("="*80)
print("RESUMEN")
print("="*80)
if score >= 83.3:
    print("✓ APROBADO - Las correcciones funcionan correctamente")
    print(f"  Score: {score:.1f}% >= 83.3% (objetivo)")
else:
    print("✗ RECHAZADO - Las correcciones NO alcanzan el objetivo")
    print(f"  Score: {score:.1f}% < 83.3% (objetivo)")
print()

# Detalles de problemas
if score < 100:
    print("PROBLEMAS DETECTADOS:")
    for bio_key, valor_esperado in esperados.items():
        valor_obtenido = biomarcadores.get(bio_key, 'N/A')
        if valor_esperado.upper() not in str(valor_obtenido).upper():
            if not (valor_esperado == '60%' and '60' in str(valor_obtenido)):
                print(f"  - {bio_key}: '{valor_obtenido}' != '{valor_esperado}'")
