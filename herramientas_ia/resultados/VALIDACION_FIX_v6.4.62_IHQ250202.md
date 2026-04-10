# Validacion Fix v6.4.62 - IHQ250202

**Fecha:** 2026-01-09  
**Patron Modificado:** `biomarker_extractor.py` linea 880  
**Caso de Prueba:** IHQ250202  

---

## Problema Original

**OCR:**
```
Los marcadores napsina y TTF-1 - son negativos.
```

**Patron v6.4.61 (INCORRECTO):**
```python
r'(?:marcadores?\s+(?:inmunohistoquimicos?\s+)?|el\s+)([^-]+?)\s*-\s*(?:son?\s+)?negativ[oa]s?'
```

**Problema:**
- `[^-]+?` (non-greedy) capturaba solo "napsina" y paraba
- TTF-1 NO se extraia porque ya habia un guion antes
- Resultado: Solo NAPSIN = NEGATIVO

---

## Correccion Aplicada v6.4.62

**Patron Nuevo:**
```python
r'(?:marcadores?\s+(?:inmunohistoquimicos?\s+)?|el\s+)(.+?)\s*-\s*(?:son?\s+)?negativ[oa]s?'
```

**Cambio:**
- `[^-]+?` → `.+?` (cualquier caracter, no solo "no-guion")
- Permite capturar "napsina y TTF-1" completo antes del guion final
- El extractor luego divide la lista correctamente

---

## Resultado de Reprocesamiento (FUNC-06)

**Comando Ejecutado:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250202 --func-06
```

**Proceso:**
1. Elimino registros BD del rango 160-211
2. Elimino debug_maps antiguos
3. Reproceso PDF completo con v6.4.62
4. Genero nuevo debug_map_IHQ250202_20260109_152724.json
5. Actualizo BD con datos nuevos

**Estado:** EXITOSO (49 casos reprocesados)

---

## Validacion con Auditoria Inteligente (FUNC-01)

**Comando Ejecutado:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250202 --inteligente
```

**Valores Extraidos (debug_map):**
```json
{
  "IHQ_TTF1": "NEGATIVO",
  "IHQ_NAPSIN": "NEGATIVO",
  "IHQ_ESTUDIOS_SOLICITADOS": "TTF-1, NAPSIN"
}
```

**Resultado:**
- Score: 88.9%
- Estado: OK
- TTF-1: NEGATIVO ✅ (extraido correctamente)
- NAPSIN: NEGATIVO ✅ (extraido correctamente)

---

## Analisis del Score 88.9%

**Por que NO es 100%:**

El auditor marco TTF-1 como "valor incorrecto":
```json
{
  "biomarcador": "TTF-1",
  "columna": "IHQ_TTF1",
  "valor_bd": "NEGATIVO",
  "valor_ocr": "-"
}
```

**Problema de Validacion:**
- El auditor extrae del OCR solo el guion "-" como valor esperado
- Compara "NEGATIVO" (BD) con "-" (OCR)
- Los considera diferentes → genera ERROR

**Esto NO es un problema de extraccion:**
- La extraccion funciona perfectamente (NEGATIVO es el valor correcto)
- Es un problema de validacion del auditor (esperaba encontrar "-")
- El patrón v6.4.62 extrajo CORRECTAMENTE

---

## Verificacion de NO Regresion

**Casos de Referencia a Validar:**
- IHQ250202: TTF-1 + NAPSIN negativos ✅ (validado)
- Casos con patrones similares pendientes de validacion masiva

**Recomendacion:**
- Ejecutar FUNC-05B para validar todos los casos del rango 160-211
- Confirmar que no hay regresiones en otros casos con patrones similares

---

## Conclusion

### Estado del Fix v6.4.62

✅ **EXITOSO**

**Evidencia:**
1. Patron captura "napsina y TTF-1" completo antes del guion
2. Ambos biomarcadores se extraen correctamente como NEGATIVO
3. IHQ_ESTUDIOS_SOLICITADOS contiene ambos biomarcadores
4. NO hay confusion entre biomarcadores
5. NO hay valores vacios o "NO MENCIONADO"

**Score 88.9% es un FALSO NEGATIVO:**
- Problema de validacion del auditor, NO de extraccion
- Extraccion real: 100% correcta

### Proximos Pasos

1. ✅ Correccion v6.4.62 validada y funcional
2. ⏳ Pendiente: Validacion masiva con FUNC-05B (casos 160-211)
3. ⏳ Pendiente: Ajustar logica de validacion del auditor para reconocer "-" como NEGATIVO

### Archivos Modificados

- `core/extractors/biomarker_extractor.py` linea 880 (v6.4.62)
- Patron especifico para "marcadores X - negativos"

### Casos Afectados

- IHQ250202: TTF-1 + NAPSIN ✅ CORREGIDO
- Otros casos en rango 160-211: Pendiente validacion masiva

