@echo off
title Migracion Completa Firebird a SQL Server - UNP

REM Usar py launcher de Windows
set PYTHON_CMD=py

REM Verificar Python silenciosamente
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    cls
    echo ================================================================================
    echo                         PYTHON NO INSTALADO
    echo ================================================================================
    echo.
    echo [ERROR] Python no esta instalado en este PC.
    echo.
    echo Instala Python 3.11+ desde: https://www.python.org/downloads/
    echo.
    pause
    exit
)

REM Verificar fdb silenciosamente
%PYTHON_CMD% -c "import fdb" >nul 2>&1
if errorlevel 1 (
    cls
    echo ================================================================================
    echo                    DEPENDENCIA FALTANTE: fdb
    echo ================================================================================
    echo.
    echo [ERROR] El paquete 'fdb' no esta instalado.
    echo.
    echo Para instalar, ejecuta:
    echo   py -m pip install --user fdb
    echo.
    echo O ejecuta INICIAR.bat que te guiara en la instalacion.
    echo.
    pause
    exit
)

cls
echo ================================================================================
echo           MIGRACION COMPLETA: FIREBIRD ^-^> SQL SERVER
echo ================================================================================
echo.
echo Este proceso ejecutara los 4 pasos de migracion:
echo.
echo   1. Extraer modelo Entidad-Relacion (esquema completo)
echo   2. Extraer Triggers y Stored Procedures (logica de negocio)
echo   3. Analizar problemas de normalizacion
echo   4. Exportar toda la data a CSV
echo.
echo ADVERTENCIA: Este proceso puede tomar varios minutos.
echo.
echo ================================================================================
set /p confirmar="Deseas continuar con la migracion completa? (S/N): "

if /i not "%confirmar%"=="S" (
    echo.
    echo Migracion cancelada.
    timeout /t 2 >nul
    exit
)

echo.
echo ================================================================================
echo PASO 1/4: EXTRAYENDO MODELO ENTIDAD-RELACION
echo ================================================================================
echo.
%PYTHON_CMD% extraer_modelo_er.py
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la extraccion del modelo.
    pause
    exit
)

echo.
echo ================================================================================
echo PASO 2/4: EXTRAYENDO TRIGGERS Y STORED PROCEDURES
echo ================================================================================
echo.
%PYTHON_CMD% extraer_triggers_procedures.py
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la extraccion de triggers y procedures.
    pause
    exit
)

echo.
echo ================================================================================
echo PASO 3/4: ANALIZANDO PROBLEMAS DE NORMALIZACION
echo ================================================================================
echo.
%PYTHON_CMD% analizar_normalizacion.py
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo el analisis de normalizacion.
    pause
    exit
)

echo.
echo ================================================================================
echo PASO 4/4: EXPORTANDO DATA COMPLETA A CSV
echo ================================================================================
echo.
%PYTHON_CMD% exportar_data_completa.py
if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la exportacion de data.
    pause
    exit
)

echo.
echo ================================================================================
echo                    MIGRACION COMPLETA EXITOSA
echo ================================================================================
echo.
echo Archivos generados:
echo   - modelo_er_*.txt y modelo_er_*.sql
echo   - triggers_procedures_*.txt y triggers_procedures_*.sql
echo   - analisis_normalizacion_*.txt
echo   - data_export_*/ (carpeta con CSVs)
echo.
echo Proximos pasos:
echo   1. Revisar el modelo ER y el analisis de normalizacion
echo   2. Crear la base de datos en SQL Server usando modelo_er_*.sql
echo   3. Convertir triggers y procedures de Firebird a T-SQL
echo   4. Importar los CSVs a SQL Server
echo   5. Validar integridad de datos
echo.
echo ================================================================================
pause
