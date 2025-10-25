# FUNCIONES EXACTAS A MODIFICAR - IHQ250984

**Fecha**: 24/10/2025 07:55:40
**Versión objetivo**: v6.0.11
**Total de archivos**: 2
**Total de funciones**: 2

---

## ARCHIVO 1: core/extractors/biomarker_extractor.py

### Función 1: extract_biomarkers()

**Ubicación**: Línea **1137**

**Signatura**:
```python
def extract_biomarkers(text: str) -> Dict[str, str]:
```

**Prioridad**: CRÍTICA ⚠️

**Problema**:
La función pasa `text` sin filtrar a funciones internas, permitiendo que capturen texto de la sección técnica "Anticuerpos:" en lugar de "REPORTE DE BIOMARCADORES:".

**Solución**:
Agregar filtrado de texto ANTES de línea 1150 (antes de `results = {}`).

**Código a insertar** (después de línea 1148 `if not text: return {}`):

```python
    # ═══════════════════════════════════════════════════════════════════════
    # V6.0.11: FILTRO CRÍTICO - Eliminar sección "Anticuerpos:" (IHQ250984)
    # ═══════════════════════════════════════════════════════════════════════
    text_filtered = text

    # ESTRATEGIA 1: Eliminar sección técnica
    text_filtered = re.sub(
        r'Anticuerpos?:\s*.*?(?=DESCRIPCI[ÓO]N|REPORTE|DIAGN[ÓO]STICO|$)',
        '',
        text_filtered,
        flags=re.IGNORECASE | re.DOTALL
    )

    # ESTRATEGIA 2: Priorizar bloque "REPORTE DE BIOMARCADORES:"
    match_reporte = re.search(
        r'REPORTE\s+DE\s+BIOMARCADORES?:\s*(.+?)(?=DIAGN[ÓO]STICO\s+FINAL|CONCLUSI[ÓO]N|$)',
        text_filtered,
        re.IGNORECASE | re.DOTALL
    )

    priority_text = match_reporte.group(1) if match_reporte else text_filtered
```

**Cambios adicionales en la función**:

| Línea aproximada | Cambio | De | A |
|------------------|--------|-----|-----|
| 1154 | Usar texto filtrado | `extract_molecular_expression_section(text)` | `extract_molecular_expression_section(text_filtered)` |
| 1157 | Usar texto filtrado | `extract_report_section(text)` | `extract_report_section(text_filtered)` |
| 1174 | Usar texto prioritario | `extract_narrative_biomarkers(text)` | `extract_narrative_biomarkers(priority_text)` |
| 1194 | Usar texto prioritario | `extract_single_biomarker(text, ...)` | `extract_single_biomarker(priority_text, ...)` |

**Total de líneas nuevas**: ~30 líneas
**Total de líneas modificadas**: 4 líneas

---

### Función 2: extract_narrative_biomarkers()

**Ubicación**: Línea **1203**

**Signatura**:
```python
def extract_narrative_biomarkers(text: str) -> Dict[str, str]:
```

**Prioridad**: ALTA

**Problema**:
Patrones insuficientes para capturar variantes de GATA3 y SOX10.

**Solución**:
Agregar patrones adicionales en lista `complex_patterns` (líneas 1210-1236).

**Código a insertar** (después de línea 1219, después de patrones existentes de GATA3/SOX10):

```python
    # V6.0.11: PATRONES ADICIONALES para GATA3 y SOX10 (IHQ250984)
    r'(?i)positivas?\s+(?:fuerte\s+y\s+)?difusa\s+para\s+GATA\s*-?\s*3',
    r'(?i)tienen\s+una\s+tinción\s+nuclear\s+positiva\s+.*?para\s+GATA\s*-?\s*3',
    r'(?i)son\s+negativas?\s+para\s+S[OX]{2,3}\s*-?\s*10',  # Variante con "son"
```

**Total de líneas nuevas**: 3 líneas

---

## ARCHIVO 2: core/extractors/medical_extractor.py

### Función 3: extract_factor_pronostico()

**Ubicación**: Línea **465**

**Signatura**:
```python
def extract_factor_pronostico(diagnostico_completo: str, ihq_estudios_solicitados: str = "",
                               nombre_paciente: str = "") -> str:
```

**Prioridad**: MEDIA

**Problema**:
Patrón no captura correctamente biomarcadores con paréntesis (ej: "HER 2: Positivo (Score 3+)").

**Solución**:
Modificar patrón en línea 513.

**Código a modificar** (línea 513):

**ANTES**:
```python
    patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-]+:.*?\n?)+)'
```

**DESPUÉS**:
```python
    # V6.0.11: MEJORADO - Captura paréntesis en biomarcadores (IHQ250984)
    patron_bloque_estructurado = r'(?:REPORTE\s+DE\s+BIOMARCADORES?|BIOMARCADORES?)\s*:?\s*\n\n?((?:-[A-ZÁÉÍÓÚÑ\s0-9/\-()]+:.*?\n?)+)'
```

