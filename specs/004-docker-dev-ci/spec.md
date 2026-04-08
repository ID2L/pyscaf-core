# F004 — Docker dev/CI image: uv, ruff, pytest

**Feature ID**: F004  
**Phase**: 0  
**Status**: Ready for implementation  
**Dependencies**: F001 (and preferably F002–F003 so sync runs meaningfully)  

## Scope

Provide a **single reproducible environment** for developers and CI: Python + `uv`, dependencies synced from the workspace, and commands for **Ruff** and **pytest**. All documented project commands for lint/test must be runnable **inside Docker** (per project policy).

**Deliverables** (choose one primary; both are acceptable):

1. **`Dockerfile`** at repo root (multi-stage optional) installing uv, copying the repo, running `uv sync --all-packages`, default `CMD` or documented `docker run … sh -c "…"`.
2. **`compose.yaml`** (optional) defining a `dev` service that mounts the workspace read-write for live editing.

**Tooling versions**

- **Ruff**: configured via `pyproject.toml` (`[tool.ruff]`) at root or per-package; F004 ensures `uv run ruff check .` works from workspace root inside the image.
- **pytest**: minimal `pytest.ini` or `[tool.pytest.ini_options]` in root or `packages/pyscaf-core`; zero tests is OK at Phase 0 exit.

**Out of scope**

- Publishing images to a registry (optional follow-up).
- Full GitHub Actions / Azure Pipelines YAML (optional stub: a one-line comment in README pointing to future CI; F005 documents the Docker contract).

## Directory and file structure

```text
pyscaf-core/
├── Dockerfile
├── compose.yaml              # optional
├── .dockerignore             # exclude .git, __pycache__, .venv on host if bind-mounting
└── pyproject.toml            # [tool.ruff], [tool.pytest.ini_options] as needed
```

### `Dockerfile` sketch (illustrative)

```dockerfile
FROM ghcr.io/astral-sh/uv:python3.12-bookworm
WORKDIR /workspace
COPY . .
RUN uv sync --all-packages
# Default: run tests
CMD ["uv", "run", "pytest", "-q"]
```

Adjust `COPY` vs bind-mount strategy: for **CI**, `COPY` is typical; for **local dev**, README (F005) should show `docker run -v "$PWD":/workspace …`.

## Acceptance criteria

- [ ] Image builds from repo root: `docker build -t pyscaf-core-dev .`
- [ ] Inside a container with workspace mounted at `/workspace`, `uv sync --all-packages` succeeds.
- [ ] `uv run ruff check .` completes (fix any initial violations or scope paths to exclude `specs/` if agreed).
- [ ] `uv run pytest` completes with **0 tests** or empty collection without error.
- [ ] `.dockerignore` prevents large or sensitive paths from slowing builds (at minimum `__pycache__`, `.venv`, `.git` optional).

## Dependencies on other features

- **F001**: workspace layout and lockfile.
- **F002–F003**: recommended so sync installs real members; F004 can land in same PR as F001–F003.

## Validation (Docker only)

Build and test:

```bash
cd /path/to/pyscaf-core
docker build -t pyscaf-core-dev .
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run ruff check . && uv run pytest -q"
```

Optional Compose:

```bash
docker compose run --rm dev sh -c "uv sync --all-packages && uv run ruff check . && uv run pytest -q"
```

## Notes

- Pin base image digest in CI for reproducibility when adding workflows later.
- Ensure Python version in Dockerfile matches `.python-version`.
