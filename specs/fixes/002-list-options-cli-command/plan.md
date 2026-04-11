# Implementation Plan: List Options in ActionTestRunner CLI Command

**Branch**: `fix/002-list-options-cli-command` | **Date**: 2026-04-11 | **Spec**: `spec.md`

## Summary

Add `isinstance(value, list)` branch in `_build_cli_command()` to expand YAML list values into repeated `--key item` CLI flags, matching Click's `multiple=True` convention.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PyYAML (already present), Click (downstream)
**Testing**: pytest
**Project Type**: Library (pyscaf-core package)

## Architecture Decision

Minimal, surgical fix — add one `elif` branch in the existing type-dispatch chain. No new classes, no API changes, full backward compatibility.

## Files Changed

| File | Change |
|------|--------|
| `packages/pyscaf-core/src/pyscaf_core/testing/runner.py` | Add `elif isinstance(value, list)` branch in `_build_cli_command()` |
| `packages/pyscaf-core/tests/testing/test_runner_cli_command.py` | New unit test file for `_build_cli_command()` list handling |

## Implementation Strategy

### Phase 1: Fix

1. Add list type check between bool and scalar branches in `_build_cli_command()`
2. For each item in the list, emit `--key item`

### Phase 2: Test

1. Create focused unit test for `_build_cli_command()` covering:
   - Multi-item list → repeated flags
   - Single-item list → one flag pair
   - Empty list → no flags
   - Mixed options (bool + list + scalar)
   - Existing behavior preserved (bool, scalar)

## Dependencies

None — pure logic change with no new dependencies.
