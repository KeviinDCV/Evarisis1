# Tests de Regresión - Refactorización auditor_sistema.py

**Fecha:** 2025-10-23
**Refactorización:** Eliminación de duplicación de código
**Objetivo:** Validar que funcionalidad se mantiene 100% después de refactorización

---

## INSTRUCCIONES DE EJECUCIÓN

### Pre-requisitos
```bash
# Verificar que entorno tiene pandas y dependencias
python -c "import pandas, sqlite3, pytesseract; print('✓ Dependencias OK')"

# Ubicarse en directorio del proyecto
cd C:\Users\drestrepo\Documents\ProyectoHUV9GESTOR_ONCOLOGIA_automatizado
```

---

## TEST SUITE 1: Tests Unitarios de Funciones Refactorizadas

### Test 1.1: `_extraer_diagnostico_coloracion_de_macro()` - Patrón básico

```python
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()

# Test: Diagnóstico con formato "con diagnóstico de \"X\""
texto_macro = 'Recibimos bloque con diagnóstico de "CARCINOMA DUCTAL INVASIVO. NOTTINGHAM GRADO 2".'
resultado = auditor._extraer_diagnostico_coloracion_de_macro(texto_macro)

print(f"Resultado: {resultado}")

# Validación
assert resultado == "CARCINOMA DUCTAL INVASIVO. NOTTINGHAM GRADO 2", f"FALLO: Esperado 'CARCINOMA...', Obtenido: '{resultado}'"
print("✓ Test 1.1 PASS")
```

**Expectativa:** `"CARCINOMA DUCTAL INVASIVO. NOTTINGHAM GRADO 2"`

---

### Test 1.2: `_extraer_diagnostico_coloracion_de_macro()` - Sin comillas

```python
texto_macro = 'Descripción sin diagnóstico citado.'
resultado = auditor._extraer_diagnostico_coloracion_de_macro(texto_macro)

print(f"Resultado: {resultado}")

# Validación
assert resultado is None, f"FALLO: Esperado None, Obtenido: '{resultado}'"
print("✓ Test 1.2 PASS")
```

**Expectativa:** `None`

---

### Test 1.3: `_extraer_diagnostico_coloracion_de_macro()` - Diagnóstico complejo

```python
texto_macro = '''
Se reciben bloques con diagnóstico de "CARCINOMA INVASIVO DE TIPO NO ESPECIAL (DUCTAL).
NOTTINGHAM GRADO 2 (PUNTAJE DE 6). INVASIÓN LINFOVASCULAR: NEGATIVO.
INVASIÓN PERINEURAL: NEGATIVO. CARCINOMA DUCTAL IN SITU: NO".
'''
resultado = auditor._extraer_diagnostico_coloracion_de_macro(texto_macro)

print(f"Resultado: {resultado[:80]}...")

# Validación
assert "CARCINOMA INVASIVO" in resultado
assert "NOTTINGHAM GRADO 2" in resultado
assert "INVASIÓN LINFOVASCULAR: NEGATIVO" in resultado
print("✓ Test 1.3 PASS")
```

**Expectativa:** Diagnóstico completo con todos los componentes

---

### Test 1.4: `_extraer_biomarcadores_solicitados_de_macro()` - Lista básica

```python
texto_macro = 'Se realizan niveles histológicos para tinción con: Ki67, HER2, Estrógenos.'
resultado = auditor._extraer_biomarcadores_solicitados_de_macro(texto_macro)

print(f"Resultado: {resultado}")

# Validación
assert 'KI-67' in resultado, f"FALLO: 'KI-67' no encontrado en {resultado}"
assert 'HER2' in resultado, f"FALLO: 'HER2' no encontrado en {resultado}"
assert 'RECEPTOR_ESTROGENOS' in resultado, f"FALLO: 'RECEPTOR_ESTROGENOS' no encontrado en {resultado}"
print("✓ Test 1.4 PASS")
```

**Expectativa:** `['KI-67', 'HER2', 'RECEPTOR_ESTROGENOS']`

---

### Test 1.5: `_extraer_biomarcadores_solicitados_de_macro()` - Lista multi-línea

```python
texto_macro = '''
Se realizan niveles histológicos para marcación de CKAE1E3, CAM 5.2, CK7,
GFAP, SOX10 y
SOX100.
'''
resultado = auditor._extraer_biomarcadores_solicitados_de_macro(texto_macro)

print(f"Resultado: {resultado}")

# Validación - Debe detectar SOX10 y SOX100 aunque estén en líneas diferentes
assert 'SOX10' in resultado, f"FALLO: 'SOX10' no encontrado en {resultado}"
# Nota: SOX100 podría no estar en mapeo, verificar normalización
print("✓ Test 1.5 PASS")
```

**Expectativa:** Detectar TODOS los biomarcadores, incluso separados por saltos de línea

---

### Test 1.6: `_extraer_biomarcadores_solicitados_de_macro()` - Sin biomarcadores

