#!/usr/bin/env python3
"""
Script para crear el ejecutable de la aplicación (Windows/macOS/Linux) usando PyInstaller.

Notas:
- Evita caracteres no ASCII en consola Windows (cp1252) para no romper la salida.
- Si PyInstaller no está instalado, el script lo instalará automáticamente.
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse


def _info(msg: str):
    print(f"[INFO] {msg}")


def _ok(msg: str):
    print(f"[ OK ] {msg}")


def _err(msg: str):
    print(f"[ERR ] {msg}")


def run_command(command: str, description: str) -> bool:
    """Ejecuta un comando de shell y muestra salida compacta."""
    _info(f"{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            _ok(f"{description} - completado")
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        else:
            _err(f"{description} - falló")
            if result.stderr.strip():
                print(result.stderr.strip())
            return False
    except Exception as e:
        _err(f"{description} - excepción: {e}")
        return False


def check_dependencies() -> bool:
    """Verifica que PyInstaller esté disponible; si no, lo instala."""
    _info("Verificando PyInstaller")
    try:
        import PyInstaller  # noqa: F401
        _ok("PyInstaller disponible")
        return True
    except ImportError:
        _info("Instalando PyInstaller")
        return run_command(f"{sys.executable} -m pip install --upgrade pip pyinstaller", "Instalación de PyInstaller")


def build_executable(main_script: str) -> bool:
    """Construye el ejecutable con parámetros recomendados."""
    if not os.path.exists(main_script):
        _err(f"No se encuentra {main_script}")
        return False
    
    # Determinar nombre del ejecutable basado en el script
    if main_script == "ui.py":
        exe_name = "Gestiononcologia"
    else:
        exe_name = "OCR_Medico"

    # PyInstaller con dependencias específicas para el sistema de gestión oncológica
    command = " ".join([
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--name={exe_name}",
        "--clean",
        "--hidden-import=ttkbootstrap",
        "--hidden-import=matplotlib",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=sqlite3",
        "--hidden-import=PIL",
        "--hidden-import=requests",
        "--hidden-import=selenium",
        "--hidden-import=pytesseract",
        "--add-data=version_info.py;.",
        "--add-data=huv_constants.py;.",
        main_script,
    ])

    _info("Construyendo ejecutable")
    _info(f"Comando: {command}")
    return run_command(command, "PyInstaller build")


def main() -> int:
    parser = argparse.ArgumentParser(description="Constructor de ejecutable (PyInstaller)")
    parser.add_argument(
        "script",
        nargs="?",
        default="ui.py",
        help="Script principal de la aplicación",
    )
    args = parser.parse_args()

    script_name = args.script
    app_title = "Gestión Oncológica HUV" if script_name == "ui.py" else "OCR Medico"
    
    print("=" * 60)
    print(f"Constructor de Ejecutable - {app_title}")
    print("=" * 60)

    if not check_dependencies():
        _err("No fue posible preparar PyInstaller")
        return 1

    if not build_executable(args.script):
        _err("Error al construir ejecutable")
        return 1

    dist_dir = Path("dist")
    if dist_dir.exists():
        # Buscar tanto OCR_Medico como Gestiononcologia
        executables = list(dist_dir.glob("OCR_Medico*")) + list(dist_dir.glob("Gestiononcologia*"))
        if executables:
            exe_path = executables[0]
            exe_size = exe_path.stat().st_size / (1024 * 1024)
            print("-" * 60)
            _ok("Ejecutable creado exitosamente")
            print(f"Ubicación: {exe_path}")
            print(f"Tamaño: {exe_size:.1f} MB")
            
            if "Gestiononcologia" in str(exe_path):
                print("Notas para Gestión Oncológica:")
                print("  - Sistema completo de gestión médica")
                print("  - Incluye procesamiento OCR y análisis IHQ")
                print("  - Compatible con base de datos SQLite")
            else:
                print("Notas para OCR Medico:")
                print("  - Requiere Tesseract OCR instalado en el sistema")
                print("  - Chrome debe estar instalado para funciones Selenium")
            return 0
        else:
            _err("No se encontró el ejecutable en dist/")
            return 1
    else:
        _err("Carpeta dist/ no creada")
        return 1


if __name__ == "__main__":
    sys.exit(main())
