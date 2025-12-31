"""Tests for new features added to WatchFlow."""

import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from watchflow.core.executor import (
    CommandExecutor,
    ExecutionResult,
    find_command,
    validate_command,
)
from watchflow.core.watcher import compute_file_hash
from watchflow.exceptions import (
    CommandExecutionError,
    CommandNotFoundError,
    CommandTimeoutError,
    ConfigNotFoundError,
    ConfigSyntaxError,
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


class TestFileHashDetection:
    """Tests for file hash-based change detection."""

    def test_compute_file_hash_returns_hash(self, tmp_path):
        """Test that compute_file_hash returns a valid hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        hash_result = compute_file_hash(str(test_file))
        assert hash_result is not None
        assert len(hash_result) == 32  # MD5 hex digest length

    def test_compute_file_hash_consistent(self, tmp_path):
        """Test that same content produces same hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")

        hash1 = compute_file_hash(str(test_file))
        hash2 = compute_file_hash(str(test_file))
        assert hash1 == hash2

    def test_compute_file_hash_changes_on_content_change(self, tmp_path):
        """Test that different content produces different hash."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("hello world")
        hash1 = compute_file_hash(str(test_file))

        test_file.write_text("hello world modified")
        hash2 = compute_file_hash(str(test_file))

        assert hash1 != hash2

    def test_compute_file_hash_nonexistent_file(self, tmp_path):
        """Test that nonexistent file returns None."""
        result = compute_file_hash(str(tmp_path / "nonexistent.txt"))
        assert result is None

    def test_compute_file_hash_large_file(self, tmp_path):
        """Test hash computation for larger files."""
        test_file = tmp_path / "large.txt"
        # Create a file larger than the chunk size (8192 bytes)
        test_file.write_text("x" * 20000)

        hash_result = compute_file_hash(str(test_file))
        assert hash_result is not None
        assert len(hash_result) == 32


class TestCommandValidation:
    """Tests for command existence validation."""

    def test_find_command_existing(self):
        """Test finding an existing command."""
        # Python should exist on all platforms
        result = find_command("python") or find_command("python3")
        assert result is not None

    def test_find_command_nonexistent(self):
        """Test finding a nonexistent command."""
        result = find_command("nonexistent_command_12345")
        assert result is None

    def test_validate_command_empty(self):
        """Test validating empty command list."""
        is_valid, error = validate_command([])
        assert not is_valid
        assert error == "Empty command"

    def test_validate_command_existing(self):
        """Test validating an existing command."""
        # Use a command that exists on all platforms
        cmd = "python" if sys.platform == "win32" else "python3"
        is_valid, error = validate_command([cmd, "--version"])
        assert is_valid
        assert error is None

    def test_validate_command_nonexistent(self):
        """Test validating a nonexistent command."""
        is_valid, error = validate_command(["nonexistent_cmd_12345"])
        assert not is_valid
        assert "not found" in error.lower()

    def test_validate_command_with_path(self, tmp_path):
        """Test validating command with file path."""
        # Create a dummy script
        script = tmp_path / "script.py"
        script.write_text("print('hello')")

        is_valid, error = validate_command([str(script)])
        assert is_valid
        assert error is None

    def test_validate_command_with_nonexistent_path(self):
        """Test validating command with nonexistent path."""
        is_valid, error = validate_command(["/nonexistent/path/script.py"])
        assert not is_valid
        assert "not found" in error.lower()


class TestCommandExecutorValidation:
    """Tests for CommandExecutor with validation."""

    def test_executor_validates_commands(self, tmp_path):
        """Test that executor validates commands before running."""
        from watchflow.config import Command

        async def run_test():
            executor = CommandExecutor(validate_commands=True)
            cmd = Command(name="test", cmd=["nonexistent_command_12345"])

            result = await executor.execute_command(
                cmd,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        # On Windows, we skip validation due to shell=True
        if sys.platform != "win32":
            assert not result.success
            assert "not found" in result.stderr.lower()

    def test_executor_skips_validation_when_disabled(self, tmp_path):
        """Test that executor can skip validation."""
        from watchflow.config import Command

        async def run_test():
            executor = CommandExecutor(validate_commands=False)
            cmd = Command(
                name="test",
                cmd=["echo", "hello"],  # Valid command
                timeout=5,
            )

            result = await executor.execute_command(
                cmd,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())
        assert result.success


class TestExceptionHierarchy:
    """Tests for the exception hierarchy."""

    def test_watchflow_error_base(self):
        """Test base WatchFlowError."""
        error = WatchFlowError("Test error", details={"key": "value"})
        assert error.message == "Test error"
        assert error.details == {"key": "value"}
        assert str(error) == "Test error"

    def test_config_not_found_error(self):
        """Test ConfigNotFoundError."""
        error = ConfigNotFoundError("/path/to/config.yaml")
        assert error.path == "/path/to/config.yaml"
        assert "not found" in error.message.lower()
        assert isinstance(error, WatchFlowError)

    def test_config_validation_error(self):
        """Test ConfigValidationError."""
        errors = ["Error 1", "Error 2"]
        error = ConfigValidationError(errors, path="/config.yaml")
        assert error.errors == errors
        assert error.path == "/config.yaml"
        assert "2 error" in error.message
        assert isinstance(error, WatchFlowError)

    def test_config_syntax_error(self):
        """Test ConfigSyntaxError."""
        error = ConfigSyntaxError("Invalid syntax", line=10)
        assert error.line == 10
        assert "Invalid syntax" in error.message
        assert isinstance(error, WatchFlowError)

    def test_command_not_found_error(self):
        """Test CommandNotFoundError."""
        error = CommandNotFoundError("pytest", search_paths=["/usr/bin"])
        assert error.command == "pytest"
        assert error.search_paths == ["/usr/bin"]
        assert isinstance(error, ExecutionError)
        assert isinstance(error, WatchFlowError)

    def test_command_timeout_error(self):
        """Test CommandTimeoutError."""
        error = CommandTimeoutError("slow_command", 30)
        assert error.command == "slow_command"
        assert error.timeout == 30
        assert "30 seconds" in error.message
        assert isinstance(error, ExecutionError)

    def test_command_execution_error(self):
        """Test CommandExecutionError."""
        error = CommandExecutionError(
            "failed_cmd",
            return_code=1,
            stdout="out",
            stderr="err",
        )
        assert error.command == "failed_cmd"
        assert error.return_code == 1
        assert error.stdout == "out"
        assert error.stderr == "err"
        assert isinstance(error, ExecutionError)

    def test_watch_path_not_found_error(self):
        """Test WatchPathNotFoundError."""
        error = WatchPathNotFoundError("/src", "my-watcher")
        assert error.path == "/src"
        assert error.watcher_name == "my-watcher"
        assert isinstance(error, WatcherError)

    def test_watcher_start_error(self):
        """Test WatcherStartError."""
        error = WatcherStartError("Permission denied")
        assert "Permission denied" in error.message
        assert isinstance(error, WatcherError)

    def test_engine_already_running_error(self):
        """Test EngineAlreadyRunningError."""
        error = EngineAlreadyRunningError()
        assert "already running" in error.message.lower()
        assert isinstance(error, EngineError)

    def test_engine_not_running_error(self):
        """Test EngineNotRunningError."""
        error = EngineNotRunningError()
        assert "not running" in error.message.lower()
        assert isinstance(error, EngineError)

    def test_exception_inheritance(self):
        """Test that all exceptions inherit from WatchFlowError."""
        exceptions = [
            ConfigNotFoundError("/path"),
            ConfigValidationError(["error"]),
            ConfigSyntaxError("error"),
            CommandNotFoundError("cmd"),
            CommandTimeoutError("cmd", 30),
            CommandExecutionError("cmd", 1),
            WatchPathNotFoundError("/path", "watcher"),
            WatcherStartError("error"),
            EngineAlreadyRunningError(),
            EngineNotRunningError(),
        ]

        for exc in exceptions:
            assert isinstance(exc, WatchFlowError), f"{type(exc)} should inherit from WatchFlowError"


class TestUISpinner:
    """Tests for the UI spinner functionality."""

    def test_command_spinner_context_exists(self):
        """Test that CommandSpinnerContext class exists."""
        from watchflow.ui.renderer import CommandSpinnerContext
        assert CommandSpinnerContext is not None

    def test_ui_renderer_has_spinner_method(self):
        """Test that UIRenderer has command_spinner method."""
        from watchflow.ui.renderer import UIRenderer
        renderer = UIRenderer(theme_name="minimal")
        assert hasattr(renderer, "command_spinner")
        assert callable(renderer.command_spinner)

    def test_spinner_context_update(self):
        """Test that spinner context can be updated."""
        from watchflow.ui.renderer import CommandSpinnerContext
        from rich.spinner import Spinner

        spinner = Spinner("dots", text="initial")
        ctx = CommandSpinnerContext(spinner, "test-cmd")

        ctx.update("running...")
        assert "test-cmd" in spinner.text
        assert "running" in spinner.text
