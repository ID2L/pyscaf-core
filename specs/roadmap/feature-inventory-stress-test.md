# Inventaire des features — Stress-test pyscaf-core

**Companion** : [roadmap-stress-test.md](./roadmap-stress-test.md)  
**Convention** : une ligne = une portée plausible pour **`/specify`** (ou regroupement explicite dans un seul spec avec `tasks.md` découpé).  
**Complexité** : S = petit, M = moyen, L = grand, XL = très grand.

## Phase 6 — Fondation monorepo & empaquetage

| ID | Feature | Priorité | Complexité | Dépendances | Spec (à créer) |
|----|---------|----------|------------|-------------|----------------|
| F601 | Créer `apps/pyscaf` et `apps/septeo-scaf` : `pyproject.toml`, layout `src/`, dépendance `pyscaf-core` workspace, scripts CLI (`pyscaf` / `septeo-scaf` ou noms validés), stubs `main.py` + `actions/__init__.py` (pattern `demo-scaf`) | P0 | M | Phases 0–5 | `specs/601-stress-apps-skeleton/` |
| F602 | Convention unique pour embarquer templates : Hatchling (`packages` / `force-include`), chemins stables, helper partagé ou doc pour `importlib.resources` (ou équivalent) depuis les actions | P0 | M | F601 | `specs/602-stress-template-packaging/` |
| F603 | Étendre la config pytest racine (`testpaths`, optionnellement marqueurs `integration` / `slow`) pour les nouvelles apps ; aligner `uv run pytest` | P0 | S | F601 | `specs/603-stress-pytest-wiring/` (ou fusion F601) |
| F604 | Stratégie **Docker** pour valider cette piste (Dockerfile minimal ou `compose`, commandes documentées) ; réconciliation avec workflow `uv` natif post-F006 | P0 | M | F001–F005 (contexte) | `specs/604-stress-docker-ci/` |

### Arêtes (Phase 6)

- F602 dépend de F601 (packages réels).
- F603 peut être fusionné dans F601 si préférence pour moins de specs.

---

## Phase 7 — `apps/pyscaf` (port ~/lab/pyscaf)

| ID | Feature | Priorité | Complexité | Dépendances | Notes |
|----|---------|----------|------------|-------------|-------|
| F701 | Fil conducteur : `build_cli` / `make_main`, `discover_actions`, **tous** les entry points `pyscaf_core.plugins` pointant vers les classes (stubs OK), `--help` riche | P0 | M | F601 | Aucun moteur local. |
| F702 | Port **CoreAction** : options (`--author`, etc.), `uv init` / pyproject / README / `src/` / `.vscode` — dépendances `tomli`/`tomli-w` sur l’app | P0 | L | F701, F602 | Référence : repo source. |
| F703 | Port **GitAction** : `.gitignore`, `git init`, options versionning / remote / host | P0 | M | F702 | `subprocess` + tests mockés. |
| F704 | Port **LicenseAction** | P0 | S | F702 | Templates fichiers. |
| F705 | Port **JupyterAction** | P0 | M | F702 | |
| F706 | Port **TestAction** | P0 | M | F702 | |
| F707 | Port **SemanticReleaseAction** | P0 | M | F703 | Dépend de `git`. |
| F708 | Port **DocumentationAction** | P0 | M | F702 | |
| F709 | Port **JupyterToolsAction** | P0 | M | F705 | Dépend de `jupyter`. |
| F710 | Suite de tests d’intégration app : découverte, ordre d’exécution, au moins un flux create sur répertoire temporaire | P0 | L | F701–F709 | Docker pour exécution si politique F604. |

### Regroupement optionnel (moins de specs)

- **F703–F709** : un seul spec « Port actions pyscaf (hors core) » avec `tasks.md` par action.
- **F702** : toujours isolé (volume + risque).

---

## Phase 8 — `apps/septeo-scaf` (port septeo-agentic-scaffolder)

| ID | Feature | Priorité | Complexité | Dépendances | Notes |
|----|---------|----------|------------|-------------|-------|
| F801 | Fil conducteur + `pyproject.toml` : deps **app** (`jinja2`, `tomlkit`, …), CLI, entry points pour toutes les actions (stubs OK) | P0 | M | F601, F602 | Jinja2 **hors core**. |
| F802 | Port **CoreAction** (options nombreuses, `visible_when`, `postfill_hook`, templates Jinja2) | P0 | XL | F801 | Spec dédiée ; risque principal. |
| F803 | Port actions **stack** : Git, Python, Php, Javascript, Database, Docker | P0 | XL | F802 | Découpage interne par action dans `tasks.md`. |
| F804 | Port actions **infra / produit** : Localstack, EnvConfig, DocsStarlight, I18n, Pipeline | P0 | L | F802, F803 (selon `depends`) | |
| F805 | Port actions **DX** : Agents, Rules, Skills, Mcp, IdeBinding | P0 | L | F802 | |
| F806 | Tests ciblés `visible_when` / `postfill_hook` + intégration minimale bout-en-bout | P0 | L | F801–F805 | |

### Arêtes (Phase 8)

- F803–F805 peuvent être parallélisés après F802 **si** les graphes `depends` le permettent ; l’ordre du spec doit suivre la résolution topologique réelle du source.

---

## Phase 9 — Validation transversale

| ID | Feature | Priorité | Complexité | Dépendances | Notes |
|----|---------|----------|------------|-------------|-------|
| F901 | (Optionnel) Script ou doc de **parité** avec les repos sources : diff d’arborescence générée, liste d’écart acceptée | P1 | M | F710, F806 | |
| F902 | Smoke **full graph** : chargement de toutes les entry points sans erreur ; temps acceptable | P1 | S | F710, F806 | |
| F903 | Mise à jour doc : lien depuis `roadmap.md` vers cette piste ; statut « stress-test complété » | P2 | S | F901 ou F902 | |

---

## Synthèse des dépendances (features)

```text
F601 → F602 → F603
F601 → F604

F601 → F701 → F702 → F703–F709 → F710

F601 → F801 → F802 → F803–F805 → F806
F710 ─┐
F806 ┘ → F901 → F902 → F903
```

## Ordre de spécification recommandé pour `/specify`

```text
F601, F602, F603, F604
F701, F702, (F703–F709 groupé ou séquentiel), F710
F801, F802, F803, F804, F805, F806
F901, F902, F903
```

## Identifiants spec suggérés (dossiers `specs/`)

| ID | Dossier suggéré |
|----|-----------------|
| F601 | `601-stress-apps-skeleton` |
| F602 | `602-stress-template-packaging` |
| F603 | `603-stress-pytest-wiring` |
| F604 | `604-stress-docker-ci` |
| F701–F710 | `701-pyscaf-cli-wiring` … ou un spec par ID si granularité fine |
| F801–F806 | `801-septeo-scaf-cli-wiring` … idem |
| F901–F903 | `901-stress-parity-smoke` (grouper P1/P2 possible) |

*(Les numéros exacts peuvent être réassignés par l’équipe pour éviter collision avec futurs specs ; garder la traçabilité ID F6xx–F9xx dans `tasks.md`.)*
