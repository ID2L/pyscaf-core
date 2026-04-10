# Implementation Plan: Semantic Release for pyscaf-core

**Branch**: `1001-semantic-release` | **Date**: 2025-04-09 | **Spec**: spec.md

## Summary

Add python-semantic-release configuration and GitHub Actions workflows to automate versioning
and publishing of the `pyscaf-core` package, following the proven pattern from open-pyscaf.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: python-semantic-release >= 9.21.1
**Build**: hatchling (already configured)
**Target**: PyPI / TestPyPI
**Project Type**: Library (monorepo — only `packages/pyscaf-core` is published)

## Architecture Decision

Configuration lives at the **repo root** (`pyproject.toml`) because python-semantic-release
reads from the working directory. The `version_toml` and `version_variables` directives
point into `packages/pyscaf-core/`.

The `build_command` must `cd` into the package directory to build only pyscaf-core.

## Key Differences with open-pyscaf

| Aspect | open-pyscaf | pyscaf-core |
|--------|-------------|-------------|
| Layout | Single-package | Monorepo (uv workspace) |
| version_toml | `pyproject.toml:project.version` | `packages/pyscaf-core/pyproject.toml:project.version` |
| version_variables | `src/pyscaf/__init__.py:__version__` | `packages/pyscaf-core/src/pyscaf_core/__init__.py:__version__` |
| build_command | `pip install uv && uv build` | `pip install uv && cd packages/pyscaf-core && uv build` |

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `pyproject.toml` (root) | Modify | Add `[tool.semantic_release]` + dev dep |
| `.github/workflows/release.yml` | Create | Auto-release on push to main |
| `.github/workflows/deploy-production-manual.yml` | Create | Manual prod PyPI deploy |

## GitHub / PyPI Setup Reminder

### GitHub Repository Settings

1. **Settings → Secrets and variables → Actions**:
   - `TEST_PYPI_PASSWORD` — TestPyPI API token
   - `PYPI_PASSWORD` — Production PyPI API token

2. **Settings → Actions → General → Workflow permissions**:
   - "Read and write permissions" must be enabled (for tag/release creation)

### TestPyPI (https://test.pypi.org)

1. Create an account (or use existing)
2. Go to **Account Settings → API tokens**
3. Create token with scope "Entire account" (or project-specific once first publish succeeds)
4. **Important**: register the project name `pyscaf-core` if not already taken

### Production PyPI (https://pypi.org)

1. Create an account (or use existing)
2. Go to **Account Settings → API tokens**
3. Create token with scope "Entire account" (or project-specific once first publish succeeds)
4. **Important**: register the project name `pyscaf-core` if not already taken
