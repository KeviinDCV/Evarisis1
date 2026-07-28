# -*- coding: utf-8 -*-
"""
V6.9.46 — Procesador de PDFs de "Coloraciones básicas" (estudios M autónomos).

Modelo (AISLADO del IHQ; NO toca su pipeline de extracción):
  1. De cada PDF se extrae SOLO el DIAGNÓSTICO + demografía mínima
     (core.extractors.coloracion_extractor.agrupar_y_extraer).
  2. CADA coloración se guarda como su PROPIA fila M (clave 'Numero de caso' = Nº M).
     Las filas M son la FUENTE DE VERDAD: nunca se pisan ni se pierden, y un paciente con
     varias coloraciones tiene una fila por cada una.
  3. El enlace coloración<->IHQ NO se hace al guardar. Lo hace reconciliar_coloraciones()
     DESPUÉS de importar (independiente del orden de llegada): recalcula la columna
     'Diagnostico Coloracion 2' de las filas IHQ a partir de las filas M, por cédula.

Así da igual si llega primero el PDF de coloración o el de IHQ: la reconciliación los
empareja en cuanto ambos existen, sin pérdida ni sobreescritura (es idempotente).

dry_run=True devuelve el plan/estadísticas SIN guardar nada.
"""
from __future__ import annotations

import os
import re
import logging
from typing import Callable, Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Columnas (nombres EXACTOS de la BD) que lleva una fila de coloración.
_COLS_DEMOGRAFIA = (
    "N. de identificación", "Tipo de documento",
    "Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido",
    "Genero", "Edad", "Organo", "Fecha Informe",
    # V6.9.77: estos CINCO vienen impresos en el informe de coloración y no se
    # copiaban, así que 20.471 filas (el 91% de la BD) los tenían vacíos. Sin esta
    # lista no llegan a la BD aunque el extractor ya los lea.
    "EPS", "Médico tratante", "Servicio",
    "Fecha de ingreso (2. Fecha de la muestra)", "Patologo",
)

# V6.9.55: la descripción REAL del tejido de la coloración (macro/micro del estudio de
# histología) va a columnas PROPIAS ('… Coloracion') para diferenciarla del texto del
# informe IHQ (solicitud/proceso/técnica), que vive en 'Descripcion macro/microscopica'.
# Mapa: clave que devuelve el extractor de coloración -> columna destino en la fila M.
_MAP_DESC_COLORACION = {
    "Descripcion macroscopica": "Descripcion macroscopica Coloracion",
    "Descripcion microscopica": "Descripcion microscopica Coloracion",
}
# V6.9.49/51: campos DERIVADOS del texto (misma semántica del flujo IHQ):
#   Malignidad -> determine_malignancy;  Procedimiento -> CIRUGÍA/BIOPSIA/CONGELACIÓN.
_COLS_DERIVADAS = ("Malignidad", "Procedimiento")

# Texto que se escribe en la columna IHQ cuando el paciente tiene >1 coloración distinta:
# se concatenan TODAS, numeradas y cada una en una línea (se colapsan saltos internos),
# para mostrar el texto COMPLETO en la propia fila IHQ.
def _concatenar_coloraciones(items: List[str]) -> str:
    partes = []
    for i, dx in enumerate(items, 1):
        una_linea = re.sub(r"\s+", " ", dx).strip()
        partes.append(f"{i}) {una_linea}")
    return "  |  ".join(partes)


def _solo_digitos(s: Any) -> str:
    return re.sub(r"\D", "", str(s or ""))


def _es_fila_m(caso: str) -> bool:
    """True si 'Numero de caso' es una fila de coloración (clave M#####)."""
    return len(caso) >= 2 and caso[0] in "Mm" and caso[1].isdigit()


def _dx_real(v: Any) -> str:
    """Normaliza un valor de dx; '' si está vacío/placeholder."""
    s = str(v or "").strip()
    return "" if s.lower() in ("", "nan", "none", "n/a") else s


