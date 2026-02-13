"""C/C++ code executor"""

import asyncio
import os
import shutil
import tempfile
from typing import Dict, Any

from .base import BaseExecutor


class CExecutor(BaseExecutor):
    """Executor for C code"""

    def __init__(self):
        self.compiler = self._find_compiler()
        self.language = "c"

    def _find_compiler(self) -> str:
        """Find C compiler"""
        for name in ["gcc", "clang"]:
            if shutil.which(name):
                return name
        raise RuntimeError("C compiler not found")

    def get_language_name(self) -> str:
        return "c"

    def get_executor_path(self) -> str:
        return self.compiler

    async def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Compile and execute C code"""
        from ..config import Config

        # Create source file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.c',
            delete=False,
            dir=Config.WORKING_DIR
        ) as src:
            src.write(code)
            src_file = src.name

        # Output file (same name without extension)
        output_file = src_file.replace('.c', '')

        compile_proc = None
        exec_proc = None

        try:
            # Compile
            compile_proc = await asyncio.create_subprocess_exec(
                self.compiler,
                src_file,
                "-o", output_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Config.WORKING_DIR
            )

            stdout, compile_err = await compile_proc.communicate()

            if compile_proc.returncode != 0:
                return {
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": f"Compilation error:\n{compile_err.decode('utf-8', errors='replace')}",
                    "status": compile_proc.returncode,
                    "language": "c"
                }

            # Execute
            exec_proc = await asyncio.create_subprocess_exec(
                output_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Config.WORKING_DIR
            )

            stdout, stderr = await asyncio.wait_for(
                exec_proc.communicate(),
                timeout=timeout
            )

            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "status": exec_proc.returncode,
                "language": "c"
            }

        except asyncio.TimeoutError:
            if exec_proc:
                exec_proc.kill()
                await exec_proc.wait()
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "status": -1,
                "language": "c"
            }
        finally:
            # Clean up temporary files
            for f in [src_file, output_file]:
                try:
                    os.unlink(f)
                except Exception:
                    pass


class CppExecutor(BaseExecutor):
    """Executor for C++ code"""

    def __init__(self):
        self.compiler = self._find_compiler()
        self.language = "cpp"

    def _find_compiler(self) -> str:
        """Find C++ compiler"""
        for name in ["g++", "clang++"]:
            if shutil.which(name):
                return name
        raise RuntimeError("C++ compiler not found")

    def get_language_name(self) -> str:
        return "cpp"

    def get_executor_path(self) -> str:
        return self.compiler

    async def execute(self, code: str, timeout: int = 300) -> Dict[str, Any]:
        """Compile and execute C++ code"""
        from ..config import Config

        # Create source file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.cpp',
            delete=False,
            dir=Config.WORKING_DIR
        ) as src:
            src.write(code)
            src_file = src.name

        # Output file (same name without extension)
        output_file = src_file.replace('.cpp', '')

        compile_proc = None
        exec_proc = None

        try:
            # Compile
            compile_proc = await asyncio.create_subprocess_exec(
                self.compiler,
                src_file,
                "-o", output_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Config.WORKING_DIR
            )

            stdout, compile_err = await compile_proc.communicate()

            if compile_proc.returncode != 0:
                return {
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": f"Compilation error:\n{compile_err.decode('utf-8', errors='replace')}",
                    "status": compile_proc.returncode,
                    "language": "cpp"
                }

            # Execute
            exec_proc = await asyncio.create_subprocess_exec(
                output_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Config.WORKING_DIR
            )

            stdout, stderr = await asyncio.wait_for(
                exec_proc.communicate(),
                timeout=timeout
            )

            return {
                "stdout": stdout.decode('utf-8', errors='replace'),
                "stderr": stderr.decode('utf-8', errors='replace'),
                "status": exec_proc.returncode,
                "language": "cpp"
            }

        except asyncio.TimeoutError:
            if exec_proc:
                exec_proc.kill()
                await exec_proc.wait()
            return {
                "stdout": "",
                "stderr": f"Execution timed out after {timeout} seconds",
                "status": -1,
                "language": "cpp"
            }
        finally:
            # Clean up temporary files
            for f in [src_file, output_file]:
                try:
                    os.unlink(f)
                except Exception:
                    pass
