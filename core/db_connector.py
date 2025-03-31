#!/usr/bin/env python3
"""
db_connector.py - Conexión dinámica a bases de datos

PROPÓSITO:
    Establece conexiones a cualquier base de datos compatible con SQLAlchemy
    y proporciona una interfaz unificada para consultas.

ENTRADA:
    - connection_string: URI de conexión o parámetros descompuestos
    - options: Opciones adicionales de conexión (opcional)

SALIDA:
    - Objeto de conexión activa
    - Estado de conexión y metadatos

ERRORES:
    - ConnectionError: No se pudo establecer conexión
    - CredentialError: Credenciales inválidas o insuficientes
    - DBNotFoundError: Base de datos especificada no existe

DEPENDENCIAS:
    - sqlalchemy: Para gestión de conexiones
    - utils.progress: Para indicadores de progreso
    - utils.error_handler: Para manejo de errores
    - core.config: Para configuración global
"""

import sys
import time
from pathlib import Path
import logging
from typing import Dict, Any, Optional, Tuple, Union

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones de SQLAlchemy
try:
    from sqlalchemy import create_engine, inspect, MetaData, text
    from sqlalchemy.exc import SQLAlchemyError
    from sqlalchemy.engine import Engine
    from sqlalchemy.engine.url import make_url
except ImportError:
    print("Error: SQLAlchemy no está instalado. Instale con 'pip install sqlalchemy'")
    sys.exit(1)

# Importaciones internas
from core.config import Config
from utils.progress import start_phase, update_progress, complete_phase, show_error, show_success

# Configurar logger
logger = logging.getLogger('db_connector')

