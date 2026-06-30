# -*- coding: utf-8 -*-
"""
Visor de Datos (PySide6 / Qt) — ventana independiente de alto rendimiento.

Muestra EXACTAMENTE las mismas columnas y datos que la tabla del Visualizador en
ui.py (tksheet), pero con QTableView (modelo/vista respaldado en C++), cuyo scroll
es nativo y veloz incluso con ~8.000 filas x ~140 columnas.

Se lanza como PROCESO APARTE desde la app Tkinter (botón "Tabla Rápida (Qt)"),
porque Tkinter y Qt no pueden compartir el mismo bucle de eventos. Lee la MISMA
base de datos (respeta ONCONOVA_DB_OVERRIDE -> prod/DEV) usando el mismo backend.

Ejecutar con el entorno Qt:
    env_qt\\Scripts\\python.exe visor_datos_qt.py
Autotest headless:
    set QT_QPA_PLATFORM=offscreen && env_qt\\Scripts\\python.exe visor_datos_qt.py --self-test

V6.9.50 — Paridad v1: todas las columnas/orden/datos, colores (parcial/completa/
incompleto), ocultar filas M redundantes, búsqueda (caso/cédula/nombre) y orden.
"""
import os
import re
import sys
import unicodedata

# Permitir importar el backend (core/...) ejecutando desde cualquier cwd
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

import pandas as pd
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QColor, QBrush, QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QLabel, QTableView, QHeaderView, QPushButton,
)

from core.columnas_visor import (
    COLS_TO_SHOW, simplificar_header, ancho_columna, ocultar_m_redundantes,
)
from core.validation_checker import verificar_completitud_registro

try:
    from core.unified_extractor import build_clean_full_name
except Exception:
    build_clean_full_name = None


# ---------------------------------------------------------------------------
# Preparación de datos (mismo pipeline que ui.py._populate_treeview)
# ---------------------------------------------------------------------------
def _norm(s) -> str:
    """minúsculas + sin acentos (para búsqueda insensible)."""
    s = str(s).lower()
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _calcular_completitud(dfx: pd.DataFrame) -> dict:
    """Completitud por caso IHQ (reutiliza el verificador del backend).
    Igual criterio que ui.py: solo filas IHQ (no 'M...'); registro con todas las
    columnas; si no hay datos -> True (no marcar rojo)."""
    cache = {}
    if "Numero de caso" not in dfx.columns:
        return cache
    nums = set(dfx["Numero de caso"].dropna().unique())
    ihq = {n for n in nums if not re.match(r"^[Mm]\d", str(n))}
    if not ihq:
        return cache
    sub = dfx[dfx["Numero de caso"].isin(ihq)].drop_duplicates("Numero de caso").fillna("")
    regs = {r["Numero de caso"]: r for r in sub.to_dict("records")}
    for n in ihq:
        reg = regs.get(n)
        if reg is None:
            cache[n] = True
            continue
        try:
            cache[n] = verificar_completitud_registro(n, registro=reg).get("completo", True)
        except Exception:
            cache[n] = True
    return cache


