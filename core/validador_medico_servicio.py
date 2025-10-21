#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🩺 VALIDADOR DE CONSISTENCIA MÉDICO-SERVICIO - EVARISIS CIRUGÍA ONCOLÓGICA
===========================================================================

Módulo que detecta inconsistencias entre el médico tratante y el servicio asignado,
y las corrige automáticamente basándose en una base de conocimiento de especialistas.

Ejemplo de error detectado:
- Médico: LUIS ALFONSO GONZALEZ (Cirujano Oncólogo)
- Servicio: NEUROCIRUGIA (❌ INCORRECTO)
- Corrección: UNIDAD DE ONCOLOGIA COEX (✅ CORRECTO)

Autor: Sistema EVARISIS CIRUGÍA ONCOLÓGICA
Versión: 5.3.8
Fecha: 19 de octubre de 2025
"""

import sys
import logging
import io
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

# Configurar salida UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@dataclass
class PerfilMedico:
    """Define el perfil de un médico con su especialidad y servicio correcto"""
    nombre_completo: str
    variantes: List[str]  # Variantes de escritura del nombre
    especialidad: str
    servicio_correcto: str
    servicios_validos: List[str]  # Servicios donde podría estar (si rota)


# Base de conocimiento de médicos oncólogos HUV
BASE_CONOCIMIENTO_MEDICOS = {
    "LUIS_ALFONSO_GONZALEZ": PerfilMedico(
        nombre_completo="LUIS ALFONSO GONZALEZ",
        variantes=[
            "LUIS ALFONSO GONZALEZ",
            "LUIS A GONZALEZ",
            "LUIS A. GONZALEZ",
            "L.A. GONZALEZ",
            "GONZALEZ LUIS ALFONSO"
        ],
        especialidad="Cirujano Oncólogo",
        servicio_correcto="UNIDAD DE ONCOLOGIA COEX",
        servicios_validos=[
            "UNIDAD DE ONCOLOGIA COEX",
            "CIRUGIA ONCOLOGICA",
            "ONCOLOGIA",
            "QUIROFANO CENTRAL",  # Válido: realiza cirugías oncológicas
            "CIRUGIA GENERAL",    # Válido: puede estar en cirugía general
            "HOSPITALIZACION"     # Válido: seguimiento de pacientes hospitalizados
        ]
    ),

    "JUAN_CAMILO_BAYONA": PerfilMedico(
        nombre_completo="JUAN CAMILO BAYONA",
        variantes=[
            "JUAN CAMILO BAYONA",
            "JUAN C BAYONA",
            "JUAN C. BAYONA",
            "J.C. BAYONA",
            "BAYONA JUAN CAMILO"
        ],
        especialidad="Coordinador Cirugía Oncológica",
        servicio_correcto="UNIDAD DE ONCOLOGIA COEX",
        servicios_validos=[
            "UNIDAD DE ONCOLOGIA COEX",
            "CIRUGIA ONCOLOGICA",
            "ONCOLOGIA",
            "QUIROFANO CENTRAL",  # Válido: realiza cirugías oncológicas
            "CIRUGIA GENERAL",    # Válido: puede estar en cirugía general
            "HOSPITALIZACION"     # Válido: seguimiento de pacientes
        ]
    ),

    # Agregar más médicos oncólogos conocidos aquí
    "ONCOLOGIA_GENERICO": PerfilMedico(
        nombre_completo="SERVICIO DE ONCOLOGIA",
        variantes=[
            "ONCOLOGIA",
            "ONCOLOGO",
            "CIRUGIA ONCOLOGICA"
        ],
        especialidad="Oncología",
        servicio_correcto="UNIDAD DE ONCOLOGIA COEX",
        servicios_validos=[
            "UNIDAD DE ONCOLOGIA COEX",
            "CIRUGIA ONCOLOGICA",
            "ONCOLOGIA"
        ]
    )
}


# Servicios válidos del HUV
SERVICIOS_VALIDOS_HUV = [
    "UNIDAD DE ONCOLOGIA COEX",
    "CIRUGIA ONCOLOGICA",
    "ONCOLOGIA",
    "NEUROCIRUGIA",
    "CIRUGIA GENERAL",
    "GINECOLOGIA",
    "UROLOGIA",
    "MEDICINA INTERNA",
    "PEDIATRIA",
    "GASTROENTEROLOGIA",
    "CIRUGIA CARDIOVASCULAR",
    "CIRUGIA PLASTICA",
    "ORTOPEDIA",
    "OTORRINOLARINGOLOGIA",
    "OFTALMOLOGIA",
    "DERMATOLOGIA"
]


def normalizar_nombre_medico(nombre: str) -> str:
    """
    Normaliza el nombre del médico para comparación

    Args:
        nombre: Nombre del médico como aparece en el sistema

    Returns:
        Nombre normalizado (MAYÚSCULAS, sin puntos, espacios únicos)
    """
    if not nombre:
        return ""

    # Convertir a mayúsculas
    nombre_norm = nombre.upper()

    # Remover puntos
    nombre_norm = nombre_norm.replace(".", "")

    # Normalizar espacios múltiples a uno solo
    import re
    nombre_norm = re.sub(r'\s+', ' ', nombre_norm)

    # Remover espacios al inicio/final
    nombre_norm = nombre_norm.strip()

    return nombre_norm


def identificar_medico(nombre_medico: str) -> Optional[PerfilMedico]:
    """
    Identifica el médico en la base de conocimiento

    Args:
        nombre_medico: Nombre del médico a identificar

    Returns:
        PerfilMedico si se encuentra, None si no
    """
    if not nombre_medico:
        return None

    nombre_norm = normalizar_nombre_medico(nombre_medico)

    # Buscar en la base de conocimiento
    for codigo_medico, perfil in BASE_CONOCIMIENTO_MEDICOS.items():
        # Comparar con nombre completo
        if normalizar_nombre_medico(perfil.nombre_completo) == nombre_norm:
            return perfil

        # Comparar con variantes
        for variante in perfil.variantes:
            if normalizar_nombre_medico(variante) == nombre_norm:
                return perfil

    return None


def validar_servicio_por_medico(
    nombre_medico: str,
    servicio_actual: str
) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Valida que el servicio sea consistente con el médico tratante

    Args:
        nombre_medico: Nombre del médico tratante
        servicio_actual: Servicio asignado actualmente

    Returns:
        Tuple (es_valido, servicio_correcto, razon)
        - es_valido: True si el servicio es correcto
        - servicio_correcto: Servicio que debería tener (None si es válido)
        - razon: Explicación de la corrección
    """
    # Identificar médico
    perfil_medico = identificar_medico(nombre_medico)

    if not perfil_medico:
        # Médico no identificado, no podemos validar
        return True, None, None

    # Normalizar servicio actual
    servicio_actual_norm = normalizar_nombre_medico(servicio_actual)

    # Verificar si el servicio actual es válido para este médico
    servicios_validos_norm = [
        normalizar_nombre_medico(s) for s in perfil_medico.servicios_validos
    ]

    if servicio_actual_norm in servicios_validos_norm:
        # Servicio válido, no hay problema
        return True, None, None

    # Servicio inválido, necesita corrección
    razon = (
        f"El médico {perfil_medico.nombre_completo} es {perfil_medico.especialidad}. "
        f"El servicio '{servicio_actual}' es inconsistente. "
        f"Servicio correcto: '{perfil_medico.servicio_correcto}'"
    )

    return False, perfil_medico.servicio_correcto, razon


