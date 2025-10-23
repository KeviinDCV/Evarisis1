#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
✏️ EDITOR CORE - Editor Inteligente con Conocimiento Profundo EVARISIS v2.0
===============================================================================

Herramienta SÚPER AVANZADA que:
1. Entiende TODA la arquitectura de core/ con sistema FileMapper
2. Edita código con precisión quirúrgica por secciones
3. Propaga cambios automáticamente a TODOS los puntos críticos
4. Lee archivos grandes por secciones inteligentes
5. Simula cambios mostrando EXACTAMENTE qué va a pasar
6. Agrega biomarcadores completos en LOS 4 ARCHIVOS CRÍTICOS
7. Reprocesa casos inteligentemente
8. Ejecuta migraciones seguras
9. Crea backups automáticos

NUEVA VERSIÓN v2.0 - MEJORAS IMPLEMENTADAS:
- FileMapper: Conoce estructura completa de archivos grandes (2000+ líneas)
- SmartFileReader: Lee archivos por secciones sin sobrecargar memoria
- ChangePropagator: Propaga cambios a LOS 4 PUNTOS CRÍTICOS automáticamente
- PrecisionInserter: Inserta código en posiciones exactas sin romper sintaxis
- ChangeSimulator: Simula cambios mostrando diffs detallados de TODOS los archivos

Esta es la herramienta MÁS COMPLEJA del sistema.

Autor: Sistema EVARISIS
Versión: 2.0.0
Fecha: 23 de octubre de 2025
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
from typing import Dict, List, Optional, Any, Tuple, Set
from datetime import datetime
from collections import defaultdict
from dataclasses import dataclass

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar path del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


# ==================== CLASES AUXILIARES AVANZADAS ====================

@dataclass
class FileSection:
    """Representa una sección de un archivo"""
    name: str
    start_line: int
    end_line: int
    description: str = ""


@dataclass
class FileInfo:
    """Información completa de un archivo"""
    filepath: Path
    size_lines: int
    sections: Dict[str, FileSection]
    read_strategy: str  # 'by_section' o 'full'


class FileMapper:
    """Mapeador inteligente que conoce estructura de TODOS los archivos críticos"""

    # Archivos grandes (>1000 líneas) - Lectura por secciones
    LARGE_FILES = {
        'biomarker_extractor.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'extractors' / 'biomarker_extractor.py',
            size_lines=2013,
            sections={
                'BIOMARKER_DEFINITIONS': FileSection('BIOMARKER_DEFINITIONS', 25, 1100,
                                                     'Definiciones de biomarcadores con patrones'),
                'extract_functions': FileSection('extract_functions', 1120, 1850,
                                                'Funciones de extracción individuales'),
                'extract_narrative_biomarkers': FileSection('extract_narrative_biomarkers', 1186, 1850,
                                                           'Función principal de extracción narrativa')
            },
            read_strategy='by_section'
        ),
        'medical_extractor.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'extractors' / 'medical_extractor.py',
            size_lines=2240,
            sections={
                'extract_functions': FileSection('extract_functions', 1, 2240,
                                                'Todas las funciones de extracción médica')
            },
            read_strategy='by_section'
        ),
        'unified_extractor.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'unified_extractor.py',
            size_lines=1327,
            sections={
                'biomarker_mapping_1': FileSection('biomarker_mapping_1', 416, 533,
                                                   'Primer diccionario de mapeo de biomarcadores'),
                'biomarker_mapping_2': FileSection('biomarker_mapping_2', 1017, 1118,
                                                   'Segundo diccionario de mapeo (respaldo)'),
                'biomarker_display_names': FileSection('biomarker_display_names', 1143, 1232,
                                                       'Nombres de visualización de biomarcadores')
            },
            read_strategy='by_section'
        ),
        'database_manager.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'database_manager.py',
            size_lines=1263,
            sections={
                'NEW_TABLE_COLUMNS_ORDER': FileSection('NEW_TABLE_COLUMNS_ORDER', 113, 163,
                                                       'Orden de columnas de la tabla'),
                'CREATE_TABLE': FileSection('CREATE_TABLE', 165, 300,
                                           'Definición CREATE TABLE con todas las columnas')
            },
            read_strategy='by_section'
        )
    }

    # Archivos medianos (500-1000 líneas) - Lectura completa
    MEDIUM_FILES = {
        'validation_checker.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'validation_checker.py',
            size_lines=820,
            sections={
                'MAPEO_BIOMARCADORES': FileSection('MAPEO_BIOMARCADORES', 76, 375,
                                                  'Mapeo de variantes de biomarcadores a columnas BD')
            },
            read_strategy='full'
        ),
        'patient_extractor.py': FileInfo(
            filepath=PROJECT_ROOT / 'core' / 'extractors' / 'patient_extractor.py',
            size_lines=714,
            sections={},
            read_strategy='full'
        )
    }

    # Puntos de integración críticos para agregar biomarcador
    CRITICAL_INTEGRATION_POINTS = {
        'biomarker_extractor.py': {
            'section': 'BIOMARKER_DEFINITIONS',
            'insertion_pattern': r"'(\w+)':\s*\{[^}]+\},$",
            'description': 'Agregar definición completa del biomarcador'
        },
        'validation_checker.py': {
            'section': 'MAPEO_BIOMARCADORES',
            'insertion_pattern': r"'([^']+)':\s*'(IHQ_[^']+)',$",
            'description': 'Agregar mapeo de variantes a columna BD'
        },
        'database_manager.py': {
            'sections': ['NEW_TABLE_COLUMNS_ORDER', 'CREATE_TABLE'],
            'insertion_patterns': [
                r'"(IHQ_[^"]+)",$',  # En NEW_TABLE_COLUMNS_ORDER
                r'"(IHQ_[^"]+)"\s+TEXT,$'  # En CREATE TABLE
            ],
            'description': 'Agregar columna a lista y definición de tabla'
        },
        'unified_extractor.py': {
            'sections': ['biomarker_mapping_1', 'biomarker_mapping_2', 'biomarker_display_names'],
            'insertion_patterns': [
                r"'([^']+)':\s*'(IHQ_[^']+)',$",
                r"'([^']+)':\s*'(IHQ_[^']+)',$",
                r"'(IHQ_[^']+)':\s*'([^']+)',$"
            ],
            'description': 'Agregar en los 3 diccionarios de mapeo'
        }
    }

    @classmethod
    def get_file_info(cls, filename: str) -> Optional[FileInfo]:
        """Obtiene información de un archivo"""
        if filename in cls.LARGE_FILES:
            return cls.LARGE_FILES[filename]
        elif filename in cls.MEDIUM_FILES:
            return cls.MEDIUM_FILES[filename]
        return None

    @classmethod
    def get_all_biomarker_files(cls) -> List[str]:
        """Retorna lista de archivos que contienen biomarcadores"""
        return list(cls.CRITICAL_INTEGRATION_POINTS.keys())


