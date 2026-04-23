# Kit de Conexión a Firebird - Base de Datos Activos UNP

Sistema portátil para consultar y explorar la base de datos Firebird de activos de la UNP sin necesidad de instalaciones complejas.

---

## Inicio Rápido (3 pasos)

### 1. Instalar Python
- Descargar: https://www.python.org/downloads/
- Durante instalación marcar: **[X] Add Python to PATH**
- Tiempo: 5 minutos

### 2. Configurar conexión
- Copiar `configuracion.ini.example` a `configuracion.ini`
- Editar `configuracion.ini` con tus credenciales:
  - `password`: Solicitar al administrador de BD
  - `database`: Ruta al archivo .gdb
  - `host`: IP del servidor (o vacío para modo local)

### 3. Ejecutar INICIAR.bat
- Doble clic en: `INICIAR.bat`
- El script detecta automáticamente si falta `fdb`
- Te pregunta si deseas instalarlo (responde **S**)
- Listo!

**Después de la primera vez:** Solo doble clic en `INICIAR.bat`

**Verificar instalación:** Ejecuta `verificar_dependencias.bat` para verificar que todo está correcto

---

## Contenido del Kit

```
KIT_CONEXION_FIREBIRD/
├── README.md                       # Esta documentación
├── INICIAR.bat                     # Menu principal (USAR ESTE)
├── verificar_dependencias.bat      # Verificar instalación rápida
├── MIGRACION_COMPLETA.bat         # Migración automática completa
├── INICIAR_CON_VENV.bat           # Para desarrolladores con Django
├── configuracion.ini.example       # Plantilla de configuración (COPIAR Y RENOMBRAR)
├── configuracion.ini               # Tu configuración (NO SUBIR A GIT)
├── .gitignore                      # Protege credenciales
├── fbclient.dll                   # Cliente Firebird 64-bit (NO ELIMINAR)
│
├── CONSULTAS:
├── conexion_simple.py             # Script: Probar conexión
├── explorar_tablas.py             # Script: Listar y explorar tablas
├── consultar_activos.py           # Script: Consultar activos por cédula
│
└── MIGRACIÓN A SQL SERVER:
    ├── extraer_modelo_er.py           # Script: Extraer esquema (PKs, FKs)
    ├── extraer_triggers_procedures.py # Script: Extraer triggers y SPs
    ├── analizar_normalizacion.py      # Script: Analizar problemas de normalización
    └── exportar_data_completa.py      # Script: Exportar data a CSV
```

---

## Funcionalidades

### CONSULTAS

#### 1. Probar conexión a Firebird
Verifica que puedes conectarte a la base de datos y muestra información básica (número de tablas, registros).

#### 2. Listar todas las tablas
Muestra todas las tablas disponibles en la base de datos con el número de registros de cada una.

#### 3. Ver estructura de una tabla
Te pide el nombre de una tabla y muestra todas las columnas, tipos de datos y ejemplos de registros.

**Ejemplo:** `MATERIAL`, `TERCEROS`, `SALAJUSTES`

#### 4. Consultar activos por cédula
Te pide una cédula y muestra todos los activos asignados a esa persona (placa, descripción, serial, dependencia, valor).

**Ejemplo:** `43875542`

### MIGRACIÓN A SQL SERVER

#### 5. Extraer modelo Entidad-Relación
Extrae el esquema completo de la base de datos:
- Todas las tablas con columnas y tipos de datos
- Primary Keys (PKs)
- Foreign Keys (FKs) - relaciones entre tablas
- Índices y constraints
- Genera archivos `.txt` (documentación) y `.sql` (script SQL Server)

**Salida:** `modelo_er_TIMESTAMP.txt` y `modelo_er_TIMESTAMP.sql`

#### 6. Extraer Triggers y Stored Procedures
Extrae toda la lógica de negocio:
- Código fuente completo de todos los triggers
- Código fuente completo de todos los stored procedures
- Parámetros de entrada/salida
- Comentarios para conversión a T-SQL

**Salida:** `triggers_procedures_TIMESTAMP.txt` y `triggers_procedures_TIMESTAMP.sql`

**NOTA:** Requiere conversión manual de sintaxis Firebird a SQL Server

#### 7. Exportar toda la data (CSV)
Exporta todos los datos para normalización:
- Cada tabla se exporta a un archivo CSV individual
- Todos los registros de todas las tablas
- Archivo de resumen con estadísticas
- Formato UTF-8 con BOM para Excel

