# Bug Investigation Report: `pytest` not found when running from `apps/pyscaf/`

## Executive Summary

- **Bug** : `uv run pytest` échoue avec `Failed to spawn: pytest — No such file or directory` quand exécuté depuis `apps/pyscaf/`
- **Impact** : Impossible de lancer les tests YAML d'actions depuis le sous-dossier de l'app
- **Cause racine** : `pytest` est une dépendance **dev du workspace racine**, pas de l'app `pyscaf-app`. Quand `uv run` est exécuté depuis `apps/pyscaf/`, uv résout le projet local (`pyscaf-app`) qui n'a pas `pytest` dans ses dépendances.

## Reproduction

### Étapes

1. `cd apps/pyscaf/`
2. `uv run pytest apps/pyscaf/tests/test_yaml_actions.py --action-filter="license" -v`

### Résultat actuel

```
error: Failed to spawn: `pytest`
  Caused by: No such file or directory (os error 2)
```

### Résultat attendu

Les tests YAML s'exécutent et affichent les résultats.

### Environnement

- macOS (darwin 25.4.0), fish shell
- Python 3.12.13 via uv
- Workspace uv monorepo (`[tool.uv.workspace]` dans `pyproject.toml` racine)

## Log Analysis

Ligne clé du terminal (l.111-118) :

```
warning: Ignoring existing virtual environment linked to non-existent Python interpreter
Removed virtual environment at: /Users/guilhemheinrich/lab/pyscaf-core/.venv
Creating virtual environment at: /Users/guilhemheinrich/lab/pyscaf-core/.venv
Built pyscaf-app @ file:///...
Built pyscaf-core @ file:///...
Installed 19 packages in 17ms
error: Failed to spawn: `pytest`
```

uv reconstruit le venv avec **19 packages** (les dépendances de `pyscaf-app` + `pyscaf-core`), mais **pas les dev dependencies du workspace** (dont `pytest`). Même après `uv sync` (l.122-124), le problème persiste car `uv sync` depuis `apps/pyscaf/` ne synchronise que ce projet.

## Code Path Analysis

### Chaîne de résolution uv

1. L'utilisateur lance `uv run pytest` depuis `apps/pyscaf/`
2. uv détecte le `pyproject.toml` local (`apps/pyscaf/pyproject.toml`)
3. uv résout les dépendances de `pyscaf-app` : `pyscaf-core`, `tomli`, `tomli-w`
4. uv installe ces 19 packages dans le venv **workspace** (`.venv` à la racine)
5. `pytest` n'est **pas** dans les dépendances de `pyscaf-app`
6. `pytest` est dans `[dependency-groups] dev` du **workspace root** `pyproject.toml`
7. `uv run` depuis un sous-projet ne résout pas automatiquement les dev dependencies du workspace root

### Configuration pertinente

**Workspace root** (`pyproject.toml` l.7-8) :
```toml
[dependency-groups]
dev = ["pytest>=8", "ruff>=0.8", "python-semantic-release>=9.21.1"]
```

**App pyscaf** (`apps/pyscaf/pyproject.toml`) :
```toml
[project]
dependencies = ["pyscaf-core", "tomli>=2.0.0", "tomli-w>=1.0.0"]
# Pas de [dependency-groups] dev
# Pas de pytest dans les dépendances
```

## Root Cause Analysis

### Cause primaire

**`uv run` depuis un sous-dossier workspace résout le projet local, pas le workspace root.** Les `dependency-groups` (dont `dev` avec `pytest`) sont déclarées uniquement au niveau du workspace root. Quand on lance `uv run` depuis `apps/pyscaf/`, uv utilise le `pyproject.toml` de `pyscaf-app` qui n'inclut pas `pytest`.

### Technique des 5 Pourquoi

1. **Pourquoi `pytest` n'est pas trouvé ?** — Il n'est pas installé dans le venv au moment de l'exécution
2. **Pourquoi n'est-il pas installé ?** — `uv run` depuis `apps/pyscaf/` ne résout que les deps de `pyscaf-app`
3. **Pourquoi ne résout-il pas les dev deps ?** — Les dev deps sont dans le workspace root, pas dans `pyscaf-app`
4. **Pourquoi sont-elles uniquement dans le root ?** — C'est le pattern monorepo standard : les outils dev sont centralisés
5. **Pourquoi l'utilisateur lance depuis le sous-dossier ?** — Le cwd du terminal est `apps/pyscaf/` (visible l.3 du terminal)

## Recommandations

### Fix 1 — Lancer depuis la racine du workspace (immédiat, pas de changement de code)

```bash
cd /Users/guilhemheinrich/lab/pyscaf-core
uv run pytest apps/pyscaf/tests/test_yaml_actions.py --action-filter="license" -v
```

C'est la méthode qui fonctionne déjà (testée dans Docker lors de l'implémentation).

### Fix 2 — Utiliser `--all-packages` pour synchroniser (immédiat)

```bash
cd /Users/guilhemheinrich/lab/pyscaf-core
uv sync --all-packages
uv run pytest apps/pyscaf/tests/ -v
```

### Fix 3 — Ajouter pytest aux dev deps de chaque app (changement de code)

Ajouter dans `apps/pyscaf/pyproject.toml` :

```toml
[dependency-groups]
dev = ["pytest>=8", "pyyaml>=6.0"]
```

Cela permettrait de lancer `uv run pytest` depuis n'importe quel sous-dossier. **Inconvénient** : duplication des dépendances dev dans chaque app.

### Fix 4 — Documenter la commande correcte (changement de docs)

Ajouter un `README.md` ou mettre à jour la doc pour indiquer que les tests doivent être lancés depuis la racine du workspace.

### Recommandation

**Fix 1 + Fix 4** : lancer depuis la racine et documenter. C'est le pattern standard des monorepos uv.

## Status Tracking

- [x] Investigation complete
- [x] Root cause identified
- [ ] Fix implemented
- [ ] Testing completed
- [ ] Bug resolved
