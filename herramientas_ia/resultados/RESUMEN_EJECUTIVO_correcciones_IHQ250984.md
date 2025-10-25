# RESUMEN EJECUTIVO - Correcciones IHQ250984

**Fecha:** 2025-10-24 09:53:00
**Estado:** SIMULACIÓN COMPLETADA - Pendiente Aplicación

---

## PROBLEMA CRÍTICO DETECTADO

**Caso IHQ250984:** Extracción de biomarcadores FALLIDA (0/6 biomarcadores correctos)

**Causa raíz:** Los extractores NO reconocen el formato estructurado con guiones utilizado en el PDF:
```
-RECEPTOR DE ESTRÓGENOS: Negativo.
-RECEPTOR DE PROGESTERONA: Negativo.
-HER 2: Positivo (Score 3+) [descripción]
-Ki-67: Tinción nuclear en el 60%
```

---

## ARCHIVOS ANALIZADOS

1. `core/extractors/medical_extractor.py` (36,644 tokens)
   - Función: `extract_factor_pronostico()` (líneas 465-614)

2. `core/extractors/biomarker_extractor.py` (30,494 tokens)
   - Función: `extract_narrative_biomarkers()` (líneas 1203-1440)

---

## CORRECCIONES PROPUESTAS

### 1. extract_factor_pronostico() - CRÍTICA

**Ubicación:** `medical_extractor.py` línea ~500

**Cambio:** Agregar PRIORIDAD 0 para capturar formato estructurado con guiones

**CÓDIGO ANTES:**
```python
# PRIORIDAD 1: FORMATO NARRATIVO
patron_narrativo = r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)'
# Solo captura: "positivas para X, Y, Z"
```

**CÓDIGO DESPUÉS (PROPUESTO):**
```python
# PRIORIDAD 0: FORMATO ESTRUCTURADO CON GUIONES (V6.0.10 - IHQ250984)
# Captura bloque completo:
# -RECEPTOR DE ESTRÓGENOS: Negativo.
# -RECEPTOR DE PROGESTERONA: Negativo.
# -HER 2: Positivo (Score 3+) [descripción]

patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-]+:.*?\n?)+)'
patron_linea_biomarcador = r'-\s*([A-ZÁÉÍÓÚÑ\s0-9/\-]+)\s*:\s*(.+?)(?=\n-|\n\n|$)'

# Extraer línea por línea
# Agregar patrones complementarios para "tinción positiva para GATA3"
# Agregar patrones para "negativas para SOX10"
```

**Impacto:**
- Factor Pronóstico ANTES: `"positivo para: negativo para SXO10"` (erróneo)
- Factor Pronóstico DESPUÉS: `"RECEPTOR DE ESTRÓGENOS: Negativo / RECEPTOR DE PROGESTERONA: Negativo / HER 2: Positivo (Score 3+) [...] / Ki-67: Tinción nuclear en el 60% / Positivo para GATA 3 / Negativo para SXO10"`

---

### 2. extract_narrative_biomarkers() - ALTA PRIORIDAD

**Ubicación:** `biomarker_extractor.py` línea ~1211

**Cambio:** Agregar patrones para formato estructurado SIN paréntesis

**CÓDIGO ANTES:**
```python
complex_patterns = [
    # Solo captura formato CON paréntesis obligatorio:
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    # Falla con: "-RECEPTOR DE ESTRÓGENOS: Negativo." (sin paréntesis)
]
```

**CÓDIGO DESPUÉS (PROPUESTO):**
```python
complex_patterns = [
    # PRIORIDAD MÁXIMA - Formato estructurado SIN paréntesis (V6.0.10 - IHQ250984)
    r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\(([^)]+)\))?(?:\s+(.+?))?\.?',
    r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(.+?)\.?$',

    # Patrones originales CON paréntesis (mantener compatibilidad)
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    # ...

    # NUEVOS patrones para GATA3 y SOX10
    r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3',
    r'(?i)negativas?\s+para\s+S[OX]{2,3}10',  # Captura SOX10 y typo SXO10
]
```

