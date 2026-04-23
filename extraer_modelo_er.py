"""
Script para extraer el modelo Entidad-Relación de Firebird
Genera un archivo con:
- Todas las tablas y sus columnas
- Primary Keys
- Foreign Keys (relaciones)
- Índices
- Constraints

Uso: python extraer_modelo_er.py
Salida: modelo_er.txt y modelo_er.sql
"""

import fdb
import configparser
import os
import sys
from datetime import datetime
from validar_config import validar_o_salir

def cargar_configuracion():
    config = validar_o_salir()
    return config['FIREBIRD']

def conectar():
    cfg = cargar_configuracion()
    fbclient_path = os.path.join(os.path.dirname(__file__), 'fbclient.dll')
    
    try:
        return fdb.connect(
            host=cfg['host'],
            database=cfg['database'],
            user=cfg['user'],
            password=cfg['password'],
            charset=cfg['charset'],
            fb_library_name=fbclient_path
        )
    except Exception as e:
        print("\n" + "=" * 100)
        print("ERROR DE CONEXIÓN A FIREBIRD")
        print("=" * 100)
        print(f"\n❌ {str(e)}\n")
        print("POSIBLES CAUSAS:")
        print("  1. Usuario o password incorrectos")
        print("  2. El servidor Firebird no está corriendo")
        print("  3. No hay conectividad de red al servidor")
        print("  4. El archivo de base de datos no existe")
        print("  5. El puerto 3050 está bloqueado")
        print("\nSOLUCIÓN:")
        print("  - Verifica las credenciales en configuracion.ini")
        print("  - Usa la opción 9 del menú para editar la configuración")
        print("  - Usa la opción 1 del menú para probar la conexión")
        print("\n" + "=" * 100 + "\n")
        sys.exit(1)

def obtener_tablas(cur):
    """Obtiene todas las tablas de usuario"""
    cur.execute("""
        SELECT RDB$RELATION_NAME
        FROM RDB$RELATIONS 
        WHERE RDB$SYSTEM_FLAG = 0 
          AND RDB$VIEW_BLR IS NULL
        ORDER BY RDB$RELATION_NAME
    """)
    return [row[0].strip() for row in cur.fetchall()]

def obtener_columnas(cur, tabla):
    """Obtiene todas las columnas de una tabla con sus propiedades"""
    cur.execute("""
        SELECT 
            rf.RDB$FIELD_NAME,
            rf.RDB$FIELD_POSITION,
            f.RDB$FIELD_TYPE,
            f.RDB$FIELD_LENGTH,
            f.RDB$FIELD_PRECISION,
            f.RDB$FIELD_SCALE,
            rf.RDB$NULL_FLAG,
            rf.RDB$DEFAULT_SOURCE,
            f.RDB$FIELD_SUB_TYPE
        FROM RDB$RELATION_FIELDS rf
        JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE rf.RDB$RELATION_NAME = ?
        ORDER BY rf.RDB$FIELD_POSITION
    """, (tabla,))
    return cur.fetchall()

def obtener_primary_keys(cur, tabla):
    """Obtiene las primary keys de una tabla"""
    cur.execute("""
        SELECT 
            seg.RDB$FIELD_NAME
        FROM RDB$RELATION_CONSTRAINTS rc
        JOIN RDB$INDEX_SEGMENTS seg ON rc.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
        WHERE rc.RDB$RELATION_NAME = ?
          AND rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
        ORDER BY seg.RDB$FIELD_POSITION
    """, (tabla,))
    return [row[0].strip() for row in cur.fetchall()]

def obtener_foreign_keys(cur, tabla):
    """Obtiene las foreign keys de una tabla"""
    cur.execute("""
        SELECT 
            rc.RDB$CONSTRAINT_NAME,
            seg.RDB$FIELD_NAME,
            rc2.RDB$RELATION_NAME AS REFERENCED_TABLE,
            seg2.RDB$FIELD_NAME AS REFERENCED_FIELD
        FROM RDB$RELATION_CONSTRAINTS rc
        JOIN RDB$REF_CONSTRAINTS ref ON rc.RDB$CONSTRAINT_NAME = ref.RDB$CONSTRAINT_NAME
        JOIN RDB$RELATION_CONSTRAINTS rc2 ON ref.RDB$CONST_NAME_UQ = rc2.RDB$CONSTRAINT_NAME
        JOIN RDB$INDEX_SEGMENTS seg ON rc.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
        JOIN RDB$INDEX_SEGMENTS seg2 ON rc2.RDB$INDEX_NAME = seg2.RDB$INDEX_NAME
        WHERE rc.RDB$RELATION_NAME = ?
          AND rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
        ORDER BY rc.RDB$CONSTRAINT_NAME, seg.RDB$FIELD_POSITION
    """, (tabla,))
    return cur.fetchall()

