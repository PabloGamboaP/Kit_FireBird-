"""
Script para consultar facturas de compra en Firebird
Busca activos asociados a una factura específica

Uso:
    python consultar_factura.py FC000983
    python consultar_factura.py 000983
"""
import sys
import os
import fdb
import configparser

def cargar_configuracion():
    """Carga la configuración desde configuracion.ini"""
    config = configparser.ConfigParser()
    
    if not os.path.exists('configuracion.ini'):
        print("ERROR: No se encontró el archivo 'configuracion.ini'")
        print("Copia 'configuracion.ini.example' a 'configuracion.ini' y configúralo")
        return None
    
    config.read('configuracion.ini', encoding='utf-8')
    
    if 'FIREBIRD' not in config:
        print("ERROR: Sección [FIREBIRD] no encontrada en configuracion.ini")
        return None
    
    return config['FIREBIRD']

def get_connection():
    """Obtiene conexión a Firebird"""
    try:
        fb_config = cargar_configuracion()
        if not fb_config:
            return None
        
        host = fb_config.get('HOST', '').strip()
        database = fb_config.get('DATABASE_PATH', '').strip()
        user = fb_config.get('USER', 'SYSDBA').strip()
        password = fb_config.get('PASSWORD', 'masterkey').strip()
        
        if not database:
            print("ERROR: DATABASE_PATH no configurado en configuracion.ini")
            return None
        
        FBCLIENT = os.path.join(os.path.dirname(__file__), "fbclient.dll")
        
        if not os.path.exists(FBCLIENT):
            print(f"ERROR: No se encontró fbclient.dll en {os.path.dirname(__file__)}")
            return None
        
        kwargs = dict(
            database=database,
            user=user,
            password=password,
            charset='WIN1252',
            fb_library_name=FBCLIENT,
        )
        
        if host:
            kwargs['host'] = host
        
        return fdb.connect(**kwargs)
        
    except Exception as e:
        print(f"ERROR conectando a Firebird: {str(e)}")
        return None

def buscar_factura(prefijo_numero):
    """Busca una factura por su prefijo y número"""
    con = get_connection()
    if not con:
        return
    
    try:
        cur = con.cursor()
        
        print("=" * 80)
        print(f"BUSCANDO FACTURA: {prefijo_numero}")
        print("=" * 80)
        print()
        
        print("Buscando en tabla MATERIAL (campo NROCOMPRA)...")
        query_material = """
        SELECT 
            m.MATID,
            m.CODIGO AS PLACA,
            m.DESMAT AS DESCRIPCION,
            m.NROCOMPRA AS FACTURA,
            m.FECCOMPRA AS FECHA_COMPRA,
            m.VALORCOMP AS VALOR,
            m.PROVEEDOR,
            t.NOMBRE AS NOMBRE_PROVEEDOR,
            gm.DESCRIP AS GRUPO
        FROM MATERIAL m
        LEFT JOIN TERCEROS t ON m.PROVEEDOR = t.TERID
        LEFT JOIN GRUPMAT gm ON m.GRUPMATID = gm.GRUPMATID
        WHERE m.NROCOMPRA LIKE ?
        ORDER BY m.FECCOMPRA DESC
        """
        
        cur.execute(query_material, [f'%{prefijo_numero}%'])
        resultados = cur.fetchall()
        
        if resultados:
            print(f"\nEncontrados {len(resultados)} activos con esta factura:")
            print("-" * 80)
            
            total_valor = 0
            for row in resultados:
                matid = row[0]
                placa = row[1] or 'N/A'
                descripcion = (row[2] or 'N/A')[:60]
                factura = row[3] or 'N/A'
                fecha = row[4] or 'N/A'
                valor = row[5] or 0
                proveedor_id = row[6]
                proveedor = (row[7] or 'N/A')[:40]
                grupo = (row[8] or 'N/A')[:30]
                
                total_valor += valor
                
                print(f"\nPlaca: {placa}")
                print(f"  Descripcion: {descripcion}")
                print(f"  Factura: {factura}")
                print(f"  Fecha compra: {fecha}")
                print(f"  Valor: ${valor:,.2f}")
                print(f"  Proveedor: {proveedor}")
                print(f"  Grupo: {grupo}")
            
            print()
            print("=" * 80)
            print(f"RESUMEN:")
            print(f"  Total de activos: {len(resultados)}")
            print(f"  Valor total: ${total_valor:,.2f}")
            print("=" * 80)
            
        else:
            print(f"\nNo se encontraron activos con la factura '{prefijo_numero}'")
            print()
            print("Intentando busqueda mas amplia...")
            
            # Buscar solo por el número sin prefijo
            numero_solo = prefijo_numero.replace('FC', '').replace('fc', '').replace('F', '').replace('f', '')
            cur.execute(query_material, [f'%{numero_solo}%'])
            resultados = cur.fetchall()
            
            if resultados:
                print(f"\nEncontrados {len(resultados)} activos con numero similar:")
                print("-" * 80)
                for row in resultados:
                    placa = row[1] or 'N/A'
                    factura = row[3] or 'N/A'
                    fecha = row[4] or 'N/A'
                    print(f"  Placa: {placa} - Factura: {factura} - Fecha: {fecha}")
            else:
                print("\nNo se encontraron resultados.")
                print()
                print("NOTA: Verifica que la base de datos tenga datos actualizados.")
                print("      Si la factura es reciente, puede que no este en esta copia.")
        
        cur.close()
        con.close()
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        if con:
            con.close()

def main():
    print("=" * 80)
    print("CONSULTA DE FACTURAS DE COMPRA")
    print("=" * 80)
    print()
    
    if len(sys.argv) > 1:
        prefijo = sys.argv[1]
    else:
        prefijo = input("Ingresa el numero de factura (ej: FC000983 o 000983): ").strip()
        if not prefijo:
            print("ERROR: Debe ingresar un numero de factura")
            return
    
    buscar_factura(prefijo)
    print()

if __name__ == '__main__':
    main()
