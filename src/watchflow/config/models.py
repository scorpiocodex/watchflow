"""Configuration models for WatchFlow."""

from enum import Enum
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class RetryStrategy(str, Enum):
    """Retry strategy types."""

    FIXED = "fixed"
    EXPONENTIAL = "exponential"


class UITheme(str, Enum):
    """UI theme types."""

    PRO = "pro"
    MINIMAL = "minimal"
    NEON = "neon"
    AUTO = "auto"


class Command(BaseModel):
    """Command configuration."""

    name: str = Field(..., description="Command name")
    cmd: list[str] = Field(..., description="Command to execute")
    timeout: Optional[int] = Field(None, ge=1, description="Timeout in seconds")
    retries: int = Field(0, ge=0, le=10, description="Number of retries")
    retry_strategy: RetryStrategy = Field(
        RetryStrategy.FIXED, description="Retry strategy"
    )
    working_dir: Optional[str] = Field(None, description="Working directory")
    skip_until_exists: Optional[str] = Field(None, description="Skip until path exists")
    only_if_changed: Optional[list[str]] = Field(
        None, description="Only run if these patterns changed"
    )

    @field_validator("cmd")
    @classmethod
    def validate_cmd(cls, v: list[str]) -> list[str]:
        """Validate command is not empty."""
        if not v or not any(v):
            raise ValueError("Command cannot be empty")
        return v

    @field_validator("working_dir")
    @classmethod
    def validate_working_dir(cls, v: Optional[str]) -> Optional[str]:
        """Validate working directory exists if specified."""
        if v is not None and not Path(v).exists():
            raise ValueError(f"Working directory does not exist: {v}")
        return v


class Watcher(BaseModel):
    """Watcher configuration."""

    name: str = Field(..., description="Watcher name")
    paths: list[str] = Field(..., description="Paths to watch")
    recursive: bool = Field(True, description="Watch recursively")
    patterns: Optional[list[str]] = Field(None, description="Include patterns")
    ignore_patterns: Optional[list[str]] = Field(None, description="Ignore patterns")
    debounce: int = Field(100, ge=0, le=60000, description="Debounce in milliseconds")
    commands: list[Command] = Field(..., description="Commands to execute")
    parallel: bool = Field(False, description="Execute commands in parallel")

    @field_validator("paths")
    @classmethod
    def validate_paths(cls, v: list[str]) -> list[str]:
        """Validate paths exist."""
        if not v:
            raise ValueError("At least one path is required")
        for path in v:
            if not Path(path).exists():
                raise ValueError(f"Path does not exist: {path}")
        return v

    @field_validator("commands")
    @classmethod
    def validate_commands(cls, v: list[Command]) -> list[Command]:
        """Validate at least one command exists."""
        if not v:
            raise ValueError("At least one command is required")
        return v


class GlobalConfig(BaseModel):
    """Global configuration."""

    theme: UITheme = Field(UITheme.PRO, description="UI theme")
    fail_fast: bool = Field(False, description="Stop on first error")
    max_parallel_commands: int = Field(
        4, ge=1, le=32, description="Max parallel commands"
    )
    log_level: str = Field("INFO", description="Logging level")

    model_config = {"extra": "forbid"}


class Config(BaseModel):
    """Root configuration."""

    version: Literal[1] = Field(1, description="Config version")
    project_name: Optional[str] = Field(None, description="Project name")
    project_type: Optional[str] = Field(None, description="Project type")
    global_config: GlobalConfig = Field(
        default_factory=GlobalConfig,  # type: ignore[arg-type]
        description="Global configuration",
        alias="global",
    )
    watchers: list[Watcher] = Field(..., description="Watchers")

    @field_validator("watchers")
    @classmethod
    def validate_watchers(cls, v: list[Watcher]) -> list[Watcher]:
        """Validate at least one watcher exists."""
        if not v:
            raise ValueError("At least one watcher is required")
        return v

    @model_validator(mode="before")
    @classmethod
    def handle_global_alias(cls, data: Any) -> Any:
        """Handle 'global' field alias."""
        if isinstance(data, dict) and "global" in data:
            data["global_config"] = data.pop("global")
        return data

    model_config = {"populate_by_name": True}
