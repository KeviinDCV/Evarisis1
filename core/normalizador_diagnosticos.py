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
    # V6.6.12 FIX typos del patólogo: corregir errores ortográficos
    # comunes ANTES del matching de patrones. Estos typos hacen que
    # casos oncológicos reales (ej. IHQ250060) caigan en
    # "OTRO / NO CATEGORIZADO".
    t = t.replace("CARICNOMA", "CARCINOMA")
    # V6.6.16 FIX IHQ250026: el patólogo escribió "HISTOLOGIOS" (typo
    # OCR/dactilográfico, falta la 'C'). Sin esta corrección, el
    # preámbulo "LOS HALLAZGOS HISTOLOGICOS Y DE INMUNOHISTOQUIMICA
    # SON COMPATIBLES CON" no matchea y el caso (MELANOMA) cae en
    # "ESTUDIO IHQ".
    t = t.replace("HISTOLOGIOS", "HISTOLOGICOS")
    return t


# V6.6.14 — Preámbulos típicos del patólogo del HUV. Cuando el dx empieza
# con una de estas frases, la entidad clínica real (CARCINOMA, LINFOMA,
# MELANOMA, etc.) viene DESPUÉS. Sin stripear el preámbulo, el matching
# se queda en "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)" porque la palabra
# "INMUNOHISTOQUIMICA" matchea primero.
#
# IMPORTANTE: este stripping ocurre ÚNICAMENTE sobre una copia local del
# texto durante la categorización. NO modifica el dato original guardado
# en BD (`Diagnostico Principal`) ni el OCR. El campo del patólogo queda
# intacto, exactamente como él lo escribió. Solo cambia cómo el bucketing
# estadístico interpreta el texto para asignar categoría.
#
# Ordenado por LONGITUD DESCENDIENTE para que la frase más larga gane
# primero (ej: "LOS HALLAZGOS MORFOLOGICOS Y EL PERFIL DE EXPRESION..."
# debe stripear antes que "LOS HALLAZGOS").
PREAMBULOS_PATOLOGO: list[str] = [
    "LOS HALLAZGOS MORFOLOGICOS Y EL PERFIL DE EXPRESION DE INMUNOHISTOQUIMICA FAVORECEN",
    "LOS HALLAZGOS HISTOLOGICOS Y DE INMUNOHISTOQUIMICA SON COMPATIBLES CON",
    "LOS HALLAZGOS MORFOLOGICOS Y DE INMUNOHISTOQUIMICA FAVORECEN",
    "HALLAZGOS MORFOLOGICOS Y DE INMUNOHISTOQUIMICA COMPATIBLE CON",
    "HALLAZGOS DE INMUNOHISTOQUIMICA COMPATIBLES CON",
    "HALLAZGOS DE INMUNOHISTOQUIMICA COMPATIBLE CON",
    "PERFIL DE EXPRESION DE INMUNOHISTOQUIMICA COMPATIBLE CON",
    "PERFIL DE EXPRESION DE INMUNOHISTOQUIMICA QUE FAVORECE",
    "PERFIL DE INMUNOHISTOQUIMICA COMPATIBLE CON",
    "LOS HALLAZGOS DE INMUNOHISTOQUIMICA FAVORECEN",
    "ESTUDIO DE INMUNOHISTOQUIMICA",
]


# V6.9.29 FIX: palabras que identifican la ENTIDAD clínica como tal. Si el
# "header ÓRGANO:" capturado por el regex de stripping contiene una de
# estas, NO se debe strippear — porque ese "header" ES el diagnóstico
# (ej. "TUMOR NEUROENDOCRINO GRADO HISTOLOGICO:" o "TUMOR DEL ESTROMA DE
# LOS CORDONES SEXUALES :"). Antes, el regex se comía el dx real y lo
# mandaba a OTRO / NO CATEGORIZADO. Los órganos legítimos (VEJIGA, MAMA,
# RIÑON, etc.) nunca contienen estas palabras, así que el caso de uso
# original ("VEJIGA: LOS HALLAZGOS...") sigue funcionando.
_KEYWORDS_ENTIDAD_DX: tuple[str, ...] = (
    "TUMOR", "CARCINOMA", "ADENOCARCINOMA", "NEOPLASIA", "LINFOMA",
    "LEUCEMIA", "SARCOMA", "MELANOMA", "MIELOMA", "BLASTOMA", "GLIOMA",
    "MENINGIOMA", "CARCINOSARCOMA", "MESOTELIOMA", "SCHWANNOMA", "TIMOMA",
    # V6.9.41: hallazgos que NO son órgano -> el header-stripper NO debe borrarlos
    # ("LINFOCITOS INTRAEPITELIALES:" no es una cabecera de órgano sino el hallazgo).
    "LINFOCITOS INTRAEPITELIALES",
)


def stripear_preambulos(texto: str) -> str:
    """Elimina preámbulos del patólogo del INICIO del texto, solo para
    propósitos de categorización. NO modifica el dato original.

    Si el texto empieza con un preámbulo conocido y queda contenido
    sustantivo después, devuelve el contenido residual. Si no, devuelve
    el texto sin cambios.

    También strip-pea headers de órgano "ÓRGANO:" al inicio (ej.
    "VEJIGA: HALLAZGOS..." → "HALLAZGOS...").
    """
    if not texto:
        return texto

    t = texto

    def intentar_strip_preambulo(s: str) -> str:
        for preambulo in PREAMBULOS_PATOLOGO:
            if s.startswith(preambulo):
                residual = s[len(preambulo):].strip()
                # Solo strippear si queda al menos 1 palabra de 4+ chars.
                # Evita borrar el dx cuando el texto es solo el preámbulo
                # (caso "ESTUDIO DE INMUNOHISTOQUIMICA" sin más). Permite
                # 1 palabra para casos como "MELANOMA" o "LEIOMIOSARCOMA"
                # donde la entidad clínica es una sola palabra.
                palabras = residual.split()
                if len(palabras) >= 1 and len(palabras[0]) >= 4:
                    return residual
        return s

    # 1. Stripear preámbulo si está al inicio
    t = intentar_strip_preambulo(t)

    # 2. Stripear header "ÓRGANO:" al inicio (ej. "VEJIGA: ...")
    # Requisito: 4+ caracteres en mayúsculas (excluye M:, X:, etc.) y
    # al menos 3 palabras de contenido residual.
    header_match = re.match(r'^([A-Z]{4,}(?:\s+[A-Z]+)*)\s*:\s*', t)
    if header_match:
        cabecera = header_match.group(1)
        # V6.9.29 FIX: si la "cabecera" ya contiene la entidad clínica
        # (TUMOR, CARCINOMA, etc.), NO strippear — el dx real está ahí.
        tiene_entidad = any(kw in cabecera for kw in _KEYWORDS_ENTIDAD_DX)
        residual = t[header_match.end():].strip()
        if not tiene_entidad and len(residual.split()) >= 3:
            t = residual

    # 3. Stripear preámbulo OTRA vez (caso "VEJIGA: LOS HALLAZGOS...")
    t = intentar_strip_preambulo(t)

    return t


# --- categorías canónicas ----------------------------------------------
# Orden de evaluación: específicas primero. Cada entrada es una lista de
# patrones (substrings) que activan la categoría.

