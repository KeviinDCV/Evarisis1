# -*- coding: utf-8 -*-
"""V6.9.64 — DIAGNÓSTICO PRINCIPAL CON IA LOCAL + GUARDA DE CITA VERBATIM.

╔══════════════════════════════════════════════════════════════════════════╗
║  ⛔ NO ESTÁ CABLEADO. NO ACTIVAR SIN VOLVER A MEDIR.                      ║
║                                                                          ║
║  MEDIDO (2026-07-16) sobre 44 casos con la verdad establecida por         ║
║  adjudicación CIEGA de revisores contra el informe:                       ║
║      opina en 27 -> acierta 20 (74%) · falla 7 · se abstiene en 17        ║
║      MEJORA 6  ·  ROMPE 5 casos que el regex YA resolvía bien             ║
║  74% es insuficiente para el campo más crítico del sistema, y romper 5    ║
║  diagnósticos correctos es inaceptable. NO se conecta al extractor.       ║
║                                                                          ║
║  El DISEÑO es correcto (la guarda de cita funciona: rechaza texto         ║
║  redactado o inventado). El techo está en el MODELO: mistral-nemo 12B     ║
║  en Q3 (lo máximo que entra en una RTX 3050 de 8 GB) no sostiene el       ║
║  razonamiento de dos pasos que esto exige ("¿algún espécimen es maligno?  ║
║  -> entonces ese es el principal").                                       ║
║  Se reescribió el prompt dos veces: NO movió los casos clave. Con este    ║
║  modelo, mejores instrucciones NO mejoran el juicio (medido 3 veces hoy). ║
║                                                                          ║
║  QUÉ HARÍA FALTA: GPU con más VRAM -> modelo mejor cuantizado.            ║
║  Banco de pruebas listo: scratchpad/dx_verdad.json + test_dx_ia.py        ║
╚══════════════════════════════════════════════════════════════════════════╝

POR QUÉ EXISTE
--------------
El regex pierde el diagnóstico en informes MULTI-ESPÉCIMEN (~49 casos, 2,4%):
  · "DIAGNÓSTICO A. Mama derecha. Tumor. Biopsia. Inmunohistoquímica.
     CARCINOMA INVASIVO DE TIPO NO ESPECIAL DUCTAL…"   -> devolvía "INMUNOHISTOQUÍMICA"
  · "A. Próstata der.: NEGATIVO PARA MALIGNIDAD ·
     B. Próstata izq.: ADENOCARCINOMA (GLEASON 3+3)"    -> devolvía el espécimen BENIGNO
Se midieron 3 reglas distintas para saltar el rótulo (última / primera / run contiguo):
la actual ya era la MEJOR (2.027 vs 2.008 vs 2.025). El regex tocó techo: acertar exige
entender de qué espécimen habla el estudio, no reconocer un patrón.

POR QUÉ ESTA IA **NO** ES LA QUE ALUCINABA
------------------------------------------
La capa `extractor_diagnostico_ia` se desactivó porque INVENTABA diagnósticos: generaba
texto libre y no había con qué contrastarlo. Aquí el contrato es otro:

  1. NO GENERA, **SELECCIONA**: debe devolver un fragmento del informe, copiado tal cual.
  2. GUARDA DE CITA VERBATIM: se comprueba que ese texto esté **literalmente** en la
     sección DIAGNÓSTICO. Si no está -> se DESCARTA. Una alucinación no puede sobrevivir:
     por construcción, solo puede devolver texto que ya está escrito en el PDF.
  3. CONSENSO A 2 LENTES: dos encuadres distintos; si no coinciden, NO se toca nada y el
     caso va a la cola de revisión (medido en polaridad: la "confianza" de una sola lente
     no es un aval fiable para dato clínico).
  4. SOLO INTERVIENE si el dx actual es inválido/sospechoso. Si el regex acertó, no se toca.

En la duda NO se adivina: se conserva lo que hay y se encola para revisión humana.
Proveedor LOCAL obligatorio (Ley 1581 / Habeas Data): nada sale del hospital.
"""
from __future__ import annotations

import logging
import re
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Reutilizamos la infraestructura ya validada de la capa de polaridad
from core.extractors.biomarcador_polaridad_ia import (  # noqa: E402
    _norm, _parsear_json, _endpoint_local, _modelo_por_defecto, _llm_local_call)

_PROMPT_A = """Eres patólogo. Del INFORME siguiente, extrae el DIAGNÓSTICO PRINCIPAL.

NO redactes ni resumas: COPIA el diagnóstico EXACTAMENTE como está escrito en el informe.

REGLAS:
1. VARIOS ESPECÍMENES (A., B., C.): si ALGUNO tiene un diagnóstico MALIGNO (carcinoma,
   linfoma, sarcoma, melanoma, metástasis...), ESE es el diagnóstico principal — aunque otro
   espécimen sea negativo.
   Ejemplo: "A. Próstata der.: NEGATIVO PARA MALIGNIDAD · B. Próstata izq.: ADENOCARCINOMA"
            -> el principal es ADENOCARCINOMA (el de B).
2. Solo si NINGÚN espécimen tiene diagnóstico maligno, el principal es el hallazgo negativo
   o benigno ("sin evidencia de tumor", "hiperplasia reactiva").
3. NO confundas un ANTECEDENTE con un diagnóstico de este estudio. "Historia de carcinoma
   ductal", "paciente con antecedente de..." es contexto clínico, NO el dx de este espécimen.
   El dx tiene que ser un hallazgo DE LAS MUESTRAS de este informe.
4. Un RÓTULO no es un diagnóstico: "Inmunohistoquímica", "Mama derecha. Tumor. Biopsia",
   "Estudio de inmunohistoquímica" son la etiqueta del espécimen, NO el resultado.
5. Prefiere el diagnóstico DEFINITIVO sobre el PRELIMINAR si el informe trae los dos.
6. "dx" DEBE ser un fragmento COPIADO LITERALMENTE del informe (mismas palabras, mismo orden).
   Si no puedes copiar uno literal, responde con dx "" y encontrado false.

Responde SOLO este JSON, sin nada más:
{{"encontrado": true|false, "dx": "<copiado literal del informe>"}}

INFORME:
\"\"\"
{informe}
\"\"\"
"""

