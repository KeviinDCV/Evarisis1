# 📋 REGLAS DE EXTRACCIÓN - SISTEMA EVARISIS

**Propósito**: Guía para auditoría IA - explica cómo el sistema extrae datos del PDF a la base de datos

---

## 🎯 CAMPOS PRINCIPALES Y SUS REGLAS

### **1. ORGANO vs IHQ_ORGANO** ⚠️ DOS COLUMNAS DIFERENTES

#### **Columna: "Organo (1. Muestra enviada a patología)"**
- **Se extrae de**: Tabla superior del PDF → línea "Organo"
- **Qué contiene**: Órgano GENERAL/PRINCIPAL
- **Ejemplos correctos**:
  - `"MAMA"`
  - `"TUMOR REGION INTRADURAL"`
  - `"BX DE PLEURA + BX DE PULMON"`
  - `"LESION HIPOFISIS"`

#### **Columna: "IHQ_ORGANO"**
- **Se extrae de**: Sección "DIAGNÓSTICO" → primera línea antes del diagnóstico
- **Qué contiene**: Sección/área ESPECÍFICA del órgano
- **Ejemplos correctos**:
  - `"MAMA DERECHA, CUADRANTE SUPERIOR EXTERNO"`
  - `"Región intradural (cauda equina)"`
  - `"Pleura"`

**⚠️ Errores comunes**:
- Órgano general en columna de órgano específico (o viceversa)
- Texto cortado por salto de línea

---

### **2. DIAGNOSTICO PRINCIPAL**

- **Se extrae de**: Sección "DIAGNÓSTICO" → líneas que empiezan con "-"
- **Qué contiene**: Diagnóstico histopatológico completo
- **Ejemplos correctos**:
  - `"CARCINOMA ESCAMOCELULAR METASTÁSICO p40 POSITIVO / p16 POSITIVO"`
  - `"ADENOCARCINOMA METASTÁSICO CON PRIMARIO PULMONAR"`
  - `"TUMOR NUEROENDOCRINO HIPOFISIARIO"`

**⚠️ Errores comunes**:
- Solo captura primera palabra: `"CARCINOMA"` (debería estar completo)
- Se corta por salto de línea
- Incluye biomarcadores que deberían ir en Factor Pronóstico

---

### **3. FACTOR PRONOSTICO** ⚠️ SE CONSTRUYE, NO SE EXTRAE LITERAL

**IMPORTANTE**: La palabra "Factor Pronóstico" casi NUNCA aparece literal en el PDF.

**Cómo lo construye el sistema automático**:

1. **Busca Ki-67** (índice de proliferación) en TODO el texto
   - Ejemplo: `"Ki-67: 8%"`, `"ÍNDICE DE PROLIFERACIÓN CÉLULAR MEDIDO CON Ki 67: 8%"`

2. **Busca p53** (supresor tumoral) en TODO el texto
   - Ejemplo: `"p53 tiene expresión en mosaico (no mutado)"`, `"p53: POSITIVO"`

3. **Busca otros biomarcadores** en descripción microscópica y diagnóstico
   - Ejemplo: `"p40 positivo"`, `"p16 positivo en bloque"`

4. **Une todos** con " / "
   - Resultado: `"Ki-67: 8% / p53 tiene expresión en mosaico (no mutado)"`

**Si NO encuentra nada** → Campo vacío en BD

---

#### **⚠️ TU TRABAJO: CORREGIR/COMPLETAR EL FACTOR PRONÓSTICO**

**Debes**:

1. **Verificar** si el sistema lo extrajo bien:
   - ¿El PDF menciona Ki-67? → ¿Está en BD?
   - ¿El PDF menciona p53? → ¿Está en BD?
   - ¿El PDF menciona p40, p16, Synaptofisina? → ¿Están en BD?

2. **Completar si falta algo**:
   - BD vacío + PDF tiene Ki-67 → Agregar `"Ki-67: 15%"`
   - BD tiene `"Ki-67: 15%"` + PDF también tiene p53 → Completar con `"Ki-67: 15% / p53: POSITIVO"`

3. **Entender por qué falló**:
   - Biomarcador en página diferente
   - Formato diferente al esperado
   - Sección no revisada por el sistema

4. **Usar "No se indica" SOLO si**:
   - Buscaste en TODAS las secciones
   - NO hay Ki-67, p53, Synaptofisina, p40, p16, HER2, ni NINGÚN biomarcador
   - Entonces → `"No se indica"`

**Ejemplos**:

**Caso 1: Sistema falló, pero SÍ hay datos**
```
BD: vacío
PDF: "p40 positivo. p16 positivo en bloque."
→ Corrección: "p40 POSITIVO / p16 POSITIVO"
→ Razón: "Biomarcadores p40 y p16 encontrados en descripción microscópica"
```

