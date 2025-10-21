#!/bin/bash

# 🍎 INICIADOR PYTHON - GESTOR ONCOLOGÍA HUV (macOS) 🍎
# Activando entorno virtual y ejecutando

echo ""
echo "================================================================================"
echo "                   🏥 INICIADOR PYTHON - GESTOR ONCOLOGÍA HUV 🏥"
echo "                        Activando entorno virtual y ejecutando"
echo "================================================================================"
echo ""

# Obtener directorio donde está el script (VERSION_MAC)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# El directorio de trabajo es el padre (raíz del proyecto)
WORK_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# El entorno virtual se crea en VERSION_MAC pero ejecutamos desde raíz
VENV_PATH="$SCRIPT_DIR/venv0"
PYTHON_SCRIPT="ui.py"

cd "$WORK_DIR"

echo "[PASO 1/4] Verificando entorno virtual..."
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ ERROR: No se encontró el entorno virtual en: $VENV_PATH"
    echo "ℹ️ Asegúrate de que existe la carpeta venv0 en el directorio del proyecto"
    echo "💡 Para crear el entorno virtual ejecuta:"
    echo "   python3 -m venv venv0"
    echo "   source venv0/bin/activate"
    echo "   pip install -r requirements.txt"
    read -p "Presiona Enter para continuar..."
    exit 1
fi
echo "✅ Entorno virtual encontrado"

echo ""
echo "[PASO 2/4] Activando entorno virtual..."
source "$VENV_PATH/bin/activate"
if [ $? -ne 0 ]; then
    echo "❌ ERROR: No se pudo activar el entorno virtual"
    read -p "Presiona Enter para continuar..."
    exit 1
fi
echo "✅ Entorno virtual activado"

echo ""
echo "[PASO 3/4] Verificando archivo principal..."
if [ ! -f "$WORK_DIR/$PYTHON_SCRIPT" ]; then
    echo "❌ ERROR: No se encontró $PYTHON_SCRIPT en $WORK_DIR"
    read -p "Presiona Enter para continuar..."
    exit 1
fi
echo "✅ Archivo $PYTHON_SCRIPT encontrado en directorio raíz"

echo ""
echo "[PASO 4/4] Iniciando Gestor de Oncología HUV..."
echo "ℹ️ Ejecutando con argumentos reales de EVARISIS:"
echo "  --lanzado-por-evarisis --nombre 'Daniel Restrepo' --cargo 'Ingeniero de soluciones'"
echo "  --foto '/Users/usuario/Desktop/DEBERES_HUV/ProyectoHUV1EVARISISDASHBOARD/base_de_usuarios/Daniel Restrepo.jpeg'"
echo "  --tema 'cosmo' --ruta-datos '/Users/usuario/Desktop/DEBERES_HUV/ProyectoHUV1EVARISISDASHBOARD'"
echo "================================================================================"
echo ""

# Ejecutar la aplicación con argumentos macOS desde el directorio raíz
python3 "$WORK_DIR/$PYTHON_SCRIPT" \
    --lanzado-por-evarisis \
    --nombre "Daniel Restrepo" \
    --cargo "Ingeniero de soluciones" \
    --foto "/Users/usuario/Desktop/DEBERES_HUV/ProyectoHUV1EVARISISDASHBOARD/base_de_usuarios/Daniel Restrepo.jpeg" \
    --tema "cosmo" \
    --ruta-fotos "/Users/usuario/Desktop/DEBERES_HUV/ProyectoHUV1EVARISISDASHBOARD/base_de_usuarios"

echo ""
echo "================================================================================"
echo "                             Aplicación finalizada"
echo "================================================================================"
read -p "Presiona Enter para continuar..."