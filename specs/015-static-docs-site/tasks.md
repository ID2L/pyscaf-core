# Tasks: Static Documentation Site

## Phase 1: Setup (Tooling & Configuration)

**Purpose**: Install dependencies and create the MkDocs configuration

- [X] T001 Add `mkdocs>=1.6`, `mkdocs-material>=9.5`, `mkdocstrings[python]>=0.27` to `[dependency-groups] dev` in `pyproject.toml`
- [X] T002 Run `uv sync` to install new dependencies
- [X] T003 Create `mkdocs.yml` with site metadata, Material theme, mkdocstrings plugin, and navigation structure
- [X] T004 Create `docs/` directory with placeholder `docs/index.md`
- [X] T005 Validate build: `uv run mkdocs build` completes without errors

**Checkpoint**: MkDocs builds an empty site successfully

## Phase 2: Guide Pages (Hand-written Content)

**Purpose**: Write the narrative documentation pages

- [X] T006 [P] Write `docs/index.md` — project overview (adapted from README.md)
- [X] T007 [P] Write `docs/getting-started.md` — prerequisites, installation, dev workflow, running tests
- [X] T008 [P] Write `docs/architecture.md` — monorepo layout, plugin system, preference chain, action lifecycle
- [X] T009 [P] Write `docs/creating-actions.md` — step-by-step guide to create a new action plugin

**Checkpoint**: All guide pages render correctly with `mkdocs serve`

## Phase 3: API Reference Pages (Generated from Code)

**Purpose**: Create mkdocstrings directive pages for each public module

- [X] T010 Create `docs/reference/index.md` — API reference overview with links to each module
- [X] T011 [P] Create `docs/reference/actions.md` — `::: pyscaf_core.actions` directive
- [X] T012 [P] Create `docs/reference/cli.md` — `::: pyscaf_core.cli` directive
- [X] T013 [P] Create `docs/reference/preference_chain.md` — `::: pyscaf_core.preference_chain` directive
- [X] T014 [P] Create `docs/reference/tools.md` — `::: pyscaf_core.tools` directive
- [X] T015 [P] Create `docs/reference/testing.md` — `::: pyscaf_core.testing` directive
- [X] T016 Validate: all public symbols (`Action`, `ActionManager`, `build_cli`, `make_main`, `CLIOption`, `ChoiceOption`) appear with correct signatures

**Checkpoint**: Full API reference renders correctly

## Phase 4: GitHub Actions Deployment

**Purpose**: Automate documentation deployment to GitHub Pages

- [X] T017 Create `.github/workflows/docs.yml` — build and deploy on push to `main`
- [X] T018 Document manual step: enable GitHub Pages source = GitHub Actions in repo settings

**Checkpoint**: CI workflow file is valid YAML and triggers on correct paths

## Phase 5: Polish & Cross-Cutting

**Purpose**: Final touches, cross-links, and project integration

- [X] T019 Add cross-links from guide pages to API reference pages
- [X] T020 Verify search works across guides and API reference
- [X] T021 Update root `README.md` with documentation site link
- [X] T022 Update `_todo.md` with Phase 11 docs entry
- [X] T023 Run full build validation: `uv run mkdocs build --strict`

## Dependency Graph

```
Phase 1 (T001-T005) → Phase 2 (T006-T009) ──┐
                    → Phase 3 (T010-T016) ──┤→ Phase 5 (T019-T023)
                    → Phase 4 (T017-T018) ──┘
```

Phases 2, 3, and 4 can run in parallel after Phase 1. Phase 5 depends on all three.

## Summary

- Total tasks: 23
- By priority: P0=0, P1=18, P2=5
- Parallelizable: T006-T009, T011-T015
- Estimated effort: ~1 j/h (human), ~15min (AI)
