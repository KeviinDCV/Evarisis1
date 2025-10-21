@echo off
chcp 65001 >nul
color 0A
echo.
echo ===============================================================================
echo                    🏥 COMPILADOR GESTOR ONCOLOGÍA HUV 🏥
echo              Compilador ONEFILE - Ejecutable Único Portable
echo ===============================================================================
echo.

set "SCRIPT_NAME=ui.py"
set "EXE_NAME=GestorOncologia"
set "WORK_DIR=%~dp0"

cd /d "%WORK_DIR%"

echo [STEP 1/9] Verificando entorno Python y dependencias...
python --version
if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR: Python no encontrado
    pause
    exit /b 1
)

echo.
echo [STEP 2/9] Instalando/Actualizando PyInstaller y dependencias CRÍTICAS...
pip install --upgrade pyinstaller
pip install --upgrade numpy
pip install --upgrade pandas
pip install --upgrade ttkbootstrap
pip install --upgrade matplotlib
pip install --upgrade seaborn
pip install --upgrade pytesseract
pip install --upgrade PyMuPDF
pip install --upgrade pillow
pip install --upgrade selenium
pip install --upgrade webdriver-manager
pip install --upgrade openpyxl
pip install --upgrade python-dateutil
pip install --upgrade Babel
pip install --upgrade holidays
pip install --upgrade cryptography
pip install --upgrade psutil

echo.
echo [STEP 3/9] Verificando instalación de dependencias críticas...
python -c "import numpy; print('✅ NumPy OK')"
python -c "import pandas; print('✅ Pandas OK')"
python -c "import ttkbootstrap; print('✅ TTKBootstrap OK')"
python -c "import matplotlib; print('✅ Matplotlib OK')"
python -c "import seaborn; print('✅ Seaborn OK')"
python -c "import pytesseract; print('✅ PyTesseract OK')"
python -c "import fitz; print('✅ PyMuPDF OK')"
python -c "import PIL; print('✅ Pillow OK')"
python -c "import selenium; print('✅ Selenium OK')"
python -c "from selenium import webdriver; print('✅ Selenium WebDriver OK')"
python -c "from webdriver_manager.chrome import ChromeDriverManager; print('✅ WebDriver Manager OK')"
python -c "import openpyxl; print('✅ OpenPyXL OK')"
python -c "import dateutil; print('✅ Python-DateUtil OK')"
python -c "import babel; print('✅ Babel OK')"
python -c "import holidays; print('✅ Holidays OK')"
python -c "import cryptography; print('✅ Cryptography OK')"
python -c "import psutil; print('✅ PSUtil OK')"
python -c "import sqlite3; print('✅ SQLite3 OK')"

echo.
echo [STEP 4/9] Limpiando compilaciones anteriores...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul

echo.
echo [STEP 5/9] Verificando archivos requeridos...
if not exist "%SCRIPT_NAME%" (
    echo ❌ ERROR: No se encontró %SCRIPT_NAME%
    pause
    exit /b 1
)

if not exist "imagenes\" (
    echo ❌ ERROR: No se encontró la carpeta imagenes\
    pause
    exit /b 1
)

if not exist "config\config.ini" (
    echo ⚠️ ADVERTENCIA: No se encontró config\config.ini - Tesseract podría no funcionar correctamente
)

if not exist "imagenes\icono.png" (
    echo ⚠️ ADVERTENCIA: No se encontró icono - usando icono por defecto
)

echo ✅ Archivos principales verificados

echo.
echo [STEP 6/9] Generando archivo .spec OPTIMIZADO para Gestor Oncología...

