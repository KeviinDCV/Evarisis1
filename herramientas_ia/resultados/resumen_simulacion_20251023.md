# RESUMEN VISUAL - CAMBIOS PROPUESTOS EN EXTRACTORES

**Modo:** SIMULACIÓN (Dry-run)
**Fecha:** 2025-10-23
**Estado:** PENDIENTE DE APROBACIÓN

---

## CAMBIO 1: DIAGNOSTICO_COLORACION

### Archivo
`core/extractors/medical_extractor.py`

### Línea modificada
**Línea 320**

### ANTES
```python
patron_citado = r'diagn[óo]stico\s+de?\s*["\']([^"\']+)["\']'
```

### DESPUÉS
```python
# v6.0.3: CORREGIDO - Capturar TODO el contenido entre comillas incluyendo comillas Unicode
patron_citado = r'diagn[óo]stico\s+de\s*[""\"\'"]([^""\"\']+)[""\"\'"]'
```

### Qué mejora
- Reconoce comillas tipográficas Unicode (`""`) usadas en PDFs
- Captura diagnóstico completo sin truncamiento
- Extrae correctamente: `CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)`

---

## CAMBIO 2: ORGANO MULTILÍNEA

### Archivo
`core/extractors/patient_extractor.py`

### Líneas modificadas
**Líneas 234-235**

### ANTES
```python
# V6.0.0: Patrón 1 - Captura multilínea completa (ej: "MASTECTOMIA RADICAL\nIZQUIERDA")
r'(?:Bloques y laminas|Tejido en fresco|Organo:)\s+([A-ZÁÉÍÓÚÑ][^\n]*)\n\s+([A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s0-9]+?)(?=\s*(?:\n|INFORME|DESCRIPCI))',
```

### DESPUÉS
```python
# V6.0.3: CORREGIDO - Capturar TODAS las líneas después de "Organo:" hasta siguiente campo
r'(?:Bloques y laminas|Tejido en fresco|Organo:)\s+((?:[A-ZÁÉÍÓÚÑ0-9][^\n]*(?:\n|$))+?)(?=\s*(?:INFORME|DESCRIPCI|Estudios\s+solicitados))',
```

### Qué mejora
- Captura TODAS las líneas (no solo 2)
- Extrae correctamente: `ESTUDIO DE 898807 Estudio anatomopatologico de marcacion MASTECTOMIA RADICAL`
- Compatible con casos existentes (1 o 2 líneas)

---

## CASO DE PRUEBA: IHQ250981

### Campo: DIAGNOSTICO_COLORACION

**Valor en PDF:**
```
y con diagnóstico de "CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)"
```

**Extracción ACTUAL:**
```
CARCINOMA MICROPAPILAR (truncado)
```

**Extracción ESPERADA después del cambio:**
```
CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9) ✓
```

---

### Campo: ORGANO

**Valor en PDF (multilínea):**
```
Organo:
ESTUDIO DE
898807 Estudio anatomopatologico de marcacion
MASTECTOMIA RADICAL
```

**Extracción ACTUAL:**
```
MASTECTOMIA RADICAL (solo última línea)
```

**Extracción ESPERADA después del cambio:**
```
ESTUDIO DE 898807 Estudio anatomopatologico de marcacion MASTECTOMIA RADICAL ✓
```

---

## RIESGO DE CAMBIOS

| Cambio | Riesgo | Justificación |
|--------|--------|---------------|
| DIAGNOSTICO_COLORACION | **BAJO** | Solo amplía tipos de comillas reconocidas, sin afectar lógica |
| ORGANO multilínea | **BAJO-MEDIO** | Mejora captura sin romper casos existentes, pero requiere validación |

---

## VALIDACIÓN RECOMENDADA

Después de aplicar cambios, ejecutar:

```bash
# 1. Validar sintaxis
python -m py_compile core/extractors/medical_extractor.py
python -m py_compile core/extractors/patient_extractor.py

# 2. Reprocesar caso crítico IHQ250981
python core/unified_extractor.py --reprocesar IHQ250981

# 3. Auditar caso
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente

# 4. Verificar campos específicos
python herramientas_ia/gestor_base_datos.py --buscar IHQ250981 --mostrar-completo
```

---

## BACKUPS AUTOMÁTICOS

Se crearán automáticamente antes de aplicar:

```
backups/medical_extractor_backup_20251023_HHMMSS.py
backups/patient_extractor_backup_20251023_HHMMSS.py
```

---

## DECISIÓN REQUERIDA

¿Desea aplicar estos cambios?

- **SÍ:** Aplicaré los cambios, crearé backups, validaré sintaxis y reprocesaré IHQ250981
- **NO:** Cancelaré la operación sin modificar archivos
- **REVISAR:** Puedo mostrar más detalles o ajustar los cambios

---

**Esperando su aprobación...**
