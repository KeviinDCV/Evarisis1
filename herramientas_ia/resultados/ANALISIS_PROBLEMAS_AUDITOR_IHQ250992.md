# 🔍 ANÁLISIS DE PROBLEMAS DEL AUDITOR - Caso IHQ250992

**Fecha:** 29 de octubre de 2025
**Caso analizado:** IHQ250992 (MARIELA FERNANDEZ - MÉDULA ÓSEA)
**Versión auditor:** 3.0.2
**Estado:** ⚠️ MÚLTIPLES PROBLEMAS CRÍTICOS DETECTADOS

---

## 📋 RESUMEN EJECUTIVO

El auditor reportó **100% de validación sin errores**, pero un análisis manual del PDF y datos guardados revela **errores críticos de extracción y validación NO detectados**:

| Campo | Valor en BD | Valor Correcto (PDF) | Estado Auditor | ¿Detectó error? |
|-------|-------------|---------------------|----------------|-----------------|
| **DIAGNOSTICO_PRINCIPAL** | "N/A" | "NEOPLASIA DE CÉLULAS PLASMÁTICAS CON RESTRICCIÓN DE CADENAS LIVIANAS KAPPA" | ✅ OK | ❌ **NO** |
| **DIAGNOSTICO_COLORACION** | "NO APLICA" | "MUESTRA SUBÓPTIMA PARA DIAGNÓSTICO..." | ✅ OK | ❌ **NO** |
| **IHQ_ESTUDIOS_SOLICITADOS** | "CD5" (solo 1) | "CD38, CD138, CD56, CD117, kappa, lambda" (6 biomarcadores) | ✅ OK (implícito) | ❌ **NO** |
| **FACTOR_PRONOSTICO** | "NO APLICA" | "NO APLICA" (correcto) | ✅ OK | ✅ **SÍ** |

**Conclusión:** El auditor tiene **validaciones superficiales** que no detectan inconsistencias graves entre OCR y datos guardados.

---

## 🚨 PROBLEMA #1: DIAGNOSTICO_PRINCIPAL Vacío NO es Error Crítico

### Datos del Caso

**En BD (`datos_guardados`):**
```json
"Diagnostico Principal": "N/A"
```

**En PDF (sección "Descripcion Diagnostico"):**
```
Médula ósea. Biopsia. Estudios de inmunohistoquímica.
LOS HALLAZGOS MORFOLÓGICOS Y DE INMUNOHISTOQUÍMICA SON COMPATIBLES CON
NEOPLASIA DE CÉLULAS PLASMÁTICAS CON RESTRICCIÓN DE CADENAS LIVIANAS KAPPA.
```

**Diagnóstico correcto esperado:**
```
NEOPLASIA DE CÉLULAS PLASMÁTICAS CON RESTRICCIÓN DE CADENAS LIVIANAS KAPPA
```

### Comportamiento Actual del Auditor

**Función:** `_validar_diagnostico_principal()` (línea 792-838)

```python
def _validar_diagnostico_principal(self, datos_bd: Dict, texto_ocr: str) -> Dict:
    """Valida DIAGNOSTICO_PRINCIPAL.

    NOTA: El sistema NO extrae DIAGNOSTICO_PRINCIPAL en unified_extractor.
    Este campo se rellena directamente en la BD desde otro proceso.

    Por lo tanto, esta validación SOLO verifica:
    1. Que el campo NO esté vacío
    2. Que NO contenga datos contaminados del estudio M

    NO intenta validar contra OCR porque no hay patrón consistente.
    """
    diagnostico_bd = datos_bd.get('Diagnostico Principal', '').strip()

    # 1. Verificar que no esté vacío
    if not diagnostico_bd:
        return {
            'estado': 'ERROR',
            'mensaje': 'DIAGNOSTICO_PRINCIPAL está vacío',
            'valor_bd': diagnostico_bd
        }

    # 2. Validar que NO contenga gradación ni invasiones (datos del estudio M)
    # ...
```

### ❌ Problema Detectado

El auditor **DEBERÍA marcar ERROR** cuando `Diagnostico Principal == "N/A"`, pero **NO lo hace** porque:

