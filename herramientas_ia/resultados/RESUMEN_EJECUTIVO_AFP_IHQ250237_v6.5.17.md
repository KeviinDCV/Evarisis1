# RESUMEN EJECUTIVO: FUNC-06 IHQ250237 - AFP v6.5.17 FALLÓ

## RESULTADO DEL REPROCESAMIENTO

**Estado:** FALLIDO
- **Caso:** IHQ250237
- **Modificación:** v6.5.17 (filtro "PARA TINCIÓN CON")
- **Score ANTES:** 88.9%
- **Score DESPUÉS:** 88.9% (sin cambio)
- **IHQ_AFP:** POSITIVO (esperado: NEGATIVO)

## CAUSA RAÍZ CONFIRMADA

**El filtro v6.5.17 NO funciona porque:**

1. **Orden de extracción incorrecta:**
   - El extractor procesa PRIMERO la descripción macroscópica
   - Encuentra "AFP" en contexto "para tinción con los marcadores" (sin resultado clínico)
   - Extrae AFP como POSITIVO (valor por defecto cuando no hay indicador negativo)
   - **Este valor se GUARDA** antes de llegar a la descripción microscópica

2. **Filtro agregado en lugar equivocado:**
   - El filtro está en `extract_narrative_biomarkers_list()` (línea 8731-8746)
   - Pero AFP se extrae con otro patrón ANTES de llegar a esa función
   - El filtro nunca se evalúa porque el match ya ocurrió

3. **Contexto verificado:**
   - Distancia "tinción con" → "AFP": 66 caracteres
   - Ventana de contexto: 100 caracteres
   - El filtro DEBERÍA funcionar... si se evaluara

## SOLUCIÓN CORRECTA

**NO es agregar filtro "PARA TINCIÓN CON"**. Ya está agregado pero en función incorrecta.

**La solución REAL es:**

**Opción 1 (PREFERIDA): Procesar SOLO descripción microscópica**
```python
# En unified_extractor.py, al llamar extract_narrative_biomarkers_list:
# ANTES (incorrecto):
biomarcadores_lista = extract_narrative_biomarkers_list(texto_completo)

# DESPUÉS (correcto):
descripcion_microscopica = extraer_seccion_microscopica(texto_completo)
biomarcadores_lista = extract_narrative_biomarkers_list(descripcion_microscopica)
```

**Opción 2: Migrar filtro a función que procesa texto completo**
```python
# Agregar el filtro contextos_excluidos a TODAS las funciones que extraen:
# - extract_narrative_biomarkers()
# - extract_specific_biomarker_patterns()
# - extract_structured_biomarkers()
```

**Opción 3: Pre-filtrado del texto completo**
```python
# En unified_extractor, ANTES de cualquier extracción:
texto_limpio = eliminar_descripcion_macroscopica(texto_original)
# Luego procesar texto_limpio
```

## RECOMENDACIÓN INMEDIATA

Implementar **Opción 1** porque:
- Quirúrgica (afecta solo AFP y casos similares)
- No requiere modificar múltiples funciones
- Resuelve el problema de raíz (descripción macroscópica NO debe procesarse para resultados)
- Más fácil de validar sin regresiones

## PRÓXIMOS PASOS

1. Identificar dónde se llama `extract_narrative_biomarkers_list()` en `unified_extractor.py`
2. Modificar para que reciba SOLO `descripcion_microscopica` (no texto completo)
3. Validar con IHQ250237:
   - AFP debe ser NEGATIVO
   - Score debe subir a 100%
4. Validar anti-regresión con casos de referencia

## ARCHIVOS GENERADOS

- Diagnóstico completo: `herramientas_ia/resultados/DIAGNOSTICO_AFP_IHQ250237_v6.5.17_FALLO.md`
- Contexto AFP OCR: `herramientas_ia/resultados/IHQ250237_AFP_context.txt`
- Este resumen ejecutivo

---

**Fecha:** 2026-01-28
**Modificación probada:** v6.5.17
**Resultado:** FALLÓ - Filtro agregado en función incorrecta
**Acción:** Implementar Opción 1 (procesar solo descripción microscópica)
