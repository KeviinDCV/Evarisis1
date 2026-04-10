#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para procesar IHQ251030 y capturar debug output
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase, consolidate_ihq_content
from core.unified_extractor import unified_extractor
from core.debug_mapper import create_debug_map
from core.database_manager import DatabaseManager
import json

def main():
    print("=" * 80)
    print("Procesando IHQ251030")
    print("=" * 80)

    # 1. Extraer OCR del PDF
    pdf_path = 'pdfs_patologia/IHQ DEL 980 AL 1037.pdf'
    print(f"\n[1/5] Extrayendo OCR de {pdf_path}...")
    text = pdf_to_text_enhanced(pdf_path)

    # 2. Segmentar casos
    print("\n[2/5] Segmentando casos...")
    casos = segment_reports_multicase(text)

    # 3. Encontrar IHQ251030
    print("\n[3/5] Buscando IHQ251030...")
    caso = None
    for c in casos:
        if 'IHQ251030' in c:
            caso = c
            break

    if not caso:
        print("❌ No se encontró IHQ251030 en el PDF")
        return

    print("✅ Caso encontrado")

    # 4. Consolidar contenido
    print("\n[4/5] Consolidando contenido...")
    texto_consolidado = consolidate_ihq_content(caso, 'IHQ251030')

    # 5. Extraer datos
    print("\n[5/5] Ejecutando extractor...")
    print("-" * 80)
    resultado = unified_extractor(texto_consolidado)
    print("-" * 80)

    # Mostrar resultados relevantes
    print("\n" + "=" * 80)
    print("RESULTADOS")
    print("=" * 80)

    desc_macro = resultado.get('descripcion_macroscopica', '')
    desc_micro = resultado.get('descripcion_microscopica', '')

    print(f"\nDescripción Macroscópica ({len(desc_macro)} chars):")
    print(f"  Termina en: '{desc_macro[-50:] if desc_macro else 'N/A'}'")

    print(f"\nDescripción Microscópica ({len(desc_micro)} chars):")
    print(f"  Empieza con: '{desc_micro[:100] if desc_micro else 'N/A'}'")

    # Guardar debug_map
    print("\n[EXTRA] Guardando debug_map...")
    db_manager = DatabaseManager()
    create_debug_map(
        caso_numero='IHQ251030',
        ocr_result={'texto_consolidado': texto_consolidado},
        extracted_data=resultado,
        db_manager=db_manager,
        pdf_source=pdf_path
    )

    print("\n✅ Proceso completado")

if __name__ == '__main__':
    main()
