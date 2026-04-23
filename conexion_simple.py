"""
Script simple para probar la conexión a Firebird
Uso: python conexion_simple.py
"""

import fdb
import configparser
import os
import sys
from validar_config import validar_o_salir

def cargar_configuracion():
    """Carga la configuración desde configuracion.ini"""
    config = validar_o_salir()
    return config['FIREBIRD']

def probar_conexion():
    """Prueba la conexión a Firebird y muestra información básica"""
    print("=" * 60)
    print("PRUEBA DE CONEXIÓN A FIREBIRD")
    print("=" * 60)
    
    # Cargar configuración
    cfg = cargar_configuracion()
    
    print(f"\nConfiguracion:")
    print(f"   Host: {cfg['host']}")
    print(f"   Database: {cfg['database']}")
    print(f"   User: {cfg['user']}")
    print(f"   Charset: {cfg['charset']}")
    
    # Verificar fbclient.dll
    fbclient_path = os.path.join(os.path.dirname(__file__), 'fbclient.dll')
    if not os.path.exists(fbclient_path):
        print("\n[ERROR] No se encontro fbclient.dll en esta carpeta")
        print("   Descarga Firebird 2.5.9 64-bit y copia fbclient.dll aqui")
        sys.exit(1)
    
    print(f"\n[OK] fbclient.dll encontrado: {fbclient_path}")
    
    # Intentar conexión
    print("\nConectando a Firebird...")
    
    try:
        con = fdb.connect(
            host=cfg['host'],
            database=cfg['database'],
            user=cfg['user'],
            password=cfg['password'],
            charset=cfg['charset'],
            fb_library_name=fbclient_path
        )
        
        print("[OK] CONEXION EXITOSA!")
        
        # Obtener información de la base de datos
        cur = con.cursor()
        
        # Contar tablas
        cur.execute("""
            SELECT COUNT(*) 
            FROM RDB$RELATIONS 
            WHERE RDB$SYSTEM_FLAG = 0 AND RDB$VIEW_BLR IS NULL
        """)
        num_tablas = cur.fetchone()[0]
        
        # Contar registros en MATERIAL
        cur.execute("SELECT COUNT(*) FROM MATERIAL")
        num_materiales = cur.fetchone()[0]
        
        # Contar registros en TERCEROS
        cur.execute("SELECT COUNT(*) FROM TERCEROS")
        num_terceros = cur.fetchone()[0]
        
        print(f"\nInformacion de la base de datos:")
        print(f"   Tablas: {num_tablas}")
        print(f"   Materiales (activos): {num_materiales:,}")
        print(f"   Terceros (personas): {num_terceros:,}")
        
        # Mostrar algunas tablas principales
        print(f"\nTablas principales:")
        cur.execute("""
            SELECT RDB$RELATION_NAME 
            FROM RDB$RELATIONS 
            WHERE RDB$SYSTEM_FLAG = 0 
              AND RDB$VIEW_BLR IS NULL
              AND RDB$RELATION_NAME IN ('MATERIAL', 'TERCEROS', 'SALAJUSTES', 'SERVICIO', 'GRUPMAT')
            ORDER BY RDB$RELATION_NAME
        """)
        
        for row in cur.fetchall():
            tabla = row[0].strip()
            cur.execute(f"SELECT COUNT(*) FROM {tabla}")
            count = cur.fetchone()[0]
            print(f"   - {tabla}: {count:,} registros")
        
        cur.close()
        con.close()
        
        print("\n" + "=" * 60)
        print("[OK] PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("\nPuedes usar los otros scripts para explorar la base de datos:")
        print("  - python explorar_tablas.py")
        print("  - python consultar_activos.py 43875542")
        
    except Exception as e:
        print(f"\n[ERROR] ERROR DE CONEXION:")
        print(f"   {str(e)}")
        print("\nPosibles soluciones:")
        print("   1. Verificar que el servidor Firebird esta corriendo")
        print("   2. Verificar conectividad de red al servidor")
        print("   3. Verificar credenciales en configuracion.ini")
        print("   4. Verificar que el puerto 3050 esta abierto")
        sys.exit(1)

if __name__ == "__main__":
    probar_conexion()
