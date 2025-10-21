# 🍎 EVARISIS CIRUGÍA ONCOLÓGICA - VERSIÓN macOS

**Versión**: 2.1.6
**Compatible con**: macOS 10.14+ (Mojave o superior)
**Python**: 3.8 o superior
**Arquitecturas**: Intel y Apple Silicon (M1/M2/M3)

---

## 📋 TRES SCRIPTS ESENCIALES

Esta carpeta contiene **3 scripts bash** probados y funcionales al 100% para macOS:

### 1. 🔧 `instalar_entorno_mac.sh` - INSTALADOR
**Función**: Crea el entorno virtual e instala todas las dependencias

```bash
# Dar permisos de ejecución
chmod +x instalar_entorno_mac.sh

# Ejecutar
./instalar_entorno_mac.sh
```

**Lo que hace**:
- ✅ Verifica Python 3 y pip
- ✅ Crea entorno virtual `venv0/` en VERSION_MAC/
- ✅ Instala 61 paquetes de requirements.txt
- ✅ Verifica módulos críticos (numpy, pandas, ttkbootstrap, etc.)
- ✅ Muestra instrucciones de uso
- ⚡ **Ejecutar SOLO UNA VEZ** (primera instalación)

**Resultado**: Entorno virtual listo para usar

---

### 2. 🚀 `iniciar_python_mac.sh` - LAUNCHER
**Función**: Inicia la aplicación (uso diario)

```bash
# Dar permisos de ejecución (solo primera vez)
chmod +x iniciar_python_mac.sh

# Ejecutar (cada vez que quieras usar la app)
./iniciar_python_mac.sh
```

**Lo que hace**:
- ✅ Verifica que el entorno virtual exista
- ✅ Activa `venv0/`
- ✅ Verifica ui.py
- ✅ Ejecuta la aplicación con argumentos de EVARISIS
- ⚡ **Ejecutar CADA VEZ** que quieras usar la aplicación

**Resultado**: Aplicación en ejecución

---

### 3. 📦 `compilar_mac.sh` - COMPILADOR (NUEVO)
**Función**: Compila la aplicación en un ejecutable .app para macOS

```bash
# Dar permisos de ejecución
chmod +x compilar_mac.sh

# Ejecutar
./compilar_mac.sh
```

**Lo que hace**:
- ✅ Verifica entorno virtual
- ✅ Instala/verifica PyInstaller
- ✅ Detecta arquitectura (Intel/Apple Silicon)
- ✅ Limpia compilaciones anteriores
- ✅ Compila ui.py con todas las dependencias
- ✅ Crea bundle `EVARISIS HUV.app`
- ✅ Configura Info.plist
- ✅ Incluye icono (si existe)
- ⚡ **Ejecutar CUANDO QUIERAS DISTRIBUIR** la aplicación

**Resultado**: `dist/EVARISIS HUV.app` - Ejecutable independiente

---

## 🎯 FLUJO DE TRABAJO RECOMENDADO

### Primera Vez (Instalación)
```bash
# 1. Instalar entorno
chmod +x instalar_entorno_mac.sh
./instalar_entorno_mac.sh

# 2. Probar que funciona
chmod +x iniciar_python_mac.sh
./iniciar_python_mac.sh
```

### Uso Diario (Desarrollo)
```bash
# Simplemente ejecutar
./iniciar_python_mac.sh
```

### Distribución (Compilar)
```bash
# Crear ejecutable para distribuir
chmod +x compilar_mac.sh
./compilar_mac.sh

# Resultado: dist/EVARISIS HUV.app
# Puedes copiar esta app a /Applications
# O distribuirla a otros Macs
```

---

## 📂 ESTRUCTURA DE VERSION_MAC/