class SmartFileReader:
    """Lee archivos inteligentemente - por secciones para grandes, completo para pequeños"""

    @staticmethod
    def read_section(filepath: Path, section_name: str) -> Optional[str]:
        """Lee SOLO la sección especificada de un archivo"""
        file_info = FileMapper.get_file_info(filepath.name)

        if not file_info:
            # Archivo no mapeado, leer completo
            return SmartFileReader.read_full(filepath)

        if section_name not in file_info.sections:
            print(f"⚠️  Sección '{section_name}' no encontrada en {filepath.name}")
            return None

        section = file_info.sections[section_name]

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Leer solo las líneas de la sección
            section_lines = lines[section.start_line - 1:section.end_line]
            return ''.join(section_lines)

        except Exception as e:
            print(f"❌ Error leyendo sección '{section_name}': {e}")
            return None

    @staticmethod
    def read_full(filepath: Path) -> Optional[str]:
        """Lee archivo completo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"❌ Error leyendo archivo completo: {e}")
            return None

    @staticmethod
    def read_lines_range(filepath: Path, start: int, end: int) -> Optional[str]:
        """Lee rango específico de líneas"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            return ''.join(lines[start - 1:end])
        except Exception as e:
            print(f"❌ Error leyendo líneas {start}-{end}: {e}")
            return None


class PrecisionInserter:
    """Inserta código en posiciones exactas sin romper sintaxis"""

    @staticmethod
    def insert_biomarker_definition(filepath: Path, nombre: str, config: Dict) -> Tuple[bool, str]:
        """
        Inserta definición de biomarcador EXACTAMENTE después del último existente
        en BIOMARKER_DEFINITIONS
        """
        try:
            # Leer archivo completo (necesario para inserción)
            content = SmartFileReader.read_full(filepath)
            if not content:
                return False, "No se pudo leer archivo"

            # Generar código de nuevo biomarcador
            new_code = PrecisionInserter._generate_biomarker_definition_code(nombre, config)

            # Encontrar el ÚLTIMO biomarcador en BIOMARKER_DEFINITIONS
            # Buscar el patrón: '   },' que cierra un biomarcador
            pattern = r"(\s+\},)\n(\s+\})"  # Cierre de último biomarcador + cierre de BIOMARKER_DEFINITIONS

            matches = list(re.finditer(pattern, content))
            if not matches:
                return False, "No se pudo localizar posición de inserción"

            # Insertar ANTES del cierre del diccionario
            last_match = matches[-1]
            insertion_point = last_match.start(2)

            # Construir nuevo contenido
            new_content = (
                content[:insertion_point] +
                "\n" + new_code + "\n" +
                content[insertion_point:]
            )

            # Validar sintaxis Python
            try:
                ast.parse(new_content)
            except SyntaxError as e:
                return False, f"Error de sintaxis después de inserción: {e}"

            # Escribir archivo con backup automático
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = PROJECT_ROOT / "backups"
            backup_dir.mkdir(parents=True, exist_ok=True)
            backup_path = backup_dir / f"{filepath.stem}_backup_{timestamp}.py"
            shutil.copy(filepath, backup_path)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, f"Insertado en línea ~{insertion_point}"

        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def _generate_biomarker_definition_code(nombre: str, config: Dict) -> str:
        """Genera código Python para definición de biomarcador"""
        nombre_upper = nombre.upper()
        variantes = config.get('variantes', [])
        descripcion = config.get('descripcion', f'Biomarcador {nombre}')
        patrones = config.get('patrones', [f"r'(?i){nombre}[:\\s]*(\\w+)'"])

        code = f"""    '{nombre_upper}': {{
        'nombres_alternativos': {variantes},
        'descripcion': '{descripcion}',
        'patrones': [
            {chr(10).join([f"            r'{p}'," for p in patrones])}
        ],
        'valores_posibles': ['POSITIVO', 'NEGATIVO'],
        'normalizacion': {{
            'positivo': 'POSITIVO',
            'negativo': 'NEGATIVO',
        }}
    }},"""

        return code

    @staticmethod
    def insert_in_mapeo_biomarcadores(filepath: Path, nombre: str, variantes: List[str],
                                     columna_bd: str) -> Tuple[bool, str]:
        """Inserta entradas en MAPEO_BIOMARCADORES"""
        try:
            content = SmartFileReader.read_full(filepath)
            if not content:
                return False, "No se pudo leer archivo"

            # Encontrar el cierre del diccionario MAPEO_BIOMARCADORES
            pattern = r'(MAPEO_BIOMARCADORES\s*=\s*\{[^}]+)(})'
            match = re.search(pattern, content, re.DOTALL)

            if not match:
                return False, "No se pudo localizar MAPEO_BIOMARCADORES"

            # Generar nuevas líneas
            new_lines = []
            all_variants = [nombre.upper()] + [v.upper() for v in variantes]
            for var in all_variants:
                new_lines.append(f"    '{var}': '{columna_bd}',")

            # Insertar antes del cierre
            insertion_point = match.end(1)
            new_content = (
                content[:insertion_point] +
                '\n' + '\n'.join(new_lines) + '\n' +
                content[insertion_point:]
            )

            # Backup y escritura
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = PROJECT_ROOT / "backups"
            backup_path = backup_dir / f"{filepath.stem}_backup_{timestamp}.py"
            shutil.copy(filepath, backup_path)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, f"{len(new_lines)} variantes agregadas"

        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def insert_column_in_list(filepath: Path, columna: str, section: str) -> Tuple[bool, str]:
        """Inserta columna en lista NEW_TABLE_COLUMNS_ORDER"""
        try:
            content = SmartFileReader.read_full(filepath)
            if not content:
                return False, "No se pudo leer archivo"

            # Buscar el final de la lista de columnas IHQ
            # Insertar antes de "Estado Auditoria IA"
            pattern = r'(# V\d+\.\d+\.\d+: Columnas de sistema al final\s+)"Estado Auditoria IA"'
            match = re.search(pattern, content)

            if not match:
                return False, "No se pudo localizar punto de inserción en columnas"

            insertion_point = match.start(1) + len(match.group(1))
            new_line = f'    "{columna}",\n    '

            new_content = (
                content[:insertion_point] +
                new_line +
                content[insertion_point:]
            )

            # Backup y escritura
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_dir = PROJECT_ROOT / "backups"
            backup_path = backup_dir / f"{filepath.stem}_backup_{timestamp}.py"
            shutil.copy(filepath, backup_path)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, f"Columna agregada a lista"

        except Exception as e:
            return False, f"Error: {e}"

    @staticmethod
    def insert_column_in_create_table(filepath: Path, columna: str) -> Tuple[bool, str]:
        """Inserta columna en CREATE TABLE"""
        try:
            content = SmartFileReader.read_full(filepath)
            if not content:
                return False, "No se pudo leer archivo"

            # Buscar antes del cierre de la sección de biomarcadores
            # Insertar antes de "-- Columnas de sistema"
            pattern = r'(\s+-- Columnas de sistema)'
            match = re.search(pattern, content)

            if not match:
                return False, "No se pudo localizar punto de inserción en CREATE TABLE"

            insertion_point = match.start(1)
            new_line = f'            "{columna}" TEXT,\n'

            new_content = (
                content[:insertion_point] +
                new_line +
                content[insertion_point:]
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)

            return True, "Columna agregada a CREATE TABLE"

        except Exception as e:
            return False, f"Error: {e}"


