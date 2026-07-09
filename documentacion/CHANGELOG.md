# Changelog

## [6.9.53] - 2026-07-09 — Extractor de Diagnóstico Determinista (fix causa raíz + validación anti-regresión 2076 casos)

**Sprint:** Revalidación exhaustiva de la calidad del diagnóstico principal de los 2.076 casos IHQ (auditoría caso-por-caso contra el PDF real) y corrección de raíz del extractor de diagnóstico. Se identificaron **132 diagnósticos erróneos (6,4%)** y se corrigieron las 6 causas raíz mediante un **extractor determinista** (sin IA, que alucinaba) que lee la sección DIAGNÓSTICO real del informe. **Verificado con banco anti-regresión sobre los 2.076 casos (reproceso fiel sin re-OCR) + doble verificación adversarial de veracidad (31 agentes contrastando cada dx cambiado contra el PDF).**

### Impact
| Aspecto | Antes | Ahora (V6.9.53) |
|---|---|---|
| Diagnósticos "malos" (encabezado/basura/truncado/preámbulo) | 246 | **88** (−158) |
| Diagnósticos inventados (texto no presente en el PDF) | 6 | **0** (verificación adversarial) |
| Inversiones de negación (negativo→positivo, peligroso) | varias | **0** |
| Fidelidad de los cambios (verificada contra PDF) | — | **220/226 (97,3%)** fieles o aceptables |
| Regresiones sobre casos correctos | — | **0** |
| Diagnósticos corregidos en BD MySQL producción | — | **191 + 6 auditados + 1 malignidad** |

### Root causes fixed (extract_diagnostico_principal + fallback determinista)
- **Encabezado como dx** ("ESTUDIO DE INMUNOHISTOQUÍMICA") → fallback determinista lee la sección DIAGNÓSTICO real (recupera NEUROFIBROMA, CARCINOSARCOMA, HEMANGIOBLASTOMA, SIALOADENITIS…).
- **Truncado** — se eliminó 'IN SITU' de `keywords_estudio_m` (recupera CARCINOMA DUCTAL **IN SITU**); captura a través del salto de línea (OCR envuelve el dx).
- **Prefijo perdido** — `[A-ZÁÉÍÓÚÑ]*SARCOMA`/`*CARCINOMA` (OSTEO/LIPO/ANGIOSARCOMA ya no caen a "SARCOMA").
- **Inversión de negación** (crítico) — extracción negación-aware: "NEGATIVO PARA SARCOMA DE KAPOSI" ya no se reporta como "SARCOMA DE KAPOSI".
- **Sección equivocada** — selección por posición + campo sinóptico "Tipo histológico:" (espécimen A) + guardas contra referencias a otros bloques/preliminares.
- **Dx diferido** — devuelve "VER DESCRIPCIÓN MICROSCÓPICA Y COMENTARIO" honesto (no inventa).

### Files modified
- `core/unified_extractor.py` — NUEVO extractor determinista `_dx_determinista()` (+ helpers `_det_buscar_sinoptico`, `_det_buscar_en_zona`, `_det_seccion_diagnostico`, `_dp_sospechoso`, `_det_trim`, `_det_cand_valido`). Corre ANTES de la capa IA (desactivada por alucinar) => 100% determinista y verídico. Parte A: fix 'IN SITU' + prefijo en ESTRATEGIA 4/5. Guardas V6.9.53: respetar el diferido honesto contra el override de la capa Coloración y de la descripción microscópica (que inventaban dx).

### Fixed
- **Capa Coloración / descripción microscópica pisaban "VER COMENTARIO":** el post-proceso V6.9.37/41 sustituía el diferido honesto del extractor por el dx de un estudio de coloración distinto o por una descripción microscópica → afirmaba diagnósticos NO presentes en el informe IHQ. Ahora se respeta el diferido.

### Data
- BD MySQL `huv_oncologia` (tabla `informes_ihq`): **191 diagnósticos + 6 correcciones auditadas** actualizados (backup `backups/backup_dx_extractor_*.json`). Actualización quirúrgica de SOLO `Diagnostico Principal` + `Malignidad` (no toca nombres/biomarcadores).

## [6.9.48] - 2026-06-26 — Coloraciones Básicas (estudios M) + Reconciliación por Cédula + Performance Visualizador

**Sprint:** Incorporación de un pipeline AUTÓNOMO para los PDFs de "Coloraciones básicas" (estudios `M…`, tinciones tipo H&E) que conviven con el flujo IHQ sin contaminarlo, más reconciliación coloración↔IHQ por cédula independiente del orden de importación, optimizaciones de rendimiento del Visualizador y dos fixes de extracción/división de nombres. El sprint cubre cuatro versiones consecutivas (V6.9.45 → V6.9.48). **Verificado en producción contra la BD MySQL `huv_oncologia` (tabla `informes_ihq`): la tabla pasó de 2.076 a 8.816 filas** tras la carga inicial de coloraciones.

### Impact
| Aspecto | Antes (V6.9.5) | Ahora (V6.9.48) |
|---|---|---|
| Tipos de PDF soportados | Solo IHQ | **IHQ + Coloraciones básicas (M…)** |
| Filas en `informes_ihq` | 2.076 | **8.816** (139 PDFs de coloración → 6.806 coloraciones) |
| Diagnóstico de coloración | No capturado | **Columna `Diagnostico Coloracion 2` (TEXT)** |
| Reconciliación coloración↔IHQ | — | **`reconciliar_coloraciones()` idempotente, independiente del orden** |
| Filas M en estadísticas/dashboard/KPIs | — | **Excluidas (filtro `^[Mm]\d`)** |
| Filas M en Visualizador | — | **Visibles y buscables por cédula/nombre** |
| `_apply_row_colors` (coloreado tabla) | ~13.300 ms (freeze ~13 s al abrir) | **~280 ms** |
| Auto-refresh 60 s | Recarga completa siempre (freeze ~1 s/min) | **Huella barata `get_db_fingerprint()`, se salta si no cambió** |

