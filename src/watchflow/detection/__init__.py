"""Project and tool detection package."""

from watchflow.detection.detector import ProjectDetection, ProjectDetector
from watchflow.detection.tools import ToolDetector, ToolInfo

__all__ = ["ProjectDetection", "ProjectDetector", "ToolDetector", "ToolInfo"]
