# Investigación de Errores - Caso IHQ251017

**Fecha:** 2025-11-07
**Agente:** Claude (data-auditor)
**Caso:** IHQ251017 (Biopsia de médula ósea)

---

## Resumen Ejecutivo

Se investigaron 2 errores críticos detectados en la auditoría del caso IHQ251017:
1. **DIAGNOSTICO_COLORACION** no extraído (marcado como "NO APLICA" pero existe en OCR)
2. **Campo Organo** contaminado con texto administrativo y duplicados

Ambos problemas tienen su origen en los extractores de `medical_extractor.py`.

---

## Problema 1: DIAGNOSTICO_COLORACION No Extraído

### Hallazgos

**Estado en BD:** `"NO APLICA"`
**Valor esperado en OCR:** `"CELULARIDAD..."` (diagnóstico del estudio M previo)
**Patrón detectado por auditoría:** `bloque M + diagnóstico de "..."`

### Análisis del Extractor

**Ubicación:** `core/extractors/medical_extractor.py:379-578`
**Función:** `extract_diagnostico_coloracion(text: str)`

La función tiene **múltiples estrategias** de extracción en orden de prioridad:

1. **PRIORIDAD -3.5** (línea 426): Diagnóstico entrecomillado ANTES de INFORME PRELIMINAR
2. **PRIORIDAD -3** (línea 447): Tumores gliales con patrón "LESIÓN NEOPLÁSICA... A CLASIFICAR"
3. **PRIORIDAD -2.7** (línea 467): **Diagnóstico del bloque M previo** ← RELEVANTE
4. **PRIORIDAD -2.5** (línea 517): Tumor bifásico a clasificar
5. **PRIORIDAD -2** (línea 535): Biopsia de hueso/médula ósea con diagnóstico previo ← RELEVANTE
6. Otras estrategias de menor prioridad

### Diagnóstico del Problema

El caso IHQ251017 es una **biopsia de médula ósea** con diagnóstico previo del estudio M.

**Patrón esperado** (PRIORIDAD -2.7, línea 484):
```regex
(?:rotulado\s+)?(?:como\s+)?(?:bloque\s+)?["\'\u201c\u201d]?M[\dA-Z-]+(?:\s+y\s+M[\dA-Z-]+)?["\'\u201c\u201d]?\s*[,\s]+(?:el\s+cual\s+|que\s+)?corresponden?\s+a\s+["\'\u201c\u201d][^"\'\u201c\u201d]+["\'\u201c\u201d]\s*,?\s*con\s+diagn[óo]stico\s+de\s+["\'\u201c\u201d\s]+(.*?)["\'\u201c\u201d]
```

**Patrón alternativo** (PRIORIDAD -2, línea 541):
```regex
con\s+diagn[óo]stico\s+de\s+"([^"]+)"\s*por\s+lo\s+que\s+se\s+realiza
```

### Posibles Causas

1. **El OCR del PDF puede tener variaciones** que no coinciden con los patrones regex
2. **Comillas Unicode diferentes** (el patrón soporta `["\'\u201c\u201d]` pero puede haber otras)
3. **Espacios o saltos de línea** entre "diagnóstico" y "de" que rompen el patrón
4. **Texto previo/posterior** que hace que el patrón no coincida correctamente

### Corrección Recomendada

**NECESITA ACCESO AL OCR COMPLETO** del caso IHQ251017 para:
1. Identificar el patrón exacto del texto en el PDF
2. Verificar si hay variaciones en comillas, espacios o formato
3. Ajustar/añadir un nuevo patrón específico si es necesario

**Archivo objetivo:** `pdfs_patologia/IHQ DEL 980 AL 1037.pdf` (contiene IHQ251017)

---

## Problema 2: Campo Organo Contaminado

### Hallazgos

**Valor actual en BD:**
```
BIOPSIA DE MEDULA OSEA IHQ251017-B ESTUDIO DE INMUNOHISTOQUIMICA 898807 ESTUDIO ANATOMOPATOLOGICO DE MARCACION INMUNOHISTOQUIMICA BASICA (ESPECIFICO) BLOQUES Y LAMINAS BIOPSIA DE MEDULA OSEA
```

**Valor esperado:**
```
BIOPSIA DE MEDULA OSEA
```

**Problemas detectados:**
- Texto duplicado: "BIOPSIA DE MEDULA OSEA" aparece 2 veces
- Código de caso: "IHQ251017-B"
- Múltiples fragmentos de texto administrativo
- Información de estudios y bloques

### Análisis del Extractor

**Ubicación:** `core/extractors/medical_extractor.py:2473-2566`
**Función:** `extract_organ_information(text: str)`

La función tiene **7 estrategias** de extracción:

