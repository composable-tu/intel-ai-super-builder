# MCP Server Generator

A code generator tool for creating Model Context Protocol (MCP) servers with standardized structure and functionality.

## Overview

This generator creates a complete MCP server package with all necessary files and boilerplate code, allowing developers to focus on implementing server-specific tools and business logic.

## Key Features

- **FastMCP Server**: Complete server implementation with stdio/HTTP/SSE protocols
- **Centralized Tool Registration**: Simple list-based tool management system
- **Production Ready**: Cross-process control, port conflict detection, graceful shutdown
- **Build Scripts**: PowerShell management and PyInstaller executable generation
- **Testing Framework**: Unit tests with proper MCP testing
- **Cross-Platform**: Works on Windows and Unix/Linux systems

## Usage

### Basic Command
```bash
python McpServerGen.py myserver --description "My Custom MCP Server"
```

### Arguments
- `server_name`: Name of the server (required)
- `--output-dir, -o`: Parent directory for server package (default: current directory)
- `--description, -d`: Server description (default: "MCP Server Template")
- `--port, -p`: Default server port (default: 7905, ignored for stdio protocol)
- `--protocol`: Communication protocol (stdio, http, sse - default: stdio)

### Examples
```bash
# Basic server with default stdio protocol (recommended)
python McpServerGen.py calculator -d "Calculator MCP Server"

# Explicitly specify stdio protocol
python McpServerGen.py filemanager --protocol stdio

# HTTP server with custom port (for web-based integrations)
python McpServerGen.py webserver -d "Web API MCP Server" --port 7906 --protocol http

# SSE protocol (legacy, use stdio or http instead)
python McpServerGen.py calculator -d "Calculator MCP Server" -port 7908 --protocol sse
```

## Generated Package Structure

```
mcp_<server_name>/
├── server.py                 # Main server implementation
├── requirements.txt          # Python dependencies
├── run.ps1                   # Setup and run script
├── manage-server.ps1         # Server management script
├── test_server.py            # Unit tests
├── build.bat / build.ps1     # Build scripts
├── setup.bat / setup.ps1     # Setup scripts
├── <server_name>_server.spec # PyInstaller specification
└── README.md                 # Server documentation
```

## Server Management

Generated servers support these commands:

```bash
# Start server
python server.py start [--port PORT] [--protocol PROTOCOL]

# Stop server
python server.py stop [--json]

# Check status
python server.py status [--json]

# Health check
python server.py ping [--json]

# Version info
python server.py version [--json]
```

## Adding Tools to Generated Servers

Generated servers use a centralized tool registration system. To add new tools:

### 1. Define Your Tool Function
```python
async def my_custom_tool(input_param: str, optional_param: int = 42) -> dict:
    """Custom tool implementation.
    
    Args:
        input_param: Description of the input parameter
        optional_param: Optional parameter with default value
    
    Returns:
        dict: Structured response with processed data
    """
    try:
        result = {
            "processed_input": input_param,
            "multiplied_value": optional_param * 2,
            "timestamp": time.time()
        }
        return result
    except Exception as e:
        raise RuntimeError(f"Error in my_custom_tool: {str(e)}")
```

### 2. Add to TOOL_FUNCTIONS List
```python
TOOL_FUNCTIONS = [
    example_tool,
    my_custom_tool,  # ← Add your new tool here
    # Add additional tool functions here
]
```

Tools are automatically registered when the server starts - no decorators needed!

### 3. Update Dependencies (When Adding New Imports)
**Important**: When you add new imports to `server.py`, you must update the following files:

- **`requirements.txt`**: Add any new Python packages your tools require
  ```bash
  # Example: if you import requests, pandas, etc.
  requests>=2.25.0
  pandas>=1.3.0
  ```

- **`<server_name>_server.spec`**: Update the `hiddenimports` list for PyInstaller
  ```python
  # In the .spec file, add to hiddenimports:
  hiddenimports=['your_new_module', 'another_module'],
  ```

**Example**: If you add `import requests` to your tool function, you need to:
1. Add `requests>=2.25.0` to `requirements.txt`
2. Add `'requests'` to the `hiddenimports` list in the `.spec` file
3. Run `pip install -r requirements.txt` to install the dependency

This ensures your server works correctly in both development and when built as an executable.

## Testing and Building

### Run Tests
```bash
# Run all tests
python test_server.py

# Run specific test
python -m unittest test_server.TestMyServerServer.test_server_version
```

### Build Executable
```bash
# Windows
.\build.bat
# or
.\build.ps1
```

This creates a standalone executable in the `dist/` directory.

## Troubleshooting

### Common Issues

**Port already in use** (for http/sse protocols):
- Check for existing server: `python server.py status`
- Kill conflicting process: `netstat -ano | findstr <port>`

**Tool registration issues**:
- Ensure tools are added to `TOOL_FUNCTIONS` list
- Check for syntax errors in tool function definitions
- Use `python server.py version` to see registered tools

**Permission errors**:
- Run terminal as Administrator (Windows)
- Ensure PowerShell execution policy allows running scripts

## Requirements

- Python 3.8 or higher
- PowerShell 5.0 or higher (Windows)

## License

This project is licensed under the MIT License.