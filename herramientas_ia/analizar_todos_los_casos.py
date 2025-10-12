#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis COMPLETO de TODOS los 50 registros de la BD
Identifica patrones de éxito y problemas en cada caso
"""
import sys
import os
import sqlite3
from pathlib import Path
import json

# Configurar UTF-8
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Rutas
PROYECTO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROYECTO_ROOT))
DB_PATH = PROYECTO_ROOT / 'data' / 'huv_oncologia_NUEVO.db'

def analizar_caso_detallado(row, index):
    """Análisis detallado de un caso individual"""
    (ihq, nombre_completo, edad, genero, eps, servicio, medico, organo, 
     diag_principal, desc_diag, desc_micro, desc_macro, malignidad, 
     factor_pron, her2, ki67, re, rp, pdl1, p16, p40, p53) = row
    
    analisis = {
        'index': index,
        'ihq': ihq,
        'campos_demograficos': {},
        'campos_medicos': {},
        'biomarcadores': {},
        'calidad': {},
        'patrones': [],
        'problemas': [],
        'necesita_ia': False,
        'nivel_confianza': 'HIGH'
    }
    
    # === ANÁLISIS DEMOGRÁFICO ===
    analisis['campos_demograficos'] = {
        'nombre': {'valor': nombre_completo, 'ok': bool(nombre_completo and nombre_completo not in ['N/A', '', 'None'])},
        'edad': {'valor': edad, 'ok': bool(edad and edad not in ['N/A', '', 'None'])},
        'genero': {'valor': genero, 'ok': bool(genero and genero not in ['N/A', '', 'None'])},
        'eps': {'valor': eps, 'ok': bool(eps and eps not in ['N/A', '', 'None'])},
        'servicio': {'valor': servicio, 'ok': bool(servicio and servicio not in ['N/A', '', 'None'])},
        'medico': {'valor': medico, 'ok': bool(medico and medico not in ['N/A', '', 'None'])}
    }
    
    demo_score = sum(1 for v in analisis['campos_demograficos'].values() if v['ok']) / len(analisis['campos_demograficos']) * 100
    
    # === ANÁLISIS MÉDICO ===
    analisis['campos_medicos'] = {
        'organo': {
            'valor': organo,
            'ok': bool(organo and organo not in ['N/A', '', 'None']),
            'longitud': len(organo) if organo else 0
        },
        'diagnostico_principal': {
            'valor': diag_principal,
            'ok': bool(diag_principal and diag_principal not in ['N/A', '', 'None']),
            'longitud': len(diag_principal) if diag_principal else 0,
            'tiene_keywords': False
        },
        'descripcion_diagnostico': {
            'valor': desc_diag,
            'ok': bool(desc_diag and len(desc_diag) > 20),
            'longitud': len(desc_diag) if desc_diag else 0
        },
        'descripcion_micro': {
            'valor': desc_micro,
            'ok': bool(desc_micro and len(desc_micro) > 20),
            'longitud': len(desc_micro) if desc_micro else 0
        },
        'descripcion_macro': {
            'valor': desc_macro,
            'ok': bool(desc_macro and len(desc_macro) > 20),
            'longitud': len(desc_macro) if desc_macro else 0
        },
        'malignidad': {
            'valor': malignidad,
            'ok': bool(malignidad and malignidad not in ['N/A', '', 'None', 'NO_DETERMINADO']),
            'es_maligno': malignidad == 'MALIGNO',
            'es_benigno': malignidad == 'BENIGNO',
            'no_determinado': malignidad == 'NO_DETERMINADO'
        },
        'factor_pronostico': {
            'valor': factor_pron,
            'ok': bool(factor_pron and factor_pron not in ['N/A', '', 'None']),
            'longitud': len(factor_pron) if factor_pron else 0
        }
    }
    
    # Detectar keywords en diagnóstico
    if diag_principal:
        keywords_oncologicos = ['CARCINOMA', 'ADENOCARCINOMA', 'SARCOMA', 'MELANOMA', 'LINFOMA', 'TUMOR', 'NEOPLASIA']
        analisis['campos_medicos']['diagnostico_principal']['tiene_keywords'] = any(kw in diag_principal.upper() for kw in keywords_oncologicos)
    
    med_score = sum(1 for v in analisis['campos_medicos'].values() if isinstance(v, dict) and v.get('ok', False)) / len(analisis['campos_medicos']) * 100
    
    # === ANÁLISIS BIOMARCADORES ===
    analisis['biomarcadores'] = {
        'HER2': {'valor': her2, 'ok': bool(her2 and her2 not in ['N/A', '', 'None'])},
        'Ki67': {'valor': ki67, 'ok': bool(ki67 and ki67 not in ['N/A', '', 'None'])},
        'RE': {'valor': re, 'ok': bool(re and re not in ['N/A', '', 'None'])},
        'RP': {'valor': rp, 'ok': bool(rp and rp not in ['N/A', '', 'None'])},
        'PDL1': {'valor': pdl1, 'ok': bool(pdl1 and pdl1 not in ['N/A', '', 'None'])},
        'P16': {'valor': p16, 'ok': bool(p16 and p16 not in ['N/A', '', 'None'])},
        'P40': {'valor': p40, 'ok': bool(p40 and p40 not in ['N/A', '', 'None'])},
        'P53': {'valor': p53, 'ok': bool(p53 and p53 not in ['N/A', '', 'None'])}
    }
    
    bio_score = sum(1 for v in analisis['biomarcadores'].values() if v['ok']) / len(analisis['biomarcadores']) * 100
    
    # === DETECCIÓN DE PATRONES ===
    
    # PATRÓN 1: Caso perfecto
    if demo_score == 100 and med_score >= 85 and bio_score >= 50:
        analisis['patrones'].append('CASO_PERFECTO')
        analisis['nivel_confianza'] = 'HIGH'
    
    # PATRÓN 2: Diagnóstico vacío con descripción
    if not analisis['campos_medicos']['diagnostico_principal']['ok'] and analisis['campos_medicos']['descripcion_diagnostico']['ok']:
        analisis['patrones'].append('DIAG_VACÍO_CON_DESC')
        analisis['problemas'].append('Diagnóstico principal vacío pero hay descripción diagnóstico')
        analisis['necesita_ia'] = True
        analisis['nivel_confianza'] = 'LOW'
    
    # PATRÓN 3: Diagnóstico muy corto
    if analisis['campos_medicos']['diagnostico_principal']['ok']:
        if analisis['campos_medicos']['diagnostico_principal']['longitud'] < 10:
            keywords_validos = ['BENIGNO', 'MALIGNO', 'TUMOR', 'GIST', 'MELANOMA']
            if diag_principal.upper() not in keywords_validos:
                analisis['patrones'].append('DIAG_MUY_CORTO')
                analisis['problemas'].append(f'Diagnóstico muy corto: {diag_principal}')
                analisis['necesita_ia'] = True
    
    # PATRÓN 4: Diagnóstico con texto explicativo
    if diag_principal:
        keywords_explicativos = ['SIN EMBARGO', 'SE REALIZARON', 'SE SUGIERE', 'A CRITERIO', 'VER COMENTARIO']
        if any(kw in diag_principal.upper() for kw in keywords_explicativos):
            analisis['patrones'].append('DIAG_CON_EXPLICACIÓN')
            analisis['problemas'].append('Diagnóstico contiene texto explicativo')
            analisis['necesita_ia'] = True
    
    # PATRÓN 5: Diagnóstico = Descripción completa
    if diag_principal and desc_diag:
        if diag_principal == desc_diag and len(diag_principal) > 200:
            analisis['patrones'].append('DIAG_SIN_EXTRAER')
            analisis['problemas'].append('Diagnóstico no está extraído de la descripción')
            analisis['necesita_ia'] = True
    
    # PATRÓN 6: Malignidad no determinada
    if analisis['campos_medicos']['malignidad']['no_determinado']:
        analisis['patrones'].append('MALIGNIDAD_NO_DET')
        analisis['problemas'].append('Malignidad NO_DETERMINADO')
        analisis['necesita_ia'] = True
    
    # PATRÓN 7: Factor pronóstico mencionado pero no extraído
    if not analisis['campos_medicos']['factor_pronostico']['ok'] and desc_micro:
        keywords_fp = ['KI-67', 'KI67', 'P53', 'GRADO']
        if any(kw in desc_micro.upper() for kw in keywords_fp):
            analisis['patrones'].append('FACTOR_PRON_NO_EXTRAÍDO')
            analisis['problemas'].append('Factor pronóstico mencionado en descripción pero no extraído')
    
    # PATRÓN 8: Biomarcadores mencionados pero no extraídos
    if bio_score == 0 and desc_micro:
        keywords_bio = ['HER2', 'KI-67', 'RE:', 'RP:', 'RECEPTOR']
        if any(kw in desc_micro.upper() for kw in keywords_bio):
            analisis['patrones'].append('BIOMARCADORES_NO_EXTRAÍDOS')
            analisis['problemas'].append('Biomarcadores mencionados pero no extraídos')
    
    # PATRÓN 9: Caso bien mapeado con biomarcadores completos
    if demo_score >= 80 and med_score >= 80 and bio_score >= 75:
        analisis['patrones'].append('CASO_COMPLETO_BIOMARCADORES')
        analisis['nivel_confianza'] = 'HIGH'
    
    # PATRÓN 10: Caso bien mapeado sin biomarcadores
    if demo_score >= 80 and med_score >= 80 and bio_score < 25:
        analisis['patrones'].append('CASO_COMPLETO_SIN_BIOMARCADORES')
    
    # === SCORES FINALES ===
    analisis['calidad'] = {
        'score_demografico': round(demo_score, 2),
        'score_medico': round(med_score, 2),
        'score_biomarcadores': round(bio_score, 2),
        'score_total': round((demo_score * 0.3 + med_score * 0.5 + bio_score * 0.2), 2)
    }
    
    return analisis

def main():
    print("="*100)
    print("🔍 ANÁLISIS EXHAUSTIVO DE TODOS LOS 50 REGISTROS")
    print("="*100)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener TODOS los registros con todos los campos necesarios
    cursor.execute('''
        SELECT 
            "N. peticion (0. Numero de biopsia)",
            "Primer nombre" || ' ' || "Primer apellido" as nombre_completo,
            "Edad",
            "Genero",
            "EPS",
            "Servicio",
            "Médico tratante",
            "Organo (1. Muestra enviada a patología)",
            "Diagnostico Principal",
            "Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)",
            "Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)",
            "Descripcion macroscopica",
            "Malignidad",
            "Factor pronostico",
            "IHQ_HER2",
            "IHQ_KI-67",
            "IHQ_RECEPTOR_ESTROGENO",
            "IHQ_RECEPTOR_PROGESTERONOS",
            "IHQ_PDL-1",
            "IHQ_P16_ESTADO",
            "IHQ_P40_ESTADO",
            "IHQ_P53"
        FROM informes_ihq
        ORDER BY id
    ''')
    
    registros = cursor.fetchall()
    
    print(f"\n📊 Total de registros a analizar: {len(registros)}")
    print("\n" + "="*100)
    
    # Analizar TODOS los registros
    todos_analisis = []
    
    for idx, row in enumerate(registros, 1):
        analisis = analizar_caso_detallado(row, idx)
        todos_analisis.append(analisis)
    
    # ========== REPORTES ==========
    
    # REPORTE 1: Distribución por Patrones
    print("\n📊 DISTRIBUCIÓN POR PATRONES")
    print("="*100)
    
    patrones_count = {}
    for analisis in todos_analisis:
        for patron in analisis['patrones']:
            patrones_count[patron] = patrones_count.get(patron, 0) + 1
    
    for patron, count in sorted(patrones_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {patron:40} {count:3} casos ({count/len(registros)*100:5.1f}%)")
    
    # REPORTE 2: Distribución por Scores
    print("\n📊 DISTRIBUCIÓN POR CALIDAD")
    print("="*100)
    
    scores_rangos = {
        '95-100% (Excelente)': 0,
        '85-94% (Muy Bueno)': 0,
        '70-84% (Bueno)': 0,
        '50-69% (Regular)': 0,
        '0-49% (Malo)': 0
    }
    
    for analisis in todos_analisis:
        score = analisis['calidad']['score_total']
        if score >= 95:
            scores_rangos['95-100% (Excelente)'] += 1
        elif score >= 85:
            scores_rangos['85-94% (Muy Bueno)'] += 1
        elif score >= 70:
            scores_rangos['70-84% (Bueno)'] += 1
        elif score >= 50:
            scores_rangos['50-69% (Regular)'] += 1
        else:
            scores_rangos['0-49% (Malo)'] += 1
    
    for rango, count in scores_rangos.items():
        print(f"  {rango:30} {count:3} casos ({count/len(registros)*100:5.1f}%)")
    
    # REPORTE 3: Casos que NO necesitan IA (Alta Confianza)
    print("\n✅ CASOS QUE NO NECESITAN IA (Alta Confianza)")
    print("="*100)
    
    casos_no_ia = [a for a in todos_analisis if not a['necesita_ia'] and a['nivel_confianza'] == 'HIGH']
    print(f"Total: {len(casos_no_ia)} casos ({len(casos_no_ia)/len(registros)*100:.1f}%)")
    
    if len(casos_no_ia) > 0:
        print("\nPrimeros 10 ejemplos:")
        for analisis in casos_no_ia[:10]:
            print(f"  {analisis['ihq']} - Score: {analisis['calidad']['score_total']:.1f}% - Patrones: {', '.join(analisis['patrones'][:2])}")
    
    # REPORTE 4: Casos que SÍ necesitan IA
    print("\n⚠️ CASOS QUE NECESITAN IA")
    print("="*100)
    
    casos_necesitan_ia = [a for a in todos_analisis if a['necesita_ia']]
    print(f"Total: {len(casos_necesitan_ia)} casos ({len(casos_necesitan_ia)/len(registros)*100:.1f}%)")
    
    for i, analisis in enumerate(casos_necesitan_ia, 1):
        print(f"\n{i}. {analisis['ihq']} - Score: {analisis['calidad']['score_total']:.1f}% - Confianza: {analisis['nivel_confianza']}")
        print(f"   Patrones: {', '.join(analisis['patrones'])}")
        print(f"   Problemas:")
        for prob in analisis['problemas']:
            print(f"     • {prob}")
    
    # REPORTE 5: Análisis Detallado de Scores
    print("\n📊 ANÁLISIS DETALLADO DE SCORES (Todos los casos)")
    print("="*100)
    
    scores_demo = [a['calidad']['score_demografico'] for a in todos_analisis]
    scores_med = [a['calidad']['score_medico'] for a in todos_analisis]
    scores_bio = [a['calidad']['score_biomarcadores'] for a in todos_analisis]
    scores_total = [a['calidad']['score_total'] for a in todos_analisis]
    
    print(f"\nScore Demográfico:")
    print(f"  Promedio: {sum(scores_demo)/len(scores_demo):.1f}%")
    print(f"  Máximo: {max(scores_demo):.1f}%")
    print(f"  Mínimo: {min(scores_demo):.1f}%")
    
    print(f"\nScore Médico:")
    print(f"  Promedio: {sum(scores_med)/len(scores_med):.1f}%")
    print(f"  Máximo: {max(scores_med):.1f}%")
    print(f"  Mínimo: {min(scores_med):.1f}%")
    
    print(f"\nScore Biomarcadores:")
    print(f"  Promedio: {sum(scores_bio)/len(scores_bio):.1f}%")
    print(f"  Máximo: {max(scores_bio):.1f}%")
    print(f"  Mínimo: {min(scores_bio):.1f}%")
    
    print(f"\nScore Total:")
    print(f"  Promedio: {sum(scores_total)/len(scores_total):.1f}%")
    print(f"  Máximo: {max(scores_total):.1f}%")
    print(f"  Mínimo: {min(scores_total):.1f}%")
    
    # REPORTE 6: Exportar JSON completo
    output_data = {
        'fecha_analisis': '2025-10-05',
        'total_casos': len(registros),
        'estadisticas': {
            'casos_no_necesitan_ia': len(casos_no_ia),
            'casos_necesitan_ia': len(casos_necesitan_ia),
            'porcentaje_necesita_ia': round(len(casos_necesitan_ia)/len(registros)*100, 2),
            'scores_promedios': {
                'demografico': round(sum(scores_demo)/len(scores_demo), 2),
                'medico': round(sum(scores_med)/len(scores_med), 2),
                'biomarcadores': round(sum(scores_bio)/len(scores_bio), 2),
                'total': round(sum(scores_total)/len(scores_total), 2)
            }
        },
        'patrones_detectados': patrones_count,
        'todos_los_casos': todos_analisis
    }
    
    output_file = PROYECTO_ROOT / 'herramientas_ia' / 'resultados' / 'analisis_completo_50_casos.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 JSON COMPLETO EXPORTADO:")
    print(f"   {output_file}")
    print(f"   Contiene análisis detallado de los 50 casos")
    
    conn.close()
    
    print("\n" + "="*100)
    print("✅ ANÁLISIS COMPLETO FINALIZADO")
    print("="*100)

if __name__ == '__main__':
    main()
