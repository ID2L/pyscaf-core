# Plan technique — F701 Port des actions vers `pyscaf_app`

## 1. Contexte

| Élément | Chemin / remarque |
|---------|-------------------|
| Dépôt source (référence) | `~/lab/pyscaf` — package `pyscaf`, actions sous `src/pyscaf/actions/` |
| Cible | `apps/pyscaf/src/pyscaf_app/actions/` — un package Python par action (`core`, `git`, …) |
| Moteur | `packages/pyscaf-core` — `Action`, `ActionManager`, `CLIOption`, `ChoiceOption`, `cli_option_to_key`, `discover_actions_from_package`, outils `pyscaf_core.tools.toml_merge` et `format_toml` |

Le CLI de l’app assemble déjà les actions via `discover_actions()` ; les entry points `pyscaf_core.plugins` restent inchangés en identifiants (ex. `semantic_release`).

## 2. Cartographie des imports

| Source | Cible |
|--------|--------|
| `from pyscaf.actions import Action, CLIOption, ChoiceOption` | `from pyscaf_core import Action, CLIOption, ChoiceOption` |
| `from pyscaf.tools.toml_merge import merge_toml_files` | `from pyscaf_core.tools.toml_merge import merge_toml_files` |
| `from pyscaf.tools.format_toml import ...` | `from pyscaf_core.tools.format_toml import ...` (si une action ou un script importé utilisait ce module — vérifier lors du port ; les actions listées n’en ont pas besoin sauf évolution future) |

Ne pas copier `pyscaf.actions.manager` ni importer le package `pyscaf` depuis l’app.

## 3. Journalisation vs Rich

Aujourd’hui, le source utilise `Console().print` pour les étapes utilisateur. Le `ActionManager` du core utilise `logging` (`logger.info`, etc.).

**Décision de port** : dans chaque `actions/<name>/__init__.py` porté :

1. Supprimer la dépendance locale à `Console()` pour le flux principal (ou la garder uniquement si un cas impose Rich — par défaut **non** pour réduire la duplication).
2. Ajouter en tête de module :  
   `import logging`  
   `logger = logging.getLogger(__name__)`
3. Remplacer chaque `console.print("...")` par un `logger.info("...")` en **texte plain** (sans balises Rich `[bold blue]...[/]`). Conserver l’information (étape, succès, avertissement, code de sortie).
4. Remplacer les `print(...)` de debug dans ces `__init__.py` par `logger.info` ou `logger.debug`.

Les fichiers sous `scripts/` (documentation, jupyter_tools) sont des utilitaires ; conserver les `print` sauf si un import `pyscaf` y apparaît (alors seulement corriger l’import ou retirer la dépendance).

## 4. Fichiers par action

### 4.1 `core`

- **Copier** : `config.toml`, `default_settings.json`, `README.md`.
- **`__init__.py`** : port intégral — `uv init`, `tomli`/`tomli-w` sur `pyproject.toml`, `uv sync`, installation extension Ruff, `get_local_git_author`, `skeleton` avec chemins via `Path(__file__).parent`.
- **Retirer** : import `pyscaf.actions` ; `Console` → logger comme §3.

### 4.2 `git`

- **Copier** : `README.md`, `template.gitignore`.
- **`__init__.py`** : `questionary` pour `_configure_remote`, `postfill_remote_url` / `postfill_git_host`, subprocess `git` — inchangé hors imports et logging.
- Les messages « Detected GitHub… » : passer en `logger.info`.

### 4.3 `license`

- **Copier** : les six `template_*.txt`.
- **`__init__.py`** : lecture des templates via `Path(__file__).parent` — inchangé hors imports.

### 4.4 `documentation`

- **Copier** : `config.toml`, `README.md`, répertoire `scripts/` (ex. `parse_doc.py`).
- **`__init__.py`** : remplacer les `print` de debug par `logger` ; imports `pyscaf_core`.

### 4.5 `test`

- **Copier** : `config.toml`, `README.md`, `template_test_example.py`, `template.gitignore`.
- **`__init__.py`** : idem logging.

### 4.6 `jupyter`

- **Copier** : `config.toml`, `README.md`, `template.gitignore`.
- **`__init__.py`** : idem.

### 4.7 `jupyter_tools`

- **Copier** : `config.toml`, `README.md`, `scripts/` (tout l’arbre).
- **`__init__.py`** : `merge_toml_files` depuis `pyscaf_core.tools.toml_merge` ; logging à la place de `console.print`.
- **CLI option** : conserver le nom exact de l’option dans la source (ex. `--jupyter_tools`) pour ne pas changer la clé de contexte dérivée par `cli_option_to_key`.

### 4.8 `semantic_release`

- **Copier** : `config.toml`, `README.md`, `github/workflows/*.yml`.
- **`__init__.py`** : skeleton vers sous-chemins `github/` dans le projet généré ; mises à jour `pyproject.toml` ; logging.

## 5. Dépendances `apps/pyscaf/pyproject.toml`

- Conserver `tomli`, `tomli-w`.
- Si nécessaire pour politique « imports explicites » ou type-checking : ajouter `rich` et `questionary` en dépendances directes avec contraintes alignées sur `pyscaf-core` (éviter de figer des versions incompatibles avec le workspace).

## 6. Stratégie de tests d’intégration

1. **Objectif** : valider que le graphe d’actions + CLI + squelette s’exécutent sans erreur lorsqu’on désactive l’installation.
2. **Mise en œuvre suggérée** :  
   - `tmp_path` pytest ;  
   - subprocess ou API Click `CliRunner` sur `pyscaf_app.main:main` (ou fonction équivalente exposée par le CLI) avec arguments non interactifs : nom de projet, flags pour désactiver prompts (selon options déjà définies sur `build_cli` — ex. `--no-install`) ;  
   - sous-ensemble d’options pour limiter les actions activées si le contexte par défaut exécute trop de branches (documenter le vecteur exact dans la PR d’implémentation).
3. **CI** : si `uv` ou `git` est absent sur un runner, utiliser `pytest.mark` pour sauter le test ou mock subprocess — **à trancher à l’implémentation** en priorité « test minimal qui tourne partout » (ex. vérifier seulement `core` + squelette si `--no-install` et options booléennes à false).

## 7. Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| CI sans `uv` / `git` | Test d’intégration conditionnel ou mock ; smoke limité aux modules sans subprocess. |
| Divergence Rich vs logs | Accepter perte de couleur dans les actions ; le core reste la référence de style. |
| Chemins `__file__` et wheel | Hatchling inclut `src/pyscaf_app` en entier — même modèle que F602. |

## 8. Ordre d’implémentation recommandé

1. `core` (racine du graphe).  
2. `git`, `license`, `test`, `jupyter`, `documentation` (dépendent de `core` ou indépendants entre eux sauf dépendances déjà définies).  
3. `jupyter_tools` (après `jupyter`).  
4. `semantic_release` (après `git`).  
5. Tests d’intégration + passage pytest complet.
