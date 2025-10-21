#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 VALIDACIÓN CRUZADA POR TIPO DE TUMOR - EVARISIS CIRUGÍA ONCOLÓGICA
=====================================================================

Módulo para validar que los biomarcadores extraídos sean consistentes
con el tipo de tumor diagnosticado. Previene errores como confundir
receptores hormonales en meningiomas con marcadores de cáncer de mama.

Autor: Sistema EVARISIS CIRUGÍA ONCOLÓGICA
Versión: 3.2.2
Fecha: 11 de octubre de 2025
"""

import re
import logging
import sys
import io
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Configurar salida UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


@dataclass
class PerfilTumor:
    """Define los biomarcadores esperados para un tipo de tumor"""
    nombre: str
    biomarcadores_esperados: List[str]  # Biomarcadores típicos
    biomarcadores_inesperados: List[str]  # Biomarcadores que NO debería tener
    keywords: List[str]  # Palabras clave para detectar este tipo de tumor


# Base de conocimiento de perfiles tumorales
PERFILES_TUMORALES = {
    "meningioma": PerfilTumor(
        nombre="Meningioma",
        biomarcadores_esperados=[
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_EMA",
            "IHQ_KI-67",
            "IHQ_VIMENTINA"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",  # NO debería tener ER
            "IHQ_HER2",  # NO es cáncer de mama
            "IHQ_CDX2",  # NO es intestinal
            "IHQ_TTF1"   # NO es pulmonar
        ],
        keywords=[
            "meningioma",
            "meningotelial",
            "fibroblastico",
            "transicional",
            "psammomatoso",
            "who 1", "who 2", "who 3",
            "grado who",
            "duramadre",
            "meninges"
        ]
    ),

    "cancer_mama": PerfilTumor(
        nombre="Cáncer de mama",
        biomarcadores_esperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_KI-67"
        ],
        biomarcadores_inesperados=[
            "IHQ_CDX2",  # NO es intestinal
            "IHQ_TTF1",  # NO es pulmonar
            "IHQ_P40",   # NO es escamoso
            "IHQ_CD20",  # NO es linfoma
            "IHQ_CD3"
        ],
        keywords=[
            "carcinoma ductal",
            "carcinoma lobulillar",
            "mama",
            "mamario",
            "triple negativo",
            "luminal",
            "her2 positivo"
        ]
    ),

    "linfoma": PerfilTumor(
        nombre="Linfoma",
        biomarcadores_esperados=[
            "IHQ_CD3",
            "IHQ_CD5",
            "IHQ_CD10",
            "IHQ_CD20",
            "IHQ_CD30",
            "IHQ_CD45",
            "IHQ_KI-67"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_CDX2",
            "IHQ_TTF1"
        ],
        keywords=[
            "linfoma",
            "hodgkin",
            "no hodgkin",
            "linfoblastico",
            "celulas b",
            "celulas t",
            "burkitt",
            "difuso celulas grandes"
        ]
    ),

    "cancer_pulmon": PerfilTumor(
        nombre="Cáncer de pulmón",
        biomarcadores_esperados=[
            "IHQ_TTF1",
            "IHQ_P40",
            "IHQ_CK7",
            "IHQ_CK20",
            "IHQ_KI-67",
            "IHQ_PDL-1"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_CDX2",
            "IHQ_CD20",
            "IHQ_CD3"
        ],
        keywords=[
            "pulmon",
            "pulmonar",
            "adenocarcinoma pulmonar",
            "carcinoma escamoso pulmonar",
            "microcítico",
            "no microcítico",
            "bronquial"
        ]
    ),

    "cancer_colon": PerfilTumor(
        nombre="Cáncer colorrectal",
        biomarcadores_esperados=[
            "IHQ_CDX2",
            "IHQ_CK20",
            "IHQ_CK7",
            "IHQ_KI-67"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_TTF1",
            "IHQ_P40",
            "IHQ_CD20"
        ],
        keywords=[
            "colon",
            "rectal",
            "colorrectal",
            "adenocarcinoma intestinal",
            "intestino",
            "sigmoides",
            "ciego"
        ]
    ),

    "melanoma": PerfilTumor(
        nombre="Melanoma",
        biomarcadores_esperados=[
            "IHQ_S100",
            "IHQ_MELAN_A",
            "IHQ_SOX10",
            "IHQ_KI-67"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_CDX2",
            "IHQ_TTF1",
            "IHQ_CD20"
        ],
        keywords=[
            "melanoma",
            "melanocitico",
            "pigmentado",
            "breslow",
            "clark"
        ]
    ),

    "tumor_neuroendocrino": PerfilTumor(
        nombre="Tumor neuroendocrino",
        biomarcadores_esperados=[
            "IHQ_SYNAPTOPHYSIN",
            "IHQ_CHROMOGRANINA",
            "IHQ_CD56",
            "IHQ_KI-67"
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_CD20",
            "IHQ_CD3"
        ],
        keywords=[
            "neuroendocrino",
            "carcinoide",
            "tumor neuroendocrino bien diferenciado",
            "tumor neuroendocrino poco diferenciado",
            "sinaptofisina",
            "chromogranina"
        ]
    ),

    "glioma": PerfilTumor(
        nombre="Glioma",
        biomarcadores_esperados=[
            "IHQ_P53",
            "IHQ_KI-67",
            "IHQ_GFAP"  # No está en BD actual pero es esperado
        ],
        biomarcadores_inesperados=[
            "IHQ_RECEPTOR_ESTROGENOS",
            "IHQ_RECEPTOR_PROGESTERONA",
            "IHQ_HER2",
            "IHQ_CDX2",
            "IHQ_TTF1",
            "IHQ_CD20"
        ],
        keywords=[
            "glioma",
            "glioblastoma",
            "astrocitoma",
            "oligodendroglioma",
            "grado who"
        ]
    )
}


def detectar_tipo_tumor(diagnostico: str) -> Optional[str]:
    """
    Detecta el tipo de tumor basándose en el diagnóstico principal

    Args:
        diagnostico: Texto del diagnóstico principal

    Returns:
        Clave del tipo de tumor detectado o None si no se detecta
    """
    if not diagnostico:
        return None

    diagnostico_lower = diagnostico.lower()

    # Buscar coincidencias con keywords de cada perfil
    coincidencias = []
    for tipo_tumor, perfil in PERFILES_TUMORALES.items():
        for keyword in perfil.keywords:
            if keyword.lower() in diagnostico_lower:
                coincidencias.append((tipo_tumor, perfil.nombre))
                break

    if coincidencias:
        # Retornar el primer tipo detectado (prioridad por orden en PERFILES_TUMORALES)
        return coincidencias[0][0]

    return None


def validar_biomarcadores_por_tumor(
    diagnostico: str,
    biomarcadores_extraidos: Dict[str, str]
) -> Tuple[bool, List[str]]:
    """
    Valida que los biomarcadores extraídos sean consistentes con el tipo de tumor

    Args:
        diagnostico: Diagnóstico principal del caso
        biomarcadores_extraidos: Dict con {campo_bd: valor} de biomarcadores

    Returns:
        Tuple (es_valido, lista_advertencias)
        - es_valido: True si no hay inconsistencias críticas
        - lista_advertencias: Lista de advertencias detectadas
    """
    advertencias = []

    # 1. Detectar tipo de tumor
    tipo_tumor = detectar_tipo_tumor(diagnostico)

    if not tipo_tumor:
        # No se pudo detectar tipo de tumor, no podemos validar
        return True, ["No se pudo detectar tipo de tumor para validación cruzada"]

    perfil = PERFILES_TUMORALES[tipo_tumor]

    # 2. Buscar biomarcadores inesperados
    biomarcadores_con_valor = {
        campo: valor for campo, valor in biomarcadores_extraidos.items()
        if valor and valor not in ["N/A", "NO MENCIONADO", ""]
    }

    # 3. Validar cada biomarcador presente
    for campo_bd, valor in biomarcadores_con_valor.items():
        # Solo validar si tiene un valor positivo/relevante
        if valor.upper() in ["POSITIVO", "POSITIVA", "FOCAL", "DIFUSO"]:
            if campo_bd in perfil.biomarcadores_inesperados:
                advertencias.append(
                    f"⚠️ INCONSISTENCIA CRÍTICA: {campo_bd} = '{valor}' en {perfil.nombre}. "
                    f"Este biomarcador NO es típico de este tipo de tumor. "
                    f"Revisar si hubo confusión con otro marcador."
                )

    # 4. Verificar si faltan biomarcadores esperados (advertencia suave)
    biomarcadores_presentes = set(biomarcadores_con_valor.keys())
    biomarcadores_esperados_faltantes = [
        b for b in perfil.biomarcadores_esperados
        if b not in biomarcadores_presentes
    ]

    if biomarcadores_esperados_faltantes and len(biomarcadores_presentes) > 0:
        # Solo advertir si hay ALGÚN biomarcador extraído (no casos sin IHQ)
        advertencias.append(
            f"ℹ️ INFO: {perfil.nombre} típicamente incluye {', '.join(biomarcadores_esperados_faltantes[:3])}. "
            f"Si el informe los menciona, verificar extracción."
        )

    # 5. Determinar si hay inconsistencias críticas
    hay_criticas = any("CRÍTICA" in adv for adv in advertencias)
    es_valido = not hay_criticas

    return es_valido, advertencias


def validar_caso_completo(datos_bd: Dict[str, str]) -> Dict[str, any]:
    """
    Valida un caso completo de la BD con validación cruzada

    Args:
        datos_bd: Diccionario con todos los campos del caso

    Returns:
        Dict con resultado de validación:
        {
            "valido": bool,
            "tipo_tumor_detectado": str,
            "advertencias": List[str],
            "biomarcadores_validados": int,
            "inconsistencias_criticas": int
        }
    """
    # Extraer diagnóstico
    diagnostico = datos_bd.get("Diagnostico Principal", "")

    # Extraer todos los biomarcadores IHQ_*
    biomarcadores = {
        campo: valor for campo, valor in datos_bd.items()
        if campo.startswith("IHQ_")
    }

    # Validar
    es_valido, advertencias = validar_biomarcadores_por_tumor(diagnostico, biomarcadores)

    tipo_tumor = detectar_tipo_tumor(diagnostico)
    inconsistencias_criticas = sum(1 for adv in advertencias if "CRÍTICA" in adv)

    return {
        "valido": es_valido,
        "tipo_tumor_detectado": tipo_tumor,
        "advertencias": advertencias,
        "biomarcadores_validados": len([v for v in biomarcadores.values() if v and v != "N/A"]),
        "inconsistencias_criticas": inconsistencias_criticas
    }


def generar_reporte_validacion(casos_validados: List[Dict]) -> str:
    """
    Genera un reporte de validación cruzada para múltiples casos

    Args:
        casos_validados: Lista de resultados de validar_caso_completo()

    Returns:
        Texto formateado del reporte
    """
    total_casos = len(casos_validados)
    casos_validos = sum(1 for c in casos_validados if c["valido"])
    total_inconsistencias = sum(c["inconsistencias_criticas"] for c in casos_validados)

    reporte = []
    reporte.append("=" * 80)
    reporte.append("REPORTE DE VALIDACIÓN CRUZADA POR TIPO DE TUMOR")
    reporte.append("=" * 80)
    reporte.append("")
    reporte.append(f"Total casos analizados: {total_casos}")
    reporte.append(f"Casos válidos: {casos_validos} ({casos_validos/total_casos*100:.1f}%)")
    reporte.append(f"Casos con inconsistencias: {total_casos - casos_validos}")
    reporte.append(f"Total inconsistencias críticas: {total_inconsistencias}")
    reporte.append("")

    if total_inconsistencias > 0:
        reporte.append("CASOS CON INCONSISTENCIAS CRÍTICAS:")
        reporte.append("-" * 80)
        for caso in casos_validados:
            if not caso["valido"]:
                numero_peticion = caso.get("numero_peticion", "Desconocido")
                reporte.append(f"\n{numero_peticion} - {caso.get('tipo_tumor_detectado', 'N/A')}:")
                for adv in caso["advertencias"]:
                    if "CRÍTICA" in adv:
                        reporte.append(f"  • {adv}")

    reporte.append("")
    reporte.append("=" * 80)

    return "\n".join(reporte)


if __name__ == "__main__":
    # Test con caso IHQ250010 (el error real detectado)
    logging.info("🔍 Test de Validación Cruzada")
    logging.info("=" * 80)

    # Caso de prueba: Meningioma con ER incorrecto
    caso_test = {
        "Numero de caso": "IHQ250010",
        "Diagnostico Principal": "MENINGIOMA MENINGOTELIAL, WHO 1",
        "IHQ_RECEPTOR_ESTROGENOS": "POSITIVO",  # ERROR: No debería estar
        "IHQ_RECEPTOR_PROGESTERONA": "POSITIVO",  # CORRECTO
        "IHQ_EMA": "POSITIVO",  # CORRECTO
        "IHQ_KI-67": "1-2%"  # CORRECTO
    }

    resultado = validar_caso_completo(caso_test)

    logging.info(f"\nCaso: {caso_test['N. peticion (0. Numero de biopsia)']}")
    logging.info(f"Diagnóstico: {caso_test['Diagnostico Principal']}")
    logging.info(f"Tipo de tumor detectado: {resultado['tipo_tumor_detectado']}")
    logging.info(f"¿Válido?: {'✅ SÍ' if resultado['valido'] else '❌ NO'}")
    logging.info(f"Biomarcadores validados: {resultado['biomarcadores_validados']}")
    logging.info(f"Inconsistencias críticas: {resultado['inconsistencias_criticas']}")
    logging.info("\nAdvertencias:")
    for adv in resultado["advertencias"]:
        logging.info(f"  {adv}")

    logging.info("\n" + "=" * 80)
    logging.info("✅ Test completado")
