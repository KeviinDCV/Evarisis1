@echo off
chcp 65001 >nul
color 0D
echo.
echo ================================================================================
echo                    🏥 INICIADOR PYTHON - GESTOR ONCOLOGÍA HUV 🏥
echo                         Activando entorno virtual y ejecutando
echo ================================================================================
echo.

REM Configuración de rutas
set "WORK_DIR=%~dp0"
set "VENV_PATH=%WORK_DIR%venv0"
set "PYTHON_SCRIPT=ui.py"

REM Usuario y configuración
set "USUARIO_NOMBRE=Daniel Restrepo"
set "USUARIO_CARGO=Ingeniero de soluciones"
set "TEMA_APP=cosmo"

cd /d "%WORK_DIR%"

echo [PASO 1/5] Verificando entorno virtual...
if not exist "%VENV_PATH%\" (
    echo ❌ ERROR: No se encontró el entorno virtual en: %VENV_PATH%
    echo.
    echo 💡 SOLUCIÓN: Crea el entorno virtual con:
    echo    python -m venv venv0
    echo    venv0\Scripts\activate
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo ✅ Entorno virtual encontrado: %VENV_PATH%

echo.
echo [PASO 2/5] Verificando Python en entorno virtual...
if not exist "%VENV_PATH%\Scripts\python.exe" (
    echo ❌ ERROR: No se encontró python.exe en el entorno virtual
    echo.
    echo 💡 SOLUCIÓN: Recrea el entorno virtual:
    echo    rmdir /s /q venv0
    echo    python -m venv venv0
    echo.
    pause
    exit /b 1
)
echo ✅ Python encontrado: %VENV_PATH%\Scripts\python.exe

echo.
echo [PASO 3/5] Activando entorno virtual...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    echo.
    echo 💡 SOLUCIÓN: Verifica que el entorno virtual no esté corrupto
    echo.
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado

echo.
echo [PASO 4/5] Verificando archivo principal...
if not exist "%PYTHON_SCRIPT%" (
    echo ❌ ERROR: No se encontró %PYTHON_SCRIPT% en: %WORK_DIR%
    echo.
    echo 💡 SOLUCIÓN: Asegúrate de ejecutar este script desde el directorio del proyecto
    echo.
    pause
    exit /b 1
)
echo ✅ Archivo %PYTHON_SCRIPT% encontrado

echo.
echo [PASO 5/5] Verificando dependencias críticas...
"%VENV_PATH%\Scripts\python.exe" -c "import tkinter, sqlite3, PIL, ttkbootstrap" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚠️ ADVERTENCIA: Algunas dependencias pueden no estar instaladas
    echo 💡 Si la aplicación falla, ejecuta: pip install -r requirements.txt
    echo.
    timeout /t 3 >nul
) else (
    echo ✅ Dependencias críticas encontradas
)

echo.
echo ================================================================================
echo                         🚀 INICIANDO APLICACIÓN
echo ================================================================================
echo.
echo ℹ️ Configuración:
echo   • Usuario: %USUARIO_NOMBRE%
echo   • Cargo: %USUARIO_CARGO%
echo   • Tema: %TEMA_APP%
echo   • Modo: Independiente
echo.
echo 📌 La ventana aparecerá después de cargar la base de datos...
echo 📌 Mantén esta consola abierta para ver logs del sistema
echo.
echo ================================================================================
echo.

REM Configurar variables de entorno para webdriver_manager (evita errores de rutas)
set WDM_LOCAL=1
set WDM_LOG_LEVEL=0
set WDM_PRINT_FIRST_LINE=False
set WDM_SSL_VERIFY=0

REM Configurar PYTHONIOENCODING para capturar errores completos
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM Ejecutar la aplicación en modo independiente (sin rutas hardcodeadas)
echo [DEBUG] Ejecutando: "%VENV_PATH%\Scripts\python.exe" %PYTHON_SCRIPT%
"%VENV_PATH%\Scripts\python.exe" %PYTHON_SCRIPT% --lanzado-por-evarisis --nombre "%USUARIO_NOMBRE%" --cargo "%USUARIO_CARGO%" --tema "%TEMA_APP%" --modo-independiente 2>&1

REM Capturar código de salida
set EXIT_CODE=%ERRORLEVEL%

echo.
echo ================================================================================
if %EXIT_CODE% equ 0 (
    echo                    ✅ Aplicación cerrada correctamente
) else (
    echo                    ⚠️ Aplicación cerrada con errores ^(Código: %EXIT_CODE%^)
    echo.
    echo 💡 Revisa los mensajes anteriores para identificar el problema
)
echo ================================================================================
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul