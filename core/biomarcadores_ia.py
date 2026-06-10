# -*- coding: utf-8 -*-
"""V6.9.31 — Capa IA de respaldo para BIOMARCADORES.

El extractor regex capta las formas estándar ("CD31: positivo", "CD31 positivo")
pero NO la redacción narrativa libre del patólogo ("el CD31 resalta el endotelio",
"CD31+", "marcación de CD31 en estructuras vasculares"). Esto dejaba biomarcadores
SOLICITADOS y MENCIONADOS con la columna vacía (ej. CD31 en casos vasculares).

Esta capa, SOLO para los marcadores que están VACÍOS pero SÍ se mencionan en el
informe, le pide al LLM LOCAL (mismo de extractor_diagnostico_ia, con guard
anti-cloud) que lea la descripción y extraiga su resultado.

ANTI-REGRESIÓN: nunca toca un biomarcador que el regex YA llenó; solo rellena los
vacíos. Si el LLM no está / falla, todo queda igual (best-effort).
"""
from __future__ import annotations

import re
import json
import logging
import unicodedata
from typing import Dict, Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None

# Reutilizamos la infra local del extractor de diagnóstico (endpoint, modelo,
# guard anti-cloud, flag de config).
from core.extractor_diagnostico_ia import (
    _leer_config, _resolver_modelo, _es_endpoint_local, _ia_habilitada,
)

_VACIO = ("", "N/A", "NA", "NO MENCIONADO", "NO APLICA", "NONE", "NULL", "NAN",
          "NO ENCONTRADO", "SIN DATO")

# Columnas IHQ_* que NO son biomarcadores con resultado (metadatos)
_NO_BIOMARCADOR = {"IHQ_ESTUDIOS_SOLICITADOS", "IHQ_ORGANO", "IHQ_P16_PORCENTAJE",
                   "IHQ_HER2_PORCENTAJE", "IHQ_HER2_INTENSIDAD", "IHQ_ER_PORCENTAJE",
                   "IHQ_PR_PORCENTAJE"}


def _norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    nf = unicodedata.normalize("NFKD", s)
    t = "".join(c for c in nf if not unicodedata.combining(c)).upper()
    t = re.sub(r"\s+", " ", t)
    # juntar "CD 31" / "CD-31" -> "CD31" para detección robusta
    t = re.sub(r"\bCD\s*[-/]?\s*(\d+)", r"CD\1", t)
    return t


def _token_marcador(columna: str) -> Optional[str]:
    """Token buscable derivado de la columna (IHQ_CD31 -> 'CD31'). Solo para
    marcadores con nombre-token claro (CDxx, DOG1, HHV8, ALK, PAX8, etc.)."""
    nombre = columna[4:] if columna.startswith("IHQ_") else columna
    t = nombre.replace("_", "").replace("-", "").upper()
    # Aceptar solo tokens alfanuméricos cortos y específicos (evita falsos
    # positivos de nombres genéricos). CD\d+, DOG1, HHV8, ALK, ALK1, WT1, PAX5/8,
    # SOX10/11, TTF1, GATA3, CK7/20/19, P53/63/40, BCL2/6, MUM1, CD1A, etc.
    if re.fullmatch(r"(CD\d{1,3}[A-Z]?|DOG1|HHV8|ALK1?|WT1|PAX[58]|SOX1[01]|TTF1|"
                    r"GATA3|CK\d{1,2}|P\d{2}|BCL[26]|MUM1|DESMINA|VIMENTINA|"
                    r"SINAPTOFISINA|CROMOGRANINA|PODOPLANINA|CALRETININA|MELANA|"
                    r"HMB45|S100|EMA|PSA|GFAP|CDX2|NAPSIN|MDM2|CDK4|DOG1)", t):
        return t
    return None


