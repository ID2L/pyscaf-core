# Tâches — F601 + F602 + F603 (ordre d’implémentation)

Cocher au fil de l’`/implement`. Les chemins sont relatifs à la racine du monorepo.

---

## Préambule — Verrouillage workspace

- [ ] **T000** Exécuter `uv sync` à l’état actuel du repo (avant ajout des apps) pour disposer d’une base propre ; noter si `uv.lock` change (ne devrait pas).

---

## F601 — `apps/pyscaf`

### Métadonnées et build

- [ ] **T101** Créer `apps/pyscaf/pyproject.toml` avec :
  - `[project]` : `name = "pyscaf-app"`, `version = "0.1.0"`, `requires-python = ">=3.12"`.
  - `dependencies = ["pyscaf-core", "tomli", "tomli-w"]` (bornes minimales explicites, ex. `tomli>=2.0.0`, `tomli-w>=1.0.0`).
  - `[project.scripts]` : `pyscaf-app = "pyscaf_app.main:main"`.
  - `[project.entry-points."pyscaf_core.plugins"]` — 8 lignes :
    - `core = "pyscaf_app.actions.core:CoreAction"`
    - `git = "pyscaf_app.actions.git:GitAction"`
    - `license = "pyscaf_app.actions.license:LicenseAction"`
    - `jupyter = "pyscaf_app.actions.jupyter:JupyterAction"`
    - `test = "pyscaf_app.actions.test:TestAction"`
    - `semantic_release = "pyscaf_app.actions.semantic_release:SemanticReleaseAction"`
    - `documentation = "pyscaf_app.actions.documentation:DocumentationAction"`
    - `jupyter_tools = "pyscaf_app.actions.jupyter_tools:JupyterToolsAction"`
  - `[build-system]` : `hatchling>=1.26.0`, backend `hatchling.build`.
  - `[tool.hatch.build.targets.wheel] packages = ["src/pyscaf_app"]`.
  - `[tool.uv.sources] pyscaf-core = { workspace = true }`.

### Package racine

- [ ] **T102** Créer `apps/pyscaf/src/pyscaf_app/__init__.py` : `__version__ = "0.1.0"`.

- [ ] **T103** Créer `apps/pyscaf/src/pyscaf_app/main.py` :
  - Imports : `build_cli`, `make_main` depuis `pyscaf_core` ; `__version__` depuis `pyscaf_app` ; `discover_actions` depuis `pyscaf_app.actions`.
  - `cli = build_cli(app_name="pyscaf-app", version=__version__, discover=discover_actions)`.
  - `main = make_main(cli)` et bloc `if __name__ == "__main__": main()`.

### Découverte d’actions

- [ ] **T104** Créer `apps/pyscaf/src/pyscaf_app/actions/__init__.py` :
  - `import os`
  - `from pyscaf_core.actions import discover_actions_from_package`
  - Fonction `discover_actions()` qui retourne `discover_actions_from_package(os.path.dirname(__file__), "pyscaf_app.actions")`.

### Stubs d’actions (8 sous-packages)

Pour chaque tâche **T105–T112**, créer `apps/pyscaf/src/pyscaf_app/actions/<module>/__init__.py` avec une classe `*Action(Action)` :
- `depends: set[str] = set()`
- `run_preferably_after: str | None = None`
- `cli_options: list = []` (ou `list[CLIOption] = []` avec import `CLIOption` depuis `pyscaf_core`)
- `from pyscaf_core import Action` en tête.

- [ ] **T105** `actions/core/__init__.py` — classe `CoreAction`.
- [ ] **T106** `actions/git/__init__.py` — `GitAction`.
- [ ] **T107** `actions/license/__init__.py` — `LicenseAction`.
- [ ] **T108** `actions/jupyter/__init__.py` — `JupyterAction`.
- [ ] **T109** `actions/test/__init__.py` — `TestAction`.
- [ ] **T110** `actions/semantic_release/__init__.py` — `SemanticReleaseAction`.
- [ ] **T111** `actions/documentation/__init__.py` — `DocumentationAction`.
- [ ] **T112** `actions/jupyter_tools/__init__.py` — `JupyterToolsAction`.

