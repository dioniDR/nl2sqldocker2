#!/usr/bin/env python3
"""
config.py - Gestión de configuración del sistema

PROPÓSITO:
    Carga y proporciona acceso a la configuración global del sistema.

ENTRADA:
    - Archivo .env en la raíz del proyecto
    - Variables de entorno del sistema

SALIDA:
    - Variables de configuración accesibles globalmente

ERRORES:
    - ConfigFileNotFoundError: Archivo .env no encontrado
    - ConfigValueError: Valor de configuración inválido

DEPENDENCIAS:
    - python-dotenv: Para cargar variables desde .env
    - utils.config_helpers: Funciones auxiliares de configuración
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Agregar el directorio raíz al path para importaciones
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.config_helpers import (
    get_project_root, 
    setup_logging,
    DEFAULT_CONFIG
)

# Configuración del logger
logger = setup_logging('config')

# Determinar ubicación del proyecto
PROJECT_ROOT = get_project_root()
ENV_FILE = PROJECT_ROOT / '.env'

# Carga de archivo .env
try:
    if not ENV_FILE.exists():
        logger.warning(f"Archivo .env no encontrado en {ENV_FILE}. Se usarán valores predeterminados.")
    else:
        load_dotenv(dotenv_path=ENV_FILE)
        logger.info(f"Configuración cargada desde {ENV_FILE}")
except Exception as e:
    logger.error(f"Error al cargar configuración: {e}")
    raise

class Config:
    """Clase para gestionar la configuración global del sistema."""
    
    @staticmethod
    def get(key, default=None):
        """Obtiene un valor de configuración."""
        # Prioridad: Variable de entorno > .env > DEFAULT_CONFIG > default proporcionado
        value = os.getenv(key)
        
        if value is None:
            value = DEFAULT_CONFIG.get(key, default)
            
        return value
    
    @staticmethod
    def get_bool(key, default=False):
        """Obtiene un valor booleano de configuración."""
        value = Config.get(key, str(default))
        return value.lower() in ('true', 'yes', 'y', '1', 'on')
    
    @staticmethod
    def get_int(key, default=0):
        """Obtiene un valor entero de configuración."""
        try:
            return int(Config.get(key, default))
        except (ValueError, TypeError):
            logger.warning(f"No se pudo convertir {key} a entero, se usa valor predeterminado: {default}")
            return default
    
    @staticmethod
    def get_float(key, default=0.0):
        """Obtiene un valor flotante de configuración."""
        try:
            return float(Config.get(key, default))
        except (ValueError, TypeError):
            logger.warning(f"No se pudo convertir {key} a flotante, se usa valor predeterminado: {default}")
            return default

# Constantes de configuración para usar en todo el código
SHOW_PROGRESS = Config.get_bool('SHOW_PROGRESS', True)
LOG_LEVEL = Config.get('LOG_LEVEL', 'INFO')
TIMEOUT = Config.get_int('TIMEOUT', 30)
MAX_RETRIES = Config.get_int('MAX_RETRIES', 3)
AI_PROVIDER = Config.get('AI_PROVIDER', 'ollama')

# Auto-diagnóstico
if __name__ == "__main__":
    from utils.config_diagnostics import print_config_summary
    print_config_summary()
