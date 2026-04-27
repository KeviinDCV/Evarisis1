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
        "CRANEO", "MANDIBULA", "MAXILAR INFERIOR", "ROTULA",
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
    "PERITONEO / EPIPLON",
    "RETROPERITONEO",
    "RIÑON",
    "VEJIGA / VIA URINARIA",
    "PROSTATA",
    "TESTICULO",
    "PENE",
    "TIROIDES",
    "PARATIROIDES",
    "GLANDULA SUPRARRENAL",
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
            if kw in limpio:
                return categoria

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
