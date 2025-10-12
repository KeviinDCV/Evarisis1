#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛠️ Utilidades de Debug y Herramientas Auxiliares
============================================

Este módulo contiene funciones auxiliares comunes para todas las herramientas
de IA del sistema de gestión oncológica HUV.

Autor: Sistema EVARISIS
Fecha: 3 de octubre de 2025
Versión: 1.0.0
"""

import sys
import os
import json
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
import logging
from dataclasses import dataclass
import sqlite3

# Configuración de logging mejorada
def configurar_logging(nivel: str = "INFO", archivo_log: str = None) -> logging.Logger:
    """Configurar sistema de logging avanzado"""
    
    # Mapeo de niveles
    niveles = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    # Configurar formato
    formato = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Configurar logger
    logger = logging.getLogger('HUV_IA_Tools')
    logger.setLevel(niveles.get(nivel.upper(), logging.INFO))
    
    # Limpiar handlers existentes
    logger.handlers.clear()
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(niveles.get(nivel.upper(), logging.INFO))
    console_formatter = logging.Formatter(formato)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo si se especifica
    if archivo_log:
        file_handler = logging.FileHandler(archivo_log, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # Archivo siempre en DEBUG
        file_formatter = logging.Formatter(formato)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

@dataclass
class EstadisticasProcesamiento:
    """Clase para manejar estadísticas de procesamiento"""
    total_registros: int = 0
    registros_procesados: int = 0
    registros_con_errores: int = 0
    tiempo_inicio: datetime = None
    tiempo_fin: datetime = None
    errores: List[str] = None
    
    def __post_init__(self):
        if self.errores is None:
            self.errores = []
        if self.tiempo_inicio is None:
            self.tiempo_inicio = datetime.now()
    
    def agregar_error(self, error: str):
        """Agregar un error a la lista"""
        self.errores.append(f"[{datetime.now().isoformat()}] {error}")
        self.registros_con_errores += 1
    
    def finalizar(self):
        """Finalizar el procesamiento"""
        self.tiempo_fin = datetime.now()
    
    def duracion(self) -> timedelta:
        """Obtener duración del procesamiento"""
        fin = self.tiempo_fin or datetime.now()
        return fin - self.tiempo_inicio
    
    def porcentaje_exito(self) -> float:
        """Calcular porcentaje de éxito"""
        if self.total_registros == 0:
            return 0.0
        return ((self.registros_procesados - self.registros_con_errores) / self.total_registros) * 100
    
    def reporte(self) -> str:
        """Generar reporte de estadísticas"""
        duracion = self.duracion()
        
        reporte = f"""
📊 REPORTE DE PROCESAMIENTO
{'=' * 50}
• Total de registros: {self.total_registros:,}
• Registros procesados: {self.registros_procesados:,}
• Registros con errores: {self.registros_con_errores:,}
• Porcentaje de éxito: {self.porcentaje_exito():.1f}%
• Duración: {duracion}
• Velocidad: {self.registros_procesados / duracion.total_seconds():.1f} registros/segundo

