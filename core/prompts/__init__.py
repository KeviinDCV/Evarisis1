#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompts para sistema de auditoría IA
Contiene los prompts del sistema en archivos .txt para fácil edición
"""

from pathlib import Path
import logging

def cargar_prompt(nombre_archivo):
    """Carga un prompt desde archivo .txt"""
    try:
        ruta = Path(__file__).parent / nombre_archivo
        with open(ruta, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.info(f"Error cargando prompt {nombre_archivo}: {e}")
        return ""

def get_system_prompt_completa():
    """Retorna el system prompt para auditoría COMPLETA"""
    return cargar_prompt('system_prompt_completa.txt')

def get_system_prompt_parcial():
    """Retorna el system prompt para auditoría PARCIAL"""
    return cargar_prompt('system_prompt_parcial.txt')

def get_system_prompt_comun():
    """Retorna el system prompt COMÚN (usado en ambos modos)"""
    return cargar_prompt('system_prompt_comun.txt')

__all__ = ['get_system_prompt_completa', 'get_system_prompt_parcial', 'get_system_prompt_comun']
