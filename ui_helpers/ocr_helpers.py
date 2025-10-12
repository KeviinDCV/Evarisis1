#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR Helpers - Funciones auxiliares para procesamiento OCR
Funciones independientes para manejo de PDFs y OCR
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional


def validar_ruta_pdf(file_path: str) -> Tuple[bool, str]:
    """
    Valida que un archivo PDF existe y es accesible

    Args:
        file_path: Ruta al archivo PDF

    Returns:
        Tupla (es_valido, mensaje)
    """
    if not file_path:
        return False, "No se proporcionó ninguna ruta"

    if not os.path.exists(file_path):
        return False, f"El archivo no existe: {file_path}"

    if not file_path.lower().endswith('.pdf'):
        return False, "El archivo no es un PDF"

    if not os.path.isfile(file_path):
        return False, "La ruta no corresponde a un archivo"

    # Verificar que se puede leer
    try:
        with open(file_path, 'rb') as f:
            f.read(10)  # Leer primeros 10 bytes
        return True, "Archivo válido"
    except PermissionError:
        return False, "No se tienen permisos para leer el archivo"
    except Exception as e:
        return False, f"Error al acceder al archivo: {str(e)}"


def obtener_pdfs_en_carpeta(folder_path: str, recursivo: bool = False) -> List[str]:
    """
    Obtiene lista de archivos PDF en una carpeta

    Args:
        folder_path: Ruta a la carpeta
        recursivo: Si True, busca en subcarpetas también

    Returns:
        Lista de rutas completas a archivos PDF
    """
    if not os.path.exists(folder_path):
        return []

    pdf_files = []

    if recursivo:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
    else:
        for file in os.listdir(folder_path):
            full_path = os.path.join(folder_path, file)
            if os.path.isfile(full_path) and file.lower().endswith('.pdf'):
                pdf_files.append(full_path)

    return sorted(pdf_files)


def obtener_nombre_debug_file(pdf_path: str, prefijo: str = "DEBUG_OCR_OUTPUT") -> str:
    """
    Genera nombre para archivo debug basado en el PDF

    Args:
        pdf_path: Ruta al archivo PDF original
        prefijo: Prefijo para el archivo debug

    Returns:
        Nombre del archivo debug (sin ruta)
    """
    pdf_name = os.path.basename(pdf_path)
    return f"{prefijo}_{pdf_name}.txt"


def limpiar_texto_ocr(texto: str) -> str:
    """
    Limpia texto obtenido por OCR eliminando caracteres extraños

    Args:
        texto: Texto crudo del OCR

    Returns:
        Texto limpiado
    """
    if not texto:
        return ""

    # Eliminar caracteres de control excepto saltos de línea y tabs
    texto_limpio = ''.join(char for char in texto if char.isprintable() or char in '\n\t')

    # Eliminar líneas vacías múltiples
    lineas = texto_limpio.split('\n')
    lineas_limpias = []
    linea_vacia_anterior = False

    for linea in lineas:
        linea_stripped = linea.strip()
        if linea_stripped:
            lineas_limpias.append(linea)
            linea_vacia_anterior = False
        elif not linea_vacia_anterior:
            lineas_limpias.append('')
            linea_vacia_anterior = True

    return '\n'.join(lineas_limpias)


def obtener_estadisticas_texto(texto: str) -> dict:
    """
    Obtiene estadísticas básicas de un texto OCR

    Args:
        texto: Texto a analizar

    Returns:
        Dict con estadísticas (caracteres, palabras, líneas, etc.)
    """
    if not texto:
        return {
            'caracteres': 0,
            'palabras': 0,
            'lineas': 0,
            'lineas_no_vacias': 0
        }

    lineas = texto.split('\n')
    lineas_no_vacias = [l for l in lineas if l.strip()]
    palabras = texto.split()

    return {
        'caracteres': len(texto),
        'palabras': len(palabras),
        'lineas': len(lineas),
        'lineas_no_vacias': len(lineas_no_vacias)
    }


def es_pdf_duplicado(pdf_path: str, carpeta_procesados: str) -> bool:
    """
    Verifica si un PDF ya fue procesado previamente

    Args:
        pdf_path: Ruta al PDF a verificar
        carpeta_procesados: Carpeta donde se guardan registros de procesados

    Returns:
        True si el PDF ya fue procesado
    """
    if not os.path.exists(carpeta_procesados):
        return False

    pdf_name = os.path.basename(pdf_path)
    registro_path = os.path.join(carpeta_procesados, f"{pdf_name}.processed")

    return os.path.exists(registro_path)


def marcar_pdf_como_procesado(pdf_path: str, carpeta_procesados: str) -> bool:
    """
    Marca un PDF como procesado creando un archivo de registro

    Args:
        pdf_path: Ruta al PDF procesado
        carpeta_procesados: Carpeta donde guardar el registro

    Returns:
        True si se marcó exitosamente
    """
    try:
        os.makedirs(carpeta_procesados, exist_ok=True)

        pdf_name = os.path.basename(pdf_path)
        registro_path = os.path.join(carpeta_procesados, f"{pdf_name}.processed")

        with open(registro_path, 'w', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f"Procesado: {datetime.now().isoformat()}\n")
            f.write(f"Archivo: {pdf_path}\n")

        return True
    except Exception as e:
        print(f"Error marcando PDF como procesado: {e}")
        return False


__all__ = [
    'validar_ruta_pdf',
    'obtener_pdfs_en_carpeta',
    'obtener_nombre_debug_file',
    'limpiar_texto_ocr',
    'obtener_estadisticas_texto',
    'es_pdf_duplicado',
    'marcar_pdf_como_procesado'
]