```
VERSION_MAC/
├── README.md                      # ⭐ Esta guía
├── README_MAC.md                  # Guía técnica detallada
├── README_INSTALACION_MACOS.md    # Guía de instalación completa
│
├── instalar_entorno_mac.sh       # 🔧 Script 1: Instalador
├── iniciar_python_mac.sh         # 🚀 Script 2: Launcher
├── compilar_mac.sh               # 📦 Script 3: Compilador (NUEVO)
│
└── venv0/                         # Entorno virtual (creado por instalador)
    ├── bin/
    ├── lib/
    └── ...
```

---

## 🔐 PERMISOS DE EJECUCIÓN

```bash
# Dar permisos a todos los scripts de una vez
chmod +x *.sh

# O individualmente
chmod +x instalar_entorno_mac.sh
chmod +x iniciar_python_mac.sh
chmod +x compilar_mac.sh
```

---

## 📊 COMPARATIVA DE LOS 3 SCRIPTS

| Script | Cuándo Usar | Frecuencia | Resultado |
|--------|-------------|------------|-----------|
| **instalar_entorno_mac.sh** | Primera instalación | 1 vez | venv0/ con dependencias |
| **iniciar_python_mac.sh** | Uso normal | Diario | Aplicación en ejecución |
| **compilar_mac.sh** | Distribuir | Ocasional | EVARISIS HUV.app |

---

## 🍏 CARACTERÍSTICAS DEL COMPILADOR

### Ventajas del .app Compilado
- ✅ **Ejecutable independiente**: No necesita Python instalado
- ✅ **Bundle macOS nativo**: Icono, Info.plist, estructura .app
- ✅ **Distribución fácil**: Copiar y ejecutar en cualquier Mac
- ✅ **Integración con macOS**: Aparece en Launchpad, Dock, etc.
- ✅ **Detección automática de arquitectura**: Intel o Apple Silicon

### Qué Incluye el Compilador
```
EVARISIS HUV.app/
├── Contents/
│   ├── MacOS/
│   │   └── EVARISIS HUV           # Ejecutable principal
│   ├── Resources/
│   │   ├── app.icns              # Icono de la aplicación
│   │   ├── config/                # Carpeta config incluida
│   │   ├── core/                  # Módulos Python incluidos
│   │   └── imagenes/              # Recursos gráficos
│   └── Info.plist                 # Metadatos de la aplicación
```

### Requisitos en el Mac de Destino
- ⚠️ **Tesseract OCR**: Debe estar instalado (`brew install tesseract`)
- ⚠️ **Python**: NO necesario (incluido en el bundle)
- ⚠️ **Dependencias**: NO necesarias (incluidas en el bundle)
- ✅ **Arquitectura compatible**: Compilar en Intel para Intel, M1 para M1

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### El compilador falla
```bash
# Verificar PyInstaller
source venv0/bin/activate
pip install --upgrade pyinstaller

# Verificar dependencias
pip list

# Limpiar y reintentar
rm -rf dist/ build/ *.spec
./compilar_mac.sh
```

### La app compilada no abre
```bash
# Quitar cuarentena de macOS
xattr -cr "dist/EVARISIS HUV.app"

# Verificar permisos
chmod -R 755 "dist/EVARISIS HUV.app"

# Ejecutar desde terminal para ver errores
open -a "dist/EVARISIS HUV.app"
```

### Error "damaged and can't be opened"
```bash
# Deshabilitar Gatekeeper temporalmente
sudo spctl --master-disable

# Abrir la app
open -a "dist/EVARISIS HUV.app"

# Rehabilitar Gatekeeper
sudo spctl --master-enable
```

### El instalador falla
```bash
# Verificar Python
python3 --version

# Si falta, instalar con Homebrew
brew install python3

# O descargar de python.org
```

### El launcher no encuentra venv0
```bash
# Ejecutar primero el instalador
./instalar_entorno_mac.sh

# Verificar que se creó
ls -la venv0/
```

---

## 📋 REQUISITOS PREVIOS (macOS)