CATEGORIAS_DIAGNOSTICO: dict[str, list[str]] = {
    # === No oncológico / control ===
    "NEGATIVO PARA MALIGNIDAD": [
        "NEGATIVO PARA MALIGNIDAD",
        "NEGATIVO PARA NEOPLASIA",
        "NEGATIVO PARA CARCINOMA", "NEGATIVO PARA CARCINOMA METASTASICO",
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
    # V6.6.16 FIX IHQ250037, IHQ250075, IHQ250061: procesos inflamatorios
    # e infecciosos no oncológicos. Antes caían en OTRO/NO CATEGORIZADO
    # aunque el extractor de Malignidad los marca BENIGNO correctamente.
    # Va antes de ESTUDIO IHQ para que matchee primero por la inflamación
    # específica en lugar del header genérico de IHQ.
    "INFLAMACION / PROCESO INFECCIOSO": [
        "INFLAMACION AGUDA",
        "INFLAMACION CRONICA",
        "INFLAMACION GRANULOMATOSA",
        "PERITONITIS AGUDA",
        "PERITONITIS CRONICA",
        "PERITONITIS",
        "COLITIS AGUDA",
        "COLITIS CRONICA",
        "GASTRITIS",
        "ENTERITIS",
        "PROCTITIS",
        "GRANULOMA",
        "ABSCESO",
        # Hallazgo característico de Hirschsprung sin enfermedad
        "NO SE IDENTIFICAN CELULAS GANGLIONARES",
    ],
    "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)": [
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
        # V6.6.13 FIX IHQ250081: nomenclatura OMS 2022 — algunos patólogos
        # usan "NEOPLASIA DE CELULAS B" en lugar de "LINFOMA". Captura
        # estas redacciones para que no caigan en OTRO/NO CATEGORIZADO.
        "NEOPLASIA DE CELULAS B MADURAS",
        "NEOPLASIA DE CELULAS B MADURA",
        "NEOPLASIA B MADURA",
        # V6.6.14 FIX IHQ250164: "LINFOMA EXTRANODAL DE LA ZONA MARGINAL"
        # tiene EXTRANODAL en medio, así que el patrón "LINFOMA DE LA
        # ZONA MARGINAL" no matchea. Agregar "ZONA MARGINAL" como ancla
        # genérica para capturar todas las variantes (extranodal, nodal,
        # esplénico, etc.) que son linfomas B por definición.
        "ZONA MARGINAL",
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
    # V6.6.14 FIX IHQ250105: Reordenar — LEUCEMIA MIELOIDE y LEUCEMIA
    # LINFOIDE AGUDA deben evaluarse ANTES de LINFOMA (OTRO SUBTIPO)
    # porque "LEUCEMIA/LINFOMA LINFOBLASTICO" contiene la palabra
    # "LINFOMA" que dispararía LINFOMA (OTRO) primero. La leucemia
    # linfoblástica B (B-ALL/LBL) es una entidad específica.
    "LEUCEMIA MIELOIDE": [
        "LEUCEMIA MIELOIDE", "LEUCEMIA AGUDA MIELOIDE", "LMA", "LAM ",
        "SARCOMA MIELOIDE", "SARCOMA GRANULOCITICO",
    ],
    "LEUCEMIA LINFOIDE AGUDA": [
        "LEUCEMIA LINFOBLASTICA", "LEUCEMIA AGUDA LINFOBLASTICA", "LLA ",
        # V6.6.14 FIX IHQ250105: B-ALL/LBL puede presentarse como leucemia
        # o como linfoma; OMS 2022 los unifica. El patólogo a veces escribe
        # "LEUCEMIA/LINFOMA LINFOBLASTICO". Capturar ambos géneros (-O/-A)
        # y la forma con barra.
        "LEUCEMIA/LINFOMA LINFOBLASTICO",
        "LEUCEMIA/LINFOMA LINFOBLASTICA",
        "LINFOMA LINFOBLASTICO",
        "LINFOMA LINFOBLASTICA",
    ],
    "LINFOMA (OTRO SUBTIPO)": ["LINFOMA"],
    "LEUCEMIA (OTRO SUBTIPO)": ["LEUCEMIA"],
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
        # V6.9.43: variantes que caían en "OTRO CARCINOMA DE MAMA" siendo ductales/
        # NST. "TIPO NO ESPECIAL" (NST) es terminología WHO exclusiva del carcinoma
        # de mama. Los demás llevan "MAMA" explícito. NO se usan "NOS"/"(DUCTAL)"/
        # "SIN SUBTIPO" sueltos: capturaban escamocelular de cérvix y ductal pancreático.
        "TIPO NO ESPECIAL",
        "CARCINOMA INVASIVO DE MAMA", "CARCINOMA INFILTRANTE DE MAMA",
        "CARCINOMA DE MAMA INVASIVO", "CARCINOMA DE MAMA INFILTRANTE",
        # Variantes con preposición "SIN" (CARCINOMA INVASIVO SIN TIPO ESPECIAL)
        "CARCINOMA INVASIVO SIN TIPO ESPECIAL",
        "CARCINOMA INVASOR SIN TIPO ESPECIAL",
        "SIN TIPO ESPECIAL",
        # V6.9.44: se RETIRÓ "CARCINOMA DUCTAL" suelto -> capturaba "adenocarcinoma
        # DUCTAL pancreático" (y otros ductales no-mama) como mama. Los ductales de
        # mama reales se cubren con los patrones explícitos de arriba; si el dx solo
        # dice "carcinoma ductal" y el órgano es mama, lo recupera la inferencia
        # órgano=mama (categorizar_diagnostico_con_organo, regla "DUCTAL").
    ],
    "CARCINOMA LOBULILLAR DE MAMA": [
        "CARCINOMA LOBULILLAR", "CARCINOMA LOBULAR",
    ],
    "CARCINOMA DE MAMA (SIN SUBTIPO ESPECIFICADO)": [
        # V6.9.43/44: los subtipos (ductal/NST, medular, tubular, papilar...) se
        # resuelven en categorías propias vía _SUBTIPOS_MAMA y la inferencia NST
        # (solo con órgano=mama). Aquí solo caen los carcinomas de mama cuyo dx
        # NO trae subtipo extraíble (p.ej. "carcinoma invasivo con neoadyuvancia",
        # dx truncado). Nombre honesto: es de mama pero el PDF no dio el subtipo.
    ],
    # V6.6.13 FIX IHQ250116: Carcinoma papilar de mama es entidad
    # distinta de la OMS. El patólogo lo describe a veces como "LESION
    # NEOPLASICA EN PATRON PAPILAR" sin nombrar explícitamente carcinoma.
    # Patrones específicos de mama para evitar falsos positivos en otros
    # órganos (tiroides, vejiga, ovario serio).
    "CARCINOMA PAPILAR DE MAMA": [
        "CARCINOMA PAPILAR DE MAMA",
        "CARCINOMA PAPILAR INTRADUCTAL",
        "CARCINOMA PAPILAR INVASIVO DE MAMA",
        "LESION NEOPLASICA EN PATRON PAPILAR",
        "PATRON PAPILAR CON ATIPIA",
    ],
    # V6.6.13 FIX IHQ250071: Tumor Filodes es neoplasia estromal mamaria
    # distinta de los carcinomas. Puede ser benigno, borderline o maligno.
    "TUMOR FILODES DE MAMA": [
        "TUMOR FILODES",
        "TUMOR PHYLLODES",
        "FILODES",
        "PHYLLODES",
    ],

    # === Tumores neuroendocrinos ===
    "TUMOR / CARCINOMA NEUROENDOCRINO": [
        "CARCINOMA NEUROENDOCRINO", "TUMOR NEUROENDOCRINO", "CARCINOIDE",
        "TUMOR DE CELULAS PEQUENAS", "CARCINOMA DE CELULAS PEQUENAS",
        "NEURO ENDOCRINO",
        # V6.9.44: variantes que caían en la categoría mezclada de abajo.
        # "TUMOR NEUROENDOCRINA" (typo con A) y "DIFERENCIACION NEUROENDOCRINA".
        # NO capturan "...HIPOFISARIO" (usa NEUROENDOCRINO con O).
        "TUMOR NEUROENDOCRINA", "DIFERENCIACION NEUROENDOCRINA",
    ],

    # === Sistema digestivo / GIST ===
    # Patrones flexibles para capturar variantes con OCR ruidoso (palabras
    # pegadas) y formas con/sin "DEL".
    "GIST (TUMOR ESTROMAL GASTROINTESTINAL)": [
        "GIST",
        "TUMOR ESTROMAL GASTROINTESTINAL",
        "TUMOR DEL ESTROMA GASTROINTESTINAL",
        "ESTROMA GASTROINTESTINAL",
        # V6.9.30: variantes que nombran el órgano (estómago) sin "GASTROINTESTINAL"
        "ESTROMA GASTRICO", "ESTROMA ESTOMAGO", "ESTROMA DEL ESTOMAGO",
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
    # V6.9.42 FIX: PARAGANGLIOMA / FEOCROMOCITOMA antes de GLIOMA — "paraganGLIOMA"
    # contiene "GLIOMA" como substring y caía mal en la categoría de gliomas.
    "PARAGANGLIOMA / FEOCROMOCITOMA": [
        "PARAGANGLIOMA", "FEOCROMOCITOMA", "GLOMUS YUGULAR", "TUMOR DEL GLOMUS",
    ],
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
    # V6.6.14 FIX IHQ250166: Carcinoma anexial cutáneo es entidad rara
    # pero distinta de los carcinomas escamocelulares de piel (origina
    # de glándulas/anexos cutáneos: sebáceas, sudoríparas, foliculares).
    "CARCINOMA ANEXIAL CUTANEO": [
        "CARCINOMA ANEXIAL CUTANEO",
        "CARCINOMA ANEXIAL",
        "CARCINOMA DE ANEXOS CUTANEOS",
        "CARCINOMA SEBACEO",
        "CARCINOMA SUDORIPARO",
    ],

    # === Sarcomas y partes blandas ===
    "SARCOMA DE KAPOSI": ["SARCOMA DE KAPOSI", "KAPOSI"],
    "LIPOSARCOMA": ["LIPOSARCOMA"],
    "LEIOMIOSARCOMA": ["LEIOMIOSARCOMA"],
    "RABDOMIOSARCOMA": ["RABDOMIOSARCOMA"],
    "OSTEOSARCOMA / SARCOMA OSEO": [
        "OSTEOSARCOMA", "SARCOMA OSEO", "CONDROSARCOMA", "EWING",
    ],
    # V6.9.43: subtipos de sarcoma que NO tenían categoría propia (DFSP,
    # angiosarcoma, condrosarcoma, sinovial). LIPOSARCOMA/LEIOMIOSARCOMA/
    # RABDOMIOSARCOMA/OSTEOSARCOMA ya existen arriba -> NO se redefinen (evita
    # duplicar clave). Los sarcomas sin subtipo caen en "SARCOMA (OTRO SUBTIPO)".
    "DERMATOFIBROSARCOMA PROTUBERANS": ["DERMATOFIBROSARCOMA"],
    "ANGIOSARCOMA": ["ANGIOSARCOMA"],
    "CONDROSARCOMA": ["CONDROSARCOMA"],
    "SARCOMA SINOVIAL": ["SARCOMA SINOVIAL"],
    "TUMOR DE CELULAS GRANULARES": ["TUMOR DE CELULAS GRANULARES"],
    "TUMOR FIBROSO SOLITARIO / HEMANGIOPERICITOMA": [
        "TUMOR FIBROSO SOLITARIO", "HEMANGIOPERICITOMA",
        "TUMOR FIBOSO SOLITARIO", "TUMOR FIBOSO",  # typo frecuente del patólogo
    ],
    "FIBROMATOSIS / TUMOR DESMOIDE": [
        "FIBROMATOSIS DE TIPO DESMOIDE",
        "TUMOR DESMOIDE",
        "FIBROMATOSIS DESMOIDE",
        "FIBROMATOSIS",
        "DESMOIDE",
    ],
    # V6.6.13 FIX IHQ250107: Lesiones de células fusiformes son una
    # categoría histológica que puede contener sarcomas, melanoma
    # fusocelular, GIST, etc. Cuando el patólogo describe "LESION EN
    # PATRON FUSIFORME" sin nombrar la entidad específica, va aquí
    # como neoplasia mesenquimal indeterminada.
    "NEOPLASIA DE CELULAS FUSIFORMES / FUSOCELULAR": [
        "NEOPLASIA DE CELULAS FUSIFORMES",
        "LESION EN PATRON FUSIFORME",
        "LESION FUSIFORME",
        "LESION FUSOCELULAR",
        "TUMOR FUSOCELULAR",
        "PROLIFERACION FUSOCELULAR",
        "LESION DE CELULAS FUSIFORMES",
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
    # V6.6.13 FIX IHQ250066/IHQ250126: Lesiones intraepiteliales (NIC,
    # HSIL, LSIL) son neoplasias preinvasivas según OMS. La "N" en NIC
    # significa Neoplasia. Va ANTES de CARCINOMA DE CERVIX para evitar
    # que un NIC matchee patrones cervicales invasivos.
    "LESION ESCAMOSA INTRAEPITELIAL / NIC": [
        "LESION ESCAMOSA INTRAEPITELIAL",
        "LESION INTRAEPITELIAL ESCAMOSA",
        "NEOPLASIA INTRAEPITELIAL CERVICAL",
        "NEOPLASIA INTRAEPITELIAL",
        "NIC 3", "NIC 2", "NIC 1",
        "HSIL", "LSIL",
        "DISPLASIA CERVICAL",
    ],
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
    "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)": [
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
        # V6.9.44: el adenocarcinoma DUCTAL de páncreas (tipo más común) se nombra
        # "ductal pancreático / ductal de páncreas"; antes caía en ductal de mama.
        "DUCTAL PANCREATICO", "DUCTAL DE PANCREAS",
    ],
    "HEPATOCARCINOMA": [
        "HEPATOCARCINOMA", "CARCINOMA HEPATOCELULAR",
    ],

    # === Metastásicos ===
    "CARCINOMA METASTASICO": [
        "METASTASICO", "METASTASIS", "ORIGEN MAMARIO", "ORIGEN PULMONAR",
        "ORIGEN COLORRECTAL", "ORIGEN GINECOLOGICO",
    ],

    # === Adenocarcinoma / carcinoma genéricos ===
    # V6.6.14 FIX IHQ250028, IHQ250147: Reordenados ANTES de RESULTADO IHQ.
    # Razón: textos como "ADENOCARCINOMA BIEN DIFERENCIADO INFILTRANTE
    # CON PATRÓN MICROSATELITAL ESTABLE SOBREEXPRESION DE HER-2" empiezan
    # con ADENOCARCINOMA (entidad clínica real) pero contienen
    # "SOBREEXPRESION DE" que disparaba RESULTADO IHQ. Si el texto
    # menciona ADENOCARCINOMA, es un adenocarcinoma — el resultado IHQ
    # de HER-2 es complementario, no el dx primario.
    "ADENOCARCINOMA (OTRAS LOCALIZACIONES)": [
        "ADENOCARCINOMA",
    ],
    "CARCINOMA (OTRAS LOCALIZACIONES)": ["CARCINOMA"],

    # === Resultado IHQ usado como "diagnóstico" (sin tumor específico) ===
    # Se evalúa DESPUÉS de todos los carcinomas/linfomas específicos y
    # adenocarcinomas genéricos para que textos como "ADENOCARCINOMA CON
    # EXPRESION POSITIVA DE CK7" matcheen primero el adenocarcinoma. Solo
    # captura cuando el "diagnóstico" es estrictamente un resultado IHQ
    # sin entidad clínica nombrada.
    "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)": [
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

    # ===================================================================
    # V6.9.23: Categorías AÑADIDAS AL FINAL (anti-regresión por construcción).
    # Se evalúan de últimas (primer-match-gana), así que SOLO capturan casos
    # que hoy caen en "OTRO / NO CATEGORIZADO"; no alteran ninguna categoría
    # existente. Patrones en MAYÚSCULA y SIN ACENTOS (normalizar_texto los
    # elimina). Diseñadas para reducir los 320 "sin categorizar".
    # ===================================================================
    "CARCINOSARCOMA / TUMOR MULLERIANO MIXTO": [
        "CARCINOSARCOMA", "MULLERIANO MALIGNO MIXTO",
    ],
    "TUMOR DE CORDONES SEXUALES / GRANULOSA": [
        "CELULAS DE LA GRANULOSA", "CELULAS DE GRANULOSA", "CORDONES SEXUALES",
    ],
    "TUMOR GLIAL / NEUROGLIAL (OTRO)": [
        "LESION GLIAL", "ORIGEN GLIAL", "TUMOR GLIAL", "GLIONEURONAL",
        "NEUROGLIAL", "GLIAL DE BAJO GRADO",
    ],
    # V6.9.44: la antigua "TUMOR NEUROENDOCRINO / ONCOCITICO (OTRO)" mezclaba 3
    # entidades clínicamente distintas. Separadas:
    #  - neuroendocrinos -> "TUMOR / CARCINOMA NEUROENDOCRINO" (más arriba)
    #  - neoplasia folicular de tiroides (Bethesda IV: adenoma vs ca. folicular)
    #  - oncocitoma / tumor oncocítico (renal sobre todo; benigno/bajo grado)
    "NEOPLASIA FOLICULAR DE TIROIDES": [
        "NEOPLASIA FOLICULAR", "CARCINOMA FOLICULAR",
    ],
    "ONCOCITOMA / TUMOR ONCOCITICO": [
        # Términos específicos -> NO captura "cambios oncocíticos" descriptivos
        # de otros dx (p.ej. patrón acinar renal -> CARCINOMA RENAL).
        "ONCOCITOMA", "TUMOR ONCOCITICO",
    ],
    "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES": [
        "HIRSCHSPRUNG", "AGANGLIONOSIS", "CELULAS GANGLIONARES", "CELULAS GANGLI",
    ],
    "NEOPLASIA HEMATOLINFOIDE A CLASIFICAR": [
        "HEMATOLINFOIDE", "LINFOPROLIFERATIVO", "PROLIFERACION LINFOIDE",
        "NEOPLASIA DE CELULAS T", "NEOPLASIA DE CELULA B", "NEOPLASIA DE CELULAS B",
        "MALT", "PRECURSORES MIELOIDES", "NEOPLASIA MIELODISPLASICA",
        "NEOPLASIA HISTIOCITICA", "PROLIFERACION HEMATOLINFOIDE", "FOLICULO LINFOIDE",
        "PROLIFERACION CUTANEA DE LINFOCITOS",
    ],
    "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)": [
        "MEGACARIOCITOS", "CELULARIDAD GLOBAL", "CELULARIDAD DEL", "RELACION MIELOIDE",
        "INCREMENTO DE BLASTOS", "TRES LINEAS", "MIELOPEROXIDASA", "RELACION MPO",
        "CELULARIDAD HEMATOPOYETICA", "TRILINEAL", "CELULARIDAD DISMINUIDA PARA LA EDAD",
        "CELULARIDAD INCREMENTADA", "CELULARIDAD AUMENTADA", "CELULARIDAD NORMAL PARA LA EDAD",
        "CELULARIDAD VARIABLE", "MEDULA OSEA HIPOCELULAR", "RELACION CD15",
    ],
    "MESOTELIOMA (MALIGNO)": ["MESOTELIOMA"],
    "NEOPLASIA BENIGNA / TUMOR NO MALIGNO": [
        "DERMATOFIBROMA", "DERMATOMIOFIBROMA", "LEIOMIOMA", "NEVUS",
        "HEMANGIOMA", "LINFANGIOMA", "HEMANGIOBLASTOMA", "HEMANGIOENDOTELIOMA",
        "HEMANGIONENDOTELIOMA", "HIBERNOMA", "LIPOMA", "CONDROBLASTOMA", "MIXOMA",
        "ANGIOFIBROMA", "FASCITIS NODULAR", "MIOFIBROMA", "CISTOADENOFIBROMA",
        "POROMA", "SEBACEOMA", "NODULO FIBROMUSCULAR", "TUMOR FILOIDES", "TUMOR FILODES",
        "TUMOR DE CELULAS GIGANTES", "PLEOMORFICO HIALINIZANTE",
        "NEOPLASIA SOLIDA PSEUDOPAPILAR", "PSEUDOPAPILAR", "NEOPLASIA QUISTICA MUCINOSA",
        "NEOPLASIA MUCINOSA APENDICULAR", "SEROMUCINOSO BORDERLINE",
        "PTERIGION", "CONDILOMA", "VITILIGO",
        "PROLIFERACION MELANOCITICA BENIGNA", "TUMOR CUTANEO ANEXIAL", "TUMOR ANEXIAL",
    ],
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)": [
        "DERMATITIS", "DERMATOSIS", "CERVICITIS", "ENDOCERVICITIS", "NEFRITIS",
        "GLOMERULONEFRITIS", "GLOMERULOESCLEROSIS", "OSTEOMIELITIS", "SIALODENITIS",
        "COLANGITIS", "CISTITIS", "PERICARDITIS", "VASCULITIS", "TIROIDITIS",
        "DACRIOCISTITIS", "SINUSOPATIA", "SINOSOPATIA", "PROCESO INFLAMATORIO",
        "INFILTRADO INFLAMATORIO", "INFILTRACION INFLAMATORIO", "RESPUESTA INFLAMATORIA",
        "CELULARIDAD INFLAMATORIA", "ACTIVIDAD INFLAMATORIA", "CITOMEGALOVIRUS",
        "ESTEATOSIS", "MICROANGIOPATIA", "NECROSIS TUBULAR", "TEJIDO DE GRANULACION",
        "CRYPTOCOCCUS", "ESTRUCTURAS FUNGICAS", "PROCESO REPARATIVO", "REACCION REPARATIVA",
    ],
    "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)": [
        "NEGATIVO PARA LESION NEOPLASICA", "SIN EVIDENCIA DE LESION NEOPLASICA",
        "SIN COMPROMISO POR LESION", "NEGATIVO PARA ATIPIA", "SIN CELULAS DE ASPECTO NEOPLASICO",
        "SIN EVIDENCIA DE POBLACION NEOPLASICA", "NEGATIVO PARA POBLACION LINFOIDE",
        "NEGATIVO PARA PROLIFERACION", "SIN EVIDENCIA DE CAMBIOS DISPLASICOS",
        "NEGATIVO PARA CAMBIOS DISPLASICOS", "MUESTRA NEGATIVA PARA",
        "NEGATIVA PARA CAMBIOS DISPLASICOS", "ATROFIA", "SIN REPRESENTACION DE LESION",
        "METAPLASIA", "ENDOMETRIO EN FASE", "TEJIDO ENDOMETRIAL ECTOPICO",
        "NEGATIVO PARA ENFERMEDAD POR IGG4", "NEGATIVO PARA IGG4",
        "SIN HALLAZGOS DE ENFERMEDAD POR IGG4", "SIN HALLAZGOS QUE SUGIERAN ENFERMEDAD RELACIONADA CON IGG4",
        "CAMBIOS REACTIVOS", "CAMBIOS CELULARES REACTIVES", "ASPECTO REACTIVO",
        "TEJIDO ENCEFALICO SIN CAMBIOS", "NEGATIVOS PARA CMV", "NEGATIVO PARA MALIGNIDAD",
        "SIN EVIDENCIA DE MALIGNIDAD", "SIN ENVIDENCIA DE LESION", "SIN EVIDENCIA DE LESION",
        "APARIENCIA REACTIVA", "PROCESO REACTIVO HIPERPLASICO", "SIN ALTERACIONES",
    ],
    "MUESTRA INSUFICIENTE / NO CONCLUYENTE": [
        "MUESTRA LIMITADA", "MUESTRA MUY LIMITADA", "LIMITADA PARA DIAGNOSTICO",
        "LIMITADA PARA EVALUACION", "LIMITADA PARA VALORACION", "CALIDAD INSUFICIENTE",
        "DEFECTOS DE LA FASE PREANALITICA", "SUBOPTIMA", "MUESTRA INDEFINIDA",
        "INDEFINIDA PARA DISPLASIA", "MUESTRA EXAMINADA ES NEGATIVA",
    ],
    # V6.9.30: SARCOMA genérico (sin subtipo nombrado). Va DESPUÉS de los
    # sarcomas específicos (lipo/leiomio/osteo/rabdomio/sinovial) y de
    # CARCINOSARCOMA, así que "SARCOMA" a secas solo captura lo no
    # especificado. Antes caían en el cajón "...A CLASIFICAR (OTRO)".
    "SARCOMA (OTRO SUBTIPO)": [
        "SARCOMA", "RADOMIOSARCOMA", "NEOPLASIA FUSOCELULAR DE ALTO GRADO",
    ],
    # V6.9.30: Lesión acinar atípica de próstata (ASAP) — sospechosa de
    # carcinoma, sin diagnóstico definitivo. Entidad prostática reconocible.
    "LESION ACINAR ATIPICA DE PROSTATA (ASAP)": [
        "PROLIFERACION ACINAR ATIPICA", "ACINAR ATIPICA", "ASAP",
        "MICROACINARES ATIPICOS", "LESION NEOPLASICA ACINAR",
    ],
    # V6.9.30: renombrada (antes "...A CLASIFICAR (OTRO)") para no mostrar
    # "OTRO" al gerente. Quedan los malignos genuinamente sin tipo nombrado.
    "NEOPLASIA MALIGNA INDIFERENCIADA": [
        "TUMOR DEL ESTROMA",
        "TUMOR MALIGNO", "NEOPLASIA MALIGNA", "LESION NEOPLASICA MALIGNA",
        "NEOPLASIA DE CELULAS REDONDAS", "CELULA PEQUENA REDONDA Y AZUL",
        "CELULAS REDONDAS Y AZULES", "TUMOR INDIFERENCIADO", "FUSOCELULAR",
        "PROLIFERACION CELULAR ATIPICA", "NEOPLASIA DE ORIGEN EPITELIAL",
        "NEOPLASIA EN PATRON SOLIDO", "TUMOR DE ALTO GRADO",
        "TUMOR DE CELULAS DE LA GRANULOSA",
    ],
    "LESION INTRAEPITELIAL / DISPLASIA (NIC)": [
        "LESION INTRAEPITELIAL", "INTRAEPITELIAL DE BAJO GRADO",
        "INTRAEPITELIAL DE ALTO GRADO", "NEOPLASIA ESCAMOSA INTRAEPITELIAL",
        "NIC I", "NIC II", "NIC III", "DISPLASIA LEVE", "DISPLASIA MODERADA",
        "DISPLASIA SEVERA",
    ],
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)": [
        "VER DESCRIPCION", "VER COMENTARIO", "HER2", "HER 2", "HER-2",
        "RECEPTOR DE ESTROGENO", "RECEPTOR DE PROGESTERONA", "SCORE 0", "SCORE 1",
        "SCORE 2", "SCORE 3", "PATRON MICROSATELITAL", "MICROSATELITAL ESTABLE",
        "HALLAZGOS MORFOLOGICOS Y DE INMUNOHSITOQUIMICA",
        "LOS HALLAZGOS HISTOLOGICOS E INMUNOHISTOQUIMICOS", "LOS HALLAZGOS INMUNOHISTOQUIMICOS",
        "MUCOSA GASTRICA", "MUCOSA DE ESTOMAGO", "MUCOSA DE COLON", "MUCOSA DUODENAL",
        "GANGLIO LINFATICO", "GANGLIOS LINFATICOS", "ENDOSCOPICA",
        "ENDOSCOPIA", "COLONOSCOPIA", "SACABOCADO", "E-CADHERINA", "FOCUS SCORE",
        "LESION EN MAMA", "LEISON EN MAMA", "EXPRESION POSITIVA",
    ],

    # ===================================================================
    # V6.9.29: Entidades clínicas REALES recuperadas tras corregir el
    # over-stripping (Fix A). Añadidas AL FINAL (primer-match-gana) => SOLO
    # capturan casos que hoy caen en OTRO/NO CATEGORIZADO; CERO regresión
    # sobre las categorías ya existentes. Todas son neoplasias (van al
    # bucket "Diagnósticos oncológicos" de cobertura).
    # IMPORTANTE: patrones diseñados para NO capturar negativos (ej. la
    # categoría de Langerhans EXIGE "HISTIOCITOSIS" para no robar el
    # "NEGATIVO PARA INFILTRACION DE CELULAS DE LANGERHANS").
    # ===================================================================
    "TUMOR DE WILMS / NEFROBLASTOMA": [
        "TUMOR DE WILMS", "NEFROBLASTOMA", "WILMS",
    ],
    "TUMOR PINEAL": [
        "PINEOBLASTOMA", "PINEOCITOMA", "TUMOR DE LA GLANDULA PINEAL",
        "TUMOR PINEAL", "GLANDULA PINEAL", "REGION PINEAL", "PARENQUIMA PINEAL",
    ],
    "NEUROBLASTOMA / TUMOR NEUROBLASTICO": [
        "NEUROBLASTOMA", "ESTESIONEUROBLASTOMA", "ESTHESIONEUROBLASTOMA",
        "GANGLIONEUROBLASTOMA",
    ],
    "HISTIOCITOSIS DE CELULAS DE LANGERHANS": [
        "HISTIOCITOSIS DE CELULAS DE LANGERHANS", "HISTIOCITOSIS DE LANGERHANS",
        "HISTIOCITOSIS X",
    ],
    "ENFERMEDAD DE PAGET (MAMA/PIEL)": [
        "ENFERMEDAD DE PAGET", "PAGET DEL PEZON", "PAGET MAMARIO",
    ],
    "TUMOR DE CELULAS DE LEYDIG / SERTOLI": [
        "CELULAS DE LEYDIG", "TUMOR DE LEYDIG", "HILIO OVARICO",
        "CELULAS DE SERTOLI", "SERTOLI-LEYDIG", "FIBROTECOMA", "TECOMA OVARICO",
    ],
    "TUMOR DE MUSCULO LISO (POTENCIAL INCIERTO)": [
        "MUSCULO LISO DE POTENCIAL", "POTENCIAL MALIGNO INCIERTO",
        "POTENCIAL DE MALIGNIDAD INCIERTO", "STUMP",
    ],
    "NEOPLASIA SUPRARRENAL / CORTICOSUPRARRENAL": [
        "CORTEZA SUPRARRENAL", "CORTICOSUPRARRENAL", "ORIGEN SUPRARRENAL",
        "FEOCROMOCITOMA", "ADENOMA SUPRARRENAL", "CARCINOMA SUPRARRENAL",
        "NEOPLASIA SUPRARRENAL",
    ],
    # V6.9.39: tumores/lesiones VÁLIDOS que caían en "SIN DIAGNOSTICO" por falta
    # de categoría. Añadidos AL FINAL (primer-match-gana) => SOLO capturan casos
    # que hoy caen en el fallback; cero regresión sobre las categorías de arriba.
    "TUMOR BENIGNO DE NERVIO PERIFERICO": [
        "NEUROMA", "NEUROTEQUEOMA", "NEUROFIBROMA", "PERINEURIOMA", "SCHAWNNOMA",
    ],
    "TUMOR DE CELULAS GERMINALES (GERMINOMA)": [
        "GERMINOMA",
    ],
    "ADENOMA PLEOMORFICO (GLANDULA SALIVAL)": [
        "ADENOMA PLEOMORFICO", "TUMOR MIXTO BENIGNO DE GLANDULA SALIVAL",
    ],
    "LESION OSEA / DISPLASIA FIBROSA": [
        "DISPLASIA FIBROSA",
    ],
    "LESION VASCULAR BENIGNA": [
        "HEMANGIOMA", "LINFANGIOMA", "MALFORMACION VASCULAR", "LINFANGIOHEMANGIOMA",
    ],
    "PATOLOGIA TIROIDEA BENIGNA (BOCIO)": [
        "BOCIO", "ENFERMEDAD NODULAR FOLICULAR TIROIDEA",
    ],
    # V6.9.40: hallazgos/tejidos no-tumorales y proliferaciones a clasificar que
    # quedaban en SIN DIAGNOSTICO. Son dx/hallazgos REALES (no fragmentos).
    "TEJIDO NORMAL / SIN ALTERACIONES SIGNIFICATIVAS": [
        "HISTOARQUITECTURA USUAL", "ARQUITECTURA HISTOLOGICA USUAL",
        "CONSERVACION DE SU MORFOLOGIA", "CONSERVACION DE LA MORFOLOGIA",
    ],
    "BIOPSIA RENAL / EVALUACION DE INJERTO": [
        "INJERTO RENAL", "LESION TUBULAR AGUDA", "TUBULAR AGUDA MULTIFOCAL",
    ],
    "MEDULA OSEA / EVALUACION HEMATOLOGICA": [
        "MEDULA OSEA", "TRES LINEAS CELULARES", "LINEAS CELULARES CON PREDOMINIO",
        "CELULARIDAD LINFOIDE ABERRANTE", "INMUNOFENOTIPO ABERRANTE",
        "POBLACION DE CELULAS PLASMATICAS", "AUMENTO DE CELULAS PLASMATICAS",
        "CELULAS PLASMATICAS DE INMUNOFENOTIPO",
    ],
    "PROLIFERACION ATIPICA / A CLASIFICAR": [
        "PROLIFERACION ACINAR", "PROLIFERACION GLANDULAR", "PROLIFERACION VASCULAR",
        "LESION BIFASICA", "NODULO FIBROMUSCULAR", "CAMBIOS CITOLOGICOS INESPECIFICOS",
        "LINFANGIOHEMANGIOMA", "NECROSIS GRASA", "LECHO ULCEROSO",
        "INFLAMACION CRONICA CON PREDOMINIO", "MALFORMACION VASCULAR",
    ],
    # V6.9.41: tejido linfoide reactivo y hallazgos de mucosa que quedaban en SIN.
    "TEJIDO LINFOIDE REACTIVO / NORMAL": [
        "INMUNOPERFIL ESPERADO EN TEJIDO LINFOIDE", "TEJIDO LINFOIDE DE ARQUITECTURA",
        "TEJIDO LINFOIDE REACTIVO", "HIPERPLASIA LINFOIDE REACTIVA",
        "INMUNOPERFIL ESPERADO EN TEJIDO LINFATICO",
    ],
    "MUCOSA DUODENAL / LINFOCITOS INTRAEPITELIALES": [
        "LINFOCITOS INTRAEPITELIALES",
    ],
    "LESION DEL SISTEMA NERVIOSO / GLIAL": [
        "LESION GLIAL", "PROCESO GLIAL", "NEOPLASIA GLIAL", "TUMOR GLIAL",
        "ASTROCITOMA", "ASTROCITARIA", "GLIOSIS",
    ],
    "PATOLOGIA RENAL MEDICA (NO ONCOLOGICA)": [
        "NEFRITIS", "NEFROPATIA", "TUBULOINTERSTICIAL", "GLOMERULONEFRITIS",
        "NEFRITIS INTERSTICIAL",
    ],
    # V6.9.41: razones VÁLIDAS (extraídas del propio informe) por las que un caso
    # no trae dx tumoral. NO son errores de extracción -> aclaran el estado real.
    "ESTUDIO EN CURSO / PENDIENTE (INFORME POSTERIOR)": [
        "ESTUDIO COMPLEMENTARIO EN CURSO", "EN CURSO (INFORME POSTERIOR)",
        "PENDIENTE INFORME POSTERIOR", "RESULTADO EN INFORME POSTERIOR",
        "BIOMARCADORES EN INFORME POSTERIOR",
    ],
}


