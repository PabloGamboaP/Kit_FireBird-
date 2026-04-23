"""
Script para analizar la base de datos y detectar problemas de normalización
Genera un reporte con:
- Tablas sin Primary Key
- Columnas con valores NULL excesivos
- Posibles duplicados
- Tablas relacionadas sin Foreign Keys
- Sugerencias de normalización

Uso: python analizar_normalizacion.py
Salida: analisis_normalizacion_TIMESTAMP.txt
"""

import fdb
import configparser
import os
import sys
from datetime import datetime
from collections import defaultdict
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

def obtener_primary_keys(cur, tabla):
    """Obtiene las primary keys de una tabla"""
    cur.execute("""
        SELECT seg.RDB$FIELD_NAME
        FROM RDB$RELATION_CONSTRAINTS rc
        JOIN RDB$INDEX_SEGMENTS seg ON rc.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
        WHERE rc.RDB$RELATION_NAME = ?
          AND rc.RDB$CONSTRAINT_TYPE = 'PRIMARY KEY'
    """, (tabla,))
    return [row[0].strip() for row in cur.fetchall()]

def obtener_foreign_keys(cur, tabla):
    """Obtiene las foreign keys de una tabla"""
    cur.execute("""
        SELECT 
            seg.RDB$FIELD_NAME,
            rc2.RDB$RELATION_NAME AS REFERENCED_TABLE
        FROM RDB$RELATION_CONSTRAINTS rc
        JOIN RDB$REF_CONSTRAINTS ref ON rc.RDB$CONSTRAINT_NAME = ref.RDB$CONSTRAINT_NAME
        JOIN RDB$RELATION_CONSTRAINTS rc2 ON ref.RDB$CONST_NAME_UQ = rc2.RDB$CONSTRAINT_NAME
        JOIN RDB$INDEX_SEGMENTS seg ON rc.RDB$INDEX_NAME = seg.RDB$INDEX_NAME
        WHERE rc.RDB$RELATION_NAME = ?
          AND rc.RDB$CONSTRAINT_TYPE = 'FOREIGN KEY'
    """, (tabla,))
    return cur.fetchall()

def obtener_columnas(cur, tabla):
    """Obtiene columnas con información de nullabilidad"""
    cur.execute("""
        SELECT 
            rf.RDB$FIELD_NAME,
            rf.RDB$NULL_FLAG,
            f.RDB$FIELD_TYPE
        FROM RDB$RELATION_FIELDS rf
        JOIN RDB$FIELDS f ON rf.RDB$FIELD_SOURCE = f.RDB$FIELD_NAME
        WHERE rf.RDB$RELATION_NAME = ?
        ORDER BY rf.RDB$FIELD_POSITION
    """, (tabla,))
    return cur.fetchall()

def analizar_nulls(cur, tabla, columnas):
    """Analiza el porcentaje de NULLs en cada columna"""
    try:
        cur.execute(f"SELECT COUNT(*) FROM {tabla}")
        total = cur.fetchone()[0]
        
        if total == 0:
            return []
        
        problemas = []
        for col in columnas:
            nombre = col[0].strip()
            permite_null = col[1] != 1
            
            if permite_null:
                try:
                    cur.execute(f'SELECT COUNT(*) FROM {tabla} WHERE "{nombre}" IS NULL')
                    nulls = cur.fetchone()[0]
                    porcentaje = (nulls / total) * 100
                    
                    if porcentaje > 50:  # Más del 50% son NULL
                        problemas.append({
                            'columna': nombre,
                            'nulls': nulls,
                            'total': total,
                            'porcentaje': porcentaje
                        })
                except:
                    pass
        
        return problemas
    except:
        return []

def buscar_columnas_id_sin_fk(cur, tabla, columnas, fks):
    """Busca columnas que parecen IDs pero no tienen FK"""
    fk_cols = [fk[0].strip() for fk in fks]
    posibles_fks = []
    
    for col in columnas:
        nombre = col[0].strip()
        
        # Buscar columnas que terminen en ID o parezcan referencias
        if (nombre.endswith('ID') or nombre.endswith('_ID') or 
            nombre.startswith('COD') or nombre.startswith('ID_')):
            
            if nombre not in fk_cols:
                posibles_fks.append(nombre)
    
    return posibles_fks

