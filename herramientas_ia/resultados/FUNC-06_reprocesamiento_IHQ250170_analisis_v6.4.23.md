# REPORTE FUNC-06: Reprocesamiento IHQ250170 v6.4.23

## INFORMACIÓN DEL CASO
- **Caso**: IHQ250170
- **Timestamp**: 2026-01-08 04:44:14
- **Score final**: 88.9%
- **Estado**: OK (con 2 biomarcadores sin mapear)

---

## CORRECCIONES APLICADAS

### 1. Agregados Aliases de CK → CKAE1AE3 ✅
**Archivo**: `core/extractors/biomarker_extractor.py` (líneas 6145-6150)

```python
# V6.4.23 FIX IHQ250170: Agregar aliases CK → CKAE1AE3
'CK AE1/AE2': 'CKAE1AE3',
'AE1AE2': 'CKAE1AE3',
'AE1/AE2': 'CKAE1AE3',
'CK': 'CKAE1AE3',
```

### 2. Patrón Parentético Corregido ✅
**Archivo**: `core/extractors/biomarker_extractor.py` (líneas 4070-4073)

```python
# V6.4.23 FIX IHQ250170: Patrón parentético ahora procesa "S100-"
elif val_clean.endswith('-'):
    val_clean = 'NEGATIVO'
    self.logger.info(f"✅ [Parentético+/-] '{bio}' → {bio_clean} = {val_clean}")
```

---

## RESULTADOS DE VALIDACIÓN

### Biomarcadores Solicitados (IHQ_ESTUDIOS_SOLICITADOS) ✅
```
CK, AE1AE2, EMA, Receptor de Progesterona, Ki-67, VIMENTINA, S100
```
- **Estado**: Todos detectados correctamente

### Biomarcadores Extraídos

| Biomarcador | Columna | Valor BD | Valor OCR | Estado |
|-------------|---------|----------|-----------|--------|
| **Ki-67** | IHQ_KI-67 | POSITIVO | "Ki67" | ✅ OK |
| **VIMENTINA** | IHQ_VIMENTINA | POSITIVO | "vimentina +" | ⚠️ WARNING* |
| **S100** | IHQ_S100 | NEGATIVO | "S100-" | ✅ OK (CORRECCIÓN APLICADA) |
| **EMA** | IHQ_EMA | N/A | "EMA ... negativos" | ❌ NO EXTRAÍDO |
| **Receptor de Progesterona** | IHQ_RECEPTOR_PROGESTERONA | N/A | "progesterona negativos" | ❌ NO EXTRAÍDO |
| **CK** | - | Sin columna | "CK AE1/AE2" | ⚠️ NO MAPEADO |
| **AE1AE2** | - | Sin columna | "AE1/AE3" | ⚠️ NO MAPEADO |

*WARNING VIMENTINA: El auditor reporta "valor_bd POSITIVO vs valor_ocr +" - Esto es correcto, solo diferencia de formato.

---

## ANÁLISIS DEL PROBLEMA PRINCIPAL

### Contexto en el PDF

**Línea 29 (Solicitud):**
```
siguientes marcadores: CK AE1/AE2 , EMA , progesterona , Ki67 , vimentina , S100.
```

**Línea 34 (Resultado):**
```
En la muestra evaluada no se reconocen meninges, EMA, AE1/AE3, progesterona negativos.
```

**Línea 36 (Resultado adicional):**
```
observa tejido fibroconectivo denso ... (vimentina +, S100-)
```

### ¿Por qué CK y AE1AE2 NO se extrajeron?

1. **Problema de nomenclatura inconsistente**:
   - **Solicitado**: `CK AE1/AE2` (dos nombres juntos)
   - **Resultado**: `AE1/AE3` (nota: dice AE**3**, no AE2)
   - El alias agregado es `'AE1/AE2': 'CKAE1AE3'` pero el PDF dice `AE1/AE3`

2. **El patrón de extracción narrativo busca**:
   ```python
   r'(?i)AE1/AE2\s*:\s*(POSITIVO|NEGATIVO|...)'
   ```
   Pero el texto dice:
   ```
   EMA, AE1/AE3, progesterona negativos
   ```
   (Sin ":", estado al final de la lista)

3. **Formato de lista compacta**:
   ```
   EMA, AE1/AE3, progesterona negativos
   ```
   El sistema debe interpretar que "negativos" aplica a los 3 biomarcadores de la lista.

---

## CORRECCIONES PENDIENTES

### CRÍTICA: Agregar Alias AE1/AE3 → CKAE1AE3

**Archivo**: `core/extractors/biomarker_extractor.py`
**Línea**: ~6145

```python
# V6.4.24 FIX IHQ250170: Agregar alias AE1/AE3 (el PDF usa AE3, no AE2)
'AE1/AE3': 'CKAE1AE3',
```

### CRÍTICA: Patrón de Lista Compacta con Estado Final

