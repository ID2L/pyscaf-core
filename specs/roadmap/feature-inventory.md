# Feature Inventory: pyscaf-core

**Companion to**: [roadmap.md](./roadmap.md)  
**Status**: Phase 0–1 specified (see roadmap [Specification progress](./roadmap.md#specification-progress))  

Use each row as a single **`/specify`** or ticket scope. Complexity: S = small, M = medium, L = large, XL = very large.

## Phase 0 — Bootstrap

| ID | Feature | Priority | Complexity | Dependencies | Phase | Spec |
|----|---------|----------|------------|--------------|-------|------|
| F001 | Root uv workspace, lockfile, shared Python version | P0 | M | None | 0 | [spec](../001-uv-workspace-root/spec.md) |
| F002 | `packages/pyscaf-core` package: `pyproject.toml`, `src/...`, `py.typed` | P0 | S | F001 | 0 | [spec](../002-pyscaf-core-package-skeleton/spec.md) |
| F003 | `apps/demo-scaf` app: path dep on core, console script stub | P0 | S | F002 | 0 | [spec](../003-demo-scaf-app-skeleton/spec.md) |
| F004 | Docker dev/CI image: `uv sync`, `ruff`, `pytest` entry | P0 | M | F001 | 0 | [spec](../004-docker-dev-ci/spec.md) |
| F005 | Minimal README: architecture one-pager, how to run tests in Docker | P1 | S | F004 | 0 | [spec](../005-readme-docker-docs/spec.md) |

## Phase 1 — Preference chain

| ID | Feature | Priority | Complexity | Dependencies | Phase | Spec |
|----|---------|----------|------------|--------------|-------|------|
| F101 | Port chain resolution (`Node`, `ExtendedNode`, `ChainLink`, `extend_nodes`, `build_chains`, path scoring, `best_execution_order`, `CircularDependencyError`) | P0 | L | F002 | 1 | [spec](../101-preference-chain-core-apis/spec.md) |
| F102 | Port `dependency_loader.py`, `tree_walker.py` (model covered in F101) | P1 | M | F101 | 1 | [spec](../102-preference-chain-loader-tree-walker/spec.md) |
| F103 | Port tests from `septeo-agentic-scaffolder/tests/preference_chain/` | P0 | M | F101 | 1 | [spec](../103-preference-chain-tests/spec.md) |

## Phase 2 — Actions base, TOML, discovery primitives

| ID | Feature | Priority | Complexity | Dependencies | Phase |
|----|---------|----------|------------|--------------|-------|
| F201 | `ChoiceOption`, `CLIOption` (incl. `visible_when`), Pydantic config for callables | P0 | M | F002 | 2 |
| F202 | `Action` base class, `__init_subclass__` rules, default `init`/`skeleton`/`install` | P0 | M | F201, F203 | 2 |
| F203 | Port `tools/toml_merge.py`, `tools/format_toml.py` + tests | P0 | M | F002 | 2 |
| F204 | `discover_actions` (pkgutil) + **entry point** loader returning action classes | P0 | L | F202 | 2 |
| F205 | Move/adapt `cli_option_to_key` helpers if still needed as shared utility | P2 | S | F201 | 2 |

## Phase 3 — Manager and CLI factory

| ID | Feature | Priority | Complexity | Dependencies | Phase |
|----|---------|----------|------------|--------------|-------|
| F301 | Port `ActionManager` (ordering, postfill, interactive prompts, `create_project`) | P0 | XL | F101, F204 | 3 |
| F302 | Port `fill_default_context` / `collect_cli_options` with `visible_when` | P0 | M | F301 | 3 |
| F303 | Core Click `build_cli` (or equivalent): inject discovery, dynamic options | P0 | L | F302 | 3 |
| F304 | Manager + CLI tests ported from Septeo/pyscaf | P0 | L | F301–F303 | 3 |

## Phase 4 — Demo application (hello-world)

| ID | Feature | Priority | Complexity | Dependencies | Phase |
|----|---------|----------|------------|--------------|-------|
| F401 | App package layout under `apps/demo-scaf` with minimal structure | P0 | S | F303 | 4 |
| F402 | Implement 2-3 sample actions (e.g. `HelloAction`, `ReadmeAction`) demonstrating core lifecycle hooks | P0 | M | F401 | 4 |
| F403 | Declare entry points (`pyscaf_core.plugins`); wire `main` to core CLI factory | P0 | S | F402 | 4 |
| F404 | Minimal test suite proving plugin discovery and action execution | P0 | M | F403 | 4 |
| F405 | Demo README documenting how to create a plugin app from core | P1 | S | F404 | 4 |

## Phase 5 — pyscaf consumer (external repo)

| ID | Feature | Priority | Complexity | Dependencies | Phase |
|----|---------|----------|------------|--------------|-------|
| F501 | Add `pyscaf-core` dependency to `open-pyscaf` | P1 | S | F304 release | 5 |
| F502 | Delete duplicated engine; implement entry points for pyscaf actions | P1 | L | F501 | 5 |
| F503 | Release notes + migration guide for pyscaf users | P2 | S | F502 | 5 |

## Dependency edges (feature level)

- F202 depends on F203 if default `Action.init` imports TOML tools (can soften with lazy import).
- F301 strictly depends on F101 (ordering) and F204 (discovery).
- F303 depends on F301/F302.
- F402 depends on stable F303 behavior.

## Suggested specification order

```text
F001 → F002 → F003 → F004
F101 → F103
F201 → F203 → F202 → F204
F301 → F302 → F303 → F304
F401 → F402 → F403 → F404 → F405 (demo app)
(later) F501 → F502 → F503
```
