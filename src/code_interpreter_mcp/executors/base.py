"""Base executor interface for code execution"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseExecutor(ABC):
    """Base class for code executors"""

    @abstractmethod
    async def execute(
        self,
        code: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute code and return result

        Args:
            code: Code string to execute
            timeout: Timeout in seconds

        Returns:
            Dictionary with keys:
                - stdout: str - Standard output
                - stderr: str - Standard error
                - status: int - Exit code (-1 for timeout)
                - language: str - Language name
        """
        pass

    @abstractmethod
    def get_language_name(self) -> str:
        """Return the language name"""
        pass

    @abstractmethod
    def get_executor_path(self) -> str:
        """Return the path to the compiler/interpreter"""
        pass

    def is_available(self) -> bool:
        """Check if the executor is available"""
        import shutil
        return shutil.which(self.get_executor_path()) is not None
