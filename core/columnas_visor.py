# -*- coding: utf-8 -*-
"""
Fuente ÚNICA de la especificación de columnas del Visualizador de Datos.

La usan TANTO la tabla Tkinter (tksheet) en ui.py COMO el visor Qt
(visor_datos_qt.py), para garantizar que ambas vistas muestren EXACTAMENTE las
mismas columnas, en el mismo orden y con los mismos anchos. Centralizar aquí evita
que las dos vistas se desincronicen.

V6.9.50: extraído de ui.py._populate_treeview.
FIX: en la lista literal de ui.py faltaba una coma tras "IHQ_MUC2", por lo que
Python concatenaba   "IHQ_MUC2" "IHQ_CD15" -> "IHQ_MUC2IHQ_CD15"   y NINGUNA de
las dos columnas reales se mostraba. Aquí van como columnas separadas y correctas.
"""

# Orden EXACTO de columnas a mostrar (luego se filtran las que no existan en el DF).
COLS_TO_SHOW = [
    "Numero de caso",
    "N. de identificación",
    "Nombre Completo",
    "Procedimiento",
    "Organo",
    "Malignidad",
    "Diagnostico Coloracion",
    "Diagnostico Coloracion 2",
    "Diagnostico Principal",
    "Factor pronostico",
    "Descripcion macroscopica",   # V6.9.49: descripción macro (IHQ + coloración)
    "Descripcion microscopica",   # V6.9.49: descripción micro (IHQ + coloración)
    "IHQ_ORGANO",
    "IHQ_ESTUDIOS_SOLICITADOS",
    "IHQ_HER2",
    "IHQ_KI-67",
    "IHQ_RECEPTOR_ESTROGENOS",
    "IHQ_RECEPTOR_PROGESTERONA",
    "IHQ_PDL-1",
    "IHQ_P16_ESTADO",
    "IHQ_P16_PORCENTAJE",
    "IHQ_P40_ESTADO",
    "IHQ_E_CADHERINA",
    "IHQ_CK7",
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
    "IHQ_EBER",
    "IHQ_SYNAPTOFISINA",
    "IHQ_CKAE1E3",
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
    "IHQ_MAMOGLOBINA",
    "IHQ_HEPATOCITO",
    "IHQ_CK19",
    "IHQ_CK20",
    "IHQ_CDX2",
    "IHQ_EMA",
    "IHQ_GATA3",
    "IHQ_SOX10",
    "IHQ_P53",
    "IHQ_TTF1",
    "IHQ_S100",
    "IHQ_VIMENTINA",
    "IHQ_CHROMOGRANINA",
    "IHQ_SYNAPTOPHYSIN",
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
    "IHQ_BCL2",
    "IHQ_BCL6",
    "IHQ_MUM1",
    "IHQ_MUC1",
    "IHQ_MUC2",   # FIX V6.9.50: antes se perdía por coma faltante
    "IHQ_CD15",   # FIX V6.9.50: antes se perdía por coma faltante
    "IHQ_CD79A",
    "IHQ_ALK",
    "IHQ_CKAE1AE3",
    "IHQ_NAPSIN",
    "IHQ_CDK4",
    "IHQ_MDM2",
    "IHQ_PAX5",
    "IHQ_ACTIN",
    "IHQ_PAX8",
    "IHQ_GFAP",
    "IHQ_DOG1",
    "IHQ_H_CALDESMON",
    "IHQ_AML",
    "IHQ_HHV8",
    "IHQ_NEUN",
    "IHQ_P63",
    "IHQ_CALPONINA",
    "IHQ_BER_EP4",
    "IHQ_WT1",
    "IHQ_MLH1",
    "IHQ_MSH2",
    "IHQ_MSH6",
    "IHQ_PMS2",
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
    "IHQ_HMB45",
    "IHQ_PSA",
    "IHQ_INHIBINA",
    "IHQ_RACEMASA",
    "IHQ_34BETA",
    "IHQ_B2",
    "IHQ_SALL4",
    "IHQ_ALK1",
    "Estado Auditoria IA",
    "Fecha Ingreso Base de Datos",
]


# Renombrado SOLO de ENCABEZADOS (display). Las columnas de la BD conservan su
# nombre real (todo el pipeline de extracción/guardado depende de él); aquí solo
# cambiamos la ETIQUETA visible en la tabla para evitar confusión:
#   "Diagnostico Coloracion"    -> se EXTRAE del PDF de IHQ            -> "Diagnostico IHQ"
#   "Diagnostico Coloracion 2"  -> se EXTRAE de los PDFs de Coloración -> "Diagnostico Coloracion"
HEADER_ALIAS = {
    "Diagnostico Coloracion": "Diagnostico IHQ",
    "Diagnostico Coloracion 2": "Diagnostico Coloracion",
}


def simplificar_header(col: str) -> str:
    """Etiqueta del encabezado. Aplica primero el alias de display (HEADER_ALIAS);
    si no hay alias, quita lo que vaya después de '(' (igual que ui.py)."""
    if col in HEADER_ALIAS:
        return HEADER_ALIAS[col]
    return str(col).split("(")[0].strip()


def ancho_columna(col: str) -> int:
    """Ancho (px) por columna. Replica EXACTAMENTE el if/elif de ui.py
    (incluido el orden: 'Fecha' se evalúa antes que 'Fecha Ingreso')."""
    if "Numero de caso" in col:
        return 120
    elif "Fecha" in col:
        return 120
    elif "Procedimiento" in col:
        return 200
    elif "Organo" in col:
        return 200
    elif "Malignidad" in col:
        return 100
    elif "Diagnostico Coloracion" in col:
        return 300
    elif "Diagnostico Principal" in col:
        return 300
    elif "Factor pronostico" in col:
        return 200
    elif "Descripcion" in col:
        return 350
    elif col.startswith("IHQ_"):
        return 150
    elif "Estado Auditoria IA" in col:
        return 150
    elif "Fecha Ingreso" in col:
        return 180
    return 150


def ocultar_m_redundantes(df, base=None):
    """Quita del DISPLAY las filas M de coloración cuyo PACIENTE ya tiene una fila
    IHQ que refleja la coloración en su columna 'Diagnostico Coloracion 2'. NO borra
    de la BD; solo oculta para no duplicar. Versión PURA (sin self) extraída de
    ui.py._ocultar_m_redundantes. 'base' = DataFrame de referencia (por defecto df)."""
    if df is None or getattr(df, "empty", True) or "Numero de caso" not in df.columns:
        return df
    col = "Diagnostico Coloracion 2"
    if base is None or getattr(base, "empty", True):
        base = df
    if col not in base.columns or "N. de identificación" not in base.columns:
        return df
    if col not in df.columns or "N. de identificación" not in df.columns:
        return df

    def _ced(serie):
        return serie.astype(str).str.replace(r"\D", "", regex=True)

    b_nc = base["Numero de caso"].astype(str)
    b_esM = b_nc.str.match(r"^[Mm]\d", na=False)
    b_dx = base[col].astype(str).str.strip()
    b_real = ~b_dx.str.lower().isin(["", "nan", "none", "n/a"])
    b_ihq = (~b_esM) & b_real
    ceds_cubiertas = set(_ced(base.loc[b_ihq, "N. de identificación"]))
    if not ceds_cubiertas:
        return df

    d_nc = df["Numero de caso"].astype(str)
    d_esM = d_nc.str.match(r"^[Mm]\d", na=False)
    d_ced = _ced(df["N. de identificación"])
    redundante = d_esM.values & d_ced.isin(ceds_cubiertas).values
    return df[~redundante]
