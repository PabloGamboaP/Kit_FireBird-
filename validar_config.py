"""
Módulo para validar la configuración antes de conectar a Firebird
"""

import configparser
import os
import sys

def validar_configuracion():
    """
    Valida que el archivo configuracion.ini existe y tiene valores válidos
    Retorna: (valido, mensaje_error, config)
    """
    config_file = os.path.join(os.path.dirname(__file__), 'configuracion.ini')
    
    # Verificar que existe el archivo
    if not os.path.exists(config_file):
        return False, "No se encontró el archivo configuracion.ini", None
    
    # Leer configuración
    config = configparser.ConfigParser()
    try:
        config.read(config_file, encoding='utf-8')
    except Exception as e:
        return False, f"Error al leer configuracion.ini: {str(e)}", None
    
    # Verificar sección FIREBIRD
    if 'FIREBIRD' not in config:
        return False, "El archivo configuracion.ini no tiene la sección [FIREBIRD]", None
    
    cfg = config['FIREBIRD']
    
    # Validar campos requeridos
    campos_requeridos = ['database', 'user', 'password', 'charset']
    campos_faltantes = []
    
    for campo in campos_requeridos:
        if campo not in cfg or not cfg[campo].strip():
            campos_faltantes.append(campo)
    
    if campos_faltantes:
        return False, f"Faltan campos en configuracion.ini: {', '.join(campos_faltantes)}", None
    
    # Validar que no sean valores placeholder
    password = cfg['password'].strip()
    if password in ['TU_PASSWORD_AQUI', 'password', 'CAMBIAR', 'PLACEHOLDER']:
        return False, "El password en configuracion.ini es un placeholder. Debes configurar el password real.", None
    
    database = cfg['database'].strip()
    if database in ['C:\\temp\\activos.gdb', 'ruta/a/base.gdb']:
        return False, "La ruta de database en configuracion.ini parece ser un placeholder. Verifica la ruta correcta.", None
    
    # Validar que el archivo de base de datos existe (si es local)
    host = cfg.get('host', '').strip()
    if not host:  # Modo local
        if not os.path.exists(database):
            return False, f"El archivo de base de datos no existe: {database}", None
    
    return True, "Configuración válida", config

def mostrar_error_configuracion(mensaje_error):
    """Muestra un mensaje de error amigable sobre la configuración"""
    print("\n" + "=" * 100)
    print("ERROR DE CONFIGURACIÓN")
    print("=" * 100)
    print(f"\n❌ {mensaje_error}\n")
    print("SOLUCIÓN:")
    print("  1. Verifica que existe el archivo 'configuracion.ini'")
    print("  2. Si no existe, copia 'configuracion.ini.example' a 'configuracion.ini'")
    print("  3. Edita 'configuracion.ini' con tus credenciales reales:")
    print("     - password: Solicita el password al administrador de BD")
    print("     - database: Ruta correcta al archivo .gdb")
    print("     - host: IP del servidor (o vacío para modo local)")
    print("\n  Puedes usar la opción 9 del menú INICIAR.bat para editar la configuración")
    print("\n" + "=" * 100 + "\n")

def validar_o_salir():
    """
    Valida la configuración y sale del programa si hay error
    Retorna el objeto config si es válido
    """
    valido, mensaje, config = validar_configuracion()
    
    if not valido:
        mostrar_error_configuracion(mensaje)
        sys.exit(1)
    
    return config