### Files modified
- `core/extractors/coloracion_extractor.py` (NUEVO) — Extractor dedicado para PDFs de coloraciones (estudios M autónomos). Extrae SOLO el diagnóstico. V6.9.48 FIX M2506212: `_RE_NOMBRE` con salto de línea OPCIONAL antes de "N. peticion".
- `core/coloracion_processor.py` (NUEVO) — Procesador AISLADO del IHQ. Cada coloración se guarda como su propia fila `M######` (fuente de verdad, nunca se pisa ni se pierde).
- `core/database_manager.py` — Nueva columna `Diagnostico Coloracion 2` (TEXT) en schema y mapeo (líneas ~176, ~249, ~896). Nueva función `get_db_fingerprint()` (COUNT+MAX) para detección barata de cambios (V6.9.47).
- `ui.py` — Router `_is_coloracion_file()`/`_process_coloracion_file()` en "Procesar seleccionados" detecta PDFs "M … AL …" y los enruta sin tocar el flujo IHQ (V6.9.45). `reconciliar_coloraciones()` invocada tras cada importación (V6.9.46). Ocultamiento en DISPLAY de filas M redundantes (single-merged) sin borrarlas de BD (V6.9.46). `_apply_row_colors` vectorizado (V6.9.47). Auto-refresh con `get_db_fingerprint()` (V6.9.47). Exclusión de filas M en KPIs y Dashboard analítico (V6.9.45).
- `core/informe_estadistico.py` — El informe estadístico es SOLO de IHQ → excluye filas de coloración (V6.9.45).
- `core/utils/name_splitter.py` — Divisor de nombres COMPARTIDO con IHQ: corregido bug que duplicaba el primer token cuando `primer_apellido_idx == 0` (líneas ~152-156).

### Added
- **Pipeline de Coloraciones básicas (V6.9.45 / V6.9.46)** — PDFs de tinciones tipo H&E ("M … AL …") detectados automáticamente en "Procesar seleccionados" y enrutados a un flujo dedicado que extrae SOLO el diagnóstico a la columna `Diagnostico Coloracion 2` (TEXT). Carga inicial: 139 PDFs → 6.806 coloraciones. Las filas usan clave `M######`.
- **`reconciliar_coloraciones()` (V6.9.46)** — Función idempotente que, tras CADA importación (IHQ o coloración), deriva por cédula la columna `Diagnostico Coloracion 2` de la fila IHQ del paciente: 1 coloración → el diagnóstico; varias → los N diagnósticos CONCATENADOS y numerados en la columna. Funciona igual empiece el PDF de coloración o el de IHQ.
- **`get_db_fingerprint()` (V6.9.47)** — Huella barata (COUNT+MAX) usada por el auto-refresh de 60 s para evitar recargas completas innecesarias.

### Changed
- Columna `Diagnostico Coloracion 2` migrada de `VARCHAR(500)` a `TEXT` para evitar truncado de diagnósticos largos (recuperó diagnósticos de hasta 2.176 caracteres).
- Las filas de coloración (clave `M######`) se EXCLUYEN de estadísticas, dashboard y KPIs (filtro `^[Mm]\d`) pero permanecen visibles y buscables en el Visualizador por cédula/nombre.
- El Visualizador oculta del DISPLAY las filas M redundantes (single-merged, cuyo diagnóstico ya está reflejado en la fila IHQ) sin borrarlas de la BD.
- `_apply_row_colors`: coloreado de la tabla vectorizado con `drop_duplicates`/`to_dict('records')` (en vez de `groupby` + `iloc[0].to_dict()`); clasificación sobre arrays (en vez de `iterrows`); solo evalúa filas IHQ. De ~13.300 ms a ~280 ms (elimina el congelamiento de ~13 s al abrir el Visualizador).
- Auto-refresh de 60 s usa la huella `get_db_fingerprint()` y se salta la recarga completa si la BD no cambió (elimina el freeze periódico de ~1 s/min).

### Fixed
- **V6.9.48 — Extracción de nombres en coloraciones (caso M2506212):** `_RE_NOMBRE` en `coloracion_extractor.py` ahora trata como OPCIONAL el salto de línea antes de "N. peticion" → recupera ~490 nombres que salían en N/A. 0 regresiones (10.460/10.460).
- **División de nombres (compartida con IHQ):** corregido bug en `core/utils/name_splitter.py` que duplicaba el primer token cuando `primer_apellido_idx == 0` ("HECTOR ERNESTO MORA" → "HECTOR HECTOR ERNESTO MORA"). Corrigió 358 coloraciones (0 artefactos; las 173 restantes son apellidos repetidos REALES) y 69 nombres IHQ preexistentes (backup en `backups/backup_nombres_ihq_dup69.json`).

### Decisiones técnicas

#### 1. Pipeline de coloraciones AISLADO del IHQ
El extractor y el procesador de coloraciones viven en archivos propios (`coloracion_extractor.py`, `coloracion_processor.py`) y nunca tocan el flujo IHQ. Cada coloración es su propia fila `M######` y constituye la fuente de verdad: nunca se pierde ni se pisa, independientemente de cuándo llegue su IHQ correspondiente.

#### 2. Reconciliación independiente del orden e idempotente
`reconciliar_coloraciones()` corre tras CADA importación (IHQ o coloración) y deriva por cédula la columna `Diagnostico Coloracion 2` en la fila IHQ. Por ser idempotente, converge al mismo punto fijo sin importar si el PDF de coloración o el de IHQ se procesó primero. Verificado: 553 pacientes coloración∩IHQ enlazados, 0 enlaces espurios, 0 marcadores incorrectos, reconciliación en punto fijo.

