@echo off
chcp 65001 > nul
title Consultar Factura de Compra - Kit FireBird

echo ================================================================================
echo CONSULTA DE FACTURAS DE COMPRA
echo ================================================================================
echo.
echo Este script busca activos asociados a una factura especifica
echo.
echo Ejemplos:
echo   - FC000983
echo   - 000983
echo   - F-2024-001
echo.
echo ================================================================================
echo.

REM Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en el PATH
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verificar si existe configuracion.ini
if not exist "configuracion.ini" (
    echo ERROR: No se encontro el archivo 'configuracion.ini'
    echo.
    echo Copia 'configuracion.ini.example' a 'configuracion.ini' y configuralo
    echo.
    pause
    exit /b 1
)

REM Verificar si fdb esta instalado
python -c "import fdb" >nul 2>&1
if errorlevel 1 (
    echo Instalando libreria fdb...
    pip install fdb
    echo.
)

REM Ejecutar el script
python consultar_factura.py %*

echo.
echo ================================================================================
echo.
pause
