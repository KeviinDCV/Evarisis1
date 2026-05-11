"""BD SQLite dedicada para acumular diagnósticos extraídos por la IA.

V6.7.0 — Pipeline alternativo: el botón "🤖 Procesar con IA" pasa el OCR
completo de cada PDF al LLM, que identifica todos los IHQ presentes con
sus diagnósticos. Cada extracción se persiste acá para que el usuario
pueda procesar PDFs en sesiones separadas y mantener el acumulado.

V6.8.0 — Schema expandido a 184 columnas (todas las de la BD principal).
La IA extrae el caso COMPLETO con todos los biomarcadores. Si un campo
no aparece en el informe, se guarda "N/A".

Esta BD es PARALELA a la BD principal `huv_oncologia_NUEVO.db` — no la
modifica ni la reemplaza. Sirve como referencia para comparar lo que el
extractor tradicional capturó vs lo que el LLM detecta.
"""

from __future__ import annotations

import os
import sqlite3
import logging
from typing import Optional, Dict, Any

from core.columnas_huv_ia import COLUMNAS_IA


_DB_PATH = os.path.join(os.getcwd(), "data", "diagnosticos_ia.db")

# Columnas extra (metadata del proceso IA, no vienen del LLM)
_META_COLUMNS = [
    "pdf_origen",
    "fecha_procesamiento",
    "modelo_utilizado",
    "ocr_caracteres_pdf",
]


def _get_db_path() -> str:
    return _DB_PATH


def _quote_col(col: str) -> str:
    """Escapa nombre de columna con comillas dobles para SQLite."""
    safe = col.replace('"', '""')
    return f'"{safe}"'


