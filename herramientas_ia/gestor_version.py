#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTOR DE VERSIONES - EVARISIS
Herramienta para actualizar la versión del sistema en todos los archivos relevantes

IMPORTANTE: Solo actualiza la versión cuando el usuario lo solicita explícitamente.
Las modificaciones funcionales NO deben cambiar la versión automáticamente.
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple
import json

# Configuración UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent

# ============================================================================
# TEMPLATES PARA CHANGELOG Y BITÁCORA
# ============================================================================

TEMPLATE_CHANGELOG_INICIAL = """# Changelog

Todos los cambios importantes de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Added
- Próximas funcionalidades...

---
"""

TEMPLATE_BITACORA_INICIAL = """# Bitácora de Acercamientos - {nombre_proyecto}

**Propósito**: Registro formal y auditable de la evolución del proyecto.

Documenta cada iteración de trabajo y validación con stakeholders del Hospital Universitario del Valle.

---
"""


class GestorVersion:
    """Gestor centralizado de versiones del sistema EVARISIS"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.version_file = self.project_root / "config" / "version_info.py"

        # NUEVOS archivos para gestión de documentación
        self.docs_dir = self.project_root / "documentacion"
        self.changelog_file = self.docs_dir / "CHANGELOG.md"
        self.bitacora_file = self.docs_dir / "BITACORA_DE_ACERCAMIENTOS.md"
        self.legacy_dir = self.project_root / "LEGACY"

        # Archivos que contienen versión y deben actualizarse
        self.archivos_version = [
            self.version_file,
            self.project_root / "README.md",
            self.project_root / ".claude" / "CLAUDE.md",
            self.project_root / "ECOSISTEMA_4+5_VALIDACION.md",
            self.project_root / "ui.py",
        ]

    def obtener_version_actual(self) -> Dict[str, str]:
        """Lee la versión actual desde config/version_info.py"""
        if not self.version_file.exists():
            return {
                "version": "0.0.0",
                "version_name": "Unknown",
                "build_date": datetime.now().strftime("%d/%m/%Y"),
                "build_number": "00000000000",
                "release_type": "Unknown"
            }

        with open(self.version_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extraer información de VERSION_INFO
        version_match = re.search(r'"version":\s*"([^"]+)"', content)
        name_match = re.search(r'"version_name":\s*"([^"]+)"', content)
        date_match = re.search(r'"build_date":\s*"([^"]+)"', content)
        build_match = re.search(r'"build_number":\s*"([^"]+)"', content)
        type_match = re.search(r'"release_type":\s*"([^"]+)"', content)

        return {
            "version": version_match.group(1) if version_match else "0.0.0",
            "version_name": name_match.group(1) if name_match else "Unknown",
            "build_date": date_match.group(1) if date_match else "",
            "build_number": build_match.group(1) if build_match else "",
            "release_type": type_match.group(1) if type_match else "Unknown"
        }

    def validar_formato_version(self, version: str) -> bool:
        """Valida que la versión tenga formato X.Y.Z"""
        patron = r'^\d+\.\d+\.\d+$'
        return bool(re.match(patron, version))

    def comparar_versiones(self, v1: str, v2: str) -> int:
        """Compara dos versiones. Retorna 1 si v1 > v2, -1 si v1 < v2, 0 si iguales"""
        parts1 = [int(x) for x in v1.split('.')]
        parts2 = [int(x) for x in v2.split('.')]

        for i in range(3):
            if parts1[i] > parts2[i]:
                return 1
            elif parts1[i] < parts2[i]:
                return -1
        return 0

    def incrementar_version(self, version_actual: str, tipo: str = 'patch') -> str:
        """Incrementa la versión según el tipo: major, minor, patch"""
        parts = [int(x) for x in version_actual.split('.')]

        if tipo == 'major':
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        elif tipo == 'minor':
            parts[1] += 1
            parts[2] = 0
        elif tipo == 'patch':
            parts[2] += 1

        return f"{parts[0]}.{parts[1]}.{parts[2]}"

    def generar_build_number(self) -> str:
        """Genera build number en formato YYYYMMDDHHH"""
        now = datetime.now()
        return now.strftime("%Y%m%d%H%M")

    def actualizar_version_info(self, nueva_version: str, version_name: str = None,
                                release_type: str = "Stable", dry_run: bool = False) -> Dict:
        """Actualiza config/version_info.py con la nueva versión"""

        if not self.version_file.exists():
            return {"error": "Archivo version_info.py no encontrado"}

        with open(self.version_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Generar nuevos valores
        nueva_fecha = datetime.now().strftime("%d/%m/%Y")
        nuevo_build = self.generar_build_number()

        # Si no se proporciona version_name, mantener el actual
        if version_name is None:
            name_match = re.search(r'"version_name":\s*"([^"]+)"', content)
            version_name = name_match.group(1) if name_match else "Sistema Consolidado"

        # Reemplazos
        content = re.sub(
            r'"version":\s*"[^"]+"',
            f'"version": "{nueva_version}"',
            content
        )
        content = re.sub(
            r'"version_name":\s*"[^"]+"',
            f'"version_name": "{version_name}"',
            content
        )
        content = re.sub(
            r'"build_date":\s*"[^"]+"',
            f'"build_date": "{nueva_fecha}"',
            content
        )
        content = re.sub(
            r'"build_number":\s*"[^"]+"',
            f'"build_number": "{nuevo_build}"',
            content
        )
        content = re.sub(
            r'"release_type":\s*"[^"]+"',
            f'"release_type": "{release_type}"',
            content
        )

        if not dry_run:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(content)

        return {
            "archivo": "config/version_info.py",
            "version": nueva_version,
            "version_name": version_name,
            "build_date": nueva_fecha,
            "build_number": nuevo_build,
            "release_type": release_type,
            "dry_run": dry_run
        }

    def actualizar_readme(self, nueva_version: str, dry_run: bool = False) -> Dict:
        """Actualiza la versión en README.md"""
        readme = self.project_root / "README.md"

        if not readme.exists():
            return {"archivo": "README.md", "status": "no encontrado"}

        with open(readme, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar patrones de versión
        patterns = [
            (r'(?i)versión:?\s*v?\d+\.\d+\.\d+', f'Versión: {nueva_version}'),
            (r'(?i)version:?\s*v?\d+\.\d+\.\d+', f'Version: {nueva_version}'),
            (r'v\d+\.\d+\.\d+', f'v{nueva_version}'),
        ]

        cambios = 0
        for patron, reemplazo in patterns:
            if re.search(patron, content):
                content = re.sub(patron, reemplazo, content)
                cambios += 1

        if not dry_run and cambios > 0:
            with open(readme, 'w', encoding='utf-8') as f:
                f.write(content)

        return {
            "archivo": "README.md",
            "cambios": cambios,
            "dry_run": dry_run
        }

    def actualizar_documentacion_ecosistema(self, nueva_version: str, dry_run: bool = False) -> List[Dict]:
        """Actualiza versión en archivos de documentación del ecosistema"""
        archivos_doc = [
            self.project_root / ".claude" / "CLAUDE.md",
            self.project_root / "ECOSISTEMA_4+5_VALIDACION.md",
        ]

        resultados = []

        for archivo in archivos_doc:
            if not archivo.exists():
                resultados.append({"archivo": archivo.name, "status": "no encontrado"})
                continue

            with open(archivo, 'r', encoding='utf-8') as f:
                content = f.read()

            # Patrones comunes en documentación
            patterns = [
                (r'Versión:\s*\d+\.\d+\.\d+', f'Versión: {nueva_version}'),
                (r'versión:\s*\d+\.\d+\.\d+', f'versión: {nueva_version}'),
                (r'\*\*Versión\*\*:\s*\d+\.\d+\.\d+', f'**Versión**: {nueva_version}'),
                (r'v\d+\.\d+\.\d+', f'v{nueva_version}'),
            ]

            cambios = 0
            for patron, reemplazo in patterns:
                if re.search(patron, content):
                    content = re.sub(patron, reemplazo, content)
                    cambios += 1

            if not dry_run and cambios > 0:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(content)

            resultados.append({
                "archivo": archivo.name,
                "cambios": cambios,
                "dry_run": dry_run
            })

        return resultados

    def crear_entrada_changelog(self, version: str, cambios: List[str], dry_run: bool = False) -> Dict:
        """
        DEPRECADO: Usar generar_changelog() en su lugar.
        Mantener por compatibilidad hacia atrás.
        """
        return self.generar_changelog(version, cambios, dry_run)

    # ========================================================================
    # NUEVOS MÉTODOS PARA GESTIÓN COMPLETA DE CHANGELOG Y BITÁCORA
    # ========================================================================

    def buscar_version_legacy_mas_reciente(self) -> str:
        """Busca la versión más reciente en LEGACY"""
        if not self.legacy_dir.exists():
            return None

        versiones = []
        for carpeta in self.legacy_dir.iterdir():
            if carpeta.is_dir() and carpeta.name.startswith('v'):
                # Extraer versión (ej: v2.5.0 -> 2.5.0)
                version_str = carpeta.name[1:]
                try:
                    # Validar que sea formato X.Y.Z
                    parts = [int(x) for x in version_str.split('.')]
                    if len(parts) == 3:
                        versiones.append((version_str, carpeta))
                except:
                    continue

        if not versiones:
            return None

        # Ordenar y retornar la más reciente
        versiones.sort(key=lambda x: [int(n) for n in x[0].split('.')], reverse=True)
        return versiones[0][1].name  # Retorna "vX.Y.Z"

    def copiar_desde_legacy(self, archivo: str, version_anterior: str = None) -> Dict:
        """
        Copia CHANGELOG o BITÁCORA desde LEGACY

        Args:
            archivo: 'changelog' o 'bitacora'
            version_anterior: Versión específica (ej: 'v2.5.0'), o None para autodetectar

        Returns:
            Dict con status de la operación
        """
        # Autodetectar versión si no se especificó
        if version_anterior is None:
            version_anterior = self.buscar_version_legacy_mas_reciente()
            if version_anterior is None:
                return {
                    "status": "error",
                    "mensaje": "No se encontraron versiones en LEGACY"
                }

        # Determinar archivo fuente
        if archivo.lower() == 'changelog':
            archivo_fuente = self.legacy_dir / version_anterior / "documentacion" / "CHANGELOG.md"
            archivo_destino = self.changelog_file
        elif archivo.lower() == 'bitacora':
            archivo_fuente = self.legacy_dir / version_anterior / "documentacion" / "BITACORA_DE_ACERCAMIENTOS.md"
            archivo_destino = self.bitacora_file
        else:
            return {
                "status": "error",
                "mensaje": f"Archivo desconocido: {archivo}. Use 'changelog' o 'bitacora'"
            }

        # Verificar que existe el archivo fuente
        if not archivo_fuente.exists():
            return {
                "status": "no_encontrado",
                "mensaje": f"No se encontró {archivo_fuente}",
                "version_legacy": version_anterior
            }

        # Crear directorio destino si no existe
        archivo_destino.parent.mkdir(parents=True, exist_ok=True)

        # Copiar archivo
        import shutil
        shutil.copy2(archivo_fuente, archivo_destino)

        return {
            "status": "copiado",
            "archivo": archivo,
            "fuente": str(archivo_fuente),
            "destino": str(archivo_destino),
            "version_legacy": version_anterior
        }

    def generar_changelog(self, version: str, cambios: List[str] = None,
                         added: List[str] = None, changed: List[str] = None,
                         fixed: List[str] = None, deprecated: List[str] = None,
                         removed: List[str] = None, security: List[str] = None,
                         dry_run: bool = False) -> Dict:
        """
        Genera o actualiza CHANGELOG.md de forma ACUMULATIVA

        Args:
            version: Nueva versión (ej: "5.4.0")
            cambios: Lista genérica de cambios (se categoriza automáticamente como "Changed")
            added: Lista de funcionalidades agregadas
            changed: Lista de cambios en funcionalidades existentes
            fixed: Lista de bugs corregidos
            deprecated: Lista de funcionalidades obsoletas
            removed: Lista de funcionalidades eliminadas
            security: Lista de parches de seguridad
            dry_run: Si es True, no escribe el archivo

        Returns:
            Dict con status de la operación
        """
        # Crear directorio si no existe
        if not dry_run:
            self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Si no existe CHANGELOG, verificar si hay uno en LEGACY
        if not self.changelog_file.exists():
            resultado_copia = self.copiar_desde_legacy('changelog')
            if resultado_copia['status'] == 'copiado':
                print(f"✅ CHANGELOG copiado desde {resultado_copia['version_legacy']}")
            elif resultado_copia['status'] == 'no_encontrado':
                # Crear desde template inicial
                if not dry_run:
                    with open(self.changelog_file, 'w', encoding='utf-8') as f:
                        f.write(TEMPLATE_CHANGELOG_INICIAL)
                print("✅ CHANGELOG creado desde template inicial")

        # Leer CHANGELOG actual (si existe)
        if self.changelog_file.exists():
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                content_actual = f.read()
        else:
            content_actual = TEMPLATE_CHANGELOG_INICIAL

        # Generar nueva entrada
        fecha = datetime.now().strftime("%Y-%m-%d")
        entrada = f"\n## [{version}] - {fecha}\n"

        # Agregar secciones solo si tienen contenido
        if added:
            entrada += "\n### Added\n"
            for item in added:
                entrada += f"- {item}\n"

        if changed or cambios:  # 'cambios' es el genérico
            entrada += "\n### Changed\n"
            if changed:
                for item in changed:
                    entrada += f"- {item}\n"
            if cambios:  # Retrocompatibilidad
                for item in cambios:
                    entrada += f"- {item}\n"

        if fixed:
            entrada += "\n### Fixed\n"
            for item in fixed:
                entrada += f"- {item}\n"

        if deprecated:
            entrada += "\n### Deprecated\n"
            for item in deprecated:
                entrada += f"- {item}\n"

        if removed:
            entrada += "\n### Removed\n"
            for item in removed:
                entrada += f"- {item}\n"

        if security:
            entrada += "\n### Security\n"
            for item in security:
                entrada += f"- {item}\n"

        entrada += "\n---\n"

        # Insertar nueva entrada al inicio (después de [Unreleased])
        if "## [Unreleased]" in content_actual:
            # Insertar después de la sección Unreleased
            content_nuevo = content_actual.replace(
                "---\n",
                f"---\n{entrada}",
                1  # Solo el primer ---
            )
        elif "# Changelog" in content_actual or "# CHANGELOG" in content_actual:
            # Insertar después del título
            lines = content_actual.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    lines.insert(i + 1, entrada)
                    break
            content_nuevo = '\n'.join(lines)
        else:
            # Crear estructura completa
            content_nuevo = f"# Changelog\n{entrada}\n{content_actual}"

        # Escribir archivo
        if not dry_run:
            with open(self.changelog_file, 'w', encoding='utf-8') as f:
                f.write(content_nuevo)

        # Validar que no se perdieron versiones
        versiones_anteriores = len(re.findall(r'## \[[\d.]+\]', content_actual))
        versiones_nuevas = len(re.findall(r'## \[[\d.]+\]', content_nuevo))

        return {
            "archivo": "documentacion/CHANGELOG.md",
            "version": version,
            "status": "actualizado" if self.changelog_file.exists() else "creado",
            "versiones_anteriores_preservadas": versiones_anteriores,
            "total_versiones": versiones_nuevas,
            "dry_run": dry_run
        }

    def generar_bitacora(self, numero_iteracion: int = None,
                        nombre_iteracion: str = None,
                        contexto: str = None,
                        cambios_implementados: List[str] = None,
                        validacion_tecnica: str = None,
                        validacion_medica: str = None,
                        decisiones_tecnicas: List[str] = None,
                        proximos_pasos: List[str] = None,
                        dry_run: bool = False) -> Dict:
        """
        Genera o actualiza BITÁCORA de forma ACUMULATIVA

        Args:
            numero_iteracion: Número de iteración (autodetecta si es None)
            nombre_iteracion: Nombre descriptivo de la iteración
            contexto: Contexto y objetivos de la iteración
            cambios_implementados: Lista de cambios implementados
            validacion_tecnica: Resultado de validación técnica
            validacion_medica: Resultado de validación médica/funcional
            decisiones_tecnicas: Lista de decisiones técnicas clave
            proximos_pasos: Lista de próximos pasos identificados
            dry_run: Si es True, no escribe el archivo

        Returns:
            Dict con status de la operación
        """
        # Crear directorio si no existe
        if not dry_run:
            self.docs_dir.mkdir(parents=True, exist_ok=True)

        # Si no existe BITÁCORA, verificar si hay una en LEGACY
        if not self.bitacora_file.exists():
            resultado_copia = self.copiar_desde_legacy('bitacora')
            if resultado_copia['status'] == 'copiado':
                print(f"✅ BITÁCORA copiada desde {resultado_copia['version_legacy']}")
            elif resultado_copia['status'] == 'no_encontrado':
                # Crear desde template inicial
                nombre_proyecto = "EVARISIS CIRUGÍA ONCOLÓGICA"
                if not dry_run:
                    with open(self.bitacora_file, 'w', encoding='utf-8') as f:
                        f.write(TEMPLATE_BITACORA_INICIAL.format(nombre_proyecto=nombre_proyecto))
                print("✅ BITÁCORA creada desde template inicial")

        # Leer BITÁCORA actual
        if self.bitacora_file.exists():
            with open(self.bitacora_file, 'r', encoding='utf-8') as f:
                content_actual = f.read()
        else:
            nombre_proyecto = "EVARISIS CIRUGÍA ONCOLÓGICA"
            content_actual = TEMPLATE_BITACORA_INICIAL.format(nombre_proyecto=nombre_proyecto)

        # Autodetectar número de iteración si no se especificó
        if numero_iteracion is None:
            # Contar iteraciones existentes
            iteraciones_existentes = len(re.findall(r'## Iteración \d+', content_actual))
            numero_iteracion = iteraciones_existentes + 1

        # Generar nueva iteración
        fecha = datetime.now().strftime("%d/%m/%Y")
        if nombre_iteracion is None:
            nombre_iteracion = f"Actualización {fecha}"

        entrada = f"\n## Iteración {numero_iteracion} — {nombre_iteracion} ({fecha})\n"

        if contexto:
            entrada += f"\n### Contexto de la iteración\n{contexto}\n"

        if cambios_implementados:
            entrada += "\n### Cambios implementados\n"
            for i, cambio in enumerate(cambios_implementados, 1):
                entrada += f"{i}. {cambio}\n"

        if validacion_tecnica:
            entrada += f"\n### Validación técnica\n{validacion_tecnica}\n"

        if validacion_medica:
            entrada += f"\n### Validación médica/funcional\n{validacion_medica}\n"

        if decisiones_tecnicas:
            entrada += "\n### Decisiones técnicas clave\n"
            for decision in decisiones_tecnicas:
                entrada += f"- {decision}\n"

        if proximos_pasos:
            entrada += "\n### Próximos pasos identificados\n"
            for paso in proximos_pasos:
                entrada += f"- [ ] {paso}\n"

        entrada += "\n---\n"

        # Insertar nueva iteración al inicio (después del propósito)
        if "---" in content_actual:
            # Insertar después del primer separador (propósito)
            parts = content_actual.split("---", 1)
            if len(parts) == 2:
                content_nuevo = parts[0] + "---\n" + entrada + parts[1]
            else:
                content_nuevo = content_actual + entrada
        else:
            content_nuevo = content_actual + entrada

        # Escribir archivo
        if not dry_run:
            with open(self.bitacora_file, 'w', encoding='utf-8') as f:
                f.write(content_nuevo)

        # Validar que no se perdieron iteraciones
        iteraciones_anteriores = len(re.findall(r'## Iteración \d+', content_actual))
        iteraciones_nuevas = len(re.findall(r'## Iteración \d+', content_nuevo))

        return {
            "archivo": "documentacion/BITACORA_DE_ACERCAMIENTOS.md",
            "iteracion": numero_iteracion,
            "nombre": nombre_iteracion,
            "status": "actualizada" if self.bitacora_file.exists() else "creada",
            "iteraciones_anteriores_preservadas": iteraciones_anteriores,
            "total_iteraciones": iteraciones_nuevas,
            "dry_run": dry_run
        }

    def actualizar_version_completa(self, nueva_version: str, version_name: str = None,
                                    release_type: str = "Stable", cambios: List[str] = None,
                                    generar_changelog: bool = False, generar_bitacora: bool = False,
                                    contexto_iteracion: str = None, validacion_tecnica: str = None,
                                    validacion_medica: str = None,
                                    dry_run: bool = False) -> Dict:
        """
        Actualiza la versión en todo el sistema de forma coordinada

        Args:
            nueva_version: Nueva versión en formato X.Y.Z
            version_name: Nombre descriptivo de la versión
            release_type: Tipo de release (Stable, Beta, Alpha)
            cambios: Lista de cambios para el CHANGELOG
            generar_changelog: Si es True, genera/actualiza CHANGELOG.md
            generar_bitacora: Si es True, genera/actualiza BITÁCORA
            contexto_iteracion: Contexto para la BITÁCORA
            validacion_tecnica: Validación técnica para la BITÁCORA
            validacion_medica: Validación médica para la BITÁCORA
            dry_run: Si es True, simula los cambios sin aplicarlos
        """

        # Validar formato
        if not self.validar_formato_version(nueva_version):
            return {"error": "Formato de versión inválido. Use X.Y.Z"}

        # Obtener versión actual
        version_actual_info = self.obtener_version_actual()
        version_actual = version_actual_info["version"]

        # Comparar versiones
        comparacion = self.comparar_versiones(nueva_version, version_actual)
        if comparacion < 0:
            return {"error": f"La nueva versión {nueva_version} es menor que la actual {version_actual}"}
        elif comparacion == 0:
            return {"error": f"La versión {nueva_version} es igual a la actual"}

        resultados = {
            "version_anterior": version_actual,
            "version_nueva": nueva_version,
            "dry_run": dry_run,
            "archivos_actualizados": []
        }

        # 1. Actualizar config/version_info.py
        resultado_version = self.actualizar_version_info(
            nueva_version, version_name, release_type, dry_run
        )
        resultados["archivos_actualizados"].append(resultado_version)

        # 2. Actualizar README.md
        resultado_readme = self.actualizar_readme(nueva_version, dry_run)
        resultados["archivos_actualizados"].append(resultado_readme)

        # 3. Actualizar documentación del ecosistema
        resultados_docs = self.actualizar_documentacion_ecosistema(nueva_version, dry_run)
        resultados["archivos_actualizados"].extend(resultados_docs)

        # 4. Generar/actualizar CHANGELOG (NUEVO - método mejorado)
        if generar_changelog and cambios:
            resultado_changelog = self.generar_changelog(nueva_version, cambios=cambios, dry_run=dry_run)
            resultados["archivos_actualizados"].append(resultado_changelog)

        # 5. Generar/actualizar BITÁCORA (NUEVO)
        if generar_bitacora:
            resultado_bitacora = self.generar_bitacora(
                nombre_iteracion=version_name or f"Versión {nueva_version}",
                contexto=contexto_iteracion,
                cambios_implementados=cambios,
                validacion_tecnica=validacion_tecnica,
                validacion_medica=validacion_medica,
                dry_run=dry_run
            )
            resultados["archivos_actualizados"].append(resultado_bitacora)

        return resultados

    def buscar_menciones_version(self) -> List[Dict]:
        """Busca todos los archivos que mencionan la versión actual"""
        version_actual = self.obtener_version_actual()["version"]

        # Extensiones a buscar
        extensiones = ['.py', '.md', '.txt', '.rst']

        menciones = []

        for extension in extensiones:
            for archivo in self.project_root.rglob(f'*{extension}'):
                # Ignorar LEGACY y venv
                if 'LEGACY' in str(archivo) or 'venv' in str(archivo):
                    continue

                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if version_actual in content or f"v{version_actual}" in content:
                        # Contar ocurrencias
                        ocurrencias = content.count(version_actual) + content.count(f"v{version_actual}")

                        menciones.append({
                            "archivo": str(archivo.relative_to(self.project_root)),
                            "ocurrencias": ocurrencias
                        })
                except:
                    continue

        return menciones


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='GESTOR DE VERSIONES - EVARISIS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:

  # Ver versión actual
  python herramientas_ia/gestor_version.py --actual

  # Copiar CHANGELOG y BITÁCORA desde LEGACY (primera vez)
  python herramientas_ia/gestor_version.py --copiar-legacy ambos
  python herramientas_ia/gestor_version.py --copiar-legacy changelog --legacy-version v2.5.0

  # Actualizar versión CON CHANGELOG y BITÁCORA (COMPLETO)
  python herramientas_ia/gestor_version.py --actualizar 5.4.0 \\
    --nombre "Nuevos Biomarcadores" \\
    --cambios "BCL2 agregado" "SOX11 agregado" "MYC agregado" \\
    --generar-changelog \\
    --generar-bitacora \\
    --contexto-iteracion "Expansión de biomarcadores oncológicos" \\
    --validacion-tecnica "Tests pasados: 95%" \\
    --validacion-medica "Dr. Bayona aprobó BCL2 y SOX11"

  # Actualizar versión simple (sin CHANGELOG/BITÁCORA)
  python herramientas_ia/gestor_version.py --actualizar 6.0.0 --nombre "Ecosistema 4+5"

  # Simular actualización completa (dry-run)
  python herramientas_ia/gestor_version.py --actualizar 5.4.0 \\
    --nombre "Test" \\
    --cambios "Cambio 1" \\
    --generar-changelog \\
    --generar-bitacora \\
    --dry-run

  # Incrementar versión automáticamente con CHANGELOG
  python herramientas_ia/gestor_version.py --incrementar patch \\
    --nombre "Hotfix Ki-67" \\
    --cambios "Corrección patrón extracción Ki-67" \\
    --generar-changelog

  # Incrementar versión minor
  python herramientas_ia/gestor_version.py --incrementar minor --nombre "Nuevas features"

  # Incrementar versión major
  python herramientas_ia/gestor_version.py --incrementar major --nombre "Breaking changes"

  # Buscar menciones de la versión actual
  python herramientas_ia/gestor_version.py --buscar-menciones

  # Exportar información de versión a JSON
  python herramientas_ia/gestor_version.py --actual --json version_actual.json

NOTAS IMPORTANTES:
  - Solo actualiza la versión cuando se ejecuta explícitamente este script
  - Las modificaciones funcionales NO deben cambiar la versión automáticamente
  - Usa --dry-run primero para simular los cambios
  - La versión sigue el formato semántico: MAJOR.MINOR.PATCH
  - CHANGELOG y BITÁCORA se generan en documentacion/ (acumulativos)
  - Si no existen, se copian automáticamente desde LEGACY o se crean desde template
        """
    )

    parser.add_argument("--actual", action="store_true",
                       help="Mostrar versión actual")

    parser.add_argument("--actualizar", metavar="VERSION",
                       help="Actualizar a nueva versión (formato X.Y.Z)")

    parser.add_argument("--incrementar", choices=['major', 'minor', 'patch'],
                       help="Incrementar versión automáticamente")

    parser.add_argument("--nombre", help="Nombre descriptivo de la versión")

    parser.add_argument("--tipo", choices=['Stable', 'Beta', 'Alpha'], default='Stable',
                       help="Tipo de release (default: Stable)")

    parser.add_argument("--cambios", nargs='+',
                       help="Lista de cambios para el CHANGELOG")

    # NUEVOS ARGUMENTOS para CHANGELOG y BITÁCORA
    parser.add_argument("--generar-changelog", action="store_true",
                       help="Generar/actualizar CHANGELOG.md (acumulativo)")

    parser.add_argument("--generar-bitacora", action="store_true",
                       help="Generar/actualizar BITACORA_DE_ACERCAMIENTOS.md (acumulativo)")

    parser.add_argument("--copiar-legacy", choices=['changelog', 'bitacora', 'ambos'],
                       help="Copiar CHANGELOG/BITÁCORA desde LEGACY")

    parser.add_argument("--legacy-version",
                       help="Versión específica de LEGACY para copiar (ej: v2.5.0)")

    parser.add_argument("--contexto-iteracion",
                       help="Contexto de la iteración para BITÁCORA")

    parser.add_argument("--validacion-tecnica",
                       help="Resultado de validación técnica para BITÁCORA")

    parser.add_argument("--validacion-medica",
                       help="Resultado de validación médica para BITÁCORA")

    parser.add_argument("--dry-run", action="store_true",
                       help="Simular cambios sin aplicarlos")

    parser.add_argument("--buscar-menciones", action="store_true",
                       help="Buscar archivos que mencionan la versión actual")

    parser.add_argument("--json", metavar="ARCHIVO",
                       help="Exportar resultado a JSON")

    args = parser.parse_args()

    gestor = GestorVersion()

    # Mostrar versión actual
    if args.actual:
        version_info = gestor.obtener_version_actual()
        print("\n" + "="*80)
        print("📦 VERSIÓN ACTUAL DEL SISTEMA")
        print("="*80)
        print(f"Versión: {version_info['version']}")
        print(f"Nombre: {version_info['version_name']}")
        print(f"Build: {version_info['build_number']}")
        print(f"Fecha: {version_info['build_date']}")
        print(f"Tipo: {version_info['release_type']}")
        print("="*80 + "\n")

        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2, ensure_ascii=False)
            print(f"✅ Información exportada a {args.json}")

        return

    # Buscar menciones
    if args.buscar_menciones:
        menciones = gestor.buscar_menciones_version()
        print("\n" + "="*80)
        print("🔍 ARCHIVOS QUE MENCIONAN LA VERSIÓN ACTUAL")
        print("="*80)
        for mencion in menciones:
            print(f"  {mencion['archivo']} ({mencion['ocurrencias']} veces)")
        print(f"\nTotal: {len(menciones)} archivos")
        print("="*80 + "\n")
        return

    # Copiar desde LEGACY
    if args.copiar_legacy:
        print(f"\n📋 COPIANDO {args.copiar_legacy.upper()} DESDE LEGACY")
        print("="*80)

        if args.copiar_legacy == 'ambos':
            archivos = ['changelog', 'bitacora']
        else:
            archivos = [args.copiar_legacy]

        for archivo in archivos:
            resultado = gestor.copiar_desde_legacy(archivo, args.legacy_version)

            if resultado['status'] == 'copiado':
                print(f"✅ {archivo.upper()} copiado exitosamente")
                print(f"   Fuente: {resultado['fuente']}")
                print(f"   Destino: {resultado['destino']}")
                print(f"   Versión LEGACY: {resultado['version_legacy']}")
            elif resultado['status'] == 'no_encontrado':
                print(f"⚠️  {archivo.upper()} no encontrado en LEGACY")
                print(f"   {resultado['mensaje']}")
            else:
                print(f"❌ Error copiando {archivo.upper()}")
                print(f"   {resultado['mensaje']}")

        print("="*80 + "\n")
        return

    # Actualizar versión
    if args.actualizar or args.incrementar:
        if args.incrementar:
            version_actual = gestor.obtener_version_actual()["version"]
            nueva_version = gestor.incrementar_version(version_actual, args.incrementar)
            print(f"\n🔢 Incrementando versión ({args.incrementar}): {version_actual} → {nueva_version}")
        else:
            nueva_version = args.actualizar

        print(f"\n{'🔍 SIMULANDO' if args.dry_run else '🚀 ACTUALIZANDO'} VERSIÓN A {nueva_version}")
        print("="*80)

        resultados = gestor.actualizar_version_completa(
            nueva_version,
            args.nombre,
            args.tipo,
            args.cambios,
            generar_changelog=args.generar_changelog,
            generar_bitacora=args.generar_bitacora,
            contexto_iteracion=args.contexto_iteracion,
            validacion_tecnica=args.validacion_tecnica,
            validacion_medica=args.validacion_medica,
            dry_run=args.dry_run
        )

        if "error" in resultados:
            print(f"❌ ERROR: {resultados['error']}")
            return

        print(f"\n📊 VERSIÓN: {resultados['version_anterior']} → {resultados['version_nueva']}")
        print(f"{'   (DRY-RUN - Sin cambios reales)' if args.dry_run else '   (CAMBIOS APLICADOS)'}\n")

        print("📝 ARCHIVOS ACTUALIZADOS:")
        for archivo in resultados['archivos_actualizados']:
            nombre = archivo.get('archivo', 'Unknown')
            cambios = archivo.get('cambios', 'N/A')
            print(f"  ✅ {nombre} ({cambios} cambios)")

        print("\n" + "="*80)

        if args.dry_run:
            print("\n💡 Ejecuta sin --dry-run para aplicar los cambios")
        else:
            print(f"\n✅ VERSIÓN ACTUALIZADA EXITOSAMENTE A {nueva_version}")

        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            print(f"📄 Resultados exportados a {args.json}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
