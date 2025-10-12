# database_manager.py
import sqlite3
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
import pandas as pd

# Configuración
# Construir ruta absoluta a la base de datos
# CORREGIDO: Detectar si estamos en un ejecutable empaquetado (PyInstaller)
def get_base_path():
    """
    Retorna la ruta base de la aplicación.
    Si está empaquetado con PyInstaller, usa el directorio del ejecutable.
    Si es desarrollo, usa el directorio del script.
    """
    if getattr(sys, 'frozen', False):
        # Estamos ejecutando como .exe empaquetado
        # sys.executable es la ruta al .exe
        return Path(sys.executable).parent
    else:
        # Estamos ejecutando como script Python
        return Path(__file__).resolve().parent.parent

DB_FILE = str(get_base_path() / "data" / "huv_oncologia_NUEVO.db")
TABLE_NAME = "informes_ihq"

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ======================== CONSTANTES HUV ========================
# Movido desde: config/huv_constants.py

# Configuración hospitalaria
HUV_CONFIG = {
    'hospital_name': 'HOSPITAL UNIVERSITARIO DEL VALLE',
    'hospital_code': 'HUV',
    'sede_default': 'PRINCIPAL',
    'departamento_default': 'VALLE DEL CAUCA',
    'municipio_default': 'CALI',
    'tipo_documento_default': 'CC',
    'tarifa_default': 'GENERAL',
    'valor_default': 0.0,
}

# Códigos CUPS y procedimientos
CUPS_CODES = {
    'AUTOPSIA': '898301',
    'INMUNOHISTOQUIMICA': '898807',
    'BIOPSIA': '898201',
    'REVISION': '898806',
    'CITOLOGIA': '898241',
    'CONGELACION': '898242',
}

PROCEDIMIENTOS = {
    '898301': '898301 Autopsia completa',
    '898807': '898807 Estudio anatomopatologico de marcacion inmunohistoquimica basica (especifico)',
    '898201': '898201 Estudio de coloracion basica en especimen de reconocimiento',
    '898806': '898806 Verificacion integral con preparacion de material de rutina',
}

# Especialidades por servicio
ESPECIALIDADES_SERVICIOS = {
    'UCI': 'MEDICO INTENSIVISTA',
    'GINECOLOGIA': 'GINECOLOGIA Y OBSTETRICIA',
    'GINECOLOGIA ONCOLOGICA': 'GINECOLOGIA ONCOLOGICA',
    'ALTO RIESGO OBSTETRICO': 'GINECOLOGIA ONCOLOGICA',
    'MEDICINA': 'MEDICINA GENERAL',
    'URGENCIAS': 'MEDICINA DE URGENCIAS',
    'NEONATOLOGIA': 'NEONATOLOGIA',
    'PEDIATRIA': 'PEDIATRA',
}

# Umbrales de confiabilidad estadística
CONFIDENCE_THRESHOLDS = {
    'alto': 20,      # 20+ registros = alta confiabilidad
    'medio': 10,     # 10-19 registros = confiabilidad media
    'bajo': 5        # 5-9 registros = baja confiabilidad
}

#########################################
# NUEVO ESQUEMA (columnas eliminadas)   #
#########################################

# Columnas eliminadas según solicitud del usuario:
# "Ubicación", "Identificador Unico", "Número celular", "Direccion de correo electronico",
# "Direccion de correo electronico 2", "Contacto de emergencia", "Teléfono del contacto",
# "Valor", "Copago", "Descuento", "Usuario asignacion micro", "Fecha asignacion micro",
# "Condicion", "Comentario", "Informe adicional".

REMOVED_COLUMNS = {
    "Ubicación", "Identificador Unico", "Número celular", "Direccion de correo electronico",
    "Direccion de correo electronico 2", "Contacto de emergencia", "Teléfono del contacto",
    "Valor", "Copago", "Descuento", "Usuario asignacion micro", "Fecha asignacion micro",
    "Condicion", "Comentario", "Informe adicional", "Tarifa", "Comentario diagnostico"  # Tarifa eliminada y reemplazada por Fecha de toma; Comentario diagnostico retirado
}

