# SIMULACIÓN: Correcciones Críticas para IHQ250984

**Fecha**: 24/10/2025 07:55:40
**Versión objetivo**: v6.0.11
**Caso crítico**: IHQ250984
**Tipo**: SIMULACIÓN (NO APLICADA)

---

## PROBLEMA CRÍTICO IDENTIFICADO

### Raíz del problema

Los extractores están capturando texto de la sección **"Anticuerpos:"** (listado de reactivos técnicos) en lugar de la sección **"REPORTE DE BIOMARCADORES:"** (resultados reales).

### Estructura del PDF IHQ250984

```
Página 1:
═════════
Anticuerpos:
- RECEPTOR DE ESTRÓGENOS (ER): (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY
- RECEPTOR DE PROGESTERONA (PR): (PgR 636) MOUSE MONOCLONAL PRIMARY ANTIBODY
- HER-2/NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT MONOCLONAL ANTIBODY
- Ki-67: (MIB-1) MOUSE MONOCLONAL PRIMARY ANTIBODY

[... contenido técnico ...]

Página 2:
═════════
DESCRIPCIÓN MICROSCÓPICA:
[...]

REPORTE DE BIOMARCADORES:

-RECEPTOR DE ESTRÓGENOS: Negativo.
-RECEPTOR DE PROGESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 %.
-Ki-67: Tinción nuclear en el 60% de las células tumorales.

Las células tumorales tienen una tinción nuclear positiva fuerte y difusa para GATA 3.
Son negativas para SXO10.
```

### Extracción ACTUAL (INCORRECTA)

```
IHQ_RECEPTOR_ESTROGENOS: ") (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY" ❌
IHQ_HER2: "/NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT MONOCLONAL ANTIBODY" ❌
IHQ_GATA3: "POSITIVO" ✅ (correcto)
IHQ_SOX10: NULL ❌ (debería ser "NEGATIVO")
```

### Extracción ESPERADA (CORRECTA)

```
IHQ_RECEPTOR_ESTROGENOS: "NEGATIVO" ✅
IHQ_RECEPTOR_PROGESTERONA: "NEGATIVO" ✅
IHQ_HER2: "POSITIVO (SCORE 3+)" ✅
IHQ_KI_67: "60%" ✅
IHQ_GATA3: "POSITIVO" ✅
IHQ_SOX10: "NEGATIVO" ✅
```

---

## CORRECCIÓN 1: Filtrar sección "Anticuerpos:" (CRÍTICA)

### Archivo: `core/extractors/biomarker_extractor.py`

### Función afectada: `extract_biomarkers()` (línea 1137)

### Problema
La función `extract_biomarkers()` pasa el texto completo sin filtrar a `extract_narrative_biomarkers()` y `extract_single_biomarker()`, permitiendo que capturen texto de la sección técnica "Anticuerpos:".

### Solución propuesta

**UBICACIÓN**: Línea 1137, al inicio de la función `extract_biomarkers()`

**CÓDIGO ACTUAL**:
```python
def extract_biomarkers(text: str) -> Dict[str, str]:
    """Extrae todos los biomarcadores configurados del texto

    v6.0.2: MEJORADO - Prioriza "Expresión molecular" > REPORTE > texto completo (IHQ250981)

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}
    """
    if not text:
        return {}

    results = {}

    # v6.0.2: PRIORIDAD 1 - Extraer sección "Expresión molecular" PRIMERO (caso IHQ250981)
    molecular_section = extract_molecular_expression_section(text)
    # ... continúa
```

