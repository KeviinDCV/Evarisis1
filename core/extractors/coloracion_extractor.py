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

# Inicio de la sección de diagnóstico. Tolera SIN tilde ("DIAGNOSTICO"), con tilde
# ("DIAGNÓSTICO") o mojibake, y un posible "." o ":" final ("DIAGNOSTICO.").
_RE_DIAG = re.compile(r"(?:^|\n)[ \t]*DIAGN[" + _ACC_O + r"]ST[" + _ACC_I + r"]CO[ \t]*[.:]?[ \t]*\n")

# Encabezado de continuación de página (multipágina): "Mxxxx / Copia|Final Pag. n de m / ...
# Fecha Informe : dd/mm/aaaa". Es RUIDO embebido — se borra ANTES de cortar la sección.
_RE_CONT_HEADER = re.compile(
    r"\n[ \t]*M\d+[ \t]*\n[ \t]*(?:Copia|Final)[ \t]+Pag\.\s*\d+\s+de\s+\d+"
    r".*?Fecha\s+Informe[ \t]*\n?[ \t]*:[ \t]*\d{2}/\d{2}/\d{4}",
    re.DOTALL | re.IGNORECASE,
)

# Pie legal estándar del informe (RUIDO).
_RE_PIE_LEGAL = re.compile(
    r"Todos\s+los\s+an[" + _ACC_A + r"]?lisis.*?(?:Oneworld\s+Accuracy|1WA)(?:\s*\(1WA\))?",
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
# V6.9.48 FIX M2506212: el salto de línea antes de "N. peticion" es OPCIONAL. En algunos
# PDFs el nombre queda PEGADO a la etiqueta en la misma línea ("…ORTIZ N. peticion"); con
# "\n" obligatorio el nombre no se capturaba (quedaba N/A). Recupera ~490 filas, 0 regresión.
_RE_NOMBRE = re.compile(r"Nombre\s*\n?\s*:\s*(.+?)\s*\n?\s*N\.?\s*petici", re.IGNORECASE | re.DOTALL)
_RE_GENERO = re.compile(r"Genero\s*\n?\s*:\s*([A-Za-z]+)", re.IGNORECASE)
_RE_EDAD = re.compile(r"Edad\s*\n?\s*:\s*(\d{1,3})", re.IGNORECASE)
_RE_FECHA_INF = re.compile(r"Fecha\s+Informe\s*\n?\s*:\s*(\d{2}/\d{2}/\d{4})", re.IGNORECASE)
# ── Órgano (columna "Organo" de la tabla "Estudios solicitados") ────────────
# V6.9.49 FIX órgano coloración: el ÓRGANO está en la columna "Organo" de la
# tabla "Estudios solicitados" (la misma sección que usa el flujo IHQ). El
# patrón anterior ("Formol…\n órgano \n fecha") solo acertaba ~69% porque fallaba con:
#   • órgano en varias líneas ("PIEL DE CUELLO"/"POSTERIOR")
#   • fecha pegada o en la misma línea ("BX DE PROSTATA DERECHA2025-04-01")
#   • Almacenamiento ≠ "Formol" ("Tejido en fresco", "Lamina", "Bloques y laminas", "Tubo Transfix")
#   • un mismo Nº M con VARIOS sub-estudios (-A/-B/…), cada uno con su órgano
# Enfoque estructural (independiente del vocabulario de Almacenamiento; validado
# en 6.806 casos de los 139 PDFs de coloración: 100% detección, 0 regresión):
# dentro de la tabla, cada sub-estudio empieza por el código de estudio ("898xxx …")
# y el ÓRGANO es la corrida de líneas EN MAYÚSCULAS que le sigue (Almacenamiento y
# el tipo de estudio SIEMPRE llevan minúsculas). Varios sub-estudios -> se
# concatenan los órganos distintos con " | ".
_RE_TABLA_ESTUDIOS = re.compile(
    r"Estudios solicitados(.*?)(?:INFORME DE ANATOM|DESCRIPCI[" + _ACC_O + r"]N\s+MACRO|\Z)",
    re.DOTALL | re.IGNORECASE,
)
_RE_FILA_ESTUDIO = re.compile(r"(?m)^\s*M\d{6,}(?:-[A-Za-z0-9]+)?\s*$")  # Nº de estudio (inicio de fila)
_RE_TIPO_ESTUDIO = re.compile(r"^\d{5,}\b")                              # línea "898101 Estudio de…"
_RE_FECHA_SOLA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_RE_ORG_Y_FECHA = re.compile(r"^(.+?)\s*\d{4}-\d{2}-\d{2}$")             # órgano + fecha en la misma línea

# ── Descripciones macro/micro (sección "INFORME DE ANATOMÍA PATOLÓGICA /
# ESTUDIO DE HISTOLOGIA") ────────────────────────────────────────────────────
# V6.9.49: encabezados de las descripciones. Toleran mojibake en la 'Ó' (igual que _RE_DIAG).
_RE_MACRO = re.compile(r"DESCRIPCI[" + _ACC_O + r"]N[ \t]+MACROSC[" + _ACC_O + r"]PICA")
_RE_MICRO = re.compile(r"DESCRIPCI[" + _ACC_O + r"]N[ \t]+MICROSC[" + _ACC_O + r"]PICA")
# Terminadores SEGUROS de una descripción: el siguiente encabezado real (MICRO/DIAG) + firma/nota.
# IMPORTANTE: NO se usa el terminador de firma "NOMBRE … Patólogo" (_TERMINADORES) porque el texto
# microscópico de los informes sinápticos menciona "COLEGIO AMERICANO DE PATÓLOGOS" y lo cortaría.
_RE_NOTA_INFORME = re.compile(r"\n[ \t]*Nota:\s*Este\s+informe", re.IGNORECASE)
_RE_COMENTARIOS = re.compile(r"\n[ \t]*COMENTARIOS?\b", re.IGNORECASE)
_RE_RESPONSABLE = re.compile(r"[ \t\n]*Responsable\s+del\s+an", re.IGNORECASE)
_RE_LINEA_FIRMA = re.compile(r"\n_{3,}")
_TERM_DESCRIPCION = (_RE_NOTA_INFORME, _RE_COMENTARIOS, _RE_RESPONSABLE, _RE_LINEA_FIRMA)


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


# ═══════════════════════════════════════════════════════════════════════════
# V6.9.73 — quitar el RÓTULO DEL ESPÉCIMEN del diagnóstico.
#
# La sección DIAGNÓSTICO del informe empieza describiendo la muestra:
#     Mucosa gástrica antral. Biopsia por endoscopia.      <- rótulo
#     GASTRITIS CRÓNICA NO ATRÓFICA…                       <- el diagnóstico
# Se guardaba el bloque entero, así que en la tabla se leía "Mucosa gástrica
# antral. Biopsia por endoscopia." donde debía ir el diagnóstico. Medido sobre
# los 20.455 casos reales: afecta a 15.246 (75%).
#
# Se borran LÍNEAS COMPLETAS, nunca trozos: una línea es rótulo solo si TERMINA
# nombrando el procedimiento con el que se tomó la muestra. Y se exige además
# que NO contenga ningún término diagnóstico —medido: 0 de las 19.960 líneas
# quitadas lo contenía—, así que un dx que mencione el procedimiento de pasada
# ("PÓLIPO HIPERPLÁSICO, POLIPECTOMÍA COMPLETA") jamás se pierde.
#
# En informes multi-espécimen (A., B., C.…) se quita el rótulo de CADA uno y se
# conservan todos los diagnósticos.
# ═══════════════════════════════════════════════════════════════════════════
_PROC_ROTULO = (
    r'BIOPSIA|RESECCI[OÓ]N|POLIPECTOM[IÍ]A|MUCOSECTOM[IÍ]A|CUADRANTECTOM[IÍ]A|'
    r'MASTECTOM[IÍ]A|COLONOSCOPIA|ENDOSCOPIA|LEGRADO|CONIZACI[OÓ]N|HISTERECTOM[IÍ]A|'
    r'SACABOCADO|TRUCUT|TREPANACI[OÓ]N|CURETAJE|PUNCI[OÓ]N|CITOLOG[IÍ]A|ESCISI[OÓ]N|'
    r'APENDICECTOM[IÍ]A|COLECISTECTOM[IÍ]A|AMPUTACI[OÓ]N|NEFRECTOM[IÍ]A|LOBECTOM[IÍ]A|'
    r'PROSTATECTOM[IÍ]A|ORQUIECTOM[IÍ]A|GASTRECTOM[IÍ]A|TIROIDECTOM[IÍ]A|MOHS|'
    r'CIRUG[IÍ]A|EXTIRPACI[OÓ]N|TORACOSCOPIA|LAPAROSCOPIA|VITRECTOM[IÍ]A'
)
_RE_ROTULO_LINEA = re.compile(
    r'(?i)^(?:[A-Z]\s*[.\-)]\s*)?[^\n]{0,150}?\b(?:' + _PROC_ROTULO + r')\b'
    r'(?:\s+(?:por|con|de|end\w+|escisional|incisional|percut[aá]nea|'
    r'aguja\s+gruesa|sacabocado|endosc[oó]pica|guiada[^\n]{0,30}))?\s*[.:;]?\s*$')
_RE_TERMINO_DX = re.compile(
    r'(?i)CARCINOM|SARCOM|LINFOM|MELANOM|MIELOM|LEUCEMI|BLASTOM|ADENOM|'
    r'NEOPLASI|TUMOR\w*\s|HIPERPLASI|DISPLASI|INFLAMAC|GRANULOM|POLIPO|'
    r'P[OÓ]LIPO|GASTRITIS|COLITIS|DERMATITIS|CERVICITIS|NEGATIV|POSITIV|'
    r'BENIGN|MALIGN|ATIPI|METAPLASI|FIBROSIS|NECROSIS|QUISTE|NEVUS|'
    r'CONDILOM|PAPILOM|LIPOM|HEMANGIOM|MIOM|ADENOSIS|COMPATIBLE|SUGESTIV')


def quitar_rotulo_especimen(dx: str) -> str:
    """Quita las líneas de rótulo del espécimen. Si al hacerlo NO quedaría nada,
    devuelve el texto original: es preferible mostrar el rótulo a dejar el
    diagnóstico vacío (el informe no traía otra cosa)."""
    if not dx:
        return dx
    quedan = [ln for ln in dx.split("\n")
              if not (ln.strip() and _RE_ROTULO_LINEA.match(ln.strip())
                      and not _RE_TERMINO_DX.search(ln))]
    limpio = "\n".join(quedan).strip()
    return limpio if limpio else dx


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
    # OJO: aquí se devuelve el bloque COMPLETO, con el rótulo del espécimen.
    # El rótulo es la única fuente del Procedimiento ("…Biopsia por endoscopia")
    # y lo consumen extraer_procedimiento() y clasificar_malignidad(). Quitarlo
    # aquí costaría 13.839 procedimientos (medido). Se quita en agrupar_y_extraer,
    # justo al guardar el campo del diagnóstico. Ver quitar_rotulo_especimen().
    return _limpiar_dx(cuerpo)


def _limpiar_descripcion(bloque: str) -> str:
    """Colapsa saltos/espacios a un párrafo de una sola línea (para celda de tabla)."""
    return re.sub(r"\s+", " ", bloque).strip()


def _extraer_seccion(texto_caso: str, ini_rgx, fin_rgxs) -> str:
    """Aísla el bloque entre 'ini_rgx' y el primer terminador de 'fin_rgxs'. Borra antes
    el ruido embebido (headers de continuación + pie legal). Devuelve '' si no está."""
    if not texto_caso:
        return ""
    t = _RE_CONT_HEADER.sub("\n", texto_caso)
    t = _RE_PIE_LEGAL.sub("\n", t)
    m = ini_rgx.search(t)
    if not m:
        return ""
    cuerpo = t[m.end():]
    fin = len(cuerpo)
    for rgx in fin_rgxs:
        mm = rgx.search(cuerpo)
        if mm and mm.start() < fin:
            fin = mm.start()
    return _limpiar_descripcion(cuerpo[:fin])


def extraer_descripcion_macro(texto_caso: str) -> str:
    """DESCRIPCIÓN MACROSCÓPICA del informe de histología. '' si no está (no inventa)."""
    return _extraer_seccion(texto_caso, _RE_MACRO, (_RE_MICRO, _RE_DIAG) + _TERM_DESCRIPCION)


def extraer_descripcion_micro(texto_caso: str) -> str:
    """DESCRIPCIÓN MICROSCÓPICA del informe de histología. '' si no está (no inventa)."""
    return _extraer_seccion(texto_caso, _RE_MICRO, (_RE_DIAG,) + _TERM_DESCRIPCION)


def clasificar_malignidad(diagnostico: str, microscopica: str = "") -> str:
    """Malignidad ('BENIGNO'/'MALIGNO') REUTILIZANDO la MISMA lógica auditada de IHQ
    (core.extractors.medical_extractor.determine_malignancy) — una sola fuente de verdad.

    Se clasifica desde el DIAGNÓSTICO (conclusión del patólogo). Si no hay diagnóstico,
    se usa la microscópica como respaldo. IMPORTANTE: NO se pasan macro/micro como fuente
    primaria — su texto descriptivo dispara falsos positivos en el scoring afinado para IHQ
    (validado en 6.806 casos: dx-only da 82.7% BENIGNO / 17.3% MALIGNO, sin los FP de macro+micro).
    Sin información -> 'BENIGNO' (criterio conservador, idéntico al de IHQ)."""
    texto = (diagnostico or "").strip()
    if not texto or texto == "REVISAR":
        texto = (microscopica or "").strip()
    if not texto:
        return "BENIGNO"
    try:
        from core.extractors.medical_extractor import determine_malignancy
        return determine_malignancy(texto, "", "", "")
    except Exception:
        return "BENIGNO"


# ── Procedimiento (BIOPSIA / CIRUGÍA / CONGELACIÓN) ───────────────────────────
# V6.9.51: el "Procedimiento" del caso (MISMO campo que llena el flujo IHQ) se
# infiere del DIAGNÓSTICO (y, de respaldo, la macroscópica), que nombran el
# procedimiento REAL del espécimen: "Próstata. Resección transuretral.",
# "Vesícula biliar. Colecistectomía.", "Mucosa gástrica antral. Biopsia
# endoscópica". Se reutiliza la MISMA semántica del flujo IHQ (verbo quirúrgico ->
# CIRUGÍA; biopsia/BX -> BIOPSIA), extendida con los verbos vistos en coloración.
# NO se usa la columna "Tipo estudio" ("...en biopsia/en especimen") porque es la
# categoría de laboratorio, no el procedimiento clínico (y "especimen" es genérico).
# Las clases de acento toleran el mojibake ('�') igual que el resto del módulo.
# '' si no se puede determinar (no inventa).
_RE_PROC_CIRUGIA = re.compile(
    r"(?i)\b(?:"
    # Cualquier "-ectomía" es extirpación quirúrgica de un órgano/lesión: cubre
    # colecistectomía, histerectomía, prostatectomía, tiroidectomía, hemitiroidectomía,
    # hemorroidectomía, mastectomía, nefrectomía, lobectomía, etc. La 'p?' tolera la
    # errata de OCR "salpingectompía". NO se usa "-tomía" genérico: chocaría con
    # "anaTOMÍA" del encabezado "INFORME DE ANATOMÍA PATOLÓGICA".
    r"[a-záéíóúñü�]*ectomp?[" + _ACC_I + r"]a|"
    r"apendic[a-z�]*tom[" + _ACC_I + r"]a|"   # apendicectomía y la errata "apendicetomía" (sin 'c')
    r"resecci[" + _ACC_O + r"]n|extirpaci[" + _ACC_O + r"]n|ex[eé�]resis|amputaci[" + _ACC_O + r"]n|"
    r"escisi[" + _ACC_O + r"]n|decorticaci[" + _ACC_O + r"]n|conizaci[" + _ACC_O + r"]n|vaciamiento"
    r")\b"
)
# 'sacabocado' = biopsia por punch (dermatopatología); 'biosia' = errata OCR de 'biopsia'.
_RE_PROC_BIOPSIA = re.compile(r"(?i)\b(?:biopsia|biosia|bx|sacabocado|punci[" + _ACC_O + r"]n|legrado|curetaje|endosc[" + _ACC_O + r"]pica)\b")
_RE_PROC_CONGELA = re.compile(r"(?i)congelaci[" + _ACC_O + r"]n")

# ── V6.9.52 FALLBACK aditivo (NO reemplaza los patrones de arriba) ─────────────
# Los patrones ORIGINALES corren PRIMERO e intactos: si clasifican, se devuelve su
# resultado sin tocar. Estos patrones de RESPALDO SOLO se evalúan cuando el caso
# quedó en "" — así es imposible reclasificar un caso ya resuelto (0 regresión,
# validado sobre 6.806 casos: 6.629→6.695 con procedimiento, 66 vacíos→valor,
# 0 flips, 0 obstétricos tocados). Cubren verbos quirúrgicos/de muestreo que el
# vocabulario original no listaba, más variantes de OCR (reseción sin doble-c,
# amputació sin 'n', biospia, omentent/mucosesct/amidelect-ectomía) y plurales.
# Filosofía intacta: si NO hay verbo de procedimiento en el texto, se deja "".
_RE_PROC_CIRUGIA_FB = re.compile(
    r"(?i)(?:"
    r"[a-záéíóúñü]*plastia"                         # mamoplastia, pieloplastia, septoplastia, timpanoplastia
    r"|enucleaci[o" + "ó" + r"]n|evisceraci[oó]n|exenteraci[oó]n"
    r"|reseci[oó]n"                                 # OCR "reseción" (una c; la doble-c ya la ve el patrón original)
    r"|amputaci[a-zñ]*"                             # amputación / OCR "amputació" (sin 'n')
    r"|anastomosis|ostom[ií]a"                      # colostomía, ileostomía, vesicostomía, timpanostomía
    r"|reconstrucci[oó]n|reconstruct"
    r"|explantaci[oó]n|laparoscop"
    r"|recambio\s+valvular"
    r"|correcci[oó]n\s+de\b"
    r"|ampliaci[oó]n\s+quir[uú]rgic|quir[uú]rgic"
    r"|extracci[oó]n"
    r"|\bcono\b|\blletz\b|cono\s+lleep|cono\s+lleitz"   # cono/LEEP cervical (excisión)
    r"|pomeroy"
    r"|omenten?tecom[ií]a|omentectom[ií]a"          # OCR omentectomía
    r"|mucos[a-z]*ectom[ií]a|mucosesctom[ií]a"      # (muco)sectomía y su OCR
    r"|amidelectom|amigdalectom|amidalectom"        # amigdalectomía y OCR
    r")"
)
_RE_PROC_BIOPSIA_FB = re.compile(r"(?i)(?:biospia|biopsias|sacabocados|colposcopia|drenaje)")


def extraer_procedimiento(diagnostico: str, macroscopica: str = "") -> str:
    """Procedimiento del caso ('CIRUGÍA' / 'BIOPSIA' / 'CONGELACIÓN') inferido del
    texto del diagnóstico (+macroscópica de respaldo), con la MISMA semántica del
    flujo IHQ. Devuelve '' si no se puede determinar (no inventa)."""
    texto = f"{diagnostico or ''}\n{macroscopica or ''}"
    # 1) Patrones ORIGINALES (intactos) — máxima prioridad.
    if _RE_PROC_CIRUGIA.search(texto):
        return "CIRUGÍA"
    if _RE_PROC_BIOPSIA.search(texto):
        return "BIOPSIA"
    if _RE_PROC_CONGELA.search(texto):
        return "CONGELACIÓN"
    # 2) V6.9.52 FALLBACK — solo si lo anterior no clasificó (llena vacíos, no reclasifica).
    if _RE_PROC_CIRUGIA_FB.search(texto):
        return "CIRUGÍA"
    if _RE_PROC_BIOPSIA_FB.search(texto):
        return "BIOPSIA"
    return ""


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


def _es_texto_organo(s: str) -> bool:
    """True si la línea parece un valor de ÓRGANO: SIN minúsculas (Almacenamiento y
    tipo de estudio siempre las tienen) y con al menos una mayúscula."""
    s = s.strip()
    if not s:
        return False
    if re.search(r"[a-záéíóúñü]", s):
        return False
    return bool(re.search(r"[A-ZÁÉÍÓÚÑ]", s))


def _organo_de_fila(row: str) -> str:
    """Órgano de UN sub-estudio (bloque de texto entre dos Nº de estudio de la tabla).
    Salta el tipo de estudio ("898xxx …") y la línea de Almacenamiento, y devuelve la
    corrida de líneas en MAYÚSCULAS (uniendo órganos multilínea y quitando la fecha)."""
    lineas = row.split("\n")
    ini = 0
    for i, ln in enumerate(lineas):
        if _RE_TIPO_ESTUDIO.match(ln.strip()):
            ini = i + 1
            break
    else:
        ini = 1 if lineas and lineas[0].strip().upper().startswith("ESTUDIO") else 0
    org: List[str] = []
    visto = False
    for ln in lineas[ini:]:
        s = ln.strip()
        if not s:
            if visto:
                break
            continue
        if _RE_FECHA_SOLA.match(s):          # fecha en su propia línea -> fin del órgano
            break
        mf = _RE_ORG_Y_FECHA.match(s)        # órgano con la fecha pegada/al final
        if mf:
            cand = mf.group(1).strip()
            if _es_texto_organo(cand):
                org.append(cand)
                visto = True
            break
        if _es_texto_organo(s):
            org.append(s)
            visto = True
        elif visto:                          # se acabó la corrida de mayúsculas del órgano
            break
        # si no: Almacenamiento/continuación previa al órgano -> seguir saltando
    return re.sub(r"\s+", " ", " ".join(org)).strip()


def extraer_organo(texto_caso: str) -> str:
    """ÓRGANO desde la columna "Organo" de la tabla "Estudios solicitados".
    Si el Nº M tiene varios sub-estudios (-A/-B/…), concatena los órganos DISTINTOS
    con " | " (conserva el orden). Devuelve "" si no hay tabla/órgano (no inventa)."""
    if not texto_caso:
        return ""
    mt = _RE_TABLA_ESTUDIOS.search(texto_caso)
    region = mt.group(1) if mt else ""
    if not region:
        return ""
    marcas = list(_RE_FILA_ESTUDIO.finditer(region))
    try:  # V6.9.54: normalizar procedimiento->órgano (TIROIDECTOMIA TOTAL -> TIROIDES)
        from core.extractors.medical_extractor import normalizar_organo as _norm_org
    except Exception:
        _norm_org = lambda x: x
    organos: List[str] = []
    for i, mk in enumerate(marcas):
        desde = mk.end()
        hasta = marcas[i + 1].start() if i + 1 < len(marcas) else len(region)
        org = _organo_de_fila(region[desde:hasta])
        if org and org not in ("ORGANO", "FECHA TOMA"):
            org = _norm_org(org) or org
            if org not in organos:
                organos.append(org)
    return " | ".join(organos)


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
    org = extraer_organo(texto_caso)
    if org:
        d["Organo"] = org
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
            # V6.9.73: el campo guarda el DIAGNÓSTICO sin el rótulo del espécimen.
            # `dx` (con rótulo) se sigue usando más abajo para derivar Procedimiento
            # y Malignidad, que es donde el rótulo sí hace falta.
            "diagnostico_coloracion_2": quitar_rotulo_especimen(dx) if dx else "REVISAR",
        }
        macro = extraer_descripcion_macro(texto)
        if macro:
            reg["Descripcion macroscopica"] = macro
        micro = extraer_descripcion_micro(texto)
        if micro:
            reg["Descripcion microscopica"] = micro
        reg["Malignidad"] = clasificar_malignidad(dx, micro)
        proc = extraer_procedimiento(dx, macro)
        if proc:
            reg["Procedimiento"] = proc
        reg.update(extraer_demografia(texto))
        casos.append(reg)
    return casos
