#!/usr/bin/env python3
"""
config_diagnostics.py - Funciones de diagnóstico para configuración

PROPÓSITO:
    Proporciona funciones para diagnóstico y visualización de configuración.

ENTRADA:
    - Estado actual de la configuración

SALIDA:
    - Información de diagnóstico formateada

DEPENDENCIAS:
    - utils.config_helpers: Para funciones de configuración básicas
    - utils.db_helpers: Para cadenas de conexión
"""

from utils.config_helpers import get_project_root, is_setup_complete, DEFAULT_CONFIG
from utils.db_helpers import get_db_connection_string

def print_config_summary():
    """
    Imprime un resumen de la configuración actual.
    Es útil para diagnóstico cuando se ejecuta config.py directamente.
    """
    # Importación circular pero solo para diagnóstico
    from core.config import Config, ENV_FILE
    
    project_root = get_project_root()
    
    print("\n=== Configuración del Sistema ===\n")
    
    # Mostrar valores actuales
    print(f"Archivo de configuración: {ENV_FILE}")
    print(f"Estado de la configuración: {'Completa' if is_setup_complete(Config.get) else 'Incompleta'}")
    print("\nValores de configuración cargados:")
    
    # Determinar longitud máxima para alineación
    max_key_len = max(len(k) for k in DEFAULT_CONFIG.keys())
    
    # Categorías para organizar la salida
    db_keys = [k for k in DEFAULT_CONFIG.keys() if k.startswith("DB_")]
    ai_keys = ["AI_PROVIDER", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OLLAMA_URL"]
    system_keys = [k for k in DEFAULT_CONFIG.keys() if k not in db_keys and k not in ai_keys]
    
    categories = {
        "Base de Datos": db_keys,
        "Proveedores IA": ai_keys,
        "Sistema": system_keys
    }
    
    # Mostrar valores por categoría
    for category, keys in categories.items():
        print(f"\n{category}:")
        for key in keys:
            value = Config.get(key)
            # Ocultar contraseñas y claves API
            if any(sensitive in key for sensitive in ("PASSWORD", "API_KEY")):
                if value:
                    value = value[:3] + "*" * (len(value) - 3) if len(value) > 3 else "***"
                else:
                    value = "No configurado"
            # Formatear salida alineada
            print(f"  {key:{max_key_len}} = {value}")
    
    print("\nCadena de conexión a base de datos:")
    print(f"  {get_db_connection_string(Config.get)}")
    
    print("\nDirectorios del proyecto:")
    print(f"  Raíz: {project_root}")
    print(f"  Estado: {project_root / 'status'}")
    print(f"  Logs: {project_root / 'status' / 'logs'}")
    
    print("\n=== Fin del diagnóstico ===\n")

# Para poder ejecutar el diagnóstico directamente
if __name__ == "__main__":
    # Importación circular pero solo para diagnóstico
    from core.config import Config
    print_config_summary()
