# 📊 ANÁLISIS COMPLETO DEL SISTEMA DE EXTRACCIÓN HUV
**Fecha**: 2025-10-05
**Versión actual**: 4.2.1
**Total de casos**: 50
**BD**: data/huv_oncologia_NUEVO.db

---

## 🎯 RESUMEN EJECUTIVO

### Estado Actual de Completitud
- **Diagnóstico Principal**: 34/50 casos (68%) → ❌ **16 casos faltantes (32%)**
- **Factor Pronóstico**: 6/50 casos (12%) → ❌ **44 casos faltantes (88%)**
- **Biomarcadores Principales**:
  - HER2: 8/50 (16%)
  - Ki-67: 5/50 (10%)
  - RE: 6/50 (12%)
  - RP: 5/50 (10%)

### Problema Principal Identificado

Los 16 casos sin "Diagnóstico Principal" **SÍ TIENEN EL DIAGNÓSTICO**, pero está en el campo:
**"Descripción Diagnóstico (5,6,7 Tipo histológico...)"**

---

## 🔍 ANÁLISIS DETALLADO DE CASOS PROBLEMÁTICOS

### Casos Sin Diagnóstico (pero con info en Desc_Diagnostico)

| Caso | Petición | Diagnóstico Real en Desc_Diagnostico |
|------|----------|--------------------------------------|
| 9 | IHQ250009 | HALLAZGOS... COMPATIBLES CON **HIBERNOMA** |
| 11 | IHQ250011 | HALLAZGOS... COMPATIBLES CON **TEJIDO ENDOMETRIAL ECTÓPICO** |
| 13 | IHQ250013 | HALLAZGOS... COMPATIBLES CON **FIBROMA** |
| 14 | IHQ250014 | **NEGATIVO PARA LESIÓN ESCAMOSA** PREINVASIVA/INVASIVA |
| 15 | IHQ250015 | **NEGATIVO PARA LESIÓN ESCAMOSA** PREINVASIVA/INVASIVA |
| 17 | IHQ250017 | NEOPLASIA **LINFOIDE** B (Desc_Diagnostico) |
| 24 | IHQ250024 | ... (más casos similares) |
| 30 | IHQ250030 | EXPRESIÓN DE CD117 Y CD56 **NEGATIVA** |
| 32 | IHQ250032 | HALLAZGOS COMPATIBLES CON **TIMOMA TIPO B2** |

---

## 🧬 PATRONES ENCONTRADOS

### Patrones QUE SÍ Funcionan (34 casos)
✅ Diagnósticos con términos en _KEY_DIAG_TERMS:
- "CARCINOMA ESCAMOCELULAR METASTÁSICO"
- "ADENOCARCINOMA METASTÁSICO CON PRIMARIO PULMONAR"
- "MENINGIOMA MENINGOTELIAL, WHO 1"
- "TUMOR NEUROENDOCRINO HIPOFISIARIO"

### Patrones QUE NO Funcionan (16 casos)
❌ Diagnósticos sin términos clave:
- "HALLAZGOS COMPATIBLES CON **[HIBERNOMA|FIBROMA|TIMOMA]**"
- "NEGATIVO PARA **LESIÓN ESCAMOSA**"
- "EXPRESIÓN DE **[marcador]** NEGATIVA"
- "NEOPLASIA **LINFOIDE**" (LINFOIDE no está en lista)
- Diagnósticos en campo "Descripción Diagnóstico" en lugar de "Diagnóstico Principal"

---

## 🔧 CAUSAS RAÍZ IDENTIFICADAS

### 1. Lista Incompleta de Términos Diagnósticos
**Archivo**: core/extractors/medical_extractor.py
**Variable**: _KEY_DIAG_TERMS

**Términos FALTANTES**:
- HIBERNOMA
- FIBROMA
- TIMOMA
- LINFOIDE
- PLASMATICAS (para "NEOPLASIA DE CELULAS PLASMATICAS")
- ENDOMETRIAL
- ESCAMOSA (para "LESIÓN ESCAMOSA")
- ECTÓPICO

### 2. No se Capturan Diagnósticos con Prefijos Especiales
Patrones NO reconocidos:
- "HALLAZGOS COMPATIBLES CON [diagnóstico]"
- "NEGATIVO PARA [diagnóstico]"
- "EXPRESIÓN DE [marcador] NEGATIVA/POSITIVA"

### 3. El Extractor Solo Busca en Texto de "Diagnóstico"
La función xtract_principal_diagnosis() solo procesa el campo extraído como "Diagnóstico".

