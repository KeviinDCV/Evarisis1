# -*- coding: utf-8 -*-
"""Replica el loop corregido de _show_version_info contra el TEAM_INFO real."""
import sys
sys.path.insert(0, r"C:\Users\Kechavarro\Desktop\ProyectoHUV9GESTOR_ONCOLOGIA")
from config.version_info import get_full_version_info
vi = get_full_version_info()
role_titles = {'desarrolladores': 'Dev', 'lider_investigacion': 'Lider', 'jefe_gestion_informacion': 'Jefe'}
count = 0
for role_key, role_info in vi['team'].items():
    personas = role_info if isinstance(role_info, list) else [role_info]
    for persona in personas:
        if not isinstance(persona, dict):
            continue
        rd = [("Nombre", persona.get('nombre', 'N/A')),
              ("Cargo", persona.get('cargo', 'N/A')),
              ("Departamento", persona.get('departamento', 'N/A')),
              ("Correo", persona.get('correo', 'N/A'))]
        title = role_titles.get(role_key, persona.get('cargo', role_key))
        count += 1
        print(f"OK [{role_key}] tipo={type(role_info).__name__} -> {persona.get('nombre')}")
print(f"TOTAL secciones equipo: {count} (sin error 'list indices')")
