"""Tests for configuration models and validation."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from watchflow.config import (
    Command,
    Config,
    ConfigValidator,
    GlobalConfig,
    RetryStrategy,
    UITheme,
    Watcher,
    expand_env_vars,
)
from watchflow.exceptions import (
    ConfigNotFoundError,
    ConfigSyntaxError,
    ConfigValidationError,
)


class TestCommand:
    """Tests for Command model."""

    def test_valid_command(self):
        """Test valid command creation."""
        cmd = Command(
            name="test-command",
            cmd=["echo", "hello"],
        )
        assert cmd.name == "test-command"
        assert cmd.cmd == ["echo", "hello"]
        assert cmd.timeout is None
        assert cmd.retries == 0

    def test_command_with_all_fields(self):
        """Test command with all optional fields."""
        cmd = Command(
            name="complex-command",
            cmd=["python", "script.py"],
            timeout=60,
            retries=3,
            retry_strategy=RetryStrategy.EXPONENTIAL,
            working_dir=".",
            skip_until_exists="output.txt",
            only_if_changed=["*.py"],
        )
        assert cmd.timeout == 60
        assert cmd.retries == 3
        assert cmd.retry_strategy == RetryStrategy.EXPONENTIAL

    def test_empty_command_fails(self):
        """Test that empty command fails validation."""
        with pytest.raises(ValidationError):
            Command(name="test", cmd=[])

    def test_invalid_retries_fails(self):
        """Test that invalid retry count fails."""
        with pytest.raises(ValidationError):
            Command(name="test", cmd=["echo"], retries=-1)

        with pytest.raises(ValidationError):
            Command(name="test", cmd=["echo"], retries=11)


class TestWatcher:
    """Tests for Watcher model."""

    def test_valid_watcher(self, tmp_path):
        """Test valid watcher creation."""
        watcher = Watcher(
            name="test-watcher",
            paths=[str(tmp_path)],
            commands=[Command(name="cmd", cmd=["echo"])],
        )
        assert watcher.name == "test-watcher"
        assert len(watcher.commands) == 1
        assert watcher.recursive is True
        assert watcher.debounce == 100

    def test_watcher_with_patterns(self, tmp_path):
        """Test watcher with patterns."""
        watcher = Watcher(
            name="test-watcher",
            paths=[str(tmp_path)],
            patterns=["*.py", "*.js"],
            ignore_patterns=["*.pyc", "__pycache__"],
            debounce=500,
            commands=[Command(name="cmd", cmd=["echo"])],
            parallel=True,
        )
        assert watcher.patterns == ["*.py", "*.js"]
        assert watcher.ignore_patterns == ["*.pyc", "__pycache__"]
        assert watcher.debounce == 500
        assert watcher.parallel is True

    def test_empty_paths_fails(self):
        """Test that empty paths fails validation."""
        with pytest.raises(ValidationError):
            Watcher(
                name="test",
                paths=[],
                commands=[Command(name="cmd", cmd=["echo"])],
            )

    def test_nonexistent_path_fails(self):
        """Test that nonexistent path fails validation."""
        with pytest.raises(ValidationError):
            Watcher(
                name="test",
                paths=["/nonexistent/path/12345"],
                commands=[Command(name="cmd", cmd=["echo"])],
            )

    def test_empty_commands_fails(self, tmp_path):
        """Test that empty commands fails validation."""
        with pytest.raises(ValidationError):
            Watcher(
                name="test",
                paths=[str(tmp_path)],
                commands=[],
            )


class TestGlobalConfig:
    """Tests for GlobalConfig model."""

    def test_default_global_config(self):
        """Test default global config."""
        config = GlobalConfig()
        assert config.theme == UITheme.PRO
        assert config.fail_fast is False
        assert config.max_parallel_commands == 4

    def test_custom_global_config(self):
        """Test custom global config."""
        config = GlobalConfig(
            theme=UITheme.NEON,
            fail_fast=True,
            max_parallel_commands=8,
        )
        assert config.theme == UITheme.NEON
        assert config.fail_fast is True
        assert config.max_parallel_commands == 8

    def test_invalid_max_parallel_fails(self):
        """Test that invalid max_parallel fails."""
        with pytest.raises(ValidationError):
            GlobalConfig(max_parallel_commands=0)

        with pytest.raises(ValidationError):
            GlobalConfig(max_parallel_commands=33)


class TestConfig:
    """Tests for Config model."""

    def test_minimal_config(self, tmp_path):
        """Test minimal valid configuration."""
        config = Config(
            version=1,
            watchers=[
                Watcher(
                    name="test",
                    paths=[str(tmp_path)],
                    commands=[Command(name="cmd", cmd=["echo"])],
                )
            ],
        )
        assert config.version == 1
        assert len(config.watchers) == 1

    def test_full_config(self, tmp_path):
        """Test full configuration with all fields."""
        config = Config(
            version=1,
            project_name="test-project",
            project_type="python",
            global_config=GlobalConfig(theme=UITheme.MINIMAL),
            watchers=[
                Watcher(
                    name="test",
                    paths=[str(tmp_path)],
                    commands=[Command(name="cmd", cmd=["echo"])],
                )
            ],
        )
        assert config.project_name == "test-project"
        assert config.project_type == "python"
        assert config.global_config.theme == UITheme.MINIMAL

    def test_global_alias(self, tmp_path):
        """Test that 'global' alias works."""
        data = {
            "version": 1,
            "global": {"theme": "neon"},
            "watchers": [
                {
                    "name": "test",
                    "paths": [str(tmp_path)],
                    "commands": [{"name": "cmd", "cmd": ["echo"]}],
                }
            ],
        }
        config = Config(**data)
        assert config.global_config.theme == UITheme.NEON

    def test_empty_watchers_fails(self):
        """Test that empty watchers fails validation."""
        with pytest.raises(ValidationError):
            Config(version=1, watchers=[])


class TestConfigValidator:
    """Tests for ConfigValidator."""

    def test_load_valid_config(self, tmp_path):
        """Test loading valid configuration."""
        config_path = tmp_path / "config.yaml"
        config_content = f"""
