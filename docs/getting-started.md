# Getting Started

## Prerequisites

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) — the Python toolchain and package manager used by this project.

## Installation (Development)

Clone the repository and sync the workspace:

```bash
git clone https://github.com/ID2L/pyscaf-core.git
cd pyscaf-core
uv sync --all-packages
```

Verify the installation:

```bash
uv run python -c "import pyscaf_core; print(pyscaf_core.__version__)"
```

## Running Tests

All tests across the monorepo:

```bash
uv run pytest -q
```

Filter by action name (uses the built-in `--action-filter` pytest plugin):

```bash
uv run pytest --action-filter="core:test_default" -v
```

## Linting

```bash
uv run ruff check .
```

## Running the Demo App

```bash
uv run demo-scaf init my-project --interactive
```

This launches the interactive scaffolder using the demo actions (`HelloAction`, `ReadmeAction`).

## Project Structure

```
pyscaf-core/
├── packages/
│   └── pyscaf-core/          # The library (pyscaf_core)
│       ├── src/pyscaf_core/
│       └── tests/
├── apps/
│   ├── demo-scaf/            # Demo CLI app
│   ├── pyscaf/               # Full Python scaffolder
│   └── septeo-scaf/          # Septeo-specific scaffolder
├── specs/                    # Feature specifications
├── pyproject.toml            # Root workspace config
└── mkdocs.yml                # Documentation config
```

## Building the Documentation

Preview the docs locally:

```bash
uv run mkdocs serve
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

Build the static site:

```bash
uv run mkdocs build
```

## Next Steps

- Read the [Architecture](architecture.md) guide to understand the plugin system
- Learn how to [create a new action](creating-actions.md)
- Browse the [API Reference](reference/index.md)
