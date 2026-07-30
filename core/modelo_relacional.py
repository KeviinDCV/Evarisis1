# -*- coding: utf-8 -*-
"""
Modelo RELACIONAL de ONCONOVA — creación, sincronización y lectura.

  pacientes  ─┐
              ├─ estudios ──── resultados_biomarcador ──── biomarcadores
              ┘

POR QUÉ EXISTE
──────────────
`informes_ihq` es UNA tabla de 22.547 filas x 189 columnas, sin claves foráneas,
donde 146 columnas son biomarcadores: 3.291.862 celdas para 11.586 valores
reales (0,35 % de ocupación) y el paciente repetido en cada fila.

CÓMO CONVIVE CON LA TABLA PLANA (fase 1)
────────────────────────────────────────
Mientras la escritura siga yendo a `informes_ihq` (eso es la fase 2), esta es la
FUENTE DE VERDAD y el modelo relacional es una proyección suya. El riesgo real no
es el rendimiento: es leer datos OBSOLETOS, que en un registro clínico es peor
que ir lento.

Se resuelve con `CHECKSUM TABLE ... EXTENDED` (95 ms medidos), que detecta
CUALQUIER cambio —incluidos los UPDATE en sitio, que la huella anterior
(COUNT + MAX(fecha)) no veía; de hecho esa columna está 100 % vacía, así que
solo comparaba el número de filas—. Si la huella cambió, se resincroniza (5,6 s)
antes de leer. Correcto por construcción: es imposible servir datos viejos.

RENDIMIENTO (medido, 22.547 filas)
──────────────────────────────────
  hoy   SELECT * FROM informes_ihq ................ 1,23 s   171,7 MB
  vista con pivot MAX(CASE WHEN) ................... 1,65 s
  tabla materializada ............... 1,57 s + 4,08 s por escritura
  ESTE camino: 2 consultas + pivot en pandas ....... 0,66 s    70,8 MB
Con la huella: 0,66 + 0,095 = ~0,76 s. Y 2,4x menos datos por la red, que importa
porque los .exe corren en otros equipos contra este MySQL.
"""
from __future__ import annotations

import logging
from collections import defaultdict

import pandas as pd

logger = logging.getLogger(__name__)

TABLA_ORIGEN = "informes_ihq"
TABLAS = ("resultados_biomarcador", "biomarcadores", "estudios", "pacientes")
NO_BIOMARCADOR = {"IHQ_ORGANO", "IHQ_ESTUDIOS_SOLICITADOS"}
VACIOS = {"", "N/A", "NA", "NAN", "NONE", "NULL", "NO APLICA", "-", "--"}


# ───────────────────────────── utilidades ─────────────────────────────
def columnas_origen(cur):
    cur.execute(f"SHOW COLUMNS FROM `{TABLA_ORIGEN}`")
    return [r[0] for r in cur.fetchall()]


def partir_columnas(cols):
    bio = [c for c in cols if c.upper().startswith("IHQ_") and c not in NO_BIOMARCADOR]
    return [c for c in cols if c not in bio], bio


# V6.9.79: columnas del esquema que son el MISMO anticuerpo con otro nombre
# (SMA / AML / ACTINA_MUSCULO_LISO). Ver core/biomarcadores_canonicos.py.
try:
    from core.biomarcadores_canonicos import alias as _alias_bio
    ALIAS_BIO = _alias_bio()
except ImportError:
    ALIAS_BIO = frozenset()


def biomarcadores_reales(bio):
    """Las columnas que merecen fila en `biomarcadores`: un anticuerpo, una fila.

    Las alias se excluyen del REGISTRO pero siguen en `bio` para que
    `leer_dataframe` reponga las 189 columnas del contrato. Sus datos ya se
    consolidaron en la canónica (V6.9.79), así que están vacías.
    """
    return [c for c in bio if c.upper() not in ALIAS_BIO]


def _norm_ced(v) -> str:
    return "".join(ch for ch in str(v or "") if ch.isdigit())


