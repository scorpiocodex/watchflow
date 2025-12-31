"""Command execution engine."""

import asyncio
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

from watchflow.config.models import Command, RetryStrategy
from watchflow.utils.logger import get_logger
from watchflow.utils.templates import TemplateEngine

logger = get_logger(__name__)


class CommandNotFoundError(Exception):
    """Raised when a command executable is not found."""

    def __init__(self, command: str, search_paths: Optional[list[str]] = None):
        """Initialize error.

        Args:
            command: The command that was not found
            search_paths: Paths that were searched (optional)
        """
        self.command = command
        self.search_paths = search_paths or []
        super().__init__(f"Command not found: {command}")


def find_command(cmd: str) -> Optional[str]:
    """Find command executable in PATH.

    Args:
        cmd: Command name to find

    Returns:
        Full path to executable if found, None otherwise
    """
    return shutil.which(cmd)


def validate_command(cmd_list: list[str]) -> tuple[bool, Optional[str]]:
    """Validate that a command exists and can be executed.

    Args:
        cmd_list: Command and arguments

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not cmd_list:
        return False, "Empty command"

    cmd = cmd_list[0]

    # Check if it's a path
    if "/" in cmd or "\\" in cmd:
        if Path(cmd).exists():
            return True, None
        return False, f"Command path not found: {cmd}"

    # Check if it's in PATH
    if find_command(cmd):
        return True, None

    return False, f"Command not found in PATH: {cmd}"


class ExecutionResult:
    """Result of command execution."""

    def __init__(
        self,
        command_name: str,
        success: bool,
        duration: float,
        return_code: int = 0,
        stdout: str = "",
        stderr: str = "",
        skipped: bool = False,
        skip_reason: Optional[str] = None,
    ):
        """Initialize execution result."""
        self.command_name = command_name
        self.success = success
        self.duration = duration
        self.return_code = return_code
        self.stdout = stdout
        self.stderr = stderr
        self.skipped = skipped
        self.skip_reason = skip_reason


class CommandExecutor:
    """Executes commands with retry logic and timeouts."""

    def __init__(self, max_parallel: int = 4, validate_commands: bool = True):
        """Initialize executor.

        Args:
            max_parallel: Maximum number of parallel executions
            validate_commands: Whether to validate command existence before execution
        """
        self.max_parallel = max_parallel
        self.validate_commands = validate_commands
        self.semaphore = asyncio.Semaphore(max_parallel)

    async def execute_command(
        self,
        command: Command,
        template_vars: dict[str, Any],
        project_root: Path,
    ) -> ExecutionResult:
        """Execute a single command.

        Args:
            command: Command configuration
            template_vars: Template variables for substitution
            project_root: Project root directory

        Returns:
            ExecutionResult with execution details
        """
        async with self.semaphore:
            start_time = time.time()

            # Check skip conditions
            skip_reason = self._check_skip_conditions(command, project_root)
            if skip_reason:
                duration = time.time() - start_time
                return ExecutionResult(
                    command_name=command.name,
                    success=True,
                    duration=duration,
                    skipped=True,
                    skip_reason=skip_reason,
                )

            # Substitute template variables
            cmd_list = TemplateEngine.substitute_list(command.cmd, template_vars)

            # Validate command exists (skip on Windows where shell=True handles it)
            import sys

            if self.validate_commands and sys.platform != "win32":
                is_valid, error = validate_command(cmd_list)
                if not is_valid:
                    duration = time.time() - start_time
                    logger.warning(
                        "command_not_found",
                        command=command.name,
                        error=error,
                    )
                    return ExecutionResult(
                        command_name=command.name,
                        success=False,
                        duration=duration,
                        return_code=-1,
                        stderr=error or "Command not found",
                    )

            # Execute with retries
            for attempt in range(command.retries + 1):
                try:
                    result = await self._run_command(
                        cmd_list=cmd_list,
                        timeout=command.timeout,
                        working_dir=command.working_dir or str(project_root),
                    )

                    duration = time.time() - start_time

                    if result.returncode == 0:
                        logger.debug(
                            "command_success",
                            command=command.name,
                            attempt=attempt + 1,
                            duration=duration,
                        )
                        return ExecutionResult(
                            command_name=command.name,
                            success=True,
                            duration=duration,
                            return_code=result.returncode,
                            stdout=result.stdout,
                            stderr=result.stderr,
                        )

                    # Command failed, check if we should retry
                    if attempt < command.retries:
                        wait_time = self._calculate_retry_delay(
                            attempt, command.retry_strategy
                        )
                        logger.debug(
                            "command_retry",
                            command=command.name,
                            attempt=attempt + 1,
                            wait_time=wait_time,
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        # Final attempt failed
                        logger.debug(
                            "command_failed",
                            command=command.name,
                            return_code=result.returncode,
                            duration=duration,
                        )
                        return ExecutionResult(
                            command_name=command.name,
                            success=False,
                            duration=duration,
                            return_code=result.returncode,
                            stdout=result.stdout,
                            stderr=result.stderr,
                        )

                except asyncio.TimeoutError:
                    duration = time.time() - start_time
                    logger.debug(
                        "command_timeout", command=command.name, timeout=command.timeout
                    )
                    return ExecutionResult(
                        command_name=command.name,
                        success=False,
                        duration=duration,
                        return_code=-1,
                        stderr=f"Command timed out after {command.timeout}s",
                    )

                except (OSError, ValueError) as e:
                    duration = time.time() - start_time
                    logger.error("command_error", command=command.name, error=str(e))
                    return ExecutionResult(
                        command_name=command.name,
                        success=False,
                        duration=duration,
                        return_code=-1,
                        stderr=str(e),
                    )

            # Should not reach here, but just in case
            duration = time.time() - start_time
            return ExecutionResult(
                command_name=command.name,
                success=False,
                duration=duration,
                return_code=-1,
                stderr="Unknown error",
            )

    async def execute_commands(
        self,
        commands: list[Command],
        template_vars: dict[str, Any],
        project_root: Path,
        parallel: bool = False,
    ) -> list[ExecutionResult]:
        """Execute multiple commands.

        Args:
            commands: List of commands to execute
            template_vars: Template variables for substitution
            project_root: Project root directory
            parallel: Whether to execute in parallel

        Returns:
            List of ExecutionResults
        """
        if parallel:
            # Execute all commands in parallel
            tasks = [
                self.execute_command(cmd, template_vars, project_root)
                for cmd in commands
            ]
            results = await asyncio.gather(*tasks)
            return list(results)
        else:
            # Execute commands sequentially
            result_list: list[ExecutionResult] = []
            for cmd in commands:
                result = await self.execute_command(cmd, template_vars, project_root)
                result_list.append(result)
            return result_list

    async def _run_command(
        self,
        cmd_list: list[str],
        timeout: Optional[int],
        working_dir: str,
    ) -> subprocess.CompletedProcess[str]:
        """Run a command as subprocess.

        Args:
            cmd_list: Command and arguments
            timeout: Timeout in seconds
            working_dir: Working directory

        Returns:
            CompletedProcess with result
        """
        # On Windows, we need shell=True for built-in commands like echo
        import sys

        use_shell = sys.platform == "win32"

        if use_shell:
            # Convert list to string for shell execution on Windows
            # Note: Commands come from trusted configuration files.
            # Windows cmd.exe doesn't support POSIX-style quoting (shlex.quote),
            # so we use subprocess.list2cmdline which handles Windows escaping.
            cmd_str = subprocess.list2cmdline(cmd_list)
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )
        else:
            process = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout,
            )

            # Note: We need to check the actual return code from the result
            actual_returncode = (
                process.returncode if process.returncode is not None else 0
            )

            return subprocess.CompletedProcess(
                args=cmd_list,
                returncode=actual_returncode,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
            )

        except asyncio.TimeoutError:
            # Kill process on timeout
            process.kill()
            await process.wait()
            raise

    def _check_skip_conditions(
        self, command: Command, project_root: Path
    ) -> Optional[str]:
        """Check if command should be skipped.

        Args:
            command: Command configuration
            project_root: Project root directory

        Returns:
            Skip reason if should skip, None otherwise
        """
        # Check skip_until_exists
        if command.skip_until_exists:
            path = project_root / command.skip_until_exists
            if not path.exists():
                return f"waiting for {command.skip_until_exists}"

        # Check if tests exist (intelligent test handling)
        if "test" in command.name.lower():
            if not self._has_tests(project_root):
                return "no test files or directories found"

        return None

    def _has_tests(self, project_root: Path) -> bool:
        """Check if project has test files or directories.

        Args:
            project_root: Project root directory

        Returns:
            True if tests exist, False otherwise
        """
        # Common test directories
        test_dirs = ["tests", "test", "spec", "__tests__"]
        for test_dir in test_dirs:
            if (project_root / test_dir).exists():
                return True

        # Common test file patterns
        test_patterns = [
            "*_test.py",
            "test_*.py",
            "*_test.go",
            "*_spec.rb",
            "*.test.js",
        ]
        for pattern in test_patterns:
            if list(project_root.rglob(pattern)):
                return True

        return False

    def _calculate_retry_delay(self, attempt: int, strategy: RetryStrategy) -> float:
        """Calculate delay before retry.

        Args:
            attempt: Attempt number (0-indexed)
            strategy: Retry strategy

        Returns:
            Delay in seconds
        """
        if strategy == RetryStrategy.EXPONENTIAL:
            # Exponential backoff: 1s, 2s, 4s, 8s, ...
            return min(2**attempt, 60)  # Cap at 60 seconds
        else:
            # Fixed delay: 1 second
            return 1.0
