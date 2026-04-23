# Kit de Conexión a Firebird - Base de Datos Activos UNP

Sistema portátil para consultar y explorar la base de datos Firebird de activos de la UNP sin necesidad de instalaciones complejas.

---

## Inicio Rápido (2 pasos)

### 1. Instalar Python
- Descargar: https://www.python.org/downloads/
- Durante instalación marcar: **[X] Add Python to PATH**
- Tiempo: 5 minutos

### 2. Ejecutar INICIAR.bat
- Doble clic en: `INICIAR.bat`
- El script detecta automáticamente si falta `fdb`
- Te pregunta si deseas instalarlo (responde **S**)
- Cerrar y ejecutar `INICIAR.bat` de nuevo
- Listo!

**Después de la primera vez:** Solo doble clic en `INICIAR.bat`

---

## Contenido del Kit

```
KIT_CONEXION_FIREBIRD/
├── README.md                    # Esta documentación
├── INICIAR.bat                  # Menu principal (USAR ESTE)
├── INICIAR_CON_VENV.bat        # Para desarrolladores con Django
├── configuracion.ini            # Configuración de conexión
├── fbclient.dll                # Cliente Firebird 64-bit (NO ELIMINAR)
├── conexion_simple.py          # Script: Probar conexión
├── explorar_tablas.py          # Script: Listar y explorar tablas
└── consultar_activos.py        # Script: Consultar activos por cédula
```

---

## Funcionalidades

### 1. Probar conexión a Firebird
Verifica que puedes conectarte a la base de datos y muestra información básica (número de tablas, registros).

### 2. Listar todas las tablas
Muestra todas las tablas disponibles en la base de datos con el número de registros de cada una.

### 3. Ver estructura de una tabla
Te pide el nombre de una tabla y muestra todas las columnas, tipos de datos y ejemplos de registros.

**Ejemplo:** `MATERIAL`, `TERCEROS`, `SALAJUSTES`

### 4. Consultar activos por cédula
Te pide una cédula y muestra todos los activos asignados a esa persona (placa, descripción, serial, dependencia, valor).

**Ejemplo:** `43875542`

### 5. Verificar instalación
Verifica que Python, fdb, fbclient.dll y configuracion.ini estén correctamente instalados.

### 6. Editar configuración
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
- Cerrar y ejecutar `INICIAR.bat` de nuevo

### "unavailable database"
**Solución:**
- Verificar que el archivo .gdb existe en la ruta configurada
- Si es local: verificar que `C:\temp\activos.gdb` existe
- Si es remoto: verificar conectividad de red al servidor
- Usar opción 6 para editar la ruta en `configuracion.ini`

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

### El .bat se cierra inmediatamente después de instalar
**Solución:**
- Esto es normal después de instalar fdb
- Simplemente ejecutar `INICIAR.bat` de nuevo
- Los cambios ya están aplicados

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

### Credenciales de Desarrollo
```
Usuario: SYSDBA
Password: masterkey
```
**ADVERTENCIA:** Solo para desarrollo/pruebas

### Credenciales de Producción
Solicitar al administrador de base de datos:
- Usuario de solo lectura
- Password seguro
- Permisos limitados

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
