# Tâches — F801–F806 Port des actions `septeo_scaf`

Format : cases à cocher ordonnées par dépendance. Chemins relatifs à la racine du monorepo `pyscaf-core`.  
**Source** : `~/lab/septeo-agentic-scaffolder/src/septeo_scaffolder/actions/`  
**Cible** : `apps/septeo-scaf/src/septeo_scaf/actions/`

---

## Préparation

- [ ] T001 [P] Vérifier branche verte : stubs `septeo-scaf`, 17 entry points, `pytest` OK — racine du repo
- [ ] T002 [P] Inventaire diff source ↔ cible : lister pour chaque module les fichiers `templates/**/*.j2` et assets hors Python à copier

---

## F802 — CoreAction

- [ ] T010 [F802] Copier `core/templates/` (`AGENTS.md.j2`, `README.md.j2`, `Makefile.j2`, `_todo.md.j2`) vers `apps/septeo-scaf/src/septeo_scaf/actions/core/templates/`
- [ ] T011 [F802] Porter `core/__init__.py` : imports `pyscaf_core` ; conserver `_render_template`, `_apps_postfill_hook`, toutes les `CLIOption` avec `visible_when` et `postfill_hook` ; méthode `skeleton` — `apps/septeo-scaf/src/septeo_scaf/actions/core/__init__.py`
- [ ] T012 [F802] Remplacer sorties utilisateur par `logging` si la source utilisait `print`/`Console` dans ce module — même fichier
- [ ] T013 [F802] Vérifier ruff + absence de `septeo_scaffolder` sous `apps/septeo-scaf/src/septeo_scaf/actions/core/`

---

## F803 — Actions stack (Git, Python, PHP, Javascript, Database, Docker)

- [ ] T020 [F803] **Git** : copier `git/templates/.gitignore.j2` ; porter `git/__init__.py` + `depends`/`run_preferably_after`/`cli_options` alignés source — `apps/septeo-scaf/src/septeo_scaf/actions/git/`
- [ ] T021 [F803] **Python** : copier tout `python/templates/` ; porter `python/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/python/`
- [ ] T022 [F803] **PHP** : copier tout `php/templates/` ; porter `php/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/php/`
- [ ] T023 [F803] **Javascript** : copier tout `javascript/templates/` ; porter `javascript/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/javascript/`
- [ ] T024 [F803] **Database** : copier `database/templates/` ; porter `database/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/database/`
- [ ] T025 [F803] **Docker** : copier `docker/templates/` (incl. `dockerfiles/`) ; porter `docker/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/docker/`
- [ ] T026 [F803] Contrôle transversal F803 : imports `pyscaf_core` / `pyscaf_core.tools` ; logging ; ruff sur les six modules

---

## F804 — Infra / produit (Localstack, EnvConfig, DocsStarlight, I18n, Pipeline)

- [ ] T030 [F804] **Localstack** : copier `localstack/templates/` ; porter `localstack/__init__.py` (`depends={"docker"}`, `run_preferably_after="docker"`) — `apps/septeo-scaf/src/septeo_scaf/actions/localstack/`
- [ ] T031 [F804] **EnvConfig** : copier `env_config/templates/` ; porter `env_config/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/env_config/`
- [ ] T032 [F804] **DocsStarlight** : copier `docs_starlight/templates/` ; porter `docs_starlight/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/docs_starlight/`
- [ ] T033 [F804] **I18n** : copier `i18n/templates/` ; porter `i18n/__init__.py` — `apps/septeo-scaf/src/septeo_scaf/actions/i18n/`
- [ ] T034 [F804] **Pipeline** : copier `pipeline/templates/` ; porter `pipeline/__init__.py` avec **`depends={"core","git"}`** et **`run_preferably_after="git"`** (corriger le stub si besoin) — `apps/septeo-scaf/src/septeo_scaf/actions/pipeline/`
- [ ] T035 [F804] Contrôle transversal F804 : ruff ; pas de `septeo_scaffolder`

---

## F805 — DX (Agents, Rules, Skills, Mcp, IdeBinding)

- [ ] T040 [F805] **Agents** : copier `agents/templates/` ; porter `agents/__init__.py` (`depends={"core"}`, `run_preferably_after="core"`) — `apps/septeo-scaf/src/septeo_scaf/actions/agents/`
- [ ] T041 [F805] **Rules** : copier `rules/templates/` ; porter `rules/__init__.py` avec **`depends={"agents"}`**, **`run_preferably_after="agents"`** (aligner sur la source, corriger stub) — `apps/septeo-scaf/src/septeo_scaf/actions/rules/`
- [ ] T042 [F805] **Skills** : copier `skills/templates/` (incl. sous-dossiers) ; porter `skills/__init__.py` (`depends={"agents"}`, `run_preferably_after="agents"`) — `apps/septeo-scaf/src/septeo_scaf/actions/skills/`
- [ ] T043 [F805] **Mcp** : copier `mcp/templates/` ; porter `mcp/__init__.py` (`depends={"agents"}`, `run_preferably_after="agents"`) — `apps/septeo-scaf/src/septeo_scaf/actions/mcp/`
- [ ] T044 [F805] **IdeBinding** : porter `ide_binding/__init__.py` (`depends={"agents"}`, `run_preferably_after="agents"`) et tout template ou fichier statique présent à la source — `apps/septeo-scaf/src/septeo_scaf/actions/ide_binding/`
- [ ] T045 [F805] Contrôle transversal F805 : graphe `agents` → enfants validé par chargement manager ou test léger

---

## F806 — Tests

- [ ] T050 [F806] Tests **CoreAction** : `visible_when` (ex. options masquées si `project_type == "library"` ou `docker` faux pour serverless) ; `postfill_hook` (`has_*`, `backend_dir`, etc.) — sous `apps/septeo-scaf/tests/` (ou `tests/` racine selon convention existante Phase 6)
- [ ] T051 [F806] Test rendu Jinja2 minimal : `_render_template` ou `skeleton` avec contexte fixe pour un fichier `core/templates/*.j2`
- [ ] T052 [F806] Test d’intégration minimal : `tmp_path` + `CliRunner` ou `ActionManager` + options non interactives documentées ; assertions sur fichiers clés et absence d’exception (stratégie sans dépendre de tous les outils externes)
- [ ] T053 [F806] Smoke : découverte / chargement des 17 actions sans erreur d’import

---

## Validation finale

- [ ] T060 [P] `uv run pytest` à la racine — monorepo
- [ ] T061 [P] `uv run septeo-scaf --help` — code 0, 17 actions visibles
- [ ] T062 [P] `rg 'septeo_scaffolder' apps/septeo-scaf/src` — aucun résultat
