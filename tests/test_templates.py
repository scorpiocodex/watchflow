"""Tests for template engine."""

from watchflow.utils.templates import CONFIG_TEMPLATES, TemplateEngine


class TestTemplateEngine:
    """Tests for TemplateEngine."""

    def test_substitute_single_variable(self):
        """Test substituting a single variable."""
        template = "Hello {{name}}"
        variables = {"name": "World"}

        result = TemplateEngine.substitute(template, variables)
        assert result == "Hello World"

    def test_substitute_multiple_variables(self):
        """Test substituting multiple variables."""
        template = "{{greeting}} {{name}}, you have {{count}} messages"
        variables = {
            "greeting": "Hello",
            "name": "Alice",
            "count": 5,
        }

        result = TemplateEngine.substitute(template, variables)
        assert result == "Hello Alice, you have 5 messages"

    def test_substitute_missing_variable(self):
        """Test substituting with missing variable."""
        template = "Hello {{name}}"
        variables = {}

        result = TemplateEngine.substitute(template, variables)
        # Should leave placeholder unchanged
        assert result == "Hello {{name}}"

    def test_substitute_no_variables(self):
        """Test substituting template without variables."""
        template = "Hello World"
        variables = {"name": "Alice"}

        result = TemplateEngine.substitute(template, variables)
        assert result == "Hello World"

    def test_substitute_empty_string(self):
        """Test substituting empty string."""
        template = ""
        variables = {"name": "Alice"}

        result = TemplateEngine.substitute(template, variables)
        assert result == ""

    def test_substitute_list(self):
        """Test substituting list of templates."""
        templates = ["Hello {{name}}", "Goodbye {{name}}"]
        variables = {"name": "World"}

        results = TemplateEngine.substitute_list(templates, variables)
        assert results == ["Hello World", "Goodbye World"]

    def test_create_context(self):
        """Test creating template context."""
        context = TemplateEngine.create_context(
            path="/path/to/file.py",
            paths=["/path/to/file.py", "/path/to/other.py"],
            event="modified",
            watcher_name="test-watcher",
        )

        assert context["path"] == "/path/to/file.py"
        assert context["paths"] == "/path/to/file.py /path/to/other.py"
        assert context["event"] == "modified"
        assert context["watcher"] == "test-watcher"
        assert "timestamp" in context

    def test_substitute_with_path(self):
        """Test path substitution in command."""
        template = "python process.py {{path}}"
        variables = {"path": "data.txt"}

        result = TemplateEngine.substitute(template, variables)
        assert result == "python process.py data.txt"

    def test_substitute_with_paths(self):
        """Test paths substitution in command."""
        template = "./batch.sh {{paths}}"
        variables = {"paths": "file1.txt file2.txt file3.txt"}

        result = TemplateEngine.substitute(template, variables)
        assert result == "./batch.sh file1.txt file2.txt file3.txt"

    def test_substitute_with_event(self):
        """Test event substitution."""
        template = "echo File {{event}}: {{path}}"
        variables = {"event": "created", "path": "new.txt"}

        result = TemplateEngine.substitute(template, variables)
        assert result == "echo File created: new.txt"


class TestConfigTemplates:
    """Tests for config templates."""

    def test_python_template_exists(self):
        """Test Python template exists."""
        assert "python" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["python"]
        assert "watchers:" in CONFIG_TEMPLATES["python"]

    def test_nodejs_template_exists(self):
        """Test Node.js template exists."""
        assert "nodejs" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["nodejs"]

    def test_go_template_exists(self):
        """Test Go template exists."""
        assert "go" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["go"]

    def test_rust_template_exists(self):
        """Test Rust template exists."""
        assert "rust" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["rust"]

    def test_java_template_exists(self):
        """Test Java template exists."""
        assert "java" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["java"]

    def test_ruby_template_exists(self):
        """Test Ruby template exists."""
        assert "ruby" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["ruby"]

    def test_php_template_exists(self):
        """Test PHP template exists."""
        assert "php" in CONFIG_TEMPLATES
        assert "version: 1" in CONFIG_TEMPLATES["php"]

    def test_template_substitution(self):
        """Test template can be substituted."""
        template = CONFIG_TEMPLATES["python"]
        variables = {
            "project_name": '"test-project"',
            "format_cmd": '"black", "."',
            "lint_cmd": '"ruff", "check", "."',
            "test_cmd": '"pytest"',
        }

        result = TemplateEngine.substitute(template, variables)
        assert "test-project" in result
        assert "black" in result
        assert "ruff" in result
        assert "pytest" in result
