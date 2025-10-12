# -*- coding: utf-8 -*-
"""
Script de auditoría para verificar correcciones de IA
Verifica casos críticos IHQ250044 y IHQ250010
"""
import sqlite3
import json
import sys
from pathlib import Path

# Configurar encoding UTF-8 para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Conectar a BD
db_path = Path("data/huv_oncologia_NUEVO.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Casos críticos a verificar
casos_criticos = ["IHQ250044", "IHQ250010"]

print("=" * 80)
print("🔍 AUDITORÍA DE CORRECCIONES IA - CASOS CRÍTICOS")
print("=" * 80)
print()

for caso in casos_criticos:
    print(f"\n{'=' * 80}")
    print(f"📋 CASO: {caso}")
    print('=' * 80)

    # Obtener datos de BD
    cursor.execute("SELECT * FROM informes_ihq WHERE `N. peticion (0. Numero de biopsia)` = ?", (caso,))
    columnas = [desc[0] for desc in cursor.description]
    fila = cursor.fetchone()

    if not fila:
        print(f"❌ No se encontró el caso {caso} en la BD")
        continue

    # Convertir a diccionario
    datos = dict(zip(columnas, fila))

    # Extraer campos relevantes
    print("\n📊 DATOS DEMOGRÁFICOS:")
    print(f"  Nombre: {datos.get('Nombre completo')}")
    print(f"  Edad: {datos.get('Edad')}")
    print(f"  Género: {datos.get('Genero')}")

    print("\n🏥 DATOS MÉDICOS:")
    print(f"  Órgano: {datos.get('Organo (tabla)')}")
    print(f"  Diagnóstico Principal: {datos.get('Diagnostico Principal')}")
    print(f"  Malignidad: {datos.get('Malignidad')}")
    print(f"  Factor Pronóstico: {datos.get('Factor pronostico')[:100] if datos.get('Factor pronostico') else 'N/A'}...")

    print("\n🧬 BIOMARCADORES CRÍTICOS:")
    biomarcadores_criticos = {
        'Ki-67': datos.get('IHQ_KI-67'),
        'HER2': datos.get('IHQ_HER2'),
        'Receptor Estrógeno': datos.get('IHQ_RECEPTOR_ESTROGENO'),
        'Receptor Progesterona': datos.get('IHQ_RECEPTOR_PROGESTERONOS'),
        'P53': datos.get('IHQ_P53'),
        'PDL-1': datos.get('IHQ_PDL-1')
    }

    for nombre, valor in biomarcadores_criticos.items():
        icono = "✅" if valor and valor not in ['N/A', ''] else "⚠️"
        print(f"  {icono} {nombre}: {valor if valor else 'N/A'}")

    # Verificaciones específicas por caso
    print("\n🎯 VERIFICACIÓN DE CORRECCIONES:")

    if caso == "IHQ250044":
        ki67 = datos.get('IHQ_KI-67')
        print(f"\n  📌 Error original: Ki-67 era 10% pero PDF decía 20%")
        print(f"  📊 Valor actual en BD: {ki67}")

        if ki67 == "20%":
            print(f"  ✅ CORRECTO: IA corrigió Ki-67 a 20%")
        elif ki67 == "10%":
            print(f"  ❌ ERROR: Ki-67 sigue siendo 10% (no se corrigió)")
        else:
            print(f"  ⚠️ INESPERADO: Ki-67 tiene valor '{ki67}'")

    if caso == "IHQ250010":
        er = datos.get('IHQ_RECEPTOR_ESTROGENO')
        her2 = datos.get('IHQ_HER2')
        p53 = datos.get('IHQ_P53')
        pdl1 = datos.get('IHQ_PDL-1')

        print(f"\n  📌 Error original: IA infería 'NEGATIVO' sin evidencia")
        print(f"  📊 Valores actuales:")
        print(f"     - Receptor Estrógeno: {er}")
        print(f"     - HER2: {her2}")
        print(f"     - P53: {p53}")
        print(f"     - PDL-1: {pdl1}")

        errores = []
        for nombre, valor in [('ER', er), ('HER2', her2), ('P53', p53), ('PDL-1', pdl1)]:
            if valor == "NEGATIVO":
                errores.append(nombre)

        if errores:
            print(f"  ❌ ERROR: Biomarcadores marcados como NEGATIVO sin evidencia: {', '.join(errores)}")
        elif any(v in ['NO MENCIONADO', 'NO REPORTADO'] for v in [er, her2, p53, pdl1]):
            print(f"  ✅ CORRECTO: IA usa 'NO MENCIONADO' en lugar de inferir NEGATIVO")
        else:
            print(f"  ⚠️ REVISAR: Valores inesperados en biomarcadores")

conn.close()

print("\n" + "=" * 80)
print("✅ AUDITORÍA COMPLETADA")
print("=" * 80)
