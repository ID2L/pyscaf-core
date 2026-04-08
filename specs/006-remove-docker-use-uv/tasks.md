# Tasks: Remove Docker, adopt native uv/uvx workflow

## Phase 1: Cleanup (Remove Docker artifacts)

**Purpose**: Delete all Docker-related files

- [X] T001 Delete `Dockerfile` from repo root
- [X] T002 Delete `compose.yaml` from repo root
- [X] T003 Delete `.dockerignore` from repo root

## Phase 2: Safety net (.gitignore)

**Purpose**: Prevent build artifacts from being tracked

- [X] T004 Create `.gitignore` at repo root with Python/uv exclusions
- [X] T005 Remove `__pycache__/` and `*.pyc` files from git tracking

## Phase 3: Documentation (README rewrite)

**Purpose**: Replace Docker-based workflow with native uv workflow

- [X] T006 Rewrite README.md "Development" section with native uv commands
- [X] T007 Add "Prerequisites" section with uv install link
- [X] T008 Remove all Docker references from README.md

## Phase 4: Housekeeping (Specs and meta)

**Purpose**: Keep project metadata consistent

- [X] T009 [P] Add superseded notice to `specs/004-docker-dev-ci/spec.md`
- [X] T010 [P] Add superseded notice to `specs/005-readme-docker-docs/spec.md`
- [X] T011 [P] Update `_todo.md` with F006 migration entry
- [X] T012 [P] Check and update `.cursor/rules/` if any reference Docker (N/A — verified no Docker refs)

**Checkpoint**: All files updated, Docker fully removed

## Phase 5: Validation

**Purpose**: Confirm everything works natively with uv

- [X] T013 Run `uv sync --all-packages` and verify success
- [X] T014 Run `uv run python -c "import pyscaf_core; print(pyscaf_core.__version__)"` and verify output
- [X] T015 Run `uv run demo-scaf` and verify it starts (`--help` used for non-interactive check)
- [X] T016 Run `uv run ruff check .` and verify zero violations
- [X] T017 Run `uv run pytest -q` and verify all tests pass

## Dependency Graph

Cleanup (Phase 1) → Safety net (Phase 2) → Documentation (Phase 3) → Housekeeping (Phase 4) → Validation (Phase 5)

## Summary

- Total tasks: 17
- By priority: P0=5 (T001-T005), P1=8 (T006-T012, T013), P2=4 (T014-T017)
- Estimated effort: ~30 minutes
