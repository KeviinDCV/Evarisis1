#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 CLI UNIFICADO - HERRAMIENTAS GESTOR ONCOLOGÍA HUV
===================================================

Interfaz unificada de línea de comandos para todas las herramientas
de debug, análisis y verificación del sistema.

OPTIMIZADO PARA USO DE IA - Todos los comandos por línea de comandos

Autor: Sistema EVARISIS
Fecha: 4 de octubre de 2025
Versión: 4.2.1 - CLI Mejorado para IA
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

class CLIHerramientas:
    """CLI unificado para todas las herramientas del sistema"""

    def __init__(self):
        self.herramientas_dir = Path(__file__).parent
        self.proyecto_dir = self.herramientas_dir.parent
        self.venv_path = self.proyecto_dir / "venv0"

    def _ejecutar_python(self, script_name, args=None):
        """Ejecutar script Python con el intérprete del venv"""
        if args is None:
            args = []

        try:
            python_exe = self.venv_path / "Scripts" / "python.exe"
            script_path = self.herramientas_dir / script_name

            if not script_path.exists():
                print(f"❌ Script no encontrado: {script_path}")
                return False

            cmd = [str(python_exe), str(script_path)] + args

            print(f"🚀 Ejecutando: {script_name}")
            if args:
                print(f"📝 Argumentos: {' '.join(args)}")
            print("-" * 80)

            result = subprocess.run(cmd, cwd=str(self.proyecto_dir))

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error ejecutando {script_name}: {e}")
            return False

    def _importar_y_ejecutar(self, modulo, funcion, *args, **kwargs):
        """Importar módulo y ejecutar función directamente (más rápido)"""
        try:
            import importlib
            mod = importlib.import_module(f"herramientas_ia.{modulo}")
            func = getattr(mod, funcion)
            return func(*args, **kwargs)
        except Exception as e:
            print(f"❌ Error ejecutando {modulo}.{funcion}: {e}")
            return None

