"""
sql_generator.py - Generación de SQL a partir de lenguaje natural

PROPÓSITO:
    Coordina la generación de consultas SQL a partir de descripciones en
    lenguaje natural, utilizando proveedores de IA y el contexto del esquema
    de la base de datos.

ENTRADA:
    - Consulta en lenguaje natural
    - Esquema de base de datos
    - Configuración del proveedor de IA
    - Opciones de generación (formato, validación, etc.)

SALIDA:
    - Consulta SQL generada
    - Explicación de la consulta
    - Metadata sobre la generación
    - Estado de validación

ERRORES:
    - GenerationError: Error al generar la consulta SQL
    - ValidationError: La consulta generada no es válida
    - ProviderError: Error con el proveedor de IA
    - SchemaError: Esquema de base de datos incompleto o inválido

DEPENDENCIAS:
    - providers: Módulos de proveedores de IA
    - utils.progress: Para indicadores visuales
    - utils.error_handler: Para manejo de errores
    - utils.validators: Para validación de consultas SQL
"""

import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Union

from utils.progress import ProgressBar
from utils.error_handler import GenerationError, ValidationError, ProviderError, SchemaError

# Configurar logger
logger = logging.getLogger(__name__)

class SQLGenerator:
    """Clase para generar consultas SQL a partir de lenguaje natural."""
    
    def __init__(self, provider=None, schema=None):
        """
        Inicializa el generador SQL.
        
        Args:
            provider: Instancia del proveedor de IA (opcional)
            schema: Esquema de la base de datos (opcional)
        """
        self.provider = provider
        self.schema = schema
        self.last_query = ""
        self.last_sql = ""
        self.last_explanation = ""
        self.last_generation_time = 0
        self.default_prompt_template = self._get_default_prompt_template()
        self.prompt_template = self.default_prompt_template
    
    def set_provider(self, provider) -> bool:
        """
        Establece el proveedor de IA.
        
        Args:
            provider: Instancia del proveedor de IA
            
        Returns:
            bool: True si se estableció correctamente
        """
        if hasattr(provider, 'generate') and callable(provider.generate):
            self.provider = provider
            return True
        else:
            logger.error("Proveedor de IA inválido: debe tener un método 'generate'")
            return False
    
    def set_schema(self, schema) -> bool:
        """
        Establece el esquema de la base de datos.
        
        Args:
            schema: Diccionario con el esquema
            
        Returns:
            bool: True si se estableció correctamente
        """
        required_keys = ["tables", "relationships"]
        
        # Verificar estructura básica
        if not isinstance(schema, dict) or not all(key in schema for key in required_keys):
            logger.error("Esquema inválido: estructura incompleta")
            return False
        
        # Verificar existencia de tablas
        if not schema["tables"]:
            logger.error("Esquema inválido: no contiene tablas")
            return False
        
        self.schema = schema
        return True
    
    def set_prompt_template(self, template: str) -> None:
        """
        Establece una plantilla personalizada para el prompt.
        
        Args:
            template: Plantilla de prompt que incluya al menos {query} y {schema}
        """
        required_placeholders = ["{query}", "{schema}"]
        for placeholder in required_placeholders:
            if placeholder not in template:
                logger.warning(f"Plantilla de prompt sin placeholder requerido: {placeholder}")
                return
        
        self.prompt_template = template
    
    def reset_prompt_template(self) -> None:
        """Restaura la plantilla de prompt por defecto."""
        self.prompt_template = self.default_prompt_template
    
    def generate(self, query: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Genera una consulta SQL a partir de lenguaje natural.
        
        Args:
            query: Consulta en lenguaje natural
            options: Opciones de generación (opcional)
            
        Returns:
            Dict: Resultado de la generación
            
        Raises:
            GenerationError: Error al generar la consulta
            ProviderError: Error con el proveedor de IA
            SchemaError: Esquema de base de datos inválido
        """
        # Verificar proveedor y esquema
        if not self.provider:
            raise ProviderError("No se ha establecido un proveedor de IA")
        if not self.schema:
            raise SchemaError("No se ha establecido un esquema de base de datos")
        
        # Aplicar opciones
        options = options or {}
        validate_sql = options.get("validate_sql", True)
        include_explanation = options.get("include_explanation", True)
        format_sql = options.get("format_sql", True)
        timeout = options.get("timeout", 30)
        
        # Guardar la consulta
        self.last_query = query
        
        # Crear barra de progreso
        progress = ProgressBar("Generando SQL")
        progress.start()
        
        try:
            # Preparar el prompt para el modelo de IA
            start_time = time.time()
            prompt = self._prepare_prompt(query)
            progress.update(20)
            
            # Enviar prompt al proveedor de IA
            ai_response = self.provider.generate(prompt, timeout=timeout)
            if not ai_response or not isinstance(ai_response, dict):
                raise GenerationError("Respuesta inválida del proveedor de IA")
            
            progress.update(60)
            
            # Extraer SQL y explicación de la respuesta
            generated_sql = self._extract_sql(ai_response.get("text", ""))
            if not generated_sql:
                raise GenerationError("No se pudo extraer una consulta SQL válida de la respuesta")
            
            explanation = self._extract_explanation(ai_response.get("text", "")) if include_explanation else ""
            
            # Formatear SQL si se solicita
            if format_sql:
                generated_sql = self._format_sql(generated_sql)
            
            progress.update(80)
            
            # Validar SQL si se solicita
            validation_result = {"valid": True, "errors": []}
            if validate_sql:
                validation_result = self._validate_sql(generated_sql)
            
            # Guardar resultados
            self.last_sql = generated_sql
            self.last_explanation = explanation
            self.last_generation_time = time.time() - start_time
            
            # Preparar resultado
            result = {
                "sql": generated_sql,
                "explanation": explanation,
                "generation_time": self.last_generation_time,
                "validation": validation_result,
                "query": query
            }
            
            progress.finish(success=True)
            logger.info(f"SQL generado correctamente en {self.last_generation_time:.2f}s")
            
            return result
            
        except Exception as e:
            progress.finish(success=False)
            logger.error(f"Error al generar SQL: {str(e)}")
            
            error_type = type(e).__name__
            if error_type == "ProviderError":
                raise ProviderError(f"Error con el proveedor de IA: {str(e)}")
            else:
                raise GenerationError(f"Error al generar SQL: {str(e)}")
    
    def _prepare_prompt(self, query: str) -> str:
        """
        Prepara el prompt para el modelo de IA.
        
        Args:
            query: Consulta en lenguaje natural
            
        Returns:
            str: Prompt completo
        """
        # Obtener representación del esquema
        schema_summary = self._get_schema_summary()
        
        # Aplicar plantilla
        prompt = self.prompt_template.format(
            query=query,
            schema=schema_summary,
            examples=self._get_examples()
        )
        
        return prompt
    
    def _get_schema_summary(self) -> str:
        """
        Obtiene un resumen del esquema para el prompt.
        
        Returns:
            str: Resumen del esquema
        """
        summary = []
        
        # Información de la base de datos
        if "database_info" in self.schema:
            db_info = self.schema["database_info"]
            summary.append(f"Base de datos: {db_info.get('name', 'N/A')} ({db_info.get('type', 'N/A')})")
        
        # Detalles de tablas
        summary.append("\nESTRUCTURA DE TABLAS:")
        for table_name, table_info in self.schema["tables"].items():
            summary.append(f"\nTABLA {table_name}")
            
            # Columnas y tipos
            for col_name, col_info in table_info["columns"].items():
                pk_mark = "*" if col_info["primary_key"] else ""
                null_mark = "NULL" if col_info["nullable"] else "NOT NULL"
                summary.append(f"  {pk_mark}{col_name} {col_info['type']} {null_mark}")
            
            # Claves foráneas
            if table_info["foreign_keys"]:
                summary.append("  FOREIGN KEYS:")
                for fk in table_info["foreign_keys"]:
                    summary.append(f"    {fk['column']} -> {fk['references_table']}.{fk['references_column']}")
        
        # Relaciones
        if self.schema["relationships"]:
            summary.append("\nRELACIONES:")
            for rel in self.schema["relationships"]:
                summary.append(f"  {rel['table_from']}.{rel['column_from']} -> "
                              f"{rel['table_to']}.{rel['column_to']} ({rel['relationship_type']})")
        
        return "\n".join(summary)
    
    def _extract_sql(self, response: str) -> str:
        """
        Extrae la consulta SQL de la respuesta del modelo.
        
        Args:
            response: Respuesta del modelo de IA
            
        Returns:
            str: Consulta SQL extraída
        """
        # Buscar SQL entre marcadores de código
        sql_markers = [
            (r"```sql\s*(.*?)\s*```", 1),  # Markdown con tipo SQL
            (r"```\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|BEGIN|WITH).*?```", 0),  # Markdown sin tipo pero con comandos SQL
            (r"SQL:\s*```\s*(.*?)\s*```", 1),  # Etiqueta SQL seguida de bloque de código
            (r"SQL Query:\s*```\s*(.*?)\s*```", 1),  # Etiqueta SQL Query seguida de bloque
            (r"SQL:\s*(SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|BEGIN|WITH).*?;", 0)  # SQL: seguido de comando
        ]
        
        # Intentar cada patrón
        for pattern, group in sql_markers:
            matches = re.search(pattern, response, re.DOTALL)
            if matches:
                sql = matches.group(group) if group > 0 else matches.group().replace("SQL:", "").strip()
                return sql.strip()
        
        # Si no se encuentra con los patrones, buscar comandos SQL directamente
        sql_commands = ["SELECT", "INSERT INTO", "UPDATE", "DELETE FROM", "CREATE TABLE", 
                       "ALTER TABLE", "DROP TABLE", "BEGIN TRANSACTION"]
        
        for command in sql_commands:
            if command in response:
                # Extraer desde el comando hasta el siguiente punto o final
                pattern = f"({command}.*?)(\\.|$)"
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    return match.group(1).strip()
        
        # Si no se encuentra nada, devolver vacío
        return ""
    
    def _extract_explanation(self, response: str) -> str:
        """
        Extrae la explicación de la consulta SQL.
        
        Args:
            response: Respuesta del modelo de IA
            
        Returns:
            str: Explicación extraída
        """
        # Buscar secciones de explicación
        explanation_markers = [
            (r"Explicación:(.*?)(?:```|$)", 1),
            (r"Explanation:(.*?)(?:```|$)", 1),
            (r"Esta consulta:(.*?)(?:```|$)", 1),
            (r"This query:(.*?)(?:```|$)", 1)
        ]
        
        # Intentar cada patrón
        for pattern, group in explanation_markers:
            matches = re.search(pattern, response, re.DOTALL)
            if matches:
                return matches.group(group).strip()
        
        # Si no hay explicación explícita, usar todo el texto excepto el SQL
        sql = self._extract_sql(response)
        if sql:
            # Eliminar el SQL y los bloques de código del texto
            explanation = re.sub(r"```.*?```", "", response, flags=re.DOTALL)
            explanation = re.sub(re.escape(sql), "", explanation)
            return explanation.strip()
        
        # Si no se encuentra nada específico, devolver la respuesta completa
        return response.strip()
    
    def _format_sql(self, sql: str) -> str:
        """
        Formatea la consulta SQL para mejor legibilidad.
        
        Args:
            sql: Consulta SQL a formatear
            
        Returns:
            str: Consulta SQL formateada
        """
        # Eliminar punto y coma final si existe
        sql = sql.strip()
        
        # Implementación básica de formato
        # 1. Palabras clave en mayúsculas
        keywords = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING", 
                    "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN",
                    "LIMIT", "OFFSET", "INSERT INTO", "VALUES", "UPDATE", "SET", 
                    "DELETE FROM", "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
                    "AND", "OR", "NOT", "IN", "LIKE", "BETWEEN", "IS NULL", "IS NOT NULL"]
        
        formatted = sql
        for keyword in keywords:
            # Usar expresión regular para coincidencias de palabras completas
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            formatted = re.sub(pattern, keyword, formatted, flags=re.IGNORECASE)
        
        # 2. Añadir saltos de línea después de ciertas palabras clave
        newline_after = ["SELECT", "FROM", "WHERE", "GROUP BY", "ORDER BY", "HAVING",
                         "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN",
                         "LIMIT", "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM"]
        
        for keyword in newline_after:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            formatted = re.sub(pattern, f"\n{keyword}", formatted)
        
        # 3. Añadir indentación después de saltos de línea (excepto el primero)
        lines = formatted.split('\n')
        for i in range(1, len(lines)):
            lines[i] = "    " + lines[i].strip()
        
        return "\n".join(lines).strip()
    
    def _validate_sql(self, sql: str) -> Dict[str, Any]:
        """
        Valida una consulta SQL.
        
        Args:
            sql: Consulta SQL a validar
            
        Returns:
            Dict: Resultado de la validación
        """
        # Implementación básica de validación
        validation = {"valid": True, "errors": []}
        
        # 1. Verificar sintaxis básica
        # Verificar paréntesis balanceados
        if sql.count('(') != sql.count(')'):
            validation["valid"] = False
            validation["errors"].append("Paréntesis no balanceados")
        
        # 2. Verificar palabras clave requeridas
        if sql.strip().upper().startswith("SELECT"):
            required_keyword = "FROM"
            if required_keyword not in sql.upper():
                validation["valid"] = False
                validation["errors"].append(f"Falta palabra clave requerida: {required_keyword}")
        
        # 3. Verificar comillas
        if sql.count("'") % 2 != 0:
            validation["valid"] = False
            validation["errors"].append("Comillas simples no balanceadas")
        
        if sql.count('"') % 2 != 0:
            validation["valid"] = False
            validation["errors"].append("Comillas dobles no balanceadas")
        
        # 4. Verificar tablas y columnas contra el esquema
        if self.schema:
            # Obtener todas las tablas y columnas del esquema
            schema_tables = set(self.schema["tables"].keys())
            schema_columns = set()
            table_columns = {}
            
            for table, info in self.schema["tables"].items():
                table_columns[table] = set(info["columns"].keys())
                schema_columns.update(table_columns[table])
            
            # Buscar tablas en la consulta SQL
            table_pattern = r'\bFROM\s+([a-zA-Z0-9_]+)|\bJOIN\s+([a-zA-Z0-9_]+)'
            table_matches = re.finditer(table_pattern, sql, re.IGNORECASE)
            
            for match in table_matches:
                table_name = match.group(1) if match.group(1) else match.group(2)
                if table_name and table_name not in schema_tables:
                    validation["valid"] = False
                    validation["errors"].append(f"Tabla no encontrada en el esquema: {table_name}")
            
            # Análisis más avanzado de columnas requeriría un parser SQL completo
            # Esta es una implementación básica
        
        return validation
    
    def _get_default_prompt_template(self) -> str:
        """
        Obtiene la plantilla de prompt por defecto.
        
        Returns:
            str: Plantilla de prompt por defecto
        """
        return """
# Tarea: Generar una consulta SQL a partir de una descripción en lenguaje natural

## Esquema de la base de datos
{schema}

## Consulta en lenguaje natural
{query}

## Instrucciones
- Genera una consulta SQL que responda correctamente a la consulta en lenguaje natural.
- La consulta debe ser compatible con el esquema de base de datos proporcionado.
- Utiliza únicamente tablas y columnas que existan en el esquema.
- No inventes nombres de tablas o columnas.
- No utilices funciones o sintaxis específica de un motor de base de datos, a menos que se indique lo contrario.
- Si no es posible generar una consulta SQL con la información disponible, explica por qué.
- Proporciona una breve explicación de lo que hace la consulta y cómo responde a la pregunta.

## Formato de respuesta
Primero proporciona la consulta SQL entre comillas triples con la etiqueta sql:

```sql
-- Tu consulta SQL aquí
```

Luego proporciona una explicación de cómo la consulta resuelve la pregunta:

Explicación: 
[Breve explicación de la consulta y cómo responde a la pregunta]

{examples}
"""
    
    def _get_examples(self) -> str:
        """
        Obtiene ejemplos para incluir en el prompt.
        
        Returns:
            str: Ejemplos formateados
        """
        # Por defecto, no incluimos ejemplos en el prompt básico
        return ""


# Función utilitaria para generar SQL
def generate_sql(query: str, provider, schema: Dict[str, Any], 
                options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Función auxiliar para generar SQL a partir de lenguaje natural.
    
    Args:
        query: Consulta en lenguaje natural
        provider: Instancia del proveedor de IA
        schema: Esquema de la base de datos
        options: Opciones de generación
        
    Returns:
        Dict: Resultado de la generación
    """
    generator = SQLGenerator(provider, schema)
    return generator.generate(query, options)


# Punto de entrada para pruebas
if __name__ == "__main__":
    import sys
    import json
    from db_connector import DBConnector
    from schema_analyzer import SchemaAnalyzer
    
    # Simulación de proveedor para pruebas
    class MockProvider:
        def generate(self, prompt, timeout=30):
            print(f"Simulando generación con prompt de {len(prompt)} caracteres...")
            return {
                "text": """
Para esta consulta, necesitamos una consulta SQL que muestre usuarios activos:

```sql
SELECT user_id, username, email, last_login
FROM users
WHERE status = 'active'
ORDER BY last_login DESC
LIMIT 10
```

Explicación: Esta consulta selecciona los usuarios con estado 'activo', mostrando su ID, nombre de usuario, correo y fecha de último login, ordenados por la fecha de último login en orden descendente y limitado a los 10 más recientes.
"""
            }
    
    # Si se proporciona un argumento, úsalo como URI de conexión
    if len(sys.argv) > 1:
        conn_string = sys.argv[1]
        try:
            # Conectar a la base de datos
            print(f"Conectando a {conn_string}")
            connector = DBConnector()
            status, _ = connector.connect(conn_string)
            
            if status:
                # Analizar esquema
                print("Analizando esquema...")
                analyzer = SchemaAnalyzer(connector.connection)
                schema = analyzer.analyze()
                
                # Probar generación
                print("Probando generación de SQL...")
                generator = SQLGenerator(MockProvider(), schema)
                result = generator.generate("Muestra los 10 usuarios activos más recientes")
                
                print("\nConsulta generada:")
                print(result["sql"])
                print("\nExplicación:")
                print(result["explanation"])
            
            # Desconectar
            connector.disconnect()
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Uso: python sql_generator.py <connection_string>")
        print("Ejemplo: python sql_generator.py mysql://user:pass@localhost/dbname")
