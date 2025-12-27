"""Tests for project detection."""

from watchflow.detection import ProjectDetector


class TestProjectDetector:
    """Tests for ProjectDetector."""

    def test_detect_python_pyproject(self, tmp_path):
        """Test detecting Python project with pyproject.toml."""
        (tmp_path / "pyproject.toml").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "python"
        assert primary.confidence > 0.6  # Adjusted for single file detection
        assert "pyproject.toml" in primary.detected_files

    def test_detect_python_requirements(self, tmp_path):
        """Test detecting Python project with requirements.txt."""
        (tmp_path / "requirements.txt").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "python"
        assert "requirements.txt" in primary.detected_files

    def test_detect_nodejs(self, tmp_path):
        """Test detecting Node.js project."""
        (tmp_path / "package.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "nodejs"
        assert "package.json" in primary.detected_files

    def test_detect_go(self, tmp_path):
        """Test detecting Go project."""
        (tmp_path / "go.mod").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "go"
        assert "go.mod" in primary.detected_files

    def test_detect_rust(self, tmp_path):
        """Test detecting Rust project."""
        (tmp_path / "Cargo.toml").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "rust"
        assert "Cargo.toml" in primary.detected_files

    def test_detect_java_maven(self, tmp_path):
        """Test detecting Java project with Maven."""
        (tmp_path / "pom.xml").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "java"
        assert "pom.xml" in primary.detected_files

    def test_detect_java_gradle(self, tmp_path):
        """Test detecting Java project with Gradle."""
        (tmp_path / "build.gradle").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "java"
        assert "build.gradle" in primary.detected_files

    def test_detect_ruby(self, tmp_path):
        """Test detecting Ruby project."""
        (tmp_path / "Gemfile").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "ruby"
        assert "Gemfile" in primary.detected_files

    def test_detect_php(self, tmp_path):
        """Test detecting PHP project."""
        (tmp_path / "composer.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.language == "php"
        assert "composer.json" in primary.detected_files

    def test_detect_multiple_languages(self, tmp_path):
        """Test detecting multiple languages."""
        (tmp_path / "package.json").touch()
        (tmp_path / "requirements.txt").touch()

        detector = ProjectDetector(tmp_path)
        detections = detector.detect_all()

        assert len(detections) == 2
        languages = [d.language for d in detections]
        assert "nodejs" in languages
        assert "python" in languages

    def test_detect_nothing(self, tmp_path):
        """Test detecting no project."""
        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is None

    def test_detect_all_empty(self, tmp_path):
        """Test detect_all with no projects."""
        detector = ProjectDetector(tmp_path)
        detections = detector.detect_all()

        assert len(detections) == 0

    def test_confidence_ordering(self, tmp_path):
        """Test that detections are ordered by confidence."""
        # Python with multiple indicators
        (tmp_path / "pyproject.toml").touch()
        (tmp_path / "poetry.lock").touch()
        (tmp_path / "requirements.txt").touch()

        # Node.js with single indicator
        (tmp_path / "package.json").touch()

        detector = ProjectDetector(tmp_path)
        detections = detector.detect_all()

        # Python should have higher confidence
        assert detections[0].language == "python"
        assert detections[1].language == "nodejs"
        assert detections[0].confidence > detections[1].confidence

    def test_detect_poetry(self, tmp_path):
        """Test detecting Poetry as package manager."""
        (tmp_path / "poetry.lock").touch()
        (tmp_path / "pyproject.toml").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.package_manager == "poetry"

    def test_detect_npm(self, tmp_path):
        """Test detecting npm as package manager."""
        (tmp_path / "package-lock.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.package_manager == "npm"

    def test_detect_yarn(self, tmp_path):
        """Test detecting Yarn as package manager."""
        (tmp_path / "yarn.lock").touch()
        (tmp_path / "package.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.package_manager == "yarn"

    def test_detect_pnpm(self, tmp_path):
        """Test detecting pnpm as package manager."""
        (tmp_path / "pnpm-lock.yaml").touch()
        (tmp_path / "package.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.package_manager == "pnpm"

    def test_detect_test_framework_pytest(self, tmp_path):
        """Test detecting pytest."""
        (tmp_path / "pytest.ini").touch()
        (tmp_path / "pyproject.toml").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.test_framework == "pytest"

    def test_detect_test_framework_jest(self, tmp_path):
        """Test detecting Jest."""
        (tmp_path / "jest.config.js").touch()
        (tmp_path / "package.json").touch()

        detector = ProjectDetector(tmp_path)
        primary = detector.detect_primary()

        assert primary is not None
        assert primary.test_framework == "jest"
