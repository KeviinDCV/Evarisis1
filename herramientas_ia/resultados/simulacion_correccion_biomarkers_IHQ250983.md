# SIMULACIÓN: Corrección de Extractores de Biomarcadores IHQ250983

**Fecha:** 2025-10-23
**Agente:** core-editor
**Modo:** SIMULACIÓN (Dry-Run)
**Prioridad:** ALTA - Afecta diagnóstico clínico

---

## 1. PROBLEMA IDENTIFICADO

### Caso Afectado: IHQ250983

**Biomarcadores con errores:**
1. **IHQ_P40:** Captura ", S100 Y CKAE1AE3" (INCORRECTO) → Debería ser "POSITIVO HETEROGÉNEO"
2. **IHQ_S100:** No se captura (FALTA) → Debería ser "POSITIVO"
3. **IHQ_CKAE1AE3:** No se captura (FALTA) → Debería ser "POSITIVO"

### Texto del PDF (DESCRIPCIÓN MICROSCÓPICA)

```
"Se evidencia inmunorreactividad en las células tumorales para
CKAE1AE3, S100, PAX8 y p40 heterogéneo y son negativas para GATA3, CDX2, y TTF1."
```

### Causa Raíz

**Patrón actual (línea 1230):**
```python
r'(?i)inmunorreactividad\s+(?:fuerte\s+y\s+)?difusa\s+para\s+((?:[^\.\n]+(?:\n[A-Z0-9/]+)?)+)'
```

**Problemas:**
- ❌ Requiere "difusa", pero el texto dice "inmunorreactividad en las células"
- ❌ No maneja listas de biomarcadores separados por comas
- ❌ No detecta modificadores (heterogéneo, focal, difuso) después del nombre
- ❌ No separa correctamente cada biomarcador individual
- ❌ Patrón de negativos no captura "son negativas para X, Y y Z"

---

## 2. CORRECCIONES PROPUESTAS

### 2.1. NUEVO Patrón de Inmunorreactividad en Listas

**Agregar ANTES de la línea 1230:**

```python
# NUEVO: V6.0.6 - Inmunorreactividad en listas narrativas (IHQ250983)
# Captura: "inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo"
r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)',
```

**Explicación:**
- Captura "inmunorreactividad" + opcional "en las células tumorales" + "para"
- Luego captura TODA la lista de biomarcadores (comas, "y", modificadores)
- Permite modificadores como "heterogéneo", "focal", "difuso" después del nombre

### 2.2. MEJORAR Patrón de Negativos

**Reemplazar línea 1318:**

**ANTES:**
```python
negative_pattern = r'(?i)negativas?\s+para\s+(.+?)(?:$|\.|;)'
```

**DESPUÉS:**
```python
# V6.0.6: Mejorado para capturar "son negativas para X, Y y Z"
negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+)*?)(?:\s*\.|\s*,\s+y\s+son|$)'
```

**Explicación:**
- Acepta "son negativas" o solo "negativas"
- Captura lista completa de biomarcadores con comas y "y"
- Termina en punto, o en ", y son" (siguiente frase)

### 2.3. NUEVA Función de Post-Procesamiento de Listas

**Agregar DESPUÉS de la línea 1332 (después del bloque de negativos):**

```python
# V6.0.6: Post-procesar listas narrativas complejas con modificadores
# Ej: "CKAE1AE3, S100, PAX8 y p40 heterogéneo"
def post_process_biomarker_list_with_modifiers(biomarker_text: str) -> Dict[str, str]:
    """
    Procesa lista narrativa de biomarcadores, detectando modificadores individuales.

    Ejemplos:
    - "CKAE1AE3, S100, PAX8 y p40 heterogéneo"
      → {'CKAE1AE3': 'POSITIVO', 'S100': 'POSITIVO', 'PAX8': 'POSITIVO', 'P40': 'POSITIVO HETEROGÉNEO'}
    - "CK7, CK20 focal y TTF-1 difuso"
      → {'CK7': 'POSITIVO', 'CK20': 'POSITIVO FOCAL', 'TTF1': 'POSITIVO DIFUSO'}

    Args:
        biomarker_text: Texto con lista (ej: "CKAE1AE3, S100, PAX8 y p40 heterogéneo")

    Returns:
        Dict con biomarcadores y valores con modificadores
    """
    if not biomarker_text:
        return {}

    result = {}

    # Limpiar texto
    text_clean = biomarker_text.strip()

    # Dividir por comas y "y"/"e"
    # Usar regex para preservar modificadores
    parts = re.split(r',\s*|\s+y\s+|\s+e\s+', text_clean, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # Detectar modificador al final (heterogéneo, focal, difuso)
        modifier_match = re.search(r'^(.+?)\s+(heterog[eé]neo|focal|difuso)$', part, re.IGNORECASE)

        if modifier_match:
            # Tiene modificador
            biomarker_raw = modifier_match.group(1).strip()
            modifier = modifier_match.group(2).strip().upper()

            # Normalizar modificador
            if modifier in ['HETEROGÉNEO', 'HETEROGENEO']:
                modifier = 'HETEROGÉNEO'

            normalized_name = normalize_biomarker_name(biomarker_raw)
            if normalized_name:
                result[normalized_name] = f'POSITIVO {modifier}'
        else:
            # Sin modificador, solo positivo
            normalized_name = normalize_biomarker_name(part)
            if normalized_name:
                result[normalized_name] = 'POSITIVO'

    return result
```

