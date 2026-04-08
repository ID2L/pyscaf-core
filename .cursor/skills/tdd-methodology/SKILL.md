---
name: tdd-methodology
description: "Test-Driven Development patterns for this scaffolder project. Use when creating new features, fixing bugs, or refactoring existing code. Includes YAML-driven action tests, preference chain tests, and tool unit tests."
---

# TDD Methodology

This project follows **strict Test-Driven Development**. Every new action, tool, feature, or algorithm change MUST ship with tests. No PR is complete without test coverage.

## When to Use This Skill

- Creating a new feature or action
- Fixing a reported bug (write failing test first)
- Refactoring existing code (ensure tests exist before changing)
- Adding a new tool or utility

## Main Instructions

### Red-Green-Refactor Cycle

1. **Red**: Write a failing test that describes the expected behavior
2. **Green**: Write the minimum code to make the test pass
3. **Refactor**: Clean up while keeping tests green

### Three Test Patterns

| Pattern | Location | When to Use |
|---|---|---|
| **YAML-driven action tests** | `tests/actions/<action>/test_*.yaml` | Any new or modified Action |
| **Preference chain tests** | `tests/preference_chain/` | Dependency resolution changes |
| **Tool unit tests** | `tests/tools/test_*.py` | New or modified tools |

### YAML Test Format (for Actions)

```yaml
cli_arguments:
  options:
    versionning: true
    license: "mit"

checks:
  - name: "README exists"
    type: exist
    file_path: "tmp_project/README.md"
  - name: "Has MIT header"
    type: contains
    file_path: "tmp_project/LICENSE"
    content: "MIT License"
  - name: "No unwanted file"
    type: not_exist
    file_path: "tmp_project/.env"
```

Check types: `exist`, `not_exist`, `contains`, `not_contains`, `custom`

### Tool Unit Tests

```python
import tempfile
from pathlib import Path

def test_my_tool():
    with tempfile.TemporaryDirectory() as tmp:
        # Arrange
        input_path = Path(tmp) / "input.toml"
        input_path.write_text("[tool]\nkey = 'value'\n")

        # Act
        result = my_tool(input_path)

        # Assert
        assert result == expected
```

### Running Tests

```bash
uv run pytest                                           # All tests
uv run pytest tests/actions/ -v                         # Action tests only
uv run pytest tests/actions/ --action-filter="core" -v  # Single action
uv run pytest tests/tools/ -v                           # Tool tests
uv run pytest -s --log-cli-level=DEBUG                  # With debug output
```

## Project-Specific Context

- Test framework: pytest 8.x with pytest-cov, pytest-mock, pytest-xdist
- Action tests use `ActionTestRunner` class that runs the CLI in a temp dir
- `conftest.py` adds `--action-filter` option for targeted test runs
- Coverage target: all new code must be covered

## Anti-Patterns

- Never write implementation before tests
- Never mock internal modules — only mock at boundaries (filesystem, network, subprocess)
- Never create tests that depend on other tests' state
- Never skip edge cases in test coverage
- Never commit with failing tests
