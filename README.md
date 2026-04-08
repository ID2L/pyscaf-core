# pyscaf-core

**pyscaf-core** is a shared scaffolding engine for generating and evolving Python projects. This repository is a **monorepo** managed with **uv workspaces**: library code lives under `packages/`, runnable applications under `apps/`, and specifications under `specs/`.

## Layout

| Path | Role |
|------|------|
| `packages/pyscaf-core` | Installable library **`pyscaf-core`** (import: `pyscaf_core`) |
| `apps/demo-scaf` | Demo CLI app consuming the workspace library |
| `specs/` | Feature specs, roadmap, and design notes |

## Roadmap

See [specs/roadmap/roadmap.md](specs/roadmap/roadmap.md).

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) on your machine (Python toolchain and package manager).

## Development

From the repository root, sync the workspace and install all members:

```bash
uv sync --all-packages
```

Import check:

```bash
uv run python -c "import pyscaf_core; print(pyscaf_core.__version__)"
```

Run the demo app:

```bash
uv run demo-scaf
```

Lint with Ruff:

```bash
uv run ruff check .
```

Run tests:

```bash
uv run pytest -q
```

## Resolved decisions

- **PyPI distribution name**: `pyscaf-core`
- **Import package**: `pyscaf_core`
- **Plugin entry point group** (for future plugins): `pyscaf_core.plugins`
- **Versioning**: `0.x` until a stable API is declared
