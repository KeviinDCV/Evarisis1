# -*- coding: utf-8 -*-
"""V6.9.30 — Fallback IA para extraer el DIAGNÓSTICO PRINCIPAL.

Cuando el regex de ``unified_extractor.extract_diagnostico_principal`` devuelve
un valor que NO es un diagnóstico real (resultado de marcadores IHQ, puntero
"VER COMENTARIO", línea de espécimen sola tipo "Mucosa gástrica. Biopsia", o un
fragmento), este módulo usa el LLM LOCAL (mistral-nemo vía LM Studio) para
extraer el diagnóstico verdadero leyendo el informe completo — la sección
DIAGNÓSTICO, sus viñetas y el COMENTARIO — como lo haría un patólogo.

DISEÑO ANTI-REGRESIÓN (regla crítica #1):
- SOLO se activa cuando ``es_diagnostico_no_valido()`` es True (el regex falló).
  Las extracciones regex correctas NO se tocan jamás.
- Si el LLM no está disponible o falla, se conserva el valor original (best-effort).

SEGURIDAD (Ley 1581 / Habeas Data):
- Datos médicos confidenciales: el LLM DEBE ser LOCAL. Este módulo llama
  ÚNICAMENTE a endpoints locales/LAN (127.0.0.1, localhost, IP privada). Si el
  endpoint configurado no es local, se ABORTA sin enviar nada (no hay riesgo de
  fuga a la nube).
"""
from __future__ import annotations

import re
import json
import logging
import unicodedata
from typing import Optional

try:
    import requests
except Exception:  # pragma: no cover
    requests = None


# ===================================================================
#  Utilidades
# ===================================================================
def _norm(s: str) -> str:
    if not isinstance(s, str):
        return ""
    nf = unicodedata.normalize("NFKD", s)
    t = "".join(c for c in nf if not unicodedata.combining(c)).upper()
    return re.sub(r"\s+", " ", t).strip()


# ===================================================================
#  Detector: ¿el "diagnóstico" extraído NO es un diagnóstico real?
# ===================================================================
# Conservador a propósito: solo marca patrones de los que estamos SEGUROS que
# no son diagnóstico, para no disparar la IA sobre diagnósticos buenos cortos
# (MELANOMA, GIST, SEMINOMA, HIPERPLASIA...). Esos NO se tocan.
_PREFIJOS_MARCADOR = (
    "RECEPTOR DE", "RECEPTORES DE", "HER2", "HER-2", "HER 2", "HER2/NEU", "HER-2/NEU",
    "INMUNOFENOTIPO", "KI-67", "KI67", "KI 67", "SCORE", "PATRON MICROSATELITAL",
    "SIN PERDIDA DE", "E-CADHERINA", "E CADHERINA", "EXPRESION DE", "EXPRESION POSITIVA",
    "EXPRESION NEGATIVA", "AUSENCIA DE EXPRESION", "MLH 1", "MLH1", "PMS2", "MSH2", "MSH6",
    "PRESENCIA DE CELULAS", "LAS CELULAS TUMORALES", "PERFIL INMUNOHISTOQUIMICO",
    "PERFIL DE INMUNOHISTOQUIMICA", "P16 ", "P53 ", "P40 ", "P63 ",
)
_PUNTEROS = ("VER DESCRIPCION", "VER COMENTARIO")
_FRAGMENTOS_EXACTOS = {
    "EN CURSO", "RECTOSIGMOIDE", "ENDOSCOPICA", "POR COLONOSCOPIA",
    "POR SACABOCADO", "ENDOSCOPIA", "COLONOSCOPIA",
}
_PROCEDIMIENTOS = (
    "BIOPSIA", "RESECCION", "ENDOSCOPIA", "COLONOSCOPIA", "HEMICOLECTOMIA",
    "HISTERECTOMIA", "VACIAMIENTO", "PUNCION", "SACABOCADO", "MASTECTOMIA",
    "EXERESIS", "ESCISION", "BIOPSIA INCISIONAL", "BIOPSIA EXCISIONAL",
)

