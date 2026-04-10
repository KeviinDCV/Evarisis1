# INVESTIGACIÓN: Valor "EXPRESION MODERADA" en IHQ250999

**Fecha:** 2025-11-14  
**Caso:** IHQ250999  
**Problema:** Campo con valor "EXPRESION MODERADA" sin normalización estándar POSITIVO/NEGATIVO

---

## HALLAZGOS

### 1. CAMPO AFECTADO

**Columnas BD con "EXPRESION MODERADA":**
- `IHQ_RECEPTOR_ESTROGENOS`: "EXPRESION MODERADA"
- `Factor pronostico`: "Receptor de Estrógeno: EXPRESION MODERADA"

### 2. CONTEXTO DEL OCR (PDF)

**Descripción Microscópica:**
```
Se realizan estudios de inmunohistoquímica con el método inmunoperoxidasa en el 
sistema ROCHE VENTANA. Se verifica el rendimiento de los controles externos e 
internos y se observa: Se observa células mioepiteliales positivas para P63, 
calponina y CK5/6, recubriendo los tallos fibrovasculares, con expresión 
moderada de los receptores de estrógeno.
```

**Texto clave:** "con expresión moderada de los receptores de estrógeno"

### 3. BIOMARCADOR IDENTIFICADO

**Biomarcador:** Receptor de Estrógeno (ER)  
**Contexto:** Papiloma intraductal con células mioepiteliales  
**Formato del PDF:** Narrativo (no tabular)

### 4. ANÁLISIS DEL EXTRACTOR

**Ubicación:** core/extractors/biomarker_extractor.py

**Configuración actual del biomarcador ER (líneas 236-263):**
- valores_posibles incluye explícitamente "EXPRESION MODERADA"
- normalizacion convierte "moderada" a "EXPRESION MODERADA"

**Patrón que captura (línea 241):**
```
expresion de receptor de estrogeno: (.+?)
```

**Flujo de extracción:**
1. El patrón captura: "expresión moderada de los receptores de estrógeno"
2. Extrae el valor: "moderada" (o posiblemente toda la frase)
3. La normalización convierte "moderada" a "EXPRESION MODERADA"
4. El sistema ACEPTA el valor porque está en valores_posibles

### 5. ES UN ERROR DEL EXTRACTOR?

**NO.** El extractor está funcionando según su diseño actual.

**Comportamiento actual:**
- El sistema está configurado para capturar y almacenar literalmente "EXPRESION MODERADA"
- Esto NO es un bug, es una decisión de diseño

---

## OPCIONES DE NORMALIZACIÓN

### OPCIÓN 1: Normalizar a "POSITIVO (moderada)"

**Ventajas:**
- Formato consistente con otros biomarcadores
- Compatible con análisis estadísticos POSITIVO/NEGATIVO
- Conserva información de intensidad

**Implementación:**
```python
# En normalizacion de ER/PR:
'moderada': 'POSITIVO (intensidad moderada)',
'débil': 'POSITIVO (intensidad débil)',
'intensa': 'POSITIVO (intensidad fuerte)',
'fuerte': 'POSITIVO (intensidad fuerte)',
```

---

### OPCIÓN 2: Normalizar a "POSITIVO MODERADO" (RECOMENDADA)

**Ventajas:**
- Formato más compacto
- Mantiene calificador de intensidad
- Compatible con patrones existentes de PDL-1, HER2, etc.

**Implementación:**
```python
# En normalizacion de ER/PR:
'moderada': 'POSITIVO MODERADO',
'débil': 'POSITIVO DÉBIL',
'intensa': 'POSITIVO INTENSO',
'fuerte': 'POSITIVO FUERTE',
```

---

### OPCIÓN 3: Mantener literal "EXPRESION MODERADA" (status quo)

**Desventajas:**
- NO compatible con análisis estadísticos basados en POSITIVO/NEGATIVO
- Formato inconsistente con otros casos
- Dificulta filtros y queries SQL

---

## RECOMENDACIÓN

**OPCIÓN 2: Normalizar a "POSITIVO MODERADO"**

**Razones:**
1. Formato consistente con otros biomarcadores que incluyen intensidad
2. Compatible con análisis estadísticos (filtros por POSITIVO/NEGATIVO)
3. Conserva información de intensidad sin formato verboso
4. Fácil de implementar (cambio simple en diccionario de normalización)

**Cambio necesario:**
```python
# Archivo: core/extractors/biomarker_extractor.py
# Líneas: 252-263 (ER) y 296-307 (PR)

'normalizacion': {
    'positivo': 'POSITIVO',
    'negativo': 'NEGATIVO',
    '+': 'POSITIVO',
    '-': 'NEGATIVO',
    'moderada': 'POSITIVO MODERADO',
    'débil': 'POSITIVO DÉBIL',
    'debil': 'POSITIVO DÉBIL',
    'intensa': 'POSITIVO INTENSO',
    'fuerte': 'POSITIVO FUERTE',
}
```

---

## SIGUIENTE PASO

**SI SE APRUEBA OPCIÓN 2:**

1. Modificar biomarker_extractor.py (2 lugares: ER y PR)
2. Reprocesar caso IHQ250999 usando FUNC-06
3. Validar resultado con FUNC-01

**Resultado esperado:**
- IHQ_RECEPTOR_ESTROGENOS: "POSITIVO MODERADO"
- Factor pronostico: "Receptor de Estrógeno: POSITIVO MODERADO"

---

## RESUMEN EJECUTIVO

| Aspecto | Detalle |
|---------|---------|
| **Problema** | "EXPRESION MODERADA" no normalizado a POSITIVO/NEGATIVO |
| **Causa** | Diseño actual del extractor permite valores literales de intensidad |
| **Campo afectado** | IHQ_RECEPTOR_ESTROGENOS, Factor pronostico |
| **Caso ejemplo** | IHQ250999 (papiloma intraductal) |
| **Texto OCR** | "con expresión moderada de los receptores de estrógeno" |
| **Solución recomendada** | Normalizar a "POSITIVO MODERADO" |
| **Archivos a modificar** | core/extractors/biomarker_extractor.py (2 lugares) |
| **Reprocesamiento** | Sí (casos existentes con este formato) |

---

**Conclusión:** El sistema está capturando correctamente lo que dice el PDF, pero la normalización actual no es óptima para análisis estadísticos. Se recomienda normalizar "expresión moderada" a "POSITIVO MODERADO" para consistencia y compatibilidad con el resto del sistema.
