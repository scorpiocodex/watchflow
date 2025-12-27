"""Test utilities for cross-platform command execution."""

import sys


def get_echo_command(text: str) -> list[str]:
    """Get platform-specific echo command.

    Args:
        text: Text to echo

    Returns:
        Command list
    """
    if sys.platform == "win32":
        return ["cmd", "/c", "echo", text]
    else:
        return ["echo", text]


def get_sleep_command(seconds: int) -> list[str]:
    """Get platform-specific sleep command.

    Args:
        seconds: Seconds to sleep

    Returns:
        Command list
    """
    if sys.platform == "win32":
        # Windows: use ping command as a sleep alternative (more reliable than timeout)
        # ping localhost with count n takes approximately n seconds
        return ["cmd", "/c", "ping", "127.0.0.1", "-n", str(seconds + 1), ">", "nul"]
    else:
        return ["sleep", str(seconds)]


def get_pwd_command() -> list[str]:
    """Get platform-specific print working directory command.

    Returns:
        Command list
    """
    if sys.platform == "win32":
        # Use echo %CD% to print current directory on Windows
        return ["cmd", "/c", "echo", "%CD%"]
    else:
        return ["pwd"]


def get_false_command() -> list[str]:
    """Get platform-specific command that always fails.

    Returns:
        Command list
    """
    if sys.platform == "win32":
        return ["cmd", "/c", "exit", "1"]
    else:
        return ["false"]


def get_true_command() -> list[str]:
    """Get platform-specific command that always succeeds.

    Returns:
        Command list
    """
    if sys.platform == "win32":
        return ["cmd", "/c", "exit", "0"]
    else:
        return ["true"]
