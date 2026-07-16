# -*- coding: utf-8 -*-
"""V6.9.61 — POLARIDAD DE BIOMARCADORES CON IA LOCAL + GUARDA DE CITA VERBATIM.

POR QUÉ EXISTE
--------------
El texto del PDF se lee PERFECTO (100% capa nativa, 0% OCR). El fallo nunca estuvo
en leer, sino en INTERPRETAR. Acertar la polaridad exige comprender la frase:

  · "sin pérdida de expresión de CD2 y CD7"            -> CD7 es POSITIVO (¡dice "pérdida"!)
  · "El CD34 resalta los vasos ... sin marcación
     dentro de la lesión"                              -> NEGATIVO (¡dice "resalta"!)
  · "positividad para PSA y Racemasa con negatividad
     para CK7, CK20"                                   -> cruce de polaridad en la misma frase
  · negatividad en el componente tumoral + positividad
     en el epitelio benigno residual                   -> el mismo marcador, dos compartimentos

Medido sobre 60 discrepancias adjudicadas contra el informe: el extractor por regex
acierta el 40%; un parser de cláusulas afinado, el 60%. Ninguno es clínicamente
aceptable. Es comprensión de lenguaje, no coincidencia de patrones.

LA GUARDA (esto es lo que lo hace seguro)
-----------------------------------------
La IA de DIAGNÓSTICO se desactivó porque ALUCINABA: generaba texto libre y no había
con qué contrastarlo. Aquí el riesgo es estructuralmente distinto y se acota así:

  1. CLASIFICACIÓN CERRADA: solo POSITIVO | NEGATIVO | NO_DICE. No genera texto libre.
  2. VOCABULARIO CERRADO: solo puede opinar sobre marcadores que YA sabemos que el
     informe nombra (los pasa el llamador, verificados con el matcher de alias).
  3. CITA OBLIGATORIA VERBATIM: debe devolver el fragmento del informe que sustenta
     su veredicto, y aquí se comprueba que ese fragmento esté LITERALMENTE en el texto.
     Si no está -> se DESCARTA el veredicto. Una alucinación no puede sobrevivir.

Nunca inventa un valor: en la duda devuelve NO_DICE y el llamador conserva lo que ya
tenía. Solo puede AFIRMAR con respaldo textual comprobado.

Datos confidenciales: el proveedor es LOCAL (LM Studio/Ollama). Nada sale del hospital.
"""
from __future__ import annotations

import json
import logging
import os
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

VEREDICTOS = ('POSITIVO', 'NEGATIVO', 'NO_DICE')

# Una cita solo sustenta un veredicto si AFIRMA UN RESULTADO. Las frases de
# procedimiento ("se realizan niveles histológicos para tinción con…") nombran el
# marcador sin decir nada de él. (Se aplica sobre la cita ya normalizada: sin tildes.)
_RESULTADO_EN_CITA = re.compile(
    r'positiv|negativ|inmunorreactiv|inmunoreactiv|reactivid|expres|marcaci|marca\b|tin[ec]|'
    r'sobreexpres|ausen|perdida|conservad|intact|resalta|realza|score|\d\s*%|\+|no\s+presentan?|'
    r'no\s+se\s+observ|sin\s+')

# ── Guarda: POSITIVO atribuido a una población que NO es el tumor ──────────
# La causa de 6 de los 8 errores que la verificación adversarial cazó: el marcador tiñe
# vasos/estroma/basales y la IA lo daba por positivo DEL TUMOR.
#   "Positividad en las paredes vasculares para CD34"   -> CD34 NEGATIVO en el tumor
#   "positividad estromal difusa para S100"             -> S100  NEGATIVO en el tumor
#   "p40 es positivo en los queratinocitos basales"     -> p40   NEGATIVO en el tumor
# Se intentó resolver reforzando el prompt: el modelo se volvió tan cauto que la cobertura
# cayó de 46 a 26 sobre 60 (arreglaba 1 de 8) -> peor en neto. Se resuelve en CÓDIGO.
#
# OJO — 'linfocitos' NO entra a propósito: en un LINFOMA el tumor SON los linfocitos y
# rechazar "linfocitos B positivos para CD20" destruiría positivos legítimos.
_POBLACION_NO_TUMORAL = re.compile(
    r'pared(?:es)?\s+vascular|vasos\s+(?:sanguineos|acompanantes)|endotelial|endotelio|'
    r'estromal|del\s+estroma|queratinocitos?\s+basal|celulas\s+basales|mastocitos|'
    r'histiocitos|control\s+interno|epitelio\s+(?:benigno|residual|normal)|'
    r'hepatocitos\s+(?:normales|no\s+tumorales)')