def validar_y_corregir_datos_extraidos(datos_extraidos: Dict[str, str]) -> Tuple[Dict[str, str], Optional[Dict]]:
    """
    Valida y corrige datos extraídos ANTES de mapear a BD (V5.3.9.3)

    Esta función se ejecuta durante la extracción, antes de crear el debug_map,
    para que las correcciones se reflejen en todos los archivos generados.

    Args:
        datos_extraidos: Dict con datos recién extraídos del PDF

    Returns:
        Tuple (datos_corregidos, correccion_info o None)
    """
    # Extraer médico y servicio (pueden venir con diferentes nombres de campo)
    nombre_medico = (datos_extraidos.get("medico_tratante") or
                     datos_extraidos.get("Médico tratante") or
                     datos_extraidos.get("Medico tratante (1. Medico solicitante)") or "")

    servicio_actual = (datos_extraidos.get("servicio") or
                       datos_extraidos.get("Servicio") or
                       datos_extraidos.get("Servicio (1. Servicio solicitante)") or "")

    if not nombre_medico or not servicio_actual:
        return datos_extraidos, None

    # Validar
    es_valido, servicio_correcto, razon = validar_servicio_por_medico(
        nombre_medico,
        servicio_actual
    )

    if es_valido or not servicio_correcto:
        return datos_extraidos, None

    # Aplicar corrección
    datos_corregidos = datos_extraidos.copy()

    # Actualizar todos los campos posibles donde pueda estar el servicio
    campos_servicio = ["servicio", "Servicio", "Servicio (1. Servicio solicitante)"]
    for campo in campos_servicio:
        if campo in datos_corregidos:
            datos_corregidos[campo] = servicio_correcto

    # Información de la corrección para el debug_map
    correccion_info = {
        "tipo": "medico_servicio",
        "campo": "Servicio",
        "valor_original": servicio_actual,
        "valor_corregido": servicio_correcto,
        "razon": razon,
        "timestamp": datetime.now().isoformat(),
        "confianza": 1.0
    }

    return datos_corregidos, correccion_info


