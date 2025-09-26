#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo de la funcionalidad de información de versión
Este script demuestra la nueva funcionalidad de versión integrada
"""

import tkinter as tk
from version_info import get_version_string, get_build_info, get_full_version_info

def demo_version_info():
    """Demostración de la información de versión"""
    print("=" * 60)
    print("DEMO: Información de Versión - EVARISIS Gestor H.U.V")
    print("=" * 60)
    
    # Información básica
    print(f"\n🚀 VERSIÓN ACTUAL:")
    print(f"   Versión: {get_version_string()}")
    print(f"   Build: {get_build_info()}")
    
    # Información completa
    full_info = get_full_version_info()
    
    print(f"\n📋 INFORMACIÓN DEL PROYECTO:")
    print(f"   Nombre: {full_info['project']['name']}")
    print(f"   Organización: {full_info['project']['organization']}")
    print(f"   Descripción: {full_info['project']['description']}")
    print(f"   Repositorio: {full_info['project']['repository']}")
    
    print(f"\n💻 INFORMACIÓN DEL SISTEMA:")
    print(f"   Python: {full_info['system']['python_version'].split()[0]}")
    print(f"   Plataforma: {full_info['system']['platform']}")
    print(f"   Arquitectura: {full_info['system']['architecture']}")
    
    print(f"\n✨ CARACTERÍSTICAS PRINCIPALES:")
    for i, feature in enumerate(full_info['features'][:5], 1):
        print(f"   {i}. {feature}")
    
    print(f"\n📊 MÉTRICAS DE RENDIMIENTO:")
    for metric, value in list(full_info['performance'].items())[:3]:
        metric_name = metric.replace('_', ' ').title()
        print(f"   • {metric_name}: {value}")
    
    print(f"\n🗺️ PRÓXIMAS VERSIONES:")
    for version, description in list(full_info['roadmap'].items())[:2]:
        print(f"   • {version}: {description}")
    
    print(f"\n💡 INTEGRACIÓN EN LA UI:")
    print("   ✅ Botón 'ℹ️ Acerca de' en el menú flotante")
    print("   ✅ Botón de versión rápida en el header (ej: v3.2)")
    print("   ✅ Ventana modal completa con 5 tabs:")
    print("      - 📋 General: Info del proyecto y versión")
    print("      - 💻 Sistema: Información técnica del entorno")
    print("      - 📦 Dependencias: Estado de todas las librerías")
    print("      - ✨ Características: Features y métricas de rendimiento")
    print("      - 🗺️ Roadmap: Próximas versiones planificadas")
    print("   ✅ Función copiar al portapapeles para soporte técnico")
    
    print(f"\n🎯 CASOS DE USO:")
    print("   • Soporte técnico: Info rápida del sistema")
    print("   • Troubleshooting: Verificar dependencias")
    print("   • Documentación: Referencia de características")
    print("   • Gestión: Seguimiento de roadmap y versiones")
    
    print("\n" + "=" * 60)
    print("Para probar en la UI, ejecutar:")
    print("python ui.py --tema=litera --nombre='Test Usuario' --cargo='Testing'")
    print("Luego hacer clic en el botón 'v3.2' del header o 'ℹ️ Acerca de' del menú")
    print("=" * 60)

if __name__ == "__main__":
    demo_version_info()