# FUNC-03 (MANUAL): Agregación de Aliases para IHQ250277

## Objetivo
Agregar aliases faltantes en `biomarker_extractor.py` para 4 biomarcadores que ya existen en BD pero cuyos aliases no estaban mapeados en `normalize_biomarker_name()`.

## Problema Detectado
- **Caso:** IHQ250277
- **Score inicial:** 80%
- **Problema:** 4 biomarcadores (CD31, LCA, ALK, CROMOGRANINA) existen en BD pero no se extraen porque faltan aliases en el mapeo de normalización

## Verificación Previa
```
Columnas en BD:
✓ IHQ_CD31 - EXISTE
✓ IHQ_LCA - EXISTE (0% uso, legacy)
✓ IHQ_CD45 - EXISTE (100% uso, columna principal para LCA)
✓ IHQ_ALK - EXISTE
✓ IHQ_CROMOGRANINA - EXISTE
```

## Modificaciones Realizadas

### 1. CD31 (6 aliases agregados)
**Archivo:** `core/extractors/biomarker_extractor.py`
**Líneas:** 8221-8227

```python
# V6.5.94 FIX IHQ250277: CD31/PECAM-1 - Marcador endotelial vascular
'CD31': 'CD31',
'CD-31': 'CD31',
'CD 31': 'CD31',
'PECAM1': 'CD31',
'PECAM-1': 'CD31',
'PECAM 1': 'CD31',
```

**Contexto:**
- CD31 ya estaba definido en BIOMARKER_DEFINITIONS (línea 2843)
- Mapeo en unified_extractor.py ya existía (línea 983)
- Solo faltaban aliases en normalize_biomarker_name()

### 2. LCA (5 aliases agregados)
**Archivo:** `core/extractors/biomarker_extractor.py`
**Líneas:** 8240-8244

```python
'CD-45': 'CD45',  # V6.5.94 FIX IHQ250277: Variante con guion
'CD 45': 'CD45',  # V6.5.94 FIX IHQ250277: Variante con espacio
'LCA': 'CD45',  # V6.5.94 FIX IHQ250277: Alias LCA (Antigeno Leucocitario Comun)
'LEUCOCITO COMUN': 'CD45',  # V6.5.94 FIX IHQ250277: Alias descriptivo
'ANTIGENO LEUCOCITARIO COMUN': 'CD45',  # V6.5.94 FIX IHQ250277: Alias completo
```

**Decisión importante:**
- Existen 2 columnas: IHQ_LCA e IHQ_CD45
- IHQ_CD45: 100% uso (49/49 casos)
- IHQ_LCA: 0% uso (0/49 casos)
- **Decisión:** Mapear 'LCA' → 'CD45' (columna principal)
- Eliminadas entradas antiguas 'LCA': 'LCA' que apuntaban a columna legacy

### 3. ALK (Ya estaba completo)
**Archivo:** `core/extractors/biomarker_extractor.py`
**Líneas:** 8289-8295

```python
'ALK': 'ALK',  # V6.3.51 FIX IHQ250055: Anaplastic Lymphoma Kinase
'ALK-1': 'ALK',
'ALK1': 'ALK',
'ALK 01': 'ALK',  # V6.5.91 FIX IHQ250277: Variante con espacio y cero
'ALK-01': 'ALK',  # V6.5.91 FIX IHQ250277: Variante con guión y cero
'ALK 1': 'ALK',
```

**Nota:** ALK ya tenía todos los aliases necesarios (agregados en v6.5.91)

### 4. CROMOGRANINA (2 aliases agregados)
**Archivo:** `core/extractors/biomarker_extractor.py`
**Líneas:** 8328-8329

```python
'CHROMOGRANIN': 'CROMOGRANINA',  # V6.5.94 FIX IHQ250277: Alias ingles
'CHROMOGRANIN A': 'CROMOGRANINA',  # V6.5.94 FIX IHQ250277: Alias completo ingles
```

**Contexto:**
- Ya existían: CHROMOGRANINA, CROMOGRAMINA (typo OCR)
- Faltaban: CHROMOGRANIN, CHROMOGRANIN A (inglés)

## Duplicados Eliminados

Durante el proceso se detectaron y eliminaron duplicados:
- 8 entradas duplicadas de aliases
- 3 entradas obsoletas de 'LCA': 'LCA' (líneas 7920-7922)
- 6 duplicados de CD31 (segunda aparición)
- 2 duplicados de CHROMOGRANIN

## Versión Actualizada
- **Versión anterior:** v6.5.60
- **Versión nueva:** v6.5.94
- **Changelog:** Agregado en líneas 24-36

## Impacto Esperado

### En IHQ250277:
- **Score esperado:** 80% → ~100%
- **Biomarcadores corregidos:** 4 (CD31, LCA, CROMOGRANINA, ALK ya estaba)

### General:
- Todos los casos con CD31, LCA, CROMOGRANINA en formato inglés ahora se extraerán correctamente
- No requiere agregar columnas nuevas (ya existían)
- No requiere FUNC-06 si los casos nunca fueron procesados (solo procesar)
- Requiere FUNC-06 si los casos ya fueron procesados (reprocesar con extractor actualizado)

## Siguiente Paso

**Usuario debe:**
1. Reprocesar IHQ250277 (si ya fue procesado antes)
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250277 --func-06
   ```
   
   O procesar por primera vez (si nunca fue procesado):
   ```bash
   # Via ui.py - Procesar PDF que contiene IHQ250277
   ```

2. Validar score actualizado:
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250277 --inteligente
   ```

## Verificación Post-Modificación

```
OK Sintaxis Python validada
OK TODOS LOS ALIASES VERIFICADOS CORRECTAMENTE (15/15)

Aliases críticos verificados:
✓ CD31 (6 aliases)
✓ LCA a CD45 (5 aliases)
✓ ALK (6 aliases - ya existían)
✓ CROMOGRANINA (4 aliases, 2 nuevos)
```

## Archivos Modificados
- `core/extractors/biomarker_extractor.py` (v6.5.94)
  - Líneas 8221-8227: CD31 aliases
  - Líneas 8240-8244: LCA/CD45 aliases
  - Líneas 8328-8329: CHROMOGRANIN aliases
  - Líneas 24-36: Changelog v6.5.94

## Fecha
3 de febrero de 2026

## Autor
Claude Code (asistido por usuario)

---

**Nota:** Este fue un proceso manual de FUNC-03 porque los biomarcadores ya existían en BD. FUNC-03 automático se usa cuando el biomarcador NO existe en absoluto (requiere modificar 6 archivos: database_manager.py, auditor_sistema.py, ui.py, validation_checker.py, biomarker_extractor.py, unified_extractor.py).