1. La validación `if not diagnostico_bd:` solo detecta strings vacíos (`""`)
2. **"N/A" es un string NO vacío** → pasa la validación
3. No hay keywords de estudio M → pasa la validación
4. **Resultado:** ✅ OK (FALSO POSITIVO)

### 🔧 Corrección Necesaria

```python
# Verificar que no esté vacío O sea placeholder
PLACEHOLDERS_VACIOS = ['N/A', 'n/a', 'NO APLICA', '', 'SIN DATO', 'PENDIENTE']

if not diagnostico_bd or diagnostico_bd.upper() in PLACEHOLDERS_VACIOS:
    return {
        'estado': 'ERROR',
        'mensaje': 'DIAGNOSTICO_PRINCIPAL está vacío o es placeholder',
        'valor_bd': diagnostico_bd,
        'valor_esperado': '(extraer de "Descripcion Diagnostico" en OCR)',
        'sugerencia': 'Verificar extracción en unified_extractor o medical_extractor'
    }
```

---

## 🚨 PROBLEMA #2: DIAGNOSTICO_COLORACION Incorrecto NO Detectado

### Datos del Caso

**En BD (`datos_guardados`):**
```json
"Diagnostico Coloracion": "NO APLICA"
```

**En PDF (sección "Descripcion macroscopica"):**
```
Se realizan niveles al bloque M2510141 el cual corresponde a "biopsia de hueso" con diagnóstico de
"MUESTRA SUBÓPTIMA PARA DIAGNÓSTICO (ESCASA Y FRAGMENTADA). CELULARIDAD GLOBAL DEL 30%.
RELACIÓN MIELOIDE ERITROIDE DE 3:1. MADURACIÓN NORMAL DE LA LÍNEA MIELOIDE. SIN EVIDENCIA
MORFOLÓGICA DE INCREMENTO DE BLASTOS."
```

**Diagnóstico de coloración esperado:**
```
MUESTRA SUBÓPTIMA PARA DIAGNÓSTICO (ESCASA Y FRAGMENTADA). CELULARIDAD GLOBAL DEL 30%.
RELACIÓN MIELOIDE ERITROIDE DE 3:1. MADURACIÓN NORMAL DE LA LÍNEA MIELOIDE. SIN EVIDENCIA
MORFOLÓGICA DE INCREMENTO DE BLASTOS.
```

### Comportamiento Actual del Auditor

**Función:** `_validar_diagnostico_coloracion()` (línea 725-789)

```python
def _validar_diagnostico_coloracion(self, bd: Dict, ocr: str) -> Dict:
    valor_bd = bd.get('Diagnostico Coloracion', '')

    # Casos donde no aplica validacion
    if valor_bd in ['NO APLICA', '', 'N/A']:
        return {'estado': 'OK', 'valor': 'NO APLICA', 'mensaje': 'No hay estudio M previo'}

    # ... (resto de validaciones)
```

### ❌ Problema Detectado

El auditor **asume que "NO APLICA" es siempre correcto** sin validar contra el OCR:

1. Si BD dice "NO APLICA" → **retorna OK inmediatamente**
2. **NO busca** en OCR si realmente existe un diagnóstico de coloración
3. En este caso, **SÍ existe** diagnóstico en descripción macroscópica (bloque M2510141)
4. **Resultado:** ✅ OK (FALSO POSITIVO)

### 🔧 Corrección Necesaria

```python
def _validar_diagnostico_coloracion(self, bd: Dict, ocr: str) -> Dict:
    valor_bd = bd.get('Diagnostico Coloracion', '')

    # PASO 1: Buscar patrones de diagnóstico de coloración en OCR
    patron_diagnostico_m = r'bloque\s+M\d+.*?diagn[óo]stico\s+de\s*["\'](.+?)["\']'
    match_ocr = re.search(patron_diagnostico_m, ocr, re.IGNORECASE | re.DOTALL)

    diagnostico_en_ocr = match_ocr.group(1).strip() if match_ocr else None

    # CASO 1: OCR tiene diagnóstico pero BD dice "NO APLICA"
    if diagnostico_en_ocr and valor_bd in ['NO APLICA', '', 'N/A']:
        return {
            'estado': 'ERROR',
            'mensaje': 'DIAGNOSTICO_COLORACION marcado como "NO APLICA" pero existe en OCR',
            'valor_bd': valor_bd,
            'valor_en_ocr': diagnostico_en_ocr[:200],
            'sugerencia': 'Verificar extracción en medical_extractor.extract_diagnostico_coloracion()'
        }

    # CASO 2: BD dice "NO APLICA" y OCR no tiene diagnóstico → OK
    if not diagnostico_en_ocr and valor_bd in ['NO APLICA', '', 'N/A']:
        return {'estado': 'OK', 'valor': 'NO APLICA', 'mensaje': 'No hay estudio M previo'}

    # ... (resto de validaciones existentes)
```

