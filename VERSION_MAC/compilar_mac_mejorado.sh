#!/bin/bash

# 🍎 COMPILADOR MEJORADO PARA MAC - GESTOR ONCOLOGÍA HUV 🍎
# Compila la aplicación Python en un ejecutable .app para macOS
# CON DETECCIÓN AUTOMÁTICA DE DEPENDENCIAS Y WARNINGS
# Versión: 3.0.0 (MEJORADA)

clear
echo ""
echo "================================================================================"
echo "       🍎 COMPILADOR MEJORADO GESTOR ONCOLOGÍA HUV - macOS V3.0.0 🍎"
echo "           Generando aplicación ejecutable para macOS (MEJORADO)"
echo "================================================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funciones de impresión
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_step() {
    echo -e "${PURPLE}▶️  $1${NC}"
}

print_note() {
    echo -e "${CYAN}💡 $1${NC}"
}

# Bandera de warnings
WARNINGS=0
HAS_TESSERACT=false

# Obtener directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_PATH="$SCRIPT_DIR/venv0"
DIST_DIR="$PROJECT_DIR/dist"
BUILD_DIR="$PROJECT_DIR/build"

echo "📂 Directorio del proyecto: $PROJECT_DIR"
echo "🐍 Entorno virtual: $VENV_PATH"
echo ""

# ============================================================
# PASO 0: Verificar dependencias EXTERNAS (NUEVO)
# ============================================================
print_step "[PASO 0/12] Verificando dependencias externas..."

# Verificar Tesseract OCR
print_info "Verificando Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version 2>&1 | head -n1)
    print_success "Tesseract encontrado: $TESSERACT_VERSION"
    HAS_TESSERACT=true

    # Verificar idioma español
    if tesseract --list-langs 2>&1 | grep -q "spa"; then
        print_success "Idioma español disponible"
    else
        print_warning "Idioma español NO disponible"
        print_note "Instala con: brew install tesseract-lang"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_warning "Tesseract OCR NO está instalado"
    print_note "La aplicación compilada NECESITARÁ Tesseract en el Mac de destino"
    print_note "Instálalo con: brew install tesseract tesseract-lang"
    echo ""
    print_note "El usuario final DEBERÁ instalar Tesseract para usar OCR"
    WARNINGS=$((WARNINGS + 1))
    HAS_TESSERACT=false

    # Preguntar si continuar
    read -p "¿Continuar compilación de todos modos? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        print_info "Compilación cancelada"
        exit 0
    fi
fi

echo ""

# ============================================================
# PASO 1: Verificar entorno virtual
# ============================================================
print_step "[PASO 1/12] Verificando entorno virtual..."
if [ ! -d "$VENV_PATH" ]; then
    print_error "No se encontró el entorno virtual en: $VENV_PATH"
    echo ""
    print_info "Ejecuta primero el instalador:"
    echo "   chmod +x instalar_entorno_mac.sh"
    echo "   ./instalar_entorno_mac.sh"
    echo ""
    exit 1
fi
print_success "Entorno virtual encontrado"

# ============================================================
# PASO 2: Activar entorno virtual
# ============================================================
print_step "[PASO 2/12] Activando entorno virtual..."
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    print_error "Error al activar el entorno virtual"
    exit 1
fi
print_success "Entorno virtual activado"

# ============================================================
# PASO 3: Verificar/Instalar PyInstaller
# ============================================================
print_step "[PASO 3/12] Verificando PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    print_info "PyInstaller no está instalado. Instalando..."
    pip install pyinstaller
    if [ $? -ne 0 ]; then
        print_error "Error al instalar PyInstaller"
        exit 1
    fi
    print_success "PyInstaller instalado correctamente"
else
    PYINSTALLER_VERSION=$(python -c "import PyInstaller; print(PyInstaller.__version__)")
    print_success "PyInstaller encontrado: v$PYINSTALLER_VERSION"
fi

# ============================================================
# PASO 4: Verificar archivo principal
# ============================================================
print_step "[PASO 4/12] Verificando archivo principal ui.py..."
cd "$PROJECT_DIR"
if [ ! -f "ui.py" ]; then
    print_error "No se encontró ui.py en el directorio del proyecto"
    exit 1
fi
print_success "ui.py encontrado"

# ============================================================
# PASO 5: Verificar/Generar icono (NUEVO)
# ============================================================
print_step "[PASO 5/12] Verificando icono de la aplicación..."

