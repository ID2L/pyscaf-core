# CHANGELOG


## v0.1.0 (2026-04-10)

### Bug Fixes

- **006**: Update demo-scaf README, add review report and stats
  ([`d1746cc`](https://github.com/ID2L/pyscaf-core/commit/d1746ccae234037ed56d52af6691359eb4630a2c))

Fix Docker reference missed in apps/demo-scaf/README.md during implementation. Add review.md report
  and update stats.md with all three sessions (specify, implement, review).

Made-with: Cursor

### Chores

- Initial commit of pyscaf-core monorepo
  ([`e0d58fe`](https://github.com/ID2L/pyscaf-core/commit/e0d58fee37433599e05919146182534d965dffa7))

uv workspace with packages/pyscaf-core library, apps/demo-scaf demo, specs 001-005 and 101-103,
  Docker dev environment, and full test suite.

Made-with: Cursor

### Continuous Integration

- **semantic-release**: Add python-semantic-release config and GitHub workflows
  ([`a0ed134`](https://github.com/ID2L/pyscaf-core/commit/a0ed1345cee79421656165132baf1fe58d962d1c))

- Add [tool.semantic_release] to root pyproject.toml with monorepo paths - Add
  python-semantic-release>=9.21.1 as dev dependency - Create release.yml: auto-release on push to
  main + TestPyPI deploy - Create deploy-production-manual.yml: manual production PyPI deploy -
  Build command targets packages/pyscaf-core only

Made-with: Cursor

### Documentation

- **semantic-release**: Add specification, plan, tasks and review
  ([`a6047b3`](https://github.com/ID2L/pyscaf-core/commit/a6047b38a0153572eb62bf20cbf69fb39264700c))

- Create specs/1001-semantic-release/ with full spec-kit artifacts - Update _todo.md with Phase 10
  entries

Made-with: Cursor

### Features

- **006**: Remove Docker, adopt native uv/uvx workflow
  ([`f194ca4`](https://github.com/ID2L/pyscaf-core/commit/f194ca413868b8755c3a6229aa1ff72995897b87))

CLI project should run natively, not in containers. Remove Dockerfile, compose.yaml, .dockerignore.
  Add .gitignore, clean __pycache__ from tracking. Rewrite README with native uv commands. Mark
  F004/F005 as superseded.

All 66 tests pass, ruff clean, uv sync works natively.

Made-with: Cursor
