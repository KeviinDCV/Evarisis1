# -*- coding: utf-8 -*-
"""V6.9.66 — ¿QUÉ PDFs YA ESTÁN ANALIZADOS?

Con cientos de PDFs en la carpeta no había forma de saber cuáles ya se procesaron salvo
seleccionarlos y lanzarlos. Esto lo resuelve deduciendo, del NOMBRE del archivo, el rango
de casos que contiene, y consultando cuántos de esos casos ya están en la BD.

Formatos de nombre reales (los tres que hay en pdfs_patologia/):
  · 2025 IHQ         "IHQ DEL 001 AL 050.pdf"        -> IHQ250001 … IHQ250050
  · 2026 IHQ         "IHQ260001 al IHQ260050.pdf"    -> IHQ260001 … IHQ260050
  · Coloraciones     "M 2503754 AL 2503803.pdf"      -> M2503754  … M2503803
El AÑO sale del propio nombre o, si no está, de la carpeta contenedora (…/2025/…).

CRITERIO PRUDENTE (importante): ante la duda, NUNCA se marca como analizado.
Si el nombre no se puede interpretar -> DESCONOCIDO (el usuario decide). Marcar de más
haría que el usuario se SALTARA un PDF sin procesar y se perderían datos; marcar de menos
solo cuesta un reproceso, que es inofensivo.
"""
from __future__ import annotations

import os
import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Estados
COMPLETO = 'COMPLETO'        # todos los casos del rango están en la BD
PARCIAL = 'PARCIAL'          # algunos sí, otros no (se quedó a medias)
NUEVO = 'NUEVO'              # ninguno está: sin analizar
DESCONOCIDO = 'DESCONOCIDO'  # no se pudo interpretar el nombre -> no opinamos

# "IHQ260001 al IHQ260050"  /  "IHQ260001 AL IHQ260050"
_RE_IHQ_FULL = re.compile(r'(?i)IHQ\s*(\d{6,8})\s*(?:al|a|-)\s*IHQ?\s*(\d{6,8})')
# "IHQ DEL 001 AL 050"  (sin año en el nombre: lo pone la carpeta)
_RE_IHQ_CORTO = re.compile(r'(?i)IHQ\s*(?:DEL\s*)?(\d{1,4})\s*(?:al|a|-)\s*(\d{1,4})')
# "M 2503754 AL 2503803"
_RE_M = re.compile(r'(?i)\bM\s*(\d{6,8})\s*(?:al|a|-)\s*M?\s*(\d{6,8})')


def _anio_de_ruta(ruta: str) -> Optional[str]:
    """Año (2 dígitos) tomado de una carpeta '2025'/'2026' en la ruta."""
    for parte in os.path.normpath(ruta).split(os.sep):
        if re.fullmatch(r'20\d{2}', parte.strip()):
            return parte.strip()[2:]
    return None


def rango_de_pdf(ruta: str) -> Optional[Tuple[str, int, int, int]]:
    """(prefijo, desde, hasta, ancho) o None si el nombre no es interpretable.
    'ancho' = dígitos del número dentro del caso, para reconstruirlo con ceros."""
    nombre = os.path.basename(ruta)
    nombre = re.sub(r'(?i)\.pdf$', '', nombre)

    m = _RE_IHQ_FULL.search(nombre)
    if m:
        a, b = m.group(1), m.group(2)
        if len(a) == len(b):
            return ('IHQ', int(a), int(b), len(a))

    m = _RE_M.search(nombre)
    if m:
        a, b = m.group(1), m.group(2)
        if len(a) == len(b):
            return ('M', int(a), int(b), len(a))

    m = _RE_IHQ_CORTO.search(nombre)
    if m:
        anio = _anio_de_ruta(ruta)
        if anio:
            a, b = int(m.group(1)), int(m.group(2))
            # IHQ + AA + 4 dígitos  -> IHQ250001
            return ('IHQ', int(f'{anio}{a:04d}'), int(f'{anio}{b:04d}'), 6)

    # PDF de UN SOLO caso: "IHQ251391.pdf" / "M2511630.pdf"
    m = re.fullmatch(r'(?i)\s*(IHQ|M)\s*(\d{6,8})\s*', nombre)
    if m:
        n = m.group(2)
        return (m.group(1).upper(), int(n), int(n), len(n))

    return None


