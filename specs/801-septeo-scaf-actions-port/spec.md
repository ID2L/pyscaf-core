# F801 (Phase 8) — Port des actions `septeo-agentic-scaffolder` vers `apps/septeo-scaf`

**ID** : fil conducteur **F801** ; lots d’implémentation **F802–F806** (voir `tasks.md`)  
**Statut** : Spécification  
**Source de vérité fonctionnelle** : dépôt local `~/lab/septeo-agentic-scaffolder`, package `septeo_scaffolder`, répertoire `src/septeo_scaffolder/actions/` (hors `manager.py`, hors agrégat `actions/__init__.py` du moteur — le monorepo utilise `pyscaf_core`).

## Synthèse

Porter les **implémentations réelles** des dix-sept actions du scaffolder Septeo vers le monorepo `pyscaf-core`, application `septeo-scaf`, sous `apps/septeo-scaf/src/septeo_scaf/actions/<module>/`. Les Phases 6–7 ont livré des **stubs**, un CLI opérationnel et la découverte via entry points ; cette phase remplace le corps des actions, copie les répertoires **`templates/`** (fichiers **Jinja2** `.j2`) et garantit la **parité de comportement** avec le dépôt source pour les options CLI conditionnelles et les hooks de contexte.

## Objectifs mesurables

1. **Couverture** : les dix-sept modules d’action listés ci-dessous contiennent la logique et les assets issus de `septeo-agentic-scaffolder`, pas seulement des stubs.
2. **Templates** : pour chaque action concernée, l’arborescence `templates/**/*.j2` (et tout autre fichier statique référencé par le code) est présente à côté de `__init__.py` dans `septeo_scaf`, avec résolution des chemins au runtime via `Path(__file__).parent`.
3. **Imports** : aucune dépendance résiduelle vers `septeo_scaffolder.*` dans le code porté ; primitives du moteur et outils partagés depuis `pyscaf_core` et `pyscaf_core.tools.*` ; imports croisés entre actions du même app en `septeo_scaf.actions.*` uniquement si la source le faisait déjà (sinon éviter).
4. **Contrats d’action** : `depends`, `run_preferably_after`, `cli_options` (y compris `visible_when`, `postfill_hook`, choix multiples), méthodes `skeleton` / `init` / `install` / `activate` **alignés sur la source**.  
   *Note* : certains stubs Phase 6–7 peuvent différer (ex. `depends` simplifiés) ; le port **corrige** pour refléter la source.
5. **Régression** : la suite de tests du monorepo reste verte ; des tests **F806** couvrent au minimum des scénarios `visible_when` / `postfill_hook` (Core) et un parcours d’intégration bout-en-bout contrôlé.

## Inventaire des actions

| # | Module | Classe (attendue) | Dépendances source (`depends`) | `run_preferably_after` source |
|---|--------|-------------------|--------------------------------|-------------------------------|
| 1 | `core` | `CoreAction` | `∅` | — |
| 2 | `git` | `GitAction` | `{core}` | `core` |
| 3 | `python` | `PythonAction` | `{core}` | `core` |
| 4 | `php` | `PhpAction` | `{core}` | `core` |
| 5 | `javascript` | `JavascriptAction` | `{core}` | `core` |
| 6 | `database` | `DatabaseAction` | `{core}` | `core` |
| 7 | `docker` | `DockerAction` | `{core}` | `core` |
| 8 | `localstack` | `LocalstackAction` | `{docker}` | `docker` |
| 9 | `env_config` | `EnvConfigAction` | `{core}` | `core` |
| 10 | `docs_starlight` | `DocsStarlightAction` | `{core}` | `core` |
| 11 | `i18n` | `I18nAction` | `{core}` | `core` |
| 12 | `pipeline` | `PipelineAction` | `{core, git}` | `git` |
| 13 | `agents` | `AgentsAction` | `{core}` | `core` |
| 14 | `rules` | `RulesAction` | `{agents}` | `agents` |
| 15 | `skills` | `SkillsAction` | `{agents}` | `agents` |
| 16 | `mcp` | `McpAction` | `{agents}` | `agents` |
| 17 | `ide_binding` | `IdeBindingAction` | `{agents}` | `agents` |

**Hors périmètre de copie** : `septeo_scaffolder/actions/manager.py`, mécanique `discover_actions` du package source — remplacés par `pyscaf_core`.

## Exigences fonctionnelles

