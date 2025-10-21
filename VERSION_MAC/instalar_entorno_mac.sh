#!/bin/bash

# 🍎 INSTALADOR AUTOMÁTICO - GESTOR ONCOLOGÍA HUV (macOS) 🍎
# Script de instalación completa del entorno virtual y dependencias

clear
echo ""
echo "================================================================================"
echo "                   🏥 INSTALADOR GESTOR ONCOLOGÍA HUV (macOS) 🏥"
echo "                      Configuración automática del entorno"
echo "================================================================================"
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir con colores
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

# Obtener directorio donde está el script (VERSION_MAC)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# El directorio del proyecto es el padre
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
VENV_NAME="venv0"
VENV_PATH="$SCRIPT_DIR/$VENV_NAME"
REQUIREMENTS_FILE="$PROJECT_DIR/requirements.txt"

echo "📂 Directorio del script: $SCRIPT_DIR"
echo "📂 Directorio del proyecto: $PROJECT_DIR"
echo "🐍 Entorno virtual: $VENV_PATH"
echo ""

# PASO 1: Verificar Python 3
print_info "[PASO 1/8] Verificando instalación de Python 3..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    echo ""
    echo "💡 Para instalar Python 3 en macOS:"
    echo "   Opción 1 (Homebrew): brew install python3"
    echo "   Opción 2 (Oficial): Descarga desde https://www.python.org/downloads/"
    echo ""
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Python encontrado: $PYTHON_VERSION"

# PASO 2: Verificar pip
print_info "[PASO 2/8] Verificando pip..."
if ! python3 -m pip --version &> /dev/null; then
    print_error "pip no está disponible"
    echo ""
    echo "💡 Para instalar pip:"
    echo "   python3 -m ensurepip --upgrade"
    echo ""
    exit 1
fi

PIP_VERSION=$(python3 -m pip --version)
print_success "pip encontrado: $PIP_VERSION"

# PASO 3: Verificar requirements.txt
print_info "[PASO 3/8] Verificando archivo de dependencias..."
if [ ! -f "$REQUIREMENTS_FILE" ]; then
    print_error "No se encontró requirements.txt en: $REQUIREMENTS_FILE"
    exit 1
fi
print_success "requirements.txt encontrado"

# PASO 4: Limpiar entorno virtual anterior (si existe)
if [ -d "$VENV_PATH" ]; then
    print_warning "[PASO 4/8] Entorno virtual existente encontrado. ¿Deseas eliminarlo y crear uno nuevo?"
    echo "   Ubicación: $VENV_PATH"
    read -p "   Eliminar entorno existente? (s/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[SsYy]$ ]]; then
        print_info "Eliminando entorno virtual anterior..."
        rm -rf "$VENV_PATH"
        print_success "Entorno anterior eliminado"
    else
        print_info "Manteniendo entorno virtual existente"
    fi
else
    print_info "[PASO 4/8] No se encontró entorno virtual anterior"
fi

# PASO 5: Crear entorno virtual
if [ ! -d "$VENV_PATH" ]; then
    print_info "[PASO 5/8] Creando entorno virtual..."
    cd "$WORK_DIR"
    python3 -m venv "$VENV_NAME"
    if [ $? -ne 0 ]; then
        print_error "Error al crear el entorno virtual"
        exit 1
    fi
    print_success "Entorno virtual creado: $VENV_NAME"
else
    print_info "[PASO 5/8] Usando entorno virtual existente"
fi

# PASO 6: Activar entorno virtual
print_info "[PASO 6/8] Activando entorno virtual..."
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    print_error "Error al activar el entorno virtual"
    exit 1
fi
print_success "Entorno virtual activado"

# Verificar que estamos en el entorno virtual
VIRTUAL_ENV_PYTHON=$(which python)
print_info "Python activo: $VIRTUAL_ENV_PYTHON"

# PASO 7: Actualizar pip, setuptools y wheel
print_info "[PASO 7/8] Actualizando herramientas base (pip, setuptools, wheel)..."
python -m pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    print_warning "Error al actualizar herramientas base, continuando..."
fi

# PASO 8: Instalar dependencias
print_info "[PASO 8/8] Instalando dependencias desde requirements.txt..."
echo ""
echo "📦 Instalando paquetes principales:"

# Instalar dependencias una por una para mejor control
FAILED_PACKAGES=()

