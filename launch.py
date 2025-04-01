#!/usr/bin/env python3
"""
launch.py - Script para iniciar los servicios de NL2SQL

PROPÓSITO:
    Inicia el servidor API y la interfaz web

ENTRADA:
    - Argumentos de línea de comandos

SALIDA:
    - Servidores en ejecución

ERRORES:
    - ConfigError: Error de configuración
    - ProcessError: Error al iniciar procesos

DEPENDENCIAS:
    - subprocess: Para ejecutar procesos
    - core.config: Para configuración global
"""

import sys
import os
import time
import subprocess
import signal
import argparse
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent))

# Importaciones internas
from core.config import Config

# Procesos en ejecución
processes = []

def signal_handler(sig, frame):
    """Manejador de señales para terminar procesos al salir."""
    print("\nDeteniendo servicios...")
    for proc in processes:
        if proc.poll() is None:  # Si el proceso sigue en ejecución
            proc.terminate()
    sys.exit(0)

def start_api():
    """Inicia el servidor API."""
    print("Iniciando servidor API...")
    api_process = subprocess.Popen([
        sys.executable, 
        "-m", "api.main"
    ], env=os.environ.copy())
    processes.append(api_process)
    return api_process

def start_web():
    """Inicia el servidor web."""
    print("Iniciando servidor web...")
    web_process = subprocess.Popen([
        sys.executable, 
        "-m", "web.app"
    ], env=os.environ.copy())
    processes.append(web_process)
    return web_process

def main():
    """Función principal."""
    parser = argparse.ArgumentParser(description="Inicia los servicios de NL2SQL")
    parser.add_argument("--api-only", action="store_true", help="Iniciar solo la API")
    parser.add_argument("--web-only", action="store_true", help="Iniciar solo la web")
    args = parser.parse_args()
    
    # Configurar manejador de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Iniciar servicios según argumentos
        if args.api_only:
            api_proc = start_api()
            api_proc.wait()
        elif args.web_only:
            web_proc = start_web()
            web_proc.wait()
        else:
            # Iniciar ambos servicios
            api_proc = start_api()
            time.sleep(2)  # Esperar a que la API esté lista
            web_proc = start_web()
            
            # Imprimir URLs de acceso
            api_port = Config.get('API_PORT', 8000)
            web_port = Config.get('WEB_PORT', 8080)
            print("\n=== Servicios NL2SQL iniciados ===")
            print(f"API disponible en: http://localhost:{api_port}")
            print(f"Web disponible en: http://localhost:{web_port}")
            print("\nPresione Ctrl+C para detener los servicios\n")
            
            # Esperar a que terminen los procesos
            while True:
                if api_proc.poll() is not None:
                    print("El servidor API se ha detenido")
                    break
                if web_proc.poll() is not None:
                    print("El servidor web se ha detenido")
                    break
                time.sleep(1)
    
    except Exception as e:
        print(f"Error al iniciar servicios: {e}")
    finally:
        # Asegurar que todos los procesos se detengan
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()

if __name__ == "__main__":
    main()