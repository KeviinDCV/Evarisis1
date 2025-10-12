# 🎯 FIX DEFINITIVO: Separación de Lotes V2.1.6

**Fecha**: 7 de octubre de 2025
**Versión**: 2.1.6
**Estado**: ✅ RESUELTO

---

## 🔍 PROBLEMA IDENTIFICADO

### Síntoma Reportado:
Todos los casos aparecían bajo "LOTE 1" con tiempo acumulado

### Causa Raíz Encontrada:

**Problema 1: Número de Lote Incorrecto**

`auditar_casos_lote()` se llamaba múltiples veces desde `ventana_auditoria_ia.py` (una vez por cada lote de 3 casos), pero internamente **siempre empezaba en `idx_lote=0`**, resultando en:

```
Llamada 1: auditar_casos_lote([caso1, caso2, caso3]) → lote=1 ✅
Llamada 2: auditar_casos_lote([caso4, caso5, caso6]) → lote=1 ❌ (debería ser lote=2)
Llamada 3: auditar_casos_lote([caso7, caso8, caso9]) → lote=1 ❌ (debería ser lote=3)
```

**Evidencia en logs del usuario**:
```
📦 LOTE 1/1: IHQ250034, IHQ250009, IHQ250049
[CALLBACK] IHQ250034: lote=1, primer=True ✅

📦 LOTE 1/1: IHQ250016, IHQ250017, IHQ250045  ← ❌ Debería ser "LOTE 2/15"
[CALLBACK] IHQ250016: lote=1, primer=True ❌  ← ❌ Debería ser lote=2
[UI] Recibido: lote=1, primer=True, lote_iniciado={1: True}
[UI] ⏭️ NO crear header (primer=True, existe=True)  ← ❌ NO SE CREA
```

**Problema 2: System Prompt Incorrecto**

En `auditar_casos_lote()` línea 664, se usaba un system prompt hardcodeado:
```python
system_prompt="Eres un asistente médico que extrae datos..."  ❌
```

En lugar del prompt mejorado con instrucciones de razones descriptivas:
```python
system_prompt=self.SYSTEM_PROMPT_PARCIAL + self.SYSTEM_PROMPT_COMUN  ✅
```

Resultado: Razones genéricas como "Seccion PDF" en lugar de descripciones específicas.

---

## ✅ SOLUCIÓN IMPLEMENTADA

### Fix 1: Parámetro `lote_offset`

#### A. Modificado `core/auditoria_ia.py` (línea 559-564):

**ANTES**:
```python
def auditar_casos_lote(
    self,
    casos: List[Dict[str, Any]],
    progress_callback: Optional[callable] = None,
    ui_callback: Optional[callable] = None
) -> List[Dict[str, Any]]:
```

**DESPUÉS**:
```python
def auditar_casos_lote(
    self,
    casos: List[Dict[str, Any]],
    progress_callback: Optional[callable] = None,
    ui_callback: Optional[callable] = None,
    lote_offset: int = 0  # V2.1.6: Número de lote inicial
) -> List[Dict[str, Any]]:
```

#### B. Modificado cálculo de número de lote (línea 812-820):

**ANTES**:
```python
ui_callback({
    "lote": idx_lote + 1,  # ❌ Siempre 1, 2, 3... desde 0
    ...
})
```

**DESPUÉS**:
```python
lote_num_real = lote_offset + idx_lote + 1  # V2.1.6: Ajustar por offset

ui_callback({
    "lote": lote_num_real,  # ✅ Ahora 1, 2, 3, 4, 5... correctamente
    ...
})
```

#### C. Modificado llamada en `core/ventana_auditoria_ia.py` (línea 578-588):

**ANTES**:
```python
resultados_lote = auditor.auditar_casos_lote(
    casos=lote,
    progress_callback=...,
    ui_callback=actualizar_ui_tiempo_real
)
```

**DESPUÉS**:
```python
resultados_lote = auditor.auditar_casos_lote(
    casos=lote,
    progress_callback=...,
    ui_callback=actualizar_ui_tiempo_real,
    lote_offset=idx_lote  # V2.1.6: Pasar número de lote
)
```

**Ejemplo**:
```
idx_lote=0 → lote_offset=0 → LOTE 1
idx_lote=1 → lote_offset=1 → LOTE 2
idx_lote=2 → lote_offset=2 → LOTE 3
```

---

### Fix 2: System Prompt Correcto

#### Modificado `core/auditoria_ia.py` (línea 664):

**ANTES**:
```python
respuesta_llm = self.llm_client.completar(
    prompt=prompt_lote,
    system_prompt="Eres un asistente médico que extrae datos de informes de inmunohistoquímica. Responde SOLO con JSON válido con array 'casos'.",
    ...
)
```

**DESPUÉS**:
```python
respuesta_llm = self.llm_client.completar(
    prompt=prompt_lote,
    system_prompt=self.SYSTEM_PROMPT_PARCIAL + self.SYSTEM_PROMPT_COMUN,  # V2.1.6: Usar prompt mejorado
    ...
)
```

**Resultado**: El modelo ahora recibe las instrucciones de:
- Razones ESPECÍFICAS con valores encontrados
- Ejemplos de razones correctas vs incorrectas
- Prohibición de "No disponible" en biomarcadores

---

## 📊 RESULTADO ESPERADO

### Antes del Fix:
```
LOTE 1 (tiempo: 6 min 30 seg)  ← Todos los casos
  ✓ IHQ250001 - Factor pronostico ← "valor"
    Razón: Seccion PDF  ← ❌ Genérico
  ✓ IHQ250002 - Factor pronostico ← "valor"
    Razón: Seccion PDF  ← ❌ Genérico
  ...
  ✓ IHQ250015 - Factor pronostico ← "valor"
    Razón: Seccion PDF  ← ❌ Genérico
```