def validar_caso_completo(
    datos_caso: Dict[str, str]
) -> Dict[str, any]:
    """
    Valida un caso completo y detecta inconsistencias médico-servicio

    Args:
        datos_caso: Diccionario con los campos del caso

    Returns:
        Dict con resultado de validación:
        {
            "valido": bool,
            "medico_identificado": str,
            "especialidad": str,
            "servicio_actual": str,
            "servicio_correcto": str (si necesita corrección),
            "razon_correccion": str,
            "comentario_sistema": str (para agregar al caso)
        }
    """
    # Extraer campos relevantes (nombres simplificados en v5.3.5+)
    nombre_medico = datos_caso.get("Médico tratante", "") or datos_caso.get("Medico tratante (1. Medico solicitante)", "")
    servicio_actual = datos_caso.get("Servicio", "") or datos_caso.get("Servicio (1. Servicio solicitante)", "")
    numero_caso = datos_caso.get("Numero de caso", "") or datos_caso.get("N. peticion (0. Numero de biopsia)", "N/A")

    # Validar
    es_valido, servicio_correcto, razon = validar_servicio_por_medico(
        nombre_medico,
        servicio_actual
    )

    # Identificar médico
    perfil_medico = identificar_medico(nombre_medico)

    resultado = {
        "valido": es_valido,
        "medico_identificado": perfil_medico.nombre_completo if perfil_medico else None,
        "especialidad": perfil_medico.especialidad if perfil_medico else None,
        "servicio_actual": servicio_actual,
        "servicio_correcto": servicio_correcto,
        "razon_correccion": razon,
        "comentario_sistema": None
    }

    # Generar comentario para el sistema si necesita corrección
    if not es_valido and servicio_correcto:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        resultado["comentario_sistema"] = (
            f"[CORREGIDO POR SISTEMA - {timestamp}] "
            f"Servicio corregido de '{servicio_actual}' a '{servicio_correcto}'. "
            f"Razón: {razon}"
        )

    return resultado


def aplicar_correccion_bd(
    numero_caso: str,
    servicio_correcto: str,
    comentario_sistema: str
) -> bool:
    """
    Aplica la corrección directamente en la base de datos Y en el debug_map

    Args:
        numero_caso: Número de petición del caso
        servicio_correcto: Servicio corregido
        comentario_sistema: Comentario explicando la corrección

    Returns:
        True si se aplicó correctamente, False si hubo error
    """
    try:
        import json
        import glob
        from pathlib import Path
        from core.database_manager import update_campo_registro, get_registro_by_peticion, get_base_path

        # 1. Actualizar servicio en BD (nombre simplificado en v5.3.5+)
        update_campo_registro(
            numero_caso,
            "Servicio",
            servicio_correcto
        )

        # 2. Buscar y actualizar debug_map correspondiente
        data_path = get_base_path()
        debug_maps_path = data_path / "debug_maps"

        if debug_maps_path.exists():
            # Buscar archivo debug_map para este caso
            pattern = f"debug_map_{numero_caso}_*.json"
            debug_files = list(debug_maps_path.glob(pattern))

            if debug_files:
                # Tomar el más reciente
                debug_file = sorted(debug_files)[-1]

                # Leer debug_map
                with open(debug_file, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)

                # Actualizar campo servicio en extracted_data
                if 'extracted_data' in debug_data:
                    debug_data['extracted_data']['Servicio'] = servicio_correcto

                    # Agregar metadato de corrección
                    if 'metadata' not in debug_data:
                        debug_data['metadata'] = {}

                    if 'correcciones_sistema' not in debug_data['metadata']:
                        debug_data['metadata']['correcciones_sistema'] = []

                    debug_data['metadata']['correcciones_sistema'].append({
                        'timestamp': datetime.now().isoformat(),
                        'campo': 'Servicio',
                        'valor_anterior': debug_data['extracted_data'].get('Servicio_original', 'N/A'),
                        'valor_nuevo': servicio_correcto,
                        'razon': comentario_sistema
                    })

                    # Guardar debug_map actualizado
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        json.dump(debug_data, f, ensure_ascii=False, indent=2)

                    logging.info(f"   📁 Debug map actualizado: {debug_file.name}")

        # 3. Obtener comentarios actuales (si existe el campo)
        registro = get_registro_by_peticion(numero_caso)
        comentarios_actuales = registro.get("Comentarios", "") or registro.get("Comentarios del patólogo", "")

        # 4. Agregar comentario del sistema (si el campo existe)
        if comentarios_actuales or True:  # Intentar siempre
            if comentarios_actuales:
                nuevos_comentarios = f"{comentarios_actuales}\n\n{comentario_sistema}"
            else:
                nuevos_comentarios = comentario_sistema

            # Intentar actualizar comentarios (puede fallar si no existe la columna)
            try:
                update_campo_registro(
                    numero_caso,
                    "Comentarios",
                    nuevos_comentarios
                )
            except:
                # Columna no existe, no es crítico
                pass

        logging.info(f"✅ Corrección aplicada para caso {numero_caso}")
        logging.info(f"   Servicio actualizado: {servicio_correcto}")
        logging.info(f"   Comentario agregado: {comentario_sistema[:100]}...")

        return True

    except Exception as e:
        logging.info(f"❌ Error aplicando corrección para caso {numero_caso}: {e}")
        import traceback
        traceback.print_exc()
        return False


