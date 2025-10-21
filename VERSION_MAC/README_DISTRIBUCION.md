# 🍎 GUÍA DE DISTRIBUCIÓN PARA MACOS

**EVARISIS - Sistema Inteligente de Gestión Oncológica**
**Versión macOS para Dr. Bayona**

---

## 📋 TABLA DE CONTENIDOS

1. [Requisitos Previos](#requisitos-previos)
2. [Flujo Completo de Distribución](#flujo-completo-de-distribución)
3. [Scripts Disponibles](#scripts-disponibles)
4. [Guía Paso a Paso](#guía-paso-a-paso)
5. [Solución de Problemas](#solución-de-problemas)
6. [Estructura del DMG Final](#estructura-del-dmg-final)
7. [Notas Importantes](#notas-importantes)

---

## 🎯 REQUISITOS PREVIOS

### En el Mac de Compilación (Desarrollador)

**Sistema Operativo:**
- macOS 10.15 (Catalina) o superior
- Se recomienda macOS 12.0 (Monterey) o superior

**Herramientas de Desarrollo:**
```bash
# Xcode Command Line Tools (OBLIGATORIO)
xcode-select --install

# Homebrew (Recomendado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Python y Dependencias:**
```bash
# Python 3.8 o superior
python3 --version

# Entorno virtual
python3 -m venv venv_mac
source venv_mac/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r ../requirements.txt
pip install pyinstaller==5.13.0
```

**Tesseract OCR:**
```bash
# Instalación vía Homebrew
brew install tesseract tesseract-lang

# Verificar instalación
tesseract --version
```

**Verificar que todo está listo:**
```bash
# Debe mostrar rutas válidas para todos
which python3
which pyinstaller
which tesseract
which sips
which iconutil
which hdiutil
```

---

## 🔄 FLUJO COMPLETO DE DISTRIBUCIÓN

### OPCIÓN A: DMG BÁSICO (Rápido - FASE 1)

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Preparar Icono (opcional)                         │
│  ./crear_icono_mac.sh                                       │
│  → Convierte icon.png a icon.icns                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: Compilar Aplicación                               │
│  ./compilar_mac_mejorado.sh                                 │
│  → Genera EVARISIS Cirugía Oncológica.app                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: Crear DMG Básico                                  │
│  ./crear_dmg.sh                                             │
│  → Genera EVARISIS_HUV_vX.X.X_macOS.dmg                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 4: Compartir con Dr. Bayona                          │
│  Enviar DMG por correo/USB/Google Drive/OneDrive            │
└─────────────────────────────────────────────────────────────┘
```

### OPCIÓN B: DMG PROFESIONAL (Recomendado - FASE 2) ⭐

```
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Preparar Icono (opcional)                         │
│  ./crear_icono_mac.sh                                       │
│  → Convierte icon.png a icon.icns                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: Compilar Aplicación                               │
│  ./compilar_mac_mejorado.sh                                 │
│  → Genera EVARISIS Cirugía Oncológica.app                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: Generar Fondo Visual (NUEVO - FASE 2) 🎨         │
│  ./generar_fondo_dmg.sh                                     │
│  → Genera fondo profesional institucional HUV               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 4: Crear DMG Profesional (NUEVO - FASE 2) ✨        │
│  ./crear_dmg_visual.sh                                      │
│  → Genera EVARISIS_HUV_vX.X.X_macOS_Professional.dmg        │
│  → Con diseño institucional HUV                             │
│  → Fondo personalizado con instrucciones visuales           │
│  → Iconos coordinados con flechas indicadoras               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PASO 5: Compartir con Dr. Bayona                          │
│  Enviar DMG por correo/USB/Google Drive/OneDrive            │
└─────────────────────────────────────────────────────────────┘
```

**Diferencias entre OPCIÓN A y OPCIÓN B:**

| Aspecto | DMG Básico (A) | DMG Profesional (B) ⭐ |
|---------|----------------|------------------------|
| **Funcionalidad** | ✅ Completa | ✅ Completa |
| **Apariencia** | ⚪ Básica | 🎨 Profesional HUV |
| **Fondo personalizado** | ❌ No | ✅ Sí |
| **Instrucciones visuales** | ❌ No | ✅ Sí (en fondo) |
| **Flecha drag-and-drop** | ❌ No | ✅ Sí |
| **Diseño institucional** | ❌ No | ✅ Logo/colores HUV |
| **Tiempo compilación** | ~10 min | ~12 min (+2 min) |
| **Tamaño final** | ~85 MB | ~86 MB (+1 MB) |
| **Impresión** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

**Recomendación:** Usa OPCIÓN B (DMG Profesional) para impresionar al Dr. Bayona 🎁

---

## 🛠️ SCRIPTS DISPONIBLES

### 1️⃣ `crear_icono_mac.sh`

**Propósito:** Convierte una imagen PNG en un icono .icns compatible con macOS.

**Uso:**
```bash
# Uso básico (usa imagenes/icon.png)
./crear_icono_mac.sh

# Uso personalizado
./crear_icono_mac.sh /ruta/a/imagen.png /ruta/salida/icon.icns
```

**Salida:**
- `imagenes/icon.icns` - Icono en formato macOS

**Detalles Técnicos:**
- Genera 10 resoluciones diferentes (16x16 a 1024x1024)
- Incluye versiones Retina (@2x)
- Usa herramientas nativas de macOS: `sips` e `iconutil`

**Duración:** ~30 segundos

---

### 2️⃣ `compilar_mac_mejorado.sh`

**Propósito:** Compila la aplicación Python en un ejecutable .app para macOS.

**Uso:**
```bash
# Ejecutar desde la carpeta VERSION_MAC
cd VERSION_MAC
./compilar_mac_mejorado.sh
```

**Proceso (12 pasos):**
1. ✅ Verificar dependencias externas (Tesseract)
2. ✅ Verificar entorno virtual de Python
3. ✅ Detectar arquitectura (Apple Silicon vs Intel)
4. ✅ Limpiar compilaciones anteriores
5. ✅ Verificar/Generar icono .icns
6. ✅ Verificar dependencias de Python
7. ✅ Instalar PyInstaller
8. ✅ Compilar aplicación con PyInstaller
9. ✅ Verificar estructura de la app
10. ✅ Generar README para usuario final
11. ✅ Resumen de advertencias
12. ✅ Instrucciones de distribución

**Salida:**
- `dist/EVARISIS Cirugía Oncológica.app` - Aplicación compilada
- `dist/LÉEME - IMPORTANTE.txt` - Guía para el usuario final

**Duración:** 5-10 minutos (depende del tamaño del proyecto)

**Advertencias Comunes:**
- ⚠️ Si Tesseract no está instalado, creará advertencia
- ⚠️ Contadores de advertencias al final
- ℹ️ Instrucciones claras sobre qué hacer

---

### 3️⃣ `crear_dmg.sh`

**Propósito:** Empaqueta la aplicación .app en un DMG profesional para distribución.

**Uso:**
```bash
# Ejecutar desde la carpeta VERSION_MAC
./crear_dmg.sh
```

**Proceso (8 pasos):**
1. ✅ Verificar que existe la aplicación .app
2. ✅ Limpiar DMG previos
3. ✅ Crear estructura temporal
4. ✅ Copiar aplicación al directorio temporal
5. ✅ Crear enlace simbólico a /Applications (drag-and-drop)
6. ✅ Generar README de instalación para usuario final
7. ✅ Crear y comprimir DMG
8. ✅ Limpiar archivos temporales

**Salida:**
- `dist/EVARISIS_HUV_vX.X.X_macOS.dmg` - Instalador DMG

**Contenido del DMG:**
- `EVARISIS Cirugía Oncológica.app` - Aplicación lista para usar
- `Applications` (symlink) - Atajo para instalación drag-and-drop
- `LÉEME - INSTALACIÓN.txt` - Guía completa de instalación

**Duración:** 3-5 minutos (depende del tamaño de la app)

---

### 4️⃣ `generar_fondo_dmg.py` (NUEVO - FASE 2) 🎨

**Propósito:** Genera el fondo visual profesional para el DMG con diseño institucional HUV.

**Uso:**
```bash
# Se ejecuta automáticamente desde generar_fondo_dmg.sh
# O directamente con Python:
python3 generar_fondo_dmg.py
```

**Características del fondo generado:**
- 🎨 Diseño institucional del Hospital Universitario del Valle
- 📐 Dimensiones: 600x400 px (coordinado con ventana DMG)
- 🏥 Colores institucionales HUV (azul profesional)
- ➡️ Flecha visual indicando drag-and-drop
- 📝 Instrucciones visuales en el fondo
- ✅ Nota sobre Tesseract ya instalado
- 🔢 Versión del sistema visible

**Salida:**
- `imagenes/dmg_background.png` - Fondo profesional PNG

**Duración:** ~10 segundos

**Dependencias:**
- Python 3.8+
- Pillow (PIL) - Se instala automáticamente si no está

---

### 5️⃣ `generar_fondo_dmg.sh` (NUEVO - FASE 2) 🎨

**Propósito:** Wrapper bash que ejecuta el generador Python de fondo visual.

**Uso:**
```bash
# Ejecutar desde la carpeta VERSION_MAC
./generar_fondo_dmg.sh
```

**Proceso:**
1. ✅ Verificar Python 3
2. ✅ Verificar/Instalar Pillow
3. ✅ Ejecutar generador Python
4. ✅ Verificar que se generó el PNG
5. ✅ Preguntar si desea visualizar

**Salida:**
- `imagenes/dmg_background.png` - Fondo profesional

**Duración:** ~30 segundos (incluye instalación de Pillow si es necesario)

---

### 6️⃣ `crear_dmg_visual.sh` (NUEVO - FASE 2) ✨

**Propósito:** Crea un DMG profesional con diseño visual institucional HUV.

**Uso:**
```bash
# Ejecutar desde la carpeta VERSION_MAC
./crear_dmg_visual.sh
```

**Diferencias vs crear_dmg.sh básico:**
- 🎨 **Fondo personalizado** con diseño institucional HUV
- ➡️ **Flecha visual** indicando donde arrastrar la app
- 📝 **Instrucciones visuales** directamente en el fondo
- 🏥 **Header institucional** con logo y nombre HUV
- 📐 **Iconos posicionados** estratégicamente (128x128)
- ✨ **Elementos decorativos** sutiles
- 📋 **README mejorado** específico para Dr. Bayona

**Proceso (9 pasos):**
1. ✅ Verificar/Generar fondo visual (automático)
2. ✅ Verificar que existe la aplicación .app
3. ✅ Limpiar DMG previos
4. ✅ Crear estructura temporal + copiar fondo
5. ✅ Copiar aplicación
6. ✅ Crear enlace simbólico a /Applications
7. ✅ Generar README personalizado para Dr. Bayona
8. ✅ Crear DMG con AppleScript para posicionar iconos
9. ✅ Comprimir con nivel máximo + limpiar

**Salida:**
- `dist/EVARISIS_HUV_vX.X.X_macOS_Professional.dmg` - DMG profesional

**Contenido del DMG:**
- `EVARISIS Cirugía Oncológica.app` - Aplicación
- `Applications` (symlink) - Atajo instalación
- `LÉEME - INSTALACIÓN.txt` - Guía específica Dr. Bayona
- `.background/background.png` - Fondo visual (oculto)

**Apariencia Visual:**
```
┌────────────────────────────────────────────────────────┐
│  🏥 EVARISIS - Cirugía Oncológica                      │
│  Hospital Universitario del Valle • Cali, Colombia     │
├────────────────────────────────────────────────────────┤
│                                                        │
│    ┌─────────┐                  ┌──────────┐         │
│    │  [App]  │  ────────────→   │ [folder] │         │
│    │  Icon   │   Arrastra aquí  │   Apps   │         │
│    └─────────┘                  └──────────┘         │
│                                                        │
│                  [📄 LÉEME.txt]                        │
├────────────────────────────────────────────────────────┤
│  1. Arrastra EVARISIS a Applications                  │
│  2. Abre desde Launchpad                              │
│  3. Click derecho → Abrir (primera vez)               │
│  ✅ Tesseract OCR ya está instalado en este Mac       │
└────────────────────────────────────────────────────────┘
```

**Duración:** 5-7 minutos (incluye generación de fondo)

**⭐ RECOMENDADO para Dr. Bayona** - Impresión profesional máxima

---

## 📖 GUÍA PASO A PASO

### PASO 0: Preparación Inicial

```bash
# 1. Clonar el repositorio o tener el código fuente
cd /ruta/a/ProyectoHUV9GESTOR_ONCOLOGIA_automatizado

# 2. Crear y activar entorno virtual
python3 -m venv venv_mac
source venv_mac/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Verificar que Tesseract está instalado
tesseract --version
# Si no está: brew install tesseract tesseract-lang

# 5. Ir a la carpeta VERSION_MAC
cd VERSION_MAC
```

---

### PASO 1: Generar Icono (Opcional)

Si ya tienes `imagenes/icon.icns`, puedes omitir este paso.

```bash
# Verificar si existe el icono PNG
ls -lh ../imagenes/icon.png

# Si existe, generar el icono .icns
chmod +x crear_icono_mac.sh
./crear_icono_mac.sh

# Verificar que se creó correctamente
ls -lh ../imagenes/icon.icns
```

**Resultado esperado:**
```
✅ Icono .icns creado para macOS
📦 Información del icono:
   📥 Entrada: /ruta/imagenes/icon.png
   📤 Salida: /ruta/imagenes/icon.icns
   📏 Tamaño: 150K
```

---

### PASO 2: Compilar la Aplicación

```bash
# Dar permisos de ejecución al script
chmod +x compilar_mac_mejorado.sh

# Ejecutar compilación
./compilar_mac_mejorado.sh
```

**Durante la compilación:**
- Verás 12 pasos numerados
- Cada paso muestra checkmarks ✅ cuando se completa
- Si hay advertencias ⚠️, se mostrarán al final
- Duración: 5-10 minutos

**Verificar que la compilación fue exitosa:**
```bash
# Verificar que existe la aplicación
ls -lh dist/"EVARISIS Cirugía Oncológica.app"

# Verificar estructura interna
ls -la dist/"EVARISIS Cirugía Oncológica.app"/Contents/
# Debe contener: Info.plist, MacOS/, Resources/

# Probar la aplicación localmente
open dist/"EVARISIS Cirugía Oncológica.app"
```

**Resultado esperado:**
```
✅ COMPILACIÓN COMPLETADA EXITOSAMENTE

📦 APLICACIÓN GENERADA:
   📁 Nombre: EVARISIS Cirugía Oncológica.app
   📏 Tamaño: 180MB
   📍 Ubicación: /ruta/VERSION_MAC/dist/
   🎯 Arquitectura: x86_64 (compatible con Intel y Rosetta 2)

⚠️  ADVERTENCIAS TOTALES: 1
   ⚠️ Tesseract debe estar instalado en el Mac de destino
```

---

### PASO 3: Crear DMG de Distribución

```bash
# Dar permisos de ejecución al script
chmod +x crear_dmg.sh

# Crear el DMG
./crear_dmg.sh
```

**Durante la creación:**
- Verás 8 pasos numerados
- Se monta temporalmente el DMG para configurarlo
- Se comprime automáticamente con nivel máximo
- Duración: 3-5 minutos

**Verificar que el DMG se creó correctamente:**
```bash
# Verificar que existe el DMG
ls -lh dist/EVARISIS_HUV_v*.dmg

# Ver información del DMG
hdiutil imageinfo dist/EVARISIS_HUV_v*.dmg | grep -E "Format|Compressed|Size"

# Probar el DMG localmente (montarlo)
open dist/EVARISIS_HUV_v*.dmg
```

**Resultado esperado:**
```
🎉 DMG GENERADO EXITOSAMENTE

📦 Información del DMG:
   📁 Nombre: EVARISIS_HUV_v2.1.6_macOS.dmg
   📏 Tamaño: 85MB (comprimido desde ~180MB)
   📍 Ubicación: /ruta/VERSION_MAC/dist/
   🔢 Versión: 2.1.6
   🔐 SHA-256: a1b2c3d4e5f6...
```

**Al abrir el DMG, debes ver:**
- Icono de la aplicación EVARISIS
- Atajo a /Applications (para arrastrar)
- Archivo LÉEME - INSTALACIÓN.txt

---

### PASO 3B: Crear DMG PROFESIONAL (OPCIÓN B - RECOMENDADO) ⭐

**Esta es la opción mejorada con diseño visual institucional HUV.**

**Prerrequisito:** Haber completado PASO 1 y PASO 2 (compilación)

```bash
# 1. Dar permisos de ejecución a los scripts visuales
chmod +x generar_fondo_dmg.sh
chmod +x generar_fondo_dmg.py
chmod +x crear_dmg_visual.sh

# 2. (OPCIONAL) Generar fondo visual primero para verificarlo
./generar_fondo_dmg.sh

# Esto genera: imagenes/dmg_background.png
# Puedes abrirlo para verificar el diseño:
open imagenes/dmg_background.png

# 3. Crear el DMG profesional
./crear_dmg_visual.sh

# NOTA: Si NO generaste el fondo en el paso 2,
# crear_dmg_visual.sh lo generará automáticamente
```

**Durante la creación:**
- Verás 9 pasos numerados (vs 8 del básico)
- PASO 0: Verifica/genera fondo visual automáticamente
- PASO 8: Configura apariencia con AppleScript
- Posiciona iconos estratégicamente
- Aplica fondo personalizado
- Duración: 5-7 minutos

**Verificar que el DMG PROFESIONAL se creó correctamente:**
```bash
# Verificar que existe el DMG
ls -lh dist/EVARISIS_HUV_v*_macOS_Professional.dmg

# Ver información del DMG
hdiutil imageinfo dist/EVARISIS_HUV_v*_Professional.dmg | grep -E "Format|Compressed|Size"

# Abrir el DMG para verificar apariencia visual
open dist/EVARISIS_HUV_v*_Professional.dmg
```

**Resultado esperado:**
```
🎉 DMG PROFESIONAL GENERADO EXITOSAMENTE

📦 Información del DMG:
   📁 Nombre: EVARISIS_HUV_v2.1.6_macOS_Professional.dmg
   📏 Tamaño: 86MB (comprimido con nivel máximo)
   📍 Ubicación: /ruta/VERSION_MAC/dist/
   🔢 Versión: 2.1.6
   🎨 Diseño: Profesional institucional HUV
   🔐 SHA-256: a1b2c3d4e5f6...

🎨 Características visuales:
   ✅ Diseño institucional del Hospital Universitario del Valle
   ✅ Iconos grandes (128x128) para fácil identificación
   ✅ Fondo personalizado con instrucciones visuales
   ✅ Flecha indicando drag-and-drop
   ✅ Información de versión visible
   ✅ Instrucciones paso a paso en el fondo
```

**Al abrir el DMG PROFESIONAL, debes ver:**

```
┌─────────────────────────────────────────────────────────────┐
│  🏥 EVARISIS - Cirugía Oncológica                           │
│  Hospital Universitario del Valle • Cali, Colombia          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│     [🎯 EVARISIS Icon]  ──→  [📁 Applications]             │
│     128x128                 "Arrastra aquí"                │
│                                                             │
│              [📄 LÉEME - INSTALACIÓN.txt]                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  1. Arrastra EVARISIS a la carpeta Applications            │
│  2. Abre la aplicación desde Launchpad                     │
│  3. Si macOS pregunta, haz click derecho → 'Abrir'         │
│  ✅ Tesseract OCR ya está instalado en este Mac            │
└─────────────────────────────────────────────────────────────┘
                     EVARISIS v2.1.6 • macOS
```

**Características visuales a verificar:**
- ✅ Fondo azul claro institucional (no blanco genérico)
- ✅ Header azul con "🏥 EVARISIS - Cirugía Oncológica"
- ✅ Subtítulo "Hospital Universitario del Valle • Cali, Colombia"
- ✅ Flecha gráfica desde el icono de la app hacia Applications
- ✅ Texto "Arrastra aquí" sobre la flecha
- ✅ Instrucciones numeradas en la parte inferior
- ✅ Nota verde "✅ Tesseract OCR ya está instalado"
- ✅ Versión visible en esquina inferior derecha
- ✅ Elementos decorativos sutiles (círculos azules)

**Comparación visual rápida:**

| Aspecto | DMG Básico | DMG Profesional ⭐ |
|---------|------------|-------------------|
| Fondo | Blanco liso | Azul HUV con gráficos |
| Instrucciones | Solo en README | En fondo + README |
| Flecha visual | ❌ No | ✅ Sí, gráfica |
| Logo institucional | ❌ No | ✅ Sí, en header |
| Impresión | Funcional | Profesional institucional |

**⭐ RECOMENDACIÓN:** Usa esta opción para impresionar al Dr. Bayona con un instalador de calidad profesional que refleja la seriedad del HUV.

---

### PASO 4: Compartir con Dr. Bayona

**Opciones para enviar el DMG:**

**Opción 1: Correo Electrónico**
```bash
# Si el archivo es menor a 25MB, puedes enviarlo por correo
# Si es mayor, usa Google Drive/OneDrive/WeTransfer
```

**Opción 2: Google Drive / OneDrive**
1. Sube el archivo DMG a tu nube
2. Comparte el enlace con Dr. Bayona
3. Asegúrate de que tenga permisos de descarga

**Opción 3: USB**
```bash
# Copiar a USB
cp dist/EVARISIS_HUV_v*.dmg /Volumes/USB_NAME/
```

**Instrucciones para Dr. Bayona:**

Envía este mensaje junto con el DMG:

```
Estimado Dr. Bayona,

Adjunto encontrará el instalador de EVARISIS para macOS.

PASOS PARA INSTALAR:

1. Haga doble clic en el archivo DMG
2. Arrastre "EVARISIS Cirugía Oncológica" a la carpeta "Applications"
3. Abra la aplicación desde Launchpad o Applications

IMPORTANTE - PRIMERA VEZ:
macOS puede mostrar una advertencia de seguridad.
Solución: Click derecho sobre la app → "Abrir" → Confirmar

REQUISITO OBLIGATORIO - TESSERACT OCR:
La aplicación necesita Tesseract para procesar PDFs.

Para instalar Tesseract:
1. Abra Terminal
2. Ejecute: brew install tesseract tesseract-lang
3. Si no tiene Homebrew, instálelo primero desde: https://brew.sh

Dentro del DMG encontrará un archivo "LÉEME - INSTALACIÓN.txt"
con instrucciones completas y detalladas.

Cualquier duda, no dude en contactarme.

Saludos,
[Tu nombre]
```

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### Problema 1: "Permission Denied" al ejecutar scripts

**Causa:** Los scripts no tienen permisos de ejecución.

**Solución:**
```bash
chmod +x crear_icono_mac.sh
chmod +x compilar_mac_mejorado.sh
chmod +x crear_dmg.sh
```

---

### Problema 2: "Command not found: pyinstaller"

**Causa:** PyInstaller no está instalado en el entorno virtual.

**Solución:**
```bash
# Activar entorno virtual
source venv_mac/bin/activate

# Instalar PyInstaller
pip install pyinstaller==5.13.0

# Verificar instalación
which pyinstaller
pyinstaller --version
```

---

### Problema 3: "Tesseract not found"

**Causa:** Tesseract OCR no está instalado.

**Solución:**
```bash
# Instalar con Homebrew
brew install tesseract tesseract-lang

# Verificar instalación
tesseract --version
which tesseract
```

**Nota:** El script compilar_mac_mejorado.sh continuará aunque Tesseract no esté instalado, pero generará una advertencia. La aplicación se compilará correctamente, pero Dr. Bayona deberá instalar Tesseract en su Mac.

---

### Problema 4: "Error building .app"

**Causa:** Falta alguna dependencia de Python.

**Solución:**
```bash
# Verificar que todas las dependencias están instaladas
pip install -r ../requirements.txt

# Verificar que el entorno virtual está activo
which python3
# Debe mostrar: /ruta/venv_mac/bin/python3

# Si no está activo
source venv_mac/bin/activate
```

---

### Problema 5: "DMG creation failed"

**Causa:** No se encontró la aplicación .app.

**Solución:**
```bash
# Verificar que existe la aplicación
ls -lh dist/"EVARISIS Cirugía Oncológica.app"

# Si no existe, compilar primero
./compilar_mac_mejorado.sh

# Luego crear el DMG
./crear_dmg.sh
```

---

### Problema 6: "Xcode Command Line Tools not installed"

**Causa:** No están instaladas las herramientas de Xcode.

**Solución:**
```bash
# Instalar Xcode Command Line Tools
xcode-select --install

# Verificar instalación
xcode-select -p
# Debe mostrar: /Library/Developer/CommandLineTools
```

---

### Problema 7: "Icon not found"

**Causa:** No existe el archivo icon.icns.

**Solución:**
```bash
# Opción 1: Generar el icono
./crear_icono_mac.sh

# Opción 2: Si no tienes icon.png, crear uno genérico
# El script compilar_mac_mejorado.sh generará uno automáticamente
# si no encuentra el icono
```

---

### Problema 8: "Application is damaged and can't be opened" (en Mac de destino)

**Causa:** macOS Gatekeeper bloqueando la aplicación porque no está firmada.

**Solución para Dr. Bayona:**
```bash
# Opción 1: Click derecho → Abrir → Confirmar

# Opción 2: Eliminar atributos de cuarentena
xattr -cr "/Applications/EVARISIS Cirugía Oncológica.app"
```

**Solución para desarrolladores (firmar la app - requiere Apple Developer Account):**
```bash
# Firmar la aplicación
codesign --force --deep --sign - "dist/EVARISIS Cirugía Oncológica.app"
```

---

## 📦 ESTRUCTURA DEL DMG FINAL

```
EVARISIS_HUV_v2.1.6_macOS.dmg
│
├── EVARISIS Cirugía Oncológica.app/
│   ├── Contents/
│   │   ├── Info.plist
│   │   ├── MacOS/
│   │   │   └── EVARISIS Cirugía Oncológica (ejecutable)
│   │   ├── Resources/
│   │   │   ├── icon.icns
│   │   │   ├── ui.py
│   │   │   ├── core/
│   │   │   ├── config/
│   │   │   ├── herramientas_ia/
│   │   │   └── ... (todos los archivos del proyecto)
│   │   └── Frameworks/ (dependencias Python)
│
├── Applications → /Applications (symlink)
│
└── LÉEME - INSTALACIÓN.txt
    ├── Instrucciones de instalación
    ├── Requisitos del sistema
    ├── Cómo instalar Tesseract
    ├── Solución de problemas comunes
    └── Información de soporte
```

---

## 📝 NOTAS IMPORTANTES

### Arquitectura

**El script genera por defecto una aplicación UNIVERSAL que funciona en:**
- ✅ Intel Macs (x86_64)
- ✅ Apple Silicon Macs (M1/M2/M3 vía Rosetta 2)

Si quieres compilar específicamente para Apple Silicon:
```bash
# Editar compilar_mac_mejorado.sh
# Cambiar la línea:
--target-arch x86_64 \
# Por:
--target-arch arm64 \
```

**Recomendación:** Dejar x86_64 para máxima compatibilidad.

---

### Tamaños de Archivo

**Tamaños esperados:**
- `.app` compilada: ~150-200 MB
- DMG comprimido: ~70-100 MB (compresión ~40-50%)

**Si el tamaño es mucho mayor:**
- Verifica que no hay archivos innecesarios en el proyecto
- Revisa que `build/` y `dist/` previos fueron eliminados
- Considera excluir carpetas grandes en `.spec` de PyInstaller

---

### Versión del Sistema

**El número de versión se lee automáticamente de:**
```python
# config/version_info.py
VERSION = "2.1.6"
```

**Para cambiar la versión:**
1. Edita `config/version_info.py`
2. Recompila la aplicación
3. El DMG usará automáticamente la nueva versión

---

### Dependencias Externas (Tesseract)

**IMPORTANTE:** Tesseract OCR es una dependencia EXTERNA que NO se puede empaquetar dentro de la app.

**Dr. Bayona DEBE instalarlo en su Mac:**
```bash
brew install tesseract tesseract-lang
```

**Alternativa sin Homebrew:**
- Descargar instalador desde: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar manualmente

**La aplicación detectará automáticamente Tesseract si está en:**
- `/usr/local/bin/tesseract` (Homebrew Intel)
- `/opt/homebrew/bin/tesseract` (Homebrew Apple Silicon)
- `/usr/bin/tesseract`

---

### Seguridad y Gatekeeper

**macOS Gatekeeper bloqueará la app la primera vez porque:**
1. No está firmada con certificado de desarrollador de Apple
2. No está notarizada por Apple

**Soluciones para Dr. Bayona:**

**Opción 1 (Recomendada):**
1. Click derecho sobre la app
2. Seleccionar "Abrir"
3. Confirmar en el diálogo de seguridad
4. macOS recordará esta decisión

**Opción 2:**
1. Preferencias del Sistema → Seguridad y Privacidad
2. Pestaña "General"
3. Clic en "Abrir de todas formas"

**Opción 3 (Terminal):**
```bash
xattr -cr "/Applications/EVARISIS Cirugía Oncológica.app"
```

---

### Firma de Código (Opcional - Avanzado)

**Si tienes una cuenta de Apple Developer:**

```bash
# 1. Obtener tu identidad de firma
security find-identity -v -p codesigning

# 2. Firmar la aplicación
codesign --force --deep --sign "Apple Development: Tu Nombre (TEAM_ID)" \
  "dist/EVARISIS Cirugía Oncológica.app"

# 3. Verificar firma
codesign -vv "dist/EVARISIS Cirugía Oncológica.app"

# 4. Notarizar (requiere Xcode)
xcrun altool --notarize-app \
  --primary-bundle-id "com.huv.evarisis" \
  --username "tu@email.com" \
  --password "@keychain:AC_PASSWORD" \
  --file "dist/EVARISIS_HUV_v2.1.6_macOS.dmg"
```

**Nota:** Esto NO es obligatorio para uso interno en el hospital.

---

### Pruebas Recomendadas

**Antes de enviar a Dr. Bayona, prueba en tu Mac:**

```bash
# 1. Montar el DMG
open dist/EVARISIS_HUV_v*.dmg

# 2. Copiar la app a /Applications
cp -R /Volumes/EVARISIS*/EVARISIS*.app /Applications/

# 3. Ejecutar la aplicación
open /Applications/EVARISIS*.app

# 4. Verificar funcionalidades básicas:
#    - Que abra la interfaz gráfica
#    - Que detecte Tesseract
#    - Que pueda procesar un PDF de prueba
#    - Que pueda exportar a Excel

# 5. Limpiar
rm -rf /Applications/EVARISIS*.app
```

---

### Logs y Debugging

**Si Dr. Bayona reporta problemas:**

**Opción 1: Ver logs de la aplicación**
```bash
# Ejecutar la app desde Terminal para ver errores
/Applications/EVARISIS*.app/Contents/MacOS/EVARISIS*
```

**Opción 2: Ver logs del sistema**
```bash
# Abrir Console.app
# Filtrar por: "EVARISIS"
```

**Opción 3: Verificar permisos**
```bash
# Verificar que la app tiene permisos de ejecución
ls -la /Applications/EVARISIS*.app/Contents/MacOS/
```

---

### Actualizaciones Futuras

**Para distribuir una nueva versión:**

1. Actualizar código fuente
2. Cambiar versión en `config/version_info.py`
3. Recompilar con `./compilar_mac_mejorado.sh`
4. Regenerar DMG con `./crear_dmg.sh`
5. Enviar nuevo DMG a Dr. Bayona

**Dr. Bayona simplemente:**
1. Elimina la app anterior de /Applications
2. Instala la nueva versión desde el nuevo DMG
3. La base de datos y configuraciones se preservan (están en ~/Library/Application Support/)

---

## ✅ CHECKLIST PRE-DISTRIBUCIÓN

Antes de enviar el DMG a Dr. Bayona, verifica:

- [ ] El DMG se abre correctamente
- [ ] La aplicación está visible dentro del DMG
- [ ] El symlink a /Applications funciona
- [ ] El archivo LÉEME está presente y legible
- [ ] La app se puede arrastrar a /Applications
- [ ] La app se ejecuta correctamente (prueba local)
- [ ] Tesseract está instalado en tu Mac (para pruebas)
- [ ] La versión en el nombre del DMG es correcta
- [ ] El tamaño del DMG es razonable (~70-100 MB)
- [ ] Has probado importar un PDF de ejemplo
- [ ] Has verificado que la interfaz gráfica se ve bien
- [ ] Has leído el README de instalación para asegurarte de que es claro

---

## 📧 SOPORTE

**Para problemas técnicos durante la compilación:**
- Revisar sección "Solución de Problemas" arriba
- Verificar logs en Terminal durante la compilación
- Revisar que todas las dependencias están instaladas

**Para problemas en el Mac de Dr. Bayona:**
- Referirlo al archivo "LÉEME - INSTALACIÓN.txt" incluido en el DMG
- Verificar que Tesseract está instalado
- Verificar permisos de seguridad de macOS

---

## 🎉 ¡LISTO!

Con estos scripts, puedes generar fácilmente un instalador DMG profesional para macOS que Dr. Bayona puede usar con un simple doble clic.

**Resumen del proceso:**
1. `./crear_icono_mac.sh` → Icono .icns
2. `./compilar_mac_mejorado.sh` → Aplicación .app
3. `./crear_dmg.sh` → Instalador DMG
4. Compartir DMG con Dr. Bayona

**Tiempo total:** ~10-15 minutos

---

**Versión de este documento:** 1.0.0
**Fecha:** 2025-10-21
**Para:** EVARISIS v2.1.6 macOS
**Hospital Universitario del Valle - Cali, Colombia**
