# Feature Specification: Semantic Release for pyscaf-core

**Feature Branch**: `1001-semantic-release`
**Created**: 2025-04-09
**Status**: Draft
**Input**: User description: "Add semantic release configuration and GitHub Actions for pyscaf-core, following the pattern from open-pyscaf."

## User Scenarios & Testing

### User Story 1 — Automatic release on push to main (Priority: P0)

As a maintainer, when I push conventional commits to `main`, a GitHub Actions workflow
should automatically determine the next version, update version files, create a GitHub
release with assets, and publish the package to TestPyPI.

**Why this priority**: Core release automation — the primary value proposition.
**Independent Test**: Push a `feat:` commit to main; verify a new GitHub release appears,
version is bumped, and TestPyPI receives the package.

**Acceptance Scenarios**:

1. **Given** a `feat: …` commit pushed to main, **When** the release workflow runs,
   **Then** version is bumped (minor), a GitHub release is created, and the package is
   published to TestPyPI.
2. **Given** a `fix: …` commit pushed to main, **When** the release workflow runs,
   **Then** version is bumped (patch).
3. **Given** a `chore: …` commit pushed to main, **When** the release workflow runs,
   **Then** no release is created.

### User Story 2 — Manual deploy to production PyPI (Priority: P1)

As a maintainer, I can manually trigger a workflow to publish the latest GitHub release to
production PyPI.

**Why this priority**: Production publish must be deliberate.
**Independent Test**: Trigger the manual workflow; verify the latest release assets are
published to PyPI.

**Acceptance Scenarios**:

1. **Given** a GitHub release exists, **When** I manually trigger the deploy-production
   workflow, **Then** the release artifacts are published to production PyPI.

### Edge Cases

- No conventional commits since last release → no release created, workflow succeeds silently.
- Missing GitHub secrets → workflow fails with clear error message.
- First release (no prior tags) → semantic-release creates v0.2.0 (or appropriate).

## Requirements

### Functional Requirements

- **FR-001**: The root `pyproject.toml` MUST contain `[tool.semantic_release]` configuration
  pointing to `packages/pyscaf-core/pyproject.toml:project.version` and
  `packages/pyscaf-core/src/pyscaf_core/__init__.py:__version__`.
- **FR-002**: A `release.yml` GitHub Actions workflow MUST run on push to `main` and perform
  semantic versioning, GitHub release creation, artifact upload, and TestPyPI publish.
- **FR-003**: A `deploy-production-manual.yml` workflow MUST allow manual trigger to publish
  to production PyPI.
- **FR-004**: `python-semantic-release` MUST be listed as a dev dependency.
- **FR-005**: The build command MUST build only `packages/pyscaf-core` (not the workspace root).

## Success Criteria

- **SC-001**: After a `feat:` commit on main, a new GitHub release is created within 5 minutes.
- **SC-002**: The TestPyPI package is installable after an automated release.
- **SC-003**: The production PyPI package is installable after a manual deploy.
- **SC-004**: Version is consistent across `pyproject.toml` and `__init__.py` after release.