def process_coloracion_file(
    file_path: str,
    dry_run: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    out_numeros: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Procesa un PDF de coloraciones: crea UNA fila M por caso (clave = Nº M) con su
    diagnóstico y demografía. NO fusiona aquí; el enlace coloración<->IHQ lo hace
    reconciliar_coloraciones() tras importar (independiente del orden)."""
    def _log(msg: str):
        logger.info(msg)
        if log_callback:
            try:
                log_callback(msg)
            except Exception:
                pass

    import fitz  # PyMuPDF
    from core.extractors.coloracion_extractor import agrupar_y_extraer

    _log(f"📄 Abriendo coloraciones: {file_path}")
    doc = fitz.open(file_path)
    paginas = [doc[i].get_text() for i in range(len(doc))]
    doc.close()

    casos = agrupar_y_extraer(paginas)
    _log(f"   {len(paginas)} páginas → {len(casos)} casos de coloración")

    registros: List[Dict[str, Any]] = []
    stats = {"casos": len(casos), "filas": 0, "revisar": 0}
    for c in casos:
        dx = c.get("diagnostico_coloracion_2", "") or ""
        if dx == "REVISAR":
            stats["revisar"] += 1
        rec: Dict[str, Any] = {"Numero de caso": c["numero_caso"],
                               "Diagnostico Coloracion 2": dx}
        for k in _COLS_DEMOGRAFIA + _COLS_DERIVADAS:
            if c.get(k):
                rec[k] = c[k]
        # V6.9.55: descripción real del tejido -> columnas propias de coloración
        for _src, _dst in _MAP_DESC_COLORACION.items():
            if c.get(_src):
                rec[_dst] = c[_src]
        registros.append(rec)

    if out_numeros is not None:
        out_numeros.extend(r["Numero de caso"] for r in registros)

    if dry_run:
        _log("   [DRY-RUN] No se guarda nada.")
        stats["plan"] = registros
        return stats

    from core.database_manager import save_records
    guardados = save_records(registros)
    stats["filas"] = guardados
    _log(f"   ✅ Guardadas {guardados} filas de coloración (revisar={stats['revisar']}).")
    return stats


def process_coloracion_batch(
    file_paths: List[str],
    dry_run: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Carga MASIVA: crea UNA fila M por cada coloración de TODOS los PDFs.
    NO fusiona aquí; llamar reconciliar_coloraciones() al terminar para enlazar por cédula."""
    def _log(m: str):
        logger.info(m)
        if log_callback:
            try:
                log_callback(m)
            except Exception:
                pass

    import fitz
    from core.extractors.coloracion_extractor import agrupar_y_extraer
    from core.database_manager import save_records

    todos: List[Dict[str, Any]] = []
    errores: List[str] = []
    for i, fp in enumerate(file_paths, 1):
        try:
            doc = fitz.open(fp)
            pags = [doc[k].get_text() for k in range(len(doc))]
            doc.close()
            casos = agrupar_y_extraer(pags)
            todos.extend(casos)
            _log(f"[{i}/{len(file_paths)}] {os.path.basename(fp)} → {len(casos)} casos")
        except Exception as e:
            errores.append(os.path.basename(fp))
            _log(f"[{i}/{len(file_paths)}] ⚠️ ERROR {os.path.basename(fp)}: {e}")

    registros: List[Dict[str, Any]] = []
    stats = {"pdfs": len(file_paths), "errores_pdf": len(errores),
             "casos": len(todos), "revisar": 0, "filas": 0}
    for c in todos:
        dx = c.get("diagnostico_coloracion_2", "") or ""
        if dx == "REVISAR":
            stats["revisar"] += 1
        rec: Dict[str, Any] = {"Numero de caso": c["numero_caso"],
                               "Diagnostico Coloracion 2": dx}
        for k in _COLS_DEMOGRAFIA + _COLS_DERIVADAS:
            if c.get(k):
                rec[k] = c[k]
        # V6.9.55: descripción real del tejido -> columnas propias de coloración
        for _src, _dst in _MAP_DESC_COLORACION.items():
            if c.get(_src):
                rec[_dst] = c[_src]
        registros.append(rec)

    if dry_run:
        _log(f"[DRY-RUN] {len(registros)} filas M planificadas (no se guarda).")
        return stats

    total = 0
    for i in range(0, len(registros), 200):
        total += save_records(registros[i:i + 200])
        _log(f"   guardadas {min(i + 200, len(registros))}/{len(registros)}…")
    stats["filas"] = total
    return stats


def reconciliar_coloraciones(
    dry_run: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Enlace coloración<->IHQ INDEPENDIENTE DEL ORDEN.

    Recalcula 'Diagnostico Coloracion 2' en las filas IHQ a partir de las filas M de
    coloración, emparejadas por cédula ('N. de identificación'). Las filas M son la fuente
    de verdad (nunca se tocan aquí). Es idempotente: recalcula desde la fuente cada vez,
    por lo que NUNCA pisa un dx bueno con uno malo.

      - paciente con IHQ + 1 coloración    -> columna IHQ = ese dx
      - paciente con IHQ + >1 coloración    -> columna IHQ = los N diagnósticos concatenados (numerados)
      - paciente con >1 fila IHQ            -> se escribe en TODAS sus filas IHQ
      - paciente sin IHQ                    -> la coloración queda en su fila M (no se toca)

    NOTA: solo ESCRIBE valores no vacíos (save_records ignora vacíos); nunca limpia la
    columna. En el modelo actual eso no hace falta porque toda coloración tiene su fila M.
    """
    def _log(m: str):
        logger.info(m)
        if log_callback:
            try:
                log_callback(m)
            except Exception:
                pass

    from core.database_manager import get_all_records_as_dataframe, save_records

    # V6.9.55: además del diagnóstico, la reconciliación arrastra a la fila IHQ la
    # DESCRIPCIÓN REAL del tejido (macro/micro) tomada de las filas M, a columnas propias
    # '… Coloracion'. Mismo criterio: filas M = fuente de verdad; solo escribe no vacíos.
    _MACRO_COL = "Descripcion macroscopica Coloracion"
    _MICRO_COL = "Descripcion microscopica Coloracion"

    df = get_all_records_as_dataframe()
    m_by_ced: Dict[str, List[tuple]] = {}
    ihq_by_ced: Dict[str, List[tuple]] = {}
    for _, r in df.iterrows():
        caso = str(r.get("Numero de caso", "") or "").strip()
        if not caso:
            continue
        ced = _solo_digitos(r.get("N. de identificación", ""))
        if not ced:
            continue
        if _es_fila_m(caso):
            dx = _dx_real(r.get("Diagnostico Coloracion 2", ""))
            macro = _dx_real(r.get(_MACRO_COL, ""))
            micro = _dx_real(r.get(_MICRO_COL, ""))
            if dx or macro or micro:
                m_by_ced.setdefault(ced, []).append((caso, dx, macro, micro))
        else:
            ihq_by_ced.setdefault(ced, []).append((
                caso,
                _dx_real(r.get("Diagnostico Coloracion 2", "")),
                _dx_real(r.get(_MACRO_COL, "")),
                _dx_real(r.get(_MICRO_COL, "")),
            ))

    def _dedup_concat(valores: List[str]) -> str:
        """Dedupe conservando el orden; concatena numerado si hay >1 distinto."""
        vistos = set(); items: List[str] = []
        for v in valores:
            v = (v or "").strip()
            if v and v not in vistos:
                vistos.add(v)
                items.append(v)
        if not items:
            return ""
        return items[0] if len(items) == 1 else _concatenar_coloraciones(items)

    updates: List[Dict[str, Any]] = []
    stats = {"ihq_actualizados": 0, "pacientes_enlazados": 0, "con_varias": 0,
             "desc_arrastradas": 0}
    for ced, pares in m_by_ced.items():
        ihqs = ihq_by_ced.get(ced, [])
        if not ihqs:
            continue  # paciente sin IHQ: la coloración vive en su fila M
        pares_ord = sorted(pares, key=lambda x: str(x[0]))  # por Nº M (cronológico)
        val_dx = _dedup_concat([p[1] for p in pares_ord])
        val_macro = _dedup_concat([p[2] for p in pares_ord])
        val_micro = _dedup_concat([p[3] for p in pares_ord])
        if len({p[1] for p in pares_ord if p[1]}) > 1:
            stats["con_varias"] += 1
        enlazo = False
        for (ihq_caso, cur_dx, cur_macro, cur_micro) in ihqs:
            upd: Dict[str, Any] = {"Numero de caso": ihq_caso}
            campos = 0
            if val_dx and val_dx != cur_dx:
                upd["Diagnostico Coloracion 2"] = val_dx; campos += 1
            if val_macro and val_macro != cur_macro:
                upd[_MACRO_COL] = val_macro; campos += 1; stats["desc_arrastradas"] += 1
            if val_micro and val_micro != cur_micro:
                upd[_MICRO_COL] = val_micro; campos += 1
            if campos:
                updates.append(upd)
                enlazo = True
        if enlazo:
            stats["pacientes_enlazados"] += 1

    stats["ihq_actualizados"] = len(updates)
    if dry_run:
        stats["updates"] = updates
        _log(f"   [DRY-RUN] {len(updates)} filas IHQ se actualizarían "
             f"({stats['con_varias']} con varias coloraciones).")
        return stats

    if updates:
        for i in range(0, len(updates), 200):
            save_records(updates[i:i + 200])
    _log(f"   🔗 Reconciliación: {len(updates)} filas IHQ actualizadas, "
         f"{stats['con_varias']} con varias coloraciones, "
         f"{stats['desc_arrastradas']} descripciones arrastradas.")
    return stats
