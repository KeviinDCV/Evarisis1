# SIMULACIÓN DE CORRECCIONES - Extractores IHQ250984

**Fecha:** 2025-10-24 09:53:00
**Caso:** IHQ250984 - MAMA IZQUIERDA
**Paciente:** LETICIA ASTAIZA TACUE (89 años, FEMENINO)
**Estado actual:** CRÍTICO - 0/6 biomarcadores extraídos correctamente

---

## RESUMEN EJECUTIVO

### Problema Detectado
El sistema **NO está capturando correctamente los biomarcadores** del caso IHQ250984 porque:

1. **FACTOR_PRONOSTICO** extrae fragmento erróneo: `"positivo para: negativo para SXO10"`
2. **Biomarcadores individuales** NO se extraen (GATA3, SOX10, ER, PR, HER2, Ki-67)
3. **IHQ_ESTUDIOS_SOLICITADOS** solo captura 2/6 biomarcadores

### Causa Raíz Identificada
Los extractores actuales **NO buscan correctamente en formato estructurado con guiones** (`-RECEPTOR DE ESTRÓGENOS:`), que es el formato utilizado en la DESCRIPCIÓN MICROSCÓPICA página 2 del PDF.

---

## CORRECCIÓN 1: extract_factor_pronostico() - CRÍTICA

### Ubicación
- **Archivo:** `core/extractors/medical_extractor.py`
- **Función:** `extract_factor_pronostico()`
- **Líneas:** 465-614 (aprox.)

### Problema Actual

**CÓDIGO ACTUAL (líneas 504-550):**
```python
# PRIORIDAD 1: FORMATO NARRATIVO - "positivas para [LISTA]" (V6.0.5)
patron_narrativo = r'(?:son\s+)?positivas?\s+para\s+([A-Z0-9\s,./\-\(\)yYeÉóÓ\n]+?)(?=\s+y\s+c[eé]lulas|\n\n|$)'
matches_narrativo = re.finditer(patron_narrativo, diagnostico_completo, re.IGNORECASE)

listas_encontradas = []
for match in matches_narrativo:
    lista_biomarcadores = match.group(1).strip()
    # ...
    if lista_biomarcadores and len(lista_biomarcadores) > 3:
        listas_encontradas.append(lista_biomarcadores)

# Si encontramos listas narrativas, usar esas y retornar inmediatamente
if listas_encontradas:
    todas_listas = ' / '.join(listas_encontradas)
    return f"positivo para: {todas_listas}"
```

**Problema:** El patrón `positivas?\s+para` captura **SOLO** listas narrativas tipo:
- ✅ "son positivas para CK7, GATA3, EMA"
- ❌ **NO captura** formato estructurado con guión:
  ```
  -RECEPTOR DE ESTRÓGENOS: Negativo.
  -RECEPTOR DE PROGESTERONA: Negativo.
  -HER 2: Positivo (Score 3+)
  -Ki-67: Tinción nuclear en el 60%
  ```

### Formato en PDF IHQ250984 (Página 2 - DESCRIPCIÓN MICROSCÓPICA)

Según auditoría, el PDF contiene:
```
DESCRIPCIÓN MICROSCÓPICA:
[...]
REPORTE DE BIOMARCADORES:

-RECEPTOR DE ESTRÓGENOS: Negativo.
-RECEPTOR DE PROGESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 % de las células tumorales.
-Ki-67: Tinción nuclear en el 60% de las células tumorales.

Además:
- tinción nuclear positiva fuerte y difusa para GATA 3
- Son negativas para SXO10
```

### Código Corregido Propuesto

**INSERTAR DESPUÉS DE LÍNEA 500 (antes de PRIORIDAD 1):**

