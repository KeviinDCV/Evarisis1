# -*- coding: utf-8 -*-
"""
FASE 0 de la migración a modelo relacional — ONCONOVA / EVARISIS HUV.

QUÉ HACE Y QUÉ NO
─────────────────
Crea el modelo relacional AL LADO del actual y lo puebla desde `informes_ihq`.
NO toca `informes_ihq`. NO cambia nada del programa. Nadie lee las tablas nuevas
todavía. Es reversible por definición: `--eliminar` las borra y no queda rastro.

Al final VERIFICA que desde el modelo nuevo se puede reconstruir la tabla plana
de 189 columnas, celda a celda. Si no cuadra al 100 %, lo dice y falla.

MODELO
──────
  pacientes                18.200  identidad para agrupar (cédula)
  estudios                 22.547  un estudio = una fila de informes_ihq
  biomarcadores               146  catálogo (una fila por columna IHQ_*)
  resultados_biomarcador   ~11.586 solo los valores REALES

DOS DECISIONES QUE VIENEN DE MEDIR, NO DE SUPONER
─────────────────────────────────────────────────
1) Los datos demográficos NO son constantes por paciente: el nombre varía en 9
   pacientes, el género en 2, el tipo de documento en 19 y la edad en 203 (son
   estudios de años distintos). Por eso CADA ESTUDIO conserva los suyos tal como
   los registró ese informe —que además es lo correcto: el informe es un
   documento legal— y `pacientes` guarda solo la identidad para agrupar.

2) Hay DOS formas de "vacío" en los biomarcadores: NULL (3.003.477 celdas) y el
   literal 'N/A' (276.799). Ningún código los distingue (`_NA_DISPLAY` en
   columnas_visor.py trata igual '', 'N/A' y NULL), así que la reconstrucción
   normaliza la ausencia a NULL. La verificación lo reporta aparte y de forma
   explícita: son celdas que cambian de 'N/A' a NULL, no datos que se pierden.

USO
───
    python herramientas_ia/migracion_relacional.py --crear
    python herramientas_ia/migracion_relacional.py --poblar
    python herramientas_ia/migracion_relacional.py --verificar
    python herramientas_ia/migracion_relacional.py --todo
    python herramientas_ia/migracion_relacional.py --eliminar   (revierte)
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_adapter import get_connection  # noqa: E402

TABLA_ORIGEN = "informes_ihq"
TABLAS_NUEVAS = ("resultados_biomarcador", "biomarcadores", "estudios", "pacientes")
NO_BIOMARCADOR = {"IHQ_ORGANO", "IHQ_ESTUDIOS_SOLICITADOS"}
VACIOS = {"", "N/A", "NA", "NAN", "NONE", "NULL", "NO APLICA", "-", "--"}


def _cols_origen(cur):
    cur.execute(f"SHOW COLUMNS FROM `{TABLA_ORIGEN}`")
    return [r[0] for r in cur.fetchall()]


def _partir_columnas(cols):
    """Devuelve (columnas_de_negocio, columnas_de_biomarcador)."""
    bio = [c for c in cols if c.upper().startswith("IHQ_") and c not in NO_BIOMARCADOR]
    negocio = [c for c in cols if c not in bio]
    return negocio, bio


def _norm_ced(v) -> str:
    return "".join(ch for ch in str(v or "") if ch.isdigit())


def _vacio(v) -> bool:
    return v is None or str(v).strip().upper() in VACIOS


# ───────────────────────────── CREAR ─────────────────────────────
def crear(cur):
    negocio, bio = _partir_columnas(_cols_origen(cur))

    cur.execute("""
        CREATE TABLE IF NOT EXISTS pacientes (
            id       INT AUTO_INCREMENT PRIMARY KEY,
            cedula   VARCHAR(32) NULL,
            nombre   VARCHAR(255) NULL,
            UNIQUE KEY uq_pac_cedula (cedula),
            KEY idx_pac_nombre (nombre)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    # `estudios` conserva los nombres EXACTOS de las columnas actuales: la fase 0
    # cambia la ESTRUCTURA, no la nomenclatura. Así la reconstrucción es 1:1 y no
    # hay lugar para errores de mapeo.
    defs = ",\n            ".join(f"`{c}` LONGTEXT NULL" for c in negocio
                                  if c != "Numero de caso")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS estudios (
            id            INT AUTO_INCREMENT PRIMARY KEY,
            `Numero de caso` VARCHAR(64) NOT NULL,
            paciente_id   INT NOT NULL,
            tipo          VARCHAR(16) NOT NULL,
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
    print(f"  tablas creadas  ·  estudios lleva {len(negocio)} columnas de negocio "
          f"(las 189 originales menos {len(bio)} de biomarcador)")


# ───────────────────────────── POBLAR ─────────────────────────────
def poblar(cur):
    cols = _cols_origen(cur)
    negocio, bio = _partir_columnas(cols)
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in cols)} FROM `{TABLA_ORIGEN}`")
    filas = cur.fetchall()
    idx = {c: i for i, c in enumerate(cols)}
    print(f"  leídas {len(filas):,} filas de {TABLA_ORIGEN}")

    # ── pacientes ─────────────────────────────────────────────────
    # Se agrupa SOLO por cédula. Sin cédula fiable NO se fusiona: cada estudio
    # es su propio paciente. Juntar por nombre mezclaría homónimos, y mezclar la
    # historia clínica de dos personas es un error grave, no un detalle.
    por_ced, sueltos = defaultdict(list), []
    for k, f in enumerate(filas):
        ced = _norm_ced(f[idx["N. de identificación"]])
        if len(ced) >= 4:
            por_ced[ced].append(k)
        else:
            sueltos.append(k)

    def _nombre(k):
        if "Nombre Completo" not in idx:
            return ""
        return str(filas[k][idx["Nombre Completo"]] or "").strip()

    pac_rows, pac_de_fila = [], {}
    for ced, ks in por_ced.items():
        # nombre canónico: el del último estudio que lo traiga (el más reciente
        # por número de caso). Los demás quedan intactos en su estudio.
        nom = next((_nombre(k) for k in sorted(
            ks, key=lambda x: str(filas[x][idx["Numero de caso"]]), reverse=True)
            if _nombre(k)), "")
        pac_rows.append((ced, nom or None))
        for k in ks:
            pac_de_fila[k] = ced
    for k in sueltos:
        pac_rows.append((None, _nombre(k) or None))
        pac_de_fila[k] = f"__sin_cedula__{k}"

    cur.executemany("INSERT INTO pacientes (cedula, nombre) VALUES (%s, %s)", pac_rows)
    cur.execute("SELECT id, cedula FROM pacientes WHERE cedula IS NOT NULL")
    id_por_ced = {c: i for i, c in cur.fetchall()}
    cur.execute("SELECT id FROM pacientes WHERE cedula IS NULL ORDER BY id")
    ids_sin_ced = [r[0] for r in cur.fetchall()]
    for pos, k in enumerate(sueltos):
        id_por_ced[f"__sin_cedula__{k}"] = ids_sin_ced[pos]
    print(f"  pacientes: {len(pac_rows):,}  ({len(por_ced):,} con cédula, "
          f"{len(sueltos)} sin cédula fiable — no fusionados)")

    # ── estudios ──────────────────────────────────────────────────
    otras = [c for c in negocio if c != "Numero de caso"]
    sql = (f"INSERT INTO estudios (`Numero de caso`, paciente_id, tipo, "
           f"{', '.join(f'`{c}`' for c in otras)}) "
           f"VALUES ({', '.join(['%s'] * (3 + len(otras)))})")
    lote = []
    for k, f in enumerate(filas):
        num = str(f[idx["Numero de caso"]] or "").strip()
        tipo = "COLORACION" if (num[:1] in "Mm" and num[1:2].isdigit()) else "IHQ"
        lote.append((num, id_por_ced[pac_de_fila[k]], tipo,
                     *(f[idx[c]] for c in otras)))
    cur.executemany(sql, lote)
    cur.execute("SELECT id, `Numero de caso` FROM estudios")
    id_estudio = {n: i for i, n in cur.fetchall()}
    print(f"  estudios: {len(lote):,}")

    # ── biomarcadores + resultados ────────────────────────────────
    cur.executemany("INSERT INTO biomarcadores (columna, nombre) VALUES (%s, %s)",
                    [(c, c[4:]) for c in bio])
    cur.execute("SELECT id, columna FROM biomarcadores")
    id_bio = {c: i for i, c in cur.fetchall()}

    res = []
    for f in filas:
        eid = id_estudio[str(f[idx["Numero de caso"]] or "").strip()]
        for c in bio:
            v = f[idx[c]]
            if not _vacio(v):
                res.append((eid, id_bio[c], str(v)))
    for i in range(0, len(res), 5000):
        cur.executemany("INSERT INTO resultados_biomarcador "
                        "(estudio_id, biomarcador_id, valor) VALUES (%s,%s,%s)",
                        res[i:i + 5000])
    celdas = len(bio) * len(filas)
    print(f"  biomarcadores: {len(bio)} en catálogo")
    print(f"  resultados: {len(res):,} filas  (antes {celdas:,} celdas → "
          f"{100 * len(res) / celdas:.2f}% de ocupación)")


