# DIAGNÓSTICO TÉCNICO: Corrección v6.5.72 - Patrón "Resultado de" con Balanceo de Paréntesis

## CASO: IHQ250260

### PROBLEMA DETECTADO

**Versión:** v6.5.71 (FALLIDA)
**Síntoma:** Biomarcadores MMR capturan texto hasta "RECEPTORES ESTROGENOS" en lugar de detenerse después del paréntesis de cierre correspondiente.

**Valores capturados INCORRECTAMENTE:**
```
IHQ_MLH1: POSITIVO (EXPRESIÓN NUCLEAR INTACTA RESULTADO DE MSH2: EXPRESIÓN NUCLEAR INTACTA RESULTADO DE MSH6: EXPRESIÓN NUCLEAR INTACTA RESULTADO DE PMS2: EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO) RECEPTORES ESTROGENOS)

IHQ_MSH2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA RESULTADO DE MSH6: EXPRESIÓN NUCLEAR INTACTA RESULTADO DE PMS2: EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO) RECEPTORES ESTROGENOS)

IHQ_MSH6: POSITIVO (EXPRESIÓN NUCLEAR INTACTA RESULTADO DE PMS2: EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO) RECEPTORES ESTROGENOS)

IHQ_PMS2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO) RECEPTORES ESTROGENOS)
```

**Valores esperados CORRECTOS:**
```
IHQ_MLH1: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_MSH2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_MSH6: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_PMS2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO))
```

### TEXTO OCR ORIGINAL

```
Resultado de MLH1: expresión nuclear intacta 
Resultado de MSH2: expresión nuclear intacta
Resultado de MSH6: expresión nuclear intacta
Resultado de PMS2: expresión nuclear intacta (hay marcación citoplasmática patrón punteado y
nuclear moteado)
RECEPTORES ESTROGENOS. HER2: NEGATIVO 1+
```

### ANÁLISIS DE CAUSA RAÍZ

**Patrón v6.5.71 (FALLIDO):**
```python
r'(?i)Resultado\s+de\s+MLH1[:\s]*(.+?\))(?=\s*\n[A-Z]|\s*Resultado|$)'
```

**Problemas identificados:**

1. **`.+?\)` captura hasta primer `)` encontrado pero no balancea paréntesis**
   - En "PMS2: intacta (hay marcación... moteado)" hay 1 apertura y 1 cierre
   - El patrón encuentra el primer `)` después de "moteado", que es correcto
   - Pero el lookahead falla

2. **Lookahead `(?=\s*\n[A-Z]|\s*Resultado|$)` demasiado estricto**
   - Requiere: nueva línea + mayúscula, O "Resultado", O fin de string
   - Después del `)` correcto hay: " RECEPTORES ESTROGENOS"
   - NO hay `\n` antes de "RECEPTORES", por lo que el lookahead falla
   - El motor regex continúa buscando el siguiente `)`

3. **Consecuencia: Captura cascada de todos los marcadores**
   - MLH1 captura hasta el `)` de PMS2 + "RECEPTORES ESTROGENOS)"
   - MSH2 captura hasta el `)` de PMS2 + "RECEPTORES ESTROGENOS)"
   - MSH6 captura hasta el `)` de PMS2 + "RECEPTORES ESTROGENOS)"
   - PMS2 captura hasta "ESTROGENOS)"

### SOLUCIÓN PROPUESTA: v6.5.72

**Estrategia:** Detener en nueva línea vacía o línea con campo conocido

**Nuevo patrón:**
```python
# V6.5.72 FIX IHQ250260: Detener en nueva línea vacía o línea con campo conocido
# Captura hasta fin de línea (puede tener paréntesis internos)
r'(?i)Resultado\s+de\s+MLH1[:\s]*(.+?)(?=\s*\n\s*(?:Resultado|RECEPTORES|DIAGNÓSTICO|Interpretación|$))'
```

**Ventajas:**

1. **Captura multilínea dentro del marcador**
   - Permite texto en múltiples líneas dentro del mismo marcador
   - Ejemplo: "intacta (hay marcación... \n nuclear moteado)"

2. **Detiene en separadores conocidos**
   - Nueva línea seguida de "Resultado de" (siguiente marcador)
   - Nueva línea seguida de "RECEPTORES" (nuevo campo)
   - Nueva línea seguida de "DIAGNÓSTICO" (nueva sección)
   - Nueva línea seguida de "Interpretación" (nueva sección)
   - Fin de string

3. **No requiere balanceo complejo de paréntesis**
   - Usa separadores de contexto en lugar de contar paréntesis
   - Más robusto ante variaciones de formato

### VALIDACIÓN REQUERIDA

**Casos de prueba:**

1. **IHQ250260** (caso actual)
   - PMS2 con paréntesis interno multilinea
   - Verificar que NO capture "RECEPTORES ESTROGENOS"

2. **IHQ250259** (validado en v6.5.69)
   - MLH1 con descripción completa hasta punto
   - Verificar que no rompa caso anterior

3. **IHQ250133** (validado en v6.4.19)
   - Formato "no presentan pérdida" narrativo
   - Verificar que patrón de fallback sigue funcionando

4. **IHQ250239** (validado en v6.5.34)
   - Protocolo CAP con múltiples líneas
   - Verificar que multilinea dentro de marcador funcione

### IMPLEMENTACIÓN

**Archivos a modificar:**
1. `core/extractors/biomarker_extractor.py` líneas 3635, 3690, 3739, 3788
   - Reemplazar patrón v6.5.71 con v6.5.72 en MLH1, MSH2, MSH6, PMS2

**Comando de reprocesamiento:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250260 --func-06
```

**Validación anti-regresión:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250260 --inteligente  # Debe ser 100%
python herramientas_ia/auditor_sistema.py IHQ250259 --func-06 && python herramientas_ia/auditor_sistema.py IHQ250259 --inteligente  # Debe mantener 100%
python herramientas_ia/auditor_sistema.py IHQ250133 --func-06 && python herramientas_ia/auditor_sistema.py IHQ250133 --inteligente  # Debe mantener 100%
python herramientas_ia/auditor_sistema.py IHQ250239 --func-06 && python herramientas_ia/auditor_sistema.py IHQ250239 --inteligente  # Debe mantener 100%
```

### RESULTADO ESPERADO

**Después de v6.5.72:**
```
IHQ_MLH1: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_MSH2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_MSH6: POSITIVO (EXPRESIÓN NUCLEAR INTACTA)
IHQ_PMS2: POSITIVO (EXPRESIÓN NUCLEAR INTACTA (HAY MARCACIÓN CITOPLASMÁTICA PATRÓN PUNTEADO Y NUCLEAR MOTEADO))
```

**Score de auditoría:** 100% (sin contaminación de "RECEPTORES ESTROGENOS")

---

**Fecha:** 2026-01-29
**Versión:** v6.5.72 (propuesta)
**Autor:** Claude Sonnet 4.5 (data-auditor agent)