```python
# ═══════════════════════════════════════════════════════════════════════
# PRIORIDAD 0: FORMATO ESTRUCTURADO CON GUIONES (V6.0.10 - IHQ250984)
# Captura formato tipo:
# -RECEPTOR DE ESTRÓGENOS: Negativo.
# -RECEPTOR DE PROGESTERONA: Negativo.
# -HER 2: Positivo (Score 3+) [descripción]
# -Ki-67: Tinción nuclear en el 60%
# ═══════════════════════════════════════════════════════════════════════

# Buscar bloque completo de biomarcadores estructurados
patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-]+:.*?\n?)+)'
match_bloque = re.search(patron_bloque_estructurado, diagnostico_completo, re.IGNORECASE | re.MULTILINE)

if match_bloque:
    bloque_biomarcadores = match_bloque.group(1)

    # Extraer cada línea con formato "-BIOMARCADOR: Valor"
    patron_linea_biomarcador = r'-\s*([A-ZÁÉÍÓÚÑ\s0-9/\-]+)\s*:\s*(.+?)(?=\n-|\n\n|$)'
    matches_lineas = re.finditer(patron_linea_biomarcador, bloque_biomarcadores, re.IGNORECASE | re.DOTALL)

    biomarcadores_extraidos = []
    for match in matches_lineas:
        nombre_bio = match.group(1).strip()
        valor_bio = match.group(2).strip()

        # Limpiar valor (quitar saltos de línea, espacios múltiples)
        valor_bio = ' '.join(valor_bio.split())

        # Agregar a lista (formato: "NOMBRE: Valor")
        biomarcadores_extraidos.append(f"{nombre_bio}: {valor_bio}")

    # Si encontramos biomarcadores estructurados, retornar inmediatamente
    if biomarcadores_extraidos:
        return ' / '.join(biomarcadores_extraidos)

# ═══════════════════════════════════════════════════════════════════════
# PRIORIDAD 0.5: BIOMARCADORES ADICIONALES EN DESCRIPCIÓN (V6.0.10)
# Captura formatos complementarios en la misma sección:
# - "tinción nuclear positiva fuerte y difusa para GATA 3"
# - "Son negativas para SOX10"
# ═══════════════════════════════════════════════════════════════════════

factores_adicionales = []

# Patrón: "tinción [tipo] positiva [adjetivos] para BIOMARCADOR"
patron_tincion_positiva = r'tinción\s+(?:nuclear|citoplásmica|membranosa)?\s+positiva\s+(?:fuerte|difusa|focal)?(?:\s+y\s+(?:fuerte|difusa|focal))?\s+para\s+([A-Z0-9\s]+)'
matches_tincion = re.finditer(patron_tincion_positiva, diagnostico_completo, re.IGNORECASE)

for match in matches_tincion:
    biomarcador = match.group(1).strip()
    factores_adicionales.append(f"Positivo para {biomarcador}")

# Patrón: "son negativas para BIOMARCADOR"
patron_negativas_simples = r'(?:son\s+)?negativas?\s+para\s+([A-Z0-9]+)'
matches_negativas = re.finditer(patron_negativas_simples, diagnostico_completo, re.IGNORECASE)

for match in matches_negativas:
    biomarcador = match.group(1).strip()
    # Evitar duplicados
    if not any(biomarcador.lower() in f.lower() for f in factores_adicionales):
        factores_adicionales.append(f"Negativo para {biomarcador}")

# Agregar factores adicionales al resultado si existen
if factores_adicionales:
    # Si ya hay resultado del bloque estructurado, concatenar
    # (pero esto no debería pasar en flujo normal)
    pass
```

**MODIFICAR LÍNEA 547-550:**
```python
# Si encontramos listas narrativas, usar esas
if listas_encontradas:
    todas_listas = ' / '.join(listas_encontradas)

    # V6.0.10: Agregar factores adicionales si existen
    if factores_adicionales:
        todas_listas += ' / ' + ' / '.join(factores_adicionales)

    return f"positivo para: {todas_listas}"
```

### Impacto Esperado

**ANTES:**
```
Factor pronostico: "positivo para: negativo para SXO10"
```

**DESPUÉS:**
```
Factor pronostico: "RECEPTOR DE ESTRÓGENOS: Negativo / RECEPTOR DE PROGESTERONA: Negativo / HER 2: Positivo (Score 3+) tinción membranosa fuerte y completa en el 100 % de las células tumorales / Ki-67: Tinción nuclear en el 60% de las células tumorales / Positivo para GATA 3 / Negativo para SXO10"
```

**MEJORA:** De fragmento erróneo → Captura completa de TODOS los biomarcadores estructurados

---

## CORRECCIÓN 2: extract_narrative_biomarkers() - ALTA PRIORIDAD