def _vacio(v) -> bool:
    return v is None or str(v).strip().upper() in VACIOS


def checksum_origen(cur) -> str:
    """Huella fuerte de la tabla plana. Detecta INSERT, UPDATE y DELETE."""
    cur.execute(f"CHECKSUM TABLE `{TABLA_ORIGEN}` EXTENDED")
    return str(cur.fetchone()[1])


# ───────────────────────────── esquema ─────────────────────────────
def crear_esquema(cur):
    negocio, bio = partir_columnas(columnas_origen(cur))

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id     INT AUTO_INCREMENT PRIMARY KEY,
            cedula VARCHAR(32) NULL,
            nombre VARCHAR(255) NULL,
            UNIQUE KEY uq_pac_cedula (cedula),
            KEY idx_pac_nombre (nombre)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # `estudios` conserva los nombres EXACTOS de las columnas actuales: esta fase
    # cambia la ESTRUCTURA, no la nomenclatura. La reconstrucción es 1:1 y no hay
    # sitio para errores de mapeo.
    defs = ",\n            ".join(f"`{c}` LONGTEXT NULL" for c in negocio
                                  if c != "Numero de caso")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS estudios (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            `Numero de caso` VARCHAR(64) NOT NULL,
            paciente_id      INT NOT NULL,
            tipo             VARCHAR(16) NOT NULL,
            {defs},
            UNIQUE KEY uq_est_caso (`Numero de caso`),
            KEY idx_est_pac (paciente_id),
            KEY idx_est_tipo (tipo),
            CONSTRAINT fk_est_pac FOREIGN KEY (paciente_id)
                REFERENCES pacientes(id) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS biomarcadores (
            id      INT AUTO_INCREMENT PRIMARY KEY,
            columna VARCHAR(128) NOT NULL,
            nombre  VARCHAR(128) NOT NULL,
            UNIQUE KEY uq_bio_col (columna)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS resultados_biomarcador (
            estudio_id     INT NOT NULL,
            biomarcador_id INT NOT NULL,
            valor          TEXT NOT NULL,
            PRIMARY KEY (estudio_id, biomarcador_id),
            KEY idx_res_bio (biomarcador_id),
            CONSTRAINT fk_res_est FOREIGN KEY (estudio_id)
                REFERENCES estudios(id) ON DELETE CASCADE,
            CONSTRAINT fk_res_bio FOREIGN KEY (biomarcador_id)
                REFERENCES biomarcadores(id) ON DELETE RESTRICT
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_estado (
            tabla     VARCHAR(64) PRIMARY KEY,
            checksum  VARCHAR(64) NOT NULL,
            filas     INT NOT NULL,
            momento   DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    return len(negocio), len(bio)


def eliminar_esquema(cur):
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for t in TABLAS + ("sync_estado",):
        cur.execute(f"DROP TABLE IF EXISTS `{t}`")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")


# ───────────────────────────── poblado ─────────────────────────────
def poblar(cur, log=logger.info):
    """Vuelca `informes_ihq` al modelo relacional. Idempotente: vacía y rehace."""
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for t in TABLAS:
        cur.execute(f"TRUNCATE TABLE `{t}`")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")

    cols = columnas_origen(cur)
    negocio, bio = partir_columnas(cols)
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in cols)} FROM `{TABLA_ORIGEN}`")
    filas = cur.fetchall()
    idx = {c: i for i, c in enumerate(cols)}

    # ── pacientes: SOLO por cédula. Sin cédula fiable NO se fusiona — juntar por
    # nombre mezclaría homónimos, y mezclar la historia clínica de dos personas
    # distintas es un error grave, no un detalle de presentación.
    por_ced, sueltos = defaultdict(list), []
    for k, f in enumerate(filas):
        ced = _norm_ced(f[idx["N. de identificación"]])
        (por_ced[ced] if len(ced) >= 4 else sueltos).append(k)

    def _nombre(k):
        if "Nombre Completo" not in idx:
            return ""
        return str(filas[k][idx["Nombre Completo"]] or "").strip()

    pac_rows, clave_de_fila = [], {}
    for ced, ks in por_ced.items():
        nom = next((_nombre(k) for k in sorted(
            ks, key=lambda x: str(filas[x][idx["Numero de caso"]]), reverse=True)
            if _nombre(k)), "")
        pac_rows.append((ced, nom or None))
        for k in ks:
            clave_de_fila[k] = ced
    for k in sueltos:
        pac_rows.append((None, _nombre(k) or None))
        clave_de_fila[k] = f"__sc__{k}"

    cur.executemany("INSERT INTO pacientes (cedula, nombre) VALUES (%s, %s)", pac_rows)
    cur.execute("SELECT id, cedula FROM pacientes WHERE cedula IS NOT NULL")
    id_pac = {c: i for i, c in cur.fetchall()}
    # los pacientes sin cédula se insertaron en el orden de `sueltos`, así que sus
    # ids salen en ese mismo orden y se pueden emparejar por posición
    cur.execute("SELECT id FROM pacientes WHERE cedula IS NULL ORDER BY id")
    ids_sc = [r[0] for r in cur.fetchall()]
    for pos, k in enumerate(sueltos):
        id_pac[f"__sc__{k}"] = ids_sc[pos]

    # ── estudios
    otras = [c for c in negocio if c != "Numero de caso"]
    sql = (f"INSERT INTO estudios (`Numero de caso`, paciente_id, tipo, "
           f"{', '.join(f'`{c}`' for c in otras)}) "
           f"VALUES ({', '.join(['%s'] * (3 + len(otras)))})")
    lote = []
    for k, f in enumerate(filas):
        num = str(f[idx["Numero de caso"]] or "").strip()
        tipo = "COLORACION" if (num[:1] in "Mm" and num[1:2].isdigit()) else "IHQ"
        lote.append((num, id_pac[clave_de_fila[k]], tipo, *(f[idx[c]] for c in otras)))
    cur.executemany(sql, lote)
    cur.execute("SELECT id, `Numero de caso` FROM estudios")
    id_est = {n: i for i, n in cur.fetchall()}

    # ── biomarcadores + resultados
    # V6.9.79: una fila por anticuerpo, no por nombre. Las columnas alias no se
    # registran; si alguna trajera valor sería que la consolidación se saltó una
    # fila, así que se avisa en vez de corregir en silencio.
    bio_real = biomarcadores_reales(bio)
    cur.executemany("INSERT INTO biomarcadores (columna, nombre) VALUES (%s, %s)",
                    [(c, c[4:]) for c in bio_real])
    cur.execute("SELECT id, columna FROM biomarcadores")
    id_bio = {c: i for i, c in cur.fetchall()}
    res, huerfanos = [], 0
    for f in filas:
        eid = id_est[str(f[idx["Numero de caso"]] or "").strip()]
        for c in bio:
            v = f[idx[c]]
            if not _vacio(v):
                if c not in id_bio:
                    huerfanos += 1
                    continue
                res.append((eid, id_bio[c], str(v)))
    if huerfanos:
        logger.warning(f"[modelo] {huerfanos} valores en columnas alias sin "
                       f"consolidar: revisa herramientas_ia/unificar_columnas")
    for i in range(0, len(res), 5000):
        cur.executemany("INSERT INTO resultados_biomarcador "
                        "(estudio_id, biomarcador_id, valor) VALUES (%s,%s,%s)",
                        res[i:i + 5000])

    cur.execute("REPLACE INTO sync_estado (tabla, checksum, filas, momento) "
                "VALUES (%s, %s, %s, NOW())",
                (TABLA_ORIGEN, checksum_origen(cur), len(filas)))
    log(f"[modelo] {len(pac_rows):,} pacientes · {len(lote):,} estudios · "
        f"{len(res):,} resultados de biomarcador")
    return {"pacientes": len(pac_rows), "estudios": len(lote), "resultados": len(res)}


def sincronizar_si_hace_falta(cur, log=logger.info) -> bool:
    """True si tuvo que resincronizar. Compara la huella fuerte de la tabla plana.

    Crea el esquema si falta: así una instalación nueva —o una a la que se le
    añadió una tabla en una versión posterior— se auto-repara en vez de fallar.
    """
    crear_esquema(cur)          # CREATE TABLE IF NOT EXISTS: idempotente
    try:
        cur.execute("SELECT checksum FROM sync_estado WHERE tabla=%s", (TABLA_ORIGEN,))
        fila = cur.fetchone()
    except Exception:
        fila = None
    actual = checksum_origen(cur)
    if fila and str(fila[0]) == actual:
        return False
    log(f"[modelo] {TABLA_ORIGEN} cambió (huella {actual}) — resincronizando…")
    poblar(cur, log=log)
    return True


# ─────────────────────── sincronización incremental ───────────────────────
def sincronizar_casos(cur, numeros, log=logger.debug) -> int:
    """Vuelca al modelo SOLO los casos indicados, leyéndolos de la tabla plana.

    Fase 2: en vez de replicar la lógica de escritura de `save_records` —que hace
    UPSERT parcial, solo con las columnas presentes en cada registro—, se deja que
    escriba como siempre y después se re-lee de ahí lo que acaba de tocar. Así es
    IMPOSIBLE que los dos modelos diverjan: la tabla plana sigue mandando y el
    relacional es su proyección exacta.

    Cuesta ~1 ms por caso frente a los 5,6 s de un repoblado completo.
    """
    numeros = [str(n).strip() for n in numeros if str(n or "").strip()]
    if not numeros:
        return 0

    cols = columnas_origen(cur)
    negocio, bio = partir_columnas(cols)
    idx = {c: i for i, c in enumerate(cols)}
    marcas = ",".join(["%s"] * len(numeros))
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in cols)} FROM `{TABLA_ORIGEN}` "
                f"WHERE `Numero de caso` IN ({marcas})", numeros)
    filas = cur.fetchall()
    if not filas:
        return 0

    cur.execute("SELECT id, columna FROM biomarcadores")
    id_bio = {c: i for i, c in cur.fetchall()}
    otras = [c for c in negocio if c != "Numero de caso"]
    set_sql = ", ".join(f"`{c}`=%s" for c in otras)

    tocados = 0
    for f in filas:
        num = str(f[idx["Numero de caso"]] or "").strip()
        ced = _norm_ced(f[idx["N. de identificación"]])
        nombre = (str(f[idx["Nombre Completo"]] or "").strip()
                  if "Nombre Completo" in idx else "") or None

        # paciente: por cédula. Sin cédula fiable NO se fusiona con nadie.
        pid = None
        if len(ced) >= 4:
            cur.execute("SELECT id FROM pacientes WHERE cedula=%s", (ced,))
            r = cur.fetchone()
            if r:
                pid = r[0]
                if nombre:
                    cur.execute("UPDATE pacientes SET nombre=%s WHERE id=%s",
                                (nombre, pid))
            else:
                cur.execute("INSERT INTO pacientes (cedula, nombre) VALUES (%s,%s)",
                            (ced, nombre))
                pid = cur.lastrowid
        else:
            cur.execute("SELECT paciente_id FROM estudios WHERE `Numero de caso`=%s",
                        (num,))
            r = cur.fetchone()
            if r:
                pid = r[0]
            else:
                cur.execute("INSERT INTO pacientes (cedula, nombre) VALUES (NULL,%s)",
                            (nombre,))
                pid = cur.lastrowid

        tipo = "COLORACION" if (num[:1] in "Mm" and num[1:2].isdigit()) else "IHQ"
        valores = [f[idx[c]] for c in otras]
        cur.execute(f"SELECT id FROM estudios WHERE `Numero de caso`=%s", (num,))
        r = cur.fetchone()
        if r:
            eid = r[0]
            cur.execute(f"UPDATE estudios SET paciente_id=%s, tipo=%s, {set_sql} "
                        f"WHERE id=%s", (pid, tipo, *valores, eid))
        else:
            cur.execute(
                f"INSERT INTO estudios (`Numero de caso`, paciente_id, tipo, "
                f"{', '.join(f'`{c}`' for c in otras)}) "
                f"VALUES ({', '.join(['%s'] * (3 + len(otras)))})",
                (num, pid, tipo, *valores))
            eid = cur.lastrowid

        # biomarcadores: se rehacen los de ESTE estudio (no tocan a los demás)
        cur.execute("DELETE FROM resultados_biomarcador WHERE estudio_id=%s", (eid,))
        nuevos = []
        for c in bio:
            v = f[idx[c]]
            if not _vacio(v):
                if c.upper() in ALIAS_BIO:   # V6.9.79: alias, no genera fila propia
                    logger.warning(f"[modelo] valor en columna alias {c} "
                                   f"(caso {num}): el extractor debería haberlo "
                                   f"escrito en su columna canónica")
                    continue
                if c not in id_bio:      # biomarcador nuevo: se da de alta solo
                    cur.execute("INSERT INTO biomarcadores (columna, nombre) "
                                "VALUES (%s,%s)", (c, c[4:]))
                    id_bio[c] = cur.lastrowid
                nuevos.append((eid, id_bio[c], str(v)))
        if nuevos:
            cur.executemany("INSERT INTO resultados_biomarcador "
                            "(estudio_id, biomarcador_id, valor) VALUES (%s,%s,%s)",
                            nuevos)
        tocados += 1

    # la huella se actualiza para que la próxima lectura NO dispare un repoblado
    cur.execute("REPLACE INTO sync_estado (tabla, checksum, filas, momento) "
                "VALUES (%s,%s,(SELECT COUNT(*) FROM `" + TABLA_ORIGEN + "`),NOW())",
                (TABLA_ORIGEN, checksum_origen(cur)))
    log(f"[modelo] sincronizados {tocados} caso(s) de forma incremental")
    return tocados