def init_db() -> str:
    """Crea la BD y la tabla con TODAS las columnas (184 + metadata).
    Idempotente. Si la tabla ya existe con esquema antiguo, agrega las
    columnas faltantes con ALTER TABLE.

    Returns:
        Ruta absoluta de la BD.
    """
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        # Construir CREATE TABLE con todas las columnas
        # PK = "Numero de caso" (que reemplaza al antiguo numero_peticion)
        col_defs = []
        for col in COLUMNAS_IA:
            quoted = _quote_col(col)
            if col == "Numero de caso":
                col_defs.append(f'{quoted} TEXT PRIMARY KEY')
            else:
                col_defs.append(f'{quoted} TEXT')
        # Metadata columnas
        col_defs.append('"pdf_origen" TEXT')
        col_defs.append('"fecha_procesamiento" TEXT')
        col_defs.append('"modelo_utilizado" TEXT')
        col_defs.append('"ocr_caracteres_pdf" INTEGER')

        ddl = (
            "CREATE TABLE IF NOT EXISTS diagnosticos_ia (\n  "
            + ",\n  ".join(col_defs)
            + "\n)"
        )
        conn.execute(ddl)

        # Migración: si la tabla existía con esquema antiguo, agregar
        # columnas que falten via ALTER TABLE.
        cur = conn.execute("PRAGMA table_info(diagnosticos_ia)")
        existing_cols = {row[1] for row in cur.fetchall()}
        all_expected = set(COLUMNAS_IA) | set(_META_COLUMNS)
        missing = all_expected - existing_cols
        for col in missing:
            try:
                conn.execute(f'ALTER TABLE diagnosticos_ia ADD COLUMN {_quote_col(col)} TEXT')
                logging.info(f"[diagnosticos_ia_db] Columna agregada: {col!r}")
            except sqlite3.OperationalError as e:
                logging.warning(f"[diagnosticos_ia_db] No se pudo agregar {col!r}: {e}")

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pdf_origen
            ON diagnosticos_ia(pdf_origen)
        """)
        conn.commit()
    finally:
        conn.close()
    return db_path


def save_caso_completo(
    datos_columnas: Dict[str, str],
    pdf_origen: str,
    fecha_procesamiento: str,
    modelo_utilizado: Optional[str] = None,
    ocr_caracteres_pdf: Optional[int] = None,
) -> bool:
    """Persiste un caso IHQ completo (184 columnas) en la BD.

    INSERT OR REPLACE por "Numero de caso". Si el mismo IHQ ya existe,
    sobrescribe.

    Args:
        datos_columnas: dict con keys = nombres de columnas BD originales
                        (ver COLUMNAS_IA), values = strings extraídos del LLM.
                        Si falta una columna, se guarda "N/A".
        pdf_origen: nombre del PDF de origen.
        fecha_procesamiento: ISO timestamp.
        modelo_utilizado: nombre del modelo LLM usado.
        ocr_caracteres_pdf: tamaño del OCR procesado.

    Returns:
        True si guardó, False si "Numero de caso" vino vacío.
    """
    numero_caso = (datos_columnas.get("Numero de caso") or "").strip()
    if not numero_caso:
        return False

    # Construir filas: una por cada columna de COLUMNAS_IA + metadata
    cols_finales = list(COLUMNAS_IA) + _META_COLUMNS
    valores = []
    for col in COLUMNAS_IA:
        v = datos_columnas.get(col, "N/A")
        if not isinstance(v, str):
            v = str(v) if v is not None else "N/A"
        valores.append(v.strip() or "N/A")
    valores.append(pdf_origen)
    valores.append(fecha_procesamiento)
    valores.append(modelo_utilizado or "")
    valores.append(int(ocr_caracteres_pdf) if ocr_caracteres_pdf is not None else 0)

    placeholders = ",".join(["?"] * len(cols_finales))
    cols_sql = ",".join(_quote_col(c) for c in cols_finales)

    conn = sqlite3.connect(_get_db_path())
    try:
        conn.execute(
            f"INSERT OR REPLACE INTO diagnosticos_ia ({cols_sql}) VALUES ({placeholders})",
            valores,
        )
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"[diagnosticos_ia_db] Error guardando {numero_caso}: {e}")
        return False
    finally:
        conn.close()


# === Compatibilidad con la API anterior (usada por código existente) ===

def save_diagnostico(
    numero_peticion: str,
    diagnostico: str,
    organo: str,
    pdf_origen: str,
    fecha_procesamiento: str,
    modelo_utilizado: Optional[str] = None,
    ocr_caracteres_pdf: Optional[int] = None,
) -> bool:
    """COMPAT V6.7.x — guarda solo los 3 campos clásicos.

    Sigue funcionando para no romper código viejo. Los demás campos
    quedan como "N/A".
    """
    if not numero_peticion or not numero_peticion.strip():
        return False
    datos = {col: "N/A" for col in COLUMNAS_IA}
    datos["Numero de caso"] = numero_peticion.strip().upper()
    datos["Diagnostico Principal"] = (diagnostico or "").strip()
    datos["Organo"] = (organo or "").strip()
    return save_caso_completo(
        datos, pdf_origen, fecha_procesamiento,
        modelo_utilizado, ocr_caracteres_pdf,
    )


def count_total() -> int:
    """Cuenta cuántos casos únicos hay acumulados en la BD."""
    if not os.path.exists(_get_db_path()):
        return 0
    conn = sqlite3.connect(_get_db_path())
    try:
        cur = conn.execute("SELECT COUNT(*) FROM diagnosticos_ia")
        return int(cur.fetchone()[0])
    except Exception:
        return 0
    finally:
        conn.close()


def count_by_pdf() -> dict:
    """Devuelve {pdf_origen: cantidad} para resumen."""
    if not os.path.exists(_get_db_path()):
        return {}
    conn = sqlite3.connect(_get_db_path())
    try:
        cur = conn.execute("""
            SELECT pdf_origen, COUNT(*) as n
            FROM diagnosticos_ia
            GROUP BY pdf_origen
            ORDER BY pdf_origen
        """)
        return {row[0]: row[1] for row in cur.fetchall()}
    finally:
        conn.close()


def get_all_diagnosticos() -> list[dict]:
    """Devuelve todos los casos acumulados como dicts (con todas las
    columnas, para visualizador o export)."""
    if not os.path.exists(_get_db_path()):
        return []
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute('SELECT * FROM diagnosticos_ia ORDER BY "Numero de caso"')
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
