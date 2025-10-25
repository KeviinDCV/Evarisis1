# 🔍 DIAGNÓSTICO COMPLETO - PROBLEMA DE MAPEO EN BASE DE DATOS

**Fecha**: 5 de octubre de 2025  
**Versión Sistema**: 4.2.0  
**Analista**: GitHub Copilot  
**Severidad**: ALTA ⚠️

---

## 📊 RESUMEN EJECUTIVO

Se identificó un problema crítico de mapeo entre la extracción de datos y la base de datos que afecta al **38% de los casos (19 de 50)**. Los datos diagnósticos SÍ se extraen correctamente del PDF pero NO se mapean correctamente a la columna `Diagnostico Principal` en la base de datos.

### Impacto
- **19 casos** (38%) sin diagnóstico principal en BD
- **De esos 19 casos, 15 casos** (79%) SÍ tienen información diagnóstica válida que NO se mapeó
- **Datos extraídos**: ✅ Correctos
- **Mapeo a BD**: ❌ Fallando

---

## 🎯 CASOS AFECTADOS

### Casos CON información diagnóstica NO mapeada (15/19):

1. **IHQ250005**: ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO
2. **IHQ250006**: ADENOCARCINOMA INVASIVO MODERADAMENTE DIFERENCIADO
3. **IHQ250016**: CARCINOMA ESCAMOCELULAR INVASIVO QUERATINIZANTE
4. **IHQ250025**: ADENOCARCINOMA INVASIVO PULMONAR
5. **IHQ250027**: TUMOR NEUROENDOCRINO
6. **IHQ250028**: ADENOCARCINOMA INVASIVO DE COLON
7. **IHQ250036**: ADENOCARCINOMA PULMONAR
8. **IHQ250037**: CARCINOMA INVASIVO NO ESPECIAL (DUCTAL)
9. **IHQ250039**: ADENOCARCINOMA MUCINOSO DEL ESTOMAGO
10. **IHQ250040**: ADENOCARCINOMA PULMONAR
11. **IHQ250041**: CARCINOMA PULMONAR DE CELULAS PEQUEÑAS
12. **IHQ250042**: SARCOMA FUSOCELULAR
13. **IHQ250043**: COMPATIBLE CON ESCLEROSIS HIPOCAMPAL
14. **IHQ250044**: CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL)
15. **IHQ250046**: ADENOCARCINOMA MUCINOSO

### Casos SIN información diagnóstica (4/19):
- IHQ250017, IHQ250019, IHQ250021, IHQ250048

---

## 🔍 ANÁLISIS TÉCNICO DEL PROBLEMA

### Flujo de Extracción Actual

```
PDF → OCR → unified_extractor.extract_ihq_data() 
           ↓
           medical_extractor.extract_medical_data()
           ↓ 
           results['diagnostico_final_ihq'] = "ADENOCARCINOMA..."
           ↓
           unified_extractor.map_to_database_format()
           ↓
           ❌ PROBLEMA AQUÍ ❌
           ↓
           db_record["Diagnostico Principal"] = extract_principal_diagnosis(diagnostico_completo)
           ↓
           BD: "N/A" 
```

### Causa Raíz Identificada

El problema está en `core/unified_extractor.py` líneas **751-757**:

```python
# LÍNEA 751
diagnostico_completo = extracted_data.get('diagnostico', 'N/A')

# LÍNEA 754
diagnostico_principal = extract_principal_diagnosis(diagnostico_completo) if diagnostico_completo and diagnostico_completo != 'N/A' else 'N/A'

# LÍNEA 756
db_record["Diagnostico Principal"] = diagnostico_principal
```

**Problema**: Se busca `'diagnostico'` pero `medical_extractor.py` guarda en `'diagnostico_final_ihq'` y luego se mapea a `'diagnostico_final'`.

### Mapeo de Campos (Cascada de Transformaciones)

1. **medical_extractor.py** línea 335:
   ```python
   results['diagnostico_final_ihq'] = diagnostico_extraido
   ```

2. **medical_extractor.py** línea 348-349:
   ```python
   'diagnostico_final_ihq': 'diagnostico_final'
   results['diagnostico_final'] = results['diagnostico_final_ihq']
   ```

3. **unified_extractor.py** línea 179:
   ```python
   combined_data['diagnostico'] = medical_data.get('diagnostico_final', '') or medical_data.get('diagnostico_final_ihq', '')
   ```

4. **unified_extractor.py** línea 751 (❌ ERROR):
   ```python
   diagnostico_completo = extracted_data.get('diagnostico', 'N/A')
   ```

**El campo existe en `extracted_data['diagnostico']` PERO puede estar vacío si el patrón `DIAGNOSTICO:` no se detectó en el PDF.**

---

## 💡 SOLUCIONES PROPUESTAS

### Solución 1: Usar TAMBIÉN "Descripcion Diagnostico" (RECOMENDADA ⭐)

**Archivo**: `core/unified_extractor.py`  
**Línea**: 751-757