_PROMPT_B = """Eres patólogo. Localiza en el INFORME la línea del DIAGNÓSTICO PRINCIPAL.

Procede así:
1. Busca la sección DIAGNÓSTICO.
2. Identifica el RÓTULO del espécimen: es la parte que dice sitio, tipo de muestra,
   procedimiento y técnica ("A. Mama derecha. Tumor. Biopsia con aguja gruesa.
   Inmunohistoquímica."). El rótulo NO es el diagnóstico: sáltalo.
3. Lo que viene DESPUÉS del rótulo es el diagnóstico. Cópialo TAL CUAL.
4. Si hay varios especímenes (A., B., C.), revisa el diagnóstico de CADA UNO:
   · ¿Alguno es MALIGNO (carcinoma, linfoma, sarcoma, melanoma, metástasis)? -> ese es el
     principal, aunque otro espécimen salga negativo.
   · ¿Ninguno es maligno? -> entonces sí, el hallazgo negativo/benigno es el principal.
5. Un ANTECEDENTE no es un diagnóstico: "Historia de carcinoma ductal" es contexto clínico
   del paciente, NO un hallazgo de estas muestras. Ignóralo.
6. No inventes, no resumas, no traduzcas: copia el texto del informe.
   Si no hay diagnóstico legible, responde encontrado false.

Responde SOLO este JSON:
{{"encontrado": true|false, "dx": "<copiado literal del informe>"}}

INFORME:
\"\"\"
{informe}
\"\"\"
"""


def _limpia(s: str) -> str:
    return re.sub(r'\s+', ' ', str(s or '')).strip(' .,:;-\t\n')


def _es_literal(dx: str, informe: str, min_pal: int = 3) -> bool:
    """LA GUARDA. El dx debe estar LITERALMENTE en el informe.

    Se compara en el plano normalizado (sin tildes, sin puntuación de adorno) para tolerar
    diferencias tipográficas — NO cambios de contenido. Si el modelo redacta, resume o
    inventa, el texto no aparece y el veredicto se descarta.
    """
    d = _norm(dx)
    if not d or len(d.split()) < min_pal:
        return False
    return d in _norm(informe)


def _pedir(plantilla: str, informe: str, llm_call) -> Optional[str]:
    try:
        raw = llm_call(plantilla.format(informe=informe))
    except Exception as e:
        logger.warning(f"[dx-ia] fallo del LLM local: {type(e).__name__}: {e}")
        return None
    filas = _parsear_json(raw)
    obj = None
    if isinstance(filas, list) and filas:
        obj = filas[0] if isinstance(filas[0], dict) else None
    if obj is None:
        m = re.search(r'\{.*\}', str(raw), re.DOTALL)
        if not m:
            return None
        try:
            import json as _j
            obj = _j.loads(m.group(0))
        except Exception:
            return None
    if not isinstance(obj, dict) or not obj.get('encontrado'):
        return None
    return _limpia(obj.get('dx', ''))


def elegir_dx_principal(seccion: str, llm_call_a, llm_call_b,
                        max_texto: int = 5000) -> Tuple[Optional[str], str, str]:
    """(dx, cita, confianza). confianza: 'ALTA' si las 2 lentes coinciden y el dx está
    LITERAL en el texto; si no, (None, '', 'BAJA') -> el llamador NO toca nada y encola.
    """
    if not seccion or not seccion.strip():
        return None, '', 'BAJA'
    txt = seccion[:max_texto]

    a = _pedir(_PROMPT_A, txt, llm_call_a)
    if not a or not _es_literal(a, txt):
        if a:
            logger.warning(f"🛡️ [dx-ia] lente A descartada (no literal en el informe): {a[:60]!r}")
        return None, '', 'BAJA'

    b = _pedir(_PROMPT_B, txt, llm_call_b)
    if not b or not _es_literal(b, txt):
        if b:
            logger.warning(f"🛡️ [dx-ia] lente B descartada (no literal): {b[:60]!r}")
        return None, '', 'BAJA'

    na, nb = _norm(a), _norm(b)
    # Acuerdo: idénticas, o una contenida en la otra (una lente recorta más que la otra
    # pero señalan el MISMO diagnóstico). Se conserva la más completa.
    if na == nb:
        return a, a, 'ALTA'
    if na in nb:
        return b, b, 'ALTA'
    if nb in na:
        return a, a, 'ALTA'
    logger.warning(f"🔎 [dx-ia] lentes DISCREPAN -> no se toca nada. A={a[:45]!r} B={b[:45]!r}")
    return None, '', 'BAJA'


def dx_con_ia(seccion: str) -> Tuple[Optional[str], str, str]:
    """Punto de entrada: resuelve el endpoint LOCAL y aplica consenso + guarda de cita."""
    ep = _endpoint_local()
    if not ep:
        return None, '', 'BAJA'
    base, modelo = ep
    modelo = modelo or _modelo_por_defecto(base)
    llm = _llm_local_call(base, modelo, 320)   # el dx es corto; un tope alto cuesta 3,4x
    return elegir_dx_principal(seccion, llm, llm)