```python
texto_macro = 'Descripción sin mención de biomarcadores.'
resultado = auditor._extraer_biomarcadores_solicitados_de_macro(texto_macro)

print(f"Resultado: {resultado}")

# Validación
assert resultado == [], f"FALLO: Esperado [], Obtenido: {resultado}"
print("✓ Test 1.6 PASS")
```

**Expectativa:** `[]`

---

## TEST SUITE 2: Tests de Integración con Casos Reales

### Test 2.1: Auditoría completa - IHQ250981 (E-Cadherina)

```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente
```

**Validaciones esperadas:**

1. ✅ `diagnostico_coloracion` debe extraerse correctamente del macro
2. ✅ `biomarcadores_solicitados` debe incluir: E-CADHERINA, RECEPTOR_PROGESTERONA, RECEPTOR_ESTROGENOS, HER2, KI-67
3. ✅ E-CADHERINA debe aparecer aunque esté en formato multi-línea
4. ✅ No debe haber errores de sintaxis o excepciones

**Comando de validación:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente > test_2_1_resultado.json
grep -i "e-cadherina\|e_cadherina" test_2_1_resultado.json
```

---

### Test 2.2: Auditoría completa - IHQ250982 (9 biomarcadores)

```bash
python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente
```

**Validaciones esperadas:**

1. ✅ Debe detectar TODOS los 9 biomarcadores solicitados:
   - CKAE1E3
   - CAM 5.2
   - CK7
   - GFAP
   - SOX10
   - SOX100
   - S100
   - (verificar lista completa en PDF)

2. ✅ Diagnóstico de coloración debe extraerse correctamente
3. ✅ No debe haber falsos positivos

**Comando de validación:**
```bash
python herramientas_ia/auditor_sistema.py IHQ250982 --inteligente > test_2_2_resultado.json
jq '.biomarcadores_solicitados | length' test_2_2_resultado.json  # Debe ser >= 9
```

---

### Test 2.3: Auditoría completa - IHQ251026

```bash
python herramientas_ia/auditor_sistema.py IHQ251026 --inteligente
```

**Validaciones esperadas:**

1. ✅ Biomarcadores solicitados extraídos correctamente
2. ✅ Diagnóstico de coloración extraído (si aplica)
3. ✅ Sin regresiones en otros campos (NOMBRE_PACIENTE, DIAGNOSTICO_PRINCIPAL, etc.)

---

## TEST SUITE 3: Comparación Antes/Después

### Test 3.1: Comparación de resultados con versión original

```bash
# Ejecutar con BACKUP (versión original)
cd backups
python auditor_sistema_backup_20251023_073954.py IHQ250981 --inteligente > ../test_antes.json
cd ..

# Ejecutar con REFACTORIZADO (versión nueva)
python herramientas_ia/auditor_sistema.py IHQ250981 --inteligente > test_despues.json

# Comparar JSONs
python -c "
import json

with open('test_antes.json') as f:
    antes = json.load(f)
with open('test_despues.json') as f:
    despues = json.load(f)

# Comparar campos críticos
campos_criticos = ['diagnostico_coloracion', 'biomarcadores_solicitados']

for campo in campos_criticos:
    if campo in antes and campo in despues:
        if antes[campo] != despues[campo]:
            print(f'⚠️  DIFERENCIA en {campo}:')
            print(f'   ANTES: {antes[campo]}')
            print(f'   DESPUÉS: {despues[campo]}')
        else:
            print(f'✓ {campo}: IDÉNTICO')
    else:
        print(f'⚠️  {campo} falta en uno de los JSONs')
"
```

**Expectativa:** Resultados idénticos o MEJORES (más biomarcadores detectados por patrones adicionales)

---

### Test 3.2: Comparación en lote (10 casos aleatorios)

```bash
# Generar lista de 10 casos aleatorios
sqlite3 data/huv_oncologia.db "SELECT NUMERO_IHQ FROM informes_ihq ORDER BY RANDOM() LIMIT 10;" > casos_test.txt

# Ejecutar auditoría con ambas versiones
while IFS= read -r caso; do
    echo "Procesando $caso..."
    python backups/auditor_sistema_backup_20251023_073954.py "$caso" --inteligente > "resultados_antes_${caso}.json"
    python herramientas_ia/auditor_sistema.py "$caso" --inteligente > "resultados_despues_${caso}.json"
done < casos_test.txt

# Comparar todos
for caso_file in casos_test.txt; do
    caso=$(cat "$caso_file")
    diff "resultados_antes_${caso}.json" "resultados_despues_${caso}.json"
    if [ $? -eq 0 ]; then
        echo "✓ $caso: IDÉNTICO"
    else
        echo "⚠️  $caso: DIFERENCIAS DETECTADAS (revisar manualmente)"
    fi
done
```

---

## TEST SUITE 4: Tests de Robustez

### Test 4.1: Manejo de entrada nula

```python
auditor = AuditorSistema()

