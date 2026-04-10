@echo off
chcp 65001 >nul
color 0E
:: ============================================================================
:: REINICIO COMPLETO - EVARISIS ONCOLOGÍA
:: Version: 5.3.8
:: Descripción: Limpia caché, datos y reinicia la aplicación
:: ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║          🔄 REINICIO COMPLETO - EVARISIS CIRUGÍA ONCOLÓGICA           ║
echo ║              Limpieza total + Arranque desde cero                      ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

:: ============================================================================
:: PASO 1: LIMPIEZA DE CACHÉ __pycache__
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 1/5] 🧹 LIMPIANDO CACHÉ DE PYTHON (__pycache__)
echo ════════════════════════════════════════════════════════════════════════
echo.

set "contador_cache=0"

for /d /r "%~dp0" %%i in (__pycache__) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache+=1
    )
)

if %contador_cache% GTR 0 (
    echo   ✅ %contador_cache% carpeta^(s^) __pycache__ eliminada^(s^)
) else (
    echo   ℹ️ No se encontraron carpetas __pycache__
)

:: ============================================================================
:: PASO 2: LIMPIEZA DE ARCHIVOS .pyc
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 2/5] 🧹 LIMPIANDO ARCHIVOS COMPILADOS (.pyc)
echo ════════════════════════════════════════════════════════════════════════
echo.

set "contador_pyc=0"

for /r "%~dp0" %%i in (*.pyc) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        del /f /q "%%i" 2>nul
        set /a contador_pyc+=1
    )
)

if %contador_pyc% GTR 0 (
    echo   ✅ %contador_pyc% archivo^(s^) .pyc eliminado^(s^)
) else (
    echo   ℹ️ No se encontraron archivos .pyc
)

:: ============================================================================
:: PASO 2.5: LIMPIEZA DE CACHÉS ADICIONALES DE PYTHON
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 2.5/5] 🧹 LIMPIANDO CACHÉS ADICIONALES (.pyo, pytest, mypy, etc.)
echo ════════════════════════════════════════════════════════════════════════
echo.

set "contador_pyo=0"
set "contador_cache_dirs=0"

:: Eliminar archivos .pyo (Python optimized bytecode)
echo   🔍 Buscando archivos .pyo...
for /r "%~dp0" %%i in (*.pyo) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        del /f /q "%%i" 2>nul
        set /a contador_pyo+=1
    )
)

if %contador_pyo% GTR 0 (
    echo   ✅ %contador_pyo% archivo^(s^) .pyo eliminado^(s^)
) else (
    echo   ℹ️ No se encontraron archivos .pyo
)

:: Eliminar carpetas de caché de herramientas
echo.
echo   🔍 Buscando carpetas de caché de herramientas...

:: .pytest_cache
for /d /r "%~dp0" %%i in (.pytest_cache) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .mypy_cache
for /d /r "%~dp0" %%i in (.mypy_cache) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .ruff_cache
for /d /r "%~dp0" %%i in (.ruff_cache) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .tox
for /d /r "%~dp0" %%i in (.tox) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .eggs
for /d /r "%~dp0" %%i in (.eggs) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .cache (carpeta genérica de caché)
for /d /r "%~dp0" %%i in (.cache) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .hypothesis (caché de hypothesis testing)
for /d /r "%~dp0" %%i in (.hypothesis) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        rmdir /s /q "%%i" 2>nul
        set /a contador_cache_dirs+=1
    )
)

:: .coverage (archivos de cobertura)
for /r "%~dp0" %%i in (.coverage) do (
    if exist "%%i" (
        echo   [ELIMINANDO] %%i
        del /f /q "%%i" 2>nul
    )
)

if %contador_cache_dirs% GTR 0 (
    echo   ✅ %contador_cache_dirs% carpeta^(s^) de caché eliminada^(s^)
) else (
    echo   ℹ️ No se encontraron carpetas de caché adicionales
)

:: ============================================================================
:: PASO 3: LIMPIEZA DE CARPETA DATA
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 3/5] 🗑️ ELIMINANDO COMPLETAMENTE LA CARPETA DATA
echo ════════════════════════════════════════════════════════════════════════
echo.

set "DATA_DIR=%~dp0data"

