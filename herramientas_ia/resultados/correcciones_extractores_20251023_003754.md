# REPORTE DE CORRECCIONES: Extractores de Diagnóstico

**Fecha:** 2025-10-23 00:37:54
**Caso referencia:** IHQ250981
**Archivo modificado:** `core/extractors/medical_extractor.py`
**Backup creado:** `backups/medical_extractor_backup_20251023_003754.py`

---

## PROBLEMAS DETECTADOS

### 1. DIAGNOSTICO_PRINCIPAL - Contaminación con información del Estudio M

**Valor incorrecto en BD:**
```
CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
```

**Problema:** Incluye "INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)" que pertenece al estudio M (coloración), NO al diagnóstico principal de IHQ.

**Valor correcto esperado:**
```
CARCINOMA MICROPAPILAR
```

**Regla:** DIAGNOSTICO_PRINCIPAL debe contener SOLO el tipo histológico SIN grado Nottingham, invasiones, ni score.

---

### 2. DIAGNOSTICO_COLORACION - Texto contaminado y duplicado

**Valor incorrecto en BD:**
```
de "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)". Previa revisión CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
```

**Problema:**
- Contiene texto basura al inicio ("de")
- Está duplicado (aparece 2 veces el mismo diagnóstico)
- Incluye contexto narrativo de DESCRIPCIÓN MACROSCÓPICA

**Valor correcto esperado:**
```
CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
```

**Regla:** DIAGNOSTICO_COLORACION debe extraerse limpio del texto entre comillas en DESCRIPCIÓN MACROSCÓPICA.

---

## CORRECCIONES APLICADAS

### CORRECCIÓN 1: extract_principal_diagnosis() - Líneas 2061-2087

**Ubicación:** `core/extractors/medical_extractor.py:2061-2087`

**Cambio:** Se agregó limpieza final al diagnóstico principal para eliminar contaminación del estudio M.

**Patrones regex agregados:**

1. **Eliminar grado histológico con score:**
   ```python
   r',?\s*INVASIVO\s+GRADO\s+HISTOL[ÓO]GICO\s*[:\s]+\d+\s*\(SCORE\s+\d+/\d+\)'
   ```
   Ejemplo: "INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)" → eliminado

2. **Eliminar grado Nottingham:**
   ```python
   r',?\s*NOTTINGHAM\s+GRADO\s+\d+'
   r',?\s*GRADO\s+NOTTINGHAM\s+\d+(\s*\(SCORE\s+\d+(/\d+)?\))?'
   ```
   Ejemplo: "NOTTINGHAM GRADO 2", "GRADO NOTTINGHAM 2 (SCORE 7)" → eliminados

3. **Eliminar grado genérico:**
   ```python
   r',?\s*GRADO\s+[I1-3]+(\s*\(SCORE\s+\d+(/\d+)?\))?'
   ```
   Ejemplo: "GRADO 2", "GRADO I (SCORE 3)" → eliminados

4. **Eliminar invasiones:**
   ```python
   r',?\s*INVASI[ÓO]N\s+(LINFOVASCULAR|PERINEURAL)\s*[:\s]+(NEGATIVO|POSITIVO|NO|SI)'
   ```
   Ejemplo: "INVASIÓN LINFOVASCULAR: NEGATIVO" → eliminado

5. **Eliminar score aislado:**
   ```python
   r',?\s*SCORE\s+\d+(/\d+)?'
   ```

6. **Limpieza de comas/espacios:**
   - Comas duplicadas: `\s*,\s*,\s*` → `, `
   - Comas al inicio/fin: `^,\s*|\s*,$` → eliminadas
   - Espacios múltiples: `\s{2,}` → ` `

**Ejemplo de transformación:**
```
ANTES: CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
DESPUÉS: CARCINOMA MICROPAPILAR
```

---

### CORRECCIÓN 2: extract_diagnostico_coloracion() - Líneas 297-312

**Ubicación:** `core/extractors/medical_extractor.py:297-312`

**Cambio:** Se mejoró la limpieza del texto inicial para eliminar contexto narrativo y duplicación.

**Patrones regex mejorados:**

1. **Eliminar duplicación completa:**
   ```python
   r'^de\s+"([^"]+)"\.\s*Previa\s+revisi[óo]n\s+\1'
   ```
   Ejemplo: 'de "DIAG". Previa revisión DIAG' → 'DIAG'

2. **Eliminar contexto con punto:**
   ```python
   r'^de\s+"([^"]+)"\.\s*'
   ```
   Ejemplo: 'de "DIAG". ' → 'DIAG. '

3. **Eliminar contexto sin punto:**
   ```python
   r'^de\s+"([^"]+)"'
   ```
   Ejemplo: 'de "DIAG"' → 'DIAG'

4. **Normalizar espacios:**
   ```python
   r'\s{2,}' → ' '
   ```

**Ejemplo de transformación:**
```
ANTES: de "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)". Previa revisión CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
DESPUÉS: CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
```

---

## VALIDACIÓN

**Sintaxis Python:** ✅ VALIDADO - Sin errores

**Backup creado:** ✅ `backups/medical_extractor_backup_20251023_003754.py`

---

## IMPACTO ESTIMADO

**Casos afectados potencialmente:**
- Todos los casos donde DIAGNOSTICO_PRINCIPAL contiene grado Nottingham o score
- Todos los casos donde DIAGNOSTICO_COLORACION tiene duplicación

**Campos modificados:**
- `DIAGNOSTICO_PRINCIPAL` (extract_principal_diagnosis)
- `DIAGNOSTICO_COLORACION` (extract_diagnostico_coloracion)

**Severidad:** ALTA - Estos campos son críticos para validación de casos

---

## PRÓXIMOS PASOS

1. **REPROCESAR caso IHQ250981** para verificar correcciones:
   ```bash
   python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente
   ```

2. **VALIDAR resultado esperado:**
   - DIAGNOSTICO_PRINCIPAL: "CARCINOMA MICROPAPILAR"
   - DIAGNOSTICO_COLORACION: "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)"

3. **AUDITAR casos procesados** para verificar que no se introdujeron regresiones:
   ```bash
   python herramientas_ia/auditor_sistema.py --rango IHQ250980-IHQ251000
   ```

4. **ACTUALIZAR versión del sistema** si las correcciones son exitosas:
   ```bash
   python herramientas_ia/gestor_version.py --version v6.0.3
   ```

---

## CAMBIOS EN CÓDIGO

**Archivo:** `core/extractors/medical_extractor.py`
**Líneas modificadas:**
- 2061-2087 (extract_principal_diagnosis - limpieza final)
- 297-312 (extract_diagnostico_coloracion - limpieza inicial)

**Total líneas agregadas:** 35
**Total líneas modificadas:** 12

---

## AUTOR

**Generado por:** core-editor (EVARISIS)
**Responsable:** Claude Code
**Fecha:** 2025-10-23 00:37:54
**Versión sistema:** 6.0.2 → 6.0.3 (pendiente)
