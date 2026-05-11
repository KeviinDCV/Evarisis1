# -*- coding: utf-8 -*-
"""Configuración de columnas HUV para extracción IA.

Define las 184 columnas que la IA debe extraer de cada informe IHQ
(excluye 2 metadata del sistema: 'Estado Auditoria IA' y 'Fecha Ingreso
Base de Datos' que se llenan automáticamente).

Todas las columnas son string. Si la IA no encuentra un campo, debe
devolver "N/A" (literal).

Uso:
    from core.columnas_huv_ia import COLUMNAS_IA, build_json_schema, build_prompt_instructions
"""

# Lista completa de las 184 columnas que la IA extrae (en el orden de la BD).
# Las nombres preservan acentos y caracteres especiales del esquema original.
COLUMNAS_IA = [
    # === Identificación administrativa (19) ===
    "Numero de caso",
    "Hospitalizado",
    "Sede",
    "EPS",
    "Servicio",
    "Médico tratante",
    "Especialidad",
    "Datos Clinicos",
    "Tipo de documento",
    "N. de identificación",
    "Primer nombre",
    "Segundo nombre",
    "Primer apellido",
    "Segundo apellido",
    "Edad",
    "Genero",
    "Departamento",
    "Municipio",
    "CUPS",
    # === Procedimiento (7) ===
    "Tipo de examen",
    "Procedimiento",
    "Organo",
    "Fecha de toma (1. Fecha de la toma)",
    "Fecha de ingreso (2. Fecha de la muestra)",
    "Fecha Informe",
    "Patologo",
    # === Diagnóstico clínico (7) ===
    "Malignidad",
    "Descripcion macroscopica",
    "Descripcion microscopica",
    "Descripcion Diagnostico",
    "Diagnostico Coloracion",
    "Diagnostico Principal",
    "Factor pronostico",
    # === Estudios IHQ generales (5) ===
    "IHQ_ESTUDIOS_SOLICITADOS",
    "IHQ_ORGANO",
    "Congelaciones /Otros estudios",
    "Liquidos (5 Tipo histologico)",
    "Citometria de flujo (5 Tipo histologico)",
    # === Biomarcadores comunes (8) ===
    "IHQ_HER2",
    "IHQ_KI-67",
    "IHQ_RECEPTOR_ESTROGENOS",
    "IHQ_RECEPTOR_PROGESTERONA",
    "IHQ_PDL-1",
    "IHQ_P16_ESTADO",
    "IHQ_P16_PORCENTAJE",
    "IHQ_P40_ESTADO",
    # === Biomarcadores específicos (138) ===
    "IHQ_E_CADHERINA",
    "IHQ_CK7",
    "IHQ_MAMOGLOBINA",
    "IHQ_CROMOGRAMINA",
    "IHQ_DESMINA",
    "IHQ_LCA",
    "IHQ_CD11",
    "IHQ_MIOGENINA",
    "IHQ_MAMAGLOBINA",
    "IHQ_TIROGLOBULINA",
    "IHQ_CK34BETAE12",
    "IHQ_CK34BETA12",
    "IHQ_OCT4",
    "IHQ_PODOPLANINA",
    "IHQ_IDH",
    "IHQ_GPC3",
    "IHQ_AFP",
    "IHQ_IGD",
    "IHQ_BETACATENINA",
    "IHQ_ACTINA_MUSCULO_ESPECIFICA",
    "IHQ_MIELOPEROXIDASA",
    "IHQ_CD7",
    "IHQ_HCG",
    "IHQ_ACTINA_MUSCULO_LISO",
    "IHQ_EBER",
    "IHQ_CALRRETININA",
    "IHQ_SINAPTOFISINA",
    "IHQ_CROMOGRANINA",
    "IHQ_CK56",
    "IHQ_CAM5",
    "IHQ_GLICOFORINA",
    "IHQ_TDT",
    "IHQ_ATRX",
    "IHQ_IDH1",
    "IHQ_CMYC",
    "IHQ_IGG4",
    "IHQ_IGG",
    "IHQ_HEPATOCITO",
    "IHQ_PSA",
    "IHQ_RCC",
    "IHQ_CK19",
    "IHQ_CK20",
    "IHQ_CDX2",
    "IHQ_EMA",
    "IHQ_GATA3",
    "IHQ_SOX10",
    "IHQ_SOX11",
    "IHQ_P53",
    "IHQ_TTF1",
    "IHQ_S100",
    "IHQ_VIMENTINA",
    "IHQ_MELAN_A",
    "IHQ_CD2",
    "IHQ_CD3",
    "IHQ_CD5",
    "IHQ_CD10",
    "IHQ_CD20",
    "IHQ_CD30",
    "IHQ_CD34",
    "IHQ_CD38",
    "IHQ_CD45",
    "IHQ_CD56",
    "IHQ_CD61",
    "IHQ_CD68",
    "IHQ_CD117",
    "IHQ_CD138",
    "IHQ_KAPPA",
    "IHQ_LAMBDA",
    "IHQ_CICLINA_D1",
    "IHQ_PAX8",
    "IHQ_PAX5",
    "IHQ_WT1",
    "IHQ_NAPSIN",
    "IHQ_P63",
    "IHQ_CALPONINA",
    "IHQ_CDK4",
    "IHQ_MDM2",
    "IHQ_MLH1",
    "IHQ_MSH2",
    "IHQ_MSH6",
    "IHQ_PMS2",
    "IHQ_DOG1",
    "IHQ_HHV8",
    "IHQ_ACTIN",
    "IHQ_GFAP",
    "IHQ_CKAE1AE3",
    "IHQ_NEUN",
    "IHQ_CD15",
    "IHQ_CD79A",
    "IHQ_ALK",
    "IHQ_DESMIN",
    "IHQ_MYOGENIN",
    "IHQ_MYOD1",
    "IHQ_SMA",
    "IHQ_MSA",
    "IHQ_CALRETININ",
    "IHQ_CD31",
    "IHQ_FACTOR_VIII",
    "IHQ_BCL2",
    "IHQ_BCL6",
    "IHQ_MUM1",
    "IHQ_MUC1",
    "IHQ_MUC2",
    "IHQ_HMB45",
    "IHQ_TYROSINASE",
    "IHQ_MELANOMA",
    "IHQ_BER_EP4",
    "IHQ_H_CALDESMON",
    "IHQ_AML",
    "IHQ_PROLACTINA",
    "IHQ_ACTH",
    "IHQ_GH",
    "IHQ_FSH",
    "IHQ_LH",
    "IHQ_TSH",
    "IHQ_INHIBINA",
    "IHQ_CD23",
    "IHQ_CD4",
    "IHQ_CD8",
    "IHQ_CD99",
    "IHQ_CD1A",
    "IHQ_C4D",
    "IHQ_LMP1",
    "IHQ_CITOMEGALOVIRUS",
    "IHQ_SV40",
    "IHQ_CEA",
    "IHQ_CA19_9",
    "IHQ_CALRETININA",
    "IHQ_CK34BE12",
    "IHQ_CK5_6",
    "IHQ_HEPAR",
    "IHQ_GLIPICAN",
    "IHQ_ARGINASA",
    "IHQ_RACEMASA",
    "IHQ_34BETA",
    "IHQ_B2",
    "IHQ_SALL4",
    "IHQ_ALK1",
]

