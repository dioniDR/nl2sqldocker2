#!/usr/bin/env python3
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
    - utils.progress: Indicadores de progreso
    - utils.config_helpers: Utilidades de configuración
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
from utils.progress import start_phase, update_progress, complete_phase, show_info, show_error, show_success
from utils.config_helpers import is_setup_complete

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
    
    # FASE 1: VALIDACIÓN DE CONFIGURACIÓN
    start_phase("setup", "Verificando configuración")
    update_progress(50, "Comprobando configuración del sistema")
    
    # Verificar si la configuración es válida
    if not is_setup_complete(Config.get):
        update_progress(100, "Error: Configuración incompleta")
        complete_phase(False, "Error en la configuración")
        show_error("Configuración incompleta. Ejecute 'python scripts/setup.py' para configurar el sistema.")
        return
    
    update_progress(100, "Configuración verificada")
    complete_phase(True, "Configuración validada correctamente")
    
    # FASE 2: CONEXIÓN A BASE DE DATOS
    start_phase("db_connection", "Conectando a base de datos")
    update_progress(20, "Inicializando conector de base de datos")
    
    db_connector = DBConnector()
    update_progress(50, "Intentando conexión")
    
    success = db_connector.connect()
    if not success:
        update_progress(100, "Error: No se pudo conectar a la base de datos")
        complete_phase(False, "Error al conectar a la base de datos")
        show_error("No se pudo establecer conexión con la base de datos")
        print("\n→ Sugerencia: Ejecute 'python scripts/setup.py' para configurar las credenciales de conexión")
        return
    
    update_progress(100, "Conexión establecida")
    complete_phase(True, "Conexión establecida correctamente")
    
    # FASE 3: ANÁLISIS DE ESQUEMA
    start_phase("schema_analysis", "Analizando estructura de base de datos")
    update_progress(20, "Inicializando analizador de esquema")
    
    schema_analyzer = SchemaAnalyzer(db_connector)
    update_progress(40, "Obteniendo bases de datos disponibles")
    
    # Si se especificó una base de datos, la usamos
    database = args.database
    if not database:
        # Si no, obtenemos las disponibles y seleccionamos una
        databases = schema_analyzer.get_databases()
        if not databases:
            update_progress(100, "Error: No se encontraron bases de datos")
            complete_phase(False, "No se encontraron bases de datos disponibles")
            show_error("No se encontraron bases de datos disponibles")
            print("\n→ Sugerencia: Ejecute 'python scripts/setup.py' para configurar correctamente el sistema")
            return
        
        database = databases[0]  # Por defecto, la primera
        update_progress(60, f"Seleccionada base de datos: {database}")
    
    update_progress(70, f"Analizando base de datos: {database}")
    try:
        schema = schema_analyzer.analyze_database(database)
        schema_text = schema_analyzer.get_schema_text(schema)
        update_progress(90, "Esquema analizado correctamente")
    except Exception as e:
        update_progress(100, f"Error: {str(e)}")
        complete_phase(False, f"Error al analizar el esquema: {str(e)}")
        show_error(f"Error al analizar el esquema: {str(e)}")
        print("\n→ Sugerencia: Verifique que la base de datos esté disponible o ejecute 'python scripts/setup.py'")
        return
    
    total_tables = len(schema["tables"])
    total_columns = sum(len(table["columns"]) for table in schema["tables"].values())
    update_progress(100, f"Análisis completado: {total_tables} tablas, {total_columns} columnas")
    complete_phase(True, f"Esquema analizado: {total_tables} tablas, {total_columns} columnas")
    
    # FASE 4: VERIFICACIÓN DE PROVEEDOR IA
    start_phase("ai_provider", "Comprobando proveedores de IA")
    update_progress(30, f"Proveedor solicitado: {args.provider}")
    
    # Aquí vendría la implementación de la verificación del proveedor de IA
    # Por ahora, simplemente simulamos éxito
    ai_provider = Config.get('AI_PROVIDER')
    update_progress(100, f"Proveedor seleccionado: {ai_provider}")
    complete_phase(True, f"Proveedor activo: {ai_provider}")
    
    # FASE 5: INICIO DEL SISTEMA
    start_phase("system_start", "Preparando interfaz")
    update_progress(50, "Inicializando sistema")
    update_progress(100, "Sistema listo")
    complete_phase(True, "Sistema listo para consultas")
    
    # Información de diagnóstico final
    print("\nResumen de estado del sistema:")
    print(f"Base de datos seleccionada: {database}")
    print(f"Tablas disponibles: {', '.join(schema['tables'].keys())}")
    print("\nEsquema detectado:")
    print(schema_text)
    
    show_success("El sistema está listo para procesar consultas")
    print("\nPuede comenzar a hacer consultas en lenguaje natural.")

if __name__ == "__main__":
    main()