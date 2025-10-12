#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✅ VALIDADOR DE EXTRACCIÓN - Gestor Oncología HUV
=================================================

Valida la extracción de datos de PDFs comparando con la base de datos.
Útil para verificar que los extractores funcionan correctamente.

Autor: Sistema EVARISIS
Fecha: 4 de octubre de 2025
Versión: 4.2.1
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.database_manager import DB_FILE, get_connection
    from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase
    from core.extractors.patient_extractor import extract_patient_data
    from core.extractors.medical_extractor import extract_medical_data
    from core.extractors.biomarker_extractor import extract_biomarkers
    from core.unified_extractor import extract_ihq_data
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)


def normalizar_valor(valor: Any) -> str:
    """Normaliza un valor para comparación"""
    if valor is None or valor == '':
        return ''
    return str(valor).strip().upper()


def similitud_texto(texto1: str, texto2: str) -> float:
    """Calcula similitud entre dos textos (0.0 - 1.0)"""
    return SequenceMatcher(None, normalizar_valor(texto1), normalizar_valor(texto2)).ratio()


def obtener_datos_bd(ihq_numero: str) -> Dict[str, Any]:
    """Obtiene datos de un caso IHQ desde la base de datos"""
    conn = get_connection(DB_FILE)
    cursor = conn.cursor()

    # Buscar por número de petición
    query = f"""
        SELECT * FROM ihq_data
        WHERE `N. peticion (0. Numero de biopsia)` LIKE ?
    """

    cursor.execute(query, (f"%{ihq_numero}%",))
    row = cursor.fetchone()

    if not row:
        return {}

    # Convertir a diccionario
    columns = [description[0] for description in cursor.description]
    datos = dict(zip(columns, row))

    conn.close()
    return datos


def extraer_de_pdf(pdf_path: str, ihq_numero: str) -> Dict[str, Any]:
    """Extrae datos de un PDF para un caso IHQ específico"""
    # OCR del PDF
    full_text = pdf_to_text_enhanced(pdf_path)

    # Segmentar reportes
    segments = segment_reports_multicase(full_text)

    # Buscar el segmento con el IHQ solicitado
    target_segment = None
    for segment in segments:
        if f"IHQ{ihq_numero}" in segment or f"IHQ {ihq_numero}" in segment:
            target_segment = segment
            break

    if not target_segment:
        return {}

    # Extraer datos del segmento
    datos_extraidos = extract_ihq_data(target_segment)

    return datos_extraidos


def comparar_campos(bd_data: Dict, pdf_data: Dict, campos: List[str] = None) -> List[Tuple[str, str, str, float]]:
    """Compara campos entre BD y PDF

    Returns:
        Lista de tuplas (campo, valor_bd, valor_pdf, similitud)
    """
    diferencias = []

    # Si no se especifican campos, usar los campos principales
    if not campos:
        campos = [
            'N. peticion (0. Numero de biopsia)',
            'Primer nombre', 'Segundo nombre', 'Primer apellido', 'Segundo apellido',
            'N. de identificación', 'Genero', 'Edad',
            'Órgano (tabla)', 'IHQ_ORGANO',
            'Diagnóstico (2. Diagnóstico final)', 'Factor pronóstico',
            'IHQ_RECEPTOR_ESTROGENO', 'IHQ_RECEPTOR_PROGESTERONOS', 'IHQ_HER2', 'IHQ_KI-67'
        ]

    for campo in campos:
        valor_bd = bd_data.get(campo, '')
        valor_pdf = pdf_data.get(campo, '')

        sim = similitud_texto(valor_bd, valor_pdf)

        diferencias.append((campo, valor_bd, valor_pdf, sim))

    return diferencias