def preparar_datos(df: pd.DataFrame = None) -> dict:
    """Devuelve todo lo que el modelo necesita. Si df es None, carga desde la BD."""
    if df is None:
        from core.database_manager import get_all_records_as_dataframe
        df = get_all_records_as_dataframe()
    if df is None or df.empty:
        return None

    # "Nombre Completo" (fallback si el backend no la trae)
    name_parts = ["Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido"]
    if "Nombre Completo" not in df.columns and build_clean_full_name and all(c in df.columns for c in name_parts):
        def _mk(row):
            try:
                return build_clean_full_name(
                    str(row.get("Primer nombre", "")), str(row.get("Segundo nombre", "")),
                    str(row.get("Primer apellido", "")), str(row.get("Segundo apellido", "")),
                )
            except Exception:
                return ""
        df["Nombre Completo"] = df.apply(_mk, axis=1)

    # Orden por Numero de caso (igual que ui.py)
    if "Numero de caso" in df.columns:
        df = df.sort_values("Numero de caso", ascending=True, na_position="last").reset_index(drop=True)

    # Ocultar filas M redundantes (base = df completo)
    dfx = ocultar_m_redundantes(df, base=df)
    if dfx is None:
        dfx = df
    dfx = dfx.reset_index(drop=True)

    # Colores por fila (parcial / completa / incompleto)
    completitud = _calcular_completitud(dfx)
    estados = dfx["Estado Auditoria IA"].astype(str).tolist() if "Estado Auditoria IA" in dfx.columns else [""] * len(dfx)
    nums = dfx["Numero de caso"].astype(str).tolist() if "Numero de caso" in dfx.columns else [""] * len(dfx)
    row_bg, row_fg = [], []
    for i in range(len(dfx)):
        est = estados[i].strip()
        bg = fg = None
        if est == "PARCIAL":
            bg, fg = "#FFF3CD", "#856404"
        elif est == "COMPLETA":
            bg, fg = "#D4EDDA", "#155724"
        elif completitud.get(nums[i]) is False:
            bg, fg = "#FFE5E5", "#721C24"
        row_bg.append(QColor(bg) if bg else None)
        row_fg.append(QColor(fg) if fg else None)

    # Haystacks para búsqueda (mismas columnas que ui.py.filter_tabla)
    search_cols = [c for c in ["Numero de caso", "N. de identificación", "Nombre Completo",
                               "Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido"]
                   if c in dfx.columns]
    if search_cols:
        haystacks = dfx[search_cols].fillna("").astype(str).agg(" ".join, axis=1).map(_norm).tolist()
    else:
        haystacks = [""] * len(dfx)

    # Columnas a mostrar (orden EXACTO, filtrando las que existan)
    available = [c for c in COLS_TO_SHOW if c in dfx.columns]
    df_view = dfx[available]
    rows = df_view.fillna("").astype(str).values.tolist()

    return {
        "rows": rows,
        "headers": [simplificar_header(c) for c in available],
        "anchos": [ancho_columna(c) for c in available],
        "row_bg": row_bg,
        "row_fg": row_fg,
        "haystacks": haystacks,
        "total": len(rows),
    }


# ---------------------------------------------------------------------------
# Modelo / Proxy / Vista
# ---------------------------------------------------------------------------
class TablaModel(QAbstractTableModel):
    def __init__(self, datos: dict):
        super().__init__()
        self._rows = datos["rows"]
        self._headers = datos["headers"]
        self._ncols = len(self._headers)
        self._row_bg = datos["row_bg"]
        self._row_fg = datos["row_fg"]
        self._haystacks = datos["haystacks"]
        self._font = QFont("Segoe UI", 10)

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else self._ncols

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        r, c = index.row(), index.column()
        if role == Qt.DisplayRole:
            row = self._rows[r]
            return row[c] if c < len(row) else ""
        if role == Qt.BackgroundRole:
            bg = self._row_bg[r] if r < len(self._row_bg) else None
            return QBrush(bg) if bg else None
        if role == Qt.ForegroundRole:
            fg = self._row_fg[r] if r < len(self._row_fg) else None
            return QBrush(fg) if fg else None
        if role == Qt.TextAlignmentRole:
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        if role == Qt.FontRole:
            return self._font
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section] if section < self._ncols else ""
            return str(section + 1)
        return None

    def haystack(self, source_row: int) -> str:
        if 0 <= source_row < len(self._haystacks):
            return self._haystacks[source_row]
        return ""


class BuscadorProxy(QSortFilterProxyModel):
    """Búsqueda por tokens, insensible a mayúsculas/acentos, sobre el haystack
    precomputado (caso/cédula/nombre). Igual semántica que ui.py.filter_tabla."""
    def __init__(self):
        super().__init__()
        self._tokens = []

    def set_query(self, text: str):
        self._tokens = [_norm(t) for t in text.split() if t.strip()]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, parent):
        if not self._tokens:
            return True
        src = self.sourceModel()
        hay = src.haystack(source_row) if hasattr(src, "haystack") else ""
        return all(tok in hay for tok in self._tokens)


