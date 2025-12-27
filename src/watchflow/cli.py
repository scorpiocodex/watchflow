"""CLI interface for WatchFlow."""

import asyncio
import platform
from pathlib import Path
from typing import Optional

import typer
from rich.prompt import Confirm, Prompt

from watchflow import __version__
from watchflow.config import ConfigValidator, UITheme
from watchflow.core.engine import WatchFlowEngine
from watchflow.detection import ProjectDetector, ToolDetector
from watchflow.ui.renderer import UIRenderer
from watchflow.utils.logger import setup_logging
from watchflow.utils.templates import CONFIG_TEMPLATES, TemplateEngine

app = typer.Typer(
    name="watchflow",
    help="Next-Generation Intelligent File Watcher & Automation CLI",
    add_completion=False,
)


@app.command()
def init(
    project_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Project type (python, nodejs, go, rust, java, ruby, php)",
    ),
    no_check_tools: bool = typer.Option(
        False,
        "--no-check-tools",
        help="Skip tool availability checking",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing configuration",
    ),
) -> None:
    """Initialize WatchFlow configuration for your project.

    Automatically detects project type and generates optimized configuration.
    """
    ui = UIRenderer(theme_name="pro")
    ui.print_banner(__version__)

    project_root = Path.cwd()
    config_path = project_root / "watchflow.yaml"

    # Check if config already exists
    if config_path.exists() and not force:
        ui.print_error(f"Configuration already exists: {config_path}")
        ui.print_info("Use --force to overwrite")
        raise typer.Exit(1)

    # Detect projects
    detector = ProjectDetector(project_root)
    detections = detector.detect_all()

    if not detections and not project_type:
        ui.print_error("No project detected. Use --type to specify manually.")
        raise typer.Exit(1)

    # Handle project selection
    selected_detection = None

    if project_type:
        # User specified type
        project_type = project_type.lower()
        if project_type not in CONFIG_TEMPLATES:
            ui.print_error(f"Unknown project type: {project_type}")
            raise typer.Exit(1)

        # Find matching detection or create minimal one
        for detection in detections:
            if detection.language == project_type:
                selected_detection = detection
                break

    elif len(detections) == 1:
        # Single detection, use it
        selected_detection = detections[0]
        ui.print_project_detection(detections, selected=selected_detection.language)

    else:
        # Multiple detections, let user choose
        ui.print_project_detection(detections)
        ui.print_info("\nMultiple project types detected.")

        # Create choices
        choices = [d.language for d in detections]
        default = detections[0].language

        language = Prompt.ask(
            "Select project type",
            choices=choices,
            default=default,
        )

        for detection in detections:
            if detection.language == language:
                selected_detection = detection
                break

    if not selected_detection:
        ui.print_error("Could not determine project type")
        raise typer.Exit(1)

    language = selected_detection.language
    package_manager = selected_detection.package_manager

    # Check tools
    if not no_check_tools:
        missing_tools = ToolDetector.get_missing_tools(language, package_manager)

        if missing_tools:
            ui.print_tool_status(missing_tools)
            ui.print_warning(
                "\nSome required tools are missing. Install them before running WatchFlow."
            )

            if not Confirm.ask("Continue anyway?", default=True):
                raise typer.Exit(1)
        else:
            # Show all tools as available
            all_tools = ToolDetector.check_language_tools(language)
            if package_manager:
                all_tools.append(ToolDetector.check_package_manager(package_manager))
            ui.print_tool_status(all_tools)

    # Generate configuration
    project_name = project_root.name
    config_content = _generate_config(
        language=language,
        project_name=project_name,
        package_manager=package_manager,
    )

    # Save configuration
    config_path.write_text(config_content, encoding="utf-8")
    ui.print_config_created(str(config_path))

    ui.print_info("\n✨ Next steps:")
    ui.print_info(f"  1. Review and customize {config_path}")
    ui.print_info("  2. Run: watchflow run")


