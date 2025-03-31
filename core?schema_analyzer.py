"""
schema_analyzer.py - Análisis de esquemas de bases de datos

PROPÓSITO:
    Analiza la estructura de la base de datos conectada,
    extrayendo tablas, columnas, relaciones y tipos de datos
    para proporcionar contexto a los generadores de SQL.

ENTRADA:
    - Objeto de conexión a base de datos
    - Opciones de análisis (profundidad, inclusiones, exclusiones)

SALIDA:
    - Diccionario completo de esquema
    - Representación en formato JSON/dict del esquema
    - Metadata para uso en prompts a IA

ERRORES:
    - SchemaError: No se pudo analizar el esquema
    - ConnectionError: No hay conexión activa
    - PermissionError: Sin permisos para leer el esquema

DEPENDENCIAS:
    - sqlalchemy: Para inspección de esquemas
    - utils.progress: Para indicadores visuales
    - utils.error_handler: Para manejo de errores
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Set, Tuple

try:
    from sqlalchemy import MetaData, Table, ForeignKey, select, text
    from sqlalchemy.engine import Engine, Connection
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    raise ImportError("SQLAlchemy no está instalado. Ejecute 'pip install sqlalchemy'")

from utils.progress import ProgressBar
from utils.error_handler import SchemaError, ConnectionError, PermissionError

# Configurar logger
logger = logging.getLogger(__name__)

class SchemaAnalyzer:
    """Clase para analizar esquemas de bases de datos."""
    
    def __init__(self, connection=None, engine=None):
        """
        Inicializa el analizador de esquemas.
        
        Args:
            connection: Objeto de conexión SQLAlchemy (opcional)
            engine: Objeto engine SQLAlchemy (opcional)
        """
        self.connection = connection
        self.engine = engine
        self.metadata = None
        self.inspector = None
        self.schema_data = {}
        self.sample_data = {}
        self.analyzed = False
        
    def set_connection(self, connection=None, engine=None):
        """
        Establece la conexión para análisis.
        
        Args:
            connection: Objeto de conexión SQLAlchemy (opcional)
            engine: Objeto engine SQLAlchemy (opcional)
            
        Returns:
            bool: True si se estableció correctamente
        """
        if connection:
            self.connection = connection
            self.engine = connection.engine
            return True
        elif engine:
            self.engine = engine
            self.connection = engine.connect()
            return True
        return False
    
    def analyze(self, depth: str = "full", 
                include_tables: Optional[List[str]] = None,
                exclude_tables: Optional[List[str]] = None,
                include_sample_data: bool = True,
                max_sample_rows: int = 5) -> Dict[str, Any]:
        """
        Analiza el esquema de la base de datos.
        
        Args:
            depth: Nivel de profundidad de análisis ('basic', 'standard', 'full')
            include_tables: Lista de tablas a incluir (None = todas)
            exclude_tables: Lista de tablas a excluir
            include_sample_data: Si se debe incluir datos de muestra
            max_sample_rows: Número máximo de filas de muestra
            
        Returns:
            Dict: Esquema completo de la base de datos
            
        Raises:
            ConnectionError: No hay conexión activa
            SchemaError: Error al analizar el esquema
            PermissionError: Sin permisos para leer el esquema
        """
        # Verificar conexión
        if not self.connection and not self.engine:
            raise ConnectionError("No hay conexión activa a base de datos")
        
        # Crear barra de progreso
        progress = ProgressBar("Analizando estructura de base de datos")
        progress.start()
        
        try:
            # Inicializar metadata e inspector
            self.metadata = MetaData()
            self.metadata.reflect(bind=self.engine)
            self.inspector = self.engine.dialect.inspector
            
            # Filtrar tablas según parámetros
            all_tables = self.metadata.tables.keys()
            tables_to_analyze = set(all_tables)
            
            if include_tables:
                tables_to_analyze = tables_to_analyze.intersection(include_tables)
            if exclude_tables:
                tables_to_analyze = tables_to_analyze.difference(exclude_tables)
            
            # Inicializar estructura de esquema
            self.schema_data = {
                "database_info": self._get_database_info(),
                "tables": {},
                "relationships": [],
                "stats": {
                    "tables_count": len(tables_to_analyze),
                    "columns_count": 0,
                    "foreign_keys_count": 0,
                    "primary_keys_count": 0,
                    "indexes_count": 0
                }
            }
            
            # Procesar cada tabla
            progress.update(20)
            table_count = len(tables_to_analyze)
            for idx, table_name in enumerate(sorted(tables_to_analyze)):
                # Analizar tabla
                self._analyze_table(table_name, depth)
                # Actualizar progreso proporcionalmente
                progress_value = 20 + int(60 * (idx + 1) / table_count)
                progress.update(progress_value)
            
            # Analizar relaciones
            self._analyze_relationships()
            progress.update(90)
            
            # Recolectar datos de muestra si se solicita
            if include_sample_data:
                self._collect_sample_data(tables_to_analyze, max_sample_rows)
            
            # Calcular estadísticas finales
            self._calculate_statistics()
            progress.update(95)
            
            # Marcar como analizado
            self.analyzed = True
            
            progress.finish(success=True)
            logger.info(f"Esquema analizado: {self.schema_data['stats']['tables_count']} tablas, "
                       f"{self.schema_data['stats']['columns_count']} columnas")
            
            return self.schema_data
            
        except SQLAlchemyError as e:
            progress.finish(success=False)
            error_msg = str(e)
            logger.error(f"Error al analizar esquema: {error_msg}")
            
            if "permission" in error_msg.lower() or "privilege" in error_msg.lower():
                raise PermissionError(f"Sin permisos para leer el esquema: {error_msg}")
            else:
                raise SchemaError(f"Error al analizar esquema: {error_msg}")
    
    def _get_database_info(self) -> Dict[str, Any]:
        """
        Obtiene información general de la base de datos.
        
        Returns:
            Dict: Información de la base de datos
        """
        try:
            # Obtener tipo de BD
            db_type = self.engine.name
            
            # Intentar obtener versión
            if db_type == "mysql":
                version_query = "SELECT VERSION()"
            elif db_type == "postgresql":
                version_query = "SELECT version()"
            elif db_type == "sqlite":
                version_query = "SELECT sqlite_version()"
            else:
                version_query = None
            
            version = None
            if version_query:
                try:
                    version_result = self.connection.execute(text(version_query)).fetchone()
                    version = version_result[0] if version_result else "Desconocida"
                except:
                    version = "Error al obtener versión"
            
            return {
                "name": self.engine.url.database if hasattr(self.engine.url, 'database') else "Desconocida",
                "type": db_type,
                "version": version,
                "charset": self.engine.dialect.encoding if hasattr(self.engine.dialect, 'encoding') else "Desconocido"
            }
        except Exception as e:
            logger.warning(f"Error al obtener información de la base de datos: {e}")
            return {
                "name": "Desconocida",
                "type": self.engine.name if hasattr(self.engine, 'name') else "Desconocido",
                "version": "Desconocida",
                "charset": "Desconocido"
            }
    
    def _analyze_table(self, table_name: str, depth: str) -> None:
        """
        Analiza una tabla específica.
        
        Args:
            table_name: Nombre de la tabla a analizar
            depth: Nivel de profundidad de análisis
        """
        table_info = {
            "name": table_name,
            "columns": {},
            "primary_key": [],
            "foreign_keys": [],
            "indexes": [],
            "row_count": 0
        }
        
        # Obtener objeto Table
        table = self.metadata.tables[table_name]
        
        # Analizar columnas
        for column in table.columns:
            col_info = {
                "name": column.name,
                "type": str(column.type),
                "nullable": column.nullable,
                "primary_key": column.primary_key,
                "default": str(column.default) if column.default is not None else None,
            }
            
            # Añadir información adicional para análisis completo
            if depth == "full":
                col_info.update({
                    "unique": column.unique,
                    "index": column.index,
                    "autoincrement": column.autoincrement if hasattr(column, 'autoincrement') else None,
                    "comment": column.comment if hasattr(column, 'comment') else None,
                })
            
            table_info["columns"][column.name] = col_info
            
            # Registrar clave primaria
            if column.primary_key:
                table_info["primary_key"].append(column.name)
        
        # Obtener claves foráneas
        for fk in table.foreign_keys:
            fk_info = {
                "column": fk.parent.name,
                "references_table": fk.column.table.name,
                "references_column": fk.column.name
            }
            table_info["foreign_keys"].append(fk_info)
        
        # Obtener índices si el análisis es completo
        if depth in ["standard", "full"]:
            for index in table.indexes:
                idx_info = {
                    "name": index.name,
                    "columns": [col.name for col in index.columns],
                    "unique": index.unique
                }
                table_info["indexes"].append(idx_info)
        
        # Obtener conteo aproximado de filas si el análisis es completo
        if depth == "full":
            try:
                # Para bases de datos grandes, usar estimación en lugar de COUNT exacto
                if self.engine.name == "postgresql":
                    count_query = text(f"SELECT reltuples::bigint AS estimate FROM pg_class WHERE relname = '{table_name}'")
                    row_count_result = self.connection.execute(count_query).fetchone()
                    table_info["row_count"] = int(row_count_result[0]) if row_count_result else 0
                else:
                    # Fallback para otras bases de datos
                    count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                    row_count_result = self.connection.execute(count_query).fetchone()
                    table_info["row_count"] = row_count_result[0] if row_count_result else 0
            except Exception as e:
                logger.warning(f"No se pudo obtener el conteo de filas para {table_name}: {e}")
                table_info["row_count"] = 0
        
        # Guardar información de la tabla
        self.schema_data["tables"][table_name] = table_info
    
    def _analyze_relationships(self) -> None:
        """Analiza las relaciones entre tablas basadas en claves foráneas."""
        relationships = []
        
        # Procesar cada tabla
        for table_name, table_info in self.schema_data["tables"].items():
            # Revisar las claves foráneas
            for fk in table_info["foreign_keys"]:
                # Crear relación
                relationship = {
                    "table_from": table_name,
                    "column_from": fk["column"],
                    "table_to": fk["references_table"],
                    "column_to": fk["references_column"],
                    "relationship_type": "many_to_one"  # Asunción por defecto
                }
                
                # Intentar determinar cardinalidad
                try:
                    # Verificar si la columna de origen es única o PK
                    from_is_unique = (fk["column"] in table_info["primary_key"] or
                                     any(idx["unique"] and fk["column"] in idx["columns"] 
                                         for idx in table_info["indexes"]))
                    
                    # Verificar si la columna destino es única o PK
                    to_table = self.schema_data["tables"].get(fk["references_table"], {})
                    to_is_unique = (fk["references_column"] in to_table.get("primary_key", []) or
                                   any(idx["unique"] and fk["references_column"] in idx["columns"] 
                                       for idx in to_table.get("indexes", [])))
                    
                    # Determinar tipo de relación
                    if from_is_unique and to_is_unique:
                        relationship["relationship_type"] = "one_to_one"
                    elif from_is_unique:
                        relationship["relationship_type"] = "one_to_many"
                    else:
                        relationship["relationship_type"] = "many_to_one"
                except Exception as e:
                    logger.warning(f"Error al determinar cardinalidad: {e}")
                
                # Añadir a la lista de relaciones
                relationships.append(relationship)
        
        # Guardar relaciones
        self.schema_data["relationships"] = relationships
    
    def _collect_sample_data(self, tables: Set[str], max_rows: int = 5) -> None:
        """
        Recolecta datos de muestra para las tablas.
        
        Args:
            tables: Conjunto de nombres de tablas
            max_rows: Número máximo de filas por tabla
        """
        self.sample_data = {}
        
        for table_name in tables:
            try:
                # Obtener objeto tabla
                table = self.metadata.tables[table_name]
                
                # Crear consulta
                query = select(table).limit(max_rows)
                
                # Ejecutar consulta
                result = self.connection.execute(query)
                
                # Convertir resultados a diccionario
                rows = []
                for row in result:
                    # Usar _asdict() para SQLAlchemy >= 1.4
                    if hasattr(row, '_asdict'):
                        rows.append(row._asdict())
                    # Usar __dict__ para versiones anteriores
                    else:
                        row_dict = {col: getattr(row, col) for col in row.keys()}
                        rows.append(row_dict)
                
                # Guardar datos
                self.sample_data[table_name] = rows
                
            except Exception as e:
                logger.warning(f"Error al recolectar datos de muestra para {table_name}: {e}")
                self.sample_data[table_name] = []
        
        # Agregar datos de muestra al esquema
        self.schema_data["sample_data"] = self.sample_data
    
    def _calculate_statistics(self) -> None:
        """Calcula estadísticas generales del esquema."""
        # Conteo de columnas
        columns_count = 0
        foreign_keys_count = 0
        primary_keys_count = 0
        indexes_count = 0
        
        for table_name, table_info in self.schema_data["tables"].items():
            columns_count += len(table_info["columns"])
            foreign_keys_count += len(table_info["foreign_keys"])
            primary_keys_count += len(table_info["primary_key"])
            indexes_count += len(table_info["indexes"])
        
        # Actualizar estadísticas
        self.schema_data["stats"].update({
            "columns_count": columns_count,
            "foreign_keys_count": foreign_keys_count,
            "primary_keys_count": primary_keys_count,
            "indexes_count": indexes_count
        })
    
    def get_schema_json(self) -> str:
        """
        Obtiene el esquema en formato JSON.
        
        Returns:
            str: Esquema en formato JSON
        """
        if not self.analyzed:
            return "{}"
        
        return json.dumps(self.schema_data, indent=2)
    
    def get_schema_summary(self) -> str:
        """
        Obtiene un resumen textual del esquema para usar en prompts.
        
        Returns:
            str: Resumen del esquema
        """
        if not self.analyzed:
            return "No hay esquema analizado"
        
        summary = []
        
        # Información de la base de datos
        db_info = self.schema_data["database_info"]
        summary.append(f"Base de datos: {db_info['name']} ({db_info['type']} {db_info['version']})")
        
        # Estadísticas
        stats = self.schema_data["stats"]
        summary.append(f"Tablas: {stats['tables_count']}, Columnas: {stats['columns_count']}")
        
        # Detalles de tablas
        summary.append("\nESTRUCTURA DE TABLAS:")
        for table_name, table_info in self.schema_data["tables"].items():
            summary.append(f"\nTABLA {table_name}")
            
            # Columnas y tipos
            for col_name, col_info in table_info["columns"].items():
                pk_mark = "*" if col_info["primary_key"] else ""
                null_mark = "NULL" if col_info["nullable"] else "NOT NULL"
                summary.append(f"  {pk_mark}{col_name} {col_info['type']} {null_mark}")
            
            # Claves foráneas
            if table_info["foreign_keys"]:
                summary.append("  FOREIGN KEYS:")
                for fk in table_info["foreign_keys"]:
                    summary.append(f"    {fk['column']} -> {fk['references_table']}.{fk['references_column']}")
        
        # Relaciones
        if self.schema_data["relationships"]:
            summary.append("\nRELACIONES:")
            for rel in self.schema_data["relationships"]:
                summary.append(f"  {rel['table_from']}.{rel['column_from']} -> "
                              f"{rel['table_to']}.{rel['column_to']} ({rel['relationship_type']})")
        
        return "\n".join(summary)


# Función utilitaria para analizar un esquema
def analyze_schema(connection=None, engine=None, depth="full", 
                  include_tables=None, exclude_tables=None) -> Dict[str, Any]:
    """
    Función auxiliar para analizar un esquema de base de datos.
    
    Args:
        connection: Objeto de conexión SQLAlchemy (opcional)
        engine: Objeto engine SQLAlchemy (opcional)
        depth: Nivel de profundidad de análisis
        include_tables: Lista de tablas a incluir
        exclude_tables: Lista de tablas a excluir
        
    Returns:
        Dict: Esquema de la base de datos
    """
    analyzer = SchemaAnalyzer(connection, engine)
    return analyzer.analyze(depth, include_tables, exclude_tables)


# Punto de entrada para pruebas
if __name__ == "__main__":
    import sys
    from db_connector import DBConnector
    
    # Si se proporciona un argumento, úsalo como URI de conexión
    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        try:
            print(f"Conectando a {conn_string}")
            connector = DBConnector()
            status, _ = connector.connect(conn_string)
            
            if status:
                print("Analizando esquema...")
                analyzer = SchemaAnalyzer(connector.connection)
                schema = analyzer.analyze()
                
                print("\nResumen del esquema:")
                print(analyzer.get_schema_summary())
                print("\nEstadísticas:")
                stats = schema["stats"]
                print(f"- Tablas: {stats['tables_count']}")
                print(f"- Columnas: {stats['columns_count']}")
                print(f"- Claves foráneas: {stats['foreign_keys_count']}")
                print(f"- Claves primarias: {stats['primary_keys_count']}")
                
                # Desconectar
                connector.disconnect()
                
            else:
                print("No se pudo conectar a la base de datos")
                
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Uso: python schema_analyzer.py <connection_string>")
        print("Ejemplo: python schema_analyzer.py mysql://user:pass@localhost/dbname")
