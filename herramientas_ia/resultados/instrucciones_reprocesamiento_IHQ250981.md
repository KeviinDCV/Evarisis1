# INSTRUCCIONES DE REPROCESAMIENTO - CASO IHQ250981

**Fecha**: 2025-10-22
**Agente**: core-editor (EVARISIS)
**Objetivo**: Verificar que las correcciones implementadas funcionen en el caso IHQ250981

---

## HALLAZGO CRÍTICO

**TODAS las correcciones solicitadas YA ESTÁN IMPLEMENTADAS** en el código actual (v6.0.1):

1. ✅ E-Cadherina normalizada correctamente (`medical_extractor.py` líneas 879-881)
2. ✅ DIAGNOSTICO_PRINCIPAL incluye grado histológico (sin filtros activos)
3. ✅ Biomarcadores priorizan "Expresión molecular" (`biomarker_extractor.py` líneas 1009-1073)

**Por lo tanto, NO se requiere modificar código.**

---

## ACCIÓN NECESARIA

El caso IHQ250981 **debe ser reprocesado** con la versión actual del código para aplicar las correcciones.

---

## PROCEDIMIENTO DE REPROCESAMIENTO

### PASO 1: Verificar versión del sistema

```bash
cd "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV9GESTOR_ONCOLOGIA"
python -c "from config.version_info import VERSION_INFO; print(f'Versión: {VERSION_INFO[\"version\"]}')"
```

**Versión esperada**: 6.0.1 o superior

---

### PASO 2: Leer OCR del PDF (pre-validación)

```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --leer-ocr
```

**Verificar que el texto contenga**:
- "se realizan niveles histológicos para tinción con: E-Cadherina, Progesterona, Estrógenos, Her2, Ki67"
- "Expresión molecular:"
- "RECEPTORES DE ESTRÓGENOS: POSITIVOS (90-100%)."
- "RECEPTORES DE PROGESTERONA: NEGATIVOS (MENOR AL 1 %)."
- "SOBREEXPRESIÓN DE HER-2: EQUIVOCO (SCORE 2+)."

---

### PASO 3: Reprocesar caso IHQ250981

#### Opción A: Usando unified_extractor.py

```bash
python core/unified_extractor.py --reprocesar IHQ250981
```

#### Opción B: Usando procesador principal

```bash
python main.py --reprocesar IHQ250981
```

#### Opción C: Si tienes función de reprocesamiento en core-editor

```bash
python herramientas_ia/editor_core.py --reprocesar IHQ250981 --validar-antes
```

---

### PASO 4: Auditar resultado (post-validación)

```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --nivel profundo
```

---

## RESULTADOS ESPERADOS POST-REPROCESAMIENTO

### IHQ_ESTUDIOS_SOLICITADOS
**Antes** (incorrecto):
```
HER2, Ki-67, Receptor de Estrógeno, Receptor de Progesterona
```

**Después** (correcto):
```
E-Cadherina, HER2, Ki-67, Receptor de Estrógeno, Receptor de Progesterona
```

---

### DIAGNOSTICO_PRINCIPAL
**Antes** (si estaba incorrecto):
```
CARCINOMA MICROPAPILAR, INVASIVO
```

**Después** (correcto):
```
CARCINOMA MICROPAPILAR, INVASIVO GRADO HISTOLOGICO: 1 (SCORE 3/9)
```

**Nota**: Si ya estaba completo, NO debería cambiar.

---

### BIOMARCADORES (ER, PR, HER2)

#### IHQ_RECEPTOR_ESTROGENO
**Antes** (si era de DESCRIPCIÓN MICROSCÓPICA):
```
Valor incorrecto o incompleto
```

**Después** (de "Expresión molecular"):
```
POSITIVOS (90-100%)
```

#### IHQ_RECEPTOR_PROGESTERONA
**Antes**:
```
Valor incorrecto o incompleto
```

**Después**:
```
NEGATIVOS (MENOR AL 1 %)
```

#### IHQ_HER2
**Antes**:
```
Valor incorrecto o incompleto
```

**Después**:
```
EQUIVOCO (SCORE 2+)
```

---

## VALIDACIÓN FINAL

Ejecutar auditoría completa para confirmar:

```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --buscar "E-Cadherina" --buscar "Expresión molecular" --buscar "grado"
```

**Métricas esperadas**:
- **Completitud de estudios solicitados**: 100% (5/5 biomarcadores capturados)
- **Precisión de biomarcadores**: 100% (ER, PR, HER2 correctos desde "Expresión molecular")
- **Precisión de diagnóstico**: 100% (incluye grado histológico completo)

---

## TROUBLESHOOTING

### Problema 1: E-Cadherina sigue sin capturarse

**Diagnóstico**:
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --leer-ocr | grep -i "cadherina"
```

**Posibles causas**:
- El PDF usa variante no contemplada (ej: "E- Cadherina" con espacio extra)
- El texto está en sección distinta (no en DESCRIPCIÓN MACROSCÓPICA)

**Solución**: Agregar variante específica a `normalize_biomarker_name_simple()`

---

### Problema 2: Biomarcadores no vienen de "Expresión molecular"

**Diagnóstico**:
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --leer-ocr | grep -A10 "Expresión molecular"
```

**Posibles causas**:
- El PDF usa variante "Expresion molecular" (sin tilde)
- La sección se llama diferente (ej: "Perfil molecular")

**Solución**: Verificar patrón en `buscar_en_diagnostico()` línea 1028:
```python
inicio=r"DIAGN[ÓO]STICO|EXPRESI[ÓO]N\s+MOLECULAR",
```

---

### Problema 3: Grado histológico no se incluye en diagnóstico

**Diagnóstico**:
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --buscar "grado" --buscar "score"
```

**Posibles causas**:
- El patrón de extracción no coincide con la estructura del PDF
- Hay filtros activos no detectados

**Solución**: Revisar función `extract_principal_diagnosis()` línea 1879

---

## CONTACTO

Si después de reprocesar el caso IHQ250981 **persisten errores**:

1. Generar reporte completo:
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --nivel profundo > reporte_IHQ250981_post_reproceso.txt
```

2. Compartir con desarrolladores:
   - `reporte_IHQ250981_post_reproceso.txt`
   - `herramientas_ia/resultados/analisis_correcciones_IHQ250981_20251022_162759.md`
   - `data/debug_maps/debug_map_IHQ250981_*.json` (si existe)

3. Considerar ajustes específicos de patrones regex para este caso particular.

---

**Generado por**: core-editor (EVARISIS)
**Versión**: 1.0.0
**Fecha**: 2025-10-22
