"""Main WatchFlow engine."""

import asyncio
import signal
from pathlib import Path
from typing import Any, Optional

from watchflow.config.models import Config, Watcher
from watchflow.config.validator import ConfigValidator
from watchflow.core.executor import CommandExecutor, ExecutionResult
from watchflow.core.watcher import FileWatcher, compute_file_hash
from watchflow.ui.renderer import UIRenderer
from watchflow.utils.logger import get_logger
from watchflow.utils.templates import TemplateEngine

logger = get_logger(__name__)


class WatchFlowEngine:
    """Main orchestration engine for WatchFlow."""

    def __init__(
        self,
        config: Config,
        project_root: Path,
        ui_renderer: UIRenderer,
        config_path: Optional[Path] = None,
        enable_hot_reload: bool = True,
    ):
        """Initialize engine.

        Args:
            config: Configuration
            project_root: Project root directory
            ui_renderer: UI renderer
            config_path: Path to configuration file (for hot-reload)
            enable_hot_reload: Whether to enable hot-reload of configuration
        """
        self.config = config
        self.project_root = project_root
        self.ui_renderer = ui_renderer
        self.config_path = config_path
        self.enable_hot_reload = enable_hot_reload

        self.executor = CommandExecutor(
            max_parallel=config.global_config.max_parallel_commands
        )
        self.watcher = FileWatcher()

        self.running = False
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self._config_hash: Optional[str] = None
        self._reload_lock = asyncio.Lock()

    async def start(self) -> None:
        """Start the engine."""
        self.running = True
        self.loop = asyncio.get_event_loop()

        # Setup signal handlers
        self._setup_signal_handlers()

        # Initialize watchers
        self._initialize_watchers()

        # Set event loop for watcher
        self.watcher.set_event_loop(self.loop)

        # Store initial config hash for hot-reload
        if self.config_path and self.enable_hot_reload:
            self._config_hash = compute_file_hash(str(self.config_path))

        # Start file watching
        self.watcher.start()

        # Print start message
        self.ui_renderer.print_watching_start(self.config)

        try:
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(0.1)
                # Check for config changes periodically
                if self.config_path and self.enable_hot_reload:
                    await self._check_config_reload()
        except asyncio.CancelledError:
            logger.debug("engine_cancelled")
        finally:
            await self.stop()

    async def _check_config_reload(self) -> None:
        """Check if configuration has changed and reload if needed."""
        if not self.config_path or not self._config_hash:
            return

        new_hash = compute_file_hash(str(self.config_path))
        if new_hash is None or new_hash == self._config_hash:
            return

        # Config has changed, try to reload
        async with self._reload_lock:
            try:
                new_config = ConfigValidator.load_config(self.config_path)

                # Update config
                self.config = new_config
                self._config_hash = new_hash

                # Recreate executor with new settings
                self.executor = CommandExecutor(
                    max_parallel=new_config.global_config.max_parallel_commands
                )

                # Notify user
                self.ui_renderer.print_info("Configuration reloaded successfully")
                logger.info("config_reloaded", path=str(self.config_path))

            except Exception as e:
                self.ui_renderer.print_warning(f"Failed to reload config: {e}")
                logger.error("config_reload_failed", error=str(e))

    async def stop(self) -> None:
        """Stop the engine gracefully."""
        if not self.running:
            return

        self.running = False
        logger.info("engine_stopping")

        # Stop file watcher
        try:
            self.watcher.stop()
        except RuntimeError as e:
            logger.error("watcher_stop_error", error=str(e))

        logger.info("engine_stopped")

    def _initialize_watchers(self) -> None:
        """Initialize all watchers from configuration."""
        for watcher_config in self.config.watchers:
            self.watcher.add_watcher(
                watcher_config=watcher_config,
                callback=self._on_file_event,
                project_root=self.project_root,
            )

    def _on_file_event(
        self, event_type: str, paths: list[str], watcher_name: str
    ) -> None:
        """Handle file system events.

        Args:
            event_type: Type of event
            paths: Affected paths
            watcher_name: Name of watcher that detected event
        """
        if not self.running:
            return

        # Find the watcher configuration
        watcher_config = None
        for watcher in self.config.watchers:
            if watcher.name == watcher_name:
                watcher_config = watcher
                break

        if not watcher_config:
            logger.error("watcher_not_found", watcher=watcher_name)
            return

        # Print file event
        self.ui_renderer.print_file_event(
            event_type=event_type,
            path=paths[0] if paths else "unknown",
            watcher_name=watcher_name,
        )

        # Create template context
        template_vars = TemplateEngine.create_context(
            path=paths[0] if paths else "",
            paths=paths,
            event=event_type,
            watcher_name=watcher_name,
        )

        # Execute commands
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self._execute_watcher_commands(watcher_config, template_vars),
                self.loop,
            )

    async def _execute_watcher_commands(
        self, watcher_config: Watcher, template_vars: dict[str, Any]
    ) -> None:
        """Execute commands for a watcher.

        Args:
            watcher_config: Watcher configuration
            template_vars: Template variables
        """
        # Execute commands
        results = await self.executor.execute_commands(
            commands=watcher_config.commands,
            template_vars=template_vars,
            project_root=self.project_root,
            parallel=watcher_config.parallel,
        )

        # Print results
        for result in results:
            self._print_execution_result(result)

            # Check fail_fast
            if self.config.global_config.fail_fast and not result.success:
                logger.info("fail_fast_triggered", command=result.command_name)
                self.ui_renderer.print_error(
                    f"Fail-fast triggered by {result.command_name}"
                )
                await self.stop()
                break

    def _print_execution_result(self, result: ExecutionResult) -> None:
        """Print execution result.

        Args:
            result: Execution result
        """
        if result.skipped:
            self.ui_renderer.print_command_skip(
                command_name=result.command_name,
                reason=result.skip_reason or "unknown",
                duration=result.duration,
            )
        elif result.success:
            self.ui_renderer.print_command_success(
                command_name=result.command_name,
                duration=result.duration,
            )
        else:
            error_msg = None
            if result.stderr:
                # Show first line of stderr only (compact mode)
                first_line = result.stderr.strip().split("\n")[0]
                # Truncate if too long
                if len(first_line) > 100:
                    error_msg = first_line[:97] + "..."
                else:
                    error_msg = first_line
            elif result.stdout:
                # If no stderr, check stdout for errors
                first_line = result.stdout.strip().split("\n")[0]
                if len(first_line) > 100:
                    error_msg = first_line[:97] + "..."
                else:
                    error_msg = first_line

            self.ui_renderer.print_command_error(
                command_name=result.command_name,
                duration=result.duration,
                error=error_msg,
            )

    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""

        def signal_handler(signum: int, _: Any) -> None:
            """Handle shutdown signals."""
            logger.info("signal_received", signal=signum)
            self.ui_renderer.print_shutdown()

            if self.loop and self.running:
                # Schedule stop in the event loop
                self.loop.create_task(self.stop())

        # Handle SIGINT (Ctrl+C) and SIGTERM
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
