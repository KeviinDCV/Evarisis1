# 🍎 INSTALACIÓN Y CONFIGURACIÓN - GESTOR ONCOLOGÍA HUV (macOS)

## 📖 Descripción
Esta guía te llevará paso a paso para instalar y configurar el Gestor de Oncología HUV en sistemas macOS. El proceso incluye la instalación de Tesseract OCR, configuración del entorno Python y ejecución de la aplicación.

---

## ⚡ INICIO RÁPIDO

Si ya tienes todo instalado:
```bash
cd VERSION_MAC/
./iniciar_python_mac.sh
```

---

## 📋 PRERREQUISITOS

### 🔧 Software necesario:
- **macOS 10.15** o superior
- **Python 3.8+** (se puede instalar con Homebrew)
- **Tesseract OCR** (motor de reconocimiento de texto)
- **Homebrew** (gestor de paquetes para macOS)

---

## 🚀 INSTALACIÓN PASO A PASO

### PASO 1: 🍺 Instalar Homebrew (si no lo tienes)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### PASO 2: 🐍 Instalar Python 3
```bash
brew install python3
```

Verificar instalación:
```bash
python3 --version
# Debe mostrar Python 3.8 o superior
```

### PASO 3: 👁️ Instalar Tesseract OCR
```bash
# Instalar Tesseract con soporte para español
brew install tesseract
brew install tesseract-lang
```

Verificar instalación:
```bash
tesseract --version
# Debe mostrar información de Tesseract
```

**🌍 Configurar idiomas OCR:**
```bash
# Verificar idiomas disponibles
tesseract --list-langs
# Debe incluir 'spa' (español) y 'eng' (inglés)

# Si no aparece español, instalar manualmente:
brew install tesseract-lang
```

### PASO 4: 📁 Navegar al directorio del proyecto
```bash
cd /ruta/a/tu/ProyectoHUV9GESTOR_ONCOLOGIA/VERSION_MAC/
```

### PASO 5: 🔧 Dar permisos de ejecución a los scripts
```bash
chmod +x instalar_entorno_mac.sh
chmod +x iniciar_python_mac.sh
```

### PASO 6: 🏗️ Ejecutar el instalador automático
```bash
./instalar_entorno_mac.sh
```

**El instalador hará automáticamente:**
- ✅ Verificar Python 3
- ✅ Crear entorno virtual `venv0`
- ✅ Activar entorno virtual
- ✅ Actualizar pip
- ✅ Instalar dependencias desde `requirements.txt`
- ✅ Verificar instalación de Tesseract
- ✅ Probar importaciones básicas

---

## 🎯 EJECUCIÓN DE LA APLICACIÓN

### 🚀 Iniciar el programa:
```bash
./iniciar_python_mac.sh
```

**El iniciador hará:**
1. **Verificar entorno virtual** en `VERSION_MAC/venv0/`
2. **Activar entorno virtual**
3. **Verificar archivo principal** `ui.py` en directorio raíz
4. **Ejecutar aplicación** con parámetros EVARISIS

### 🔧 Estructura de directorios:
```
ProyectoHUV9GESTOR_ONCOLOGIA/
├── ui.py                    # ← Archivo principal (directorio raíz)
├── core/                    # ← Módulos principales
├── data/                    # ← Base de datos
└── VERSION_MAC/             # ← Scripts macOS
    ├── venv0/               # ← Entorno virtual (se crea aquí)
    ├── instalar_entorno_mac.sh
    └── iniciar_python_mac.sh
```

---

## 🛠️ CONFIGURACIÓN AVANZADA

### 🎨 Personalizar rutas EVARISIS:
Editar `iniciar_python_mac.sh` en las líneas de argumentos:
```bash
python3 "$WORK_DIR/$PYTHON_SCRIPT" \
    --lanzado-por-evarisis \
    --nombre "TU_NOMBRE" \
    --cargo "TU_CARGO" \
    --foto "/ruta/a/tu/foto.jpeg" \
    --tema "cosmo" \
    --ruta-fotos "/ruta/a/carpeta/fotos"
```

### 🔍 Verificar configuración OCR:
```bash
# Probar Tesseract con imagen de prueba
tesseract --list-langs
echo "Hola mundo" | tesseract stdin stdout -l spa
```

### 📊 Verificar exportaciones:
El sistema exporta a:
```
~/Documents/EVARISIS Gestor Oncologico/Exportaciones Base de datos/
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### ❌ Error: "Permission denied"
```bash
chmod +x *.sh
```

### ❌ Error: "Tesseract not found"
```bash
# Reinstalar Tesseract
brew uninstall tesseract
brew install tesseract tesseract-lang