# Entidades clínicas "fuertes": si el texto las contiene, YA es un diagnóstico
# real (aunque traiga un "(ver comentario)" anexo o un marcador antes) y NO
# debe marcarse como no-válido. Protección anti-falso-positivo (anti-regresión).
_ENTIDAD_FUERTE = (
    "CARCINOMA", "ADENOCARCINOMA", "LINFOMA", "LEUCEMIA", "SARCOMA", "MELANOMA",
    "MIELOMA", "BLASTOMA", "GLIOMA", "MENINGIOMA", "GIST", "HEPATOCARCINOMA",
    "SEMINOMA", "TERATOMA", "SCHWANNOMA", "MESOTELIOMA", "TIMOMA", "NEFROBLASTOMA",
    "WILMS", "PAGET", "HISTIOCITOSIS", "NEUROENDOCRINO", "CARCINOIDE",
    "GASTRITIS", "COLITIS", "HIPERPLASIA", "ADENOMA", "FIBROADENOMA", "NEVUS",
    "QUISTE", "POLIPO", "LIPOMA", "HEMANGIOMA", "DISPLASIA", "METAPLASIA",
    "INFLAMACION", "GRANULOMATOSA", "GRANULOMA", "FUSOCELULAR", "FUSIFORME",
    "PROLIFERACION MELANOCITICA", "OSTEOSARCOMA", "LIPOSARCOMA", "LEIOMIOSARCOMA",
)

# Conclusiones diagnósticas VÁLIDAS (benignas/negativas) que tampoco deben
# marcarse, aunque no contengan una entidad tumoral. Protección anti-falso-pos.
_CONCLUSION_VALIDA = (
    "NEGATIVO PARA MALIGNIDAD", "NEGATIVO PARA NEOPLASIA", "NEGATIVA PARA MALIGNIDAD",
    "SIN EVIDENCIA DE MALIGNIDAD", "SIN EVIDENCIA DE NEOPLASIA", "SIN EVIDENCIA DE LESION",
    "NEGATIVO PARA LESION", "AUSENCIA DE MALIGNIDAD", "SIN MALIGNIDAD",
    "ULCERA", "TEJIDO DE GRANULACION", "NECROSIS", "ATROFIA", "ESTEATOSIS",
)


def es_diagnostico_no_valido(dx: Optional[str]) -> bool:
    """True si ``dx`` NO es un diagnóstico real (marcador/puntero/espécimen/fragmento)."""
    if not dx:
        return True
    t = _norm(dx)
    if not t or t in ("N/A", "NO APLICA", "NA", "SIN DATO", "NO MENCIONADO", "NONE", "NULL"):
        return True
    # GUARD anti-falso-positivo: si ya contiene una entidad clínica fuerte O una
    # conclusión válida (benigna/negativa), es un diagnóstico real -> NO marcar
    # (aunque traiga "(ver comentario)" o un marcador antes). Protege MELANOMA,
    # SARCOMA MIELOIDE, CARCINOMA, NEGATIVO PARA MALIGNIDAD, ÚLCERA, etc.
    if any(k in t for k in _ENTIDAD_FUERTE) or any(k in t for k in _CONCLUSION_VALIDA):
        return False
    # Puntero "ver comentario / ver descripción"
    if any(p in t for p in _PUNTEROS):
        return True
    # Empieza con resultado de marcador IHQ (no es un diagnóstico)
    if any(t.startswith(p) for p in _PREFIJOS_MARCADOR):
        return True
    # Encabezado de sección sin diagnóstico ("ESTUDIO(S) DE INMUNOHISTOQUIMICA")
    if "INMUNOHISTOQUIMICA" in t and len(t) < 45:
        return True
    # Fragmentos conocidos
    if t in _FRAGMENTOS_EXACTOS or t.startswith("BLOQUE "):
        return True
    if t.startswith("POR LO QUE SE REVISA") or t.startswith("REPRESENTACION DE LAS LINEAS"):
        return True
    if t.startswith("LOS HALLAZGOS MORFOLOGICOS Y DE INMUNOH") and len(t) < 60:
        return True
    # Injerto renal sin diagnóstico (biopsia de seguimiento de trasplante)
    if "INJERTO RENAL" in t and len(t) < 50:
        return True
    # Línea de espécimen SIN diagnóstico (ya filtramos entidad/conclusión arriba):
    #  (a) termina en un procedimiento -> "Mucosa gástrica antral. Biopsia"
    #  (b) contiene un procedimiento y termina en localización/lateralidad ->
    #      "A. Piel. Lesión. Biopsia. Mama lado izquierdo"
    # NO marca textos donde tras el procedimiento viene un diagnóstico real
    # (ej. "Exocérvix. Lesión. Biopsia. LESIÓN INTRAEPITELIAL DE ALTO GRADO").
    if len(t) <= 110:
        cuerpo = t.rstrip(". ")
        if any(cuerpo.endswith(p) for p in _PROCEDIMIENTOS):
            return True
        if any(p in t for p in _PROCEDIMIENTOS) and any(cuerpo.endswith(l) for l in _LATERALIDAD):
            return True
    return False


