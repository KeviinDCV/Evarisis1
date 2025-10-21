#!/bin/bash

# 🍎 COMPILADOR PARA MAC - GESTOR ONCOLOGÍA HUV 🍎
# Compila la aplicación Python en un ejecutable .app para macOS
# Versión: 2.1.6

clear
echo ""
echo "================================================================================"
echo "            🍎 COMPILADOR GESTOR ONCOLOGÍA HUV - macOS V2.1.6 🍎"
echo "              Generando aplicación ejecutable para macOS"
echo "================================================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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
# PASO 1: Verificar entorno virtual
# ============================================================
print_step "[PASO 1/10] Verificando entorno virtual..."
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
print_step "[PASO 2/10] Activando entorno virtual..."
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    print_error "Error al activar el entorno virtual"
    exit 1
fi
print_success "Entorno virtual activado"

# ============================================================
# PASO 3: Verificar/Instalar PyInstaller
# ============================================================
print_step "[PASO 3/10] Verificando PyInstaller..."
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
print_step "[PASO 4/10] Verificando archivo principal ui.py..."
cd "$PROJECT_DIR"
if [ ! -f "ui.py" ]; then
    print_error "No se encontró ui.py en el directorio del proyecto"
    exit 1
fi
print_success "ui.py encontrado"

# ============================================================
# PASO 5: Limpiar compilaciones anteriores
# ============================================================
print_step "[PASO 5/10] Limpiando compilaciones anteriores..."
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
# PASO 6: Detectar arquitectura
# ============================================================
print_step "[PASO 6/10] Detectando arquitectura del sistema..."
ARCH=$(uname -m)
if [[ "$ARCH" == "arm64" ]]; then
    print_success "Arquitectura: Apple Silicon (M1/M2/M3)"
    ARCH_TYPE="Apple Silicon"
else
    print_success "Arquitectura: Intel"
    ARCH_TYPE="Intel"
fi

# ============================================================
# PASO 7: Preparar recursos adicionales
# ============================================================
print_step "[PASO 7/10] Preparando recursos adicionales..."

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

if [ -d "imagenes" ]; then
    DATAS="$DATAS --add-data imagenes:imagenes"
    print_info "Incluyendo: imagenes/"
fi

# Icono de la aplicación (si existe)
ICON_PATH=""
if [ -f "imagenes/icon.icns" ]; then
    ICON_PATH="--icon=imagenes/icon.icns"
    print_info "Icono encontrado: imagenes/icon.icns"
elif [ -f "imagenes/icon.png" ]; then
    print_warning "Se encontró icon.png, pero se necesita .icns para Mac"
    print_info "Puedes convertirlo con: sips -s format icns imagenes/icon.png --out imagenes/icon.icns"
fi

print_success "Recursos preparados"

# ============================================================
# PASO 8: Compilar aplicación
# ============================================================
print_step "[PASO 8/10] Compilando aplicación..."
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
# PASO 9: Verificar resultado
# ============================================================
print_step "[PASO 9/10] Verificando archivo generado..."

if [ -f "$DIST_DIR/EVARISIS HUV" ]; then
    FILE_SIZE=$(du -h "$DIST_DIR/EVARISIS HUV" | cut -f1)
    print_success "Ejecutable generado: EVARISIS HUV"
    print_info "Tamaño: $FILE_SIZE"
    print_info "Ubicación: $DIST_DIR/EVARISIS HUV"
else
    print_error "No se encontró el archivo ejecutable"
    exit 1
fi

# ============================================================
# PASO 10: Crear paquete .app (bundle)
# ============================================================
print_step "[PASO 10/10] Creando paquete .app..."

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

# Crear Info.plist
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
    <key>LSMinimumSystemVersion</key>
    <string>10.14</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSApplicationCategoryType</key>
    <string>public.app-category.healthcare-fitness</string>
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
# RESUMEN FINAL
# ============================================================
echo ""
echo "================================================================================"
echo "                        🎉 COMPILACIÓN EXITOSA 🎉"
echo "================================================================================"
echo ""
print_success "Aplicación compilada para macOS ($ARCH_TYPE)"
echo ""
print_info "📦 Archivos generados:"
echo "   📁 Aplicación: $APP_PATH"
echo "   📏 Tamaño: $(du -sh "$APP_PATH" | cut -f1)"
echo ""
print_info "🚀 Para ejecutar la aplicación:"
echo "   1. Navega a: $DIST_DIR"
echo "   2. Doble clic en: EVARISIS HUV.app"
echo ""
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
echo "   Puedes copiar EVARISIS HUV.app a /Applications"
echo "   O distribuirlo a otros Macs con la misma arquitectura"
echo ""
print_info "🔧 Troubleshooting:"
echo "   Si la app no abre:"
echo "   - Verifica permisos: chmod -R 755 \"$APP_PATH\""
echo "   - Ejecuta desde terminal para ver errores"
echo "   - Asegúrate de que Tesseract esté instalado en el Mac de destino"
echo ""
echo "================================================================================"
print_success "🍎 Compilación para macOS completada"
print_info "Versión: 2.1.6 | Arquitectura: $ARCH_TYPE"
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
print_success "¡Gracias por usar el compilador para macOS!"
echo ""
