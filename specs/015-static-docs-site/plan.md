# Implementation Plan: Static Documentation Site

**Branch**: `015-static-docs-site` | **Date**: 2026-04-12 | **Spec**: [spec.md](./spec.md)

---

## Summary

Add a static documentation site to `pyscaf-core` using **MkDocs + Material + mkdocstrings**, with API reference auto-generated from code and hand-written guides. Deployed to GitHub Pages via GitHub Actions on every push to `main`.

---

## Technical Context

**Language/Version**: Python 3.12+
**Primary Dependencies**: mkdocs 1.6+, mkdocs-material 9.5+, mkdocstrings[python] 0.27+
**Build tool**: `mkdocs build` (static HTML output)
**Deployment**: GitHub Actions → GitHub Pages (artifact-based)
**Project Type**: Documentation add-on to existing monorepo

---

## Architecture Decision

### Single docs site within the monorepo

The documentation lives at `docs/` in the repo root. MkDocs reads Markdown guide pages from `docs/` and generates API reference pages from `packages/pyscaf-core/src/pyscaf_core/` via mkdocstrings + Griffe (static analysis).

```
pyscaf-core/                    (repo root)
├── docs/
│   ├── index.md                 # Homepage
│   ├── getting-started.md       # Setup guide
│   ├── architecture.md          # Architecture overview
│   ├── creating-actions.md      # Plugin authoring guide
│   └── reference/
│       ├── index.md             # API reference landing
│       ├── actions.md           # ::: pyscaf_core.actions
│       ├── cli.md               # ::: pyscaf_core.cli
│       ├── preference_chain.md  # ::: pyscaf_core.preference_chain
│       ├── tools.md             # ::: pyscaf_core.tools
│       └── testing.md           # ::: pyscaf_core.testing
├── mkdocs.yml                   # MkDocs configuration
└── ...
```

### Why not a separate docs repo?

Keeping docs in the same repo as code ensures API reference is always in sync with the source. The `mkdocstrings` `paths` option points directly at the local source tree.

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Site generator | MkDocs 1.6+ | Standard Python doc builder |
| Theme | Material for MkDocs 9.5+ | Best-in-class Python docs theme |
| API extraction | mkdocstrings[python] (Griffe) | Static analysis, no imports |
| Deployment | GitHub Actions + Pages | Native GitHub integration |
| Dev preview | `mkdocs serve` | Live reload during writing |

---

## Project Structure (new/modified files)

```
pyscaf-core/
├── docs/                          # NEW — guide pages
│   ├── index.md
│   ├── getting-started.md
│   ├── architecture.md
│   ├── creating-actions.md
│   └── reference/
│       ├── index.md
│       ├── actions.md
│       ├── cli.md
│       ├── preference_chain.md
│       ├── tools.md
│       └── testing.md
├── mkdocs.yml                     # NEW — MkDocs config
├── .github/workflows/
│   └── docs.yml                   # NEW — GitHub Actions workflow
└── pyproject.toml                 # MODIFIED — add docs deps to dev group
```

---

## Implementation Strategy

### Phase 1: Foundation — Tooling & Configuration

1. Add `mkdocs`, `mkdocs-material`, `mkdocstrings[python]` to `[dependency-groups] dev` in root `pyproject.toml`.
2. Create `mkdocs.yml` with:
   - Site name, description, repo URL
   - Material theme config (palette, features)
   - mkdocstrings plugin with `paths: [packages/pyscaf-core/src]`
   - Navigation structure
3. Verify build works: `uv run mkdocs build` (via Docker).

### Phase 2: Content — Guide Pages

1. Create `docs/index.md` — project overview (adapted from README).
2. Create `docs/getting-started.md` — installation, dev setup, running tests.
3. Create `docs/architecture.md` — monorepo structure, plugin system, preference chain.
4. Create `docs/creating-actions.md` — how to create a new action (based on existing skill docs).

### Phase 3: Content — API Reference Pages

1. Create `docs/reference/index.md` — API reference landing page.
2. Create one page per top-level module with mkdocstrings directives:
   - `actions.md`: `::: pyscaf_core.actions`
   - `cli.md`: `::: pyscaf_core.cli`
   - `preference_chain.md`: `::: pyscaf_core.preference_chain`
   - `tools.md`: `::: pyscaf_core.tools`
   - `testing.md`: `::: pyscaf_core.testing`
3. Verify all public symbols render correctly.

### Phase 4: Deployment — GitHub Actions

1. Create `.github/workflows/docs.yml`:
   - Trigger: push to `main` (paths: `docs/**`, `mkdocs.yml`, `packages/pyscaf-core/src/**`)
   - Setup: Python 3.12, uv, install deps
   - Build: `mkdocs build`
   - Deploy: GitHub Pages via `actions/deploy-pages`
2. Configure repo Settings → Pages → Source: GitHub Actions.

### Phase 5: Polish

1. Add cross-links between guides and API reference.
2. Add project logo/favicon if available.
3. Verify search works across guides + API.
4. Update root `README.md` with docs link.
5. Update `_todo.md`.

---

## Configuration Reference

### `mkdocs.yml` (key sections)

```yaml
site_name: pyscaf-core
site_url: https://<owner>.github.io/pyscaf-core/
repo_url: https://github.com/<owner>/pyscaf-core
repo_name: <owner>/pyscaf-core

theme:
  name: material
  palette:
    - scheme: default
      primary: indigo
      toggle:
        icon: material/brightness-7
        name: Dark mode
    - scheme: slate
      primary: indigo
      toggle:
        icon: material/brightness-4
        name: Light mode
  features:
    - navigation.sections
    - navigation.expand
    - search.suggest
    - search.highlight
    - content.code.copy

plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          paths: [packages/pyscaf-core/src]
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true
            members_order: source

nav:
  - Home: index.md
  - Getting Started: getting-started.md
  - Architecture: architecture.md
  - Creating Actions: creating-actions.md
  - API Reference:
    - Overview: reference/index.md
    - actions: reference/actions.md
    - cli: reference/cli.md
    - preference_chain: reference/preference_chain.md
    - tools: reference/tools.md
    - testing: reference/testing.md
```

---

## Dependencies

- `mkdocs>=1.6` — static site generator
- `mkdocs-material>=9.5` — Material theme
- `mkdocstrings[python]>=0.27` — API reference generation (includes Griffe)

All added to `[dependency-groups] dev` in root `pyproject.toml`.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Griffe can't parse a module | Griffe handles standard Python well; test each module page during Phase 3 |
| mkdocstrings version incompatibility | Pin minimum versions; test in Docker |
| GitHub Pages not configured | Document manual step: Settings → Pages → Source: GitHub Actions |
| Large build time | Current codebase is small (~20 modules); well under 30s threshold |