# ─────────────────────────── VERIFICAR ───────────────────────────
def verificar(cur) -> bool:
    """Reconstruye la tabla plana desde el modelo nuevo y la compara celda a celda."""
    cols = _cols_origen(cur)
    negocio, bio = _partir_columnas(cols)

    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in cols)} FROM `{TABLA_ORIGEN}`")
    orig = {}
    idx = {c: i for i, c in enumerate(cols)}
    for f in cur.fetchall():
        orig[str(f[idx["Numero de caso"]] or "").strip()] = f

    otras = [c for c in negocio if c != "Numero de caso"]
    cur.execute(f"SELECT e.`Numero de caso`, "
                f"{', '.join(f'e.`{c}`' for c in otras)} FROM estudios e")
    nuevo_neg = {str(r[0]).strip(): r[1:] for r in cur.fetchall()}

    cur.execute("""SELECT e.`Numero de caso`, b.columna, r.valor
                   FROM resultados_biomarcador r
                   JOIN estudios e ON e.id = r.estudio_id
                   JOIN biomarcadores b ON b.id = r.biomarcador_id""")
    nuevo_bio = defaultdict(dict)
    for num, col, val in cur.fetchall():
        nuevo_bio[str(num).strip()][col] = val

    faltan = set(orig) - set(nuevo_neg)
    sobran = set(nuevo_neg) - set(orig)
    dif_neg, dif_bio, na_a_null = [], [], 0

    for num, f in orig.items():
        if num not in nuevo_neg:
            continue
        for pos, c in enumerate(otras):
            a, b = f[idx[c]], nuevo_neg[num][pos]
            if (a is None) != (b is None) or (a is not None and str(a) != str(b)):
                dif_neg.append((num, c, a, b))
        for c in bio:
            a = f[idx[c]]
            b = nuevo_bio.get(num, {}).get(c)
            if _vacio(a) and b is None:
                # ausencia normalizada: 'N/A' -> NULL. Se cuenta, no es un error.
                if a is not None:
                    na_a_null += 1
                continue
            if str(a) != str(b):
                dif_bio.append((num, c, a, b))

    print("=" * 72)
    print(f"  estudios en origen        : {len(orig):,}")
    print(f"  estudios reconstruidos    : {len(nuevo_neg):,}")
    print(f"  faltan / sobran           : {len(faltan)} / {len(sobran)}")
    print(f"  celdas de negocio distintas    : {len(dif_neg)}")
    print(f"  celdas de biomarcador distintas: {len(dif_bio)}")
    print(f"  ausencias normalizadas 'N/A'→NULL (esperado, no es pérdida): {na_a_null:,}")
    print("=" * 72)
    for n, c, a, b in (dif_neg + dif_bio)[:10]:
        print(f"   ✗ {n} · {c}: origen={str(a)[:40]!r}  nuevo={str(b)[:40]!r}")
    ok = not (faltan or sobran or dif_neg or dif_bio)
    print("  ✅ RECONSTRUCCIÓN EXACTA" if ok else "  ❌ NO CUADRA — no avanzar a la fase 1")
    return ok


