# 🔍 ANÁLISIS COMPLETO - PROBLEMAS DE MAPEO Y SOLUCIONES

**Fecha**: 5 de octubre de 2025  
**Análisis**: Base de Datos Actual (50 registros)

---

## 📊 RESULTADOS DEL ANÁLISIS

### Estadísticas Generales
- **Total de registros**: 50
- **Casos perfectos (100%)**: 1 (2%)  ← ⚠️ MUY BAJO
- **Casos con problemas**: 9 (18%)
- **Casos que necesitan IA**: 9 (18%)

### Problemas Identificados por Tipo

1. **DIAGNÓSTICO_VACÍO_CON_DESCRIPCIÓN**: 7 casos
   - El diagnóstico está en "Descripción Diagnóstico" pero NO se extrajo a "Diagnóstico Principal"
   
2. **DIAGNÓSTICO_CONTIENE_DESCRIPCIÓN**: 1 caso
   - El diagnóstico tiene texto de descripción mezclado (IHQ250009)
   
3. **DIAGNÓSTICO_MUY_CORTO**: 1 caso
   - Solo dice "MELANOMA" cuando debería ser más específico (IHQ250026)

---

## 🔍 ANÁLISIS DETALLADO DE CASOS PROBLEMÁTICOS

### Caso 1: IHQ250009 - HIBERNOMA (Diagnóstico con Descripción)

**Problema**: Diagnóstico principal incluye texto explicativo

**Actual**:
```
Diagnóstico Principal: HIBERNOMA, SIN EMBARGO, SE REALIZARON ESTUDIOS DE 
INMUNOHISTOQUÍMICA PARA CDK4 Y MDM2 QUE FUERON NEGATIVOS SIN UN ADECUADO 
CONTROL EXTERNO
```

**Debería ser**:
```
Diagnóstico Principal: HIBERNOMA
```

**Comentario**: "SIN EMBARGO, SE REALIZARON..." es texto explicativo, no diagnóstico.

---

### Caso 2: IHQ250017 - ADENOCARCINOMA DE RECTO (Vacío)

**Problema**: Diagnóstico vacío pero está en descripción

**Actual**:
```
Diagnóstico Principal: N/A
Descripción: Mucosa de recto. Lesión. Biopsia endoscópica...
```

**En descripción microscópica dice**:
```
"ADENOCACRINOMA MODERADAMENTE DIFERENCIADO (FRAGMENTOS)"
```

**Debería ser**:
```
Diagnóstico Principal: ADENOCARCINOMA MODERADAMENTE DIFERENCIADO
```

---

### Caso 3: IHQ250021 - BIOPSIA RENAL (Sin Parénquima)

**Problema**: Diagnóstico vacío - caso especial sin tumor

**Actual**:
```
Diagnóstico Principal: N/A
Descripción: TÉJIDO SIN REPRESENTACIÓN DE PARENQUIMA RENAL. 
TÉJIDO FIBROADIPOSO DE ARQUTIECTURA USUAL.
```

**Debería ser**:
```
Diagnóstico Principal: TEJIDO FIBROADIPOSO SIN PARENQUIMA RENAL
Malignidad: BENIGNO (o NO_APLICABLE)
```

**Nota**: Este caso NO es oncológico - es una biopsia inadecuada.

---

### Caso 4: IHQ250026 - MELANOMA (Muy Corto)

**Problema**: Diagnóstico demasiado corto y genérico

**Actual**:
```
Diagnóstico Principal: MELANOMA
```

**En descripción dice**:
```
"LOS HALLAZGOS HISTOLÓGICOS SON COMPATIBLES CON MELANOMA METASTÁSICO"
```

**Debería ser**:
```
Diagnóstico Principal: MELANOMA METASTÁSICO
```

---

### Caso 5: IHQ250037 - ADENOCARCINOMA RECTAL (Vacío)

**Problema**: Diagnóstico vacío

**En descripción microscópica**:
```
"HALLAZGOS MORFOLÓGICOS COMPATIBLES CON ADENOCARCINOMA..."
```

