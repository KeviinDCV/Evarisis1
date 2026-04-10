#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Procesador OCR para documentos médicos PDF
Migrado de: core/ocr_processing.py

Versión: 4.2.0 - Refinamiento de extracción y consolidación
Fecha: 4 de octubre de 2025
"""

import io
import os
import re
import sys
import configparser
from pathlib import Path
from typing import List

import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# ─────────────────────────── CONFIGURACIÓN ─────────────────────────────
_config = configparser.ConfigParser(interpolation=None)

# CORREGIDO: Detectar si estamos en un ejecutable empaquetado
if getattr(sys, 'frozen', False):
    # Estamos ejecutando como .exe
    _base_path = Path(sys.executable).parent
else:
    # Estamos ejecutando como script Python
    _base_path = Path(__file__).resolve().parent.parent.parent

_config.read(_base_path / "config" / "config.ini", encoding="utf-8")

def _merge_split_lines(txt: str) -> str:
    """Fusiona líneas donde OCR separa 'Label' y ': Valor' en líneas diferentes."""
    lines = txt.split('\n')
    merged_lines = []
    i = 0

    while i < len(lines):
        current_line = lines[i].strip()

        # Verificar si la siguiente línea empieza con ": " seguido de contenido
        if (i + 1 < len(lines) and
            lines[i + 1].strip().startswith(': ') and
            len(lines[i + 1].strip()) > 2):

            next_line = lines[i + 1].strip()
            # Fusionar: "Label" + ": Valor" -> "Label : Valor"
            merged_line = current_line + ' ' + next_line
            merged_lines.append(merged_line)
            i += 2  # Saltar la línea siguiente porque ya la procesamos
        else:
            merged_lines.append(lines[i])
            i += 1

    return '\n'.join(merged_lines)

def _post_ocr_cleanup(txt: str) -> str:
    """Normaliza errores comunes del OCR que afectan la segmentación por IHQ."""
    # PRIMERO: Fusionar líneas separadas por OCR
    txt = _merge_split_lines(txt)

    # Une 'I H Q 250006' o 'IHQ 250006' → 'IHQ250006'
    txt = re.sub(r'I\s*H\s*Q\s*(\d{5,7})', r'IHQ\1', txt, flags=re.IGNORECASE)
    # Corrige IHO/IH0/lHQ → IHQ solo si van seguidos de 6–7 dígitos
    txt = re.sub(r'IH[O0lI]\s*(\d{5,7})', r'IHQ\1', txt, flags=re.IGNORECASE)
    # Variantes de "N. petición"
    txt = re.sub(r'(N[°.\s]*|No\.\s*|Nº\s*|N\s*)petici[oó]n\s*[:\-]?', 'N. peticion :', txt, flags=re.IGNORECASE)
    # Colapsa espacios múltiples, conserva saltos de línea
    txt = re.sub(r'[ \t]+', ' ', txt)
    return txt

if sys.platform.startswith("win"):
    tesseract_cmd = _config.get(
        "PATHS", "WINDOWS_TESSERACT", fallback=os.getenv("WINDOWS_TESSERACT")
    )
elif sys.platform.startswith("darwin"):
    tesseract_cmd = _config.get(
        "PATHS", "MACOS_TESSERACT", fallback=os.getenv("MACOS_TESSERACT")
    )
else:
    tesseract_cmd = _config.get(
        "PATHS", "LINUX_TESSERACT", fallback=os.getenv("LINUX_TESSERACT")
    )

if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Parámetros OCR y de procesamiento
DPI = _config.getint("OCR_SETTINGS", "DPI", fallback=300)
PSM_MODE = _config.getint("OCR_SETTINGS", "PSM_MODE", fallback=6)
LANGUAGE = _config.get("OCR_SETTINGS", "LANGUAGE", fallback="spa")
_extra_config = _config.get("OCR_SETTINGS", "OCR_CONFIG", fallback="")
_extra_config = re.sub(r"--psm\s*\d+", "", _extra_config).strip()

FIRST_PAGE = _config.getint("PROCESSING", "FIRST_PAGE", fallback=1)
LAST_PAGE = _config.getint("PROCESSING", "LAST_PAGE", fallback=0)
MIN_WIDTH = _config.getint("PROCESSING", "MIN_WIDTH", fallback=1000)


def pdf_to_text_enhanced(pdf_path: str) -> str:
    """
    Convierte PDF a texto con OCR optimizado

    Args:
        pdf_path: Ruta al archivo PDF

    Returns:
        Texto extraído del PDF con limpieza OCR aplicada

    Raises:
        Exception: Si hay error procesando el PDF
    """
    try:
        full_text = ""
        doc = fitz.open(pdf_path)

        start_page = max(0, FIRST_PAGE - 1)
        end_page = LAST_PAGE if LAST_PAGE > 0 else len(doc)

        for page_num in range(start_page, min(end_page, len(doc))):
            page = doc.load_page(page_num)

            # 1) Intento texto nativo (mucho más limpio si el PDF no es escaneado)
            # v5.3.3: CORREGIDO - Priorizar SIEMPRE texto nativo si tiene contenido
            # V6.2.10: FIX IHQ251029 - Usar "dict" para captura COMPLETA de todas las capas y elementos
            # Problema: get_text("text") y get_text("blocks") pierden texto en capas ocultas o elementos flotantes
            # Solución: get_text("dict") captura TODO el contenido del PDF incluyendo capas y elementos flotantes
            try:
                # V6.2.10: Usar método "text" que SÍ captura todo correctamente
                # El análisis muestra que get_text("text") ya contiene TODO el contenido
                # incluyendo "diagnóstico" y "Previa revisión"
                native = page.get_text("text") or ""
            except Exception:
                # Fallback al método básico
                native = ""

            # Usar texto nativo si tiene contenido razonable (más de 50 caracteres)
            # No requerir código IHQ ya que puede estar en páginas posteriores
            if len(native.strip()) > 50:
                page_text = native
            else:
                # 2) Fallback a OCR con preprocesamiento + reintento de PSM
                pix = page.get_pixmap(matrix=fitz.Matrix(DPI / 72, DPI / 72))
                img_bytes = pix.tobytes("ppm")
                img = Image.open(io.BytesIO(img_bytes))

                if img.mode != "L":
                    img = img.convert("L")

                if img.width < MIN_WIDTH:
                    scale = MIN_WIDTH / img.width
                    new_size = (int(img.width * scale), int(img.height * scale))
                    img = img.resize(new_size, Image.LANCZOS)

                # Idioma por defecto: español+inglés (mejor para siglas)
                lang = LANGUAGE if LANGUAGE else "spa+eng"

                # v5.3.3: Probamos múltiples PSM modes y elegimos el mejor
                # PSM 3: Segmentación automática completa (mejor orden de lectura)
                # PSM 6: Bloque de texto uniforme
                # PSM 4: Columna de texto variable
                tried_psm = []
                candidates = [3, PSM_MODE] + [m for m in (6, 4) if m != PSM_MODE]
                page_texts = []

                for psm in candidates:
                    if psm in tried_psm:
                        continue
                    tried_psm.append(psm)
                    config_str = f"--oem 1 --psm {psm} {_extra_config}".strip()
                    text = pytesseract.image_to_string(img, lang=lang, config=config_str)

                    # Guardar resultado con score de calidad
                    has_ihq = bool(re.search(r'IHQ\s*\d{5,7}', text, flags=re.IGNORECASE))
                    length_ok = len(text) > 200

                    # v5.3.3: Verificar orden correcto de secciones para IHQ
                    # El texto debe tener "DESCRIPCIÓN MACROSCÓPICA" antes de "DESCRIPCIÓN MICROSCÓPICA"
                    macro_match = re.search(r'DESCRIPCI[ÓO]N\s+MACROSC[ÓO]PICA', text, re.IGNORECASE)
                    micro_match = re.search(r'DESCRIPCI[ÓO]N\s+MICROSC[ÓO]PICA', text, re.IGNORECASE)
                    correct_order = False
                    if macro_match and micro_match:
                        correct_order = macro_match.start() < micro_match.start()

                    score = (has_ihq * 10) + (length_ok * 5) + (correct_order * 20) + len(text) / 100
                    page_texts.append((text, score, psm))

                # Elegir el texto con mejor score
                if page_texts:
                    page_texts.sort(key=lambda x: x[1], reverse=True)
                    page_text = page_texts[0][0]
                    # Debug: mostrar qué PSM se eligió
                    # print(f"DEBUG: Elegido PSM {page_texts[0][2]} con score {page_texts[0][1]}")
                else:
                    page_text = ""

            # Limpieza post-OCR / nativo para estabilizar tokens de corte
            page_text = _post_ocr_cleanup(page_text)
            full_text += f"\n--- PÁGINA {page_num + 1} ---\n" + page_text

        doc.close()
        return full_text
    except Exception as e:
        raise Exception(f"Error procesando PDF {pdf_path}: {str(e)}")


# ─────────────────────────── SEGMENTACIÓN DE REPORTES ─────────────────────────────

DEBUG_IHQ_SEGMENTACION = False  # Cambiar a True para ver trazas de segmentación y nombres

def segment_reports_multicase(full_text: str) -> List[str]:
    """Segmenta un documento OCR que puede contener varias peticiones concatenadas.

    ALGORITMO CORREGIDO: Segmentación simplificada que funciona correctamente.

    1. Encuentra códigos IHQ únicos en orden de aparición
    2. Para cada IHQ, extrae desde su primera aparición hasta la primera aparición del siguiente IHQ
    3. Limpia contenido duplicado
    """
    if not full_text:
        return []

    # 1. Encontrar todas las apariciones de códigos IHQ
    ihq_matches = []
    for match in re.finditer(r'IHQ(\d{6})', full_text):
        ihq_code = f"IHQ{match.group(1)}"
        position = match.start()
        ihq_matches.append((ihq_code, position))

    if not ihq_matches:
        return [full_text.strip()]

    # 2. Obtener códigos únicos en orden de primera aparición
    unique_ihqs = []
    seen = set()
    for ihq_code, position in ihq_matches:
        if ihq_code not in seen:
            unique_ihqs.append((ihq_code, position))
            seen.add(ihq_code)

    # 3. Crear segmentos individuales
    segments = []

    for i, (ihq_code, first_pos) in enumerate(unique_ihqs):
        # Inicio: desde la primera aparición de este IHQ
        start_pos = first_pos

        # Final: hasta la primera aparición del siguiente IHQ
        if i + 1 < len(unique_ihqs):
            next_ihq_code, next_pos = unique_ihqs[i + 1]
            end_pos = next_pos
        else:
            end_pos = len(full_text)

        # Buscar un inicio mejor (retroceder hasta inicio del encabezado del caso)
        search_start = max(0, start_pos - 2000)  # Ampliar búsqueda
        search_text = full_text[search_start:start_pos]

        # Buscar separadores hacia atrás en orden de prioridad
        best_start = search_start

        # 1. Primero buscar separadores de página
        for pattern in [r'--- PÁGINA \d+ ---', r'Oneworld Accuracy \(1WA\)']:
            matches = list(re.finditer(pattern, search_text))
            if matches:
                last_match = matches[-1]
                separator_end = search_start + last_match.end()
                best_start = max(best_start, separator_end)

        # 2. Si no hay separador de página, buscar el inicio del encabezado "Nombre"
        # Esto es crítico para casos donde el IHQ está en la misma línea que el nombre
        nombre_match = None
        for match in re.finditer(r'^Nombre\s*:', search_text, re.MULTILINE):
            # Tomar el último match de "Nombre :" antes del código IHQ
            nombre_match = match

        if nombre_match:
            # Usar el inicio de la línea "Nombre" como inicio del caso
            nombre_start = search_start + nombre_match.start()
            best_start = max(best_start, nombre_start)

        # Usar el mejor inicio encontrado
        if best_start > search_start:
            start_pos = best_start

        # Extraer segmento
        segment_text = full_text[start_pos:end_pos].strip()

        if segment_text and ihq_code in segment_text:
            # Limpiar y consolidar el contenido
            clean_text = consolidate_ihq_content(segment_text, ihq_code)
            if clean_text.strip():
                segments.append(clean_text)

    return segments if segments else [full_text.strip()]


def consolidate_ihq_content(text: str, ihq_code: str) -> str:
    """Consolida el contenido médico de un IHQ, eliminando duplicados de encabezado."""
    lines = text.splitlines()

    # Secciones importantes a preservar
    sections = {
        'header': [],
        'descripcion_macroscopica': [],
        'descripcion_microscopica': [],
        'diagnostico': [],
        'expresion_hormonal': [],
        'factores_transcripcion': [],
        'comentarios': [],
        'footer': []
    }

    current_section = 'header'
    seen_header = False
    in_organ_zone = False  # NUEVO: Flag para zona de órgano (entre Bloques y INFORME/DESCRIPCIÓN)

    for line in lines:
        line_upper = line.upper().strip()

        # NUEVO: Detectar inicio de zona de órgano
        if 'BLOQUES' in line_upper and 'LAMINAS' in line_upper:
            in_organ_zone = True

        # Detectar cambios de sección PRIMERO (antes de desactivar in_organ_zone)
        # CORREGIDO: Agregar todas las variantes con/sin acentos
        # v5.3.4 FIX: Solo cambiar de sección si la línea SOLO contiene el encabezado (no hay texto adicional)
        # Esto previene que líneas como "con\nDESCRIPCIÓN MICROSCÓPICA" corten el texto

        is_section_header = False  # Flag para detectar si es solo un encabezado

        if ('DESCRIPCIÓN MACROSCÓPICA' in line_upper or 'DESCRIPCION MACROSCOPICA' in line_upper or
            'DESCRIPCIÓN MACROSCOPICA' in line_upper or 'DESCRIPCION MACROSCÓPICA' in line_upper):
            # Solo cambiar de sección si la línea es SOLO el encabezado (máximo 50 chars)
            if len(line.strip()) < 50:
                current_section = 'descripcion_macroscopica'
                in_organ_zone = False
                is_section_header = True
        elif ('DESCRIPCIÓN MICROSCÓPICA' in line_upper or 'DESCRIPCION MICROSCOPICA' in line_upper or
              'DESCRIPCIÓN MICROSCOPICA' in line_upper or 'DESCRIPCION MICROSCÓPICA' in line_upper):
            # Solo cambiar de sección si la línea es SOLO el encabezado (máximo 50 chars)
            if len(line.strip()) < 50:
                current_section = 'descripcion_microscopica'
                in_organ_zone = False
                is_section_header = True
        elif line_upper.startswith('DIAGNÓSTICO') or line_upper.startswith('DIAGNOSTICO'):
            if len(line.strip()) < 50:
                current_section = 'diagnostico'
                is_section_header = True
        elif 'EXPRESIÓN HORMONAL' in line_upper or 'EXPRESION HORMONAL' in line_upper:
            current_section = 'expresion_hormonal'
            is_section_header = True
        elif 'FACTORES DE TRANSCRIPCION' in line_upper:
            current_section = 'factores_transcripcion'
            is_section_header = True
        elif 'COMENTARIOS' in line_upper:
            current_section = 'comentarios'
            is_section_header = True
        elif 'Todos los análisis son avalados' in line or 'Todos los analisis son avalados' in line:
            current_section = 'footer'
            is_section_header = True

        # Solo incluir el primer encabezado completo
        if current_section == 'header':
            if f'N. peticion' in line and ihq_code in line:
                if not seen_header:
                    seen_header = True
                    sections[current_section].append(line)
                # Omitir encabezados duplicados
            # CORREGIDO: Preservar TODA la zona de órgano (entre Bloques e INFORME)
            elif in_organ_zone:
                sections[current_section].append(line)
            # CORREGIDO: Preservar líneas "INFORME DE" y "ESTUDIO DE INMUNOHISTOQUIMICA"
            elif 'INFORME DE' in line_upper or ('ESTUDIO' in line_upper and 'INMUNOHISTOQUIMICA' in line_upper):
                sections[current_section].append(line)
            elif not seen_header or (seen_header and any(keyword in line_upper for keyword in ['NOMBRE', 'N.IDENTIFICACIÓN', 'GENERO', 'GÉNERO', 'EDAD', 'EPS', 'SALUD', 'MÉDICO TRATANTE', 'SERVICIO', 'FECHA INGRESO', 'FECHA INFORME', 'ORGANO', 'ESTUDIOS SOLICITADOS', 'BLOQUES', 'LAMINAS', 'N. ESTUDIO', 'ESTUDIO', 'TIPO ESTUDIO', 'ALMACENAMIENTO', 'FECHA TOMA'])):
                sections[current_section].append(line)
        else:
            # Para secciones médicas, agregar la línea (incluyendo encabezados de sección)
            # v5.3.4 FIX: Agregar encabezados de sección también, no solo contenido
            # Evitar duplicación de títulos solo si son exactamente iguales
            if not (sections[current_section] and line.strip() == sections[current_section][-1].strip()):
                sections[current_section].append(line)

    # Reconstruir el texto consolidado
    result_parts = []
    for section_name, section_lines in sections.items():
        if section_lines:
            clean_lines = [line for line in section_lines if line.strip()]
            if clean_lines:
                result_parts.extend(clean_lines)

    return '\n'.join(result_parts)
