#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validación de Fase 3 v6.0.7 - Expansión de Biomarcadores
Hospital Universitario del Valle
"""

import sys
sys.path.insert(0, 'herramientas_ia')

from auditor_sistema import AuditorSistema

def validar_biomarcadores():
    """Valida el diccionario BIOMARCADORES completo"""

    print("=" * 80)
    print("VALIDACIÓN FASE 3 v6.0.7 - EXPANSIÓN BIOMARCADORES")
    print("=" * 80)
    print()

    # Acceder al diccionario BIOMARCADORES directamente (atributo de clase)
    biomarcadores = AuditorSistema.BIOMARCADORES

    # Estadísticas generales
    total_variantes = len(biomarcadores)
    biomarcadores_unicos = len(set(biomarcadores.values()))

    print(f"ESTADÍSTICAS GENERALES:")
    print(f"  Total de variantes: {total_variantes}")
    print(f"  Biomarcadores únicos: {biomarcadores_unicos}")
    print(f"  Promedio variantes/biomarcador: {total_variantes/biomarcadores_unicos:.1f}")
    print()

    # Contar variantes por biomarcador
    categorias = {}
    for k, v in biomarcadores.items():
        if v not in categorias:
            categorias[v] = []
        categorias[v].append(k)

    # Top 10 con más variantes
    print("TOP 10 BIOMARCADORES CON MÁS VARIANTES:")
    top10 = sorted(categorias.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (bio, variantes) in enumerate(top10, 1):
        print(f"  {i}. {bio}: {len(variantes)} variantes")
        if len(variantes) <= 5:
            print(f"     Variantes: {', '.join(variantes)}")
    print()

    # Validar biomarcadores clave agregados en Fase 3
    biomarcadores_fase3 = [
        ('CD3', 'IHQ_CD3'),
        ('CD20', 'IHQ_CD20'),
        ('BCL2', 'IHQ_BCL2'),
        ('CYCLIN D1', 'IHQ_CYCLIN_D1'),
        ('MLH1', 'IHQ_MLH1'),
        ('MSH2', 'IHQ_MSH2'),
        ('CK AE1/AE3', 'IHQ_CK_AE1_AE3'),
        ('CK5/6', 'IHQ_CK5_6'),
        ('DESMINA', 'IHQ_DESMINA'),
        ('HMB-45', 'IHQ_HMB45'),
        ('MELAN-A', 'IHQ_MELAN_A'),
        ('PSA', 'IHQ_PSA'),
        ('AMACR', 'IHQ_AMACR'),
        ('HEP PAR-1', 'IHQ_HEP_PAR_1'),
        ('DOG1', 'IHQ_DOG1'),
        ('ALK', 'IHQ_ALK'),
    ]

    print("VALIDACIÓN BIOMARCADORES CLAVE FASE 3:")
    errores = 0
    for nombre, columna_esperada in biomarcadores_fase3:
        if nombre in biomarcadores:
            columna_real = biomarcadores[nombre]
            if columna_real == columna_esperada:
                print(f"  OK: {nombre} -> {columna_real}")
            else:
                print(f"  ERROR: {nombre} -> {columna_real} (esperado: {columna_esperada})")
                errores += 1
        else:
            print(f"  ERROR: {nombre} NO ENCONTRADO")
            errores += 1

    print()
    if errores == 0:
        print("VALIDACIÓN EXITOSA: Todos los biomarcadores clave están correctamente mapeados")
    else:
        print(f"ERRORES ENCONTRADOS: {errores}")

    print()
    print("=" * 80)

    # Verificar biomarcadores con múltiples nombres comunes
    print()
    print("BIOMARCADORES CON NOMBRES ALTERNATIVOS COMUNES:")

    alias_importantes = [
        ('CD117', ['C-KIT', 'CKIT']),
        ('MELAN-A', ['MART-1', 'MELANA']),
        ('AMACR', ['RACEMASA', 'P504S']),
        ('NSE', ['ENOLASA']),
    ]

    for principal, alias in alias_importantes:
        if principal in biomarcadores:
            columna = biomarcadores[principal]
            alias_encontrados = [a for a in alias if a in biomarcadores and biomarcadores[a] == columna]
            if len(alias_encontrados) == len(alias):
                print(f"  OK: {principal} con alias {', '.join(alias_encontrados)}")
            else:
                print(f"  PARCIAL: {principal} solo tiene {len(alias_encontrados)}/{len(alias)} alias")

    print()
    print("=" * 80)

    return biomarcadores_unicos, total_variantes

if __name__ == "__main__":
    unicos, variantes = validar_biomarcadores()

    # Resultado final
    print()
    print("RESULTADO FINAL:")
    print(f"  Biomarcadores únicos: {unicos}")
    print(f"  Variantes totales: {variantes}")
    print(f"  Cobertura: {'100%' if unicos >= 93 else f'{unicos/93*100:.1f}%'}")
    print()
