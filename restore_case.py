import os
import sys
import re
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(r'c:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA')
sys.path.insert(0, str(PROJECT_ROOT))

# Save original stdout
original_stdout = sys.__stdout__

def log(msg):
    try:
        if not sys.stdout.closed:
            print(msg)
        else:
            original_stdout.write(str(msg) + "\n")
            original_stdout.flush()
    except:
        try:
            original_stdout.write(str(msg) + "\n")
            original_stdout.flush()
        except:
            pass

from core.processors.ocr_processor import pdf_to_text_enhanced, segment_reports_multicase
from core.unified_extractor import extract_ihq_data, map_to_database_format
from core.database_manager import save_records, get_registro_by_peticion
from core.debug_mapper import DebugMapper

def restore_ihq250133():
    pdf_path = str(PROJECT_ROOT / 'pdfs_patologia' / 'IHQ DEL 108 AL 159.pdf')
    target_case = "IHQ250133"
    target_page = 46

    log(f"🚀 Restoring {target_case} from {pdf_path} (Page {target_page})...")

    import fitz
    doc = fitz.open(pdf_path)
    page = doc.load_page(target_page - 1)
    text_native = page.get_text("text")
    doc.close()
    
    if len(text_native.strip()) < 100:
        log("⚠️ Native text insufficient, using full extraction...")
        full_text = pdf_to_text_enhanced(pdf_path)
    else:
        full_text = f"--- PÁGINA {target_page} ---\n" + text_native

    segmentos = segment_reports_multicase(full_text)
    case_segment = None
    for seg in segmentos:
        if target_case in seg:
            case_segment = seg
            break
    
    if not case_segment:
        log(f"❌ Could not find segment for {target_case}.")
        return False

    log("🔍 Extracting medical data...")
    mapper = DebugMapper()
    mapper.iniciar_sesion(target_case, pdf_path)
    
    mapper.registrar_ocr(
        texto_original=full_text,
        texto_consolidado=case_segment,
        metadata={'pdf_path': pdf_path, 'numero_ihq': target_case, 'restored': True}
    )

    datos_extraidos = extract_ihq_data(case_segment)
    mapper.registrar_extractor("unified", datos_extraidos)

    datos_mapeados = map_to_database_format(datos_extraidos)
    
    log("💾 Saving to database...")
    try:
        count = save_records([datos_mapeados])
        if count > 0:
            log("✅ Record successfully saved.")
        else:
            log("⚠️ Warning: No records saved.")
    except Exception as e:
        log(f"❌ Error during save: {e}")
        return False

    datos_bd = get_registro_by_peticion(target_case)
    if datos_bd:
        mapper.registrar_base_datos(datos_bd)
        map_path = mapper.guardar_mapa()
        log(f"✅ Debug map generated: {map_path}")
        return True
    else:
        log("❌ Failed to retrieve saved data.")
        return False

if __name__ == "__main__":
    try:
        success = restore_ihq250133()
        if success:
            log("\n🎉 Restoration completed successfully.")
            sys.exit(0)
        else:
            log("\n❌ Restoration failed.")
            sys.exit(1)
    except Exception as e:
        log(f"\n💥 Fatal error: {e}")
        sys.exit(1)
