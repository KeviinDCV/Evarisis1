#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📊 VERIFICADOR DE EXCEL - Gestor Oncología HUV
==============================================

Herramienta para verificar, analizar y comparar archivos Excel exportados.

Autor: Sistema EVARISIS
Fecha: 4 de octubre de 2025
Versión: 4.2.1
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import pandas as pd
    import openpyxl
    from core.database_manager import NEW_TABLE_COLUMNS_ORDER
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)


class VerificadorExcel:
    """Verificador de archivos Excel exportados"""

    def __init__(self):
        self.proyecto_dir = Path(__file__).parent.parent
        self.excel_dir = self.proyecto_dir / "EXCEL"
        self.columnas_esperadas = NEW_TABLE_COLUMNS_ORDER

    def listar_archivos(self):
        """Lista todos los archivos Excel en la carpeta EXCEL"""
        print("=" * 80)
        print("📊 ARCHIVOS EXCEL EXPORTADOS")
        print("=" * 80)

        if not self.excel_dir.exists():
            print(f"❌ Carpeta EXCEL no encontrada: {self.excel_dir}")
            return

        archivos = sorted(self.excel_dir.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)

        if not archivos:
            print("📁 No hay archivos Excel en la carpeta")
            return

        print(f"\n📁 Carpeta: {self.excel_dir}")
        print(f"📈 Total de archivos: {len(archivos)}\n")

        print(f"{'#':<4} {'Archivo':<50} {'Tamaño':<12} {'Fecha':<20}")
        print("-" * 86)

        for idx, archivo in enumerate(archivos, 1):
            tamaño = archivo.stat().st_size / 1024  # KB
            fecha = datetime.fromtimestamp(archivo.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')

            # Truncar nombre si es muy largo
            nombre = archivo.name[:47] + "..." if len(archivo.name) > 50 else archivo.name

            print(f"{idx:<4} {nombre:<50} {tamaño:>8.1f} KB  {fecha}")

        print("=" * 80)

    def obtener_ultimo_archivo(self) -> Path:
        """Obtiene el último archivo Excel generado"""
        archivos = sorted(self.excel_dir.glob("*.xlsx"), key=lambda x: x.stat().st_mtime, reverse=True)

        if not archivos:
            raise FileNotFoundError("No hay archivos Excel en la carpeta")

        return archivos[0]

    def estadisticas_excel(self, archivo_path: Path = None):
        """Muestra estadísticas de un archivo Excel"""
        if archivo_path is None:
            archivo_path = self.obtener_ultimo_archivo()

        print("=" * 80)
        print(f"📊 ESTADÍSTICAS - {archivo_path.name}")
        print("=" * 80)

        try:
            df = pd.read_excel(archivo_path)

            print(f"\n📋 Información General:")
            print(f"   Filas: {len(df)}")
            print(f"   Columnas: {len(df.columns)}")
            print(f"   Tamaño: {archivo_path.stat().st_size / 1024:.1f} KB")

            print(f"\n📊 Estadísticas de Datos:")
            print(f"   Celdas totales: {len(df) * len(df.columns)}")
            print(f"   Celdas vacías: {df.isna().sum().sum()}")
            print(f"   Celdas con datos: {df.notna().sum().sum()}")
            print(f"   Completitud: {(df.notna().sum().sum() / (len(df) * len(df.columns)) * 100):.1f}%")

            # Top campos con más datos
            print(f"\n✅ Top 10 Campos Más Completos:")
            completitud = df.notna().sum().sort_values(ascending=False).head(10)
            for campo, count in completitud.items():
                porcentaje = (count / len(df)) * 100
                print(f"   {campo[:45]:<45}: {count:>4}/{len(df)} ({porcentaje:>5.1f}%)")

            # Top campos con menos datos
            print(f"\n❌ Top 10 Campos Menos Completos:")
            vacios = df.isna().sum().sort_values(ascending=False).head(10)
            for campo, count in vacios.items():
                porcentaje = (count / len(df)) * 100
                if count > 0:
                    print(f"   {campo[:45]:<45}: {count:>4}/{len(df)} vacíos ({porcentaje:>5.1f}%)")

            print("=" * 80)

        except Exception as e:
            print(f"❌ Error leyendo Excel: {e}")

    def verificar_columnas(self, archivo_path: Path):
        """Verifica que el Excel tenga todas las columnas esperadas"""
        print("=" * 80)
        print(f"✅ VERIFICACIÓN DE COLUMNAS - {archivo_path.name}")
        print("=" * 80)

        try:
            df = pd.read_excel(archivo_path)
            columnas_archivo = set(df.columns)
            columnas_esperadas = set(self.columnas_esperadas)

            # Columnas faltantes
            faltantes = columnas_esperadas - columnas_archivo
            # Columnas extra
            extra = columnas_archivo - columnas_esperadas

            print(f"\n📊 Resumen:")
            print(f"   Columnas esperadas: {len(columnas_esperadas)}")
            print(f"   Columnas en archivo: {len(columnas_archivo)}")
            print(f"   Columnas correctas: {len(columnas_esperadas & columnas_archivo)}")

            if faltantes:
                print(f"\n❌ Columnas Faltantes ({len(faltantes)}):")
                for col in sorted(faltantes):
                    print(f"   - {col}")

            if extra:
                print(f"\n⚠️  Columnas Extra ({len(extra)}):")
                for col in sorted(extra):
                    print(f"   + {col}")

            if not faltantes and not extra:
                print(f"\n✅ PERFECTO: Todas las columnas están presentes y correctas")

            print("=" * 80)

        except Exception as e:
            print(f"❌ Error verificando columnas: {e}")

    def calidad_datos(self, archivo_path: Path):
        """Genera reporte de calidad de datos"""
        print("=" * 80)
        print(f"📈 REPORTE DE CALIDAD DE DATOS - {archivo_path.name}")
        print("=" * 80)

        try:
            df = pd.read_excel(archivo_path)

            # Campos críticos que deberían estar siempre llenos
            campos_criticos = [
                'N. peticion (0. Numero de biopsia)',
                'Primer nombre',
                'Primer apellido',
                'N. de identificación',
                'Genero',
                'Edad'
            ]

            print(f"\n🔴 Campos Críticos:")
            for campo in campos_criticos:
                if campo in df.columns:
                    vacios = df[campo].isna().sum()
                    total = len(df)
                    completitud = ((total - vacios) / total * 100) if total > 0 else 0

                    estado = "✅" if vacios == 0 else "❌"
                    print(f"   {estado} {campo:<45}: {total - vacios}/{total} ({completitud:.1f}%)")

            # Detectar posibles problemas
            print(f"\n⚠️  Detección de Problemas:")

            # Duplicados de N. petición
            if 'N. peticion (0. Numero de biopsia)' in df.columns:
                duplicados = df['N. peticion (0. Numero de biopsia)'].duplicated().sum()
                if duplicados > 0:
                    print(f"   ❌ {duplicados} N. petición duplicados detectados")
                else:
                    print(f"   ✅ No hay N. petición duplicados")

            # Valores sospechosos en Edad
            if 'Edad' in df.columns:
                edades_invalidas = df[(df['Edad'] < 0) | (df['Edad'] > 120)].shape[0]
                if edades_invalidas > 0:
                    print(f"   ⚠️  {edades_invalidas} edades fuera de rango (0-120)")
                else:
                    print(f"   ✅ Todas las edades en rango válido")

            # Género con valores válidos
            if 'Genero' in df.columns:
                generos = df['Genero'].value_counts()
                print(f"   📊 Distribución de Género:")
                for genero, count in generos.items():
                    print(f"      {genero}: {count}")

            print("=" * 80)

        except Exception as e:
            print(f"❌ Error en análisis de calidad: {e}")

    def comparar_archivos(self, archivo1_path: Path, archivo2_path: Path):
        """Compara dos archivos Excel"""
        print("=" * 80)
        print(f"🔄 COMPARACIÓN DE ARCHIVOS")
        print("=" * 80)

        try:
            df1 = pd.read_excel(archivo1_path)
            df2 = pd.read_excel(archivo2_path)

            print(f"\n📄 Archivo 1: {archivo1_path.name}")
            print(f"   Filas: {len(df1)}, Columnas: {len(df1.columns)}")

            print(f"\n📄 Archivo 2: {archivo2_path.name}")
            print(f"   Filas: {len(df2)}, Columnas: {len(df2.columns)}")

            # Comparar número de filas
            diff_filas = len(df2) - len(df1)
            print(f"\n📊 Diferencias:")
            print(f"   Filas: {diff_filas:+d} ({len(df1)} → {len(df2)})")

            # Comparar columnas
            cols1 = set(df1.columns)
            cols2 = set(df2.columns)

            nuevas_cols = cols2 - cols1
            eliminadas_cols = cols1 - cols2

            if nuevas_cols:
                print(f"   ➕ Columnas añadidas ({len(nuevas_cols)}):")
                for col in sorted(nuevas_cols):
                    print(f"      + {col}")

            if eliminadas_cols:
                print(f"   ➖ Columnas eliminadas ({len(eliminadas_cols)}):")
                for col in sorted(eliminadas_cols):
                    print(f"      - {col}")

            if not nuevas_cols and not eliminadas_cols:
                print(f"   ✅ Mismas columnas en ambos archivos")

            print("=" * 80)

        except Exception as e:
            print(f"❌ Error comparando archivos: {e}")

    def abrir_archivo(self, archivo_path: Path):
        """Abre un archivo Excel con la aplicación predeterminada"""
        try:
            if sys.platform.startswith('win'):
                os.startfile(archivo_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', archivo_path])
            else:  # Linux
                subprocess.run(['xdg-open', archivo_path])

            print(f"✅ Abriendo: {archivo_path.name}")
        except Exception as e:
            print(f"❌ Error abriendo archivo: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="📊 Verificador de Excel - Gestor Oncología HUV",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--listar', action='store_true', help='Listar archivos Excel')
    parser.add_argument('--estadisticas-ultimo', action='store_true', help='Estadísticas del último Excel')
    parser.add_argument('--calidad', metavar='ARCHIVO', help='Reporte de calidad de datos')
    parser.add_argument('--verificar-columnas', metavar='ARCHIVO', help='Verificar columnas esperadas')
    parser.add_argument('--comparar', nargs=2, metavar=('EXCEL1', 'EXCEL2'), help='Comparar dos archivos')
    parser.add_argument('--abrir', metavar='ARCHIVO', help='Abrir Excel específico')
    parser.add_argument('--abrir-ultimo', action='store_true', help='Abrir último Excel generado')

    args = parser.parse_args()

    verificador = VerificadorExcel()

    try:
        if args.listar:
            verificador.listar_archivos()

        elif args.estadisticas_ultimo:
            verificador.estadisticas_excel()

        elif args.calidad:
            archivo = verificador.excel_dir / args.calidad
            if not archivo.exists():
                print(f"❌ Archivo no encontrado: {archivo}")
                sys.exit(1)
            verificador.calidad_datos(archivo)

        elif args.verificar_columnas:
            archivo = verificador.excel_dir / args.verificar_columnas
            if not archivo.exists():
                print(f"❌ Archivo no encontrado: {archivo}")
                sys.exit(1)
            verificador.verificar_columnas(archivo)

        elif args.comparar:
            archivo1 = verificador.excel_dir / args.comparar[0]
            archivo2 = verificador.excel_dir / args.comparar[1]

            if not archivo1.exists():
                print(f"❌ Archivo 1 no encontrado: {archivo1}")
                sys.exit(1)
            if not archivo2.exists():
                print(f"❌ Archivo 2 no encontrado: {archivo2}")
                sys.exit(1)

            verificador.comparar_archivos(archivo1, archivo2)

        elif args.abrir:
            archivo = verificador.excel_dir / args.abrir
            if not archivo.exists():
                print(f"❌ Archivo no encontrado: {archivo}")
                sys.exit(1)
            verificador.abrir_archivo(archivo)

        elif args.abrir_ultimo:
            archivo = verificador.obtener_ultimo_archivo()
            verificador.abrir_archivo(archivo)

        else:
            # Por defecto, listar archivos
            verificador.listar_archivos()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