_ES_EL_TUMOR = re.compile(
    r'tumoral|neoplasic|lesional|de\s+la\s+lesion|celulas\s+atipicas|del\s+tumor|carcinom')


def _positivo_de_otra_poblacion(cita_norm: str) -> bool:
    """True si la cita atribuye la marcación a una población NO tumoral y no menciona
    el tumor -> ese POSITIVO no es del tumor y no debe aplicarse."""
    return bool(_POBLACION_NO_TUMORAL.search(cita_norm)) and not _ES_EL_TUMOR.search(cita_norm)

_PROMPT = """Eres patólogo. Lee el INFORME y di qué afirma sobre CADA marcador de la LISTA.

Para cada marcador responde:
- "POSITIVO": el informe afirma positividad / expresión / inmunorreactividad / marcación.
- "NEGATIVO": el informe afirma negatividad / sin expresión / sin marcación / pérdida de expresión.
- "NO_DICE" : el marcador solo aparece en la lista de estudios SOLICITADOS (p.ej. "se realizan
  niveles histológicos para tinción con X, Y, Z"), o no hay resultado claro para él.

REGLAS:
1. Usa SOLO el informe. No uses conocimiento médico externo para deducir un resultado.
2. Listas con polaridad cruzada: "positivas para A, B; negativas para C, D" -> C y D son NEGATIVOS.
3. "sin pérdida de expresión de X" -> X es POSITIVO (la expresión está conservada).
   "pérdida de X limitada a escasas células" -> X es POSITIVO (la expresión se conserva en el resto).

4. Si un marcador tiñe estructuras de control/acompañantes (vasos, estroma, queratinocitos
   basales) pero NO la lesión, es NEGATIVO.
5. Si el resultado difiere por compartimento, responde por las CÉLULAS TUMORALES/lesionales.
6. Si HAY marcación aunque sea escasa, débil, focal, parcheada o heterogénea -> POSITIVO
   (hay expresión). Solo es NEGATIVO si el informe dice que NO hay marcación.
7. Ante cualquier duda: NO_DICE. Es preferible NO_DICE a equivocarse.
8. "cita" DEBE ser un fragmento COPIADO LITERALMENTE del informe (mismas palabras, mismo orden).
   Si no puedes copiar una cita literal que lo sustente, el veredicto es NO_DICE con cita "".

Responde SOLO un array JSON, sin nada más:
[{{"marcador":"<nombre exacto de la lista>","veredicto":"POSITIVO|NEGATIVO|NO_DICE","cita":"<fragmento literal del informe>"}}]

LISTA DE MARCADORES: {marcadores}

INFORME:
\"\"\"
{informe}
\"\"\"
"""

