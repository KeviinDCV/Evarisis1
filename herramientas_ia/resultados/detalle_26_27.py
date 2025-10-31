#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'c:/Users/USUARIO/Desktop/DEBERES HUV/ProyectoHUV9GESTOR_ONCOLOGIA')

from core.database_manager import get_all_records_as_dataframe

df = get_all_records_as_dataframe()

casos = ['IHQ251026', 'IHQ251027']

for caso_num in casos:
    caso = df[df['Numero de caso'] == caso_num].iloc[0]
    print(f"\n{'='*80}")
    print(f"CASO: {caso_num}")
    print(f"{'='*80}")
    print(f"Paciente: {caso['Nombre Completo']}")
    print(f"\nDescripcion Diagnostico:")
    print(f"  {caso['Descripcion Diagnostico'][:500]}...")
    print(f"\nDiagnostico Principal:")
    print(f"  '{caso['Diagnostico Principal']}'")
    print(f"\nDiagnostico Coloracion:")
    print(f"  '{caso['Diagnostico Coloracion']}'")
