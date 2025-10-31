#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test rápido para verificar extracción de Diagnostico Principal en IHQ250988
UBICACIÓN: LEGACY/ - Script temporal de testing
"""

import sys
import os

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.unified_extractor import extract_ihq_data
from core.database_manager import init_db, save_record_to_db
import json
import pytesseract
from pdf2image import convert_from_path

def test_ihq250988():
    """Procesa IHQ250988 y verifica Diagnostico Principal"""
    
    print("\n" + "="*80)
    print("TEST: Extracción de Diagnostico Principal - IHQ250988")
    print("="*80)
    
    # Inicializar BD
    init_db()
    
    # Procesar PDF
    pdf_path = "pdfs_patologia/ordenamientos.pdf"
    print(f"\n📄 Procesando: {pdf_path}")
    
    try:
        # Convertir PDF a imágenes y hacer OCR
        images = convert_from_path(pdf_path, dpi=300)
        full_text = ""
        for img in images:
            full_text += pytesseract.image_to_string(img, lang='spa') + "\n"
        
        # Extraer datos
        result = extract_ihq_data(full_text)
        
        if result:
            print(f"\n✅ Extracción exitosa")
            print(f"\n📊 Número de petición: {result.get('numero_peticion', 'N/A')}")
            
            # VERIFICAR DIAGNOSTICO PRINCIPAL
            diagnostico_principal = result.get('Diagnostico Principal', 'N/A')
            print(f"\n🔍 Diagnostico Principal extraído:")
            print(f"   {diagnostico_principal}")
            
            # Mostrar diagnóstico completo para comparar
            diagnostico_completo = result.get('diagnostico', 'N/A')
            print(f"\n📝 Diagnóstico completo (primeras 200 chars):")
            print(f"   {diagnostico_completo[:200]}...")
            
            # Verificar si contiene "LINFOMA"
            if "LINFOMA" in diagnostico_principal:
                print(f"\n✅ ¡ÉXITO! Diagnóstico Principal contiene 'LINFOMA'")
            else:
                print(f"\n❌ FALLO: Diagnóstico Principal NO contiene 'LINFOMA'")
                print(f"   Diagnóstico completo: {diagnostico_completo}")
            
            # Guardar en BD
            save_record_to_db(result)
            print(f"\n💾 Registro guardado en BD")
            
            # Mostrar JSON completo para debug
            print(f"\n📋 Datos completos extraídos:")
            print(json.dumps({
                'numero_peticion': result.get('numero_peticion'),
                'Diagnostico Principal': diagnostico_principal,
                'IHQ_CD3': result.get('IHQ_CD3'),
                'IHQ_P53': result.get('IHQ_P53'),
                'IHQ_KI-67': result.get('IHQ_KI-67')
            }, indent=2, ensure_ascii=False))
            
        else:
            print(f"\n❌ No se pudo extraer información del PDF")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ihq250988()