# El orden importa: las llaves de dict en Python 3.7+ se preservan, así
# que se evalúan en el orden definido arriba (de más específico a más
# genérico).
ORDEN_EVALUACION: list[str] = list(CATEGORIAS_DIAGNOSTICO.keys())


# ===================================================================
# V6.9.49 — CATÁLOGO CANÓNICO de categorías NO oncológicas (no neoplásicas / sin tumor
# clasificado). FUENTE ÚNICA DE VERDAD: los consumidores (p.ej. el informe estadístico)
# deben IMPORTAR esto en vez de mantener su propia lista, para no desincronizarse y
# terminar contando hallazgos no-neoplásicos (inflamación, tejido reactivo/normal,
# evaluaciones médicas, médula ósea, muestras no concluyentes…) como TUMORES.
# Si se agrega una categoría NO-neoplásica a CATEGORIAS_DIAGNOSTICO, agrégala AQUÍ también.
# (Las categorías dudosas —lesión benigna/hiperplasia, displasias/NIC, etc.— quedan FUERA
#  de este set, es decir cuentan como neoplásicas, hasta decisión clínica.)
# ===================================================================
CATEGORIAS_NO_ONCOLOGICAS: frozenset = frozenset({
    # Negativos / normales / reactivos / inflamatorios / infecciosos
    "NEGATIVO PARA MALIGNIDAD",
    "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO",
    "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)",
    "TEJIDO NORMAL / SIN ALTERACIONES SIGNIFICATIVAS",
    "TEJIDO LINFOIDE REACTIVO / NORMAL",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)",
    "INFLAMACION / PROCESO INFECCIOSO",
    "GLIOSIS / LESION REACTIVA SNC",
    "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
    # Médula ósea (morfología / evaluación / reactiva)
    "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)",
    "MEDULA OSEA / EVALUACION HEMATOLOGICA",
    "MEDULA OSEA REACTIVA / NORMAL",
    # Evaluaciones médicas NO oncológicas
    "RECHAZO DE TRASPLANTE",
    "BIOPSIA RENAL / EVALUACION DE INJERTO",
    "PATOLOGIA RENAL MEDICA (NO ONCOLOGICA)",
    "MUCOSA DUODENAL / LINFOCITOS INTRAEPITELIALES",
    "PATOLOGIA TIROIDEA BENIGNA (BOCIO)",
    # Estudios IHQ de marcadores sin tumor clasificado
    "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)",
    "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)",
    # Muestra insuficiente / sin diagnóstico / pendiente
    "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA",
    "MUESTRA INSUFICIENTE / NO CONCLUYENTE",
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)",
    "ESTUDIO EN CURSO / PENDIENTE (INFORME POSTERIOR)",
})


