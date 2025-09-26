#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST FINAL - Verificación de Actualizaciones v3.2.1
Valida todas las correcciones implementadas
"""

def test_actualizaciones_v321():
    """Test completo de las actualizaciones implementadas"""
    print("🔍 TESTING - Actualizaciones v3.2.1")
    print("=" * 60)
    
    try:
        from version_info import get_full_version_info, TEAM_INFO, PROJECT_INFO
        
        # 1. Verificar información del equipo actualizada
        print("\n✅ 1. VERIFICANDO INFORMACIÓN DEL EQUIPO:")
        print("-" * 40)
        
        expected_roles = ['desarrollador', 'lider_investigacion', 'jefe_gestion_informacion']
        for role in expected_roles:
            if role in TEAM_INFO:
                info = TEAM_INFO[role]
                print(f"✅ {role}:")
                print(f"   Nombre: {info['nombre']}")
                print(f"   Cargo: {info['cargo']}")
                print(f"   Departamento: {info['departamento']}")
                print(f"   Correo: {info['correo']}")
            else:
                print(f"❌ {role} NO encontrado")
                return False
        
        # 2. Verificar que no hay información de repositorio
        print("\n✅ 2. VERIFICANDO ELIMINACIÓN DE REPOSITORIO:")
        print("-" * 40)
        
        if 'repository' not in PROJECT_INFO:
            print("✅ Información del repositorio eliminada correctamente")
        else:
            print("❌ Información del repositorio aún presente")
            return False
        
        # 3. Verificar estructura de campos
        print("\n✅ 3. VERIFICANDO ESTRUCTURA DE CAMPOS:")
        print("-" * 40)
        
        for role_key, role_info in TEAM_INFO.items():
            if 'correo' in role_info and 'contacto' not in role_info:
                print(f"✅ {role_key}: Campo 'correo' presente, 'contacto' eliminado")
            else:
                print(f"❌ {role_key}: Estructura de campos incorrecta")
                return False
        
        # 4. Verificar información específica solicitada
        print("\n✅ 4. VERIFICANDO INFORMACIÓN ESPECÍFICA:")
        print("-" * 40)
        
        # Desarrollador
        dev_info = TEAM_INFO['desarrollador']
        if (dev_info['departamento'] == 'Innovación y Desarrollo' and
            dev_info['correo'] == 'Pendiente'):
            print("✅ Desarrollador: Información actualizada correctamente")
        else:
            print("❌ Desarrollador: Información no actualizada")
            return False
        
        # Líder de investigación  
        lider_info = TEAM_INFO['lider_investigacion']
        if (lider_info['cargo'] == 'Coordinador del Área Cirugía Oncológica' and
            lider_info['departamento'] == 'Servicio de Oncología' and
            lider_info['correo'] == 'Pendiente'):
            print("✅ Líder de investigación: Información actualizada correctamente")
        else:
            print("❌ Líder de investigación: Información no actualizada")
            return False
        
        # Jefe gestión información
        jefe_info = TEAM_INFO['jefe_gestion_informacion']  
        if (jefe_info['departamento'] == 'Gestión de la Información' and
            jefe_info['correo'] == 'Pendiente'):
            print("✅ Jefe gestión información: Información actualizada correctamente")
        else:
            print("❌ Jefe gestión información: Información no actualizada")
            return False
        
        # 5. Test de integración UI
        print("\n✅ 5. VERIFICANDO INTEGRACIÓN UI:")
        print("-" * 40)
        
        with open('ui.py', 'r', encoding='utf-8') as f:
            ui_content = f.read()
        
        if 'role_info[\'correo\']' in ui_content and 'role_info[\'contacto\']' not in ui_content:
            print("✅ UI: Referencias actualizadas a 'correo'")
        else:
            print("❌ UI: Referencias no actualizadas correctamente")
            return False
        
        if 'role_titles' in ui_content:
            print("✅ UI: Títulos de roles implementados")
        else:
            print("❌ UI: Títulos de roles no implementados")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON - Actualizaciones v3.2.1 completas")
        print("=" * 60)
        
        # Resumen final
        print("\n📊 RESUMEN DE ACTUALIZACIONES:")
        print("✅ Información del equipo actualizada")
        print("✅ Repositorio eliminado")
        print("✅ Campos contacto → correo")
        print("✅ Departamentos actualizados")
        print("✅ Correos marcados como 'Pendiente'")
        print("✅ UI sincronizada correctamente")
        print("✅ Títulos con iconos implementados")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = test_actualizaciones_v321()
    sys.exit(0 if success else 1)