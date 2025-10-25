# Editor Core v2.0 - Nuevas Funciones Avanzadas

**Fecha**: 23 de octubre de 2025
**Versión**: 2.0.0 → 2.1.0 (propuesta)
**Archivo modificado**: `herramientas_ia/editor_core.py`
**Líneas totales**: 2358 (+544 líneas nuevas)

---

## Resumen de Cambios

Se han agregado **2 funciones avanzadas** al `editor_core.py` para gestión completa de biomarcadores:

1. **`modificar_biomarcador()`** - Modificar biomarcadores existentes
2. **`eliminar_biomarcador()`** - Eliminar biomarcadores del sistema (con protección)

---

## FUNCIÓN 1: `modificar_biomarcador()`

### Ubicación
Líneas **984-1165** (182 líneas)

### Firma
```python
def modificar_biomarcador(self, nombre: str, campo: str, nuevo_valor: Any,
                         agregar: bool = False, simular: bool = True):
```

### Parámetros
- `nombre`: Nombre del biomarcador (ej: 'KI67', 'HER2')
- `campo`: Campo a modificar ('descripcion', 'patrones', 'valores_posibles', 'normalizacion')
- `nuevo_valor`: Nuevo valor para el campo
- `agregar`: Si True, agrega valor (para patrones). Si False, reemplaza
- `simular`: Si True, solo muestra cambios sin aplicar

### Capacidades

1. **Modificar descripción**
   ```bash
   python editor_core.py --modificar-biomarcador KI67 --campo descripcion \
     --valor "Índice de proliferación celular actualizado" --simular
   ```

2. **Agregar patrón nuevo a lista existente**
   ```bash
   python editor_core.py --modificar-biomarcador HER2 --campo patrones \
     --valor "r'(?i)HER2\\s+SCORE\\s*:\\s*(\\d+)'" --agregar
   ```

3. **Reemplazar todos los patrones**
   ```bash
   python editor_core.py --modificar-biomarcador HER2 --campo patrones \
     --valor "r'(?i)HER2\\s*:\\s*(\\d+)'"
   ```

4. **Modificar valores posibles**
   ```bash
   python editor_core.py --modificar-biomarcador PDL1 --campo valores_posibles \
     --valor "['POSITIVO', 'NEGATIVO', 'ALTO', 'BAJO']"
   ```

5. **Modificar normalización**
   ```bash
   python editor_core.py --modificar-biomarcador ER --campo normalizacion \
     --valor "{'positivo': 'POSITIVO', 'negativo': 'NEGATIVO', 'alto': 'ALTO'}"
   ```

### Protecciones

- Validación de biomarcador existente
- Validación de campo válido
- Backup automático antes de modificar
- Validación de sintaxis Python post-modificación
- Modo simulación por defecto (requiere quitar `--simular` para aplicar)
- Registro de acción en reporte

### Workflow

1. Busca biomarcador en `BIOMARKER_DEFINITIONS`
2. Si `simular=True`: Muestra diff (ANTES/DESPUÉS) sin aplicar
3. Si `simular=False`:
   - Crea backup en `backups/biomarker_extractor_backup_TIMESTAMP.py`
   - Aplica modificación
   - Valida sintaxis Python
   - Registra acción para reporte
   - Muestra próximos pasos

### Ejemplo de Salida (Simulación)

```
================================================================================
🔧 MODIFICANDO BIOMARCADOR: KI67
================================================================================

Campo a modificar: descripcion
Nuevo valor: Índice de proliferación celular actualizado
Modo: Reemplazar
Simulación: SÍ

✅ Biomarcador 'KI67' encontrado
🔍 SIMULACIÓN DE CAMBIOS:
================================================================================

📄 Archivo: biomarker_extractor.py
🔧 Biomarcador: KI67
📝 Campo: descripcion

ANTES:
--------------------------------------------------------------------------------
'KI67': {
    'nombres_alternativos': [...],
    'descripcion': 'Biomarcador Ki-67',
    ...
}

DESPUÉS:
--------------------------------------------------------------------------------
'KI67': {
    'nombres_alternativos': [...],
    'descripcion': 'Índice de proliferación celular actualizado',
    ...
}

================================================================================
✅ Simulación completada - Usa sin --simular para aplicar
```

