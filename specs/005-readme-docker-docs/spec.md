# F005 — Minimal README: architecture one-pager, Docker workflow

**Feature ID**: F005  
**Phase**: 0  
**Status**: Ready for implementation  
**Dependencies**: F004  

## Scope

Update the **repository root `README.md`** with:

1. **One-paragraph project identity**: `pyscaf-core` shared engine, `pyscaf_core` import, uv workspace (`packages/pyscaf-core`, `apps/demo-scaf`).
2. **Architecture one-pager**: pointer to `specs/roadmap/roadmap.md` for full phases; summarize critical path Phase 0→4 in 5–8 lines.
3. **Primary development workflow via Docker**: build image, run sync, lint, test — **all shell snippets must use `docker run` or `docker compose`**, not bare-metal `uv`.
4. **Resolved decisions** (short bullets): PyPI name, entry point group `pyscaf_core.plugins`, 0.x versioning, demo app location `apps/demo-scaf/`.

**Out of scope**

- User-facing docs site or MkDocs.
- Duplicating full feature inventory (link to `specs/roadmap/feature-inventory.md`).

## Directory and file structure

```text
pyscaf-core/
└── README.md                 # edit only this file for F005
```

## Content checklist

- [ ] Title and description mention **monorepo**, **pyscaf-core** (distribution), **pyscaf_core** (import).
- [ ] Section **Layout** listing `packages/pyscaf-core`, `apps/demo-scaf`, `specs/`.
- [ ] Section **Roadmap** with link to `specs/roadmap/roadmap.md`.
- [ ] Section **Development (Docker)** with copy-paste commands:
  - build `pyscaf-core-dev` (or the chosen image name from F004),
  - `uv sync --all-packages`,
  - `uv run ruff check .`,
  - `uv run pytest`,
  - `uv run demo-scaf` (stub).
- [ ] Note that **host** `uv` is optional and not the supported primary path.

## Acceptance criteria

- [ ] A new contributor can follow README **without** installing Python tooling on the host (only Docker).
- [ ] README does not instruct users to run `uv` or `pytest` on the host as the default path.
- [ ] Links to roadmap and feature inventory use repo-relative paths (`specs/roadmap/...`).

## Dependencies on other features

- **F004**: image name and commands must match the implemented Dockerfile/compose.

## Validation (Docker only)

No code execution required for README; optional smoke check that documented commands match reality:

```bash
docker build -t pyscaf-core-dev .
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run ruff check . && uv run pytest -q && uv run demo-scaf"
```

## Notes

- Keep README short; defer deep API docs to specs and later phases.
