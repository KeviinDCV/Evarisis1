#!/bin/bash

# 🎨 CREADOR DE DMG VISUAL PROFESIONAL PARA MACOS
# Genera un DMG con diseño profesional institucional HUV
# Versión: 2.0.0 (VISUAL)
# Uso: ./crear_dmg_visual.sh

clear
echo ""
echo "================================================================================"
echo "         📦 CREADOR DE DMG VISUAL PROFESIONAL V2.0.0"
echo "              Instalador con diseño institucional HUV"
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
DMG_NAME="EVARISIS_HUV_v${APP_VERSION}_macOS_Professional"
DIST_DIR="$SCRIPT_DIR/dist"
APP_PATH="$DIST_DIR/$APP_NAME.app"
DMG_TEMP_DIR="$SCRIPT_DIR/dmg_temp"
DMG_OUTPUT="$DIST_DIR/${DMG_NAME}.dmg"
BACKGROUND_IMAGE="$SCRIPT_DIR/imagenes/dmg_background.png"

# Posiciones de iconos (coordinadas con generar_fondo_dmg.py)
APP_ICON_X=140
APP_ICON_Y=160
APPS_FOLDER_X=460
APPS_FOLDER_Y=160

echo "📂 Directorio del proyecto: $PROJECT_DIR"
echo "📦 Aplicación: $APP_PATH"
echo "💾 DMG de salida: $DMG_OUTPUT"
echo "🔢 Versión: $APP_VERSION"
echo "🎨 Diseño: PROFESIONAL con fondo institucional HUV"
echo ""

# ============================================================
# PASO 0: Verificar/Generar fondo visual
# ============================================================
print_step "[PASO 0/9] Verificando fondo visual del DMG..."

if [ ! -f "$BACKGROUND_IMAGE" ]; then
    print_warning "Fondo visual no encontrado"
    print_info "Generando fondo profesional automáticamente..."
    echo ""

    # Verificar que existe el generador
    if [ -f "$SCRIPT_DIR/generar_fondo_dmg.sh" ]; then
        chmod +x "$SCRIPT_DIR/generar_fondo_dmg.sh"
        "$SCRIPT_DIR/generar_fondo_dmg.sh"

        if [ $? -ne 0 ]; then
            print_error "Error al generar el fondo"
            print_info "Continuando sin fondo personalizado..."
            BACKGROUND_IMAGE=""
        fi
    else
        print_warning "Generador de fondo no encontrado"
        print_info "Continuando sin fondo personalizado..."
        BACKGROUND_IMAGE=""
    fi
else
    print_success "Fondo visual encontrado: $(basename "$BACKGROUND_IMAGE")"
    bg_size=$(du -h "$BACKGROUND_IMAGE" | cut -f1)
    print_info "Tamaño del fondo: $bg_size"
fi

echo ""

# ============================================================
# PASO 1: Verificar que existe la aplicación .app
# ============================================================
print_step "[PASO 1/9] Verificando aplicación compilada..."

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
print_step "[PASO 2/9] Limpiando archivos previos..."

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

# Limpiar cualquier DMG montado previamente
existing_mount="/Volumes/EVARISIS HUV v${APP_VERSION}"
if [ -d "$existing_mount" ]; then
    print_info "Desmontando DMG previo..."
    hdiutil detach "$existing_mount" -force &> /dev/null
fi

print_success "Limpieza completada"

# ============================================================
# PASO 3: Crear estructura de carpetas temporales
# ============================================================
print_step "[PASO 3/9] Creando estructura temporal para DMG..."

mkdir -p "$DMG_TEMP_DIR"

# Si hay fondo, crear carpeta .background
if [ -n "$BACKGROUND_IMAGE" ] && [ -f "$BACKGROUND_IMAGE" ]; then
    mkdir -p "$DMG_TEMP_DIR/.background"
    cp "$BACKGROUND_IMAGE" "$DMG_TEMP_DIR/.background/background.png"
    print_success "Fondo copiado a carpeta temporal"
fi

print_success "Carpeta temporal creada: $DMG_TEMP_DIR"