⚠️ ERRORES ({len(self.errores)}):
"""
        
        for error in self.errores[-10:]:  # Últimos 10 errores
            reporte += f"   {error}\n"
        
        if len(self.errores) > 10:
            reporte += f"   ... y {len(self.errores) - 10} errores más\n"
        
        return reporte

class FormateadorSalida:
    """Clase para formatear salidas de manera consistente"""
    
    @staticmethod
    def titulo(texto: str, caracter: str = "=", ancho: int = 80) -> str:
        """Formatear un título"""
        return f"\n{caracter * ancho}\n{texto.center(ancho)}\n{caracter * ancho}\n"
    
    @staticmethod
    def subtitulo(texto: str, caracter: str = "-", ancho: int = 60) -> str:
        """Formatear un subtítulo"""
        return f"\n{caracter * ancho}\n{texto}\n{caracter * ancho}\n"
    
    @staticmethod
    def lista_numerada(items: List[str], prefijo: str = "") -> str:
        """Formatear una lista numerada"""
        resultado = ""
        for i, item in enumerate(items, 1):
            resultado += f"{prefijo}{i:2d}. {item}\n"
        return resultado
    
    @staticmethod
    def lista_con_viñetas(items: List[str], viñeta: str = "•", prefijo: str = "   ") -> str:
        """Formatear una lista con viñetas"""
        resultado = ""
        for item in items:
            resultado += f"{prefijo}{viñeta} {item}\n"
        return resultado
    
    @staticmethod
    def tabla_simple(datos: List[Dict[str, Any]], columnas: List[str] = None) -> str:
        """Formatear una tabla simple"""
        if not datos:
            return "No hay datos para mostrar\n"
        
        if not columnas:
            columnas = list(datos[0].keys())
        
        # Calcular anchos de columna
        anchos = {}
        for col in columnas:
            anchos[col] = max(
                len(str(col)),
                max(len(str(row.get(col, ""))) for row in datos)
            )
        
        # Construir tabla
        resultado = ""
        
        # Header
        header = " | ".join(str(col).ljust(anchos[col]) for col in columnas)
        resultado += header + "\n"
        resultado += "-" * len(header) + "\n"
        
        # Filas
        for row in datos:
            fila = " | ".join(str(row.get(col, "")).ljust(anchos[col]) for col in columnas)
            resultado += fila + "\n"
        
        return resultado
    
    @staticmethod
    def progreso(actual: int, total: int, ancho: int = 50) -> str:
        """Formatear barra de progreso"""
        if total == 0:
            porcentaje = 0
        else:
            porcentaje = (actual / total) * 100
        
        bloques_llenos = int((actual / total) * ancho) if total > 0 else 0
        bloques_vacios = ancho - bloques_llenos
        
        barra = "█" * bloques_llenos + "░" * bloques_vacios
        return f"[{barra}] {actual:,}/{total:,} ({porcentaje:.1f}%)"

class ValidadorDatos:
    """Clase para validar consistencia de datos"""
    
    @staticmethod
    def validar_numero_peticion(numero: str) -> bool:
        """Validar formato de número de petición"""
        if not numero:
            return False
        
        # Formato típico: IHQ250001, AUTO250001, etc.
        import re
        patron = r'^[A-Z]{2,5}\d{6}$'
        return bool(re.match(patron, numero.strip()))
    
    @staticmethod
    def validar_identificacion(identificacion: str) -> bool:
        """Validar número de identificación"""
        if not identificacion:
            return False
        
        # Remover puntos y espacios
        num_limpio = identificacion.replace(".", "").replace(" ", "")
        
        # Debe ser numérico y tener longitud razonable
        return num_limpio.isdigit() and 6 <= len(num_limpio) <= 12
    
    @staticmethod
    def validar_fecha(fecha: str) -> bool:
        """Validar formato de fecha"""
        if not fecha:
            return False
        
        formatos = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d-%m-%Y"
        ]
        
        for formato in formatos:
            try:
                datetime.strptime(fecha, formato)
                return True
            except ValueError:
                continue
        
        return False
    
    @staticmethod
    def detectar_problemas_registro(registro: Dict[str, Any]) -> List[str]:
        """Detectar problemas en un registro"""
        problemas = []
        
        # Validar campos obligatorios
        campos_obligatorios = [
            "N. peticion (0. Numero de biopsia)",
            "Primer nombre",
            "Primer apellido",
            "N. de identificación"
        ]
        
        for campo in campos_obligatorios:
            if not registro.get(campo) or str(registro[campo]).strip() == "":
                problemas.append(f"Campo obligatorio vacío: {campo}")
        
        # Validar número de petición
        numero_peticion = registro.get("N. peticion (0. Numero de biopsia)", "")
        if numero_peticion and not ValidadorDatos.validar_numero_peticion(numero_peticion):
            problemas.append(f"Formato de número de petición inválido: {numero_peticion}")
        
        # Validar identificación
        identificacion = registro.get("N. de identificación", "")
        if identificacion and not ValidadorDatos.validar_identificacion(identificacion):
            problemas.append(f"Formato de identificación inválido: {identificacion}")
        
        # Validar fechas
        campos_fecha = ["Fecha Informe", "Fecha de ingreso (2. Fecha de la muestra)"]
        for campo in campos_fecha:
            fecha = registro.get(campo, "")
            if fecha and not ValidadorDatos.validar_fecha(fecha):
                problemas.append(f"Formato de fecha inválido en {campo}: {fecha}")
        
        return problemas

class ManejadorArchivos:
    """Clase para manejar operaciones de archivos"""
    
    @staticmethod
    def crear_backup(archivo: str, sufijo: str = None) -> str:
        """Crear backup de un archivo"""
        if not os.path.exists(archivo):
            raise FileNotFoundError(f"Archivo no encontrado: {archivo}")
        
        if sufijo is None:
            sufijo = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        nombre_base = Path(archivo).stem
        extension = Path(archivo).suffix
        directorio = Path(archivo).parent
        
        archivo_backup = directorio / f"{nombre_base}_backup_{sufijo}{extension}"
        
        import shutil
        shutil.copy2(archivo, archivo_backup)
        
        return str(archivo_backup)
    
    @staticmethod
    def limpiar_archivos_antiguos(directorio: str, patron: str = "*", dias: int = 30):
        """Limpiar archivos antiguos de un directorio"""
        directorio = Path(directorio)
        if not directorio.exists():
            return
        
        fecha_limite = datetime.now() - timedelta(days=dias)
        archivos_eliminados = 0
        
        for archivo in directorio.glob(patron):
            if archivo.is_file():
                fecha_mod = datetime.fromtimestamp(archivo.stat().st_mtime)
                if fecha_mod < fecha_limite:
                    try:
                        archivo.unlink()
                        archivos_eliminados += 1
                    except Exception as e:
                        print(f"Error eliminando {archivo}: {e}")
        
        return archivos_eliminados

class ConectorBaseDatos:
    """Clase para operaciones avanzadas con la base de datos"""
    
    def __init__(self, ruta_db: str):
        self.ruta_db = ruta_db
    
    def ejecutar_consulta(self, consulta: str, parametros: tuple = None) -> List[Dict[str, Any]]:
        """Ejecutar consulta y retornar resultados como lista de diccionarios"""
        try:
            with sqlite3.connect(self.ruta_db) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                if parametros:
                    cursor.execute(consulta, parametros)
                else:
                    cursor.execute(consulta)
                
                return [dict(row) for row in cursor.fetchall()]
        
        except Exception as e:
            raise Exception(f"Error ejecutando consulta: {e}")
    
    def obtener_estadisticas_tabla(self, tabla: str) -> Dict[str, Any]:
        """Obtener estadísticas detalladas de una tabla"""
        try:
            # Información básica
            consulta_info = f"PRAGMA table_info({tabla})"
            columnas_info = self.ejecutar_consulta(consulta_info)
            
            consulta_count = f"SELECT COUNT(*) as total FROM {tabla}"
            resultado_count = self.ejecutar_consulta(consulta_count)
            total_registros = resultado_count[0]['total']
            
            estadisticas = {
                'tabla': tabla,
                'total_registros': total_registros,
                'total_columnas': len(columnas_info),
                'columnas': [],
                'estadisticas_por_columna': {}
            }
            
            # Información por columna
            for col_info in columnas_info:
                nombre_col = col_info['name']
                tipo_col = col_info['type']
                
                estadisticas['columnas'].append({
                    'nombre': nombre_col,
                    'tipo': tipo_col,
                    'not_null': bool(col_info['notnull']),
                    'pk': bool(col_info['pk'])
                })
                
                # Estadísticas específicas de la columna
                try:
                    consulta_col = f"""
                        SELECT 
                            COUNT(*) as total,
                            COUNT("{nombre_col}") as no_nulos,
                            COUNT(DISTINCT "{nombre_col}") as valores_unicos
                        FROM {tabla}
                    """
                    resultado_col = self.ejecutar_consulta(consulta_col)
                    
                    if resultado_col:
                        stats_col = resultado_col[0]
                        estadisticas['estadisticas_por_columna'][nombre_col] = {
                            'total_valores': stats_col['total'],
                            'valores_no_nulos': stats_col['no_nulos'],
                            'valores_nulos': stats_col['total'] - stats_col['no_nulos'],
                            'valores_unicos': stats_col['valores_unicos'],
                            'porcentaje_completitud': (stats_col['no_nulos'] / stats_col['total'] * 100) if stats_col['total'] > 0 else 0
                        }
                except Exception as e:
                    print(f"Error obteniendo estadísticas para columna {nombre_col}: {e}")
            
            return estadisticas
            
        except Exception as e:
            raise Exception(f"Error obteniendo estadísticas de tabla {tabla}: {e}")

# Funciones utilitarias globales
def convertir_tamaño_archivo(tamaño_bytes: int) -> str:
    """Convertir tamaño en bytes a formato legible"""
    for unidad in ['B', 'KB', 'MB', 'GB', 'TB']:
        if tamaño_bytes < 1024.0:
            return f"{tamaño_bytes:.1f} {unidad}"
        tamaño_bytes /= 1024.0
    return f"{tamaño_bytes:.1f} PB"

def tiempo_transcurrido(inicio: datetime, fin: datetime = None) -> str:
    """Formatear tiempo transcurrido de manera legible"""
    if fin is None:
        fin = datetime.now()
    
    delta = fin - inicio
    
    dias = delta.days
    horas, resto = divmod(delta.seconds, 3600)
    minutos, segundos = divmod(resto, 60)
    
    partes = []
    
    if dias > 0:
        partes.append(f"{dias}d")
    if horas > 0:
        partes.append(f"{horas}h")
    if minutos > 0:
        partes.append(f"{minutos}m")
    if segundos > 0 or not partes:
        partes.append(f"{segundos}s")
    
    return " ".join(partes)

def generar_timestamp(formato: str = "%Y%m%d_%H%M%S") -> str:
    """Generar timestamp en formato especificado"""
    return datetime.now().strftime(formato)

def verificar_dependencias(dependencias: List[str]) -> Dict[str, bool]:
    """Verificar si las dependencias están disponibles"""
    resultado = {}
    
    for dep in dependencias:
        try:
            __import__(dep)
            resultado[dep] = True
        except ImportError:
            resultado[dep] = False
    
    return resultado

# Decorador para medir tiempo de ejecución
def cronometrar(func):
    """Decorador para medir tiempo de ejecución de funciones"""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = datetime.now()
        try:
            resultado = func(*args, **kwargs)
            fin = datetime.now()
            duracion = fin - inicio
            print(f"⏱️ {func.__name__} ejecutado en {tiempo_transcurrido(inicio, fin)}")
            return resultado
        except Exception as e:
            fin = datetime.now()
            duracion = fin - inicio
            print(f"❌ {func.__name__} falló después de {tiempo_transcurrido(inicio, fin)}: {e}")
            raise
    
    return wrapper

# Ejemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logger = configurar_logging("INFO", "debug_utilities.log")
    
    # Ejemplo de estadísticas
    stats = EstadisticasProcesamiento(total_registros=100)
    stats.registros_procesados = 95
    stats.agregar_error("Error de ejemplo")
    stats.finalizar()
    
    print(stats.reporte())
    
    # Ejemplo de formateo
    formatter = FormateadorSalida()
    print(formatter.titulo("HERRAMIENTAS DE IA - HUV"))
    print(formatter.progreso(75, 100))
    
    # Ejemplo de validación
    validator = ValidadorDatos()
    print(f"IHQ250001 válido: {validator.validar_numero_peticion('IHQ250001')}")
    print(f"12345678 válido: {validator.validar_identificacion('12345678')}")