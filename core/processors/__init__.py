#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Procesadores principales

Procesadores del flujo de datos:
- ocr_processor: Procesador OCR para PDFs médicos
"""

from .ocr_processor import pdf_to_text_enhanced

__version__ = "4.1.0"
__all__ = ['pdf_to_text_enhanced']
