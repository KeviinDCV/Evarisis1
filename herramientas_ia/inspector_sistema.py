#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 INSPECTOR DE SISTEMA - Herramienta de Diagnóstico Completo EVARISIS
========================================================================

Herramienta súper densa que consolida:
1. utilidades_comunes.py - Verificación de entorno
2. utilidades_debug.py - Validación de datos
3. validar_copilot_config.py - Verificación de configs
4. + NUEVAS FUNCIONES:
   - Análisis AST de código redundante
   - Sugerencias de modularización
   - Testing de componentes aislados
   - Análisis de imports y dependencias
   - Trazabilidad completa de flujo

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 20 de octubre de 2025
"""

import sys
import os
import ast
import sqlite3
import importlib
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from collections import defaultdict
import re

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class InspectorSistema:
    """Inspector súper denso - Diagnóstico completo del sistema"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.core_dir = PROJECT_ROOT / "core"
        self.db_path = PROJECT_ROOT / "data" / "huv_oncologia_NUEVO.db"
        self.debug_maps_dir = PROJECT_ROOT / "data" / "debug_maps"
        self.errores = []
        self.warnings = []
        self.info = []

    # ========== 1. HEALTH CHECK COMPLETO ==========

    def verificar_salud_completa(self):
        """Health check completo del sistema"""
        print(f"\n{'='*80}")
        print("🏥 VERIFICACIÓN DE SALUD DEL SISTEMA EVARISIS")
        print(f"{'='*80}\n")

        # 1. Entorno Python
        self._verificar_entorno()

        # 2. Base de datos
        self._verificar_base_datos()

        # 3. Paths del sistema
        self._verificar_paths()

        # 4. Configuraciones
        self._verificar_configuraciones()

        # 5. Imports y dependencias
        self._verificar_dependencias_core()

        # Resumen final
        self._mostrar_resumen()

    def _verificar_entorno(self):
        """Verifica entorno Python y módulos"""
        print("📦 VERIFICANDO ENTORNO PYTHON")
        print("-" * 80)

        # Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.minor}"
        if sys.version_info >= (3, 8):
            self._ok(f"Python {py_version} ✓")
        else:
            self._error(f"Python {py_version} - Se requiere Python 3.8+")

        # Módulos críticos
        modulos_criticos = [
            'sqlite3', 'pathlib', 'json', 're', 'datetime',
            'pytesseract', 'pdf2image', 'PIL', 'openpyxl',
            'tkinter', 'pandas', 'numpy'
        ]

        for modulo in modulos_criticos:
            try:
                importlib.import_module(modulo)
                self._ok(f"Módulo {modulo} ✓")
            except ImportError:
                self._error(f"Módulo {modulo} NO disponible")

        # Virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_path = sys.prefix
            self._ok(f"Virtual environment activo: {venv_path}")
        else:
            self._warning("No se detectó virtual environment")

        print()

    def _verificar_base_datos(self):
        """Verifica integridad de la BD"""
        print("💾 VERIFICANDO BASE DE DATOS")
        print("-" * 80)

        if not self.db_path.exists():
            self._error(f"Base de datos NO encontrada: {self.db_path}")
            print()
            return

        self._ok(f"Archivo existe: {self.db_path}")

        # Tamaño
        size_mb = self.db_path.stat().st_size / (1024 * 1024)
        self._ok(f"Tamaño: {size_mb:.2f} MB")

        # Conectar y verificar
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verificar tabla
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='informes_ihq'")
            if cursor.fetchone():
                self._ok("Tabla 'informes_ihq' existe")

                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM informes_ihq")
                count = cursor.fetchone()[0]
                self._ok(f"Registros: {count}")

                # Contar columnas
                cursor.execute("PRAGMA table_info(informes_ihq)")
                columnas = cursor.fetchall()
                self._ok(f"Columnas: {len(columnas)}")

                # Verificar columnas IHQ
                ihq_cols = [c[1] for c in columnas if c[1].startswith('IHQ_')]
                self._ok(f"Columnas IHQ (biomarcadores): {len(ihq_cols)}")

                # Verificar duplicados
                cursor.execute('''
                    SELECT "Numero de caso", COUNT(*) as count
                    FROM informes_ihq
                    GROUP BY "Numero de caso"
                    HAVING count > 1
                ''')
                duplicados = cursor.fetchall()
                if duplicados:
                    self._warning(f"{len(duplicados)} casos duplicados encontrados")
                else:
                    self._ok("Sin duplicados")

            else:
                self._error("Tabla 'informes_ihq' NO existe")

            conn.close()

        except Exception as e:
            self._error(f"Error conectando a BD: {e}")

        print()

    def _verificar_paths(self):
        """Verifica paths críticos del sistema"""
        print("📁 VERIFICANDO PATHS DEL SISTEMA")
        print("-" * 80)

        paths_criticos = {
            'PDFs entrada': PROJECT_ROOT / 'pdfs_patologia',
            'Debug maps': self.debug_maps_dir,
            'Core modules': self.core_dir,
            'Herramientas IA': PROJECT_ROOT / 'herramientas_ia',
            'Exportaciones': Path.home() / 'Documents' / 'EVARISIS Exportaciones',
        }

        for nombre, path in paths_criticos.items():
            if path.exists():
                if path.is_dir():
                    archivos = list(path.glob('*'))
                    self._ok(f"{nombre}: {path} ({len(archivos)} archivos)")
                else:
                    self._ok(f"{nombre}: {path}")
            else:
                self._warning(f"{nombre}: {path} NO existe")

        print()

    def _verificar_configuraciones(self):
        """Verifica configuraciones del proyecto"""
        print("⚙️ VERIFICANDO CONFIGURACIONES")
        print("-" * 80)

        # CLAUDE.md
        claude_md = PROJECT_ROOT / "CLAUDE.md"
        if claude_md.exists():
            self._ok("CLAUDE.md existe")
            # Verificar versión
            content = claude_md.read_text(encoding='utf-8')
            version_match = re.search(r'Versión:\s*(\d+\.\d+\.\d+)', content)
            if version_match:
                self._ok(f"Versión detectada: {version_match.group(1)}")
        else:
            self._warning("CLAUDE.md NO encontrado")

        # config/version_info.py
        version_info = PROJECT_ROOT / "config" / "version_info.py"
        if version_info.exists():
            self._ok("version_info.py existe")
        else:
            self._warning("version_info.py NO encontrado")

        # .claude/agents/
        agents_dir = PROJECT_ROOT / ".claude" / "agents"
        if agents_dir.exists():
            agents = list(agents_dir.glob("*.md"))
            self._ok(f"Agentes configurados: {len(agents)}")
            for agent in agents:
                self._info(f"  - {agent.stem}")
        else:
            self._warning("Directorio .claude/agents/ NO encontrado")

        print()

    def _verificar_dependencias_core(self):
        """Verifica imports y dependencias de core/"""
        print("🔗 VERIFICANDO DEPENDENCIAS DE CORE")
        print("-" * 80)

        core_files = list(self.core_dir.rglob("*.py"))

        if not core_files:
            self._error("No se encontraron archivos Python en core/")
            print()
            return

        self._ok(f"Archivos Python en core/: {len(core_files)}")

        # Analizar imports
        imports_externos = set()
        imports_internos = set()
        imports_circulares = []

        for py_file in core_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if not alias.name.startswith('core'):
                                imports_externos.add(alias.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('core'):
                            imports_internos.add(node.module)
                        elif node.module:
                            imports_externos.add(node.module.split('.')[0])

            except Exception as e:
                self._warning(f"Error parseando {py_file.name}: {e}")

        self._ok(f"Imports externos únicos: {len(imports_externos)}")
        self._ok(f"Imports internos (core): {len(imports_internos)}")

        # Verificar imports externos disponibles
        faltan = []
        for modulo in imports_externos:
            try:
                importlib.import_module(modulo)
            except ImportError:
                faltan.append(modulo)

        if faltan:
            self._error(f"Módulos faltantes: {', '.join(faltan)}")
        else:
            self._ok("Todos los módulos externos disponibles")

        print()

    # ========== 2. ANÁLISIS DE CÓDIGO ==========

    def analizar_codigo_redundante(self):
        """Detecta código duplicado y redundante"""
        print(f"\n{'='*80}")
        print("🔍 ANÁLISIS DE CÓDIGO REDUNDANTE")
        print(f"{'='*80}\n")

        core_files = list(self.core_dir.rglob("*.py"))

        # 1. Funciones duplicadas (mismo nombre)
        funciones_por_nombre = defaultdict(list)

        for py_file in core_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        funciones_por_nombre[node.name].append(py_file.name)

            except Exception as e:
                self._warning(f"Error parseando {py_file.name}: {e}")

        # Reportar duplicados
        duplicadas = {nombre: archivos for nombre, archivos in funciones_por_nombre.items() if len(archivos) > 1}

        if duplicadas:
            print("⚠️  FUNCIONES DUPLICADAS (mismo nombre en múltiples archivos):")
            for nombre, archivos in sorted(duplicadas.items()):
                print(f"\n  Función: {nombre}")
                for archivo in archivos:
                    print(f"    - {archivo}")
        else:
            print("✅ No se detectaron funciones duplicadas")

        # 2. Imports no utilizados
        print(f"\n{'-'*80}")
        print("IMPORTS NO UTILIZADOS:")
        print(f"{'-'*80}\n")

        for py_file in core_files[:5]:  # Limitar a 5 para no saturar
            self._analizar_imports_no_usados(py_file)

    def _analizar_imports_no_usados(self, py_file: Path):
        """Analiza imports no utilizados en un archivo"""
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
                tree = ast.parse(contenido)

            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        nombre = alias.asname if alias.asname else alias.name
                        imports.add(nombre.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        nombre = alias.asname if alias.asname else alias.name
                        imports.add(nombre)

            # Buscar uso de cada import
            no_usados = []
            for imp in imports:
                # Buscar apariciones (simple, no perfecto)
                pattern = rf'\b{re.escape(imp)}\b'
                matches = re.findall(pattern, contenido)
                # Si solo aparece 1 vez (el import mismo), no se usa
                if len(matches) <= 1:
                    no_usados.append(imp)

            if no_usados:
                print(f"  {py_file.name}:")
                for imp in no_usados:
                    print(f"    - {imp}")

        except Exception as e:
            pass

    def sugerir_modularizacion(self):
        """Sugiere oportunidades de modularización"""
        print(f"\n{'='*80}")
        print("📦 SUGERENCIAS DE MODULARIZACIÓN")
        print(f"{'='*80}\n")

        core_files = list(self.core_dir.rglob("*.py"))

        archivos_grandes = []

        for py_file in core_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    num_lineas = len(lineas)

                if num_lineas > 500:
                    # Contar funciones
                    tree = ast.parse(''.join(lineas))
                    funciones = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    clases = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]

                    archivos_grandes.append({
                        'archivo': py_file.name,
                        'lineas': num_lineas,
                        'funciones': len(funciones),
                        'clases': len(clases)
                    })

            except Exception as e:
                pass

        if archivos_grandes:
            print("⚠️  ARCHIVOS GRANDES (>500 líneas) - Considerar modularizar:\n")
            for info in sorted(archivos_grandes, key=lambda x: x['lineas'], reverse=True):
                print(f"  {info['archivo']}: {info['lineas']} líneas")
                print(f"    - {info['funciones']} funciones, {info['clases']} clases")
                print(f"    💡 Sugerencia: Dividir en módulos más pequeños")
                print()
        else:
            print("✅ Todos los archivos tienen tamaño adecuado (<500 líneas)")

    def identificar_funciones_no_usadas(self):
        """Identifica funciones que no se llaman en ningún lado"""
        print(f"\n{'='*80}")
        print("🔍 IDENTIFICANDO FUNCIONES NO UTILIZADAS")
        print(f"{'='*80}\n")

        core_files = list(self.core_dir.rglob("*.py"))

        # 1. Recolectar todas las funciones definidas
        funciones_definidas = set()
        for py_file in core_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if not node.name.startswith('_'):  # Ignorar privadas
                            funciones_definidas.add(node.name)

            except Exception:
                pass

        # 2. Buscar llamadas a esas funciones
        funciones_llamadas = set()
        for py_file in core_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                for func in funciones_definidas:
                    if re.search(rf'\b{re.escape(func)}\s*\(', contenido):
                        funciones_llamadas.add(func)

            except Exception:
                pass

        # 3. Reportar no usadas
        no_usadas = funciones_definidas - funciones_llamadas

        if no_usadas:
            print(f"⚠️  FUNCIONES POTENCIALMENTE NO UTILIZADAS ({len(no_usadas)}):\n")
            for func in sorted(no_usadas):
                print(f"  - {func}()")
            print(f"\n💡 Nota: Revisar manualmente, pueden ser llamadas dinámicamente")
        else:
            print("✅ Todas las funciones públicas están en uso")

    # ========== 3. TRAZABILIDAD DE FLUJO ==========

    def trazar_flujo_procesamiento(self, numero_ihq: Optional[str] = None):
        """Traza el flujo completo de procesamiento"""
        print(f"\n{'='*80}")
        print("📊 TRAZABILIDAD DE FLUJO DE PROCESAMIENTO")
        print(f"{'='*80}\n")

        if numero_ihq:
            print(f"Caso: {numero_ihq}\n")
            self._trazar_flujo_caso(numero_ihq)
        else:
            print("FLUJO GENERAL DEL SISTEMA:\n")
            self._trazar_flujo_general()

    def _trazar_flujo_caso(self, numero_ihq: str):
        """Traza flujo de un caso específico"""
        # Buscar debug_map
        debug_map_pattern = f"debug_map_{numero_ihq}_*.json"
        debug_maps = list(self.debug_maps_dir.glob(debug_map_pattern))

        if not debug_maps:
            print(f"❌ No se encontró debug_map para {numero_ihq}")
            return

        debug_map_file = max(debug_maps, key=lambda p: p.stat().st_mtime)

        try:
            with open(debug_map_file, 'r', encoding='utf-8') as f:
                debug_data = json.load(f)

            print("FLUJO EJECUTADO:")
            print(f"{'='*80}\n")

            # 1. PDF → OCR
            if 'ocr' in debug_data:
                ocr_info = debug_data['ocr']
                texto_len = len(ocr_info.get('texto_consolidado', ''))
                print(f"1️⃣  PDF → OCR")
                print(f"   ✓ Texto extraído: {texto_len:,} caracteres")
                if 'metadata' in ocr_info:
                    print(f"   ✓ PDF: {ocr_info['metadata'].get('pdf_path', 'N/A')}")
                print()

            # 2. OCR → Extracción
            if 'extraccion' in debug_data:
                extraccion = debug_data['extraccion']
                print(f"2️⃣  OCR → EXTRACCIÓN")
                for extractor, datos in extraccion.items():
                    if isinstance(datos, dict):
                        campos = len(datos)
                        print(f"   ✓ {extractor}: {campos} campos extraídos")
                print()

            # 3. Extracción → BD
            if 'base_datos' in debug_data:
                bd_info = debug_data['base_datos']
                if 'datos_guardados' in bd_info:
                    campos_bd = len(bd_info['datos_guardados'])
                    print(f"3️⃣  EXTRACCIÓN → BASE DE DATOS")
                    print(f"   ✓ Campos guardados: {campos_bd}")

                    # Mostrar campos críticos
                    if 'campos_criticos' in bd_info:
                        print(f"   ✓ Campos críticos:")
                        for campo, valor in bd_info['campos_criticos'].items():
                            if valor and str(valor).strip():
                                val_str = str(valor)[:50]
                                print(f"      - {campo}: {val_str}")
                print()

            # 4. Métricas
            if 'metricas' in debug_data:
                metricas = debug_data['metricas']
                print(f"4️⃣  MÉTRICAS DE RENDIMIENTO")
                print(f"   ⏱️  Tiempo OCR: {metricas.get('tiempo_ocr_segundos', 0):.2f}s")
                print(f"   ⏱️  Tiempo extracción: {metricas.get('tiempo_extraccion_segundos', 0):.2f}s")
                print(f"   ⏱️  Tiempo total: {metricas.get('tiempo_total_segundos', 0):.2f}s")
                print()

        except Exception as e:
            print(f"❌ Error leyendo debug_map: {e}")

    def _trazar_flujo_general(self):
        """Traza flujo general del sistema"""
        print("PDF (archivo) → OCR (Tesseract)")
        print("     ↓")
        print("OCR Text → Segmentación (múltiples informes)")
        print("     ↓")
        print("Segmentos → Extractores")
        print("     ├─ patient_extractor.py")
        print("     ├─ medical_extractor.py")
        print("     └─ biomarker_extractor.py")
        print("     ↓")
        print("Datos extraídos → unified_extractor.py (combina)")
        print("     ↓")
        print("Datos combinados → Validadores")
        print("     ├─ validador_medico_servicio.py")
        print("     └─ validation_checker.py")
        print("     ↓")
        print("Datos validados → Mapeo a BD (database_manager.py)")
        print("     ↓")
        print("SQLite (huv_oncologia_NUEVO.db)")
        print("     ↓")
        print("Debug Map (JSON para auditoría)")

    # ========== 4. TESTING DE COMPONENTES ==========

    def probar_componente(self, componente: str, **kwargs):
        """Prueba un componente aislado"""
        print(f"\n{'='*80}")
        print(f"🧪 PROBANDO COMPONENTE: {componente.upper()}")
        print(f"{'='*80}\n")

        if componente == 'ocr':
            self._probar_ocr(kwargs.get('pdf_path'))
        elif componente == 'extractor':
            self._probar_extractor(kwargs.get('texto'))
        elif componente == 'mapeo':
            self._probar_mapeo(kwargs.get('datos'))
        elif componente == 'validacion':
            self._probar_validacion(kwargs.get('caso'))
        else:
            print(f"❌ Componente '{componente}' no reconocido")
            print("Componentes disponibles: ocr, extractor, mapeo, validacion")

    def _probar_ocr(self, pdf_path: Optional[str]):
        """Prueba el componente OCR aislado"""
        if not pdf_path:
            print("❌ Se requiere --pdf para probar OCR")
            return

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            print(f"❌ PDF no encontrado: {pdf_path}")
            return

        try:
            from core.processors.ocr_processor import pdf_to_text_enhanced

            print(f"Procesando: {pdf_path.name}")
            print("Ejecutando OCR...\n")

            inicio = datetime.now()
            texto = pdf_to_text_enhanced(str(pdf_path))
            duracion = (datetime.now() - inicio).total_seconds()

            print(f"✅ OCR completado en {duracion:.2f}s")
            print(f"📊 Texto extraído: {len(texto):,} caracteres")
            print(f"📊 Líneas: {texto.count(chr(10)) + 1}")
            print(f"\nPrimeros 500 caracteres:")
            print("-" * 80)
            print(texto[:500])
            print("-" * 80)

        except Exception as e:
            print(f"❌ Error en OCR: {e}")
            import traceback
            traceback.print_exc()

    def _probar_extractor(self, texto: Optional[str]):
        """Prueba el extractor aislado"""
        if not texto:
            print("❌ Se requiere --texto para probar extractor")
            return

        try:
            from core.unified_extractor import extract_ihq_data

            print("Ejecutando extracción...\n")

            inicio = datetime.now()
            datos = extract_ihq_data(texto)
            duracion = (datetime.now() - inicio).total_seconds()

            print(f"✅ Extracción completada en {duracion:.2f}s")
            print(f"📊 Campos extraídos: {len(datos)}")

            print(f"\nCampos con valor:")
            for campo, valor in datos.items():
                if valor and str(valor).strip():
                    val_str = str(valor)[:60]
                    print(f"  - {campo}: {val_str}")

        except Exception as e:
            print(f"❌ Error en extracción: {e}")
            import traceback
            traceback.print_exc()

    def _probar_mapeo(self, datos: Optional[Dict]):
        """Prueba el mapeo a BD aislado"""
        if not datos:
            print("❌ Se requieren datos para probar mapeo")
            return

        try:
            from core.unified_extractor import map_to_database_format

            print("Ejecutando mapeo...\n")

            datos_mapeados = map_to_database_format(datos)

            print(f"✅ Mapeo completado")
            print(f"📊 Campos mapeados: {len(datos_mapeados)}")

            print(f"\nCampos críticos:")
            campos_criticos = ['Numero de caso', 'Primer nombre', 'Organo', 'Diagnostico Principal']
            for campo in campos_criticos:
                valor = datos_mapeados.get(campo, 'N/A')
                print(f"  - {campo}: {valor}")

        except Exception as e:
            print(f"❌ Error en mapeo: {e}")
            import traceback
            traceback.print_exc()

    def _probar_validacion(self, caso: Optional[str]):
        """Prueba validación cruzada de un caso"""
        if not caso:
            print("❌ Se requiere --caso para probar validación")
            return

        try:
            from core.validacion_cruzada import validar_caso_completo

            print(f"Validando caso: {caso}\n")

            resultado = validar_caso_completo(caso)

            if resultado:
                print(f"✅ Validación completada")
                print(f"📊 Resultado:")
                for key, value in resultado.items():
                    print(f"  - {key}: {value}")
            else:
                print(f"❌ No se pudo validar el caso")

        except Exception as e:
            print(f"❌ Error en validación: {e}")
            import traceback
            traceback.print_exc()

    # ========== 5. REPORTES ==========

    def generar_reporte_salud(self, exportar: bool = False):
        """Genera reporte completo de salud del sistema"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        print(f"\n{'='*80}")
        print(f"📊 REPORTE DE SALUD DEL SISTEMA - {timestamp}")
        print(f"{'='*80}\n")

        # Ejecutar todas las verificaciones
        self.verificar_salud_completa()

        if exportar:
            reporte = {
                'timestamp': timestamp,
                'errores': self.errores,
                'warnings': self.warnings,
                'info': self.info
            }

            output_dir = PROJECT_ROOT / "herramientas_ia" / "resultados"
            output_dir.mkdir(exist_ok=True)

            output_file = output_dir / f"reporte_salud_{timestamp}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(reporte, f, ensure_ascii=False, indent=2)

            print(f"\n💾 Reporte exportado: {output_file}")

    # ========== HELPERS INTERNOS ==========

    def _ok(self, mensaje: str):
        """Marca como OK"""
        print(f"  ✅ {mensaje}")
        self.info.append(mensaje)

    def _warning(self, mensaje: str):
        """Marca como WARNING"""
        print(f"  ⚠️  {mensaje}")
        self.warnings.append(mensaje)

    def _error(self, mensaje: str):
        """Marca como ERROR"""
        print(f"  ❌ {mensaje}")
        self.errores.append(mensaje)

    def _info(self, mensaje: str):
        """Info adicional"""
        print(f"  ℹ️  {mensaje}")
        self.info.append(mensaje)

    def _mostrar_resumen(self):
        """Muestra resumen final"""
        print(f"\n{'='*80}")
        print("📋 RESUMEN DE VERIFICACIÓN")
        print(f"{'='*80}\n")

        total_checks = len(self.errores) + len(self.warnings) + len(self.info)

        print(f"Total de checks: {total_checks}")
        print(f"  ✅ OK: {len(self.info)}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")
        print(f"  ❌ Errores: {len(self.errores)}")

        if self.errores:
            print(f"\n⚠️  ERRORES CRÍTICOS:")
            for error in self.errores:
                print(f"  - {error}")

        if not self.errores and not self.warnings:
            print(f"\n{'='*80}")
            print("✅ SISTEMA COMPLETAMENTE OPERATIVO")
            print(f"{'='*80}")
        elif not self.errores:
            print(f"\n{'='*80}")
            print("✅ SISTEMA OPERATIVO CON ADVERTENCIAS MENORES")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print("❌ SISTEMA REQUIERE CORRECCIONES")
            print(f"{'='*80}")

    # ========== FUNCIONALIDADES EXTENDIDAS ==========

    def analizar_complejidad_ciclomatica(self, archivo: Optional[str] = None):
        """Analiza la complejidad ciclomática del código"""
        print(f"\n{'='*80}")
        print("📊 ANÁLISIS DE COMPLEJIDAD CICLOMÁTICA")
        print(f"{'='*80}\n")

        archivos = []
        if archivo:
            archivos = [Path(archivo)]
        else:
            # Analizar todos los archivos core/
            archivos = list(self.core_dir.rglob("*.py"))

        resultados = []

        for archivo_py in archivos:
            try:
                with open(archivo_py, 'r', encoding='utf-8') as f:
                    codigo = f.read()

                tree = ast.parse(codigo)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complejidad = self._calcular_complejidad(node)
                        resultados.append({
                            'archivo': archivo_py.name,
                            'funcion': node.name,
                            'complejidad': complejidad,
                            'linea': node.lineno
                        })

            except Exception as e:
                continue

        # Ordenar por complejidad
        resultados.sort(key=lambda x: x['complejidad'], reverse=True)

        if resultados:
            print("🔴 TOP 15 FUNCIONES MÁS COMPLEJAS:\n")
            for i, r in enumerate(resultados[:15], 1):
                nivel = "🔴" if r['complejidad'] > 10 else "🟡" if r['complejidad'] > 5 else "🟢"
                print(f"{i:2}. {nivel} {r['archivo']:<30} {r['funcion']:<35} CC={r['complejidad']:2} (L{r['linea']})")

            print(f"\n📊 ESTADÍSTICAS:")
            complejidades = [r['complejidad'] for r in resultados]
            print(f"   Promedio: {sum(complejidades) / len(complejidades):.1f}")
            print(f"   Máxima: {max(complejidades)}")
            print(f"   Funciones complejas (CC>10): {len([c for c in complejidades if c > 10])}")

    def _calcular_complejidad(self, node):
        """Calcula complejidad ciclomática de un nodo"""
        complejidad = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complejidad += 1
            elif isinstance(child, ast.BoolOp):
                complejidad += len(child.values) - 1
        return complejidad

    def detectar_code_smells(self):
        """Detecta code smells en el código"""
        print(f"\n{'='*80}")
        print("👃 DETECCIÓN DE CODE SMELLS")
        print(f"{'='*80}\n")

        smells = []

        # Analizar archivos core/
        for archivo_py in self.core_dir.rglob("*.py"):
            try:
                with open(archivo_py, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                    codigo = ''.join(lineas)

                # Smell 1: Funciones muy largas (>100 líneas)
                tree = ast.parse(codigo)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if hasattr(node, 'end_lineno') and node.end_lineno:
                            longitud = node.end_lineno - node.lineno
                            if longitud > 100:
                                smells.append({
                                    'tipo': 'Función larga',
                                    'archivo': archivo_py.name,
                                    'detalle': f'{node.name} ({longitud} líneas)',
                                    'linea': node.lineno
                                })

                # Smell 2: Líneas muy largas (>120 caracteres)
                for i, linea in enumerate(lineas, 1):
                    if len(linea.rstrip()) > 120:
                        smells.append({
                            'tipo': 'Línea larga',
                            'archivo': archivo_py.name,
                            'detalle': f'{len(linea.rstrip())} chars',
                            'linea': i
                        })

                # Smell 3: Muchos argumentos (>5)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        num_args = len(node.args.args)
                        if num_args > 5:
                            smells.append({
                                'tipo': 'Muchos argumentos',
                                'archivo': archivo_py.name,
                                'detalle': f'{node.name} ({num_args} args)',
                                'linea': node.lineno
                            })

                # Smell 4: Código duplicado (importaciones repetidas)
                imports = [n for n in ast.walk(tree) if isinstance(n, ast.Import)]
                if len(imports) > 20:
                    smells.append({
                        'tipo': 'Muchos imports',
                        'archivo': archivo_py.name,
                        'detalle': f'{len(imports)} imports',
                        'linea': 1
                    })

            except Exception as e:
                continue

        # Agrupar por tipo
        smells_por_tipo = defaultdict(list)
        for smell in smells:
            smells_por_tipo[smell['tipo']].append(smell)

        print(f"📊 CODE SMELLS DETECTADOS: {len(smells)}\n")

        for tipo, items in smells_por_tipo.items():
            print(f"🔴 {tipo}: {len(items)}")
            for item in items[:5]:  # Mostrar primeros 5
                print(f"   • {item['archivo']}:{item['linea']} - {item['detalle']}")
            if len(items) > 5:
                print(f"   ... y {len(items) - 5} más")
            print()

    def benchmark_rendimiento(self, componente: str = 'all'):
        """Benchmark de rendimiento de componentes"""
        print(f"\n{'='*80}")
        print(f"⚡ BENCHMARK DE RENDIMIENTO")
        print(f"{'='*80}\n")

        import time

        resultados = []

        if componente in ['all', 'ocr']:
            # Test OCR
            pdf_ejemplo = list((PROJECT_ROOT / "pdfs_patologia").glob("*.pdf"))
            if pdf_ejemplo:
                try:
                    from core.processors.ocr_processor import pdf_to_text_enhanced

                    print("Testing OCR processor...")
                    inicio = time.time()
                    texto = pdf_to_text_enhanced(str(pdf_ejemplo[0]))
                    duracion = time.time() - inicio

                    resultados.append({
                        'componente': 'OCR',
                        'operacion': 'pdf_to_text_enhanced',
                        'duracion': duracion,
                        'resultado': f'{len(texto)} chars'
                    })
                except Exception as e:
                    resultados.append({
                        'componente': 'OCR',
                        'operacion': 'pdf_to_text_enhanced',
                        'duracion': 0,
                        'resultado': f'ERROR: {e}'
                    })

        if componente in ['all', 'extractor']:
            # Test Extractor
            try:
                from core.unified_extractor import extract_ihq_data

                texto_ejemplo = "CASO IHQ250001 PACIENTE: JUAN PEREZ ORGANO: PULMON"
                print("Testing Unified Extractor...")
                inicio = time.time()
                datos = extract_ihq_data(texto_ejemplo)
                duracion = time.time() - inicio

                resultados.append({
                    'componente': 'Extractor',
                    'operacion': 'extract_ihq_data',
                    'duracion': duracion,
                    'resultado': f'{len(datos)} campos'
                })
            except Exception as e:
                resultados.append({
                    'componente': 'Extractor',
                    'operacion': 'extract_ihq_data',
                    'duracion': 0,
                    'resultado': f'ERROR: {e}'
                })

        if componente in ['all', 'database']:
            # Test Database
            try:
                import sqlite3
                print("Testing Database queries...")
                inicio = time.time()
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM informes_ihq LIMIT 100")
                rows = cursor.fetchall()
                conn.close()
                duracion = time.time() - inicio

                resultados.append({
                    'componente': 'Database',
                    'operacion': 'SELECT 100 rows',
                    'duracion': duracion,
                    'resultado': f'{len(rows)} rows'
                })
            except Exception as e:
                resultados.append({
                    'componente': 'Database',
                    'operacion': 'SELECT',
                    'duracion': 0,
                    'resultado': f'ERROR: {e}'
                })

        # Mostrar resultados
        print(f"\n📊 RESULTADOS DEL BENCHMARK:\n")
        print(f"{'Componente':<15} {'Operación':<25} {'Tiempo':<12} {'Resultado'}")
        print("-" * 80)

        for r in resultados:
            tiempo_str = f"{r['duracion']:.3f}s" if r['duracion'] > 0 else "ERROR"
            print(f"{r['componente']:<15} {r['operacion']:<25} {tiempo_str:<12} {r['resultado']}")

    def analizar_uso_memoria(self):
        """Analiza el uso de memoria del sistema"""
        print(f"\n{'='*80}")
        print("💾 ANÁLISIS DE USO DE MEMORIA")
        print(f"{'='*80}\n")

        try:
            import psutil
            import gc

            # Forzar garbage collection
            gc.collect()

            # Memoria del proceso actual
            proceso = psutil.Process()
            mem_info = proceso.memory_info()

            print(f"📊 MEMORIA DEL PROCESO:")
            print(f"   RSS (Resident Set Size): {mem_info.rss / 1024 / 1024:.2f} MB")
            print(f"   VMS (Virtual Memory Size): {mem_info.vms / 1024 / 1024:.2f} MB")

            # Memoria del sistema
            mem_sistema = psutil.virtual_memory()
            print(f"\n📊 MEMORIA DEL SISTEMA:")
            print(f"   Total: {mem_sistema.total / 1024 / 1024 / 1024:.2f} GB")
            print(f"   Disponible: {mem_sistema.available / 1024 / 1024 / 1024:.2f} GB")
            print(f"   Usada: {mem_sistema.used / 1024 / 1024 / 1024:.2f} GB ({mem_sistema.percent}%)")

            # Objetos en memoria
            import sys
            print(f"\n📊 OBJETOS EN MEMORIA:")
            print(f"   Total objetos rastreados: {len(gc.get_objects())}")

        except ImportError:
            print("⚠️  Requiere: pip install psutil")

    def detectar_memory_leaks(self):
        """Detecta posibles fugas de memoria"""
        print(f"\n{'='*80}")
        print("🔍 DETECCIÓN DE MEMORY LEAKS")
        print(f"{'='*80}\n")

        try:
            import gc
            import sys

            # Obtener objetos no recolectables
            gc.collect()
            garbage = gc.garbage

            if garbage:
                print(f"⚠️  {len(garbage)} objetos no recolectables detectados:\n")
                tipos = defaultdict(int)
                for obj in garbage:
                    tipos[type(obj).__name__] += 1

                for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
                    print(f"   • {tipo}: {count}")
            else:
                print("✅ No se detectaron fugas de memoria evidentes")

            # Verificar referencias circulares
            print(f"\n🔍 VERIFICANDO REFERENCIAS CIRCULARES...")
            gc.set_debug(gc.DEBUG_SAVEALL)
            gc.collect()

            if gc.garbage:
                print(f"⚠️  {len(gc.garbage)} referencias circulares detectadas")
            else:
                print("✅ No se detectaron referencias circulares")

            gc.set_debug(0)

        except Exception as e:
            print(f"❌ Error: {e}")

    def validar_encoding_archivos(self):
        """Valida que todos los archivos usen UTF-8"""
        print(f"\n{'='*80}")
        print("📝 VALIDACIÓN DE ENCODING UTF-8")
        print(f"{'='*80}\n")

        archivos_problematicos = []

        # Verificar archivos .py
        for archivo in self.project_root.rglob("*.py"):
            if "LEGACY" in str(archivo) or ".venv" in str(archivo):
                continue

            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                # Verificar BOM UTF-8
                if contenido.startswith('\ufeff'):
                    archivos_problematicos.append({
                        'archivo': archivo.relative_to(self.project_root),
                        'problema': 'UTF-8 BOM detectado'
                    })

                # Verificar declaración de encoding
                primera_linea = contenido.split('\n')[0] if contenido else ''
                segunda_linea = contenido.split('\n')[1] if len(contenido.split('\n')) > 1 else ''

                tiene_encoding = ('coding' in primera_linea or 'coding' in segunda_linea)

                if not tiene_encoding:
                    archivos_problematicos.append({
                        'archivo': archivo.relative_to(self.project_root),
                        'problema': 'Sin declaración # -*- coding: utf-8 -*-'
                    })

            except UnicodeDecodeError:
                archivos_problematicos.append({
                    'archivo': archivo.relative_to(self.project_root),
                    'problema': 'No es UTF-8 válido'
                })
            except Exception as e:
                continue

        if archivos_problematicos:
            print(f"⚠️  {len(archivos_problematicos)} archivos con problemas de encoding:\n")
            for item in archivos_problematicos[:20]:
                print(f"   • {item['archivo']}: {item['problema']}")
            if len(archivos_problematicos) > 20:
                print(f"\n   ... y {len(archivos_problematicos) - 20} más")
        else:
            print("✅ Todos los archivos usan UTF-8 correctamente")

    def generar_diagrama_flujo(self, exportar: bool = False):
        """Genera diagrama de flujo del sistema"""
        print(f"\n{'='*80}")
        print("📊 DIAGRAMA DE FLUJO DEL SISTEMA EVARISIS")
        print(f"{'='*80}\n")

        diagrama = """
┌─────────────────────────────────────────────────────────────────────┐
│                         FLUJO EVARISIS V5                           │
└─────────────────────────────────────────────────────────────────────┘

1. ENTRADA DE DATOS
   ┌──────────────┐
   │  PDF IHQ     │
   └──────┬───────┘
          │
          v
   ┌──────────────────────┐
   │  OCR Processor       │  ← pdf2image + pytesseract
   │  (ocr_processor.py)  │
   └──────┬───────────────┘
          │
          v
   ┌──────────────────────┐
   │  Texto consolidado   │  ← debug_maps/*/ocr/texto_consolidado
   └──────┬───────────────┘

2. EXTRACCIÓN
          │
          v
   ┌────────────────────────────────────┐
   │  Unified Extractor                 │
   │  (unified_extractor.py)            │
   ├────────────────────────────────────┤
   │  • patient_extractor.py (11 func)  │
   │  • medical_extractor.py (21 func)  │
   │  • biomarker_extractor.py (10 func)│
   └──────┬─────────────────────────────┘
          │
          v
   ┌──────────────────────┐
   │  Datos estructurados │  ← 129 campos
   └──────┬───────────────┘

3. VALIDACIÓN
          │
          v
   ┌──────────────────────────┐
   │  Validación Cruzada      │
   │  (validacion_cruzada.py) │
   └──────┬───────────────────┘
          │
          v
   ┌──────────────────────────┐
   │  Quality Detector        │
   │  (quality_detector.py)   │
   └──────┬───────────────────┘

4. CORRECCIÓN IA (Opcional)
          │
          v
   ┌──────────────────────────┐
   │  Auditoría IA            │
   │  (auditoria_ia.py)       │
   │  ← LM Studio GPT-OSS-20B │
   └──────┬───────────────────┘

5. PERSISTENCIA
          │
          v
   ┌──────────────────────────┐
   │  Database Manager        │
   │  (database_manager.py)   │
   └──────┬───────────────────┘
          │
          v
   ┌──────────────────────────┐
   │  SQLite Database         │
   │  huv_oncologia_NUEVO.db  │
   │  129 columnas, 47 casos  │
   └──────────────────────────┘

6. HERRAMIENTAS DE GESTIÓN

   ┌───────────────────┐  ┌──────────────────┐  ┌─────────────────┐
   │ auditor_sistema   │  │ gestor_base_datos│  │ inspector_      │
   │ Valida PDF vs BD  │  │ Queries avanzadas│  │ sistema         │
   │ 934 líneas        │  │ 1074 líneas      │  │ Health checks   │
   └───────────────────┘  └──────────────────┘  └─────────────────┘

   ┌───────────────────┐
   │ editor_core       │
   │ Edición inteligente│
   │ de extractores    │
   └───────────────────┘
"""

        print(diagrama)

        if exportar:
            output_dir = PROJECT_ROOT / "herramientas_ia" / "resultados"
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"diagrama_flujo_{timestamp}.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(diagrama)

            print(f"\n💾 Diagrama exportado: {output_file}")


def main():
    """CLI principal"""
    parser = argparse.ArgumentParser(
        description="🔍 Inspector de Sistema EVARISIS - Diagnóstico Completo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

HEALTH CHECK:
  python inspector_sistema.py --salud                    # Verificación completa
  python inspector_sistema.py --salud --exportar         # + exportar JSON

ANÁLISIS DE CÓDIGO:
  python inspector_sistema.py --codigo-redundante        # Detectar duplicados
  python inspector_sistema.py --modularizacion           # Sugerencias
  python inspector_sistema.py --funciones-no-usadas      # Funciones huérfanas

TRAZABILIDAD:
  python inspector_sistema.py --flujo                    # Flujo general
  python inspector_sistema.py --flujo --caso IHQ250001   # Flujo de caso

TESTING:
  python inspector_sistema.py --probar ocr --pdf pdfs_patologia/ejemplo.pdf
  python inspector_sistema.py --probar extractor --texto "texto ejemplo"
  python inspector_sistema.py --probar validacion --caso IHQ250001

REPORTES:
  python inspector_sistema.py --reporte-salud            # Reporte completo
  python inspector_sistema.py --reporte-salud --exportar # + JSON

ANÁLISIS AVANZADO:
  python inspector_sistema.py --complejidad              # Complejidad ciclomática
  python inspector_sistema.py --complejidad --archivo core/ihq_processor.py
  python inspector_sistema.py --code-smells              # Detectar malas prácticas
  python inspector_sistema.py --benchmark                # Benchmark componentes
  python inspector_sistema.py --benchmark --componente ocr

MEMORIA:
  python inspector_sistema.py --analizar-memoria         # Uso de memoria
  python inspector_sistema.py --detectar-leaks           # Memory leaks

CALIDAD DE CÓDIGO:
  python inspector_sistema.py --validar-encoding         # Validar UTF-8
  python inspector_sistema.py --diagrama                 # Diagrama de flujo
  python inspector_sistema.py --diagrama --exportar      # + exportar
        """
    )

    # Verificación básica
    parser.add_argument("--salud", action="store_true", help="Verificación de salud completa")
    parser.add_argument("--codigo-redundante", action="store_true", help="Analizar código redundante")
    parser.add_argument("--modularizacion", action="store_true", help="Sugerencias de modularización")
    parser.add_argument("--funciones-no-usadas", action="store_true", help="Identificar funciones no usadas")

    # Trazabilidad
    parser.add_argument("--flujo", action="store_true", help="Trazar flujo de procesamiento")
    parser.add_argument("--caso", help="Caso específico para trazabilidad")

    # Testing
    parser.add_argument("--probar", choices=['ocr', 'extractor', 'mapeo', 'validacion'], help="Probar componente")
    parser.add_argument("--pdf", help="PDF para probar OCR")
    parser.add_argument("--texto", help="Texto para probar extractor")

    # Reportes
    parser.add_argument("--reporte-salud", action="store_true", help="Generar reporte de salud")
    parser.add_argument("--exportar", action="store_true", help="Exportar reporte a JSON")

    # Análisis avanzado
    parser.add_argument("--complejidad", action="store_true", help="Analizar complejidad ciclomática")
    parser.add_argument("--archivo", help="Archivo específico para análisis")
    parser.add_argument("--code-smells", action="store_true", help="Detectar code smells")
    parser.add_argument("--benchmark", action="store_true", help="Benchmark de rendimiento")
    parser.add_argument("--componente", choices=['all', 'ocr', 'extractor', 'database'], default='all', help="Componente específico")

    # Memoria
    parser.add_argument("--analizar-memoria", action="store_true", help="Analizar uso de memoria")
    parser.add_argument("--detectar-leaks", action="store_true", help="Detectar memory leaks")

    # Calidad
    parser.add_argument("--validar-encoding", action="store_true", help="Validar encoding UTF-8")
    parser.add_argument("--diagrama", action="store_true", help="Generar diagrama de flujo")

    args = parser.parse_args()

    try:
        inspector = InspectorSistema()

        if args.salud:
            inspector.verificar_salud_completa()

        elif args.codigo_redundante:
            inspector.analizar_codigo_redundante()

        elif args.modularizacion:
            inspector.sugerir_modularizacion()

        elif args.funciones_no_usadas:
            inspector.identificar_funciones_no_usadas()

        elif args.flujo:
            inspector.trazar_flujo_procesamiento(args.caso)

        elif args.probar:
            kwargs = {
                'pdf_path': args.pdf,
                'texto': args.texto,
                'caso': args.caso
            }
            inspector.probar_componente(args.probar, **kwargs)

        elif args.reporte_salud:
            inspector.generar_reporte_salud(exportar=args.exportar)

        elif args.complejidad:
            inspector.analizar_complejidad_ciclomatica(archivo=args.archivo)

        elif args.code_smells:
            inspector.detectar_code_smells()

        elif args.benchmark:
            inspector.benchmark_rendimiento(componente=args.componente)

        elif args.analizar_memoria:
            inspector.analizar_uso_memoria()

        elif args.detectar_leaks:
            inspector.detectar_memory_leaks()

        elif args.validar_encoding:
            inspector.validar_encoding_archivos()

        elif args.diagrama:
            inspector.generar_diagrama_flujo(exportar=args.exportar)

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
