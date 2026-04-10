# VALIDACION FIXES v6.4.89 - IHQ250218

## CONTEXTO
- Caso: IHQ250218 (Linfoma Difuso de Celulas B Grandes)
- Version: v6.4.89
- Fixes aplicados: 3 (Ki-67, MUM1, CD3)

---

## RESULTADOS DESPUES DE REPROCESAMIENTO (FUNC-06)

### Score de Auditoria
- Score actual: 66.7%
- Estado: ERROR
- Warnings: 1
- Errores: 1

---

## VALIDACION DE FIXES INDIVIDUALES

### FIX 1: Ki-67 (patron "Ki67o es de 90%" - error OCR)
- Valor en BD: 90%
- Valor esperado: 90%
- Estado: OK CORRECTO
- Conclusion: Fix funcionando correctamente

### FIX 2: MUM1 (patron "el MUM1 es del 30%")
- Valor en BD: 30%
- Valor esperado: 30%
- Estado: OK CORRECTO
- Conclusion: Fix funcionando correctamente

### FIX 3: CD3 (post-filtro "linfocitos T acompanantes")
- Valor en BD: POSITIVO
- Valor esperado: NEGATIVO (sin contaminacion)
- Estado: FALLO (aun contaminado)
- Conclusion: Fix NO esta funcionando

---

## ANALISIS DETALLADO DEL FALLO CD3

### Contexto en OCR
Linea 40: Hay linfocitos T acompanantes CD3+, BCL2+

### Problema Identificado
El post-filtro v6.4.89 esta implementado en extract_narrative_biomarkers() (linea 6647-6669),
pero CD3 esta siendo extraido por OTRA funcion ANTES de que se aplique el filtro.

### Patrones que capturan CD3+ erroneamente
1. Patron generico: [BIOMARCADOR]+ (captura cualquier biomarcador seguido de +)
2. Patron: acompanantes [A-Z0-9]+ (captura biomarcador despues de acompanantes)
3. Patron: T acompanantes [A-Z0-9]+ (captura biomarcador despues de T acompanantes)

### Causa Raiz
- Extractor responsable: Probablemente extract_positive_list() o funcion similar
- Ejecucion: Se ejecuta ANTES de extract_narrative_biomarkers()
- Problema: CD3 ya esta en el diccionario cuando extract_narrative_biomarkers() ejecuta el post-filtro
- Resultado: El post-filtro busca clave CD3 o IHQ_CD3, pero el valor puede estar en otra clave

---

## SOLUCION PROPUESTA

### Opcion 1: Aplicar post-filtro en TODAS las funciones extractoras
Agregar el bloque de post-filtro v6.4.89 (lineas 6647-6669) al final de CADA funcion extractora.

### Opcion 2: Post-filtro centralizado en unified_extractor (RECOMENDADO)
Aplicar el filtro de "linfocitos T acompanantes" DESPUES de combinar resultados de todos los extractores,
en unified_extractor.py.

### Opcion 3: Pre-filtro en texto
Antes de ejecutar extractores, detectar patron "linfocitos T acompanantes CD3+, BCL2+" y ELIMINAR
esa linea del texto OCR temporalmente.

---

## RESUMEN EJECUTIVO

Fixes exitosos: 2/3 (Ki-67 OK, MUM1 OK)
Fixes fallidos: 1/3 (CD3 FALLO)
Score mejoro: No (66.7% - bajo por otros errores)
Accion requerida: Implementar post-filtro centralizado para CD3/BCL2
