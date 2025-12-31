"""UI themes for WatchFlow."""

import os
import sys
from dataclasses import dataclass

from rich.console import Console
from rich.theme import Theme as RichTheme


def _can_display_emoji() -> bool:
    """Check if the terminal can display emoji.

    Returns:
        True if emoji can be displayed, False otherwise
    """
    # On Windows, check if we're using Windows Terminal or a modern console
    if sys.platform == "win32":
        # Windows Terminal sets WT_SESSION
        if os.getenv("WT_SESSION"):
            return True
        # VS Code terminal
        if os.getenv("TERM_PROGRAM") == "vscode":
            return True
        # ConEmu/Cmder
        if os.getenv("ConEmuANSI") == "ON":
            return True
        # Default Windows console doesn't support emoji well
        return False

    # On Unix-like systems, check TERM
    term = os.getenv("TERM", "")
    if "xterm" in term or "screen" in term or "tmux" in term or "256color" in term:
        return True

    # Check if stdout is a TTY
    if not sys.stdout.isatty():
        return False

    return True


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

        theme = themes.get(theme_name.lower(), cls.PRO)

        # If the selected theme uses emoji but terminal doesn't support it,
        # return a version with emoji disabled
        if theme.use_emoji and not _can_display_emoji():
            return ThemeConfig(
                name=theme.name,
                use_emoji=False,
                use_icons=theme.use_icons,
                use_panels=theme.use_panels,
                use_colors=theme.use_colors,
                rich_theme=theme.rich_theme,
            )

        return theme

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

        # Check for emoji support
        if _can_display_emoji():
            return cls.PRO

        # Return PRO theme but with emoji disabled for Windows legacy console
        return cls._get_safe_pro_theme()

    @classmethod
    def _get_safe_pro_theme(cls) -> ThemeConfig:
        """Get PRO theme with emoji disabled for terminals that don't support it.

        Returns:
            ThemeConfig with colors but no emoji
        """
        return ThemeConfig(
            name="pro",
            use_emoji=False,  # Disable emoji for compatibility
            use_icons=True,
            use_panels=True,
            use_colors=True,
            rich_theme=cls.PRO.rich_theme,
        )


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
