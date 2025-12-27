"""UI rendering for WatchFlow."""

import shutil
from datetime import datetime
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from watchflow.config.models import Config
from watchflow.detection.detector import ProjectDetection
from watchflow.detection.tools import ToolInfo
from watchflow.ui.themes import Icons, Themes


class UIRenderer:
    """Renders UI elements for WatchFlow."""

    def __init__(self, theme_name: str = "pro"):
        """Initialize renderer.

        Args:
            theme_name: Name of theme to use
        """
        self.theme = Themes.get_theme(theme_name)
        self.console = Console(theme=self.theme.rich_theme)
        self.terminal_width = shutil.get_terminal_size().columns

    def _get_layout_mode(self) -> str:
        """Determine layout mode based on terminal width.

        Returns:
            Layout mode: 'full', 'compact', or 'minimal'
        """
        if self.terminal_width >= 80:
            return "full"
        elif self.terminal_width >= 60:
            return "compact"
        else:
            return "minimal"

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text intelligently.

        Args:
            text: Text to truncate
            max_length: Maximum length

        Returns:
            Truncated text with ellipsis if needed
        """
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    def print_banner(self, version: str) -> None:
        """Print WatchFlow banner.

        Args:
            version: Version string
        """
        icon = Icons.get("watch", self.theme)
        title = f"{icon} WatchFlow v{version}"

        if self.theme.use_panels:
            panel = Panel(
                Text(title, style="title", justify="center"),
                subtitle="Watch. React. Automate.",
                border_style="cyan",
            )
            self.console.print(panel)
        else:
            self.console.print(f"\n{title}\n", style="title")

    def print_project_detection(
        self, detections: list[ProjectDetection], selected: Optional[str] = None
    ) -> None:
        """Print detected projects.

        Args:
            detections: List of project detections
            selected: Selected project type (if any)
        """
        if not detections:
            self.console.print(
                f"{Icons.get('warning', self.theme)} No projects detected",
                style="warning",
            )
            return

        icon = Icons.get("info", self.theme)
        self.console.print(f"\n{icon} Detected Projects:\n", style="info")

        table = Table(show_header=True, header_style="bold")
        table.add_column("Language", style="cyan")
        table.add_column("Confidence", justify="right")
        table.add_column("Package Manager")
        table.add_column("Files", style="dim")

        for detection in detections:
            confidence_str = f"{detection.confidence * 100:.0f}%"
            pm = detection.package_manager or "-"
            files = ", ".join(detection.detected_files[:3])
            if len(detection.detected_files) > 3:
                files += f" (+{len(detection.detected_files) - 3})"

            style = "bold green" if detection.language == selected else ""
            table.add_row(detection.language, confidence_str, pm, files, style=style)

        self.console.print(table)

    def print_tool_status(self, tools: list[ToolInfo]) -> None:
        """Print tool availability status.

        Args:
            tools: List of tool information
        """
        if not tools:
            return

        icon = Icons.get("gear", self.theme)
        self.console.print(f"\n{icon} Required Tools:\n", style="info")

        for tool in tools:
            if tool.available:
                status_icon = Icons.get("check", self.theme)
                version = f" ({tool.version})" if tool.version else ""
                self.console.print(
                    f"  {status_icon} {tool.name}{version}", style="success"
                )
            else:
                status_icon = Icons.get("cross", self.theme)
                self.console.print(f"  {status_icon} {tool.name}", style="error")
                if tool.install_hint:
                    self.console.print(
                        f"     {Icons.get('arrow', self.theme)} {tool.install_hint}",
                        style="dim",
                    )

    def print_config_created(self, config_path: str) -> None:
        """Print configuration created message.

        Args:
            config_path: Path to created config
        """
        icon = Icons.get("success", self.theme)
        self.console.print(
            f"\n{icon} Configuration created: {config_path}", style="success"
        )

    def print_watching_start(self, config: Config) -> None:
        """Print watching start message.

        Args:
            config: Configuration being watched
        """
        icon = Icons.get("rocket", self.theme)
        project_name = config.project_name or "project"
        self.console.print(
            f"\n{icon} Starting WatchFlow for {project_name}...\n", style="info"
        )

        # Show watchers
        for watcher in config.watchers:
            watcher_icon = Icons.get("watch", self.theme)
            self.console.print(
                f"  {watcher_icon} {watcher.name}: {len(watcher.commands)} command(s)",
                style="watcher",
            )

    def print_file_event(self, event_type: str, path: str, watcher_name: str) -> None:
        """Print file system event.

        Args:
            event_type: Type of event (modified, created, etc.)
            path: Path that changed
            watcher_name: Name of watcher that triggered
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = Icons.get("file", self.theme)

        layout = self._get_layout_mode()

        if layout == "minimal":
            # Minimal: just essential info
            path_short = self._truncate(path, 30)
            self.console.print(f"{timestamp} {event_type}: {path_short}")
        elif layout == "compact":
            # Compact: no watcher name
            path_short = self._truncate(path, 40)
            self.console.print(
                f"{icon} [{timestamp}] {event_type}: [path]{path_short}[/]",
                style="info",
            )
        else:
            # Full: all details
            self.console.print(
                f"{icon} [{timestamp}] [watcher]{watcher_name}[/]: {event_type} [path]{path}[/]"
            )

    def print_command_start(self, command_name: str) -> None:
        """Print command start message.

        Args:
            command_name: Name of command
        """
        icon = Icons.get("play", self.theme)
        self.console.print(f"  {icon} Running: [command]{command_name}[/]")

    def print_command_success(self, command_name: str, duration: float) -> None:
        """Print command success message.

        Args:
            command_name: Name of command
            duration: Execution duration in seconds
        """
        icon = Icons.get("success", self.theme)
        self.console.print(
            f"  {icon} [success]SUCCESS[/] {command_name} ({duration:.2f}s)"
        )

    def print_command_error(
        self, command_name: str, duration: float, error: Optional[str] = None
    ) -> None:
        """Print command error message.

        Args:
            command_name: Name of command
            duration: Execution duration in seconds
            error: Error message
        """
        icon = Icons.get("error", self.theme)
        self.console.print(
            f"  {icon} [error]FAILED[/] {command_name} ({duration:.2f}s)"
        )
        if error:
            self.console.print(f"     {error}", style="dim red")

    def print_command_skip(
        self, command_name: str, reason: str, duration: float = 0.0
    ) -> None:
        """Print command skip message.

        Args:
            command_name: Name of command
            reason: Reason for skip
            duration: Execution duration in seconds
        """
        icon = Icons.get("skip", self.theme)
        self.console.print(
            f"  {icon} [warning]SKIPPED[/] {command_name} ({duration:.2f}s)"
        )
        self.console.print(f"     Reason: {reason}", style="dim yellow")

    def print_validation_errors(self, errors: list[str]) -> None:
        """Print configuration validation errors.

        Args:
            errors: List of error messages
        """
        icon = Icons.get("error", self.theme)
        self.console.print(
            f"\n{icon} Configuration validation failed:\n", style="error"
        )

        for error in errors:
            self.console.print(
                f"  {Icons.get('bullet', self.theme)} {error}", style="error"
            )

    def print_info(self, message: str) -> None:
        """Print info message.

        Args:
            message: Message to print
        """
        icon = Icons.get("info", self.theme)
        self.console.print(f"{icon} {message}", style="info")

    def print_error(self, message: str) -> None:
        """Print error message.

        Args:
            message: Message to print
        """
        icon = Icons.get("error", self.theme)
        self.console.print(f"{icon} {message}", style="error")

    def print_warning(self, message: str) -> None:
        """Print warning message.

        Args:
            message: Message to print
        """
        icon = Icons.get("warning", self.theme)
        self.console.print(f"{icon} {message}", style="warning")

    def print_shutdown(self) -> None:
        """Print shutdown message."""
        icon = Icons.get("stop", self.theme)
        self.console.print(f"\n{icon} Shutting down gracefully...", style="warning")
