# pyscaf-core Phase 0 bootstrap

- [X] F001 — Root uv workspace
- [X] F002 — pyscaf-core package skeleton
- [X] F003 — demo-scaf app skeleton
- [X] F004 — Docker dev/CI
- [X] F005 — README
- [X] Validation (Docker)

# Phase 1 — preference chain

- [X] F101 — Port preference chain core APIs (`preference_chain/`)
- [X] F102 — `dependency_loader`, `tree_walker`, exports
- [X] F103 — Tests `preference_chain/test_execution_order.py`
- [X] Validation (Docker ruff + pytest)

# Phase 2 — Action base, TOML tools, discovery

- [X] F203 — TOML tools (`tools/toml_merge`, `tools/format_toml`, tests)
- [X] F201–F202 — `CLIOption`, `ChoiceOption`, `Action` (`actions/__init__.py`)
- [X] F204 — Action / discovery tests (`tests/actions/test_actions.py`)
- [X] F205 — `discover_actions_from_package`, `discover_actions_from_entry_points`
- [X] Dependencies (`tomlkit`, `click`, `questionary`, `rich`) + `__init__` re-exports
- [X] Validation (Docker: ruff, pytest, import smoke)

# Phase 3 — ActionManager, CLI factory, tests

- [X] F301 — `ActionManager` (`actions/manager.py`)
- [X] F302 — CLI helpers (`cli.py`: `fill_default_context`, `collect_cli_options`, `set_option_default`, `add_dynamic_options`, `build_cli`, `make_main`)
- [X] F304 — Tests `tests/actions/test_manager.py`, `tests/cli/test_cli.py`
- [X] `__init__.py` re-exports (`ActionManager`, `build_cli`, `make_main`)
- [X] Validation (Docker: ruff, pytest, imports)

# Phase 4 — demo-scaf working demo

- [X] F401 — App package layout (`actions/` subpackage)
- [X] F402 — Sample actions (`HelloAction`, `ReadmeAction`)
- [X] F403 — Entry points + CLI wiring (`main.py`, `pyproject.toml`)
- [X] F404 — Tests + root `pytest` testpaths
- [X] F405 — `apps/demo-scaf/README.md`
- [X] Validation (Docker: ruff, pytest, CLI smoke)
