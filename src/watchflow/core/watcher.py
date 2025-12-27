"""File system watching engine."""

import asyncio
import fnmatch
from pathlib import Path
from typing import Callable, Optional

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from watchflow.config.models import Watcher as WatcherConfig
from watchflow.utils.logger import get_logger

logger = get_logger(__name__)


class WatcherEventHandler(FileSystemEventHandler):
    """Handles file system events from watchdog."""

    def __init__(
        self,
        watcher_config: WatcherConfig,
        callback: Callable[[str, list[str], str], None],
        debounce_ms: int = 100,
    ):
        """Initialize event handler.

        Args:
            watcher_config: Watcher configuration
            callback: Callback function(event_type, paths, watcher_name)
            debounce_ms: Debounce time in milliseconds
        """
        super().__init__()
        self.watcher_config = watcher_config
        self.callback = callback
        self.debounce_ms = debounce_ms
        self.pending_events: dict[str, float] = {}
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set the event loop for async operations.

        Args:
            loop: Asyncio event loop
        """
        self.event_loop = loop

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle any file system event.

        Args:
            event: File system event from watchdog
        """
        if event.is_directory:
            return

        path = event.src_path

        # Ensure path is a string
        if isinstance(path, bytes):
            path = path.decode("utf-8")

        # Apply pattern matching
        if not self._should_process(path):
            return

        # Debounce events
        import time

        current_time = time.time()
        if path in self.pending_events:
            last_time = self.pending_events[path]
            if (current_time - last_time) * 1000 < self.debounce_ms:
                return

        self.pending_events[path] = current_time

        # Determine event type
        event_type = "unknown"
        if hasattr(event, "event_type"):
            event_type = str(event.event_type)

        logger.debug(
            "file_event",
            watcher=self.watcher_config.name,
            event_type=event_type,
            path=path,
        )

        # Schedule callback in event loop
        if self.event_loop:
            asyncio.run_coroutine_threadsafe(
                self._async_callback(event_type, [path]),
                self.event_loop,
            )

    async def _async_callback(self, event_type: str, paths: list[str]) -> None:
        """Async wrapper for callback.

        Args:
            event_type: Type of event
            paths: List of affected paths
        """
        self.callback(event_type, paths, self.watcher_config.name)

    def _should_process(self, path: str) -> bool:
        """Check if path should be processed based on patterns.

        Args:
            path: File path

        Returns:
            True if should process, False otherwise
        """
        path_obj = Path(path)
        filename = path_obj.name

        # Check ignore patterns first
        if self.watcher_config.ignore_patterns:
            for pattern in self.watcher_config.ignore_patterns:
                if fnmatch.fnmatch(filename, pattern) or pattern in path:
                    return False

        # Check include patterns
        if self.watcher_config.patterns:
            for pattern in self.watcher_config.patterns:
                if fnmatch.fnmatch(filename, pattern):
                    return True
            return False  # No pattern matched

        # No patterns specified, process all
        return True


class FileWatcher:
    """Manages file system watching."""

    def __init__(self):
        """Initialize file watcher."""
        self.observer = Observer()
        self.handlers: list[WatcherEventHandler] = []
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None

    def add_watcher(
        self,
        watcher_config: WatcherConfig,
        callback: Callable[[str, list[str], str], None],
        project_root: Path,
    ) -> None:
        """Add a watcher for paths.

        Args:
            watcher_config: Watcher configuration
            callback: Callback function for events
            project_root: Project root directory
        """
        handler = WatcherEventHandler(
            watcher_config=watcher_config,
            callback=callback,
            debounce_ms=watcher_config.debounce,
        )

        if self.event_loop:
            handler.set_event_loop(self.event_loop)

        self.handlers.append(handler)

        # Schedule watches for each path
        for path_str in watcher_config.paths:
            path = project_root / path_str
            if not path.exists():
                logger.warning(
                    "watch_path_not_found",
                    watcher=watcher_config.name,
                    path=str(path),
                )
                continue

            self.observer.schedule(
                handler,
                str(path),
                recursive=watcher_config.recursive,
            )

            logger.debug(
                "watcher_added",
                watcher=watcher_config.name,
                path=str(path),
                recursive=watcher_config.recursive,
            )

    def set_event_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """Set event loop for all handlers.

        Args:
            loop: Asyncio event loop
        """
        self.event_loop = loop
        for handler in self.handlers:
            handler.set_event_loop(loop)

    def start(self) -> None:
        """Start watching."""
        self.observer.start()
        logger.info("file_watcher_started")

    def stop(self) -> None:
        """Stop watching."""
        self.observer.stop()
        self.observer.join(timeout=5)
        logger.info("file_watcher_stopped")
