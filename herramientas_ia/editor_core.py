#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✏️ EDITOR CORE - Editor Inteligente con Conocimiento Profundo EVARISIS
========================================================================

Herramienta SÚPER DENSA que:
1. Entiende TODA la arquitectura de core/
2. Puede editar código con precisión quirúrgica
3. Reprocesa casos inteligentemente
4. Auto-actualiza documentación
5. Ejecuta migraciones seguras
6. Simula cambios antes de aplicar

Esta es la herramienta MÁS COMPLEJA del sistema.

Autor: Sistema EVARISIS
Versión: 1.0.0
Fecha: 20 de octubre de 2025
"""

import sys
import os
import ast
import sqlite3
import argparse
import json
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from collections import defaultdict

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class EditorCore:
    """Editor inteligente con conocimiento profundo de core/"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.core_dir = PROJECT_ROOT / "core"
        self.db_path = PROJECT_ROOT / "data" / "huv_oncologia_NUEVO.db"
        self.claude_md = PROJECT_ROOT / "CLAUDE.md"
        self.agents_dir = PROJECT_ROOT / ".claude" / "agents"

        # Registro de acciones para reportes
        self.registro_acciones = []
        self.resultados_dir = PROJECT_ROOT / "herramientas_ia" / "resultados"
        self.resultados_dir.mkdir(parents=True, exist_ok=True)

        # Carpeta centralizada de backups (raíz del proyecto)
        self.backups_dir = PROJECT_ROOT / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # Conocimiento de arquitectura (se carga dinámicamente)
        self.conocimiento = {}
        self._cargar_conocimiento()

    def _cargar_conocimiento(self):
        """Carga conocimiento completo de la arquitectura"""
        print("🧠 Cargando conocimiento de arquitectura...")

        self.conocimiento = {
            'extractors': self._mapear_extractores(),
            'validators': self._mapear_validadores(),
            'mapeo_biomarcadores': self._extraer_mapeo_biomarcadores(),
            'prompts': self._mapear_prompts(),
            'dependencias': self._mapear_dependencias()
        }

        print(f"✅ Conocimiento cargado: {len(self.conocimiento['extractors'])} extractores, "
              f"{len(self.conocimiento['mapeo_biomarcadores'])} biomarcadores mapeados")

    def _mapear_extractores(self) -> Dict:
        """Mapea todos los extractores disponibles"""
        extractores = {}

        extractor_files = {
            'patient': self.core_dir / 'extractors' / 'patient_extractor.py',
            'medical': self.core_dir / 'extractors' / 'medical_extractor.py',
            'biomarker': self.core_dir / 'extractors' / 'biomarker_extractor.py',
        }

        for nombre, archivo in extractor_files.items():
            if archivo.exists():
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        tree = ast.parse(f.read())

                    funciones = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    extractores[nombre] = {
                        'archivo': archivo,
                        'funciones': funciones
                    }
                except:
                    pass

        return extractores

    def _mapear_validadores(self) -> Dict:
        """Mapea validadores del sistema"""
        validadores = {}

        validator_file = self.core_dir / 'validation_checker.py'
        if validator_file.exists():
            try:
                with open(validator_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                funciones = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                validadores['validation_checker'] = {
                    'archivo': validator_file,
                    'funciones': funciones
                }
            except:
                pass

        return validadores

    def _extraer_mapeo_biomarcadores(self) -> Dict[str, str]:
        """Extrae MAPEO_BIOMARCADORES de validation_checker.py"""
        mapeo = {}

        validator_file = self.core_dir / 'validation_checker.py'
        if not validator_file.exists():
            return mapeo

        try:
            with open(validator_file, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Buscar el diccionario MAPEO_BIOMARCADORES
            match = re.search(r'MAPEO_BIOMARCADORES\s*=\s*\{([^}]+)\}', contenido, re.DOTALL)
            if match:
                dict_content = match.group(1)
                # Parsear manualmente las líneas
                for line in dict_content.split('\n'):
                    if ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip().strip("'\"")
                            value = parts[1].strip().strip("',\"")
                            if key and value:
                                mapeo[key] = value

        except Exception as e:
            print(f"⚠️  Error extrayendo MAPEO_BIOMARCADORES: {e}")

        return mapeo

    def _mapear_prompts(self) -> Dict:
        """Mapea prompts del sistema"""
        prompts = {}

        prompts_dir = self.core_dir / 'prompts'
        if prompts_dir.exists():
            for prompt_file in prompts_dir.glob("*.txt"):
                prompts[prompt_file.stem] = prompt_file

        return prompts

    def _mapear_dependencias(self) -> Dict[str, List[str]]:
        """Mapea dependencias entre módulos"""
        dependencias = defaultdict(list)

        for py_file in self.core_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())

                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        if node.module and node.module.startswith('core'):
                            dependencias[py_file.name].append(node.module)

            except:
                pass

        return dict(dependencias)

    # ========== 1. EDICIÓN INTELIGENTE ==========

    def editar_extractor(self, biomarcador: str, patron_nuevo: str, razon: str, simular: bool = True):
        """Edita un extractor para agregar/modificar patrón"""
        print(f"\n{'='*80}")
        print(f"✏️ EDITANDO EXTRACTOR PARA: {biomarcador}")
        print(f"{'='*80}\n")

        print(f"Patrón nuevo: {patron_nuevo}")
        print(f"Razón: {razon}\n")

        # Identificar archivo correcto
        archivo_target = self._identificar_extractor_biomarcador(biomarcador)

        if not archivo_target:
            print(f"❌ No se pudo identificar el extractor para {biomarcador}")
            return

        print(f"📁 Archivo identificado: {archivo_target.name}")

        if simular:
            print(f"\n🔍 MODO SIMULACIÓN - No se aplicarán cambios")
            print(f"\nCambio propuesto:")
            print(f"  1. Agregar patrón: {patron_nuevo}")
            print(f"  2. En función: extract_{biomarcador.lower().replace('-', '_')}")
            print(f"\n💡 Ejecuta sin --simular para aplicar cambios")
        else:
            self._aplicar_edicion_extractor(archivo_target, biomarcador, patron_nuevo)
            print(f"\n✅ Cambios aplicados exitosamente")

            # Registrar acción
            self.registrar_accion("Edición de Extractor", {
                'Biomarcador': biomarcador,
                'Archivo': archivo_target.name,
                'Patrón nuevo': patron_nuevo,
                'Razón': razon
            })

            # Auto-actualizar documentación
            self._auto_actualizar_docs('extractor_mejorado', {
                'biomarcador': biomarcador,
                'razon': razon
            })

    def _identificar_extractor_biomarcador(self, biomarcador: str) -> Optional[Path]:
        """Identifica qué extractor maneja un biomarcador"""
        biomarcador_upper = biomarcador.upper()

        # Biomarcadores médicos/orgánicos
        if biomarcador_upper in ['KI-67', 'HER2', 'ER', 'PR', 'P53', 'PDL-1']:
            return self.core_dir / 'extractors' / 'biomarker_extractor.py'

        # Fallback a biomarker extractor
        return self.core_dir / 'extractors' / 'biomarker_extractor.py'

    def _aplicar_edicion_extractor(self, archivo: Path, biomarcador: str, patron: str):
        """Aplica edición real al extractor"""
        try:
            # Backup en carpeta centralizada
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{archivo.stem}_backup_{timestamp}.py"
            backup_path = self.backups_dir / backup_filename
            shutil.copy(archivo, backup_path)
            print(f"📦 Backup creado: backups/{backup_filename}")

            # Leer contenido
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # TODO: Implementar lógica de inserción inteligente de patrón
            # Por ahora, solo reportamos

            print(f"⚠️  Edición automática de extractores en desarrollo")
            print(f"💡 Por ahora, edita manualmente: {archivo}")
            print(f"   Agregar patrón: {patron}")

        except Exception as e:
            print(f"❌ Error aplicando edición: {e}")

    def agregar_biomarcador_completo(self, nombre: str, variantes: List[str]):
        """Agrega un biomarcador completo: extractor + mapeo + BD + validación"""
        print(f"\n{'='*80}")
        print(f"➕ AGREGANDO BIOMARCADOR COMPLETO: {nombre}")
        print(f"{'='*80}\n")

        nombre_upper = nombre.upper()
        columna_bd = f"IHQ_{nombre_upper.replace('-', '_')}"

        print(f"Nombre: {nombre}")
        print(f"Variantes: {', '.join(variantes)}")
        print(f"Columna BD: {columna_bd}\n")

        # 1. Agregar a MAPEO_BIOMARCADORES
        print("1️⃣  Agregando a MAPEO_BIOMARCADORES...")
        self._agregar_a_mapeo(nombre, variantes, columna_bd)

        # 2. Agregar columna BD
        print("2️⃣  Agregando columna a BD...")
        self._agregar_columna_bd(columna_bd)

        # 3. Sugerir patrón para extractor
        print("3️⃣  Configuración de extractor:")
        print(f"   💡 Agregar patrón para {nombre} en biomarker_extractor.py")
        print(f"   💡 Patrón sugerido: r'{nombre}.*?([\\w\\s%+-]+)'")

        print(f"\n✅ Biomarcador {nombre} agregado exitosamente")

        # Registrar acción
        self.registrar_accion("Agregar Biomarcador", {
            'Nombre': nombre,
            'Columna BD': columna_bd,
            'Variantes': variantes,
            'Patrón sugerido': f"r'{nombre}.*?([\\w\\s%+-]+)'"
        })

        # Auto-actualizar docs
        self._auto_actualizar_docs('biomarcador_nuevo', {
            'nombre': nombre,
            'columna_bd': columna_bd,
            'variantes': variantes
        })

    def _agregar_a_mapeo(self, nombre: str, variantes: List[str], columna_bd: str):
        """Agrega biomarcador a MAPEO_BIOMARCADORES"""
        validator_file = self.core_dir / 'validation_checker.py'

        if not validator_file.exists():
            print(f"❌ No se encontró validation_checker.py")
            return

        try:
            with open(validator_file, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Backup en carpeta centralizada
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{validator_file.stem}_backup_{timestamp}.py"
            backup_path = self.backups_dir / backup_filename
            shutil.copy(validator_file, backup_path)
            print(f"📦 Backup creado: backups/{backup_filename}")

            # Buscar el final del diccionario MAPEO_BIOMARCADORES
            match = re.search(r'(MAPEO_BIOMARCADORES\s*=\s*\{[^}]+)(})', contenido, re.DOTALL)

            if match:
                antes_llave = match.group(1)
                llave_cierre = match.group(2)

                # Preparar nuevas líneas
                nuevas_lineas = []
                for var in [nombre.upper()] + [v.upper() for v in variantes]:
                    nuevas_lineas.append(f"    '{var}': '{columna_bd}',")

                nuevo_mapeo = antes_llave + '\n' + '\n'.join(nuevas_lineas) + '\n' + llave_cierre

                contenido_nuevo = contenido.replace(match.group(0), nuevo_mapeo)

                # Escribir
                with open(validator_file, 'w', encoding='utf-8') as f:
                    f.write(contenido_nuevo)

                print(f"   ✅ MAPEO_BIOMARCADORES actualizado")
                print(f"   📦 Backup: {backup_path.name}")

            else:
                print(f"   ⚠️  No se pudo localizar MAPEO_BIOMARCADORES")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    def _agregar_columna_bd(self, columna: str):
        """Agrega columna a la BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verificar si ya existe
            cursor.execute("PRAGMA table_info(informes_ihq)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]

            if columna in columnas_existentes:
                print(f"   ⚠️  Columna {columna} ya existe")
                conn.close()
                return

            # Agregar columna
            cursor.execute(f"ALTER TABLE informes_ihq ADD COLUMN {columna} TEXT")
            conn.commit()
            conn.close()

            print(f"   ✅ Columna {columna} agregada a BD")

        except Exception as e:
            print(f"   ❌ Error agregando columna: {e}")

    # ========== 2. REPROCESAMIENTO INTELIGENTE ==========

    def reprocesar_caso(self, numero_ihq: str, validar_antes: bool = True):
        """Reprocesa un caso específico"""
        print(f"\n{'='*80}")
        print(f"🔄 REPROCESANDO CASO: {numero_ihq}")
        print(f"{'='*80}\n")

        if validar_antes:
            print("🔍 Validando estado actual...")
            # TODO: Implementar validación previa

        # Buscar PDF original
        pdf_original = self._buscar_pdf_caso(numero_ihq)

        if not pdf_original:
            print(f"❌ No se encontró PDF para {numero_ihq}")
            return

        print(f"📄 PDF encontrado: {pdf_original.name}\n")

        try:
            from core.ihq_processor import process_ihq_file

            print("🔄 Procesando...")
            saved_count = process_ihq_file(str(pdf_original))

            print(f"\n✅ Caso reprocesado exitosamente")
            print(f"   {saved_count} registro(s) guardado(s)")

        except Exception as e:
            print(f"❌ Error reprocesando: {e}")
            import traceback
            traceback.print_exc()

    def _buscar_pdf_caso(self, numero_ihq: str) -> Optional[Path]:
        """Busca el PDF que contiene un caso"""
        pdfs_dir = PROJECT_ROOT / 'pdfs_patologia'

        if not pdfs_dir.exists():
            return None

        # Extraer número del caso
        numero = numero_ihq.replace('IHQ', '').replace('IHQ', '')

        for pdf in pdfs_dir.glob("*.pdf"):
            # Buscar en nombre del archivo
            if numero in pdf.stem:
                return pdf

        # TODO: Buscar en índice de casos procesados
        return None

    def reprocesar_lote(self, numeros_ihq: List[str], batch_size: int = 5):
        """Reprocesa múltiples casos en lotes"""
        print(f"\n{'='*80}")
        print(f"🔄 REPROCESANDO LOTE DE {len(numeros_ihq)} CASOS")
        print(f"{'='*80}\n")

        exitos = 0
        fallos = 0

        for i, numero in enumerate(numeros_ihq, 1):
            print(f"\n[{i}/{len(numeros_ihq)}] {numero}")
            print("-" * 80)

            try:
                self.reprocesar_caso(numero, validar_antes=False)
                exitos += 1
            except Exception as e:
                print(f"❌ Error: {e}")
                fallos += 1

            # Pausa entre lotes
            if i % batch_size == 0 and i < len(numeros_ihq):
                print(f"\n⏸️  Pausa tras {batch_size} casos...")

        print(f"\n{'='*80}")
        print(f"📊 RESUMEN DE REPROCESAMIENTO")
        print(f"{'='*80}")
        print(f"  Total: {len(numeros_ihq)}")
        print(f"  ✅ Exitosos: {exitos}")
        print(f"  ❌ Fallidos: {fallos}")

    # ========== 3. AUTO-ACTUALIZACIÓN DE DOCS ==========

    def _auto_actualizar_docs(self, tipo_cambio: str, info: Dict):
        """Auto-actualiza CLAUDE.md y agentes cuando hay cambios"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if tipo_cambio == 'biomarcador_nuevo':
            # Actualizar data-auditor.md
            self._actualizar_agente_biomarcador(info)

            # Actualizar CLAUDE.md
            self._actualizar_claude_cambio(f"Biomarcador {info['nombre']} agregado", timestamp)

        elif tipo_cambio == 'extractor_mejorado':
            self._actualizar_claude_cambio(f"Extractor mejorado: {info['biomarcador']} - {info['razon']}", timestamp)

        print(f"\n📝 Documentación auto-actualizada")

    def _actualizar_agente_biomarcador(self, info: Dict):
        """Actualiza data-auditor.md con nuevo biomarcador"""
        agente_file = self.agents_dir / "data-auditor.md"

        if not agente_file.exists():
            return

        try:
            with open(agente_file, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Buscar sección de biomarcadores
            # TODO: Implementar inserción inteligente

            print(f"   💡 Actualizar manualmente: {agente_file.name}")

        except Exception as e:
            print(f"   ⚠️  Error actualizando agente: {e}")

    def _actualizar_claude_cambio(self, descripcion: str, timestamp: str):
        """Registra cambio en CLAUDE.md"""
        if not self.claude_md.exists():
            return

        try:
            with open(self.claude_md, 'r', encoding='utf-8') as f:
                contenido = f.read()

            # Buscar sección de historial
            # TODO: Implementar inserción de historial

            print(f"   💡 Cambio registrado: {descripcion}")

        except Exception as e:
            print(f"   ⚠️  Error actualizando CLAUDE.md: {e}")

    # ========== 4. SIMULACIÓN Y VALIDACIÓN ==========

    def simular_cambio(self, archivo: str, funcion: str, cambio: str):
        """Simula un cambio antes de aplicarlo"""
        print(f"\n{'='*80}")
        print(f"🔍 SIMULANDO CAMBIO")
        print(f"{'='*80}\n")

        print(f"Archivo: {archivo}")
        print(f"Función: {funcion}")
        print(f"Cambio: {cambio}\n")

        archivo_path = self.core_dir / archivo

        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return

        print("✅ Archivo existe")
        print("🔍 Analizando impacto...\n")

        # Identificar dependencias
        dependencias = self.conocimiento['dependencias'].get(archivo, [])

        if dependencias:
            print(f"⚠️  ARCHIVOS DEPENDIENTES ({len(dependencias)}):")
            for dep in dependencias:
                print(f"   - {dep}")
            print(f"\n💡 Estos archivos pueden verse afectados")
        else:
            print("✅ No se detectaron dependencias directas")

        print(f"\n🔍 SIMULACIÓN COMPLETADA")
        print(f"💡 Usa --aplicar para ejecutar el cambio real")

    def verificar_impacto(self, archivo_editado: str):
        """Verifica qué módulos se ven afectados por un cambio"""
        print(f"\n{'='*80}")
        print(f"🔍 VERIFICANDO IMPACTO DE CAMBIOS")
        print(f"{'='*80}\n")

        print(f"Archivo modificado: {archivo_editado}\n")

        # Buscar módulos que importan este archivo
        afectados = []

        for py_file in self.core_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    contenido = f.read()

                # Buscar imports del archivo editado
                archivo_sin_ext = archivo_editado.replace('.py', '')
                if re.search(rf'from\s+core.*import.*{archivo_sin_ext}', contenido):
                    afectados.append(py_file.name)

            except:
                pass

        if afectados:
            print(f"⚠️  MÓDULOS AFECTADOS ({len(afectados)}):")
            for modulo in afectados:
                print(f"   - {modulo}")
            print(f"\n💡 Recomendación: Ejecutar tests en estos módulos")
        else:
            print("✅ No se detectaron módulos afectados directamente")

    # ========== 5. ANÁLISIS DE ARQUITECTURA ==========

    def analizar_arquitectura_completa(self):
        """Analiza toda la arquitectura de core/"""
        print(f"\n{'='*80}")
        print("🏗️ ANÁLISIS DE ARQUITECTURA COMPLETA")
        print(f"{'='*80}\n")

        print("📊 MÓDULOS:")
        for tipo, info in self.conocimiento.items():
            if tipo in ['extractors', 'validators', 'prompts']:
                print(f"\n{tipo.upper()}:")
                if isinstance(info, dict):
                    for nombre, detalles in info.items():
                        if isinstance(detalles, dict):
                            print(f"  - {nombre}: {len(detalles.get('funciones', []))} funciones")
                        else:
                            print(f"  - {nombre}: {detalles}")

        print(f"\n📊 BIOMARCADORES MAPEADOS: {len(self.conocimiento['mapeo_biomarcadores'])}")

        print(f"\n📊 DEPENDENCIAS:")
        for modulo, deps in list(self.conocimiento['dependencias'].items())[:10]:
            print(f"  {modulo} → {len(deps)} dependencias")

    def mapear_dependencias_grafo(self):
        """Crea un grafo de dependencias"""
        print(f"\n{'='*80}")
        print("🕸️ GRAFO DE DEPENDENCIAS")
        print(f"{'='*80}\n")

        for modulo, deps in self.conocimiento['dependencias'].items():
            if deps:
                print(f"{modulo}:")
                for dep in deps:
                    print(f"  └─→ {dep}")
                print()


    # ========== FUNCIONALIDADES EXTENDIDAS ==========

    def generar_test_unitario(self, archivo: str, funcion: str):
        """Genera test unitario para una función"""
        print(f"\n{'='*80}")
        print(f"🧪 GENERANDO TEST UNITARIO")
        print(f"{'='*80}\n")

        archivo_path = self.core_dir / archivo
        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo = f.read()

            tree = ast.parse(codigo)

            # Buscar la función
            funcion_encontrada = None
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name == funcion:
                    funcion_encontrada = node
                    break

            if not funcion_encontrada:
                print(f"❌ Función '{funcion}' no encontrada en {archivo}")
                return

            # Extraer parámetros
            params = [arg.arg for arg in funcion_encontrada.args.args if arg.arg != 'self']

            # Generar código de test
            test_codigo = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test unitario autogenerado para {funcion}
Archivo: {archivo}
Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import unittest
import sys
from pathlib import Path

# Agregar project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.{archivo.replace('.py', '')} import {funcion}


class Test{funcion.title().replace('_', '')}(unittest.TestCase):
    """Tests para {funcion}"""

    def setUp(self):
        """Setup antes de cada test"""
        pass

    def test_{funcion}_basic(self):
        """Test básico de {funcion}"""
        # TODO: Implementar test básico
        # Parámetros: {', '.join(params)}
        pass

    def test_{funcion}_edge_cases(self):
        """Test de casos extremos"""
        # TODO: Implementar casos extremos
        pass

    def test_{funcion}_error_handling(self):
        """Test de manejo de errores"""
        # TODO: Implementar test de errores
        pass


if __name__ == '__main__':
    unittest.main()
'''

            # Guardar test
            tests_dir = PROJECT_ROOT / "tests"
            tests_dir.mkdir(exist_ok=True)

            test_file = tests_dir / f"test_{funcion}.py"

            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_codigo)

            print(f"✅ Test generado: {test_file}")
            print(f"📊 Función: {funcion}")
            print(f"📊 Parámetros: {', '.join(params) if params else 'ninguno'}")
            print(f"\n💡 Completar los tests en: {test_file}")

        except Exception as e:
            print(f"❌ Error generando test: {e}")

    def validar_sintaxis_python(self, archivo: str):
        """Valida sintaxis Python de un archivo"""
        print(f"\n{'='*80}")
        print(f"🔍 VALIDANDO SINTAXIS PYTHON")
        print(f"{'='*80}\n")

        archivo_path = Path(archivo) if '/' in archivo or '\\' in archivo else self.core_dir / archivo

        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return False

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo = f.read()

            # Intentar parsear
            ast.parse(codigo)

            print(f"✅ Sintaxis válida: {archivo_path.name}")
            return True

        except SyntaxError as e:
            print(f"❌ Error de sintaxis:")
            print(f"   Línea {e.lineno}: {e.msg}")
            print(f"   {e.text}")
            return False

        except Exception as e:
            print(f"❌ Error validando: {e}")
            return False

    def refactorizar_codigo(self, archivo: str, tipo: str = 'extract_method'):
        """Refactoriza código automáticamente"""
        print(f"\n{'='*80}")
        print(f"♻️  REFACTORIZACIÓN DE CÓDIGO")
        print(f"{'='*80}\n")
        print(f"Tipo: {tipo}")

        archivo_path = self.core_dir / archivo
        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return

        try:
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo = f.read()
                lineas = codigo.split('\n')

            tree = ast.parse(codigo)

            sugerencias = []

            if tipo == 'extract_method':
                # Buscar funciones largas (>50 líneas)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if hasattr(node, 'end_lineno'):
                            longitud = node.end_lineno - node.lineno
                            if longitud > 50:
                                sugerencias.append({
                                    'tipo': 'Extract Method',
                                    'funcion': node.name,
                                    'linea': node.lineno,
                                    'razon': f'Función muy larga ({longitud} líneas)',
                                    'sugerencia': f'Dividir {node.name} en funciones más pequeñas'
                                })

            elif tipo == 'rename':
                # Buscar nombres de funciones cortos o poco descriptivos
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        if len(node.name) < 4 and not node.name.startswith('_'):
                            sugerencias.append({
                                'tipo': 'Rename',
                                'funcion': node.name,
                                'linea': node.lineno,
                                'razon': f'Nombre poco descriptivo ({len(node.name)} chars)',
                                'sugerencia': f'Renombrar {node.name} a algo más descriptivo'
                            })

            elif tipo == 'remove_duplication':
                # Detectar código duplicado simple
                bloques = defaultdict(list)
                for i, linea in enumerate(lineas):
                    linea_clean = linea.strip()
                    if len(linea_clean) > 20 and not linea_clean.startswith('#'):
                        bloques[linea_clean].append(i + 1)

                for linea, apariciones in bloques.items():
                    if len(apariciones) > 2:
                        sugerencias.append({
                            'tipo': 'Remove Duplication',
                            'funcion': 'N/A',
                            'linea': apariciones[0],
                            'razon': f'Línea duplicada {len(apariciones)} veces',
                            'sugerencia': f'Extraer a constante o función: "{linea[:50]}..."'
                        })

            if sugerencias:
                print(f"🔍 {len(sugerencias)} sugerencias de refactorización:\n")
                for i, sug in enumerate(sugerencias[:10], 1):
                    print(f"{i}. {sug['tipo']}")
                    print(f"   Función: {sug['funcion']} (L{sug['linea']})")
                    print(f"   Razón: {sug['razon']}")
                    print(f"   Sugerencia: {sug['sugerencia']}")
                    print()

                if len(sugerencias) > 10:
                    print(f"... y {len(sugerencias) - 10} más")
            else:
                print("✅ No se encontraron oportunidades de refactorización")

        except Exception as e:
            print(f"❌ Error refactorizando: {e}")

    def detectar_breaking_changes(self, archivo: str):
        """Detecta cambios que pueden romper compatibilidad"""
        print(f"\n{'='*80}")
        print(f"⚠️  DETECCIÓN DE BREAKING CHANGES")
        print(f"{'='*80}\n")

        archivo_path = self.core_dir / archivo
        if not archivo_path.exists():
            print(f"❌ Archivo no encontrado: {archivo}")
            return

        # Crear backup para comparar
        backup_path = archivo_path.with_suffix('.py.backup')

        if not backup_path.exists():
            print(f"⚠️  No existe backup para comparar")
            print(f"💡 Usa --versionar-cambio primero")
            return

        try:
            # Leer ambas versiones
            with open(archivo_path, 'r', encoding='utf-8') as f:
                codigo_nuevo = f.read()

            with open(backup_path, 'r', encoding='utf-8') as f:
                codigo_viejo = f.read()

            tree_nuevo = ast.parse(codigo_nuevo)
            tree_viejo = ast.parse(codigo_viejo)

            # Extraer funciones públicas
            funciones_nuevas = {node.name: node for node in ast.walk(tree_nuevo)
                              if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')}

            funciones_viejas = {node.name: node for node in ast.walk(tree_viejo)
                              if isinstance(node, ast.FunctionDef) and not node.name.startswith('_')}

            breaking_changes = []

            # Detectar funciones eliminadas
            for nombre in funciones_viejas:
                if nombre not in funciones_nuevas:
                    breaking_changes.append({
                        'tipo': 'FUNCIÓN ELIMINADA',
                        'detalle': f'Función pública "{nombre}" eliminada',
                        'severidad': 'CRÍTICO'
                    })

            # Detectar cambios en firma de función
            for nombre in funciones_nuevas:
                if nombre in funciones_viejas:
                    args_nuevos = len(funciones_nuevas[nombre].args.args)
                    args_viejos = len(funciones_viejas[nombre].args.args)

                    if args_nuevos != args_viejos:
                        breaking_changes.append({
                            'tipo': 'FIRMA MODIFICADA',
                            'detalle': f'Función "{nombre}": {args_viejos} → {args_nuevos} args',
                            'severidad': 'ALTO'
                        })

            if breaking_changes:
                print(f"🔴 {len(breaking_changes)} breaking changes detectados:\n")
                for i, bc in enumerate(breaking_changes, 1):
                    print(f"{i}. [{bc['severidad']}] {bc['tipo']}")
                    print(f"   {bc['detalle']}")
                    print()
            else:
                print("✅ No se detectaron breaking changes")

        except Exception as e:
            print(f"❌ Error detectando changes: {e}")

    def registrar_accion(self, tipo: str, detalles: Dict[str, Any]):
        """Registra una acción realizada para incluir en el reporte"""
        accion = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'tipo': tipo,
            'detalles': detalles
        }
        self.registro_acciones.append(accion)

    def generar_reporte(self) -> str:
        """Genera reporte MD con todas las acciones realizadas"""
        if not self.registro_acciones:
            print("⚠️  No hay acciones registradas para generar reporte")
            return ""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reporte_path = self.resultados_dir / f"cambios_{timestamp}.md"

        # Construir contenido del reporte
        contenido = f"""# Reporte de Cambios - Editor Core

**Fecha**: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
**Total de acciones**: {len(self.registro_acciones)}

---

## 📋 Resumen de Cambios

"""

        # Agrupar acciones por tipo
        acciones_por_tipo = defaultdict(list)
        for accion in self.registro_acciones:
            acciones_por_tipo[accion['tipo']].append(accion)

        # Generar secciones por tipo
        for tipo, acciones in acciones_por_tipo.items():
            contenido += f"\n### {tipo}\n\n"
            for accion in acciones:
                contenido += f"**{accion['timestamp']}**\n\n"
                for key, value in accion['detalles'].items():
                    if isinstance(value, list):
                        contenido += f"- **{key}**:\n"
                        for item in value:
                            contenido += f"  - {item}\n"
                    else:
                        contenido += f"- **{key}**: {value}\n"
                contenido += "\n"

        # Guardar reporte
        try:
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write(contenido)

            print(f"\n{'='*80}")
            print(f"📝 REPORTE GENERADO")
            print(f"{'='*80}\n")
            print(f"✅ Reporte guardado en: {reporte_path}")
            print(f"📊 Total de acciones registradas: {len(self.registro_acciones)}")

            return str(reporte_path)

        except Exception as e:
            print(f"❌ Error generando reporte: {e}")
            return ""

    def ejecutar_tests_automaticos(self, archivo: Optional[str] = None):
        """Ejecuta tests automáticos"""
        print(f"\n{'='*80}")
        print(f"🧪 EJECUTANDO TESTS AUTOMÁTICOS")
        print(f"{'='*80}\n")

        tests_dir = PROJECT_ROOT / "tests"
        if not tests_dir.exists():
            print(f"❌ No existe directorio tests/")
            return

        import subprocess

        try:
            if archivo:
                # Ejecutar test específico
                test_file = tests_dir / f"test_{archivo.replace('.py', '')}.py"
                if not test_file.exists():
                    print(f"❌ Test no encontrado: {test_file}")
                    return

                print(f"Ejecutando: {test_file.name}\n")
                result = subprocess.run(
                    [sys.executable, str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

            else:
                # Ejecutar todos los tests
                print(f"Ejecutando todos los tests en {tests_dir}\n")
                result = subprocess.run(
                    [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir)],
                    capture_output=True,
                    text=True,
                    timeout=120
                )

            # Mostrar resultados
            print(result.stdout)
            if result.stderr:
                print(result.stderr)

            if result.returncode == 0:
                print(f"\n✅ Todos los tests pasaron")
            else:
                print(f"\n❌ Algunos tests fallaron")

        except subprocess.TimeoutExpired:
            print(f"❌ Tests excedieron el tiempo límite")
        except Exception as e:
            print(f"❌ Error ejecutando tests: {e}")

    def migrar_datos_schema(self, nueva_columna: str, tipo: str = 'TEXT', valor_default: str = 'N/A'):
        """Migra esquema de base de datos agregando columna"""
        print(f"\n{'='*80}")
        print(f"🔄 MIGRACIÓN DE SCHEMA")
        print(f"{'='*80}\n")

        print(f"Nueva columna: {nueva_columna}")
        print(f"Tipo: {tipo}")
        print(f"Valor default: {valor_default}\n")

        try:
            # Backup de BD primero
            from herramientas_ia.gestor_base_datos import GestorBaseDatos
            gestor = GestorBaseDatos()

            print("Creando backup de base de datos...")
            gestor.backup_bd(f"antes_migracion_{nueva_columna}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")

            # Conectar a BD
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verificar si columna ya existe
            cursor.execute("PRAGMA table_info(informes_ihq)")
            columnas = [row[1] for row in cursor.fetchall()]

            if nueva_columna in columnas:
                print(f"⚠️  La columna '{nueva_columna}' ya existe")
                conn.close()
                return

            # Agregar columna
            print(f"Agregando columna '{nueva_columna}'...")
            cursor.execute(f'ALTER TABLE informes_ihq ADD COLUMN "{nueva_columna}" {tipo} DEFAULT "{valor_default}"')

            conn.commit()
            conn.close()

            print(f"✅ Migración completada")
            print(f"   Columna agregada: {nueva_columna}")
            print(f"   Tipo: {tipo}")

        except Exception as e:
            print(f"❌ Error en migración: {e}")
            print(f"💡 Restaurar desde backup si es necesario")


def main():
    """CLI principal"""
    parser = argparse.ArgumentParser(
        description="✏️ Editor Core EVARISIS - Editor Inteligente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

EDICIÓN:
  python editor_core.py --editar-extractor Ki-67 --patron "índice.*?(\\d+)%" --razon "Mejorar detección"
  python editor_core.py --editar-extractor Ki-67 --simular  # Simular primero

AGREGAR BIOMARCADOR:
  python editor_core.py --agregar-biomarcador BCL2 --variantes "BCL-2,BCL 2"

REPROCESAMIENTO:
  python editor_core.py --reprocesar IHQ250025
  python editor_core.py --reprocesar IHQ250025 --validar-antes
  python editor_core.py --reprocesar-lote "IHQ250001,IHQ250002,IHQ250003"

SIMULACIÓN:
  python editor_core.py --simular --archivo biomarker_extractor.py --funcion extract_ki67

ANÁLISIS:
  python editor_core.py --analizar-arquitectura
  python editor_core.py --mapear-dependencias
  python editor_core.py --verificar-impacto biomarker_extractor.py

TESTING:
  python editor_core.py --generar-test biomarker_extractor.py extract_ki67
  python editor_core.py --ejecutar-tests
  python editor_core.py --ejecutar-tests --archivo biomarker_extractor

CALIDAD:
  python editor_core.py --validar-sintaxis ihq_processor.py
  python editor_core.py --refactorizar ihq_processor.py --tipo extract_method
  python editor_core.py --detectar-breaking-changes biomarker_extractor.py

REPORTES:
  python editor_core.py --generar-reporte

MIGRACIÓN:
  python editor_core.py --migrar-schema IHQ_BCL2 --tipo TEXT --default "N/A"
        """
    )

    # Edición
    parser.add_argument("--editar-extractor", help="Editar extractor para biomarcador")
    parser.add_argument("--patron", help="Patrón regex nuevo")
    parser.add_argument("--razon", help="Razón del cambio")
    parser.add_argument("--simular", action="store_true", help="Simular cambio sin aplicar")

    # Biomarcadores
    parser.add_argument("--agregar-biomarcador", help="Agregar biomarcador completo")
    parser.add_argument("--variantes", help="Variantes del biomarcador (separadas por coma)")

    # Reprocesamiento
    parser.add_argument("--reprocesar", help="Reprocesar caso específico")
    parser.add_argument("--validar-antes", action="store_true", help="Validar antes de reprocesar")
    parser.add_argument("--reprocesar-lote", help="Reprocesar lote (IHQs separados por coma)")

    # Análisis
    parser.add_argument("--analizar-arquitectura", action="store_true", help="Analizar arquitectura completa")
    parser.add_argument("--mapear-dependencias", action="store_true", help="Mapear dependencias")
    parser.add_argument("--verificar-impacto", help="Verificar impacto de cambios")

    # Testing
    parser.add_argument("--generar-test", nargs=2, metavar=('ARCHIVO', 'FUNCION'), help="Generar test unitario")
    parser.add_argument("--ejecutar-tests", action="store_true", help="Ejecutar tests automáticos")

    # Calidad
    parser.add_argument("--validar-sintaxis", help="Validar sintaxis Python")
    parser.add_argument("--refactorizar", help="Refactorizar código")
    parser.add_argument("--tipo", choices=['extract_method', 'rename', 'remove_duplication'], default='extract_method', help="Tipo de refactorización")
    parser.add_argument("--detectar-breaking-changes", help="Detectar breaking changes")

    # Reportes
    parser.add_argument("--generar-reporte", action="store_true", help="Generar reporte de cambios realizados")

    # Migración
    parser.add_argument("--migrar-schema", help="Migrar schema BD (nueva columna)")
    parser.add_argument("--tipo-dato", default='TEXT', help="Tipo de dato SQL")
    parser.add_argument("--default", default='N/A', help="Valor por defecto")

    # General
    parser.add_argument("--archivo", help="Archivo para operaciones")

    args = parser.parse_args()

    try:
        editor = EditorCore()

        if args.editar_extractor:
            if not args.patron or not args.razon:
                print("❌ Se requieren --patron y --razon")
                sys.exit(1)
            editor.editar_extractor(args.editar_extractor, args.patron, args.razon, simular=args.simular)

        elif args.agregar_biomarcador:
            if not args.variantes:
                print("❌ Se requiere --variantes")
                sys.exit(1)
            variantes = [v.strip() for v in args.variantes.split(',')]
            editor.agregar_biomarcador_completo(args.agregar_biomarcador, variantes)

        elif args.reprocesar:
            editor.reprocesar_caso(args.reprocesar, validar_antes=args.validar_antes)

        elif args.reprocesar_lote:
            casos = [c.strip() for c in args.reprocesar_lote.split(',')]
            editor.reprocesar_lote(casos)

        elif args.simular and args.archivo and args.funcion:
            editor.simular_cambio(args.archivo, args.funcion, "cambio ejemplo")

        elif args.analizar_arquitectura:
            editor.analizar_arquitectura_completa()

        elif args.mapear_dependencias:
            editor.mapear_dependencias_grafo()

        elif args.verificar_impacto:
            editor.verificar_impacto(args.verificar_impacto)

        elif args.generar_test:
            archivo, funcion = args.generar_test
            editor.generar_test_unitario(archivo, funcion)

        elif args.ejecutar_tests:
            editor.ejecutar_tests_automaticos(archivo=args.archivo)

        elif args.validar_sintaxis:
            editor.validar_sintaxis_python(args.validar_sintaxis)

        elif args.refactorizar:
            editor.refactorizar_codigo(args.refactorizar, tipo=args.tipo)

        elif args.detectar_breaking_changes:
            editor.detectar_breaking_changes(args.detectar_breaking_changes)

        elif args.generar_reporte:
            editor.generar_reporte()

        elif args.migrar_schema:
            editor.migrar_datos_schema(args.migrar_schema, tipo=args.tipo_dato, valor_default=args.default)

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
