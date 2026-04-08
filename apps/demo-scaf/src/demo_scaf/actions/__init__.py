"""Demo actions package — showcases pyscaf-core plugin API."""

import importlib
import os
import pkgutil

from pyscaf_core import Action


def discover_actions() -> list[type[Action]]:
    """Discover all Action subclasses in this package."""
    actions: list[type[Action]] = []
    package_dir = os.path.dirname(__file__)
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        mod = importlib.import_module(f"demo_scaf.actions.{module_name}")
        for attr in dir(mod):
            obj = getattr(mod, attr)
            if isinstance(obj, type) and issubclass(obj, Action) and obj is not Action:
                actions.append(obj)
    return actions
