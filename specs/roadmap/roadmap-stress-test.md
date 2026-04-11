# Roadmap — Stress-test pyscaf-core (apps réels)

**Créé** : 2026-04-08  
**Auteur** : Cartographe (piste complémentaire)  
**Statut** : Brouillon — à valider avant `/specify`  
**Prérequis** : Phases 0–5 du [roadmap principal](./roadmap.md) **terminées** (moteur + `demo-scaf` en place).

## Résumé exécutif

Cette piste **ne remplace pas** le roadmap historique : elle démarre à **Phase 6** et vise à **valider la robustesse** de `pyscaf-core` en portant deux applications consommatrices **dans le monorepo** :

1. **`apps/pyscaf`** — fidélité fonctionnelle avec `~/lab/pyscaf` (`open-pyscaf`) : 8 actions, templates fichiers, `tomli`/`tomli-w`, pas de `visible_when` sur les options (cas minimal).
2. **`apps/septeo-scaf`** — fidélité avec `~/lab/septeo-agentic-scaffolder` : ~18 actions, Jinja2, `visible_when` et `postfill_hook` intensifs.

Les deux apps **ne dupliquent pas le moteur** : elles dépendent de `pyscaf-core` (workspace), exposent un script CLI, enregistrent les actions via `[project.entry-points."pyscaf_core.plugins"]`, et suivent le pattern `demo-scaf` (`build_cli`, `make_main`, découverte locale + entry points).

## Lien avec l’inventaire

Table détaillée des features : [feature-inventory-stress-test.md](./feature-inventory-stress-test.md).

## Analyse d’état (cible)

| Élément | État attendu après cette piste |
|---------|-------------------------------|
| Membres workspace | `apps/pyscaf`, `apps/septeo-scaf` inclus par `apps/*` |
| `pytest` racine | `testpaths` étendus pour inclure les tests des nouvelles apps |
| Moteur | Inchangé en principe ; les écarts découverts alimentent des correctifs ciblés dans `packages/pyscaf-core` |
| Sources externes | `~/lab/pyscaf` et `~/lab/septeo-agentic-scaffolder` restent la référence de comportement |

## Défis adressés (cartographie → phases)

| Défi | Traitement dans le roadmap |
|------|----------------------------|
| Imports | Remplacer tout import moteur par `pyscaf_core` (`Action`, `CLIOption`, `ChoiceOption`, `ActionManager`, utilitaires, chaîne de préférences si réexportée). |
| Templates / assets | Packager avec l’**app** (Hatchling : `force-include` / données de package / `importlib.resources` + chemins stables). |
| Jinja2 | Dépendance **uniquement** de `septeo-scaf` (pas dans le core). |
| `subprocess` (git, uv) | Actions invoquent le sous-processus depuis le contexte plugin ; tests avec mocks ou environnement contrôlé (pas d’hypothèse « cwd = repo moteur »). |
| `visible_when` | Couvert par `septeo-scaf` ; `pyscaf` valide l’absence de régression quand le champ est absent. |
| `postfill_hook` | Les deux apps l’utilisent → validation transversale du pipeline core. |
| `tomli` / `tomli-w` (`pyscaf`) | Déclarés sur `apps/pyscaf` uniquement. |
| `config.toml` | S’appuyer sur le `Action.init()` par défaut du core (fusion TOML). |
| Workspace root | Aucune modification de glob `members` si `apps/*` suffit ; vérifier `uv lock` et scripts. |
| Tests | Par app : tests d’intégration cycle de vie (découverte → ordre → phases skeleton/init/install sur fixture temporaire). |

## Politique d’exécution des commandes (Docker)

**Contrainte demandée pour cette piste** : exécuter lint, tests et smokes CLI **dans un conteneur**, pas sur l’hôte.

**Contexte repo** : la Phase 5 a retiré les artefacts Docker au profit d’un flux `uv` natif ([`_todo.md`](../../_todo.md)). **Réconciliation recommandée** :

- Réintroduire une **image ou cible `docker compose` minimale** dédiée CI / stress-test (sans imposer Docker aux contributeurs pour le flux quotidien, si le projet préfère `uv` local), **ou**
- Documenter dans les specs Phase 6 que les **pipelines CI** de cette piste passent par Docker alors que le dev local reste `uv`.

Les specs `spec.md` / `plan.md` / `tasks.md` de chaque feature devront indiquer explicitement la commande Docker utilisée pour la validation.

## Plan par phases

### Phase 6 — Fondation monorepo & empaquetage des apps

**Objectif** : deux squelettes d’applications installables, dépendant de `pyscaf-core`, avec convention unique pour les assets et extension de la config de test racine.

**Features** : F601–F604 (voir inventaire).

**Jalons**

- M6.1 : `uv sync` à la racine résout les trois packages (`pyscaf-core`, `pyscaf`, `septeo-scaf`).
- M6.2 : Pattern documenté pour résoudre un template depuis le package installé (editable inclus).

**Critères de sortie**

- [ ] Les deux apps exposent un `--help` CLI minimal (sans toutes les actions encore portées si incrémental).
- [ ] `pytest` racine découvre les répertoires de tests des nouvelles apps (config mise à jour).
- [ ] Validation décrite via Docker (ou décision d’exception tracée dans la spec F604).

**Dépendances** : Phases 0–5 complètes.

---

### Phase 7 — Application `apps/pyscaf` (port open-pyscaf)

**Objectif** : porter les **8 actions** et leurs fichiers template depuis `~/lab/pyscaf`, en conservant la sémantique (dépendances, options CLI, hooks).

**Features** : F701–F710 (voir inventaire).

**Stratégie d’implémentation**