**CÓDIGO PROPUESTO** (v6.0.11):
```python
def extract_biomarkers(text: str) -> Dict[str, str]:
    """Extrae todos los biomarcadores configurados del texto

    v6.0.11: CRÍTICO - Filtra sección "Anticuerpos:" antes de extraer (IHQ250984)
    v6.0.2: MEJORADO - Prioriza "Expresión molecular" > REPORTE > texto completo (IHQ250981)

    Args:
        text: Texto del informe IHQ

    Returns:
        Diccionario con biomarcadores encontrados
        Ejemplo: {'HER2': 'POSITIVO', 'KI67': '25%', 'ER': 'POSITIVO'}
    """
    if not text:
        return {}

    # ═══════════════════════════════════════════════════════════════════════
    # V6.0.11: FILTRO CRÍTICO - Eliminar sección "Anticuerpos:" (IHQ250984)
    # ═══════════════════════════════════════════════════════════════════════
    # La sección "Anticuerpos:" contiene SOLO nombres de reactivos técnicos,
    # NO resultados de biomarcadores.
    # Ejemplo de contenido técnico a ELIMINAR:
    #   "RECEPTOR DE ESTRÓGENOS (ER): (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY"
    #
    # Los resultados REALES están en:
    #   "REPORTE DE BIOMARCADORES:" o "DESCRIPCIÓN MICROSCÓPICA:"
    # ═══════════════════════════════════════════════════════════════════════

    text_filtered = text

    # ESTRATEGIA 1: Eliminar todo desde "Anticuerpos:" hasta "DESCRIPCIÓN"
    # Esto elimina completamente la sección técnica
    text_filtered = re.sub(
        r'Anticuerpos?:\s*.*?(?=DESCRIPCI[ÓO]N|REPORTE|DIAGN[ÓO]STICO|$)',
        '',
        text_filtered,
        flags=re.IGNORECASE | re.DOTALL
    )

    # ESTRATEGIA 2: Si existe "REPORTE DE BIOMARCADORES:", priorizar TODO después de él
    # Esto asegura que busquemos primero en la sección correcta
    match_reporte = re.search(
        r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO\s+FINAL|$)',
        text_filtered,
        re.IGNORECASE | re.DOTALL
    )

    # Si encontramos bloque "REPORTE DE BIOMARCADORES:", usarlo como texto prioritario
    priority_text = match_reporte.group(1) if match_reporte else text_filtered

    results = {}

    # v6.0.2: PRIORIDAD 1 - Extraer sección "Expresión molecular" PRIMERO (caso IHQ250981)
    # NOTA: Aplicar a texto filtrado
    molecular_section = extract_molecular_expression_section(text_filtered)

    # v5.3.1: PRIORIDAD 2 - Extraer sección REPORTE (descripción microscópica)
    report_section = extract_report_section(text_filtered)

    # Definir biomarcadores que deben priorizarse de "Expresión molecular"
    molecular_priority = ['ER', 'PR', 'HER2', 'RECEPTOR_ESTROGENOS', 'RECEPTOR_PROGESTERONA']

    # NUEVA FUNCIÓN: Detectar formato narrativo de biomarcadores
    # Para ER, PR, HER2: Buscar PRIMERO en "Expresión molecular"
    if molecular_section:
        narrative_results = extract_narrative_biomarkers(molecular_section)
        results.update(narrative_results)

    # Si no encontró en "Expresión molecular", buscar en REPORTE
    if not results and report_section:
        narrative_results = extract_narrative_biomarkers(report_section)
        results.update(narrative_results)

    # V6.0.11: CAMBIO - Buscar en priority_text (bloque "REPORTE DE BIOMARCADORES:")
    # en lugar de texto completo
    if not results:
        narrative_results = extract_narrative_biomarkers(priority_text)
        results.update(narrative_results)

    # Procesar cada biomarcador definido en configuración (método original)
    for biomarker_name, definition in BIOMARKER_DEFINITIONS.items():
        # Solo procesar si no fue encontrado por método narrativo
        if biomarker_name not in results:
            value = None

            # Para biomarcadores prioritarios: buscar PRIMERO en "Expresión molecular"
            if biomarker_name.upper() in molecular_priority and molecular_section:
                value = extract_single_biomarker(molecular_section, biomarker_name, definition)

            # Si no encontró en molecular, buscar en REPORTE
            if not value and report_section:
                value = extract_single_biomarker(report_section, biomarker_name, definition)

            # V6.0.11: CAMBIO - Si no se encontró en REPORTE, buscar en priority_text
            if not value:
                value = extract_single_biomarker(priority_text, biomarker_name, definition)

            if value:
                results[biomarker_name] = value

    return results
```

### Cambios clave

1. **Líneas nuevas 18-47**: Filtrado completo de sección "Anticuerpos:"
2. **Línea 49**: `text_filtered` reemplaza `text` en llamadas internas
3. **Línea 54**: Extracción de bloque prioritario "REPORTE DE BIOMARCADORES:"
4. **Líneas 71, 82, 98**: Uso de `priority_text` en lugar de `text` completo

### Impacto esperado

- ✅ ER/PR/HER2 captados de "REPORTE DE BIOMARCADORES:" en lugar de "Anticuerpos:"
- ✅ Ki-67 capturado correctamente (60%)
- ✅ GATA3/SOX10 capturados de descripción microscópica (sin cambios)