**Cambio**: Agregar `()` al patrón de caracteres permitidos.

**Total de líneas modificadas**: 1 línea

---

## RESUMEN CONSOLIDADO

### Archivos a modificar
1. `core/extractors/biomarker_extractor.py`
2. `core/extractors/medical_extractor.py`

### Funciones a modificar
1. `extract_biomarkers()` (línea 1137) - biomarker_extractor.py
2. `extract_narrative_biomarkers()` (línea 1203) - biomarker_extractor.py
3. `extract_factor_pronostico()` (línea 465) - medical_extractor.py

### Estadísticas de cambios

| Archivo | Funciones | Líneas nuevas | Líneas modificadas | Total cambios |
|---------|-----------|---------------|-------------------|---------------|
| biomarker_extractor.py | 2 | 33 | 4 | 37 |
| medical_extractor.py | 1 | 0 | 1 | 1 |
| **TOTAL** | **3** | **33** | **5** | **38** |

---

## PASOS PARA APLICAR MANUALMENTE

### Opción 1: Usar Edit tool de Claude (RECOMENDADO)

```
1. Claude lee archivo biomarker_extractor.py
2. Claude usa Edit tool para modificar extract_biomarkers()
3. Claude usa Edit tool para modificar extract_narrative_biomarkers()
4. Claude lee archivo medical_extractor.py
5. Claude usa Edit tool para modificar extract_factor_pronostico()
6. Claude valida sintaxis con editor_core.py --validar-sintaxis
```

### Opción 2: Editar manualmente con editor

```
1. Abrir core/extractors/biomarker_extractor.py
2. Ir a línea 1148 (después de "if not text: return {}")
3. Insertar código de filtrado (ver arriba)
4. Modificar líneas 1154, 1157, 1174, 1194 (cambiar "text" por "text_filtered" o "priority_text")
5. Ir a línea 1219 (dentro de lista complex_patterns)
6. Insertar 3 patrones adicionales
7. Guardar y cerrar

8. Abrir core/extractors/medical_extractor.py
9. Ir a línea 513
10. Modificar patrón (agregar "()" a caracteres permitidos)
11. Guardar y cerrar

12. Validar sintaxis:
    python herramientas_ia/editor_core.py --validar-sintaxis biomarker_extractor.py
    python herramientas_ia/editor_core.py --validar-sintaxis medical_extractor.py
```

### Opción 3: Usar script automatizado (FUTURO)

```bash
# Comando futuro (no implementado aún)
python herramientas_ia/editor_core.py --aplicar-correcciones --simulacion-id 20251024_075540
```

---

## BACKUPS AUTOMÁTICOS

Antes de modificar, se crearán backups automáticos en:

```
backups/biomarker_extractor_backup_YYYYMMDD_HHMMSS.py
backups/medical_extractor_backup_YYYYMMDD_HHMMSS.py
```

**IMPORTANTE**: Estos backups se crean automáticamente cuando usas editor_core.py o cuando Claude modifica archivos.

---

## VALIDACIÓN POST-APLICACIÓN

### 1. Validar sintaxis
```bash
python herramientas_ia/editor_core.py --validar-sintaxis biomarker_extractor.py
python herramientas_ia/editor_core.py --validar-sintaxis medical_extractor.py
```

### 2. Reprocesar caso crítico
```bash
python herramientas_ia/editor_core.py --reprocesar IHQ250984
```

### 3. Auditar resultado
```bash
python herramientas_ia/auditor_sistema.py IHQ250984 --inteligente
```

### 4. Verificar casos de regresión
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente  # v6.0.2
python herramientas_ia/auditor_sistema.py IHQ250983 --inteligente  # v6.0.5
```

---

## RESULTADO ESPERADO

Después de aplicar las correcciones y reprocesar IHQ250984:

```
ANTES:
  IHQ_RECEPTOR_ESTROGENOS: ") (SP1) RABBIT MONOCLONAL PRIMARY ANTIBODY" ❌
  IHQ_HER2: "/NEU: PATHWAY ANTI-HER-2/NEU (4B5) RABBIT..." ❌
  IHQ_SOX10: NULL ❌

DESPUÉS:
  IHQ_RECEPTOR_ESTROGENOS: "NEGATIVO" ✅
  IHQ_HER2: "POSITIVO (SCORE 3+)" ✅
  IHQ_SOX10: "NEGATIVO" ✅

Score: 33% → 100% (+67 puntos)
```

---

**Generado por**: core-editor (agent)
**Herramienta**: editor_core.py (simulación)
**Archivos relacionados**:
- SIMULACION_correcciones_extractores_IHQ250984_20251024_075540.md (reporte completo)
- CODIGO_PROPUESTO_extract_biomarkers_v6.0.11.py (código completo)
- CODIGO_PROPUESTO_patrones_mejorados_v6.0.11.py (patrones completos)
- RESUMEN_EJECUTIVO_simulacion_IHQ250984.md (resumen ejecutivo)