---

## FUNCIÓN 2: `eliminar_biomarcador()`

### Ubicación
Líneas **1167-1491** (325 líneas)

### Firma
```python
def eliminar_biomarcador(self, nombre: str, confirmar: bool = False,
                        mantener_datos: bool = True):
```

### Parámetros
- `nombre`: Nombre del biomarcador a eliminar
- `confirmar`: Debe ser True para ejecutar (protección)
- `mantener_datos`: Si True, mantiene columna BD con datos (solo elimina código)

### Capacidades

Esta función es **PELIGROSA** y elimina el biomarcador de **LOS 4 ARCHIVOS CRÍTICOS**:

1. `biomarker_extractor.py` - BIOMARKER_DEFINITIONS
2. `validation_checker.py` - MAPEO_BIOMARCADORES (todas las variantes)
3. `unified_extractor.py` - 3 diccionarios de mapeo
4. `database_manager.py` - NEW_TABLE_COLUMNS_ORDER + CREATE TABLE

### Protecciones

- **Requiere confirmación explícita** (`--confirmar`)
- Análisis previo de lo que se eliminará
- Backup automático de TODOS los archivos modificados
- Backup de BD antes de eliminar columna (si se usa `--eliminar-datos`)
- Validación de sintaxis Python post-eliminación
- Por defecto mantiene datos en BD (solo elimina código)
- Registro exhaustivo de acción

### Workflow

1. **Análisis**: Busca biomarcador en los 4 archivos críticos
2. **Resumen**: Muestra EXACTAMENTE qué se eliminará (archivos, líneas, variantes)
3. **Verificación BD**: Indica si columna existe y qué pasará con los datos
4. **Protección**: Si no hay `--confirmar`, CANCELA y muestra advertencia
5. **Ejecución** (solo si `--confirmar`):
   - Crea backups de los 4 archivos con timestamp único
   - Elimina definición de `biomarker_extractor.py`
   - Elimina variantes de `validation_checker.py`
   - Elimina entradas de `unified_extractor.py` (3 diccionarios)
   - Elimina referencias de `database_manager.py`
   - Si `--eliminar-datos`: Intenta eliminar columna de BD (con advertencia)
   - Genera resumen de operación
   - Registra acción exhaustiva

### Casos de Uso

#### Caso 1: Ver qué se eliminaría (SIN confirmar)
```bash
python editor_core.py --eliminar-biomarcador TEST_DEMO
```

**Salida:**
```
================================================================================
⚠️  ELIMINAR BIOMARCADOR: TEST_DEMO
================================================================================

🔍 Analizando presencia del biomarcador en el sistema...

⚠️  ADVERTENCIA: Eliminar biomarcador TEST_DEMO
================================================================================

📄 biomarker_extractor.py:
   - Definición completa (líneas 1050-1078)

📄 validation_checker.py:
   - 3 variantes mapeadas: TEST_DEMO, TEST-DEMO, TESTDEMO

📄 unified_extractor.py:
   - 3 entradas en diccionarios de mapeo

📄 database_manager.py:
   - Columna 'IHQ_TEST_DEMO' en NEW_TABLE_COLUMNS_ORDER y CREATE TABLE

💾 BASE DE DATOS:
   Columna: IHQ_TEST_DEMO
   ✅ Mantener datos: SÍ (columna permanece, solo se elimina código)

================================================================================
❌ OPERACIÓN CANCELADA
================================================================================

⚠️  Esta es una operación PELIGROSA.
💡 Usa --confirmar para ejecutar la eliminación
💡 Usa --eliminar-datos para también eliminar la columna de BD (PELIGROSO)
```

#### Caso 2: Eliminar biomarcador (MANTENER datos BD)
```bash
python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar
```

**Ejecuta eliminación de código, mantiene columna BD con datos**

#### Caso 3: Eliminar biomarcador Y columna BD (PELIGROSO)
```bash
python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar --eliminar-datos
```

**Ejecuta eliminación completa (código + intento de eliminar columna BD)**

