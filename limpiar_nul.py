#!/usr/bin/env python3
"""
Script para Eliminar Archivos 'nul' del Proyecto
Creado: 2025-11-14
Descripción: Busca y elimina todos los archivos llamados 'nul'
             en el proyecto (excepto en venv0)

Uso: python limpiar_nul.py
"""

import os
import pathlib
from datetime import datetime


def limpiar_archivos_nul(proyecto_root='.', dry_run=False):
    """
    Busca y elimina archivos llamados 'nul' en el proyecto

    Args:
        proyecto_root: Directorio raíz del proyecto
        dry_run: Si es True, solo muestra los archivos sin eliminarlos
    """
    print()
    print("=" * 60)
    print("   LIMPIEZA DE ARCHIVOS 'NUL'")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Modo: {'SIMULACIÓN (no se eliminará nada)' if dry_run else 'ELIMINACIÓN'}")
    print("=" * 60)
    print()

    project_root = pathlib.Path(proyecto_root).resolve()
    print(f"Buscando archivos 'nul' en: {project_root}")
    print()

    # Buscar archivos 'nul' usando pathlib.rglob (evita problemas con os.walk y 'nul')
    nul_files = []

    # Lista de subdirectorios conocidos donde pueden estar archivos 'nul'
    search_paths = [
        project_root,
        project_root / 'data' / 'debug_maps',
        project_root / 'backups',
        project_root / 'herramientas_ia' / 'resultados',
    ]

    for search_path in search_paths:
        if not search_path.exists():
            continue

        # Buscar archivos 'nul' directamente
        nul_path = search_path / 'nul'

        # En Windows, 'nul' es un nombre reservado, usar ruta UNC para verificar existencia
        unc_path = f"\\\\?\\{nul_path.absolute()}"
        try:
            if os.path.exists(unc_path) and os.path.isfile(unc_path):
                # Verificar que no esté en venv0
                if 'venv0' not in str(nul_path):
                    nul_files.append(nul_path)
        except:
            # Fallback: intentar sin UNC
            try:
                if nul_path.exists() and nul_path.is_file():
                    if 'venv0' not in str(nul_path):
                        nul_files.append(nul_path)
            except:
                pass

        # También buscar recursivamente en subdirectorios
        try:
            for subdir in search_path.iterdir():
                if subdir.is_dir() and 'venv0' not in str(subdir):
                    nul_in_subdir = subdir / 'nul'
                    unc_subdir = f"\\\\?\\{nul_in_subdir.absolute()}"

                    try:
                        if os.path.exists(unc_subdir) and os.path.isfile(unc_subdir):
                            nul_files.append(nul_in_subdir)
                    except:
                        try:
                            if nul_in_subdir.exists() and nul_in_subdir.is_file():
                                nul_files.append(nul_in_subdir)
                        except:
                            pass
        except (PermissionError, OSError):
            pass

    print(f"Total de archivos 'nul' encontrados: {len(nul_files)}")
    print()

    if not nul_files:
        print("[OK] No se encontraron archivos 'nul' en el proyecto")
        return 0

    # Mostrar archivos encontrados
    print("Archivos encontrados:")
    print("-" * 60)
    for i, file_path in enumerate(nul_files, 1):
        rel_path = file_path.relative_to(project_root)
        size = file_path.stat().st_size
        print(f"{i}. {rel_path} ({size} bytes)")
    print("-" * 60)
    print()

    # Eliminar archivos
    eliminados = 0
    errores = 0

    if not dry_run:
        print("Eliminando archivos...")
        print()

        for file_path in nul_files:
            rel_path = file_path.relative_to(project_root)
            try:
                # Leer contenido antes de eliminar (para log)
                try:
                    with open(file_path, 'r') as f:
                        contenido = f.read().strip()
                    if contenido:
                        print(f"[INFO] Contenido de {rel_path}: {contenido[:50]}...")
                except:
                    pass

                # Eliminar archivo usando ruta UNC para evitar problemas con 'nul'
                # En Windows, el prefijo \\?\ permite acceder a archivos con nombres reservados
                unc_path = f"\\\\?\\{file_path.absolute()}"
                try:
                    os.remove(unc_path)
                except:
                    # Fallback: intentar sin UNC
                    file_path.unlink()

                # Verificar que se eliminó
                if not file_path.exists():
                    print(f"[OK] [ELIMINADO] {rel_path}")
                    eliminados += 1
                else:
                    print(f"[ERROR] No se pudo verificar eliminacion: {rel_path}")
                    errores += 1

            except Exception as e:
                print(f"[ERROR] {rel_path}: {str(e)}")
                errores += 1

            print()
    else:
        print("[ADVERTENCIA] MODO SIMULACION: Los archivos NO seran eliminados")
        print()

    # Resumen
    print("=" * 60)
    print("   RESULTADO")
    print("=" * 60)
    if not dry_run:
        print(f"[OK] Archivos eliminados exitosamente: {eliminados}")
        if errores > 0:
            print(f"[ERROR] Errores: {errores}")
    else:
        print(f"[INFO] Archivos que se eliminarian: {len(nul_files)}")
    print("=" * 60)
    print()

    return eliminados


if __name__ == "__main__":
    import sys

    # Verificar si se pasa --dry-run como argumento
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv

    if dry_run:
        print("[ADVERTENCIA] Ejecutando en modo SIMULACION (--dry-run)")
        print("              Para eliminar archivos, ejecute sin parametros")
        print()

    try:
        eliminados = limpiar_archivos_nul(dry_run=dry_run)

        if not dry_run and eliminados > 0:
            print("[OK] Limpieza completada exitosamente")

    except KeyboardInterrupt:
        print()
        print("[ADVERTENCIA] Operacion cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print()
        print(f"[ERROR] {str(e)}")
        sys.exit(1)

    # Pausa para ver resultados
    if os.name == 'nt':  # Windows
        input("\nPresione Enter para continuar...")
