# DIAGNÓSTICO v6.4.81 - IHQ250214: DIAGNOSTICO_COLORACION Truncado

**Fecha:** 2026-01-17
**Caso problemático:** IHQ250214
**Score actual:** 88.9% (WARNING)
**Versión del extractor:** v6.4.81

---

## 🔴 PROBLEMA DETECTADO

### Extracción Actual (TRUNCADA):
```
"M2501390 QUE CORRESPONDE A \"ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL"
```
- Longitud: 79 caracteres
- Falta: "PERITONEO VISCERAL" (diagnóstico incompleto)
- Problema: Contiene bloque M2501390 (debería removerse)

### Valor Esperado (OCR completo):
```
"ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL PERITONEO VISCERAL"
```
- Longitud: ~72 caracteres
- Sin bloque M, solo diagnóstico limpio

---

## 🔍 CAUSA RAÍZ

**Archivo:** `core/extractors/medical_extractor.py`
**Línea:** 881
**Patrón problemático:**

```python
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"(.{10,300}?)\."'
```

### Por qué falla:

1. **Patrón `(.{10,300}?)\."`:**
   - Busca: 10-300 caracteres + PUNTO + COMILLA DE CIERRE
   - Problema: El diagnóstico tiene un salto de línea antes del punto final
   
2. **Texto en OCR:**
   ```
   M2501390 que corresponde a "ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL
   PERITONEO VISCERAL. Previa valoración...
   ```

3. **Regex non-greedy `{10,300}?`:**
   - Se detiene en el primer match mínimo
   - No captura después del salto de línea
   - Corta el diagnóstico a la mitad

4. **Falta normalización:**
   - El patrón captura el bloque M completo
   - Debería extraer SOLO el contenido entre comillas

---

## ✅ SOLUCIÓN

### Opción 1: Patrón sin punto obligatorio (RECOMENDADA)

**Cambiar línea 881:**

```python
# V6.4.82 FIX IHQ250214: Capturar diagnóstico completo hasta comilla de cierre
# Solución: No requerir punto antes de comilla, permitir saltos de línea
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"([^"]{10,300})"'
```

**Ventajas:**
- Captura TODO entre comillas (permite saltos de línea, puntos intermedios)
- `[^"]` = Cualquier carácter excepto comillas
- Se detiene automáticamente en la comilla de cierre
- Límite de 300 caracteres se mantiene

**Después de capturar, el código ya normaliza:**
```python
diagnostico_directo = ' '.join(diagnostico_directo.split())  # Ya está en línea 887
```

### Opción 2: Patrón con punto opcional

```python
patron_m_directo = r'M[\dA-Z-]+\s+que\s+corresponden?\s+a\s+"(.{10,300}?)\.?"'
```

**Desventaja:** Mantiene `{10,300}?` non-greedy, puede seguir cortando antes de tiempo.

---

## 🔬 VALIDACIÓN POST-CORRECCIÓN

### Comando para reprocesar:
```python
from herramientas_ia.auditor_sistema import AuditorSistema
auditor = AuditorSistema()
auditor.reprocesar_caso_completo('IHQ250214')
```

### Resultado esperado:
- **DIAGNOSTICO_COLORACION:** `"ADENOCARCINOMA MUCINOSO INVASIVO CON COMPROMISO DEL PERITONEO VISCERAL"`
- **Longitud:** ~72 caracteres (dentro del límite de 300)
- **Sin bloque M:** Solo diagnóstico limpio
- **Score:** 88.9% → 100% ✅

---

## 📋 ANTI-REGRESIÓN

### Casos de referencia a validar:

**Casos con diagnóstico entre comillas directas:**
1. IHQ250214 (este caso - diagnóstico con salto de línea)
2. IHQ250995 (caso original v4.2.10)
3. IHQ250999 (caso original v4.2.10)

**Patrón del caso:**
```
M[NUMERO] que corresponde a "[DIAGNOSTICO]"
```

### Validación obligatoria:
```bash
# Reprocesar IHQ250214
python herramientas_ia/auditor_sistema.py IHQ250214 --func-06

# Validar casos de referencia NO se rompan
python herramientas_ia/auditor_sistema.py IHQ250995 --inteligente
python herramientas_ia/auditor_sistema.py IHQ250999 --inteligente
```

---

## 🚨 CRÍTICO: Limpieza del Bloque M

**Problema adicional detectado:**

El patrón actual captura:
```
M2501390 QUE CORRESPONDE A "ADENOCARCINOMA..."
```

Debería capturar SOLO:
```
ADENOCARCINOMA...
```

**Solución en línea 885:**

```python
if match_m_directo:
    diagnostico_directo = match_m_directo.group(1).strip()  # group(1) = SOLO contenido entre comillas
    diagnostico_directo = ' '.join(diagnostico_directo.split())  # Ya normaliza
    diagnostico_directo = diagnostico_directo.upper()  # Ya convierte a mayúsculas
```

El `group(1)` ya captura SOLO el contenido entre comillas (sin el bloque M), por lo que la limpieza es correcta.

**El problema es que el patrón se está cortando antes de la comilla de cierre.**

---

## 📊 RESUMEN EJECUTIVO

| Aspecto | Estado Actual | Estado Esperado |
|---------|--------------|-----------------|
| Patrón regex | `(.{10,300}?)\."` | `([^"]{10,300})"` |
| Captura | Truncada (79 chars) | Completa (~72 chars) |
| Bloque M | Incluido | Removido ✅ (group(1)) |
| Saltos de línea | Rompen el patrón | Permitidos |
| Score | 88.9% (WARNING) | 100% (OK) |

---

**Acción requerida:**
Modificar línea 881 en `medical_extractor.py` con el patrón recomendado (Opción 1).