def eliminar(cur):
    cur.execute("SET FOREIGN_KEY_CHECKS=0")
    for t in TABLAS_NUEVAS:
        cur.execute(f"DROP TABLE IF EXISTS `{t}`")
    cur.execute("SET FOREIGN_KEY_CHECKS=1")
    print("  tablas nuevas eliminadas — la BD queda como estaba")


def main():
    p = argparse.ArgumentParser(description="Fase 0 de la migración relacional")
    p.add_argument("--crear", action="store_true")
    p.add_argument("--poblar", action="store_true")
    p.add_argument("--verificar", action="store_true")
    p.add_argument("--todo", action="store_true")
    p.add_argument("--eliminar", action="store_true")
    a = p.parse_args()
    if not any(vars(a).values()):
        p.print_help()
        return

    cn = get_connection()
    cur = cn.cursor()
    t0 = time.time()
    try:
        if a.eliminar:
            eliminar(cur); cn.commit(); return
        if a.crear or a.todo:
            print("── CREAR ──"); crear(cur); cn.commit()
        if a.poblar or a.todo:
            print("── POBLAR ──"); poblar(cur); cn.commit()
        if a.verificar or a.todo:
            print("── VERIFICAR ──")
            if not verificar(cur):
                sys.exit(1)
    finally:
        print(f"\n  ({time.time() - t0:.1f}s)  · `{TABLA_ORIGEN}` NO se ha tocado")
        cn.close()


if __name__ == "__main__":
    main()
