@echo off
chcp 65001 >nul
color 0A
setlocal enabledelayedexpansion

echo.
echo ===============================================================================
echo            🏥 COMPILADOR GESTOR ONCOLOGÍA HUV V6.9.0 🏥
echo                  Usando venv0 (entorno virtual del proyecto)
echo ===============================================================================
echo.

set "WORK_DIR=%~dp0"
cd /d "%WORK_DIR%"

set "VENV_PY=%WORK_DIR%venv0\Scripts\python.exe"
set "VENV_PIP=%WORK_DIR%venv0\Scripts\pip.exe"
set "VENV_PYINSTALLER=%WORK_DIR%venv0\Scripts\pyinstaller.exe"
set "EXE_NAME=GestorOncologia"

echo [STEP 1/6] Verificando venv0...
if not exist "%VENV_PY%" (
    echo ❌ ERROR: No se encontró venv0\Scripts\python.exe
    echo Ejecutá primero: instalar_entorno.bat
    pause
    exit /b 1
)
echo ✅ venv0 OK
"%VENV_PY%" --version

echo.
echo [STEP 2/6] Verificando dependencias críticas en venv0...
"%VENV_PY%" -c "import numpy, pandas, ttkbootstrap, matplotlib, seaborn, pytesseract, fitz, PIL, selenium, openpyxl, cryptography, psutil, pymysql, PyInstaller; print('Todas las dependencias OK')" 2>nul
if %ERRORLEVEL% neq 0 (
    echo ⚠️ Faltan dependencias. Instalando...
    "%VENV_PIP%" install -r requirements.txt
)
echo ✅ Dependencias OK

echo.
echo [STEP 3/6] Limpiando builds anteriores...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "%EXE_NAME%.spec" del /q "%EXE_NAME%.spec" 2>nul
echo ✅ Limpieza OK

echo.
echo [STEP 4/6] Generando .spec...
(
echo # -*- mode: python ; coding: utf-8 -*-
echo from PyInstaller.utils.hooks import collect_submodules
echo.
echo ttkbootstrap_modules = collect_submodules^('ttkbootstrap'^)
echo matplotlib_modules = collect_submodules^('matplotlib'^)
echo selenium_modules = collect_submodules^('selenium'^)
echo numpy_modules = collect_submodules^('numpy'^)
echo.
echo # IMPORTANTE V6.9.0: config se incluye, pero el COMPILADOR copia
echo # tambien una version externa a dist/config/ para que sea editable
echo added_files = [
echo     ^('imagenes', 'imagenes'^),
echo     ^('config', 'config'^),
echo     ^('core', 'core'^),
echo     ^('requirements.txt', '.'^),
echo ]
echo.
echo hiddenimports = [
echo     'numpy', 'pandas', 'tkinter', 'ttkbootstrap',
echo     'matplotlib.backends.backend_tkagg', 'seaborn',
echo     'pytesseract', 'fitz', 'PIL.Image',
echo     'selenium.webdriver', 'webdriver_manager.chrome',
echo     'openpyxl', 'dateutil', 'babel', 'holidays',
echo     'sqlite3', 'psutil', 'cryptography',
echo     # V6.9.0 - MySQL/MariaDB driver
echo     'pymysql', 'pymysql.cursors', 'pymysql.constants',
echo     'pymysql.constants.CLIENT', 'pymysql.constants.COMMAND',
echo     'pymysql.constants.FIELD_TYPE', 'pymysql.constants.SERVER_STATUS',
echo     # Modulos core
echo     'core.calendario', 'core.database_manager',
echo     'core.db_adapter', 'core.diagnosticos_ia_db',
echo     'core.columnas_huv_ia', 'core.llm_client',
echo     'core.huv_web_automation', 'core.ocr_processing',
echo     'core.procesador_ihq', 'core.procesador_ihq_biomarcadores',
echo     'core.enhanced_export_system', 'core.enhanced_database_dashboard',
echo     'config.version_info',
echo ] + ttkbootstrap_modules + matplotlib_modules + selenium_modules + numpy_modules
echo.
echo a = Analysis^(
echo     ['ui.py'], pathex=[], binaries=[], datas=added_files,
echo     hiddenimports=hiddenimports, hookspath=[], hooksconfig={},
echo     runtime_hooks=[], excludes=[], noarchive=False, optimize=0,
echo ^)
echo pyz = PYZ^(a.pure^)
echo exe = EXE^(
echo     pyz, a.scripts, a.binaries, a.datas, [],
echo     name='%EXE_NAME%', debug=False, bootloader_ignore_signals=False,
echo     strip=False, upx=True, console=False, disable_windowed_traceback=False,
echo     argv_emulation=False, target_arch=None, codesign_identity=None,
echo     entitlements_file=None, icon=None,
echo ^)
) > "%EXE_NAME%.spec"

if not exist "%EXE_NAME%.spec" (
    echo ❌ ERROR generando .spec
    pause
    exit /b 1
)
echo ✅ .spec generado

echo.
echo [STEP 5/6] Compilando con PyInstaller (puede tardar 3-10 min)...
echo.
"%VENV_PYINSTALLER%" --clean --noconfirm "%EXE_NAME%.spec"

if %ERRORLEVEL% neq 0 (
    echo.
    echo ❌ ERROR en compilación PyInstaller
    pause
    exit /b 1
)

if not exist "dist\%EXE_NAME%.exe" (
    echo ❌ ERROR: dist\%EXE_NAME%.exe no se generó
    pause
    exit /b 1
)

echo ✅ Ejecutable generado: dist\%EXE_NAME%.exe
for %%F in ("dist\%EXE_NAME%.exe") do echo    Tamaño: %%~zF bytes (~%%~zF / 1024 / 1024 MB)

echo.
echo [STEP 6/6] Configurando archivos EXTERNOS al .exe (editables)...

REM Crear estructura post-build para distribución
if not exist "dist\config" mkdir "dist\config"
copy /Y "config\config.ini" "dist\config\config.ini" >nul
echo ✅ dist\config\config.ini (EDITABLE por cada cliente)

if not exist "dist\data" mkdir "dist\data"
echo. > "dist\data\.gitkeep"
echo ✅ dist\data\ (para BD SQLite si modo offline)

if not exist "dist\pdfs_patologia" mkdir "dist\pdfs_patologia"
echo Carpeta para los PDFs de patologia > "dist\pdfs_patologia\README.txt"
echo ✅ dist\pdfs_patologia\ (para PDFs del usuario)

if exist "CLIENTE_SETUP.md" copy /Y "CLIENTE_SETUP.md" "dist\CLIENTE_SETUP.md" >nul

echo.
echo ===============================================================================
echo                       🎉 COMPILACIÓN COMPLETADA 🎉
echo ===============================================================================
echo.
echo 📁 Carpeta lista para distribuir: dist\
echo.
echo Contenido:
dir /b "dist"
echo.
echo 📋 PRÓXIMOS PASOS:
echo   1. Probá el .exe: cd dist  ^&^&  GestorOncologia.exe
echo   2. Copiá toda la carpeta dist\ a otras PCs del HUV
echo   3. En cada PC cliente: editá config\config.ini con la IP del servidor
echo   4. Doble click en GestorOncologia.exe
echo.
echo Ver CLIENTE_SETUP.md para mas detalles.
echo.
pause
endlocal
