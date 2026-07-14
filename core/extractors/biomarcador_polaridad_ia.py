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
4. Si un marcador tiñe estructuras de control/acompañantes pero NO la lesión, es NEGATIVO.
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
    for n in range(len(pal), 3, -1):                          # tramo contiguo más largo, >=4 palabras
        for i in range(len(pal) - n + 1):
            tramo = ' '.join(pal[i:i + n])
            pos = informe_norm.find(tramo)
            if pos < 0:
                continue
            # (b) ¿el marcador está en la MISMA frase que el tramo anclado?
            ini = informe_norm.rfind('.', 0, pos) + 1
            fin = informe_norm.find('.', pos + len(tramo))
            frase = informe_norm[ini: fin if fin > 0 else len(informe_norm)]
            if clave and clave in re.sub(r'[^a-z0-9]', '', frase).upper():
                return True
            return False   # tramo anclado pero el marcador NO está en esa frase -> se rechaza
    return False


def _parsear_json(raw: str) -> Optional[list]:
    """Extrae el array JSON de la respuesta (el modelo a veces lo envuelve en prosa/```)."""
    if not raw:
        return None
    m = re.search(r'\[.*\]', raw, re.DOTALL)
    if not m:
        return None
    try:
        d = json.loads(m.group(0))
        return d if isinstance(d, list) else None
    except json.JSONDecodeError:
        return None


def clasificar_polaridad(informe: str,
                         marcadores: List[str],
                         llm_call,
                         max_informe: int = 7000) -> Dict[str, Tuple[str, str]]:
    """Devuelve {marcador: (veredicto, cita)} SOLO para los veredictos con cita verificada.

    informe    : texto del informe (tal como se leyó del PDF).
    marcadores : nombres que el informe SÍ nombra (el llamador ya lo verificó).
    llm_call   : fn(prompt:str) -> str  (respuesta cruda del LLM LOCAL).

    Un marcador ausente del resultado = "no me consta" -> el llamador conserva su valor.
    NUNCA se devuelve un veredicto cuya cita no esté literal en el informe.
    """
    if not informe or not marcadores:
        return {}

    txt = informe[:max_informe]
    prompt = _PROMPT.format(marcadores=', '.join(marcadores), informe=txt)
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
    # la IA responde 'CA19-9' donde nuestra clave es 'CA19_9' -> comparar normalizado
    validos = {_clave_norm(m): m for m in marcadores}
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
        if not _cita_respaldada(cita, informe_norm, marc_raw):   # ← LA GUARDA
            rechazados.append(f'{marc_raw}={ver}(cita sin respaldo)')
            continue
        out[validos[marc]] = (ver, cita)

    if rechazados:
        logger.warning(f"🛡️ [polaridad-ia] descartados sin respaldo textual: "
                       f"{', '.join(rechazados[:8])}{' …' if len(rechazados) > 8 else ''}")
    return out