def validar_y_corregir_todos_los_casos() -> Dict[str, any]:
    """
    Valida todos los casos en la base de datos y corrige inconsistencias

    Returns:
        Dict con estadísticas de correcciones:
        {
            "total_casos": int,
            "casos_validados": int,
            "casos_corregidos": int,
            "casos_con_error": int,
            "detalle_correcciones": List[Dict]
        }
    """
    try:
        from core.database_manager import get_all_records_as_dataframe

        # Obtener todos los registros
        df = get_all_records_as_dataframe()

        # Filtrar solo casos con médico y servicio
        df_filtrado = df[df['Médico tratante'].notna() & df['Servicio'].notna()]

        estadisticas = {
            "total_casos": len(df_filtrado),
            "casos_validados": 0,
            "casos_corregidos": 0,
            "casos_con_error": 0,
            "detalle_correcciones": []
        }

        logging.info(f"\n🔍 Validando {len(df_filtrado)} casos...")
        logging.info("=" * 80)

        for _, row in df_filtrado.iterrows():
            datos_caso = {
                "Numero de caso": row['Numero de caso'],
                "Médico tratante": row['Médico tratante'],
                "Servicio": row['Servicio'],
                "Comentarios": row.get('Comentarios', '')
            }

            # Validar caso
            resultado = validar_caso_completo(datos_caso)

            estadisticas["casos_validados"] += 1

            # Si necesita corrección
            if not resultado["valido"] and resultado["servicio_correcto"]:
                logging.info(f"\n⚠️ Inconsistencia detectada en caso {datos_caso['Numero de caso']}:")
                logging.info(f"   Médico: {datos_caso['Médico tratante']} ({resultado['especialidad']})")
                logging.info(f"   Servicio actual: {datos_caso['Servicio']}")
                logging.info(f"   Servicio correcto: {resultado['servicio_correcto']}")
                logging.info(f"   Razón: {resultado['razon_correccion']}")

                # Aplicar corrección
                exito = aplicar_correccion_bd(
                    datos_caso['Numero de caso'],
                    resultado["servicio_correcto"],
                    resultado["comentario_sistema"]
                )

                if exito:
                    estadisticas["casos_corregidos"] += 1
                    estadisticas["detalle_correcciones"].append({
                        "numero_caso": datos_caso['Numero de caso'],
                        "medico": datos_caso['Médico tratante'],
                        "servicio_anterior": datos_caso['Servicio'],
                        "servicio_nuevo": resultado["servicio_correcto"],
                        "razon": resultado["razon_correccion"]
                    })
                else:
                    estadisticas["casos_con_error"] += 1

        # Reporte final
        logging.info("\n" + "=" * 80)
        logging.info("📊 REPORTE FINAL DE VALIDACIÓN Y CORRECCIÓN")
        logging.info("=" * 80)
        logging.info(f"Total casos validados: {estadisticas['casos_validados']}")
        logging.info(f"Casos corregidos: {estadisticas['casos_corregidos']}")
        logging.info(f"Casos con error al corregir: {estadisticas['casos_con_error']}")
        logging.info(f"Casos sin problemas: {estadisticas['casos_validados'] - estadisticas['casos_corregidos'] - estadisticas['casos_con_error']}")

        if estadisticas["detalle_correcciones"]:
            logging.info("\n📝 Detalle de correcciones aplicadas:")
            for detalle in estadisticas["detalle_correcciones"]:
                logging.info(f"\n  • Caso: {detalle['numero_caso']}")
                logging.info(f"    Médico: {detalle['medico']}")
                logging.info(f"    Servicio: {detalle['servicio_anterior']} → {detalle['servicio_nuevo']}")

        logging.info("\n" + "=" * 80)

        return estadisticas

    except Exception as e:
        logging.info(f"❌ Error en validación global: {e}")
        import traceback
        traceback.print_exc()
        return {
            "total_casos": 0,
            "casos_validados": 0,
            "casos_corregidos": 0,
            "casos_con_error": 0,
            "detalle_correcciones": [],
            "error": str(e)
        }


