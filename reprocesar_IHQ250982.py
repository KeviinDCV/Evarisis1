#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script temporal para reprocesar caso IHQ250982 con correcciones v6.0.3"""

import sys
import logging
from pathlib import Path

# Configurar logging (DEBUG temporal para investigación)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Agregar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database_manager import init_db, save_records
from core.unified_extractor import extract_ihq_data, map_to_database_format
import json

def reprocesar_caso_ihq250982():
    """Reprocesa el caso IHQ250982 con las correcciones v6.0.3"""

    # Inicializar BD
    logger.info("Inicializando base de datos...")
    init_db()

    # Leer debug map que ya tiene el texto extraído
    debug_map_path = Path("data/debug_maps/debug_map_IHQ250982_20251023_013556.json")

    if not debug_map_path.exists():
        logger.error(f"Debug map no encontrado: {debug_map_path}")
        logger.info("Intentando buscar otro debug map...")

        # Buscar cualquier debug map de IHQ250982
        import glob
        debug_maps = glob.glob("data/debug_maps/debug_map_IHQ250982_*.json")
        if not debug_maps:
            logger.error("No se encontró ningún debug map para IHQ250982")
            return False

        debug_map_path = Path(debug_maps[0])
        logger.info(f"Usando debug map: {debug_map_path}")

    logger.info(f"Leyendo debug map: {debug_map_path}")

    # Leer el debug map
    with open(debug_map_path, 'r', encoding='utf-8') as f:
        debug_data = json.load(f)

    texto_caso = debug_data.get('ocr', {}).get('texto_original', '')

    if not texto_caso:
        logger.error("No se encontró texto en el debug map")
        return False

    # Extraer solo la sección del caso IHQ250982
    inicio = texto_caso.find("IHQ250982")
    siguiente_caso = texto_caso.find("IHQ250983", inicio)

    if siguiente_caso == -1:
        texto_caso = texto_caso[inicio:]
    else:
        texto_caso = texto_caso[inicio:siguiente_caso]

    logger.info(f"Texto del caso IHQ250982: {len(texto_caso)} caracteres")

    # Extraer datos con las nuevas correcciones v6.0.3
    logger.info("Extrayendo datos con correcciones v6.0.3...")
    datos_extraidos = extract_ihq_data(texto_caso)

    if not datos_extraidos:
        logger.error("No se pudieron extraer datos del caso")
        return False

    logger.info(f"Datos extraídos: {len(datos_extraidos)} campos")

    # Mostrar campos críticos
    logger.info("\n=== CAMPOS CRÍTICOS EXTRAÍDOS ===")
    logger.info(f"IHQ_ESTUDIOS_SOLICITADOS: {datos_extraidos.get('estudios_solicitados', 'N/A')}")
    logger.info(f"FACTOR_PRONOSTICO: {datos_extraidos.get('factor_pronostico', 'N/A')}")
    logger.info(f"DIAGNOSTICO_PRINCIPAL: {datos_extraidos.get('diagnostico_principal', 'N/A')}")
    logger.info(f"IHQ_ORGANO: {datos_extraidos.get('ihq_organo', 'N/A')}")
    logger.info(f"IHQ_CK7: {datos_extraidos.get('IHQ_CK7', 'N/A')}")
    logger.info(f"IHQ_CKAE1_AE3: {datos_extraidos.get('IHQ_CKAE1AE3', 'N/A')}")
    logger.info(f"IHQ_CAM52: {datos_extraidos.get('IHQ_CAM52', 'N/A')}")
    logger.info(f"IHQ_GFAP: {datos_extraidos.get('IHQ_GFAP', 'N/A')}")
    logger.info(f"IHQ_S100: {datos_extraidos.get('IHQ_S100', 'N/A')}")
    logger.info(f"IHQ_SOX10: {datos_extraidos.get('IHQ_SOX10', 'N/A')}")

    # Verificar y forzar número de petición en todos los formatos posibles
    numero_peticion = datos_extraidos.get('numero_peticion') or datos_extraidos.get('Numero de caso') or datos_extraidos.get('numero_de_caso')
    logger.info(f"\nN°Petición detectado: {numero_peticion}")
    logger.info(f"factor_pronostico PRE-MAPEO: {datos_extraidos.get('factor_pronostico', 'NO EXISTE')}")
    logger.info(f"Factor pronostico PRE-MAPEO: {datos_extraidos.get('Factor pronostico', 'NO EXISTE')}")

    if not numero_peticion:
        logger.warning("⚠️ Número de petición no detectado, forzando 'IHQ250982'")

    # Forzar IHQ250982 en TODOS los formatos de columna
    datos_extraidos['numero_peticion'] = 'IHQ250982'
    datos_extraidos['Numero de caso'] = 'IHQ250982'
    datos_extraidos['numero_de_caso'] = 'IHQ250982'  # Formato normalizado que espera save_records()

    # CORREGIDO v6.0.4.1: Mapear a formato de BD antes de guardar
    # extract_ihq_data() retorna campos internos como 'estudios_solicitados_tabla'
    # pero la BD necesita 'IHQ_ESTUDIOS_SOLICITADOS'
    logger.info("\nMapeando datos a formato de BD...")
    datos_bd = map_to_database_format(datos_extraidos)

    logger.info(f"IHQ_ESTUDIOS_SOLICITADOS (post-mapeo): {datos_bd.get('IHQ_ESTUDIOS_SOLICITADOS', 'N/A')}")
    logger.info(f"Factor pronostico (post-mapeo): {datos_bd.get('Factor pronostico', 'N/A')}")
    logger.info(f"IHQ_CK7 (post-mapeo): {datos_bd.get('IHQ_CK7', 'N/A')}")
    logger.info(f"IHQ_CKAE1AE3 (post-mapeo): {datos_bd.get('IHQ_CKAE1AE3', 'N/A')}")

    # DEBUG: Mostrar TODAS las claves del diccionario mapeado
    logger.info(f"\nClaves en datos_bd ({len(datos_bd)}): {', '.join(list(datos_bd.keys())[:20])}")

    # Insertar en BD
    logger.info("\nInsertando en base de datos...")
    try:
        # save_records espera una lista de diccionarios YA MAPEADOS
        registros_guardados = save_records([datos_bd])
        logger.info(f"✅ Caso IHQ250982 reprocesado y guardado exitosamente ({registros_guardados} registro)")
        return True
    except Exception as e:
        logger.error(f"Error al insertar en BD: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "="*80)
    print("REPROCESAMIENTO CASO IHQ250982 - v6.0.3")
    print("="*80 + "\n")

    exito = reprocesar_caso_ihq250982()

    if exito:
        print("\n" + "="*80)
        print("✅ REPROCESAMIENTO COMPLETADO EXITOSAMENTE")
        print("="*80)
        print("\nPróximo paso: Ejecutar auditoría con:")
        print("python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente")
    else:
        print("\n" + "="*80)
        print("❌ ERROR EN REPROCESAMIENTO")
        print("="*80)
        sys.exit(1)
