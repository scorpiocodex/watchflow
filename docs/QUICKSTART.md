# WatchFlow Quick Start Guide

Get up and running with WatchFlow in 5 minutes!

## Installation

### Pre-built (Recommended)

Download the pre-built version from the [Release page](https://github.com/scorpiocodex/watchflow/releases)

```bash
pip install watchflow
```

## 1. Initialize Your Project

Navigate to your project directory and run:

```bash
cd your-project
watchflow init
```

WatchFlow will:

- 🔍 Auto-detect your project type (Python, Node.js, Go, etc.)
- ✅ Check for required development tools
- 📝 Generate an optimized `watchflow.yaml` configuration
- 💡 Show you what to do next

### Example Output

```bash
👁️ WatchFlow v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️ Detected Projects:

┏━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Language ┃ Confidence ┃ Package Manager┃ Files                 ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ python   │ 95%        │ poetry         │ pyproject.toml, po... │
└──────────┴────────────┴────────────────┴───────────────────────┘

⚙️ Required Tools:

  ✓ python (3.11.0)
  ✓ pip (23.0.1)
  ✓ poetry (1.7.1)

✅ Configuration created: watchflow.yaml
```

## 2. Review Your Configuration

Open `watchflow.yaml` to see your generated configuration:

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
    patterns:
      - "*.py"
    ignore_patterns:
      - "__pycache__"
      - "*.pyc"
    commands:
      - name: format-code
        cmd: ["black", "."]
      
      - name: run-tests
        cmd: ["pytest"]
```

## 3. Start Watching

Start WatchFlow to begin watching your files:

```bash
watchflow run
```

### What Happens Now?

WatchFlow is now:

- 👁️ **Watching** your source files for changes
- ⚡ **Executing** configured commands when files change
- 📊 **Displaying** real-time status in your terminal

### Example

```bash
👁️ WatchFlow v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Starting WatchFlow for my-project...

  👁️ python-watcher: 2 command(s)

📄 [10:15:23] python-watcher: modified src/main.py

  ▶️ Running: format-code
  ✅ SUCCESS format-code (0.45s)
  
  ▶️ Running: run-tests
  ✅ SUCCESS run-tests (2.31s)
```

## 4. Make Changes

Try editing a Python file in your project. WatchFlow will automatically:

1. Detect the file change
2. Run the configured commands (format, lint, test)
3. Display the results in real-time

## Common Workflows

### Python Development

```bash
# Initialize
watchflow init --type python

# Start watching
watchflow run
```

Your workflow now includes automatic:

- ✨ Code formatting (Black)
- 🔍 Linting (Ruff)
- 🧪 Test execution (pytest)

### Node.js Development

```bash
# Initialize
watchflow init --type nodejs

# Start watching
watchflow run
```

Automatically handles:

- 🔍 ESLint checking
- 🧪 Jest tests
- 📦 TypeScript compilation

### Multiple Languages

If your project uses multiple languages:

```bash
watchflow init
# Select your primary language when prompted
```

## Customization

### Change UI Theme

```bash
# Minimal theme (CI/CD friendly)
watchflow run --theme minimal

# Neon theme (high contrast)
watchflow run --theme neon

# Auto-detect best theme
watchflow run --theme auto
```

### Debug Mode

```bash
watchflow run --debug
```

### Custom Config Location

```bash
watchflow run --config path/to/config.yaml
```

## Stopping WatchFlow

Press `Ctrl+C` to stop WatchFlow gracefully:

```bash
⏹️ Shutting down gracefully...
```

## Next Steps

### Customize Your Configuration

Edit `watchflow.yaml` to:

- Add more watchers
- Configure command timeouts
- Add retry strategies
- Use template variables
- Set up parallel execution

See the [full documentation](../README.md) for all options.

### Validate Your Config

```bash
watchflow validate
```

Ensures your configuration is correct before running.

### Check System Info

```bash
watchflow info
```

Displays system and environment information.

## Tips & Tricks

### 1. Multiple Watchers

Watch different file types separately:

```yaml
watchers:
  - name: python-watcher
    paths: [src]
    patterns: ["*.py"]
    commands: [...]
  
  - name: docs-watcher
    paths: [docs]
    patterns: ["*.md"]
    commands: [...]
```

### 2. Ignore Patterns

Prevent unnecessary triggers:

```yaml
ignore_patterns:
  - "__pycache__"
  - "*.pyc"
  - ".venv"
  - "node_modules"
  - ".git"
```

### 3. Debouncing

Adjust debounce time to prevent duplicate runs:

```yaml
debounce: 500  # Wait 500ms for more changes
```

### 4. Parallel Execution

Run commands simultaneously:

```yaml
parallel: true
commands:
  - name: lint
    cmd: ["ruff", "check"]
  - name: test
    cmd: ["pytest"]
```

Both commands run at the same time!

### 5. Template Variables

Use dynamic values in commands:

```yaml
commands:
  - name: process
    cmd: ["python", "process.py", "{{path}}"]
```

Available variables:

- `{{path}}` - Changed file path
- `{{paths}}` - All changed paths
- `{{event}}` - Event type
- `{{timestamp}}` - Current timestamp
- `{{watcher}}` - Watcher name

## Troubleshooting

### Config Not Found

```bash
Error: Configuration file not found: watchflow.yaml
```

**Solution**: Run `watchflow init` to create one.

### Invalid Configuration

```bash
Error: Configuration validation failed
```

**Solution**: Run `watchflow validate` for detailed errors.

### Tools Not Found

```bash
✗ black
   → pip install black
```

**Solution**: Install the missing tool as indicated.

### Permission Denied

```bash
Error: Permission denied: /path/to/file
```

**Solution**: Ensure you have read/write permissions.

## Getting Help

- 📖 [Full Documentation](../README.md)
- 🐛 [Report Issues](https://github.com/scorpiocodex/watchflow/issues)

---

## **Happy Watching! 🚀**