NEW_TABLE_COLUMNS_ORDER: List[str] = [
    # Mantener orden lógico (id se gestiona aparte)
    "N. peticion (0. Numero de biopsia)", "Hospitalizado", "Sede", "EPS", "Servicio",
    "Médico tratante", "Especialidad", "Datos Clinicos",
    "Tipo de documento", "N. de identificación", "Primer nombre", "Segundo nombre",
    "Primer apellido", "Segundo apellido", "Fecha de nacimiento", "Edad", "Genero",
    "Departamento", "Municipio", "CUPS",
    "Tipo de examen (4, 12, Metodo de obtención de la muestra, factor de certeza para el diagnóstico)",
    "Procedimiento (11. Tipo de estudio para el diagnóstico)",
    "Organo (1. Muestra enviada a patología)",
    "Fecha de toma (1. Fecha de la toma)",  # Nueva columna reemplaza a Tarifa
    "Fecha de ingreso (2. Fecha de la muestra)", "Fecha Informe",
    "Usuario finalizacion", "Malignidad", "Descripcion macroscopica",
    "Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)",
    "Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)",
    "Diagnostico Principal", "Factor pronostico", "Congelaciones /Otros estudios", "Liquidos (5 Tipo histologico)",
    "Citometria de flujo (5 Tipo histologico)", "Hora Desc. macro", "Responsable macro",
    # Biomarcadores principales
    "IHQ_HER2", "IHQ_KI-67", "IHQ_RECEPTOR_ESTROGENO", "IHQ_RECEPTOR_PROGESTERONOS", "IHQ_PDL-1",
    "IHQ_ESTUDIOS_SOLICITADOS", "IHQ_P16_ESTADO", "IHQ_P16_PORCENTAJE", "IHQ_P40_ESTADO", "IHQ_ORGANO",
    # Biomarcadores agregados v4.0
    "IHQ_CK7", "IHQ_CK20", "IHQ_CDX2", "IHQ_EMA", "IHQ_GATA3", "IHQ_SOX10",
    # Biomarcadores adicionales v4.1 (extracción completa)
    "IHQ_P53", "IHQ_TTF1", "IHQ_S100", "IHQ_VIMENTINA", "IHQ_CHROMOGRANINA", "IHQ_SYNAPTOPHYSIN", "IHQ_MELAN_A",
    # Marcadores CD
    "IHQ_CD3", "IHQ_CD5", "IHQ_CD10", "IHQ_CD20", "IHQ_CD30", "IHQ_CD34", "IHQ_CD38",
    "IHQ_CD45", "IHQ_CD56", "IHQ_CD61", "IHQ_CD68", "IHQ_CD117", "IHQ_CD138"
]