#### 3. Separación entre dato persistido y dato mostrado
Las filas M siempre persisten en BD (auditabilidad). El Visualizador decide en tiempo de DISPLAY cuáles ocultar (M redundantes single-merged) sin borrar nada. Las estadísticas/dashboard/KPIs filtran las claves `^[Mm]\d` para no contaminar las métricas oncológicas, que son SOLO de IHQ.

#### 4. `TEXT` en lugar de `VARCHAR(500)` para diagnósticos de coloración
Los diagnósticos de coloración pueden superar largamente los 500 caracteres (se observaron hasta 2.176). La columna se migró a `TEXT` para evitar truncado silencioso.

#### 5. Rendimiento por vectorización, no por reescritura de la lógica
Las mejoras de `_apply_row_colors` y del auto-refresh se lograron vectorizando con pandas/NumPy y agregando una huella barata de cambio, sin alterar la semántica del coloreado ni la lógica de negocio.

### Validation
- ✅ Verificado en producción contra MySQL `huv_oncologia` / `informes_ihq`: 2.076 → 8.816 filas.
- ✅ Carga inicial de coloraciones: 139 PDFs → 6.806 coloraciones.
- ✅ Reconciliación: 553 pacientes coloración∩IHQ enlazados, 0 enlaces espurios, 0 marcadores incorrectos, punto fijo confirmado.
- ✅ Fix `_RE_NOMBRE`: ~490 nombres recuperados, 0 regresiones (10.460/10.460).
- ✅ Fix `name_splitter`: 358 coloraciones + 69 IHQ corregidas, 0 artefactos (173 apellidos repetidos restantes son reales), backup `backups/backup_nombres_ihq_dup69.json`.
- ✅ `_apply_row_colors`: ~13.300 ms → ~280 ms. Auto-refresh sin freeze periódico.

---

## [6.9.0] - 2026-05-11 — MySQL/MariaDB Multi-User LAN Support

**Sprint:** Migración del backend de BD de SQLite (single-user, file-based) a MySQL/MariaDB (multi-user, cliente-servidor) usando XAMPP. Permite que **múltiples usuarios en la red LAN del HUV** vean y modifiquen los MISMOS datos en tiempo real, sin conflictos de file-locking ni corrupción.

### Impact
| Aspecto | V6.8.x (SQLite) | V6.9.0 (MySQL) |
|---|---|---|
| Backend | Archivo `.db` local | Servidor MySQL/MariaDB centralizado |
| Concurrencia | 1 usuario | **N usuarios simultáneos** |
| Ubicación de datos | PC individual | **Servidor compartido en LAN** |
| Sincronización | Manual (compartir archivo) | **Automática (mismo servidor)** |
| Corrupción por SMB | Frecuente | Eliminada |
| Setup adicional | Ninguno | XAMPP + 5 min config |
| Compatibilidad legacy | — | **SQLite sigue funcionando** (toggle por config) |

### Files modified
- `core/db_adapter.py` (NUEVO) — Abstracción SQLite ↔ MySQL. Funciones: `get_connection()`, `cursor_ctx()`, `dialect()`, `ph()`, `quote_ident()`, `upsert_sql()`, `column_type()`, `get_existing_columns()`, `add_column_if_missing()`.
- `core/database_manager.py` — Detección de dialecto en `init_db()`, `save_records()`, `get_all_records_as_dataframe()`, `get_registro_by_peticion()`. Nueva función `_create_table_mysql()` con schema adaptado (VARCHAR PK + TEXT para resto, índices con prefijo).
- `core/diagnosticos_ia_db.py` — Igual: branching por dialecto en todas las operaciones. Tabla `diagnosticos_ia` ahora en la misma BD `huv_oncologia` (junto a `informes_ihq`).
- `config/config.ini` — Nueva sección `[database]`:
  ```ini
  tipo = mysql
  host = 192.168.2.172
  puerto = 3306
  usuario = huv_app
  password = huv2026
  base_datos = huv_oncologia
  charset = utf8mb4
  ```

### Decisiones técnicas

