#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Normalizador de órganos / sitios anatómicos / procedimientos
=============================================================

Las columnas `Organo` e `IHQ_ORGANO` de la BD contienen miles de variantes
textuales que en realidad refieren al mismo órgano:

  - Acentos inconsistentes:    "MEDULA ÓSEA"  vs  "MÉDULA ÓSEA"
  - Lateralidad:               "MAMA DERECHA" vs  "MAMA IZQUIERDA" → MAMA
  - Prefijos quirúrgicos:      "BX HUESO" / "BX DE HUESO" / "HUESO"
  - Procedimiento incluido:    "CUADRANTECTOMIA MAMA" → MAMA
  - Sinónimos / topografías:   "EXOCERVIX" / "ENDOCERVIX" → CERVIX

Este módulo provee funciones puras y deterministas para producir
estadísticas FIELES a la realidad clínica. NO modifica la BD.
"""

from __future__ import annotations
import re
import unicodedata
from typing import Iterable, Dict, List, Optional


# ----------------------------------------------------------------------
#  Limpieza léxica básica
# ----------------------------------------------------------------------
def quitar_acentos(texto: str) -> str:
    """Elimina diacríticos manteniendo Ñ → N."""
    if not texto:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def normalizar_texto_basico(valor: object) -> str:
    """Mayúsculas, sin acentos, espacios colapsados."""
    if valor is None:
        return ""
    s = str(valor).strip().upper()
    s = quitar_acentos(s)
    s = re.sub(r"\s+", " ", s)
    return s


# ----------------------------------------------------------------------
#  Diccionario de categorías canónicas
#  Clave = categoría canónica
#  Valor = lista de keywords (ya normalizadas SIN acentos, MAYÚSCULAS).
#          Se evalúa por substring en el texto normalizado.
# ----------------------------------------------------------------------
CATEGORIAS_ORGANO: Dict[str, List[str]] = {
    "MAMA": [
        "MAMA", "CUADRANTECTOMIA", "MASTECTOMIA", "TUMORECTOMIA MAMARIA",
    ],
    "MEDULA OSEA": ["MEDULA OSEA"],
    "HUESO": [
        "HUESO", "FEMUR", "ESTERNON", "TIBIA", "PERONE", "HUMERO",
        "CLAVICULA", "ESCAPULA", "ILIACO", "VERTEBRA", "COSTILLA",
        # V6.9.72: "MAXILAR" a secas faltaba en la tabla; al arreglar el bug de AXILA
        # esos casos dejaron de caer (mal) en GANGLIO LINFATICO y se quedaban sin
        # categoría. El maxilar es hueso facial. Va DESPUÉS de PIEL en el orden, así
        # que "PIEL DE LA CARA, MAXILAR IZQUIERDA" sigue resolviéndose como PIEL.
        "CRANEO", "MANDIBULA", "MAXILAR", "ROTULA",
    ],
    "PROSTATA": ["PROSTATA"],
    "HIGADO": ["HIGADO", "HEPATIC"],
    "CERVIX": ["CERVIX", "EXOCERVIX", "ENDOCERVIX", "CONO CERVICAL"],
    "UTERO": [
        "UTERO", "ENDOMETRIO", "MIOMETRIO", "HISTERECTOMIA",
        "CAVIDAD UTERINA", "CAVIDAD ENDOMETRIAL",
    ],
    "OVARIO": ["OVARIO", "OOFORECTOMIA"],
    "TROMPA UTERINA": ["TROMPA", "SALPINGECTOMIA"],
    "ANEXO GINECOLOGICO": ["ANEXO"],
    "VULVA": ["VULVA"],
    "VAGINA": ["VAGINA"],
    "PULMON": [
        "PULMON", "BRONQUIO", "LOBECTOMIA PULMONAR",
        "LOBULO SUPERIOR", "LOBULO INFERIOR", "LOBULO MEDIO",
    ],
    "ESTOMAGO": ["ESTOMAGO", "GASTRIC", "MUCOSA GASTRICA", "GASTRECTOMIA", "ANTRO"],
    "COLON": [
        "COLON", "RECTO", "RECTAL", "MUCOSA RECTAL", "SIGMOIDE", "CIEGO",
        "HEMICOLECTOMIA", "COLECTOMIA",
    ],
    "INTESTINO DELGADO": [
        "DUODENO", "DUODENAL", "YEYUNO", "ILEON", "INTESTINO DELGADO",
    ],
    "ANO / CANAL ANAL": ["CANAL ANAL", "MARGEN ANAL", " ANO ", "ANO,"],
    "PANCREAS": ["PANCREAS", "WHIPPLE"],
    "VESICULA / VIA BILIAR": ["VESICULA", "COLECISTECTOMIA", "VIA BILIAR", "COLEDOCO"],
    "ESOFAGO": ["ESOFAGO"],
    "RIÑON": [
        "RIÑON", "RINON", "RENAL", "NEFRECTOMIA", "INJERTO RENAL",
    ],
    "VEJIGA / VIA URINARIA": ["VEJIGA", "URETER", "URETRA", "RTU"],
    "TIROIDES": ["TIROIDES", "TIROIDECTOMIA"],
    "PARATIROIDES": ["PARATIROIDES"],
    "GLANDULA SUPRARRENAL": ["SUPRARRENAL", "ADRENAL"],
    "HIPOFISIS": ["HIPOFISIS", "PITUITARIA", "REGION SELAR", "TUMOR SELAR"],
    "SISTEMA NERVIOSO CENTRAL": [
        "CEREBRO", "ENCEFALO", "MENINGE", "MENINGIOMA", "GLIOMA",
        "MEDULA ESPINAL", "INTRACRANEAL", "INTRAMEDULAR",
        "LOBULO FRONTAL", "LOBULO TEMPORAL",
        "LOBULO PARIETAL", "LOBULO OCCIPITAL",
        "TUMOR CEREBRAL", "TUMOR FRONTAL", "TUMOR TEMPORAL",
        "TUMOR PARIETAL", "TUMOR OCCIPITAL",
        "FOSA POSTERIOR", "FOSA ANTERIOR",
    ],
    "GANGLIO LINFATICO": [
        "GANGLIO", "LINFADENECTOMIA", "ADENOPATIA", "ADENECTOMIA",
        "REGION SUPRACLAVICULAR", "REGION INGUINAL",
        "REGION CERVICAL", "REGION AXILAR", "AXILA",
        "GANGLIO CENTINELA",
    ],
    "PIEL": [
        "PIEL", "DERMIS", "EPIDERMIS", "LESION CUTANEA", "DERMATOLOGIC",
        "MELANOM",
    ],
    "TEJIDO BLANDO": [
        "TEJIDO BLANDO", "PARTES BLANDAS", "MUSCULO", "MUSLO", "BRAZO",
        "ANTEBRAZO", "PIERNA", "PARED ABDOMINAL", "PARED TORACICA",
        "PIE", "MANO", "DEDO", "GLUTEO", "REGION GLUTEA", "ESPALDA",
    ],
    "RETROPERITONEO": ["RETROPERITONEAL", "RETROPERITONEO"],
    "BAZO": ["BAZO", "ESPLENECTOMIA"],
    "TESTICULO": ["TESTICULO", "ORQUIECTOMIA"],
    "PENE": ["PENE"],
    "CAVIDAD ORAL / OROFARINGE": [
        "LENGUA", "PALADAR", "ENCIA", "MUCOSA ORAL", "AMIGDALA",
        "OROFARINGE", "LABIO", "CAVIDAD ORAL",
    ],
    "NASOFARINGE": ["NASOFARING"],
    "GLANDULA SALIVAL": ["PAROTIDA", "SALIVAL", "SUBMANDIBULAR"],
    "FOSA NASAL / SENO PARANASAL": ["FOSA NASAL", "SENO MAXILAR", "SENO PARANASAL"],
    "LARINGE": ["LARINGE", "CUERDA VOCAL"],
    "CUELLO": ["MASA EN CUELLO", "REGION CERVICAL ANTERIOR"],
    "TIMO": ["TIMO"],
    "PERITONEO / EPIPLON": ["PERITONEO", "EPIPLON", "OMENTO"],
    "PLEURA": ["PLEURA"],
    "MEDIASTINO": ["MEDIASTINO", "MEDIASTINAL"],
    "ABDOMEN (INESPECIFICO)": ["MASA INTRAABDOMINAL", "INTRAABDOMINAL"],
    "CORAZON": ["CORAZON", "MIOCARDIO", "PERICARDIO"],
    "OJO / ANEXOS": ["OJO", "PARPADO", "RETINA", "CORNEA", "GLOBO OCULAR"],
    "OIDO": [" OIDO", "PABELLON AURICULAR"],
    "PLACENTA": ["PLACENTA"],
    "PRODUCTO DE LEGRADO": ["LEGRADO", "RESTOS OVULARES", "PRODUCTO GESTACIONAL"],
}


# Orden de evaluación: las categorías más específicas primero.
# IMPORTANTE: "MEDULA OSEA" debe evaluarse antes que "HUESO"
# porque ambos contienen "HUESO" implícito en algunos casos.
ORDEN_EVALUACION: List[str] = [
    "MEDULA OSEA",   # antes que HUESO
    "MAMA",
    "CERVIX",
    "UTERO",
    "OVARIO",
    "TROMPA UTERINA",
    "ANEXO GINECOLOGICO",
    "VULVA",
    "VAGINA",
    "HIPOFISIS",
    "SISTEMA NERVIOSO CENTRAL",
    "NASOFARINGE",
    "GANGLIO LINFATICO",
    "MEDIASTINO",
    "PLEURA",
    "PULMON",
    "ESOFAGO",
    "ESTOMAGO",
    "COLON",
    "INTESTINO DELGADO",
    "ANO / CANAL ANAL",
    "PANCREAS",
    "VESICULA / VIA BILIAR",
    "HIGADO",
    "BAZO",
    # V6.9.72: tres pares estaban al REVÉS de la regla "lo más específico primero"
    # que declara esta misma lista, y como la búsqueda es por subcadena el genérico
    # se los comía: PERITONEO capturaba RETROPERITONEO (14 casos), RENAL capturaba
    # ADRENAL/SUPRARRENAL (7 casos) y TIROIDES capturaba PARATIROIDES (1 caso).
    "RETROPERITONEO",        # antes que PERITONEO ("RETROPERITONEO" contiene "PERITONEO")
    "PERITONEO / EPIPLON",
    "GLANDULA SUPRARRENAL",  # antes que RIÑON ("ADRENAL"/"SUPRARRENAL" contienen "RENAL")
    "RIÑON",
    "VEJIGA / VIA URINARIA",
    "PROSTATA",
    "TESTICULO",
    "PENE",
    "PARATIROIDES",          # antes que TIROIDES ("PARATIROIDES" contiene "TIROIDES")
    "TIROIDES",
    "TIMO",
    "GLANDULA SALIVAL",
    "CAVIDAD ORAL / OROFARINGE",
    "FOSA NASAL / SENO PARANASAL",
    "LARINGE",
    "CUELLO",
    "OJO / ANEXOS",
    "OIDO",
    "CORAZON",
    "PLACENTA",
    "PRODUCTO DE LEGRADO",
    "PIEL",
    "HUESO",          # después de MEDULA OSEA
    "TEJIDO BLANDO",  # categoría amplia
    "ABDOMEN (INESPECIFICO)",  # último: muy genérico
]


# Tokens léxicos que indican "tipo de muestra" pero no aportan al órgano.
# Se eliminan ANTES de buscar la categoría.
PREFIJOS_MUESTRA = [
    r"\bBX\s+DE\b", r"\bBX\b",
    r"\bBIOPSIA\s+DE\b", r"\bBIOPSIA\b",
    r"\bMUESTRA\s+DE\b", r"\bMUESTRA\b",
    r"\bRESECCION\s+DE\b", r"\bRESECCION\b",
    r"\bPIEZA\s+DE\b", r"\bPIEZA\b",
]
SUFIJOS_LATERALIDAD = [
    r"\bDERECH[AO]\b", r"\bIZQUIERD[AO]\b",
    r"\bBILATERAL\b", r"\bUNILATERAL\b",
]


# V6.9.72 FIX: la búsqueda era `kw in limpio`, subcadena pura, así que "AXILA"
# casaba dentro de "MAXILAR" y mandaba a GANGLIO LINFATICO cualquier maxilar
# ("SENO MAXILAR IZQUIERDO", "PIEL DE LA CARA, MAXILAR IZQUIERDA"). Se exige
# frontera de palabra SOLO AL INICIO del keyword: así se corta la subcadena
# interna y a la vez se conservan los stems deliberados de la tabla, que están
# pensados para casar por prefijo (MELANOM->MELANOMA, NASOFARING->NASOFARINGEO,
# DERMATOLOGIC, RETROPERITONEAL, MEDIASTINAL).
# La coincidencia por SUBCADENA se mantiene para el resto de la tabla a propósito:
# de ella dependen los plurales y las formas adjetivas y compuestas que trae el
# corpus (GANGLIO->GANGLIOS, MAMA->INFRAMAMARIO, VERTEBRA->PARAVERTEBRAL,
# VULVA->HEMIVULVA, MANDIBULA->RETROMANDIBULAR, COLON->COLONICA). Cerrarla en
# bloque se midió: perdía ~200 casos. Por eso las fronteras se aplican SOLO a los
# cuatro keywords en los que está medido que la subcadena produce un error.
_KW_INICIO = frozenset((
    'AXILA',   # "MAXILAR" / "SENO MAXILAR" no son ganglio (bug de origen)
    'PIEL',    # "UNION PIELOURETERAL" no es piel
    'PIE',     # "PIEL …" no es tejido blando del pie
    'ROTULA',  # "A-ROTULADO MASA RETROAREOLAR" no es hueso
))
# AXILA necesita el final ABIERTO ("REGION AXILAR" sí es ganglio); los otros tres no.
_KW_FIN = _KW_INICIO - {'AXILA'}
_KW_CACHE: dict = {}


# ── V6.9.103 · tabla de RESERVA ───────────────────────────────────────────────
# Se aplica SOLO si CATEGORIAS_ORGANO no encontró nada, así que no puede alterar lo que
# ya funciona. Cada entrada sale de un valor REAL medido en el corpus, no de imaginar
# sinónimos. Se mapea únicamente lo inequívoco: "HOMBRO", "RODILLA" o "MIEMBRO INFERIOR"
# quedan fuera a propósito, porque ahí la biopsia puede ser de hueso o de tejido blando
# y adivinar sería peor que dejarlo sin categorizar.
CATEGORIAS_ORGANO_RESERVA = {
    "SISTEMA NERVIOSO CENTRAL": [
        "CEREBELO", "TALLO CEREBRAL", "BULBO MEDULAR", "BULBO-MEDULAR", "DURAMADRE",
        "SILLA TURCA", "TALAMO", "VENTRICULO LATERAL", "TERCER VENTRICULO",
        "IV VENTRICULO", "INTRAVENTRICULAR", "ANGULO PONTOCEREBELOSO", "REGION PINEAL",
        "CLIVUS", "PETROCLIVAL", "SUPRA SELAR", "SUPRACELAR", "CAUDA EQUINA",
        "INTRADURAL", "EPIDURAL", "EXTRADURAL", "EXTRAAXIAL", "FALCOTENTORIAL",
        "PARASAGITAL", "PARENQUIMA CEREBRAL", "CANAL MEDULAR", "BULBO OLFATORIO",
        "BOVEDA CRANEAL", "BOVEDA CRANEANA", "TEMPOROINSULAR", "FRONTOPARIETAL",
        "PARIETOTEMPORAL", "PARIETO OCCIPITAL", "REGION FRONTAL", "REGION PARIETAL",
        "REGION OCCIPITAL",
    ],
    "TIROIDES": ["LOBULO TIROIDEO"],
    "MEDULA OSEA": ["MUDELA OSEA"],          # errata del informe
    "ESTOMAGO": ["MUCOSA ANTRAL", "MUCOSA CORPORAL", "PREPILORICA", "CARDIAS",
                 "UNION GASTROESOFAGICA"],
    "ESOFAGO": ["MUCOSA ESOFAGICA"],
    "INTESTINO DELGADO": ["MUCOSA YEYUNAL", "YEYUNO", "DUEDENO", "AMPOLLA DE VATER",
                          "ILION TERMINAL", "ILEON TERMINAL"],
    "COLON": ["MUCOSA DE CIEGA", "CIEGO", "APENDICE CECAL", "COLOSTOMIA"],
    "ANO / CANAL ANAL": ["REGION ANAL", "MUCOSA ANAL", "PERIANAL", "ANO POSTRASPLA"],
    "CAVIDAD ORAL / OROFARINGE": ["MUCOSA VESTIBULAR ORAL", "MUCOSA PALATINA",
                                  "MUCOSA BUCAL", "CARRILLO", "REBORDE ALVEOLAR",
                                  "HIPOFARINGE"],
    "NASOFARINGE": ["CAVUM FARINGEO"],
    "VEJIGA / VIA URINARIA": ["CAVIDAD VESICAL", "MUCOSA VESICAL", "CUELLO VESICAL"],
    "OJO / ANEXOS": ["ORBITA", "ORBITARIA", "PERIORBITARIO", "GLANDULA LACRIMAL",
                     "GLANDULA LAGRIMAL"],
    "PERITONEO / EPIPLON": ["IMPLANTES PERITONEALES", "MESENTERIO", "SACO HERNIARIO"],
    "RETROPERITONEO": ["RETRO PERITONEAL", "RETROPERITONEAL"],
    "ABDOMEN (INESPECIFICO)": ["CAVIDAD ABDOMINAL", "CAVIDAD INTRABDOMINAL",
                               "REGION INTRABDOMINAL", "MASA ABDOMINAL", "FOSA ILIACA",
                               "REGION UMBILICAL"],
    "FOSA NASAL / SENO PARANASAL": ["CAVIDAD NASAL", "SEPTO NASAL", "TECHO NASAL",
                                    "LESION NASAL", "REGION SINUSAL", "CORNETE",
                                    "ETMOIDAL", "ESFENOIDES"],
    "CUELLO": ["HEMICUELLO", "VACIAMIENTO DE CUELLO", "TUMOR CUELLO", "CUERPO CAROTIDEO",
               "PERIFARINGEA"],
    "MAMA": ["PERIAREOLAR", "RETROAREOLAR", "PEZON", "CUADRANTE SUPERIOR EXTERNO"],
    "CERVIX": ["CUELLO UTERINO", "MUCOSA EXOCERVICAL"],
    "TROMPA UTERINA": ["TUBA UTERINA"],
    "PIEL": ["LECHO UNGUEAL", "HALLUX", "PREAURICULAR", "PREARICULAR", "INFRAAURICULAR",
             "HEMICARA", "REGION MALAR"],
    "GLANDULA SALIVAL": ["PAROTIDEA"],
    "OIDO": ["CONDUCTO AUDITIVO"],
    "LARINGE": ["PLIEGUE VOCAL"],
    "PULMON": ["MUCOSA BRONQUIAL", "LINGULA"],
    "PENE": ["GLANDE"],
    "TEJIDO BLANDO": ["TEJIDO SUBCUTANEO", "TEJIDO FIBROADIPOSO", "TEJIDOS BLANDOS"],
    "HUESO": ["COLUMNA TORACICA", "ALA SACRA", "REGION SACRA", "ARCO COSTAL",
              "PARED COSTAL", "REJA COSTAL"],
}

# Restos de extracción que NO son un órgano. Medidos en el corpus: ")", "A", "B-D",
# "APEX D", "LOS HALLAZGOS MORFOLOGICOS Y", 'REFERIDO COMO "LESION…'.
_ORGANO_NO_ES_ORGANO = re.compile(
    r'(?i)^\W*$|^los\s+hallazgos|^referido\s+como|^[a-z]\s*-?\s*[a-z]?$|'
    r'^apex\s+[a-z]$|^tercio\s+medio\s+del\s+lobulo$|^canal\s+anterior$')


def _kw_re(kw: str):
    r = _KW_CACHE.get(kw)
    if r is None:
        k = kw.strip()
        if k in _KW_INICIO:
            pat = r'\b' + re.escape(k) + (r'\b' if k in _KW_FIN else '')
        else:
            pat = re.escape(kw)
        r = _KW_CACHE[kw] = re.compile(pat)
    return r


# ----------------------------------------------------------------------
#  API pública
# ----------------------------------------------------------------------
def normalizar_organo(valor: object) -> str:
    """
    Devuelve la categoría anatómica canónica.
    Si no se reconoce, devuelve el texto normalizado (mayúsculas, sin
    acentos, sin prefijos de muestra ni lateralidad) para que sea
    fácilmente agregable.
    """
    s = normalizar_texto_basico(valor)
    if not s or s in {"N/A", "NA", "SIN DATO", "NONE", "NULL"}:
        return "SIN DATO"

    # Limpiar prefijos y sufijos puramente léxicos
    limpio = s
    for patron in PREFIJOS_MUESTRA:
        limpio = re.sub(patron, " ", limpio)
    for patron in SUFIJOS_LATERALIDAD:
        limpio = re.sub(patron, " ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    if not limpio:
        return "SIN DATO"

    # Buscar categoría canónica por orden de especificidad
    for categoria in ORDEN_EVALUACION:
        keywords = CATEGORIAS_ORGANO.get(categoria, [])
        for kw in keywords:
            if _kw_re(kw).search(limpio):
                return categoria

    # ── V6.9.103 · SEGUNDA PASADA (tabla de reserva) ──────────────────────────
    # Antes de esto, todo lo que el bucle principal no reconocía se devolvía tal cual.
    # Consecuencia medida en el informe estadístico: 148 valores de texto libre (193
    # casos) contaban como "categorías anatómicas" propias, inflando ese KPI a 195
    # cuando los órganos reales son 47. Y ensuciaban la cola del gráfico de distribución
    # con entradas de un solo caso: "LECHO UNGUEAL DE HALLUX", "CUELLO, LADO ESTACION 4
    # Y 5", "REGION INTRADURAL (CAUDA EQUINA)".
    #
    # 🛑 Va DESPUÉS del bucle principal y solo se ejecuta si aquel no encontró nada, así
    # que NO PUEDE cambiar ninguna categorización que hoy funcione. La alternativa
    # —añadir estas palabras a CATEGORIAS_ORGANO— sí podría, porque el orden de
    # evaluación decide y una keyword nueva puede robarle un caso a otra categoría.
    for categoria, keywords in CATEGORIAS_ORGANO_RESERVA.items():
        for kw in keywords:
            if _kw_re(kw).search(limpio):
                return categoria

    # Restos de extracción que no son un órgano: paréntesis sueltos, una letra de
    # rótulo, un trozo de frase. Mejor SIN DATO que una "categoría anatómica" falsa.
    if _ORGANO_NO_ES_ORGANO.search(limpio) or len(limpio) <= 2:
        return "SIN DATO"

    # Sin coincidencia: devolver el texto limpio (no canónico)
    return limpio


def normalizar_serie(valores: Iterable) -> List[str]:
    """Aplica normalizar_organo a una colección."""
    return [normalizar_organo(v) for v in valores]


def elegir_columna_organo(columnas: Iterable[str]) -> Optional[str]:
    """
    Elige la mejor columna disponible para extraer el órgano.
    Prefiere `IHQ_ORGANO` (más limpia) sobre `Organo`.
    """
    cols = list(columnas)
    if "IHQ_ORGANO" in cols:
        return "IHQ_ORGANO"
    if "Organo" in cols:
        return "Organo"
    return None


# ----------------------------------------------------------------------
#  Auto-test
# ----------------------------------------------------------------------
if __name__ == "__main__":
    casos = [
        ("MAMA DERECHA", "MAMA"),
        ("MAMA IZQUIERDA", "MAMA"),
        ("BX MAMA DERECHA", "MAMA"),
        ("CUADRANTECTOMIA MAMA IZQUIERDA", "MAMA"),
        ("MEDULA ÓSEA", "MEDULA OSEA"),
        ("MEDULA OSEA", "MEDULA OSEA"),
        ("BX MEDULA OSEA", "MEDULA OSEA"),
        ("BX DE HUESO", "HUESO"),
        ("BX HUESO", "HUESO"),
        ("BX PROSTATA", "PROSTATA"),
        ("BX HIGADO", "HIGADO"),
        ("BX EXOCERVIX", "CERVIX"),
        ("BX CERVIX", "CERVIX"),
        ("TUMOR DE HIPOFISIS", "HIPOFISIS"),
        ("MUCOSA RECTAL", "COLON"),
        ("RECTO", "COLON"),
        ("MUSLO IZQUIERDO", "TEJIDO BLANDO"),
        ("PULMÓN DERECHO", "PULMON"),
        ("ÚTERO", "UTERO"),
        ("", "SIN DATO"),
        ("N/A", "SIN DATO"),
    ]
    ok = fail = 0
    for entrada, esperado in casos:
        obtenido = normalizar_organo(entrada)
        marca = "OK" if obtenido == esperado else "FAIL"
        if obtenido == esperado:
            ok += 1
        else:
            fail += 1
        print(f"  [{marca}] {entrada!r:45s} → {obtenido!r}  (esperado: {esperado!r})")
    print(f"\nTotal: {ok} OK, {fail} FAIL")
