# Guía Completa de Migración: Firebird → SQL Server

## Índice
1. [Preparación](#preparación)
2. [Extracción de Esquema](#extracción-de-esquema)
3. [Extracción de Lógica](#extracción-de-lógica)
4. [Análisis de Normalización](#análisis-de-normalización)
5. [Exportación de Datos](#exportación-de-datos)
6. [Creación en SQL Server](#creación-en-sql-server)
7. [Conversión de Triggers/SPs](#conversión-de-triggersps)
8. [Importación de Datos](#importación-de-datos)
9. [Validación](#validación)
10. [Troubleshooting](#troubleshooting)

---

## Preparación

### Requisitos Previos

**En el servidor origen (Firebird):**
- Acceso a la base de datos Firebird
- Permisos de lectura en todas las tablas
- Espacio en disco para exportar datos (estimar 2x tamaño BD)

**En el servidor destino (SQL Server):**
- SQL Server 2016 o superior
- SQL Server Management Studio (SSMS)
- Permisos para crear base de datos
- Espacio en disco suficiente

**En tu PC:**
- Python 3.11+ instalado
- Paquete `fdb` instalado
- Este kit de migración completo

### Checklist Pre-Migración

- [ ] Backup completo de la base de datos Firebird
- [ ] Verificar conectividad a Firebird
- [ ] Verificar conectividad a SQL Server
- [ ] Estimar tiempo de migración (1-4 horas típicamente)
- [ ] Coordinar ventana de mantenimiento si es producción
- [ ] Notificar a usuarios del downtime

---

## Extracción de Esquema

### Paso 1: Ejecutar Extracción

```bash
# Opción A: Migración completa automática
MIGRACION_COMPLETA.bat

# Opción B: Solo esquema
python extraer_modelo_er.py
```

### Archivos Generados

**modelo_er_TIMESTAMP.txt:**
- Documentación legible del esquema
- Lista de tablas con columnas
- Primary Keys y Foreign Keys
- Índices

**modelo_er_TIMESTAMP.sql:**
- Script SQL Server listo para ejecutar
- CREATE TABLE para todas las tablas
- ALTER TABLE para Foreign Keys
- Tipos de datos ya convertidos

### Revisión del Esquema

**Verificar:**
1. Todas las tablas están presentes
2. Tipos de datos convertidos correctamente
3. Primary Keys definidas
4. Foreign Keys con referencias correctas

**Tipos de datos comunes:**

| Firebird | SQL Server | Notas |
|----------|------------|-------|
| VARCHAR(n) | NVARCHAR(n) | Unicode en SQL Server |
| CHAR(n) | NCHAR(n) | Unicode en SQL Server |
| INTEGER | INT | Mismo tamaño |
| BIGINT | BIGINT | Mismo tamaño |
| DOUBLE PRECISION | FLOAT | Precisión similar |
| TIMESTAMP | DATETIME2 | Mayor precisión en SQL Server |
| DATE | DATE | Mismo tipo |
| BLOB SUB_TYPE TEXT | NVARCHAR(MAX) | Para texto largo |
| BLOB | VARBINARY(MAX) | Para binarios |

---

## Extracción de Lógica

### Paso 2: Extraer Triggers y Stored Procedures

```bash
python extraer_triggers_procedures.py
```

### Archivos Generados

**triggers_procedures_TIMESTAMP.txt:**
- Código fuente completo de triggers
- Código fuente completo de stored procedures
- Parámetros de entrada/salida
- Documentación de cada objeto

**triggers_procedures_TIMESTAMP.sql:**
- Plantillas SQL Server comentadas
- Código Firebird original como referencia
- Estructura lista para conversión

### Inventario de Lógica

Crear una hoja de cálculo con:

| Nombre | Tipo | Tabla | Complejidad | Estado | Notas |
|--------|------|-------|-------------|--------|-------|
| TRG_MATERIAL_BI | Trigger | MATERIAL | Media | Pendiente | Calcula valores |
| SP_CONSULTAR_ACTIVOS | SP | - | Baja | Pendiente | Solo SELECT |

**Complejidad:**
- **Baja:** Solo SELECT, INSERT básicos
- **Media:** Lógica condicional, múltiples tablas
- **Alta:** Cursores, transacciones complejas, lógica de negocio crítica

---

## Análisis de Normalización

### Paso 3: Analizar Problemas

```bash
python analizar_normalizacion.py
```

### Archivo Generado

**analisis_normalizacion_TIMESTAMP.txt:**
- Tablas sin Primary Key
- Columnas con >50% NULLs
- Posibles Foreign Keys faltantes
- Recomendaciones de normalización

### Decisiones de Normalización

**Para cada problema detectado:**

1. **Tablas sin PK:**
   - ¿Existe una columna única natural?
   - ¿Necesitamos crear un ID autoincremental?
   - ¿Es una tabla de relación muchos-a-muchos?

2. **Columnas con NULLs excesivos:**
   - ¿Son datos realmente opcionales?
   - ¿Deberían estar en tabla separada?
   - ¿Podemos usar valores por defecto?

3. **FKs faltantes:**
   - ¿La columna referencia otra tabla?
   - ¿Hay datos huérfanos?
   - ¿Necesitamos limpiar datos antes?

---

## Exportación de Datos

### Paso 4: Exportar a CSV

```bash
python exportar_data_completa.py
```

### Carpeta Generada

**data_export_TIMESTAMP/:**
- Un archivo CSV por tabla
- `_RESUMEN.txt` con estadísticas
- Encoding UTF-8 con BOM (compatible Excel)

### Validación de Exportación

```bash
# Verificar que todos los archivos se crearon
dir data_export_TIMESTAMP\*.csv

# Revisar el resumen
type data_export_TIMESTAMP\_RESUMEN.txt
```

**Verificar:**
- [ ] Todas las tablas exportadas
- [ ] Conteo de registros coincide
- [ ] Archivos CSV se abren correctamente
- [ ] Caracteres especiales se ven bien

---

## Creación en SQL Server

### Paso 5: Crear Base de Datos

```sql
-- 1. Crear base de datos
CREATE DATABASE [ACTIVOS_UNP]
GO

USE [ACTIVOS_UNP]
GO

-- 2. Configurar collation (importante para caracteres especiales)
ALTER DATABASE [ACTIVOS_UNP] 
COLLATE Latin1_General_CI_AS
GO
```

### Paso 6: Ejecutar Script de Esquema

```sql
-- Abrir modelo_er_TIMESTAMP.sql en SSMS
-- Ejecutar en dos fases:

-- FASE 1: Crear tablas (sin FKs)
-- Ejecutar solo las secciones CREATE TABLE

-- FASE 2: Crear Foreign Keys
-- Ejecutar las secciones ALTER TABLE ... ADD CONSTRAINT
```

**Orden recomendado para FKs:**
1. Tablas maestras sin dependencias (ej: TERCEROS, SERVICIO)
2. Tablas con una FK (ej: MATERIAL)
3. Tablas con múltiples FKs (ej: SALAJUSTES)

### Verificación

```sql
-- Contar tablas creadas
SELECT COUNT(*) AS TotalTablas
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'

-- Listar Primary Keys
SELECT 
    t.TABLE_NAME,
    c.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS t
JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE c 
    ON t.CONSTRAINT_NAME = c.CONSTRAINT_NAME
WHERE t.CONSTRAINT_TYPE = 'PRIMARY KEY'
ORDER BY t.TABLE_NAME

-- Listar Foreign Keys
SELECT 
    fk.name AS FK_Name,
    tp.name AS Parent_Table,
    cp.name AS Parent_Column,
    tr.name AS Referenced_Table,
    cr.name AS Referenced_Column
FROM sys.foreign_keys fk
INNER JOIN sys.tables tp ON fk.parent_object_id = tp.object_id
INNER JOIN sys.tables tr ON fk.referenced_object_id = tr.object_id
INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id
INNER JOIN sys.columns cp ON fkc.parent_column_id = cp.column_id AND fkc.parent_object_id = cp.object_id
INNER JOIN sys.columns cr ON fkc.referenced_column_id = cr.column_id AND fkc.referenced_object_id = cr.object_id
ORDER BY tp.name, fk.name
```

---

## Conversión de Triggers/SPs

### Paso 7: Convertir Sintaxis

**Diferencias principales:**

| Firebird | SQL Server | Ejemplo |
|----------|------------|---------|
| `NEW.campo` | `INSERTED.campo` | En triggers INSERT/UPDATE |
| `OLD.campo` | `DELETED.campo` | En triggers UPDATE/DELETE |
| `||` | `+` | Concatenación de strings |
| `SUSPEND` | `RETURN` | En stored procedures |
| `FOR SELECT ... INTO ... DO` | `CURSOR` + `WHILE` | Iteración |
| `GEN_ID(gen, 1)` | `NEXT VALUE FOR seq` | Secuencias |
| `EXCEPTION nombre` | `THROW 50000, 'mensaje', 1` | Excepciones |

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
    
    INSERT INTO [MATERIAL] (
        CODIGO,
        FECHA_CREACION,
        -- otros campos
    )
    SELECT 
        ISNULL(CODIGO, NEXT VALUE FOR SEQ_MATERIAL_ID),
        GETDATE(),
        -- otros campos
    FROM INSERTED;
END
GO
```

### Testing de Triggers/SPs

```sql
-- Crear tabla de prueba
SELECT TOP 0 * INTO [MATERIAL_TEST] FROM [MATERIAL]

-- Probar trigger en tabla de prueba
INSERT INTO [MATERIAL_TEST] (DESMAT, SERIAL)
VALUES ('Prueba', 'TEST001')

-- Verificar resultado
SELECT * FROM [MATERIAL_TEST]

-- Limpiar
DROP TABLE [MATERIAL_TEST]
```

---

## Importación de Datos

### Paso 8: Importar CSVs

**Opción A: SQL Server Management Studio (Recomendado para pocas tablas)**

1. Clic derecho en base de datos
2. Tasks → Import Flat File
3. Seleccionar CSV
4. Mapear columnas
5. Ejecutar

**Opción B: BULK INSERT (Recomendado para muchas tablas)**

```sql
-- Deshabilitar constraints temporalmente
ALTER TABLE [MATERIAL] NOCHECK CONSTRAINT ALL
GO

-- Importar
BULK INSERT [MATERIAL]
FROM 'C:\ruta\data_export_20260423_120000\MATERIAL.csv'
WITH (
    FIRSTROW = 2,              -- Saltar encabezado
    FIELDTERMINATOR = ',',     -- Separador de campos
    ROWTERMINATOR = '\n',      -- Separador de filas
    CODEPAGE = '65001',        -- UTF-8
    TABLOCK,                   -- Optimización
    KEEPNULLS                  -- Preservar NULLs
)
GO

-- Rehabilitar constraints
ALTER TABLE [MATERIAL] CHECK CONSTRAINT ALL
GO

-- Verificar conteo
SELECT COUNT(*) FROM [MATERIAL]
```

**Opción C: Script PowerShell para importar todas las tablas**

```powershell
# importar_todas.ps1
$servidor = "localhost"
$basedatos = "ACTIVOS_UNP"
$carpeta = "C:\ruta\data_export_20260423_120000"

Get-ChildItem "$carpeta\*.csv" | ForEach-Object {
    $tabla = $_.BaseName
    
    if ($tabla -ne "_RESUMEN") {
        Write-Host "Importando $tabla..."
        
        $sql = @"
        BULK INSERT [$tabla]
        FROM '$($_.FullName)'
        WITH (
            FIRSTROW = 2,
            FIELDTERMINATOR = ',',
            ROWTERMINATOR = '\n',
            CODEPAGE = '65001',
            TABLOCK,
            KEEPNULLS
        )
"@
        
        Invoke-Sqlcmd -ServerInstance $servidor -Database $basedatos -Query $sql
        
        Write-Host "✓ $tabla importado" -ForegroundColor Green
    }
}
```

### Orden de Importación

**Importante:** Importar en orden de dependencias

1. **Tablas sin FKs:**
   - TERCEROS
   - SERVICIO
   - GRUPMAT

2. **Tablas con 1 FK:**
   - MATERIAL (depende de GRUPMAT)

3. **Tablas con múltiples FKs:**
   - SALAJUSTES (depende de MATERIAL, TERCEROS, SERVICIO)

---

## Validación

### Paso 9: Validar Migración

**1. Validar Conteos**

```sql
-- Comparar conteos tabla por tabla
-- En Firebird:
SELECT 'MATERIAL' AS TABLA, COUNT(*) AS REGISTROS FROM MATERIAL
UNION ALL
SELECT 'TERCEROS', COUNT(*) FROM TERCEROS
UNION ALL
SELECT 'SALAJUSTES', COUNT(*) FROM SALAJUSTES

-- En SQL Server:
SELECT 'MATERIAL' AS TABLA, COUNT(*) AS REGISTROS FROM [MATERIAL]
UNION ALL
SELECT 'TERCEROS', COUNT(*) FROM [TERCEROS]
UNION ALL
SELECT 'SALAJUSTES', COUNT(*) FROM [SALAJUSTES]
```

**2. Validar Integridad Referencial**

```sql
-- Verificar que no hay registros huérfanos
SELECT 
    m.CODIGO,
    m.DESMAT
FROM [MATERIAL] m
LEFT JOIN [GRUPMAT] g ON m.GRUPMATID = g.GRUPMATID
WHERE g.GRUPMATID IS NULL
  AND m.GRUPMATID IS NOT NULL

-- Debe retornar 0 registros
```

**3. Validar Datos Críticos**

```sql
-- Comparar algunos registros específicos
-- En Firebird:
SELECT * FROM MATERIAL WHERE CODIGO = 'ACT001'

-- En SQL Server:
SELECT * FROM [MATERIAL] WHERE CODIGO = 'ACT001'

-- Verificar que los valores coinciden
```

**4. Validar Consultas de Negocio**

```sql
-- Ejecutar consultas típicas del negocio
-- Ejemplo: Activos por persona
SELECT 
    t.NIT,
    t.NOMBRE,
    COUNT(*) AS TOTAL_ACTIVOS
FROM [MATERIAL] m 
INNER JOIN [SALAJUSTES] sa ON m.MATID = sa.MATID
INNER JOIN [TERCEROS] t ON sa.RESPONSABLE = t.TERID
WHERE m.FEC_BAJA IS NULL
GROUP BY t.NIT, t.NOMBRE
ORDER BY TOTAL_ACTIVOS DESC

-- Comparar resultados con Firebird
```

**5. Validar Performance**

```sql
-- Ejecutar consultas pesadas y medir tiempo
SET STATISTICS TIME ON
SET STATISTICS IO ON

-- Tu consulta aquí
SELECT ...

SET STATISTICS TIME OFF
SET STATISTICS IO OFF
```

---

## Troubleshooting

### Problemas Comunes

**1. Error: "Cannot insert NULL into column"**

```sql
-- Solución: Verificar que la columna permite NULL
ALTER TABLE [MATERIAL]
ALTER COLUMN [SERIAL] NVARCHAR(50) NULL
```

**2. Error: "Violation of PRIMARY KEY constraint"**

```sql
-- Solución: Verificar duplicados en CSV
SELECT CODIGO, COUNT(*)
FROM [MATERIAL]
GROUP BY CODIGO
HAVING COUNT(*) > 1

-- Limpiar duplicados antes de importar
```

**3. Error: "The FOREIGN KEY constraint ... conflicts"**

```sql
-- Solución: Importar tablas en orden correcto
-- O deshabilitar FKs temporalmente
ALTER TABLE [MATERIAL] NOCHECK CONSTRAINT ALL
-- Importar
ALTER TABLE [MATERIAL] CHECK CONSTRAINT ALL
```

**4. Caracteres especiales se ven mal**

```sql
-- Solución: Verificar collation
SELECT DATABASEPROPERTYEX('ACTIVOS_UNP', 'Collation')

-- Cambiar si es necesario
ALTER DATABASE [ACTIVOS_UNP]
COLLATE Latin1_General_CI_AS
```

**5. Importación muy lenta**

```sql
-- Solución: Optimizaciones
-- 1. Deshabilitar índices temporalmente
ALTER INDEX ALL ON [MATERIAL] DISABLE

-- 2. Importar

-- 3. Reconstruir índices
ALTER INDEX ALL ON [MATERIAL] REBUILD
```

---

## Checklist Final

### Post-Migración

- [ ] Todos los conteos coinciden
- [ ] No hay registros huérfanos
- [ ] Consultas de negocio funcionan
- [ ] Performance es aceptable
- [ ] Triggers funcionan correctamente
- [ ] Stored procedures funcionan correctamente
- [ ] Backup de SQL Server creado
- [ ] Documentación actualizada
- [ ] Usuarios notificados
- [ ] Aplicaciones apuntando a nueva BD

### Rollback Plan

Si algo sale mal:

1. Mantener Firebird activo durante período de prueba
2. Tener backup de SQL Server antes de migración
3. Documentar problemas encontrados
4. Plan B: volver a Firebird temporalmente

---

## Recursos Adicionales

**Documentación:**
- [SQL Server Migration Assistant](https://docs.microsoft.com/en-us/sql/ssma/)
- [Firebird to SQL Server Migration Guide](https://firebirdsql.org/)

**Herramientas:**
- SQL Server Management Studio (SSMS)
- Azure Data Studio
- DBConvert for Firebird & SQL Server

**Soporte:**
- Equipo de desarrollo UNP
- DBA SQL Server
- Documentación de este kit

---

**Versión:** 1.0  
**Fecha:** Abril 2026  
**Autor:** Equipo de Desarrollo UNP
