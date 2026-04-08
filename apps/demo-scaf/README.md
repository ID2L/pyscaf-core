# demo-scaf

A demo application built on **pyscaf-core** that showcases the plugin-based action system.

## What this demonstrates

- **Action plugins**: `HelloAction` and `ReadmeAction` show how to implement the `Action` lifecycle (skeleton, init, install)
- **Dependency ordering**: `ReadmeAction` depends on `HelloAction`, proving the preference chain works
- **CLI options**: Both actions declare `CLIOption` with different types (choice, str, bool)
- **Entry points**: Actions are registered via `[project.entry-points."pyscaf_core.plugins"]` in `pyproject.toml`
- **CLI factory**: `build_cli()` from core wires everything together with zero boilerplate

## Usage (Docker)

```bash
# From the monorepo root
docker run --rm -v "$PWD":/workspace -w /workspace ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run demo-scaf init my-project --no-install"
```

## Creating your own plugin app

1. Create a new package depending on `pyscaf-core`
2. Implement `Action` subclasses with `depends`, `cli_options`, and lifecycle hooks
3. Register them as entry points under `pyscaf_core.plugins`
4. Wire `main.py` using `build_cli()` and `make_main()`

See `src/demo_scaf/actions/` for examples.
