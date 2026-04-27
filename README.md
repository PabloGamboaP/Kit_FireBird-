# Kit de Conexión y Migración Firebird → SQL Server

Sistema portátil para consultar y migrar la base de datos Firebird de activos de la UNP a SQL Server.

---

## 📋 Inicio Rápido

### 1. Instalar Python
- Descargar: https://www.python.org/downloads/
- Durante instalación marcar: **[X] Add Python to PATH**

### 2. Configurar Conexión
```bash
# Copiar plantilla
copy configuracion.ini.example configuracion.ini

# Editar con tus credenciales
notepad configuracion.ini
```

**Configurar:**
- `password`: Solicitar al administrador de BD
- `database`: Ruta al archivo .gdb
- `host`: IP del servidor (vacío para modo local)

### 3. Ejecutar
```bash
# Doble clic en:
INICIAR.bat
```

**Primera vez:** Si falta `fdb`, usar opción 9 del menú para instalarlo.

---

## 📁 Estructura del Proyecto

```
Kit_FireBird/
├── INICIAR.bat                     # ⭐ Menú principal
├── MIGRACION_COMPLETA.bat         # Migración automática
├── verificar_dependencias.bat      # Verificar instalación
│
├── configuracion.ini.example       # Plantilla de configuración
├── configuracion.ini               # Tu configuración (NO SUBIR A GIT)
├── fbclient.dll                   # Cliente Firebird (NO ELIMINAR)
│
├── SCRIPTS DE CONSULTA:
│   ├── conexion_simple.py         # Probar conexión
│   ├── explorar_tablas.py         # Listar y explorar tablas
│   └── consultar_activos.py       # Consultar activos por cédula
│
├── SCRIPTS DE MIGRACIÓN:
│   ├── extraer_modelo_er.py           # Extraer esquema (PKs, FKs)
│   ├── extraer_triggers_procedures.py # Extraer triggers y SPs
│   ├── analizar_normalizacion.py      # Analizar problemas
│   ├── exportar_data_completa.py      # Exportar todo (pesado)
│   └── exportar_data_optimizada.py    # Exportar optimizado (recomendado)
│
└── migracion_output/               # Archivos generados (auto-creado)
    ├── modelo_er_*.txt|sql
    ├── triggers_procedures_*.txt|sql
    ├── analisis_normalizacion_*.txt
    └── data_export_*/
```

---

## 🎯 Menú Principal (INICIAR.bat)

### Consultas
1. **Probar conexión** - Verifica conectividad a Firebird
2. **Listar tablas** - Muestra todas las tablas con conteo
3. **Ver estructura** - Detalle de columnas de una tabla
4. **Consultar activos** - Activos por cédula

### Migración a SQL Server
5. **Extraer modelo ER** - Esquema completo (tablas, PKs, FKs, índices)
6. **Extraer triggers/SPs** - Lógica de negocio
7. **Exportar data completa** - Todo el historial (~12M registros en SALAJUSTES)
8. **Exportar data optimizada** ⭐ - Solo último período (~196K registros)

### Configuración
9. **Verificar instalación** - Estado de Python, fdb, archivos
A. **Instalar/Actualizar fdb** - Instalar dependencia manualmente
B. **Editar configuración** - Abrir configuracion.ini
0. **Salir**

---

## 🔄 Proceso de Migración a SQL Server

### Opción A: Migración Automática (Recomendado)

```bash
# Ejecutar todo en un solo paso
MIGRACION_COMPLETA.bat
```

Ejecuta automáticamente:
1. Extrae modelo ER
2. Extrae triggers y stored procedures
3. Analiza problemas de normalización
4. Exporta data completa

**Tiempo:** 10-20 minutos

### Opción B: Migración Manual

#### Paso 1: Extraer Esquema (Opción 5)
```bash
python extraer_modelo_er.py
```

**Genera:**
- `migracion_output/modelo_er_TIMESTAMP.txt` - Documentación
- `migracion_output/modelo_er_TIMESTAMP.sql` - Script SQL Server

**Contiene:**
- Tablas con columnas y tipos convertidos
- Primary Keys
- Foreign Keys
- Índices

#### Paso 2: Extraer Lógica (Opción 6)
```bash
python extraer_triggers_procedures.py
```

**Genera:**
- `migracion_output/triggers_procedures_TIMESTAMP.txt` - Documentación
- `migracion_output/triggers_procedures_TIMESTAMP.sql` - Plantillas T-SQL

**IMPORTANTE:** Requiere conversión manual de sintaxis Firebird → T-SQL

