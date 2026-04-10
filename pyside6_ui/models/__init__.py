#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos Qt - PySide6
Arquitectura Model-View para tablas y datos
"""

from .database_model import DatabaseTableModel, FilterProxyModel

__all__ = [
    "DatabaseTableModel",
    "FilterProxyModel",
]