### F602 — Exemple d’arborescence template (pyscaf)

- [ ] **T113** Créer `apps/pyscaf/src/pyscaf_app/actions/core/templates/.gitkeep` (fichier vide) pour matérialiser le pattern « templates à côté du module » ; documenter dans `README.md` (T119) l’usage de `Path(__file__).resolve().parent / "templates"`.

---

## F601 — `apps/septeo-scaf`

### Métadonnées et build

- [ ] **T201** Créer `apps/septeo-scaf/pyproject.toml` avec :
  - `name = "septeo-scaf"`, `version = "0.1.0"`, `requires-python = ">=3.12"`.
  - `dependencies = ["pyscaf-core", "jinja2", "tomlkit"]` (bornes minimales raisonnables).
  - `[project.scripts] septeo-scaf = "septeo_scaf.main:main"`.
  - `[project.entry-points."pyscaf_core.plugins"]` — 17 lignes, cibles `septeo_scaf.actions.<pkg>:<Class>` :
    - `core` → `CoreAction`
    - `agents` → `AgentsAction`
    - `rules` → `RulesAction`
    - `skills` → `SkillsAction`
    - `mcp` → `McpAction`
    - `ide_binding` → `IdeBindingAction`
    - `git` → `GitAction`
    - `python` → `PythonAction`
    - `php` → `PhpAction`
    - `javascript` → `JavascriptAction`
    - `database` → `DatabaseAction`
    - `docker` → `DockerAction`
    - `localstack` → `LocalstackAction`
    - `env_config` → `EnvConfigAction`
    - `docs_starlight` → `DocsStarlightAction`
    - `i18n` → `I18nAction`
    - `pipeline` → `PipelineAction`
  - Hatchling + `packages = ["src/septeo_scaf"]` + `[tool.uv.sources]` comme ci-dessus.

### Package racine et CLI

- [ ] **T202** Créer `apps/septeo-scaf/src/septeo_scaf/__init__.py` : `__version__ = "0.1.0"`.

- [ ] **T203** Créer `apps/septeo-scaf/src/septeo_scaf/main.py` : même pattern que T103 avec `app_name="septeo-scaf"`, imports `septeo_scaf`.

- [ ] **T204** Créer `apps/septeo-scaf/src/septeo_scaf/actions/__init__.py` : `discover_actions_from_package(..., "septeo_scaf.actions")`.

### Stubs d’actions (17 sous-packages)

Même squelette de classe que pour pyscaf-app (depends / run_preferably_after / cli_options vides).

- [ ] **T205** `actions/core/__init__.py` — `CoreAction`.
- [ ] **T206** `actions/agents/__init__.py` — `AgentsAction`.
- [ ] **T207** `actions/rules/__init__.py` — `RulesAction`.
- [ ] **T208** `actions/skills/__init__.py` — `SkillsAction`.
- [ ] **T209** `actions/mcp/__init__.py` — `McpAction`.
- [ ] **T210** `actions/ide_binding/__init__.py` — `IdeBindingAction`.
- [ ] **T211** `actions/git/__init__.py` — `GitAction`.
- [ ] **T212** `actions/python/__init__.py` — `PythonAction`.
- [ ] **T213** `actions/php/__init__.py` — `PhpAction`.
- [ ] **T214** `actions/javascript/__init__.py` — `JavascriptAction`.
- [ ] **T215** `actions/database/__init__.py` — `DatabaseAction`.
- [ ] **T216** `actions/docker/__init__.py` — `DockerAction`.
- [ ] **T217** `actions/localstack/__init__.py` — `LocalstackAction`.
- [ ] **T218** `actions/env_config/__init__.py` — `EnvConfigAction`.
- [ ] **T219** `actions/docs_starlight/__init__.py` — `DocsStarlightAction`.
- [ ] **T220** `actions/i18n/__init__.py` — `I18nAction`.
- [ ] **T221** `actions/pipeline/__init__.py` — `PipelineAction`.

