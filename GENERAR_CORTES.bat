@echo off
chcp 65001 > nul
title Generador de Cortes Históricos - Kit FireBird

echo ================================================================================
echo GENERADOR DE CORTES HISTORICOS
echo ================================================================================
echo.
echo Este script genera reportes Excel de activos a fechas de corte específicas
echo (31 de diciembre de cada año)
echo.
echo Requisitos:
echo   - Archivo configuracion.ini configurado
echo   - Librería fdb instalada
echo   - Librería openpyxl instalada
echo.
echo ================================================================================
echo.

REM Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo.
    echo Instala Python desde: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Verificar si existe configuracion.ini
if not exist "configuracion.ini" (
    echo ERROR: No se encontró el archivo 'configuracion.ini'
    echo.
    echo Copia 'configuracion.ini.example' a 'configuracion.ini' y configuralo
    echo.
    pause
    exit /b 1
)

REM Verificar si fdb está instalado
python -c "import fdb" >nul 2>&1
if errorlevel 1 (
    echo Instalando librería fdb...
    pip install fdb
    echo.
)

REM Verificar si openpyxl está instalado
python -c "import openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Instalando librería openpyxl...
    pip install openpyxl
    echo.
)

REM Ejecutar el script
echo Iniciando generador de cortes...
echo.
python generar_cortes_historicos.py

echo.
echo ================================================================================
echo.
pause
