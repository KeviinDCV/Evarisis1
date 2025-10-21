#!/bin/bash

# 🍎 CREADOR DE DMG PARA DISTRIBUCIÓN MACOS
# Genera un archivo DMG profesional para distribuir EVARISIS HUV
# Versión: 1.0.0
# Uso: ./crear_dmg.sh

clear
echo ""
echo "================================================================================"
echo "            📦 CREADOR DE DMG PARA MACOS V1.0.0"
echo "                 Generando instalador para EVARISIS HUV"
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
    echo -e "${CYAN}📝 $1${NC}"
}

# Obtener directorios
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Leer versión desde version_info.py
VERSION_FILE="$PROJECT_DIR/config/version_info.py"
if [ -f "$VERSION_FILE" ]; then
    APP_VERSION=$(grep "VERSION = " "$VERSION_FILE" | sed 's/VERSION = "\(.*\)"/\1/')
else
    APP_VERSION="2.1.6"
    print_warning "No se encontró version_info.py, usando versión por defecto: $APP_VERSION"
fi

# Configuración
APP_NAME="EVARISIS Cirugía Oncológica"
DMG_NAME="EVARISIS_HUV_v${APP_VERSION}_macOS"
DIST_DIR="$SCRIPT_DIR/dist"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_TEMP_DIR="$SCRIPT_DIR/dmg_temp"
DMG_OUTPUT="$DIST_DIR/${DMG_NAME}.dmg"

echo "📂 Directorio del proyecto: $PROJECT_DIR"
echo "📦 Aplicación: $APP_PATH"
echo "💾 DMG de salida: $DMG_OUTPUT"
echo "🔢 Versión: $APP_VERSION"
echo ""

# ============================================================
# PASO 1: Verificar que existe la aplicación .app
# ============================================================
print_step "[PASO 1/8] Verificando aplicación compilada..."

if [ ! -d "$APP_PATH" ]; then
    print_error "No se encontró la aplicación: $APP_PATH"
    echo ""
    print_info "Primero debes compilar la aplicación:"
    echo "   cd $SCRIPT_DIR"
    echo "   ./compilar_mac_mejorado.sh"
    echo ""
    exit 1
fi

print_success "Aplicación encontrada: $(basename "$APP_PATH")"

# Verificar tamaño de la aplicación
app_size=$(du -sh "$APP_PATH" | cut -f1)
print_info "Tamaño de la aplicación: $app_size"

# ============================================================
# PASO 2: Limpiar archivos previos
# ============================================================
print_step "[PASO 2/8] Limpiando archivos previos..."

# Eliminar DMG anterior si existe
if [ -f "$DMG_OUTPUT" ]; then
    print_info "Eliminando DMG anterior..."
    rm -f "$DMG_OUTPUT"
fi

# Eliminar carpeta temporal si existe
if [ -d "$DMG_TEMP_DIR" ]; then
    print_info "Eliminando carpeta temporal anterior..."
    rm -rf "$DMG_TEMP_DIR"
fi

print_success "Limpieza completada"

# ============================================================
# PASO 3: Crear estructura de carpetas temporales
# ============================================================
print_step "[PASO 3/8] Creando estructura temporal para DMG..."

mkdir -p "$DMG_TEMP_DIR"
print_success "Carpeta temporal creada: $DMG_TEMP_DIR"

# ============================================================
# PASO 4: Copiar aplicación al directorio temporal
# ============================================================
print_step "[PASO 4/8] Copiando aplicación..."

print_info "Esto puede tomar unos minutos dependiendo del tamaño de la aplicación..."
cp -R "$APP_PATH" "$DMG_TEMP_DIR/"

if [ $? -ne 0 ]; then
    print_error "Error al copiar la aplicación"
    rm -rf "$DMG_TEMP_DIR"
    exit 1
fi

print_success "Aplicación copiada al directorio temporal"

# ============================================================
# PASO 5: Crear enlace simbólico a /Applications
# ============================================================
print_step "[PASO 5/8] Creando enlace a /Applications..."

# Crear symlink para facilitar instalación drag-and-drop
ln -s /Applications "$DMG_TEMP_DIR/Applications"

if [ $? -ne 0 ]; then
    print_error "Error al crear enlace simbólico"
    rm -rf "$DMG_TEMP_DIR"
    exit 1
fi

print_success "Enlace simbólico creado"
print_note "Los usuarios podrán arrastrar la app a /Applications fácilmente"

# ============================================================
# PASO 6: Crear archivo README para el usuario final
# ============================================================
print_step "[PASO 6/8] Generando README para el usuario..."

cat > "$DMG_TEMP_DIR/LÉEME - INSTALACIÓN.txt" << EOF
🍎 EVARISIS CIRUGÍA ONCOLÓGICA - macOS v${APP_VERSION}
═══════════════════════════════════════════════════════════════════════════════