---

## 🚨 PROBLEMA #3: IHQ_ESTUDIOS_SOLICITADOS Incompleto NO Detectado

### Datos del Caso

**En BD (`datos_guardados`):**
```json
"IHQ_ESTUDIOS_SOLICITADOS": "(no visible en debug_map, pero según auditor detectó biomarcadores)"
```

**Columnas IHQ_* pobladas:**
```json
"IHQ_CD5": "6",  // Solo este tiene valor
"IHQ_CD38": "",
"IHQ_CD138": "",
"IHQ_CD56": "",
// ... resto vacíos
```

**En PDF (descripción macroscópica):**
```
por lo que se realiza marcación para CD38, CD138, CD56, CD117, kappa y lambda.
```

**Estudios solicitados esperados:**
```
CD38, CD138, CD56, CD117, kappa, lambda
```

**Estudios REALMENTE extraídos:** Solo "CD5" (según columna IHQ_CD5 = "6")

### Comportamiento Actual del Auditor

**Función:** `_validar_biomarcadores_completos()` (línea 940-982)

```python
def _validar_biomarcadores_completos(self, bd: Dict, criticos: Dict, ocr: str) -> Dict:
    estudios = criticos.get('IHQ_ESTUDIOS_SOLICITADOS', '').split(', ')

    mapeados = []
    no_mapeados = []

    for biomarcador in estudios:
        if not biomarcador.strip():
            continue

        # V6.0.10: Usar búsqueda flexible
        columna = self._buscar_columna_biomarcador(biomarcador, bd, criticos)

        if columna:
            mapeados.append(biomarcador)
        else:
            no_mapeados.append(biomarcador)

    cobertura = (len(mapeados) / len(estudios) * 100) if estudios else 0

    return {
        'total_solicitado': len(estudios),
        'mapeados': len(mapeados),
        'no_mapeados': len(no_mapeados),
        'cobertura': round(cobertura, 1),
        'lista_no_mapeados': no_mapeados,
        'estado': 'OK' if cobertura == 100 else 'WARNING'
    }
```

### ❌ Problemas Detectados

1. **Depende EXCLUSIVAMENTE de `criticos['IHQ_ESTUDIOS_SOLICITADOS']`**
   - Si el campo está mal extraído → validación incorrecta
   - **NO valida contra OCR** para verificar si la lista es completa

2. **NO detecta discrepancias entre OCR y BD**
   - OCR dice: "CD38, CD138, CD56, CD117, kappa, lambda"
   - BD dice: (solo CD5 tiene valor)
   - Auditor: ✅ OK (porque confía ciegamente en `IHQ_ESTUDIOS_SOLICITADOS`)

3. **Validación circular:**
   ```
   unified_extractor extrae IHQ_ESTUDIOS_SOLICITADOS (MAL)
        ↓
   auditor_sistema valida usando IHQ_ESTUDIOS_SOLICITADOS (MAL)
        ↓
   ✅ OK (porque compara dato malo con dato malo)
   ```

### 🔧 Corrección Necesaria

