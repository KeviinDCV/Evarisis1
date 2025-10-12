#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chart Helpers - Funciones auxiliares para generación de gráficos
Funciones independientes para visualización de datos
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np


def preparar_datos_para_grafico_barras(
    df: pd.DataFrame,
    columna: str,
    limite_categorias: int = 10
) -> Tuple[List[str], List[int]]:
    """
    Prepara datos de un DataFrame para gráfico de barras

    Args:
        df: DataFrame con datos
        columna: Nombre de la columna a graficar
        limite_categorias: Máximo de categorías a mostrar

    Returns:
        Tupla (labels, valores)
    """
    if columna not in df.columns:
        return [], []

    # Contar valores únicos
    conteos = df[columna].value_counts()

    # Limitar categorías si es necesario
    if len(conteos) > limite_categorias:
        conteos = conteos.head(limite_categorias)

    labels = [str(label) for label in conteos.index]
    valores = conteos.values.tolist()

    return labels, valores


def preparar_datos_para_grafico_pastel(
    df: pd.DataFrame,
    columna: str,
    agrupar_otros: bool = True,
    umbral_otros: float = 0.05
) -> Tuple[List[str], List[float]]:
    """
    Prepara datos para gráfico de pastel (pie chart)

    Args:
        df: DataFrame con datos
        columna: Columna a graficar
        agrupar_otros: Si True, agrupa categorías pequeñas en "Otros"
        umbral_otros: Porcentaje mínimo para no agrupar en "Otros" (0-1)

    Returns:
        Tupla (labels, porcentajes)
    """
    if columna not in df.columns:
        return [], []

    # Contar valores
    conteos = df[columna].value_counts()
    total = conteos.sum()

    if total == 0:
        return [], []

    # Calcular porcentajes
    porcentajes = (conteos / total) * 100

    if agrupar_otros:
        # Separar categorías grandes de pequeñas
        grandes = porcentajes[porcentajes >= (umbral_otros * 100)]
        pequenas = porcentajes[porcentajes < (umbral_otros * 100)]

        labels = [str(label) for label in grandes.index]
        valores = grandes.values.tolist()

        # Agregar "Otros" si hay categorías pequeñas
        if len(pequenas) > 0:
            labels.append("Otros")
            valores.append(pequenas.sum())
    else:
        labels = [str(label) for label in porcentajes.index]
        valores = porcentajes.values.tolist()

    return labels, valores


def calcular_estadisticas_columna(
    df: pd.DataFrame,
    columna: str
) -> Dict[str, Any]:
    """
    Calcula estadísticas descriptivas de una columna

    Args:
        df: DataFrame con datos
        columna: Nombre de la columna

    Returns:
        Dict con estadísticas (media, mediana, min, max, etc.)
    """
    if columna not in df.columns:
        return {}

    serie = df[columna]

    stats = {
        'total': len(serie),
        'no_nulos': serie.notna().sum(),
        'nulos': serie.isna().sum(),
        'valores_unicos': serie.nunique()
    }

    # Si es numérica, agregar estadísticas numéricas
    if pd.api.types.is_numeric_dtype(serie):
        serie_numerica = serie.dropna()
        if len(serie_numerica) > 0:
            stats.update({
                'media': float(serie_numerica.mean()),
                'mediana': float(serie_numerica.median()),
                'min': float(serie_numerica.min()),
                'max': float(serie_numerica.max()),
                'desviacion_std': float(serie_numerica.std()) if len(serie_numerica) > 1 else 0
            })

    return stats


def generar_paleta_colores(n_colores: int, estilo: str = "vibrante") -> List[str]:
    """
    Genera una paleta de colores para gráficos

    Args:
        n_colores: Cantidad de colores necesarios
        estilo: Estilo de la paleta ("vibrante", "pastel", "profesional")

    Returns:
        Lista de colores en formato hex
    """
    paletas = {
        'vibrante': [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8',
            '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739', '#52B788'
        ],
        'pastel': [
            '#FFB3BA', '#BAFFC9', '#BAE1FF', '#FFFFBA', '#FFDFBA',
            '#E0BBE4', '#FFDFD3', '#C7CEEA', '#FFDAC1', '#B5EAD7'
        ],
        'profesional': [
            '#2C3E50', '#E74C3C', '#3498DB', '#2ECC71', '#F39C12',
            '#9B59B6', '#1ABC9C', '#34495E', '#E67E22', '#95A5A6'
        ]
    }

    paleta = paletas.get(estilo, paletas['vibrante'])

    # Repetir colores si se necesitan más
    while len(paleta) < n_colores:
        paleta.extend(paleta)

    return paleta[:n_colores]