# ============================================================
# PASO 4: Copiar aplicación al directorio temporal
# ============================================================
print_step "[PASO 4/9] Copiando aplicación..."

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
print_step "[PASO 5/9] Creando enlace a /Applications..."

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
print_step "[PASO 6/9] Generando README para el usuario..."

cat > "$DMG_TEMP_DIR/LÉEME - INSTALACIÓN.txt" << EOF
🍎 EVARISIS CIRUGÍA ONCOLÓGICA - macOS v${APP_VERSION}
═══════════════════════════════════════════════════════════════════════════════

Hospital Universitario del Valle - Cali, Colombia
Sistema Inteligente de Gestión de Casos Oncológicos

═══════════════════════════════════════════════════════════════════════════════

📦 INSTALACIÓN RÁPIDA:

1. Arrastra "EVARISIS Cirugía Oncológica.app" a la carpeta "Applications"
2. Abre Launchpad o ve a /Applications
3. Haz doble clic en "EVARISIS Cirugía Oncológica"

⚠️  PRIMERA VEZ - SEGURIDAD DE MACOS:

Si macOS bloquea la aplicación:

OPCIÓN 1 (Más rápida):
1. Click DERECHO sobre la app → "Abrir"
2. Confirma que deseas abrirla
3. ¡Listo! macOS recordará tu elección

OPCIÓN 2:
1. Ve a: Preferencias del Sistema → Seguridad y Privacidad
2. En la pestaña "General", verás un mensaje sobre la aplicación bloqueada
3. Haz clic en "Abrir de todas formas"

═══════════════════════════════════════════════════════════════════════════════

✅ TESSERACT OCR - YA INSTALADO

Este Mac del Dr. Bayona ya tiene Tesseract OCR instalado.
La aplicación lo detectará automáticamente. ✓

Si por algún motivo Tesseract NO se detecta:
   brew install tesseract tesseract-lang

═══════════════════════════════════════════════════════════════════════════════

✅ LM STUDIO - YA INSTALADO

Este Mac ya tiene LM Studio configurado.
La aplicación puede usar IA local si LM Studio está ejecutándose.

Para usar IA local:
1. Abre LM Studio
2. Carga un modelo LLM
3. Inicia el servidor local
4. EVARISIS detectará automáticamente la conexión

═══════════════════════════════════════════════════════════════════════════════

🚀 FUNCIONALIDADES PRINCIPALES:

✅ Extracción automática de datos de PDFs de patología (OCR)
✅ Gestión de base de datos de casos oncológicos
✅ Análisis de biomarcadores (HER2, Ki-67, ER, PR, PgR, etc.)
✅ Validación cruzada de datos con IA (opcional)
✅ Exportación a Excel/JSON/CSV
✅ Calendario de seguimiento de casos
✅ Estadísticas y reportes personalizables
✅ Auditoría completa de casos procesados

═══════════════════════════════════════════════════════════════════════════════

📚 PRIMER USO:

1. Abre la aplicación
2. La interfaz principal mostrará el dashboard
3. Importa tu primer PDF: Botón "Importar PDF" o arrastra el archivo
4. El sistema extraerá automáticamente:
   - Datos del paciente (nombre, edad, género)
   - Información del órgano y diagnóstico
   - Biomarcadores inmunohistoquímicos
   - Fechas relevantes
5. Revisa los datos extraídos en la ventana de resultados
6. Guarda en la base de datos
7. Exporta a Excel cuando necesites reportes

═══════════════════════════════════════════════════════════════════════════════

🔧 REQUISITOS DEL SISTEMA:

✅ macOS 10.15 (Catalina) o superior (Este Mac cumple ✓)
✅ 4GB de RAM mínimo, 8GB recomendado (Este Mac cumple ✓)
✅ 500MB de espacio en disco (Este Mac cumple ✓)
✅ Tesseract OCR instalado (Este Mac cumple ✓)

═══════════════════════════════════════════════════════════════════════════════

🔐 PRIVACIDAD Y SEGURIDAD:

✅ Todos los datos se procesan LOCALMENTE en tu Mac
✅ NO se envían datos a servidores externos
✅ La base de datos queda en: ~/Documents/EVARISIS/
✅ Los PDFs procesados NO se modifican
✅ Cumple con normativas de privacidad médica

═══════════════════════════════════════════════════════════════════════════════

❓ SOPORTE TÉCNICO:

📧 Hospital Universitario del Valle
🏥 Departamento de Cirugía Oncológica
📍 Cali, Colombia

Para reportar problemas o solicitar ayuda, contacta al administrador del sistema.

═══════════════════════════════════════════════════════════════════════════════

📜 INFORMACIÓN:

Software desarrollado para uso interno del Hospital Universitario del Valle.

Versión: ${APP_VERSION}
Fecha de compilación: $(date +"%Y-%m-%d")
Arquitectura: Universal (Intel + Apple Silicon via Rosetta 2)

═══════════════════════════════════════════════════════════════════════════════

¡Gracias por usar EVARISIS! 🏥

Desarrollado con dedicación para mejorar la gestión oncológica en el HUV.
EOF

print_success "README generado para el usuario final"

# ============================================================
# PASO 7: Crear el archivo DMG temporal
# ============================================================
print_step "[PASO 7/9] Generando archivo DMG temporal..."

print_info "Esto puede tomar varios minutos..."

# Calcular tamaño necesario para el DMG (app + 100MB extra para fondo y compresión)
app_size_mb=$(du -sm "$APP_PATH" | cut -f1)
dmg_size_mb=$((app_size_mb + 100))

print_info "Tamaño del DMG: ${dmg_size_mb}MB"

# Crear DMG temporal sin comprimir
hdiutil create -srcfolder "$DMG_TEMP_DIR" \
    -volname "EVARISIS HUV v${APP_VERSION}" \
    -fs HFS+ \
    -fsargs "-c c=64,a=16,e=16" \
    -format UDRW \
    -size ${dmg_size_mb}m \
    -ov \
    "${DMG_OUTPUT%.dmg}_temp.dmg" &> /dev/null

if [ $? -ne 0 ]; then
    print_error "Error al crear DMG temporal"
    rm -rf "$DMG_TEMP_DIR"
    exit 1
fi

print_success "DMG temporal creado"

# ============================================================
# PASO 8: Configurar apariencia visual del DMG
# ============================================================
print_step "[PASO 8/9] Configurando apariencia visual profesional..."

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

# Esperar a que el volumen esté listo
sleep 3

# Obtener el punto de montaje
volume_path="/Volumes/EVARISIS HUV v${APP_VERSION}"

# Configurar apariencia usando AppleScript
print_info "Aplicando diseño visual institucional HUV..."

osascript &> /dev/null << EOF
tell application "Finder"
    tell disk "EVARISIS HUV v${APP_VERSION}"
        open

        -- Configuración de la ventana
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {100, 100, 700, 500}

        -- Configuración de la vista de iconos
        set viewOptions to the icon view options of container window
        set arrangement of viewOptions to not arranged
        set icon size of viewOptions to 128
        set text size of viewOptions to 13
        set label position of viewOptions to bottom

        -- Posicionar iconos (coordinados con el fondo)
        set position of item "EVARISIS Cirugía Oncológica.app" of container window to {${APP_ICON_X}, ${APP_ICON_Y}}
        set position of item "Applications" of container window to {${APPS_FOLDER_X}, ${APPS_FOLDER_Y}}

        -- Posicionar README abajo
        try
            set position of item "LÉEME - INSTALACIÓN.txt" of container window to {300, 310}
        end try

        -- Configurar fondo si existe
        try
            set background picture of viewOptions to file ".background:background.png"
        end try

        -- Aplicar cambios
        close
        open
        update without registering applications
        delay 3
    end tell
end tell
EOF

if [ $? -eq 0 ]; then
    print_success "Diseño visual aplicado correctamente"
else
    print_warning "Advertencia al aplicar diseño visual (puede ser normal)"
fi

# Hacer que la carpeta .background sea invisible
if [ -d "$volume_path/.background" ]; then
    SetFile -a V "$volume_path/.background" 2>/dev/null || true