# ===================================================================
# V6.9.29 — FALLBACK FINAL: garantiza CERO "OTRO / NO CATEGORIZADO".
# Cuando ningún patrón explícito matchea, todo texto NO vacío se enruta a
# un bucket clínico con sentido según palabras clave amplias. Esto SOLO se
# ejecuta para casos que hoy caían en "OTRO / NO CATEGORIZADO" (los que
# matchean un patrón retornan antes) => cero regresión por construcción.
#
# Orden de prioridad (importa):
#   1) MUESTRA inadecuada / no concluyente  -> "Estudios sin dx específico"
#   2) BENIGNO / negativo / inflamatorio     -> "Hallazgos no-neoplásicos"
#   3) ENTIDAD neoplásica (tumor, atipia...)  -> "Diagnósticos oncológicos"
#   4) Fragmento sin entidad reconocible      -> "Texto a revisar (extracción)"
# El benigno se evalúa ANTES que neoplasia para que un "NEGATIVO PARA
# NEOPLASIA" o "LESION PAPILAR SIN ATIPIA" no se marque como tumor.
# ===================================================================
_FB_MUESTRA: tuple[str, ...] = (
    "INADECUADA PARA EVALUACION", "NO ADECUADA PARA EVALUACION",
    "MENOS DE 10 ESPACIOS PORTA", "ESPACIOS PORTA EVALUABLES",
    "NO CONCLUYENTE", "NO ES CONCLUYENTE", "MUESTRA NO CONCLUYENTE",
    "INDEFINID", "NO REPRESENTAT", "MATERIAL INSUFICIENTE", "MUESTRA LIMITADA",
)
_FB_BENIGNO: tuple[str, ...] = (
    "NEGATIV",  # negativo / negativa / negativos para...
    "SIN EVIDENCIA", "SIN COMPROMISO", "SIN ATIPIA", "SIN INCREMENTO",
    "SIN PERDIDA", "SIN ALTERACIONES", "SIN INMUNOFENOTIPO",
    "AUSENCIA", "REACTIV", "BENIGN", "HIPERPLASIA",
    "INFLAMATORI", "INFLAMACION", "ITIS",  # hepatitis, miositis, sialoadenitis, colitis...
    "MIOPATIA", "NEUMONIA", "FIBROSIS", "FIBROREPARATIV", "REPARATIV",
    "NORMOCELULAR", "MEGACARIOCITO", "APLASIA", "ULCERACION",
    "MALACOPLAQUIA", "NODULAR TIROIDEA", "ECTOPIC", "DEGRANULACION",
    "FIBRINOPURULENTA", "PURULENTA", "COLESTASIS", "INJURIA TUBULAR",
    "CASTLEMAN", "ROSSAI", "ROSAI", "DERMATOPATICA", "IGG4",
    "GRANULACION", "ENFERMEDAD INFLAMATORIA INTESTINAL", "COLITIS",
    "XANTOMA",
)
_FB_NEOPLASIA: tuple[str, ...] = (
    "TUMOR", "NEOPLASIA", "CARCINOMA", "ADENOCARCINOMA", "SARCOMA",
    "LINFOMA", "LEUCEMIA", "MELANOMA", "MIELOMA", "BLASTOMA", "GLIOMA",
    "PAGET", "WILMS", "LANGERHANS", "LEYDIG", "MELANOCITOMA", "MELANOCITICA",
    "SCHWANNOMA", "SCHAWANNOMA",  # incl. typo del patólogo (MPNST)
    "ORIGEN EPITELIAL", "PERFIL ESCAMOSO", "MALIGNAS DE ORIGEN",
    "QUERATOSIS", "DISPLASICOS DE ALTO GRADO", "DISPLASIA DE ALTO GRADO",
    "ATIPIA SEVERA", "ATIPIA ARQUITECTURAL", "ATIPIA LEVE",
    "LESION PAPILAR", "PROLIFERACION PAPILAR", "NEOPLASIA PAPILAR",
    "LESION TIROIDEA", "INVASIV", "INFILTRANTE", "POTENCIAL MALIGNO",
)