#### Paso 3: Analizar Normalización (Opcional)
```bash
python analizar_normalizacion.py
```

**Genera:**
- `migracion_output/analisis_normalizacion_TIMESTAMP.txt`

**Detecta:**
- Tablas sin Primary Key
- Columnas con >50% NULLs
- Posibles Foreign Keys faltantes

#### Paso 4: Exportar Datos (Opción 8 - Recomendado)
```bash
python exportar_data_optimizada.py
```

**Genera:**
- `migracion_output/data_export_optimizada_TIMESTAMP/`
  - Un CSV por tabla
  - SALAJUSTES solo con último período
  - `_RESUMEN.txt` con estadísticas

**Ventajas:**
- ✅ Mucho más rápido (minutos vs horas)
- ✅ Archivos más pequeños (MB vs GB)
- ✅ Suficiente para sistema actual
- ✅ SALAJUSTES: ~196K registros en lugar de ~12M

**¿Por qué optimizado?**
SALAJUSTES guarda historial mensual desde 2015. Para el sistema actual solo necesitas el último período (responsable actual, ubicación actual, depreciación actual).

---

## 📊 Tablas Principales

| Tabla | Descripción | Registros |
|-------|-------------|-----------|
| **MATERIAL** | Activos físicos (placa, descripción, serial, valor) | ~196K |
| **TERCEROS** | Personas (cédula, nombre, cargo) | ~6K |
| **SALAJUSTES** | Asignaciones mensuales (responsable, ubicación, depreciación) | ~12M |
| **SERVICIO** | Dependencias y servicios | ~124 |
| **GRUPMAT** | Grupos de materiales | ~252 |

**Relaciones:**
- MATERIAL → GRUPMAT (grupo del activo)
- SALAJUSTES → MATERIAL (qué activo)
- SALAJUSTES → TERCEROS (quién lo tiene)
- SALAJUSTES → SERVICIO (dónde está)

---

## 🔧 Configuración

### Modo Local (Base de datos en tu PC)
```ini
[FIREBIRD]
host = 
database = C:\temp\activos.gdb
user = SYSDBA
password = ****
charset = WIN1252
```

### Modo Remoto (Servidor Firebird)
```ini
[FIREBIRD]
host = 172.16.20.62
database = D:/DATOS TNS/ACTIVOS_UNP_COPIA.GDB
user = SYSDBA
password = *****
charset = WIN1252
port = 3050
```

---

## 🚀 Importar a SQL Server

### 1. Crear Base de Datos
```sql
CREATE DATABASE [ACTIVOS_UNP]
GO

USE [ACTIVOS_UNP]
GO
```

### 2. Ejecutar Script de Esquema
```sql
-- Ejecutar: migracion_output/modelo_er_TIMESTAMP.sql
-- Crea todas las tablas con PKs y FKs
```

### 3. Importar CSVs

**Opción A: SQL Server Management Studio**
1. Clic derecho en BD → Tasks → Import Flat File
2. Seleccionar CSV
3. Mapear columnas
4. Ejecutar

**Opción B: BULK INSERT**
```sql
-- Importar en orden de dependencias:
-- 1. Tablas sin FKs (TERCEROS, SERVICIO, GRUPMAT)
-- 2. Tablas con FKs (MATERIAL, SALAJUSTES)

BULK INSERT [MATERIAL]
FROM 'C:\ruta\migracion_output\data_export_optimizada_20260423\MATERIAL.csv'
WITH (
    FIRSTROW = 2,              -- Saltar encabezado
    FIELDTERMINATOR = ',',
    ROWTERMINATOR = '\n',
    CODEPAGE = '65001',        -- UTF-8
    TABLOCK
)
GO
```

### 4. Validar
```sql
-- Comparar conteos
SELECT 'MATERIAL' AS Tabla, COUNT(*) AS Registros FROM [MATERIAL]
UNION ALL
SELECT 'TERCEROS', COUNT(*) FROM [TERCEROS]
UNION ALL
SELECT 'SALAJUSTES', COUNT(*) FROM [SALAJUSTES]

-- Verificar integridad referencial
SELECT COUNT(*) AS Huerfanos
FROM [SALAJUSTES] s
LEFT JOIN [MATERIAL] m ON s.MATID = m.MATID
WHERE m.MATID IS NULL
-- Debe retornar 0
```

---

## 🔄 Conversión de Triggers/SPs

### Diferencias Firebird → T-SQL