def main():
    """Función principal del CLI unificado"""
    parser = argparse.ArgumentParser(
        description="🔧 CLI Unificado - Herramientas Gestor Oncología HUV v4.2.1",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
═══════════════════════════════════════════════════════════════════════════════
📋 EJEMPLOS DE USO COMPLETOS:
═══════════════════════════════════════════════════════════════════════════════

📊 BASE DE DATOS - Consultas y Verificación:

  # Estadísticas generales de la BD
  python cli_herramientas.py bd --stats

  # Buscar caso IHQ específico
  python cli_herramientas.py bd --buscar IHQ250001

  # Listar todos los registros (con límite)
  python cli_herramientas.py bd --listar --limite 20

  # Buscar por paciente
  python cli_herramientas.py bd --paciente "Juan Perez"

  # Buscar por órgano
  python cli_herramientas.py bd --organo PULMON

  # Buscar por diagnóstico (regex)
  python cli_herramientas.py bd --diagnostico "ADENOCARCINOMA"

  # Ver biomarcadores de un caso
  python cli_herramientas.py bd --biomarcadores IHQ250001

  # Exportar resultados de búsqueda a JSON
  python cli_herramientas.py bd --buscar IHQ250001 --json salida.json

  # Verificar integridad de la BD
  python cli_herramientas.py bd --verificar

───────────────────────────────────────────────────────────────────────────────

📄 PDF - Análisis y Extracción:

  # Análisis rápido de caso IHQ específico (RECOMENDADO)
  python cli_herramientas.py pdf --archivo ordenamientos.pdf --ihq 250001

  # Solo OCR del PDF
  python cli_herramientas.py pdf --archivo documento.pdf --ocr

  # Extraer todos los segmentos IHQ
  python cli_herramientas.py pdf --archivo ordenamientos.pdf --segmentar

  # Análisis completo (paciente + médico + biomarcadores)
  python cli_herramientas.py pdf --archivo documento.pdf --completo

  # Solo datos de paciente
  python cli_herramientas.py pdf --archivo documento.pdf --paciente

  # Solo biomarcadores
  python cli_herramientas.py pdf --archivo documento.pdf --biomarcadores

  # Buscar patrón específico en PDF
  python cli_herramientas.py pdf --archivo documento.pdf --patron "Ki-67"

  # Comparar extracción con BD
  python cli_herramientas.py pdf --archivo documento.pdf --ihq 250001 --comparar

───────────────────────────────────────────────────────────────────────────────

📊 EXCEL - Verificación y Análisis:

  # Listar todos los Excel exportados
  python cli_herramientas.py excel --listar

  # Estadísticas del último Excel
  python cli_herramientas.py excel --stats

  # Verificar calidad de datos en Excel
  python cli_herramientas.py excel --calidad archivo.xlsx

  # Comparar dos exportaciones
  python cli_herramientas.py excel --comparar archivo1.xlsx archivo2.xlsx

  # Verificar columnas faltantes
  python cli_herramientas.py excel --verificar-columnas archivo.xlsx

───────────────────────────────────────────────────────────────────────────────

🔍 VALIDACIÓN - Verificar Extracción vs BD:

  # Validar extracción de caso IHQ
  python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

  # Validar todos los campos de un caso
  python cli_herramientas.py validar --ihq 250001 --completo

  # Generar reporte de diferencias
  python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte

───────────────────────────────────────────────────────────────────────────────

🧪 TEST Y DEBUG:

  # Ejecutar todos los tests
  python cli_herramientas.py test

  # Test de imports y dependencias
  python cli_herramientas.py test --imports

  # Test de conexión a BD
  python cli_herramientas.py test --bd

  # Utilidades de debug
  python cli_herramientas.py debug

  # Información del sistema
  python cli_herramientas.py info

───────────────────────────────────────────────────────────────────────────────

⚡ COMANDOS RÁPIDOS (Más Usados):

  # Ver caso IHQ250001
  python cli_herramientas.py bd -b IHQ250001

  # Analizar caso específico en PDF
  python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

  # Stats generales
  python cli_herramientas.py bd -s

  # Último Excel
  python cli_herramientas.py excel -l

═══════════════════════════════════════════════════════════════════════════════
        """
    )

    # ═══════════════════════════════════════════════════════════════════════════════
    # SUBCOMANDOS
    # ═══════════════════════════════════════════════════════════════════════════════

    subparsers = parser.add_subparsers(dest='comando', help='Herramientas disponibles')

    # ──────────────────────────── BASE DE DATOS ────────────────────────────────────

    bd_parser = subparsers.add_parser('bd', help='🔍 Consultas de base de datos')
    bd_parser.add_argument('-s', '--stats', action='store_true', help='Estadísticas generales')
    bd_parser.add_argument('-b', '--buscar', metavar='IHQ', help='Buscar por número de petición')
    bd_parser.add_argument('-l', '--listar', action='store_true', help='Listar todos los registros')
    bd_parser.add_argument('--limite', type=int, default=50, help='Límite de registros (default: 50)')
    bd_parser.add_argument('-p', '--paciente', metavar='NOMBRE', help='Buscar por nombre de paciente')
    bd_parser.add_argument('-o', '--organo', metavar='ORGANO', help='Filtrar por órgano')
    bd_parser.add_argument('-d', '--diagnostico', metavar='DIAG', help='Filtrar por diagnóstico (regex)')
    bd_parser.add_argument('--biomarcadores', metavar='IHQ', help='Ver biomarcadores de caso IHQ')
    bd_parser.add_argument('--json', metavar='ARCHIVO', help='Exportar resultado a JSON')
    bd_parser.add_argument('--verificar', action='store_true', help='Verificar integridad de BD')
    bd_parser.add_argument('--contar', action='store_true', help='Contar registros por categoría')

    # ──────────────────────────── PDF ────────────────────────────────────────────

    pdf_parser = subparsers.add_parser('pdf', help='📄 Análisis de archivos PDF')
    pdf_parser.add_argument('-f', '--archivo', required=True, metavar='PDF', help='Archivo PDF a analizar')
    pdf_parser.add_argument('-i', '--ihq', metavar='NUMERO', help='⚡ Analizar solo caso IHQ específico (ej: 250001)')
    pdf_parser.add_argument('--ocr', action='store_true', help='Solo mostrar texto OCR')
    pdf_parser.add_argument('--segmentar', action='store_true', help='Segmentar y mostrar todos los casos IHQ')
    pdf_parser.add_argument('--completo', action='store_true', help='Análisis completo (paciente + médico + biomarcadores)')
    pdf_parser.add_argument('--paciente', action='store_true', help='Solo extraer datos de paciente')
    pdf_parser.add_argument('--medico', action='store_true', help='Solo extraer datos médicos')
    pdf_parser.add_argument('--biomarcadores', action='store_true', help='Solo extraer biomarcadores')
    pdf_parser.add_argument('--patron', metavar='REGEX', help='Buscar patrón específico (regex)')
    pdf_parser.add_argument('--comparar', action='store_true', help='Comparar extracción con BD (requiere --ihq)')
    pdf_parser.add_argument('--json', metavar='ARCHIVO', help='Exportar resultado a JSON')
    pdf_parser.add_argument('--limite-paginas', type=int, help='Limitar número de páginas a procesar')

    # ──────────────────────────── EXCEL ──────────────────────────────────────────

    excel_parser = subparsers.add_parser('excel', help='📊 Verificación de archivos Excel')
    excel_parser.add_argument('-l', '--listar', action='store_true', help='Listar archivos Excel exportados')
    excel_parser.add_argument('-s', '--stats', action='store_true', help='Estadísticas del último Excel')
    excel_parser.add_argument('--calidad', metavar='ARCHIVO', help='Reporte de calidad de datos')
    excel_parser.add_argument('--verificar-columnas', metavar='ARCHIVO', help='Verificar columnas esperadas')
    excel_parser.add_argument('--comparar', nargs=2, metavar=('EXCEL1', 'EXCEL2'), help='Comparar dos exportaciones')
    excel_parser.add_argument('--abrir', metavar='ARCHIVO', help='Abrir Excel específico')
    excel_parser.add_argument('--ultimo', action='store_true', help='Abrir último Excel generado')

    # ──────────────────────────── VALIDACIÓN ────────────────────────────────────

    validar_parser = subparsers.add_parser('validar', help='✅ Validar extracción vs BD')
    validar_parser.add_argument('--ihq', required=True, metavar='NUMERO', help='Número de petición IHQ')
    validar_parser.add_argument('--pdf', metavar='ARCHIVO', help='PDF para extraer y comparar')
    validar_parser.add_argument('--completo', action='store_true', help='Validar todos los campos')
    validar_parser.add_argument('--solo-diferencias', action='store_true', help='Mostrar solo diferencias')
    validar_parser.add_argument('--reporte', action='store_true', help='Generar reporte detallado')
    validar_parser.add_argument('--campos', nargs='+', help='Validar campos específicos')

    # ──────────────────────────── TEST ──────────────────────────────────────────

    test_parser = subparsers.add_parser('test', help='🧪 Ejecutar tests del sistema')
    test_parser.add_argument('--imports', action='store_true', help='Test de imports y dependencias')
    test_parser.add_argument('--bd', action='store_true', help='Test de conexión a BD')
    test_parser.add_argument('--ocr', action='store_true', help='Test de OCR')
    test_parser.add_argument('--extractores', action='store_true', help='Test de extractores')
    test_parser.add_argument('--todo', action='store_true', help='Ejecutar todos los tests')

    # ──────────────────────────── OTROS ──────────────────────────────────────────

    subparsers.add_parser('debug', help='🐛 Utilidades de debug')
    subparsers.add_parser('info', help='ℹ️ Información del sistema y versión')

    # ═══════════════════════════════════════════════════════════════════════════════
    # PROCESAMIENTO DE ARGUMENTOS
    # ═══════════════════════════════════════════════════════════════════════════════

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        return

    cli = CLIHerramientas()

    # ──────────────────────────── COMANDO: BD ────────────────────────────────────

    if args.comando == 'bd':
        cmd_args = []

        if args.stats:
            cmd_args.append("--estadisticas")
        elif args.buscar:
            cmd_args.extend(["--buscar-peticion", args.buscar])
        elif args.listar:
            cmd_args.extend(["--listar", "--limite", str(args.limite)])
        elif args.paciente:
            cmd_args.extend(["--paciente", args.paciente])
        elif args.organo:
            cmd_args.extend(["--organo", args.organo])
        elif args.diagnostico:
            cmd_args.extend(["--diagnostico", args.diagnostico])
        elif args.biomarcadores:
            cmd_args.extend(["--biomarcadores", args.biomarcadores])
        elif args.verificar:
            cmd_args.append("--verificar-integridad")
        elif args.contar:
            cmd_args.append("--contar")

        if args.json:
            cmd_args.extend(["--json", args.json])

        cli._ejecutar_python("consulta_base_datos.py", cmd_args)

    # ──────────────────────────── COMANDO: PDF ──────────────────────────────────

    elif args.comando == 'pdf':
        cmd_args = ["--archivo", args.archivo]

        if args.ihq:
            cmd_args.extend(["--ihq", args.ihq])
        if args.ocr:
            cmd_args.append("--solo-ocr")
        if args.segmentar:
            cmd_args.append("--segmentar")
        if args.completo:
            cmd_args.append("--completo")
        if args.paciente:
            cmd_args.append("--paciente")
        if args.medico:
            cmd_args.append("--medico")
        if args.biomarcadores:
            cmd_args.append("--biomarcadores")
        if args.patron:
            cmd_args.extend(["--patron", args.patron])
        if args.comparar:
            cmd_args.append("--comparar-bd")
        if args.json:
            cmd_args.extend(["--json", args.json])
        if args.limite_paginas:
            cmd_args.extend(["--limite-paginas", str(args.limite_paginas)])

        cli._ejecutar_python("analizar_pdf_completo.py", cmd_args)

    # ──────────────────────────── COMANDO: EXCEL ────────────────────────────────

    elif args.comando == 'excel':
        cmd_args = []

        if args.listar:
            cmd_args.append("--listar")
        elif args.stats:
            cmd_args.append("--estadisticas-ultimo")
        elif args.calidad:
            cmd_args.extend(["--calidad", args.calidad])
        elif args.verificar_columnas:
            cmd_args.extend(["--verificar-columnas", args.verificar_columnas])
        elif args.comparar:
            cmd_args.extend(["--comparar", args.comparar[0], args.comparar[1]])
        elif args.abrir:
            cmd_args.extend(["--abrir", args.abrir])
        elif args.ultimo:
            cmd_args.append("--abrir-ultimo")

        # Crear el script si no existe
        script_excel = cli.herramientas_dir / "verificar_excel.py"
        if not script_excel.exists():
            print("⚠️ Creando herramienta verificar_excel.py...")
            # Se creará después

        cli._ejecutar_python("verificar_excel.py", cmd_args)

    # ──────────────────────────── COMANDO: VALIDAR ──────────────────────────────

    elif args.comando == 'validar':
        cmd_args = ["--ihq", args.ihq]

        if args.pdf:
            cmd_args.extend(["--pdf", args.pdf])
        if args.completo:
            cmd_args.append("--completo")
        if args.solo_diferencias:
            cmd_args.append("--solo-diferencias")
        if args.reporte:
            cmd_args.append("--reporte")
        if args.campos:
            cmd_args.extend(["--campos"] + args.campos)

        # Crear el script si no existe
        script_validar = cli.herramientas_dir / "validar_extraccion.py"
        if not script_validar.exists():
            print("⚠️ Creando herramienta validar_extraccion.py...")
            # Se creará después

        cli._ejecutar_python("validar_extraccion.py", cmd_args)

    # ──────────────────────────── COMANDO: TEST ──────────────────────────────────

    elif args.comando == 'test':
        cmd_args = []

        if args.imports:
            cmd_args.append("--test-imports")
        elif args.bd:
            cmd_args.append("--test-bd")
        elif args.ocr:
            cmd_args.append("--test-ocr")
        elif args.extractores:
            cmd_args.append("--test-extractores")
        elif args.todo:
            cmd_args.append("--todo")

        cli._ejecutar_python("test_herramientas.py", cmd_args)

    # ──────────────────────────── COMANDO: DEBUG ────────────────────────────────

    elif args.comando == 'debug':
        cli._ejecutar_python("utilidades_debug.py", [])

    # ──────────────────────────── COMANDO: INFO ──────────────────────────────────

    elif args.comando == 'info':
        try:
            from config.version_info import get_full_version_info, get_version_string, get_build_info
            import json

            print("=" * 80)
            print(f"📋 EVARISIS Gestor H.U.V - Información del Sistema")
            print("=" * 80)
            print(f"\n📌 Versión: {get_version_string()}")
            print(f"🔨 Build: {get_build_info()}")

            info = get_full_version_info()

            print(f"\n🎯 Proyecto: {info['project']['name']}")
            print(f"   {info['project']['description']}")
            print(f"   Organización: {info['project']['organization']}")

            print(f"\n💻 Sistema:")
            print(f"   Python: {info['system']['python_version'].split()[0]}")
            print(f"   Plataforma: {info['system']['platform']}")
            print(f"   Arquitectura: {info['system']['architecture']}")

            print(f"\n✨ Características:")
            for feature in info['features'][:5]:
                print(f"   {feature}")

            print("\n" + "=" * 80)

        except Exception as e:
            print(f"❌ Error obteniendo información: {e}")

if __name__ == "__main__":
    main()
