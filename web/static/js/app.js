// Configuración de la aplicación
const config = {
    apiBase: 'http://localhost:8001/api',
};

// Referencias a elementos DOM
const elements = {
    // Botones de tablas
    btnClientes: document.getElementById('btn-clientes'),
    btnProductos: document.getElementById('btn-productos'),
    btnVentas: document.getElementById('btn-ventas'),
    
    // Contenedores de filtros
    filterClientes: document.getElementById('filter-clientes'),
    filterProductos: document.getElementById('filter-productos'),
    filterVentas: document.getElementById('filter-ventas'),
    
    // Filtros de Clientes
    clienteNombre: document.getElementById('cliente-nombre'),
    clienteApellido: document.getElementById('cliente-apellido'),
    clienteTipo: document.getElementById('cliente-tipo'),
    clienteCiudad: document.getElementById('cliente-ciudad'),
    filterClientesBtn: document.getElementById('filter-clientes-btn'),
    resetClientesBtn: document.getElementById('reset-clientes-btn'),
    
    // Filtros de Productos
    productoNombre: document.getElementById('producto-nombre'),
    productoCategoria: document.getElementById('producto-categoria'),
    productoMarca: document.getElementById('producto-marca'),
    productoPrecioMin: document.getElementById('producto-precio-min'),
    productoPrecioMax: document.getElementById('producto-precio-max'),
    filterProductosBtn: document.getElementById('filter-productos-btn'),
    resetProductosBtn: document.getElementById('reset-productos-btn'),
    
    // Filtros de Ventas
    ventaCliente: document.getElementById('venta-cliente'),
    ventaProducto: document.getElementById('venta-producto'),
    ventaEstado: document.getElementById('venta-estado'),
    ventaFechaInicio: document.getElementById('venta-fecha-inicio'),
    ventaFechaFin: document.getElementById('venta-fecha-fin'),
    filterVentasBtn: document.getElementById('filter-ventas-btn'),
    resetVentasBtn: document.getElementById('reset-ventas-btn'),
    
    // Elementos de visualización
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    tableHead: document.getElementById('table-head'),
    tableBody: document.getElementById('table-body')
};

// Estado de la aplicación
const state = {
    currentTable: null,
};

// Manejadores de eventos
function setupEventListeners() {
    // Botones de selección de tabla
    elements.btnClientes.addEventListener('click', () => {
        state.currentTable = 'clientes';
        showFilters('clientes');
        fetchClientes();
    });
    
    elements.btnProductos.addEventListener('click', () => {
        state.currentTable = 'productos';
        showFilters('productos');
        fetchProductos();
    });
    
    elements.btnVentas.addEventListener('click', () => {
        state.currentTable = 'ventas';
        showFilters('ventas');
        fetchVentas();
    });
    
    // Botones de filtrado
    elements.filterClientesBtn.addEventListener('click', fetchClientes);
    elements.filterProductosBtn.addEventListener('click', fetchProductos);
    elements.filterVentasBtn.addEventListener('click', fetchVentas);
    
    // Botones de reinicio
    elements.resetClientesBtn.addEventListener('click', () => {
        elements.clienteNombre.value = '';
        elements.clienteApellido.value = '';
        elements.clienteTipo.value = '';
        elements.clienteCiudad.value = '';
        fetchClientes();
    });
    
    elements.resetProductosBtn.addEventListener('click', () => {
        elements.productoNombre.value = '';
        elements.productoCategoria.value = '';
        elements.productoMarca.value = '';
        elements.productoPrecioMin.value = '';
        elements.productoPrecioMax.value = '';
        fetchProductos();
    });
    
    elements.resetVentasBtn.addEventListener('click', () => {
        elements.ventaCliente.value = '';
        elements.ventaProducto.value = '';
        elements.ventaEstado.value = '';
        elements.ventaFechaInicio.value = '';
        elements.ventaFechaFin.value = '';
        fetchVentas();
    });
}

// Funciones de utilidad para la interfaz
function showFilters(tableType) {
    // Ocultar todos los filtros
    elements.filterClientes.style.display = 'none';
    elements.filterProductos.style.display = 'none';
    elements.filterVentas.style.display = 'none';
    
    // Mostrar el filtro correspondiente
    if (tableType === 'clientes') {
        elements.filterClientes.style.display = 'block';
    } else if (tableType === 'productos') {
        elements.filterProductos.style.display = 'block';
    } else if (tableType === 'ventas') {
        elements.filterVentas.style.display = 'block';
    }
}

function showLoading() {
    elements.loading.style.display = 'block';
    elements.error.style.display = 'none';
}

function hideLoading() {
    elements.loading.style.display = 'none';
}

function showError(message) {
    hideLoading();
    elements.error.style.display = 'block';
    elements.error.textContent = message;
}

// Funciones para obtener datos de la API
async function fetchClientes() {
    showLoading();
    
    const params = new URLSearchParams();
    if (elements.clienteNombre.value) params.append('nombre', elements.clienteNombre.value);
    if (elements.clienteApellido.value) params.append('apellido', elements.clienteApellido.value);
    if (elements.clienteTipo.value) params.append('tipo_cliente', elements.clienteTipo.value);
    if (elements.clienteCiudad.value) params.append('ciudad', elements.clienteCiudad.value);
    
    try {
        const response = await fetch(`${config.apiBase}/clientes?${params.toString()}`);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        
        const data = await response.json();
        displayData(data, 'clientes');
        hideLoading();
    } catch (err) {
        showError(`Error al cargar clientes: ${err.message}`);
    }
}

async function fetchProductos() {
    showLoading();
    
    const params = new URLSearchParams();
    if (elements.productoNombre.value) params.append('nombre', elements.productoNombre.value);
    if (elements.productoCategoria.value) params.append('categoria', elements.productoCategoria.value);
    if (elements.productoMarca.value) params.append('marca', elements.productoMarca.value);
    if (elements.productoPrecioMin.value) params.append('precio_min', elements.productoPrecioMin.value);
    if (elements.productoPrecioMax.value) params.append('precio_max', elements.productoPrecioMax.value);
    
    try {
        const response = await fetch(`${config.apiBase}/productos?${params.toString()}`);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        
        const data = await response.json();
        displayData(data, 'productos');
        hideLoading();
    } catch (err) {
        showError(`Error al cargar productos: ${err.message}`);
    }
}

async function fetchVentas() {
    showLoading();
    
    const params = new URLSearchParams();
    if (elements.ventaCliente.value) params.append('cliente_id', elements.ventaCliente.value);
    if (elements.ventaProducto.value) params.append('producto_id', elements.ventaProducto.value);
    if (elements.ventaEstado.value) params.append('estado', elements.ventaEstado.value);
    if (elements.ventaFechaInicio.value) params.append('fecha_inicio', elements.ventaFechaInicio.value);
    if (elements.ventaFechaFin.value) params.append('fecha_fin', elements.ventaFechaFin.value);
    
    try {
        const response = await fetch(`${config.apiBase}/ventas?${params.toString()}`);
        if (!response.ok) throw new Error(`Error ${response.status}: ${response.statusText}`);
        
        const data = await response.json();
        displayData(data, 'ventas');
        hideLoading();
    } catch (err) {
        showError(`Error al cargar ventas: ${err.message}`);
    }
}

// Función para mostrar datos en la tabla
function displayData(data, type) {
    if (!data || data.length === 0) {
        elements.tableHead.innerHTML = '<tr><th>No se encontraron datos</th></tr>';
        elements.tableBody.innerHTML = '';
        return;
    }
    
    // Obtener columnas del primer elemento
    const columns = Object.keys(data[0]);
    
    // Generar encabezado de tabla
    elements.tableHead.innerHTML = `
        <tr>
            ${columns.map(column => `<th>${formatColumnName(column)}</th>`).join('')}
        </tr>
    `;
    
    // Generar filas de datos
    elements.tableBody.innerHTML = data.map(item => `
        <tr>
            ${columns.map(column => `<td>${formatCellValue(item[column], column)}</td>`).join('')}
        </tr>
    `).join('');
}

// Funciones auxiliares para formateo de datos
function formatColumnName(column) {
    // Convertir snake_case a formato legible
    return column
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

function formatCellValue(value, column) {
    if (value === null || value === undefined) return '-';
    
    // Formateo específico según el tipo de columna
    if (column.includes('precio') || column.includes('total')) {
        return `$${parseFloat(value).toFixed(2)}`;
    }
    
    if (column.includes('fecha')) {
        // Verificar si es una fecha y formatearla
        const date = new Date(value);
        if (!isNaN(date.getTime())) {
            return date.toLocaleDateString('es-ES');
        }
    }
    
    return value;
}

// Inicialización de la aplicación
async function initApp() {
    setupEventListeners();
    
    try {
        // Verificar estado de la API
        const response = await fetch(`${config.apiBase}/../status`);
        const data = await response.json();
        console.log('API Status:', data);
        
        // Si la API está online, mostrar un mensaje de bienvenida
        if (data.status === 'online') {
            console.log('Conexión exitosa con la API');
        }
    } catch (err) {
        showError(`Error al conectar con la API: ${err.message}`);
    }
}

// Iniciar la aplicación cuando se carga la página
document.addEventListener('DOMContentLoaded', initApp);