@app.command()
def run(
    config_file: Path = typer.Option(
        Path("watchflow.yaml"),
        "--config",
        "-c",
        help="Path to configuration file",
    ),
    theme: str = typer.Option(
        "pro",
        "--theme",
        help="UI theme (pro, minimal, neon, auto)",
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging",
    ),
    no_show_tools: bool = typer.Option(
        False,
        "--no-show-tools",
        help="Don't show tool status on startup",
    ),
) -> None:
    """Start watching files and executing commands.

    Monitors your project files and automatically runs configured commands
    when changes are detected.
    """
    # Setup logging
    log_level = "DEBUG" if debug else "INFO"
    setup_logging(level=log_level)

    # Load configuration
    try:
        config = ConfigValidator.load_config(config_file)
    except FileNotFoundError:
        print(f"Error: Configuration file not found: {config_file}")
        print("Run 'watchflow init' to create one.")
        raise typer.Exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        raise typer.Exit(1)

    # Override theme if specified
    if theme:
        try:
            config.global_config.theme = UITheme(theme)
        except ValueError:
            print(f"Error: Invalid theme: {theme}")
            raise typer.Exit(1)

    # Create UI renderer
    ui = UIRenderer(theme_name=config.global_config.theme.value)
    ui.print_banner(__version__)

    # Show tool status
    if not no_show_tools and config.project_type:
        tools = ToolDetector.check_language_tools(config.project_type)
        if tools:
            ui.print_tool_status(tools)

    # Create and start engine
    project_root = config_file.parent if config_file.parent != Path() else Path.cwd()
    engine = WatchFlowEngine(
        config=config,
        project_root=project_root,
        ui_renderer=ui,
    )

    # Run engine
    try:
        asyncio.run(engine.start())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        ui.print_error(f"Fatal error: {e}")
        if debug:
            raise
        raise typer.Exit(1)


@app.command()
def validate(
    config_file: Path = typer.Argument(
        Path("watchflow.yaml"),
        help="Path to configuration file",
    )
) -> None:
    """Validate configuration file.

    Checks your WatchFlow configuration for errors and provides
    detailed feedback on any issues.
    """
    ui = UIRenderer(theme_name="pro")

    if not config_file.exists():
        ui.print_error(f"Configuration file not found: {config_file}")
        raise typer.Exit(1)

    try:
        config = ConfigValidator.load_config(config_file)
        ui.print_info(f"✅ Configuration is valid: {config_file}")
        ui.print_info(f"   Project: {config.project_name or 'unnamed'}")
        ui.print_info(f"   Watchers: {len(config.watchers)}")

        total_commands = sum(len(w.commands) for w in config.watchers)
        ui.print_info(f"   Commands: {total_commands}")

    except ValueError as e:
        ui.print_error("Configuration validation failed:")
        error_lines = str(e).split("\n")
        for line in error_lines:
            if line.strip():
                ui.print_error(f"  • {line}")
        raise typer.Exit(1)


@app.command()
def info() -> None:
    """Display system and environment information.

    Shows details about your system, Python environment, and
    WatchFlow installation.
    """
    ui = UIRenderer(theme_name="pro")
    ui.print_banner(__version__)

    from rich.table import Table

    table = Table(title="System Information", show_header=False)
    table.add_column("Property", style="cyan")
    table.add_column("Value")

    table.add_row("WatchFlow Version", __version__)
    table.add_row("Python Version", platform.python_version())
    table.add_row("Platform", platform.platform())
    table.add_row("Architecture", platform.machine())
    table.add_row("Working Directory", str(Path.cwd()))

    ui.console.print(table)


def _generate_config(
    language: str,
    project_name: str,
    package_manager: Optional[str],
) -> str:
    """Generate configuration content.

    Args:
        language: Project language
        project_name: Project name
        package_manager: Package manager (if any)

    Returns:
        Configuration content as string
    """
    template = CONFIG_TEMPLATES.get(language, CONFIG_TEMPLATES["python"])

    # Determine commands based on language and package manager
    variables = {
        "project_name": f'"{project_name}"',
        "package_manager": package_manager or "npm",
    }

    # Language-specific defaults with proper YAML list formatting
    if language == "python":
        variables["format_cmd"] = '"black", "."'
        variables["lint_cmd"] = '"ruff", "check", "."'
        variables["test_cmd"] = '"pytest"'
    elif language == "java":
        build_cmd = "mvn" if package_manager == "maven" else "gradle"
        variables["build_cmd"] = f'"{build_cmd}"'

    return TemplateEngine.substitute(template, variables)


if __name__ == "__main__":
    app()
