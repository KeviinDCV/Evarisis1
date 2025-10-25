# 🤖 Herramientas de IA - Gestor de Oncología HUV

**Versión 4.2.1** - Optimizado para uso de IA por línea de comandos

Esta carpeta contiene herramientas CLI completas para verificar, analizar y operar el sistema de gestión oncológica del HUV. **Todas las herramientas están diseñadas para uso exclusivo por línea de comandos**, ideales para automatización e integración con IA.

> 🎯 **NUEVO**: GitHub Copilot está configurado automáticamente para este proyecto. Consulta la [documentación de configuración](resultados/2025-10-04_configuracion_copilot.md) para más detalles.

---

## 📁 Estructura de Herramientas

### 🎯 CLI Unificado (PUNTO DE ENTRADA PRINCIPAL)
- **Archivo**: `cli_herramientas.py`
- **Descripción**: Interfaz unificada que integra TODAS las herramientas
- **Uso**: `python cli_herramientas.py [comando] [opciones]`

### 🔍 Herramientas Especializadas

1. **consulta_base_datos.py** - Consultas y gestión de BD SQLite
2. **analizar_pdf_completo.py** - Análisis profundo de PDFs
3. **validar_extraccion.py** - Validar extracción vs BD
4. **verificar_excel.py** - Verificación de exportaciones Excel
5. **test_herramientas.py** - Testing del sistema
6. **utilidades_debug.py** - Debug avanzado
7. **utilidades_comunes.py** - Funciones compartidas

---

## 🚀 Guía de Uso Rápido

### ⚡ Comandos Más Usados

```bash
# Ver información del sistema
python cli_herramientas.py info

# Ver caso IHQ específico
python cli_herramientas.py bd -b IHQ250001

# Analizar caso en PDF
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Estadísticas de BD
python cli_herramientas.py bd -s

# Último Excel exportado
python cli_herramientas.py excel -l
```

---

## 📋 Comandos Completos por Categoría

### 🔍 BASE DE DATOS (bd)

#### Consultas Básicas
```bash
# Estadísticas generales
python cli_herramientas.py bd --stats

# Buscar caso IHQ
python cli_herramientas.py bd --buscar IHQ250001
python cli_herramientas.py bd -b IHQ250001  # Forma corta

# Listar todos los registros
python cli_herramientas.py bd --listar
python cli_herramientas.py bd -l --limite 100
```

#### Búsquedas Avanzadas
```bash
# Buscar por paciente
python cli_herramientas.py bd --paciente "Juan Perez"
python cli_herramientas.py bd -p "Maria"

# Filtrar por órgano
python cli_herramientas.py bd --organo PULMON
python cli_herramientas.py bd -o MAMA

# Filtrar por diagnóstico (regex)
python cli_herramientas.py bd --diagnostico "ADENOCARCINOMA"
python cli_herramientas.py bd -d "CARCINOMA.*PULMON"
```

#### Análisis de Biomarcadores
```bash
# Ver biomarcadores de un caso
python cli_herramientas.py bd --biomarcadores IHQ250001

# Contar registros por categoría
python cli_herramientas.py bd --contar
```

#### Exportar y Verificar
```bash
# Exportar resultado a JSON
python cli_herramientas.py bd --buscar IHQ250001 --json resultado.json

# Verificar integridad de BD
python cli_herramientas.py bd --verificar
```

---

### 📄 ANÁLISIS PDF (pdf)

#### Análisis Rápido (RECOMENDADO)
```bash
# Analizar caso IHQ específico (más rápido)
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001
python cli_herramientas.py pdf --archivo documento.pdf --ihq 250002
```

#### Extracción por Componentes
```bash
# Solo OCR del PDF
python cli_herramientas.py pdf -f documento.pdf --ocr

# Segmentar todos los casos IHQ
python cli_herramientas.py pdf -f ordenamientos.pdf --segmentar

# Solo datos de paciente
python cli_herramientas.py pdf -f documento.pdf --paciente

# Solo datos médicos
python cli_herramientas.py pdf -f documento.pdf --medico

# Solo biomarcadores
python cli_herramientas.py pdf -f documento.pdf --biomarcadores

# Análisis completo
python cli_herramientas.py pdf -f documento.pdf --completo
```

