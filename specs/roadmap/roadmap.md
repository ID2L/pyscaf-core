# Project Roadmap: pyscaf-core

**Created**: 2026-04-08  
**Author**: Cartographer (roadmap planning)  
**Status**: In progress — Phase 0–1 **specified** (see [Specification progress](#specification-progress)); implementation not started  

## Executive Summary

This monorepo introduces **pyscaf-core**, a shared Python library that owns the scaffolding engine currently duplicated between `open-pyscaf` (`pyscaf`) and `septeo-scaf` (`septeo_scaffolder`). Consumer projects become thin **applications**: they depend on core, declare how to discover their **action plugins**, and ship a CLI entry point wired to core’s Click framework.

The first in-repo application is **`apps/demo-scaf`**: a **demo/hello-world** with 2–3 sample actions on the core plugin API. Full Septeo product migration stays in the external repo for now. A later phase (Phase 5) migrates `pyscaf` to depend on published core so both products share one engine.

The roadmap is intentionally incremental: establish package boundaries and discovery first, port the engine with tests, then deliver the demo app on top of the CLI factory, and finally point external consumers at published `pyscaf-core`.

## Specification progress

| Phase | Feature IDs | Spec path(s) | Status |
|-------|----------------|--------------|--------|
| 0 | F001 | [specs/001-uv-workspace-root/spec.md](../001-uv-workspace-root/spec.md) | Specified |
| 0 | F002 | [specs/002-pyscaf-core-package-skeleton/spec.md](../002-pyscaf-core-package-skeleton/spec.md) | Specified |
| 0 | F003 | [specs/003-demo-scaf-app-skeleton/spec.md](../003-demo-scaf-app-skeleton/spec.md) | Specified |
| 0 | F004 | [specs/004-docker-dev-ci/spec.md](../004-docker-dev-ci/spec.md) | Specified |
| 0 | F005 | [specs/005-readme-docker-docs/spec.md](../005-readme-docker-docs/spec.md) | Specified |
| 1 | F101 | [specs/101-preference-chain-core-apis/spec.md](../101-preference-chain-core-apis/spec.md) | Specified |
| 1 | F102 | [specs/102-preference-chain-loader-tree-walker/spec.md](../102-preference-chain-loader-tree-walker/spec.md) | Specified |
| 1 | F103 | [specs/103-preference-chain-tests/spec.md](../103-preference-chain-tests/spec.md) | Specified |

**Next to specify** (Phase 2): F201–F205 per [feature-inventory.md](./feature-inventory.md).

## Current State Analysis

| Area | `pyscaf` (`~/lab/pyscaf`) | `septeo-agentic-scaffolder` |
|------|---------------------------|-----------------------------|
| Layout | `src/pyscaf/` | `src/septeo_scaffolder/` |
| Engine | `actions/`, `preference_chain/`, `cli.py`, `tools/toml_*` | Same modules, evolved |
| `CLIOption` | No `visible_when` | `visible_when: Callable[[dict], bool] \| None` + `model_config` for callables |
| Actions | core, git, license, jupyter, test, semantic_release, documentation, jupyter_tools | core, agents, rules, skills, mcp, ide_binding, git, python, php, javascript, database, docker, localstack, env_config, docs_starlight, i18n, pipeline |
| Build | Hatchling, script `pyscaf` | Hatchling, script `septeo-scaf` |

**Target workspace** (`~/lab/pyscaf-core`): empty git repo on `main` — greenfield for layout, tooling, and docs.

## Technical Decisions (with Rationale)

### 1. Plugin discovery: entry points as primary, pkgutil as implementation detail

**Decision**: Standardize on **`importlib.metadata` entry points** (group `pyscaf_core.plugins`) that reference **modules** or **callables returning action classes**. Keep **walking a package namespace** (`pkgutil.iter_modules`) as an optional helper used *inside* the app package (e.g. `septeo_scaffolder.actions`) for developer ergonomics, not as the only contract.

**Rationale**:

- Entry points are the conventional Python plugin surface: installable, composable, no import-path magic, works with editable installs and multiple distributions in one env.
- Pure pkgutil discovery ties plugins to a single package tree and makes “optional extras” harder than `pip install septeo-scaf[php]` registering extra entry points.
- Septeo’s large action set benefits from grouping (optional dependency groups → optional entry point modules).

**Alternative rejected for v1**: Registry-only (global dict) — flexible but pushes registration order bugs onto apps; still useful as a **test hook** alongside entry points.

### 2. `visible_when` on `CLIOption`

**Decision**: **Include `visible_when` in core** on `CLIOption`, default `None` (always visible). Core’s `fill_default_context` / interactive collection must respect it when building prompts and when attaching Click options (options omitted or hidden when not visible).

**Rationale**: It is a small, backward-compatible extension; `pyscaf` gains conditional UX without forking types. Septeo already has tests (`test_visible_when.py`) that can move with the behavior.

### 3. Click CLI extensibility

**Decision**: Core exposes a **factory** (e.g. `build_cli(app_name, discover_actions_callable, **kwargs) -> click.Group`) that:

1. Resolves the list of action classes via the app-supplied discovery.
2. Aggregates `cli_options` from all actions, applying `visible_when` where applicable.
3. Registers commands/options in a stable order (aligned with dependency resolution / execution order where it matters).

Apps only provide: **project display name**, **discovery function or entry-point configuration**, and optional **command overrides** (later phase).

**Rationale**: Duplicating Click wiring in each app recreates drift; the Septeo/`pyscaf` split already shows parallel `cli.py` files.

### 4. Monorepo layout and uv workspaces

**Decision**: Use **`uv` workspace** with members:

- `packages/pyscaf-core` — library, import `pyscaf_core`.
- `apps/demo-scaf` — demo application depending on workspace core (hello-world plugin showcase).

Root `pyproject.toml` defines `[tool.uv.workspace]` members; each member has its own `pyproject.toml`.

**Rationale**: Single repo for coordinated API changes; `uv lock` at root gives reproducible dev. Hatchling can remain per-package if preferred; uv works with standard PEP 517 backends.

**Note**: Align **PyPI distribution names** early (`pyscaf-core` vs `pyscaf_core` import) to avoid confusion with the `pyscaf` consumer app.

### 5. TOML merge / format utilities

**Decision**: Ship **`toml_merge` and `format_toml` inside core** as stable utilities used by the default `Action.init()` implementation.

**Rationale**: Both products depend on them; they are not optional for the default action contract. If a consumer wants zero TOML merging, they can override `init()` without pulling extra deps beyond what core already needs (`tomlkit`, etc.).

### 6. Minimal action lifecycle contract (core public API)

**Decision**: Core documents and stabilizes:

| Element | Contract |
|---------|----------|
| Class attributes | `depends: set[str]`, `run_preferably_after: str \| None`, `cli_options: list[CLIOption]` |
| Identity | Derived ID: `ClassName.replace("Action", "").lower()` (keep convention; document explicitly) |
| Hooks | `activate(context) -> bool`, `skeleton(context) -> dict[Path, str \| None]`, `init(context) -> None`, `install(context) -> None` |
| Orchestration | `ActionManager.create_project` three-phase flow unchanged semantically |

**Rationale**: Plugins are action classes; the smallest stable surface reduces breakage when internal manager code changes.

---

## Phased Plan

### Phase 0: Repository bootstrap

**Goal**: Runnable monorepo with lint/test/CI skeleton and no engine code yet.

**Milestones**

- M0.1: Root `pyproject.toml` (uv workspace), `.python-version`, README with local dev via **Docker** (per project policy: all shell commands in CI/dev docs go through containers).
- M0.2: `packages/pyscaf-core` empty package with version, typed `py.typed`, minimal public `__init__`.
- M0.3: `apps/demo-scaf` placeholder depending on core path dependency.
- M0.4: Ruff/pytest config shared or per-package; `uv run pytest` from Docker recipe.

**Exit criteria**

- [ ] `docker compose` or documented `docker run … uv sync && uv run pytest` succeeds at root with zero tests.
- [ ] Workspace installs editable core + app.

**Dependencies**: None.

---

### Phase 1: Core extraction — preference chain and models

**Goal**: `pyscaf_core.preference_chain` is the single source of truth; tests ported from Septeo (and pyscaf if present).

**Features** (see [feature-inventory.md](./feature-inventory.md))

- F101: Port `model`, `chain`, `circular_dependency_error`, `extend_nodes`, ordering APIs.
- F102: Port `dependency_loader`, `tree_walker` (dev/docs; keep test utilities clear).
- F103: Unit tests for execution order, cycles, scores.

**Milestones**

- M1.1: Package subtree compiles; public re-exports documented.
- M1.2: Test parity with `septeo-agentic-scaffolder/tests/preference_chain/`.

**Exit criteria**

- [ ] No dependency on Click/actions in this package subtree.
- [ ] `CircularDependencyError` and resolution behavior covered by tests.

**Dependencies**: Phase 0.

---

### Phase 2: Core — actions base, CLI types, TOML tools

**Goal**: `Action`, `CLIOption` (with `visible_when`), `ChoiceOption`, discovery helpers, `tools/toml_*` live in core.

**Features** (see [feature-inventory.md](./feature-inventory.md))

- F201: Port `ChoiceOption`, `CLIOption` (incl. `visible_when`), Pydantic config for callables.
- F202: Port `Action` base, `__init_subclass__` rules, default hooks (depends on F201, F203).
- F203: Port TOML utilities + tests from Septeo.
- F204: `discover_actions` (pkgutil) + **entry-point** loader (`pyscaf_core.plugins`).
- F205: Move/adapt `cli_option_to_key` helpers if still needed (P2).

**Milestones**

- M2.1: Types and base class match Septeo semantics (superset of pyscaf).
- M2.2: `visible_when` covered by tests moved from Septeo.

**Exit criteria**

- [ ] `pyscaf` could theoretically depend on this release without `visible_when` regressions (field unused).
- [ ] Entry point loader returns ordered/class map for manager consumption.

**Dependencies**: Phase 1 optional for imports only — can parallelize after F101 stubs, but manager needs F101 complete.

---

### Phase 3: Core — ActionManager and CLI factory

**Goal**: Orchestration and Click CLI construction are centralized.

**Features**

- F301: Port `ActionManager` (discovery, ordering, postfill, interactive prompts, `create_project` phases).
- F302: Port/adapt `cli.py` into `pyscaf_core.cli` with app-injectable discovery.
- F303: `fill_default_context`, `collect_cli_options` with `visible_when` integration.

**Milestones**

- M3.1: Manager unit tests (from Septeo/pyscaf) pass against core.
- M3.2: Minimal integration test: dummy action package + CLI `--help` and one dry run.

**Exit criteria**

- [ ] Single code path for three-phase create.
- [ ] CLI options reflect merged action options and visibility rules.

**Dependencies**: Phase 2 complete.

---

### Phase 4: Demo application (hello-world)

**Goal**: `apps/demo-scaf` demonstrates the core plugin API with **2–3 sample actions** and entry point registration; not a full Septeo migration.

**Features** (see [feature-inventory.md](./feature-inventory.md))

- F401: App package layout under `apps/demo-scaf` (beyond Phase 0 stub) with structure ready for actions.
- F402: Sample actions (e.g. `HelloAction`, `ReadmeAction`) demonstrating lifecycle hooks.
- F403: Declare `[project.entry-points."pyscaf_core.plugins"]`; wire `main` to core CLI factory.
- F404: Minimal tests: plugin discovery and action execution path.
- F405: Demo README: how to build a plugin app on core.

**Milestones**

- M4.1: CLI `--help` and one documented create flow work in Docker.
- M4.2: Entry point discovery matches manager expectations.

**Exit criteria**

- [ ] `uv run demo-scaf` (or agreed console script name) runs inside Docker with documented sample commands.
- [ ] Plugins load via `pyscaf_core.plugins` entry points.

**Dependencies**: Phase 3.

---

### Phase 5: pyscaf consumer (follow-up, outside initial monorepo scope)

**Goal**: `open-pyscaf` depends on published `pyscaf-core`; deletes duplicated engine.

**Features**

- F501: Add dependency on `pyscaf-core`.
- F502: Replace local engine modules with imports; entry points for pyscaf actions.
- F503: Release and migration notes.

**Dependencies**: Phase 4 stable API (semver commitment) and ideally one patch release after dogfooding.

---

## Dependency Graph (High Level)

```text
Phase 0 (bootstrap)
    │
    ▼
Phase 1 (preference_chain)
    │
    ├──────────────────────┐
    ▼                      │
Phase 2 (Action / CLI types / TOML)
    │
    ▼
Phase 3 (Manager + CLI factory)
    │
    ▼
Phase 4 (demo app)
    │
    ▼
Phase 5 (pyscaf consumer — separate repo)
```

Critical path: **0 → 1 → 2 → 3 → 4**.

---

## Milestone Summary

| Milestone | Phase | Meaning of done |
|-----------|-------|------------------|
| M0.x | 0 | Dockerized dev, workspace installs |
| M1.x | 1 | Preference chain tested in core |
| M2.x | 2 | Action/CLIOption + TOML in core |
| M3.x | 3 | Manager + CLI factory in core |
| M4.x | 4 | Demo app on core (plugins + CLI) |
| M5.x | 5 | pyscaf on published core |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Subtle drift between two copies during port | Med | High | Port tests first; run side-by-side CLI diff scripts in Phase 4 |
| Entry point discovery ordering differs from pkgutil | Med | Med | Define deterministic sort (topological + stable tie-break) |
| Jinja/template paths break when moving packages | Med | Med | Use `importlib.resources` or package-relative paths consistently |
| Over-generalizing plugin API delays MVP | Med | Med | Ship Septeo-parity with one entry-point group; extend later |
| Import name `pyscaf_core` vs product `pyscaf` confusion | Low | Med | Clear docs and PyPI package naming |

---

## Resolved Questions

1. **Distribution and import names**: `pyscaf-core` on PyPI, `pyscaf_core` as Python import. **Confirmed.**
2. **Entry point group name**: `pyscaf_core.plugins`. **Confirmed.**
3. **Default `init` logging**: Replace `print` with `logging` in core; apps configure handlers. **Confirmed.**
4. **Demo app scope**: The `apps/demo-scaf` app is a **demo/hello-world** showcasing core usage — not a full Septeo migration. Full Septeo migration stays in the external repo later.
5. **Versioning policy**: Core starts `0.x` until both consumers validate. **Confirmed.**

---

## Development Note (Docker)

Project policy requires running commands in **Docker**. The Phase 0 deliverable should include a `Dockerfile` or `compose.yaml` that runs `uv sync`, `ruff check`, and `pytest` so contributors and CI share one environment. Local bare-metal `uv` can remain optional but must not be the documented primary path.

---

## Next Steps

1. **Implement** Phase 0 using specs `001`–`005`, then Phase 1 using `101`–`103` (Docker-validated).
2. Specify Phase 2: **F201–F205** (see [feature-inventory.md](./feature-inventory.md)), then Phase 3 **F301–F304**, then Phase 4 **F401–F405**.

### Specification complete (Phase 0–1)

| Order | Feature | Spec |
|-------|---------|------|
| 1 | F001 | [001-uv-workspace-root](../001-uv-workspace-root/spec.md) |
| 2 | F002 | [002-pyscaf-core-package-skeleton](../002-pyscaf-core-package-skeleton/spec.md) |
| 3 | F003 | [003-demo-scaf-app-skeleton](../003-demo-scaf-app-skeleton/spec.md) |
| 4 | F004 | [004-docker-dev-ci](../004-docker-dev-ci/spec.md) |
| 5 | F005 | [005-readme-docker-docs](../005-readme-docker-docs/spec.md) |
| 6 | F101 | [101-preference-chain-core-apis](../101-preference-chain-core-apis/spec.md) |
| 7 | F102 | [102-preference-chain-loader-tree-walker](../102-preference-chain-loader-tree-walker/spec.md) |
| 8 | F103 | [103-preference-chain-tests](../103-preference-chain-tests/spec.md) |
