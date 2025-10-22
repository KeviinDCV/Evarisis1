# 🔧 SUGERENCIAS DE MEJORA PARA PROMPTS IA

**Generado**: 2025-10-22 05:06:54
**Sistema**: EVARISIS v6.1.0

---

## 📊 RESUMEN DE ANÁLISIS

### system_prompt_comun.txt

- **Cobertura actual**: 33.3%
- **Conocimiento presente**: 2/6
- **Conocimiento ausente**: 4/6

**Conocimiento faltante CRÍTICO**:
- 🚨 Campo DIAGNOSTICO_COLORACION con 5 componentes semánticos
- 🚨 5 componentes semánticos de DIAGNOSTICO_COLORACION

### system_prompt_parcial.txt

- **Cobertura actual**: 33.3%
- **Conocimiento presente**: 2/6
- **Conocimiento ausente**: 4/6

**Conocimiento faltante CRÍTICO**:
- 🚨 Campo DIAGNOSTICO_COLORACION con 5 componentes semánticos
- 🚨 5 componentes semánticos de DIAGNOSTICO_COLORACION

---

## 💡 MODIFICACIONES SUGERIDAS

### Modificación #1: system_prompt_comun.txt

- **Acción**: INSERTAR_AL_INICIO
- **Ubicación**: Línea 1 (antes del contenido actual)
- **Líneas a insertar**: 112
- **Cobertura**: 33.3% → 100.0%
- **Beneficio**: IA entenderá Study M vs IHQ, evitará contaminación, detectará 5 componentes semánticos

**Conocimiento que se agregará**:
- ✅ diagnostico_coloracion
- ✅ busqueda_multiseccion
- ✅ componentes_semanticos
- ✅ deteccion_semantica

**Texto a insertar**:

```
═══════════════════════════════════════════════════════════════
🧠 CONOCIMIENTO MÉDICO ONCOLÓGICO - EVARISIS v6.1.0
═══════════════════════════════════════════════════════════════

IMPORTANTE: Existen DOS estudios diferentes en patología oncológica:

1. **STUDY M (COLORACIÓN)**: Estudio inicial de patología
   - Usa técnicas de coloración H&E (Hematoxilina-Eosina)
   - Evalúa morfología celular y arquitectura tisular
   - Proporciona: Diagnóstico base, Grado Nottingham, Invasión linfovascular, Invasión perineural
   - Ubicación en PDF: DESCRIPCION_MACROSCOPICA o secciones específicas de coloración
   - Campo de destino: DIAGNOSTICO_COLORACION

2. **STUDY IHQ (INMUNOHISTOQUÍMICA)**: Estudio molecular posterior
   - Usa anticuerpos para detectar proteínas específicas
   - Evalúa expresión de biomarcadores (HER2, ER, PR, Ki-67, etc.)
   - Proporciona: Estado y porcentaje de biomarcadores
   - Ubicación en PDF: DESCRIPCION_MICROSCOPICA, DIAGNOSTICO, COMENTARIOS
   - Campos de destino: IHQ_HER2, IHQ_KI-67, IHQ_ER, etc.

⚠️ REGLA CRÍTICA ANTI-CONTAMINACIÓN:
❌ NUNCA mezclar datos del Study M (Coloración) en campos IHQ
❌ NUNCA usar información de Grado Nottingham para biomarcadores IHQ
❌ NUNCA confundir "invasión linfovascular" (Study M) con biomarcadores (Study IHQ)
✅ DIAGNOSTICO_COLORACION debe contener SOLO información del Study M
✅ Campos IHQ_* deben contener SOLO información de biomarcadores moleculares

---

📋 CAMPO CRÍTICO: DIAGNOSTICO_COLORACION (v6.1.0 - NUEVO)
---

**5 COMPONENTES SEMÁNTICOS** (deben extraerse del Study M - Coloración):

1. **Diagnóstico base**:
   - Ejemplo: "CARCINOMA DUCTAL INVASIVO"
   - Variantes: "CARCINOMA LOBULILLAR", "ADENOCARCINOMA", "TUMOR NEUROENDOCRINO"

2. **Grado Nottingham** (si aplica para tumores mamarios):
   - Ejemplo: "GRADO NOTTINGHAM 2 (SCORE 7: TUBULOS 3, PLEOMORFISMO 2, MITOSIS 2)"
   - Variantes: "GRADO 1", "GRADO 2", "GRADO 3"
   - Keywords: "Nottingham", "score", "grado histológico"

3. **Invasión linfovascular**:
   - Ejemplo: "INVASIÓN LINFOVASCULAR: NEGATIVO"
   - Variantes: "INVASIÓN VASCULAR: POSITIVO", "No se observa invasión linfovascular"
   - Keywords: "invasión linfovascular", "invasión vascular", "embolias vasculares"

4. **Invasión perineural**:
   - Ejemplo: "INVASIÓN PERINEURAL: NEGATIVO"
   - Variantes: "INVASIÓN PERINEURAL: POSITIVO", "No hay invasión perineural"
   - Keywords: "invasión perineural", "perineural"

5. **Carcinoma in situ**:
   - Ejemplo: "CARCINOMA DUCTAL IN SITU: NO"
   - Variantes: "CARCINOMA LOBULILLAR IN SITU: PRESENTE", "Sin componente in situ"
   - Keywords: "in situ", "CDIS", "CLIS"

**EJEMPLO CORRECTO DE DIAGNOSTICO_COLORACION COMPLETO**:
```
CARCINOMA DUCTAL INVASIVO, GRADO NOTTINGHAM 2 (SCORE 7: TUBULOS 3, PLEOMORFISMO 2, MITOSIS 2). INVASIÓN LINFOVASCULAR: NEGATIVO. INVASIÓN PERINEURAL: NEGATIVO. CARCINOMA DUCTAL IN SITU: NO.
```

**UBICACIÓN EN PDF**: Buscar en estas secciones (en orden de prioridad):
1. DESCRIPCION_MACROSCOPICA
2. Secciones tituladas "COLORACIÓN", "H&E", "HISTOLOGÍA"
3. Secciones de diagnóstico inicial (antes de IHQ)

---

🔍 BÚSQUEDA MULTI-SECCIÓN (PRIORIDAD PARA BIOMARCADORES IHQ)
---

Al buscar biomarcadores IHQ (HER2, Ki-67, ER, PR, etc.), usar PRIORIDAD:

1. **DESCRIPCION_MICROSCOPICA** (primera prioridad)
   - Contiene descripción detallada de expresión de marcadores
   - Ejemplo: "Ki-67 muestra índice proliferativo del 20%"

2. **DIAGNOSTICO** (segunda prioridad)
   - Puede contener resumen de biomarcadores
   - Ejemplo: "HER2 POSITIVO (3+)"

3. **COMENTARIOS** (tercera prioridad)
   - Puede contener aclaraciones o interpretaciones
   - Ejemplo: "El alto índice de Ki-67 sugiere alta proliferación"

⚠️ NO buscar biomarcadores IHQ en DESCRIPCION_MACROSCOPICA (es para Study M)

---

🎯 DETECCIÓN SEMÁNTICA (ENFOQUE INTELIGENTE)
---

El sistema EVARISIS usa detección basada en CONTENIDO, no en posiciones fijas:

✅ **Buscar por keywords contextuales**:
   - "Grado Nottingham" → DIAGNOSTICO_COLORACION (componente 2)
   - "Ki-67:" → IHQ_KI-67
   - "HER2:" → IHQ_HER2
   - "invasión linfovascular" → DIAGNOSTICO_COLORACION (componente 3)

✅ **Considerar variaciones de formato**:
   - "Ki-67: 20%" = "Ki 67: 20%" = "KI67: 20%" (mismo dato)
   - "HER2 POSITIVO" = "HER-2: POSITIVO" = "HER 2 +" (mismo dato)

✅ **Contexto médico importa**:
   - "INVASIÓN LINFOVASCULAR" en Study M → DIAGNOSTICO_COLORACION
   - "Ki-67 del 2%" en Study IHQ → IHQ_KI-67
   - NO confundir contextos

═══════════════════════════════════════════════════════════════
```

