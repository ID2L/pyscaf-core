# Feature Specification: Static Documentation Site

**Feature Branch**: `1002-static-docs-site`
**Created**: 2026-04-12
**Status**: Draft
**Input**: User description: "Doc statique hébergée sur GitHub Pages, doc technique générée depuis le code. Choix : Starlight ou solution pythonesque."

---

## User Scenarios & Testing

### User Story 1 — Developer reads API reference (Priority: P1)

A developer consuming `pyscaf-core` as a library opens the documentation site and navigates the **API reference** section. Every public class, function, and module is documented with signatures, type hints, and docstrings extracted directly from the source code.

**Why this priority**: The primary motivation is to expose generated-from-code technical documentation.

**Independent Test**: Visit `/reference/pyscaf_core/` on the deployed site and verify that `Action`, `ActionManager`, `build_cli`, `make_main`, `CLIOption`, `ChoiceOption`, and `preference_chain` are all documented with correct signatures.

**Acceptance Scenarios**:

1. **Given** a developer visits the docs site, **When** they navigate to the API reference for `pyscaf_core.actions`, **Then** they see the `Action` class with its docstring, methods, and type annotations.
2. **Given** a PR merges to `main`, **When** CI completes, **Then** the documentation site on GitHub Pages is updated within 5 minutes.
3. **Given** a function has Google-style docstrings with `Args:` / `Returns:`, **When** the API reference is generated, **Then** parameters and return types are rendered in a structured, readable format.

### User Story 2 — Contributor reads project guides (Priority: P1)

A new contributor opens the documentation site to understand the project architecture, how to set up a dev environment, and how to create a new action plugin.

**Why this priority**: Guides and API reference together form a complete documentation site.

**Independent Test**: Visit the site root and verify navigation includes at least: Getting Started, Architecture, Creating Actions, API Reference.

**Acceptance Scenarios**:

1. **Given** a contributor visits the docs site, **When** they click "Getting Started", **Then** they see setup instructions (uv install, sync, run tests).
2. **Given** a contributor visits the docs site, **When** they use the search feature, **Then** results span both guides and API reference.
3. **Given** a page references a class (e.g. `Action`), **When** the contributor clicks the link, **Then** they are taken to the corresponding API reference page.

### User Story 3 — Maintainer deploys docs (Priority: P2)

A maintainer pushes a change to `main`. The documentation is rebuilt and deployed to GitHub Pages automatically via GitHub Actions without any manual step.

**Why this priority**: Deployment automation is essential but lower than content correctness.

**Independent Test**: Push a trivial docs change and verify the Pages deployment succeeds.

**Acceptance Scenarios**:

1. **Given** a push to `main`, **When** the GitHub Actions workflow triggers, **Then** the site is built and deployed to `https://<owner>.github.io/pyscaf-core/`.
2. **Given** a build failure, **When** a docstring has invalid syntax, **Then** the CI workflow fails with a clear error message pointing to the problematic file.

### Edge Cases

- What happens when a module has no docstring? → It should still appear in the reference with its signature.
- What happens when a private function (prefixed `_`) exists? → It should be excluded from the API reference by default.
- What happens when the monorepo adds a new app? → Only `pyscaf-core` API reference is generated; apps are not part of the published library docs.

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate API reference pages from Python source code (docstrings + type annotations) for the `pyscaf_core` package.
- **FR-002**: System MUST support Google-style docstrings (Args, Returns, Raises sections).
- **FR-003**: System MUST produce a navigable static site with sidebar, search, and responsive layout.
- **FR-004**: System MUST support hand-written guide pages in Markdown alongside generated API pages.
- **FR-005**: System MUST deploy the built site to GitHub Pages via GitHub Actions on every push to `main`.
- **FR-006**: System MUST build locally for preview during development.
- **FR-007**: System SHOULD cross-link between guide pages and API reference (e.g. link from a guide to a class page).
- **FR-008**: System SHOULD render the site in under 30 seconds for the current codebase size.

