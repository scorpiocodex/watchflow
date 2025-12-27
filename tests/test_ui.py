"""Tests for UI components."""

from rich.console import Console

from watchflow.detection import ProjectDetection
from watchflow.detection.tools import ToolInfo
from watchflow.ui import Icons, Themes, UIRenderer


class TestThemes:
    """Tests for theme system."""

    def test_get_pro_theme(self):
        """Test getting Pro theme."""
        theme = Themes.get_theme("pro")
        assert theme.name == "pro"
        assert theme.use_emoji
        assert theme.use_icons
        assert theme.use_panels
        assert theme.use_colors

    def test_get_minimal_theme(self):
        """Test getting Minimal theme."""
        theme = Themes.get_theme("minimal")
        assert theme.name == "minimal"
        assert not theme.use_emoji
        assert not theme.use_icons
        assert not theme.use_panels
        assert not theme.use_colors

    def test_get_neon_theme(self):
        """Test getting Neon theme."""
        theme = Themes.get_theme("neon")
        assert theme.name == "neon"
        assert theme.use_emoji
        assert theme.use_icons
        assert theme.use_panels
        assert theme.use_colors

    def test_get_auto_theme(self):
        """Test auto theme detection."""
        theme = Themes.get_theme("auto")
        assert theme.name in ["pro", "minimal"]

    def test_get_default_theme(self):
        """Test getting default theme for unknown name."""
        theme = Themes.get_theme("unknown")
        assert theme.name == "pro"


class TestIcons:
    """Tests for icon system."""

    def test_icons_with_emoji(self):
        """Test icons with emoji enabled."""
        theme = Themes.PRO
        icon = Icons.get("success", theme)
        assert icon == "✅"

    def test_icons_without_emoji(self):
        """Test icons with emoji disabled."""
        theme = Themes.MINIMAL
        icon = Icons.get("success", theme)
        assert icon == "[OK]"

    def test_unknown_icon_with_emoji(self):
        """Test unknown icon with emoji."""
        theme = Themes.PRO
        icon = Icons.get("unknown_icon", theme)
        assert icon == "•"

    def test_unknown_icon_without_emoji(self):
        """Test unknown icon without emoji."""
        theme = Themes.MINIMAL
        icon = Icons.get("unknown_icon", theme)
        assert icon == "*"


class TestUIRenderer:
    """Tests for UIRenderer."""

    def test_renderer_initialization(self):
        """Test renderer initialization."""
        renderer = UIRenderer(theme_name="pro")
        assert renderer.theme.name == "pro"
        assert isinstance(renderer.console, Console)

    def test_print_banner(self, capsys):
        """Test printing banner."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_banner("0.1.0")

        # Just ensure it doesn't crash
        # Actual output testing with Rich is complex

    def test_print_project_detection(self):
        """Test printing project detections."""
        renderer = UIRenderer(theme_name="minimal")
        detections = [
            ProjectDetection(
                language="python",
                confidence=0.9,
                detected_files=["pyproject.toml"],
                package_manager="poetry",
            ),
            ProjectDetection(
                language="nodejs",
                confidence=0.5,
                detected_files=["package.json"],
                package_manager="npm",
            ),
        ]

        renderer.print_project_detection(detections, selected="python")
        # Should not crash

    def test_print_tool_status(self):
        """Test printing tool status."""
        renderer = UIRenderer(theme_name="minimal")
        tools = [
            ToolInfo(name="python", available=True, version="3.11.0"),
            ToolInfo(name="black", available=False, install_hint="pip install black"),
        ]

        renderer.print_tool_status(tools)
        # Should not crash

    def test_print_file_event(self):
        """Test printing file event."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_file_event("modified", "test.py", "python-watcher")
        # Should not crash

    def test_print_command_success(self):
        """Test printing command success."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_command_success("test-command", 1.23)
        # Should not crash

    def test_print_command_error(self):
        """Test printing command error."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_command_error("test-command", 1.23, "Command failed")
        # Should not crash

    def test_print_command_skip(self):
        """Test printing command skip."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_command_skip("test-command", "no tests found", 0.0)
        # Should not crash

    def test_truncate_short_text(self):
        """Test truncating short text."""
        renderer = UIRenderer(theme_name="minimal")
        text = "short"
        truncated = renderer._truncate(text, 10)
        assert truncated == "short"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        renderer = UIRenderer(theme_name="minimal")
        text = "this is a very long text that needs truncation"
        truncated = renderer._truncate(text, 20)
        assert len(truncated) == 20
        assert truncated.endswith("...")

    def test_get_layout_mode_full(self):
        """Test layout mode detection for full width."""
        renderer = UIRenderer(theme_name="minimal")
        # Mock terminal width
        renderer.terminal_width = 100
        mode = renderer._get_layout_mode()
        assert mode == "full"

    def test_get_layout_mode_compact(self):
        """Test layout mode detection for compact width."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.terminal_width = 70
        mode = renderer._get_layout_mode()
        assert mode == "compact"

    def test_get_layout_mode_minimal(self):
        """Test layout mode detection for minimal width."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.terminal_width = 50
        mode = renderer._get_layout_mode()
        assert mode == "minimal"

    def test_print_validation_errors(self):
        """Test printing validation errors."""
        renderer = UIRenderer(theme_name="minimal")
        errors = [
            "Error 1: Invalid configuration",
            "Error 2: Missing required field",
        ]
        renderer.print_validation_errors(errors)
        # Should not crash

    def test_print_info(self):
        """Test printing info message."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_info("Test info message")
        # Should not crash

    def test_print_error(self):
        """Test printing error message."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_error("Test error message")
        # Should not crash

    def test_print_warning(self):
        """Test printing warning message."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_warning("Test warning message")
        # Should not crash

    def test_print_shutdown(self):
        """Test printing shutdown message."""
        renderer = UIRenderer(theme_name="minimal")
        renderer.print_shutdown()
        # Should not crash
