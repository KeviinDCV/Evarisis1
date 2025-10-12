#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Export Helpers - Funciones auxiliares para exportación de datos
Funciones independientes para generación de reportes y exportaciones
"""

import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd


def generar_nombre_archivo_export(
    prefijo: str = "export",
    tipo: str = "xlsx",
    incluir_timestamp: bool = True
) -> str:
    """
    Genera nombre de archivo para exportación

    Args:
        prefijo: Prefijo del nombre del archivo
        tipo: Extensión del archivo (xlsx, csv, pdf, etc.)
        incluir_timestamp: Si True, incluye fecha y hora

    Returns:
        Nombre del archivo generado
    """
    if incluir_timestamp:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefijo}_{timestamp}.{tipo}"
    else:
        return f"{prefijo}.{tipo}"


def validar_ruta_exportacion(file_path: str) -> tuple[bool, str]:
    """
    Valida que la ruta de exportación sea válida

    Args:
        file_path: Ruta donde se exportará el archivo

    Returns:
        Tupla (es_valido, mensaje)
    """
    if not file_path:
        return False, "No se proporcionó ruta de exportación"

    # Verificar que el directorio padre existe
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
            return True, "Directorio creado exitosamente"
        except Exception as e:
            return False, f"No se pudo crear el directorio: {str(e)}"

    # Verificar que se puede escribir
    try:
        # Intentar crear un archivo temporal
        test_file = file_path + ".test"
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True, "Ruta válida y escribible"
    except Exception as e:
        return False, f"No se puede escribir en la ruta: {str(e)}"


def preparar_dataframe_para_export(
    df: pd.DataFrame,
    columnas_a_incluir: Optional[List[str]] = None,
    renombrar_columnas: Optional[Dict[str, str]] = None
) -> pd.DataFrame:
    """
    Prepara un DataFrame para exportación

    Args:
        df: DataFrame original
        columnas_a_incluir: Lista de columnas a incluir (None = todas)
        renombrar_columnas: Dict con mapeo de nombres antiguos a nuevos

    Returns:
        DataFrame preparado para exportación
    """
    df_export = df.copy()

    # Filtrar columnas si se especifica
    if columnas_a_incluir:
        columnas_existentes = [col for col in columnas_a_incluir if col in df_export.columns]
        df_export = df_export[columnas_existentes]

    # Renombrar columnas si se especifica
    if renombrar_columnas:
        df_export = df_export.rename(columns=renombrar_columnas)

    # Limpiar valores NaN
    df_export = df_export.fillna("N/A")

    return df_export


def calcular_estadisticas_export(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calcula estadísticas del DataFrame a exportar

    Args:
        df: DataFrame con datos

    Returns:
        Dict con estadísticas
    """
    stats = {
        'total_registros': len(df),
        'total_columnas': len(df.columns),
        'columnas': list(df.columns),
        'campos_vacios_por_columna': {},
        'completitud_promedio': 0.0
    }

    # Calcular campos vacíos por columna
    for col in df.columns:
        vacios = df[col].isna().sum() + (df[col] == "N/A").sum() + (df[col] == "").sum()
        stats['campos_vacios_por_columna'][col] = int(vacios)

    # Calcular completitud promedio
    total_celdas = len(df) * len(df.columns)
    if total_celdas > 0:
        celdas_llenas = sum(
            ((~df[col].isna()) & (df[col] != "N/A") & (df[col] != "")).sum()
            for col in df.columns
        )
        stats['completitud_promedio'] = (celdas_llenas / total_celdas) * 100

    return stats


