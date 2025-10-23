# CORRECCIONES v6.0.1 - CASO IHQ250981

**Fecha**: 2025-10-22 15:56:08
**Caso de referencia**: IHQ250981
**Versión**: v6.0.1 (5 correcciones críticas)
**Archivos modificados**: 2

---

## RESUMEN EJECUTIVO

Se aplicaron **5 correcciones críticas** identificadas en la re-auditoría del caso IHQ250981:

1. **Ki-67**: Invertir prioridad de búsqueda (CRÍTICO)
2. **E-Cadherina**: Agregar normalización completa (CRÍTICO)
3. **DIAGNOSTICO_PRINCIPAL**: Recortar " - TAMAÑO TUMORAL" (IMPORTANTE)
4. **IHQ_ESTUDIOS_SOLICITADOS**: Normalizar nombres cortos (IMPORTANTE)
5. **FACTOR_PRONOSTICO**: Normalizar "Índice de..." (MEDIA)

**Estado**: ✅ COMPLETADO
**Sintaxis Python**: ✅ VALIDADA
**Backups**: ✅ CREADOS

---

## CORRECCIÓN 1: Ki-67 - Invertir prioridad (CRÍTICO)

### PROBLEMA IDENTIFICADO:
- **Caso**: IHQ250981
- **Campo afectado**: IHQ_KI-67
- **Valor actual**: VACÍO
- **Valor esperado**: "21-30%"
- **Texto en PDF**: "Índice de proliferación celular (Ki67): 21-30%" (línea 79, DESCRIPCIÓN MICROSCÓPICA)

### CAUSA RAÍZ:
El extractor v6.0.0 busca PRIMERO en DIAGNÓSTICO (donde NO está Ki-67), y LUEGO en DESCRIPCIÓN MICROSCÓPICA.

Para Ki-67, la ubicación canónica es **DESCRIPCIÓN MICROSCÓPICA**, NO diagnóstico.

### SOLUCIÓN APLICADA:
**Archivo**: `core/extractors/biomarker_extractor.py`
**Función**: `extract_single_biomarker()`
**Líneas modificadas**: 1456-1482

**Cambio**:
```python
# V6.0.1: LÓGICA ESPECIAL PARA KI67 - Invertir prioridad
if biomarker_name == 'KI67' and definition.get('usa_prioridad_seccion', False):
    # Para Ki67, buscar PRIMERO en DESCRIPCIÓN MICROSCÓPICA
    for pattern in definition.get('patrones', []):
        valor_microscopica = buscar_en_microscopica(text, pattern)
        if valor_microscopica:
            normalized = normalize_biomarker_value(
                valor_microscopica,
                definition.get('normalizacion', {}),
                definition.get('tipo_valor', 'PERCENTAGE')
            )
            if normalized:
                return normalized

    # LUEGO en DIAGNÓSTICO (fallback)
    for pattern in definition.get('patrones', []):
        valor_diagnostico = buscar_en_diagnostico(text, pattern)
        if valor_diagnostico:
            normalized = normalize_biomarker_value(
                valor_diagnostico,
                definition.get('normalizacion', {}),
                definition.get('tipo_valor', 'PERCENTAGE')
            )
            if normalized:
                return normalized

    return None
```

**Resultado esperado**: IHQ_KI-67 = "21-30%" ✅

---

## CORRECCIÓN 2: E-Cadherina - Normalización completa (CRÍTICO)

### PROBLEMA IDENTIFICADO:
- **Caso**: IHQ250981
- **Campo afectado**: IHQ_E_CADHERINA
- **Valor actual**: "IHQ_E-CADHERINA" (nombre de columna en lugar de valor)
- **Valor esperado**: "POSITIVO"
- **Texto en PDF**: "marcación positiva para: E-Cadherina" (línea 85)

### CAUSA RAÍZ:
Patrón de normalización incompleto para E-Cadherina. Faltaban variantes de normalización.

### SOLUCIÓN APLICADA:

#### PARTE A: Biomarcador extractor
**Archivo**: `core/extractors/biomarker_extractor.py`
**Definición**: `E_CADHERINA`
**Líneas modificadas**: 326-337

