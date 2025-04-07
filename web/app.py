#!/usr/bin/env python3
"""
app.py - Servidor web para la interfaz de NL2SQL

PROPÓSITO:
    Sirve la interfaz web de usuario para NL2SQL

ENTRADA:
    - Solicitudes HTTP

SALIDA:
    - Páginas HTML
    - Archivos estáticos (CSS, JavaScript)

ERRORES:
    - ConfigError: Error de configuración
    - TemplateError: Error en plantillas
    - StaticFileError: Error al servir archivos estáticos

DEPENDENCIAS:
    - flask: Framework web
    - jinja2: Motor de plantillas
"""

import sys
import os
from pathlib import Path
import logging
from flask import Flask, render_template, send_from_directory
from dotenv import load_dotenv

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones internas
from core.config import Config

# Configurar logger
logger = logging.getLogger('web')

# Crear directorios para archivos estáticos si no existen
STATIC_FOLDER = Path(__file__).parent / 'static'
CSS_FOLDER = STATIC_FOLDER / 'css'
JS_FOLDER = STATIC_FOLDER / 'js'

# Crear directorios si no existen
CSS_FOLDER.mkdir(parents=True, exist_ok=True)
JS_FOLDER.mkdir(parents=True, exist_ok=True)

# Crear aplicación
app = Flask(__name__, static_folder=str(STATIC_FOLDER))

# Cargar variables de entorno desde .env
load_dotenv()

@app.route('/')
def index():
    """Página principal."""
    return render_template('index.html')

@app.route('/static/css/<path:filename>')
def serve_css(filename):
    """Servir archivos CSS."""
    return send_from_directory(CSS_FOLDER, filename)

@app.route('/static/js/<path:filename>')
def serve_js(filename):
    """Servir archivos JavaScript."""
    return send_from_directory(JS_FOLDER, filename)

# Para ejecutar como script independiente
if __name__ == "__main__":
    # Obtener puerto de la configuración o usar 8081 por defecto
    port = int(os.getenv('WEB_PORT', 8081))
    
    print(f"Iniciando servidor web en puerto {port}...")
    app.run(host="0.0.0.0", port=port, debug=True)