def _fallback_categoria(t: str) -> str:
    """Enruta texto no reconocido a un bucket clínico (nunca 'OTRO')."""
    if any(k in t for k in _FB_MUESTRA):
        return "MUESTRA INSUFICIENTE / NO CONCLUYENTE"
    if any(k in t for k in _FB_BENIGNO):
        return "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)"
    if any(k in t for k in _FB_NEOPLASIA):
        return "NEOPLASIA MALIGNA INDIFERENCIADA"
    return "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)"


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

    # V6.6.14 FIX: Stripear preámbulos del patólogo ANTES del matching.
    # NO modifica el dato original en BD — solo opera sobre la copia
    # local `t` para que el matching encuentre la entidad clínica
    # debajo del preámbulo. Recupera ~13 casos donde el dx oncológico
    # real estaba escondido tras frases como "PERFIL DE INMUNOHISTOQUIMICA
    # COMPATIBLE CON CARCINOMA UROTELIAL".
    t = stripear_preambulos(t)

    for categoria in ORDEN_EVALUACION:
        for patron in CATEGORIAS_DIAGNOSTICO[categoria]:
            if patron in t:
                return categoria

    # V6.9.29: ya no devolvemos "OTRO / NO CATEGORIZADO" — el fallback
    # enruta TODO texto no vacío a un bucket clínico con sentido.
    return _fallback_categoria(t)