# Alias compatibles con SQL: el JSON schema necesita keys que el LLM
# pueda escribir limpio (sin acentos ni espacios). Usamos snake_case ASCII
# y mapeamos al nombre real de la BD al guardar.
def _alias_para_llm(col_name: str) -> str:
    """Convierte nombre de columna BD → key segura para JSON del LLM."""
    import re
    s = col_name
    # Normalizar acentos
    s = (s.replace("á", "a").replace("é", "e").replace("í", "i")
           .replace("ó", "o").replace("ú", "u").replace("ñ", "n")
           .replace("Á", "A").replace("É", "E").replace("Í", "I")
           .replace("Ó", "O").replace("Ú", "U").replace("Ñ", "N"))
    # Reemplazar caracteres no alfanuméricos por _
    s = re.sub(r"[^a-zA-Z0-9_]+", "_", s)
    # Compactar múltiples _
    s = re.sub(r"_+", "_", s).strip("_")
    return s.lower()


# Diccionario alias_llm → columna_BD (orden preservado de COLUMNAS_IA)
ALIAS_TO_COLUMN = {_alias_para_llm(c): c for c in COLUMNAS_IA}

# Diccionario inverso columna_BD → alias_llm
COLUMN_TO_ALIAS = {c: a for a, c in ALIAS_TO_COLUMN.items()}


