@echo off
chcp 65001 >nul
color 0D
echo.
echo ================================================================================
echo                    🏥 INICIADOR PYTHON - GESTOR ONCOLOGÍA HUV 🏥
echo                         Activando entorno virtual y ejecutando
echo ================================================================================
echo.

set "WORK_DIR=%~dp0"
set "VENV_PATH=%WORK_DIR%venv0"
set "PYTHON_SCRIPT=ui.py"

cd /d "%WORK_DIR%"

echo [PASO 1/4] Verificando entorno virtual...
if not exist "%VENV_PATH%\" (
    echo ❌ ERROR: No se encontró el entorno virtual en: %VENV_PATH%
    echo ℹ️ Asegúrate de que existe la carpeta venv0 en el directorio del proyecto
    pause
    exit /b 1
)
echo ✅ Entorno virtual encontrado

echo.
echo [PASO 2/4] Activando entorno virtual...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado

echo.
echo [PASO 3/4] Verificando archivo principal...
if not exist "%PYTHON_SCRIPT%" (
    echo ❌ ERROR: No se encontró %PYTHON_SCRIPT%
    pause
    exit /b 1
)
echo ✅ Archivo %PYTHON_SCRIPT% encontrado

echo.
echo [PASO 4/4] Iniciando Gestor de Oncología HUV...
echo ℹ️ Ejecutando con argumentos de EVARISIS:
echo   --lanzado-por-evarisis --nombre "Daniel Restrepo" --cargo "Ingeniero de soluciones"
echo   --tema "cosmo" --ruta-datos "..."
echo ================================================================================
echo.

REM Ejecutar la aplicación (con consola visible para ver logs)
echo 🚀 Lanzando aplicación...
echo ℹ️ La ventana aparecerá después de cargar la base de datos...
echo.

"%VENV_PATH%\Scripts\python.exe" %PYTHON_SCRIPT% --lanzado-por-evarisis --nombre "Daniel Restrepo" --cargo "Ingeniero de soluciones" --foto "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD\base_de_usuarios\Daniel Restrepo.jpeg" --tema "cosmo" --ruta-fotos "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD\base_de_usuarios" --ruta-datos "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD" --modo-independiente

echo.
echo ================================================================================
echo                         Aplicación cerrada
echo ================================================================================
pause