```python
# ANTES (INCORRECTO)
diagnostico_completo = extracted_data.get('diagnostico', 'N/A')
diagnostico_principal = extract_principal_diagnosis(diagnostico_completo) if diagnostico_completo and diagnostico_completo != 'N/A' else 'N/A'
db_record["Diagnostico Principal"] = diagnostico_principal

# DESPUÉS (CORRECTO)
# Prioridad 1: Diagnóstico extraído
diagnostico_completo = extracted_data.get('diagnostico', '')

# Prioridad 2: Si no hay diagnóstico, usar "Descripcion Diagnostico"
if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
    # Ya tenemos la descripción diagnóstico guardada
    desc_diagnostico = extracted_data.get('descripcion_diagnostico', '')
    if desc_diagnostico and desc_diagnostico not in ['', 'N/A']:
        # Extraer diagnóstico principal de la descripción
        diagnostico_completo = desc_diagnostico

# Extraer solo el diagnóstico principal (sin texto adicional)
diagnostico_principal = extract_principal_diagnosis(diagnostico_completo) if diagnostico_completo and diagnostico_completo != 'N/A' else 'N/A'

db_record["Diagnostico Principal"] = diagnostico_principal
```

### Solución 2: Verificar que se mapee correctamente "Descripcion Diagnostico"

**Archivo**: `core/unified_extractor.py`  
**Línea**: 197

Verificar que el campo se esté guardando:

```python
# VERIFICAR QUE ESTO EXISTA
combined_data['Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)'] = medical_data.get('descripcion_microscopica', '') or medical_data.get('descripcion_microscopica_final', '')
```

**PROBLEMA**: Actualmente se está mapeando la descripción MICROSCOPICA a la columna de descripción DIAGNOSTICO.

**CORRECCIÓN NECESARIA**:
```python
# AGREGAR campo faltante (no existe actualmente)
combined_data['Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)'] = medical_data.get('diagnostico_final', '') or medical_data.get('diagnostico_final_ihq', '')
```

### Solución 3: Ajustar `map_to_database_format()` (CRÍTICA ⭐⭐⭐)

**Archivo**: `core/unified_extractor.py`  
**Línea**: 751-757

```python
# CÓDIGO COMPLETO CORREGIDO
def map_to_database_format(extracted_data: Dict[str, Any]) -> Dict[str, str]:
    # ...código anterior...
    
    # === INFORMACIÓN MÉDICA ===
    
    # CORREGIDO: Extraer ambos campos
    diagnostico_completo = extracted_data.get('diagnostico', '')
    descripcion_diagnostico = extracted_data.get('descripcion_diagnostico', '')
    
    # Priorizar descripción diagnóstico si diagnóstico está vacío
    if not diagnostico_completo or diagnostico_completo in ['', 'N/A']:
        diagnostico_completo = descripcion_diagnostico
    
    # Extraer diagnóstico principal limpio
    diagnostico_principal = extract_principal_diagnosis(diagnostico_completo) if diagnostico_completo and diagnostico_completo != 'N/A' else 'N/A'
    
    db_record["Diagnostico Principal"] = diagnostico_principal
    db_record["Descripcion Diagnostico (5,6,7 Tipo histológico, subtipo histológico, margenes tumorales)"] = diagnostico_completo
```

---

## 📝 PASOS PARA IMPLEMENTAR LA SOLUCIÓN

### Paso 1: Verificar qué se está extrayendo

```bash
cd herramientas_ia
python cli_herramientas.py bd -b IHQ250005
```

Verificar campos:
- `Diagnostico Principal` (vacío ❌)
- `Descripcion Diagnostico` (lleno ✅)

### Paso 2: Aplicar corrección en `unified_extractor.py`

Modificar función `map_to_database_format()` líneas 751-757.

### Paso 3: Eliminar BD y reprocesar

```bash
rm data/huv_oncologia_NUEVO.db
```

Ejecutar UI y procesar todos los PDFs de nuevo.

### Paso 4: Validar mejoras

```bash
cd herramientas_ia
python cli_herramientas.py bd --stats
python cli_herramientas.py bd -b IHQ250005
```

Verificar que:
- Diagnóstico Principal: 47+/50 (94%+)
- Descripción Diagnóstico: 50/50 (100%)

---

## 🎯 IMPACTO ESPERADO

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Diagnóstico Principal | 31/50 (62%) | 47+/50 (94%+) | +32% |
| Casos correctos | 31 | 47+ | +16 casos |
| Casos sin info | 4 | 3-4 | Similar |

---

## ⚠️ NOTAS IMPORTANTES

1. **NO modificar `medical_extractor.py`**: La extracción funciona correctamente. El problema es el mapeo.

2. **Campo "Descripcion Diagnostico"**: Este campo ya contiene toda la información del diagnóstico completo extraído del PDF.

3. **Función `extract_principal_diagnosis()`**: Esta función ya existe y funciona correctamente para extraer solo el diagnóstico principal de un texto largo.

4. **Reprocesamiento obligatorio**: Después de la corrección, es necesario eliminar la BD y reprocesar todos los PDFs.

---

## 🔄 PRÓXIMOS PASOS

1. ✅ Análisis completado
2. ⏳ Implementar Solución 3 en `unified_extractor.py`
3. ⏳ Eliminar base de datos
4. ⏳ Reprocesar PDFs
5. ⏳ Validar mejoras con herramientas CLI
6. ⏳ Generar reporte de validación

---

**Estado**: PENDIENTE DE IMPLEMENTACIÓN  
**Prioridad**: ALTA ⚠️  
**Tiempo Estimado**: 30-45 minutos (implementación + reprocesamiento)

---

*Generado por: GitHub Copilot*  
*Fecha: 5 de octubre de 2025*  
*Versión: 1.0*