```python
def _validar_biomarcadores_completos(self, bd: Dict, criticos: Dict, ocr: str) -> Dict:
    """
    V6.1.0: VALIDACIÓN INDEPENDIENTE - Extrae estudios solicitados DIRECTAMENTE del OCR
    para evitar validación circular.
    """

    # PASO 1: Extraer estudios solicitados DIRECTAMENTE del OCR (independiente de BD)
    estudios_ocr = self._extraer_estudios_desde_ocr(ocr)
    estudios_bd = criticos.get('IHQ_ESTUDIOS_SOLICITADOS', '').split(', ')
    estudios_bd = [e.strip() for e in estudios_bd if e.strip()]

    # PASO 2: Validar que BD contenga TODOS los estudios del OCR
    faltantes_en_bd = [e for e in estudios_ocr if e not in estudios_bd]
    extras_en_bd = [e for e in estudios_bd if e not in estudios_ocr]

    # PASO 3: Validar que cada estudio tenga columna IHQ_* poblada
    mapeados = []
    no_mapeados = []

    for biomarcador in estudios_ocr:  # Usar OCR como fuente de verdad
        columna = self._buscar_columna_biomarcador(biomarcador, bd, criticos)

        if columna:
            valor = bd.get(columna) or criticos.get(columna)
            if valor and valor.strip():
                mapeados.append(biomarcador)
            else:
                no_mapeados.append(f"{biomarcador} (columna vacía: {columna})")
        else:
            no_mapeados.append(f"{biomarcador} (sin columna)")

    cobertura = (len(mapeados) / len(estudios_ocr) * 100) if estudios_ocr else 0

    # PASO 4: Determinar estado
    estado = 'OK'
    if faltantes_en_bd or no_mapeados:
        estado = 'ERROR'
    elif extras_en_bd:
        estado = 'WARNING'

    return {
        'total_solicitado_ocr': len(estudios_ocr),
        'total_solicitado_bd': len(estudios_bd),
        'estudios_ocr': estudios_ocr,
        'estudios_bd': estudios_bd,
        'faltantes_en_bd': faltantes_en_bd,
        'extras_en_bd': extras_en_bd,
        'mapeados': len(mapeados),
        'no_mapeados': no_mapeados,
        'cobertura': round(cobertura, 1),
        'estado': estado,
        'mensaje': self._generar_mensaje_biomarcadores(estado, faltantes_en_bd, no_mapeados)
    }

def _extraer_estudios_desde_ocr(self, ocr: str) -> List[str]:
    """Extrae estudios solicitados DIRECTAMENTE del OCR (independiente de BD)."""
    # Patrón 1: "se realiza marcación para X, Y, Z"
    patron1 = r'se\s+realiza.*?marcaci[óo]n\s+para\s+([^\.]+)'

    # Patrón 2: "ESTUDIOS DE INMUNOHISTOQUIMICA: X, Y, Z"
    patron2 = r'ESTUDIOS\s+DE\s+INMUNOHISTOQU[ÍI]MICA[:\s]+([^\.]+)'

    for patron in [patron1, patron2]:
        match = re.search(patron, ocr, re.IGNORECASE)
        if match:
            texto = match.group(1)
            # Parsear biomarcadores (reutilizar función existente)
            from core.extractors.medical_extractor import parse_biomarker_list
            biomarcadores = parse_biomarker_list(texto)
            if biomarcadores:
                return biomarcadores

    return []
```

---

## 🚨 PROBLEMA #4: Validaciones NO Usan OCR como Fuente de Verdad

### Problema Conceptual

El auditor **lee el debug_map correctamente** (línea 508-548), pero:

1. ✅ **SÍ obtiene** `texto_ocr` del debug_map
2. ✅ **SÍ obtiene** `datos_bd` del debug_map (NO consulta BD directamente)
3. ❌ **NO usa** `texto_ocr` para validar INDEPENDIENTEMENTE

### Comportamiento Actual

```python
def _inicializar_auditoria_inteligente(self, numero_caso: str, nivel: str):
    debug_map = self._obtener_debug_map(numero_caso)

    # ✅ CORRECTO: Extrae datos del debug_map
    datos_bd = debug_map.get('base_datos', {}).get('datos_guardados', {})
    texto_ocr = debug_map.get('ocr', {}).get('texto_consolidado', '')

    resultado = {
        '_datos_bd': datos_bd,      # Datos guardados en BD
        '_texto_ocr': texto_ocr,    # OCR del PDF
        # ...
    }
```

Pero luego en las validaciones:

