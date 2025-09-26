#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test de corrección del error _show_welcome_screen
Verifica que el método nav_to_welcome funcione correctamente
"""

import sys
import os

def test_navigation_fix():
    """Test para verificar la corrección del error de navegación"""
    print("🔍 TESTING - Corrección de error _show_welcome_screen")
    print("=" * 60)
    
    try:
        # Importar el módulo UI
        import ui
        print("✅ Módulo ui.py importado correctamente")
        
        # Verificar que la clase HUVUI se puede instanciar
        app = ui.HUVUI
        print("✅ Clase HUVUI accesible")
        
        # Verificar que los métodos existen
        methods_to_check = [
            'show_welcome_screen',
            '_nav_to_welcome',
        ]
        
        for method_name in methods_to_check:
            if hasattr(app, method_name):
                print(f"✅ Método {method_name} existe")
            else:
                print(f"❌ Método {method_name} NO existe")
                return False
        
        # Verificar que no hay referencias incorrectas
        with open('ui.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '_show_welcome_screen(' in content:
            print("❌ Aún existen referencias a _show_welcome_screen")
            return False
        else:
            print("✅ No hay referencias incorrectas a _show_welcome_screen")
        
        # Verificar que show_welcome_screen está siendo llamado correctamente
        correct_calls = content.count('self.show_welcome_screen()')
        if correct_calls > 0:
            print(f"✅ {correct_calls} llamadas correctas a show_welcome_screen encontradas")
        
        print("\n" + "=" * 60)
        print("🎉 TODOS LOS TESTS PASARON - Error corregido exitosamente")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR durante el test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_navigation_fix()
    sys.exit(0 if success else 1)