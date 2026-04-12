# Architecture

pyscaf-core follows a **plugin architecture** where each scaffolding feature is an independent [Action](reference/actions.md) that is auto-discovered and executed in dependency order.

## High-Level Overview

```
CLI Layer (Click)
  └── ActionManager (orchestrator)
       ├── Action Discovery (pkgutil / entry points)
       ├── Preference Chain (dependency resolution)
       └── Action Execution (skeleton → init → install)
```

## Monorepo Layout

The project uses **uv workspaces** to manage multiple packages:

| Package | Role | Import |
|---------|------|--------|
| `packages/pyscaf-core` | Core library | `pyscaf_core` |
| `apps/demo-scaf` | Demo CLI | `demo_scaf` |
| `apps/pyscaf` | Python scaffolder | `pyscaf_app` |
| `apps/septeo-scaf` | Septeo scaffolder | `septeo_scaf` |

Apps depend on `pyscaf-core` via workspace references and register their actions through entry points.

## Action Lifecycle

Every action goes through a **3-pass execution**:

### Pass 1: Skeleton

Each action's [`skeleton(context)`][pyscaf_core.actions.Action.skeleton] returns a `dict[Path, str | None]` describing files and directories to create:

- `Path → str` — create a file with the given content
- `Path → None` — create a directory

### Pass 2: Init

Each action's [`init(context)`][pyscaf_core.actions.Action.init] runs post-skeleton setup. The default implementation merges a `config.toml` file (co-located with the action module) into the project's `pyproject.toml`.

### Pass 3: Install

Each action's [`install(context)`][pyscaf_core.actions.Action.install] runs dependency installation or post-init commands. This pass is skippable with the `--no-install` CLI flag.

## Dependency Resolution

Actions declare dependencies via two attributes:

- `depends: set[str]` — hard dependencies (must run before this action)
- `run_preferably_after: str | None` — soft ordering preference (required when `len(depends) > 1`)

The [preference chain](reference/preference_chain.md) algorithm computes the optimal execution order:

1. **`extend_nodes()`** — builds a reverse dependency graph
2. **`build_chains()`** — groups related actions into chains
3. **`compute_all_resolution_pathes()`** — finds all valid topological orderings
4. **`compute_path_score()`** — selects the best ordering based on preference hints

## Action Discovery

Actions are discovered automatically through two mechanisms:

### Package-based discovery

[`discover_actions_from_package()`][pyscaf_core.actions.discover_actions_from_package] scans a directory for Python modules containing `Action` subclasses using `pkgutil.iter_modules`.

### Entry-point discovery

[`discover_actions_from_entry_points()`][pyscaf_core.actions.discover_actions_from_entry_points] loads actions registered under the `pyscaf_core.plugins` entry point group. This is how apps register their actions:

```toml
# In an app's pyproject.toml
[project.entry-points."pyscaf_core.plugins"]
my_app = "my_app.actions:discover_actions"
```

## Context Dictionary

All user inputs flow through a `dict[str, Any]` context:

- CLI flags are converted to keys: `--remote-url` → `remote_url`
- `None` means "not yet set"
- `False` means "explicitly disabled"
- [`postfill_hook`][pyscaf_core.actions.CLIOption] functions can transform context values after user input

## CLI Framework

The [`build_cli()`][pyscaf_core.cli.build_cli] function creates a complete Click CLI group with:

- An `init` command with dynamic options from all discovered actions
- `--interactive` / `--no-install` flags
- Automatic version display via `--version`

See the [CLI reference](reference/cli.md) for details.