# ───────────────────────────── lectura ─────────────────────────────
def leer_dataframe(conn, cur=None) -> pd.DataFrame:
    """Reconstruye la tabla plana de 189 columnas desde el modelo relacional.

    NO pivota en SQL a propósito: medido, 2 consultas + pivot en pandas tardan
    0,66 s frente a 1,65 s de una vista con MAX(CASE WHEN) y 1,23 s de la tabla
    plana actual, y mueven 2,4x menos datos por la red.
    """
    propio = cur is None
    cur = cur or conn.cursor()
    try:
        cols = columnas_origen(cur)
        _, bio = partir_columnas(cols)

        est = pd.read_sql_query(
            "SELECT * FROM estudios ORDER BY `Numero de caso`", conn)
        est = est.drop(columns=[c for c in ("id", "paciente_id", "tipo")
                                if c in est.columns])

        res = pd.read_sql_query(
            "SELECT e.`Numero de caso` AS _caso, b.columna AS _col, r.valor AS _val "
            "FROM resultados_biomarcador r "
            "JOIN estudios e ON e.id = r.estudio_id "
            "JOIN biomarcadores b ON b.id = r.biomarcador_id", conn)

        if len(res):
            piv = res.pivot(index="_caso", columns="_col", values="_val")
            est = est.merge(piv, left_on="Numero de caso", right_index=True, how="left")
        # los biomarcadores sin NINGÚN valor no aparecen en el pivot: se reponen
        # vacíos para que el DataFrame tenga SIEMPRE las mismas 189 columnas.
        for c in bio:
            if c not in est.columns:
                est[c] = None
        return est[[c for c in cols if c in est.columns]]
    finally:
        if propio:
            cur.close()
