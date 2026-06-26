# -*- coding: utf-8 -*-
"""
V6.9.45 — Procesador de PDFs de "Coloraciones básicas" (estudios M autónomos).

Flujo (aislado del IHQ; NO toca su pipeline):
  1. Abre el PDF con fitz (texto nativo) y extrae por caso el DIAGNÓSTICO + demografía
     mínima (core.extractors.coloracion_extractor.agrupar_y_extraer).
  2. Empareja cada caso con la BD POR CÉDULA contra una FOTO (snapshot) tomada ANTES de
     guardar nada, para no confundir coloraciones del mismo paciente dentro del lote:
       - cédula aparece 1 sola vez en el lote Y existe 1 registro con esa cédula
         -> escribe 'Diagnostico Coloracion 2' en ESE registro (merge).
       - en cualquier otro caso (sin cédula / no existe / varios registros / varias
         coloraciones del mismo paciente en el lote) -> crea fila nueva con clave = Nº M
         (para NO atribuir el diagnóstico a la muestra equivocada).
  3. Guarda con database_manager.save_records (UPSERT por 'Numero de caso'); solo escribe
     las columnas presentes en cada registro -> el flujo IHQ nunca pisa estos datos.

dry_run=True devuelve el plan (registros + estadísticas) SIN guardar nada.
"""
from __future__ import annotations

import os
import re
import logging
from collections import Counter
from typing import Callable, Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Columnas (nombres EXACTOS de la BD) que lleva una fila nueva de coloración.
_COLS_DEMOGRAFIA = (
    "N. de identificación", "Tipo de documento",
    "Primer nombre", "Segundo nombre", "Primer apellido", "Segundo apellido",
    "Genero", "Edad", "Organo", "Fecha Informe",
)


def _solo_digitos(s: Any) -> str:
    return re.sub(r"\D", "", str(s or ""))


