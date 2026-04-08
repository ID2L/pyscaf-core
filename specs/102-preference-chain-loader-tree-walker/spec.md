# F102 — Port `dependency_loader` and `tree_walker`

**Feature ID**: F102  
**Phase**: 1  
**Status**: Ready for implementation  
**Dependencies**: F101  

## Scope

Port **`dependency_loader.py`** and **`tree_walker.py`** from Septeo into `pyscaf_core.preference_chain`, wire **public exports** in `preference_chain/__init__.py`, and align with project **logging policy** (no `print` in core for diagnostics).

**Source reference**

- `~/lab/septeo-agentic-scaffolder/src/septeo_scaffolder/preference_chain/dependency_loader.py`
- `~/lab/septeo-agentic-scaffolder/src/septeo_scaffolder/preference_chain/tree_walker.py`

## Behavioral requirements

### `dependency_loader.py`

- **`load_and_complete_dependencies(yaml_path: str) -> list[Node]`**
  - Load YAML list of dependency entries with keys `id`, optional `depends`, optional `after`.
  - Construct **`Node`** instances (Pydantic validation).
  - Completion rules when `after is None` and `depends` has exactly one element: set `after` to that element (same as Septeo).
  - **Logging**: on `ValidationError`, log at **`warning`** (or `error` if you prefer strictness) with entry id context; **do not** use `print`.
  - Multiple `depends` without `after`: log **`warning`** with message equivalent to Septeo’s WARNING string; still append the node (Septeo behavior) unless tests dictate otherwise — **F103** may not cover loader; if no tests, preserve Septeo behavior verbatim.

- **`build_dependency_tree(dependencies: list[Node], root_id: str) -> tuple[dict, set[str]]`**
  - Same algorithm as Septeo: walk `after` links from `root_id`, collect `extra_depends` for multi-dependency nodes.

### `tree_walker.py`

- **`DependencyTreeWalker`**
  - `__init__(dependencies: list[Node], root_id: str)` builds internal tree like Septeo.
  - Attributes: `tree`, `external_depends`, `fullfilled_depends` (keep Septeo spelling **`fullfilled`** for API compatibility unless F103 renames — prefer **keep** to avoid silent breakage).
  - **`print_tree(self) -> None`**: Septeo uses **`print`** for ASCII tree rendering. **Decision**: this is **UX/debug output**; options:
    1. Keep `print` only in `print_tree` (document as intentional CLI-style helper), or
    2. Refactor to `format_tree() -> str` + logger/debug (breaking for anyone who relied on stdout only).

  **Spec recommendation**: implement **`format_tree() -> str`** and make **`print_tree`** call `print(self.format_tree())` for backward compatibility, so tests can assert on string without capturing stdout if needed later. If that is too much scope, **preserve Septeo `print_tree` verbatim** and document exception to “no print in core” for this debug helper.

## Dependencies to add

- **`pyyaml`** (or `ruamel.yaml` if project standardizes later; Septeo uses `yaml.safe_load` from PyYAML) on **`pyscaf-core`** package.

## Directory and file structure

```text
packages/pyscaf-core/src/pyscaf_core/preference_chain/
├── __init__.py              # add to __all__: DependencyTreeWalker, load_and_complete_dependencies
├── dependency_loader.py
└── tree_walker.py
```

Update **`__all__`** to include:

- `DependencyTreeWalker`
- `load_and_complete_dependencies`
- `build_dependency_tree` (if exported from Septeo `__init__` — Septeo root `__init__.py` exports `load_and_complete_dependencies` only; **`build_dependency_tree`** is used internally — export from submodule or add to `__all__` if useful for docs/tests).

Septeo `preference_chain/__init__.py` exports:

- `load_and_complete_dependencies`
- `DependencyTreeWalker`

Match that minimum; exporting `build_dependency_tree` is optional.

## Acceptance criteria

- [ ] YAML loader completes nodes per Septeo rules; invalid entries are logged, not silently dropped without trace (see logging above).
- [ ] `DependencyTreeWalker` builds the same tree structure as Septeo for equivalent inputs.
- [ ] `pyscaf_core.preference_chain` re-exports walker and loader per `__all__`.
- [ ] Core does not introduce Septeo or `pyscaf` imports.

## Dependencies on other features

- **F101**: `Node` and package layout.

## Validation (Docker only)

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run python -c \"
from pyscaf_core.preference_chain import DependencyTreeWalker, load_and_complete_dependencies
from pyscaf_core.preference_chain.model import Node
w = DependencyTreeWalker([Node(id='r', depends=set(), after=None), Node(id='c', depends={'r'}, after='r')], 'r')
assert w.tree is not None
print('ok')
\""
```

Optional: small fixture YAML in `packages/pyscaf-core/tests/fixtures/` when F103 extends coverage.

## Notes

- If F103 only covers `best_execution_order`, add **minimal new tests** for loader/walker in F102 or F103 follow-up to prevent regressions.
