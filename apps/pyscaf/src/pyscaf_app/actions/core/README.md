## uv Integration

This project uses uv for dependency management and packaging. uv provides a modern and extremely fast way to manage Python dependencies and build packages.

### Features

- **Dependency Management**: uv manages project dependencies through `pyproject.toml`
- **Virtual Environment**: Automatically creates and manages a virtual environment
- **Build System**: Integrated build system for creating Python packages
- **Lock File**: Generates a `uv.lock` file for reproducible installations

### Common Commands

```bash
# Install dependencies
uv sync

# Add a new dependency
uv add package-name

# Add a development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Run a command within the virtual environment
uv run python script.py

# Activate the virtual environment
uv run shell
```

### Project Structure

The project follows a standard Python package structure:
- `pyproject.toml`: Project configuration and dependencies
- `uv.lock`: Locked dependencies for reproducible builds
- `src/`: Source code directory
- `tests/`: Test files directory

### Development

To start developing:
1. Ensure uv is installed
2. Run `uv sync` to install all dependencies
3. Use `uv run` to execute scripts in the environment
4. Start coding!

For more information, visit [uv's official documentation](https://docs.astral.sh/uv/).

## Ruff Integration

Ruff is an extremely fast Python linter and code formatter, written in Rust. It can replace Flake8, Black, isort, pyupgrade, and more, while being much faster than any individual tool.

### VSCode Default Configuration

The file `.vscode/default_settings.json` provides a recommended configuration for using Ruff in VSCode:

```json
{
    "[python]": {
      "editor.formatOnSave": true,
      "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
      },
      "editor.defaultFormatter": "charliermarsh.ruff"
    },
    "notebook.formatOnSave.enabled": true,
    "notebook.codeActionsOnSave": {
      "notebook.source.fixAll": "explicit",
      "notebook.source.organizeImports": "explicit"
    },
    "ruff.lineLength": 88
}
```

#### Explanation of each line:
- `editor.formatOnSave`: Enables automatic formatting on save for all files.
- `[python].editor.defaultFormatter`: Sets Ruff as the default formatter for Python files.
- `[python]editor.codeActionsOnSave.source.organizeImports`: Organizes Python imports automatically on save.
- `[python]editor.codeActionsOnSave.source.fixAll`: Applies all available code fixes (including linting) on save.
- `ruff.lineLength`: Line length for your python files

### Useful Ruff Commands

You can run the following commands commands directly in the shell

```bash
# Lint all Python files in the current directory
ruff check .

# Format all Python files in the current directory
ruff format .

# Automatically fix all auto-fixable problems
ruff check . --fix
```

For more information, see the [official Ruff VSCode extension documentation](https://github.com/astral-sh/ruff-vscode) and the [Ruff documentation](https://docs.astral.sh/ruff/). 

You can enable specific rules over a catalog of over 800+ rules, depending on your needs or framework of choice. Check it out at the [Ruff documentation](docs.astral.sh/ruff/rules/). 