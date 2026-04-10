# DIAGNÓSTICO CRÍTICO: INHIBINA Extraída como NEGATIVO (Debería ser POSITIVO HETEROGÉNEO)

**Caso:** IHQ250270
**Versión extractor:** v6.5.77_unified_corrections
**Fecha análisis:** 2026-02-03
**Severidad:** CRÍTICA (ERROR de extracción + ERROR de auditoría)

---

## 1. RESUMEN EJECUTIVO

### Problema Detectado
- **OCR dice:** "positividad heterogénea para CKAE1AE3, inhibina y calretinina"
- **BD tiene:** `IHQ_INHIBINA = "NEGATIVO"`
- **Valor correcto:** `IHQ_INHIBINA = "POSITIVO HETEROGÉNEO"`

### Impacto
- Discrepancia crítica en biomarcador diagnóstico (tumor de células de la granulosa)
- El auditor NO detectó esta discrepancia (score: 100%, estado: OK)
- **FALSA SENSACIÓN DE CALIDAD:** Caso marcado como "perfecto" cuando tiene error crítico

---

## 2. EVIDENCIA DEL PROBLEMA

### 2.1 OCR Completo (debug_map línea 58)