ICON_PATH=""
if [ -f "imagenes/icon.icns" ]; then
    ICON_PATH="--icon=imagenes/icon.icns"
    print_success "Icono .icns encontrado: imagenes/icon.icns"
elif [ -f "imagenes/icon.png" ]; then
    print_warning "Solo se encontró icon.png, generando icon.icns..."

    # Ejecutar script de creación de icono
    if [ -f "$SCRIPT_DIR/crear_icono_mac.sh" ]; then
        chmod +x "$SCRIPT_DIR/crear_icono_mac.sh"
        "$SCRIPT_DIR/crear_icono_mac.sh" "imagenes/icon.png" "imagenes/icon.icns"

        if [ -f "imagenes/icon.icns" ]; then
            ICON_PATH="--icon=imagenes/icon.icns"
            print_success "Icono .icns generado correctamente"
        else
            print_warning "No se pudo generar icon.icns automáticamente"
            WARNINGS=$((WARNINGS + 1))
        fi
    else
        print_warning "No se encontró crear_icono_mac.sh"
        print_note "Puedes convertir manualmente con:"
        echo "   ./crear_icono_mac.sh imagenes/icon.png imagenes/icon.icns"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    print_warning "No se encontró ningún icono (icon.png o icon.icns)"
    print_note "La aplicación usará el icono por defecto de Python"
    WARNINGS=$((WARNINGS + 1))
fi

# ============================================================
# PASO 6: Limpiar compilaciones anteriores
# ============================================================
print_step "[PASO 6/12] Limpiando compilaciones anteriores..."
if [ -d "$DIST_DIR" ]; then
    print_info "Eliminando directorio dist/..."
    rm -rf "$DIST_DIR"
fi
if [ -d "$BUILD_DIR" ]; then
    print_info "Eliminando directorio build/..."
    rm -rf "$BUILD_DIR"
fi
if [ -f "ui.spec" ]; then
    print_info "Eliminando ui.spec..."
    rm -f "ui.spec"
fi
print_success "Directorios de compilación limpiados"

# ============================================================
# PASO 7: Detectar arquitectura
# ============================================================
print_step "[PASO 7/12] Detectando arquitectura del sistema..."
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_success "Arquitectura: Apple Silicon (M1/M2/M3/M4)"
    ARCH_TYPE="Apple Silicon"
else
    print_success "Arquitectura: Intel"
    ARCH_TYPE="Intel"
fi

# ============================================================
# PASO 8: Verificar dependencias Python (NUEVO)
# ============================================================
print_step "[PASO 8/12] Verificando dependencias Python críticas..."

declare -a required_packages=(
    "ttkbootstrap"
    "matplotlib"
    "PIL"
    "pytesseract"
    "openpyxl"
    "pandas"
    "numpy"
)

MISSING_PACKAGES=0

for package in "${required_packages[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        print_info "✓ $package"
    else
        print_warning "✗ $package (NO INSTALADO)"
        MISSING_PACKAGES=$((MISSING_PACKAGES + 1))
    fi
done

if [ $MISSING_PACKAGES -gt 0 ]; then
    print_warning "$MISSING_PACKAGES paquete(s) faltante(s)"
    print_note "Instala con: pip install -r requirements.txt"
    WARNINGS=$((WARNINGS + 1))

    read -p "¿Continuar de todos modos? (s/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        print_info "Compilación cancelada"
        exit 0
    fi
else
    print_success "Todas las dependencias están instaladas"
fi

# ============================================================
# PASO 9: Preparar recursos adicionales
# ============================================================
print_step "[PASO 9/12] Preparando recursos adicionales..."

# Crear lista de archivos de datos a incluir
DATAS=""

# Incluir carpetas necesarias
if [ -d "config" ]; then
    DATAS="$DATAS --add-data config:config"
    print_info "Incluyendo: config/"
fi

if [ -d "core" ]; then
    DATAS="$DATAS --add-data core:core"
    print_info "Incluyendo: core/"
fi

if [ -d "ui_helpers" ]; then
    DATAS="$DATAS --add-data ui_helpers:ui_helpers"
    print_info "Incluyendo: ui_helpers/"
fi

if [ -d "imagenes" ]; then
    DATAS="$DATAS --add-data imagenes:imagenes"
    print_info "Incluyendo: imagenes/"
fi

