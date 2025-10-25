# ⚠️ REGLAS ESTRICTAS PARA IA - GESTOR ONCOLOGÍA HUV

**VERSIÓN**: 4.2.1
**FECHA**: 4 de octubre de 2025
**PRIORIDAD**: MÁXIMA - CUMPLIMIENTO OBLIGATORIO

---

## 🚫 PROHIBICIONES ABSOLUTAS

### 1. ❌ NUNCA Crear Scripts en el Directorio Raíz

**PROHIBIDO**:
- ❌ Crear archivos `.py` en el directorio raíz del proyecto
- ❌ Crear archivos `test_*.py` en el directorio raíz
- ❌ Crear archivos `verificar_*.py` en el directorio raíz
- ❌ Crear archivos `analizar_*.py` en el directorio raíz
- ❌ Crear archivos `debug_*.py` en el directorio raíz

**RAZÓN**: Ya existen herramientas CLI completas en `herramientas_ia/` que cubren TODOS los casos de uso.

**EXCEPCIONES**: Solo se permiten archivos `.py` en el raíz si son parte del flujo principal del sistema (`ui.py`).

---

### 2. ❌ NUNCA Crear Herramientas Redundantes

**PROHIBIDO**:
- ❌ Crear scripts para consultar la BD (ya existe `consulta_base_datos.py`)
- ❌ Crear scripts para analizar PDFs (ya existe `analizar_pdf_completo.py`)
- ❌ Crear scripts para validar datos (ya existe `validar_extraccion.py`)
- ❌ Crear scripts para verificar Excel (ya existe `verificar_excel.py`)
- ❌ Crear scripts de "prueba rápida" o "test simple"

**RAZÓN**: Todas las funcionalidades ya están implementadas y probadas.

---

### 3. ❌ NUNCA Crear Reportes/Documentos en el Raíz

**PROHIBIDO**:
- ❌ Crear archivos `.md` en el raíz (excepto `CHANGELOG_*.md`)
- ❌ Crear archivos `.txt` de prueba en el raíz
- ❌ Crear archivos `.json` de resultados en el raíz

**UBICACIONES CORRECTAS**:
- ✅ Reportes de mejoras → `herramientas_ia/resultados/`
- ✅ Logs de prueba → `LEGACY/test_files_cleanup/`
- ✅ Resultados JSON → Carpeta del usuario o `data/`

---

## ✅ ALTERNATIVAS CORRECTAS

### Antes de Crear Cualquier Script Nuevo:

#### 1️⃣ PREGÚNTATE: ¿Ya existe una herramienta para esto?

**Herramientas Disponibles**:

| Necesidad | Herramienta Existente | Comando |
|-----------|----------------------|---------|
| Consultar BD | `consulta_base_datos.py` | `python cli_herramientas.py bd --stats` |
| Buscar caso IHQ | `consulta_base_datos.py` | `python cli_herramientas.py bd -b IHQ250001` |
| Analizar PDF | `analizar_pdf_completo.py` | `python cli_herramientas.py pdf -f archivo.pdf -i 250001` |
| Validar extracción | `validar_extraccion.py` | `python cli_herramientas.py validar --ihq 250001 --pdf archivo.pdf` |
| Verificar Excel | `verificar_excel.py` | `python cli_herramientas.py excel -s` |
| Test del sistema | `test_herramientas.py` | `python cli_herramientas.py test` |

#### 2️⃣ USA EL CLI UNIFICADO

**SIEMPRE** usa `cli_herramientas.py` como punto de entrada:

```bash
# Ver ayuda completa
python cli_herramientas.py -h

# Ver ayuda de un comando específico
python cli_herramientas.py bd -h
python cli_herramientas.py pdf -h
python cli_herramientas.py validar -h
```

#### 3️⃣ SI LA FUNCIONALIDAD NO EXISTE: Extiende la Herramienta Existente

**En lugar de crear un script nuevo**, agrega la funcionalidad a la herramienta correspondiente:

- ¿Necesitas una nueva consulta a BD? → Agrega argumento a `consulta_base_datos.py`
- ¿Necesitas un nuevo análisis de PDF? → Agrega argumento a `analizar_pdf_completo.py`
- ¿Necesitas una nueva validación? → Agrega argumento a `validar_extraccion.py`