**Salida:** Carpeta `data_export_TIMESTAMP/` con archivos CSV

**ADVERTENCIA:** Puede tomar varios minutos dependiendo del tamaño de la BD

### CONFIGURACIÓN

#### 8. Verificar instalación
Verifica que Python, fdb, fbclient.dll y configuracion.ini estén correctamente instalados.

#### 9. Editar configuración
Abre `configuracion.ini` en Notepad para cambiar host, database, usuario o password.

---

## Configuración

### Modo Local (Base de datos en tu PC)

```ini
[FIREBIRD]
host = 
database = C:\temp\activos.gdb
user = SYSDBA
password = masterkey
charset = WIN1252
```

- `host` vacío = modo embedded (base de datos local)
- `database` = ruta al archivo .gdb en tu PC

### Modo Remoto (Servidor Firebird)

```ini
[FIREBIRD]
host = 172.16.20.62
database = D:/DATOS TNS/ACTIVOS_UNP_COPIA.GDB
user = SYSDBA
password = masterkey
charset = WIN1252
```

- `host` = IP del servidor Firebird
- `database` = ruta del archivo .gdb EN EL SERVIDOR
- Requiere acceso a la red UNP
- Puerto 3050 debe estar abierto

### Cómo editar
1. Usar opción 6 del menú (Editar configuración)
2. O abrir `configuracion.ini` con Notepad
3. Modificar los valores necesarios
4. Guardar y cerrar
5. Probar conexión (opción 1)

---

## Proceso de Migración a SQL Server

Este kit incluye herramientas para facilitar la migración de Firebird a SQL Server:

### Opción A: Migración Automática Completa (Recomendado)

Ejecutar `MIGRACION_COMPLETA.bat` para realizar todos los pasos automáticamente:

```bash
# Doble clic en:
MIGRACION_COMPLETA.bat
```

Este script ejecuta los 4 pasos en secuencia:
1. Extrae el modelo ER
2. Extrae triggers y stored procedures
3. Analiza problemas de normalización
4. Exporta toda la data a CSV

**Tiempo estimado:** 5-15 minutos dependiendo del tamaño de la BD

### Opción B: Migración Manual Paso a Paso

### Paso 1: Extraer el Modelo (Opción 5)
```bash
python extraer_modelo_er.py
```

**Genera:**
- `modelo_er_TIMESTAMP.txt` - Documentación legible del esquema
- `modelo_er_TIMESTAMP.sql` - Script SQL Server con CREATE TABLE y ALTER TABLE

**Contiene:**
- Definición de todas las tablas con tipos de datos convertidos
- Primary Keys
- Foreign Keys con relaciones
- Índices

### Paso 2: Extraer Lógica de Negocio (Opción 6)
```bash
python extraer_triggers_procedures.py
```

**Genera:**
- `triggers_procedures_TIMESTAMP.txt` - Documentación de triggers y SPs
- `triggers_procedures_TIMESTAMP.sql` - Código comentado para conversión

**Contiene:**
- Código fuente de todos los triggers
- Código fuente de todos los stored procedures
- Parámetros de entrada/salida

**IMPORTANTE:** La sintaxis Firebird debe convertirse manualmente a T-SQL:
- `NEW.campo` → `INSERTED.campo`
- `OLD.campo` → `DELETED.campo`
- `SUSPEND` → `RETURN`
- `FOR SELECT ... INTO ... DO` → `CURSOR` o `WHILE`

### Paso 3: Exportar Datos (Opción 7)
```bash
python exportar_data_completa.py
```

**Genera:**
- Carpeta `data_export_TIMESTAMP/` con archivos CSV
- Un CSV por cada tabla
- `_RESUMEN.txt` con estadísticas

**Importar a SQL Server:**
```sql
-- Opción 1: SQL Server Management Studio
-- Clic derecho en BD → Tasks → Import Flat File

-- Opción 2: BULK INSERT
BULK INSERT [nombre_tabla]
FROM 'C:\ruta\data_export_TIMESTAMP\TABLA.csv'
WITH (
    FIRSTROW = 2,
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    CODEPAGE = '65001'  -- UTF-8
);

-- Opción 3: bcp utility
bcp nombre_tabla in "TABLA.csv" -S servidor -d base_datos -T -c -t, -r\n
```

### Paso 4: Analizar Normalización (Opcional pero Recomendado)
```bash
python analizar_normalizacion.py
```