def obtener_indices(cur, tabla):
    """Obtiene los índices de una tabla"""
    cur.execute("""
        SELECT 
            idx.RDB$INDEX_NAME,
            idx.RDB$UNIQUE_FLAG,
            seg.RDB$FIELD_NAME
        FROM RDB$INDICES idx
        JOIN RDB$INDEX_SEGMENTS seg ON idx.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
        WHERE idx.RDB$RELATION_NAME = ?
          AND idx.RDB$INDEX_NAME NOT LIKE 'RDB$%'
        ORDER BY idx.RDB$INDEX_NAME, seg.RDB$FIELD_POSITION
    """, (tabla,))
    return cur.fetchall()

def tipo_firebird_a_sql(tipo_num, longitud, precision, scale, subtipo):
    """Convierte tipos de datos Firebird a SQL Server"""
    tipos = {
        7: 'SMALLINT',
        8: 'INTEGER',
        10: 'FLOAT',
        12: 'DATE',
        13: 'TIME',
        14: f'CHAR({longitud})',
        16: 'BIGINT',
        27: 'DOUBLE PRECISION',
        35: 'TIMESTAMP',
        37: f'VARCHAR({longitud})',
        261: 'BLOB SUB_TYPE TEXT' if subtipo == 1 else 'BLOB'
    }
    
    tipo_base = tipos.get(tipo_num, f'UNKNOWN_TYPE_{tipo_num}')
    
    # Ajustar para SQL Server
    tipo_sql = tipo_base
    if tipo_base == 'DOUBLE PRECISION':
        tipo_sql = 'FLOAT'
    elif tipo_base == 'TIMESTAMP':
        tipo_sql = 'DATETIME'
    elif tipo_base.startswith('BLOB'):
        tipo_sql = 'NVARCHAR(MAX)' if 'TEXT' in tipo_base else 'VARBINARY(MAX)'
    elif tipo_base.startswith('CHAR'):
        tipo_sql = f'NCHAR({longitud})'
    elif tipo_base.startswith('VARCHAR'):
        tipo_sql = f'NVARCHAR({longitud})'
    
    return tipo_base, tipo_sql

