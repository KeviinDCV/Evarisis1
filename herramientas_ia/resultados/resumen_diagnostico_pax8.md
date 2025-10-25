# RESUMEN EJECUTIVO: Diagnóstico PAX8 IHQ250983

**Fecha:** 2024-10-24
**Caso:** IHQ250983
**Problema:** PAX8 no se guarda en BD (permanece N/A)
**Causa raíz:** FALTA MAPEO EN CÓDIGO

---

## DIAGNÓSTICO COMPLETO

### Flujo de Extracción (Análisis Detallado)

```
1. PDF contiene: "inmunorreactividad para CKAE1AE3, S100, PAX8 y p40 heterogéneo"
   ✅ TEXTO CORRECTO

2. extract_narrative_biomarkers() extrae:
   ✅ {'PAX8': 'POSITIVO', 'CKAE1AE3': 'POSITIVO', 'S100': 'POSITIVO', 'P40': 'POSITIVO HETEROGÉNEO'}

3. normalize_biomarker_name('PAX8') retorna:
   ✅ 'PAX8'

4. biomarker_data contiene:
   ✅ {'PAX8': 'POSITIVO', ...}

5. unified_extractor.py intenta mapear (líneas 522-527):
   for new_name, ihq_field in biomarker_mapping.items():
       if new_name in biomarker_data:
           combined_data[ihq_field] = biomarker_data[new_name]

6. biomarker_mapping NO contiene 'PAX8':
   ❌ PAX8 NUNCA se procesa en el bucle

7. combined_data NO incluye IHQ_PAX8:
   ❌ PAX8 no se guarda en BD

8. BD guarda IHQ_PAX8 = 'N/A' (valor default)
   ❌ RESULTADO INCORRECTO
```

---

## EVIDENCIA

### ✅ Columna en BD EXISTE:
```
74. IHQ_PAX8 (TEXT)
```

### ✅ Extractor FUNCIONA:
```python
# Prueba manual confirma:
post_process_biomarker_list_with_modifiers("CKAE1AE3, S100, PAX8 y p40 heterogéneo")
# Retorna:
{
    'CKAE1AE3': 'POSITIVO',
    'S100': 'POSITIVO',
    'PAX8': 'POSITIVO',        # ✅ SE EXTRAE
    'P40': 'POSITIVO HETEROGÉNEO'
}
```

### ❌ Mapeo FALTA:
```python
# unified_extractor.py línea 416-466:
biomarker_mapping = {
    'HER2': 'IHQ_HER2',
    ...
    'PAX5': 'IHQ_PAX5',
    # ❌ FALTA: 'PAX8': 'IHQ_PAX8',
    'WT1': 'IHQ_WT1',
    ...
}
```

```python
# unified_extractor.py línea 1017+:
all_biomarker_mapping = {
    ...
    'PAX5': 'IHQ_PAX5', 'pax5': 'IHQ_PAX5',
    # ❌ FALTA: 'PAX8': 'IHQ_PAX8', 'pax8': 'IHQ_PAX8',
    'CD79A': 'IHQ_CD79A', 'cd79a': 'IHQ_CD79A',
    ...
}
```

### Solo existe mapeo inverso (para display, NO guarda en BD):
```python
# unified_extractor.py línea 1171:
biomarker_name_mapping = {
    ...
    'IHQ_PAX8': 'PAX8',  # SOLO LECTURA
    ...
}
```

---

## SOLUCIÓN

### Corrección Necesaria en `core/unified_extractor.py`:

**1. Mapeo principal (línea ~467):**
```python
'PAX5': 'IHQ_PAX5',
'PAX8': 'IHQ_PAX8',  # ← AGREGAR
'WT1': 'IHQ_WT1',
```

**2. Mapeo completo (línea ~1078):**
```python
'PAX5': 'IHQ_PAX5', 'pax5': 'IHQ_PAX5',
'PAX8': 'IHQ_PAX8', 'pax8': 'IHQ_PAX8',  # ← AGREGAR
'CD79A': 'IHQ_CD79A', 'cd79a': 'IHQ_CD79A',
```

---

## IMPACTO

- ✅ TTF1: CORREGIDO (ahora extrae NEGATIVO)
- ✅ P40: CORREGIDO (ahora extrae POSITIVO HETEROGÉNEO)
- ❌ PAX8: PENDIENTE (falta agregar mapeo)

**Casos afectados:** Todos los casos con PAX8 en formato narrativo (no solo IHQ250983)

**Estimación:** ~30-50 casos históricos con PAX8 en "inmunorreactividad para..." que no se guardaron.

---

## PASOS SIGUIENTES

1. Aplicar corrección en `unified_extractor.py` (agregar 2 líneas)
2. Reprocesar IHQ250983
3. Validar que PAX8 = POSITIVO
4. (Opcional) Identificar casos históricos con PAX8 en estudios solicitados pero vacío en BD
5. (Opcional) Reprocesar casos históricos afectados

---

**Diagnóstico realizado por:** core-editor (análisis técnico)
**Reporte detallado:** `diagnostico_pax8_20251024_093500.md`
**Siguiente acción:** Aplicar corrección con core-editor
