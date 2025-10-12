#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 Herramienta Avanzada de Consulta y Gestión de Base de Datos
================================================================

Herramienta consolidada para consultar, verificar y actualizar registros
en la base de datos SQLite del sistema de gestión oncológica HUV.

Funcionalidades:
- Consultar registros por número de petición (IHQ)
- Verificar datos de casos específicos
- Actualizar registros existentes
- Buscar registros por criterios
- Estadísticas y análisis de la base de datos

Autor: Sistema EVARISIS
Fecha: 4 de octubre de 2025
Versión: 4.2.0 - Consolidado y mejorado
"""

import sys
import os
import sqlite3
import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Configurar salida UTF-8 en Windows
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from core.database_manager import DB_FILE, TABLE_NAME, init_db, save_records
    from core import unified_extractor as ihq
    from core.processors.ocr_processor import pdf_to_text_enhanced
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)


class GestorBaseDatos:
    """Gestor avanzado para la base de datos de oncología HUV"""
    
    def __init__(self):
        self.db_path = DB_FILE
        self.table_name = TABLE_NAME
        self._verificar_bd()
    
    def _verificar_bd(self):
        """Verificar que la base de datos existe"""
        if not os.path.exists(self.db_path):
            print(f"⚠️  Base de datos no encontrada: {self.db_path}")
            print("Creando base de datos...")
            init_db()
    
    def consultar_ihq(self, numero_ihq: str) -> Optional[Dict]:
        """Consultar un registro específico por número IHQ
        
        Args:
            numero_ihq: Número de petición (ej: IHQ250001)
        
        Returns:
            Diccionario con los datos del registro o None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(f'''
                SELECT * FROM {self.table_name}
                WHERE "N. peticion (0. Numero de biopsia)" = ?
            ''', (numero_ihq,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()
    
    def verificar_campos_criticos(self, numero_ihq: str) -> Dict[str, Any]:
        """Verificar campos críticos de un registro
        
        Args:
            numero_ihq: Número de petición
        
        Returns:
            Diccionario con campos críticos y su estado
        """
        registro = self.consultar_ihq(numero_ihq)
        
        if not registro:
            return {'error': f'Registro {numero_ihq} no encontrado'}
        
        # Campos críticos a verificar
        campos_criticos = {
            'Genero': registro.get('Genero'),
            'EPS': registro.get('EPS'),
            'IHQ_ORGANO': registro.get('IHQ_ORGANO'),
            'Organo (1. Muestra enviada a patología)': registro.get('Organo (1. Muestra enviada a patología)'),
            'Primer nombre': registro.get('Primer nombre'),
            'Primer apellido': registro.get('Primer apellido'),
        }
        
        # Identificar campos vacíos o con N/A
        problemas = []
        for campo, valor in campos_criticos.items():
            if not valor or valor == 'N/A' or valor.strip() == '':
                problemas.append(campo)
        
        return {
            'numero_peticion': numero_ihq,
            'campos_criticos': campos_criticos,
            'campos_con_problemas': problemas,
            'tiene_problemas': len(problemas) > 0
        }
    
    def buscar_por_criterio(self, campo: str, valor: str, limite: int = 10) -> List[Dict]:
        """Buscar registros por un criterio específico
        
        Args:
            campo: Nombre del campo a buscar
            valor: Valor a buscar (acepta LIKE con %)
            limite: Número máximo de resultados
        
        Returns:
            Lista de diccionarios con registros encontrados
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            # Usar LIKE si el valor contiene %
            if '%' in valor:
                query = f'SELECT * FROM {self.table_name} WHERE "{campo}" LIKE ? LIMIT ?'
            else:
                query = f'SELECT * FROM {self.table_name} WHERE "{campo}" = ? LIMIT ?'
            
            cursor.execute(query, (valor, limite))
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
        finally:
            conn.close()
    
    def actualizar_desde_pdf(self, numero_ihq: str, pdf_path: str) -> Dict[str, Any]:
        """Actualizar un registro extrayendo datos del PDF
        
        Args:
            numero_ihq: Número de petición a actualizar
            pdf_path: Ruta al PDF con los datos
        
        Returns:
            Diccionario con resultado de la actualización
        """
        print(f"\n{'='*80}")
        print(f"ACTUALIZANDO REGISTRO {numero_ihq}")
        print(f"{'='*80}\n")
        
        # Paso 1: Verificar que existe el registro
        print(f"1️⃣  Verificando registro existente...")
        registro_anterior = self.consultar_ihq(numero_ihq)
        
        if not registro_anterior:
            return {'error': f'Registro {numero_ihq} no encontrado en la BD'}
        
        print(f"   ✅ Registro encontrado")
        
        # Paso 2: Extraer texto del PDF
        print(f"\n2️⃣  Extrayendo texto del PDF...")
        if not os.path.exists(pdf_path):
            return {'error': f'PDF no encontrado: {pdf_path}'}
        
        texto_completo = pdf_to_text_enhanced(pdf_path)
        
        # Buscar el segmento del IHQ específico
        idx = texto_completo.find(numero_ihq)
        if idx == -1:
            return {'error': f'{numero_ihq} no encontrado en el PDF'}
        
        # Extraer segmento (hasta el siguiente IHQ o 3000 chars)
        import re
        siguiente_match = re.search(r'IHQ\d{6}', texto_completo[idx+len(numero_ihq):])
        if siguiente_match:
            idx_next = idx + len(numero_ihq) + siguiente_match.start()
            segmento = texto_completo[idx:idx_next]
        else:
            segmento = texto_completo[idx:idx+3000]
        
        print(f"   ✅ Segmento extraído ({len(segmento)} caracteres)")
        
        # Paso 3: Procesar con extractores
        print(f"\n3️⃣  Procesando con extractores refactorizados...")
        datos_extraidos = ihq.extract_ihq_data(segmento)
        filas = ihq.map_to_excel_format(datos_extraidos)
        
        if not filas:
            return {'error': 'No se pudieron extraer datos del PDF'}
        
        fila = filas[0]
        print(f"   ✅ Datos extraídos:")
        print(f"      - Género: {fila.get('Genero', 'NO')}")
        print(f"      - EPS: {fila.get('EPS', 'NO')[:50]}...")
        print(f"      - IHQ_ORGANO: {fila.get('IHQ_ORGANO', 'NO')}")
        
        # Paso 4: Eliminar registro anterior
        print(f"\n4️⃣  Eliminando registro anterior...")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f'''
            DELETE FROM {self.table_name}
            WHERE "N. peticion (0. Numero de biopsia)" = ?
        ''', (numero_ihq,))
        conn.commit()
        conn.close()
        print(f"   ✅ Registro anterior eliminado")
        
        # Paso 5: Guardar nuevo registro
        print(f"\n5️⃣  Guardando nuevo registro...")
        guardados = save_records(filas)
        print(f"   ✅ Guardado: {guardados} registro(s)")
        
        # Paso 6: Verificar
        print(f"\n6️⃣  Verificando actualización...")
        registro_nuevo = self.consultar_ihq(numero_ihq)
        
        if registro_nuevo:
            print(f"   ✅ Verificación exitosa:")
            print(f"      - Género: {registro_nuevo.get('Genero')}")
            print(f"      - EPS: {registro_nuevo.get('EPS')}")
            print(f"      - IHQ_ORGANO: {registro_nuevo.get('IHQ_ORGANO')}")
            print(f"\n{'='*80}\n")
            
            return {
                'exito': True,
                'numero_ihq': numero_ihq,
                'registro_anterior': registro_anterior,
                'registro_nuevo': registro_nuevo
            }
        else:
            return {'error': 'No se pudo verificar el registro actualizado'}
    
    def analizar_completitud(self, numero_ihq: str) -> Dict[str, Any]:
        """Analizar la completitud de datos de un registro

        Args:
            numero_ihq: Número de petición

        Returns:
            Diccionario con análisis de completitud detallado
        """
        registro = self.consultar_ihq(numero_ihq)

        if not registro:
            return {'error': f'Registro {numero_ihq} no encontrado'}

        # Definir categorías de campos
        campos_paciente = [
            'Primer nombre', 'Segundo nombre', 'Primer apellido', 'Segundo apellido',
            'Genero', 'Edad', 'EPS', 'Medico tratante', 'Servicio/Origen',
            'N. identificacion', 'Tipo de identificacion'
        ]

        campos_medicos = [
            'Organo (1. Muestra enviada a patología)', 'IHQ_ORGANO',
            'Diagnostico Principal (segun CIE 10)',
            'Descripcion Microscopica', 'Descripcion Macroscopica',
            'Fecha toma de muestra', 'Fecha informe'
        ]

        # Biomarcadores comunes
        campos_biomarcadores = [
            'IHQ_HER2', 'IHQ_KI-67', 'IHQ_RECEPTOR_ESTROGENO', 'IHQ_RECEPTOR_PROGESTERONOS',
            'IHQ_P16_ESTADO', 'IHQ_P40_ESTADO', 'IHQ_CK7', 'IHQ_CK20', 'IHQ_TTF1',
            'IHQ_SYNAPTOPHYSIN', 'IHQ_CHROMOGRANINA', 'IHQ_GATA3'
        ]

        # Analizar completitud por categoría
        def analizar_categoria(campos):
            total = len(campos)
            completos = 0
            vacios = []

            for campo in campos:
                valor = registro.get(campo, '')
                if valor and valor not in ['N/A', '', 'ORGANO_NO_ESPECIFICADO', 'NO ESPECIFICADO']:
                    completos += 1
                else:
                    vacios.append(campo)

            porcentaje = round((completos / total * 100), 1) if total > 0 else 0
            return {
                'total': total,
                'completos': completos,
                'vacios': len(vacios),
                'porcentaje': porcentaje,
                'campos_vacios': vacios
            }

        analisis_paciente = analizar_categoria(campos_paciente)
        analisis_medicos = analizar_categoria(campos_medicos)
        analisis_biomarcadores = analizar_categoria(campos_biomarcadores)

        # Calcular completitud global
        total_campos = len(campos_paciente) + len(campos_medicos) + len(campos_biomarcadores)
        total_completos = analisis_paciente['completos'] + analisis_medicos['completos'] + analisis_biomarcadores['completos']
        completitud_global = round((total_completos / total_campos * 100), 1) if total_campos > 0 else 0

        return {
            'numero_peticion': numero_ihq,
            'completitud_global': completitud_global,
            'paciente': analisis_paciente,
            'medicos': analisis_medicos,
            'biomarcadores': analisis_biomarcadores,
            'resumen': {
                'total_campos_analizados': total_campos,
                'total_campos_completos': total_completos,
                'total_campos_vacios': total_campos - total_completos
            }
        }

    def generar_reporte_registros(self, numeros_ihq: List[str], output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generar reporte detallado de múltiples registros

        Args:
            numeros_ihq: Lista de números de petición
            output_file: Archivo de salida opcional (Markdown)

        Returns:
            Diccionario con el reporte completo
        """
        resultados = []

        for numero_ihq in numeros_ihq:
            analisis = self.analizar_completitud(numero_ihq)
            if 'error' not in analisis:
                registro = self.consultar_ihq(numero_ihq)

                # Contar biomarcadores detectados
                biomarcadores_detectados = []
                for campo, valor in registro.items():
                    if campo.startswith('IHQ_') and valor and valor not in ['N/A', '', 'NO']:
                        biomarcadores_detectados.append(campo)

                resultados.append({
                    'numero_ihq': numero_ihq,
                    'completitud': analisis['completitud_global'],
                    'paciente': analisis['paciente'],
                    'medicos': analisis['medicos'],
                    'biomarcadores': analisis['biomarcadores'],
                    'biomarcadores_detectados': len(biomarcadores_detectados),
                    'lista_biomarcadores': biomarcadores_detectados,
                    'registro_completo': registro
                })

        # Calcular promedios
        if resultados:
            promedio_completitud = round(sum(r['completitud'] for r in resultados) / len(resultados), 1)
            promedio_biomarcadores = round(sum(r['biomarcadores_detectados'] for r in resultados) / len(resultados), 1)
        else:
            promedio_completitud = 0
            promedio_biomarcadores = 0

        reporte = {
            'fecha_generacion': datetime.now().isoformat(),
            'total_registros_analizados': len(resultados),
            'promedio_completitud': promedio_completitud,
            'promedio_biomarcadores': promedio_biomarcadores,
            'registros': resultados
        }

        # Generar archivo Markdown si se especifica
        if output_file:
            self._generar_markdown_reporte(reporte, output_file)

        return reporte

    def _generar_markdown_reporte(self, reporte: Dict[str, Any], output_file: str):
        """Generar archivo Markdown con el reporte"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Reporte de Análisis de Registros HUV - Oncología\n\n")
            f.write(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total de registros analizados:** {reporte['total_registros_analizados']}\n\n")
            f.write(f"**Completitud promedio:** {reporte['promedio_completitud']}%\n\n")
            f.write(f"**Biomarcadores promedio por registro:** {reporte['promedio_biomarcadores']}\n\n")

            f.write("---\n\n")

            # Detalle por registro
            for idx, reg in enumerate(reporte['registros'], 1):
                f.write(f"## {idx}. Registro {reg['numero_ihq']}\n\n")
                f.write(f"**Completitud global:** {reg['completitud']}%\n\n")

                # Tabla de completitud por categoría
                f.write("### Completitud por Categoría\n\n")
                f.write("| Categoría | Completos | Vacíos | Total | Porcentaje |\n")
                f.write("|-----------|-----------|--------|-------|------------|\n")
                f.write(f"| Datos del Paciente | {reg['paciente']['completos']} | {reg['paciente']['vacios']} | {reg['paciente']['total']} | {reg['paciente']['porcentaje']}% |\n")
                f.write(f"| Datos Médicos | {reg['medicos']['completos']} | {reg['medicos']['vacios']} | {reg['medicos']['total']} | {reg['medicos']['porcentaje']}% |\n")
                f.write(f"| Biomarcadores | {reg['biomarcadores']['completos']} | {reg['biomarcadores']['vacios']} | {reg['biomarcadores']['total']} | {reg['biomarcadores']['porcentaje']}% |\n")
                f.write("\n")

                # Biomarcadores detectados
                f.write(f"### Biomarcadores Detectados ({reg['biomarcadores_detectados']})\n\n")
                if reg['lista_biomarcadores']:
                    for bio in reg['lista_biomarcadores']:
                        valor = reg['registro_completo'].get(bio, 'N/A')
                        f.write(f"- **{bio}**: {valor}\n")
                else:
                    f.write("No se detectaron biomarcadores.\n")

                f.write("\n")

                # Campos vacíos críticos
                if reg['paciente']['campos_vacios'] or reg['medicos']['campos_vacios']:
                    f.write("### Campos Vacíos o Incompletos\n\n")

                    if reg['paciente']['campos_vacios']:
                        f.write("**Datos del Paciente:**\n")
                        for campo in reg['paciente']['campos_vacios']:
                            f.write(f"- {campo}\n")
                        f.write("\n")

                    if reg['medicos']['campos_vacios']:
                        f.write("**Datos Médicos:**\n")
                        for campo in reg['medicos']['campos_vacios']:
                            f.write(f"- {campo}\n")
                        f.write("\n")

                f.write("---\n\n")

            # Resumen final
            f.write("## Resumen General\n\n")
            f.write(f"- **Completitud promedio:** {reporte['promedio_completitud']}%\n")
            f.write(f"- **Biomarcadores promedio:** {reporte['promedio_biomarcadores']} por registro\n")
            f.write(f"- **Estado del sistema:** Funcional al {reporte['promedio_completitud']}%\n\n")

            if reporte['promedio_completitud'] >= 90:
                f.write("✅ **Estado: EXCELENTE** - El sistema está funcionando de manera óptima.\n")
            elif reporte['promedio_completitud'] >= 70:
                f.write("⚠️ **Estado: BUENO** - El sistema funciona correctamente con margen de mejora.\n")
            elif reporte['promedio_completitud'] >= 50:
                f.write("⚠️ **Estado: ACEPTABLE** - Se requieren mejoras en la extracción de datos.\n")
            else:
                f.write("❌ **Estado: DEFICIENTE** - Se requiere revisión urgente del sistema de extracción.\n")

        print(f"\n[OK] Reporte generado: {output_file}")

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Total de registros
            cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
            total = cursor.fetchone()[0]

            # Registros por género
            cursor.execute(f'''
                SELECT Genero, COUNT(*) as cantidad
                FROM {self.table_name}
                WHERE Genero IS NOT NULL AND Genero != 'N/A'
                GROUP BY Genero
            ''')
            por_genero = dict(cursor.fetchall())

            # Registros con problemas (N/A en campos críticos)
            cursor.execute(f'''
                SELECT COUNT(*) FROM {self.table_name}
                WHERE Genero = 'N/A' OR EPS = 'N/A' OR "IHQ_ORGANO" = 'ORGANO_NO_ESPECIFICADO'
            ''')
            con_problemas = cursor.fetchone()[0]

            # Últimos registros
            cursor.execute(f'''
                SELECT "N. peticion (0. Numero de biopsia)"
                FROM {self.table_name}
                ORDER BY id DESC
                LIMIT 5
            ''')
            ultimos = [row[0] for row in cursor.fetchall()]

            return {
                'total_registros': total,
                'por_genero': por_genero,
                'con_problemas': con_problemas,
                'porcentaje_problemas': round(con_problemas / total * 100, 2) if total > 0 else 0,
                'ultimos_registros': ultimos
            }
        finally:
            conn.close()


def main():
    """Función principal con CLI mejorado"""
    parser = argparse.ArgumentParser(
        description='🔍 Herramienta de Consulta y Gestión de Base de Datos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Consultar un registro específico
  python consulta_base_datos.py --consultar IHQ250001
  
  # Verificar campos críticos
  python consulta_base_datos.py --verificar IHQ250001
  
  # Actualizar desde PDF
  python consulta_base_datos.py --actualizar IHQ250001 --pdf "despues de ordenamientos/IHQ DEL 001 AL 050.pdf"
  
  # Buscar por criterio
  python consulta_base_datos.py --buscar --campo Genero --valor MASCULINO
  
  # Estadísticas
  python consulta_base_datos.py --estadisticas
        """
    )
    
    parser.add_argument('--consultar', '-c', metavar='IHQ',
                       help='Consultar registro por número IHQ')
    parser.add_argument('--verificar', '-v', metavar='IHQ',
                       help='Verificar campos críticos de un registro')
    parser.add_argument('--actualizar', '-a', metavar='IHQ',
                       help='Actualizar registro desde PDF')
    parser.add_argument('--pdf', '-p', metavar='RUTA',
                       help='Ruta al PDF (requerido con --actualizar)')
    parser.add_argument('--buscar', '-b', action='store_true',
                       help='Buscar registros por criterio')
    parser.add_argument('--campo', metavar='CAMPO',
                       help='Campo para buscar (usar con --buscar)')
    parser.add_argument('--valor', metavar='VALOR',
                       help='Valor a buscar (usar con --buscar)')
    parser.add_argument('--estadisticas', '-e', action='store_true',
                       help='Mostrar estadísticas de la base de datos')
    parser.add_argument('--analizar-completitud', '--completitud', metavar='IHQ',
                       help='Analizar completitud de datos de un registro')
    parser.add_argument('--generar-reporte', '--reporte', nargs='+', metavar='IHQ',
                       help='Generar reporte detallado de múltiples registros')
    parser.add_argument('--output', '-o', metavar='ARCHIVO',
                       help='Archivo de salida para el reporte (Markdown)')
    parser.add_argument('--buscar-peticion', metavar='IHQ',
                       help='Buscar y mostrar detalles de un registro específico (análisis completo)')
    parser.add_argument('--limite', '-l', type=int, default=10,
                       help='Límite de resultados para búsquedas')

    # NUEVOS ARGUMENTOS para compatibilidad con CLI v4.2.1
    parser.add_argument('--listar', action='store_true',
                       help='Listar todos los registros')
    parser.add_argument('--paciente', metavar='NOMBRE',
                       help='Buscar por nombre de paciente')
    parser.add_argument('--organo', metavar='ORGANO',
                       help='Filtrar por órgano')
    parser.add_argument('--diagnostico', metavar='DIAG',
                       help='Filtrar por diagnóstico (regex)')
    parser.add_argument('--biomarcadores', metavar='IHQ',
                       help='Ver biomarcadores de caso IHQ')
    parser.add_argument('--verificar-integridad', action='store_true',
                       help='Verificar integridad de la BD')
    parser.add_argument('--contar', action='store_true',
                       help='Contar registros por categoría')
    parser.add_argument('--json', metavar='ARCHIVO',
                       help='Exportar resultado a JSON')

    args = parser.parse_args()
    
    # Crear gestor
    gestor = GestorBaseDatos()
    
    # Ejecutar comando
    if args.consultar:
        print(f"\n[CONSULTAR REGISTRO] {args.consultar}\n")
        registro = gestor.consultar_ihq(args.consultar)
        if registro:
            print("[OK] Registro encontrado:\n")
            for campo, valor in list(registro.items())[:15]:  # Primeros 15 campos
                print(f"  {campo}: {valor}")
            print(f"\n  ... (y {len(registro) - 15} campos mas)")
        else:
            print(f"[ERROR] Registro {args.consultar} no encontrado")

    elif args.verificar:
        print(f"\n[VERIFICAR CAMPOS CRITICOS] DE {args.verificar}\n")
        resultado = gestor.verificar_campos_criticos(args.verificar)

        if 'error' in resultado:
            print(f"[ERROR] {resultado['error']}")
        else:
            print("Campos criticos:")
            for campo, valor in resultado['campos_criticos'].items():
                estado = "[OK]" if valor and valor != 'N/A' else "[VACIO]"
                print(f"  {estado} {campo}: {valor}")

            if resultado['tiene_problemas']:
                print(f"\n[WARNING] Campos con problemas: {', '.join(resultado['campos_con_problemas'])}")
            else:
                print(f"\n[OK] Todos los campos criticos estan completos")

    elif args.actualizar:
        if not args.pdf:
            print("[ERROR] Error: --pdf es requerido con --actualizar")
            sys.exit(1)

        resultado = gestor.actualizar_desde_pdf(args.actualizar, args.pdf)

        if 'error' in resultado:
            print(f"[ERROR] Error: {resultado['error']}")
        elif resultado.get('exito'):
            print("[OK] Actualizacion completada exitosamente")

    elif args.buscar:
        if not args.campo or not args.valor:
            print("[ERROR] Error: --campo y --valor son requeridos con --buscar")
            sys.exit(1)

        print(f"\n[BUSCAR] EN CAMPO '{args.campo}' VALOR '{args.valor}'\n")
        resultados = gestor.buscar_por_criterio(args.campo, args.valor, args.limite)

        if resultados:
            print(f"[OK] Se encontraron {len(resultados)} resultado(s):\n")
            for i, reg in enumerate(resultados, 1):
                print(f"{i}. {reg.get('N. peticion (0. Numero de biopsia)', 'N/A')} - "
                      f"{reg.get('Primer nombre', '')} {reg.get('Primer apellido', '')}")
        else:
            print(f"[ERROR] No se encontraron resultados")
    
    elif args.estadisticas:
        print(f"\n[ESTADISTICAS] DE LA BASE DE DATOS\n")
        stats = gestor.obtener_estadisticas()

        print(f"Total de registros: {stats['total_registros']}")
        print(f"\nDistribución por género:")
        for genero, cantidad in stats['por_genero'].items():
            print(f"  {genero}: {cantidad}")

        print(f"\nRegistros con problemas: {stats['con_problemas']} ({stats['porcentaje_problemas']}%)")
        print(f"\nÚltimos 5 registros:")
        for ihq in stats['ultimos_registros']:
            print(f"  - {ihq}")

    elif args.analizar_completitud:
        print(f"\n[ANALISIS DE COMPLETITUD] - {args.analizar_completitud}\n")
        analisis = gestor.analizar_completitud(args.analizar_completitud)

        if 'error' in analisis:
            print(f"[ERROR] {analisis['error']}")
        else:
            print(f"Completitud Global: {analisis['completitud_global']}%\n")

            print("Detalle por Categoria:")
            print(f"  - Datos del Paciente: {analisis['paciente']['completos']}/{analisis['paciente']['total']} ({analisis['paciente']['porcentaje']}%)")
            print(f"  - Datos Medicos: {analisis['medicos']['completos']}/{analisis['medicos']['total']} ({analisis['medicos']['porcentaje']}%)")
            print(f"  - Biomarcadores: {analisis['biomarcadores']['completos']}/{analisis['biomarcadores']['total']} ({analisis['biomarcadores']['porcentaje']}%)")

            # Mostrar campos vacíos
            total_vacios = len(analisis['paciente']['campos_vacios']) + len(analisis['medicos']['campos_vacios'])
            if total_vacios > 0:
                print(f"\n[WARNING] Campos vacios detectados: {total_vacios}")

    elif args.generar_reporte:
        print(f"\n[GENERANDO REPORTE] DE {len(args.generar_reporte)} REGISTRO(S)\n")

        output_file = args.output if args.output else f"reporte_registros_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        reporte = gestor.generar_reporte_registros(args.generar_reporte, output_file)

        print(f"\n[OK] Reporte generado exitosamente")
        print(f"  - Registros analizados: {reporte['total_registros_analizados']}")
        print(f"  - Completitud promedio: {reporte['promedio_completitud']}%")
        print(f"  - Biomarcadores promedio: {reporte['promedio_biomarcadores']}")
        print(f"  - Archivo de salida: {output_file}")

    elif args.buscar_peticion:
        print(f"\n[BUSCAR PETICION] Analizando registro {args.buscar_peticion}\n")

        # Consultar registro
        registro = gestor.consultar_ihq(args.buscar_peticion)

        if not registro:
            print(f"[ERROR] Registro {args.buscar_peticion} no encontrado")
        else:
            # Analizar completitud
            analisis = gestor.analizar_completitud(args.buscar_peticion)

            print(f"[OK] Registro encontrado: {args.buscar_peticion}")
            print(f"Completitud: {analisis['completitud_global']}%\n")

            # Mostrar datos principales
            print("DATOS DEL PACIENTE:")
            print(f"  Nombre: {registro.get('Primer nombre', 'N/A')} {registro.get('Segundo nombre', '')} {registro.get('Primer apellido', 'N/A')} {registro.get('Segundo apellido', '')}")
            print(f"  Género: {registro.get('Genero', 'N/A')}")
            print(f"  Edad: {registro.get('Edad', 'N/A')}")
            print(f"  EPS: {registro.get('EPS', 'N/A')}")

            print("\nDATO MÉDICOS:")
            print(f"  Órgano (tabla): {registro.get('Organo (1. Muestra enviada a patología)', 'N/A')}")
            print(f"  IHQ Órgano: {registro.get('IHQ_ORGANO', 'N/A')}")
            print(f"  Diagnóstico: {registro.get('Diagnostico Principal (segun CIE 10)', 'N/A')[:100]}...")

            # Contar biomarcadores
            biomarcadores = [k for k, v in registro.items() if k.startswith('IHQ_') and v and v not in ['N/A', '', 'NO']]
            print(f"\nBIOMARCADORES DETECTADOS: {len(biomarcadores)}")
            if biomarcadores:
                for bio in biomarcadores[:10]:  # Mostrar máximo 10
                    print(f"  - {bio}: {registro.get(bio, 'N/A')}")
                if len(biomarcadores) > 10:
                    print(f"  ... y {len(biomarcadores) - 10} más")

    # NUEVOS COMANDOS v4.2.1
    elif args.listar:
        print(f"\n[LISTAR REGISTROS] (Límite: {args.limite})\n")
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT ?", (args.limite,))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        if rows:
            print(f"[OK] Se encontraron {len(rows)} registro(s):\n")
            for row in rows:
                registro = dict(zip(columns, row))
                print(f"  • {registro.get('N. peticion (0. Numero de biopsia)', 'N/A')} - "
                      f"{registro.get('Primer nombre', '')} {registro.get('Primer apellido', '')}")
        conn.close()

    elif args.paciente:
        print(f"\n[BUSCAR POR PACIENTE] '{args.paciente}'\n")
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()
        query = f"""
            SELECT * FROM {TABLE_NAME}
            WHERE `Primer nombre` LIKE ? OR `Primer apellido` LIKE ? OR `Segundo nombre` LIKE ? OR `Segundo apellido` LIKE ?
            LIMIT ?
        """
        pattern = f"%{args.paciente}%"
        cursor.execute(query, (pattern, pattern, pattern, pattern, args.limite))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        if rows:
            print(f"[OK] Se encontraron {len(rows)} resultado(s):\n")
            for row in rows:
                registro = dict(zip(columns, row))
                print(f"  • {registro.get('N. peticion (0. Numero de biopsia)', 'N/A')} - "
                      f"{registro.get('Primer nombre', '')} {registro.get('Segundo nombre', '')} "
                      f"{registro.get('Primer apellido', '')} {registro.get('Segundo apellido', '')}")
        else:
            print(f"[ERROR] No se encontraron resultados para '{args.paciente}'")
        conn.close()

    elif args.organo:
        print(f"\n[FILTRAR POR ÓRGANO] '{args.organo}'\n")
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()
        query = f"""
            SELECT * FROM {TABLE_NAME}
            WHERE `Organo (1. Muestra enviada a patología)` LIKE ? OR `IHQ_ORGANO` LIKE ?
            LIMIT ?
        """
        pattern = f"%{args.organo}%"
        cursor.execute(query, (pattern, pattern, args.limite))
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        if rows:
            print(f"[OK] Se encontraron {len(rows)} resultado(s):\n")
            for row in rows:
                registro = dict(zip(columns, row))
                print(f"  • {registro.get('N. peticion (0. Numero de biopsia)', 'N/A')} - "
                      f"Órgano: {registro.get('Organo (1. Muestra enviada a patología)', 'N/A')}")
        else:
            print(f"[ERROR] No se encontraron resultados para órgano '{args.organo}'")
        conn.close()

    elif args.diagnostico:
        print(f"\n[FILTRAR POR DIAGNÓSTICO] '{args.diagnostico}'\n")
        import re as regex_module
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        resultados = []
        for row in rows:
            registro = dict(zip(columns, row))
            diag = str(registro.get('Diagnostico Principal (segun CIE 10)', ''))
            if regex_module.search(args.diagnostico, diag, regex_module.IGNORECASE):
                resultados.append(registro)
                if len(resultados) >= args.limite:
                    break

        if resultados:
            print(f"[OK] Se encontraron {len(resultados)} resultado(s):\n")
            for registro in resultados:
                print(f"  • {registro.get('N. peticion (0. Numero de biopsia)', 'N/A')} - "
                      f"Diagnóstico: {str(registro.get('Diagnostico Principal (segun CIE 10)', 'N/A'))[:60]}...")
        else:
            print(f"[ERROR] No se encontraron resultados para el patrón '{args.diagnostico}'")
        conn.close()

    elif args.biomarcadores:
        print(f"\n[BIOMARCADORES] DE {args.biomarcadores}\n")
        registro = gestor.consultar_ihq(args.biomarcadores)

        if registro:
            biomarcadores = {k: v for k, v in registro.items()
                           if k.startswith('IHQ_') and v and v not in ['N/A', '', 'NO', None]}

            print(f"[OK] Biomarcadores encontrados: {len(biomarcadores)}\n")
            if biomarcadores:
                for bio, valor in biomarcadores.items():
                    print(f"  • {bio}: {valor}")
            else:
                print("[WARNING] No hay biomarcadores con valores positivos")
        else:
            print(f"[ERROR] Registro {args.biomarcadores} no encontrado")

    elif args.verificar_integridad:
        print(f"\n[VERIFICAR INTEGRIDAD] DE LA BASE DE DATOS\n")
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()

        # Total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        total = cursor.fetchone()[0]

        # Registros con N. petición vacío
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE `N. peticion (0. Numero de biopsia)` IS NULL OR `N. peticion (0. Numero de biopsia)` = ''")
        sin_peticion = cursor.fetchone()[0]

        # Registros con nombre vacío
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE `Primer nombre` IS NULL OR `Primer nombre` = ''")
        sin_nombre = cursor.fetchone()[0]

        print(f"Total de registros: {total}")
        print(f"Registros sin N. petición: {sin_peticion}")
        print(f"Registros sin nombre: {sin_nombre}")

        if sin_peticion == 0 and sin_nombre == 0:
            print(f"\n[OK] ✅ La base de datos tiene integridad correcta")
        else:
            print(f"\n[WARNING] ⚠️ Se detectaron {sin_peticion + sin_nombre} registros con problemas")

        conn.close()

    elif args.contar:
        print(f"\n[CONTAR REGISTROS] POR CATEGORÍA\n")
        conn = get_connection(DB_FILE)
        cursor = conn.cursor()

        # Por género
        cursor.execute(f"SELECT Genero, COUNT(*) FROM {TABLE_NAME} GROUP BY Genero")
        por_genero = cursor.fetchall()
        print("Por Género:")
        for genero, count in por_genero:
            print(f"  • {genero or 'N/A'}: {count}")

        # Por órgano (top 10)
        cursor.execute(f"SELECT `Organo (1. Muestra enviada a patología)`, COUNT(*) as cnt FROM {TABLE_NAME} GROUP BY `Organo (1. Muestra enviada a patología)` ORDER BY cnt DESC LIMIT 10")
        por_organo = cursor.fetchall()
        print("\nTop 10 Órganos:")
        for organo, count in por_organo:
            print(f"  • {organo or 'N/A'}: {count}")

        conn.close()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
