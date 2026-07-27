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
    "Descripcion macroscopica",   # V6.9.55: descripción macro del informe IHQ (proceso/solicitud)
    "Descripcion microscopica",   # V6.9.55: descripción micro del informe IHQ (técnica + interpretación)
    "Descripcion macroscopica Coloracion",   # V6.9.55: macro REAL del tejido (PDF de coloración)
    "Descripcion microscopica Coloracion",   # V6.9.55: micro REAL del tejido (PDF de coloración)
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
    # V6.9.55: desdoble de descripciones por ORIGEN. Las columnas viejas contienen el
    # texto del informe IHQ (solicitud/proceso/técnica); las nuevas, la descripción
    # REAL del tejido tomada del PDF de coloración (macro/micro del estudio de histología).
    # V6.9.56: encabezados CORTOS — los largos ("Descripcion Macroscopica Coloracion")
    # se cortaban en la cabecera y no se distinguía cuál era la del IHQ y cuál la de la
    # Coloración. El ORIGEN va primero y en mayúsculas para que sea inequívoco.
    "Descripcion macroscopica": "IHQ · Macroscópica",
    "Descripcion microscopica": "IHQ · Microscópica",
    "Descripcion macroscopica Coloracion": "COLORACIÓN · Macroscópica",
    "Descripcion microscopica Coloracion": "COLORACIÓN · Microscópica",
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


# ═══════════════════════════════════════════════════════════════════════════
# V6.9.56: mostrar SOLO las columnas que APLICAN.
# Con ~130 columnas de biomarcadores, la tabla se llena de "N/A" inútiles. Estas
# columnas se OCULTAN cuando NINGUNA fila mostrada tiene un valor real; en cuanto
# un paciente sí tiene el biomarcador, la columna reaparece sola. Las columnas de
# identidad del caso NUNCA se ocultan (aunque vengan vacías).
# ═══════════════════════════════════════════════════════════════════════════
COLS_SIEMPRE = {
    "Numero de caso",
    "N. de identificación",
    "Nombre Completo",
    "Procedimiento",
    "Organo",
    "Malignidad",
    "Diagnostico Principal",
    "Fecha Ingreso Base de Datos",
}
def columna_tiene_datos(df, col) -> bool:
    """True si la columna tiene AL MENOS un valor real (no vacío/N/A) en el df.
    Usa comparación EXACTA (isin) por rendimiento; ver _NA_DISPLAY más abajo."""
    if df is None or col not in getattr(df, "columns", []):
        return False
    s = df[col]
    if s.isna().all():
        return False
    vals = s.fillna("").astype(str)
    return bool((~vals.isin(_NA_DISPLAY)).any())


# ═══════════════════════════════════════════════════════════════════════════
# V6.9.73: los BIOMARCADORES salen de la tabla.
# De las 139 columnas que se mostraban, 125 eran biomarcadores: el 90% del ancho
# de la tabla para un dato que casi siempre está vacío en la fila que miras. Ahora
# viven donde tienen sentido: en la FICHA DEL PACIENTE, agrupados por estudio y
# mostrando SOLO los que ese estudio tiene con resultado.
#
# Es un cambio de VISTA, no de datos: la BD los conserva, la exportación a Excel
# los sigue llevando (lee de la BD, no de la tabla), la búsqueda y el orden no
# cambian. Un solo interruptor para que la tabla Tkinter y el visor Qt sigan en
# paridad exacta, que fue lo que se buscó en V6.9.50.
#
# IHQ_ORGANO e IHQ_ESTUDIOS_SOLICITADOS NO son biomarcadores: son metadatos del
# estudio (órgano de la muestra y qué panel pidió el patólogo) y se quedan.
# ═══════════════════════════════════════════════════════════════════════════
# V6.9.73: se probó ocultarlos (139 -> 17 columnas) pero el usuario los quiere en el
# Visualizador: es donde se comparan biomarcadores entre casos. El interruptor se deja
# porque la infraestructura ya está y puede querer apagarlos en otro momento.
MOSTRAR_BIOMARCADORES_EN_TABLA = True
BIO_NO_ES_BIOMARCADOR = {"IHQ_ORGANO", "IHQ_ESTUDIOS_SOLICITADOS"}


def es_columna_biomarcador(col) -> bool:
    c = str(col or "").strip().upper()
    return c.startswith("IHQ_") and c not in BIO_NO_ES_BIOMARCADOR


def columnas_visibles(df, cols=None):
    """Columnas a mostrar: las de identidad SIEMPRE + las demás solo si aplican
    (tienen algún dato real en el df mostrado). Evita el mar de 'N/A'."""
    if cols is None:
        cols = COLS_TO_SHOW
    if not MOSTRAR_BIOMARCADORES_EN_TABLA:
        cols = [c for c in cols if not es_columna_biomarcador(c)]
    if df is None or getattr(df, "empty", True):
        return [c for c in cols if c in getattr(df, "columns", []) and c in COLS_SIEMPRE]
    out = []
    for c in cols:
        if c not in df.columns:
            continue
        if c in COLS_SIEMPRE or columna_tiene_datos(df, c):
            out.append(c)
    return out


# ═══════════════════════════════════════════════════════════════════════════
# V6.9.57: celdas SIN DATO se muestran VACÍAS (no "N/A").
# Ocultar la COLUMNA solo funciona si NINGÚN paciente de la vista tiene el
# biomarcador; en la vista completa casi todas las columnas tienen algún paciente
# con dato, así que la columna se queda y el resto de celdas quedaban llenas de
# "N/A". Aquí se limpia la CELDA: sin dato -> celda vacía. Solo afecta al DISPLAY
# (la BD conserva su valor; búsqueda, orden y exportación no cambian).
#
# "NO MENCIONADO" SÍ se conserva: significa que el biomarcador se SOLICITÓ pero no
# aparece en el informe -> es un dato real (señal de calidad), no un "no aplica".
# ═══════════════════════════════════════════════════════════════════════════
# Marcadores LITERALES de "sin dato". En la BD real solo aparecen '', 'N/A' y
# 'NO APLICA'; el resto se incluye por defensa. Se comparan EXACTOS (isin) porque
# es ~5x más rápido que normalizar 1,2 M de celdas (0,42 s -> 0,09 s).
_NA_DISPLAY = {
    "", "N/A", "n/a", "N/a", "NA", "na", "NaN", "nan", "NAN",
    "None", "none", "NONE", "NULL", "null", "Null",
    "NO APLICA", "No aplica", "no aplica", "NO ENCONTRADO", "No encontrado",
    "-", "--",
}


def filas_para_display(df):
    """DataFrame -> lista de filas (strings) con las celdas SIN DATO en blanco."""
    if df is None or getattr(df, "empty", True):
        return []
    d = df.fillna("").astype(str)
    return d.mask(d.isin(_NA_DISPLAY), "").values.tolist()


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
