#!/usr/bin/env python3
"""
Script de verificación de correcciones de alias en BIOMARCADORES
"""
import sys
sys.path.insert(0, 'C:/Users/drestrepo/Documents/ProyectoHUV9GESTOR_ONCOLOGIA_automatizado/herramientas_ia')

from auditor_sistema import AuditorSistema

BIOMARCADORES = AuditorSistema.BIOMARCADORES

print("=" * 60)
print("VERIFICACION FINAL DE CORRECCIONES v6.0.9")
print("=" * 60)
print()

# Lista de correcciones esperadas
correcciones_esperadas = {
    'DESMIN': 'IHQ_DESMIN',
    'CKAE1AE3': 'IHQ_CKAE1AE3',
    'CAM52': 'IHQ_CAM52',
    'HEPAR': 'IHQ_HEPAR',
    'NAPSIN': 'IHQ_NAPSIN',
    'GLIPICAN': 'IHQ_GLIPICAN',
    'RACEMASA': 'IHQ_RACEMASA',
    'TYROSINASE': 'IHQ_TYROSINASE',
}

# Verificar cada corrección
total = len(correcciones_esperadas)
correctos = 0

for alias, columna_esperada in correcciones_esperadas.items():
    columna_actual = BIOMARCADORES.get(alias, 'NO ENCONTRADO')

    if columna_actual == columna_esperada:
        print(f"✓ {alias:15} -> {columna_actual:20} [OK]")
        correctos += 1
    else:
        print(f"✗ {alias:15} -> {columna_actual:20} [ERROR - Esperado: {columna_esperada}]")

print()
print("=" * 60)
print(f"RESULTADO: {correctos}/{total} correcciones verificadas")
print("=" * 60)

if correctos == total:
    print("✓ TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE")
    sys.exit(0)
else:
    print("✗ HAY CORRECCIONES PENDIENTES O INCORRECTAS")
    sys.exit(1)