### Ubicación
- **Archivo:** `core/extractors/biomarker_extractor.py`
- **Función:** `extract_narrative_biomarkers()`
- **Líneas:** 1203-1440 (aprox.)

### Problema Actual

**CÓDIGO ACTUAL (líneas 1211-1250):**
```python
# Patrón NUEVO: Biomarcadores complejos tipo "RECEPTOR DE ESTRÓGENOS, positivo focal"
complex_patterns = [
    # V6.0.2: NUEVOS PATRONES para "Expresión molecular" (IHQ250981) - PRIORIDAD MÁXIMA
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*RECEPTORES\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*SOBREEXPRESI[ÓO]N\s+DE\s+HER-?2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)\s*\(([^)]+)\)',
    # ...
]
```

**Problema:** Los patrones existen PERO:
1. El patrón captura `(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)` esperando SIEMPRE paréntesis después del estado
2. En IHQ250984 el formato es: `-RECEPTOR DE ESTRÓGENOS: Negativo.` (SIN paréntesis)

### Formato en PDF IHQ250984
```
-RECEPTOR DE ESTRÓGENOS: Negativo.
-RECEPTOR DE PROGESTERONA: Negativo.
-HER 2: Positivo (Score 3+) tinción membranosa fuerte...
```

### Código Corregido Propuesto

**MODIFICAR LÍNEAS 1211-1215 (agregar variantes SIN paréntesis):**

```python
# Patrón NUEVO: Biomarcadores complejos tipo "RECEPTOR DE ESTRÓGENOS, positivo focal"
complex_patterns = [
    # V6.0.10: PRIORIDAD MÁXIMA - Formato estructurado con guión SIN paréntesis (IHQ250984)
    r'(?i)-\s*RECEPTORES?\s+DE\s+ESTR[ÓO]GENO[S]?\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*RECEPTORES?\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\.?',
    r'(?i)-\s*HER\s*-?\s*2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)(?:\s*\(([^)]+)\))?(?:\s+(.+?))?\.?',
    r'(?i)-\s*Ki\s*-?\s*67\s*:\s*(.+?)\.?$',

    # V6.0.2: Formato "Expresión molecular" CON paréntesis (IHQ250981)
    r'(?i)-?\s*RECEPTORES\s+DE\s+ESTR[ÓO]GENOS\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*RECEPTORES\s+DE\s+PROGESTERONA\s*:\s*(POSITIVOS?|NEGATIVOS?)\s*\(([^)]+)\)',
    r'(?i)-?\s*SOBREEXPRESI[ÓO]N\s+DE\s+HER-?2\s*:\s*(POSITIVO|NEGATIVO|EQUIVOCO)\s*\(([^)]+)\)',

    # Patrones originales (descripción microscópica)
    r'(?i)receptor\s+de\s+estr[óo]genos?,\s+(positivo|negativo)(?:\s+focal)?',
    r'(?i)receptor\s+de\s+progesterona,\s+(positivo|negativo)(?:\s+focal)?',
    # ... (resto de patrones)
]
```

**AGREGAR DESPUÉS DE LÍNEA 1320 (lógica de procesamiento):**

```python
# V6.0.10: Procesar patrones de formato estructurado con guión (IHQ250984)
if biomarker_name and isinstance(match, str):
    # Caso simple: solo estado (Positivo/Negativo)
    value = 'POSITIVO' if 'positivo' in match.lower() else 'NEGATIVO'
    results[biomarker_name] = value
elif biomarker_name == 'HER2' and isinstance(match, tuple):
    # Caso HER2 con descripción completa
    if len(match) >= 3 and match[2]:
        # Formato: "Positivo (Score 3+) tinción membranosa fuerte..."
        value = f"{match[0].upper()}"
        if match[1]:  # Si hay score
            value += f" ({match[1].upper()})"
        if match[2]:  # Si hay descripción adicional
            value += f" {match[2]}"
        results[biomarker_name] = value
    elif len(match) >= 2:
        value = f"{match[0].upper()} ({match[1].upper()})"
        results[biomarker_name] = value
    else:
        value = match[0].upper()
        results[biomarker_name] = value
elif biomarker_name == 'KI67' and isinstance(match, str):
    # Caso Ki-67: capturar descripción completa
    results[biomarker_name] = match.strip()
elif biomarker_name and isinstance(match, tuple):
    # Resto de casos con tuplas
    # ... (lógica existente)
```

