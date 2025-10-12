#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validador de Instrucciones de GitHub Copilot
==============================================

Verifica que las instrucciones de Copilot estén sincronizadas con las guías del proyecto.

Autor: EVARISIS Team
Fecha: 4 de octubre de 2025
Versión: 1.0.0
"""

import os
import sys
from pathlib import Path

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Imprime un encabezado formateado"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(text):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def check_file_exists(filepath, description):
    """Verifica que un archivo exista"""
    if filepath.exists():
        print_success(f"{description}: {filepath.name}")
        return True
    else:
        print_error(f"{description} NO ENCONTRADO: {filepath}")
        return False

def get_file_version(filepath):
    """Extrae la versión de un archivo MD"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read(500)  # Leer primeras líneas
            if '4.2.1' in content:
                return '4.2.1'
            elif 'v4.2' in content:
                return '4.2.x'
            else:
                return 'desconocida'
    except Exception as e:
        return f'error: {e}'

def main():
    """Función principal"""
    print_header("VALIDADOR DE INSTRUCCIONES GITHUB COPILOT")
    
    # Obtener directorio raíz del proyecto
    project_root = Path(__file__).parent.parent
    print_info(f"Directorio del proyecto: {project_root}")
    
    # Archivos a verificar
    files_to_check = {
        'copilot_github': project_root / '.github' / 'copilot-instructions.md',
        'copilot_root': project_root / '.copilot-instructions.md',
        'reglas_estrictas': project_root / 'herramientas_ia' / 'REGLAS_ESTRICTAS_IA.md',
        'guia_comportamiento': project_root / 'herramientas_ia' / 'GUIA_COMPORTAMIENTO_IA.md',
        'guia_tecnica': project_root / 'herramientas_ia' / 'GUIA_TECNICA_COMPLETA.md',
        'readme_herramientas': project_root / 'herramientas_ia' / 'README.md',
    }
    
    print("\n📁 VERIFICANDO ARCHIVOS DE CONFIGURACIÓN\n")
    
    all_exist = True
    versions = {}
    
    for key, filepath in files_to_check.items():
        exists = check_file_exists(filepath, key.replace('_', ' ').title())
        all_exist = all_exist and exists
        
        if exists:
            versions[key] = get_file_version(filepath)
    
    # Verificar versiones
    print("\n📊 VERSIONES DETECTADAS\n")
    for key, version in versions.items():
        print(f"  • {key.replace('_', ' ').title()}: {version}")
    
    # Validar sincronización
    print("\n🔄 VALIDANDO SINCRONIZACIÓN\n")
    
    if all_exist:
        print_success("Todos los archivos existen")
        
        # Verificar que copilot-instructions.md esté en ambas ubicaciones
        if files_to_check['copilot_github'].exists() and files_to_check['copilot_root'].exists():
            print_success("copilot-instructions.md existe en .github/ y en raíz")
            
            # Comparar tamaños
            size_github = files_to_check['copilot_github'].stat().st_size
            size_root = files_to_check['copilot_root'].stat().st_size
            
            if size_github == size_root:
                print_success(f"Tamaños coinciden: {size_github} bytes")
            else:
                print_warning(f"Tamaños difieren: .github={size_github}, raíz={size_root}")
                print_info("Puede que necesites sincronizar los archivos")
        
        # Verificar versiones consistentes
        expected_version = '4.2.1'
        version_ok = all(v == expected_version or expected_version in v for v in versions.values() if 'error' not in v)
        
        if version_ok:
            print_success(f"Todas las guías están en versión {expected_version}")
        else:
            print_warning("Las versiones de los archivos pueden no estar sincronizadas")
            print_info("Verifica que todos los archivos estén actualizados")
        
        print("\n" + "="*70)
        print(f"{Colors.GREEN}{Colors.BOLD}✓ VALIDACIÓN COMPLETADA EXITOSAMENTE{Colors.RESET}")
        print("="*70 + "\n")
        
        return 0
    else:
        print("\n" + "="*70)
        print(f"{Colors.RED}{Colors.BOLD}✗ VALIDACIÓN FALLIDA - Archivos faltantes{Colors.RESET}")
        print("="*70 + "\n")
        return 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validación cancelada por el usuario{Colors.RESET}\n")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error inesperado: {e}{Colors.RESET}\n")
        sys.exit(1)
