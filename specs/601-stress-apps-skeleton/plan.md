# Plan technique — F601 + F602 + F603

## Principes

- **Pas de modification du moteur** `pyscaf-core` pour cette spec (sauf découverte ultérieure d’écart bloquant — hors périmètre nominal).
- **Même famille d’outils** que `demo-scaf` : Hatchling, `src/` layout, uv workspace.
- **Découverte** : `from pyscaf_core.actions import discover_actions_from_package` (non ré-exporté depuis `pyscaf_core` racine).

## F601 — Arborescence cible

### `apps/pyscaf/`

```text
apps/pyscaf/
├── pyproject.toml
├── README.md                    # optionnel court : rôle de l’app + lien roadmap (recommandé)
└── src/
    └── pyscaf_app/
        ├── __init__.py          # __version__ = "0.1.0"
        ├── main.py
        └── actions/
            ├── __init__.py      # discover_actions()
            ├── core/
            │   ├── __init__.py  # CoreAction stub
            │   └── templates/
            │       └── .gitkeep # exemple F602 (optionnel mais illustratif)
            ├── git/__init__.py
            ├── license/__init__.py
            ├── jupyter/__init__.py
            ├── test/__init__.py
            ├── semantic_release/__init__.py
            ├── documentation/__init__.py
            └── jupyter_tools/__init__.py
```

### `apps/septeo-scaf/`

```text
apps/septeo-scaf/
├── pyproject.toml
├── README.md                    # optionnel (recommandé)
└── src/
    └── septeo_scaf/
        ├── __init__.py
        ├── main.py
        └── actions/
            ├── __init__.py
            ├── core/
            │   ├── __init__.py
            │   └── templates/.gitkeep
            ├── agents/__init__.py
            ├── rules/__init__.py
            ├── skills/__init__.py
            ├── mcp/__init__.py
            ├── ide_binding/__init__.py
            ├── git/__init__.py
            ├── python/__init__.py
            ├── php/__init__.py
            ├── javascript/__init__.py
            ├── database/__init__.py
            ├── docker/__init__.py
            ├── localstack/__init__.py
            ├── env_config/__init__.py
            ├── docs_starlight/__init__.py
            ├── i18n/__init__.py
            └── pipeline/__init__.py
```

**Note** : le module Python `test` est un nom légal pour un sous-package `actions/test/` ; à l’import `septeo_scaf.actions.test` il n’entre pas en conflit avec le paquet stdlib `test` tant que l’import reste qualifié. Pour `pyscaf-app` uniquement, l’action s’appelle aussi `test` — même remarque.

## F601 — `pyproject.toml` (champs clés)

### `pyscaf-app`

- `[project] name = "pyscaf-app"`, `version = "0.1.0"`.
- `dependencies = ["pyscaf-core", "tomli", "tomli-w"]` (versions avec borne minimale raisonnable, ex. `>=2`, `>=1.0` selon écosystème).
- `[project.scripts] pyscaf-app = "pyscaf_app.main:main"`.
- `[project.entry-points."pyscaf_core.plugins"]` : une ligne par action, valeur `pyscaf_app.actions.<pkg>:<ClassName>`.
- `[tool.hatch.build.targets.wheel] packages = ["src/pyscaf_app"]`.
- `[tool.uv.sources] pyscaf-core = { workspace = true }`.

### `septeo-scaf`

- `dependencies = ["pyscaf-core", "jinja2", "tomlkit"]`.
- `[project.scripts] septeo-scaf = "septeo_scaf.main:main"`.
- Entry points pour les 17 actions.
- `packages = ["src/septeo_scaf"]`.

## F601 — Fichiers Python

### `__init__.py` (racine package)

Identique en esprit à `demo-scaf` :

```python
__version__ = "0.1.0"
```

### `main.py`

```python
from pyscaf_core import build_cli, make_main
from pyscaf_app import __version__
from pyscaf_app.actions import discover_actions

cli = build_cli(app_name="pyscaf-app", version=__version__, discover=discover_actions)
main = make_main(cli)

if __name__ == "__main__":
    main()
```

Adapter `app_name`, imports et `__version__` pour `septeo-scaf` (`septeo-scaf`, `septeo_scaf`).

### `actions/__init__.py`

```python
import os

from pyscaf_core.actions import discover_actions_from_package


def discover_actions():
    package_dir = os.path.dirname(__file__)
    return discover_actions_from_package(package_dir, "pyscaf_app.actions")
```

Remplacer `pyscaf_app.actions` par `septeo_scaf.actions` dans l’app Septeo.

### Stub par action (`actions/<name>/__init__.py`)

Modèle (à dupliquer avec noms de classe adaptés) :

```python
from pyscaf_core import Action


class XxxAction(Action):
    depends: set[str] = set()
    run_preferably_after: str | None = None
    cli_options: list = []
```

- Utiliser `list` vide pour éviter l’import `CLIOption` si aucune option ; ou `from pyscaf_core import CLIOption` et `cli_options: list[CLIOption] = []` pour cohérence typée.
- Noms de classes : voir tableau ci-dessous.

| Module (`actions/<pkg>/`) | Classe |
|---------------------------|--------|
| `core` | `CoreAction` |
| `git` | `GitAction` |
| `license` | `LicenseAction` |
| `jupyter` | `JupyterAction` |
| `test` | `TestAction` |
| `semantic_release` | `SemanticReleaseAction` |
| `documentation` | `DocumentationAction` |
| `jupyter_tools` | `JupyterToolsAction` |

Septeo : `AgentsAction`, `RulesAction`, `SkillsAction`, `McpAction`, `IdeBindingAction`, `PythonAction`, `PhpAction`, `JavascriptAction`, `DatabaseAction`, `DockerAction`, `LocalstackAction`, `EnvConfigAction`, `DocsStarlightAction`, `I18nAction`, `PipelineAction`, plus `CoreAction`, `GitAction` communs.

## F602 — Rappel implémentation

- Documenter dans `README.md` de chaque app (ou commentaire dans `plan.md` / spec — déjà dans `spec.md`) le snippet `Path(__file__).resolve().parent / "templates"`.
- Les phases 7/8 utiliseront ce pattern dans `skeleton()`, `init()`, ou helpers dédiés.

## F603 — Racine `pyproject.toml`

Remplacer / étendre :

```toml
[tool.pytest.ini_options]
testpaths = [
    "packages/pyscaf-core/tests",
    "apps/demo-scaf/tests",
    "apps/pyscaf/tests",
    "apps/septeo-scaf/tests",
]
```

## F603 — Tests applicatifs

Structure :

```text
apps/pyscaf/tests/__init__.py
apps/pyscaf/tests/test_smoke.py
apps/septeo-scaf/tests/__init__.py
apps/septeo-scaf/tests/test_smoke.py
```

Contenu suggéré pour `test_smoke.py` :

- Importer `cli` depuis `<pkg>.main`.
- `CliRunner().invoke(cli, ["--help"])` → `exit_code == 0` et chaîne attendue dans la sortie.
- Importer `discover_actions` depuis `<pkg>.actions` ; assert `len(discover_actions()) == N` (8 ou 17).

## Verrou `uv.lock`

- Après ajout des apps, exécuter `uv lock` (ou `uv sync` qui met à jour le lock) et **commiter** `uv.lock` mis à jour.

## Ordre d’implémentation recommandé

1. Créer `apps/pyscaf` (pyproject + arborescence + stubs + tests).
2. Créer `apps/septeo-scaf` (idem).
3. Mettre à jour racine `pyproject.toml` (`testpaths`).
4. `uv sync`, `ruff`, `pytest`, smoke CLI.
