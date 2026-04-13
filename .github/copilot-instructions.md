# 🤖 GitHub Copilot - Instrucciones del Proyecto EVARISIS Gestor Oncológico HUV

**Sistema**: Gestor de Oncología - Hospital Universitario del Valle
**Versión**: 4.2.1
**Fecha**: 4 de octubre de 2025

---

## 📋 CONTEXTO DEL PROYECTO

Este proyecto es un sistema de gestión oncológica que procesa PDFs de patología mediante OCR (Tesseract), extrae información médica estructurada (datos de pacientes, diagnósticos, biomarcadores) y la almacena en una base de datos SQLite con capacidad de exportación a Excel.

**Tecnologías principales**: Python 3.8+, TTKBootstrap (UI), SQLite3, Tesseract OCR, pdf2image, pandas, openpyxl

---

## 🚫 PROHIBICIONES ESTRICTAS - CUMPLIMIENTO OBLIGATORIO

### ❌ NUNCA crear scripts en el directorio raíz

**PROHIBIDO**:

- ❌ Crear archivos `.py` en el directorio raíz (excepto `ui.py` que ya existe)
- ❌ Crear archivos de test, verificación, análisis o debug en el raíz
- ❌ Crear archivos `.md` de reportes en el raíz (usar `herramientas_ia/resultados/`)
- ❌ Crear scripts de "prueba rápida" o "test simple"

**RAZÓN**: Ya existen herramientas CLI completas en `herramientas_ia/` que cubren TODOS los casos de uso.

### ❌ NUNCA crear herramientas redundantes

**HERRAMIENTAS YA DISPONIBLES**:

- `herramientas_ia/consulta_base_datos.py` - Consultas y gestión de BD
- `herramientas_ia/analizar_pdf_completo.py` - Análisis profundo de PDFs
- `herramientas_ia/validar_extraccion.py` - Validación de extracción vs BD
- `herramientas_ia/verificar_excel.py` - Verificación de exportaciones Excel
- `herramientas_ia/cli_herramientas.py` - CLI unificado (punto de entrada principal)
- `herramientas_ia/test_herramientas.py` - Suite de pruebas completa

### ❌ NUNCA modificar datos en la BD directamente

**ENFOQUE CORRECTO**:

1. Analizar PDF con herramientas existentes
2. Detectar problemas en patrones de extracción
3. Corregir extractores en `core/extractors/`
4. Eliminar BD: `rm data/huv_oncologia_NUEVO.db`
5. Reprocesar todos los PDFs
6. Validar con herramientas

**NO** crear scripts para "arreglar" o "llenar" datos faltantes.

### ❌ NUNCA usar documentación obsoleta

**IGNORAR COMPLETAMENTE**:

- Carpeta `documentacion/` → DESACTUALIZADA, NO USAR

**USAR ÚNICAMENTE**:

- `herramientas_ia/README.md` ✅
- `herramientas_ia/GUIA_COMPORTAMIENTO_IA.md` ✅
- `herramientas_ia/GUIA_TECNICA_COMPLETA.md` ✅
- `herramientas_ia/REGLAS_ESTRICTAS_IA.md` ✅
- `VERSION_MAC/README_INSTALACION_MACOS.md` ✅

---

## ✅ USO CORRECTO DE HERRAMIENTAS CLI

### 🎯 CLI Unificado (Punto de Entrada Principal)

**Siempre usar**: `python cli_herramientas.py [comando] [opciones]`

### 📋 Comandos Esenciales por Categoría

#### 🔍 Base de Datos (bd)

```bash
# Estadísticas generales
python cli_herramientas.py bd --stats
python cli_herramientas.py bd -s

# Buscar caso IHQ específico
python cli_herramientas.py bd --buscar IHQ250001
python cli_herramientas.py bd -b IHQ250001

# Buscar por paciente
python cli_herramientas.py bd --paciente "Maria Garcia"
python cli_herramientas.py bd -p "Juan"

# Filtrar por órgano
python cli_herramientas.py bd --organo PULMON
python cli_herramientas.py bd -o MAMA

# Ver biomarcadores
python cli_herramientas.py bd --biomarcadores IHQ250001

# Exportar a JSON
python cli_herramientas.py bd -b IHQ250001 --json resultado.json
```

#### 📄 Análisis PDF (pdf)