def generar_resumen_exportacion(
    tipo_exportacion: str,
    archivo_destino: str,
    registros_exportados: int,
    columnas_exportadas: int,
    tiempo_segundos: float
) -> str:
    """
    Genera un resumen legible de la exportación realizada

    Args:
        tipo_exportacion: Tipo de exportación (completa, selección, etc.)
        archivo_destino: Ruta del archivo exportado
        registros_exportados: Cantidad de registros
        columnas_exportadas: Cantidad de columnas
        tiempo_segundos: Tiempo que tomó la exportación

    Returns:
        String con resumen de la exportación
    """
    resumen = f"✅ EXPORTACIÓN {tipo_exportacion.upper()} COMPLETADA\n\n"
    resumen += f"📄 Archivo: {os.path.basename(archivo_destino)}\n"
    resumen += f"📊 Registros exportados: {registros_exportados}\n"
    resumen += f"📋 Columnas incluidas: {columnas_exportadas}\n"
    resumen += f"⏱️  Tiempo: {tiempo_segundos:.2f} segundos\n"
    resumen += f"💾 Tamaño: {obtener_tamano_archivo_legible(archivo_destino)}\n"
    resumen += f"\n📁 Ubicación completa:\n{archivo_destino}"

    return resumen


def obtener_tamano_archivo_legible(file_path: str) -> str:
    """
    Obtiene el tamaño de un archivo en formato legible

    Args:
        file_path: Ruta al archivo

    Returns:
        String con tamaño legible (ej: "1.5 MB")
    """
    if not os.path.exists(file_path):
        return "N/A"

    try:
        size_bytes = os.path.getsize(file_path)

        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    except Exception:
        return "N/A"


def filtrar_dataframe_por_criterios(
    df: pd.DataFrame,
    filtros: Dict[str, Any]
) -> pd.DataFrame:
    """
    Filtra un DataFrame según criterios especificados

    Args:
        df: DataFrame original
        filtros: Dict con criterios de filtrado {columna: valor}

    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()

    for columna, valor in filtros.items():
        if columna in df_filtrado.columns:
            if isinstance(valor, list):
                # Filtrar por lista de valores
                df_filtrado = df_filtrado[df_filtrado[columna].isin(valor)]
            elif isinstance(valor, tuple) and len(valor) == 2:
                # Filtrar por rango (min, max)
                df_filtrado = df_filtrado[
                    (df_filtrado[columna] >= valor[0]) &
                    (df_filtrado[columna] <= valor[1])
                ]
            else:
                # Filtrar por valor exacto
                df_filtrado = df_filtrado[df_filtrado[columna] == valor]

    return df_filtrado


def agrupar_registros_por_campo(
    df: pd.DataFrame,
    campo_agrupacion: str
) -> Dict[str, pd.DataFrame]:
    """
    Agrupa registros según un campo específico

    Args:
        df: DataFrame con datos
        campo_agrupacion: Nombre del campo por el cual agrupar

    Returns:
        Dict con grupos {valor_campo: DataFrame}
    """
    if campo_agrupacion not in df.columns:
        return {}

    grupos = {}
    valores_unicos = df[campo_agrupacion].unique()

    for valor in valores_unicos:
        if pd.isna(valor):
            grupos['Sin especificar'] = df[df[campo_agrupacion].isna()]
        else:
            grupos[str(valor)] = df[df[campo_agrupacion] == valor]

    return grupos


def crear_metadata_exportacion(
    tipo_exportacion: str,
    usuario: Optional[str] = None,
    filtros_aplicados: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea metadata para incluir en la exportación

    Args:
        tipo_exportacion: Tipo de exportación realizada
        usuario: Usuario que realizó la exportación
        filtros_aplicados: Filtros que se aplicaron a los datos

    Returns:
        Dict con metadata
    """
    metadata = {
        'fecha_exportacion': datetime.now().isoformat(),
        'tipo_exportacion': tipo_exportacion,
        'sistema': 'EVARISIS CIRUGÍA ONCOLÓGICA',
        'version': '4.2.0'
    }

    if usuario:
        metadata['usuario'] = usuario

    if filtros_aplicados:
        metadata['filtros_aplicados'] = filtros_aplicados

    return metadata


__all__ = [
    'generar_nombre_archivo_export',
    'validar_ruta_exportacion',
    'preparar_dataframe_para_export',
    'calcular_estadisticas_export',
    'generar_resumen_exportacion',
    'obtener_tamano_archivo_legible',
    'filtrar_dataframe_por_criterios',
    'agrupar_registros_por_campo',
    'crear_metadata_exportacion'
]
