# Implementation Plan: Remove Docker, adopt native uv/uvx workflow

**Branch**: `006-remove-docker-use-uv` | **Date**: 2026-04-08 | **Spec**: [spec.md](spec.md)

## Summary

Remove all Docker infrastructure (Dockerfile, compose.yaml, .dockerignore) and rewrite the development workflow to use native `uv` commands. Add a proper `.gitignore` and update all documentation.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: uv (package manager), ruff (linter), pytest (tests)
**Testing**: pytest >= 8
**Target Platform**: macOS / Linux / Windows (developer workstations)
**Project Type**: CLI library monorepo

## Architecture Decision

This is a **simplification** — removing an abstraction layer (Docker) in favor of the native toolchain (uv). The project is a CLI tool, not a service; Docker adds overhead without benefit.

## Implementation Strategy

### Phase 1: Cleanup — Remove Docker artifacts

Delete `Dockerfile`, `compose.yaml`, `.dockerignore`. These are no longer needed.

### Phase 2: Safety net — Add .gitignore

Create a proper `.gitignore` to prevent `.venv/`, `__pycache__/`, `*.pyc`, cache dirs from being tracked. The initial commit unfortunately included some `__pycache__` dirs — they should be removed from tracking.

### Phase 3: Documentation — Rewrite README

Replace the "Development (Docker)" section with "Development" using native `uv` commands:
- `uv sync --all-packages`
- `uv run pytest -q`
- `uv run ruff check .`
- `uv run demo-scaf`

Add a "Prerequisites" section with uv installation link.

### Phase 4: Housekeeping — Update specs and todo

- Mark F004 and F005 as superseded
- Update `_todo.md` with F006 entry
- Update cursor rules if they reference Docker

### Phase 5: Validation

Run the full validation natively to confirm everything works.

## Dependencies

- uv (already configured)
- Existing pyproject.toml workspace config (no changes needed)
- Existing .python-version (no changes needed)
