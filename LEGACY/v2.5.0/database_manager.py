# database_manager.py
import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional
import pandas as pd

# Configuración
DB_FILE = "huv_oncologia.db"
TABLE_NAME = "informes_ihq"

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Crea la base de datos y la tabla si no existen."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Crear tabla con esquema completo y mejorado
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "N. peticion (0. Numero de biopsia)" TEXT UNIQUE NOT NULL,
            "Hospitalizado" TEXT, "Sede" TEXT, "EPS" TEXT, "Servicio" TEXT,
            "Médico tratante" TEXT, "Especialidad" TEXT, "Ubicación" TEXT, "N. Autorizacion" TEXT,
            "Identificador Unico" TEXT, "Datos Clinicos" TEXT, "Fecha ordenamiento" TEXT,
            "Tipo de documento" TEXT, "N. de identificación" TEXT, "Primer nombre" TEXT,
            "Segundo nombre" TEXT, "Primer apellido" TEXT, "Segundo apellido" TEXT,
            "Fecha de nacimiento" TEXT, "Edad" TEXT, "Genero" TEXT, "Número celular" TEXT,
            "Direccion de correo electronico" TEXT, "Direccion de correo electronico 2" TEXT,
            "Contacto de emergencia" TEXT, "Departamento" TEXT, "Teléfono del contacto" TEXT,
            "Municipio" TEXT, "N. muestra" TEXT, "CUPS" TEXT,
            "Tipo de examen (4, 12, Metodo de obtención de la muestra, factor de certeza para el diagnóstico)" TEXT,
            "Procedimiento (11. Tipo de estudio para el diagnóstico)" TEXT,
            "Organo (1. Muestra enviada a patología)" TEXT, "Tarifa" TEXT, "Valor" TEXT,
            "Copago" TEXT, "Descuento" TEXT, "Fecha de ingreso (2. Fecha de la muestra)" TEXT,
            "Fecha finalizacion (3. Fecha del informe)" TEXT, "Usuario finalizacion" TEXT,
            "Usuario asignacion micro" TEXT, "Fecha asignacion micro" TEXT, "Malignidad" TEXT,
            "Condicion" TEXT, "Descripcion macroscopica" TEXT,
            "Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)" TEXT,
            "Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)" TEXT,
            "Diagnostico Principal" TEXT, "Comentario" TEXT, "Informe adicional" TEXT,
            "Congelaciones /Otros estudios" TEXT, "Liquidos (5 Tipo histologico)" TEXT,
            "Citometria de flujo (5 Tipo histologico)" TEXT, "Hora Desc. macro" TEXT, "Responsable macro" TEXT,
            "IHQ_HER2" TEXT, "IHQ_KI-67" TEXT, "IHQ_RECEPTOR_ESTROGENO" TEXT,
            "IHQ_RECEPTOR_PROGESTAGENOS" TEXT, "IHQ_PDL-1" TEXT, "IHQ_ESTUDIOS_SOLICITADOS" TEXT,
            "IHQ_P16_ESTADO" TEXT, "IHQ_P16_PORCENTAJE" TEXT, "IHQ_ORGANO" TEXT,
            fecha_procesado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Crear índices para mejorar performance
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_peticion ON {TABLE_NAME}("N. peticion (0. Numero de biopsia)")')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_fecha_procesado ON {TABLE_NAME}(fecha_procesado)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_malignidad ON {TABLE_NAME}(Malignidad)')
        cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_servicio ON {TABLE_NAME}(Servicio)')
        
        conn.commit()
        logger.info(f"Base de datos inicializada correctamente: {DB_FILE}")
        
    except sqlite3.Error as e:
        logger.error(f"Error inicializando base de datos: {e}")
        raise
    finally:
        if conn:
            conn.close()