# === PLAN B: schemas divididos en 2 pasadas (V6.8.0) ===
# qwen 27B con schema de 184 campos saturó en pruebas (timeout 10+ min).
# Solución: dividir en 2 schemas más manejables.

# Pasada 1 — 46 campos críticos (siempre se piden, ~13-20s/IHQ)
COLUMNAS_PASADA_1 = COLUMNAS_IA[:46]

# Pasada 2 — 138 biomarcadores específicos (solo se piden los que el OCR
# menciona; si OCR no menciona ninguno → se saltea esta pasada)
COLUMNAS_PASADA_2 = COLUMNAS_IA[46:]


def build_json_schema() -> dict:
    """Construye el JSON schema para forzar al LLM a devolver TODAS las
    184 columnas en cada respuesta. Cada campo es string (con default "N/A"
    instruido en el prompt).

    Returns:
        Dict listo para usar como `json_schema` argument en LMStudioClient.
    """
    properties = {alias: {"type": "string"} for alias in ALIAS_TO_COLUMN}
    required = list(ALIAS_TO_COLUMN.keys())
    return {
        "name": "extraccion_ihq_completa",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "diagnosticos": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": properties,
                        "required": required,
                    },
                }
            },
            "required": ["diagnosticos"],
        },
    }


def build_json_schema_pasada_1() -> dict:
    """Schema para PASADA 1 (46 campos críticos: admin + dx + biomarcadores
    comunes). Versión chica/rápida para cumplir tiempos viables."""
    cols = COLUMNAS_PASADA_1
    properties = {COLUMN_TO_ALIAS[c]: {"type": "string"} for c in cols}
    required = [COLUMN_TO_ALIAS[c] for c in cols]
    return {
        "name": "extraccion_ihq_critica",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "diagnosticos": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": properties,
                        "required": required,
                    },
                }
            },
            "required": ["diagnosticos"],
        },
    }


def build_json_schema_pasada_2(biomarcadores_detectados: list) -> dict:
    """Schema dinámico para PASADA 2: solo los biomarcadores que el OCR
    menciona. Si la lista viene vacía, no se hace pasada 2.

    Args:
        biomarcadores_detectados: lista de nombres BD, ej:
            ['IHQ_HER2', 'IHQ_KI-67', 'IHQ_CD20']
    """
    if not biomarcadores_detectados:
        return None
    # Solo aliases que existan en nuestro mapeo
    aliases = []
    for col in biomarcadores_detectados:
        if col in COLUMN_TO_ALIAS:
            aliases.append(COLUMN_TO_ALIAS[col])
    if not aliases:
        return None

    properties = {a: {"type": "string"} for a in aliases}
    return {
        "name": "extraccion_biomarcadores",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "biomarcadores": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": properties,
                        "required": aliases,
                    },
                }
            },
            "required": ["biomarcadores"],
        },
    }


# === Detector de biomarcadores en OCR ===
# Mapea biomarcador BD → lista de patrones regex que reconocen su mención
# en el OCR. Si alguno hace match, se le pide al LLM en pasada 2.
import re as _re_detect

