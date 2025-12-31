"""Custom exceptions for WatchFlow.

This module provides a hierarchy of exceptions for more precise error handling
throughout the WatchFlow application.
"""

from typing import Any, Optional


class WatchFlowError(Exception):
    """Base exception for all WatchFlow errors."""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        """Initialize error.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


# Configuration Errors
class ConfigurationError(WatchFlowError):
    """Base class for configuration-related errors."""

    pass


class ConfigNotFoundError(ConfigurationError):
    """Raised when configuration file is not found."""

    def __init__(self, path: str):
        """Initialize error.

        Args:
            path: Path to the missing configuration file
        """
        super().__init__(
            f"Configuration file not found: {path}",
            details={"path": path},
        )
        self.path = path


class ConfigValidationError(ConfigurationError):
    """Raised when configuration validation fails."""

    def __init__(self, errors: list[str], path: Optional[str] = None):
        """Initialize error.

        Args:
            errors: List of validation error messages
            path: Optional path to the configuration file
        """
        error_count = len(errors)
        message = f"Configuration validation failed with {error_count} error(s)"
        super().__init__(message, details={"errors": errors, "path": path})
        self.errors = errors
        self.path = path


class ConfigSyntaxError(ConfigurationError):
    """Raised when configuration file has invalid syntax."""

    def __init__(self, message: str, line: Optional[int] = None):
        """Initialize error.

        Args:
            message: Parser error message
            line: Optional line number where error occurred
        """
        super().__init__(
            f"Invalid configuration syntax: {message}",
            details={"line": line},
        )
        self.line = line


# Execution Errors
class ExecutionError(WatchFlowError):
    """Base class for command execution errors."""

    pass


class CommandNotFoundError(ExecutionError):
    """Raised when a command executable is not found."""

    def __init__(self, command: str, search_paths: Optional[list[str]] = None):
        """Initialize error.

        Args:
            command: The command that was not found
            search_paths: Paths that were searched
        """
        super().__init__(
            f"Command not found: {command}",
            details={"command": command, "search_paths": search_paths or []},
        )
        self.command = command
        self.search_paths = search_paths or []


class CommandTimeoutError(ExecutionError):
    """Raised when a command execution times out."""

    def __init__(self, command: str, timeout: int):
        """Initialize error.

        Args:
            command: The command that timed out
            timeout: Timeout value in seconds
        """
        super().__init__(
            f"Command '{command}' timed out after {timeout} seconds",
            details={"command": command, "timeout": timeout},
        )
        self.command = command
        self.timeout = timeout


class CommandExecutionError(ExecutionError):
    """Raised when a command fails to execute."""

    def __init__(
        self,
        command: str,
        return_code: int,
        stdout: str = "",
        stderr: str = "",
    ):
        """Initialize error.

        Args:
            command: The command that failed
            return_code: Exit code from the command
            stdout: Standard output from command
            stderr: Standard error from command
        """
        super().__init__(
            f"Command '{command}' failed with exit code {return_code}",
            details={
                "command": command,
                "return_code": return_code,
                "stdout": stdout,
                "stderr": stderr,
            },
        )
        self.command = command
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr


# Watcher Errors
class WatcherError(WatchFlowError):
    """Base class for file watcher errors."""

    pass


class WatchPathNotFoundError(WatcherError):
    """Raised when a watch path does not exist."""

    def __init__(self, path: str, watcher_name: str):
        """Initialize error.

        Args:
            path: The path that was not found
            watcher_name: Name of the watcher
        """
        super().__init__(
            f"Watch path not found: {path}",
            details={"path": path, "watcher": watcher_name},
        )
        self.path = path
        self.watcher_name = watcher_name


class WatcherStartError(WatcherError):
    """Raised when file watcher fails to start."""

    def __init__(self, message: str):
        """Initialize error.

        Args:
            message: Error message
        """
        super().__init__(f"Failed to start file watcher: {message}")


# Engine Errors
class EngineError(WatchFlowError):
    """Base class for engine errors."""

    pass


class EngineAlreadyRunningError(EngineError):
    """Raised when trying to start an already running engine."""

    def __init__(self):
        super().__init__("Engine is already running")


class EngineNotRunningError(EngineError):
    """Raised when trying to stop an engine that isn't running."""

    def __init__(self):
        super().__init__("Engine is not running")
