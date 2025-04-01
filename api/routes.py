#\!/usr/bin/env python3
"""
routes.py - Rutas de la API de NL2SQL

PROPOSITO:
    Define los endpoints de la API

ENTRADA:
    - Solicitudes HTTP
    - Parametros de consulta

SALIDA:
    - Respuestas JSON

ERRORES:
    - ValidationError: Errores de validacion de datos
    - DBError: Errores de base de datos
    - NotFoundError: Recurso no encontrado

DEPENDENCIAS:
    - fastapi: Framework API
    - core.db_connector: Conexion a base de datos
    - pydantic: Validacion de modelos
"""

import sys
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query, HTTPException, Depends

# Asegurar que el directorio raiz este en el path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importaciones desde Pydantic para validacion
from pydantic import BaseModel

# Importaciones internas
from core.db_connector import DBConnector, connect as db_connect

# Configurar logger
logger = logging.getLogger('api.routes')

# Crear router
router = APIRouter()

# Modelos para validacion de datos
class Cliente(BaseModel):
    id: int
    nombre: str
    email: Optional[str] = None
    fecha_registro: Optional[str] = None
    apellido: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    pais: Optional[str] = None
    limite_credito: Optional[float] = None
    comentarios: Optional[str] = None
    tipo_cliente: Optional[str] = None

class Producto(BaseModel):
    id: int
    nombre: str
    precio: Optional[float] = None
    existencias: Optional[int] = None
    descripcion: Optional[str] = None
    categoria: Optional[str] = None
    marca: Optional[str] = None
    codigo_barras: Optional[str] = None
    fecha_creacion: Optional[str] = None
    peso: Optional[float] = None
    color: Optional[str] = None
    dimensiones: Optional[str] = None
    proveedor_id: Optional[int] = None

class Venta(BaseModel):
    id: int
    cliente_id: Optional[int] = None
    producto_id: Optional[int] = None
    fecha: Optional[str] = None
    total: Optional[float] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[float] = None
    descuento: Optional[float] = None
    impuesto: Optional[float] = None
    estado: Optional[str] = None
    metodo_pago: Optional[str] = None
    notas: Optional[str] = None
    vendedor_id: Optional[int] = None

# Dependencia para obtener conexion a BD
def get_db():
    """Obtiene conexion a la base de datos para usar como dependencia."""
    connector = db_connect()
    try:
        if not connector.is_connected:
            raise HTTPException(status_code=500, detail="Error de conexion a base de datos")
        yield connector
    finally:
        connector.disconnect()

# Rutas para clientes
@router.get("/clientes", response_model=List[Cliente])
async def get_clientes(
    db: DBConnector = Depends(get_db),
    nombre: Optional[str] = None, 
    apellido: Optional[str] = None,
    tipo_cliente: Optional[str] = None,
    ciudad: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtiene lista de clientes con filtros opcionales."""
    
    query = "SELECT * FROM clientes WHERE 1=1"
    params = {}
    
    # Aplicar filtros si se proporcionan
    if nombre:
        query += " AND nombre LIKE :nombre"
        params["nombre"] = f"%{nombre}%"
        
    if apellido:
        query += " AND apellido LIKE :apellido"
        params["apellido"] = f"%{apellido}%"
        
    if tipo_cliente:
        query += " AND tipo_cliente = :tipo_cliente"
        params["tipo_cliente"] = tipo_cliente
        
    if ciudad:
        query += " AND ciudad LIKE :ciudad"
        params["ciudad"] = f"%{ciudad}%"
    
    # Limitar resultados
    query += f" LIMIT {limit}"
    
    success, result = db.execute_query(query, params)
    
    if not success:
        logger.error(f"Error al obtener clientes: {result}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {result}")
    
    clientes = []
    for row in result:
        cliente = dict(row._mapping)
        
        # Convertir fechas a string para JSON
        if cliente.get("fecha_registro"):
            cliente["fecha_registro"] = str(cliente["fecha_registro"])
            
        clientes.append(cliente)
    
    return clientes

# Rutas para productos
@router.get("/productos", response_model=List[Producto])
async def get_productos(
    db: DBConnector = Depends(get_db),
    nombre: Optional[str] = None,
    categoria: Optional[str] = None,
    marca: Optional[str] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtiene lista de productos con filtros opcionales."""
    
    query = "SELECT * FROM productos WHERE 1=1"
    params = {}
    
    # Aplicar filtros si se proporcionan
    if nombre:
        query += " AND nombre LIKE :nombre"
        params["nombre"] = f"%{nombre}%"
        
    if categoria:
        query += " AND categoria LIKE :categoria"
        params["categoria"] = f"%{categoria}%"
        
    if marca:
        query += " AND marca LIKE :marca"
        params["marca"] = f"%{marca}%"
        
    if precio_min is not None:
        query += " AND precio >= :precio_min"
        params["precio_min"] = precio_min
        
    if precio_max is not None:
        query += " AND precio <= :precio_max"
        params["precio_max"] = precio_max
    
    # Limitar resultados
    query += f" LIMIT {limit}"
    
    success, result = db.execute_query(query, params)
    
    if not success:
        logger.error(f"Error al obtener productos: {result}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {result}")
    
    productos = []
    for row in result:
        producto = dict(row._mapping)
        
        # Convertir fechas a string para JSON
        if producto.get("fecha_creacion"):
            producto["fecha_creacion"] = str(producto["fecha_creacion"])
            
        productos.append(producto)
    
    return productos

# Rutas para ventas
@router.get("/ventas", response_model=List[Venta])
async def get_ventas(
    db: DBConnector = Depends(get_db),
    cliente_id: Optional[int] = None,
    producto_id: Optional[int] = None,
    estado: Optional[str] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Obtiene lista de ventas con filtros opcionales."""
    
    query = "SELECT * FROM ventas WHERE 1=1"
    params = {}
    
    # Aplicar filtros si se proporcionan
    if cliente_id:
        query += " AND cliente_id = :cliente_id"
        params["cliente_id"] = cliente_id
        
    if producto_id:
        query += " AND producto_id = :producto_id"
        params["producto_id"] = producto_id
        
    if estado:
        query += " AND estado = :estado"
        params["estado"] = estado
        
    if fecha_inicio:
        query += " AND fecha >= :fecha_inicio"
        params["fecha_inicio"] = fecha_inicio
        
    if fecha_fin:
        query += " AND fecha <= :fecha_fin"
        params["fecha_fin"] = fecha_fin
    
    # Limitar resultados
    query += f" LIMIT {limit}"
    
    success, result = db.execute_query(query, params)
    
    if not success:
        logger.error(f"Error al obtener ventas: {result}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {result}")
    
    ventas = []
    for row in result:
        venta = dict(row._mapping)
        
        # Convertir fechas a string para JSON
        if venta.get("fecha"):
            venta["fecha"] = str(venta["fecha"])
            
        ventas.append(venta)
    
    return ventas

# Ruta para obtener datos de venta con detalles
@router.get("/ventas/{venta_id}")
async def get_venta_detalle(
    venta_id: int,
    db: DBConnector = Depends(get_db)
):
    """Obtiene detalles de una venta especifica incluyendo informacion de cliente y producto."""
    
    query = """
    SELECT v.*, c.nombre as cliente_nombre, c.apellido as cliente_apellido, 
           p.nombre as producto_nombre, p.precio as producto_precio
    FROM ventas v
    LEFT JOIN clientes c ON v.cliente_id = c.id
    LEFT JOIN productos p ON v.producto_id = p.id
    WHERE v.id = :venta_id
    """
    
    success, result = db.execute_query(query, {"venta_id": venta_id})
    
    if not success:
        logger.error(f"Error al obtener venta {venta_id}: {result}")
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {result}")
    
    # Verificar si se encontro la venta
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail=f"Venta con ID {venta_id} no encontrada")
    
    venta = dict(row._mapping)
    
    # Convertir fechas a string para JSON
    if venta.get("fecha"):
        venta["fecha"] = str(venta["fecha"])
        
    return venta
