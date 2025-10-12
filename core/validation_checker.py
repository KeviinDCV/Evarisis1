#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Verificación de Completitud de Registros
Verifica si los registros importados tienen todos los campos requeridos

Versión: 1.0.1
Fecha: 5 de octubre de 2025
Autor: Sistema EVARISIS
"""

from typing import Dict, List, Any
import sqlite3
import sys
import os

# Permitir imports cuando se ejecuta como script
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database_manager import DB_FILE

# Definición de campos requeridos para considerar un registro completo
# PRIORIDAD: Datos médicos > Biomarcadores > Datos paciente
# IMPORTANTE: Usar nombres EXACTOS de las columnas de la BD
CAMPOS_REQUERIDOS = {
    # Datos del paciente (BÁSICOS - baja prioridad)
    'paciente': [
        'N. de identificación',
        'Edad',
        'Genero'
    ],

    # Nombres (LÓGICA ESPECIAL: Si hay 1 nombre + 1 apellido = OK)
    'nombres': [
        'Primer nombre',
        'Segundo nombre',
        'Primer apellido',
        'Segundo apellido'
    ],

    # Datos médicos (CRÍTICOS - MÁXIMA PRIORIDAD)
    'medicos': [
        'N. peticion (0. Numero de biopsia)',
        'Fecha Informe',
        'Diagnostico Principal',
        'Factor pronostico',
        'Organo (1. Muestra enviada a patología)',
        'Malignidad'
    ],

    # Biomarcadores (IMPORTANTE - mínimo 2)
    'biomarcadores': [
        'IHQ_RECEPTOR_ESTROGENO',
        'IHQ_RECEPTOR_PROGESTERONOS',
        'IHQ_HER2',
        'IHQ_KI-67',
        'IHQ_P53',
        'IHQ_PDL-1'
    ]
}

# Porcentajes mínimos (CRITERIOS ESTRICTOS)
PORCENTAJE_COMPLETO = 100  # SOLO 100% = completo (CRÍTICO)
BIOMARCADORES_MINIMOS = 2  # Mínimo 2 biomarcadores detectados (HER2 + Ki-67 mínimo)

# Mapeo de biomarcadores en IHQ_ESTUDIOS_SOLICITADOS a columnas de BD
MAPEO_BIOMARCADORES = {
    'RE': 'IHQ_RECEPTOR_ESTROGENO',
    'RECEPTOR ESTROGENICO': 'IHQ_RECEPTOR_ESTROGENO',
    'RECEPTOR ESTROGENO': 'IHQ_RECEPTOR_ESTROGENO',
    'IHQ_RECEPTOR_ESTROGENO': 'IHQ_RECEPTOR_ESTROGENO',

    'RP': 'IHQ_RECEPTOR_PROGESTERONOS',
    'RECEPTOR PROGESTACIONAL': 'IHQ_RECEPTOR_PROGESTERONOS',
    'RECEPTOR PROGESTERONA': 'IHQ_RECEPTOR_PROGESTERONOS',
    'IHQ_RECEPTOR_PROGESTERONOS': 'IHQ_RECEPTOR_PROGESTERONOS',

    'HER2': 'IHQ_HER2',
    'HER-2': 'IHQ_HER2',
    'IHQ_HER2': 'IHQ_HER2',

    'KI-67': 'IHQ_KI-67',
    'KI67': 'IHQ_KI-67',
    'IHQ_KI-67': 'IHQ_KI-67',

    'P53': 'IHQ_P53',
    'IHQ_P53': 'IHQ_P53',

    'PDL1': 'IHQ_PDL-1',
    'PDL-1': 'IHQ_PDL-1',
    'PD-L1': 'IHQ_PDL-1',
    'IHQ_PDL-1': 'IHQ_PDL-1',

    'P16': 'IHQ_P16_ESTADO',
    'IHQ_P16_ESTADO': 'IHQ_P16_ESTADO',

    'P40': 'IHQ_P40_ESTADO',
    'IHQ_P40_ESTADO': 'IHQ_P40_ESTADO',

    'CK7': 'IHQ_CK7',
    'IHQ_CK7': 'IHQ_CK7',

    'CK20': 'IHQ_CK20',
    'IHQ_CK20': 'IHQ_CK20',

    'CDX2': 'IHQ_CDX2',
    'IHQ_CDX2': 'IHQ_CDX2',

    'EMA': 'IHQ_EMA',
    'IHQ_EMA': 'IHQ_EMA',

    'GATA3': 'IHQ_GATA3',
    'IHQ_GATA3': 'IHQ_GATA3',

    'SOX10': 'IHQ_SOX10',
    'IHQ_SOX10': 'IHQ_SOX10',

    'TTF1': 'IHQ_TTF1',
    'TTF-1': 'IHQ_TTF1',
    'IHQ_TTF1': 'IHQ_TTF1',

    'S100': 'IHQ_S100',
    'IHQ_S100': 'IHQ_S100',

    'VIMENTINA': 'IHQ_VIMENTINA',
    'IHQ_VIMENTINA': 'IHQ_VIMENTINA',

    'CHROMOGRANINA': 'IHQ_CHROMOGRANINA',
    'IHQ_CHROMOGRANINA': 'IHQ_CHROMOGRANINA',

    'SYNAPTOPHYSIN': 'IHQ_SYNAPTOPHYSIN',
    'SINAPTOFISINA': 'IHQ_SYNAPTOPHYSIN',
    'IHQ_SYNAPTOPHYSIN': 'IHQ_SYNAPTOPHYSIN',

    'MELAN A': 'IHQ_MELAN_A',
    'MELAN-A': 'IHQ_MELAN_A',
    'IHQ_MELAN_A': 'IHQ_MELAN_A',

    'CD3': 'IHQ_CD3',
    'CD5': 'IHQ_CD5',
    'CD10': 'IHQ_CD10',
    'CD20': 'IHQ_CD20',
    'CD30': 'IHQ_CD30',
    'CD34': 'IHQ_CD34',
    'CD38': 'IHQ_CD38',
    'CD45': 'IHQ_CD45',
    'CD56': 'IHQ_CD56',
    'CD61': 'IHQ_CD61',
    'CD68': 'IHQ_CD68',
    'CD117': 'IHQ_CD117',
    'CD138': 'IHQ_CD138',
}


def verificar_completitud_registro(numero_peticion: str) -> Dict[str, Any]:
    """
    Verifica la completitud de un registro específico

    Args:
        numero_peticion: Número de petición del registro (ej: 'IHQ250001')

    Returns:
        {
            'numero_peticion': str,
            'completo': bool,
            'porcentaje_completitud': float,
            'campos_totales': int,
            'campos_completos': int,
            'campos_faltantes': list,
            'biomarcadores_detectados': int,
            'biomarcadores_faltantes': list,
            'nivel': str,  # 'completo' o 'incompleto'
            'paciente_nombre': str
        }
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Obtener registro completo
        cursor.execute("""
            SELECT * FROM informes_ihq
            WHERE "N. peticion (0. Numero de biopsia)" = ?
        """, (numero_peticion,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return {
                'numero_peticion': numero_peticion,
                'completo': False,
                'error': 'Registro no encontrado'
            }

        # Convertir row a diccionario
        columns = [description[0] for description in cursor.description]
        registro = dict(zip(columns, row))
        conn.close()

        # Analizar completitud
        campos_faltantes = []
        campos_completos = 0
        campos_totales = 0

        # ESPECIAL: Verificar nombres con lógica flexible
        # Si hay al menos 1 nombre Y 1 apellido = OK, NO marcar como incompleto
        primer_nombre = registro.get('Primer nombre', '').strip()
        segundo_nombre = registro.get('Segundo nombre', '').strip()
        primer_apellido = registro.get('Primer apellido', '').strip()
        segundo_apellido = registro.get('Segundo apellido', '').strip()

        tiene_nombre = bool(primer_nombre or segundo_nombre)
        tiene_apellido = bool(primer_apellido or segundo_apellido)

        # Solo marcar nombres como faltantes si NO hay nombre O NO hay apellido
        if not (tiene_nombre and tiene_apellido):
            if not tiene_nombre:
                campos_faltantes.append('Nombres (Primer o Segundo)')
            if not tiene_apellido:
                campos_faltantes.append('Apellidos (Primer o Segundo)')
            # Contar como 1 campo para el cálculo
            campos_totales += 1
        else:
            # Si tiene nombre + apellido, contar como completo
            campos_totales += 1
            campos_completos += 1

        # Verificar campos de paciente (básicos)
        for campo in CAMPOS_REQUERIDOS['paciente']:
            campos_totales += 1
            valor = registro.get(campo, '')
            if valor and valor not in ['', 'NO ENCONTRADO', 'nan', None, 'N/A']:
                campos_completos += 1
            else:
                campos_faltantes.append(campo)

        # Verificar campos médicos (CRÍTICOS - alta prioridad)
        for campo in CAMPOS_REQUERIDOS['medicos']:
            campos_totales += 1
            valor = registro.get(campo, '')
            if valor and valor not in ['', 'NO ENCONTRADO', 'nan', None, 'N/A']:
                campos_completos += 1
            else:
                campos_faltantes.append(campo)

        # Verificar biomarcadores BASADO EN IHQ_ESTUDIOS_SOLICITADOS
        biomarcadores_detectados = 0
        biomarcadores_faltantes = []
        biomarcadores_solicitados = []

        # Obtener estudios solicitados
        estudios_solicitados_raw = registro.get('IHQ_ESTUDIOS_SOLICITADOS', '')

        if estudios_solicitados_raw and estudios_solicitados_raw not in ['', 'N/A', 'NO ENCONTRADO', None]:
            # Parsear la lista de biomarcadores (separados por comas)
            estudios_lista = [e.strip().upper() for e in estudios_solicitados_raw.split(',')]

            # Para cada biomarcador solicitado, verificar si está mapeado
            for estudio in estudios_lista:
                if not estudio or estudio == 'N/A':
                    continue

                # Buscar la columna correspondiente
                columna_bd = MAPEO_BIOMARCADORES.get(estudio)

                if columna_bd:
                    biomarcadores_solicitados.append(estudio)
                    # Verificar si tiene valor en la BD
                    valor = registro.get(columna_bd, '')
                    if valor and valor not in ['', 'NO ENCONTRADO', 'nan', None, 'NO APLICA', 'N/A']:
                        biomarcadores_detectados += 1
                    else:
                        biomarcadores_faltantes.append(f"{estudio} ({columna_bd})")

        # Si no hay estudios solicitados, usar la lista básica de biomarcadores
        if not biomarcadores_solicitados:
            for campo in CAMPOS_REQUERIDOS['biomarcadores']:
                valor = registro.get(campo, '')
                if valor and valor not in ['', 'NO ENCONTRADO', 'nan', None, 'NO APLICA', 'N/A']:
                    biomarcadores_detectados += 1
                else:
                    biomarcadores_faltantes.append(campo)

        # Calcular porcentaje (campos + biomarcadores ponderados)
        # Campos requeridos = 70% del peso
        # Biomarcadores = 30% del peso
        porcentaje_campos = (campos_completos / campos_totales) * 70 if campos_totales > 0 else 0

        # Calcular porcentaje de biomarcadores basado en estudios solicitados
        total_biomarcadores_esperados = len(biomarcadores_solicitados) if biomarcadores_solicitados else len(CAMPOS_REQUERIDOS['biomarcadores'])
        porcentaje_biomarcadores = (biomarcadores_detectados / total_biomarcadores_esperados) * 30 if total_biomarcadores_esperados > 0 else 0
        porcentaje_total = porcentaje_campos + porcentaje_biomarcadores

        # Determinar nivel
        # CRITERIO ESTRICTO: Solo 100% + mínimo 1 biomarcador = completo
        # (Si hay biomarcadores solicitados, TODOS deben estar completos)
        if porcentaje_total == 100.0 and biomarcadores_detectados >= 1:
            nivel = 'completo'
            completo = True
        else:
            nivel = 'incompleto'
            completo = False

        # Construir nombre completo para display
        nombre_display = ""
        if primer_nombre:
            nombre_display += primer_nombre + " "
        if segundo_nombre:
            nombre_display += segundo_nombre + " "
        if primer_apellido:
            nombre_display += primer_apellido + " "
        if segundo_apellido:
            nombre_display += segundo_apellido

        nombre_display = nombre_display.strip() or "Sin nombre completo"

        # Formatear campos faltantes para mostrar - MOSTRAR TODOS, NO USAR "..."
        detalles_faltantes = []
        if campos_faltantes:
            # Mostrar TODOS los campos faltantes, no truncar
            campos_str = ', '.join(campos_faltantes)
            detalles_faltantes.append(f"Campos: {campos_str}")

        if biomarcadores_faltantes:
            # Mostrar TODOS los biomarcadores faltantes, no truncar
            biomarcadores_str = ', '.join(biomarcadores_faltantes)
            detalles_faltantes.append(f"Biomarcadores: {biomarcadores_str}")

        campos_faltantes_detalle = "\n".join(detalles_faltantes) if detalles_faltantes else "Ninguno"

        return {
            'numero_peticion': numero_peticion,
            'completo': completo,
            'nivel': nivel,
            'porcentaje_completitud': round(porcentaje_total, 1),
            'campos_totales': campos_totales,
            'campos_completos': campos_completos,
            'campos_faltantes': campos_faltantes,
            'campos_faltantes_detalle': campos_faltantes_detalle,
            'biomarcadores_detectados': biomarcadores_detectados,
            'biomarcadores_faltantes': biomarcadores_faltantes,
            'paciente_nombre': nombre_display
        }

    except Exception as e:
        print(f"ERROR verificando completitud de {numero_peticion}: {e}")
        return {
            'numero_peticion': numero_peticion,
            'completo': False,
            'error': str(e)
        }


def analizar_batch_registros(numeros_peticion: List[str]) -> Dict[str, List[Dict]]:
    """
    Analiza un lote de registros recién importados

    Args:
        numeros_peticion: Lista de números de petición a analizar

    Returns:
        {
            'completos': [registro1, registro2, ...],
            'incompletos': [registro3, registro4, ...],
            'resumen': {
                'total': int,
                'completos': int,
                'incompletos': int,
                'porcentaje_exito': float
            }
        }
    """
    completos = []
    incompletos = []

    print(f"Analizando completitud de {len(numeros_peticion)} registros...")

    for numero in numeros_peticion:
        resultado = verificar_completitud_registro(numero)

        if 'error' in resultado:
            print(f"   ERROR en {numero}: {resultado['error']}")
            incompletos.append(resultado)
            continue

        if resultado.get('completo', False):
            completos.append(resultado)
            print(f"   OK {numero} - COMPLETO ({resultado['porcentaje_completitud']}%)")
        else:
            incompletos.append(resultado)
            print(f"   WARN {numero} - INCOMPLETO ({resultado['porcentaje_completitud']}%) - Faltan {len(resultado['campos_faltantes'])} campos y {len(resultado['biomarcadores_faltantes'])} biomarcadores")

    total = len(numeros_peticion)
    num_completos = len(completos)
    porcentaje_exito = (num_completos / total * 100) if total > 0 else 0

    print(f"\nResumen:")
    print(f"   Total: {total}")
    print(f"   Completos: {num_completos} ({porcentaje_exito:.1f}%)")
    print(f"   Incompletos: {len(incompletos)} ({100-porcentaje_exito:.1f}%)")

    return {
        'completos': completos,
        'incompletos': incompletos,
        'resumen': {
            'total': total,
            'completos': num_completos,
            'incompletos': len(incompletos),
            'porcentaje_exito': round(porcentaje_exito, 1)
        }
    }


# Test rápido
if __name__ == "__main__":
    print("=" * 70)
    print("TEST DEL VERIFICADOR DE COMPLETITUD")
    print("=" * 70)

    # Obtener algunos registros de la BD para probar
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT "N. peticion (0. Numero de biopsia)"
            FROM informes_ihq
            LIMIT 5
        """)
        registros = [row[0] for row in cursor.fetchall()]
        conn.close()

        if registros:
            print(f"\nEncontrados {len(registros)} registros para probar\n")

            # Test individual
            print("-" * 70)
            print("TEST 1: Verificacion individual")
            print("-" * 70)
            resultado = verificar_completitud_registro(registros[0])
            print(f"\nRegistro: {resultado['numero_peticion']}")
            print(f"   Paciente: {resultado.get('paciente_nombre', 'N/A')}")
            print(f"   Nivel: {resultado.get('nivel', 'desconocido').upper()}")
            print(f"   Completitud: {resultado.get('porcentaje_completitud', 0)}%")
            print(f"   Campos completos: {resultado.get('campos_completos', 0)}/{resultado.get('campos_totales', 0)}")
            print(f"   Biomarcadores: {resultado.get('biomarcadores_detectados', 0)}/{len(CAMPOS_REQUERIDOS['biomarcadores'])}")

            if resultado.get('campos_faltantes'):
                print(f"\n   WARN Campos faltantes ({len(resultado['campos_faltantes'])}):")
                for campo in resultado['campos_faltantes'][:3]:
                    print(f"      - {campo}")
                if len(resultado['campos_faltantes']) > 3:
                    print(f"      ... y {len(resultado['campos_faltantes']) - 3} mas")

            if resultado.get('biomarcadores_faltantes'):
                print(f"\n   WARN Biomarcadores faltantes ({len(resultado['biomarcadores_faltantes'])}):")
                for bio in resultado['biomarcadores_faltantes'][:3]:
                    print(f"      - {bio}")
                if len(resultado['biomarcadores_faltantes']) > 3:
                    print(f"      ... y {len(resultado['biomarcadores_faltantes']) - 3} mas")

            # Test batch
            print(f"\n{'-' * 70}")
            print("TEST 2: Analisis batch")
            print("-" * 70)
            analisis = analizar_batch_registros(registros)

            print(f"\nTEST COMPLETADO EXITOSAMENTE")

        else:
            print("WARN No hay registros en la base de datos para probar")

    except Exception as e:
        print(f"ERROR en test: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 70)
