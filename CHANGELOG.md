# CHANGELOG


## v0.2.0 (2026-04-11)

### Chores

- Ignore apps directory in gitignore
  ([`05ea3fb`](https://github.com/ID2L/pyscaf-core/commit/05ea3fb0d223451d72c69d21853b7dd534167e06))

Stress-test apps are workspace-local and should not be tracked.

Made-with: Cursor

- Update lockfile after testing framework changes
  ([`4acdebe`](https://github.com/ID2L/pyscaf-core/commit/4acdebe771a653999bf425867b984969ddc4af9d))

Made-with: Cursor

### Documentation

- **roadmap**: Add stress-test feature inventory and roadmap
  ([`ca5c892`](https://github.com/ID2L/pyscaf-core/commit/ca5c892bf8ce5474e56d7d2a7c7628e7df19e252))

Feature inventory mapping pyscaf/septeo-scaf actions to pyscaf-core coverage, plus phased roadmap
  for the stress-test migration.

Made-with: Cursor

- **specs**: Add entry point refactoring specification
  ([`09a353e`](https://github.com/ID2L/pyscaf-core/commit/09a353e97f35e7ce5e1e27d04a8211ab4aec8640))

Spec 901 describes the refactoring of per-action entry points to single discover_actions callables,
  and the shared YAML testing framework.

Made-with: Cursor

- **specs**: Add pyscaf actions port specification
  ([`a436e7c`](https://github.com/ID2L/pyscaf-core/commit/a436e7c0b06bcbbfbe330b4434785a85ed047e31))

Spec 701 defines the plan to port all pyscaf actions (core, git, license, jupyter, test,
  semantic-release, documentation, jupyter-tools) to pyscaf-core.

Made-with: Cursor

- **specs**: Add septeo-scaf actions port specification
  ([`d759414`](https://github.com/ID2L/pyscaf-core/commit/d7594146be894fa6e982581a4544701cb44ae7bb))

Spec 801 defines the plan to port septeo-scaf-specific actions (docker, python, agents, rules, etc.)
  to the pyscaf-core monorepo.

Made-with: Cursor

- **specs**: Add stress-test apps skeleton specification
  ([`5e4ddf9`](https://github.com/ID2L/pyscaf-core/commit/5e4ddf91ff933ea1cfc78284d08ab2ef9890e537))

Spec 601 defines the structure for demo-scaf, pyscaf and septeo-scaf stress-test applications that
  validate the pyscaf-core plugin API.

Made-with: Cursor

### Features

- Track stress-test apps in repository
  ([`09d6e7c`](https://github.com/ID2L/pyscaf-core/commit/09d6e7cb8b85b354b2f376942324b52ef7713f81))

Add demo-scaf, pyscaf-app, and septeo-scaf workspace apps. These serve as stress-test and validation
  apps for the pyscaf-core plugin API.

Made-with: Cursor

- **pyscaf-core**: Add shared testing framework and pytest plugin
  ([`0f8d0d5`](https://github.com/ID2L/pyscaf-core/commit/0f8d0d584a41654583c467992a9ef154d1d0a647))

- ActionTestRunner: YAML-driven action test runner (adapted from pyscaf) - discover_test_files():
  filesystem-based YAML discovery - discover_test_files_from_entry_points(): entry-point-based
  discovery - create_yaml_tests(): one-liner to create parametrized pytest functions - pytest plugin
  with --action-filter option (via pytest11 entry point)

Downstream packages can now test actions with minimal boilerplate: test_action =
  create_yaml_tests("my-cli")

Made-with: Cursor


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