1. Patrón "TUMOR REGION" + "INTRADURAL" (multilinea)
2. Búsqueda en tabla de estudios solicitados
3. **Patrón "Bloques y laminas ÓRGANO"** ← PROBLEMA ENCONTRADO
4. Patrón directo de órgano (PATTERNS_IHQ['organo_raw'])
5. Búsqueda en estudios solicitados con keywords
6. Búsqueda en descripción macroscópica con keywords
7. Búsqueda en todo el texto con keywords

### Diagnóstico del Problema

**Estrategia 3** (línea 2517-2528) está capturando demasiado:

```python
bloques_pattern = r'bloques\s+y\s+laminas\s*\n?\s*([A-Z\s]+?(?:\n[A-Z\s]+?)?)(?:\s+INFORME|\s+ESTUDIO|\n\s*INFORME|\n\s*ESTUDIO|$)'
```

Este patrón captura:
- `[A-Z\s]+?` → Cualquier secuencia de mayúsculas y espacios (NO RESTRICTIVO)
- Continúa hasta encontrar "INFORME" o "ESTUDIO" o fin de texto
- En el caso IHQ251017, captura TODO desde "BIOPSIA DE MEDULA OSEA" hasta el final

**Texto capturado probablemente:**
```
BIOPSIA DE MEDULA OSEA IHQ251017-B ESTUDIO DE INMUNOHISTOQUIMICA 898807
ESTUDIO ANATOMOPATOLOGICO DE MARCACION INMUNOHISTOQUIMICA BASICA (ESPECIFICO)
BLOQUES Y LAMINAS BIOPSIA DE MEDULA OSEA
```

### Corrección Propuesta

**Opción 1: Limitar el patrón a órganos conocidos**

Modificar el patrón para que solo capture hasta encontrar un delimitador administrativo:

```python
# MEJORADO: Detener en códigos IHQ, números o texto administrativo
bloques_pattern = r'bloques\s+y\s+laminas\s*\n?\s*([A-Z\s]+?)(?:\s+IHQ|\s+ESTUDIO|\s+INFORME|\s+\d{5,}|\n\s*INFORME|\n\s*ESTUDIO|$)'
```

**Cambios:**
- Añadido `\s+IHQ` para detener antes de códigos de caso
- Añadido `\s+\d{5,}` para detener antes de números largos (códigos administrativos)
- Cambiado `[A-Z\s]+?` (lazy) para evitar captura excesiva

**Opción 2: Post-procesamiento en normalize_organ_name**

Añadir limpieza en `normalize_organ_name()` (línea 2569):

```python
def normalize_organ_name(organ_text: str) -> str:
    """Normaliza el nombre del órgano"""
    if not organ_text:
        return 'ORGANO_NO_ESPECIFICADO'

    # NUEVO: Limpiar códigos IHQ y texto administrativo
    # Detener antes de códigos IHQ
    organ_text = re.split(r'\s+IHQ\d+', organ_text)[0]
    # Detener antes de "ESTUDIO DE" (texto administrativo)
    organ_text = re.split(r'\s+ESTUDIO\s+DE', organ_text)[0]
    # Detener antes de números largos (códigos)
    organ_text = re.split(r'\s+\d{5,}', organ_text)[0]

    organ_lower = organ_text.lower().strip()

    # ... resto del código existente
```

**Opción 3: Priorizar IHQ_ORGANO**

Como el campo `IHQ_ORGANO` está limpio (`"MEDULA ÓSEA"`), podría priorizarse sobre el campo `Organo` contaminado. Esto requiere cambios en el flujo de datos en `unified_extractor.py`.

### Corrección Recomendada

**Implementar Opción 1 + Opción 2** (defensa en profundidad):

1. Mejorar el patrón regex en `extract_organ_information()` línea 2519
2. Añadir limpieza adicional en `normalize_organ_name()` línea 2569
3. Verificar que no afecte otros casos existentes

---

## Próximos Pasos

### Para DIAGNOSTICO_COLORACION:
1. ✅ **NECESITA OCR COMPLETO:** Extraer el texto OCR del PDF `IHQ DEL 980 AL 1037.pdf` para el caso IHQ251017
2. Identificar el patrón exacto del diagnóstico del estudio M
3. Ajustar los patrones regex en `extract_diagnostico_coloracion()`
4. Probar con FUNC-06 (reprocesar caso)

### Para Campo Organo:
1. Implementar correcciones propuestas en `medical_extractor.py:2519` y `medical_extractor.py:2569`
2. Probar con caso IHQ251017
3. Validar que no rompe otros casos (auditar casos de prueba)
4. Ejecutar FUNC-06 para reprocesar IHQ251017

---

## Archivos Afectados

- `core/extractors/medical_extractor.py:379-578` (DIAGNOSTICO_COLORACION)
- `core/extractors/medical_extractor.py:2517-2528` (extract_organ_information)
- `core/extractors/medical_extractor.py:2569-2595` (normalize_organ_name)

---

**Fin del reporte**
