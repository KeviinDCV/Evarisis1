#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VALIDADOR AUTOMÁTICO - Sistema de Versionado Obligatorio
Verifica que el sistema de versionado esté correctamente implementado
"""

import os
import sys
import importlib.util
import inspect
from pathlib import Path

class VersionSystemValidator:
    def __init__(self, project_path):
        self.project_path = Path(project_path)
        self.errors = []
        self.warnings = []
        self.passed = []
        
    def validate_all(self):
        """Ejecuta todas las validaciones"""
        print("🔍 VALIDADOR DE SISTEMA DE VERSIONADO OBLIGATORIO")
        print("=" * 60)
        
        # Validaciones obligatorias
        self._validate_version_info_module()
        self._validate_version_info_content()
        self._validate_team_info()
        self._validate_system_detection()
        self._validate_dependencies_detection()
        self._validate_documentation()
        self._validate_ui_integration()
        
        # Mostrar resultados
        self._show_results()
        
        return len(self.errors) == 0
    
    def _validate_version_info_module(self):
        """Validar que existe el módulo version_info.py"""
        version_info_path = self.project_path / "version_info.py"
        
        if not version_info_path.exists():
            self.errors.append("❌ CRÍTICO: Archivo version_info.py no encontrado")
            return False
        
        try:
            spec = importlib.util.spec_from_file_location("version_info", version_info_path)
            version_info = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(version_info)
            self.version_info = version_info
            self.passed.append("✅ Módulo version_info.py encontrado y cargado")
            return True
        except Exception as e:
            self.errors.append(f"❌ CRÍTICO: Error al cargar version_info.py: {str(e)}")
            return False
    
    def _validate_version_info_content(self):
        """Validar contenido del módulo version_info"""
        if not hasattr(self, 'version_info'):
            return
        
        required_constants = [
            'VERSION_INFO', 'PROJECT_INFO', 'TEAM_INFO', 
            'DEPENDENCIES', 'FEATURES', 'ROADMAP'
        ]
        
        for constant in required_constants:
            if hasattr(self.version_info, constant):
                self.passed.append(f"✅ Constante {constant} encontrada")
            else:
                self.errors.append(f"❌ CRÍTICO: Constante {constant} no encontrada")
        
        # Validar VERSION_INFO específico
        if hasattr(self.version_info, 'VERSION_INFO'):
            version_info = self.version_info.VERSION_INFO
            required_fields = ['version', 'version_name', 'build_date', 'build_number']
            
            for field in required_fields:
                if field in version_info and version_info[field] != f"[{field.upper()}]":
                    self.passed.append(f"✅ Campo VERSION_INFO.{field} configurado")
                else:
                    self.errors.append(f"❌ Campo VERSION_INFO.{field} no configurado (contiene placeholder)")
    
    def _validate_team_info(self):
        """Validar información del equipo"""
        if not hasattr(self, 'version_info') or not hasattr(self.version_info, 'TEAM_INFO'):
            return
        
        team_info = self.version_info.TEAM_INFO
        min_team_members = 2  # Mínimo desarrollador + supervisor
        
        if len(team_info) >= min_team_members:
            self.passed.append(f"✅ Equipo de desarrollo: {len(team_info)} miembros configurados")
        else:
            self.errors.append(f"❌ CRÍTICO: Solo {len(team_info)} miembros del equipo, mínimo {min_team_members}")
        
        # Validar que no contengan placeholders
        for role, info in team_info.items():
            if isinstance(info, dict):
                placeholder_count = sum(1 for v in info.values() if isinstance(v, str) and v.startswith('[') and v.endswith(']'))
                if placeholder_count == 0:
                    self.passed.append(f"✅ Información de {role} configurada completamente")
                else:
                    self.warnings.append(f"⚠️ {role} tiene {placeholder_count} campos sin configurar")
    
    def _validate_system_detection(self):
        """Validar detección del sistema"""
        if not hasattr(self, 'version_info'):
            return
        
        required_functions = ['get_system_info', 'get_full_version_info']
        
        for func_name in required_functions:
            if hasattr(self.version_info, func_name):
                try:
                    func = getattr(self.version_info, func_name)
                    result = func()  # Ejecutar función
                    if isinstance(result, dict) and result:
                        self.passed.append(f"✅ Función {func_name}() funciona correctamente")
                    else:
                        self.warnings.append(f"⚠️ Función {func_name}() retorna resultado vacío")
                except Exception as e:
                    self.errors.append(f"❌ Error en función {func_name}(): {str(e)}")
            else:
                self.errors.append(f"❌ CRÍTICO: Función {func_name}() no encontrada")
        
        # Verificar detección de psutil
        try:
            system_info = self.version_info.get_system_info()
            if 'memoria_total' in system_info and not system_info['memoria_total'].startswith('No disponible'):
                self.passed.append("✅ Detección avanzada del sistema (psutil) funcionando")
            else:
                self.warnings.append("⚠️ psutil no disponible - información limitada del sistema")
        except:
            pass
    
    def _validate_dependencies_detection(self):
        """Validar detección de dependencias"""
        if not hasattr(self, 'version_info') or not hasattr(self.version_info, 'get_dependencies_actual'):
            return
        
        try:
            deps = self.version_info.get_dependencies_actual()
            if isinstance(deps, dict) and deps:
                self.passed.append(f"✅ Detección de dependencias: {len(deps)} paquetes")
                
                # Verificar iconos de estado
                status_icons = ['✅', '❌', '⚠️']
                has_status_icons = any(any(icon in str(status) for icon in status_icons) 
                                     for status in deps.values())
                
                if has_status_icons:
                    self.passed.append("✅ Estados de dependencias con iconos implementados")
                else:
                    self.warnings.append("⚠️ Estados de dependencias sin iconos claros")
            else:
                self.errors.append("❌ get_dependencies_actual() no retorna datos válidos")
        except Exception as e:
            self.errors.append(f"❌ Error en detección de dependencias: {str(e)}")
    
    def _validate_documentation(self):
        """Validar documentación requerida"""
        required_docs = [
            ("VERSION_INFO_GUIDE.md", "Guía de información de versión"),
            ("CHANGELOG.md", "Registro de cambios"),
            ("README.md", "Documentación principal")
        ]
        
        for doc_file, description in required_docs:
            doc_path = self.project_path / doc_file
            if doc_path.exists():
                # Verificar que contiene referencias al sistema de versión
                try:
                    content = doc_path.read_text(encoding='utf-8')
                    version_keywords = ['versión', 'version', 'acerca de', 'about', 'sistema']
                    
                    if any(keyword.lower() in content.lower() for keyword in version_keywords):
                        self.passed.append(f"✅ {doc_file} existe y menciona sistema de versión")
                    else:
                        self.warnings.append(f"⚠️ {doc_file} existe pero no menciona sistema de versión")
                except:
                    self.warnings.append(f"⚠️ {doc_file} existe pero no se pudo leer")
            else:
                if doc_file == "VERSION_INFO_GUIDE.md":
                    self.errors.append(f"❌ CRÍTICO: {doc_file} requerido no encontrado")
                else:
                    self.warnings.append(f"⚠️ {doc_file} recomendado no encontrado")
    
    def _validate_ui_integration(self):
        """Validar integración en UI (si existe)"""
        ui_files = list(self.project_path.glob("*ui*.py")) + list(self.project_path.glob("*main*.py")) + list(self.project_path.glob("*app*.py"))
        
        if not ui_files:
            self.warnings.append("⚠️ No se encontraron archivos de UI para validar integración")
            return
        
        for ui_file in ui_files:
            try:
                content = ui_file.read_text(encoding='utf-8')
                
                # Buscar indicadores de integración
                integration_indicators = [
                    '_show_version_info',
                    'version_info',
                    'acerca de',
                    'about',
                    'Toplevel',
                    'Notebook'
                ]
                
                found_indicators = [indicator for indicator in integration_indicators 
                                  if indicator.lower() in content.lower()]
                
                if found_indicators:
                    self.passed.append(f"✅ {ui_file.name}: Integración UI detectada ({len(found_indicators)} indicadores)")
                else:
                    self.warnings.append(f"⚠️ {ui_file.name}: No se detecta integración del sistema de versión")
                    
            except Exception as e:
                self.warnings.append(f"⚠️ Error al analizar {ui_file.name}: {str(e)}")
    
    def _show_results(self):
        """Mostrar resultados de la validación"""
        print("\n" + "=" * 60)
        print("📊 RESULTADOS DE VALIDACIÓN")
        print("=" * 60)
        
        if self.passed:
            print(f"\n✅ APROBADO ({len(self.passed)} elementos):")
            for item in self.passed:
                print(f"  {item}")
        
        if self.warnings:
            print(f"\n⚠️ ADVERTENCIAS ({len(self.warnings)} elementos):")
            for item in self.warnings:
                print(f"  {item}")
        
        if self.errors:
            print(f"\n❌ ERRORES CRÍTICOS ({len(self.errors)} elementos):")
            for item in self.errors:
                print(f"  {item}")
        
        print("\n" + "=" * 60)
        
        if len(self.errors) == 0:
            if len(self.warnings) == 0:
                print("🎉 ¡VALIDACIÓN PERFECTA! Sistema de versionado completamente implementado.")
            else:
                print("✅ ¡VALIDACIÓN APROBADA! Sistema implementado con advertencias menores.")
        else:
            print("❌ VALIDACIÓN FALLIDA. Corrija los errores críticos antes de continuar.")
        
        print("=" * 60)
        
        # Puntuación
        total_checks = len(self.passed) + len(self.warnings) + len(self.errors)
        score = (len(self.passed) + (len(self.warnings) * 0.5)) / total_checks * 100 if total_checks > 0 else 0
        print(f"📊 PUNTUACIÓN: {score:.1f}% ({len(self.passed)} ✅, {len(self.warnings)} ⚠️, {len(self.errors)} ❌)")

def main():
    """Función principal"""
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = os.getcwd()
    
    print(f"🔍 Validando proyecto en: {project_path}")
    
    validator = VersionSystemValidator(project_path)
    success = validator.validate_all()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())