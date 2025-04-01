#\!/usr/bin/env python3
"""
main.py - Punto de entrada para la API de NL2SQL

PROPOSITO:
    Inicia el servidor FastAPI y configura middleware y rutas

ENTRADA:
    - Configuracion desde variables de entorno

SALIDA:
    - Servidor API en funcionamiento

ERRORES:
    - ConfigError: Error de configuracion
    - ConnectionError: Error de conexion a base de datos

DEPENDENCIAS:
    - fastapi: Framework API
    - uvicorn: Servidor ASGI
    - core.db_connector: Conexion a base de datos
    - api.routes: Definicion de rutas
    - api.middleware: Middleware personalizado
"""

import sys
from pathlib import Path
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones internas
from core.config import Config
from core.db_connector import connect as db_connect
from api.routes import router as api_router

# Configurar logger
logger = logging.getLogger('api')

# Crear aplicacion
app = FastAPI(
    title="NL2SQL API",
    description="API para consultar datos SQL con lenguaje natural",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En produccion, limitar a origenes especificos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas de la API
app.include_router(api_router, prefix="/api")

# Ruta raiz
@app.get("/")
async def root():
    """Endpoint raiz para verificar que la API esta funcionando."""
    return {
        "status": "online",
        "api_version": "1.0.0",
        "message": "NL2SQL API esta funcionando correctamente"
    }

# Ruta de estado de la BD
@app.get("/status")
async def status():
    """Endpoint para verificar el estado de la conexion a la base de datos."""
    try:
        # Intentar conexion a la base de datos
        connector = db_connect()
        
        if connector.is_connected:
            tables = connector.get_tables()
            table_count = len(tables)
            result = {
                "status": "online",
                "database": "connected",
                "tables": table_count,
                "table_list": list(tables.keys())
            }
        else:
            result = {
                "status": "online",
                "database": "error",
                "message": "No se pudo conectar a la base de datos"
            }
        
        connector.disconnect()
        return result
        
    except Exception as e:
        logger.error(f"Error en status: {str(e)}")
        return {
            "status": "online",
            "database": "error",
            "message": str(e)
        }

# Para ejecutar como script independiente
if __name__ == "__main__":
    # Obtener puerto de la configuracion o usar 8000 por defecto
    port = Config.get('API_PORT', 8000)
    
    print(f"Iniciando servidor API en puerto {port}...")
    uvicorn.run("api.main:app", host="0.0.0.0", port=port, reload=True)