_BIOMARCADOR_PATTERNS = {
    # Biomarcadores específicos (138 — todos los de PASADA 2)
    "IHQ_E_CADHERINA":          [r"\bE-?CADHERINA\b"],
    "IHQ_CK7":                  [r"\bCK[-\s]?7\b", r"\bCITOQUERATINA\s*7\b"],
    "IHQ_MAMOGLOBINA":          [r"\bMAMOGLOBINA\b"],
    "IHQ_CROMOGRAMINA":         [r"\bCROMOGRAMINA\b"],
    "IHQ_DESMINA":              [r"\bDESMINA\b"],
    "IHQ_LCA":                  [r"\bLCA\b"],
    "IHQ_CD11":                 [r"\bCD\s*11\b"],
    "IHQ_MIOGENINA":            [r"\bMIOGENINA\b"],
    "IHQ_MAMAGLOBINA":          [r"\bMAMAGLOBINA\b"],
    "IHQ_TIROGLOBULINA":        [r"\bTIROGLOBULINA\b"],
    "IHQ_CK34BETAE12":          [r"\bCK\s*34\s*BETA\s*E\s*12\b", r"\bCK34BE\s?12\b"],
    "IHQ_CK34BETA12":           [r"\bCK\s*34\s*BETA\s*12\b"],
    "IHQ_OCT4":                 [r"\bOCT[-\s]?4\b"],
    "IHQ_PODOPLANINA":          [r"\bPODOPLANINA\b", r"\bD2-?40\b"],
    "IHQ_IDH":                  [r"\bIDH\b(?!\s*1)"],
    "IHQ_GPC3":                 [r"\bGPC[-\s]?3\b", r"\bGLIPICAN[-\s]?3\b"],
    "IHQ_AFP":                  [r"\bAFP\b", r"\bALFAFETOPROTE[ÍI]NA\b"],
    "IHQ_IGD":                  [r"\bIGD\b", r"\bINMUNOGLOBULINA\s*D\b"],
    "IHQ_BETACATENINA":         [r"\bBETA[-\s]?CATENINA\b", r"\bß[-\s]?CATENINA\b"],
    "IHQ_ACTINA_MUSCULO_ESPECIFICA": [r"\bACTINA\s+M[ÚU]SCULO\s+ESPEC[IÍ]FICA\b", r"\bMSA\b"],
    "IHQ_MIELOPEROXIDASA":      [r"\bMIELOPEROXIDASA\b", r"\bMPO\b"],
    "IHQ_CD7":                  [r"\bCD\s*7\b"],
    "IHQ_HCG":                  [r"\bHCG\b", r"\bß[-\s]?HCG\b"],
    "IHQ_ACTINA_MUSCULO_LISO":  [r"\bACTINA\s+M[ÚU]SCULO\s+LISO\b", r"\bSMA\b", r"\bACTINA\s+ML\b"],
    "IHQ_EBER":                 [r"\bEBER\b"],
    "IHQ_CALRRETININA":         [r"\bCALRR?ETININA\b"],
    "IHQ_SINAPTOFISINA":        [r"\bSINAPTOFISINA\b", r"\bSYNAPTOPHYSIN\b"],
    "IHQ_CROMOGRANINA":         [r"\bCROMOGRANINA\b"],
    "IHQ_CK56":                 [r"\bCK\s*5[/]?6\b"],
    "IHQ_CAM5":                 [r"\bCAM\s*5\.?2\b"],
    "IHQ_GLICOFORINA":          [r"\bGLICOFORINA\b"],
    "IHQ_TDT":                  [r"\bTDT\b", r"\bTERMINAL\s+DEOXY"],
    "IHQ_ATRX":                 [r"\bATRX\b"],
    "IHQ_IDH1":                 [r"\bIDH[-\s]?1\b"],
    "IHQ_CMYC":                 [r"\bC[-\s]?MYC\b", r"\bMYC\b"],
    "IHQ_IGG4":                 [r"\bIGG[-\s]?4\b"],
    "IHQ_IGG":                  [r"\bIGG\b(?!4)"],
    "IHQ_HEPATOCITO":           [r"\bHEPATOCITO\b", r"\bHEP\s*PAR\b"],
    "IHQ_PSA":                  [r"\bPSA\b"],
    "IHQ_RCC":                  [r"\bRCC\b", r"\bRENAL\s+CELL\s+CARCINOMA\b"],
    "IHQ_CK19":                 [r"\bCK[-\s]?19\b"],
    "IHQ_CK20":                 [r"\bCK[-\s]?20\b"],
    "IHQ_CDX2":                 [r"\bCDX[-\s]?2\b"],
    "IHQ_EMA":                  [r"\bEMA\b"],
    "IHQ_GATA3":                [r"\bGATA[-\s]?3\b"],
    "IHQ_SOX10":                [r"\bSOX[-\s]?10\b"],
    "IHQ_SOX11":                [r"\bSOX[-\s]?11\b"],
    "IHQ_P53":                  [r"\bP\s*53\b"],
    "IHQ_TTF1":                 [r"\bTTF[-\s]?1\b"],
    "IHQ_S100":                 [r"\bS[-\s]?100\b"],
    "IHQ_VIMENTINA":            [r"\bVIMENTINA\b"],
    "IHQ_MELAN_A":              [r"\bMELAN[-\s]?A\b"],
    "IHQ_CD2":                  [r"\bCD\s*2\b"],
    "IHQ_CD3":                  [r"\bCD\s*3\b"],
    "IHQ_CD5":                  [r"\bCD\s*5\b"],
    "IHQ_CD10":                 [r"\bCD\s*10\b"],
    "IHQ_CD20":                 [r"\bCD\s*20\b"],
    "IHQ_CD30":                 [r"\bCD\s*30\b"],
    "IHQ_CD34":                 [r"\bCD\s*34\b"],
    "IHQ_CD38":                 [r"\bCD\s*38\b"],
    "IHQ_CD45":                 [r"\bCD\s*45\b"],
    "IHQ_CD56":                 [r"\bCD\s*56\b"],
    "IHQ_CD61":                 [r"\bCD\s*61\b"],
    "IHQ_CD68":                 [r"\bCD\s*68\b"],
    "IHQ_CD117":                [r"\bCD\s*117\b", r"\bC[-\s]?KIT\b"],
    "IHQ_CD138":                [r"\bCD\s*138\b"],
    "IHQ_KAPPA":                [r"\bKAPPA\b"],
    "IHQ_LAMBDA":               [r"\bLAMBDA\b"],
    "IHQ_CICLINA_D1":           [r"\bCICLINA\s+D1\b", r"\bCYCLIN\s+D1\b"],
    "IHQ_PAX8":                 [r"\bPAX[-\s]?8\b"],
    "IHQ_PAX5":                 [r"\bPAX[-\s]?5\b"],
    "IHQ_WT1":                  [r"\bWT[-\s]?1\b"],
    "IHQ_NAPSIN":               [r"\bNAPSIN\b"],
    "IHQ_P63":                  [r"\bP\s*63\b"],
    "IHQ_CALPONINA":            [r"\bCALPONINA\b"],
    "IHQ_CDK4":                 [r"\bCDK[-\s]?4\b"],
    "IHQ_MDM2":                 [r"\bMDM[-\s]?2\b"],
    "IHQ_MLH1":                 [r"\bMLH[-\s]?1\b"],
    "IHQ_MSH2":                 [r"\bMSH[-\s]?2\b"],
    "IHQ_MSH6":                 [r"\bMSH[-\s]?6\b"],
    "IHQ_PMS2":                 [r"\bPMS[-\s]?2\b"],
    "IHQ_DOG1":                 [r"\bDOG[-\s]?1\b"],
    "IHQ_HHV8":                 [r"\bHHV[-\s]?8\b"],
    "IHQ_ACTIN":                [r"\bACTIN\b"],
    "IHQ_GFAP":                 [r"\bGFAP\b"],
    "IHQ_CKAE1AE3":             [r"\bCK\s*AE1[/]?AE3\b", r"\bAE1[/]?AE3\b"],
    "IHQ_NEUN":                 [r"\bNEUN\b"],
    "IHQ_CD15":                 [r"\bCD\s*15\b"],
    "IHQ_CD79A":                [r"\bCD\s*79A?\b"],
    "IHQ_ALK":                  [r"\bALK\b(?!\s*1)"],
    "IHQ_DESMIN":               [r"\bDESMIN\b"],
    "IHQ_MYOGENIN":             [r"\bMYOGENIN\b"],
    "IHQ_MYOD1":                [r"\bMYOD[-\s]?1\b"],
    "IHQ_SMA":                  [r"\bSMA\b"],
    "IHQ_MSA":                  [r"\bMSA\b"],
    "IHQ_CALRETININ":           [r"\bCALRETININ\b"],
    "IHQ_CD31":                 [r"\bCD\s*31\b"],
    "IHQ_FACTOR_VIII":          [r"\bFACTOR\s+VIII\b"],
    "IHQ_BCL2":                 [r"\bBCL[-\s]?2\b"],
    "IHQ_BCL6":                 [r"\bBCL[-\s]?6\b"],
    "IHQ_MUM1":                 [r"\bMUM[-\s]?1\b"],
    "IHQ_MUC1":                 [r"\bMUC[-\s]?1\b"],
    "IHQ_MUC2":                 [r"\bMUC[-\s]?2\b"],
    "IHQ_HMB45":                [r"\bHMB[-\s]?45\b"],
    "IHQ_TYROSINASE":           [r"\bTYROSINASE\b", r"\bTIROSINASA\b"],
    "IHQ_MELANOMA":             [r"\bMELANOMA\b"],  # marker, no la entidad
    "IHQ_BER_EP4":              [r"\bBER[-\s]?EP[-\s]?4\b"],
    "IHQ_H_CALDESMON":          [r"\bH[-\s]?CALDESMON\b"],
    "IHQ_AML":                  [r"\bAML\b"],
    "IHQ_PROLACTINA":           [r"\bPROLACTINA\b"],
    "IHQ_ACTH":                 [r"\bACTH\b"],
    "IHQ_GH":                   [r"\bGH\b(?!\s*-?[34])"],
    "IHQ_FSH":                  [r"\bFSH\b"],
    "IHQ_LH":                   [r"\bLH\b"],
    "IHQ_TSH":                  [r"\bTSH\b"],
    "IHQ_INHIBINA":             [r"\bINHIBINA\b"],
    "IHQ_CD23":                 [r"\bCD\s*23\b"],
    "IHQ_CD4":                  [r"\bCD\s*4\b"],
    "IHQ_CD8":                  [r"\bCD\s*8\b"],
    "IHQ_CD99":                 [r"\bCD\s*99\b"],
    "IHQ_CD1A":                 [r"\bCD\s*1A?\b"],
    "IHQ_C4D":                  [r"\bC4D\b"],
    "IHQ_LMP1":                 [r"\bLMP[-\s]?1\b"],
    "IHQ_CITOMEGALOVIRUS":      [r"\bCITOMEGALOVIRUS\b", r"\bCMV\b"],
    "IHQ_SV40":                 [r"\bSV[-\s]?40\b"],
    "IHQ_CEA":                  [r"\bCEA\b"],
    "IHQ_CA19_9":               [r"\bCA\s*19[-\s]?9\b"],
    "IHQ_CALRETININA":          [r"\bCALRETININA\b"],
    "IHQ_CK34BE12":             [r"\bCK\s*34\s*BE\s*12\b"],
    "IHQ_CK5_6":                [r"\bCK\s*5[/]?6\b"],
    "IHQ_HEPAR":                [r"\bHEP\s*PAR\b", r"\bHEPAR\b"],
    "IHQ_GLIPICAN":             [r"\bGLIPICAN\b"],
    "IHQ_ARGINASA":             [r"\bARGINASA\b"],
    "IHQ_RACEMASA":             [r"\bRACEMASA\b"],
    "IHQ_34BETA":               [r"\b34\s*BETA\b"],
    "IHQ_B2":                   [r"\bß2\b", r"\bBETA[-\s]?2\b"],
    "IHQ_SALL4":                [r"\bSALL[-\s]?4\b"],
    "IHQ_ALK1":                 [r"\bALK[-\s]?1\b"],
}
# Compilar patrones una vez (eficiencia)
_BIOMARCADOR_PATTERNS_COMPILED = {
    col: [_re_detect.compile(p, _re_detect.IGNORECASE) for p in patterns]
    for col, patterns in _BIOMARCADOR_PATTERNS.items()
}


