# -*- coding: utf-8 -*-
"""
Informe estadístico (fact-sheet) en PDF — ONCONOVA Gestor Oncológico HUV.

Informe DETERMINISTA (sin IA) con maqueta institucional decorada:
encabezado navy con logo, KPIs como tarjetas de colores, bandas de sección,
gráficos (donas por sexo, dona de malignidad, barras top diagnósticos,
tendencia mensual) y tabla maestra. Construido con reportlab + matplotlib.

Uso:
    from core.informe_estadistico import generar_informe_estadistico_pdf
    generar_informe_estadistico_pdf(df, "ruta/salida.pdf")
"""
import os
import tempfile
from datetime import datetime

NAVY = "#2d3e5e"
GREY = "#5a6472"
HEADER_FILL = "#e9edf3"
LINE = "#c7ceda"
# Paleta para tarjetas KPI y gráficos
KPI_COLORS = ["#2d3e5e", "#c0392b", "#1f8a5b", "#d98e2b", "#2980b9"]
PALETA = ["#2d3e5e", "#c0392b", "#1f8a5b", "#e0a23a", "#2980b9",
          "#8a909c", "#7d5ba6", "#16a085", "#cd6155", "#34495e", "#5b7aa8", "#d35400"]

NO_ONCOLOGICAS = {
    "NEGATIVO PARA MALIGNIDAD", "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA",
    "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO", "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)",
    "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)", "GLIOSIS / LESION REACTIVA SNC",
    "RECHAZO DE TRASPLANTE", "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)", "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)",
    "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)", "MUESTRA INSUFICIENTE / NO CONCLUYENTE",
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)", "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
    "OTRO / NO CATEGORIZADO", "SIN DATO",
}
# Subgrupos NO oncológicos (para la tabla de cobertura que reconcilia al total)
GRUPO_NO_NEOPLASICO = {
    "NEGATIVO PARA MALIGNIDAD", "HALLAZGO HISTOLOGICO NORMAL / NO PATOLOGICO",
    "GLIOSIS / LESION REACTIVA SNC", "RECHAZO DE TRASPLANTE",
    "MALFORMACION DEL DESARROLLO / HETEROTOPIA SNC",
    "PROCESO INFLAMATORIO / INFECCIOSO (NO NEOPLASICO)",
    "HALLAZGO NO NEOPLASICO / NEGATIVO (OTRO)", "ESTUDIO DE MEDULA OSEA (MORFOLOGIA)",
    "ENFERMEDAD DE HIRSCHSPRUNG / CELULAS GANGLIONARES",
}
GRUPO_SIN_DX = {
    "RESULTADO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)", "ESTUDIO IHQ DE MARCADORES (SIN TUMOR CLASIFICADO)",
    "MUESTRA NO REPRESENTATIVA / NO DIAGNOSTICA", "MUESTRA INSUFICIENTE / NO CONCLUYENTE",
    # V6.9.30: el campo Dx traía marcadores IHQ / "ver comentario" / descripción
    # de espécimen en vez de un diagnóstico (problema de extracción). Se agrupan
    # aquí como "estudios sin diagnóstico específico" en vez de una fila aparte.
    "SIN DIAGNOSTICO EN TEXTO / REVISAR (EXTRACCION)",
}
_VACIO = ("", "N/A", "NO MENCIONADO", "NO APLICA", "NAN", "NONE", "NULL", "SIN DATO", "NO ENCONTRADO")
_MESES = {"01": "Ene", "02": "Feb", "03": "Mar", "04": "Abr", "05": "May", "06": "Jun",
          "07": "Jul", "08": "Ago", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dic"}


def _sexo(v):
    s = str(v or "").strip().upper()
    if not s or s in ("N/A", "NAN", "NO ENCONTRADO", "NONE", "-"):
        return "Sin dato"  # genuinamente vacio (sin dato real)
    if "MASC" in s or "HOMBRE" in s or s == "M":
        return "Hombres"
    if "FEM" in s or "MUJER" in s or s == "F":
        return "Mujeres"
    # V6.9.28 FIX: valores presentes pero NO binarios (INDETERMINADO, AMBOS,
    # TRANSGENERO, etc.) -> "Otro". El dato SI existe; no es "Sin dato".
    return "Otro"


def _es_maligno(v):
    return "MALIGNO" in str(v or "").upper()


def _es_benigno(v):
    return "BENIGNO" in str(v or "").upper()


def _pct(n, d):
    return f"{(100.0 * n / d):.1f}%" if d else "0.0%"


def _logo(nombre):
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "imagenes", nombre)
    return p if os.path.exists(p) else None


