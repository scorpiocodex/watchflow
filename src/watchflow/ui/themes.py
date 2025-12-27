"""UI themes for WatchFlow."""

import os
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.theme import Theme as RichTheme


@dataclass
class ThemeConfig:
    """Theme configuration."""

    name: str
    use_emoji: bool
    use_icons: bool
    use_panels: bool
    use_colors: bool
    rich_theme: RichTheme


class Themes:
    """Theme definitions for WatchFlow."""

    PRO = ThemeConfig(
        name="pro",
        use_emoji=True,
        use_icons=True,
        use_panels=True,
        use_colors=True,
        rich_theme=RichTheme(
            {
                "success": "bold green",
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold blue",
                "debug": "dim white",
                "title": "bold cyan",
                "subtitle": "italic cyan",
                "command": "bold magenta",
                "path": "bold blue",
                "timestamp": "dim cyan",
                "watcher": "bold yellow",
            }
        ),
    )

    MINIMAL = ThemeConfig(
        name="minimal",
        use_emoji=False,
        use_icons=False,
        use_panels=False,
        use_colors=False,
        rich_theme=RichTheme(
            {
                "success": "white",
                "error": "white",
                "warning": "white",
                "info": "white",
                "debug": "white",
                "title": "bold white",
                "subtitle": "white",
                "command": "white",
                "path": "white",
                "timestamp": "white",
                "watcher": "white",
            }
        ),
    )

    NEON = ThemeConfig(
        name="neon",
        use_emoji=True,
        use_icons=True,
        use_panels=True,
        use_colors=True,
        rich_theme=RichTheme(
            {
                "success": "bold bright_green",
                "error": "bold bright_red",
                "warning": "bold bright_yellow",
                "info": "bold bright_cyan",
                "debug": "dim bright_white",
                "title": "bold bright_magenta",
                "subtitle": "italic bright_magenta",
                "command": "bold bright_cyan",
                "path": "bold bright_blue",
                "timestamp": "bright_white",
                "watcher": "bold bright_yellow",
            }
        ),
    )

    @classmethod
    def get_theme(cls, theme_name: str) -> ThemeConfig:
        """Get theme by name.

        Args:
            theme_name: Name of theme (pro, minimal, neon, auto)

        Returns:
            ThemeConfig for the requested theme
        """
        if theme_name == "auto":
            return cls._detect_theme()

        themes = {
            "pro": cls.PRO,
            "minimal": cls.MINIMAL,
            "neon": cls.NEON,
        }

        return themes.get(theme_name.lower(), cls.PRO)

    @classmethod
    def _detect_theme(cls) -> ThemeConfig:
        """Auto-detect appropriate theme based on terminal capabilities.

        Returns:
            ThemeConfig based on detection
        """
        # Check if running in CI/CD
        ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "CIRCLECI", "TRAVIS"]
        if any(os.getenv(var) for var in ci_vars):
            return cls.MINIMAL

        # Check if output is redirected
        if not sys.stdout.isatty():
            return cls.MINIMAL

        # Check terminal capabilities
        console = Console()

        # No color support
        if not console.color_system:
            return cls.MINIMAL

        # Check for emoji support (rough heuristic)
        term = os.getenv("TERM", "")
        if "xterm" in term or "screen" in term or "tmux" in term:
            # Modern terminals usually support emoji
            return cls.PRO

        # Default to minimal if unsure
        return cls.MINIMAL


class Icons:
    """Icon definitions for different themes."""

    @staticmethod
    def get(name: str, theme: ThemeConfig) -> str:
        """Get icon for theme.

        Args:
            name: Icon name
            theme: Theme configuration

        Returns:
            Icon string or ASCII fallback
        """
        if theme.use_emoji:
            emoji_icons = {
                "watch": "👁️",
                "success": "✅",
                "error": "❌",
                "warning": "⚠️",
                "info": "ℹ️",
                "rocket": "🚀",
                "gear": "⚙️",
                "folder": "📁",
                "file": "📄",
                "code": "💻",
                "time": "⏱️",
                "skip": "⏭️",
                "play": "▶️",
                "stop": "⏹️",
                "check": "✓",
                "cross": "✗",
                "arrow": "→",
                "bullet": "•",
            }
            return emoji_icons.get(name, "•")

        # ASCII fallback
        ascii_icons = {
            "watch": "[W]",
            "success": "[OK]",
            "error": "[ERR]",
            "warning": "[WARN]",
            "info": "[INFO]",
            "rocket": "[*]",
            "gear": "[*]",
            "folder": "[D]",
            "file": "[F]",
            "code": "[C]",
            "time": "[T]",
            "skip": "[SKIP]",
            "play": "[>]",
            "stop": "[#]",
            "check": "[+]",
            "cross": "[-]",
            "arrow": "->",
            "bullet": "*",
        }
        return ascii_icons.get(name, "*")
