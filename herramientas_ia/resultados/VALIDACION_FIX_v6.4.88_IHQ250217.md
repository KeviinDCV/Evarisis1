# VALIDACION FIX v6.4.88 - IHQ250217

**Fecha:** 2026-01-19  
**Caso:** IHQ250217  
**Version:** v6.4.88  
**Estado:** EXITOSO

---

## FIXES APLICADOS

### 1. biomarker_extractor.py
**Problema corregido:** Patron "Son negativas para" capturaba secciones siguientes como DIAGNOSTICO  
**Solucion:** Terminador mejorado para delimitar correctamente fin de lista de biomarcadores  
**Impacto:** Evita captura de texto erroneo despues de lista de negativos

### 2. unified_extractor.py
**Problema corregido:** Claves con prefijo IHQ_ (IHQ_PAX8, IHQ_CDX2, etc.) no se normalizaban  
**Solucion:** Agregado soporte para claves con prefijo IHQ_  
**Impacto:** Permite mapeo correcto de biomarcadores con formato IHQ_ en extractores

---

## VALIDACION DE REPROCESAMIENTO (FUNC-06)

| Metrica | Valor |
|---------|-------|
| **Estado** | EXITOSO |
| **Score final** | 100% |
| **Casos procesados** | 50 |
| **PDF procesado** | IHQ DEL 212 AL 262.pdf |
| **Validaciones OK** | 9/9 |
| **Warnings** | 0 |
| **Errores** | 0 |

---

## VALIDACION ESPECIFICA - BIOMARCADORES

### IHQ_PAX8 (FIX PRINCIPAL)
| Aspecto | Valor |
|---------|-------|
| **ANTES** | NO MENCIONADO |
| **DESPUES** | NEGATIVO |
| **OCR dice** | "Son negativas para CK20, CDX2, TTF-1 y PAX-8" |
| **Resultado** | **FIX EXITOSO** - Ahora se extrae correctamente |
| **Impacto** | Correccion critica aplicada |

### Biomarcadores Correctos

| Biomarcador | Valor BD | OCR | Estado |
|-------------|----------|-----|--------|
| IHQ_CK7 | POSITIVO | "positivas para CK7" | OK |
| IHQ_CK20 | NEGATIVO | "negativas para CK20" | OK |
| IHQ_CK19 | POSITIVO | "positivas para CK19" | OK |
| IHQ_CDX2 | NEGATIVO | "negativas para CDX2" | OK |
| IHQ_PAX8 | NEGATIVO | "negativas para PAX-8" | **OK - CORREGIDO** |

**Total: 5/7 biomarcadores OK (71.4%)**

### Biomarcadores Pendientes

| Biomarcador | Problema | OCR dice | Accion requerida |
|-------------|----------|----------|------------------|
| **IHQ_TTF-1** | No se guarda en BD | "negativas para TTF-1" | Investigar mapeo |
| **IHQ_CA19-9** | No se guarda en BD | "positivas para CA19-9" | Investigar mapeo |

**Nota:** Estos biomarcadores aparecen en OCR pero no se guardan en BD. Posible problema de mapeo en database_manager.py o validation_checker.py.

---

## VALIDACION ANTI-REGRESION

**Casos de referencia validados:** Ninguno  
**Razon:** No se identificaron casos de referencia previos con PAX8  

**Recomendacion:** Buscar casos con PAX8 procesados antes de v6.4.88 para validar que el fix no introdujo regresiones.

---

## CONCLUSION

### FIX PRINCIPAL: EXITOSO

- **IHQ_PAX8** ahora se extrae correctamente como **NEGATIVO** (antes: NO MENCIONADO)
- Score del caso: **100%** (9/9 validaciones OK)
- Regresion: **NO DETECTADA** (sin casos de referencia para comparar)

### PENDIENTES

1. **Investigar por que TTF-1 no se guarda en BD**
   - Aparece en OCR como NEGATIVO
   - No se encuentra columna IHQ_TTF-1 en BD o mapeo incorrecto

2. **Investigar por que CA19-9 no se guarda en BD**
   - Aparece en OCR como POSITIVO
   - No se encuentra columna IHQ_CA19-9 en BD o mapeo incorrecto

### SIGUIENTES PASOS

1. Verificar existencia de columnas IHQ_TTF-1 e IHQ_CA19-9 en database_manager.py
2. Verificar mapeos en validation_checker.py (BIOMARKER_ALIAS_MAP)
3. Si no existen, usar FUNC-03 para agregarlos:
   ```python
   auditor.agregar_biomarcador('TTF-1', ['TTF1', 'TTF-1', 'TTF 1'])
   auditor.agregar_biomarcador('CA19-9', ['CA19-9', 'CA 19-9', 'CA199'])
   ```
4. Reprocesar caso IHQ250217 con FUNC-06 para validar que ahora se extraen

---

**Reporte generado:** 2026-01-19 01:08:45  
**Herramienta:** auditor_sistema.py FUNC-06 + validacion manual  
**Agente:** data-auditor
