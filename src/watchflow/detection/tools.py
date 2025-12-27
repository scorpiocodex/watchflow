"""Tool detection and validation."""

import shutil
from dataclasses import dataclass
from typing import Optional


@dataclass
class ToolInfo:
    """Tool information."""

    name: str
    available: bool
    version: Optional[str] = None
    install_hint: Optional[str] = None


class ToolDetector:
    """Detects and validates development tools."""

    TOOL_REQUIREMENTS = {
        "python": [
            ("python", "python --version", "Install from python.org"),
            ("pip", "pip --version", "Install from python.org"),
        ],
        "nodejs": [
            ("node", "node --version", "Install from nodejs.org"),
            ("npm", "npm --version", "Included with Node.js"),
        ],
        "go": [
            ("go", "go version", "Install from go.dev"),
        ],
        "rust": [
            ("cargo", "cargo --version", "Install from rustup.rs"),
            ("rustc", "rustc --version", "Install from rustup.rs"),
        ],
        "java": [
            ("java", "java -version", "Install JDK from adoptium.net"),
            ("javac", "javac -version", "Install JDK from adoptium.net"),
        ],
        "ruby": [
            ("ruby", "ruby --version", "Install from ruby-lang.org"),
            ("gem", "gem --version", "Included with Ruby"),
        ],
        "php": [
            ("php", "php --version", "Install from php.net"),
        ],
    }

    PACKAGE_MANAGER_TOOLS = {
        "poetry": ("poetry", "poetry --version", "pip install poetry"),
        "uv": ("uv", "uv --version", "pip install uv"),
        "pipenv": ("pipenv", "pipenv --version", "pip install pipenv"),
        "pnpm": ("pnpm", "pnpm --version", "npm install -g pnpm"),
        "yarn": ("yarn", "yarn --version", "npm install -g yarn"),
        "npm": ("npm", "npm --version", "Included with Node.js"),
        "bundler": ("bundle", "bundle --version", "gem install bundler"),
        "composer": ("composer", "composer --version", "Install from getcomposer.org"),
        "maven": ("mvn", "mvn --version", "Install from maven.apache.org"),
        "gradle": ("gradle", "gradle --version", "Install from gradle.org"),
    }

    @staticmethod
    def check_tool(tool_name: str, version_cmd: Optional[str] = None) -> ToolInfo:
        """Check if a tool is available.

        Args:
            tool_name: Name of the tool
            version_cmd: Command to check version (optional)

        Returns:
            ToolInfo with availability and version
        """
        available = shutil.which(tool_name) is not None
        version = None

        if available and version_cmd:
            import subprocess

            try:
                result = subprocess.run(
                    version_cmd.split(),
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    # Extract version from output (first line usually)
                    version = result.stdout.strip().split("\n")[0]
            except (subprocess.SubprocessError, OSError):
                pass

        return ToolInfo(name=tool_name, available=available, version=version)

    @classmethod
    def check_language_tools(cls, language: str) -> list[ToolInfo]:
        """Check all tools required for a language.

        Args:
            language: Programming language

        Returns:
            List of ToolInfo for required tools
        """
        tools = cls.TOOL_REQUIREMENTS.get(language, [])
        results: list[ToolInfo] = []

        for tool_name, version_cmd, install_hint in tools:
            info = cls.check_tool(tool_name, version_cmd)
            info.install_hint = install_hint
            results.append(info)

        return results

    @classmethod
    def check_package_manager(cls, package_manager: str) -> ToolInfo:
        """Check if package manager is available.

        Args:
            package_manager: Package manager name

        Returns:
            ToolInfo for the package manager
        """
        if package_manager in cls.PACKAGE_MANAGER_TOOLS:
            tool_name, version_cmd, install_hint = cls.PACKAGE_MANAGER_TOOLS[
                package_manager
            ]
            info = cls.check_tool(tool_name, version_cmd)
            info.install_hint = install_hint
            return info

        # Fallback for unknown package managers
        return ToolInfo(
            name=package_manager,
            available=shutil.which(package_manager) is not None,
        )

    @classmethod
    def get_missing_tools(
        cls, language: str, package_manager: Optional[str] = None
    ) -> list[ToolInfo]:
        """Get list of missing tools for a language.

        Args:
            language: Programming language
            package_manager: Optional package manager

        Returns:
            List of missing ToolInfo
        """
        missing: list[ToolInfo] = []

        # Check language tools
        for tool in cls.check_language_tools(language):
            if not tool.available:
                missing.append(tool)

        # Check package manager
        if package_manager:
            pm_info = cls.check_package_manager(package_manager)
            if not pm_info.available:
                missing.append(pm_info)

        return missing