def extraer_modelo():
    """Extrae el modelo completo de la base de datos"""
    print("=" * 100)
    print("EXTRACCIÓN DE MODELO ENTIDAD-RELACIÓN")
    print("=" * 100)
    
    con = conectar()
    cur = con.cursor()
    
    # Obtener todas las tablas
    tablas = obtener_tablas(cur)
    print(f"\n✓ Encontradas {len(tablas)} tablas")
    
    # Crear carpeta de salida
    carpeta_salida = "migracion_output"
    os.makedirs(carpeta_salida, exist_ok=True)
    
    # Archivos de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_txt = os.path.join(carpeta_salida, f"modelo_er_{timestamp}.txt")
    archivo_sql = os.path.join(carpeta_salida, f"modelo_er_{timestamp}.sql")
    
    with open(archivo_txt, 'w', encoding='utf-8') as f_txt, \
         open(archivo_sql, 'w', encoding='utf-8') as f_sql:
        
        # Encabezado
        f_txt.write("=" * 100 + "\n")
        f_txt.write("MODELO ENTIDAD-RELACIÓN - BASE DE DATOS ACTIVOS UNP\n")
        f_txt.write(f"Extraído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_txt.write("=" * 100 + "\n\n")
        
        f_sql.write("-- ============================================================================\n")
        f_sql.write("-- MODELO ENTIDAD-RELACIÓN - BASE DE DATOS ACTIVOS UNP\n")
        f_sql.write(f"-- Extraído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_sql.write("-- Conversión: Firebird -> SQL Server\n")
        f_sql.write("-- ============================================================================\n\n")
        
        # Diccionario para almacenar relaciones
        todas_fks = {}
        
        # Procesar cada tabla
        for i, tabla in enumerate(tablas, 1):
            print(f"  [{i}/{len(tablas)}] Procesando {tabla}...")
            
            # Obtener información
            columnas = obtener_columnas(cur, tabla)
            pks = obtener_primary_keys(cur, tabla)
            fks = obtener_foreign_keys(cur, tabla)
            indices = obtener_indices(cur, tabla)
            
            # Contar registros
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                num_registros = cur.fetchone()[0]
            except:
                num_registros = 0
            
            # Guardar FKs para el diagrama de relaciones
            if fks:
                todas_fks[tabla] = fks
            
            # ===== ARCHIVO TXT =====
            f_txt.write("=" * 100 + "\n")
            f_txt.write(f"TABLA: {tabla}\n")
            f_txt.write(f"Registros: {num_registros:,}\n")
            f_txt.write("=" * 100 + "\n\n")
            
            # Columnas
            f_txt.write("COLUMNAS:\n")
            f_txt.write("-" * 100 + "\n")
            f_txt.write(f"{'#':<4} {'NOMBRE':<30} {'TIPO FIREBIRD':<20} {'TIPO SQL SERVER':<20} {'NULL':<8} {'PK':<4}\n")
            f_txt.write("-" * 100 + "\n")
            
            for col in columnas:
                nombre = col[0].strip()
                tipo_fb, tipo_sql = tipo_firebird_a_sql(col[2], col[3], col[4], col[5], col[8])
                permite_null = 'NO' if col[6] == 1 else 'SÍ'
                es_pk = 'SÍ' if nombre in pks else ''
                
                f_txt.write(f"{col[1]+1:<4} {nombre:<30} {tipo_fb:<20} {tipo_sql:<20} {permite_null:<8} {es_pk:<4}\n")
            
            # Primary Keys
            if pks:
                f_txt.write(f"\nPRIMARY KEY: {', '.join(pks)}\n")
            
            # Foreign Keys
            if fks:
                f_txt.write("\nFOREIGN KEYS:\n")
                fk_actual = None
                for fk in fks:
                    if fk[0].strip() != fk_actual:
                        fk_actual = fk[0].strip()
                        f_txt.write(f"  - {fk[1].strip()} -> {fk[2].strip()}.{fk[3].strip()}\n")
            
            # Índices
            if indices:
                f_txt.write("\nÍNDICES:\n")
                idx_actual = None
                campos_idx = []
                for idx in indices:
                    if idx[0].strip() != idx_actual:
                        if idx_actual:
                            unique = " (UNIQUE)" if indices[0][1] == 1 else ""
                            f_txt.write(f"  - {idx_actual}: {', '.join(campos_idx)}{unique}\n")
                        idx_actual = idx[0].strip()
                        campos_idx = [idx[2].strip()]
                    else:
                        campos_idx.append(idx[2].strip())
                if idx_actual:
                    unique = " (UNIQUE)" if indices[-1][1] == 1 else ""
                    f_txt.write(f"  - {idx_actual}: {', '.join(campos_idx)}{unique}\n")
            
            f_txt.write("\n\n")
            
            # ===== ARCHIVO SQL =====
            f_sql.write(f"-- Tabla: {tabla} ({num_registros:,} registros)\n")
            f_sql.write(f"CREATE TABLE [{tabla}] (\n")
            
            # Columnas
            col_defs = []
            for col in columnas:
                nombre = col[0].strip()
                tipo_fb, tipo_sql = tipo_firebird_a_sql(col[2], col[3], col[4], col[5], col[8])
                permite_null = 'NOT NULL' if col[6] == 1 else 'NULL'
                
                col_def = f"    [{nombre}] {tipo_sql} {permite_null}"
                col_defs.append(col_def)
            
            f_sql.write(",\n".join(col_defs))
            
            # Primary Key
            if pks:
                pk_cols = ', '.join([f'[{pk}]' for pk in pks])
                f_sql.write(f",\n    CONSTRAINT [PK_{tabla}] PRIMARY KEY ({pk_cols})")
            
            f_sql.write("\n);\n")
            f_sql.write("GO\n\n")
        
        # ===== DIAGRAMA DE RELACIONES =====
        f_txt.write("=" * 100 + "\n")
        f_txt.write("DIAGRAMA DE RELACIONES (FOREIGN KEYS)\n")
        f_txt.write("=" * 100 + "\n\n")
        
        for tabla, fks in todas_fks.items():
            f_txt.write(f"{tabla}:\n")
            fk_actual = None
            for fk in fks:
                if fk[0].strip() != fk_actual:
                    fk_actual = fk[0].strip()
                    f_txt.write(f"  └─> {fk[2].strip()} ({fk[1].strip()} -> {fk[3].strip()})\n")
            f_txt.write("\n")
        
        # ===== FOREIGN KEYS EN SQL =====
        f_sql.write("-- ============================================================================\n")
        f_sql.write("-- FOREIGN KEYS\n")
        f_sql.write("-- ============================================================================\n\n")
        
        for tabla, fks in todas_fks.items():
            fk_actual = None
            for fk in fks:
                if fk[0].strip() != fk_actual:
                    fk_actual = fk[0].strip()
                    f_sql.write(f"ALTER TABLE [{tabla}]\n")
                    f_sql.write(f"    ADD CONSTRAINT [FK_{tabla}_{fk[2].strip()}]\n")
                    f_sql.write(f"    FOREIGN KEY ([{fk[1].strip()}])\n")
                    f_sql.write(f"    REFERENCES [{fk[2].strip()}] ([{fk[3].strip()}]);\n")
                    f_sql.write("GO\n\n")
    
    cur.close()
    con.close()
    
    print(f"\n✓ Modelo extraído exitosamente:")
    print(f"  - {archivo_txt}")
    print(f"  - {archivo_sql}")
    print("\n" + "=" * 100)

if __name__ == "__main__":
    try:
        extraer_modelo()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