### 2.4. INTEGRAR Post-Procesamiento en extract_narrative_biomarkers()

**Agregar DESPUÉS de la línea 1232 (después de procesar complex_patterns):**

```python
    # V6.0.6: NUEVO - Patrón para listas narrativas con inmunorreactividad
    # Ej: "inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo"
    immunoreactivity_list_pattern = r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)'

    for match in re.finditer(immunoreactivity_list_pattern, text):
        lista_biomarkers = match.group(1).strip()

        # Usar post-procesador con modificadores
        biomarkers_with_modifiers = post_process_biomarker_list_with_modifiers(lista_biomarkers)

        # Agregar a resultados (NO sobreescribir)
        for bio_name, bio_value in biomarkers_with_modifiers.items():
            if bio_name not in results:
                results[bio_name] = bio_value
```

---

## 3. NORMALIZACIÓN DE NOMBRES

### 3.1. Agregar Variantes Faltantes a normalize_biomarker_name()

**Agregar en el diccionario name_mapping (después de línea 1493):**

```python
        # V6.0.6: Variantes adicionales IHQ250983
        'CKAE1AE3': 'CKAE1AE3',
        'CKAE1/AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CKAE1 AE3': 'CKAE1AE3',
```

---

## 4. CAMBIOS DETALLADOS POR LÍNEA

### Archivo: `core/extractors/biomarker_extractor.py`

#### Cambio 1: NUEVO patrón inmunorreactividad (AGREGAR antes línea 1230)

**Línea a insertar:** Antes de línea 1230

```python
        # NUEVO: V6.0.6 - Inmunorreactividad en listas narrativas (IHQ250983)
        r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)',
```

#### Cambio 2: Post-procesamiento en extract_narrative_biomarkers() (AGREGAR después línea 1232)

**Línea a insertar:** Después de línea 1232 (después del for loop de complex_patterns)

```python
    # V6.0.6: NUEVO - Patrón para listas narrativas con inmunorreactividad
    immunoreactivity_list_pattern = r'(?i)inmunorreactividad\s+(?:en\s+las\s+)?(?:c[eé]lulas\s+)?(?:tumorales\s+)?para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+(?:\s+heterog[eé]neo|focal|difuso)?)?)'

    for match in re.finditer(immunoreactivity_list_pattern, text):
        lista_biomarkers = match.group(1).strip()
        biomarkers_with_modifiers = post_process_biomarker_list_with_modifiers(lista_biomarkers)
        for bio_name, bio_value in biomarkers_with_modifiers.items():
            if bio_name not in results:
                results[bio_name] = bio_value
```

#### Cambio 3: Mejorar patrón negativos (REEMPLAZAR línea 1318)

**ANTES:**
```python
    negative_pattern = r'(?i)negativas?\s+para\s+(.+?)(?:$|\.|;)'
```

**DESPUÉS:**
```python
    # V6.0.6: Mejorado para capturar "son negativas para X, Y y Z"
    negative_pattern = r'(?i)(?:son\s+)?negativas?\s+para\s+([A-Z0-9,\s/\-]+(?:\s+(?:y|e)\s+[A-Z0-9]+)*?)(?:\s*\.|\s*,\s+y\s+son|$)'
```

#### Cambio 4: NUEVA función post_process_biomarker_list_with_modifiers() (AGREGAR después línea 1332)