#### Búsqueda y Comparación
```bash
# Buscar patrón específico
python cli_herramientas.py pdf -f documento.pdf --patron "Ki-67"
python cli_herramientas.py pdf -f documento.pdf --patron "p53.*expresi[oó]n"

# Comparar extracción con BD
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001 --comparar
```

#### Opciones Avanzadas
```bash
# Exportar a JSON
python cli_herramientas.py pdf -f documento.pdf -i 250001 --json salida.json

# Limitar páginas a procesar
python cli_herramientas.py pdf -f documento.pdf --limite-paginas 10
```

---

### 📊 EXCEL (excel)

#### Listado y Estadísticas
```bash
# Listar todos los Excel exportados
python cli_herramientas.py excel --listar
python cli_herramientas.py excel -l

# Estadísticas del último Excel
python cli_herramientas.py excel --stats
python cli_herramientas.py excel -s
```

#### Verificación de Calidad
```bash
# Reporte de calidad de datos
python cli_herramientas.py excel --calidad archivo.xlsx

# Verificar columnas esperadas
python cli_herramientas.py excel --verificar-columnas archivo.xlsx
```

#### Comparación
```bash
# Comparar dos exportaciones
python cli_herramientas.py excel --comparar archivo1.xlsx archivo2.xlsx
```

#### Abrir Archivos
```bash
# Abrir Excel específico
python cli_herramientas.py excel --abrir archivo.xlsx

# Abrir último Excel generado
python cli_herramientas.py excel --ultimo
```

---

### ✅ VALIDACIÓN (validar)

#### Validar Extracción vs BD
```bash
# Validar caso IHQ con PDF
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

# Validar todos los campos
python cli_herramientas.py validar --ihq 250001 --completo

# Solo mostrar diferencias
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --solo-diferencias

# Generar reporte detallado
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte
```

#### Validar Campos Específicos
```bash
# Validar campos específicos
python cli_herramientas.py validar --ihq 250001 --campos "Edad" "Genero" "Órgano"
```

---

### 🧪 TESTING (test)

```bash
# Ejecutar todos los tests
python cli_herramientas.py test

# Test de imports y dependencias
python cli_herramientas.py test --imports

# Test de conexión a BD
python cli_herramientas.py test --bd

# Test de OCR
python cli_herramientas.py test --ocr

# Test de extractores
python cli_herramientas.py test --extractores

# Ejecutar batería completa
python cli_herramientas.py test --todo
```

---

### 🐛 DEBUG E INFO

```bash
# Utilidades de debug
python cli_herramientas.py debug

# Información del sistema
python cli_herramientas.py info
```

---

## 📚 Uso Directo de Herramientas

### consulta_base_datos.py

```bash
# Estadísticas
python consulta_base_datos.py --estadisticas

# Buscar petición
python consulta_base_datos.py --buscar-peticion IHQ250001

# Listar con límite
python consulta_base_datos.py --listar --limite 50

# Filtros avanzados
python consulta_base_datos.py --paciente "Juan"
python consulta_base_datos.py --organo PULMON
python consulta_base_datos.py --diagnostico "ADENOCARCINOMA"

# Biomarcadores
python consulta_base_datos.py --biomarcadores IHQ250001

# Exportar a JSON
python consulta_base_datos.py --buscar-peticion IHQ250001 --json salida.json

# Verificar integridad
python consulta_base_datos.py --verificar-integridad
```

### analizar_pdf_completo.py

