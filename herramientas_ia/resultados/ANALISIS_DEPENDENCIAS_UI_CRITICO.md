# ANÁLISIS DE DEPENDENCIAS UI CRÍTICO
## DOCUMENTO TÉCNICO PARA PREVENIR BREAKING CHANGES

**Sistema**: EVARISIS Cirugía Oncológica HUV
**Versión**: 6.0.5
**Archivo principal**: `ui.py` (270.6KB, ~7,000 líneas)
**Fecha análisis**: 2025-10-24
**Propósito**: Guía DEFINITIVA para que `core-editor` NO rompa UI al modificar

---

## TABLA DE CONTENIDOS

1. [MAPA DE DEPENDENCIAS COMPLETO](#1-mapa-de-dependencias-completo)
2. [VARIABLES PROHIBIDAS DE MODIFICAR](#2-variables-prohibidas-de-modificar)
3. [MÉTODOS PROHIBIDOS DE CAMBIAR FIRMA](#3-métodos-prohibidos-de-cambiar-firma)
4. [ALIAS Y TRUCOS PELIGROSOS](#4-alias-y-trucos-peligrosos)
5. [CHECKLIST DE SEGURIDAD](#5-checklist-de-seguridad)
6. [MATRIZ DE IMPACTO](#6-matriz-de-impacto)
7. [REGLAS ABSOLUTAS PARA CORE-EDITOR](#7-reglas-absolutas-para-core-editor)

---

## 1. MAPA DE DEPENDENCIAS COMPLETO

### 1.1 ÁRBOL DE IMPORTS

```
ui.py (ARCHIVO PRINCIPAL - 270.6KB)
├── IMPORTS ESTÁNDAR
│   ├── tkinter as tk
│   ├── ttkbootstrap as ttk
│   ├── pandas as pd
│   ├── sqlite3
│   ├── logging
│   └── PIL (Image, ImageTk, ImageDraw)
│
├── IMPORTS CORE (Módulos de extracción/procesamiento)
│   ├── core.enhanced_export_system → EnhancedExportSystem (línea 40)
│   ├── core.ventana_auditoria_ia → mostrar_ventana_auditoria (línea 45)
│   ├── core.database_manager → 15+ funciones
│   ├── core.unified_extractor → extract_ihq_data
│   ├── core.processors.ocr_processor → pdf_to_text_enhanced
│   └── core.debug_mapper → DebugMapper
│
├── IMPORTS UI_HELPERS (Módulos auxiliares UI)
│   ├── ui_helpers.ocr_helpers (línea 49)
│   ├── ui_helpers.database_helpers (línea 49)
│   ├── ui_helpers.export_helpers (línea 49)
│   └── ui_helpers.chart_helpers (línea 49)
│
└── IMPORTS DINÁMICOS (Dentro de métodos)
    ├── core.ventana_selector_auditoria → mostrar_selector_auditoria (línea 714)
    ├── core.ventana_resultados_importacion → mostrar_ventana_resultados (líneas 4995, 5118, 5309)
    ├── core.enhanced_database_dashboard → EnhancedDatabaseDashboard (línea 1905)
    └── core.process_with_audit → process_ihq_paths_with_audit
```

### 1.2 DIAGRAMA ASCII DE DEPENDENCIAS

```
┌────────────────────────────────────────────────────────────────┐
│                         ui.py (App class)                       │
│                                                                 │
│  VARIABLES DE ESTADO CRÍTICAS:                                 │
│  • self.current_view        → "welcome" | "database" | ...     │
│  • self.master_df           → DataFrame FUENTE DE VERDAD       │
│  • self.sheet / self.tree   → Widget Sheet (ALIAS!)            │
│  • self.db_filters          → Dict de filtros activos          │
│  • self._ultimos_registros  → Lista IDs recién importados      │
│  • self._ruta_ultimo_reporte→ Ruta último reporte IA           │
│                                                                 │
│  WIDGETS CRÍTICOS:                                              │
│  • self.enhanced_dashboard  → Dashboard avanzado               │
│  • self.export_system       → Sistema de exportación           │
│  • self.cmb_servicio/malig/resp → Comboboxes de filtros       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ EnhancedExport  │  │ EnhancedDatabase│  │ VentanaAuditoria│
│ System          │  │ Dashboard       │  │ IA              │
│                 │  │                 │  │                 │
│ DEPENDE DE:     │  │ DEPENDE DE:     │  │ DEPENDE DE:     │
│ • parent_app    │  │ • parent (App)  │  │ • parent (App)  │
│   .master_df    │  │ • DB completa   │  │ • callback      │
│   .tree         │  │                 │  │                 │
│   ._nav_to_     │  │ PROVEE:         │  │ PROVEE:         │
│     database()  │  │ • .notebook     │  │ • resultados[]  │
│                 │  │ • .import_files │  │                 │
│ PROVEE:         │  │   _listbox      │  │ LLAMADO POR:    │
│ • export_*()    │  │ • refresh_*()   │  │ • process_with_ │
│   métodos       │  │   métodos       │  │   audit.py      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### 1.3 DEPENDENCIAS EXTERNAS HACIA UI

**Archivos que LLAMAN a ui.py:**

1. **process_with_audit.py** (líneas 48-65)
   - Llama: `parent_app.refresh_data_and_table()`
   - Propósito: Actualizar tabla después de importar PDFs

2. **enhanced_export_system.py** (líneas 355-377)
   - Llama: `parent_app._nav_to_database()`
   - Llama: `parent_app.enhanced_dashboard.refresh_exports_list()`
   - Llama: `parent_app.enhanced_dashboard.notebook.select(5)`
   - Propósito: Navegar a dashboard y pestaña Exportaciones

3. **ventana_auditoria_ia.py** (líneas 836-846)
   - Accede: `parent._ruta_ultimo_reporte`
   - Propósito: Mostrar ruta del reporte IA generado

**CRÍTICO**: Estos archivos esperan que `App` tenga estos métodos/variables. Si los renombras/eliminas, SE ROMPE TODO.

---

## 2. VARIABLES PROHIBIDAS DE MODIFICAR

### 2.1 VARIABLES DE ESTADO (App.__init__)

#### ⚠️ CRÍTICO - NIVEL 1 (NO TOCAR NUNCA)

| Variable | Línea | Tipo | Usada Por | ¿Por qué es crítica? |
|----------|-------|------|-----------|----------------------|
| `self.current_view` | 214 | str | Navegación interna | Controla qué vista mostrar. Valores: "welcome", "database", "visualizar", "dashboard", "analisis_ia" |
| `self.master_df` | 233 | DataFrame | TODA la UI | FUENTE ÚNICA DE VERDAD. Todos los widgets leen de aquí. Cambiar nombre ROMPE 100+ referencias |
| `self.sheet` | 2054-2184 | Sheet widget | Sistema tabla | Widget principal de tabla. Tiene 40+ métodos. Es el CORE de visualización |
| `self.tree` | 2184 | ALIAS → self.sheet | Código legado | ALIAS CRÍTICO. Ver sección 4. Cambiar ROMPE bindings |

#### ⚠️ CRÍTICO - NIVEL 2 (TOCAR CON EXTREMA PRECAUCIÓN)

| Variable | Línea | Tipo | Usada Por | ¿Por qué es crítica? |
|----------|-------|------|-----------|----------------------|
| `self._ultimos_registros_procesados` | 217 | List[str] | process_with_audit.py | Lista de IDs recién importados. Auditoría IA depende de esto |
| `self._ruta_ultimo_reporte` | 1237 | str | ventana_auditoria_ia.py | Ruta último reporte IA. Ventana auditoría la lee directamente |
| `self.enhanced_dashboard` | 1906 | EnhancedDatabaseDashboard | enhanced_export_system.py | Dashboard. Exportación navega a él. Tiene .notebook, .import_files_listbox |
| `self.export_system` | 243 | EnhancedExportSystem | Botones exportación | Sistema de exportación. Tiene métodos export_full_database(), export_selected_data() |

#### ⚠️ IMPORTANTE - NIVEL 3 (PUEDE TOCARSE SI SE ACTUALIZAN REFERENCIAS)

| Variable | Línea | Tipo | Usada Por | ¿Por qué es crítica? |
|----------|-------|------|-----------|----------------------|
| `self.db_filters` | 2280 | Dict | Filtros BD | Keys: fecha_desde, fecha_hasta, servicio, malignidad, responsable |
| `self.cmb_servicio` | 2301 | Combobox | Filtros BD | Combobox de servicios médicos |
| `self.cmb_malig` | 2305 | Combobox | Filtros BD | Combobox de malignidad |
| `self.cmb_resp` | 2309 | Combobox | Filtros BD | Combobox de médico responsable |

### 2.2 VARIABLES DE CONFIGURACIÓN

| Variable | Línea | Tipo | Cambiar Impacto |
|----------|-------|------|-----------------|
| `self.info_usuario` | 188 | Dict | MEDIO - Solo afecta perfil mostrado |
| `self.current_theme` | 199 | str | MEDIO - Solo afecta tema visual |
| `self.FONT_*` | 191-196 | Tuple | BAJO - Solo afecta fuentes |
| `self.iconos` | 207 | Dict | BAJO - Solo afecta iconos mostrados |
| `self.foto_usuario` | 208 | PIL.Image | BAJO - Solo afecta foto perfil |

---

## 3. MÉTODOS PROHIBIDOS DE CAMBIAR FIRMA

### 3.1 MÉTODOS LLAMADOS POR MÓDULOS EXTERNOS

#### ⚠️ CRÍTICO - NIVEL 1

**Método**: `refresh_data_and_table()`
**Línea**: 3897
**Firma actual**:
```python
def refresh_data_and_table(self) -> None
```
**Llamado por**:
- `process_with_audit.py` (línea ~195)
- `enhanced_export_system.py` (línea 904)

**Descripción**: Recarga `self.master_df` desde BD y actualiza tabla visual.

**¿Qué pasa si cambias la firma?**
- ❌ Agregar parámetros obligatorios → process_with_audit.py FALLA
- ❌ Cambiar nombre → ImportError inmediato
- ❌ Cambiar tipo de retorno → No afecta (se ignora)

**Cambios seguros**:
- ✅ Agregar parámetros opcionales: `refresh_data_and_table(self, force=False)`
- ✅ Cambiar implementación interna (mientras siga actualizando `self.master_df`)

---

**Método**: `_nav_to_database()`
**Línea**: 657
**Firma actual**:
```python
def _nav_to_database(self) -> None
```
**Llamado por**:
- `enhanced_export_system.py` (línea 358)

**Descripción**: Navega a vista de base de datos. Actualiza `self.current_view = "database"`.

**¿Qué pasa si cambias?**
- ❌ Renombrar → enhanced_export_system.py FALLA al exportar
- ❌ Eliminar → Exportación queda en vista incorrecta

**Cambios seguros**:
- ✅ Refactorizar implementación interna
- ✅ Agregar parámetros opcionales

---

**Método**: `_populate_treeview(df_to_display: pd.DataFrame)`
**Línea**: 3947
**Firma actual**:
```python
def _populate_treeview(self, df_to_display: pd.DataFrame) -> None
```
**Llamado por**:
- `refresh_data_and_table()` (línea 3911)
- Filtros internos (múltiples líneas)

**Descripción**: Llena el widget Sheet con datos del DataFrame.

**¿Qué pasa si cambias?**
- ❌ Cambiar tipo de parámetro (`df_to_display`) → TypeError en runtime
- ❌ Hacer parámetro obligatorio adicional → Todos los callers FALLAN
- ❌ Renombrar → Búsqueda masiva necesaria

**Parámetro DEBE ser DataFrame**. NO aceptar None, lista, dict, etc.

---

### 3.2 MÉTODOS LLAMADOS INTERNAMENTE (PERO CRÍTICOS)

| Método | Línea | Firma | Cambios peligrosos |
|--------|-------|-------|--------------------|
| `mostrar_detalle_registro(event)` | 2123 | `(self, event)` | Cambiar firma ROMPE binding `<<SheetSelect>>` |
| `_actualizar_estadisticas_db()` | ~3500 | `(self)` | Renombrar → Buscar 10+ llamadas |
| `_crear_visualizacion_dashboard()` | ~1800 | `(self)` | Renombrar → Buscar 5+ llamadas |
| `_iniciar_auditoria_ia(tipo)` | 722 | `(self, tipo_auditoria: str)` | Cambiar parámetro → Botones FALLAN |

### 3.3 CALLBACKS Y BINDINGS

**CRÍTICO**: Estos métodos están BINDEADOS a eventos Tk. Cambiar firma los DESCONECTA.

```python
# Línea 2123 - Binding crítico
self.sheet.bind("<<SheetSelect>>", self.mostrar_detalle_registro)

# Firma DEBE ser: (self, event)
def mostrar_detalle_registro(self, event):
    # ...
```

**Otros bindings críticos**:

| Evento | Método | Línea Binding | Firma EXACTA |
|--------|--------|---------------|--------------|
| `<<SheetSelect>>` | `mostrar_detalle_registro` | 2123 | `(self, event)` |
| `<<TreeviewSelect>>` | `_update_selection_buttons` | 2257 | `(event)` |
| `<Button-1>` | `_on_cell_click` | ~2300 | `(self, event)` |

---

## 4. ALIAS Y TRUCOS PELIGROSOS

### 4.1 EL ALIAS MÁS PELIGROSO: `self.tree = self.sheet`

**Ubicación**: Línea 2184

**Código exacto**:
```python
# Línea 2184
self.tree = self.sheet
```

**¿Por qué existe?**

El código ORIGINALMENTE usaba `ttk.Treeview` (widget nativo Tkinter). Luego se migró a `tksheet.Sheet` (widget mucho más potente) pero había **CIENTOS** de referencias a `self.tree` en el código.

En vez de reemplazar todas las referencias, se creó este ALIAS.

**Consecuencias del alias**:

1. **Código confuso**: `self.tree` NO es un Treeview, es un Sheet
2. **Métodos simulados**: Sheet NO tiene métodos nativos de Treeview, así que se crearon wrappers:

```python
# Líneas 2178-2181 - Wrappers de compatibilidad
self.sheet.selection = _sheet_selection      # Simula tree.selection()
self.sheet.item = _sheet_item                # Simula tree.item()
self.sheet.get_children = _sheet_get_children # Simula tree.get_children()
self.sheet.index = _sheet_index              # Simula tree.index()
```

3. **Código que usa el alias**:

```python
# Línea 880 - Código espera "tree" pero es Sheet
selected = self.tree.selection()

# Línea 895 - Accede a columnas
columns = self.tree["columns"]

# Línea 905 - Lee valores
values = self.tree.item(item_id, 'values')
```

**¿Qué pasa si eliminas el alias?**

```python
# ANTES (actual)
self.tree = self.sheet
selected = self.tree.selection()  # ✅ FUNCIONA (llama wrapper)

# DESPUÉS (sin alias)
# self.tree = self.sheet  ← ELIMINADO
selected = self.tree.selection()  # ❌ AttributeError: 'App' has no attribute 'tree'
```

**TODAS** estas líneas FALLARÍAN:
- Líneas 880, 895, 905, 2191, 2210, 2215, 2257, y **50+ más**

### 4.2 OTROS ALIAS Y REFERENCIAS CRUZADAS

**`self.enhanced_dashboard.notebook`**

```python
# Línea 1906 - Creación
self.enhanced_dashboard = EnhancedDatabaseDashboard(...)

# Línea 376 (enhanced_export_system.py) - Uso externo
self.parent_app.enhanced_dashboard.notebook.select(5)
```

**Peligro**: Si renombras `enhanced_dashboard` → enhanced_export_system.py SE ROMPE

**`self.enhanced_dashboard.import_files_listbox`**

```python
# Línea 1945 (ui.py) - Uso interno
if hasattr(self.enhanced_dashboard, 'import_files_listbox'):
    # ...
```

**Peligro**: Si EnhancedDatabaseDashboard cambia este atributo → ui.py falla silenciosamente

---

## 5. CHECKLIST DE SEGURIDAD

### 5.1 CHECKLIST: Añadir Nuevo Widget

- [ ] **Paso 1**: Verificar que el widget NO use nombres de variables existentes
  - Buscar: `grep -r "nombre_widget" .`
  - Validar: No hay colisiones con `self.master_df`, `self.sheet`, `self.tree`, etc.

- [ ] **Paso 2**: Decidir dónde colocar el widget
  - ¿Va en `main_container`? ¿En `header_frame`? ¿En `floating_menu`?
  - Verificar que NO se superponga con widgets existentes

- [ ] **Paso 3**: Asignar a variable de instancia solo si es necesario
  - ¿Otros métodos necesitan acceder a él? → `self.mi_widget`
  - ¿Solo se usa localmente? → Variable local `mi_widget`

- [ ] **Paso 4**: Si el widget actualiza datos, SIEMPRE actualizar `self.master_df`
  - NO crear fuentes de verdad alternativas
  - Después de actualizar `master_df`, llamar `refresh_data_and_table()`

- [ ] **Paso 5**: Si el widget tiene callbacks, usar lambdas o métodos privados
  ```python
  # CORRECTO
  btn = ttk.Button(parent, command=lambda: self._mi_callback_interno())

  # INCORRECTO (expone método público innecesario)
  btn = ttk.Button(parent, command=self.mi_callback_publico)
  ```

- [ ] **Paso 6**: Documentar el widget en código
  ```python
  # NUEVO WIDGET: Botón para X
  # Ubicación: header_frame (derecha)
  # Callback: _mi_callback_interno()
  self.btn_nuevo = ttk.Button(...)
  ```

- [ ] **Paso 7**: Probar en todas las vistas
  - Vista Welcome
  - Vista Database
  - Vista Dashboard
  - Vista Análisis IA

### 5.2 CHECKLIST: Cambiar Layout

- [ ] **Paso 1**: Identificar contenedor padre
  - ¿Es `main_container`? ¿`header_frame`? ¿`content_frame`?

- [ ] **Paso 2**: Verificar geometría manager usado
  - `.pack()` → Orden de empaquetado importa
  - `.grid()` → Filas/columnas deben ser consistentes
  - `.place()` → Coordenadas absolutas

- [ ] **Paso 3**: Si cambias de geometría manager, ELIMINAR widgets primero
  ```python
  # CORRECTO
  for widget in parent.winfo_children():
      widget.destroy()
  # Ahora puedes usar .grid() en vez de .pack()

  # INCORRECTO (mezclar geometría managers)
  widget1.pack()
  widget2.grid()  # ❌ ERROR: cannot use geometry manager grid inside . which already has slaves managed by pack
  ```

- [ ] **Paso 4**: Actualizar constantes de tamaño si existen
  - Buscar: `HEADER_HEIGHT`, `MENU_WIDTH`, etc.

- [ ] **Paso 5**: Probar responsividad
  - Minimizar ventana
  - Maximizar ventana
  - Cambiar tamaño manualmente

- [ ] **Paso 6**: Verificar que NO se rompieron bindings
  - Verificar que `<<SheetSelect>>` sigue funcionando
  - Verificar que botones responden

### 5.3 CHECKLIST: Renombrar Variable

- [ ] **Paso 1**: ¿Es variable CRÍTICA de nivel 1 o 2?
  - SI → ❌ **NO RENOMBRAR** (ver sección 2.1)
  - NO → Continuar

- [ ] **Paso 2**: Buscar TODAS las referencias
  ```bash
  grep -rn "nombre_variable" .
  ```

- [ ] **Paso 3**: Buscar referencias STRING (pueden estar en dicts, configs)
  ```bash
  grep -rn '"nombre_variable"' .
  grep -rn "'nombre_variable'" .
  ```

- [ ] **Paso 4**: Verificar uso en módulos externos
  - `enhanced_export_system.py`
  - `process_with_audit.py`
  - `ventana_auditoria_ia.py`
  - `enhanced_database_dashboard.py`

- [ ] **Paso 5**: Hacer reemplazo con regex (cuidado con false positives)
  ```python
  # Usar editor con regex para reemplazar SOLO palabra completa
  # Buscar: \bself\.nombre_variable\b
  # Reemplazar: self.nuevo_nombre
  ```

- [ ] **Paso 6**: Ejecutar ALL tests
  ```bash
  pytest tests/
  ```

- [ ] **Paso 7**: Ejecutar UI completa y probar TODAS las vistas
  - Importar PDFs
  - Exportar BD
  - Ver dashboard
  - Ejecutar auditoría IA

### 5.4 CHECKLIST: Modificar Método

- [ ] **Paso 1**: ¿Es método CRÍTICO de nivel 1?
  - `refresh_data_and_table()` → ❌ NO cambiar firma
  - `_nav_to_database()` → ❌ NO cambiar firma
  - `_populate_treeview()` → ❌ NO cambiar firma
  - Otros → Continuar

- [ ] **Paso 2**: ¿Tiene binding a eventos Tk?
  ```python
  # Buscar en código bindings
  grep -n "self\\.bind(" ui.py
  grep -n "\\.bind(" ui.py
  ```

- [ ] **Paso 3**: Si cambias firma, actualizar TODOS los callers
  - Buscar: `grep -rn "nombre_metodo(" .`

- [ ] **Paso 4**: Si es método público (sin `_`), verificar uso externo
  - Buscar en `core/`, `ui_helpers/`

- [ ] **Paso 5**: Si cambias tipo de retorno, verificar que callers lo manejan
  ```python
  # ANTES
  def mi_metodo(self) -> None:
      # ...

  # DESPUÉS
  def mi_metodo(self) -> Dict:
      return {'status': 'ok'}

  # ¿Callers esperan dict o ignoran retorno?
  resultado = self.mi_metodo()  # ¿Qué hace con resultado?
  ```

- [ ] **Paso 6**: Agregar type hints si no existen
  ```python
  # CORRECTO (type hints claros)
  def mi_metodo(self, param: str, opcional: int = 5) -> Dict[str, Any]:
      return {'data': param}
  ```

- [ ] **Paso 7**: Ejecutar mypy (si está configurado)
  ```bash
  mypy ui.py
  ```

---

## 6. MATRIZ DE IMPACTO

### 6.1 SI MODIFICO X → SE AFECTA Y, Z

| Modificación | Impacto Directo | Impacto Indirecto | Severidad |
|--------------|-----------------|-------------------|-----------|
| Renombrar `self.master_df` | **TODO EL SISTEMA** | Exportación, Dashboard, Filtros | 🔴 CRÍTICO |
| Renombrar `self.sheet` | Visualización de tabla | Selección, Exportación | 🔴 CRÍTICO |
| Eliminar alias `self.tree` | 50+ líneas fallan | Bindings, Callbacks | 🔴 CRÍTICO |
| Cambiar firma `refresh_data_and_table()` | `process_with_audit.py` | Importación de PDFs | 🔴 CRÍTICO |
| Cambiar firma `_nav_to_database()` | `enhanced_export_system.py` | Navegación post-exportación | 🟠 ALTO |
| Renombrar `self.enhanced_dashboard` | `enhanced_export_system.py` | Pestaña Exportaciones | 🟠 ALTO |
| Renombrar `self._ruta_ultimo_reporte` | `ventana_auditoria_ia.py` | Mensaje de completado IA | 🟡 MEDIO |
| Cambiar layout `main_container` | Visualización completa | Todos los widgets hijos | 🟡 MEDIO |
| Renombrar `self.db_filters` | Filtros de BD | Ninguno | 🟢 BAJO |
| Cambiar `self.current_theme` | Tema visual | Ninguno | 🟢 BAJO |

### 6.2 DEPENDENCIAS DE MÓDULOS EXTERNOS

```
┌─────────────────────────────────────────────────────────────┐
│ enhanced_export_system.py                                    │
├─────────────────────────────────────────────────────────────┤
│ DEPENDE DE:                                                  │
│ • parent_app.master_df         (lectura)                    │
│ • parent_app.tree              (lectura - selection())      │
│ • parent_app._nav_to_database() (llamada)                   │
│ • parent_app.enhanced_dashboard (acceso)                    │
│   └─ .notebook                 (acceso - select(5))         │
│   └─ .refresh_exports_list()   (llamada)                    │
│                                                              │
│ SI SE MODIFICA ALGUNO → enhanced_export_system.py FALLA     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ process_with_audit.py                                        │
├─────────────────────────────────────────────────────────────┤
│ DEPENDE DE:                                                  │
│ • parent_app.refresh_data_and_table() (llamada)             │
│ • parent_app._ultimos_registros_procesados (escritura)      │
│                                                              │
│ SI SE MODIFICA ALGUNO → Importación PDFs FALLA              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ ventana_auditoria_ia.py                                      │
├─────────────────────────────────────────────────────────────┤
│ DEPENDE DE:                                                  │
│ • parent._ruta_ultimo_reporte (lectura)                     │
│                                                              │
│ SI SE MODIFICA → Mensaje de completado NO muestra ruta      │
└─────────────────────────────────────────────────────────────┘
```

### 6.3 CADENA DE DEPENDENCIAS (Efecto Dominó)

```
Usuario hace clic "Exportar Todo"
  ↓
enhanced_export_system.export_full_database()
  ↓
Llama: get_all_records_as_dataframe()
  ↓
Llama: self.execute_export(df, "completa", "excel", dialog)
  ↓
Llama: self.export_to_excel(df, filepath)
  ↓
Llama: self.parent_app._nav_to_database()  ← DEPENDENCIA 1
  ↓
Llama: self.parent_app.enhanced_dashboard.refresh_exports_list()  ← DEPENDENCIA 2
  ↓
Llama: self.parent_app.enhanced_dashboard.notebook.select(5)  ← DEPENDENCIA 3
```

**Si cambias CUALQUIERA de las 3 dependencias, la cadena SE ROMPE.**

---

## 7. REGLAS ABSOLUTAS PARA CORE-EDITOR

### 7.1 LO QUE NUNCA DEBE HACER

#### ❌ REGLA 1: NO RENOMBRAR VARIABLES CRÍTICAS DE NIVEL 1

```python
# ❌ PROHIBIDO
self.master_df → self.data_frame  # ROMPE TODO
self.sheet → self.table_widget     # ROMPE TODO
self.tree → self.data_tree         # ROMPE TODO
self.current_view → self.active_view  # ROMPE navegación
```

#### ❌ REGLA 2: NO ELIMINAR ALIAS `self.tree = self.sheet`

```python
# ❌ PROHIBIDO
# self.tree = self.sheet  ← NO eliminar este alias
```

**Motivo**: Código legado usa `self.tree` en 50+ lugares.

**Si REALMENTE necesitas eliminar el alias**:
1. Buscar TODAS las referencias: `grep -rn "self\.tree" ui.py`
2. Reemplazar MANUALMENTE una por una (NO regex masivo)
3. Verificar que cada reemplazo es correcto
4. Ejecutar tests después de CADA reemplazo

#### ❌ REGLA 3: NO CAMBIAR FIRMAS DE MÉTODOS CRÍTICOS

```python
# ❌ PROHIBIDO cambiar firma
def refresh_data_and_table(self, nuevo_param):  # process_with_audit.py SE ROMPE
    pass

# ❌ PROHIBIDO cambiar nombre
def actualizar_datos_y_tabla(self):  # process_with_audit.py SE ROMPE
    pass
```

**Cambio seguro**:
```python
# ✅ PERMITIDO (parámetro opcional)
def refresh_data_and_table(self, force: bool = False):
    pass
```

#### ❌ REGLA 4: NO CAMBIAR TIPO DE `self.master_df`

```python
# ❌ PROHIBIDO
self.master_df = {'data': [...]}  # DEBE ser DataFrame
self.master_df = None  # NUNCA None, debe ser DataFrame vacío
```

**Correcto**:
```python
# ✅ CORRECTO
import pandas as pd
self.master_df = pd.DataFrame()  # DataFrame vacío
```

#### ❌ REGLA 5: NO MEZCLAR GEOMETRY MANAGERS

```python
# ❌ PROHIBIDO
widget1.pack()
widget2.grid(row=0, column=0)  # ERROR: cannot mix pack() and grid()
```

**Correcto**:
```python
# ✅ CORRECTO (todos pack o todos grid)
widget1.pack()
widget2.pack()

# O

widget1.grid(row=0, column=0)
widget2.grid(row=0, column=1)
```

### 7.2 LO QUE SIEMPRE DEBE HACER

#### ✅ REGLA 1: SIEMPRE BUSCAR REFERENCIAS ANTES DE RENOMBRAR

```bash
# ANTES de renombrar cualquier variable/método
grep -rn "nombre_a_renombrar" .
grep -rn '"nombre_a_renombrar"' .  # Buscar en strings también
```

#### ✅ REGLA 2: SIEMPRE ACTUALIZAR `master_df` DESPUÉS DE CAMBIOS EN BD

```python
# ✅ CORRECTO - Siempre hacer en este orden
from core.database_manager import save_records, get_all_records_as_dataframe

# 1. Modificar BD
save_records(nuevos_datos)

# 2. Actualizar master_df
self.master_df = get_all_records_as_dataframe()

# 3. Actualizar UI
self._populate_treeview(self.master_df)
```

#### ✅ REGLA 3: SIEMPRE USAR TYPE HINTS EN MÉTODOS NUEVOS

```python
# ✅ CORRECTO
def mi_nuevo_metodo(self, param: str, opcional: int = 5) -> Dict[str, Any]:
    return {'status': 'ok', 'data': param}

# ❌ INCORRECTO (sin type hints)
def mi_nuevo_metodo(self, param, opcional=5):
    return {'status': 'ok', 'data': param}
```

#### ✅ REGLA 4: SIEMPRE DOCUMENTAR CAMBIOS IMPORTANTES

```python
# ✅ CORRECTO
# NUEVO MÉTODO (2025-10-24): Exportar selección mejorada
# Motivo: Usuario pidió exportar con filtros
# Depende de: self.master_df, self.db_filters
def exportar_con_filtros(self) -> None:
    """
    Exporta datos aplicando filtros activos.

    Returns:
        None

    Raises:
        ValueError: Si no hay filtros activos
    """
    pass
```

#### ✅ REGLA 5: SIEMPRE PROBAR EN TODAS LAS VISTAS

Después de cualquier cambio UI, probar:
1. ✅ Vista Welcome
2. ✅ Vista Database (tabla)
3. ✅ Vista Dashboard
4. ✅ Vista Análisis IA
5. ✅ Importar PDFs
6. ✅ Exportar BD
7. ✅ Filtros

### 7.3 CHECKLIST FINAL ANTES DE COMMIT

- [ ] **1. Verificar que NO se modificaron variables CRÍTICAS nivel 1**
  - `master_df`, `sheet`, `tree`, `current_view`

- [ ] **2. Verificar que NO se modificaron firmas de métodos críticos**
  - `refresh_data_and_table()`, `_nav_to_database()`, `_populate_treeview()`

- [ ] **3. Buscar referencias a variables/métodos modificados**
  ```bash
  grep -rn "nombre_modificado" .
  ```

- [ ] **4. Ejecutar UI completa y probar flujo completo**
  - Iniciar app
  - Importar PDF de prueba
  - Verificar que se muestra en tabla
  - Exportar a Excel
  - Verificar que navega a Dashboard
  - Aplicar filtros
  - Ejecutar auditoría IA (si aplica)

- [ ] **5. Verificar logs por errores**
  ```bash
  tail -f logs/sistema.log
  # Buscar: ERROR, WARNING, CRITICAL
  ```

- [ ] **6. Generar reporte de cambios en `herramientas_ia/resultados/`**
  ```bash
  python herramientas_ia/editor_core.py --generar-reporte
  ```

- [ ] **7. Actualizar documentación si aplica**
  - Si agregaste método público → Documentar en docstring
  - Si modificaste flujo → Actualizar WORKFLOWS.md

---

## APÉNDICE A: VARIABLES COMPLETAS DE `App.__init__`

### Variables de Estado (Líneas 210-218)

```python
# Estados del nuevo sistema de navegación flotante
self.header_visible = True
self.floating_menu_visible = False
self.welcome_screen_active = True
self.current_view = "welcome"  # welcome, database, visualizar, dashboard

# Variables para tracking de importación y auditoría IA
self._ultimos_registros_procesados = []  # Lista de IDs recién importados
self.ultimos_resultados_ia = None  # Resultados de última auditoría IA
```

### Variables de Configuración (Líneas 187-208)

```python
# Información del usuario
self.info_usuario = info_usuario or {"nombre": "Invitado", "cargo": "N/A", ...}

# Fuentes estándar
self.FONT_TITULO = ("Segoe UI", 22, "bold")
self.FONT_SUBTITULO = ("Segoe UI", 12)
self.FONT_NORMAL = ("Segoe UI", 11)
self.FONT_ETIQUETA = ("Segoe UI", 9, "italic")
self.FONT_NOMBRE_PERFIL = ("Segoe UI", 16, "bold")
self.FONT_BOTONES = ("Segoe UI", 12)

# Configurar tema actual
self.current_theme = tema
self.temas_disponibles = ['superhero', 'flatly', 'cyborg', ...]

# Configurar iconos y foto del usuario
self.iconos = self._cargar_iconos()
self.foto_usuario = self._cargar_foto_usuario()
```

### Variables de Widgets (Creadas en `_create_layout()`)

```python
# Línea 233 - DataFrame maestro
self.master_df = get_all_records_as_dataframe()

# Línea 243 - Sistema de exportación
self.export_system = EnhancedExportSystem(self)

# Línea 1906 - Dashboard avanzado
self.enhanced_dashboard = EnhancedDatabaseDashboard(...)

# Línea 2054-2184 - Widget Sheet (tabla)
self.sheet = Sheet(...)
self.tree = self.sheet  # ALIAS CRÍTICO

# Línea 2280 - Filtros de BD
self.db_filters = {
    'fecha_desde': tk.StringVar(),
    'fecha_hasta': tk.StringVar(),
    'servicio': tk.StringVar(),
    'malignidad': tk.StringVar(),
    'responsable': tk.StringVar()
}

# Líneas 2301, 2305, 2309 - Comboboxes de filtros
self.cmb_servicio = ttk.Combobox(...)
self.cmb_malig = ttk.Combobox(...)
self.cmb_resp = ttk.Combobox(...)
```

---

## APÉNDICE B: MÉTODOS COMPLETOS DE `App`

### Métodos de Navegación

```python
def _nav_to_welcome(self) -> None: ...       # Línea ~600
def _nav_to_database(self) -> None: ...      # Línea 657
def _nav_to_visualizar(self) -> None: ...    # Línea ~700
def _nav_to_dashboard(self) -> None: ...     # Línea ~750
def _nav_to_analisis_ia(self) -> None: ...   # Línea ~1200
```

### Métodos de Datos

```python
def refresh_data_and_table(self) -> None: ...            # Línea 3897
def _populate_treeview(self, df: pd.DataFrame) -> None: ... # Línea 3947
def _actualizar_estadisticas_db(self) -> None: ...       # Línea ~3500
```

### Métodos de Auditoría IA

```python
def _iniciar_auditoria_ia(self, tipo_auditoria: str) -> None: ...  # Línea 722
def _callback_auditoria_completada(self, resultados: List) -> None: ... # Línea ~1300
def _guardar_reporte_ia(self, resultados: List) -> str: ...  # Línea ~1400
```

### Métodos de Filtros

```python
def _aplicar_filtros_bd(self) -> None: ...   # Línea ~2400
def _limpiar_filtros_bd(self) -> None: ...   # Línea ~2500
```

### Métodos de Exportación

```python
# NOTA: Estos están en EnhancedExportSystem, NO en App directamente
# App solo tiene referencias:
self.export_system.export_full_database()
self.export_system.export_selected_data(df)
```

---

## APÉNDICE C: ESTRUCTURA DE ARCHIVOS RELACIONADOS

```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py (270.6KB - ARCHIVO PRINCIPAL)
├── core/
│   ├── enhanced_export_system.py (910 líneas)
│   │   └── EnhancedExportSystem class
│   │       ├── DEPENDE: parent_app.master_df
│   │       ├── DEPENDE: parent_app.tree
│   │       ├── DEPENDE: parent_app._nav_to_database()
│   │       └── DEPENDE: parent_app.enhanced_dashboard
│   │
│   ├── ventana_auditoria_ia.py (914 líneas)
│   │   └── VentanaAuditoriaIA class
│   │       └── DEPENDE: parent._ruta_ultimo_reporte
│   │
│   ├── process_with_audit.py (~300 líneas)
│   │   └── process_ihq_paths_with_audit()
│   │       ├── DEPENDE: parent_app.refresh_data_and_table()
│   │       └── DEPENDE: parent_app._ultimos_registros_procesados
│   │
│   ├── enhanced_database_dashboard.py (~2000 líneas)
│   │   └── EnhancedDatabaseDashboard class
│   │       ├── PROVEE: .notebook
│   │       ├── PROVEE: .import_files_listbox
│   │       └── PROVEE: .refresh_exports_list()
│   │
│   └── database_manager.py
│       ├── get_all_records_as_dataframe() → DataFrame
│       ├── save_records(records: List[Dict])
│       └── get_registro_by_peticion(numero: str) → Dict
│
└── ui_helpers/
    ├── database_helpers.py (318 líneas)
    │   └── Funciones de validación
    ├── ocr_helpers.py
    ├── export_helpers.py
    └── chart_helpers.py
```

---

## APÉNDICE D: EJEMPLO DE CAMBIO SEGURO vs PELIGROSO

### CAMBIO PELIGROSO (NO HACER)

```python
# ❌ ANTES (ui.py línea 3897)
def refresh_data_and_table(self):
    from core.database_manager import get_all_records_as_dataframe
    self.master_df = get_all_records_as_dataframe()
    self._populate_treeview(self.master_df)

# ❌ DESPUÉS (PELIGROSO - cambia firma)
def refresh_data_and_table(self, filtros: Dict):  # ← PARÁMETRO NUEVO OBLIGATORIO
    from core.database_manager import get_all_records_as_dataframe
    df = get_all_records_as_dataframe()
    # Aplicar filtros...
    self.master_df = df_filtrado
    self._populate_treeview(self.master_df)

# ❌ RESULTADO: process_with_audit.py SE ROMPE
# Línea ~195 (process_with_audit.py)
parent_app.refresh_data_and_table()  # TypeError: missing 1 required positional argument: 'filtros'
```

### CAMBIO SEGURO (HACER ESTO)

```python
# ✅ ANTES (ui.py línea 3897)
def refresh_data_and_table(self):
    from core.database_manager import get_all_records_as_dataframe
    self.master_df = get_all_records_as_dataframe()
    self._populate_treeview(self.master_df)

# ✅ DESPUÉS (SEGURO - parámetro opcional)
def refresh_data_and_table(self, filtros: Optional[Dict] = None):
    from core.database_manager import get_all_records_as_dataframe
    df = get_all_records_as_dataframe()

    if filtros:
        # Aplicar filtros si se proporcionan
        df = self._aplicar_filtros_internos(df, filtros)

    self.master_df = df
    self._populate_treeview(self.master_df)

# ✅ RESULTADO: process_with_audit.py SIGUE FUNCIONANDO
# Línea ~195 (process_with_audit.py)
parent_app.refresh_data_and_table()  # ✅ OK (filtros es opcional)

# Y ADEMÁS ahora puedes llamar con filtros
parent_app.refresh_data_and_table({'servicio': 'Oncología'})  # ✅ OK también
```

---

## CONCLUSIÓN

Este documento contiene **TODA** la información necesaria para que `core-editor` modifique UI sin romper nada.

**Reglas de oro**:
1. ❌ NO tocar variables CRÍTICAS nivel 1
2. ❌ NO cambiar firmas de métodos llamados externamente
3. ❌ NO eliminar alias `self.tree = self.sheet`
4. ✅ SIEMPRE buscar referencias antes de renombrar
5. ✅ SIEMPRE probar en todas las vistas después de cambios

**Si tienes dudas**:
1. Buscar en este documento
2. Usar grep para encontrar referencias
3. Simular cambio primero con `--simular`
4. Consultar con usuario antes de aplicar

**Última actualización**: 2025-10-24
**Versión documento**: 1.0.0
**Autor**: system-diagnostician + data-auditor (análisis colaborativo)