---

## 📋 COMANDOS COMPLETOS DISPONIBLES

### 🔍 Base de Datos (bd)

```bash
# Estadísticas
python cli_herramientas.py bd --stats
python cli_herramientas.py bd -s

# Buscar caso
python cli_herramientas.py bd --buscar IHQ250001
python cli_herramientas.py bd -b IHQ250001

# Listar registros
python cli_herramientas.py bd --listar --limite 50
python cli_herramientas.py bd -l --limite 100

# Buscar por paciente
python cli_herramientas.py bd --paciente "Maria Garcia"
python cli_herramientas.py bd -p "Juan"

# Filtrar por órgano
python cli_herramientas.py bd --organo PULMON
python cli_herramientas.py bd -o MAMA

# Filtrar por diagnóstico (regex)
python cli_herramientas.py bd --diagnostico "ADENOCARCINOMA"
python cli_herramientas.py bd -d "CARCINOMA.*DUCTAL"

# Ver biomarcadores
python cli_herramientas.py bd --biomarcadores IHQ250001

# Verificar integridad
python cli_herramientas.py bd --verificar

# Contar por categoría
python cli_herramientas.py bd --contar

# Exportar a JSON
python cli_herramientas.py bd -b IHQ250001 --json resultado.json
```

### 📄 Análisis PDF (pdf)

```bash
# Análisis rápido de caso específico
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001

# Solo OCR
python cli_herramientas.py pdf -f documento.pdf --ocr

# Segmentar casos
python cli_herramientas.py pdf -f ordenamientos.pdf --segmentar

# Análisis completo
python cli_herramientas.py pdf -f documento.pdf --completo

# Solo paciente
python cli_herramientas.py pdf -f documento.pdf --paciente

# Solo médico
python cli_herramientas.py pdf -f documento.pdf --medico

# Solo biomarcadores
python cli_herramientas.py pdf -f documento.pdf --biomarcadores

# Buscar patrón
python cli_herramientas.py pdf -f documento.pdf --patron "Ki-67"

# Comparar con BD
python cli_herramientas.py pdf -f ordenamientos.pdf -i 250001 --comparar

# Exportar a JSON
python cli_herramientas.py pdf -f documento.pdf -i 250001 --json salida.json
```

### 📊 Excel (excel)

```bash
# Listar archivos
python cli_herramientas.py excel --listar
python cli_herramientas.py excel -l

# Estadísticas del último
python cli_herramientas.py excel --stats
python cli_herramientas.py excel -s

# Calidad de datos
python cli_herramientas.py excel --calidad archivo.xlsx

# Verificar columnas
python cli_herramientas.py excel --verificar-columnas archivo.xlsx

# Comparar dos archivos
python cli_herramientas.py excel --comparar archivo1.xlsx archivo2.xlsx

# Abrir archivo
python cli_herramientas.py excel --abrir archivo.xlsx
python cli_herramientas.py excel --ultimo
```

### ✅ Validación (validar)

```bash
# Validar caso con PDF
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf

# Validación completa
python cli_herramientas.py validar --ihq 250001 --completo

# Solo diferencias
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --solo-diferencias

# Generar reporte
python cli_herramientas.py validar --ihq 250001 --pdf ordenamientos.pdf --reporte

# Campos específicos
python cli_herramientas.py validar --ihq 250001 --campos "Edad" "Genero" "Diagnóstico"
```

### 🧪 Testing (test)

```bash
# Todos los tests
python cli_herramientas.py test

# Test específico
python cli_herramientas.py test --imports
python cli_herramientas.py test --bd
python cli_herramientas.py test --ocr
python cli_herramientas.py test --extractores
python cli_herramientas.py test --todo
```

### 🐛 Debug e Info

```bash
# Debug
python cli_herramientas.py debug

# Información del sistema
python cli_herramientas.py info
```

---

## 🎯 FLUJO DE TRABAJO OBLIGATORIO

### Cuando Necesites Información:

1. **Primero**: Verifica si existe un comando CLI
2. **Segundo**: Usa el comando existente
3. **Tercero**: Si NO existe, pregunta al usuario antes de crear algo nuevo
4. **Último Recurso**: Si es absolutamente necesario, agrega a herramienta existente

### Ejemplo Correcto:

❌ **INCORRECTO** (crear script nuevo):
```python
# archivo: test_caso_ihq.py (EN EL RAÍZ)
# Consultar caso IHQ250001
...
```

✅ **CORRECTO** (usar herramienta existente):
```bash
python cli_herramientas.py bd -b IHQ250001
```

### Ejemplo de Extensión Correcta:

Si necesitas una nueva funcionalidad que NO existe:

❌ **INCORRECTO** (crear script nuevo):
```python
# archivo: exportar_biomarcadores.py (EN EL RAÍZ)
# Exportar biomarcadores a CSV
...
```

✅ **CORRECTO** (extender herramienta existente):
```python
# En consulta_base_datos.py, agregar:
parser.add_argument('--exportar-biomarcadores-csv', ...)

# Luego usar:
python cli_herramientas.py bd --exportar-biomarcadores-csv salida.csv
```

---

## 📁 ESTRUCTURA DE ARCHIVOS PERMITIDA

### ✅ Archivos Permitidos en el Raíz:

```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py                      # ✅ Interfaz principal
├── requirements.txt           # ✅ Dependencias
├── .gitignore                # ✅ Git
├── .gitattributes            # ✅ Git
├── COMPILADOR.bat            # ✅ Scripts de sistema
├── iniciar_python.bat        # ✅ Scripts de sistema
├── CHANGELOG_v*.md           # ✅ Changelogs oficiales
└── [NADA MÁS]                # ❌ NO crear otros archivos
```

### ✅ Ubicaciones Correctas:

```
herramientas_ia/               # ✅ TODAS las herramientas CLI
├── cli_herramientas.py        # Punto de entrada principal
├── consulta_base_datos.py     # Consultas BD
├── analizar_pdf_completo.py   # Análisis PDF
├── validar_extraccion.py      # Validación
├── verificar_excel.py         # Verificación Excel
├── test_herramientas.py       # Tests
└── resultados/                # ✅ Reportes aquí

LEGACY/                        # ✅ Archivos obsoletos
└── test_files_cleanup/        # ✅ Tests antiguos

data/                          # ✅ Datos y BD
config/                        # ✅ Configuración
core/                          # ✅ Código core
```

---

## 🚨 CHECKLIST ANTES DE CREAR ARCHIVOS

Antes de crear CUALQUIER archivo nuevo, responde:

- [ ] ¿Ya existe una herramienta que hace esto?
- [ ] ¿Puedo usar el CLI unificado en su lugar?
- [ ] ¿Puedo extender una herramienta existente?
- [ ] ¿He consultado `README.md` en `herramientas_ia/`?
- [ ] ¿He consultado este documento `REGLAS_ESTRICTAS_IA.md`?

**Si respondiste NO a todas**: DETENTE y pregunta al usuario.

---

## 📌 RECORDATORIOS CLAVE

1. **El CLI unificado (`cli_herramientas.py`) es la ÚNICA interfaz que necesitas**
2. **TODAS las funcionalidades ya existen - úsalas**
3. **NO crees scripts de prueba rápida - usa las herramientas existentes**
4. **NO crees reportes en el raíz - usa `herramientas_ia/resultados/`**
5. **Cuando tengas dudas, revisa `herramientas_ia/README.md`**

---

## ⚡ COMANDOS MÁS USADOS (MEMORIZA ESTOS)

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
```

---

## 🔒 CUMPLIMIENTO OBLIGATORIO

**ESTAS REGLAS SON OBLIGATORIAS Y NO NEGOCIABLES.**

Si una IA las viola:
1. El código será rechazado
2. Los archivos creados incorrectamente serán movidos a `LEGACY/`
3. Se deberá usar la herramienta correcta

**Última actualización**: 4 de octubre de 2025
**Versión del sistema**: 4.2.1
**Estado**: ACTIVO Y OBLIGATORIO
