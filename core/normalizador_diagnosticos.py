"""Normalizador de diagnósticos oncológicos.

Agrupa los 883 valores literales distintos del campo
``Diagnostico Principal`` en categorías clínicas amplias para que las
estadísticas reflejen volúmenes realistas (ej. "ADENOCARCINOMA" agrupa
todas las variantes de diferenciación, localización metastásica, etc.).

NO reemplaza el ranking literal: lo COMPLEMENTA. Las estadísticas siguen
incluyendo el TOP literal para trazabilidad clínica.
"""

from __future__ import annotations

import re
import unicodedata


# --- utilidades ---------------------------------------------------------

def quitar_acentos(texto: str) -> str:
    if not isinstance(texto, str):
        return ""
    nf = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in nf if not unicodedata.combining(c))


def normalizar_texto(valor: str) -> str:
    if not isinstance(valor, str):
        return ""
    t = quitar_acentos(valor).upper()
    t = re.sub(r"\s+", " ", t).strip()
    return t


# --- categorías canónicas ----------------------------------------------
# Orden de evaluación: específicas primero. Cada entrada es una lista de
# patrones (substrings) que activan la categoría.

CATEGORIAS_DIAGNOSTICO: dict[str, list[str]] = {
    # === No oncológico / control ===
    "NEGATIVO PARA MALIGNIDAD": [
        "NEGATIVO PARA MALIGNIDAD",
        "NEGATIVO PARA NEOPLASIA",
        "NEGATIVO PARA CELULAS NEOPLASICAS",
        "SIN EVIDENCIA DE MALIGNIDAD",
        "SIN EVIDENCIA DE NEOPLASIA",
        "AUSENCIA DE MALIGNIDAD",
        "NO HAY EVIDENCIA DE MALIGNIDAD",
        # Lesiones escamosas negativas (citología cervical / biopsias)
        "NEGATIVO PARA LESION ESCAMOSA",
        "NEGATIVO PARA LESION INTRAEPITELIAL",
        "NEGATIVO PARA LESION PREINVASIVA",
        "NEGATIVO PARA LESION INVASIVA",
        "NEGATIVO PARA INVASION",
        "AUSENCIA DE LESION",
        "SIN LESION INTRAEPITELIAL",
        "SIN LESION PREINVASIVA",
        # Localizaciones específicas con resultado negativo
        "EXOCERVIX NEGATIVO",
        "ENDOCERVIX NEGATIVO",
        "ENDOMETRIO NEGATIVO",
        "GANGLIO NEGATIVO",
        # Resultados negativos por tipo de cambio celular
        "NEGATIVO PARA CAMBIOS DISPLASICOS",
        "NEGATIVO PARA DISPLASIA",
        "SIN CAMBIOS DISPLASICOS",
        "AUSENCIA DE CAMBIOS DISPLASICOS",
    ],
    "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA": [
        "SIN REPRESENTACION DE PARENQUIMA",
        "SIN REPRESENTACION DEL PARENQUIMA",
        "TEJIDO NO REPRESENTATIVO",
        "MUESTRA NO REPRESENTATIVA",
        "MUESTRA INSUFICIENTE",
        "MATERIAL INSUFICIENTE",
        "TEJIDO INSUFICIENTE",
        "NO REPRESENTATIVO PARA DIAGNOSTICO",
        "NO DIAGNOSTICA",
    ],
    "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO": [
        "CELULAS GANGLIONARES PRESENTES",
        "GANGLIONARES PRESENTES",
        "HISTOLOGIA NORMAL",
        "HISTOLOGIA SIN ALTERACIONES",
        "BIOPSIA SIN ALTERACIONES",
        "MUCOSA SIN ALTERACIONES",
        "TEJIDO SIN ALTERACIONES",
        "ARQUITECTURA CONSERVADA",
        "PARENQUIMA NORMAL",
    ],
    "RECHAZO DE TRASPLANTE": [
        "RECHAZO ACTIVO",
        "RECHAZO MEDIADO POR ANTICUERPOS",
        "RECHAZO HUMORAL",
        "RECHAZO CELULAR",
        "RECHAZO AGUDO",
        "RECHAZO CRONICO",
        "RECHAZO DE ALOINJERTO",
        "RECHAZO DEL INJERTO",
        "RECHAZO DE INJERTO",
        "BANFF",
    ],
    "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)": [
        "ESTUDIO DE INMUNOHISTOQUIMICA",
        "INMUNOHISTOQUIMICA",
    ],

    # === Hematolinfoides (deben evaluarse antes que carcinomas) ===
    # IMPORTANTE: LINFOMA NO HODGKIN B se evalúa ANTES que LINFOMA HODGKIN
    # porque "LINFOMA NO HODGKIN" contiene la subcadena "HODGKIN" — sin este
    # orden, casos NO Hodgkin se clasificarían erróneamente como Hodgkin.
    # V6.6.8 FIX feedback clínico "linfoma especificar".
    "LINFOMA NO HODGKIN B": [
        "LINFOMA NO HODGKIN", "LINFOMA B DIFUSO", "LINFOMA DIFUSO DE CELULAS B",
        "LINFOMA FOLICULAR", "LINFOMA DE LA ZONA MARGINAL", "LINFOMA MALT",
        "LINFOMA DE BURKITT", "LINFOMA DE CELULAS DEL MANTO",
        "LINFOMA LINFOCITICO", "LEUCEMIA LINFOCITICA CRONICA",
        # Variantes adicionales de linfomas B
        "LINFOMA DE CELULAS B MADURAS",
        "LINFOMA DE CELULAS B",
        "LINFOMA B MADURO",
        "LINFOMA DE LINFOCITOS B",
    ],
    "LINFOMA T/NK": [
        "LINFOMA T", "LINFOMA DE CELULAS T", "LINFOMA NK", "LINFOMA ANAPLASICO",
        "MICOSIS FUNGOIDE",
    ],
    # LINFOMA HODGKIN evaluado DESPUÉS de NO HODGKIN para evitar matching
    # falso. Ahora el patrón "HODGKIN" es seguro porque NO HODGKIN ya
    # consumió esos casos.
    "LINFOMA HODGKIN": [
        "LINFOMA DE HODGKIN", "LINFOMA HODGKIN CLASICO",
        "ENFERMEDAD DE HODGKIN", "HODGKIN CLASICO", "HODGKIN",
    ],
    "LINFOMA (OTRO/INESPECIFICO)": ["LINFOMA"],
    "LEUCEMIA MIELOIDE": [
        "LEUCEMIA MIELOIDE", "LEUCEMIA AGUDA MIELOIDE", "LMA", "LAM ",
        "SARCOMA MIELOIDE", "SARCOMA GRANULOCITICO",
    ],
    "LEUCEMIA LINFOIDE AGUDA": [
        "LEUCEMIA LINFOBLASTICA", "LEUCEMIA AGUDA LINFOBLASTICA", "LLA ",
    ],
    "LEUCEMIA (OTRA)": ["LEUCEMIA"],
    "MIELOMA / NEOPLASIA PLASMOCELULAR": [
        "MIELOMA", "PLASMOCITOMA", "NEOPLASIA DE CELULAS PLASMATICAS",
    ],
    "NEOPLASIA MIELOPROLIFERATIVA / SMD": [
        "MIELOPROLIFERATIVA", "MIELODISPLASICO", "SINDROME MIELODISPLASICO",
        "POLICITEMIA VERA", "TROMBOCITEMIA ESENCIAL", "MIELOFIBROSIS",
    ],
    "MEDULA OSEA REACTIVA / NORMAL": [
        "MEDULA OSEA REACTIVA", "MEDULA OSEA NORMAL", "HIPERPLASIA MEDULAR",
        "CAMBIOS REACTIVOS",
    ],

    # === Mama ===
    # IMPORTANTE: IN SITU debe evaluarse ANTES que DUCTAL DE MAMA porque
    # "CARCINOMA DUCTAL IN SITU" contiene la subcadena "CARCINOMA DUCTAL"
    # que matchearía DUCTAL DE MAMA (clínicamente incorrecto).
    "CARCINOMA IN SITU DE MAMA (DCIS/LCIS)": [
        "CARCINOMA DUCTAL IN SITU", "CARCINOMA LOBULILLAR IN SITU",
        "DCIS", "LCIS", "CARCINOMA INTRADUCTAL",
    ],
    "CARCINOMA DUCTAL DE MAMA": [
        "CARCINOMA INVASIVO DE TIPO NO ESPECIAL", "CARCINOMA DUCTAL INVASIVO",
        "CARCINOMA DUCTAL INFILTRANTE", "CARCINOMA INVASOR DE TIPO NO ESPECIAL",
        "CARCINOMA NST",
        # Variantes con preposición "SIN" (CARCINOMA INVASIVO SIN TIPO ESPECIAL)
        "CARCINOMA INVASIVO SIN TIPO ESPECIAL",
        "CARCINOMA INVASOR SIN TIPO ESPECIAL",
        "SIN TIPO ESPECIAL",
        # CARCINOMA DUCTAL solo (sin INVASIVO/INFILTRANTE explícito) —
        # va al final del array; IN SITU se evalúa antes (categoría
        # superior) por lo que no hay riesgo de falso positivo en DCIS.
        "CARCINOMA DUCTAL",
    ],
    "CARCINOMA LOBULILLAR DE MAMA": [
        "CARCINOMA LOBULILLAR", "CARCINOMA LOBULAR",
    ],
    "OTRO CARCINOMA DE MAMA": [
        # NOTA V6.5.95: Removido "CARCINOMA MUCINOSO" del set porque era
        # demasiado genérico — causaba falsos positivos en mucinosos
        # pulmonares (IHQ250046). Si se necesita capturar el mucinoso de
        # mama, requiere contexto explícito (no inferible solo del dx).
        "CARCINOMA MEDULAR DE MAMA",
        "CARCINOMA MEDULAR", "CARCINOMA TUBULAR",
        "CARCINOMA METAPLASICO", "CARCINOMA APOCRINO",
    ],

    # === Tumores neuroendocrinos ===
    "CARCINOMA NEUROENDOCRINO": [
        "CARCINOMA NEUROENDOCRINO", "TUMOR NEUROENDOCRINO", "CARCINOIDE",
        "TUMOR DE CELULAS PEQUENAS", "CARCINOMA DE CELULAS PEQUENAS",
        "NEURO ENDOCRINO",
    ],

    # === Sistema digestivo / GIST ===
    # Patrones flexibles para capturar variantes con OCR ruidoso (palabras
    # pegadas) y formas con/sin "DEL".
    "GIST (TUMOR ESTROMAL GASTROINTESTINAL)": [
        "GIST",
        "TUMOR ESTROMAL GASTROINTESTINAL",
        "TUMOR DEL ESTROMA GASTROINTESTINAL",
        "ESTROMA GASTROINTESTINAL",
    ],

    # === Tórax / Mediastino ===
    "TIMOMA / NEOPLASIA TIMICA": [
        "TIMOMA",
        "CARCINOMA TIMICO",
        "TIMOCARCINOMA",
        "NEOPLASIA TIMICA",
    ],

    # === Sistema nervioso central ===
    "MENINGIOMA": ["MENINGIOMA"],
    "GLIOMA / ASTROCITOMA / GLIOBLASTOMA": [
        "GLIOMA", "ASTROCITOMA", "GLIOBLASTOMA", "OLIGODENDROGLIOMA",
        "EPENDIMOMA",
    ],
    "MEDULOBLASTOMA / TUMOR EMBRIONARIO SNC": [
        "MEDULOBLASTOMA", "TUMOR EMBRIONARIO", "PNET",
    ],
    "ADENOMA HIPOFISARIO / TUMOR NEUROENDOCRINO HIPOFISARIO": [
        "ADENOMA HIPOFISARIO", "ADENOMA DE HIPOFISIS",
        "TUMOR NEUROENDOCRINO HIPOFISARIO", "PITNET",
    ],
    "CRANEOFARINGIOMA": [
        "CRANEOFARINGIOMA",
    ],
    "SCHWANNOMA / NEURINOMA": ["SCHWANNOMA", "NEURINOMA", "NEURILEMOMA"],
    "NEUROFIBROMA": ["NEUROFIBROMA"],
    "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC": [
        "HETEROTOPIA NEURONAL",
        "HETEROTOPIA",
        "DISPLASIA CORTICAL",
        "MALFORMACION DEL DESARROLLO CORTICAL",
        "MALFORMACION CORTICAL",
    ],
    "GLIOSIS / LESION REACTIVA SNC": [
        "GLIOSIS REACTIVA",
        "GLIOSIS",
        "ASTROGLIOSIS",
        "LESION GLIAL REACTIVA",
    ],

    # === Piel / melanoma ===
    "MELANOMA": ["MELANOMA"],
    "CARCINOMA BASOCELULAR": ["CARCINOMA BASOCELULAR", "BASOCELULAR"],

    # === Sarcomas y partes blandas ===
    "SARCOMA DE KAPOSI": ["SARCOMA DE KAPOSI", "KAPOSI"],
    "LIPOSARCOMA": ["LIPOSARCOMA"],
    "LEIOMIOSARCOMA": ["LEIOMIOSARCOMA"],
    "RABDOMIOSARCOMA": ["RABDOMIOSARCOMA"],
    "OSTEOSARCOMA / SARCOMA OSEO": [
        "OSTEOSARCOMA", "SARCOMA OSEO", "CONDROSARCOMA", "EWING",
    ],
    "SARCOMA SINOVIAL / OTROS SARCOMAS": [
        "SARCOMA SINOVIAL", "DERMATOFIBROSARCOMA", "FIBROSARCOMA",
        "ANGIOSARCOMA", "SARCOMA INDIFERENCIADO", "SARCOMA PLEOMORFICO",
    ],
    "TUMOR DE CELULAS GRANULARES": ["TUMOR DE CELULAS GRANULARES"],
    "TUMOR FIBROSO SOLITARIO / HEMANGIOPERICITOMA": [
        "TUMOR FIBROSO SOLITARIO", "HEMANGIOPERICITOMA",
    ],
    "FIBROMATOSIS / TUMOR DESMOIDE": [
        "FIBROMATOSIS DE TIPO DESMOIDE",
        "TUMOR DESMOIDE",
        "FIBROMATOSIS DESMOIDE",
        "FIBROMATOSIS",
        "DESMOIDE",
    ],

    # === Vías genitourinarias ===
    "CARCINOMA UROTELIAL": ["UROTELIAL", "CARCINOMA TRANSICIONAL"],
    "CARCINOMA RENAL": [
        "CARCINOMA DE CELULAS RENALES",
        "CARCINOMA RENAL",
        # Diagnósticos sugestivos / probables de origen renal
        "NEOPLASIA RENAL",
        "PROBABLE ORIGEN RENAL",
        "ORIGEN RENAL",
        "PATRON ACINAR CON CAMBIOS ONCOCITICOS",
    ],
    "CARCINOMA DE PROSTATA": [
        "ADENOCARCINOMA DE PROSTATA", "CARCINOMA DE PROSTATA",
        "ADENOCARCINOMA ACINAR DE LA PROSTATA",
    ],
    "TUMOR GERMINAL TESTICULAR / OVARICO": [
        "SEMINOMA", "TERATOMA", "DISGERMINOMA", "TUMOR DEL SACO VITELINO",
        "TUMOR GERMINAL", "CORIOCARCINOMA",
    ],

    # === Ginecológico ===
    "CARCINOMA DE CERVIX (ESCAMOCELULAR/ADENO)": [
        "CARCINOMA DE CUELLO UTERINO", "CARCINOMA CERVICAL",
        "CARCINOMA ESCAMOCELULAR DE CERVIX",
        "ADENOCARCINOMA ENDOCERVICAL", "CARCINOMA DE CERVIX",
        # Diagnósticos sugestivos / probables de origen cervical
        "PROBABLE ORIGEN ENDOCERVICAL",
        "ORIGEN ENDOCERVICAL",
        "PROBABLE ORIGEN CERVICAL",
    ],
    "CARCINOMA DE ENDOMETRIO / UTERO": [
        "ADENOCARCINOMA ENDOMETRIAL", "CARCINOMA ENDOMETRIOIDE",
        "CARCINOMA SEROSO", "CARCINOMA DE ENDOMETRIO",
        # Diagnósticos sugestivos / probables de origen endometrial
        "PROBABLE ORIGEN ENDOMETRIAL",
        "ORIGEN ENDOMETRIAL",
    ],
    "CARCINOMA DE OVARIO": [
        "CARCINOMA DE OVARIO", "ADENOCARCINOMA OVARICO",
        "CARCINOMA OVARICO",
    ],

    # === Pulmón / aerodigestivo ===
    "CARCINOMA DE PULMON (NO MICROCITICO)": [
        "ADENOCARCINOMA DE PULMON", "ADENOCARCINOMA PULMONAR",
        "CARCINOMA ESCAMOCELULAR DE PULMON", "CARCINOMA NO MICROCITICO",
        "CARCINOMA NO DE CELULAS PEQUENAS",
        # Variantes con orden invertido / patrones histológicos pulmonares
        "ADENOCARCINOMA INVASIVO PULMONAR",
        "ADENOCARCINOMA INVASIVO DE PULMON",
        "CARCINOMA INVASIVO PULMONAR",
        "INVASIVO PULMONAR",
    ],

    # === Carcinoma nasofaríngeo (entidad clínica distinta, EBV-asociada) ===
    # Debe evaluarse ANTES que CARCINOMA ESCAMOCELULAR (OTRO) porque su
    # diagnóstico típico es "CARCINOMA ESCAMOSO NO QUERATINIZANTE" que
    # matchearía el escamoso genérico.
    "CARCINOMA NASOFARINGEO": [
        "CARCINOMA NASOFARINGEO",
        "CARCINOMA DE NASOFARINGE",
        "CARCINOMA ESCAMOSO NO QUERATINIZANTE",
        "ESCAMOSO NO QUERATINIZANTE",
        "CARCINOMA NO QUERATINIZANTE DE NASOFARINGE",
    ],

    # === Carcinoma escamocelular de cabeza y cuello (entidad clínica común) ===
    # Detecta solo cuando el diagnóstico explícitamente menciona cabeza/cuello.
    # Si el dx es genérico, la inferencia por órgano (V6.6.8) refinará usando
    # el campo Organo (LENGUA, PALADAR, etc.).
    "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO": [
        "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
        "CARCINOMA ESCAMOSO DE CABEZA Y CUELLO",
        "CARCINOMA EPIDERMOIDE DE LENGUA",
        "CARCINOMA EPIDERMOIDE DE LARINGE",
        "CARCINOMA EPIDERMOIDE DE OROFARINGE",
        "CARCINOMA ESCAMOCELULAR DE LENGUA",
        "CARCINOMA ESCAMOCELULAR DE LARINGE",
        "CARCINOMA ESCAMOCELULAR DE PALADAR",
    ],
    "CARCINOMA ESCAMOCELULAR DE PIEL": [
        "CARCINOMA ESCAMOCELULAR DE PIEL",
        "CARCINOMA EPIDERMOIDE DE PIEL",
        "CARCINOMA ESCAMOCELULAR CUTANEO",
    ],

    # === Carcinomas escamosos en general (fallback) ===
    "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)": [
        "CARCINOMA ESCAMOCELULAR", "CARCINOMA EPIDERMOIDE",
        "CARCINOMA DE CELULAS ESCAMOSAS",
    ],

    # === Adenocarcinomas con origen identificable ===
    "ADENOCARCINOMA COLORRECTAL": [
        "ADENOCARCINOMA DE COLON", "ADENOCARCINOMA COLORRECTAL",
        "ADENOCARCINOMA DE RECTO", "ADENOCARCINOMA COLONICO",
        # Hallazgos de invasión pericólica (típico de cáncer colorrectal
        # operado): el diagnóstico menciona "INVASIÓN DE TEJIDO PERICÓLICO"
        # como característica patognomónica.
        "INVASION DE TEJIDO PERICOLICO",
        "TEJIDO PERICOLICO",
        "PERICOLICO",
    ],
    "ADENOCARCINOMA GASTRICO": [
        "ADENOCARCINOMA GASTRICO", "ADENOCARCINOMA DE ESTOMAGO",
    ],
    # Carcinoma poco cohesivo / de células en anillo de sello —
    # histología característicamente gástrica (también puede ser de mama
    # lobulillar o de vesícula). Va aparte de ADENOCARCINOMA GASTRICO
    # porque el diagnóstico no siempre menciona el órgano.
    "CARCINOMA POCO COHESIVO / CELULAS EN ANILLO DE SELLO": [
        "CARCINOMA POCO COHESIVO",
        "POCO COHESIVO",
        "CELULAS EN ANILLO DE SELLO",
        "CARCINOMA DE CELULAS EN ANILLO",
        "ANILLO DE SELLO",
        "TIPO SELLO",
    ],
    "ADENOCARCINOMA DE PANCREAS / VIA BILIAR": [
        "ADENOCARCINOMA DE PANCREAS", "ADENOCARCINOMA PANCREATICO",
        "COLANGIOCARCINOMA", "ADENOCARCINOMA DE VIAS BILIARES",
    ],
    "HEPATOCARCINOMA": [
        "HEPATOCARCINOMA", "CARCINOMA HEPATOCELULAR",
    ],

    # === Metastásicos ===
    "CARCINOMA METASTASICO": [
        "METASTASICO", "METASTASIS", "ORIGEN MAMARIO", "ORIGEN PULMONAR",
        "ORIGEN COLORRECTAL", "ORIGEN GINECOLOGICO",
    ],

    # === Resultado IHQ usado como "diagnóstico" (sin tumor específico) ===
    # Se evalúa DESPUÉS de todos los carcinomas/linfomas específicos para que
    # textos como "ADENOCARCINOMA CON EXPRESION POSITIVA DE CK7" matcheen
    # primero el adenocarcinoma. Solo captura cuando el "diagnóstico" es
    # estrictamente un resultado IHQ sin entidad clínica nombrada.
    "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)": [
        "EXPRESION DE CD",
        "EXPRESION DE LOS MARCADORES",
        "EXPRESION POSITIVA PARA",
        "EXPRESION NEGATIVA PARA",
        "AUSENCIA DE EXPRESION",
        "PERDIDA DE EXPRESION",
        "SOBREEXPRESION DE HER",
        "SOBREEXPRESION DE",
        "HER-2 EQUIVOCO",
        "HER2 EQUIVOCO",
        "EQUIVOCO PARA HER",
        "PERFIL INMUNOHISTOQUIMICO",
        "PANEL INMUNOHISTOQUIMICO",
    ],

    # === Adenocarcinoma genérico (último: solo si no calzó arriba) ===
    "ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)": [
        "ADENOCARCINOMA",
    ],
    "CARCINOMA (OTRO/INESPECIFICO)": ["CARCINOMA"],

    # === Lesiones benignas ===
    "LESION BENIGNA / HIPERPLASIA": [
        "HIPERPLASIA", "FIBROADENOMA", "ADENOMA", "POLIPO",
        "QUISTE", "LIPOMA", "HEMANGIOMA",
        # Lesiones benignas mamarias adicionales
        "ADENOSIS ESCLEROSANTE",
        "ADENOSIS",
        "MASTOPATIA FIBROQUISTICA",
        "CAMBIOS FIBROQUISTICOS",
        "PAPILOMA",
    ],
}