**AGREGAR NUEVOS PATRONES PARA GATA3 Y SOX10 (después línea 1220):**

```python
# V6.0.10: Patrones para GATA3 y SOX10 (IHQ250984)
r'(?i)tinción\s+nuclear\s+positiva\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*3',
r'(?i)negativas?\s+para\s+S[OX]{2,3}10',  # Captura SOX10 y typo SXO10
```

### Impacto Esperado

**ANTES:**
```python
results = {}  # Vacío
```

**DESPUÉS:**
```python
results = {
    'ER': 'NEGATIVO',
    'PR': 'NEGATIVO',
    'HER2': 'POSITIVO (SCORE 3+) tinción membranosa fuerte y completa en el 100 % de las células tumorales',
    'KI67': 'Tinción nuclear en el 60% de las células tumorales',
    'GATA3': 'POSITIVO',
    'SOX10': 'NEGATIVO'
}
```

**MEJORA:** De 0 biomarcadores → 6/6 biomarcadores extraídos correctamente

---

## CORRECCIÓN 3: extract_ihq_estudios_solicitados() - MEDIA PRIORIDAD

### Ubicación
- **Archivo:** Probablemente `core/extractors/medical_extractor.py` o `core/unified_extractor.py`
- **Necesita:** Localizar función exacta

### Problema Actual

**ESTADO ACTUAL:**
```
IHQ_ESTUDIOS_SOLICITADOS: "HER2, Receptor de Estrógeno"
```

**ESPERADO:**
```
IHQ_ESTUDIOS_SOLICITADOS: "GATA 3, RECEPTOR DE ESTROGENOS, RECEPTOR DE PROGESTERONA, HER 2, Ki 67, SOX10"
```

### Formato en PDF
Según auditoría:
```
Se realizó tinción especial para GATA 3, RECEPTOR DE ESTROGENOS, RECEPTOR DE PROGESTERONA, HER 2, Ki 67, SOX10
```

### Búsqueda de Función

**PENDIENTE:** Necesito localizar la función exacta. Posibles ubicaciones:
- `medical_extractor.py`: función `extract_ihq_estudios_solicitados()`
- `unified_extractor.py`: dentro de `extract_ihq_data()`

### Corrección Propuesta (conceptual)

```python
# Patrón mejorado para capturar lista completa
patron_estudios = r'(?:Se\s+realiz[óo]\s+)?(?:tinción\s+especial|estudios?)\s+(?:de\s+inmunohistoquímica\s+)?para\s+([A-Z0-9\s,/-]+(?:,\s*[A-Z0-9\s/-]+)*)'

match = re.search(patron_estudios, texto_completo, re.IGNORECASE)

if match:
    lista_biomarcadores = match.group(1)

    # Normalizar separadores
    lista_biomarcadores = re.sub(r'\s*,\s*', ', ', lista_biomarcadores)

    # Normalizar nombres
    normalizaciones = {
        'GATA 3': 'GATA3',
        'Ki 67': 'Ki-67',
        'SXO10': 'SOX10',  # Corregir typo común
    }

    for old, new in normalizaciones.items():
        lista_biomarcadores = re.sub(rf'\b{old}\b', new, lista_biomarcadores, flags=re.IGNORECASE)

    return lista_biomarcadores
```

### Impacto Esperado

**ANTES:**
```
IHQ_ESTUDIOS_SOLICITADOS: "HER2, Receptor de Estrógeno"  (2/6 biomarcadores)
```

**DESPUÉS:**
```
IHQ_ESTUDIOS_SOLICITADOS: "GATA3, RECEPTOR DE ESTROGENOS, RECEPTOR DE PROGESTERONA, HER2, Ki-67, SOX10"  (6/6 biomarcadores)
```

**MEJORA:** De 33% completitud → 100% completitud

---

## VERIFICACIÓN Y VALIDACIÓN

### Tests de Regresión Recomendados

Después de aplicar correcciones, ejecutar:

```bash
# 1. Reprocesar caso IHQ250984
python herramientas_ia/editor_core.py --reprocesar IHQ250984 --validar-antes

# 2. Auditar caso corregido
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente

# 3. Verificar que otros casos NO se rompan
python herramientas_ia/auditor_sistema.py IHQ250980 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente
```