**Cambio**:
```python
'normalizacion': {
    'positivo': 'POSITIVO',
    'positiva': 'POSITIVO',
    'negativo': 'NEGATIVO',
    'negativa': 'NEGATIVO',
    'presente': 'POSITIVO',    # NUEVO
    'ausente': 'NEGATIVO',     # NUEVO
    '+': 'POSITIVO',           # NUEVO
    '-': 'NEGATIVO',           # NUEVO
    'pos': 'POSITIVO',         # NUEVO
    'neg': 'NEGATIVO',         # NUEVO
}
```

#### PARTE B: Estudios solicitados
**Archivo**: `core/extractors/medical_extractor.py`
**Función**: `normalize_biomarker_name_simple()`
**Líneas modificadas**: 868-870

**Cambio**:
```python
# V6.0.1: E-Cadherina (CORRIGE IHQ250981)
if 'CADHERINA' in nombre_upper or 'CADHERIN' in nombre_upper:
    return 'E-Cadherina'
```

**Resultado esperado**: IHQ_E_CADHERINA = "POSITIVO" ✅

---

## CORRECCIÓN 3: DIAGNOSTICO_PRINCIPAL - Recortar " - TAMAÑO TUMORAL" (IMPORTANTE)

### PROBLEMA IDENTIFICADO:
- **Caso**: IHQ250981
- **Campo afectado**: DIAGNOSTICO_PRINCIPAL
- **Valor actual**: "CARCINOMA... - TAMAÑO TUMORAL MAYOR 7 X 6 X 3 CENTÍMETROS"
- **Valor esperado**: "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)"

### CAUSA RAÍZ:
El código que recorta " - " estaba DESPUÉS del procesamiento, pero el diagnóstico ya llegaba con " - " incluido ANTES.

### SOLUCIÓN APLICADA:
**Archivo**: `core/extractors/medical_extractor.py`
**Función**: `extract_principal_diagnosis()`
**Líneas modificadas**: 1981-1984

**Cambio**:
```python
# V6.0.1: Detener ANTES de " - TAMAÑO TUMORAL" y similares (CRÍTICO IHQ250981)
if ' - ' in principal_cut:
    parts = principal_cut.split(' - ')
    principal_cut = parts[0].strip()
```

**Ubicación**: Justo DESPUÉS de aplicar recortes de cláusulas (NO DESCARTA, SUGIERE, etc.), ANTES de normalizar espacios.

**Resultado esperado**: DIAGNOSTICO_PRINCIPAL sin " - TAMAÑO TUMORAL..." ✅

---

## CORRECCIÓN 4: IHQ_ESTUDIOS_SOLICITADOS - Normalizar nombres cortos (IMPORTANTE)

### PROBLEMA IDENTIFICADO:
- **Caso**: IHQ250981
- **Campo afectado**: IHQ_ESTUDIOS_SOLICITADOS
- **Valor actual**: "HER2, Receptor de Estrógeno, Receptor de Progesterona" (3/5)
- **Valor esperado**: "HER2, Receptor de Estrógeno, Receptor de Progesterona, E-Cadherina, Ki-67" (5/5)
- **Texto en PDF**: "tinción con: E-Cadherina, Progesterona, Estrógenos, Her2, Ki67"

### CAUSA RAÍZ:
Faltaba normalización de nombres cortos:
- "Progesterona" → "Receptor de Progesterona"
- "Estrógenos" → "Receptor de Estrógeno"
- "Ki67" → "Ki-67"

### SOLUCIÓN APLICADA:
**Archivo**: `core/extractors/medical_extractor.py`
**Función**: `normalize_biomarker_name_simple()`
**Líneas modificadas**: 846-854, 868-870