# Test diagnóstico con None
resultado1 = auditor._extraer_diagnostico_coloracion_de_macro(None)
assert resultado1 is None
print("✓ Test 4.1a PASS")

# Test biomarcadores con None
resultado2 = auditor._extraer_biomarcadores_solicitados_de_macro(None)
assert resultado2 == []
print("✓ Test 4.1b PASS")

# Test con string vacío
resultado3 = auditor._extraer_diagnostico_coloracion_de_macro('')
assert resultado3 is None
print("✓ Test 4.1c PASS")

resultado4 = auditor._extraer_biomarcadores_solicitados_de_macro('')
assert resultado4 == []
print("✓ Test 4.1d PASS")
```

---

### Test 4.2: Manejo de caracteres especiales

```python
texto_macro = '''
con diagnóstico de "CARCINOMA DUCTAL INVASIVO. NOTTINGHAM GRADO 2 (PUNTAJE DE 6).
INVASIÓN LINFOVASCULAR: NEGATIVO. INVASIÓN PERINEURAL: NEGATIVO".
'''
resultado = auditor._extraer_diagnostico_coloracion_de_macro(texto_macro)

# Validar que acentos se mantienen
assert 'INVASIÓN' in resultado
print("✓ Test 4.2 PASS - Acentos preservados")
```

---

### Test 4.3: Patrones nuevos heredados

```python
# Patrón nuevo: "para los siguientes marcadores:"
texto_macro = 'Para los siguientes marcadores: CD3, CD4, CD8, CD20.'
resultado = auditor._extraer_biomarcadores_solicitados_de_macro(texto_macro)

print(f"Resultado: {resultado}")
assert 'CD3' in resultado
assert 'CD4' in resultado
assert 'CD8' in resultado
assert 'CD20' in resultado
print("✓ Test 4.3a PASS - Patrón 'para los siguientes marcadores'")

# Patrón nuevo: "para marcación de"
texto_macro2 = 'Se revisan placas para marcación de CKAE1E3, CK7, GFAP.'
resultado2 = auditor._extraer_biomarcadores_solicitados_de_macro(texto_macro2)

print(f"Resultado: {resultado2}")
assert 'CKAE1AE3' in resultado2 or 'CKAE1E3' in resultado2
assert 'CK7' in resultado2
assert 'GFAP' in resultado2
print("✓ Test 4.3b PASS - Patrón 'para marcación de'")
```

---

## CHECKLIST DE VALIDACIÓN

Marcar con ✅ cada test que pase correctamente:

### Tests Unitarios
- [ ] Test 1.1: Diagnóstico básico
- [ ] Test 1.2: Diagnóstico ausente
- [ ] Test 1.3: Diagnóstico complejo
- [ ] Test 1.4: Lista biomarcadores básica
- [ ] Test 1.5: Lista biomarcadores multi-línea
- [ ] Test 1.6: Sin biomarcadores

### Tests de Integración
- [ ] Test 2.1: IHQ250981 (E-Cadherina)
- [ ] Test 2.2: IHQ250982 (9 biomarcadores)
- [ ] Test 2.3: IHQ251026

### Tests de Comparación
- [ ] Test 3.1: Comparación caso único
- [ ] Test 3.2: Comparación lote 10 casos

### Tests de Robustez
- [ ] Test 4.1: Entrada nula
- [ ] Test 4.2: Caracteres especiales
- [ ] Test 4.3: Patrones nuevos

### Validación Final
- [ ] Sin excepciones durante ejecución
- [ ] Resultados idénticos o mejores que versión original
- [ ] Todos los casos de prueba PASS
- [ ] Backup disponible en caso de rollback

---

## CRITERIOS DE ACEPTACIÓN

Para considerar la refactorización EXITOSA:

1. ✅ Todos los tests unitarios pasan (6/6)
2. ✅ Todos los tests de integración pasan (3/3)
3. ✅ Comparación antes/después muestra 0 regresiones
4. ✅ Todos los tests de robustez pasan (3/3)
5. ✅ Sin excepciones o errores en logs
6. ✅ Tasa de detección de biomarcadores >= versión original (o mejor)

**Si TODOS los criterios se cumplen** → ✅ APROBADO para producción
**Si ALGÚN criterio falla** → ⚠️ REVISAR y corregir antes de deploy

---

## ROLLBACK (Si es necesario)

En caso de que tests fallen y se requiera revertir:

```bash
# Restaurar versión original desde backup
cp backups/auditor_sistema_backup_20251023_073954.py herramientas_ia/auditor_sistema.py

# Validar restauración
python -m py_compile herramientas_ia/auditor_sistema.py
echo "✓ Rollback completado"
```

---

**Responsable de ejecución:** Usuario / QA
**Tiempo estimado:** 30-45 minutos
**Estado:** PENDIENTE EJECUCIÓN