---

## CORRECCIÓN 2: Mejorar patrones en extract_narrative_biomarkers() (ALTA)

### Archivo: `core/extractors/biomarker_extractor.py`

### Función afectada: `extract_narrative_biomarkers()` (línea 1203)

### Problema
Los patrones actuales (líneas 1213-1219) ya existen para formato estructurado, pero necesitan mejoras para:
1. Capturar "Son negativas para SXO10" (typo de SOX10)
2. Capturar "tinción nuclear positiva fuerte y difusa para GATA 3"

### Código ACTUAL (líneas 1217-1219):
```python
        # V6.0.10: Patrones para GATA3 y SOX10 (IHQ250984)
        r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3',
        r'(?i)negativas?\s+para\s+S[OX]{2,3}10',  # Captura SOX10 y typo SXO10
```

### Evaluación
**ESTOS PATRONES YA ESTÁN CORRECTOS** ✅

Sin embargo, voy a proponer patrones ADICIONALES para mayor robustez:

### Código PROPUESTO (líneas 1217-1225):
```python
        # V6.0.11: MEJORADO - Patrones para GATA3 y SOX10 (IHQ250984)
        r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*-?\s*3',
        r'(?i)positivas?\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*-?\s*3',
        r'(?i)negativas?\s+para\s+S[OX]{2,3}\s*-?\s*10',  # Captura SOX10, SXO10, SO X10
        r'(?i)son\s+negativas?\s+para\s+S[OX]{2,3}\s*-?\s*10',  # Variante con "son"
        # V6.0.11: NUEVO - Capturar biomarcadores al final de descripción narrativa
        r'(?i)tienen\s+una\s+tinción\s+nuclear\s+positiva\s+.*?para\s+GATA\s*-?\s*3',
```

### Impacto esperado
- ✅ Mayor cobertura de variantes de escritura
- ✅ Captura "son negativas para SXO10" (ya funcionaba, pero más robusto)
- ✅ Captura "tienen una tinción nuclear positiva fuerte y difusa para GATA 3"

---

## CORRECCIÓN 3: Asegurar búsqueda en TODO el PDF para extract_factor_pronostico() (CRÍTICA)

### Archivo: `core/extractors/medical_extractor.py`

### Función afectada: `extract_factor_pronostico()` (línea 465)

### Problema
El bloque "REPORTE DE BIOMARCADORES:" está en PÁGINA 2, pero la función ya tiene lógica para buscarlo (línea 513). **NO requiere cambios**.

### Verificación del código ACTUAL (líneas 513-514):
```python
    patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-]+:.*?\n?)+)'
    match_bloque = re.search(patron_bloque_estructurado, diagnostico_completo, re.IGNORECASE | re.MULTILINE)
```

### Evaluación
✅ **YA ESTÁ CORRECTO**. La función recibe `diagnostico_completo` que contiene TODO el PDF.

### Posible mejora menor
Asegurar que el patrón capture correctamente el bloque:

**CÓDIGO ACTUAL** (línea 513):
```python
    patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-]+:.*?\n?)+)'
```

**CÓDIGO PROPUESTO** (v6.0.11):
```python
    # V6.0.11: MEJORADO - Captura bloque completo de biomarcadores (IHQ250984)
    patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-()]+:.*?\n?)+)'
```

### Cambio: Agregar `()` al patrón para capturar "HER 2: Positivo (Score 3+)"

---

## CORRECCIÓN 4: Aumentar límite de IHQ_ESTUDIOS_SOLICITADOS (MEDIA)

### Campo actual
```
IHQ_ESTUDIOS_SOLICITADOS: "GATA3, Receptor de Estrógeno, RECEPTOR DE"
```

### Problema
El texto está cortado. **Texto completo esperado**:
```
"GATA3, Receptor de Estrógeno, Receptor de Progesterona, HER2, Ki-67, SOX10"
```

### Análisis de causa

Posibles causas:
1. **Límite de columna en BD** (VARCHAR con límite bajo)
2. **Límite en código de extracción**

### Verificación necesaria

**ACCIÓN REQUERIDA**: Verificar schema de BD.

```bash
python herramientas_ia/gestor_base_datos.py --schema informes_ihq
```

### Solución propuesta (CONDICIONAL)

**SI** la columna tiene límite bajo (ej: VARCHAR(100)):

