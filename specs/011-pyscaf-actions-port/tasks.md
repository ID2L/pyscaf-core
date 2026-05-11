# Tâches — F701 Port des actions `pyscaf_app`

Format : cases à cocher ordonnées par dépendance logique. Les chemins sont relatifs à la racine du monorepo `pyscaf-core`.

---

## Préparation

- [ ] T001 [P] Vérifier que la branche de travail inclut Phase 6 verte (`apps/pyscaf` stubs, 8 actions découvertes, pytest OK) — racine du repo
- [ ] T002 [P] Comparer chaque `__init__.py` source sous `~/lab/pyscaf/src/pyscaf/actions/` avec le stub `apps/pyscaf/src/pyscaf_app/actions/*/__init__.py` pour liste de fichiers assets manquants

---

## Action `core`

- [ ] T010 [US1] Copier `config.toml`, `default_settings.json`, `README.md` depuis `~/lab/pyscaf/src/pyscaf/actions/core/` vers `apps/pyscaf/src/pyscaf_app/actions/core/`
- [ ] T011 [US1] Remplacer `apps/pyscaf/src/pyscaf_app/actions/core/__init__.py` par le port depuis la source : imports `pyscaf_core`, `merge_toml_files` N/A ; remplacer `Console().print` par `logger` — `apps/pyscaf/src/pyscaf_app/actions/core/__init__.py`
- [ ] T012 [US1] Vérifier absence de `from pyscaf` et exécuter ruff sur `apps/pyscaf/src/pyscaf_app/actions/core/__init__.py`

---

## Action `git`

- [ ] T020 [US2] Copier `README.md`, `template.gitignore` vers `apps/pyscaf/src/pyscaf_app/actions/git/`
- [ ] T021 [US2] Porter `__init__.py` : imports `pyscaf_core`, conserver `questionary` / subprocess ; logging au lieu de `console.print` — `apps/pyscaf/src/pyscaf_app/actions/git/__init__.py`

---

## Action `license`

- [ ] T030 [US3] Copier les six fichiers `template_*.txt` vers `apps/pyscaf/src/pyscaf_app/actions/license/`
- [ ] T031 [US3] Porter `__init__.py` avec imports `pyscaf_core` — `apps/pyscaf/src/pyscaf_app/actions/license/__init__.py`

---

## Action `documentation`

- [ ] T040 [US4] Copier `config.toml`, `README.md` et le répertoire `scripts/` vers `apps/pyscaf/src/pyscaf_app/actions/documentation/`
- [ ] T041 [US4] Porter `__init__.py` : imports `pyscaf_core` ; `print` → `logger` — `apps/pyscaf/src/pyscaf_app/actions/documentation/__init__.py`
- [ ] T042 [US4] Parcourir `apps/pyscaf/src/pyscaf_app/actions/documentation/scripts/*.py` pour toute référence `pyscaf` ; corriger ou documenter exception

---

## Action `test`

- [ ] T050 [US5] Copier `config.toml`, `README.md`, `template_test_example.py`, `template.gitignore` vers `apps/pyscaf/src/pyscaf_app/actions/test/`
- [ ] T051 [US5] Porter `__init__.py` avec imports `pyscaf_core` et logging — `apps/pyscaf/src/pyscaf_app/actions/test/__init__.py`

---

## Action `jupyter`

- [ ] T060 [US6] Copier `config.toml`, `README.md`, `template.gitignore` vers `apps/pyscaf/src/pyscaf_app/actions/jupyter/`
- [ ] T061 [US6] Porter `__init__.py` avec imports `pyscaf_core` et logging — `apps/pyscaf/src/pyscaf_app/actions/jupyter/__init__.py`

---

## Action `jupyter_tools`

- [ ] T070 [US7] Copier `config.toml`, `README.md` et tout `scripts/` vers `apps/pyscaf/src/pyscaf_app/actions/jupyter_tools/`
- [ ] T071 [US7] Porter `__init__.py` : `from pyscaf_core.tools.toml_merge import merge_toml_files`, logging — `apps/pyscaf/src/pyscaf_app/actions/jupyter_tools/__init__.py`
- [ ] T072 [US7] Vérifier les scripts sous `jupyter_tools/scripts/` : pas d’import `pyscaf` ; laisser `print` CLI sauf correction d’import

---

## Action `semantic_release`

- [ ] T080 [US8] Copier `config.toml`, `README.md` et `github/` (workflows) vers `apps/pyscaf/src/pyscaf_app/actions/semantic_release/`
- [ ] T081 [US8] Porter `__init__.py` avec imports `pyscaf_core` et logging — `apps/pyscaf/src/pyscaf_app/actions/semantic_release/__init__.py`

---

## Dépendances app et hygiène

- [ ] T090 [P] Mettre à jour `apps/pyscaf/pyproject.toml` si des dépendances directes `rich` / `questionary` sont requises (politique d’imports explicites)
- [ ] T091 [P] `rg "from pyscaf\\.|import pyscaf"` sur `apps/pyscaf/src/pyscaf_app/actions/` — résultat vide attendu

---

## Tests et validation

- [ ] T100 [P] Ajouter un test d’intégration minimal (temp dir, flux create avec `--no-install` ou équivalent) — `apps/pyscaf/tests/test_pyscaf_app_create_flow.py` (nom final au choix de l’implémentation)
- [ ] T101 [P] Exécuter `uv run pytest` à la racine du monorepo et corriger les régressions
- [ ] T102 [P] Smoke : `uv run pyscaf-app --help` (code 0) et vérification que 8 actions sont toujours découvertes — racine du repo

---

## Documentation de suivi

- [ ] T110 [P] Mettre à jour `_todo.md` : cocher F702–F710 au fur et à mesure de l’implémentation réelle (hors ce livrable spec-only)

---

**Légende** : `[P]` = parallélisable avec d’autres tâches sans dépendance ; `[USn]` = aligné sur le parcours utilisateur / action dans `spec.md`.
