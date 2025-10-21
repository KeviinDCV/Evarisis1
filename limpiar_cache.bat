@echo off
chcp 65001 >nul
:: ============================================================================
:: LIMPIAR CACHE DE PYTHON - EVARISIS ONCOLOGIA
:: Version: 3.2.5.1
:: Descripcion: Elimina todas las carpetas __pycache__ del proyecto
:: ============================================================================

echo.
echo ╔════════════════════════════════════════════════════════════════════════╗
echo ║          LIMPIANDO CACHE DE PYTHON - __pycache__                       ║
echo ╚════════════════════════════════════════════════════════════════════════╝
echo.

set "contador=0"

:: Buscar y eliminar todas las carpetas __pycache__ recursivamente
for /d /r "%~dp0" %%i in (__pycache__) do (
    if exist "%%i" (
        echo [ELIMINANDO] %%i
        rmdir /s /q "%%i"
        set /a contador+=1
    )
)

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
if %contador% GTR 0 (
    echo   LIMPIEZA COMPLETADA: %contador% carpeta^(s^) __pycache__ eliminada^(s^)
) else (
    echo   No se encontraron carpetas __pycache__ para eliminar
)
echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
pause
