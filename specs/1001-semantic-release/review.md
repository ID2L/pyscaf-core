# Review: Semantic Release for pyscaf-core

**Spec**: `specs/1001-semantic-release/`
**Date**: 2025-04-09
**Reviewer**: AI (Claude 4.6 Opus)

## Spec Coverage Matrix

| User Story | Status | Notes |
|-----------|--------|-------|
| US1 — Auto-release on push to main | Implemented | `release.yml` triggers on push to main, runs semantic-release, publishes to TestPyPI |
| US2 — Manual deploy to prod PyPI | Implemented | `deploy-production-manual.yml` with workflow_dispatch |

## Requirements Compliance

| Requirement | Status | Evidence |
|------------|--------|----------|
| FR-001 — `[tool.semantic_release]` config with monorepo paths | ✅ Pass | `pyproject.toml` L31-97; `version_toml` and `version_variables` point to `packages/pyscaf-core/` |
| FR-002 — `release.yml` workflow | ✅ Pass | `.github/workflows/release.yml` — checkout, semantic-release, publish, artifact upload, TestPyPI deploy |
| FR-003 — `deploy-production-manual.yml` workflow | ✅ Pass | `.github/workflows/deploy-production-manual.yml` — workflow_dispatch, latest release download, PyPI publish |
| FR-004 — Dev dependency | ✅ Pass | `pyproject.toml` L8: `python-semantic-release>=9.21.1` |
| FR-005 — Build only pyscaf-core | ✅ Pass | `build_command = "pip install uv && cd packages/pyscaf-core && uv build --out-dir ../../dist"` |

## Issues to Fix (CRITICAL + HIGH)

None.

## Issues to Review (MEDIUM)

### M-001: Python version alignment

Workflows use Python 3.12 (matching project `requires-python`), while the reference project
uses 3.10. This is intentional — the python-semantic-release action only needs Python to run
the tool, not the project's target version. **No action needed** but worth noting.

### M-002: `uv build` in CI without workspace context

The `build_command` does `cd packages/pyscaf-core && uv build`. In CI, `uv build` should
work since it only needs `pyproject.toml` and the source tree — it does not install dependencies.
However, if `pyscaf-core` has workspace-specific build hooks in the future, this might need
adjustment. **No action needed now.**

### M-003: Version consistency

Current version is `0.1.0` in both `packages/pyscaf-core/pyproject.toml` and
`packages/pyscaf-core/src/pyscaf_core/__init__.py`. These are in sync. ✅

## Security Review

| Check | Status |
|-------|--------|
| No secrets in committed files | ✅ Pass |
| Secrets referenced via `${{ secrets.* }}` | ✅ Pass |
| Workflow permissions minimized | ✅ Pass (`contents: write` only on release job) |
| No `pull_request_target` risk | ✅ Pass (triggers only on `push`) |

## Final Checklist

- [X] Spec coverage: all user stories implemented
- [X] All requirements met
- [X] No security issues
- [X] No breaking changes
- [X] Lint passes (0 errors)
- [X] Version files in sync
- [X] `_todo.md` updated

## Verdict

**Approved** — Implementation is complete, follows the reference project's proven pattern with
correct monorepo adaptations. Ready to merge.
