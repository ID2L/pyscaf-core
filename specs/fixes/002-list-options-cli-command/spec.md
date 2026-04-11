# Bug Fix Specification: List Options in ActionTestRunner CLI Command

**Fix Branch**: `fix/002-list-options-cli-command`
**Created**: 2026-04-11
**Status**: Draft
**Severity**: Medium — causes downstream workarounds
**Input**: Bug report — YAML list values serialized as Python repr instead of repeated CLI flags

## Problem Statement

`ActionTestRunner._build_cli_command()` in `pyscaf_core.testing.runner` does not handle YAML list values. When a test YAML file contains:

```yaml
cli_arguments:
  options:
    apps: [backend, frontend]
```

The runner produces `--apps "['backend', 'frontend']"` (Python list repr) instead of the Click-compatible `--apps backend --apps frontend`.

### Impact

- ~12 out of 32 downstream YAML test files use list-valued options
- `septeo-scaf` had to create a `SepteoTestRunner` subclass to work around this
- Any downstream project using `multiple=True` Click options is affected

## User Scenarios & Testing

### User Story 1 — YAML list options expand to repeated CLI flags (Priority: P0)

A downstream developer writes a YAML test with list-valued options and expects the runner to produce correct Click `multiple=True` flags.

**Why this priority**: Core functionality bug — blocks correct test execution for downstream projects.
**Independent Test**: Unit test on `_build_cli_command()` with list-valued options.

**Acceptance Scenarios**:

1. **Given** a YAML config with `options: {apps: [backend, frontend]}`, **When** `_build_cli_command()` runs, **Then** the command contains `--apps backend --apps frontend` (two separate flag pairs).
2. **Given** a YAML config with `options: {name: myproject}` (scalar), **When** `_build_cli_command()` runs, **Then** the command contains `--name myproject` (unchanged behavior).
3. **Given** a YAML config with `options: {verbose: true}` (bool), **When** `_build_cli_command()` runs, **Then** the command contains `--verbose` (unchanged behavior).
4. **Given** a YAML config with `options: {apps: []}` (empty list), **When** `_build_cli_command()` runs, **Then** no `--apps` flag is emitted.

### Edge Cases

- Empty list value → no flags emitted for that key
- Single-item list `[backend]` → `--apps backend` (one pair)
- Mixed options: bool + list + scalar in same config → all handled correctly

## Requirements

### Functional Requirements

- **FR-001**: `_build_cli_command()` MUST expand list values into repeated `--key item` pairs
- **FR-002**: Existing bool and scalar handling MUST remain unchanged
- **FR-003**: Empty lists MUST produce no flags for that key

## Success Criteria

- **SC-001**: All existing tests pass without modification
- **SC-002**: New unit test covers list expansion (multi-item, single-item, empty)
- **SC-003**: Downstream projects can remove their `SepteoTestRunner` workarounds