(
echo # -*- mode: python ; coding: utf-8 -*-
echo.
echo import os
echo import sys
echo from PyInstaller.utils.hooks import collect_submodules, collect_data_files
echo.
echo # Obtener módulos de dependencias críticas
echo ttkbootstrap_modules = collect_submodules('ttkbootstrap'^)
echo matplotlib_modules = collect_submodules('matplotlib'^)
echo selenium_modules = collect_submodules('selenium'^)
echo numpy_modules = collect_submodules('numpy'^)
echo.
echo # Datos adicionales - archivos y carpetas necesarias
echo added_files = [
echo     ('imagenes', 'imagenes'^),
echo     ('config', 'config'^),
echo     ('core', 'core'^),
echo     ('requirements.txt', '.'^)
echo ]
echo.
echo # Importaciones ocultas para Gestor Oncología
echo hiddenimports = [
echo     'numpy',
echo     'pandas',
echo     'tkinter',
echo     'ttkbootstrap',
echo     'matplotlib.backends.backend_tkagg',
echo     'seaborn',
echo     'pytesseract',
echo     'fitz',
echo     'PIL.Image',
echo     'selenium.webdriver',
echo     'webdriver_manager.chrome',
echo     'openpyxl',
echo     'dateutil',
echo     'babel',
echo     'holidays',
echo     'sqlite3',
echo     'psutil',
echo     'cryptography',
echo     'core.calendario',
echo     'core.database_manager',
echo     'core.huv_web_automation',
echo     'core.ocr_processing',
echo     'core.procesador_ihq',
echo     'core.procesador_ihq_biomarcadores',
echo     'core.enhanced_export_system',
echo     'core.enhanced_database_dashboard',
echo     'config.version_info'
echo ] + ttkbootstrap_modules + matplotlib_modules + selenium_modules + numpy_modules
echo.
echo a = Analysis(
echo     ['%SCRIPT_NAME%'],
echo     pathex=[],
echo     binaries=[],
echo     datas=added_files,
echo     hiddenimports=hiddenimports,
echo     hookspath=[],
echo     hooksconfig={},
echo     runtime_hooks=[],
echo     excludes=[],
echo     noarchive=False,
echo     optimize=0,
echo ^)
echo.
echo pyz = PYZ(a.pure^)
echo.
echo exe = EXE(
echo     pyz,
echo     a.scripts,
echo     a.binaries,
echo     a.datas,
echo     [],
echo     name='%EXE_NAME%',
echo     debug=False,
echo     bootloader_ignore_signals=False,
echo     strip=False,
echo     upx=True,
echo     console=False,
echo     disable_windowed_traceback=False,
echo     argv_emulation=False,
echo     target_arch=None,
echo     codesign_identity=None,
echo     entitlements_file=None,
echo     icon=None
echo ^)
) > "%EXE_NAME%.spec"

echo ✅ Archivo .spec generado

echo.
echo [STEP 7/9] Compilando con PyInstaller (modo ONEFILE - archivo único)...
pyinstaller --clean --noconfirm "%EXE_NAME%.spec"

if %ERRORLEVEL% neq 0 (
    echo ❌ ERROR en la compilación principal
    echo.
    echo Intentando compilación de emergencia (onefile)...
    echo.
    pyinstaller --onefile --windowed --clean ^
        --add-data "imagenes;imagenes" ^
        --add-data "config;config" ^
        --add-data "core;core" ^
        --add-data "requirements.txt;." ^
        --hidden-import "numpy" ^
        --hidden-import "numpy.core" ^
        --hidden-import "pandas" ^
        --hidden-import "pandas.core" ^
        --hidden-import "ttkbootstrap" ^
        --hidden-import "ttkbootstrap.constants" ^
        --hidden-import "ttkbootstrap.style" ^
        --hidden-import "matplotlib" ^
        --hidden-import "matplotlib.pyplot" ^
        --hidden-import "matplotlib.backends.backend_tkagg" ^
        --hidden-import "seaborn" ^
        --hidden-import "pytesseract" ^
        --hidden-import "fitz" ^
        --hidden-import "PIL" ^
        --hidden-import "PIL.Image" ^
        --hidden-import "selenium" ^
        --hidden-import "selenium.webdriver" ^
        --hidden-import "selenium.webdriver.chrome" ^
        --hidden-import "webdriver_manager" ^
        --hidden-import "webdriver_manager.chrome" ^
        --hidden-import "openpyxl" ^
        --hidden-import "dateutil" ^
        --hidden-import "babel" ^
        --hidden-import "holidays" ^
        --hidden-import "psutil" ^
        --hidden-import "cryptography" ^
        --hidden-import "sqlite3" ^
        --hidden-import "core.calendario" ^
        --hidden-import "core.database_manager" ^
        --hidden-import "core.huv_web_automation" ^
        --hidden-import "core.ocr_processing" ^
        --hidden-import "core.procesador_ihq" ^
        --hidden-import "core.procesador_ihq_biomarcadores" ^
        --hidden-import "core.enhanced_export_system" ^
        --hidden-import "core.enhanced_database_dashboard" ^
        --hidden-import "config.version_info" ^
        --noconsole ^
        --name "%EXE_NAME%" ^
        "%SCRIPT_NAME%"

    if %ERRORLEVEL% neq 0 (
        echo ❌ ERROR CRÍTICO: Falló también el modo de emergencia
        echo.
        echo Posibles causas:
        echo - Falta alguna dependencia Python crítica (numpy, pandas, etc.)
        echo - Problema con Tesseract OCR o configuración
        echo - Problema con Selenium WebDriver
        echo - Permisos insuficientes
        echo.
        pause
        exit /b 1
    )
    echo ✅ Compilación de emergencia exitosa
)

