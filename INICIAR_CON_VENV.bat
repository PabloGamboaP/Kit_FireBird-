@echo off
title Kit de Conexion Firebird - UNP (con venv)

REM Activar entorno virtual del proyecto Django
call ..\..\.venv\Scripts\activate.bat

:MENU
cls
echo ================================================================================
echo                    KIT DE CONEXION FIREBIRD - UNP
echo                         (Usando entorno virtual)
echo ================================================================================
echo.
echo Selecciona una opcion:
echo.
echo   1. Probar conexion a Firebird
echo   2. Listar todas las tablas
echo   3. Ver estructura de una tabla
echo   4. Consultar activos por cedula
echo   5. Exportar activos a Excel
echo   6. Verificar instalacion
echo   7. Salir
echo.
echo ================================================================================
set /p opcion="Ingresa el numero de opcion: "

if "%opcion%"=="1" goto PROBAR_CONEXION
if "%opcion%"=="2" goto LISTAR_TABLAS
if "%opcion%"=="3" goto VER_ESTRUCTURA
if "%opcion%"=="4" goto CONSULTAR_ACTIVOS
if "%opcion%"=="5" goto EXPORTAR_EXCEL
if "%opcion%"=="6" goto VERIFICAR
if "%opcion%"=="7" goto SALIR

echo Opcion invalida
timeout /t 2 >nul
goto MENU

:PROBAR_CONEXION
cls
echo ================================================================================
echo                         PROBANDO CONEXION A FIREBIRD
echo ================================================================================
echo.
python conexion_simple.py
echo.
pause
goto MENU

:LISTAR_TABLAS
cls
echo ================================================================================
echo                         LISTANDO TABLAS DISPONIBLES
echo ================================================================================
echo.
python explorar_tablas.py
echo.
pause
goto MENU

:VER_ESTRUCTURA
cls
echo ================================================================================
echo                         VER ESTRUCTURA DE TABLA
echo ================================================================================
echo.
set /p tabla="Ingresa el nombre de la tabla (ej: MATERIAL): "
echo.
python explorar_tablas.py %tabla%
echo.
pause
goto MENU

:CONSULTAR_ACTIVOS
cls
echo ================================================================================
echo                         CONSULTAR ACTIVOS POR CEDULA
echo ================================================================================
echo.
set /p cedula="Ingresa la cedula (ej: 43875542): "
echo.
python consultar_activos.py %cedula%
echo.
pause
goto MENU

:EXPORTAR_EXCEL
cls
echo ================================================================================
echo                         EXPORTAR ACTIVOS A EXCEL
echo ================================================================================
echo.
set /p cedula="Ingresa la cedula (ej: 43875542): "
echo.
python exportar_a_excel.py %cedula%
echo.
pause
goto MENU

:VERIFICAR
cls
echo ================================================================================
echo                         VERIFICANDO INSTALACION
echo ================================================================================
echo.
echo Verificando Python...
python --version
echo.
echo Verificando dependencias...
python -c "import fdb; print('[OK] fdb instalado')"
python -c "import openpyxl; print('[OK] openpyxl instalado')"
echo.
echo Verificando fbclient.dll...
if exist "fbclient.dll" (
    echo [OK] fbclient.dll encontrado
) else (
    echo [ERROR] fbclient.dll NO encontrado
    echo    Copia fbclient.dll a esta carpeta
)
echo.
echo Verificando configuracion.ini...
if exist "configuracion.ini" (
    echo [OK] configuracion.ini encontrado
) else (
    echo [ERROR] configuracion.ini NO encontrado
)
echo.
echo ================================================================================
echo.
pause
goto MENU

:SALIR
cls
echo.
echo Saliendo...
timeout /t 1 >nul
exit