# Lista de paquetes críticos
CRITICAL_PACKAGES=(
    "numpy>=1.24.0"
    "pandas>=2.0.0"
    "ttkbootstrap>=1.10.1"
    "matplotlib>=3.8.0"
    "seaborn>=0.13.0"
    "PyMuPDF>=1.23.0"
    "pytesseract>=0.3.10"
    "pillow>=10.0.0"
    "selenium>=4.15.0"
    "webdriver-manager>=4.0.0"
    "openpyxl>=3.1.0"
    "python-dateutil>=2.8.0"
    "psutil>=5.9.0"
    "Babel>=2.12.0"
    "holidays>=0.34"
)

# Instalar paquetes críticos individualmente
for package in "${CRITICAL_PACKAGES[@]}"; do
    package_name=$(echo $package | cut -d'>' -f1 | cut -d'=' -f1)
    echo "   📦 Instalando $package_name..."
    pip install "$package" --no-cache-dir
    if [ $? -ne 0 ]; then
        FAILED_PACKAGES+=("$package_name")
        print_warning "Error instalando $package_name"
    fi
done

# Instalar el resto desde requirements.txt
print_info "Instalando dependencias restantes..."
pip install -r "$REQUIREMENTS_FILE" --no-cache-dir

echo ""
echo "================================================================================"
echo "                           🎉 INSTALACIÓN COMPLETADA 🎉"
echo "================================================================================"
echo ""

# Verificar instalaciones críticas
print_info "🔍 Verificando instalaciones críticas..."
VERIFICATION_FAILED=()

# Lista de módulos para verificar
MODULES_TO_CHECK=(
    "numpy"
    "pandas" 
    "ttkbootstrap"
    "matplotlib"
    "seaborn"
    "fitz"  # PyMuPDF
    "pytesseract"
    "PIL"   # Pillow
    "selenium"
    "openpyxl"
)

for module in "${MODULES_TO_CHECK[@]}"; do
    if python -c "import $module" 2>/dev/null; then
        print_success "$module: OK"
    else
        print_error "$module: FALLO"
        VERIFICATION_FAILED+=("$module")
    fi
done

echo ""

# Mostrar información del entorno
print_info "📊 Información del entorno instalado:"
echo "   🐍 Python: $(python --version)"
echo "   📦 pip: $(pip --version)"
echo "   📂 Entorno virtual: $VENV_PATH"
echo "   📄 Paquetes instalados: $(pip list --format=freeze | wc -l) paquetes"

echo ""

# Mostrar instrucciones de uso
if [ ${#VERIFICATION_FAILED[@]} -eq 0 ]; then
    print_success "✨ ¡Instalación exitosa! Todos los módulos críticos funcionan correctamente."
    echo ""
    echo "🚀 Para ejecutar la aplicación:"
    echo ""
    echo "   # Opción 1: Usar el script de inicio"
    echo "   chmod +x iniciar_python_mac.sh"
    echo "   ./iniciar_python_mac.sh"
    echo ""
    echo "   # Opción 2: Activar manualmente"
    echo "   source $VENV_PATH/bin/activate"
    echo "   python ui.py"
    echo ""
    echo "   # Opción 3: Una línea completa"
    echo "   source $VENV_PATH/bin/activate && python ui.py"
else
    print_warning "⚠️  Instalación completada con algunos problemas:"
    for failed in "${VERIFICATION_FAILED[@]}"; do
        echo "     ❌ $failed"
    done
    echo ""
    echo "💡 Soluciones sugeridas:"
    echo "   1. Reinstalar paquetes problemáticos: pip install --upgrade --force-reinstall <paquete>"
    echo "   2. Verificar versión de Python: python --version"
    echo "   3. Revisar logs de error arriba"
fi

echo ""

# Información adicional para macOS
print_info "📝 Notas importantes para macOS:"
echo "   1. 🔧 Para OCR, instala Tesseract: brew install tesseract"
echo "   2. 🌐 Para automatización web, Chrome se descargará automáticamente"
echo "   3. 📱 Si usas Apple Silicon (M1/M2), algunos paquetes pueden requerir Rosetta 2"
echo "   4. 🔐 macOS puede bloquear la primera ejecución por seguridad"

echo ""
echo "================================================================================"
print_success "🍎 Entorno macOS configurado correctamente"
echo "🎯 ¡Ya puedes ejecutar el Gestor de Oncología HUV!"
echo "================================================================================"
echo ""

# Preguntar si desea ejecutar inmediatamente
read -p "¿Deseas ejecutar la aplicación ahora? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    print_info "🚀 Iniciando Gestor de Oncología HUV..."
    python ui.py
fi