# Creating Actions

This guide walks through creating a new scaffolder action (plugin) for pyscaf-core.

## Overview

Each scaffolding feature is implemented as an [`Action`][pyscaf_core.actions.Action] — a self-contained plugin that is auto-discovered and executed in dependency order.

## Step 1: Write Tests First (TDD)

Create a YAML test file at `tests/actions/<name>/test_default.yaml`:

```yaml
cli_arguments:
  options: {}

checks:
  - name: "Expected file exists"
    type: exist
    file_path: "tmp_project/<expected_file>"
```

Run with:

```bash
uv run pytest --action-filter="<name>:test_default" -v
```

## Step 2: Create the Action Module

Create `src/<your_app>/actions/<name>/__init__.py`:

```python
from pathlib import Path

from pyscaf_core import Action, CLIOption, ChoiceOption


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
        pass
```

## Step 3: Add config.toml (Optional)

Create `src/<your_app>/actions/<name>/config.toml` to inject settings into the generated project's `pyproject.toml`:

```toml
[tool.my-feature]
enabled = true
```

The default [`init()`][pyscaf_core.actions.Action.init] implementation will merge this into the project's `pyproject.toml` automatically.

## CLI Option Types

| Type | Click Mapping | Interactive (Questionary) | Context Value |
|------|---------------|--------------------------|---------------|
| `str` | `click.STRING` | `text()` | `str` |
| `bool` | `--flag/--no-flag` | `confirm()` | `bool` |
| `int` | `click.INT` | `text()` → `int()` | `int` |
| `choice` | `click.Choice` | `select()` / `checkbox()` | `str` (key) |

## Rich Choices with ChoiceOption

Use [`ChoiceOption`][pyscaf_core.actions.ChoiceOption] for choices that need different display vs. stored values:

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

## Dependency Declaration

```python
class MyAction(Action):
    depends = {"core", "git"}           # hard deps
    run_preferably_after = "git"        # soft ordering (required if len(depends) > 1)
```

!!! warning
    If your action has more than one hard dependency, you **must** set `run_preferably_after` to one of them. The preference chain algorithm needs this hint to resolve ordering ambiguity.

## Conditional Visibility

Use `visible_when` to show/hide CLI options based on context:

```python
CLIOption(
    name="--docker-registry",
    type="str",
    help="Docker registry URL",
    visible_when=lambda ctx: ctx.get("docker", False),
)
```

## Post-fill Hooks

Use `postfill_hook` to transform context values after user input:

```python
CLIOption(
    name="--project-name",
    type="str",
    postfill_hook=lambda ctx: {**ctx, "project_slug": ctx["project_name"].replace("-", "_")},
)
```

## Anti-Patterns

- Never create an action without tests
- Never use `os.chdir()` in actions — use `self.project_path`
- Never access other actions' internals
- Never forget `run_preferably_after` when `len(depends) > 1`
- Never write to filesystem outside of `skeleton()` return dict (use `init()` for subprocess calls)
