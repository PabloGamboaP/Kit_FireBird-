"""
Script para consultar activos asignados a una cédula
Uso: python consultar_activos.py <cedula>
Ejemplo: python consultar_activos.py 43875542
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

def consultar_activos(cedula):
    """Consulta los activos asignados a una cédula"""
    cfg = cargar_configuracion()
    ano = cfg.get('ano_consulta', '2026')
    mes = cfg.get('mes_consulta', '02')
    
    print("=" * 100)
    print(f"CONSULTA DE ACTIVOS - CÉDULA: {cedula}")
    print("=" * 100)
    
    con = conectar()
    cur = con.cursor()
    
    # Query principal
    query = """
        SELECT 
            t.NIT AS CEDULA,
            t.NOMBRE AS NOMBRE_RESPONSABLE,
            m.CODIGO AS PLACA_ACTIVO,
            m.DESMAT AS DESCRIPCION_ACTIVO,
            m.SERIAL AS SERIAL,
            se.nomservi AS GRUPO_DE_TRABAJO,
            COALESCE(se.codservi, 'SIN-CODIGO') AS CODIGO_SERVICIO,
            m.VALORCOMP AS VALOR_COMPRA,
            m.FECCOMPRA AS FECHA_COMPRA
        FROM MATERIAL m 
        INNER JOIN SALAJUSTES sa ON m.MATID = sa.MATID
        INNER JOIN TERCEROS t ON sa.RESPONSABLE = t.TERID
        LEFT JOIN SERVICIO se ON sa.SERVICIOID = se.SERVICIOID
        WHERE 
            t.NIT = ? 
            AND sa.ANO = ?
            AND sa.MES = ?
            AND m.FEC_BAJA IS NULL
            AND (se.nomservi IS NULL OR UPPER(se.nomservi) NOT LIKE '%BODEGA%')
        GROUP BY 
            t.NIT, t.NOMBRE, m.CODIGO, m.DESMAT, m.SERIAL, 
            se.nomservi, se.codservi, m.MATID, m.VALORCOMP, m.FECCOMPRA
        ORDER BY m.CODIGO
    """
    
    cur.execute(query, (cedula, int(ano), mes))
    rows = cur.fetchall()
    
    if not rows:
        print(f"\n[ERROR] No se encontraron activos para la cedula {cedula}")
        print(f"\nVerifica que:")
        print(f"   - La cedula existe en la tabla TERCEROS")
        print(f"   - Tiene activos asignados en el año {ano}, mes {mes}")
        print(f"   - Los activos no estan dados de baja")
        cur.close()
        con.close()
        return
    
    # Información del responsable
    responsable = rows[0]
    print(f"\nRESPONSABLE:")
    print(f"   Cedula: {responsable[0]}")
    print(f"   Nombre: {responsable[1]}")
    print(f"\nACTIVOS ASIGNADOS: {len(rows)}")
    print("\n" + "-" * 100)
    
    # Mostrar activos
    valor_total = 0
    for i, row in enumerate(rows, 1):
        placa = row[2]
        descripcion = row[3]
        serial = row[4] if row[4] else 'SIN SERIAL'
        grupo = row[5] if row[5] else 'SIN GRUPO'
        codigo = row[6]
        valor = row[7] if row[7] else 0
        fecha = row[8] if row[8] else 'N/A'
        
        valor_total += valor
        
        print(f"\n{i}. PLACA: {placa}")
        print(f"   Descripción: {descripcion}")
        print(f"   Serial: {serial}")
        print(f"   Dependencia: {codigo}")
        print(f"   Grupo: {grupo}")
        print(f"   Valor: ${valor:,.2f}")
        print(f"   Fecha compra: {fecha}")
        print("-" * 100)
    
    # Resumen
    print(f"\nRESUMEN:")
    print(f"   Total de activos: {len(rows)}")
    print(f"   Valor total: ${valor_total:,.2f}")
    
    cur.close()
    con.close()
    
    print("\n" + "=" * 100)
    print("[OK] CONSULTA COMPLETADA")
    print("=" * 100)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[ERROR] Debes proporcionar una cedula")
        print("\nUso: python consultar_activos.py <cedula>")
        print("Ejemplo: python consultar_activos.py 43875542")
        sys.exit(1)
    
    cedula = sys.argv[1]
    
    try:
        consultar_activos(cedula)
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        sys.exit(1)