```bash
# Análisis rápido de caso específico (RECOMENDADO)
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Solo biomarcadores
python cli_herramientas.py pdf -f documento.pdf --biomarcadores

# Solo datos de paciente
python cli_herramientas.py pdf -f documento.pdf --paciente

# Comparar extracción con BD
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001 --comparar

# Buscar patrón específico (regex)
python cli_herramientas.py pdf -f documento.pdf --patron "Ki-67"
```

#### ✅ Validación (validar)

```bash
# Validar caso IHQ con PDF
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

# Solo mostrar diferencias
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --solo-diferencias

# Generar reporte detallado
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte
```

#### 📊 Excel (excel)

```bash
# Listar archivos exportados
python cli_herramientas.py excel --listar
python cli_herramientas.py excel -l

# Estadísticas del último
python cli_herramientas.py excel --stats
python cli_herramientas.py excel -s

# Verificar calidad de datos
python cli_herramientas.py excel --calidad archivo.xlsx
```

#### 🧪 Testing (test)

```bash
# Ejecutar todos los tests
python cli_herramientas.py test

# Tests específicos
python cli_herramientas.py test --imports
python cli_herramientas.py test --bd
python cli_herramientas.py test --ocr
```

#### 🐛 Debug e Info

```bash
# Información del sistema
python cli_herramientas.py info

# Utilidades de debug
python cli_herramientas.py debug
```

---

## 📁 ESTRUCTURA DEL PROYECTO

```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py                    # ⭐ ARCHIVO PRINCIPAL (interfaz gráfica)
├── iniciar_python.bat       # 🚀 Iniciador Windows
├── requirements.txt         # 📦 Dependencias
├── core/                    # 🧠 LÓGICA PRINCIPAL
│   ├── database_manager.py        # Gestión BD SQLite
│   ├── unified_extractor.py       # Coordinador de extracción
│   ├── enhanced_export_system.py  # Exportación a Excel
│   └── extractors/                # Extractores modulares
│       ├── patient_extractor.py      # Datos de pacientes
│       ├── medical_extractor.py      # Datos médicos
│       └── biomarker_extractor.py    # Biomarcadores IHQ
├── config/                  # ⚙️ Configuración
├── data/                    # 💾 Base de datos
│   └── huv_oncologia_NUEVO.db    # BD SQLite principal
├── herramientas_ia/         # 🤖 HERRAMIENTAS CLI (tu área de trabajo)
│   ├── cli_herramientas.py         # CLI unificado
│   ├── consulta_base_datos.py      # Consultas BD
│   ├── analizar_pdf_completo.py    # Análisis PDF
│   ├── validar_extraccion.py       # Validación
│   ├── verificar_excel.py          # Verificación Excel
│   ├── test_herramientas.py        # Testing
│   ├── README.md                   # Documentación CLI
│   ├── GUIA_COMPORTAMIENTO_IA.md   # Guía para IAs
│   ├── GUIA_TECNICA_COMPLETA.md    # Docs técnicas
│   ├── REGLAS_ESTRICTAS_IA.md      # Reglas obligatorias
│   └── resultados/                 # Reportes de mejoras
├── pdfs_patologia/          # 📄 PDFs a procesar
├── VERSION_MAC/             # 🍎 Scripts para macOS
└── LEGACY/                  # 📦 Archivos obsoletos
```

---

## 🔧 MÓDULOS CORE PRINCIPALES

### 📊 database_manager.py

- Gestión completa de BD SQLite
- Tabla principal: `informes_ihq`
- Funciones: `init_db()`, `save_record_to_db()`, `get_all_records_as_dataframe()`

### 🔍 unified_extractor.py

- Coordinador principal de extracción
- Flujo: PDF → Imágenes → OCR → Extracción → BD
- Usa: `pdf2image`, `pytesseract`

### 👤 patient_extractor.py (core/extractors/)

- Extrae: Número de petición (IHQ250XXX), nombre, edad, género, servicio
- Usa patrones regex configurables en `PATIENT_PATTERNS`

### 🧬 medical_extractor.py (core/extractors/)

- Extrae: Diagnósticos, malignidad, procedimientos
- Usa keywords en `MALIGNIDAD_KEYWORDS_IHQ`

### 🔬 biomarker_extractor.py (core/extractors/)

- Extrae: HER2, Ki-67, RE, RP, PDL-1, P53, BRCA1/2
- Patrones específicos para cada biomarcador

### 📤 enhanced_export_system.py

- Exportación avanzada a Excel
- Directorio: `Documents/EVARISIS Gestor Oncologico/Exportaciones Base de datos/`