- Incrément recommandé : **F701** (fil conducteur CLI + entry points pour toutes les classes, stubs acceptables) → **F702** `CoreAction` → actions dépendantes par couches (git / license / …) → **F710** tests d’intégration.
- Chaque action : spec dédiée ou sous-tâches dans `tasks.md` si un seul spec regroupe plusieurs fichiers.

**Critères de sortie**

- [ ] Toutes les actions enregistrées en entry points + découverte cohérente avec `demo-scaf`.
- [ ] Au moins un test d’intégration bout-en-bout (projet temporaire, subprocess mocké ou sandbox).
- [ ] Pas de code moteur dupliqué dans l’app.

**Dépendances** : Phase 6.

---

### Phase 8 — Application `apps/septeo-scaf` (port septeo-agentic-scaffolder)

**Objectif** : porter **~18 actions** et arborescences `templates/` (Jinja2), en conservant `visible_when` / `postfill_hook`.

**Features** : F801–F806 (voir inventaire).

**Stratégie d’implémentation**

- **F801** : dépendances app (`jinja2`, `tomlkit`, etc. alignées sur l’existant Septeo, **sans** les tirer dans le core si non nécessaires).
- **F802** : `CoreAction` (gros périmètre) en spec prioritaire.
- **F803–F805** : lots par domaine (stack technique, infra, DX agents/rules/skills) pour limiter le bruit de review.
- **F806** : tests ciblant les chemins interactifs / visibilité conditionnelle.

**Critères de sortie**

- [ ] Parité fonctionnelle raisonnable avec le repo source (liste d’écart documentée si simplification volontaire).
- [ ] Tests couvrant au moins un enchaînement `visible_when` + `postfill_hook`.

**Dépendances** : Phase 6 ; **recommandé** après Phase 7 pour réutiliser les apprentissages d’empaquetage (Phase 7 peut être parallélisée après F601–F602 si capacité).

---

### Phase 9 — Validation transversale & dette consciente

**Objectif** : garde-fous contre les régressions du core et documentation de fin de piste.

**Features** : F901–F903.

**Critères de sortie**

- [ ] Matrice « action × app » à jour dans l’inventaire ou README d’app.
- [ ] Décision documentée : publication PyPI des apps ou usage monorepo-only.

**Dépendances** : Phases 7 et 8 (ou sous-ensemble significatif).

---

## Graphe de dépendances (haut niveau)

```text
Phase 6 (F601–F604)
        │
        ├──────────────────────┐
        ▼                      ▼
Phase 7 (pyscaf)         Phase 8 (septeo-scaf)
F701–F710                F801–F806
        │                      │
        └──────────┬───────────┘
                   ▼
            Phase 9 (F901–F903)
```

Chemin critique pour réduire le risque : **F601 → F602 → F701 / F801** (empaquetage + CLI avant le gros du port).

## Registre des risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| Dérive par rapport aux repos sources (oubli de template / option) | Moyenne | Élevé | Checklist par action ; comparaison de arborescence générée sur fixture fixée ; F901. |
| Chemins templates cassés en editable vs wheel | Moyenne | Élevé | `importlib.resources` / tests des deux modes ; documenter le layout Hatchling. |
| `subprocess` flaky en CI (git/uv absents dans l’image) | Moyenne | Moyen | Image Docker avec git + uv ; mocks pour tests unitaires ; séparer tests « réseau / réel ». |
| Scope `septeo-scaf` trop large pour une seule PR | Élevée | Moyen | Découper F803–F805 en specs successives ; maintenir une branche de longue durée documentée. |
| Conflit Docker vs workflow `uv` natif (Phase 5) | Moyenne | Faible | F604 tranche : image CI dédiée stress-test sans ré-imposer Docker au README principal si non souhaité. |
| Besoin de modifier le core (API manquante) | Moyenne | Moyen | Issues + mini-specs core ; éviter d’étendre l’API sans cas d’usage des deux apps. |

## Questions ouvertes

1. **Nom du package PyPI / script** pour `apps/pyscaf` : conserver `open-pyscaf` / `pyscaf` en conflit avec le produit existant — préférer un nom monorepo explicite (ex. `pyscaf-legacy-app`) ou garder `pyscaf` en interne uniquement ?
2. **`septeo-scaf`** : même question (nom public vs interne Septeo).
3. **Parité stricte** : objectif 100 % ligne-à-ligne des templates ou « comportement équivalent » acceptable (à figer dans les specs F701/F801).

## Prochaines étapes (workflow /specify + /implement)

1. **F601** — `/specify` : ajouter les membres workspace `apps/pyscaf` et `apps/septeo-scaf`, structure `src/`, `pyproject.toml`, scripts console.
2. **F602** — `/specify` : convention Hatchling + accès runtime aux assets.
3. **F604** — `/specify` : stratégie Docker pour cette piste (alignement CI).
4. Enchaîner **F701** puis port par lots (**F702+** / **F802+**) selon [feature-inventory-stress-test.md](./feature-inventory-stress-test.md).

### Prêt pour spécification (ordre suggéré)

| Ordre | ID | Intitulé |
|-------|-----|----------|
| 1 | F601 | Squelettes workspace `apps/pyscaf` + `apps/septeo-scaf` |
| 2 | F602 | Empaquetage templates / assets (pattern unique) |
| 3 | F603 | Extension `pytest` / marqueurs monorepo |
| 4 | F604 | Validation Docker (CI stress-test) |
| 5 | F701 | CLI + discovery + entry points `pyscaf` |
| … | … | Voir inventaire |

---

## Voir aussi

- [roadmap.md](./roadmap.md) — phases 0–5 et historique produit  
- [feature-inventory-stress-test.md](./feature-inventory-stress-test.md) — inventaire F6xx–F9xx  