def analizar_normalizacion():
    """Analiza la base de datos para detectar problemas de normalización"""
    print("=" * 100)
    print("ANÁLISIS DE NORMALIZACIÓN")
    print("=" * 100)
    
    con = conectar()
    cur = con.cursor()
    
    tablas = obtener_tablas(cur)
    print(f"\n✓ Analizando {len(tablas)} tablas...\n")
    
    # Archivo de salida
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archivo_salida = f"analisis_normalizacion_{timestamp}.txt"
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("ANÁLISIS DE NORMALIZACIÓN - BASE DE DATOS ACTIVOS UNP\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 100 + "\n\n")
        
        # Contadores
        tablas_sin_pk = []
        tablas_con_nulls_excesivos = []
        tablas_con_posibles_fks = []
        
        # Analizar cada tabla
        for i, tabla in enumerate(tablas, 1):
            print(f"  [{i}/{len(tablas)}] Analizando {tabla}...")
            
            pks = obtener_primary_keys(cur, tabla)
            fks = obtener_foreign_keys(cur, tabla)
            columnas = obtener_columnas(cur, tabla)
            
            # Contar registros
            try:
                cur.execute(f"SELECT COUNT(*) FROM {tabla}")
                num_registros = cur.fetchone()[0]
            except:
                num_registros = 0
            
            problemas_tabla = []
            
            # 1. Verificar Primary Key
            if not pks:
                tablas_sin_pk.append(tabla)
                problemas_tabla.append("⚠ NO TIENE PRIMARY KEY")
            
            # 2. Analizar NULLs excesivos
            problemas_nulls = analizar_nulls(cur, tabla, columnas)
            if problemas_nulls:
                tablas_con_nulls_excesivos.append((tabla, problemas_nulls))
                problemas_tabla.append(f"⚠ {len(problemas_nulls)} columnas con >50% NULLs")
            
            # 3. Buscar posibles FKs faltantes
            posibles_fks = buscar_columnas_id_sin_fk(cur, tabla, columnas, fks)
            if posibles_fks:
                tablas_con_posibles_fks.append((tabla, posibles_fks))
                problemas_tabla.append(f"⚠ {len(posibles_fks)} posibles FKs sin definir")
            
            # Escribir si hay problemas
            if problemas_tabla:
                f.write(f"\n{'─' * 100}\n")
                f.write(f"TABLA: {tabla} ({num_registros:,} registros)\n")
                f.write(f"{'─' * 100}\n")
                
                for problema in problemas_tabla:
                    f.write(f"{problema}\n")
                
                if not pks:
                    f.write("\n  PROBLEMA: Tabla sin Primary Key\n")
                    f.write("  IMPACTO: No se pueden establecer relaciones confiables\n")
                    f.write("  SOLUCIÓN: Identificar columna(s) que identifiquen únicamente cada registro\n")
                
                if problemas_nulls:
                    f.write("\n  PROBLEMA: Columnas con NULLs excesivos:\n")
                    for pn in problemas_nulls:
                        f.write(f"    - {pn['columna']}: {pn['porcentaje']:.1f}% NULLs ({pn['nulls']:,}/{pn['total']:,})\n")
                    f.write("  IMPACTO: Posible diseño deficiente o datos opcionales mal manejados\n")
                    f.write("  SOLUCIÓN: Considerar tabla separada o valores por defecto\n")
                
                if posibles_fks:
                    f.write("\n  PROBLEMA: Posibles Foreign Keys sin definir:\n")
                    for pfk in posibles_fks:
                        f.write(f"    - {pfk}\n")
                    f.write("  IMPACTO: Integridad referencial no garantizada\n")
                    f.write("  SOLUCIÓN: Verificar si son referencias y crear FKs correspondientes\n")
        
        # ===== RESUMEN =====
        f.write("\n\n" + "=" * 100 + "\n")
        f.write("RESUMEN DE PROBLEMAS DETECTADOS\n")
        f.write("=" * 100 + "\n\n")
        
        f.write(f"1. TABLAS SIN PRIMARY KEY ({len(tablas_sin_pk)}):\n")
        if tablas_sin_pk:
            for t in tablas_sin_pk:
                f.write(f"   - {t}\n")
        else:
            f.write("   ✓ Todas las tablas tienen Primary Key\n")
        
        f.write(f"\n2. TABLAS CON NULLS EXCESIVOS ({len(tablas_con_nulls_excesivos)}):\n")
        if tablas_con_nulls_excesivos:
            for t, problemas in tablas_con_nulls_excesivos:
                f.write(f"   - {t}: {len(problemas)} columnas\n")
        else:
            f.write("   ✓ No se detectaron problemas significativos\n")
        
        f.write(f"\n3. TABLAS CON POSIBLES FKs FALTANTES ({len(tablas_con_posibles_fks)}):\n")
        if tablas_con_posibles_fks:
            for t, posibles in tablas_con_posibles_fks:
                f.write(f"   - {t}: {', '.join(posibles)}\n")
        else:
            f.write("   ✓ No se detectaron columnas sospechosas\n")
        
        # ===== RECOMENDACIONES =====
        f.write("\n\n" + "=" * 100 + "\n")
        f.write("RECOMENDACIONES PARA NORMALIZACIÓN\n")
        f.write("=" * 100 + "\n\n")
        
        f.write("1. INTEGRIDAD REFERENCIAL:\n")
        f.write("   - Definir Primary Keys en todas las tablas\n")
        f.write("   - Crear Foreign Keys para todas las relaciones\n")
        f.write("   - Usar índices en columnas de búsqueda frecuente\n\n")
        
        f.write("2. CALIDAD DE DATOS:\n")
        f.write("   - Revisar columnas con >50% NULLs\n")
        f.write("   - Considerar valores por defecto en lugar de NULL\n")
        f.write("   - Normalizar tablas con datos opcionales extensos\n\n")
        
        f.write("3. MIGRACIÓN A SQL SERVER:\n")
        f.write("   - Convertir tipos de datos apropiadamente\n")
        f.write("   - Implementar constraints (CHECK, DEFAULT)\n")
        f.write("   - Crear índices para optimizar consultas\n")
        f.write("   - Considerar particionamiento para tablas grandes\n\n")
        
        f.write("=" * 100 + "\n")
    
    cur.close()
    con.close()
    
    print(f"\n{'=' * 100}")
    print(f"✓ Análisis completado:")
    print(f"  - Tablas sin PK: {len(tablas_sin_pk)}")
    print(f"  - Tablas con NULLs excesivos: {len(tablas_con_nulls_excesivos)}")
    print(f"  - Tablas con posibles FKs faltantes: {len(tablas_con_posibles_fks)}")
    print(f"  - Reporte: {archivo_salida}")
    print("=" * 100)

if __name__ == "__main__":
    try:
        analizar_normalizacion()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