**Archivo**: `core/extractors/biomarker_extractor.py`
**Función**: `extract_biomarkers_compacto()`
**Línea**: ~3920

Agregar patrón para capturar:
```
EMA, AE1/AE3, progesterona negativos
```

**Patrón sugerido**:
```python
# V6.4.24 FIX IHQ250170: Patrón lista compacta con estado final
# Ejemplo: "EMA, AE1/AE3, progesterona negativos"
pattern = r'(?i)([A-Z0-9/]+(?:\s*,\s*[A-Z0-9/]+)*)\s+(POSITIVO|NEGATIVO|POSITIVOS|NEGATIVOS)'

for match in re.finditer(pattern, text):
    bio_list = match.group(1)  # "EMA, AE1/AE3, progesterona"
    estado = match.group(2)    # "negativos"
    
    # Dividir la lista y asignar el mismo estado a todos
    for bio in bio_list.split(','):
        bio_clean = bio.strip()
        # Mapear y guardar con estado NEGATIVO
```

---

## VALIDACIÓN DE CORRECCIÓN S100 ✅

### ANTES (v6.4.22 y anteriores):
```python
# Patrón parentético descartaba "S100-" por el guión final
elif val_clean.endswith('+'):
    val_clean = 'POSITIVO'
# NO había elif para '-'
```

### DESPUÉS (v6.4.23):
```python
# Patrón parentético procesa "S100-" correctamente
elif val_clean.endswith('-'):
    val_clean = 'NEGATIVO'
    self.logger.info(f"✅ [Parentético+/-] '{bio}' → {bio_clean} = {val_clean}")
```

### Resultado:
- **IHQ_S100**: ✅ NEGATIVO (extraído correctamente)
- **Contexto OCR**: `S100-` → interpretado como NEGATIVO

---

## VALIDACIÓN DE ALIAS CK ⚠️ PARCIAL

### ANTES (v6.4.22 y anteriores):
- No había alias `'CK': 'CKAE1AE3'`
- El biomarcador "CK" no se mapeaba a ninguna columna

### DESPUÉS (v6.4.23):
- ✅ Alias agregado: `'CK': 'CKAE1AE3'`
- ⚠️ PERO: El biomarcador NO se extrajo porque:
  1. El PDF usa `AE1/AE3` en el resultado (no `AE1/AE2`)
  2. No hay patrón para listas compactas tipo "EMA, AE1/AE3, progesterona negativos"

---

## PRÓXIMOS PASOS RECOMENDADOS

### 1. Agregar Alias Faltante (CRÍTICO)
```bash
# Editar biomarker_extractor.py línea ~6145
'AE1/AE3': 'CKAE1AE3',
```

### 2. Implementar Patrón de Lista Compacta (CRÍTICO)
- Crear patrón para `"bio1, bio2, bio3 ESTADO"`
- Aplicar ESTADO a todos los biomarcadores de la lista
- Usar en `extract_biomarkers_compacto()`

### 3. Validar con Casos de Referencia (OBLIGATORIO)
- IHQ250170 (caso actual)
- Buscar otros casos con formato similar de lista compacta
- Ejecutar FUNC-01 en casos de referencia ANTES/DESPUÉS del cambio

### 4. Reprocesar IHQ250170 (Después de correcciones)
```bash
python -c "
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
auditor.reprocesar_caso_completo('IHQ250170')
"
```

---

## MÉTRICAS FINALES

| Métrica | Valor | Objetivo |
|---------|-------|----------|
| **Score de Validación** | 88.9% | 100% |
| **Campos Validados** | 8/9 | 9/9 |
| **Biomarcadores Mapeados** | 5/7 | 7/7 |
| **Biomarcadores No Mapeados** | 2 (CK, AE1AE2) | 0 |
| **Biomarcadores con Valores** | 3/7 (43%) | 7/7 (100%) |

---

## CONCLUSIÓN

### Correcciones Aplicadas con Éxito ✅
1. **S100**: Ahora se extrae como NEGATIVO (patrón parentético `S100-` funciona)
2. **Alias CK agregados**: Listos para mapear a CKAE1AE3

### Correcciones Pendientes ⚠️
1. **Alias AE1/AE3 faltante**: El PDF usa AE3, no AE2
2. **Patrón de lista compacta**: No existe patrón para "bio1, bio2, bio3 ESTADO"
3. **EMA y Progesterona**: No se extraen (mismo problema de lista compacta)

### Impacto de Correcciones Adicionales
Si se aplican las correcciones pendientes, el score esperado es:
- **Score actual**: 88.9% (8/9 validaciones OK)
- **Score esperado**: 100% (9/9 validaciones OK, todos biomarcadores extraídos)

---

**Generado por**: FUNC-06 (data-auditor v6.4.23)
**Fecha**: 2026-01-08 04:44:14
**Caso**: IHQ250170
