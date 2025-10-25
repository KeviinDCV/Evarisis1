#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Debug Simple para IHQ250984 - Consultar BD directamente
v6.0.12 - Verificar qué valores están en la BD actualmente

Uso:
    python herramientas_ia/debug_simple_IHQ250984.py
"""

import sys
import os
import sqlite3
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════

DB_PATH = "huv_oncologia.db"
CASO_ID = "IHQ250984"

# ═══════════════════════════════════════════════════════════════════════
# FUNCIONES
# ═══════════════════════════════════════════════════════════════════════

def conectar_bd():
    """Conecta a la base de datos"""
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Base de datos no encontrada en {DB_PATH}")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"❌ ERROR al conectar a BD: {e}")
        return None


def obtener_caso(conn, caso_id):
    """Obtiene un caso de la BD"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM casos WHERE numero_estudio = ?", (caso_id,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        else:
            print(f"❌ Caso {caso_id} no encontrado en BD")
            return None
    except Exception as e:
        print(f"❌ ERROR al consultar caso: {e}")
        return None


def analizar_caso(caso):
    """Analiza y muestra los valores del caso"""
    print(f"\n{'='*80}")
    print(f"ANÁLISIS DEL CASO {caso['numero_estudio']}")
    print(f"{'='*80}\n")

    # Campos de interés
    campos_interes = [
        ("NUMERO_ESTUDIO", "Número de Estudio"),
        ("PACIENTE_NOMBRE", "Nombre Paciente"),
        ("IHQ_ORGANO", "Órgano"),
        ("DIAGNOSTICO_PRINCIPAL", "Diagnóstico Principal"),
        ("FACTOR_PRONOSTICO", "Factor Pronóstico"),
        ("IHQ_RECEPTOR_ESTROGENOS", "Receptor Estrógenos"),
        ("IHQ_RECEPTOR_PROGESTERONA", "Receptor Progesterona"),
        ("IHQ_HER2", "HER2"),
        ("IHQ_KI_67", "Ki-67"),
        ("IHQ_GATA3", "GATA3"),
        ("IHQ_SOX10", "SOX10"),
        ("IHQ_ESTUDIOS_SOLICITADOS", "Estudios Solicitados"),
    ]

    # Valores esperados
    valores_esperados = {
        "IHQ_RECEPTOR_ESTROGENOS": "NEGATIVO",
        "IHQ_RECEPTOR_PROGESTERONA": "NEGATIVO",
        "IHQ_HER2": "POSITIVO (SCORE 3+)",
        "IHQ_KI_67": "60%",
        "IHQ_GATA3": "POSITIVO",
        "IHQ_SOX10": "NEGATIVO",
    }

    print(f"{'Campo':<35} {'Valor en BD':<50} {'Estado'}")
    print(f"{'-'*95}")

    for campo_db, campo_nombre in campos_interes:
        valor = caso.get(campo_db, "N/A")

        # Limitar longitud de valor para display
        valor_display = str(valor) if valor else "N/A"
        if len(valor_display) > 45:
            valor_display = valor_display[:45] + "..."

        # Verificar estado
        esperado = valores_esperados.get(campo_db)
        if esperado:
            if esperado.upper() in str(valor).upper():
                estado = "✅ OK"
            elif not valor or valor == "N/A":
                estado = "❌ VACÍO"
            else:
                estado = f"❌ ERROR (esperado: {esperado})"
        else:
            estado = ""

        print(f"{campo_nombre:<35} {valor_display:<50} {estado}")

    # Análisis específico de problemas
    print(f"\n{'='*80}")
    print("ANÁLISIS DE PROBLEMAS DETECTADOS")
    print(f"{'='*80}\n")

    problemas = []

    # Verificar si captura texto técnico
    er_valor = str(caso.get("IHQ_RECEPTOR_ESTROGENOS", ""))
    if "RABBIT" in er_valor.upper() or "ANTIBODY" in er_valor.upper():
        problemas.append(
            "🔴 ER captura REACTIVO TÉCNICO en lugar de resultado\n"
            f"   Valor actual: {er_valor[:100]}\n"
            f"   Problema: Captura de sección 'Anticuerpos:' (página 1)\n"
            f"   Debería capturar: NEGATIVO (de 'REPORTE DE BIOMARCADORES:' página 2)"
        )

    her2_valor = str(caso.get("IHQ_HER2", ""))
    if "PATHWAY" in her2_valor.upper() or "ANTIBODY" in her2_valor.upper():
        problemas.append(
            "🔴 HER2 captura REACTIVO TÉCNICO en lugar de resultado\n"
            f"   Valor actual: {her2_valor[:100]}\n"
            f"   Problema: Captura de sección 'Anticuerpos:' (página 1)\n"
            f"   Debería capturar: POSITIVO (SCORE 3+) (de 'REPORTE DE BIOMARCADORES:' página 2)"
        )

    # Verificar si hay campos vacíos
    campos_vacios = []
    for campo_db in ["IHQ_RECEPTOR_PROGESTERONA", "IHQ_KI_67", "IHQ_SOX10"]:
        valor = caso.get(campo_db)
        if not valor or valor == "N/A":
            campos_vacios.append(campo_db)

    if campos_vacios:
        problemas.append(
            f"🔴 Campos VACÍOS (deberían tener valores):\n" +
            "\n".join(f"   - {campo}" for campo in campos_vacios)
        )

    # Verificar IHQ_ESTUDIOS_SOLICITADOS truncado
    estudios = str(caso.get("IHQ_ESTUDIOS_SOLICITADOS", ""))
    if estudios.endswith("RECEPTOR DE") or len(estudios) < 50:
        problemas.append(
            "🔴 IHQ_ESTUDIOS_SOLICITADOS está TRUNCADO\n"
            f"   Valor actual: {estudios}\n"
            f"   Problema: Lista cortada en mitad de palabra\n"
            f"   Debería contener: 6 biomarcadores completos"
        )

    if problemas:
        for i, problema in enumerate(problemas, 1):
            print(f"{i}. {problema}\n")
    else:
        print("✅ No se detectaron problemas críticos")

    # Resumen
    print(f"\n{'='*80}")
    print("RESUMEN")
    print(f"{'='*80}\n")

    correctos = sum(1 for campo in valores_esperados.keys()
                   if valores_esperados[campo].upper() in str(caso.get(campo, "")).upper())
    total = len(valores_esperados)
    score = (correctos / total * 100) if total > 0 else 0

    print(f"Biomarcadores correctos: {correctos}/{total}")
    print(f"Score: {score:.1f}%")
    print(f"Estado: {'✅ OK' if score >= 90 else '⚠️ WARNING' if score >= 50 else '❌ CRÍTICO'}")

    print(f"\n{'='*80}")
    print("DIAGNÓSTICO")
    print(f"{'='*80}\n")

    if "RABBIT" in er_valor.upper() or "PATHWAY" in her2_valor.upper():
        print(
            "❌ PROBLEMA CONFIRMADO: Los extractores están leyendo la sección\n"
            "   'Anticuerpos:' (reactivos técnicos de página 1) en lugar de\n"
            "   'REPORTE DE BIOMARCADORES:' (resultados de página 2)\n\n"
            "📋 CAUSA RAÍZ PROBABLE:\n"
            "   - La corrección v6.0.12 NO está funcionando\n"
            "   - La sección 'REPORTE DE BIOMARCADORES:' NO se está extrayendo\n"
            "   - O la cascada de prioridades NO se está ejecutando\n\n"
            "🛠️ SOLUCIÓN SUGERIDA:\n"
            "   - Verificar que el caso se REPROCESÓ con v6.0.12\n"
            "   - Agregar prints/logging en extract_biomarkers() para debug\n"
            "   - Crear extractor quirúrgico específico para formato '-BIOMARCADOR:'\n"
        )
    elif score < 90:
        print(
            "⚠️ PROBLEMAS DETECTADOS:\n"
            f"   - {len(campos_vacios)} campo(s) vacío(s)\n"
            "   - Extracción parcial funcionando\n\n"
            "🛠️ POSIBLES CAUSAS:\n"
            "   - Patrones regex no coinciden con formato exacto del PDF\n"
            "   - Typos en el PDF (ej: 'PROGRESTERONA' en lugar de 'PROGESTERONA')\n"
            "   - Sección específica no contiene todos los biomarcadores\n"
        )
    else:
        print("✅ Extracción funcionando correctamente")


# ═══════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════

def main():
    print(f"\n{'#'*80}")
    print(f"# DEBUG SIMPLE - Consulta BD para IHQ250984")
    print(f"# Versión: v6.0.12")
    print(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'#'*80}\n")

    # Conectar a BD
    conn = conectar_bd()
    if not conn:
        return

    # Obtener caso
    caso = obtener_caso(conn, CASO_ID)
    if not caso:
        conn.close()
        return

    # Analizar caso
    analizar_caso(caso)

    # Cerrar conexión
    conn.close()

    print(f"\n✅ Debug completado\n")


if __name__ == "__main__":
    main()
