"""
Script para exportar data optimizada (solo último período de SALAJUSTES)
Uso: python exportar_data_optimizada.py
Salida: Carpeta migracion_output/data_export_optimizada_TIMESTAMP/ con archivos CSV
"""

import fdb
import configparser
import os
import sys
import csv
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
    """Obtiene los nombres de columnas de una tabla"""
    cur.execute("""
        SELECT rf.RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS rf
        WHERE rf.RDB$RELATION_NAME = ?
        ORDER BY rf.RDB$FIELD_POSITION
    """, (tabla,))
    return [row[0].strip() for row in cur.fetchall()]

def exportar_tabla(cur, tabla, columnas, carpeta_salida):
    """Exporta una tabla completa a CSV"""
    archivo_csv = os.path.join(carpeta_salida, f"{tabla}.csv")
    
    # Construir query
    cols_query = ', '.join([f'"{col}"' for col in columnas])
    query = f'SELECT {cols_query} FROM "{tabla}"'
    
    try:
        cur.execute(query)
        
        # Escribir CSV
        with open(archivo_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            
            # Encabezados
            writer.writerow(columnas)
            
            # Datos
            num_registros = 0
            for row in cur:
                # Convertir valores a strings seguros
                row_limpia = []
                for val in row:
                    if val is None:
                        row_limpia.append('')
                    elif isinstance(val, (bytes, bytearray)):
                        row_limpia.append('[BLOB]')
                    else:
                        row_limpia.append(str(val))
                
                writer.writerow(row_limpia)
                num_registros += 1
        
        return num_registros
    
    except Exception as e:
        print(f"    ⚠ Error exportando {tabla}: {str(e)}")
        return 0

def exportar_salajustes_optimizado(cur, carpeta_salida):
    """Exporta solo el último período de SALAJUSTES"""
    archivo_csv = os.path.join(carpeta_salida, "SALAJUSTES.csv")
    
    print("  Detectando último período...")
    
    # Obtener el último año y mes
    cur.execute("""
        SELECT FIRST 1 ANO, MES
        FROM SALAJUSTES
        ORDER BY ANO DESC, MES DESC
    """)
    
    resultado = cur.fetchone()
    if not resultado:
        print("    ⚠ SALAJUSTES está vacía")
        return 0
    
    ultimo_ano = resultado[0]
    ultimo_mes = resultado[1]
    
    print(f"  Último período: {ultimo_ano}-{ultimo_mes}")
    print(f"  Exportando solo registros del último período...")
    
    # Obtener columnas
    cur.execute("""
        SELECT rf.RDB$FIELD_NAME
        FROM RDB$RELATION_FIELDS rf
        WHERE rf.RDB$RELATION_NAME = 'SALAJUSTES'
        ORDER BY rf.RDB$FIELD_POSITION
    """)
    columnas = [row[0].strip() for row in cur.fetchall()]
    
    # Query optimizada: solo último período
    cols_query = ', '.join([f'"{col}"' for col in columnas])
    query = f"""
        SELECT {cols_query}
        FROM SALAJUSTES
        WHERE ANO = ? AND MES = ?
    """
    
    try:
        cur.execute(query, (ultimo_ano, ultimo_mes))
        
        # Escribir CSV
        with open(archivo_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_ALL)
            
            # Encabezados
            writer.writerow(columnas)
            
            # Datos
            num_registros = 0
            for row in cur:
                row_limpia = []
                for val in row:
                    if val is None:
                        row_limpia.append('')
                    elif isinstance(val, (bytes, bytearray)):
                        row_limpia.append('[BLOB]')
                    else:
                        row_limpia.append(str(val))
                
                writer.writerow(row_limpia)
                num_registros += 1
        
        return num_registros
    
    except Exception as e:
        print(f"    ⚠ Error exportando SALAJUSTES: {str(e)}")
        return 0

def exportar_data():
    """Exporta toda la data de forma optimizada"""
    print("=" * 100)
    print("EXPORTACIÓN DE DATA OPTIMIZADA")
    print("=" * 100)
    print("\nNOTA: SALAJUSTES se exportará solo con el último período")
    print("      (reduce de ~12M registros a ~196K registros)")
    print("=" * 100)
    
    con = conectar()
    cur = con.cursor()
    
    # Obtener todas las tablas
    tablas = obtener_tablas(cur)
    print(f"\n✓ Encontradas {len(tablas)} tablas para exportar")
    
    # Crear carpeta de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta_salida = os.path.join("migracion_output", f"data_export_optimizada_{timestamp}")
    os.makedirs(carpeta_salida, exist_ok=True)
    
    print(f"✓ Carpeta de salida: {carpeta_salida}\n")
    
    # Archivo de resumen
    archivo_resumen = os.path.join(carpeta_salida, "_RESUMEN.txt")
    
    with open(archivo_resumen, 'w', encoding='utf-8') as f_resumen:
        f_resumen.write("=" * 100 + "\n")
        f_resumen.write("RESUMEN DE EXPORTACIÓN OPTIMIZADA\n")
        f_resumen.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f_resumen.write("=" * 100 + "\n\n")
        f_resumen.write("NOTA: SALAJUSTES exportado solo con último período\n\n")
        
        total_registros = 0
        tablas_exportadas = 0
        
        # Exportar cada tabla
        for i, tabla in enumerate(tablas, 1):
            print(f"  [{i}/{len(tablas)}] Exportando {tabla}...", end=' ')
            
            # SALAJUSTES con lógica especial
            if tabla == 'SALAJUSTES':
                num_registros = exportar_salajustes_optimizado(cur, carpeta_salida)
            else:
                # Otras tablas normales
                columnas = obtener_columnas(cur, tabla)
                num_registros = exportar_tabla(cur, tabla, columnas, carpeta_salida)
            
            if num_registros > 0:
                print(f"✓ {num_registros:,} registros")
                f_resumen.write(f"{tabla:<40} {num_registros:>10,} registros\n")
                total_registros += num_registros
                tablas_exportadas += 1
            else:
                print("⚠ Sin datos o error")
                f_resumen.write(f"{tabla:<40} {'ERROR':>10}\n")
        
        f_resumen.write("\n" + "=" * 100 + "\n")
        f_resumen.write(f"TOTAL: {tablas_exportadas} tablas exportadas\n")
        f_resumen.write(f"TOTAL: {total_registros:,} registros exportados\n")
        f_resumen.write("=" * 100 + "\n")
    
    cur.close()
    con.close()
    
    print(f"\n{'=' * 100}")
    print(f"✓ Exportación completada:")
    print(f"  - Tablas exportadas: {tablas_exportadas}/{len(tablas)}")
    print(f"  - Total registros: {total_registros:,}")
    print(f"  - Carpeta: {carpeta_salida}")
    print(f"  - Resumen: {archivo_resumen}")
    print("=" * 100)

if __name__ == "__main__":
    try:
        exportar_data()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