print_success "Recursos preparados"

# ============================================================
# PASO 10: Compilar aplicación
# ============================================================
print_step "[PASO 10/12] Compilando aplicación..."
echo ""
print_info "Esto puede tardar varios minutos. Por favor espera..."
echo ""

# Comando PyInstaller
pyinstaller --name "EVARISIS HUV" \
    --onefile \
    --windowed \
    --noconfirm \
    $ICON_PATH \
    $DATAS \
    --hidden-import=ttkbootstrap \
    --hidden-import=matplotlib \
    --hidden-import=seaborn \
    --hidden-import=PIL \
    --hidden-import=pytesseract \
    --hidden-import=selenium \
    --hidden-import=fitz \
    --hidden-import=openpyxl \
    --hidden-import=pandas \
    --hidden-import=numpy \
    --collect-all ttkbootstrap \
    --osx-bundle-identifier "com.huv.evarisis" \
    ui.py

if [ $? -ne 0 ]; then
    print_error "Error durante la compilación"
    echo ""
    print_info "Posibles soluciones:"
    echo "   1. Verifica que todas las dependencias estén instaladas"
    echo "   2. Revisa los logs de error arriba"
    echo "   3. Intenta reinstalar PyInstaller: pip install --upgrade pyinstaller"
    exit 1
fi

print_success "Compilación completada exitosamente"

# ============================================================
# PASO 11: Verificar resultado
# ============================================================
print_step "[PASO 11/12] Verificando archivo generado..."

if [ -f "$DIST_DIR/EVARISIS HUV" ]; then
    FILE_SIZE=$(du -h "$DIST_DIR/EVARISIS HUV" | cut -f1)
    print_success "Ejecutable generado: EVARISIS HUV"
    print_info "Tamaño: $FILE_SIZE"
else
    print_error "No se encontró el archivo ejecutable"
    exit 1
fi

# ============================================================
# PASO 12: Crear paquete .app (bundle)
# ============================================================
print_step "[PASO 12/12] Creando paquete .app..."

APP_NAME="EVARISIS HUV.app"
APP_PATH="$DIST_DIR/$APP_NAME"

if [ -d "$APP_PATH" ]; then
    print_info "Paquete .app ya existe, limpiando..."
    rm -rf "$APP_PATH"
fi

# Crear estructura .app
mkdir -p "$APP_PATH/Contents/MacOS"
mkdir -p "$APP_PATH/Contents/Resources"

# Mover ejecutable
mv "$DIST_DIR/EVARISIS HUV" "$APP_PATH/Contents/MacOS/"

# Crear Info.plist (MEJORADO con más metadata)
cat > "$APP_PATH/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>EVARISIS HUV</string>
    <key>CFBundleDisplayName</key>
    <string>EVARISIS Cirugía Oncológica</string>
    <key>CFBundleIdentifier</key>
    <string>com.huv.evarisis</string>
    <key>CFBundleVersion</key>
    <string>2.1.6</string>
    <key>CFBundleShortVersionString</key>
    <string>2.1.6</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>EVARISIS HUV</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.healthcare-fitness</string>
    <key>NSHumanReadableCopyright</key>
    <string>© 2025 Hospital Universitario del Valle</string>
    <key>CFBundleDocumentTypes</key>
    <array>
        <dict>
            <key>CFBundleTypeName</key>
            <string>PDF Document</string>
            <key>CFBundleTypeRole</key>
            <string>Viewer</string>
            <key>LSItemContentTypes</key>
            <array>
                <string>com.adobe.pdf</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
EOF

# Copiar icono si existe
if [ -f "imagenes/icon.icns" ]; then
    cp "imagenes/icon.icns" "$APP_PATH/Contents/Resources/app.icns"
    print_info "Icono copiado al bundle"
fi

# Dar permisos de ejecución
chmod +x "$APP_PATH/Contents/MacOS/EVARISIS HUV"

print_success "Paquete .app creado correctamente"

# ============================================================
# CREAR README PARA EL USUARIO FINAL (NUEVO)
# ============================================================
print_info "Generando README para usuario final..."

cat > "$DIST_DIR/LÉEME - IMPORTANTE.txt" << EOF
🍎 EVARISIS CIRUGÍA ONCOLÓGICA - macOS v2.1.6

INSTALACIÓN:
1. Arrastra "EVARISIS HUV.app" a tu carpeta /Applications
2. Abre "EVARISIS HUV" desde Applications

