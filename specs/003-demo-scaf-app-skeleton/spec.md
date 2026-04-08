# F003 — `demo-scaf` app skeleton (path dependency on core)

**Feature ID**: F003  
**Phase**: 0  
**Status**: Ready for implementation  
**Dependencies**: F002  

## Scope

Add **`apps/demo-scaf`**, a minimal **demo/hello-world** application that depends on the workspace library **`pyscaf-core`** via a **path dependency** (uv workspace). Ship a **console script stub** that exits successfully or prints a placeholder message; full CLI wiring to `pyscaf_core` happens in Phase 4 (F401–F403).

**Naming**

- **App / distribution name** (suggested): `demo-scaf` or `pyscaf-demo-scaf` — choose one and use consistently in `[project.scripts]`.
- **Python package** under `src/`: e.g. `demo_scaf` (snake_case).

**Out of scope**

- Real plugin actions, entry points `pyscaf_core.plugins`, or Click commands (Phase 4).
- Duplicating engine code from `pyscaf` or Septeo repos.

## Directory and file structure

```text
apps/demo-scaf/
├── pyproject.toml
└── src/
    └── demo_scaf/
        ├── __init__.py
        └── main.py              # stub: def main() -> None: ...
```

### `pyproject.toml` requirements

- **Dependency on core**: path dependency to `../../packages/pyscaf-core` (or uv workspace-relative form per uv docs, e.g. `{ workspace = true }` if the member is named in the workspace).
- **`[project.scripts]`**: e.g. `demo-scaf = "demo_scaf.main:main"` (name can be `demo-scaf` with hyphen in console script key).

### Stub `main`

```python
# src/demo_scaf/main.py
def main() -> None:
    import pyscaf_core
    print(f"demo-scaf stub; pyscaf-core {pyscaf_core.__version__}")
```

**Note**: For alignment with roadmap Phase 2+, prefer **`logging`** over `print` in any **core** code; a demo app stub may use `print` for UX until F402/F403. Optionally use logging in the stub for consistency.

## Acceptance criteria

- [ ] `uv sync --all-packages` at repo root installs `demo-scaf` and `pyscaf-core` editable.
- [ ] Console script is on `PATH` when using `uv run`: e.g. `uv run demo-scaf` prints stub output including core version.
- [ ] No circular dependency: app depends on core only; core does not depend on app.

## Dependencies on other features

- **F002**: `pyscaf_core` must exist and expose `__version__`.

## Validation (Docker only)

```bash
docker run --rm \
  -v "$PWD":/workspace -w /workspace \
  ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv sync --all-packages && uv run demo-scaf"
```

With F004 image:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run demo-scaf"
```

Expected: non-zero success; output references `pyscaf-core` version.

## Notes

- Roadmap Phase 4 replaces this stub with real plugin demo (2–3 actions) and `pyscaf_core.plugins` entry points.
