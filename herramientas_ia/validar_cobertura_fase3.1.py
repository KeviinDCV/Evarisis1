#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validación: Fase 3.1 v6.0.8 - Cobertura 100%

Verifica que el diccionario BIOMARCADORES cubra todas las columnas IHQ_ de la BD.
"""

import sys
import os
import sqlite3

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from herramientas_ia.auditor_sistema import AuditorSistema


def validar_cobertura_completa():
    """Valida que la cobertura sea 100%"""

    print("="*80)
    print("VALIDACIÓN FASE 3.1 v6.0.8 - COBERTURA 100%")
    print("="*80)
    print()

    # 1. Conectar a BD
    bd_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'huv_oncologia_NUEVO.db')

    if not os.path.exists(bd_path):
        print(f"ERROR: Base de datos no encontrada en {bd_path}")
        return False

    conn = sqlite3.connect(bd_path)
    cursor = conn.cursor()

    # 2. Obtener columnas IHQ de la BD
    cursor.execute("PRAGMA table_info(informes_ihq)")
    columnas_bd = [col[1] for col in cursor.fetchall() if col[1].startswith('IHQ_')]

    # 3. Excluir campos meta (no son biomarcadores)
    campos_meta = {'IHQ_ESTUDIOS_SOLICITADOS', 'IHQ_ORGANO'}
    columnas_bd = [c for c in columnas_bd if c not in campos_meta]

    print(f"1. COLUMNAS IHQ EN BD (sin campos meta)")
    print(f"   Total: {len(columnas_bd)}")
    print(f"   Excluidas (campos meta): {len(campos_meta)} - {campos_meta}")
    print()

    # 4. Obtener biomarcadores únicos del diccionario
    biomarcadores_mapeados = set(AuditorSistema.BIOMARCADORES.values())

    print(f"2. BIOMARCADORES MAPEADOS EN DICCIONARIO")
    print(f"   Biomarcadores únicos: {len(biomarcadores_mapeados)}")
    print(f"   Variantes totales: {len(AuditorSistema.BIOMARCADORES)}")
    print()

    # 5. Calcular cobertura
    columnas_bd_set = set(columnas_bd)
    cobertura = len(biomarcadores_mapeados & columnas_bd_set) / len(columnas_bd_set) * 100

    print(f"3. COBERTURA")
    print(f"   Columnas BD a mapear: {len(columnas_bd_set)}")
    print(f"   Biomarcadores en diccionario: {len(biomarcadores_mapeados)}")
    print(f"   Intersección (mapeados correctamente): {len(biomarcadores_mapeados & columnas_bd_set)}")
    print(f"   COBERTURA: {cobertura:.2f}%")
    print()

    # 6. Biomarcadores faltantes en BD
    faltantes_bd = columnas_bd_set - biomarcadores_mapeados
    if faltantes_bd:
        print(f"4. BIOMARCADORES FALTANTES EN DICCIONARIO ({len(faltantes_bd)})")
        for f in sorted(faltantes_bd):
            print(f"   - {f}")
        print()

    # 7. Biomarcadores extra en diccionario (no en BD)
    extra_diccionario = biomarcadores_mapeados - columnas_bd_set
    if extra_diccionario:
        print(f"5. BIOMARCADORES EN DICCIONARIO PERO NO EN BD ({len(extra_diccionario)})")
        print(f"   (Pueden ser futuros o variantes de nomenclatura)")
        for e in sorted(extra_diccionario):
            print(f"   - {e}")
        print()

    # 8. Análisis de variantes por biomarcador
    print(f"6. ESTADÍSTICAS DE VARIANTES")
    variantes_por_biomarcador = {}
    for variante, biomarcador in AuditorSistema.BIOMARCADORES.items():
        if biomarcador not in variantes_por_biomarcador:
            variantes_por_biomarcador[biomarcador] = []
        variantes_por_biomarcador[biomarcador].append(variante)

    # Top 10 biomarcadores con más variantes
    top_variantes = sorted(variantes_por_biomarcador.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    print(f"   Top 10 biomarcadores con más variantes:")
    for biomarcador, variantes in top_variantes:
        print(f"   - {biomarcador}: {len(variantes)} variantes")
        if len(variantes) <= 3:
            print(f"     ({', '.join(variantes)})")
    print()

    # 9. Verificar duplicados en diccionario
    print(f"7. VERIFICACIÓN DE DUPLICADOS")
    variantes_keys = list(AuditorSistema.BIOMARCADORES.keys())
    duplicados = [v for v in variantes_keys if variantes_keys.count(v) > 1]
    if duplicados:
        print(f"   ADVERTENCIA: {len(set(duplicados))} variantes duplicadas encontradas:")
        for d in sorted(set(duplicados)):
            print(f"   - {d}")
    else:
        print(f"   OK: No hay variantes duplicadas")
    print()

    # 10. Resumen final
    print("="*80)
    print("RESUMEN FINAL")
    print("="*80)

    if cobertura >= 100.0 and not faltantes_bd:
        print("STATUS: ✅ COBERTURA 100% ALCANZADA")
        print()
        print(f"✅ Todas las {len(columnas_bd_set)} columnas IHQ están mapeadas")
        print(f"✅ {len(AuditorSistema.BIOMARCADORES)} variantes disponibles")
        print(f"✅ {len(biomarcadores_mapeados)} biomarcadores únicos")
        resultado = True
    else:
        print(f"STATUS: ❌ COBERTURA INCOMPLETA ({cobertura:.2f}%)")
        print()
        print(f"❌ Faltan {len(faltantes_bd)} biomarcadores por mapear")
        resultado = False

    print()
    print("="*80)

    conn.close()
    return resultado


def analizar_fase_3_1():
    """Analiza específicamente los biomarcadores agregados en Fase 3.1"""

    print()
    print("="*80)
    print("ANÁLISIS ESPECÍFICO FASE 3.1")
    print("="*80)
    print()

    # Biomarcadores que DEBERÍAN estar agregados en Fase 3.1
    biomarcadores_fase_3_1 = {
        # Grupo 1: Aliases
        'DESMIN', 'CKAE1AE3', '34BETA', 'HEPAR', 'NAPSIN', 'GLIPICAN', 'RACEMASA', 'TYROSINASE', 'MELANOMA',

        # Grupo 2: Campos específicos
        'P16 ESTADO', 'P16 PORCENTAJE', 'P40 ESTADO',

        # Grupo 3: Linfomas
        'CD1A', 'CD4', 'CD8', 'CD15', 'CD31', 'CD38', 'CD61', 'CD79A', 'CD99',

        # Grupo 4: Mesenquimales
        'SMA', 'MSA', 'GFAP',

        # Grupo 5: Oncogénicos
        'MDM2', 'CDK4', 'C4D',

        # Grupo 6: Virales
        'HHV8', 'LMP1', 'CITOMEGALOVIRUS', 'SV40',

        # Grupo 7: Otros
        'CALRETININA', 'FACTOR VIII', 'NEUN', 'ACTIN', 'B2',
    }

    print(f"Biomarcadores esperados en Fase 3.1: {len(biomarcadores_fase_3_1)}")
    print()

    # Verificar cuáles están presentes
    presentes = []
    faltantes = []

    for biomarcador in biomarcadores_fase_3_1:
        if biomarcador in AuditorSistema.BIOMARCADORES:
            presentes.append(biomarcador)
        else:
            faltantes.append(biomarcador)

    print(f"✅ PRESENTES: {len(presentes)}/{len(biomarcadores_fase_3_1)}")
    print(f"❌ FALTANTES: {len(faltantes)}/{len(biomarcadores_fase_3_1)}")
    print()

    if faltantes:
        print("Biomarcadores NO encontrados en diccionario:")
        for f in sorted(faltantes):
            print(f"  - {f}")
        print()

    # Mapeo de columnas BD para nuevos biomarcadores
    print("Mapeo de nuevos biomarcadores:")
    for biomarcador in sorted(presentes)[:10]:  # Mostrar primeros 10
        columna = AuditorSistema.BIOMARCADORES[biomarcador]
        print(f"  {biomarcador} → {columna}")
    print(f"  ... y {len(presentes)-10} más")
    print()

    return len(faltantes) == 0


if __name__ == '__main__':
    print()
    print("🔍 INICIANDO VALIDACIÓN DE COBERTURA FASE 3.1 v6.0.8")
    print()

    # Ejecutar validación completa
    exito_cobertura = validar_cobertura_completa()

    # Ejecutar análisis específico Fase 3.1
    exito_fase = analizar_fase_3_1()

    # Resultado final
    if exito_cobertura and exito_fase:
        print("="*80)
        print("✅ VALIDACIÓN EXITOSA: FASE 3.1 IMPLEMENTADA CORRECTAMENTE")
        print("="*80)
        sys.exit(0)
    else:
        print("="*80)
        print("❌ VALIDACIÓN FALLIDA: REVISAR ERRORES ARRIBA")
        print("="*80)
        sys.exit(1)
