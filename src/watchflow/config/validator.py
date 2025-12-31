"""Configuration validation utilities."""

import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from watchflow.config.models import Config
from watchflow.exceptions import (
    ConfigNotFoundError,
    ConfigSyntaxError,
    ConfigValidationError,
)


# Pattern for environment variable expansion: ${VAR} or ${VAR:-default}
ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?::-([^}]*))?\}")


def expand_env_vars(value: Any) -> Any:
    """Recursively expand environment variables in configuration values.

    Supports ${VAR} and ${VAR:-default} syntax.

    Args:
        value: Configuration value (string, list, or dict)

    Returns:
        Value with environment variables expanded
    """
    if isinstance(value, str):

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            default = match.group(2)
            env_value = os.environ.get(var_name)
            if env_value is not None:
                return env_value
            if default is not None:
                return default
            return match.group(0)  # Keep original if no match and no default

        return ENV_VAR_PATTERN.sub(replacer, value)
    elif isinstance(value, list):
        return [expand_env_vars(item) for item in value]
    elif isinstance(value, dict):
        return {k: expand_env_vars(v) for k, v in value.items()}
    return value


class ConfigValidator:
    """Validates WatchFlow configuration files."""

    @staticmethod
    def load_config(config_path: Path, expand_env: bool = True) -> Config:
        """Load and validate configuration from file.

        Args:
            config_path: Path to configuration file
            expand_env: Whether to expand environment variables (default: True)

        Returns:
            Validated Config object

        Raises:
            ConfigNotFoundError: If config file doesn't exist
            ConfigSyntaxError: If YAML is malformed
            ConfigValidationError: If config is invalid
        """
        if not config_path.exists():
            raise ConfigNotFoundError(str(config_path))

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            # Try to extract line number from YAML error
            line = None
            if hasattr(e, "problem_mark") and e.problem_mark:
                line = e.problem_mark.line + 1
            raise ConfigSyntaxError(str(e), line=line) from e

        if not data:
            raise ConfigValidationError(
                ["Configuration file is empty"], path=str(config_path)
            )

        # Expand environment variables if enabled
        if expand_env:
            data = expand_env_vars(data)

        try:
            return Config(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                loc = " -> ".join(str(loc_part) for loc_part in error["loc"])
                msg = error["msg"]
                errors.append(f"{loc}: {msg}")
            raise ConfigValidationError(errors, path=str(config_path)) from e

    @staticmethod
    def save_config(config: Config, config_path: Path) -> None:
        """Save configuration to file.

        Args:
            config: Config object to save
            config_path: Path to save configuration
        """
        # Convert to dict and handle aliases, converting enums to strings
        data = config.model_dump(by_alias=False, exclude_none=True, mode="json")

        # Rename global_config to global for output
        if "global_config" in data:
            data["global"] = data.pop("global_config")

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    @staticmethod
    def validate_config_dict(data: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate configuration dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        try:
            Config(**data)
            return True, []
        except ValidationError as e:
            errors = []
            for error in e.errors():
                loc = " -> ".join(str(loc_part) for loc_part in error["loc"])
                msg = error["msg"]
                errors.append(f"{loc}: {msg}")
            return False, errors