if __name__ == "__main__":
    logging.info("🩺 VALIDADOR DE CONSISTENCIA MÉDICO-SERVICIO")
    logging.info("=" * 80)

    # Test con el caso IHQ250980
    logging.info("\n📋 Test con caso IHQ250980...")
    caso_test = {
        "Numero de caso": "IHQ250980",
        "Médico tratante": "LUIS ALFONSO GONZALEZ",
        "Servicio": "NEUROCIRUGIA",
        "Comentarios": ""
    }

    resultado = validar_caso_completo(caso_test)

    logging.info(f"\nCaso: {caso_test['Numero de caso']}")
    logging.info(f"Médico: {caso_test['Médico tratante']}")
    logging.info(f"Especialidad: {resultado['especialidad']}")
    logging.info(f"Servicio actual: {resultado['servicio_actual']}")
    logging.info(f"¿Válido?: {'✅ SÍ' if resultado['valido'] else '❌ NO'}")

    if not resultado['valido']:
        logging.info(f"\n🔧 Corrección necesaria:")
        logging.info(f"   Servicio correcto: {resultado['servicio_correcto']}")
        logging.info(f"   Razón: {resultado['razon_correccion']}")
        logging.info(f"\n💬 Comentario del sistema:")
        logging.info(f"   {resultado['comentario_sistema']}")

    logging.info("\n" + "=" * 80)

    # Opción para validar todos los casos
    respuesta = input("\n¿Deseas validar y corregir TODOS los casos en la BD? (s/n): ")
    if respuesta.lower() == 's':
        validar_y_corregir_todos_los_casos()


def validar_y_obtener_correccion(registro: Dict) -> Optional[Dict]:
    """
    Valida médico-servicio y retorna corrección si aplica (V5.3.9)

    NO aplica la corrección a la BD, solo retorna la información
    para que sea aplicada por el sistema de correcciones unificado.

    Args:
        registro: Diccionario con datos del caso que incluye:
            - "Médico tratante": Nombre del médico
            - "Servicio": Servicio actual
            - "Numero de caso": Número de petición

    Returns:
        Dict con corrección si aplica, None si no hay corrección necesaria

        Estructura del dict de corrección:
        {
            "tipo": "medico_servicio",
            "campo": "Servicio",
            "valor_original": "NEUROCIRUGIA",
            "valor_corregido": "UNIDAD DE ONCOLOGIA COEX",
            "razon": "Dr. LUIS ALFONSO GONZALEZ es Cirujano Oncólogo...",
            "numero_caso": "IHQ250980",
            "medico": "LUIS ALFONSO GONZALEZ"
        }

    Example:
        >>> registro = {
        ...     "Numero de caso": "IHQ250980",
        ...     "Médico tratante": "LUIS ALFONSO GONZALEZ",
        ...     "Servicio": "NEUROCIRUGIA"
        ... }
        >>> corr = validar_y_obtener_correccion(registro)
        >>> if corr:
        ...     print(f"Corregir {corr['campo']}: {corr['valor_original']} → {corr['valor_corregido']}")
    """
    try:
        # Validar que el registro tenga los campos necesarios
        if not registro.get("Médico tratante") or not registro.get("Servicio"):
            return None

        # Validar caso completo
        resultado = validar_caso_completo(registro)

        # Si el caso es válido, no hay corrección
        if resultado["valido"]:
            return None

        # Si hay inconsistencia pero no tenemos servicio correcto, no podemos corregir
        if not resultado["servicio_correcto"]:
            return None

        # Construir corrección
        numero_caso = registro.get("Numero de caso", "")
        medico = registro.get("Médico tratante", "")

        correccion = {
            "tipo": "medico_servicio",
            "campo": "Servicio",
            "valor_original": resultado["servicio_actual"],
            "valor_corregido": resultado["servicio_correcto"],
            "razon": resultado["comentario_sistema"],
            "numero_caso": numero_caso,
            "medico": medico
        }

        return correccion

    except Exception as e:
        logging.info(f"⚠️ Error en validación de {registro.get('Numero de caso', 'N/A')}: {e}")
        return None