### F602 — Exemple template (septeo)

- [ ] **T222** Créer `apps/septeo-scaf/src/septeo_scaf/actions/core/templates/.gitkeep`.

---

## F602 — Documentation courte (optionnelle mais recommandée)

- [ ] **T301** Créer `apps/pyscaf/README.md` (quelques phrases) : objectif stress-test Phase 7, liste des 8 actions, rappel du pattern chemins `Path(__file__).resolve().parent / "templates"` et inclusion Hatchling.

- [ ] **T302** Créer `apps/septeo-scaf/README.md` : objectif Phase 8, liste des 17 actions, même rappel F602 + mention Jinja2 / tomlkit.

---

## F603 — Pytest racine + tests apps

- [ ] **T401** Modifier `pyproject.toml` **à la racine** : dans `[tool.pytest.ini_options]`, étendre `testpaths` pour inclure `"apps/pyscaf/tests"` et `"apps/septeo-scaf/tests"` (conserver l’ordre existant pour les entrées déjà présentes, ajouter les nouvelles en fin de liste).

- [ ] **T402** Créer `apps/pyscaf/tests/__init__.py` (fichier vide ou docstring courte).

- [ ] **T403** Créer `apps/pyscaf/tests/test_smoke.py` :
  - `from click.testing import CliRunner`
  - `from pyscaf_core import Action`
  - `from pyscaf_app.actions import discover_actions`
  - `from pyscaf_app.main import cli`
  - Test `test_cli_help` : `invoke(cli, ["--help"])`, assert code 0 et `"pyscaf-app"` dans la sortie.
  - Test `test_discover_actions_count` : `len(discover_actions()) == 8` et chaque élément `issubclass(..., Action)`.

- [ ] **T404** Créer `apps/septeo-scaf/tests/__init__.py`.

- [ ] **T405** Créer `apps/septeo-scaf/tests/test_smoke.py` : même structure que T403 avec `septeo_scaf`, `septeo-scaf`, et `len(...) == 17`.

---

## Fermeture — Lock et validation

- [ ] **T501** Exécuter `uv lock` ou `uv sync` depuis la racine ; valider que `uv.lock` inclut `pyscaf-app` et `septeo-scaf` ; commiter le lock mis à jour.

- [ ] **T502** `uv run ruff check packages/pyscaf-core apps/demo-scaf apps/pyscaf apps/septeo-scaf` — 0 erreur.

- [ ] **T503** `uv run pytest` — tous les tests verts.

- [ ] **T504** `uv run pyscaf-app --help` et `uv run septeo-scaf --help` — code 0.

---

## Récapitulatif des fichiers créés / modifiés

| Fichier | Action |
|---------|--------|
| `apps/pyscaf/pyproject.toml` | créer |
| `apps/pyscaf/README.md` | créer (T301) |
| `apps/pyscaf/src/pyscaf_app/__init__.py` | créer |
| `apps/pyscaf/src/pyscaf_app/main.py` | créer |
| `apps/pyscaf/src/pyscaf_app/actions/__init__.py` | créer |
| `apps/pyscaf/src/pyscaf_app/actions/*/__init__.py` | créer ×8 |
| `apps/pyscaf/src/pyscaf_app/actions/core/templates/.gitkeep` | créer |
| `apps/pyscaf/tests/__init__.py` | créer |
| `apps/pyscaf/tests/test_smoke.py` | créer |
| `apps/septeo-scaf/pyproject.toml` | créer |
| `apps/septeo-scaf/README.md` | créer (T302) |
| `apps/septeo-scaf/src/septeo_scaf/...` | créer (miroir) |
| `apps/septeo-scaf/tests/...` | créer |
| `pyproject.toml` (racine) | modifier `testpaths` |
| `uv.lock` | mettre à jour via uv |
