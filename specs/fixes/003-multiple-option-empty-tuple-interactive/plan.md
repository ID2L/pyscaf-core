# Implementation Plan: Fix Empty Tuple Skips Interactive Prompt

**Branch**: `fix/003-multiple-option-empty-tuple-interactive` | **Date**: 2026-05-15 | **Spec**: [spec.md](./spec.md)

## Summary

Extract a shared helper function `_is_unanswered()` that treats `None`, `()`, and `[]` as unanswered values. Apply it in both `ask_interactive_questions()` and `run_postfill_hooks()` guards.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Click 8.x, Questionary 2.x, Pydantic 2.x
**Testing**: pytest 8.x
**Project Type**: Library (pyscaf-core)

## Architecture Decision

**Approach**: Extract a module-level helper rather than inline the check twice.

**Rationale**:
- DRY — the "is this value answered?" semantic appears in two methods
- Single source of truth for the definition of "unanswered"
- Easy to extend if new "empty" sentinels appear (e.g. `frozenset()`)
- Testable in isolation

**Alternatives considered**:
1. Inline `value is not None and value != () and value != []` in both methods — rejected (DRY violation)
2. Normalize empty tuples to `None` in `add_dynamic_options` / Click layer — rejected (too invasive, changes Click's contract)
3. Override Click's default for `multiple=True` — rejected (Click does not support this cleanly)

## Affected Files

| File | Change |
|------|--------|
| `packages/pyscaf-core/src/pyscaf_core/actions/manager.py` | Add `_is_unanswered()` helper; update guards in `ask_interactive_questions()` and `run_postfill_hooks()` |
| `packages/pyscaf-core/tests/actions/test_manager.py` | Add tests for empty-tuple and empty-list scenarios |

## Implementation Strategy

### Phase 1: Helper Function

Add a module-level helper in `manager.py`:

```python
def _is_unanswered(value: Any) -> bool:
    """Return True if the value represents an unanswered CLI option.

    Click sets multiple=True defaults to () rather than None.
    Both () and [] should be treated as "not yet answered".
    """
    if value is None:
        return True
    if isinstance(value, (tuple, list)) and len(value) == 0:
        return True
    return False
```

### Phase 2: Apply in Guards

In `ask_interactive_questions()` (line 92):
```python
# Before
if context.get(context_key) is not None:
    continue

# After
if not _is_unanswered(context.get(context_key)):
    continue
```

In `run_postfill_hooks()` (line 78):
```python
# Before
if context.get(context_key) is None:
    continue

# After
if _is_unanswered(context.get(context_key)):
    continue
```

### Phase 3: Tests

Add test cases in `test_manager.py`:
- `test_ask_interactive_shows_prompt_for_empty_tuple` — verifies checkbox shown when value is `()`
- `test_ask_interactive_skips_prompt_for_nonempty_tuple` — verifies checkbox NOT shown when value is `("a", "b")`
- `test_postfill_hook_skips_for_empty_tuple` — verifies hook NOT run when value is `()`
- `test_postfill_hook_runs_for_nonempty_tuple` — verifies hook runs when value is `("a",)`

## Dependencies

None — no new packages needed.

## Risk Assessment

**Low risk**:
- Change is surgical (2 guard conditions + 1 helper)
- Existing tests cover all non-tuple paths
- New tests cover the tuple-specific paths
- Fully backward compatible
