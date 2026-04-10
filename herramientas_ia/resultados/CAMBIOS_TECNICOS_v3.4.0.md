# CAMBIOS TECNICOS - VALIDACION CAMPO ORGANO v3.4.0

## ARCHIVO MODIFICADO
- **Ruta:** `herramientas_ia/auditor_sistema.py`
- **Version anterior:** 3.3.0
- **Version nueva:** 3.4.0
- **Fecha:** 5 de noviembre de 2025

## LINEAS MODIFICADAS

### 1. METADATA (Lineas 27-28)
```python
# ANTES:
Versión: 3.3.0 - VALIDACIÓN ANTI-PROBLEMAS (IHQ251007)
Fecha: 3 de noviembre de 2025

# DESPUES:
Versión: 3.4.0 - VALIDACIÓN ORGANO (IHQ251014)
Fecha: 5 de noviembre de 2025
```

### 2. CHANGELOG (Lineas 30-40)
```python
# NUEVO BLOQUE INSERTADO:
CHANGELOG v3.4.0:
- NUEVA FUNCIONALIDAD: Validacion campo Organo (detecta duplicacion y contaminacion)
- Nueva funcion: _validar_organo() - valida limpieza del campo Organo
- Detecta: Texto duplicado (ej: "BIOPSIA DE HUESO" aparece 2 veces)
- Detecta: Codigos de caso (IHQ251014-B), codigos numericos (898807)
- Detecta: Texto administrativo (ESTUDIO DE INMUNOHISTOQUIMICA, etc.)
- Genera: Sugerencia automatica de valor limpio
- Resuelve: IHQ251014 con campo Organo contaminado
- Integrado en: _auditar_datos_guardados() linea ~823
- Impacto: Detecta contaminacion en campo Organo que antes pasaba desapercibida
- Total validaciones: 9 -> 10 (agregada validacion Organo)

[CHANGELOG v3.3.0 sigue intacto debajo]
```

### 3. NUEVA FUNCION _validar_organo() (Lineas 1314-1409)

**Ubicacion:** Despues de `_validar_ihq_organo()`, antes de `_validar_factor_pronostico_regla_4()`

```python
def _validar_organo(self, campos_criticos: dict) -> dict:
    """
    Valida que el campo Organo esté limpio (sin duplicación ni contaminación).
    
    V3.4.0: Nueva validación para detectar:
    - Texto duplicado (órgano aparece 2+ veces)
    - Códigos de caso (IHQ251014-B)
    - Códigos numéricos (898807)
    - Texto administrativo (ESTUDIO DE INMUNOHISTOQUIMICA, etc.)
    
    Args:
        campos_criticos: Diccionario base_datos.campos_criticos del debug_map
    
    Returns:
        Dict con estado de validación y valor sugerido
    
    Ejemplo:
        IHQ251014: "BIOPSIA DE HUESO IHQ251014-B ... BIOPSIA DE HUESO"
        → ERROR: duplicación + contaminación
        → Sugerencia: "BIOPSIA DE HUESO"
    """
    # [95 lineas de implementacion]
```

**Componentes de la funcion:**

#### A. Validacion campo vacio (Lineas 1335-1343)
```python
if not organo or organo.strip() == '':
    return {
        'estado': 'WARNING',
        'mensaje': 'Campo Organo está vacío',
        'valor_bd': organo
    }
```

#### B. Deteccion texto duplicado (Lineas 1347-1363)
```python
# Buscar frases de 2-5 palabras que aparecen 2+ veces
for tamano in range(5, 1, -1):  # De 5 a 2 palabras
    for i in range(len(palabras) - tamano + 1):
        frase = ' '.join(palabras[i:i+tamano])
        resto = ' '.join(palabras[i+tamano:])
        if frase in resto:
            texto_duplicado = frase
            problemas.append(f'texto duplicado: "{frase}"')
            break
```

#### C. Deteccion contaminacion (Lineas 1365-1378)
```python
patrones_contaminacion = [
    (r'IHQ\d{6}[-A-Z]*', 'código de caso'),
    (r'\d{6,}', 'código numérico largo'),
    (r'ESTUDIO DE INMUNOHISTOQUIMICA', 'texto administrativo'),
    (r'ESTUDIO ANATOMOPATOLOGICO', 'texto administrativo'),
    (r'MARCACION INMUNOHISTOQUIMICA', 'texto administrativo'),
    (r'BLOQUES Y LAMINAS', 'texto administrativo'),
    (r'BASICA\s*\(ESPECIFICO\)', 'texto administrativo'),
]

for patron, tipo in patrones_contaminacion:
    if re.search(patron, organo, re.IGNORECASE):
        if tipo not in [p.split(': ')[0] for p in problemas if ': ' in p]:
            problemas.append(tipo)
```

