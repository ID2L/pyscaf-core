# Technology Research: Static Documentation Site

**Feature**: `1002-static-docs-site`
**Date**: 2026-04-12

---

## Research Question

Which static site generator best fits a Python monorepo (uv workspaces) that needs:
- API reference auto-generated from Google-style docstrings
- Hand-written guide pages in Markdown
- GitHub Pages deployment
- Minimal toolchain complexity

---

## Candidates Evaluated

### 1. MkDocs + Material for MkDocs + mkdocstrings

**Version landscape** (as of 2026):
- MkDocs: 1.6+
- Material for MkDocs: 9.5+
- mkdocstrings[python]: 1.x (backed by Griffe for static analysis)

**How API generation works**:
Griffe performs **static analysis** of Python source files — it does NOT import modules. It parses AST + type annotations + docstrings (Google, Numpy, Sphinx styles). In `mkdocs.yml`, you configure `mkdocstrings` plugin with handler `python` and point `paths` at source directories. In Markdown files, you use `::: pyscaf_core.actions.Action` directives to render API docs inline.

**Monorepo support**:
```yaml
plugins:
  - mkdocstrings:
      handlers:
        python:
          paths: [packages/pyscaf-core/src]
```

**GitHub Pages**:
- `mkdocs gh-deploy` (built-in command, pushes to `gh-pages` branch)
- Or standard GitHub Actions: `mkdocs build` → upload artifact → deploy

**Verdict**: ✅ Best fit for this project.

---

### 2. Sphinx + autodoc + Furo

**How API generation works**:
`sphinx.ext.autodoc` **imports** the Python modules at build time to introspect them. This means all dependencies must be installed. `napoleon` extension converts Google/Numpy docstrings. Output is RST by default, but `myst-parser` enables Markdown.

**Monorepo gotcha**:
`conf.py` must manipulate `sys.path` to find packages. All dependencies (pydantic, click, etc.) must be importable at build time.

**GitHub Pages**: Standard `sphinx-build -b html` → deploy.

**Verdict**: ⚠️ Viable but heavier setup. Import-based approach requires full dependency resolution at build time.

---

### 3. Astro Starlight

**How it works**:
Astro-based static site generator for documentation. Content in Markdown/MDX. No native Python docstring extraction.

**Python API integration options**:
1. Run `pdoc` or `sphinx` to generate HTML/Markdown → embed as Starlight pages
2. Manual Markdown API pages
3. Use `starlight-openapi` for HTTP APIs (not applicable here)

**Monorepo impact**:
Introduces `node_modules/`, `package.json`, `astro.config.mjs` into a pure-Python monorepo. Requires Node.js in CI.

**Verdict**: ❌ Poor fit. Dual toolchain overhead with no native Python API generation.

---

### 4. pdoc

**How it works**:
Imports modules at runtime, generates standalone HTML pages. Excellent for pure API reference. Limited guide/narrative support.

**Monorepo**:
`pdoc pyscaf_core -o docs/` — simple but imports code (needs deps installed).

**Verdict**: ⚠️ Good for API-only docs. No guide system. Could be used as a sub-tool feeding into another framework.

---

## Decision Matrix

| Criterion (weight) | MkDocs+Material | Sphinx+Furo | Starlight | pdoc |
|---------------------|:-:|:-:|:-:|:-:|
| API from docstrings (30%) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| Guide pages (20%) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ |
| Pure Python toolchain (15%) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐ |
| GitHub Pages ease (10%) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| Monorepo support (10%) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ |
| Community/ecosystem (10%) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| Setup simplicity (5%) | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Weighted total** | **3.0** | **2.5** | **1.8** | **2.3** |

---

## Final Decision

**MkDocs + Material for MkDocs + mkdocstrings[python]**

Rationale:
1. Static analysis (Griffe) avoids import side-effects — critical for a scaffolding library that manipulates file systems.
2. Single `mkdocs.yml` config — no `conf.py` + extensions juggling.
3. Native Markdown for guides — matches existing project style (README, specs).
4. Material theme is the de facto standard for Python library docs.
5. Zero Node.js dependency — stays within the Python toolchain.
6. `mkdocs gh-deploy` is a one-liner for GitHub Pages.

Dependencies to add (dev group):
```
mkdocs>=1.6
mkdocs-material>=9.5
mkdocstrings[python]>=0.27
```
