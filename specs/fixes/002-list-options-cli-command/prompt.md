# Original Prompt

Le ActionTestRunner dans pyscaf_core.testing.runner ne gère pas les options de type liste (YAML list values) dans `_build_cli_command()`. Actuellement, quand une option YAML a une valeur liste comme `apps: [backend, frontend]`, le runner fait `str(value)` ce qui produit `--apps "['backend', 'frontend']"` au lieu de `--apps backend --apps frontend`.

Contexte :
- Le runner est utilisé par des projets downstream (septeo-scaf) qui ont des options Click avec `multiple=True`
- septeo-scaf a dû créer un SepteoTestRunner en sous-classe pour contourner le problème
- ~12 fichiers YAML de test sur 32 utilisent des listes dans les options (apps, database-extensions, languages)
- Le pattern Click pour les options multiples est `--key item1 --key item2`

Ce qui doit changer dans `_build_cli_command()` :
```python
# Avant (actuel)
for key, value in self.config.get("cli_arguments", {}).get("options", {}).items():
    if isinstance(value, bool):
        cmd.append(f"--{key}" if value else f"--no-{key}")
    else:
        cmd.extend([f"--{key}", str(value)])

# Après (attendu)
for key, value in self.config.get("cli_arguments", {}).get("options", {}).items():
    if isinstance(value, bool):
        cmd.append(f"--{key}" if value else f"--no-{key}")
    elif isinstance(value, list):
        for item in value:
            cmd.extend([f"--{key}", str(item)])
    else:
        cmd.extend([f"--{key}", str(value)])
```

Fichier impacté : `packages/pyscaf-core/src/pyscaf_core/testing/runner.py`

Tests à ajouter : un test unitaire vérifiant que `_build_cli_command()` expand correctement les listes en flags multiples.

Cela permettra aux projets downstream de supprimer leurs sous-classes de contournement (SepteoTestRunner) et d'utiliser directement `create_yaml_tests()` sans wrapper.