### Non-Functional Requirements

- **NFR-001**: The documentation toolchain MUST be Python-native (installable via `pip`/`uv`), avoiding a Node.js dependency in the monorepo.
- **NFR-002**: Configuration MUST be minimal and maintainable (single config file preferred).
- **NFR-003**: The site MUST be accessible (semantic HTML, keyboard navigation).

### Key Entities

- **Guide Page**: A hand-written Markdown file under `docs/` covering architecture, setup, or usage.
- **API Reference Page**: An auto-generated page from a Python module's docstrings and signatures.
- **Navigation**: Sidebar tree with sections for Guides and API Reference.

---

## Technology Decision: Comparison

### Option A — MkDocs + Material + mkdocstrings (RECOMMENDED)

| Aspect | Detail |
|--------|--------|
| **API generation** | `mkdocstrings[python]` via Griffe (static analysis, no import needed) |
| **Docstring style** | Google, Numpy, Sphinx — all supported |
| **Guide pages** | Native Markdown in `docs/` |
| **Search** | Built-in client-side search (lunr.js) |
| **GitHub Pages** | `mkdocs gh-deploy` or standard Actions workflow |
| **Monorepo** | `paths` option to point at `packages/pyscaf-core/src` |
| **Toolchain** | Pure Python (`pip install mkdocs-material mkdocstrings[python]`) |
| **Community** | Very large, well-maintained, widely adopted |

**Pros**: Single Markdown-based site for guides + API; pure Python toolchain; excellent theme; static analysis (no need to import modules).
**Cons**: Plugin orchestration can be verbose for complex setups.

### Option B — Sphinx + autodoc + Furo

| Aspect | Detail |
|--------|--------|
| **API generation** | `sphinx.ext.autodoc` + `napoleon` (imports modules at build time) |
| **Guide pages** | RST or MyST-Parser (Markdown) |
| **Search** | Built-in |
| **GitHub Pages** | `sphinx-build` → HTML, standard deployment |
| **Toolchain** | Pure Python |

**Pros**: Industry standard; enormous extension ecosystem; intersphinx for cross-project linking.
**Cons**: Steeper learning curve; RST by default (MyST mitigates); imports code at build time (side-effects risk).

### Option C — Astro Starlight

| Aspect | Detail |
|--------|--------|
| **API generation** | None native for Python — requires external generation (pdoc/mkdocstrings) then import |
| **Guide pages** | MDX/Markdown, excellent DX |
| **Toolchain** | Node.js (Astro) — introduces a second runtime in a pure Python monorepo |

**Pros**: Beautiful UI; excellent performance; great for product docs.
**Cons**: No Python API doc integration; dual toolchain (Node + Python); significant overhead for a library project.

### Option D — pdoc

| Aspect | Detail |
|--------|--------|
| **API generation** | Excellent — imports modules, renders full API |
| **Guide pages** | Limited — no native guide system |

**Pros**: Minimal setup; great API output.
**Cons**: API-only; no guide pages; executes code at build time.

### Decision

**Option A — MkDocs + Material + mkdocstrings** is the recommended choice because:

1. Pure Python toolchain — no Node.js in a Python monorepo.
2. Best-in-class Markdown guide support alongside auto-generated API reference.
3. Static analysis via Griffe — no module imports, no side-effects.
4. Widely adopted in the Python ecosystem with strong community.
5. GitHub Pages deployment is trivial.

---

## Success Criteria

- **SC-001**: 100% of public modules in `pyscaf_core` appear in the API reference with correct signatures.
- **SC-002**: The documentation site is reachable at the project's GitHub Pages URL within 10 minutes of a push to `main`.
- **SC-003**: A new contributor can find setup instructions within 2 clicks from the homepage.
- **SC-004**: The full site builds in under 30 seconds on a standard CI runner.
- **SC-005**: Guide pages and API reference pages are cross-linked (at least one link from guide to API per guide page).
