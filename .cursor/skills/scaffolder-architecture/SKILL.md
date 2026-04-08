---
name: scaffolder-architecture
description: "Plugin-based scaffolder architecture patterns inspired by pyscaf. Use when designing the overall system, adding new modules, or making structural decisions about the CLI scaffolder. Includes action lifecycle, dependency resolution, and project generation flow."
---

# Scaffolder Architecture

This project is a CLI scaffolder (inspired by [pyscaf](https://github.com/ID2L/pyscaf)) that generates project structures via a plugin-based action system. Phase 1 is the CLI tool; Phase 2 will add MCP server capabilities.

## When to Use This Skill

- Designing or modifying the overall scaffolder architecture
- Adding a new module or subsystem
- Reviewing how actions are orchestrated
- Understanding the project generation pipeline

## Main Instructions

### Core Architecture

The scaffolder follows a **plugin architecture** with these layers:

```
CLI Layer (Click)
  └── ActionManager (orchestrator)
       ├── Action Discovery (pkgutil auto-import)
       ├── Preference Chain (dependency resolution)
       └── Action Execution (skeleton → init → install)
```

### Action Lifecycle (3-pass execution)

1. **Skeleton Pass**: Each action's `skeleton(context)` returns a `dict[Path, str | None]` describing files/dirs to create
2. **Init Pass**: Each action's `init(context)` runs post-skeleton setup (default: merge `config.toml` into `pyproject.toml`)
3. **Install Pass**: Each action's `install(context)` runs dependency installation (skippable with `--no-install`)

### Dependency Resolution

Actions declare dependencies via:
- `depends: set[str]` — hard dependencies (must run before)
- `run_preferably_after: str | None` — soft ordering preference

The preference-chain algorithm computes optimal execution order at runtime:
1. `extend_nodes()` — builds reverse dependency graph
2. `build_chains()` — groups related actions into chains
3. `compute_all_resolution_pathes()` — finds valid orderings
4. `compute_path_score()` — selects best ordering

### Context Dictionary

- All user inputs flow through a `dict[str, Any]` context
- CLI flags are converted: `--remote-url` → `remote_url`
- `None` = not yet set, `False` = explicitly disabled
- `postfill_hook` functions can transform context after user input

### Key Differences from pyscaf

This project (septeo-agentic-scaffolder) will:
- Target Septeo-specific project templates (not just Python/uv)
- Add custom actions for Septeo tooling
- Eventually expose actions as MCP tools (Phase 2)

## Project-Specific Context

- Package: `septeo_scaffolder` (src layout)
- CLI entry: `septeo-scaf`
- Python >= 3.12, managed by uv
- Same dependency stack as pyscaf: Click, Rich, Questionary, Pydantic, Jinja2, tomlkit

## Anti-Patterns

- Never bypass the ActionManager to create files directly
- Never hardcode action execution order — use `depends`/`run_preferably_after`
- Never modify another action's output in your action's lifecycle methods
- Never register actions manually — discovery is automatic via `pkgutil`
