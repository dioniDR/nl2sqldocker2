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