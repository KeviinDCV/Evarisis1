# REPORTE FINAL - VALIDACION IHQ251011 v6.1.6

## RESUMEN EJECUTIVO

**Fecha:** 2025-11-04
**Caso:** IHQ251011
**Version validada:** v6.1.6
**Reprocesamiento:** FUNC-06 ejecutado exitosamente

**RESULTADO GLOBAL:**
- Biomarcadores correctos: 4/6 (66.7%)
- Errores corregidos: 2/4 (P53, Ki-67)
- Errores pendientes: 2/4 (IDH1, ATRX)

---

## TEXTO ORIGINAL DEL PDF



---

## TABLA COMPARATIVA COMPLETA

| Biomarcador | VERSION INICIAL | DESPUES v6.1.5 | DESPUES v6.1.6 | ESPERADO | ESTADO |
|-------------|-----------------|----------------|----------------|----------|--------|
| IHQ_P53     | NO MENCIONADO   | CONTRIBUTIVA   | NO ES CONTRIBUTIVA | NO ES CONTRIBUTIVA | CORRECTO |
| IHQ_KI-67   | NO MENCIONADO   | 10%            | 10%            | 10%      | CORRECTO |
| IHQ_IDH1    | (no existia)    | N/A            | POSITIVO       | POSITIVO (MUTADO) | ERROR |
| IHQ_ATRX    | (no existia)    | N/A            | AUSENCIA DE EXPRESION... | NEGATIVO (MUTADO) | ERROR |
| IHQ_GFAP    | POSITIVO        | POSITIVO       | POSITIVO       | POSITIVO | CORRECTO |
| IHQ_CD34    | NEGATIVO        | NEGATIVO       | NEGATIVO       | NEGATIVO | CORRECTO |

---

## SCORE FINAL

- Errores corregidos: 2/4 (P53, Ki-67)
- Errores pendientes: 2/4 (IDH1, ATRX)
- Biomarcadores correctos: 4/6
- Porcentaje exito: 66.7%
- Mejora total: +33.3% (de v6.1.4 a v6.1.6)

---

## ERRORES PENDIENTES

### ERROR 1: IHQ_IDH1 - Falta capturar (MUTADO)
- Patron actual captura solo "positiva" pero no "(mutado)"
- Normalizacion definida pero NO se aplica
- Solucion: Post-procesamiento o modificar patron

### ERROR 2: IHQ_ATRX - No normaliza "Ausencia de expresion"
- Patron captura texto completo sin normalizar
- Deberia convertir a "NEGATIVO (MUTADO)"
- Solucion: Post-procesamiento o modificar patron

---

**Archivos generados:**
- FUNC-06_validacion_final_IHQ251011_v6.1.6.json
- REPORTE_FINAL_IHQ251011_v6.1.6.md