def biomarcadores_faltantes_mencionados(db_record: Dict, full_text: str) -> Dict[str, str]:
    """Devuelve {columna_IHQ: token} de biomarcadores VACÍOS en db_record pero
    MENCIONADOS en el informe (candidatos a rescatar con IA)."""
    if not full_text:
        return {}
    t = _norm(full_text)
    # V6.9.31 FIX: iterar la LISTA COMPLETA de columnas IHQ_* (no solo las que
    # db_record trae). map_to_database_format no crea todas las columnas (ej.
    # IHQ_CD31 faltaba), por eso el detector nunca las veía.
    try:
        from core.columnas_huv_ia import COLUMNAS_IA
        columnas = [c for c in COLUMNAS_IA if c.startswith("IHQ_")]
    except Exception:
        columnas = [c for c in db_record if c.startswith("IHQ_")]
    faltantes: Dict[str, str] = {}
    for col in columnas:
        if col in _NO_BIOMARCADOR:
            continue
        val = db_record.get(col)
        if val is not None and str(val).strip().upper() not in _VACIO:
            continue  # el regex YA lo llenó -> NO tocar
        token = _token_marcador(col)
        if not token:
            continue
        if re.search(rf"\b{re.escape(token)}\b", t):
            faltantes[col] = token
        if len(faltantes) >= 18:  # cota de seguridad por caso
            break
    return faltantes


_INSTR = (
    "Eres un patólogo experto. Del siguiente informe de inmunohistoquímica, "
    "extrae el RESULTADO de cada marcador de la LISTA. El resultado debe ser "
    "'POSITIVO', 'NEGATIVO', un porcentaje (ej. '20%' para Ki-67), o una "
    "descripción MUY breve si el informe la da (ej. 'POSITIVO EN ENDOTELIO'). "
    "Interpreta la redacción narrativa: 'CD31 resalta el endotelio' = POSITIVO; "
    "'CD31+' = POSITIVO; 'marcación de CD31' = POSITIVO; 'CD34 negativo' = "
    "NEGATIVO. Si un marcador de la lista NO aparece en el informe, OMÍTELO "
    "(no lo inventes).\n"
    "CRÍTICO: reporta CADA marcador de la lista POR SEPARADO. Si varios "
    "comparten un resultado (ej. 'CD31 Y CD34 resaltan el endotelio' o "
    "'CD31+ y CD34+'), debes incluir CADA UNO con ese resultado (CD31: "
    "POSITIVO, CD34: POSITIVO). NO agrupes ni omitas ninguno mencionado.\n"
    'Responde SOLO JSON: {"MARCADOR": "RESULTADO", ...}'
)


def _parse_json(texto: str) -> Dict:
    if not texto:
        return {}
    m = re.search(r"\{.*\}", texto, re.DOTALL)
    if not m:
        return {}
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def completar_biomarcadores_con_ia(full_text: str, faltantes: Dict[str, str],
                                   timeout: int = 120) -> Dict[str, str]:
    """Para {columna: token} faltantes, pide al LLM local los resultados.
    Devuelve {columna: resultado} SOLO de los que el LLM encontró."""
    if requests is None or not full_text or not faltantes or not _ia_habilitada():
        return {}
    base_url, modelo_cfg = _leer_config()
    if not _es_endpoint_local(base_url):  # GUARD anti-cloud (Ley 1581)
        logging.warning("[bio-ia] endpoint NO local; se omite por seguridad.")
        return {}
    modelo = _resolver_modelo(base_url, modelo_cfg)
    if not modelo:
        return {}
    tokens = sorted(set(faltantes.values()))
    prompt = f"{_INSTR}\n\nLISTA: {', '.join(tokens)}\n\nINFORME:\n\"\"\"\n{full_text[:8000]}\n\"\"\""
    payload = {"model": modelo, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.1, "max_tokens": 600}
    try:
        r = requests.post(f"{base_url}/chat/completions", json=payload, timeout=timeout)
        r.raise_for_status()
        contenido = r.json()["choices"][0]["message"].get("content", "")
    except Exception as e:
        logging.warning(f"[bio-ia] llamada falló: {e}")
        return {}
    res_ia = _parse_json(contenido)
    if not res_ia:
        return {}
    # Mapear token -> columna (puede haber 1 token por columna)
    token_a_col = {tok: col for col, tok in faltantes.items()}
    out: Dict[str, str] = {}
    for k, v in res_ia.items():
        tok = _norm(str(k)).replace(" ", "")
        col = token_a_col.get(tok)
        if col and v and str(v).strip().upper() not in _VACIO:
            out[col] = str(v).strip().upper()[:60]
    return out
