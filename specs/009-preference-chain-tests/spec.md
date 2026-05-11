# F103 — Port preference chain tests

**Feature ID**: F103  
**Phase**: 1  
**Status**: Ready for implementation  
**Dependencies**: F101 (F102 if tests touch loader/walker)  

## Scope

Port **`tests/preference_chain/`** from Septeo to **`packages/pyscaf-core/tests/preference_chain/`**, rewriting imports from `septeo_scaffolder.preference_chain` to **`pyscaf_core.preference_chain`** (and `pyscaf_core.preference_chain.model` where used).

**Source reference**

- `~/lab/septeo-agentic-scaffolder/tests/preference_chain/test_execution_order.py`

**Current upstream file** exercises:

- `CircularDependencyError`, `best_execution_order`
- `Node` from `model`

**Out of scope**

- Property-based or fuzz tests (optional later).
- Tests for `dependency_loader` / `DependencyTreeWalker` unless added as part of F102 acceptance; if absent, create **`test_loader_walker.py`** with 1–2 focused tests (YAML fixture + walker shape) — optional P1 in same PR as F102.

## Directory and file structure

```text
packages/pyscaf-core/
├── pyproject.toml            # [tool.pytest.ini_options] testpaths if needed
└── tests/
    └── preference_chain/
        ├── __init__.py         # optional empty
        └── test_execution_order.py
```

### Import mapping (example)

```python
# before (Septeo)
from septeo_scaffolder.preference_chain import CircularDependencyError, best_execution_order
from septeo_scaffolder.preference_chain.model import Node

# after (core)
from pyscaf_core.preference_chain import CircularDependencyError, best_execution_order
from pyscaf_core.preference_chain.model import Node
```

## Test cases to preserve (from `test_execution_order.py`)

- `test_simple_linear_execution_order`
- `test_diamond_execution_order`
- `test_single_dependency_auto_after`
- `test_multiple_external_dependencies`
- `test_circular_dependency_detection`
- `test_complex_circular_dependency_detection`
- `test_complex_real_world_scenario`
- `test_empty_input`
- `test_single_node`
- `test_invalid_after_field` (`ValueError` message match)
- `test_auto_after_for_single_dependency`

**Assertions** must remain equivalent (ordering constraints, exception types, regex matches).

## Acceptance criteria

- [ ] `uv run pytest packages/pyscaf-core/tests/preference_chain -q` passes inside Docker.
- [ ] Test module uses only **`pyscaf_core`** imports.
- [ ] No network or filesystem dependencies for `test_execution_order` (unchanged from Septeo).
- [ ] Ruff passes on new test code.

## Dependencies on other features

- **F101**: implementation under test.
- **F102**: required before merging tests that import loader/walker; `test_execution_order.py` does **not** require F102.

## Validation (Docker only)

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run pytest packages/pyscaf-core/tests/preference_chain -q"
```

Full package tests (if more suites exist):

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run pytest packages/pyscaf-core/tests -q"
```

## Notes

- If `compute_all_resolution_pathes` behavior for **>8 chains** (greedy path) is untested upstream, consider a follow-up spec for edge-case tests (not blocking F103).
