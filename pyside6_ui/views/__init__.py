#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vistas Principales - PySide6
Pantallas principales de la aplicación EVARISIS
"""

from .welcome_view import WelcomeView
from .dashboard_view import DashboardView
from .database_view import DatabaseView
from .audit_view import AuditIAView
from .web_view import WebAutoView

__all__ = [
    "WelcomeView",
    "DashboardView",
    "DatabaseView",
    "AuditIAView",
    "WebAutoView",
]