version: 1
project_name: test
watchers:
  - name: test-watcher
    paths:
      - {tmp_path}
    commands:
      - name: test-cmd
        cmd: ["echo", "hello"]
"""
        config_path.write_text(config_content)

        config = ConfigValidator.load_config(config_path)
        assert config.project_name == "test"
        assert len(config.watchers) == 1

    def test_load_nonexistent_file_fails(self):
        """Test loading nonexistent file fails."""
        with pytest.raises(ConfigNotFoundError) as exc_info:
            ConfigValidator.load_config(Path("/nonexistent.yaml"))
        assert "nonexistent.yaml" in str(exc_info.value.path)

    def test_load_invalid_yaml_fails(self, tmp_path):
        """Test loading invalid YAML fails."""
        config_path = tmp_path / "invalid.yaml"
        config_path.write_text("invalid: yaml: content:")

        with pytest.raises(ConfigSyntaxError):
            ConfigValidator.load_config(config_path)

    def test_load_empty_file_fails(self, tmp_path):
        """Test loading empty file fails."""
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")

        with pytest.raises(ConfigValidationError) as exc_info:
            ConfigValidator.load_config(config_path)
        assert "empty" in exc_info.value.errors[0].lower()

    def test_save_config(self, tmp_path):
        """Test saving configuration."""
        config = Config(
            version=1,
            project_name="test",
            watchers=[
                Watcher(
                    name="test",
                    paths=[str(tmp_path)],
                    commands=[Command(name="cmd", cmd=["echo"])],
                )
            ],
        )

        config_path = tmp_path / "saved.yaml"
        ConfigValidator.save_config(config, config_path)

        assert config_path.exists()

        # Load it back
        loaded = ConfigValidator.load_config(config_path)
        assert loaded.project_name == "test"

    def test_validate_config_dict(self, tmp_path):
        """Test validating configuration dictionary."""
        data = {
            "version": 1,
            "watchers": [
                {
                    "name": "test",
                    "paths": [str(tmp_path)],
                    "commands": [{"name": "cmd", "cmd": ["echo"]}],
                }
            ],
        }

        is_valid, errors = ConfigValidator.validate_config_dict(data)
        assert is_valid
        assert len(errors) == 0

    def test_validate_invalid_dict(self):
        """Test validating invalid configuration dictionary."""
        data = {
            "version": 1,
            "watchers": [],  # Empty watchers should fail
        }

        is_valid, errors = ConfigValidator.validate_config_dict(data)
        assert not is_valid
        assert len(errors) > 0


class TestEnvironmentVariableExpansion:
    """Tests for environment variable expansion in configuration."""

    def test_expand_simple_env_var(self, monkeypatch):
        """Test simple environment variable expansion."""
        monkeypatch.setenv("TEST_VAR", "hello")
        result = expand_env_vars("${TEST_VAR}")
        assert result == "hello"

    def test_expand_env_var_with_default(self, monkeypatch):
        """Test environment variable with default value."""
        # When env var exists, use it
        monkeypatch.setenv("EXISTING_VAR", "value")
        result = expand_env_vars("${EXISTING_VAR:-default}")
        assert result == "value"

        # When env var doesn't exist, use default
        monkeypatch.delenv("NONEXISTENT_VAR", raising=False)
        result = expand_env_vars("${NONEXISTENT_VAR:-default_value}")
        assert result == "default_value"

    def test_expand_env_var_in_string(self, monkeypatch):
        """Test environment variable in middle of string."""
        monkeypatch.setenv("NAME", "world")
        result = expand_env_vars("hello ${NAME}!")
        assert result == "hello world!"

    def test_expand_multiple_env_vars(self, monkeypatch):
        """Test multiple environment variables in same string."""
        monkeypatch.setenv("FIRST", "1")
        monkeypatch.setenv("SECOND", "2")
        result = expand_env_vars("${FIRST} and ${SECOND}")
        assert result == "1 and 2"

    def test_expand_env_vars_in_list(self, monkeypatch):
        """Test environment variable expansion in lists."""
        monkeypatch.setenv("CMD", "python")
        result = expand_env_vars(["${CMD}", "script.py"])
        assert result == ["python", "script.py"]

    def test_expand_env_vars_in_dict(self, monkeypatch):
        """Test environment variable expansion in dictionaries."""
        monkeypatch.setenv("PROJECT", "myproject")
        data = {
            "name": "${PROJECT}",
            "version": 1,
        }
        result = expand_env_vars(data)
        assert result["name"] == "myproject"
        assert result["version"] == 1

    def test_expand_nested_structures(self, monkeypatch):
        """Test environment variable expansion in nested structures."""
        monkeypatch.setenv("HOST", "localhost")
        monkeypatch.setenv("PORT", "8080")
        data = {
            "servers": [
                {"host": "${HOST}", "port": "${PORT}"},
            ],
        }
        result = expand_env_vars(data)
        assert result["servers"][0]["host"] == "localhost"
        assert result["servers"][0]["port"] == "8080"

    def test_unexpanded_var_without_default(self, monkeypatch):
        """Test that undefined vars without defaults stay as-is."""
        monkeypatch.delenv("UNDEFINED_VAR", raising=False)
        result = expand_env_vars("${UNDEFINED_VAR}")
        assert result == "${UNDEFINED_VAR}"

    def test_load_config_with_env_vars(self, tmp_path, monkeypatch):
        """Test loading configuration with environment variables."""
        monkeypatch.setenv("PROJECT_NAME", "env-test-project")
        config_path = tmp_path / "config.yaml"
        config_content = f"""
version: 1
project_name: ${{PROJECT_NAME}}
watchers:
  - name: test-watcher
    paths:
      - {tmp_path}
    commands:
      - name: test-cmd
        cmd: ["echo", "hello"]
"""
        config_path.write_text(config_content)

        config = ConfigValidator.load_config(config_path)
        assert config.project_name == "env-test-project"

    def test_load_config_without_env_expansion(self, tmp_path, monkeypatch):
        """Test loading configuration with env expansion disabled."""
        monkeypatch.setenv("PROJECT_NAME", "should-not-expand")
        config_path = tmp_path / "config.yaml"
        config_content = f"""
version: 1
project_name: "${{PROJECT_NAME}}"
watchers:
  - name: test-watcher
    paths:
      - {tmp_path}
    commands:
      - name: test-cmd
        cmd: ["echo", "hello"]
"""
        config_path.write_text(config_content)

        config = ConfigValidator.load_config(config_path, expand_env=False)
        assert config.project_name == "${PROJECT_NAME}"