def detectar_biomarcadores_en_ocr(ocr_texto: str) -> list:
    """Detecta qué biomarcadores específicos (PASADA 2) menciona el OCR.

    Args:
        ocr_texto: texto del informe IHQ.

    Returns:
        Lista de nombres BD (subset de COLUMNAS_PASADA_2) encontrados.
        Vacía si no detecta ninguno.
    """
    if not ocr_texto:
        return []
    encontrados = []
    for col, patterns in _BIOMARCADOR_PATTERNS_COMPILED.items():
        for pat in patterns:
            if pat.search(ocr_texto):
                encontrados.append(col)
                break  # un patrón positivo es suficiente
    return encontrados


def build_prompt_field_list() -> str:
    """Construye un bloque de texto con la lista de aliases agrupados por
    categoría, para incluir en el system prompt del LLM."""
    lines = []
    lines.append("CAMPOS A EXTRAER (alias_json → significado clínico):")
    lines.append("")
    lines.append("--- IDENTIFICACIÓN ADMINISTRATIVA ---")
    for col in COLUMNAS_IA[0:19]:
        lines.append(f"  {COLUMN_TO_ALIAS[col]:<35} → {col}")
    lines.append("")
    lines.append("--- PROCEDIMIENTO ---")
    for col in COLUMNAS_IA[19:26]:
        lines.append(f"  {COLUMN_TO_ALIAS[col]:<35} → {col}")
    lines.append("")
    lines.append("--- DIAGNÓSTICO CLÍNICO ---")
    for col in COLUMNAS_IA[26:33]:
        lines.append(f"  {COLUMN_TO_ALIAS[col]:<35} → {col}")
    lines.append("")
    lines.append("--- ESTUDIOS IHQ GENERALES ---")
    for col in COLUMNAS_IA[33:38]:
        lines.append(f"  {COLUMN_TO_ALIAS[col]:<35} → {col}")
    lines.append("")
    lines.append("--- BIOMARCADORES (formato: 'POSITIVO/NEGATIVO/NO REPORTADO' "
                 "o el texto exacto del informe) ---")
    for col in COLUMNAS_IA[38:]:
        lines.append(f"  {COLUMN_TO_ALIAS[col]:<35}")
    return "\n".join(lines)


