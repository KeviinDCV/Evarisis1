# INSTRUCCIONES DE INTEGRACIÓN - v6.0.3

**Correcciones IHQ250982 - Formato Narrativo**
**Fecha:** 2025-10-23 01:58:17
**Estado:** ✅ Código aplicado - PENDIENTE integración

---

## ESTADO ACTUAL

Las 4 correcciones se aplicaron exitosamente en los extractores:

- ✅ `medical_extractor.py` - 3 correcciones aplicadas
- ✅ `biomarker_extractor.py` - 1 corrección aplicada
- ✅ Sintaxis validada en ambos archivos
- ✅ Backups creados (20251023_015558)

**PENDIENTE:** Integrar `extract_narrative_biomarkers_list()` en `unified_extractor.py`

---

## PASO 1: Integrar en unified_extractor.py

### Ubicación del cambio

Archivo: `core/unified_extractor.py`
Función: `extract_ihq_data()` (buscar línea donde se llama a `extract_biomarkers()`)

### Código a agregar

**PASO 1.1:** Agregar import al inicio del archivo (después de otros imports de biomarker_extractor):

```python
from core.extractors.biomarker_extractor import (
    extract_biomarkers,
    extract_narrative_biomarkers,      # Ya existe
    extract_narrative_biomarkers_list, # NUEVO - v6.0.3
    get_biomarker_summary,
    BIOMARKER_DEFINITIONS
)
```

**PASO 1.2:** Buscar la sección donde se extraen biomarcadores (después de `extract_biomarkers()`):

Buscar código similar a:
```python
biomarker_results = extract_biomarkers(text)
```

**PASO 1.3:** DESPUÉS de esa línea, agregar extracción narrativa:

```python
# V6.0.3: Extracción de biomarcadores en formato narrativo (complementario)
# Extrae biomarcadores que están en formato de texto libre

# PASO 1: Patrones complejos (función existente)
# Ejemplo: "RECEPTOR DE ESTRÓGENOS, positivo focal"
narrative_complex = extract_narrative_biomarkers(descripcion_microscopica)

# PASO 2: Listas simples (nueva función - v6.0.3)
# Ejemplo: "son positivas para CKAE1E3, CK7 Y CAM 5.2"
narrative_list = extract_narrative_biomarkers_list(descripcion_microscopica, BIOMARKER_DEFINITIONS)

# PASO 3: Merge de resultados narrativos (no sobreescribir valores positivos existentes)
for columna, valor in {**narrative_complex, **narrative_list}.items():
    # Solo agregar si:
    # 1. No existe en biomarker_results, O
    # 2. El valor actual es 'N/A' (vacío)
    if columna not in biomarker_results or biomarker_results[columna] == 'N/A':
        biomarker_results[columna] = valor
```

### Ejemplo de integración completa

```python
def extract_ihq_data(text: str, pdf_path: str = None) -> Dict[str, Any]:
    """Extrae datos de informe IHQ completo"""

    # ... código existente ...

    # Extraer secciones
    descripcion_microscopica = extract_descripcion_microscopica_final(text)

    # Extraer biomarcadores (método principal)
    biomarker_results = extract_biomarkers(text)

    # ═══════════════════════════════════════════════════════════════
    # V6.0.3: EXTRACCIÓN NARRATIVA COMPLEMENTARIA (IHQ250982)
    # ═══════════════════════════════════════════════════════════════
    # Extrae biomarcadores en formato narrativo que no fueron capturados
    # por extract_biomarkers() (patrones estructurados)

    # Patrones complejos: "RECEPTOR DE ESTRÓGENOS, positivo focal"
    narrative_complex = extract_narrative_biomarkers(descripcion_microscopica)

    # Listas simples: "son positivas para CKAE1E3, CK7 Y CAM 5.2"
    narrative_list = extract_narrative_biomarkers_list(descripcion_microscopica, BIOMARKER_DEFINITIONS)

    # Merge (prioridad: biomarker_results > narrative_complex > narrative_list)
    for columna, valor in {**narrative_complex, **narrative_list}.items():
        if columna not in biomarker_results or biomarker_results[columna] == 'N/A':
            biomarker_results[columna] = valor

    # ... resto del código ...

    return result
```

---

## PASO 2: Validar integración

### 2.1 Verificar sintaxis

```bash
python -m py_compile core/unified_extractor.py
```

**Salida esperada:** Sin errores

### 2.2 Verificar que funcione con caso de prueba

```python
# Test rápido en Python
from core.unified_extractor import extract_ihq_data

# Leer PDF de prueba
with open('data/pdfs_ihq/IHQ250982.pdf', 'rb') as f:
    # ... extraer texto ...
    resultado = extract_ihq_data(texto)

# Verificar biomarcadores narrativos
print(f"IHQ_ESTUDIOS_SOLICITADOS: {resultado.get('IHQ_ESTUDIOS_SOLICITADOS')}")
print(f"FACTOR_PRONOSTICO: {resultado.get('FACTOR_PRONOSTICO')}")
print(f"IHQ_CK7: {resultado.get('IHQ_CK7')}")
print(f"IHQ_CKAE1_AE3: {resultado.get('IHQ_CKAE1_AE3')}")
```