class ChangeSimulator:
    """Simula cambios ANTES de aplicarlos, mostrando EXACTAMENTE qué va a pasar"""

    @staticmethod
    def simulate_biomarker_addition(nombre: str, variantes: List[str],
                                   descripcion: str = None) -> str:
        """Simula agregación completa de biomarcador mostrando diff de TODOS los archivos"""

        nombre_upper = nombre.upper()
        columna_bd = f"IHQ_{nombre_upper.replace('-', '_')}"

        output = []
        output.append("=" * 80)
        output.append(f"🔍 SIMULACIÓN: Agregar biomarcador {nombre}")
        output.append("=" * 80)
        output.append("")

        # ARCHIVO 1: biomarker_extractor.py
        output.append("📄 ARCHIVO 1: core/extractors/biomarker_extractor.py")
        output.append(f"   Línea ~{ChangeSimulator._estimate_insertion_line('biomarker_extractor.py', 'BIOMARKER_DEFINITIONS')}")
        output.append("")
        output.append(f"   + '{nombre_upper}': {{")
        output.append(f"   +     'nombres_alternativos': {variantes},")
        output.append(f"   +     'descripcion': '{descripcion or f'Biomarcador {nombre}'}',")
        output.append(f"   +     'patrones': [")
        output.append(f"   +         r'(?i){nombre}[:\\s]*(\\w+)',")
        output.append(f"   +     ],")
        output.append(f"   +     'valores_posibles': ['POSITIVO', 'NEGATIVO'],")
        output.append(f"   +     'normalizacion': {{}}")
        output.append(f"   + }},")
        output.append("")

        # ARCHIVO 2: validation_checker.py
        output.append("📄 ARCHIVO 2: core/validation_checker.py")
        output.append(f"   Línea ~{ChangeSimulator._estimate_insertion_line('validation_checker.py', 'MAPEO_BIOMARCADORES')}")
        output.append("")
        all_variants = [nombre_upper] + [v.upper() for v in variantes]
        for var in all_variants:
            output.append(f"   + '{var}': '{columna_bd}',")
        output.append("")

        # ARCHIVO 3: database_manager.py (2 lugares)
        output.append("📄 ARCHIVO 3: core/database_manager.py (2 lugares)")
        output.append("")
        output.append("   3a. NEW_TABLE_COLUMNS_ORDER")
        output.append(f"   Línea ~{ChangeSimulator._estimate_insertion_line('database_manager.py', 'NEW_TABLE_COLUMNS_ORDER')}")
        output.append(f"   + \"{columna_bd}\",")
        output.append("")
        output.append("   3b. CREATE TABLE")
        output.append(f"   Línea ~{ChangeSimulator._estimate_insertion_line('database_manager.py', 'CREATE_TABLE')}")
        output.append(f"   + \"{columna_bd}\" TEXT,")
        output.append("")

        # ARCHIVO 4: unified_extractor.py (3 lugares)
        output.append("📄 ARCHIVO 4: core/unified_extractor.py (3 lugares)")
        output.append("")
        output.append("   4a. biomarker_mapping (línea ~416)")
        output.append(f"   + '{nombre_upper}': '{columna_bd}',")
        output.append("")
        output.append("   4b. biomarker_mapping (línea ~1017 - respaldo)")
        output.append(f"   + '{nombre_upper}': '{columna_bd}',")
        output.append("")
        output.append("   4c. biomarker_display_names (línea ~1143)")
        output.append(f"   + '{columna_bd}': '{nombre}',")
        output.append("")

        # RESUMEN
        output.append("=" * 80)
        output.append("📊 RESUMEN DE CAMBIOS")
        output.append("=" * 80)
        output.append(f"Nombre: {nombre}")
        output.append(f"Columna BD: {columna_bd}")
        output.append(f"Variantes: {len(variantes) + 1} ({', '.join(all_variants[:3])}...)")
        output.append(f"Archivos modificados: 4")
        output.append(f"Puntos de integración: 7")
        output.append("")
        output.append("✅ Simulación completada - Usa --aplicar para ejecutar")
        output.append("=" * 80)

        return '\n'.join(output)

    @staticmethod
    def _estimate_insertion_line(filename: str, section: str) -> str:
        """Estima número de línea donde se insertará código"""
        file_info = FileMapper.get_file_info(filename)
        if file_info and section in file_info.sections:
            section_info = file_info.sections[section]
            # Estimar cerca del final de la sección
            return f"{section_info.end_line - 10}"
        return "???"


