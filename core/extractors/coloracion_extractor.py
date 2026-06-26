# -*- coding: utf-8 -*-
"""
V6.9.45 — Extractor dedicado para PDFs de "Coloraciones básicas" (estudios M autónomos).

Estos informes son los estudios de histología / coloración básica (H&E) del laboratorio,
PREVIOS a la IHQ. De ellos se extrae SOLO el campo DIAGNÓSTICO + la demografía mínima del
paciente. Características verificadas de los PDF:
  - Texto NATIVO (fitz get_text), NO requiere OCR. NO usa IA.
  - 1 caso por página (algunos casos ocupan 2-3 páginas consecutivas con el mismo Nº M).
  - Hay una página-manifiesto/índice al final ("LABORATORIO CLINICO" + "No. Caso") que se descarta.

IMPORTANTE: este módulo NO toca el flujo IHQ (no usa segment_reports_multicase ni
extract_ihq_data). Filosofía del sistema: si no se puede aislar el diagnóstico con
seguridad, se devuelve "" / "REVISAR" — NUNCA se inventa.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Dict, List, Optional


# ───────────────────────── utilidades ─────────────────────────
def _norm(s: str) -> str:
    """minúsculas + sin tildes (tolera mojibake), para detección robusta."""
    s = str(s or "").lower()
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# La 'Ó' de DIAGNÓSTICO/PATÓLOGO a veces llega como mojibake (�). Las clases la toleran.
_ACC_O = "OÓ�"
_ACC_A = "AÁ�"
_ACC_I = "IÍ�"

# Inicio de la sección de diagnóstico (línea que es solo "DIAGNÓSTICO").
_RE_DIAG = re.compile(r"(?:^|\n)[ \t]*DIAGN[" + _ACC_O + r"]ST[" + _ACC_I + r"]CO[ \t]*\n")

# Encabezado de continuación de página (multipágina): "Mxxxx / Copia|Final Pag. n de m / ...
# Fecha Informe : dd/mm/aaaa". Es RUIDO embebido — se borra ANTES de cortar la sección.
_RE_CONT_HEADER = re.compile(
    r"\n[ \t]*M\d+[ \t]*\n[ \t]*(?:Copia|Final)[ \t]+Pag\.\s*\d+\s+de\s+\d+"
    r".*?Fecha\s+Informe[ \t]*\n?[ \t]*:[ \t]*\d{2}/\d{2}/\d{4}",
    re.DOTALL | re.IGNORECASE,
)

# Pie legal estándar del informe (RUIDO).
_RE_PIE_LEGAL = re.compile(
    r"Todos\s+los\s+an[" + _ACC_A + r"]?lisis.*?(?:1WA|Oneworld\s+Accuracy)",
    re.DOTALL | re.IGNORECASE,
)

# Terminadores de la sección de diagnóstico (firma del patólogo, nota, comentarios…).
# El primero captura "NOMBRE DEL PATÓLOGO\nResponsable del análisis" para cortar ANTES del nombre.
_TERMINADORES = [
    # FIRMA: NOMBRE del patólogo (2-4 palabras en MAYÚSCULAS, misma línea) seguido del
    # ROL ("[Médica ]Patólog…" o "Responsable del análisis"). Corta ANTES del nombre.
    # El nombre puede ir en su propia línea o pegado al final del dx. El NOMBRE es
    # MAYÚS-only (sin IGNORECASE) y limitado a 2-4 palabras -> NO se come el diagnóstico
    # (que termina a menudo en mayúsculas pero NO va seguido del rol).
    re.compile(
        r"[ \t\n]+[A-ZÁÉÍÓÚÑÜ]{2,}(?:[ \t]+[A-ZÁÉÍÓÚÑÜ]{2,}){1,3}[ \t\n]+"
        r"(?i:(?:m[eé]dic[oa]\s+)?pat[oó�]log|responsable\s+del\s+an)"
    ),
    # Fallbacks (cortan en el marcador; podrían dejar el nombre en casos raros):
    re.compile(r"[ \t\n]*[Rr]esponsable\s+del\s+an"),
    re.compile(r"[ \t\n]+(?i:(?:m[eé]dic[oa]\s+)?pat[oó�]log)"),
    re.compile(r"[ \t\n]+RM[:\.]?\s*\d{2,}", re.IGNORECASE),
    re.compile(r"\n_{3,}"),
    re.compile(r"\n[ \t]*Nota:\s*Este\s+informe", re.IGNORECASE),
    re.compile(r"\n[ \t]*COMENTARIOS?\b", re.IGNORECASE),
    re.compile(r"Todos\s+los\s+an[aáAÁ�]?lisis", re.IGNORECASE),
]

_RE_M = re.compile(r"N\.?\s*petici[" + _ACC_O + r"]n\s*\n?\s*:\s*(M\d{5,})", re.IGNORECASE)
_RE_M_FALLBACK = re.compile(r"^\s*(M\d{5,})\s*$", re.MULTILINE)
_RE_CEDULA = re.compile(r"Identificaci[oó�]n\s*\n?\s*:\s*([A-Za-z]{2,3})?\.?\s*([\d\.]{4,})", re.IGNORECASE)
_RE_NOMBRE = re.compile(r"Nombre\s*\n?\s*:\s*(.+?)\s*\n\s*N\.?\s*petici", re.IGNORECASE | re.DOTALL)
_RE_GENERO = re.compile(r"Genero\s*\n?\s*:\s*([A-Za-z]+)", re.IGNORECASE)
_RE_EDAD = re.compile(r"Edad\s*\n?\s*:\s*(\d{1,3})", re.IGNORECASE)
_RE_FECHA_INF = re.compile(r"Fecha\s+Informe\s*\n?\s*:\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
# Órgano: aparece entre el medio de fijación ("Formol…") y la fecha de toma (aaaa-mm-dd).
_RE_ORGANO = re.compile(r"Formol[^\n]*\n\s*([^\n]+?)\s*\n\s*\d{4}-\d{2}-\d{2}", re.IGNORECASE)


def es_pagina_manifiesto(texto: str) -> bool:
    """La última página suele ser un índice/manifiesto del lote (no es un caso)."""
    t = _norm(texto)
    return ("laboratorio clinico" in t and "no. caso" in t) or ("n. peticion" not in t and "diagnostico" not in t)


def extraer_m_number(texto: str) -> Optional[str]:
    m = _RE_M.search(texto)
    if m:
        return m.group(1).upper()
    m = _RE_M_FALLBACK.search(texto)
    return m.group(1).upper() if m else None


def _limpiar_dx(bloque: str) -> str:
    """Normaliza saltos/espacios SIN alterar el contenido (solo presentación).
    Une líneas de una sola palabra (tokenización palabra-por-línea) y colapsa blancos."""
    lineas = [ln.strip() for ln in bloque.split("\n")]
    lineas = [ln for ln in lineas if ln]
    # Re-unir: si una línea es muy corta (1-2 palabras sin punto final) y la siguiente
    # continúa la frase, se concatenan con espacio.
    out: List[str] = []
    for ln in lineas:
        if out and len(out[-1]) > 0 and not out[-1].endswith((".", ":", ";")) and (len(ln.split()) <= 3 or len(out[-1].split()) <= 2):
            out[-1] = (out[-1] + " " + ln).strip()
        else:
            out.append(ln)
    txt = "\n".join(out)
    txt = re.sub(r"[ \t]{2,}", " ", txt)
    return txt.strip()


def extraer_diagnostico(texto_caso: str) -> str:
    """Aísla SOLO el bloque DIAGNÓSTICO del texto (1 caso, ya concatenado si era multipágina).
    Devuelve '' si no se puede aislar con seguridad (no inventa)."""
    if not texto_caso:
        return ""
    # FASE A: borrar ruido embebido (headers de continuación + pie legal) ANTES de cortar.
    t = _RE_CONT_HEADER.sub("\n", texto_caso)
    t = _RE_PIE_LEGAL.sub("\n", t)
    # FASE B: localizar el inicio de la sección.
    m = _RE_DIAG.search(t)
    if not m:
        return ""
    cuerpo = t[m.end():]
    # FASE C: cortar en el primer terminador real (firma/nota/comentarios…).
    fin = len(cuerpo)
    for rgx in _TERMINADORES:
        mm = rgx.search(cuerpo)
        if mm and mm.start() < fin:
            fin = mm.start()
    cuerpo = cuerpo[:fin]
    return _limpiar_dx(cuerpo)


def _split_nombre(nombre_crudo: str) -> Dict[str, str]:
    """Parte el nombre en 4 campos REUTILIZANDO el divisor del flujo IHQ
    (core.utils.name_splitter.split_full_name) para mantener consistencia con el
    resto del sistema. Si falla el import, cae a una heurística simple."""
    d = {"Primer nombre": "", "Segundo nombre": "", "Primer apellido": "", "Segundo apellido": ""}
    nombre_crudo = str(nombre_crudo or "").strip()
    if not nombre_crudo:
        return d
    try:
        from core.utils.name_splitter import split_full_name
        sp = split_full_name(nombre_crudo)
        noms = (sp.get("nombres") or "").split()
        apes = (sp.get("apellidos") or "").split()
    except Exception:
        toks = nombre_crudo.split()
        noms, apes = toks[:2], toks[2:]
    if noms:
        d["Primer nombre"] = noms[0]
        if len(noms) > 1:
            d["Segundo nombre"] = " ".join(noms[1:])
    if apes:
        d["Primer apellido"] = apes[0]
        if len(apes) > 1:
            d["Segundo apellido"] = " ".join(apes[1:])
    return d


def extraer_demografia(texto_caso: str) -> Dict[str, str]:
    """Demografía mínima del PDF M (solo datos REALES presentes; lo ausente queda '')."""
    d: Dict[str, str] = {}
    mc = _RE_CEDULA.search(texto_caso)
    if mc:
        d["Tipo de documento"] = (mc.group(1) or "").upper().strip(".")
        d["N. de identificación"] = re.sub(r"\D", "", mc.group(2) or "")
    mn = _RE_NOMBRE.search(texto_caso)
    if mn:
        nombre = re.sub(r"\s+", " ", mn.group(1).replace("\n", " ")).strip()
        d.update(_split_nombre(nombre))
    mg = _RE_GENERO.search(texto_caso)
    if mg:
        d["Genero"] = mg.group(1).upper()
    me = _RE_EDAD.search(texto_caso)
    if me:
        d["Edad"] = me.group(1)
    mf = _RE_FECHA_INF.search(texto_caso)
    if mf:
        d["Fecha Informe"] = mf.group(1)
    mo = _RE_ORGANO.search(texto_caso)
    if mo:
        org = mo.group(1).strip()
        if org and len(org) <= 60:
            d["Organo"] = org.upper()
    return d


def agrupar_y_extraer(paginas: List[str]) -> List[Dict[str, str]]:
    """Recibe la lista de textos por página de un PDF de coloraciones; agrupa páginas
    consecutivas con el mismo Nº M en un caso y devuelve un dict por caso con:
    {numero_caso, diagnostico_coloracion_2, + demografía}. Descarta el manifiesto."""
    grupos: List[List[str]] = []
    actual_m: Optional[str] = None
    for pg in paginas:
        if es_pagina_manifiesto(pg):
            continue
        m = extraer_m_number(pg)
        if m is None:
            # página huérfana (continuación sin Nº): adjuntar al grupo previo si existe
            if grupos:
                grupos[-1].append(pg)
            continue
        if m == actual_m and grupos:
            grupos[-1].append(pg)
        else:
            grupos.append([pg])
            actual_m = m

    casos: List[Dict[str, str]] = []
    for g in grupos:
        texto = "\n".join(g)
        m = extraer_m_number(texto)
        if not m:
            continue
        dx = extraer_diagnostico(texto)
        reg: Dict[str, str] = {
            "numero_caso": m,
            "diagnostico_coloracion_2": dx if dx else "REVISAR",
        }
        reg.update(extraer_demografia(texto))
        casos.append(reg)
    return casos