**Impacto:**
- Biomarcadores ANTES: {} (vacío)
- Biomarcadores DESPUÉS: {'ER': 'NEGATIVO', 'PR': 'NEGATIVO', 'HER2': 'POSITIVO (SCORE 3+) [...]', 'KI67': 'Tinción nuclear en el 60%', 'GATA3': 'POSITIVO', 'SOX10': 'NEGATIVO'}

---

### 3. extract_ihq_estudios_solicitados() - MEDIA PRIORIDAD

**Ubicación:** PENDIENTE LOCALIZAR (probablemente `medical_extractor.py`)

**Cambio:** Mejorar patrón para capturar lista completa separada por comas

**CÓDIGO PROPUESTO:**
```python
# Patrón mejorado para listas largas
patron_estudios = r'(?:Se\s+realiz[óo]\s+)?(?:tinción\s+especial|estudios?)\s+(?:de\s+inmunohistoquímica\s+)?para\s+([A-Z0-9\s,/-]+(?:,\s*[A-Z0-9\s/-]+)*)'

# Normalizar nombres:
# - "GATA 3" → "GATA3"
# - "Ki 67" → "Ki-67"
# - "SXO10" → "SOX10" (corregir typo)
```

**Impacto:**
- IHQ_ESTUDIOS_SOLICITADOS ANTES: `"HER2, Receptor de Estrógeno"` (2/6)
- IHQ_ESTUDIOS_SOLICITADOS DESPUÉS: `"GATA3, RECEPTOR DE ESTROGENOS, RECEPTOR DE PROGESTERONA, HER2, Ki-67, SOX10"` (6/6)

---

## PREDICCIÓN DE IMPACTO

| Métrica | ANTES | DESPUÉS | Mejora |
|---------|-------|---------|--------|
| Biomarcadores extraídos | 0/6 (0%) | 6/6 (100%) | +100% |
| Factor Pronóstico | Fragmento erróneo | Bloque completo | ✅ |
| IHQ_ESTUDIOS_SOLICITADOS | 2/6 (33%) | 6/6 (100%) | +67% |
| Score de validación | 33.3% (CRÍTICO) | 100% (OK) | +66.7% |

---

## LÍNEAS MODIFICADAS EXACTAS

### medical_extractor.py
- Línea 500: **INSERTAR** ~60 líneas (PRIORIDAD 0: Formato estructurado)
- Línea 547-550: **MODIFICAR** (agregar factores adicionales)

### biomarker_extractor.py
- Línea 1211: **INSERTAR** 4 líneas (patrones SIN paréntesis)
- Línea 1220: **INSERTAR** 2 líneas (patrones GATA3/SOX10)
- Línea 1320: **INSERTAR** ~20 líneas (lógica de procesamiento)

---

## TESTS DE REGRESIÓN

Después de aplicar, ejecutar:
```bash
# Validar sintaxis
python herramientas_ia/editor_core.py --validar-sintaxis medical_extractor.py
python herramientas_ia/editor_core.py --validar-sintaxis biomarker_extractor.py

# Reprocesar caso objetivo
python herramientas_ia/editor_core.py --reprocesar IHQ250984

# Auditar caso corregido
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente

# Verificar casos previos (NO romper)
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente
```

---

## RIESGOS

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| Romper casos previos | MEDIA | Tests de regresión obligatorios |
| Aumentar complejidad ciclomática | ALTA | Refactorizar si CC > 20 |
| Capturar texto erróneo | BAJA | Validar límites de regex |

---

## DECISIÓN REQUERIDA

¿Proceder con aplicación de correcciones?

**Opciones:**
1. **Aplicar TODAS las correcciones** (recomendado)
2. **Aplicar solo CORRECCIÓN 1** (factor_pronostico) y evaluar
3. **Modificar propuesta** (si hay ajustes necesarios)
4. **Cancelar** (si hay riesgos no contemplados)

---

**Reporte detallado:** `herramientas_ia/resultados/SIMULACION_correcciones_extractores_IHQ250984_20251024_095300.md`