Hospital Universitario del Valle - Cali, Colombia
Sistema Inteligente de Gestión de Casos Oncológicos

═══════════════════════════════════════════════════════════════════════════════

📦 INSTALACIÓN:

1. Arrastra "EVARISIS Cirugía Oncológica.app" a la carpeta "Applications"
2. Abre Launchpad o ve a /Applications
3. Haz doble clic en "EVARISIS Cirugía Oncológica"

⚠️  PRIMERA VEZ - SEGURIDAD DE MACOS:

Si macOS bloquea la aplicación:
1. Ve a: Preferencias del Sistema → Seguridad y Privacidad
2. En la pestaña "General", verás un mensaje sobre la aplicación bloqueada
3. Haz clic en "Abrir de todas formas"
4. Confirma abriendo la aplicación nuevamente

O alternativamente:
1. Click derecho sobre la app → "Abrir"
2. Confirma que deseas abrirla

═══════════════════════════════════════════════════════════════════════════════

🔧 REQUISITOS DEL SISTEMA:

✅ macOS 10.15 (Catalina) o superior
✅ 4GB de RAM mínimo (8GB recomendado)
✅ 500MB de espacio en disco

⚠️  DEPENDENCIA CRÍTICA - TESSERACT OCR:

Esta aplicación requiere Tesseract OCR para procesar PDFs de patología.

¿TESSERACT YA ESTÁ INSTALADO?
Abre Terminal y escribe: tesseract --version

Si ves la versión de Tesseract → ✅ Listo para usar
Si dice "command not found" → ⚠️ Necesitas instalarlo

═══════════════════════════════════════════════════════════════════════════════

📥 INSTALAR TESSERACT (OBLIGATORIO):

OPCIÓN 1 - Homebrew (Recomendado):

1. Instala Homebrew (si no lo tienes):
   /bin/bash -c "\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. Instala Tesseract:
   brew install tesseract tesseract-lang

3. Verifica instalación:
   tesseract --version

OPCIÓN 2 - Instalador oficial:

1. Descarga desde: https://github.com/UB-Mannheim/tesseract/wiki
2. Sigue el asistente de instalación
3. Reinicia la aplicación EVARISIS

═══════════════════════════════════════════════════════════════════════════════

🚀 PRIMER USO:

1. Abre la aplicación
2. Ve a: Herramientas → Configuración
3. Verifica que Tesseract esté detectado (luz verde)
4. Importa tu primer PDF de patología
5. El sistema extraerá automáticamente los datos relevantes

═══════════════════════════════════════════════════════════════════════════════

📚 FUNCIONALIDADES PRINCIPALES:

✅ Extracción automática de datos de PDFs de patología
✅ Gestión de base de datos de casos oncológicos
✅ Exportación a Excel/JSON/CSV
✅ Análisis de biomarcadores (HER2, Ki-67, ER, PR, etc.)
✅ Validación cruzada de datos
✅ Calendario de seguimiento de casos
✅ Estadísticas y reportes

═══════════════════════════════════════════════════════════════════════════════

❓ SOPORTE TÉCNICO:

📧 Hospital Universitario del Valle
🏥 Departamento de Cirugía Oncológica
📍 Cali, Colombia

Para reportar problemas o solicitar ayuda, contacta al administrador del sistema.

═══════════════════════════════════════════════════════════════════════════════

🔐 PRIVACIDAD:

Esta aplicación procesa datos médicos sensibles localmente en tu Mac.
NO se envían datos a servidores externos.
Todos los datos permanecen en tu computadora.

═══════════════════════════════════════════════════════════════════════════════

📜 LICENCIA:

Software desarrollado para uso interno del Hospital Universitario del Valle.
Versión: ${APP_VERSION}
Fecha: $(date +"%Y-%m-%d")

═══════════════════════════════════════════════════════════════════════════════

¡Gracias por usar EVARISIS! 🏥
EOF

print_success "README generado para el usuario final"

# ============================================================
# PASO 7: Crear el archivo DMG
# ============================================================
print_step "[PASO 7/8] Generando archivo DMG..."

print_info "Esto puede tomar varios minutos..."

# Calcular tamaño necesario para el DMG (app + 50MB extra)
app_size_mb=$(du -sm "$APP_PATH" | cut -f1)
dmg_size_mb=$((app_size_mb + 50))

print_info "Tamaño del DMG: ${dmg_size_mb}MB"

# Crear DMG temporal sin comprimir
hdiutil create -srcfolder "$DMG_TEMP_DIR" \
    -volname "EVARISIS HUV v${APP_VERSION}" \
    -fs HFS+ \
    -size ${dmg_size_mb}m \
    -format UDRW \
    -ov \
    "${DMG_OUTPUT%.dmg}_temp.dmg" &> /dev/null

if [ $? -ne 0 ]; then
    print_error "Error al crear DMG temporal"
    rm -rf "$DMG_TEMP_DIR"
    exit 1
