"""Configuration management for Code Interpreter MCP Server"""

import os
from pathlib import Path


class Config:
    """Configuration management"""

    # Working directory for code execution
    WORKING_DIR: Path = Path(os.environ.get("WORKING_DIR", "/tmp/code-exec"))

    # MCP Server configuration
    HOST: str = os.environ.get("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("MCP_PORT", "8000"))

    # Logging level
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    @classmethod
    def setup(cls) -> None:
        """Initialize configuration - create working directory if needed"""
        cls.WORKING_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_info(cls) -> dict:
        """Get configuration info as dictionary"""
        return {
            "working_dir": str(cls.WORKING_DIR),
            "host": cls.HOST,
            "port": cls.PORT,
            "log_level": cls.LOG_LEVEL
        }
