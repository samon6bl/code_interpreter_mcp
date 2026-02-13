# Code Interpreter MCP Server

A Model Context Protocol (MCP) server that provides secure code execution capabilities for multiple programming languages including Python, Bash/Shell, C, and C++.

## Features

- **Multiple Languages**: Execute Python, Bash, C, and C++ code
- **Streamable HTTP**: Uses MCP's recommended transport protocol for production environments
- **Fixed Working Directory**: All code executes in a configurable working directory
- **File Operations**: Built-in tools for file management
- **Timeout Protection**: Configurable execution timeouts prevent infinite loops

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd code-interpreter-mcp

# Install dependencies
pip install -e .
```

### Using pip (when published)

```bash
pip install code-interpreter-mcp
```

## Configuration

Set environment variables to configure the server:

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKING_DIR` | Directory for code execution | `/tmp/code-exec` |
| `MCP_HOST` | Server host | `0.0.0.0` |
| `MCP_PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Example

```bash
export WORKING_DIR=/tmp/my-workspace
export MCP_PORT=9000
```

## Usage

### Starting the Server

```bash
# Basic usage
python -m code_interpreter_mcp

# With custom working directory
WORKING_DIR=/path/to/workspace python -m code_interpreter_mcp

# With custom port
MCP_PORT=9000 python -m code_interpreter_mcp
```

The server will start on `http://0.0.0.0:8000/mcp` (or your configured port).

### Connecting from Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "code-interpreter": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

For remote servers:

```json
{
  "mcpServers": {
    "remote-code-interpreter": {
      "transport": "http",
      "url": "http://your-server-ip:8000/mcp"
    }
  }
}
```

## Available Tools

### `execute_code`

Execute code in a specified programming language.

**Parameters:**
- `code` (string): The code to execute
- `language` (string): Programming language (`python`, `bash`, `c`, `cpp`)
- `timeout` (integer): Timeout in seconds (default: 300)

**Example:**
```python
# Python code
execute_code('print("Hello, World!")', language="python")

# Bash command
execute_code('ls -la', language="bash")

# C code
execute_code('''
#include <stdio.h>
int main() {
    printf("Hello from C!\\n");
    return 0;
}
''', language="c")
```

### `list_languages`

List all supported programming languages and their availability.

**Example:**
```python
list_languages()
# Returns: {"python": {"executor": "/usr/bin/python3", "available": true}, ...}
```

### `get_working_dir`

Get information about the current working directory and disk usage.

**Example:**
```python
get_working_dir()
# Returns: {"working_directory": "/tmp/code-exec", "disk_usage": {...}}
```

### `write_file`

Write a file to the working directory.

**Parameters:**
- `filename` (string): Name of the file to create
- `content` (string): Content to write
- `overwrite` (boolean): Overwrite if file exists (default: false)

**Example:**
```python
write_file("script.py", "print('Hello!')", overwrite=True)
```

### `list_files`

List files in the working directory.

**Parameters:**
- `directory` (string, optional): Subdirectory to list

**Example:**
```python
list_files()
list_files("subdirectory")
```

## Deployment

### Using systemd

Create a service file `/etc/systemd/system/mcp-code-interpreter.service`:

```ini
[Unit]
Description=MCP Code Interpreter Server
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp-code-interpreter
Environment="WORKING_DIR=/var/mcp-workspace"
Environment="MCP_HOST=0.0.0.0"
Environment="MCP_PORT=8000"
Environment="LOG_LEVEL=INFO"
ExecStart=/usr/bin/python -m code_interpreter_mcp
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-code-interpreter
sudo systemctl start mcp-code-interpreter
sudo systemctl status mcp-code-interpreter
```

### Using Docker (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .

ENV WORKING_DIR=/workspace
RUN mkdir -p /workspace

EXPOSE 8000

CMD ["python", "-m", "code_interpreter_mcp"]
```

Build and run:

```bash
docker build -t mcp-code-interpreter .
docker run -d -p 8000:8000 -v /my/workspace:/workspace mcp-code-interpreter
```

## Security Warning

⚠️ **This server does NOT implement sandboxing or resource limits**

Users assume full responsibility for:
- Infinite loops that may exhaust server resources
- Malicious code that could access files outside the working directory
- CPU/memory intensive operations affecting server stability

**Recommendations:**
- Run in a containerized environment (Docker, LXC)
- Use cgroups to limit resources
- Restrict working directory permissions
- Clean the working directory regularly
- Use a reverse proxy (nginx) for authentication
- Consider implementing API key authentication

## Development

### Project Structure

```
code-interpreter-mcp/
├── src/code_interpreter_mcp/
│   ├── server.py           # MCP Server main file
│   ├── config.py           # Configuration management
│   └── executors/
│       ├── base.py         # Base executor interface
│       ├── python.py       # Python executor
│       ├── shell.py        # Shell executor
│       └── c_cpp.py        # C/C++ executor
```

### Testing with MCP Inspector

```bash
# Start the server
WORKING_DIR=/tmp/test python -m code_interpreter_mcp

# In another terminal, run the inspector
npx -y @modelcontextprotocol/inspector

# Connect to: http://localhost:8000/mcp
```

## Requirements

- Python 3.10+
- MCP Python SDK (`mcp`)
- Python interpreter (python3)
- Bash shell (bash or sh)
- GCC or Clang (for C/C++ support)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## References

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Specification](https://modelcontextprotocol.io/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
