# PLAN DE VALIDACION ANTI-REGRESION - FIX P40 v6.4.60

## RESUMEN

**Total casos con P40 auditados:** 33 casos
**Caso de prueba validado:** IHQ250200 (100% ✅)
**Patron modificado:** v6.4.60 - "marcacion celular... con p40"

**Objetivo:** Validar que el nuevo patron especifico NO rompe casos previos con P40 que ya funcionaban correctamente.

---

## CASOS DE REFERENCIA IDENTIFICADOS (33 total)

### Casos con Score 100% (Candidatos para validacion anti-regresion)

| Caso | Score | Estudios con P40 |
|------|-------|------------------|
| IHQ250001 | 100% | P16, P40 |
| IHQ250020 | 100% | P16, P40 |
| IHQ250027 | 100% | Ki-67, P16, P40 |
| IHQ250041 | 100% | P40 |
| IHQ250045 | 100% | CK20, CK7, Ki-67, P40, TTF1 |
| IHQ250062 | 100% | P40, TTF-1 |
| IHQ250063 | 100% | P16, P40 |
| IHQ250064 | 100% | P16, P40 |
| IHQ250067 | 100% | P16, P40 |
| IHQ250069 | 100% | (10+ biomarcadores con P40) |
| IHQ250073 | 100% | CK7, CK20, TTF-1, P40, NAPSINA A |
| IHQ250076 | 100% | (12+ biomarcadores con P40) |
| IHQ250087 | 100% | SOX 10, CKAE1E3, CD34, DESMINA, P40, ... |
| IHQ250142 | 100% | P40 |

### Casos con Score < 100% (Revisar si P40 es la causa)

| Caso | Score | Estudios con P40 |
|------|-------|------------------|
| IHQ250003 | 88.9% | CK7, CK20, TTF-1, NAPSINA A, P40 |
| IHQ250005 | 77.8% | (10+ biomarcadores con P40) |
| IHQ250016 | 88.9% | P16, P40 |
| IHQ250033 | 88.9% | TTF-1, GATA 3, ..., P40, ... |
| IHQ250146 | 88.9% | CKAE1AE3, P40, P16, Ki-67 |

---

## ESTRATEGIA DE VALIDACION ANTI-REGRESION

### FASE 1: Validacion Minima (3 casos representativos)

**Seleccion estrategica:**
1. **IHQ250001** - Caso simple (P16, P40) - Score 100%
2. **IHQ250062** - Caso con TTF-1 + P40 - Score 100%
3. **IHQ250073** - Caso con 5 biomarcadores incluye P40 - Score 100%

**Comando:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250001 --func-06
python herramientas_ia/auditor_sistema.py IHQ250062 --func-06
python herramientas_ia/auditor_sistema.py IHQ250073 --func-06
```

**Criterio de exito:**
- ✅ Los 3 casos mantienen score 100%
- ✅ P40 sigue extrayendose correctamente
- ✅ Ningun otro biomarcador se afecta

### FASE 2: Validacion Extendida (5 casos adicionales)

**Seleccion adicional:**
4. **IHQ250041** - Caso solo con P40 - Score 100%
5. **IHQ250069** - Caso complejo (10+ biomarcadores) - Score 100%
6. **IHQ250003** - Caso con 88.9% (revisar si P40 es la causa)
7. **IHQ250005** - Caso con 77.8% (revisar si P40 es la causa)
8. **IHQ250146** - Caso con 88.9% (P40 + P16 + Ki-67 + CKAE1AE3)

**Comando:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250041 --func-06
python herramientas_ia/auditor_sistema.py IHQ250069 --func-06
python herramientas_ia/auditor_sistema.py IHQ250003 --func-06
python herramientas_ia/auditor_sistema.py IHQ250005 --func-06
python herramientas_ia/auditor_sistema.py IHQ250146 --func-06
```

**Criterio de exito:**
- ✅ Casos con 100% mantienen score
- ✅ Casos con <100% NO empeoran (pueden mejorar si P40 era el problema)
- ✅ P40 sigue extrayendose correctamente en todos

