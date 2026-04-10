# REPORTE COMPARATIVO: FUNC-06 IHQ250042
## Validación de extracción SV40 y C4D

**Fecha:** 2025-12-17  
**Caso:** IHQ250042  
**Score auditoría:** 66.7%  
**Estado:** ERROR (2 biomarcadores no extraídos)

---

## RESUMEN EJECUTIVO

El caso IHQ250042 se reprocesó usando FUNC-06 después de agregar alias para SV40 y C4D. Sin embargo, **los valores de ambos biomarcadores NO se extrajeron correctamente** a pesar de que:

1. Los alias están configurados correctamente en `biomarker_extractor.py`
2. Los biomarcadores se detectaron en `IHQ_ESTUDIOS_SOLICITADOS`
3. Las columnas IHQ_SV40 e IHQ_C4D se crearon correctamente

**Problema:** Los patrones regex NO capturan los formatos específicos del texto OCR del caso.

---

## ESTADO ACTUAL EN BASE DE DATOS

| Biomarcador | Valor en BD | Valor Esperado (OCR) | Estado |
|-------------|-------------|----------------------|--------|
| IHQ_SV40 | NO MENCIONADO | NEGATIVO | ERROR |
| IHQ_C4D | NO MENCIONADO | MINIMAMENTE POSITIVO EN CAPILARES PERITUBULARES (C4d 1) | ERROR |

---

## ANÁLISIS DETALLADO

### SV40 (Simian Virus 40 / Poliomavirus)

**Texto en OCR (líneas 52-53):**
```
...se efectuó marcación para SV40 (Poliomavirus) a través de la misma técnica y
resultó NEGATIVO.
```

**Patrón actual (línea 1902):**
```python
r'(?i)sv[^\w]*40[:\s]*(positivo|negativo)'
```

**Problema:**
- El patrón busca: `SV40:` o `SV40 ` seguido inmediatamente de `positivo|negativo`
- El texto tiene: `SV40 (Poliomavirus)` seguido de texto adicional, luego `resultó NEGATIVO`
- El patrón no captura el formato con paréntesis ni el verbo "resultó"

**Patrón sugerido:**
```python
r'(?i)sv[^\w]*40\s*(?:\([^)]+\))?\s*(?:.*?\s+)?result[oó]\s+(positivo|negativo)'
```

**Explicación del patrón:**
- `sv[^\w]*40` - Detecta "SV40" (con variantes)
- `\s*(?:\([^)]+\))?` - Captura opcional de texto en paréntesis como "(Poliomavirus)"
- `\s*(?:.*?\s+)?` - Permite cualquier texto intermedio
- `result[oó]\s+` - Detecta "resultó" o "resultado"
- `(positivo|negativo)` - Captura el valor

---

### C4D (Complement Component 4d)

**Texto en OCR (líneas 50-52):**
```
Se efectuó marcación para C4d a través de la técnica de inmunoperoxidasa indirecta en el tejido
del bloque de parafina. El resultado fue MINIMAMENTE POSITIVO EN CAPILARES PERITUBULARES
(C4d 1). Además, se efectuó marcación para SV40...
```

**Patrón actual (línea 1927):**
```python
r'(?i)c4[^\w]*d[:\s]*(positivo|negativo)'
```

**Problema:**
- El patrón busca: `C4d:` o `C4d ` seguido inmediatamente de `positivo|negativo`
- El texto tiene: `resultado fue MINIMAMENTE POSITIVO ... (C4d 1)`
- El patrón no captura:
  - El formato inverso (resultado antes del nombre del biomarcador)
  - La palabra "MINIMAMENTE" antes de "POSITIVO"
  - El valor numérico en paréntesis después del nombre

**Patrón sugerido:**
```python
r'(?i)(?:resultado|marcaci[oó]n)\s+(?:fue\s+)?(?:minimamente\s+)?(positivo|negativo)\s+.*?c4d\s*\(\d+\)'
```

**Explicación del patrón:**
- `(?:resultado|marcaci[oó]n)` - Detecta contexto previo
- `\s+(?:fue\s+)?` - Captura opcional "fue"
- `(?:minimamente\s+)?` - Captura opcional "minimamente"
- `(positivo|negativo)` - Captura el valor
- `\s+.*?c4d\s*\(\d+\)` - Busca "C4d (número)" después del valor

**Normalización adicional necesaria:**
```python
'minimamente positivo': 'POSITIVO DEBIL',
```

---

## SOLUCIÓN PROPUESTA

### Paso 1: Modificar biomarker_extractor.py

**Archivo:** `core/extractors/biomarker_extractor.py`

**Cambio 1 - SV40 (línea 1902):**
```python
# ANTES:
r'(?i)sv[^\w]*40[:\s]*(positivo|negativo)',

# AGREGAR NUEVO PATRÓN (antes del patrón actual):
r'(?i)sv[^\w]*40\s*(?:\([^)]+\))?\s*(?:.*?\s+)?result[oó]\s+(positivo|negativo)',
```

**Cambio 2 - C4D (línea 1927):**
```python
# ANTES:
r'(?i)c4[^\w]*d[:\s]*(positivo|negativo)',

# AGREGAR NUEVO PATRÓN (antes del patrón actual):
r'(?i)(?:resultado|marcaci[oó]n)\s+(?:fue\s+)?(?:minimamente\s+)?(positivo|negativo)\s+.*?c4d\s*\(\d+\)',
```

**Cambio 3 - Normalización C4D (línea 1935+):**
```python
'normalizacion': {
    'positivo': 'POSITIVO',
    'negativo': 'NEGATIVO',
    'positivo para ambas': 'POSITIVO',
    'negativo para ambas': 'NEGATIVO',
    'minimamente positivo': 'POSITIVO DEBIL',  # AGREGAR ESTA LÍNEA
    '+': 'POSITIVO',
    '-': 'NEGATIVO',
}
```

### Paso 2: Ejecutar FUNC-06 nuevamente

```bash
cd "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV9GESTOR_ONCOLOGIA"
python -c "
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
resultado = auditor.reprocesar_caso_completo('IHQ250042')
"
```

### Paso 3: Validar extracción

Después del reprocesamiento, verificar que:
- IHQ_SV40 = "NEGATIVO"
- IHQ_C4D = "POSITIVO DEBIL" o "MINIMAMENTE POSITIVO EN CAPILARES PERITUBULARES (C4d 1)"

---

## ARCHIVOS GENERADOS

- **Reporte JSON:** `herramientas_ia/resultados/FUNC-06_reprocesamiento_IHQ250042_20251217.json`
- **Reporte MD:** `herramientas_ia/resultados/FUNC-06_reprocesamiento_IHQ250042_20251217.md`
- **Auditoría:** `herramientas_ia/resultados/auditoria_inteligente_IHQ250042.json`

---

## CONCLUSIÓN

Los alias para SV40 y C4D se agregaron correctamente al sistema, pero los patrones de extracción necesitan ser ajustados para capturar los formatos específicos encontrados en el caso IHQ250042. 

**Próximo paso:** Aplicar los cambios sugeridos en `biomarker_extractor.py` y ejecutar FUNC-06 nuevamente para validar la extracción correcta.

---

**Generado por:** data-auditor (FUNC-06)  
**Timestamp:** 2025-12-17 03:42:55
