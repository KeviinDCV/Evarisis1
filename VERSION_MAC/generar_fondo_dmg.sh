#!/bin/bash

# 🎨 WRAPPER PARA GENERAR FONDO DE DMG
# Ejecuta el script Python que genera el fondo visual
# Versión: 1.0.0

clear
echo ""
echo "================================================================================"
echo "         🎨 GENERADOR DE FONDO PROFESIONAL PARA DMG - HUV"
echo "================================================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Obtener directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    exit 1
fi

print_success "Python 3 encontrado: $(python3 --version)"

# Verificar PIL/Pillow
print_info "Verificando Pillow (PIL)..."
if ! python3 -c "import PIL" 2>/dev/null; then
    print_warning "Pillow no está instalado"
    print_info "Instalando Pillow..."
    pip3 install Pillow

    if [ $? -ne 0 ]; then
        print_error "Error al instalar Pillow"
        exit 1
    fi

    print_success "Pillow instalado correctamente"
else
    print_success "Pillow ya está instalado"
fi

# Ejecutar el script Python
print_info "Generando fondo profesional..."
echo ""

python3 "$SCRIPT_DIR/generar_fondo_dmg.py"

if [ $? -ne 0 ]; then
    print_error "Error al generar el fondo"
    exit 1
fi

# Verificar que se generó la imagen
if [ -f "$SCRIPT_DIR/imagenes/dmg_background.png" ]; then
    echo ""
    echo "================================================================================"
    print_success "🎉 FONDO GENERADO EXITOSAMENTE"
    echo "================================================================================"
    echo ""

    # Mostrar información del archivo
    file_size=$(du -h "$SCRIPT_DIR/imagenes/dmg_background.png" | cut -f1)
    print_info "📦 Archivo generado:"
    echo "   📁 Ubicación: imagenes/dmg_background.png"
    echo "   📏 Tamaño: $file_size"
    echo ""

    # Preguntar si quiere ver el fondo
    read -p "¿Deseas visualizar el fondo generado? (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        open "$SCRIPT_DIR/imagenes/dmg_background.png"
    fi

    echo ""
    print_info "📝 Próximo paso:"
    echo "   Ejecuta: ./crear_dmg_visual.sh"
    echo "   (El DMG usará automáticamente este fondo profesional)"
    echo ""
else
    print_error "No se encontró la imagen generada"
    exit 1
fi
