# -*- coding: utf-8 -*-
"""
CLI de la migración a modelo relacional — ONCONOVA / EVARISIS HUV.

La lógica vive en `core/modelo_relacional.py` (la usa también la app al leer).
Esto es solo la línea de comandos para operarla y verificarla.

    python herramientas_ia/migracion_relacional.py --crear
    python herramientas_ia/migracion_relacional.py --poblar
    python herramientas_ia/migracion_relacional.py --verificar
    python herramientas_ia/migracion_relacional.py --todo
    python herramientas_ia/migracion_relacional.py --eliminar     (revierte)

`informes_ihq` NUNCA se toca: es la fuente de verdad mientras la escritura no
migre (fase 2). El modelo es una proyección suya que se resincroniza sola cuando
la huella de la tabla plana cambia.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.db_adapter import get_connection            # noqa: E402
from core import modelo_relacional as mr              # noqa: E402


def verificar(cur) -> bool:
    """Reconstruye la tabla plana desde el modelo y la compara CELDA A CELDA."""
    from collections import defaultdict

    cols = mr.columnas_origen(cur)
    negocio, bio = mr.partir_columnas(cols)
    idx = {c: i for i, c in enumerate(cols)}

    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in cols)} FROM `{mr.TABLA_ORIGEN}`")
    orig = {str(f[idx["Numero de caso"]] or "").strip(): f for f in cur.fetchall()}

    otras = [c for c in negocio if c != "Numero de caso"]
    cur.execute(f"SELECT e.`Numero de caso`, {', '.join(f'e.`{c}`' for c in otras)} "
                f"FROM estudios e")
    nuevo = {str(r[0]).strip(): r[1:] for r in cur.fetchall()}

    cur.execute("""SELECT e.`Numero de caso`, b.columna, r.valor
                   FROM resultados_biomarcador r
                   JOIN estudios e ON e.id = r.estudio_id
                   JOIN biomarcadores b ON b.id = r.biomarcador_id""")
    nuevo_bio = defaultdict(dict)
    for num, col, val in cur.fetchall():
        nuevo_bio[str(num).strip()][col] = val

    faltan, sobran = set(orig) - set(nuevo), set(nuevo) - set(orig)
    dif, na_null = [], 0
    for num, f in orig.items():
        if num not in nuevo:
            continue
        for pos, c in enumerate(otras):
            a, b = f[idx[c]], nuevo[num][pos]
            if (a is None) != (b is None) or (a is not None and str(a) != str(b)):
                dif.append((num, c, a, b))
        for c in bio:
            a, b = f[idx[c]], nuevo_bio.get(num, {}).get(c)
            if mr._vacio(a) and b is None:
                na_null += 1 if a is not None else 0
                continue
            if str(a) != str(b):
                dif.append((num, c, a, b))

    print("=" * 72)
    print(f"  estudios en origen / reconstruidos : {len(orig):,} / {len(nuevo):,}")
    print(f"  faltan / sobran                    : {len(faltan)} / {len(sobran)}")
    print(f"  CELDAS DISTINTAS                   : {len(dif)}")
    print(f"  ausencias normalizadas 'N/A'→NULL  : {na_null:,}  (esperado, no es pérdida)")
    print("=" * 72)
    for n, c, a, b in dif[:10]:
        print(f"   ✗ {n} · {c}: origen={str(a)[:40]!r}  nuevo={str(b)[:40]!r}")
    ok = not (faltan or sobran or dif)
    print("  ✅ RECONSTRUCCIÓN EXACTA" if ok else "  ❌ NO CUADRA — no avanzar")
    return ok


def main():
    p = argparse.ArgumentParser(description="Migración al modelo relacional")
    for f in ("crear", "poblar", "verificar", "todo", "eliminar"):
        p.add_argument(f"--{f}", action="store_true")
    a = p.parse_args()
    if not any(vars(a).values()):
        p.print_help()
        return

    cn = get_connection()
    cur = cn.cursor()
    t0 = time.time()
    try:
        if a.eliminar:
            mr.eliminar_esquema(cur); cn.commit()
            print("  tablas eliminadas — la BD queda como estaba")
            return
        if a.crear or a.todo:
            neg, bio = mr.crear_esquema(cur); cn.commit()
            print(f"── CREAR ──  estudios: {neg} columnas de negocio "
                  f"(189 originales − {bio} de biomarcador)")
        if a.poblar or a.todo:
            print("── POBLAR ──")
            r = mr.poblar(cur, log=lambda m: print("  " + m)); cn.commit()
            print(f"  {r['pacientes']:,} pacientes · {r['estudios']:,} estudios · "
                  f"{r['resultados']:,} resultados")
        if a.verificar or a.todo:
            print("── VERIFICAR ──")
            if not verificar(cur):
                sys.exit(1)
    finally:
        print(f"\n  ({time.time() - t0:.1f}s)  · `{mr.TABLA_ORIGEN}` NO se ha tocado")
        cn.close()


if __name__ == "__main__":
    main()