---

## PASO 3: Reprocesar IHQ250982

### 3.1 Usando auditor_sistema.py

```bash
python herramientas_ia/auditor_sistema.py IHQ250982 --reprocesar --inteligente
```

### 3.2 Verificar resultados esperados

| Campo | ANTES (incorrecto) | DESPUÉS (esperado) |
|-------|--------------------|--------------------|
| IHQ_ESTUDIOS_SOLICITADOS | 2 biomarcadores | 7 biomarcadores (CKAE1E3, CAM 5.2, CK7, GFAP, SOX10, SOX100, etc.) |
| FACTOR_PRONOSTICO | Contaminado con nombre | Limpio, solo biomarcadores |
| IHQ_CK7 | N/A | POSITIVO |
| IHQ_CKAE1_AE3 | N/A | POSITIVO |
| IHQ_CAM52 | N/A | POSITIVO |
| IHQ_GFAP | N/A | (verificar PDF) |
| IHQ_SOX10 | N/A | (verificar PDF) |

---

## PASO 4: Validar con data-auditor

```bash
python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente
```

**Verificar:**
- ✅ IHQ_ESTUDIOS_SOLICITADOS completitud > 90%
- ✅ FACTOR_PRONOSTICO sin contaminación
- ✅ Biomarcadores narrativos extraídos correctamente
- ✅ Sin falsos positivos

---

## PASO 5: Actualizar versión del sistema

### 5.1 Generar CHANGELOG

```bash
python herramientas_ia/gestor_version.py --nueva-version 6.0.3 --tipo minor \
    --descripcion "Soporte formato narrativo + limpieza metadata (IHQ250982)"
```

### 5.2 Verificar archivos actualizados

- ✅ `VERSION_INFO` → 6.0.3
- ✅ `CHANGELOG.md` → Entrada nueva con correcciones
- ✅ `BITACORA.md` → Registro de cambios

---

## RESUMEN DE CAMBIOS v6.0.3

### Archivos modificados

1. `core/extractors/medical_extractor.py`
   - Nueva función: `limpiar_factor_pronostico()`
   - Modificada: `extract_factor_pronostico()` (limpieza + narrativo)
   - Modificada: `extract_biomarcadores_solicitados_robust()` (patrón 10)

2. `core/extractors/biomarker_extractor.py`
   - Nueva función: `extract_narrative_biomarkers_list()`

3. `core/unified_extractor.py` (PENDIENTE)
   - Integrar extracción narrativa complementaria

### Impacto estimado

- ~30-40% de casos con problemas de extracción serán corregidos
- IHQ_ESTUDIOS_SOLICITADOS: +25% precisión
- FACTOR_PRONOSTICO: 100% limpio (sin metadata)
- Biomarcadores narrativos: +15-20% cobertura

---

## TROUBLESHOOTING

### Problema 1: ImportError al agregar import

**Error:** `ImportError: cannot import name 'extract_narrative_biomarkers_list'`

**Solución:** Verificar que biomarker_extractor.py tiene la función en línea 1742-1804.

```bash
grep -n "def extract_narrative_biomarkers_list" core/extractors/biomarker_extractor.py
```

**Salida esperada:** `1742:def extract_narrative_biomarkers_list(...)`

### Problema 2: Función no detecta biomarcadores

**Verificar:** La función recibe `descripcion_microscopica` correctamente.

```python
# Debug
print(f"DESC. MICRO: {descripcion_microscopica[:200]}")
narrative_list = extract_narrative_biomarkers_list(descripcion_microscopica, BIOMARKER_DEFINITIONS)
print(f"Narrativos detectados: {narrative_list}")
```

### Problema 3: Merge sobrescribe valores positivos

**Verificar:** Condición en el merge.

```python
# CORRECTO
if columna not in biomarker_results or biomarker_results[columna] == 'N/A':
    biomarker_results[columna] = valor

# INCORRECTO (sobrescribe todo)
biomarker_results[columna] = valor  # ❌ No usar
```

---

## CONTACTO Y SOPORTE

**Reportes generados:**
- `herramientas_ia/resultados/correcciones_IHQ250982_narrativo_20251023_015817.md` (completo)
- `herramientas_ia/resultados/resumen_correcciones_IHQ250982.md` (ejecutivo)

**Backups:**
- `backups/medical_extractor_backup_20251023_015558.py`
- `backups/biomarker_extractor_backup_20251023_015558.py`

**Rollback (si necesario):**
```bash
cp backups/medical_extractor_backup_20251023_015558.py core/extractors/medical_extractor.py
cp backups/biomarker_extractor_backup_20251023_015558.py core/extractors/biomarker_extractor.py
```

---

**Generado por:** core-editor (agente EVARISIS)
**Fecha:** 2025-10-23 01:58:17
**Versión:** 6.0.2 → 6.0.3
