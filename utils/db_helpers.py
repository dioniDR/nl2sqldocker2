#!/usr/bin/env python3
"""
db_helpers.py - Funciones auxiliares para conexiones de bases de datos

PROPÓSITO:
    Proporciona funciones de utilidad para conexiones de bases de datos.

ENTRADA:
    - Parámetros de configuración de bases de datos

SALIDA:
    - Cadenas de conexión y utilidades para bases de datos

DEPENDENCIAS:
    - utils.config_helpers: Para funciones de configuración básicas
"""

import logging
from utils.config_helpers import get_project_root, setup_logging

# Configurar logger
logger = setup_logging('db_helpers')

def get_db_connection_string(config_get) -> str:
    """
    Construye la cadena de conexión para SQLAlchemy.
    
    Args:
        config_get: Función para obtener valores de configuración
        
    Returns:
        Cadena de conexión formateada
    """
    db_type = config_get('DB_TYPE')
    project_root = get_project_root()
    
    if db_type == 'sqlite':
        db_path = project_root / config_get('DB_NAME')
        return f"sqlite:///{db_path}"
    
    user = config_get('DB_USER')
    password = config_get('DB_PASSWORD')
    host = config_get('DB_HOST')
    port = config_get('DB_PORT')
    database = config_get('DB_NAME')
    
    if db_type in ('mysql', 'mariadb'):
        # MySQL/MariaDB connection string
        auth = f"{user}:{password}@" if user else ""
        port_str = f":{port}" if port else ""
        return f"mysql+pymysql://{auth}{host}{port_str}/{database}"
    
    elif db_type == 'postgresql':
        # PostgreSQL connection string
        auth = f"{user}:{password}@" if user else ""
        port_str = f":{port}" if port else ""
        return f"postgresql://{auth}{host}{port_str}/{database}"
    
    else:
        logger.error(f"Tipo de base de datos no soportado: {db_type}")
        return ""
