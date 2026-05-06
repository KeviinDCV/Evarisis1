"""BD SQLite dedicada para acumular diagnósticos extraídos por la IA.

V6.7.0 — Pipeline alternativo: el botón "🤖 Procesar con IA" pasa el OCR
completo de cada PDF al LLM, que identifica todos los IHQ presentes con
sus diagnósticos. Cada extracción se persiste acá para que el usuario
pueda procesar PDFs en sesiones separadas y mantener el acumulado.

Esta BD es PARALELA a la BD principal `huv_oncologia_NUEVO.db` — no la
modifica ni la reemplaza. Sirve como referencia para comparar lo que el
extractor tradicional capturó vs lo que el LLM detecta.
"""

from __future__ import annotations

import os
import sqlite3
import logging
from typing import Optional


_DB_PATH = os.path.join(os.getcwd(), "data", "diagnosticos_ia.db")


def _get_db_path() -> str:
    return _DB_PATH


def init_db() -> str:
    """Crea la BD y la tabla si no existen. Idempotente.

    Returns:
        Ruta absoluta de la BD.
    """
    db_path = _get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS diagnosticos_ia (
                numero_peticion       TEXT PRIMARY KEY,
                diagnostico           TEXT NOT NULL,
                organo                TEXT,
                pdf_origen            TEXT NOT NULL,
                fecha_procesamiento   TEXT NOT NULL,
                modelo_utilizado      TEXT,
                ocr_caracteres_pdf    INTEGER
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pdf_origen
            ON diagnosticos_ia(pdf_origen)
        """)
        conn.commit()
    finally:
        conn.close()
    return db_path


def save_diagnostico(
    numero_peticion: str,
    diagnostico: str,
    organo: str,
    pdf_origen: str,
    fecha_procesamiento: str,
    modelo_utilizado: Optional[str] = None,
    ocr_caracteres_pdf: Optional[int] = None,
) -> bool:
    """Persiste un diagnóstico (INSERT OR REPLACE por numero_peticion).

    Si el mismo IHQ aparece de nuevo (re-procesamiento del PDF, otro
    chunk que lo identifica, etc.), se actualiza la fila existente.

    Returns:
        True si se guardó, False si numero_peticion vino vacío.
    """
    if not numero_peticion or not numero_peticion.strip():
        return False
    if not diagnostico:
        diagnostico = ""

    conn = sqlite3.connect(_get_db_path())
    try:
        conn.execute("""
            INSERT OR REPLACE INTO diagnosticos_ia
            (numero_peticion, diagnostico, organo, pdf_origen,
             fecha_procesamiento, modelo_utilizado, ocr_caracteres_pdf)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            numero_peticion.strip().upper(),
            diagnostico.strip(),
            (organo or "").strip(),
            pdf_origen,
            fecha_procesamiento,
            modelo_utilizado,
            ocr_caracteres_pdf,
        ))
        conn.commit()
        return True
    except Exception as e:
        logging.error(f"[diagnosticos_ia_db] Error guardando {numero_peticion}: {e}")
        return False
    finally:
        conn.close()


def count_total() -> int:
    """Cuenta cuántos diagnósticos únicos hay acumulados en la BD."""
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
    """Devuelve {pdf_origen: cantidad_diagnosticos} para resumen."""
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
    """Devuelve todos los diagnósticos acumulados (para visualizador o export)."""
    if not os.path.exists(_get_db_path()):
        return []
    conn = sqlite3.connect(_get_db_path())
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("""
            SELECT * FROM diagnosticos_ia
            ORDER BY numero_peticion
        """)
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