if exist "%DATA_DIR%\" (
    echo   ⚠️ ADVERTENCIA: Se eliminará COMPLETAMENTE:
    echo   📁 %DATA_DIR%
    echo.
    echo   Esto incluye TODO su contenido:
    echo     • Base de datos (huv_oncologia_NUEVO.db)
    echo     • Debug maps (debug_maps/)
    echo     • Auditorías IA (auditorias_ia/)
    echo     • Exportaciones (exports/)
    echo     • Cualquier otro archivo o carpeta dentro de data/
    echo.

    choice /C SN /M "¿Deseas continuar con la eliminación COMPLETA de data (S/N)?"

    if errorlevel 2 (
        echo.
        echo   ❌ Limpieza de datos CANCELADA por el usuario
        echo   ℹ️ Se continuará sin eliminar la carpeta data
        echo.
        goto :skip_data_cleanup
    )

    echo.
    echo   🗑️ Eliminando TODA la carpeta data/...

    rmdir /s /q "%DATA_DIR%" 2>nul

    if %ERRORLEVEL% equ 0 (
        echo   ✅ Carpeta data eliminada completamente
    ) else (
        echo   ⚠️ Advertencia: Hubo problemas al eliminar algunos archivos
        echo   ℹ️ Algunos archivos podrían estar en uso
    )

    echo   📁 Recreando carpeta data vacía...
    mkdir "%DATA_DIR%" 2>nul

    if exist "%DATA_DIR%\" (
        echo   ✅ Carpeta data recreada (vacía y lista para uso)
    ) else (
        echo   ⚠️ No se pudo recrear la carpeta data
        echo   ℹ️ Se creará automáticamente al iniciar la aplicación
    )
) else (
    echo   ℹ️ Carpeta data no existe (se creará al iniciar la app)
)

:skip_data_cleanup

:: ============================================================================
:: PASO 4: CONFIGURACIÓN DEL ENTORNO
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 4/5] ⚙️ CONFIGURANDO ENTORNO VIRTUAL
echo ════════════════════════════════════════════════════════════════════════
echo.

set "WORK_DIR=%~dp0"
set "VENV_PATH=%WORK_DIR%venv0"
set "PYTHON_SCRIPT=ui.py"

cd /d "%WORK_DIR%"

echo   📂 Directorio de trabajo: %WORK_DIR%
echo   🐍 Entorno virtual: %VENV_PATH%
echo   📄 Script principal: %PYTHON_SCRIPT%
echo.

:: Verificar entorno virtual
if not exist "%VENV_PATH%\" (
    echo   ❌ ERROR: No se encontró el entorno virtual en: %VENV_PATH%
    echo   ℹ️ Asegúrate de que existe la carpeta venv0
    echo.
    pause
    exit /b 1
)
echo   ✅ Entorno virtual encontrado

:: Activar entorno virtual
echo   🔄 Activando entorno virtual...
call "%VENV_PATH%\Scripts\activate.bat"
if %ERRORLEVEL% neq 0 (
    echo   ❌ ERROR: No se pudo activar el entorno virtual
    echo.
    pause
    exit /b 1
)
echo   ✅ Entorno virtual activado

:: Verificar script principal
if not exist "%PYTHON_SCRIPT%" (
    echo   ❌ ERROR: No se encontró %PYTHON_SCRIPT%
    echo.
    pause
    exit /b 1
)
echo   ✅ Archivo %PYTHON_SCRIPT% encontrado

:: ============================================================================
:: PASO 5: INICIAR APLICACIÓN
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 5/5] 🚀 INICIANDO EVARISIS CIRUGÍA ONCOLÓGICA
echo ════════════════════════════════════════════════════════════════════════
echo.

echo   ℹ️ Argumentos de EVARISIS:
echo     --lanzado-por-evarisis
echo     --nombre "Daniel Restrepo"
echo     --cargo "Ingeniero de soluciones"
echo     --tema "cosmo"
echo     --modo-independiente
echo.
echo   📊 La base de datos se creará automáticamente al iniciar
echo   ⏳ Por favor espera mientras se carga la aplicación...
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.

"%VENV_PATH%\Scripts\python.exe" %PYTHON_SCRIPT% --lanzado-por-evarisis --nombre "Daniel Restrepo" --cargo "Ingeniero de soluciones" --foto "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD\base_de_usuarios\Daniel Restrepo.jpeg" --tema "cosmo" --ruta-fotos "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD\base_de_usuarios" --ruta-datos "C:\Users\USUARIO\Desktop\DEBERES HUV\ProyectoHUV1EVARISISDASHBOARD" --modo-independiente

:: ============================================================================
:: FINALIZACIÓN
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo                    ✅ APLICACIÓN CERRADA CORRECTAMENTE
echo ════════════════════════════════════════════════════════════════════════
echo.
echo   💡 Resumen de limpieza:
echo     • Carpetas __pycache__: %contador_cache% eliminada(s)
echo     • Archivos .pyc: %contador_pyc% eliminado(s)
echo     • Archivos .pyo: %contador_pyo% eliminado(s)
echo     • Cachés adicionales (pytest, mypy, etc.): %contador_cache_dirs% eliminada(s)
echo     • Carpeta data: Limpiada y lista para uso
echo.
echo   🔄 Para reiniciar nuevamente, ejecuta: reinicio.bat
echo.
pause
