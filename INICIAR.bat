@echo off
title Kit de Conexion Firebird - UNP

REM Buscar Python real (no el alias de WindowsApps)
set PYTHON_EXE=
for /f "delims=" %%i in ('where python 2^>nul') do (
    echo %%i | find /i "WindowsApps" >nul
    if errorlevel 1 (
        set PYTHON_EXE=%%i
        goto :found_python
    )
)

REM Si solo encontro WindowsApps, usar python directamente
if "%PYTHON_EXE%"=="" (
    set PYTHON_EXE=python
)

:found_python

REM Verificar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    cls
    echo ================================================================================
    echo                         PYTHON NO INSTALADO
    echo ================================================================================
    echo.
    echo [ERROR] Python no esta instalado en este PC.
    echo.
    echo Para usar este kit necesitas:
    echo   1. Instalar Python 3.11 o superior
    echo   2. Durante la instalacion, marcar: [X] Add Python to PATH
    echo.
    echo Descarga Python desde:
    echo   https://www.python.org/downloads/
    echo.
    echo Despues de instalar Python, ejecuta este .bat de nuevo.
    echo.
    echo ================================================================================
    pause
    exit
)

REM Mostrar que Python se esta usando
echo Detectando Python...
python --version
echo.

REM Verificar si fdb esta instalado
python -c "import fdb" >nul 2>&1
if errorlevel 1 (
    cls
    echo ================================================================================
    echo                    DEPENDENCIA NO INSTALADA: fdb
    echo ================================================================================
    echo.
    echo [ADVERTENCIA] El paquete 'fdb' no esta instalado.
    echo.
    echo 'fdb' es el driver de Python para conectarse a bases de datos Firebird.
    echo Sin este paquete, no podras usar este kit.
    echo.
    echo Deseas instalar 'fdb' ahora? (S/N)
    set /p instalar="Respuesta: "
    
    if /i "%instalar%"=="S" (
        echo.
        echo Instalando paquete 'fdb'...
        echo Esto puede tomar 1-2 minutos...
        echo.
        python -m pip install --user fdb
        echo.
        if errorlevel 1 (
            echo [ERROR] No se pudo instalar 'fdb'.
            echo Verifica tu conexion a internet e intenta de nuevo.
            pause
            exit
        ) else (
            echo.
            echo [OK] Paquete 'fdb' instalado correctamente.
            echo.
            echo Verificando instalacion...
            python -c "import fdb; print('fdb version:', fdb.__version__)"
            echo.
            if errorlevel 1 (
                echo [ADVERTENCIA] fdb se instalo pero no se puede importar.
                echo Intenta cerrar y abrir INICIAR.bat de nuevo.
                pause
                exit
            ) else (
                echo [OK] fdb funciona correctamente!
                echo.
                pause
                goto MENU
            )
        )
    ) else (
        echo.
        echo No se instalo 'fdb'.
        echo Para instalar manualmente, ejecuta:
        echo   python -m pip install --user fdb
        echo.
        pause
        exit
    )
)

REM Verificar que existe fbclient.dll
if not exist "fbclient.dll" (
    cls
    echo ================================================================================
    echo                      ARCHIVO FALTANTE: fbclient.dll
    echo ================================================================================
    echo.
    echo [ERROR] No se encontro el archivo fbclient.dll
    echo.
    echo Este archivo es necesario para conectarse a Firebird.
    echo Deberia estar incluido en esta carpeta.
    echo.
    echo Si falta, descarga Firebird 2.5.9 64-bit desde:
    echo   https://firebirdsql.org/en/firebird-2-5-9/
    echo.
    echo Y copia fbclient.dll a esta carpeta.
    echo.
    echo ================================================================================
    pause
    exit
)

REM Verificar que existe configuracion.ini
if not exist "configuracion.ini" (
    cls
    echo ================================================================================
    echo                   ARCHIVO FALTANTE: configuracion.ini
    echo ================================================================================
    echo.
    echo [ERROR] No se encontro el archivo configuracion.ini
    echo.
    echo Este archivo contiene la configuracion de conexion a Firebird.
    echo Deberia estar incluido en esta carpeta.
    echo.
    echo ================================================================================
    pause
    exit
)

:MENU
cls
echo ================================================================================
echo                    KIT DE CONEXION FIREBIRD - UNP
echo ================================================================================
echo.
echo Selecciona una opcion:
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
echo   7. Exportar toda la data (CSV para normalizacion)
echo.
echo   CONFIGURACION:
echo   8. Verificar instalacion
echo   9. Editar configuracion
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
if "%opcion%"=="8" goto VERIFICAR
if "%opcion%"=="9" goto EDITAR_CONFIG
if "%opcion%"=="0" goto SALIR

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

:EXTRAER_MODELO
cls
echo ================================================================================
echo                    EXTRAER MODELO ENTIDAD-RELACION
echo ================================================================================
echo.
echo Este proceso extraera:
echo   - Todas las tablas con sus columnas y tipos de datos
echo   - Primary Keys
echo   - Foreign Keys (relaciones entre tablas)
echo   - Indices
echo.
echo Generara archivos .txt y .sql listos para SQL Server
echo.
pause
echo.
python extraer_modelo_er.py
echo.
pause
goto MENU

:EXTRAER_TRIGGERS
cls
echo ================================================================================
echo                    EXTRAER TRIGGERS Y STORED PROCEDURES
echo ================================================================================
echo.
echo Este proceso extraera:
echo   - Todos los triggers con su codigo fuente
echo   - Todos los stored procedures con parametros
echo   - Codigo comentado para conversion a T-SQL
echo.
echo NOTA: Requerira conversion manual de sintaxis Firebird a SQL Server
echo.
pause
echo.
python extraer_triggers_procedures.py
echo.
pause
goto MENU

:EXPORTAR_DATA
cls
echo ================================================================================
echo                    EXPORTAR DATA COMPLETA (CSV)
echo ================================================================================
echo.
echo Este proceso exportara:
echo   - Todas las tablas a archivos CSV individuales
echo   - Todos los registros de cada tabla
echo   - Archivo de resumen con estadisticas
echo.
echo ADVERTENCIA: Puede tomar varios minutos dependiendo del tamano de la BD
echo.
set /p confirmar="Deseas continuar? (S/N): "
if /i not "%confirmar%"=="S" goto MENU
echo.
python exportar_data_completa.py
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
python --version
echo.
echo Verificando dependencias...
python -c "import fdb; print('[OK] fdb instalado - version:', fdb.__version__)" 2>nul || echo [ERROR] fdb NO instalado
echo.
echo Verificando fbclient.dll...
if exist "fbclient.dll" (
    echo [OK] fbclient.dll encontrado
) else (
    echo [ERROR] fbclient.dll NO encontrado
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

:EDITAR_CONFIG
cls
echo ================================================================================
echo                         EDITAR CONFIGURACION
echo ================================================================================
echo.
echo Abriendo configuracion.ini en el editor de texto...
echo.
notepad configuracion.ini
echo.
echo Configuracion guardada.
echo.
pause
goto MENU

:SALIR
cls
echo.
echo Saliendo...
timeout /t 1 >nul
exit
