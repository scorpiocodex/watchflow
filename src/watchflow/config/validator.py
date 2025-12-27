"""Configuration validation utilities."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from watchflow.config.models import Config


class ConfigValidator:
    """Validates WatchFlow configuration files."""

    @staticmethod
    def load_config(config_path: Path) -> Config:
        """Load and validate configuration from file.

        Args:
            config_path: Path to configuration file

        Returns:
            Validated Config object

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
            yaml.YAMLError: If YAML is malformed
        """
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}") from e

        if not data:
            raise ValueError("Config file is empty")

        try:
            return Config(**data)
        except ValidationError as e:
            raise ValueError(f"Invalid configuration: {e}") from e

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