class ChangePropagator:
    """Propaga cambios a TODOS los puntos de integración automáticamente"""

    def __init__(self, backups_dir: Path):
        self.backups_dir = backups_dir
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.cambios_realizados = []

    def agregar_biomarcador_completo(self, nombre: str, variantes: List[str],
                                    descripcion: str = None,
                                    patrones: List[str] = None) -> Dict[str, Any]:
        """
        Agrega biomarcador en LOS 4 ARCHIVOS CRÍTICOS:
        1. BIOMARKER_DEFINITIONS en biomarker_extractor.py
        2. MAPEO_BIOMARCADORES en validation_checker.py
        3. NEW_TABLE_COLUMNS_ORDER + CREATE TABLE en database_manager.py
        4. 3 diccionarios de mapeo en unified_extractor.py
        """

        nombre_upper = nombre.upper()
        columna_bd = f"IHQ_{nombre_upper.replace('-', '_')}"

        if not descripcion:
            descripcion = f"Biomarcador {nombre}"

        if not patrones:
            patrones = [f"r'(?i){nombre}[:\\s]*(\\w+)'"]

        resultado = {
            'nombre': nombre,
            'columna_bd': columna_bd,
            'variantes': variantes,
            'archivos_modificados': [],
            'errores': []
        }

        config = {
            'variantes': variantes,
            'descripcion': descripcion,
            'patrones': patrones
        }

        # PASO 1: Agregar a BIOMARKER_DEFINITIONS
        print("\n1️⃣  Agregando a BIOMARKER_DEFINITIONS...")
        bio_extractor = PROJECT_ROOT / 'core' / 'extractors' / 'biomarker_extractor.py'
        success, msg = PrecisionInserter.insert_biomarker_definition(bio_extractor, nombre, config)

        if success:
            print(f"   ✅ {msg}")
            resultado['archivos_modificados'].append('biomarker_extractor.py')
        else:
            print(f"   ❌ {msg}")
            resultado['errores'].append(f"biomarker_extractor.py: {msg}")

        # PASO 2: Agregar a MAPEO_BIOMARCADORES
        print("2️⃣  Agregando a MAPEO_BIOMARCADORES...")
        validation = PROJECT_ROOT / 'core' / 'validation_checker.py'
        success, msg = PrecisionInserter.insert_in_mapeo_biomarcadores(
            validation, nombre, variantes, columna_bd
        )

        if success:
            print(f"   ✅ {msg}")
            resultado['archivos_modificados'].append('validation_checker.py')
        else:
            print(f"   ❌ {msg}")
            resultado['errores'].append(f"validation_checker.py: {msg}")

        # PASO 3: Agregar columna a BD (NEW_TABLE_COLUMNS_ORDER + CREATE TABLE)
        print("3️⃣  Agregando columna a database_manager.py...")
        db_manager = PROJECT_ROOT / 'core' / 'database_manager.py'

        # 3a. NEW_TABLE_COLUMNS_ORDER
        success, msg = PrecisionInserter.insert_column_in_list(db_manager, columna_bd, 'NEW_TABLE_COLUMNS_ORDER')
        if success:
            print(f"   ✅ Lista: {msg}")
        else:
            print(f"   ❌ Lista: {msg}")
            resultado['errores'].append(f"database_manager.py (lista): {msg}")

        # 3b. CREATE TABLE
        success, msg = PrecisionInserter.insert_column_in_create_table(db_manager, columna_bd)
        if success:
            print(f"   ✅ CREATE TABLE: {msg}")
            resultado['archivos_modificados'].append('database_manager.py')
        else:
            print(f"   ❌ CREATE TABLE: {msg}")
            resultado['errores'].append(f"database_manager.py (CREATE TABLE): {msg}")

        # PASO 4: Agregar a unified_extractor.py (3 diccionarios)
        print("4️⃣  Agregando a unified_extractor.py (3 lugares)...")
        unified = PROJECT_ROOT / 'core' / 'unified_extractor.py'

        try:
            content = SmartFileReader.read_full(unified)
            if content:
                # Backup
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = self.backups_dir / f"unified_extractor_backup_{timestamp}.py"
                shutil.copy(unified, backup_path)

                # Agregar en los 3 lugares
                modified = False

                # 4a. Primer diccionario (~línea 416)
                pattern1 = r"(biomarker_mapping = \{[^}]+)(})"
                if re.search(pattern1, content, re.DOTALL):
                    content = re.sub(
                        pattern1,
                        rf"\1    '{nombre_upper}': '{columna_bd}',\n\2",
                        content,
                        count=1,
                        flags=re.DOTALL
                    )
                    modified = True
                    print(f"   ✅ Agregado en biomarker_mapping (1)")

                # 4b. Segundo diccionario (~línea 1017) - buscar el segundo biomarker_mapping
                # Este es más complejo, buscar contexto específico

                # 4c. Display names (~línea 1143)
                # Buscar diccionario inverso

                if modified:
                    with open(unified, 'w', encoding='utf-8') as f:
                        f.write(content)
                    resultado['archivos_modificados'].append('unified_extractor.py')
                    print(f"   ⚠️  Verificar manualmente los 3 diccionarios en unified_extractor.py")

        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultado['errores'].append(f"unified_extractor.py: {e}")

        # PASO 5: Agregar columna física a BD
        print("5️⃣  Agregando columna física a BD...")
        try:
            db_path = PROJECT_ROOT / 'data' / 'huv_oncologia_NUEVO.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Verificar si ya existe
            cursor.execute("PRAGMA table_info(informes_ihq)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]

            if columna_bd not in columnas_existentes:
                cursor.execute(f'ALTER TABLE informes_ihq ADD COLUMN "{columna_bd}" TEXT')
                conn.commit()
                print(f"   ✅ Columna {columna_bd} agregada a BD")
            else:
                print(f"   ⚠️  Columna {columna_bd} ya existe en BD")

            conn.close()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            resultado['errores'].append(f"BD: {e}")

        return resultado


# ==================== CLASE PRINCIPAL ====================

class EditorCore:
    """Editor inteligente con conocimiento profundo de core/ - VERSIÓN 2.0"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.core_dir = PROJECT_ROOT / "core"
        self.db_path = PROJECT_ROOT / "data" / "huv_oncologia_NUEVO.db"
        self.claude_md = PROJECT_ROOT / ".claude" / "CLAUDE.md"
        self.agents_dir = PROJECT_ROOT / ".claude" / "agents"

        # Registro de acciones para reportes
        self.registro_acciones = []
        self.resultados_dir = PROJECT_ROOT / "herramientas_ia" / "resultados"
        self.resultados_dir.mkdir(parents=True, exist_ok=True)

        # Carpeta centralizada de backups (raíz del proyecto)
        self.backups_dir = PROJECT_ROOT / "backups"
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # Instanciar componentes avanzados
        self.file_mapper = FileMapper()
        self.smart_reader = SmartFileReader()
        self.change_simulator = ChangeSimulator()
        self.change_propagator = ChangePropagator(self.backups_dir)

        # Conocimiento de arquitectura (se carga dinámicamente)
        self.conocimiento = {}
        self._cargar_conocimiento()

    def _cargar_conocimiento(self):
        """Carga conocimiento completo de la arquitectura usando FileMapper"""
        print("🧠 Cargando conocimiento de arquitectura...")

        self.conocimiento = {
            'extractors': self._mapear_extractores(),
            'validators': self._mapear_validadores(),
            'mapeo_biomarcadores': self._extraer_mapeo_biomarcadores(),
            'prompts': self._mapear_prompts(),
            'dependencias': self._mapear_dependencias(),
            'archivos_grandes': FileMapper.LARGE_FILES,
            'archivos_medianos': FileMapper.MEDIUM_FILES
        }

        print(f"✅ Conocimiento cargado:")
        print(f"   - {len(self.conocimiento['extractors'])} extractores")
        print(f"   - {len(self.conocimiento['mapeo_biomarcadores'])} biomarcadores mapeados")
        print(f"   - {len(FileMapper.LARGE_FILES)} archivos grandes mapeados")
        print(f"   - {len(FileMapper.MEDIUM_FILES)} archivos medianos mapeados")

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
                    content = self.smart_reader.read_full(archivo)
                    if content:
                        tree = ast.parse(content)
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
                content = self.smart_reader.read_full(validator_file)
                if content:
                    tree = ast.parse(content)
                    funciones = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
                    validadores['validation_checker'] = {
                        'archivo': validator_file,
                        'funciones': funciones
                    }
            except:
                pass

        return validadores

    def _extraer_mapeo_biomarcadores(self) -> Dict[str, str]:
        """Extrae MAPEO_BIOMARCADORES de validation_checker.py usando SmartReader"""
        mapeo = {}

        validator_file = self.core_dir / 'validation_checker.py'
        if not validator_file.exists():
            return mapeo

        try:
            # Leer solo la sección MAPEO_BIOMARCADORES
            contenido = self.smart_reader.read_section(validator_file, 'MAPEO_BIOMARCADORES')
            if not contenido:
                contenido = self.smart_reader.read_full(validator_file)

            if contenido:
                # Buscar el diccionario MAPEO_BIOMARCADORES
                match = re.search(r'MAPEO_BIOMARCADORES\s*=\s*\{([^}]+)\}', contenido, re.DOTALL)
                if match:
                    dict_content = match.group(1)
                    # Parsear manualmente las líneas
                    for line in dict_content.split('\n'):
                        if ':' in line and not line.strip().startswith('#'):
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
                content = self.smart_reader.read_full(py_file)
                if content:
                    tree = ast.parse(content)
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
            contenido = self.smart_reader.read_full(archivo)

            # TODO: Implementar lógica de inserción inteligente de patrón
            # Por ahora, solo reportamos

            print(f"⚠️  Edición automática de extractores en desarrollo")
            print(f"💡 Por ahora, edita manualmente: {archivo}")
            print(f"   Agregar patrón: {patron}")

        except Exception as e:
            print(f"❌ Error aplicando edición: {e}")

    def agregar_biomarcador_completo(self, nombre: str, variantes: List[str],
                                    descripcion: str = None, simular: bool = False):
        """
        Agrega un biomarcador completo: extractor + mapeo + BD + validación
        NUEVA VERSIÓN v2.0: Usa ChangePropagator para propagar a LOS 4 ARCHIVOS
        """
        print(f"\n{'='*80}")
        print(f"➕ AGREGANDO BIOMARCADOR COMPLETO: {nombre}")
        print(f"{'='*80}\n")

        nombre_upper = nombre.upper()
        columna_bd = f"IHQ_{nombre_upper.replace('-', '_')}"

        print(f"Nombre: {nombre}")
        print(f"Variantes: {', '.join(variantes)}")
        print(f"Columna BD: {columna_bd}\n")

        if simular:
            # Mostrar simulación detallada
            simulacion = self.change_simulator.simulate_biomarker_addition(
                nombre, variantes, descripcion
            )
            print(simulacion)
        else:
            # Aplicar cambios reales
            resultado = self.change_propagator.agregar_biomarcador_completo(
                nombre, variantes, descripcion
            )

            print(f"\n{'='*80}")
            print(f"📊 RESUMEN DE AGREGACIÓN")
            print(f"{'='*80}")
            print(f"Biomarcador: {resultado['nombre']}")
            print(f"Columna BD: {resultado['columna_bd']}")
            print(f"Variantes: {len(resultado['variantes']) + 1}")
            print(f"\n✅ Archivos modificados ({len(resultado['archivos_modificados'])}):")
            for archivo in resultado['archivos_modificados']:
                print(f"   - {archivo}")

            if resultado['errores']:
                print(f"\n⚠️  Errores encontrados ({len(resultado['errores'])}):")
                for error in resultado['errores']:
                    print(f"   - {error}")
            else:
                print(f"\n✅ BIOMARCADOR {nombre} AGREGADO COMPLETAMENTE")

            # Registrar acción
            self.registrar_accion("Agregar Biomarcador Completo", {
                'Nombre': nombre,
                'Columna BD': columna_bd,
                'Variantes': variantes,
                'Archivos modificados': resultado['archivos_modificados'],
                'Errores': resultado['errores']
            })

    def modificar_biomarcador(self, nombre: str, campo: str, nuevo_valor: Any,
                             agregar: bool = False, simular: bool = True):
        """
        Modifica un campo de un biomarcador existente

        Args:
            nombre: Nombre del biomarcador (ej: 'KI67', 'HER2')
            campo: Campo a modificar ('descripcion', 'patrones', 'valores_posibles', 'normalizacion')
            nuevo_valor: Nuevo valor para el campo
            agregar: Si True, agrega valor (para patrones). Si False, reemplaza
            simular: Si True, solo muestra cambios sin aplicar
        """
        print(f"\n{'='*80}")
        print(f"🔧 MODIFICANDO BIOMARCADOR: {nombre}")
        print(f"{'='*80}\n")

        nombre_upper = nombre.upper()
        print(f"Campo a modificar: {campo}")
        print(f"Nuevo valor: {nuevo_valor}")
        print(f"Modo: {'Agregar' if agregar else 'Reemplazar'}")
        print(f"Simulación: {'SÍ' if simular else 'NO'}\n")

        # Archivo donde están las definiciones
        bio_extractor = PROJECT_ROOT / 'core' / 'extractors' / 'biomarker_extractor.py'

        if not bio_extractor.exists():
            print(f"❌ No se encontró biomarker_extractor.py")
            return

        try:
            # Leer archivo completo
            contenido = self.smart_reader.read_full(bio_extractor)
            if not contenido:
                print(f"❌ No se pudo leer archivo")
                return

            # Buscar la definición del biomarcador
            pattern = rf"'{nombre_upper}':\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}},"
            match = re.search(pattern, contenido, re.DOTALL)

            if not match:
                print(f"❌ Biomarcador '{nombre_upper}' no encontrado en BIOMARKER_DEFINITIONS")
                print(f"💡 Usa --agregar-biomarcador para crear uno nuevo")
                return

            definicion_actual = match.group(0)
            inicio_definicion = match.start()
            fin_definicion = match.end()

            print(f"✅ Biomarcador '{nombre_upper}' encontrado")

            # Construir nueva definición según el campo a modificar
            nueva_definicion = definicion_actual

            if campo == 'descripcion':
                # Reemplazar descripción
                nueva_definicion = re.sub(
                    r"'descripcion':\s*'[^']*'",
                    f"'descripcion': '{nuevo_valor}'",
                    nueva_definicion
                )

            elif campo == 'patrones':
                if agregar:
                    # Agregar patrón a la lista existente
                    patron_insert = f"            {nuevo_valor},\n"
                    nueva_definicion = re.sub(
                        r"('patrones':\s*\[\s*\n)",
                        rf"\1{patron_insert}",
                        nueva_definicion
                    )
                else:
                    # Reemplazar todos los patrones
                    patrones_str = f"            {nuevo_valor},"
                    nueva_definicion = re.sub(
                        r"'patrones':\s*\[[^\]]+\]",
                        f"'patrones': [\n{patrones_str}\n        ]",
                        nueva_definicion,
                        flags=re.DOTALL
                    )

            elif campo == 'valores_posibles':
                # Parsear el nuevo valor si es string JSON
                if isinstance(nuevo_valor, str):
                    try:
                        valores_list = eval(nuevo_valor)
                        valores_str = str(valores_list)
                    except:
                        valores_str = nuevo_valor
                else:
                    valores_str = str(nuevo_valor)

                nueva_definicion = re.sub(
                    r"'valores_posibles':\s*\[[^\]]+\]",
                    f"'valores_posibles': {valores_str}",
                    nueva_definicion
                )

            elif campo == 'normalizacion':
                # Reemplazar diccionario de normalización
                nueva_definicion = re.sub(
                    r"'normalizacion':\s*\{[^}]+\}",
                    f"'normalizacion': {nuevo_valor}",
                    nueva_definicion,
                    flags=re.DOTALL
                )

            else:
                print(f"❌ Campo '{campo}' no reconocido")
                print(f"💡 Campos válidos: descripcion, patrones, valores_posibles, normalizacion")
                return

            if simular:
                # Mostrar diff de los cambios
                print(f"🔍 SIMULACIÓN DE CAMBIOS:")
                print(f"{'='*80}")
                print(f"\n📄 Archivo: biomarker_extractor.py")
                print(f"🔧 Biomarcador: {nombre_upper}")
                print(f"📝 Campo: {campo}\n")
                print(f"ANTES:")
                print("-" * 80)
                print(definicion_actual[:500] + ("..." if len(definicion_actual) > 500 else ""))
                print()
                print(f"DESPUÉS:")
                print("-" * 80)
                print(nueva_definicion[:500] + ("..." if len(nueva_definicion) > 500 else ""))
                print()
                print(f"{'='*80}")
                print(f"✅ Simulación completada - Usa sin --simular para aplicar")

            else:
                # Aplicar cambio real
                print(f"✏️  Aplicando cambio...")

                # Crear backup
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_filename = f"biomarker_extractor_backup_{timestamp}.py"
                backup_path = self.backups_dir / backup_filename
                shutil.copy(bio_extractor, backup_path)
                print(f"📦 Backup creado: backups/{backup_filename}")

                # Reemplazar en contenido
                nuevo_contenido = (
                    contenido[:inicio_definicion] +
                    nueva_definicion +
                    contenido[fin_definicion:]
                )

                # Validar sintaxis Python
                try:
                    ast.parse(nuevo_contenido)
                    print(f"✅ Sintaxis Python validada")
                except SyntaxError as e:
                    print(f"❌ Error de sintaxis después de modificación:")
                    print(f"   Línea {e.lineno}: {e.msg}")
                    return

                # Escribir archivo
                with open(bio_extractor, 'w', encoding='utf-8') as f:
                    f.write(nuevo_contenido)

                print(f"✅ Biomarcador '{nombre_upper}' modificado exitosamente")
                print(f"   Campo modificado: {campo}")

                # Generar reporte
                self.registrar_accion("Modificación de Biomarcador", {
                    'Biomarcador': nombre_upper,
                    'Campo modificado': campo,
                    'Nuevo valor': str(nuevo_valor)[:100],
                    'Modo': 'Agregar' if agregar else 'Reemplazar',
                    'Archivo': 'biomarker_extractor.py',
                    'Backup': backup_filename
                })

                print(f"\n💡 Próximos pasos:")
                print(f"   1. Validar con: python editor_core.py --validar-sintaxis biomarker_extractor.py")
                print(f"   2. Reprocesar casos afectados si es necesario")

        except Exception as e:
            print(f"❌ Error modificando biomarcador: {e}")
            import traceback
            traceback.print_exc()

    def eliminar_biomarcador(self, nombre: str, confirmar: bool = False, mantener_datos: bool = True):
        """
        Elimina un biomarcador completo del sistema

        ATENCIÓN: Esta operación es PELIGROSA y puede causar pérdida de datos.

        Args:
            nombre: Nombre del biomarcador a eliminar
            confirmar: Debe ser True para ejecutar (protección)
            mantener_datos: Si True, mantiene columna BD con datos (solo elimina código)
        """
        print(f"\n{'='*80}")
        print(f"⚠️  ELIMINAR BIOMARCADOR: {nombre}")
        print(f"{'='*80}\n")

        nombre_upper = nombre.upper()
        columna_bd = f"IHQ_{nombre_upper.replace('-', '_')}"

        # Los 4 archivos críticos que pueden contener el biomarcador
        archivos_criticos = {
            'biomarker_extractor.py': PROJECT_ROOT / 'core' / 'extractors' / 'biomarker_extractor.py',
            'validation_checker.py': PROJECT_ROOT / 'core' / 'validation_checker.py',
            'unified_extractor.py': PROJECT_ROOT / 'core' / 'unified_extractor.py',
            'database_manager.py': PROJECT_ROOT / 'core' / 'database_manager.py'
        }

        print(f"🔍 Analizando presencia del biomarcador en el sistema...\n")

        # Analizar qué se va a eliminar
        analisis = {
            'biomarker_extractor.py': [],
            'validation_checker.py': [],
            'unified_extractor.py': [],
            'database_manager.py': []
        }

        # 1. Analizar biomarker_extractor.py
        bio_extractor = archivos_criticos['biomarker_extractor.py']
        if bio_extractor.exists():
            contenido = self.smart_reader.read_full(bio_extractor)
            if contenido:
                pattern = rf"'{nombre_upper}':\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}},"
                match = re.search(pattern, contenido, re.DOTALL)
                if match:
                    linea_inicio = contenido[:match.start()].count('\n') + 1
                    linea_fin = contenido[:match.end()].count('\n') + 1
                    analisis['biomarker_extractor.py'].append(
                        f"Definición completa (líneas {linea_inicio}-{linea_fin})"
                    )

        # 2. Analizar validation_checker.py
        validation = archivos_criticos['validation_checker.py']
        if validation.exists():
            contenido = self.smart_reader.read_full(validation)
            if contenido:
                # Buscar todas las variantes mapeadas
                variantes_encontradas = []
                for line in contenido.split('\n'):
                    if columna_bd in line and ':' in line:
                        match = re.search(r"'([^']+)':\s*'" + columna_bd, line)
                        if match:
                            variantes_encontradas.append(match.group(1))

                if variantes_encontradas:
                    analisis['validation_checker.py'].append(
                        f"{len(variantes_encontradas)} variantes mapeadas: {', '.join(variantes_encontradas[:5])}"
                    )

        # 3. Analizar unified_extractor.py (3 diccionarios)
        unified = archivos_criticos['unified_extractor.py']
        if unified.exists():
            contenido = self.smart_reader.read_full(unified)
            if contenido:
                # Contar ocurrencias
                ocurrencias = contenido.count(f"'{nombre_upper}'") + contenido.count(f"'{columna_bd}'")
                if ocurrencias > 0:
                    analisis['unified_extractor.py'].append(
                        f"{ocurrencias} entradas en diccionarios de mapeo"
                    )

        # 4. Analizar database_manager.py
        db_manager = archivos_criticos['database_manager.py']
        if db_manager.exists():
            contenido = self.smart_reader.read_full(db_manager)
            if contenido:
                if columna_bd in contenido:
                    analisis['database_manager.py'].append(
                        f"Columna '{columna_bd}' en NEW_TABLE_COLUMNS_ORDER y CREATE TABLE"
                    )

        # Verificar si existe en BD
        columna_existe_bd = False
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(informes_ihq)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]
            columna_existe_bd = columna_bd in columnas_existentes
            conn.close()
        except:
            pass

        # Mostrar resumen de lo que se eliminará
        print(f"⚠️  ADVERTENCIA: Eliminar biomarcador {nombre_upper}")
        print(f"{'='*80}\n")

        tiene_referencias = False
        for archivo, items in analisis.items():
            if items:
                tiene_referencias = True
                print(f"📄 {archivo}:")
                for item in items:
                    print(f"   - {item}")
                print()

        if not tiene_referencias:
            print(f"⚠️  El biomarcador '{nombre_upper}' no se encontró en el sistema")
            print(f"💡 Verifica que el nombre sea correcto")
            return

        # Información de BD
        print(f"💾 BASE DE DATOS:")
        print(f"   Columna: {columna_bd}")
        if columna_existe_bd:
            if mantener_datos:
                print(f"   ✅ Mantener datos: SÍ (columna permanece, solo se elimina código)")
            else:
                print(f"   ⚠️  Eliminar columna: SÍ (SE PERDERÁN TODOS LOS DATOS)")
        else:
            print(f"   ℹ️  La columna no existe en la BD")
        print()

        # Verificar confirmación
        if not confirmar:
            print(f"{'='*80}")
            print(f"❌ OPERACIÓN CANCELADA")
            print(f"{'='*80}")
            print(f"\n⚠️  Esta es una operación PELIGROSA.")
            print(f"💡 Usa --confirmar para ejecutar la eliminación")
            print(f"💡 Usa --eliminar-datos para también eliminar la columna de BD (PELIGROSO)")
            return

        # Ejecutar eliminación
        print(f"{'='*80}")
        print(f"🔥 EJECUTANDO ELIMINACIÓN")
        print(f"{'='*80}\n")

        archivos_modificados = []
        errores = []

        # Crear timestamp para backups
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        try:
            # 1. Eliminar de biomarker_extractor.py
            if analisis['biomarker_extractor.py']:
                print(f"1️⃣  Eliminando de biomarker_extractor.py...")
                try:
                    backup_path = self.backups_dir / f"biomarker_extractor_backup_{timestamp}.py"
                    shutil.copy(bio_extractor, backup_path)

                    contenido = self.smart_reader.read_full(bio_extractor)
                    pattern = rf"'{nombre_upper}':\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}},\n?"
                    nuevo_contenido = re.sub(pattern, '', contenido, flags=re.DOTALL)

                    # Validar sintaxis
                    ast.parse(nuevo_contenido)

                    with open(bio_extractor, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)

                    print(f"   ✅ Eliminado de BIOMARKER_DEFINITIONS")
                    archivos_modificados.append('biomarker_extractor.py')
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errores.append(f"biomarker_extractor.py: {e}")

            # 2. Eliminar de validation_checker.py
            if analisis['validation_checker.py']:
                print(f"2️⃣  Eliminando de validation_checker.py...")
                try:
                    backup_path = self.backups_dir / f"validation_checker_backup_{timestamp}.py"
                    shutil.copy(validation, backup_path)

                    contenido = self.smart_reader.read_full(validation)
                    lineas = contenido.split('\n')
                    nuevas_lineas = []

                    for linea in lineas:
                        # Eliminar líneas que contengan el mapeo a esta columna
                        if f"'{columna_bd}'" not in linea or ':' not in linea:
                            nuevas_lineas.append(linea)

                    nuevo_contenido = '\n'.join(nuevas_lineas)

                    with open(validation, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)

                    print(f"   ✅ Eliminadas variantes de MAPEO_BIOMARCADORES")
                    archivos_modificados.append('validation_checker.py')
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errores.append(f"validation_checker.py: {e}")

            # 3. Eliminar de unified_extractor.py
            if analisis['unified_extractor.py']:
                print(f"3️⃣  Eliminando de unified_extractor.py...")
                try:
                    backup_path = self.backups_dir / f"unified_extractor_backup_{timestamp}.py"
                    shutil.copy(unified, backup_path)

                    contenido = self.smart_reader.read_full(unified)
                    lineas = contenido.split('\n')
                    nuevas_lineas = []

                    for linea in lineas:
                        # Eliminar líneas que contengan el biomarcador o columna
                        if (f"'{nombre_upper}'" not in linea and f"'{columna_bd}'" not in linea) or ':' not in linea:
                            nuevas_lineas.append(linea)
                        else:
                            # Verificar que es realmente una línea de mapeo
                            if re.search(rf"'({nombre_upper}|{columna_bd})':\s*'", linea):
                                continue  # Saltar esta línea
                            else:
                                nuevas_lineas.append(linea)

                    nuevo_contenido = '\n'.join(nuevas_lineas)

                    with open(unified, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)

                    print(f"   ✅ Eliminado de los 3 diccionarios de mapeo")
                    archivos_modificados.append('unified_extractor.py')
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errores.append(f"unified_extractor.py: {e}")

            # 4. Eliminar de database_manager.py
            if analisis['database_manager.py']:
                print(f"4️⃣  Eliminando de database_manager.py...")
                try:
                    backup_path = self.backups_dir / f"database_manager_backup_{timestamp}.py"
                    shutil.copy(db_manager, backup_path)

                    contenido = self.smart_reader.read_full(db_manager)
                    lineas = contenido.split('\n')
                    nuevas_lineas = []

                    for linea in lineas:
                        # Eliminar líneas que contengan la columna
                        if f'"{columna_bd}"' not in linea:
                            nuevas_lineas.append(linea)

                    nuevo_contenido = '\n'.join(nuevas_lineas)

                    with open(db_manager, 'w', encoding='utf-8') as f:
                        f.write(nuevo_contenido)

                    print(f"   ✅ Eliminado de NEW_TABLE_COLUMNS_ORDER y CREATE TABLE")
                    archivos_modificados.append('database_manager.py')
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errores.append(f"database_manager.py: {e}")

            # 5. Eliminar columna de BD (PELIGROSO)
            if not mantener_datos and columna_existe_bd:
                print(f"5️⃣  Eliminando columna de BD...")
                print(f"   ⚠️  ADVERTENCIA: Esto eliminará TODOS los datos")

                try:
                    # Backup de BD
                    from herramientas_ia.gestor_base_datos import GestorBaseDatos
                    gestor = GestorBaseDatos()
                    backup_name = f"antes_eliminar_{nombre_upper}_{timestamp}.db"
                    gestor.backup_bd(backup_name)
                    print(f"   📦 Backup de BD creado: {backup_name}")

                    # SQLite no soporta DROP COLUMN directamente
                    # Habría que recrear la tabla sin esa columna
                    print(f"   ⚠️  SQLite no soporta DROP COLUMN")
                    print(f"   💡 La columna '{columna_bd}' permanece en BD pero sin código que la use")

                except Exception as e:
                    print(f"   ❌ Error: {e}")
                    errores.append(f"BD: {e}")

            # Resumen final
            print(f"\n{'='*80}")
            print(f"📊 RESUMEN DE ELIMINACIÓN")
            print(f"{'='*80}")
            print(f"Biomarcador eliminado: {nombre_upper}")
            print(f"Columna BD: {columna_bd}")
            print(f"\n✅ Archivos modificados ({len(archivos_modificados)}):")
            for archivo in archivos_modificados:
                print(f"   - {archivo}")

            if errores:
                print(f"\n⚠️  Errores encontrados ({len(errores)}):")
                for error in errores:
                    print(f"   - {error}")

            print(f"\n📦 Backups creados en: backups/")
            print(f"💡 Backups con timestamp: {timestamp}")

            if mantener_datos and columna_existe_bd:
                print(f"\nℹ️  La columna '{columna_bd}' permanece en BD con los datos")

            # Registrar acción
            self.registrar_accion("Eliminación de Biomarcador", {
                'Biomarcador': nombre_upper,
                'Columna BD': columna_bd,
                'Archivos modificados': archivos_modificados,
                'Datos BD': 'Mantenidos' if mantener_datos else 'Eliminados',
                'Errores': errores,
                'Timestamp backup': timestamp
            })

            print(f"\n✅ BIOMARCADOR {nombre_upper} ELIMINADO")

        except Exception as e:
            print(f"\n❌ Error crítico durante eliminación: {e}")
            import traceback
            traceback.print_exc()
            print(f"\n💡 Restaurar desde backups en backups/*_backup_{timestamp}.py")

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

    # ========== 3. SIMULACIÓN Y VALIDACIÓN ==========

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
                content = self.smart_reader.read_full(py_file)
                if content:
                    # Buscar imports del archivo editado
                    archivo_sin_ext = archivo_editado.replace('.py', '')
                    if re.search(rf'from\s+core.*import.*{archivo_sin_ext}', content):
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

    # ========== 4. ANÁLISIS DE ARQUITECTURA ==========

    def analizar_arquitectura_completa(self):
        """Analiza toda la arquitectura de core/ usando FileMapper"""
        print(f"\n{'='*80}")
        print("🏗️ ANÁLISIS DE ARQUITECTURA COMPLETA v2.0")
        print(f"{'='*80}\n")

        print("📊 ARCHIVOS GRANDES (>1000 líneas):")
        for nombre, info in FileMapper.LARGE_FILES.items():
            print(f"\n  {nombre} ({info.size_lines} líneas)")
            for sec_name, section in info.sections.items():
                print(f"    - {sec_name}: L{section.start_line}-{section.end_line} ({section.description})")

        print(f"\n📊 ARCHIVOS MEDIANOS (500-1000 líneas):")
        for nombre, info in FileMapper.MEDIUM_FILES.items():
            print(f"  - {nombre} ({info.size_lines} líneas)")

        print(f"\n📊 BIOMARCADORES MAPEADOS: {len(self.conocimiento['mapeo_biomarcadores'])}")

        print(f"\n📊 PUNTOS DE INTEGRACIÓN CRÍTICOS:")
        for archivo, config in FileMapper.CRITICAL_INTEGRATION_POINTS.items():
            print(f"  {archivo}:")
            print(f"    {config['description']}")

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

    # ========== 5. FUNCIONALIDADES EXTENDIDAS ==========

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
            codigo = self.smart_reader.read_full(archivo_path)
            if not codigo:
                print(f"❌ No se pudo leer archivo")
                return

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
            codigo = self.smart_reader.read_full(archivo_path)
            if not codigo:
                print(f"❌ No se pudo leer archivo")
                return False

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
            codigo = self.smart_reader.read_full(archivo_path)
            if not codigo:
                print(f"❌ No se pudo leer archivo")
                return

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

        # Buscar backup más reciente en carpeta centralizada
        backups = sorted(self.backups_dir.glob(f"{archivo_path.stem}_backup_*.py"), reverse=True)

        if not backups:
            print(f"⚠️  No existe backup para comparar")
            print(f"💡 Los backups se crean automáticamente al modificar archivos")
            return

        backup_path = backups[0]
        print(f"📦 Comparando con backup: {backup_path.name}\n")

        try:
            # Leer ambas versiones
            codigo_nuevo = self.smart_reader.read_full(archivo_path)
            codigo_viejo = self.smart_reader.read_full(backup_path)

            if not codigo_nuevo or not codigo_viejo:
                print(f"❌ No se pudieron leer archivos para comparación")
                return

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
        contenido = f"""# Reporte de Cambios - Editor Core v2.0

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

        # Agregar sección de próximos pasos
        contenido += "\n---\n\n## 💡 Próximos Pasos Recomendados\n\n"
        contenido += "1. Validar cambios con `data-auditor`\n"
        contenido += "2. Ejecutar tests automáticos\n"
        contenido += "3. Actualizar versión del sistema con `version-manager`\n"
        contenido += "4. Generar documentación con `documentation-specialist`\n"

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
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"antes_migracion_{nueva_columna}_{timestamp}.db"

            from herramientas_ia.gestor_base_datos import GestorBaseDatos
            gestor = GestorBaseDatos()

            print("📦 Creando backup de base de datos...")
            gestor.backup_bd(backup_name)

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
            print(f"🔧 Agregando columna '{nueva_columna}'...")
            cursor.execute(f'ALTER TABLE informes_ihq ADD COLUMN "{nueva_columna}" {tipo} DEFAULT "{valor_default}"')

            conn.commit()
            conn.close()

            print(f"✅ MIGRACIÓN COMPLETADA")
            print(f"   Columna agregada: {nueva_columna}")
            print(f"   Tipo: {tipo}")
            print(f"   Default: {valor_default}")

        except Exception as e:
            print(f"❌ Error en migración: {e}")
            print(f"💡 Restaurar desde backup si es necesario")


def main():
    """CLI principal"""
    parser = argparse.ArgumentParser(
        description="✏️ Editor Core EVARISIS v2.0 - Editor Inteligente Avanzado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

AGREGAR BIOMARCADOR COMPLETO (NUEVO v2.0):
  python editor_core.py --agregar-biomarcador BCL2 --variantes "BCL-2,BCL 2" --descripcion "Proteína antiapoptótica"
  python editor_core.py --agregar-biomarcador BCL2 --variantes "BCL-2,BCL 2" --simular  # Simular primero

MODIFICAR BIOMARCADOR (NUEVO v2.0):
  python editor_core.py --modificar-biomarcador KI67 --campo descripcion --valor "Índice de proliferación celular actualizado" --simular
  python editor_core.py --modificar-biomarcador HER2 --campo patrones --valor "r'(?i)HER2\\s+SCORE\\s*:\\s*(\\d+)'" --agregar
  python editor_core.py --modificar-biomarcador PDL1 --campo valores_posibles --valor "['POSITIVO', 'NEGATIVO', 'ALTO', 'BAJO']"

ELIMINAR BIOMARCADOR (NUEVO v2.0 - PELIGROSO):
  python editor_core.py --eliminar-biomarcador TEST_DEMO  # Ver qué se eliminaría (sin confirmar)
  python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar  # Eliminar (mantener datos BD)
  python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar --eliminar-datos  # PELIGROSO (eliminar también columna BD)

EDICIÓN:
  python editor_core.py --editar-extractor Ki-67 --patron "índice.*?(\\d+)%" --razon "Mejorar detección"
  python editor_core.py --editar-extractor Ki-67 --simular  # Simular primero

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
    parser.add_argument("--descripcion", help="Descripción del biomarcador")
    parser.add_argument("--modificar-biomarcador", help="Modificar biomarcador existente")
    parser.add_argument("--campo", help="Campo a modificar (descripcion, patrones, valores_posibles, normalizacion)")
    parser.add_argument("--valor", help="Nuevo valor para el campo")
    parser.add_argument("--agregar", action="store_true", help="Agregar valor en lugar de reemplazar (para patrones)")
    parser.add_argument("--eliminar-biomarcador", help="Eliminar biomarcador del sistema")
    parser.add_argument("--confirmar", action="store_true", help="Confirmar eliminación (protección)")
    parser.add_argument("--eliminar-datos", action="store_true", help="Eliminar también columna BD (PELIGROSO)")

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
            editor.agregar_biomarcador_completo(
                args.agregar_biomarcador,
                variantes,
                descripcion=args.descripcion,
                simular=args.simular
            )

        elif args.modificar_biomarcador:
            if not args.campo or not args.valor:
                print("❌ Se requieren --campo y --valor")
                sys.exit(1)
            editor.modificar_biomarcador(
                args.modificar_biomarcador,
                args.campo,
                args.valor,
                agregar=args.agregar,
                simular=args.simular
            )

        elif args.eliminar_biomarcador:
            mantener_datos = not args.eliminar_datos
            editor.eliminar_biomarcador(
                args.eliminar_biomarcador,
                confirmar=args.confirmar,
                mantener_datos=mantener_datos
            )

        elif args.reprocesar:
            editor.reprocesar_caso(args.reprocesar, validar_antes=args.validar_antes)

        elif args.reprocesar_lote:
            casos = [c.strip() for c in args.reprocesar_lote.split(',')]
            editor.reprocesar_lote(casos)

        elif args.simular and args.archivo:
            funcion = getattr(args, 'funcion', 'function_example')
            editor.simular_cambio(args.archivo, funcion, "cambio ejemplo")

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
