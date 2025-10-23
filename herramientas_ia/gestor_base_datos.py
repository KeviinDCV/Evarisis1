#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💾 GESTOR DE BASE DE DATOS - Herramienta Consolidada EVARISIS
===============================================================

Consolida 5 herramientas en una sola:
1. cli_herramientas.py - CLI completo
2. consulta_base_datos.py - Consultas y stats
3. listar_tablas_bd.py - Listado de tablas
4. ver_columnas_bd.py - Ver columnas
5. ver_columnas_tabla.py - Ver columnas específicas

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 20 de octubre de 2025
"""

import sys
import os
import sqlite3
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.database_manager import DB_FILE, TABLE_NAME


class GestorBaseDatos:
    """Gestor consolidado de base de datos oncológica"""

    def __init__(self):
        self.db_path = DB_FILE
        self.table_name = TABLE_NAME

        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Base de datos no encontrada: {self.db_path}")

    # ========== CONSULTAS ==========

    def buscar_caso(self, numero_ihq: str, detallado: bool = False) -> Optional[Dict]:
        """Busca un caso por número IHQ"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE "Numero de caso" = ?', (numero_ihq,))
            row = cursor.fetchone()

            if not row:
                print(f"❌ No se encontró el caso {numero_ihq}")
                return None

            datos = dict(row)

            # Mostrar resultados
            print(f"\n{'='*80}")
            print(f"📋 CASO: {numero_ihq}")
            print(f"{'='*80}\n")

            print("PACIENTE:")
            print(f"  Nombre: {datos.get('Primer nombre', '')} {datos.get('Segundo nombre', '')} {datos.get('Primer apellido', '')} {datos.get('Segundo apellido', '')}")
            print(f"  Identificación: {datos.get('N. de identificación', 'N/A')}")
            print(f"  Edad: {datos.get('Edad', 'N/A')} años | Género: {datos.get('Genero', 'N/A')}")
            print(f"  EPS: {datos.get('EPS', 'N/A')}")

            print(f"\nDATOS MÉDICOS:")
            print(f"  Órgano: {datos.get('Organo', 'N/A')}")
            diag = datos.get('Diagnostico Principal', '')
            print(f"  Diagnóstico: {diag[:100]}{'...' if len(diag) > 100 else ''}")
            print(f"  Factor Pronóstico: {datos.get('Factor pronostico', 'N/A')}")

            # Calcular completitud
            campos_llenos = sum(1 for v in datos.values() if v and str(v).strip())
            completitud = (campos_llenos / len(datos) * 100) if len(datos) > 0 else 0
            print(f"  Completitud: {completitud:.1f}%")

            if detallado:
                print(f"\n{'='*80}")
                print("TODOS LOS CAMPOS:")
                for campo, valor in datos.items():
                    if valor and str(valor).strip():
                        val_str = str(valor)[:60]
                        print(f"  {campo}: {val_str}{'...' if len(str(valor)) > 60 else ''}")

            return datos

        finally:
            conn.close()

    def buscar_por_paciente(self, nombre: str) -> List[Dict]:
        """Busca casos por nombre de paciente"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                SELECT "Numero de caso", "Primer nombre", "Primer apellido", "Organo", "Diagnostico Principal"
                FROM {self.table_name}
                WHERE "Primer nombre" LIKE ? OR "Primer apellido" LIKE ?
            ''', (f'%{nombre}%', f'%{nombre}%'))

            resultados = [dict(row) for row in cursor.fetchall()]

            print(f"\n📋 Encontrados {len(resultados)} caso(s) para '{nombre}':\n")
            for caso in resultados:
                print(f"  {caso['Numero de caso']} - {caso.get('Primer nombre', '')} {caso.get('Primer apellido', '')} - {caso.get('Organo', 'N/A')}")

            return resultados

        finally:
            conn.close()

    def buscar_por_organo(self, organo: str) -> List[Dict]:
        """Busca casos por órgano"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            cursor.execute(f'''
                SELECT "Numero de caso", "Primer nombre", "Primer apellido", "Organo", "Diagnostico Principal"
                FROM {self.table_name}
                WHERE "Organo" LIKE ?
            ''', (f'%{organo}%',))

            resultados = [dict(row) for row in cursor.fetchall()]

            print(f"\n📋 Encontrados {len(resultados)} caso(s) de {organo}:\n")
            for caso in resultados:
                diag = caso.get('Diagnostico Principal', '')
                print(f"  {caso['Numero de caso']} - {caso.get('Primer nombre', '')} {caso.get('Primer apellido', '')} - {diag[:50]}")

            return resultados

        finally:
            conn.close()

    # ========== LISTADOS ==========

    def listar_casos(self, limite: Optional[int] = None, orden: str = 'recientes') -> List[Dict]:
        """Lista casos de la BD"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            order_by = '"Numero de caso" DESC' if orden == 'recientes' else '"Numero de caso" ASC'
            limit_clause = f'LIMIT {limite}' if limite else ''

            cursor.execute(f'''
                SELECT "Numero de caso", "Primer nombre", "Primer apellido", "Organo", "Fecha Informe"
                FROM {self.table_name}
                ORDER BY {order_by}
                {limit_clause}
            ''')

            resultados = [dict(row) for row in cursor.fetchall()]

            print(f"\n📋 Casos en base de datos ({len(resultados)}):\n")
            for caso in resultados:
                print(f"  {caso['Numero de caso']} - {caso.get('Primer nombre', '')} {caso.get('Primer apellido', '')} - {caso.get('Organo', 'N/A')} - {caso.get('Fecha Informe', 'N/A')}")

            return resultados

        finally:
            conn.close()

    def listar_biomarcadores(self, numero_ihq: str):
        """Lista biomarcadores de un caso"""
        datos = self.buscar_caso(numero_ihq)

        if not datos:
            return

        print(f"\n{'='*80}")
        print("BIOMARCADORES DETECTADOS:")
        print(f"{'='*80}\n")

        biomarcadores = {k: v for k, v in datos.items() if k.startswith('IHQ_') and v and str(v).strip() and str(v) not in ['N/A', 'nan', 'None', '']}

        if not biomarcadores:
            print("  ⚠️  No se detectaron biomarcadores")
            return

        # Agrupar por categoría
        categorias = {
            'Hormonales': ['IHQ_RECEPTOR_ESTROGENOS', 'IHQ_RECEPTOR_PROGESTERONA'],
            'Crecimiento': ['IHQ_HER2', 'IHQ_KI-67'],
            'MMR': ['IHQ_MLH1', 'IHQ_MSH2', 'IHQ_MSH6', 'IHQ_PMS2'],
            'CD Markers': [k for k in biomarcadores.keys() if k.startswith('IHQ_CD')],
            'Otros': [k for k in biomarcadores.keys() if k not in ['IHQ_RECEPTOR_ESTROGENOS', 'IHQ_RECEPTOR_PROGESTERONA', 'IHQ_HER2', 'IHQ_KI-67', 'IHQ_MLH1', 'IHQ_MSH2', 'IHQ_MSH6', 'IHQ_PMS2'] and not k.startswith('IHQ_CD')]
        }

        for categoria, campos in categorias.items():
            campos_encontrados = {k: biomarcadores[k] for k in campos if k in biomarcadores}
            if campos_encontrados:
                print(f"{categoria}:")
                for campo, valor in campos_encontrados.items():
                    nombre = campo.replace('IHQ_', '').replace('_', ' ')
                    print(f"  - {nombre}: {valor}")
                print()

    # ========== SCHEMA ==========

    def listar_tablas(self):
        """Lista todas las tablas de la BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tablas = [row[0] for row in cursor.fetchall()]

            print(f"\n📊 Tablas en la base de datos ({len(tablas)}):\n")
            for tabla in tablas:
                # Contar registros
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                count = cursor.fetchone()[0]
                print(f"  - {tabla} ({count} registros)")

        finally:
            conn.close()

    def ver_columnas(self, tabla: Optional[str] = None):
        """Ver columnas de una tabla"""
        if not tabla:
            tabla = self.table_name

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = cursor.fetchall()

            print(f"\n📋 Columnas de la tabla '{tabla}' ({len(columnas)}):\n")
            for col in columnas:
                cid, name, tipo, notnull, default, pk = col
                extras = []
                if pk:
                    extras.append("PRIMARY KEY")
                if notnull:
                    extras.append("NOT NULL")
                extras_str = f" [{', '.join(extras)}]" if extras else ""
                print(f"  {cid+1}. {name} ({tipo}){extras_str}")

        finally:
            conn.close()

    # ========== ESTADÍSTICAS ==========

    def estadisticas_globales(self):
        """Genera estadísticas globales de la BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print("📊 ESTADÍSTICAS GLOBALES")
            print(f"{'='*80}\n")

            # Total registros
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total = cursor.fetchone()[0]
            print(f"Total de registros: {total}")

            # Por órgano
            cursor.execute(f'''
                SELECT "Organo", COUNT(*) as count
                FROM {self.table_name}
                WHERE "Organo" IS NOT NULL AND "Organo" != ''
                GROUP BY "Organo"
                ORDER BY count DESC
                LIMIT 10
            ''')

            print(f"\nDistribución por órgano (Top 10):")
            for organo, count in cursor.fetchall():
                porcentaje = (count / total * 100) if total > 0 else 0
                print(f"  - {organo}: {count} ({porcentaje:.1f}%)")

            # Completitud promedio
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            total_columnas = len(cursor.fetchall())

            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()

            completitudes = []
            for row in rows:
                campos_llenos = sum(1 for v in row if v and str(v).strip())
                completitudes.append(campos_llenos / total_columnas * 100)

            prom_completitud = sum(completitudes) / len(completitudes) if completitudes else 0
            print(f"\nCompletitud promedio: {prom_completitud:.1f}%")

        finally:
            conn.close()

    def calcular_completitud(self, numero_ihq: Optional[str] = None):
        """Calcula completitud de un caso o promedio.

        V6.0.5: MEJORADO - Solo cuenta campos REQUERIDOS:
        - Campos críticos obligatorios (diagnóstico, paciente, fechas)
        - Biomarcadores SOLICITADOS (en IHQ_ESTUDIOS_SOLICITADOS)
        - NO cuenta biomarcadores no solicitados como incompletos
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Obtener nombres de columnas
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            columnas_info = cursor.fetchall()
            columnas_nombres = [col[1] for col in columnas_info]

            # Campos críticos obligatorios (siempre se validan)
            campos_criticos = [
                'Numero de caso', 'N. de identificación', 'Edad', 'Genero',
                'Fecha de ingreso (2. Fecha de la muestra)', 'Fecha Informe',
                'Diagnostico Principal', 'Factor pronostico',
                'Organo', 'Descripcion Diagnostico',
                'IHQ_ESTUDIOS_SOLICITADOS'
            ]

            if numero_ihq:
                cursor.execute(f'SELECT * FROM {self.table_name} WHERE "Numero de caso" = ?', (numero_ihq,))
                row = cursor.fetchone()

                if row:
                    # Crear diccionario columna -> valor
                    row_dict = dict(zip(columnas_nombres, row))

                    # Extraer biomarcadores solicitados
                    estudios_solicitados = row_dict.get('IHQ_ESTUDIOS_SOLICITADOS', '')
                    biomarcadores_solicitados = []

                    if estudios_solicitados and estudios_solicitados != 'N/A':
                        # Parsear lista de biomarcadores: "CKAE1E3, CAM5.2, CK7, GFAP, SOX10, SOX100"
                        biomarcadores_raw = [b.strip().upper() for b in estudios_solicitados.split(',')]

                        # Mapear a nombres de columnas IHQ
                        mapeo_biomarcadores = {
                            'CKAE1E3': 'IHQ_CKAE1AE3', 'CKAE1AE3': 'IHQ_CKAE1AE3',
                            'CAM5.2': 'IHQ_CAM52', 'CAM52': 'IHQ_CAM52',
                            'CK7': 'IHQ_CK7', 'CK20': 'IHQ_CK20',
                            'GFAP': 'IHQ_GFAP', 'SOX10': 'IHQ_SOX10', 'SOX100': 'IHQ_SOX10',
                            'S100': 'IHQ_S100', 'HER2': 'IHQ_HER2', 'KI-67': 'IHQ_KI-67',
                            'ER': 'IHQ_RECEPTOR_ESTROGENOS', 'PR': 'IHQ_RECEPTOR_PROGESTERONA',
                            'P16': 'IHQ_P16_ESTADO', 'P40': 'IHQ_P40_ESTADO',
                            'TTF1': 'IHQ_TTF1', 'CDX2': 'IHQ_CDX2', 'EMA': 'IHQ_EMA',
                            'GATA3': 'IHQ_GATA3', 'P53': 'IHQ_P53'
                        }

                        for bio_raw in biomarcadores_raw:
                            if bio_raw in mapeo_biomarcadores:
                                biomarcadores_solicitados.append(mapeo_biomarcadores[bio_raw])

                    # Construir lista de campos requeridos
                    campos_requeridos = campos_criticos + biomarcadores_solicitados

                    # Contar campos llenos
                    campos_llenos = 0
                    campos_vacios = []

                    for campo in campos_requeridos:
                        if campo in row_dict:
                            valor = row_dict[campo]
                            if valor and str(valor).strip() and str(valor).strip().upper() != 'N/A':
                                campos_llenos += 1
                            else:
                                campos_vacios.append(campo)

                    total_requeridos = len(campos_requeridos)
                    completitud = (campos_llenos / total_requeridos * 100) if total_requeridos > 0 else 0

                    print(f"\n{'='*80}")
                    print(f"📊 COMPLETITUD: {numero_ihq}")
                    print(f"{'='*80}")
                    print(f"Completitud: {completitud:.1f}% ({campos_llenos}/{total_requeridos} campos requeridos)")
                    print(f"\nCampos críticos: {len(campos_criticos)}")
                    print(f"Biomarcadores solicitados: {len(biomarcadores_solicitados)}")

                    if campos_vacios:
                        print(f"\n⚠️  Campos vacíos ({len(campos_vacios)}):")
                        for campo in campos_vacios[:10]:  # Mostrar max 10
                            print(f"   - {campo}")
                        if len(campos_vacios) > 10:
                            print(f"   ... y {len(campos_vacios) - 10} más")
                    else:
                        print(f"\n✅ Todos los campos requeridos están completos")

                    print(f"{'='*80}")
                else:
                    print(f"❌ No se encontró {numero_ihq}")
            else:
                # Promedio de todos los casos (simplificado)
                cursor.execute(f"SELECT * FROM {self.table_name}")
                rows = cursor.fetchall()

                completitudes = []
                for row in rows:
                    campos_llenos = sum(1 for v in row if v and str(v).strip() and str(v).strip().upper() != 'N/A')
                    completitudes.append(campos_llenos / len(columnas_nombres) * 100)

                prom = sum(completitudes) / len(completitudes) if completitudes else 0
                print(f"\nCompletitud promedio (estimada): {prom:.1f}%")
                print(f"Casos evaluados: {len(completitudes)}")
                print(f"\nNOTA: Para análisis detallado por caso, usar: --completitud --caso IHQxxxxxx")

        finally:
            conn.close()

    # ========== VERIFICACIÓN ==========

    def verificar_integridad(self):
        """Verifica integridad de la BD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print("🔍 VERIFICACIÓN DE INTEGRIDAD")
            print(f"{'='*80}\n")

            # Verificar archivo
            print(f"✅ Archivo BD existe: {self.db_path}")
            size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            print(f"   Tamaño: {size_mb:.2f} MB")

            # Verificar tabla
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{self.table_name}'")
            if cursor.fetchone():
                print(f"✅ Tabla '{self.table_name}' existe")
            else:
                print(f"❌ Tabla '{self.table_name}' NO existe")
                return

            # Contar registros
            cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")
            total = cursor.fetchone()[0]
            print(f"✅ Registros: {total}")

            # Contar columnas
            cursor.execute(f"PRAGMA table_info({self.table_name})")
            total_columnas = len(cursor.fetchall())
            print(f"✅ Columnas: {total_columnas}")

            # Verificar duplicados
            cursor.execute(f'''
                SELECT "Numero de caso", COUNT(*) as count
                FROM {self.table_name}
                GROUP BY "Numero de caso"
                HAVING count > 1
            ''')
            duplicados = cursor.fetchall()

            if duplicados:
                print(f"\n⚠️  {len(duplicados)} caso(s) duplicado(s):")
                for caso, count in duplicados:
                    print(f"   - {caso}: {count} veces")
            else:
                print(f"✅ Sin duplicados")

            print(f"\n{'='*80}")
            print("✅ INTEGRIDAD VERIFICADA")
            print(f"{'='*80}")

        finally:
            conn.close()

    # ========== EXPORTACIÓN ==========

    def exportar_json(self, datos: Any, nombre_archivo: str):
        """Exporta datos a JSON"""
        output_dir = PROJECT_ROOT / "herramientas_ia" / "resultados"
        output_dir.mkdir(exist_ok=True)

        if not nombre_archivo.endswith('.json'):
            nombre_archivo = f"{nombre_archivo}.json"

        output_path = output_dir / nombre_archivo

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Datos exportados a: {output_path}")

    # ========== FUNCIONALIDADES EXTENDIDAS ==========

    def buscar_avanzado(self, **filtros):
        """
        Búsqueda avanzada con múltiples filtros

        Parámetros:
            organo: str - Órgano específico
            edad_min: int - Edad mínima
            edad_max: int - Edad máxima
            genero: str - Género (M/F)
            eps: str - EPS
            diagnostico: str - Patrón en diagnóstico
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            query = f"SELECT * FROM {self.table_name} WHERE 1=1"
            params = []

            if filtros.get('organo'):
                query += ' AND "Organo" LIKE ?'
                params.append(f"%{filtros['organo']}%")

            if filtros.get('edad_min'):
                query += ' AND CAST("Edad" AS INTEGER) >= ?'
                params.append(int(filtros['edad_min']))

            if filtros.get('edad_max'):
                query += ' AND CAST("Edad" AS INTEGER) <= ?'
                params.append(int(filtros['edad_max']))

            if filtros.get('genero'):
                query += ' AND "Genero" = ?'
                params.append(filtros['genero'])

            if filtros.get('eps'):
                query += ' AND "EPS" LIKE ?'
                params.append(f"%{filtros['eps']}%")

            if filtros.get('diagnostico'):
                query += ' AND "Diagnostico Principal" LIKE ?'
                params.append(f"%{filtros['diagnostico']}%")

            cursor.execute(query, params)
            resultados = cursor.fetchall()

            print(f"\n{'='*80}")
            print(f"🔍 BÚSQUEDA AVANZADA")
            print(f"{'='*80}\n")
            print(f"Filtros aplicados: {filtros}")
            print(f"Resultados encontrados: {len(resultados)}\n")

            if resultados:
                for row in resultados[:10]:  # Limitar a 10 primeros
                    datos = dict(row)
                    print(f"  {datos.get('Numero de caso', 'N/A')} - "
                          f"{datos.get('Primer nombre', '')} {datos.get('Primer apellido', '')} - "
                          f"{datos.get('Organo', 'N/A')}")

                if len(resultados) > 10:
                    print(f"\n  ... y {len(resultados) - 10} más")

            return [dict(r) for r in resultados]

        finally:
            conn.close()

    def buscar_por_fecha_rango(self, fecha_inicio: str, fecha_fin: str):
        """Busca casos en un rango de fechas (formato: YYYY-MM-DD)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Intentar buscar por diferentes campos de fecha
            campos_fecha = ['Fecha recibido', 'Fecha desc. macro', 'Fecha ingreso']

            print(f"\n{'='*80}")
            print(f"📅 BÚSQUEDA POR RANGO DE FECHAS")
            print(f"{'='*80}\n")
            print(f"Rango: {fecha_inicio} → {fecha_fin}\n")

            resultados_totales = []
            for campo_fecha in campos_fecha:
                try:
                    query = f'''
                        SELECT * FROM {self.table_name}
                        WHERE "{campo_fecha}" BETWEEN ? AND ?
                    '''
                    cursor.execute(query, (fecha_inicio, fecha_fin))
                    resultados = cursor.fetchall()

                    if resultados:
                        print(f"📊 Campo '{campo_fecha}': {len(resultados)} casos")
                        resultados_totales.extend([dict(r) for r in resultados])
                except:
                    pass

            # Eliminar duplicados
            casos_unicos = {}
            for r in resultados_totales:
                numero = r.get('Numero de caso')
                if numero and numero not in casos_unicos:
                    casos_unicos[numero] = r

            print(f"\n✅ Total casos únicos: {len(casos_unicos)}")

            if casos_unicos:
                print(f"\nPrimeros 10 casos:")
                for i, (numero, datos) in enumerate(list(casos_unicos.items())[:10], 1):
                    print(f"  {i}. {numero} - {datos.get('Organo', 'N/A')}")

            return list(casos_unicos.values())

        finally:
            conn.close()

    def analizar_tendencias_temporales(self):
        """Analiza tendencias temporales de casos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print(f"📈 ANÁLISIS DE TENDENCIAS TEMPORALES")
            print(f"{'='*80}\n")

            # Casos por órgano
            cursor.execute(f'''
                SELECT "Organo", COUNT(*) as count
                FROM {self.table_name}
                WHERE "Organo" IS NOT NULL AND "Organo" != ""
                GROUP BY "Organo"
                ORDER BY count DESC
            ''')
            organos = cursor.fetchall()

            print("📊 DISTRIBUCIÓN POR ÓRGANO:")
            for organo, count in organos[:10]:
                porcentaje = (count / sum(r[1] for r in organos) * 100)
                print(f"  {organo[:30]:<30} {count:>4} casos ({porcentaje:>5.1f}%)")

            # Casos por género
            cursor.execute(f'''
                SELECT "Genero", COUNT(*) as count
                FROM {self.table_name}
                WHERE "Genero" IS NOT NULL AND "Genero" != ""
                GROUP BY "Genero"
            ''')
            generos = cursor.fetchall()

            print(f"\n📊 DISTRIBUCIÓN POR GÉNERO:")
            total_genero = sum(r[1] for r in generos)
            for genero, count in generos:
                porcentaje = (count / total_genero * 100) if total_genero > 0 else 0
                print(f"  {genero}: {count} casos ({porcentaje:.1f}%)")

            # Rango de edades
            cursor.execute(f'''
                SELECT "Edad"
                FROM {self.table_name}
                WHERE "Edad" IS NOT NULL AND "Edad" != ""
            ''')
            edades = [int(r[0]) for r in cursor.fetchall() if str(r[0]).isdigit()]

            if edades:
                print(f"\n📊 ESTADÍSTICAS DE EDAD:")
                print(f"  Edad promedio: {sum(edades) / len(edades):.1f} años")
                print(f"  Edad mínima: {min(edades)} años")
                print(f"  Edad máxima: {max(edades)} años")
                print(f"  Mediana: {sorted(edades)[len(edades)//2]} años")

        finally:
            conn.close()

    def detectar_anomalias(self):
        """Detecta anomalías en los datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print(f"🔍 DETECCIÓN DE ANOMALÍAS")
            print(f"{'='*80}\n")

            anomalias = []

            # Casos con edad anormal
            cursor.execute(f'''
                SELECT "Numero de caso", "Edad"
                FROM {self.table_name}
                WHERE CAST("Edad" AS INTEGER) > 120 OR CAST("Edad" AS INTEGER) < 0
            ''')
            edades_anomalas = cursor.fetchall()
            if edades_anomalas:
                anomalias.append(f"⚠️  {len(edades_anomalas)} casos con edad anormal")
                for caso, edad in edades_anomalas[:5]:
                    print(f"  - {caso}: {edad} años")

            # Casos sin diagnóstico
            cursor.execute(f'''
                SELECT "Numero de caso"
                FROM {self.table_name}
                WHERE "Diagnostico Principal" IS NULL OR "Diagnostico Principal" = ""
            ''')
            sin_diagnostico = cursor.fetchall()
            if sin_diagnostico:
                anomalias.append(f"⚠️  {len(sin_diagnostico)} casos sin diagnóstico")

            # Casos sin órgano
            cursor.execute(f'''
                SELECT "Numero de caso"
                FROM {self.table_name}
                WHERE "Organo" IS NULL OR "Organo" = ""
            ''')
            sin_organo = cursor.fetchall()
            if sin_organo:
                anomalias.append(f"⚠️  {len(sin_organo)} casos sin órgano")

            # Casos sin nombre de paciente
            cursor.execute(f'''
                SELECT "Numero de caso"
                FROM {self.table_name}
                WHERE ("Primer nombre" IS NULL OR "Primer nombre" = "")
                  AND ("Primer apellido" IS NULL OR "Primer apellido" = "")
            ''')
            sin_nombre = cursor.fetchall()
            if sin_nombre:
                anomalias.append(f"⚠️  {len(sin_nombre)} casos sin nombre de paciente")

            if anomalias:
                print("ANOMALÍAS DETECTADAS:")
                for anomalia in anomalias:
                    print(f"  {anomalia}")
            else:
                print("✅ No se detectaron anomalías")

        finally:
            conn.close()

    def comparar_casos_similares(self, numero_ihq: str):
        """Encuentra casos similares al caso especificado"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Obtener caso de referencia
            cursor.execute(f'SELECT * FROM {self.table_name} WHERE "Numero de caso" = ?', (numero_ihq,))
            caso_ref = cursor.fetchone()

            if not caso_ref:
                print(f"❌ No se encontró el caso {numero_ihq}")
                return

            caso_ref = dict(caso_ref)

            print(f"\n{'='*80}")
            print(f"🔍 CASOS SIMILARES A: {numero_ihq}")
            print(f"{'='*80}\n")
            print(f"Referencia: {caso_ref.get('Organo', 'N/A')} - "
                  f"Edad {caso_ref.get('Edad', 'N/A')} - "
                  f"{caso_ref.get('Genero', 'N/A')}")

            # Buscar casos similares (mismo órgano, edad cercana, mismo género)
            query = f'''
                SELECT *
                FROM {self.table_name}
                WHERE "Numero de caso" != ?
                  AND "Organo" = ?
                  AND "Genero" = ?
                  AND ABS(CAST("Edad" AS INTEGER) - ?) <= 10
            '''

            params = [
                numero_ihq,
                caso_ref.get('Organo', ''),
                caso_ref.get('Genero', ''),
                int(caso_ref.get('Edad', 0)) if caso_ref.get('Edad') else 0
            ]

            cursor.execute(query, params)
            similares = cursor.fetchall()

            print(f"\n✅ Casos similares encontrados: {len(similares)}\n")

            if similares:
                for i, row in enumerate(similares[:10], 1):
                    datos = dict(row)
                    print(f"{i}. {datos.get('Numero de caso', 'N/A')} - "
                          f"Edad {datos.get('Edad', 'N/A')} - "
                          f"{datos.get('Primer nombre', '')} {datos.get('Primer apellido', '')}")

                if len(similares) > 10:
                    print(f"\n... y {len(similares) - 10} más")

            return [dict(r) for r in similares]

        finally:
            conn.close()

    def backup_bd(self, nombre_backup: Optional[str] = None):
        """Crea un backup de la base de datos"""
        import shutil

        if not nombre_backup:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_backup = f"huv_oncologia_backup_{timestamp}.db"

        backup_dir = PROJECT_ROOT / "backups"
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / nombre_backup

        try:
            shutil.copy2(self.db_path, backup_path)
            size_mb = os.path.getsize(backup_path) / (1024 * 1024)

            print(f"\n{'='*80}")
            print("💾 BACKUP CREADO")
            print(f"{'='*80}\n")
            print(f"✅ Backup guardado en: {backup_path}")
            print(f"   Tamaño: {size_mb:.2f} MB")
            print(f"   Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            return backup_path

        except Exception as e:
            print(f"❌ Error creando backup: {e}")
            return None

    def restaurar_bd(self, archivo_backup: str):
        """Restaura la base de datos desde un backup"""
        import shutil

        backup_path = Path(archivo_backup)

        if not backup_path.exists():
            print(f"❌ Archivo de backup no encontrado: {archivo_backup}")
            return False

        try:
            # Crear backup del estado actual antes de restaurar
            print("Creando backup del estado actual antes de restaurar...")
            self.backup_bd("antes_restaurar_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".db")

            # Restaurar
            shutil.copy2(backup_path, self.db_path)

            print(f"\n{'='*80}")
            print("✅ BASE DE DATOS RESTAURADA")
            print(f"{'='*80}\n")
            print(f"Restaurado desde: {backup_path}")
            print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            return True

        except Exception as e:
            print(f"❌ Error restaurando backup: {e}")
            return False

    def limpiar_duplicados(self, simular: bool = True):
        """Limpia casos duplicados (mantiene el más reciente)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print(f"🧹 LIMPIEZA DE DUPLICADOS {'(SIMULACIÓN)' if simular else '(REAL)'}")
            print(f"{'='*80}\n")

            # Encontrar duplicados
            cursor.execute(f'''
                SELECT "Numero de caso", COUNT(*) as count
                FROM {self.table_name}
                GROUP BY "Numero de caso"
                HAVING count > 1
            ''')
            duplicados = cursor.fetchall()

            if not duplicados:
                print("✅ No se encontraron duplicados")
                return

            print(f"⚠️  {len(duplicados)} casos duplicados:\n")

            for caso, count in duplicados:
                print(f"  - {caso}: {count} veces")

                if not simular:
                    # Mantener solo el primer registro
                    cursor.execute(f'''
                        DELETE FROM {self.table_name}
                        WHERE rowid NOT IN (
                            SELECT MIN(rowid)
                            FROM {self.table_name}
                            WHERE "Numero de caso" = ?
                        )
                    ''', (caso,))

            if not simular:
                conn.commit()
                print(f"\n✅ {len(duplicados)} casos duplicados eliminados")
            else:
                print(f"\n💡 Usa simular=False para eliminar duplicados realmente")

        finally:
            conn.close()

    def optimizar_bd(self):
        """Optimiza la base de datos (VACUUM y ANALYZE)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            print(f"\n{'='*80}")
            print("⚡ OPTIMIZANDO BASE DE DATOS")
            print(f"{'='*80}\n")

            size_antes = os.path.getsize(self.db_path) / (1024 * 1024)
            print(f"Tamaño antes: {size_antes:.2f} MB")

            # VACUUM reorganiza la BD y libera espacio
            print("\n🔄 Ejecutando VACUUM...")
            cursor.execute("VACUUM")

            # ANALYZE actualiza estadísticas para optimizar queries
            print("🔄 Ejecutando ANALYZE...")
            cursor.execute("ANALYZE")

            conn.commit()

            size_despues = os.path.getsize(self.db_path) / (1024 * 1024)
            ahorro = size_antes - size_despues

            print(f"\n✅ OPTIMIZACIÓN COMPLETADA")
            print(f"   Tamaño después: {size_despues:.2f} MB")
            print(f"   Espacio liberado: {ahorro:.2f} MB")

        finally:
            conn.close()


def main():
    """CLI principal"""
    parser = argparse.ArgumentParser(
        description="💾 Gestor de Base de Datos EVARISIS - Herramienta Consolidada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

CONSULTAS:
  python gestor_base_datos.py --buscar IHQ250001           # Buscar caso
  python gestor_base_datos.py --buscar IHQ250001 --detallado  # Con todos los campos
  python gestor_base_datos.py --paciente "Juan"           # Por nombre
  python gestor_base_datos.py --organo PULMON              # Por órgano

LISTADOS:
  python gestor_base_datos.py --listar                     # Listar todos
  python gestor_base_datos.py --listar --limite 10         # Primeros 10
  python gestor_base_datos.py --biomarcadores IHQ250001    # Biomarcadores

SCHEMA:
  python gestor_base_datos.py --tablas                     # Listar tablas
  python gestor_base_datos.py --columnas                   # Ver columnas
  python gestor_base_datos.py --columnas --tabla informes_ihq  # Tabla específica

ESTADÍSTICAS:
  python gestor_base_datos.py --stats                      # Estadísticas globales
  python gestor_base_datos.py --completitud                # Completitud promedio
  python gestor_base_datos.py --completitud --caso IHQ250001  # Caso específico

VERIFICACIÓN:
  python gestor_base_datos.py --verificar                  # Verificar integridad
  python gestor_base_datos.py --detectar-anomalias         # Detectar anomalías

BÚSQUEDA AVANZADA:
  python gestor_base_datos.py --buscar-avanzado --organo PULMON --edad-min 40 --edad-max 60
  python gestor_base_datos.py --buscar-fechas 2025-01-01 2025-12-31
  python gestor_base_datos.py --casos-similares IHQ250001  # Casos similares

ANÁLISIS:
  python gestor_base_datos.py --tendencias                 # Análisis temporal
  python gestor_base_datos.py --detectar-anomalias         # Detectar anomalías

MANTENIMIENTO:
  python gestor_base_datos.py --backup                     # Crear backup
  python gestor_base_datos.py --backup --nombre mi_backup.db
  python gestor_base_datos.py --restaurar backups/backup.db
  python gestor_base_datos.py --limpiar-duplicados         # Simular limpieza
  python gestor_base_datos.py --limpiar-duplicados --aplicar  # Limpiar realmente
  python gestor_base_datos.py --optimizar                  # Optimizar BD

EXPORTACIÓN:
  python gestor_base_datos.py --buscar IHQ250001 --json salida.json
        """
    )

    # Consultas básicas
    parser.add_argument("--buscar", "-b", help="Buscar caso por número IHQ")
    parser.add_argument("--detallado", action="store_true", help="Mostrar todos los campos")
    parser.add_argument("--paciente", help="Buscar por nombre de paciente")
    parser.add_argument("--organo", help="Buscar por órgano")
    parser.add_argument("--listar", action="store_true", help="Listar casos")
    parser.add_argument("--limite", type=int, help="Limitar resultados")
    parser.add_argument("--biomarcadores", help="Listar biomarcadores de un caso")

    # Schema
    parser.add_argument("--tablas", action="store_true", help="Listar tablas")
    parser.add_argument("--columnas", action="store_true", help="Ver columnas")
    parser.add_argument("--tabla", help="Tabla específica (default: informes_ihq)")

    # Estadísticas
    parser.add_argument("--stats", action="store_true", help="Estadísticas globales")
    parser.add_argument("--completitud", action="store_true", help="Calcular completitud")
    parser.add_argument("--caso", help="Caso específico para completitud")

    # Verificación
    parser.add_argument("--verificar", action="store_true", help="Verificar integridad")
    parser.add_argument("--detectar-anomalias", action="store_true", help="Detectar anomalías en datos")

    # Búsqueda avanzada
    parser.add_argument("--buscar-avanzado", action="store_true", help="Búsqueda avanzada con filtros")
    parser.add_argument("--edad-min", type=int, help="Edad mínima (para búsqueda avanzada)")
    parser.add_argument("--edad-max", type=int, help="Edad máxima (para búsqueda avanzada)")
    parser.add_argument("--genero", help="Género M/F (para búsqueda avanzada)")
    parser.add_argument("--eps", help="EPS (para búsqueda avanzada)")
    parser.add_argument("--diagnostico", help="Patrón en diagnóstico (para búsqueda avanzada)")
    parser.add_argument("--buscar-fechas", nargs=2, metavar=('INICIO', 'FIN'), help="Buscar por rango de fechas (YYYY-MM-DD)")
    parser.add_argument("--casos-similares", help="Encontrar casos similares al especificado")

    # Análisis
    parser.add_argument("--tendencias", action="store_true", help="Analizar tendencias temporales")

    # Mantenimiento
    parser.add_argument("--backup", action="store_true", help="Crear backup de la BD")
    parser.add_argument("--nombre", help="Nombre del backup (opcional)")
    parser.add_argument("--restaurar", help="Restaurar desde backup (ruta al archivo)")
    parser.add_argument("--limpiar-duplicados", action="store_true", help="Limpiar casos duplicados")
    parser.add_argument("--aplicar", action="store_true", help="Aplicar cambios (sin esto, solo simula)")
    parser.add_argument("--optimizar", action="store_true", help="Optimizar base de datos")

    # Exportación
    parser.add_argument("--json", help="Exportar a JSON")

    args = parser.parse_args()

    try:
        gestor = GestorBaseDatos()

        if args.buscar:
            datos = gestor.buscar_caso(args.buscar, detallado=args.detallado)
            if args.json and datos:
                gestor.exportar_json(datos, args.json)

        elif args.paciente:
            gestor.buscar_por_paciente(args.paciente)

        elif args.organo:
            gestor.buscar_por_organo(args.organo)

        elif args.listar:
            gestor.listar_casos(limite=args.limite)

        elif args.biomarcadores:
            gestor.listar_biomarcadores(args.biomarcadores)

        elif args.tablas:
            gestor.listar_tablas()

        elif args.columnas:
            gestor.ver_columnas(args.tabla)

        elif args.stats:
            gestor.estadisticas_globales()

        elif args.completitud:
            gestor.calcular_completitud(args.caso)

        elif args.verificar:
            gestor.verificar_integridad()

        elif args.detectar_anomalias:
            gestor.detectar_anomalias()

        elif args.buscar_avanzado:
            filtros = {}
            if args.organo:
                filtros['organo'] = args.organo
            if args.edad_min:
                filtros['edad_min'] = args.edad_min
            if args.edad_max:
                filtros['edad_max'] = args.edad_max
            if args.genero:
                filtros['genero'] = args.genero
            if args.eps:
                filtros['eps'] = args.eps
            if args.diagnostico:
                filtros['diagnostico'] = args.diagnostico

            resultados = gestor.buscar_avanzado(**filtros)
            if args.json and resultados:
                gestor.exportar_json(resultados, args.json)

        elif args.buscar_fechas:
            fecha_inicio, fecha_fin = args.buscar_fechas
            resultados = gestor.buscar_por_fecha_rango(fecha_inicio, fecha_fin)
            if args.json and resultados:
                gestor.exportar_json(resultados, args.json)

        elif args.casos_similares:
            resultados = gestor.comparar_casos_similares(args.casos_similares)
            if args.json and resultados:
                gestor.exportar_json(resultados, args.json)

        elif args.tendencias:
            gestor.analizar_tendencias_temporales()

        elif args.backup:
            gestor.backup_bd(args.nombre)

        elif args.restaurar:
            gestor.restaurar_bd(args.restaurar)

        elif args.limpiar_duplicados:
            gestor.limpiar_duplicados(simular=not args.aplicar)

        elif args.optimizar:
            gestor.optimizar_bd()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\n⚠️  Operación cancelada")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
