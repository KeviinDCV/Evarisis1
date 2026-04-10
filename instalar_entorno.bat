@echo off
chcp 65001 >nul
color 0B
echo.
echo ================================================================================
echo              🔧 INSTALADOR DE ENTORNO VIRTUAL - GESTOR ONCOLOGÍA HUV 🔧
echo                     Creación e instalación de dependencias
echo ================================================================================
echo.

REM Configuración
set "WORK_DIR=%~dp0"
set "VENV_NAME=venv0"
set "VENV_PATH=%WORK_DIR%%VENV_NAME%"
set "REQUIREMENTS=%WORK_DIR%requirements.txt"
set "PYTHON_MIN_VERSION=3.9"

cd /d "%WORK_DIR%"

echo [INFO] Directorio de trabajo: %WORK_DIR%
echo [INFO] Nombre del entorno virtual: %VENV_NAME%
echo.

REM ============================================================================
REM PASO 1: Verificar que Python está instalado
REM ============================================================================
echo [PASO 1/7] Verificando instalación de Python...
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: Python no está instalado o no está en el PATH
    echo.
    echo 💡 SOLUCIÓN:
    echo    1. Descarga Python desde: https://www.python.org/downloads/
    echo    2. Durante la instalación, marca "Add Python to PATH"
    echo    3. Versión recomendada: Python 3.9 o superior
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado
echo.

REM ============================================================================
REM PASO 2: Verificar que requirements.txt existe
REM ============================================================================
echo [PASO 2/7] Verificando archivo requirements.txt...
if not exist "%REQUIREMENTS%" (
    echo ❌ ERROR: No se encontró requirements.txt en: %REQUIREMENTS%
    echo.
    echo 💡 SOLUCIÓN: Asegúrate de que el archivo requirements.txt existe
    echo.
    pause
    exit /b 1
)
echo ✅ requirements.txt encontrado
echo.

REM ============================================================================
REM PASO 3: Eliminar entorno virtual anterior (si existe)
REM ============================================================================
echo [PASO 3/7] Verificando entorno virtual existente...
if exist "%VENV_PATH%" (
    echo ⚠️ Se encontró un entorno virtual existente en: %VENV_PATH%
    echo.
    choice /C SN /M "¿Deseas eliminarlo y crear uno nuevo? (S=Sí, N=No)"
    if errorlevel 2 (
        echo.
        echo ❌ Instalación cancelada por el usuario
        echo.
        pause
        exit /b 0
    )
    echo.
    echo 🗑️ Eliminando entorno virtual anterior...
    rmdir /s /q "%VENV_PATH%"
    if exist "%VENV_PATH%" (
        echo ❌ ERROR: No se pudo eliminar el entorno virtual
        echo 💡 Cierra cualquier programa que esté usando el entorno e intenta de nuevo
        echo.
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual anterior eliminado
) else (
    echo ℹ️ No se encontró entorno virtual previo
)
echo.

REM ============================================================================
REM PASO 4: Crear nuevo entorno virtual
REM ============================================================================
echo [PASO 4/7] Creando entorno virtual nuevo...
echo ℹ️ Esto puede tomar 1-2 minutos...
python -m venv "%VENV_PATH%"
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: No se pudo crear el entorno virtual
    echo.
    echo 💡 SOLUCIÓN:
    echo    1. Verifica que tienes permisos de escritura en el directorio
    echo    2. Ejecuta: python -m pip install --upgrade pip
    echo    3. Intenta de nuevo
    echo.
    pause
    exit /b 1
)
echo ✅ Entorno virtual creado exitosamente
echo.

REM ============================================================================
REM PASO 5: Activar entorno virtual
REM ============================================================================
echo [PASO 5/7] Activando entorno virtual...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo ✅ Entorno virtual activado
echo.

REM ============================================================================
REM PASO 6: Actualizar pip, setuptools y wheel
REM ============================================================================
echo [PASO 6/7] Actualizando herramientas base (pip, setuptools, wheel)...
echo ℹ️ Esto puede tomar 1-2 minutos...
python -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% neq 0 (
    echo ⚠️ ADVERTENCIA: No se pudieron actualizar las herramientas base
    echo    Continuando con la instalación...
    echo.
)
echo ✅ Herramientas actualizadas
echo.

REM ============================================================================
REM PASO 7: Instalar dependencias desde requirements.txt
REM ============================================================================
echo [PASO 7/7] Instalando dependencias desde requirements.txt...
echo ℹ️ Esto puede tomar 5-10 minutos dependiendo de tu conexión...
echo.
python -m pip install -r "%REQUIREMENTS%"
if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ ERROR: Hubo problemas al instalar algunas dependencias
    echo.
    echo 💡 SOLUCIÓN:
    echo    1. Verifica tu conexión a internet
    echo    2. Intenta ejecutar manualmente: venv0\Scripts\activate ^& pip install -r requirements.txt
    echo    3. Si persiste, revisa los errores específicos arriba
    echo.
    pause
    exit /b 1
)
echo.
echo ✅ Todas las dependencias instaladas correctamente
echo.

REM ============================================================================
REM VERIFICACIÓN FINAL
REM ============================================================================
echo ================================================================================
echo                           🔍 VERIFICACIÓN FINAL
echo ================================================================================
echo.
echo Verificando paquetes críticos instalados...
echo.

python -c "import tkinter; print('✅ tkinter:', tkinter.TkVersion)" 2>nul || echo ❌ tkinter: NO DISPONIBLE
python -c "import ttkbootstrap; print('✅ ttkbootstrap:', ttkbootstrap.__version__)" 2>nul || echo ❌ ttkbootstrap: ERROR
python -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>nul || echo ❌ pandas: ERROR
python -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>nul || echo ❌ numpy: ERROR
python -c "import pytesseract; print('✅ pytesseract:', pytesseract.__version__)" 2>nul || echo ❌ pytesseract: ERROR
python -c "import PIL; print('✅ Pillow:', PIL.__version__)" 2>nul || echo ❌ Pillow: ERROR
python -c "import fitz; print('✅ PyMuPDF:', fitz.__version__)" 2>nul || echo ❌ PyMuPDF: ERROR
python -c "import selenium; print('✅ selenium:', selenium.__version__)" 2>nul || echo ❌ selenium: ERROR
python -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)" 2>nul || echo ❌ openpyxl: ERROR
python -c "import matplotlib; print('✅ matplotlib:', matplotlib.__version__)" 2>nul || echo ❌ matplotlib: ERROR

echo.
echo ================================================================================
echo                          ✅ INSTALACIÓN COMPLETADA
echo ================================================================================
echo.
echo 🎉 El entorno virtual "%VENV_NAME%" está listo para usar
echo.
echo 📌 PRÓXIMOS PASOS:
echo    1. Para activar el entorno manualmente:
echo       %VENV_NAME%\Scripts\activate
echo.
echo    2. Para ejecutar la aplicación:
echo       Haz doble clic en: iniciar_python.bat
echo.
echo    3. Para instalar paquetes adicionales:
echo       %VENV_NAME%\Scripts\pip install nombre_paquete
echo.
echo ================================================================================
echo.
pause
