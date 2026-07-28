# -*- coding: utf-8 -*-
"""Adapter DB para soportar SQLite (single-user dev) y MySQL/MariaDB (red multi-user).

V6.9.0 — Migración a MySQL/MariaDB via XAMPP para uso compartido en LAN
del Hospital Universitario del Valle. Múltiples usuarios pueden ver y
modificar los mismos datos en tiempo real.

Configuración en `config/config.ini`:
    [database]
    tipo = mysql              ; o "sqlite" para desarrollo
    host = 192.168.2.172      ; IP del servidor (o localhost si es la misma PC)
    puerto = 3306
    usuario = huv_app
    password = huv2026
    base_datos = huv_oncologia
    charset = utf8mb4

    ; Si tipo = sqlite (modo legacy):
    archivo = data/huv_oncologia_NUEVO.db

Uso:
    from core.db_adapter import get_connection, dialect, ph
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM informes_ihq WHERE \"Numero de caso\" = {ph()}", (caso,))
"""

from __future__ import annotations

import os
import sys
import logging
import sqlite3
import configparser
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import contextmanager


# Singleton de configuración cargada (evita releer config.ini cada vez)
_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def _get_base_path() -> Path:
    """Retorna el directorio base de la app.

    Soporta tanto modo script (desarrollo) como modo PyInstaller onefile
    (cuando la app está empaquetada como .exe).

    - En .exe: el config.ini DEBE estar al lado del .exe (editable por usuario)
    - En script: usa el directorio del proyecto
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller .exe: directorio del ejecutable (editable)
        return Path(sys.executable).parent
    # Modo script: directorio del proyecto (2 niveles arriba de core/)
    return Path(__file__).resolve().parent.parent


def _load_config() -> Dict[str, Any]:
    """Lee config/config.ini → devuelve dict con la sección [database].

    V6.9.0 — En .exe busca config.ini AL LADO del .exe (editable post-instalación).
    Si la sección no existe, asume SQLite legacy con el archivo histórico.
    """
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    base = _get_base_path()
    cfg_path = base / "config" / "config.ini"
    parser = configparser.ConfigParser()
    if cfg_path.exists():
        try:
            parser.read(str(cfg_path), encoding="utf-8")
        except Exception as e:
            logging.warning(f"[db_adapter] No se pudo leer config.ini: {e}")
    else:
        logging.warning(f"[db_adapter] config.ini NO encontrado en: {cfg_path}")

    if not parser.has_section("database"):
        # Modo legacy: SQLite con el archivo original
        _CONFIG_CACHE = {
            "tipo": "sqlite",
            "archivo": str(base / "data" / "huv_oncologia_NUEVO.db"),
        }
        return _CONFIG_CACHE

    sec = parser["database"]
    tipo = sec.get("tipo", "sqlite").lower().strip()
    cfg: Dict[str, Any] = {"tipo": tipo}
    # V6.9.75: interruptor del modelo relacional (fase 1). Por defecto NO, para que
    # una instalación que aún no lo tenga poblado siga leyendo la tabla plana.
    cfg["usar_modelo_relacional"] = sec.getboolean("usar_modelo_relacional",
                                                   fallback=False)
    if tipo == "mysql":
        cfg.update({
            "host": sec.get("host", "127.0.0.1"),
            "puerto": sec.getint("puerto", 3306),
            "usuario": sec.get("usuario", "root"),
            "password": sec.get("password", ""),
            "base_datos": sec.get("base_datos", "huv_oncologia"),
            "charset": sec.get("charset", "utf8mb4"),
        })
    else:
        archivo_cfg = sec.get("archivo", "")
        if archivo_cfg:
            # Si el path no es absoluto, resolverlo relativo al base path
            archivo_path = Path(archivo_cfg)
            if not archivo_path.is_absolute():
                archivo_path = base / archivo_path
            cfg["archivo"] = str(archivo_path)
        else:
            cfg["archivo"] = str(base / "data" / "huv_oncologia_NUEVO.db")

    _CONFIG_CACHE = cfg
    return cfg


def reload_config() -> None:
    """Fuerza relectura del config.ini (útil tras cambios en runtime)."""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


def dialect() -> str:
    """Devuelve 'mysql' o 'sqlite' según la configuración activa."""
    return _load_config()["tipo"]


def ph(n: int = 1) -> str:
    """Devuelve el placeholder de parámetros según el dialecto:
    SQLite usa '?', MySQL/MariaDB usa '%s'.

    Args:
        n: cantidad de placeholders separados por coma. ph(3) = '?, ?, ?' (sqlite).
    """
    p = "?" if dialect() == "sqlite" else "%s"
    return ", ".join([p] * n)


def quote_ident(name: str) -> str:
    """Quote de identificador (columna/tabla) según dialecto.
    SQLite: "Nombre con espacios"
    MySQL: `Nombre con espacios`
    """
    if dialect() == "mysql":
        safe = name.replace("`", "``")
        return f"`{safe}`"
    safe = name.replace('"', '""')
    return f'"{safe}"'


def upsert_sql(table: str, columns: list, pk_column: str) -> str:
    """Construye query UPSERT (insert or replace si existe el PK).

    SQLite: INSERT OR REPLACE
    MySQL: INSERT ... ON DUPLICATE KEY UPDATE col1=VALUES(col1), col2=VALUES(col2)...

    Args:
        table: nombre de la tabla.
        columns: lista de nombres de columnas (incluyendo PK).
        pk_column: nombre de la columna PK (para excluirla del UPDATE).
    """
    cols_quoted = [quote_ident(c) for c in columns]
    placeholders = ", ".join([ph(1)] * len(columns))

    if dialect() == "mysql":
        update_parts = [
            f"{quote_ident(c)} = VALUES({quote_ident(c)})"
            for c in columns if c != pk_column
        ]
        update_clause = ", ".join(update_parts) if update_parts else f"{quote_ident(pk_column)} = {quote_ident(pk_column)}"
        return (
            f"INSERT INTO {quote_ident(table)} ({', '.join(cols_quoted)}) "
            f"VALUES ({placeholders}) "
            f"ON DUPLICATE KEY UPDATE {update_clause}"
        )
    # SQLite
    return (
        f"INSERT OR REPLACE INTO {quote_ident(table)} ({', '.join(cols_quoted)}) "
        f"VALUES ({placeholders})"
    )


def column_type(use_for_pk: bool = False, length: int = 500) -> str:
    """Devuelve el tipo SQL para columnas TEXT según dialecto.

    En MySQL las PKs deben ser VARCHAR (TEXT no se puede indexar como PK).
    En SQLite todo puede ser TEXT.
    """
    if dialect() == "mysql":
        if use_for_pk:
            return f"VARCHAR({length})"
        return "TEXT"
    # SQLite
    return "TEXT"


def get_connection(database: Optional[str] = None):
    """Devuelve conexión a la BD según config.

    Args:
        database: nombre de BD a usar (solo MySQL — para BDs alternativas como
                  la de diagnosticos IA si se quiere separar). Si None, usa la
                  base_datos del config.

    Returns:
        Connection object (pymysql o sqlite3, según dialecto).
    """
    cfg = _load_config()
    if cfg["tipo"] == "mysql":
        import pymysql
        return pymysql.connect(
            host=cfg["host"],
            port=cfg["puerto"],
            user=cfg["usuario"],
            password=cfg["password"],
            database=database or cfg["base_datos"],
            charset=cfg.get("charset", "utf8mb4"),
            autocommit=False,
        )
    # SQLite
    archivo = cfg["archivo"]
    os.makedirs(os.path.dirname(archivo), exist_ok=True)
    return sqlite3.connect(archivo)


@contextmanager
def cursor_ctx(database: Optional[str] = None):
    """Context manager para obtener conexión + cursor y cerrar automáticamente.

    Uso:
        with cursor_ctx() as (conn, cur):
            cur.execute(f"SELECT * FROM informes_ihq WHERE ... = {ph()}", (val,))
            for row in cur.fetchall():
                ...
            conn.commit()
    """
    conn = get_connection(database=database)
    try:
        cur = conn.cursor()
        yield conn, cur
    finally:
        try:
            conn.close()
        except Exception:
            pass


def get_existing_columns(table: str, database: Optional[str] = None) -> set:
    """Devuelve set con nombres de columnas existentes en la tabla.

    Funciona en SQLite (PRAGMA) y MySQL (INFORMATION_SCHEMA).
    """
    cfg = _load_config()
    with cursor_ctx(database=database) as (conn, cur):
        if cfg["tipo"] == "mysql":
            db_name = database or cfg["base_datos"]
            cur.execute(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s",
                (db_name, table),
            )
            return {row[0] for row in cur.fetchall()}
        else:
            cur.execute(f"PRAGMA table_info({quote_ident(table)})")
            return {row[1] for row in cur.fetchall()}


def add_column_if_missing(table: str, col_name: str, col_type: str = None,
                          database: Optional[str] = None) -> bool:
    """Agrega columna a una tabla si no existe (migración soft).

    Args:
        table: nombre tabla.
        col_name: nombre columna a agregar.
        col_type: tipo SQL. Si None, usa TEXT.
        database: nombre BD opcional.

    Returns:
        True si se agregó, False si ya existía.
    """
    existing = get_existing_columns(table, database=database)
    if col_name in existing:
        return False
    tipo_sql = col_type or column_type()
    with cursor_ctx(database=database) as (conn, cur):
        try:
            cur.execute(
                f"ALTER TABLE {quote_ident(table)} "
                f"ADD COLUMN {quote_ident(col_name)} {tipo_sql}"
            )
            conn.commit()
            logging.info(f"[db_adapter] Columna agregada: {table}.{col_name}")
            return True
        except Exception as e:
            logging.warning(f"[db_adapter] No se pudo agregar {table}.{col_name}: {e}")
            return False


if __name__ == "__main__":
    cfg = _load_config()
    print(f"=== Config cargada ===")
    print(f"  Tipo: {cfg['tipo']}")
    if cfg['tipo'] == 'mysql':
        print(f"  Host: {cfg.get('host')}:{cfg.get('puerto')}")
        print(f"  BD: {cfg.get('base_datos')}")
        print(f"  Usuario: {cfg.get('usuario')}")
    else:
        print(f"  Archivo: {cfg.get('archivo')}")

    print(f"\n  Dialect: {dialect()}")
    print(f"  Placeholder(3): {ph(3)}")
    print(f"  Quote ident 'Numero de caso': {quote_ident('Numero de caso')}")

    print(f"\n  UPSERT 3 cols:")
    print(f"  {upsert_sql('test', ['col1', 'col2', 'col3'], 'col1')}")

    print(f"\n  Test conexión...")
    try:
        with cursor_ctx() as (conn, cur):
            if dialect() == "mysql":
                cur.execute("SELECT VERSION()")
                ver = cur.fetchone()[0]
                print(f"  OK — MariaDB/MySQL v{ver}")
            else:
                cur.execute("SELECT sqlite_version()")
                ver = cur.fetchone()[0]
                print(f"  OK — SQLite v{ver}")
    except Exception as e:
        print(f"  FAIL: {e}")
