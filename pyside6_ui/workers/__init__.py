#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workers Qt - PySide6
QThread workers para tareas asíncronas pesadas

Este módulo contiene workers para ejecutar operaciones pesadas
sin bloquear la interfaz de usuario:

- OCRWorker: Procesamiento de PDFs con OCR
- ExportWorker: Exportación de datos a Excel
- AuditWorker: Auditoría inteligente de casos
"""

from .ocr_worker import OCRWorker, OCRBatchWorker
from .export_worker import ExportWorker, MultiFormatExportWorker
from .audit_worker import AuditWorker, BatchAuditWorker, RepairWorker

__all__ = [
    # OCR Workers
    "OCRWorker",
    "OCRBatchWorker",

    # Export Workers
    "ExportWorker",
    "MultiFormatExportWorker",

    # Audit Workers
    "AuditWorker",
    "BatchAuditWorker",
    "RepairWorker",
]
