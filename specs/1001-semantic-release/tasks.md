# Tasks: Semantic Release for pyscaf-core

## Phase 1: Configuration

**Purpose**: Add semantic release config to the repo

- [X] T001 Add `python-semantic-release>=9.21.1` to root dev dependencies in `pyproject.toml`
- [X] T002 Add `[tool.semantic_release]` section to root `pyproject.toml` with monorepo paths
- [X] T003 Verify `__version__` exists in `packages/pyscaf-core/src/pyscaf_core/__init__.py`

## Phase 2: GitHub Workflows

**Purpose**: Create CI/CD workflows for automated release

- [X] T004 [P] Create `.github/workflows/release.yml` (auto-release + TestPyPI)
- [X] T005 [P] Create `.github/workflows/deploy-production-manual.yml` (manual prod deploy)

## Phase 3: Bookkeeping

- [X] T006 Update `_todo.md` with Phase 10 entry
- [X] T007 Run linter validation (ruff)

## Dependency Graph

Configuration (Phase 1) → Workflows (Phase 2) → Bookkeeping (Phase 3)

## Summary

- Total tasks: 7
- Estimated effort: ~30min AI / ~2h human
