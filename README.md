# NL2SQL: Sistema de Consultas SQL con Lenguaje Natural

Este proyecto proporciona una interfaz para consultar bases de datos usando lenguaje natural.

## Requisitos

- Python 3.8+
- MySQL Server (o Docker con MySQL)
- Credenciales de acceso para servicios de IA (opcional)

## Configuración Inicial

1. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Ejecutar el script de configuración:

```bash
python scripts/setup.py
```

3. Poblar la base de datos con datos de prueba:

```bash
mysql -h 127.0.0.1 -P 3307 -u root -ppassword testdb < populate_tables.sql
```

## Estructura de la Base de Datos

El sistema está configurado para trabajar con tres tablas principales:

- **clientes**: Información de clientes
- **productos**: Catálogo de productos
- **ventas**: Registro de transacciones

## Uso

### Iniciar la API y el Frontend

```bash
# Iniciar ambos servicios
python launch.py

# Iniciar solo la API
python launch.py --api-only

# Iniciar solo el frontend
python launch.py --web-only
```

### Acceder a la Aplicación

- **API**: http://localhost:8000
- **Frontend**: http://localhost:8080

### Endpoints API

- `/api/clientes`: Lista de clientes con filtros opcionales
- `/api/productos`: Lista de productos con filtros opcionales
- `/api/ventas`: Lista de ventas con filtros opcionales
- `/api/ventas/{id}`: Detalles de una venta específica

## Pruebas

Para probar la funcionalidad:

```bash
python test_api.py
```
# NL2SQL: Sistema Modular de Consultas SQL con Lenguaje Natural

## Descripción

NL2SQL es un sistema modular que permite generar consultas SQL a partir de instrucciones en lenguaje natural. El sistema analiza la estructura de una base de datos, interpreta consultas del usuario en lenguaje natural y genera el SQL correspondiente utilizando modelos de IA.

Este repositorio contiene dos componentes principales:
1. **El proyecto NL2SQL en desarrollo** - Sistema modular basado en IA para generar SQL desde lenguaje natural
2. **Una API REST funcional con interfaz web** - Para consultas básicas a bases de datos (ya implementada)

## Filosofía de Diseño del Proyecto NL2SQL

Este proyecto sigue una filosofía de diseño centrada en:

1. **Modularidad extrema**: Cada archivo tiene una única responsabilidad bien definida
2. **Depuración sencilla**: Cada archivo puede ejecutarse y probarse de forma independiente
3. **Documentación incorporada**: Cada módulo documenta claramente qué esperar y cómo usarlo
4. **Manejo robusto de errores**: Estados de error bien definidos y respuestas claras
5. **Retroalimentación visual**: Indicadores de progreso para cada fase del proceso
6. **Adaptabilidad**: Funciona con cualquier base de datos mediante análisis dinámico de esquemas

## Requisitos

- Python 3.8+
- MySQL/MariaDB, PostgreSQL o SQLite
- Credenciales de acceso para servicios de IA (opcional)

## Instalación

1. Crear un entorno virtual e instalar dependencias:

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Ejecutar el script de configuración:

```bash
python scripts/setup.py
```

## Estructura del Repositorio

```
/nl2sqldocker2/                # Directorio principal
│
├── core/                      # Núcleo del proyecto NL2SQL
│   ├── __init__.py
│   ├── config.py              # Gestión de configuración
│   ├── db_connector.py        # Conexión dinámica a BD
│   ├── schema_analyzer.py     # Análisis de esquemas BD
│   └── sql_generator.py       # Generación de SQL
│
├── providers/                 # Proveedores de IA para NL2SQL
│   ├── __init__.py
│   ├── base.py                # Clase base para proveedores
│   ├── claude.py              # Implementación de Claude
│   ├── ollama.py              # Implementación de Ollama
│   └── openai_client.py       # Implementación de OpenAI
│
├── utils/                     # Utilidades compartidas
│   ├── __init__.py
│   ├── config_helpers.py      # Funciones de configuración
│   ├── config_diagnostics.py  # Diagnóstico de configuración
│   ├── db_helpers.py          # Ayudantes para base de datos
│   ├── error_handler.py       # Manejo de errores
│   ├── formatter.py           # Formato de resultados
│   ├── progress.py            # Indicadores de progreso
│   ├── state_tracker.py       # Seguimiento de estado
│   └── validators.py          # Validación de entradas
│
├── cli/                       # CLI para proyecto NL2SQL
│   ├── __init__.py
│   ├── interactive.py         # CLI interactiva
│   └── commands/              # Comandos de CLI
│       ├── __init__.py
│       ├── db_commands.py     # Comandos de base de datos
│       └── query_commands.py  # Comandos de consulta
│
├── api/                       # API REST funcional
│   ├── __init__.py
│   ├── main.py                # Punto de entrada API
│   ├── routes.py              # Rutas de API
│   └── middleware.py          # Middleware de API
│
├── web/                       # Interfaz web 
│   ├── templates/             # Plantillas HTML
│   │   └── index.html         # Página principal
│   └── app.py                 # Servidor web
│
├── scripts/                   # Scripts de utilidad para NL2SQL
│   ├── debug.py               # Herramientas de diagnóstico
│   ├── reset.py               # Reinicio de configuración
│   ├── run.py                 # Script principal de ejecución
│   ├── setup.py               # Configuración inicial
│   └── test_core.py           # Pruebas de componentes core
│
├── status/                    # Estado del sistema NL2SQL
│   ├── .setup_complete        # Bandera de configuración
│   ├── .last_checkpoint       # Último punto de control
│   └── logs/                  # Registros de operación
│
├── .env                       # Variables de entorno
├── .gitignore                 # Archivos ignorados por git
├── launch.py                  # Script para iniciar servicios
├── populate_tables.sql        # Script SQL para poblar tablas
├── requirements.txt           # Dependencias
├── test_api.py                # Pruebas de API
├── api.log                    # Logs de la API
├── web.log                    # Logs del servidor web
└── CLAUDE.md                  # Guía de desarrollo
```