def casos_de_pdf(ruta: str) -> Optional[List[str]]:
    """Casos que contiene el PDF según su nombre, o None si no se puede interpretar.

    OJO con el separador — cambia el significado por completo:
      "IHQ260001 AL IHQ260050"  -> RANGO  (los 50 casos intermedios)
      "IHQ260782 Y IHQ260795"   -> LISTA  (SOLO esos dos)
    Tratar la lista como rango daba PARCIAL 2/14 en un PDF que está completo.
    """
    nombre = re.sub(r'(?i)\.pdf$', '', os.path.basename(ruta))

    # ¿enumeración con "y"/"," y SIN "al"? -> son casos concretos, no un rango
    if re.search(r'(?i)\s+y\s+|,', nombre) and not re.search(r'(?i)\s+al?\s+', nombre):
        m = re.findall(r'(?i)\b(IHQ|M)\s*(\d{6,8})\b', nombre)
        if len(m) >= 2 and len({x[0].upper() for x in m}) == 1 \
                and len({len(x[1]) for x in m}) == 1:
            return [f'{x[0].upper()}{x[1]}' for x in m]

    rg = rango_de_pdf(ruta)
    if not rg:
        return None
    return _casos_del_rango(*rg)


def _casos_del_rango(pref: str, desde: int, hasta: int, ancho: int) -> List[str]:
    if hasta < desde or (hasta - desde) > 5000:      # rango absurdo -> no opinamos
        return []
    return [f'{pref}{n:0{ancho}d}' for n in range(desde, hasta + 1)]


def estado_pdfs(rutas: List[str], conn=None) -> Dict[str, dict]:
    """{ruta: {'estado', 'en_bd', 'total', 'rango'}} para una lista de PDFs.
    Una sola consulta a la BD para todos (rápido aunque haya cientos de archivos)."""
    info: Dict[str, dict] = {}
    pedidos: Dict[str, List[str]] = {}
    for r in rutas:
        casos = casos_de_pdf(r)
        if not casos:
            info[r] = {'estado': DESCONOCIDO, 'en_bd': 0, 'total': 0, 'rango': ''}
            continue
        pedidos[r] = casos
        info[r] = {'estado': DESCONOCIDO, 'en_bd': 0, 'total': len(casos),
                   'rango': f'{casos[0]}–{casos[-1]}'}
    if not pedidos:
        return info

    todos = sorted({c for cs in pedidos.values() for c in cs})
    presentes = set()
    cerrar = False
    try:
        if conn is None:
            from core.db_adapter import get_connection
            conn = get_connection()
            cerrar = True
        cur = conn.cursor()
        # por lotes: evita una consulta con miles de parámetros
        for i in range(0, len(todos), 900):
            lote = todos[i:i + 900]
            marks = ','.join(['%s'] * len(lote))
            cur.execute(f'SELECT `Numero de caso` FROM informes_ihq '
                        f'WHERE `Numero de caso` IN ({marks})', lote)
            presentes.update(str(x[0]).strip() for x in cur.fetchall())
    except Exception as e:
        logger.warning(f'[estado-pdfs] no se pudo consultar la BD: {e}')
        return info      # todo queda DESCONOCIDO: prudente
    finally:
        if cerrar and conn is not None:
            try:
                conn.close()
            except Exception:
                pass

    for r, casos in pedidos.items():
        n = sum(1 for c in casos if c in presentes)
        info[r]['en_bd'] = n
        if n == 0:
            info[r]['estado'] = NUEVO
        elif n >= len(casos) * 0.9:
            # 90%: un PDF puede traer huecos legítimos (casos anulados, rangos con saltos)
            info[r]['estado'] = COMPLETO
        else:
            info[r]['estado'] = PARCIAL
    return info