---

### Modificación #2: system_prompt_parcial.txt

- **Acción**: INSERTAR_DESPUES_HEADER
- **Ubicación**: Después de línea 2 (después del header de MODO ULTRA-RÁPIDO)
- **Líneas a insertar**: 18
- **Cobertura**: 33.3% → 100.0%
- **Beneficio**: IA rápida entenderá Study M vs IHQ sin perder velocidad

**Conocimiento que se agregará**:
- ✅ diagnostico_coloracion
- ✅ busqueda_multiseccion
- ✅ componentes_semanticos
- ✅ deteccion_semantica

**Texto a insertar**:

```
🧠 CONOCIMIENTO RÁPIDO - STUDY M vs STUDY IHQ:
⚡ Study M (Coloración): Grado Nottingham, invasiones → DIAGNOSTICO_COLORACION
⚡ Study IHQ: Biomarcadores (Ki-67, HER2, ER, PR) → Campos IHQ_*
⚡ ANTI-CONTAMINACIÓN: NO mezclar Study M con IHQ
⚡ BÚSQUEDA MULTI-SECCIÓN: DESCRIPCION_MICROSCOPICA > DIAGNOSTICO > COMENTARIOS (para IHQ)

📋 DIAGNOSTICO_COLORACION - 5 componentes del Study M:
1. Diagnóstico base (ej: "CARCINOMA DUCTAL INVASIVO")
2. Grado Nottingham (ej: "GRADO NOTTINGHAM 2")
3. Invasión linfovascular (ej: "INVASIÓN LINFOVASCULAR: NEGATIVO")
4. Invasión perineural (ej: "INVASIÓN PERINEURAL: NEGATIVO")
5. Carcinoma in situ (ej: "CARCINOMA DUCTAL IN SITU: NO")

🔍 DETECCIÓN SEMÁNTICA - Busca por CONTENIDO no por posición:
✅ "Grado Nottingham" → DIAGNOSTICO_COLORACION
✅ "Ki-67: 20%" → IHQ_KI-67
✅ "invasión linfovascular" → DIAGNOSTICO_COLORACION
✅ Contexto médico importa - NO confundir Study M con IHQ
```

---

## 🎯 PRÓXIMOS PASOS

1. **Revisar sugerencias**: Valida que el texto propuesto es correcto
2. **Aplicar con core-editor**: Usa el agente core-editor para aplicar modificaciones
3. **Comando sugerido**:
   ```bash
   # Aplicar modificaciones usando este reporte
   python herramientas_ia/editor_core.py --aplicar-sugerencias-prompts sugerencias_mejoras_prompts_20251022_050654.json
   ```

4. **Validar**: Probar validación IA después de modificar prompts