# ── SEGUNDA LENTE (V6.9.63) ────────────────────────────────────────────────
# MISMA tarea, encuadre distinto: en vez de dar reglas, obliga a RECORRER un procedimiento
# (localizar frases -> elegir la que reporta -> mirar la cláusula -> mirar la población).
# A temperatura 0 el modelo es determinista: para tener una segunda opinión REAL hay que
# cambiar el PROMPT, no la semilla.
# Medido sobre 80 casos difíciles: cuando ambas lentes coinciden acierta ~94%; cuando
# discrepan, la respuesta es dudosa el 62% de las veces -> ese desacuerdo es la SEÑAL de
# "no sé", y es lo que manda el caso a revisión en vez de adivinar.
_PROMPT_LENTE_B = """Eres patólogo. Para CADA marcador de la LISTA, localiza en el INFORME la
frase que habla de él y decide a qué cláusula pertenece.

Procede así, marcador por marcador:
1. Busca TODAS las frases del informe donde aparece el marcador.
2. Quédate con la que reporta un RESULTADO (no con la que PIDE el estudio:
   "se realizan niveles para tinción con X, Y" es una petición, no un resultado).
3. Mira si el marcador cae en la parte POSITIVA o en la NEGATIVA de esa frase.
   Las listas cruzan polaridad: "positivas para A, B; negativas para C, D" -> C y D NEGATIVOS.
4. Comprueba de qué POBLACIÓN habla: si tiñe vasos, estroma o queratinocitos basales pero
   NO la lesión -> NEGATIVO. (En un LINFOMA los linfocitos SON el tumor.)
5. "sin pérdida de expresión de X" -> X POSITIVO (la expresión está conservada).
6. Si no puedes copiar una cita LITERAL del informe que lo sustente -> NO_DICE.

Responde SOLO un array JSON, sin nada más:
[{{"marcador":"<de la lista>","veredicto":"POSITIVO|NEGATIVO|NO_DICE","cita":"<literal del informe>"}}]

LISTA DE MARCADORES: {marcadores}

INFORME:
\"\"\"
{informe}
\"\"\"
"""


# El coste de cada llamada lo domina el TAMAÑO del prompt: informe de 7.000 chars = 40 s;
# de 1.500 = 16 s. El encabezado (datos del paciente), la lista de estudios solicitados y el
# pie legal no dicen NADA sobre la polaridad y encarecen la llamada 2,5x. Se manda solo la
# zona donde están los resultados.
_INI_RESULTADOS = re.compile(
    r'(?i)(DESCRIPCI[OÓ]N\s+MICROSC[OÓ]PICA|MICROSC[OÓ]PICO|INMUNOHISTOQU[IÍ]MICA\s*:|'
    r'RESULTADO\s+DE\s+INMUNO)')
_FIN_RESULTADOS = re.compile(
    r'(?i)(La\s+informaci[oó]n\s+contenida|depende\s+de\s+la\s+representatividad|'
    r'Este\s+informe\s+(?:es|no)|FIRMA\s+DIGITAL|Patólogo\(a\)|Elaborado\s+por)')


def zona_resultados(texto: str, minimo: int = 400) -> str:
    """Recorta el informe a la zona con los RESULTADOS (microscópica + comentarios +
    diagnóstico), fuera encabezado y pie legal. Si el recorte queda demasiado corto o no
    encuentra las marcas, devuelve el texto completo: mejor lento que ciego."""
    if not texto:
        return texto
    m = _INI_RESULTADOS.search(texto)
    ini = m.start() if m else 0
    f = _FIN_RESULTADOS.search(texto, ini)
    fin = f.start() if f else len(texto)
    z = texto[ini:fin].strip()
    return z if len(z) >= minimo else texto


