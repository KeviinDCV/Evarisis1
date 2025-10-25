#!/usr/bin/env python3
"""
Genera archivo con casos de ejemplo específicos para debugging
"""
import json
import sys
from pathlib import Path
from collections import defaultdict

def cargar_resultados(json_path: str) -> dict:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extraer_casos_ejemplo(diagnosticos, tipo_error, max_casos=5):
    """Extrae casos ejemplo de un tipo de error específico"""
    casos = defaultdict(list)

    for diag in diagnosticos:
        if diag['problema_detectado'] == tipo_error:
            campo = diag['campo']
            casos[campo].append({
                'valor_bd': diag['valor_bd'],
                'valor_pdf': diag['valor_pdf_real'],
                'patron': diag['patron_que_debio_usar'],
                'fuente': diag.get('fuente_pdf', ''),
                'sugerencia': diag.get('sugerencia_correccion', '')
            })

    return casos

def generar_archivo_ejemplos(json_path: str):
    """Genera archivo de texto con ejemplos específicos"""

    datos = cargar_resultados(json_path)
    diagnosticos = datos.get('todos_los_diagnosticos', [])

    output_file = Path(__file__).parent / 'resultados' / 'casos_ejemplo_debug.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*100 + "\n")
        f.write("CASOS DE EJEMPLO PARA DEBUGGING - AUDITORÍA V3.0\n")
        f.write("="*100 + "\n\n")

        # PATRONES FALTANTES
        f.write("█ TIPO 1: PATRON_FALTANTE\n")
        f.write("="*100 + "\n")
        f.write("Estos casos NO tienen patrón definido en los extractors.\n")
        f.write("ACCIÓN: Agregar patrones regex al extractor correspondiente.\n\n")

        casos_faltantes = extraer_casos_ejemplo(diagnosticos, 'PATRON_FALTANTE', max_casos=10)

        for campo, ejemplos in sorted(casos_faltantes.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"\nCampo: {campo}\n")
            f.write(f"Total de casos: {len(ejemplos)}\n")
            f.write("-"*100 + "\n")

            for i, ejemplo in enumerate(ejemplos[:5], 1):
                f.write(f"\nEjemplo {i}:\n")
                f.write(f"  BD tiene:     '{ejemplo['valor_bd']}'\n")
                f.write(f"  PDF debería:  '{ejemplo['valor_pdf']}'\n")
                f.write(f"  Fuente PDF:   {ejemplo['fuente']}\n")
                f.write(f"\n  PATRÓN SUGERIDO:\n")

                # Analizar el PDF para sugerir patrón
                pdf_val = str(ejemplo['valor_pdf'])
                if pdf_val and pdf_val != 'None':
                    # Sugerir patrón basado en el texto
                    if pdf_val.startswith('DE "'):
                        f.write(f"    r'DE\\s*\"(.+?)\"', 'Diagnóstico entre comillas'\n")
                    elif 'SE SOLICITA' in pdf_val or 'PARA' in pdf_val[:50]:
                        f.write(f"    r'(?:SE SOLICITA|PARA|SE REALIZA)[:\s]+(.+?)(?:\\.|$)', 'Estudios solicitados'\n")
                    elif pdf_val.startswith('"'):
                        f.write(f"    r'\"(.+?)\"', 'Texto entre comillas'\n")
                    else:
                        f.write(f"    # Analizar manualmente el PDF:\n")
                        f.write(f"    # {pdf_val[:100]}...\n")

                f.write("\n")

        # EXTRACCIÓN INCORRECTA
        f.write("\n\n")
        f.write("█ TIPO 2: EXTRACCION_INCORRECTA\n")
        f.write("="*100 + "\n")
        f.write("Estos casos TIENEN patrón, pero extraen INCORRECTAMENTE.\n")
        f.write("ACCIÓN: Corregir el patrón regex o la lógica de normalización.\n\n")

        casos_incorrectos = extraer_casos_ejemplo(diagnosticos, 'EXTRACCION_INCORRECTA', max_casos=10)

        for campo, ejemplos in sorted(casos_incorrectos.items(), key=lambda x: len(x[1]), reverse=True):
            f.write(f"\nCampo: {campo}\n")
            f.write(f"Total de casos: {len(ejemplos)}\n")
            f.write("-"*100 + "\n")

            for i, ejemplo in enumerate(ejemplos[:5], 1):
                f.write(f"\nEjemplo {i}:\n")
                f.write(f"  BD extrajo:   '{ejemplo['valor_bd']}'\n")
                f.write(f"  PDF real:     '{ejemplo['valor_pdf']}'\n")
                f.write(f"  Patrón usado: {ejemplo['patron']}\n")
                f.write(f"  Fuente PDF:   {ejemplo['fuente']}\n")

                # Análisis del problema
                bd_val = str(ejemplo['valor_bd'])
                pdf_val = str(ejemplo['valor_pdf'])

                if bd_val and pdf_val and bd_val != 'None' and pdf_val != 'None':
                    f.write(f"\n  ANÁLISIS:\n")

                    if len(bd_val) > len(pdf_val):
                        f.write(f"    ⚠ BD captura MÁS texto ({len(bd_val)} chars) que PDF ({len(pdf_val)} chars)\n")
                        f.write(f"    → El patrón está capturando texto extra o procesamiento incorrecto\n")
                        f.write(f"    → SOLUCIÓN: Hacer regex más restrictivo\n")

                        # Encontrar la diferencia
                        if bd_val.startswith(pdf_val):
                            extra = bd_val[len(pdf_val):]
                            f.write(f"    → Texto extra capturado: '{extra[:50]}...'\n")
                        elif pdf_val in bd_val:
                            idx = bd_val.index(pdf_val)
                            if idx > 0:
                                f.write(f"    → Prefijo extra: '{bd_val[:idx]}'\n")
                            if idx + len(pdf_val) < len(bd_val):
                                f.write(f"    → Sufijo extra: '{bd_val[idx+len(pdf_val):]}'\n")

                    elif len(bd_val) < len(pdf_val):
                        f.write(f"    ⚠ BD captura MENOS texto ({len(bd_val)} chars) que PDF ({len(pdf_val)} chars)\n")
                        f.write(f"    → El patrón está cortando prematuramente\n")
                        f.write(f"    → SOLUCIÓN: Expandir regex o capturar hasta fin de sección\n")

                        # Encontrar lo que falta
                        if pdf_val.startswith(bd_val):
                            faltante = pdf_val[len(bd_val):]
                            f.write(f"    → Texto faltante: '{faltante[:50]}...'\n")

                    else:
                        f.write(f"    ⚠ BD y PDF tienen igual longitud pero diferente contenido\n")
                        f.write(f"    → Posible normalización/transformación incorrecta\n")
                        f.write(f"    → SOLUCIÓN: Revisar métodos normalize_*\n")

                        # Mostrar caracteres diferentes
                        diff_chars = sum(1 for a, b in zip(bd_val, pdf_val) if a != b)
                        f.write(f"    → Caracteres diferentes: {diff_chars}/{len(bd_val)}\n")

                f.write("\n")

        # VALORES POR DEFECTO
        f.write("\n\n")
        f.write("█ TIPO 3: VALOR_POR_DEFECTO_INCORRECTO\n")
        f.write("="*100 + "\n")
        f.write("El PDF NO tiene el campo, pero la BD sí (valor aplicado automáticamente).\n")
        f.write("ACCIÓN: Revisar si es apropiado aplicar valores por defecto.\n\n")

        casos_defecto = extraer_casos_ejemplo(diagnosticos, 'VALOR_POR_DEFECTO_INCORRECTO', max_casos=10)

        for campo, ejemplos in sorted(casos_defecto.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            f.write(f"\nCampo: {campo}\n")
            f.write(f"Total de casos: {len(ejemplos)}\n")
            f.write("-"*100 + "\n")

            # Contar valores frecuentes
            from collections import Counter
            valores_freq = Counter([ej['valor_bd'] for ej in ejemplos])

            f.write(f"\n  Valores aplicados automáticamente:\n")
            for valor, count in valores_freq.most_common(5):
                f.write(f"    - '{valor}': {count} veces\n")

            f.write(f"\n  RECOMENDACIÓN:\n")
            f.write(f"    ¿Debe el sistema inferir '{campo}' cuando NO está en el PDF?\n")
            f.write(f"    → SI: Mejorar lógica de inferencia (mayor contexto)\n")
            f.write(f"    → NO: Retornar cadena vacía en lugar de valor por defecto\n")
            f.write("\n")

        f.write("\n" + "="*100 + "\n")
        f.write("FIN DEL REPORTE DE CASOS DE EJEMPLO\n")
        f.write("="*100 + "\n")

    print(f"✅ Archivo generado: {output_file}")
    return output_file

if __name__ == '__main__':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    # Buscar archivo más reciente
    resultados_dir = Path(__file__).parent / 'resultados'
    archivos_json = list(resultados_dir.glob('auditoria_inteligente_*.json'))

    if not archivos_json:
        print("❌ No se encontraron archivos de auditoría")
        sys.exit(1)

    json_path = max(archivos_json, key=lambda p: p.stat().st_mtime)
    print(f"📂 Analizando: {json_path.name}\n")

    archivo_generado = generar_archivo_ejemplos(str(json_path))
    print(f"\n📄 Revisar casos específicos en: {archivo_generado}")