### E1 — Fichiers à porter

Pour chaque ligne de l’inventaire : copier depuis la source le fichier `__init__.py` du module et, s’il existe, le répertoire **`templates/`** complet (fichiers `.j2` et toute ressource statique référencée). Ne pas omettre les sous-dossiers (ex. `docker/templates/dockerfiles/`, `skills/templates/...`).

### E2 — Modifications autorisées

1. **Imports** (obligatoire)  

   | Source | Cible |
   |--------|--------|
   | `from septeo_scaffolder.actions import Action, CLIOption, ChoiceOption` | `from pyscaf_core import Action, CLIOption, ChoiceOption` |
   | `from septeo_scaffolder.tools.*` | `from pyscaf_core.tools.*` |

2. **TOML** : ne pas introduire `tomli` / `tomli-w` pour le merge ; s’appuyer sur **`pyscaf_core.tools.toml_merge`** et **`pyscaf_core.tools.format_toml`** (implémentation déjà basée sur **tomlkit** côté core). Si une action source utilisait `tomlkit` en direct pour un cas non couvert par ces outils, conserver la logique en important **`tomlkit`** depuis la dépendance déjà déclarée dans `apps/septeo-scaf/pyproject.toml`.

3. **Journalisation** : harmoniser avec le moteur — remplacer `print` / `Console().print` de pilotage dans les `__init__.py` d’actions par `logging.getLogger(__name__)` (`info` / `warning` / `debug`), sauf pour des scripts ou snippets explicitement destinés au projet **généré** (conserver le comportement source si ceux-ci sont copiés tels quels).

4. **Jinja2** : conserver `Environment` + `FileSystemLoader`, `autoescape=False` pour les templates de scaffolding (comme la source), chemins basés sur le répertoire du module action.

### E3 — CoreAction et options conditionnelles

- Reproduire l’ensemble des `CLIOption` du **CoreAction** source, y compris **`visible_when`** (lambdas ou fonctions) et **`postfill_hook`** (ex. `_apps_postfill_hook` pour clés dérivées `has_python`, `backend_dir`, etc.).
- Vérifier que le remplissage de contexte et l’injection Click dans `pyscaf_core` appliquent correctement ces champs (régression couverte par **F806**).

### E4 — Graphe d’exécution

Respecter l’ordre implicite : **localstack** après **docker** ; **pipeline** après **git** (et avec dépendance explicite à **core** comme à la source) ; chaîne **agents** → **rules**, **skills**, **mcp**, **ide_binding**.

### E5 — Tests (F806)

- Tests unitaires ou d’intégration ciblant au minimum le **CoreAction** : visibilité d’options selon un contexte partiel, application des `postfill_hook`, cohérence des clés dérivées.
- Test d’intégration minimal : CLI ou `ActionManager` + répertoire temporaire, jeu d’options **non interactives** documenté, sans imposer à la CI l’exécution complète de tous les installeurs externes (`uv`, `docker`, etc.) sauf stratégie explicite (marqueurs pytest, mocks).

## Critères de succès (acceptation)

1. `uv run pytest` à la racine du monorepo passe, **y compris** les tests ajoutés pour F806.
2. `septeo-scaf --help` (ou script console défini dans `apps/septeo-scaf/pyproject.toml`) termine avec code 0 ; la découverte expose **17** actions.
3. Aucune occurrence de `septeo_scaffolder.` dans `apps/septeo-scaf/src/septeo_scaf/actions/`.
4. Pour chaque action, un revueur peut comparer avec `~/lab/septeo-agentic-scaffolder` : écarts limités aux transformations listées en E2 et aux corrections de stubs (`depends` / `run_preferably_after`).

## Hors périmètre

- Refactor fonctionnel majeur ou changement de produit (nouvelles stacks, nouvelles options) non présentes dans le dépôt source.
- Déplacement de **Jinja2** dans `pyscaf-core` (reste une dépendance **application** `septeo-scaf`, conformément à la roadmap).
- Parité ligne-à-ligne globale des fichiers **générés** sur tous les chemins du graphe (objectif : parité du **code des actions** et des **templates** ; les sorties peuvent varier avec la version des outils).

## Références

- Roadmap Phase 8 : `specs/roadmap/feature-inventory-stress-test.md` (F801–F806).
- Spécification analogue (pyscaf) : `specs/701-pyscaf-actions-port/spec.md`.