# Mapeo de inferencia órgano → categoría refinada cuando el dx es genérico
# V6.6.8: Para casos donde el patólogo escribió un dx genérico ("ADENOCARCINOMA
# INVASIVO" sin especificar origen), inferir la categoría usando el órgano.
# Solo se aplica para 3 categorías genéricas:
#   - "ADENOCARCINOMA (OTRAS LOCALIZACIONES)"
#   - "CARCINOMA (OTRAS LOCALIZACIONES)"
#   - "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)"
INFERENCIA_POR_ORGANO_ADENO = {
    # ADENOCARCINOMA + órgano → categoría específica
    "COLON": "ADENOCARCINOMA COLORRECTAL",
    "RECTO": "ADENOCARCINOMA COLORRECTAL",
    # V6.6.14 FIX IHQ250159: el normalizador de órganos devuelve a veces
    # "TUMOR MUCOSA RECTAL" como literal (variante adjetiva). El patrón
    # "RECTO" no matchea "RECTAL" como substring (RECTO termina en O,
    # RECTAL en AL). Agregar "RECTAL" como ancla independiente.
    "RECTAL": "ADENOCARCINOMA COLORRECTAL",
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
    "MAMA": "CARCINOMA DE MAMA (SIN SUBTIPO ESPECIFICADO)",
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
    # V6.6.16: Órganos adicionales detectados como CARCINOMA ESCAMOCELULAR
    # (OTRO) en producción que pueden refinarse por contexto anatómico.
    "LABIO": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "BOCA": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "FARINGE": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "HIPOFARINGE": "CARCINOMA ESCAMOCELULAR DE CABEZA Y CUELLO",
    "NASOFARINGE": "CARCINOMA NASOFARINGEO",
    "ESOFAGO": "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)",
    "ANO": "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)",
    "VULVA": "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)",
    "VAGINA": "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)",
}

