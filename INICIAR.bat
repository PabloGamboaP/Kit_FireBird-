@echo off
title Kit de Conexion Firebird - UNP

REM Python directo sin verificaciones
set PYTHON_CMD=%LOCALAPPDATA%\Python\pythoncore-3.14-64\python.exe

:MENU
cls
echo ================================================================================
echo                    KIT DE CONEXION FIREBIRD - UNP
echo ================================================================================
echo.
echo   CONSULTAS:
echo   1. Probar conexion a Firebird
echo   2. Listar todas las tablas
echo   3. Ver estructura de una tabla
echo   4. Consultar activos por cedula
echo.
echo   MIGRACION A SQL SERVER:
echo   5. Extraer modelo Entidad-Relacion (tablas, PKs, FKs)
echo   6. Extraer Triggers y Stored Procedures
echo   7. Exportar toda la data (CSV completo - puede ser pesado)
echo   8. Exportar data optimizada (CSV solo ultimo periodo)
echo.
echo   CONFIGURACION:
echo   9. Verificar instalacion
echo   A. Instalar/Actualizar fdb
echo   B. Editar configuracion
echo   0. Salir
echo.
echo ================================================================================
set /p opcion="Ingresa el numero de opcion: "

if "%opcion%"=="1" goto PROBAR_CONEXION
if "%opcion%"=="2" goto LISTAR_TABLAS
if "%opcion%"=="3" goto VER_ESTRUCTURA
if "%opcion%"=="4" goto CONSULTAR_ACTIVOS
if "%opcion%"=="5" goto EXTRAER_MODELO
if "%opcion%"=="6" goto EXTRAER_TRIGGERS
if "%opcion%"=="7" goto EXPORTAR_DATA
if "%opcion%"=="8" goto EXPORTAR_DATA_OPTIMIZADA
if "%opcion%"=="9" goto VERIFICAR
if /i "%opcion%"=="A" goto INSTALAR_FDB
if /i "%opcion%"=="B" goto EDITAR_CONFIG
if "%opcion%"=="0" goto SALIR
goto MENU

:PROBAR_CONEXION
cls
echo ================================================================================
echo                         PROBANDO CONEXION A FIREBIRD
echo ================================================================================
echo.
"%PYTHON_CMD%" conexion_simple.py
echo.
pause
goto MENU

:LISTAR_TABLAS
cls
echo ================================================================================
echo                         LISTANDO TABLAS DISPONIBLES
echo ================================================================================
echo.
"%PYTHON_CMD%" explorar_tablas.py
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
"%PYTHON_CMD%" explorar_tablas.py %tabla%
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
"%PYTHON_CMD%" consultar_activos.py %cedula%
echo.
pause
goto MENU

:EXTRAER_MODELO
cls
echo ================================================================================
echo                    EXTRAER MODELO ENTIDAD-RELACION
echo ================================================================================
echo.
echo Este proceso extraera el esquema completo de la base de datos.
echo.
pause
echo.
"%PYTHON_CMD%" extraer_modelo_er.py
echo.
pause
goto MENU

:EXTRAER_TRIGGERS
cls
echo ================================================================================
echo                    EXTRAER TRIGGERS Y STORED PROCEDURES
echo ================================================================================
echo.
echo Este proceso extraera todos los triggers y stored procedures.
echo.
pause
echo.
"%PYTHON_CMD%" extraer_triggers_procedures.py
echo.
pause
goto MENU

:EXPORTAR_DATA
cls
echo ================================================================================
echo                    EXPORTAR DATA COMPLETA (CSV)
echo ================================================================================
echo.
echo ADVERTENCIA: Exporta TODO el historial (puede ser muy pesado)
echo             SALAJUSTES tendra ~12M registros
echo.
echo Recomendacion: Usa opcion 8 (Data Optimizada) en su lugar
echo.
set /p confirmar="Deseas continuar con exportacion completa? (S/N): "
if /i not "%confirmar%"=="S" goto MENU
echo.
"%PYTHON_CMD%" exportar_data_completa.py
echo.
pause
goto MENU

:EXPORTAR_DATA_OPTIMIZADA
cls
echo ================================================================================
echo                    EXPORTAR DATA OPTIMIZADA (CSV)
echo ================================================================================
echo.
echo Este proceso exporta:
echo   - Todas las tablas completas
echo   - SALAJUSTES solo con el ultimo periodo (reduce de 12M a 196K registros)
echo.
echo Ventajas:
echo   - Mucho mas rapido
echo   - Archivos mas pequenos
echo   - Suficiente para sistema actual
echo.
set /p confirmar="Deseas continuar? (S/N): "
if /i not "%confirmar%"=="S" goto MENU
echo.
"%PYTHON_CMD%" exportar_data_optimizada.py
echo.
pause
goto MENU

:VERIFICAR
cls
echo ================================================================================
echo                         VERIFICANDO INSTALACION
echo ================================================================================
echo.
echo Version de Python:
"%PYTHON_CMD%" --version
echo.
echo Verificando fdb...
"%PYTHON_CMD%" -c "import fdb; print('[OK] fdb version:', fdb.__version__)"
echo.
echo Verificando archivos...
if exist "fbclient.dll" (echo [OK] fbclient.dll encontrado) else (echo [ERROR] fbclient.dll NO encontrado)
if exist "configuracion.ini" (echo [OK] configuracion.ini encontrado) else (echo [ERROR] configuracion.ini NO encontrado)
echo.
echo ================================================================================
echo.
pause
goto MENU

:INSTALAR_FDB
cls
echo ================================================================================
echo                         INSTALAR/ACTUALIZAR FDB
echo ================================================================================
echo.
echo Este proceso instalara o actualizara el paquete 'fdb'.
echo.
echo Deseas continuar? (S/N)
set /p confirmar="Respuesta: "

if /i not "%confirmar%"=="S" goto MENU

echo.
echo Instalando fdb...
"%PYTHON_CMD%" -m pip install --user --upgrade fdb
echo.
echo ================================================================================
echo.
pause
goto MENU

:EDITAR_CONFIG
notepad configuracion.ini
goto MENU

:SALIR
exit