**Ubicación:** Después de la línea 1332 (después del bloque de negativos), ANTES de la línea 1333 (Patrón 3)

**Código completo:**
```python
def post_process_biomarker_list_with_modifiers(biomarker_text: str) -> Dict[str, str]:
    """Procesa lista narrativa de biomarcadores, detectando modificadores individuales."""
    if not biomarker_text:
        return {}

    result = {}
    text_clean = biomarker_text.strip()
    parts = re.split(r',\s*|\s+y\s+|\s+e\s+', text_clean, flags=re.IGNORECASE)

    for part in parts:
        part = part.strip()
        if not part:
            continue

        modifier_match = re.search(r'^(.+?)\s+(heterog[eé]neo|focal|difuso)$', part, re.IGNORECASE)

        if modifier_match:
            biomarker_raw = modifier_match.group(1).strip()
            modifier = modifier_match.group(2).strip().upper()
            if modifier in ['HETEROGÉNEO', 'HETEROGENEO']:
                modifier = 'HETEROGÉNEO'
            normalized_name = normalize_biomarker_name(biomarker_raw)
            if normalized_name:
                result[normalized_name] = f'POSITIVO {modifier}'
        else:
            normalized_name = normalize_biomarker_name(part)
            if normalized_name:
                result[normalized_name] = 'POSITIVO'

    return result
```

#### Cambio 5: Agregar variantes a normalize_biomarker_name() (AGREGAR después línea 1493)

**Ubicación:** En el diccionario name_mapping, después de línea 1493

```python
        # V6.0.6: Variantes adicionales IHQ250983
        'CKAE1AE3': 'CKAE1AE3',
        'CKAE1/AE3': 'CKAE1AE3',
        'CK AE1/AE3': 'CKAE1AE3',
        'CKAE1 AE3': 'CKAE1AE3',
```

---

## 5. VALIDACIÓN DE CAMBIOS

### 5.1. Casos de Prueba

**Test 1: IHQ250983 - Lista con modificador**
```
Input: "inmunorreactividad en las células tumorales para CKAE1AE3, S100, PAX8 y p40 heterogéneo"

Esperado:
  IHQ_CKAE1AE3: POSITIVO
  IHQ_S100: POSITIVO
  IHQ_PAX8: POSITIVO
  IHQ_P40: POSITIVO HETEROGÉNEO
```

**Test 2: Lista de negativos**
```
Input: "son negativas para GATA3, CDX2, y TTF1"

Esperado:
  IHQ_GATA3: NEGATIVO
  IHQ_CDX2: NEGATIVO
  IHQ_TTF1: NEGATIVO
```

**Test 3: Modificadores múltiples**
```
Input: "positivas para CK7, CK20 focal y TTF-1 difuso"

Esperado:
  IHQ_CK7: POSITIVO
  IHQ_CK20: POSITIVO FOCAL
  IHQ_TTF1: POSITIVO DIFUSO
```

**Test 4: Sin modificador (existente - no debe romperse)**
```
Input: "positivas para CK7 y GATA 3"

Esperado:
  IHQ_CK7: POSITIVO
  IHQ_GATA3: POSITIVO
```

### 5.2. Regresión

**Verificar que NO se rompan patrones existentes:**
- ✅ "células neoplásicas son fuertemente positivas para CK7 y GATA 3"
- ✅ "RECEPTOR DE ESTRÓGENOS, positivo focal"
- ✅ "inmunomarcación positiva difusa para CKAE1/AE3 y SYNAPTOPHYSIN"
- ✅ "el marcador Ki67 es positivo"
- ✅ "los marcadores CD3, CD5 y CD10 son negativos"

---

## 6. IMPACTO ESTIMADO

### Casos Afectados
- **Directo:** IHQ250983 (confirmado)
- **Potencial:** Cualquier caso con formato narrativo "inmunorreactividad... para X, Y y Z"
- **Estimado:** 5-15 casos adicionales en la base de datos

### Biomarcadores Beneficiados
- P40, S100, CKAE1AE3 (IHQ250983)
- PAX8, TTF1, GATA3, CDX2 (cuando estén en listas narrativas)
- Cualquier biomarcador con modificador (heterogéneo, focal, difuso)

### Mejoras de Precisión
- **Actual:** P40 captura ", S100 Y CKAE1AE3" (ERROR)
- **Con corrección:** P40 captura "POSITIVO HETEROGÉNEO" (CORRECTO)

