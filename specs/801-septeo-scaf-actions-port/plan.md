# Plan technique — Port des actions Septeo vers `septeo_scaf`

## 1. Contexte

| Élément | Chemin / remarque |
|---------|-------------------|
| Dépôt source | `~/lab/septeo-agentic-scaffolder` — `src/septeo_scaffolder/actions/` |
| Cible | `apps/septeo-scaf/src/septeo_scaf/actions/` — un package Python par action |
| Moteur | `packages/pyscaf-core` — `Action`, `ActionManager`, `CLIOption`, `ChoiceOption`, `build_cli`, `make_main`, `cli_option_to_key`, outils `pyscaf_core.tools` |
| App | `septeo-scaf` — entry points `pyscaf_core.plugins` déjà déclarés dans `apps/septeo-scaf/pyproject.toml` ; dépendances **jinja2**, **tomlkit** |

Le CLI de l’app (`septeo_scaf.main`) s’appuie sur le factory du core ; le port ne modifie la mécanique d’enregistrement des plugins sauf si un **identifiant d’action** dans `depends` ne correspond pas aux clés d’entry point (à vérifier : les noms `docs_starlight`, `ide_binding`, etc. doivent rester stables).

## 2. Cartographie des imports

| Source (`septeo_scaffolder`) | Cible |
|------------------------------|--------|
| `from septeo_scaffolder.actions import Action, CLIOption, ChoiceOption` | `from pyscaf_core import Action, CLIOption, ChoiceOption` |
| `from septeo_scaffolder.tools.toml_merge import ...` | `from pyscaf_core.tools.toml_merge import ...` |
| `from septeo_scaffolder.tools.format_toml import ...` | `from pyscaf_core.tools.format_toml import ...` |

**Interne au package app** : si la source importait un autre module sous `septeo_scaffolder.actions`, remplacer par `septeo_scaf.actions.<module>` (ou chemin relatif cohérent avec le package installé). En pratique, la plupart des actions sont autonomes ; vérifier `cli_option_to_key` s’il était dupliqué localement — utiliser **`pyscaf_core.cli_option_to_key`** si nécessaire.

## 3. Stratégie templates Jinja2

1. **Copie** : reproduire l’arborescence `templates/` à l’identique (noms `.j2`, sous-dossiers).
2. **Résolution** :  
   `templates_dir = Path(__file__).parent / "templates"`  
   puis `Environment(loader=FileSystemLoader(str(templates_dir)), autoescape=False)` comme dans la source **core** et les autres actions qui rendent des fichiers.
3. **Contexte** : ne pas modifier les clés attendues par les templates sauf si une clé dépend d’un bug avéré ; les `postfill_hook` du core fournissent des clés consommées par d’**autres** actions — conserver les mêmes noms (`has_python`, `backend_dir`, etc.).
4. **Tests** : pour F806, au moins un test peut assert le rendu d’un template minimal du core avec un contexte dict fixe (sans passer par le réseau ni subprocess).

## 4. `visible_when` et `postfill_hook`

- Le core **pyscaf** valide déjà `visible_when` et les hooks dans `fill_default_context` / collecte CLI ; le port Septeo sert de **stress test** (nombreuses options, choix multiples, lambdas).
- **CoreAction** : conserver les mêmes prédicats et le même ordre des `CLIOption` pour que les indices de défaut interactifs restent alignés avec la source.
- Documenter dans la PR d’implémentation tout écart si le comportement du core diffère du vieux `ActionManager` Septeo (peu probable après Phase 3).

## 5. Dépendances `apps/septeo-scaf/pyproject.toml`

- Conserver **jinja2** et **tomlkit** (déjà présents).
- Ajouter des dépendances directes seulement si le code porté importe explicitement des bibliothèques non couvertes par `pyscaf-core` (ex. **questionary**, **rich**) — aligner les versions sur le workspace / le core pour éviter les conflits.

## 6. Ordre d’implémentation recommandé

1. **F802** — `core` + copie `templates/` (AGENTS, README, Makefile, _todo).
2. **F803** — `git`, `python`, `php`, `javascript`, `database`, `docker` (toutes `run_preferably_after="core"` sauf ordre manager).
3. **F804** — `localstack` (après docker), `env_config`, `docs_starlight`, `i18n`, `pipeline` (correction des stubs : `depends={"core","git"}`, `run_preferably_after="git"`).
4. **F805** — `agents` puis `rules`, `skills`, `mcp`, `ide_binding` (tous dépendent de **agents** dans la source).
5. **F806** — tests.

Le parallélisme **F803 / F804 / F805** n’est possible qu’après **F802** et en respectant les arêtes du tableau dans `spec.md`.

## 7. Risques et mitigations

| Risque | Mitigation |
|--------|------------|
| Stubs avec `depends` incomplets (ex. pipeline sans `core`, rules sans `agents`) | Corriger lors du port ; valider avec le tri topologique du manager |
| CI lente ou instable à cause d’`install()` (subprocess, réseau) | Tests d’intégration avec `--no-install` ou équivalent ; marqueurs pytest ; mocks ciblés |
| Divergence silencieuse des clés de contexte | Tests F806 sur `postfill_hook` et sur un squelette minimal |

## 8. Livrables de review

- Diff par lot (F802 → F805) pour limiter la taille des PR.
- Checklist : absence de `septeo_scaffolder`, présence des dossiers `templates/`, ruff/pytest verts.