class VisorDatos(QMainWindow):
    def __init__(self, datos: dict):
        super().__init__()
        self.setWindowTitle("EVARISIS · Visualizador de Datos (Qt)")
        self.resize(1500, 820)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Barra superior: búsqueda + contador + refrescar
        top = QHBoxLayout()
        top.addWidget(QLabel("🔍"))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Buscar por N° de caso, cédula o nombre…")
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(360)
        top.addWidget(self.search)
        top.addStretch()
        self.lbl_count = QLabel()
        top.addWidget(self.lbl_count)
        self.btn_refresh = QPushButton("🔄 Actualizar")
        top.addWidget(self.btn_refresh)
        layout.addLayout(top)

        # Tabla
        self.table = QTableView()
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableView.SelectRows)
        self.table.setSelectionMode(QTableView.ExtendedSelection)
        self.table.setWordWrap(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.setStyleSheet(
            "QTableView { background: #ffffff; gridline-color: #dcdcdc; "
            "selection-background-color: #BBDEFB; selection-color: black; }"
            "QHeaderView::section { background-color: #E8F5E9; color: #1B5E20; "
            "font: bold 10pt 'Segoe UI'; padding: 4px; border: 1px solid #cfcfcf; }"
        )
        layout.addWidget(self.table)

        # Estado inferior
        self.status = self.statusBar()

        # Datos
        self._cargar_modelo(datos)

        # Conexiones
        self.search.textChanged.connect(self._on_search)
        self.btn_refresh.clicked.connect(self.recargar)

    def _cargar_modelo(self, datos: dict):
        self._anchos = datos["anchos"]
        self.model = TablaModel(datos)
        self.proxy = BuscadorProxy()
        self.proxy.setSourceModel(self.model)
        self.table.setModel(self.proxy)
        for i, w in enumerate(self._anchos):
            self.table.setColumnWidth(i, w)
        self._total = datos["total"]
        self._actualizar_contador()

    def _on_search(self, text: str):
        self.proxy.set_query(text)
        self._actualizar_contador()

    def _actualizar_contador(self):
        visibles = self.proxy.rowCount()
        self.lbl_count.setText(f"Registros: {visibles} / {self._total}")
        self.status.showMessage(f"{visibles} de {self._total} filas")

    def recargar(self):
        self.btn_refresh.setEnabled(False)
        self.status.showMessage("Actualizando desde la base de datos…")
        QApplication.processEvents()
        try:
            datos = preparar_datos()
            if datos:
                self.search.clear()
                self._cargar_modelo(datos)
                self.status.showMessage("Datos actualizados", 4000)
            else:
                self.status.showMessage("La base de datos no devolvió registros", 6000)
        except Exception as e:
            self.status.showMessage(f"Error al actualizar: {e}", 8000)
        finally:
            self.btn_refresh.setEnabled(True)


def _datos_sinteticos() -> pd.DataFrame:
    """Dataset mínimo para autotest headless (no toca la BD)."""
    return pd.DataFrame({
        "Numero de caso": ["IHQ250001", "IHQ250002", "M250003"],
        "N. de identificación": ["111", "222", "222"],
        "Nombre Completo": ["JUAN PEREZ", "ANA GOMEZ", "ANA GOMEZ"],
        "Diagnostico Principal": ["CARCINOMA", "LINFOMA", ""],
        "Diagnostico Coloracion 2": ["", "", "AZUL ALCIAN"],
        "Estado Auditoria IA": ["COMPLETA", "PARCIAL", ""],
        "IHQ_KI-67": ["20%", "", ""],
        "IHQ_MUC2": ["POSITIVO", "", ""],
        "IHQ_CD15": ["", "NEGATIVO", ""],
        "Fecha Ingreso Base de Datos": ["2026-01-01", "2026-01-02", "2026-01-03"],
    })


def main():
    self_test = "--self-test" in sys.argv
    app = QApplication(sys.argv)
    datos = preparar_datos(_datos_sinteticos() if self_test else None)
    if datos is None:
        print("Sin datos para mostrar.")
        return 0
    win = VisorDatos(datos)
    if self_test:
        print(f"SELFTEST OK filas={datos['total']} columnas={len(datos['headers'])} "
              f"headers0={datos['headers'][:3]}")
        return 0
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