```python
def _validar_diagnostico_principal(self, datos_bd: Dict, texto_ocr: str):
    diagnostico_bd = datos_bd.get('Diagnostico Principal', '').strip()

    # ❌ PROBLEMA: Solo valida BD, NO usa texto_ocr para comparar
    if not diagnostico_bd:
        return {'estado': 'ERROR', ...}

    # ✅ OK: Valida contaminación
    if contaminacion:
        return {'estado': 'ERROR', ...}

    # ❌ FALTA: NO valida contra texto_ocr (debería extraer diagnóstico del OCR y comparar)
    return {'estado': 'OK', ...}
```

### 🔧 Filosofía de Validación Correcta

```
FUENTE DE VERDAD: OCR del PDF (texto_consolidado en debug_map)
DATOS A VALIDAR: datos_guardados en BD

VALIDACIÓN CORRECTA:
1. Extraer campo X DIRECTAMENTE del OCR (independiente de BD)
2. Comparar con valor en BD
3. Si discrepancia → ERROR con detalle de ambos valores
4. Si coinciden → OK
5. Si OCR no tiene dato pero BD sí → WARNING (verificar)
6. Si OCR tiene dato pero BD no → ERROR (falta extracción)
```

---

## 🚨 PROBLEMA #5: Score 100% a Pesar de Errores Críticos

### Comportamiento Actual

**Función:** `_calcular_metricas_finales()` (línea 1012-1078)

```python
def _calcular_metricas_finales(self, resultado: Dict) -> None:
    auditoria_bd = resultado.get('auditoria_bd', {})

    total_validaciones = 5  # diagnostico_coloracion, principal, factor, biomarcadores, campos
    validaciones_ok = 0

    if auditoria_bd.get('diagnostico_coloracion', {}).get('estado') == 'OK':
        validaciones_ok += 1
    if auditoria_bd.get('diagnostico_principal', {}).get('estado') == 'OK':
        validaciones_ok += 1
    # ...

    score = (validaciones_ok / total_validaciones) * 100
```

### ❌ Problema Detectado

**Caso IHQ250992:**
- `diagnostico_coloracion`: ✅ OK (FALSO - debería ser ERROR)
- `diagnostico_principal`: ✅ OK (FALSO - debería ser ERROR)
- `factor_pronostico`: ✅ OK (VERDADERO)
- `biomarcadores`: ✅ OK (FALSO - debería ser ERROR)
- `campos_obligatorios`: ✅ OK (FALSO - debería ser ERROR)

**Score calculado:** 5/5 = 100% ✅ Excelente

**Score real:** 1/5 = 20% ❌ Crítico

### 🔧 Corrección Necesaria

