#!/usr/bin/env python3
"""
schema_analyzer.py - Análisis de esquemas de base de datos

PROPÓSITO:
    Analiza y extrae la estructura completa de una base de datos
    incluyendo tablas, columnas, tipos, y relaciones.

ENTRADA:
    - Conexión a base de datos activa
    - Opciones de análisis (opcional)

SALIDA:
    - Diccionario con la estructura completa del esquema
    - Representación textual del esquema para prompts

ERRORES:
    - SchemaError: Error al analizar el esquema
    - AccessError: Permisos insuficientes para acceder al esquema

DEPENDENCIAS:
    - core.db_connector: Para acceso a la base de datos
    - utils.progress: Para indicadores de progreso
"""

import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import os

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones internas
from core.db_connector import DBConnector, connect
from utils.progress import start_phase, update_progress, complete_phase
from utils.progress import show_info, show_success, show_error, show_warning

# Configurar logger
logger = logging.getLogger('schema_analyzer')

class SchemaAnalyzer:
    """Clase para analizar esquemas de bases de datos."""
    
    def __init__(self, db_connector=None):
        """
        Inicializa el analizador de esquemas.
        
        Args:
            db_connector: Conector de base de datos ya conectado (opcional)
        """
        self.db_connector = db_connector
        self.current_database = None
    
    def ensure_connection(self) -> bool:
        """
        Asegura que exista una conexión activa a la base de datos.
        
        Returns:
            True si hay conexión, False en caso contrario
        """
        if self.db_connector and self.db_connector.is_connected:
            return True
            
        # Cargar configuración desde .env
        load_dotenv()
        connection_string = os.getenv('DB_CONNECTION_STRING')
        if not connection_string:
            show_error("No se encontró la cadena de conexión en el archivo .env")
            show_info("→ Ejecute 'python scripts/setup.py' para configurar las credenciales de conexión")
            return False
        
        # Intentar crear una nueva conexión
        self.db_connector = connect(connection_string)
        
        if not self.db_connector.is_connected:
            show_error("No hay conexión activa a la base de datos")
            show_info("→ Ejecute 'python scripts/setup.py' para configurar las credenciales de conexión")
            return False
            
        return True
    
    def get_databases(self) -> List[str]:
        """
        Obtiene la lista de bases de datos disponibles.
        
        Returns:
            Lista de nombres de bases de datos
        """
        if not self.ensure_connection():
            return []
            
        # Obtener todas las bases de datos
        success, result = self.db_connector.execute_query("SHOW DATABASES")
        
        if not success:
            show_error(f"Error al obtener bases de datos: {result}")
            return []
            
        # Extraer nombres de bases de datos
        all_dbs = [row[0] for row in result]
        
        # Filtrar bases de datos del sistema
        system_dbs = ['mysql', 'information_schema', 'performance_schema', 'sys']
        user_dbs = [db for db in all_dbs if db not in system_dbs]
        
        return user_dbs
    
    def analyze_database(self, database_name: str) -> Dict[str, Any]:
        """
        Analiza la estructura completa de una base de datos.
        
        Args:
            database_name: Nombre de la base de datos a analizar
            
        Returns:
            Diccionario con la estructura del esquema
        """
        start_phase("schema_analysis", f"Analizando base de datos: {database_name}")
        
        if not self.ensure_connection():
            complete_phase(False, "Sin conexión a la base de datos")
            return {}
            
        # Cambiamos a la base de datos seleccionada
        update_progress(10, f"Seleccionando base de datos {database_name}")
        success, result = self.db_connector.execute_query(f"USE `{database_name}`")
        
        if not success:
            update_progress(20, f"Error al seleccionar base de datos: {result}")
            complete_phase(False, f"Error al seleccionar base de datos: {result}")
            return {}
            
        self.current_database = database_name
        
        # Obtenemos la lista de tablas
        update_progress(20, "Obteniendo lista de tablas")
        success, result = self.db_connector.execute_query("SHOW TABLES")
        
        if not success:
            update_progress(30, f"Error al obtener tablas: {result}")
            complete_phase(False, f"Error al obtener tablas: {result}")
            return {}
            
        tables = [row[0] for row in result]
        update_progress(30, f"Se encontraron {len(tables)} tablas")
        
        # Estructura para almacenar el esquema
        schema = {
            "database": database_name,
            "tables": {}
        }
        
        # Analizar cada tabla
        for i, table in enumerate(tables):
            progress_percent = 30 + (i / len(tables) * 60)
            update_progress(progress_percent, f"Analizando tabla {table}")
            
            # Obtener estructura de la tabla
            success, columns_result = self.db_connector.execute_query(f"DESCRIBE `{table}`")
            
            if not success:
                logger.warning(f"Error al analizar tabla {table}: {columns_result}")
                continue
                
            # Obtener claves primarias
            success, pk_result = self.db_connector.execute_query(
                "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                f"WHERE TABLE_SCHEMA = '{database_name}' AND TABLE_NAME = '{table}' "
                "AND CONSTRAINT_NAME = 'PRIMARY'"
            )
            
            primary_keys = [row[0] for row in pk_result] if success else []
            
            # Obtener claves foráneas
            success, fk_result = self.db_connector.execute_query(
                "SELECT COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME "
                "FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE "
                f"WHERE TABLE_SCHEMA = '{database_name}' AND TABLE_NAME = '{table}' "
                "AND REFERENCED_TABLE_NAME IS NOT NULL"
            )
            
            foreign_keys = []
            if success:
                for row in fk_result:
                    foreign_keys.append({
                        "column": row[0],
                        "referenced_table": row[1],
                        "referenced_column": row[2]
                    })
            
            # Estructurar la información de la tabla
            table_info = {
                "name": table,
                "columns": [],
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            }
            
            # Procesar columnas
            for column in columns_result:
                column_info = {
                    "name": column[0],
                    "type": column[1],
                    "null": column[2] == "YES",
                    "key": column[3],
                    "default": column[4],
                    "extra": column[5]
                }
                
                table_info["columns"].append(column_info)
            
            # Agregar la tabla al esquema
            schema["tables"][table] = table_info
        
        # Completar el análisis
        total_tables = len(schema["tables"])
        total_columns = sum(len(table_info["columns"]) for table_info in schema["tables"].values())
        
        update_progress(100, f"Análisis completado: {total_tables} tablas, {total_columns} columnas")
        complete_phase(True, f"Esquema analizado: {total_tables} tablas, {total_columns} columnas")
        
        return schema
    
    def get_schema_text(self, schema: Dict[str, Any]) -> str:
        """
        Genera una representación textual del esquema para prompts.
        
        Args:
            schema: Diccionario con el esquema analizado
            
        Returns:
            Representación textual del esquema
        """
        if not schema or "tables" not in schema:
            return "Esquema no disponible"
            
        text = f"Base de datos: {schema['database']}\n\n"
        
        for table_name, table in schema["tables"].items():
            text += f"Tabla {table_name}:\n"
            
            # Agregar columnas
            for column in table["columns"]:
                # Determinar información de clave
                key_info = ""
                if column["name"] in table.get("primary_keys", []):
                    key_info = " (Clave primaria)"
                else:
                    # Buscar si es clave foránea
                    for fk in table.get("foreign_keys", []):
                        if fk["column"] == column["name"]:
                            key_info = f" (Clave foránea → {fk['referenced_table']}.{fk['referenced_column']})"
                            break
                
                # Agregar información de la columna
                text += f"  - {column['name']} ({column['type']}){key_info}"
                
                # Restricciones
                constraints = []
                if not column["null"]:
                    constraints.append("NOT NULL")
                if column["default"] is not None:
                    constraints.append(f"DEFAULT {column['default']}")
                if column["extra"]:
                    constraints.append(column["extra"])
                
                if constraints:
                    text += f": {' '.join(constraints)}"
                
                text += "\n"
            
            text += "\n"
        
        return text
    
    def analyze_and_get_text(self, database_name: Optional[str] = None) -> str:
        """
        Analiza una base de datos y retorna su representación textual.
        
        Args:
            database_name: Nombre de la base de datos (opcional)
            
        Returns:
            Representación textual del esquema
        """
        if database_name is None:
            # Si no se especifica, intentamos obtener las disponibles
            databases = self.get_databases()
            
            if not databases:
                return "No se encontraron bases de datos disponibles"
            
            database_name = databases[0]  # Usamos la primera disponible
        
        schema = self.analyze_database(database_name)
        return self.get_schema_text(schema)


