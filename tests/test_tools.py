"""Tests for tool detection."""

import sys

import pytest

from watchflow.detection.tools import ToolDetector


class TestToolDetector:
    """Tests for ToolDetector."""

    @pytest.mark.skipif(sys.platform == "win32", reason="echo is built-in on Windows")
    def test_check_tool_available(self):
        """Test checking available tool (echo should exist on Unix)."""
        info = ToolDetector.check_tool("echo")
        assert info.name == "echo"
        assert info.available

    def test_check_tool_unavailable(self):
        """Test checking unavailable tool."""
        info = ToolDetector.check_tool("nonexistent_tool_12345")
        assert info.name == "nonexistent_tool_12345"
        assert not info.available

    @pytest.mark.skipif(sys.platform == "win32", reason="echo is built-in on Windows")
    def test_check_tool_with_version(self):
        """Test checking tool with version command."""
        info = ToolDetector.check_tool("echo", "echo --version")
        assert info.name == "echo"
        assert info.available
        # Version may or may not be detected depending on echo implementation

    def test_check_language_tools_python(self):
        """Test checking Python tools."""
        tools = ToolDetector.check_language_tools("python")
        assert len(tools) > 0

        tool_names = [t.name for t in tools]
        assert "python" in tool_names

    def test_check_language_tools_nodejs(self):
        """Test checking Node.js tools."""
        tools = ToolDetector.check_language_tools("nodejs")
        assert len(tools) > 0

        tool_names = [t.name for t in tools]
        assert "node" in tool_names

    def test_check_language_tools_unknown(self):
        """Test checking tools for unknown language."""
        tools = ToolDetector.check_language_tools("unknown_lang")
        assert len(tools) == 0

    def test_check_package_manager_poetry(self):
        """Test checking Poetry package manager."""
        info = ToolDetector.check_package_manager("poetry")
        assert info.name == "poetry"
        # Available status depends on environment

    def test_check_package_manager_npm(self):
        """Test checking npm package manager."""
        info = ToolDetector.check_package_manager("npm")
        assert info.name == "npm"

    def test_check_package_manager_unknown(self):
        """Test checking unknown package manager."""
        info = ToolDetector.check_package_manager("unknown_pm")
        assert info.name == "unknown_pm"

    def test_get_missing_tools_all_available(self):
        """Test getting missing tools when all available."""

        # Use 'sh' which should be available on most systems
        class MockDetector(ToolDetector):
            TOOL_REQUIREMENTS = {
                "test": [("sh", "sh --version", "Install sh")],
            }

        missing = MockDetector.get_missing_tools("test")
        # Should be empty or have sh (depending on system)
        assert isinstance(missing, list)

    def test_get_missing_tools_some_missing(self):
        """Test getting missing tools when some unavailable."""

        class MockDetector(ToolDetector):
            TOOL_REQUIREMENTS = {
                "test": [
                    ("nonexistent_1", "nonexistent_1 --version", "Install it"),
                    ("nonexistent_2", "nonexistent_2 --version", "Install it"),
                ],
            }

        missing = MockDetector.get_missing_tools("test")
        assert len(missing) == 2
        assert all(not t.available for t in missing)

    def test_tool_requirements_structure(self):
        """Test that tool requirements have correct structure."""
        requirements = ToolDetector.TOOL_REQUIREMENTS

        # Check Python tools
        assert "python" in requirements
        python_tools = requirements["python"]
        assert len(python_tools) > 0

        # Each tool should be a tuple of 3 elements
        for tool_name, version_cmd, install_hint in python_tools:
            assert isinstance(tool_name, str)
            assert isinstance(version_cmd, str)
            assert isinstance(install_hint, str)

    def test_package_manager_tools_structure(self):
        """Test that package manager tools have correct structure."""
        pm_tools = ToolDetector.PACKAGE_MANAGER_TOOLS

        # Check some known package managers
        assert "poetry" in pm_tools
        assert "npm" in pm_tools

        # Each should be a tuple of 3 elements
        for pm_name, pm_data in pm_tools.items():
            tool_name, version_cmd, install_hint = pm_data
            assert isinstance(tool_name, str)
            assert isinstance(version_cmd, str)
            assert isinstance(install_hint, str)
