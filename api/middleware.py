#\!/usr/bin/env python3
"""
middleware.py - Middleware para la API de NL2SQL

PROPOSITO:
    Define middleware para la API FastAPI

ENTRADA:
    - Solicitudes HTTP

SALIDA:
    - Solicitudes procesadas

ERRORES:
    - AuthError: Errores de autenticacion
    - RateLimitError: Errores de limite de velocidad

DEPENDENCIAS:
    - fastapi: Framework API
    - starlette: HTTP y middleware
"""

import sys
import time
import logging
from pathlib import Path
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar logger
logger = logging.getLogger('api.middleware')

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para registrar solicitudes y respuestas."""
    
    async def dispatch(self, request: Request, call_next):
        """Procesa la solicitud y registra informacion relevante."""
        start_time = time.time()
        
        # Registrar la solicitud
        logger.info(f"Solicitud: {request.method} {request.url.path}")
        
        # Procesar la solicitud
        response = await call_next(request)
        
        # Calcular tiempo de procesamiento
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
        
        # Registrar la respuesta
        logger.info(f"Respuesta: {response.status_code} - {process_time:.2f}ms")
        
        return response
