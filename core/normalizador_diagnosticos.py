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
    "LINFOMA HODGKIN": ["LINFOMA DE HODGKIN", "HODGKIN"],
    "LINFOMA NO HODGKIN B": [
        "LINFOMA NO HODGKIN", "LINFOMA B DIFUSO", "LINFOMA DIFUSO DE CELULAS B",
        "LINFOMA FOLICULAR", "LINFOMA DE LA ZONA MARGINAL", "LINFOMA MALT",
        "LINFOMA DE BURKITT", "LINFOMA DE CELULAS DEL MANTO",
        "LINFOMA LINFOCITICO", "LEUCEMIA LINFOCITICA CRONICA",
    ],
    "LINFOMA T/NK": [
        "LINFOMA T", "LINFOMA DE CELULAS T", "LINFOMA NK", "LINFOMA ANAPLASICO",
        "MICOSIS FUNGOIDE",
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
    "CARCINOMA DUCTAL DE MAMA": [
        "CARCINOMA INVASIVO DE TIPO NO ESPECIAL", "CARCINOMA DUCTAL INVASIVO",
        "CARCINOMA DUCTAL INFILTRANTE", "CARCINOMA INVASOR DE TIPO NO ESPECIAL",
        "CARCINOMA NST",
    ],
    "CARCINOMA LOBULILLAR DE MAMA": [
        "CARCINOMA LOBULILLAR", "CARCINOMA LOBULAR",
    ],
    "CARCINOMA IN SITU DE MAMA (DCIS/LCIS)": [
        "CARCINOMA DUCTAL IN SITU", "CARCINOMA LOBULILLAR IN SITU",
        "DCIS", "LCIS",
    ],
    "OTRO CARCINOMA DE MAMA": [
        "CARCINOMA MUCINOSO", "CARCINOMA MEDULAR", "CARCINOMA TUBULAR",
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
    ],
    "CARCINOMA DE ENDOMETRIO / UTERO": [
        "ADENOCARCINOMA ENDOMETRIAL", "CARCINOMA ENDOMETRIOIDE",
        "CARCINOMA SEROSO", "CARCINOMA DE ENDOMETRIO",
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
    ],

    # === Carcinomas escamosos en general ===
    "CARCINOMA ESCAMOCELULAR (OTRO/SIN ESPECIFICAR)": [
        "CARCINOMA ESCAMOCELULAR", "CARCINOMA EPIDERMOIDE",
        "CARCINOMA DE CELULAS ESCAMOSAS",
    ],

    # === Adenocarcinomas con origen identificable ===
    "ADENOCARCINOMA COLORRECTAL": [
        "ADENOCARCINOMA DE COLON", "ADENOCARCINOMA COLORRECTAL",
        "ADENOCARCINOMA DE RECTO", "ADENOCARCINOMA COLONICO",
    ],
    "ADENOCARCINOMA GASTRICO": [
        "ADENOCARCINOMA GASTRICO", "ADENOCARCINOMA DE ESTOMAGO",
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