1. **Arreglar validaciones individuales** (problemas #1-#4)
2. **Agregar validación de completitud general:**

```python
def _calcular_metricas_finales(self, resultado: Dict) -> None:
    # ... (cálculo existente)

    # NUEVA VALIDACIÓN: Completitud general
    datos_bd = resultado['_datos_bd']
    campos_criticos_vacios = []

    CAMPOS_CRITICOS = [
        'Diagnostico Principal',
        'Diagnostico Coloracion',
        'Factor pronostico',
        'IHQ_ESTUDIOS_SOLICITADOS',
        'Descripcion Diagnostico',
        'Descripcion macroscopica',
        'Descripcion microscopica'
    ]

    PLACEHOLDERS = ['N/A', 'NO APLICA', '', 'SIN DATO', 'PENDIENTE']

    for campo in CAMPOS_CRITICOS:
        valor = datos_bd.get(campo, '').strip()
        if not valor or valor.upper() in PLACEHOLDERS:
            # EXCEPCIÓN: Factor pronostico puede ser "NO APLICA" legítimamente
            if campo == 'Factor pronostico' and valor == 'NO APLICA':
                # Validar si realmente no aplica (verificar biomarcadores)
                if self._verificar_no_aplica_factor_pronostico(datos_bd):
                    continue

            campos_criticos_vacios.append(campo)

    if campos_criticos_vacios:
        validaciones_ok -= len(campos_criticos_vacios) * 0.2  # Penalizar score
        resultado['warnings'].append(
            f"Campos críticos vacíos/placeholder: {', '.join(campos_criticos_vacios)}"
        )
```

---

## 📊 RESUMEN DE CORRECCIONES NECESARIAS

### Prioridad 1 - CRÍTICO

1. **`_validar_diagnostico_principal()`**
   - Detectar placeholders ("N/A", "NO APLICA") como ERROR
   - Intentar extraer diagnóstico del OCR y comparar

2. **`_validar_diagnostico_coloracion()`**
   - NO asumir "NO APLICA" como correcto automáticamente
   - Buscar diagnóstico de coloración en OCR (bloque M, descripción macroscópica)
   - Comparar OCR vs BD

3. **`_validar_biomarcadores_completos()`**
   - Extraer estudios solicitados DIRECTAMENTE del OCR (independiente de BD)
   - Validar que BD contenga TODOS los estudios del OCR
   - Detectar faltantes y extras

### Prioridad 2 - IMPORTANTE

4. **`_calcular_metricas_finales()`**
   - Agregar validación de completitud general
   - Penalizar campos críticos vacíos/placeholder
   - Ajustar score real

5. **Agregar función `_extraer_estudios_desde_ocr()`**
   - Nueva función para extracción independiente
   - Evitar validación circular

### Prioridad 3 - MEJORA

6. **Mejorar mensajes de error**
   - Incluir valor esperado vs valor encontrado
   - Incluir sugerencias de corrección
   - Incluir ubicación en el código (archivo, función)

---

## 🎯 COMPORTAMIENTO ESPERADO DESPUÉS DE CORRECCIONES

### Caso IHQ250992 - Auditoría Corregida

```
PASO 3: AUDITORIA DE BASE DE DATOS (datos_guardados)
================================================================

Validando DIAGNOSTICO_COLORACION...
❌ ERROR: DIAGNOSTICO_COLORACION marcado como "NO APLICA" pero existe en OCR
   Valor BD: "NO APLICA"
   Valor OCR: "MUESTRA SUBÓPTIMA PARA DIAGNÓSTICO (ESCASA Y FRAGMENTADA)..."
   Sugerencia: Verificar medical_extractor.extract_diagnostico_coloracion()

Validando DIAGNOSTICO_PRINCIPAL...
❌ ERROR: DIAGNOSTICO_PRINCIPAL es placeholder
   Valor BD: "N/A"
   Valor esperado (OCR): "NEOPLASIA DE CÉLULAS PLASMÁTICAS CON RESTRICCIÓN..."
   Sugerencia: Verificar extracción en unified_extractor

Validando FACTOR_PRONOSTICO...
✅ OK: NO APLICA (no hay HER2/Ki-67/ER/PR)

Validando completitud de biomarcadores...
❌ ERROR: Estudios solicitados incompletos
   Esperado (OCR): CD38, CD138, CD56, CD117, kappa, lambda (6)
   En BD: CD5 (1)
   Faltantes: CD38, CD138, CD56, CD117, kappa, lambda
   Cobertura: 16.7% (1/6)

Validando campos obligatorios...
❌ ERROR: Campos críticos vacíos/placeholder:
   - Diagnostico Principal (N/A)
   - Diagnostico Coloracion (NO APLICA - pero existe en OCR)

================================================================
METRICAS FINALES
================================================================

Score de Validacion: 20.0%
Estado Final: ERROR (Crítico - requiere corrección inmediata)
Validaciones OK: 1/5
Errores: 4
Warnings: 0

❌ CASO REQUIERE CORRECCIÓN
```

---

## 📝 CONCLUSIÓN

El auditor actual tiene **validaciones superficiales** que confían ciegamente en los datos guardados sin validar contra el OCR (fuente de verdad). Esto genera **falsos positivos** (casos marcados como OK cuando tienen errores críticos).

**Causa raíz:** Validación circular (compara dato extraído vs dato extraído, en lugar de dato extraído vs OCR original).

**Solución:** Implementar validaciones independientes que extraigan datos directamente del OCR y comparen con BD.

**Impacto:** Sin estas correcciones, el auditor es **inútil** para detectar errores reales de extracción.

---

**Archivos a modificar:**
- `herramientas_ia/auditor_sistema.py` (funciones de validación)
- `.claude/agents/data-auditor.md` (actualizar documentación)

**Próximo paso:** Implementar correcciones en orden de prioridad.
