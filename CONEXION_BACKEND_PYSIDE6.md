# 🔌 CONEXIÓN BACKEND - PySide6

## ✅ Corrección Aplicada

**Fecha:** 20 Noviembre 2025
**Problema:** La UI PySide6 no se conectaba al backend existente
**Estado:** ✅ RESUELTO

---

## 🔧 Cambios Realizados

### 1. OCRWorker Corregido

**Archivo:** `pyside6_ui/workers/ocr_worker.py`

**Problema:**
```python
# ❌ INCORRECTO - La clase UnifiedExtractor NO existe
from core.unified_extractor import UnifiedExtractor
extractor = UnifiedExtractor()
```

**Solución:**
```python
# ✅ CORRECTO - Usar la función process_ihq_paths()
from core.unified_extractor import process_ihq_paths
casos_procesados = process_ihq_paths(
    pdf_paths=self.pdf_paths,
    output_dir=temp_output
)
```

---

## 📋 Mapeo de Funciones Backend → PySide6

### Procesamiento de PDFs

| Frontend (PySide6) | Backend (Existente) | Estado |
|-------------------|---------------------|--------|
| `OCRWorker.run()` | `process_ihq_paths()` | ✅ **CONECTADO** |
| `DatabaseView.load_data_from_database()` | `get_all_records_as_dataframe()` | ✅ **CONECTADO** |
| `ExportWorker.run()` | `EnhancedExportSystem` | ⏳ Pendiente |
| `AuditWorker.run()` | `AuditorSistema` (FUNC-01) | ⏳ Pendiente |

---

## 🧪 Cómo Probar

### 1. Iniciar la versión PySide6

```bash
# Opción A: Doble clic
iniciar_pyside6.bat

# Opción B: Terminal
venv0\Scripts\activate
python main_pyside6.py
```

### 2. Importar un PDF

1. Ve al tab **"📥 Importación de PDFs"**
2. Click en **"📂 Seleccionar Archivos PDF"**
3. Selecciona un PDF de prueba de `pdfs_patologia/`
4. Confirma la importación
5. El worker OCR debería:
   - ✅ Procesar el PDF con `unified_extractor`
   - ✅ Guardar en BD usando `database_manager`
   - ✅ Mostrar progreso en UI

### 3. Visualizar Datos

1. Ve al tab **"👁️ Visualizar Datos"**
2. Click en **"🔄 Actualizar"**
3. Deberías ver:
   - ✅ Datos cargados desde BD
   - ✅ Tabla con casos procesados
   - ✅ Mensaje de éxito

---

## 🔍 Arquitectura de Conexión

```
┌─────────────────────────────────────────────────┐
│         PYSIDE6 UI (Nuevo)                      │
├─────────────────────────────────────────────────┤
│                                                 │
│  DatabaseView                                   │
│  ├─ import_requested.emit(files)                │
│  └─ load_data_from_database()                   │
│      ↓                                           │
│  OCRWorker (QThread)                            │
│  ├─ progress.emit(%, msg)                       │
│  ├─ finished.emit(results)                      │
│  └─ run()                                        │
│      ↓                                           │
├─────────────────────────────────────────────────┤
│         BACKEND (Existente) ✅                   │
├─────────────────────────────────────────────────┤
│                                                 │
│  core/unified_extractor.py                      │
│  └─ process_ihq_paths(pdf_paths, output_dir)   │
│      ├─ OCR con ocr_processor.py                │
│      ├─ Extracción con extractors/              │
│      └─ Retorna: casos_procesados (int)         │
│                                                 │
│  core/database_manager.py                       │
│  ├─ inicializar_base_datos()                    │
│  ├─ guardar_registro_completo(datos)            │
│  └─ get_all_records_as_dataframe()              │
│      └─ Retorna: pd.DataFrame                   │
│                                                 │
└─────────────────────────────────────────────────┘
```

---

## ⚠️ Limitaciones Actuales

### 1. Progreso Interno NO Disponible

**Problema:**
`process_ihq_paths()` del backend **NO emite progreso interno**. Solo retorna el total al final.

**Solución Temporal:**
El `OCRWorker` simula progreso con incrementos del 10% cada 100ms.