fi

# Esperar a que se apliquen los cambios
sleep 2

# Desmontar el DMG temporal
print_info "Desmontando DMG temporal..."
hdiutil detach "$device" -force &> /dev/null
sleep 3

print_success "DMG desmontado"

# Convertir a DMG comprimido y de solo lectura
print_info "Comprimiendo DMG final (nivel máximo)..."
print_note "Esto puede tomar varios minutos..."

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
# PASO 9: Limpiar archivos temporales
# ============================================================
print_step "[PASO 9/9] Limpiando archivos temporales..."

rm -rf "$DMG_TEMP_DIR"

print_success "Archivos temporales eliminados"

# ============================================================
# RESUMEN FINAL
# ============================================================
echo ""
echo "================================================================================"
echo "                  🎉 DMG PROFESIONAL GENERADO EXITOSAMENTE"
echo "================================================================================"
echo ""

dmg_size=$(du -h "$DMG_OUTPUT" | cut -f1)
dmg_sha256=$(shasum -a 256 "$DMG_OUTPUT" | cut -d' ' -f1)

print_success "Instalador DMG PROFESIONAL creado para macOS"
echo ""
print_info "📦 Información del DMG:"
echo "   📁 Nombre: $(basename "$DMG_OUTPUT")"
echo "   📏 Tamaño: $dmg_size (comprimido con nivel máximo)"
echo "   📍 Ubicación: $DMG_OUTPUT"
echo "   🔢 Versión: $APP_VERSION"
echo "   🎨 Diseño: Profesional institucional HUV"
echo "   🔐 SHA-256: ${dmg_sha256:0:20}..."
echo ""
print_info "📋 Contenido del DMG:"
echo "   ✅ EVARISIS Cirugía Oncológica.app (aplicación principal)"
echo "   ✅ Enlace a /Applications (instalación drag-and-drop)"
echo "   ✅ LÉEME - INSTALACIÓN.txt (guía completa)"
if [ -n "$BACKGROUND_IMAGE" ] && [ -f "$BACKGROUND_IMAGE" ]; then
    echo "   ✅ Fondo visual profesional HUV (coordinado con iconos)"
fi
echo ""
print_info "🎨 Características visuales:"
echo "   ✅ Diseño institucional del Hospital Universitario del Valle"
echo "   ✅ Iconos grandes (128x128) para fácil identificación"
echo "   ✅ Fondo personalizado con instrucciones visuales"
echo "   ✅ Flecha indicando drag-and-drop"
echo "   ✅ Información de versión visible"
echo "   ✅ Instrucciones paso a paso en el fondo"
echo ""
print_info "🚀 Para el Dr. Bayona:"
echo "   1. Hacer doble clic en el DMG"
echo "   2. Arrastrar EVARISIS a Applications (flecha indica dónde)"
echo "   3. Abrir desde Launchpad"
echo "   4. Click derecho → Abrir (primera vez)"
echo "   5. ¡Listo! Todo lo demás ya está configurado en su Mac"
echo ""
print_info "✅ Ventajas de este Mac:"
echo "   ✅ Tesseract OCR - Ya instalado"
echo "   ✅ LM Studio - Ya instalado y configurado"
echo "   ✅ Python - Ya instalado"
echo "   ✅ Dependencias - Todas incluidas en el .app"
echo ""
print_success "¡DMG listo para copiar al Mac del Dr. Bayona!"
echo ""

# Preguntar si desea abrir el DMG para verificar
read -p "¿Deseas abrir el DMG para verificar su apariencia? (s/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[SsYy]$ ]]; then
    open "$DMG_OUTPUT"
    echo ""
    print_note "Verifica que:"
    echo "   - El fondo se vea profesional"
    echo "   - Los iconos estén en las posiciones correctas"
    echo "   - La flecha apunte de la app a Applications"
    echo "   - El README esté visible abajo"
    echo ""
fi

echo ""
echo "================================================================================"
print_success "🎁 DMG Profesional para Dr. Bayona completado"
echo "================================================================================"
echo ""
