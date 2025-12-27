"""Project type detection."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ProjectDetection:
    """Project detection result."""

    language: str
    confidence: float
    detected_files: list[str]
    package_manager: Optional[str] = None
    test_framework: Optional[str] = None


class ProjectDetector:
    """Detects project types and package managers."""

    # Detection patterns: (language, files, confidence_boost)
    DETECTION_PATTERNS = {
        "python": [
            (["pyproject.toml"], 1.0),
            (["setup.py"], 0.9),
            (["requirements.txt"], 0.7),
            (["Pipfile"], 0.8),
            (["poetry.lock"], 1.0),
            (["setup.cfg"], 0.8),
            ([".python-version"], 0.6),
        ],
        "nodejs": [
            (["package.json"], 1.0),
            (["package-lock.json"], 0.9),
            (["yarn.lock"], 0.9),
            (["pnpm-lock.yaml"], 0.9),
            (["node_modules"], 0.5),
            ([".nvmrc"], 0.6),
        ],
        "go": [
            (["go.mod"], 1.0),
            (["go.sum"], 0.9),
            (["Gopkg.toml"], 0.8),
            (["Gopkg.lock"], 0.8),
        ],
        "rust": [
            (["Cargo.toml"], 1.0),
            (["Cargo.lock"], 0.9),
        ],
        "java": [
            (["pom.xml"], 1.0),
            (["build.gradle"], 1.0),
            (["build.gradle.kts"], 1.0),
            (["settings.gradle"], 0.8),
            (["gradlew"], 0.7),
        ],
        "ruby": [
            (["Gemfile"], 1.0),
            (["Gemfile.lock"], 0.9),
            ([".ruby-version"], 0.7),
            (["Rakefile"], 0.6),
        ],
        "php": [
            (["composer.json"], 1.0),
            (["composer.lock"], 0.9),
            (["artisan"], 0.7),
        ],
    }

    PACKAGE_MANAGERS = {
        "python": {
            "poetry": ["poetry.lock", "pyproject.toml"],
            "uv": ["uv.lock"],
            "pip": ["requirements.txt"],
            "pipenv": ["Pipfile"],
        },
        "nodejs": {
            "pnpm": ["pnpm-lock.yaml"],
            "yarn": ["yarn.lock"],
            "npm": ["package-lock.json"],
        },
        "go": {
            "go": ["go.mod"],
        },
        "rust": {
            "cargo": ["Cargo.toml"],
        },
        "java": {
            "maven": ["pom.xml"],
            "gradle": ["build.gradle", "build.gradle.kts"],
        },
        "ruby": {
            "bundler": ["Gemfile"],
        },
        "php": {
            "composer": ["composer.json"],
        },
    }

    def __init__(self, project_path: Path):
        """Initialize detector.

        Args:
            project_path: Path to project directory
        """
        self.project_path = project_path

    def detect_all(self) -> list[ProjectDetection]:
        """Detect all project types in directory.

        Returns:
            List of detected projects, sorted by confidence
        """
        detections: list[ProjectDetection] = []

        for language, patterns in self.DETECTION_PATTERNS.items():
            confidence = 0.0
            detected_files: list[str] = []

            for files, boost in patterns:
                for file in files:
                    if (self.project_path / file).exists():
                        confidence += boost
                        detected_files.append(file)

            if confidence > 0:
                # Normalize confidence to 0-1 range (more generous scoring)
                normalized_confidence = min(confidence / 1.5, 1.0)

                package_manager = self._detect_package_manager(language)
                test_framework = self._detect_test_framework(language)

                detections.append(
                    ProjectDetection(
                        language=language,
                        confidence=normalized_confidence,
                        detected_files=detected_files,
                        package_manager=package_manager,
                        test_framework=test_framework,
                    )
                )

        # Sort by confidence descending
        detections.sort(key=lambda x: x.confidence, reverse=True)
        return detections

    def detect_primary(self) -> Optional[ProjectDetection]:
        """Detect primary project type.

        Returns:
            Highest confidence detection, or None if nothing detected
        """
        detections = self.detect_all()
        return detections[0] if detections else None

    def _detect_package_manager(self, language: str) -> Optional[str]:
        """Detect package manager for language.

        Args:
            language: Project language

        Returns:
            Package manager name or None
        """
        managers = self.PACKAGE_MANAGERS.get(language, {})

        for manager, files in managers.items():
            for file in files:
                if (self.project_path / file).exists():
                    return manager

        return None

    def _detect_test_framework(self, language: str) -> Optional[str]:
        """Detect test framework for language.

        Args:
            language: Project language

        Returns:
            Test framework name or None
        """
        test_patterns = {
            "python": [
                ("pytest", ["pytest.ini", "pyproject.toml"]),
                ("unittest", ["test_*.py", "tests/"]),
            ],
            "nodejs": [
                ("jest", ["jest.config.js", "jest.config.ts"]),
                ("vitest", ["vitest.config.ts"]),
                ("mocha", [".mocharc.json"]),
            ],
            "go": [
                ("go test", ["*_test.go"]),
            ],
            "rust": [
                ("cargo test", ["tests/"]),
            ],
            "java": [
                ("junit", ["src/test/"]),
            ],
            "ruby": [
                ("rspec", [".rspec", "spec/"]),
            ],
            "php": [
                ("phpunit", ["phpunit.xml"]),
            ],
        }

        frameworks = test_patterns.get(language, [])

        for framework, files in frameworks:
            for file in files:
                path = self.project_path / file
                if path.exists() or list(self.project_path.glob(file)):
                    return framework

        return None
