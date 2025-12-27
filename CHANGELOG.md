# Changelog

All notable changes to WatchFlow will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0] - 2025-01-20

### Added

- **Intelligent Project Detection**: Auto-detects 7+ languages (Python, Node.js, Go, Rust, Java, Ruby, PHP)
- **Package Manager Detection**: Supports Poetry, uv, pip, npm, Yarn, pnpm, Maven, Gradle, and more
- **Responsive Terminal UI**: Adapts to terminal width with full, compact, and minimal layouts
- **4 UI Themes**: Pro (default), Minimal (CI/CD safe), Neon, and Auto-detect
- **High-Performance File Watching**: Cross-platform async file watching with debouncing
- **Parallel Command Execution**: Configurable concurrency limits with global and per-watcher controls
- **Template Variables**: Support for `{{path}}`, `{{paths}}`, `{{event}}`, `{{timestamp}}`, `{{watcher}}`
- **Conditional Execution**: `skip_until_exists` and `only_if_changed` conditions
- **Retry Strategies**: Fixed and exponential backoff retry mechanisms
- **Intelligent Test Handling**: Auto-detects and gracefully skips tests when none exist
- **Tool Detection**: Checks for required development tools and provides installation guidance
- **Structured Logging**: Production-ready logging with structlog
- **Graceful Shutdown**: Clean handling of SIGINT/SIGTERM signals
- **Type Safety**: Full mypy type checking throughout the codebase
- **Comprehensive Tests**: 91%+ test coverage with 44+ tests

### Commands

- `watchflow init`: Initialize configuration with auto-detection
- `watchflow run`: Start file watching and command execution
- `watchflow validate`: Validate configuration files
- `watchflow info`: Display system and environment information

### Configuration Features

- YAML-based configuration with Pydantic validation
- Version control (v1)
- Global settings (theme, fail_fast, max_parallel_commands)
- Per-watcher configuration (paths, patterns, debounce)
- Per-command settings (timeout, retries, retry_strategy, working_dir)

### Documentation

- Comprehensive README with examples
- Full configuration reference
- Usage examples for all supported languages
- Best practices and patterns

### Development

- Black code formatting
- Ruff linting
- mypy type checking
- pytest test suite
- Makefile for common tasks
- GitHub-ready project structure

---

## [0.5] - Initial Release (Internal)

### Added Additional

- Core file watching functionality
- Basic command execution
- Initial project structure

---

## Release Notes

### v1.0 - Production Release

This is the first production-ready release of WatchFlow, designed for professional developers and DevOps engineers.

**Key Highlights:**

- 🧠 **Smart Detection**: Automatically identifies your project type and generates optimized configs
- 📱 **Responsive UI**: Beautiful terminal output that adapts to any screen size
- ⚡ **High Performance**: Async operations with intelligent debouncing and parallel execution
- 🛡️ **Production Ready**: 91%+ test coverage, full type safety, and comprehensive error handling

**What's Next:**
Future releases may include:

- DAG-based command dependencies
- Hot-reload configuration
- Plugin system
- Remote execution agents
- Web dashboard
- Distributed watching

---

For detailed upgrade instructions and migration guides, see the [README](./README.md).
