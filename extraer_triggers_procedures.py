"""
Script para extraer Triggers y Stored Procedures de Firebird
Genera archivos con:
- Todos los triggers (código fuente completo)
- Todos los stored procedures (código fuente completo)
- Funciones UDF si existen

Uso: python extraer_triggers_procedures.py
Salida: triggers_procedures_TIMESTAMP.txt y triggers_procedures_TIMESTAMP.sql
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

def obtener_triggers(cur):
    """Obtiene todos los triggers de usuario"""
    cur.execute("""
        SELECT 
            RDB$TRIGGER_NAME,
            RDB$RELATION_NAME,
            RDB$TRIGGER_SEQUENCE,
            RDB$TRIGGER_TYPE,
            RDB$TRIGGER_SOURCE,
            RDB$TRIGGER_INACTIVE
        FROM RDB$TRIGGERS
        WHERE RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$RELATION_NAME, RDB$TRIGGER_SEQUENCE
    """)
    return cur.fetchall()

def obtener_procedures(cur):
    """Obtiene todos los stored procedures"""
    cur.execute("""
        SELECT 
            RDB$PROCEDURE_NAME,
            RDB$PROCEDURE_INPUTS,
            RDB$PROCEDURE_OUTPUTS,
            RDB$PROCEDURE_SOURCE,
            RDB$DESCRIPTION
        FROM RDB$PROCEDURES
        WHERE RDB$SYSTEM_FLAG = 0
        ORDER BY RDB$PROCEDURE_NAME
    """)
    return cur.fetchall()

def obtener_parametros_procedure(cur, proc_name):
    """Obtiene los parámetros de un stored procedure"""
    cur.execute("""
        SELECT 
            pp.RDB$PARAMETER_NAME,
            pp.RDB$PARAMETER_TYPE,
            f.RDB$FIELD_TYPE,
            f.RDB$FIELD_LENGTH,
            pp.RDB$PARAMETER_NUMBER
        FROM RDB$PROCEDURE_PARAMETERS pp
        JOIN RDB$FIELDS f ON pp.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE pp.RDB$PROCEDURE_NAME = ?
        ORDER BY pp.RDB$PARAMETER_TYPE, pp.RDB$PARAMETER_NUMBER
    """, (proc_name,))
    return cur.fetchall()

def tipo_trigger(tipo_num):
    """Convierte el tipo numérico de trigger a texto"""
    tipos = {
        1: 'BEFORE INSERT',
        2: 'AFTER INSERT',
        3: 'BEFORE UPDATE',
        4: 'AFTER UPDATE',
        5: 'BEFORE DELETE',
        6: 'AFTER DELETE',
        17: 'BEFORE INSERT OR UPDATE',
        18: 'AFTER INSERT OR UPDATE',
        25: 'BEFORE INSERT OR UPDATE OR DELETE',
        26: 'AFTER INSERT OR UPDATE OR DELETE',
        27: 'BEFORE INSERT OR DELETE',
        28: 'AFTER INSERT OR DELETE',
        113: 'BEFORE UPDATE OR DELETE',
        114: 'AFTER UPDATE OR DELETE'
    }
    return tipos.get(tipo_num, f'TIPO_{tipo_num}')

def tipo_firebird_simple(tipo_num):
    """Convierte tipo numérico a nombre simple"""
    tipos = {
        7: 'SMALLINT',
        8: 'INTEGER',
        10: 'FLOAT',
        12: 'DATE',
        13: 'TIME',
        14: 'CHAR',
        16: 'BIGINT',
        27: 'DOUBLE PRECISION',
        35: 'TIMESTAMP',
        37: 'VARCHAR',
        261: 'BLOB'
    }
    return tipos.get(tipo_num, f'TYPE_{tipo_num}')

def extraer_triggers_procedures():
    """Extrae todos los triggers y stored procedures"""
    print("=" * 100)
    print("EXTRACCIÓN DE TRIGGERS Y STORED PROCEDURES")
    print("=" * 100)
    
    con = conectar()
    cur = con.cursor()
    
    # Obtener triggers y procedures
    triggers = obtener_triggers(cur)
    procedures = obtener_procedures(cur)
    
    print(f"\n✓ Encontrados {len(triggers)} triggers")
    print(f"✓ Encontrados {len(procedures)} stored procedures")
    
    # Archivos de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_txt = f"triggers_procedures_{timestamp}.txt"
    archivo_sql = f"triggers_procedures_{timestamp}.sql"
    
    with open(archivo_txt, 'w', encoding='utf-8') as f_txt, \
         open(archivo_sql, 'w', encoding='utf-8') as f_sql:
        
        # ===== ENCABEZADO =====
        f_txt.write("=" * 100 + "\n")
        f_txt.write("TRIGGERS Y STORED PROCEDURES - BASE DE DATOS ACTIVOS UNP\n")
        f_txt.write(f"Extraído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_txt.write("=" * 100 + "\n\n")
        
        f_sql.write("-- ============================================================================\n")
        f_sql.write("-- TRIGGERS Y STORED PROCEDURES - BASE DE DATOS ACTIVOS UNP\n")
        f_sql.write(f"-- Extraído: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_sql.write("-- Conversión: Firebird -> SQL Server\n")
        f_sql.write("-- ============================================================================\n\n")
        
        # ===== TRIGGERS =====
        f_txt.write("=" * 100 + "\n")
        f_txt.write(f"TRIGGERS ({len(triggers)})\n")
        f_txt.write("=" * 100 + "\n\n")
        
        f_sql.write("-- ============================================================================\n")
        f_sql.write(f"-- TRIGGERS ({len(triggers)})\n")
        f_sql.write("-- ============================================================================\n\n")
        
        if triggers:
            tabla_actual = None
            for i, trg in enumerate(triggers, 1):
                nombre = trg[0].strip() if trg[0] else 'SIN_NOMBRE'
                tabla = trg[1].strip() if trg[1] else 'SIN_TABLA'
                secuencia = trg[2]
                tipo = tipo_trigger(trg[3])
                codigo = trg[4].strip() if trg[4] else '-- Sin código fuente'
                inactivo = trg[5]
                
                estado = " (INACTIVO)" if inactivo == 1 else ""
                
                print(f"  [{i}/{len(triggers)}] Procesando trigger {nombre}...")
                
                # Separador por tabla
                if tabla != tabla_actual:
                    tabla_actual = tabla
                    f_txt.write(f"\n{'─' * 100}\n")
                    f_txt.write(f"TABLA: {tabla}\n")
                    f_txt.write(f"{'─' * 100}\n\n")
                
                # TXT
                f_txt.write(f"TRIGGER: {nombre}{estado}\n")
                f_txt.write(f"Tipo: {tipo}\n")
                f_txt.write(f"Secuencia: {secuencia}\n")
                f_txt.write(f"\nCÓDIGO FIREBIRD:\n")
                f_txt.write("-" * 100 + "\n")
                f_txt.write(codigo + "\n")
                f_txt.write("-" * 100 + "\n\n")
                
                # SQL
                f_sql.write(f"-- Trigger: {nombre}{estado}\n")
                f_sql.write(f"-- Tabla: {tabla}\n")
                f_sql.write(f"-- Tipo: {tipo}\n")
                f_sql.write(f"-- Secuencia: {secuencia}\n")
                f_sql.write(f"-- NOTA: Requiere conversión manual de sintaxis Firebird a T-SQL\n")
                f_sql.write(f"\n/*\nCREATE TRIGGER [{nombre}]\n")
                f_sql.write(f"ON [{tabla}]\n")
                f_sql.write(f"{tipo.replace('BEFORE', 'INSTEAD OF').replace('AFTER', 'AFTER')}\n")
                f_sql.write(f"AS\nBEGIN\n")
                f_sql.write(f"    -- Código original Firebird:\n")
                for linea in codigo.split('\n'):
                    f_sql.write(f"    -- {linea}\n")
                f_sql.write(f"    \n    -- TODO: Convertir sintaxis Firebird a T-SQL\n")
                f_sql.write(f"END;\n*/\n")
                f_sql.write("GO\n\n")
        else:
            f_txt.write("No se encontraron triggers.\n\n")
            f_sql.write("-- No se encontraron triggers.\n\n")
        
        # ===== STORED PROCEDURES =====
        f_txt.write("\n" + "=" * 100 + "\n")
        f_txt.write(f"STORED PROCEDURES ({len(procedures)})\n")
        f_txt.write("=" * 100 + "\n\n")
        
        f_sql.write("\n-- ============================================================================\n")
        f_sql.write(f"-- STORED PROCEDURES ({len(procedures)})\n")
        f_sql.write("-- ============================================================================\n\n")
        
        if procedures:
            for i, proc in enumerate(procedures, 1):
                nombre = proc[0].strip() if proc[0] else 'SIN_NOMBRE'
                num_inputs = proc[1] if proc[1] else 0
                num_outputs = proc[2] if proc[2] else 0
                codigo = proc[3].strip() if proc[3] else '-- Sin código fuente'
                descripcion = proc[4].strip() if proc[4] else ''
                
                print(f"  [{i}/{len(procedures)}] Procesando procedure {nombre}...")
                
                # Obtener parámetros
                parametros = obtener_parametros_procedure(cur, nombre)
                params_in = [p for p in parametros if p[1] == 0]
                params_out = [p for p in parametros if p[1] == 1]
                
                # TXT
                f_txt.write(f"{'─' * 100}\n")
                f_txt.write(f"PROCEDURE: {nombre}\n")
                f_txt.write(f"{'─' * 100}\n")
                if descripcion:
                    f_txt.write(f"Descripción: {descripcion}\n")
                f_txt.write(f"Parámetros de entrada: {num_inputs}\n")
                f_txt.write(f"Parámetros de salida: {num_outputs}\n\n")
                
                if params_in:
                    f_txt.write("PARÁMETROS DE ENTRADA:\n")
                    for p in params_in:
                        param_nombre = p[0].strip()
                        param_tipo = tipo_firebird_simple(p[2])
                        f_txt.write(f"  - {param_nombre}: {param_tipo}\n")
                    f_txt.write("\n")
                
                if params_out:
                    f_txt.write("PARÁMETROS DE SALIDA:\n")
                    for p in params_out:
                        param_nombre = p[0].strip()
                        param_tipo = tipo_firebird_simple(p[2])
                        f_txt.write(f"  - {param_nombre}: {param_tipo}\n")
                    f_txt.write("\n")
                
                f_txt.write("CÓDIGO FIREBIRD:\n")
                f_txt.write("-" * 100 + "\n")
                f_txt.write(codigo + "\n")
                f_txt.write("-" * 100 + "\n\n\n")
                
                # SQL
                f_sql.write(f"-- Procedure: {nombre}\n")
                if descripcion:
                    f_sql.write(f"-- Descripción: {descripcion}\n")
                f_sql.write(f"-- Parámetros IN: {num_inputs}, OUT: {num_outputs}\n")
                f_sql.write(f"-- NOTA: Requiere conversión manual de sintaxis Firebird a T-SQL\n")
                f_sql.write(f"\n/*\nCREATE PROCEDURE [{nombre}]\n")
                
                # Parámetros
                if params_in:
                    f_sql.write("    -- Parámetros de entrada:\n")
                    for p in params_in:
                        param_nombre = p[0].strip()
                        param_tipo = tipo_firebird_simple(p[2])
                        f_sql.write(f"    @{param_nombre} {param_tipo},\n")
                
                if params_out:
                    f_sql.write("    -- Parámetros de salida:\n")
                    for p in params_out:
                        param_nombre = p[0].strip()
                        param_tipo = tipo_firebird_simple(p[2])
                        f_sql.write(f"    @{param_nombre} {param_tipo} OUTPUT,\n")
                
                f_sql.write("AS\nBEGIN\n")
                f_sql.write("    -- Código original Firebird:\n")
                for linea in codigo.split('\n'):
                    f_sql.write(f"    -- {linea}\n")
                f_sql.write("    \n    -- TODO: Convertir sintaxis Firebird a T-SQL\n")
                f_sql.write("END;\n*/\n")
                f_sql.write("GO\n\n")
        else:
            f_txt.write("No se encontraron stored procedures.\n\n")
            f_sql.write("-- No se encontraron stored procedures.\n\n")
    
    cur.close()
    con.close()
    
    print(f"\n✓ Triggers y Procedures extraídos exitosamente:")
    print(f"  - {archivo_txt}")
    print(f"  - {archivo_sql}")
    print("\n" + "=" * 100)

if __name__ == "__main__":
    try:
        extraer_triggers_procedures()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
