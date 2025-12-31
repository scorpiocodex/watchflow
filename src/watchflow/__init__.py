"""WatchFlow - Next-Generation Intelligent File Watcher & Automation CLI."""

__version__ = "1.1"
__author__ = "ScorpioCodeX"
__license__ = "MIT"

from watchflow.cli import app
from watchflow.exceptions import (
    CommandExecutionError,
    CommandNotFoundError,
    CommandTimeoutError,
    ConfigNotFoundError,
    ConfigSyntaxError,
    ConfigurationError,
    ConfigValidationError,
    EngineAlreadyRunningError,
    EngineError,
    EngineNotRunningError,
    ExecutionError,
    WatcherError,
    WatcherStartError,
    WatchFlowError,
    WatchPathNotFoundError,
)

__all__ = [
    "app",
    "CommandExecutionError",
    "CommandNotFoundError",
    "CommandTimeoutError",
    "ConfigNotFoundError",
    "ConfigSyntaxError",
    "ConfigurationError",
    "ConfigValidationError",
    "EngineAlreadyRunningError",
    "EngineError",
    "EngineNotRunningError",
    "ExecutionError",
    "WatcherError",
    "WatcherStartError",
    "WatchFlowError",
    "WatchPathNotFoundError",
]
