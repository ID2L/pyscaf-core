---
name: action-plugin-system
description: "Guide for creating new scaffolder actions (plugins). Use when adding a new action to the scaffolder, modifying an existing action, or understanding the action API. Includes complete checklist, code templates, and testing patterns."
---

# Action Plugin System

Each scaffolder feature is implemented as an **Action** — a self-contained plugin that is auto-discovered and executed in dependency order.

## When to Use This Skill

- Adding a new scaffolding action (e.g., Docker setup, CI/CD config)
- Modifying an existing action's behavior
- Understanding the Action API and lifecycle
- Debugging action execution order

## Main Instructions

### Step-by-Step: Creating a New Action

#### 1. Write Tests First (TDD)

Create `tests/actions/<name>/test_default.yaml`:

```yaml
cli_arguments:
  options: {}

checks:
  - name: "Expected file exists"
    type: exist
    file_path: "tmp_project/<expected_file>"
```

#### 2. Create the Action Module

Create `src/septeo_scaffolder/actions/<name>/__init__.py`:

```python
from pathlib import Path
from septeo_scaffolder.actions import Action, CLIOption, ChoiceOption

class MyFeatureAction(Action):
    depends = {"core"}
    run_preferably_after = "core"
    cli_options = [
        CLIOption(
            name="--my-option",
            type="bool",
            help="Enable my feature",
            prompt="Do you want my feature?",
            default=True,
        ),
    ]

    def activate(self, context: dict) -> bool:
        return context.get("my_option", True)

    def skeleton(self, context: dict) -> dict[Path, str | None]:
        return {
            Path("my-config.json"): '{"key": "value"}',
            Path("my-dir"): None,  # None = directory
        }

    def init(self, context: dict) -> None:
        super().init(context)  # merges config.toml if present

    def install(self, context: dict) -> None:
        pass  # optional: run post-install commands
```

#### 3. Add config.toml (Optional)

Create `src/septeo_scaffolder/actions/<name>/config.toml` to inject settings into `pyproject.toml`:

```toml
[tool.my-feature]
enabled = true
```

#### 4. Verify

```bash
uv run pytest tests/actions/ --action-filter="<name>" -v
```

### CLIOption Types

| Type | Click Mapping | Questionary | Context Value |
|---|---|---|---|
| `str` | `click.STRING` | `text()` | `str` |
| `bool` | `--flag/--no-flag` | `confirm()` | `bool` |
| `int` | `click.INT` | `text()` → `int()` | `int` |
| `choice` | `click.Choice` | `select()` / `checkbox()` | `str` (key) |

### ChoiceOption for Rich Choices

```python
CLIOption(
    name="--license",
    type="choice",
    choices=[
        ChoiceOption(key="mit", display="MIT License (permissive)", value="template_MIT.txt"),
        ChoiceOption(key="apache", display="Apache 2.0", value="template_Apache-2.0.txt"),
    ],
    default=0,  # index of default choice
)
```

### Dependency Declaration

```python
class MyAction(Action):
    depends = {"core", "git"}           # hard deps
    run_preferably_after = "git"        # soft ordering (mandatory if len(depends) > 1)
```

## Project-Specific Context

- Actions live in `src/septeo_scaffolder/actions/<name>/`
- Auto-discovered by `discover_actions()` via `pkgutil.iter_modules`
- `ActionManager` orchestrates: discovery → ordering → execution
- Context flows through all actions as `dict[str, Any]`

## Anti-Patterns

- Never create an action without tests
- Never use `os.chdir()` in actions — use `self.project_path`
- Never access other actions' internals
- Never forget `run_preferably_after` when `len(depends) > 1`
- Never write to filesystem outside of `skeleton()` return dict (use `init()` for subprocess calls)
