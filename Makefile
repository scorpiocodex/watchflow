.PHONY: help dev test test-cov test-quick lint format type-check check build clean install all

help:
	@echo ============================== 
	@echo WatchFlow Development Commands
	@echo ==============================
	@echo.
	@echo Setup:
	@echo   make dev              - Install development dependencies
	@echo   make install          - Install package locally
	@echo.
	@echo Testing:
	@echo   make test             - Run all tests with verbose output
	@echo   make test-quick       - Run tests without coverage (faster)
	@echo   make test-cov         - Run tests with coverage report
	@echo.
	@echo Code Quality:
	@echo   make lint             - Run all linters (ruff + mypy)
	@echo   make format           - Format code with black
	@echo   make type-check       - Run mypy type checking only
	@echo   make check            - Run format + lint + test (full check)
	@echo.
	@echo Build and Clean:
	@echo   make build            - Build distribution packages
	@echo   make clean            - Remove build artifacts and caches
	@echo.
	@echo Workflow:
	@echo   make all              - Run format, lint, and test (recommended)

dev:
	@echo Installing development dependencies...
	@pip install -e ".[dev]"
	@echo Done! Development environment ready.

test:
	@echo Running tests with verbose output...
	@pytest -v

test-quick:
	@echo Running quick tests (no coverage)...
	@pytest -q

test-cov:
	@echo Running tests with coverage...
	@pytest --cov=src/watchflow --cov-report=term-missing --cov-report=html
	@echo Coverage report generated in htmlcov/index.html

lint: type-check
	@echo Running ruff linter...
	@ruff check src/watchflow tests
	@echo Linting passed!

format:
	@echo Formatting code with black...
	@black src/watchflow tests
	@echo Auto-fixing ruff issues...
	@ruff check --fix src/watchflow tests || exit 0
	@echo Code formatted!

type-check:
	@echo Running mypy type checker...
	@mypy src/watchflow
	@echo Type checking passed!

check: format lint test
	@echo.
	@echo ========================================
	@echo All checks passed successfully!
	@echo ========================================

all: format lint test
	@echo.
	@echo ========================================
	@echo Build complete and verified!
	@echo ========================================

build:
	@echo Building distribution packages...
	@poetry build --clean --verbose
	@echo Build complete! Packages in dist/

clean:
	@echo Cleaning build artifacts and caches...
	@if exist build rmdir /s /q build 2>nul
	@if exist dist rmdir /s /q dist 2>nul
	@if exist *.egg-info rmdir /s /q *.egg-info 2>nul
	@if exist .pytest_cache rmdir /s /q .pytest_cache 2>nul
	@if exist .mypy_cache rmdir /s /q .mypy_cache 2>nul
	@if exist .ruff_cache rmdir /s /q .ruff_cache 2>nul
	@if exist htmlcov rmdir /s /q htmlcov 2>nul
	@if exist .coverage del /q .coverage 2>nul
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d" 2>nul
	@for /r . %%f in (*.pyc) do @if exist "%%f" del /q "%%f" 2>nul
	@echo Cleanup complete!

install:
	@echo Installing package locally...
	@pip install -e .
	@echo Package installed!