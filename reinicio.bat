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
:: PASO 3: LIMPIEZA DE CARPETA DATA
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════════════
echo [PASO 3/5] 🗑️ LIMPIANDO CARPETA DATA (BASE DE DATOS Y ARCHIVOS TEMPORALES)
echo ════════════════════════════════════════════════════════════════════════
echo.

set "DATA_DIR=%~dp0data"

if exist "%DATA_DIR%\" (
    echo   ⚠️ ADVERTENCIA: Se eliminarán TODOS los datos de:
    echo   📁 %DATA_DIR%
    echo.
    echo   Esto incluye:
    echo     • Base de datos (huv_oncologia_NUEVO.db)
    echo     • Debug maps (debug_maps/)
    echo     • Auditorías IA (auditorias_ia/)
    echo     • Exportaciones (exports/)
    echo.

    choice /C SN /M "¿Deseas continuar con la eliminación de datos (S/N)?"

    if errorlevel 2 (
        echo.
        echo   ❌ Limpieza de datos CANCELADA por el usuario
        echo   ℹ️ Se continuará sin eliminar la carpeta data
        echo.
        goto :skip_data_cleanup
    )

    echo.
    echo   🗑️ Eliminando contenido de data/...

    :: Eliminar contenido preservando la estructura de carpetas principales
    if exist "%DATA_DIR%\huv_oncologia_NUEVO.db" (
        echo   [ELIMINANDO] Base de datos: huv_oncologia_NUEVO.db
        del /f /q "%DATA_DIR%\huv_oncologia_NUEVO.db" 2>nul
    )

    if exist "%DATA_DIR%\debug_maps\" (
        echo   [ELIMINANDO] Debug maps: debug_maps\*
        rmdir /s /q "%DATA_DIR%\debug_maps" 2>nul
        mkdir "%DATA_DIR%\debug_maps" 2>nul
    )

    if exist "%DATA_DIR%\auditorias_ia\" (
        echo   [ELIMINANDO] Auditorías IA: auditorias_ia\*
        rmdir /s /q "%DATA_DIR%\auditorias_ia" 2>nul
        mkdir "%DATA_DIR%\auditorias_ia" 2>nul
    )

    if exist "%DATA_DIR%\exports\" (
        echo   [ELIMINANDO] Exportaciones: exports\*
        rmdir /s /q "%DATA_DIR%\exports" 2>nul
        mkdir "%DATA_DIR%\exports" 2>nul
    )

    echo   ✅ Carpeta data limpiada (estructura preservada)
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
echo     • Caché Python: %contador_cache% carpeta(s) eliminada(s)
echo     • Archivos .pyc: %contador_pyc% archivo(s) eliminado(s)
echo     • Carpeta data: Limpiada y lista para uso
echo.
echo   🔄 Para reiniciar nuevamente, ejecuta: reinicio.bat
echo.
pause
