# AUDITORIA COMPLETA - CASO IHQ250981

**Fecha:** 2025-10-22 18:52:00
**Auditor:** data-auditor (nivel profundo)

## RESUMEN EJECUTIVO

**Estado:** ADVERTENCIA - FALSA COMPLETITUD
- Precision reportada: 100%
- Score de validacion: 50%
- Problemas criticos: 4

## PROBLEMAS DETECTADOS

### 1. E-CADHERINA NO CAPTURADA (CRITICO)
- PDF menciona: E-Cadherina POSITIVO
- BD: Columna no existe
- Solucion: Agregar biomarcador al sistema

### 2. IHQ_ORGANO INCORRECTO (CRITICO)
- BD: MASTECTOMIA RADICAL
- Deberia ser: MAMA IZQUIERDA
- Problema: Captura procedimiento, no organo

### 3. DIAGNOSTICO_PRINCIPAL CONTAMINADO (ALTO)
- Incluye: TAMAÑO TUMORAL
- Problema: No se detiene en primer guion

### 4. FACTOR_PRONOSTICO INCOMPLETO (ALTO)
- Solo tiene biomarcadores IHQ
- Falta: Tamaño, margenes, invasion, ganglios

## SUGERENCIAS

1. python herramientas_ia/editor_core.py --agregar-biomarcador E-CADHERINA
2. python herramientas_ia/editor_core.py --editar-extractor IHQ_ORGANO
3. python herramientas_ia/editor_core.py --editar-extractor DIAGNOSTICO_PRINCIPAL
4. python herramientas_ia/editor_core.py --editar-extractor FACTOR_PRONOSTICO
