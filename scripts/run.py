"""
run.py - Script principal de ejecución del sistema NL2SQL

PROPÓSITO:
    Punto de entrada principal que orquesta la ejecución de todos
    los componentes del sistema NL2SQL en secuencia.

ENTRADA:
    - Argumentos de línea de comandos (opcional)
    - Configuración del sistema

SALIDA:
    - Flujo completo de ejecución con indicadores visuales
    - Manejo de errores y recuperación

DEPENDENCIAS:
    - core.config: Configuración del sistema
    - core.db_connector: Conexión a base de datos
    - core.schema_analyzer: Análisis de esquema
    - core.sql_generator: Generación de SQL
    - providers.*: Proveedores de IA
    - utils.progress: Indicadores de progreso
    - utils.error_handler: Manejo de errores
"""

import sys
import argparse
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from core.config import Config
from core.db_connector import DBConnector
from core.schema_analyzer import SchemaAnalyzer
from utils.progress import Progress

def parse_args():
    """Parsea los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(description='NL2SQL - Sistema de consultas SQL con lenguaje natural')
    parser.add_argument('--config', type=str, help='Ruta al archivo de configuración')
    parser.add_argument('--database', type=str, help='Base de datos a utilizar')
    parser.add_argument('--provider', type=str, default='claude', help='Proveedor de IA a utilizar')
    parser.add_argument('--interactive', action='store_true', help='Modo interactivo')
    return parser.parse_args()

def main():
    """Función principal que ejecuta el flujo completo del sistema"""
    args = parse_args()
    progress = Progress()
    
    # FASE 1: VALIDACIÓN DE CONFIGURACIÓN
    progress.start_phase("VALIDACIÓN")
    config = Config(args.config)
    if not config.validate():
        progress.error("Error en la configuración. Ejecute setup.py para configurar el sistema.")
        return
    progress.complete("Configuración validada correctamente")
    
    # FASE 2: CONEXIÓN A BASE DE DATOS
    progress.start_phase("CONEXIÓN BD")
    db_connector = DBConnector()
    success = db_connector.connect()
    if not success:
        progress.error("Error al conectar a la base de datos.")
        print("\n→ Sugerencia: Ejecute 'python scripts/setup.py' para configurar las credenciales de conexión")
        return
    progress.complete("Conexión establecida correctamente")
    
    # FASE 3: ANÁLISIS DE ESQUEMA
    progress.start_phase("ANÁLISIS ESQUEMA")
    schema_analyzer = SchemaAnalyzer(db_connector)
    
    # Si se especificó una base de datos, la usamos
    database = args.database
    if not database:
        # Si no, obtenemos las disponibles y seleccionamos una
        databases = schema_analyzer.get_databases()
        if not databases:
            progress.error("No se encontraron bases de datos disponibles")
            print("\n→ Sugerencia: Ejecute 'python scripts/setup.py' para configurar correctamente el sistema")
            return
        database = databases[0]  # Por defecto, la primera
        
    try:
        schema = schema_analyzer.analyze_database(database)
        schema_text = schema_analyzer.get_schema_text(schema)
    except Exception as e:
        progress.error(f"Error al analizar el esquema: {e}")
        print("\n→ Sugerencia: Verifique que la base de datos esté disponible o ejecute 'python scripts/setup.py'")
        return
    
    total_tables = len(schema["tables"])
    total_columns = sum(len(table["columns"]) for table in schema["tables"].values())
    progress.complete(f"Esquema analizado: {total_tables} tablas, {total_columns} columnas")
    
    # FASE 4: VERIFICACIÓN DE PROVEEDOR IA
    # Aquí vendría la implementación cuando tengamos los proveedores
    
    # FASE 5: INICIO DEL SISTEMA
    # Aquí vendría la implementación del modo interactivo o procesamiento de consultas
    
    # Información de diagnóstico final
    print("\nResumen de estado del sistema:")
    print(f"Base de datos seleccionada: {database}")
    print(f"Tablas disponibles: {', '.join(schema['tables'].keys())}")
    print("\nEsquema detectado:")
    print(schema_text)
    
    print("\nEl sistema está listo para procesar consultas.")

if __name__ == "__main__":
    main()