def llm_response_to_db_dict(llm_dict: dict) -> dict:
    """Mapea respuesta del LLM (con aliases JSON) → dict con nombres de
    columnas reales de la BD.

    Args:
        llm_dict: respuesta parseada del LLM, ej: {"numero_de_caso": "IHQ250001", ...}

    Returns:
        Dict con keys = nombres BD originales, ej: {"Numero de caso": "IHQ250001", ...}
    """
    out = {}
    for alias, col in ALIAS_TO_COLUMN.items():
        valor = llm_dict.get(alias, "N/A")
        if not isinstance(valor, str):
            valor = str(valor) if valor is not None else "N/A"
        out[col] = valor.strip() or "N/A"
    return out


if __name__ == "__main__":
    # Test rápido
    print(f"Total columnas: {len(COLUMNAS_IA)}")
    print(f"Total aliases únicos: {len(set(ALIAS_TO_COLUMN.keys()))}")
    if len(set(ALIAS_TO_COLUMN.keys())) != len(COLUMNAS_IA):
        print("⚠️ COLISIÓN de aliases — revisar")
    print()
    print("Primeros 5 mapeos:")
    for c in COLUMNAS_IA[:5]:
        print(f"  {c!r} → {COLUMN_TO_ALIAS[c]!r}")
    print()
    print("Schema válido:", "schema" in build_json_schema())
