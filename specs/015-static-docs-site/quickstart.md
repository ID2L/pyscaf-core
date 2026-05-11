# Quickstart: Documentation Site

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed
- Repository cloned and synced (`uv sync --all-packages`)

## Local Preview

```bash
# Install docs dependencies (included in dev group)
uv sync

# Start live-reload dev server
uv run mkdocs serve

# Open http://127.0.0.1:8000 in browser
```

## Build

```bash
# Build static site to site/ directory
uv run mkdocs build

# Strict mode (fail on warnings)
uv run mkdocs build --strict
```

## Deploy (manual, one-time)

```bash
# Deploy to GitHub Pages (gh-pages branch)
uv run mkdocs gh-deploy
```

After initial setup, deployment is automated via GitHub Actions on push to `main`.

## Adding a Guide Page

1. Create a new `.md` file in `docs/`
2. Add it to the `nav:` section in `mkdocs.yml`
3. Preview with `mkdocs serve`

## Adding API Reference for a New Module

1. Create `docs/reference/<module>.md` with content:
   ```markdown
   # <module>

   ::: pyscaf_core.<module>
   ```
2. Add it to `nav:` under `API Reference`
3. Verify rendering with `mkdocs serve`

## Verifying API Coverage

Check that all public symbols render:

```bash
uv run mkdocs build --strict 2>&1 | grep -i "warning"
```

No warnings = all referenced symbols were found.