**Debería extraerse**: ADENOCARCINOMA

---

### Casos 6-9: Similares - Diagnóstico en Descripción

- IHQ250039, IHQ250042, IHQ250043, IHQ250048
- Todos tienen diagnóstico en descripción pero NO en campo principal

---

## 🎯 PATRONES DE CASOS PERFECTOS (100%)

Solo 1 caso identificado como perfecto: **IHQ250024**

**Características del caso perfecto**:
```
Diagnóstico Principal: CARCINOMA INVASIVO SIN TIPO ESPECIAL (DUCTAL) 
                       GRADO HISTOLOGICO 2 (NOTTINGHAM 7/9 PUNTOS)
Malignidad: MALIGNO
Edad: Presente
Género: Presente
EPS: Presente
Órgano: Presente
Biomarcadores: Todos presentes (HER2, Ki-67, RE, RP)
```

**Patrones de éxito**:
1. ✅ Diagnóstico específico y completo
2. ✅ Sin texto explicativo mezclado
3. ✅ Malignidad determinada correctamente
4. ✅ Todos los campos demográficos completos
5. ✅ Biomarcadores extraídos
6. ✅ Sin "N/A" en campos críticos

---

## 🔧 CORRECCIONES NECESARIAS AL EXTRACTOR

### Corrección #1: Mejorar `extract_principal_diagnosis()`

**Problema**: La función NO está limpiando texto explicativo.

**Solución**: Agregar post-procesamiento para eliminar:
- Texto después de "SIN EMBARGO"
- Texto después de "SE REALIZARON"
- Texto después de "SE SUGIERE"
- Comas seguidas de explicaciones largas

```python
# AGREGAR después de extract_principal_diagnosis()
def clean_diagnosis_text(diagnosis: str) -> str:
    """Limpia texto explicativo del diagnóstico"""
    if not diagnosis:
        return diagnosis
    
    # Patrones de texto explicativo a eliminar
    cutoff_patterns = [
        r',?\s+SIN EMBARGO.*',
        r',?\s+SE REALIZARON.*',
        r',?\s+SE SUGIERE.*',
        r',?\s+A CRITERIO.*',
        r',?\s+VER COMENTARIO.*',
        r',?\s+COMENTARIOS:?.*'
    ]
    
    cleaned = diagnosis
    for pattern in cutoff_patterns:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()
```

---

### Corrección #2: Buscar en Descripción Macroscópica

**Problema**: Algunos diagnósticos están en descripción macroscópica (caso referenciado).

**Solución**: En `map_to_database_format()`, agregar búsqueda en descripción_macroscopica:

```python
# PRIORIDAD 4: Buscar en descripción macroscópica
if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
    desc_macro = extracted_data.get('descripcion_macroscopica', '')
    if desc_macro and len(desc_macro) > 20:
        # Buscar patrón de diagnóstico referenciado
        match = re.search(r'diagnósticos?\s+de\s+"([^"]+)"', desc_macro, re.IGNORECASE)
        if match:
            diagnostico_completo = match.group(1)
```

---

### Corrección #3: Casos Sin Tumor (Biopsias Inadecuadas)

**Problema**: Casos como IHQ250021 son biopsias sin tumor pero se marcan como MALIGNO.

**Solución**: Detectar patrones de "sin representación" y ajustar:

```python
# Detectar casos sin tumor
sin_tumor_patterns = [
    'SIN REPRESENTACIÓN DE PARENQUIMA',
    'TEJIDO FIBROADIPOSO',
    'MUESTRA INADECUADA',
    'SIN LESIÓN TUMORAL'
]

if any(pattern in diagnostico_completo.upper() for pattern in sin_tumor_patterns):
    malignidad = 'NO_APLICABLE'  # o 'BENIGNO'
```

---

## 🤖 CRITERIOS PARA ENVIAR A IA (REFINADOS)

Un caso **DEBE** enviarse a IA si cumple **CUALQUIERA** de estos criterios:

