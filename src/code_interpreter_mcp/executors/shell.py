"""Shell/Bash code executor"""

import asyncio
import shutil
from typing import Dict, Any

from .base import BaseExecutor


class ShellExecutor(BaseExecutor):
    """Executor for Shell/Bash code"""

    def __init__(self):
        self.shell = self._find_shell()

    def _find_shell(self) -> str:
        """Find shell"""
        # Priority: bash > sh
        for name in ["bash", "sh"]:
            path = shutil.which(name)
            if path:
                return path
        return "/bin/sh"

    def get_language_name(self) -> str:
        return "bash"

    def get_executor_path(self) -> str:
        return self.shell

    async def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Execute shell code"""
        from ..config import Config

        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                self.shell,
                "-c",
                code,
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
                "language": "bash"
            }

        except asyncio.TimeoutError:
            if process:
                process.kill()
                await process.wait()
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "status": -1,
                "language": "bash"
            }