#### D. Generacion sugerencia limpieza (Lineas 1380-1402)
```python
if problemas:
    # Estrategia 1: Extraer órgano antes de códigos
    match_organo = re.search(r'^([A-Z\s]+?)\s+(?:IHQ\d{6}|\d{6})', organo)
    
    if match_organo:
        organo_limpio = match_organo.group(1).strip()
    elif texto_duplicado:
        # Estrategia 2: Tomar primera ocurrencia si hay duplicación
        organo_limpio = texto_duplicado.strip()
    else:
        # Estrategia 3: Tomar primeras 2-4 palabras
        organo_limpio = ' '.join(palabras[:min(4, len(palabras))])
    
    return {
        'estado': 'ERROR',
        'mensaje': f'Campo Organo contiene problemas: {", ".join(problemas)}',
        'valor_bd': organo,
        'valor_sugerido': organo_limpio,
        'nota': f'Debe limpiarse: "{organo}" → "{organo_limpio}"',
        'problemas_detectados': problemas
    }
```

### 4. INTEGRACION EN FLUJO (Lineas 837-855)

**Ubicacion:** En `_auditar_datos_guardados()`, seccion 3.2.6

```python
# 3.2.6 Campo Organo (validar duplicacion y contaminacion)
print("Validando campo Organo...")
resultado_organo = self._validar_organo(criticos)
auditoria['organo'] = resultado_organo

if resultado_organo['estado'] == 'ERROR':
    print(f"   ERROR: {resultado_organo['mensaje']}")
    if len(resultado_organo.get('valor_bd', '')) > 80:
        print(f"   Valor BD: {resultado_organo['valor_bd'][:80]}...")
    else:
        print(f"   Valor BD: {resultado_organo.get('valor_bd', '')}")
    print(f"   Valor sugerido: {resultado_organo.get('valor_sugerido', '')}")
    auditoria['errores'].append(resultado_organo['mensaje'])
    auditoria['estado'] = 'ERROR'
elif resultado_organo['estado'] == 'WARNING':
    print(f"   WARNING: {resultado_organo['mensaje']}")
    auditoria['warnings'].append(resultado_organo['mensaje'])
else:
    print(f"   OK: {resultado_organo['mensaje']}")
```

## VALIDACION

### Sintaxis Python
```bash
python -m py_compile herramientas_ia/auditor_sistema.py
# Resultado: OK (sin errores)
```

### Verificacion funcion unica
```bash
grep -c "def _validar_organo" herramientas_ia/auditor_sistema.py
# Resultado: 1 (unica ocurrencia)
```

### Verificacion integracion
```bash
grep -n "resultado_organo = self._validar_organo" herramientas_ia/auditor_sistema.py
# Resultado: 837: resultado_organo = self._validar_organo(criticos)
```

## BACKUP

**Ubicacion:** `herramientas_ia/auditor_sistema.py.backup_20251105_034035`
**Comando rollback:** `cp herramientas_ia/auditor_sistema.py.backup_20251105_034035 herramientas_ia/auditor_sistema.py`

## TESTING

### Comando de prueba
```bash
python herramientas_ia/auditor_sistema.py IHQ251014 --inteligente
```

### Resultado esperado
```
Validando campo Organo...
   ERROR: Campo Organo contiene problemas: texto duplicado: "BIOPSIA DE HUESO", codigo de caso, codigo numerico largo, texto administrativo
   Valor BD: BIOPSIA DE HUESO IHQ251014-B ESTUDIO DE INMUNOHISTOQUIMICA 898807...
   Valor sugerido: BIOPSIA DE HUESO
```

## ESTADISTICAS

- **Total lineas agregadas:** 98
- **Total lineas modificadas:** 3 (version, fecha, changelog)
- **Total funciones nuevas:** 1 (`_validar_organo`)
- **Total validaciones sistema:** 9 → 10
- **Tamano archivo:** 193K → 199K (+6K)

## COMPATIBILIDAD

- Retrocompatible: SI (no rompe funcionalidad existente)
- Requiere migracion BD: NO
- Requiere actualizacion dependencias: NO
- Impacto en otras funciones: NINGUNO (funcion aislada)

## PROXIMOS PASOS

1. Ejecutar prueba en IHQ251014
2. Validar resultado con caso real
3. Auditar casos similares con campo Organo contaminado
4. Documentar resultados en CHANGELOG_CLAUDE.md
5. Considerar implementar FUNC-02 (correccion automatica)
