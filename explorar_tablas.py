"""
Script para explorar la estructura de las tablas en Firebird
Uso: python explorar_tablas.py [nombre_tabla]
Ejemplos:
  python explorar_tablas.py              # Lista todas las tablas
  python explorar_tablas.py MATERIAL     # Muestra estructura de MATERIAL
"""

import fdb
import configparser
import os
import sys

def cargar_configuracion():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'configuracion.ini'))
    return config['FIREBIRD']

def conectar():
    cfg = cargar_configuracion()
    fbclient_path = os.path.join(os.path.dirname(__file__), 'fbclient.dll')
    
    return fdb.connect(
        host=cfg['host'],
        database=cfg['database'],
        user=cfg['user'],
        password=cfg['password'],
        charset=cfg['charset'],
        fb_library_name=fbclient_path
    )

def listar_tablas():
    """Lista todas las tablas de usuario en la base de datos"""
    print("=" * 80)
    print("TABLAS DISPONIBLES EN LA BASE DE DATOS")
    print("=" * 80)
    
    con = conectar()
    cur = con.cursor()
    
    cur.execute("""
        SELECT RDB$RELATION_NAME, RDB$DESCRIPTION
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
          AND RDB$VIEW_BLR IS NULL
        ORDER BY RDB$RELATION_NAME
    """)
    
    tablas = []
    for row in cur.fetchall():
        nombre = row[0].strip()
        tablas.append(nombre)
    
    print(f"\nTotal de tablas: {len(tablas)}\n")
    
    # Mostrar en columnas
    for i, tabla in enumerate(tablas, 1):
        # Contar registros
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cur.fetchone()[0]
            print(f"{i:3}. {tabla:30} ({count:,} registros)")
        except:
            print(f"{i:3}. {tabla:30} (error al contar)")
    
    cur.close()
    con.close()
    
    print("\n" + "=" * 80)
    print("Para ver la estructura de una tabla específica:")
    print("  python explorar_tablas.py NOMBRE_TABLA")
    print("=" * 80)

def mostrar_estructura_tabla(nombre_tabla):
    """Muestra la estructura de una tabla específica"""
    nombre_tabla = nombre_tabla.upper().strip()
    
    print("=" * 80)
    print(f"ESTRUCTURA DE LA TABLA: {nombre_tabla}")
    print("=" * 80)
    
    con = conectar()
    cur = con.cursor()
    
    # Verificar que la tabla existe
    cur.execute("""
        SELECT COUNT(*) 
        FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = ? AND RDB$SYSTEM_FLAG = 0
    """, (nombre_tabla,))
    
    if cur.fetchone()[0] == 0:
        print(f"\n❌ ERROR: La tabla '{nombre_tabla}' no existe")
        cur.close()
        con.close()
        return
    
    # Obtener columnas
    cur.execute("""
        SELECT 
            rf.RDB$FIELD_NAME AS field_name,
            f.RDB$FIELD_TYPE AS field_type,
            f.RDB$FIELD_LENGTH AS field_length,
            rf.RDB$NULL_FLAG AS null_flag,
            rf.RDB$DEFAULT_SOURCE AS default_value
        FROM RDB$RELATION_FIELDS rf
        JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE rf.RDB$RELATION_NAME = ?
        ORDER BY rf.RDB$FIELD_POSITION
    """, (nombre_tabla,))
    
    columnas = cur.fetchall()
    
    # Mapeo de tipos de datos Firebird
    tipos_firebird = {
        7: 'SMALLINT',
        8: 'INTEGER',
        10: 'FLOAT',
        12: 'DATE',
        13: 'TIME',
        14: 'CHAR',
        16: 'BIGINT',
        27: 'DOUBLE',
        35: 'TIMESTAMP',
        37: 'VARCHAR',
        261: 'BLOB'
    }
    
    print(f"\nColumnas ({len(columnas)}):\n")
    print(f"{'#':<4} {'NOMBRE':<30} {'TIPO':<15} {'LONGITUD':<10} {'NULL':<8}")
    print("-" * 80)
    
    for i, col in enumerate(columnas, 1):
        nombre = col[0].strip()
        tipo_num = col[1]
        longitud = col[2] if col[2] else ''
        permite_null = 'NO' if col[3] == 1 else 'SÍ'
        
        tipo = tipos_firebird.get(tipo_num, f'TIPO_{tipo_num}')
        
        print(f"{i:<4} {nombre:<30} {tipo:<15} {str(longitud):<10} {permite_null:<8}")
    
    # Contar registros
    cur.execute(f"SELECT COUNT(*) FROM {nombre_tabla}")
    total = cur.fetchone()[0]
    
    print("\n" + "-" * 80)
    print(f"Total de registros: {total:,}")
    
    # Mostrar algunos registros de ejemplo
    if total > 0:
        print(f"\nPrimeros 5 registros de ejemplo:")
        print("-" * 80)
        
        # Construir query con nombres de columnas
        columnas_nombres = [col[0].strip() for col in columnas[:10]]  # Primeras 10 columnas
        query = f"SELECT FIRST 5 {', '.join(columnas_nombres)} FROM {nombre_tabla}"
        
        try:
            cur.execute(query)
            rows = cur.fetchall()
            
            for row in rows:
                print("\nRegistro:")
                for i, valor in enumerate(row):
                    if i < len(columnas_nombres):
                        print(f"  {columnas_nombres[i]}: {valor}")
        except Exception as e:
            print(f"No se pudieron mostrar registros de ejemplo: {e}")
    
    cur.close()
    con.close()
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    try:
        if len(sys.argv) > 1:
            # Mostrar estructura de tabla específica
            mostrar_estructura_tabla(sys.argv[1])
        else:
            # Listar todas las tablas
            listar_tablas()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        sys.exit(1)
