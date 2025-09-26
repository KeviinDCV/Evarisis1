#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EVARISIS Gestor HUV - Test de Versión Mejorada
Prueba las mejoras al sistema de información de versión
"""

import sys
import os

# Asegurar que podemos importar los módulos del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("EVARISIS Gestor H.U.V - Test de Información de Versión Mejorada")
    print("=" * 60)
    
    try:
        # Intentar instalar psutil si no está disponible
        try:
            import psutil
            print("✅ psutil ya está instalado")
        except ImportError:
            print("❌ psutil no encontrado, intentando instalar...")
            import subprocess
            import sys
            
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "psutil"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ psutil instalado exitosamente")
                import psutil
            else:
                print("⚠️ No se pudo instalar psutil automáticamente")
                print("   Ejecute manualmente: pip install psutil")
        
        # Importar módulos locales
        from version_info import get_full_version_info, get_version_string, get_build_info, get_dependencies_actual
        
        print(f"\n🚀 VERSIÓN: {get_version_string()}")
        print(f"🏗️ BUILD: {get_build_info()}")
        
        # Obtener información completa
        version_info = get_full_version_info()
        actual_deps = get_dependencies_actual()
        
        print("\n" + "=" * 60)
        print("💻 INFORMACIÓN DEL SISTEMA")
        print("=" * 60)
        
        system_info = version_info['system']
        print(f"Python: {system_info['python_version'].split()[0]}")
        print(f"Plataforma: {system_info['platform']}")
        print(f"Sistema: {system_info.get('system', 'No disponible')}")
        print(f"Arquitectura: {system_info['architecture']}")
        print(f"Procesador: {system_info['processor']}")
        
        # Información avanzada si está disponible
        if 'memoria_total' in system_info:
            print(f"\n🧠 MEMORIA:")
            print(f"  Total: {system_info['memoria_total']}")
            print(f"  Disponible: {system_info['memoria_disponible']}")
            print(f"  Usada: {system_info['memoria_usada']} ({system_info['memoria_porcentaje']})")
        
        if 'cpu_cores' in system_info:
            print(f"\n⚡ PROCESADOR:")
            print(f"  Núcleos físicos: {system_info['cpu_cores']}")
            print(f"  Hilos lógicos: {system_info['cpu_threads']}")
            print(f"  Frecuencia máxima: {system_info['cpu_frecuencia']}")
        
        if 'tarjeta_grafica' in system_info:
            print(f"\n🎮 TARJETA GRÁFICA:")
            gpus = system_info['tarjeta_grafica']
            if isinstance(gpus, list):
                for i, gpu in enumerate(gpus):
                    print(f"  GPU {i+1}: {gpu}")
            else:
                print(f"  GPU: {gpus}")
        
        if 'placa_madre' in system_info:
            print(f"\n🔧 PLACA MADRE: {system_info['placa_madre']}")
        
        if 'discos' in system_info and isinstance(system_info['discos'], list):
            print(f"\n💾 DISCOS:")
            for i, disco in enumerate(system_info['discos']):
                if isinstance(disco, dict):
                    print(f"  Disco {i+1}: {disco.get('dispositivo', 'N/A')}")
                    print(f"    Tamaño: {disco.get('total', 'N/A')} "
                          f"(Usado: {disco.get('porcentaje', 'N/A')})")
                    print(f"    Libre: {disco.get('libre', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("👥 EQUIPO DE DESARROLLO")
        print("=" * 60)
        
        team_info = version_info['team']
        for role_key, role_data in team_info.items():
            print(f"\n{role_data['cargo']}:")
            print(f"  👤 {role_data['nombre']}")
            print(f"  🏢 {role_data['departamento']}")
            print(f"  📧 {role_data['contacto']}")
        
        print("\n" + "=" * 60)
        print("📦 DEPENDENCIAS")
        print("=" * 60)
        
        for package, expected_version in version_info['dependencies'].items():
            actual_version = actual_deps.get(package, "❌ No instalado")
            status_icon = "✅" if not actual_version.startswith(("❌", "⚠️")) else actual_version[0]
            print(f"{status_icon} {package:15} | Esperado: {expected_version:10} | Actual: {actual_version}")
        
        print("\n" + "=" * 60)
        print("✨ CARACTERÍSTICAS PRINCIPALES")
        print("=" * 60)
        
        for feature in version_info['features'][:5]:  # Mostrar solo las primeras 5
            print(f"  {feature}")
        
        print(f"\n... y {len(version_info['features']) - 5} características más.")
        
        print("\n" + "=" * 60)
        print("🚀 PRÓXIMAS VERSIONES")
        print("=" * 60)
        
        for version, description in version_info['roadmap'].items():
            print(f"{version}: {description}")
        
        print("\n✅ Test completado exitosamente")
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())