# V6.9.43: subtipos histológicos de carcinoma de mama (entidades OMS distintas).
# Solo se aplican cuando el ÓRGANO es MAMA -> NO capturan papilar de tiroides,
# mucinoso de colon/ovario, medular de tiroides, etc. (esos tienen otro órgano).
# El orden importa: MICROPAPILAR antes que PAPILAR (substring).
_SUBTIPOS_MAMA = {
    "MICROPAPILAR": "CARCINOMA MICROPAPILAR DE MAMA",
    "PAPILAR": "CARCINOMA PAPILAR DE MAMA",
    "MUCINOSO": "CARCINOMA MUCINOSO DE MAMA",
    "COLOIDE": "CARCINOMA MUCINOSO DE MAMA",
    "MEDULAR": "CARCINOMA MEDULAR DE MAMA",
    "APOCRINO": "CARCINOMA APOCRINO DE MAMA",
    "TUBULAR": "CARCINOMA TUBULAR DE MAMA",
    "METAPLASIC": "CARCINOMA METAPLASICO DE MAMA",
    "CRIBIFORME": "CARCINOMA CRIBIFORME DE MAMA",
    "SECRETOR": "CARCINOMA SECRETOR DE MAMA",
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
        "ADENOCARCINOMA (OTRAS LOCALIZACIONES)",
        "CARCINOMA (OTRAS LOCALIZACIONES)",
        "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)",
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

    # V6.9.43: subtipos histológicos de MAMA (papilar, mucinoso, medular, apocrino...)
    # -> su categoría específica. Solo con órgano MAMA -> no afecta papilar de
    # tiroides, mucinoso de colon, etc. (esos tienen otro órgano).
    if "MAMA" in organo_norm:
        # V6.9.44: en mama, "tipo no especial" (NST) = "NOS" = "ductal" = "sin
        # subtipo especial" son SINÓNIMOS del carcinoma ductal infiltrante (OMS,
        # ~80% de los carcinomas de mama). Solo con órgano=mama -> seguro: NO
        # afecta "adenocarcinoma ductal pancreático" ni "escamocelular NOS de
        # cérvix" (tienen otro órgano y aquí solo entran dx genéricos de mama).
        if (any(k in dx_norm for k in (
                "TIPO NO ESPECIAL", "SIN TIPO ESPECIAL", "SIN SUBTIPO",
                "DUCTAL", " NST"))
                or re.search(r"\bNOS\b", dx_norm)):
            return "CARCINOMA DUCTAL DE MAMA"
        for _kw, _cat_mama in _SUBTIPOS_MAMA.items():
            if _kw in dx_norm:
                return _cat_mama

    # Adenocarcinoma genérico → buscar inferencia
    if base in ("ADENOCARCINOMA (OTRAS LOCALIZACIONES)", "CARCINOMA (OTRAS LOCALIZACIONES)"):
        for organo_key, categoria_refinada in INFERENCIA_POR_ORGANO_ADENO.items():
            if organo_key in organo_norm:
                return categoria_refinada

    # Carcinoma escamocelular genérico → buscar inferencia
    if base == "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)":
        for organo_key, categoria_refinada in INFERENCIA_POR_ORGANO_ESCAMO.items():
            if organo_key in organo_norm:
                return categoria_refinada

    return base


# --- self-test ----------------------------------------------------------
if __name__ == "__main__":
    casos = [
        ("CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL)", "CARCINOMA DUCTAL DE MAMA"),
        ("CARCINOMA DUCTAL INFILTRANTE GRADO 2", "CARCINOMA DUCTAL DE MAMA"),
        ("ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO", "ADENOCARCINOMA (OTRAS LOCALIZACIONES)"),
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
        ("CARCINOMA ESCAMOCELULAR INVASIVO", "CARCINOMA ESCAMOCELULAR (OTRAS LOCALIZACIONES)"),
        ("HEPATOCARCINOMA", "HEPATOCARCINOMA"),
        ("GIST DE BAJO GRADO", "GIST (TUMOR ESTROMAL GASTROINTESTINAL)"),
        ("NEGATIVO PARA MALIGNIDAD", "NEGATIVO PARA MALIGNIDAD"),
        ("NEGATIVO PARA NEOPLASIA", "NEGATIVO PARA MALIGNIDAD"),
        ("ESTUDIO DE INMUNOHISTOQUÍMICA", "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)"),
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
        ("EXPRESIÓN DE CD117 Y CD56 NEGATIVA", "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)"),
        ("SOBREEXPRESIÓN DE HER-2: EQUÍVOCO", "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)"),
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
        ("ADENOCARCINOMA MUCINOSO", "ADENOCARCINOMA (OTRAS LOCALIZACIONES)"),
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
