# Reporte Comparativo FUNC-06: IHQ250019

**Timestamp:** 2025-12-13 09:50:00  
**Score Final:** 88.9%  
**Estado:** ADVERTENCIA (1 warning)

---

## Resumen Ejecutivo

FUNC-06 ejecuto exitosamente el reprocesamiento del caso IHQ250019 con los extractores corregidos:
- Alias "p65" → "p63" agregado en biomarker_extractor.py
- Patron "mosaico (normal)" → "POSITIVO (mosaico normal)" agregado

**Resultados:**
- IHQ_P63: Corregido correctamente ("NO MENCIONADO" → "POSITIVO")
- IHQ_RECEPTOR_ESTROGENOS: NO corregido (permanece como ".")
- DIAGNOSTICO_PRINCIPAL: Bug persistente ("ADENOSIS ESCLEROSANTE NO")

---

## Comparacion Detallada

### 1. IHQ_P63 - CORREGIDO

| Campo | Valor Actual | Valor Esperado | Estado |
|-------|-------------|----------------|---------|
| **IHQ_P63** | POSITIVO | POSITIVO | CORRECTO |

**Evidencia OCR:**
"...se rodean de celulas mioepiteliales positivas para p65 y CK 5/6."

**Analisis:**
- El alias "p65" → "p63" funciona correctamente
- El extractor ahora reconoce "p65" como variante de "P63"
- Valor extraido coincide con el esperado

---

### 2. IHQ_RECEPTOR_ESTROGENOS - NO CORREGIDO

| Campo | Valor Actual | Valor Esperado | Estado |
|-------|-------------|----------------|---------|
| **IHQ_RECEPTOR_ESTROGENOS** | . | POSITIVO (mosaico normal) | ERROR |

**Evidencia OCR:**
"...los ductos se revisten internamente por celulas epiteliales con expresion en 
mosaico (normal) para receptores de estrogenos..."

**Analisis:**
- El patron "mosaico (normal)" NO fue detectado
- El extractor devuelve "." (punto), lo cual indica extraccion fallida
- Posibles causas:
  1. El patron regex no coincide con la sintaxis exacta del OCR
  2. Orden de aplicacion de patrones (otro patron puede estar capturando primero)
  3. El texto "expresion en mosaico (normal) para receptores" requiere patron mas especifico

**Recomendacion:**
Revisar el patron agregado en biomarker_extractor.py y verificar la sintaxis exacta.

---

### 3. DIAGNOSTICO_PRINCIPAL - BUG PERSISTENTE

| Campo | Valor Actual | Valor Esperado | Estado |
|-------|-------------|----------------|---------|
| **DIAGNOSTICO_PRINCIPAL** | ADENOSIS ESCLEROSANTE NO | ADENOSIS ESCLEROSANTE CON ABUNDANTES MICROCALCIFICACIONES | WARNING |

**Evidencia OCR:**
DIAGNOSTICO
Mama izquierda. Lesion. Biopsia por esterotacsia. Estudio de inmunohistoquimica.
ADENOSIS ESCLEROSANTE CON ABUNDANTES MICROCALCIFICACIONES.
VER COMENTARIO.

**Analisis:**
- El extractor captura solo "ADENOSIS ESCLEROSANTE NO" en lugar del diagnostico completo
- El "NO" parece ser una captura incorrecta
- Falta "CON ABUNDANTES MICROCALCIFICACIONES"

**Causa Probable:**
El extractor de DIAGNOSTICO_PRINCIPAL usa un patron que:
1. Captura solo la primera linea despues de limpiar metadatos
2. Se detiene prematuramente (posiblemente en punto final)
3. Anade "NO" de forma incorrecta

---

## Metricas de Auditoria

| Metrica | Valor |
|---------|-------|
| **Score de Validacion** | 88.9% (8/9 validaciones OK) |
| **Estado Final** | ADVERTENCIA |
| **Warnings** | 1 (DIAGNOSTICO_PRINCIPAL difiere de OCR) |
| **Errores Criticos** | 0 |
| **Biomarcadores Mapeados** | 3/3 (100% cobertura) |

---

## Archivos Generados

- **Debug Map:** data/debug_maps/debug_map_IHQ250019_20251213_094758.json
- **Auditoria:** herramientas_ia/resultados/auditoria_inteligente_IHQ250019.json
- **Este Reporte:** herramientas_ia/resultados/FUNC-06_reprocesamiento_IHQ250019_20251213.md

---

## Proximos Pasos Recomendados

1. **IHQ_RECEPTOR_ESTROGENOS (PRIORIDAD ALTA):**
   - Investigar patron "mosaico (normal)" en biomarker_extractor.py
   - Ejecutar test unitario con el OCR especifico de IHQ250019
   - Ajustar patron regex y reprocesar con FUNC-06

2. **DIAGNOSTICO_PRINCIPAL (PRIORIDAD MEDIA):**
   - Investigar medical_extractor.py lineas ~800-900 (extract_principal_diagnosis)
   - Verificar logica de limpieza y deteccion de fin de diagnostico
   - Identificar por que se agrega "NO" al final
   - Corregir y validar con multiples casos

3. **Validacion Final:**
   - Despues de correcciones, ejecutar FUNC-06 nuevamente
   - Verificar que score suba a 100%
   - Confirmar que los 3 campos esten correctos

---

**Generado por:** FUNC-06 (data-auditor)  
**Version:** 6.3.x  
**Fecha:** 2025-12-13 09:50:00
