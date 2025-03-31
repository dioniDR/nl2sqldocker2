#!/usr/bin/env python3
"""
config_helpers.py - Funciones auxiliares básicas para la configuración

PROPÓSITO:
    Proporciona funciones de utilidad básicas para el módulo de configuración.

ENTRADA:
    - Llamadas a funciones con parámetros específicos

SALIDA:
    - Valores de utilidad para configuración

DEPENDENCIAS:
    - logging: Para registro de operaciones
    - pathlib: Para manejo de rutas
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Valores predeterminados para parámetros críticos
DEFAULT_CONFIG = {
    # Configuración de base de datos
    'DB_TYPE': 'sqlite',
    'DB_USER': '',
    'DB_PASSWORD': '',
    'DB_HOST': '',
    'DB_PORT': '',
    'DB_NAME': 'nl2sql.db',
    
    # Configuración de proveedores de IA
    'AI_PROVIDER': 'ollama',
    'ANTHROPIC_API_KEY': '',
    'OPENAI_API_KEY': '',
    'OLLAMA_URL': 'http://localhost:11434',
    
    # Configuración del sistema
    'LOG_LEVEL': 'INFO',
    'TIMEOUT': '30',
    'MAX_RETRIES': '3',
    'SHOW_PROGRESS': 'true',
}

def get_project_root() -> Path:
    """
    Determina la ruta raíz del proyecto.
    
    Returns:
        Path: Ruta al directorio raíz del proyecto
    """
    # Asumiendo que este archivo está en utils/ bajo la raíz del proyecto
    return Path(__file__).parent.parent

def setup_logging(name: str) -> logging.Logger:
    """
    Configura un logger con nombre específico.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    return logger

def is_setup_complete(config_get) -> bool:
    """
    Verifica si la configuración inicial está completa.
    
    Args:
        config_get: Función para obtener valores de configuración
        
    Returns:
        True si la configuración está completa, False en caso contrario
    """
    # Comprobar variables mínimas requeridas
    required_configs = [
        'DB_TYPE',
        'AI_PROVIDER',
    ]
    
    for config in required_configs:
        if not config_get(config):
            return False
            
    # Verificar la presencia del archivo de estado
    setup_complete_file = get_project_root() / 'status' / '.setup_complete'
    return setup_complete_file.exists()