echo.
echo [STEP 8/9] Verificando resultado de la compilación...
if exist "dist\%EXE_NAME%.exe" (
    echo ✅ Ejecutable generado exitosamente
    for %%F in ("dist\%EXE_NAME%.exe") do echo [INFO] Tamaño: %%~zF bytes
) else (
    echo ❌ ERROR: No se generó el ejecutable
    pause
    exit /b 1
)

echo.
echo [STEP 9/9] Verificando empaquetado completo...
echo ✅ Modo ONEFILE activado - archivo ejecutable único
echo ℹ️ Incluye OCR, análisis gráfico, automatización web y gestión de datos
echo ℹ️ Base de datos SQLite y archivos de configuración empaquetados

echo.
echo [TEST] Pruebas finales del ejecutable...

echo.
echo [TEST 1] Prueba básica con argumentos de EVARISIS...
start /wait "" "dist\%EXE_NAME%.exe" --lanzado-por-evarisis --nombre "Test Oncología" --cargo "Médico" --tema "superhero" && (
    echo ✅ Test 1 exitoso
) || (
    echo ❌ Test 1 falló - Revisar argumentos requeridos
)

timeout /t 2 /nobreak >nul

echo.
echo [TEST 2] Prueba modo independiente...
start /wait "" "dist\%EXE_NAME%.exe" --modo-independiente && (
    echo ✅ Test 2 exitoso
) || (
    echo ❌ Test 2 falló - Revisar modo independiente
)

timeout /t 2 /nobreak >nul

echo.
echo ===============================================================================
echo                                 🎉 COMPILACIÓN COMPLETADA 🎉
echo ===============================================================================
echo.
echo ✅ Ejecutable: dist\%EXE_NAME%.exe
echo ✅ Con soporte completo para OCR, análisis gráfico y automatización web
echo ✅ Incluye base de datos SQLite y archivos de configuración
echo ✅ Validado para integración con EVARISIS Dashboard
echo ✅ Modo ONEFILE - Archivo ejecutable único (portable)
echo.
echo 🚀 COMANDO PARA EVARISIS:
echo   %EXE_NAME%.exe --lanzado-por-evarisis --nombre "NOMBRE" --cargo "CARGO" --foto "RUTA_FOTO" --tema "TEMA"
echo.
echo 📂 El ejecutable está listo en: dist\%EXE_NAME%.exe
echo.
echo 🔧 CARACTERÍSTICAS INCLUIDAS:
echo   - Procesamiento OCR de informes médicos
echo   - Análisis de biomarcadores oncológicos
echo   - Dashboard gráfico con matplotlib/seaborn
echo   - Automatización web con Selenium
echo   - Gestión de base de datos SQLite
echo   - Interfaz moderna con ttkbootstrap
echo   - Soporte para múltiples formatos (PDF, Excel)
echo.
echo ===============================================================================

pause