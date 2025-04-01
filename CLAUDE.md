# NL2SQL Project Guidelines

## Commands
- Setup: `python scripts/setup.py`
- Run: `python scripts/run.py`
- Test: `python scripts/test_core.py`
- Single test: `pytest path/to/test_file.py::test_function_name -v`

## Code Style
- **Imports**: stdlib → third-party → internal; use absolute imports
- **Typing**: Always use type hints for parameters and return values
- **Docstrings**: Triple quotes with Args/Returns/Raises sections
- **Naming**: snake_case for functions/variables, CamelCase for classes
- **File Headers**: Include PROPÓSITO, ENTRADA, SALIDA, ERRORES, DEPENDENCIAS
- **Error Handling**: Use specific exceptions with informative messages
- **Paths**: Normalize with `sys.path.insert(0, str(Path(__file__).parent.parent))`

## Architecture
- Core logic (/core/): schema analysis, SQL generation
- API (/api/): FastAPI routes
- CLI (/cli/): command interface
- Providers (/providers/): AI model interfaces
- Utils (/utils/): shared helper functions