# Para ejecutar como script independiente
if __name__ == "__main__":
    # Configurar logs básicos
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Modo de auto-test
    print("=== Analizador de Esquemas de Base de Datos ===\n")
    
    # Crear analizador
    analyzer = SchemaAnalyzer()
    
    if not analyzer.ensure_connection():
        sys.exit(1)
    
    # Obtener bases de datos disponibles
    databases = analyzer.get_databases()
    
    if not databases:
        print("No se encontraron bases de datos disponibles")
        sys.exit(1)
    
    print("Bases de datos disponibles:")
    for i, db in enumerate(databases, 1):
        print(f"  {i}. {db}")
    
    # Permitir selección de base de datos
    selected = input("\nSeleccione una base de datos (número o nombre): ")
    
    try:
        # Intentar interpretar como índice
        index = int(selected) - 1
        if 0 <= index < len(databases):
            database_name = databases[index]
        else:
            print("Índice fuera de rango, usando la primera base de datos")
            database_name = databases[0]
    except ValueError:
        # Es un nombre, verificar si existe
        if selected in databases:
            database_name = selected
        else:
            print(f"La base de datos '{selected}' no fue encontrada, usando la primera disponible")
            database_name = databases[0]
    
    # Analizar la base de datos seleccionada
    schema_text = analyzer.analyze_and_get_text(database_name)
    
    print("\n=== Esquema de la Base de Datos ===\n")
    print(schema_text)