def _create_table_if_not_exists(cursor: sqlite3.Cursor):
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            "N. peticion (0. Numero de biopsia)" TEXT UNIQUE NOT NULL,
            "Hospitalizado" TEXT, "Sede" TEXT, "EPS" TEXT, "Servicio" TEXT,
            "Médico tratante" TEXT, "Especialidad" TEXT,
            "Datos Clinicos" TEXT,
            "Tipo de documento" TEXT, "N. de identificación" TEXT, "Primer nombre" TEXT,
            "Segundo nombre" TEXT, "Primer apellido" TEXT, "Segundo apellido" TEXT,
            "Fecha de nacimiento" TEXT, "Edad" TEXT, "Genero" TEXT,
            "Departamento" TEXT, "Municipio" TEXT, "CUPS" TEXT,
            "Tipo de examen (4, 12, Metodo de obtención de la muestra, factor de certeza para el diagnóstico)" TEXT,
            "Procedimiento (11. Tipo de estudio para el diagnóstico)" TEXT,
            "Organo (1. Muestra enviada a patología)" TEXT,
            "Fecha de toma (1. Fecha de la toma)" TEXT,
            "Fecha de ingreso (2. Fecha de la muestra)" TEXT,
            "Fecha Informe" TEXT, "Usuario finalizacion" TEXT,
            "Malignidad" TEXT, "Descripcion macroscopica" TEXT,
            "Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)" TEXT,
            "Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)" TEXT,
            "Diagnostico Principal" TEXT,
            "Factor pronostico" TEXT,
            "Congelaciones /Otros estudios" TEXT, "Liquidos (5 Tipo histologico)" TEXT,
            "Citometria de flujo (5 Tipo histologico)" TEXT, "Hora Desc. macro" TEXT, "Responsable macro" TEXT,
            "IHQ_HER2" TEXT, "IHQ_KI-67" TEXT, "IHQ_RECEPTOR_ESTROGENO" TEXT,
            "IHQ_RECEPTOR_PROGESTERONOS" TEXT, "IHQ_PDL-1" TEXT, "IHQ_ESTUDIOS_SOLICITADOS" TEXT,
            "IHQ_P16_ESTADO" TEXT, "IHQ_P16_PORCENTAJE" TEXT, "IHQ_P40_ESTADO" TEXT, "IHQ_ORGANO" TEXT,
            "IHQ_CK7" TEXT, "IHQ_CK20" TEXT, "IHQ_CDX2" TEXT, "IHQ_EMA" TEXT, "IHQ_GATA3" TEXT, "IHQ_SOX10" TEXT,
            "IHQ_P53" TEXT, "IHQ_TTF1" TEXT, "IHQ_S100" TEXT, "IHQ_VIMENTINA" TEXT,
            "IHQ_CHROMOGRANINA" TEXT, "IHQ_SYNAPTOPHYSIN" TEXT, "IHQ_MELAN_A" TEXT,
            "IHQ_CD3" TEXT, "IHQ_CD5" TEXT, "IHQ_CD10" TEXT, "IHQ_CD20" TEXT, "IHQ_CD30" TEXT,
            "IHQ_CD34" TEXT, "IHQ_CD38" TEXT, "IHQ_CD45" TEXT, "IHQ_CD56" TEXT, "IHQ_CD61" TEXT,
            "IHQ_CD68" TEXT, "IHQ_CD117" TEXT, "IHQ_CD138" TEXT,
            "Fecha Ingreso Base de Datos" TIMESTAMP DEFAULT (datetime('now', 'localtime'))
        )
    """)

def _needs_migration(cursor: sqlite3.Cursor) -> bool:
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    existing_cols = {row[1] for row in cursor.fetchall()}
    return any(col in existing_cols for col in REMOVED_COLUMNS)

def _migrate_schema(conn: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Realiza migración eliminando columnas obsoletas sin perder datos restantes."""
    if not _needs_migration(cursor):
        return
    logger.info("Iniciando migración de esquema: eliminando columnas obsoletas…")

    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    current_cols = [row[1] for row in cursor.fetchall()]  # orden actual

    # Columnas destino (manteniendo id si existe)
    destination_cols = [c for c in NEW_TABLE_COLUMNS_ORDER if c in current_cols]

    # Crear tabla temporal
    temp_table = f"{TABLE_NAME}_new"
    cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")

    # Construir definición de columnas (idéntica a _create_table_if_not_exists pero con nombre temporal)
    col_defs: List[str] = []
    for col in NEW_TABLE_COLUMNS_ORDER:
        # Definiciones (todas TEXT salvo clave y timestamps)
        if col == "N. peticion (0. Numero de biopsia)":
            col_defs.append(f'"{col}" TEXT UNIQUE NOT NULL')
        else:
            col_defs.append(f'"{col}" TEXT')
    col_defs.append('"Fecha Ingreso Base de Datos" TIMESTAMP DEFAULT (datetime(\'now\', \'localtime\'))')

    cursor.execute(f"""
        CREATE TABLE {temp_table} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {', '.join(col_defs)}
        )
    """)

    # Copiar datos (id + columnas destino que existan)
    select_cols = ["id"] + destination_cols + [c for c in ["Fecha Ingreso Base de Datos"] if c in current_cols]
    insert_cols = ["id"] + destination_cols + ["Fecha Ingreso Base de Datos"]
    cursor.execute(
        f"INSERT INTO {temp_table} ({', '.join(f'"{c}"' for c in insert_cols)}) "
        f"SELECT {', '.join(f'"{c}"' for c in select_cols)} FROM {TABLE_NAME}"
    )

    # Reemplazar tabla original
    cursor.execute(f"DROP TABLE {TABLE_NAME}")
    cursor.execute(f"ALTER TABLE {temp_table} RENAME TO {TABLE_NAME}")

    # Recrear índices
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_peticion ON {TABLE_NAME}("N. peticion (0. Numero de biopsia)")')
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_fecha_ingreso ON {TABLE_NAME}("Fecha Ingreso Base de Datos")')
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_malignidad ON {TABLE_NAME}(Malignidad)')
    cursor.execute(f'CREATE INDEX IF NOT EXISTS idx_servicio ON {TABLE_NAME}(Servicio)')

    conn.commit()
    logger.info("Migración completada correctamente.")

def _add_new_biomarker_columns(conn: sqlite3.Connection, cursor: sqlite3.Cursor):
    """Agrega las nuevas columnas de biomarcadores si no existen."""
    new_biomarkers = [
        # v4.0
        "IHQ_CK7", "IHQ_CK20", "IHQ_CDX2", "IHQ_EMA", "IHQ_GATA3", "IHQ_SOX10",
        # v4.1 - Biomarcadores adicionales
        "IHQ_P53", "IHQ_TTF1", "IHQ_S100", "IHQ_VIMENTINA",
        "IHQ_CHROMOGRANINA", "IHQ_SYNAPTOPHYSIN", "IHQ_MELAN_A",
        # Marcadores CD
        "IHQ_CD3", "IHQ_CD5", "IHQ_CD10", "IHQ_CD20", "IHQ_CD30", "IHQ_CD34",
        "IHQ_CD38", "IHQ_CD45", "IHQ_CD56", "IHQ_CD61", "IHQ_CD68", "IHQ_CD117", "IHQ_CD138"
    ]

    # Verificar qué columnas ya existen
    cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
    existing_cols = {row[1] for row in cursor.fetchall()}

    added_count = 0
    for biomarker in new_biomarkers:
        if biomarker not in existing_cols:
            try:
                cursor.execute(f'ALTER TABLE {TABLE_NAME} ADD COLUMN "{biomarker}" TEXT')
                logger.info(f"✅ Agregada columna: {biomarker}")
                added_count += 1
            except sqlite3.OperationalError as e:
                if "duplicate column name" not in str(e).lower():
                    logger.warning(f"⚠️ Error agregando columna {biomarker}: {e}")

    if added_count > 0:
        logger.info(f"✅ Total de nuevas columnas agregadas: {added_count}")

    conn.commit()

