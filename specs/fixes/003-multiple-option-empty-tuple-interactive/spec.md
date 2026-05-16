# Bug Fix Specification: Empty Tuple Skips Interactive Prompt for multiple=True Options

**Fix Branch**: `fix/003-multiple-option-empty-tuple-interactive`
**Created**: 2026-05-15
**Status**: Draft
**Severity**: High — interactive mode completely broken for multi-select options
**Input**: Bug report from septeo-agentic-scaffolder KNOWN_ISSUES.md

## Problem Statement

When Click registers an option with `multiple=True`, the default value is `()` (empty tuple) instead of `None`. In `ActionManager.ask_interactive_questions()`, the guard at line 92:

```python
if context.get(context_key) is not None:
    continue
```

treats `()` as a truthy, non-None value and skips the interactive prompt. The user never sees the checkbox for multi-select options like `--bricks`.

The same issue exists in `run_postfill_hooks()` at line 78 where the guard:

```python
if context.get(context_key) is None:
    continue
```

incorrectly runs postfill hooks on empty tuples (minor, but inconsistent).

### Root Cause

Click's `multiple=True` injects `()` as the default value into the context dict. Python's `() is not None` evaluates to `True`, so the "already answered" guard fires incorrectly.

### Impact

- Every downstream project using `multiple=True` CLI options in interactive mode is broken
- `septeo-agentic-scaffolder` had to implement a per-action workaround (`_set_default_bricks`)
- Affects all `questionary.checkbox`-based prompts

## User Scenarios & Testing

### User Story 1 — Interactive prompt shown for multiple=True options (Priority: P0)

A downstream developer defines a CLI option with `multiple=True` and `type="choice"`. In interactive mode, the user should see a checkbox prompt.

**Why this priority**: Core interactive workflow completely broken for multi-select options.
**Independent Test**: Unit test on `ask_interactive_questions()` with empty-tuple context value.

**Acceptance Scenarios**:

1. **Given** a context with `bricks=()` (Click default for multiple=True), **When** `ask_interactive_questions()` runs, **Then** the checkbox prompt IS shown (empty tuple treated as unanswered).
2. **Given** a context with `bricks=("frontend", "backend")` (user provided values), **When** `ask_interactive_questions()` runs, **Then** the checkbox prompt is NOT shown (non-empty tuple treated as answered).
3. **Given** a context with `bricks=None`, **When** `ask_interactive_questions()` runs, **Then** the checkbox prompt IS shown (None treated as unanswered — existing behavior preserved).
4. **Given** a context with `name="myproject"` (scalar value), **When** `ask_interactive_questions()` runs, **Then** the text prompt is NOT shown (existing behavior preserved).

### User Story 2 — Postfill hooks consistent with interactive guard (Priority: P1)

`run_postfill_hooks()` should use the same "is answered" logic as `ask_interactive_questions()`.

**Why this priority**: Consistency — prevents subtle bugs where hooks run on empty tuples.
**Independent Test**: Unit test on `run_postfill_hooks()` with empty-tuple context value.

**Acceptance Scenarios**:

1. **Given** a context with `bricks=()`, **When** `run_postfill_hooks()` runs, **Then** the postfill hook is NOT executed (empty tuple = unanswered).
2. **Given** a context with `bricks=("frontend",)`, **When** `run_postfill_hooks()` runs, **Then** the postfill hook IS executed (non-empty tuple = answered).

### Edge Cases

- Context key missing entirely → treated as unanswered (existing behavior)
- Context key set to `False` or `0` → treated as answered (existing behavior, these are valid values)
- Context key set to empty string `""` → treated as answered (existing behavior)
- Context key set to empty list `[]` → treated as unanswered (same semantic as empty tuple)

## Requirements

### Functional Requirements

- **FR-001**: `ask_interactive_questions()` MUST treat `()` and `[]` as unanswered values (same as `None`)
- **FR-002**: `run_postfill_hooks()` MUST treat `()` and `[]` as unanswered values (same as `None`)
- **FR-003**: Non-empty tuples and lists MUST be treated as answered values
- **FR-004**: Existing behavior for `None`, `str`, `int`, `bool` values MUST be preserved

## Success Criteria

- **SC-001**: All existing tests pass without modification
- **SC-002**: New unit tests cover empty-tuple and empty-list scenarios for both methods
- **SC-003**: Downstream projects can remove their `_set_default_bricks` workarounds