def _fig():
    from matplotlib.figure import Figure
    return Figure


def _donut(data, titulo, path, top=6, center=None, numerar=False):
    import matplotlib
    matplotlib.use("Agg")
    Figure = _fig()
    items = list(data.items())
    grandes = items[:top]
    resto = sum(v for _, v in items[top:])
    labels = [k for k, _ in grandes]
    vals = [v for _, v in grandes]
    if resto > 0:
        labels.append("OTROS")
        vals.append(resto)
    fig = Figure(figsize=(3.4, 3.4), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax = fig.add_subplot(111)
    if sum(vals) <= 0:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center")
        ax.axis("off")
    else:
        colores = [PALETA[i % len(PALETA)] for i in range(len(labels))]
        wedges, _t = ax.pie(vals, colors=colores, startangle=90, counterclock=False,
                            wedgeprops={"width": 0.42, "edgecolor": "white", "linewidth": 1.2})
        if numerar:
            # V6.9.28 - numero de ranking (#) sobre cada porcion, para mapearla
            # con su fila en la tabla de abajo (mismo orden que 'labels').
            import math
            import matplotlib.patheffects as _pe
            r_lbl = 1.0 - 0.42 / 2.0  # centro del anillo del donut
            for i, w in enumerate(wedges):
                ang = math.radians((w.theta1 + w.theta2) / 2.0)
                ax.text(r_lbl * math.cos(ang), r_lbl * math.sin(ang), str(i + 1),
                        ha="center", va="center", fontsize=8, fontweight="bold", color="white",
                        path_effects=[_pe.withStroke(linewidth=1.8, foreground="#222222")])
        if center:
            ax.text(0, 0, center, ha="center", va="center", fontsize=13, fontweight="bold", color=NAVY)
        ax.set_title(titulo, fontsize=10, fontweight="bold", color=NAVY, pad=8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="#ffffff")
    return labels, vals


def _barh(data, titulo, path, top=10):
    import matplotlib
    matplotlib.use("Agg")
    Figure = _fig()
    items = list(data.items())[:top][::-1]
    fig = Figure(figsize=(7.2, 4.3), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax = fig.add_subplot(111)
    if not items:
        ax.text(0.5, 0.5, "Sin datos", ha="center", va="center"); ax.axis("off")
    else:
        # V6.9.29: las etiquetas pueden venir en 2 líneas "DIAGNOSTICO\nÓrgano".
        # Truncamos solo la 1ª línea (diagnóstico) para no cortar el órgano.
        def _fmt(k):
            ps = str(k).split("\n")
            ps[0] = ps[0][:40]
            return "\n".join(ps)
        et = [_fmt(k) for k, _ in items]
        va = [v for _, v in items]
        colores = [PALETA[i % len(PALETA)] for i in range(len(items))]
        ax.barh(et, va, color=colores)
        ax.set_title(titulo, fontsize=11, fontweight="bold", color=NAVY, pad=8)
        ax.tick_params(axis="y", labelsize=7)
        ax.tick_params(axis="x", labelsize=8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.margins(x=0.12)
        for i, v in enumerate(va):
            ax.text(v, i, f" {v}", va="center", fontsize=8, color=GREY)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="#ffffff")


def _trend(monthly, path):
    import matplotlib
    matplotlib.use("Agg")
    Figure = _fig()
    fig = Figure(figsize=(7.2, 2.9), dpi=150)
    fig.patch.set_facecolor("#ffffff")
    ax = fig.add_subplot(111)
    if not monthly:
        ax.text(0.5, 0.5, "Sin datos de fecha", ha="center", va="center"); ax.axis("off")
    else:
        xs = list(range(len(monthly)))
        ys = [v for _, v in monthly]
        labs = [f"{_MESES.get(k.split('-')[1], k.split('-')[1])} {k.split('-')[0][2:]}" for k, _ in monthly]
        ax.fill_between(xs, ys, color="#2d3e5e", alpha=0.18)
        ax.plot(xs, ys, color="#2d3e5e", marker="o", markersize=4, linewidth=2)
        ax.set_xticks(xs)
        ax.set_xticklabels(labs, rotation=45, ha="right", fontsize=7)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_title("Casos por mes", fontsize=11, fontweight="bold", color=NAVY, pad=8)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
        for x, y in zip(xs, ys):
            ax.text(x, y, f"{y}", ha="center", va="bottom", fontsize=6.5, color=GREY)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="#ffffff")


def generar_informe_estadistico_pdf(df, out_path,
                                    institucion="Hospital Universitario del Valle",
                                    area="Área de Cirugía Oncológica"):
    """Genera el informe estadístico PDF decorado. Devuelve la ruta de salida."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether,
    )
    from core.normalizador_diagnosticos import categorizar_diagnostico_con_organo
    from core.normalizador_organos import normalizar_organo, elegir_columna_organo
    import pandas as pd

    navy = colors.HexColor(NAVY)
    grey = colors.HexColor(GREY)
    hfill = colors.HexColor(HEADER_FILL)
    line = colors.HexColor(LINE)
    CW = 17.8 * cm  # ancho de contenido (A4, márgenes 1.6cm)

    total = len(df)
    dc = "Diagnostico Principal" if "Diagnostico Principal" in df.columns else None
    co = elegir_columna_organo(df.columns)
    org_norm = df[co].apply(normalizar_organo) if co is not None else None
    if dc is not None:
        cat = df.apply(lambda r: categorizar_diagnostico_con_organo(
            r[dc], org_norm.loc[r.name] if (org_norm is not None and r.name in org_norm.index) else None), axis=1)
    else:
        cat = None
    sexo = df["Genero"].apply(_sexo) if "Genero" in df.columns else None
    mal_col = "Malignidad" if "Malignidad" in df.columns else None
    malignos = int(df[mal_col].apply(_es_maligno).sum()) if mal_col else 0
    benignos = int(df[mal_col].apply(_es_benigno).sum()) if mal_col else 0
    otros_mal = total - malignos - benignos

    # periodo + serie mensual
    fmin = fmax = "—"
    monthly = []
    if "Fecha Informe" in df.columns:
        f = df["Fecha Informe"].astype(str).str.strip()
        f = f[f.str.match(r"^\d{2}/\d{2}/\d{4}$", na=False)]
        if not f.empty:
            fp = pd.to_datetime(f, format="%d/%m/%Y", errors="coerce").dropna()
            if not fp.empty:
                fmin = fp.min().strftime("%d/%m/%Y")
                fmax = fp.max().strftime("%d/%m/%Y")
                ms = fp.dt.strftime("%Y-%m").value_counts().sort_index()
                monthly = list(ms.items())

    def onco_counts(serie_cat):
        vc = serie_cat.value_counts()
        return vc[~vc.index.isin(NO_ONCOLOGICAS)]

    # V6.9.28: en "Diagnosticos por sexo" clasificamos por DIAGNOSTICO + ORGANO.
    SEP_DX_ORG = " ||| "
    def onco_counts_org(mask):
        if cat is None or mask is None:
            return None
        c = cat[mask].astype(str)
        onco = ~c.isin(NO_ONCOLOGICAS)
        c = c[onco]
        if org_norm is not None:
            o = org_norm[mask].astype(str)[onco]
            return c.str.cat(o, sep=SEP_DX_ORG).value_counts()
        return c.value_counts()

    onco_total = onco_counts(cat) if cat is not None else None
    n_onco = int(onco_total.sum()) if onco_total is not None else 0
    # V6.9.29: órgano DOMINANTE (más frecuente) por categoría diagnóstica, para
    # especificar el órgano de cada diagnóstico en la tabla maestra y el Top-10.
    org_dom = {}
    if cat is not None and org_norm is not None:
        import pandas as _pd
        _dfx = _pd.DataFrame({"c": list(cat.values), "o": list(org_norm.values)})
        _dfx = _dfx[(~_dfx["c"].isin(NO_ONCOLOGICAS)) & (~_dfx["o"].isin(_VACIO))]
        for _c, _grp in _dfx.groupby("c"):
            _vc = _grp["o"].value_counts()
            if len(_vc):
                org_dom[_c] = str(_vc.index[0]).title()
    # por categoria de diagnostico (para la tabla maestra: columnas Hombres/Mujeres)
    onco_h = onco_counts(cat[sexo == "Hombres"]) if (cat is not None and sexo is not None) else None
    onco_m = onco_counts(cat[sexo == "Mujeres"]) if (cat is not None and sexo is not None) else None
    # por diagnostico + organo (para las donas/tablas "por sexo")
    onco_h_org = onco_counts_org(sexo == "Hombres") if (cat is not None and sexo is not None) else None
    onco_m_org = onco_counts_org(sexo == "Mujeres") if (cat is not None and sexo is not None) else None

    # Reconciliación de cobertura: TODOS los casos se reparten en estos grupos (suma = total)
    allcat = cat.value_counts() if cat is not None else None

    def _gsum(s):
        return int(sum(int(allcat.get(k, 0)) for k in s)) if allcat is not None else 0

    n_noneo = _gsum(GRUPO_NO_NEOPLASICO)
    n_sindx = _gsum(GRUPO_SIN_DX)  # V6.9.30: ahora incluye los ex-"revisar extracción"
    n_otrocat = int(allcat.get("OTRO / NO CATEGORIZADO", 0)) if allcat is not None else 0
    n_sindato = total - n_onco - n_noneo - n_sindx - n_otrocat

    org_top = org_norm[org_norm != "SIN DATO"].value_counts().head(12) if org_norm is not None else None
    n_organos = int(org_norm[org_norm != "SIN DATO"].nunique()) if org_norm is not None else 0
    bio_cols = [c for c in df.columns if c.upper().startswith("IHQ_")
                and c.upper() not in ("IHQ_ORGANO", "IHQ_ESTUDIOS_SOLICITADOS")]
    bio_counts = {}
    for bc in bio_cols:
        n = int(df[bc].apply(lambda v: v is not None and str(v).strip().upper() not in _VACIO).sum())
        if n > 0:
            bio_counts[bc] = n
    n_biomarcadores = len(bio_counts)
    bio_top = sorted(bio_counts.items(), key=lambda x: -x[1])[:12]

    # ---------- gráficos a temp ----------
    tmp = tempfile.mkdtemp(prefix="onconova_fs_")
    p_dh, p_dm = os.path.join(tmp, "dh.png"), os.path.join(tmp, "dm.png")
    p_mal, p_bar, p_trend = os.path.join(tmp, "mal.png"), os.path.join(tmp, "bar.png"), os.path.join(tmp, "trend.png")
    lab_h = vals_h = lab_m = vals_m = None
    if onco_h_org is not None and onco_h_org.sum() > 0:
        lab_h, vals_h = _donut(onco_h_org.to_dict(), "Hombres", p_dh, numerar=True)
    if onco_m_org is not None and onco_m_org.sum() > 0:
        lab_m, vals_m = _donut(onco_m_org.to_dict(), "Mujeres", p_dm, numerar=True)
    _donut({"Maligno": malignos, "Benigno": benignos, "Otros/N.D.": max(otros_mal, 0)},
           "Malignidad", p_mal, top=3, center=_pct(malignos, total))
    if onco_total is not None:
        # V6.9.29: etiqueta en 2 líneas -> "DIAGNÓSTICO\nÓrgano principal"
        bar_data = {f"{k}\n{org_dom.get(k, '—')}": v for k, v in onco_total.items()}
        _barh(bar_data, "Top 10 diagnósticos oncológicos (con órgano principal)", p_bar, top=10)
    _trend(monthly, p_trend)

    # ---------- estilos ----------
    styles = getSampleStyleSheet()
    cell = ParagraphStyle("c", parent=styles["Normal"], fontSize=8, leading=10)
    h_sub = ParagraphStyle("s", parent=styles["Normal"], textColor=grey, fontSize=9, leading=11)
    # V6.9.28 FIX: estilos con leading suficiente para fuentes grandes. Evita que el
    # numero/titulo (18pt) se monte sobre la etiqueta de abajo en header y tarjetas KPI.
    cell_num = ParagraphStyle("cnum", parent=cell, fontSize=18, leading=21)
    cell_lbl = ParagraphStyle("clbl", parent=cell, fontSize=6.7, leading=8.5)
    h_title = ParagraphStyle("ht", parent=cell, fontSize=18, leading=22)
    h_sub1 = ParagraphStyle("hs1", parent=cell, fontSize=11, leading=14)
    h_sub2 = ParagraphStyle("hs2", parent=cell, fontSize=8.5, leading=11)

    def band(text):
        t = Table([[Paragraph(f'<font color="white" size=12><b>{text}</b></font>', cell)]], colWidths=[CW])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), navy), ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        return t

    story = []

    # ---------- ENCABEZADO (banda navy con logo) ----------
    fav = _logo("favicon.png")
    titulo_par = [
        Paragraph('<font color="white"><b>Estadísticas de Inmunohistoquímica</b></font>', h_title),
        Paragraph('<font color="#cfd8e6">Informe de un vistazo · ONCONOVA Gestor Oncológico</font>', h_sub1),
        Spacer(1, 3),
        Paragraph(f'<font color="#cfd8e6">{institucion} · {area}</font>', h_sub2),
    ]
    if fav:
        try:
            head = Table([[Image(fav, width=1.7 * cm, height=1.7 * cm), titulo_par]],
                         colWidths=[2.3 * cm, CW - 2.3 * cm])
        except Exception:
            head = Table([[titulo_par]], colWidths=[CW])
    else:
        head = Table([[titulo_par]], colWidths=[CW])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), navy), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(head)
    # franja de acento de colores
    acc = Table([[""] * 5], colWidths=[CW / 5.0] * 5, rowHeights=[5])
    acc.setStyle(TableStyle([("BACKGROUND", (i, 0), (i, 0), colors.HexColor(KPI_COLORS[i])) for i in range(5)]))
    story.append(acc)
    story.append(Paragraph(
        f'Periodo: <b>{fmin}</b> a <b>{fmax}</b>  ·  Total de casos: <b>{total}</b>  ·  '
        f'Generado: {datetime.now().strftime("%d/%m/%Y")}', h_sub))
    story.append(Spacer(1, 8))

    # ---------- KPI cards (colores) ----------
    kpis = [
        ("TOTAL CASOS", f"{total:,}".replace(",", ".")),
        ("% MALIGNOS", _pct(malignos, total)),
        ("CATEGORÍAS ANATÓMICAS", str(n_organos)),
        ("BIOMARCADORES DISTINTOS", str(n_biomarcadores)),
        ("TUMORES ANALIZADOS", str(n_onco)),
    ]
    kcell = []
    for k, v in kpis:
        kcell.append([Paragraph(f'<font color="white"><b>{v}</b></font>', cell_num),
                      Paragraph(f'<font color="#eef2f8"><b>{k}</b></font>', cell_lbl)])
    kpi_tbl = Table([kcell], colWidths=[CW / 5.0] * 5)
    ksty = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("INNERGRID", (0, 0), (-1, -1), 3, colors.white)]
    for i in range(5):
        ksty.append(("BACKGROUND", (i, 0), (i, 0), colors.HexColor(KPI_COLORS[i])))
    kpi_tbl.setStyle(TableStyle(ksty))
    story.append(kpi_tbl)
    story.append(Spacer(1, 12))

    # ---------- Resumen por sexo ----------
    story.append(band("Resumen por sexo"))
    story.append(Spacer(1, 5))

    def top3(serie):
        if serie is None or serie.empty:
            return "—"
        return ", ".join(list(serie.index[:3]))

    def fila_sexo(nombre, mask):
        sub = df[mask] if mask is not None else df
        n = len(sub)
        nmal = int(sub[mal_col].apply(_es_maligno).sum()) if mal_col else 0
        t3 = top3(onco_counts(cat[mask])) if (cat is not None and mask is not None) else top3(onco_total)
        return [nombre, f"{n}", _pct(n, total), _pct(nmal, n), Paragraph(f'<font size=7>{t3}</font>', cell)]

    sex_rows = [["Sexo", "Casos", "% del total", "% malignos", "Top 3 diagnósticos oncológicos"]]
    if sexo is not None:
        sex_rows.append(fila_sexo("Hombres", sexo == "Hombres"))
        sex_rows.append(fila_sexo("Mujeres", sexo == "Mujeres"))
        for _et in ("Otro", "Sin dato"):
            if (sexo == _et).sum() > 0:
                sex_rows.append(fila_sexo(_et, sexo == _et))
    sex_rows.append(fila_sexo("Total", None))
    sex_tbl = Table(sex_rows, colWidths=[2.2 * cm, 1.7 * cm, 2.2 * cm, 2.2 * cm, 9.5 * cm])
    sex_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), hfill), ("TEXTCOLOR", (0, 0), (-1, 0), navy),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f4f6fa")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#fafbfd")]),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(sex_tbl)
    # V6.9.28: aclara que "Otro" = genero NO binario PRESENTE (no faltante).
    if sexo is not None and (sexo == "Otro").sum() > 0:
        _det = df.loc[sexo == "Otro", "Genero"].astype(str).str.strip().str.upper().value_counts()
        _desg = ", ".join(f"{str(k).capitalize()} ({int(v)})" for k, v in _det.items())
        story.append(Spacer(1, 3))
        story.append(Paragraph(
            f'<font size=7 color="#5a6472"><b>Otro</b> = género no binario registrado en el informe '
            f'(el dato SÍ existe, no es faltante): {_desg}.</font>', cell))
    story.append(Spacer(1, 10))

    # ---------- Donas por sexo (banda + contenido juntos, sin huerfanas) ----------

    def ranked(labels, vals):
        if not labels:
            return Paragraph('<font size=8 color="#5a6472">Sin datos</font>', cell)
        tot = sum(vals) or 1
        rows = [["#", "Diagnóstico", "Órgano", "N", "%"]]
        for i, (lb, v) in enumerate(zip(labels, vals), 1):
            if SEP_DX_ORG in str(lb):
                diag, org = str(lb).split(SEP_DX_ORG, 1)
            else:
                diag, org = str(lb), "—"  # p.ej. "OTROS"
            rows.append([str(i),
                         Paragraph(f'<font size=6.8>{diag}</font>', cell),
                         Paragraph(f'<font size=6.8>{org}</font>', cell),
                         str(v), _pct(v, tot)])
        t = Table(rows, colWidths=[0.55 * cm, 3.5 * cm, 2.25 * cm, 0.85 * cm, 0.95 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), hfill), ("TEXTCOLOR", (0, 0), (-1, 0), navy),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.3, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafbfd")]),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    ch = [Image(p_dh, 4.9 * cm, 4.9 * cm), Spacer(1, 4), ranked(lab_h, vals_h)] if lab_h else \
        [Paragraph('<font size=8 color="#5a6472">Hombres: sin datos oncológicos</font>', cell)]
    cm_ = [Image(p_dm, 4.9 * cm, 4.9 * cm), Spacer(1, 4), ranked(lab_m, vals_m)] if lab_m else \
        [Paragraph('<font size=8 color="#5a6472">Mujeres: sin datos oncológicos</font>', cell)]
    drow = Table([[ch, cm_]], colWidths=[CW / 2.0, CW / 2.0])
    drow.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story.append(KeepTogether([
        band("Diagnósticos oncológicos más frecuentes por sexo"), Spacer(1, 5), drow]))
    story.append(Spacer(1, 12))

    # ---------- Panorama general (malignidad + barras + tendencia) ----------
    pano = Table([[Image(p_mal, 5.0 * cm, 5.0 * cm), Image(p_bar, 10.2 * cm, 5.4 * cm)]],
                 colWidths=[5.4 * cm, CW - 5.4 * cm])
    pano.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(KeepTogether([
        band("Panorama general"), Spacer(1, 6), pano, Spacer(1, 8),
        Image(p_trend, width=CW, height=CW * 0.34)]))
    story.append(Spacer(1, 12))

    # ---------- Cobertura: reconciliación al total (banda + tabla juntas) ----------
    # V6.9.43: agrupado en "Casos CON diagnóstico" (tumores + no-neoplásicos: ambos
    # SON un diagnóstico, solo que uno tiene tumor y el otro no) vs "Sin diagnóstico".
    # Las 2 sub-filas indentadas suman el subtotal -> evita verlas como grupos
    # separados al mismo nivel (que confundía).
    n_con_dx = n_onco + n_noneo
    n_sin_dx_total = n_sindx + (n_otrocat if n_otrocat > 0 else 0) + (n_sindato if n_sindato > 0 else 0)
    rec_rows = [["Grupo", "Casos", "%"]]
    rec_rows.append([Paragraph('<b>Casos CON diagnóstico</b>', cell), str(n_con_dx), _pct(n_con_dx, total)])
    rec_rows.append([Paragraph('<font size=8>&nbsp;&nbsp;&nbsp;Tumores (neoplasias benignas o malignas)</font>', cell),
                     str(n_onco), _pct(n_onco, total)])
    rec_rows.append([Paragraph('<font size=8>&nbsp;&nbsp;&nbsp;Hallazgos no-neoplásicos (negativos, inflamatorios, médula ósea, etc.)</font>', cell),
                     str(n_noneo), _pct(n_noneo, total)])
    rec_rows.append([Paragraph('<b>Casos SIN diagnóstico específico / muestra no diagnóstica</b>', cell),
                     str(n_sin_dx_total), _pct(n_sin_dx_total, total)])
    rec_rows.append([Paragraph('<b>TOTAL</b>', cell), str(total), "100%"])
    rec_tbl = Table(rec_rows, colWidths=[CW - 5.0 * cm, 2.5 * cm, 2.5 * cm])
    rec_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), hfill), ("TEXTCOLOR", (0, 0), (-1, 0), navy),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#eaf3ee")),  # subtotal CON diagnóstico
        ("BACKGROUND", (0, 2), (-1, 3), colors.white),                # sub-filas (tumores / no-neoplásicos)
        ("BACKGROUND", (0, 4), (-1, 4), colors.HexColor("#f7f0e8")),  # fila SIN diagnóstico
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#f4f6fa")),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(KeepTogether([
        band(f"Cobertura: cómo se distribuyen los {total} casos"), Spacer(1, 5), rec_tbl]))
    story.append(Spacer(1, 12))

    # ---------- Tabla maestra (solo oncológicos) ----------
    story.append(band(f"Diagnósticos oncológicos en detalle — {n_onco} casos neoplásicos"))
    story.append(Spacer(1, 5))
    if onco_total is not None and not onco_total.empty:
        hc = onco_h.to_dict() if onco_h is not None else {}
        mc = onco_m.to_dict() if onco_m is not None else {}
        rows = [["#", "Categoría neoplásica", "Órgano principal", "Casos", "%", "Hombres", "Mujeres"]]
        for i, (k, v) in enumerate(onco_total.items(), 1):
            rows.append([str(i), Paragraph(f'<font size=7>{k}</font>', cell),
                         Paragraph(f'<font size=7>{org_dom.get(k, "—")}</font>', cell),
                         str(int(v)), _pct(int(v), n_onco),
                         str(int(hc.get(k, 0))), str(int(mc.get(k, 0)))])
        rows.append(["", Paragraph('<b>TOTAL ONCOLÓGICOS</b>', cell), "", str(n_onco), "100%",
                     str(int(sum(hc.values()))), str(int(sum(mc.values())))])
        master = Table(rows, colWidths=[0.7 * cm, 6.6 * cm, 3.6 * cm, 1.5 * cm, 1.3 * cm, 1.55 * cm, 1.55 * cm], repeatRows=1)
        master.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), navy), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.3, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (3, 0), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f4f6fa")]),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"), ("BACKGROUND", (0, -1), (-1, -1), hfill),
            ("TOPPADDING", (0, 0), (-1, -1), 1.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ]))
        story.append(master)
    story.append(Spacer(1, 12))

    # ---------- Órganos + biomarcadores (banda + tablas juntas) ----------

    def kv_tbl(items, c1, total_ref):
        rows = [[c1, "Casos", "%"]]
        for k, v in items:
            rows.append([Paragraph(f'<font size=7.5>{str(k).replace("IHQ_", "")}</font>', cell),
                         str(int(v)), _pct(int(v), total_ref)])
        t = Table(rows, colWidths=[5.2 * cm, 1.5 * cm, 1.4 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), hfill), ("TEXTCOLOR", (0, 0), (-1, 0), navy),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("GRID", (0, 0), (-1, -1), 0.3, line), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fafbfd")]),
            ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    sub = ParagraphStyle("k", parent=styles["Heading3"], textColor=navy, fontSize=11, spaceAfter=3)
    col_org = [Paragraph("Top órganos (categoría anatómica)", sub),
               kv_tbl(list(org_top.items()) if org_top is not None else [], "Órgano", total)]
    col_bio = [Paragraph("Top biomarcadores (casos evaluados)", sub),
               kv_tbl(bio_top, "Biomarcador", total)]
    dual = Table([[col_org, col_bio]], colWidths=[CW / 2.0, CW / 2.0])
    dual.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    story.append(KeepTogether([band("Órganos y biomarcadores"), Spacer(1, 6), dual]))
    story.append(Spacer(1, 10))

    nota = ParagraphStyle("n", parent=styles["Normal"], fontSize=7.5, textColor=grey, leading=10)
    no_onco = total - n_onco
    story.append(Paragraph(
        f"<b>Nota metodológica:</b> informe basado en {total} estudios de inmunohistoquímica del periodo. "
        f"Las cifras son <b>conteos de casos</b> (no incidencia poblacional, mortalidad ni prevalencia). "
        f"De los {total} casos, {n_onco} corresponden a diagnósticos oncológicos categorizados y "
        f"{no_onco} a hallazgos no-neoplásicos, estudios sin diagnóstico específico o pendientes de revisión. "
        f"% malignos calculado sobre el campo Malignidad ({malignos} malignos, {benignos} benignos).", nota))

    # ---------- Footer (banda con logo) ----------
    logo_color = _logo("logo.png")

    def _footer(canvas, doc_):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(navy); canvas.setLineWidth(1.2)
        canvas.line(1.6 * cm, 1.35 * cm, w - 1.6 * cm, 1.35 * cm)
        canvas.setFont("Helvetica-Oblique", 7); canvas.setFillColor(grey)
        canvas.drawString(1.6 * cm, 1.02 * cm,
                          "Documento confidencial — Ley 1581 (Habeas Data). ONCONOVA Gestor Oncológico HUV.")
        canvas.drawRightString(w - 1.6 * cm, 1.02 * cm, f"Página {doc_.page}")
        # V6.9.28 FIX: se elimino el logo centrado del footer (se montaba sobre el texto).
        canvas.restoreState()

    doc = SimpleDocTemplate(out_path, pagesize=A4,
                            leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                            topMargin=1.4 * cm, bottomMargin=1.9 * cm,
                            title="Informe estadístico ONCONOVA")
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)

    for p in (p_dh, p_dm, p_mal, p_bar, p_trend):
        try:
            os.remove(p)
        except Exception:
            pass
    try:
        os.rmdir(tmp)
    except Exception:
        pass
    return out_path
