# Review — Spec 901: Entry Point Refactoring & Shared Test Framework

## Spec Coverage Matrix

| Acceptance Criterion | Status | Evidence |
|---|---|---|
| Single entry point per package replaces per-action entries | **Implemented** | `apps/*/pyproject.toml` — single `discover_actions` callable |
| `discover_actions_from_entry_points()` works with both patterns | **Implemented** | Function already handles callable returning list (no code change needed) |
| `pyscaf_core.testing` module provides ActionTestRunner | **Implemented** | `runner.py`, `discovery.py`, `__init__.py` |
| pytest `--action-filter` option via plugin | **Implemented** | `pytest_plugin.py` + `pytest11` entry point |
| Downstream with minimal boilerplate | **Implemented** | `test_yaml_actions.py` is a single `create_yaml_tests()` call |
| All existing tests pass | **Verified** | 91/91 tests pass (68 pre-existing + 17 new core + 4 YAML + 2 security) |

## Constitution Compliance

N/A — no `CONSTITUTION.md` in this project.

## Issues Fixed (CRITICAL + HIGH)

| Category | Issue | Fix |
|---|---|---|
| **CRITICAL** — Path traversal | `_check_file_exists/contains` accepted `../` and absolute paths | Added `_resolve_safe_path()` with `resolve()` + `is_relative_to()` guard |
| **CRITICAL** — Arbitrary code exec | `_execute_custom_check` silently swallowed errors | Now raises `RuntimeError` with context; docstring warns about trust |
| **HIGH** — `cli_command` ignored | `discover_test_files_from_entry_points` dropped the `cli_command` from configs | Returns `(Path, str, str)` tuples; `create_yaml_tests` propagates to runner |
| **HIGH** — Silent exception | `_check_file_contains` caught all exceptions silently | Now catches only `OSError|UnicodeDecodeError` and raises `RuntimeError` |

## Issues to Review (MEDIUM — pending)

| Category | File | Description |
|---|---|---|
| Test coverage | `pytest_plugin.py` | No dedicated tests for `--action-filter` collection hook (works via integration) |
| Test coverage | `create_yaml_tests` | No direct unit test (tested indirectly via demo-scaf YAML tests) |
| Test coverage | `discover_test_files_from_entry_points` | No unit test with mocked entry points |
| Test coverage | `runner.py:run_test()` | No test for subprocess execution (tested indirectly via YAML integration) |
| Edge case | `discovery.py:relative_to()` | Could raise `ValueError` with symlinks; low risk in practice |
| SOLID | `ActionTestRunner` | Single class handles YAML loading, CLI building, file checks, subprocess — could extract check strategy |

## Stats

| Metric | Value |
|---|---|
| Files changed | 14 new + 6 modified |
| Lines added | ~630 (code + tests + spec) |
| Tests added | 17 unit + 4 YAML integration + 2 security = 23 |
| Total test suite | 91 passing |
| Entry points removed | 26 individual action entries |
| Entry points added | 3 `pyscaf_core.plugins` + 3 `pyscaf_core.test_yamls` + 1 `pytest11` = 7 |

## Final Checklist

| Check | Status |
|---|---|
| Code compiles and runs | PASS |
| All tests pass | PASS (91/91) |
| Linter clean | PASS |
| Security issues addressed | PASS (path traversal + error propagation) |
| Spec criteria met | PASS (6/6) |
| Backward compatibility | PASS (callable entry points already supported) |

## Verdict

**Approved** — All acceptance criteria met, critical security issues fixed, 91 tests passing.
Remaining MEDIUM items (test coverage for plugin, entry-point discovery mock) are improvements
for a follow-up iteration.
