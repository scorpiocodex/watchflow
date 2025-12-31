# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability in WatchFlow, please report it responsibly.

### How to Report

1. **Do NOT** create a public GitHub issue for security vulnerabilities
2. Email your findings to: scorpiocodex0@gmail.com
3. Include the following in your report:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Assessment**: We will assess the vulnerability and its impact within 7 days
- **Resolution**: Critical vulnerabilities will be addressed within 30 days
- **Disclosure**: We will coordinate disclosure timing with you

## Security Best Practices

When using WatchFlow, please follow these guidelines:

### Configuration Files

- **Do not** store sensitive credentials in `watchflow.yaml`
- Use environment variables with `${VAR}` syntax for secrets
- Keep configuration files out of public repositories if they contain sensitive paths

### Command Execution

- WatchFlow executes commands defined in your configuration file
- Only use configuration files from trusted sources
- Review commands before running `watchflow run` on untrusted projects
- Commands run with the same permissions as the WatchFlow process

### Environment Variables

- Use `${VAR:-default}` syntax to provide safe defaults
- Avoid exposing sensitive environment variables in command output
- Be cautious when using template variables like `{{path}}` in shell commands

## Known Security Considerations

1. **Shell Command Execution**: On Windows, commands are executed via shell. Ensure your configuration files are from trusted sources.

2. **File Watching**: WatchFlow monitors filesystem events. It does not validate file contents before triggering commands.

3. **No Sandbox**: Commands run in the same environment as WatchFlow, with full access to the filesystem and network.

## Dependencies

WatchFlow uses these core dependencies:
- typer (CLI framework)
- rich (terminal UI)
- watchdog (filesystem monitoring)
- pydantic (data validation)
- pyyaml (configuration parsing)
- structlog (logging)

We regularly update dependencies to include security patches. Run `pip install --upgrade watchflow` to get the latest version.

## Changelog

Security-related changes are documented in [CHANGELOG.md](./CHANGELOG.md) with the `[Security]` prefix.
