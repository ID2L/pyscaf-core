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

## Development (Docker)

Run all Python, uv, and tooling commands **inside Docker** from the repository root (`$PWD` = repo root).

Sync the workspace and install all members:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages"
```

Import check:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run python -c \"import pyscaf_core; print(pyscaf_core.__version__)\""
```

Run the demo app:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run demo-scaf"
```

Lint with Ruff:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run ruff check ."
```

Run tests:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run pytest -q"
```

Full validation (sync, import, demo, ruff, pytest):

```bash
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run python -c 'import pyscaf_core; print(pyscaf_core.__version__)' && uv run demo-scaf && uv run ruff check . && uv run pytest -q"
```

Optional: build and use the local dev image (after `Dockerfile` is present):

```bash
docker build -t pyscaf-core-dev .
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev
```

Optional Compose service:

```bash
docker compose run --rm dev sh -c "uv sync --all-packages && uv run pytest -q"
```

## Resolved decisions

- **PyPI distribution name**: `pyscaf-core`
- **Import package**: `pyscaf_core`
- **Plugin entry point group** (for future plugins): `pyscaf_core.plugins`
- **Versioning**: `0.x` until a stable API is declared