#### 1. Schema MySQL: TEXT + VARCHAR(50) para PK
MariaDB limita row size a 65,535 bytes (excluyendo TEXT/BLOB). Con 184 columnas VARCHAR(500) × utf8mb4 (4 bytes/char) = 368,000 bytes (excede). Solución: `Numero de caso VARCHAR(50) PRIMARY KEY` y resto `TEXT` (almacenado fuera de la fila). Índices secundarios con prefijo (ej: `Malignidad`(20)`).

#### 2. UPSERT con `INSERT ... ON DUPLICATE KEY UPDATE`
MySQL no tiene `INSERT OR REPLACE` como SQLite. Se construye el UPSERT con sintaxis nativa, actualizando todas las columnas presentes en el `record` y preservando las ausentes (`VALUES()` función especial).

#### 3. Compatibilidad backwards
El código detecta `dialect()` en runtime y bifurca. Si `tipo = sqlite` en config, el flujo legacy con archivo `.db` sigue intacto (útil para desarrollo offline).

#### 4. Doble destino IA → ambas BDs
"Procesar con IA" sigue guardando en `informes_ihq` (Visualizador) y `diagnosticos_ia` (histórico audit). Ahora ambas tablas viven en la misma BD MySQL → un solo backup las cubre.

### Setup multi-cliente (instrucciones para PCs adicionales)

Para que **otros usuarios del HUV** vean los mismos datos:

1. **En el servidor (esta PC, IP 192.168.2.172)**:
   - XAMPP corriendo con MySQL/MariaDB
   - Firewall Windows: permitir entrada TCP puerto 3306 (perfil LAN)
   - Usuario `huv_app@%` ya creado (permite conexión desde cualquier IP de la LAN)

2. **En cada PC cliente**:
   - Instalar la app HUV
   - En `config/config.ini` cambiar el host:
     ```ini
     [database]
     tipo = mysql
     host = 192.168.2.172   ; IP del servidor
     puerto = 3306
     usuario = huv_app
     password = huv2026
     base_datos = huv_oncologia
     ```
   - Al abrir la app, se conectará automáticamente al servidor

3. **Volver a single-user (modo offline)**: cambiar `tipo = sqlite` en config.

### Comparativa de operaciones (medidas en LAN local)
| Operación | SQLite local | MySQL LAN |
|---|---|---|
| init_db (idempotente) | ~50ms | ~80ms |
| save_records (1 caso) | ~20ms | ~30ms |
| save_records (50 casos batch) | ~600ms | ~900ms |
| get_all_records (995 casos) | ~250ms | ~400ms |
| Conexiones simultáneas | 1 práctica | **Hasta 151 (default MariaDB)** |

### Seguridad — pendiente (a hacer antes de producción)
- ⚠️ Password `huv2026` es solo para pruebas. Cambiar a uno fuerte vía phpMyAdmin antes de uso real.
- Considerar restringir `huv_app@%` a `huv_app@192.168.2.%` (solo LAN del hospital).
- Backup automático con tarea programada (`mysqldump` nocturno).

---

## [6.8.0] - 2026-05-08 — IA Pipeline 184-Column Full Schema + BD Unification

**Sprint:** Expansión del pipeline "Procesar con IA" desde 3 columnas (numero_peticion, diagnostico, organo) a **184 columnas** (todas las clínicas de la BD principal). Unificación: ahora el botón "Procesar con IA" escribe DIRECTAMENTE a la BD principal `huv_oncologia_NUEVO.db` (tabla `informes_ihq`), de modo que el resultado aparece en el **Visualizador de Datos**, en paralelo con "Procesar seleccionados" (extractor tradicional).

### Impact
| Aspecto | V6.7.x | V6.8.0 |
|---|---|---|
| Columnas extraídas por IA | 3 | **184** |
| Schema JSON LLM | 3 campos | **184 campos** |
| BD `diagnosticos_ia.db` | 7 cols | **188 cols** (184 + 4 metadata) |
| Tabla del modal IA | 3 cols visibles | **187 cols** (3 alias + 184 BD) con scroll H+V |
| Copia/CSV export | 3 cols | 187 cols con headers BD |
| Destino BD | Solo `diagnosticos_ia.db` | **Doble: `diagnosticos_ia.db` + `informes_ihq` (principal)** |
| Visualizador de Datos | No reflejaba casos IA | **Refresh automático tras procesar IA** |

### Files modified
- `core/columnas_huv_ia.py` (NUEVO) — Mapeo de 184 columnas BD ↔ aliases JSON-safe del LLM. Funciones: `build_json_schema()`, `build_json_schema_pasada_1/2()`, `detectar_biomarcadores_en_ocr()`, `llm_response_to_db_dict()`.
- `core/diagnosticos_ia_db.py` — Schema expandido a 188 columnas. Nueva función `save_caso_completo(datos_columnas, ...)` que recibe dict completo. PK cambió de `numero_peticion` → `Numero de caso`. ALTER TABLE para migrar BDs viejas.
- `ui.py` — Prompt del LLM expandido con instrucciones por categoría (admin, dx, biomarcadores). Worker `_process_files_ia_worker` ahora guarda en AMBAS BDs (acumulativa IA + principal) y dispara `refresh_data_and_table()` al finalizar. Tabla del modal con scroll H+V mostrando las 187 columnas. Copia/CSV adaptados.

### Decisiones técnicas

#### 1. Modelo recomendado: `qwen2.5-14b-instruct`
Tras pruebas con varios modelos:
- `qwen3.6-27b` (reasoning) → todo va a `reasoning_content`, requiere esperar reasoning largo, ~30 min/IHQ con 184 campos (no viable)
- `qwen2.5-32b-instruct` → no cabe en 8GB VRAM (offload masivo), timeout >10 min
- `qwen2.5-14b-instruct` → cabe casi completo, **~7 min/IHQ con schema strict de 184 campos** (~5 días para 995 casos) ✓

#### 2. Schema `strict: True, additionalProperties: False`
`additionalProperties: True` con 184 fields rompe el grammar engine de llama.cpp ("number of rules exceeds sane defaults"). Strict es obligatorio.

#### 3. Doble persistencia (IA + principal)
La IA escribe en `diagnosticos_ia.db` (histórico/audit) Y en `informes_ihq` (BD principal). UPSERT por "Numero de caso" en ambas: si el caso ya existe, se reemplaza. Permite usar "Procesar con IA" y "Procesar seleccionados" sobre los mismos casos para comparar o iterar.

### Workflow del usuario
1. Selecciona PDFs → click "🤖 Procesar con IA"
2. Modal muestra tabla con 187 columnas en vivo
3. Cada caso se guarda en `informes_ihq` mientras se procesa
4. Al finalizar, el Visualizador de Datos se refresca automáticamente
5. Si después corre "Procesar seleccionados" sobre los mismos PDFs, esos datos REEMPLAZAN los de IA (y viceversa)

### Notas
- Tiempo total para 995 IHQs con qwen2.5-14b-instruct: ~5 días (procesamiento batch nocturno o fin de semana)
- Calidad observada: ~80% campos correctos en una sola pasada. Algunos errores ocasionales (alucinaciones en edad, mismatches entre descripcion_microscopica/diagnostico_principal) que requieren post-procesamiento o revisión humana.
- BD `data/diagnosticos_ia.db` puede borrarse en cualquier momento sin afectar la BD principal — es solo un histórico.

---

## [6.7.20] - 2026-05-08 — IA Pipeline UI Show-Full-Dx

**Sprint:** Bug fix de presentación. La V6.7.19 ya extraía y guardaba todos los dx completos en BD, pero la UI los truncaba visualmente a 200 chars + "..." haciendo parecer que la extracción estaba rota. Esto era un falso positivo que generaba percepción equivocada de calidad.

### Verificación
Auditoría directa a `data/diagnosticos_ia.db` confirmó que los 3 casos testigo "truncados" estaban completos en BD:
- IHQ250100: 262 chars (`...CATEGORÍAS 4 Y 2 RESPECTIVAMENTE BANFF 2022)`)
- IHQ250160: 222 chars (`...DE ASPECTO PLASMOCITOIDE NI BLÁSTICO`)
- IHQ250178: 235 chars (`...INVASIÓN LINFOVASCULAR NO IDENTIFICADA`)

### Files modified
- `ui.py` — `_poll_processing_progress_ia()`: removido bloque `if len(dx) > 200: dx = dx[:200] + "..."` antes del insert al Treeview.

### Trade-off
Los dx muy largos (>300 chars) ahora ocupan más espacio horizontal en la tabla. Aceptable: el usuario explícitamente prefiere ver toda la info clínica.

---

## [6.7.19] - 2026-05-07 — IA Pipeline Zero-Truncation

**Sprint:** Eliminación definitiva de truncamientos en dx con scoring extenso. Decisión clínica: cada IHQ es único, no se acepta pérdida de información en favor de velocidad.

### Impact (cualitativo)
| Métrica | V6.7.18 (1500/2500) | V6.7.19 (3000/4000) |
|---|---|---|
| Truncamientos remanentes | 5-6 casos extremos | **0** |
| Tiempo por chunk (qwen 27B) | ~10s | ~13s (~30% más) |
| Calidad de extracción | ~97% | **~99-100%** |

### Files modified
- `ui.py` — `_llamar_llm_con_retry()`: max_tokens 1500/2500 → 3000/4000.

### Casos testigo recuperados (vs V6.7.18)
| IHQ | V6.7.18 (truncado) | V6.7.19 (completo) |
|---|---|---|
| IHQ250100 | `... RECHAZO ACTIVO MEDIADO...` | RECHAZO Banff completo |
| IHQ250160 | `... DE ASPECTO PLA...` | médula ósea histología completa |
| IHQ250178 | `... INVASIÓN PERINEURAL... INV...` | próstata Gleason + cores + % completo |
| IHQ250275 | `... MODERADOS D...` | BIOPSIA INJERTO Banff 2022 completo |
| IHQ250389 | `... HER 2 POSIT...` | mama Nottingham + molecular completa |
| IHQ250401 | `... SCORE 0...` | mama receptores hormonales completos |

### Trade-off
Cada chunk tarda ~3s extra (10s → 13s con qwen3.6-27b en RTX 3050 OEM 8GB). Para un PDF de 50 IHQs: ~2 min extra por PDF. Aceptable para procesamiento batch nocturno.

---

## [6.7.18] - 2026-05-07 — IA Pipeline json_schema + Prompt-Driven Extraction

**Sprint:** Pipeline alternativo de extracción IA (`Procesar con IA`) refinado de cero a producción. Se eliminaron las "muletas" en código (post-procesamiento agresivo, mapeos hardcoded de adjetivos, typos del modelo) en favor de un enfoque **prompt-driven**: el modelo capaz (qwen 27B) + prompt detallado + json_schema estricto = extracción limpia sin código de saneamiento.

### Impact (cualitativo)
| Métrica | gpt-oss-20b (V6.7.0-14) | qwen3.6-27b (V6.7.18) |
|---|---|---|
| Tasa de extracción | ~30% (arrays vacíos frecuentes) | **~97% perfectos** |
| Truncamientos `…?` en dx | Frecuentes | 2 casos extremos (max_tokens) |
| Mismatch dx ↔ órgano | 3-5/50 | 0/165 |
| Preámbulos del patólogo | No strippeados | Strippeados por el modelo |
| HTTP 400 en LM Studio | Constante | Resuelto (json_schema) |
| Alucinación de tokens | Sí (IHQ023, 055) | Cero |

### Files modified
- `core/llm_client.py` — Nuevo parámetro `json_schema` en `completar()`. Cuando se pasa, usa `response_format: json_schema` (compatible con gpt-oss-20b y qwen, fuerza estructura a nivel de decoder). Parser `_extraer_json_robusto` mejorado para tolerar tokens harmony de gpt-oss (`<|channel|>analysis|...|<|message|>...<|end|>`).
- `ui.py` — Pipeline IA completo: prompt detallado con stripping de preámbulos como instrucción del LLM (no como regex post-procesamiento), schema con `minItems: 1, maxItems: 1` para forzar 1 entrada por chunk, max_tokens=1500/2500 para dx con scoring extenso (Banff, Gleason, médula ósea histology). Cleanup post-LLM mantenido SOLO para typos residuales y normalización de tildes.
- `core/diagnosticos_ia_db.py` — Nueva BD SQLite acumulativa (`data/diagnosticos_ia.db`) para persistir diagnósticos extraídos a lo largo de múltiples sesiones de procesamiento.

### Decisiones técnicas clave

#### 1. `json_object` → `json_schema`
gpt-oss-20b (LM Studio) rechaza `response_format: json_object` con HTTP 400 (`'response_format.type' must be 'json_schema' or 'text'`). El cliente caía a retry sin format, y sin la restricción el modelo emitía razonamiento mezclado con JSON, rompiendo el parser. Migrar a `json_schema` con strict=true forzó la estructura a nivel de generación de tokens.

#### 2. `minItems: 1, maxItems: 1`
Tras resolver el parsing, gpt-oss-20b empezó a devolver `{"diagnosticos":[]}` cuando no encontraba dx claro (~70% de chunks). Con `minItems: 1, maxItems: 1` el modelo está obligado a extraer exactamente 1 entrada por chunk. Tasa de extracción saltó de 30% a 100%.

#### 3. Cambio de modelo: gpt-oss-20b → qwen3.6-27b
Aún con json_schema + minItems, gpt-oss-20b mostraba problemas residuales:
- Truncamientos arbitrarios del dx (`...`)
- Mismatches dx ↔ órgano
- Alucinación de tokens (`…?…OCR…`)
- Typos del modelo (`PARIETO`, `MEDIANTE`, `MESA MEDIASTINAL`)
qwen3.6-27b cabe parcialmente en RTX 3050 OEM 8GB con offload a RAM (más lento ~10s/chunk vs ~3s) pero entrega calidad superior consistentemente.

#### 4. Preámbulos: prompt > código
En vez de mantener regex de stripping en post-procesamiento (`stripear_preambulos`), se trasladó la regla al prompt del LLM como instrucción explícita con ejemplos. Resultado: qwen respeta la regla y devuelve dx limpios sin necesidad de regex.

### Roadmap V6.7
- V6.7.0: Botón "Procesar con IA" inicial
- V6.7.3-7.5: Cleanup regex post-LLM (post-procesamiento agresivo — descartado en V6.7.15+)
- V6.7.8-7.13: Chunking IHQ-aware (1 IHQ por chunk)
- V6.7.14: Workaround typos gpt-oss
- V6.7.15: json_schema + parser harmony tokens
- V6.7.16: minItems/maxItems + tilde stripping
- V6.7.17: max_tokens 800 → 1200 (scoring Banff)
- V6.7.18: max_tokens 1200 → 1500 (médula ósea, Gleason)

### Casos testigo recuperados (vs gpt-oss-20b)
| IHQ | Antes | Ahora |
|---|---|---|
| IHQ250023 | `NEOPLASIA EN PATRON … …?…OCR…???..?` (basura) | `NEOPLASIA EN PATRON ACINAR CON CAMBIOS ONCOCITICOS DE PROBABLE ORIGEN RENAL` |
| IHQ250037 | `- HALLAZGOS` | `COLITIS AGUDA Y CRÓNICA NO ESPECÍFICA` |
| IHQ250043 | `GLIOSIS REACTIVA` / `ESTOMAGO` (mismatch) | `GLIOSIS REACTIVA` / `CEREBRO` |
| IHQ250045 | órgano `CUELLO` | órgano `GANGLIO LINFATICO` |
| IHQ250056 | órgano `CERVIX` (mismatch para LINFOMA FOLICULAR) | órgano `GANGLIO LINFATICO` |
| IHQ250076 | `LOS HALLAZGOS MORFOLOGICOS Y DE IHQ SUGIEREN UN ADENOCARCINOMA…` | `ADENOCARCINOMA DE ORIGEN EN EL TRACTO GENITAL FEMENINO` (preámbulo strippeado por modelo) |
| IHQ250095 | `HALLAZGOS DE INMUNOHISTIQUÍMICA COMPATIBLES CON LINFOMA…` | `LINFOMA DIFUSO DE CÉLULAS B GRANDES, FENOTIPO CENTROGERMINAL` |
| IHQ250096 | `LOS HALLAZGOS FAVORECEN UN LINFOMA LINFOBLÁSTICO T` | `LINFOMA LINFOBLÁSTICO DE CÉLULAS T` |

### Notas
- Hardware constraint: RTX 3050 OEM 8GB VRAM. qwen3.6-27b requiere offload parcial → ~10s por chunk. Aceptable para extracción batch nocturna.
- Pipeline NO modifica BD principal (`huv_oncologia_NUEVO.db`). Es paralelo: persiste en `data/diagnosticos_ia.db` como referencia para comparar cobertura del extractor tradicional (588 IHQs detectados) vs IA (995 IHQs esperados en el set total).

---

## [6.6.16] - 2026-05-04 — Diagnosis Categorization Sprint

**Sprint:** Refinamiento masivo del normalizador de diagnósticos (`core/normalizador_diagnosticos.py`) y un fix crítico de detección de malignidad en `core/extractors/medical_extractor.py`. El sprint cubre seis versiones consecutivas (V6.6.12 → V6.6.16) aplicadas como cambios quirúrgicos validados con auditoría cuantitativa sobre 188 casos del rango IHQ250001-200.

### Impact (cuantitativo)
| Métrica | Antes | Después | Mejora |
|---|---|---|---|
| Diagnósticos oncológicos categorizados | 62/100 (62.0%) | 161/188 (85.6%) | **+23.6 pts** |
| Casos problemáticos (OTRO + SIN DX) | 28/100 (28.0%) | 27/188 (14.4%) | **−13.6 pts** |
| Distribución MALIGNO/BENIGNO | 73/27 | 75/25 | sin desbalance |
| Regresiones detectadas | — | 0 | limpio |

### Files modified
- `core/normalizador_diagnosticos.py` — cambios mayores: typos del patólogo, 6 categorías nuevas/extendidas, stripping de preámbulos, reordenamientos de prioridad, ampliación de inferencia por órgano.
- `core/extractors/medical_extractor.py` (función `determine_malignancy`, líneas ~3641-3686) — nueva PRIORIDAD -2 que aísla negaciones explícitas en `Diagnostico Principal` para evitar contaminación por historia clínica.

### Changes by version

#### V6.6.12 — Typo del patólogo "CARICNOMA"
- `normalizar_texto()`: corregido typo "CARICNOMA" → "CARCINOMA" en preprocesamiento.
- **Caso piloto:** IHQ250060.
- **Impacto:** 1 caso recuperado (OTRO/NO CATEGORIZADO → CARCINOMA → refinado por órgano a OTRO CARCINOMA DE MAMA).

#### V6.6.13 — Categorías faltantes en el diccionario
- Agregadas 4 categorías nuevas: **TUMOR FILODES DE MAMA**, **CARCINOMA PAPILAR DE MAMA**, **NEOPLASIA DE CELULAS FUSIFORMES / FUSOCELULAR**, **LESION ESCAMOSA INTRAEPITELIAL / NIC**.
- Extendida **LINFOMA NO HODGKIN B** con patrones OMS 2022 ("NEOPLASIA DE CELULAS B MADURAS").
- **Casos piloto:** IHQ250071, IHQ250081, IHQ250066, IHQ250126, IHQ250107, IHQ250116.
- **Impacto:** 6 casos recuperados.

#### V6.6.14 — Stripping de preámbulos del patólogo + reordenamiento
- Nueva función `stripear_preambulos()` con 11 preámbulos típicos del patólogo del HUV (ej. "RESULTADO IHQ COMPATIBLE CON…").
- `categorizar_diagnostico()` modificada para invocar el stripping antes del matching.
- **Reordenamientos críticos** (resolver cortocircuitos contra patrones genéricos):
  - `ADENOCARCINOMA (SIN ORIGEN)` y `CARCINOMA (OTRO)` ANTES de `RESULTADO IHQ`.
  - `LEUCEMIA MIELOIDE` y `LEUCEMIA LINFOIDE AGUDA` ANTES de `LINFOMA (OTRO/INESPECIFICO)`.
- Nueva categoría: **CARCINOMA ANEXIAL CUTANEO**.
- **LINFOMA NO HODGKIN B** extendido con "ZONA MARGINAL".
- **LEUCEMIA LINFOIDE AGUDA** extendida con "LEUCEMIA/LINFOMA LINFOBLASTICO".
- **Casos piloto:** IHQ250026, IHQ250028, IHQ250041, IHQ250087, IHQ250091, IHQ250099, IHQ250105, IHQ250140, IHQ250147, IHQ250158, IHQ250164, IHQ250166, IHQ250174.
- **Impacto:** 15 casos recuperados (13 por preámbulos + 2 por sufijo SOBREEXPRESIÓN).

#### V6.6.14 (cont.) — Mini-fix RECTAL en INFERENCIA_POR_ORGANO_ADENO
- El patrón "RECTO" no matcheaba "RECTAL" como substring.
- **Caso piloto:** IHQ250159.
- **Impacto:** 1 caso recuperado.

#### V6.6.15 — Fix CRÍTICO Malignidad (PRIORIDAD -2 en `determine_malignancy`)
- **Problema:** la PRIORIDAD -1 evaluaba `combined_text = diagnostico + macroscopica + microscopica + full_text`. La historia clínica con "Historia de carcinoma de mama" disparaba MALIGNO aunque el dx final fuera benigno (ej. INFLAMACIÓN AGUDA SIN EVIDENCIA DE LESIÓN NEOPLÁSICA).
- **Solución:** nueva PRIORIDAD -2 que evalúa SOLO el `Diagnostico Principal` para negaciones explícitas. Si tiene negación y NO tiene también keyword maligno (caso multi-muestra), retorna BENIGNO.
- **Casos piloto:** IHQ250106 (target — crítico clínicamente), IHQ250065 (bonus).
- **Impacto:** 2 casos recuperados.

#### V6.6.16 — Mini-fixes basados en audit cuantitativo
- Typo "HISTOLOGIOS" → "HISTOLOGICOS" en `normalizar_texto` (caso IHQ250026 MELANOMA).
- Nueva categoría **INFLAMACION / PROCESO INFECCIOSO** (cubre IHQ250037 colitis, IHQ250075 peritonitis, IHQ250061 Hirschsprung).
- `INFERENCIA_POR_ORGANO_ESCAMO` ampliado con: LABIO, BOCA, FARINGE, HIPOFARINGE, NASOFARINGE, ESOFAGO, ANO, VULVA, VAGINA.
- **Impacto:** 4+ casos recuperados.

### Validation
- 75+ casos validados manualmente con resultados esperados (todos OK).
- 54 self-tests internos del normalizador (54/54 OK).
- 12 casos de regresión específicos para `determine_malignancy` (12/12 OK).
- Audit cuantitativo sobre 188 casos del período IHQ250001-200 (**0 regresiones**).

### Anti-regression notes (REGLA CRÍTICA #1)
Todos los cambios siguen el patrón "patrón específico nuevo ANTES + fallback genérico ORIGINAL preservado". Ningún patrón existente fue eliminado o sobrescrito; todas las extensiones se agregaron como ramas adicionales o reordenamientos de prioridad. Comentarios `V6.6.XX FIX IHQYYYYY` en el código documentan la trazabilidad caso-por-caso.

---

## [6.0.0] - 2025-10-20

### Changed
- Consolidación 19→6 archivos core
- 7 workflows maestros implementados
- version-manager gestiona CHANGELOG+BITÁCORA acumulativos
- documentation-specialist simplificado (solo lee CHANGELOG)
- 4 herramientas densas (4665 líneas)
- 5 agentes especializados (2066 líneas)

---

Changelog

Este proyecto sigue versionamiento semantico.

[Unreleased]
- **CONSOLIDACIÓN COMPLETA SYSTEMPROMPT**: Finalización protocolo análisis SYSTEMPROMPT con reporte navegación ChatGPT.
- **REPORTE_CHATGPT.md completo**: Mapa navegable proyecto con rutas absolutas Drive, componentes principales, flujos pipeline y comandos navegación.
- **28 Plantillas NotebookLM**: Contenido especializado para 4 audiencias (Médico oncológico, Desarrollo, Dirección, Investigadores) en formatos audio, video y cuestionarios.
- **Navegación IA Externa**: Estructura optimizada para ChatGPT con referencias exactas archivo:línea y flujos consulta típicos por dominio técnico/médico.
- Integracion completa de Biopsia/Autopsia al flujo persistente y dashboards.
- Sincronizacion incremental con Power BI y agendas clinicas.
- Hardening de pruebas automaticas de extraccion y visualizacion.

2025-09-22 — docs - SYSTEMPROMPT Analysis
- **DOCUMENTACIÓN TÉCNICA MODULAR COMPLETA**: Análisis exhaustivo de 10 componentes críticos del sistema siguiendo protocolo SYSTEMPROMPT con 12 secciones por componente.
- **Análisis técnico evidence-based**: Documentación con referencias exactas archivo:línea para cada componente del pipeline OCR.
- **Arquitectura médica especializada**: Documentación profunda del dominio oncológico HUV con vocabulario biomarcadores, patrones extracción y flujos clínicos.
- **Componentes analizados**: 
  - `01_huv_ocr_sistema_definitivo.md` - Entry point y configuración Tesseract
  - `02_ui.md` - Interfaz CustomTkinter 1299 líneas con 4 tabs especializados
  - `03_ocr_processing.md` - Engine OCR híbrido PyMuPDF/Tesseract con limpieza médica
  - `04_procesador_ihq_biomarcadores.md` - Extractor biomarcadores HER2/Ki-67/RE/RP/PD-L1 
  - `05_database_manager.md` - Gestor SQLite con esquema 167 campos transaccional
  - `06_huv_web_automation.md` - Automatización portal Selenium con error recovery
  - `07_calendario.md` - Scheduler interno tareas automatizadas con threading
  - `08_huv_constants.md` - Vocabulario médico centralizado y patrones regex
  - `09_config.ini.md` - Configuración multiplataforma con detección OS
  - `10_test_sistema.py.md` - Suite pruebas automatizadas con fixtures médicas
- **Gestión técnica**: Identificación riesgos médicos críticos, deuda técnica, puntos extensión y estrategias optimización por componente.
- **Cobertura completa**: Desde entry point hasta testing, incluyendo seguridad datos médicos, performance OCR y mantenibilidad arquitectura.
- **Documentación ONCONOVA**: Actualización README.md, INFORME_GLOBAL_PROYECTO.md, INICIO_RAPIDO.md con nueva arquitectura v2.5.

2025-09-20 — docs
- Generado/actualizado `documentacion/REPORTE_CHATGPT.md` con el mapa del proyecto.
- Enlace agregado en `documentacion/README.md`.
 - Documentado `scripts/inspect_excel.py` en `documentacion/analisis/21_inspect_excel.md`.
 - Limpieza de binarios: movidos a `utilidades/binarios/` y `.gitignore` ampliado (EXCEL/, pdfs_patologia/, huv_oncologia.db, *.exe).
 - Ejecutable probado con PyInstaller (`dist/OCR_Medico.exe`).

2025-09-15 – v2.5.0
- Rediseno de la aplicacion de escritorio con CustomTkinter: navegacion por Procesar PDFs, Visualizar Datos, Dashboard Analitico y Automatizar BD Web.
- Canalizacion persistente: `procesador_ihq_biomarcadores` segmenta multiples informes por PDF, normaliza biomarcadores y guarda resultados en `huv_oncologia.db` mediante `database_manager`.
- Dashboard analitico integrado (Matplotlib/Seaborn) con filtros dinamicos, comparador parametrizado y modo pantalla completa.
- Automatizacion del portal `huvpatologia.qhorte.com` con Selenium (`huv_web_automation.py`) para consultas guiadas desde la aplicacion.
- Widget `CalendarioInteligente` (Babel + holidays) para seleccionar rangos de fecha con contexto de festivos.
- Documentacion actualizada para arquitectura 2.5 e incorporacion de analisis de `database_manager`, `huv_web_automation` y `calendario.py`.

2025-09-10 – v1.1.0
- Version estable v1.1 liberada.
- Nuevo analisis avanzado de IHQ accesible desde la UI (boton "Analizar Biomarcadores IHQ (v1.1)") que genera un Excel separado con HER2, Ki-67, RE/ER, RP/PR, PD-L1, P16 (estado/porcentaje) y "Estudios Solicitados".
- Documentacion actualizada: `INFORME_GLOBAL_PROYECTO.md`, `README.md`, `INICIO_RAPIDO.md` y bitacora.

2025-09-10
- Rebranding y reestructuracion documental al ecosistema "ONCONOVA Gestor H.U.V".
- Creacion de `BITACORA_DE_ACERCAMIENTOS.md` y carpeta `comunicados/` (cinco artefactos).
- Ajustes de analisis: documentacion de extensiones IHQ y activos de datos.

2025-09-05 – v1.0.0
- Fundacion y validacion: motor OCR + app de escritorio.
- Procesadores especializados: Autopsia, IHQ, Biopsia, Revision.
- Exportacion validada a Excel (55 columnas) con formato profesional.

2025-08-20 – v0.1.0
- Inicio del desarrollo: estructura base, OCR y primeras reglas de extraccion.
