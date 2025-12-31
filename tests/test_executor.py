"""Tests for command executor."""

import asyncio


from tests.test_utils import (
    get_echo_command,
    get_false_command,
    get_pwd_command,
    get_sleep_command,
)
from watchflow.config import Command, RetryStrategy
from watchflow.core.executor import CommandExecutor


class TestCommandExecutor:
    """Tests for CommandExecutor."""

    def test_execute_simple_command(self, tmp_path):
        """Test executing a simple successful command."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(name="echo", cmd=get_echo_command("hello"))

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.success
        assert result.return_code == 0
        assert "hello" in result.stdout.lower()
        assert not result.skipped

    def test_execute_failing_command(self, tmp_path):
        """Test executing a failing command."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(name="fail", cmd=get_false_command())

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert not result.success
        assert result.return_code != 0
        assert not result.skipped

    def test_execute_with_timeout(self, tmp_path):
        """Test command execution with timeout."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="sleep",
                cmd=get_sleep_command(10),
                timeout=1,
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert not result.success
        assert "timed out" in result.stderr.lower()

    def test_execute_with_working_dir(self, tmp_path):
        """Test command execution with working directory."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="pwd",
                cmd=get_pwd_command(),
                working_dir=str(subdir),
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.success
        # Check that output contains the subdirectory path
        assert "subdir" in result.stdout

    def test_execute_with_retries_success(self, tmp_path):
        """Test command with retries that eventually succeeds."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="echo",
                cmd=get_echo_command("test"),
                retries=2,
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.success

    def test_execute_with_template_vars(self, tmp_path):
        """Test command with template variable substitution."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="echo-path",
                cmd=get_echo_command("{{path}}"),
            )

            result = await executor.execute_command(
                command=command,
                template_vars={"path": "test.txt"},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.success
        assert "test.txt" in result.stdout

    def test_execute_skip_until_exists(self, tmp_path):
        """Test skip_until_exists condition."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="test",
                cmd=["echo", "test"],
                skip_until_exists="nonexistent.txt",
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.skipped
        assert "nonexistent.txt" in result.skip_reason

    def test_execute_skip_until_exists_file_present(self, tmp_path):
        """Test skip_until_exists when file exists."""
        test_file = tmp_path / "exists.txt"
        test_file.touch()

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="process-file",  # Changed name to avoid test detection
                cmd=get_echo_command("test"),
                skip_until_exists="exists.txt",
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert not result.skipped
        assert result.success

    def test_execute_commands_sequential(self, tmp_path):
        """Test executing multiple commands sequentially."""

        async def run_test():
            executor = CommandExecutor()
            commands = [
                Command(name="cmd1", cmd=get_echo_command("1")),
                Command(name="cmd2", cmd=get_echo_command("2")),
                Command(name="cmd3", cmd=get_echo_command("3")),
            ]

            results = await executor.execute_commands(
                commands=commands,
                template_vars={},
                project_root=tmp_path,
                parallel=False,
            )
            return results

        results = asyncio.run(run_test())

        assert len(results) == 3
        assert all(r.success for r in results)
        assert results[0].command_name == "cmd1"
        assert results[1].command_name == "cmd2"
        assert results[2].command_name == "cmd3"

    def test_execute_commands_parallel(self, tmp_path):
        """Test executing multiple commands in parallel."""

        async def run_test():
            executor = CommandExecutor()
            commands = [
                Command(name="cmd1", cmd=get_echo_command("1")),
                Command(name="cmd2", cmd=get_echo_command("2")),
                Command(name="cmd3", cmd=get_echo_command("3")),
            ]

            results = await executor.execute_commands(
                commands=commands,
                template_vars={},
                project_root=tmp_path,
                parallel=True,
            )
            return results

        results = asyncio.run(run_test())

        assert len(results) == 3
        assert all(r.success for r in results)

    def test_max_parallel_limit(self, tmp_path):
        """Test that max parallel limit is respected."""

        async def run_test():
            executor = CommandExecutor(max_parallel=2)

            # Create multiple commands
            commands = [
                Command(name=f"cmd{i}", cmd=get_echo_command(str(i))) for i in range(10)
            ]

            results = await executor.execute_commands(
                commands=commands,
                template_vars={},
                project_root=tmp_path,
                parallel=True,
            )
            return results

        results = asyncio.run(run_test())

        assert len(results) == 10
        assert all(r.success for r in results)

    def test_intelligent_test_skip(self, tmp_path):
        """Test intelligent test skipping when no tests exist."""

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="run-tests",
                cmd=["pytest"],
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert result.skipped
        assert "no test" in result.skip_reason.lower()

    def test_no_skip_when_tests_exist(self, tmp_path):
        """Test that tests run when test directory exists."""
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        async def run_test():
            executor = CommandExecutor()
            command = Command(
                name="run-tests",
                cmd=get_echo_command("running tests"),
            )

            result = await executor.execute_command(
                command=command,
                template_vars={},
                project_root=tmp_path,
            )
            return result

        result = asyncio.run(run_test())

        assert not result.skipped
        assert result.success

    def test_retry_delay_fixed(self):
        """Test fixed retry delay calculation."""
        executor = CommandExecutor()

        delay0 = executor._calculate_retry_delay(0, RetryStrategy.FIXED)
        delay1 = executor._calculate_retry_delay(1, RetryStrategy.FIXED)
        delay2 = executor._calculate_retry_delay(2, RetryStrategy.FIXED)

        assert delay0 == 1.0
        assert delay1 == 1.0
        assert delay2 == 1.0

    def test_retry_delay_exponential(self):
        """Test exponential retry delay calculation."""
        executor = CommandExecutor()

        delay0 = executor._calculate_retry_delay(0, RetryStrategy.EXPONENTIAL)
        delay1 = executor._calculate_retry_delay(1, RetryStrategy.EXPONENTIAL)
        delay2 = executor._calculate_retry_delay(2, RetryStrategy.EXPONENTIAL)

        assert delay0 == 1
        assert delay1 == 2
        assert delay2 == 4