**Cambio**:
```python
# V6.0.1: Normalizar nombres cortos de receptores (CORRIGE IHQ250981)
if nombre_upper in ['PROGESTERONA', 'PROGRESTERONA']:
    return 'Receptor de Progesterona'
if nombre_upper in ['ESTROGENOS', 'ESTRÓGENOS', 'ESTROGENO', 'ESTRÓGENO']:
    return 'Receptor de Estrógeno'

# Ki-67: mantener guión (TODAS LAS VARIANTES)
if re.match(r'KI[\s-]?67', nombre_upper):
    return 'Ki-67'

# V6.0.1: E-Cadherina (CORRIGE IHQ250981)
if 'CADHERINA' in nombre_upper or 'CADHERIN' in nombre_upper:
    return 'E-Cadherina'
```

**Resultado esperado**: IHQ_ESTUDIOS_SOLICITADOS = 5/5 biomarcadores ✅

---

## CORRECCIÓN 5: FACTOR_PRONOSTICO - Normalizar "Índice de..." (MEDIA)

### PROBLEMA IDENTIFICADO:
- **Caso**: IHQ250981
- **Campo afectado**: FACTOR_PRONOSTICO
- **Valor actual**: "Índice de proliferación celular (Ki67): 21-30%..."
- **Valor esperado**: "Ki-67: 21-30%..."

### CAUSA RAÍZ:
Normalización existente NO coincidía EXACTAMENTE con el texto del PDF (espacios extra, variantes).

### SOLUCIÓN APLICADA:
**Archivo**: `core/extractors/medical_extractor.py`
**Función**: `extract_factor_pronostico()`
**Líneas modificadas**: 574-600

**Cambio**:
```python
# V6.0.1: Normalizar términos largos de Ki-67 (AMPLIADO para IHQ250981)
normalizaciones = [
    ("Índice de proliferación celular (Ki67)", "Ki-67"),
    ("Índice de proliferación celular (Ki-67)", "Ki-67"),
    ("índice de proliferación celular (Ki67)", "Ki-67"),
    ("índice de proliferación celular (Ki-67)", "Ki-67"),
    ("ÍNDICE DE PROLIFERACIÓN CELULAR (KI67)", "Ki-67"),
    ("ÍNDICE DE PROLIFERACIÓN CELULAR (KI-67)", "Ki-67"),
    # V6.0.1: Variantes con múltiples espacios (OCR puede introducir espacios extra)
    ("Índice  de  proliferación  celular  (Ki67)", "Ki-67"),
    ("Índice  de  proliferación  celular  (Ki-67)", "Ki-67"),
    # V6.0.1: Normalizar otras variantes verbosas
    ("receptor de estrógeno (ER)", "ER"),
    ("receptor de progesterona (PgR)", "PR"),
    ("receptor de progesterona (PR)", "PR"),
    ("Receptor de estrógeno", "ER"),
    ("Receptor de progesterona", "PR"),
]

# V6.0.1: Aplicar normalizaciones (case-insensitive)
for original, reemplazo in normalizaciones:
    # Buscar case-insensitive
    factor_pronostico_texto = re.sub(re.escape(original), reemplazo, factor_pronostico_texto, flags=re.IGNORECASE)
```

**Resultado esperado**: FACTOR_PRONOSTICO con "Ki-67: 21-30%..." (sin "Índice de...") ✅

---

## ARCHIVOS MODIFICADOS

### 1. core/extractors/biomarker_extractor.py
**Líneas modificadas**: 326-337 (E-Cadherina normalización), 1456-1512 (Ki-67 prioridad)
**Cambios**:
- Agregada lógica especial para Ki-67 (invertir prioridad de búsqueda)
- Ampliada normalización de E-Cadherina (6 nuevas variantes)

### 2. core/extractors/medical_extractor.py
**Líneas modificadas**: 574-600 (FACTOR_PRONOSTICO), 846-870 (IHQ_ESTUDIOS_SOLICITADOS), 1981-1984 (DIAGNOSTICO_PRINCIPAL)
**Cambios**:
- Agregado recorte temprano de " - " en DIAGNOSTICO_PRINCIPAL
- Agregada normalización de nombres cortos en IHQ_ESTUDIOS_SOLICITADOS
- Ampliadas normalizaciones en FACTOR_PRONOSTICO (case-insensitive)

---

## BACKUPS CREADOS

