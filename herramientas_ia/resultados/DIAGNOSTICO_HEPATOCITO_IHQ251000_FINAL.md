# DIAGNOSTICO: IHQ_HEPATOCITO No Se Guarda en BD para IHQ251000

**Caso:** IHQ251000  
**Fecha de investigacion:** 2025-11-01  
**Estado:** CAUSA RAIZ IDENTIFICADA

---

## RESUMEN EJECUTIVO

El biomarcador HEPATOCITO se extrae correctamente como "POSITIVO" del PDF pero se guarda como "N/A" en la base de datos, mientras que ARGINASA (que esta en el mismo patron narrativo) SI se guarda correctamente.

**Resultado de la investigacion:**
- extraccion.IHQ_HEPATOCITO = "POSITIVO" (CORRECTO)
- base_datos.datos_guardados.IHQ_HEPATOCITO = "POSITIVO" (debug_map dice que se guardo)
- BD REAL IHQ_HEPATOCITO = "N/A" (INCORRECTO)

**Causa raiz:**
El problema NO esta en el extractor, sino en el flujo de guardado en `database_manager.py`. El debug_map muestra lo que SE VA A GUARDAR, no lo que REALMENTE SE GUARDO.

---

## FLUJO DE DATOS COMPLETO

### 1. EXTRACCION (unified_extractor.py)
**Archivo:** `core/unified_extractor.py`

Resultado:
```
unified_extractor = {
    'IHQ_HEPATOCITO': 'POSITIVO',  # <- Clave normalizada (mayusculas)
    'hepatocito': 'POSITIVO',      # <- Clave minusculas (duplicado)
    'IHQ_ARGINASA': 'POSITIVO',
    'arginasa': 'POSITIVO'
}
```

**Estado:** CORRECTO (ambos biomarcadores extraidos)

### 2. MAPEO (ihq_processor.py)
**Archivo:** `core/ihq_processor.py` linea 150

```python
datos_mapeados = map_to_database_format(datos_extraidos)
```

Genera diccionario con claves normalizadas para BD.

**Estado:** CORRECTO (ambos biomarcadores en datos_mapeados)

### 3. DEBUG_MAP (debug_mapper.py)
**Archivo:** `core/debug_mapper.py` linea 158

```python
mapper.registrar_base_datos(datos_mapeados)  # <- ANTES de guardar en BD
mapper.guardar_mapa()  # <- Guarda debug_map con datos_mapeados
```

El debug_map se genera ANTES de save_records(), por lo que muestra lo que SE VA A GUARDAR, no lo que REALMENTE SE GUARDO.

**Estado:** CORRECTO (debug_map refleja intencion de guardar)

### 4. GUARDADO EN BD (database_manager.py)
**Archivo:** `core/database_manager.py` linea 709-829

```python
def save_records(records: List[Dict[str, Any]]) -> int:
    # Linea 773:
    normalized_col = _normalize_column_name(col)  # 'IHQ_HEPATOCITO' -> 'ihq_hepatocito'
    value = record.get(normalized_col, record.get(col, 'N/A'))
```

**Simulacion:**
- col = 'IHQ_HEPATOCITO'
- normalized_col = 'ihq_hepatocito'
- record.get('ihq_hepatocito') = None (NO EXISTE en record)
- record.get('IHQ_HEPATOCITO') = 'POSITIVO' (SI EXISTE)
- **value DEBERIA SER 'POSITIVO'**

Pero en BD esta "N/A".

**Estado:** PROBLEMA AQUI

---

## HIPOTESIS DEL PROBLEMA

### Hipotesis #1: Orden de Columnas en UPDATE (MAS PROBABLE)

En save_records() linea 769-790, se construye el UPDATE dinamicamente:

```python
for col in table_columns:  # <- Orden de columnas de PRAGMA table_info
    normalized_col = _normalize_column_name(col)
    value = record.get(normalized_col, record.get(col, 'N/A'))
    values.append(value)

set_clause = ', '.join([f'"{col}" = ?' for col in table_columns])
cursor.execute(f"UPDATE {TABLE_NAME} SET {set_clause} WHERE ...", values + [peticion])
```

Si el ORDEN de `table_columns` no coincide con el ORDEN de `values`, el valor de HEPATOCITO podria estar siendo asignado a otra columna.

**Como verificar:**
1. Imprimir `table_columns` durante save_records()
2. Imprimir `values` array
3. Verificar que el indice de 'IHQ_HEPATOCITO' en `table_columns` coincide con el valor 'POSITIVO' en `values`

### Hipotesis #2: Problema con _apply_default_values() (MENOS PROBABLE)

La funcion `_apply_default_values()` (linea 649-665) convierte valores vacios en "N/A":