## Componentes Principales

### 1. Proyecto NL2SQL (En Desarrollo)

El proyecto NL2SQL está diseñado para convertir lenguaje natural en consultas SQL mediante análisis de esquemas y modelos de IA. Está organizado en módulos independientes siguiendo la filosofía de modularidad extrema.

#### Estado de Implementación de NL2SQL
- ✅ Estructura de carpetas principal
- ✅ Módulo de configuración (`core/config.py`)
- ✅ Sistema de progreso visual (`utils/progress.py`)
- ✅ Conector de base de datos (`core/db_connector.py`)
- ✅ Analizador de esquemas (`core/schema_analyzer.py`)
- ✅ Script de configuración (`scripts/setup.py`)
- ✅ Script de ejecución (`scripts/run.py`)
- ⏳ Proveedores de IA (archivos creados pero sin implementación completa)
- ⏳ CLI interactiva (estructura creada)
- ⏳ Generador de SQL (`core/sql_generator.py` en desarrollo)

#### Uso del Proyecto NL2SQL
```bash
# Configurar el sistema
python scripts/setup.py

# Iniciar el sistema
python scripts/run.py
```

El flujo de ejecución del sistema NL2SQL incluye:
1. Validación de configuración
2. Conexión a base de datos
3. Análisis del esquema
4. Verificación del proveedor de IA
5. Inicio del sistema

### 2. API REST Funcional con Interfaz Web

Paralelamente al desarrollo de NL2SQL, el repositorio contiene una API REST funcional que permite interactuar con bases de datos a través de endpoints predefinidos y una interfaz web sencilla. **Esta parte del proyecto ya está implementada y funcional**.

#### Componentes de la API REST Funcional
- ✅ API REST con FastAPI (`api/main.py`, `api/routes.py`, `api/middleware.py`)
- ✅ Interfaz web simple (`web/app.py`, `web/templates/index.html`)
- ✅ Endpoints para acceso a datos (`/api/clientes`, `/api/productos`, `/api/ventas`)
- ✅ Script para lanzar servicios (`launch.py`)
- ✅ Script para poblar tablas (`populate_tables.sql`)

#### Uso de la API REST
```bash
# Iniciar ambos servicios
python launch.py

# Iniciar solo la API
python launch.py --api-only

# Iniciar solo el frontend
python launch.py --web-only
```

#### Acceso a la API y Interfaz Web
- **API**: http://localhost:8000
- **API Status**: http://localhost:8000/status
- **Frontend**: http://localhost:8080

#### Endpoints API
- `GET /api/clientes`: Lista de clientes con filtros opcionales
- `GET /api/productos`: Lista de productos con filtros opcionales
- `GET /api/ventas`: Lista de ventas con filtros opcionales
- `GET /api/ventas/{id}`: Detalles de una venta específica con información de cliente y producto

## Distinción Entre Ambos Componentes

Es importante entender que este repositorio contiene dos sistemas relacionados pero distintos:

1. **NL2SQL (En desarrollo)**: El sistema principal en desarrollo que usará IA para convertir lenguaje natural a SQL.
   - Utiliza principalmente los directorios `core/`, `providers/`, `utils/`, `cli/` y `scripts/`
   - Se ejecuta con `python scripts/run.py`
   - Sigue la filosofía de diseño modular y documentación exhaustiva

2. **API REST con Interfaz Web (Funcional)**: Un sistema ya implementado para consultas básicas a bases de datos.
   - Utiliza principalmente `api/`, `web/` y los scripts en la raíz como `launch.py`
   - Se ejecuta con `python launch.py`
   - Proporciona endpoints REST y una interfaz web sin CSS pero funcional

Ambos componentes comparten el mismo repositorio pero tienen propósitos diferentes. La API funcional puede servir como referencia o como sistema de prueba mientras se desarrolla el proyecto principal NL2SQL.

## Pruebas

```bash
# Probar componentes core de NL2SQL
python scripts/test_core.py

# Probar API funcional
python test_api.py
```

## Características Futuras (Proyecto NL2SQL)

- Sistema de importación de datos desde Excel, CSV y otras fuentes
- Explorador automático de bases de datos
- Modo de conversación con memoria de contexto
- Caché inteligente para optimizar el rendimiento
- Creación dinámica de endpoints REST
- Modo de uso cruzado con fuentes externas

## Contribuir

1. Para contribuir, primero revisa la estructura modular y la filosofía de diseño
2. Cada módulo debe tener una responsabilidad única y menos de 100 líneas
3. Todo el código debe incluir documentación con secciones PROPÓSITO, ENTRADA, SALIDA, ERRORES y DEPENDENCIAS
4. Asegúrate de que cada módulo se pueda ejecutar y probar de forma independiente

## Licencia

Este proyecto es software libre y puedes utilizarlo bajo los términos de la licencia MIT.
