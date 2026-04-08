---
name: cli-patterns
description: "CLI design patterns for the scaffolder using Click + Rich + Questionary. Use when working on the CLI layer, adding commands, or modifying interactive prompts. Includes dynamic option injection and dual-mode (interactive/non-interactive) patterns."
---

# CLI Patterns

The scaffolder CLI combines Click (command framework), Rich (terminal output), and Questionary (interactive prompts) to provide both scripted and interactive usage modes.

## When to Use This Skill

- Adding a new CLI command or subcommand
- Modifying the interactive question flow
- Adding new CLI options
- Working on the dual-mode (interactive / non-interactive) pattern

## Main Instructions

### CLI Architecture

```
cli.py
├── cli()              — @click.group() root
├── init()             — @cli.command() main command
├── collect_cli_options() — discovers actions, collects CLIOption list
├── add_dynamic_options() — injects options into Click command
└── fill_default_context() — fills defaults for non-interactive mode
```

### Dual-Mode Pattern

The CLI supports two modes:
1. **Interactive** (`--interactive`): Questionary prompts for each missing option
2. **Non-interactive**: All options from CLI flags, defaults fill the rest

```python
@cli.command()
@add_dynamic_options
@click.argument("project_name")
@click.option("--interactive", is_flag=True)
@click.option("--no-install", is_flag=True)
def init(project_name, interactive, no_install, **kwargs):
    context = dict(kwargs)
    context["project_name"] = project_name

    if not interactive:
        context = fill_default_context(context)

    manager = ActionManager(project_name, context)
    context = manager.run_postfill_hooks(context)

    if interactive:
        context = manager.ask_interactive_questions(context)
    manager.create_project()
```

### Dynamic Option Injection

Actions define `cli_options: list[CLIOption]`. These are collected in dependency order and injected into the Click command via `add_dynamic_options()`:

```python
def add_dynamic_options(command):
    cli_options = collect_cli_options()
    for opt in reversed(cli_options):
        # Convert CLIOption to click.option decorator
        command = click.option(...)(command)
    return command
```

### Adding a New Command

```python
@cli.command()
@click.argument("target")
@click.option("--dry-run", is_flag=True, help="Preview without changes")
def add(target, dry_run):
    """Add a component to an existing project."""
    # Implementation
```

### Postfill Hooks

Actions can define `postfill_hook` on CLIOption to transform context after user input:

```python
def postfill_remote_url(context: dict) -> dict:
    url = context.get("remote_url", "")
    if "github" in url:
        context["host"] = "github"
    return context

CLIOption(
    name="--remote-url",
    type="str",
    postfill_hook=postfill_remote_url,
)
```

## Project-Specific Context

- Entry point: `septeo-scaf` (defined in `pyproject.toml [project.scripts]`)
- Click group: `cli()` with `init` as primary subcommand
- Rich Console for all output formatting
- Questionary for interactive prompts

## Anti-Patterns

- Never parse `sys.argv` manually — let Click handle it
- Never use `input()` — use Questionary
- Never use `print()` — use Rich Console
- Never add options directly to commands — use the `CLIOption` + `add_dynamic_options` pattern
- Never block on prompts without a default value (breaks non-interactive mode)
