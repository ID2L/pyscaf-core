# Spec 901 — Entry Point Refactoring & Shared Test Framework

## Problem

1. **Action entry points are verbose**: Each action requires its own entry in `pyproject.toml` (8 lines for pyscaf-app). Adding/removing an action requires editing pyproject.toml.
2. **No shared test infrastructure**: Each downstream package must implement its own test runner for YAML-driven action tests, duplicating the logic from pyscaf.

## Solution

### 1. Single Action Entry Point

Replace per-action entry points with a single callable per package:

```toml
# Before (8 entries)
[project.entry-points."pyscaf_core.plugins"]
core = "pyscaf_app.actions.core:CoreAction"
git = "pyscaf_app.actions.git:GitAction"
# ... 6 more

# After (1 entry)
[project.entry-points."pyscaf_core.plugins"]
pyscaf_app = "pyscaf_app.actions:discover_actions"
```

The existing `discover_actions_from_entry_points()` already handles callables that return lists — no core logic change needed.

### 2. Shared Testing Framework (`pyscaf_core.testing`)

A new module in pyscaf-core providing:

- **`ActionTestRunner`**: Runs YAML test specs (build CLI command, execute, check results)
- **`discover_test_files(base_dir)`**: Scans directory for `*.yaml` test files
- **`discover_test_files_from_entry_points()`**: Discovers YAML dirs via `pyscaf_core.test_yamls` entry points
- **`create_yaml_tests(cli_command, yaml_dir)`**: Returns a parametrized pytest function
- **pytest plugin** (`pytest11` entry point): Provides `--action-filter` option

### 3. Test YAML Entry Points

New entry point group `pyscaf_core.test_yamls`:

```toml
[project.entry-points."pyscaf_core.test_yamls"]
pyscaf_app = "pyscaf_app.testing:get_test_config"
```

The callable returns an `ActionTestConfig(yaml_dir=Path, cli_command=str)`.

### 4. Downstream Usage

A downstream package needs only:

```python
# tests/test_actions.py (entire file)
from pyscaf_core.testing import create_yaml_tests
test_action = create_yaml_tests("pyscaf-app")
```

YAML files live in `tests/actions/{action_name}/test_*.yaml`.

## Acceptance Criteria

- [ ] Single entry point per package replaces per-action entries
- [ ] `discover_actions_from_entry_points()` works with both old and new patterns
- [ ] `pyscaf_core.testing` module provides ActionTestRunner
- [ ] pytest `--action-filter` option works via plugin
- [ ] Downstream packages can run YAML action tests with minimal boilerplate
- [ ] All existing tests pass
