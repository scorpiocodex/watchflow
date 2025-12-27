# Contributing to WatchFlow

Thank you for your interest in contributing to WatchFlow! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git
- pip

### Setup Steps

1. **Fork and clone the repository**

```bash
git clone https://github.com/scorpiocodex/watchflow.git
cd watchflow
```

1. **Create a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

1. **Install development dependencies**

```bash
make dev
```

1. **Verify installation**

```bash
make test
make lint
```

## Development Workflow

### Making Changes

#### **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

#### **Make your changes**

- Write clear, concise code
- Follow existing code style
- Add docstrings to functions and classes
- Update type hints

#### **Add tests**

```bash
# Add tests in tests/ directory
# Run tests
make test
```

#### **Format and lint your code**

```bash
make format
make lint
```

#### **Commit your changes**

```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit messages:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Build/tooling changes

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_detector.py

# Run specific test
pytest tests/test_detector.py::test_detect_python
```

### Code Quality

```bash
# Format code with Black
make format

# Run linters
make lint

# Type check with mypy
mypy src/watchflow
```

## Project Structure

```bash
watchflow/
├── src/watchflow/          # Source code
│   ├── cli.py             # CLI interface
│   ├── core/              # Core engine
│   ├── config/            # Configuration
│   ├── detection/         # Project detection
│   ├── ui/                # UI rendering
│   └── utils/             # Utilities
├── tests/                 # Test suite
├── examples/              # Example configs
├── docs/                  # Documentation
└── Makefile              # Development tasks
```

## Coding Standards

### Python Style

- **PEP 8** compliance via Black
- **Type hints** on all functions
- **Docstrings** in Google style
- **Max line length**: 100 characters

### Example Function

```python
def process_file(path: Path, options: dict[str, Any]) -> Result:
    """Process a file with given options.
    
    Args:
        path: Path to file to process
        options: Processing options
        
    Returns:
        Result object with status and data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If options are invalid
    """
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    # Implementation
    return Result(success=True, data=data)
```

### Testing Standards

- **91%+ coverage** required
- Test both success and failure cases
- Use descriptive test names
- Mock external dependencies
- Use pytest fixtures

### Example Test

```python
class TestProjectDetector:
    """Tests for ProjectDetector."""
    
    def test_detect_python_project(self, tmp_path):
        """Test detecting Python project with pyproject.toml."""
        (tmp_path / "pyproject.toml").touch()
        
        detector = ProjectDetector(tmp_path)
        result = detector.detect_primary()
        
        assert result is not None
        assert result.language == "python"
        assert result.confidence > 0.8
```

## Adding New Features

### Adding a New Language

1. Update `ProjectDetector.DETECTION_PATTERNS`
2. Update `ProjectDetector.PACKAGE_MANAGERS`
3. Add tool requirements in `ToolDetector.TOOL_REQUIREMENTS`
4. Create config template in `utils/templates.py`
5. Add tests
6. Update documentation

### Adding a New Command

1. Add command in `cli.py` using Typer
2. Implement functionality
3. Add tests
4. Update README

### Adding a New UI Theme

1. Create theme in `ui/themes.py`
2. Add to `Themes` class
3. Update `UITheme` enum
4. Add tests
5. Document in README

## Pull Request Process

1. **Update documentation**
   - Update README if needed
   - Add docstrings
   - Update CHANGELOG

2. **Ensure tests pass**

   ```bash
   make test
   make lint
   ```

3. **Create pull request**
   - Clear title and description
   - Reference related issues
   - Include screenshots for UI changes

4. **Code review**
   - Address reviewer feedback
   - Keep commits clean
   - Squash if requested

5. **Merge**
   - Maintainers will merge when approved
   - Delete branch after merge

## Reporting Issues

### Bug Reports

Include:

- WatchFlow version (`watchflow info`)
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Error messages/logs

### Feature Requests

Include:

- Use case description
- Proposed solution
- Alternative solutions considered
- Potential impact

## Documentation

- Keep README updated
- Document new features
- Add examples
- Update configuration reference

## Questions?

- Open an issue for questions
- Check existing issues first
- Be respectful and patient

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to WatchFlow! 🚀
