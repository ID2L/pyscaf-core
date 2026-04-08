# F002 — `pyscaf-core` package skeleton

**Feature ID**: F002  
**Phase**: 0  
**Status**: Ready for implementation  
**Dependencies**: F001  

## Scope

Create the **library** package `packages/pyscaf-core` as an installable distribution **`pyscaf-core`** (PEP 621) with import name **`pyscaf_core`**. The package is a **skeleton**: version `0.x`, `py.typed`, and a minimal public `__init__.py` (e.g. `__version__` only). No engine code (preference chain, actions, CLI) until later phases.

**Out of scope**

- Implementing `preference_chain`, `actions`, or CLI (Phases 1–3).
- Declaring `[project.entry-points."pyscaf_core.plugins"]` in core (consumers/apps register plugins; core only documents the group name).

## Decisions

- **PyPI name**: `pyscaf-core`
- **Import package**: `pyscaf_core` under `src/pyscaf_core/`
- **Initial version**: `0.1.0` (or `0.0.1` if you prefer stricter pre-release semantics; stay on **0.x** per roadmap).

## Directory and file structure

```text
packages/pyscaf-core/
├── pyproject.toml
├── README.md                 # optional one-liner; full docs in F005 root README
└── src/
    └── pyscaf_core/
        ├── __init__.py       # __version__ = "0.1.0" (or import from importlib.metadata)
        └── py.typed          # empty marker for PEP 561
```

### `pyproject.toml` requirements

- **Build backend**: Hatchling (aligned with source projects) or another PEP 517 backend compatible with uv.
- **`[project]`**: `name = "pyscaf-core"`, `version`, `requires-python` aligned with root `.python-version`, `dependencies = []` for skeleton (Phase 1 adds `pydantic` etc.).
- **Package discovery**: `src` layout; only package `pyscaf_core`.

## Public API (skeleton)

```python
# src/pyscaf_core/__init__.py
__all__ = ["__version__"]

__version__ = "0.1.0"  # or: __version__ = metadata.version("pyscaf-core")
```

## Acceptance criteria

- [ ] `pip install -e packages/pyscaf-core` equivalent via `uv sync` installs importable `pyscaf_core`.
- [ ] `py.typed` is present so type checkers treat the package as typed.
- [ ] Distribution name is `pyscaf-core`; `python -c "import pyscaf_core; print(pyscaf_core.__version__)"` works inside the dev container.
- [ ] No dependency on Click, YAML, or Septeo-specific packages at this stage.

## Dependencies on other features

- **F001**: workspace member path and Python version.

## Validation (Docker only)

From repository root (workspace):

```bash
docker run --rm \
  -v "$PWD":/workspace -w /workspace \
  ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run python -c 'import pyscaf_core; print(pyscaf_core.__version__)'"
```

After F004 image exists:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run python -c 'import pyscaf_core; print(pyscaf_core.__version__)'"
```

## Notes

- Phase 1 (F101) will add `pydantic` to `pyscaf-core` dependencies for `Node` models.
