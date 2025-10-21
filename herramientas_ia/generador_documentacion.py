#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR DE DOCUMENTACIÓN - EVARISIS
Herramienta para generar documentación profesional automática usando los 6 prompts especializados

Basado en el sistema de prompts adaptativos ubicado en:
"agente Especialista Documentador de Programas/"
"""

import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import json

# Configuración UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.parent


class GeneradorDocumentacion:
    """Generador automático de documentación profesional para EVARISIS"""

    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.prompts_dir = self.project_root / "agente Especialista Documentador de Programas"

        # IMPORTANTE: Generar en documentacion/ (NO en documentacion_actualizada/)
        self.docs_dir = self.project_root / "documentacion"
        self.legacy_dir = self.project_root / "LEGACY"

        # Archivos que DEBE verificar que ya existan (generados por version-manager)
        self.changelog_file = self.docs_dir / "CHANGELOG.md"
        self.bitacora_file = self.docs_dir / "BITACORA_DE_ACERCAMIENTOS.md"

        # Archivos de prompts
        self.prompts = {
            "informe_global": self.prompts_dir / "01_PROMPT_ANALISIS_GLOBAL.md",
            "analisis_tecnico": self.prompts_dir / "02_PROMPT_ANALISIS_TECNICO_MODULAR.md",
            "gestion": self.prompts_dir / "03_PROMPT_GESTION_Y_TRAZABILIDAD.md",
            "comunicacion": self.prompts_dir / "04_PROMPT_COMUNICACION_STAKEHOLDERS.md",
            "doc_tecnica": self.prompts_dir / "05_PROMPT_DOCUMENTACION_TECNICA_ESPECIALIZADA.md",
            "versionado": self.prompts_dir / "06_PROMPT_SISTEMA_VERSIONADO_OBLIGATORIO.md"
        }

        # Validar que existen los prompts
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Directorio de prompts no encontrado: {self.prompts_dir}")

    def obtener_info_version(self) -> Dict[str, str]:
        """Obtiene información de versión desde config/version_info.py"""
        version_file = self.project_root / "config" / "version_info.py"

        if not version_file.exists():
            return {
                "version": "Unknown",
                "version_name": "Unknown",
                "build_date": datetime.now().strftime("%d/%m/%Y")
            }

        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()

        version_match = re.search(r'"version":\s*"([^"]+)"', content)
        name_match = re.search(r'"version_name":\s*"([^"]+)"', content)
        date_match = re.search(r'"build_date":\s*"([^"]+)"', content)

        return {
            "version": version_match.group(1) if version_match else "Unknown",
            "version_name": name_match.group(1) if name_match else "Unknown",
            "build_date": date_match.group(1) if date_match else ""
        }

    def analizar_estructura_proyecto(self) -> Dict:
        """Analiza la estructura actual del proyecto"""
        estructura = {
            "archivos_python": [],
            "directorios": [],
            "total_archivos": 0,
            "lineas_codigo": 0
        }

        # Contar archivos Python
        for archivo_py in self.project_root.rglob("*.py"):
            if "LEGACY" in str(archivo_py) or "venv" in str(archivo_py):
                continue

            estructura["archivos_python"].append(str(archivo_py.relative_to(self.project_root)))

            try:
                with open(archivo_py, 'r', encoding='utf-8') as f:
                    lineas = len(f.readlines())
                    estructura["lineas_codigo"] += lineas
            except:
                pass

        estructura["total_archivos"] = len(estructura["archivos_python"])

        # Directorios principales
        for item in self.project_root.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ['venv', 'LEGACY', '__pycache__']:
                estructura["directorios"].append(item.name)

        return estructura

    def detectar_documentacion_legacy(self) -> Dict:
        """Detecta documentación existente en LEGACY"""
        legacy_docs = {
            "existe_legacy": False,
            "documentos_encontrados": [],
            "versiones_anteriores": []
        }

        if not self.legacy_dir.exists():
            return legacy_docs

        legacy_docs["existe_legacy"] = True

        # Buscar archivos de documentación
        for doc in self.legacy_dir.rglob("*.md"):
            legacy_docs["documentos_encontrados"].append(str(doc.relative_to(self.legacy_dir)))

        # Buscar versiones antiguas
        for version_dir in self.legacy_dir.glob("v*"):
            if version_dir.is_dir():
                legacy_docs["versiones_anteriores"].append(version_dir.name)

        return legacy_docs

    def verificar_changelog_bitacora(self) -> Dict[str, bool]:
        """
        Verifica que CHANGELOG y BITÁCORA ya existan
        (deben haber sido generados por version-manager)

        IMPORTANTE: Este agente NO genera CHANGELOG ni BITÁCORA.
        Esa es responsabilidad de version-manager.

        Returns:
            Dict con estado de cada archivo y mensaje de advertencia si falta alguno
        """
        resultado = {
            "changelog_existe": self.changelog_file.exists(),
            "bitacora_existe": self.bitacora_file.exists(),
            "ambos_existen": False,
            "mensaje": ""
        }

        resultado["ambos_existen"] = resultado["changelog_existe"] and resultado["bitacora_existe"]

        if not resultado["changelog_existe"]:
            resultado["mensaje"] += f"⚠️  ADVERTENCIA: No se encontró {self.changelog_file}\n"
            resultado["mensaje"] += "   Este archivo debe ser generado por version-manager.\n"
            resultado["mensaje"] += "   Ejecuta: python herramientas_ia/gestor_version.py --copiar-legacy changelog\n\n"

        if not resultado["bitacora_existe"]:
            resultado["mensaje"] += f"⚠️  ADVERTENCIA: No se encontró {self.bitacora_file}\n"
            resultado["mensaje"] += "   Este archivo debe ser generado por version-manager.\n"
            resultado["mensaje"] += "   Ejecuta: python herramientas_ia/gestor_version.py --copiar-legacy bitacora\n\n"

        if resultado["ambos_existen"]:
            resultado["mensaje"] = "✅ CHANGELOG y BITÁCORA encontrados correctamente."

        return resultado

    def leer_cambios_version_actual(self) -> List[str]:
        """
        Lee CHANGELOG.md para extraer los cambios de la versión actual

        Esto permite que la documentación generada incluya los cambios
        de la versión actual sin tener que preguntarlos nuevamente.

        Returns:
            Lista de cambios de la versión actual
        """
        if not self.changelog_file.exists():
            return []

        try:
            with open(self.changelog_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Buscar la primera versión (la más reciente)
            # Patrón: ## [X.Y.Z] - YYYY-MM-DD
            version_match = re.search(r'## \[[\d.]+\] - [\d-]+\n(.*?)(?=\n## \[|$)', content, re.DOTALL)

            if not version_match:
                return []

            seccion_version = version_match.group(1)

            # Extraer todos los items (líneas que empiezan con "- ")
            cambios = re.findall(r'^- (.+)$', seccion_version, re.MULTILINE)

            return cambios

        except Exception as e:
            print(f"⚠️  Error leyendo CHANGELOG: {e}")
            return []

    def modo_interactivo(self, tipo_doc: str) -> Dict:
        """Modo interactivo que pregunta al usuario sobre el contexto"""
        print("\n" + "="*80)
        print(f"📝 GENERADOR DE DOCUMENTACIÓN INTERACTIVO - {tipo_doc.upper()}")
        print("="*80 + "\n")

        contexto = {}

        # Pregunta 1: ¿Nuevo o actualización?
        print("1. ¿Es un proyecto nuevo o actualización de documentación existente?")
        print("   [1] Proyecto nuevo (crear desde cero)")
        print("   [2] Actualización (extender/actualizar docs existentes)")
        opcion = input("\n   Selecciona [1/2]: ").strip()

        contexto["es_nuevo"] = (opcion == "1")

        if contexto["es_nuevo"]:
            # Preguntas para proyecto nuevo
            print("\n2. ¿Cuál es el nombre exacto del proyecto?")
            contexto["nombre_proyecto"] = input("   Nombre: ").strip()

            print("\n3. ¿Cuál es el dominio del proyecto?")
            print("   (médico, financiero, educativo, otro)")
            contexto["dominio"] = input("   Dominio: ").strip()

            print("\n4. ¿Cuáles son los stakeholders principales?")
            print("   (Separados por coma: Nombre1-Rol1, Nombre2-Rol2)")
            stakeholders_input = input("   Stakeholders: ").strip()
            contexto["stakeholders"] = stakeholders_input.split(",")

            print("\n5. ¿Cuáles son las audiencias objetivo?")
            print("   (Separadas por coma: Equipo Médico, Dirección, Investigadores)")
            audiencias_input = input("   Audiencias: ").strip()
            contexto["audiencias"] = audiencias_input.split(",")

        else:
            # Preguntas para actualización
            print("\n2. ¿Cuál es la nueva versión?")
            print(f"   (Versión actual: {self.obtener_info_version()['version']})")
            contexto["version_nueva"] = input("   Nueva versión: ").strip()

            print("\n3. ¿Qué cambios principales se han implementado?")
            print("   (Separados por coma)")
            cambios_input = input("   Cambios: ").strip()
            contexto["cambios"] = cambios_input.split(",")

            print("\n4. ¿Han cambiado los stakeholders?")
            print("   [s] Sí, [n] No")
            cambio_stakeholders = input("   ¿Cambios? [s/n]: ").strip().lower()
            contexto["stakeholders_cambiaron"] = (cambio_stakeholders == 's')

        print("\n" + "="*80)
        print("✅ Contexto capturado. Generando documentación...")
        print("="*80 + "\n")

        return contexto

    def leer_prompt(self, tipo: str) -> str:
        """Lee el contenido de un prompt específico"""
        prompt_file = self.prompts.get(tipo)

        if not prompt_file or not prompt_file.exists():
            raise FileNotFoundError(f"Prompt '{tipo}' no encontrado en {prompt_file}")

        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()

    def generar_documentacion(self, tipo: str, contexto: Dict = None, salida: Optional[str] = None) -> Dict:
        """
        Genera documentación según el tipo especificado

        Args:
            tipo: Tipo de documentación (informe_global, analisis_tecnico, etc.)
            contexto: Diccionario con contexto del usuario (modo interactivo)
            salida: Ruta de archivo de salida (opcional)
        """

        # Obtener info del proyecto
        version_info = self.obtener_info_version()
        estructura = self.analizar_estructura_proyecto()
        legacy = self.detectar_documentacion_legacy()

        # Leer prompt correspondiente
        prompt_content = self.leer_prompt(tipo)

        # Generar metadata
        metadata = {
            "tipo_documentacion": tipo,
            "fecha_generacion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version_sistema": version_info["version"],
            "archivos_analizados": estructura["total_archivos"],
            "lineas_codigo": estructura["lineas_codigo"],
            "legacy_detectado": legacy["existe_legacy"]
        }

        if contexto:
            metadata["contexto_usuario"] = contexto

        resultado = {
            "metadata": metadata,
            "prompt_usado": tipo,
            "contenido_prompt": prompt_content,
            "archivo_salida": salida if salida else f"{tipo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        }

        # Si se especificó salida, guardar el prompt
        if salida:
            output_file = self.docs_dir / salida
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Documentación Generada - {tipo.replace('_', ' ').title()}\n\n")
                f.write(f"**Fecha**: {metadata['fecha_generacion']}\n")
                f.write(f"**Versión Sistema**: {metadata['version_sistema']}\n")
                f.write(f"**Tipo**: {tipo}\n\n")
                f.write("---\n\n")
                f.write("## Prompt Utilizado\n\n")
                f.write(f"```markdown\n{prompt_content}\n```\n\n")
                f.write("---\n\n")
                f.write("## Información del Proyecto\n\n")
                f.write(f"- **Archivos Python analizados**: {estructura['total_archivos']}\n")
                f.write(f"- **Líneas de código**: {estructura['lineas_codigo']:,}\n")
                f.write(f"- **Legacy detectado**: {'Sí' if legacy['existe_legacy'] else 'No'}\n")

                if contexto:
                    f.write("\n## Contexto Capturado\n\n")
                    for key, value in contexto.items():
                        f.write(f"- **{key}**: {value}\n")

            resultado["archivo_generado"] = str(output_file)

        return resultado

    def mostrar_prompt_completo(self, tipo: str):
        """Muestra el prompt completo en consola para copiar a Claude/ChatGPT"""
        prompt_content = self.leer_prompt(tipo)

        print("\n" + "="*80)
        print(f"📋 PROMPT COMPLETO: {tipo.upper()}")
        print("="*80)
        print("\n💡 Copia este prompt completo y úsalo en Claude/ChatGPT:\n")
        print("="*80 + "\n")
        print(prompt_content)
        print("\n" + "="*80)
        print("\n✅ Prompt listo para copiar y usar en tu agente de IA preferido")
        print("="*80 + "\n")

    def validar_documentacion_existente(self) -> Dict:
        """Valida la documentación existente en el proyecto"""
        validacion = {
            "archivos_encontrados": [],
            "archivos_faltantes": [],
            "completitud": 0.0
        }

        # Documentos esperados con sus rutas correctas
        documentos_esperados = {
            "README.md": self.project_root / "README.md",
            "CHANGELOG.md": self.docs_dir / "CHANGELOG.md",
            "INFORME_GLOBAL_PROYECTO.md": self.docs_dir / "INFORME_GLOBAL_PROYECTO.md",
        }

        for nombre_doc, ruta_doc in documentos_esperados.items():
            if ruta_doc.exists():
                validacion["archivos_encontrados"].append(nombre_doc)
            else:
                validacion["archivos_faltantes"].append(nombre_doc)

        total = len(documentos_esperados)
        encontrados = len(validacion["archivos_encontrados"])
        validacion["completitud"] = (encontrados / total) * 100 if total > 0 else 0

        return validacion

    def generar_documentacion_completa(self, interactivo: bool = False) -> Dict:
        """
        Genera todos los tipos de documentación

        IMPORTANTE: Este método ASUME que version-manager YA generó:
        - documentacion/CHANGELOG.md
        - documentacion/BITACORA_DE_ACERCAMIENTOS.md

        Si no existen, mostrará una advertencia y continuará.
        """
        print("\n🚀 GENERANDO DOCUMENTACIÓN COMPLETA DEL PROYECTO\n")

        # VERIFICAR que CHANGELOG y BITÁCORA existan
        verificacion = self.verificar_changelog_bitacora()
        print(verificacion["mensaje"])

        if not verificacion["ambos_existen"]:
            print("\n⚠️  Recomendación: Ejecuta version-manager primero para generar CHANGELOG y BITÁCORA.")
            print("   Esto asegura que la documentación incluya información completa.\n")

            respuesta = input("¿Continuar de todas formas? [s/n]: ").strip().lower()
            if respuesta != 's':
                return {
                    "total_documentos": 0,
                    "exitosos": 0,
                    "fallidos": 0,
                    "detalles": [],
                    "cancelado": True,
                    "mensaje": "Generación cancelada por el usuario"
                }

        print("\n" + "="*80 + "\n")

        resultados = {
            "total_documentos": 0,
            "exitosos": 0,
            "fallidos": 0,
            "detalles": [],
            "changelog_existe": verificacion["changelog_existe"],
            "bitacora_existe": verificacion["bitacora_existe"]
        }

        tipos_docs = list(self.prompts.keys())

        for tipo in tipos_docs:
            try:
                print(f"📝 Generando: {tipo.replace('_', ' ').title()}...")

                contexto = None
                if interactivo:
                    contexto = self.modo_interactivo(tipo)

                resultado = self.generar_documentacion(tipo, contexto)
                resultados["exitosos"] += 1
                resultados["detalles"].append({
                    "tipo": tipo,
                    "status": "exitoso",
                    "metadata": resultado["metadata"]
                })

                print(f"   ✅ Completado\n")

            except Exception as e:
                print(f"   ❌ Error: {str(e)}\n")
                resultados["fallidos"] += 1
                resultados["detalles"].append({
                    "tipo": tipo,
                    "status": "fallido",
                    "error": str(e)
                })

        resultados["total_documentos"] = len(tipos_docs)

        return resultados


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='GENERADOR DE DOCUMENTACIÓN - EVARISIS',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EJEMPLOS DE USO:

  # Ver estado de documentación actual
  python herramientas_ia/generador_documentacion.py --estado

  # Mostrar prompt completo para copiar a Claude/ChatGPT
  python herramientas_ia/generador_documentacion.py --mostrar-prompt informe-global

  # Generar con modo interactivo (pregunta contexto)
  python herramientas_ia/generador_documentacion.py --generar informe-global --interactivo

  # Generar sin interacción
  python herramientas_ia/generador_documentacion.py --generar analisis-tecnico --salida analisis_modular.md

  # Generar todos los tipos de documentación
  python herramientas_ia/generador_documentacion.py --completo

  # Validar documentación existente
  python herramientas_ia/generador_documentacion.py --validar

TIPOS DE DOCUMENTACIÓN DISPONIBLES:
  - informe-global       : Documento estratégico para stakeholders
  - analisis-tecnico     : Análisis técnico modular por componente
  - gestion              : CHANGELOG, README, bitácora
  - comunicacion         : Documentos diferenciados por audiencia
  - doc-tecnica          : Manuales técnicos especializados
  - versionado           : Sistema de versionado profesional

NOTAS:
  - Los prompts son adaptativos y preguntan automáticamente
  - Modo interactivo captura contexto del usuario
  - Puedes copiar el prompt completo para usar en Claude/ChatGPT directamente
        """
    )

    parser.add_argument("--estado", action="store_true",
                       help="Mostrar estado de documentación actual")

    parser.add_argument("--mostrar-prompt", metavar="TIPO",
                       choices=['informe-global', 'analisis-tecnico', 'gestion', 'comunicacion', 'doc-tecnica', 'versionado'],
                       help="Mostrar prompt completo para copiar a Claude/ChatGPT")

    parser.add_argument("--generar", metavar="TIPO",
                       choices=['informe-global', 'analisis-tecnico', 'gestion', 'comunicacion', 'doc-tecnica', 'versionado'],
                       help="Generar tipo específico de documentación")

    parser.add_argument("--interactivo", action="store_true",
                       help="Modo interactivo (pregunta contexto al usuario)")

    parser.add_argument("--salida", metavar="ARCHIVO",
                       help="Archivo de salida para documentación generada")

    parser.add_argument("--completo", action="store_true",
                       help="Generar todos los tipos de documentación")

    parser.add_argument("--validar", action="store_true",
                       help="Validar documentación existente")

    parser.add_argument("--json", metavar="ARCHIVO",
                       help="Exportar resultado a JSON")

    args = parser.parse_args()

    generador = GeneradorDocumentacion()

    # Mostrar estado
    if args.estado:
        version_info = generador.obtener_info_version()
        estructura = generador.analizar_estructura_proyecto()
        legacy = generador.detectar_documentacion_legacy()

        print("\n" + "="*80)
        print("📊 ESTADO DE DOCUMENTACIÓN DEL PROYECTO")
        print("="*80)
        print(f"\n📦 Versión: {version_info['version']} - {version_info['version_name']}")
        print(f"📅 Build: {version_info['build_date']}")
        print(f"\n📁 Estructura del Proyecto:")
        print(f"   - Archivos Python: {estructura['total_archivos']}")
        print(f"   - Líneas de código: {estructura['lineas_codigo']:,}")
        print(f"   - Directorios principales: {len(estructura['directorios'])}")
        print(f"\n📚 Legacy:")
        print(f"   - Documentación legacy: {'Sí' if legacy['existe_legacy'] else 'No'}")
        print(f"   - Documentos encontrados: {len(legacy['documentos_encontrados'])}")
        print(f"   - Versiones anteriores: {len(legacy['versiones_anteriores'])}")
        print("\n" + "="*80 + "\n")
        return

    # Mostrar prompt completo
    if args.mostrar_prompt:
        tipo_map = {
            'informe-global': 'informe_global',
            'analisis-tecnico': 'analisis_tecnico',
            'gestion': 'gestion',
            'comunicacion': 'comunicacion',
            'doc-tecnica': 'doc_tecnica',
            'versionado': 'versionado'
        }
        tipo = tipo_map[args.mostrar_prompt]
        generador.mostrar_prompt_completo(tipo)
        return

    # Generar documentación específica
    if args.generar:
        tipo_map = {
            'informe-global': 'informe_global',
            'analisis-tecnico': 'analisis_tecnico',
            'gestion': 'gestion',
            'comunicacion': 'comunicacion',
            'doc-tecnica': 'doc_tecnica',
            'versionado': 'versionado'
        }
        tipo = tipo_map[args.generar]

        contexto = None
        if args.interactivo:
            contexto = generador.modo_interactivo(tipo)

        resultado = generador.generar_documentacion(tipo, contexto, args.salida)

        print("\n" + "="*80)
        print(f"✅ DOCUMENTACIÓN GENERADA: {tipo.upper()}")
        print("="*80)
        print(f"\n📅 Fecha: {resultado['metadata']['fecha_generacion']}")
        print(f"📦 Versión: {resultado['metadata']['version_sistema']}")
        print(f"📁 Archivos analizados: {resultado['metadata']['archivos_analizados']}")

        if 'archivo_generado' in resultado:
            print(f"📄 Archivo generado: {resultado['archivo_generado']}")

        print("\n💡 Usa el prompt generado con Claude/ChatGPT para crear la documentación final")
        print("="*80 + "\n")

        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(resultado, f, indent=2, ensure_ascii=False)
            print(f"📄 Resultado exportado a {args.json}\n")

        return

    # Generar documentación completa
    if args.completo:
        resultados = generador.generar_documentacion_completa(args.interactivo)

        print("\n" + "="*80)
        print("📊 RESUMEN DE GENERACIÓN COMPLETA")
        print("="*80)
        print(f"\n✅ Exitosos: {resultados['exitosos']}/{resultados['total_documentos']}")
        print(f"❌ Fallidos: {resultados['fallidos']}/{resultados['total_documentos']}")

        if args.json:
            with open(args.json, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            print(f"\n📄 Resultados exportados a {args.json}")

        print("="*80 + "\n")
        return

    # Validar documentación
    if args.validar:
        # PASO 1: Verificar CHANGELOG y BITÁCORA (responsabilidad de version-manager)
        verificacion = generador.verificar_changelog_bitacora()

        print("\n" + "="*80)
        print("📋 VERIFICACIÓN DE CHANGELOG Y BITÁCORA")
        print("="*80 + "\n")
        print(verificacion["mensaje"])

        # PASO 2: Validar documentación general
        validacion = generador.validar_documentacion_existente()

        print("\n" + "="*80)
        print("🔍 VALIDACIÓN DE DOCUMENTACIÓN")
        print("="*80)
        print(f"\n📊 Completitud: {validacion['completitud']:.1f}%")
        print(f"\n✅ Archivos encontrados ({len(validacion['archivos_encontrados'])}):")
        for doc in validacion['archivos_encontrados']:
            print(f"   - {doc}")

        if validacion['archivos_faltantes']:
            print(f"\n❌ Archivos faltantes ({len(validacion['archivos_faltantes'])}):")
            for doc in validacion['archivos_faltantes']:
                print(f"   - {doc}")

        print("\n" + "="*80 + "\n")
        return

    # Si no se especificó ninguna acción, mostrar ayuda
    parser.print_help()


if __name__ == "__main__":
    main()