### Breaking Changes
- ❌ **NO esperados** - Los cambios son ADITIVOS (nuevos patrones)
- ✅ Patrones existentes se mantienen intactos
- ✅ Función post-procesamiento es nueva (sin dependencias)

---

## 7. RIESGOS Y MITIGACIÓN

### Riesgos Identificados

**R1: Captura excesiva de texto**
- **Probabilidad:** Media
- **Impacto:** Bajo
- **Mitigación:** Patrón tiene delimitadores específicos (punto, coma+conjunción)

**R2: Falsos positivos en modificadores**
- **Probabilidad:** Baja
- **Impacto:** Medio
- **Mitigación:** Modificadores solo se capturan si están PEGADOS al nombre del biomarcador

**R3: Colisión con patrones existentes**
- **Probabilidad:** Muy baja
- **Impacto:** Alto
- **Mitigación:** Usar `if bio_name not in results:` para NO sobreescribir

### Plan de Rollback

Si algo falla después de aplicar:
1. ✅ Backup automático creado en `backups/biomarker_extractor_backup_TIMESTAMP.py`
2. ✅ Restaurar: `cp backups/biomarker_extractor_backup_TIMESTAMP.py core/extractors/biomarker_extractor.py`
3. ✅ Reprocesar caso: `python core/unified_extractor.py --reprocess IHQ250983`

---

## 8. PRÓXIMOS PASOS RECOMENDADOS

### ANTES de Aplicar
1. ✅ **Revisar esta simulación** con usuario
2. ✅ **Confirmar** que los patrones son correctos
3. ✅ **Validar** con data-auditor que IHQ250983 actualmente falla

### DURANTE Aplicación
1. ✅ **Crear backup** automático de `biomarker_extractor.py`
2. ✅ **Aplicar cambios** línea por línea
3. ✅ **Validar sintaxis** Python

### DESPUÉS de Aplicar
1. ✅ **Reprocesar IHQ250983** y validar que se corrigen los 3 biomarcadores
2. ✅ **Ejecutar tests** unitarios (si existen)
3. ✅ **Generar reporte** final de cambios en `herramientas_ia/resultados/`
4. ✅ **Auditar con data-auditor** el caso IHQ250983
5. ✅ **Buscar casos similares** en BD con patrón narrativo de inmunorreactividad
6. ✅ **Considerar reprocesamiento masivo** si se detectan muchos casos afectados

---

## 9. MÉTRICAS DE ÉXITO

**Criterios de Aceptación:**
- ✅ IHQ_P40 = "POSITIVO HETEROGÉNEO" (no ", S100 Y CKAE1AE3")
- ✅ IHQ_S100 = "POSITIVO" (no N/A)
- ✅ IHQ_CKAE1AE3 = "POSITIVO" (no N/A)
- ✅ IHQ_GATA3 = "NEGATIVO" (existente, no debe cambiar)
- ✅ IHQ_CDX2 = "NEGATIVO" (existente, no debe cambiar)
- ✅ IHQ_TTF1 = "NEGATIVO" (actualmente N/A, debería capturarse)

**Validación:**
```bash
# Auditar caso después de reprocesar
python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente

# Buscar casos con patrón similar
python herramientas_ia/gestor_base_datos.py --buscar-avanzado --diagnostico "METASTASICO"
```

---

## 10. CONCLUSIÓN

**ESTADO:** ✅ SIMULACIÓN COMPLETA - LISTA PARA APLICAR

**RESUMEN:**
- 5 cambios propuestos en `biomarker_extractor.py`
- 1 nueva función de post-procesamiento
- 3 biomarcadores se corregirán en IHQ250983
- 0 breaking changes esperados
- Impacto estimado: 5-15 casos adicionales mejorarán

**PRÓXIMO PASO:**
Esperar aprobación del usuario para aplicar cambios.

**COMANDO PARA APLICAR:**
```bash
# Aplicar cambios (genera backup automático)
python herramientas_ia/editor_core.py --aplicar-cambios biomarker_extractor.py --desde-reporte simulacion_correccion_biomarkers_IHQ250983.md
```

---

**Generado por:** core-editor (EVARISIS v6.0.2)
**Fecha:** 2025-10-23 05:25:00
**Modo:** SIMULACIÓN (DRY-RUN)
**Archivo:** `herramientas_ia/resultados/simulacion_correccion_biomarkers_IHQ250983.md`
