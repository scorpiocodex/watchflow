"""Template variable substitution."""

import re
from datetime import datetime
from typing import Any


class TemplateEngine:
    """Handles template variable substitution in commands."""

    VARIABLE_PATTERN = re.compile(r"\{\{(\w+)\}\}")

    @classmethod
    def substitute(
        cls,
        template: str,
        variables: dict[str, Any],
    ) -> str:
        """Substitute template variables.

        Args:
            template: Template string with {{variable}} placeholders
            variables: Dictionary of variable values

        Returns:
            String with variables substituted
        """

        def replacer(match: re.Match[str]) -> str:
            var_name = match.group(1)
            value = variables.get(var_name, match.group(0))
            return str(value)

        return cls.VARIABLE_PATTERN.sub(replacer, template)

    @classmethod
    def substitute_list(
        cls,
        templates: list[str],
        variables: dict[str, Any],
    ) -> list[str]:
        """Substitute template variables in a list of strings.

        Args:
            templates: List of template strings
            variables: Dictionary of variable values

        Returns:
            List with variables substituted
        """
        return [cls.substitute(template, variables) for template in templates]

    @staticmethod
    def create_context(
        path: str,
        paths: list[str],
        event: str,
        watcher_name: str,
    ) -> dict[str, Any]:
        """Create template variable context.

        Args:
            path: Primary changed path
            paths: List of all changed paths
            event: Event type (modified, created, etc.)
            watcher_name: Name of watcher

        Returns:
            Dictionary of template variables
        """
        return {
            "path": path,
            "paths": " ".join(paths),
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "watcher": watcher_name,
        }


# Config templates for different languages
CONFIG_TEMPLATES = {
    "python": """version: 1
project_name: {{project_name}}
project_type: python

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: python-watcher
    paths:
      - .
    recursive: true
    patterns:
      - "*.py"
    ignore_patterns:
      - "__pycache__"
      - "*.pyc"
      - ".venv"
      - "venv"
      - ".git"
    debounce: 100
    commands:
      - name: format-code
        cmd: [{{format_cmd}}]
        timeout: 30
        retries: 0

      - name: run-linter
        cmd: [{{lint_cmd}}]
        timeout: 60
        retries: 1
        retry_strategy: fixed

      - name: run-tests
        cmd: [{{test_cmd}}]
        timeout: 300
        retries: 0
""",
    "nodejs": """version: 1
project_name: "{project_name}"
project_type: nodejs

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: nodejs-watcher
    paths:
      - src
      - lib
    recursive: true
    patterns:
      - "*.js"
      - "*.ts"
      - "*.jsx"
      - "*.tsx"
    ignore_patterns:
      - "node_modules"
      - "dist"
      - "build"
      - ".git"
    debounce: 100
    commands:
      - name: run-linter
        cmd: ["{package_manager}", "run", "lint"]
        timeout: 60
        retries: 1

      - name: run-tests
        cmd: ["{package_manager}", "test"]
        timeout: 300
        retries: 0
""",
    "go": """version: 1
project_name: "{project_name}"
project_type: go

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: go-watcher
    paths:
      - .
    recursive: true
    patterns:
      - "*.go"
    ignore_patterns:
      - "vendor"
      - ".git"
    debounce: 100
    commands:
      - name: format-code
        cmd: ["go", "fmt", "./..."]
        timeout: 30
        retries: 0

      - name: run-tests
        cmd: ["go", "test", "./..."]
        timeout: 300
        retries: 0
""",
    "rust": """version: 1
project_name: "{project_name}"
project_type: rust

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: rust-watcher
    paths:
      - src
    recursive: true
    patterns:
      - "*.rs"
    ignore_patterns:
      - "target"
      - ".git"
    debounce: 100
    commands:
      - name: check-code
        cmd: ["cargo", "check"]
        timeout: 60
        retries: 0

      - name: run-tests
        cmd: ["cargo", "test"]
        timeout: 300
        retries: 0
""",
    "java": """version: 1
project_name: "{project_name}"
project_type: java

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: java-watcher
    paths:
      - src
    recursive: true
    patterns:
      - "*.java"
    ignore_patterns:
      - "target"
      - "build"
      - ".git"
    debounce: 100
    commands:
      - name: compile-code
        cmd: ["{build_cmd}", "compile"]
        timeout: 120
        retries: 0

      - name: run-tests
        cmd: ["{build_cmd}", "test"]
        timeout: 300
        retries: 0
""",
    "ruby": """version: 1
project_name: "{project_name}"
project_type: ruby

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: ruby-watcher
    paths:
      - lib
      - app
    recursive: true
    patterns:
      - "*.rb"
    ignore_patterns:
      - ".git"
    debounce: 100
    commands:
      - name: run-linter
        cmd: ["bundle", "exec", "rubocop"]
        timeout: 60
        retries: 0

      - name: run-tests
        cmd: ["bundle", "exec", "rspec"]
        timeout: 300
        retries: 0
""",
    "php": """version: 1
project_name: "{project_name}"
project_type: php

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: php-watcher
    paths:
      - src
      - app
    recursive: true
    patterns:
      - "*.php"
    ignore_patterns:
      - "vendor"
      - ".git"
    debounce: 100
    commands:
      - name: run-linter
        cmd: ["composer", "lint"]
        timeout: 60
        retries: 0

      - name: run-tests
        cmd: ["composer", "test"]
        timeout: 300
        retries: 0
""",
}
