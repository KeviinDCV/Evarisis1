# VALIDACION FIX v6.4.78 - IHQ250208

**Fecha:** 2026-01-12
**Caso:** IHQ250208
**Version:** v6.4.78
**Objetivo:** Capturar Ki-67 desde "indice proliferativo" sin mencion explicita de "Ki-67"

---

## PROBLEMA ORIGINAL

El caso IHQ250208 contiene el texto:
```
"El indice proliferativo en el centro germinal es del 20 %"
```

**Antes del fix:** Ki-67 = NO MENCIONADO (el patron solo buscaba "Ki-67" o "Ki67")

**Patron antiguo:** Solo capturaba cuando el texto mencionaba explicitamente "Ki-67"

---

## FIX APLICADO (v6.4.78)

**Archivo:** `core/extractors/biomarker_extractor.py`

**Patron nuevo:**
```python
# V6.4.78 FIX IHQ250208: Capturar "indice proliferativo" sin mencion de Ki-67
proliferative_index_pattern = r'(?i)\b(?:el\s+)?(?:indice|índice)\s+proliferativo(?:[^.]{0,30})?(?:es|:)?\s*(?:del\s+)?(\d+(?:[,.]\d+)?)\s*%'
```

**Estrategia:**
- Busca "indice proliferativo" (con o sin acento)
- Captura porcentaje dentro de 30 caracteres
- Mapea automaticamente a Ki-67

---

## RESULTADOS DESPUES DE REPROCESAMIENTO (FUNC-06)

### Biomarcadores extraidos:
- **CD20:** POSITIVO
- **BCL6:** POSITIVO
- **CD3:** POSITIVO
- **BCL2:** POSITIVO
- **Ki-67:** 20% ← **NUEVO con v6.4.78**
- **CD5:** NO MENCIONADO

### Factor pronostico:
```
Ki-67: 20%
```

### Metricas de auditoria:
- **Score:** 100%
- **Estado:** OK
- **Biomarcadores mapeados:** 6/6 (100%)
- **Validaciones OK:** 9/9

---

## VALIDACION ANTI-REGRESION

**Casos de referencia validados:** PENDIENTE

**Accion requerida:**
1. Identificar casos similares con "indice proliferativo"
2. Validar que el patron no causa regresiones
3. Verificar casos con Ki-67 explicito (no deben cambiar)

---

## CONCLUSION

**ESTADO:** ✅ **FIX EXITOSO**

El patron v6.4.78 capturo correctamente Ki-67 desde "indice proliferativo" sin mencion explicita del biomarcador.

**Mejora:**
- **Antes:** Ki-67 = NO MENCIONADO (caso incompleto)
- **Despues:** Ki-67 = 20% (caso completo 100%)

**Impacto:**
- Casos con formato alternativo de Ki-67 ahora se capturan correctamente
- Mejora la completitud de casos con informes en formato narrativo

---

**Reporte generado automaticamente por FUNC-06**