# El orden importa: las llaves de dict en Python 3.7+ se preservan, así
# que se evalúan en el orden definido arriba (de más específico a más
# genérico).
ORDEN_EVALUACION: list[str] = list(CATEGORIAS_DIAGNOSTICO.keys())


def categorizar_diagnostico(valor: str) -> str:
    """Devuelve la categoría canónica para un diagnóstico libre.

    Si no se reconoce, devuelve ``"OTRO / NO CATEGORIZADO"``.
    Si el valor está vacío, devuelve ``"SIN DATO"``.
    """
    if valor is None:
        return "SIN DATO"
    t = normalizar_texto(str(valor))
    if not t or t in {"N/A", "NA", "SIN DATO", "NO MENCIONADO", "NONE", "NULL"}:
        return "SIN DATO"

    for categoria in ORDEN_EVALUACION:
        for patron in CATEGORIAS_DIAGNOSTICO[categoria]:
            if patron in t:
                return categoria

    return "OTRO / NO CATEGORIZADO"


# Mapeo de inferencia órgano → categoría refinada cuando el dx es genérico
# V6.6.8: Para casos donde el patólogo escribió un dx genérico ("ADENOCARCINOMA
# INVASIVO" sin especificar origen), inferir la categoría usando el órgano.
# Solo se aplica para 3 categorías genéricas:
#   - "ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)"
#   - "CARCINOMA (OTRO/INESPECIFICO)"
#   - "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)"
INFERENCIA_POR_ORGANO_ADENO = {
    # ADENOCARCINOMA + órgano → categoría específica
    "COLON": "ADENOCARCINOMA COLORRECTAL",
    "RECTO": "ADENOCARCINOMA COLORRECTAL",
    "SIGMOIDES": "ADENOCARCINOMA COLORRECTAL",
    "CIEGO": "ADENOCARCINOMA COLORRECTAL",
    "ESTOMAGO": "ADENOCARCINOMA GASTRICO",
    "PULMON": "CARCINOMA DE PULMON (NO MICROCITICO)",
    "ENDOMETRIO": "CARCINOMA DE ENDOMETRIO / UTERO",
    "UTERO": "CARCINOMA DE ENDOMETRIO / UTERO",
    "CERVIX": "CARCINOMA DE CERVIX (ESCAMOCELULAR/ADENO)",
    "PROSTATA": "CARCINOMA DE PROSTATA",
    "RIÑON": "CARCINOMA RENAL",
    "RINON": "CARCINOMA RENAL",
    "PANCREAS": "ADENOCARCINOMA DE PANCREAS / VIA BILIAR",
    "VIA BILIAR": "ADENOCARCINOMA DE PANCREAS / VIA BILIAR",
    "VESICULA BILIAR": "ADENOCARCINOMA DE PANCREAS / VIA BILIAR",
    "HIGADO": "HEPATOCARCINOMA",
    "MAMA": "OTRO CARCINOMA DE MAMA",
    "OVARIO": "CARCINOMA DE OVARIO",
}