def _norm(s: str) -> str:
    """Normaliza para comparar la cita con el informe: sin tildes, sin mayúsculas,
    espacios colapsados y puntuación de adorno fuera. La cita debe seguir siendo el
    MISMO texto; esto solo tolera diferencias tipográficas, no cambios de contenido."""
    s = unicodedata.normalize('NFKD', str(s or '')).encode('ascii', 'ignore').decode()
    s = s.lower()
    s = re.sub(r'[^a-z0-9%+/.\-]+', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()


def _clave_norm(nombre: str) -> str:
    """Nombre de marcador comparable: sin separadores ni sufijos de columna.
    La IA responde 'CA19-9', 'CKAE1/AE3', 'P40'; nuestras claves son 'CA19_9',
    'CKAE1AE3', 'P40_ESTADO'. Sin esto se rechazaban veredictos CORRECTOS."""
    s = _norm(nombre).upper()
    s = re.sub(r'(?:_|\s)?(?:ESTADO|PORCENTAJE)$', '', s)
    return re.sub(r'[^A-Z0-9]', '', s)


def _equivalentes(clave: str) -> set:
    """Todas las formas con las que la IA puede nombrar este marcador (nombre + alias
    reales de los informes). La IA responde 'CKAE1E3' donde la columna es 'CKAE1AE3',
    o 'IDH' donde es 'IDH1'. Reusa la tabla de alias del extractor: no inventa nada,
    solo reconoce el mismo marcador escrito de otra forma."""
    formas = {clave}
    try:
        from core.extractors.biomarker_extractor import BIOMARKER_DEFINITIONS, _ALIAS_PDF
    except Exception:
        return {_clave_norm(f) for f in formas}
    base = clave[4:] if clave.upper().startswith('IHQ_') else clave
    for fuente in (base, _clave_norm(base)):
        d = BIOMARKER_DEFINITIONS.get(fuente) or {}
        for a in (d.get('nombres_alternativos') or []):
            formas.add(str(a))
        for a in _ALIAS_PDF.get(fuente, []):
            formas.add(a)
    return {k for k in (_clave_norm(f) for f in formas) if k}


def _cita_respaldada(cita: str, informe_norm: str, marcador: str) -> bool:
    """LA GUARDA ANTI-ALUCINACIÓN. La IA solo puede AFIRMAR lo que el informe respalda.

    Nivel 1 — la cita está LITERAL en el informe: se acepta.

    Nivel 2 — la IA abrevia una lista y no copia literal. Caso real y benigno:
      informe: "no presentan inmunomarcación para EMA, GFAP, S100, CKAE1/AE3"
      cita IA: "No presentan inmunomarcación para GFAP"        (veredicto correcto)
    Aceptar sin más sería abrir la puerta a inventar. Así que se exige ANCLAJE REAL:
      (a) un tramo CONTIGUO y LITERAL de >=4 palabras de la cita existe en el informe, y
      (b) el marcador aparece en el informe DENTRO de esa misma frase.
    O sea: la IA comprende, pero la afirmación se verifica contra el texto del PDF.
    Una cita fabricada no supera (a); un marcador ajeno a la frase no supera (b).
    """
    c = _norm(cita)
    if not c or len(c.split()) < 3:
        return False
    # Nivel 0: la cita debe EXPRESAR UN RESULTADO. Una frase de procedimiento
    # ("se realiza estudios de inmunohistoquímica en la plataforma automatizada…")
    # menciona el marcador pero no afirma nada sobre él: no puede sustentar un
    # veredicto. Sin esto, la IA respaldaba polaridades con la frase del panel.
    if not _RESULTADO_EN_CITA.search(c):
        return False
    if c in informe_norm:                                    # Nivel 1: literal
        return True

    pal = c.split()
    clave = _clave_norm(marcador)
    if not clave:
        return False
    for n in range(len(pal), 3, -1):                          # tramo contiguo más largo, >=4 palabras
        for i in range(len(pal) - n + 1):
            tramo = ' '.join(pal[i:i + n])
            # TODAS las ocurrencias del tramo, no solo la primera: una frase genérica
            # ("las celulas tumorales son negativas para") aparece varias veces en el
            # informe y anclar en la primera hacía rechazar citas VÁLIDAS (era el 25%
            # de los rechazos: el marcador estaba en OTRA ocurrencia de la misma frase).
            pos = informe_norm.find(tramo)
            while pos >= 0:
                ini = informe_norm.rfind('.', 0, pos) + 1
                fin = informe_norm.find('.', pos + len(tramo))
                frase = informe_norm[ini: fin if fin > 0 else len(informe_norm)]
                if clave in re.sub(r'[^a-z0-9]', '', frase).upper():
                    return True
                pos = informe_norm.find(tramo, pos + 1)
    return False


def _parsear_json(raw: str) -> Optional[list]:
    """Extrae el array JSON de la respuesta (el modelo a veces lo envuelve en prosa/```).
    Tolera el array TRUNCADO por max_tokens: rescata los objetos completos que haya."""
    if not raw:
        return None
    m = re.search(r'\[.*\]', raw, re.DOTALL)
    if m:
        try:
            d = json.loads(m.group(0))
            if isinstance(d, list):
                return d
        except json.JSONDecodeError:
            pass
    # respuesta cortada a media lista: recuperar los objetos {…} bien formados
    filas = []
    for om in re.finditer(r'\{[^{}]*\}', raw, re.DOTALL):
        try:
            o = json.loads(om.group(0))
            if isinstance(o, dict):
                filas.append(o)
        except json.JSONDecodeError:
            continue
    return filas or None


def clasificar_polaridad(informe: str,
                         marcadores: List[str],
                         llm_call,
                         max_informe: int = 7000,
                         max_por_llamada: int = 8,
                         plantilla: Optional[str] = None) -> Dict[str, Tuple[str, str]]:
    """Devuelve {marcador: (veredicto, cita)} SOLO para los veredictos con cita verificada.

    informe    : texto del informe (tal como se leyó del PDF).
    marcadores : nombres que el informe SÍ nombra (el llamador ya lo verificó).
    llm_call   : fn(prompt:str) -> str  (respuesta cruda del LLM LOCAL).

    Un marcador ausente del resultado = "no me consta" -> el llamador conserva su valor.
    NUNCA se devuelve un veredicto cuya cita no esté literal en el informe.
    """
    if not informe or not marcadores:
        return {}

    # Trocear: con muchos marcadores a la vez el modelo pierde calidad y la respuesta
    # se trunca a media lista. Medido: en lotes pequeños recupera veredictos correctos
    # que antes se perdían.
    if len(marcadores) > max_por_llamada:
        out: Dict[str, Tuple[str, str]] = {}
        for i in range(0, len(marcadores), max_por_llamada):
            out.update(clasificar_polaridad(informe, marcadores[i:i + max_por_llamada],
                                            llm_call, max_informe, max_por_llamada, plantilla))
        return out

    # Recortar a la zona de resultados abarata la llamada 2,5x… pero el 4% de los
    # marcadores vive fuera de ella (p.ej. solo en el DIAGNÓSTICO) y se perderían.
    # Si ALGUNO de los que preguntamos no está en la zona, se manda el informe entero:
    # ahorrar tiempo no puede costar cobertura.
    txt = zona_resultados(informe)
    _z = _norm(txt)
    if any(_clave_norm(m) not in re.sub(r'[^a-z0-9]', '', _z).upper() for m in marcadores):
        txt = informe
    txt = txt[:max_informe]
    prompt = (plantilla or _PROMPT).format(marcadores=', '.join(marcadores), informe=txt)
    try:
        raw = llm_call(prompt)
    except Exception as e:
        logger.warning(f"[polaridad-ia] fallo del LLM local: {type(e).__name__}: {e}")
        return {}

    filas = _parsear_json(raw)
    if not filas:
        logger.warning("[polaridad-ia] respuesta no parseable como JSON -> se descarta")
        return {}

    informe_norm = _norm(txt)
    # la IA responde 'CA19-9'/'CKAE1E3'/'IDH' donde la clave es 'CA19_9'/'CKAE1AE3'/'IDH1'
    validos = {}
    for m in marcadores:
        for k in _equivalentes(m):
            validos.setdefault(k, m)
    out: Dict[str, Tuple[str, str]] = {}
    rechazados = []

    for f in filas:
        if not isinstance(f, dict):
            continue
        marc_raw = str(f.get('marcador', '')).strip()
        marc = _clave_norm(marc_raw)
        ver = str(f.get('veredicto', '')).strip().upper()
        cita = str(f.get('cita', '') or '')

        if marc not in validos:          # vocabulario cerrado: no puede inventar marcadores
            rechazados.append(f'{marc_raw}(no en lista)')
            continue
        if ver not in VEREDICTOS:        # clasificación cerrada
            rechazados.append(f'{marc_raw}(veredicto invalido)')
            continue
        if ver == 'NO_DICE':             # abstención: válida y no necesita cita
            out[validos[marc]] = ('NO_DICE', '')
            continue
        if not _cita_respaldada(cita, informe_norm, marc_raw):   # ← GUARDA 1: cita real
            rechazados.append(f'{marc_raw}={ver}(cita sin respaldo)')
            continue
        # GUARDA 2: un POSITIVO cuya cita atribuye la marcación a vasos/estroma/basales
        # no es positivo DEL TUMOR. Se descarta (se conserva lo que hubiera).
        if ver == 'POSITIVO' and _positivo_de_otra_poblacion(_norm(cita)):
            rechazados.append(f'{marc_raw}=POSITIVO(marca poblacion NO tumoral)')
            continue
        out[validos[marc]] = (ver, cita)

    if rechazados:
        logger.warning(f"🛡️ [polaridad-ia] descartados sin respaldo textual: "
                       f"{', '.join(rechazados[:8])}{' …' if len(rechazados) > 8 else ''}")
    return out


# ═══════════════════════════════════════════════════════════════════════════
# CLIENTE LOCAL + PUNTO DE ENTRADA DEL EXTRACTOR
# ═══════════════════════════════════════════════════════════════════════════
_HOSTS_LOCALES = ('localhost', '127.0.0.1', '::1', '0.0.0.0')
_CONS_CACHE: Dict[str, bool] = {}


def _revisar_todos() -> bool:
    """¿Va a REVISIÓN todo cambio de polaridad, no solo los dudosos?
    config.ini [llm] revisar_todos_los_cambios. Por defecto SÍ.

    POR QUÉ (medido, no opinión): con el consenso a 2 lentes, sobre 90 casos difíciles con
    veredicto conocido se escribieron **20 datos FALSOS (22%)**. Es decir: cuando las dos
    lentes coinciden NO se puede confiar en que acierten -> la "confianza ALTA" del modelo
    local NO es un aval suficiente para dato clínico.
    Única regla que da 100% verificado con este hardware: si la IA quiere CAMBIAR una
    polaridad, un humano lo confirma. Son ~522 de 2.077 casos (25%), con la cita al lado.
    El valor SÍ se escribe (la IA acierta 82% vs 40% del regex): lo que no se hace es darlo
    por bueno en silencio.
    """
    if 'r' in _CONS_CACHE:
        return bool(_CONS_CACHE['r'])
    val = True
    try:
        import configparser
        cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
        cfg.read(os.path.join(_RAIZ, 'config', 'config.ini'), encoding='utf-8')
        if cfg.has_option('llm', 'revisar_todos_los_cambios'):
            val = cfg.getboolean('llm', 'revisar_todos_los_cambios')
    except Exception:
        pass
    _CONS_CACHE['r'] = val
    return val


def _usar_consenso() -> bool:
    """¿Doble lente + cola de revisión? config.ini [llm] usar_consenso_polaridad.
    Por defecto SÍ: una sola lente acierta ~82% en las frases difíciles y NO avisa cuando
    falla. Con dos lentes, el desacuerdo es la señal de 'no sé' -> el caso va a revisión en
    vez de escribirse mal. Cuesta 2 llamadas por lote (~2x tiempo)."""
    if 'v' in _CONS_CACHE:
        return _CONS_CACHE['v']
    val = True
    try:
        import configparser
        cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
        cfg.read(os.path.join(_RAIZ, 'config', 'config.ini'), encoding='utf-8')
        if cfg.has_option('llm', 'usar_consenso_polaridad'):
            val = cfg.getboolean('llm', 'usar_consenso_polaridad')
    except Exception:
        pass
    _CONS_CACHE['v'] = val
    return val


def _endpoint_local() -> Optional[Tuple[str, str]]:
    """(url, modelo) del LLM LOCAL según config.ini [llm]. None si no hay o NO es local.

    DATOS MÉDICOS CONFIDENCIALES (Ley 1581, Habeas Data): esta capa NUNCA puede hablar
    con un proveedor en la nube. Si el endpoint configurado no apunta a la máquina local,
    se REHÚSA a llamar — mejor quedarse con el valor del regex que filtrar un informe.
    """
    import configparser
    from urllib.parse import urlparse
    try:
        cfg = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
        cfg.read(os.path.join(_RAIZ, 'config', 'config.ini'), encoding='utf-8')
        if not cfg.has_section('llm'):
            return None
        prov = (cfg.get('llm', 'provider', fallback='') or '').strip().lower()
        base = (cfg.get('llm', 'base_url', fallback='') or '').strip()
        if not base:
            base = ('http://localhost:11434/v1' if prov == 'ollama'
                    else 'http://127.0.0.1:1234/v1')
        host = (urlparse(base).hostname or '').lower()
        if host not in _HOSTS_LOCALES:
            logger.error(f"🚫 [polaridad-ia] endpoint NO local ({host}): se rehúsa la llamada. "
                         f"Los informes no pueden salir del hospital.")
            return None
        modelo = (cfg.get('llm', 'modelo', fallback='') or
                  cfg.get('llm', 'model', fallback='') or '').strip()
        return base.rstrip('/'), modelo
    except Exception as e:
        logger.warning(f"[polaridad-ia] no se pudo leer config [llm]: {e}")
        return None


_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _llm_local_call(base: str, modelo: str, max_tokens: int = 500):
    """fn(prompt)->str contra el endpoint OpenAI-compatible LOCAL.

    OJO con max_tokens: LM Studio reserva recursos proporcionales al LÍMITE pedido, no a
    lo que realmente genera. Medido con el MISMO prompt y las MISMAS 62 tokens de salida:
        max_tokens=1500 -> 26,3 s
        max_tokens= 500 ->  7,8 s   (3,4x más rápido)
    Por eso se ajusta al tamaño real de la respuesta (~60 tokens por marcador) en vez de
    poner un límite generoso "por si acaso".
    """
    import requests

    def call(prompt: str) -> str:
        body = {'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0.0, 'max_tokens': max_tokens}
        if modelo:
            body['model'] = modelo
        r = requests.post(f'{base}/chat/completions', json=body, timeout=300)
        r.raise_for_status()
        return r.json()['choices'][0]['message']['content']
    return call


def _modelo_por_defecto(base: str) -> str:
    import requests
    try:
        r = requests.get(f'{base}/models', timeout=5)
        r.raise_for_status()
        for m in r.json().get('data', []):
            mid = str(m.get('id', ''))
            if mid and 'embed' not in mid.lower():
                return mid
    except Exception:
        pass
    return ''


def clasificar_con_consenso(informe: str, marcadores: List[str], llm_call_a, llm_call_b):
    """Dos lentes independientes sobre el MISMO informe. Devuelve
        {marcador: {'veredicto', 'cita', 'confianza', 'lente_a', 'lente_b'}}
    confianza:
      'ALTA'  -> las dos lentes coinciden en POSITIVO/NEGATIVO y la cita está verificada
                 -> se puede escribir el valor.
      'BAJA'  -> discrepan, una se abstiene, o la cita no cuadra
                 -> NO se adivina: el caso va a REVISIÓN con las dos opiniones.
    Nunca se pierde la trazabilidad: siempre se devuelve la cita de cada lente.
    """
    a = clasificar_polaridad(informe, marcadores, llm_call_a)
    b = clasificar_polaridad(informe, marcadores, llm_call_b, plantilla=_PROMPT_LENTE_B)
    out = {}
    for m in marcadores:
        va, ca = a.get(m, (None, ''))
        vb, cb = b.get(m, (None, ''))
        firme = (va in ('POSITIVO', 'NEGATIVO')) and va == vb
        out[m] = {
            'veredicto': va if firme else None,
            'cita': ca or cb,
            'confianza': 'ALTA' if firme else 'BAJA',
            'lente_a': va,
            'lente_b': vb,
        }
    return out


def corregir_polaridad_con_ia(results: Dict[str, str], texto: str) -> Dict[str, str]:
    """Corrige la POLARIDAD de los biomarcadores usando la IA LOCAL, con la guarda de cita.

    Solo revisa los que YA tienen un valor POSITIVO/NEGATIVO puesto por el regex (no crea
    marcadores nuevos). Sobrescribe únicamente cuando la IA afirma lo contrario Y su cita
    está verificada contra el informe. Si el LLM local no está disponible, o la guarda
    rechaza, o la IA se abstiene -> se conserva el valor del regex (degradación segura).

    Medido sobre 60 casos adjudicados contra el informe (el subconjunto MÁS ambiguo del
    corpus): regex 40% de acierto; esta capa, 100% sobre lo que afirma.
    """
    if not results or not texto:
        return results
    revisables = [k for k, v in results.items()
                  if str(v).strip().upper() in ('POSITIVO', 'NEGATIVO')]
    if not revisables:
        return results

    ep = _endpoint_local()
    if not ep:
        return results
    base, modelo = ep
    if not modelo:
        modelo = _modelo_por_defecto(base)

    nombres = [k[4:] if k.upper().startswith('IHQ_') else k for k in revisables]
    n2k = {n: k for n, k in zip(nombres, revisables)}
    # ~60 tokens por marcador + margen; un límite generoso "por si acaso" cuesta 3,4x
    tope = min(500, 70 * min(len(nombres), 8) + 120)
    llm = _llm_local_call(base, modelo, tope)
    try:
        if _usar_consenso():
            dic = clasificar_con_consenso(texto, nombres, llm, llm)
        else:
            dic = {n: {'veredicto': v, 'cita': c, 'confianza': 'ALTA', 'lente_a': v, 'lente_b': v}
                   for n, (v, c) in clasificar_polaridad(texto, nombres, llm).items()}
    except Exception as e:
        logger.warning(f"[polaridad-ia] no se pudo consultar el LLM local: {e}")
        return results

    out = dict(results)
    todos = _revisar_todos()
    cambios, dudosos = [], []
    for nombre, d in dic.items():
        k = n2k.get(nombre)
        if not k:
            continue
        actual = str(out[k]).strip().upper()
        ver = d.get('veredicto')
        alta = d.get('confianza') == 'ALTA' and ver in ('POSITIVO', 'NEGATIVO')

        if alta and ver != actual:
            # Se ESCRIBE el valor de la IA (acierta 82% vs 40% del regex)…
            out[k] = ver
            cambios.append({'columna': k, 'antes': actual, 'despues': ver,
                            'cita': d.get('cita', '')})
            if todos:
                # …pero NO se da por bueno en silencio: todo cambio se confirma.
                # Medido: con "confianza ALTA" aún se colaba un 22% de datos falsos.
                dudosos.append({'columna': k, 'valor_actual': ver, 'valor_previo': actual,
                                'motivo': 'CAMBIO_APLICADO_PENDIENTE_DE_CONFIRMAR',
                                'lente_a': d.get('lente_a'), 'lente_b': d.get('lente_b'),
                                'cita': d.get('cita', '')})
        elif not alta and (d.get('lente_a') in ('POSITIVO', 'NEGATIVO')
                           or d.get('lente_b') in ('POSITIVO', 'NEGATIVO')):
            # Las lentes NO coinciden -> el sistema NO SABE. No se adivina: se conserva
            # el valor actual y va a REVISIÓN con las dos opiniones.
            dudosos.append({'columna': k, 'valor_actual': actual,
                            'motivo': 'LENTES_DISCREPAN_NO_SE_TOCO',
                            'lente_a': d.get('lente_a'), 'lente_b': d.get('lente_b'),
                            'cita': d.get('cita', '')})

    if cambios:
        logger.info(f"🤖 [polaridad-ia] {len(cambios)} polaridades corregidas (confianza ALTA):")
        for c in cambios[:8]:
            logger.info(f"      {c['columna']}: {c['antes']}->{c['despues']}  «{c['cita'][:55]}»")
    if dudosos:
        logger.warning(f"🔎 [polaridad-ia] {len(dudosos)} marcadores DUDOSOS -> a revisión "
                       f"(se conserva el valor actual, NO se adivina):")
        for d in dudosos[:6]:
            logger.warning(f"      {d['columna']}: lente A={d['lente_a']} / B={d['lente_b']}")
    # el llamador (unified_extractor) recoge esto para la cola de revisión + auditoría
    out['__AUDIT_POLARIDAD__'] = {'cambios': cambios, 'dudosos': dudosos}
    return out
