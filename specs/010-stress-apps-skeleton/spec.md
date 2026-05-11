# F601 + F602 + F603 — Fondation des apps stress-test (squelettes, assets, pytest)

**IDs** : F601, F602, F603  
**Phase** : 6 (stress-test)  
**Statut** : Spécification  
**Hors périmètre** : F604 (Docker / CI conteneurisée) — traité séparément.

## Synthèse

Livrable unique couvrant trois briques liées :

| ID | Thème | Objectif |
|----|--------|----------|
| **F601** | Squelettes d’apps | Ajouter `apps/pyscaf` et `apps/septeo-scaf` comme membres workspace (déjà couverts par `apps/*`), avec layout `src/`, dépendance `pyscaf-core` (workspace), scripts CLI, découverte d’actions via `discover_actions_from_package`, et entry points `pyscaf_core.plugins` pour chaque action (stubs). |
| **F602** | Templates / assets | Convention d’accès aux fichiers statiques à l’exécution : chemins relatifs à `__file__`, empaquetage via Hatchling (arbre `src/` inclus). Pas d’obligation d’`importlib.resources` pour cette phase. |
| **F603** | Pytest monorepo | Étendre `testpaths` à la racine et créer les répertoires de tests des deux apps avec au moins un test placeholder ou smoke CLI. |

## Contexte

- Le monorepo dispose déjà de `packages/pyscaf-core` et `apps/demo-scaf`.
- Le moteur expose `discover_actions_from_package(package_path, package_name)` dans `pyscaf_core.actions` (découverte par `pkgutil` des modules **immédiats** sous le répertoire `actions/`, en ignorant les noms réservés `base` et `manager`).
- Lorsque `build_cli(..., discover=...)` est utilisé, la liste d’actions provient **uniquement** du callable `discover` (les entry points ne sont pas fusionnés automatiquement avec cette liste). Les entry points restent **requis** pour alignement roadmap, parité wheel/éditable, et phases ultérieures (F701, F801, F902).

## F601 — Exigences fonctionnelles

### Workspace et empaquetage

- Les répertoires `apps/pyscaf/` et `apps/septeo-scaf/` existent avec un `pyproject.toml` valide, build Hatchling, layout `src/<package>/`.
- Chaque app déclare `pyscaf-core` en dépendance avec `[tool.uv.sources] pyscaf-core = { workspace = true }`.
- `requires-python = ">=3.12"` (aligné sur le reste du monorepo).

### Application `apps/pyscaf` (distribution `pyscaf-app`)

- **Nom de distribution** : `pyscaf-app` (évite la collision avec le paquet PyPI `open-pyscaf` / confusion de nommage).
- **Import Python** : `pyscaf_app` (répertoire `src/pyscaf_app/`).
- **Script console** : `pyscaf-app` → `pyscaf_app.main:main`.
- **Actions prévues (8)** — une classe stub par action, enregistrée en entry point et découverte via le package `actions` :
  - `core`, `git`, `license`, `jupyter`, `test`, `semantic_release`, `documentation`, `jupyter_tools`.
- **Dépendances supplémentaires** : `tomli`, `tomli-w` (manipulation `pyproject.toml` côté CoreAction en phases suivantes). **Pas** de `jinja2` sur cette app.
- **CLI** : `main.py` utilise `build_cli(app_name="pyscaf-app", version=..., discover=discover_actions)` et `make_main`, comme `demo-scaf`.
- **Découverte** : `actions/__init__.py` expose `discover_actions()` qui délègue à `discover_actions_from_package` avec le chemin du répertoire `actions` et le nom qualifié `pyscaf_app.actions`.

### Application `apps/septeo-scaf`

- **Nom de distribution** : `septeo-scaf`.
- **Import Python** : `septeo_scaf` (`src/septeo_scaf/`).
- **Script console** : `septeo-scaf` → `septeo_scaf.main:main`.
- **Actions prévues (17 modules)** — stubs + entry points :
  - `core`, `agents`, `rules`, `skills`, `mcp`, `ide_binding`, `git`, `python`, `php`, `javascript`, `database`, `docker`, `localstack`, `env_config`, `docs_starlight`, `i18n`, `pipeline`.
- **Dépendances supplémentaires** : `jinja2`, `tomlkit` (usage direct prévu dans l’app même si `tomlkit` est déjà transitif via le core).

