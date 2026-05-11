# Tasks — Spec 901

## Phase 1: Core Testing Module

- [x] Create `pyscaf_core/testing/__init__.py` with exports
- [x] Create `pyscaf_core/testing/runner.py` — ActionTestRunner
- [x] Create `pyscaf_core/testing/discovery.py` — YAML discovery functions
- [x] Create `pyscaf_core/testing/conftest_helpers.py` — pytest hooks
- [x] Create `pyscaf_core/testing/pytest_plugin.py` — pytest11 plugin
- [x] Add `pytest11` entry point in pyscaf-core pyproject.toml
- [x] Add `pyyaml` to pyscaf-core dependencies (already present)

## Phase 2: Action Entry Point Refactoring

- [x] Update `apps/pyscaf/pyproject.toml` — single action entry point
- [x] Update `apps/demo-scaf/pyproject.toml` — single action entry point

## Phase 3: Test Entry Points

- [x] Add `pyscaf_core.test_yamls` entry point in demo-scaf
- [x] Add `pyscaf_core.test_yamls` entry point in pyscaf-app
- [x] Create `demo_scaf/testing.py` with get_test_config
- [x] Create `pyscaf_app/testing.py` with get_test_config

## Phase 4: Test YAML Files

- [x] Create demo-scaf test YAMLs (hello, readme)
- [x] Update `tests/test_demo.py` or create `tests/test_actions.py` using framework

## Phase 5: Verification

- [x] Run unit tests for pyscaf_core.testing
- [x] Run demo-scaf tests
- [x] Run pyscaf-app smoke tests