INFERENCIA_POR_ORGANO_ESCAMO = {
    # CARCINOMA ESCAMOCELULAR + órgano → categoría específica
    "CERVIX": "CARCINOMA DE CERVIX (ESCAMOCELULAR/ADENO)",
    "PULMON": "CARCINOMA DE PULMON (NO MICROCITICO)",
    "LENGUA": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "PALADAR": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "AMIGDALA": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "AMIGDALAS": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "OROFARINGE": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "LARINGE": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "CAVIDAD ORAL": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "ENCIA": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "PIEL": "CARCINOMA ESCAMOCELULAR DE PIEL",
}


def categorizar_diagnostico_con_organo(valor_dx, valor_organo):
    """Versión enriquecida que usa el órgano para refinar diagnósticos genéricos.

    V6.6.8 — Implementa Opción β del feedback clínico: cuando el patólogo
    escribió un diagnóstico genérico ("ADENOCARCINOMA INVASIVO" sin órgano),
    pero el campo Organo está poblado, inferir la categoría específica.

    V6.6.10 — Agregada lógica para casos "ESCAMOCELULAR METASTÁSICO" que
    deben categorizarse como CARCINOMA METASTÁSICO (la metástasis es lo
    clínicamente más relevante; el sitio primario suele ser desconocido).

    NO sobrescribe categorías ya específicas — solo refina las 3 genéricas.

    Args:
        valor_dx: Diagnóstico libre del patólogo
        valor_organo: Órgano canónico (ej: "COLON", "MAMA"; output de
                      normalizador_organos.normalizar_organo)

    Returns:
        Categoría canónica refinada usando contexto de órgano cuando aplique.
    """
    base = categorizar_diagnostico(valor_dx)

    # Solo refinar categorías genéricas
    if base not in (
        "ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)",
        "CARCINOMA (OTRO/INESPECIFICO)",
        "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)",
    ):
        return base

    # V6.6.10: Si el dx menciona METÁSTASIS pero cayó en categoría genérica
    # (ej. "CARCINOMA ESCAMOCELULAR METASTÁSICO" sin sitio primario claro),
    # categorizar como CARCINOMA METASTASICO. La metástasis tiene prioridad
    # clínica sobre la histología cuando el primario no está identificado.
    dx_norm = normalizar_texto(str(valor_dx)) if valor_dx else ""
    if any(kw in dx_norm for kw in ["METASTASICO", "METASTASIS", "METASTATICO"]):
        return "CARCINOMA METASTASICO"

    if not valor_organo:
        return base
    organo_norm = normalizar_texto(str(valor_organo))
    if not organo_norm or organo_norm == "SIN DATO":
        return base

    # Adenocarcinoma genérico → buscar inferencia
    if base in ("ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)", "CARCINOMA (OTRO/INESPECIFICO)"):
        for organo_key, categoria_refinada in INFERENCIA_POR_ORGANO_ADENO.items():
            if organo_key in organo_norm:
                return categoria_refinada

    # Carcinoma escamocelular genérico → buscar inferencia
    if base == "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)":
        for organo_key, categoria_refinada in INFERENCIA_POR_ORGANO_ESCAMO.items():
            if organo_key in organo_norm:
                return categoria_refinada

    return base