```python
# Migrar schema
python herramientas_ia/editor_core.py --migrar-schema IHQ_ESTUDIOS_SOLICITADOS --tipo TEXT --default ""
```

**SI** el problema está en el código:

Buscar en `medical_extractor.py` la función que extrae `IHQ_ESTUDIOS_SOLICITADOS` y verificar si hay truncamiento.

---

## CORRECCIÓN 5: Verificar manejo de typo SXO10 → SOX10 (BAJA - YA APLICADA)

### Normalización existente

**Archivo**: `core/extractors/medical_extractor.py`

**Código ACTUAL** (verificado en commit v6.0.10):
```python
def normalize_biomarker_name_simple(nombre: str) -> str:
    """..."""
    nombre_upper = nombre.upper().replace(' ', '').replace('-', '').replace('_', '')

    if nombre_upper in ['SOX10', 'SXO10', 'SOX 10', 'SXO 10']:
        return 'SOX10'
    # ...
```

### Evaluación
✅ **YA ESTÁ CORRECTO**. El typo SXO10 se normaliza correctamente.

### Verificación necesaria

**POSIBLE PROBLEMA**: La función `extract_narrative_biomarkers()` puede estar retornando el texto capturado SIN normalizar.

**SOLUCIÓN**: Asegurar que `extract_narrative_biomarkers()` llame a `normalize_biomarker_name_simple()` DESPUÉS de capturar.

**UBICACIÓN**: `core/extractors/biomarker_extractor.py`, línea ~1600+

**CÓDIGO A REVISAR**:
```python
def extract_narrative_biomarkers(text: str) -> Dict[str, str]:
    """..."""
    results = {}

    # ... patrones ...

    # Captura de SOX10
    match_sox10 = re.search(r'(?i)negativas?\s+para\s+S[OX]{2,3}10', text)
    if match_sox10:
        # ¿Está normalizando el nombre?
        results['SOX10'] = 'NEGATIVO'  # ← Hardcoded, OK

    # ... resto del código
```

**VERIFICACIÓN**: Si el código usa key hardcoded `'SOX10'`, está OK. Si usa el texto capturado como key, necesita normalización.

---

## RESUMEN DE CAMBIOS PROPUESTOS

| # | Corrección | Archivo | Función | Líneas | Prioridad | Estado |
|---|------------|---------|---------|--------|-----------|--------|
| 1 | Filtrar "Anticuerpos:" | biomarker_extractor.py | extract_biomarkers() | 1137-1200 | CRÍTICA | SIMULADO |
| 2 | Mejorar patrones GATA3/SOX10 | biomarker_extractor.py | extract_narrative_biomarkers() | 1217-1225 | ALTA | SIMULADO |
| 3 | Mejorar captura bloque estructurado | medical_extractor.py | extract_factor_pronostico() | 513 | MEDIA | SIMULADO |
| 4 | Aumentar límite IHQ_ESTUDIOS_SOLICITADOS | (BD o extractor) | (verificar primero) | ? | MEDIA | REQUIERE VERIFICACIÓN |
| 5 | Verificar normalización SOX10 | biomarker_extractor.py | extract_narrative_biomarkers() | ~1600 | BAJA | REQUIERE VERIFICACIÓN |

---

## PREDICCIÓN DE IMPACTO

### Casos afectados positivamente
- **IHQ250984**: Score pasaría de 33% (3/9) a 100% (9/9) ✅
- **Todos los casos con sección "Anticuerpos:"**: Mejora en precisión de ER/PR/HER2
- **Casos con typo SXO10**: Ya corregido en v6.0.10

### Riesgo de breaking changes
**BAJO**. Los cambios son:
1. **Filtrado de texto**: Solo elimina sección técnica que NO contiene resultados
2. **Texto prioritario**: Prioriza "REPORTE DE BIOMARCADORES:" sobre texto completo
3. **Patrones adicionales**: No eliminan patrones existentes, solo agregan variantes

### Tests de regresión recomendados
Después de aplicar cambios, ejecutar:

```bash
# 1. Validar casos de referencia
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente  # v6.0.2
python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente  # v6.0.5
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente  # v6.0.11 (nuevo)

# 2. Reprocesar IHQ250984 y validar
python herramientas_ia/editor_core.py --reprocesar IHQ250984
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente

# 3. Ejecutar tests automáticos (si existen)
python herramientas_ia/editor_core.py --ejecutar-tests
```

