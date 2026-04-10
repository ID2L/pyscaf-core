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

# Phase 5 — Remove Docker, native uv workflow

- [X] F006 — Remove Docker artifacts (Dockerfile, compose.yaml, .dockerignore)
- [X] F006 — Add .gitignore, clean __pycache__ from tracking
- [X] F006 — Rewrite README with native uv commands
- [X] F006 — Mark F004/F005 as superseded
- [X] F006 — Validation (uv sync, ruff, pytest)

# Phase 6 — Stress-test : fondation apps réelles

- [X] F601 — Squelettes `apps/pyscaf` + `apps/septeo-scaf` (workspace, CLI, pattern demo-scaf)
- [X] F602 — Empaquetage templates / assets (Hatchling + accès runtime)
- [X] F603 — Pytest racine : `testpaths` / marqueurs pour les nouvelles apps
- [ ] F604 — Validation Docker (CI stress-test ; réconciliation avec flux `uv` natif)
- [X] Validation Phase 6 (uv sync, ruff, pytest, CLI smoke)

# Phase 7 — Stress-test : `apps/pyscaf` (port open-pyscaf)

- [X] F701-spec — Spécification port actions : `specs/701-pyscaf-actions-port/` (`spec.md`, `plan.md`, `tasks.md`)
- [X] F701 — CLI + discovery + entry points (fil conducteur)
- [X] F702 — CoreAction
- [X] F703 — GitAction
- [X] F704 — LicenseAction
- [X] F705 — JupyterAction
- [X] F706 — TestAction
- [X] F707 — SemanticReleaseAction
- [X] F708 — DocumentationAction
- [X] F709 — JupyterToolsAction
- [ ] F710 — Tests d’intégration app pyscaf
- [X] Validation Phase 7 (ruff + pytest + CLI via Docker uv image)

# Phase 8 — Stress-test : `apps/septeo-scaf` (port septeo-agentic-scaffolder)

- [X] F801-spec — Spécification port actions : `specs/801-septeo-scaf-actions-port/` (`spec.md`, `plan.md`, `tasks.md`)
- [ ] F801 — CLI + deps app + entry points (fil conducteur)
- [X] F802 — CoreAction (Jinja2, visible_when, postfill_hook)
- [X] F803 — Actions stack (Git, Python, Php, Javascript, Database, Docker)
- [X] F804 — Localstack, EnvConfig, DocsStarlight, I18n, Pipeline
- [X] F805 — Agents, Rules, Skills, Mcp, IdeBinding
- [ ] F806 — Tests visible_when / postfill_hook + intégration
- [X] Validation Phase 8 (ruff + pytest + CLI via Docker uv image)

# Phase 9 — Stress-test : validation transversale

- [ ] F901 — Parité / diff vs repos sources (optionnel)
- [ ] F902 — Smoke full graph (toutes les entry points)
- [ ] F903 — Doc + lien roadmap principal

# Phase 10 — Semantic Release (pyscaf-core)

- [X] F1001-spec — Spécification : `specs/1001-semantic-release/`
- [X] F1001 — Config `[tool.semantic_release]` dans `pyproject.toml` racine
- [X] F1002 — Dev dep `python-semantic-release>=9.21.1`
- [X] F1003 — `.github/workflows/release.yml` (auto TestPyPI)
- [X] F1004 — `.github/workflows/deploy-production-manual.yml` (prod manuelle)
- [X] Validation Phase 10 (ruff)