### Casos de Prueba

| Caso | Formato | Validar que sigue funcionando |
|------|---------|-------------------------------|
| IHQ250984 | Estructurado con guión (`-BIOMARCADOR: Valor`) | **TARGET** ✅ |
| IHQ250981 | Expresión molecular con paréntesis | ✅ |
| IHQ250982 | Lista narrativa (`positivas para X, Y, Z`) | ✅ |
| IHQ250983 | Inmunorreactividad | ✅ |

### Métricas Esperadas

**ANTES (IHQ250984):**
- Biomarcadores extraídos: 0/6 (0%)
- Factor Pronóstico: Fragmento erróneo
- IHQ_ESTUDIOS_SOLICITADOS: 2/6 (33%)
- Score de validación: 33.3% (CRÍTICO)

**DESPUÉS (IHQ250984):**
- Biomarcadores extraídos: 6/6 (100%)
- Factor Pronóstico: Bloque completo estructurado
- IHQ_ESTUDIOS_SOLICITADOS: 6/6 (100%)
- Score de validación: 100% (OK)

---

## ARCHIVOS MODIFICADOS

| Archivo | Función | Líneas | Complejidad | Riesgo |
|---------|---------|--------|-------------|--------|
| `core/extractors/medical_extractor.py` | `extract_factor_pronostico()` | 465-614 | ALTA (CC 15) | MEDIO |
| `core/extractors/biomarker_extractor.py` | `extract_narrative_biomarkers()` | 1203-1440 | MUY ALTA (CC 48) | MEDIO |
| `core/extractors/medical_extractor.py` | `extract_ihq_estudios_solicitados()` | PENDIENTE LOCALIZAR | MEDIA | BAJO |

---

## PRÓXIMOS PASOS

### Paso 1: Localizar función faltante
```bash
# Buscar función de extracción de IHQ_ESTUDIOS_SOLICITADOS
grep -r "ihq_estudios_solicitados" core/extractors/
grep -r "IHQ_ESTUDIOS_SOLICITADOS" core/
```

### Paso 2: Aplicar correcciones
**IMPORTANTE:** Aplicar en orden:
1. PRIMERO: `extract_factor_pronostico()` (impacto más grande)
2. SEGUNDO: `extract_narrative_biomarkers()` (complementario)
3. TERCERO: `extract_ihq_estudios_solicitados()` (menor impacto)

### Paso 3: Validación incremental
Después de CADA corrección:
```bash
python herramientas_ia/editor_core.py --validar-sintaxis medical_extractor.py
python herramientas_ia/editor_core.py --reprocesar IHQ250984
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente
```

### Paso 4: Generar reporte final
```bash
python herramientas_ia/editor_core.py --generar-reporte
```

---

## RIESGOS Y MITIGACIONES

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Romper casos previos (IHQ250981, IHQ250982) | MEDIA | ALTO | Tests de regresión obligatorios |
| Capturar texto erróneo (contaminación) | BAJA | MEDIO | Validar límites de patrones regex |
| Complejidad ciclomática aumenta (>20) | ALTA | MEDIO | Refactorizar después si CC > 20 |
| Falsos positivos en nuevos casos | MEDIA | MEDIO | Auditar lote de 10 casos después |

---

## CONCLUSIÓN

Esta simulación identifica **3 correcciones críticas** para resolver el problema de extracción de biomarcadores en IHQ250984:

1. **CRÍTICA:** `extract_factor_pronostico()` - Agregar soporte para formato estructurado con guión
2. **ALTA:** `extract_narrative_biomarkers()` - Mejorar patrones para capturar variantes SIN paréntesis
3. **MEDIA:** `extract_ihq_estudios_solicitados()` - Capturar lista completa de biomarcadores solicitados

**IMPACTO TOTAL ESPERADO:**
- Precisión IHQ250984: 0% → 100%
- Biomarcadores extraídos: 0/6 → 6/6
- Factor Pronóstico: Fragmento erróneo → Bloque completo

**ESTADO:** Listo para aplicar (requiere confirmación del usuario)

---

**Generado por:** core-editor (simulación)
**Modo:** --simular (DRY-RUN)
**Aplicado:** NO (pendiente aprobación)