---

## 🎯 FLUJO DE TRABAJO CORRECTO

### Cuando necesites información:

1. **PRIMERO**: Verifica si existe un comando CLI
2. **SEGUNDO**: Usa el comando existente con `cli_herramientas.py`
3. **TERCERO**: Si NO existe, pregunta al usuario antes de crear algo nuevo
4. **ÚLTIMO RECURSO**: Si es necesario, extiende herramienta existente en `herramientas_ia/`

### Ejemplo Correcto vs Incorrecto:

❌ **INCORRECTO**:

```python
# Crear: test_caso_ihq.py en el raíz
# Consultar caso IHQ250001
...
```

✅ **CORRECTO**:

```bash
python cli_herramientas.py bd -b IHQ250001
```

### Para extender funcionalidad:

❌ **INCORRECTO**:

```python
# Crear: exportar_biomarcadores.py en el raíz
```

✅ **CORRECTO**:

```python
# Editar: herramientas_ia/consulta_base_datos.py
# Agregar argumento: --exportar-biomarcadores-csv
# Usar: python cli_herramientas.py bd --exportar-biomarcadores-csv salida.csv
```

---

## 🔄 FLUJO DE CORRECCIÓN DE PROBLEMAS

### Cuando hay datos faltantes o incorrectos:

**NUNCA** crear scripts para modificar la BD directamente.

**PROCESO CORRECTO**:

1. **Analizar**: Usar `analizar_pdf_completo.py` para ver el PDF completo

   ```bash
   python cli_herramientas.py pdf -f caso.pdf -i 250001
   ```

2. **Comparar**: Verificar qué se extrajo vs qué debería extraerse

   ```bash
   python cli_herramientas.py bd -b IHQ250001
   python cli_herramientas.py validar --ihq 250001 --pdf caso.pdf
   ```

3. **Identificar patrones faltantes**: Detectar qué regex no están capturando

4. **Modificar extractores**: Editar `core/extractors/` con nuevos patrones
   - `patient_extractor.py` → Para datos de pacientes
   - `medical_extractor.py` → Para datos médicos
   - `biomarker_extractor.py` → Para biomarcadores

5. **Eliminar BD**: `rm data/huv_oncologia_NUEVO.db`

6. **Reprocesar**: Ejecutar el programa completo y procesar todos los PDFs

7. **Validar**: Usar herramientas para verificar mejoras
   ```bash
   python cli_herramientas.py bd --stats
   python cli_herramientas.py validar --ihq 250001 --pdf caso.pdf
   ```

---

## 💡 MEJORES PRÁCTICAS PARA CÓDIGO

### Al modificar extractores (core/extractors/):

1. **Agregar patrones regex** en lugar de crear lógica compleja
2. **Probar con casos conocidos** usando herramientas CLI
3. **Documentar** los patrones nuevos con comentarios
4. **No eliminar** patrones existentes sin confirmar que están obsoletos

### Al usar herramientas CLI:

1. **Preferir comandos cortos**: `-b`, `-f`, `-i`, `-s`, `-l`, `-p`, `-o`, `-d`
2. **Exportar a JSON** para procesamiento automatizado: `--json salida.json`
3. **Usar --help** para ver opciones completas: `python cli_herramientas.py bd -h`
4. **Validar siempre** después de cambios: `python cli_herramientas.py bd --verificar`

### Al crear reportes:

1. **Guardar en** `herramientas_ia/resultados/`
2. **Formato**: `YYYY-MM-DD_descripcion_mejora.md`
3. **NO generar** reportes hasta confirmar que funcionan
4. **Incluir**: Fecha, cambios aplicados, resultados de validación

---

## 🚀 INICIO DEL PROGRAMA

### ⚠️ La UI NUNCA se inicia directamente

**INCORRECTO**: `python ui.py`

**CORRECTO**: Usar `iniciar_python.bat` (Windows) o script en `VERSION_MAC/` (macOS)

### Argumentos obligatorios EVARISIS:

```bash
--lanzado-por-evarisis
--nombre "Innovación y Desarrollo"
--cargo "Ingenieros de soluciones"
--foto "ruta/a/foto.jpeg"
--tema "cosmo"
--ruta-fotos "ruta/a/carpeta"
```

---

## 📊 BASE DE DATOS

**Ubicación**: `data/huv_oncologia_NUEVO.db`
**Tipo**: SQLite3
**Tabla principal**: `informes_ihq`

**Campos principales**:

- `numero_peticion` (IHQ250XXX)
- `nombre_paciente`, `edad`, `genero`, `servicio`
- `fecha_informe`, `diagnostico`, `malignidad`
- `ihq_her2`, `ihq_ki67`, `ihq_receptor_estrogeno`, `ihq_receptor_progesteronos`, `ihq_pdl1`
- `fecha_procesamiento`, `archivo_origen`

**Para consultas**: Siempre usar `cli_herramientas.py bd` o `consulta_base_datos.py`

---

## 🔍 CASOS DE USO FRECUENTES

### 1. Verificar un caso IHQ completo

```bash
# Ver datos en BD
python cli_herramientas.py bd -b IHQ250001

# Analizar extracción del PDF
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Validar extracción vs BD
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte
```

### 2. Verificar exportación Excel

```bash
# Listar archivos
python cli_herramientas.py excel -l

# Estadísticas del último
python cli_herramientas.py excel -s

# Verificar calidad
python cli_herramientas.py excel --calidad archivo.xlsx
```

### 3. Debugging de problemas de extracción

```bash
# Ver texto OCR del PDF
python cli_herramientas.py pdf -f problema.pdf --ocr

# Análisis completo
python cli_herramientas.py pdf -f problema.pdf --completo

# Comparar con BD
python cli_herramientas.py pdf -f problema.pdf -i 250001 --comparar
```

### 4. Búsquedas en la BD

```bash
# Por paciente
python cli_herramientas.py bd -p "Maria Garcia"

# Por órgano
python cli_herramientas.py bd -o MAMA --json casos_mama.json

# Por diagnóstico (regex)
python cli_herramientas.py bd -d "CARCINOMA.*DUCTAL"
```

---

## 🚨 CHECKLIST ANTES DE CUALQUIER ACCIÓN

### ✅ Antes de crear algo nuevo:

- [ ] ¿Ya existe esta funcionalidad en herramientas existentes?
- [ ] ¿Puedo extender una herramienta existente en lugar de crear nueva?
- [ ] ¿Es para diagnóstico/análisis o para "corregir" datos?
- [ ] ¿Estoy trabajando solo en `herramientas_ia/`?
- [ ] ¿He revisado `herramientas_ia/README.md`?

### ✅ Antes de modificar extractores:

- [ ] ¿Analicé el PDF completo con la herramienta?
- [ ] ¿Comparé con los datos en BD?
- [ ] ¿Identifiqué exactamente qué patrones faltan?
- [ ] ¿Tengo plan para eliminar BD y reprocesar?

### ✅ Antes de generar reportes:

- [ ] ¿Confirmé que los cambios funcionan?
- [ ] ¿El usuario validó que la solución es correcta?
- [ ] ¿Estoy guardando en `herramientas_ia/resultados/`?

---

## ⚡ COMANDOS MÁS USADOS (MEMORIZA)

```bash
# Info del sistema
python cli_herramientas.py info

# Ver caso IHQ
python cli_herramientas.py bd -b IHQ250001

# Analizar PDF
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Validar extracción
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

# Stats BD
python cli_herramientas.py bd -s

# Último Excel
python cli_herramientas.py excel -l

# Verificar integridad
python cli_herramientas.py bd --verificar

# Testing completo
python cli_herramientas.py test
```

---

## 📝 DOCUMENTACIÓN DE REFERENCIA

**USAR SIEMPRE**:

- `herramientas_ia/README.md` - Comandos y referencia completa
- `herramientas_ia/GUIA_COMPORTAMIENTO_IA.md` - Metodología de trabajo
- `herramientas_ia/GUIA_TECNICA_COMPLETA.md` - Documentación técnica
- `herramientas_ia/REGLAS_ESTRICTAS_IA.md` - Reglas obligatorias

**IGNORAR**:

- `documentacion/` - Completamente desactualizada

---

## 🔒 CUMPLIMIENTO OBLIGATORIO

**ESTAS INSTRUCCIONES SON OBLIGATORIAS Y NO NEGOCIABLES.**

Si un código sugestionado las viola:

1. El código será rechazado
2. Los archivos creados incorrectamente serán movidos a `LEGACY/`
3. Se deberá usar la herramienta correcta existente

---

**Versión**: 4.2.1  
**Última actualización**: 4 de octubre de 2025  
**Estado**: ACTIVO Y OBLIGATORIO  
**Sistema**: EVARISIS Gestor Oncológico - Hospital Universitario del Valle
