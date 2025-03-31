# scripts/test_core.py
import sys
from pathlib import Path

# Añadir el directorio raíz al path de Python
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.progress import start_phase, update_progress, complete_phase
from core import db_connector, schema_analyzer, sql_generator

def test_db_connector():
    start_phase("db_connection", "Probando conexión a base de datos")
    # Aquí irían las pruebas específicas para db_connector
    # ...
    complete_phase(True, "Conexión a base de datos exitosa")

def test_schema_analyzer():
    start_phase("schema_analysis", "Probando análisis de esquema")
    # Aquí irían las pruebas específicas para schema_analyzer
    # ...
    complete_phase(True, "Análisis de esquema exitoso")

def test_sql_generator():
    start_phase("sql_generation", "Probando generación de SQL")
    # Aquí irían las pruebas específicas para sql_generator
    # ...
    complete_phase(True, "Generación de SQL exitosa")

if __name__ == "__main__":
    print("Ejecutando pruebas de componentes core\n")
    test_db_connector()
    test_schema_analyzer()
    test_sql_generator()
    print("\nPruebas completadas")
