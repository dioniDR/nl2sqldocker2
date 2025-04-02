# Documentación de la Interfaz Web para NL2SQL

## Archivos Creados o Modificados

### Archivos Principales de la API

1. **api/main.py**
   - Punto de entrada para la API FastAPI
   - Configuración CORS para permitir solicitudes desde el frontend
   - Rutas raíz y de estado para verificar la conexión a la base de datos

2. **api/routes.py**
   - Definición de endpoints para consultar tablas
   - Implementación de filtros para cada tipo de datos
   - Modelos Pydantic para validación de datos
   - Consultas SQL parametrizadas

3. **api/middleware.py**
   - Middleware para registrar solicitudes y respuestas
   - Medición del tiempo de procesamiento

### Archivos de la Interfaz Web

4. **web/templates/index.html**
   - Interfaz de usuario para visualizar y filtrar datos
   - Implementación de JavaScript para consultas AJAX a la API
   - Formularios de filtrado para cada tipo de tabla
   - Visualización de datos en formato tabular

5. **web/app.py**
   - Servidor Flask para servir la interfaz web
   - Ruta principal para servir el archivo index.html

### Archivos de Utilidad

6. **launch.py**
   - Script para iniciar tanto la API como el servidor web
   - Gestión de procesos y señales
   - Opciones para iniciar solo la API o solo el frontend

7. **test_api.py**
   - Script para probar los endpoints de la API
   - Verificación de respuestas y visualización de resultados

8. **populate_tables.sql**
   - Script SQL para modificar y poblar las tablas con datos de ejemplo
   - Estructura de las tablas con múltiples campos

## Funcionalidad de la API

### Endpoints disponibles

- **GET /api/clientes**
  - Lista todos los clientes
  - Filtros: nombre, apellido, tipo_cliente, ciudad

- **GET /api/productos**
  - Lista todos los productos
  - Filtros: nombre, categoria, marca, precio_min, precio_max

- **GET /api/ventas**
  - Lista todas las ventas
  - Filtros: cliente_id, producto_id, estado, fecha_inicio, fecha_fin

- **GET /api/ventas/{id}**
  - Muestra detalles de una venta específica, incluyendo información de cliente y producto

### Características

- Esquema de autenticación: No implementado en esta versión
- Paginación: Implementada mediante el parámetro `limit`
- Filtrado: Por múltiples campos según el tipo de datos
- Formato de respuesta: JSON estándar

## Interfaz Web

### Características

- **Selección de Tablas**: Botones para cambiar entre visualización de clientes, productos y ventas
- **Filtros Dinámicos**: Cada tabla tiene su propio conjunto de filtros específicos
- **Visualización de Datos**: Tabla interactiva que muestra los datos según los filtros aplicados
- **Interfaz Minimalista**: Sin CSS, enfocado en la funcionalidad

### Flujo de Trabajo

1. El usuario selecciona una tabla (clientes, productos o ventas)
2. Se cargan los datos por defecto y se muestran los filtros específicos
3. El usuario puede aplicar filtros según necesite
4. Al hacer clic en "Filtrar", se realiza una consulta a la API con los parámetros
5. Los resultados se muestran en formato tabular

## Cómo Ejecutar

1. **Iniciar ambos servicios**:
   ```bash
   python launch.py
   ```

2. **Iniciar solo la API**:
   ```bash
   python launch.py --api-only
   ```

3. **Iniciar solo el frontend**:
   ```bash
   python launch.py --web-only
   ```

## Acceso

- **API**: http://localhost:8000
  - Documentación interactiva: http://localhost:8000/docs

- **Frontend**: http://localhost:8080

## Notas Técnicas

- La API utiliza FastAPI para un rendimiento óptimo y tipado estático
- El frontend utiliza JavaScript puro, sin frameworks adicionales
- Los servidores API y web se ejecutan en puertos separados
- Se implementa CORS para permitir la comunicación entre servidores
- Las consultas a la base de datos utilizan parámetros para evitar inyección SQL

## Limitaciones y Mejoras Futuras

- **Autenticación**: Implementar sistema de autenticación para proteger los datos
- **CSS y Diseño**: Mejorar la apariencia visual con estilos CSS
- **Paginación en Frontend**: Implementar navegación entre páginas de resultados
- **Edición de Datos**: Añadir funcionalidad para crear, editar y eliminar registros
- **Ordenamiento**: Permitir ordenar por columnas en las tablas
- **Exportación**: Agregar opciones para exportar datos a CSV o Excel