fi

print_success "DMG temporal creado"

# Montar el DMG temporal
print_info "Montando DMG para configuración..."
device=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_OUTPUT%.dmg}_temp.dmg" | grep "^/dev/" | head -1 | awk '{print $1}')

if [ -z "$device" ]; then
    print_error "Error al montar DMG temporal"
    rm -rf "$DMG_TEMP_DIR"
    rm -f "${DMG_OUTPUT%.dmg}_temp.dmg"
    exit 1
fi

print_success "DMG montado en: $device"

# Configurar apariencia del Finder (opcional)
print_info "Configurando apariencia del DMG..."

# Esperar a que el volumen esté listo
sleep 2

# Obtener el punto de montaje
volume_path="/Volumes/EVARISIS HUV v${APP_VERSION}"

# Configurar posición de ventana e iconos usando AppleScript
osascript &> /dev/null << EOF
tell application "Finder"
    tell disk "EVARISIS HUV v${APP_VERSION}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 450}
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set position of item "EVARISIS Cirugía Oncológica.app" of container window to {150, 150}
        set position of item "Applications" of container window to {450, 150}
        set position of item "LÉEME - INSTALACIÓN.txt" of container window to {300, 300}
        close
        open
        update without registering applications
        delay 2
    end tell
end tell
EOF

print_success "Apariencia configurada"

# Desmontar el DMG temporal
print_info "Desmontando DMG temporal..."
hdiutil detach "$device" &> /dev/null
sleep 2

# Convertir a DMG comprimido y de solo lectura
print_info "Comprimiendo DMG final..."
hdiutil convert "${DMG_OUTPUT%.dmg}_temp.dmg" \
    -format UDZO \
    -imagekey zlib-level=9 \
    -o "$DMG_OUTPUT" &> /dev/null

if [ $? -ne 0 ]; then
    print_error "Error al comprimir DMG final"
    rm -rf "$DMG_TEMP_DIR"
    rm -f "${DMG_OUTPUT%.dmg}_temp.dmg"
    exit 1
fi

print_success "DMG comprimido correctamente"

# Eliminar DMG temporal
rm -f "${DMG_OUTPUT%.dmg}_temp.dmg"

# ============================================================
# PASO 8: Limpiar archivos temporales
# ============================================================
print_step "[PASO 8/8] Limpiando archivos temporales..."

rm -rf "$DMG_TEMP_DIR"

print_success "Archivos temporales eliminados"

# ============================================================
# RESUMEN FINAL
# ============================================================
echo ""
echo "================================================================================"
echo "                        🎉 DMG GENERADO EXITOSAMENTE"
echo "================================================================================"
echo ""

dmg_size=$(du -h "$DMG_OUTPUT" | cut -f1)
dmg_sha256=$(shasum -a 256 "$DMG_OUTPUT" | cut -d' ' -f1)

print_success "Instalador DMG creado para macOS"
echo ""
print_info "📦 Información del DMG:"
echo "   📁 Nombre: $(basename "$DMG_OUTPUT")"
echo "   📏 Tamaño: $dmg_size"
echo "   📍 Ubicación: $DMG_OUTPUT"
echo "   🔢 Versión: $APP_VERSION"
echo "   🔐 SHA-256: ${dmg_sha256:0:16}..."
echo ""
print_info "📋 Contenido del DMG:"
echo "   ✅ EVARISIS Cirugía Oncológica.app"
echo "   ✅ Enlace a /Applications (drag-and-drop)"
echo "   ✅ LÉEME - INSTALACIÓN.txt (guía completa)"
echo ""
print_info "🚀 Cómo compartir este DMG:"
echo "   1. Envía el archivo DMG a Dr. Bayona por correo/USB/nube"
echo "   2. Dr. Bayona hace doble clic en el DMG"
echo "   3. Arrastra la aplicación a /Applications"
echo "   4. Instala Tesseract OCR (ver README incluido)"
echo "   5. ¡Listo para usar!"
echo ""
print_info "⚠️  IMPORTANTE - Primera vez en el Mac de destino:"
echo "   - macOS puede mostrar advertencia de seguridad"
echo "   - Solución: Click derecho → Abrir → Confirmar"
echo "   - O: Preferencias → Seguridad → Abrir de todas formas"
echo ""
print_info "🔧 Requisitos en el Mac de destino:"
echo "   - macOS 10.15 (Catalina) o superior"
echo "   - Tesseract OCR instalado (brew install tesseract)"
echo "   - 4GB RAM mínimo (8GB recomendado)"
echo ""
print_success "¡El DMG está listo para distribuir!"
echo ""

# Preguntar si desea abrir la carpeta de distribución
read -p "¿Deseas abrir la carpeta de distribución? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    open "$DIST_DIR"
fi

echo ""
echo "================================================================================"
print_success "🎁 DMG para Dr. Bayona completado"
echo "================================================================================"
echo ""