### Stubs d’actions (cette phase)

- Chaque action est une sous-classe de `Action` avec :
  - `depends: set[str]` explicite (vide `{}` acceptable pour tous les stubs) ;
  - `run_preferably_after: str | None` explicite ;
  - `cli_options: list[CLIOption] = []` (aucune option CLI pour l’instant).
- Pas d’implémentation métier : les méthodes héritées par défaut (`skeleton` vide, `init` / `install` par défaut) suffisent.
- Nommage des classes : suffixe `Action` (ex. `CoreAction`, `GitAction`, `SemanticReleaseAction`, `JupyterToolsAction`, `DocsStarlightAction`).

### Structure de package `actions/` (lien avec F602)

- Pour chaque action nommée `<name>`, le code vit dans un **sous-package** `actions/<name>/` avec `__init__.py` contenant la classe, afin de pouvoir ajouter sans refonte `actions/<name>/templates/`, `config.toml`, `template.gitignore`, etc., au même niveau que dans les projets sources de référence.
- `discover_actions_from_package` importe `pyscaf_app.actions.<name>` (ou `septeo_scaf.actions.<name>`) et collecte les sous-classes de `Action` exportées dans ce module.

## F602 — Exigences (convention templates / assets)

- Les fichiers statiques résident **à côté** du code de l’action : par exemple `actions/core/templates/`, `actions/core/config.toml`.
- **Pattern recommandé** à l’exécution :  
  `Path(__file__).resolve().parent / "templates"`  
  ou  
  `Path(__file__).resolve().parent / "config.toml"`  
  depuis un module dans `actions/<name>/`.
- **Empaquetage** : la directive Hatchling `packages = ["src/<import_package>"]` inclut l’arbre complet sous `src/` ; pas besoin d’`importlib.resources` pour cette phase (install éditable et wheel conservent la hiérarchie de fichiers).
- La spec / plan documente ce choix ; une action exemple peut inclure `templates/.gitkeep` pour matérialiser l’arborescence (optionnel mais utile pour la revue).

## F603 — Exigences (pytest)

- Le fichier racine `pyproject.toml` section `[tool.pytest.ini_options]` étend `testpaths` avec :
  - `apps/pyscaf/tests`
  - `apps/septeo-scaf/tests`
- Chaque app possède un répertoire `tests/` avec au minimum :
  - un `__init__.py` (package de tests), **et**
  - un fichier de test minimal (smoke : import, ou `CliRunner` sur `--help`, ou nombre d’actions découvertes).

## Critères d’acceptation mesurables

1. `uv sync` à la racine du monorepo résout et installe **sans erreur** `pyscaf-core`, `pyscaf-app`, `septeo-scaf` (et les autres membres existants).
2. `uv run pyscaf-app --help` et `uv run septeo-scaf --help` retournent un code de sortie 0 et affichent le nom d’app attendu.
3. `uv run pytest` depuis la racine collecte et exécute les tests sous `packages/pyscaf-core/tests`, `apps/demo-scaf/tests`, `apps/pyscaf/tests`, `apps/septeo-scaf/tests`.
4. Chaque app déclare **tous** les entry points `pyscaf_core.plugins` listés ci-dessus pour les stubs.
5. `discover_actions()` dans chaque app retourne **exactement** le même nombre de classes d’actions que d’entry points déclarés pour les stubs (8 et 17 respectivement), sans doublon ni module réservé (`base`, `manager`).

## Validation (hors F604)

Pour cette spec combinée, la validation est **locale / uv** (cohérent avec la Phase 5 sans Docker obligatoire jusqu’à F604) :

```bash
uv sync
uv run ruff check packages/pyscaf-core apps/demo-scaf apps/pyscaf apps/septeo-scaf
uv run pytest
uv run pyscaf-app --help
uv run septeo-scaf --help
```

## Dépendances

- Phases 0–5 complètes (moteur, `demo-scaf`, `discover_actions_from_package`).
- F604 pourra ajouter la couche Docker décrite dans `specs/roadmap/roadmap-stress-test.md`.

## Références

- `specs/roadmap/roadmap-stress-test.md`
- `specs/roadmap/feature-inventory-stress-test.md`
- Pattern de référence : `apps/demo-scaf/`
