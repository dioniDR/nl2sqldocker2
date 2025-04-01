#\!/usr/bin/env python3
"""
app.py - Servidor web para la interfaz de NL2SQL

PROPÓSITO:
    Sirve la interfaz web de usuario para NL2SQL

ENTRADA:
    - Solicitudes HTTP

SALIDA:
    - Páginas HTML

ERRORES:
    - ConfigError: Error de configuración
    - TemplateError: Error en plantillas

DEPENDENCIAS:
    - flask: Framework web
    - jinja2: Motor de plantillas
"""

import sys
from pathlib import Path
import logging
from flask import Flask, render_template

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones internas
from core.config import Config

# Configurar logger
logger = logging.getLogger('web')

# Crear aplicación
app = Flask(__name__)

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

# Para ejecutar como script independiente
if __name__ == "__main__":
    # Obtener puerto de la configuración o usar 8080 por defecto
    port = Config.get('WEB_PORT', 8080)
    
    print(f"Iniciando servidor web en puerto {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)