| Firebird | SQL Server | Ejemplo |
|----------|------------|---------|
| `NEW.campo` | `INSERTED.campo` | En triggers INSERT/UPDATE |
| `OLD.campo` | `DELETED.campo` | En triggers UPDATE/DELETE |
| `\|\|` | `+` | Concatenación |
| `SUSPEND` | `RETURN` | En stored procedures |
| `FOR SELECT ... DO` | `CURSOR` + `WHILE` | Iteración |
| `GEN_ID(gen, 1)` | `NEXT VALUE FOR seq` | Secuencias |

### Ejemplo de Conversión

**Firebird:**
```sql
CREATE TRIGGER TRG_MATERIAL_BI FOR MATERIAL
BEFORE INSERT
AS
BEGIN
  IF (NEW.CODIGO IS NULL) THEN
    NEW.CODIGO = GEN_ID(GEN_MATERIAL_ID, 1);
  NEW.FECHA_CREACION = CURRENT_TIMESTAMP;
END
```

**SQL Server:**
```sql
CREATE TRIGGER [TRG_MATERIAL_BI]
ON [MATERIAL]
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO [MATERIAL] (CODIGO, FECHA_CREACION, ...)
    SELECT 
        ISNULL(CODIGO, NEXT VALUE FOR SEQ_MATERIAL_ID),
        GETDATE(),
        ...
    FROM INSERTED;
END
GO
```

---

## ⚠️ Problemas Comunes

### "Python no esta instalado"
**Solución:**
- Instalar Python desde https://www.python.org/downloads/
- Marcar **[X] Add Python to PATH**

### "Dependencia no instalada" (fdb)
**Solución:**
- Usar opción A del menú para instalar
- O ejecutar: `python -m pip install --user fdb`

### "Your user name and password are not defined"
**Solución:**
- Editar `configuracion.ini` con credenciales reales
- No usar placeholders como "TU_PASSWORD_AQUI"
- Usar opción B del menú para editar

### "unavailable database"
**Solución:**
- Verificar que el archivo .gdb existe en la ruta configurada
- Si es local: verificar ruta completa
- Si es remoto: verificar conectividad de red

### "No se encontraron activos para la cedula"
**Solución:**
- Verificar que la cédula existe
- Probar con cédula de ejemplo: `43875542`

---

## 📝 Consultas SQL Útiles

### Ver activos de una persona
```sql
SELECT 
    t.NIT AS CEDULA,
    t.NOMBRE,
    m.CODIGO AS PLACA,
    m.DESMAT AS DESCRIPCION,
    m.SERIAL
FROM MATERIAL m 
INNER JOIN SALAJUSTES sa ON m.MATID = sa.MATID
INNER JOIN TERCEROS t ON sa.RESPONSABLE = t.TERID
WHERE 
    t.NIT = '43875542'
    AND m.FEC_BAJA IS NULL
    AND sa.ANO = 2026
    AND sa.MES = '02'
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

## 🛠️ Requisitos Técnicos

### Mínimos
- Windows 7 o superior
- Python 3.11 o superior
- 50 MB de espacio en disco
- Conexión a internet (solo para instalar fdb)

### Recomendados
- Windows 10 o superior
- Python 3.12+
- Acceso a red UNP (para servidor remoto)

---

## 🔒 Seguridad

### Credenciales
- **NUNCA** subir `configuracion.ini` a repositorios públicos
- Solicitar credenciales al administrador de BD
- Usar usuario de solo lectura en producción

### Base de Datos
- Este kit opera en modo **SOLO LECTURA**
- No ejecuta DELETE, UPDATE o DROP
- Seguro para usar en producción

---

## 📞 Soporte

**Documentación:**
- Este README.md

**Verificación:**
- Ejecutar `verificar_dependencias.bat`
- Usar opción 9 del menú INICIAR.bat

**Contacto:**
- Equipo de desarrollo UNP
- Administrador de base de datos

---

## 📌 Notas Importantes

### SALAJUSTES
- Guarda historial mensual desde 2015
- ~12M registros totales
- Para migración usar **exportación optimizada** (opción 8)
- Solo último período es suficiente para sistema actual

### Charset
- Firebird usa **WIN1252**
- SQL Server usa **Latin1_General_CI_AS** o **UTF-8**
- CSVs se exportan en **UTF-8 con BOM**

### Archivos Generados
- Todos se guardan en `migracion_output/`
- Incluir timestamp en nombre
- Ignorados por Git (.gitignore)

---

**Versión:** 2.0  
**Fecha:** Abril 2026  
**Módulo:** SGAI - Almacén - Migración de Activos
