
================================================================================
REPORTE FINAL - REPROCESAMIENTO IHQ250035 (FUNC-06)
================================================================================
Fecha: 2025-12-16 03:42:08

1. ESTADO DE REPROCESAMIENTO:
   - Status: EXITOSO
   - Casos procesados: 50 casos del PDF (IHQ250001-IHQ250050)
   - Timestamp: 2025-12-16 03:38:20
   - Método: FUNC-06 (limpieza automática + reprocesamiento completo)

2. VALORES EN BASE DE DATOS (IHQ250035):

   Marcadores MMR:
   - MLH1: POSITIVO (expresión nuclear intacta)
   - MSH2: POSITIVO (expresión nuclear intacta)
   - MSH6: POSITIVO (expresión nuclear intacta)
   - PMS2: POSITIVO (expresión nuclear intacta)

   Otros:
   - HER2: NEGATIVO (score 0)

3. AUDITORIA INTELIGENTE (FUNC-01):
   - Score de validación: 100.0%
   - Estado final: OK
   - Validaciones OK: 9/9
   - Warnings: 0
   - Errores: 0

4. CORRECCION APLICADA:
   - Marcadores MMR (MLH1, MSH2, MSH6, PMS2) excluidos del extractor narrativo
   - Patrón específico en ADVANCED_BIOMARKER_PATTERNS captura correctamente
   - Normalización aplicada: "Expresión nuclear intact" -> "POSITIVO (expresión nuclear intacta)"

5. RESULTADO ESPERADO vs OBTENIDO:
   Valor esperado MLH1:  "POSITIVO (expresión nuclear intacta)"
   Valor obtenido MLH1:  "POSITIVO (expresión nuclear intacta)"
   
   Match: SI (valores coinciden)

6. TEXTO ORIGINAL EN OCR:
   "MLH1: Expresión nuclear intact"
   
   Procesamiento:
   - Extractor narrativo: EXCLUIDO (MMR no procesado por narrativo)
   - Patrón específico: APLICADO (ADVANCED_BIOMARKER_PATTERNS)
   - Normalización: "intact" -> "intacta", agregado "POSITIVO" explícito

================================================================================
CONCLUSION: CORRECCION EXITOSA
================================================================================

MLH1 = "POSITIVO (expresión nuclear intacta)"
Score = 100%

La exclusión de marcadores MMR del extractor narrativo funcionó correctamente.
El patrón específico en ADVANCED_BIOMARKER_PATTERNS capturó y normalizó el valor.
Todos los 4 marcadores MMR se extrajeron correctamente con el formato esperado.