### Ejemplo de Salida (Ejecución Confirmada)

```
================================================================================
🔥 EJECUTANDO ELIMINACIÓN
================================================================================

1️⃣  Eliminando de biomarker_extractor.py...
   📦 Backup creado: backups/biomarker_extractor_backup_20251023_120000.py
   ✅ Eliminado de BIOMARKER_DEFINITIONS

2️⃣  Eliminando de validation_checker.py...
   📦 Backup creado: backups/validation_checker_backup_20251023_120000.py
   ✅ Eliminadas variantes de MAPEO_BIOMARCADORES

3️⃣  Eliminando de unified_extractor.py...
   📦 Backup creado: backups/unified_extractor_backup_20251023_120000.py
   ✅ Eliminado de los 3 diccionarios de mapeo

4️⃣  Eliminando de database_manager.py...
   📦 Backup creado: backups/database_manager_backup_20251023_120000.py
   ✅ Eliminado de NEW_TABLE_COLUMNS_ORDER y CREATE TABLE

================================================================================
📊 RESUMEN DE ELIMINACIÓN
================================================================================
Biomarcador eliminado: TEST_DEMO
Columna BD: IHQ_TEST_DEMO

✅ Archivos modificados (4):
   - biomarker_extractor.py
   - validation_checker.py
   - unified_extractor.py
   - database_manager.py

📦 Backups creados en: backups/
💡 Backups con timestamp: 20251023_120000

ℹ️  La columna 'IHQ_TEST_DEMO' permanece en BD con los datos

✅ BIOMARCADOR TEST_DEMO ELIMINADO
```

---

## Argumentos CLI Agregados

### ArgumentParser (Líneas 2210-2216)

```python
parser.add_argument("--modificar-biomarcador", help="Modificar biomarcador existente")
parser.add_argument("--campo", help="Campo a modificar (descripcion, patrones, valores_posibles, normalizacion)")
parser.add_argument("--valor", help="Nuevo valor para el campo")
parser.add_argument("--agregar", action="store_true", help="Agregar valor en lugar de reemplazar (para patrones)")
parser.add_argument("--eliminar-biomarcador", help="Eliminar biomarcador del sistema")
parser.add_argument("--confirmar", action="store_true", help="Confirmar eliminación (protección)")
parser.add_argument("--eliminar-datos", action="store_true", help="Eliminar también columna BD (PELIGROSO)")
```

### Lógica Main (Líneas 2272-2290)

```python
elif args.modificar_biomarcador:
    if not args.campo or not args.valor:
        print("❌ Se requieren --campo y --valor")
        sys.exit(1)
    editor.modificar_biomarcador(
        args.modificar_biomarcador,
        args.campo,
        args.valor,
        agregar=args.agregar,
        simular=args.simular
    )

elif args.eliminar_biomarcador:
    mantener_datos = not args.eliminar_datos
    editor.eliminar_biomarcador(
        args.eliminar_biomarcador,
        confirmar=args.confirmar,
        mantener_datos=mantener_datos
    )
```

---

## Documentación en Help (Líneas 2165-2173)

```
MODIFICAR BIOMARCADOR (NUEVO v2.0):
  python editor_core.py --modificar-biomarcador KI67 --campo descripcion --valor "..." --simular
  python editor_core.py --modificar-biomarcador HER2 --campo patrones --valor "..." --agregar
  python editor_core.py --modificar-biomarcador PDL1 --campo valores_posibles --valor "['POSITIVO', 'NEGATIVO']"

ELIMINAR BIOMARCADOR (NUEVO v2.0 - PELIGROSO):
  python editor_core.py --eliminar-biomarcador TEST_DEMO  # Ver qué se eliminaría (sin confirmar)
  python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar  # Eliminar (mantener datos BD)
  python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar --eliminar-datos  # PELIGROSO
```

---

## Integración con Sistema de Reportes

Ambas funciones usan `self.registrar_accion()` para generar reportes en `herramientas_ia/resultados/`:

### Reporte de Modificación
```markdown
### Modificación de Biomarcador

**2025-10-23 12:00:00**

- Biomarcador: KI67
- Campo modificado: descripcion
- Nuevo valor: Índice de proliferación celular actualizado
- Modo: Reemplazar
- Archivo: biomarker_extractor.py
- Backup: biomarker_extractor_backup_20251023_120000.py
```

### Reporte de Eliminación
```markdown
### Eliminación de Biomarcador

**2025-10-23 12:00:00**

- Biomarcador: TEST_DEMO
- Columna BD: IHQ_TEST_DEMO
- Archivos modificados:
  - biomarker_extractor.py
  - validation_checker.py
  - unified_extractor.py
  - database_manager.py
- Datos BD: Mantenidos
- Errores: []
- Timestamp backup: 20251023_120000
```

---

## Validaciones Realizadas

### Sintaxis Python
```bash
python -m py_compile herramientas_ia/editor_core.py
✅ Sintaxis validada correctamente
```

### Help Command
```bash
python herramientas_ia/editor_core.py --help
✅ Muestra correctamente las nuevas opciones
```

### Test Funcional (Eliminar sin confirmar)
```bash
python herramientas_ia/editor_core.py --eliminar-biomarcador KI67
✅ Muestra análisis y CANCELA por falta de --confirmar
```

---

## Estadísticas de Código

| Métrica | Valor |
|---------|-------|
| Líneas totales | 2358 (+544 nuevas) |
| `modificar_biomarcador()` | 182 líneas |
| `eliminar_biomarcador()` | 325 líneas |
| Argumentos CLI nuevos | 7 |
| Ejemplos en help | 6 |
| Archivos críticos afectados | 4 (por eliminar_biomarcador) |

---

## Flujo de Trabajo Recomendado

### Para Modificar Biomarcador
```bash
# 1. Simular primero
python editor_core.py --modificar-biomarcador KI67 --campo descripcion \
  --valor "Nueva descripción" --simular

# 2. Si OK, aplicar
python editor_core.py --modificar-biomarcador KI67 --campo descripcion \
  --valor "Nueva descripción"

# 3. Validar sintaxis
python editor_core.py --validar-sintaxis biomarker_extractor.py

# 4. Generar reporte
python editor_core.py --generar-reporte
```

### Para Eliminar Biomarcador
```bash
# 1. Ver qué se eliminará (SIN confirmar)
python editor_core.py --eliminar-biomarcador TEST_DEMO

# 2. Si estás seguro, ejecutar con confirmación
python editor_core.py --eliminar-biomarcador TEST_DEMO --confirmar

# 3. Generar reporte
python editor_core.py --generar-reporte

# 4. (Opcional) Actualizar versión del sistema
python herramientas_ia/gestor_version.py --actualizar-version-parche
```

---

## Próximos Pasos Sugeridos

1. **Actualizar documentación del agente core-editor**
   - Agregar sección de modificación de biomarcadores
   - Agregar sección de eliminación de biomarcadores
   - Actualizar ejemplos de uso

2. **Actualizar versión del sistema**
   - v6.0.2 → v6.1.0 (funcionalidad nueva)
   - Generar CHANGELOG con estos cambios

3. **Testing exhaustivo**
   - Probar modificación de diferentes campos
   - Probar eliminación con y sin --eliminar-datos
   - Validar backups creados

4. **Actualizar agente documentation-specialist-HUV**
   - Documentar las nuevas funciones
   - Agregar guías de uso

---

## Notas Importantes

1. **BACKUPS AUTOMÁTICOS**: Ambas funciones crean backups automáticos en `backups/` antes de modificar
2. **SIMULACIÓN POR DEFECTO**: `modificar_biomarcador()` tiene simulación activada por defecto
3. **PROTECCIÓN DOBLE**: `eliminar_biomarcador()` requiere `--confirmar` explícito
4. **MANTENER DATOS**: Por defecto se mantienen datos en BD al eliminar (solo código se elimina)
5. **VALIDACIÓN SINTAXIS**: Ambas funciones validan sintaxis Python post-modificación

---

**Fecha de creación**: 2025-10-23
**Autor**: Sistema EVARISIS - core-editor
**Versión propuesta**: 2.1.0