def preparar_datos_serie_temporal(
    df: pd.DataFrame,
    columna_fecha: str,
    columna_valor: str,
    frecuencia: str = 'D'
) -> Tuple[List[str], List[Any]]:
    """
    Prepara datos para gráfico de serie temporal

    Args:
        df: DataFrame con datos
        columna_fecha: Nombre de la columna con fechas
        columna_valor: Nombre de la columna con valores
        frecuencia: Frecuencia de agrupación ('D'=día, 'W'=semana, 'M'=mes, 'Y'=año)

    Returns:
        Tupla (fechas, valores)
    """
    if columna_fecha not in df.columns or columna_valor not in df.columns:
        return [], []

    # Convertir a datetime si no lo es
    df_temp = df.copy()
    df_temp[columna_fecha] = pd.to_datetime(df_temp[columna_fecha], errors='coerce')

    # Eliminar nulos
    df_temp = df_temp.dropna(subset=[columna_fecha, columna_valor])

    if len(df_temp) == 0:
        return [], []

    # Ordenar por fecha
    df_temp = df_temp.sort_values(columna_fecha)

    # Agrupar por frecuencia
    df_temp.set_index(columna_fecha, inplace=True)
    df_agrupado = df_temp[columna_valor].resample(frecuencia).count()

    fechas = [fecha.strftime('%Y-%m-%d') for fecha in df_agrupado.index]
    valores = df_agrupado.values.tolist()

    return fechas, valores


def calcular_distribucion_porcentual(
    df: pd.DataFrame,
    columna: str
) -> Dict[str, float]:
    """
    Calcula la distribución porcentual de valores en una columna

    Args:
        df: DataFrame con datos
        columna: Nombre de la columna

    Returns:
        Dict con {valor: porcentaje}
    """
    if columna not in df.columns:
        return {}

    conteos = df[columna].value_counts()
    total = conteos.sum()

    if total == 0:
        return {}

    distribucion = {
        str(valor): (count / total) * 100
        for valor, count in conteos.items()
    }

    return distribucion


def generar_datos_heatmap(
    df: pd.DataFrame,
    columna_x: str,
    columna_y: str,
    columna_valor: str = None
) -> Tuple[List[str], List[str], List[List[float]]]:
    """
    Prepara datos para un mapa de calor (heatmap)

    Args:
        df: DataFrame con datos
        columna_x: Columna para eje X
        columna_y: Columna para eje Y
        columna_valor: Columna con valores (si None, cuenta ocurrencias)

    Returns:
        Tupla (labels_x, labels_y, matriz_valores)
    """
    if columna_x not in df.columns or columna_y not in df.columns:
        return [], [], []

    # Crear tabla pivot
    if columna_valor and columna_valor in df.columns:
        pivot = pd.pivot_table(
            df,
            values=columna_valor,
            index=columna_y,
            columns=columna_x,
            aggfunc='mean',
            fill_value=0
        )
    else:
        # Contar ocurrencias
        pivot = pd.crosstab(df[columna_y], df[columna_x])

    labels_x = [str(x) for x in pivot.columns]
    labels_y = [str(y) for y in pivot.index]
    matriz = pivot.values.tolist()

    return labels_x, labels_y, matriz


def calcular_tendencia_lineal(
    x: List[float],
    y: List[float]
) -> Tuple[float, float]:
    """
    Calcula la tendencia lineal de un conjunto de datos

    Args:
        x: Lista de valores X
        y: Lista de valores Y

    Returns:
        Tupla (pendiente, intercepto) para y = pendiente*x + intercepto
    """
    if len(x) != len(y) or len(x) < 2:
        return 0.0, 0.0

    x_arr = np.array(x)
    y_arr = np.array(y)

    # Calcular pendiente e intercepto usando mínimos cuadrados
    pendiente, intercepto = np.polyfit(x_arr, y_arr, 1)

    return float(pendiente), float(intercepto)


__all__ = [
    'preparar_datos_para_grafico_barras',
    'preparar_datos_para_grafico_pastel',
    'calcular_estadisticas_columna',
    'generar_paleta_colores',
    'preparar_datos_serie_temporal',
    'calcular_distribucion_porcentual',
    'generar_datos_heatmap',
    'calcular_tendencia_lineal'
]