# --- self-test ----------------------------------------------------------
if __name__ == "__main__":
    casos = [
        ("CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL)", "CARCINOMA DUCTAL DE MAMA"),
        ("CARCINOMA DUCTAL INFILTRANTE GRADO 2", "CARCINOMA DUCTAL DE MAMA"),
        ("ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO", "ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)"),
        ("ADENOCARCINOMA DE COLON BIEN DIFERENCIADO", "ADENOCARCINOMA COLORRECTAL"),
        ("CARCINOMA METASTÁSICO DE PROBABLE ORIGEN MAMARIO", "CARCINOMA METASTASICO"),
        ("LINFOMA DIFUSO DE CÉLULAS B GRANDES", "LINFOMA NO HODGKIN B"),
        ("LINFOMA DE HODGKIN CLASICO", "LINFOMA HODGKIN"),
        ("LEUCEMIA MIELOIDE AGUDA", "LEUCEMIA MIELOIDE"),
        ("MIELOMA MULTIPLE", "MIELOMA / NEOPLASIA PLASMOCELULAR"),
        ("MELANOMA MALIGNO NODULAR", "MELANOMA"),
        ("SARCOMA DE KAPOSI", "SARCOMA DE KAPOSI"),
        ("SCHWANNOMA", "SCHWANNOMA / NEURINOMA"),
        ("MENINGIOMA GRADO I", "MENINGIOMA"),
        ("GLIOBLASTOMA MULTIFORME", "GLIOMA / ASTROCITOMA / GLIOBLASTOMA"),
        ("ADENOCARCINOMA ACINAR DE LA PROSTATA", "CARCINOMA DE PROSTATA"),
        ("CARCINOMA UROTELIAL DE ALTO GRADO", "CARCINOMA UROTELIAL"),
        ("ADENOCARCINOMA DE PULMÓN", "CARCINOMA DE PULMON (NO MICROCITICO)"),
        ("CARCINOMA ESCAMOCELULAR INVASIVO", "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)"),
        ("HEPATOCARCINOMA", "HEPATOCARCINOMA"),
        ("GIST DE BAJO GRADO", "GIST (TUMOR ESTROMAL GASTROINTESTINAL)"),
        ("NEGATIVO PARA MALIGNIDAD", "NEGATIVO PARA MALIGNIDAD"),
        ("NEGATIVO PARA NEOPLASIA", "NEGATIVO PARA MALIGNIDAD"),
        ("ESTUDIO DE INMUNOHISTOQUÍMICA", "ESTUDIO IHQ (SIN DIAGNOSTICO ESPECIFICO)"),
        ("TUMOR DE CÉLULAS GRANULARES", "TUMOR DE CELULAS GRANULARES"),
        ("FIBROADENOMA", "LESION BENIGNA / HIPERPLASIA"),
        ("", "SIN DATO"),
        ("N/A", "SIN DATO"),
        # === Cobertura ampliada (casos reales del HUV antes "OTRO/NO CATEGORIZADO") ===
        ("HETEROTOPIA NEURONAL", "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC"),
        ("FIBROMATOSIS DE TIPO DESMOIDE", "FIBROMATOSIS / TUMOR DESMOIDE"),
        ("NEGATIVO PARA LESIÓN ESCAMOSA PREINVASIVA/INVASIVA", "NEGATIVO PARA MALIGNIDAD"),
        ("TUMOR DEL ESTROMA GASTROINTESTINALFUSOCELULAR DE BAJO GRADO", "GIST (TUMOR ESTROMAL GASTROINTESTINAL)"),
        ("ADENOSIS ESCLEROSANTE CON ABUNDANTES MICROCALCIFICACIONES", "LESION BENIGNA / HIPERPLASIA"),
        ("RIÑÓN (BIOPSIA POR PUNCIÓN): TEJIDO SIN REPRESENTACIÓN DE PARENQUIMA RENAL",
         "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA"),
        ("HALLAZGOS SUGESTIVOS DE NEOPLASIA EN PATRON ACINAR CON CAMBIOS ONCOCITICOS DE PROBABLE ORIGEN RENAL",
         "CARCINOMA RENAL"),
        ("EXPRESIÓN DE CD117 Y CD56 NEGATIVA", "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)"),
        ("SOBREEXPRESIÓN DE HER-2: EQUÍVOCO", "RESULTADO IHQ (SIN DIAGNOSTICO ESPECIFICO)"),
        ("TIMOMA TIPO B2", "TIMOMA / NEOPLASIA TIMICA"),
        ("CRANEOFARINGIOMA ADAMANTINOMATOSO", "CRANEOFARINGIOMA"),
        ("RECHAZO ACTIVO CON DATOS SUGERENTES DE COMPONENTE HUMORAL", "RECHAZO DE TRASPLANTE"),
        ("HALLAZGOS QUE FAVORECEN GLIOSIS REACTIVA", "GLIOSIS / LESION REACTIVA SNC"),
        ("EXOCÉRVIX NEGATIVO", "NEGATIVO PARA MALIGNIDAD"),
        ("CÉLULAS GANGLIONARES PRESENTES", "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO"),
        # === Refinamiento de categorías genéricas (V6.5.95) ===
        # Adenocarcinomas con origen sugestivo
        ("ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO DE PROBABLE ORIGEN ENDOCERVICAL",
         "CARCINOMA DE CERVIX (ESCAMOCELULAR/ADENO)"),
        ("ADENOCARCINOMA DE PROBABLE ORIGEN ENDOMETRIAL", "CARCINOMA DE ENDOMETRIO / UTERO"),
        ("ADENOCARCINOMA INVASIVO PULMONAR EN PATRÓN SOLIDO", "CARCINOMA DE PULMON (NO MICROCITICO)"),
        ("ADENOCARCINOMA MODERADAMENTE DIFERENCIADO CON INVASIÓN DE TEJIDO PERICÓLICO",
         "ADENOCARCINOMA COLORRECTAL"),
        # Carcinoma ductal de mama (variantes con/sin "INVASIVO")
        ("CARCINOMA INVASIVO SIN TIPO ESPECIAL (DUCTAL)", "CARCINOMA DUCTAL DE MAMA"),
        ("CARCINOMA DUCTAL", "CARCINOMA DUCTAL DE MAMA"),
        # IN SITU debe seguir matcheando IN SITU, no DUCTAL invasivo
        ("CARCINOMA DUCTAL IN SITU DE ALTO GRADO", "CARCINOMA IN SITU DE MAMA (DCIS/LCIS)"),
        ("CARCINOMA INTRADUCTAL", "CARCINOMA IN SITU DE MAMA (DCIS/LCIS)"),
        # Linfoma B (variantes adicionales)
        ("LINFOMA DE CELULAS B MADURAS", "LINFOMA NO HODGKIN B"),
        # Carcinoma poco cohesivo (gástrico típico)
        ("CARCINOMA POCO COHESIVO - PATRÓN MICROSATELITAL ESTABLE",
         "CARCINOMA POCO COHESIVO / CELULAS EN ANILLO DE SELLO"),
        # Carcinoma nasofaríngeo
        ("CARCINOMA ESCAMOSO NO QUERATINIZANTE NEGATIVO PARA TINCIÓN CON LMP-1",
         "CARCINOMA NASOFARINGEO"),
        # No-regresión: ADENOCARCINOMA MUCINOSO sin contexto NO debe ir a OTRO CARCINOMA DE MAMA
        ("ADENOCARCINOMA MUCINOSO", "ADENOCARCINOMA (SIN ORIGEN ESPECIFICADO)"),
    ]

    ok = 0
    fail = 0
    for entrada, esperado in casos:
        obtenido = categorizar_diagnostico(entrada)
        marca = "[OK]" if obtenido == esperado else "[FAIL]"
        if obtenido == esperado:
            ok += 1
        else:
            fail += 1
        print(f"  {marca} {entrada!r:55s} → {obtenido!r}  (esperado: {esperado!r})")

    print(f"\nTotal: {ok} OK, {fail} FAIL")