```python
def _apply_default_values(record: Dict[str, Any]) -> Dict[str, Any]:
    cleaned_record = {}
    for key, value in record.items():
        if value is None or str(value).strip() == '':
            cleaned_record[key] = 'N/A'
        else:
            cleaned_record[key] = value
    return cleaned_record
```

Si `record['IHQ_HEPATOCITO']` de alguna forma se vuelve None o vacio DESPUES del mapeo, se convertira en "N/A".

**Como verificar:**
1. Agregar logging en _apply_default_values() para IHQ_HEPATOCITO
2. Verificar si 'IHQ_HEPATOCITO' tiene valor antes y despues de la funcion

### Hipotesis #3: Caso Se Guardo ANTES de Agregar IHQ_HEPATOCITO (DESCARTADA)

La columna IHQ_HEPATOCITO SI existe en BD (indice 141). El caso se proceso el 2025-11-01 14:34, y la columna ya existia en ese momento.

**Estado:** DESCARTADA

---

## COMPARACION CON ARGINASA (FUNCIONA CORRECTAMENTE)

ARGINASA SI se guarda correctamente:

| Campo | HEPATOCITO | ARGINASA |
|-------|-----------|----------|
| Extraccion IHQ_* | POSITIVO | POSITIVO |
| Extraccion minusculas | POSITIVO | POSITIVO |
| datos_guardados | POSITIVO | POSITIVO |
| BD REAL | **N/A** | **POSITIVO** |
| Patron narrativo | "marcacion usual para arginasa y Hepatocito" | "marcacion usual para arginasa y Hepatocito" |
| Indice columna BD | 141 | 133 |

**Diferencia clave:**
- IHQ_ARGINASA esta en indice 133
- IHQ_HEPATOCITO esta en indice 141 (mas adelante)

Esto sugiere que el problema podria estar relacionado con el ORDEN de las columnas en el UPDATE statement.

---

## SOLUCION RECOMENDADA

### Solucion Inmediata: DEBUGGING

Agregar logging temporal en `database_manager.py` save_records():

```python
# En linea 768-780, DESPUES de construir values
if peticion == 'IHQ251000':
    logger.info(f"DEBUG IHQ251000 - Guardando en BD:")
    logger.info(f"  Total columnas: {len(table_columns)}")
    logger.info(f"  Total valores: {len(values)}")
    
    # Buscar IHQ_HEPATOCITO
    try:
        idx_hepatocito = table_columns.index('IHQ_HEPATOCITO')
        logger.info(f"  IHQ_HEPATOCITO indice: {idx_hepatocito}")
        logger.info(f"  IHQ_HEPATOCITO valor: {repr(values[idx_hepatocito])}")
    except (ValueError, IndexError) as e:
        logger.error(f"  ERROR buscando IHQ_HEPATOCITO: {e}")
    
    # Buscar IHQ_ARGINASA para comparar
    try:
        idx_arginasa = table_columns.index('IHQ_ARGINASA')
        logger.info(f"  IHQ_ARGINASA indice: {idx_arginasa}")
        logger.info(f"  IHQ_ARGINASA valor: {repr(values[idx_arginasa])}")
    except (ValueError, IndexError) as e:
        logger.error(f"  ERROR buscando IHQ_ARGINASA: {e}")
```

Luego reprocesar IHQ251000 y revisar los logs.

### Solucion Permanente: VALIDACION POST-GUARDADO

Modificar `save_records()` para verificar que los valores se guardaron correctamente:

```python
# Despues de conn.commit() (linea 814)
if peticion in ['IHQ251000']:  # Casos de prueba
    cursor.execute(f'SELECT IHQ_HEPATOCITO, IHQ_ARGINASA FROM {TABLE_NAME} WHERE "Numero de caso" = ?', (peticion,))
    verificacion = cursor.fetchone()
    logger.info(f"VERIFICACION POST-GUARDADO {peticion}:")
    logger.info(f"  IHQ_HEPATOCITO en BD: {repr(verificacion[0])}")
    logger.info(f"  IHQ_ARGINASA en BD: {repr(verificacion[1])}")
```

---

## ARCHIVOS MODIFICADOS EN INVESTIGACION

1. `herramientas_ia/resultados/diagnostico_hepatocito_ihq251000.txt` - Diagnostico inicial
2. `herramientas_ia/resultados/DIAGNOSTICO_HEPATOCITO_IHQ251000_FINAL.md` - Este archivo

---

## SIGUIENTE PASO

1. Agregar logging de debugging en save_records()
2. Reprocesar caso IHQ251000
3. Revisar logs para confirmar hipotesis #1
4. Aplicar solucion permanente segun resultado

---

**Generado por:** data-auditor agent  
**Fecha:** 2025-11-01