⚠️  REQUISITO IMPORTANTE:
Esta aplicación requiere Tesseract OCR para procesar PDFs.

¿NO TIENES TESSERACT INSTALADO?
Opción A (Recomendada - Homebrew):
  1. Instala Homebrew: https://brew.sh
  2. Ejecuta en Terminal:
     brew install tesseract tesseract-lang

Opción B (Manual):
  Descarga desde: https://github.com/tesseract-ocr/tesseract

PRIMERA EJECUCIÓN:
macOS podría mostrar un warning de seguridad.
Solución:
  - Click derecho en "EVARISIS HUV.app" → Abrir
  - O: Sistema > Seguridad > "Abrir de todos modos"

SOPORTE:
Hospital Universitario del Valle
Dr. Bayona - Cirugía Oncológica

Versión: 2.1.6
Arquitectura: $ARCH_TYPE
Compilado: $(date +"%Y-%m-%d %H:%M:%S")
EOF

print_success "README creado: $DIST_DIR/LÉEME - IMPORTANTE.txt"

# ============================================================
# RESUMEN FINAL
# ============================================================
echo ""
echo "================================================================================"
echo "                        🎉 COMPILACIÓN EXITOSA 🎉"
echo "================================================================================"
echo ""

if [ $WARNINGS -gt 0 ]; then
    print_warning "⚠️  $WARNINGS warning(s) durante la compilación"
    echo ""
fi

print_success "Aplicación compilada para macOS ($ARCH_TYPE)"
echo ""

print_info "📦 Archivos generados:"
echo "   📁 Aplicación: $APP_PATH"
echo "   📏 Tamaño: $(du -sh "$APP_PATH" | cut -f1)"
echo "   📄 README: $DIST_DIR/LÉEME - IMPORTANTE.txt"
echo ""

print_info "🚀 Para ejecutar la aplicación:"
echo "   1. Navega a: $DIST_DIR"
echo "   2. Doble clic en: EVARISIS HUV.app"
echo ""

if [ "$HAS_TESSERACT" = false ]; then
    echo "┌─────────────────────────────────────────────────────────────────────┐"
    print_warning "│  ⚠️  IMPORTANTE: Tesseract NO está instalado en este Mac          │"
    print_warning "│                                                                    │"
    print_warning "│  La aplicación compilada FUNCIONARÁ, pero el usuario final        │"
    print_warning "│  NECESITARÁ instalar Tesseract para usar el OCR.                  │"
    print_warning "│                                                                    │"
    print_note "│  💡 Incluye estas instrucciones al distribuir:                     │"
    echo "│     brew install tesseract tesseract-lang                           │"
    echo "└─────────────────────────────────────────────────────────────────────┘"
    echo ""
fi

print_warning "⚠️  Nota de Seguridad (macOS):"
echo "   La primera vez que ejecutes la app, macOS podría bloquearla."
echo "   Solución:"
echo "   1. Sistema > Seguridad y Privacidad"
echo "   2. Clic en 'Abrir de todos modos'"
echo ""
echo "   O desde terminal:"
echo "   xattr -cr \"$APP_PATH\""
echo ""

print_info "📋 Distribución:"
echo "   1. Copia EVARISIS HUV.app a /Applications del Mac de destino"
echo "   2. Incluye el archivo 'LÉEME - IMPORTANTE.txt'"
echo "   3. El usuario deberá instalar Tesseract (ver README)"
echo ""

print_info "🎁 Siguiente paso (OPCIONAL):"
echo "   Genera un DMG para distribución fácil:"
echo "   ./crear_dmg.sh"
echo ""

echo "================================================================================"
print_success "🍎 Compilación mejorada para macOS completada"
print_info "Versión: 3.0.0 | Arquitectura: $ARCH_TYPE | Warnings: $WARNINGS"
echo "================================================================================"
echo ""

# Preguntar si desea abrir la carpeta
read -p "¿Deseas abrir la carpeta dist/ en Finder? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    open "$DIST_DIR"
fi

# Preguntar si desea ejecutar la app
echo ""
read -p "¿Deseas ejecutar la aplicación ahora? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    print_info "🚀 Abriendo EVARISIS HUV..."
    open "$APP_PATH"
fi

echo ""
print_success "¡Gracias por usar el compilador mejorado para macOS!"
echo ""
