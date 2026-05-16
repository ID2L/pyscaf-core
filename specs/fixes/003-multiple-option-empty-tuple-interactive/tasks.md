# Tasks: Fix Empty Tuple Skips Interactive Prompt

## Phase 1: Foundation

**Purpose**: Create the helper function and its unit tests (TDD — test first)

- [ ] T001 Write unit tests for `_is_unanswered()` helper in `packages/pyscaf-core/tests/actions/test_manager.py`
- [ ] T002 Implement `_is_unanswered()` helper in `packages/pyscaf-core/src/pyscaf_core/actions/manager.py`

## Phase 2: Fix Interactive Guard

**Purpose**: Fix `ask_interactive_questions()` to treat empty tuples as unanswered

- [ ] T003 Write test `test_ask_interactive_shows_prompt_for_empty_tuple` in `packages/pyscaf-core/tests/actions/test_manager.py`
- [ ] T004 Write test `test_ask_interactive_skips_prompt_for_nonempty_tuple` in `packages/pyscaf-core/tests/actions/test_manager.py`
- [ ] T005 Update guard in `ask_interactive_questions()` (line 92) to use `_is_unanswered()` in `packages/pyscaf-core/src/pyscaf_core/actions/manager.py`

**Checkpoint**: Interactive mode works correctly for multiple=True options

## Phase 3: Fix Postfill Hook Guard

**Purpose**: Ensure consistency between postfill hooks and interactive guard

- [ ] T006 Write test `test_postfill_hook_skips_for_empty_tuple` in `packages/pyscaf-core/tests/actions/test_manager.py`
- [ ] T007 Write test `test_postfill_hook_runs_for_nonempty_tuple` in `packages/pyscaf-core/tests/actions/test_manager.py`
- [ ] T008 Update guard in `run_postfill_hooks()` (line 78) to use `_is_unanswered()` in `packages/pyscaf-core/src/pyscaf_core/actions/manager.py`

**Checkpoint**: Both methods use consistent "is answered" logic

## Phase 4: Validation

**Purpose**: Full test suite pass, no regressions

- [ ] T009 Run full test suite (`uv run pytest`) and verify zero regressions

## Dependency Graph

T001 → T002 → T003/T004 (parallel) → T005 → T006/T007 (parallel) → T008 → T009

## Summary

- Total tasks: 9
- By priority: P0=5 (T001-T005), P1=3 (T006-T008), P2=1 (T009)
- Estimated effort: ~1h (human), ~5min (AI)
