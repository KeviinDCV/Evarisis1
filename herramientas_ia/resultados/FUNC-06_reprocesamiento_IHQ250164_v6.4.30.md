
=================================================================
REPORTE DE VALIDACION FUNC-06: IHQ250164 (v6.4.30)
=================================================================

Timestamp: 2026-01-08 02:56:15
Debug_map: debug_map_IHQ250164_20260108_025418.json

-----------------------------------------------------------------
CORRECCIONES APLICADAS v6.4.30
-----------------------------------------------------------------

1. Normalizacion previa:
   OK "SOX -11" -> "SOX-11" (espacios internos)

2. Patron mixto (captura "negativa con el [lista]"):
   OK Implementado en biomarker_extractor.py linea 3663

3. Sobrescritura POSITIVO -> NEGATIVO:
   OK Alta confianza al detectar lista de negativos

-----------------------------------------------------------------
VALORES EXTRAIDOS (BD)
-----------------------------------------------------------------

IHQ_SOX11:      NEGATIVO
IHQ_CICLINA_D1: POSITIVO
IHQ_BCL6:       NEGATIVO
IHQ_CD10:       NEGATIVO
IHQ_CD5:        NEGATIVO

-----------------------------------------------------------------
CONTEXTO OCR
-----------------------------------------------------------------

Texto relevante:
"...negativa con el CD5, CD10, BCL6, IgD, SOX -11 y Ciclyna D1..."

Lista de negativos detectada:
- CD5 -> NEGATIVO OK
- CD10 -> NEGATIVO OK
- BCL6 -> NEGATIVO OK
- IgD -> N/A (sin columna)
- SOX-11 -> NEGATIVO OK (normalizado desde "SOX -11")
- Ciclyna D1 -> POSITIVO ADVERTENCIA (capturado por patron previo)

-----------------------------------------------------------------
VALIDACION DE RESULTADOS
-----------------------------------------------------------------

Score final: 88.9%
Estado: OK

Validaciones correctas:
OK SOX11: NEGATIVO (esperado: NEGATIVO)
OK BCL6: NEGATIVO (esperado: NEGATIVO)
OK CD10: NEGATIVO (esperado: NEGATIVO)
OK CD5: NEGATIVO (esperado: NEGATIVO)

Validaciones con discrepancia:
ADVERTENCIA CICLINA_D1: POSITIVO (esperado: NEGATIVO)

-----------------------------------------------------------------
ANALISIS DE DISCREPANCIA
-----------------------------------------------------------------

Biomarcador: CICLINA_D1
Valor BD: POSITIVO
Valor esperado: NEGATIVO

Contexto OCR:
"negativa con el CD5, CD10, BCL6, IgD, SOX -11 y Ciclyna D1"

CAUSA RAIZ:
- Patron anterior detecto: "Ciclyna D1" como POSITIVO
- Patron mixto v6.4.30 deberia SOBRESCRIBIR con NEGATIVO
- Sin embargo, CICLINA_D1 aparece con valor POSITIVO

HIPOTESIS:
1. Patron previo ejecuta DESPUES del patron mixto
2. Orden de ejecucion de patrones permite sobrescritura incorrecta
3. Necesario agregar logica de confianza/prioridad

-----------------------------------------------------------------
CONCLUSION
-----------------------------------------------------------------

Estado general: PARCIALMENTE EXITOSO

Correcciones exitosas (4/5):
OK SOX11 normalizado y extraido como NEGATIVO
OK CD5 extraido como NEGATIVO (no confundido con linfocitos T CD5+)
OK BCL6 extraido como NEGATIVO
OK CD10 extraido como NEGATIVO

Correccion pendiente (1/5):
ERROR CICLINA_D1 sigue siendo POSITIVO (esperado: NEGATIVO)

PROXIMO PASO:
Investigar orden de ejecucion de patrones para garantizar que
patron mixto v6.4.30 tenga prioridad sobre detecciones previas.

=================================================================