def process_coloracion_file(
    file_path: str,
    dry_run: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    out_numeros: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Procesa un PDF de coloraciones. Devuelve estadísticas (y el plan si dry_run)."""
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

    # Snapshot de la BD ANTES de guardar (cédula -> [Numero de caso])
    from core.database_manager import get_all_records_as_dataframe
    cedula_a_casos: Dict[str, List[str]] = {}
    try:
        df = get_all_records_as_dataframe()
        if "N. de identificación" in df.columns and "Numero de caso" in df.columns:
            for _, r in df.iterrows():
                caso = str(r.get("Numero de caso", "") or "").strip()
                # V6.9.45: NO emparejar contra otras filas de coloración (clave M…);
                # solo contra registros IHQ -> evita que una coloración pise a otra.
                if caso[:1].upper() == "M" and caso[1:2].isdigit():
                    continue
                ced = _solo_digitos(r.get("N. de identificación", ""))
                if ced and caso:
                    cedula_a_casos.setdefault(ced, []).append(caso)
    except Exception as e:
        _log(f"   ⚠️ No se pudo leer la BD para emparejar: {e}")

    # Cuántas veces aparece cada cédula DENTRO del lote
    conteo_lote = Counter(_solo_digitos(c.get("N. de identificación", "")) for c in casos)

    registros: List[Dict[str, Any]] = []
    stats = {"casos": len(casos), "merge": 0, "nuevos": 0, "ambiguos": 0,
             "sin_cedula": 0, "revisar": 0}

    for c in casos:
        ced = _solo_digitos(c.get("N. de identificación", ""))
        dx = c.get("diagnostico_coloracion_2", "") or ""
        if dx == "REVISAR":
            stats["revisar"] += 1
        existentes = cedula_a_casos.get(ced, [])

        rec: Dict[str, Any] = {}
        if ced and conteo_lote[ced] == 1 and len(existentes) == 1:
            # MERGE: escribir SOLO el dx en el registro existente del paciente
            rec["Numero de caso"] = existentes[0]
            rec["Diagnostico Coloracion 2"] = dx
            rec["_accion"] = f"merge→{existentes[0]}"
            stats["merge"] += 1
        else:
            # FILA NUEVA por Nº M (con demografía)
            rec["Numero de caso"] = c["numero_caso"]
            rec["Diagnostico Coloracion 2"] = dx
            for k in _COLS_DEMOGRAFIA:
                if c.get(k):
                    rec[k] = c[k]
            if not ced:
                rec["_accion"] = "nuevo(sin cédula)"
                stats["sin_cedula"] += 1
            elif len(existentes) > 1:
                rec["_accion"] = f"nuevo(cédula con {len(existentes)} registros)"
                stats["ambiguos"] += 1
            elif conteo_lote[ced] > 1:
                rec["_accion"] = "nuevo(varias coloraciones del mismo paciente en el lote)"
                stats["nuevos"] += 1
            else:
                rec["_accion"] = "nuevo"
                stats["nuevos"] += 1
        registros.append(rec)

    if out_numeros is not None:
        out_numeros.extend(r["Numero de caso"] for r in registros)

    if dry_run:
        _log("   [DRY-RUN] No se guarda nada.")
        stats["plan"] = registros
        return stats

    # Guardado real: quitar la clave interna '_accion' antes de persistir
    from core.database_manager import save_records
    limpios = [{k: v for k, v in r.items() if k != "_accion"} for r in registros]
    guardados = save_records(limpios)
    stats["guardados"] = guardados
    _log(f"   ✅ Guardados {guardados} (merge={stats['merge']}, nuevos={stats['nuevos']}, "
         f"ambiguos={stats['ambiguos']}, sin_cédula={stats['sin_cedula']}, revisar={stats['revisar']})")
    return stats


def process_coloracion_batch(
    file_paths: List[str],
    dry_run: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Carga MASIVA y SEGURA de varios PDFs de coloración.

    A diferencia del procesado por-PDF, cuenta las cédulas en TODO el conjunto y
    empareja solo contra registros NO-coloración (IHQ). Así un paciente con varias
    coloraciones recibe UNA FILA por cada una (nunca se pisan); solo se fusiona el caso
    inequívoco: 1 sola coloración del paciente + 1 solo registro IHQ existente.
    """
    def _log(m: str):
        logger.info(m)
        if log_callback:
            try:
                log_callback(m)
            except Exception:
                pass

    import fitz
    from core.extractors.coloracion_extractor import agrupar_y_extraer
    from core.database_manager import get_all_records_as_dataframe, save_records

    # 1) Extraer TODOS los casos de todos los PDFs
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

    # 2) Conteo GLOBAL de cédulas (sobre las coloraciones del lote completo)
    conteo = Counter(_solo_digitos(c.get("N. de identificación", "")) for c in todos)
    # 3) Snapshot de registros IHQ (NO coloración) por cédula
    ihq_por_ced: Dict[str, List[str]] = {}
    try:
        df = get_all_records_as_dataframe()
        for _, r in df.iterrows():
            caso = str(r.get("Numero de caso", "") or "").strip()
            if caso[:1].upper() == "M" and caso[1:2].isdigit():
                continue
            ced = _solo_digitos(r.get("N. de identificación", ""))
            if ced and caso:
                ihq_por_ced.setdefault(ced, []).append(caso)
    except Exception as e:
        _log(f"⚠️ No se pudo leer la BD: {e}")

    registros: List[Dict[str, Any]] = []
    stats = {"pdfs": len(file_paths), "errores_pdf": len(errores), "casos": len(todos),
             "merge": 0, "nuevos": 0, "multi_coloracion": 0, "ambiguos": 0,
             "sin_cedula": 0, "revisar": 0}
    for c in todos:
        ced = _solo_digitos(c.get("N. de identificación", ""))
        dx = c.get("diagnostico_coloracion_2", "") or ""
        if dx == "REVISAR":
            stats["revisar"] += 1
        ihq = ihq_por_ced.get(ced, [])
        rec: Dict[str, Any] = {}
        if ced and conteo[ced] == 1 and len(ihq) == 1:
            rec["Numero de caso"] = ihq[0]
            rec["Diagnostico Coloracion 2"] = dx
            stats["merge"] += 1
        else:
            rec["Numero de caso"] = c["numero_caso"]
            rec["Diagnostico Coloracion 2"] = dx
            for k in _COLS_DEMOGRAFIA:
                if c.get(k):
                    rec[k] = c[k]
            if not ced:
                stats["sin_cedula"] += 1
            elif conteo[ced] > 1:
                stats["multi_coloracion"] += 1
            elif len(ihq) > 1:
                stats["ambiguos"] += 1
            else:
                stats["nuevos"] += 1
        registros.append(rec)

    if dry_run:
        _log(f"[DRY-RUN] {len(registros)} registros planificados (no se guarda).")
        return stats

    total = 0
    for i in range(0, len(registros), 200):
        total += save_records(registros[i:i + 200])
        _log(f"   guardados {min(i + 200, len(registros))}/{len(registros)}…")
    stats["guardados"] = total
    return stats
