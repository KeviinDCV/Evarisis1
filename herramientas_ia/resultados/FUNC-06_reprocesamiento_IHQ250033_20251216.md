# FUNC-06: Reprocesamiento IHQ250033
## Validacion Unificacion CROMOGRANINA y SINAPTOFISINA en Espanol

**Fecha:** 2025-12-16 01:57
**Caso:** IHQ250033
**Objetivo:** Verificar que extractores generen SOLO columnas en espanol

---

## RESULTADO FINAL

### ESTADO: PROBLEMA DETECTADO

El reprocesamiento se completo exitosamente, pero se encontro duplicacion de columnas.

---

## HALLAZGOS CRITICOS

### 1. COLUMNAS DUPLICADAS EN BD

Se detectaron **5 columnas** relacionadas con CROMOGRANINA/SINAPTOFISINA en el schema de la BD:

```
IHQ_SYNAPTOFISINA     (duplicado)
IHQ_SINAPTOFISINA     (espanol - CORRECTO)
IHQ_CROMOGRANINA      (espanol - CORRECTO)
IHQ_CHROMOGRANINA     (duplicado)
IHQ_SYNAPTOPHYSIN     (duplicado)
```

**Ubicacion:** `core/database_manager.py`
- Linea 226-227: `IHQ_SINAPTOFISINA`, `IHQ_CROMOGRANINA` (espanol, correcto)
- Linea 244: `IHQ_CHROMOGRANINA`, `IHQ_SYNAPTOPHYSIN` (duplicados)

### 2. VALORES EN BD (IHQ250033)

Despues del reprocesamiento con FUNC-06:

```
IHQ_CROMOGRANINA (espanol):    POSITIVO
IHQ_CHROMOGRANINA (duplicado): POSITIVO
IHQ_SINAPTOFISINA (espanol):   POSITIVO
IHQ_SYNAPTOPHYSIN (ingles):    POSITIVO
IHQ_SYNAPTOFISINA (duplicado): POSITIVO
```

**Problema:** Todas las columnas (incluyendo duplicados) estan siendo pobladas.

### 3. MAPEOS EN EXTRACTORES

**unified_extractor.py** (correcto):
```python
'CHROMOGRANINA': 'IHQ_CROMOGRANINA',   # linea 710
'SYNAPTOPHYSIN': 'IHQ_SINAPTOFISINA',  # linea 711
```

**biomarker_extractor.py** (correcto):
```python
'CROMOGRANINA': {  # V6.3.40: Renombrado a espanol
    'nombres_alternativos': ['CHROMOGRANIN', 'CHROMOGRANINA'],
    ...
}
'SINAPTOFISINA': {  # V6.3.40: Renombrado a espanol
    'nombres_alternativos': ['SYNAPTOPHYSIN', 'SYNAPTOFISINA'],
    ...
}
```

### 4. CONTEXTO EN OCR (IHQ250033)

El caso menciona los biomarcadores en formato narrativo:

```
Linea 30: "chromogranina y synaptofisina" (estudios solicitados)
Linea 47: "inmunorreactividad fuerte para TTF-1, chromogranina, synaptofisina"
```

**Extraccion correcta:** POSITIVO (detectado narrativamente)

---

## ANALISIS DEL PROBLEMA

### Causa Raiz

El extractor esta poblando MULTIPLES columnas para el mismo biomarcador:

1. **Mapeo primario:** `CHROMOGRANINA` → `IHQ_CROMOGRANINA` (correcto)
2. **Mapeo secundario:** `CHROMOGRANIN` → `IHQ_CHROMOGRANINA` (duplicado)
3. **Mapeo legacy:** `SYNAPTOPHYSIN` → `IHQ_SYNAPTOPHYSIN` (duplicado)

**Posible ubicacion del bug:**
- `unified_extractor.py` linea ~1979-1982 (seccion "variantes legacy")
- El codigo tiene logica de "backward compatibility" que crea columnas duplicadas

### Impacto

1. **Almacenamiento:** Datos duplicados en BD (consume espacio innecesario)
2. **UI:** Mostrara columnas duplicadas (confusion para usuario)
3. **Exportacion:** Excel tendra columnas duplicadas
4. **Completitud:** Puede calcular incorrectamente (contar duplicados como campos distintos)

---

## SIGUIENTE PASO REQUERIDO

### Eliminar Columnas Duplicadas del Schema

**Archivo:** `core/database_manager.py`

**Eliminar de linea 244:**
```python
# ELIMINAR ESTAS COLUMNAS (duplicadas):
"IHQ_CHROMOGRANINA" TEXT,
"IHQ_SYNAPTOPHYSIN" TEXT,
```

**Conservar en lineas 226-227:**
```python
# CONSERVAR ESTAS (espanol, correcto):
"IHQ_SINAPTOFISINA" TEXT,
"IHQ_CROMOGRANINA" TEXT,
```

**Tambien revisar:**
- Linea 149: `NEW_TABLE_COLUMNS_ORDER` (eliminar `IHQ_SYNAPTOFISINA` duplicado)
- Linea 151: Eliminar `IHQ_CHROMOGRANINA`, `IHQ_SYNAPTOPHYSIN`
- Linea 356-361: Listas de nuevas columnas (eliminar duplicados)

### Eliminar Logica de Poblacion Duplicada

**Archivo:** `unified_extractor.py`

**Revisar lineas ~1979-1982:**
```python
# Esta logica de "backward compatibility" esta creando duplicados
# COMENTAR O ELIMINAR:
'IHQ_SINAPTOFISINA': ['IHQ_SYNAPTOPHYSIN', 'IHQ_SYNAPTOFISINA'],
'IHQ_CROMOGRANINA': ['IHQ_CHROMOGRANINA'],
```

### Despues de Corregir

1. Borrar BD: `rm data/huv_oncologia_NUEVO.db`
2. Reprocesar PDF completo (001-050)
3. Verificar con FUNC-01 que solo existan columnas en espanol

---

## VERIFICACIONES REALIZADAS

- [x] FUNC-06 ejecutado exitosamente
- [x] Caso IHQ250033 reprocesado (50 casos del PDF)
- [x] Valores extraidos correctamente (POSITIVO)
- [x] Debug_map actualizado
- [x] BD actualizada
- [x] Columnas duplicadas detectadas
- [x] Mapeos verificados en extractores
- [x] OCR verificado (formato narrativo)

---

## CONCLUSION

El objetivo de verificar la **unificacion en espanol** esta **PARCIALMENTE COMPLETADO**:

- ✅ Los extractores mapean correctamente a espanol
- ✅ Los valores se extraen correctamente
- ❌ PROBLEMA: Se crean columnas duplicadas en BD
- ❌ PROBLEMA: Se pueblan multiples columnas para el mismo biomarcador

**Proxima accion:** Eliminar columnas duplicadas del schema y logica de poblacion.

---

## METADATA

- Caso procesado: IHQ250033
- PDF: pdfs_patologia/IHQ DEL 001 AL 050.pdf
- Casos reprocesados: 50 (IHQ250001-IHQ250050)
- Debug map: data/debug_maps/debug_map_IHQ250033_20251216_015656.json
- Backup: (creado automaticamente por FUNC-06)