```bash
# Análisis rápido de caso IHQ
python analizar_pdf_completo.py --archivo ordenamientos.pdf --ihq 250001

# Solo OCR
python analizar_pdf_completo.py --archivo documento.pdf --solo-ocr

# Segmentar casos
python analizar_pdf_completo.py --archivo ordenamientos.pdf --segmentar

# Análisis completo
python analizar_pdf_completo.py --archivo documento.pdf --completo

# Por componentes
python analizar_pdf_completo.py --archivo documento.pdf --paciente
python analizar_pdf_completo.py --archivo documento.pdf --medico
python analizar_pdf_completo.py --archivo documento.pdf --biomarcadores

# Buscar patrón
python analizar_pdf_completo.py --archivo documento.pdf --patron "Ki-67"

# Comparar con BD
python analizar_pdf_completo.py --archivo ordenamientos.pdf --ihq 250001 --comparar-bd

# Exportar a JSON
python analizar_pdf_completo.py --archivo documento.pdf --ihq 250001 --json salida.json
```

### validar_extraccion.py

```bash
# Validar caso con PDF
python validar_extraccion.py --ihq 250001 --pdf ordenamientos.pdf

# Validación completa
python validar_extraccion.py --ihq 250001 --completo

# Solo diferencias
python validar_extraccion.py --ihq 250001 --pdf ordenamientos.pdf --solo-diferencias

# Generar reporte JSON
python validar_extraccion.py --ihq 250001 --pdf ordenamientos.pdf --reporte

# Validar campos específicos
python validar_extraccion.py --ihq 250001 --campos "Edad" "Genero" "Diagnóstico"
```

### verificar_excel.py

```bash
# Listar archivos
python verificar_excel.py --listar

# Estadísticas del último
python verificar_excel.py --estadisticas-ultimo

# Calidad de datos
python verificar_excel.py --calidad archivo.xlsx

# Verificar columnas
python verificar_excel.py --verificar-columnas archivo.xlsx

# Comparar archivos
python verificar_excel.py --comparar archivo1.xlsx archivo2.xlsx

# Abrir archivo
python verificar_excel.py --abrir archivo.xlsx
python verificar_excel.py --abrir-ultimo
```

### test_herramientas.py

```bash
# Todos los tests
python test_herramientas.py

# Tests específicos
python test_herramientas.py --test-imports
python test_herramientas.py --test-bd
python test_herramientas.py --test-ocr
python test_herramientas.py --test-extractores
python test_herramientas.py --todo
```

---

## 🎯 Casos de Uso Frecuentes

### 1. Verificar un Caso IHQ Completo

```bash
# 1. Ver datos en BD
python cli_herramientas.py bd -b IHQ250001

# 2. Analizar extracción del PDF
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# 3. Validar extracción vs BD
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte
```

### 2. Verificar Exportación Excel

```bash
# 1. Listar archivos
python cli_herramientas.py excel -l

# 2. Estadísticas del último
python cli_herramientas.py excel -s

# 3. Verificar calidad
python cli_herramientas.py excel --calidad ultimo_archivo.xlsx

# 4. Verificar columnas
python cli_herramientas.py excel --verificar-columnas ultimo_archivo.xlsx
```

### 3. Debugging de Problemas de Extracción

```bash
# 1. Ver texto OCR del PDF
python cli_herramientas.py pdf -f problema.pdf --ocr

# 2. Segmentar casos
python cli_herramientas.py pdf -f problema.pdf --segmentar

# 3. Análisis completo
python cli_herramientas.py pdf -f problema.pdf --completo

# 4. Comparar con BD
python cli_herramientas.py pdf -f problema.pdf -i 250001 --comparar
```

### 4. Búsquedas en la BD

```bash
# Por paciente
python cli_herramientas.py bd -p "Maria Garcia"

# Por órgano
python cli_herramientas.py bd -o MAMA --json casos_mama.json

# Por diagnóstico
python cli_herramientas.py bd -d "CARCINOMA.*DUCTAL"
```

---

## 💡 Tips y Mejores Prácticas

### Para IA Agents:

1. **Usa el CLI unificado** (`cli_herramientas.py`) como punto de entrada principal
2. **Comandos cortos** disponibles: `-b`, `-f`, `-i`, `-l`, `-s`, `-p`, `-o`, `-d`
3. **Exporta a JSON** para procesamiento automatizado: `--json salida.json`
4. **Valida siempre** antes de confirmar resultados: `validar --ihq <numero> --pdf <archivo>`
5. **Verifica integridad** después de cambios: `bd --verificar`

### Flujo de Trabajo Recomendado:

```bash
# 1. Info del sistema
python cli_herramientas.py info

# 2. Verificar BD
python cli_herramientas.py bd --stats

# 3. Analizar caso
python cli_herramientas.py pdf -f documento.pdf -i <numero>

# 4. Validar
python cli_herramientas.py validar --ihq <numero> --pdf documento.pdf --reporte

# 5. Verificar Excel
python cli_herramientas.py excel -s
```

---

## 🔧 Configuración y Requisitos

### Requisitos:
- Python 3.8+
- Entorno virtual activado (`venv0`)
- Dependencias instaladas (`requirements.txt`)
- Base de datos SQLite en `data/huv_oncologia_NUEVO.db`

### Activar Entorno Virtual:

**Windows:**
```powershell
.\venv0\Scripts\activate
```

**Linux/Mac:**
```bash
source venv0/bin/activate
```

---

## 📊 Arquitectura

```
herramientas_ia/
├── cli_herramientas.py           # ⭐ CLI unificado (PUNTO DE ENTRADA)
├── consulta_base_datos.py         # 🔍 Consultas y gestión BD
├── analizar_pdf_completo.py       # 📄 Análisis profundo de PDFs
├── validar_extraccion.py          # ✅ Validación de extracción
├── verificar_excel.py             # 📊 Verificación de Excel
├── test_herramientas.py           # 🧪 Testing del sistema
├── validar_copilot_config.py     # 🤖 Validador de configuración Copilot
├── utilidades_debug.py            # 🐛 Debug avanzado
├── utilidades_comunes.py          # 🛠️ Funciones compartidas
├── README.md                      # 📖 Esta documentación
├── GUIA_COMPORTAMIENTO_IA.md      # 🤖 Guía para IAs
├── GUIA_TECNICA_COMPLETA.md       # 📚 Docs técnicas
├── REGLAS_ESTRICTAS_IA.md         # ⚠️ Reglas obligatorias
└── resultados/                    # 📊 Resultados de análisis
    ├── 2025-10-04_mejoras_validadas_v4.2.md
    ├── 2025-10-04_configuracion_copilot.md
    └── README.md
```

---

## 📝 Notas de Versión 4.2.1

### Nuevas Características:

✅ **CLI Unificado Mejorado**:
- Comandos cortos para uso rápido (`-b`, `-f`, `-i`, etc.)
- Soporte completo para exportación JSON
- Ayuda contextual con ejemplos

✅ **Validador de Extracción**:
- Compara extracción de PDF con BD
- Reportes de diferencias con similitud
- Exporta reportes JSON

✅ **Verificador de Excel**:
- Análisis de calidad de datos
- Verificación de columnas
- Comparación de exportaciones
- Detección de problemas

✅ **Mejoras en Consulta BD**:
- Búsquedas por paciente, órgano, diagnóstico
- Exportación a JSON
- Verificación de integridad

✅ **UTF-8 en Windows**:
- Todos los scripts con soporte UTF-8
- Sin errores de encoding
- Soporte completo para emojis

---

## 🆘 Soporte

Para reportar problemas o solicitar mejoras:
- **GitHub**: https://github.com/anthropics/claude-code/issues
- **Documentación**: `GUIA_TECNICA_COMPLETA.md`
- **Guía para IA**: `GUIA_COMPORTAMIENTO_IA.md`

---

*EVARISIS Gestor H.U.V - Sistema de Gestión Oncológica Inteligente*
*Hospital Universitario del Valle*
*v4.2.1 - Herramientas Optimizadas para IA*
