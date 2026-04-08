# Feature Specification: Remove Docker, adopt native uv/uvx workflow

**Feature Branch**: `006-remove-docker-use-uv`
**Created**: 2026-04-08
**Status**: Draft
**Input**: User description: "Ce projet est un projet CLI : il ne doit pas vivre dans un docker, mais est géré par uv / uvx. Retire les compose / dockerfile, et assure toi que le projet fonctionne avec uv."

## Context

pyscaf-core is a **CLI scaffolding engine** distributed as a Python package. The previous specs (F004, F005) introduced Docker as the primary development and CI environment. This was a design mistake: a CLI tool intended for local developer use should run natively via `uv` / `uvx`, not inside containers. Docker adds unnecessary friction for contributors and end-users.

## User Scenarios & Testing

### User Story 1 — Developer sets up the project (Priority: P0)

A new contributor clones the repo and starts developing without Docker.

**Why this priority**: Core DX — if setup doesn't work, nothing else matters.
**Independent Test**: Clone repo, run `uv sync`, import check, run tests.

**Acceptance Scenarios**:

1. **Given** a fresh clone with uv installed, **When** the developer runs `uv sync --all-packages`, **Then** all workspace members install without error.
2. **Given** a synced workspace, **When** the developer runs `uv run pytest -q`, **Then** all tests pass.
3. **Given** a synced workspace, **When** the developer runs `uv run ruff check .`, **Then** lint passes with zero violations.

### User Story 2 — Developer runs the demo app (Priority: P1)

A developer wants to test the demo CLI app locally.

**Why this priority**: Validates the end-to-end CLI experience.
**Independent Test**: Run `uv run demo-scaf` after sync.

**Acceptance Scenarios**:

1. **Given** a synced workspace, **When** the developer runs `uv run demo-scaf`, **Then** the CLI starts without error.

### User Story 3 — Docker artifacts are removed (Priority: P0)

All Docker-related files are deleted and references purged from documentation.

**Why this priority**: Leaving dead Docker files causes confusion.
**Independent Test**: Verify absence of Docker files and references.

**Acceptance Scenarios**:

1. **Given** the repo after migration, **When** searching for `Dockerfile`, `compose.yaml`, `.dockerignore`, **Then** none exist.
2. **Given** the README, **When** reading the Development section, **Then** all commands use bare `uv run` without Docker wrappers.
3. **Given** the specs directory, **When** reading F004 and F005, **Then** they are marked as superseded by F006.

### Edge Cases

- What if a contributor doesn't have uv installed? → README must include uv installation instructions.
- What if .python-version specifies a Python not available? → uv handles Python installation automatically.
- What about CI pipelines? → Out of scope for now; CI will use `uv` natively when added later.

## Requirements

### Functional Requirements

- **FR-001**: System MUST remove `Dockerfile`, `compose.yaml`, and `.dockerignore` from the repository root.
- **FR-002**: System MUST update `README.md` to replace all Docker-based commands with native `uv` commands.
- **FR-003**: System MUST include uv installation instructions in `README.md`.
- **FR-004**: System MUST add a `.gitignore` at repo root excluding `.venv/`, `__pycache__/`, `*.pyc`, `.ruff_cache/`, `.pytest_cache/`.
- **FR-005**: System MUST verify that `uv sync --all-packages`, `uv run ruff check .`, and `uv run pytest -q` all succeed natively.
- **FR-006**: System MUST mark specs F004 and F005 as superseded by F006.
- **FR-007**: System MUST update `_todo.md` to reflect this migration.
- **FR-008**: System MUST update any cursor rules referencing Docker (if any).

## Success Criteria

- **SC-001**: A new contributor can set up the project in under 2 minutes with only `uv` installed, no Docker required.
- **SC-002**: All existing tests pass when run via `uv run pytest -q`.
- **SC-003**: Zero Docker-related files remain in the repository.
- **SC-004**: README development section contains exclusively `uv`-based commands.
- **SC-005**: `.gitignore` prevents committing build artifacts and virtual environments.

## Assumptions

- uv is the standard tool for this project (already configured in pyproject.toml with workspace support).
- The `.python-version` file (3.12) is sufficient for uv to manage the Python version.
- No CI/CD pipelines currently exist that depend on Docker.
