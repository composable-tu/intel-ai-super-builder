import os
import sys
import argparse
import re
from pathlib import Path
from datetime import datetime

def read_template(template_name: str) -> str:
    """Read a template file."""
    template_path = Path(__file__).parent / "templates" / template_name
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def find_template_variables(content: str) -> set:
    """Find all template variables in content using regex."""
    # Only match simple variable names (alphanumeric and underscore)
    pattern = r'(?<!\{)\{([a-zA-Z_][a-zA-Z0-9_]*)\}(?!\})'
    matches = re.findall(pattern, content)
    return set(matches)

def safe_format_template(template_content: str, template_vars: dict) -> str:
    """Safely format template by only replacing known variables."""
    result = template_content
    
    # Only replace variables that are simple identifiers and exist in our vars
    for var_name, var_value in template_vars.items():
        # Use raw string and escape special regex characters in var_name
        pattern = r'\{' + re.escape(var_name) + r'\}'
        # Escape backslashes in the replacement value to prevent regex issues
        safe_value = str(var_value).replace('\\', '\\\\')
        result = re.sub(pattern, safe_value, result)
    
    # Convert double braces to single braces for runtime f-string formatting
    # This converts {{variable}} to {variable} for runtime use
    result = re.sub(r'\{\{([^}]+)\}\}', r'{\1}', result)
    
    return result

def generate_server_package(
    parent_dir: str,
    server_name: str, 
    description: str, 
    default_port: int = 7905,
    protocol: str = "stdio"
):
    """Generate a complete MCP server package."""
    if not server_name.isidentifier():
        raise ValueError("Server name must be a valid Python identifier")
        
    server_name_upper = server_name.upper()
    package_dir = Path(parent_dir) / f"mcp_{server_name}"
    package_dir.mkdir(parents=True, exist_ok=True)
    
    # Base template variables
    template_vars = {
        "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "server_name": server_name,
        "server_name_upper": server_name_upper,
        "ServerName": server_name.capitalize(),
        "description": description,
        "default_port": default_port,
        "protocol": protocol,
        # Protocol-specific variables for README
        "port_required": "No" if protocol == "stdio" else "Yes",
        "port_display": "N/A (stdio protocol)" if protocol == "stdio" else str(default_port),
        "protocol_description": {
            "stdio": "Standard input/output communication, no port required",
            "sse": "Server-Sent Events over HTTP, requires a port",
            "http": "HTTP transport, requires a port"
        }.get(protocol, "Unknown protocol"),
        # Example commands based on protocol
        "start_example": "python server.py start" if protocol == "stdio" else f"python server.py start --port {default_port}",
        "start_example_exe": f".\\dist\\{server_name}-mcp-server.exe start" if protocol == "stdio" else f".\\dist\\{server_name}-mcp-server.exe start --port {default_port}"
    }
    
    # Template file mappings - only include files that exist
    all_template_mappings = {
        "server.py": "server.py.template",
        "requirements.txt": "requirements.txt.template",
        "run.ps1": "run.ps1.template",
        "test_server.py": "test_server.py.template",
        "manage-server.ps1": "manage-server.ps1.template",
        "README.md": "readme.md.template",
        "build.bat": "build.bat.template",
        "build.ps1": "build.ps1.template",
        f"{server_name}_server.spec": "server.spec.template",
        "setup.bat": "setup.bat.template",
        "setup.ps1": "setup.ps1.template"
    }
    
    # Filter to only existing templates
    template_mappings = {}
    templates_dir = Path(__file__).parent / "templates"
    
    for output_file, template_file in all_template_mappings.items():
        template_path = templates_dir / template_file
        if template_path.exists():
            template_mappings[output_file] = template_file
            print(f"Found template: {template_file}")
        else:
            print(f"Missing template: {template_file} - skipping {output_file}")
    
    if not template_mappings:
        raise ValueError("No template files found!")
    
    for output_file, template_file in template_mappings.items():
        try:
            print(f"Processing template: {template_file}")
            
            # Read template
            template_content = read_template(template_file)
            
            # Find simple template variables only
            found_vars = find_template_variables(template_content)
            missing_vars = found_vars - set(template_vars.keys())
            
            if missing_vars:
                print(f"Warning: Missing template variables in {template_file}: {missing_vars}")
                # Add default values for missing variables based on common patterns
                for var in missing_vars:
                    if var not in template_vars:
                        if var.lower() in ['version', 'server_version']:
                            template_vars[var] = "1.0.0"
                        elif var.lower() in ['author', 'maintainer']:
                            template_vars[var] = "Generated"
                        elif var.lower() in ['email', 'contact']:
                            template_vars[var] = "user@example.com"
                        elif var.lower() in ['license']:
                            template_vars[var] = "MIT"
                        elif var.lower() in ['url', 'homepage']:
                            template_vars[var] = "https://github.com/user/repo"
                        elif 'date' in var.lower():
                            template_vars[var] = datetime.now().strftime("%Y-%m-%d")
                        elif 'port' in var.lower():
                            template_vars[var] = str(default_port)
                        elif 'name' in var.lower():
                            template_vars[var] = server_name
                        else:
                            # Don't add TODO prefix - just use reasonable default
                            template_vars[var] = server_name
                        print(f"  Added default value for {var}: {template_vars[var]}")
                
                # Remove any remaining missing vars that still don't have defaults
                remaining_missing = found_vars - set(template_vars.keys())
                if remaining_missing:
                    print(f"  Still missing after defaults: {remaining_missing}")
                    # Add fallback defaults for any remaining vars
                    for var in remaining_missing:
                        template_vars[var] = server_name
                        print(f"  Added fallback for {var}: {template_vars[var]}")
            
            # Apply template using safe formatting
            output_content = safe_format_template(template_content, template_vars)
            
            # Write output file
            output_path = package_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(output_content)
            print(f"Generated: {output_file}")
                
        except Exception as e:
            print(f"Error processing template {template_file}: {str(e)}", file=sys.stderr)
            continue  # Continue with next template instead of failing completely
    
    print(f"\nGenerated MCP server package in: {package_dir}")
    print("\nGenerated files:")
    for file in template_mappings.keys():
        print(f"- {file}")
    print("\nNext steps:")
    print("1. Review the generated code")
    print("2. Add your server-specific tools")
    print(f"3. Install dependencies: cd {package_dir.name} && .\\run.ps1")

def main():
    parser = argparse.ArgumentParser(description="Generate MCP server package")
    parser.add_argument("server_name", help="Name of the server (used in code and env vars)")
    parser.add_argument("--output-dir", "-o", 
                       default=".", 
                       help="Parent directory for the server package")
    parser.add_argument("--description", "-d", 
                       default="MCP Server Template", 
                       help="Server description")
    parser.add_argument("--port", "-p", 
                       type=int, 
                       default=7905, 
                       help="Default server port")
    parser.add_argument("--protocol", 
                       default="stdio", 
                       choices=["sse", "stdio", "http"],
                       help="Communication protocol (default: stdio)")
    
    args = parser.parse_args()
    try:
        generate_server_package(args.output_dir, args.server_name, args.description, args.port, args.protocol)
        print("\nServer package generated successfully!")
    except Exception as e:
        print(f"Error generating server package: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()