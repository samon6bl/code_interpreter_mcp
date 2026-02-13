"""Code Interpreter MCP Server - Main server file"""

import json
import os
import shutil
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

from .config import Config
from .executors import PythonExecutor, ShellExecutor, CExecutor, CppExecutor

# Initialize configuration
Config.setup()

# Create MCP server
mcp = FastMCP("code-interpreter")

# Initialize executors
python_executor = PythonExecutor()
shell_executor = ShellExecutor()
c_executor = CExecutor()
cpp_executor = CppExecutor()

# Map language names to executors
EXECUTORS = {
    "python": python_executor,
    "py": python_executor,
    "bash": shell_executor,
    "sh": shell_executor,
    "shell": shell_executor,
    "c": c_executor,
    "cpp": cpp_executor,
    "c++": cpp_executor,
    "cxx": cpp_executor,
}


@mcp.tool()
async def execute_code(
    code: str,
    language: str = "python",
    timeout: int = 300
) -> str:
    """
    Execute code in the specified programming language

    Args:
        code: The code to execute
        language: Programming language (python, bash, c, cpp)
        timeout: Timeout in seconds (default: 300)

    Returns:
        JSON string with execution results including stdout, stderr, and exit status
    """
    language = language.lower()

    if language not in EXECUTORS:
        available = ", ".join(set(EXECUTORS.keys()))
        return json.dumps({
            "error": f"Unsupported language: {language}",
            "supported_languages": available
        }, indent=2)

    executor = EXECUTORS[language]

    if not executor.is_available():
        return json.dumps({
            "error": f"Executor not available: {executor.get_executor_path()}",
            "language": language
        }, indent=2)

    try:
        result = await executor.execute(code, timeout)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "language": language
        }, indent=2)


@mcp.tool()
def list_languages() -> str:
    """
    List all supported programming languages and their compiler/interpreter paths

    Returns:
        JSON string with language names and their availability
    """
    languages = {}

    # Unique executors (avoid duplicates)
    unique_executors = {
        "python": python_executor,
        "bash": shell_executor,
        "c": c_executor,
        "cpp": cpp_executor
    }

    for lang, executor in unique_executors.items():
        languages[lang] = {
            "executor": executor.get_executor_path(),
            "available": executor.is_available()
        }

    return json.dumps(languages, indent=2)


@mcp.tool()
def get_working_dir() -> str:
    """
    Get information about the current working directory

    Returns:
        JSON string with working directory path and disk usage
    """
    import shutil

    try:
        usage = shutil.disk_usage(Config.WORKING_DIR)
        info = {
            "working_directory": str(Config.WORKING_DIR),
            "disk_usage": {
                "total_gb": round(usage.total / (1024**3), 2),
                "used_gb": round(usage.used / (1024**3), 2),
                "free_gb": round(usage.free / (1024**3), 2),
                "percent_used": round((usage.used / usage.total) * 100, 2)
            }
        }
        return json.dumps(info, indent=2)
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "working_directory": str(Config.WORKING_DIR)
        }, indent=2)


@mcp.tool()
def write_file(
    filename: str,
    content: str,
    overwrite: bool = False
) -> str:
    """
    Write a file to the working directory

    Args:
        filename: Name of the file to create
        content: Content to write to the file
        overwrite: Whether to overwrite if file exists (default: False)

    Returns:
        JSON string with result status
    """
    file_path = Config.WORKING_DIR / filename

    # Check if file exists
    if file_path.exists() and not overwrite:
        return json.dumps({
            "error": f"File already exists: {filename}",
            "path": str(file_path),
            "hint": "Use overwrite=True to overwrite existing files"
        }, indent=2)

    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, 'w') as f:
            f.write(content)

        return json.dumps({
            "success": True,
            "filename": filename,
            "path": str(file_path),
            "size_bytes": len(content.encode('utf-8'))
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "filename": filename
        }, indent=2)


@mcp.tool()
def list_files(directory: str = "") -> str:
    """
    List files in the working directory

    Args:
        directory: Optional subdirectory to list (relative to working directory)

    Returns:
        JSON string with file list and metadata
    """
    try:
        target_dir = Config.WORKING_DIR / directory if directory else Config.WORKING_DIR

        if not target_dir.exists():
            return json.dumps({
                "error": f"Directory does not exist: {directory}",
                "working_directory": str(Config.WORKING_DIR)
            }, indent=2)

        if not target_dir.is_dir():
            return json.dumps({
                "error": f"Not a directory: {directory}",
                "working_directory": str(Config.WORKING_DIR)
            }, indent=2)

        files = []
        for item in target_dir.iterdir():
            try:
                stat = item.stat()
                files.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size_bytes": stat.st_size if item.is_file() else None,
                    "modified": stat.st_mtime
                })
            except Exception:
                files.append({
                    "name": item.name,
                    "type": "unknown",
                    "error": "Could not read file info"
                })

        return json.dumps({
            "directory": str(target_dir),
            "working_directory": str(Config.WORKING_DIR),
            "count": len(files),
            "files": sorted(files, key=lambda x: x["name"])
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "working_directory": str(Config.WORKING_DIR)
        }, indent=2)


def main():
    """Main entry point for the MCP server"""
    import logging

    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger("code-interpreter-mcp")
    logger.info(f"Starting Code Interpreter MCP Server")
    logger.info(f"Working directory: {Config.WORKING_DIR}")
    logger.info(f"Available executors:")
    for lang, exec in [("python", python_executor), ("bash", shell_executor),
                       ("c", c_executor), ("cpp", cpp_executor)]:
        logger.info(f"  {lang}: {exec.get_executor_path()} - {'Available' if exec.is_available() else 'Not Found'}")

    # Run server with streamable HTTP transport
    mcp.run(
        transport="streamable-http",
        stateless_http=True,
        json_response=True,
        host=Config.HOST,
        port=Config.PORT
    )


if __name__ == "__main__":
    main()
