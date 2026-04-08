# F001 — Root uv workspace, lockfile, shared Python version

**Feature ID**: F001  
**Phase**: 0  
**Status**: Ready for implementation  
**Dependencies**: None  

## Scope

Establish the monorepo root so `uv` can resolve a **workspace** of multiple packages, pin a single Python version, and produce a **root lockfile** (`uv.lock`). No application or library source code beyond what is required for the workspace to resolve (empty members may use minimal stubs if needed until F002/F003 add real packages).

**Out of scope**

- Implementing `pyscaf_core` modules (F002).
- Docker image definition (F004) — this spec only ensures the tree is valid for `uv sync` inside a container later.
- CI workflow files (optional stub only if required by F004; prefer F004 to own CI recipe).

## Decisions (from roadmap)

- **Distribution**: `pyscaf-core` on PyPI; import package `pyscaf_core` (enforced in F002).
- **Versioning**: workspace starts at **0.x** for core (e.g. `0.1.0` in F002).

## Directory and file structure

```text
pyscaf-core/
├── .python-version          # e.g. 3.12 (single line)
├── pyproject.toml           # [tool.uv.workspace] members
├── uv.lock                  # generated; committed after first successful lock
└── specs/                   # existing; unchanged by this task
```

### Root `pyproject.toml` (required sections)

- **`[project]`** — minimal metadata for the **workspace root** if uv requires it; common pattern is a `name` like `pyscaf-core-workspace` with `version = "0.0.0"` and no publish intent, **or** follow uv docs for a virtual workspace root. Prefer whatever `uv` documents as the canonical workspace-only root for 2025/2026.
- **`[tool.uv.workspace]`** — `members` including at minimum:
  - `packages/pyscaf-core`
  - `apps/demo-scaf`
- **Dev dependency groups** (optional at F001): ruff, pytest can be declared at root or deferred to F002/F004; if absent, F004 must add them.

## Acceptance criteria

- [ ] `.python-version` matches the Python series used in Docker (F004); document the chosen version in this spec’s “Python version” note (e.g. `3.12`).
- [ ] Root `pyproject.toml` defines `[tool.uv.workspace]` with `packages/pyscaf-core` and `apps/demo-scaf` as members.
- [ ] `uv.lock` exists at repo root after a successful lock (may be generated in Docker per validation below).
- [ ] No duplicate/conflicting workspace roots; `uv sync` at repo root succeeds once F002/F003 add valid member `pyproject.toml` files (F001 can land first with placeholder members only if the team agrees to a two-step PR; **preferred**: implement F001 together with minimal member `pyproject.toml` stubs so lock succeeds in one change).

## Dependencies on other features

- **None**.

## Validation (Docker only)

All commands run **inside** a container; do not document host `uv` as the primary path.

**Option A — official uv image** (adjust image tag to match `.python-version`):

```bash
docker run --rm \
  -v "$PWD":/workspace -w /workspace \
  ghcr.io/astral-sh/uv:python3.12-bookworm \
  sh -c "uv lock && uv sync --all-packages"
```

**Option B — after F004 adds `Dockerfile`**, from repo root:

```bash
docker build -t pyscaf-core-dev -f Dockerfile .
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv lock && uv sync --all-packages"
```

Expected: exit code `0`; `uv.lock` created or updated deterministically.

## Notes

- If F001 is merged before F002/F003, temporary empty member packages with minimal `pyproject.toml` are acceptable to keep `uv lock` green; remove placeholders when real specs are implemented.