NO busca en:
- "Descripción Diagnóstico (5,6,7...)"
- "Descripción Microscópica"

---

## 🛠️ SOLUCIONES PROPUESTAS

### Solución 1: Expandir Lista de Términos Clave ⚡ ALTA PRIORIDAD
**Archivo**: core/extractors/medical_extractor.py:308-314

**Agregar a _KEY_DIAG_TERMS**:
`python
_KEY_DIAG_TERMS = [
    # Existentes
    'CARCINOMA','ADENOCARCINOMA','SARCOMA','MELANOMA','LINFOMA','GLIOMA','MENINGIOMA',
    'ASTROCITOMA','OLIGODENDROGLIOMA','METASTASICO','METASTÁSICO','SCHWANNOMA','HEMANGIOMA',
    'ANGIOSARCOMA','LEIOMIOSARCOMA','RHABDOMIOSARCOMA','GLANGIOMA','NEUROBLASTOMA','MEDULOBLASTOMA',
    
    # NUEVOS - Tumores Benignos/Intermedios
    'HIBERNOMA',        # Caso IHQ250009
    'FIBROMA',          # Caso IHQ250013
    'TIMOMA',           # Caso IHQ250032
    'LIPOMA',
    'CONDROMA',
    'OSTEOMA',
    
    # NUEVOS - Términos Hematológicos
    'LINFOIDE',         # Caso IHQ250017
    'MIELOMA',
    'PLASMATICAS',      # "NEOPLASIA DE CELULAS PLASMATICAS"
    'LEUCEMIA',
    
    # NUEVOS - Lesiones Específicas
    'ENDOMETRIAL',      # Caso IHQ250011
    'ECTOPICO',
    'ECTÓPICO',
    'DECIDUALIZADO',
    
    # NUEVOS - Términos de Lesiones
    'ESCAMOSA',         # Casos IHQ250014, IHQ250015
    'PREINVASIVA',
    'DISPLASIA',
    'HETEROTOPIA'
]
`

**Impacto estimado**: Resolverá ~10 de los 16 casos (62.5%)

### Solución 2: Capturar Patrones "HALLAZGOS COMPATIBLES" y "NEGATIVO PARA" ⚡ ALTA PRIORIDAD
**Archivo**: core/extractors/medical_extractor.py:359-428

**Modificar xtract_principal_diagnosis()** para detectar estos patrones ANTES del scoring:

`python
def extract_principal_diagnosis(full_text: str) -> str:
    if not full_text:
        return ''
    
    # NUEVO: Detectar patrones especiales primero
    special_patterns = [
        # "HALLAZGOS COMPATIBLES CON [diagnóstico]"
        r'HALLAZGOS\s+(?:HIST[ÓO]L[ÓO]GICOS\s+)?(?:DE\s+)?(?:MORFOLOG[ÍI]A\s+E\s+)?INMUNOHISTOQU[ÍI]MICA\s+COMPATIBLES?\s+CON\s+([A-ZÁÉÍÓÚÑ\s]{10,100}?)(?:\.|NANCY|ARMANDO|CARLOS|$)',
        
        # "NEGATIVO PARA [condición]"
        r'NEGATIVO\s+PARA\s+([A-ZÁÉÍÓÚÑ\s/]{10,80}?)(?:\.|$)',
        
        # "EXPRESIÓN DE [marcador] NEGATIVA/POSITIVA"
        r'EXPRESI[ÓO]N\s+DE\s+([A-Z0-9\s,YÓÚ]+?)\s+(NEGATIVA|POSITIVA)(?:\.|$)',
    ]
    
    for pattern in special_patterns:
        match = re.search(pattern, full_text.upper())
        if match:
            # Capturado el diagnóstico especial
            diag = match.group(1).strip().upper()
            # Limpiar espacios múltiples
            diag = re.sub(r'\s+', ' ', diag)
            return diag
    
    # Si no match especial, continuar con lógica existente...
    text = full_text.replace('\r', '\n')
    # ... resto del código actual ...
`

**Impacto estimado**: Resolverá ~5 de los 16 casos (31.25%)

### Solución 3: Buscar en Campo "Descripción Diagnóstico" si Falta Principal 🔧 MEDIA PRIORIDAD
**Archivo**: core/unified_extractor.py (función xtract_ihq_data)

**Modificar lógica de extracción**:

`python
# Después de extraer todos los campos...
diagnostico_principal = extract_principal_diagnosis(datos_medicos.get('diagnostico', ''))

# NUEVO: Si no hay diagnóstico principal, buscar en Descripción Diagnóstico
if not diagnostico_principal or diagnostico_principal == 'N/A':
    desc_diagnostico = datos_medicos.get('descripcion_diagnostico', '')
    if desc_diagnostico and desc_diagnostico != 'N/A':
        # Intentar extraer de la descripción
        diagnostico_principal = extract_principal_diagnosis(desc_diagnostico)
`

**Impacto estimado**: Resolverá casos donde el diagnóstico está en campo incorrecto

### Solución 4: Mejorar Extracción de Factor Pronóstico 🔧 MEDIA PRIORIDAD
**Archivo**: core/extractors/medical_extractor.py:215-303

El Factor Pronóstico tiene solo **12% de completitud** (6/50 casos).

**Problema**: La función xtract_factor_pronostico() solo busca patrones muy específicos:
- Ki-67
- p53
- Líneas de "inmunorreactividad"

**Solución**: Ampliar patrones para capturar:
- Líneas completas de resultados IHQ: "p40 POSITIVO / p16 POSITIVO"
- Líneas de negatividad: "Los marcadores... son negativos"
- Expresiones complejas: "Ki 67: 8% / p53 tiene expresión en mosaico"

---

## 📈 IMPACTO ESTIMADO DE LAS SOLUCIONES

| Solución | Casos Resueltos | % Mejora Diagnóstico | Tiempo Impl. |
|----------|-----------------|----------------------|--------------|
| 1. Expandir términos | ~10 casos | +20% (68% → 88%) | 5 min |
| 2. Patrones especiales | ~5 casos | +10% (88% → 98%) | 15 min |
| 3. Buscar en Desc.Diag | ~1 caso | +2% (98% → 100%) | 10 min |
| 4. Mejorar F.Pronóstico | ~20 casos | Factor: 12% → 52% | 20 min |
| **TOTAL** | **16 casos** | **Diagnóstico: 100%** | **50 min** |

---

## 🚀 PLAN DE IMPLEMENTACIÓN

### Fase 1: Mejoras Rápidas (15 min)
1. ✅ Limpiar archivos temporales del root → **COMPLETADO**
2. ✅ Mover reportes a herramientas_ia/resultados/ → **COMPLETADO**
3. ⏳ Expandir _KEY_DIAG_TERMS con nuevos términos
4. ⏳ Agregar patrones especiales a xtract_principal_diagnosis()

### Fase 2: Mejoras Estructurales (20 min)
5. ⏳ Implementar búsqueda en "Descripción Diagnóstico"
6. ⏳ Mejorar patrones de Factor Pronóstico
7. ⏳ Probar con casos conocidos

### Fase 3: Validación y Reprocesamiento (15 min)
8. ⏳ Eliminar BD: m data/huv_oncologia_NUEVO.db
9. ⏳ Reprocesar todos los PDFs
10. ⏳ Validar con herramientas CLI
11. ⏳ Generar reporte de mejoras

---

## 📋 CHECKLIST DE VALIDACIÓN

Después de implementar, validar con:

`ash
# Ver estadísticas generales
python herramientas_ia/cli_herramientas.py bd --stats

# Validar casos específicos que antes fallaban
python herramientas_ia/cli_herramientas.py bd -b IHQ250009
python herramientas_ia/cli_herramientas.py bd -b IHQ250011
python herramientas_ia/cli_herramientas.py bd -b IHQ250013

# Exportar a Excel para análisis
# (Ya creado: EXCEL/ANALISIS_BD_COMPLETA.xlsx)
`

---

## 📁 ARCHIVOS AFECTADOS

1. core/extractors/medical_extractor.py → Modificar
2. core/unified_extractor.py → Modificar (opcional, Fase 2)
3. data/huv_oncologia_NUEVO.db → Eliminar y regenerar

---

## 🎓 LECCIONES APRENDIDAS

1. **Los datos SÍ están en el PDF**, solo no se capturan correctamente
2. **El 68% de completitud actual es engañoso** - muchos diagnósticos están en campo incorrecto
3. **Los términos clave deben incluir TODO tipo de tumor**, no solo malignos
4. **Los patrones especiales ("HALLAZGOS COMPATIBLES") son comunes** en informes IHQ

---

**Generado por**: Análisis automatizado CLI
**Próximo paso**: Implementar Fase 1 (Mejoras Rápidas)

