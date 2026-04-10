# ANALISIS FALLO v6.5.74 - IHQ250263

## RESUMEN EJECUTIVO

**Caso:** IHQ250263  
**Version:** v6.5.74  
**Estado:** FALLO - El patron v6.5.74 captura el nombre del medico junto con el diagnostico

---

## DIAGNOSTICO DEL PROBLEMA

### 1. Que deberia pasar (esperado):

**DIAGNOSTICO_PRINCIPAL en BD:** `TUMOR DE CELULAS GRANULARES`

### 2. Que esta pasando (actual):

**DIAGNOSTICO_PRINCIPAL en BD:** `LOS HALLAZGOS MORFOLOGICOS E INMUNOHISTOQUIMICOS FAVORECEN: TUMOR DE CELULAS GRANULARES`

### 3. Causa raiz:

El patron v6.5.74 (linea 4491 de medical_extractor.py) esta capturando el diagnostico pero esta **incluyendo el nombre del medico** porque el lookahead no esta funcionando correctamente con saltos de linea.

**Texto en OCR:**
```
LOS HALLAZGOS MORFOLOGICOS E INMUNOHISTOQUIMICOS FAVORECEN: TUMOR DE CELULAS
GRANULARES
CARLOS CAICEDO ESTRADA
```

**Patron actual:**
```python
r'(?:LOS\s+)?HALLAZGOS\s+MORFOL[OO]GICOS\s+E\s+INMUNOHISTOQU[II]MICOS\s+FAVORECEN\s*:\s*([A-ZAEIOUN][A-ZAEIOUN\s\-]{10,200})(?=\s*(?:POSITIVO|NEGATIVO|NANCY|ARMANDO|CARLOS|RESPONSABLE|M[EE]DICO|COMENTARIOS|---\s+P[AA]GINA|\.|$))'
```

**Problema:**
- El patron `[A-ZAEIOUN\s\-]{10,200}` es **greedy** (codicioso)
- Captura hasta 200 caracteres: "TUMOR DE CELULAS\nGRANULARES\nCARLOS CAICEDO ESTRADA"
- Cuando verifica el lookahead `(?=\s*(?:...CARLOS...))`, ya capturo "CARLOS"
- El lookahead solo confirma que **despues** hay mas texto, no detiene la captura

**Resultado capturado:**
```
TUMOR DE CELULAS
GRANULARES
CARLOS CAICEDO ESTRADA
```

**Resultado normalizado (linea 4495):**
```
TUMOR DE CELULAS GRANULARES CARLOS CAICEDO ESTRADA
```

---

## SOLUCION PROPUESTA

### Opcion 1: Hacer el patron non-greedy + limitar a saltos de linea

Modificar el patron para que:
1. Capture en modo non-greedy ({10,200}?)
2. Se detenga ANTES de un salto de linea seguido de un nombre (palabras en mayusculas)

**Patron mejorado:**
```python
r'(?:LOS\s+)?HALLAZGOS\s+MORFOL[OO]GICOS\s+E\s+INMUNOHISTOQU[II]MICOS\s+FAVORECEN\s*:\s*([A-ZAEIOUN](?:(?!\n[A-Z]{4,}\s+[A-Z]{4,})[A-ZAEIOUN\s\-\n]){10,200})'
```

**Explicacion:**
- `(?!\n[A-Z]{4,}\s+[A-Z]{4,})` - Negative lookahead: no capturar si sigue \n + nombre (2 palabras mayusculas)
- Esto detecta patrones como "\nCARLOS CAICEDO", "\nNANCY RODRIGUEZ", etc.

### Opcion 2: Post-procesamiento para limpiar nombres

Agregar limpieza despues de la captura:

```python
if match_morfologicos_e_ihq_directo:
    diag = match_morfologicos_e_ihq_directo.group(1).strip()
    diag = re.sub(r'\s+', ' ', diag)  # Normalizar espacios
    
    # NUEVO: Limpiar nombres de medicos (formato: NOMBRE APELLIDO APELLIDO)
    diag = re.sub(r'\s+[A-Z]{4,}\s+[A-Z]{4,}(?:\s+[A-Z]{4,})?$', '', diag)
    
    diag = diag.rstrip('.,;:-')
    if len(diag) > 10:
        return diag
```

**Ventaja:** Mas simple, menos probable de romper otros casos
**Desventaja:** Depende de que el nombre este al final del diagnostico

---

## RECOMENDACION

**Usar Opcion 2** (post-procesamiento) porque:
1. Mas simple de implementar
2. Menos riesgo de regresion (no cambia el patron complejo)
3. Funciona para cualquier nombre al final del diagnostico
4. Ya existe normalizacion de espacios en linea 4495

---

## VALIDACION PROPUESTA

**ANTES de aplicar la correccion:**
1. Auditar casos de referencia que usan este patron:
   - IHQ250263 (caso reportado)
   - Buscar otros casos con patron similar

**DESPUES de aplicar la correccion:**
1. Reprocesar IHQ250263 con FUNC-06
2. Validar score = 100%
3. Validar DIAGNOSTICO_PRINCIPAL = "TUMOR DE CELULAS GRANULARES" (sin prefijo ni nombre)
4. Validar casos de referencia (no regresion)

---

## CONCLUSION

El patron v6.5.74 esta capturando correctamente el patron "LOS HALLAZGOS... FAVORECEN:", pero esta incluyendo el nombre del medico porque el lookahead no funciona bien con saltos de linea. La solucion mas simple y segura es agregar post-procesamiento para limpiar nombres de medicos al final del diagnostico.

**Accion requerida:** Modificar medical_extractor.py linea 4494-4498 con limpieza de nombres.
