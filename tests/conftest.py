"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path():
    """Provide a temporary directory path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_config_dict(tmp_path):
    """Provide a sample configuration dictionary."""
    return {
        "version": 1,
        "project_name": "test-project",
        "project_type": "python",
        "global": {
            "theme": "pro",
            "fail_fast": False,
            "max_parallel_commands": 4,
        },
        "watchers": [
            {
                "name": "test-watcher",
                "paths": [str(tmp_path)],
                "recursive": True,
                "patterns": ["*.py"],
                "debounce": 100,
                "commands": [
                    {
                        "name": "test-command",
                        "cmd": ["echo", "test"],
                        "timeout": 30,
                    }
                ],
            }
        ],
    }


@pytest.fixture
def sample_config_yaml(tmp_path):
    """Provide sample configuration YAML content."""
    return f"""version: 1
project_name: test-project
project_type: python

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: test-watcher
    paths:
      - {tmp_path}
    recursive: true
    patterns:
      - "*.py"
    debounce: 100
    commands:
      - name: test-command
        cmd: ["echo", "test"]
        timeout: 30
"""