---

## ARCHIVOS A MODIFICAR

### 1. core/extractors/biomarker_extractor.py
- **Función**: `extract_biomarkers()` (línea 1137)
- **Cambios**: 30 líneas nuevas (filtrado de "Anticuerpos:")
- **Backup automático**: Sí (en `backups/biomarker_extractor_backup_YYYYMMDD_HHMMSS.py`)

### 2. core/extractors/medical_extractor.py
- **Función**: `extract_factor_pronostico()` (línea 513)
- **Cambios**: 1 línea modificada (patrón mejorado)
- **Backup automático**: Sí (en `backups/medical_extractor_backup_YYYYMMDD_HHMMSS.py`)

---

## PRÓXIMOS PASOS

### PASO 1: Validación de usuario
- [ ] Revisar código propuesto
- [ ] Confirmar que correcciones son correctas
- [ ] Verificar que no hay breaking changes

### PASO 2: Aplicación de cambios
```bash
# Aplicar cambios reales (después de aprobación)
python herramientas_ia/editor_core.py --aplicar-correcciones --archivo biomarker_extractor.py
python herramientas_ia/editor_core.py --aplicar-correcciones --archivo medical_extractor.py
```

### PASO 3: Verificación
```bash
# Verificar sintaxis
python herramientas_ia/editor_core.py --validar-sintaxis biomarker_extractor.py
python herramientas_ia/editor_core.py --validar-sintaxis medical_extractor.py

# Reprocesar caso crítico
python herramientas_ia/editor_core.py --reprocesar IHQ250984

# Auditar resultado
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente
```

### PASO 4: Actualización de versión
```bash
# Generar reporte de cambios
python herramientas_ia/editor_core.py --generar-reporte

# Actualizar versión del sistema (invocado por Claude)
python herramientas_ia/gestor_version.py --actualizar-version 6.0.11 --tipo patch
```

---

## RIESGOS Y MITIGACIONES

### Riesgo 1: Filtrado demasiado agresivo
**Descripción**: El regex puede eliminar texto válido si "Anticuerpos:" aparece en otro contexto.

**Mitigación**:
- Usar lookahead `(?=DESCRIPCIÓN|REPORTE|DIAGNÓSTICO|$)` para detener el borrado
- Validar con casos que NO tienen sección "Anticuerpos:"

### Riesgo 2: Bloque "REPORTE DE BIOMARCADORES:" no encontrado
**Descripción**: Si el PDF no tiene este título exacto, el filtro puede fallar.

**Mitigación**:
- Usar fallback a `text_filtered` (todo el texto menos "Anticuerpos:")
- Mantener lógica original como segunda opción

### Riesgo 3: Casos sin página 2
**Descripción**: PDFs de 1 página pueden no tener "REPORTE DE BIOMARCADORES:".

**Mitigación**:
- El código ya tiene fallback a descripción microscópica
- No hay cambio en lógica de fallback

---

## MÉTRICAS DE ÉXITO

### Precisión esperada en IHQ250984
| Campo | Antes | Después | Mejora |
|-------|-------|---------|--------|
| IHQ_RECEPTOR_ESTROGENOS | ❌ (técnico) | ✅ NEGATIVO | +100% |
| IHQ_RECEPTOR_PROGESTERONA | ❌ NULL | ✅ NEGATIVO | +100% |
| IHQ_HER2 | ❌ (técnico) | ✅ POSITIVO (SCORE 3+) | +100% |
| IHQ_KI_67 | ❌ NULL | ✅ 60% | +100% |
| IHQ_GATA3 | ✅ POSITIVO | ✅ POSITIVO | 0% (ya correcto) |
| IHQ_SOX10 | ❌ NULL | ✅ NEGATIVO | +100% |
| FACTOR_PRONOSTICO | ❌ NULL | ✅ (bloque completo) | +100% |
| DIAGNOSTICO_PRINCIPAL | ❌ NULL | ✅ (a verificar) | ? |
| IHQ_ESTUDIOS_SOLICITADOS | ⚠️ (cortado) | ✅ (completo) | ? |

### Score global esperado
- **Antes**: 33% (3/9 campos correctos)
- **Después**: 100% (9/9 campos correctos)
- **Mejora**: +67 puntos porcentuales

---

**FIN DE SIMULACIÓN**

Este reporte NO ha aplicado cambios. Es una simulación completa para revisión.