# Verificar PATH
echo $PATH
which tesseract
```

### ❌ Error: "No module named 'pdf2image'"
```bash
# Activar entorno y reinstalar
source venv0/bin/activate
pip install pdf2image Pillow
```

### ❌ Error: "Qt platform plugin could not be initialized"
```bash
# Instalar dependencias gráficas adicionales
brew install python-tk
pip install --upgrade tkinter
```

### ❌ Error de importación de módulos:
```bash
# Verificar desde directorio raíz del proyecto
cd ..  # Salir de VERSION_MAC
python3 -c "import core.database_manager; print('OK')"
```

---

## 🧪 PROBAR LA INSTALACIÓN

### 1. 🔧 Verificar herramientas (desde directorio raíz):
```bash
cd ..
python3 herramientas_ia/test_herramientas.py
```

### 2. 🗄️ Probar conexión a base de datos:
```bash
python3 herramientas_ia/consulta_base_datos.py
```

### 3. 📄 Probar OCR con PDF:
```bash
python3 herramientas_ia/analizar_pdf_completo.py pdfs_patologia/archivo.pdf
```

---

## 📱 INTEGRACIÓN CON EVARISIS

### 🔗 El programa se ejecuta con parámetros específicos:
- `--lanzado-por-evarisis`: Modo integración
- `--nombre`: Nombre del usuario
- `--cargo`: Cargo del usuario  
- `--foto`: Ruta a foto del usuario
- `--tema`: Tema visual (cosmo, flatly, etc.)
- `--ruta-fotos`: Directorio de fotos de usuarios

### 🎯 Ubicación esperada del proyecto:
```
/Users/usuario/Desktop/DEBERES_HUV/ProyectoHUV9GESTOR_ONCOLOGIA/
```

Si tu proyecto está en otra ubicación, ajusta las rutas en `iniciar_python_mac.sh`.

---

## 🔄 MANTENIMIENTO

### 🔄 Actualizar dependencias:
```bash
source venv0/bin/activate
pip install --upgrade -r ../requirements.txt
```

### 🧹 Limpiar entorno:
```bash
rm -rf venv0/
./instalar_entorno_mac.sh
```

### 💾 Respaldo de datos:
```bash
cp -r ../data/ ~/Desktop/backup_huv_$(date +%Y%m%d)/
```

---

## 📊 ARCHIVOS IMPORTANTES

### 🔧 Scripts de configuración:
- `instalar_entorno_mac.sh` - Instalador automático completo
- `iniciar_python_mac.sh` - Iniciador de la aplicación
- `../requirements.txt` - Dependencias Python
- `../ui.py` - Archivo principal de la aplicación

### 📁 Directorios de datos:
- `../data/huv_oncologia_NUEVO.db` - Base de datos principal
- `../pdfs_patologia/` - PDFs a procesar
- `~/Documents/EVARISIS Gestor Oncologico/` - Exportaciones

### 🤖 Herramientas de debug:
- `../herramientas_ia/` - Suite completa de herramientas de IA
- `../herramientas_ia/GUIA_TECNICA_COMPLETA.md` - Guía técnica completa

---

## 🆘 SOPORTE

### 🔍 Para diagnosticar problemas:
1. **Ejecutar test suite**: `python3 ../herramientas_ia/test_herramientas.py`
2. **Revisar logs**: Salida de consola durante ejecución
3. **Verificar permisos**: `ls -la *.sh`
4. **Comprobar rutas**: Ajustar paths en scripts si es necesario

### 📧 Información del sistema:
- **Versión**: Ver `../config/version_info.py`
- **Documentación**: `../documentacion/`
- **Changelog**: `../documentacion/CHANGELOG.md`

---

## ✅ CHECKLIST FINAL

Antes de usar el sistema, verifica:

- [ ] **Homebrew instalado** (`brew --version`)
- [ ] **Python 3.8+ instalado** (`python3 --version`)
- [ ] **Tesseract instalado** (`tesseract --version`)
- [ ] **Idioma español disponible** (`tesseract --list-langs | grep spa`)
- [ ] **Permisos de ejecución** (`ls -la *.sh`)
- [ ] **Entorno virtual creado** (`ls -la venv0/`)
- [ ] **Dependencias instaladas** (`source venv0/bin/activate && pip list`)
- [ ] **Aplicación inicia** (`./iniciar_python_mac.sh`)
- [ ] **Base de datos accesible** (test con herramientas_ia)
- [ ] **OCR funcional** (test con PDF de prueba)

---

## 🎉 ¡LISTO PARA USAR!

Una vez completada la instalación, el sistema estará listo para:
- 📄 Procesar PDFs de patología
- 🔍 Extraer datos médicos automáticamente
- 💾 Almacenar en base de datos SQLite
- 📊 Exportar a Excel con formato profesional
- 🖥️ Interfaz gráfica moderna con TTKBootstrap

**¡Disfruta del Gestor de Oncología HUV en macOS!** 🏥✨

---

*📅 Última actualización: 3 de octubre de 2025*
*🍎 Versión específica para macOS - Hospital Universitario del Valle*