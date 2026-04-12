# pyscaf-core

**pyscaf-core** is a shared scaffolding engine for generating and evolving Python projects.

This repository is a **monorepo** managed with [uv workspaces](https://docs.astral.sh/uv/): library code lives under `packages/`, runnable applications under `apps/`, and specifications under `specs/`.

## Overview

| Path | Role |
|------|------|
| `packages/pyscaf-core` | Installable library **`pyscaf-core`** (import: `pyscaf_core`) |
| `apps/demo-scaf` | Demo CLI app consuming the library |
| `apps/pyscaf` | Full-featured scaffolder for Python projects |
| `apps/septeo-scaf` | Septeo-specific project scaffolder |
| `specs/` | Feature specs, roadmap, and design notes |

## Key Features

- **Plugin-based architecture** — each scaffolding feature is an [Action](reference/actions.md) that is auto-discovered and executed in dependency order.
- **Preference chain** — a [dependency resolution algorithm](reference/preference_chain.md) that computes optimal execution order at runtime.
- **Dual-mode CLI** — supports both interactive (questionary prompts) and non-interactive (CLI flags) modes via [Click integration](reference/cli.md).
- **YAML-driven testing** — declarative test definitions for action validation via the [testing framework](reference/testing.md).
- **3-pass execution** — `skeleton()` → `init()` → `install()` lifecycle for clean separation of concerns.

## Quick Start

```bash
pip install pyscaf-core
```

Or for development, see the [Getting Started](getting-started.md) guide.

## Design Decisions

- **PyPI distribution name**: `pyscaf-core`
- **Import package**: `pyscaf_core`
- **Plugin entry point group**: `pyscaf_core.plugins`
- **Versioning**: `0.x` until a stable API is declared