def generar_reporte_validacion(ihq_numero: str, diferencias: List[Tuple], solo_diferencias: bool = False):
    """Genera reporte de validación"""
    print("=" * 100)
    print(f"📋 REPORTE DE VALIDACIÓN - IHQ{ihq_numero}")
    print("=" * 100)

    total_campos = len(diferencias)
    campos_identicos = sum(1 for _, _, _, sim in diferencias if sim >= 0.95)
    campos_similares = sum(1 for _, _, _, sim in diferencias if 0.7 <= sim < 0.95)
    campos_diferentes = sum(1 for _, _, _, sim in diferencias if sim < 0.7)

    print(f"\n📊 Resumen:")
    print(f"   Total de campos: {total_campos}")
    print(f"   ✅ Idénticos (>=95%): {campos_identicos}")
    print(f"   ⚠️  Similares (70-95%): {campos_similares}")
    print(f"   ❌ Diferentes (<70%): {campos_diferentes}")
    print(f"   📈 Precisión general: {(campos_identicos / total_campos * 100):.1f}%")

    print(f"\n{'Campo':<40} {'BD':<25} {'PDF':<25} {'Simil.':<8}")
    print("-" * 100)

    for campo, val_bd, val_pdf, sim in sorted(diferencias, key=lambda x: x[3]):
        # Truncar valores largos
        val_bd_str = str(val_bd)[:22] + "..." if len(str(val_bd)) > 25 else str(val_bd)
        val_pdf_str = str(val_pdf)[:22] + "..." if len(str(val_pdf)) > 25 else str(val_pdf)

        # Determinar símbolo
        if sim >= 0.95:
            simbolo = "✅"
        elif sim >= 0.7:
            simbolo = "⚠️ "
        else:
            simbolo = "❌"

        # Filtrar por solo diferencias si se solicita
        if solo_diferencias and sim >= 0.95:
            continue

        print(f"{simbolo} {campo:<38} {val_bd_str:<25} {val_pdf_str:<25} {sim*100:>6.1f}%")

    print("=" * 100)


def validar_caso_completo(ihq_numero: str, pdf_path: str = None, solo_diferencias: bool = False, generar_reporte: bool = False, campos_especificos: List[str] = None):
    """Valida un caso IHQ completo"""

    print(f"🔍 Validando caso IHQ{ihq_numero}...")

    # 1. Obtener datos de BD
    print("📚 Obteniendo datos de la base de datos...")
    bd_data = obtener_datos_bd(ihq_numero)

    if not bd_data:
        print(f"❌ No se encontró el caso IHQ{ihq_numero} en la base de datos")
        return

    print(f"   ✅ Encontrado en BD: {bd_data.get('Primer nombre', '')} {bd_data.get('Primer apellido', '')}")

    # 2. Extraer de PDF si se proporciona
    pdf_data = {}
    if pdf_path:
        print(f"📄 Extrayendo datos del PDF: {pdf_path}...")
        pdf_data = extraer_de_pdf(pdf_path, ihq_numero)

        if not pdf_data:
            print(f"❌ No se pudo extraer el caso IHQ{ihq_numero} del PDF")
            return

        print(f"   ✅ Datos extraídos del PDF")

    # 3. Comparar
    print("🔬 Comparando datos...")
    diferencias = comparar_campos(bd_data, pdf_data, campos_especificos)

    # 4. Generar reporte
    generar_reporte_validacion(ihq_numero, diferencias, solo_diferencias)

    # 5. Guardar reporte si se solicita
    if generar_reporte and pdf_path:
        reporte_file = Path(f"validacion_IHQ{ihq_numero}_{Path(pdf_path).stem}.json")
        reporte_data = {
            'ihq': ihq_numero,
            'pdf': pdf_path,
            'bd_data': {k: str(v) for k, v in bd_data.items()},
            'pdf_data': {k: str(v) for k, v in pdf_data.items()},
            'diferencias': [
                {'campo': campo, 'bd': str(val_bd), 'pdf': str(val_pdf), 'similitud': sim}
                for campo, val_bd, val_pdf, sim in diferencias
            ]
        }

        with open(reporte_file, 'w', encoding='utf-8') as f:
            json.dump(reporte_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Reporte guardado en: {reporte_file}")


def main():
    parser = argparse.ArgumentParser(
        description="✅ Validador de Extracción - Gestor Oncología HUV",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--ihq', required=True, help='Número de petición IHQ (ej: 250001)')
    parser.add_argument('--pdf', help='Archivo PDF para extraer y comparar')
    parser.add_argument('--completo', action='store_true', help='Validar todos los campos')
    parser.add_argument('--solo-diferencias', action='store_true', help='Mostrar solo diferencias')
    parser.add_argument('--reporte', action='store_true', help='Generar reporte JSON')
    parser.add_argument('--campos', nargs='+', help='Validar campos específicos')

    args = parser.parse_args()

    # Limpiar número IHQ
    ihq_numero = args.ihq.replace('IHQ', '').replace('ihq', '').strip()

    try:
        validar_caso_completo(
            ihq_numero=ihq_numero,
            pdf_path=args.pdf,
            solo_diferencias=args.solo_diferencias,
            generar_reporte=args.reporte,
            campos_especificos=args.campos
        )
    except Exception as e:
        print(f"❌ Error durante la validación: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
