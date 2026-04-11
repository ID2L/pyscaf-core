# F701 — Port des actions open-pyscaf vers `apps/pyscaf` (pyscaf-app)

**ID** : F701 (Phase 7 — fil conducteur avec F702–F710)  
**Statut** : Spécification  
**Source de vérité fonctionnelle** : dépôt `open-pyscaf` local, répertoire `src/pyscaf/actions/` (hors `manager.py` et agrégats réservés au package source).

## Synthèse

Porter les **implémentations réelles** des huit actions du scaffolder historique vers le monorepo `pyscaf-core`, package d’application `pyscaf_app`, sous `apps/pyscaf/src/pyscaf_app/actions/<module>/`. La Phase 6 a livré des stubs et un CLI opérationnel ; cette phase remplace le corps des actions tout en conservant les **contrats** (`depends`, `run_preferably_after`, `cli_options`, cycle de vie) et les **fichiers statiques** (templates, `config.toml`, `README.md`, `scripts/`, etc.).

## Objectifs mesurables

1. **Couverture des actions** : les huit modules `core`, `git`, `license`, `documentation`, `test`, `jupyter`, `jupyter_tools`, `semantic_release` contiennent le code métier issu d’open-pyscaf, pas seulement des stubs.
2. **Parité des assets** : pour chaque action, l’arborescence de fichiers non-Python présente dans la source est reproduite à côté de `__init__.py` dans `pyscaf_app` (noms de fichiers et contenu identiques sauf contraintes explicites ci-dessous).
3. **Imports** : aucune dépendance résiduelle vers le namespace `pyscaf.*` dans le code porté des actions ; les primitives du moteur viennent de `pyscaf_core` et des outils TOML de `pyscaf_core.tools`.
4. **Régression** : la suite de tests du monorepo reste verte ; au moins un test d’intégration exécute un parcours de création de projet (répertoire temporaire, option équivalente à « sans installation ») via `pyscaf-app`.

## Exigences fonctionnelles

### E1 — Périmètre des fichiers à porter

| Module app | Source (`open-pyscaf`) | Fichiers / dossiers à copier (indicatif) |
|------------|-------------------------|------------------------------------------|
| `core` | `actions/core/` | `__init__.py`, `config.toml`, `default_settings.json`, `README.md` |
| `git` | `actions/git/` | `__init__.py`, `README.md`, `template.gitignore` |
| `license` | `actions/license/` | `__init__.py` + les six `template_*.txt` |
| `documentation` | `actions/documentation/` | `__init__.py`, `config.toml`, `README.md`, `scripts/` |
| `test` | `actions/test/` | `__init__.py`, `config.toml`, `README.md`, `template_test_example.py`, `template.gitignore` |
| `jupyter` | `actions/jupyter/` | `__init__.py`, `config.toml`, `README.md`, `template.gitignore` |
| `jupyter_tools` | `actions/jupyter_tools/` | `__init__.py`, `config.toml`, `README.md`, `scripts/` |
| `semantic_release` | `actions/semantic-release/` | `__init__.py`, `config.toml`, `README.md`, `github/` |

**Hors périmètre** : `actions/manager.py`, `actions/__init__.py` et `actions/cli_option_to_key.py` du dépôt source — le monorepo s’appuie sur `pyscaf_core.actions.manager` et `pyscaf_core.cli_option_to_key`.

**Convention de nommage** : le dossier source `semantic-release/` devient le package Python `semantic_release/` (déjà aligné avec les entry points Phase 6).

### E2 — Modifications autorisées sur le code porté

1. **Imports**  
   - `from pyscaf.actions import ...` → `from pyscaf_core import ...` (ou import explicite depuis `pyscaf_core.actions` si le projet préfère un style uniforme, tant que l’API publique reste celle exportée par `pyscaf_core`).  
   - `from pyscaf.tools...` → `from pyscaf_core.tools...` (ex. `toml_merge`).