### Obligatorios
```bash
# Python 3.8+
python3 --version

# Homebrew (recomendado)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Tesseract OCR
brew install tesseract tesseract-lang
```

### Opcionales
```bash
# LM Studio (para IA)
Descargar de: https://lmstudio.ai

# Xcode Command Line Tools (si no están)
xcode-select --install
```

---

## 🎨 ICONOS Y APARIENCIA

### Crear icono .icns
```bash
# Si tienes icon.png
sips -s format icns imagenes/icon.png --out imagenes/icon.icns

# El compilador lo detecta automáticamente
```

### Modo Oscuro
- ✅ La aplicación detecta automáticamente el tema de macOS
- ✅ Modo oscuro macOS → Tema 'darkly'
- ✅ Modo claro macOS → Tema 'litera'

---

## 🚀 GUÍA RÁPIDA DE 3 PASOS

### PASO 1: Instalar (Primera vez)
```bash
chmod +x instalar_entorno_mac.sh
./instalar_entorno_mac.sh
```

### PASO 2: Ejecutar (Diario)
```bash
./iniciar_python_mac.sh
```

### PASO 3: Compilar (Opcional - Distribuir)
```bash
./compilar_mac.sh
```

---

## 📝 NOTAS IMPORTANTES

### Sobre el Entorno Virtual
- ✅ Se crea en `VERSION_MAC/venv0/`
- ✅ Es independiente del `venv0/` de Windows (en raíz)
- ✅ Contiene las mismas dependencias (61 paquetes)
- ✅ Es específico de macOS

### Sobre la Compilación
- ⚠️ El .app solo funciona en la arquitectura en que se compiló
- ⚠️ Compilar en M1 → Solo funciona en M1/M2/M3
- ⚠️ Compilar en Intel → Solo funciona en Intel Macs
- ✅ El tamaño del .app es ~150-200 MB
- ✅ Tesseract debe instalarse por separado en el Mac de destino

### Sobre los Argumentos de EVARISIS
- El launcher usa argumentos específicos para integración con EVARISIS Dashboard
- Puedes modificar `iniciar_python_mac.sh` para cambiar nombre, cargo, foto, etc.
- Líneas 66-71 del script

---

## 📚 DOCUMENTACIÓN ADICIONAL

- **README_MAC.md**: Guía técnica completa
- **README_INSTALACION_MACOS.md**: Guía de instalación paso a paso
- **../documentacion_actualizada/**: Documentación del proyecto

---

## ✅ CHECKLIST DE VERIFICACIÓN

### Instalación Correcta
- [ ] Python 3.8+ instalado
- [ ] Homebrew instalado
- [ ] Tesseract OCR instalado
- [ ] `instalar_entorno_mac.sh` ejecutado
- [ ] `venv0/` creado en VERSION_MAC/
- [ ] 61 paquetes instalados correctamente

### Funcionamiento
- [ ] `iniciar_python_mac.sh` abre la aplicación
- [ ] Interfaz gráfica se ve correctamente
- [ ] OCR funciona (Tesseract detectado)
- [ ] LM Studio conecta (si está instalado)

### Compilación (Opcional)
- [ ] PyInstaller instalado
- [ ] `compilar_mac.sh` ejecuta sin errores
- [ ] `dist/EVARISIS HUV.app` creado
- [ ] App abre correctamente
- [ ] Icono visible en el bundle

---

## 🆘 SOPORTE

Si encuentras problemas:

1. **Verifica los logs** de cada script
2. **Revisa las guías** en README_MAC.md
3. **Ejecuta desde terminal** para ver errores detallados
4. **Verifica permisos** con `chmod +x *.sh`

---

**Versión macOS**: 2.1.6
**Scripts**: 100% probados y funcionales
**Última actualización**: 7 de octubre de 2025

---

> 🍎 **3 Scripts = Instalación + Ejecución + Compilación**
> Todo lo que necesitas para macOS en una carpeta