# Palabras de localización/lateralidad: si una línea de espécimen termina aquí
# (tras un procedimiento), describe el sitio, no un diagnóstico.
_LATERALIDAD = (
    "IZQUIERDO", "IZQUIERDA", "DERECHO", "DERECHA", "BILATERAL", "SUPERIOR",
    "INFERIOR", "PROXIMAL", "DISTAL", "ANTERIOR", "POSTERIOR", "MEDIAL",
    "LATERAL", "CENTRAL", "PROFUNDO", "PROFUNDA",
)


# ===================================================================
#  Resolución del LLM LOCAL (con guard anti-cloud)
# ===================================================================
import os
import configparser

_CFG_CACHE = None
_MODELO_CACHE = None


def _es_endpoint_local(url: str) -> bool:
    """¿El endpoint está dentro del hospital? (Ley 1581)

    V6.9.93 — delega en core/red_local.py. Antes esta funcion tenia su PROPIA
    implementacion con expresiones regulares, y la capa de polaridad tenia otra
    distinta y mas estricta: dos reglas para la misma decision de seguridad, que
    es como se acaba con una permitiendo lo que la otra prohibe. Ademas la de
    aqui se rompia con IPv6 entre corchetes (http://[::1]:1234 -> host '[')
    y no contemplaba 169.254.x.

    El nombre y la firma se mantienen porque core/biomarcadores_ia.py la importa.
    """
    from core.red_local import endpoint_dentro_del_hospital
    return endpoint_dentro_del_hospital(url)


def _leer_config():
    """Lee [llm] base_url/modelo de config/config.ini (best-effort)."""
    global _CFG_CACHE
    if _CFG_CACHE is not None:
        return _CFG_CACHE
    base_url, modelo = "http://127.0.0.1:1234/v1", ""
    aqui = os.path.dirname(os.path.abspath(__file__))
    candidatos = [
        os.path.join(aqui, "..", "config", "config.ini"),
        os.path.join(os.getcwd(), "config", "config.ini"),
    ]
    for ruta in candidatos:
        try:
            if os.path.isfile(ruta):
                cp = configparser.ConfigParser()
                cp.read(ruta, encoding="utf-8")
                if cp.has_section("llm"):
                    base_url = cp.get("llm", "base_url", fallback=base_url) or base_url
                    modelo = cp.get("llm", "modelo", fallback=modelo) or modelo
                break
        except Exception:
            continue
    _CFG_CACHE = (base_url.rstrip("/"), modelo.strip())
    return _CFG_CACHE


_HABILITADA_CACHE = None


def _ia_habilitada() -> bool:
    """Lee [extraccion] usar_ia_diagnostico de config.ini (default: True)."""
    global _HABILITADA_CACHE
    if _HABILITADA_CACHE is not None:
        return _HABILITADA_CACHE
    val = True
    # V6.9.93 — en el .exe (onefile) __file__ apunta al temporal _MEIPASS,
    # o sea al config EMPAQUETADO en tiempo de compilacion. El cliente
    # editaba dist/config/config.ini, veia cambiar la BD (db_adapter SI
    # contempla sys.frozen) y creia haber apagado la IA, pero los
    # interruptores seguian congelados al valor del build. Se usa la
    # MISMA raiz que db_adapter para que el fichero de al lado del .exe
    # mande sobre todo, no solo sobre la base de datos.
    try:
        from core.db_adapter import _get_base_path as _bp
        _raiz_cfg = str(_bp())
    except Exception:
        _raiz_cfg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    aqui = os.path.dirname(os.path.abspath(__file__))
    for ruta in (os.path.join(_raiz_cfg, "config", "config.ini"),
                 os.path.join(aqui, "..", "config", "config.ini"),
                 os.path.join(os.getcwd(), "config", "config.ini")):
        try:
            if os.path.isfile(ruta):
                cp = configparser.ConfigParser()
                cp.read(ruta, encoding="utf-8")
                if cp.has_option("extraccion", "usar_ia_diagnostico"):
                    val = cp.getboolean("extraccion", "usar_ia_diagnostico")
                break
        except Exception:
            pass
    _HABILITADA_CACHE = val
    return val


def _resolver_modelo(base_url: str, modelo_cfg: str) -> Optional[str]:
    """Devuelve el modelo a usar; autodetecta el cargado si no está en config."""
    global _MODELO_CACHE
    if _MODELO_CACHE is not None:
        return _MODELO_CACHE
    if modelo_cfg:
        _MODELO_CACHE = modelo_cfg
        return _MODELO_CACHE
    try:
        r = requests.get(f"{base_url}/models", timeout=6)
        ids = [m.get("id", "") for m in r.json().get("data", [])]
        # preferir un modelo de chat (no embedding)
        for mid in ids:
            if mid and "embed" not in mid.lower():
                _MODELO_CACHE = mid
                return _MODELO_CACHE
    except Exception as e:
        logging.warning(f"[dx-ia] no se pudo autodetectar modelo: {e}")
    return None