**Caso 2: Sistema incompleto**
```
BD: "Ki-67: 8%"
PDF: También dice "p53 tiene expresión en mosaico (no mutado)"
→ Corrección: "Ki-67: 8% / p53 tiene expresión en mosaico (no mutado)"
→ Razón: "Faltaba agregar p53 encontrado en el PDF"
```

**Caso 3: Realmente no hay**
```
BD: vacío
PDF: No menciona ningún biomarcador pronóstico
→ Corrección: "No se indica"
→ Razón: "No se encontró ningún biomarcador pronóstico en el PDF"
```

---

### **4. BIOMARCADORES IHQ** (IHQ_HER2, IHQ_KI-67, IHQ_P40, etc.)

**Se extraen de**: Descripción microscópica, secciones específicas (EXPRESIÓN HORMONAL, FACTORES DE TRANSCRIPCIÓN)

#### **TIPOS DE DATOS POR COLUMNA**:

**TIPO A: POSITIVO/NEGATIVO**
- Columnas: `IHQ_P16_ESTADO`, `IHQ_P40_ESTADO`, `IHQ_HER2`, `IHQ_PDL-1`, `IHQ_RECEPTOR_ESTROGENO`, `IHQ_CK7`, etc.
- ✅ Valores correctos: `"POSITIVO"`, `"NEGATIVO"`, `"POSITIVO FOCAL"`, `"POSITIVO DIFUSO"`
- ❌ NO enviar: `"15%"`, números sin contexto

**TIPO B: PORCENTAJE**
- Columnas: `IHQ_KI-67`, `IHQ_P16_PORCENTAJE`
- ✅ Valores correctos: `"15%"`, `"80%"`, `"1-2%"`
- ❌ NO enviar: `"POSITIVO"`, solo texto

**⚠️ Errores comunes**:
- Porcentaje en columna que debe ser POSITIVO/NEGATIVO
- POSITIVO/NEGATIVO en columna de porcentaje
- Biomarcador mencionado en PDF pero columna vacía en BD

---

### **5. DESCRIPCION MACROSCOPICA**

- **Se extrae de**: Sección "DESCRIPCIÓN MACROSCÓPICA"
- **Qué contiene**: Descripción visual del espécimen
- **⚠️ Error común**: Texto cortado por salto de página

---

### **6. DESCRIPCION MICROSCOPICA**

- **Se extrae de**: Sección "DESCRIPCIÓN MICROSCÓPICA"
- **Qué contiene**: Descripción histológica + biomarcadores + inmunorreactividad
- **⚠️ Error común**: No captura biomarcadores mencionados aquí

---

## 🔍 QUÉ DEBES VERIFICAR AL AUDITAR

### **AUDITORÍA PARCIAL** (completar vacíos):
1. ✅ ¿Los campos vacíos tienen datos en el PDF?
2. ✅ ¿El tipo de dato es correcto? (POSITIVO/NEGATIVO vs %)
3. ✅ Si no existe el dato → `"No se indica"`

### **AUDITORÍA COMPLETA** (análisis profundo):
1. ✅ **Veracidad**: ¿El dato en BD coincide con el PDF?
2. ✅ **Ubicación correcta**: ¿Órgano general vs específico en columna correcta?
3. ✅ **Completitud**: ¿Diagnóstico completo o cortado?
4. ✅ **Tipo de dato**: ¿Formato correcto para la columna?
5. ✅ **Biomarcadores no mapeados**: ¿Hay marcadores en PDF sin columna en BD?

---

## 📊 CAUSAS COMUNES DE ERROR

| Error | Causa | Qué hacer |
|-------|-------|-----------|
| Diagnóstico incompleto | Salto de línea en PDF | Completar con texto del PDF |
| Factor Pronóstico vacío | Biomarcadores en sección diferente | Buscar Ki-67, p53 en TODO el PDF |
| Órgano en columna incorrecta | Confusión general vs específico | Verificar fuente (tabla superior vs diagnóstico) |
| Biomarcador no capturado | No existe columna en BD | Sugerir agregar columna nueva (solo en auditoría completa) |
| Porcentaje en columna de estado | Tipo de dato incorrecto | Indicar error de tipo |

---

## 📝 REGLA "No se indica"

Usar **SOLO** cuando:
- Buscaste en TODAS las secciones del PDF
- El dato NO existe en ninguna parte
- Ejemplo: Factor Pronóstico cuando no hay ningún biomarcador

**NO usar** cuando:
- El dato existe pero el sistema no lo capturó → Completar con el dato correcto
- El dato está incompleto → Completar con la versión completa

---

**FIN - DOCUMENTO SIMPLIFICADO PARA IA**
