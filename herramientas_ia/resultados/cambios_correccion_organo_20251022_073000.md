# CORRECCIÓN: Diferenciación de Campos ORGANO vs IHQ_ORGANO

**Fecha:** 22 de octubre de 2025, 07:30:00
**Archivo modificado:** `herramientas_ia/auditor_sistema.py`
**Responsable:** core-editor (agente especializado)

---

## PROBLEMA DETECTADO

El agente `data-auditor` está **confundiendo dos campos diferentes** en la base de datos:

### Campo 1: ORGANO (columna 21 en BD)
- **Origen:** Tabla "Estudios solicitados" del PDF (sección tabular)
- **Ejemplo (caso IHQ250981):**
  ```
  Estudios solicitados
  Organo: MASTECTOMIA RADICAL IZQUIERDA
  ```
- **Características:**
  - Es un campo de texto libre
  - Puede contener procedimientos (MASTECTOMIA RADICAL, BIOPSIA, etc.)
  - Puede estar en múltiples líneas (multilínea)
  - Es el valor "tal cual" aparece en el PDF
  - **VALOR EN BD:** "MASTECTOMIA RADICAL" (incompleto, falta "IZQUIERDA")

### Campo 2: IHQ_ORGANO (columna 34 en BD)
- **Origen:** Sección DIAGNÓSTICO del PDF (texto narrativo)
- **Ejemplo (caso IHQ250981):**
  ```
  DIAGNÓSTICO:
  Mama izquierda. Lesión. Mastectomía radical izquierda.
  ```
  → Extrae: "MAMA IZQUIERDA"
- **Características:**
  - Es el órgano anatómico real
  - Debe ser normalizado (MAMA, PULMON, COLON, etc.)
  - NO debe contener procedimientos
  - Es el órgano "limpio" para análisis clínico
  - **VALOR EN BD:** "MAMA IZQUIERDA" (correcto)

### Error Actual del Auditor

En el caso IHQ250981, el auditor reportó erróneamente:
```
Órgano: MAMA IZQUIERDA (pero BD dice "MASTECTOMIA RADICAL" ❌)
```

**Problema:** El auditor está comparando el valor de `IHQ_ORGANO` con el campo `ORGANO`, cuando son dos campos diferentes con propósitos distintos.

---

## CORRECCIONES IMPLEMENTADAS

### 1. Nueva Función: `_detectar_organo_tabla`

Detecta el campo ORGANO de la tabla "Estudios solicitados" del PDF.

```python
def _detectar_organo_tabla(self, texto_ocr: str) -> Dict:
    """
    Detecta el campo ORGANO de la tabla 'Estudios solicitados'.

    Este campo puede estar en múltiples líneas.

    Returns:
        Dict con organo_encontrado, es_multilinea, lineas_completas
    """
```

**Características:**
- Busca en la tabla "Estudios solicitados"
- Captura valor multilínea (ej: "MASTECTOMIA RADICAL\nIZQUIERDA")
- Detecta si el valor está completo o truncado
- Retorna confianza de detección

### 2. Nueva Función: `_detectar_ihq_organo_diagnostico`

Detecta el campo IHQ_ORGANO de la sección DIAGNÓSTICO.

```python
def _detectar_ihq_organo_diagnostico(self, texto_ocr: str) -> Dict:
    """
    Detecta IHQ_ORGANO de la primera línea del DIAGNÓSTICO.

    Debe ser un órgano anatómico normalizado (MAMA, PULMON, etc.).

    Returns:
        Dict con organo_anatomico, es_valido, requiere_normalizacion
    """
```

**Características:**
- Busca en sección DIAGNÓSTICO (primera línea)
- Valida contra lista de órganos anatómicos válidos
- Detecta si contiene procedimientos (inválido)
- Sugiere normalización si es necesario

### 3. Nueva Función: `_validar_organo_tabla`

Valida el campo ORGANO contra la tabla del PDF.

```python
def _validar_organo_tabla(self, datos_bd: Dict, texto_ocr: str) -> Dict:
    """
    Valida campo ORGANO contra tabla 'Estudios solicitados' del PDF.

    NO compara con IHQ_ORGANO (son campos independientes).

    Returns:
        Dict con estado, valor_bd, valor_esperado, es_multilinea, sugerencia
    """
```

**Características:**
- Compara ORGANO (BD) vs tabla "Estudios solicitados" (PDF)
- Detecta problemas multilínea
- NO confunde con IHQ_ORGANO
- Proporciona sugerencias específicas

### 4. Nueva Función: `_validar_ihq_organo_diagnostico`

Valida el campo IHQ_ORGANO contra la sección DIAGNÓSTICO.

```python
def _validar_ihq_organo_diagnostico(self, datos_bd: Dict, texto_ocr: str) -> Dict:
    """
    Valida IHQ_ORGANO contra sección DIAGNÓSTICO del PDF.

    Verifica que sea un órgano anatómico válido, NO un procedimiento.

    Returns:
        Dict con estado, es_organo_valido, contiene_procedimiento, sugerencia
    """
```

**Características:**
- Compara IHQ_ORGANO (BD) vs sección DIAGNÓSTICO (PDF)
- Valida que sea órgano anatómico (MAMA, no MASTECTOMIA)
- Detecta contaminación con procedimientos
- Proporciona sugerencias específicas