2. **Journalisation** : dans les fichiers `__init__.py` des actions, remplacer les sorties qui dupliquent le style « orchestration » du cœur :  
   - les appels `rich.console.Console().print(...)` utilisés pour le fil utilisateur pendant `init` / `install` / configuration → **`logging.getLogger(__name__)`** avec `info` / `warning` / `error`, en cohérence avec `pyscaf_core.actions.manager` ;  
   - les `print(...)` de débogage dans ces mêmes modules (ex. `DocumentationAction`) → **`logger.info`** (ou `debug` si le message est verbeux).  
   **Exception** : les scripts sous `scripts/` copiés tels quels pour être exécutés en ligne de commande dans le projet généré peuvent conserver `print` s’ils ne font pas partie du runtime du gestionnaire d’actions — l’objectif est d’éviter la divergence avec le moteur, pas de réécrire des petits CLI outil.

3. **Aucune autre « amélioration »** : pas de refactor fonctionnel, pas de changement de logique `subprocess`, pas de modification des chaînes de templates sauf si une chaîne référence explicitement l’ancien nom de projet (dans ce cas, aligner sur `pyscaf-app` / monorepo uniquement si indispensable au build).

### E3 — Fidélité des contrats d’action

Pour chaque classe `*Action` :

- Conserver `depends`, `run_preferably_after` et la liste `cli_options` (noms d’options, types, prompts, defaults, `choices`, callbacks `postfill_*` / `default` callable) **identiques** à la source.
- Conserver les méthodes `skeleton`, `init`, `install`, `activate` avec le même comportement observable (fichiers créés, commandes invoquées, conditions sur `context`).

### E4 — Contexte d’exécution et dépendances externes

- Les appels à `uv`, `git`, `code`, Jupyter, etc. restent tels quels ; ils s’exécutent dans le répertoire projet cible (`os.chdir(self.project_path)` là où la source le fait).
- `tomli` / `tomli-w` restent des dépendances déclarées de `pyscaf-app` (déjà présentes Phase 6). `rich` et `questionary` peuvent rester **transitifs** via `pyscaf-core` ; si l’outil d’empaquetage ou le linter impose des imports explicites, les ajouter dans `apps/pyscaf/pyproject.toml` sans changer les versions imposées par le workspace.

### E5 — Tests d’intégration

- Ajouter (ou étendre) des tests sous `apps/pyscaf/tests/` qui :  
  - créent un répertoire temporaire ;  
  - invoquent le flux CLI de création de projet avec les flags non interactifs nécessaires et **sans étape d’installation** équivalente à `--no-install` (ou combinaison documentée dans le plan si le nom diffère) ;  
  - vérifient au minimum la présence de fichiers clés et/ou l’absence d’exception, selon une stratégie définie dans `plan.md` pour limiter la dépendance à `uv`/`git` sur les runners CI.

## Critères de succès (acceptation)

1. `uv run pytest` (ou équivalent documenté à la racine du monorepo) passe, **y compris** le nouveau test d’intégration minimal.
2. `pyscaf-app --help` termine avec code 0 et la découverte continue d’exposer **8** actions.
3. Aucune occurrence de `from pyscaf.` dans `apps/pyscaf/src/pyscaf_app/actions/`.
4. Pour chaque action, un revueur peut comparer fichier par fichier avec open-pyscaf et n’y voir que les écarts listés en E2.

## Hors périmètre

- Port de `apps/septeo-scaf` (Phase 8).
- Harmonisation globale des messages utilisateur du CLI au-delà des actions (ex. `build_cli` / `ActionManager`).
- Exécution réelle de `uv sync` ou installation d’extensions VS Code dans la CI comme prérequis du test unitaire par défaut (sauf stratégie optionnelle « job manuel » ou marqueur pytest documenté).

## Références internes

- Spécification fondation apps : `specs/601-stress-apps-skeleton/spec.md` (F601–F603, conventions templates, nommage `pyscaf-app`).