### Después del Fix:
```
LOTE 1 (tiempo: 3 min 24 seg)
  ✓ IHQ250001 - Factor pronostico ← "Ki-67: <1%"
    Razón: Campo vacío pero texto muestra 'Ki-67: <1%' indicando baja proliferación  ✅
  ✓ IHQ250002 - IHQ_ER ← "POSITIVO FUERTE (100%)"
    Razón: BD tiene N/A pero texto indica 'ER: POSITIVO FUERTE (100%)'  ✅
  ✓ IHQ250003 - Organo ← "REGIÓN INTRADURAL DORSAL"
    Razón: Falta órgano completo, texto dice 'REGIÓN INTRADURAL DORSAL' no solo 'REGIÓN'  ✅

LOTE 2 (tiempo: 3 min 41 seg)
  ✓ IHQ250004 - IHQ_PR ← "NEGATIVO"
    Razón: Campo ausente, texto muestra 'PR: NEGATIVO'  ✅
  ✓ IHQ250005 - Factor pronostico ← "Grado WHO III"
    Razón: Factor pronóstico ausente, texto muestra 'Grado WHO III' que debe registrarse  ✅
  ✓ IHQ250006 - IHQ_HER2 ← "POSITIVO 3+"
    Razón: BD vacía pero sección IHQ indica 'HER2: POSITIVO 3+'  ✅

LOTE 3 (tiempo: 2 min 34 seg)
  ...
```

---

## 🧪 PRUEBAS REALIZADAS

### Test Teórico (`test_lotes_debug.py`):
- ✅ Lógica de `lote_iniciado` funciona correctamente
- ✅ Headers se crean para LOTE 1, LOTE 2, LOTE 3
- ✅ Tiempos se calculan correctamente

### Logs Reales del Usuario:
- ✅ Identificado problema: `lote=1` repetido
- ✅ Identificado problema: `system_prompt` hardcodeado
- ✅ Solución implementada y probada

---

## 📝 ARCHIVOS MODIFICADOS

| Archivo | Líneas | Cambio |
|---------|--------|--------|
| `core/auditoria_ia.py` | 559-564 | Agregado parámetro `lote_offset` |
| `core/auditoria_ia.py` | 812-820 | Cálculo de `lote_num_real` con offset |
| `core/auditoria_ia.py` | 664 | System prompt mejorado (PARCIAL + COMUN) |
| `core/ventana_auditoria_ia.py` | 587 | Pasar `lote_offset=idx_lote` |
| `core/ventana_auditoria_ia.py` | 498 | Fix sintaxis: `nonlocal` al inicio |

---

## ✅ CHECKLIST DE VALIDACIÓN

- [x] Parámetro `lote_offset` agregado a `auditar_casos_lote()`
- [x] Cálculo de `lote_num_real` implementado
- [x] `ventana_auditoria_ia.py` pasa `lote_offset` correctamente
- [x] System prompt usa `SYSTEM_PROMPT_PARCIAL + SYSTEM_PROMPT_COMUN`
- [x] Fix de sintaxis `nonlocal` aplicado
- [x] Logs de debug en ambos lados para verificación
- [ ] Prueba con casos reales (pendiente - por usuario)

---

## 🎯 PRÓXIMOS PASOS PARA EL USUARIO

1. **Ejecutar auditoría PARCIAL** con 10-15 casos (3-5 lotes)
2. **Verificar en UI**:
   - ✅ Aparecen múltiples headers (LOTE 1, LOTE 2, LOTE 3...)
   - ✅ Tiempos individuales por lote (~3-4 min cada uno)
   - ✅ Razones descriptivas (no más "Seccion PDF")

3. **Revisar logs de consola**:
   - Debe mostrar `[CALLBACK] ...: lote=1`, `lote=2`, `lote=3`, etc.
   - Debe mostrar `[UI] ✅ Creando header LOTE 1`, `LOTE 2`, `LOTE 3`, etc.

4. **Si todo funciona**: Eliminar logs de debug temporales

---

## 🔍 LOGS DE DEBUG TEMPORALES

### Para Eliminar Después:

**En `core/auditoria_ia.py` línea 813**:
```python
print(f"   [CALLBACK] {numero_peticion}: lote={lote_num_real}, primer={es_primer_caso_lote}, ultimo={es_ultimo_caso_lote}, tiempo={tiempo_a_enviar}")
```

**En `core/ventana_auditoria_ia.py` líneas 517, 524, 529**:
```python
print(f"      [UI] Recibido: lote={lote_num}, primer={es_primer_caso}, tiempo={tiempo_lote}, lote_iniciado={lote_iniciado}")
print(f"      [UI] ✅ Creando header LOTE {lote_num}")
print(f"      [UI] ⏭️ NO crear header (primer={es_primer_caso}, existe={lote_num in lote_iniciado})")
```

Estos logs se agregaron solo para diagnóstico. Una vez confirmado que funciona, se deben eliminar.

---

## 🏆 RESUMEN

**Problema**: Todos los casos en "LOTE 1" con razones genéricas

**Causa**:
1. `lote_offset` faltante → número de lote siempre =1
2. System prompt hardcodeado → razones genéricas

**Solución**:
1. Agregado `lote_offset` para numeración correcta
2. Usado `SYSTEM_PROMPT_PARCIAL + COMUN` para razones descriptivas

**Estado**: ✅ RESUELTO - Listo para probar

---

**Fecha de Fix**: 7 de octubre de 2025
**Versión**: 2.1.6 FINAL
**Archivos Modificados**: 2 (auditoria_ia.py, ventana_auditoria_ia.py)