# ===================================================================
#  Extracción IA del diagnóstico real
# ===================================================================
# nemo/mistral NO acepta role=system -> se fusiona todo en un único mensaje user.
_INSTRUCCIONES = (
    "Eres un patólogo experto del Hospital Universitario del Valle. Lee el "
    "siguiente informe de inmunohistoquímica (IHQ) y extrae el DIAGNÓSTICO "
    "anatomopatológico FINAL: la entidad o lesión diagnosticada.\n\n"
    "REGLAS:\n"
    "1. El diagnóstico puede estar en la sección DIAGNÓSTICO (y sus viñetas) o "
    "en COMENTARIOS. Léelas TODAS.\n"
    "2. NO devuelvas resultados de marcadores (HER2, Ki-67, receptores de "
    "estrógeno/progesterona, MMR), NI la línea del espécimen ('Mucosa gástrica. "
    "Biopsia'), NI 'ver descripción/comentario'.\n"
    "3. Si es un IHQ de SEGUIMIENTO con solo panel de marcadores sobre un tumor "
    "conocido, infiere la entidad por el ÓRGANO + el panel (ej. órgano MAMA con "
    "ER/PR/HER2 -> 'CARCINOMA DE MAMA'; órgano ESTÓMAGO con HER2 -> "
    "'ADENOCARCINOMA GÁSTRICO').\n"
    "4. Si el informe es no concluyente, indica el hallazgo principal (ej. "
    "'LESIÓN ENDOTELIAL ATÍPICA, NEGATIVA PARA SARCOMA DE KAPOSI').\n"
    "5. Devuelve SOLO el diagnóstico, conciso y en MAYÚSCULAS.\n\n"
    'Responde ÚNICAMENTE con JSON válido: {"diagnostico": "<texto>"}'
)


def _parse_dx(texto: str) -> Optional[str]:
    """Extrae el campo diagnostico del JSON devuelto por el modelo."""
    if not texto:
        return None
    m = re.search(r'\{.*\}', texto, re.DOTALL)
    if m:
        try:
            obj = json.loads(m.group(0))
            dx = obj.get("diagnostico") or obj.get("diagnostico_principal") or obj.get("diagnosis")
            if dx and isinstance(dx, str):
                return dx.strip().strip('"').rstrip(".").strip()
        except Exception:
            pass
    # fallback: si no hubo JSON, usar la primera línea no vacía corta
    linea = texto.strip().splitlines()[0].strip() if texto.strip() else ""
    if 4 < len(linea) < 200 and "{" not in linea:
        return linea.strip('"').rstrip(".").strip()
    return None


def extraer_diagnostico_con_ia(full_text: str, organo: str = "", timeout: int = 120) -> Optional[str]:
    """Extrae el diagnóstico real del informe usando el LLM LOCAL.

    Devuelve el diagnóstico (str) o None si no se pudo (LLM caído, no local, etc.).
    """
    if requests is None or not full_text or not _ia_habilitada():
        return None
    base_url, modelo_cfg = _leer_config()
    # GUARD ANTI-CLOUD: nunca enviar datos médicos fuera de la red local.
    if not _es_endpoint_local(base_url):
        logging.warning(f"[dx-ia] endpoint NO local ({base_url}); se omite IA por seguridad (Ley 1581).")
        return None
    modelo = _resolver_modelo(base_url, modelo_cfg)
    if not modelo:
        return None

    contexto_organo = f"ÓRGANO DEL CASO: {organo}\n\n" if organo and organo not in ("N/A", "SIN DATO") else ""
    prompt = f"{_INSTRUCCIONES}\n\n{contexto_organo}INFORME:\n\"\"\"\n{full_text[:8000]}\n\"\"\""
    payload = {
        "model": modelo,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 400,
    }
    try:
        r = requests.post(f"{base_url}/chat/completions", json=payload, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        contenido = data["choices"][0]["message"].get("content", "")
        dx = _parse_dx(contenido)
        # Sanidad: el resultado IA no debe volver a ser "no válido"
        if dx and not es_diagnostico_no_valido(dx):
            return dx.upper()
        return None
    except Exception as e:
        logging.warning(f"[dx-ia] extracción IA falló: {e}")
        return None