def save_records(records: List[Dict]) -> int:
    """Guarda una lista de registros (diccionarios) en la base de datos.
    
    Args:
        records: Lista de diccionarios con los datos a guardar
        
    Returns:
        int: Número de registros guardados exitosamente
    """
    if not records:
        logger.warning("No se proporcionaron registros para guardar")
        return 0
    
    saved_count = 0
    skipped_count = 0
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Obtener columnas de la tabla
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        table_columns = [col[1] for col in cursor.fetchall() if col[1] not in ('id', 'fecha_procesado', 'fecha_actualizacion')]
        
        for record in records:
            try:
                # Validar que el registro tenga al menos el número de petición
                peticion = record.get("N. peticion (0. Numero de biopsia)", "")
                if not peticion or peticion.strip() == "":
                    logger.warning("Registro sin número de petición válido, omitiendo")
                    skipped_count += 1
                    continue

                # Verificar si ya existe (usando UPSERT)
                cursor.execute(f"SELECT id FROM {TABLE_NAME} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", (peticion,))
                existing = cursor.fetchone()
                
                if existing:
                    # Actualizar registro existente
                    values = [record.get(col, '') for col in table_columns]
                    set_clause = ', '.join([f'"{col}" = ?' for col in table_columns])
                    set_clause += ', fecha_actualizacion = CURRENT_TIMESTAMP'
                    
                    cursor.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", 
                                 values + [peticion])
                    logger.info(f"Registro actualizado: {peticion}")
                else:
                    # Insertar nuevo registro
                    values = [record.get(col, '') for col in table_columns]
                    placeholders = ', '.join(['?'] * len(table_columns))
                    column_names = ', '.join([f'"{col}"' for col in table_columns])
                    
                    cursor.execute(f"INSERT INTO {TABLE_NAME} ({column_names}) VALUES ({placeholders})", values)
                    logger.info(f"Registro insertado: {peticion}")
                
                saved_count += 1
                
            except sqlite3.Error as e:
                logger.error(f"Error procesando registro {peticion}: {e}")
                skipped_count += 1
                continue

        conn.commit()
        logger.info(f"Guardado completado: {saved_count} registros guardados, {skipped_count} omitidos")
        
    except sqlite3.Error as e:
        logger.error(f"Error en la base de datos: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        raise
    finally:
        if conn:
            conn.close()
    
    return saved_count


def get_all_records_as_dataframe() -> pd.DataFrame:
    """Obtiene todos los registros de la BD y los devuelve como un DataFrame de Pandas.
    
    Returns:
        pd.DataFrame: DataFrame con todos los registros de la base de datos
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME} ORDER BY fecha_procesado DESC", conn)
        logger.info(f"Cargados {len(df)} registros de la base de datos")
        return df
        
    except sqlite3.Error as e:
        logger.error(f"Error consultando la base de datos: {e}")
        return pd.DataFrame()  # Retorna DataFrame vacío en caso de error
    except Exception as e:
        logger.error(f"Error inesperado consultando datos: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()


def get_statistics() -> Dict:
    """Obtiene estadísticas básicas de la base de datos.
    
    Returns:
        Dict: Diccionario con estadísticas básicas
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        stats = {}
        
        # Total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        stats['total_registros'] = cursor.fetchone()[0]
        
        # Registros por malignidad
        cursor.execute(f"SELECT Malignidad, COUNT(*) FROM {TABLE_NAME} GROUP BY Malignidad")
        stats['por_malignidad'] = dict(cursor.fetchall())
        
        # Últimos registros procesados
        cursor.execute(f"SELECT DATE(fecha_procesado), COUNT(*) FROM {TABLE_NAME} GROUP BY DATE(fecha_procesado) ORDER BY DATE(fecha_procesado) DESC LIMIT 7")
        stats['ultimos_7_dias'] = dict(cursor.fetchall())
        
        return stats
        
    except sqlite3.Error as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return {}
    finally:
        if conn:
            conn.close()


def validate_database_integrity() -> bool:
    """Valida la integridad de la base de datos.
    
    Returns:
        bool: True si la base de datos es válida, False en caso contrario
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Verificar integridad de la base de datos
        cursor.execute("PRAGMA integrity_check")
        integrity_result = cursor.fetchone()[0]
        
        if integrity_result != "ok":
            logger.error(f"Problema de integridad en la base de datos: {integrity_result}")
            return False
        
        # Verificar que la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (TABLE_NAME,))
        if not cursor.fetchone():
            logger.error(f"Tabla {TABLE_NAME} no encontrada")
            return False
        
        logger.info("Validación de integridad de la base de datos exitosa")
        return True
        
    except sqlite3.Error as e:
        logger.error(f"Error validando integridad: {e}")
        return False
    finally:
        if conn:
            conn.close()