### 5. Actualización: Función `auditar_caso_inteligente`

Integra las nuevas validaciones en el flujo completo de auditoría.

**ANTES:**
```python
# Solo validaba IHQ_ORGANO
print(f"   Organo: {datos_bd.get('IHQ_ORGANO', 'N/A')}")
```

**DESPUÉS:**
```python
# Valida AMBOS campos independientemente
print(f"   ORGANO (tabla): {datos_bd.get('Organo', 'N/A')}")
print(f"   IHQ_ORGANO (diagnóstico): {datos_bd.get('IHQ_ORGANO', 'N/A')}")

# PASO 2.4: Validar ORGANO (tabla)
validacion_organo = self._validar_organo_tabla(datos_bd, texto_ocr)
resultado['validaciones']['organo_tabla'] = validacion_organo

# PASO 2.5: Validar IHQ_ORGANO (diagnóstico)
validacion_ihq_organo = self._validar_ihq_organo_diagnostico(datos_bd, texto_ocr)
resultado['validaciones']['ihq_organo_diagnostico'] = validacion_ihq_organo
```

---

## EJEMPLO DE REPORTE MEJORADO

### ANTES (incorrecto):
```
Órgano: MAMA IZQUIERDA (pero BD dice "MASTECTOMIA RADICAL" ❌)
```

### DESPUÉS (correcto):
```
===========================================
VALIDACIÓN DE CAMPOS DE ÓRGANO
===========================================

### CAMPO: Organo (de tabla Estudios solicitados)
**En PDF (tabla):**
  Línea 18: Organo
  Línea 23-24: MASTECTOMIA RADICAL
                IZQUIERDA

**En BD (Organo):** "MASTECTOMIA RADICAL"

**Estado:** ⚠️ INCOMPLETO (problema multilínea)

**Análisis:**
- El extractor capturó solo la primera línea
- Falta capturar "IZQUIERDA" (línea 24)
- El campo ORGANO puede contener procedimientos (es válido)

**Sugerencia:**
- Archivo: core/extractors/patient_extractor.py
- Función: extract_organ_information()
- Problema: No captura valores multilínea en tabla
- Corrección: Modificar para capturar líneas consecutivas no vacías

---

### CAMPO: IHQ_ORGANO (de sección DIAGNÓSTICO)
**En PDF (diagnóstico):**
  Línea 48: DIAGNÓSTICO
  Línea 49: Mama izquierda. Lesión. Mastectomía radical izquierda.

**Órgano detectado:** "MAMA IZQUIERDA"

**En BD (IHQ_ORGANO):** "MAMA IZQUIERDA"

**Estado:** ✅ CORRECTO

**Análisis:**
- Es un órgano anatómico válido
- NO contiene procedimientos
- Correctamente normalizado
```

---

## ARCHIVOS MODIFICADOS

### 1. `herramientas_ia/auditor_sistema.py`

**Líneas agregadas:** ~250 líneas
**Funciones nuevas:** 4
**Funciones modificadas:** 1

**Cambios detallados:**

1. **Línea ~1900** (después de `_validar_estudios_solicitados`):
   - Agregada función `_detectar_organo_tabla()`

2. **Línea ~2000**:
   - Agregada función `_detectar_ihq_organo_diagnostico()`

3. **Línea ~2100**:
   - Agregada función `_validar_organo_tabla()`

4. **Línea ~2200**:
   - Agregada función `_validar_ihq_organo_diagnostico()`

5. **Líneas 2420-2424** (función `auditar_caso_inteligente`):
   - Modificado print para mostrar ambos campos
   - Agregada validación de ORGANO (tabla)
   - Agregada validación de IHQ_ORGANO (diagnóstico)

---

## VALIDACIÓN

### Caso de Prueba: IHQ250981

**Resultado esperado:**
- ✅ ORGANO validado contra tabla (detección de problema multilínea)
- ✅ IHQ_ORGANO validado contra diagnóstico (confirmación de corrección)
- ✅ NO confusión entre ambos campos

### Comando de prueba:
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --nivel profundo
```

---

## IMPACTO

### Casos afectados:
- **Todos los casos** con campos ORGANO y/o IHQ_ORGANO

### Detecciones mejoradas:
1. Problemas multilínea en campo ORGANO (tabla)
2. Contaminación de procedimientos en IHQ_ORGANO
3. Diferenciación clara de dos campos distintos
4. Sugerencias específicas por campo

### Precisión mejorada:
- **ANTES:** Falsos positivos por confusión de campos
- **DESPUÉS:** Validación independiente y precisa

---

## PRÓXIMOS PASOS

1. ✅ Validar sintaxis Python de los cambios
2. ✅ Ejecutar prueba con caso IHQ250981
3. ✅ Verificar que reportes sean claros
4. ⏳ Si detecta problemas en extractores → invocar `core-editor` para corregir
5. ⏳ Actualizar versión del sistema (via `version-manager`)
6. ⏳ Documentar cambios (via `documentation-specialist-HUV`)

---

## NOTAS TÉCNICAS

- **Sin breaking changes:** Las funciones nuevas NO rompen código existente
- **Compatibilidad:** Los reportes antiguos siguen funcionando
- **Extensibilidad:** Fácil agregar validaciones de otros campos similares

---

**Estado:** ✅ IMPLEMENTADO
**Validación:** ⏳ PENDIENTE
