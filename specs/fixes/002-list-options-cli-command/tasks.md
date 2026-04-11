# Tasks: List Options in ActionTestRunner CLI Command

## Phase 1: Fix (Blocking)

**Purpose**: Correct the list handling in `_build_cli_command()`

- [X] T001 Add `elif isinstance(value, list)` branch in `_build_cli_command()` in `packages/pyscaf-core/src/pyscaf_core/testing/runner.py`

## Phase 2: Tests

**Purpose**: Verify the fix and prevent regression

- [X] T002 Add unit tests for list expansion in `packages/pyscaf-core/tests/testing/test_runner.py`
- [X] T003 Run full test suite to confirm no regression (73 passed, 1 pre-existing failure)

**Checkpoint**: Fix verified, all tests green

## Phase 3: Validation

- [X] T004 Run ruff linter on changed files (no new issues)

## Dependency Graph

T001 → T002 → T003 → T004

## Summary

- Total tasks: 4
- Estimated effort: ~15 minutes
