@echo off
color 0E
title ONCONOVA [MODO DESARROLLO UI - BD COPIA, NO PRODUCCION]
echo.
echo ================================================================================
echo            ONCONOVA - MODO DESARROLLO DE INTERFAZ (UI/UX)
echo   Esta instancia usa una COPIA de la base de datos (huv_oncologia_DEV.db).
echo   NO afecta la BD de produccion ni el lote de IA que este procesando.
echo   Sirve para iterar el diseno visual sin riesgo de 'database is locked'.
echo ================================================================================
echo.

REM Configuracion de rutas (mismo proyecto, reusa venv0)
set "WORK_DIR=%~dp0"
set "VENV_PATH=%WORK_DIR%venv0"
cd /d "%WORK_DIR%"

REM Apuntar a la BD de DESARROLLO (copia). database_manager lee esta variable.
set "ONCONOVA_DB_OVERRIDE=%WORK_DIR%data\huv_oncologia_DEV.db"

REM Encoding UTF-8 para logs completos
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

echo BD activa (desarrollo): %ONCONOVA_DB_OVERRIDE%
echo.

if not exist "%VENV_PATH%\Scripts\python.exe" (
    echo ERROR: No se encontro el entorno virtual venv0.
    echo Lanza primero iniciar_python.bat normal.
    pause
    exit /b 1
)

if not exist "%WORK_DIR%data\huv_oncologia_DEV.db" (
    echo ADVERTENCIA: No existe la BD de desarrollo huv_oncologia_DEV.db.
    echo Copiala manualmente con:
    echo    copy data\huv_oncologia_NUEVO.db data\huv_oncologia_DEV.db
    echo.
)

echo Iniciando instancia de desarrollo de UI con tema institucional 'huv'...
echo.
"%VENV_PATH%\Scripts\python.exe" ui.py --lanzado-por-onconova --nombre "DESARROLLO UI" --cargo "Diseno UI-UX" --tema "huv" --modo-independiente 2>&1

echo.
echo ================================================================================
echo                    Instancia de desarrollo cerrada
echo ================================================================================
pause >nul