class DBConnector:
    """Clase para gestionar conexiones a bases de datos."""
    
    def __init__(self, connection_string: Optional[str] = None, **kwargs):
        """
        Inicializa un conector de base de datos.
        
        Args:
            connection_string: URI de conexión SQLAlchemy (opcional)
            **kwargs: Parámetros de conexión alternativos
        """
        self.engine = None
        self.metadata = None
        self.inspector = None
        self.connection_string = connection_string
        self.connection_params = kwargs
        self.is_connected = False
        
    def connect(self) -> bool:
        """
        Establece una conexión a la base de datos.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        start_phase("db_connection", "Conectando a base de datos")
        
        try:
            update_progress(10, "Preparando parámetros de conexión")
            
            # Si no se proporcionó una cadena de conexión, intentar construirla
            if not self.connection_string:
                from utils.db_helpers import get_db_connection_string
                self.connection_string = get_db_connection_string(Config.get)
                
                if not self.connection_string:
                    update_progress(20, "Error: No se pudo obtener cadena de conexión")
                    raise ValueError("No se proporcionó una cadena de conexión válida")
            
            update_progress(30, f"Intentando conexión a {self._get_safe_connection_info()}")
            
            # Crear el motor de SQLAlchemy
            self.engine = create_engine(
                self.connection_string,
                echo=False,  # No mostrar consultas SQL en logs
                future=True  # Usar la API más reciente de SQLAlchemy
            )
            
            update_progress(50, "Motor de base de datos inicializado")
            
            # Probar la conexión
            update_progress(70, "Probando conexión")
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            
            update_progress(80, "Conexión exitosa, inicializando metadatos")
            
            # Inicializar metadatos e inspector
            self.metadata = MetaData()
            self.inspector = inspect(self.engine)
            self.is_connected = True
            
            update_progress(100, "Conexión establecida correctamente")
            
            # Obtener información del servidor
            db_info = self._get_db_info()
            complete_phase(True, f"Conexión establecida con {db_info}")
            
            return True
            
        except SQLAlchemyError as e:
            update_progress(90, f"Error de SQLAlchemy: {str(e)}")
            complete_phase(False, f"Error de conexión: {str(e)}")
            logger.error(f"Error de conexión SQLAlchemy: {str(e)}")
            return False
            
        except Exception as e:
            update_progress(90, f"Error inesperado: {str(e)}")
            complete_phase(False, f"Error inesperado: {str(e)}")
            logger.error(f"Error inesperado al conectar: {str(e)}")
            return False
    
    def disconnect(self) -> None:
        """Cierra la conexión a la base de datos."""
        if self.engine:
            self.engine.dispose()
            self.is_connected = False
            logger.info("Conexión a base de datos cerrada")
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> Tuple[bool, Any]:
        """
        Ejecuta una consulta SQL.
        
        Args:
            query: Consulta SQL a ejecutar
            params: Parámetros para la consulta (opcional)
            
        Returns:
            Tupla (éxito, resultados)
        """
        if not self.is_connected or not self.engine:
            return False, "No hay conexión activa a la base de datos"
            
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return True, result
                
        except SQLAlchemyError as e:
            logger.error(f"Error al ejecutar consulta: {str(e)}")
            return False, str(e)
    
    def get_tables(self) -> Dict[str, Any]:
        """
        Obtiene información sobre las tablas en la base de datos.
        
        Returns:
            Diccionario con información de tablas
        """
        if not self.is_connected or not self.inspector:
            return {}
            
        result = {}
        for table_name in self.inspector.get_table_names():
            columns = self.inspector.get_columns(table_name)
            primary_keys = self.inspector.get_pk_constraint(table_name)
            foreign_keys = self.inspector.get_foreign_keys(table_name)
            
            result[table_name] = {
                "columns": columns,
                "primary_keys": primary_keys,
                "foreign_keys": foreign_keys
            }
            
        return result
    
    def _get_db_info(self) -> str:
        """
        Obtiene información sobre el servidor de base de datos.
        
        Returns:
            Cadena con información del servidor
        """
        if not self.is_connected or not self.engine:
            return "No conectado"
            
        try:
            with self.engine.connect() as connection:
                if 'sqlite' in self.engine.name:
                    return "SQLite"
                    
                elif 'mysql' in self.engine.name:
                    result = connection.execute(text("SELECT VERSION()"))
                    version = result.scalar()
                    return f"MySQL {version}"
                    
                elif 'postgresql' in self.engine.name:
                    result = connection.execute(text("SELECT version()"))
                    version = result.scalar()
                    return f"PostgreSQL {version}"
                    
                else:
                    return self.engine.name
                    
        except Exception:
            return self.engine.name
    
    def _get_safe_connection_info(self) -> str:
        """
        Obtiene información de conexión sin credenciales sensibles.
        
        Returns:
            Información de conexión segura para mostrar en logs
        """
        if not self.connection_string:
            return "Conexión no especificada"
            
        try:
            url = make_url(self.connection_string)
            db_type = url.drivername
            host = url.host or 'local'
            database = url.database or 'sin nombre'
            
            return f"{db_type}://{host}/{database}"
            
        except Exception:
            # Si no se puede parsear, devolver tipo genérico
            if 'sqlite' in self.connection_string:
                return "SQLite local"
            elif 'mysql' in self.connection_string:
                return "MySQL"
            elif 'postgresql' in self.connection_string:
                return "PostgreSQL"
            else:
                return "Base de datos desconocida"

# Función de conveniencia para obtener una conexión rápida
def connect(connection_string: Optional[str] = None, **kwargs) -> DBConnector:
    """
    Crea y conecta a una base de datos rápidamente.
    
    Args:
        connection_string: URI de conexión (opcional)
        **kwargs: Parámetros alternativos
        
    Returns:
        Objeto DBConnector conectado
    """
    connector = DBConnector(connection_string, **kwargs)
    success = connector.connect()
    
    if not success:
        print("\n→ Sugerencia: Ejecute 'python scripts/setup.py' para configurar las credenciales de conexión")
    
    return connector

# Función de prueba para diagnóstico
def test_connection(connection_string: Optional[str] = None) -> str:
    """
    Prueba una conexión a la base de datos.
    
    Args:
        connection_string: URI de conexión opcional
        
    Returns:
        Mensaje con el resultado de la prueba
    """
    connector = DBConnector(connection_string)
    
    if connector.connect():
        tables = connector.get_tables()
        table_count = len(tables)
        column_count = sum(len(table_info["columns"]) for table_info in tables.values())
        
        result = f"Conexión exitosa: {table_count} tablas, {column_count} columnas"
        connector.disconnect()
        return result
    else:
        return "Error al conectar a la base de datos"

# Para ejecutar como script independiente
if __name__ == "__main__":
    print("=== Prueba de Conexión a Base de Datos ===\n")
    
    # Usar argumentos de línea de comandos si se proporcionan
    if len(sys.argv) > 1:
        connection_str = sys.argv[1]
        print(f"Usando cadena de conexión proporcionada: {connection_str}")
        result = test_connection(connection_str)
    else:
        # Usar configuración por defecto
        print("Usando configuración del archivo .env")
        result = test_connection()
    
    print(f"\nResultado: {result}")
