"""Python code executor"""

import asyncio
import os
import shutil
import sys
import tempfile
from typing import Dict, Any

from .base import BaseExecutor


class PythonExecutor(BaseExecutor):
    """Executor for Python code"""

    def __init__(self):
        self.interpreter = self._find_python()

    def _find_python(self) -> str:
        """Find Python interpreter"""
        # Priority: python3 > python > sys.executable
        for name in ["python3", "python"]:
            path = shutil.which(name)
            if path:
                return path
        # Fallback to current Python
        return sys.executable

    def get_language_name(self) -> str:
        return "python"

    def get_executor_path(self) -> str:
        return self.interpreter

    async def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute Python code"""
        from ..config import Config

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            dir=Config.WORKING_DIR
        ) as f:
            f.write(code)
            temp_file = f.name

        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                self.interpreter,
                temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Config.WORKING_DIR
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )

            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "status": process.returncode,
                "language": "python"
            }

        except asyncio.TimeoutError:
            if process:
                process.kill()
                await process.wait()
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "status": -1,
                "language": "python"
            }
        finally:
            try:
                os.unlink(temp_file)
            except Exception:
                pass