**Genera:**
- `analisis_normalizacion_TIMESTAMP.txt`

**Detecta:**
- Tablas sin Primary Key
- Columnas con >50% valores NULL
- Posibles Foreign Keys faltantes
- Sugerencias de normalización

### Paso 5: Validación Post-Migración

**Verificar conteos:**
```sql
-- En Firebird
SELECT COUNT(*) FROM MATERIAL;

-- En SQL Server
SELECT COUNT(*) FROM [MATERIAL];
```

**Verificar relaciones:**
```sql
-- Verificar que las FKs funcionan
SELECT 
    fk.name AS FK_Name,
    tp.name AS Parent_Table,
    tr.name AS Referenced_Table
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id;
```

**Verificar datos:**
```sql
-- Comparar algunos registros clave
SELECT TOP 10 * FROM [MATERIAL] ORDER BY CODIGO;
SELECT TOP 10 * FROM [TERCEROS] ORDER BY NIT;
```

### Consideraciones de Migración

**Tipos de datos:**
- `VARCHAR` Firebird → `NVARCHAR` SQL Server (soporte Unicode)
- `BLOB SUB_TYPE TEXT` → `NVARCHAR(MAX)`
- `BLOB` → `VARBINARY(MAX)`
- `DOUBLE PRECISION` → `FLOAT`
- `TIMESTAMP` → `DATETIME` o `DATETIME2`

**Charset:**
- Firebird usa `WIN1252`
- SQL Server usa `UTF-8` o `Latin1_General_CI_AS`
- Los CSV se exportan en UTF-8 con BOM

**Secuencias/Generadores:**
- Firebird: `GENERATOR` o `SEQUENCE`
- SQL Server: `IDENTITY` o `SEQUENCE`
- Revisar triggers que usan `GEN_ID()`

**Diferencias de sintaxis:**
- Firebird: `||` para concatenar → SQL Server: `+`
- Firebird: `SUBSTRING(str FROM pos FOR len)` → SQL Server: `SUBSTRING(str, pos, len)`
- Firebird: `COALESCE` → SQL Server: `COALESCE` o `ISNULL`

---

## Tablas Principales

| Tabla | Descripción |
|-------|-------------|
| MATERIAL | Activos físicos (CODIGO=placa, DESMAT=descripción, SERIAL, VALORCOMP) |
| TERCEROS | Personas (NIT=cédula, NOMBRE, CARGO) |
| SALAJUSTES | Asignaciones de activos a personas (relaciona MATERIAL con TERCEROS) |
| SERVICIO | Dependencias y servicios (CODSERVI, NOMSERVI) |
| GRUPMAT | Grupos de materiales (CODIGO, DESCRIP) |

---

## Consultas SQL Útiles

### Ver activos de una persona
```sql
SELECT 
    t.NIT AS CEDULA,
    t.NOMBRE AS NOMBRE_RESPONSABLE,
    m.CODIGO AS PLACA,
    m.DESMAT AS DESCRIPCION,
    m.SERIAL AS SERIAL
FROM MATERIAL m 
INNER JOIN SALAJUSTES sa ON m.MATID = sa.MATID
INNER JOIN TERCEROS t ON sa.RESPONSABLE = t.TERID
WHERE 
    t.NIT = '43875542'
    AND m.FEC_BAJA IS NULL
    AND sa.ANO = 2026
    AND sa.MES = '02'
```

### Ver estructura de una tabla
```sql
SELECT 
    RDB$FIELD_NAME AS COLUMNA,
    RDB$FIELD_TYPE AS TIPO
FROM RDB$RELATION_FIELDS
WHERE RDB$RELATION_NAME = 'MATERIAL'
ORDER BY RDB$FIELD_POSITION
```

### Contar activos por persona
```sql
SELECT 
    t.NIT,
    t.NOMBRE,
    COUNT(*) AS TOTAL_ACTIVOS
FROM MATERIAL m 
INNER JOIN SALAJUSTES sa ON m.MATID = sa.MATID
INNER JOIN TERCEROS t ON sa.RESPONSABLE = t.TERID
WHERE 
    m.FEC_BAJA IS NULL
    AND sa.ANO = 2026
    AND sa.MES = '02'
GROUP BY t.NIT, t.NOMBRE
ORDER BY TOTAL_ACTIVOS DESC
```

---

## Herramientas Gráficas (Opcional)

Si prefieres una interfaz gráfica para consultas SQL:

### IBExpert (Recomendado)
- Descarga: https://www.ibexpert.net/ibe/
- GUI completa para Firebird
- Editor SQL, explorador visual, generador de reportes

### FlameRobin
- Descarga: http://www.flamerobin.org/
- Open source, ligero
- Gratis, portable

### DBeaver
- Descarga: https://dbeaver.io/
- Universal (soporta muchas BD)
- Moderno, multiplataforma

---

## Problemas Comunes

### "Python no esta instalado"
**Solución:**
- Instalar Python desde https://www.python.org/downloads/
- Marcar **[X] Add Python to PATH** durante instalación
- Reiniciar CMD si ya estaba abierto

### "Dependencia no instalada" (fdb)
**Solución:**
- El .bat pregunta si deseas instalarla
- Responder **S**
- Esperar a que instale (1 minuto)
- El script continúa automáticamente al menú

**Nota:** Ya no es necesario cerrar y abrir el .bat de nuevo después de instalar fdb

### "unavailable database"
**Solución:**
- Verificar que el archivo .gdb existe en la ruta configurada
- Si es local: verificar que `C:\temp\activos.gdb` existe
- Si es remoto: verificar conectividad de red al servidor
- Usar opción 9 para editar la ruta en `configuracion.ini`

### "Your user name and password are not defined"
**Solución:**
- El archivo `configuracion.ini` tiene credenciales placeholder
- Editar `configuracion.ini` con credenciales reales:
  - `password`: Solicitar al administrador de BD (no usar "TU_PASSWORD_AQUI")
  - `user`: Típicamente "SYSDBA"
  - `database`: Ruta real al archivo .gdb
- Usar opción 9 del menú para editar la configuración
- Usar opción 1 del menú para probar la conexión

### "Error de conexion al servidor"
**Solución:**
- Verificar que el servidor Firebird está corriendo
- Verificar conectividad de red: `ping 172.16.20.62`
- Verificar que el puerto 3050 está abierto
- Verificar credenciales en `configuracion.ini`

### "No se encontraron activos para la cedula"
**Solución:**
- Verificar que la cédula existe en la base de datos
- Verificar que tiene activos asignados
- Probar con cédula de ejemplo: `43875542`

### Verificar que todo está bien instalado
**Solución:**
- Ejecutar `verificar_dependencias.bat`
- Revisa el reporte de cada componente
- Corrige los que aparezcan con [X]

---

## Requisitos

### Mínimos
- Windows 7 o superior
- Python 3.11 o superior
- Conexión a internet (solo para instalar fdb)
- 50 MB de espacio en disco

### Recomendados
- Windows 10 o superior
- Python 3.12
- Acceso a la red UNP (para servidor remoto)

---

## Conectividad

### Verificar acceso al servidor
```bash
# Windows
Test-NetConnection -ComputerName 172.16.20.62 -Port 3050

# Linux/Mac
nc -zv 172.16.20.62 3050
```

### Puerto requerido
- **Puerto:** 3050 (default Firebird)
- **Protocolo:** TCP
- **Firewall:** Debe estar abierto

---

## Seguridad

### Primera Configuración

1. Copiar `configuracion.ini.example` a `configuracion.ini`
2. Editar `configuracion.ini` con tus credenciales
3. Solicitar credenciales al administrador de BD

### Credenciales de Desarrollo
```
Usuario: SYSDBA
Password: (solicitar al administrador)
```

### Credenciales de Producción
Solicitar al administrador de base de datos:
- Usuario de solo lectura
- Password seguro
- Permisos limitados

**IMPORTANTE:** Nunca subir `configuracion.ini` a repositorios públicos

---

## Notas Importantes

- Base de datos en modo **SOLO LECTURA** (no modifica datos)
- Usar charset **WIN1252** siempre
- Incluir **fbclient.dll** en la misma carpeta (NO ELIMINAR)
- No compartir credenciales de producción
- No ejecutar DELETE, UPDATE o DROP en producción
- Firebird embedded NO soporta rutas UNC (`\\servidor\path`)
- Para servidor remoto, usar IP y ruta en el servidor

---

## Soporte

Para dudas o problemas:
1. Revisar esta documentación
2. Usar opción 5 (Verificar instalación)
3. Contactar al equipo de desarrollo del ecosistema UNP

---

## Versión

- **Versión:** 1.0
- **Fecha:** Abril 2026
- **Módulo:** SGAI - Almacén - Consulta de Activos