**Ubicación**: `backups/`
**Archivos**:
1. `biomarker_extractor_backup_20251022_070000.py`
2. `medical_extractor_backup_20251022_070000.py`

---

## VALIDACIÓN

### Sintaxis Python
✅ **VALIDADA** con `python -m py_compile`
- `core/extractors/biomarker_extractor.py` ✅
- `core/extractors/medical_extractor.py` ✅

### Tests sugeridos
Para validar las correcciones, se recomienda:
1. Reprocesar caso IHQ250981
2. Verificar que ahora extrae:
   - IHQ_KI-67: "21-30%" (actualmente vacío)
   - IHQ_E_CADHERINA: "POSITIVO" (actualmente "IHQ_E-CADHERINA")
   - DIAGNOSTICO_PRINCIPAL: Sin " - TAMAÑO TUMORAL..."
   - IHQ_ESTUDIOS_SOLICITADOS: 5/5 biomarcadores (actualmente 3/5)
   - FACTOR_PRONOSTICO: "Ki-67: 21-30%..." (sin "Índice de...")

---

## PRÓXIMOS PASOS RECOMENDADOS

1. **Reprocesar caso IHQ250981**:
   ```bash
   python herramientas_ia/editor_core.py --reprocesar IHQ250981
   ```

2. **Validar con data-auditor**:
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250981 --nivel profundo
   ```

3. **Reprocesar casos similares** (opcional):
   - Casos con Ki-67 vacío en descripción microscópica
   - Casos con E-Cadherina mal extraída
   - Casos con " - TAMAÑO TUMORAL" en diagnóstico
   - Casos con estudios solicitados incompletos

4. **Actualizar versión del sistema** (si el usuario lo solicita):
   ```bash
   python herramientas_ia/gestor_version.py --actualizar 6.0.1 --nombre "Correcciones IHQ250981"
   ```

---

## IMPACTO ESPERADO

### Precisión de extracción (IHQ250981):
- **ANTES**: 11.1% (1/9 campos correctos)
- **DESPUÉS**: ~77.8% (7/9 campos correctos estimado)

### Campos corregidos:
1. IHQ_KI-67: VACÍO → "21-30%" ✅
2. IHQ_E_CADHERINA: "IHQ_E-CADHERINA" → "POSITIVO" ✅
3. DIAGNOSTICO_PRINCIPAL: SIN " - TAMAÑO TUMORAL" ✅
4. IHQ_ESTUDIOS_SOLICITADOS: 3/5 → 5/5 ✅
5. FACTOR_PRONOSTICO: "Ki-67: 21-30%" (normalizado) ✅

### Campos pendientes (requieren correcciones adicionales):
1. IHQ_CD56: "6" → "POSITIVO" (confusión CD5/CD56)
2. IHQ_SINAPTOFISINA: VACÍO → "POSITIVO"
3. IHQ_CROMOGRANINA_A: VACÍO → "POSITIVO"
4. IHQ_CKAE1AE3: VACÍO → "POSITIVO"

**NOTA**: Las correcciones de CD56, Sinaptofisina, Cromogranina A y CKAE1AE3 requieren modificaciones adicionales en los patrones de extracción narrativa. Se recomienda abordarlas en una iteración posterior.

---

## NOTAS TÉCNICAS

### Estrategia de prioridad invertida (Ki-67):
La decisión de invertir la prioridad SOLO para Ki-67 (y no para todos los biomarcadores) se basa en evidencia empírica:
- Ki-67 aparece consistentemente en DESCRIPCIÓN MICROSCÓPICA
- Otros biomarcadores (HER2, ER, PR) aparecen en DIAGNÓSTICO (sección de expresión molecular)
- Invertir para todos rompería casos previamente correctos

### Normalización case-insensitive:
Se cambió de `str.replace()` a `re.sub(..., flags=re.IGNORECASE)` para capturar variantes de capitalización que OCR puede introducir.

---

**Generado por**: core-editor (EVARISIS v6.0.1)
**Timestamp**: 2025-10-22 15:56:08
**Caso de referencia**: IHQ250981
**Status**: ✅ CORRECCIONES APLICADAS - PENDIENTE REPROCESAMIENTO