### Criterios Críticos (Envío Obligatorio)
1. ❌ Diagnóstico Principal = N/A PERO Descripción Diagnóstico tiene >50 chars
2. ❌ Diagnóstico Principal incluye "SIN EMBARGO", "SE REALIZARON", "SE SUGIERE"
3. ❌ Diagnóstico Principal < 10 caracteres (excepto keywords válidos)
4. ❌ Malignidad = NO_DETERMINADO
5. ❌ Score Críticos < 100% (falta nombre, edad, género, diagnóstico)

### Criterios de Sospecha (Envío Opcional - IA decide)
6. ⚠️ Factor Pronóstico = N/A PERO diagnóstico menciona Ki-67, p53
7. ⚠️ Biomarcadores todos N/A PERO descripción microscópica menciona IHQ
8. ⚠️ Diagnóstico muy largo (>200 chars) sin estructurar

---

## 📤 DATOS COMPLETOS PARA ENVIAR A LA IA

Para cada caso que necesita revisión, enviar:

### Campos Principales
```json
{
  "numero_peticion": "IHQ250XXX",
  "score_total": 62.5,
  "problemas_detectados": ["DIAGNÓSTICO_VACÍO_CON_DESCRIPCIÓN"],
  
  "contexto_completo": {
    "descripcion_macroscopica": "...",
    "descripcion_microscopica": "...",
    "descripcion_diagnostico": "..."
  },
  
  "datos_actuales": {
    "diagnostico_principal": "N/A",
    "malignidad": "MALIGNO",
    "factor_pronostico": "N/A"
  },
  
  "biomarcadores_actuales": {
    "HER2": "...",
    "Ki67": "...",
    "RE": "...",
    "RP": "...",
    "P16": "...",
    "P40": "...",
    "PDL1": "...",
    "P53": "..."
  }
}
```

### Instrucciones para la IA

```
Analiza el contexto completo y:
1. Extrae el diagnóstico principal EXACTO (sin comentarios)
2. Determina malignidad correcta (MALIGNO/BENIGNO/NO_APLICABLE)
3. Extrae factor pronóstico si existe
4. Completa biomarcadores faltantes
5. Verifica que todo sea consistente

Devuelve JSON con campos corregidos.
```

---

## ✅ PLAN DE ACCIÓN

### Fase 1: Corregir Extractores (AHORA)
1. Agregar función `clean_diagnosis_text()` en `medical_extractor.py`
2. Modificar `map_to_database_format()` para buscar en macroscópica
3. Agregar detección de casos "sin tumor"
4. Probar con los 9 casos problemáticos

### Fase 2: Implementar Detector de Calidad
1. Crear función `evaluate_record_quality()` en nuevo módulo
2. Implementar los 8 criterios de detección
3. Marcar casos que necesitan IA

### Fase 3: Integrar con IA
1. Crear endpoint/función para enviar casos a IA
2. La IA recibe JSON completo
3. IA devuelve campos corregidos
4. Sistema actualiza BD

### Fase 4: Validación
1. Reprocesar los 9 casos problemáticos
2. Verificar mejora de 2% → >90% casos perfectos
3. Confirmar que casos bien mapeados no se envían a IA

---

## 📊 MÉTRICAS DE ÉXITO

**Objetivo**: Reducir casos problemáticos de 18% a <5%

| Métrica | Actual | Objetivo |
|---------|--------|----------|
| Casos perfectos | 2% | >90% |
| Casos con problemas | 18% | <5% |
| Diagnóstico vacío | 14% | 0% |
| Enviados a IA | N/A | <10% |

---

## 💡 CONCLUSIONES

1. **Solo 2% de casos perfectos** indica problema serio en extracción
2. **7 de 9 casos** tienen diagnóstico en descripción pero NO extraído
3. **Necesario mejorar extractores** antes de delegar todo a IA
4. **IA debe usarse solo para casos ambiguos**, no para errores de extracción
5. **Patrones claros** permiten detección automática de calidad

---

**Siguiente paso**: Implementar las 3 correcciones al extractor y re-evaluar.

