# 📋 REGLAS DE EXTRACCIÓN - SISTEMA EVARISIS (RESUMIDO)

## 🎯 CAMPOS PRINCIPALES

### **1. ORGANO vs IHQ_ORGANO** ⚠️
- **"Organo"**: Órgano GENERAL (tabla superior PDF) → Ej: `"MAMA"`, `"TUMOR REGION INTRADURAL"`
- **"IHQ_ORGANO"**: Órgano ESPECÍFICO (sección diagnóstico) → Ej: `"MAMA DERECHA, CUADRANTE SUPERIOR EXTERNO"`

### **2. DIAGNOSTICO PRINCIPAL**
- Sección "DIAGNÓSTICO" → líneas con "-"
- ⚠️ Error común: Se corta por salto de línea

### **3. FACTOR PRONOSTICO** ⚠️ SE CONSTRUYE, NO SE EXTRAE
**NO busques literal "Factor Pronóstico"**. Sistema busca:
1. **Ki-67** (índice proliferación) → `"Ki-67: 8%"`
2. **p53** (supresor tumoral) → `"p53: POSITIVO"`
3. **Otros** (p40, p16, Synaptofisina) → `"p40 POSITIVO"`
4. Une todo con " / " → `"Ki-67: 8% / p53 POSITIVO"`

**Tu trabajo**: Completar si falta algo, usar `"No se indica"` SOLO si realmente no hay biomarcadores.

### **4. BIOMARCADORES IHQ**
**TIPO A (POSITIVO/NEGATIVO)**: IHQ_HER2, IHQ_P40_ESTADO, IHQ_CK7...
- ✅ Correcto: `"POSITIVO"`, `"NEGATIVO"`
- ❌ Incorrecto: Porcentajes

**TIPO B (PORCENTAJE)**: IHQ_KI-67, IHQ_P16_PORCENTAJE
- ✅ Correcto: `"15%"`, `"1-2%"`
- ❌ Incorrecto: `"POSITIVO"`

## 🔍 AUDITORÍA COMPLETA
1. ✅ **Veracidad**: ¿BD = PDF?
2. ✅ **Ubicación correcta**: ¿Campo correcto?
3. ✅ **Completitud**: ¿Datos completos o cortados?
4. ✅ **Tipo dato**: ¿Formato correcto?

## 📊 CAUSAS COMUNES
- **Diagnóstico incompleto**: Salto línea → Completar
- **Factor Pronóstico vacío**: Biomarcador en otra sección → Buscar en TODO el PDF
- **Biomarcador no capturado**: Buscar y completar
