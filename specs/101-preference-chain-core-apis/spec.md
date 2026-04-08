# F101 — Port preference chain: models, chain resolution, `best_execution_order`

**Feature ID**: F101  
**Phase**: 1  
**Status**: Ready for implementation  
**Dependencies**: F002  

## Scope

Port the **preference chain** engine from `septeo-agentic-scaffolder` into `pyscaf_core.preference_chain` with **no dependency** on Click, actions, or Septeo-specific packages. Preserve public behavior and API shape so existing tests (F103) can be ported with import renames only.

**Source reference** (read-only, sibling repo):

- `~/lab/septeo-agentic-scaffolder/src/septeo_scaffolder/preference_chain/`

**Public surface** (must match semantics; adjust imports to `pyscaf_core`):

| Symbol | Module |
|--------|--------|
| `Node`, `ExtendedNode`, `ChainLink` | `model.py` |
| `CircularDependencyError` | `circular_dependency_error.py` |
| `extend_nodes`, `build_chains`, `compute_all_resolution_pathes`, `compute_path_score` | `chain.py` |
| `best_execution_order` | `__init__.py` (or dedicated module re-exported in `__init__`) |

**Typos / API stability**

- Keep the name **`compute_all_resolution_pathes`** (historical spelling) unless a follow-up ADR explicitly renames; F103 tests should use the same name as Septeo for a mechanical port.

**Dependencies to add** (`packages/pyscaf-core/pyproject.toml`)

- **`pydantic`** (v2), aligned with Septeo `BaseModel` usage in `model.py`.
- **No** `pyyaml` in F101 unless F101 inappropriately pulls loader code — **F102** adds YAML for `dependency_loader`.

**Logging**

- Replace any remaining `print` in ported chain code with **`logging`** (project decision). F101 chain/model/circular error modules should use `logger = logging.getLogger(__name__)` like Septeo’s `chain.py` and `__init__.py`.

**Out of scope**

- `dependency_loader.py`, `tree_walker.py` (F102).
- Unit tests beyond what F103 specifies (F103 ports `tests/preference_chain/`).

## Directory and file structure

```text
packages/pyscaf-core/src/pyscaf_core/preference_chain/
├── __init__.py              # __all__, best_execution_order, re-exports
├── circular_dependency_error.py
├── chain.py
└── model.py
```

### `__init__.py` contract

Re-export at minimum:

```python
__all__ = [
    "CircularDependencyError",
    "best_execution_order",
    "build_chains",
    "compute_all_resolution_pathes",
    "compute_path_score",
    "extend_nodes",
    # F102 will add: DependencyTreeWalker, load_and_complete_dependencies, build_dependency_tree
]
```

Until F102 lands, either omit F102 symbols from `__all__` or add F102 in the same PR series; **recommended**: F101 implements only the four files above; F102 extends `__init__.py`.

### `best_execution_order` behavior (summary)

- Normalize `Node.after`: if `depends` non-empty and `after is None`, set effective `after` to `next(iter(depends))`.
- Raise **`ValueError`** if `after` is set but not in `depends` (same message pattern as Septeo).
- **`extend_nodes`** → **`build_chains`** → **`compute_all_resolution_pathes`** → sort paths by **`-compute_path_score`** → flatten chain IDs to ordered node IDs.
- Raise **`CircularDependencyError`** when no resolution paths exist or when chain build detects a loop (see Septeo `build_chains`).

## Interface reference (concise)

```python
from pydantic import BaseModel

class Node(BaseModel):
    id: str
    depends: set[str] = set()
    after: str | None = None

    @property
    def external_dependencies(self) -> set[str]: ...

class ExtendedNode(Node):
    referenced_by: set[str] = set()

class ChainLink(BaseModel):
    children: list[ExtendedNode]
    head: ExtendedNode
    tail: ExtendedNode
    # properties: ids, external_dependencies, depends, referenced_by

def extend_nodes(tree: list[Node]) -> list[ExtendedNode]: ...
def build_chains(tree: list[ExtendedNode]) -> list[ChainLink]: ...
def compute_all_resolution_pathes(chains: list[ChainLink]) -> list[list[ChainLink]]: ...
def compute_path_score(path: list[ChainLink]) -> int: ...
def best_execution_order(nodes: list[Node]) -> list[str]: ...
```

## Acceptance criteria

- [ ] Subpackage **`pyscaf_core.preference_chain`** imports without optional deps beyond pydantic.
- [ ] **`best_execution_order`** implements the same normalization, scoring, and error cases as Septeo (F103 proves parity).
- [ ] **`CircularDependencyError`** is a dedicated exception type subclassing `Exception`.
- [ ] **No imports** from `click`, `pyscaf_core.actions`, or app packages.
- [ ] Ruff/pytest green in Docker (F103 adds tests; until then F101 can rely on F103 same-PR or temporary smoke test).

## Dependencies on other features

- **F002**: package layout and `pyproject.toml`.

## Validation (Docker only)

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run python -c \"
from pyscaf_core.preference_chain import best_execution_order
from pyscaf_core.preference_chain.model import Node
print(best_execution_order([
    Node(id='A', depends=set(), after=None),
    Node(id='B', depends={'A'}, after='A'),
]))
\""
```

Full suite after F103:

```bash
docker run --rm -v "$PWD":/workspace -w /workspace pyscaf-core-dev \
  sh -c "uv sync --all-packages && uv run pytest packages/pyscaf-core/tests/preference_chain -q"
```

## Notes

- `~/lab/pyscaf` may have a simpler copy; **Septeo is the canonical source** for F101–F103 per roadmap.