**Mejora Futura:**
Modificar `unified_extractor.py` para emitir signals o usar callback de progreso.

### 2. Casos Individuales

**Problema:**
`process_ihq_paths()` procesa **TODOS** los PDFs de golpe. No hay desglose por archivo.

**Solución Temporal:**
El worker estima casos por archivo: `casos_totales // len(archivos)`

**Mejora Futura:**
Modificar backend para retornar resultados por archivo.

---

## 🚀 Próximos Pasos (Workers Pendientes)

### ExportWorker
```python
# Conectar con:
from core.enhanced_export_system import EnhancedExportSystem

export_system = EnhancedExportSystem()
export_system.export_to_excel(df, output_path)
```

### AuditWorker
```python
# Conectar con:
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.auditar_caso_inteligente(case_id)
```

### RepairWorker
```python
# Conectar con:
from herramientas_ia.auditor_sistema import AuditorSistema

auditor = AuditorSistema()
resultado = auditor.reprocesar_caso_completo(case_id)
```

---

## 📊 Estado de Integración Backend

| Módulo Backend | Función/Clase | PySide6 Worker | Estado |
|---------------|---------------|----------------|--------|
| `unified_extractor` | `process_ihq_paths()` | `OCRWorker` | ✅ Conectado |
| `database_manager` | `get_all_records_as_dataframe()` | `DatabaseView` | ✅ Conectado |
| `database_manager` | `inicializar_base_datos()` | `OCRWorker` | ✅ Conectado |
| `enhanced_export_system` | `EnhancedExportSystem` | `ExportWorker` | ⏳ Pendiente |
| `auditor_sistema` | `AuditorSistema.auditar_caso_inteligente()` | `AuditWorker` | ⏳ Pendiente |
| `auditor_sistema` | `AuditorSistema.reprocesar_caso_completo()` | `RepairWorker` | ⏳ Pendiente |
| `llm_client` | `LLMClient` | `AuditWorker` | ⏳ Pendiente |
| `huv_web_automation` | `automatizar_entrega_resultados()` | `WebWorker` | ⏳ Pendiente |

**Progreso:** 3/8 conexiones completadas (37.5%)

---

## ✅ Verificación de Funcionamiento

### Checklist de Testing

- [ ] **Iniciar UI PySide6**
  ```bash
  iniciar_pyside6.bat
  ```

- [ ] **Importar PDF**
  - Tab "Importación de PDFs"
  - Seleccionar PDF de `pdfs_patologia/`
  - Confirmar importación
  - Verificar progreso en UI
  - Verificar mensaje de éxito

- [ ] **Visualizar Datos**
  - Tab "Visualizar Datos"
  - Click "Actualizar"
  - Verificar tabla con datos
  - Verificar conteo de registros

- [ ] **Verificar BD**
  ```bash
  # Desde terminal Python
  from core.database_manager import get_all_records_as_dataframe
  df = get_all_records_as_dataframe()
  print(f"Total registros: {len(df)}")
  ```

---

## 🐛 Troubleshooting

### Error: "cannot import name 'UnifiedExtractor'"

✅ **RESUELTO** - El archivo ya fue corregido para usar `process_ihq_paths()`

### Error: "No module named 'core.unified_extractor'"

**Causa:** Ruta incorrecta o entorno virtual equivocado

**Solución:**
```bash
# Verificar que estás en la carpeta correcta
cd ProyectoHUV9GESTOR_ONCOLOGIA

# Activar entorno correcto
venv0\Scripts\activate

# Verificar importación
python -c "from core.unified_extractor import process_ihq_paths; print('✅ OK')"
```

### UI se congela durante procesamiento

**Causa:** Worker no está corriendo en thread separado

**Solución:**
Verificar que `OCRWorker` hereda de `QThread` y se llama `.start()` (no `.run()`)

---

## 📚 Documentación Relacionada

- **Plan de migración:** `PLAN_MIGRACION_PYSIDE6.md`
- **Estado actual:** `README_MIGRACION.md`
- **Cómo iniciar:** `COMO_INICIAR.md`
- **Backend EVARISIS:** `.claude/CLAUDE.md`

---

**Última Actualización:** 20 Noviembre 2025
**Autor:** Sistema Claude + Daniel Restrepo
**Versión:** 1.0
