#!/bin/bash

# 🍎 CREADOR DE ICONO .ICNS PARA MACOS
# Convierte una imagen PNG en un icono .icns compatible con macOS
# Versión: 1.0.0
# Uso: ./crear_icono_mac.sh [ruta_imagen.png] [salida.icns]

clear
echo ""
echo "================================================================================"
echo "            🎨 CREADOR DE ICONO .ICNS PARA MACOS V1.0.0"
echo "                  Generando icono para EVARISIS HUV"
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

# Archivos de entrada/salida
if [ -n "$1" ]; then
    INPUT_PNG="$1"
else
    INPUT_PNG="$PROJECT_DIR/imagenes/icon.png"
fi

if [ -n "$2" ]; then
    OUTPUT_ICNS="$2"
else
    OUTPUT_ICNS="$PROJECT_DIR/imagenes/icon.icns"
fi

echo "📂 Directorio del proyecto: $PROJECT_DIR"
echo "📥 Imagen de entrada: $INPUT_PNG"
echo "📤 Icono de salida: $OUTPUT_ICNS"
echo ""

# ============================================================
# PASO 1: Verificar archivo de entrada
# ============================================================
print_step "[PASO 1/5] Verificando archivo de entrada..."

if [ ! -f "$INPUT_PNG" ]; then
    print_error "No se encontró la imagen: $INPUT_PNG"
    echo ""
    print_info "Uso:"
    echo "   ./crear_icono_mac.sh [imagen.png] [salida.icns]"
    echo ""
    print_info "Ejemplos:"
    echo "   ./crear_icono_mac.sh ../imagenes/icon.png ../imagenes/icon.icns"
    echo "   ./crear_icono_mac.sh logo.png app_icon.icns"
    echo ""
    exit 1
fi

# Verificar que es PNG
file_type=$(file -b "$INPUT_PNG")
if [[ ! "$file_type" =~ PNG ]]; then
    print_warning "El archivo no parece ser PNG: $file_type"
    print_info "Continuando de todos modos..."
fi

print_success "Imagen encontrada"

# ============================================================
# PASO 2: Verificar herramientas necesarias
# ============================================================
print_step "[PASO 2/5] Verificando herramientas de macOS..."

# Verificar sips (viene con macOS)
if ! command -v sips &> /dev/null; then
    print_error "sips no está disponible (requerido en macOS)"
    exit 1
fi
print_success "sips encontrado"

# Verificar iconutil (viene con Xcode Command Line Tools)
if ! command -v iconutil &> /dev/null; then
    print_warning "iconutil no está disponible"
    print_info "Instalando Xcode Command Line Tools..."
    echo "   xcode-select --install"
    xcode-select --install

    print_info "Después de instalar, ejecuta este script nuevamente"
    exit 1
fi
print_success "iconutil encontrado"

# ============================================================
# PASO 3: Crear iconset temporal
# ============================================================
print_step "[PASO 3/5] Generando iconset con múltiples resoluciones..."

# Crear directorio temporal para iconset
ICONSET_DIR=$(mktemp -d)/icon.iconset
mkdir -p "$ICONSET_DIR"

print_info "Iconset temporal: $ICONSET_DIR"

# Generar todas las resoluciones necesarias para macOS
declare -a sizes=(
    "16:16x16"
    "32:16x16@2x"
    "32:32x32"
    "64:32x32@2x"
    "128:128x128"
    "256:128x128@2x"
    "256:256x256"
    "512:256x256@2x"
    "512:512x512"
    "1024:512x512@2x"
)

total_sizes=${#sizes[@]}
current=0

for size_spec in "${sizes[@]}"; do
    current=$((current + 1))

    # Separar tamaño y nombre
    IFS=':' read -r size name <<< "$size_spec"

    print_info "[${current}/${total_sizes}] Generando icon_${name}.png (${size}x${size})..."

    sips -z "$size" "$size" "$INPUT_PNG" --out "$ICONSET_DIR/icon_${name}.png" &> /dev/null

    if [ $? -ne 0 ]; then
        print_error "Error al generar resolución ${size}x${size}"
        rm -rf "$(dirname "$ICONSET_DIR")"
        exit 1
    fi
done

print_success "Todas las resoluciones generadas correctamente"

# ============================================================
# PASO 4: Generar archivo .icns
# ============================================================
print_step "[PASO 4/5] Convirtiendo iconset a .icns..."

iconutil -c icns "$ICONSET_DIR" -o "$OUTPUT_ICNS"

if [ $? -ne 0 ]; then
    print_error "Error al generar archivo .icns"
    rm -rf "$(dirname "$ICONSET_DIR")"
    exit 1
fi

print_success "Archivo .icns generado correctamente"

# ============================================================
# PASO 5: Limpiar archivos temporales
# ============================================================
print_step "[PASO 5/5] Limpiando archivos temporales..."

rm -rf "$(dirname "$ICONSET_DIR")"

print_success "Archivos temporales eliminados"

# ============================================================
# RESUMEN FINAL
# ============================================================
echo ""
echo "================================================================================"
echo "                        🎉 ICONO GENERADO EXITOSAMENTE"
echo "================================================================================"
echo ""

file_size=$(du -h "$OUTPUT_ICNS" | cut -f1)

print_success "Icono .icns creado para macOS"
echo ""
print_info "📦 Información del icono:"
echo "   📥 Entrada: $INPUT_PNG"
echo "   📤 Salida: $OUTPUT_ICNS"
echo "   📏 Tamaño: $file_size"
echo ""
print_info "🔍 Resoluciones incluidas:"
echo "   ✅ 16x16, 32x32, 64x64, 128x128"
echo "   ✅ 256x256, 512x512, 1024x1024"
echo "   ✅ Retina (@2x) para todas las resoluciones"
echo ""
print_info "🚀 Uso del icono:"
echo "   1. Compilar aplicación: ./compilar_mac.sh"
echo "      (usará automáticamente: $OUTPUT_ICNS)"
echo "   2. O especificar manualmente en PyInstaller:"
echo "      --icon=$OUTPUT_ICNS"
echo ""
print_success "¡El icono está listo para usar!"
echo ""

# Preguntar si desea visualizar el icono
read -p "¿Deseas visualizar el icono generado? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    open "$OUTPUT_ICNS"
fi

echo ""
echo "================================================================================"
print_success "🎨 Creación de icono completada"
echo "================================================================================"
echo ""