### FASE 3: Validacion Masiva (Opcional - 33 casos completos)

**Solo si:**
- Fases 1 y 2 pasan exitosamente
- Hay tiempo/recursos para validacion exhaustiva
- Se quiere confirmar 100% que no hay regresion

**Comando (script batch):**
```bash
# Todos los casos con P40 identificados
for caso in IHQ250001 IHQ250003 IHQ250005 IHQ250016 IHQ250020 IHQ250027 IHQ250033 IHQ250041 IHQ250045 IHQ250062 IHQ250063 IHQ250064 IHQ250067 IHQ250069 IHQ250073 IHQ250076 IHQ250087 IHQ250142 IHQ250146 ...; do
    python herramientas_ia/auditor_sistema.py $caso --func-06
done
```

---

## FORMATO DE REPORTE DE VALIDACION

Para cada caso validado, documentar:

```
CASO: IHQXXXXXX
ANTES (v6.4.59): Score YY.Y%
DESPUES (v6.4.60): Score ZZ.Z%
CAMBIO: +/- D.D%

P40 ANTES: [valor si existe]
P40 DESPUES: [valor reprocesado]

REGRESION: SI/NO
MEJORA: SI/NO

NOTAS: [observaciones especificas]
```

---

## CRITERIOS DE DECISION

### SI NO HAY REGRESION (todos los casos mantienen/mejoran)

✅ **APROBAR FIX v6.4.60**
- Incrementar version a v6.4.61
- Documentar en CHANGELOG con casos de referencia
- Agregar IHQ250200 + casos validados a lista de referencia

### SI HAY REGRESION (algún caso empeora)

❌ **REVERTIR FIX v6.4.60**
- Volver a v6.4.59 para casos problemáticos
- Replantear estrategia:
  - Opcion 1: Patron mas especifico con condiciones adicionales
  - Opcion 2: Fallback a patron generico si especifico no aplica
  - Opcion 3: Agregar contexto adicional al patron

### SI HAY MEJORA SIN REGRESION

✅✅ **FIX EXITOSO CON BONUS**
- Aprobar + documentar casos mejorados
- Reportar mejora en precision global

---

## TIMELINE PROPUESTO

**FASE 1 (Validacion Minima):**
- Duracion: ~10 minutos (3 casos)
- Prioridad: ALTA
- Decision: Aprobar/Revisar FIX

**FASE 2 (Validacion Extendida):**
- Duracion: ~20 minutos (5 casos adicionales)
- Prioridad: MEDIA
- Decision: Confirmar estabilidad

**FASE 3 (Validacion Masiva):**
- Duracion: ~2 horas (33 casos completos)
- Prioridad: BAJA (opcional)
- Decision: Confirmacion exhaustiva

---

## PROXIMOS PASOS INMEDIATOS

1. ✅ **COMPLETADO:** Validar caso de prueba IHQ250200 (Score 100%)
2. 📋 **PENDIENTE:** Ejecutar FASE 1 (3 casos representativos)
3. 📋 **PENDIENTE:** Analizar resultados FASE 1
4. 📋 **PENDIENTE:** Decidir si continuar con FASE 2

**Comando para iniciar FASE 1:**
```bash
# Validar 3 casos representativos
python herramientas_ia/auditor_sistema.py IHQ250001 --func-06
python herramientas_ia/auditor_sistema.py IHQ250062 --func-06
python herramientas_ia/auditor_sistema.py IHQ250073 --func-06

# Revisar scores en auditorias generadas
```

---

## ARCHIVOS RELACIONADOS

- `VALIDACION_FIX_P40_v6.4.60_IHQ250200.md` - Validacion caso de prueba
- `PLAN_VALIDACION_ANTI_REGRESION_P40_v6.4.60.md` - Este plan (33 casos identificados)
- `core/extractors/biomarker_extractor.py` - Archivo con fix v6.4.60

---

**Fecha:** 2026-01-09
**Casos identificados:** 33 casos con P40
**Casos validados:** 1/33 (IHQ250200 ✅)
**Pendientes FASE 1:** 3 casos (IHQ250001, IHQ250062, IHQ250073)