def init_db():
    """Crea o migra la base de datos al nuevo esquema sin columnas obsoletas."""
    conn: Optional[sqlite3.Connection] = None
    try:
        # CORREGIDO: Crear la carpeta data/ si no existe
        db_dir = Path(DB_FILE).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Carpeta de base de datos verificada: {db_dir}")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        _create_table_if_not_exists(cursor)  # Garantiza existencia
        conn.commit()
        _migrate_schema(conn, cursor)
        
        # Agregar nuevas columnas de biomarcadores
        _add_new_biomarker_columns(conn, cursor)
        
        logger.info(f"Base de datos preparada correctamente: {DB_FILE}")
    except sqlite3.Error as e:
        logger.error(f"Error inicializando/migrando base de datos: {e}")
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass

def get_registro_by_peticion(numero_peticion: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene un registro de la BD por número de petición

    Args:
        numero_peticion: Número de petición IHQ

    Returns:
        Dict con el registro o None si no existe
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            f'SELECT * FROM {TABLE_NAME} WHERE "N. peticion (0. Numero de biopsia)" = ?',
            (numero_peticion,)
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    except Exception as e:
        logger.error(f"Error obteniendo registro {numero_peticion}: {e}")
        return None


def update_campo_registro(
    numero_peticion: str,
    campo: str,
    valor: Any
) -> bool:
    """
    Actualiza un campo específico de un registro en la BD

    Args:
        numero_peticion: Número de petición IHQ
        campo: Nombre del campo a actualizar
        valor: Nuevo valor

    Returns:
        True si se actualizó correctamente
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Verificar que el campo existe
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        columnas = [row[1] for row in cursor.fetchall()]

        if campo not in columnas:
            logger.warning(f"Campo '{campo}' no existe en la tabla")
            conn.close()
            return False

        # Actualizar
        query = f'UPDATE {TABLE_NAME} SET "{campo}" = ? WHERE "N. peticion (0. Numero de biopsia)" = ?'
        cursor.execute(query, (valor, numero_peticion))

        conn.commit()
        conn.close()

        logger.info(f"✅ Campo '{campo}' actualizado para {numero_peticion}")
        return True

    except Exception as e:
        logger.error(f"Error actualizando campo {campo}: {e}")
        return False


def smart_update_records(records: List[Dict[str, Any]]) -> int:
    """
    Actualiza registros de forma inteligente, preservando campos que ya tienen datos válidos.
    Solo actualiza campos que están vacíos, son None, o contienen 'NO ENCONTRADO'.

    Args:
        records: Lista de diccionarios con los datos a actualizar

    Returns:
        int: Número de registros actualizados exitosamente
    """
    if not records:
        logger.warning("No se proporcionaron registros para actualizar")
        return 0
    
    updated_count = 0
    skipped_count = 0
    
    # Campos de biomarcadores que NO deben sobrescribirse si ya tienen datos
    biomarcador_fields = {
        'IHQ_P16_ESTADO', 'IHQ_P40_ESTADO', 'IHQ_HER2', 'IHQ_KI-67', 
        'IHQ_RECEPTOR_ESTROGENO', 'IHQ_RECEPTOR_PROGESTERONOS', 'IHQ_PDL-1',
        'IHQ_P16_PORCENTAJE', 'IHQ_ESTUDIOS_SOLICITADOS', 'IHQ_ORGANO',
        # Campos diagnósticos adicionales
        'Congelaciones /Otros estudios', 'Liquidos (5 Tipo histologico)', 
        'Citometria de flujo (5 Tipo histologico)'
    }

    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Obtener columnas de la tabla
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        table_columns: List[str] = [col[1] for col in cursor.fetchall() if col[1] not in ('id', 'Fecha Ingreso Base de Datos')]

        for record in records:
            peticion: str = ""
            try:
                peticion = str(record.get("N. peticion (0. Numero de biopsia)", "") or "").strip()
                if not peticion:
                    logger.warning("Registro sin número de petición válido, omitiendo")
                    skipped_count += 1
                    continue

                # Obtener registro actual
                cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", (peticion,))
                existing_row = cursor.fetchone()
                
                if not existing_row:
                    logger.warning(f"Registro {peticion} no existe, omitiendo")
                    skipped_count += 1
                    continue
                
                # Obtener nombres de columnas
                cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
                col_info = cursor.fetchall()
                col_names = [col[1] for col in col_info]
                
                # Convertir fila actual a diccionario
                current_data = dict(zip(col_names, existing_row))
                
                # Preparar campos a actualizar (solo los que están realmente vacíos)
                fields_to_update = []
                values_to_update = []
                
                for col in table_columns:
                    new_value = record.get(col, '')
                    current_value = current_data.get(col, '')
                    
                    # Decidir si actualizar este campo
                    should_update = False
                    
                    # Para biomarcadores: solo actualizar si el campo actual está realmente vacío
                    if col in biomarcador_fields:
                        if (not current_value or current_value.strip() == '' or 
                            current_value == 'NO ENCONTRADO' or current_value == 'SIN DATO'):
                            if (new_value and new_value.strip() != '' and 
                                new_value != 'NO ENCONTRADO' and new_value != 'SIN DATO'):
                                should_update = True
                    else:
                        # Para otros campos: actualizar si está vacío o tiene datos incorrectos
                        if (not current_value or current_value.strip() == '' or 
                            current_value == 'NO ENCONTRADO' or current_value == 'SIN DATO'):
                            if (new_value and new_value.strip() != '' and 
                                new_value != 'NO ENCONTRADO' and new_value != 'SIN DATO'):
                                should_update = True
                    
                    if should_update:
                        fields_to_update.append(f'"{col}" = ?')
                        values_to_update.append(new_value)
                
                # Solo actualizar si hay campos que cambiar
                if fields_to_update:
                    set_clause = ', '.join(fields_to_update)
                    cursor.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", 
                                 values_to_update + [peticion])
                    logger.info(f"Registro actualizado inteligentemente: {peticion} ({len(fields_to_update)} campos)")
                    updated_count += 1
                else:
                    logger.info(f"Registro {peticion} ya está completo, no necesita actualización")
                
            except sqlite3.Error as e:
                logger.error(f"Error procesando registro {peticion if peticion else '?'}: {e}")
                skipped_count += 1
                continue

        conn.commit()
        logger.info(f"Actualización inteligente completada: {updated_count} registros actualizados, {skipped_count} omitidos")
        return updated_count

    except Exception as e:
        logger.error(f"Error en actualización inteligente: {e}")
        if conn:
            conn.rollback()
        return 0
    finally:
        if conn:
            conn.close()


def _apply_default_values(record: Dict[str, Any]) -> Dict[str, Any]:
    """Aplica valores por defecto 'N/A' a campos vacíos o nulos.
    
    Args:
        record: Diccionario con los datos del registro
        
    Returns:
        Dict[str, Any]: Registro con valores por defecto aplicados
    """
    cleaned_record = {}
    for key, value in record.items():
        # Aplicar N/A si el valor está vacío, es None, o solo tiene espacios
        if value is None or str(value).strip() == '':
            cleaned_record[key] = 'N/A'
        else:
            cleaned_record[key] = value
    return cleaned_record


def _normalize_column_name(column_name: str) -> str:
    """Normaliza nombres de columnas para mapeo correcto entre registro y BD.

    Args:
        column_name: Nombre de columna de la BD

    Returns:
        str: Nombre normalizado para buscar en el registro
    """
    # Mapeo específico de nombres de columnas conocidos
    column_mappings = {
        'Descripcion macroscopica': 'descripcion_macroscopica',
        'Descripcion microscopica (8,9, 10,12,. Invasión linfovascular y perineural, indice mitótico/Ki67, Inmunohistoquímica, tamaño tumoral)': 'descripcion_microscopica',
        'Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)': 'diagnostico_final',
        'N. de identificación': 'numero_identificacion',
        'N. peticion (0. Numero de biopsia)': 'numero_peticion',  # FIX: Mapeo crítico faltante
        'Médico tratante': 'medico_tratante',
        # CORREGIDO: Agregar múltiples variantes de mapeo para órganos
        'Organo (1. Muestra enviada a patología)': 'organo',
        'IHQ_ORGANO': 'ihq_organo',  # NUEVO: Órgano extraído del diagnóstico
        'organo': 'organo',  # Fallback directo
        'ihq_organo': 'ihq_organo',  # Fallback directo
        'Factor pronostico': 'factor_pronostico',
        'Diagnostico Principal': 'diagnostico_principal'
    }
    
    # Si hay un mapeo específico, usarlo
    if column_name in column_mappings:
        return column_mappings[column_name]
    
    # Si no, normalizar el nombre: minúsculas y quitar caracteres especiales
    normalized = column_name.lower()
    normalized = normalized.replace(' ', '_')
    normalized = normalized.replace('(', '').replace(')', '')
    normalized = normalized.replace('.', '').replace(',', '')
    normalized = normalized.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    
    return normalized


def save_records(records: List[Dict[str, Any]]) -> int:
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

    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Obtener columnas de la tabla (excluyendo claves y timestamps gestionados automáticamente)
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        table_columns: List[str] = [col[1] for col in cursor.fetchall() if col[1] not in ('id', 'Fecha Ingreso Base de Datos')]

        for record in records:
            peticion: str = ""
            try:
                # Validar que el registro tenga al menos el número de petición
                # FIX: Usar mapeo normalizado para encontrar el número de petición
                peticion_col = "N. peticion (0. Numero de biopsia)"
                normalized_peticion_col = _normalize_column_name(peticion_col)
                peticion = str(record.get(normalized_peticion_col, record.get(peticion_col, "")) or "").strip()
                if not peticion:
                    logger.warning("Registro sin número de petición válido, omitiendo")
                    skipped_count += 1
                    continue

                # Aplicar valores por defecto N/A a campos vacíos
                record = _apply_default_values(record)

                # Verificar si ya existe (usando UPSERT)
                cursor.execute(f"SELECT id FROM {TABLE_NAME} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", (peticion,))
                existing = cursor.fetchone()
                
                if existing:
                    # Actualizar registro existente
                    values = []
                    for col in table_columns:
                        # Buscar el valor correcto usando mapeo de nombres
                        normalized_col = _normalize_column_name(col)
                        value = record.get(normalized_col, record.get(col, 'N/A'))
                        values.append(value)
                    
                    set_clause = ', '.join([f'"{col}" = ?' for col in table_columns])
                    
                    cursor.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE \"N. peticion (0. Numero de biopsia)\" = ?", 
                                 values + [peticion])
                    logger.info(f"Registro actualizado: {peticion}")
                else:
                    # Insertar nuevo registro
                    values = []
                    for col in table_columns:
                        # Buscar el valor correcto usando mapeo de nombres
                        normalized_col = _normalize_column_name(col)
                        value = record.get(normalized_col, record.get(col, 'N/A'))
                        values.append(value)
                    
                    placeholders = ', '.join(['?'] * len(table_columns))
                    column_names = ', '.join([f'"{col}"' for col in table_columns])
                    
                    cursor.execute(f"INSERT INTO {TABLE_NAME} ({column_names}) VALUES ({placeholders})", values)
                    logger.info(f"Registro insertado: {peticion}")
                
                saved_count += 1
                
            except sqlite3.Error as e:
                logger.error(f"Error procesando registro {peticion if peticion else '?'}: {e}")
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
    # Garantizar que la tabla exista antes de consultar (evita 'no such table')
    try:
        init_db()
    except Exception as e:
        logger.error(f"No se pudo inicializar la base de datos antes de la consulta: {e}")
        return pd.DataFrame()
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_FILE)
        df = pd.read_sql_query(f'SELECT * FROM {TABLE_NAME} ORDER BY "Fecha Ingreso Base de Datos" DESC', conn)
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


def get_statistics() -> Dict[str, Any]:
    """Obtiene estadísticas básicas de la base de datos.
    
    Returns:
        Dict: Diccionario con estadísticas básicas
    """
    conn: Optional[sqlite3.Connection] = None
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        stats: Dict[str, Any] = {}
        
        # Total de registros
        cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        stats['total_registros'] = cursor.fetchone()[0]
        
        # Registros por malignidad
        cursor.execute(f"SELECT Malignidad, COUNT(*) FROM {TABLE_NAME} GROUP BY Malignidad")
        stats['por_malignidad'] = dict(cursor.fetchall())
        
        # Últimos registros procesados
        cursor.execute(f'SELECT DATE("Fecha Ingreso Base de Datos"), COUNT(*) FROM {TABLE_NAME} GROUP BY DATE("Fecha Ingreso Base de Datos") ORDER BY DATE("Fecha Ingreso Base de Datos") DESC LIMIT 7')
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
    # Asegurar esquema antes de validar
    try:
        init_db()
    except Exception:
        pass
    conn: Optional[sqlite3.Connection] = None
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


def update_incomplete_records_with_debug_data(debug_file_path: str = None) -> int:
    """Actualiza registros incompletos usando datos del archivo DEBUG.
    
    Args:
        debug_file_path: Ruta al archivo DEBUG. Si es None, usa la ruta por defecto.
        
    Returns:
        int: Número de registros actualizados exitosamente
    """
    if debug_file_path is None:
        # CORREGIDO: Usar get_base_path() para compatibilidad con .exe
        debug_file_path = get_base_path() / "EXCEL" / "DEBUG_OCR_OUTPUT_ordenamientos.pdf.txt"
    
    if not Path(debug_file_path).exists():
        logger.warning(f"Archivo DEBUG no encontrado: {debug_file_path}")
        return 0
    
    try:
        # Leer archivo DEBUG
        with open(debug_file_path, 'r', encoding='utf-8') as f:
            debug_content = f.read()
        
        # Obtener registros incompletos
        df = get_all_records_as_dataframe()
        if df.empty:
            logger.info("No hay registros en la base de datos")
            return 0
        
        # Identificar campos críticos
        critical_fields = ['Médico tratante', 'Tipo de documento', 'N. de identificación', 'Edad']
        
        # Encontrar registros incompletos
        incomplete_mask = df[critical_fields].isnull().any(axis=1) | (df[critical_fields] == '').any(axis=1) | (df[critical_fields] == 'NO ENCONTRADO').any(axis=1)
        incomplete_records = df[incomplete_mask]
        
        if incomplete_records.empty:
            logger.info("No se encontraron registros incompletos para actualizar")
            return 0
        
        logger.info(f"Encontrados {len(incomplete_records)} registros incompletos para actualizar")
        
        updated_count = 0
        
        # Importar funciones de procesamiento del unified_extractor
        from core.unified_extractor import extract_ihq_data, map_to_excel_format
        
        for _, record in incomplete_records.iterrows():
            ihq_code = record.get("N. peticion (0. Numero de biopsia)", "")
            
            if not ihq_code:
                continue
            
            try:
                # Extraer contenido específico del IHQ del archivo DEBUG
                ihq_content = _extract_ihq_content_from_debug(debug_content, ihq_code)
                
                if not ihq_content:
                    logger.warning(f"No se pudo extraer contenido para {ihq_code}")
                    continue
                
                # Procesar con patrones actualizados
                extracted_data = extract_ihq_data(ihq_content)
                
                # Verificar si los datos extraídos están completos
                if not _has_critical_data(extracted_data):
                    logger.warning(f"Datos extraídos incompletos para {ihq_code}")
                    continue
                
                # Mapear a formato Excel
                excel_rows = map_to_excel_format(extracted_data)
                
                if excel_rows and excel_rows[0]:
                    # Actualizar el registro de forma inteligente (preservando biomarcadores)
                    result = smart_update_records([excel_rows[0]])
                    if result > 0:
                        updated_count += 1
                        logger.info(f"Actualizado exitosamente: {ihq_code}")
                    else:
                        logger.warning(f"Error actualizando: {ihq_code}")
                        
            except Exception as e:
                logger.error(f"Error procesando {ihq_code}: {e}")
                continue
        
        logger.info(f"Actualización completada: {updated_count} registros actualizados")
        return updated_count
        
    except Exception as e:
        logger.error(f"Error en actualización automática: {e}")
        return 0


def _extract_ihq_content_from_debug(debug_content: str, ihq_code: str) -> str:
    """Extrae contenido específico de un IHQ del archivo DEBUG."""
    lines = debug_content.split('\n')
    
    start_idx = None
    end_idx = None
    
    for i, line in enumerate(lines):
        if ihq_code in line and 'N. peticion' in line:
            start_idx = max(0, i - 5)
        elif start_idx is not None and ('IHQ25' in line and ihq_code not in line and 'N. peticion' in line):
            end_idx = i
            break
    
    if start_idx is not None:
        if end_idx is None:
            end_idx = min(len(lines), start_idx + 100)
        return '\n'.join(lines[start_idx:end_idx])
    
    return ''


def _has_critical_data(extracted_data: Dict[str, Any]) -> bool:
    """Verifica si los datos extraídos contienen información crítica."""
    critical_fields = ['medico_tratante', 'tipo_documento', 'identificacion_numero', 'edad']
    
    for field in critical_fields:
        value = extracted_data.get(field, '')
        if not value or value == 'NO ENCONTRADO':
            return False
    
    return True


def get_incomplete_records_summary() -> Dict[str, Any]:
    """Obtiene un resumen de registros incompletos en la base de datos.
    
    Returns:
        Dict con estadísticas de completitud
    """
    try:
        df = get_all_records_as_dataframe()
        if df.empty:
            return {"total_records": 0, "complete_records": 0, "incomplete_records": 0, "completeness_percentage": 0}
        
        critical_fields = ['Médico tratante', 'Tipo de documento', 'N. de identificación', 'Edad']
        
        # Contar registros completos
        complete_mask = df[critical_fields].notna().all(axis=1) & (df[critical_fields] != '').all(axis=1) & (df[critical_fields] != 'NO ENCONTRADO').all(axis=1)
        complete_count = complete_mask.sum()
        
        total_count = len(df)
        incomplete_count = total_count - complete_count
        completeness_percentage = (complete_count / total_count * 100) if total_count > 0 else 0
        
        return {
            "total_records": total_count,
            "complete_records": complete_count,
            "incomplete_records": incomplete_count,
            "completeness_percentage": round(completeness_percentage, 1),
            "incomplete_ihq_codes": df[~complete_mask]["N. peticion (0. Numero de biopsia)"].tolist()
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo resumen de completitud: {e}")
        return {"error": str(e)}

def verificar_duplicado_por_peticion(numero_peticion: str) -> Dict[str, Any]:
    """
    Verifica si un número de petición ya existe en la base de datos
    Retorna información del registro existente si se encuentra
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {TABLE_NAME} 
                WHERE "N. peticion (0. Numero de biopsia)" = ?
            """, (numero_peticion,))
            
            result = cursor.fetchone()
            if result:
                # Obtener nombres de columnas
                column_names = [description[0] for description in cursor.description]
                # Crear diccionario con los datos
                registro = dict(zip(column_names, result))
                return {
                    "existe": True,
                    "registro": registro
                }
            else:
                return {"existe": False, "registro": None}
                
    except Exception as e:
        logger.error(f"Error verificando duplicado: {e}")
        return {"existe": False, "error": str(e)}

def get_fecha_range_registros() -> Dict[str, str]:
    """
    Obtiene el rango de fechas de los registros en la base de datos
    Retorna fechas mínima y máxima en formato DD/MM/YYYY

    CORREGIDO: Ordena correctamente las fechas usando SUBSTR para convertir DD/MM/YYYY a YYYY-MM-DD
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            # CORREGIDO: Ordenar fechas correctamente con conversión DD/MM/YYYY -> YYYY-MM-DD
            cursor.execute(f"""
                SELECT
                    MIN(SUBSTR("Fecha Informe", 7, 4) || '-' || SUBSTR("Fecha Informe", 4, 2) || '-' || SUBSTR("Fecha Informe", 1, 2)) as fecha_min_sorted,
                    MAX(SUBSTR("Fecha Informe", 7, 4) || '-' || SUBSTR("Fecha Informe", 4, 2) || '-' || SUBSTR("Fecha Informe", 1, 2)) as fecha_max_sorted,
                    COUNT(*) as total
                FROM {TABLE_NAME}
                WHERE "Fecha Informe" IS NOT NULL AND "Fecha Informe" != '' AND LENGTH("Fecha Informe") = 10
            """)

            result = cursor.fetchone()
            if result and result[0]:
                # Convertir de vuelta a DD/MM/YYYY
                from datetime import datetime
                fecha_min_dt = datetime.strptime(result[0], "%Y-%m-%d")
                fecha_max_dt = datetime.strptime(result[1], "%Y-%m-%d")

                return {
                    "fecha_min": fecha_min_dt.strftime("%d/%m/%Y"),
                    "fecha_max": fecha_max_dt.strftime("%d/%m/%Y"),
                    "total_registros": result[2]
                }
            else:
                return {"fecha_min": None, "fecha_max": None, "total_registros": 0}

    except Exception as e:
        logger.error(f"Error obteniendo rango de fechas: {e}")
        return {"error": str(e)}

def get_distribucion_mensual() -> Dict[str, int]:
    """
    Obtiene la distribución mensual de registros
    Retorna diccionario con mes: cantidad

    CORREGIDO: Usa format='%d/%m/%Y' para parsear correctamente fechas en formato español
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            df = pd.read_sql_query(f"""
                SELECT "Fecha Informe"
                FROM {TABLE_NAME}
                WHERE "Fecha Informe" IS NOT NULL AND "Fecha Informe" != ''
            """, conn)

            if df.empty:
                return {}

            # CORREGIDO: Convertir fechas especificando formato DD/MM/YYYY
            df['Fecha Informe'] = pd.to_datetime(df['Fecha Informe'], format='%d/%m/%Y', errors='coerce')
            df = df.dropna(subset=['Fecha Informe'])

            # Crear columna mes-año
            df['mes_ano'] = df['Fecha Informe'].dt.strftime('%Y-%m')

            # Contar por mes
            distribucion = df['mes_ano'].value_counts().sort_index().to_dict()

            return distribucion

    except Exception as e:
        logger.error(f"Error obteniendo distribución mensual: {e}")
        return {"error": str(e)}

def calcular_estadisticas_confiabilidad() -> Dict[str, Any]:
    """
    Calcula estadísticas de confiabilidad basadas en la distribución temporal
    """
    try:
        distribucion = get_distribucion_mensual()
        if not distribucion or "error" in distribucion:
            return {"error": "No se pudo obtener distribución"}
        
        valores = list(distribucion.values())
        total_registros = sum(valores)
        
        # Umbrales de confiabilidad
        THRESHOLDS = {
            'alto': 20,
            'medio': 10,
            'bajo': 5
        }
        
        # Clasificar meses por confiabilidad
        meses_alta = sum(1 for v in valores if v >= THRESHOLDS['alto'])
        meses_media = sum(1 for v in valores if THRESHOLDS['medio'] <= v < THRESHOLDS['alto'])
        meses_baja = sum(1 for v in valores if THRESHOLDS['bajo'] <= v < THRESHOLDS['medio'])
        meses_muy_baja = sum(1 for v in valores if v < THRESHOLDS['bajo'])
        
        # Calcular porcentaje de confiabilidad general
        registros_alta_conf = sum(v for v in valores if v >= THRESHOLDS['alto'])
        porcentaje_confiabilidad = (registros_alta_conf / total_registros * 100) if total_registros > 0 else 0
        
        return {
            "total_registros": total_registros,
            "total_meses": len(valores),
            "meses_alta_confiabilidad": meses_alta,
            "meses_media_confiabilidad": meses_media, 
            "meses_baja_confiabilidad": meses_baja,
            "meses_muy_baja_confiabilidad": meses_muy_baja,
            "porcentaje_confiabilidad_general": round(porcentaje_confiabilidad, 1),
            "distribucion": distribucion
        }
        
    except Exception as e:
        logger.error(f"Error calculando estadísticas de confiabilidad: {e}")
        return {"error": str(e)}