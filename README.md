# 👁️ WatchFlow

## **Next-Generation Intelligent File Watcher & Automation CLI**

[![Python 3.11+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Watch. React. Automate.**

WatchFlow is a production-ready, cross-platform intelligent file watcher and automation CLI designed for professional developers and DevOps engineers. It automatically detects your project type, generates optimized configurations, and executes commands intelligently with beautiful terminal output.

---

## ✨ Features

### 🧠 **Intelligent Project Detection**

- **Auto-detects 7+ languages**: Python, Node.js, Go, Rust, Java, Ruby, PHP
- **Smart package manager detection**: Poetry, uv, pip, npm, Yarn, pnpm, and more
- **Confidence scoring** with interactive multi-language selection
- **Tool availability checking** with installation guidance

### 📱 **Responsive Terminal UI**

- **Adaptive layouts** based on terminal width (80+, 60-79, <60 columns)
- **4 beautiful themes**: Pro (default), Minimal (CI/CD safe), Neon, Auto-detect
- **Smart truncation** for optimal information density
- **Emoji + icon support** with ASCII fallback

### ⚡ **High-Performance Execution**

- **Async file watching** across Linux, macOS, and Windows
- **Parallel command execution** with configurable concurrency limits
- **Intelligent debouncing** (0-60000ms) to prevent duplicate runs
- **Smart test skipping** when no tests exist
- **Retry strategies**: Fixed and exponential backoff

### ⚙️ **Flexible Configuration**

- **YAML-based** with full Pydantic validation
- **Template variables**: `{{path}}`, `{{paths}}`, `{{event}}`, `{{timestamp}}`, `{{watcher}}`
- **Conditional execution**: `skip_until_exists`, `only_if_changed`
- **Per-command settings**: timeout, retries, working directory

### 🛡️ **Production Ready**

- **91%+ test coverage** with 44+ comprehensive tests
- **Full type safety** with mypy
- **Structured logging** via structlog
- **Graceful shutdown** handling SIGINT/SIGTERM
- **Error recovery** with detailed reporting

---

## 🚀 Quick Start

### Installation (Recommended)

**Download the pre-built version from the** [Release page](https://github.com/scorpiocodex/watchflow/releases)

```bash
pip install watchflow
```

### Initialize Your Project

```bash
cd your-project
watchflow init
```

WatchFlow will:

1. 🔍 Auto-detect your project type
2. ✅ Check required tools
3. 📝 Generate optimized `watchflow.yaml`
4. 🎯 Provide next steps

### Start Watching

```bash
watchflow run
```

That's it! WatchFlow is now monitoring your files and running commands on changes.

---

## 📖 Usage

### Commands

#### `watchflow init`

Initialize configuration with intelligent project detection:

```bash
# Auto-detect project
watchflow init

# Specify project type
watchflow init --type python

# Skip tool checking
watchflow init --no-check-tools

# Force overwrite existing config
watchflow init --force
```

#### `watchflow run`

Start watching and executing commands:

```bash
# Use default config (watchflow.yaml)
watchflow run

# Use custom config
watchflow run --config my-config.yaml

# Select theme
watchflow run --theme neon

# Enable debug logging
watchflow run --debug
```

**Themes:**

- `pro` (default): Full-featured with emojis, colors, and panels
- `minimal`: ASCII-only, CI/CD safe
- `neon`: High contrast for presentations
- `auto`: Auto-detect based on terminal capabilities

#### `watchflow validate`

Validate your configuration:

```bash
watchflow validate
watchflow validate my-config.yaml
```

#### `watchflow info`

Display system information:

```bash
watchflow info
```

---

## ⚙️ Configuration

### Basic Structure

```yaml
version: 1
project_name: "my-project"
project_type: python

global:
  theme: pro
  fail_fast: false
  max_parallel_commands: 4

watchers:
  - name: python-watcher
    paths:
      - src
      - tests
    recursive: true
    patterns:
      - "*.py"
    ignore_patterns:
      - "__pycache__"
      - "*.pyc"
    debounce: 100
    parallel: false
    commands:
      - name: format-code
        cmd: ["black", "."]
        timeout: 30
        retries: 0
      
      - name: run-tests
        cmd: ["pytest"]
        timeout: 300
        retries: 1
        retry_strategy: exponential
```

### Configuration Reference

#### Global Settings

| Field | Type | Default | Description |
| ------- | ------ | --------- | ------------- |
| `theme` | string | `pro` | UI theme (pro, minimal, neon, auto) |
| `fail_fast` | boolean | `false` | Stop on first command failure |
| `max_parallel_commands` | integer | `4` | Maximum concurrent commands |
| `log_level` | string | `INFO` | Logging level |

#### Watcher Settings

| Field | Type | Required | Description |
| ------- | ------ | ---------- | ------------- |
| `name` | string | ✅ | Watcher identifier |
| `paths` | list[string] | ✅ | Paths to watch |
| `recursive` | boolean | ❌ | Watch subdirectories (default: true) |
| `patterns` | list[string] | ❌ | File patterns to include |
| `ignore_patterns` | list[string] | ❌ | File patterns to ignore |
| `debounce` | integer | ❌ | Debounce time in ms (default: 100) |
| `parallel` | boolean | ❌ | Run commands in parallel (default: false) |
| `commands` | list[Command] | ✅ | Commands to execute |

#### Command Settings

| Field | Type | Required | Description |
| ------- | ------ | ---------- | ------------- |
| `name` | string | ✅ | Command identifier |
| `cmd` | list[string] | ✅ | Command and arguments |
| `timeout` | integer | ❌ | Timeout in seconds |
| `retries` | integer | ❌ | Number of retries (default: 0) |
| `retry_strategy` | string | ❌ | Retry strategy (fixed, exponential) |
| `working_dir` | string | ❌ | Working directory |
| `skip_until_exists` | string | ❌ | Skip until file/dir exists |
| `only_if_changed` | list[string] | ❌ | Run only if patterns changed |

### Template Variables

Use template variables in commands for dynamic values:

```yaml
commands:
  - name: process-file
    cmd: ["python", "process.py", "{{path}}"]
  
  - name: log-event
    cmd: ["echo", "{{event}} at {{timestamp}}"]
  
  - name: batch-process
    cmd: ["./batch.sh", "{{paths}}"]
```

Available variables:

- `{{path}}` - Primary changed file path
- `{{paths}}` - All changed file paths (space-separated)
- `{{event}}` - Event type (modified, created, deleted, moved)
- `{{timestamp}}` - ISO 8601 timestamp
- `{{watcher}}` - Watcher name

---

## 🎯 Examples

### Python Project with Poetry

```yaml
version: 1
project_name: "my-python-app"
project_type: python

watchers:
  - name: python-watcher
    paths: ["."]
    patterns: ["*.py"]
    ignore_patterns: ["__pycache__", ".venv", "*.pyc"]
    commands:
      - name: format
        cmd: ["poetry", "run", "black", "."]
      
      - name: lint
        cmd: ["poetry", "run", "ruff", "check", "."]
      
      - name: type-check
        cmd: ["poetry", "run", "mypy", "src"]
      
      - name: test
        cmd: ["poetry", "run", "pytest", "-v"]
```

### Node.js with Multiple Watchers

```yaml
version: 1
project_name: "web-app"
project_type: nodejs

watchers:
  - name: typescript-watcher
    paths: ["src"]
    patterns: ["*.ts", "*.tsx"]
    commands:
      - name: compile
        cmd: ["npm", "run", "build"]
        timeout: 60
  
  - name: css-watcher
    paths: ["styles"]
    patterns: ["*.css", "*.scss"]
    commands:
      - name: build-styles
        cmd: ["npm", "run", "build:css"]
  
  - name: test-watcher
    paths: ["src", "tests"]
    patterns: ["*.test.ts"]
    commands:
      - name: run-tests
        cmd: ["npm", "test", "--", "{{path}}"]
```

### Parallel Execution

```yaml
watchers:
  - name: multi-task
    paths: ["src"]
    parallel: true  # Run all commands simultaneously
    commands:
      - name: lint
        cmd: ["eslint", "."]
      
      - name: type-check
        cmd: ["tsc", "--noEmit"]
      
      - name: test
        cmd: ["jest"]
```

### Retry Strategies

```yaml
commands:
  # Fixed retry: 1 second between attempts
  - name: flaky-test
    cmd: ["npm", "test"]
    retries: 3
    retry_strategy: fixed
  
  # Exponential backoff: 1s, 2s, 4s, 8s
  - name: api-call
    cmd: ["./sync-api.sh"]
    retries: 4
    retry_strategy: exponential
```

### Conditional Execution

```yaml
commands:
  # Wait for build output before deploying
  - name: deploy
    cmd: ["./deploy.sh"]
    skip_until_exists: "dist/bundle.js"
  
  # Only run on specific file changes
  - name: update-docs
    cmd: ["./generate-docs.sh"]
    only_if_changed: ["*.md", "docs/**"]
```

---

## 🧪 Intelligent Test Handling

WatchFlow intelligently handles test execution:

✅ **Detects test files** in common locations (`tests/`, `test/`, `spec/`, `__tests__/`)

✅ **Detects test frameworks** (pytest, jest, rspec, etc.)

✅ **Gracefully skips** tests if none exist

✅ **Clear reporting** of skip reasons

```bash
⏭️ SKIPPED run-tests (0.00s)
   Reason: no test files or directories found
```

This prevents build failures in projects without tests and provides clear feedback.

---

## 🎨 UI Themes

### Pro Theme (Default)

```bash
watchflow run --theme pro
```

- ✨ Full emoji and icon support
- 🎨 Rich colors and panels
- 📊 Information-dense layout
- 🖥️ Beautiful terminal experience

### Minimal Theme (CI/CD Safe)

```bash
watchflow run --theme minimal
```

- 📝 ASCII-only characters
- ⚫ No colors
- 🤖 Perfect for CI/CD pipelines
- 📦 Parseable output

### Neon Theme

```bash
watchflow run --theme neon
```

- 💡 High contrast colors
- ✨ Bright, vibrant UI
- 📺 Presentation-friendly
- 🌟 Eye-catching design

### Auto Theme

```bash
watchflow run --theme auto
```

- 🤖 Detects terminal capabilities
- 🔄 Adapts to CI/CD environments
- 📊 Chooses best theme automatically
- ⚙️ Zero configuration

---

## 🏗️ Architecture

WatchFlow is built with a clean, modular architecture:

```bash
watchflow/
├── cli.py              # CLI interface (Typer)
├── core/
│   ├── engine.py       # Main orchestration
│   ├── watcher.py      # File system watching
│   └── executor.py     # Command execution
├── config/
│   ├── models.py       # Pydantic models
│   └── validator.py    # Config validation
├── detection/
│   ├── detector.py     # Project detection
│   └── tools.py        # Tool checking
├── ui/
│   ├── renderer.py     # UI rendering
│   └── themes.py       # Theme definitions
└── utils/
    ├── logging.py      # Structured logging
    └── templates.py    # Template engine
```

---

## 🧪 Development

### Setup

```bash
# Clone repository
git clone https://github.com/scorpiocodex/watchflow.git
cd watchflow

# Install development dependencies
make dev
```

### Additional Commands

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# Run linters
make lint

# Format code
make format

# Build package
make build

# Clean artifacts
make clean
```

### Testing

WatchFlow has comprehensive test coverage:

- ✅ **91%+ coverage**
- ✅ **44+ tests**
- ✅ **Unit tests** for all components
- ✅ **Integration tests** for workflows
- ✅ **Type safety** with mypy

```bash
# Run tests
pytest

# With coverage report
pytest --cov=src/watchflow --cov-report=html

# Run specific test
pytest tests/test_detector.py::test_detect_python
```

---

## 📊 Supported Languages & Tools

### Languages (7+)

| Language | Detection Files | Package Managers |
| ---------- | --------------- | ---------------- |
| **Python** | pyproject.toml, setup.py, requirements.txt | poetry, uv, pip, pipenv |
| **Node.js** | package.json, package-lock.json | npm, yarn, pnpm |
| **Go** | go.mod, go.sum | go modules |
| **Rust** | Cargo.toml, Cargo.lock | cargo |
| **Java** | pom.xml, build.gradle | maven, gradle |
| **Ruby** | Gemfile, Gemfile.lock | bundler |
| **PHP** | composer.json, composer.lock | composer |

### Tool Detection

WatchFlow checks for required tools and provides installation guidance:

```bash
⚙️ Required Tools:

  ✓ python (Python 3.11.0)
  ✓ pip (23.0.1)
  ✓ poetry (1.7.1)
  ✗ black
     → pip install black
```

---

## 🚀 Performance

WatchFlow is designed for performance:

- ⚡ **Async I/O** for non-blocking operations
- 🔄 **Debouncing** prevents duplicate executions
- 🎯 **Smart filtering** with glob patterns
- 🔀 **Parallel execution** with concurrency limits
- 📊 **Efficient file watching** using native OS events

### Benchmarks

- **Startup time**: <100ms
- **Event processing**: <10ms latency
- **Memory usage**: <50MB baseline
- **CPU usage**: <1% when idle

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure `make lint` and `make test` pass
5. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](./LICENSE) for details.

---

## 🙏 Acknowledgments

Built with:

- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal UI
- [Watchdog](https://python-watchdog.readthedocs.io/) - File system events
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [structlog](https://www.structlog.org/) - Structured logging

---

## 📞 Support

- 📖 [Documentation](https://github.com/scorpiocodex/watchflow#readme)
- 🐛 [Issue Tracker](https://github.com/scorpiocodex/watchflow/issues)

---

**Made with ❤️ by developer, for developers.**

**Watch. React. Automate.** 🚀
