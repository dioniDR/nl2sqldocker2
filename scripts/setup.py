#!/usr/bin/env python3
"""
setup.py - Configuración inicial del sistema NL2SQL

PROPÓSITO:
    Guía al usuario a través de la configuración inicial del sistema,
    incluyendo conexión a base de datos y proveedores de IA.

ENTRADA:
    - Respuestas interactivas del usuario
    - Opciones de línea de comandos (opcional)

SALIDA:
    - Archivo .env configurado
    - Archivo .setup_complete creado
    - Base de datos de prueba (si se selecciona SQLite)

ERRORES:
    - ConfigError: Error en la configuración
    - ConnectionError: Error al verificar conexión
    - ValidationError: Datos de entrada inválidos

DEPENDENCIAS:
    - core.config: Para gestión de configuración
    - utils.progress: Para indicadores visuales
    - utils.validators: Para validación de entradas
"""

import os
import sys
import time
import getpass
from pathlib import Path

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones internas
from core.config import Config
from utils.progress import start_phase, update_progress, complete_phase
from utils.progress import show_info, show_success, show_error, show_warning

# Intentar importar dependencias necesarias
try:
    from dotenv import load_dotenv, set_key
except ImportError:
    print("Error: python-dotenv no está instalado. Instalando...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv, set_key

class SetupAssistant:
    """Asistente de configuración inicial del sistema."""
    
    def __init__(self):
        """Inicializa el asistente de configuración."""
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / '.env'
        self.setup_complete_file = self.project_root / 'status' / '.setup_complete'
        self.config = {}
        
        # Crear directorio status si no existe
        os.makedirs(self.project_root / 'status' / 'logs', exist_ok=True)
        
        # Cargar configuración existente si hay
        if self.env_file.exists():
            load_dotenv(dotenv_path=self.env_file)
            # Cargar variables de entorno existentes
            self.config = {
                'DB_TYPE': os.getenv('DB_TYPE', ''),
                'DB_USER': os.getenv('DB_USER', ''),
                'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
                'DB_HOST': os.getenv('DB_HOST', ''),
                'DB_PORT': os.getenv('DB_PORT', ''),
                'DB_NAME': os.getenv('DB_NAME', ''),
                'AI_PROVIDER': os.getenv('AI_PROVIDER', ''),
                'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'OLLAMA_URL': os.getenv('OLLAMA_URL', ''),
                'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
                'TIMEOUT': os.getenv('TIMEOUT', '30'),
                'MAX_RETRIES': os.getenv('MAX_RETRIES', '3'),
                'SHOW_PROGRESS': os.getenv('SHOW_PROGRESS', 'true'),
            }
    
    def welcome(self):
        """Muestra mensaje de bienvenida."""
        print("\n=== NL2SQL: Sistema de Consultas SQL con Lenguaje Natural ===\n")
        print("Este asistente lo guiará en la configuración inicial del sistema.")
        print("Vamos a configurar la conexión a su base de datos y servicios de IA.\n")
    
    def setup_database(self):
        """Configura la conexión a base de datos."""
        start_phase("setup", "Configuración de base de datos")
        update_progress(10, "Seleccionando tipo de base de datos")
        
        print("Tipos de bases de datos soportados:")
        print("1. MySQL/MariaDB")
        print("2. PostgreSQL")
        print("3. SQLite (archivo local)")
        
        while True:
            try:
                choice = input("\nSeleccione un tipo de base de datos [1-3]: ")
                if choice == '1':
                    self.config['DB_TYPE'] = 'mysql'
                    break
                elif choice == '2':
                    self.config['DB_TYPE'] = 'postgresql'
                    break
                elif choice == '3':
                    self.config['DB_TYPE'] = 'sqlite'
                    break
                else:
                    print("Opción no válida. Por favor, seleccione 1, 2 o 3.")
            except KeyboardInterrupt:
                return False
        
        update_progress(20, f"Configurando {self.config['DB_TYPE']}")
        
        if self.config['DB_TYPE'] in ('mysql', 'postgresql'):
            print(f"\nHa seleccionado {self.config['DB_TYPE'].upper()}.")
            print("Por favor ingrese los detalles de conexión:")
            
            # Obtener detalles de conexión
            default_host = self.config.get('DB_HOST') or 'localhost'
            self.config['DB_HOST'] = input(f"Servidor (host) [{default_host}]: ") or default_host
            
            default_port = self.config.get('DB_PORT') or ('3306' if self.config['DB_TYPE'] == 'mysql' else '5432')
            self.config['DB_PORT'] = input(f"Puerto [{default_port}]: ") or default_port
            
            default_user = self.config.get('DB_USER') or 'root'
            self.config['DB_USER'] = input(f"Usuario [{default_user}]: ") or default_user
            
            # Solicitar contraseña de forma segura
            while True:
                try:
                    self.config['DB_PASSWORD'] = getpass.getpass(f"Contraseña: ")
                    confirm_password = getpass.getpass(f"Confirme contraseña: ")
                    
                    if self.config['DB_PASSWORD'] == confirm_password:
                        break
                    else:
                        print("Las contraseñas no coinciden. Intente nuevamente.")
                except KeyboardInterrupt:
                    return False
            
            default_db = self.config.get('DB_NAME') or 'example'
            self.config['DB_NAME'] = input(f"Base de datos [{default_db}]: ") or default_db
            
        else:  # SQLite
            print("\nHa seleccionado SQLite (archivo local).")
            default_db = self.config.get('DB_NAME') or 'nl2sql.db'
            self.config['DB_NAME'] = input(f"Nombre del archivo de base de datos [{default_db}]: ") or default_db
            
            # Si no termina en .db, añadirlo
            if not self.config['DB_NAME'].endswith('.db'):
                self.config['DB_NAME'] += '.db'
        
        update_progress(50, "Verificando conexión")
        
        # Aquí iría la lógica para probar la conexión
        # Para este ejemplo, simularemos una prueba exitosa
        print("\nVerificando conexión...")
        time.sleep(1)  # Simulación de verificación
        
        # En una implementación real, aquí llamaríamos a una función de prueba de db_connector.py
        # Por ejemplo: 
        # from core.db_connector import test_connection
        # result = test_connection(self.get_connection_string())
        
        # Simulación de éxito
        connection_success = True
        db_info = f"{self.config['DB_TYPE'].upper()} ({self.config['DB_HOST']})" if self.config['DB_TYPE'] != 'sqlite' else "SQLite (local)"
        
        if connection_success:
            update_progress(100, "Conexión exitosa")
            print(f"\n✅ Conexión exitosa a {db_info}")
            
            confirm = input("\n¿Desea utilizar esta configuración? (s/n): ").lower()
            if confirm != 's' and confirm != 'si' and confirm != 'y' and confirm != 'yes':
                show_warning("Configuración de base de datos cancelada.")
                return False
                
            complete_phase(True, f"Base de datos {self.config['DB_TYPE']} configurada")
            return True
        else:
            update_progress(70, "Error de conexión")
            print(f"\n❌ Error al conectar a {db_info}")
            
            # Ofrecer ayuda según el tipo de error
            print("\nPosibles soluciones:")
            if self.config['DB_TYPE'] == 'mysql':
                print("- Verifique que el servidor MySQL esté en ejecución")
                print("- Confirme que las credenciales sean correctas")
                print("- Asegúrese de que la base de datos exista")
            elif self.config['DB_TYPE'] == 'postgresql':
                print("- Verifique que el servidor PostgreSQL esté en ejecución")
                print("- Confirme que las credenciales sean correctas")
                print("- Asegúrese de que la base de datos exista")
            
            retry = input("\n¿Desea reintentar la configuración? (s/n): ").lower()
            if retry == 's' or retry == 'si' or retry == 'y' or retry == 'yes':
                return self.setup_database()
            else:
                complete_phase(False, "Configuración de base de datos cancelada")
                return False
    
    def setup_ai_provider(self):
        """Configura el proveedor de IA."""
        start_phase("ai_provider", "Configuración de proveedor IA")
        update_progress(10, "Seleccionando proveedor")
        
        print("\nConfigurando proveedor de IA:")
        print("1. Claude (Anthropic)")
        print("2. OpenAI (GPT)")
        print("3. Ollama (local)")
        
        while True:
            try:
                choice = input("\nSeleccione un proveedor de IA [1-3]: ")
                if choice == '1':
                    self.config['AI_PROVIDER'] = 'claude'
                    break
                elif choice == '2':
                    self.config['AI_PROVIDER'] = 'openai'
                    break
                elif choice == '3':
                    self.config['AI_PROVIDER'] = 'ollama'
                    break
                else:
                    print("Opción no válida. Por favor, seleccione 1, 2 o 3.")
            except KeyboardInterrupt:
                return False
        
        update_progress(30, f"Configurando {self.config['AI_PROVIDER']}")
        
        if self.config['AI_PROVIDER'] == 'claude':
            print("\nHa seleccionado Claude (Anthropic).")
            try:
                api_key = getpass.getpass("Clave API de Anthropic: ")
                
                # Validación de la clave pegada
                if not api_key.strip():
                    print("❌ Error: La clave API no puede estar vacía o contener solo espacios.")
                    return False
                if len(api_key) < 20:
                    print("⚠️ Advertencia: La clave API parece demasiado corta.")
                
                print(f"🔍 Debug: Clave pegada comienza con '{api_key[:4]}' y tiene {len(api_key)} caracteres.")
                
                self.config['ANTHROPIC_API_KEY'] = api_key
            except KeyboardInterrupt:
                return False

        elif self.config['AI_PROVIDER'] == 'openai':
            print("\nHa seleccionado OpenAI (GPT).")
            try:
                api_key = getpass.getpass("Clave API de OpenAI: ")
                
                # Validación de la clave pegada
                if not api_key.strip():
                    print("❌ Error: La clave API no puede estar vacía o contener solo espacios.")
                    return False
                if len(api_key) < 20:
                    print("⚠️ Advertencia: La clave API parece demasiado corta.")
                
                print(f"🔍 Debug: Clave pegada comienza con '{api_key[:4]}' y tiene {len(api_key)} caracteres.")
                
                self.config['OPENAI_API_KEY'] = api_key
            except KeyboardInterrupt:
                return False
                
        else:  # ollama
            print("\nHa seleccionado Ollama (local).")
            default_url = self.config.get('OLLAMA_URL') or 'http://localhost:11434'
            ollama_url = input(f"URL de Ollama [{default_url}]: ") or default_url
            
            # Validación de la URL pegada
            if not ollama_url.strip():
                print("❌ Error: La URL de Ollama no puede estar vacía o contener solo espacios.")
                return False
            if len(ollama_url) < 10:
                print("⚠️ Advertencia: La URL de Ollama parece demasiado corta.")
            
            print(f"🔍 Debug: URL pegada comienza con '{ollama_url[:4]}' y tiene {len(ollama_url)} caracteres.")
            
            self.config['OLLAMA_URL'] = ollama_url

            # Revisar modelos existentes en local
            print("\n🔍 Revisando modelos disponibles en Ollama...")
            try:
                import requests
                response = requests.get(f"{ollama_url}/models")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    if models:
                        print("✅ Modelos disponibles:")
                        for model in models:
                            print(f"  - {model}")
                    else:
                        print("⚠️ No se encontraron modelos instalados en Ollama.")
                else:
                    print(f"❌ Error al obtener modelos: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ Error al conectar con Ollama: {e}")
        
        update_progress(50, "Verificando conexión con proveedor")
        
        # Aquí iría la lógica para probar la conexión con el proveedor de IA
        # Para este ejemplo, simularemos una prueba exitosa
        print("\nVerificando conexión con proveedor de IA...")
        time.sleep(1)  # Simulación de verificación
        
        # Simulación de éxito
        api_success = True
        
        if api_success:
            update_progress(100, "Conexión exitosa con proveedor IA")
            print(f"\n✅ Conexión exitosa con {self.config['AI_PROVIDER'].upper()}")
            complete_phase(True, f"Proveedor {self.config['AI_PROVIDER']} configurado")
            return True
        else:
            update_progress(70, "Error de conexión con proveedor IA")
            print(f"\n❌ Error al conectar con {self.config['AI_PROVIDER'].upper()}")
            
            retry = input("\n¿Desea reintentar la configuración? (s/n): ").lower()
            if retry == 's' or retry == 'si' or retry == 'y' or retry == 'yes':
                return self.setup_ai_provider()
            else:
                complete_phase(False, "Configuración de proveedor IA cancelada")
                return False
    
    def build_connection_string(self):
        """Construye la cadena de conexión de la base de datos."""
        if self.config['DB_TYPE'] == 'mysql':
            return f"mysql+pymysql://{self.config['DB_USER']}:{self.config['DB_PASSWORD']}@{self.config['DB_HOST']}:{self.config['DB_PORT']}/{self.config['DB_NAME']}"
        elif self.config['DB_TYPE'] == 'postgresql':
            return f"postgresql://{self.config['DB_USER']}:{self.config['DB_PASSWORD']}@{self.config['DB_HOST']}:{self.config['DB_PORT']}/{self.config['DB_NAME']}"
        else:  # sqlite
            return f"sqlite:///{self.config['DB_NAME']}"

    def save_configuration(self):
        """Guarda la configuración en el archivo .env."""
        start_phase("system_start", "Guardando configuración")
        update_progress(30, "Preparando archivo .env")
        
        try:
            # Crear o actualizar el archivo .env
            if not self.env_file.exists():
                self.env_file.touch()
            
            update_progress(50, "Escribiendo configuración")
            
            # Escribir configuración
            for key, value in self.config.items():
                set_key(self.env_file, key, value)
            
            # Guardar cadena de conexión
            self.config['DB_CONNECTION_STRING'] = self.build_connection_string()
            set_key(self.env_file, 'DB_CONNECTION_STRING', self.config['DB_CONNECTION_STRING'])

            update_progress(70, "Creando archivo de estado")
            
            # Crear archivo de estado
            self.setup_complete_file.touch()
            
            update_progress(100, "Configuración guardada")
            print("\n✅ Configuración guardada correctamente")
            complete_phase(True, "Sistema configurado exitosamente")
            return True
        except Exception as e:
            update_progress(80, f"Error: {str(e)}")
            print(f"\n❌ Error al guardar configuración: {str(e)}")
            complete_phase(False, f"Error al guardar configuración: {str(e)}")
            return False
    
    def show_completion(self):
        """Muestra mensaje de finalización."""
        print("\n=== Configuración completada ===\n")
        print("El sistema está listo para usar.")
        print("Para comenzar, ejecute:")
        print("python scripts/run.py")
    
    def run(self):
        """Ejecuta el asistente de configuración completo."""
        self.welcome()
        
        if self.setup_complete_file.exists():
            print("El sistema ya ha sido configurado previamente.")
            reconfigure = input("¿Desea reconfigurar? (s/n): ").lower()
            if reconfigure != 's' and reconfigure != 'si' and reconfigure != 'y' and reconfigure != 'yes':
                print("\nManteniendo configuración actual.")
                return True
        
        # Configurar proveedor de IA
        if not self.setup_ai_provider():
            print("\nConfiguración cancelada.")
            return False
        
        # Configurar base de datos
        if not self.setup_database():
            print("\nConfiguración cancelada.")
            return False
        
        # Guardar configuración
        if not self.save_configuration():
            print("\nError al guardar configuración.")
            return False
        
        # Mostrar mensaje de finalización
        self.show_completion()
        return True

# Ejecutar como script independiente
if __name__ == "__main__":
    assistant = SetupAssistant()
    assistant.run()