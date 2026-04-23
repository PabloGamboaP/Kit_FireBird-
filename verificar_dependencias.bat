@echo off
title Verificacion de Dependencias - Kit Firebird

cls
echo ================================================================================
echo                    VERIFICACION DE DEPENDENCIAS
echo ================================================================================
echo.

REM Verificar Python
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   [X] Python NO instalado
    echo.
    echo   Instala Python desde: https://www.python.org/downloads/
    echo.
    set PYTHON_OK=0
) else (
    for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo   [OK] %PYTHON_VERSION%
    set PYTHON_OK=1
)

REM Verificar fdb
echo.
echo [2/4] Verificando paquete fdb...
python -c "import fdb" >nul 2>&1
if errorlevel 1 (
    echo   [X] fdb NO instalado
    echo.
    echo   Para instalar: python -m pip install --user fdb
    echo   O ejecuta INICIAR.bat para instalacion guiada
    echo.
    set FDB_OK=0
) else (
    for /f "tokens=*" %%i in ('python -c "import fdb; print(fdb.__version__)" 2^>^&1') do set FDB_VERSION=%%i
    echo   [OK] fdb version %FDB_VERSION%
    set FDB_OK=1
)

REM Verificar fbclient.dll
echo.
echo [3/4] Verificando fbclient.dll...
if exist "fbclient.dll" (
    echo   [OK] fbclient.dll encontrado
    set FBCLIENT_OK=1
) else (
    echo   [X] fbclient.dll NO encontrado
    echo.
    echo   Descarga Firebird 2.5.9 64-bit y copia fbclient.dll aqui
    echo.
    set FBCLIENT_OK=0
)

REM Verificar configuracion.ini
echo.
echo [4/4] Verificando configuracion.ini...
if exist "configuracion.ini" (
    echo   [OK] configuracion.ini encontrado
    set CONFIG_OK=1
) else (
    echo   [X] configuracion.ini NO encontrado
    echo.
    echo   Copia configuracion.ini.example a configuracion.ini
    echo   y edita con tus credenciales
    echo.
    set CONFIG_OK=0
)

REM Resumen
echo.
echo ================================================================================
echo                              RESUMEN
echo ================================================================================
echo.

if "%PYTHON_OK%"=="1" if "%FDB_OK%"=="1" if "%FBCLIENT_OK%"=="1" if "%CONFIG_OK%"=="1" (
    echo   [OK] TODAS LAS DEPENDENCIAS ESTAN INSTALADAS
    echo.
    echo   Puedes usar el kit sin problemas.
    echo   Ejecuta INICIAR.bat para comenzar.
    echo.
) else (
    echo   [!] FALTAN ALGUNAS DEPENDENCIAS
    echo.
    echo   Revisa los mensajes anteriores y corrige los problemas.
    echo.
)

echo ================================================================================
echo.
pause
